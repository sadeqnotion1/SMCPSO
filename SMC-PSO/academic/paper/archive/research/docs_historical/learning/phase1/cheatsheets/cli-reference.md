<!-- AUTO-GENERATED from .project/ai/edu/ - DO NOT EDIT DIRECTLY -->
<!-- Source: .project/ai/edu/phase1/cheatsheets/cli-reference.md -->
<!-- Generated: 2025-11-11 13:29:26 -->

# Command Line Reference - Quick Cheatsheet

**Platform**: Windows PowerShell (works in Command Prompt too)

------

## Navigation

| Command | Description | Example |
|---------|-------------|---------|
| `pwd` | Print working directory (where am I?) | `pwd` |
| `ls` | List files in current directory | `ls` |
| `ls -Force` | List all files (including hidden) | `ls -Force` |
| `cd <path>` | Change directory | `cd Documents` |
| `cd ..` | Go up one level | `cd ..` |
| `cd ~` | Go to home directory | `cd ~` |
| `cd \` | Go to root of drive | `cd \` |

------

## File Operations

| Command | Description | Example |
|---------|-------------|---------|
| `mkdir <name>` | Create directory | `mkdir my_project` |
| `New-Item -Path <name> -ItemType File` | Create empty file | `New-Item -Path "file.txt" -ItemType File` |
| `Copy-Item <src> <dst>` | Copy file | `Copy-Item source.txt dest.txt` |
| `Move-Item <src> <dst>` | Move/rename file | `Move-Item old.txt new.txt` |
| `Remove-Item <file>` | Delete file | `Remove-Item file.txt` |
| `Remove-Item <dir> -Recurse` | Delete directory (recursive) | `Remove-Item old_folder -Recurse` |
| `cat <file>` | Display file contents | `cat README.md` |
| `echo "text" > file` | Write to file (overwrite) | `echo "Hello" > file.txt` |
| `echo "text" >> file` | Append to file | `echo "World" >> file.txt` |

------

## System Information

| Command | Description | Example |
|---------|-------------|---------|
| `Get-ComputerInfo` | System information | `Get-ComputerInfo` |
| `$env:PATH` | Show PATH variable | `$env:PATH` |
| `Get-Process` | List running processes | `Get-Process` |
| `Get-Help <command>` | Get help for command | `Get-Help ls` |

------

## Python Commands

| Command | Description | Example |
|---------|-------------|---------|
| `python --version` | Check Python version | `python --version` |
| `python script.py` | Run Python script | `python simulate.py` |
| `python -m venv venv` | Create virtual environment | `python -m venv venv` |
| `.\venv\Scripts\Activate.ps1` | Activate venv (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| `deactivate` | Deactivate venv | `deactivate` |
| `pip install <package>` | Install package | `pip install numpy` |
| `pip install -r requirements.txt` | Install from file | `pip install -r requirements.txt` |
| `pip list` | List installed packages | `pip list` |
| `pip freeze > requirements.txt` | Save dependencies | `pip freeze > requirements.txt` |

------

## Git Commands (Quick Reference)

| Command | Description | Example |
|---------|-------------|---------|
| `git init` | Initialize repository | `git init` |
| `git status` | Check status | `git status` |
| `git add <file>` | Stage file | `git add script.py` |
| `git add .` | Stage all changes | `git add .` |
| `git commit -m "message"` | Commit changes | `git commit -m "Add feature"` |
| `git log` | View commit history | `git log` |
| `git log --oneline` | Compact log | `git log --oneline` |

------

## Useful Shortcuts

| Shortcut | Action |
|----------|--------|
| `Tab` | Auto-complete file/directory names |
| `Ctrl + C` | Cancel current command |
| `Ctrl + L` | Clear screen (or type `cls`) |
| `↑` / `↓` arrows | Navigate command history |
| `Ctrl + R` | Search command history |

------

## Common Patterns

### Navigate to Project and Activate venv

```powershell
cd ~\Desktop\my_project
.\venv\Scripts\Activate.ps1
```

### Install Multiple Packages

```powershell
pip install numpy scipy matplotlib
```

### Check if File Exists

```powershell
Test-Path file.txt
```

### Find Files by Name

```powershell
Get-ChildItem -Recurse -Filter "*.py"
```

------

## Troubleshooting

### "Command not found"

**Solution**: Command might not be installed or not in PATH

```powershell
# Check if command exists
Get-Command python
```

### "Access denied"

**Solution**: You might need administrator privileges

- Right-click PowerShell → "Run as Administrator"

### "Execution policy" error for scripts

**Solution**: Change execution policy

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

------

**Last Updated**: 2025-10-17
