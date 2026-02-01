# LuisBank Data Platform

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Stack](https://img.shields.io/badge/stack-dbt%20%7C%20duckdb%20%7C%20streamlit-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> Plataforma de dados end-to-end que simula a operação de um banco digital, o **LuisBank**, construída como camada analítica sobre o projeto transacional [Immutable Ledger](https://github.com/ricardoribs/immutable-ledger), cobrindo desde a ingestão de eventos financeiros até analytics avançado de CRM (RFM) e compliance.

---

## Arquitetura da Solução

O projeto segue a arquitetura Modern Data Stack, focada em alta performance local e baixo custo, utilizando processamento in-process (DuckDB).

```mermaid
graph LR
    A[Gerador Python] -->|JSONL| B((MinIO / S3));
    B -->|Bronze Layer| C{DuckDB};
    C -->|dbt Transformations| D[Data Warehouse];
    D -->|Silver: Dimensões/Fatos| E[Gold: Aggregates];
    E -->|Analytics| F[Streamlit Dashboard];
    E -->|Marketing| G[RFM Segmentation];
```

---

## Tech Stack

| Componente     | Tecnologia                | Função                                                               |
| -------------- | ------------------------- | -------------------------------------------------------------------- |
| Ingestion      | Python (Faker, Pydantic)  | Geração de dados sintéticos com integridade referencial e contratos. |
| Data Lake      | MinIO (Docker)            | Armazenamento de objetos (S3 compatible).                            |
| Processing     | DuckDB                    | Motor OLAP de alta performance (zero-copy).                          |
| Transformation | dbt Core                  | Modelagem dimensional, testes de qualidade e linhagem.               |
| Visualization  | Streamlit + Plotly        | Data app interativo para executivos e operação.                      |
| Orchestration  | Makefile / GitHub Actions | Automação de pipeline e CI/CD.                                       |

---

## Inteligência de Negócio (Business Logic)

O projeto não apenas processa dados, mas gera valor por meio de regras de negócio complexas:

### 1. Segmentação RFM (Recency, Frequency, Monetary)

Algoritmo SQL (ntile) para classificar clientes em quintis.

Categorias: Champions, Loyal, Promising, At Risk, Hibernating.

### 2. Auditoria & Compliance

Monitoramento de transações acima de R$ 5k.

Detecção de outliers transacionais.

### 3. Data Quality

Testes de unicidade (unique) e não nulos (not_null).

Validação de chaves estrangeiras entre contas e transações.

---

## Como Rodar Localmente

### Pré-requisitos

Docker & Docker Compose

Python 3.10+

Git

### Configuração de Credenciais

1. Copie `.env.example` para `.env`
2. Ajuste `MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD`

> Aviso: faça rotação periódica de credenciais e nunca versione o arquivo `.env`.

### Passo a Passo

#### 1. Clone o repositório

```bash
git clone https://github.com/ricardoribs/luisbank-data-platform.git
cd luisbank-data-platform
```

#### 2. Setup do Ambiente

```bash
# Cria ambiente virtual e instala libs
make setup
```

#### 3. Inicie a Infraestrutura (Data Lake)

```bash
make infra-up
```

#### 4. Pipeline Completo (Ingestão -> Transformação)

```bash
# Gera dados, sobe para o MinIO, roda dbt run e dbt test
make pipeline
```

#### 5. Acesse o Dashboard

```bash
make dashboard
```

Acesse em: [http://localhost:8501](http://localhost:8501)

## Segurança

- Credenciais são lidas via variáveis de ambiente (`.env`).
- Rotacione senhas regularmente e trate valores reais como secrets.

---

## Documentação Técnica

- ADRs: `docs/adr/` (001-escolha-duckdb.md, 002-secrets-config.md)
- ERD: `docs/erd.md`
- Runbook: `docs/runbook.md`

## Estrutura do Projeto

```
luisbank-data-platform/
|-- data/                  # Arquivos locais (DuckDB, JSONLs)
|-- dbt_project/           # Projeto de transformação
|   |-- models/
|   |   |-- staging/       # Views em cima do Data Lake (Bronze)
|   |   |-- marts/         # Tabelas Fato e Dimensões (Silver/Gold)
|   |   `-- marketing/     # Segmentação RFM
|   `-- tests/             # Testes de qualidade de dados
|-- infrastructure/        # Arquivos Docker/Terraform
|-- src/
|   |-- generators/        # Scripts Python (Faker)
|   `-- dashboard/         # Aplicação Streamlit
|-- Makefile               # Automação de comandos
`-- docker-compose.yml     # Infraestrutura MinIO
```

---

## Resultados Visuais

### 1. Dashboard Executivo (Streamlit)

Visão consolidada de KPIs financeiros com cálculo de deltas e tendências temporais.
![Dashboard Overview](docs/dashboard_overview.png)

### 2. Segmentação Inteligente (RFM)

Aplicação de lógica de negócio (SQL Window Functions) para classificar clientes em clusters (Champions, At Risk, etc.) e gerar listas de ação para o marketing.
![RFM Segmentation](docs/rfm_segmentation.png)

### 3. Engenharia & Linhagem (dbt)

Pipeline de dados estruturado em camadas (Bronze, Silver, Gold), garantindo rastreabilidade e qualidade.
![dbt Lineage](docs/dbt_lineage.png)
