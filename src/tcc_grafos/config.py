"""Parâmetros centrais do recorte de pesquisa."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_INTERIM_DIR = ROOT_DIR / "data" / "interim"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"

for _dir in (DATA_RAW_DIR, DATA_INTERIM_DIR, DATA_PROCESSED_DIR):
    _dir.mkdir(parents=True, exist_ok=True)

# só 2015 por enquanto, até o prof passar o resto dos dados
ANO_INICIO = int(os.getenv("ANO_INICIO", "2015"))
ANO_FIM = int(os.getenv("ANO_FIM", "2015"))
UF_ALVO = os.getenv("UF_ALVO", "PR")

CODIGO_IBGE_CAMPO_MOURAO = 4104808

# TODO: conferir códigos Cine no manual do INEP
CODIGOS_CINE_TI = {
    "0611": "Ciência da computação",
    "0612": "Desenvolvimento e análise de software e aplicativos",
    "0613": "Uso de computadores",
}

# TODO: conferir códigos CBO no manual oficial
PREFIXOS_CBO_TI = (
    "2124",
    "2123",
    "3171",
    "3172",
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://tcc_user:troque_esta_senha@localhost:5432/tcc_grafos",
)
