"""Camada 1 (H1, H5, QP1, QP2): raio de atuação e influenciadores via SISU.

Rodar com: python -m tcc_grafos.camada_raio [--atualizar]
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from tcc_grafos.config import (
    CODIGO_IBGE_CAMPO_MOURAO,
    DATA_INTERIM_DIR,
    DATA_PROCESSED_DIR,
    MUNICIPIOS_POLOS_PROVISORIOS,
    TERMOS_CURSO_TI_SISU,
    UF_ALVO,
)
from tcc_grafos.etl.basedosdados_extract import fluxo_sisu
from tcc_grafos.etl.inep_cursos import REDE_PUBLICA, carregar_cursos_censo, carregar_cursos_ti
from tcc_grafos.etl.municipios import SIGLA_UF, carregar_municipios, coordenadas
from tcc_grafos.graph.arestas import montar_arestas
from tcc_grafos.graph.metrics import (
    construir_grafo,
    distribuicao_distancia,
    influenciadores,
    principais_origens,
    raio_por_destino,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARQUIVO_FLUXO = DATA_INTERIM_DIR / "fluxo_sisu.parquet"
DESTINO = "codigo_ibge_municipio_destino"
MODALIDADE_PRESENCIAL = 1

# H1 compara triênios: as amostras anuais de um campus pequeno são de poucas dezenas
TRIENIOS = {"2017-2019": (2017, 2019), "2020-2022": (2020, 2022)}
FAIXAS_KM = (100, 300)
TOP_ORIGENS = 15


def carregar_fluxo(atualizar: bool = False) -> pd.DataFrame:
    if ARQUIVO_FLUXO.exists() and not atualizar:
        return pd.read_parquet(ARQUIVO_FLUXO)
    fluxo = fluxo_sisu()
    fluxo.to_parquet(ARQUIVO_FLUXO, index=False)
    return fluxo


def recorte_ti(
    sisu: pd.DataFrame, cursos_ti: set[tuple[int, int]], cursos_censo: set[tuple[int, int]]
) -> pd.DataFrame:
    """Cursos de TI pelo par (código INEP do curso, município do campus).

    O código sozinho não basta: o SISU tem códigos inválidos que coincidem com cursos
    de TI de outros municípios (ex.: Matemática com o código de uma Ciência da
    Computação de MT). Par que não existe no Censo é erro de registro e cai no nome.
    """
    pares = list(zip(
        pd.to_numeric(sisu["id_curso"], errors="coerce"),
        pd.to_numeric(sisu["destino"], errors="coerce"),
    ))
    eh_ti = pd.Series([p in cursos_ti for p in pares], index=sisu.index)
    existe = pd.Series([p in cursos_censo for p in pares], index=sisu.index)
    pelo_nome = sisu["nome_curso"].str.contains("|".join(TERMOS_CURSO_TI_SISU), na=False)
    return sisu[eh_ti | (~existe & pelo_nome)]


def com_trienio(arestas: pd.DataFrame) -> pd.DataFrame:
    trienio = pd.Series(pd.NA, index=arestas.index, dtype="object")
    for nome, (inicio, fim) in TRIENIOS.items():
        trienio[arestas["ano"].between(inicio, fim)] = nome
    return arestas.assign(trienio=trienio).dropna(subset=["trienio"])


def oferta_publica_ti(cursos: pd.DataFrame) -> pd.DataFrame:
    """(município, ano) com curso de TI público e presencial oferecendo vagas."""
    tem_oferta = (
        (cursos["rede"] == REDE_PUBLICA)
        & (cursos["modalidade"] == MODALIDADE_PRESENCIAL)
        & (cursos["vagas"] > 0)
    )
    oferta = cursos.loc[tem_oferta, ["codigo_ibge", "ano"]].dropna().drop_duplicates()
    return oferta.astype({"codigo_ibge": "int64"})


def democratizacao(arestas: pd.DataFrame, oferta: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """H5: parcela dos alunos vindos de municípios sem oferta pública de TI no ano."""
    marcadas = arestas.merge(
        oferta.rename(columns={"codigo_ibge": "codigo_ibge_municipio_origem"}).assign(
            origem_tem_oferta=True
        ),
        on=["codigo_ibge_municipio_origem", "ano"],
        how="left",
    )
    marcadas["sem_oferta"] = marcadas["peso_alunos"].where(
        marcadas["origem_tem_oferta"].isna(), 0
    )
    out = marcadas.groupby(chaves, as_index=False).agg(
        alunos=("peso_alunos", "sum"), alunos_sem_oferta_publica=("sem_oferta", "sum")
    )
    out["pct_sem_oferta_publica"] = out["alunos_sem_oferta_publica"] / out["alunos"]
    return out


def cobertura_sisu(arestas_ies: pd.DataFrame, cursos: pd.DataFrame) -> pd.DataFrame:
    """Matrículas 'Efetivada' do SISU / ingressantes via ENEM declarados pela IES ao Censo.

    Mede quanto da entrada real o SISU registra como efetivada, por campus e ano.
    """
    sisu = arestas_ies.groupby(["ano", DESTINO, "sigla_ies"], as_index=False)["peso_alunos"].sum()
    publicos = cursos[
        (cursos["rede"] == REDE_PUBLICA) & (cursos["modalidade"] == MODALIDADE_PRESENCIAL)
    ]
    censo = (
        publicos.dropna(subset=["codigo_ibge"])
        .astype({"codigo_ibge": "int64"})
        .groupby(["ano", "codigo_ibge", "sigla_ies"], as_index=False)["ingressantes_enem"]
        .sum()
        .rename(columns={"codigo_ibge": DESTINO})
    )
    out = sisu.merge(censo, on=["ano", DESTINO, "sigla_ies"], how="left")
    out["cobertura"] = out["peso_alunos"] / out["ingressantes_enem"].where(
        out["ingressantes_enem"] > 0
    )
    return out.rename(columns={"peso_alunos": "sisu_efetivada"})


def main(atualizar: bool = False) -> None:
    cursos = carregar_cursos_ti()
    pares_ti = cursos[["co_curso", "codigo_ibge"]].dropna().astype("int64")
    sisu_ti = recorte_ti(
        carregar_fluxo(atualizar),
        set(zip(pares_ti["co_curso"], pares_ti["codigo_ibge"])),
        carregar_cursos_censo(),
    )
    fluxo = sisu_ti[sisu_ti["efetivada"].fillna(False).astype(bool)]
    municipios = carregar_municipios()
    coords = coordenadas(municipios)
    nomes = dict(zip(municipios["codigo_ibge"], municipios["nome"]))
    codigo_uf = {sigla: codigo for codigo, sigla in SIGLA_UF.items()}[UF_ALVO]

    arestas = montar_arestas(fluxo, coords)
    arestas_ies = montar_arestas(fluxo, coords, chaves_extras=("sigla_ies",))

    raio_total = raio_por_destino(arestas, [DESTINO])
    raio_anual = raio_por_destino(arestas, [DESTINO, "ano"])
    raio_trienio = raio_por_destino(com_trienio(arestas), [DESTINO, "trienio"])
    raio_ies = raio_por_destino(arestas_ies, [DESTINO, "sigla_ies"])
    # sensibilidade: raio de todos os aprovados, porque parte dos matriculados fica
    # sem registro no Sisu Gestão
    aprovados = montar_arestas(
        sisu_ti[sisu_ti["status_aprovado"].fillna(False).astype(bool)], coords,
        chaves_extras=("sigla_ies",),
    )
    raio_ies_aprovados = raio_por_destino(aprovados, [DESTINO, "sigla_ies"])
    distribuicao = distribuicao_distancia(arestas_ies, [DESTINO, "sigla_ies"], codigo_uf, FAIXAS_KM)
    oferta = oferta_publica_ti(cursos)
    democ = democratizacao(arestas_ies, oferta, [DESTINO, "sigla_ies"])
    democ_trienio = democratizacao(com_trienio(arestas_ies), oferta, [DESTINO, "sigla_ies", "trienio"])
    cobertura = cobertura_sisu(arestas_ies, cursos)
    tabelas = (raio_total, raio_anual, raio_trienio, raio_ies, raio_ies_aprovados, distribuicao,
               democ, democ_trienio, cobertura)
    for tabela in tabelas:
        tabela.insert(1, "municipio", tabela[DESTINO].map(nomes))

    # soma os anos antes: o DiGraph sobrescreveria o peso da mesma aresta
    periodo = arestas.groupby(["codigo_ibge_municipio_origem", DESTINO], as_index=False).agg(
        peso_alunos=("peso_alunos", "sum"),
        distancia_km_haversine=("distancia_km_haversine", "first"),
    )
    infl = influenciadores(construir_grafo(periodo))
    infl.insert(1, "municipio", infl["codigo_ibge_municipio"].map(nomes))
    # QP2: quem exporta alunos para o campus e para os grandes polos
    grupos = {CODIGO_IBGE_CAMPO_MOURAO: "UTFPR-CM"}
    grupos.update({m: "grandes polos" for m in MUNICIPIOS_POLOS_PROVISORIOS})
    por_grupo = periodo.assign(grupo_destino=periodo[DESTINO].map(grupos)).dropna(
        subset=["grupo_destino"]
    )
    origens = principais_origens(por_grupo, "grupo_destino", TOP_ORIGENS)
    origens.insert(2, "municipio_origem", origens["codigo_ibge_municipio_origem"].map(nomes))

    arestas.to_parquet(DATA_PROCESSED_DIR / "arestas_sisu_ti.parquet", index=False)
    raio_total.to_csv(DATA_PROCESSED_DIR / "raio_por_municipio.csv", index=False)
    raio_anual.to_csv(DATA_PROCESSED_DIR / "raio_por_municipio_ano.csv", index=False)
    raio_trienio.to_csv(DATA_PROCESSED_DIR / "raio_por_municipio_trienio.csv", index=False)
    raio_ies.to_csv(DATA_PROCESSED_DIR / "raio_por_ies.csv", index=False)
    raio_ies_aprovados.to_csv(DATA_PROCESSED_DIR / "raio_por_ies_aprovados.csv", index=False)
    distribuicao.to_csv(DATA_PROCESSED_DIR / "distribuicao_distancia_por_ies.csv", index=False)
    democ.to_csv(DATA_PROCESSED_DIR / "democratizacao_por_ies.csv", index=False)
    democ_trienio.to_csv(DATA_PROCESSED_DIR / "democratizacao_por_ies_trienio.csv", index=False)
    cobertura.to_csv(DATA_PROCESSED_DIR / "cobertura_sisu.csv", index=False)
    infl.to_csv(DATA_PROCESSED_DIR / "influenciadores.csv", index=False)
    origens.to_csv(DATA_PROCESSED_DIR / "principais_origens.csv", index=False)

    logger.info("arestas: %d | destinos: %d", len(arestas), arestas[DESTINO].nunique())
    print(raio_total.sort_values("alunos", ascending=False).head(15).round(1).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atualizar", action="store_true", help="refaz a consulta ao BigQuery")
    main(parser.parse_args().atualizar)
