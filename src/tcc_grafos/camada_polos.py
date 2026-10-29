"""Escore dos grandes polos de TI do estado (objetivo específico 2 da proposta).

Rodar com: python -m tcc_grafos.camada_polos [--atualizar]

Precisa da RAIS (BigQuery). O resultado vira a lista MUNICIPIOS_POLOS do config.
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from tcc_grafos.config import (
    ANO_FIM,
    ANO_INICIO,
    DATA_INTERIM_DIR,
    DATA_PROCESSED_DIR,
    UF_ALVO,
)
from tcc_grafos.etl.basedosdados_extract import estoque_empregos_ti_rais
from tcc_grafos.etl.capes import carregar_programas, municipios_com_pos_computacao
from tcc_grafos.etl.inep_cursos import carregar_cursos_ti
from tcc_grafos.etl.municipios import SIGLA_UF, carregar_municipios
from tcc_grafos.polos.scoring import calcular_escore, classificar_polos

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARQUIVO_RAIS = DATA_INTERIM_DIR / "rais_ti.parquet"
MODALIDADE_PRESENCIAL = 1


def carregar_rais(atualizar: bool = False) -> pd.DataFrame:
    if ARQUIVO_RAIS.exists() and not atualizar:
        return pd.read_parquet(ARQUIVO_RAIS)
    rais = estoque_empregos_ti_rais()
    rais.to_parquet(ARQUIVO_RAIS, index=False)
    return rais


def indicadores_ensino(cursos: pd.DataFrame) -> pd.DataFrame:
    """Critérios (a) e (b): concluintes presenciais no período e média anual de IES com
    curso presencial de TI funcionando. Só presencial: o EAD é registrado no polo de
    apoio, que não é uma IES do município (em Maringá passa o presencial)."""
    presencial = cursos[
        (cursos["modalidade"] == MODALIDADE_PRESENCIAL) & cursos["codigo_ibge"].notna()
    ].astype({"codigo_ibge": "int64"})
    concluintes = presencial.groupby("codigo_ibge")["concluintes"].sum()
    ativos = presencial[presencial["matriculas"] > 0]
    ies_por_ano = ativos.groupby(["codigo_ibge", "ano"])["co_ies"].nunique()
    num_ies = ies_por_ano.groupby("codigo_ibge").sum() / cursos["ano"].nunique()
    return pd.DataFrame({"total_concluintes": concluintes, "num_ies_ti": num_ies}).fillna(0)


def montar_indicadores(
    cursos: pd.DataFrame, rais: pd.DataFrame | None, com_pos: set[int]
) -> pd.DataFrame:
    df = indicadores_ensino(cursos)
    df = df[df["num_ies_ti"] > 0]
    if rais is not None:
        estoque = rais.assign(codigo_ibge=rais["id_municipio"].astype("int64")).groupby(
            "codigo_ibge"
        )["vinculos_ti"].mean()
        df["estoque_empregos_ti"] = estoque.reindex(df.index).fillna(0)
    df["tem_pos_graduacao_capes"] = df.index.isin(com_pos).astype(int)
    return df.rename_axis("codigo_ibge_municipio").reset_index()


def main(atualizar: bool = False) -> None:
    cursos = carregar_cursos_ti()
    cursos = cursos[(cursos["sigla_uf"] == UF_ALVO) & cursos["ano"].between(ANO_INICIO, ANO_FIM)]
    municipios = carregar_municipios()
    codigo_uf = {sigla: codigo for codigo, sigla in SIGLA_UF.items()}[UF_ALVO]
    com_pos = municipios_com_pos_computacao(carregar_programas(), municipios, UF_ALVO, codigo_uf)

    indicadores = montar_indicadores(cursos, carregar_rais(atualizar), com_pos)
    polos = classificar_polos(calcular_escore(indicadores))
    polos.insert(1, "municipio", polos["codigo_ibge_municipio"].map(
        dict(zip(municipios["codigo_ibge"], municipios["nome"]))
    ))
    polos.to_csv(DATA_PROCESSED_DIR / "polos.csv", index=False)
    print(polos.head(12).round(2).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atualizar", action="store_true", help="refaz a consulta da RAIS")
    main(parser.parse_args().atualizar)
