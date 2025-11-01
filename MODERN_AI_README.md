# 🧠 Modern AI for Othello

## Overview
This implementation adds a **Deep Learning AI** using PyTorch alongside the classic Minimax AI. The modern AI uses a Convolutional Neural Network (CNN) with Deep Q-Learning to learn optimal Othello strategies through self-play.

## Features

### 🎯 Neural Network Architecture
- **3-channel CNN input**: Player pieces, Opponent pieces, Empty squares
- **3 Convolutional layers** with Batch Normalization (64 → 128 → 128 filters)
- **3 Fully Connected layers** (512 → 256 → 64 neurons)
- **Output**: Q-values for all 64 board positions

### 🏋️ Training Method
- **Deep Q-Learning (DQN)** with Experience Replay
- **Self-Play Training**: AI plays against itself to learn
- **Target Network**: Stable training with periodic updates
- **Epsilon-Greedy Exploration**: Balances exploration vs exploitation

### ⚡ Performance
- GPU acceleration (CUDA) if available
- Faster move selection than deep Minimax
- Learns novel strategies not in hand-crafted heuristics

---

## Installation

### 1. Install PyTorch

**For CPU only:**
```bash
pip install torch torchvision
```

**For GPU (CUDA 11.8):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**For GPU (CUDA 12.1):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

Visit [PyTorch.org](https://pytorch.org/get-started/locally/) for other configurations.

### 2. Verify Installation
```bash
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
```

---

## Training the AI

### Quick Start (500 games)
```bash
python train_modern_ai.py
```

This will:
- Play 500 self-play games
- Save model checkpoints every 50 episodes
- Create `othello_model_final.pth` (final trained model)

### Custom Training
Edit `train_modern_ai.py` to adjust:
```python
num_episodes = 1000   # More episodes = better learning
save_interval = 100   # How often to save checkpoints
```

### Training Time
- **CPU**: ~30-60 minutes for 500 games
- **GPU**: ~10-15 minutes for 500 games
- **Recommended**: 1000+ games for best results

### Training Output
```
🚀 Starting Self-Play Training for 500 episodes...
Device: cuda

Episode 10/500 | Loss: 0.1234 | ε: 0.9500 | Black: 60.0% | White: 30.0% | Draw: 10.0%
Episode 20/500 | Loss: 0.0987 | ε: 0.9025 | Black: 55.0% | White: 35.0% | Draw: 10.0%
...
✅ Training Complete!
```

---

## Using the Trained AI

### Automatic Detection
The game will automatically use the Modern AI if:
1. PyTorch is installed
2. A trained model file exists (`othello_model_final.pth` or `othello_model.pth`)

### Check AI Status
When you run the game:
```bash
python main.py
```

You'll see:
- ✅ `🧠 Modern AI loaded successfully` - Modern AI active
- ⚠️  `PyTorch available but no trained model found` - Need to train
- ℹ️  `PyTorch not installed` - Using classic AI

### In-Game Indicator
During gameplay, you'll see:
- **Modern AI**: `🧠 Modern AI thinking...` (blue text)
- **Classic AI**: `AI thinking...` (pink text)

---

## Model Files

### Generated Files
```
othello_model_final.pth          # Final trained model (use this)
othello_model_ep50.pth           # Checkpoint after 50 episodes
othello_model_ep100.pth          # Checkpoint after 100 episodes
...
othello_model_interrupted.pth   # If training was interrupted
```

### File Size
- ~15-20 MB per model file

### Loading Models
The game loads models in this priority:
1. `othello_model_final.pth` (preferred)
2. `othello_model.pth` (fallback)

---

## Architecture Details

### Network Structure
```
Input: 8x8x3 board tensor
  ↓
Conv2D(3→64) + BatchNorm + ReLU
  ↓
Conv2D(64→128) + BatchNorm + ReLU
  ↓
Conv2D(128→128) + BatchNorm + ReLU
  ↓
Flatten → 8192 values
  ↓
FC(8192→512) + ReLU + Dropout(0.3)
  ↓
FC(512→256) + ReLU
  ↓
FC(256→64)
  ↓
Output: 64 Q-values (one per board square)
```

### Hyperparameters
```python
Learning Rate: 0.001
Gamma (discount): 0.95
Batch Size: 64
Replay Buffer: 10,000 experiences
Epsilon Start: 1.0 (100% exploration)
Epsilon Decay: 0.995 per episode
Epsilon Min: 0.01 (1% exploration)
Target Network Update: Every 10 training steps
```

---

## Comparison: Modern AI vs Classic AI

| Feature | Modern AI (Deep Learning) | Classic AI (Minimax) |
|---------|---------------------------|----------------------|
| **Algorithm** | Deep Q-Learning (DQN) | Minimax + Alpha-Beta |
| **Learning** | Learns from experience | Fixed heuristics |
| **Speed** | Very Fast (GPU) | Slower at high depth |
| **Adaptability** | Adapts over time | Static strategy |
| **Setup** | Requires training | Ready immediately |
| **Dependencies** | PyTorch (~500MB) | None |
| **Novel Strategies** | Yes, discovers new tactics | No, predefined |

---

## Advanced Usage

### Continue Training Existing Model
```python
from modern_ai import ModernOthelloAI, SelfPlayTrainer
from Board import Board
from Game import Game

# Load existing model
ai = ModernOthelloAI(model_path='othello_model_final.pth')

# Continue training
trainer = SelfPlayTrainer(ai, Board, Game)
trainer.train(num_episodes=500)  # Train 500 more games
```

### Evaluate Model Performance
```python
# Play Modern AI vs Classic AI
from ai import choose_move

def evaluate_ai_battle(num_games=100):
    modern_wins = 0
    classic_wins = 0
    draws = 0
    
    for i in range(num_games):
        board = Board()
        game = Game(board)
        
        while not game.check_game_over():
            valid_moves = board.get_valid_moves(game.current_player)
            
            if game.current_player == 'B':
                # Modern AI plays Black
                move = modern_ai_instance.choose_move(board, 'B', valid_moves)
            else:
                # Classic AI plays White
                move = choose_move(board, 'W', difficulty='hard')
            
            if move:
                board.place_disc(move[0], move[1], game.current_player)
                game.switch_player()
        
        winner = game.get_winner()
        if winner == 'B':
            modern_wins += 1
        elif winner == 'W':
            classic_wins += 1
        else:
            draws += 1
    
    print(f"Modern AI: {modern_wins} wins ({modern_wins/num_games*100:.1f}%)")
    print(f"Classic AI: {classic_wins} wins ({classic_wins/num_games*100:.1f}%)")
    print(f"Draws: {draws} ({draws/num_games*100:.1f}%)")
```

---

## Troubleshooting

### PyTorch Import Error
```
❌ PyTorch not installed!
```
**Solution**: Install PyTorch
```bash
pip install torch torchvision
```

### CUDA Not Available
```
🔧 Using device: cpu
```
**Solution**: Install GPU version or continue with CPU (slower but works)

### Model Not Loading
```
⚠️ PyTorch available but no trained model found
```
**Solution**: Train the model first
```bash
python train_modern_ai.py
```

### Training Too Slow
**Solutions**:
1. Use GPU if available
2. Reduce `num_episodes` in training script
3. Use a more powerful machine
4. Download pre-trained model (if available)

---

## Future Improvements

### Possible Enhancements
1. **Curriculum Learning**: Start with easier opponents, gradually increase difficulty
2. **Monte Carlo Tree Search**: Combine DQN with MCTS (AlphaZero style)
3. **Larger Networks**: ResNet or Transformer architecture
4. **Priority Experience Replay**: Focus on important experiences
5. **Multi-GPU Training**: Distribute training across GPUs
6. **Transfer Learning**: Pre-train on chess/checkers, fine-tune for Othello
7. **Ensemble Models**: Combine multiple networks for better decisions

---

## Technical Notes

### Why Deep Q-Learning?
- **Q-Learning**: Learns action values (Q-values) for each state-action pair
- **Deep**: Uses neural network to approximate Q-function
- **Experience Replay**: Stores past experiences and learns from random batches
- **Target Network**: Prevents instability during training

### Board Representation
The board is encoded as a 3-channel tensor:
- **Channel 0**: Current player's pieces (1 = piece, 0 = no piece)
- **Channel 1**: Opponent's pieces (1 = piece, 0 = no piece)
- **Channel 2**: Empty squares (1 = empty, 0 = occupied)

This representation is rotation/reflection invariant and works well with CNNs.

---

## Credits

**Algorithm**: Deep Q-Network (DQN) by DeepMind (2015)  
**Framework**: PyTorch by Meta AI  
**Game**: Othello (Reversi) - Classic Strategy Board Game  

---

## License

This Modern AI implementation is part of the Othello Game project.
Free to use for educational and personal projects.

---

**Happy Training! 🚀🧠**
