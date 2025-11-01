"""
Training script for Modern AI
Run this to train the neural network through self-play
"""

import sys
import os

# Check if PyTorch is installed
try:
    import torch
    print(f"✅ PyTorch {torch.__version__} found")
    print(f"🔧 CUDA Available: {torch.cuda.is_available()}")
except ImportError:
    print("❌ PyTorch not installed!")
    print("\n📦 To install PyTorch, run:")
    print("   pip install torch torchvision")
    print("\nOr visit: https://pytorch.org/get-started/locally/")
    sys.exit(1)

from board import Board
from game import Game
from modern_ai import ModernOthelloAI, SelfPlayTrainer

def main():
    print("=" * 60)
    print("🧠 MODERN AI TRAINING FOR OTHELLO")
    print("=" * 60)
    
    # Configuration
    num_episodes = 1000  # Number of self-play games (increased for better learning)
    save_interval = 100   # Save model every N episodes
    
    print(f"\n⚙️  Configuration:")
    print(f"   Episodes: {num_episodes}")
    print(f"   Save Interval: {save_interval}")
    print(f"   Device: {'CUDA (GPU)' if torch.cuda.is_available() else 'CPU'}")
    
    # Initialize AI
    print("\n🎯 Initializing Modern AI...")
    ai = ModernOthelloAI()
    
    # Initialize trainer
    print("🏋️  Setting up Self-Play Trainer...")
    trainer = SelfPlayTrainer(ai, Board, Game)
    
    # Start training
    print("\n" + "=" * 60)
    print("🚀 STARTING TRAINING")
    print("=" * 60)
    print("The AI will play against itself and learn from experience.")
    print("This may take several minutes to hours depending on your hardware.\n")
    
    try:
        trainer.train(num_episodes=num_episodes, save_interval=save_interval)
    except KeyboardInterrupt:
        print("\n\n⚠️  Training interrupted by user")
        print("💾 Saving current model...")
        ai.save_model('othello_model_interrupted.pth')
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    print("\n📁 Model files saved:")
    print("   - othello_model_final.pth (final model)")
    print("   - othello_model_ep*.pth (checkpoints)")
    
    print("\n🎮 To use the trained AI in game:")
    print("   1. Run: python main.py")
    print("   2. Select 'Play vs AI'")
    print("   3. Choose difficulty (Modern AI will be used if available)")
    
    print("\n📊 Training Statistics:")
    print(f"   Total Games Played: {trainer.num_episodes}")
    print(f"   Black Wins: {trainer.total_wins_black} ({trainer.total_wins_black/trainer.num_episodes*100:.1f}%)")
    print(f"   White Wins: {trainer.total_wins_white} ({trainer.total_wins_white/trainer.num_episodes*100:.1f}%)")
    print(f"   Draws: {trainer.total_draws} ({trainer.total_draws/trainer.num_episodes*100:.1f}%)")

if __name__ == "__main__":
    main()
