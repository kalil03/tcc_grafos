"""Classificação dos "grandes polos" de TI por escore de z-scores; Campo Mourão
fica isolado como caso de referência (UTFPR-CM)."""

from __future__ import annotations

import pandas as pd

from tcc_grafos.config import CODIGO_IBGE_CAMPO_MOURAO

# critérios (a)-(d) da proposta
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


def calcular_escore(indicadores: pd.DataFrame, campos: list[str] = CAMPOS_ESCORE) -> pd.DataFrame:
    """Uma linha por codigo_ibge_municipio (indicadores do período) + colunas de `campos`."""
    df = indicadores.copy()
    for campo in campos:
        df[f"z_{campo}"] = _zscore(df[campo].astype(float))
    df["score"] = df[[f"z_{c}" for c in campos]].sum(axis=1)
    return df


def classificar_polos(escores: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """Marca is_grande_polo (top-N, sem Campo Mourão) e is_utfpr_cm."""
    df = escores.copy()
    df["is_utfpr_cm"] = df["codigo_ibge_municipio"] == CODIGO_IBGE_CAMPO_MOURAO
    df["rank"] = df["score"].where(~df["is_utfpr_cm"]).rank(ascending=False, method="min")
    df["is_grande_polo"] = df["rank"] <= top_n
    return df.sort_values("score", ascending=False).reset_index(drop=True)
