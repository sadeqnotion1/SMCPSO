<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/cheatsheets/git-commands.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Git Commands - Quick Cheatsheet

**Version Control Essentials for Beginners**

------

## Setup and Configuration

| Command | Description | Example |
|---------|-------------|---------|
| `git --version` | Check Git version | `git --version` |
| `git config --global user.name "Name"` | Set your name | `git config --global user.name "Alice"` |
| `git config --global user.email "email"` | Set your email | `git config --global user.email "alice@example.com"` |
| `git config --list` | View all settings | `git config --list` |

------

## Creating Repositories

| Command | Description | Example |
|---------|-------------|---------|
| `git init` | Initialize new repository | `git init` |
| `git clone <url>` | Clone existing repository | `git clone https://github.com/user/repo.git` |

------

## Basic Workflow

### 1. Check Status

```bash
git status
```

Shows:
- Modified files
- Staged files
- Untracked files

### 2. Stage Changes

```bash
git add file.py          # Stage specific file
git add .                # Stage all changes
git add *.py             # Stage all .py files
```

### 3. Commit Changes

```bash
git commit -m "Descriptive message"
```

**Good commit messages**:
- "Add login functionality"
- "Fix bug in calculation"
- "Update documentation for API"

**Bad commit messages**:
- "Update"
- "Changes"
- "Fix stuff"

### 4. View History

```bash
git log                  # Full history
git log --oneline        # Compact view
git log --graph          # Visual graph
```

------

## Viewing Changes

| Command | Description | Example |
|---------|-------------|---------|
| `git diff` | Show unstaged changes | `git diff` |
| `git diff --staged` | Show staged changes | `git diff --staged` |
| `git diff HEAD~1` | Compare to previous commit | `git diff HEAD~1` |
| `git show <commit>` | Show specific commit | `git show abc1234` |

------

## Branching

| Command | Description | Example |
|---------|-------------|---------|
| `git branch` | List branches | `git branch` |
| `git branch <name>` | Create new branch | `git branch feature` |
| `git checkout <name>` | Switch to branch | `git checkout feature` |
| `git checkout -b <name>` | Create and switch | `git checkout -b feature` |
| `git merge <branch>` | Merge branch into current | `git merge feature` |
| `git branch -d <name>` | Delete branch | `git branch -d feature` |

------

## Remote Repositories

| Command | Description | Example |
|---------|-------------|---------|
| `git remote -v` | List remotes | `git remote -v` |
| `git remote add origin <url>` | Add remote | `git remote add origin https://...` |
| `git push origin <branch>` | Push to remote | `git push origin main` |
| `git push -u origin <branch>` | Push and set upstream | `git push -u origin main` |
| `git pull` | Fetch and merge from remote | `git pull` |
| `git fetch` | Fetch without merging | `git fetch` |

------

## Undoing Changes

| Command | Description | Example |
|---------|-------------|---------|
| `git restore <file>` | Discard changes (unstaged) | `git restore file.py` |
| `git restore --staged <file>` | Unstage file | `git restore --staged file.py` |
| `git reset HEAD~1` | Undo last commit (keep changes) | `git reset HEAD~1` |
| `git reset --hard HEAD~1` | Undo last commit (discard changes) | `git reset --hard HEAD~1` |
| `git revert <commit>` | Create new commit that undoes | `git revert abc1234` |

**⚠️ WARNING**: `git reset --hard` permanently deletes changes!

------

## Common Workflows

### Workflow 1: Local Development

```bash
# Make changes to code
# ...

# Check what changed
git status
git diff

# Stage and commit
git add .
git commit -m "Add new feature"

# View history
git log --oneline
```

### Workflow 2: Working with GitHub

```bash
# Clone repository
git clone https://github.com/user/repo.git
cd repo

# Make changes
# ...

# Commit changes
git add .
git commit -m "Fix bug"

# Push to GitHub
git push origin main
```

### Workflow 3: Feature Branch

```bash
# Create feature branch
git checkout -b feature-login

# Make changes and commit
git add .
git commit -m "Add login page"

# Switch back to main
git checkout main

# Merge feature
git merge feature-login

# Delete feature branch
git branch -d feature-login
```

------

## Inspecting Repository

| Command | Description | Example |
|---------|-------------|---------|
| `git log --oneline` | Compact commit history | `git log --oneline` |
| `git log --graph --all` | Visual branch history | `git log --graph --all` |
| `git blame <file>` | Show who changed each line | `git blame file.py` |
| `git show <commit>:<file>` | Show file at specific commit | `git show abc1234:file.py` |

------

## .gitignore

Create a `.gitignore` file to exclude files from version control:

```
# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project-specific
*.log
data/
results/
```

------

## Useful Aliases

Add to your Git config for shortcuts:

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'restore --staged'
```

Now you can use:

```bash
git st      # Instead of git status
git co main # Instead of git checkout main
```

------

## Common Scenarios

### Scenario 1: Undo Last Commit (Keep Changes)

```bash
git reset HEAD~1
# Edit files
git add .
git commit -m "Better commit message"
```

### Scenario 2: Discard All Local Changes

```bash
git restore .
```

### Scenario 3: See What Changed in Last Commit

```bash
git show HEAD
```

### Scenario 4: Commit Only Part of a File

```bash
git add -p file.py
# Interactive: choose which chunks to stage
```

------

## Troubleshooting

### Problem: Merge Conflict

```
Auto-merging file.py
CONFLICT (content): Merge conflict in file.py
```

**Solution**:
1. Open `file.py` and look for conflict markers:
   ```
   <<<<<<< HEAD
   Your changes
   =======
   Their changes
   >>>>>>> branch-name
   ```
2. Edit to resolve conflict
3. Remove markers
4. Stage and commit:
   ```bash
   git add file.py
   git commit -m "Resolve merge conflict"
   ```

### Problem: Accidentally Committed to Wrong Branch

**Solution**:
```bash
# On wrong-branch
git reset HEAD~1     # Undo commit, keep changes
git stash            # Save changes temporarily

git checkout correct-branch
git stash pop        # Apply saved changes
git add .
git commit -m "Message"
```

### Problem: Forgot to Add File to Last Commit

**Solution**:
```bash
git add forgotten-file.py
git commit --amend --no-edit
```

------

## Git Best Practices

1. **Commit often**: Small, focused commits are better than large ones
2. **Write good messages**: Explain "why", not "what"
3. **Don't commit secrets**: Never commit passwords, API keys, etc.
4. **Pull before push**: Avoid conflicts by staying up-to-date
5. **Use branches**: Keep main branch stable, experiment in branches
6. **Review before commit**: Always check `git diff` and `git status`

------

**Last Updated**: 2025-10-17
**More Info**: https://git-scm.com/doc
