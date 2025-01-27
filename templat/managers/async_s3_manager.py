from os import PathLike
from pathlib import Path
from typing import Union

import aiobotocore.session
import aiofiles
from aiobotocore.client import AioBaseClient

from templat.core.settings import settings


class AsyncS3Manager:
    def __init__(
        self,
        s3_access_key_id: str = settings.S3_ACCESS_ID,
        s3_secret_access_key: str = settings.S3_SECRET_KEY,
        region_name: str = "auto",
        endpoint_url: str = settings.S3_BUCKET_URL,
    ):
        self.s3_access_key_id = s3_access_key_id
        self.s3_secret_access_key = s3_secret_access_key
        self.region_name = region_name
        self.endpoint_url = endpoint_url
        self.session = aiobotocore.session.get_session()

    async def _create_client(self) -> AioBaseClient:
        return self.session.create_client(
            service_name="s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.s3_access_key_id,
            aws_secret_access_key=self.s3_secret_access_key,
            region_name=self.region_name,
        )

    async def create_bucket(self, bucket_name: str):
        async with await self._create_client() as client:
            await client.create_bucket(Bucket=bucket_name)

    async def bucket_exists(self, bucket_name: str) -> bool:
        async with await self._create_client() as client:
            response = await client.list_buckets()
            buckets = [bucket["Name"] for bucket in response["Buckets"]]
            return bucket_name in buckets

    async def put_object(self, bucket_name: str, key: str, data: bytes) -> dict:
        async with await self._create_client() as client:
            resp = await client.put_object(Bucket=bucket_name, Key=key, Body=data)
            return resp

    async def fput_object(self, bucket_name: str, key: str, file_path: Union[str, PathLike, Path]) -> dict:
        async with aiofiles.open(file_path, "rb") as file:
            file_data = await file.read()
        return await self.put_object(bucket_name, key, file_data)

    async def get_object(self, bucket_name: str, key: str) -> dict:
        async with await self._create_client() as client:
            response = await client.get_object(Bucket=bucket_name, Key=key)
            async with response["Body"] as stream:
                data = await stream.read()
            return {
                "Content": data,
                "ContentType": response.get("ContentType", "application/octet-stream"),
            }

    async def delete_object(self, bucket_name: str, key: str) -> dict:
        async with await self._create_client() as client:
            resp = await client.delete_object(Bucket=bucket_name, Key=key)
            return resp

    async def list_objects(self, bucket_name: str, prefix: str = "") -> list:
        async with await self._create_client() as client:
            paginator = client.get_paginator("list_objects")
            objects = []
            async for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
                for obj in page.get("Contents", []):
                    objects.append(obj)
            return objects

    async def delete_folder(self, bucket_name: str, folder_name: str) -> None:
        async with await self._create_client() as client:
            if not folder_name.endswith("/"):
                folder_key = f"{folder_name}/"

            objects = await self.list_objects(bucket_name, "test1")
            if not objects:
                return await client.delete_object(Bucket=bucket_name, Key=folder_key)

            delete_requests = [{"Key": obj["Key"]} for obj in objects]

            return await client.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_requests})

    async def generate_download_link(self, bucket_name: str, key: str, expires_in: int = 3600) -> str:
        async with await self._create_client() as client:
            donwload_link = await client.generate_presigned_url(
                "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=expires_in
            )
            return donwload_link
