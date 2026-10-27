import math

import pandas as pd

from tcc_grafos.camada_mercado import agregar_concluintes, consolidar, deflacionar, resumo_periodo
from tcc_grafos.etl.populacao import completar_anos


def test_deflacionar_leva_ao_ano_base():
    indice = pd.Series({2020: 100.0, 2024: 125.0})
    real = deflacionar(pd.Series([1000.0, 1250.0]), pd.Series([2020, 2024]), indice, 2024)
    assert list(real) == [1250.0, 1250.0]


def test_agregar_concluintes_separa_presencial():
    conc = pd.DataFrame(
        {
            "id_municipio": ["1", "1"],
            "ano": [2020, 2020],
            "tipo_modalidade_ensino": ["1", "2"],
            "quantidade_concluintes": [10, 90],
        }
    )
    out = agregar_concluintes(conc).iloc[0]
    assert out["concluintes_total"] == 100
    assert out["concluintes_presencial"] == 10


def test_completar_anos_interpola_o_buraco():
    pop = pd.DataFrame({"codigo_ibge": [1, 1], "ano": [2022, 2024], "populacao": [100, 120]})
    out = completar_anos(pop, range(2021, 2026)).set_index("ano")["populacao"]
    assert out[2023] == 110
    assert out[2021] == 100
    assert out[2025] == 120


def test_consolidar_calcula_indicadores():
    conc = pd.DataFrame(
        {"id_municipio": ["1"], "ano": [2024], "tipo_modalidade_ensino": ["1"],
         "quantidade_concluintes": [20]}
    )
    caged = pd.DataFrame(
        {"id_municipio": ["1"], "ano": [2024], "admissoes": [30], "desligamentos": [20],
         "saldo": [10], "salario_nominal": [4000.0]}
    )
    pop = pd.DataFrame({"codigo_ibge": [1], "ano": [2024], "populacao": [100_000]})
    indice = pd.Series({2024: 100.0})
    linha = consolidar(conc, caged, pop, indice, 2024).iloc[0]
    assert linha["concl_presencial_por_100k"] == 20
    assert linha["vagas_por_formando"] == 0.5
    assert linha["salario_real"] == 4000.0


def test_resumo_sem_formando_nao_divide_por_zero():
    df = pd.DataFrame(
        {"codigo_ibge": [1], "saldo": [5], "concluintes_presencial": [0],
         "salario_real": [3000.0], "concl_presencial_por_100k": [0.0]}
    )
    assert math.isnan(resumo_periodo(df)["vagas_por_formando"].iloc[0])


def test_ano_sem_censo_nao_entra_como_zero():
    conc = pd.DataFrame(
        {"id_municipio": ["1"], "ano": [2024], "tipo_modalidade_ensino": ["1"],
         "quantidade_concluintes": [10]}
    )
    caged = pd.DataFrame(
        {"id_municipio": ["1", "1"], "ano": [2024, 2025], "admissoes": [5, 50],
         "desligamentos": [0, 0], "saldo": [5, 50], "salario_nominal": [1.0, 1.0]}
    )
    pop = pd.DataFrame({"codigo_ibge": [1, 1], "ano": [2024, 2025], "populacao": [1000, 1000]})
    indice = pd.Series({2024: 1.0, 2025: 1.0})
    df = consolidar(conc, caged, pop, indice, 2025)
    assert pd.isna(df.set_index("ano").loc[2025, "concluintes_presencial"])
    assert resumo_periodo(df)["vagas_por_formando"].iloc[0] == 0.5
