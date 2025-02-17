import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..')))
from pathlib import Path
from sqlite3 import connect, Connection, Cursor, IntegrityError


conn: Connection | None = None
curs: Cursor | None = None


def get_fake_db(name:str | None = None, reset: bool = False):
    global conn, curs
    if conn:
        if not reset:
            return
        conn = None
    if not name:
        name = os.getenv("FAKE_MIRROR_SQLITE_DB")
        top_dir = Path(__file__).resolve().parents[1]
        db_dir = top_dir / "fake_db"
        db_name = "fake_mirror.db"
        db_path = str(db_dir/db_name)
        name = os.getenv("FAKE_MIRROR_SQLITE_DB", db_path)
    conn = connect(name, check_same_thread=False)
    curs = conn.cursor()


get_fake_db()