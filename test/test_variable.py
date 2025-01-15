import unittest

from random_events.variable import *
from random_events.interval import *


str_set = {'a', 'c', 'b'}

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
        a = SetElement("a", str_set)
        b = SetElement("b", str_set)
        c = SetElement("c", str_set)
        x = Symbolic("x", Set(a, b, c))
        self.assertEqual(x.name, "x")
        self.assertEqual(x.domain, Set(a, b, c))

    def test_to_json(self):
        a = SetElement("a", str_set)
        b = SetElement("b", str_set)
        c = SetElement("c", str_set)
        x = Symbolic("x", Set(a, b, c))
        x_ = Variable.from_json(x.to_json())
        self.assertEqual(x, x_)


if __name__ == '__main__':
    unittest.main()
