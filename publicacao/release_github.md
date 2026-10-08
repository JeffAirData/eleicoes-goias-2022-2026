# Perfil do eleitorado de Goiás: contexto territorial e demográfico

## Resumo executivo

Este projeto documenta uma análise exploratória do perfil do eleitorado em Goiás, com foco na composição demográfica municipal, distribuição territorial e concentração de eleitores em diferentes municípios do estado.

A base validada no ambiente foi o perfil do eleitorado por seção, agregada em nível municipal. A partir dela, foi possível mensurar proporções por sexo, identificar concentrações de eleitores em alguns municípios e mapear a distribuição territorial do eleitorado em Goiás.

## Objetivo

- descrever a estrutura do eleitorado em Goiás em nível municipal
- gerar uma leitura territorial e demográfica do eleitorado
- produzir um painel visual de apoio para apresentação pública
- manter uma narrativa técnica e honesta sobre as limitações analíticas

## O que foi analisado

- proporção de eleitores do sexo feminino e masculino por município
- concentração de eleitores em municípios de maior massa eleitoral
- distribuição por faixa etária jovem (16 a 29 anos)
- estrutura do eleitorado em painel visual interativo
- geografia municipal de Goiás para contextualização territorial

## O que não foi analisado

Este projeto não substitui a base oficial de votos por candidato. Não há inferência de voto individual nem afirmação de preferência eleitoral a partir do perfil municipal.

Em outras palavras:

- a análise é demográfica e territorial
- a inferência individual de voto exige a base oficial do TSE/TRE
- o material deve ser lido como contexto eleitoral, não como resultado oficial de eleição

## Metodologia

A análise foi realizada com base no eleitorado municipal validado em Goiás, já processado em formato Parquet. A estrutura de dados foi consolidada em nível municipal para permitir comparação entre municípios e construção do dashboard.

A transparência metodológica é parte essencial do projeto:

> Este projeto analisa o perfil do eleitorado em Goiás em nível municipal e territorial. A base utilizada foi o eleitorado por seção, agregada em nível municipal, e não uma tabela oficial de votos por candidato para presidente. Portanto, o material deve ser lido como análise exploratória de contexto eleitoral e estrutura demográfica, e não como inferência individual de voto. Qualquer comparação com os resultados oficiais exige a base do TSE/TRE.

## Limitações

- não há tabela oficial de votação por candidato no conjunto local validado
- não é possível afirmar voto individual a partir de dados agregados por município
- a correlação municipal é útil para contextualizar, mas não substitui a análise oficial de resultados eleitorais

## Produto final

O repositório inclui:

- notebook de exploração e preparação de dados
- notebook geoespacial para contexto territorial
- notebook final com dashboard público em HTML
- README de publicação
- materiais de apoio para GitHub e LinkedIn

## Saídas principais

- dashboard público em HTML
- painel temático em Plotly
- mapa geoespacial do perfil do eleitorado
- base municipal em formato parquet

## Próximos passos

1. incorporar a base oficial de votação por município/candidato do TSE/TRE
2. comparar estrutura demográfica com resultados oficiais
3. ampliar o painel para uma narrativa mais institucional
4. preparar versão final para publicação em redes sociais e apresentação técnica

## Conclusão

Este projeto oferece uma visão inicial e útil da composição do eleitorado em Goiás, com foco em estrutura territorial e demográfica. Ele é especialmente relevante para contexto, comunicação e visualização pública, mas exige cautela metodológica e transparência sobre as limitações da base.
