import unittest

from random_events.interval import *
from random_events.sigma_algebra import AbstractSimpleSet


class SimpleIntervalTestCase(unittest.TestCase):

    def test_intersection(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 2)
        c = SimpleInterval(0.5, 0.75, Bound.OPEN, Bound.CLOSED)

        intersection_a_b = a.intersection_with(b)
        intersection_a_b_ = SimpleInterval(0.5, 1, Bound.OPEN, Bound.OPEN)
        self.assertEqual(intersection_a_b, intersection_a_b_)

        intersection_a_c = a.intersection_with(c)
        self.assertEqual(intersection_a_c, c)

    def test_is_empty(self):
        a = SimpleInterval()
        b = SimpleInterval(3, 1)
        c = SimpleInterval(0, 1)
        self.assertTrue(a.is_empty())
        self.assertTrue(b.is_empty())
        self.assertFalse(c.is_empty())

    def test_complement(self):
        a = SimpleInterval()
        complement_a = a.complement()
        self.assertEqual(complement_a, SortedSet([SimpleInterval(-float('inf'), float('inf'), Bound.OPEN, Bound.OPEN)]))
        b = SimpleInterval(0, 1)
        complement_b = b.complement()
        self.assertEqual(complement_b, SortedSet([SimpleInterval(-float('inf'), 0, Bound.OPEN, Bound.CLOSED),
                                                  SimpleInterval(1, float('inf'), Bound.CLOSED, Bound.OPEN)]))

    def test_contains(self):
        a = SimpleInterval(0, 1)
        self.assertFalse(a.contains(0))
        self.assertTrue(a.contains(0.5))
        self.assertFalse(a.contains(1))
        self.assertFalse(a.contains(-1))
        self.assertFalse(a.contains(1.1))

    def test_to_json(self):
        a = SimpleInterval(0, 1)
        b = AbstractSimpleSet.from_json(a.to_json())
        self.assertIsInstance(b, SimpleInterval)
        self.assertEqual(a, b)


class IntervalTestCase(unittest.TestCase):

    def test_simplify(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 1.5)
        c = SimpleInterval(1.5, 2, Bound.CLOSED)
        d = SimpleInterval(3, 4)
        a_b = Interval(d, a, b, c)
        a_b_simplified = a_b.simplify()
        a_b_simplified_ = Interval(SimpleInterval(0, 2), SimpleInterval(3, 4))
        self.assertEqual(a_b_simplified, a_b_simplified_)

    def test_intersection_with_self(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 1.5)
        c = SimpleInterval(1.5, 2, Bound.CLOSED)
        d = SimpleInterval(3, 4)
        a_d = Interval(a, d)
        b_c = Interval(b, c)

        intersection_a_d_b_c = a_d.intersection_with(b_c)
        intersection_expected = Interval(SimpleInterval(0.5, 1))
        self.assertEqual(intersection_a_d_b_c, intersection_expected)

    def test_intersection_with_simple_set(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 1.5)
        d = SimpleInterval(3, 4)
        a_d = Interval(a, d)

        intersection_a_d_b_c = a_d.intersection_with_simple_set(b)
        intersection_expected = Interval(SimpleInterval(0.5, 1))
        self.assertEqual(intersection_a_d_b_c, intersection_expected)

    def test_intersection_with_set_of_simple_sets(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 1.5)
        c = SimpleInterval(1.5, 2, Bound.CLOSED)
        d = SimpleInterval(3, 4)
        a_d = Interval(a, d)

        intersection_a_d_b_c = a_d.intersection_with_simple_sets({b, c})
        intersection_expected = Interval(SimpleInterval(0.5, 1))
        self.assertEqual(intersection_a_d_b_c, intersection_expected)

    def test_complement(self):
        a = SimpleInterval(0, 1)
        d = SimpleInterval(3, 4)
        a_d = Interval(a, d)

        complement_a_d = a_d.complement()
        complement_a_d_ = Interval(SimpleInterval(-float('inf'), 0, Bound.OPEN, Bound.CLOSED),
                                   SimpleInterval(1, 3, Bound.CLOSED, Bound.CLOSED),
                                   SimpleInterval(4, float('inf'), Bound.CLOSED, Bound.OPEN))
        self.assertEqual(complement_a_d, complement_a_d_)

    def test_make_disjoint(self):
        a = SimpleInterval(0, 1, Bound.CLOSED, Bound.CLOSED)
        b = SimpleInterval(0.5, 1.5, Bound.CLOSED, Bound.CLOSED)
        c = SimpleInterval(1.5, 2, Bound.CLOSED, Bound.CLOSED)
        d = SimpleInterval(2, 3, Bound.CLOSED, Bound.CLOSED)
        a_b_c_d = Interval(a, b, c, d)

        disjoint = a_b_c_d.make_disjoint()

        a_b_c_d_expected = Interval(SimpleInterval(0, 3, Bound.CLOSED, Bound.CLOSED))
        self.assertEqual(disjoint, a_b_c_d_expected)

    def test_union(self):
        a = SimpleInterval(0, 1)
        b = SimpleInterval(0.5, 1.5)
        c = SimpleInterval(1.5, 2, Bound.CLOSED)
        d = SimpleInterval(3, 4)
        a_d = Interval(a, d)
        b_c = Interval(b, c)

        union_a_d_b_c = a_d.union_with(b_c)
        union_a_d_b_c_ = Interval(SimpleInterval(0, 2), SimpleInterval(3, 4))
        self.assertEqual(union_a_d_b_c, union_a_d_b_c_)
        self.assertTrue(union_a_d_b_c.is_disjoint())

    def test_to_json(self):
        a = SimpleInterval(0, 1)
        b = Interval(a)
        c = AbstractSimpleSet.from_json(b.to_json())
        self.assertIsInstance(c, Interval)
        self.assertEqual(b, c)

    def test_partial_order(self):
        a = open(2, 4) | open(5, 6)
        b = open(3, 4) | open(4.5, 5.5)
        self.assertTrue(a < b)
        self.assertFalse(b < a)

    def test_contained_integers(self):
        a = open(2, 4) | closed_open(4.5, 6)
        self.assertEqual(list(a.contained_integers()), [3, 5])


if __name__ == '__main__':
    unittest.main()
