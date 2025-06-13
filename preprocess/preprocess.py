import os
import json
import sqlite3
from pathlib import Path
from tqdm import tqdm

DB_PATH = "data/db.sqlite"
MARKDOWN_DIR = "data/tds_course"
DISCOURSE_FILE = "data/discourse_posts.json"
CHUNK_SIZE = 500  # tokens approx (not exact)
OVERLAP = 50


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            content TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()
    print("⚙️ Creating tables...")


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += chunk_size - overlap
    return chunks


from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")  # or your local model

def insert_chunks(source, chunks):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for chunk in chunks:
        embedding = model.encode(chunk)
        embedding_json = json.dumps(embedding.tolist())
        cur.execute(
            "INSERT INTO chunks (source, content, embedding) VALUES (?, ?, ?)",
            (source, chunk, embedding_json)
        )

    conn.commit()
    conn.close()


def process_markdown():
    print("📦 Processing markdown...")
    files = list(Path(MARKDOWN_DIR).glob("*.md"))
    total_chunks = 0
    for md_file in files:
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                continue
            chunks = chunk_text(text)
            insert_chunks(md_file.name, chunks)
            total_chunks += len(chunks)
    print(f"✅ Stored {total_chunks} markdown chunks.")


def process_discourse():
    print("💬 Processing discourse...")
    if not os.path.exists(DISCOURSE_FILE):
        print("❌ discourse_posts.json not found")
        return

    with open(DISCOURSE_FILE, "r", encoding="utf-8") as f:
        posts_data = json.load(f)

    total_chunks = 0
    for topic in posts_data:
        url = topic.get("url", "unknown")
        posts = topic.get("posts", [])
        for idx, post_text in enumerate(posts):
            if not post_text.strip():
                continue
            chunks = chunk_text(post_text)
            insert_chunks(f"{url}_post{idx+1}", chunks)
            total_chunks += len(chunks)
    print(f"✅ Stored {total_chunks} discourse chunks.")


def main():
    create_tables()
    process_markdown()
    process_discourse()
    print("🎉 Preprocessing complete!")


if __name__ == "__main__":
    main()
