# Agent Instructions (AGENTS.md)

> **Note to Agents:** This file is the source of truth for all development standards in this repository.
> Always consult this file before writing or modifying code.

## 1. Build, Lint, and Test Commands

### 1.1 Build Process
*   **Command:** `[npm run build | cargo build | ...]`
*   **Artifacts:** generated in `[dist/ | target/ | ...]`
*   **Environment:** Ensure `.env` is configured if required.

### 1.2 Linting & Formatting
*   **Linter:** `[ESLint | Ruff | Clippy | ...]`
*   **Command:** `[npm run lint]`
*   **Fix Command:** `[npm run lint:fix]`
*   **Style Guide:** Adhere to `[Airbnb | Google | ...]` style if applicable.
*   **Pre-commit:** Verify if `husky` or similar hooks are active.

### 1.3 Testing Strategy
*   **Run All Tests:** `[npm test | pytest | cargo test]`
*   **Run Single Test File:**
    *   JS/TS: `npm test -- path/to/file.test.ts`
    *   Python: `pytest path/to/file.py`
*   **Run Single Test Case:**
    *   JS/TS: `npm test -- -t "test name"`
    *   Python: `pytest -k "test_name"`
*   **Coverage:** Minimum `[80%]` coverage required.
*   **Snapshot Testing:** If snapshots fail, inspect carefully before updating.

---

## 2. Code Style & Conventions

### 2.1 File Organization & Imports
*   **Grouping:**
    1.  Standard Library / Built-ins
    2.  Third-party dependencies
    3.  Internal/Project modules (using absolute paths/aliases like `@/components` if available)
    4.  Relative imports (siblings)
    5.  Styles / Assets
*   **Cleanup:** Remove all unused imports before committing.
*   **Exports:** Prefer `[named | default]` exports for consistency.

### 2.2 Formatting Rules
*   **Indentation:** `[2 spaces | 4 spaces]`
*   **Line Length:** `[80 | 100 | 120]` characters.
*   **Quotes:** `[Single | Double]` quotes.
*   **Semicolons:** `[Always | Never]` (for JS/TS).
*   **Trailing Commas:** `[ES5 | All | None]`.

### 2.3 Naming Conventions
*   **Variables:** `camelCase` (e.g., `userData`, `retryCount`)
*   **Functions:** `camelCase` (verbs first: `getUser`, `calculateTotal`)
*   **Classes/Components:** `PascalCase` (e.g., `UserProfile`, `PaymentGateway`)
*   **Constants:** `UPPER_SNAKE_CASE` for global constants (e.g., `MAX_RETRIES`)
*   **Files:**
    *   React Components: `PascalCase.tsx`
    *   Utilities/Hooks: `camelCase.ts` or `kebab-case.ts`
*   **Booleans:** Prefix with `is`, `has`, `should`, `can` (e.g., `isVisible`, `hasAccess`).

### 2.4 Type Safety (TypeScript/Typed Python)
*   **Strict Mode:** Treat as enabled.
*   **No Any:** Avoid `any` type. Use `unknown` or specific interfaces.
*   **Interfaces:** Use `interface` for object definitions, `type` for unions/primitives.
*   **Return Types:** Explicitly define return types for all public functions.

### 2.5 Error Handling
*   **Exceptions:** Use custom error classes where possible.
*   **Async/Await:** Use `try/catch` blocks for async operations.
*   **Validation:** Validate inputs at boundaries (API, UI inputs).
*   **Logging:** Use the project's logger. **DO NOT** leave `console.log` or `print` statements.

### 2.6 Comments & Documentation
*   **Self-Documenting Code:** Prefer clear naming over comments.
*   **JSDoc/Docstrings:** Required for all exported functions and classes.
    *   Include `@param`, `@returns`, and `@throws` tags.
*   **Complex Logic:** Explain the *why*, not the *what*.
*   **TODOs:** `TODO(username): description` - do not leave strict TODOs without tracking.

---

## 3. Project Architecture

### 3.1 Directory Structure
*   `src/` - Application source code
    *   `components/` - Reusable UI components
    *   `lib/` - Utility functions and helpers
    *   `services/` - API integration and business logic
*   `skills/` - **ToolUniverse Agent Skills** (Symlinked from user config)
    *   Contains specialized research and dev tools.
*   `tests/` - Unit and integration tests
*   `docs/` - Project documentation

---

## 4. Agent Operational Rules

### 4.1 Planning Phase
1.  **Explore:** Use `ls -R` or similar to understand the file structure.
2.  **Check Skills:** Verify available skills in `skills/` before re-implementing functionality.
3.  **Read Config:** Check `package.json`, `tsconfig.json`, or equivalent first.

### 4.2 Implementation Phase
1.  **Atomic Changes:** Keep changes small and focused.
2.  **Verify:** Run the **specific test** for the modified file.
3.  **Fix:** Address any linting errors immediately.

---

## 5. ToolUniverse Skills Integration

This repository is equipped with **ToolUniverse** agent skills, located in the `skills/` directory. These provide 10000+ scientific and development tools.

### 5.1 Core Philosophy
*   **Search Widely:** Use tool finders (e.g., `Tool_Finder_Keyword`) to discover relevant tools before starting research.
*   **Multi-Hop:** Scientific queries often require chains of 3-5 tool calls to gather comprehensive data.
*   **Clarify First:** If a request is ambiguous (e.g., "Research cancer"), ask for clarification (type, aspect) before initiating tool use.

### 5.2 Discovery & Usage
*   **Find Tools:** Use `npx skills find [query]` to locate new capabilities.
*   **Install:** Use `npx skills add [package]` to add new skills.
*   **Documentation:** Refer to `skills/[skill-name]/SKILL.md` for specific usage patterns.

---

## 6. Specific Rules (Cursor / Copilot)

### 6.1 Cursor Rules (.cursor/rules)
*(Copy relevant content from .cursor/rules/ here)*
*   [Rule 1 Placeholder]
*   [Rule 2 Placeholder]

### 6.2 Copilot Instructions
*(Copy relevant content from .github/copilot-instructions.md here)*
*   [Instruction 1 Placeholder]
*   [Instruction 2 Placeholder]
