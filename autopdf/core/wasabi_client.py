import boto3
import io
from core.config import settings
from botocore.exceptions import ClientError
from typing import Optional, List

class WasabiClient:
    def __init__(self) -> None:
        self.client = boto3.client(
            's3',
            endpoint_url=settings.wasabi_endpoint,
            aws_access_key_id=settings.wasabi_access_key,
            aws_secret_access_key=settings.wasabi_secret_key,
        )

    def upload_document(self, bucket_name: str, object_name: str, data: bytes) -> None:
        try:
            self.client.head_bucket(Bucket=bucket_name)
        except ClientError:
            self.client.create_bucket(Bucket=bucket_name,
                                      CreateBucketConfiguration={'LocationConstraint': 'us-east-2'})

        data_stream = io.BytesIO(data)
        self.client.upload_fileobj(data_stream, bucket_name, object_name)

    def get_document(self, bucket_name: str, object_name: str) -> bytes:
        try:
            response = self.client.get_object(Bucket=bucket_name, Key=object_name)
            return response['Body'].read()
        except ClientError as e:
            print(f"Error downloading from Wasabi: {e}")
            return b""

    def document_exists(self, bucket_name: str, object_name: str) -> bool:
        try:
            self.client.head_object(Bucket=bucket_name, Key=object_name)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            print(f"Error checking document existence: {e}")
            return False

    def list_objects(self, bucket_name: str, prefix: str = None, recursive: bool = False) -> List[str]:
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            params = {'Bucket': bucket_name}
            if prefix:
                params['Prefix'] = prefix
            if not recursive:
                params['Delimiter'] = '/'

            object_names = []
            for page in paginator.paginate(**params):
                if 'Contents' in page:
                    object_names.extend(obj['Key'] for obj in page['Contents'])
            return object_names
        except ClientError as e:
            print(f"Error listing objects in Wasabi: {e}")
            return []
