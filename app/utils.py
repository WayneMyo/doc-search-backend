from typing import List
from opensearchpy import OpenSearch

"""
Utility functions for the Doc-Search, including:

"""

class S3Util:
    def __init__(self, client):
        self.s3_client = client

    def upload_file(self, bucket: str, key: str, file):
        self.s3_client.upload_fileobj(file, bucket, key)
        s3_url = f"https://{bucket}.s3.amazonaws.com/{key}"
        return s3_url

    def get_file(self, bucket: str, key: str):
        return self.s3_client.get_object(Bucket=bucket, Key=key)

    def get_presigned_url(self, bucket: str, key: str):
        return self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": bucket, "Key": key}
        )

    def delete_file(self, bucket: str, key: str):
        self.s3_client.delete_object(Bucket=bucket, Key=key)

class OpenSearchUtil:
    def __init__(self, client: OpenSearch):
        self.opensearch_client = client

    def create_index_if_not_exists(self, index: str):
        if not self.opensearch_client.indices.exists(index=index):
            self.opensearch_client.indices.create(index=index, body={
                "mappings": {
                    "properties": {
                        "name": {"type": "text"},
                        "s3_url": {"type": "keyword"}
                    }
                }
            })

    def keyword_search(self, index: str, query: str) -> List[dict]:
        search_results = self.opensearch_client.search(index=index, body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["name"]
                }
            }
        })

        documents = []
        for hit in search_results["hits"]["hits"]:
            documents.append({
                "id": hit["_id"],
                "name": hit["_source"]["name"],
                "s3_url": hit["_source"]["s3_url"]
            })

        return documents