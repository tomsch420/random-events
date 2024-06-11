from random_events.set import SetElement, Set
import enum
import unittest

from random_events.sigma_algebra import AbstractSimpleSet


class TestEnum(SetElement):
    EMPTY_SET = -1
    A = 1
    B = 2
    C = 4


class SetElementTestCase(unittest.TestCase):

    def test_intersection_with(self):
        a = TestEnum.A
        b = TestEnum.B

        intersection_a_b = a.intersection_with(b)
        self.assertEqual(intersection_a_b, TestEnum.EMPTY_SET)
        self.assertEqual(a.intersection_with(TestEnum.A), a)
        self.assertEqual(TestEnum.EMPTY_SET.intersection_with(TestEnum.A), TestEnum.EMPTY_SET)

    def test_complement(self):
        a = TestEnum.A
        complement = a.complement()
        self.assertEqual(complement, {TestEnum.B, TestEnum.C})

    def test_is_empty(self):
        a = TestEnum.EMPTY_SET
        b = TestEnum.B
        self.assertTrue(a.is_empty())
        self.assertFalse(b.is_empty())

    def test_contains(self):
        a = TestEnum.A
        self.assertTrue(a.contains(TestEnum.A))
        self.assertFalse(a.contains(TestEnum.B))
        self.assertFalse(a.contains(TestEnum.C))

    def test_to_json(self):
        a = TestEnum.A
        b = AbstractSimpleSet.from_json(a.to_json())
        self.assertEqual(a, b)


class SetTestCase(unittest.TestCase):

    def test_simplify(self):
        a = TestEnum.A
        b = TestEnum.B
        c = TestEnum.C
        s = Set(a, b, c, c)
        self.assertEqual(len(s.simple_sets), 3)
        self.assertEqual(s.simplify(), s)

    def test_difference(self):
        s = Set(TestEnum.A, TestEnum.B)
        s_ = Set(TestEnum.A)
        self.assertEqual(s.difference_with(s_), Set(TestEnum.B))

    def test_complement(self):
        s = Set(TestEnum.A, TestEnum.B)
        self.assertEqual(s.complement(), Set(TestEnum.C))

    def test_to_json(self):
        s = Set(TestEnum.A, TestEnum.B)
        s_ = AbstractSimpleSet.from_json(s.to_json())
        self.assertEqual(s, s_)

    def test_to_json_with_dynamic_enum(self):
        enum_ = SetElement("Foo", "A B C")
        s = Set(enum_.A, enum_.B)
        s_ = s.to_json()
        del enum_
        s_ = AbstractSimpleSet.from_json(s_)
        self.assertEqual(s, s_)



if __name__ == '__main__':
    unittest.main()
