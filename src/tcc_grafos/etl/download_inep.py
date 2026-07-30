"""Download dos microdados do Censo da Educação Superior (INEP)."""

from __future__ import annotations

import logging
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

from tcc_grafos.config import ANO_FIM, ANO_INICIO, DATA_RAW_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: preencher com as URLs oficiais (o prof vai passar os links)
MICRODADOS_URLS: dict[int, str] = {
    # 2015: "https://...",
}


def baixar_ano(ano: int, destino: Path = DATA_RAW_DIR / "inep") -> Path:
    if ano not in MICRODADOS_URLS:
        raise KeyError(f"sem URL cadastrada para {ano}")

    destino.mkdir(parents=True, exist_ok=True)
    url = MICRODADOS_URLS[ano]
    zip_path = destino / f"censo_superior_{ano}.zip"

    logger.info("baixando INEP %s", ano)
    with requests.get(url, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(zip_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True) as bar:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
                bar.update(len(chunk))

    extraido_em = destino / str(ano)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(extraido_em)

    return extraido_em


def baixar_periodo(ano_inicio: int = ANO_INICIO, ano_fim: int = ANO_FIM) -> None:
    for ano in range(ano_inicio, ano_fim + 1):
        try:
            baixar_ano(ano)
        except KeyError as exc:
            logger.warning("pulando %s: %s", ano, exc)


if __name__ == "__main__":
    baixar_periodo()
