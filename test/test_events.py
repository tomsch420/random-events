import unittest

import portion

from random_events.events import VariableMap, Event, EncodedEvent
from random_events.variables import Continuous, Integer, Symbolic


class VariableTestCase(unittest.TestCase):

    integer: Integer
    symbol: Symbolic
    real: Continuous
    event: VariableMap

    @classmethod
    def setUpClass(cls):
        """
        Create some event for testing.
        """
        cls.integer = Integer("integer", set(range(10)))
        cls.symbol = Symbolic("symbol", {"a", "b", "c"})
        cls.real = Continuous("real")
        cls.event = VariableMap({cls.integer: 1, cls.symbol: "a", cls.real: 1.0})

    def test_creation(self):
        """
        Test that the event is created correctly.
        """
        self.assertEqual(self.event[self.integer], 1)
        self.assertEqual(self.event[self.symbol], "a")
        self.assertEqual(self.event[self.real], 1.0)

    def test_string_access(self):
        """
        Test that the event is accessible by string.
        """
        self.event["integer"] = self.event[self.integer]
        self.assertEqual(self.event["integer"], self.event[self.integer])
        self.assertEqual(self.event["symbol"], self.event[self.symbol])
        self.assertEqual(self.event["real"], self.event[self.real])

    def test_raising(self):
        """
        Test that the event raises an error if the variable is not in the map.
        """
        self.assertRaises(KeyError, lambda: self.event["not_in_map"])


class EventTestCase(unittest.TestCase):

    integer: Integer
    symbol: Symbolic
    real: Continuous
    event: Event

    @classmethod
    def setUpClass(cls):
        """
        Create some event for testing.
        """
        cls.integer = Integer("integer", set(range(10)))
        cls.symbol = Symbolic("symbol", {"a", "b", "c"})
        cls.real = Continuous("real")
        cls.event = Event({cls.integer: 1, cls.symbol: "a", cls.real: 1.0})

    def test_wrapping(self):
        """
        Test that the event is wrapped correctly.
        """
        self.assertEqual(self.event[self.integer], (1,))
        self.assertEqual(self.event[self.symbol], ("a",))
        self.assertEqual(self.event[self.real], portion.singleton(1.0))

    def test_set_assignment(self):
        """
        Test that the event is set correctly.
        """
        event = self.event.copy()
        event[self.integer] = (2, 3)
        self.assertEqual(event[self.integer], (2, 3))
        event[self.symbol] = ("b", "c")
        self.assertEqual(event[self.symbol], ("b", "c"))
        event[self.real] = portion.closed(0.0, 1.0)
        self.assertEqual(event[self.real], portion.closed(0.0, 1.0))

    def test_raising(self):
        """
        Test that errors are raised correctly.
        """
        event = self.event.copy()
        with self.assertRaises(ValueError):
            event[self.integer] = 11

        with self.assertRaises(ValueError):
            event[self.integer] = (-1,)

        with self.assertRaises(ValueError):
            event[self.symbol] = "d"

        with self.assertRaises(ValueError):
            event[self.symbol] = ("d",)

    def test_encode(self):
        """
        Test that events are correctly encoded.
        """
        encoded = self.event.encode()
        self.assertIsInstance(encoded, EncodedEvent)
        decoded = encoded.decode()
        self.assertEqual(self.event, decoded)

    def test_intersection(self):
        """
        Test ordinary intersection of events
        """
        event_1 = Event()
        event_1[self.integer] = (1, 2)
        event_1[self.symbol] = ("a", "b")

        result = event_1.intersection(self.event)

        self.assertEqual(result["integer"], (1, ))
        self.assertEqual(result["symbol"], ("a", ))
        self.assertEqual(result["real"], self.event["real"])

    def test_empty_intersection(self):
        """
        Test empty intersection of events
        """
        event_1 = Event()
        event_1[self.integer] = (1, 2)
        event_1[self.symbol] = ("c", )

        result = event_1.intersection(self.event)

        self.assertEqual(result["integer"], (1, ))
        self.assertEqual(result["symbol"], tuple())
        self.assertEqual(result["real"], self.event["real"])
        self.assertTrue(result.is_empty())


if __name__ == '__main__':
    unittest.main()
