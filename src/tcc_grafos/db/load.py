"""Carga dos resultados do pipeline no PostgreSQL.

Rodar com: python -m tcc_grafos.db.load (depois das camadas e do escore de polos)
"""

from __future__ import annotations

import logging

import pandas as pd

from tcc_grafos.config import DATA_PROCESSED_DIR, ROOT_DIR
from tcc_grafos.db.engine import get_engine
from tcc_grafos.etl.municipios import carregar_municipios, tabela_municipios
from tcc_grafos.etl.populacao import carregar_populacao

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQL_DIR = ROOT_DIR / "sql"
VIEWS = ("mv_influenciadores", "mv_resumo_mercado")


def _so_municipios_conhecidos(df: pd.DataFrame, colunas: list[str], codigos: set[int]) -> pd.DataFrame:
    # código inválido na origem quebraria a chave estrangeira
    validas = df[colunas].isin(codigos).all(axis=1)
    if (~validas).any():
        logger.warning("descartadas %d linhas com município desconhecido", (~validas).sum())
    return df[validas]


def montar_tabelas() -> dict[str, pd.DataFrame]:
    """Tabelas na ordem de carga (respeita as chaves estrangeiras)."""
    municipios = tabela_municipios(carregar_municipios())
    codigos = set(municipios["codigo_ibge"])

    arestas = pd.read_parquet(DATA_PROCESSED_DIR / "arestas_sisu_ti.parquet")
    raio = pd.read_csv(DATA_PROCESSED_DIR / "raio_por_municipio_ano.csv").drop(columns="municipio")
    mercado = pd.read_csv(DATA_PROCESSED_DIR / "mercado_por_municipio_ano.csv")
    polos = pd.read_csv(DATA_PROCESSED_DIR / "polos.csv")
    polos = polos[[c for c in polos.columns if c != "municipio" and not c.startswith("z_")]]

    origem_destino = ["codigo_ibge_municipio_origem", "codigo_ibge_municipio_destino"]
    return {
        "municipios": municipios,
        "populacao_municipio": carregar_populacao(),
        "grafo_arestas": _so_municipios_conhecidos(arestas, origem_destino, codigos),
        "raio_atuacao": _so_municipios_conhecidos(
            raio, ["codigo_ibge_municipio_destino"], codigos
        ),
        "mercado_ti_anual": _so_municipios_conhecidos(mercado, ["codigo_ibge"], codigos),
        "polos": polos,
    }


def main() -> None:
    tabelas = montar_tabelas()
    with get_engine().begin() as conn:
        for arquivo in sorted(SQL_DIR.glob("*.sql")):
            conn.exec_driver_sql(arquivo.read_text())
        conn.exec_driver_sql(f"TRUNCATE {', '.join(tabelas)} CASCADE")
        for nome, df in tabelas.items():
            df.to_sql(nome, conn, if_exists="append", index=False, method="multi", chunksize=1000)
            logger.info("%s: %d linhas", nome, len(df))
        for view in VIEWS:
            conn.exec_driver_sql(f"REFRESH MATERIALIZED VIEW {view}")


if __name__ == "__main__":
    main()
