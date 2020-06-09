from unittest import TestCase
from sym_logic import SymLogicParser


class SymLogicTest(TestCase):
    def setUp(self):
        self.parser1 = SymLogicParser()
        self.parser2 = SymLogicParser()
        # self.parser3 = SymLogicParser(['A', 'B', 'C'])

    def test__init__(self):
        correct1 = {(True,), (False,)}
        correct2 = {(True, True), (True, False), (False, True), (False, False)}
        # correct3 = {(True, True, True), (True, True, False), (True, False, True), (True, False, False),
        #             (False, True, True), (False, True, False), (False, False, True), (False, False, False)}
        self.assertEqual(correct1, self.parser1.pos)
        self.assertEqual(correct2, self.parser2.pos)
        # self.assertEqual(correct3, self.parser3.pos)

    def test_not_p(self):
        inp = '~p'
        correct = {{'p': True}: {False},
                   {'p': False}: {True}}
        seen = self.parser1.create_column(inp)
        self.assertEqual(correct, seen)

    def test_and(self):
        inp = 'p ^ q'
        p, q = 'p', 'q'
        correct = {{p: True, q: True}: True,
                   {p: False, q: True}: False,
                   {p: True, q: False}: False,
                   {p: False, q: False}: False}
        seen = self.parser2.create_column(inp)
        self.assertEqual(correct, seen)

    def test3(self):
        inp = '~(~p V ~q)'
        p, q = 'p', 'q'
        correct = {{p: True, q: True}: True,
                   {p: False, q: True}: False,
                   {p: True, q: False}: False,
                   {p: False, q: False}: False}
        seen = self.parser2.create_column(inp)
        self.assertEqual(correct, seen)
