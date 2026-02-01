import json
import logging
import os
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Iterator

import boto3
from botocore.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log


@dataclass(frozen=True)
class MinioSettings:
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str


def get_logger(name: str) -> logging.Logger:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(name)


def load_minio_settings() -> MinioSettings:
    endpoint = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
    access_key = os.getenv("MINIO_ROOT_USER")
    secret_key = os.getenv("MINIO_ROOT_PASSWORD")
    bucket = os.getenv("MINIO_BUCKET", "landing-zone")

    if not access_key or not secret_key:
        raise ValueError(
            "MINIO_ROOT_USER and MINIO_ROOT_PASSWORD must be set (use .env)."
        )

    return MinioSettings(
        endpoint=endpoint,
        access_key=access_key,
        secret_key=secret_key,
        bucket=bucket,
    )


def build_s3_client(settings: MinioSettings):
    return boto3.client(
        "s3",
        endpoint_url=settings.endpoint,
        aws_access_key_id=settings.access_key,
        aws_secret_access_key=settings.secret_key,
    )


def _retry(logger: logging.Logger):
    return retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
    )


def ensure_bucket_exists(s3_client, bucket_name: str, logger: logging.Logger) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        logger.warning("Bucket '%s' not found. Creating...", bucket_name)
        try:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info("Bucket '%s' created.", bucket_name)
        except Exception as exc:
            logger.error("Failed to create bucket: %s", exc)
            raise


@_retry(get_logger(__name__))
def upload_file_with_retry(s3_client, local_path: str, bucket: str, key: str, logger: logging.Logger) -> None:
    logger.info("Uploading to s3://%s/%s", bucket, key)
    s3_client.upload_file(local_path, bucket, key)


@_retry(get_logger(__name__))
def list_objects_with_retry(s3_client, bucket: str, prefix: str):
    return s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)


@_retry(get_logger(__name__))
def get_object_with_retry(s3_client, bucket: str, key: str):
    return s3_client.get_object(Bucket=bucket, Key=key)


def write_jsonl_atomic(records: Iterable[dict], local_path: str) -> None:
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    temp_path = f"{local_path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")
    os.replace(temp_path, local_path)


def iter_jsonl_streaming(body) -> Iterator[dict]:
    try:
        import ijson

        for record in ijson.items(body, "", multiple_values=True):
            if record is None:
                continue
            yield record
    except Exception:
        for line in body.iter_lines():
            if not line:
                continue
            yield json.loads(line.decode("utf-8"))


def write_to_dlq(local_path: str, reason: str, logger: logging.Logger) -> str:
    dlq_dir = os.path.join("data", "dlq")
    os.makedirs(dlq_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    dlq_name = f"{os.path.basename(local_path)}.{timestamp}.dlq"
    dlq_path = os.path.join(dlq_dir, dlq_name)
    shutil.copy2(local_path, dlq_path)
    logger.error("Written to DLQ (%s): %s", reason, dlq_path)
    return dlq_path
