"""Limpeza, harmonização e agregação dos microdados CAGED para empregos_ti."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from tcc_grafos.config import DATA_INTERIM_DIR, PREFIXOS_CBO_TI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# layout antigo (pré e-Social) -> layout novo. TODO: validar nomes reais
COLUNAS_CAGED_ANTIGO_PARA_NOVO = {
    "municipio": "municipio",
    "cbo2002ocupação": "cbo",
    "saldomovimentação": "saldo",
    "salário": "salario",
    "competênciamov": "competencia",
}


def _filtrar_cbo_ti(df: pd.DataFrame, coluna_cbo: str = "cbo") -> pd.DataFrame:
    cbo_str = df[coluna_cbo].astype(str)
    return df.loc[cbo_str.str.startswith(PREFIXOS_CBO_TI)].copy()


def harmonizar_layout_antigo(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=COLUNAS_CAGED_ANTIGO_PARA_NOVO)


def agregar_competencia(df: pd.DataFrame) -> pd.DataFrame:
    df = _filtrar_cbo_ti(df)

    df["admissao"] = (df["saldo"] > 0).astype(int) * df["saldo"].clip(lower=0)
    df["desligamento"] = (df["saldo"] < 0).astype(int) * df["saldo"].clip(upper=0).abs()

    return (
        df.groupby(["competencia", "municipio", "cbo"], dropna=False)
        .agg(
            admissoes=("admissao", "sum"),
            desligamentos=("desligamento", "sum"),
            saldo=("saldo", "sum"),
            salario_medio_nominal=("salario", "mean"),
        )
        .reset_index()
        .rename(columns={"municipio": "codigo_ibge_municipio"})
    )


def processar_arquivo(caminho: Path, layout: str = "novo", destino: Path = DATA_INTERIM_DIR) -> Path:
    df = pd.read_parquet(caminho) if caminho.suffix == ".parquet" else pd.read_csv(caminho, sep=";")

    if layout == "antigo":
        df = harmonizar_layout_antigo(df)

    agregado = agregar_competencia(df)

    destino.mkdir(parents=True, exist_ok=True)
    saida = destino / f"empregos_ti_{caminho.stem}.parquet"
    agregado.to_parquet(saida, index=False)
    logger.info("gravado %s (%d linhas)", saida, len(agregado))
    return saida
