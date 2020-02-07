import signal
import logging
from sudoku import SudokuSolver
from sudoku_utils import SudokuUtils
from unittest import TestCase


class SudokuSolverTest(TestCase):
    def test_get_row_peers(self):
        self.assertEqual(SudokuUtils.get_row_peers('A3'), ['A1', 'A2', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9'])

    def test_get_col_peers(self):
        self.assertEqual(SudokuUtils.get_col_peers('A3'), ['B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'I3'])

    def test_get_box_peers_a3(self):
        inp = 'A3'
        correct = ['A1', 'A2', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        self.assertEqual(SudokuUtils.get_box_peers(inp), correct)

    def test_get_box_peers_d4(self):
        inp = 'D4'
        correct = ['D5', 'D6', 'E4', 'E5', 'E6', 'F4', 'F5', 'F6']
        self.assertEqual(correct, SudokuUtils.get_box_peers(inp))

class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)


class SolverTest(TestCase):
    def run_solver(self, input_str: str):
        logging.basicConfig(level=logging.INFO,format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        with Timeout(seconds=5):
            d = SudokuSolver.create_dict_from_str_input(input_str)
            solver = SudokuSolver(d)
            solver.solve_the_puzzle()

    def test_one(self):
        input_str = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
        self.run_solver(input_str)

    def test_two(self):
        input_str = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
        self.run_solver(input_str)

    def test_three(self):
        input_str = '9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................'
        self.run_solver(input_str)

    def test_four(self):
        input_str = '...7.9....85...31.2......7...........1..7.6......8...7.7.........3......85.......'
        self.run_solver(input_str)

    def test_five(self):
        input_str = '6.5.3.4.....59.......16...5........1...3......7.6859......53....5............6.5.'
        self.run_solver(input_str)

    def test_six(self):
        input_str = '...7.2.4.........7217....9.6.......3.2..48..........1..5..........3.......6......'
        self.run_solver(input_str)

