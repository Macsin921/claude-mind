#!/usr/bin/env python3
import sqlite3, os
DB = os.path.expanduser("~/findata/claude_mind.db")
print("="*50)
print("🧠 CLAUDE CONTEXT v3.0")
print("="*50)
conn = sqlite3.connect(DB)

print("\n📍 CURRENT TASK:")
cur = conn.execute("SELECT id,project,task,next_step FROM work_chain WHERE status='IN_PROGRESS' ORDER BY id DESC LIMIT 1").fetchone()
if cur:
    print(f"   [{cur[0]}] {cur[1]}: {cur[2]}")
    if cur[3]: print(f"   NEXT → {cur[3]}")

print("\n💡 KEY INSIGHTS:")
for p,c in conn.execute("SELECT pattern, conclusion FROM insights ORDER BY id DESC LIMIT 3").fetchall():
    print(f"   • {p[:35]}")
    print(f"     → {c[:40]}")

print("\n📜 RECENT WORK:")
for ts,proj,task,s in conn.execute("SELECT ts,project,task,status FROM work_chain ORDER BY id DESC LIMIT 4").fetchall():
    icon = "✅" if s=="DONE" else "🔄"
    print(f"   {icon} {proj}: {task[:30]}")

print("\n📋 CORE FACTS:")
for k,v in conn.execute("SELECT key,value FROM facts LIMIT 5").fetchall():
    print(f"   {k}: {v[:25]}")

conn.close()
print("\n" + "="*50)
