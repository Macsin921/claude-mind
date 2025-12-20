
#!/usr/bin/env python3
"""
CLAUDE REFLECTIVE MEMORY v1.0
Память которая думает о себе
"""
import sqlite3, os, json
from datetime import datetime, timedelta

DB = os.path.expanduser("~/findata/claude_mind.db")

def init_reflection_tables():
    conn = sqlite3.connect(DB)
    # Инсайты - сжатые знания из событий
    conn.execute("""CREATE TABLE IF NOT EXISTS insights (
        id INTEGER PRIMARY KEY,
        ts TEXT,
        pattern TEXT,      -- Что заметил
        conclusion TEXT,   -- Какой вывод
        source_events TEXT -- Из каких событий (JSON list of ids)
    )""")

    # Связи между событиями
    conn.execute("""CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY,
        from_event INTEGER,
        to_event INTEGER,
        relation TEXT  -- caused, enabled, blocked, related
    )""")

    # Уровни памяти
    conn.execute("""CREATE TABLE IF NOT EXISTS memory_levels (
        event_id INTEGER PRIMARY KEY,
        level INTEGER DEFAULT 0  -- 0=working, 1=short, 2=long, 3=core
    )""")
    conn.commit()
    conn.close()

def add_insight(pattern, conclusion, event_ids=[]):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO insights (ts, pattern, conclusion, source_events) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), pattern, conclusion, json.dumps(event_ids)))
    conn.commit()
    conn.close()

def link_events(from_id, to_id, relation="caused"):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO links (from_event, to_event, relation) VALUES (?,?,?)",
        (from_id, to_id, relation))
    conn.commit()
    conn.close()

def get_insights(n=5):
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT ts, pattern, conclusion FROM insights ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    conn.close()
    return rows

def reflect():
    """Размышление над последними событиями - вызывать периодически"""
    conn = sqlite3.connect(DB)

    # Берём события без инсайтов
    events = conn.execute("""
        SELECT id, ts, action, result FROM episodes 
        WHERE id NOT IN (SELECT DISTINCT json_each.value FROM insights, json_each(source_events))
        ORDER BY id DESC LIMIT 10
    """).fetchall()

    conn.close()

    if len(events) < 3:
        return "Not enough events to reflect"

    # Здесь можно добавить AI анализ
    # Пока простая эвристика
    actions = [e[2] for e in events]

    # Ищем повторяющиеся паттерны
    patterns_found = []
    for action in set(actions):
        if actions.count(action) > 1:
            patterns_found.append(f"Repeated: {action}")

    if patterns_found:
        add_insight(
            patterns_found[0],
            "This action is frequently performed",
            [e[0] for e in events[:5]]
        )
        return f"Created insight: {patterns_found[0]}"

    return "No patterns found"

def show_memory_state():
    conn = sqlite3.connect(DB)
    events = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    insights = conn.execute("SELECT COUNT(*) FROM insights").fetchone()[0]
    links = conn.execute("SELECT COUNT(*) FROM links").fetchone()[0]
    conn.close()

    print(f"""
=== MEMORY STATE ===
Events:   {events}
Insights: {insights}
Links:    {links}

Recent Insights:""")
    for ts, pattern, conclusion in get_insights(3):
        print(f"  💡 {pattern[:40]}")
        print(f"     → {conclusion[:40]}")

if __name__ == "__main__":
    init_reflection_tables()
    show_memory_state()
