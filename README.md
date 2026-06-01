# Mini-Projeto - Análise de Dados com Python

Projeto desenvolvido para a disciplina Análise de Dados com Python - Turma T1.

O objetivo deste projeto é realizar uma Análise Exploratória de Dados aplicada a uma base de varejo, identificando problemas de qualidade, tratando dados inconsistentes e gerando estatísticas e agrupamentos básicos.

## Estrutura inicial

- "dados/Base Varejo.csv": base original do projeto.
- "miniprojeto_varejo.py": script principal da análise.
- "saidas/": pasta reservada para arquivos gerados durante o projeto.

## Etapa atual

O projeto está na Sprint 4 - Estatística Descritiva.

Nesta etapa, foram geradas estatísticas descritivas da coluna `CL_FHL`, que representa o número de filhos do cliente.

As estatísticas calculadas foram:

- contagem;
- média;
- mediana;
- desvio padrão;
- moda;
- mínimo;
- primeiro quartil;
- segundo quartil;
- terceiro quartil;
- máximo.

Além da análise sobre a base limpa, também foi criada uma análise complementar por cliente único, evitando que clientes com muitas compras tenham peso repetido na estatística.


## Como executar

No terminal, rode:

```bash
python miniprojeto_varejo.py

#ou

py miniprojeto_varejo.py