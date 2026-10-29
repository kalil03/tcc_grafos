import pandas as pd

from tcc_grafos.camada_raio import (
    cobertura_sisu,
    com_trienio,
    democratizacao,
    oferta_publica_ti,
    recorte_ti,
)


def _cursos(**colunas):
    base = {"codigo_ibge": [1], "ano": [2020], "co_curso": [10], "sigla_ies": ["X"],
            "rede": [1], "modalidade": [1], "vagas": [40], "ingressantes_enem": [20]}
    base.update(colunas)
    return pd.DataFrame(base)


def test_oferta_publica_ignora_privada_ead_e_sem_vaga():
    cursos = _cursos(codigo_ibge=[1, 2, 3, 4], ano=[2020] * 4, co_curso=[1, 2, 3, 4],
                     sigla_ies=["A"] * 4, rede=[1, 2, 1, 1], modalidade=[1, 1, 2, 1],
                     vagas=[40, 40, 40, 0], ingressantes_enem=[0] * 4)
    assert oferta_publica_ti(cursos)["codigo_ibge"].tolist() == [1]


def test_democratizacao_conta_origem_sem_oferta_no_ano():
    arestas = pd.DataFrame(
        {"ano": [2020, 2020, 2021], "codigo_ibge_municipio_origem": [1, 2, 1],
         "codigo_ibge_municipio_destino": [9, 9, 9], "peso_alunos": [3, 1, 4]}
    )
    oferta = pd.DataFrame({"codigo_ibge": [1], "ano": [2020]})
    out = democratizacao(arestas, oferta, ["codigo_ibge_municipio_destino"]).iloc[0]
    # origem 2 nunca tem oferta; origem 1 só tem em 2020
    assert out["alunos_sem_oferta_publica"] == 5
    assert out["pct_sem_oferta_publica"] == 5 / 8


def test_recorte_ti_valida_codigo_no_municipio_do_campus():
    sisu = pd.DataFrame(
        {
            # (10, 1) = TI no Censo; (20, 1) = curso válido de outra área; 1486 não existe;
            # (10, 2): código de TI, mas de outro município, e o nome não é de TI
            "id_curso": ["10", "20", "1486", "1487", "10"],
            "destino": ["1", "1", "1", "1", "2"],
            "nome_curso": ["QUALQUER", "LICENCIATURA EM COMPUTAÇÃO", "CIÊNCIAS DA COMPUTAÇÃO",
                           "QUÍMICA", "MATEMÁTICA"],
            "alunos": [1, 2, 3, 4, 5],
        }
    )
    out = recorte_ti(sisu, cursos_ti={(10, 1)}, cursos_censo={(10, 1), (20, 1)})
    assert out["alunos"].tolist() == [1, 3]


def test_cobertura_compara_com_ingresso_enem_do_censo():
    arestas = pd.DataFrame(
        {"ano": [2020], "codigo_ibge_municipio_destino": [1], "sigla_ies": ["X"],
         "peso_alunos": [15]}
    )
    out = cobertura_sisu(arestas, _cursos()).iloc[0]
    assert out["cobertura"] == 0.75


def test_trienio_descarta_ano_fora():
    arestas = pd.DataFrame({"ano": [2016, 2018, 2021]})
    assert com_trienio(arestas)["trienio"].tolist() == ["2017-2019", "2020-2022"]
