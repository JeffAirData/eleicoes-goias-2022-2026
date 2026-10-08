from __future__ import annotations

import argparse
import unicodedata
from pathlib import Path

import geopandas as gpd
import geobr
import pandas as pd
import plotly.express as px


def normalize_text(value: object) -> str:
    text = str(value).strip().upper()
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(ch for ch in text if not unicodedata.combining(ch))
    return text


def load_profile(path: str | Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df = df.copy()
    df['municipio_norm'] = df['nm_municipio'].map(normalize_text)
    return df


def load_municipal_shapes(year: int = 2020) -> gpd.GeoDataFrame:
    return geobr.read_municipality(code_muni='GO', year=year)


def build_geo_profile(profile_path: str | Path, output_html: str | Path) -> None:
    profile = load_profile(profile_path)
    municipalities = load_municipal_shapes(year=2020)

    municipalities = municipalities.copy()
    municipalities['municipio_norm'] = municipalities['name_muni'].map(normalize_text)

    merged = municipalities.merge(
        profile[['municipio_norm', 'total_eleitores', 'FEMININO', 'MASCULINO', 'total_secoes']],
        on='municipio_norm',
        how='left',
    )

    merged['share_feminino'] = (merged['FEMININO'] / merged['total_eleitores'] * 100).fillna(0)
    merged['share_masculino'] = (merged['MASCULINO'] / merged['total_eleitores'] * 100).fillna(0)
    merged['code_muni'] = merged['code_muni'].astype(str)

    fig = px.choropleth(
        merged,
        geojson=merged.geometry.__geo_interface__,
        locations='code_muni',
        featureidkey='properties.code_muni',
        color='share_feminino',
        labels={'share_feminino': '% de eleitores do sexo feminino'},
        title='Goiás: proporção de eleitores do sexo feminino por município',
        projection='mercator',
    )
    fig.update_geos(fitbounds='locations', visible=False)
    fig.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})

    output = Path(output_html)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(output)
    print(f'Mapa salvo em: {output}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Cria mapa coroplético de perfil do eleitorado por município em Goiás.')
    parser.add_argument('--input', type=str, required=True, help='Parquet municipal da base de perfil do eleitorado.')
    parser.add_argument('--output', type=str, default='data/processed/goias_profile_map.html', help='Arquivo HTML do mapa.')
    args = parser.parse_args()

    build_geo_profile(args.input, args.output)


if __name__ == '__main__':
    main()
