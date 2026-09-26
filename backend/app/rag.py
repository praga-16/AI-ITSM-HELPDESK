from pathlib import Path
import json

BASE = Path(__file__).resolve().parents[2]
KNOWLEDGE = BASE / "knowledge"
STORE = BASE / "data" / "vector_store"
STORE.mkdir(parents=True, exist_ok=True)
INDEX_FILE = STORE / "index.faiss"
META_FILE = STORE / "metadata.json"

model = None
index = None
metadata = []


def vector_libraries():
    """Load vector dependencies only when a RAG operation is requested."""
    import faiss
    import numpy as np
    return faiss, np

def get_model():
    global model
    if model is None:
        # Importing sentence-transformers also imports PyTorch. Delay that
        # cost until a semantic search is actually requested.
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return model

def chunks(text, size=750, overlap=100):
    text = " ".join(text.split())
    out = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        out.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return out

def build():
    global index, metadata
    faiss, np = vector_libraries()
    texts = []
    metadata = []
    for p in sorted(KNOWLEDGE.glob("*.txt")):
        for i, c in enumerate(chunks(p.read_text(encoding="utf-8"))):
            texts.append(c)
            metadata.append({"name":p.name,"chunk":i,"text":c})
    if not texts:
        return
    vec = np.asarray(get_model().encode(texts, normalize_embeddings=True), dtype="float32")
    index = faiss.IndexFlatIP(vec.shape[1])
    index.add(vec)
    faiss.write_index(index, str(INDEX_FILE))
    META_FILE.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

def ensure():
    global index, metadata
    if index is not None:
        return
    faiss, _ = vector_libraries()
    if INDEX_FILE.exists() and META_FILE.exists():
        index = faiss.read_index(str(INDEX_FILE))
        metadata = json.loads(META_FILE.read_text(encoding="utf-8"))
    else:
        build()

def search(query, k=4):
    ensure()
    if index is None:
        return []
    _, np = vector_libraries()
    q = np.asarray(get_model().encode([query], normalize_embeddings=True), dtype="float32")
    scores, ids = index.search(q, min(k, len(metadata)))
    out = []
    for score, idx in zip(scores[0], ids[0]):
        if idx >= 0:
            x = dict(metadata[idx])
            x["score"] = round(float(score), 4)
            out.append(x)
    return out
