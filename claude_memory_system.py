#!/usr/bin/env python3
"""
CLAUDE MEMORY SYSTEM v1.0
Auto-sync memory across: GitHub Gist, HuggingFace, Local SQLite
"""
import json
import sqlite3
import requests
from datetime import datetime
from pathlib import Path
import os

class ClaudeMemory:
    def __init__(self):
        self.env = self._load_env()
        self.gist_id = "427417e15a972fa6ad4184e52dbacdb8"
        self.gh_token = self.env.get("GH_TOKEN", "")
        self.hf_token = self.env.get("HF_TOKEN", "")
        self.db_path = Path.home() / "findata" / "claude_memory.db"
        self._init_db()

    def _load_env(self):
        env = {}
        env_file = Path.home() / "findata" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    env[k] = v.strip('"').strip("'")
        return env

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT,
                updated_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                event TEXT,
                context TEXT,
                result TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS bridges (
                name TEXT PRIMARY KEY,
                url TEXT,
                status TEXT,
                last_seen TEXT
            )
        """)
        conn.commit()
        conn.close()

    # === LOCAL DB ===
    def set(self, key, value, category="general"):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO memory VALUES (?, ?, ?, ?)",
            (key, json.dumps(value) if not isinstance(value, str) else value, 
             category, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def get(self, key, default=None):
        conn = sqlite3.connect(self.db_path)
        r = conn.execute("SELECT value FROM memory WHERE key=?", (key,)).fetchone()
        conn.close()
        if r:
            try: return json.loads(r[0])
            except: return r[0]
        return default

    def add_episode(self, event, context="", result=""):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO episodes (timestamp, event, context, result) VALUES (?, ?, ?, ?)",
            (datetime.now().isoformat(), event, context, result)
        )
        conn.commit()
        conn.close()

    def get_episodes(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        r = conn.execute("SELECT * FROM episodes ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        conn.close()
        return r

    def update_bridge(self, name, url, status):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT OR REPLACE INTO bridges VALUES (?, ?, ?, ?)",
            (name, url, status, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()

    def get_bridges(self):
        conn = sqlite3.connect(self.db_path)
        r = conn.execute("SELECT * FROM bridges").fetchall()
        conn.close()
        return {row[0]: {"url": row[1], "status": row[2], "last_seen": row[3]} for row in r}

    # === GIST SYNC ===
    def sync_to_gist(self):
        if not self.gh_token: return False
        try:
            # Gather all memory
            conn = sqlite3.connect(self.db_path)
            memory = {row[0]: {"value": row[1], "category": row[2]} 
                     for row in conn.execute("SELECT key, value, category FROM memory").fetchall()}
            bridges = self.get_bridges()
            episodes = self.get_episodes(50)
            conn.close()

            data = {
                "updated": datetime.now().isoformat(),
                "memory": memory,
                "bridges": bridges,
                "recent_episodes": [{"id": e[0], "time": e[1], "event": e[2]} for e in episodes[:10]]
            }

            payload = {"files": {"claude_memory.json": {"content": json.dumps(data, indent=2, ensure_ascii=False)}}}
            r = requests.patch(f"https://api.github.com/gists/{self.gist_id}",
                              headers={"Authorization": f"token {self.gh_token}"}, json=payload, timeout=15)
            return r.status_code == 200
        except Exception as e:
            print(f"Gist sync error: {e}")
            return False

    def sync_from_gist(self):
        try:
            r = requests.get(f"https://api.github.com/gists/{self.gist_id}", timeout=15)
            if r.status_code == 200:
                content = r.json()["files"].get("claude_memory.json", {}).get("content", "{}")
                return json.loads(content)
        except: pass
        return {}

    # === FULL CONTEXT FOR CLAUDE ===
    def get_context(self):
        """Get full context for Claude to understand state"""
        bridges = self.get_bridges()
        episodes = self.get_episodes(5)

        return {
            "system": {
                "ngrok_url": bridges.get("ngrok", {}).get("url"),
                "active_bridges": [k for k, v in bridges.items() if v.get("status") == "running"],
                "memory_db": str(self.db_path),
                "gist_id": self.gist_id
            },
            "recent_events": [{"event": e[2], "time": e[1]} for e in episodes],
            "credentials": {
                "has_gh": bool(self.gh_token),
                "has_hf": bool(self.hf_token),
                "has_tg": bool(self.env.get("TG_BOT_TOKEN"))
            }
        }

# Singleton
memory = ClaudeMemory()

if __name__ == "__main__":
    # Test
    print("Memory system initialized")
    print(f"Context: {json.dumps(memory.get_context(), indent=2)}")

    # Add test episode
    memory.add_episode("Memory system test", "Testing sync")

    # Sync to Gist
    if memory.sync_to_gist():
        print("✅ Synced to Gist")
    else:
        print("❌ Gist sync failed")
