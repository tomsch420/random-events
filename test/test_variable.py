import unittest

from random_events.variable import *
from random_events.interval import *


class TestEnum(SetElement):
    EMPTY_SET = 0
    A = 1
    B = 2
    C = 4


class ContinuousTestCase(unittest.TestCase):
    x = Continuous("x")

    def test_creation(self):
        self.assertEqual(self.x.name, "x")
        self.assertEqual(self.x.domain, reals())

    def test_to_json(self):
        x_ = Variable.from_json(self.x.to_json())
        self.assertEqual(self.x, x_)


class IntegerTestCase(unittest.TestCase):

    def test_creation(self):
        x = Integer("x")
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, reals())


class SymbolicTestCase(unittest.TestCase):

    def test_creation(self):
        x = Symbolic("x", TestEnum)
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, Set(TestEnum.A, TestEnum.B, TestEnum.C))

    def test_to_json(self):
        x = Symbolic("x", TestEnum)
        x_ = Variable.from_json(x.to_json())
        self.assertEqual(x, x_)


if __name__ == '__main__':
    unittest.main()
