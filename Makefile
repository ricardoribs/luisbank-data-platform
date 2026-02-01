# Makefile - Automacao do LuisBank Data Platform

.PHONY: setup infra-up data-gen dbt-run dashboard all clean

# 1. Configuracao Inicial
setup:
	@echo "Instalando dependencias..."
	pip install -r requirements.txt
	@echo "Dependencias instaladas."

# 2. Subir Infraestrutura (MinIO)
infra-up:
	@echo "Subindo Docker Containers..."
	docker-compose up -d
	@echo "Aguardando MinIO iniciar (5s)..."
	@timeout /t 5 >nul 2>&1 || sleep 5
	@echo "Infraestrutura pronta."

# 3. Ingestao de Dados (Python)
data-gen:
	@echo "Gerando dados sinteticos (Clientes, Contas e Transacoes)..."
	python -m src.generators.master_data
	python -m src.generators.transaction_generator
	@echo "Dados gerados e enviados para o Data Lake."

# 4. Transformacao (dbt)
dbt-run:
	@echo "dbt Transformando dados (Bronze -> Silver -> Gold)..."
	cd dbt_project && dbt deps --profiles-dir . && dbt snapshot --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir .
	@echo "Data Warehouse atualizado e testado."

# 5. Visualizacao (Streamlit)
dashboard:
	@echo "Iniciando Dashboard..."
	streamlit run src/dashboard/app.py

# --- COMANDO MESTRE ---
# Roda TUDO de uma vez: Infra -> Geracao -> Transformacao -> Testes
pipeline: infra-up data-gen dbt-run
	@echo "PIPELINE FINALIZADO COM SUCESSO! O LuisBank esta atualizado."

# Limpeza
clean:
	docker-compose down
	rm -rf data/*.jsonl
	rm -rf dbt_project/target
