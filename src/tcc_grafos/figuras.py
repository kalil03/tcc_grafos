"""Figuras da monografia a partir das saídas do pipeline (data/processed).

Rodar com: python -m tcc_grafos.figuras (depois de `make pipeline`)

Gera PDF (vetorial, para o texto) e PNG (para conferir) em docs/figuras/. Campo
Mourão em azul; as demais IES e municípios em cinza, como contexto.
"""

from __future__ import annotations

import logging
import math
from itertools import pairwise

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Patch

from tcc_grafos.config import (
    CODIGO_IBGE_CAMPO_MOURAO,
    DATA_PROCESSED_DIR,
    MUNICIPIOS_POLOS_PROVISORIOS,
    ROOT_DIR,
    ULTIMO_ANO_CAGED_ANTIGO,
)
from tcc_grafos.etl.municipios import carregar_municipios

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DIR_FIGURAS = ROOT_DIR / "docs" / "figuras"
LARGURA = 6.3  # polegadas: largura útil de uma página A4 com margens ABNT

# paleta de referência validada (skill dataviz): destaque, contraste e rampa ordinal
DESTAQUE = "#2a78d6"
SEGUNDA_SERIE = "#eb6834"
CONTEXTO = "#c3c2b7"
RAMPA_FAIXAS = ("#86b6ef", "#2a78d6", "#104281")
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_FRACA = "#898781"
GRADE = "#e1e0d9"

# IES públicas dos grandes polos que aparecem no SISU
IES_POLOS = (
    ("Ponta Grossa", "UTFPR"),
    ("Curitiba", "UTFPR"),
    ("Curitiba", "UFPR"),
    ("Cascavel", "UNIOESTE"),
    ("Londrina", "UEL"),
    ("Maringá", "UEM"),
)
MIN_ALUNOS = 40


def _estilo() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.edgecolor": CONTEXTO,
            "axes.labelcolor": TINTA_SECUNDARIA,
            "axes.titlesize": 10,
            "axes.titlecolor": TINTA,
            "axes.titlelocation": "left",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.color": GRADE,
            "grid.linewidth": 0.6,
            "xtick.color": TINTA_FRACA,
            "ytick.color": TINTA_FRACA,
            "xtick.labelcolor": TINTA_SECUNDARIA,
            "ytick.labelcolor": TINTA_SECUNDARIA,
            "legend.frameon": False,
            "savefig.bbox": "tight",
            "savefig.dpi": 200,
        }
    )


def _br(valor: float, casas: int = 0) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


MILHAR = matplotlib.ticker.FuncFormatter(lambda v, _: _br(v))


def _salvar(fig: plt.Figure, nome: str) -> None:
    DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
    for extensao in ("pdf", "png"):
        fig.savefig(DIR_FIGURAS / f"{nome}.{extensao}")
    plt.close(fig)
    logger.info("figura: %s", nome)


def _rotulo_ies(municipio: str, sigla: str, alunos: int | None = None) -> str:
    base = f"{sigla} ({municipio})"
    return f"{base}, n={alunos}" if alunos is not None else base


def _eh_cm(municipio: str, sigla: str) -> bool:
    return municipio == "Campo Mourão" and sigla == "UTFPR"


def raio_mediano_por_ies(raio_ies: pd.DataFrame) -> None:
    df = raio_ies[raio_ies["alunos"] >= MIN_ALUNOS].sort_values("raio_mediano_km")
    fig, ax = plt.subplots(figsize=(LARGURA, 0.28 * len(df) + 0.9))
    for y, linha in enumerate(df.itertuples()):
        cor = DESTAQUE if _eh_cm(linha.municipio, linha.sigla_ies) else TINTA_FRACA
        ax.plot([linha.raio_mediano_ic95_inf, linha.raio_mediano_ic95_sup], [y, y],
                color=cor, linewidth=2, solid_capstyle="round", alpha=0.45)
        ax.plot(linha.raio_mediano_km, y, "o", color=cor, markersize=6)
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(
        [_rotulo_ies(r.municipio, r.sigla_ies, r.alunos) for r in df.itertuples()]
    )
    for rotulo, linha in zip(ax.get_yticklabels(), df.itertuples()):
        if _eh_cm(linha.municipio, linha.sigla_ies):
            rotulo.set_color(DESTAQUE)
            rotulo.set_fontweight("bold")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Raio mediano (km); traço = IC de 95% (bootstrap)")
    ax.set_title("Raio mediano de atuação por IES, matriculados em TI via SISU (2017-2022)")
    _salvar(fig, "raio_mediano_por_ies")


def distribuicao_por_faixa(distribuicao: pd.DataFrame) -> None:
    chaves = [("Campo Mourão", "UTFPR"), *IES_POLOS]
    df = distribuicao.set_index(["municipio", "sigla_ies"]).loc[chaves].reset_index()
    faixas = [("ate_100_km", "até 100 km"), ("ate_300_km", "100 a 300 km"),
              ("acima_300_km", "acima de 300 km")]
    fig, ax = plt.subplots(figsize=(LARGURA, 0.32 * len(df) + 1.0))
    posicoes = range(len(df))[::-1]
    esquerda = pd.Series(0.0, index=df.index)
    for (coluna, nome), cor in zip(faixas, RAMPA_FAIXAS):
        ax.barh(list(posicoes), df[coluna], left=esquerda, color=cor, label=nome,
                edgecolor="white", linewidth=1.5, height=0.7)
        for y, valor, inicio in zip(posicoes, df[coluna], esquerda):
            if valor >= 0.08:
                ax.text(inicio + valor / 2, y, f"{valor:.0%}", ha="center", va="center",
                        fontsize=8, color=TINTA if cor == RAMPA_FAIXAS[0] else "white")
        esquerda = esquerda + df[coluna]
    ax.set_yticks(list(posicoes))
    ax.set_yticklabels([_rotulo_ies(r.municipio, r.sigla_ies, int(r.alunos))
                        for r in df.itertuples()])
    ax.get_yticklabels()[0].set_color(DESTAQUE)
    ax.get_yticklabels()[0].set_fontweight("bold")
    ax.set_xlim(0, 1)
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="y", visible=False)
    ax.legend(ncol=3, loc="lower left", bbox_to_anchor=(0, 1.0), fontsize=8)
    ax.set_title("Distância entre o município de origem e o campus", pad=22)
    _salvar(fig, "distribuicao_distancia")


def raio_por_trienio(raio_trienio: pd.DataFrame) -> None:
    municipios = ["Campo Mourão", "Ponta Grossa", "Londrina", "Curitiba", "Cascavel"]
    df = raio_trienio[raio_trienio["municipio"].isin(municipios)]
    fig, ax = plt.subplots(figsize=(LARGURA, 2.6))
    periodos = [("2017-2019", DESTAQUE, "o", "none", 0.12), ("2020-2022", SEGUNDA_SERIE, "o", None, -0.12)]
    for y, municipio in enumerate(municipios[::-1]):
        do_municipio = df[df["municipio"] == municipio].set_index("trienio")
        for periodo, cor, marcador, preenchimento, deslocamento in periodos:
            if periodo not in do_municipio.index:
                continue
            linha = do_municipio.loc[periodo]
            ax.plot([linha["raio_mediano_ic95_inf"], linha["raio_mediano_ic95_sup"]],
                    [y + deslocamento] * 2, color=cor, linewidth=2, alpha=0.4,
                    solid_capstyle="round")
            ax.plot(linha["raio_mediano_km"], y + deslocamento, marcador, color=cor,
                    markersize=7, markerfacecolor=preenchimento or cor, markeredgewidth=1.6)
    for periodo, cor, marcador, preenchimento, _ in periodos:
        ax.plot([], [], marcador, color=cor, markerfacecolor=preenchimento or cor,
                markeredgewidth=1.6, label=periodo)
    ax.set_yticks(range(len(municipios)))
    ax.set_yticklabels(municipios[::-1])
    ax.get_yticklabels()[-1].set_color(DESTAQUE)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Raio mediano (km); traço = IC de 95%")
    ax.legend(loc="lower right")
    ax.set_title("Raio mediano por triênio: Campo Mourão e grandes polos (H1)")
    _salvar(fig, "raio_por_trienio")


def democratizacao_por_ies(democ: pd.DataFrame) -> None:
    df = democ[democ["alunos"] >= MIN_ALUNOS].sort_values("pct_sem_oferta_publica")
    fig, ax = plt.subplots(figsize=(LARGURA, 0.28 * len(df) + 0.9))
    cores = [DESTAQUE if _eh_cm(r.municipio, r.sigla_ies) else CONTEXTO for r in df.itertuples()]
    ax.barh(range(len(df)), df["pct_sem_oferta_publica"], color=cores, height=0.7)
    for y, linha in enumerate(df.itertuples()):
        if _eh_cm(linha.municipio, linha.sigla_ies):
            ax.text(linha.pct_sem_oferta_publica + 0.01, y, f"{_br(linha.pct_sem_oferta_publica * 100, 1)}%",
                    va="center", color=TINTA, fontsize=8, fontweight="bold")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels([_rotulo_ies(r.municipio, r.sigla_ies, r.alunos) for r in df.itertuples()])
    for rotulo, linha in zip(ax.get_yticklabels(), df.itertuples()):
        if _eh_cm(linha.municipio, linha.sigla_ies):
            rotulo.set_color(DESTAQUE)
            rotulo.set_fontweight("bold")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Matriculados vindos de município sem curso de TI público e presencial")
    ax.set_title("Democratização do acesso por IES, SISU 2017-2022 (H5)")
    _salvar(fig, "democratizacao_por_ies")


def _marcar_quebra(ax: plt.Axes, rotulo: bool) -> None:
    quebra = ULTIMO_ANO_CAGED_ANTIGO + 0.5
    ax.axvline(quebra, color=TINTA_FRACA, linestyle="--", linewidth=1)
    if rotulo:
        ax.text(quebra - 0.12, 0.98, "CAGED antigo | Novo CAGED (eSocial)\ne pandemia",
                transform=ax.get_xaxis_transform(), ha="right", va="top", fontsize=7.5,
                color=TINTA_SECUNDARIA)


def admissoes_ti(mercado: pd.DataFrame) -> None:
    pr = mercado.groupby("ano")["admissoes"].sum()
    cm = mercado[mercado["codigo_ibge"] == CODIGO_IBGE_CAMPO_MOURAO].set_index("ano")["admissoes"]
    fig, (ax_pr, ax_cm) = plt.subplots(2, 1, figsize=(LARGURA, 4.2), sharex=True)
    for ax, serie, titulo in (
        (ax_pr, pr, "Admissões em TI no Paraná"),
        (ax_cm, cm, "Admissões em TI em Campo Mourão"),
    ):
        ax.plot(serie.index, serie.values, color=DESTAQUE, linewidth=2, marker="o", markersize=4)
        ax.set_title(titulo)
        ax.set_ylim(bottom=0)
        _marcar_quebra(ax, rotulo=ax is ax_pr)
        pico = serie.loc[2021]
        ax.annotate(f"2021: {_br(pico)}", (2021, pico), xytext=(0, 7), ha="center",
                    textcoords="offset points", fontsize=7.5, color=TINTA_SECUNDARIA)
        ax.yaxis.set_major_formatter(MILHAR)
        ax.set_ylim(top=serie.max() * 1.15)
    ax_cm.set_xticks(range(int(pr.index.min()), int(pr.index.max()) + 1))
    ax_cm.tick_params(axis="x", labelrotation=0)
    fig.suptitle("CBO de TI (famílias 2122, 2123, 2124, 3171, 3172), CAGED e Novo CAGED",
                 x=0.01, ha="left", fontsize=8, color=TINTA_FRACA, y=0.995)
    fig.tight_layout()
    _salvar(fig, "admissoes_ti")


def salario_real(mercado: pd.DataFrame, nomes: dict[int, str]) -> None:
    fig, ax = plt.subplots(figsize=(LARGURA, 3.2))
    finais = []
    for codigo in [*MUNICIPIOS_POLOS_PROVISORIOS, CODIGO_IBGE_CAMPO_MOURAO]:
        serie = mercado[mercado["codigo_ibge"] == codigo].set_index("ano")["salario_real"].dropna()
        cm = codigo == CODIGO_IBGE_CAMPO_MOURAO
        cor = DESTAQUE if cm else CONTEXTO
        ax.plot(serie.index, serie.values, color=cor, linewidth=2.2 if cm else 1.4,
                marker="o" if cm else None, markersize=4, zorder=3 if cm else 2)
        finais.append([serie.iloc[-1], nomes[codigo], cm, serie.index[-1]])
    # afasta rótulos finais que ficariam a menos de `folga` reais um do outro
    finais.sort()
    folga = 190
    for anterior, atual in pairwise(finais):
        atual[0] = max(atual[0], anterior[0] + folga)
    for y, nome, cm, ano in finais:
        ax.text(ano + 0.2, y, nome, va="center", fontsize=7.5,
                color=TINTA if cm else TINTA_SECUNDARIA, fontweight="bold" if cm else "normal")
    _marcar_quebra(ax, rotulo=False)
    ax.set_xticks(range(2015, 2026, 2))
    ax.set_xlim(2014.6, 2027.2)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"R$ {_br(v)}"))
    ax.set_title("Salário real médio de admissão em TI, a preços de 2025 (H3)\n"
                 "tracejado: troca para o Novo CAGED (eSocial), em 2020", fontsize=9)
    _salvar(fig, "salario_real")


def escore_polos(polos: pd.DataFrame) -> None:
    df = polos.sort_values("score", ascending=False).head(10).iloc[::-1]
    fig, ax = plt.subplots(figsize=(LARGURA, 3.0))
    for y, linha in enumerate(df.itertuples()):
        if linha.is_utfpr_cm:
            ax.barh(y, linha.score, color="white", edgecolor=DESTAQUE, hatch="////", height=0.7)
        else:
            ax.barh(y, linha.score, color=DESTAQUE if linha.is_grande_polo else CONTEXTO, height=0.7)
    rotulos = [f"{r.municipio} (referência)" if r.is_utfpr_cm else r.municipio
               for r in df.itertuples()]
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(rotulos)
    ax.grid(axis="y", visible=False)
    ax.axvline(0, color=CONTEXTO, linewidth=1)
    ax.legend(
        handles=[
            Patch(color=DESTAQUE, label="grande polo (top-5)"),
            Patch(facecolor="white", edgecolor=DESTAQUE, hatch="////", label="UTFPR-CM, fora do ranking"),
            Patch(color=CONTEXTO, label="demais"),
        ],
        loc="lower right",
    )
    ax.set_xlabel("Escore (soma dos z-scores: concluintes, IES, vínculos de TI, pós CAPES)")
    ax.set_title("Escore dos grandes polos de TI do Paraná")
    _salvar(fig, "escore_polos")


def _circulo_km(centro: tuple[float, float], raio_km: float) -> tuple[list[float], list[float]]:
    lat0, lon0 = map(math.radians, centro)
    d = raio_km / 6371.0
    lats, lons = [], []
    for passo in range(181):
        rumo = math.radians(passo * 2)
        lat = math.asin(math.sin(lat0) * math.cos(d) + math.cos(lat0) * math.sin(d) * math.cos(rumo))
        lon = lon0 + math.atan2(math.sin(rumo) * math.sin(d) * math.cos(lat0),
                                math.cos(d) - math.sin(lat0) * math.sin(lat))
        lats.append(math.degrees(lat))
        lons.append(math.degrees(lon))
    return lons, lats


def mapa_origens(arestas: pd.DataFrame, municipios: pd.DataFrame) -> None:
    para_cm = arestas[arestas["codigo_ibge_municipio_destino"] == CODIGO_IBGE_CAMPO_MOURAO]
    por_origem = para_cm.groupby("codigo_ibge_municipio_origem")["peso_alunos"].sum()
    coords = municipios.set_index("codigo_ibge")[["latitude", "longitude"]]
    origens = coords.loc[coords.index.intersection(por_origem.index)].assign(
        alunos=por_origem
    )
    cm = coords.loc[CODIGO_IBGE_CAMPO_MOURAO]

    fig, ax = plt.subplots(figsize=(LARGURA, LARGURA * 0.95))
    ax.scatter(municipios["longitude"], municipios["latitude"], s=0.4, color=GRADE, zorder=1)
    for linha in origens.itertuples():
        ax.plot([linha.longitude, cm["longitude"]], [linha.latitude, cm["latitude"]],
                color=DESTAQUE, linewidth=0.5, alpha=0.35, zorder=2)
    ax.scatter(origens["longitude"], origens["latitude"], s=8 + origens["alunos"] * 6,
               color=DESTAQUE, edgecolor="white", linewidth=0.6, zorder=3)
    for raio in (100, 300):
        lons, lats = _circulo_km((cm["latitude"], cm["longitude"]), raio)
        ax.plot(lons, lats, color=TINTA_SECUNDARIA, linestyle="--", linewidth=0.9, zorder=4)
        # rótulo a sudoeste do anel, longe da nuvem de origens
        ax.text(lons[112], lats[112], f"{raio} km ", fontsize=7, color=TINTA_SECUNDARIA,
                ha="right", va="top", zorder=4)
    ax.plot(cm["longitude"], cm["latitude"], "*", color=TINTA, markersize=11, zorder=4)
    ax.annotate("UTFPR-CM", (cm["longitude"], cm["latitude"]), xytext=(-8, 6), ha="right",
                textcoords="offset points", fontsize=8, fontweight="bold", color=TINTA, zorder=5)
    for tamanho in (1, 10, 40):
        ax.scatter([], [], s=8 + tamanho * 6, color=DESTAQUE, edgecolor="white",
                   label=f"{tamanho} aluno{'s' if tamanho > 1 else ''}")
    ax.legend(loc="lower left", title="Matriculados por origem", title_fontsize=8, fontsize=7.5,
              labelspacing=1.2, borderpad=0.8)
    ax.set_aspect(1 / math.cos(math.radians(-15)))
    ax.set_axis_off()
    ax.set_title(f"Origem dos matriculados no BCC da UTFPR-CM via SISU, 2017-2022 "
                 f"(n={int(por_origem.sum())})")
    _salvar(fig, "mapa_origens_cm")


def main() -> None:
    matplotlib.use("Agg")
    _estilo()
    municipios = carregar_municipios()
    nomes = dict(zip(municipios["codigo_ibge"], municipios["nome"]))
    raio_mediano_por_ies(pd.read_csv(DATA_PROCESSED_DIR / "raio_por_ies.csv"))
    distribuicao_por_faixa(pd.read_csv(DATA_PROCESSED_DIR / "distribuicao_distancia_por_ies.csv"))
    raio_por_trienio(pd.read_csv(DATA_PROCESSED_DIR / "raio_por_municipio_trienio.csv"))
    democratizacao_por_ies(pd.read_csv(DATA_PROCESSED_DIR / "democratizacao_por_ies.csv"))
    mercado = pd.read_csv(DATA_PROCESSED_DIR / "mercado_por_municipio_ano.csv")
    admissoes_ti(mercado)
    salario_real(mercado, nomes)
    escore_polos(pd.read_csv(DATA_PROCESSED_DIR / "polos.csv"))
    mapa_origens(pd.read_parquet(DATA_PROCESSED_DIR / "arestas_sisu_ti.parquet"), municipios)


if __name__ == "__main__":
    main()
