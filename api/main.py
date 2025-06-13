from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import numpy as np
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")
DB_PATH = "data/db.sqlite"

# Serve static files from the frontend folder
app.mount("/static", StaticFiles(directory="frontend"), name="static")

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

def get_all_chunks():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, source, content, embedding FROM chunks WHERE embedding IS NOT NULL")
    rows = cur.fetchall()
    conn.close()

    chunks = []
    for row in rows:
        embedding = np.array(json.loads(row[3]), dtype=np.float32)
        chunks.append({
            "id": row[0],
            "source": row[1],
            "content": row[2],
            "embedding": embedding
        })
    return chunks

# Serve the frontend index.html at the root
@app.get("/")
def read_index():
    return FileResponse(os.path.join("frontend", "index.html"))

@app.post("/search")
def search(request: QueryRequest):
    chunks = get_all_chunks()
    if not chunks:
        raise HTTPException(status_code=404, detail="No chunks found in database.")

    query_embedding = model.encode([request.query], convert_to_numpy=True)[0].reshape(1, -1)
    chunk_embeddings = np.vstack([chunk["embedding"] for chunk in chunks])
    scores = cosine_similarity(query_embedding, chunk_embeddings)[0]

    results = []
    for idx in scores.argsort()[::-1][:request.top_k]:
        results.append({
            "score": float(scores[idx]),
            "content": chunks[idx]["content"],
            "source": chunks[idx]["source"]
        })

    return {
        "query": request.query,
        "results": results
    }
