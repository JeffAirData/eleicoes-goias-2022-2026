"""Gera os gráficos (PNG) e o painel interativo (HTML) a partir das bases processadas."""
from __future__ import annotations

import json
import unicodedata
from pathlib import Path

import geobr
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "Data" / "processed"
DOCS_DIR = ROOT / "docs"
IMG_DIR = DOCS_DIR / "img"

PL, PT, CAIADO, OUTROS = "#2a78d6", "#e34948", "#eda100", "#c3c2b7"
INK, INK_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"
FONTE = "Fonte: TSE, Portal de Dados Abertos. 1º turno, votos válidos para presidente em Goiás."

# nomes que o TSE grava diferente do IBGE
NOMES_IBGE = {
    "BOM JESUS": "BOM JESUS DE GOIAS",
    "SAO JOAO D ALIANCA": "SAO JOAO D'ALIANCA",
    "SITIO D ABADIA": "SITIO D'ABADIA",
}

plt.rcParams.update({
    "font.family": "Segoe UI", "font.size": 11, "text.color": INK, "axes.labelcolor": INK_2,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.edgecolor": "#c3c2b7",
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
})


def normalize(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value).strip().upper())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return NOMES_IBGE.get(text, text)


def fmt(value: float, dec: int = 1) -> str:
    return f"{value:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def load_municipios() -> pd.DataFrame:
    votos = pd.read_parquet(DATA_DIR / "presidente_go_votos.parquet")
    detalhe = pd.read_parquet(DATA_DIR / "presidente_go_comparecimento.parquet")
    perfil = pd.read_parquet(DATA_DIR / "eleitorado_go_perfil.parquet")
    votos, detalhe = votos[votos["turno"] == 1], detalhe[detalhe["turno"] == 1]

    def pct(ano: int, numero: int) -> pd.Series:
        sel = votos[(votos["ano"] == ano) & (votos["nr_candidato"] == numero)]
        return sel.set_index("cd_municipio")["pct_validos"]

    nomes = votos[votos["ano"] == 2026].drop_duplicates("cd_municipio")
    mun = nomes.set_index("cd_municipio")[["nm_municipio"]].copy()
    mun["pt_2022"], mun["pt_2026"] = pct(2022, 13), pct(2026, 13)
    mun["pl_2022"], mun["pl_2026"] = pct(2022, 22), pct(2026, 22)
    mun["caiado_2026"] = pct(2026, 55)
    mun["var_pt"] = mun["pt_2026"] - mun["pt_2022"]
    mun["var_pl"] = mun["pl_2026"] - mun["pl_2022"]
    for ano in (2022, 2026):
        det = detalhe[detalhe["ano"] == ano].set_index("cd_municipio")
        mun[f"aptos_{ano}"] = det["aptos"]
        mun[f"abstencao_{ano}"] = det["pct_abstencao"]
        mun[f"vencedor_{ano}"] = (mun[f"pl_{ano}"] > mun[f"pt_{ano}"]).map({True: "PL", False: "PT"})
        per = perfil[perfil["ano"] == ano].set_index("cd_municipio")
        mun[f"pct_60_mais_{ano}"] = per["pct_60_mais"]
        mun[f"pct_16_29_{ano}"] = per["pct_16_29"]
    return mun.reset_index()


def load_geo(mun: pd.DataFrame):
    shapes = geobr.read_municipality(code_muni="GO", year=2020)
    shapes["chave"] = shapes["name_muni"].map(normalize)
    geo = shapes.merge(mun.assign(chave=mun["nm_municipio"].map(normalize)), on="chave", how="left")
    if geo["cd_municipio"].isna().any() or len(geo) != len(mun):
        raise ValueError("Municípios do TSE e do IBGE não casaram 1 para 1.")
    return geo


def estado(ano: int, turno: int = 1) -> pd.Series:
    votos = pd.read_parquet(DATA_DIR / "presidente_go_votos.parquet")
    sel = votos[(votos["ano"] == ano) & (votos["turno"] == turno)]
    return sel.groupby("nr_candidato")["votos"].sum() / sel["votos"].sum() * 100


def chart_resultado() -> None:
    linhas = []
    for ano, nome_pl in ((2022, "Jair Bolsonaro (PL)"), (2026, "Flávio Bolsonaro (PL)")):
        s = estado(ano)
        partes = [(nome_pl, s[22], PL), ("Lula (PT)", s[13], PT)]
        if ano == 2026:
            partes.append(("Caiado (PSD)", s[55], CAIADO))
        partes.append(("Outros", 100 - sum(p[1] for p in partes), OUTROS))
        linhas.append((ano, partes))

    fig, ax = plt.subplots(figsize=(11, 4.2))
    for y, (ano, partes) in zip((1, 0), linhas):
        left = 0.0
        for nome, valor, cor in partes:
            ax.barh(y, valor, left=left, color=cor, height=0.5, edgecolor=SURFACE, linewidth=2)
            if valor >= 9:
                ax.text(left + valor / 2, y, f"{fmt(valor)}%", ha="center", va="center",
                        color="white" if cor != CAIADO else INK, fontsize=13, fontweight="bold")
                ax.text(left + valor / 2, y + 0.36, nome, ha="center", va="bottom", color=INK_2, fontsize=10.5)
            else:
                ax.text(101, y, f"Outros\n{fmt(valor)}%", ha="left", va="center", color=INK_2, fontsize=10.5)
            left += valor
        ax.text(-1.5, y, str(ano), ha="right", va="center", fontsize=14, fontweight="bold")
    ax.set_xlim(0, 108)
    ax.set_ylim(-0.45, 1.75)
    ax.axis("off")
    fig.suptitle("Presidente em Goiás: Lula perde 8,5 pontos; PL mantém a maioria", x=0.02, ha="left",
                 fontsize=16, fontweight="bold")
    fig.text(0.02, 0.02, FONTE, color=MUTED, fontsize=9)
    fig.savefig(IMG_DIR / "01_resultado_estadual.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def chart_mapas(geo) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.3))
    for ax, ano in zip(axes, (2022, 2026)):
        col = f"vencedor_{ano}"
        geo.plot(ax=ax, color=geo[col].map({"PL": PL, "PT": PT}), edgecolor=SURFACE, linewidth=0.35)
        n = geo[col].value_counts()
        ax.set_title(f"{ano}: PL {n.get('PL', 0)} × {n.get('PT', 0)} PT", fontsize=15, fontweight="bold", color=INK)
        ax.axis("off")
    fig.legend(handles=[Patch(color=PL, label="PL à frente"), Patch(color=PT, label="PT à frente")],
               loc="lower center", ncol=2, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle("69 municípios goianos trocaram o PT pelo PL; nenhum fez o caminho inverso",
                 x=0.03, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.03, 0.02, FONTE + " Candidato mais votado por município.", color=MUTED, fontsize=9)
    fig.subplots_adjust(top=0.84, bottom=0.12, wspace=0.02)
    fig.savefig(IMG_DIR / "02_mapa_vencedor.png", dpi=100)
    plt.close(fig)


def chart_dispersao(mun: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 7.4))
    lim = (15, 85)
    ax.plot(lim, lim, color="#c3c2b7", linewidth=1, zorder=1)
    ax.text(79, 81, "mesmo % de 2022", color=MUTED, fontsize=9.5, rotation=45, ha="center", va="bottom")
    ax.scatter(mun["pt_2022"], mun["pt_2026"], s=34, color=PT, edgecolor=SURFACE, linewidth=0.8, zorder=2)
    for _, row in mun.nlargest(3, "aptos_2026").iterrows():
        ax.annotate(row["nm_municipio"].title().replace(" De ", " de "), (row["pt_2022"], row["pt_2026"]),
                    xytext=(70, -38), textcoords="offset points", color=INK, fontsize=10, va="center",
                    arrowprops={"arrowstyle": "-", "color": INK_2, "linewidth": 0.8, "shrinkB": 4})
    ax.set_xlim(lim)
    ax.set_ylim(lim)
    ax.set_aspect("equal")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.set_xlabel("% dos válidos para Lula em 2022")
    ax.set_ylabel("% dos válidos para Lula em 2026")
    ax.set_title("Lula recuou em todos os 246 municípios de Goiás", loc="left", fontsize=15,
                 fontweight="bold", color=INK, pad=14)
    fig.text(0.02, 0.01, FONTE + " Cada ponto é um município.", color=MUTED, fontsize=9)
    fig.savefig(IMG_DIR / "03_lula_2022_x_2026.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def chart_idade() -> None:
    perfil = pd.read_parquet(DATA_DIR / "eleitorado_go_perfil.parquet")
    faixas = {"16 a 29 anos": "pct_16_29", "30 a 44 anos": "pct_30_44", "45 a 59 anos": "pct_45_59",
              "60 anos ou mais": "pct_60_mais"}
    valores = {}
    for ano, df in perfil.groupby("ano"):
        valores[ano] = [(df[c] * df["eleitores"]).sum() / df["eleitores"].sum() for c in faixas.values()]

    fig, ax = plt.subplots(figsize=(9, 4.8))
    largura = 0.36
    for i, (ano, cor) in enumerate(((2022, "#9ec5f4"), (2026, "#256abf"))):
        xs = [x + (i - 0.5) * (largura + 0.03) for x in range(len(faixas))]
        ax.bar(xs, valores[ano], width=largura, color=cor, label=str(ano))
        for x, valor in zip(xs, valores[ano]):
            ax.text(x, valor + 0.5, fmt(valor), ha="center", va="bottom", color=INK_2, fontsize=10.5)
    ax.set_xticks(range(len(faixas)), faixas.keys())
    ax.tick_params(axis="x", colors=INK_2, length=0)
    ax.set_ylabel("% do eleitorado")
    ax.set_ylim(0, 36)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines["left"].set_visible(False)
    ax.legend(frameon=False, loc="upper right", ncol=2)
    ax.set_title("O eleitorado goiano envelheceu em quatro anos", loc="left", fontsize=15,
                 fontweight="bold", color=INK, pad=14)
    fig.text(0.02, 0.0, "Fonte: TSE, perfil do eleitorado por seção (2022 e 2026).", color=MUTED, fontsize=9)
    fig.savefig(IMG_DIR / "04_eleitorado_idade.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def build_painel(geo) -> None:
    simples = geo.copy()
    simples["geometry"] = simples.geometry.simplify(0.01)
    simples["cd_municipio"] = simples["cd_municipio"].astype(int).astype(str)
    geojson = json.loads(simples[["cd_municipio", "geometry"]].to_json())
    hover = {"cd_municipio": False, "pt_2022": ":.1f", "pt_2026": ":.1f", "pl_2022": ":.1f", "pl_2026": ":.1f",
             "caiado_2026": ":.1f", "abstencao_2026": ":.1f", "aptos_2026": ":,"}
    labels = {"pt_2022": "Lula 2022 (%)", "pt_2026": "Lula 2026 (%)", "pl_2022": "Jair Bolsonaro 2022 (%)",
              "pl_2026": "Flávio Bolsonaro 2026 (%)", "caiado_2026": "Caiado 2026 (%)",
              "abstencao_2026": "Abstenção 2026 (%)", "aptos_2026": "Eleitores aptos 2026",
              "var_pt": "Variação de Lula (p.p.)", "var_pl": "Variação do PL (p.p.)"}
    dados = pd.DataFrame(simples.drop(columns="geometry"))

    def mapa(coluna: str, escala: str | list, titulo: str, **kwargs):
        fig = px.choropleth(dados, geojson=geojson, locations="cd_municipio", featureidkey="properties.cd_municipio",
                            color=coluna, color_continuous_scale=escala, hover_name="name_muni",
                            hover_data=hover, labels=labels, title=titulo, **kwargs)
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_traces(marker_line_color="white", marker_line_width=0.4)
        fig.update_layout(margin={"r": 0, "l": 0, "t": 50, "b": 0}, height=620, paper_bgcolor=SURFACE,
                          font_family="Segoe UI, system-ui, sans-serif")
        return fig

    figs = [
        mapa("var_pt", ["#a82c2c", "#e66767", "#f6d5d5"],
             "Variação do voto em Lula entre 2022 e 2026 (pontos percentuais)"),
        mapa("var_pl", ["#e34948", "#f0efec", "#2a78d6"],
             "Variação do voto no PL entre 2022 e 2026 (pontos percentuais)", color_continuous_midpoint=0),
        mapa("caiado_2026", ["#fbeecb", "#eda100", "#8a5d00"], "Voto em Ronaldo Caiado em 2026 (% dos válidos)"),
    ]
    blocos = [f.to_html(full_html=False, include_plotlyjs="cdn" if i == 0 else False) for i, f in enumerate(figs)]
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Presidente em Goiás: 2022 x 2026</title>
<style>
  body {{ font-family: "Segoe UI", system-ui, sans-serif; background: #f9f9f7; color: {INK}; margin: 0; }}
  main {{ max-width: 1000px; margin: 0 auto; padding: 24px 16px; }}
  p {{ color: {INK_2}; }}
  section {{ background: {SURFACE}; border: 1px solid {GRID}; border-radius: 8px; margin: 16px 0; padding: 8px; }}
</style>
</head>
<body>
<main>
<h1>Presidente em Goiás: 2022 x 2026</h1>
<p>1º turno, votos válidos por município. Passe o mouse sobre um município para ver os números.</p>
{''.join(f'<section>{b}</section>' for b in blocos)}
<p>{FONTE} Malha municipal: IBGE 2020.</p>
</main>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    mun = load_municipios()
    mun.to_csv(DATA_DIR / "resumo_municipios_go.csv", index=False, encoding="utf-8")
    geo = load_geo(mun)
    chart_resultado()
    chart_mapas(geo)
    chart_dispersao(mun)
    chart_idade()
    build_painel(geo)
    print(f"Gráficos em {IMG_DIR} e painel em {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
