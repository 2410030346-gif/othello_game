"""
Server-based User Manager for Othello Game
Connects to external Flask API server for user authentication
"""

import requests
import json
from datetime import datetime

class ServerUserManager:
    def __init__(self, server_url="http://localhost:5000"):
        self.server_url = server_url
        self.current_user = None
        self.is_online = self.check_server_status()
    
    def check_server_status(self):
        """Check if server is online"""
        try:
            response = requests.get(f"{self.server_url}/api/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def login_user(self, email, username, provider):
        """
        Login or register a user via API
        Returns user data dict or None if failed
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/login",
                json={
                    'email': email,
                    'username': username,
                    'provider': provider
                },
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                self.current_user = user_data
                return user_data
            else:
                print(f"Login failed: {response.json().get('error', 'Unknown error')}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Server may be offline.")
            return None
        except Exception as e:
            print(f"Login error: {e}")
            return None
    
    def get_current_user(self):
        """Get the currently logged in user data"""
        return self.current_user
    
    def logout_user(self):
        """Logout current user"""
        self.current_user = None
    
    def get_user_data(self, user_id):
        """Get complete user profile and statistics"""
        try:
            response = requests.get(
                f"{self.server_url}/api/user/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user data: {response.json().get('error')}")
                return None
                
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None
    
    def add_game_to_history(self, game_data=None, user_id=None):
        """
        Save game to server
        If game_data is a dict and user_id is None, uses current_user
        If game_data is an int, it's treated as user_id (old signature)
        game_data should include: game_mode, result, player_score, opponent_score, difficulty, duration
        """
        # Handle old signature: add_game_to_history(user_id, game_data)
        if isinstance(game_data, int) or (isinstance(game_data, str) and game_data.isdigit()):
            user_id = game_data
            game_data = user_id  # This will be handled by the next line
        
        # If user_id is a dict, swap (old style call)
        if isinstance(user_id, dict):
            game_data, user_id = user_id, game_data
        
        # Use current user if no user_id provided
        if user_id is None:
            if self.current_user:
                user_id = self.current_user['user_id']
            else:
                print("No user logged in")
                return False
        
        try:
            data = {
                'user_id': user_id,
                'game_mode': game_data.get('game_mode', 'vs_ai'),
                'result': game_data.get('result', 'loss'),
                'player_score': game_data.get('player_score', 0),
                'opponent_score': game_data.get('opponent_score', 0),
                'difficulty': game_data.get('difficulty', 'N/A'),
                'duration': game_data.get('duration', 0)
            }
            
            response = requests.post(
                f"{self.server_url}/api/game/save",
                json=data,
                timeout=5
            )
            
            if response.status_code == 201:
                return True
            else:
                print(f"Failed to save game: {response.json().get('error')}")
                return False
                
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def get_user_stats(self, user_id):
        """Get user statistics (simplified version)"""
        user_data = self.get_user_data(user_id)
        if user_data:
            return user_data.get('stats', {})
        return {}
    
    def get_leaderboard(self, limit=10):
        """Get top players leaderboard"""
        try:
            response = requests.get(
                f"{self.server_url}/api/leaderboard",
                params={'limit': limit},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
                
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []
    
    def get_global_stats(self):
        """Get global game statistics"""
        try:
            response = requests.get(
                f"{self.server_url}/api/stats",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {}
                
        except Exception as e:
            print(f"Error getting global stats: {e}")
            return {}
    
    # ==================== FRIEND SYSTEM METHODS ====================
    
    def add_friend(self, user_id, friend_email):
        """Send friend request to user by email"""
        try:
            response = requests.post(
                f"{self.server_url}/api/friends/add",
                json={'user_id': user_id, 'friend_email': friend_email},
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {'error': response.json().get('error', 'Failed to send friend request')}
                
        except Exception as e:
            return {'error': str(e)}
    
    def accept_friend(self, user_id, friend_id):
        """Accept friend request"""
        try:
            response = requests.post(
                f"{self.server_url}/api/friends/accept",
                json={'user_id': user_id, 'friend_id': friend_id},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.json().get('error', 'Failed to accept friend request')}
                
        except Exception as e:
            return {'error': str(e)}
    
    def get_friends_list(self, user_id):
        """Get list of accepted friends"""
        try:
            response = requests.get(
                f"{self.server_url}/api/friends/list/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
                
        except Exception as e:
            print(f"Error getting friends list: {e}")
            return []
    
    def get_friend_requests(self, user_id):
        """Get pending friend requests"""
        try:
            response = requests.get(
                f"{self.server_url}/api/friends/requests/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
                
        except Exception as e:
            print(f"Error getting friend requests: {e}")
            return []
    
    def remove_friend(self, user_id, friend_id):
        """Remove a friend"""
        try:
            response = requests.post(
                f"{self.server_url}/api/friends/remove",
                json={'user_id': user_id, 'friend_id': friend_id},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': response.json().get('error', 'Failed to remove friend')}
                
        except Exception as e:
            return {'error': str(e)}
    
    # ==================== ACHIEVEMENT SYSTEM METHODS ====================
    
    def get_all_achievements(self):
        """Get list of all available achievements"""
        try:
            response = requests.get(
                f"{self.server_url}/api/achievements",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return []
                
        except Exception as e:
            print(f"Error getting achievements: {e}")
            return []
    
    def get_user_achievements(self, user_id):
        """Get user's unlocked achievements"""
        try:
            response = requests.get(
                f"{self.server_url}/api/achievements/{user_id}",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'unlocked_achievements': [], 'total_achievements': 0, 'total_points': 0}
                
        except Exception as e:
            print(f"Error getting user achievements: {e}")
            return {'unlocked_achievements': [], 'total_achievements': 0, 'total_points': 0}
    
    def check_achievements(self, user_id):
        """Check and unlock new achievements for user"""
        try:
            response = requests.post(
                f"{self.server_url}/api/achievements/check",
                json={'user_id': user_id},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            return {'newly_unlocked': [], 'message': 'Failed to check achievements'}
                
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return {'newly_unlocked': [], 'message': str(e)}
