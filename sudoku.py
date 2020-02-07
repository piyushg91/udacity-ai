import logging
from typing import Dict, List, Set
from sudoku_utils import SudokuUtils


class InvalidBoardException(Exception):
    pass


class UdacityException(Exception):
    pass


class SudokuSolver(object):
    peer_map = SudokuUtils.get_peers_map()

    def __init__(self, starting_grid: Dict[str, str], depth: int=1):
        self.board = starting_grid
        self.logger = logging.getLogger('Main Logger ' + str(depth))
        self.depth = depth
        self.logger.info('Instantiated with depth ' + str(self.depth))
        self.left_diagonal = set()
        self.right_diagonal = set()
        self.set_diagonals()
        print(depth)

    def set_diagonals(self):
        for i, row in enumerate(SudokuUtils.rows):
            box = row + SudokuUtils.cols[i]
            self.left_diagonal.add(box)

        reversed_cols = list(reversed(SudokuUtils.cols))
        for i, row in enumerate(SudokuUtils.rows):
            box = row + reversed_cols[i]
            self.right_diagonal.add(box)

    def eliminate_singular_values_peers(self):
        """ If we find a box that's already solved, eliminate from its peers
        :return:
        """
        for box in self.board.keys():
            value = self.board[box]
            if len(value) == 1:
                self.eliminate_from_peers(value, box)

    def get_solved_count(self):
        count = 0
        for key in self.board:
            if self.board[key].__len__() == 1:
                count += 1
        return count

    def base_eliminate(self):
        """Eliminate values from peers using various strategies

        Returns:
            Resulting Sudoku in dictionary form after eliminating values.
        """
        stalled = False
        while not stalled:
            pre_elimination_count = self.get_solved_count()
            self.eliminate_singular_values_peers()
            self.do_all_type1_elims()
            self.apply_all_naked_pair_elims(cascade=True)
            post_elimination_count = self.get_solved_count()
            stalled = pre_elimination_count == post_elimination_count
        self.check_if_board_is_solvable_for_all_peers()

    def check_if_board_is_solvable_for_all_peers(self):
        for row in SudokuUtils.all_rows:
            self.check_if_board_is_solvable(row)
        for col in SudokuUtils.all_cols:
            self.check_if_board_is_solvable(col)
        for box in SudokuUtils.all_boxes:
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
        self.eliminate_from_given_peers(self.peer_map[box], value)
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
        for col in SudokuUtils.all_cols:
            found_elimination = self.do_type_1_eliminations(col, 'col') or found_elimination
        return found_elimination

    def do_type_1_elims_with_row(self):
        found_elimination = False
        for row in SudokuUtils.all_rows:
            found_elimination = self.do_type_1_eliminations(row, 'row') or found_elimination
        return found_elimination

    def do_type_1_elims_with_box(self):
        found_elimination = False
        for box in SudokuUtils.all_boxes:
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
        for col in SudokuUtils.all_cols:
            found = self.apply_naked_pair_with_select_peers(col, 'col', cascade) or found
        return found

    def apply_naked_pair_elims_with_rows(self, cascade):
        found = False
        for row in SudokuUtils.all_rows:
            found = self.apply_naked_pair_with_select_peers(row, 'row', cascade) or found
        return found

    def apply_naked_pair_elims_with_boxes(self, cascade):
        found = False
        for box in SudokuUtils.all_boxes:
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
        self.base_eliminate()
        self.output_board()
        result = self.brute_force()
        if result:
            self.logger.info('Successfully solved the puzzle')
            self.output_board()
        else:
            raise Exception('Could not solve puzzle')

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
        unsolved_box, unsolved_pos_values = unsolved[0]
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
