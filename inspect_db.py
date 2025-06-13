import sqlite3

DB_PATH = "data/db.sqlite"

def check_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    conn.close()

    if not tables:
        print("❌ No tables found in the database.")
    else:
        print("✅ Tables found in the database:")
        for table in tables:
            print("-", table[0])

if __name__ == "__main__":
    check_tables()
