# RAG Integration Guide

This document explains how the Retrieval-Augmented Generation (RAG) system is built in this project, how to test it, and the core concepts behind it.

## What is RAG?

Retrieval-Augmented Generation combines two ideas:

- **Retrieval**: Search a set of documents or text chunks using vector similarity.
- **Generation**: Use an LLM to answer a question using the retrieved context.

The system stores document chunks with embeddings, finds the most relevant chunks for a question, and then asks a chat model to generate the answer using only that context.

## Project Files for RAG

- `services/rag_service.py`
  - Handles document ingestion, embedding creation, local vector storage, similarity search, and generation.
- `routes/rag_routes.py`
  - Implements the HTTP endpoints for ingesting documents and querying them.
- `config.py`
  - Loads environment variables and exposes `OPENAI_API_KEY` for the RAG system.
- `app.py`
  - Registers the RAG blueprint at `/rag` and integrates the routes into the Flask app.
- `instance/rag_store.json`
  - Local storage for ingested document chunks and their embeddings.

## How the RAG System is Built

### 1. Document Ingestion

When a document is ingested, the service:

1. Splits the text into smaller chunks.
2. Calls the OpenAI embedding API to create a vector for each chunk.
3. Saves the chunk text, title, and vector in a local JSON store.

This allows the system to later search for the most relevant chunks for a query.

### 2. Vector Search

For a query:

1. The query text is converted into an embedding vector.
2. The system computes cosine similarity between the query vector and each stored chunk vector.
3. It selects the top matching chunks (top K) as the retrieval context.

### 3. Answer Generation

The retrieved chunks are combined into a prompt.
The prompt tells the chat model:

- Use only the retrieved context.
- If the answer is not in the context, say `I don't know.`

Then it calls the OpenAI chat completion API and returns the answer with source snippets.

## Basic Concepts

### Embeddings

- Embeddings are numeric representations of text.
- Similar text has similar embedding vectors.
- In this project, OpenAI embedding model `text-embedding-3-small` is used.

### Vector Database / Store

- A vector database stores embeddings and enables similarity search.
- Here we use a small local store: `instance/rag_store.json`.
- This is enough for prototype and small datasets.

### Similarity Search

- The query embedding is compared to document chunk embeddings.
- Cosine similarity is used to rank relevance.
- The top results become the retrieval context.

### Retrieval-Augmented Generation

- The model does not hallucinate from unrelated knowledge.
- It answers using retrieved chunks from the actual documents.
- This makes answers grounded in the source text.

## Setup Instructions

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add environment variables

Create or update `.env` with:

```text
OPENAI_API_KEY=your_openai_api_key
GCP_BUCKET_NAME=your-gcp-bucket-name
SECRET_KEY=your_secret_key
```

### 3. Run the app

```bash
python app.py
```

The app will start on `http://127.0.0.1:5000` by default.

## API Endpoints

### Ingest a document

- `POST /rag/ingest`
- Requires admin authentication
- Accepts either:
  - multipart file upload (`file`)
  - JSON body with `title` and `text`

Example JSON request:

```json
{
  "title": "sales_document",
  "text": "This document explains sales targets, growth goals, and pricing strategy."
}
```

Example curl:

```bash
curl -X POST http://127.0.0.1:5000/rag/ingest \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"doc","text":"This is the document text."}'
```

### Query ingested documents

- `POST /rag/query`
- Requires authentication
- JSON body with `query`

Example request:

```json
{
  "query": "What does the document say about sales targets?"
}
```

Example curl:

```bash
curl -X POST http://127.0.0.1:5000/rag/query \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"What does the document say about sales targets?"}'
```

## Testing the RAG System

1. Start the Flask app.
2. Ingest a document with meaningful text.
3. Query the document for a specific question.
4. Verify the returned answer references the ingested content.

### Example

- Ingest text: `"Our product targets small retail customers and plans 20% growth in the next quarter."`
- Query: `"Who is the product targeting?"`
- Expected answer should mention `small retail customers`.

## Notes

- The current store is local and best for small proof-of-concept usage.
- For larger-scale use, you can replace the store with Pinecone, Chroma, or other vector DBs.
- The model is constrained by the retrieved context to reduce hallucinations.

## Next Improvements

- Add persistence using a real vector database
- Add document metadata and source tracking
- Add indexed chunking for better retrieval
- Add logging and error handling for OpenAI requests

---

This README focuses on the RAG portion only. Use it as a quick guide for how the system works and how to test it in this repository.
