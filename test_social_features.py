"""
Test script for Friends and Achievements features
Run this after starting auth_server.py
"""

import requests
import time

SERVER_URL = "http://localhost:5000"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_subsection(title):
    print(f"\n--- {title} ---")

def test_health():
    """Test server health check"""
    print_section("1. Testing Server Connection")
    try:
        response = requests.get(f"{SERVER_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is ONLINE!")
            print(f"   Status: {data['status']}")
            return True
        else:
            print("❌ Server returned error")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure to run: python auth_server.py")
        return False

def create_test_users():
    """Create test users"""
    print_section("2. Creating Test Users")
    
    users = [
        {"email": "alice@gmail.com", "username": "Alice", "provider": "google"},
        {"email": "bob@gmail.com", "username": "Bob", "provider": "google"},
        {"email": "charlie@gmail.com", "username": "Charlie", "provider": "facebook"},
        {"email": "diana@gmail.com", "username": "Diana", "provider": "google"},
    ]
    
    user_ids = []
    for user in users:
        response = requests.post(f"{SERVER_URL}/api/login", json=user)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created/Logged in: {user['username']} (ID: {data['user_id'][:8]}...)")
            user_ids.append((data['user_id'], user['username'], user['email']))
        else:
            print(f"❌ Failed to create {user['username']}")
    
    return user_ids

def create_game_history(users):
    """Create some game history for users"""
    print_section("3. Creating Game History")
    
    games = [
        # Alice's games
        {"user_id": users[0][0], "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Medium", "duration": 180},
        {"user_id": users[0][0], "game_mode": "vs_ai", "result": "win", "player_score": 38, "opponent_score": 26, "difficulty": "Medium", "duration": 200},
        {"user_id": users[0][0], "game_mode": "vs_ai", "result": "win", "player_score": 35, "opponent_score": 29, "difficulty": "Easy", "duration": 150},
        {"user_id": users[0][0], "game_mode": "vs_ai", "result": "win", "player_score": 64, "opponent_score": 0, "difficulty": "Easy", "duration": 90},  # Perfect game!
        {"user_id": users[0][0], "game_mode": "vs_friend", "result": "win", "player_score": 42, "opponent_score": 22, "difficulty": "N/A", "duration": 220},
        
        # Bob's games
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "win", "player_score": 35, "opponent_score": 29, "difficulty": "Easy", "duration": 160},
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "loss", "player_score": 28, "opponent_score": 36, "difficulty": "Hard", "duration": 300},
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "win", "player_score": 38, "opponent_score": 26, "difficulty": "Medium", "duration": 190},
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Hard", "duration": 280},
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "win", "player_score": 45, "opponent_score": 19, "difficulty": "Hard", "duration": 250},
        {"user_id": users[1][0], "game_mode": "vs_ai", "result": "win", "player_score": 62, "opponent_score": 2, "difficulty": "Medium", "duration": 100},  # High score!
        
        # Charlie's games
        {"user_id": users[2][0], "game_mode": "vs_friend", "result": "win", "player_score": 33, "opponent_score": 31, "difficulty": "N/A", "duration": 180},
        {"user_id": users[2][0], "game_mode": "vs_friend", "result": "win", "player_score": 36, "opponent_score": 28, "difficulty": "N/A", "duration": 170},
        {"user_id": users[2][0], "game_mode": "vs_friend", "result": "loss", "player_score": 30, "opponent_score": 34, "difficulty": "N/A", "duration": 200},
        {"user_id": users[2][0], "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Easy", "duration": 110},  # Speed win!
        
        # Diana's games
        {"user_id": users[3][0], "game_mode": "vs_ai", "result": "win", "player_score": 35, "opponent_score": 29, "difficulty": "Easy", "duration": 140},
        {"user_id": users[3][0], "game_mode": "vs_ai", "result": "loss", "player_score": 25, "opponent_score": 39, "difficulty": "Medium", "duration": 180},
    ]
    
    success_count = 0
    for game in games:
        response = requests.post(f"{SERVER_URL}/api/game/save", json=game)
        if response.status_code == 201:
            success_count += 1
    
    print(f"✅ Saved {success_count}/{len(games)} games successfully!")
    print(f"   Alice: 5 games (4 wins, 1 perfect game)")
    print(f"   Bob: 6 games (5 wins, 1 high score)")
    print(f"   Charlie: 4 games (3 wins, 1 speed win)")
    print(f"   Diana: 2 games (1 win)")

def test_achievements(users):
    """Test achievement system"""
    print_section("4. Testing Achievement System")
    
    # Get all available achievements
    print_subsection("All Available Achievements")
    response = requests.get(f"{SERVER_URL}/api/achievements")
    if response.status_code == 200:
        achievements = response.json()
        print(f"📜 {len(achievements)} total achievements available:\n")
        for ach in achievements:
            print(f"   {ach['icon']} {ach['name']} ({ach['points']} pts)")
            print(f"      {ach['description']}")
    
    time.sleep(0.5)
    
    # Check achievements for each user
    print_subsection("Checking User Achievements")
    for user_id, username, _ in users:
        response = requests.post(f"{SERVER_URL}/api/achievements/check", json={'user_id': user_id})
        if response.status_code == 200:
            data = response.json()
            print(f"\n👤 {username}:")
            if data['newly_unlocked']:
                for ach in data['newly_unlocked']:
                    print(f"   🎉 UNLOCKED: {ach['icon']} {ach['name']} (+{ach['points']} pts)")
            else:
                print(f"   No new achievements")
    
    time.sleep(0.5)
    
    # Show user achievement summary
    print_subsection("User Achievement Summary")
    for user_id, username, _ in users[:2]:  # Show first 2 users
        response = requests.get(f"{SERVER_URL}/api/achievements/{user_id}")
        if response.status_code == 200:
            data = response.json()
            print(f"\n🏆 {username}'s Achievements:")
            print(f"   Total Unlocked: {data['total_achievements']}")
            print(f"   Total Points: {data['total_points']}")
            print(f"   Achievements:")
            for ach in data['unlocked_achievements'][:5]:  # Show first 5
                print(f"      {ach['icon']} {ach['name']} - {ach['unlocked_at']}")

def test_friends(users):
    """Test friend system"""
    print_section("5. Testing Friend System")
    
    # Alice sends friend requests to Bob and Charlie
    print_subsection("Sending Friend Requests")
    alice_id, _, _ = users[0]
    bob_email = users[1][2]
    charlie_email = users[2][2]
    diana_email = users[3][2]
    
    # Alice -> Bob
    response = requests.post(f"{SERVER_URL}/api/friends/add", json={
        'user_id': alice_id,
        'friend_email': bob_email
    })
    if response.status_code in [200, 201]:
        print(f"✅ Alice sent friend request to Bob")
    
    # Alice -> Charlie
    response = requests.post(f"{SERVER_URL}/api/friends/add", json={
        'user_id': alice_id,
        'friend_email': charlie_email
    })
    if response.status_code in [200, 201]:
        print(f"✅ Alice sent friend request to Charlie")
    
    # Bob -> Diana
    bob_id = users[1][0]
    response = requests.post(f"{SERVER_URL}/api/friends/add", json={
        'user_id': bob_id,
        'friend_email': diana_email
    })
    if response.status_code in [200, 201]:
        print(f"✅ Bob sent friend request to Diana")
    
    time.sleep(0.5)
    
    # Check pending requests
    print_subsection("Pending Friend Requests")
    for user_id, username, _ in users:
        response = requests.get(f"{SERVER_URL}/api/friends/requests/{user_id}")
        if response.status_code == 200:
            requests_list = response.json()
            if requests_list:
                print(f"\n📬 {username} has {len(requests_list)} pending request(s):")
                for req in requests_list:
                    print(f"   From: {req['username']} ({req['email']})")
            else:
                print(f"\n📭 {username} has no pending requests")
    
    time.sleep(0.5)
    
    # Accept friend requests
    print_subsection("Accepting Friend Requests")
    
    # Bob accepts Alice's request
    bob_id = users[1][0]
    alice_id = users[0][0]
    response = requests.post(f"{SERVER_URL}/api/friends/accept", json={
        'user_id': bob_id,
        'friend_id': alice_id
    })
    if response.status_code == 200:
        print(f"✅ Bob accepted Alice's friend request")
    
    # Charlie accepts Alice's request
    charlie_id = users[2][0]
    response = requests.post(f"{SERVER_URL}/api/friends/accept", json={
        'user_id': charlie_id,
        'friend_id': alice_id
    })
    if response.status_code == 200:
        print(f"✅ Charlie accepted Alice's friend request")
    
    # Diana accepts Bob's request
    diana_id = users[3][0]
    response = requests.post(f"{SERVER_URL}/api/friends/accept", json={
        'user_id': diana_id,
        'friend_id': bob_id
    })
    if response.status_code == 200:
        print(f"✅ Diana accepted Bob's friend request")
    
    time.sleep(0.5)
    
    # Show friends lists
    print_subsection("Friends Lists")
    for user_id, username, _ in users:
        response = requests.get(f"{SERVER_URL}/api/friends/list/{user_id}")
        if response.status_code == 200:
            friends = response.json()
            if friends:
                print(f"\n👥 {username}'s Friends ({len(friends)}):")
                for friend in friends:
                    print(f"   • {friend['username']} - {friend['total_games']} games, {friend['win_rate']}% win rate")
            else:
                print(f"\n{username} has no friends yet")

def test_leaderboard():
    """Test leaderboard"""
    print_section("6. Global Leaderboard")
    
    response = requests.get(f"{SERVER_URL}/api/leaderboard?limit=10")
    if response.status_code == 200:
        leaderboard = response.json()
        if leaderboard:
            print("\n🏆 TOP PLAYERS (Minimum 5 games required)\n")
            print(f"{'Rank':<6} {'Username':<15} {'Games':<8} {'Wins':<8} {'Win Rate':<12}")
            print("-" * 60)
            for i, player in enumerate(leaderboard, 1):
                print(f"{i:<6} {player['username']:<15} {player['total_games']:<8} {player['wins']:<8} {player['win_rate']:.1f}%")
        else:
            print("\n⚠️  No players qualify for leaderboard yet")

def test_global_stats():
    """Test global statistics"""
    print_section("7. Global Statistics")
    
    response = requests.get(f"{SERVER_URL}/api/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"\n📊 SERVER STATISTICS")
        print(f"   Total Users: {stats['total_users']}")
        print(f"   Total Games Played: {stats['total_games']}")
        print(f"   Average Score: {stats['average_score']:.2f}")

def main():
    print("\n" + "🎮 OTHELLO SOCIAL FEATURES TEST SUITE " + "\n")
    print("This will test the Friends and Achievements systems!")
    print("Make sure auth_server.py is running first!")
    print("Start it with: python auth_server.py\n")
    
    time.sleep(1)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running. Exiting...")
        return
    
    time.sleep(0.5)
    
    # Test 2: Create users
    users = create_test_users()
    if not users or len(users) < 4:
        print("\n❌ Failed to create test users. Exiting...")
        return
    
    time.sleep(0.5)
    
    # Test 3: Create game history
    create_game_history(users)
    time.sleep(0.5)
    
    # Test 4: Test achievements
    test_achievements(users)
    time.sleep(0.5)
    
    # Test 5: Test friends
    test_friends(users)
    time.sleep(0.5)
    
    # Test 6: Leaderboard
    test_leaderboard()
    time.sleep(0.5)
    
    # Test 7: Global stats
    test_global_stats()
    
    print("\n" + "="*70)
    print("✅ ALL SOCIAL FEATURES TESTS COMPLETED!")
    print("="*70)
    print("\n💡 Features Tested:")
    print("   ✓ Friend Requests (send/accept/list)")
    print("   ✓ Achievement System (12 different achievements)")
    print("   ✓ Leaderboards (global rankings)")
    print("   ✓ Game History Tracking")
    print("\n💡 Check othello_users.db for all stored data")
    print("💡 Integrate these features into main.py for full experience!\n")

if __name__ == "__main__":
    main()
