"""População municipal por ano (IBGE): estimativas + Censo 2022, ano faltante interpolado."""

from __future__ import annotations

import pandas as pd
import requests

from tcc_grafos.config import ANO_FIM, ANO_INICIO, DATA_RAW_DIR

API = "https://servicodados.ibge.gov.br/api/v3/agregados"
ARQUIVO_POPULACAO = DATA_RAW_DIR / "ibge" / "populacao_municipios.csv"

# (agregado, variável): estimativas anuais e o Censo 2022, ano em que não há estimativa
FONTES = (("6579", "9324"), ("4714", "93"))


def _baixar(agregado: str, variavel: str, anos: range, uf: int) -> pd.DataFrame:
    disponiveis = requests.get(f"{API}/{agregado}/periodos", timeout=60).json()
    periodos = "|".join(p["id"] for p in disponiveis if int(p["id"]) in anos)
    if not periodos:
        return pd.DataFrame(columns=["codigo_ibge", "ano", "populacao"])
    url = f"{API}/{agregado}/periodos/{periodos}/variaveis/{variavel}"
    resp = requests.get(url, params={"localidades": f"N6[N3[{uf}]]"}, timeout=120)
    resp.raise_for_status()
    linhas = [
        (int(s["localidade"]["id"]), int(ano), int(valor))
        for s in resp.json()[0]["resultados"][0]["series"]
        for ano, valor in s["serie"].items()
        if valor not in (None, "", "-", "...")
    ]
    return pd.DataFrame(linhas, columns=["codigo_ibge", "ano", "populacao"])


def completar_anos(pop: pd.DataFrame, anos: range) -> pd.DataFrame:
    """Interpola linearmente os anos sem dado e repete o último valor nas pontas."""
    completo = []
    for codigo, grupo in pop.groupby("codigo_ibge"):
        serie = (
            grupo.drop_duplicates("ano").set_index("ano")["populacao"]
            .reindex(list(anos)).astype(float)
            .interpolate().ffill().bfill()
        )
        completo.append(
            pd.DataFrame({"codigo_ibge": codigo, "ano": serie.index, "populacao": serie.round()})
        )
    return pd.concat(completo, ignore_index=True).astype({"populacao": "int64"})


def carregar_populacao(uf: int = 41, atualizar: bool = False) -> pd.DataFrame:
    if ARQUIVO_POPULACAO.exists() and not atualizar:
        return pd.read_csv(ARQUIVO_POPULACAO)
    anos = range(ANO_INICIO, ANO_FIM + 1)
    pop = pd.concat([_baixar(a, v, anos, uf) for a, v in FONTES], ignore_index=True)
    pop = completar_anos(pop, anos)
    ARQUIVO_POPULACAO.parent.mkdir(parents=True, exist_ok=True)
    pop.to_csv(ARQUIVO_POPULACAO, index=False)
    return pop
