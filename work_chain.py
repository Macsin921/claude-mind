
import sqlite3, os, json
from datetime import datetime
DB = os.path.expanduser("~/findata/claude_mind.db")

def start_task(project, task, next_step=""):
    conn = sqlite3.connect(DB)
    conn.execute("INSERT INTO work_chain (ts,project,task,status,next_step) VALUES (?,?,?,?,?)",
        (datetime.now().isoformat(), project, task, "IN_PROGRESS", next_step))
    conn.commit()
    conn.close()
    return f"Started: {project}/{task}"

def done(task_id, next_step=""):
    conn = sqlite3.connect(DB)
    conn.execute("UPDATE work_chain SET status='DONE', next_step=? WHERE id=?", (next_step, task_id))
    conn.commit()
    conn.close()

def current():
    conn = sqlite3.connect(DB)
    r = conn.execute("SELECT id,project,task,next_step FROM work_chain WHERE status='IN_PROGRESS' ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return {"id":r[0],"project":r[1],"task":r[2],"next":r[3]} if r else None

def history(n=5):
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT ts,project,task,status FROM work_chain ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    conn.close()
    return rows

def context():
    c = current()
    h = history(3)
    print("=== CURRENT WORK ===")
    if c: print(f"[{c['id']}] {c['project']}: {c['task']}")
    if c and c['next']: print(f"    NEXT: {c['next']}")
    print("\n=== RECENT ===")
    for ts,p,t,s in h:
        print(f"  [{s}] {p}: {t}")

if __name__=="__main__": context()
