"""Monta as arestas do grafo município-a-município a partir de concluintes_ti."""

from __future__ import annotations

import pandas as pd

from tcc_grafos.graph.metrics import distancia_km


def montar_arestas(
    concluintes: pd.DataFrame,
    coordenadas_municipio: dict[int, tuple[float, float]],
) -> pd.DataFrame:
    """Agrega concluintes em arestas (ano, origem, destino, peso, distância)."""
    agregado = (
        concluintes.groupby(
            [
                "ano_censo",
                "codigo_ibge_municipio_nascimento",
                "codigo_ibge_municipio_curso",
            ],
            dropna=False,
        )["quantidade"]
        .sum()
        .reset_index()
        .rename(
            columns={
                "ano_censo": "ano",
                "codigo_ibge_municipio_nascimento": "codigo_ibge_municipio_origem",
                "codigo_ibge_municipio_curso": "codigo_ibge_municipio_destino",
                "quantidade": "peso_alunos",
            }
        )
    )

    # sem município de origem não dá pra calcular distância nem montar vértice
    agregado = agregado.dropna(subset=["codigo_ibge_municipio_origem"])

    def _distancia(row: pd.Series) -> float | None:
        origem = coordenadas_municipio.get(int(row["codigo_ibge_municipio_origem"]))
        destino = coordenadas_municipio.get(int(row["codigo_ibge_municipio_destino"]))
        if origem is None or destino is None:
            return None
        return distancia_km(origem, destino)

    agregado["distancia_km_haversine"] = agregado.apply(_distancia, axis=1)
    return agregado
