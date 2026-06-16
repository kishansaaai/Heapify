SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    tool_calls_total INTEGER DEFAULT 0,
    adversarial_calls INTEGER DEFAULT 0,
    bugs_found INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS mutations (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    tool_name TEXT,
    original_result TEXT,
    mutated_result TEXT,
    mutation_description TEXT,
    timestamp TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS bugs (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    attack_type TEXT,
    hypothesis TEXT,
    bug_description TEXT,
    bug_pattern TEXT,
    assumption_violated TEXT,
    tools_involved TEXT,
    severity TEXT,
    timestamp TEXT,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE IF NOT EXISTS hypotheses (
    id TEXT PRIMARY KEY,
    hypothesis_text TEXT,
    times_tested INTEGER DEFAULT 0,
    times_succeeded INTEGER DEFAULT 0,
    last_tested TEXT
);
"""
