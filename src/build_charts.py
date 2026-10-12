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


def draw_resultado(ax, escala: float = 1.0) -> None:
    linhas = []
    for ano, nome_pl in ((2022, "Jair Bolsonaro (PL)"), (2026, "Flávio Bolsonaro (PL)")):
        s = estado(ano)
        partes = [(nome_pl, s[22], PL), ("Lula (PT)", s[13], PT)]
        if ano == 2026:
            partes.append(("Caiado (PSD)", s[55], CAIADO))
        partes.append(("Outros", 100 - sum(p[1] for p in partes), OUTROS))
        linhas.append((ano, partes))

    for y, (ano, partes) in zip((1, 0), linhas):
        left = 0.0
        for nome, valor, cor in partes:
            ax.barh(y, valor, left=left, color=cor, height=0.5, edgecolor=SURFACE, linewidth=2)
            if valor >= 9:
                ax.text(left + valor / 2, y, f"{fmt(valor)}%", ha="center", va="center",
                        color="white" if cor != CAIADO else INK, fontsize=13 * escala, fontweight="bold")
                ax.text(left + valor / 2, y + 0.36, nome, ha="center", va="bottom", color=INK_2,
                        fontsize=10.5 * escala)
            else:
                ax.text(101, y, f"Outros\n{fmt(valor)}%", ha="left", va="center", color=INK_2,
                        fontsize=10.5 * escala)
            left += valor
        ax.text(-1.5, y, str(ano), ha="right", va="center", fontsize=14 * escala, fontweight="bold")
    ax.set_xlim(0, 108)
    ax.set_ylim(-0.45, 1.75)
    ax.axis("off")


def draw_mapas(axes, geo, fontsize: float = 15) -> None:
    for ax, ano in zip(axes, (2022, 2026)):
        col = f"vencedor_{ano}"
        geo.plot(ax=ax, color=geo[col].map({"PL": PL, "PT": PT}), edgecolor=SURFACE, linewidth=0.35)
        n = geo[col].value_counts()
        ax.set_title(f"{ano}: PL {n.get('PL', 0)} × {n.get('PT', 0)} PT", fontsize=fontsize, fontweight="bold",
                     color=INK)
        ax.axis("off")


def chart_resultado() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.2))
    draw_resultado(ax)
    fig.suptitle("Presidente em Goiás: Lula perde 8,5 pontos; PL mantém a maioria", x=0.02, ha="left",
                 fontsize=16, fontweight="bold")
    fig.text(0.02, 0.02, FONTE, color=MUTED, fontsize=9)
    fig.savefig(IMG_DIR / "01_resultado_estadual.png", dpi=200, bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)


def chart_mapas(geo) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 6.3))
    draw_mapas(axes, geo)
    fig.legend(handles=[Patch(color=PL, label="PL à frente"), Patch(color=PT, label="PT à frente")],
               loc="lower center", ncol=2, frameon=False, fontsize=11, bbox_to_anchor=(0.5, 0.06))
    fig.suptitle("69 municípios goianos trocaram o PT pelo PL; nenhum fez o caminho inverso",
                 x=0.03, ha="left", fontsize=17, fontweight="bold")
    fig.text(0.03, 0.02, FONTE + " Candidato mais votado por município.", color=MUTED, fontsize=9)
    fig.subplots_adjust(top=0.84, bottom=0.12, wspace=0.02)
    fig.savefig(IMG_DIR / "02_mapa_vencedor.png", dpi=100)
    plt.close(fig)


def chart_painel(mun: pd.DataFrame, geo) -> None:
    """Painel único (1200x1500) com os principais números, para redes sociais."""
    detalhe = pd.read_parquet(DATA_DIR / "presidente_go_comparecimento.parquet")
    det = detalhe[(detalhe["ano"] == 2026) & (detalhe["turno"] == 1)]
    abstencao = det["abstencoes"].sum() / det["aptos"].sum() * 100
    pt_frente = {ano: int((mun[f"vencedor_{ano}"] == "PT").sum()) for ano in (2022, 2026)}
    viraram = int(((mun["vencedor_2022"] == "PT") & (mun["vencedor_2026"] == "PL")).sum())
    voltaram = int(((mun["vencedor_2022"] == "PL") & (mun["vencedor_2026"] == "PT")).sum())
    blocos = [
        (PT, f"{pt_frente[2022]} → {pt_frente[2026]}", "cidades com Lula\nna frente"),
        (PL, f"{viraram} a {voltaram}", "cidades trocaram\no PT pelo PL"),
        (CAIADO, f"1 em {round(100 / estado(2026)[55])}", "votos foi para\nRonaldo Caiado"),
        (OUTROS, f"{round(abstencao)} em 100", "eleitores não\nforam votar"),
    ]

    fig = plt.figure(figsize=(12, 15))
    fig.text(0.05, 0.955, "Como Goiás votou para presidente", fontsize=34, fontweight="bold")
    fig.text(0.05, 0.925, "1º turno de 2022 e de 2026, nas 246 cidades do estado", fontsize=19, color=INK_2)

    for k, (cor, numero, legenda) in enumerate(blocos):
        x = 0.05 + k * 0.232
        fig.add_artist(plt.Rectangle((x, 0.875), 0.05, 0.006, color=cor, transform=fig.transFigure))
        fig.text(x, 0.835, numero, fontsize=35, fontweight="bold", va="center")
        fig.text(x, 0.808, legenda, fontsize=15.5, color=INK_2, va="top", linespacing=1.3)

    fig.text(0.05, 0.725, "De cada 100 votos no estado", fontsize=20, fontweight="bold")
    draw_resultado(fig.add_axes([0.085, 0.555, 0.90, 0.16]), escala=1.3)

    fig.text(0.05, 0.515, "Quem ficou na frente em cada cidade", fontsize=20, fontweight="bold")
    draw_mapas([fig.add_axes([0.03, 0.10, 0.47, 0.38]), fig.add_axes([0.50, 0.10, 0.47, 0.38])], geo, fontsize=18)
    fig.legend(handles=[Patch(color=PL, label="PL na frente"), Patch(color=PT, label="PT na frente")],
               loc="lower center", ncol=2, frameon=False, fontsize=15, bbox_to_anchor=(0.5, 0.058))
    fig.text(0.05, 0.025, "Fonte: TSE, Portal de Dados Abertos. Votos válidos para presidente em Goiás.",
             fontsize=13, color=MUTED)
    fig.text(0.95, 0.025, "github.com/JeffAirData", fontsize=13, color=MUTED, ha="right")
    fig.savefig(IMG_DIR / "painel_resumo.png", dpi=100)
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


def chart_cartoes(mun: pd.DataFrame) -> None:
    perfil = pd.read_parquet(DATA_DIR / "eleitorado_go_perfil.parquet")
    idosos = {ano: (df["pct_60_mais"] * df["eleitores"]).sum() / df["eleitores"].sum()
              for ano, df in perfil.groupby("ano")}
    pt_frente = {ano: int((mun[f"vencedor_{ano}"] == "PT").sum()) for ano in (2022, 2026)}
    viraram = int(((mun["vencedor_2022"] == "PT") & (mun["vencedor_2026"] == "PL")).sum())
    voltaram = int(((mun["vencedor_2022"] == "PL") & (mun["vencedor_2026"] == "PT")).sum())
    cairam = int((mun["var_pt"] < 0).sum())
    caiado = estado(2026)[55]

    cartoes = [
        (PT, f"{pt_frente[2022]} → {pt_frente[2026]}",
         "cidades de Goiás onde Lula foi\no mais votado para presidente,\nem 2022 e em 2026"),
        (PT, f"{cairam} de {len(mun)}",
         "Lula teve uma parcela menor\ndos votos em todas as\ncidades goianas" if cairam == len(mun)
         else "cidades goianas onde Lula teve\numa parcela menor dos votos"),
        (PL, f"{viraram} a {voltaram}",
         f"{viraram} cidades trocaram o PT pelo PL.\n"
         + ("Nenhuma fez o caminho contrário." if voltaram == 0 else f"{voltaram} fizeram o caminho contrário.")),
        (CAIADO, f"1 em cada {round(100 / caiado)}",
         "votos para presidente em Goiás\nfoi para Ronaldo Caiado,\nex-governador do estado"),
        ("#256abf", f"1 em cada {round(100 / idosos[2026])}",
         f"eleitores goianos tem 60 anos ou mais.\nEm 2022, eram {round(idosos[2022])} em cada 100.\n"
         f"Hoje são {round(idosos[2026])}."),
    ]
    for i, (cor, numero, frase) in enumerate(cartoes, start=1):
        fig = plt.figure(figsize=(10.8, 10.8))
        fig.add_artist(plt.Rectangle((0.08, 0.86), 0.12, 0.012, color=cor, transform=fig.transFigure))
        fig.text(0.08, 0.80, "PRESIDENTE EM GOIÁS · 2022 x 2026", fontsize=20, color=INK_2, fontweight="bold")
        fig.text(0.08, 0.50, numero, fontsize=118, fontweight="bold", color=INK, va="center")
        fig.text(0.08, 0.33, frase, fontsize=31, color=INK_2, va="top", linespacing=1.35)
        fig.text(0.08, 0.06, f"{i}/{len(cartoes)} · Fonte: TSE, 1º turno · github.com/JeffAirData",
                 fontsize=16, color=MUTED)
        fig.savefig(IMG_DIR / f"cartao_{i}.png", dpi=100)
        plt.close(fig)


def build_painel(mun: pd.DataFrame, geo) -> None:
    simples = geo.copy()
    simples["geometry"] = simples.geometry.simplify(0.01)
    simples["cd_municipio"] = simples["cd_municipio"].astype(int).astype(str)
    geojson = json.loads(simples[["cd_municipio", "geometry"]].to_json())
    dados = pd.DataFrame(simples.drop(columns="geometry"))
    dados["perda_pt"] = -dados["var_pt"]

    def mapa(div_id: str, coluna: str, escala: list[str], rotulo: str, **kwargs) -> str:
        fig = px.choropleth(dados, geojson=geojson, locations="cd_municipio", featureidkey="properties.cd_municipio",
                            color=coluna, color_continuous_scale=escala, hover_name="name_muni",
                            hover_data={"cd_municipio": False, coluna: ":.1f"}, labels={coluna: rotulo}, **kwargs)
        # limites fixos de Goiás: o fitbounds deixa o mapa pequeno dentro do quadro
        fig.update_geos(visible=False, bgcolor=SURFACE, projection_type="mercator",
                        lonaxis_range=[-53.4, -45.8], lataxis_range=[-19.7, -12.2],
                        domain={"x": [0, 1], "y": [0.14, 1]})
        fig.update_traces(marker_line_color="white", marker_line_width=0.4)
        # barra de cores horizontal embaixo: sobra largura para o mapa no celular
        fig.update_layout(margin={"r": 0, "l": 0, "t": 0, "b": 0}, autosize=True, paper_bgcolor=SURFACE,
                          font_family="Segoe UI, system-ui, sans-serif",
                          coloraxis_colorbar={"orientation": "h", "y": 0, "yanchor": "bottom", "len": 0.7,
                                              "thickness": 12, "title": {"side": "top"}})
        return fig.to_html(full_html=False, include_plotlyjs="cdn" if div_id == "mapa-pt" else False,
                           div_id=div_id, default_width="100%", default_height="100%",
                           config={"displayModeBar": False, "responsive": True, "scrollZoom": False})

    cidades = [
        {"cd": int(r.cd_municipio), "nome": r.name_muni, "aptos": int(r.aptos_2026),
         "pt22": round(r.pt_2022, 1), "pt26": round(r.pt_2026, 1), "pl22": round(r.pl_2022, 1),
         "pl26": round(r.pl_2026, 1), "caiado": round(r.caiado_2026, 1), "abst22": round(r.abstencao_2022, 1),
         "abst26": round(r.abstencao_2026, 1), "venc22": r.vencedor_2022, "venc26": r.vencedor_2026}
        for r in dados.sort_values("name_muni").itertuples()
    ]
    e22, e26 = estado(2022), estado(2026)
    resumo = {"pt22": round(e22[13], 1), "pt26": round(e26[13], 1), "pl22": round(e22[22], 1), "pl26": round(e26[22], 1),
              "var_pt": round(e26[13] - e22[13], 1), "var_pl": round(e26[22] - e22[22], 1)}

    html = (Path(__file__).parent / "painel_template.html").read_text(encoding="utf-8")
    partes = {
        "__DADOS__": json.dumps(cidades, ensure_ascii=False),
        "__ESTADO__": json.dumps(resumo),
        "__MAPA_PT__": mapa("mapa-pt", "perda_pt", ["#f6d5d5", "#e66767", "#a82c2c"], "Pontos perdidos"),
        "__MAPA_PL__": mapa("mapa-pl", "var_pl", ["#e34948", "#f0efec", "#2a78d6"], "Pontos a mais ou a menos",
                            color_continuous_midpoint=0),
        "__MAPA_CAIADO__": mapa("mapa-caiado", "caiado_2026", ["#fbeecb", "#eda100", "#8a5d00"], "De cada 100 votos"),
    }
    for marcador, valor in partes.items():
        html = html.replace(marcador, valor)
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
    chart_cartoes(mun)
    chart_painel(mun, geo)
    build_painel(mun, geo)
    print(f"Gráficos em {IMG_DIR} e painel em {DOCS_DIR / 'index.html'}")


if __name__ == "__main__":
    main()
