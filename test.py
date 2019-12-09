from unittest import TestCase


class SudokuSolverTest(TestCase):
    def test_get_row_peers(self):
        self.assertEqual(SudokuSolver.get_row_peers('A3'), ['A1', 'A2', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9'])

    def test_get_col_peers(self):
        self.assertEqual(SudokuSolver.get_col_peers('A3'), ['B3', 'C3', 'D3', 'E3', 'F3', 'G3', 'H3', 'I3'])

    def test_get_box_peers_a3(self):
        inp = 'A3'
        correct = ['A1', 'A2', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
        self.assertEqual(SudokuSolver.get_box_peers(inp), correct)

    def test_get_box_peers_d4(self):
        inp = 'D4'
        correct = ['D5', 'D6', 'E4', 'E5', 'E6', 'F4', 'F5', 'F6']
        self.assertEqual(correct, SudokuSolver.get_box_peers(inp))



