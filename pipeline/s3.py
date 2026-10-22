"""Accès au S3 local (SeaweedFS) avec boto3, la librairie S3 d'AWS."""

import os
from pathlib import Path

import boto3

BUCKET = "transactions"


def client_s3():
    return boto3.client(
        "s3",
        endpoint_url=os.environ.get("S3_ENDPOINT_URL", "http://localhost:8333"),
        aws_access_key_id=os.environ.get("S3_ACCESS_KEY", "pipeline"),
        aws_secret_access_key=os.environ.get("S3_SECRET_KEY", "pipeline-secret"),
        region_name="us-east-1",
    )


def creer_bucket(s3) -> None:
    buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    if BUCKET not in buckets:
        s3.create_bucket(Bucket=BUCKET)


def deposer_fichier(s3, chemin: Path) -> None:
    s3.upload_file(str(chemin), BUCKET, chemin.name)


def lister_csv(s3) -> list[str]:
    objets = s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    return sorted(o["Key"] for o in objets if o["Key"].endswith(".csv"))
