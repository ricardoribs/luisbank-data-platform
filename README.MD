# LuisBank Data Platform

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Stack](https://img.shields.io/badge/stack-dbt%20%7C%20duckdb%20%7C%20streamlit-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue.svg)]()

> Uma plataforma de dados End-to-End simulando a operaÃ§Ã£o de um Banco Digital, o **LuisBank**, construÃ­da como camada analÃ­tica sobre o projeto transacional [Immutable Ledger](https://github.com/ricardoribs/immutable-ledger), cobrindo desde a ingestÃ£o de eventos financeiros atÃ© Analytics avanÃ§ado de CRM (RFM) e Compliance.

---

## Arquitetura da SoluÃ§Ã£o

O projeto segue a arquitetura Modern Data Stack focada em alta performance local e baixo custo, utilizando processamento in-process (DuckDB).

```mermaid
graph LR
    A[Gerador Python] -->|JSONL| B((MinIO / S3));
    B -->|Bronze Layer| C{DuckDB};
    C -->|dbt Transformations| D[Data Warehouse];
    D -->|Silver: DimensÃµes/Fatos| E[Gold: Aggregates];
    E -->|Analytics| F[Streamlit Dashboard];
    E -->|Marketing| G[RFM Segmentation];
```

---

## Tech Stack

| Componente     | Tecnologia                | FunÃ§Ã£o                                                               |
| -------------- | ------------------------- | -------------------------------------------------------------------- |
| Ingestion      | Python (Faker, Pydantic)  | GeraÃ§Ã£o de dados sintÃ©ticos com integridade referencial e contratos. |
| Data Lake      | MinIO (Docker)            | Armazenamento de objetos (S3 Compatible).                            |
| Processing     | DuckDB                    | Motor OLAP de alta performance (Zero-Copy).                          |
| Transformation | dbt Core                  | Modelagem dimensional, testes de qualidade e linhagem.               |
| Visualization  | Streamlit + Plotly        | Data App interativo para executivos e operaÃ§Ã£o.                      |
| Orchestration  | Makefile / Github Actions | AutomaÃ§Ã£o de pipeline e CI/CD.                                       |

---

## InteligÃªncia de NegÃ³cio (Business Logic)

O projeto nÃ£o apenas processa dados, mas gera valor atravÃ©s de regras de negÃ³cio complexas:

### 1. SegmentaÃ§Ã£o RFM (Recency, Frequency, Monetary)

Algoritmo SQL (ntile) para classificar clientes em quintis.

Categorias: Champions, Loyal, Promising, At Risk, Hibernating.

### 2. Auditoria & Compliance

Monitoramento de transaÃ§Ãµes acima de R$ 5k.

DetecÃ§Ã£o de outliers transacionais.

### 3. Data Quality

Testes de unicidade (unique) e nÃ£o-nulos (not_null).

ValidaÃ§Ã£o de chaves estrangeiras entre Contas e TransaÃ§Ãµes.

---

## Como Rodar Localmente

### PrÃ©-requisitos

Docker & Docker Compose

Python 3.10+

Git

### Configuracao de Credenciais

1. Copie .env.example para .env
2. Ajuste MINIO_ROOT_USER e MINIO_ROOT_PASSWORD

> Aviso: faca rotacao periodica de credenciais e nunca versiona o arquivo .env.
### Passo a Passo

#### 1. Clone o repositÃ³rio

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

#### 4. Pipeline Completo (IngestÃ£o -> TransformaÃ§Ã£o)

```bash
# Gera dados, sobe pro MinIO, roda dbt run e dbt test
make pipeline
```

#### 5. Acesse o Dashboard

```bash
make dashboard
```

Acesse em: [http://localhost:8501](http://localhost:8501)

## Seguranca

- Credenciais sao lidas via variaveis de ambiente (.env).
- Rotacione senhas regularmente e trate valores reais como secrets.
---


## Documentacao Tecnica

- ADRs: docs/adr/
- ERD: docs/erd.md
- Runbook: docs/runbook.md
## Estrutura do Projeto

```
luisbank-data-platform/
â”œâ”€â”€ data/                  # Arquivos locais (DuckDB, JSONLs)
â”œâ”€â”€ dbt_project/           # Projeto de TransformaÃ§Ã£o
â”‚   â”œâ”€â”€ models/
â”‚   â”‚   â”œâ”€â”€ staging/       # View em cima do Data Lake (Bronze)
â”‚   â”‚   â”œâ”€â”€ marts/         # Tabela Fato e DimensÃµes (Silver/Gold)
â”‚   â”‚   â””â”€â”€ marketing/     # SegmentaÃ§Ã£o RFM
â”‚   â””â”€â”€ tests/             # Testes de qualidade de dados
â”œâ”€â”€ infrastructure/        # Arquivos Docker/Terraform
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ generators/        # Scripts Python (Faker)
â”‚   â””â”€â”€ dashboard/         # AplicaÃ§Ã£o Streamlit
â”œâ”€â”€ Makefile               # AutomaÃ§Ã£o de comandos
â””â”€â”€ docker-compose.yml     # Infraestrutura MinIO
```

---

## Resultados Visuais

### 1. Dashboard Executivo (Streamlit)
VisÃ£o consolidada de KPIs financeiros com cÃ¡lculo de deltas e tendÃªncias temporais.
![Dashboard Overview](docs/dashboard_overview.png)

### 2. SegmentaÃ§Ã£o Inteligente (RFM)
AplicaÃ§Ã£o de lÃ³gica de negÃ³cio (SQL Window Functions) para classificar clientes em clusters (Champions, At Risk, etc) e gerar listas de aÃ§Ã£o para o Marketing.
![RFM Segmentation](docs/rfm_segmentation.png)

### 3. Engenharia & Linhagem (dbt)
Pipeline de dados estruturado em camadas (Bronze, Silver, Gold) garantindo rastreabilidade e qualidade.
![dbt Lineage](docs/dbt_lineage.png)