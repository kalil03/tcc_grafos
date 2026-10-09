"""Classificação dos "grandes polos" de TI por escore de z-scores; Campo Mourão
fica isolado como caso de referência (UTFPR-CM)."""

from __future__ import annotations

import pandas as pd

from tcc_grafos.config import CODIGO_IBGE_CAMPO_MOURAO

CAMPOS_ESCORE = [
    "total_concluintes",
    "num_ies_ti",
    "estoque_empregos_ti",
    "tem_pos_graduacao_capes",
]


def _zscore(serie: pd.Series) -> pd.Series:
    desvio = serie.std(ddof=0)
    if desvio == 0 or pd.isna(desvio):
        return pd.Series(0.0, index=serie.index)
    return (serie - serie.mean()) / desvio


def calcular_escore(indicadores_por_municipio: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por (codigo_ibge_municipio, ano_referencia) + colunas de CAMPOS_ESCORE."""
    df = indicadores_por_municipio.copy()
    for campo in CAMPOS_ESCORE:
        df[f"z_{campo}"] = df.groupby("ano_referencia")[campo].transform(_zscore)

    df["score"] = df[[f"z_{c}" for c in CAMPOS_ESCORE]].sum(axis=1)
    df["rank"] = df.groupby("ano_referencia")["score"].rank(ascending=False, method="min")
    return df


def classificar_polos(escores: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Marca is_grande_polo (top-N, sem Campo Mourão) e is_utfpr_cm."""
    df = escores.copy()
    df["is_utfpr_cm"] = df["codigo_ibge_municipio"] == CODIGO_IBGE_CAMPO_MOURAO

    candidatos = df.loc[~df["is_utfpr_cm"]].copy()
    candidatos["rank"] = candidatos.groupby("ano_referencia")["score"].rank(
        ascending=False, method="min"
    )
    df.loc[candidatos.index, "rank"] = candidatos["rank"]
    df["is_grande_polo"] = (~df["is_utfpr_cm"]) & (df["rank"] <= top_n)

    return df
