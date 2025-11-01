import random
from constants import DIRECTIONS


def _flip_count(board, row, col, color):
    """Return number of opponent discs that would be flipped by playing (row,col)."""
    opponent = 'W' if color == 'B' else 'B'
    total = 0
    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        local = 0
        while 0 <= r < board.size and 0 <= c < board.size and board.grid[r][c] == opponent:
            local += 1
            r += dr
            c += dc
        if local > 0 and 0 <= r < board.size and 0 <= c < board.size and board.grid[r][c] == color:
            total += local
    return total


def _evaluate(board, color):
    """Heuristic evaluation from perspective of `color`.

    Weighted sum of:
    - corner occupancy (high)
    - disk difference
    - mobility (number of moves)
    """
    opponent = 'W' if color == 'B' else 'B'
    # corners
    corners = [(0, 0), (0, board.size - 1), (board.size - 1, 0), (board.size - 1, board.size - 1)]
    corner_score = 0
    for r, c in corners:
        if board.grid[r][c] == color:
            corner_score += 25
        elif board.grid[r][c] == opponent:
            corner_score -= 25

    # disk difference
    my_discs = 0
    opp_discs = 0
    for row in board.grid:
        for cell in row:
            if cell == color:
                my_discs += 1
            elif cell == opponent:
                opp_discs += 1
    disc_diff = my_discs - opp_discs

    # mobility
    my_moves = len(board.get_valid_moves(color))
    opp_moves = len(board.get_valid_moves(opponent))
    mobility = my_moves - opp_moves

    return corner_score + 2 * disc_diff + 3 * mobility


def _minimax(board, color, depth, maximizing, orig_color):
    """Depth-limited minimax without alpha-beta for simplicity (depth small).

    Returns (score, move) where move is None or (r,c)
    """
    moves = board.get_valid_moves(color)
    opponent = 'W' if color == 'B' else 'B'

    if depth == 0 or not moves:
        return _evaluate(board, orig_color), None

    best_move = None
    if maximizing:
        best_score = -10**9
        for m in moves:
            b2 = board.clone()
            b2.place_disc(m[0], m[1], color)
            sc, _ = _minimax(b2, opponent, depth - 1, False, orig_color)
            if sc > best_score:
                best_score = sc
                best_move = m
        return best_score, best_move
    else:
        best_score = 10**9
        for m in moves:
            b2 = board.clone()
            b2.place_disc(m[0], m[1], color)
            sc, _ = _minimax(b2, opponent, depth - 1, True, orig_color)
            if sc < best_score:
                best_score = sc
                best_move = m
        return best_score, best_move


def choose_move(board, color, difficulty='medium'):
    """Choose a move for color on board with difficulty: 'easy', 'medium', 'hard'.

    - easy: random valid move
    - medium: corner-first then max-flips (greedy)
    - hard: minimax depth 3 (selects best evaluated move)
    """
    moves = board.get_valid_moves(color)
    if not moves:
        return None

    if difficulty == 'easy':
        return random.choice(moves)

    if difficulty == 'medium':
        # Prefer corners
        corners = [(0, 0), (0, board.size - 1), (board.size - 1, 0), (board.size - 1, board.size - 1)]
        for c in corners:
            if c in moves:
                return c

        best = []
        best_score = -1
        for (r, c) in moves:
            sc = _flip_count(board, r, c, color)
            if sc > best_score:
                best = [(r, c)]
                best_score = sc
            elif sc == best_score:
                best.append((r, c))
        return random.choice(best)

    if difficulty == 'hard':
        # depth 3 minimax (you can increase depth at cost of CPU)
        depth = 3
        _, move = _minimax(board, color, depth, True, color)
        return move

    # fallback
    return random.choice(moves)
