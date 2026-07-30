"""Carga dos DataFrames tratados para as tabelas do PostgreSQL."""

from __future__ import annotations

import logging

import pandas as pd

from tcc_grafos.db.engine import get_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def carregar_tabela(df: pd.DataFrame, nome_tabela: str, if_exists: str = "append") -> int:
    engine = get_engine()
    linhas = df.to_sql(nome_tabela, engine, if_exists=if_exists, index=False, method="multi")
    logger.info("carregadas %s linhas em %s", linhas, nome_tabela)
    return linhas or 0


def carregar_municipios(df: pd.DataFrame) -> int:
    return carregar_tabela(df, "municipios", if_exists="replace")


def carregar_concluintes_ti(df: pd.DataFrame) -> int:
    return carregar_tabela(df, "concluintes_ti")


def carregar_empregos_ti(df: pd.DataFrame) -> int:
    return carregar_tabela(df, "empregos_ti")


def carregar_grafo_arestas(df: pd.DataFrame) -> int:
    return carregar_tabela(df, "grafo_arestas")


def carregar_polos(df: pd.DataFrame) -> int:
    return carregar_tabela(df, "polos")
