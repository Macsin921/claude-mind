#!/usr/bin/env python3
"""TIERED MEMORY - многоуровневая память
L0: Hot (RAM) - текущая сессия
L1: Warm (SQLite) - последние дни  
L2: Cold (Archive) - сжатые инсайты
L3: Frozen (GitHub) - бэкап
"""
import sqlite3, os, json
from datetime import datetime, timedelta

DB = os.path.expanduser("~/findata/claude_mind.db")

# L0: Hot Memory (in-process cache)
HOT_CACHE = {}

def init_tiers():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS memory_tiers (
        id INTEGER PRIMARY KEY,
        key TEXT UNIQUE,
        value TEXT,
        tier INTEGER DEFAULT 1,
        access_count INTEGER DEFAULT 0,
        last_access TEXT,
        created TEXT
    )""")
    conn.commit()
    conn.close()

def store(key, value, tier=1):
    """Сохранить в память"""
    # L0: Hot cache
    HOT_CACHE[key] = {"value": value, "ts": datetime.now().isoformat()}

    # L1: SQLite
    conn = sqlite3.connect(DB)
    conn.execute("""INSERT OR REPLACE INTO memory_tiers 
        (key, value, tier, last_access, created) VALUES (?,?,?,?,?)""",
        (key, json.dumps(value), tier, datetime.now().isoformat(), datetime.now().isoformat()))
    conn.commit()
    conn.close()

def fetch(key):
    """Получить из памяти (с promotion)"""
    # L0: Check hot cache first
    if key in HOT_CACHE:
        HOT_CACHE[key]["hits"] = HOT_CACHE[key].get("hits", 0) + 1
        return HOT_CACHE[key]["value"]

    # L1: Check SQLite
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT value, tier FROM memory_tiers WHERE key=?", (key,)).fetchone()
    if row:
        # Promote to L0 on access
        value = json.loads(row[0])
        HOT_CACHE[key] = {"value": value, "ts": datetime.now().isoformat()}
        # Update access count
        conn.execute("UPDATE memory_tiers SET access_count=access_count+1, last_access=? WHERE key=?",
            (datetime.now().isoformat(), key))
        conn.commit()
        conn.close()
        return value
    conn.close()
    return None

def demote_cold():
    """Понизить редко используемые в холодный tier"""
    conn = sqlite3.connect(DB)
    # Данные старше 7 дней с малым access_count → tier 2
    conn.execute("""UPDATE memory_tiers SET tier=2 
        WHERE tier=1 AND access_count < 3 
        AND last_access < datetime('now', '-7 days')""")
    moved = conn.total_changes
    conn.commit()
    conn.close()
    return moved

def get_stats():
    conn = sqlite3.connect(DB)
    stats = {}
    for tier in [0, 1, 2, 3]:
        if tier == 0:
            stats[f"L{tier}_hot"] = len(HOT_CACHE)
        else:
            count = conn.execute("SELECT COUNT(*) FROM memory_tiers WHERE tier=?", (tier,)).fetchone()[0]
            stats[f"L{tier}"] = count
    conn.close()
    return stats

init_tiers()
store("test_key", {"data": "test", "ts": datetime.now().isoformat()})
print("🧠 TIERED MEMORY")
print(f"Stats: {get_stats()}")
print(f"Fetch test: {fetch('test_key')}")
