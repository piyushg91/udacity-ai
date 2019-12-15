from sudoku import SudokuSolver


def naked_twins(input_grid):
    solver = SudokuSolver(input_grid)
    solver.apply_all_naked_pair_elims(cascade=False)
    return solver.board


def solve(input_grid: str):
    grid = SudokuSolver.create_dict_from_str_input(input_grid)
    solver = SudokuSolver(grid)
    solver.solve_the_puzzle()
    return solver.board
