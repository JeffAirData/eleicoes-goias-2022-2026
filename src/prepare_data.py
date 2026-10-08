from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = DATA_DIR / "data" / "raw"
INTERIM_DIR = DATA_DIR / "data" / "interim"
PROCESSED_DIR = DATA_DIR / "data" / "processed"


def infer_separator(sample: str) -> str:
    candidates = [";", ",", "\t", "|"]
    counts = {sep: sample.count(sep) for sep in candidates}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else ";"


def read_raw_file(file_path: str | Path) -> pd.DataFrame:
    path = Path(file_path)

    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="latin1", newline="") as f:
            sample = f.read(8192)
            f.seek(0)
            sep = infer_separator(sample)
        return pd.read_csv(path, sep=sep, encoding="latin1", low_memory=False)

    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as zf:
            members = [name for name in zf.namelist() if name.lower().endswith(".csv")]
            if not members:
                raise ValueError(f"Nenhum CSV encontrado dentro do ZIP: {path}")
            target = members[0]
            with zf.open(target) as f:
                text = io.TextIOWrapper(f, encoding="latin1")
                sample = text.read(8192)
                text.seek(0)
                sep = infer_separator(sample)
                return pd.read_csv(text, sep=sep, low_memory=False)

    raise ValueError(f"Formato não suportado: {path}")


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]
    return df


def save_parquet(df: pd.DataFrame, output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output, index=False)


def find_raw_sources(base_dir: Path) -> list[Path]:
    if base_dir.is_file():
        return [base_dir] if base_dir.suffix.lower() in {".csv", ".zip"} else []

    return sorted(
        [p for p in base_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".csv", ".zip"}],
        key=lambda p: str(p),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte dados do TSE em Parquet para uso em análise.")
    parser.add_argument("--source-dir", type=str, default=str(RAW_DIR), help="Arquivo ou diretório com dados CSV/ZIP originais.")
    parser.add_argument("--output-dir", type=str, default=str(PROCESSED_DIR), help="Diretório alvo para parquet.")
    args = parser.parse_args()

    source_path = Path(args.source_dir)
    output_dir = Path(args.output_dir)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    if source_path.exists() is False:
        print(f"Caminho não encontrado: {source_path}")
        return

    files = find_raw_sources(source_path)
    if not files:
        print(f"Nenhum CSV ou ZIP encontrado em {source_path}.")
        return

    for file_path in files:
        try:
            df = read_raw_file(file_path)
            df = standardize_columns(df)

            year = next((part for part in file_path.parts if part.isdigit() and len(part) == 4), "unknown")
            relative_name = file_path.name.replace(file_path.suffix, "")
            parquet_path = output_dir / year / f"{relative_name}.parquet"
            save_parquet(df, parquet_path)
            print(f"Arquivo processado: {file_path} -> {parquet_path}")
        except Exception as exc:  # pragma: no cover - log de processamento
            print(f"Erro ao processar {file_path}: {exc}")


if __name__ == "__main__":
    main()
