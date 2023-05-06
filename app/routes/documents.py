from fastapi import APIRouter, File, UploadFile
from typing import List

from app.models import Document

router = APIRouter(prefix="/v1/documents")

@router.get("/", response_model=List[Document])
async def get_documents():
    # Fetch documents from Elasticsearch and return them
    return [{
        "id": "1",
        "name": "List: Document 1",
        "s3_url": "https://s3.amazonaws.com/bucket-name/document-1.pdf",
    }]

@router.post("/")
async def upload_document(document: UploadFile = File(...)):
    # Upload the document to S3 and index it in Elasticsearch
    return 'Document uploaded successfully'

@router.get("/search", response_model=List[Document])
async def search_documents(query: str):
    # Perform search query on Elasticsearch and return the matching documents
    return [{
        "id": "1",
        "name": "Search: Document 1",
        "s3_url": "https://s3.amazonaws.com/bucket-name/document-1.pdf",
    }]
