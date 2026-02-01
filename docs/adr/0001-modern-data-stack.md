# ADR 0001 - Modern Data Stack Local

Status: Accepted
Date: 2026-02-01

## Context
O projeto precisa de uma stack local, barata e reproduzivel para demonstrar ingestao, modelagem e analytics.

## Decision
Usar DuckDB como motor OLAP local, dbt para transformacoes e MinIO como storage S3-like.

## Consequences
- Desenvolvimento rapido sem dependencia de cloud real.
- Reproducao local simples via Docker.
- Escala limitada ao ambiente local; para producao sera necessario migrar para engine e storage gerenciados.
