import math

import pandas as pd

from tcc_grafos.camada_mercado import (
    agregar_concluintes,
    consolidar,
    crescimento_salario,
    deflacionar,
    resumo_periodo,
)
from tcc_grafos.config import CODIGO_IBGE_CAMPO_MOURAO, CURSOS_UTFPR_CM
from tcc_grafos.etl.populacao import completar_anos


def _cursos(**colunas):
    base = {"codigo_ibge": [1], "ano": [2024], "co_curso": [10], "modalidade": [1],
            "concluintes": [20]}
    base.update(colunas)
    return pd.DataFrame(base)


def _caged(**colunas):
    base = {"id_municipio": ["1"], "ano": [2024], "admissoes": [30], "desligamentos": [20],
            "saldo": [10], "salario_nominal": [4000.0], "admissoes_jovens_graduados": [4]}
    base.update(colunas)
    return pd.DataFrame(base)


def test_deflacionar_leva_ao_ano_base():
    indice = pd.Series({2020: 100.0, 2024: 125.0})
    real = deflacionar(pd.Series([1000.0, 1250.0]), pd.Series([2020, 2024]), indice, 2024)
    assert list(real) == [1250.0, 1250.0]


def test_agregar_concluintes_separa_presencial():
    cursos = _cursos(codigo_ibge=[1, 1], ano=[2020, 2020], co_curso=[10, 11],
                     modalidade=[1, 2], concluintes=[10, 90])
    out = agregar_concluintes(cursos).iloc[0]
    assert out["concluintes_total"] == 100
    assert out["concluintes_presencial"] == 10


def test_campo_mourao_so_conta_o_curso_da_utfpr():
    cm = CODIGO_IBGE_CAMPO_MOURAO
    cursos = _cursos(codigo_ibge=[cm, cm], ano=[2020, 2020],
                     co_curso=[CURSOS_UTFPR_CM[0], 999], modalidade=[1, 1], concluintes=[15, 40])
    out = agregar_concluintes(cursos).iloc[0]
    assert out["concluintes_presencial"] == 15
    assert out["concluintes_presencial_municipio"] == 55


def test_completar_anos_interpola_o_buraco():
    pop = pd.DataFrame({"codigo_ibge": [1, 1], "ano": [2022, 2024], "populacao": [100, 120]})
    out = completar_anos(pop, range(2021, 2026)).set_index("ano")["populacao"]
    assert out[2023] == 110
    assert out[2021] == 100
    assert out[2025] == 120


def test_consolidar_calcula_indicadores():
    pop = pd.DataFrame({"codigo_ibge": [1], "ano": [2024], "populacao": [100_000]})
    indice = pd.Series({2024: 100.0})
    linha = consolidar(_cursos(), _caged(), pop, indice, 2024).iloc[0]
    assert linha["concl_presencial_por_100k"] == 20
    assert linha["vagas_por_formando"] == 0.5
    assert linha["salario_real"] == 4000.0


def test_resumo_sem_formando_nao_divide_por_zero():
    df = pd.DataFrame(
        {"codigo_ibge": [1], "ano": [2024], "saldo": [5], "concluintes_presencial": [0],
         "concluintes_presencial_municipio": [0], "admissoes_jovens_graduados": [1],
         "salario_real": [3000.0], "concl_presencial_por_100k": [0.0]}
    )
    resumo = resumo_periodo(df).iloc[0]
    assert math.isnan(resumo["vagas_por_formando"])
    assert math.isnan(resumo["recem_formados_por_formando"])


def test_ano_sem_censo_nao_entra_como_zero():
    caged = _caged(id_municipio=["1", "1"], ano=[2024, 2025], admissoes=[5, 50],
                   desligamentos=[0, 0], saldo=[5, 50], salario_nominal=[1.0, 1.0],
                   admissoes_jovens_graduados=[2, 9])
    pop = pd.DataFrame({"codigo_ibge": [1, 1], "ano": [2024, 2025], "populacao": [1000, 1000]})
    indice = pd.Series({2024: 1.0, 2025: 1.0})
    df = consolidar(_cursos(concluintes=[10]), caged, pop, indice, 2025)
    assert pd.isna(df.set_index("ano").loc[2025, "concluintes_presencial"])
    resumo = resumo_periodo(df).iloc[0]
    assert resumo["vagas_por_formando"] == 0.5
    assert resumo["recem_formados_por_formando"] == 0.2


def test_crescimento_salario_usa_os_anos_do_periodo():
    df = pd.DataFrame(
        {"codigo_ibge": [1] * 4, "ano": [2015, 2016, 2017, 2020],
         "salario_real": [100.0, 110.0, 121.0, 999.0]}
    )
    out = crescimento_salario(df, 2015, 2017).loc[1]
    assert math.isclose(out["cagr"], 0.1)
    assert math.isclose(out["tendencia"], 0.1)
