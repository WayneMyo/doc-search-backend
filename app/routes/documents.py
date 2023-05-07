from fastapi import APIRouter, File, Query, UploadFile
from typing import List

from app.models import Document
from app.dependencies import create_s3_client, create_opensearch_client
from app.utils import S3Util, OpenSearchUtil
from config import settings

from io import BytesIO

# nlp models
from app.nlp.spacy import spacyModel
from app.nlp.transformer import textEncoder, searchDocuments, getSummary
from app.nlp.semantic_expansion import sematic_expansion

"""
Routes for the Doc-Search application, including:
- get_documents: Get all documents from OpenSearch
- upload_document: Upload a document to S3 and index it in OpenSearch
- search_documents: Search documents in OpenSearch
"""

router = APIRouter(prefix="/v1/documents")

s3_bucket_name = settings.S3_BUCKET_NAME
s3_client = create_s3_client()
s3_util = S3Util(s3_client)

# Constants
INDEX = settings.OPEN_SEARCH_INDEX_NAME

esClient = create_opensearch_client(
    settings.OPEN_SEARCH_HOST,
    settings.OPEN_SEARCH_USERNAME,
    settings.OPEN_SEARCH_PASSWORD
)
esUtil = OpenSearchUtil(esClient)

@router.get("/", response_model=List[Document])
async def get_documents():
    # Fetch documents from OpenSearch and return them
    # Query all documents in the index
    documents = []
    search_results = esClient.search(index=INDEX, body={"query": {"match_all": {}}}, scroll="1m", size=1000)
    scroll_id = search_results["_scroll_id"]

    while len(search_results["hits"]["hits"]) > 0:
        for hit in search_results["hits"]["hits"]:
            documents.append({
                "id": hit["_id"],
                "filename": hit["_source"]["name"],
                "s3_url": hit["_source"]["s3_url"]
            })

        search_results = esClient.scroll(scroll_id=scroll_id, scroll="1m")

    return documents

@router.post("/")
async def upload_document(document: UploadFile = File(...)):
    # for some reason, importing above causes an error to fastapi
    from docx import Document

    # Call utility function to create the index if it doesn't exist
    esUtil.create_index_if_not_exists(INDEX)

    # Extract text from document
    contents = await document.read()
    file = BytesIO(contents)
    doc = Document(file)
    text = ''
    for paragraph in doc.paragraphs:
        text += paragraph.text + " "

    text = text.replace('\t', ' ').replace('\n', ' ')
    text = text.strip()

    # Extract entities
    doc = spacyModel(text)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)

    # Encode text using BERT model
    encoded_text = textEncoder(text)

    # Upload to S3
    s3_key = document.filename
    s3_url = s3_util.upload_file(s3_bucket_name, s3_key, document.file)

    # Store document and entities in Elastic Search
    body = {
        "text": text,
        "encoded_text": encoded_text.tolist(),
        "filename": document.filename,
        "s3_url": s3_url
    }

    for key, value in entities.items():
        body[key] = value

    esClient.index(index="documents", body=body)

    return "Document uploaded successfully"

@router.get("/search")
async def search_doc(question: str = Query(...)):
    # IDK yet, sometimes it failed. So I just catch the error
    # and use default question if it failed to expand
    # q = None
    # try:
    #     q = expandQuery(question)
    # except:
    #     q = question

    # Expand the question
    expanded_question = sematic_expansion(question)

    result = searchDocuments(esClient, question)
    expanded_result = searchDocuments(esClient, expanded_question)

    result_filenames = [x[0]["_source"]["filename"] for x in result]

    # Combine two results if result["_source"]["filename"] is not in result_filenames
    if expanded_result:
        for r in expanded_result:
            if r[0]["_source"]["filename"] not in result_filenames:
                result.append(r)

    if not result:
        return {
            "documents": [],
        }
    
    documents = []
    documentsToSummaries = []
    
    for r, distance in result:
        documentsToSummaries.append(r)
        documents.append({
            "id": r["_id"],
            "filename": r["_source"]["filename"],
            "s3_url": r["_source"].get("s3_url", None),
            "distance": distance
        })


    # Generate sumamry for user question
    summary = getSummary(documentsToSummaries[0], question)

    return {
        "documents": documents,
        "summary": summary
    }

@router.delete("/purge/docs")
async def delete_docs():
    esClient.delete_by_query(
        index="documents",
        body={
            "query": {
                "match_all": {}
            }
        }
    )
    return "Deleted all documents"
