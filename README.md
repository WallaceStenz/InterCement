<h1 align="center">Case Técnico – Analista de Inteligência de Mercado e Precificação</h1>

<p align="center">
  Consolidação das bases <b>COTAÇÕES (SAP)</b> e <b>SalesForce</b>, cálculo de indicadores de recorrência de aprovações e análises de negócio para a área de Inteligência de Mercado e Precificação.
</p>

---

## 📋 Sumário

- [Contexto](#-contexto)
- [Estrutura do repositório](#-estrutura-do-repositório)
- [Bases utilizadas](#-bases-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Como executar](#-como-executar)
- [Regras de negócio aplicadas](#-regras-de-negócio-aplicadas)
- [Chave de cruzamento entre as bases](#-chave-de-cruzamento-entre-as-bases)
- [Colunas criadas na base consolidada](#-colunas-criadas-na-base-consolidada)
- [Análises de negócio (Parte 2)](#-análises-de-negócio-parte-2)
- [Dashboard (Power BI)](#-dashboard-power-bi)
- [Lista de premissas](#-lista-de-premissas)
- [Entregáveis](#-entregáveis)
- [Autor](#-autor)

---

## 🎯 Contexto

O time de Inteligência de Mercado e Precificação recebe diariamente solicitações de desconto (**COTAÇÕES**), cujas informações estão distribuídas em duas fontes distintas: relatórios do **SAP** e do **SalesForce**. Este repositório contém a solução para:

1. **Parte 1 (Python, obrigatório):** consolidar as duas fontes em uma única base e calcular os indicadores de recorrência de aprovações.
2. **Parte 2 (ferramenta livre):** responder às perguntas de negócio a partir da base consolidada.

> Os dados utilizados foram manipulados, são ilustrativos e não representam a realidade — utilizados exclusivamente para fins deste case.

---

## 📂 Estrutura do repositório

```
├── assets/
│   └── Logo_InterCement.png
├── data/
│   ├── COTAÇÕES - CASE.xlsx
│   └── SalesForce - CASE.xlsx
├── notebooks/
│   ├── ETL_SalesForce_Pipeline.ipynb
│   ├── ETL_Cotacao_Pipeline.ipynb
│   └── Consolida_Cotacao_SalesForce.ipynb
├── output/
│   └── base_consolidada.xlsx (ou .csv)
├── analises/
│   └── Analises_Case.xlsx (ou .pdf / .pptx) — respostas dos itens 5.1 a 5.4
├── dashboard/
│   └── Case_Precificacao.pbix
├── premissas.md
└── README.md
```

> Ajuste os nomes de pastas acima conforme a organização final do seu repositório.

---

## 🗂 Bases utilizadas

| Arquivo | Aba | Observações |
|---|---|---|
| `COTAÇÕES - CASE.xlsx` | Base | Base principal. O cabeçalho **não está na primeira linha** — é identificado dinamicamente no código. |
| `SalesForce - CASE.xlsx` | Base 2 | Base complementar, com as colunas **Frete Comercial** e **Chapa**. Contém linhas em branco ao final e registros que não se aplicam à base de Cotações. |

As bases não estão limpas: há duplicidades, ausência de correspondência entre as fontes e valores nulos, todos tratados e documentados no código e na lista de premissas.

---

## ⚙️ Pré-requisitos

- Python 3.10+
- Jupyter Notebook / JupyterLab ou VS Code com extensão Jupyter
- Bibliotecas:
  ```bash
  pip install pandas openpyxl numpy
  ```
  *(liste aqui todas as bibliotecas de terceiros efetivamente utilizadas nos notebooks)*

---

## ▶️ Como executar

⚠️ **Antes de rodar:** em cada notebook, altere o caminho (`path`) dos arquivos de entrada para a pasta local onde as bases `.xlsx` foram salvas na sua máquina. Os caminhos estão configurados nas primeiras células de cada notebook (variáveis do tipo `PATH`, `INPUT_DIR` ou similar).

Execute os notebooks **nesta ordem**:

| Ordem | Notebook | Função |
|---|---|---|
| 1️⃣ | `ETL_SalesForce_Pipeline.ipynb` | Leitura, limpeza e deduplicação da base SalesForce (colunas Frete Comercial e Chapa). |
| 2️⃣ | `ETL_Cotacao_Pipeline.ipynb` | Leitura e tratamento da base COTAÇÕES (identificação do cabeçalho, limpeza e padronização). |
| 3️⃣ | `Consolida_Cotacao_SalesForce.ipynb` | Cruzamento das duas bases pela chave definida na seção 3.1, cálculo dos indicadores de recorrência de aprovações (30 dias) e exportação da base consolidada final (`.xlsx`/`.csv`), insumo da Parte 2. |

---

## 📐 Regras de negócio aplicadas

| Termo | Definição adotada |
|---|---|
| **Cotação aprovada** | `Status da Cotação` = "Aprovada". Desconsiderados: "Parcialmente aprovada", "Rejeitada", "Cancelada" e "Aguardando aprovação". O campo `Status FLUXO SAP*` **não** é usado como critério. |
| **Data de referência** | Sempre `Dt. Criação Sol.`. O campo `Última Ação em` não é utilizado nos cálculos de janela. |
| **Últimos 30 dias** | Janela móvel de 30 dias corridos anteriores à `Dt. Criação Sol.` da própria linha, **excluindo** a linha em análise. |
| **Tipos de cotação** | Apenas "Banda" e "PrecoFixo" entram no cálculo de recorrência (4.3.1/4.3.2). "Prazo" e "FreteComercial" ficam fora do escopo. |
| **Desconto concedido** | Campo `Var. Preço Proposto` (admite positivos, negativos e nulos — tratamento documentado em `premissas.md`). |
| **Período da base** | Cotações no início do período têm janela de 30 dias naturalmente incompleta; utilizado apenas o histórico disponível, sem extrapolação. |

---

## 🔑 Chave de cruzamento entre as bases

| # | Base COTAÇÕES | Base SalesForce |
|---|---|---|
| 1 | ID da Cotação do SAP | ID da Cotação do SAP *(não usar "ID da Cotação")* |
| 2 | Material | Material: Código do material |
| 3 | Cód. Expedição | Cód. Expedição |

**Tratamentos aplicados e documentados:**
- **Chaves duplicadas no SalesForce** (inclusive com valores divergentes de Frete Comercial): regra de deduplicação definida e registrada em `premissas.md`.
- **Cotações sem correspondência no SalesForce**: mantidas na base final e sinalizadas de forma distinta de um frete efetivamente igual a zero (relevante para o item 5.4).
- O número de linhas da base COTAÇÕES **não aumenta** após o cruzamento.

---

## 🧮 Colunas criadas na base consolidada

| Coluna | Descrição |
|---|---|
| `Frete Comercial` | Valor correspondente obtido via cruzamento (item 4.1). |
| `Chapa` | Valor correspondente obtido via cruzamento (item 4.2). |
| `Qtd. cotações aprovadas 30d` | Quantidade de cotações aprovadas (Banda/PrecoFixo) do mesmo Código do Cliente + Material + Cód. Expedição, na janela de 30 dias anteriores (item 4.3.1). `0` quando não houver cotações elegíveis. |
| `Soma da variação de desconto 30d` | Soma do `Var. Preço Proposto` das cotações elegíveis na mesma janela (item 4.3.2). `0` quando não houver cotações elegíveis. |

---

## 📊 Análises de negócio (Parte 2)

Respostas disponíveis em `analises/` (Excel/PDF/apresentação):

- **5.1** Top 10 clientes por concessão de desconto acumulada (total, por Região e por Gestão de Vendas).
- **5.2** Top 10 clientes por quantidade de cotações aprovadas na janela de 30 dias (total, por Região e por Gestão de Vendas).
- **5.3** Perfil de cliente: cotações aprovadas por `Cliente Condição` (Cai, Cresce, Churn, Igual, Novo) com representatividade percentual.
- **5.4** Fretes zerados em operações CIF por expedição, com distinção entre frete efetivamente zero e frete sem informação na base de origem, e resposta dissertativa com recomendação para os casos sem informação de frete.

---

## 📈 Dashboard (Power BI)

O arquivo `dashboard/Case_Precificacao.pbix` consome a base consolidada gerada no item 4.4.

⚠️ **Antes de abrir o arquivo `.pbix`**, atualize a fonte de dados (**Editar consultas → Configurações da fonte de dados**) para o caminho local onde a base consolidada foi salva na sua máquina.

---

## 📝 Lista de premissas

Todas as decisões tomadas diante de ambiguidades ou dados inconsistentes (tratamento de nulos, regra de deduplicação, sinal do desconto, cotações sem correspondência, etc.) estão documentadas em [`premissas.md`](./premissas.md).

---

## ✅ Entregáveis

- [x] Repositório público no GitHub com código Python da Parte 1
- [x] README com instruções de execução, bibliotecas utilizadas e premissas
- [x] Base consolidada (item 4.4)
- [x] Arquivo de análises (itens 5.1 a 5.4)
- [x] Lista de premissas

---

## 👤 Autor

*Preencha aqui seu nome, e-mail de contato e/ou LinkedIn.*
