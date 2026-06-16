import sqlite3

from heapify.config import config
from heapify.indices import SQLITE_SCHEMA


def init_db(db_path: str = None) -> sqlite3.Connection:
    path = db_path or config.DB_PATH
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SQLITE_SCHEMA)
    conn.commit()
    print(f"  Database ready at {path}")
    return conn


def setup(db_path: str = None) -> sqlite3.Connection:
    print("Initialising Heapify database...")
    conn = init_db(db_path)
    print("Done.")
    return conn


if __name__ == "__main__":
    setup()
