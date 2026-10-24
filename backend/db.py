import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("green_steps.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con

def init_db():
    with connect() as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS events (
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, date TEXT NOT NULL, location TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS runners (
          id INTEGER PRIMARY KEY, bib INTEGER UNIQUE NOT NULL, name TEXT NOT NULL,
          faculty TEXT NOT NULL, event_id INTEGER NOT NULL REFERENCES events(id)
        );
        CREATE TABLE IF NOT EXISTS runs (
          id INTEGER PRIMARY KEY, runner_id INTEGER NOT NULL REFERENCES runners(id),
          km REAL NOT NULL CHECK(km > 0), run_date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pledges (
          id TEXT PRIMARY KEY, event_id INTEGER NOT NULL REFERENCES events(id),
          runner_id INTEGER REFERENCES runners(id), sponsor_name TEXT NOT NULL,
          nok_per_km REAL NOT NULL CHECK(nok_per_km > 0), max_cap REAL,
          created_at TEXT NOT NULL
        );
        ''')
