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

# Curitiba, Londrina, Maringá, Cascavel, Ponta Grossa; provisório até rodar o
# escore de polos (polos/scoring.py)
MUNICIPIOS_POLOS_PROVISORIOS = (4106902, 4113700, 4115200, 4104808, 4119905)

# no vértice de Campo Mourão entra só o BCC da UTFPR-CM (código do curso no Censo);
# o CSTI (109550) não tem ingressante desde 2015 e formou os últimos em 2017
CURSOS_UTFPR_CM = (1164656,)

# famílias CBO 2002 de profissionais de TI
PREFIXOS_CBO_TI = ("2122", "2123", "2124", "3171", "3172")

# curso de TI pelo nome (regex), só para id_curso do SISU que não existe no Censo
# (ex.: o BCC de Campo Mourão aparece como 1486 em 2018)
TERMOS_CURSO_TI_SISU = (
    "COMPUTA",
    "SISTEMAS DE INFORMA",
    "SISTEMAS PARA INTERNET",
    "SOFTWARE",
    "INFORM.TICA",
    "REDES DE COMPUTAD",
    "AN.LISE E DESENV",
    "CI.NCIA DE DADOS",
    "TECNOLOGIA DA INFORMA",
)

# CAGED antigo até aqui; a partir do ano seguinte, Novo CAGED (eSocial), com quebra
# metodológica entre as duas séries
ULTIMO_ANO_CAGED_ANTIGO = 2019

# proxy da H2: admissão em TI com superior completo até esta idade conta como
# recém-formado (o CAGED não identifica o egresso)
IDADE_MAX_RECEM_FORMADO = 29

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://tcc_user:troque_esta_senha@localhost:5432/tcc_grafos",
)
