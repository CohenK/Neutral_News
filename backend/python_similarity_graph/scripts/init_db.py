# scripts/init_db.py
import sqlite3
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema.sql"
DB_PATH = ROOT / "data" / "news.db"

# sanity checks
if not SCHEMA_PATH.exists():
    print(f"Error: schema.sql not found at {SCHEMA_PATH}", file=sys.stderr)
    sys.exit(1)

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

con = sqlite3.connect(DB_PATH)
con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
con.execute("PRAGMA journal_mode=WAL;")
con.commit()
con.close()

print(f"Created/updated DB at {DB_PATH}")
