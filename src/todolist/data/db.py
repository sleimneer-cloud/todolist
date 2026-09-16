import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = (
    Path.home() / "Library" / "Application Support" / "TodoWidget" / "todolist.db"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    due_date TEXT,
    start_date TEXT,
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT
)
"""


def connect(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute(SCHEMA)
    columns = {row[1] for row in conn.execute("PRAGMA table_info(tasks)")}
    if "start_date" not in columns:
        conn.execute("ALTER TABLE tasks ADD COLUMN start_date TEXT")
    if "created_at" not in columns:
        # ponytail: 기존 행이 언제 생성됐는지는 알 방법이 없다 — 없는 값을
        # 지어내는 대신 NULL로 두고, 주간 조회에서 자연히 제외되게 한다.
        conn.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
    conn.commit()
    return conn
