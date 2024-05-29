import unittest

from random_events.better_variables import *
from random_events.interval import *


class TestEnum(SetElement):
    EMPTY_SET = 0
    A = 1
    B = 2
    C = 4


class ContinuousTestCase(unittest.TestCase):

    def test_creation(self):
        x = Continuous("x")
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, Interval([SimpleInterval(-float("inf"), float("inf"))]))


class IntegerTestCase(unittest.TestCase):

    def test_creation(self):
        x = Integer("x")
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, Interval([SimpleInterval(-float("inf"), float("inf"))]))


class SymbolicTestCase(unittest.TestCase):

    def test_creation(self):
        x = Symbolic("x", TestEnum)
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, Set([TestEnum.A, TestEnum.B, TestEnum.C]))


if __name__ == '__main__':
    unittest.main()
