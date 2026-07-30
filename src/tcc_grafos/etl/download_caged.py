"""Download dos microdados do CAGED (Novo CAGED e, se preciso, CAGED antigo/RAIS)."""

from __future__ import annotations

import logging
from pathlib import Path

import requests
from tqdm import tqdm

from tcc_grafos.config import DATA_RAW_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: preencher com a URL base real (o prof vai passar os links)
CAGED_BASE_URL_TEMPLATE = "PREENCHER_URL_BASE/{ano}/{ano}{mes:02d}/CAGEDMOV{ano}{mes:02d}.parquet"


def baixar_competencia(ano: int, mes: int, destino: Path = DATA_RAW_DIR / "caged") -> Path:
    destino.mkdir(parents=True, exist_ok=True)
    url = CAGED_BASE_URL_TEMPLATE.format(ano=ano, mes=mes)
    arquivo = destino / f"caged_{ano}{mes:02d}.parquet"

    logger.info("baixando CAGED %s-%02d", ano, mes)
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(arquivo, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                bar.update(len(chunk))

    return arquivo


def baixar_periodo(ano_inicio: int, ano_fim: int) -> None:
    for ano in range(ano_inicio, ano_fim + 1):
        for mes in range(1, 13):
            try:
                baixar_competencia(ano, mes)
            except requests.HTTPError as exc:
                logger.warning("sem dado para %s-%02d: %s", ano, mes, exc)


if __name__ == "__main__":
    from tcc_grafos.config import ANO_FIM, ANO_INICIO

    baixar_periodo(ANO_INICIO, ANO_FIM)
