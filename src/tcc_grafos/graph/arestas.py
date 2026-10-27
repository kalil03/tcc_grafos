"""Arestas do grafo município-a-município a partir de um fluxo origem -> destino."""

from __future__ import annotations

import pandas as pd

from tcc_grafos.graph.metrics import distancia_km


def montar_arestas(
    fluxo: pd.DataFrame,
    coordenadas: dict[int, tuple[float, float]],
    chaves_extras: tuple[str, ...] = (),
) -> pd.DataFrame:
    """Fluxo com (ano, origem, destino, alunos) -> arestas com distância Haversine.

    `chaves_extras` mantém colunas adicionais no agrupamento (ex.: sigla_ies).
    """
    df = fluxo.copy()
    for col in ("origem", "destino"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["origem", "destino"]).astype({"origem": "int64", "destino": "int64"})

    chaves = ["ano", *chaves_extras, "origem", "destino"]
    arestas = (
        df.groupby(chaves, as_index=False)["alunos"]
        .sum()
        .rename(
            columns={
                "origem": "codigo_ibge_municipio_origem",
                "destino": "codigo_ibge_municipio_destino",
                "alunos": "peso_alunos",
            }
        )
    )

    def _distancia(row: pd.Series) -> float | None:
        o = coordenadas.get(row["codigo_ibge_municipio_origem"])
        d = coordenadas.get(row["codigo_ibge_municipio_destino"])
        return distancia_km(o, d) if o and d else None

    arestas["distancia_km_haversine"] = arestas.apply(_distancia, axis=1)
    return arestas
