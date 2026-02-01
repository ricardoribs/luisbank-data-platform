import os
import random
from datetime import datetime, timedelta

from faker import Faker

from src.generators.models import Transaction, TransactionType
from src.generators.utils import (
    build_s3_client,
    get_logger,
    iter_jsonl_streaming,
    list_objects_with_retry,
    load_minio_settings,
    upload_file_with_retry,
    write_jsonl_atomic,
    write_to_dlq,
    get_object_with_retry,
)


logger = get_logger(__name__)

faker = Faker("pt_BR")

EXTERNAL_BANKS = [
    "Banco do Brasil",
    "Itau Unibanco",
    "Bradesco",
    "Caixa Economica",
    "Nubank",
    "Banco Inter",
    "Santander",
    "C6 Bank",
    "BTG Pactual",
    "Neon",
]


def load_existing_account_ids(s3_client, bucket_name: str):
    """Baixa o arquivo de contas mais recente do MinIO para pegar IDs validos."""
    logger.info("Loading existing accounts from Data Lake...")
    response = list_objects_with_retry(s3_client, bucket_name, "accounts/")
    if "Contents" not in response:
        raise RuntimeError("No accounts found. Run master_data.py first.")

    last_file = sorted(response["Contents"], key=lambda x: x["Key"])[-1]["Key"]
    logger.info("Reading file: %s", last_file)

    obj = get_object_with_retry(s3_client, bucket_name, last_file)

    account_ids = []
    for record in iter_jsonl_streaming(obj["Body"]):
        if "id" in record:
            account_ids.append(record["id"])

    logger.info("Loaded %s accounts.", len(account_ids))
    return account_ids


def generate_transactions(account_ids, days_history=60):
    """Gera transacoes retroativas dia a dia."""
    transactions = []
    start_date = datetime.now() - timedelta(days=days_history)

    logger.info("Generating transactions for the last %s days...", days_history)

    for day in range(days_history):
        current_date = start_date + timedelta(days=day)

        base_volume = random.randint(50, 200)
        daily_volume = int(base_volume * 1.5) if current_date.day <= 10 else base_volume

        for _ in range(daily_volume):
            acc_id = random.choice(account_ids)
            t_type = random.choice(list(TransactionType))

            if t_type == "PIX_IN":
                amount = round(random.uniform(10, 5000), 2)
            else:
                amount = round(random.uniform(5, 2000), 2)

            is_internal = random.random() > 0.7
            bank = "LuisBank" if is_internal else random.choice(EXTERNAL_BANKS)

            txn_date = current_date + timedelta(
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
                seconds=random.randint(0, 59),
            )

            txn = Transaction(
                account_id=acc_id,
                amount=amount,
                transaction_type=t_type,
                transaction_date=txn_date,
                counterparty_bank=bank,
                status="COMPLETED",
            )
            transactions.append(txn.model_dump(mode="json"))

    return transactions


def save_and_upload(data, s3_client, bucket_name: str):
    filename = f"transactions_{datetime.now().strftime('%Y%m%d%H%M%S')}.jsonl"
    local_path = os.path.join("data", filename)
    s3_key = f"transactions/{filename}"

    logger.info("Saving %s transactions...", len(data))
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

    ids = load_existing_account_ids(s3_client, settings.bucket)
    if ids:
        txns = generate_transactions(ids)
        save_and_upload(txns, s3_client, settings.bucket)
