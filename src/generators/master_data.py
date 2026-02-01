import os
import json
import random
import boto3
from botocore.exceptions import ClientError # Importante para tratar erros
from faker import Faker
from datetime import datetime
from models import Customer, Account, AccountType

# Configuração
faker = Faker('pt_BR')
NUM_CUSTOMERS = 100
MINIO_ENDPOINT = "http://localhost:9000"
ACCESS_KEY = "admin"
SECRET_KEY = "password123"
BUCKET_NAME = "landing-zone"

# Cliente S3 (MinIO)
s3_client = boto3.client(
    's3',
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

def ensure_bucket_exists(bucket_name):
    """Verifica se o bucket existe, se não, cria. (Idempotência)"""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        print(f"⚠️ Bucket '{bucket_name}' não encontrado. Criando agora...")
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' criado com sucesso!")
        except Exception as e:
            print(f"❌ Erro fatal ao criar bucket: {e}")
            raise

def generate_customer_data():
    """Gera uma lista de clientes e suas respectivas contas."""
    customers = []
    accounts = []

    print(f"🔄 Gerando {NUM_CUSTOMERS} clientes e contas vinculadas...")

    for _ in range(NUM_CUSTOMERS):
        created_date = faker.date_time_between(start_date='-2y', end_date='now')
        
        cust = Customer(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            cpf=faker.cpf(),
            created_at=created_date,
            updated_at=created_date,
            risk_profile=random.choice(['LOW', 'MEDIUM', 'HIGH'])
        )
        customers.append(cust.model_dump(mode='json'))

        num_accounts = random.choices([1, 2], weights=[0.8, 0.2])[0]
        
        for _ in range(num_accounts):
            acc_type = random.choice(list(AccountType))
            acc = Account(
                customer_id=cust.id,
                account_number=str(faker.random_number(digits=6, fix_len=True)),
                balance=round(random.uniform(0, 15000), 2),
                account_type=acc_type,
                created_at=created_date
            )
            accounts.append(acc.model_dump(mode='json'))

    return customers, accounts

def save_and_upload(data, entity_name):
    """Salva localmente em JSONL e sobe para o MinIO"""
    filename = f"{entity_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    local_path = f"data/{filename}"
    s3_key = f"{entity_name}/{filename}"

    os.makedirs('data', exist_ok=True)

    print(f"💾 Salvando {len(data)} registros de {entity_name}...")
    
    with open(local_path, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record) + '\n')

    print(f"🚀 Enviando para o Data Lake: s3://{BUCKET_NAME}/{s3_key}")
    try:
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        print("✅ Upload concluído com sucesso!")
    except Exception as e:
        print(f"❌ Erro no upload: {e}")

if __name__ == "__main__":
    # 1. Garantir que o bucket existe antes de tudo
    ensure_bucket_exists(BUCKET_NAME)

    # 2. Gerar dados
    customers_data, accounts_data = generate_customer_data()

    # 3. Upload
    save_and_upload(customers_data, "customers")
    save_and_upload(accounts_data, "accounts")