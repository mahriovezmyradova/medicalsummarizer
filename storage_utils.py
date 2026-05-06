"""storage_utils.py

Helper to upload files to an S3-compatible bucket (Cloudflare R2 or S3).
Uses boto3. If R2 env vars/secrets are not set, returns local path.
"""
import os
from typing import Optional

try:
    import boto3
    from botocore.client import Config
    BOTO_AVAILABLE = True
except Exception:
    BOTO_AVAILABLE = False


def upload_file_to_r2(local_path: str, key: Optional[str] = None, bucket: Optional[str] = None) -> Optional[str]:
    """Upload local_path to R2/S3 and return the object URL or key.

    Environment variables expected (or set in Streamlit secrets):
    - R2_ENDPOINT (optional)
    - R2_ACCESS_KEY_ID
    - R2_SECRET_ACCESS_KEY
    - R2_BUCKET (optional)

    If boto3 isn't available or env vars missing, falls back to returning local_path.
    """
    if not BOTO_AVAILABLE:
        return local_path

    access_key = os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("AWS_SECRET_ACCESS_KEY")
    endpoint = os.environ.get("R2_ENDPOINT")
    bucket_name = bucket or os.environ.get("R2_BUCKET")

    if not (access_key and secret_key and bucket_name):
        return local_path

    session = boto3.session.Session()
    s3_client = session.client(
        "s3",
        region_name="auto",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4")
    )

    if key is None:
        key = os.path.basename(local_path)

    try:
        s3_client.upload_file(local_path, bucket_name, key)
        # Build a URL — Cloudflare R2 doesn't enable public URLs by default; this returns a signed URL if desired.
        # For simplicity return a path "s3://bucket/key"
        return f"s3://{bucket_name}/{key}"
    except Exception:
        return local_path
