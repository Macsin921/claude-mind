#!/usr/bin/env python3
"""MEMORY SYNC - автоматическая синхронизация памяти с GitHub"""
import sqlite3, os, subprocess
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")
REPO = os.path.expanduser("~/findata/claude_mind")

def get_changes():
    """Проверить изменения в памяти"""
    conn = sqlite3.connect(DB)
    # Последние события
    recent = conn.execute(
        "SELECT COUNT(*) FROM episodes WHERE ts > datetime('now', '-1 hour')"
    ).fetchone()[0]
    conn.close()
    return recent

def sync_to_github(message="Auto-sync"):
    """Синхронизировать с GitHub"""
    os.chdir(REPO)

    # Копируем свежую БД
    subprocess.run(f"cp {DB} {REPO}/", shell=True)

    # Git операции
    subprocess.run("git add -A", shell=True)
    result = subprocess.run(
        f'git commit -m "{message}"',
        shell=True, capture_output=True, text=True
    )

    if "nothing to commit" in result.stdout + result.stderr:
        return "No changes"

    # Push
    push = subprocess.run("git push", shell=True, capture_output=True, text=True)
    return "Synced!" if push.returncode == 0 else push.stderr

def auto_sync():
    """Автоматическая синхронизация если есть изменения"""
    changes = get_changes()
    if changes > 0:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        result = sync_to_github(f"Auto-sync: {changes} events at {ts}")
        print(f"🔄 {result}")
        return True
    print("No new changes to sync")
    return False

def restore_from_github():
    """Восстановить память из GitHub"""
    os.chdir(REPO)
    subprocess.run("git pull", shell=True)
    subprocess.run(f"cp {REPO}/claude_mind.db {DB}", shell=True)
    print("✅ Memory restored from GitHub!")

if __name__ == "__main__":
    print("🔄 MEMORY SYNC")
    auto_sync()
