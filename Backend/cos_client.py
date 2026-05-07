# ═══════════════════════════════════════════════════════════════
# cos_client.py — All IBM COS operations
# ═══════════════════════════════════════════════════════════════

import ibm_boto3
from ibm_botocore.client import Config
import pandas as pd
import json
import io
import os

from config import (
    BUCKET, COS_ENDPOINT,
    COS_API_KEY, COS_INSTANCE_CRN,
    PRESIGNED_URL_EXPIRY
)

# ── Base URL for download endpoint ─────────────────────────────
# Change this when deployed to Code Engine
DOWNLOAD_BASE_URL = os.getenv(
    "DOWNLOAD_BASE_URL",
    "https://cu-backend.29ibyaelqfgx.us-south.codeengine.appdomain.cloud"
).rstrip("/")


def get_cos():
    """Returns a fresh COS client."""
    return ibm_boto3.client(
        "s3",
        ibm_api_key_id          = COS_API_KEY,
        ibm_service_instance_id = COS_INSTANCE_CRN,
        config                  = Config(signature_version="oauth"),
        endpoint_url            = COS_ENDPOINT
    )


def read_csv(key: str) -> pd.DataFrame:
    cos = get_cos()
    obj = cos.get_object(Bucket=BUCKET, Key=key)
    return pd.read_csv(io.BytesIO(obj["Body"].read()))


def read_json(key: str) -> dict:
    cos = get_cos()
    obj = cos.get_object(Bucket=BUCKET, Key=key)
    return json.loads(obj["Body"].read().decode())


def write_json(key: str, data: dict):
    cos = get_cos()
    cos.put_object(Bucket=BUCKET, Key=key, Body=json.dumps(data, indent=2).encode())


def write_csv(key: str, df: pd.DataFrame):
    cos = get_cos()
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    cos.put_object(Bucket=BUCKET, Key=key, Body=buf.getvalue().encode())


def upload_file(local_path: str, cos_key: str):
    cos = get_cos()
    cos.upload_file(local_path, BUCKET, cos_key)


def get_presigned_url(cos_key: str, expires: int = PRESIGNED_URL_EXPIRY) -> str:
    """
    Returns FastAPI download URL that streams file securely from COS.
    No public COS access required.
    """
    return f"{DOWNLOAD_BASE_URL}/download?key={cos_key}"


def list_objects(prefix: str = "") -> list:
    cos      = get_cos()
    response = cos.list_objects_v2(Bucket=BUCKET, Prefix=prefix)
    return [obj["Key"] for obj in response.get("Contents", [])]
