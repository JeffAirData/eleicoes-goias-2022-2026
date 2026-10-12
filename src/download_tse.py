"""Baixa do Portal de Dados Abertos do TSE os arquivos usados na análise."""
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "Data" / "raw" / "tse"
BASE_URL = "https://cdn.tse.jus.br/estatistica/sead/odsele"

FILES = [
    "perfil_eleitor_secao/perfil_eleitor_secao_2022_GO.zip",
    "perfil_eleitor_secao/perfil_eleitor_secao_2026_GO.zip",
    "detalhe_votacao_munzona/detalhe_votacao_munzona_2022.zip",
    "detalhe_votacao_munzona/detalhe_votacao_munzona_2026.zip",
    "votacao_candidato_munzona/votacao_candidato_munzona_2022.zip",
    "votacao_candidato_munzona/votacao_candidato_munzona_2026.zip",
]


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for item in FILES:
        target = RAW_DIR / Path(item).name
        if target.exists():
            print(f"Já existe: {target.name}")
            continue
        print(f"Baixando: {item}")
        partial = target.with_suffix(".part")
        urllib.request.urlretrieve(f"{BASE_URL}/{item}", partial)
        partial.rename(target)


if __name__ == "__main__":
    main()
