from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import json
import os
import numpy as np
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

app = FastAPI()

# Mount static frontend
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_index():
    return FileResponse(os.path.join("frontend", "index.html"))

# Fix: match frontend field name 'query'
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    image: str = None  # Optional

DB_PATH = "data/db.sqlite"
model = SentenceTransformer("all-MiniLM-L6-v2")

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

def get_answer_from_openrouter(query: str, chunks: list[dict]) -> str:
    trimmed_chunks = [chunk["content"][:500] for chunk in chunks[:3]]
    context_text = "\n\n".join(trimmed_chunks)

    prompt = f"""
You are a smart and helpful teaching assistant for an IIT Madras Data Science student.

Use only the context below to answer the question. If the answer is not found in the context, say:
"Sorry, I couldn't find the answer in the material."

Context:
{context_text}

--- End of Context ---

Question: {query}

Provide a clear, concise answer below:
"""

    messages = [
        {"role": "system", "content": "You are a helpful Teaching Assistant."},
        {"role": "user", "content": prompt}
    ]

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",
        messages=messages,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

@app.post("/api/")
def query_api(request: QueryRequest):
    all_chunks = [c for c in get_all_chunks() if "?" not in c["content"][:100]]

    if not all_chunks:
        raise HTTPException(status_code=404, detail="No chunks found in DB.")

    query_embedding = model.encode([request.query], convert_to_numpy=True)[0].reshape(1, -1)
    chunk_embeddings = np.vstack([chunk["embedding"] for chunk in all_chunks])
    scores = cosine_similarity(query_embedding, chunk_embeddings)[0]

    top_chunks = sorted(
        zip(scores, all_chunks),
        key=lambda x: x[0],
        reverse=True
    )[:request.top_k]

    final_answer = get_answer_from_openrouter(request.query, [chunk for _, chunk in top_chunks])

    links = []
    for _, chunk in top_chunks:
        if "discourse" in chunk["source"]:
            links.append({
                "url": f"https://discourse.onlinedegree.iitm.ac.in/{chunk['source']}",
                "text": chunk["source"]
            })

    return {
        "answer": final_answer,
        "links": links
    }
