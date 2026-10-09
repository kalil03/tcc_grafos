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

ANO_INICIO = int(os.getenv("ANO_INICIO", "2015"))
ANO_FIM = int(os.getenv("ANO_FIM", "2025"))
UF_ALVO = os.getenv("UF_ALVO", "PR")

# projeto GCP do basedosdados (BigQuery Sandbox, sem faturamento)
GCP_BILLING_PROJECT_ID = os.getenv("GCP_BILLING_PROJECT_ID", "")

CODIGO_IBGE_CAMPO_MOURAO = 4104303

# prefixos Cine-Brasil da área 061 (Computação e TIC); o id_curso_cine muda de
# versão por ano, então o filtro é por prefixo
PREFIXOS_CINE_TI = ("0611", "0612", "0613", "0614", "0615", "0619")

# famílias CBO 2002 de profissionais de TI
PREFIXOS_CBO_TI = ("2122", "2123", "2124", "3171", "3172")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://tcc_user:troque_esta_senha@localhost:5432/tcc_grafos",
)
