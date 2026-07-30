"""Testes de sanidade das funções matemáticas puras."""

import math

import pandas as pd

from tcc_grafos.graph.metrics import cagr, calcular_raio_medio_ponderado, distancia_km


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
