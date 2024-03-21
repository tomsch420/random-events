import unittest

import portion

from random_events.events import VariableMap, Event, EncodedEvent, ComplexEvent
from random_events.variables import Continuous, Integer, Symbolic

import plotly.graph_objects as go


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
        self.assertTrue(result.is_empty())

    def test_intersection_alias(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2)
        event_1[self.symbol] = ("a", "b")
        self.assertEqual(event_1 & self.event, event_1.intersection(self.event))
        self.assertEqual(event_1 & self.event, self.event & event_1)

    def test_union_without_intersection(self):
        event1 = Event({self.integer: 1, self.symbol: "a", self.real: 2.0})
        union = event1.union(self.event)
        self.assertIsInstance(union, ComplexEvent)
        self.assertEqual(len(union.events), 2)
        self.assertTrue(union.are_events_disjoint())

    def test_difference(self):
        event_1 = Event()
        event_1[self.integer] = (1, 2, 5)
        event_1[self.symbol] = ("a", "b")
        result = event_1.difference(self.event)
        self.assertEqual(len(result.events), 3)
        self.assertTrue(result.are_events_disjoint())

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

    def test_serialization(self):
        json = self.event.to_json()
        event = Event.from_json(json)
        self.assertEqual(event, self.event)

    def test_serialization_with_complex_interval(self):
        event = Event({self.real: portion.closed(0, 1) | portion.closed(2, 3)})
        json = event.to_json()
        event_ = Event.from_json(json)
        self.assertEqual(event_, event)


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
        self.assertEqual(type(event | event), ComplexEvent)
        self.assertEqual(type(event - event), ComplexEvent)

    def test_intersection_with_empty(self):
        event = Event({self.integer: ()})
        complete_event = Event({self.integer: self.integer.domain})
        intersection = event.intersection(complete_event)
        self.assertIn(self.integer, intersection.keys())
        self.assertTrue(intersection.is_empty())

    def test_serialization(self):
        event = EncodedEvent()
        event[self.integer] = (1, 2)
        event[self.symbol] = {1, 0}
        event[self.real] = portion.open(0, 1)

        json = event.to_json()
        event_ = EncodedEvent.from_json(json)
        self.assertEqual(event, event_)


class ComplexEventTestCase(unittest.TestCase):

    x: Continuous = Continuous("x")
    y: Continuous = Continuous("y")
    z: Continuous = Continuous("z")
    a: Symbolic = Symbolic("a", {"a1", "a2"})
    b: Symbolic = Symbolic("b", {"b1", "b2", "b3"})
    unit_interval = portion.closed(0, 1)

    def test_union(self):
        event_1 = Event({self.x: self.unit_interval, self.y: self.unit_interval})
        event_2 = Event({self.x: portion.closed(0.5, 2), self.y: portion.closed(0.5, 2)})
        union = event_1.union(event_2)
        self.assertIsInstance(union, ComplexEvent)
        self.assertEqual(len(union.events), 3)
        self.assertTrue(union.are_events_disjoint())
        # go.Figure(union.plot()).show()

    def test_union_of_complex_events(self):
        event_1 = Event({self.x: self.unit_interval, self.y: self.unit_interval})
        event_2 = Event({self.x: portion.closed(0.5, 2), self.y: portion.closed(0.5, 2)})
        complex_event_1 = event_1.union(event_2)
        event_3 = Event({self.x: portion.closed(0.5, 2), self.y: portion.closed(-0.5, 2)})
        complex_event_2 = event_1.union(event_3)

        result = complex_event_1.union(complex_event_2)

        self.assertIsInstance(result, ComplexEvent)
        self.assertTrue(result.are_events_disjoint())

    def test_make_events_disjoint_and_simplify(self):
        event_1 = Event({self.x: self.unit_interval, self.y: self.unit_interval})
        event_2 = Event({self.x: portion.closed(0.5, 2), self.y: portion.closed(0.5, 2)})
        complex_event = ComplexEvent([event_1, event_2])
        self.assertFalse(complex_event.are_events_disjoint())
        complex_event = complex_event.make_events_disjoint()
        self.assertEqual(len(complex_event.events), 5)
        self.assertTrue(complex_event.are_events_disjoint())
        simplified_event = complex_event.simplify()
        self.assertEqual(len(simplified_event.events), 3)
        self.assertTrue(simplified_event.are_events_disjoint())

    def test_are_events_disjoint(self):
        event1 = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        event2 = Event({self.x: portion.closed(0.5, 2), self.y: portion.closed(0.5, 2)})
        event3 = Event({self.x: portion.closed(2, 3), self.y: portion.closed(2, 3)})

        complex_event = ComplexEvent((event1, event2))
        self.assertFalse(complex_event.are_events_disjoint())

        complex_event = ComplexEvent((event1, event3))
        self.assertTrue(complex_event.are_events_disjoint())

        complex_event = ComplexEvent((event1, event3, event2,))
        self.assertFalse(complex_event.are_events_disjoint())

    def test_from_continuous_complement(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complement = event.complement()

        self.assertEqual(len(complement.events), 2)
        self.assertTrue(complement.are_events_disjoint())

        c1 = complement.events[0]
        self.assertEqual(c1[self.x], portion.open(-portion.inf, 0) | portion.open(1, portion.inf))
        self.assertEqual(c1[self.y], portion.open(-portion.inf, portion.inf))

        c2 = complement.events[1]
        self.assertEqual(c2[self.y], portion.open(-portion.inf, 0) | portion.open(1, portion.inf))
        self.assertEqual(c2[self.x], event[self.x])

        for sub_event in complement.events:
            self.assertTrue(sub_event.intersection(event).is_empty())

    def test_complement_3d(self):
        event = Event({self.x: portion.closed(0, 1),
                       self.y: portion.closed(0, 1),
                       self.z: portion.closed(0, 1)})
        complement = event.complement()
        self.assertEqual(len(complement.events), 3)
        self.assertTrue(complement.are_events_disjoint())

    def test_from_discrete_complement(self):
        event = Event({self.a: "a1", self.b: "b1"})
        complement = event.complement()

        self.assertEqual(len(complement.events), 2)
        self.assertTrue(complement.are_events_disjoint())

        c1 = complement.events[0]
        self.assertEqual(c1[self.a], ("a2", ))
        self.assertEqual(c1[self.b], self.b.domain)

        c2 = complement.events[1]
        self.assertEqual(c2[self.a], ("a1", ))
        self.assertEqual(c2[self.b], ("b2", "b3"))

        for sub_event in complement.events:
            self.assertTrue(sub_event.intersection(event).is_empty())

    def test_chained_complement(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complement = event.complement()
        copied_event = complement.complement()
        self.assertEqual(len(copied_event.events), 1)
        self.assertEqual(copied_event.events[0], event)

    def test_union_of_simple_with_complex(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complex_event = ComplexEvent([event])
        union1 = event.union(complex_event)
        union2 = complex_event.union(event)
        self.assertEqual(union1, union2)

    def test_union_with_different_variables(self):
        event1 = Event({self.x: portion.closed(0, 1)})
        event2 = Event({self.y: portion.closed(0, 1)})
        union = event1.union(event2)
        for event in union.events:
            self.assertEqual(len(event), 2)

    def test_copy(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        copied = event.copy()
        self.assertEqual(event, copied)
        self.assertIsNot(event, copied)

    def test_decode_encode(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        encoded = event.encode()
        decoded = encoded.decode()
        self.assertEqual(event, decoded)

    def test_marginal_event(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complement = event.complement()
        marginal_event = complement.marginal_event([self.x])
        self.assertEqual(len(marginal_event.events), 1)
        self.assertEqual(marginal_event.events[0][self.x], portion.open(-portion.inf, portion.inf))

    def test_merge_if_1d(self):
        event1 = Event({self.x: portion.closed(0, 1)})
        event2 = Event({self.x: portion.closed(3, 4)})
        complex_event = ComplexEvent([event1, event2])
        merged = complex_event.merge_if_one_dimensional()
        self.assertEqual(len(merged.events), 1)
        self.assertEqual(merged.events[0][self.x], portion.closed(0, 1) | portion.closed(3, 4))

    def test_serialization(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complement = event.complement()
        json = complement.to_json()
        complement_ = ComplexEvent.from_json(json)
        self.assertEqual(complement, complement_)

    def test_intersection_symbol_and_real(self):
        event = ComplexEvent([EncodedEvent({self.x: portion.closed(0, 1)})])
        event2 = EncodedEvent({self.a: (0, )})
        result = event & event2
        self.assertEqual(len(result.events), 1)
        event_ = result.events[0]
        self.assertEqual(event_[self.x], portion.closed(0, 1))
        self.assertEqual(event_[self.a], (0, ))


class PlottingTestCase(unittest.TestCase):
    x: Continuous = Continuous("x")
    y: Continuous = Continuous("y")
    z: Continuous = Continuous("z")

    def test_plot_2d(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        fig = go.Figure(event.plot())
        # fig.show()

    def test_plot_3d(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1), self.z: portion.closed(0, 1)})
        fig = go.Figure(event.plot())
        # fig.show()

    def test_plot_complex_event_2d(self):
        event = Event({self.x: portion.closed(0, 1), self.y: portion.closed(0, 1)})
        complement = event.complement()
        limiting_event = Event({self.x: portion.closed(-1, 2), self.y: portion.closed(-1, 2)})
        result = complement.intersection(ComplexEvent([limiting_event]))
        fig = go.Figure(result.plot(), result.plotly_layout())
        # fig.show()

    def test_plot_complex_event_3d(self):
        event = Event({self.x: portion.closed(0, 1),
                       self.y: portion.closed(0, 1),
                       self.z: portion.closed(0, 1)})
        complement = event.complement()
        limiting_event = Event({self.x: portion.closed(-1, 2),
                                self.y: portion.closed(-1, 2),
                                self.z: portion.closed(-1, 2)})
        result = complement.intersection(ComplexEvent([limiting_event]))
        fig = go.Figure(result.plot(), result.plotly_layout())
        # fig.show()


if __name__ == '__main__':
    unittest.main()
