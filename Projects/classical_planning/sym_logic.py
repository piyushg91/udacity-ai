import itertools
from typing import List


class SymLogicParser(object):
    def __init__(self):
        self.syms = ['p', 'q']
        self.index_order = {'p': 0, 'q': 1}
        possibilities = [True, False]
        self.pos = set(itertools.product(possibilities, repeat=len(self.syms)))

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
                if p_bool and not q_bool:
                    column[key] = False
                else:
                    column[key] = True
            elif statement.find('<=>') != -1:
                column[key] = p_bool == q_bool
            else:
                raise Exception('Do not know what to do with ' + statement)
        return column

