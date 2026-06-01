# Mini-Projeto - Análise de Dados com Python

Repositório: https://github.com/NicolasJunker/Miniprojeto_NicolasJRomanello_Analise_de_Dados_T1

Projeto desenvolvido para a disciplina **Análise de Dados com Python - Turma T1**.

O objetivo deste projeto é realizar uma Análise Exploratória de Dados aplicada a uma base de varejo, passando pelas etapas de importação, transformação, limpeza, estatística descritiva, agrupamentos e relatório final.

## Tecnologias utilizadas

- Python
- pandas
- csv
- re
- datetime
- Visual Studio Code
- Git e GitHub

## Estrutura do projeto

```text
Miniprojeto_NicolasJRomanello_Analise_de_Dados_T1/
│
├── dados/
│   └── Base Varejo.csv
│
├── saidas/
│   └── df_limpo.csv
│
├── .gitignore
├── miniprojeto_varejo.py
├── README.md
├── README_NicolasJRomanello_AnaliseDeDados_T1.md
└── requirements.txt

## Insights, soluções e observações de análise

Além dos resultados exibidos no terminal, a análise permite destacar alguns pontos importantes sobre a base de varejo:

### Insights principais

1. Após a limpeza, a base ficou com **733.447 registros** e **10 colunas úteis**.
2. Foram identificadas **18.471 compras únicas**, feitas por **1.000 clientes únicos**.
3. A categoria com maior volume de registros foi **ALIMENTOS**, com **384.197 itens registrados**.
4. O gênero com maior quantidade de compras únicas foi **F**, com **9.615 compras**.
5. O segmento com maior quantidade de compras únicas foi **B**, com **11.843 compras**.
6. O mês com maior volume de registros foi **2021-10**, com **28.575 registros**.

### Recomendações para a empresa

1. **Priorizar a categoria ALIMENTOS nas decisões comerciais.**  
   Como essa categoria concentra o maior volume de registros, ela pode ser tratada como uma área estratégica. A empresa pode acompanhar melhor estoque, reposição, sazonalidade e possíveis rupturas nessa categoria.

2. **Analisar o comportamento do segmento B com mais profundidade.**  
   O segmento B apresentou a maior quantidade de compras únicas. Isso indica que ele pode representar um grupo importante de clientes para ações de retenção, campanhas específicas e estudos de recorrência.

3. **Investigar o perfil de compra do público feminino.**  
   Como o gênero Femino aparece com maior quantidade de compras únicas, a empresa pode avaliar se campanhas, sortimento de produtos ou comunicações direcionadas para esse público podem gerar bons resultados.

4. **Usar os meses de maior volume como referência para planejamento.**  
   Meses de fim/início de ano tiveram o maior volume de registros. A empresa pode investigar se esse pico está ligado a sazonalidade, campanhas, datas comerciais ou aumento natural de demanda.

5. **Melhorar a qualidade do cadastro de produtos.**  
   A existência de categorias inválidas, como `#N/D`, mostra que o cadastro de produtos precisa de controle. Uma recomendação é criar validações obrigatórias para evitar produtos sem categoria definida.

6. **Manter uma rotina de tratamento de duplicatas.**  
   A remoção de duplicatas exatas foi necessária para reduzir ruído na análise. A empresa pode incluir validações no processo de entrada dos dados para evitar registros repetidos.


### Soluções aplicadas

- As colunas totalmente vazias foram removidas, pois não agregavam informação à análise.
- As categorias vazias ou inválidas, como `#N/D`, foram preenchidas com `Sem Categoria`.
- As duplicatas exatas foram removidas para reduzir ruído na base.
- A coluna `DATA` foi convertida usando o módulo `datetime`.
- A regra do identificador de compra `CO_ID` foi validada, considerando que uma mesma compra pode conter vários produtos.
- A base limpa foi salva em `saidas/df_limpo.csv`.

### Observações analíticas

A base não possui coluna de valor monetário. Por isso, a análise não calcula faturamento, ticket médio ou receita por categoria.

Os agrupamentos foram feitos com base em:

- volume de registros;
- quantidade de compras únicas;
- categorias;
- gênero dos clientes;
- segmentos;
- evolução mensal.