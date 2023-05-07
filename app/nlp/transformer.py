import torch
from transformers import AutoTokenizer, AutoModel, BertTokenizer, BertForMaskedLM, AutoModelForSeq2SeqLM
from scipy.spatial.distance import cdist
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


def expandQuery(question: str) -> str:
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

    # Compute distances between encoded question and encoded documents
    distances = []
    for hit in results["hits"]["hits"]:
        encoded_text = np.array(hit["_source"]["encoded_text"])
        distance = cdist(encoded_question, encoded_text, metric="cosine")[0][0]
        distances.append((hit, distance))

    # Sort documents by distance
    distances.sort(key=lambda x: x[1])
    return distances[:5] if distances else None

def getSummary(doc, question):
    # Initialize the tokenizer and the model
    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("t5-small")

    # Generate a prompt for the T5 model
    prompt = "answer: "

    # Get the text of the document
    text = doc["_source"]["text"]

    # Split the text into 512-token chunks
    chunk_size = 512
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    # Summarize each chunk separately
    summaries = []
    for chunk in chunks:
        # Encode the prompt and the chunk of text
        input_ids = tokenizer.encode(prompt + question + "context: " + chunk, return_tensors="pt")

        # Generate a summary of the chunk using the T5 model
        summary_ids = model.generate(input_ids=input_ids, max_length=100, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Clear the PyTorch cache
        torch.cuda.empty_cache()

        summaries.append(summary)

    # Join the summaries together
    summary = " ".join(summaries)

    return summary
