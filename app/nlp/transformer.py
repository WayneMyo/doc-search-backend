import torch
from transformers import AutoTokenizer, AutoModel
from scipy.spatial.distance import cdist
import numpy as np

def textEncoder(text):
    # Initialize BERT tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")

    # Tokenize text
    input_ids = tokenizer.encode(text, return_tensors="pt")

    # Encode text using BERT model
    with torch.no_grad():
        outputs = model(input_ids)
        encoded_text = outputs.last_hidden_state[:, 0, :].numpy()

    return encoded_text


def searchDocuments(esClient, encoded_question):
    # Search for all documents in Elastic Search
    results = esClient.search(index="documents", body={
        "query": {
            "match_all": {}
        }
    })

    # Compute distances between encoded question and encoded documents
    distances = []
    for hit in results["hits"]["hits"]:
        encoded_text = np.array(hit["_source"]["encoded_text"])
        distance = cdist(encoded_question, encoded_text, metric="cosine")[0][0]
        distances.append((hit, distance))

    # Sort documents by distance
    distances.sort(key=lambda x: x[1])

    # Return the most similar document
    return distances[0][0]