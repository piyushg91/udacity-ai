import itertools
from typing import List


class SymLogicParser(object):
    def __init__(self, symbols: List[str]):
        self.syms = symbols
        possibilities = [True, False]
        self.pos = set(itertools.product(possibilities))

    def create_column(self, statement: str):
        for p in self.pos:
            continue
