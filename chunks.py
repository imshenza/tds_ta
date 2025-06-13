import sqlite3

conn = sqlite3.connect("data/db.sqlite")
cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    embedding BLOB
)
""")
conn.commit()
conn.close()
