from pathlib import Path
from db.database import get_connection

conn = get_connection()
cursor = conn.cursor()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SQL_FILE_PATH = PROJECT_ROOT / "db" / "models.sql"

with open(SQL_FILE_PATH, "r") as f:
    cursor.executescript(f.read())

conn.commit()
conn.close()

# need to be in app directory in terminal and run python -m utils.manual_connections