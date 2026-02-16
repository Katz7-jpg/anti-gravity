# Agent Instructions (AGENTS.md)

> **Note to Agents:** This file is the source of truth for all development standards in this repository.
> Always consult this file before writing or modifying code.

## Memory Bank

This project uses a comprehensive memory bank located at [`.kilocode/memory-bank.md`](.kilocode/memory-bank.md).

**Before starting any task:**
1. Read the memory bank index for context
2. Review relevant memory bank files based on task type
3. Check progress.md for current project status

---

## 1. Build, Lint, and Test Commands

### 1.1 Build Process
* **Command:** `python -m build` (for Python packages)
* **Artifacts:** Generated in `dist/` directory
* **Environment:** Ensure `.env` is configured with required API keys

### 1.2 Linting & Formatting
* **Linter:** Ruff (Python), ESLint (JavaScript/TypeScript)
* **Command:** `ruff check .` or `npm run lint`
* **Fix Command:** `ruff check --fix .` or `npm run lint:fix`
* **Style Guide:** Follow PEP 8 for Python, Airbnb style for JS/TS

### 1.3 Testing Strategy
* **Run All Tests:** `pytest` (Python) or `npm test` (JS/TS)
* **Run Single Test File:**
    * Python: `pytest path/to/file.py`
    * JS/TS: `npm test -- path/to/file.test.ts`
* **Run Single Test Case:**
    * Python: `pytest -k "test_name"`
    * JS/TS: `npm test -- -t "test name"`
* **Coverage:** Minimum 80% coverage required

---

## 2. Code Style & Conventions

### 2.1 File Organization & Imports
* **Grouping:**
    1. Standard Library / Built-ins
    2. Third-party dependencies
    3. Internal/Project modules
    4. Relative imports
* **Cleanup:** Remove all unused imports before committing
* **Exports:** Prefer named exports for consistency

### 2.2 Formatting Rules
* **Indentation:** 4 spaces (Python), 2 spaces (JS/TS)
* **Line Length:** 100 characters
* **Quotes:** Single quotes for Python, double quotes for JS/TS
* **Semicolons:** Always for JS/TS

### 2.3 Naming Conventions
* **Variables:** `snake_case` (Python), `camelCase` (JS/TS)
* **Functions:** `snake_case` (Python), `camelCase` (JS/TS)
* **Classes:** `PascalCase`
* **Constants:** `UPPER_SNAKE_CASE` for global constants
* **Booleans:** Prefix with `is`, `has`, `should`, `can`

### 2.4 Type Safety
* **Python:** Use type hints for all function signatures
* **TypeScript:** Strict mode enabled, avoid `any`
* **Return Types:** Explicitly define return types for all public functions

### 2.5 Error Handling
* **Exceptions:** Use custom error classes where possible
* **Async/Await:** Use `try/catch` blocks for async operations
* **Logging:** Use the project's logger, avoid `print` or `console.log`

### 2.6 Comments & Documentation
* **Self-Documenting Code:** Prefer clear naming over comments
* **Docstrings:** Required for all exported functions and classes
* **Complex Logic:** Explain the *why*, not the *what*

---

## 3. Project Architecture

### 3.1 Directory Structure
```
AI_FACTORY/
├── .kilocode/           # KiloCode configuration and memory bank
├── .agent/              # Shared agent files
├── Operation-Peanut/    # Main skill implementations
│   ├── skills/          # ToolUniverse skills
│   └── AGENTS.md        # Detailed instructions
├── .env                 # API keys (never commit)
└── AGENTS.md            # This file
```

### 3.2 Key Components
* **Memory Bank:** `.kilocode/memory-bank.md` - Project context and knowledge
* **Skills:** `Operation-Peanut/skills/` - ToolUniverse skill implementations
* **Configuration:** `opencode.json` - AI model configuration

---

## 4. Agent Operational Rules

### 4.1 Planning Phase
1. **Read Memory Bank:** Start with `.kilocode/memory-bank.md`
2. **Explore:** Use `list_files` to understand the file structure
3. **Check Skills:** Verify available skills in `Operation-Peanut/skills/`
4. **Read Config:** Check `opencode.json` for model configuration

### 4.2 Implementation Phase
1. **Atomic Changes:** Keep changes small and focused
2. **Verify:** Run tests for modified files
3. **Fix:** Address any linting errors immediately
4. **Update Memory Bank:** Update relevant memory bank files if needed

---

## 5. ToolUniverse Skills Integration

This repository is equipped with **ToolUniverse** agent skills, providing access to 10,000+ scientific and development tools.

### 5.1 Core Philosophy
* **Search Widely:** Use tool finders to discover relevant tools before starting research
* **Multi-Hop:** Scientific queries often require chains of 3-5 tool calls
* **Clarify First:** If a request is ambiguous, ask for clarification

### 5.2 Key Skills by Domain
| Domain | Primary Skill | Location |
|--------|---------------|----------|
| Drug Research | `tooluniverse-drug-research` | `Operation-Peanut/skills/` |
| Clinical Trials | `tooluniverse-clinical-trial-design` | `Operation-Peanut/skills/` |
| Antibody Design | `tooluniverse-antibody-engineering` | `Operation-Peanut/skills/` |
| CRISPR Analysis | `tooluniverse-crispr-screen-analysis` | `Operation-Peanut/skills/` |
| Literature | `tooluniverse-literature-deep-research` | `Operation-Peanut/skills/` |

### 5.3 Skill Documentation
Each skill contains:
- `SKILL.md` - Main skill definition
- `EXAMPLES.md` - Example workflows
- `CHECKLIST.md` - Validation checklist
- `QUICK_START.md` - Quick start guide

---

## 6. API Configuration

### 6.1 Required API Keys
Configure in `.env` file:
```
NCBI_API_KEY=your_key
CHEMBL_API_KEY=your_key
CLINICALTRIALS_API_KEY=your_key
```

### 6.2 API Key Reference
See `Operation-Peanut/skills/setup-tooluniverse/API_KEYS_REFERENCE.md` for complete list.

---

## 7. Related Documentation

| Document | Purpose |
|----------|---------|
| [Memory Bank](.kilocode/memory-bank.md) | Project context and knowledge |
| [Operation-Peanut AGENTS.md](Operation-Peanut/AGENTS.md) | Detailed development guidelines |
| [ToolUniverse Overview](.kilocode/memory-bank/tooluniverse-overview.md) | Skills ecosystem documentation |
| [Skills Index](.kilocode/memory-bank/tooluniverse-skills-index.md) | Complete skills catalog |

---

*Last Updated: 2026-02-16*
