class Board:
    def __init__(self):
        from constants import BOARD_SIZE
        self.size = BOARD_SIZE
        self.grid = [[None for _ in range(self.size)] for _ in range(self.size)]
        self.init_board()

    def init_board(self):
        mid = self.size // 2
        # Standard Othello start position
        self.grid[mid - 1][mid - 1] = 'W'
        self.grid[mid][mid] = 'W'
        self.grid[mid - 1][mid] = 'B'
        self.grid[mid][mid - 1] = 'B'

    def is_valid_move(self, row, col, color):
        # Check if placing a disc here flips at least one opponent disc
        from constants import DIRECTIONS

        # Out of bounds or not empty
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.grid[row][col] is not None:
            return False

        opponent = 'W' if color == 'B' else 'B'

        for dr, dc in DIRECTIONS:
            r, c = row + dr, col + dc
            found_opponent = False
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == opponent:
                found_opponent = True
                r += dr
                c += dc
            if found_opponent and 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == color:
                return True
        return False

    def place_disc(self, row, col, color):
        # Place disc and flip opponent discs
        from constants import DIRECTIONS

        if not self.is_valid_move(row, col, color):
            return []

        self.grid[row][col] = color
        opponent = 'W' if color == 'B' else 'B'

        flipped_discs = []
        # Flip discs in all valid directions
        for dr, dc in DIRECTIONS:
            flips = []
            r, c = row + dr, col + dc
            while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == opponent:
                flips.append((r, c))
                r += dr
                c += dc
            if flips and 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == color:
                for fr, fc in flips:
                    self.grid[fr][fc] = color
                    flipped_discs.append((fr, fc))
        return flipped_discs

    def clone(self):
        """Return a deep copy of the board suitable for simulation."""
        new = Board()
        new.size = self.size
        new.grid = [list(row) for row in self.grid]
        return new

    def get_valid_moves(self, color):
        valid_moves = []
        for row in range(self.size):
            for col in range(self.size):
                if self.grid[row][col] is None and self.is_valid_move(row, col, color):
                    valid_moves.append((row, col))
        return valid_moves