"""Monta as bases municipais de Goiás (presidente, 2022 e 2026) a partir dos ZIPs do TSE."""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "Data" / "raw" / "tse"
OUT_DIR = ROOT / "Data" / "processed"

YEARS = [2022, 2026]
UF = "GO"

JOVENS = ["16 anos", "17 anos", "18 anos", "19 anos", "20 anos", "21 a 24 anos", "25 a 29 anos"]
IDOSOS = [
    "60 a 64 anos", "65 a 69 anos", "70 a 74 anos", "75 a 79 anos", "80 a 84 anos",
    "85 a 89 anos", "90 a 94 anos", "95 a 99 anos", "100 anos ou mais",
]
BAIXA_ESCOLARIDADE = ["ANALFABETO", "LÊ E ESCREVE", "ENSINO FUNDAMENTAL INCOMPLETO"]


def read_member(zip_path: Path, suffix: str, usecols: list[str]) -> pd.DataFrame:
    wanted = set(usecols)
    with zipfile.ZipFile(zip_path) as zf:
        names = [n for n in zf.namelist() if n.endswith(suffix)]
        if len(names) != 1:
            raise FileNotFoundError(f"Esperava um arquivo {suffix} em {zip_path.name}, achei {names}")
        with zf.open(names[0]) as fh:
            df = pd.read_csv(fh, sep=";", encoding="latin1", usecols=lambda c: c in wanted, low_memory=False)
    df.columns = df.columns.str.lower()
    return df


def find_raw(name: str) -> Path:
    matches = sorted(ROOT.joinpath("Data").rglob(name))
    if not matches:
        raise FileNotFoundError(f"{name} não encontrado. Rode src/download_tse.py.")
    return matches[0]


def build_votos(year: int) -> pd.DataFrame:
    df = read_member(
        find_raw(f"votacao_candidato_munzona_{year}.zip"),
        "_BR.csv",
        ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NM_MUNICIPIO", "DS_CARGO", "NR_CANDIDATO",
         "NM_URNA_CANDIDATO", "SG_PARTIDO", "QT_VOTOS_NOMINAIS_VALIDOS"],
    )
    df = df[(df["sg_uf"] == UF) & (df["ds_cargo"].str.upper() == "PRESIDENTE")]
    out = (
        df.groupby(["nr_turno", "cd_municipio", "nm_municipio", "nr_candidato", "nm_urna_candidato", "sg_partido"],
                   as_index=False)["qt_votos_nominais_validos"].sum()
        .rename(columns={"qt_votos_nominais_validos": "votos", "nr_turno": "turno"})
    )
    out["pct_validos"] = out["votos"] / out.groupby(["turno", "cd_municipio"])["votos"].transform("sum") * 100
    out.insert(0, "ano", year)
    return out


def build_detalhe(year: int) -> pd.DataFrame:
    df = read_member(
        find_raw(f"detalhe_votacao_munzona_{year}.zip"),
        "_BR.csv",
        ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "DS_CARGO", "QT_APTOS", "QT_TOTAL_SECOES",
         "QT_COMPARECIMENTO", "QT_ABSTENCOES", "QT_TOTAL_VOTOS_VALIDOS", "QT_VOTOS_BRANCOS",
         "QT_TOTAL_VOTOS_NULOS"],
    )
    df = df[(df["sg_uf"] == UF) & (df["ds_cargo"].str.upper() == "PRESIDENTE")]
    out = df.groupby(["nr_turno", "cd_municipio"], as_index=False).sum(numeric_only=True)
    out = out.rename(columns={
        "nr_turno": "turno", "qt_aptos": "aptos", "qt_total_secoes": "secoes",
        "qt_comparecimento": "comparecimento", "qt_abstencoes": "abstencoes",
        "qt_total_votos_validos": "validos", "qt_votos_brancos": "brancos",
        "qt_total_votos_nulos": "nulos",
    })
    out["pct_abstencao"] = out["abstencoes"] / out["aptos"] * 100
    out["pct_brancos_nulos"] = (out["brancos"] + out["nulos"]) / out["comparecimento"] * 100
    out.insert(0, "ano", year)
    return out


def build_perfil(year: int) -> pd.DataFrame:
    df = read_member(
        find_raw(f"perfil_eleitor_secao_{year}_{UF}.zip"),
        f"_{UF}.csv",
        # a contagem se chama QT_ELEITORES_PERFIL em 2022 e QT_ELEITORES em 2026
        ["CD_MUNICIPIO", "DS_GENERO", "DS_FAIXA_ETARIA", "DS_GRAU_ESCOLARIDADE", "QT_ELEITORES",
         "QT_ELEITORES_PERFIL"],
    ).rename(columns={"qt_eleitores_perfil": "qt_eleitores"})
    for col in ["ds_genero", "ds_faixa_etaria", "ds_grau_escolaridade"]:
        df[col] = df[col].str.strip()

    def share(mask: pd.Series) -> pd.Series:
        return df.loc[mask].groupby("cd_municipio")["qt_eleitores"].sum()

    out = df.groupby("cd_municipio")["qt_eleitores"].sum().to_frame("eleitores")
    parts = {
        "pct_feminino": df["ds_genero"] == "FEMININO",
        "pct_16_17": df["ds_faixa_etaria"].isin(["16 anos", "17 anos"]),
        "pct_16_29": df["ds_faixa_etaria"].isin(JOVENS),
        "pct_30_44": df["ds_faixa_etaria"].isin(["30 a 34 anos", "35 a 39 anos", "40 a 44 anos"]),
        "pct_45_59": df["ds_faixa_etaria"].isin(["45 a 49 anos", "50 a 54 anos", "55 a 59 anos"]),
        "pct_60_mais": df["ds_faixa_etaria"].isin(IDOSOS),
        "pct_superior_completo": df["ds_grau_escolaridade"] == "SUPERIOR COMPLETO",
        "pct_baixa_escolaridade": df["ds_grau_escolaridade"].isin(BAIXA_ESCOLARIDADE),
    }
    for name, mask in parts.items():
        out[name] = share(mask).reindex(out.index, fill_value=0) / out["eleitores"] * 100
    out = out.reset_index()
    out.insert(0, "ano", year)
    return out


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables = {
        "presidente_go_votos": pd.concat([build_votos(y) for y in YEARS], ignore_index=True),
        "presidente_go_comparecimento": pd.concat([build_detalhe(y) for y in YEARS], ignore_index=True),
        "eleitorado_go_perfil": pd.concat([build_perfil(y) for y in YEARS], ignore_index=True),
    }
    for name, df in tables.items():
        n_mun = df.groupby("ano")["cd_municipio"].nunique().to_dict()
        if set(n_mun.values()) != {246}:
            raise ValueError(f"{name}: esperava 246 municípios por ano, achei {n_mun}")
        df.to_parquet(OUT_DIR / f"{name}.parquet", index=False)
        df.to_csv(OUT_DIR / f"{name}.csv", index=False, encoding="utf-8")
        print(f"{name}: {len(df)} linhas")


if __name__ == "__main__":
    main()
