from sudoku_logic import (
    count_solutions,
    create_empty_board,
    fill_board,
    generate_puzzle,
    is_safe,
    solve_board,
)


def test_is_safe_rejects_row_column_and_box_conflicts():
    board = create_empty_board()
    board[0][0] = 5

    assert is_safe(board, 0, 1, 5) is False
    assert is_safe(board, 1, 0, 5) is False
    assert is_safe(board, 1, 1, 5) is False
    assert is_safe(board, 1, 1, 4) is True


def test_fill_board_completes_an_empty_board():
    board = create_empty_board()

    assert fill_board(board) is True
    assert all(sorted(row) == list(range(1, 10)) for row in board)
    for column in range(9):
        assert sorted(board[row][column] for row in range(9)) == list(range(1, 10))


def test_fill_board_preserves_existing_clues():
    board = create_empty_board()
    board[0][0] = 5

    assert fill_board(board) is True
    assert board[0][0] == 5


def test_solve_board_returns_a_solution_without_mutating_the_puzzle():
    puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9],
    ]

    solution = solve_board(puzzle)

    assert solution is not None
    assert puzzle[0][2] == 0
    assert all(sorted(row) == list(range(1, 10)) for row in solution)


def test_generated_puzzle_has_target_clues_and_one_solution():
    puzzle, solution = generate_puzzle(clues=35)

    assert sum(cell != 0 for row in puzzle for cell in row) == 35
    assert count_solutions(puzzle) == 1
    assert puzzle != solution