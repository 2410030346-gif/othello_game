# Othello Game - Complete Feature List

## Game Modes

### 1. Play vs AI
- Three difficulty levels:
  - **Easy**: Random moves
  - **Medium**: Strategic corner preference
  - **Hard**: Minimax algorithm with depth 3
- AI thinking animation
- Smooth gameplay with 800ms thinking delay

### 2. Play vs Friend (Local)
- Two players on the same computer
- Hot-seat multiplayer
- Turn-based gameplay

### 3. Play Online (🌐 NEW!)
- Network multiplayer over LAN or internet
- Client-server architecture
- Automatic matchmaking
- Real-time move synchronization
- Disconnect detection
- Visual indicators for your color and current turn

## Visual Features

### Animated Disc Flips
- Smooth 3D flip animation when pieces change color
- Horizontal scaling effect
- Synchronized animations for multiple flips
- 60 FPS animation at 0.15 speed

### Customizable Colors
- **6 Grid Background Options**: Green, Blue, Purple, Teal, Brown, Navy
- **6 Interface Background Options**: Dark Gray, Dark Blue, Dark Purple, Dark Red, Dark Teal, Dark Brown
- **Pink Theme**: Consistent pink highlights (255, 105, 180)

### UI Elements
- Gradient backgrounds on all menus
- Animated circles on waiting screen
- Hover effects on buttons
- Valid move indicators
- Score display
- Turn indicator
- Collapsible settings panel

## Audio Features

### Procedural Sound Effects
- Place Disc, Button Click, Win, Lose, Menu Navigation sounds
- Generated using NumPy sine waves
- Smooth fade-out to prevent clicks

## Files

### Core Game Files
- `main.py` - Main game loop and UI (1000+ lines)
- `board.py` - Game board logic
- `game.py` - Game state management
- `ai.py` - AI algorithms
- `constants.py` - Game constants

### Network Files (NEW!)
- `network.py` - Client and server classes
- `server.py` - Standalone game server
- `test_server.py` - Server connectivity test

### Documentation
- `ONLINE_MULTIPLAYER.md` - Complete online play guide
- `README.md` - This file

## Requirements
```bash
pip install pygame numpy
```

## Running the Game

### Local Play
```bash
python main.py
```

### Online Multiplayer
**Step 1 - Start Server (one person):**
```bash
python server.py
```

**Step 2 - Connect Clients (both players):**
```bash
python main.py
```
Then: PLAY → Play Online → Enter server address → CONNECT

See `ONLINE_MULTIPLAYER.md` for detailed instructions.

## Controls
- **Mouse**: Click to place pieces, interact with UI
- **Settings Button**: Toggle settings panel
- **ESC/Click Outside**: Close settings panel
- **Window Borders**: Drag to resize

---

Developed with ❤️ using Python and Pygame
