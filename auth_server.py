"""
Flask Backend Server for Othello Game Authentication
Handles user authentication and game history via REST API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import sqlite3
import hashlib
import json

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin requests

# Database configuration
DATABASE = 'othello_users.db'

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            username TEXT NOT NULL,
            provider TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_login TEXT NOT NULL,
            login_count INTEGER DEFAULT 1
        )
    ''')
    
    # Game history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            game_mode TEXT NOT NULL,
            result TEXT NOT NULL,
            player_score INTEGER NOT NULL,
            opponent_score INTEGER NOT NULL,
            difficulty TEXT,
            duration INTEGER,
            timestamp TEXT NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    # Friends table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            friend_id TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            requested_at TEXT NOT NULL,
            accepted_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (friend_id) REFERENCES users (user_id),
            UNIQUE(user_id, friend_id)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            achievement_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            icon TEXT NOT NULL,
            requirement_type TEXT NOT NULL,
            requirement_value INTEGER NOT NULL,
            points INTEGER DEFAULT 10
        )
    ''')
    
    # User achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            achievement_id TEXT NOT NULL,
            unlocked_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (achievement_id),
            UNIQUE(user_id, achievement_id)
        )
    ''')
    
    # Initialize default achievements
    default_achievements = [
        ('first_win', 'First Victory', 'Win your first game', '🏆', 'wins', 1, 10),
        ('winning_streak', 'Winning Streak', 'Win 3 games in a row', '🔥', 'streak', 3, 25),
        ('game_master', 'Game Master', 'Win 10 games', '👑', 'wins', 10, 50),
        ('perfect_game', 'Perfect Game', 'Win with 64-0 score', '💎', 'perfect', 1, 100),
        ('beginner', 'Beginner', 'Play 5 games', '🎮', 'games', 5, 10),
        ('experienced', 'Experienced', 'Play 25 games', '🎯', 'games', 25, 30),
        ('veteran', 'Veteran', 'Play 100 games', '⭐', 'games', 100, 75),
        ('ai_challenger', 'AI Challenger', 'Beat Hard AI', '🤖', 'ai_hard', 1, 50),
        ('social_player', 'Social Player', 'Play 10 games with friends', '👥', 'vs_friend', 10, 30),
        ('high_scorer', 'High Scorer', 'Score 60+ in a single game', '💯', 'high_score', 60, 40),
        ('comeback_king', 'Comeback King', 'Win after being behind by 20', '🎪', 'comeback', 1, 75),
        ('speed_demon', 'Speed Demon', 'Win a game in under 2 minutes', '⚡', 'speed', 120, 50),
    ]
    
    for ach in default_achievements:
        cursor.execute('''
            INSERT OR IGNORE INTO achievements 
            (achievement_id, name, description, icon, requirement_type, requirement_value, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ach)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")
    print("✅ Friend system enabled!")
    print("✅ Achievement system enabled!")

def generate_user_id(email, provider):
    """Generate unique user ID"""
    unique_string = f"{email}_{provider}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:12]

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if server is running"""
    return jsonify({
        'status': 'online',
        'message': 'Othello Game Server is running',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/api/login', methods=['POST'])
def login_user():
    """
    Login or register a user
    Expected JSON: {
        "email": "user@example.com",
        "username": "username",
        "provider": "google/facebook/google_play"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        provider = data.get('provider')
        
        if not email or not username or not provider:
            return jsonify({'error': 'Missing required fields'}), 400
        
        user_id = generate_user_id(email, provider)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if user:
            # Update existing user
            cursor.execute('''
                UPDATE users 
                SET last_login = ?, login_count = login_count + 1
                WHERE user_id = ?
            ''', (current_time, user_id))
            conn.commit()
            
            response = {
                'user_id': user_id,
                'email': email,
                'username': username,
                'provider': provider,
                'login_count': user['login_count'] + 1,
                'message': 'Welcome back!'
            }
        else:
            # Create new user
            cursor.execute('''
                INSERT INTO users (user_id, email, username, provider, created_at, last_login, login_count)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (user_id, email, username, provider, current_time, current_time))
            conn.commit()
            
            response = {
                'user_id': user_id,
                'email': email,
                'username': username,
                'provider': provider,
                'login_count': 1,
                'message': 'Account created successfully!'
            }
        
        conn.close()
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """Get user profile and statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user info
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get game history (last 100 games)
        cursor.execute('''
            SELECT * FROM game_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''', (user_id,))
        games = cursor.fetchall()
        
        # Calculate statistics
        total_games = len(games)
        wins = sum(1 for g in games if g['result'] == 'win')
        losses = sum(1 for g in games if g['result'] == 'loss')
        draws = sum(1 for g in games if g['result'] == 'draw')
        total_score = sum(g['player_score'] for g in games)
        highest_score = max([g['player_score'] for g in games]) if games else 0
        win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
        
        vs_ai = sum(1 for g in games if g['game_mode'] == 'vs_ai')
        vs_player = sum(1 for g in games if g['game_mode'] == 'vs_friend')
        online = sum(1 for g in games if g['game_mode'] == 'online')
        
        response = {
            'user_id': user['user_id'],
            'email': user['email'],
            'username': user['username'],
            'provider': user['provider'],
            'created_at': user['created_at'],
            'last_login': user['last_login'],
            'login_count': user['login_count'],
            'stats': {
                'total_games': total_games,
                'wins': wins,
                'losses': losses,
                'draws': draws,
                'win_rate': round(win_rate, 2),
                'total_score': total_score,
                'highest_score': highest_score,
                'vs_ai_games': vs_ai,
                'vs_player_games': vs_player,
                'online_games': online
            },
            'game_history': [dict(g) for g in games]
        }
        
        conn.close()
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/game/save', methods=['POST'])
def save_game():
    """
    Save game history
    Expected JSON: {
        "user_id": "abc123",
        "game_mode": "vs_ai",
        "result": "win/loss/draw",
        "player_score": 35,
        "opponent_score": 29,
        "difficulty": "Medium",
        "duration": 120
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify user exists
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'User not found'}), 404
        
        # Insert game record
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO game_history 
            (user_id, game_mode, result, player_score, opponent_score, difficulty, duration, timestamp, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('game_mode', 'vs_ai'),
            data.get('result', 'loss'),
            data.get('player_score', 0),
            data.get('opponent_score', 0),
            data.get('difficulty', 'N/A'),
            data.get('duration', 0),
            current_time,
            current_date
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Game saved successfully!',
            'timestamp': current_time
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get top players by win rate"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get all users with their stats
        cursor.execute('SELECT user_id, username, email FROM users')
        users = cursor.fetchall()
        
        leaderboard = []
        for user in users:
            cursor.execute('''
                SELECT result, player_score FROM game_history 
                WHERE user_id = ?
            ''', (user['user_id'],))
            games = cursor.fetchall()
            
            total_games = len(games)
            if total_games >= 5:  # Minimum 5 games to appear on leaderboard
                wins = sum(1 for g in games if g['result'] == 'win')
                win_rate = (wins / total_games * 100)
                total_score = sum(g['player_score'] for g in games)
                
                leaderboard.append({
                    'username': user['username'],
                    'email': user['email'],
                    'total_games': total_games,
                    'wins': wins,
                    'win_rate': round(win_rate, 2),
                    'total_score': total_score
                })
        
        # Sort by win rate, then by total games
        leaderboard.sort(key=lambda x: (x['win_rate'], x['total_games']), reverse=True)
        
        conn.close()
        return jsonify(leaderboard[:limit]), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_global_stats():
    """Get global game statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as total_users FROM users')
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute('SELECT COUNT(*) as total_games FROM game_history')
        total_games = cursor.fetchone()['total_games']
        
        cursor.execute('SELECT AVG(player_score) as avg_score FROM game_history')
        avg_score = cursor.fetchone()['avg_score'] or 0
        
        conn.close()
        
        return jsonify({
            'total_users': total_users,
            'total_games': total_games,
            'average_score': round(avg_score, 2)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FRIEND SYSTEM ENDPOINTS ====================

@app.route('/api/friends/add', methods=['POST'])
def add_friend():
    """
    Send friend request
    Expected JSON: {
        "user_id": "abc123",
        "friend_email": "friend@gmail.com"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        friend_email = data.get('friend_email')
        
        if not user_id or not friend_email:
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find friend by email
        cursor.execute('SELECT user_id, username FROM users WHERE email = ?', (friend_email,))
        friend = cursor.fetchone()
        
        if not friend:
            return jsonify({'error': 'User not found with that email'}), 404
        
        friend_id = friend['user_id']
        
        if user_id == friend_id:
            return jsonify({'error': 'Cannot add yourself as friend'}), 400
        
        # Check if already friends or request exists
        cursor.execute('''
            SELECT * FROM friends 
            WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)
        ''', (user_id, friend_id, friend_id, user_id))
        
        existing = cursor.fetchone()
        if existing:
            if existing['status'] == 'accepted':
                return jsonify({'message': 'Already friends'}), 200
            else:
                return jsonify({'message': 'Friend request already pending'}), 200
        
        # Create friend request
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO friends (user_id, friend_id, status, requested_at)
            VALUES (?, ?, 'pending', ?)
        ''', (user_id, friend_id, current_time))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': f'Friend request sent to {friend["username"]}',
            'friend_username': friend['username']
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/friends/accept', methods=['POST'])
def accept_friend():
    """
    Accept friend request
    Expected JSON: {
        "user_id": "abc123",
        "friend_id": "def456"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        friend_id = data.get('friend_id')
        
        if not user_id or not friend_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find pending request
        cursor.execute('''
            SELECT * FROM friends 
            WHERE user_id = ? AND friend_id = ? AND status = 'pending'
        ''', (friend_id, user_id))
        
        request_record = cursor.fetchone()
        if not request_record:
            return jsonify({'error': 'No pending friend request found'}), 404
        
        # Accept the request
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            UPDATE friends 
            SET status = 'accepted', accepted_at = ?
            WHERE user_id = ? AND friend_id = ?
        ''', (current_time, friend_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Friend request accepted!'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/friends/list/<user_id>', methods=['GET'])
def get_friends_list(user_id):
    """Get list of friends for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get accepted friends
        cursor.execute('''
            SELECT u.user_id, u.username, u.email, f.accepted_at
            FROM friends f
            JOIN users u ON (f.friend_id = u.user_id OR f.user_id = u.user_id)
            WHERE (f.user_id = ? OR f.friend_id = ?) 
            AND f.status = 'accepted'
            AND u.user_id != ?
        ''', (user_id, user_id, user_id))
        
        friends = cursor.fetchall()
        
        friends_list = []
        for friend in friends:
            # Get friend's stats
            cursor.execute('''
                SELECT COUNT(*) as total_games,
                       SUM(CASE WHEN result = 'win' THEN 1 ELSE 0 END) as wins
                FROM game_history WHERE user_id = ?
            ''', (friend['user_id'],))
            stats = cursor.fetchone()
            
            total_games = stats['total_games'] or 0
            wins = stats['wins'] or 0
            win_rate = (wins / total_games * 100) if total_games > 0 else 0.0
            
            friends_list.append({
                'user_id': friend['user_id'],
                'username': friend['username'],
                'email': friend['email'],
                'friends_since': friend['accepted_at'],
                'total_games': total_games,
                'wins': wins,
                'win_rate': round(win_rate, 2)
            })
        
        conn.close()
        return jsonify(friends_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/friends/requests/<user_id>', methods=['GET'])
def get_friend_requests(user_id):
    """Get pending friend requests for a user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get pending requests where user is the recipient
        cursor.execute('''
            SELECT u.user_id, u.username, u.email, f.requested_at
            FROM friends f
            JOIN users u ON f.user_id = u.user_id
            WHERE f.friend_id = ? AND f.status = 'pending'
        ''', (user_id,))
        
        requests = cursor.fetchall()
        
        requests_list = [{
            'user_id': req['user_id'],
            'username': req['username'],
            'email': req['email'],
            'requested_at': req['requested_at']
        } for req in requests]
        
        conn.close()
        return jsonify(requests_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/friends/remove', methods=['POST'])
def remove_friend():
    """
    Remove friend
    Expected JSON: {
        "user_id": "abc123",
        "friend_id": "def456"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        friend_id = data.get('friend_id')
        
        if not user_id or not friend_id:
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remove friendship (both directions)
        cursor.execute('''
            DELETE FROM friends 
            WHERE (user_id = ? AND friend_id = ?) OR (user_id = ? AND friend_id = ?)
        ''', (user_id, friend_id, friend_id, user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Friend removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ACHIEVEMENT SYSTEM ENDPOINTS ====================

@app.route('/api/achievements', methods=['GET'])
def get_all_achievements():
    """Get list of all available achievements"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM achievements ORDER BY points DESC')
        achievements = cursor.fetchall()
        
        achievements_list = [{
            'achievement_id': ach['achievement_id'],
            'name': ach['name'],
            'description': ach['description'],
            'icon': ach['icon'],
            'requirement_type': ach['requirement_type'],
            'requirement_value': ach['requirement_value'],
            'points': ach['points']
        } for ach in achievements]
        
        conn.close()
        return jsonify(achievements_list), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/achievements/<user_id>', methods=['GET'])
def get_user_achievements(user_id):
    """Get user's unlocked achievements"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get unlocked achievements
        cursor.execute('''
            SELECT a.*, ua.unlocked_at
            FROM user_achievements ua
            JOIN achievements a ON ua.achievement_id = a.achievement_id
            WHERE ua.user_id = ?
            ORDER BY ua.unlocked_at DESC
        ''', (user_id,))
        
        unlocked = cursor.fetchall()
        
        unlocked_list = [{
            'achievement_id': ach['achievement_id'],
            'name': ach['name'],
            'description': ach['description'],
            'icon': ach['icon'],
            'points': ach['points'],
            'unlocked_at': ach['unlocked_at']
        } for ach in unlocked]
        
        # Calculate total points
        total_points = sum(ach['points'] for ach in unlocked)
        
        conn.close()
        return jsonify({
            'unlocked_achievements': unlocked_list,
            'total_achievements': len(unlocked_list),
            'total_points': total_points
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/achievements/check', methods=['POST'])
def check_achievements():
    """
    Check and unlock achievements for a user based on their stats
    Expected JSON: {
        "user_id": "abc123"
    }
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's game history
        cursor.execute('''
            SELECT * FROM game_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
        ''', (user_id,))
        games = cursor.fetchall()
        
        if not games:
            return jsonify({'newly_unlocked': [], 'message': 'No games played yet'}), 200
        
        # Calculate stats
        total_games = len(games)
        wins = sum(1 for g in games if g['result'] == 'win')
        vs_friend_games = sum(1 for g in games if g['game_mode'] == 'vs_friend')
        
        # Check for win streak
        current_streak = 0
        max_streak = 0
        for game in games:
            if game['result'] == 'win':
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        # Check for perfect game
        has_perfect = any(g['player_score'] == 64 and g['opponent_score'] == 0 for g in games)
        
        # Check for high score
        max_score = max(g['player_score'] for g in games)
        
        # Check for hard AI win
        has_hard_ai_win = any(g['result'] == 'win' and g['difficulty'] == 'Hard' for g in games)
        
        # Check for speed win
        has_speed_win = any(g['result'] == 'win' and g['duration'] <= 120 for g in games)
        
        # Get all achievements
        cursor.execute('SELECT * FROM achievements')
        all_achievements = cursor.fetchall()
        
        # Get already unlocked achievements
        cursor.execute('SELECT achievement_id FROM user_achievements WHERE user_id = ?', (user_id,))
        unlocked = {row['achievement_id'] for row in cursor.fetchall()}
        
        newly_unlocked = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        for ach in all_achievements:
            ach_id = ach['achievement_id']
            
            if ach_id in unlocked:
                continue  # Already unlocked
            
            should_unlock = False
            
            if ach['requirement_type'] == 'wins' and wins >= ach['requirement_value']:
                should_unlock = True
            elif ach['requirement_type'] == 'games' and total_games >= ach['requirement_value']:
                should_unlock = True
            elif ach['requirement_type'] == 'streak' and max_streak >= ach['requirement_value']:
                should_unlock = True
            elif ach['requirement_type'] == 'perfect' and has_perfect:
                should_unlock = True
            elif ach['requirement_type'] == 'high_score' and max_score >= ach['requirement_value']:
                should_unlock = True
            elif ach['requirement_type'] == 'ai_hard' and has_hard_ai_win:
                should_unlock = True
            elif ach['requirement_type'] == 'vs_friend' and vs_friend_games >= ach['requirement_value']:
                should_unlock = True
            elif ach['requirement_type'] == 'speed' and has_speed_win:
                should_unlock = True
            
            if should_unlock:
                cursor.execute('''
                    INSERT INTO user_achievements (user_id, achievement_id, unlocked_at)
                    VALUES (?, ?, ?)
                ''', (user_id, ach_id, current_time))
                
                newly_unlocked.append({
                    'achievement_id': ach_id,
                    'name': ach['name'],
                    'description': ach['description'],
                    'icon': ach['icon'],
                    'points': ach['points']
                })
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'newly_unlocked': newly_unlocked,
            'message': f'{len(newly_unlocked)} new achievements unlocked!' if newly_unlocked else 'No new achievements'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("\n" + "="*60)
    print("🎮 OTHELLO GAME SERVER WITH SOCIAL FEATURES")
    print("="*60)
    print("✅ Server starting on http://localhost:5000")
    print("\n📡 API Endpoints:")
    print("\n🔐 Authentication:")
    print("   GET  /api/health - Health check")
    print("   POST /api/login - Login/Register user")
    print("   GET  /api/user/<user_id> - Get user profile")
    print("\n🎮 Game Management:")
    print("   POST /api/game/save - Save game history")
    print("   GET  /api/leaderboard - Get top players")
    print("   GET  /api/stats - Global statistics")
    print("\n👥 Friend System:")
    print("   POST /api/friends/add - Send friend request")
    print("   POST /api/friends/accept - Accept friend request")
    print("   GET  /api/friends/list/<user_id> - Get friends list")
    print("   GET  /api/friends/requests/<user_id> - Get pending requests")
    print("   POST /api/friends/remove - Remove friend")
    print("\n🏆 Achievement System:")
    print("   GET  /api/achievements - Get all achievements")
    print("   GET  /api/achievements/<user_id> - Get user achievements")
    print("   POST /api/achievements/check - Check/unlock achievements")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
