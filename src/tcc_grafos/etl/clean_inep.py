"""Limpeza e agregação dos microdados INEP para a tabela concluintes_ti."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from tcc_grafos.config import CODIGOS_CINE_TI, DATA_INTERIM_DIR, UF_ALVO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COLUNAS_INEP = [
    "NU_ANO_CENSO",
    "CO_MUNICIPIO_NASCIMENTO",
    "CO_MUNICIPIO_CURSO",
    "SG_UF_CURSO",
    "CO_IES",
    "CO_CINE_ROTULO",  # TODO: confirmar nome da coluna no layout do ano
    "QT_CONCLUINTE",
]


def carregar_bruto(caminho_csv: Path, **read_kwargs) -> pd.DataFrame:
    defaults = {"sep": ";", "encoding": "latin-1", "usecols": lambda c: c in COLUNAS_INEP}
    defaults.update(read_kwargs)
    return pd.read_csv(caminho_csv, **defaults)


def filtrar_ti_pr(df: pd.DataFrame) -> pd.DataFrame:
    filtro_uf = df["SG_UF_CURSO"] == UF_ALVO
    filtro_curso = df["CO_CINE_ROTULO"].astype(str).isin(CODIGOS_CINE_TI.keys())
    return df.loc[filtro_uf & filtro_curso].copy()


def agregar_concluintes(df: pd.DataFrame) -> pd.DataFrame:
    chaves = [
        "NU_ANO_CENSO",
        "CO_MUNICIPIO_NASCIMENTO",
        "CO_MUNICIPIO_CURSO",
        "CO_IES",
        "CO_CINE_ROTULO",
    ]
    return (
        df.groupby(chaves, dropna=False)["QT_CONCLUINTE"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "NU_ANO_CENSO": "ano_censo",
                "CO_MUNICIPIO_NASCIMENTO": "codigo_ibge_municipio_nascimento",
                "CO_MUNICIPIO_CURSO": "codigo_ibge_municipio_curso",
                "CO_IES": "codigo_ies",
                "CO_CINE_ROTULO": "codigo_curso_cine",
                "QT_CONCLUINTE": "quantidade",
            }
        )
    )


def processar_ano(caminho_csv: Path, destino: Path = DATA_INTERIM_DIR) -> Path:
    df = carregar_bruto(caminho_csv)
    df = filtrar_ti_pr(df)
    df = agregar_concluintes(df)

    destino.mkdir(parents=True, exist_ok=True)
    saida = destino / f"concluintes_ti_{caminho_csv.stem}.parquet"
    df.to_parquet(saida, index=False)
    logger.info("gravado %s (%d linhas)", saida, len(df))
    return saida
