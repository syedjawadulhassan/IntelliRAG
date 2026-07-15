import os
from chromadb import PersistentClient
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from collections import defaultdict

from .whoosh_index import keyword_search

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Support both CHROMA_DB_DIR (documented in README/.env) and the older
# CHROMA_DIR name for backwards compatibility.
CHROMA_DIR = os.getenv('CHROMA_DB_DIR', os.getenv('CHROMA_DIR', './chroma_db'))
# Must match the model used at ingestion time (embed_and_store.py), otherwise
# query embeddings and stored embeddings will have mismatched dimensions.
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
COLLECTION_NAME = os.getenv('CHROMA_COLLECTION', 'docs_demo')

emb = OpenAIEmbeddings(model=MODEL_NAME, openai_api_key=OPENAI_API_KEY)
client = PersistentClient(path=CHROMA_DIR)


def dense_search(query, top_k=20):
    emb_q = emb.embed_query(query)
    col = client.get_collection(COLLECTION_NAME)
    res = col.query(query_embeddings=[emb_q], n_results=top_k)
    ids = res['ids'][0]
    distances = res['distances'][0]
    return list(zip(ids, distances))


def reciprocal_rank_fusion(list1, list2, k=10):
    ranks = defaultdict(float)
    for lst in (list1, list2):
        for rank, (docid, _) in enumerate(lst, start=1):
            ranks[docid] += 1.0 / (60 + rank)
    sorted_docs = sorted(ranks.items(), key=lambda x: -x[1])
    return [doc for doc, _ in sorted_docs[:k]]


def retrieve(query, top_k=5):
    """Hybrid retrieval: fuse dense (semantic) and keyword (Whoosh) search
    results via reciprocal rank fusion."""
    dense = dense_search(query, top_k=50)

    try:
        keyword = keyword_search(query, top_k=50)
    except Exception:
        # If the Whoosh index hasn't been built yet, fall back to dense-only.
        keyword = []

    if keyword:
        fused = reciprocal_rank_fusion(dense, keyword, k=top_k)
    else:
        fused = [docid for docid, _ in dense[:top_k]]

    col = client.get_collection(COLLECTION_NAME)
    retrieved = []
    for rid in fused:
        try:
            res = col.get(ids=[rid])
            doc_text = res['documents'][0]
            meta = res['metadatas'][0]
            retrieved.append((meta, doc_text))
        except Exception:
            retrieved.append(({'id': rid}, ''))
    return retrieved
