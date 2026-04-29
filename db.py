import sqlite3
from .config import settings
from .schema import COACH_COLUMNS

CREATE_COACHES = f"""
CREATE TABLE IF NOT EXISTS coaches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_key TEXT UNIQUE,
    {', '.join([c + ' TEXT' for c in COACH_COLUMNS])}
);
"""

CREATE_CHANGELOG = """
CREATE TABLE IF NOT EXISTS changelog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_date TEXT,
    school TEXT,
    division TEXT,
    change_type TEXT,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT,
    source_url TEXT
);
"""

def connect(path: str | None = None):
    conn = sqlite3.connect(path or settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn=None):
    close = False
    if conn is None:
        conn = connect(); close = True
    conn.execute(CREATE_COACHES)
    conn.execute(CREATE_CHANGELOG)
    conn.commit()
    if close: conn.close()

def upsert_coach(conn, row: dict):
    record_key = row.get('record_key') or '|'.join([
        row.get('division',''), row.get('school',''), row.get('full_name',''), row.get('title','')
    ]).lower()
    row['record_key'] = record_key
    existing = conn.execute('SELECT * FROM coaches WHERE record_key=?', (record_key,)).fetchone()
    cols = ['record_key'] + COACH_COLUMNS
    if existing:
        updates = ', '.join([f'{c}=?' for c in COACH_COLUMNS])
        conn.execute(f'UPDATE coaches SET {updates} WHERE record_key=?', [row.get(c,'') for c in COACH_COLUMNS] + [record_key])
        return 'updated'
    placeholders = ','.join(['?'] * len(cols))
    conn.execute(f'INSERT INTO coaches ({','.join(cols)}) VALUES ({placeholders})', [row.get(c,'') for c in cols])
    return 'inserted'
