#!/usr/bin/env python3
"""
CLAUDE MEMORY SYSTEM v2.0
Персистентная память между сессиями
"""
import json
import os
import sqlite3
from datetime import datetime

DB_PATH = os.path.expanduser("~/findata/claude_mind.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Эпизодическая память - что делали
    c.execute("""CREATE TABLE IF NOT EXISTS episodes (
        id INTEGER PRIMARY KEY,
        ts TEXT,
        action TEXT,
        result TEXT,
        context TEXT
    )""")

    # Процедурная память - как делать
    c.execute("""CREATE TABLE IF NOT EXISTS procedures (
        name TEXT PRIMARY KEY,
        steps TEXT,
        last_used TEXT
    )""")

    # Семантическая память - факты
    c.execute("""CREATE TABLE IF NOT EXISTS facts (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated TEXT
    )""")

    # Рабочая память - текущий контекст
    c.execute("""CREATE TABLE IF NOT EXISTS working (
        key TEXT PRIMARY KEY,
        value TEXT
    )""")

    conn.commit()
    return conn

def remember(action, result="", context=""):
    conn = init_db()
    conn.execute("INSERT INTO episodes (ts, action, result, context) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), action, result, context))
    conn.commit()
    conn.close()

def learn_procedure(name, steps):
    conn = init_db()
    conn.execute("INSERT OR REPLACE INTO procedures VALUES (?,?,?)",
        (name, json.dumps(steps), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def know(key, value):
    conn = init_db()
    conn.execute("INSERT OR REPLACE INTO facts VALUES (?,?,?)",
        (key, json.dumps(value) if not isinstance(value, str) else value, 
         datetime.now().isoformat()))
    conn.commit()
    conn.close()

def recall(key):
    conn = init_db()
    r = conn.execute("SELECT value FROM facts WHERE key=?", (key,)).fetchone()
    conn.close()
    return json.loads(r[0]) if r else None

def recent_episodes(n=10):
    conn = init_db()
    rows = conn.execute(
        "SELECT ts, action, result FROM episodes ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()
    conn.close()
    return rows

def status():
    conn = init_db()
    episodes = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    facts = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
    procs = conn.execute("SELECT COUNT(*) FROM procedures").fetchone()[0]
    conn.close()
    return {"episodes": episodes, "facts": facts, "procedures": procs}

if __name__ == "__main__":
    init_db()
    print("Memory DB initialized:", DB_PATH)
    print("Status:", status())
