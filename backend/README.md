# GovAssist Backend

GovAssist is a student project that uses a retrieval-augmented generation (RAG) pipeline to answer government-service questions grounded in official PDF documents and structured service metadata.

## Overview

The backend is built with Flask and exposes REST APIs for:

- government service discovery
- document upload and indexing
- ChromaDB-backed retrieval
- LLM-based answer generation
- chat history storage

## Architecture

- Flask routes: API handling
- Services: business logic
- RAG: PDF loading, cleaning, chunking, embeddings, retrieval, prompt creation, generation
- PostgreSQL: structured service and chat data
- ChromaDB: persistent vector search

## Python environment

Create and activate a local virtual environment in PowerShell:

```powershell
cd C:\Users\acer\GovAssist\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## PostgreSQL setup

1. Install PostgreSQL.
2. Create a database named `govassist`.
3. Update your `.env` file using `.env.example`.

Example:

```powershell
$env:DATABASE_URL="postgresql://postgres:postgres@localhost:5432/govassist"
```

## Environment variables

Copy `.env.example` to `.env` and adjust values:

```powershell
Copy-Item .env.example .env
```

Required variables:

- `DATABASE_URL`
- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `CHROMA_PERSIST_DIRECTORY`
- `EMBEDDING_MODEL`
- `TOP_K`
- `CHUNK_SIZE`
- `CHUNK_OVERLAP`

## Initialize database

```powershell
python -c "from database.connection import Base, engine; from database.seed import seed_database; Base.metadata.create_all(bind=engine); seed_database(); print('DB ready')"
```

or run:

```powershell
python scripts\initialize_database.py
```

## Add government PDFs

Place documents under:

```text
backend\data\documents\agriculture\
backend\data\documents\education\
backend\data\documents\welfare\
backend\data\documents\employment\
backend\data\documents\subsidies\
```

For development samples, add a clear notice such as:

"DEVELOPMENT SAMPLE — NOT OFFICIAL GOVERNMENT DATA"

## Run ingestion

```powershell
python scripts\ingest_documents.py
```

This extracts PDFs, cleans text, chunks it, embeds the chunks, and stores them in ChromaDB.

## Run Flask

```powershell
python app.py
```

The app starts on:

```text
http://localhost:5000
```

## API endpoints

### Health

- GET `/api/health`

### Services

- GET `/api/services`
- GET `/api/services/`
- GET `/api/services?category=Agriculture`
- GET `/api/categories`

### Chat

- POST `/api/chat`

Example request:

```json
{
  "message": "Who is eligible for PM-KISAN?",
  "language": "en"
}
```

### Documents

- POST `/api/documents/upload`
- POST `/api/documents/index`

## Testing with curl

```powershell
curl http://localhost:5000/api/health

curl http://localhost:5000/api/services

curl -X POST http://localhost:5000/api/chat -H "Content-Type: application/json" -d '{"message":"Who is eligible for PM-KISAN?","language":"en"}'
```

## Frontend integration

Use fetch to call the backend:

```javascript
fetch("http://localhost:5000/api/chat", {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    message: userMessage,
    language: "en"
  })
})
.then(res => res.json())
.then(data => {
  if (data.success) {
    // Replace placeholder assistant output with data.answer
    console.log(data.answer);
    console.log(data.sources);
  }
});
```

## Troubleshooting

- If PostgreSQL is not running, start it and verify the database name and credentials.
- If ChromaDB indexing fails, confirm the PDF files exist and the embedding model can load.
- If LLM calls fail, set `LLM_API_KEY` and verify the provider is configured.
- If the app says the LLM is not configured, it is working as designed for a local setup without credentials.

## RAG workflow

Question -> query embedding -> ChromaDB retrieval -> relevant chunks -> LLM prompt -> grounded answer -> source metadata

## Notes

- This is the 50% core implementation focused on a working backend architecture.
- LLM calls require a provider key when enabled.
- The application is intentionally structured so the LLM provider can be replaced without rewriting the RAG flow.
