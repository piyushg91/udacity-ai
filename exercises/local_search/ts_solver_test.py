from exercises.local_search.ts_solver import TravelingSalesmanProblem
from exercises.local_search.helpers import contains
from unittest import TestCase


class TSSolverTest(TestCase):
    def setUp(self):
        test_cities = [('DC', (11, 1)), ('SF', (0, 0)), ('PHX', (2, -3)), ('LA', (0, -4))]
        self.tsp = TravelingSalesmanProblem(test_cities)

    def test_one(self):
        # Construct an instance of the TravelingSalesmanProblem and test `.__get_value()`
        assert round(-self.tsp.utility, 2) == 28.97, \
            "There was a problem with the utility value returned by your TSP class."

    def test_two(self):
        # Test the successors() method
        successor_paths = set([x.path for x in self.tsp.successors()])
        expected_paths = [
            (('SF', (0, 0)), ('DC', (11, 1)), ('PHX', (2, -3)), ('LA', (0, -4))),
            (('DC', (11, 1)), ('LA', (0, -4)), ('SF', (0, 0)), ('PHX', (2, -3))),
            (('LA', (0, -4)), ('PHX', (2, -3)), ('DC', (11, 1)), ('SF', (0, 0)))
        ]
        for x in expected_paths:
            self.assertIn(x, successor_paths)

        assert all(contains(successor_paths, x) for x in expected_paths), \
            "It looks like your successors list does not implement the suggested neighborhood function."
