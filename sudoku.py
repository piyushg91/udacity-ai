import logging
from typing import Dict, List, Set, Optional
from sudoku_utils import SudokuUtils


class InvalidBoardException(Exception):
    pass


class UdacityException(Exception):
    pass


class SudokuSolver(object):
    peer_map = SudokuUtils.get_peers_map()

    def __init__(self, starting_grid: Dict[str, str], units: Optional[Dict]=None, depth:int=1):
        self.board = starting_grid
        self.logger = logging.getLogger('Main Logger ' + str(depth))
        self.depth = depth
        self.logger.info('Instantiated with depth ' + str(self.depth))
        if not units:
            self.units = SudokuUtils.get_all_units()
        else:
            self.units = units

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
            self.apply_all_naked_pair_elims()
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
        self.check_if_board_is_solvable(list(SudokuUtils.left_diagonal))
        self.check_if_board_is_solvable(list(SudokuUtils.right_diagonal))

    def check_if_board_is_solvable(self, group_peers: List[str]):
        status = {str(i): 0 for i in range(1, 10)}
        for peer in group_peers:
            value = self.board[peer]
            if len(value) == 1 and status[value] > 0:
                self.output_board()
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

    def eliminate_from_peers(self, value, box):
        self.logger.info('Eliminating {0} for {1}'.format(value, box))
        self.board[box] = value
        self.eliminate_from_given_peers(self.peer_map[box], value)

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

    def do_all_type1_elims(self):
        """
        """
        for identifier in self.units:
            units = self.units[identifier]
            for unit in units:
                self.do_type_1_eliminations(unit, identifier)

    def do_type_1_eliminations(self, group_peer: List[str], identifier: str):
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

    def apply_all_naked_pair_elims(self):
        for identifier in self.units:
            units = self.units[identifier]
            for unit in units:
                self.apply_naked_pair_with_select_peers(unit, identifier)

    def apply_naked_pair_with_select_peers(self, group_peer: List[str], identifier: str):
        self.logger.info('processsing {0}: {1} for naked pairs'.format(identifier, group_peer[0]))
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
                self.remove_numbers_from_sequence(unsolved_combination, boxes_to_change)

    def remove_numbers_from_sequence(self, to_remove: str, boxes_to_change: Set[str]):
        for box in boxes_to_change:
            current_value = self.board[box]
            for num in to_remove:
                current_value = current_value.replace(num, '')
            if current_value == '':
                raise InvalidBoardException('{0} is blank'.format(box))
            self.board[box] = current_value

    def solve_the_puzzle(self):
        self.base_eliminate()
        self.output_board()
        result = self.brute_force()
        if result:
            self.logger.info('Successfully solved the puzzle')
            self.output_board()
        else:
            raise Exception('Could not solve puzzle')

    def brute_force(self) -> bool:
        unsolved = []
        for box in SudokuUtils.get_all_box_indicies():
            value = self.board[box]
            if len(value) > 1:
                unsolved.append((box, value))
        unsolved.sort(key=lambda x: (x[0] not in SudokuUtils.left_diagonal and x[0] not in SudokuUtils.right_diagonal, len(x[1])))
        if not unsolved:
            return True
        unsolved_box, unsolved_pos_values = unsolved[0]
        for unsolved_pos in unsolved_pos_values:
            new_grid = self.board.copy()
            new_solver = SudokuSolver(new_grid, depth=self.depth + 1, units=self.units)
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
