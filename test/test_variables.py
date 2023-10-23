import unittest

import portion

from random_events.variables import Integer, Symbolic, Continuous


class VariablesTestCase(unittest.TestCase):
    """Tests for `variables.py`."""

    integer: Integer
    symbol: Symbolic
    real: Continuous

    @classmethod
    def setUpClass(cls):
        """
        Create some variables for testing.
        """
        cls.integer = Integer("integer", set(range(10)))
        cls.symbol = Symbolic("symbol", {"a", "b", "c"})
        cls.real = Continuous("real")

    def test_creation(self):
        """
        Test that the variables are created correctly.
        """
        self.assertEqual(self.integer.name, "integer")
        self.assertEqual(self.integer.domain, tuple(range(10)))
        self.assertEqual(self.symbol.name, "symbol")
        self.assertEqual(self.symbol.domain, ("a", "b", "c"))
        self.assertEqual(self.real.name, "real")
        self.assertEqual(self.real.domain, portion.open(-portion.inf, portion.inf))

    def test_hash(self):
        """
        Test that the variables are hashable.
        """
        self.assertTrue(hash(self.integer))
        self.assertTrue(hash(self.symbol))
        self.assertTrue(hash(self.real))

    def test_ordering(self):
        """
        Test that the variables are ordered correctly.
        """
        self.assertLess(self.integer, self.symbol)
        self.assertLess(self.real, self.symbol)
        self.assertLess(self.integer, self.real)
        self.assertEqual([self.integer, self.real, self.symbol], sorted([self.symbol, self.integer, self.real]))

    def test_equality(self):
        """
        Test that the variables are equal to themselves and not equal to others.
        """
        self.assertEqual(self.integer, Integer("integer", tuple(range(10))))
        self.assertNotEqual(self.symbol, Symbolic("symbol", ("d", "b", "c")))
        self.assertEqual(self.symbol, Symbolic("symbol", ("a", "b", "c")))
        self.assertEqual(self.real, Continuous("real"))

    def test_to_json(self):
        """
        Test that the variables can be dumped to json.
        """
        self.assertTrue(self.symbol.model_dump_json())
        self.assertTrue(self.integer.model_dump_json())
        self.assertTrue(self.real.model_dump_json())

    def test_from_json(self):
        """
        Test that the variables can be loaded from json.
        """
        real = Continuous.model_validate_json(self.real.model_dump_json())
        self.assertEqual(real, self.real)

        integer = Integer.model_validate_json(self.integer.model_dump_json())
        self.assertEqual(integer, self.integer)

        symbol = Symbolic.model_validate_json(self.symbol.model_dump_json())
        self.assertEqual(symbol, self.symbol)

    def test_encode(self):
        """
        Test that the variables can be encoded.
        """
        self.assertEqual(self.integer.encode(1), 1)
        self.assertEqual(self.symbol.encode("b"), 1)

    def test_decode(self):
        """
        Test that the variables can be decoded.
        """
        self.assertEqual(self.integer.decode(1), 1)
        self.assertEqual(self.symbol.decode(1), "b")


if __name__ == '__main__':
    unittest.main()
