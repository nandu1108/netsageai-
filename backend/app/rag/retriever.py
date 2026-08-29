"""
Loads the FAISS index built by ingest.py and retrieves the most relevant
knowledge base chunks for a given query.
"""

from pathlib import Path
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

INDEX_DIR = Path(__file__).resolve().parents[2] / "data" / "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _load_vectorstore() -> FAISS:
    if not INDEX_DIR.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {INDEX_DIR}. Run `python -m app.rag.ingest` first."
        )
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
    )


def retrieve_context(query: str, k: int = 4) -> list[str]:
    """Return the top-k most relevant knowledge base chunks for a query."""
    vectorstore = _load_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return [doc.page_content for doc in results]
