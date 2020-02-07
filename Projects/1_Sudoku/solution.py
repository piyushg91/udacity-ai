import logging
from typing import Dict, Set, Tuple, List


rows = 'ABCDEFGHI'
cols = '123456789'
reversed_cols = list(reversed(cols))

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a + b for a in A for b in B]



class SudokuUtils(object):
    rows = 'ABCDEFGHI'
    cols = '123456789'
    all_rows = [cross(r, cols) for r in rows]
    all_cols = [cross(rows, c) for c in cols]
    all_boxes = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
    left_diagonal = {row + cols[i]for i, row in enumerate(rows)}
    right_diagonal = {row + reversed_cols[i] for i, row in enumerate(rows)}

    @classmethod
    def get_all_units(cls):
        units = {
            'row': cls.all_rows,
            'col': cls.all_cols,
            'boxes': cls.all_boxes,
            'diags': [list(cls.left_diagonal), list(cls.right_diagonal)]
        }
        return units

    @classmethod
    def get_all_units_without_diags(cls):
        units = {
            'row': cls.all_rows,
            'col': cls.all_cols,
            'boxes': cls.all_boxes,
        }
        return units

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

    @classmethod
    def get_all_box_indicies(cls):
        return [row + col for row in cls.rows for col in cls.cols]

    @classmethod
    def get_peers_map(cls) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        global_peers, peers_without_diags = {}, {}
        for box in cls.get_all_box_indicies():
            row = set(cls.get_row_peers(box))
            col = set(cls.get_col_peers(box))
            box_peers = set(cls.get_box_peers(box))
            all_peers = row.union(col).union(box_peers)
            peers_without_diags[box] = all_peers

            if box in cls.left_diagonal:
                all_peers = all_peers.union(cls.left_diagonal)
            if box in cls.right_diagonal:
                all_peers = all_peers.union(cls.right_diagonal)
            global_peers[box] = all_peers
        return global_peers, peers_without_diags
class InvalidBoardException(Exception):
    pass


class SudokuSolver(object):
    peer_map, peer_map_without_diags = SudokuUtils.get_peers_map()
    units = SudokuUtils.get_all_units()
    units_without_diag = SudokuUtils.get_all_units_without_diags()

    def __init__(self, starting_grid: Dict[str, str], diagonal_enabled: bool, depth:int=1):
        self.board = starting_grid
        self.logger = logging.getLogger('Main Logger ' + str(depth))
        self.depth = depth
        self.logger.info('Instantiated with depth ' + str(self.depth))
        self.diagonal_enabled = diagonal_enabled
        if diagonal_enabled:
            self.selected_peer_map = self.peer_map
            self.selected_units = self.units
        else:
            self.selected_peer_map = self.peer_map_without_diags
            self.selected_units = self.units_without_diag

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
            # Do eliminations
            for identifier in self.selected_units:
                units = self.selected_units[identifier]
                for unit in units:
                    self.do_type_1_eliminations(unit, identifier)
                    self.apply_naked_pair_with_select_peers(unit, identifier)
            post_elimination_count = self.get_solved_count()
            stalled = pre_elimination_count == post_elimination_count
        self.check_if_board_is_solvable_for_all_peers()

    def check_if_board_is_solvable_for_all_peers(self):
        for identifier in self.selected_units:
            for unit in self.selected_units[identifier]:
                self.check_if_board_is_solvable(unit)

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
        self.eliminate_from_given_peers(self.selected_peer_map[box], value)

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
        unsolved.sort(key=lambda x: len(x[1]))
        if not unsolved:
            return True
        unsolved_box, unsolved_pos_values = unsolved[0]
        for unsolved_pos in unsolved_pos_values:
            new_grid = self.board.copy()
            new_solver = SudokuSolver(new_grid, self.diagonal_enabled, depth=self.depth + 1)
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


def naked_twins(dict_input):
    solver = SudokuSolver(dict_input, diagonal_enabled=True)
    for identifier in solver.selected_units:
        units = solver.selected_units[identifier]
        for unit in units:
            solver.apply_naked_pair_with_select_peers(unit, identifier)
    return solver.board


def solve(raw_input):
    grid = SudokuSolver.create_dict_from_str_input(raw_input)
    solver = SudokuSolver(grid, diagonal_enabled=True)
    solver.solve_the_puzzle()
    return solver.board
