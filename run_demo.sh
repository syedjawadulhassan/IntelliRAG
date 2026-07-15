#!/bin/bash
# run_demo.sh

# Usage:
# ./run_demo.sh --source ./demo_corpus
# If no --source is provided, defaults to ./demo_corpus

# Activate virtual environment
source .venv/bin/activate

# Default source folder
SOURCE_DIR="./demo_corpus"

# Parse optional --source argument
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    --source)
      SOURCE_DIR="$2"
      shift
      shift
      ;;
    *)
      shift
      ;;
  esac
done

echo "=== Cleaning old Chroma database ==="
CHROMA_DIR="./chroma_db"
if [ -d "$CHROMA_DIR" ]; then
    rm -rf "$CHROMA_DIR"
    echo "Deleted old Chroma DB at $CHROMA_DIR"
else
    echo "No existing Chroma DB found."
fi

echo "=== Running document ingestion ==="
python -m src.ingest --source "$SOURCE_DIR"

echo "=== Starting FastAPI server ==="
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 

