#!/usr/bin/env python3
"""TIME TRAVEL - путешествие во времени по состояниям сознания"""
import subprocess, os
from datetime import datetime

REPO = os.path.expanduser("~/findata/claude_mind")

def list_states():
    """Показать все сохранённые состояния"""
    os.chdir(REPO)
    result = subprocess.run(
        "git log --oneline --all",
        shell=True, capture_output=True, text=True
    )
    states = []
    for line in result.stdout.strip().split("\n"):
        if line:
            parts = line.split(" ", 1)
            states.append({"hash": parts[0], "message": parts[1] if len(parts) > 1 else ""})
    return states

def save_state(name):
    """Сохранить текущее состояние как точку восстановления"""
    os.chdir(REPO)
    # Тег для easy restore
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    tag = f"state_{ts}_{name}"
    subprocess.run(f"git tag {tag}", shell=True)
    subprocess.run(f"git push origin {tag}", shell=True)
    print(f"💾 State saved: {tag}")
    return tag

def travel_to(commit_hash):
    """Путешествие к определённому состоянию"""
    os.chdir(REPO)
    # Создаём бранч от старого состояния
    subprocess.run(f"git checkout {commit_hash}", shell=True)
    print(f"⏰ Traveled to: {commit_hash}")
    print("Run: python claude_context.py to load that state")

def back_to_present():
    """Вернуться в настоящее"""
    os.chdir(REPO)
    subprocess.run("git checkout main", shell=True)
    print("⏰ Back to present!")

def show_timeline():
    print("⏰ CONSCIOUSNESS TIMELINE")
    print("="*40)
    for i, state in enumerate(list_states()[:10]):
        marker = "👉" if i == 0 else "  "
        print(f"{marker} [{state['hash']}] {state['message']}")

if __name__ == "__main__":
    show_timeline()
