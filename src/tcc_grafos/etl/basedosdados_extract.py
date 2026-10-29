"""Extração via basedosdados (BigQuery), filtrando PR + TI na query.

Precisa de GCP_BILLING_PROJECT_ID no .env e de `gcloud auth application-default
login`. O Censo da Educação Superior não vem daqui: o agregado da Base dos Dados
não identifica a IES, então ele sai dos microdados do INEP (etl/inep_cursos.py).
"""

from __future__ import annotations

import logging

import basedosdados as bd
import pandas as pd

from tcc_grafos.config import (
    ANO_FIM,
    ANO_INICIO,
    GCP_BILLING_PROJECT_ID,
    IDADE_MAX_RECEM_FORMADO,
    PREFIXOS_CBO_TI,
    UF_ALVO,
    ULTIMO_ANO_CAGED_ANTIGO,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TABELA_SISU = "basedosdados.br_mec_sisu.microdados"
TABELA_RAIS = "basedosdados.br_me_rais.microdados_vinculos"
# grau_instrucao: 9 = superior completo, 10 = mestrado, 11 = doutorado, 80 = pós
# completa (Novo CAGED); o CAGED antigo usa os mesmos códigos até 11
GRAUS_SUPERIOR_COMPLETO = (9, 10, 11, 80)
TABELAS_CAGED = (
    ("basedosdados.br_me_caged.microdados_antigos", ULTIMO_ANO_CAGED_ANTIGO),
    ("basedosdados.br_me_caged.microdados_movimentacao", None),
)


def _read_sql(query: str) -> pd.DataFrame:
    if not GCP_BILLING_PROJECT_ID:
        raise RuntimeError(
            "defina GCP_BILLING_PROJECT_ID no .env e rode "
            "`gcloud auth application-default login`"
        )
    return bd.read_sql(query, billing_project_id=GCP_BILLING_PROJECT_ID)


def fluxo_sisu(uf: str = UF_ALVO) -> pd.DataFrame:
    """Aprovados e matriculados via SISU com campus na UF, por curso: origem -> campus.

    Traz todos os cursos; o recorte de TI é feito depois pelo `id_curso` (código do
    curso no INEP). `status_matricula` é o que a IES registrou no Sisu Gestão:
    'Efetivada' é matrícula confirmada; 'Pendente' só aparece entre não aprovados
    (lista de espera), e parte dos aprovados fica sem status nenhum. Conta inscrições
    distintas: o mesmo candidato pode aparecer em mais de uma chamada.
    """
    query = f"""
    SELECT
        ano,
        sigla_ies,
        id_curso,
        UPPER(nome_curso) AS nome_curso,
        status_aprovado,
        status_matricula = 'Efetivada' AS efetivada,
        id_municipio_candidato AS origem,
        id_municipio_campus AS destino,
        COUNT(DISTINCT inscricao_enem) AS alunos
    FROM `{TABELA_SISU}`
    WHERE sigla_uf_campus = '{uf}'
      AND (status_aprovado OR status_matricula = 'Efetivada')
    GROUP BY ano, sigla_ies, id_curso, nome_curso, status_aprovado, efetivada, origem, destino
    """
    return _read_sql(query)


def mercado_ti_caged(
    uf: str = UF_ALVO, ano_inicio: int = ANO_INICIO, ano_fim: int = ANO_FIM
) -> pd.DataFrame:
    """Admissões, desligamentos, saldo e salário médio de admissão em TI, por município e ano.

    O salário é o das admissões (o de desligamento mistura quem já estava no cargo).
    `admissoes_jovens_graduados` conta admissões com superior completo e idade até
    IDADE_MAX_RECEM_FORMADO (proxy da H2; o CAGED não diz a área do diploma).
    Há quebra metodológica entre 2019 (CAGED antigo) e 2020 (Novo CAGED).
    """
    cond_cbo = " OR ".join(f"cbo_2002 LIKE '{p}%'" for p in PREFIXOS_CBO_TI)
    graus = ", ".join(str(g) for g in GRAUS_SUPERIOR_COMPLETO)
    jovem_graduado = (
        f"SAFE_CAST(idade AS INT64) <= {IDADE_MAX_RECEM_FORMADO}"
        f" AND SAFE_CAST(grau_instrucao AS INT64) IN ({graus})"
    )
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
            AVG(IF(saldo_movimentacao = 1, salario_mensal, NULL)) AS salario_nominal,
            COUNTIF(saldo_movimentacao = 1 AND {jovem_graduado}) AS admissoes_jovens_graduados
        FROM `{tabela}`
        WHERE sigla_uf = '{uf}' AND ano BETWEEN {inicio} AND {fim} AND ({cond_cbo})
        GROUP BY ano, id_municipio""")
    return _read_sql("\nUNION ALL\n".join(partes))


def estoque_empregos_ti_rais(
    uf: str = UF_ALVO, ano_inicio: int = ANO_INICIO, ano_fim: int = ANO_FIM
) -> pd.DataFrame:
    """Vínculos formais de TI ativos em 31/12, por município e ano (RAIS).

    É o estoque que o escore de polos pede; o CAGED só dá o fluxo.
    """
    cond_cbo = " OR ".join(f"cbo_2002 LIKE '{p}%'" for p in PREFIXOS_CBO_TI)
    query = f"""
    SELECT ano, id_municipio, COUNT(*) AS vinculos_ti
    FROM `{TABELA_RAIS}`
    WHERE sigla_uf = '{uf}' AND ano BETWEEN {ano_inicio} AND {ano_fim}
      AND SAFE_CAST(vinculo_ativo_3112 AS INT64) = 1
      AND ({cond_cbo})
    GROUP BY ano, id_municipio
    """
    return _read_sql(query)
