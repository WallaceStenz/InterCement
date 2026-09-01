"""
Concolida_Cotacao_SalesForce.py

Pipeline ETL para consolidar as bases de Cotação (Catacao) e SalesForce,
aplicando join, regras de negócio de janela móvel de 30 dias e
exportando o resultado final para Excel.

Convertido a partir do notebook Concolida_Cotacao_SalesForce.ipynb
"""

import pandas as pd
import os
import re
from datetime import timedelta

# ===========================================================
# 1. CONFIGURAÇÕES
# ===========================================================

PASTA_BASE = r"C:\Users\stenz\Documents\InterCement\Base Result"
ARQ_CATACAO = "Catacao_Result.xlsx"
ARQ_SALESFORCE = "SalesForce_Result.xlsx"
ARQ_SAIDA = "BaseFinal_Cotacao_SalesForce.xlsx"

# ===========================================================
# 2. SUPORTE
# ===========================================================


def carregar_excel(caminho):
    """Carrega arquivo Excel com validação."""
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    print(f"[LOAD] {caminho}")
    df = pd.read_excel(caminho)
    print(f"[LOAD] Linhas: {df.shape[0]}")
    return df


def padronizar_colunas(df):
    """Remove espaços, quebras de linha e padroniza nomes."""
    df.columns = (
        df.columns
        .str.strip()
        .str.replace("\n", "")
        .str.replace("\r", "")
    )
    return df


def detectar_formato_data(valor):
    """Detecta formato textual da data (diagnóstico)."""
    formatos = {
        r'^\d{2}/\d{2}/\d{4}$': 'dd/mm/aaaa',
        r'^\d{2}/\d{2}/\d{2}$': 'dd/mm/aa',
        r'^\d{4}-\d{2}-\d{2}$': 'aaaa-mm-dd',
        r'^\d{2}-\d{2}-\d{4}$': 'dd-mm-aaaa',
        r'^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$': 'dd/mm/aaaa hh:mm:ss'
    }
    for regex, nome in formatos.items():
        if re.match(regex, valor):
            return nome
    return "formato desconhecido"


def converter_datas(df):
    """Detecta automaticamente a coluna de data e converte."""
    print("[DATE] Procurando coluna de data...")

    col_data = [c for c in df.columns if "Criação" in c and "Sol" in c]

    if not col_data:
        raise Exception("Nenhuma coluna contendo 'Criação' e 'Sol' encontrada.")

    col_data = col_data[0]
    print(f"[DATE] Coluna detectada: {col_data}")

    df["Formato Detectado"] = df[col_data].astype(str).apply(detectar_formato_data)
    print(df["Formato Detectado"].value_counts())

    df[col_data] = pd.to_datetime(df[col_data], errors="coerce", dayfirst=True)

    df.rename(columns={col_data: "Dt_Criacao_Sol"}, inplace=True)

    return df


# ===========================================================
# 3. TRANSFORMAÇÕES
# ===========================================================


def aplicar_left_join(df_catacao, df_salesforce):
    """LEFT JOIN profissional."""
    print("[JOIN] Iniciando LEFT JOIN...")

    df_salesforce = df_salesforce.rename(columns={
        "Material: Código do material": "Material"
    })

    df_join = df_catacao.merge(
        df_salesforce[
            ["ID da Cotação do SAP", "Material", "Cód. Expedição",
             "Frete Comercial", "Chapa"]
        ],
        on=["ID da Cotação do SAP", "Material", "Cód. Expedição"],
        how="left"
    )

    df_join[["Frete Comercial", "Chapa"]] = df_join[["Frete Comercial", "Chapa"]].fillna(0)

    print(f"[JOIN] Concluído. Linhas: {df_join.shape[0]}")
    return df_join


def calcular_janela_30d(grupo):
    """Janela móvel de 30 dias."""
    grupo = grupo.sort_values("Dt_Criacao_Sol")

    grupo["cnt_shift"] = grupo["cnt_elegivel"].shift(1)
    grupo["var_shift"] = grupo["var_elegivel"].shift(1)

    grupo = grupo.set_index("Dt_Criacao_Sol")

    grupo["Qtd_cotacoes_aprovadas_30d"] = (
        grupo["cnt_shift"].rolling("30D").sum().fillna(0).astype(int)
    )

    grupo["Soma_variacao_desconto_30d"] = (
        grupo["var_shift"].rolling("30D").sum().fillna(0)
    )

    return grupo.reset_index()


def aplicar_regras_janela(df):
    """Aplica regras de negócio da janela de 30 dias."""
    print("[RULE] Aplicando regras de janela 30 dias...")

    mask = (
        (df["Status da Cotação"] == "Aprovada") &
        (df["TipoCotação"].isin(["Banda", "PrecoFixo"]))
    )

    df["Var_Preco_Proposto_aux"] = df["Var. Preço Proposto"].fillna(0)
    df["cnt_elegivel"] = mask.astype(int)
    df["var_elegivel"] = df["Var_Preco_Proposto_aux"].where(mask, 0)

    # Observação: a partir do pandas 3.0, o groupby().apply() remove
    # automaticamente as colunas usadas no agrupamento do DataFrame passado
    # à função (comportamento antigo do include_groups=False). Para manter
    # 'Código do Cliente', 'Material' e 'Cód. Expedição' no resultado final,
    # iteramos manualmente sobre os grupos em vez de usar .apply() direto.
    grupos_processados = []
    for _, grupo in df.groupby(
        ["Código do Cliente", "Material", "Cód. Expedição"], group_keys=False
    ):
        grupos_processados.append(calcular_janela_30d(grupo))

    df = pd.concat(grupos_processados, ignore_index=True)

    df.drop(columns=[
        "Var_Preco_Proposto_aux", "cnt_elegivel", "var_elegivel",
        "cnt_shift", "var_shift"
    ], inplace=True)

    print("[RULE] Regras aplicadas.")
    return df


# ===========================================================
# 4. EXPORTAÇÃO
# ===========================================================


def exportar(df):
    """Exporta para Excel."""
    caminho = os.path.join(PASTA_BASE, ARQ_SAIDA)
    print(f"[EXPORT] Exportando para: {caminho}")

    if "Formato Detectado" in df.columns:
        df.drop(columns=["Formato Detectado"], inplace=True)

    df.to_excel(caminho, index=False)
    print("[EXPORT] Concluído.")


# ===========================================================
# 5. PIPELINE ETL COMPLETO
# ===========================================================


def pipeline_etl():
    print("\n========== INÍCIO PIPELINE ETL ==========\n")

    # 1. Carregar
    df_catacao = carregar_excel(os.path.join(PASTA_BASE, ARQ_CATACAO))
    df_salesforce = carregar_excel(os.path.join(PASTA_BASE, ARQ_SALESFORCE))

    # 2. Padronizar colunas
    df_catacao = padronizar_colunas(df_catacao)
    df_salesforce = padronizar_colunas(df_salesforce)

    # 3. Converter datas
    df_catacao = converter_datas(df_catacao)

    # 4. JOIN
    df_final = aplicar_left_join(df_catacao, df_salesforce)

    # 5. Regras de negócio
    df_final = aplicar_regras_janela(df_final)

    # 6. Exportar
    exportar(df_final)

    print("\n========== PIPELINE ETL FINALIZADO ==========\n")
    return df_final


# ===========================================================
# EXECUTAR PIPELINE
# ===========================================================

if __name__ == "__main__":
    df_final = pipeline_etl()
    print(df_final.head())
