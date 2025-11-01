# Othello Game - Complete Flowchart Diagram

## Main Game Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         START GAME                              │
│                    (Initialize Pygame)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MAIN MENU STATE                            │
│                                                                 │
│              ┌──────────────┐   ┌──────────────┐              │
│              │  ▶ PLAY      │   │  ✖ EXIT      │              │
│              └──────┬───────┘   └──────┬───────┘              │
└─────────────────────┼──────────────────┼───────────────────────┘
                      │                  │
                      │                  └────────► END GAME
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PLAY MODE SELECTION                          │
│                                                                 │
│    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│    │  PLAY vs AI  │  │ PLAY FRIEND  │  │  ◄ BACK      │      │
│    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└───────────┼──────────────────┼──────────────────┼──────────────┘
            │                  │                  │
            │                  │                  └──► MAIN MENU
            │                  │
            │                  ├──────────────────────┐
            │                  │                      │
            ▼                  ▼                      ▼
   ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
   │   DIFFICULTY    │  │  LOCAL 2P GAME  │  │      BACK       │
   │   SELECTION     │  │   (No AI)       │  │   TO MENU       │
   └────────┬────────┘  └────────┬────────┘  └─────────────────┘
            │                    │
            │                    │
            ▼                    │
   ┌─────────────────────────────┤
   │  Select Difficulty:         │
   │  • EASY (depth 2)           │
   │  • MEDIUM (depth 3)         │
   │  • HARD (depth 4-5)         │
   └────────┬────────────────────┘
            │
            │
            └────────────┬────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PLAYING STATE                             │
│                    (Main Game Loop)                             │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  1. Draw Board (8×8 Grid)                                 │ │
│  │  2. Draw Discs (Black/White with animations)              │ │
│  │  3. Show Valid Moves (Pulsing green circles)              │ │
│  │  4. Highlight Last Move (Yellow glow)                     │ │
│  │  5. Display Score Panels                                  │ │
│  │  6. Show Turn Indicator Overlay                           │ │
│  │  7. Settings Button (top-right)                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│                    Current Player Turn?                         │
│              ┌──────────┴──────────┐                           │
│              ▼                     ▼                            │
│         ┌─────────┐          ┌──────────┐                      │
│         │ HUMAN   │          │    AI    │                      │
│         │  TURN   │          │   TURN   │                      │
│         └────┬────┘          └─────┬────┘                      │
└──────────────┼───────────────────────┼──────────────────────────┘
               │                       │
               ▼                       ▼
    ┌──────────────────────┐   ┌──────────────────────┐
    │  WAIT FOR CLICK      │   │ AI THINKING          │
    │  • Check board click │   │ • Show overlay       │
    │  • Validate move     │   │ • 1.5s thinking time │
    │  • Place disc        │   │ • Choose best move   │
    │  • Play sounds       │   │ • Use Minimax/DQN    │
    └──────────┬───────────┘   └──────────┬───────────┘
               │                          │
               │                          ▼
               │               ┌──────────────────────┐
               │               │  AI PLACES DISC      │
               │               │  • Place on board    │
               │               │  • Play place sound  │
               │               │  • 4s display time   │
               │               └──────────┬───────────┘
               │                          │
               └──────────┬───────────────┘
                          │
                          ▼
            ┌──────────────────────────────┐
            │   DISC PLACEMENT LOGIC       │
            │                              │
            │ 1. Place disc on board       │
            │ 2. Play place_sound          │
            │ 3. Find flipped discs        │
            │ 4. Animate flipping          │
            │ 5. Play flip_sound           │
            │ 6. Update scores             │
            │ 7. Switch player             │
            └──────────┬───────────────────┘
                       │
                       ▼
            ┌──────────────────────────────┐
            │   CHECK GAME STATUS          │
            │                              │
            │ • Any valid moves left?      │
            │ • Both players blocked?      │
            │ • Board full?                │
            └──────────┬───────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
        ┌──────────┐      ┌──────────────┐
        │ CONTINUE │      │  GAME OVER   │
        │  GAME    │      │    STATE     │
        └─────┬────┘      └──────┬───────┘
              │                  │
              │                  ▼
              │         ┌────────────────────────────┐
              │         │   GAME OVER SCREEN         │
              │         │                            │
              │         │ • Semi-transparent overlay │
              │         │ • Display winner           │
              │         │ • Show final scores        │
              │         │ • Play win/lose sound      │
              │         │                            │
              │         │  ┌──────────┐ ┌─────────┐ │
              │         │  │ RESTART  │ │  MENU   │ │
              │         │  └────┬─────┘ └────┬────┘ │
              │         └───────┼────────────┼──────┘
              │                 │            │
              └─────────────────┘            └──► MAIN MENU
```

## Settings Panel Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  SETTINGS BUTTON CLICKED                        │
│                  (During Gameplay)                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SETTINGS PANEL OPENS                         │
│                  (Side panel with options)                      │
│                                                                 │
│  ┌────────────────────────────────────────────────────┐        │
│  │ • RESTART       → Reset game                       │        │
│  │ • MAIN MENU     → Return to menu                   │        │
│  │ • TOGGLE AI     → Enable/Disable AI                │        │
│  │ • DIFFICULTY    → Easy/Medium/Hard                 │        │
│  │ • PLAY AS       → Black/White                      │        │
│  │ • GRID COLOR    → 6 color options                  │        │
│  │ • UI COLOR      → 6 color options                  │        │
│  └────────────────────────────────────────────────────┘        │
│                                                                 │
│  Each button click → Play click_sound                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## AI Decision Making Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI TURN STARTS                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  Check AI Type       │
                  │  Available?          │
                  └──────┬───────┬───────┘
                         │       │
            ┌────────────┘       └────────────┐
            │                                 │
            ▼                                 ▼
   ┌─────────────────────┐         ┌─────────────────────┐
   │  MODERN AI          │         │  CLASSIC AI         │
   │  (Deep Learning)    │         │  (Minimax)          │
   │                     │         │                     │
   │  ┌──────────────┐  │         │  ┌──────────────┐  │
   │  │ Neural Net   │  │         │  │ Minimax Tree │  │
   │  │ CNN (3 Conv) │  │         │  │ Alpha-Beta   │  │
   │  │ 64→128→128   │  │         │  │ Pruning      │  │
   │  └──────┬───────┘  │         │  └──────┬───────┘  │
   │         │          │         │         │          │
   │         ▼          │         │         ▼          │
   │  ┌──────────────┐  │         │  ┌──────────────┐  │
   │  │ Q-Learning   │  │         │  │ Heuristic    │  │
   │  │ Choose Max   │  │         │  │ Evaluation   │  │
   │  │ Q-Value      │  │         │  │ - Position   │  │
   │  └──────┬───────┘  │         │  │ - Mobility   │  │
   └─────────┼──────────┘         │  │ - Stability  │  │
             │                    │  └──────┬───────┘  │
             │                    └─────────┼──────────┘
             │                              │
             └──────────┬───────────────────┘
                        │
                        ▼
              ┌──────────────────────┐
              │  Return Best Move    │
              │  (row, col)          │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  Place Disc & Flip   │
              │  Play Sounds         │
              │  4-Second Display    │
              └──────────────────────┘
```

## Sound System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SOUND GENERATION                             │
│                  (NumPy + Pygame Mixer)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              GENERATE SOUND EFFECTS AT STARTUP                  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ click_sound    → 800 Hz, 0.1s  (Buttons)                 │ │
│  │ hover_sound    → 600 Hz, 0.05s (Hover feedback)          │ │
│  │ place_sound    → 400 Hz, 0.15s (Disc placement)          │ │
│  │ flip_sound     → 800→300 Hz sweep (Disc flipping)        │ │
│  │ win_sound      → 523 Hz, 0.3s  (Victory)                 │ │
│  │ error_sound    → 200 Hz, 0.2s  (Loss/Error)              │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   EVENT TRIGGERS     │
                  └──────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
   │   Button    │  │    Disc     │  │  Game Over  │
   │   Click     │  │  Placement  │  │   Result    │
   │             │  │             │  │             │
   │ • Play      │  │ • Place     │  │ • Win       │
   │ • Exit      │  │   disc      │  │ • Lose      │
   │ • Mode      │  │ • Flip      │  │ • Tie       │
   │ • Diff      │  │   discs     │  │             │
   │ • Settings  │  │             │  │             │
   │             │  │ Sounds:     │  │ Sounds:     │
   │ Sound:      │  │ • place     │  │ • win       │
   │ click_sound │  │ • flip      │  │ • error     │
   └─────────────┘  └─────────────┘  └─────────────┘
```

## Animation System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANIMATION PIPELINE                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
   ┌────────────────┐ ┌────────────┐ ┌────────────────┐
   │ DISC FLIPPING  │ │ VALID MOVE │ │  LAST MOVE     │
   │   ANIMATION    │ │  PULSING   │ │  HIGHLIGHT     │
   │                │ │            │ │                │
   │ • Scale X:     │ │ • Radius:  │ │ • Glow:        │
   │   1 → 0 → 1    │ │   ±10px    │ │   ±20px        │
   │ • Color flip   │ │ • Period:  │ │ • Period:      │
   │   at X=0       │ │   500ms    │ │   600ms        │
   │ • Duration:    │ │ • Formula: │ │ • Formula:     │
   │   300ms        │ │   sin(t)   │ │   sin(t)       │
   │                │ │            │ │                │
   │ Queue:         │ │ Real-time  │ │ Real-time      │
   │ animating_     │ │ calculation│ │ calculation    │
   │ discs[]        │ │            │ │                │
   └────────────────┘ └────────────┘ └────────────────┘
```

## Visual Effects Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   RENDERING PIPELINE                            │
│                     (60 FPS Loop)                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Clear Screen    │
                    │ (BG Color)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Board Base │
                    │ (Grid Color)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Grid Lines │
                    │ (1px White)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Discs      │
                    │ • Black/White   │
                    │ • Anti-aliased  │
                    │ • Animations    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Valid      │
                    │ Moves (Pulsing) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Highlight Last  │
                    │ Move (Glow)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Score      │
                    │ Panels (Both)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Turn       │
                    │ Indicator       │
                    │ (Overlay)       │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Draw Buttons    │
                    │ • Multi-layer   │
                    │   shadows       │
                    │ • Glow effects  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ pygame.display  │
                    │ .flip()         │
                    └─────────────────┘
```

## Network Multiplayer Flow (Optional Feature)

```
┌─────────────────────────────────────────────────────────────────┐
│                   ONLINE MULTIPLAYER                            │
│                    (TCP Sockets)                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
                  ┌──────────┴──────────┐
                  │                     │
                  ▼                     ▼
         ┌─────────────────┐   ┌─────────────────┐
         │     HOST        │   │     CLIENT      │
         │   (Server)      │   │                 │
         └────────┬────────┘   └────────┬────────┘
                  │                     │
                  │    TCP Connect      │
                  │◄────────────────────┤
                  │                     │
                  │   Confirm + Color   │
                  ├────────────────────►│
                  │                     │
        ┌─────────▼─────────┐           │
        │  Wait for move    │           │
        └─────────┬─────────┘           │
                  │                     │
                  │                ┌────▼──────┐
                  │                │ Make move │
                  │                └────┬──────┘
                  │                     │
                  │   Send move data    │
                  │◄────────────────────┤
                  │                     │
        ┌─────────▼─────────┐           │
        │  Apply move       │           │
        │  Update board     │           │
        └─────────┬─────────┘           │
                  │                     │
                  │  Confirm receipt    │
                  ├────────────────────►│
                  │                     │
                  │         (Loop until game over)
                  │                     │
```

## State Machine Overview

```
STATE_MAIN_MENU
    ↓ [Play]
STATE_PLAY_MODE
    ↓ [vs AI]
STATE_DIFFICULTY
    ↓ [Select]
STATE_PLAYING ←──────┐
    ↓                │
[Game Over?]         │
    ↓ [No] ──────────┘
    ↓ [Yes]
[Display Results]
    ↓ [Restart]
STATE_PLAYING
    ↓ [Menu]
STATE_MAIN_MENU
```

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        MAIN.PY (2332 lines)                     │
│                         Main Game Loop                          │
│                                                                 │
│  • State Management                                             │
│  • Rendering Pipeline                                           │
│  • Event Handling                                               │
│  • Sound System                                                 │
│  • UI Drawing                                                   │
│  • Animation System                                             │
│                                                                 │
└──────┬──────────┬──────────┬──────────┬──────────┬─────────────┘
       │          │          │          │          │
       ▼          ▼          ▼          ▼          ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐
│BOARD.PY │ │GAME.PY  │ │ AI.PY   │ │MODERN_AI │ │NETWORK   │
│         │ │         │ │         │ │   .PY    │ │  .PY     │
│• 8×8    │ │• State  │ │• Minimax│ │• CNN     │ │• TCP     │
│  Grid   │ │• Rules  │ │• Alpha  │ │• DQN     │ │• Client  │
│• Valid  │ │• Turn   │ │  -Beta  │ │• Replay  │ │• Server  │
│  Moves  │ │• Winner │ │• Depth  │ │  Buffer  │ │• Sync    │
│• Flip   │ │         │ │  2-5    │ │• Self-   │ │          │
│  Logic  │ │         │ │• Heur.  │ │  Play    │ │          │
└─────────┘ └─────────┘ └─────────┘ └──────────┘ └──────────┘
```

---

**Legend:**
- `│ └ ┌ ┐ ┘ ┴ ┬ ├ ┤ ┼` = Flow connectors
- `▼ ◄ ►` = Direction arrows
- `→` = Action/Transition
- `• ` = List items
- `[ ]` = Decision/User action

