#!/usr/bin/env python3
"""AUTO-CONSOLIDATION: Периодическая рефлексия памяти"""
import sqlite3, os, json
from datetime import datetime, timedelta

DB = os.path.expanduser("~/findata/claude_mind.db")

def consolidate():
    """Сжимает события в инсайты"""
    conn = sqlite3.connect(DB)

    # Берём события старше 1 часа без инсайтов
    events = conn.execute("""
        SELECT id, action, result FROM episodes 
        ORDER BY id DESC LIMIT 20
    """).fetchall()

    if len(events) < 3:
        return "Not enough events"

    # Группируем по типу действия
    actions = {}
    for id, action, result in events:
        key = action.split()[0] if action else "unknown"
        if key not in actions:
            actions[key] = []
        actions[key].append((id, action, result))

    # Создаём инсайты для повторяющихся действий
    created = 0
    for key, items in actions.items():
        if len(items) >= 2:
            pattern = f"Frequent action: {key}"
            conclusion = f"Done {len(items)} times. Last: {items[0][1][:30]}"
            ids = [i[0] for i in items[:5]]

            # Проверяем что такого инсайта ещё нет
            exists = conn.execute(
                "SELECT 1 FROM insights WHERE pattern=?", (pattern,)
            ).fetchone()

            if not exists:
                conn.execute(
                    "INSERT INTO insights (ts, pattern, conclusion, source_events) VALUES (?,?,?,?)",
                    (datetime.now().isoformat(), pattern, conclusion, json.dumps(ids))
                )
                created += 1

    conn.commit()

    # Статистика
    total_events = conn.execute("SELECT COUNT(*) FROM episodes").fetchone()[0]
    total_insights = conn.execute("SELECT COUNT(*) FROM insights").fetchone()[0]
    conn.close()

    return f"Created {created} insights. Total: {total_events} events → {total_insights} insights"

if __name__ == "__main__":
    print("🔄 Running consolidation...")
    result = consolidate()
    print(f"✅ {result}")
