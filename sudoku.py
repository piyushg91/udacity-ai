from typing import Dict
from unittest import TestCase


class SudokuSolver(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'

    def __init__(self, starting_grid):
        self.starting_grid = starting_grid

    def eliminate(self):
        """Eliminate values from peers of each box with a single value.

        Go through all the boxes, and whenever there is a box with a single value,
        eliminate this value from the set of values of all its peers.

        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
        """
        for box in self.starting_grid.keys():
            value = self.starting_grid[box]
            if len(value) == 1:
                self.eliminate_from_peers(value, box)

    def eliminate_from_peers(self, value, box):
        self.eliminate_from_row(value, box)
        self.eliminate_from_col(value, box)
        self.eliminate_from_box(value, box)

    def eliminate_from_given_peers(self, peers, value_to_remove: str):
        for peer in peers:
            current_value = self.starting_grid[peer]
            if current_value.__len__() == 1:
                continue
            if value_to_remove in current_value:
                new_value = current_value.replace(value_to_remove, '')
                self.starting_grid[peer] = new_value

    def eliminate_from_row(self, value_to_remove: str, target_box: str):
        row_peers = self.get_row_peers(target_box)
        self.eliminate_from_given_peers(row_peers, value_to_remove)

    def eliminate_from_col(self, value_to_remove: str, target_box: str):
        cols_peers = self.get_col_peers(target_box)
        self.eliminate_from_given_peers(cols_peers, value_to_remove)

    def eliminate_from_box(self, value_to_remove: str, target_box: str):
        box_peers = self.get_box_peers(target_box)
        self.eliminate_from_given_peers(box_peers, value_to_remove)

    @classmethod
    def get_col_peers(cls, target_box: str):
        target_row, target_col = target_box[0], target_box[1]
        peers = [row + target_col for row in cls.rows if row != target_row]
        return peers

    @classmethod
    def get_row_peers(cls, target_box: str):
        target_row, target_col = target_box[0], target_box[1]
        peers = [target_row + col for col in cls.cols if col != target_col]
        return peers

    @classmethod
    def get_box_peers(cls, target_box: str):
        row, col = target_box[0], target_box[1]
        row_index = cls.rows.find(row)
        col_index = cls.cols.find(col)

        start_row = int(int(row_index)/3) * 3
        end_row = start_row + 3 # non inclusive

        start_col = int(int(col_index)/3) * 3
        end_col = start_col + 3

        peers = []
        for row in range(start_row, end_row):
            actual_row = cls.rows[row]
            for col in range(start_col, end_col):
                actual_col = cls.cols[col]
                peer = actual_row + actual_col
                if peer == target_box:
                    continue
                peers.append(peer)
        return peers

    def output_board(self):
        width = 1 + max(len(self.starting_grid[s]) for s in boxes)
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in self.rows:
            print(''.join(self.starting_grid[r + c].center(width) + ('|' if c in '36' else '')
                          for c in self.cols))
            if r in 'CF':
                print(line)


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



