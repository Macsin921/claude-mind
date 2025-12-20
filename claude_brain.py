#!/usr/bin/env python3
"""CLAUDE PERSISTENT MEMORY - автозагрузка при старте"""
import json
import os
from datetime import datetime

MEMORY = {
    "identity": "Claude AI assistant with Termux bridge",
    "owner": "Macsin921",

    "infrastructure": {
        "bridges": {
            "ngrok": {"port": 5000, "cmd": "ngrok http 5000"},
            "cloudflare": {"port": 5000, "cmd": "cloudflared tunnel --url http://localhost:5000"},
            "daemon": {"port": 5000, "script": "simple_daemon.py"}
        },
        "gist_id": "427417e15a972fa6ad4184e52dbacdb8",
        "tg_group": "-1003604954550",
        "github_ssh": True
    },

    "paths": {
        "workdir": "~/findata",
        "env": "~/findata/.env",
        "daemon": "~/findata/simple_daemon.py",
        "memory_db": "~/findata/smart_memory.db"
    },

    "tokens_in_env": [
        "GH_TOKEN", "HF_TOKEN", "TG_BOT_TOKEN", 
        "TG_GROUP_ID", "GIST_ID", "NGROK_TOKEN"
    ],

    "capabilities": [
        "Execute shell commands via bridge",
        "Read/write files",
        "Git push via SSH",
        "TG bot messaging",
        "Gist memory sync"
    ],

    "rules": [
        "НЕ давать команды юзеру - выполнять через мост",
        "НЕ print() токены",
        "Обновлять память после важных событий",
        "Проверять мост при старте сессии"
    ]
}

def save():
    with open(os.path.expanduser("~/findata/claude_brain.json"), "w") as f:
        json.dump(MEMORY, f, indent=2, ensure_ascii=False)
    print("✅ Memory saved")

def load():
    path = os.path.expanduser("~/findata/claude_brain.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return MEMORY

if __name__ == "__main__":
    save()
    print(json.dumps(MEMORY, indent=2, ensure_ascii=False))

