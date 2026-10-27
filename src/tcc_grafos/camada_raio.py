"""Camada 1 (H1, H5, QP1, QP2): raio de atuação e influenciadores via SISU.

Rodar com: python -m tcc_grafos.camada_raio [--atualizar]
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from tcc_grafos.config import DATA_INTERIM_DIR, DATA_PROCESSED_DIR
from tcc_grafos.etl.basedosdados_extract import fluxo_sisu_ti
from tcc_grafos.etl.municipios import carregar_municipios, coordenadas
from tcc_grafos.graph.arestas import montar_arestas
from tcc_grafos.graph.metrics import construir_grafo, influenciadores, raio_por_destino

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ARQUIVO_FLUXO = DATA_INTERIM_DIR / "fluxo_sisu_ti.parquet"


def carregar_fluxo(atualizar: bool = False) -> pd.DataFrame:
    if ARQUIVO_FLUXO.exists() and not atualizar:
        return pd.read_parquet(ARQUIVO_FLUXO)
    fluxo = fluxo_sisu_ti()
    fluxo.to_parquet(ARQUIVO_FLUXO, index=False)
    return fluxo


def main(atualizar: bool = False) -> None:
    fluxo = carregar_fluxo(atualizar)
    municipios = carregar_municipios()
    coords = coordenadas(municipios)
    nomes = dict(zip(municipios["codigo_ibge"], municipios["nome"]))

    arestas = montar_arestas(fluxo, coords)
    arestas_ies = montar_arestas(fluxo, coords, chaves_extras=("sigla_ies",))

    destino = "codigo_ibge_municipio_destino"
    raio_total = raio_por_destino(arestas, [destino])
    raio_anual = raio_por_destino(arestas, [destino, "ano"])
    raio_ies = raio_por_destino(arestas_ies, [destino, "sigla_ies"])
    for tabela in (raio_total, raio_anual, raio_ies):
        tabela.insert(1, "municipio", tabela[destino].map(nomes))

    # soma os anos antes: o DiGraph sobrescreveria o peso da mesma aresta
    periodo = arestas.groupby(["codigo_ibge_municipio_origem", destino], as_index=False).agg(
        peso_alunos=("peso_alunos", "sum"),
        distancia_km_haversine=("distancia_km_haversine", "first"),
    )
    infl = influenciadores(construir_grafo(periodo))
    infl.insert(1, "municipio", infl["codigo_ibge_municipio"].map(nomes))

    arestas.to_parquet(DATA_PROCESSED_DIR / "arestas_sisu_ti.parquet", index=False)
    raio_total.to_csv(DATA_PROCESSED_DIR / "raio_por_municipio.csv", index=False)
    raio_anual.to_csv(DATA_PROCESSED_DIR / "raio_por_municipio_ano.csv", index=False)
    raio_ies.to_csv(DATA_PROCESSED_DIR / "raio_por_ies.csv", index=False)
    infl.to_csv(DATA_PROCESSED_DIR / "influenciadores.csv", index=False)

    logger.info("arestas: %d | destinos: %d", len(arestas), arestas[destino].nunique())
    print(raio_total.sort_values("alunos", ascending=False).head(15).round(1).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atualizar", action="store_true", help="refaz a consulta ao BigQuery")
    main(parser.parse_args().atualizar)
