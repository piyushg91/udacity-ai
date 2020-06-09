import itertools
from typing import List


class SymLogicParser(object):
    def __init__(self):
        self.syms = ['p', 'q']
        possibilities = [True, False]
        self.pos = set(itertools.product(possibilities, repeat=len(self.syms)))

    def create_column(self, statement: str):
        for p in self.pos:
            continue
