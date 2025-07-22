from minio import Minio, S3Error
import os
from typing import List, Optional


class MinioManager:
    def __init__(
        self, endpoint: str, access_key: str, secret_key: str, secure: bool = True
    ) -> None:
        self.client: Minio = Minio(
            endpoint, access_key=access_key, secret_key=secret_key, secure=secure
        )

    def bucket_exists(self, bucket_name: str) -> bool:
        return self.client.bucket_exists(bucket_name)

    def make_bucket(self, bucket_name: str) -> None:
        if not self.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)

    def upload_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            self.make_bucket(bucket_name)
            self.client.fput_object(bucket_name, object_name, file_path)
            print(
                f"Archivo '{file_path}' subido como '{object_name}' en el bucket '{bucket_name}'."
            )
        except S3Error as err:
            print(f"Error al subir archivo: {err}")

    def download_file(self, bucket_name: str, object_name: str, file_path: str) -> None:
        try:
            self.client.fget_object(bucket_name, object_name, file_path)
            print(f"Archivo '{object_name}' descargado a '{file_path}'.")
        except S3Error as err:
            print(f"Error al descargar archivo: {err}")

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        try:
            self.client.remove_object(bucket_name, object_name)
            print(f"Archivo '{object_name}' eliminado del bucket '{bucket_name}'.")
        except S3Error as err:
            print(f"Error al eliminar archivo: {err}")

    def list_files(self, bucket_name: str, prefix: Optional[str] = None) -> List[str]:
        try:
            objects = self.client.list_objects(
                bucket_name, prefix=prefix, recursive=True
            )
            return [obj.object_name for obj in objects]
        except S3Error as err:
            print(f"Error al listar archivos: {err}")
            return []
