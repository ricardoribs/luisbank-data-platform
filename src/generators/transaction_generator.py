import os
import json
import random
import boto3
from faker import Faker
from datetime import datetime, timedelta
from models import Transaction, TransactionType

# Configuração
faker = Faker('pt_BR')
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "landing-zone"

# Lista de bancos reais para dar realismo (Correção do erro anterior)
EXTERNAL_BANKS = [
    "Banco do Brasil", "Itaú Unibanco", "Bradesco", "Caixa Econômica", 
    "Nubank", "Banco Inter", "Santander", "C6 Bank", "BTG Pactual", "Neon"
]

s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def load_existing_account_ids():
    """Baixa o arquivo de contas mais recente do MinIO para pegar IDs válidos."""
    print("🔍 Buscando contas existentes no Data Lake...")
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="accounts/")
        if 'Contents' not in response:
            raise Exception("Nenhuma conta encontrada! Rode o master_data.py primeiro.")
            
        # Pega o último arquivo (ordem alfabética/cronológica)
        last_file = sorted(response['Contents'], key=lambda x: x['Key'])[-1]['Key']
        print(f"📂 Lendo arquivo: {last_file}")
        
        obj = s3_client.get_object(Bucket=BUCKET_NAME, Key=last_file)
        content = obj['Body'].read().decode('utf-8')
        
        account_ids = []
        for line in content.splitlines():
            if line.strip():
                record = json.loads(line)
                account_ids.append(record['id'])
                
        print(f"✅ {len(account_ids)} contas carregadas.")
        return account_ids
    except Exception as e:
        print(f"❌ Erro ao ler contas: {e}")
        exit(1)

def generate_transactions(account_ids, days_history=60):
    """Gera transações retroativas dia a dia."""
    transactions = []
    start_date = datetime.now() - timedelta(days=days_history)
    
    print(f"💸 Gerando transações para os últimos {days_history} dias...")

    for day in range(days_history):
        current_date = start_date + timedelta(days=day)
        
        # Sazonalidade: Mais transações no início do mês (dias 1-10)
        base_volume = random.randint(50, 200) 
        daily_volume = int(base_volume * 1.5) if current_date.day <= 10 else base_volume

        for _ in range(daily_volume):
            acc_id = random.choice(account_ids)
            t_type = random.choice(list(TransactionType))
            
            # Valores realistas
            if t_type == "PIX_IN":
                amount = round(random.uniform(10, 5000), 2)
            else:
                amount = round(random.uniform(5, 2000), 2)

            # Define contraparte (Banco externo ou interno)
            is_internal = random.random() > 0.7 
            bank = "LuisBank" if is_internal else random.choice(EXTERNAL_BANKS)

            # Data/Hora aleatória dentro do dia
            txn_date = current_date + timedelta(
                hours=random.randint(0, 23), 
                minutes=random.randint(0,59),
                seconds=random.randint(0,59)
            )

            txn = Transaction(
                account_id=acc_id,
                amount=amount,
                transaction_type=t_type,
                transaction_date=txn_date,
                counterparty_bank=bank,
                status="COMPLETED"
            )
            transactions.append(txn.model_dump(mode='json'))
            
    return transactions

def save_and_upload(data):
    filename = f"transactions_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    local_path = f"data/{filename}"
    s3_key = f"transactions/{filename}"

    # Garante diretório local
    os.makedirs('data', exist_ok=True)

    print(f"💾 Salvando {len(data)} transações...")
    with open(local_path, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')

    print(f"🚀 Enviando: s3://{BUCKET_NAME}/{s3_key}")
    try:
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        print("✅ Upload concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")

if __name__ == "__main__":
    ids = load_existing_account_ids()
    if ids:
        txns = generate_transactions(ids)
        save_and_upload(txns)