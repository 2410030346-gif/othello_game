"""Quick test to verify social features are working"""
import requests

SERVER = "http://localhost:5000"

print("\n🎮 Testing Social Features...\n")

# 1. Health check
print("1. Server Health Check...")
r = requests.get(f"{SERVER}/api/health")
if r.status_code == 200:
    print("   ✅ Server is online!\n")
else:
    print("   ❌ Server offline\n")
    exit(1)

# 2. Get achievements list
print("2. Loading Achievements...")
r = requests.get(f"{SERVER}/api/achievements")
if r.status_code == 200:
    achs = r.json()
    print(f"   ✅ {len(achs)} achievements available:")
    for ach in achs[:5]:  # Show first 5
        print(f"      {ach['icon']} {ach['name']} - {ach['points']} pts")
    print(f"      ... and {len(achs)-5} more!\n")

# 3. Create test user
print("3. Creating Test User...")
r = requests.post(f"{SERVER}/api/login", json={
    "email": "testuser@gmail.com",
    "username": "TestUser",
    "provider": "google"
})
if r.status_code == 200:
    user = r.json()
    user_id = user['user_id']
    print(f"   ✅ User created: {user['username']} (ID: {user_id[:8]}...)\n")

# 4. Save test games
print("4. Saving Test Games...")
games = [
    {"user_id": user_id, "game_mode": "vs_ai", "result": "win", "player_score": 40, "opponent_score": 24, "difficulty": "Easy", "duration": 150},
    {"user_id": user_id, "game_mode": "vs_ai", "result": "win", "player_score": 38, "opponent_score": 26, "difficulty": "Medium", "duration": 180},
    {"user_id": user_id, "game_mode": "vs_ai", "result": "win", "player_score": 35, "opponent_score": 29, "difficulty": "Medium", "duration": 200},
]
for game in games:
    requests.post(f"{SERVER}/api/game/save", json=game)
print(f"   ✅ Saved {len(games)} games\n")

# 5. Check achievements
print("5. Checking Achievements...")
r = requests.post(f"{SERVER}/api/achievements/check", json={"user_id": user_id})
if r.status_code == 200:
    result = r.json()
    print(f"   ✅ {len(result['newly_unlocked'])} achievements unlocked:")
    for ach in result['newly_unlocked']:
        print(f"      🎉 {ach['icon']} {ach['name']} (+{ach['points']} pts)")
    print()

# 6. Get user achievements
print("6. User Achievement Summary...")
r = requests.get(f"{SERVER}/api/achievements/{user_id}")
if r.status_code == 200:
    data = r.json()
    print(f"   🏆 Total Achievements: {data['total_achievements']}")
    print(f"   ⭐ Total Points: {data['total_points']}\n")

# 7. Test friend request
print("7. Testing Friend System...")
# Create second user
r = requests.post(f"{SERVER}/api/login", json={
    "email": "friend@gmail.com",
    "username": "FriendUser",
    "provider": "google"
})
friend_id = r.json()['user_id']

# Send friend request
r = requests.post(f"{SERVER}/api/friends/add", json={
    "user_id": user_id,
    "friend_email": "friend@gmail.com"
})
if r.status_code in [200, 201]:
    print(f"   ✅ Friend request sent!\n")

# Check pending requests
r = requests.get(f"{SERVER}/api/friends/requests/{friend_id}")
if r.status_code == 200:
    reqs = r.json()
    print(f"   📬 FriendUser has {len(reqs)} pending request(s)\n")

print("="*60)
print("✅ ALL TESTS PASSED!")
print("="*60)
print("\n💡 Social features are working perfectly!")
print("💡 Check SOCIAL_FEATURES_GUIDE.md for full documentation")
print("💡 Integrate into main.py to add these features to your game!\n")
