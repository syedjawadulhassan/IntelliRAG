#!/bin/bash
# start_backend.sh
# Used as Render's start command. Free-tier Render web services have
# ephemeral disk, so we re-ingest the demo corpus on every boot to make
# sure the Chroma/Whoosh indexes exist before the API starts serving.
set -e

echo "=== Ingesting demo corpus (ephemeral disk, re-ingest on boot) ==="
python -m src.ingest --source "${INGEST_SOURCE:-./demo_corpus}" --collection "${CHROMA_COLLECTION:-docs_demo}"

echo "=== Starting FastAPI server ==="
uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"
