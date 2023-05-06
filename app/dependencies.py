import boto3
from opensearchpy import OpenSearch

"""
Dependencies for the FastAPI application, including:
"""

def create_s3_client():
    return boto3.client("s3")

def create_opensearch_client(opensearch_host: str, username: str, password: str):
    return OpenSearch(
        hosts=[opensearch_host],
        http_auth=(username, password),
    )
