# 🎮 Othello Game - Social Features Guide

## 🌟 New Features Added

Your Othello game server now includes:

1. **👥 Friend System** - Add friends, send requests, manage friend lists
2. **🏆 Achievement System** - 12 unlockable achievements with points
3. **📊 Enhanced Statistics** - Detailed player stats and global leaderboards

---

## 🏆 Achievement System

### Available Achievements

| Icon | Name | Description | Requirement | Points |
|------|------|-------------|-------------|--------|
| 🏆 | First Victory | Win your first game | Win 1 game | 10 |
| 🔥 | Winning Streak | Win 3 games in a row | 3-win streak | 25 |
| 👑 | Game Master | Win 10 games | Win 10 games | 50 |
| 💎 | Perfect Game | Win with 64-0 score | Perfect victory | 100 |
| 🎮 | Beginner | Play 5 games | Play 5 games | 10 |
| 🎯 | Experienced | Play 25 games | Play 25 games | 30 |
| ⭐ | Veteran | Play 100 games | Play 100 games | 75 |
| 🤖 | AI Challenger | Beat Hard AI | Win vs Hard AI | 50 |
| 👥 | Social Player | Play 10 games with friends | 10 vs friend games | 30 |
| 💯 | High Scorer | Score 60+ in a single game | Score 60+ | 40 |
| 🎪 | Comeback King | Win after being behind by 20 | Comeback win | 75 |
| ⚡ | Speed Demon | Win a game in under 2 minutes | Win in <120s | 50 |

**Total Possible Points: 545**

### How Achievements Work

1. **Automatic Detection**: Achievements are checked automatically after each game
2. **Persistent**: Once unlocked, achievements are saved forever
3. **Point System**: Earn points for harder achievements
4. **Progress Tracking**: Server tracks all stats needed for achievements

---

## 👥 Friend System

### Features

- **Send Friend Requests** by email
- **Accept/Reject Requests**
- **View Friends List** with their stats
- **Remove Friends** when needed
- **See Friend Activity** - games played, win rates

### Friend Request Flow

```
User A                    Server                    User B
  |                         |                         |
  |--Send Request---------->|                         |
  |   (friend_email)        |                         |
  |                         |--Notify---------------->|
  |                         |                         |
  |                         |<--Accept Request--------|
  |<--Notification----------|                         |
  |                         |                         |
  |         Now Friends!                              |
```

### Friend Status Types

- **pending** - Request sent, waiting for acceptance
- **accepted** - Active friendship
- **removed** - Friendship ended

---

## 📡 New API Endpoints

### Friend System

#### 1. Send Friend Request
```http
POST /api/friends/add
Content-Type: application/json

{
  "user_id": "abc123",
  "friend_email": "friend@gmail.com"
}
```

**Response:**
```json
{
  "message": "Friend request sent to Bob",
  "friend_username": "Bob"
}
```

#### 2. Accept Friend Request
```http
POST /api/friends/accept
Content-Type: application/json

{
  "user_id": "abc123",
  "friend_id": "def456"
}
```

#### 3. Get Friends List
```http
GET /api/friends/list/{user_id}
```

**Response:**
```json
[
  {
    "user_id": "def456",
    "username": "Bob",
    "email": "bob@gmail.com",
    "friends_since": "2025-10-31 10:30:00",
    "total_games": 15,
    "wins": 10,
    "win_rate": 66.67
  }
]
```

#### 4. Get Pending Requests
```http
GET /api/friends/requests/{user_id}
```

#### 5. Remove Friend
```http
POST /api/friends/remove
Content-Type: application/json

{
  "user_id": "abc123",
  "friend_id": "def456"
}
```

### Achievement System

#### 1. Get All Achievements
```http
GET /api/achievements
```

**Response:**
```json
[
  {
    "achievement_id": "first_win",
    "name": "First Victory",
    "description": "Win your first game",
    "icon": "🏆",
    "requirement_type": "wins",
    "requirement_value": 1,
    "points": 10
  }
]
```

#### 2. Get User Achievements
```http
GET /api/achievements/{user_id}
```

**Response:**
```json
{
  "unlocked_achievements": [
    {
      "achievement_id": "first_win",
      "name": "First Victory",
      "description": "Win your first game",
      "icon": "🏆",
      "points": 10,
      "unlocked_at": "2025-10-31 10:30:00"
    }
  ],
  "total_achievements": 1,
  "total_points": 10
}
```

#### 3. Check/Unlock Achievements
```http
POST /api/achievements/check
Content-Type: application/json

{
  "user_id": "abc123"
}
```

**Response:**
```json
{
  "newly_unlocked": [
    {
      "achievement_id": "winning_streak",
      "name": "Winning Streak",
      "description": "Win 3 games in a row",
      "icon": "🔥",
      "points": 25
    }
  ],
  "message": "1 new achievements unlocked!"
}
```

---

## 🚀 Quick Start

### 1. Start the Server

```powershell
python auth_server.py
```

You should see:
```
==================================================
🎮 OTHELLO GAME SERVER WITH SOCIAL FEATURES
==================================================
✅ Server starting on http://localhost:5000

📡 API Endpoints:

🔐 Authentication:
   GET  /api/health - Health check
   POST /api/login - Login/Register user
   GET  /api/user/<user_id> - Get user profile

🎮 Game Management:
   POST /api/game/save - Save game history
   GET  /api/leaderboard - Get top players
   GET  /api/stats - Global statistics

👥 Friend System:
   POST /api/friends/add - Send friend request
   POST /api/friends/accept - Accept friend request
   GET  /api/friends/list/<user_id> - Get friends list
   GET  /api/friends/requests/<user_id> - Get pending requests
   POST /api/friends/remove - Remove friend

🏆 Achievement System:
   GET  /api/achievements - Get all achievements
   GET  /api/achievements/<user_id> - Get user achievements
   POST /api/achievements/check - Check/unlock achievements
==================================================
```

### 2. Test Social Features

```powershell
python test_social_features.py
```

This will:
- Create 4 test users
- Generate game history
- Send friend requests
- Accept friendships
- Unlock achievements
- Display leaderboard

### 3. Use in Your Game

Update `main.py`:
```python
from server_user_manager import ServerUserManager

# Initialize
user_manager = ServerUserManager("http://localhost:5000")

# After a game ends
user_manager.check_achievements(user_id)

# Add a friend
user_manager.add_friend(user_id, "friend@gmail.com")

# Get achievements
achievements = user_manager.get_user_achievements(user_id)
print(f"Total Points: {achievements['total_points']}")
```

---

## 💡 Integration Examples

### Example 1: Show Achievement Notification

```python
def on_game_end(user_id):
    # Check for new achievements
    result = user_manager.check_achievements(user_id)
    
    # Show notifications
    for achievement in result['newly_unlocked']:
        print(f"🎉 Achievement Unlocked!")
        print(f"{achievement['icon']} {achievement['name']}")
        print(f"+{achievement['points']} points!")
```

### Example 2: Display Friends List

```python
def show_friends_screen(user_id):
    # Get friends
    friends = user_manager.get_friends_list(user_id)
    
    # Display
    print("👥 Your Friends:")
    for friend in friends:
        print(f"  {friend['username']}")
        print(f"    Win Rate: {friend['win_rate']}%")
        print(f"    Games: {friend['total_games']}")
```

### Example 3: Send Friend Request

```python
def add_friend_by_email(user_id):
    friend_email = input("Enter friend's email: ")
    result = user_manager.add_friend(user_id, friend_email)
    
    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['message']}")
```

### Example 4: Accept Friend Requests

```python
def show_pending_requests(user_id):
    requests = user_manager.get_friend_requests(user_id)
    
    if not requests:
        print("No pending friend requests")
        return
    
    print(f"You have {len(requests)} pending request(s):")
    for i, req in enumerate(requests, 1):
        print(f"{i}. {req['username']} ({req['email']})")
    
    choice = int(input("Accept which request? "))
    friend_id = requests[choice-1]['user_id']
    
    user_manager.accept_friend(user_id, friend_id)
    print("✅ Friend request accepted!")
```

---

## 🗄️ Database Schema

### New Tables

#### friends
```sql
CREATE TABLE friends (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    friend_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    requested_at TEXT NOT NULL,
    accepted_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (friend_id) REFERENCES users (user_id),
    UNIQUE(user_id, friend_id)
);
```

#### achievements
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    achievement_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    requirement_type TEXT NOT NULL,
    requirement_value INTEGER NOT NULL,
    points INTEGER DEFAULT 10
);
```

#### user_achievements
```sql
CREATE TABLE user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    achievement_id TEXT NOT NULL,
    unlocked_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id),
    UNIQUE(user_id, achievement_id)
);
```

---

## 🎯 Achievement Requirements Detail

### wins
Tracks total wins across all game modes.

### games
Tracks total games played (any result).

### streak
Tracks consecutive wins. Resets on loss.

### perfect
Win with 64-0 score (all discs captured).

### high_score
Single game score of 60 or higher.

### ai_hard
Beat AI on Hard difficulty.

### vs_friend
Games played against friends (local multiplayer).

### speed
Win a game in 120 seconds or less.

### comeback
*Not yet implemented* - Win after being behind by 20 points.

---

## 🔧 Customization

### Add New Achievements

Edit `auth_server.py`, in `init_db()` function:

```python
default_achievements = [
    # Existing achievements...
    
    # Add your custom achievement
    ('custom_id', 'Custom Name', 'Description', '🌟', 'requirement_type', value, points),
]
```

Requirement types:
- `wins` - Total wins
- `games` - Total games
- `streak` - Win streak
- `perfect` - Perfect game
- `high_score` - Score threshold
- `ai_hard` - Beat Hard AI
- `vs_friend` - vs Friend games
- `speed` - Time threshold
- Custom (requires code modification)

### Modify Friend Request Behavior

In `auth_server.py`, `add_friend()` function:

```python
# Auto-accept friends (no request needed)
status = 'accepted'

# Or keep pending approval
status = 'pending'
```

---

## 📊 Statistics Tracked

### Per User
- Total games played
- Wins/Losses/Draws
- Win rate percentage
- Total score accumulated
- Highest single game score
- Games by mode (AI/Friend/Online)
- Achievement points
- Friend count

### Global
- Total registered users
- Total games played
- Average score per game
- Leaderboard rankings

---

## 🆘 Troubleshooting

### Achievements not unlocking

**Problem:** Played games but achievements don't appear

**Solution:**
```python
# Manually trigger achievement check
result = user_manager.check_achievements(user_id)
print(result)
```

### Friend request errors

**Problem:** "User not found"

**Solution:** Make sure friend is registered with exact email

**Problem:** "Already friends"

**Solution:** Check existing friends list first

### Database issues

**Problem:** SQLite errors

**Solution:**
```powershell
# Backup old database
move othello_users.db othello_users_backup.db

# Restart server (creates new database)
python auth_server.py
```

---

## 💡 Best Practices

### 1. Check Achievements After Every Game
```python
# In your game loop
if game_ended:
    user_manager.add_game_to_history(user_id, game_data)
    achievements = user_manager.check_achievements(user_id)
    show_achievement_notifications(achievements)
```

### 2. Cache Friends List
```python
# Don't fetch every frame
friends_cache = user_manager.get_friends_list(user_id)
# Use cache for display
```

### 3. Handle Server Offline Gracefully
```python
if not user_manager.is_online:
    print("⚠️ Playing offline - features limited")
    # Use local storage fallback
```

### 4. Validate Before API Calls
```python
# Check data before sending
if '@' not in friend_email:
    print("Invalid email format")
    return
```

---

## 🎮 Game UI Integration Ideas

### 1. Achievement Popup
Show achievement unlocks as overlay notifications during gameplay.

### 2. Friends Screen
Add a dedicated menu option to:
- View friends
- Send requests
- Accept pending requests
- See friend stats

### 3. Profile Page
Display on user profile:
- Achievement badges
- Total points
- Progress bars for locked achievements
- Friend count

### 4. Social Tab
Add tab showing:
- Leaderboard
- Friend activity
- Recent achievements
- Suggested friends

---

## 📈 Future Enhancement Ideas

1. **Chat System** - Real-time messaging between friends
2. **Challenges** - Send game challenges to friends
3. **Tournaments** - Organize multiplayer tournaments
4. **Clans/Teams** - Create player groups
5. **Daily Quests** - Time-limited challenges
6. **Seasonal Events** - Special achievements during events
7. **Gift System** - Send rewards to friends
8. **Match History** - Detailed game replays
9. **Statistics Dashboard** - Advanced analytics
10. **Achievements Progress** - Show progress bars

---

## 📝 Summary

✅ **Friend System Complete**
- Send/Accept/Remove friends
- View friend stats
- Friend requests management

✅ **Achievement System Complete**
- 12 unique achievements
- Point-based progression
- Automatic detection
- Persistent storage

✅ **Enhanced Statistics**
- Per-user tracking
- Global leaderboards
- Win streaks
- Detailed analytics

✅ **Fully Tested**
- Test script included
- All endpoints working
- Database optimized

Ready to integrate into your game! 🎉

---

## 🔗 Related Files

- `auth_server.py` - Enhanced server with social features
- `server_user_manager.py` - Client with friend/achievement methods
- `test_social_features.py` - Comprehensive test suite
- `EXTERNAL_SERVER_README.md` - General server documentation
- `SERVER_SETUP.md` - Deployment guide

---

**Have fun gaming with friends and collecting achievements! 🎮🏆👥**
