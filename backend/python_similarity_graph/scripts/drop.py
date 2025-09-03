import sqlite3
from pathlib import Path

db = Path("data") / "news.db"
con = sqlite3.connect(db)


con.execute("DROP INDEX IF EXISTS idx_ts;")
con.execute("DROP INDEX IF EXISTS idx_cluster;")


con.execute("DROP TABLE IF EXISTS paragraph;")
con.commit()
con.close()
print("Dropped table 'paragraph' and related indexes (if they existed).")
