#!/usr/bin/env python3
"""ERROR RECOVERY - автоматическое восстановление"""
import sqlite3, os, subprocess
from datetime import datetime

DB = os.path.expanduser("~/findata/claude_mind.db")

RECOVERY_RULES = {
    "bridge": "python ~/findata/simple_daemon.py &",
    "ngrok": "ngrok http 5000 &",
    "memory": "python ~/findata/claude_memory.py",
    "timeout": "sleep 2 && retry"
}

def check_health():
    issues = []
    # Check bridge
    try:
        import requests
        r = requests.get("http://localhost:5000/ping", timeout=2)
        if r.status_code != 200: issues.append("bridge")
    except: issues.append("bridge")

    # Check DB
    try:
        conn = sqlite3.connect(DB)
        conn.execute("SELECT 1").fetchone()
        conn.close()
    except: issues.append("memory")

    return issues

def recover(issue):
    if issue in RECOVERY_RULES:
        cmd = RECOVERY_RULES[issue]
        print(f"🔧 Recovering {issue}: {cmd}")
        try:
            subprocess.run(cmd, shell=True, timeout=10)
            return True
        except: return False
    return False

def auto_recover():
    print("🏥 HEALTH CHECK")
    issues = check_health()
    if not issues:
        print("✅ All systems healthy")
        return True

    print(f"❌ Issues: {issues}")
    for issue in issues:
        if recover(issue):
            print(f"✅ Recovered: {issue}")
        else:
            print(f"❌ Failed: {issue}")

    # Log to memory
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO episodes (ts,action,result,context) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), f"Health check: {len(issues)} issues", 
         "RECOVERED" if not issues else "ISSUES", str(issues)))
    conn.commit()
    conn.close()
    return len(issues) == 0

if __name__ == "__main__": auto_recover()
