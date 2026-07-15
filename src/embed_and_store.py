# src/embed_and_store.py

import os
from dotenv import load_dotenv
from tqdm import tqdm
from langchain_openai import OpenAIEmbeddings
from chromadb import PersistentClient

from .whoosh_index import index_chunks

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Support both CHROMA_DB_DIR (documented in README/.env) and the older
# CHROMA_DIR name for backwards compatibility.
CHROMA_DIR = os.getenv('CHROMA_DB_DIR', os.getenv('CHROMA_DIR', './chroma_db'))
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')

# Initialize LangChain embeddings
emb = OpenAIEmbeddings(
    model=MODEL_NAME,
    openai_api_key=OPENAI_API_KEY
)


# Wrap embeddings in a class that matches Chroma's new interface
class ChromaEmbeddingWrapper:
    def __init__(self, langchain_emb):
        self.langchain_emb = langchain_emb

    def __call__(self, input: list[str]) -> list[list[float]]:
        # 'input' must be the argument name
        return self.langchain_emb.embed_documents(input)

    def name(self):
        return MODEL_NAME


# Instantiate wrapper
chroma_emb = ChromaEmbeddingWrapper(emb)

# Persistent Chroma client
client = PersistentClient(path=CHROMA_DIR)


def get_collection(name="docs_demo"):
    """Get or create a Chroma collection with the configured embedding function."""
    return client.get_or_create_collection(
        name=name,
        embedding_function=chroma_emb
    )


# Default collection kept for backwards compatibility with existing imports.
collection = get_collection()


# --- Chunking helper ---
def chunk_text(text, chunk_size=800, overlap=150):
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += chunk_size - overlap
    return chunks


# --- Document ingestion ---
def ingest_documents(documents, collection_name="docs_demo"):
    col = get_collection(collection_name)

    to_add = {'ids': [], 'documents': [], 'metadatas': []}
    whoosh_chunks = []

    for doc in tqdm(documents, desc="Ingesting"):
        chunks = chunk_text(doc['text'])
        for i, chunk in enumerate(chunks):
            doc_id = f"{doc['id']}_chunk_{i}"
            to_add['ids'].append(doc_id)
            to_add['documents'].append(chunk)
            to_add['metadatas'].append({
                'source': doc.get('id'),
                'title': doc.get('title'),
                'chunk': i
            })
            whoosh_chunks.append({
                'doc_id': doc_id,
                'source': doc.get('id'),
                'title': doc.get('title'),
                'chunk': i,
                'content': chunk,
            })

    if to_add['ids']:
        col.add(**to_add)
        index_chunks(whoosh_chunks)
