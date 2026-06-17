import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "../../data/pricewatch.db"

def get_connection():
    return sqlite3.connect(str(DB_PATH.resolve()))