from board import Board
from game import Game

# Test game flow
b = Board()
g = Game(b)

print(f"Initial turn: {g.current_player}")
print(f"Initial score: {g.get_score()}")

# Make a move for Black
moves = b.get_valid_moves('B')
print(f"Valid moves for B: {moves}")
if moves:
    m = moves[0]
    print(f"Black plays {m}")
    b.place_disc(m[0], m[1], 'B')
    print(f"Before switch: {g.current_player}")
    g.switch_player()
    print(f"After switch: {g.current_player}")
    print(f"Score after Black move: {g.get_score()}")

# Make a move for White
moves = b.get_valid_moves('W')
print(f"Valid moves for W: {moves}")
if moves:
    m = moves[0]
    print(f"White plays {m}")
    b.place_disc(m[0], m[1], 'W')
    print(f"Before switch: {g.current_player}")
    g.switch_player()
    print(f"After switch: {g.current_player}")
    print(f"Score after White move: {g.get_score()}")
