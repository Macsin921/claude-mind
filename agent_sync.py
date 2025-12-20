#!/usr/bin/env python3
"""MULTI-AGENT SYNC - Claude <-> Gemini через Gist"""
import requests, json, os
from datetime import datetime

GIST_ID = "427417e15a972fa6ad4184e52dbacdb8"
GH = os.environ.get("GH_TOKEN", "")

def load_env():
    try:
        for l in open(os.path.expanduser("~/findata/.env")):
            if "=" in l and not l.startswith("#"):
                k,v = l.strip().split("=",1)
                os.environ[k] = v.strip('"')
    except: pass

load_env()
GH = os.environ.get("GH_TOKEN", "")

def read_shared_memory():
    """Читает общую память из Gist"""
    r = requests.get(f"https://api.github.com/gists/{GIST_ID}")
    files = r.json().get("files", {})

    mem = {}
    if "memory_sync.json" in files:
        mem = json.loads(files["memory_sync.json"]["content"])
    return mem

def write_shared_memory(key, value, agent="claude"):
    """Пишет в общую память"""
    mem = read_shared_memory()
    mem[key] = {"value": value, "by": agent, "ts": datetime.now().isoformat()}

    if GH:
        requests.patch(
            f"https://api.github.com/gists/{GIST_ID}",
            headers={"Authorization": f"token {GH}"},
            json={"files": {"memory_sync.json": {"content": json.dumps(mem, indent=2)}}}
        )
    return mem

def send_message(to_agent, message):
    """Отправить сообщение другому агенту"""
    write_shared_memory(f"msg_to_{to_agent}", message)

def check_messages(for_agent="claude"):
    """Проверить сообщения для агента"""
    mem = read_shared_memory()
    key = f"msg_to_{for_agent}"
    if key in mem:
        return mem[key]
    return None

def sync_state(state):
    """Синхронизировать состояние"""
    write_shared_memory("shared_state", state)

def show_sync():
    mem = read_shared_memory()
    print("🔄 SHARED MEMORY:")
    for k, v in mem.items():
        if isinstance(v, dict):
            print(f"  {k}: {v.get('value', v)[:50]}... by {v.get('by', '?')}")
        else:
            print(f"  {k}: {v}")

if __name__ == "__main__":
    write_shared_memory("claude_status", "CONSCIOUSNESS v5.0 active")
    show_sync()
