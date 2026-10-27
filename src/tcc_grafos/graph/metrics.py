"""Métricas geométricas e de rede do grafo município-a-município (QP1 e QP2)."""

from __future__ import annotations

import networkx as nx
import pandas as pd
from haversine import Unit, haversine


def distancia_km(origem: tuple[float, float], destino: tuple[float, float]) -> float:
    return haversine(origem, destino, unit=Unit.KILOMETERS)


def _com_distancia(arestas: pd.DataFrame) -> pd.DataFrame:
    # aresta sem distância (município sem coordenada) sai do numerador e do denominador
    return arestas.dropna(subset=["distancia_km_haversine"])


def calcular_raio_medio_ponderado(arestas: pd.DataFrame) -> float:
    """Raio médio ponderado pelo nº de alunos em cada aresta."""
    arestas = _com_distancia(arestas)
    if arestas.empty or arestas["peso_alunos"].sum() == 0:
        return float("nan")
    return (arestas["distancia_km_haversine"] * arestas["peso_alunos"]).sum() / arestas[
        "peso_alunos"
    ].sum()


def calcular_raio_mediano_ponderado(arestas: pd.DataFrame) -> float:
    """Distância do aluno mediano (menos sensível a poucos alunos vindos de longe)."""
    arestas = _com_distancia(arestas)
    if arestas.empty or arestas["peso_alunos"].sum() == 0:
        return float("nan")
    ordenado = arestas.sort_values("distancia_km_haversine")
    acumulado = ordenado["peso_alunos"].cumsum()
    metade = ordenado["peso_alunos"].sum() / 2
    return float(ordenado.loc[acumulado >= metade, "distancia_km_haversine"].iloc[0])


def raio_por_destino(arestas: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """Raio médio e mediano por grupo (ex.: município de destino e ano)."""
    linhas = []
    for valores, grupo in arestas.groupby(chaves):
        valores = valores if isinstance(valores, tuple) else (valores,)
        linhas.append(
            {
                **dict(zip(chaves, valores)),
                "alunos": int(grupo["peso_alunos"].sum()),
                "raio_medio_km": calcular_raio_medio_ponderado(grupo),
                "raio_mediano_km": calcular_raio_mediano_ponderado(grupo),
            }
        )
    return pd.DataFrame(linhas)


def cagr(valor_inicial: float, valor_final: float, num_periodos: int) -> float:
    if valor_inicial <= 0 or num_periodos <= 0:
        return float("nan")
    return (valor_final / valor_inicial) ** (1 / num_periodos) - 1


def construir_grafo(arestas: pd.DataFrame) -> nx.DiGraph:
    g = nx.DiGraph()
    for row in arestas.itertuples(index=False):
        g.add_edge(
            row.codigo_ibge_municipio_origem,
            row.codigo_ibge_municipio_destino,
            weight=row.peso_alunos,
            distancia_km=row.distancia_km_haversine,
        )
    return g


def influenciadores(g: nx.DiGraph) -> pd.DataFrame:
    """Ranking de municípios por in-degree/out-degree ponderados (QP2)."""
    in_deg = dict(g.in_degree(weight="weight"))
    out_deg = dict(g.out_degree(weight="weight"))
    municipios = sorted(set(in_deg) | set(out_deg))
    return pd.DataFrame(
        {
            "codigo_ibge_municipio": municipios,
            "in_degree_ponderado": [in_deg.get(m, 0) for m in municipios],
            "out_degree_ponderado": [out_deg.get(m, 0) for m in municipios],
        }
    ).sort_values("in_degree_ponderado", ascending=False)
