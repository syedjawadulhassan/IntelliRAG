# IntelliRAG — AI-Powered Document Intelligence System

IntelliRAG is a Retrieval-Augmented Generation (RAG) system that turns your documents into a searchable, question-answerable knowledge base. It combines LangChain, Chroma, and Whoosh with a FastAPI backend and a Streamlit frontend to deliver accurate, source-cited answers from your own document corpus.

This project demonstrates a complete, production-style RAG pipeline. It supports ingesting documents from PDF folders or JSON files, generating embeddings, storing vectors in Chroma, indexing text in Whoosh, and serving queries via an API or an interactive Streamlit UI.


## 1. Overview

**Goal**: Turn a collection of documents into an intelligent, queryable knowledge base using open-source RAG components.

How it works:

- Load documents from demo_corpus/sample_docs.json (or your own PDFs/JSON).

- Generate embeddings and store them in a Chroma vector database.

- Create a Whoosh keyword index for fast text lookup.

- Expose a query API through FastAPI.

- Interact with the system through the IntelliRAG Streamlit frontend.

### Why these components were chosen

- **LangChain**: abstraction for chaining together embedding, retrieval, and LLM calls.
- **Chroma**: vector store for embedding persistence.
- **Whoosh**: lightweight full-text index for metadata search.
- **FastAPI**: backend API framework.
- **Streamlit**: interactive frontend for demos.

## 2. Architecture overview

### High-level flow
1. Ingest raw documents from a folder of PDFs or a JSON file.
2. Chunk documents and compute embeddings.
3. Store embeddings in Chroma with metadata.
4. Index text in Whoosh for fast keyword search.
5. When queried, retrieve semantically similar chunks, rerank if needed, and generate a final answer using an LLM.

### Components
- `ingest.py` : document parsing and chunking logic.
- `embed_and_store.py` : embedding computation and Chroma storage.
- `whoosh_index.py` : Whoosh keyword index (build + search).
- `retrieve.py` : hybrid retrieval — dense (Chroma) + keyword (Whoosh) fused via reciprocal rank fusion.
- `generate.py` : LLM answer generation.
- `main.py` : FastAPI app (IntelliRAG API).
- `streamlit_app.py` : IntelliRAG Streamlit frontend.


## 3. Prerequisites

- Python 3.10+
- pip
- Git

## 4. Installation

```bash
git clone https://github.com/divij-pawar/IntelliRAG.git
cd IntelliRAG
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Environment variables

Create a .env file in the root directory:

```ini
OPENAI_API_KEY=your_api_key_here
CHROMA_DB_DIR=./chroma_db
WHOOSH_INDEX_DIR=./whoosh_index
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
```

## 6. Run the Demo

You can run the full demo using the provided shell script:
```bash
bash run_demo.sh --source ./demo_corpus
```
Streamlit frontend (separate)
```bash
bash run_streamlit.sh
```
- ```--source``` can point to a folder of PDFs or a single JSON file.

- If omitted, defaults to ```./demo_corpus```.

**Or, run each component manually as shown below**
### Step 1 Ingest Documents:
This loads and embeds documents from a folder or JSON file:
```bash
python -m src.ingest --source ./demo_corpus --collection my_collection
```
- ```--source```: path to folder of PDFs or JSON file

- ```--collection```: Chroma collection name
### Step 2: Start Backend (FastAPI)
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Start Frontend (Streamlit)

```bash
streamlit run src/streamlit_app.py
```
Frontend UI runs at http://localhost:8501

 **Optional note**:

- You can run Streamlit in a separate terminal/session while the backend is running.
- Make sure the backend is running before starting Streamlit, otherwise queries will fail.

## 7. Query API:

```bash
curl -X POST http://127.0.0.1:8000/api/query \
-H "Content-Type: application/json" \
-d '{"q": "What is a transformer model?"}'
```
Response Example:
```bash
{
  "answer": "Transformers are deep learning models that use self-attention to process sequences.",
  "sources": [
    {"chunk": 0, "source": "doc1", "title": "Intro to Transformers"},
    {"chunk": 0, "source": "doc2", "title": "RAG Systems"}
  ]
}
```

## 8. Push to GitHub

```bash
cd IntelliRAG
git init
git add .
git commit -m "Initial commit: IntelliRAG"
git branch -M main
git remote add origin https://github.com/<your-username>/IntelliRAG.git
git push -u origin main
```

(Create the empty repo first at https://github.com/new — don't initialize it with a README, or `git push` will be rejected for diverging histories.)

## 9. Deploy to Render (free tier)

This repo includes a `render.yaml` blueprint that defines two services:
- **intellirag-backend** — the FastAPI API
- **intellirag-frontend** — the Streamlit UI, pointed at the backend

Steps:
1. Push the repo to GitHub (see above).
2. In the Render dashboard: **New > Blueprint**, select your repo. Render will read `render.yaml` and create both services.
3. On the backend service, set the `OPENAI_API_KEY` environment variable (marked `sync: false` in the blueprint, so it must be entered manually — never commit real keys).
4. Once the backend deploys, copy its public URL and confirm the frontend's `BACKEND_API_URL` env var matches `https://<your-backend-service>.onrender.com/api/query` (update it in the Render dashboard if the auto-generated service name differs from `intellirag-backend`).
5. Redeploy the frontend if you changed `BACKEND_API_URL`.

**Free-tier caveats:**
- Render's free web services use ephemeral disk — anything written to `chroma_db/` or `whoosh_index/` is wiped on every redeploy/restart. `start_backend.sh` re-ingests `demo_corpus/` on every boot to handle this automatically. If you ingest your own documents, you'll need to either commit them under `demo_corpus/` (or another folder you point `INGEST_SOURCE` at) so they're re-ingested on boot, or upgrade to a paid plan with a persistent disk.
- Free services spin down after inactivity and cold-start on the next request (can take 30–60s).
- Each cold start re-embeds the whole corpus, which costs a small number of OpenAI API calls — fine for a demo corpus, worth watching if you scale up the document set.

## 10. License

MIT License © 2025 IntelliRAG
