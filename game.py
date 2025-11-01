class Game:
    def __init__(self, board):
        self.board = board
        self.current_player = 'B'

    def switch_player(self):
        self.current_player = 'W' if self.current_player == 'B' else 'B'

    def check_game_over(self):
        # Check if no valid moves for both players
        b_moves = self.board.get_valid_moves('B')
        w_moves = self.board.get_valid_moves('W')
        # Game over if neither player has a move
        if not b_moves and not w_moves:
            return True
        # Or if board is full
        for row in self.board.grid:
            for cell in row:
                if cell is None:
                    return False
        return True

    def get_score(self):
        # Count discs for each player
        score = {'B': 0, 'W': 0}
        for row in self.board.grid:
            for cell in row:
                if cell == 'B':
                    score['B'] += 1
                elif cell == 'W':
                    score['W'] += 1
        return score

    def pass_if_needed(self):
        """If current player has no moves but the opponent does, switch and return True.

        Returns True if a pass (switch) happened, False otherwise.
        """
        cur = self.current_player
        opp = 'W' if cur == 'B' else 'B'
        if not self.board.get_valid_moves(cur) and self.board.get_valid_moves(opp):
            self.switch_player()
            return True
        return False

    def winner(self):
        """Return (winner_color, counts) or (None, counts) if tie.
        
        Winner is determined by disc count.
        """
        counts = self.get_score()
        if counts['B'] > counts['W']:
            return 'B', counts
        elif counts['W'] > counts['B']:
            return 'W', counts
        else:
            return None, counts

# (standalone duplicate functions removed)
