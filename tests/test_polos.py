import pandas as pd
import pytest

from tcc_grafos.camada_polos import indicadores_ensino
from tcc_grafos.config import CODIGO_IBGE_CAMPO_MOURAO
from tcc_grafos.etl.capes import municipios_com_pos_computacao
from tcc_grafos.polos.scoring import calcular_escore, classificar_polos


def test_campo_mourao_fica_fora_do_ranking():
    indicadores = pd.DataFrame(
        {"codigo_ibge_municipio": [CODIGO_IBGE_CAMPO_MOURAO, 2, 3], "a": [100, 50, 10]}
    )
    polos = classificar_polos(calcular_escore(indicadores, ["a"]), top_n=1).set_index(
        "codigo_ibge_municipio"
    )
    assert not polos.loc[CODIGO_IBGE_CAMPO_MOURAO, "is_grande_polo"]
    assert polos.loc[2, "is_grande_polo"]
    assert polos.loc[2, "rank"] == 1


def test_indicadores_ensino_media_anual_de_ies():
    cursos = pd.DataFrame(
        {"codigo_ibge": [1, 1, 1], "ano": [2020, 2020, 2021], "co_ies": [7, 8, 7],
         "modalidade": [1, 1, 1], "matriculas": [10, 10, 10], "concluintes": [1, 2, 3]}
    )
    out = indicadores_ensino(cursos).loc[1]
    assert out["total_concluintes"] == 6
    assert out["num_ies_ti"] == 1.5


def _municipios():
    return pd.DataFrame(
        {"codigo_ibge": [4104303, 3550308], "nome": ["Campo Mourão", "São Paulo"],
         "codigo_uf": [41, 35]}
    )


def test_capes_casa_nome_sem_acento():
    programas = pd.DataFrame(
        {"SG_UF_PROGRAMA": ["PR", "PR"], "NM_AREA_AVALIACAO": ["COMPUTAÇÃO", "BIODIVERSIDADE"],
         "NM_MUNICIPIO_PROGRAMA_IES": ["CAMPO MOURAO", "CAMPO MOURÃO"]}
    )
    assert municipios_com_pos_computacao(programas, _municipios(), "PR", 41) == {4104303}


def test_capes_municipio_desconhecido_falha():
    programas = pd.DataFrame(
        {"SG_UF_PROGRAMA": ["PR"], "NM_AREA_AVALIACAO": ["COMPUTAÇÃO"],
         "NM_MUNICIPIO_PROGRAMA_IES": ["CIDADE INEXISTENTE"]}
    )
    with pytest.raises(ValueError):
        municipios_com_pos_computacao(programas, _municipios(), "PR", 41)
