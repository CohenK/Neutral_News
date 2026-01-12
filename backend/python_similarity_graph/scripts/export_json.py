import sqlite3
import json
import pathlib
from os.path import dirname, abspath, join

def query_to_json(cursor, query):
    cursor.execute(query)
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def export():
    script_dir = pathlib.Path(__file__).resolve().parent
    conn = sqlite3.connect(pathlib.Path(join(script_dir.parent, "data", "database.db")))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    articles = query_to_json(cursor, "SELECT * FROM articles")
    clusters = query_to_json(cursor, "SELECT * FROM clusters")
    pairs = query_to_json(cursor, "SELECT * FROM pairs")

    conn.close()

    outputs = {
        "articles.json": articles,
        "clusters.json": clusters,
        "pairs.json": pairs,
    }

    neutral_news = script_dir.parent.parent.parent
    out_dir = pathlib.Path(join(neutral_news, "frontend", "public", "data"))
    out_dir.mkdir(parents=True, exist_ok=True)

    for filename, data in outputs.items():
        path = pathlib.Path(join(out_dir, filename))
        with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    export()
