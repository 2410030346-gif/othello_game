"""
Test script to demonstrate the authentication server API
Run this after starting auth_server.py
"""

import requests
import time

SERVER_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_health():
    """Test server health check"""
    print_section("1. Testing Health Check")
    try:
        response = requests.get(f"{SERVER_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is ONLINE!")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            return True
        else:
            print("❌ Server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure to run: python auth_server.py")
        return False

def test_login():
    """Test user login/registration"""
    print_section("2. Testing User Login")
    
    users = [
        {"email": "john123@gmail.com", "username": "john", "provider": "google"},
        {"email": "sarah@gmail.com", "username": "sarah", "provider": "google"},
        {"email": "mike@example.com", "username": "mike", "provider": "facebook"}
    ]
    
    user_ids = []
    for user in users:
        response = requests.post(f"{SERVER_URL}/api/login", json=user)
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Logged in: {user['username']}")
            print(f"   User ID: {data['user_id']}")
            print(f"   Message: {data['message']}")
            user_ids.append(data['user_id'])
        else:
            print(f"❌ Failed to login {user['username']}")
    
    return user_ids

def test_save_games(user_ids):
    """Test saving game history"""
    print_section("3. Testing Game History Save")
    
    games = [
        {"user_id": user_ids[0], "game_mode": "vs_ai", "result": "win", "player_score": 35, "opponent_score": 29, "difficulty": "Easy", "duration": 120},
        {"user_id": user_ids[0], "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Medium", "duration": 180},
        {"user_id": user_ids[0], "game_mode": "vs_friend", "result": "loss", "player_score": 28, "opponent_score": 36, "difficulty": "N/A", "duration": 200},
        {"user_id": user_ids[1], "game_mode": "vs_ai", "result": "win", "player_score": 38, "opponent_score": 26, "difficulty": "Hard", "duration": 300},
        {"user_id": user_ids[1], "game_mode": "vs_ai", "result": "win", "player_score": 42, "opponent_score": 22, "difficulty": "Hard", "duration": 250},
        {"user_id": user_ids[1], "game_mode": "vs_ai", "result": "win", "player_score": 45, "opponent_score": 19, "difficulty": "Hard", "duration": 280},
        {"user_id": user_ids[1], "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Medium", "duration": 220},
        {"user_id": user_ids[1], "game_mode": "vs_ai", "result": "win", "player_score": 39, "opponent_score": 25, "difficulty": "Medium", "duration": 210},
        {"user_id": user_ids[2], "game_mode": "vs_friend", "result": "win", "player_score": 33, "opponent_score": 31, "difficulty": "N/A", "duration": 150},
    ]
    
    success_count = 0
    for game in games:
        response = requests.post(f"{SERVER_URL}/api/game/save", json=game)
        if response.status_code == 201:
            success_count += 1
    
    print(f"\n✅ Saved {success_count}/{len(games)} games successfully!")

def test_get_profile(user_ids):
    """Test getting user profile"""
    print_section("4. Testing User Profile Retrieval")
    
    for user_id in user_ids[:2]:  # Check first 2 users
        response = requests.get(f"{SERVER_URL}/api/user/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n👤 {data['username']} ({data['email']})")
            print(f"   Provider: {data['provider']}")
            print(f"   Login Count: {data['login_count']}")
            print(f"   Stats:")
            stats = data['stats']
            print(f"      Total Games: {stats['total_games']}")
            print(f"      Wins: {stats['wins']} | Losses: {stats['losses']} | Draws: {stats['draws']}")
            print(f"      Win Rate: {stats['win_rate']}%")
            print(f"      Highest Score: {stats['highest_score']}")

def test_leaderboard():
    """Test leaderboard"""
    print_section("5. Testing Leaderboard")
    
    response = requests.get(f"{SERVER_URL}/api/leaderboard?limit=5")
    if response.status_code == 200:
        leaderboard = response.json()
        if leaderboard:
            print("\n🏆 TOP PLAYERS (Minimum 5 games)")
            print(f"{'Rank':<6} {'Username':<15} {'Games':<8} {'Wins':<8} {'Win Rate':<10}")
            print("-" * 55)
            for i, player in enumerate(leaderboard, 1):
                print(f"{i:<6} {player['username']:<15} {player['total_games']:<8} {player['wins']:<8} {player['win_rate']:.1f}%")
        else:
            print("\n⚠️  No players qualify for leaderboard yet (need 5+ games)")

def test_global_stats():
    """Test global statistics"""
    print_section("6. Testing Global Statistics")
    
    response = requests.get(f"{SERVER_URL}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"\n📊 GLOBAL STATISTICS")
        print(f"   Total Users: {stats['total_users']}")
        print(f"   Total Games: {stats['total_games']}")
        print(f"   Average Score: {stats['average_score']:.2f}")

def main():
    print("\n" + "🎮 OTHELLO AUTHENTICATION SERVER TEST SUITE " + "\n")
    print("Make sure auth_server.py is running first!")
    print("Start it with: python auth_server.py\n")
    
    time.sleep(1)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Exiting...")
        return
    
    # Test 2: User login
    user_ids = test_login()
    if not user_ids:
        print("\n❌ Failed to create test users. Exiting...")
        return
    
    time.sleep(0.5)
    
    # Test 3: Save games
    test_save_games(user_ids)
    time.sleep(0.5)
    
    # Test 4: Get profiles
    test_get_profile(user_ids)
    time.sleep(0.5)
    
    # Test 5: Leaderboard
    test_leaderboard()
    time.sleep(0.5)
    
    # Test 6: Global stats
    test_global_stats()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)
    print("\n💡 TIP: Check othello_users.db database file for stored data")
    print("💡 TIP: Integrate ServerUserManager in main.py to use this server\n")

if __name__ == "__main__":
    main()
