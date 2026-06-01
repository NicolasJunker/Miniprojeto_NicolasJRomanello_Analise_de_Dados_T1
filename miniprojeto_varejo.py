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

PASTA_SAIDAS = PASTA_PROJETO / "saidas"
CAMINHO_DF_LIMPO = PASTA_SAIDAS / "df_limpo.csv"

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
    Aplica limpeza de texto em colunas textuais da base.
    """

    df_transformado = df.copy()

    colunas_texto = [
        coluna
        for coluna in df_transformado.columns
        if df_transformado[coluna].dtype == "object"
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
# 10. Estatística descritiva da coluna Número de Filhos
# ------------------------------------------------------------

def formatar_numero(valor) -> str:
    """
    Formata números para exibição no terminal.
    """

    if pd.isna(valor):
        return "Não calculado"

    return f"{float(valor):.2f}".replace(".", ",")


def formatar_moda(lista_moda) -> str:
    """
    Formata a moda para exibição.
    A moda pode ter um único valor ou vários valores.
    """

    if len(lista_moda) == 0:
        return "Sem moda"

    valores_formatados = []

    for valor in lista_moda:
        if float(valor).is_integer():
            valores_formatados.append(str(int(valor)))
        else:
            valores_formatados.append(formatar_numero(valor))

    return ", ".join(valores_formatados)


def gerar_estatisticas_filhos(
    df: pd.DataFrame,
    titulo: str,
    coluna_filhos: str = "CL_FHL"
) -> dict:
    """
    Gera estatísticas descritivas da coluna de número de filhos.

    Estatísticas calculadas:
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
    """

    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)

    if coluna_filhos not in df.columns:
        print(f"Coluna {coluna_filhos} não encontrada.")
        return {}

    serie_filhos = pd.to_numeric(df[coluna_filhos], errors="coerce").dropna()

    if serie_filhos.empty:
        print(f"A coluna {coluna_filhos} não possui valores válidos.")
        return {}

    moda = serie_filhos.mode().tolist()

    estatisticas = {
        "contagem": int(serie_filhos.count()),
        "media": serie_filhos.mean(),
        "mediana": serie_filhos.median(),
        "desvio_padrao": serie_filhos.std(),
        "moda": moda,
        "minimo": serie_filhos.min(),
        "quartil_1": serie_filhos.quantile(0.25),
        "quartil_2": serie_filhos.quantile(0.50),
        "quartil_3": serie_filhos.quantile(0.75),
        "maximo": serie_filhos.max(),
    }

    print(f"Coluna analisada: {coluna_filhos}")
    print(f"Contagem: {estatisticas['contagem']}")
    print(f"Média: {formatar_numero(estatisticas['media'])}")
    print(f"Mediana: {formatar_numero(estatisticas['mediana'])}")
    print(f"Desvio padrão: {formatar_numero(estatisticas['desvio_padrao'])}")
    print(f"Moda: {formatar_moda(estatisticas['moda'])}")
    print(f"Mínimo: {formatar_numero(estatisticas['minimo'])}")
    print(f"1º quartil: {formatar_numero(estatisticas['quartil_1'])}")
    print(f"2º quartil: {formatar_numero(estatisticas['quartil_2'])}")
    print(f"3º quartil: {formatar_numero(estatisticas['quartil_3'])}")
    print(f"Máximo: {formatar_numero(estatisticas['maximo'])}")

    return estatisticas


def gerar_estatisticas_filhos_cliente_unico(df: pd.DataFrame) -> dict:
    """
    Gera estatísticas da coluna CL_FHL considerando cada cliente apenas uma vez.
    Essa análise é complementar. Ela evita que um cliente com muitas compras
    pese várias vezes na estatística.
    """

    if "CL_ID" not in df.columns:
        print("\nColuna CL_ID não encontrada. Estatística por cliente único não realizada.")
        return {}

    df_clientes_unicos = df.drop_duplicates(subset=["CL_ID"])

    return gerar_estatisticas_filhos(
        df=df_clientes_unicos,
        titulo="ESTATÍSTICA DESCRITIVA DE CL_FHL POR CLIENTE ÚNICO"
    )

# ------------------------------------------------------------
# 11. Agrupamentos, relatório final e conclusões
# ------------------------------------------------------------

def formatar_inteiro(valor) -> str:
    """
    Formata números inteiros para exibição no terminal.
    """

    return f"{int(valor):,}".replace(",", ".")


def formatar_data(valor) -> str:
    """
    Formata datas para o padrão brasileiro.
    """

    if pd.isna(valor):
        return "Não encontrada"

    return valor.strftime("%d/%m/%Y")


def mostrar_ranking(titulo: str, serie: pd.Series, limite: int = 10) -> None:
    """
    Exibe rankings simples no terminal.
    """

    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)

    if serie.empty:
        print("Nenhum dado encontrado.")
        return

    print(serie.head(limite))


def gerar_agrupamentos(df: pd.DataFrame) -> dict:
    """
    Explora padrões de agrupamento na base limpa.

    Agrupamentos gerados:
    - itens por gênero;
    - compras únicas por gênero;
    - itens por categoria;
    - compras únicas por categoria;
    - itens por segmento;
    - compras únicas por segmento;
    - registros por mês.
    """

    print("\n" + "=" * 60)
    print("AGRUPAMENTOS DA BASE LIMPA")
    print("=" * 60)

    agrupamentos = {}

    if "CL_GENERO" in df.columns:
        itens_por_genero = df.groupby("CL_GENERO").size().sort_values(ascending=False)
        compras_por_genero = (
            df.drop_duplicates(subset=["CO_ID"])
            .groupby("CL_GENERO")
            .size()
            .sort_values(ascending=False)
        )

        agrupamentos["itens_por_genero"] = itens_por_genero
        agrupamentos["compras_por_genero"] = compras_por_genero

        mostrar_ranking("ITENS POR GÊNERO", itens_por_genero)
        mostrar_ranking("COMPRAS ÚNICAS POR GÊNERO", compras_por_genero)

    if "PR_CAT" in df.columns:
        itens_por_categoria = df.groupby("PR_CAT").size().sort_values(ascending=False)
        compras_por_categoria = (
            df.groupby("PR_CAT")["CO_ID"]
            .nunique()
            .sort_values(ascending=False)
        )

        agrupamentos["itens_por_categoria"] = itens_por_categoria
        agrupamentos["compras_por_categoria"] = compras_por_categoria

        mostrar_ranking("ITENS POR CATEGORIA", itens_por_categoria)
        mostrar_ranking("COMPRAS ÚNICAS POR CATEGORIA", compras_por_categoria)

    if "CL_SEG" in df.columns:
        itens_por_segmento = df.groupby("CL_SEG").size().sort_values(ascending=False)
        compras_por_segmento = (
            df.drop_duplicates(subset=["CO_ID"])
            .groupby("CL_SEG")
            .size()
            .sort_values(ascending=False)
        )

        agrupamentos["itens_por_segmento"] = itens_por_segmento
        agrupamentos["compras_por_segmento"] = compras_por_segmento

        mostrar_ranking("ITENS POR SEGMENTO", itens_por_segmento)
        mostrar_ranking("COMPRAS ÚNICAS POR SEGMENTO", compras_por_segmento)

    if "DATA" in df.columns:
        df_com_mes = df.copy()
        df_com_mes["ANO_MES"] = df_com_mes["DATA"].dt.to_period("M").astype(str)

        registros_por_mes = (
            df_com_mes.groupby("ANO_MES")
            .size()
            .sort_values(ascending=False)
        )

        agrupamentos["registros_por_mes"] = registros_por_mes

        mostrar_ranking("MESES COM MAIOR VOLUME DE REGISTROS", registros_por_mes)

    return agrupamentos


def obter_primeiro_indice(serie: pd.Series):
    """
    Retorna o primeiro índice de uma Series ordenada.
    """

    if serie.empty:
        return "Não encontrado"

    return serie.index[0]


def obter_primeiro_valor(serie: pd.Series):
    """
    Retorna o primeiro valor de uma Series ordenada.
    """

    if serie.empty:
        return 0

    return serie.iloc[0]


def gerar_conclusoes(df: pd.DataFrame, agrupamentos: dict) -> list:
    """
    Gera conclusões automáticas com base nos agrupamentos.
    """

    conclusoes = []

    total_linhas = df.shape[0]
    total_colunas = df.shape[1]

    conclusoes.append(
        f"Após a limpeza, a base ficou com {formatar_inteiro(total_linhas)} "
        f"registros e {total_colunas} colunas úteis."
    )

    if "CO_ID" in df.columns:
        total_compras = df["CO_ID"].nunique()
        conclusoes.append(
            f"Foram identificadas {formatar_inteiro(total_compras)} "
            "compras únicas na base limpa."
        )

    if "CL_ID" in df.columns:
        total_clientes = df["CL_ID"].nunique()
        conclusoes.append(
            f"A base possui {formatar_inteiro(total_clientes)} clientes únicos."
        )

    if "itens_por_categoria" in agrupamentos:
        categoria_top = obter_primeiro_indice(agrupamentos["itens_por_categoria"])
        qtd_categoria_top = obter_primeiro_valor(agrupamentos["itens_por_categoria"])

        conclusoes.append(
            f"A categoria com maior volume de registros foi {categoria_top}, "
            f"com {formatar_inteiro(qtd_categoria_top)} itens registrados."
        )

    if "compras_por_genero" in agrupamentos:
        genero_top = obter_primeiro_indice(agrupamentos["compras_por_genero"])
        qtd_genero_top = obter_primeiro_valor(agrupamentos["compras_por_genero"])

        conclusoes.append(
            f"O gênero com maior quantidade de compras únicas foi {genero_top}, "
            f"com {formatar_inteiro(qtd_genero_top)} compras."
        )

    if "compras_por_segmento" in agrupamentos:
        segmento_top = obter_primeiro_indice(agrupamentos["compras_por_segmento"])
        qtd_segmento_top = obter_primeiro_valor(agrupamentos["compras_por_segmento"])

        conclusoes.append(
            f"O segmento com maior quantidade de compras únicas foi {segmento_top}, "
            f"com {formatar_inteiro(qtd_segmento_top)} compras."
        )

    return conclusoes[:6]


def gerar_relatorio_final(
    df_original: pd.DataFrame,
    df_limpo: pd.DataFrame,
    agrupamentos: dict,
    estatisticas_filhos: dict
) -> None:
    """
    Gera o relatório final no terminal.

    O relatório reúne:
    - contadores principais;
    - período analisado;
    - dados de qualidade;
    - conclusões finais.
    """

    print("\n" + "=" * 60)
    print("RELATÓRIO FINAL DA ANÁLISE")
    print("=" * 60)

    linhas_originais = df_original.shape[0]
    colunas_originais = df_original.shape[1]
    linhas_limpas = df_limpo.shape[0]
    colunas_limpas = df_limpo.shape[1]

    print("\n1. Contadores principais:")
    print(f"Linhas originais: {formatar_inteiro(linhas_originais)}")
    print(f"Colunas originais: {colunas_originais}")
    print(f"Linhas após limpeza: {formatar_inteiro(linhas_limpas)}")
    print(f"Colunas após limpeza: {colunas_limpas}")
    print(f"Linhas removidas: {formatar_inteiro(linhas_originais - linhas_limpas)}")

    if "CO_ID" in df_limpo.columns:
        print(f"Compras únicas: {formatar_inteiro(df_limpo['CO_ID'].nunique())}")

    if "CL_ID" in df_limpo.columns:
        print(f"Clientes únicos: {formatar_inteiro(df_limpo['CL_ID'].nunique())}")

    if "PR_ID" in df_limpo.columns:
        print(f"Produtos únicos: {formatar_inteiro(df_limpo['PR_ID'].nunique())}")

    if "DATA" in df_limpo.columns:
        datas_validas = df_limpo["DATA"].dropna()

        if not datas_validas.empty:
            data_inicial = datas_validas.min()
            data_final = datas_validas.max()

            print("\n2. Período analisado:")
            print(f"Data inicial: {formatar_data(data_inicial)}")
            print(f"Data final: {formatar_data(data_final)}")

    if estatisticas_filhos:
        print("\n3. Resumo da coluna CL_FHL:")
        print(f"Média de filhos: {formatar_numero(estatisticas_filhos['media'])}")
        print(f"Mediana de filhos: {formatar_numero(estatisticas_filhos['mediana'])}")
        print(f"Moda de filhos: {formatar_moda(estatisticas_filhos['moda'])}")

    print("\n4. Observações sobre qualidade dos dados:")
    print("- Colunas totalmente vazias foram removidas.")
    print("- Categorias vazias ou inválidas foram preenchidas com Sem Categoria.")
    print("- Duplicatas exatas foram removidas.")
    print("- A base não possui colunas de dimensões físicas para tratamento específico.")
    print("- A análise não calcula faturamento, pois não há coluna de valor monetário.")

    conclusoes = gerar_conclusoes(df_limpo, agrupamentos)

    print("\n5. Conclusões principais:")
    for numero, conclusao in enumerate(conclusoes, start=1):
        print(f"{numero}. {conclusao}")

# ------------------------------------------------------------
# 12. Salvamento da base limpa
# ------------------------------------------------------------

def salvar_base_limpa(df: pd.DataFrame, caminho_saida: Path) -> None:
    """
    Salva a base limpa em arquivo CSV.

    O arquivo df_limpo.csv é uma das entregas finais do projeto.
    Ele será salvo dentro da pasta saidas.
    """

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        caminho_saida,
        sep=SEPARADOR_CSV,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print("ARQUIVO FINAL GERADO")
    print("=" * 60)
    print(f"Base limpa salva em: {caminho_saida}")
    print(f"Linhas salvas: {formatar_inteiro(df.shape[0])}")
    print(f"Colunas salvas: {df.shape[1]}")


# ------------------------------------------------------------
# 13. Execução principal do script
# ------------------------------------------------------------

def main() -> None:
    """
    Função principal do projeto.

    Sprint 5:
    - mantém importação, transformação, limpeza e estatística;
    - gera agrupamentos com groupby();
    - constrói relatório final no terminal;
    - apresenta conclusões principais da análise.
    """

    colunas_dictreader, linhas_amostra = ler_amostra_com_dictreader(CAMINHO_BASE)
    mostrar_amostra_dictreader(colunas_dictreader, linhas_amostra)

    df_varejo = carregar_base_com_pandas(CAMINHO_BASE)
    mostrar_informacoes_iniciais(df_varejo)

    df_transformado = aplicar_transformacoes_iniciais(df_varejo)
    df_limpo = limpar_base_varejo(df_transformado)

    validar_identificador_compra(df_limpo)
    mostrar_resultado_sprint3(df_varejo, df_limpo)

    estatisticas_filhos = gerar_estatisticas_filhos(
        df=df_limpo,
        titulo="ESTATÍSTICA DESCRITIVA DE CL_FHL NA BASE LIMPA"
    )

    gerar_estatisticas_filhos_cliente_unico(df_limpo)

    agrupamentos = gerar_agrupamentos(df_limpo)

    gerar_relatorio_final(
        df_original=df_varejo,
        df_limpo=df_limpo,
        agrupamentos=agrupamentos,
        estatisticas_filhos=estatisticas_filhos
    )

    salvar_base_limpa(df_limpo, CAMINHO_DF_LIMPO)


if __name__ == "__main__":
    main()