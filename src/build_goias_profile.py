from __future__ import annotations

import argparse
import io
import zipfile
from pathlib import Path

import pandas as pd


def load_table_from_file(path: str | Path) -> pd.DataFrame:
    p = Path(path)
    if p.suffix.lower() == ".csv":
        return pd.read_csv(p, sep=';', encoding='latin1', low_memory=False)
    if p.suffix.lower() == ".zip":
        with zipfile.ZipFile(p) as zf:
            csv_names = [n for n in zf.namelist() if n.lower().endswith('.csv')]
            if not csv_names:
                raise FileNotFoundError(f'Nenhum CSV encontrado em: {p}')
            target = csv_names[0]
            with zf.open(target) as fh:
                text = io.TextIOWrapper(fh, encoding='latin1')
                return pd.read_csv(text, sep=';', low_memory=False)
    raise ValueError(f'Formato não suportado: {p}')


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    return df


def aggregate_for_goias(file_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    df = load_table_from_file(file_path)
    df = normalize_columns(df)

    if 'nm_municipio' not in df.columns:
        raise KeyError('Coluna nm_municipio não encontrada. Verifique a base escolhida.')

    if 'qt_eleitores' not in df.columns:
        raise KeyError('Coluna qt_eleitores não encontrada na base escolhida.')

    out = df.groupby('nm_municipio', as_index=False).agg(
        total_eleitores=('qt_eleitores', 'sum'),
        total_secoes=('nr_secao', 'nunique'),
        total_zonas=('nr_zona', 'nunique')
    )

    if 'ds_genero' in df.columns:
        gen = (
            df.groupby(['nm_municipio', 'ds_genero'], as_index=False)['qt_eleitores']
            .sum()
            .pivot(index='nm_municipio', columns='ds_genero', values='qt_eleitores')
            .fillna(0)
        )
        gen = gen.rename_axis(None, axis=1).reset_index()
        out = out.merge(gen, on='nm_municipio', how='left')

    if 'ds_faixa_etaria' in df.columns:
        faixa = (
            df.groupby(['nm_municipio', 'ds_faixa_etaria'], as_index=False)['qt_eleitores']
            .sum()
            .pivot(index='nm_municipio', columns='ds_faixa_etaria', values='qt_eleitores')
            .fillna(0)
        )
        faixa = faixa.rename_axis(None, axis=1).reset_index()
        out = out.merge(faixa, on='nm_municipio', how='left')

    if 'ds_grau_escolaridade' in df.columns:
        esc = (
            df.groupby(['nm_municipio', 'ds_grau_escolaridade'], as_index=False)['qt_eleitores']
            .sum()
            .pivot(index='nm_municipio', columns='ds_grau_escolaridade', values='qt_eleitores')
            .fillna(0)
        )
        esc = esc.rename_axis(None, axis=1).reset_index()
        out = out.merge(esc, on='nm_municipio', how='left')

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(output, index=False)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description='Agrega perfil do eleitorado em nível municipal para Goiás.')
    parser.add_argument('--input', required=True, help='Arquivo CSV ou ZIP da base de perfil do eleitorado.')
    parser.add_argument('--output', required=True, help='Arquivo Parquet do agregado municipal.')
    args = parser.parse_args()

    aggregate_for_goias(args.input, args.output)
    print(f'Arquivo salvo em: {args.output}')


if __name__ == '__main__':
    main()
