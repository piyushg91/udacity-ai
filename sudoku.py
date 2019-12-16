import logging
from typing import Dict, List, Set
from sudoku_utils import SudokuUtils


class InvalidBoardException(Exception):
    pass


class SudokuSolver(object):
    def __init__(self, starting_grid: Dict[str, str], depth:int=1):
        self.board = starting_grid
        self.logger = logging.getLogger('Main Logger ' + str(depth))
        self.depth = depth
        self.logger.info('Instantiated with depth ' + str(self.depth))
        self.left_diagonal = set()
        self.right_diagonal = set()
        self.set_diagonals()

    def set_diagonals(self):
        for i, row in enumerate(SudokuUtils.rows):
            box = row + SudokuUtils.cols[i]
            self.left_diagonal.add(box)

        reversed_cols = list(reversed(SudokuUtils.cols))
        for i, row in enumerate(SudokuUtils.rows):
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
        self.check_if_board_is_solvable_for_all_peers()

    def check_if_board_is_solvable_for_all_peers(self):
        for row in SudokuUtils.get_rows_as_list():
            self.check_if_board_is_solvable(row)
        for col in SudokuUtils.get_cols_as_list():
            self.check_if_board_is_solvable(col)
        for box in SudokuUtils.get_boxs_as_list():
            self.check_if_board_is_solvable(box)
        self.check_if_board_is_solvable(list(self.left_diagonal))
        self.check_if_board_is_solvable(list(self.right_diagonal))

    def check_if_board_is_solvable(self, group_peers: List[str]):
        status = {str(i): 0 for i in range(1, 10)}
        for peer in group_peers:
            value = self.board[peer]
            if len(value) == 1 and status[value] > 0:
                raise InvalidBoardException('Board unsolvable due to ' + peer)
            elif len(value) > 1:
                for v in value:
                    status[v] += 1
                continue
            status[value] += 1
        for i in status:
            if status[i] == 0:
                raise InvalidBoardException('Board no longer solvable')
        return

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
        row_peers = SudokuUtils.get_row_peers(target_box)
        self.eliminate_from_given_peers(row_peers, value_to_remove)

    def eliminate_from_col(self, value_to_remove: str, target_box: str):
        cols_peers = SudokuUtils.get_col_peers(target_box)
        self.eliminate_from_given_peers(cols_peers, value_to_remove)

    def eliminate_from_box(self, value_to_remove: str, target_box: str):
        box_peers = SudokuUtils.get_box_peers(target_box)
        self.eliminate_from_given_peers(box_peers, value_to_remove)

    def output_board(self):
        self.logger.info("=======")
        width = 1 + max(len(self.board[s]) for s in SudokuUtils.get_all_box_indicies())
        horz_boundary = '  ' + '+'.join(['-' * (width * 3)] * 3)
        upper_ind = '  '
        for c in SudokuUtils.cols:
            sep = ' ' if c in '36' else ''
            upper_ind += c.center(width) + sep
        self.logger.info(upper_ind)
        self.logger.info('  ' + '-'*(width*9))
        for r in SudokuUtils.rows:
            line = r + ' '
            for c in SudokuUtils.cols:
                sep = '|' if c in '36' else ''
                line += self.board[r + c].center(width) + sep
            self.logger.info(line)
            if r in 'CF':
                self.logger.info(horz_boundary)
        self.logger.info("=======\n")

    @classmethod
    def create_dict_from_str_input(cls, str_input: str):
        answer = {}
        for i, loc in enumerate(SudokuUtils.get_all_box_indicies()):
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
        return True

    def do_all_type1_elims(self):
        """
        :return:  Will return 2 if there was an elimination
        """
        a1 = self.do_type_1_elims_with_cols()
        a2 = self.do_type_1_elims_with_row()
        a3 = self.do_type_1_elims_with_box()
        a4 = self.do_type_1_elims_with_diags()
        return a1 or a2 or a3 or a4

    def do_type_1_elims_with_cols(self):
        found_elimination = False
        for col in SudokuUtils.get_cols_as_list():
            found_elimination = self.do_type_1_eliminations(col, 'col') or found_elimination
        return found_elimination

    def do_type_1_elims_with_row(self):
        found_elimination = False
        for row in SudokuUtils.get_rows_as_list():
            found_elimination = self.do_type_1_eliminations(row, 'row') or found_elimination
        return found_elimination

    def do_type_1_elims_with_box(self):
        found_elimination = False
        for box in SudokuUtils.get_boxs_as_list():
            found_elimination = self.do_type_1_eliminations(box, 'box') or found_elimination
        return found_elimination

    def do_type_1_elims_with_diags(self):
        found_elimination = False
        found_elimination = self.do_type_1_eliminations(list(self.left_diagonal), 'left-diag')or found_elimination
        found_elimination = self.do_type_1_eliminations(list(self.right_diagonal), 'right-diag')or found_elimination
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
        for col in SudokuUtils.get_cols_as_list():
            found = self.apply_naked_pair_with_select_peers(col, 'col', cascade) or found
        return found

    def apply_naked_pair_elims_with_rows(self, cascade):
        found = False
        for row in SudokuUtils.get_rows_as_list():
            found = self.apply_naked_pair_with_select_peers(row, 'row', cascade) or found
        return found

    def apply_naked_pair_elims_with_boxes(self, cascade):
        found = False
        for box in SudokuUtils.get_boxs_as_list():
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
            if pair_count > pair_len:
                raise InvalidBoardException('Pairs {0} found to have occurred {1} times with {2}'.format(unsolved_combination, pair_count, identifier))
            if pair_count != pair_len:
                continue
            boxes_to_change = unsolved_boxes - unsolved_map[unsolved_combination]
            if boxes_to_change:
                found = self.remove_numbers_from_sequence(unsolved_combination, boxes_to_change, cascade)
        return found

    def remove_numbers_from_sequence(self, to_remove: str, boxes_to_change: Set[str], cascade: bool):
        found = False
        for box in boxes_to_change:
            current_value = self.board[box]
            for num in to_remove:
                current_value = current_value.replace(num, '')
            if current_value == '':
                raise InvalidBoardException('{0} is blank'.format(box))
            self.board[box] = current_value
            if cascade and len(current_value) == 1:
                self.eliminate_from_peers(current_value, box)
                found = True
        return found

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

    def solve_puzzle_2(self):
        self.pre_process()
        self.base_eliminate()
        self.output_board()
        unsolved_diagonals = []
        for box in SudokuUtils.get_all_box_indicies():
            if box in self.left_diagonal or box in self.right_diagonal:
                value = self.board[box]
                if len(value) > 1:
                    unsolved_diagonals.append(box)
        unsolved_diagonals.sort(key=lambda x: len(self.board[x]))
        for i in self.yield_board_with_solved_diagonals(unsolved_diagonals, 0):
            self.logger.info('Found valid board')
            i.output_board()

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
        """ Check if its even possible to solve the diagonal as well if they are unique
        :return:
        """
        for diagonal in [self.left_diagonal, self.right_diagonal]:
            status = {str(i): 0 for i in range(1, 10)}
            diagonal = list(diagonal)
            for box in diagonal:
                value = self.board[box]
                if len(value) == 1 and status[value] > 0:
                    return False
                elif len(value) > 1:
                    for v in value:
                        status[v] += 1
                    continue
                status[value] += 1
            for i in status:
                if status[i] == 0:
                    raise InvalidBoardException('Board is no longer solvable')
        return True

    def yield_board_with_solved_diagonals(self, unsolved_diagonals: List[str], start_index):
        for i in range(start_index, len(unsolved_diagonals)):
            unsolved_box = unsolved_diagonals[i]
            unsolved_pos_values = self.board[unsolved_box]
            if unsolved_pos_values.__len__() == 1:
                self.logger.info('{0} is already solved'.format(unsolved_box))
                continue
            for unsolved_pos in unsolved_pos_values:
                new_board = self.board.copy()
                new_solver = SudokuSolver(new_board, depth=self.depth + 1)
                new_solver.output_board()
                new_solver.logger.info('Picking {0} from {1} for {2}'.format(unsolved_pos, unsolved_pos_values,
                                                                             unsolved_box))
                try:
                    new_solver.eliminate_from_peers(unsolved_pos, unsolved_box)
                    new_solver.base_eliminate()
                    new_solver.output_board()
                    new_index = start_index + 1
                    for correct_board in new_solver.yield_board_with_solved_diagonals(unsolved_diagonals, new_index):
                        yield correct_board
                except InvalidBoardException as e:
                    new_solver.logger.info('Invalid board found: ' + e.args[0])
                    new_solver.output_board()
                    continue

    def brute_force(self) -> bool:
        unsolved = []
        for box in SudokuUtils.get_all_box_indicies():
            value = self.board[box]
            if len(value) > 1:
                unsolved.append((box, value))
        if len(unsolved) == 0:
            return self.check_if_diagonals_are_uniquely_solved()
        unsolved.sort(key=lambda x: (x[0] not in self.left_diagonal and x[0] not in self.right_diagonal, len(x[1])))
        for unsolved_box, unsolved_pos_values in unsolved:
            for unsolved_pos in unsolved_pos_values:
                new_grid = self.board.copy()
                new_solver = SudokuSolver(new_grid, depth=self.depth + 1)
                new_solver.output_board()
                if new_solver.depth == 11 and unsolved_pos == '7' and unsolved_pos_values == '47' and unsolved_box == 'G8':
                    print('')
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

    # d = SudokuSolver.create_dict_from_str_input('2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3')
    # d = {'E6': '124789', 'H7': '1234567', 'A7': '2357', 'D9': '124569', 'D1': '146', 'C4': '13589', 'H8': '1257', 'H3': '68', 'D5': '12345689', 'B5': '7', 'G4': '6', 'I9': '125678', 'A8': '8', 'B1': '8', 'A2': '6', 'F2': '124', 'G3': '2', 'B9': '129', 'D4': '1258', 'F5': '12456', 'E5': '168', 'G7': '157', 'B3': '5', 'H9': '12345678', 'F7': '8', 'I1': '17', 'G1': '3', 'H4': '1234578', 'B4': '129', 'E1': '5', 'I5': '1234589', 'G5': '14589', 'H2': '9', 'A3': '1', 'B2': '3', 'E8': '1279', 'I3': '68', 'B6': '6', 'A4': '2345', 'C7': '135', 'I2': '145', 'C3': '4', 'E3': '3', 'B8': '4', 'H6': '1234578', 'D2': '1248', 'H1': '147', 'C1': '2', 'A9': '357', 'E7': '124679', 'C6': '13589', 'F3': '9', 'B7': '129', 'I6': '12345789', 'G6': '145789', 'F4': '157', 'G8': '1579', 'A1': '9', 'E4': '124789', 'F8': '3', 'F1': '146', 'A6': '2345', 'I4': '12345789', 'A5': '2345', 'E2': '1248', 'I8': '12579', 'E9': '124679', 'I7': '12345679', 'G9': '145789', 'D8': '1259', 'C8': '6', 'F6': '1257', 'D7': '124569', 'C2': '7', 'H5': '123458', 'C5': '13589', 'G2': '145', 'D6': '1358', 'F9': '124567', 'C9': '1359', 'D3': '7'}
    # d = SudokuSolver.create_dict_from_str_input('9.1....8.8.5.7..4.2.4....6...7......5..............83.3..6......9................')
    # d = SudokuSolver.create_dict_from_str_input('...7.9....85...31.2......7...........1..7.6......8...7.7.........3......85.......')
    d = SudokuSolver.create_dict_from_str_input('6.5.3.4.....59.......16...5........1...3......7.6859......53....5............6.5.')
    s = SudokuSolver(d)
    s.output_board()
    s.solve_puzzle_2()
