"""Conexão SQLAlchemy com o PostgreSQL local (docker-compose)."""

from __future__ import annotations

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from tcc_grafos.config import DATABASE_URL


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(DATABASE_URL, pool_pre_ping=True)
