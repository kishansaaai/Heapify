import sqlite3
import uuid
from datetime import datetime, timezone


class Session:
    def __init__(self, db_conn: sqlite3.Connection):
        self.run_id = str(uuid.uuid4())
        self.hypothesis = None
        self.world_state = {}
        self.db_conn = db_conn
        self._record_start()

    def _record_start(self):
        self.db_conn.execute(
            "INSERT INTO sessions (id, start_time) VALUES (?, ?)",
            (self.run_id, datetime.now(timezone.utc).isoformat()),
        )
        self.db_conn.commit()

    def close(self, stats: dict):
        self.db_conn.execute(
            "UPDATE sessions SET end_time=?, tool_calls_total=?, adversarial_calls=?, bugs_found=? WHERE id=?",
            (
                datetime.now(timezone.utc).isoformat(),
                stats.get("tool_calls_total", 0),
                stats.get("adversarial_calls", 0),
                stats.get("bugs_found", 0),
                self.run_id,
            ),
        )
        self.db_conn.commit()
