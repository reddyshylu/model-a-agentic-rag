"""Optional Pinecone vector search (RETRIEVAL=pinecone).

Two namespaces in one index:
- "glossary": shared plain-language entries, no patient data.
- "notes":    visit-note chunks, every record tagged with patient_id.
Note searches ALWAYS apply a patient_id filter taken from the session, never
from the model or the user's text. scripts/ingest.py builds both namespaces.
"""
from __future__ import annotations

from functools import lru_cache

from . import config


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(config.EMBEDDING_MODEL)


QUERY_PREFIX = "Represent this sentence for searching relevant passages: "  # BGE convention


def embed_documents(texts: list[str]) -> list[list[float]]:
    return [list(map(float, v)) for v in _embedder().encode(texts, normalize_embeddings=True, batch_size=32)]


def embed_query(text: str) -> list[float]:
    return list(map(float, _embedder().encode([QUERY_PREFIX + text], normalize_embeddings=True)[0]))


@lru_cache(maxsize=1)
def index():
    from pinecone import Pinecone, ServerlessSpec
    pc = Pinecone(api_key=config.PINECONE_API_KEY)
    names = [i["name"] for i in pc.list_indexes()]
    if config.PINECONE_INDEX not in names:
        pc.create_index(name=config.PINECONE_INDEX, dimension=config.EMBEDDING_DIM, metric="cosine",
                        spec=ServerlessSpec(cloud=config.PINECONE_CLOUD, region=config.PINECONE_REGION))
    return pc.Index(config.PINECONE_INDEX)


def notes_filter(patient_id: str) -> dict:
    """The only filter used for note searches. Kept separate so tests can check it."""
    if not patient_id or not patient_id.startswith("P"):
        raise ValueError("A session patient id is required for note search")
    return {"patient_id": {"$eq": patient_id}}


def search_glossary(query: str, k: int) -> list[dict]:
    from .glossary import load_entries
    by_id = {e["id"]: e for e in load_entries()}
    res = index().query(vector=embed_query(query), top_k=k, namespace="glossary", include_metadata=True)
    return [{**by_id[m["id"]], "score": round(float(m["score"]), 3)} for m in res["matches"] if m["id"] in by_id]


def search_notes(patient_id: str, query: str, k: int = 3) -> list[dict]:
    res = index().query(vector=embed_query(query), top_k=k, namespace="notes", include_metadata=True,
                        filter=notes_filter(patient_id))
    out = []
    for m in res["matches"]:
        md = m["metadata"]
        if md.get("patient_id") != patient_id:  # belt and braces: never pass another patient's chunk on
            continue
        out.append({"text": md["text"], "visit_no": md["visit_no"], "score": round(float(m["score"]), 3)})
    return out
