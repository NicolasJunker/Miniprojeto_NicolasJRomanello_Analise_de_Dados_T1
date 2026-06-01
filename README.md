# Mini-Projeto - Análise de Dados com Python

Projeto desenvolvido para a disciplina Análise de Dados com Python - Turma T1.

O objetivo deste projeto é realizar uma Análise Exploratória de Dados aplicada a uma base de varejo, identificando problemas de qualidade, tratando dados inconsistentes e gerando estatísticas e agrupamentos básicos.

## Estrutura inicial

- "dados/Base Varejo.csv": base original do projeto.
- "miniprojeto_varejo.py": script principal da análise.
- "saidas/": pasta reservada para arquivos gerados durante o projeto.

## Etapa atual

O projeto está na Sprint 3 - Limpeza de Nulos e Duplicatas.

Nesta etapa, foram realizadas as seguintes ações:

- remoção de colunas totalmente vazias;
- identificação de valores nulos antes e depois da limpeza;
- tratamento de categorias vazias, nulas ou inválidas com o valor `Sem Categoria`;
- uso de condicionais `if/else` para tratar categorias inválidas;
- conversão da coluna de data usando o módulo `datetime`;
- remoção de duplicatas exatas;
- validação da regra de negócio do identificador de compra `CO_ID`.


## Como executar

No terminal, rode:

```bash
python miniprojeto_varejo.py

#ou

py miniprojeto_varejo.py