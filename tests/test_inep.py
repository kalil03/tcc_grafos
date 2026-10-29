from tcc_grafos.etl.inep_cursos import COLUNAS, extrair_cursos_ti


def _csv(caminho, cabecalho, linhas):
    texto = "\n".join([";".join(cabecalho), *(";".join(map(str, l)) for l in linhas)])
    caminho.write_bytes(texto.encode("latin1"))


def test_extrair_filtra_area_ti_e_junta_sigla(tmp_path):
    pasta = tmp_path / "2020"
    pasta.mkdir()
    cabecalho = [*COLUNAS, "CO_CINE_AREA_ESPECIFICA"]
    linha_ti = [2020, 4104303, "PR", 588, 1164656, "CIÊNCIA DA COMPUTAÇÃO", 1, 1, 50, 45, 40,
                200, 20, 61]
    linha_outra = [2020, 4104303, "PR", 588, 1, "QUÍMICA", 1, 1, 50, 45, 40, 200, 20, 53]
    _csv(pasta / "MICRODADOS_CADASTRO_CURSOS_2020.CSV", cabecalho, [linha_ti, linha_outra])
    _csv(pasta / "MICRODADOS_CADASTRO_IES_2020.CSV", ["CO_IES", "SG_IES"], [[588, "UTFPR"]])

    df = extrair_cursos_ti(tmp_path)
    assert df["co_curso"].tolist() == [1164656]
    assert df["sigla_ies"].iloc[0] == "UTFPR"
    assert df["concluintes"].iloc[0] == 20
