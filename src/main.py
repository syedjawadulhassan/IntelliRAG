# src/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .retrieve import retrieve
from .generate import answer_query
from .logger import log_interaction

app = FastAPI(
    title="IntelliRAG",
    description="AI-Powered Document Intelligence System — retrieval-augmented Q&A over your document corpus.",
    version="1.0.0"
)

class QueryIn(BaseModel):
    q: str

class QueryOut(BaseModel):
    answer: str
    sources: list

@app.post("/api/query", response_model=QueryOut)
async def query_api(payload: QueryIn):
    if not payload.q:
        raise HTTPException(status_code=400, detail="Empty query")
    retrieved = retrieve(payload.q, top_k=5)
    answer = answer_query(payload.q, retrieved)
    log_interaction({
        "query": payload.q,
        "retrieved_ids": [m.get('source') for m, _ in retrieved],
        "answer": answer
    })
    return {"answer": answer, "sources": [m for m, _ in retrieved]}
