"""
ETL_Cotacao_Pipeline.py

Pipeline ETL para carregar, tratar e exportar a base de Cotações
(COTAÇÕES_CASE.xlsx), gerando o arquivo Catacao_Result.xlsx.

Convertido a partir do notebook ETL_Cotacao_Pipeline.ipynb
"""

import pandas as pd
import logging
from datetime import datetime

# -----------------------------------------------------------
# CONFIGURAÇÃO DE LOG
# -----------------------------------------------------------

logging.basicConfig(
    filename="pipeline_cotacoes.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log(msg):
    """Função auxiliar para registrar logs no arquivo e no console."""
    logging.info(msg)
    print(msg)


# -----------------------------------------------------------
# 1. EXTRACT — Carregar arquivo Excel
# -----------------------------------------------------------


def carregar_arquivo(caminho, dtype_cols):
    """Carrega o arquivo Excel com tipos definidos e header correto."""
    log("Carregando arquivo Excel COTAÇÕES_CASE...")
    df = pd.read_excel(caminho, header=2, dtype=dtype_cols)
    log(f"Arquivo carregado com {df.shape[0]} linhas e {df.shape[1]} colunas.")
    return df


# -----------------------------------------------------------
# 2. TRANSFORM — Limpeza e padronização
# -----------------------------------------------------------


def converter_decimal(df, cols):
    """Converte colunas para decimal, substituindo erros por NaN."""
    log("Convertendo colunas decimais...")
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def tratar_tipo_cotacao(df):
    """Padroniza a coluna TipoCotação substituindo vazio por 'Vazio'."""
    log("Tratando coluna TipoCotação...")
    df["TipoCotação"] = df["TipoCotação"].replace("", pd.NA)
    df["TipoCotação"] = df["TipoCotação"].fillna("Vazio")
    return df


def tratar_decimais_vazios(df, cols):
    """Substitui valores vazios nas colunas decimais por zero."""
    log("Tratando valores vazios nas colunas decimais...")
    for col in cols:
        df[col] = df[col].replace("", pd.NA)
        df[col] = df[col].fillna(0)
    return df


def verificar_duplicados(df, chaves):
    """Identifica e exibe duplicados com base nas chaves."""
    log("Verificando duplicidades...")
    duplicados = df[df.duplicated(subset=chaves, keep=False)]
    qtd = duplicados.shape[0]
    log(f"Duplicidades encontradas: {qtd}")
    return duplicados


# -----------------------------------------------------------
# 3. LOAD — Exportar resultado final
# -----------------------------------------------------------


def exportar_excel(df, caminho_saida_base):
    """Exporta o DataFrame para Excel SEM timestamp no nome."""
    log(f"Exportando arquivo final: {caminho_saida_base}")
    df.to_excel(caminho_saida_base, index=False)
    log("Arquivo exportado com sucesso!")


# -----------------------------------------------------------
# PIPELINE PRINCIPAL
# -----------------------------------------------------------


def pipeline_cotacoes():
    log("Iniciando pipeline ETL — COTAÇÕES_CASE...")

    # Caminhos
    caminho = r"C:\Users\stenz\Documents\InterCement\Base Dados\COTAÇÕES_CASE.xlsx"
    caminho_saida = r"C:\Users\stenz\Documents\InterCement\Base Result\Catacao_Result.xlsx"

    # Tipos das colunas
    dtype_cols = {
        "Status FLUXO SAP*": "string",
        "TipoCotação": "string",
        "ID da Cotação do SAP": "string",
        "Dt. Criação Sol.": "string",
        "Status da Cotação": "string",
        "Id Solic. Ajuste": "string",
        "Última Ação em": "string",
        "Cód. Expedição": "string",
        "Região": "string",
        "Gestão de Vendas": "string",
        "Micro Região": "string",
        "Código do Cliente": "string",
        "Material": "string",
        "Embalagem": "string",
        "Cliente Condição": "string",
        "Incoterm": "string"
    }

    # Colunas decimais
    decimal_cols = ["Preço Atual", "Preço Proposto", "Var. Preço Proposto"]

    # Chaves para duplicidade
    cols_dup = ["ID da Cotação do SAP", "Material", "Cód. Expedição"]

    # EXECUÇÃO DO PIPELINE
    df = carregar_arquivo(caminho, dtype_cols)
    df = converter_decimal(df, decimal_cols)
    df = tratar_tipo_cotacao(df)
    df = tratar_decimais_vazios(df, decimal_cols)

    # Verificar duplicidades (somente exibe, não remove)
    duplicados = verificar_duplicados(df, cols_dup)

    # Exportar resultado final
    exportar_excel(df, caminho_saida)

    log("Pipeline ETL concluído com sucesso!")


# -----------------------------------------------------------
# EXECUTAR PIPELINE
# -----------------------------------------------------------

if __name__ == "__main__":
    pipeline_cotacoes()
