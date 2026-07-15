import os
import json
import argparse
from pathlib import Path
from src.embed_and_store import ingest_documents
from PyPDF2 import PdfReader

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def read_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    documents = []
    for item in data:
        documents.append({
            "id": item.get("id", item.get("title", "doc")),
            "title": item.get("title", ""),
            "text": item.get("text", "")
        })
    return documents

def ingest_path(path, collection_name="docs_demo"):
    documents = []

    path_obj = Path(path)
    if path_obj.is_file():
        if path_obj.suffix.lower() == ".pdf":
            doc_id = path_obj.stem
            text = read_pdf(path_obj)
            documents.append({"id": doc_id, "title": doc_id, "text": text})
        elif path_obj.suffix.lower() == ".json":
            documents.extend(read_json(path_obj))
    elif path_obj.is_dir():
        for file_path in path_obj.glob("*"):
            if file_path.suffix.lower() == ".pdf":
                doc_id = file_path.stem
                text = read_pdf(file_path)
                documents.append({"id": doc_id, "title": doc_id, "text": text})
            elif file_path.suffix.lower() == ".json":
                documents.extend(read_json(file_path))

    if documents:
        ingest_documents(documents, collection_name=collection_name)
        print(f"Ingested {len(documents)} documents into collection '{collection_name}'.")
    else:
        print("No documents found to ingest.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest documents into Chroma.")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to a folder or file to ingest (PDF or JSON)."
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="docs_demo",
        help="Chroma collection name (default: docs_demo)."
    )

    args = parser.parse_args()
    ingest_path(args.source, collection_name=args.collection)
