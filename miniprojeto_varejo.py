from pathlib import Path
import csv

import pandas as pd


# 1. Definição dos caminhos e configurações do projeto

PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_BASE = PASTA_PROJETO / "dados" / "Base Varejo.csv"

SEPARADOR_CSV = ";"


# 2. Leitura nativa com csv.DictReader

def ler_amostra_com_dictreader(caminho_csv: Path, quantidade_linhas: int = 3):

    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    linhas_amostra = []

    with caminho_csv.open(mode="r", encoding="utf-8", newline="") as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv, delimiter=SEPARADOR_CSV)

        colunas = leitor_csv.fieldnames

        for indice, linha in enumerate(leitor_csv):
            if indice >= quantidade_linhas:
                break

            linhas_amostra.append(linha)

    return colunas, linhas_amostra


def mostrar_amostra_dictreader(colunas, linhas_amostra) -> None:

    print("\n" + "=" * 60)
    print("LEITURA NATIVA COM csv.DictReader")
    print("=" * 60)

    print("\nColunas identificadas pelo csv.DictReader:")
    print(colunas)

    print("\nAmostra das primeiras linhas como dicionário:")

    for numero_linha, linha in enumerate(linhas_amostra, start=1):
        print(f"\nLinha {numero_linha}:")
        print(linha)



# 3. Leitura principal com pandas

def carregar_base_com_pandas(caminho_csv: Path) -> pd.DataFrame:

    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv, sep=SEPARADOR_CSV)

    return df


# 4. Exibição das informações iniciais da base

def mostrar_informacoes_iniciais(df: pd.DataFrame) -> None:

    print("\n" + "=" * 60)
    print("LEITURA PRINCIPAL COM pandas")
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



# 5. Execução principal do script

def main() -> None:

    colunas_dictreader, linhas_amostra = ler_amostra_com_dictreader(CAMINHO_BASE)
    mostrar_amostra_dictreader(colunas_dictreader, linhas_amostra)

    df_varejo = carregar_base_com_pandas(CAMINHO_BASE)
    mostrar_informacoes_iniciais(df_varejo)


if __name__ == "__main__":
    main()