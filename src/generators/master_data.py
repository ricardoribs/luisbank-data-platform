import os
import random
from datetime import datetime

from faker import Faker

from src.generators.models import Customer, Account, AccountType
from src.generators.utils import (
    build_s3_client,
    ensure_bucket_exists,
    get_logger,
    load_minio_settings,
    upload_file_with_retry,
    write_jsonl_atomic,
    write_to_dlq,
)


logger = get_logger(__name__)

faker = Faker("pt_BR")
NUM_CUSTOMERS = 100


def generate_customer_data():
    """Gera uma lista de clientes e suas respectivas contas."""
    customers = []
    accounts = []

    logger.info("Generating %s customers and linked accounts...", NUM_CUSTOMERS)

    for _ in range(NUM_CUSTOMERS):
        created_date = faker.date_time_between(start_date="-2y", end_date="now")

        cust = Customer(
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            email=faker.email(),
            cpf=faker.cpf(),
            created_at=created_date,
            updated_at=created_date,
            risk_profile=random.choice(["LOW", "MEDIUM", "HIGH"]),
        )
        customers.append(cust.model_dump(mode="json"))

        num_accounts = random.choices([1, 2], weights=[0.8, 0.2])[0]

        for _ in range(num_accounts):
            acc_type = random.choice(list(AccountType))
            acc = Account(
                customer_id=cust.id,
                account_number=str(faker.random_number(digits=6, fix_len=True)),
                balance=round(random.uniform(0, 15000), 2),
                account_type=acc_type,
                created_at=created_date,
            )
            accounts.append(acc.model_dump(mode="json"))

    return customers, accounts


def save_and_upload(data, entity_name, s3_client, bucket_name):
    """Salva localmente em JSONL e sobe para o MinIO com retry."""
    filename = f"{entity_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    local_path = os.path.join("data", filename)
    s3_key = f"{entity_name}/{filename}"

    logger.info("Saving %s records for %s...", len(data), entity_name)

    write_jsonl_atomic(data, local_path)

    try:
        upload_file_with_retry(s3_client, local_path, bucket_name, s3_key, logger)
        logger.info("Upload completed.")
    except Exception as exc:
        write_to_dlq(local_path, f"upload_failed:{exc}", logger)
        raise


if __name__ == "__main__":
    settings = load_minio_settings()
    s3_client = build_s3_client(settings)

    ensure_bucket_exists(s3_client, settings.bucket, logger)

    customers_data, accounts_data = generate_customer_data()

    save_and_upload(customers_data, "customers", s3_client, settings.bucket)
    save_and_upload(accounts_data, "accounts", s3_client, settings.bucket)
