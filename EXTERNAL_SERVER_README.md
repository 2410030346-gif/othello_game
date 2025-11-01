# 🌐 External Server Management for Othello Game

## 📋 Overview

Your Othello game now supports **two storage options**:

1. **Local Storage** (Current): Stores data in `user_data.json` on your computer
2. **External Server** (New): Stores data in a centralized database accessible over network

---

## 🚀 Quick Start Guide

### Step 1: Install Server Dependencies

```powershell
pip install flask flask-cors requests
```

Or use the requirements file:
```powershell
pip install -r requirements_server.txt
```

### Step 2: Start the Authentication Server

Open a new terminal and run:
```powershell
python auth_server.py
```

You should see:
```
==================================================
🎮 OTHELLO GAME SERVER
==================================================
✅ Server starting on http://localhost:5000
📡 API Endpoints: ...
==================================================
```

**Keep this terminal running!** This is your server.

### Step 3: Test the Server (Optional)

In another terminal:
```powershell
python test_auth_server.py
```

This will:
- Create test users
- Save test game data
- Display leaderboard
- Show global statistics

### Step 4: Connect Your Game to Server

Option A: **Quick Switch** (Temporary)

In `main.py`, find this line (around line 224):
```python
from user_manager import UserManager
```

Change it to:
```python
from server_user_manager import ServerUserManager as UserManager
```

Option B: **Smart Switch** (Recommended)

Add at the top of `main.py`:
```python
# Configuration
USE_SERVER = True  # Set to False to use local storage

# Import the right manager
if USE_SERVER:
    from server_user_manager import ServerUserManager as UserManager
else:
    from user_manager import UserManager
```

Now you can easily switch between local and server storage!

---

## 📂 File Structure

```
othello_game/
│
├── auth_server.py              # Flask REST API server
├── server_user_manager.py      # Client to connect to server
├── user_manager.py              # Original local storage (kept for fallback)
├── test_auth_server.py         # Test suite for server
├── requirements_server.txt     # Server dependencies
├── SERVER_SETUP.md             # Detailed setup guide
│
├── othello_users.db            # SQLite database (created automatically)
└── user_data.json              # Local storage file (old method)
```

---

## 🔌 API Endpoints

### 1. Health Check
```http
GET http://localhost:5000/api/health
```
**Response:**
```json
{
  "status": "online",
  "message": "Othello Game Server is running"
}
```

### 2. Login/Register
```http
POST http://localhost:5000/api/login
Content-Type: application/json

{
  "email": "player@gmail.com",
  "username": "player123",
  "provider": "google"
}
```

### 3. Get User Profile
```http
GET http://localhost:5000/api/user/{user_id}
```

### 4. Save Game
```http
POST http://localhost:5000/api/game/save
Content-Type: application/json

{
  "user_id": "abc123",
  "game_mode": "vs_ai",
  "result": "win",
  "player_score": 35,
  "opponent_score": 29,
  "difficulty": "Medium",
  "duration": 120
}
```

### 5. Leaderboard
```http
GET http://localhost:5000/api/leaderboard?limit=10
```

### 6. Global Stats
```http
GET http://localhost:5000/api/stats
```

---

## 💾 Database Schema

### Users Table
| Column | Type | Description |
|--------|------|-------------|
| user_id | TEXT (PRIMARY KEY) | Unique identifier |
| email | TEXT | User's email |
| username | TEXT | Display name |
| provider | TEXT | google/facebook/google_play |
| created_at | TEXT | Account creation timestamp |
| last_login | TEXT | Last login timestamp |
| login_count | INTEGER | Total login count |

### Game History Table
| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER (AUTO) | Unique game ID |
| user_id | TEXT (FOREIGN KEY) | Player's user ID |
| game_mode | TEXT | vs_ai/vs_friend/online |
| result | TEXT | win/loss/draw |
| player_score | INTEGER | Player's final score |
| opponent_score | INTEGER | Opponent's final score |
| difficulty | TEXT | AI difficulty level |
| duration | INTEGER | Game duration (seconds) |
| timestamp | TEXT | When game was played |
| date | TEXT | Game date |

---

## 🔄 Comparison: Local vs Server Storage

| Feature | Local Storage | Server Storage |
|---------|---------------|----------------|
| **Setup** | None needed | Requires Flask server |
| **Network** | Not required | Required for multiple devices |
| **Data Location** | user_data.json | othello_users.db |
| **Multi-device** | ❌ No | ✅ Yes |
| **Leaderboards** | ❌ No | ✅ Yes |
| **Global Stats** | ❌ No | ✅ Yes |
| **Offline Play** | ✅ Yes | ❌ No |
| **Performance** | ⚡ Instant | 🌐 Network dependent |
| **Scalability** | Single user | Unlimited users |

---

## 🌍 Deploying to Production

### Option 1: Heroku (Easiest)

1. Create `Procfile`:
   ```
   web: python auth_server.py
   ```

2. Deploy:
   ```bash
   heroku login
   heroku create othello-server
   git add .
   git commit -m "Add server"
   git push heroku main
   ```

3. Your server will be at: `https://othello-server.herokuapp.com`

### Option 2: PythonAnywhere (Free Tier)

1. Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. Upload your files
3. Create new web app
4. Configure WSGI to use `auth_server.py`

### Option 3: Railway.app (Modern & Easy)

1. Connect GitHub repo
2. Railway auto-detects Python
3. Deploys automatically
4. Get URL: `https://your-app.railway.app`

### Option 4: Your Own Server (VPS)

```bash
# On server (Ubuntu/Debian)
sudo apt update
sudo apt install python3-pip
pip3 install flask flask-cors requests

# Run with Gunicorn (production server)
pip3 install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 auth_server:app
```

---

## 🔐 Security Enhancements (For Production)

### 1. Add Environment Variables

```python
# In auth_server.py
import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DATABASE = os.environ.get('DATABASE_URL', 'othello_users.db')
```

### 2. Add JWT Authentication

```powershell
pip install flask-jwt-extended
```

```python
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
```

### 3. Use PostgreSQL Instead of SQLite

```powershell
pip install psycopg2
```

```python
DATABASE = 'postgresql://user:password@localhost/othello'
```

### 4. Add Rate Limiting

```powershell
pip install flask-limiter
```

```python
from flask_limiter import Limiter
limiter = Limiter(app, default_limits=["200 per day", "50 per hour"])
```

---

## 🧪 Testing the Server

### Method 1: Use Test Script
```powershell
python test_auth_server.py
```

### Method 2: PowerShell Commands

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:5000/api/health"

# Login
$body = @{email="test@gmail.com"; username="testuser"; provider="google"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:5000/api/login" -Method Post -Body $body -ContentType "application/json"
```

### Method 3: Browser

Just open: http://localhost:5000/api/health

---

## 🆘 Troubleshooting

### Problem: "Module not found: flask"
**Solution:**
```powershell
pip install flask flask-cors requests
```

### Problem: "Address already in use"
**Solution:** Change port in `auth_server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed from 5000
```

### Problem: "Cannot connect to server"
**Solution:**
1. Make sure server is running: `python auth_server.py`
2. Check firewall settings
3. Verify URL in `server_user_manager.py`

### Problem: Database errors
**Solution:**
1. Delete `othello_users.db`
2. Restart server (will create new database)

### Problem: CORS errors (cross-origin)
**Solution:** Already handled by `flask-cors`, but if issues persist:
```python
CORS(app, resources={r"/api/*": {"origins": "*"}})
```

---

## 📊 Monitoring Your Server

### View Database Contents

```powershell
# Install sqlite viewer
pip install sqlite-web

# View database
sqlite_web othello_users.db
```

Opens browser at: http://localhost:8080

### Check Server Logs

The server terminal shows all requests in real-time:
```
127.0.0.1 - - [31/Oct/2025 10:30:15] "POST /api/login HTTP/1.1" 200 -
127.0.0.1 - - [31/Oct/2025 10:30:20] "GET /api/user/abc123 HTTP/1.1" 200 -
```

---

## 🎯 Benefits of Using External Server

✅ **Centralized Data**: All users' data in one place  
✅ **Leaderboards**: Compare scores across all players  
✅ **Global Statistics**: See total games played, average scores  
✅ **Multi-device**: Play on different computers with same account  
✅ **Backup**: Data isn't lost if local file is deleted  
✅ **Analytics**: Track player behavior and game patterns  
✅ **Social Features**: Can add friend lists, matchmaking  

---

## 📝 Next Steps

1. ✅ Start the server: `python auth_server.py`
2. ✅ Test it: `python test_auth_server.py`
3. ✅ Update your game to use it (change import in `main.py`)
4. ⬜ Deploy to cloud (Heroku/Railway/PythonAnywhere)
5. ⬜ Add more features (leaderboard display in game)
6. ⬜ Implement security enhancements for production

---

## 💡 Tips

- Keep the server running in a separate terminal while playing
- Use local storage for offline testing
- Deploy server before sharing game with friends
- Monitor database size for large user bases
- Back up `othello_users.db` regularly

---

## 📞 Need Help?

Check these files:
- `SERVER_SETUP.md` - Detailed setup instructions
- `auth_server.py` - Server source code
- `server_user_manager.py` - Client source code
- `test_auth_server.py` - Test examples

Happy gaming! 🎮🎉
