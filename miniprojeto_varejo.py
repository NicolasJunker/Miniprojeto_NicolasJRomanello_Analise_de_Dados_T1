from pathlib import Path
from datetime import datetime
import csv
import re

import pandas as pd



# 1. Definição dos caminhos e configurações do projeto

PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_BASE = PASTA_PROJETO / "dados" / "Base Varejo.csv"

SEPARADOR_CSV = ";"



# 2. Expressões regulares usadas nas transformações

PADRAO_ESPACOS = re.compile(r"\s+")
PADRAO_CARACTERES_COLUNA = re.compile(r"[^A-Z0-9_]+")
PADRAO_INTEIRO = re.compile(r"[^0-9-]")
PADRAO_DECIMAL = re.compile(r"[^0-9,.\-]")



# 3. Leitura nativa com csv.DictReader

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

    print("\nColunas identificadas:")
    print(colunas)

    print("\nAmostra das primeiras linhas como dicionário:")

    for numero_linha, linha in enumerate(linhas_amostra, start=1):
        print(f"\nLinha {numero_linha}:")
        print(linha)



# 4. Leitura principal com pandas

def carregar_base_com_pandas(caminho_csv: Path) -> pd.DataFrame:

    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv, sep=SEPARADOR_CSV)

    return df



# 5. Funções de transformação de strings

def limpar_nome_coluna(nome_coluna) -> str:
    """
    Padroniza nomes de colunas.
    """

    texto = str(nome_coluna).strip().upper()
    texto = PADRAO_ESPACOS.sub("_", texto)
    texto = texto.replace(":", "_")
    texto = PADRAO_CARACTERES_COLUNA.sub("", texto)
    texto = re.sub(r"_+", "_", texto)
    texto = texto.strip("_")

    return texto


def limpar_texto(valor):
    """
    Limpa valores de texto.

    A função:
    - mantém nulos como estão;
    - remove espaços no início e no fim;
    - troca vários espaços seguidos por apenas um;
    - padroniza o texto em letras maiúsculas.
    """

    if pd.isna(valor):
        return valor

    texto = str(valor).strip()
    texto = PADRAO_ESPACOS.sub(" ", texto)
    texto = texto.upper()

    return texto



# 6. Funções de transformação de números inteiros

def converter_inteiro(valor):
    """
    Converte valores para número inteiro.
    Caso o valor não possa ser convertido, retorna pd.NA.
    """

    if pd.isna(valor):
        return pd.NA

    if isinstance(valor, int):
        return valor

    if isinstance(valor, float):
        return int(valor)

    texto = limpar_texto(valor)

    if texto == "":
        return pd.NA

    try:
        return int(float(texto.replace(",", ".")))
    except ValueError:
        texto_numerico = PADRAO_INTEIRO.sub("", texto)

        if texto_numerico in ["", "-"]:
            return pd.NA

        try:
            return int(texto_numerico)
        except ValueError:
            return pd.NA



# 7. Função de transformação de números decimais

def converter_decimal(valor):
    """
    Converte valores para número decimal.

    Caso o valor não possa ser convertido, retorna pd.NA.
    """

    if pd.isna(valor):
        return pd.NA

    if isinstance(valor, int) or isinstance(valor, float):
        return float(valor)

    texto = limpar_texto(valor)

    if texto == "":
        return pd.NA

    texto = PADRAO_DECIMAL.sub("", texto)

    if texto == "":
        return pd.NA

    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "")
            texto = texto.replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif "," in texto:
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return pd.NA



# 8. Função de transformação de datas com datetime

def converter_data_com_datetime(valor):
    """
    Converte uma string de data para datetime usando o módulo datetime.
    """

    if pd.isna(valor):
        return pd.NaT

    texto = limpar_texto(valor)

    if texto == "":
        return pd.NaT

    formatos_possiveis = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
    ]

    for formato in formatos_possiveis:
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue

    return pd.NaT



# 9. Aplicação das transformações iniciais

def transformar_colunas_texto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza de texto em todas as colunas textuais da base.
    """

    df_transformado = df.copy()

    colunas_texto = [
        coluna
        for coluna in df_transformado.columns
        if df_transformado[coluna].dtype.name in ["object", "string", "str"]
    ]

    for coluna in colunas_texto:
        df_transformado[coluna] = df_transformado[coluna].apply(limpar_texto)

    return df_transformado


def transformar_colunas_inteiras(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte colunas esperadas como inteiras.
    """

    df_transformado = df.copy()

    colunas_inteiras = [
        "CO_ID",
        "CL_ID",
        "CL_EC",
        "CL_FHL",
        "PR_ID",
    ]

    for coluna in colunas_inteiras:
        if coluna in df_transformado.columns:
            df_transformado[coluna] = (
                df_transformado[coluna]
                .apply(converter_inteiro)
                .astype("Int64")
            )

    return df_transformado


def aplicar_transformacoes_iniciais(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica as transformações
    - padronização dos nomes das colunas;
    - limpeza de textos;
    - conversão de inteiros;
    - conversão da coluna DATA usando datetime.
    """

    df_transformado = df.copy()

    df_transformado.columns = [
        limpar_nome_coluna(coluna)
        for coluna in df_transformado.columns
    ]

    df_transformado = transformar_colunas_texto(df_transformado)
    df_transformado = transformar_colunas_inteiras(df_transformado)

    if "DATA" in df_transformado.columns:
        df_transformado["DATA_CONVERTIDA"] = (
            df_transformado["DATA"].apply(converter_data_com_datetime)
        )

    return df_transformado



# 10. Exibição das informações iniciais da base

def mostrar_informacoes_iniciais(df: pd.DataFrame) -> None:
    """
    Exibe informações básicas sobre a base de dados carregada com pandas.
    """

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


def mostrar_teste_funcoes_transformacao() -> None:
    """
    Mostra pequenos exemplos das funções criadas na Sprint 2.
    """

    print("\n" + "=" * 60)
    print("TESTE DAS FUNÇÕES DE TRANSFORMAÇÃO")
    print("=" * 60)

    exemplos_texto = ["  bebidas  ", "REFRIGERANTE   GUARANA", "", "#N/D"]
    exemplos_inteiro = ["123", " 45 ", "ABC123", ""]
    exemplos_decimal = ["1234.56", "1234,56", "1.234,56", "R$ 89,90", ""]
    exemplos_data = ["01/02/2019", "2019-02-01", "31-12-2020", "data errada"]

    print("\nExemplos de limpeza de texto:")
    for valor in exemplos_texto:
        print(f"{valor!r} -> {limpar_texto(valor)!r}")

    print("\nExemplos de conversão para inteiro:")
    for valor in exemplos_inteiro:
        print(f"{valor!r} -> {converter_inteiro(valor)!r}")

    print("\nExemplos de conversão para decimal:")
    for valor in exemplos_decimal:
        print(f"{valor!r} -> {converter_decimal(valor)!r}")

    print("\nExemplos de conversão de data com datetime:")
    for valor in exemplos_data:
        print(f"{valor!r} -> {converter_data_com_datetime(valor)!r}")


def mostrar_resultado_transformacoes(
    df_original: pd.DataFrame,
    df_transformado: pd.DataFrame
) -> None:
    """
    Exibe o resultado das transformações iniciais.
    """

    print("\n" + "=" * 60)
    print("RESULTADO DAS TRANSFORMAÇÕES DA SPRINT 2")
    print("=" * 60)

    print("\n1. Colunas originais:")
    print(df_original.columns.tolist())

    print("\n2. Colunas após padronização:")
    print(df_transformado.columns.tolist())

    print("\n3. Tipos de dados após transformações:")
    print(df_transformado.dtypes)

    if "DATA" in df_transformado.columns and "DATA_CONVERTIDA" in df_transformado.columns:
        print("\n4. Comparação entre DATA original e DATA_CONVERTIDA:")
        print(df_transformado[["DATA", "DATA_CONVERTIDA"]].head())

        datas_invalidas = df_transformado["DATA_CONVERTIDA"].isna().sum()
        print(f"\nDatas inválidas encontradas: {datas_invalidas}")

    print("\n5. Primeiras 5 linhas após transformações:")
    print(df_transformado.head())



# 11. Execução principal do script

def main() -> None:

    colunas_dictreader, linhas_amostra = ler_amostra_com_dictreader(CAMINHO_BASE)
    mostrar_amostra_dictreader(colunas_dictreader, linhas_amostra)

    df_varejo = carregar_base_com_pandas(CAMINHO_BASE)
    mostrar_informacoes_iniciais(df_varejo)

    mostrar_teste_funcoes_transformacao()

    df_transformado = aplicar_transformacoes_iniciais(df_varejo)
    mostrar_resultado_transformacoes(df_varejo, df_transformado)


if __name__ == "__main__":
    main()