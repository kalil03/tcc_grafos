"""Nome, UF e coordenadas da sede de cada município (código IBGE de 7 dígitos)."""

from __future__ import annotations

import pandas as pd
import requests

from tcc_grafos.config import DATA_RAW_DIR

URL_MUNICIPIOS = (
    "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
)
ARQUIVO_MUNICIPIOS = DATA_RAW_DIR / "ibge" / "municipios_coordenadas.csv"

SIGLA_UF = {
    11: "RO", 12: "AC", 13: "AM", 14: "RR", 15: "PA", 16: "AP", 17: "TO",
    21: "MA", 22: "PI", 23: "CE", 24: "RN", 25: "PB", 26: "PE", 27: "AL", 28: "SE", 29: "BA",
    31: "MG", 32: "ES", 33: "RJ", 35: "SP", 41: "PR", 42: "SC", 43: "RS",
    50: "MS", 51: "MT", 52: "GO", 53: "DF",
}


def carregar_municipios() -> pd.DataFrame:
    if not ARQUIVO_MUNICIPIOS.exists():
        ARQUIVO_MUNICIPIOS.parent.mkdir(parents=True, exist_ok=True)
        resp = requests.get(URL_MUNICIPIOS, timeout=60)
        resp.raise_for_status()
        ARQUIVO_MUNICIPIOS.write_bytes(resp.content)
    return pd.read_csv(ARQUIVO_MUNICIPIOS)


def coordenadas(municipios: pd.DataFrame) -> dict[int, tuple[float, float]]:
    return {
        int(r.codigo_ibge): (r.latitude, r.longitude) for r in municipios.itertuples()
    }


def tabela_municipios(municipios: pd.DataFrame) -> pd.DataFrame:
    """Formato da tabela `municipios` do banco."""
    return pd.DataFrame(
        {
            "codigo_ibge": municipios["codigo_ibge"].astype("int64"),
            "nome": municipios["nome"],
            "uf": municipios["codigo_uf"].map(SIGLA_UF),
            "latitude": municipios["latitude"],
            "longitude": municipios["longitude"],
        }
    )
