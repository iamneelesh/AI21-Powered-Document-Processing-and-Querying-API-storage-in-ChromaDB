import os
import uuid
import re
import requests
from flask import Flask, request, jsonify
import chromadb
import nltk
from nltk.tokenize import sent_tokenize


nltk.download('punkt', quiet=True)

app = Flask(__name__)

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection_name = "ai_collection"

ai21_api_key = "Your API key here"
ai21_url = "https://api.ai21.com/studio/v1/embed"
ai21_complete_url = "https://api.ai21.com/studio/v1/j2-ultra/complete"
embedding_dimension = 1024

def get_or_create_collection():
    collections = chroma_client.list_collections()
    if collection_name not in [c.name for c in collections]:
        return chroma_client.create_collection(name=collection_name, embedding_function=None)
    return chroma_client.get_collection(name=collection_name)

collection = get_or_create_collection()

def get_ai21_embeddings(texts, embed_type="segment"):
    headers = {
        "Authorization": f"Bearer {ai21_api_key}",
        "Content-Type": "application/json"
    }

    embeddings = []

    try:
        for text_segment in texts:
            data = {
                "texts": [text_segment],
                "type": embed_type,
                "embedding_dimension": embedding_dimension
            }
            response = requests.post(ai21_url, headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()

            if "results" in response_json and response_json["results"]:
                embeddings.append(response_json["results"][0]["embedding"])
            else:
                print(f"Unexpected AI21 response format: {response_json}")

    except Exception as e:
        print(f"Error in get_ai21_embeddings: {e}")

    return embeddings

def chunk_text(text, chunk_size=100):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) <= chunk_size:
            current_chunk += " " + sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def ai21_complete(prompt, max_tokens=100):
    headers = {
        "Authorization": f"Bearer {ai21_api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "numResults": 1,
        "maxTokens": max_tokens,
        "temperature": 0.7,
        "topKReturn": 0,
        "topP": 1,
        "countPenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "frequencyPenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "presencePenalty": {
            "scale": 0,
            "applyToNumbers": False,
            "applyToPunctuations": False,
            "applyToStopwords": False,
            "applyToWhitespaces": False,
            "applyToEmojis": False
        },
        "stopSequences":["↵↵"]
    }
    response = requests.post(ai21_complete_url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['completions'][0]['data']['text']

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        content = file.read().decode('utf-8')
        chunks = chunk_text(content)
        
        embeddings = get_ai21_embeddings(chunks)
        
        if len(chunks) != len(embeddings):
            return jsonify({"error": "Mismatch between chunks and embeddings"}), 500

        ids = [str(uuid.uuid4()) for _ in chunks]
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=ids
        )
        
        
        overview_prompt = f"Briefly summarize the following content in 2-3 sentences:\n\n{content[:1000]}..."
        overview = ai21_complete(overview_prompt, max_tokens=150)
        
        return jsonify({
            "message": "File processed and stored successfully",
            "overview": overview
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/query', methods=['POST'])
def query():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "No query provided"}), 400

    query_text = data['query']
    try:
        query_embedding = get_ai21_embeddings([query_text])[0]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        if results['documents'][0]:
            relevant_chunks = results['documents'][0]
            combined_text = " ".join(relevant_chunks)
            
           
            relevance_check_prompt = f"Given the following context:\n\n{combined_text}\n\nIs the question '{query_text}' relevant to this context? Answer with only 'Yes' or 'No'."
            relevance_response = ai21_complete(relevance_check_prompt, max_tokens=10).strip().lower()
            
            if relevance_response == 'yes':
               
                context = f"Based on the following information:\n\n{combined_text}\n\nProvide a detailed and enhanced answer to the question: {query_text}"
                answer = ai21_complete(context, max_tokens=250)
                
              
                enhancement_prompt = f"Enhance the following answer by adding more details, examples, or explanations if necessary:\n\n{answer}"
                enhanced_answer = ai21_complete(enhancement_prompt, max_tokens=300)
                
                return jsonify({
                    "answer": enhanced_answer
                }), 200
            else:
                return jsonify({"message": "The question is not relevant to the given context"}), 404
        else:
            return jsonify({"message": "No relevant information found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        content = file.read().decode('utf-8')
        summary_prompt = f"Provide a comprehensive summary of the following content in 5-7 sentences:\n\n{content[:2000]}..."
        summary = ai21_complete(summary_prompt, max_tokens=300)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return "Welcome to the AI21 Embedding and Query API!"

if __name__ == '__main__':
    app.run(debug=True)
