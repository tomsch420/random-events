from random_events.set import SetElement, Set, EMPTY_SET_SYMBOL
import enum
import unittest

from random_events.sigma_algebra import AbstractSimpleSet


str_set = {'a', 'c', 'b'}
int_set = {1, 2, 3}
float_set = {1.001, 2.3845, 3.4345345}

EMPTY_SET = SetElement(EMPTY_SET_SYMBOL, set())

class SetElementTestCase(unittest.TestCase):

    def test_intersection_with(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)

        intersection_a_b = a.intersection_with(b)
        self.assertEqual(intersection_a_b, EMPTY_SET)
        self.assertEqual(a.intersection_with(a), a)

    def test_complement(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        c = SetElement('c', str_set)
        # a1 = SetElement(1, int_set)
        # a2 = SetElement(2, int_set)
        # a3 = SetElement(3, int_set)
        complement_a = a.complement()
        complement_b = b.complement()
        complement_c = c.complement()
        # complement_a1 = a1.complement()
        self.assertEqual(complement_a, {b, c})
        self.assertEqual(complement_b, {a, c})
        self.assertEqual(complement_c, {a, b})
        # self.assertEqual(complement_a1, {a2, a3})

    def test_contains(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        c = SetElement('c', str_set)
        self.assertTrue(a.contains(a))
        self.assertFalse(a.contains(b))
        self.assertFalse(a.contains(c))

    def test_to_json(self):
        a = SetElement('a', str_set)
        b = AbstractSimpleSet.from_json(a.to_json())
        self.assertEqual(a, b)


class SetTestCase(unittest.TestCase):

    def test_simplify(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        c = SetElement('c', str_set)
        s = Set(a, b, c, c)
        self.assertEqual(3, len(s.simple_sets))
        ss = Set(a, b, c)
        self.assertEqual(ss, s.simplify())

    def test_difference(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        s = Set(a, b)
        s_ = Set(a)
        self.assertEqual(s.difference_with(s_), Set(b))

    def test_complement(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        c = SetElement('c', str_set)
        s = Set(a, b)
        self.assertEqual(s.complement(), Set(c))

    def test_to_json(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        s = Set(a, b)
        s_ = AbstractSimpleSet.from_json(s.to_json())
        self.assertEqual(s, s_)


class SetTypeTestCase(unittest.TestCase):
    def test_int(self):
        a = SetElement(1, int_set)
        b = SetElement(2, int_set)
        c = SetElement(3, int_set)

        s = Set(a, b, c)
        s2 = Set(a, b)
        inter = s.intersection_with(s2)
        self.assertEqual(inter, s2)

    def test_str(self):
        a = SetElement('a', str_set)
        b = SetElement('b', str_set)
        c = SetElement('c', str_set)

        s = Set(a, b, c)
        s2 = Set(a, b)
        inter = s.intersection_with(s2)
        self.assertEqual(inter, s2)

    def test_float(self):
        a = SetElement(1.001, float_set)
        b = SetElement(2.3845, float_set)
        c = SetElement(3.4345345, float_set)

        s = Set(a, b, c)
        s2 = Set(a, b)
        inter = s.intersection_with(s2)
        self.assertEqual(inter, s2)


if __name__ == '__main__':
    unittest.main()
