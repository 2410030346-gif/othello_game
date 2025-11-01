"""
Modern AI for Othello using Deep Neural Networks
Implements Deep Q-Learning with PyTorch
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import os

class OthelloNeuralNetwork(nn.Module):
    """Deep Neural Network for Othello move prediction"""
    
    def __init__(self):
        super(OthelloNeuralNetwork, self).__init__()
        
        # Convolutional layers to process board state (3 channels: player, opponent, empty)
        self.conv1 = nn.Conv2d(3, 64, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(64)
        self.conv2 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(128)
        self.conv3 = nn.Conv2d(128, 128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 8 * 8, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 64)  # Output: Q-values for each board position
        
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, board_state):
        """
        Input: Batch of 8x8x3 board tensors
        Output: 64 Q-values (one per square)
        """
        x = self.relu(self.bn1(self.conv1(board_state)))
        x = self.relu(self.bn2(self.conv2(x)))
        x = self.relu(self.bn3(self.conv3(x)))
        
        x = x.view(x.size(0), -1)  # Flatten
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x


class ReplayBuffer:
    """Experience Replay Buffer for training"""
    
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample random batch from buffer"""
        return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    def __len__(self):
        return len(self.buffer)


class ModernOthelloAI:
    """Modern ML-based AI opponent using Deep Q-Learning"""
    
    def __init__(self, model_path=None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"🔧 Using device: {self.device}")
        
        # Main network
        self.policy_net = OthelloNeuralNetwork().to(self.device)
        # Target network for stable training
        self.target_net = OthelloNeuralNetwork().to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=0.001)
        self.memory = ReplayBuffer(capacity=10000)
        
        # Hyperparameters
        self.epsilon = 0.1  # Exploration rate (lower for trained model)
        self.gamma = 0.95   # Discount factor
        self.batch_size = 64
        self.target_update_freq = 10
        self.training_step = 0
        
        # Load pre-trained model if available
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
            print(f"✅ Loaded pre-trained model from {model_path}")
        else:
            print("⚠️  No pre-trained model found. AI will play with untrained network.")
    
    def board_to_tensor(self, board, current_player):
        """Convert board state to 3-channel tensor"""
        state = np.zeros((3, 8, 8), dtype=np.float32)
        
        for i in range(8):
            for j in range(8):
                cell = board.grid[i][j]
                if cell == current_player:
                    state[0, i, j] = 1  # Current player's pieces
                elif cell != ' ':
                    state[1, i, j] = 1  # Opponent's pieces
                else:
                    state[2, i, j] = 1  # Empty squares
        
        return torch.FloatTensor(state).unsqueeze(0).to(self.device)
    
    def choose_move(self, board, current_player, valid_moves, training=False):
        """Select best move using neural network"""
        
        if not valid_moves:
            return None
        
        # Exploration: Random move with epsilon probability during training
        if training and np.random.random() < self.epsilon:
            return random.choice(valid_moves)
        
        # Exploitation: Use neural network to choose best move
        state_tensor = self.board_to_tensor(board, current_player)
        
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)
        
        # Convert Q-values to 8x8 grid
        q_values = q_values.cpu().numpy().reshape(8, 8)
        
        # Find best valid move
        best_move = None
        best_q = float('-inf')
        
        for move in valid_moves:
            row, col = move
            if q_values[row, col] > best_q:
                best_q = q_values[row, col]
                best_move = move
        
        return best_move if best_move else valid_moves[0]
    
    def store_experience(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """Perform one training step using experience replay"""
        
        if len(self.memory) < self.batch_size:
            return 0.0
        
        # Sample batch from memory
        batch = self.memory.sample(self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.cat(states)
        next_states = torch.cat(next_states)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Current Q-values
        current_q_values = self.policy_net(states)
        current_q_values = current_q_values.gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q-values
        with torch.no_grad():
            next_q_values = self.target_net(next_states)
            max_next_q_values = next_q_values.max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * max_next_q_values
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
        self.optimizer.step()
        
        # Update target network periodically
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())
        
        return loss.item()
    
    def save_model(self, path='othello_model.pth'):
        """Save model to disk"""
        torch.save({
            'policy_net_state_dict': self.policy_net.state_dict(),
            'target_net_state_dict': self.target_net.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'training_step': self.training_step,
            'epsilon': self.epsilon
        }, path)
        print(f"💾 Model saved to {path}")
    
    def load_model(self, path='othello_model.pth'):
        """Load model from disk"""
        checkpoint = torch.load(path, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint['policy_net_state_dict'])
        self.target_net.load_state_dict(checkpoint['target_net_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.training_step = checkpoint.get('training_step', 0)
        self.epsilon = checkpoint.get('epsilon', 0.1)
        self.policy_net.eval()
        print(f"📂 Model loaded from {path}")


class SelfPlayTrainer:
    """Train AI through self-play"""
    
    def __init__(self, ai, board_class, game_class):
        self.ai = ai
        self.Board = board_class
        self.Game = game_class
        self.num_episodes = 0
        self.total_wins_black = 0
        self.total_wins_white = 0
        self.total_draws = 0
    
    def play_game(self, training=True):
        """Play one complete self-play game"""
        from board import Board
        from game import Game
        
        board = Board()
        game = Game(board)
        game_history = []
        
        while not game.check_game_over():
            valid_moves = board.get_valid_moves(game.current_player)
            
            if not valid_moves:
                game.switch_player()
                continue
            
            # Get current state
            state = self.ai.board_to_tensor(board, game.current_player)
            
            # AI chooses move
            move = self.ai.choose_move(board, game.current_player, valid_moves, training=training)
            
            if move:
                row, col = move
                action_idx = row * 8 + col
                
                # Make move
                board.place_disc(row, col, game.current_player)
                
                # Get next state
                next_state = self.ai.board_to_tensor(board, game.current_player)
                
                # Store experience (reward will be calculated at game end)
                game_history.append({
                    'state': state,
                    'action': action_idx,
                    'next_state': next_state,
                    'player': game.current_player
                })
                
                game.switch_player()
        
        # Calculate final reward
        winner_color, counts = game.winner()
        
        # Assign rewards to each player's moves
        for experience in game_history:
            player = experience['player']
            
            if winner_color is None:
                reward = 0.0  # Draw
            elif winner_color == player:
                reward = 1.0  # Win
            else:
                reward = -1.0  # Loss
            
            # Add score difference as additional reward
            if player == 'B':
                score_diff = (counts['B'] - counts['W']) / 64.0
            else:
                score_diff = (counts['W'] - counts['B']) / 64.0
            
            reward += score_diff * 0.1
            
            # Store in replay buffer
            self.ai.store_experience(
                experience['state'],
                experience['action'],
                reward,
                experience['next_state'],
                1.0 if winner_color is not None else 0.0
            )
        
        # Update statistics
        self.num_episodes += 1
        if winner_color == 'B':
            self.total_wins_black += 1
        elif winner_color == 'W':
            self.total_wins_white += 1
        else:
            self.total_draws += 1
        
        return winner_color, counts
    
    def train(self, num_episodes=1000, save_interval=100):
        """Train through self-play"""
        print(f"🚀 Starting Self-Play Training for {num_episodes} episodes...")
        print(f"Device: {self.ai.device}")
        
        losses = []
        
        for episode in range(num_episodes):
            # Play one game
            winner, counts = self.play_game(training=True)
            
            # Train on experiences
            if len(self.ai.memory) >= self.ai.batch_size:
                for _ in range(10):  # Multiple training steps per game
                    loss = self.ai.train_step()
                    losses.append(loss)
            
            # Decay exploration rate
            self.ai.epsilon = max(0.01, self.ai.epsilon * 0.995)
            
            # Progress report
            if (episode + 1) % 10 == 0:
                avg_loss = np.mean(losses[-100:]) if losses else 0.0
                win_rate_black = self.total_wins_black / self.num_episodes * 100
                win_rate_white = self.total_wins_white / self.num_episodes * 100
                draw_rate = self.total_draws / self.num_episodes * 100
                
                print(f"Episode {episode + 1}/{num_episodes} | "
                      f"Loss: {avg_loss:.4f} | "
                      f"ε: {self.ai.epsilon:.4f} | "
                      f"Black: {win_rate_black:.1f}% | "
                      f"White: {win_rate_white:.1f}% | "
                      f"Draw: {draw_rate:.1f}%")
            
            # Save model periodically
            if (episode + 1) % save_interval == 0:
                self.ai.save_model(f'othello_model_ep{episode + 1}.pth')
        
        # Save final model
        self.ai.save_model('othello_model_final.pth')
        print("✅ Training Complete!")
        print(f"📊 Final Stats - Black Wins: {self.total_wins_black} | "
              f"White Wins: {self.total_wins_white} | Draws: {self.total_draws}")


# Quick test function
if __name__ == "__main__":
    print("🎮 Modern AI Module for Othello")
    print("=" * 50)
    print("This module provides a Deep Learning AI using PyTorch")
    print("\nTo use:")
    print("1. Import: from modern_ai import ModernOthelloAI")
    print("2. Create: ai = ModernOthelloAI()")
    print("3. Get move: move = ai.choose_move(board, player, valid_moves)")
    print("\nTo train:")
    print("Run: python train_modern_ai.py")
