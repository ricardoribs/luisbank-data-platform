# ADR 001: Escolha do DuckDB como Motor OLAP

## Contexto
Precisávamos de um banco analítico para processar dados do Data Lake com foco em performance local, baixo custo e facilidade de reprodução.

## Decisão
Escolhemos o DuckDB por oferecer execução in-process, boa performance em OLAP e suporte a leitura direta de arquivos (parquet/CSV), alinhado com a proposta do projeto.

## Consequências
Positivas:
- Alta performance local e execução simples (sem servidor dedicado)
- Leitura direta de arquivos com abordagem zero-copy
- Fácil integração com dbt e Python

Negativas:
- Limitações para concorrência de escrita
- Escalabilidade limitada ao ambiente local
- Dependência de práticas de versionamento/backup para uso mais amplo
