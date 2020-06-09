from unittest import TestCase
from sym_logic import SymLogicParser


class SymLogicTest(TestCase):
    def setUp(self):
        # self.parser1 = SymLogicParser()
        self.parser2 = SymLogicParser()
        # self.parser3 = SymLogicParser(['A', 'B', 'C'])

    def test__init__(self):
        # correct1 = {(True,), (False,)}
        correct2 = {(True, True), (True, False), (False, True), (False, False)}
        # correct3 = {(True, True, True), (True, True, False), (True, False, True), (True, False, False),
        #             (False, True, True), (False, True, False), (False, False, True), (False, False, False)}
        # self.assertEqual(correct1, self.parser1.pos)
        self.assertEqual(correct2, self.parser2.pos)
        # self.assertEqual(correct3, self.parser3.pos)

    def test_not_p(self):
        inp = '~p'
        correct = {(True, True): False,
                   (True, False): False,
                   (False, True): True,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_not_q(self):
        inp = '~q'
        correct = {(True, True): False,
                   (True, False): True,
                   (False, True): False,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_and(self):
        inp = 'p ^ q'
        correct = {(True, True): True,
                   (False, True): False,
                   (True, False): False,
                   (False, False): False}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_or(self):
        inp = 'p V q'
        correct = {(True, True): True,
                   (False, True): True,
                   (True, False):  True,
                   (False, False): False}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_implies(self):
        inp = 'p => q'
        correct = {(True, True): True,
                   (False, True): True,
                   (True, False):  False,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_implies_backwards(self):
        inp = 'q => p'
        correct = {(True, True): True,
                   (False, True): False,
                   (True, False):  True,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_equivalence(self):
        inp = 'p <=> q'
        correct = {(True, True): True,
                   (False, True): False,
                   (True, False):  False,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_complicated_one(self):
        inp = 'p ^ (p => q)'
        correct = {(True, True): True,
                   (False, True): False,
                   (True, False):  False,
                   (False, False): False}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_complicated_two(self):
        inp = '~(~p V ~q)'
        correct = {(True, True): True,
                   (False, True): False,
                   (True, False):  False,
                   (False, False): False}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_complicated_three(self):
        inp = '(p ^ (p => q)) <=> (~(~p V ~q))'
        correct = {(True, True): True,
                   (False, True): True,
                   (True, False):  True,
                   (False, False): True}
        seen = self.parser2.get_column_vals(inp)
        self.assertEqual(correct, seen)

    def test_determine_first_and_second_input(self):
        inp = 'p ^ (p => q)'
        correct = 'p', '^', 'p => q'
        self.assertEqual(correct, SymLogicParser.determine_first_and_second_input(inp))

        inp = 'p ^ ((p => q) V q)'
        correct = 'p', '^', '(p => q) V q'
        self.assertEqual(correct, SymLogicParser.determine_first_and_second_input(inp))

        inp = '(p => q) ^ q'
        correct = 'p => q', '^', 'q'
        self.assertEqual(correct, SymLogicParser.determine_first_and_second_input(inp))

