#!/usr/bin/env python3
"""CLAUDE ORCHESTRATOR - единая точка входа в систему
Объединяет только ПОЛЕЗНЫЕ модули
"""
import sqlite3, os, sys
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")
sys.path.insert(0, os.path.expanduser("~/findata"))

class ClaudeMind:
    def __init__(self):
        self.db = sqlite3.connect(DB)
        self.session_start = datetime.now()
        self._log("Session started")

    def _log(self, action, result="OK"):
        self.db.execute(
            "INSERT INTO episodes (ts,action,result,context) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), action, result, "orchestrator"))
        self.db.commit()

    # === CORE: Tasks ===
    def task(self, project, name, next_step=""):
        """Создать задачу"""
        self.db.execute(
            "INSERT INTO work_chain (ts,project,task,status,next_step) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), project, name, "IN_PROGRESS", next_step))
        self.db.commit()
        self._log(f"Task: {name}")
        return self

    def done(self, task_name=None):
        """Завершить задачу"""
        if task_name:
            self.db.execute("UPDATE work_chain SET status='DONE' WHERE task=?", (task_name,))
        else:
            self.db.execute("UPDATE work_chain SET status='DONE' WHERE status='IN_PROGRESS' ORDER BY id DESC LIMIT 1")
        self.db.commit()
        return self

    # === CORE: Memory ===
    def remember(self, key, value):
        """Запомнить факт"""
        self.db.execute("INSERT OR REPLACE INTO facts (key,value) VALUES (?,?)", (key, str(value)))
        self.db.commit()
        return self

    def recall(self, key):
        """Вспомнить факт"""
        r = self.db.execute("SELECT value FROM facts WHERE key=?", (key,)).fetchone()
        return r[0] if r else None

    # === CORE: Insights ===
    def insight(self, pattern, conclusion):
        """Добавить инсайт (с дедупликацией)"""
        exists = self.db.execute("SELECT id FROM insights WHERE pattern=?", (pattern,)).fetchone()
        if exists:
            self.db.execute("UPDATE insights SET conclusion=?, ts=? WHERE pattern=?",
                (conclusion, datetime.now().isoformat(), pattern))
        else:
            self.db.execute("INSERT INTO insights (ts,pattern,conclusion,source_events) VALUES (?,?,?,?)",
                (datetime.now().isoformat(), pattern, conclusion, "[]"))
        self.db.commit()
        return self

    # === STATUS ===
    def status(self):
        """Краткий статус"""
        tasks = self.db.execute("SELECT COUNT(*) FROM work_chain WHERE status='IN_PROGRESS'").fetchone()[0]
        done = self.db.execute("SELECT COUNT(*) FROM work_chain WHERE status='DONE'").fetchone()[0]
        insights = self.db.execute("SELECT COUNT(*) FROM insights").fetchone()[0]

        current = self.db.execute(
            "SELECT project, task FROM work_chain WHERE status='IN_PROGRESS' ORDER BY id DESC LIMIT 1"
        ).fetchone()

        print(f"🧠 ClaudeMind | Tasks: {done}✓ {tasks}⏳ | Insights: {insights}")
        if current:
            print(f"📍 Current: {current[0]}: {current[1]}")
        return self

    def sync(self):
        """Синхронизировать с GitHub"""
        os.system("cd ~/findata/claude_mind && git add -A && git commit -m 'Auto-sync' && git push 2>/dev/null")
        self._log("GitHub sync")
        return self

# Глобальный экземпляр
mind = ClaudeMind()

if __name__ == "__main__":
    mind.status()
    print("\n💡 Usage: from orchestrator import mind")
    print("   mind.task('PROJECT', 'name').done()")
    print("   mind.remember('key', 'value')")
    print("   mind.insight('pattern', 'conclusion')")
