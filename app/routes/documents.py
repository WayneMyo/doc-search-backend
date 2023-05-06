from fastapi import APIRouter, File, UploadFile
from typing import List

from app.models import Document
from app.dependencies import create_s3_client, create_opensearch_client
from app.utils import S3Util, OpenSearchUtil
from config import settings

router = APIRouter(prefix="/v1/documents")

s3_bucket_name = settings.S3_BUCKET_NAME
s3_client = create_s3_client()
s3_util = S3Util(s3_client)

opensearch_host = settings.OPEN_SEARCH_HOST
opensearch_username = settings.OPEN_SEARCH_USERNAME
opensearch_password = settings.OPEN_SEARCH_PASSWORD
opensearch_index_name = settings.OPEN_SEARCH_INDEX_NAME
opensearch_client = create_opensearch_client(opensearch_host, opensearch_username, opensearch_password)
opensearch_util = OpenSearchUtil(opensearch_client)

@router.get("/", response_model=List[Document])
async def get_documents():
    # Fetch documents from OpenSearch and return them
    # Query all documents in the index
    documents = []
    search_results = opensearch_client.search(index=opensearch_index_name, body={"query": {"match_all": {}}}, scroll="1m", size=1000)
    scroll_id = search_results["_scroll_id"]

    while len(search_results["hits"]["hits"]) > 0:
        for hit in search_results["hits"]["hits"]:
            documents.append({
                "id": hit["_id"],
                "name": hit["_source"]["name"],
                "s3_url": hit["_source"]["s3_url"]
            })

        search_results = opensearch_client.scroll(scroll_id=scroll_id, scroll="1m")

    return documents

@router.post("/")
async def upload_document(document: UploadFile = File(...)):
    # Call utility function to create the index if it doesn't exist
    opensearch_util.create_index_if_not_exists(opensearch_index_name)

    # Upload to S3
    s3_key = document.filename
    s3_url = s3_util.upload_file(s3_bucket_name, s3_key, document.file)

    # Index the document in OpenSearch
    opensearch_client.index(index=opensearch_index_name, body={
        "name": document.filename,
        "s3_url": s3_url
    })

    return "Document uploaded successfully"

@router.get("/search", response_model=List[Document])
async def search_documents(query: str):
    # Perform keyword search
    documents = opensearch_util.keyword_search(opensearch_index_name, query)

    return documents
