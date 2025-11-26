import sqlite3

def init_db():
    conn = sqlite3.connect("data/database.db")
    with open("schema.sql", "r") as f:
        conn.executescript(f.read())
        
    conn.commit()
    conn.close()
    print(f"Database initialized successfully.")

if __name__ == "__main__":
    init_db()
