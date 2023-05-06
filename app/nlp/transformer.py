import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertForMaskedLM
from scipy.spatial.distance import cdist, euclidean
import numpy as np

from app.nlp.spacy import spacyModel

def textEncoder(text):
    # Initialize BERT tokenizer and model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
    model = AutoModel.from_pretrained("bert-base-uncased")

    # Split text into chunks
    max_length = tokenizer.model_max_length
    text_chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]

    # Encode each chunk separately
    encoded_chunks = []
    for chunk in text_chunks:
        # Tokenize chunk
        input_ids = tokenizer.encode(chunk, return_tensors="pt")

        # Encode chunk using BERT model
        with torch.no_grad():
            outputs = model(input_ids)
            encoded_chunk = outputs.last_hidden_state[:, 0, :].numpy()
            encoded_chunks.append(encoded_chunk)

    # Combine encoded vectors
    encoded_text = np.mean(encoded_chunks, axis=0)

    return encoded_text


def expandQuestion(question: str) -> str:
    # Load pre-trained BERT tokenizer and model
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForMaskedLM.from_pretrained('bert-base-uncased')

    # Tokenize the question
    input_ids = tokenizer.encode(question, return_tensors='pt')

    # Generate predictions for masked token
    mask_token_index = 5
    input_ids[0][mask_token_index] = tokenizer.mask_token_id
    with torch.no_grad():
        output = model(input_ids)

    # Get the top 5 predicted tokens
    predicted_token_ids = output[0][0][mask_token_index].topk(5).indices.tolist()
    predicted_tokens = [tokenizer.decode([token_id]) for token_id in predicted_token_ids]

    # Expand the question with the predicted tokens
    expanded_question = question + ' ' + ' '.join(predicted_tokens)

    return expanded_question


def searchDocuments(esClient, question):
    # Encode question
    encoded_question = textEncoder(question)

    # Extract entities from question
    doc = spacyModel(question)
    entities = {}
    for ent in doc.ents:
        if ent.label_ not in entities:
            entities[ent.label_] = []
        entities[ent.label_].append(ent.text)

    print(entities)

    # Build Elastic Search query
    query = {
        "query": {
            "bool": {
                "should": []
            }
        }
    }
    for entity_type, entity_values in entities.items():
        for entity_value in entity_values:
            query["query"]["bool"]["should"].append({
                "match_phrase": {
                    entity_type: entity_value
                }
            })

    # Search for all documents in Elastic Search
    results = esClient.search(index="documents", body=query)

    print(query)

    # Compute distances between encoded question and encoded documents
    distances = []
    for hit in results["hits"]["hits"]:
        encoded_text = np.array(hit["_source"]["encoded_text"])
        distance = cdist(encoded_question, encoded_text, metric="cosine")[0][0]
        # distance = euclidean(encoded_question, encoded_text)
        distances.append((hit, distance))

    # Sort documents by distance
    distances.sort(key=lambda x: x[1])

    # Print the distances
    print("\n=============\nDistances:")
    for d in distances:
        print(d[0]["_source"]["filename"], d[1])

    # Return the most similar document
    return distances[0][0] if distances else None