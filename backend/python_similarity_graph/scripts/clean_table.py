import sqlite3

def clean_tables():
    conn = sqlite3.connect("data/database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM articles;")
    cursor.execute("DELETE FROM clusters;")
    conn.commit()
    conn.close()


if __name__ == "__main__":
    clean_tables()
