from board import Board
from game import Game
from ai import choose_move

b=Board()
g=Game(b)
print('initial moves B', b.get_valid_moves('B'))
# play first valid move for B
move = b.get_valid_moves('B')[0]
print('play B', move)
b.place_disc(move[0], move[1], 'B')
g.switch_player()
print('current', g.current_player)
print('valid for W', b.get_valid_moves('W'))
ai_move = choose_move(b,'W','medium')
print('ai_move', ai_move)
if ai_move:
    b.place_disc(ai_move[0], ai_move[1], 'W')
    g.switch_player()
print('after ai current', g.current_player)
print('score', g.get_score())
