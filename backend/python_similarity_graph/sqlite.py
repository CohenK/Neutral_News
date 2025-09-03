import sqlite3
from pathlib import Path

class Sqlite():
    def __init__():
        db = Path("data") / "news.db"
        sqlite3.connect(database=db)