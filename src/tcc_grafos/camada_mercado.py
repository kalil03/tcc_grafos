"""Camada 2 (H2, H3, H4, H6, QP3): mercado, densidade e absorção por município e ano.

Rodar com: python -m tcc_grafos.camada_mercado [--atualizar]
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd

from tcc_grafos.config import (
    ANO_FIM,
    ANO_INICIO,
    CODIGO_IBGE_CAMPO_MOURAO,
    CURSOS_UTFPR_CM,
    DATA_INTERIM_DIR,
    DATA_PROCESSED_DIR,
    MUNICIPIOS_POLOS_PROVISORIOS,
    UF_ALVO,
    ULTIMO_ANO_CAGED_ANTIGO,
)
from tcc_grafos.etl.basedosdados_extract import mercado_ti_caged
from tcc_grafos.etl.inep_cursos import carregar_cursos_ti
from tcc_grafos.etl.ipca import baixar_serie_ipca
from tcc_grafos.etl.municipios import carregar_municipios
from tcc_grafos.etl.populacao import carregar_populacao
from tcc_grafos.graph.metrics import cagr, crescimento_anual_tendencia

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODALIDADE_PRESENCIAL = 1

# a taxa de crescimento do salário não atravessa a quebra CAGED antigo -> Novo CAGED
PERIODOS_CAGED = {
    "caged_antigo": (ANO_INICIO, ULTIMO_ANO_CAGED_ANTIGO),
    "novo_caged": (ULTIMO_ANO_CAGED_ANTIGO + 1, ANO_FIM),
}


def indice_ipca_anual(ipca: pd.DataFrame) -> pd.Series:
    return ipca.groupby(ipca["competencia"].dt.year)["numero_indice"].mean()


def deflacionar(valores: pd.Series, anos: pd.Series, indice: pd.Series, ano_base: int) -> pd.Series:
    """Converte valores nominais anuais para preços do ano-base."""
    return valores * indice[ano_base] / anos.map(indice)


def agregar_concluintes(cursos: pd.DataFrame) -> pd.DataFrame:
    """Concluintes por município e ano.

    No vértice de Campo Mourão só entra o curso da UTFPR-CM; nos polos, todas as IES.
    `concluintes_presencial_municipio` soma todas as IES também em Campo Mourão.
    """
    df = cursos.copy()
    presencial = df["modalidade"] == MODALIDADE_PRESENCIAL
    objeto = (df["codigo_ibge"] != CODIGO_IBGE_CAMPO_MOURAO) | df["co_curso"].isin(CURSOS_UTFPR_CM)
    df["concluintes_total"] = df["concluintes"].where(objeto, 0)
    df["concluintes_presencial"] = df["concluintes"].where(objeto & presencial, 0)
    df["concluintes_presencial_municipio"] = df["concluintes"].where(presencial, 0)
    colunas = ["concluintes_total", "concluintes_presencial", "concluintes_presencial_municipio"]
    return df.groupby(["codigo_ibge", "ano"], as_index=False)[colunas].sum()


def consolidar(
    cursos: pd.DataFrame,
    caged: pd.DataFrame,
    populacao: pd.DataFrame,
    indice_ipca: pd.Series,
    ano_base: int,
) -> pd.DataFrame:
    """Uma linha por município e ano com os indicadores das hipóteses H2, H3, H4 e H6."""
    conc = agregar_concluintes(cursos)
    caged = caged.assign(codigo_ibge=caged["id_municipio"].astype("int64")).drop(
        columns="id_municipio"
    )
    conc["codigo_ibge"] = conc["codigo_ibge"].astype("int64")
    df = conc.merge(caged, on=["codigo_ibge", "ano"], how="outer")
    df = df.merge(populacao, on=["codigo_ibge", "ano"], how="left")

    formandos = ["concluintes_total", "concluintes_presencial", "concluintes_presencial_municipio"]
    contagens = [*formandos, "admissoes", "desligamentos", "saldo", "admissoes_jovens_graduados"]
    df[contagens] = df[contagens].fillna(0).astype("Int64")
    # ano que o Censo ainda não publicou fica sem dado, não zero
    sem_censo = ~df["ano"].isin(cursos["ano"].unique())
    df.loc[sem_censo, formandos] = pd.NA

    df["salario_real"] = deflacionar(df["salario_nominal"], df["ano"], indice_ipca, ano_base)
    df["concl_presencial_por_100k"] = df["concluintes_presencial"] / df["populacao"] * 1e5
    df["saldo_ti_por_100k"] = df["saldo"] / df["populacao"] * 1e5
    # vagas de TI criadas por formando presencial no mesmo município (H6)
    df["vagas_por_formando"] = df["saldo"] / df["concluintes_presencial"].where(
        df["concluintes_presencial"] > 0
    )
    colunas = ["codigo_ibge", "ano", "populacao", *contagens, "salario_nominal", "salario_real",
               "concl_presencial_por_100k", "saldo_ti_por_100k", "vagas_por_formando"]
    return df[colunas].sort_values(["codigo_ibge", "ano"]).reset_index(drop=True)


def crescimento_salario(df: pd.DataFrame, inicio: int, fim: int) -> pd.DataFrame:
    """CAGR (pontas) e taxa da tendência log-linear do salário real no período, por município.

    Com poucas admissões por ano o salário médio oscila muito, e o CAGR depende só
    dos dois anos das pontas; a tendência usa todos os anos.
    """
    periodo = df[df["ano"].between(inicio, fim)]
    linhas = {}
    for codigo, grupo in periodo.groupby("codigo_ibge"):
        salarios = grupo.set_index("ano")["salario_real"]
        linhas[codigo] = {
            "cagr": cagr(salarios.get(inicio, float("nan")), salarios.get(fim, float("nan")),
                         fim - inicio),
            "tendencia": crescimento_anual_tendencia(grupo["ano"], grupo["salario_real"]),
        }
    return pd.DataFrame.from_dict(linhas, orient="index", columns=["cagr", "tendencia"])


def resumo_periodo(df: pd.DataFrame) -> pd.DataFrame:
    """Indicadores do período inteiro por município (razões das somas, não média de razões).

    As razões por formando só usam os anos em que existem formandos e CAGED.
    """
    out = df.groupby("codigo_ibge").agg(
        saldo=("saldo", "sum"),
        salario_real_medio=("salario_real", "mean"),
        concl_presencial_por_100k=("concl_presencial_por_100k", "mean"),
    )
    for nome, (inicio, fim) in PERIODOS_CAGED.items():
        crescimento = crescimento_salario(df, inicio, fim)
        out[f"cagr_salario_{nome}"] = crescimento["cagr"]
        out[f"tendencia_salario_{nome}"] = crescimento["tendencia"]

    com_censo = df[df["concluintes_presencial"].notna()].groupby("codigo_ibge")
    formandos = com_censo["concluintes_presencial"].sum().astype(float)
    formandos_municipio = com_censo["concluintes_presencial_municipio"].sum().astype(float)
    saldo = com_censo["saldo"].sum()
    out["concluintes_presencial"] = formandos
    out["vagas_por_formando"] = saldo / formandos.where(formandos > 0)
    out["vagas_por_formando_municipio"] = saldo / formandos_municipio.where(formandos_municipio > 0)
    # H2: admissões de jovens com superior completo por formando presencial
    jovens = com_censo["admissoes_jovens_graduados"].sum(min_count=1).astype(float)
    out["recem_formados_por_formando"] = jovens / formandos.where(formandos > 0)
    return out.reset_index()


def _cache(nome: str, buscar, atualizar: bool) -> pd.DataFrame:
    arquivo = DATA_INTERIM_DIR / f"{nome}.parquet"
    if arquivo.exists() and not atualizar:
        return pd.read_parquet(arquivo)
    df = buscar()
    df.to_parquet(arquivo, index=False)
    return df


def main(atualizar: bool = False) -> None:
    cursos = carregar_cursos_ti(atualizar)
    cursos = cursos[(cursos["sigla_uf"] == UF_ALVO) & cursos["ano"].between(ANO_INICIO, ANO_FIM)]
    caged = _cache("caged_ti", mercado_ti_caged, atualizar)
    sem_h2 = "admissoes_jovens_graduados" not in caged
    if sem_h2:
        logger.warning("cache do CAGED sem admissoes_jovens_graduados (H2): rode com --atualizar")
        caged = caged.assign(admissoes_jovens_graduados=0)
    populacao = carregar_populacao(atualizar=atualizar)
    indice = indice_ipca_anual(baixar_serie_ipca())

    df = consolidar(cursos, caged, populacao, indice, ano_base=ANO_FIM)
    if sem_h2:
        df["admissoes_jovens_graduados"] = pd.NA
    df.to_csv(DATA_PROCESSED_DIR / "mercado_por_municipio_ano.csv", index=False)

    resumo = resumo_periodo(df)
    resumo.to_csv(DATA_PROCESSED_DIR / "mercado_resumo_periodo.csv", index=False)

    municipios = carregar_municipios()
    nomes = dict(zip(municipios["codigo_ibge"], municipios["nome"]))
    alvo = [CODIGO_IBGE_CAMPO_MOURAO, *MUNICIPIOS_POLOS_PROVISORIOS]
    tabela = resumo[resumo["codigo_ibge"].isin(alvo)].copy()
    tabela.insert(1, "municipio", tabela["codigo_ibge"].map(nomes))
    logger.info("salário real a preços de %d", ANO_FIM)
    print(tabela.drop(columns="codigo_ibge").round(3).to_string(index=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--atualizar", action="store_true", help="refaz as consultas")
    main(parser.parse_args().atualizar)
