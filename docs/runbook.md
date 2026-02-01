# Runbook - LuisBank Data Platform

## Objetivo
Guia rapido para diagnostico e resolucao de problemas comuns.

## MinIO nao sobe
- Verifique se o Docker esta rodando.
- Confirme portas 9000/9001 livres.
- Recrie os containers: `docker-compose down && docker-compose up -d`.

## Credenciais invalidas
- Confirme `.env` com `MINIO_ROOT_USER` e `MINIO_ROOT_PASSWORD`.
- Rotacione senhas se necessario.

## Erros de ingestao
- Verifique logs dos geradores em `stdout`.
- Arquivos com falha sao movidos para `data/dlq/`.

## dbt falha ao compilar
- Rode `dbt deps --profiles-dir .`.
- Verifique `dbt_project/profiles.yml` e variaveis de ambiente.

## Testes falhando
- Rode `pytest -q`.
- Rode `dbt test --profiles-dir . --fail-fast`.
