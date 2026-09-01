"""
ETL_SalesForce_Pipeline.py

Pipeline ETL para carregar, tratar e exportar a base do SalesForce
(SalesForce_CASE.xlsx), gerando o arquivo SalesForce_Result.xlsx.

Convertido a partir do notebook ETL_SalesForce_Pipeline.ipynb
"""

import pandas as pd
import logging
from datetime import datetime

# -----------------------------------------------------------
# CONFIGURAÇÃO DE LOG
# -----------------------------------------------------------

logging.basicConfig(
    filename="pipeline_salesforce.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def log(msg):
    """Função auxiliar para registrar logs."""
    logging.info(msg)
    print(msg)


# -----------------------------------------------------------
# 1. EXTRACT — Carregar arquivo Excel
# -----------------------------------------------------------


def carregar_arquivo(caminho, dtype_cols):
    """Carrega o arquivo Excel com tipos definidos."""
    log("Carregando arquivo Excel...")
    df = pd.read_excel(caminho, dtype=dtype_cols)
    log(f"Arquivo carregado com {df.shape[0]} linhas e {df.shape[1]} colunas.")
    return df


# -----------------------------------------------------------
# 2. TRANSFORM — Limpeza e padronização
# -----------------------------------------------------------


def tratar_colunas_texto(df, cols):
    """Padroniza colunas de texto substituindo NaN/vazio por '0'."""
    log("Tratando colunas de texto...")
    for col in cols:
        df[col] = (
            df[col]
            .fillna("0")
            .replace("", "0")
            .astype("string")
        )
    return df


def tratar_colunas_numericas(df, cols):
    """Padroniza colunas numéricas substituindo NaN/vazio por 0.0."""
    log("Tratando colunas numéricas...")
    for col in cols:
        df[col] = (
            df[col]
            .fillna(0.0)
            .replace("", 0.0)
            .astype(float)
        )
    return df


def remover_linhas_vazias(df):
    """Remove linhas totalmente vazias."""
    log("Removendo linhas totalmente vazias...")
    cond = df.isna().all(axis=1) | df.eq("").all(axis=1)
    qtd = cond.sum()
    log(f"Linhas vazias encontradas: {qtd}")
    return df[~cond]


def remover_duplicados(df, chaves):
    """Remove duplicados com base em chaves específicas."""
    log("Verificando duplicados...")
    qtd = df.duplicated(subset=chaves).sum()
    log(f"Duplicados encontrados: {qtd}")
    return df.drop_duplicates(subset=chaves)


def remover_tipo_zero(df):
    """Remove linhas onde TipoCotação = '0'."""
    log("Removendo linhas onde TipoCotação = '0'...")
    qtd = (df["TipoCotação"] == "0").sum()
    log(f"Linhas removidas: {qtd}")
    return df[df["TipoCotação"] != "0"]


def filtrar_condicoes(df):
    """Filtra linhas onde TipoCotação está vazia e fretes/chapa <= 0."""
    log("Filtrando linhas com condições específicas...")
    cond = (
        (df["TipoCotação"] == "") &
        (df["Frete Comercial"] <= 0) &
        (df["Chapa"] <= 0)
    )
    resultado = df[cond]
    log(f"Linhas encontradas com condições: {resultado.shape[0]}")
    return resultado


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


def pipeline_salesforce():
    log("Iniciando pipeline ETL Salesforce...")

    # Caminhos
    caminho = r"C:\Users\stenz\Documents\InterCement\Base Dados\SalesForce_CASE.xlsx"
    caminho_saida = r"C:\Users\stenz\Documents\InterCement\Base Result\SalesForce_Result.xlsx"

    # Tipos das colunas
    dtype_cols = {
        "TipoCotação": "string",
        "ID da Cotação": "string",
        "ID da Cotação do SAP": "string",
        "Código do Cliente": "string",
        "Cód. Expedição": "string",
        "Material: Código do material": "string",
        "Meio de Transporte": "string"
    }

    # Colunas para tratamento
    cols_texto = list(dtype_cols.keys())
    cols_numero = ["Frete Comercial", "Chapa"]
    chaves_duplicidade = [
        "ID da Cotação do SAP",
        "Material: Código do material",
        "Cód. Expedição"
    ]

    # EXECUÇÃO DO PIPELINE
    df = carregar_arquivo(caminho, dtype_cols)
    df = tratar_colunas_texto(df, cols_texto)
    df = tratar_colunas_numericas(df, cols_numero)
    df = remover_linhas_vazias(df)
    df = remover_duplicados(df, chaves_duplicidade)
    df = remover_tipo_zero(df)

    # Filtragem adicional (opcional)
    resultado_condicoes = filtrar_condicoes(df)

    # Exportação
    exportar_excel(df, caminho_saida)

    log("Pipeline ETL concluído com sucesso!")


# -----------------------------------------------------------
# EXECUTAR PIPELINE
# -----------------------------------------------------------

if __name__ == "__main__":
    pipeline_salesforce()
