import io
from minio import Minio
from minio.error import S3Error
from fastapi import HTTPException


class MinioService:

    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str,
    ):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False,
            region=region,
        )
        self.bucket_name = bucket_name

    def upload_image(self, file_path, file_contents) -> str:
        try:
            self.client.put_object(
                self.bucket_name,
                file_path,
                io.BytesIO(file_contents),
                len(file_contents),
            )
            return file_path
        except S3Error as e:
            raise HTTPException(
                status_code=500, detail=f"Error uploading image: {str(e)}"
            )

    def delete_image(self, object_name: str) -> None:
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as e:
            raise HTTPException(
                status_code=500, detail=f"Error deleting image: {str(e)}"
            )

    def check_file_exists(self, object_name: str) -> bool:
        try:
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error as e:
            return False
