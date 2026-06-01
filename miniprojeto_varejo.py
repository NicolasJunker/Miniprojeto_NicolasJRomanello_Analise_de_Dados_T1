from pathlib import Path
from datetime import datetime
import csv
import re

import pandas as pd


# ------------------------------------------------------------
# 1. Definição dos caminhos e configurações do projeto
# ------------------------------------------------------------

PASTA_PROJETO = Path(__file__).resolve().parent
CAMINHO_BASE = PASTA_PROJETO / "dados" / "Base Varejo.csv"

SEPARADOR_CSV = ";"


# ------------------------------------------------------------
# 2. Expressões regulares usadas nas transformações
# ------------------------------------------------------------

PADRAO_ESPACOS = re.compile(r"\s+")
PADRAO_CARACTERES_COLUNA = re.compile(r"[^A-Z0-9_]+")
PADRAO_INTEIRO = re.compile(r"[^0-9-]")
PADRAO_DECIMAL = re.compile(r"[^0-9,.\-]")


# ------------------------------------------------------------
# 3. Leitura nativa com csv.DictReader
# ------------------------------------------------------------

def ler_amostra_com_dictreader(caminho_csv: Path, quantidade_linhas: int = 3):
    """
    Lê uma pequena amostra do arquivo CSV usando csv.DictReader.
    """

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
    """
    Exibe no terminal uma pequena amostra lida com csv.DictReader.
    """

    print("\n" + "=" * 60)
    print("LEITURA NATIVA COM csv.DictReader")
    print("=" * 60)

    print("\nColunas identificadas:")
    print(colunas)

    print("\nAmostra das primeiras linhas como dicionário:")

    for numero_linha, linha in enumerate(linhas_amostra, start=1):
        print(f"\nLinha {numero_linha}:")
        print(linha)


# ------------------------------------------------------------
# 4. Leitura principal com pandas
# ------------------------------------------------------------

def carregar_base_com_pandas(caminho_csv: Path) -> pd.DataFrame:
    """
    Carrega a base de varejo usando pandas.
    """

    if not caminho_csv.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    df = pd.read_csv(caminho_csv, sep=SEPARADOR_CSV)

    return df


# ------------------------------------------------------------
# 5. Funções de transformação de strings, números e datas
# ------------------------------------------------------------

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

    Mantém nulos como nulos, remove espaços desnecessários
    e padroniza textos em letras maiúsculas.
    """

    if pd.isna(valor):
        return valor

    texto = str(valor).strip()
    texto = PADRAO_ESPACOS.sub(" ", texto)
    texto = texto.upper()

    return texto


def converter_inteiro(valor):
    """
    Converte valores para número inteiro.
    Caso não consiga converter, retorna pd.NA.
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


def converter_decimal(valor):
    """
    Converte valores para número decimal.
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


def converter_data_com_datetime(valor):
    """
    Converte uma string de data para datetime usando o módulo datetime.
    """

    if pd.isna(valor):
        return pd.NaT

    texto = str(valor).strip()

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


# ------------------------------------------------------------
# 6. Funções de limpeza de nulos, categorias e duplicatas
# ------------------------------------------------------------

def remover_colunas_totalmente_vazias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove colunas que não possuem nenhum valor preenchido.
    """

    df_limpo = df.copy()

    colunas_antes = df_limpo.shape[1]
    df_limpo = df_limpo.dropna(axis=1, how="all")
    colunas_depois = df_limpo.shape[1]

    print("\n" + "=" * 60)
    print("REMOÇÃO DE COLUNAS TOTALMENTE VAZIAS")
    print("=" * 60)
    print(f"Colunas antes: {colunas_antes}")
    print(f"Colunas depois: {colunas_depois}")
    print(f"Colunas removidas: {colunas_antes - colunas_depois}")

    return df_limpo


def valor_categoria_vazio_ou_invalido(valor) -> bool:
    """
    Verifica se uma categoria está vazia ou inválida.
    """

    if pd.isna(valor):
        return True
    else:
        texto = str(valor).strip().upper()

        if texto == "":
            return True
        elif texto == "#N/D":
            return True
        elif texto == "NAN":
            return True
        elif texto == "NULL":
            return True
        elif texto == "NONE":
            return True
        else:
            return False


def tratar_categoria(valor) -> str:
    """
    Preenche categorias vazias ou inválidas com 'Sem Categoria'.
    """

    if valor_categoria_vazio_ou_invalido(valor):
        return "Sem Categoria"
    else:
        return limpar_texto(valor)


def tratar_coluna_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica o tratamento de categorias na coluna PR_CAT.
    """

    df_limpo = df.copy()

    if "PR_CAT" in df_limpo.columns:
        problemas_antes = df_limpo["PR_CAT"].apply(valor_categoria_vazio_ou_invalido).sum()

        df_limpo["PR_CAT"] = df_limpo["PR_CAT"].apply(tratar_categoria)

        problemas_depois = df_limpo["PR_CAT"].apply(valor_categoria_vazio_ou_invalido).sum()

        print("\n" + "=" * 60)
        print("TRATAMENTO DA COLUNA DE CATEGORIA")
        print("=" * 60)
        print(f"Categorias vazias ou inválidas antes: {problemas_antes}")
        print(f"Categorias vazias ou inválidas depois: {problemas_depois}")
        print("Valor usado para preenchimento: Sem Categoria")
    else:
        print("\nColuna PR_CAT não encontrada na base.")

    return df_limpo


def relatorio_nulos(df: pd.DataFrame, titulo: str) -> None:
    """
    Exibe a quantidade de valores nulos por coluna.
    """

    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)

    nulos_por_coluna = df.isna().sum()
    print(nulos_por_coluna[nulos_por_coluna > 0])

    if nulos_por_coluna.sum() == 0:
        print("Nenhum valor nulo encontrado.")


def remover_duplicatas_exatas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicatas exatas da base.

    Não removemos linhas apenas por repetirem CO_ID, porque uma compra
    pode possuir vários produtos. Por isso, a remoção é feita apenas
    quando a linha inteira é duplicada.
    """

    df_limpo = df.copy()

    linhas_antes = df_limpo.shape[0]
    duplicatas_antes = df_limpo.duplicated().sum()

    df_limpo = df_limpo.drop_duplicates()

    linhas_depois = df_limpo.shape[0]
    duplicatas_depois = df_limpo.duplicated().sum()

    print("\n" + "=" * 60)
    print("REMOÇÃO DE DUPLICATAS EXATAS")
    print("=" * 60)
    print(f"Linhas antes: {linhas_antes}")
    print(f"Duplicatas exatas encontradas: {duplicatas_antes}")
    print(f"Linhas depois: {linhas_depois}")
    print(f"Duplicatas exatas restantes: {duplicatas_depois}")

    return df_limpo


# ------------------------------------------------------------
# 7. Funções de transformação aplicadas à base
# ------------------------------------------------------------

def transformar_colunas_texto(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica limpeza de texto em todas as colunas textuais da base.
    """

    df_transformado = df.copy()

    colunas_texto = df_transformado.select_dtypes(include="object").columns

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
    Aplica transformações iniciais:

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
        df_transformado["DATA"] = df_transformado["DATA"].apply(converter_data_com_datetime)

    return df_transformado


def limpar_base_varejo(df: pd.DataFrame) -> pd.DataFrame:
    """
    Executa a limpeza principal da Sprint 3.

    Nesta função entram:
    - remoção de colunas vazias;
    - tratamento de categoria vazia;
    - tratamento de nulos em dimensões físicas, se existirem;
    - remoção de duplicatas exatas.
    """

    df_limpo = df.copy()

    relatorio_nulos(df_limpo, "NULOS ANTES DA LIMPEZA")

    df_limpo = remover_colunas_totalmente_vazias(df_limpo)
    df_limpo = tratar_coluna_categoria(df_limpo)
    df_limpo = remover_duplicatas_exatas(df_limpo)

    relatorio_nulos(df_limpo, "NULOS APÓS A LIMPEZA")

    return df_limpo


# ------------------------------------------------------------
# 8. Validação da regra de negócio do identificador de compra
# ------------------------------------------------------------

def validar_identificador_compra(df: pd.DataFrame) -> None:
    """
    Valida a regra do identificador de compra.

    Regra considerada:
    Uma compra, identificada por CO_ID, pode aparecer em várias linhas,
    pois uma compra pode conter vários produtos.

    Porém, o mesmo CO_ID não deveria misturar informações principais
    diferentes, como cliente, data, gênero, estado civil, filhos ou segmento.
    """

    print("\n" + "=" * 60)
    print("VALIDAÇÃO DA REGRA DE NEGÓCIO DO CO_ID")
    print("=" * 60)

    if "CO_ID" not in df.columns:
        print("Coluna CO_ID não encontrada. Validação não realizada.")
        return

    colunas_para_validar = [
        "DATA",
        "CL_ID",
        "CL_GENERO",
        "CL_EC",
        "CL_FHL",
        "CL_SEG",
    ]

    colunas_existentes = [
        coluna
        for coluna in colunas_para_validar
        if coluna in df.columns
    ]

    if len(colunas_existentes) == 0:
        print("Não há colunas suficientes para validar o CO_ID.")
        return

    variacoes_por_compra = df.groupby("CO_ID")[colunas_existentes].nunique(dropna=False)
    compras_inconsistentes = variacoes_por_compra[
        (variacoes_por_compra > 1).any(axis=1)
    ]

    total_compras = df["CO_ID"].nunique()
    total_inconsistentes = compras_inconsistentes.shape[0]

    print(f"Total de compras únicas analisadas: {total_compras}")
    print(f"Compras com inconsistência cadastral: {total_inconsistentes}")

    if total_inconsistentes == 0:
        print(
            "Regra validada: os identificadores de compra não misturam "
            "cliente, data ou dados cadastrais principais."
        )
    else:
        print("Atenção: foram encontradas compras com informações divergentes.")
        print(compras_inconsistentes.head())


# ------------------------------------------------------------
# 9. Exibição das informações da base
# ------------------------------------------------------------

def mostrar_informacoes_iniciais(df: pd.DataFrame) -> None:
    """
    Exibe informações básicas sobre a base de dados carregada.
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


def mostrar_resultado_sprint3(df_original: pd.DataFrame, df_limpo: pd.DataFrame) -> None:
    """
    Mostra resumo final da Sprint 3.
    """

    print("\n" + "=" * 60)
    print("RESUMO FINAL DA SPRINT 3")
    print("=" * 60)

    print(f"Linhas originais: {df_original.shape[0]}")
    print(f"Colunas originais: {df_original.shape[1]}")
    print(f"Linhas após limpeza: {df_limpo.shape[0]}")
    print(f"Colunas após limpeza: {df_limpo.shape[1]}")

    if "DATA" in df_limpo.columns:
        print("\nTipo final da coluna DATA:")
        print(df_limpo["DATA"].dtype)

        datas_invalidas = df_limpo["DATA"].isna().sum()
        print(f"Datas inválidas ou não convertidas: {datas_invalidas}")

    print("\nPrimeiras 5 linhas da base limpa:")
    print(df_limpo.head())


# ------------------------------------------------------------
# 10. Execução principal do script
# ------------------------------------------------------------

def main() -> None:
    """
    Função principal do projeto.

    Sprint 3:
    - remove colunas totalmente vazias;
    - trata categorias vazias com 'Sem Categoria';
    - verifica nulos;
    - remove duplicatas exatas;
    - converte DATA usando datetime;
    - valida regra de negócio do CO_ID.
    """

    colunas_dictreader, linhas_amostra = ler_amostra_com_dictreader(CAMINHO_BASE)
    mostrar_amostra_dictreader(colunas_dictreader, linhas_amostra)

    df_varejo = carregar_base_com_pandas(CAMINHO_BASE)
    mostrar_informacoes_iniciais(df_varejo)

    df_transformado = aplicar_transformacoes_iniciais(df_varejo)
    df_limpo = limpar_base_varejo(df_transformado)

    validar_identificador_compra(df_limpo)
    mostrar_resultado_sprint3(df_varejo, df_limpo)


if __name__ == "__main__":
    main()