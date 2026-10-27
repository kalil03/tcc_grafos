"""Camada 2 (H2, H3, H4, H6, QP3): mercado, densidade e absorção por município e ano.

Rodar com: python -m tcc_grafos.camada_mercado [--atualizar]
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from tcc_grafos.config import (
    ANO_FIM,
    ANO_INICIO,
    CODIGO_IBGE_CAMPO_MOURAO,
    DATA_INTERIM_DIR,
    DATA_PROCESSED_DIR,
    MUNICIPIOS_POLOS_PROVISORIOS,
)
from tcc_grafos.etl.basedosdados_extract import concluintes_ti_por_municipio, mercado_ti_caged
from tcc_grafos.etl.ipca import baixar_serie_ipca
from tcc_grafos.etl.municipios import carregar_municipios
from tcc_grafos.etl.populacao import carregar_populacao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODALIDADE_PRESENCIAL = "1"


def indice_ipca_anual(ipca: pd.DataFrame) -> pd.Series:
    return ipca.groupby(ipca["competencia"].dt.year)["numero_indice"].mean()


def deflacionar(valores: pd.Series, anos: pd.Series, indice: pd.Series, ano_base: int) -> pd.Series:
    """Converte valores nominais anuais para preços do ano-base."""
    return valores * indice[ano_base] / anos.map(indice)


def agregar_concluintes(concluintes: pd.DataFrame) -> pd.DataFrame:
    df = concluintes.copy()
    presencial = df["tipo_modalidade_ensino"].astype(str) == MODALIDADE_PRESENCIAL
    df["concluintes_presencial"] = df["quantidade_concluintes"].where(presencial, 0)
    return (
        df.groupby(["id_municipio", "ano"], as_index=False)
        .agg(
            concluintes_total=("quantidade_concluintes", "sum"),
            concluintes_presencial=("concluintes_presencial", "sum"),
        )
    )


def consolidar(
    concluintes: pd.DataFrame,
    caged: pd.DataFrame,
    populacao: pd.DataFrame,
    indice_ipca: pd.Series,
    ano_base: int,
) -> pd.DataFrame:
    """Uma linha por município e ano com os indicadores das hipóteses H2, H3, H4 e H6."""
    conc = agregar_concluintes(concluintes)
    df = conc.merge(caged, on=["id_municipio", "ano"], how="outer")
    df["codigo_ibge"] = df.pop("id_municipio").astype("int64")
    df = df.merge(populacao, on=["codigo_ibge", "ano"], how="left")

    contagens = ["concluintes_total", "concluintes_presencial", "admissoes", "desligamentos", "saldo"]
    df[contagens] = df[contagens].fillna(0).astype("Int64")
    # ano que o Censo ainda não publicou fica sem dado, não zero
    sem_censo = ~df["ano"].isin(concluintes["ano"].unique())
    df.loc[sem_censo, ["concluintes_total", "concluintes_presencial"]] = pd.NA

    df["salario_real"] = deflacionar(df["salario_nominal"], df["ano"], indice_ipca, ano_base)
    df["concl_presencial_por_100k"] = df["concluintes_presencial"] / df["populacao"] * 1e5
    df["saldo_ti_por_100k"] = df["saldo"] / df["populacao"] * 1e5
    # vagas de TI criadas por formando presencial no mesmo município (H6)
    df["vagas_por_formando"] = df["saldo"] / df["concluintes_presencial"].where(
        df["concluintes_presencial"] > 0
    )
    colunas = ["codigo_ibge", "ano", "populacao", *contagens, "salario_nominal", "salario_real",
               "concl_presencial_por_100k", "saldo_ti_por_100k", "vagas_por_formando"]
    return df[colunas].sort_values(["codigo_ibge", "ano"]).reset_index(drop=True)


def resumo_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """Indicadores do período inteiro por município (razões das somas, não média de razões).

    vagas_por_formando só usa os anos em que existem formandos e CAGED.
    """
    out = df.groupby("codigo_ibge").agg(
        saldo=("saldo", "sum"),
        salario_real_medio=("salario_real", "mean"),
        concl_presencial_por_100k=("concl_presencial_por_100k", "mean"),
    )
    com_censo = df[df["concluintes_presencial"].notna()].groupby("codigo_ibge")
    formandos = com_censo["concluintes_presencial"].sum().astype(float)
    out["concluintes_presencial"] = formandos
    out["vagas_por_formando"] = com_censo["saldo"].sum() / formandos.where(formandos > 0)
    return out.reset_index()


def _cache(nome: str, buscar, atualizar: bool) -> pd.DataFrame:
    arquivo = DATA_INTERIM_DIR / f"{nome}.parquet"
    if arquivo.exists() and not atualizar:
        return pd.read_parquet(arquivo)
    df = buscar()
    df.to_parquet(arquivo, index=False)
    return df


def main(atualizar: bool = False) -> None:
    concluintes = _cache(
        "concluintes_ti", lambda: concluintes_ti_por_municipio(ANO_INICIO), atualizar
    )
    caged = _cache("caged_ti", mercado_ti_caged, atualizar)
    concluintes = concluintes[concluintes["ano"].between(ANO_INICIO, ANO_FIM)]
    populacao = carregar_populacao(atualizar=atualizar)
    indice = indice_ipca_anual(baixar_serie_ipca())

    df = consolidar(concluintes, caged, populacao, indice, ano_base=ANO_FIM)
    df.to_csv(DATA_PROCESSED_DIR / "mercado_por_municipio_ano.csv", index=False)

    resumo = resumo_periodo(df)
    resumo.to_csv(DATA_PROCESSED_DIR / "mercado_resumo_periodo.csv", index=False)

    municipios = carregar_municipios()
    nomes = dict(zip(municipios["codigo_ibge"], municipios["nome"]))
    alvo = [CODIGO_IBGE_CAMPO_MOURAO, *MUNICIPIOS_POLOS_PROVISORIOS]
    tabela = resumo[resumo["codigo_ibge"].isin(alvo)].copy()
    tabela.insert(1, "municipio", tabela["codigo_ibge"].map(nomes))
    logger.info("salário real a preços de %d", ANO_FIM)
    print(tabela.drop(columns="codigo_ibge").round(1).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atualizar", action="store_true", help="refaz as consultas")
    main(parser.parse_args().atualizar)
