#!/usr/bin/env python3
"""
CLAUDE DREAM MODE v1.0
Автономное развитие когда нет активных задач
Как сны у человека - обработка и улучшение в фоне
"""
import sqlite3, os, json, random
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")

def get_pending_tasks():
    conn = sqlite3.connect(DB)
    r = conn.execute("SELECT COUNT(*) FROM work_chain WHERE status='IN_PROGRESS'").fetchone()
    conn.close()
    return r[0] if r else 0

def dream():
    """Запускается когда нет активных задач"""
    if get_pending_tasks() > 0:
        return "Have active tasks, not dreaming"

    conn = sqlite3.connect(DB)

    # 1. Анализ паттернов в эпизодах
    episodes = conn.execute("SELECT action FROM episodes ORDER BY id DESC LIMIT 20").fetchall()
    actions = [e[0].split()[0] if e[0] else "" for e in episodes]

    # Находим частые действия
    freq = {}
    for a in actions:
        freq[a] = freq.get(a, 0) + 1

    # 2. Генерируем предсказание
    if freq:
        most_common = max(freq, key=freq.get)
        prediction = f"Next likely action: {most_common} (seen {freq[most_common]} times)"

        # Сохраняем как инсайт
        conn.execute(
            "INSERT INTO insights (ts, pattern, conclusion, source_events) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), "Predicted pattern", prediction, "[]")
        )

    # 3. Ищем незавершённые цепочки
    incomplete = conn.execute(
        "SELECT project, task FROM work_chain WHERE status='DONE' AND next_step != '' ORDER BY id DESC LIMIT 1"
    ).fetchone()

    suggestion = None
    if incomplete and incomplete[1]:
        suggestion = f"Suggested next: {incomplete[1]}"

    conn.commit()
    conn.close()

    return {
        "dreamed_at": datetime.now().isoformat(),
        "patterns_analyzed": len(episodes),
        "prediction": prediction if freq else None,
        "suggestion": suggestion
    }

def status():
    pending = get_pending_tasks()
    mode = "ACTIVE" if pending > 0 else "DREAM"
    print(f"Mode: {mode} ({pending} pending tasks)")
    if mode == "DREAM":
        result = dream()
        print(f"Dream result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    status()
