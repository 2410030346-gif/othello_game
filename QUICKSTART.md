# Quick Start Guide - Online Multiplayer

## 🎮 Play Online in 3 Easy Steps!

### Option A: Same Computer (Testing)

1. **Start the server** (Terminal 1):
   ```bash
   python server.py
   ```
   You'll see: "Server running! Players can connect to: localhost:5555"

2. **Start first game client** (Terminal 2):
   ```bash
   python main.py
   ```
   - Click PLAY → Play Online
   - Type: `localhost:5555`
   - Click CONNECT
   - Wait for opponent...

3. **Start second game client** (Terminal 3):
   ```bash
   python main.py
   ```
   - Click PLAY → Play Online  
   - Type: `localhost:5555`
   - Click CONNECT
   - Game starts automatically! 🎉

---

### Option B: Two Computers (Same Network)

**Computer 1 (Server Host):**
1. Find your IP address:
   ```bash
   ipconfig          # Windows
   ifconfig          # Mac/Linux
   ```
   Look for something like: `192.168.1.100`

2. Start the server:
   ```bash
   python server.py
   ```

3. Start the game:
   ```bash
   python main.py
   ```
   - Click PLAY → Play Online
   - Type: `localhost:5555`
   - Click CONNECT

**Computer 2 (Player):**
1. Start the game:
   ```bash
   python main.py
   ```

2. Connect to server:
   - Click PLAY → Play Online
   - Type: `192.168.1.100:5555` (use the IP from step 1)
   - Click CONNECT

3. Game starts! 🎮

---

## 🎯 Tips

- **Black** always goes first
- You can only move on your turn
- The game shows "You: Black" or "You: White"
- If opponent disconnects, you'll see a notification
- Click Settings to change colors or return to menu

## ❓ Troubleshooting

**Can't connect?**
- Make sure server is running
- Check IP address is correct
- Verify both on same Wi-Fi network
- Check firewall settings

**Server won't start?**
- Port 5555 might be in use
- Try different port: `python server.py 8080`
- Then connect to: `localhost:8080`

**Game is laggy?**
- Normal for internet play
- Best on local network (LAN)
- Check your internet connection

---

## 🎨 Customize Your Game

During gameplay, click **Settings** to:
- Change grid background color (6 options)
- Change interface color (6 options)
- Restart game
- Return to menu
- Toggle fullscreen

---

## 📚 Learn More

- `ONLINE_MULTIPLAYER.md` - Detailed setup guide
- `ARCHITECTURE.txt` - How it works
- `README.md` - Complete feature list

Have fun! 🎉
