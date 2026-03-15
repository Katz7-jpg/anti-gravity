# Kilo Agent Manager - SIMPLE START

## Forget Worktrees. Just This:

### Folder Structure
```
.kilocode/
├── agents/          ← WHO does the work
│   ├── wraith.md    (research/find)
│   ├── auditor.md   (verify/check)
│   └── closer.md   (execute/finish)
├── rules/           ← HOW to work
│   └── COMMANDS.md
└── memory-bank/    ← remembers stuff
```

### Only 3 Agents

| Agent | Job |
|-------|-----|
| **Wraith** | Research, find, discover |
| **Auditor** | Verify, check, audit |
| **Closer** | Execute, close, finalize |

### How to Use

**Simple query:**
```
"[your question]"
```

**Agent-specific:**
```
"Wraith: find leads for AI companies"
"Auditor: verify this lead"
"Closer: close this deal"
```

### What You Need to Know

1. **No worktrees** - Just work in main folder
2. **No complex setup** - Just use the agents
3. **Skills auto-load** from `.agent/skills/`

### Quick Command

```bash
python CODE/vault_query.py "[question]"
```

---

*Simple. Done.*
