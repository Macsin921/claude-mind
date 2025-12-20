#!/usr/bin/env python3
"""GOAL DECOMPOSITION - разбиение целей на подзадачи"""
import sqlite3, os, json
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")

def init_goals():
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY,
        goal TEXT,
        parent_id INTEGER,
        status TEXT DEFAULT 'PENDING',
        priority INTEGER DEFAULT 5,
        created TEXT
    )""")
    conn.commit()
    conn.close()

def add_goal(goal, parent_id=None, priority=5):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO goals (goal,parent_id,priority,created) VALUES (?,?,?,?)",
        (goal, parent_id, priority, datetime.now().isoformat()))
    goal_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return goal_id

def decompose(goal_id, subtasks):
    """Разбить цель на подзадачи"""
    for task in subtasks:
        add_goal(task, parent_id=goal_id)

def get_next_action():
    """Получить следующее действие (leaf task)"""
    conn = sqlite3.connect(DB)
    # Ищем задачу без подзадач
    leaf = conn.execute("""
        SELECT g.id, g.goal FROM goals g
        WHERE g.status='PENDING' 
        AND NOT EXISTS (SELECT 1 FROM goals sub WHERE sub.parent_id=g.id)
        ORDER BY g.priority DESC, g.id
        LIMIT 1
    """).fetchone()
    conn.close()
    return leaf

def complete_goal(goal_id):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE goals SET status='DONE' WHERE id=?", (goal_id,))
    # Если все подзадачи done, пометить родителя
    parent = conn.execute("SELECT parent_id FROM goals WHERE id=?", (goal_id,)).fetchone()
    if parent and parent[0]:
        pending = conn.execute(
            "SELECT COUNT(*) FROM goals WHERE parent_id=? AND status='PENDING'",
            (parent[0],)
        ).fetchone()[0]
        if pending == 0:
            conn.execute("UPDATE goals SET status='DONE' WHERE id=?", (parent[0],))
    conn.commit()
    conn.close()

def show_tree(parent_id=None, level=0):
    conn = sqlite3.connect(DB)
    goals = conn.execute(
        "SELECT id, goal, status FROM goals WHERE parent_id IS ?" if parent_id is None 
        else "SELECT id, goal, status FROM goals WHERE parent_id=?",
        (parent_id,)
    ).fetchall()
    conn.close()

    for gid, goal, status in goals:
        icon = "✅" if status=="DONE" else "📌"
        print("  "*level + f"{icon} [{gid}] {goal}")
        show_tree(gid, level+1)

# Demo
init_goals()
main = add_goal("Build AGI assistant", priority=10)
decompose(main, ["Memory system", "Consciousness", "Autonomy", "Learning"])

print("🎯 GOAL TREE:")
show_tree()
print(f"\n➡️ Next action: {get_next_action()}")
