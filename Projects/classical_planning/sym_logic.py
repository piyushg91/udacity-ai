import itertools
from typing import Tuple


class SymLogicParser(object):
    def __init__(self):
        self.syms = ['p', 'q']
        self.index_order = {'p': 0, 'q': 1}
        possibilities = [True, False]
        self.pos = set(itertools.product(possibilities, repeat=len(self.syms)))

    @staticmethod
    def determine_first_and_second_input(statement: str):
        found_first, found_operator = False, False
        first, operator, second = '', '', ''
        skip_counter = 0
        paranthes_left = 0
        for i, letter in enumerate(statement):
            if letter == ' ':
                continue
            if skip_counter > 0:
                skip_counter -= 1
                continue
            if found_operator:
                second = statement[i:]
                break
            elif letter == '(':
                paranthes_left += 1
            elif letter == ')':
                paranthes_left -= 1
                # Have we reached the end?
                if paranthes_left == 0:
                    if not found_first:
                        found_first = True
                        first = statement[:i]
                    else:
                        raise Exception('SHould not happen')
            elif paranthes_left > 0:
                continue
            elif letter in {'^', 'V', '<', '='} and not found_operator:
                if not found_first:
                    found_first = True
                    first = statement[:i]
                found_operator = True
                if letter == '<':
                    skip_counter = 2
                    operator = '<=>'
                elif letter == '=':
                    skip_counter = 1
                    operator = '=>'
                else:
                    operator = letter
        first = first.rstrip().lstrip()
        second = second.rstrip().rstrip()
        if second[0] == '(' and second[-1] == ')':
            second = second[1:-1]
        return first, operator, second

    def create_column(self, statement: str):
        column = {}
        for p_bool, q_bool in self.pos:
            key = (p_bool, q_bool)
            if statement.find('~') != -1:
                to_nullify = statement[1]
                index_order = self.index_order[to_nullify]
                column[key] = not key[index_order]
            elif statement.find('^') != -1:
                column[key] = p_bool and q_bool
            elif statement.find('V') != -1:
                column[key] = p_bool or q_bool
            elif statement.find(' =>') != -1:
                column[key] = self.get_implies_value(statement, key)
            elif statement.find('<=>') != -1:
                column[key] = p_bool == q_bool
            else:
                raise Exception('Do not know what to do with ' + statement)
        return column

    def get_implies_value(self, sub_statement: str, input_key: Tuple[bool, bool]):
        first, second = sub_statement[0], sub_statement[5]
        bool_index1, bool_index2 = self.index_order[first], self.index_order[second]
        if input_key[bool_index1] and not input_key[bool_index2]:
            return False
        return True
