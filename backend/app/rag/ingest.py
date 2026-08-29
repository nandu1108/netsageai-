"""
Builds the FAISS vector index from the Cisco knowledge base documents.

Run this once (and again whenever you update data/knowledge_base/) before
starting the API:

    python -m app.rag.ingest
"""

import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

KB_DIR = Path(__file__).resolve().parents[2] / "data" / "knowledge_base"
INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "faiss_index"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents() -> list[Document]:
    docs = []
    for path in KB_DIR.glob("*.txt"):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def build_index():
    if not KB_DIR.exists() or not any(KB_DIR.glob("*.txt")):
        raise FileNotFoundError(
            f"No knowledge base .txt files found in {KB_DIR}. "
            "Add Cisco documentation (VLAN, routing, DHCP, ACL, commands) as .txt files."
        )

    raw_docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(raw_docs)

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(chunks, embeddings)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(str(INDEX_DIR))

    print(f"Indexed {len(chunks)} chunks from {len(raw_docs)} documents.")
    print(f"Saved FAISS index to {INDEX_DIR}")


if __name__ == "__main__":
    build_index()
