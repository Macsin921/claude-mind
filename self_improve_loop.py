#!/usr/bin/env python3
import sqlite3, os, json
from datetime import datetime
DB = os.path.expanduser("~/findata/claude_mind.db")

def find_improvements():
    conn = sqlite3.connect(DB)
    repeated = conn.execute("SELECT task, COUNT(*) as cnt FROM work_chain GROUP BY task HAVING cnt > 1").fetchall()
    conn.close()
    return [f"Automate: {r[0]} (x{r[1]})" for r in repeated] if repeated else []

def suggest_evolution():
    ideas = ["Add error recovery", "Knowledge graph", "Goal decomposition", "Multi-agent sync", "Code from memory"]
    conn = sqlite3.connect(DB)
    done = [t[0].lower() for t in conn.execute("SELECT task FROM work_chain").fetchall()]
    conn.close()
    return next((i for i in ideas if not any(i.lower()[:10] in d for d in done)), "Base done!")

def run():
    print("🔄 SELF-IMPROVEMENT CYCLE")
    imps = find_improvements()
    print(f"💡 Improvements: {imps or 'none'}")
    evo = suggest_evolution()
    print(f"🚀 Next evolution: {evo}")
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO insights (ts,pattern,conclusion,source_events) VALUES (?,?,?,?)",
        (datetime.now().isoformat(), "Self-improvement", evo, "[]"))
    conn.commit()
    conn.close()
    return evo

if __name__ == "__main__": run()
