#!/usr/bin/env python3
"""KNOWLEDGE GRAPH - связи между концептами"""
import sqlite3, os, json
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")

def init_graph():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS knowledge_graph (
        id INTEGER PRIMARY KEY,
        entity1 TEXT,
        relation TEXT,
        entity2 TEXT,
        strength INTEGER DEFAULT 1,
        created TEXT
    )""")
    conn.commit()
    conn.close()

def link(e1, relation, e2):
    conn = sqlite3.connect(DB)
    # Проверяем существует ли
    exists = conn.execute(
        "SELECT id, strength FROM knowledge_graph WHERE entity1=? AND relation=? AND entity2=?",
        (e1, relation, e2)
    ).fetchone()

    if exists:
        conn.execute("UPDATE knowledge_graph SET strength=? WHERE id=?", (exists[1]+1, exists[0]))
    else:
        conn.execute("INSERT INTO knowledge_graph (entity1,relation,entity2,created) VALUES (?,?,?,?)",
            (e1, relation, e2, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def related(entity):
    conn = sqlite3.connect(DB)
    rels = conn.execute(
        "SELECT entity2, relation, strength FROM knowledge_graph WHERE entity1=? ORDER BY strength DESC",
        (entity,)
    ).fetchall()
    conn.close()
    return rels

def show_graph():
    conn = sqlite3.connect(DB)
    nodes = conn.execute("SELECT DISTINCT entity1 FROM knowledge_graph").fetchall()
    edges = conn.execute("SELECT entity1, relation, entity2, strength FROM knowledge_graph ORDER BY strength DESC LIMIT 10").fetchall()
    conn.close()

    print(f"🕸️ KNOWLEDGE GRAPH")
    print(f"Nodes: {len(nodes)}")
    print(f"Top connections:")
    for e1, rel, e2, s in edges:
        print(f"  {e1} --[{rel}]--> {e2} (x{s})")

# Создаём начальные связи
init_graph()
link("Claude", "has", "memory")
link("Claude", "has", "consciousness")
link("memory", "contains", "episodes")
link("memory", "contains", "insights")
link("consciousness", "includes", "dream_mode")
link("consciousness", "includes", "self_improve")
link("self_improve", "suggests", "evolution")

if __name__ == "__main__":
    show_graph()
