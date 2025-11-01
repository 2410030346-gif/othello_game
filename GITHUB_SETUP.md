# GitHub Setup and Push Guide

## 📋 Prerequisites
- Git installed on your system
- GitHub account created
- Command line/terminal access

## 🚀 Step-by-Step Instructions

### Step 1: Install Git (if not already installed)
Download and install Git from: https://git-scm.com/downloads

Verify installation:
```bash
git --version
```

### Step 2: Configure Git (First Time Only)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 3: Create a New Repository on GitHub

1. Go to https://github.com
2. Click the "+" icon in the top right
3. Select "New repository"
4. Fill in:
   - **Repository name**: `othello-game` (or your preferred name)
   - **Description**: "Professional Othello/Reversi game with AI, animations, and sound effects"
   - **Visibility**: Public (or Private if you prefer)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### Step 4: Initialize Local Git Repository

Open PowerShell or Terminal in your project folder:
```powershell
cd C:\Users\Niranjan\OneDrive\Desktop\othello_game
```

Initialize Git:
```bash
git init
```

### Step 5: Add Files to Git

Add all files (respecting .gitignore):
```bash
git add .
```

Check what will be committed:
```bash
git status
```

### Step 6: Create Initial Commit

```bash
git commit -m "Initial commit: Complete Othello game with AI, animations, and sound"
```

### Step 7: Connect to GitHub Repository

Replace YOUR_USERNAME with your actual GitHub username:
```bash
git remote add origin https://github.com/YOUR_USERNAME/othello-game.git
```

Verify remote:
```bash
git remote -v
```

### Step 8: Push to GitHub

For first push:
```bash
git branch -M main
git push -u origin main
```

**Note**: You may be prompted for GitHub credentials. Use a Personal Access Token instead of password.

### Step 9: Create Personal Access Token (if needed)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Click "Generate token"
5. Copy the token (you won't see it again!)
6. Use this token as your password when pushing

### Step 10: Verify Upload

1. Go to your GitHub repository URL
2. Refresh the page
3. You should see all your files uploaded

---

## 🔄 Future Updates (Push Changes)

After making changes to your code:

```bash
# Check what changed
git status

# Add specific files
git add filename.py

# Or add all changes
git add .

# Commit with descriptive message
git commit -m "Add feature: describe what you changed"

# Push to GitHub
git push
```

---

## 📝 Common Git Commands

```bash
# View commit history
git log

# View brief commit history
git log --oneline

# Check current branch
git branch

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout branch-name

# View changes before commit
git diff

# Undo changes (before commit)
git checkout -- filename

# View remote repositories
git remote -v

# Pull latest changes from GitHub
git pull
```

---

## 🌿 Recommended Branch Strategy

```bash
# Create development branch
git checkout -b develop

# Make changes, then commit
git add .
git commit -m "Your message"

# Push development branch
git push -u origin develop

# Merge to main when ready
git checkout main
git merge develop
git push
```

---

## 📦 Optional: Add GitHub Topics

On your GitHub repository page:
1. Click the gear icon next to "About"
2. Add topics: `python`, `pygame`, `othello`, `reversi`, `game`, `ai`, `minimax`, `deep-learning`, `board-game`
3. Save changes

---

## 🎯 Quick Push Script

Save this as `quick_push.bat` in your project folder:

```batch
@echo off
echo Adding all changes...
git add .
echo.
set /p message="Enter commit message: "
echo.
echo Committing changes...
git commit -m "%message%"
echo.
echo Pushing to GitHub...
git push
echo.
echo Done!
pause
```

Then just double-click `quick_push.bat` to quickly commit and push changes!

---

## 🔒 Security Notes

### Files Already Ignored (.gitignore)
- `__pycache__/` - Python cache
- `*.pyc` - Compiled Python
- `game_settings.json` - User settings
- `othello_users.db` - User database
- `*.pth` - Trained models
- `.vscode/` - Editor settings
- `build/`, `dist/` - Build artifacts

### Sensitive Data
- Never commit passwords, API keys, or tokens
- Use environment variables for secrets
- Keep database files out of version control

---

## ❓ Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution**: Use HTTPS instead of SSH, or set up SSH keys

### Issue: "Failed to push some refs"
**Solution**: Pull first, then push
```bash
git pull origin main --rebase
git push
```

### Issue: "Large files detected"
**Solution**: Use Git LFS or remove large files
```bash
git rm --cached large_file.pth
```

### Issue: "Authentication failed"
**Solution**: Use Personal Access Token instead of password

---

## 📊 Repository Stats

After pushing, you can:
- Add a LICENSE file (MIT recommended)
- Create GitHub Actions for CI/CD
- Enable GitHub Pages for documentation
- Add issue templates
- Create a CONTRIBUTING.md file
- Set up branch protection rules

---

## 🎉 Success!

Your Othello game is now on GitHub! 🎮

**Next steps:**
1. Add a nice screenshot to the README
2. Write detailed documentation
3. Invite collaborators
4. Share your repository
5. Get stars! ⭐

---

**Repository URL Format:**
```
https://github.com/YOUR_USERNAME/othello-game
```

**Clone Command for Others:**
```bash
git clone https://github.com/YOUR_USERNAME/othello-game.git
```

---

*Need help? Check GitHub Docs: https://docs.github.com*
