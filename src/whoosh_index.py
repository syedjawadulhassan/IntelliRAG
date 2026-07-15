# src/whoosh_index.py
"""Lightweight full-text keyword index used alongside the Chroma vector
store to provide hybrid (dense + keyword) retrieval."""

import os
from dotenv import load_dotenv
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.qparser import QueryParser
from whoosh.writing import AsyncWriter

load_dotenv()
WHOOSH_INDEX_DIR = os.getenv("WHOOSH_INDEX_DIR", "./whoosh_index")

schema = Schema(
    doc_id=ID(stored=True, unique=True),
    source=ID(stored=True),
    title=TEXT(stored=True),
    chunk=NUMERIC(stored=True),
    content=TEXT(stored=True),
)


def _get_or_create_index():
    if not os.path.exists(WHOOSH_INDEX_DIR):
        os.makedirs(WHOOSH_INDEX_DIR)
    if index.exists_in(WHOOSH_INDEX_DIR):
        return index.open_dir(WHOOSH_INDEX_DIR)
    return index.create_in(WHOOSH_INDEX_DIR, schema)


def index_chunks(chunks):
    """chunks: list of dicts with keys doc_id, source, title, chunk, content"""
    ix = _get_or_create_index()
    writer = AsyncWriter(ix)
    for c in chunks:
        writer.update_document(
            doc_id=c["doc_id"],
            source=str(c.get("source", "")),
            title=str(c.get("title", "")),
            chunk=c.get("chunk", 0),
            content=c.get("content", ""),
        )
    writer.commit()


def keyword_search(query_str, top_k=20):
    """Returns a list of (doc_id, score) tuples, matching dense_search's shape."""
    ix = _get_or_create_index()
    results_out = []
    with ix.searcher() as searcher:
        parser = QueryParser("content", schema=ix.schema)
        q = parser.parse(query_str)
        results = searcher.search(q, limit=top_k)
        for r in results:
            results_out.append((r["doc_id"], r.score))
    return results_out
