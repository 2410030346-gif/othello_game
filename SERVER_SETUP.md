# 🌐 External Server Setup Guide for Othello Game

## Overview
This guide explains how to set up and use an external server for user authentication and game data storage instead of local JSON files.

## 📁 Files Created

1. **`auth_server.py`** - Flask REST API server
2. **`server_user_manager.py`** - Client to connect to the server
3. **`requirements_server.txt`** - Python dependencies

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```powershell
pip install -r requirements_server.txt
```

This installs:
- Flask (web framework)
- Flask-CORS (allow cross-origin requests)
- Requests (HTTP client library)

### Step 2: Start the Server

```powershell
python auth_server.py
```

You should see:
```
==================================================
🎮 OTHELLO GAME SERVER
==================================================
✅ Server starting on http://localhost:5000
📡 API Endpoints:
   GET  /api/health - Health check
   POST /api/login - Login/Register user
   GET  /api/user/<user_id> - Get user profile
   POST /api/game/save - Save game history
   GET  /api/leaderboard - Get top players
   GET  /api/stats - Global statistics
==================================================
```

### Step 3: Update Your Game to Use Server

In `main.py`, replace the import:

```python
# OLD (local storage)
from user_manager import UserManager

# NEW (server storage)
from server_user_manager import ServerUserManager as UserManager
```

That's it! Your game now uses the external server! 🎉

---

## 🔧 API Endpoints

### 1. Health Check
```http
GET /api/health
```
Response:
```json
{
  "status": "online",
  "message": "Othello Game Server is running",
  "timestamp": "2025-10-31T10:30:00"
}
```

### 2. Login/Register User
```http
POST /api/login
Content-Type: application/json

{
  "email": "player@gmail.com",
  "username": "player123",
  "provider": "google"
}
```
Response:
```json
{
  "user_id": "abc123def456",
  "email": "player@gmail.com",
  "username": "player123",
  "provider": "google",
  "login_count": 1,
  "message": "Account created successfully!"
}
```

### 3. Get User Profile
```http
GET /api/user/<user_id>
```
Response:
```json
{
  "user_id": "abc123def456",
  "email": "player@gmail.com",
  "username": "player123",
  "stats": {
    "total_games": 15,
    "wins": 10,
    "losses": 5,
    "win_rate": 66.67,
    "highest_score": 45
  },
  "game_history": [...]
}
```

### 4. Save Game History
```http
POST /api/game/save
Content-Type: application/json

{
  "user_id": "abc123def456",
  "game_mode": "vs_ai",
  "result": "win",
  "player_score": 35,
  "opponent_score": 29,
  "difficulty": "Medium",
  "duration": 120
}
```

### 5. Get Leaderboard
```http
GET /api/leaderboard?limit=10
```
Response:
```json
[
  {
    "username": "player123",
    "total_games": 20,
    "wins": 15,
    "win_rate": 75.0
  },
  ...
]
```

### 6. Global Statistics
```http
GET /api/stats
```
Response:
```json
{
  "total_users": 150,
  "total_games": 2500,
  "average_score": 32.5
}
```

---

## 💾 Database

The server uses **SQLite** database (`othello_users.db`) with two tables:

### Users Table
```sql
- user_id (PRIMARY KEY)
- email
- username
- provider (google/facebook/google_play)
- created_at
- last_login
- login_count
```

### Game History Table
```sql
- id (AUTO INCREMENT)
- user_id (FOREIGN KEY)
- game_mode
- result (win/loss/draw)
- player_score
- opponent_score
- difficulty
- duration (seconds)
- timestamp
- date
```

---

## 🌍 Deploy to Production

### Option 1: Deploy to Heroku (Free Tier)

1. Create `Procfile`:
```
web: python auth_server.py
```

2. Deploy:
```bash
heroku login
heroku create othello-game-server
git push heroku main
```

### Option 2: Deploy to PythonAnywhere

1. Sign up at pythonanywhere.com
2. Upload your files
3. Create a new web app
4. Point WSGI configuration to `auth_server.py`

### Option 3: Deploy to AWS/Google Cloud/Azure

1. Use EC2/Compute Engine/VM
2. Install dependencies
3. Run with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 auth_server:app
```

### Option 4: Deploy to Railway.app

1. Connect your GitHub repo
2. Railway auto-detects Python
3. Add environment variables if needed
4. Deploy automatically

---

## 🔐 Production Improvements

For production use, add these enhancements:

### 1. Use PostgreSQL instead of SQLite
```python
# Install: pip install psycopg2
DATABASE = 'postgresql://user:password@host:5432/dbname'
```

### 2. Add Authentication
```python
# Install: pip install flask-jwt-extended
from flask_jwt_extended import JWTManager, create_access_token
```

### 3. Add Rate Limiting
```python
# Install: pip install flask-limiter
from flask_limiter import Limiter
```

### 4. Add HTTPS
```python
# Use nginx reverse proxy or Flask-SSLify
```

### 5. Environment Variables
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key')
DATABASE = os.environ.get('DATABASE_URL', 'sqlite:///othello_users.db')
```

---

## 🧪 Testing the API

### Using PowerShell:

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get

# Login User
$body = @{
    email = "test@gmail.com"
    username = "testuser"
    provider = "google"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method Post -Body $body -ContentType "application/json"

# Get User Profile
Invoke-RestMethod -Uri "http://localhost:5000/api/user/abc123" -Method Get
```

### Using Python:

```python
import requests

# Login
response = requests.post('http://localhost:5000/api/login', json={
    'email': 'test@gmail.com',
    'username': 'testuser',
    'provider': 'google'
})
print(response.json())
```

---

## 📊 Monitoring

View logs in real-time:
```powershell
python auth_server.py
```

Access database:
```powershell
# Install: pip install sqlite-web
sqlite_web othello_users.db
```

---

## 🔄 Switching Between Local and Server Storage

### Keep Both Options Available

```python
# In main.py
USE_SERVER = True  # Set to False for local storage

if USE_SERVER:
    from server_user_manager import ServerUserManager as UserManager
else:
    from user_manager import UserManager
```

---

## 🆘 Troubleshooting

### Server won't start
- Check if port 5000 is already in use
- Change port: `app.run(port=5001)`

### Connection refused
- Make sure server is running
- Check firewall settings
- Verify server URL in `server_user_manager.py`

### Database errors
- Delete `othello_users.db` and restart
- Check file permissions

### CORS errors
- Flask-CORS should handle this
- If issues persist, add: `CORS(app, resources={r"/api/*": {"origins": "*"}})`

---

## 📝 Summary

✅ **Local Storage (Current)**
- File: `user_data.json`
- No setup required
- Works offline
- Limited to one machine

✅ **Server Storage (New)**
- File: `othello_users.db` (on server)
- Requires Flask server running
- Works across network
- Centralized data
- Supports leaderboards
- Production-ready with proper deployment

Choose based on your needs! Both systems work with the same game code.
