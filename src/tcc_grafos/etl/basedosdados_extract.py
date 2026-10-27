"""Extração via basedosdados (BigQuery), filtrando PR + TI na query.

Precisa de GCP_BILLING_PROJECT_ID no .env e de `gcloud auth application-default
login`. A Base dos Dados só tem o Censo Superior agregado por curso/IES (sem
nível de aluno), então a origem do estudante para o grafo vem do SISU, não daqui.
"""

from __future__ import annotations

import logging

import basedosdados as bd
import pandas as pd

from tcc_grafos.config import (
    ANO_FIM,
    ANO_INICIO,
    GCP_BILLING_PROJECT_ID,
    PREFIXOS_CBO_TI,
    PREFIXOS_CINE_TI,
    TERMOS_CURSO_TI_SISU,
    UF_ALVO,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABELA_INEP_CURSO = "basedosdados.br_inep_censo_educacao_superior.curso"
TABELA_SISU = "basedosdados.br_mec_sisu.microdados"
# CAGED antigo vai até 2019; o Novo CAGED (eSocial) começa em 2020
TABELAS_CAGED = (
    ("basedosdados.br_me_caged.microdados_antigos", 2019),
    ("basedosdados.br_me_caged.microdados_movimentacao", None),
)


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


def fluxo_sisu_ti(uf: str = UF_ALVO) -> pd.DataFrame:
    """Matriculados via SISU em cursos de TI com campus na UF: município de origem -> campus.

    Só conta status 'Efetivada' (matrícula confirmada). O dado subconta matrícula,
    porque parte dela fica como 'Pendente'.
    """
    cond_curso = " OR ".join(f"UPPER(nome_curso) LIKE '%{t}%'" for t in TERMOS_CURSO_TI_SISU)
    query = f"""
    SELECT
        ano,
        sigla_ies,
        id_municipio_candidato AS origem,
        id_municipio_campus AS destino,
        COUNT(*) AS alunos
    FROM `{TABELA_SISU}`
    WHERE sigla_uf_campus = '{uf}'
      AND status_matricula = 'Efetivada'
      AND ({cond_curso})
    GROUP BY ano, sigla_ies, origem, destino
    """
    return _read_sql(query)


def mercado_ti_caged(
    uf: str = UF_ALVO, ano_inicio: int = ANO_INICIO, ano_fim: int = ANO_FIM
) -> pd.DataFrame:
    """Admissões, desligamentos, saldo e salário médio de admissão em TI, por município e ano.

    O salário é o das admissões (o de desligamento mistura quem já estava no cargo).
    Há quebra metodológica entre 2019 (CAGED antigo) e 2020 (Novo CAGED).
    """
    cond_cbo = " OR ".join(f"cbo_2002 LIKE '{p}%'" for p in PREFIXOS_CBO_TI)
    partes = []
    for tabela, ultimo_ano in TABELAS_CAGED:
        fim = min(ano_fim, ultimo_ano) if ultimo_ano else ano_fim
        inicio = ano_inicio if ultimo_ano else max(ano_inicio, 2020)
        if inicio > fim:
            continue
        partes.append(f"""
        SELECT
            ano,
            id_municipio,
            COUNTIF(saldo_movimentacao = 1) AS admissoes,
            COUNTIF(saldo_movimentacao = -1) AS desligamentos,
            SUM(saldo_movimentacao) AS saldo,
            AVG(IF(saldo_movimentacao = 1, salario_mensal, NULL)) AS salario_nominal
        FROM `{tabela}`
        WHERE sigla_uf = '{uf}' AND ano BETWEEN {inicio} AND {fim} AND ({cond_cbo})
        GROUP BY ano, id_municipio""")
    return _read_sql("\nUNION ALL\n".join(partes))
