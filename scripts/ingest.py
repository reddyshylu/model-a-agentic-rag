"""Build the Pinecone index: glossary entries plus patient-tagged visit-note chunks.

Usage (after filling .env and `pip install -r requirements.txt`):
    python scripts/ingest.py
Notes are sanitized (hidden instructions removed) before they are embedded.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from model_a import config  # noqa: E402
from model_a.glossary import entry_text, load_entries  # noqa: E402
from model_a.records import RecordStore  # noqa: E402
from model_a.vectorstore import embed_documents, index  # noqa: E402


def chunk(text: str, max_words: int = 250, overlap: int = 40) -> list[str]:
    words = text.split()
    out, i = [], 0
    while i < len(words):
        out.append(" ".join(words[i:i + max_words]))
        i += max_words - overlap
    return out


def main():
    if not config.PINECONE_API_KEY or config.PINECONE_API_KEY.startswith("your_"):
        sys.exit("Set PINECONE_API_KEY in .env first.")
    idx = index()
    entries = load_entries()
    vecs = embed_documents([entry_text(e) for e in entries])
    idx.upsert(vectors=[{"id": e["id"], "values": v, "metadata": {"term": e["term"], "kind": "glossary"}}
                        for e, v in zip(entries, vecs)], namespace="glossary")
    print(f"glossary: {len(entries)} entries")

    store, total = RecordStore(), 0
    for pid in sorted(store.patients):
        pv = store.for_patient(pid)
        batch = []
        for n in pv.notes():
            text = pv.note_text(int(n["visit_no"])) or ""
            for j, c in enumerate(chunk(text)):
                batch.append((f"{pid}-v{n['visit_no']}-c{j}", c, int(n["visit_no"])))
        if batch:
            vecs = embed_documents([b[1] for b in batch])
            idx.upsert(vectors=[{"id": i, "values": v,
                                 "metadata": {"patient_id": pid, "visit_no": vn, "text": t, "kind": "note"}}
                                for (i, t, vn), v in zip(batch, vecs)], namespace="notes")
            total += len(batch)
    print(f"notes: {total} chunks for {len(store.patients)} patients")


if __name__ == "__main__":
    main()
