"""Deflacionamento dos salários do CAGED via IPCA (série SGS/Bacen 433)."""

from __future__ import annotations

import logging

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACEN_SGS_IPCA_URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados?formato=json"


def baixar_serie_ipca() -> pd.DataFrame:
    resp = requests.get(BACEN_SGS_IPCA_URL, timeout=30)
    resp.raise_for_status()
    df = pd.DataFrame(resp.json())
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = df["valor"].astype(float)
    df = df.rename(columns={"data": "competencia", "valor": "variacao_mensal_pct"})
    df["competencia"] = df["competencia"].dt.to_period("M").dt.to_timestamp()
    df = df.sort_values("competencia").reset_index(drop=True)

    df["numero_indice"] = 100 * (1 + df["variacao_mensal_pct"] / 100).cumprod()
    return df


def deflacionar(
    df_salarios: pd.DataFrame,
    df_ipca: pd.DataFrame,
    coluna_competencia: str = "competencia",
    coluna_salario_nominal: str = "salario_medio_nominal",
    mes_base: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Converte salário nominal em real a preços de `mes_base` (default: último mês)."""
    if mes_base is None:
        mes_base = df_ipca[coluna_competencia].max()

    indice_base = df_ipca.loc[
        df_ipca[coluna_competencia] == mes_base, "numero_indice"
    ].iloc[0]

    merged = df_salarios.merge(
        df_ipca[[coluna_competencia, "numero_indice"]], on=coluna_competencia, how="left"
    )
    merged["salario_medio_real"] = (
        merged[coluna_salario_nominal] * indice_base / merged["numero_indice"]
    )
    return merged
