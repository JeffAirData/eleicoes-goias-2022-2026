# Perfil do eleitorado de Goiás: contexto territorial e demográfico

Este repositório reúne uma análise pública do perfil do eleitorado em Goiás, com foco em contexto territorial, distribuição municipal e composição demográfica. O objetivo é produzir uma leitura técnica e transparente do eleitorado do estado, com rigor metodológico e limites explícitos sobre o que os dados disponíveis permitem afirmar.

## Objetivo

- mapear a distribuição territorial do eleitorado em Goiás
- descrever padrões demográficos municipais
- comparar municípios por composição por sexo
- contextualizar o eleitorado em relação à estrutura territorial do estado
- gerar uma narrativa visual clara para GitHub e LinkedIn
- manter a análise rigorosa e transparente sobre as limitações dos dados

## Escopo do projeto

Este trabalho foi desenvolvido com base em dados públicos de perfil do eleitorado em nível municipal, agregados para permitir análise territorial e demográfica. O foco está no contexto do eleitorado e não na apuração oficial de votos por candidato.

A análise é útil para:

- entender a estrutura do eleitorado em diferentes municípios
- comparar padrões demográficos e territoriais
- gerar visualizações públicas e didáticas
- apoiar discussões técnicas sobre perfil eleitoral e contexto estadual

## Limites metodológicos

Este projeto não substitui a apuração oficial do TSE/TRE e não pretende afirmar comportamento eleitoral individual ou votos por candidato sem a base oficial correspondente.

A interpretação deve seguir esta regra:

- o material é uma análise de contexto eleitoral e demográfico
- não é um resultado oficial de eleições
- não inferimos voto individual a partir de dados agregados por município
- qualquer comparação com resultados oficiais deve ser feita com a base do TSE/TRE

> Legenda metodológica: esta análise explora o perfil do eleitorado em Goiás em nível municipal e territorial. A base utilizada foi o eleitorado agregado por municípios e não uma tabela oficial de votos por candidato. Portanto, o material deve ser lido como contexto eleitoral e demografia do eleitorado, e não como inferência individual de voto.

## O que está incluído

- base municipal de perfil do eleitorado
- agregação territorial por município
- indicadores de composição por sexo
- leitura demográfica e territorial do eleitorado
- dashboard visual interativo
- materiais de apoio para publicação em GitHub e LinkedIn

## O que não está incluído

- resultados oficiais de votação por candidato
- análise de preferências eleitorais por partido ou candidato
- inferência de voto individual
- substituição da base oficial do TSE/TRE

## Metodologia

A análise foi construída a partir de dados públicos e processados em ambiente local, seguindo uma abordagem de:

- limpeza e organização dos dados
- agregação por município
- validação de unidades territoriais
- contextualização demográfica e territorial
- geração de visualizações e dashboard

A transparência metodológica é parte central do projeto. O objetivo é reduzir ambiguidades e evitar extrapolações que não tenham suporte na base disponível.

## Estrutura do repositório

```text
.
├── Data/
│   ├── processed/
│   └── raw/
├── notebooks/
│   ├── 01_go_presidente_2022_2026.ipynb
│   ├── 02_goias_geospatial_analysis.ipynb
│   └── 03_presidente_goias_2022_2026.ipynb
├── src/
├── publicacao/
├── README.md
├── requirements.txt
├── .gitignore
└── .venv/
```

## Reprodutibilidade

Para reproduzir a análise, basta instalar as dependências e executar os notebooks em ordem:

1. preparação e agregação dos dados
2. análise geoespacial
3. dashboard final

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Saídas principais

- dashboard interativo em HTML
- visualizações de contexto territorial
- gráficos de composição demográfica
- materiais de divulgação para GitHub e LinkedIn

## Conclusão

Este projeto oferece uma visão pública, técnica e responsável sobre o perfil do eleitorado em Goiás, destacando sua estrutura territorial e demográfica. A intenção é produzir uma leitura útil para comunicação, visualização e pesquisa, mantendo um padrão rigoroso de transparência metodológica e limites analíticos.

## Observação final

A análise aqui apresentada deve ser interpretada como contexto eleitoral e demográfico, e não como resultado oficial de apuração. O objetivo central do projeto é a compreensão do eleitorado em seu cenário territorial e institucional, sempre com método explícito e cautela analítica.

## Licença

Este material foi desenvolvido para fins de análise, visualização e divulgação técnica. O uso público deve manter a transparência metodológica e a cautela quanto às limitações da base disponível.
