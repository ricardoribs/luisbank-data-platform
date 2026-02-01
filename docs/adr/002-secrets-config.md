# ADR 0002 - Configuracao e Segredos

Status: Accepted
Date: 2026-02-01

## Context
Credenciais e endpoints nao devem ficar hardcoded no repositorio.

## Decision
Usar variaveis de ambiente via `.env` (com `.env.example`) e `env_var` no dbt.

## Consequences
- Configuracao local mais segura.
- Necessario provisionar secrets no CI/CD (ex.: GitHub Secrets).
- Padrao facil de rotacao de credenciais.
