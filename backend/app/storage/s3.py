import asyncio
from typing import BinaryIO
from app.storage.base import StorageBackend
from app.config import settings


class S3Storage(StorageBackend):
    def __init__(self):
        if not settings.aws_bucket:
            raise ValueError("AWS_BUCKET must be set when STORAGE_BACKEND=s3")
        self.bucket = settings.aws_bucket
        self.region = settings.aws_region or "us-east-1"

    def _client(self):
        import boto3
        return boto3.client("s3", region_name=self.region)

    async def put(self, key: str, content: BinaryIO, content_type: str = "") -> str:
        client = self._client()
        body = content.read()
        await asyncio.to_thread(
            client.put_object,
            Bucket=self.bucket,
            Key=key,
            Body=body,
            ContentType=content_type or "application/octet-stream",
        )
        return key

    async def get(self, key: str) -> bytes | None:
        from botocore.exceptions import ClientError
        client = self._client()
        try:
            resp = await asyncio.to_thread(
                client.get_object,
                Bucket=self.bucket,
                Key=key,
            )
            return resp["Body"].read()
        except ClientError as e:
            if e.response.get("Error", {}).get("Code") == "NoSuchKey":
                return None
            raise

    async def delete(self, key: str) -> bool:
        client = self._client()
        try:
            await asyncio.to_thread(client.delete_object, Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
