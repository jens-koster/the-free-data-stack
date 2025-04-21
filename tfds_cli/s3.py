import boto3
from botocore.exceptions import ClientError
from common import get_config


def get_s3_client():
    """Get an s3 client, implement the TFDS_S3NINJA_URL env to override the location from s3 config."""

    cfg = get_config("s3")
    cfg = cfg.get("config", {})
    url = cfg.get("url", None)
    if cfg is None or url is None:
        raise ValueError("s3 config not found")

    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        endpoint_url=cfg["url"],
    )
    return s3_client

def bucket_exists(bucket_name):
    response = get_s3_client().list_buckets()
    for bucket in response.get('Buckets', []):
        if bucket['Name'] == bucket_name:
            return True
    else:
        return False

def create_s3_bucket(bucket_name):
    """
    Create an S3 bucket

    Args:
        bucket_name (str): The name of the bucket to create.
    Returns:
        bool: True if the bucket was created successfully, False otherwise.
    """
    try:
        if bucket_exists(bucket_name):
            print(f"S3 bucket {bucket_name} already exists.")
            return True
        s3_client = get_s3_client()
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} created.")
        return True
    except ClientError as e:
        print(f"Error creating bucket: {e}")
        return False

if __name__ == '__main__':
    create_s3_bucket("data")