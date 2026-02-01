# Makefile - Automação do LuisBank Data Platform

.PHONY: setup infra-up data-gen dbt-run dashboard all clean

# 1. Configuração Inicial
setup:
	@echo "📦 Instalando dependências..."
	pip install -r requirements.txt
	@echo "✅ Dependências instaladas."

# 2. Subir Infraestrutura (MinIO)
infra-up:
	@echo "🏗️ Subindo Docker Containers..."
	docker-compose up -d
	@echo "⏳ Aguardando MinIO iniciar (5s)..."
	@timeout /t 5 >nul 2>&1 || sleep 5
	@echo "✅ Infraestrutura pronta."

# 3. Ingestão de Dados (Python)
data-gen:
	@echo "💸 Gerando dados sintéticos (Clientes, Contas e Transações)..."
	python src/generators/master_data.py
	python src/generators/transaction_generator.py
	@echo "✅ Dados gerados e enviados para o Data Lake."

# 4. Transformação (dbt)
dbt-run:
	@echo "dbt Transformando dados (Bronze -> Silver -> Gold)..."
	cd dbt_project && dbt deps --profiles-dir . && dbt run --profiles-dir . && dbt test --profiles-dir .
	@echo "✅ Data Warehouse atualizado e testado."

# 5. Visualização (Streamlit)
dashboard:
	@echo "📊 Iniciando Dashboard..."
	streamlit run src/dashboard/app.py

# --- COMANDO MESTRE ---
# Roda TUDO de uma vez: Infra -> Geração -> Transformação -> Testes
pipeline: infra-up data-gen dbt-run
	@echo "🚀 PIPELINE FINALIZADO COM SUCESSO! O LuisBank está atualizado."

# Limpeza
clean:
	docker-compose down
	rm -rf data/*.jsonl
	rm -rf dbt_project/target