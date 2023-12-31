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

    def test_intersection_alias(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2)
        event_1[self.symbol] = ("a", "b")
        self.assertEqual(event_1 & self.event, event_1.intersection(self.event))
        self.assertEqual(event_1 & self.event, self.event & event_1)

    def test_union(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2, 5)
        event_1[self.symbol] = ("a", "b")

        result = self.event.union(event_1)
        self.assertEqual(result["integer"], (1, 2, 5))
        self.assertEqual(result["symbol"], ("a", "b"))
        self.assertEqual(result["real"], self.event["real"])

    def test_union_alias(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2, 5)
        event_1[self.symbol] = ("a", "b")
        self.assertEqual(event_1 | self.event, event_1.union(self.event))
        self.assertEqual(event_1 | self.event, self.event | event_1)

    def test_difference(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2, 5)
        event_1[self.symbol] = ("a", "b")
        result = event_1.difference(self.event)
        self.assertEqual(result["integer"], (2, 5))
        self.assertEqual(result["symbol"], ("b", ))
        self.assertEqual(result["real"], portion.open(-portion.inf, portion.inf) - self.event["real"])

    def test_difference_alias(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2, 5)
        event_1[self.symbol] = ("a", "b")
        self.assertEqual(event_1 - self.event, event_1.difference(self.event))
        # differences are not symmetric
        self.assertNotEqual(event_1 - self.event, self.event - event_1)

    def test_equality(self):
        self.assertEqual(self.event, self.event)
        self.assertNotEqual(self.event, Event())

    def test_raises_on_operation_with_different_types(self):
        with self.assertRaises(TypeError):
            self.event & self.event.encode()

        with self.assertRaises(TypeError):
            self.event | self.event.encode()

        with self.assertRaises(TypeError):
            self.event - self.event.encode()


class EncodedEventTestCase(unittest.TestCase):

    integer: Integer
    symbol: Symbolic
    real: Continuous

    @classmethod
    def setUpClass(cls):
        """
        Create some event for testing.
        """
        cls.integer = Integer("integer", set(range(10)))
        cls.symbol = Symbolic("symbol", {"a", "b", "c"})
        cls.real = Continuous("real")

    def test_creation(self):
        event = EncodedEvent()
        event[self.integer] = 1
        self.assertEqual(event[self.integer], (1,))
        event[self.integer] = (1, 2)
        self.assertEqual(event[self.integer], (1, 2))
        event[self.symbol] = 0
        self.assertEqual(event[self.symbol], (0, ))
        event[self.symbol] = {1, 0}
        self.assertEqual(event[self.symbol], (0, 1))

        interval = portion.open(0, 1)
        event[self.real] = interval
        self.assertEqual(interval, event[self.real])

    def test_raises(self):
        event = EncodedEvent()
        with self.assertRaises(ValueError):
            event[self.symbol] = 3

        with self.assertRaises(ValueError):
            event[self.symbol] = portion.open(0, 1)

        with self.assertRaises(ValueError):
            event[self.symbol] = (1, 2, 3, 4)

    def test_dict_like_creation(self):
        event = EncodedEvent(zip([self.integer, self.symbol], [1, 0]))
        self.assertEqual(event[self.integer], (1,))
        self.assertEqual(event[self.symbol], (0,))

        event = EncodedEvent(zip([self.integer, self.symbol], [[0, 1], 0]))
        self.assertEqual(event[self.integer], (0, 1))
        self.assertEqual(event[self.symbol], (0,))

    def test_set_operations_return_type(self):
        event = EncodedEvent(zip([self.integer, self.symbol], [1, 0]))
        self.assertEqual(type(event & event), EncodedEvent)
        self.assertEqual(type(event | event), EncodedEvent)
        self.assertEqual(type(event - event), EncodedEvent)


if __name__ == '__main__':
    unittest.main()
