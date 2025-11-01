"""
User Management System for Othello Game
Handles user authentication and game history tracking
"""

import json
import os
from datetime import datetime
import hashlib

class UserManager:
    def __init__(self, data_file="user_data.json"):
        self.data_file = data_file
        self.current_user = None
        self.users = self.load_users()
    
    def load_users(self):
        """Load users from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_users(self):
        """Save users to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.users, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving users: {e}")
            return False
    
    def generate_user_id(self, email, provider):
        """Generate unique user ID based on email and provider"""
        unique_string = f"{email}_{provider}"
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def login_user(self, email, username, provider):
        """
        Login or register a user
        provider: 'google', 'facebook', or 'google_play'
        """
        user_id = self.generate_user_id(email, provider)
        
        # Check if user exists
        if user_id in self.users:
            # User exists, just login
            self.current_user = user_id
            self.users[user_id]['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.users[user_id]['login_count'] = self.users[user_id].get('login_count', 0) + 1
        else:
            # New user, create profile
            self.users[user_id] = {
                'user_id': user_id,
                'email': email,
                'username': username,
                'provider': provider,
                'created_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'last_login': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'login_count': 1,
                'game_history': [],
                'stats': {
                    'total_games': 0,
                    'wins': 0,
                    'losses': 0,
                    'draws': 0,
                    'win_rate': 0.0,
                    'total_score': 0,
                    'highest_score': 0,
                    'vs_ai_games': 0,
                    'vs_player_games': 0,
                    'online_games': 0
                }
            }
            self.current_user = user_id
        
        self.save_users()
        return self.users[user_id]
    
    def logout_user(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self):
        """Get current logged in user data"""
        if self.current_user and self.current_user in self.users:
            return self.users[self.current_user]
        return None
    
    def add_game_to_history(self, game_data):
        """
        Add a completed game to user's history
        game_data should contain:
        - game_mode: 'vs_ai', 'vs_friend', 'online'
        - result: 'win', 'loss', 'draw'
        - player_score: int
        - opponent_score: int
        - difficulty: str (for AI games)
        - duration: int (seconds)
        """
        if not self.current_user:
            return False
        
        user = self.users[self.current_user]
        
        # Add timestamp
        game_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        game_data['date'] = datetime.now().strftime("%Y-%m-%d")
        
        # Add to history
        user['game_history'].append(game_data)
        
        # Update stats
        stats = user['stats']
        stats['total_games'] += 1
        
        if game_data['result'] == 'win':
            stats['wins'] += 1
        elif game_data['result'] == 'loss':
            stats['losses'] += 1
        elif game_data['result'] == 'draw':
            stats['draws'] += 1
        
        # Update win rate
        if stats['total_games'] > 0:
            stats['win_rate'] = round((stats['wins'] / stats['total_games']) * 100, 2)
        
        # Update scores
        stats['total_score'] += game_data['player_score']
        if game_data['player_score'] > stats['highest_score']:
            stats['highest_score'] = game_data['player_score']
        
        # Update game type counters
        if game_data['game_mode'] == 'vs_ai':
            stats['vs_ai_games'] += 1
        elif game_data['game_mode'] == 'vs_friend':
            stats['vs_player_games'] += 1
        elif game_data['game_mode'] == 'online':
            stats['online_games'] += 1
        
        # Keep only last 100 games in history to avoid file bloat
        if len(user['game_history']) > 100:
            user['game_history'] = user['game_history'][-100:]
        
        self.save_users()
        return True
    
    def get_user_stats(self):
        """Get current user's statistics"""
        if self.current_user and self.current_user in self.users:
            return self.users[self.current_user]['stats']
        return None
    
    def get_recent_games(self, limit=10):
        """Get recent games from history"""
        if self.current_user and self.current_user in self.users:
            history = self.users[self.current_user]['game_history']
            return history[-limit:] if history else []
        return []
    
    def get_all_users_stats(self):
        """Get leaderboard data - all users stats"""
        leaderboard = []
        for user_id, user_data in self.users.items():
            leaderboard.append({
                'username': user_data['username'],
                'wins': user_data['stats']['wins'],
                'total_games': user_data['stats']['total_games'],
                'win_rate': user_data['stats']['win_rate'],
                'highest_score': user_data['stats']['highest_score']
            })
        
        # Sort by wins
        leaderboard.sort(key=lambda x: (x['wins'], x['win_rate']), reverse=True)
        return leaderboard
