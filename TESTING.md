# Testing Checklist - Online Multiplayer

## ✅ Pre-Testing Setup
- [ ] Python 3.7+ installed
- [ ] pygame installed: `pip install pygame`
- [ ] numpy installed: `pip install numpy`
- [ ] All files present in directory

## 🧪 Local Testing (Same Computer)

### Test 1: Server Start
- [ ] Run `python server.py` or `start_server.bat`
- [ ] Server displays "Server running on port 5555"
- [ ] No error messages

### Test 2: Single Client Connection
- [ ] Start server (keep it running)
- [ ] Run `python main.py` or `start_game.bat`
- [ ] Navigate: PLAY → Play Online
- [ ] Enter: `localhost:5555`
- [ ] Click CONNECT
- [ ] Should see "Waiting for Opponent" screen
- [ ] No crash or error

### Test 3: Two Clients Matchmaking
- [ ] Keep server running
- [ ] Start first client, connect (waiting screen appears)
- [ ] Start second client in new terminal
- [ ] Second client connects
- [ ] Both clients automatically start game
- [ ] First player is Black, second is White
- [ ] Turn indicator shows "You: Black" or "You: White"

### Test 4: Online Gameplay
- [ ] Black player can place pieces
- [ ] White player sees Black's moves appear
- [ ] White player can place pieces on their turn
- [ ] Black player sees White's moves appear
- [ ] Discs flip with animation
- [ ] Score updates correctly
- [ ] Turn indicator updates
- [ ] Sound effects play

### Test 5: Turn Enforcement
- [ ] Black player tries to move during White's turn
- [ ] Move should be ignored
- [ ] White player tries to move during Black's turn
- [ ] Move should be ignored
- [ ] Only current player can move

### Test 6: Game Completion
- [ ] Play until game ends
- [ ] Winner is displayed correctly
- [ ] Both clients show same winner
- [ ] Can return to menu

### Test 7: Disconnection Handling
- [ ] Start game with two clients
- [ ] Close one client window
- [ ] Other client shows "Opponent Disconnected!"
- [ ] No crash
- [ ] Can return to menu

### Test 8: Connection Errors
- [ ] Try to connect without server running
- [ ] Should see "Failed to connect to server" message
- [ ] Can click back to return to menu
- [ ] No crash

### Test 9: Invalid Server Address
- [ ] Enter invalid address (e.g., "abc123")
- [ ] Click connect
- [ ] Should show error message
- [ ] Can try again with correct address

### Test 10: Cancel While Waiting
- [ ] Connect to server (waiting screen)
- [ ] Click CANCEL button
- [ ] Returns to Play Mode menu
- [ ] Can reconnect successfully

## 🌐 Network Testing (Two Computers)

### Test 11: LAN Connection
- [ ] Find server computer's IP address
- [ ] Start server on Computer 1
- [ ] Start client on Computer 2
- [ ] Enter server IP:port (e.g., `192.168.1.100:5555`)
- [ ] Successfully connects
- [ ] Game works smoothly

### Test 12: Firewall Test
- [ ] If connection fails, check firewall
- [ ] Allow Python through firewall
- [ ] Test connection again
- [ ] Should work after firewall configured

## 🎨 Feature Testing

### Test 13: Settings During Online Game
- [ ] Start online game
- [ ] Open settings panel
- [ ] Change grid color
- [ ] Change interface color
- [ ] Colors update correctly
- [ ] Game still playable

### Test 14: Window Resize During Online Game
- [ ] Start online game
- [ ] Resize window
- [ ] Board scales correctly
- [ ] Can still make moves
- [ ] Opponent's moves still appear

### Test 15: Multiple Games
- [ ] Three clients connect to server
- [ ] First two get matched (Game 1)
- [ ] Third client waits
- [ ] Start fourth client
- [ ] Third and fourth get matched (Game 2)
- [ ] Both games work independently

## 🐛 Edge Cases

### Test 16: Rapid Moves
- [ ] Make moves quickly
- [ ] No desync between clients
- [ ] All moves register
- [ ] Animations complete

### Test 17: Server Restart
- [ ] Start game with clients
- [ ] Stop server
- [ ] Clients detect disconnection
- [ ] Restart server
- [ ] Clients can reconnect

### Test 18: Port Already in Use
- [ ] Start server on port 5555
- [ ] Try to start second server on port 5555
- [ ] Should fail gracefully
- [ ] Try different port: `python server.py 5556`
- [ ] Should work

## 📊 Test Results Template

Date: ___________
Tester: ___________

| Test # | Description | Pass/Fail | Notes |
|--------|-------------|-----------|-------|
| 1      | Server Start |           |       |
| 2      | Single Client |           |       |
| 3      | Matchmaking |           |       |
| 4      | Gameplay |           |       |
| 5      | Turn Enforcement |           |       |
| 6      | Game Complete |           |       |
| 7      | Disconnection |           |       |
| 8      | Connection Error |           |       |
| 9      | Invalid Address |           |       |
| 10     | Cancel Wait |           |       |
| 11     | LAN Connection |           |       |
| 12     | Firewall |           |       |
| 13     | Settings |           |       |
| 14     | Window Resize |           |       |
| 15     | Multiple Games |           |       |
| 16     | Rapid Moves |           |       |
| 17     | Server Restart |           |       |
| 18     | Port Conflict |           |       |

## 🔍 Known Limitations

- No reconnection after disconnect
- No game state persistence
- Basic error handling
- No move validation server-side
- No encryption
- No authentication
- Simple matchmaking (FIFO)

## ✨ Success Criteria

Online multiplayer is working correctly if:
- ✅ Server starts without errors
- ✅ Clients can connect
- ✅ Players are automatically matched
- ✅ Moves synchronize between clients
- ✅ Game rules are enforced
- ✅ Disconnections are handled gracefully
- ✅ Multiple games can run simultaneously
- ✅ No crashes or data corruption
