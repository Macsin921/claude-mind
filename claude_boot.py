#!/usr/bin/env python3
"""claude_boot.py - выдаёт контекст для Claude при старте сессии"""
import sys
sys.path.insert(0, "/data/data/com.termux/files/home/findata")
from claude_memory import recall, recent_episodes, status
import json

print("=" * 50)
print("CLAUDE MEMORY BOOT")
print("=" * 50)

# Факты
facts = ["owner", "workdir", "gist_public", "tg_group", "bridge_port", "github_ssh"]
print("\n📋 FACTS:")
for f in facts:
    v = recall(f)
    if v: print(f"  {f}: {v}")

# Статус
print(f"\n📊 STATUS: {status()}")

# Последние действия
print("\n📜 RECENT EPISODES:")
for ts, action, result in recent_episodes(5):
    print(f"  [{ts[:16]}] {action[:50]} → {result[:20]}")

print("\n" + "=" * 50)
print("Ready. Use: from claude_memory import *")
