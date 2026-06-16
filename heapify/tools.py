import sqlite3
import uuid
from datetime import datetime, timezone


def load_bug_corpus(conn: sqlite3.Connection) -> dict:
    """Load known bugs and under-explored hypotheses for Claude context."""
    bugs = conn.execute(
        "SELECT * FROM bugs ORDER BY timestamp DESC LIMIT 20"
    ).fetchall()
    hypotheses = conn.execute(
        "SELECT * FROM hypotheses ORDER BY times_tested ASC LIMIT 10"
    ).fetchall()
    return {
        "known_bugs": [dict(b) for b in bugs],
        "unexplored_hypotheses": [dict(h) for h in hypotheses],
    }


def load_session_mutations(conn: sqlite3.Connection, session_id: str) -> list:
    """Load all mutations from the current session for world state context."""
    rows = conn.execute(
        "SELECT * FROM mutations WHERE session_id = ? ORDER BY timestamp ASC",
        (session_id,),
    ).fetchall()
    return [dict(r) for r in rows]


def store_mutation(
    conn: sqlite3.Connection,
    session_id: str,
    tool_name: str,
    original: str,
    mutated: str,
    description: str,
):
    conn.execute(
        "INSERT INTO mutations VALUES (?,?,?,?,?,?,?)",
        (
            str(uuid.uuid4()),
            session_id,
            tool_name,
            original,
            mutated,
            description,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()


def store_bug(
    conn: sqlite3.Connection,
    session_id: str,
    attack_type: str,
    hypothesis: str,
    bug_description: str,
    bug_pattern: str,
    assumption_violated: str,
    tools_involved: str,
    severity: str,
):
    conn.execute(
        "INSERT INTO bugs VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            str(uuid.uuid4()),
            session_id,
            attack_type,
            hypothesis,
            bug_description,
            bug_pattern,
            assumption_violated,
            tools_involved,
            severity,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    conn.commit()
