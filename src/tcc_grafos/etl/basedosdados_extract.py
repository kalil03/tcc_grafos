"""Extração via basedosdados (BigQuery), filtrando PR + TI na query.

Precisa de GCP_BILLING_PROJECT_ID no .env e de `gcloud auth application-default
login`. A Base dos Dados só tem o Censo Superior agregado por curso/IES (sem
nível de aluno), então a origem do estudante para o grafo vem do SISU, não daqui.
"""

from __future__ import annotations

import logging

import basedosdados as bd
import pandas as pd

from tcc_grafos.config import GCP_BILLING_PROJECT_ID, PREFIXOS_CINE_TI, UF_ALVO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABELA_INEP_CURSO = "basedosdados.br_inep_censo_educacao_superior.curso"


def _read_sql(query: str) -> pd.DataFrame:
    if not GCP_BILLING_PROJECT_ID:
        raise RuntimeError(
            "defina GCP_BILLING_PROJECT_ID no .env e rode "
            "`gcloud auth application-default login`"
        )
    return bd.read_sql(query, billing_project_id=GCP_BILLING_PROJECT_ID)


def concluintes_ti_por_municipio(ano_inicio: int, uf: str = UF_ALVO) -> pd.DataFrame:
    """Concluintes de TI por município do curso, ano e modalidade (1=presencial, 2=EAD)."""
    cond_cine = " OR ".join(
        f"STARTS_WITH(REPLACE(id_curso_cine, '\"', ''), '{p}')" for p in PREFIXOS_CINE_TI
    )
    query = f"""
    SELECT
        ano,
        id_municipio,
        id_curso_cine,
        tipo_modalidade_ensino,
        SUM(quantidade_concluintes) AS quantidade_concluintes,
        SUM(quantidade_ingressantes) AS quantidade_ingressantes
    FROM `{TABELA_INEP_CURSO}`
    WHERE sigla_uf = '{uf}'
      AND ano >= {ano_inicio}
      AND ({cond_cine})
    GROUP BY ano, id_municipio, id_curso_cine, tipo_modalidade_ensino
    """
    return _read_sql(query)
