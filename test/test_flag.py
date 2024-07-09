import enum
import unittest

from random_events.flag import Set


class TestFlag(Set):
    A = enum.auto()
    B = enum.auto()
    C = enum.auto()


class FlagTestCase(unittest.TestCase):

    def test_intersection(self):
        self.assertEqual(TestFlag.A.intersection_with(TestFlag.B), TestFlag(0))
        self.assertEqual(TestFlag.A.intersection_with(TestFlag.A), TestFlag.A)
        self.assertTrue(TestFlag(0).intersection_with(TestFlag.A).is_empty())

    def test_invert(self):
        self.assertEqual(TestFlag.A.complement(), TestFlag.B | TestFlag.C)


if __name__ == '__main__':
    unittest.main()
