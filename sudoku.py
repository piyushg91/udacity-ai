import logging
from typing import Dict, List, Set


class InvalidBoardException(Exception):
    pass


class SudokuSolver(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'

    def __init__(self, starting_grid: Dict[str, str], depth:int=1):
        self.board = starting_grid
        self.logger = logging.getLogger('Main Logger ' + str(depth))
        self.depth = depth
        self.logger.info('Instantiated with depth ' + str(self.depth))
        self.left_diagonal = set()
        self.right_diagonal = set()
        self.set_diagonals()

    def set_diagonals(self):
        for i, row in enumerate(self.rows):
            box = row + self.cols[i]
            self.left_diagonal.add(box)

        reversed_cols = list(reversed(self.cols))
        for i, row in enumerate(self.rows):
            box = row + reversed_cols[i]
            self.right_diagonal.add(box)

    def pre_process(self):
        """ SHould only be called once at the start
        :return:
        """
        for box in self.board.keys():
            value = self.board[box]
            if len(value) == 1:
                self.eliminate_from_peers(value, box)

    def base_eliminate(self):
        """Eliminate values from peers using various strategies

        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
        """
        found_type1 = self.do_all_type1_elims()
        found_naked_pairs = self.apply_all_naked_pair_elims(cascade=True)
        if found_type1 or found_naked_pairs:
            self.logger.info('Redoing base elimination')
            self.base_eliminate()
        if not self.check_if_diagonals_are_uniquely_solved():
            self.output_board()
            raise InvalidBoardException('Diagonals not uniquely solved')
        if self.is_solved() and not self.check_if_board_is_valid():
            self.check_if_board_is_valid()

    def eliminate_from_peers(self, value, box, diagonal_elimination:bool=True):
        self.logger.info('Eliminating {0} for {1}'.format(value, box))
        self.board[box] = value
        self.eliminate_from_row(value, box)
        self.eliminate_from_col(value, box)
        self.eliminate_from_box(value, box)
        if diagonal_elimination:
            if box in self.left_diagonal:
                self.eliminate_from_given_peers(self.left_diagonal, value)
            if box in self.right_diagonal:
                self.eliminate_from_given_peers(self.right_diagonal, value)

    def eliminate_from_given_peers(self, peers, value_to_remove: str):
        for peer in peers:
            current_value = self.board[peer]
            if current_value.__len__() == 1:
                continue
            if value_to_remove in current_value:
                new_value = current_value.replace(value_to_remove, '')
                self.board[peer] = new_value
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
        self.logger.info("=======")
        width = 1 + max(len(self.board[s]) for s in self.get_all_box_indicies())
        horz_boundary = '  ' + '+'.join(['-' * (width * 3)] * 3)
        upper_ind = '  '
        for c in self.cols:
            sep = ' ' if c in '36' else ''
            upper_ind += c.center(width) + sep
        self.logger.info(upper_ind)
        self.logger.info('  ' + '-'*(width*9))
        for r in self.rows:
            line = r + ' '
            for c in self.cols:
                sep = '|' if c in '36' else ''
                line += self.board[r + c].center(width) + sep
            self.logger.info(line)
            if r in 'CF':
                self.logger.info(horz_boundary)
        self.logger.info("=======\n")

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
        for key in self.board:
            length = len(self.board[key])
            if length != 1:
                return False
            elif length == 0:
                raise InvalidBoardException
        return True

    def do_all_type1_elims(self):
        """
        :return:  Will return 2 if there was an elimination
        """
        a1 = self.do_type_1_elims_with_cols()
        a2 = self.do_type_1_elims_with_row()
        a3 = self.do_type_1_elims_with_box()
        return a1 or a2 or a3

    def do_type_1_elims_with_cols(self):
        found_elimination = False
        for col in self.get_cols_as_list():
            found_elimination = self.do_type_1_eliminations(col, 'col') or found_elimination
        return found_elimination

    def do_type_1_elims_with_row(self):
        found_elimination = False
        for row in self.get_rows_as_list():
            found_elimination = self.do_type_1_eliminations(row, 'row') or found_elimination
        return found_elimination

    def do_type_1_elims_with_box(self):
        found_elimination = False
        for box in self.get_boxs_as_list():
            found_elimination = self.do_type_1_eliminations(box, 'box') or found_elimination
        return found_elimination

    def do_type_1_eliminations(self, group_peer: List[str], identifier: str) -> bool:
        found_elimination = False
        count_map = {str(i): [] for i in range(1, 10)}
        for box in group_peer:
            value = self.board[box]
            if len(value) > 1:
                for pos in value:
                    count_map[pos].append(box)
        for key in count_map.keys():
            boxes_found = count_map[key]
            if count_map[key].__len__() == 1:
                box = boxes_found[0]
                self.logger.info('Type 1 elimination for {0}: {1} with value {2}'.format(identifier, box, key))
                self.eliminate_from_peers(key, box)
                found_elimination = True
        return found_elimination

    def apply_all_naked_pair_elims(self, cascade:bool=True):
        a1 = self.apply_naked_pair_elims_with_cols(cascade)
        a2 = self.apply_naked_pair_elims_with_rows(cascade)
        a3 = self.apply_naked_pair_elims_with_boxes(cascade)
        a4 = self.apply_naked_pair_with_select_peers(list(self.left_diagonal), 'left-diaganol', cascade=cascade)
        a5 = self.apply_naked_pair_with_select_peers(list(self.right_diagonal), 'left-diaganol', cascade=cascade)
        return a1 or a2 or a3 or a4 or a5

    def apply_naked_pair_elims_with_cols(self, cascade):
        found = False
        for col in self.get_cols_as_list():
            found = self.apply_naked_pair_with_select_peers(col, 'col', cascade) or found
        return found

    def apply_naked_pair_elims_with_rows(self, cascade):
        found = False
        for row in self.get_rows_as_list():
            found = self.apply_naked_pair_with_select_peers(row, 'row', cascade) or found
        return found

    def apply_naked_pair_elims_with_boxes(self, cascade):
        found = False
        for box in self.get_boxs_as_list():
            found = self.apply_naked_pair_with_select_peers(box, 'box', cascade) or found
        return found

    def apply_naked_pair_with_select_peers(self, group_peer: List[str], identifier: str, cascade: bool) -> bool:
        self.logger.info('processsing {0}: {1} for naked pairs'.format(identifier, group_peer[0]))
        found = False
        unsolved_map = {}
        unsolved_boxes = set()
        for box in group_peer:
            value = self.board[box]
            if value.__len__() > 1:
                unsolved_boxes.add(box)
                if value in unsolved_map:
                    unsolved_map[value].add(box)
                else:
                    unsolved_map[value] = {box}
        for unsolved_combination in unsolved_map:
            pair_len = len(unsolved_combination)
            pair_count = len(unsolved_map[unsolved_combination])
            if pair_count != pair_len:
                continue
            boxes_to_change = unsolved_boxes - unsolved_map[unsolved_combination]
            if boxes_to_change:
                found = True
                self.remove_numbers_from_sequence(unsolved_combination, boxes_to_change, cascade)
        return found

    def remove_numbers_from_sequence(self, to_remove: str, boxes_to_change: Set[str], cascade: bool):
        for box in boxes_to_change:
            current_value = self.board[box]
            for num in to_remove:
                current_value = current_value.replace(num, '')
            if current_value == '':
                raise InvalidBoardException
            self.board[box] = current_value
            if cascade and len(current_value) == 1:
                self.eliminate_from_peers(current_value, box)

    def solve_the_puzzle(self):
        self.pre_process()
        self.base_eliminate()
        self.output_board()
        result = self.brute_force()
        if result:
            self.logger.info('Successfully solved the puzzle')
            self.output_board()
        else:
            raise Exception('Could not solve puzzle')

    def check_if_board_is_valid(self):
        errors = []
        for row in self.get_rows_as_list():
            errors += self.check_if_peer_is_valid(row, 'row')
        for col in self.get_cols_as_list():
            errors += self.check_if_peer_is_valid(col, 'col')
        for box in self.get_boxs_as_list():
            errors += self.check_if_peer_is_valid(box, 'box')
        if errors:
            raise InvalidBoardException('\n'.join(errors))

    def check_if_peer_is_valid(self, peer: List[str], identifier: str):
        seen = set()
        errors = []
        for box in peer:
            value = self.board[box]
            if len(value) == 0:
                errors.append('{0} does not have any pos'.format(box))
            if len(value) == 1:
                if value not in seen:
                    seen.add(value)
                else:
                    errors.append('{0} with {1} is not unique'.format(identifier, box))
        return errors

    def check_if_diagonals_are_uniquely_solved(self):
        for diagonal in [self.left_diagonal, self.right_diagonal]:
            seen = set()
            diagonal = list(diagonal)
            for box in diagonal:
                value = self.board[box]
                if len(value) > 1:
                    continue
                if value in seen:
                    return False
                seen.add(value)
        return True

    def brute_force(self) -> bool:
        unsolved = []
        for box in self.get_all_box_indicies():
            value = self.board[box]
            if len(value) > 1:
                unsolved.append((box, value))
        if len(unsolved) == 0:
            return self.check_if_diagonals_are_uniquely_solved()
        unsolved.sort(key=lambda x: len(x[1]))
        for unsolved_box, unsolved_pos_values in unsolved:
            for unsolved_pos in unsolved_pos_values:
                new_grid = self.board.copy()
                new_solver = SudokuSolver(new_grid, depth=self.depth + 1)
                new_solver.output_board()
                new_solver.logger.info('Picking {0} from {1} for {2}'.format(unsolved_pos, unsolved_pos_values,
                                                                             unsolved_box))
                try:
                    new_solver.eliminate_from_peers(unsolved_pos, unsolved_box)
                    new_solver.base_eliminate()
                    output = new_solver.brute_force()
                except InvalidBoardException as e:
                    new_solver.logger.info('Invalid board found: ' + e.args[0])
                    new_solver.output_board()
                    continue
                if output:
                    self.board = new_solver.board
                    return True
        return False


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    # d = SudokuSolver.create_dict_from_str_input('..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..')
    # s = SudokuSolver(d)
    # s.output_board()
    # s.eliminate()
    # s.output_board()
    # print(s.is_solved())

    d = SudokuSolver.create_dict_from_str_input('2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3')
    s = SudokuSolver(d)
    s.solve_the_puzzle()
