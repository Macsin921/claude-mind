#!/usr/bin/env python3
"""CLAUDE MIND CLI - командная строка для мозга"""
import sys, os
sys.path.insert(0, os.path.expanduser("~/findata"))
from orchestrator import mind

def main():
    args = sys.argv[1:]

    if not args or args[0] in ["-h", "--help", "help"]:
        print("""
🧠 CLAUDE MIND CLI

Usage: cm <command> [args]

Commands:
  status, s          Show current status
  task <proj> <name> Create task
  done [name]        Complete task
  remember <k> <v>   Store fact
  recall <key>       Get fact
  insight <p> <c>    Add insight
  sync               Push to GitHub
  log <message>      Quick log

Examples:
  cm status
  cm task WORK "Fix bug"
  cm done
  cm remember api_key "xxx"
  cm insight "Pattern" "Conclusion"
        """)
        return

    cmd = args[0].lower()

    if cmd in ["status", "s"]:
        mind.status()

    elif cmd == "task" and len(args) >= 3:
        mind.task(args[1], " ".join(args[2:]))
        print(f"📌 Task created: {args[1]}: {' '.join(args[2:])}")

    elif cmd == "done":
        name = args[1] if len(args) > 1 else None
        mind.done(name)
        print("✅ Task completed")

    elif cmd == "remember" and len(args) >= 3:
        mind.remember(args[1], " ".join(args[2:]))
        print(f"💾 Remembered: {args[1]}")

    elif cmd == "recall" and len(args) >= 2:
        val = mind.recall(args[1])
        print(f"🔍 {args[1]} = {val}")

    elif cmd == "insight" and len(args) >= 3:
        mind.insight(args[1], " ".join(args[2:]))
        print(f"💡 Insight added: {args[1]}")

    elif cmd == "sync":
        mind.sync()
        print("☁️ Synced to GitHub")

    elif cmd == "log" and len(args) >= 2:
        mind._log(" ".join(args[1:]))
        print(f"📝 Logged: {' '.join(args[1:])}")

    else:
        print(f"Unknown command: {cmd}")
        print("Use 'cm help' for usage")

if __name__ == "__main__":
    main()
