"""Métricas geométricas e de rede do grafo município-a-município (QP1 e QP2)."""

from __future__ import annotations

import networkx as nx
import numpy as np
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


def ic_raio_mediano(
    arestas: pd.DataFrame, reamostras: int = 2000, semente: int = 0
) -> tuple[float, float]:
    """IC de 95% do raio mediano por bootstrap, reamostrando alunos.

    Usa a mesma mediana de `calcular_raio_mediano_ponderado` (a menor distância que
    alcança metade dos alunos).
    """
    arestas = _com_distancia(arestas)
    distancias = np.repeat(
        arestas["distancia_km_haversine"].to_numpy(), arestas["peso_alunos"].to_numpy(dtype=int)
    )
    if distancias.size == 0:
        return float("nan"), float("nan")
    gerador = np.random.default_rng(semente)
    amostras = gerador.choice(distancias, size=(reamostras, distancias.size), replace=True)
    medianas = np.quantile(amostras, 0.5, axis=1, method="inverted_cdf")
    inferior, superior = np.quantile(medianas, [0.025, 0.975])
    return float(inferior), float(superior)


def raio_por_destino(arestas: pd.DataFrame, chaves: list[str]) -> pd.DataFrame:
    """Raio médio e mediano (com IC de 95% da mediana) por grupo, ex.: destino e ano."""
    linhas = []
    for valores, grupo in arestas.groupby(chaves):
        valores = valores if isinstance(valores, tuple) else (valores,)
        inferior, superior = ic_raio_mediano(grupo)
        linhas.append(
            {
                **dict(zip(chaves, valores)),
                "alunos": int(grupo["peso_alunos"].sum()),
                "raio_medio_km": calcular_raio_medio_ponderado(grupo),
                "raio_mediano_km": calcular_raio_mediano_ponderado(grupo),
                "raio_mediano_ic95_inf": inferior,
                "raio_mediano_ic95_sup": superior,
            }
        )
    return pd.DataFrame(linhas)


def distribuicao_distancia(
    arestas: pd.DataFrame, chaves: list[str], codigo_uf: int, limites_km: tuple[float, ...]
) -> pd.DataFrame:
    """Parcela dos alunos por faixa de distância e parcela vinda de fora da UF, por grupo.

    A média e a mediana escondem a atração bimodal (muito local + muito de longe).
    """
    df = _com_distancia(arestas).copy()
    bordas = [0, *limites_km, float("inf")]
    rotulos = [f"ate_{int(b)}_km" for b in limites_km] + [f"acima_{int(limites_km[-1])}_km"]
    # string, não categoria: groupby com categoria cruza todas as combinações das chaves
    df["faixa"] = pd.cut(
        df["distancia_km_haversine"], bordas, labels=rotulos, right=True, include_lowest=True
    ).astype(str)
    df["fora_uf"] = df["codigo_ibge_municipio_origem"] // 100_000 != codigo_uf

    total = df.groupby(chaves)["peso_alunos"].sum()
    faixas = (
        df.groupby([*chaves, "faixa"])["peso_alunos"].sum().unstack("faixa")
        .reindex(columns=rotulos).fillna(0)
    )
    out = faixas.div(total, axis=0)
    out["fora_uf"] = df[df["fora_uf"]].groupby(chaves)["peso_alunos"].sum().reindex(
        total.index, fill_value=0
    ) / total
    out.insert(0, "alunos", total)
    return out.reset_index()


def cagr(valor_inicial: float, valor_final: float, num_periodos: int) -> float:
    if valor_inicial <= 0 or num_periodos <= 0:
        return float("nan")
    return (valor_final / valor_inicial) ** (1 / num_periodos) - 1


def crescimento_anual_tendencia(anos: pd.Series, valores: pd.Series) -> float:
    """Taxa anual do ajuste log-linear: usa todos os anos, não só as pontas como o CAGR."""
    validos = valores.notna() & (valores > 0)
    if validos.sum() < 3:
        return float("nan")
    inclinacao = np.polyfit(anos[validos].astype(float), np.log(valores[validos]), 1)[0]
    return float(np.exp(inclinacao) - 1)


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


def principais_origens(arestas: pd.DataFrame, chave_destino: str, top: int) -> pd.DataFrame:
    """QP2 por destino: os `top` municípios que mais enviam alunos a cada destino.

    É o out-degree ponderado de cada origem restrito às arestas que chegam ao destino.
    """
    por_origem = arestas.groupby([chave_destino, "codigo_ibge_municipio_origem"], as_index=False)[
        "peso_alunos"
    ].sum()
    por_origem["parcela"] = por_origem["peso_alunos"] / por_origem.groupby(chave_destino)[
        "peso_alunos"
    ].transform("sum")
    por_origem["posicao"] = por_origem.groupby(chave_destino)["peso_alunos"].rank(
        ascending=False, method="first"
    )
    return por_origem[por_origem["posicao"] <= top].sort_values([chave_destino, "posicao"])


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
