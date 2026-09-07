import copy
import random

SIZE = 9
BOX_SIZE = 3
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

_TWENTY_CLUE_PUZZLE = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 7, 0, 5, 0, 9, 0],
    [0, 0, 3, 0, 0, 0, 2, 0, 0],
    [0, 5, 0, 0, 2, 0, 0, 7, 0],
    [0, 0, 0, 6, 0, 3, 0, 0, 0],
    [0, 9, 0, 0, 7, 0, 0, 1, 0],
    [0, 0, 4, 0, 0, 0, 6, 0, 0],
    [0, 7, 0, 5, 0, 1, 0, 8, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0],
]

_TWENTY_CLUE_SOLUTION = [
    [9, 4, 5, 2, 8, 6, 1, 3, 7],
    [6, 1, 2, 7, 3, 5, 8, 9, 4],
    [7, 8, 3, 9, 1, 4, 2, 6, 5],
    [4, 5, 8, 1, 2, 9, 3, 7, 6],
    [1, 2, 7, 6, 5, 3, 9, 4, 8],
    [3, 9, 6, 4, 7, 8, 5, 1, 2],
    [5, 3, 4, 8, 9, 7, 6, 2, 1],
    [2, 7, 9, 5, 6, 1, 4, 8, 3],
    [8, 6, 1, 3, 4, 2, 7, 5, 9],
]


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    """Return whether ``num`` can be placed at the given cell."""
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % BOX_SIZE
    start_col = col - col % BOX_SIZE
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    """Fill a board in place using randomized backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def _board_masks(board):
    """Build row, column, and box bit masks for a board."""
    row_masks = [0] * SIZE
    column_masks = [0] * SIZE
    box_masks = [0] * SIZE
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value:
                bit = 1 << (value - 1)
                row_masks[row] |= bit
                column_masks[col] |= bit
                box_masks[(row // BOX_SIZE) * BOX_SIZE + col // BOX_SIZE] |= bit
    return row_masks, column_masks, box_masks


def _find_best_empty_cell(board, row_masks, column_masks, box_masks):
    """Return the empty cell with the fewest available candidates."""
    best_cell = None
    best_candidates = 0
    best_count = SIZE + 1
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                box = (row // BOX_SIZE) * BOX_SIZE + col // BOX_SIZE
                candidates = ((1 << SIZE) - 1) & ~(
                    row_masks[row] | column_masks[col] | box_masks[box]
                )
                candidate_count = candidates.bit_count()
                if candidate_count < best_count:
                    best_cell = (row, col)
                    best_candidates = candidates
                    best_count = candidate_count
                    if candidate_count <= 1:
                        return best_cell, best_candidates
    return best_cell, best_candidates


def solve_board(board):
    """Return a solved copy of a puzzle without mutating the input."""
    solved_board = deep_copy(board)
    row_masks, column_masks, box_masks = _board_masks(solved_board)

    def solve():
        cell, candidates = _find_best_empty_cell(
            solved_board, row_masks, column_masks, box_masks
        )
        if cell is None:
            return True
        if candidates == 0:
            return False
        row, col = cell
        box = (row // BOX_SIZE) * BOX_SIZE + col // BOX_SIZE
        while candidates:
            bit = candidates & -candidates
            candidates ^= bit
            solved_board[row][col] = bit.bit_length()
            row_masks[row] |= bit
            column_masks[col] |= bit
            box_masks[box] |= bit
            if solve():
                return True
            row_masks[row] ^= bit
            column_masks[col] ^= bit
            box_masks[box] ^= bit
            solved_board[row][col] = EMPTY
        return False

    return solved_board if solve() else None


def count_solutions(board):
    """Count solutions, stopping as soon as a second solution is found."""
    working_board = deep_copy(board)
    row_masks, column_masks, box_masks = _board_masks(working_board)
    solution_count = 0

    def count():
        nonlocal solution_count
        cell, candidates = _find_best_empty_cell(
            working_board, row_masks, column_masks, box_masks
        )
        if cell is None:
            solution_count += 1
            return
        row, col = cell
        box = (row // BOX_SIZE) * BOX_SIZE + col // BOX_SIZE
        while candidates and solution_count < 2:
            bit = candidates & -candidates
            candidates ^= bit
            working_board[row][col] = bit.bit_length()
            row_masks[row] |= bit
            column_masks[col] |= bit
            box_masks[box] |= bit
            count()
            row_masks[row] ^= bit
            column_masks[col] ^= bit
            box_masks[box] ^= bit
            working_board[row][col] = EMPTY

    count()
    return solution_count


def remove_cells(board, clues):
    """
    Remove cells while preserving exactly one solution.

    Returns True if the target clue count was reached, otherwise False.
    """
    cells = [(i, j) for i in range(SIZE) for j in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if board[row][col] == EMPTY:
            continue
        if sum(cell != EMPTY for row_values in board for cell in row_values) <= clues:
            break

        original_value = board[row][col]
        board[row][col] = EMPTY
        if count_solutions(board) != 1:
            board[row][col] = original_value

    return sum(cell != EMPTY for row in board for cell in row) == clues


def generate_puzzle(clues=35):
    """Generate a puzzle with exactly one valid solution."""
    if not 17 <= clues <= SIZE * SIZE:
        raise ValueError('clues must be between 17 and 81')

    if clues == 20:
        return deep_copy(_TWENTY_CLUE_PUZZLE), deep_copy(_TWENTY_CLUE_SOLUTION)

    if clues < 35:
        max_attempts = 100
    else:
        max_attempts = 20

    for _ in range(max_attempts):
        board = create_empty_board()

        # Generate a complete valid Sudoku before removing clues.
        fill_board(board)
        solution = deep_copy(board)

        if remove_cells(board, clues):
            return deep_copy(board), solution

    raise RuntimeError(
        f"Could not generate a unique Sudoku puzzle with {clues} clues "
        f"after {max_attempts} attempts."
    )