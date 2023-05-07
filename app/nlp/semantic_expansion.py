from transformers import pipeline

def sematic_expansion(query, model_type = 'gpt2'):
    additional_query = 'Expand the previous sentences to contain more details about its intention.'
    full_query = "'" + query + "'. " + additional_query
    result = full_query
    generator = pipeline('text-generation', model = model_type, max_length = len(full_query) * 2)
    generator.model.config.pad_token_id = generator.model.config.eos_token_id
    try:
        result = generator(full_query)
        result = result[0]['generated_text']
        if full_query in result:
            result = result[result.index(full_query) + len(full_query):].strip()
    except: 
        print("Error in generating response, return original query.")
        result = query
        
    return result