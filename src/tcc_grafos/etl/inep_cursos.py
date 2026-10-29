"""Cursos de TI do Censo da Educação Superior a partir dos microdados do INEP.

Diferente do agregado da Base dos Dados, o cadastro de cursos traz a IES, o código
do curso e a rede (pública/privada), que isolam a UTFPR-CM e alimentam a H5. Os
CSVs anuais ficam em data/raw/inep/<ano>/ (download em
https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior).
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from tcc_grafos.config import DATA_INTERIM_DIR, DATA_RAW_DIR

logger = logging.getLogger(__name__)

DIR_INEP = DATA_RAW_DIR / "inep"
ARQUIVO_CURSOS = DATA_INTERIM_DIR / "cursos_ti_inep.parquet"
ARQUIVO_CODIGOS = DATA_INTERIM_DIR / "cursos_censo_municipio.parquet"

# área específica Cine 061 (Computação e TIC); o rótulo e a área detalhada mudam de
# versão entre os anos, a área específica não
AREA_CINE_TI = 61
REDE_PUBLICA = 1

COLUNAS = {
    "NU_ANO_CENSO": "ano",
    "CO_MUNICIPIO": "codigo_ibge",
    "SG_UF": "sigla_uf",
    "CO_IES": "co_ies",
    "CO_CURSO": "co_curso",
    "NO_CURSO": "nome_curso",
    "TP_REDE": "rede",
    "TP_MODALIDADE_ENSINO": "modalidade",
    "QT_VG_TOTAL": "vagas",
    "QT_ING": "ingressantes",
    "QT_ING_ENEM": "ingressantes_enem",
    "QT_MAT": "matriculas",
    "QT_CONC": "concluintes",
}


def _ler_cursos(arquivo: Path) -> pd.DataFrame:
    partes = []
    leitor = pd.read_csv(
        arquivo, sep=";", encoding="latin1", chunksize=200_000, low_memory=False,
        usecols=[*COLUNAS, "CO_CINE_AREA_ESPECIFICA"],
    )
    for parte in leitor:
        partes.append(parte[parte["CO_CINE_AREA_ESPECIFICA"] == AREA_CINE_TI])
    return pd.concat(partes).drop(columns="CO_CINE_AREA_ESPECIFICA").rename(columns=COLUNAS)


def _ler_siglas(arquivo: Path) -> pd.DataFrame:
    ies = pd.read_csv(arquivo, sep=";", encoding="latin1", usecols=["CO_IES", "SG_IES"])
    return ies.rename(columns={"CO_IES": "co_ies", "SG_IES": "sigla_ies"})


def extrair_cursos_ti(dir_inep: Path = DIR_INEP) -> pd.DataFrame:
    """Uma linha por curso de TI e ano, no Brasil inteiro (a origem do SISU é nacional)."""
    anos = []
    for pasta in sorted(p for p in dir_inep.iterdir() if p.is_dir()):
        cursos = _ler_cursos(next(pasta.glob("MICRODADOS_CADASTRO_CURSOS_*.CSV")))
        # o arquivo de IES mudou de nome em 2022 (CADASTRO_IES -> ED_SUP_IES)
        siglas = _ler_siglas(next(pasta.glob("MICRODADOS_*IES_*.CSV")))
        anos.append(cursos.merge(siglas, on="co_ies", how="left"))
        logger.info("INEP %s: %d cursos de TI", pasta.name, len(cursos))
    if not anos:
        raise FileNotFoundError(f"nenhum microdado do INEP em {dir_inep}")

    df = pd.concat(anos, ignore_index=True)
    contagens = ["vagas", "ingressantes", "ingressantes_enem", "matriculas", "concluintes"]
    df[contagens] = df[contagens].fillna(0).astype("int64")
    return df.astype({"codigo_ibge": "Int64"})


def carregar_cursos_censo(atualizar: bool = False) -> set[tuple[int, int]]:
    """(código do curso, município) de todos os cursos do Censo, de qualquer área.

    Serve para reconhecer código de curso inválido no SISU.
    """
    if ARQUIVO_CODIGOS.exists() and not atualizar:
        pares = pd.read_parquet(ARQUIVO_CODIGOS)
        return set(zip(pares["co_curso"], pares["codigo_ibge"]))
    partes = []
    for arquivo in sorted(DIR_INEP.glob("*/MICRODADOS_CADASTRO_CURSOS_*.CSV")):
        lidos = pd.read_csv(arquivo, sep=";", encoding="latin1", usecols=["CO_CURSO", "CO_MUNICIPIO"])
        partes.append(lidos.dropna().astype("int64"))
    pares = pd.concat(partes).drop_duplicates().rename(
        columns={"CO_CURSO": "co_curso", "CO_MUNICIPIO": "codigo_ibge"}
    )
    pares.to_parquet(ARQUIVO_CODIGOS, index=False)
    return set(zip(pares["co_curso"], pares["codigo_ibge"]))


def carregar_cursos_ti(atualizar: bool = False) -> pd.DataFrame:
    if ARQUIVO_CURSOS.exists() and not atualizar:
        return pd.read_parquet(ARQUIVO_CURSOS)
    df = extrair_cursos_ti()
    df.to_parquet(ARQUIVO_CURSOS, index=False)
    return df
