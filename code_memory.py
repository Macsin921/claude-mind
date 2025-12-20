#!/usr/bin/env python3
"""CODE FROM MEMORY - генерация кода из опыта"""
import sqlite3, os, re
from difflib import SequenceMatcher

DB = os.path.expanduser("~/findata/claude_mind.db")
CODE_DIR = os.path.expanduser("~/findata")

def init_code_memory():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS code_patterns (
        id INTEGER PRIMARY KEY,
        pattern_name TEXT,
        code_template TEXT,
        usage_count INTEGER DEFAULT 1,
        last_used TEXT
    )""")
    conn.commit()
    conn.close()

def learn_pattern(name, code):
    """Запомнить паттерн кода"""
    conn = sqlite3.connect(DB)
    exists = conn.execute("SELECT id,usage_count FROM code_patterns WHERE pattern_name=?", (name,)).fetchone()
    if exists:
        conn.execute("UPDATE code_patterns SET usage_count=?, last_used=datetime('now') WHERE id=?", 
            (exists[1]+1, exists[0]))
    else:
        conn.execute("INSERT INTO code_patterns (pattern_name,code_template,last_used) VALUES (?,?,datetime('now'))",
            (name, code))
    conn.commit()
    conn.close()

def find_similar(query):
    """Найти похожий код"""
    conn = sqlite3.connect(DB)
    patterns = conn.execute("SELECT pattern_name, code_template FROM code_patterns").fetchall()
    conn.close()

    best = None
    best_score = 0
    for name, code in patterns:
        score = SequenceMatcher(None, query.lower(), name.lower()).ratio()
        if score > best_score:
            best_score = score
            best = (name, code)

    return best if best_score > 0.3 else None

def suggest_code(task):
    """Предложить код для задачи"""
    similar = find_similar(task)
    if similar:
        print(f"Found: {similar[0]}")
        return similar[1]
    return None

# Учим базовые паттерны
init_code_memory()
learn_pattern("sqlite_connect", "conn = sqlite3.connect(DB)\nconn.execute(sql)\nconn.commit()\nconn.close()")
learn_pattern("http_request", "r = requests.post(url, json=data, timeout=10)\nresult = r.json()")
learn_pattern("file_read", "with open(path) as f:\n    data = f.read()")
learn_pattern("tg_send", "requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id':id,'text':msg})")

print("💻 CODE MEMORY READY")
print(f"Patterns: {len(list(sqlite3.connect(DB).execute('SELECT * FROM code_patterns')))}")

# Тест
print(f"\nSuggest for 'database': {suggest_code('database')}")
