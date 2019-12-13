import logging
from typing import Dict, List


class SudokuSolver(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'

    def __init__(self, starting_grid):
        self.starting_grid = starting_grid
        self.logger = logging.getLogger('Main Logger')

    def eliminate(self, check_for_singular_values:bool = True):
        """Eliminate values from peers using various strategies

        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
        """
        if check_for_singular_values:
            for box in self.starting_grid.keys():
                value = self.starting_grid[box]
                if len(value) == 1:
                    self.eliminate_from_peers(value, box)
        self.do_type_1_elims_with_cols()
        self.do_type_1_elims_with_row()
        self.do_type_1_elims_with_box()

    def eliminate_from_peers(self, value, box):
        self.logger.info('Elimating {0} for {1}'.format(value, box))
        self.starting_grid[box] = value
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
                if new_value.__len__() == 1:
                    self.eliminate_from_peers(new_value, peer)

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
    def get_rows_as_list(cls):
        for row in cls.rows:
            target = row + '1'
            row_peers = cls.get_row_peers(target)
            yield [target] + row_peers

    @classmethod
    def get_cols_as_list(cls):
        for col in cls.cols:
            target = 'A' + col
            col_peers = cls.get_col_peers(target)
            yield [target] + col_peers

    @classmethod
    def get_boxs_as_list(cls):
        starting = ['A1', 'A4', 'A7', 'D1', 'D4', 'D7', 'G1', 'G4', 'G7']
        for box_target in starting:
            peers = cls.get_box_peers(box_target)
            yield [box_target] + peers

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

    @classmethod
    def get_all_box_indicies(cls):
        return [row + col for row in cls.rows for col in cls.cols]

    def output_board(self):
        print("=======")
        width = 1 + max(len(self.starting_grid[s]) for s in self.get_all_box_indicies())
        line = '+'.join(['-' * (width * 3)] * 3)
        for r in self.rows:
            print(''.join(self.starting_grid[r + c].center(width) + ('|' if c in '36' else '')
                          for c in self.cols))
            if r in 'CF':
                print(line)
        print("=======\n")

    @classmethod
    def create_dict_from_str_input(cls, str_input: str):
        answer = {}
        for i, loc in enumerate(cls.get_all_box_indicies()):
            value = str_input[i]
            if value == '.':
                answer[loc] = '123456789'
            else:
                answer[loc] = value
        return answer

    def is_solved(self):
        for key in self.starting_grid:
            if self.starting_grid[key].__len__() != 1:
                return False
        return True

    def do_type_1_elims_with_cols(self):
        for col in self.get_cols_as_list():
            self.do_type_1_eliminations(col, 'col')

    def do_type_1_elims_with_row(self):
        for row in self.get_rows_as_list():
            self.do_type_1_eliminations(row, 'row')

    def do_type_1_elims_with_box(self):
        for box in self.get_boxs_as_list():
            self.do_type_1_eliminations(box, 'box')

    def do_type_1_eliminations(self, group_peer: List[str], identifier: str):
        """
        :param group_peer:
        :param identifier:
        :return:
        """
        count_map = {str(i): [] for i in range(1, 10)}
        for box in group_peer:
            value = self.starting_grid[box]
            if len(value) > 1:
                for pos in value:
                    count_map[pos].append(box)
        for key in count_map.keys():
            boxes_found = count_map[key]
            if count_map[key].__len__() == 1:
                box = boxes_found[0]
                self.logger.info('Type 1 elimination for {0}: {1} with value {2}'.format(identifier, box, key))
                self.eliminate_from_peers(key, box)

    def do_brute_force(self):
        result = self.brute_force()
        if result:
            self.logger.info('Successfully solved the puzzle')
        else:
            raise Exception('Could not solve puzzle')
        pass

    def brute_force(self):
        pass



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # d = SudokuSolver.create_dict_from_str_input('..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..')
    # s = SudokuSolver(d)
    # s.output_board()
    # s.eliminate()
    # s.output_board()
    # print(s.is_solved())

    d = SudokuSolver.create_dict_from_str_input('4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......')
    s = SudokuSolver(d)
    s.solve_the_puzzle()
