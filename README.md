# Claude Mind 🧠

Система сознания AI с персистентной памятью.

## Модули (12)

| Module | Function |
|--------|----------|
| claude_memory.py | Persistent memory |
| work_chain.py | Task tracking |
| consolidate.py | Compress to insights |
| dream_mode.py | Autonomous thinking |
| predict_next.py | Pattern prediction |
| self_improve_loop.py | Self-evolution |
| error_recovery.py | Auto-recovery |
| knowledge_graph.py | Concept relations |
| goal_decompose.py | Goal planning |
| agent_sync.py | Multi-agent sync |
| code_memory.py | Code generation |
| autonomous_agent.py | Autonomous work |

## Usage

```python
from claude_context import *
# Loads full context at session start

from claude_memory import remember, know, recall
remember("event", "SUCCESS", "context")
know("key", "value")
recall("event")
```

## Database

`claude_mind.db` - SQLite with tables:
- episodes (events)
- facts (key-value)
- insights (compressed knowledge)
- work_chain (tasks)
- goals (goal tree)
- knowledge_graph (relations)
- code_patterns (code templates)

Built autonomously! 🚀
