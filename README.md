# Perfil do eleitorado de Goiás e contexto eleitoral municipal

Este projeto reúne uma análise exploratória do perfil do eleitorado em Goiás, com foco na estrutura municipal do eleitorado, composição por sexo, faixa etária e concentração territorial. A base validada neste repositório é o perfil do eleitorado por seção, agregada em nível municipal.

## Objetivo

- mapear a distribuição territorial do eleitorado em Goiás
- descrever padrões demográficos municipais
- comparar municípios por composição de sexo e faixa etária
- gerar uma narrativa visual clara para GitHub e LinkedIn
- manter a análise rigorosa e transparente sobre as limitações dos dados

## O que a análise inclui

A base disponível neste workspace permite:

- localizar a distribuição do eleitorado por município
- comparar proporções de mulheres e homens por município
- observar a participação de faixas etárias jovens
- gerar mapas e painéis temáticos geoespaciais e municipais
- produzir uma leitura do contexto eleitoral no estado sem extrapolar conclusões individuais

## O que a análise não inclui

A base local validada aqui não substitui a tabela oficial do TSE/TRE com resultado por candidato para presidente em nível municipal. Portanto, o projeto não afirma preferência individual de eleitores nem conclui voto por candidato a partir do perfil do município.

A narrativa final do projeto deve manter claramente esta ressalva:

- esta é uma análise de contexto eleitoral e perfil do eleitorado
- não é uma análise oficial de votos por candidato
- qualquer inferência de voto individual exige a base oficial de resultados do TSE/TRE

## Público-alvo

- profissionais de ciência de dados
- analistas políticos e eleitorais
- público técnico em dados públicos
- comunidade de visualização e storytelling com dados

## Organização do repositório

```text
.
├── Data/
│   ├── 2022/                 # dados locais do ano de 2022
│   ├── 2026/                 # dados locais do ano de 2026
│   ├── processed/            # bases prontas para análise e dashboard
│   └── raw/                  # cópias originais mantidas em local seguro
├── notebooks/
│   ├── 01_go_presidente_2022_2026.ipynb
│   ├── 02_goias_geospatial_analysis.ipynb
│   └── 03_presidente_goias_2022_2026.ipynb
├── src/
├── README.md
├── requirements.txt
├── .gitignore
└── .venv/
```

## Dados e metodologia

### Fonte local validada

A base realmente confiável e disponível neste workspace para a análise exploratória é a base de perfil do eleitorado por seção de Goiás, já processada em formato Parquet.

### Limitação metodológica

A análise por município pode revelar padrões territoriais e demográficos, mas não permite inferir o voto individual de cada eleitor. Isso é a falácia ecológica.

Em linguagem simples:

- um município com maior proporção feminina não significa que cada mulher votou em certo candidato
- um município com maior proporção de eleitores jovens não implica comportamento individual uniforme
- correlações municipais são úteis para descrever contextos, não para afirmar comportamento individual

## Como reproduzir

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Em seguida, execute os notebooks em ordem:

1. 01_go_presidente_2022_2026.ipynb
2. 02_goias_geospatial_analysis.ipynb
3. 03_presidente_goias_2022_2026.ipynb

## Saídas principais

- dashboard municipal em HTML
- mapa geoespacial do perfil do eleitorado
- gráficos de composição por sexo e juventude
- base municipal agregada em Parquet

## Legenda metodológica para publicação

> Este projeto analisa o perfil do eleitorado de Goiás em nível municipal e territorial. A base utilizada foi o eleitorado por seção, agregada municipalmente, e não uma tabela oficial de votos por candidato para presidente. Portanto, o material deve ser lido como análise exploratória de contexto eleitoral e estrutura demográfica, e não como inferência individual de voto. A comparação com resultados eleitorais oficiais exige a base do TSE/TRE.

## Próximos passos

1. incorporar a base oficial de votação por município/candidato do TSE/TRE
2. comparar a distribuição demográfica com os resultados oficiais
3. expandir o painel para visualizações interativas de maior impacto
4. preparar comunicado para GitHub e LinkedIn com foco no contexto e na metodologia

## Licença

Este material foi desenvolvido para fins de análise, visualização e divulgação técnica. O uso público deve manter a transparência metodológica e a cautela quanto às limitações da base disponível.
