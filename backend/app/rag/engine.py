import os
from pathlib import Path
from typing import List, Dict, Any



# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = BASE_DIR.parent / "knowledge"
MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    "sentence-transformers/all-MiniLM-L6-v2"
)

_model = None
_index = None
_documents: List[Dict[str, Any]] = []


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

def _get_model():
    global _model

    if _model is None:
        from sentence_transformers import SentenceTransformer

        print(f"Loading embedding model: {MODEL_NAME}")

        _model = SentenceTransformer(
            MODEL_NAME,
            local_files_only=True,
        )

        print("Embedding model loaded.")

    return _model


# ---------------------------------------------------------
# Read knowledge-base documents
# ---------------------------------------------------------

def _load_documents() -> List[Dict[str, Any]]:
    documents = []

    if not KNOWLEDGE_DIR.exists():
        print(f"Knowledge directory not found: {KNOWLEDGE_DIR}")
        return documents

    supported_extensions = {
        ".txt",
        ".md",
        ".markdown",
    }

    for file_path in KNOWLEDGE_DIR.rglob("*"):

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in supported_extensions:
            continue

        try:
            text = file_path.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()
        except Exception as exc:
            print(f"Could not read {file_path}: {exc}")
            continue

        if not text:
            continue

        # Split large documents into smaller chunks.
        chunks = _chunk_text(text)

        for index, chunk in enumerate(chunks):

            documents.append(
                {
                    "id": f"{file_path.stem}-{index}",
                    "title": file_path.stem,
                    "source": str(file_path.relative_to(KNOWLEDGE_DIR)),
                    "text": chunk,
                }
            )

    return documents


# ---------------------------------------------------------
# Chunk documents
# ---------------------------------------------------------

def _chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200
) -> List[str]:

    text = text.strip()

    if len(text) <= chunk_size:
        return [text]

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


# ---------------------------------------------------------
# Build FAISS index
# ---------------------------------------------------------

def build():
    global _index
    global _documents
    import faiss
    import numpy as np

    print("Building knowledge-base index...")

    _documents = _load_documents()

    if not _documents:
        print(
            f"No knowledge documents found in: {KNOWLEDGE_DIR}"
        )

        _index = None

        return {
            "documents": 0,
            "status": "empty"
        }

    model = _get_model()

    texts = [
        document["text"]
        for document in _documents
    ]

    print(
        f"Creating embeddings for {len(texts)} documents..."
    )

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    dimension = embeddings.shape[1]

    _index = faiss.IndexFlatIP(dimension)

    _index.add(embeddings)

    print(
        f"RAG index ready. Documents indexed: {len(_documents)}"
    )

    return {
        "documents": len(_documents),
        "status": "ready"
    }


# ---------------------------------------------------------
# Search knowledge base
# ---------------------------------------------------------

def search(
    query: str,
    top_k: int = 5
) -> List[Dict[str, Any]]:

    global _index
    global _documents
    import numpy as np

    query = (query or "").strip()

    if not query:
        return []

    # Build automatically if not initialized.
    if _index is None or not _documents:
        build()

    if _index is None or not _documents:
        return []

    model = _get_model()

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    top_k = max(
        1,
        min(int(top_k), len(_documents))
    )

    scores, indices = _index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index in zip(
        scores[0],
        indices[0]
    ):

        if index < 0 or index >= len(_documents):
            continue

        document = dict(
            _documents[index]
        )

        document["score"] = float(score)

        results.append(document)

    return results


# ---------------------------------------------------------
# Convenience helper
# ---------------------------------------------------------

def get_context(
    query: str,
    top_k: int = 5
) -> str:

    results = search(
        query,
        top_k=top_k
    )

    if not results:
        return ""

    context_parts = []

    for result in results:

        context_parts.append(
            f"Source: {result['source']}\n"
            f"Title: {result['title']}\n"
            f"Content:\n{result['text']}"
        )

    return "\n\n---\n\n".join(
        context_parts
    )
