"""Testes de sanidade das funções matemáticas puras."""

import math

import pandas as pd

from tcc_grafos.graph.arestas import montar_arestas
from tcc_grafos.graph.metrics import (
    cagr,
    calcular_raio_mediano_ponderado,
    calcular_raio_medio_ponderado,
    crescimento_anual_tendencia,
    distancia_km,
    distribuicao_distancia,
    principais_origens,
    raio_por_destino,
)


def test_distancia_km_mesmo_ponto_eh_zero():
    ponto = (-24.0459, -52.3644)  # Campo Mourão
    assert distancia_km(ponto, ponto) == 0


def test_distancia_km_campo_mourao_curitiba_ordem_de_grandeza():
    campo_mourao = (-24.0459, -52.3644)
    curitiba = (-25.4284, -49.2733)
    d = distancia_km(campo_mourao, curitiba)
    assert 250 < d < 400  # real é ~330km; só checando ordem de grandeza


def test_cagr_dobro_em_dez_anos():
    taxa = cagr(100, 200, 10)
    assert math.isclose(taxa, 0.0718, abs_tol=1e-3)


def test_cagr_periodo_zero_retorna_nan():
    assert math.isnan(cagr(100, 200, 0))


def test_raio_medio_ponderado():
    arestas = pd.DataFrame(
        {
            "distancia_km_haversine": [100.0, 300.0],
            "peso_alunos": [3, 1],
        }
    )
    assert calcular_raio_medio_ponderado(arestas) == 150.0


def test_raio_medio_ponderado_vazio_eh_nan():
    vazio = pd.DataFrame(columns=["distancia_km_haversine", "peso_alunos"])
    assert math.isnan(calcular_raio_medio_ponderado(vazio))


def test_raio_ignora_aresta_sem_distancia():
    arestas = pd.DataFrame(
        {"distancia_km_haversine": [100.0, None], "peso_alunos": [1, 9]}
    )
    assert calcular_raio_medio_ponderado(arestas) == 100.0


def test_raio_mediano_resiste_a_outlier():
    arestas = pd.DataFrame(
        {"distancia_km_haversine": [0.0, 10.0, 1000.0], "peso_alunos": [5, 4, 1]}
    )
    assert calcular_raio_mediano_ponderado(arestas) == 0.0
    assert calcular_raio_medio_ponderado(arestas) == 104.0


def test_montar_arestas_soma_ies_e_calcula_distancia():
    coords = {1: (-24.0, -52.0), 2: (-24.0, -52.0)}
    fluxo = pd.DataFrame(
        {
            "ano": [2020, 2020, 2020],
            "sigla_ies": ["A", "B", "A"],
            "origem": ["1", "1", None],
            "destino": ["2", "2", "2"],
            "alunos": [3, 2, 7],
        }
    )
    arestas = montar_arestas(fluxo, coords)
    assert len(arestas) == 1
    assert arestas["peso_alunos"].iloc[0] == 5
    assert arestas["distancia_km_haversine"].iloc[0] == 0


def test_raio_por_destino_agrupa():
    arestas = pd.DataFrame(
        {
            "codigo_ibge_municipio_destino": [1, 1, 2],
            "distancia_km_haversine": [100.0, 300.0, 50.0],
            "peso_alunos": [1, 1, 4],
        }
    )
    r = raio_por_destino(arestas, ["codigo_ibge_municipio_destino"]).set_index(
        "codigo_ibge_municipio_destino"
    )
    assert r.loc[1, "raio_medio_km"] == 200.0
    assert r.loc[2, "alunos"] == 4


def test_distribuicao_distancia_faixas_e_fora_da_uf():
    arestas = pd.DataFrame(
        {
            "codigo_ibge_municipio_destino": [1, 1, 1, 2],
            "codigo_ibge_municipio_origem": [4100001, 4100002, 3500001, 4100001],
            "distancia_km_haversine": [50.0, 200.0, 800.0, 10.0],
            "peso_alunos": [2, 1, 1, 3],
        }
    )
    out = distribuicao_distancia(
        arestas, ["codigo_ibge_municipio_destino"], 41, (100, 300)
    ).set_index("codigo_ibge_municipio_destino")
    assert len(out) == 2
    assert out.loc[1, "ate_100_km"] == 0.5
    assert out.loc[1, "acima_300_km"] == 0.25
    assert out.loc[1, "fora_uf"] == 0.25
    assert out.loc[2, "ate_100_km"] == 1.0


def test_crescimento_tendencia_exponencial_exato():
    anos = pd.Series([2015, 2016, 2017, 2018])
    valores = pd.Series([100.0, 105.0, 110.25, 115.7625])
    assert math.isclose(crescimento_anual_tendencia(anos, valores), 0.05)


def test_crescimento_tendencia_com_poucos_anos_eh_nan():
    assert math.isnan(crescimento_anual_tendencia(pd.Series([1, 2]), pd.Series([1.0, 2.0])))


def test_principais_origens_por_destino():
    arestas = pd.DataFrame(
        {
            "grupo": ["A", "A", "A", "B"],
            "codigo_ibge_municipio_origem": [1, 2, 1, 3],
            "peso_alunos": [2, 5, 1, 4],
        }
    )
    out = principais_origens(arestas, "grupo", top=1)
    assert out["codigo_ibge_municipio_origem"].tolist() == [2, 3]
    assert out["parcela"].tolist() == [5 / 8, 1.0]
