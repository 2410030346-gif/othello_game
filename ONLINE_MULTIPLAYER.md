# Othello Game - Online Multiplayer Guide

## Features
- Play vs AI (Easy, Medium, Hard)
- Play vs Friend (Local multiplayer)
- **Play Online (Network multiplayer)** 🌐
- Animated disc flips
- Sound effects
- Customizable colors
- Resizable window

## How to Play Online

### Step 1: Start the Server
One player needs to host a game server. Open a terminal/command prompt and run:

```bash
python server.py
```

The server will start on port 5555 by default. You can specify a different port:

```bash
python server.py 8080
```

**Note:** The server will display messages when players connect and games start.

### Step 2: Connect Players
Each player runs the game client:

```bash
python main.py
```

1. Click **PLAY** from the main menu
2. Click **Play Online**
3. Enter the server address:
   - For local testing: `localhost:5555`
   - For network play: `<SERVER_IP>:5555` (e.g., `192.168.1.100:5555`)
4. Click **CONNECT**

### Step 3: Wait for Opponent
- The first player will see "Waiting for Opponent"
- Once a second player connects, the game starts automatically
- Player 1 gets Black pieces, Player 2 gets White pieces

### Step 4: Play the Game
- Take turns placing pieces
- You can only place pieces on your turn
- The game shows "You: Black" or "You: White" to indicate your color
- Pieces flip with smooth animations
- If your opponent disconnects, you'll see a notification

## Network Setup Tips

### Playing on the Same Network (LAN)
1. Find the server host's IP address:
   - Windows: Open Command Prompt and run `ipconfig`
   - Look for "IPv4 Address" (e.g., 192.168.1.100)
   - Mac/Linux: Open Terminal and run `ifconfig` or `ip addr`
   
2. Make sure both computers are on the same network (Wi-Fi or Ethernet)

3. The client should connect to: `<SERVER_IP>:5555`

### Playing Over the Internet
For internet play, you'll need to:
1. Port forward port 5555 on the server's router
2. Use the server's public IP address (find at whatismyip.com)
3. Consider security implications

### Firewall
- Make sure your firewall allows Python to accept connections on port 5555
- You may need to add an exception in Windows Defender or your antivirus

## Troubleshooting

### "Failed to connect to server"
- Make sure the server is running
- Check the IP address and port are correct
- Verify firewall settings
- Ensure both devices are on the same network

### "Connection error"
- The server might not be accessible
- Check if the port is already in use
- Try a different port number

### Game feels laggy
- This is normal for internet play with high latency
- For best experience, play on local network (LAN)

## Game Controls
- **Mouse**: Click to place pieces
- **Settings Button**: Access color customization and menu options
- **ESC**: Close settings panel
- **Window Resize**: Drag window edges to resize

## Requirements
- Python 3.7+
- Pygame
- NumPy (for sound effects)

## Installation
```bash
pip install pygame numpy
```

Enjoy playing Othello online with your friends! 🎮
