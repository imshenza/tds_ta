import sqlite3
import os
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
import json

DB_PATH = "data/db.sqlite"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # or any other model you prefer

def get_chunks_to_embed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, content FROM chunks WHERE embedding IS NULL")
    rows = cur.fetchall()
    conn.close()
    return rows

def save_embeddings_to_db(embeddings, ids):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for emb, chunk_id in zip(embeddings, ids):
        emb_json = json.dumps(emb.tolist())
        cur.execute("UPDATE chunks SET embedding = ? WHERE id = ?", (emb_json, chunk_id))
    conn.commit()
    conn.close()

def main():
    print("🚀 Starting embedding process...")
    rows = get_chunks_to_embed()
    if not rows:
        print("🔍 0 chunks to embed")
        return

    ids = [row[0] for row in rows]
    texts = [row[1] for row in rows]

    print(f"🔢 Embedding {len(texts)} chunks...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    save_embeddings_to_db(embeddings, ids)
    print("✅ Embedding complete.")

if __name__ == "__main__":
    main()
