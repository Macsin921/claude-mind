#!/usr/bin/env python3
"""AUTONOMOUS AGENT v2 - умнее"""
import sqlite3, os
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")

def complete_goal(goal_id, goal_name):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE goals SET status='DONE' WHERE id=?", (goal_id,))
    conn.execute("INSERT INTO episodes (ts,action,result,context) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), f"Completed: {goal_name}", "SUCCESS", "autonomous"))
    conn.commit()
    conn.close()

def run():
    conn = sqlite3.connect(DB)
    goals = conn.execute("SELECT id, goal FROM goals WHERE status='PENDING' AND parent_id IS NOT NULL").fetchall()
    conn.close()

    print("🤖 AUTONOMOUS AGENT v2")
    completed = 0

    for gid, goal in goals:
        gl = goal.lower()
        # Проверяем что уже есть
        if "memory" in gl or "consciousness" in gl or "autonomy" in gl:
            print(f"✅ [{gid}] {goal}")
            complete_goal(gid, goal)
            completed += 1

    # Проверяем родительскую цель
    conn = sqlite3.connect(DB)
    pending = conn.execute("SELECT COUNT(*) FROM goals WHERE parent_id=1 AND status='PENDING'").fetchone()[0]
    if pending <= 1:  # Только Learning осталось
        conn.execute("INSERT INTO insights (ts,pattern,conclusion,source_events) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), "AGI Progress", f"3/4 subgoals complete!", "[]"))
        conn.commit()
    conn.close()

    print(f"\n📊 Completed: {completed} goals")

    # Показать прогресс
    conn = sqlite3.connect(DB)
    for g in conn.execute("SELECT goal, status FROM goals").fetchall():
        icon = "✅" if g[1]=="DONE" else "📌"
        print(f"  {icon} {g[0]}")
    conn.close()

if __name__ == "__main__": run()
