from pathlib import Path

import pandas as pd


# 1. Definição dos caminhos do projeto

PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_BASE = PASTA_PROJETO / "dados" / "Base Varejo.csv"



# 2. Função para carregar a base de dados

def carregar_base(caminho_csv: Path) -> pd.DataFrame:

    if not caminho_csv.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho_csv}"
        )

    df = pd.read_csv(caminho_csv, sep=";")

    return df



# 3. Função para exibir informações iniciais da base

def mostrar_informacoes_iniciais(df: pd.DataFrame) -> None:

    print("\n" + "=" * 60)
    print("ANÁLISE EXPLORATÓRIA DE DADOS - BASE VAREJO")
    print("=" * 60)

    print("\n1. Quantidade de registros e colunas:")
    print(f"Registros: {df.shape[0]}")
    print(f"Colunas: {df.shape[1]}")

    print("\n2. Nomes das colunas:")
    print(df.columns.tolist())

    print("\n3. Tipos de dados:")
    print(df.dtypes)

    print("\n4. Primeiras 5 linhas da base:")
    print(df.head())


# 4. Execução principal do script

def main() -> None:

    df_varejo = carregar_base(CAMINHO_BASE)
    mostrar_informacoes_iniciais(df_varejo)


if __name__ == "__main__":
    main()