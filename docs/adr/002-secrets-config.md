# ADR 002: Configuração de Segredos e Variáveis de Ambiente

## Contexto
As credenciais do MinIO/S3 e endpoints não devem ficar hardcoded no repositório. O projeto precisa manter a configuração local simples e, ao mesmo tempo, permitir integração segura em CI/CD.

## Decisão
Utilizar variáveis de ambiente via `.env` (com `.env.example`) e `env_var` no dbt. No CI, os valores são passados por secrets do provedor (ex.: GitHub Secrets).

## Consequências
Positivas:
- Redução do risco de vazamento de credenciais
- Rotação de segredos facilitada
- Portabilidade entre ambientes local e CI/CD

Negativas:
- Exige configuração prévia do ambiente
- Falhas de execução quando variáveis não estão definidas
