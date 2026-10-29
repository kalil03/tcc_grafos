"""Programas de pós-graduação stricto sensu da CAPES (dados abertos, sem login)."""

from __future__ import annotations

import pandas as pd
import requests
from unidecode import unidecode

from tcc_grafos.config import DATA_RAW_DIR

URL_PROGRAMAS = (
    "https://dadosabertos.capes.gov.br/dataset/414275c0-2056-4a12-b1a6-b525b74850d5/resource/"
    "76ccbd76-7f3a-40c3-a4dc-7d6f65858db8/download/br-capes-colsucup-prog-2024-2025-12-01.csv"
)
ARQUIVO_PROGRAMAS = DATA_RAW_DIR / "capes" / "programas_2024.csv"
AREA_COMPUTACAO = "COMPUTAÇÃO"


def carregar_programas() -> pd.DataFrame:
    if not ARQUIVO_PROGRAMAS.exists():
        ARQUIVO_PROGRAMAS.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(URL_PROGRAMAS, timeout=300)
        resp.raise_for_status()
        ARQUIVO_PROGRAMAS.write_bytes(resp.content)
    return pd.read_csv(ARQUIVO_PROGRAMAS, sep=";", encoding="latin1")


def _chave(nome: str) -> str:
    return unidecode(str(nome)).upper().strip()


def municipios_com_pos_computacao(
    programas: pd.DataFrame, municipios: pd.DataFrame, uf: str, codigo_uf: int
) -> set[int]:
    """Códigos IBGE dos municípios da UF com programa da área de avaliação Computação.

    O arquivo de 2024 só lista programas em funcionamento naquele ano.
    """
    comp = programas[
        (programas["SG_UF_PROGRAMA"] == uf) & (programas["NM_AREA_AVALIACAO"] == AREA_COMPUTACAO)
    ]
    da_uf = municipios[municipios["codigo_uf"] == codigo_uf]
    por_nome = dict(zip(da_uf["nome"].map(_chave), da_uf["codigo_ibge"].astype(int)))
    nomes = set(comp["NM_MUNICIPIO_PROGRAMA_IES"].map(_chave))
    faltando = nomes - por_nome.keys()
    if faltando:
        raise ValueError(f"município da CAPES sem código IBGE: {sorted(faltando)}")
    return {por_nome[n] for n in nomes}
