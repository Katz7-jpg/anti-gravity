# Kilo Code Agent Manager - Worktree Infrastructure

This directory manages Git worktrees for parallel agent operations in Kilo Code Agent Manager.

## Why Use Worktrees?

Worktrees allow you to have multiple working directories linked to the same Git repository. This is ideal for:

- **Parallel Agent Work**: Run multiple agents simultaneously on different tasks
- **Isolation**: Each worktree is completely isolated from others
- **No Branch Switching**: Agents can work on different branches without switching
- **Clean State**: Each worktree has its own working directory, no git checkout conflicts
- **Shared History**: All worktrees share the same git history and objects

## Quick Reference Commands

### Create a New Worktree

```bash
# Create a new branch with a worktree
git worktree add <path> -b <branch-name>

# Example: Create worktree for an agent task
git worktree add ./worktrees/agent-research -b agent/research-task
```

### List Worktrees

```bash
# Show all worktrees
git worktree list
```

### Delete a Worktree

```bash
# Remove worktree (must be clean or use force)
git worktree remove <path>

# Force remove if dirty
git worktree remove --force <path>
```

### Prune Dead Worktrees

```bash
# Clean up stale worktree references
git worktree prune
```

## How to Create a New Worktree for an Agent Task

### Step 1: Create the Worktree

From the main repository (`D:/AI_FACTORY`), run:

```bash
git worktree add ./worktrees/<agent-name-task> -b <branch-name>
```

### Step 2: Navigate to the Worktree

```bash
cd ./worktrees/<agent-name-task>
```

### Step 3: Open in VS Code (Optional)

```bash
code ./worktrees/<agent-name-task>
```

### Step 4: Work on Your Task

Make changes, commits, and push as needed.

### Step 5: Clean Up (When Done)

```bash
# Remove the worktree when done
git worktree remove ./worktrees/<agent-name-task>

# Delete the branch (optional)
git branch -D <branch-name>
```

## Example Workflow

### Creating a Worktree for Research Agent

```bash
# From D:/AI_FACTORY directory
git worktree add ./worktrees/wraith-market-research -b wraith/market-research
```

This creates:
- New directory: `D:/AI_FACTORY/worktrees/wraith-market-research`
- New branch: `wraith/market-research`

### Creating a Worktree for Audit Agent

```bash
git worktree add ./worktrees/auditor-verify-claims -b auditor/verification
```

### Creating a Worktree for Execution Agent

```bash
git worktrees add ./worktrees/closer-finalize -b closer/execution
```

## Worktree Management Script

For convenience, you can use the PowerShell script:

```powershell
# Create a new worktree
.\scripts\manage-worktree.ps1 -Action create -Name "agent-name" -Branch "branch-name"

# Remove a worktree
.\scripts\manage-worktree.ps1 -Action remove -Name "agent-name"

# List all worktrees
.\scripts\manage-worktree.ps1 -Action list
```

## Current Branches Available

- `master` - Main stable branch
- `temp-branch` - Current working branch
- Agent-generated branches (e.g., `wraith/*`, `auditor/*`, `closer/*`)

## Best Practices

1. **Use Descriptive Names**: Name worktrees after the agent/task (e.g., `wraith-market-research`)
2. **Clean Up**: Remove worktrees when done to avoid clutter
3. **Push Changes**: Always push work from worktrees before removing
4. **Track Branches**: Keep branch names consistent with worktree names
5. **Avoid Conflicts**: Don't work on the same branch in multiple worktrees

## Troubleshooting

### Worktree Already Exists
```
fatal: 'path' already exists
```
Solution: Use a different path or remove existing worktree first.

### Branch Already Exists
```
fatal: branch 'name' already exists
```
Solution: Use a different branch name or checkout existing branch.

### Cannot Remove Dirty Worktree
```
error: The branch 'name' is not yet merged...
```
Solution: Either merge/stash changes, or use `--force` flag.
