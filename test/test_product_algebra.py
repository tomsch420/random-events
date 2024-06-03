import unittest

import plotly.graph_objects as go

from random_events.interval import *
from random_events.product_algebra import SimpleEvent, Event
from random_events.set import SetElement, Set
from random_events.sigma_algebra import AbstractSimpleSet
from random_events.variable import Continuous, Symbolic


class TestEnum(SetElement):
    EMPTY_SET = 0
    A = 1
    B = 2
    C = 4


class EventTestCase(unittest.TestCase):
    x = Continuous("x")
    y = Continuous("y")
    z = Continuous("z")
    a = Symbolic("a", TestEnum)
    b = Symbolic("b", TestEnum)

    def test_constructor(self):
        event = SimpleEvent({self.a: Set(TestEnum.A), self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)})

        self.assertEqual(event[self.x], Interval(SimpleInterval(0, 1)))
        self.assertEqual(event[self.y], Interval(SimpleInterval(0, 1)))
        self.assertEqual(event[self.a], Set(TestEnum.A))

        self.assertFalse(event.is_empty())
        self.assertTrue(event.contains((TestEnum.A, 0.5, 0.1,)))
        self.assertFalse(event.contains((TestEnum.B, 0.5, 0.1,)))

    def test_intersection_with(self):
        event_1 = SimpleEvent(
            {self.a: Set(TestEnum.A, TestEnum.B), self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)})
        event_2 = SimpleEvent({self.a: TestEnum.A, self.x: SimpleInterval(0.5, 1)})
        intersection = event_1.intersection_with(event_2)
        intersection_ = SimpleEvent(
            {self.a: Set(TestEnum.A), self.x: Interval(SimpleInterval(0.5, 1)), self.y: Interval(SimpleInterval(0, 1))})
        self.assertEqual(intersection, intersection_)
        self.assertNotEqual(intersection, event_1)

        event_3 = SimpleEvent({self.a: TestEnum.C})
        intersection = event_1.intersection_with(event_3)
        self.assertTrue(intersection.is_empty())

    def test_complement(self):
        event = SimpleEvent({self.a: Set(TestEnum.A, TestEnum.B), self.x: SimpleInterval(0, 1), self.y: self.y.domain})
        complement = event.complement()
        self.assertEqual(len(complement), 2)
        complement_1 = SimpleEvent({self.a: TestEnum.C, self.x: self.x.domain, self.y: self.y.domain})
        complement_2 = SimpleEvent({self.a: event[self.a], self.x: event[self.x].complement(), self.y: self.y.domain})
        self.assertEqual(complement, SortedSet([complement_1, complement_2]))

    def test_simplify(self):
        event_1 = SimpleEvent(
            {self.a: Set(TestEnum.A, TestEnum.B), self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)})
        event_2 = SimpleEvent(
            {self.a: Set(TestEnum.C), self.x: SimpleInterval(0, 1), self.y: Interval(SimpleInterval(0, 1))})
        event = Event(event_1, event_2)
        simplified = event.simplify()
        self.assertEqual(len(simplified.simple_sets), 1)

        result = Event(SimpleEvent(
            {self.a: self.a.domain, self.x: Interval(SimpleInterval(0, 1)), self.y: Interval(SimpleInterval(0, 1))}))
        self.assertEqual(simplified, result)

    def test_to_json(self):
        event = SimpleEvent({self.a: Set(TestEnum.A, TestEnum.B), self.x: SimpleInterval(0, 1),
                             self.y: SimpleInterval(0, 1)})
        event_ = AbstractSimpleSet.from_json(event.to_json())
        self.assertEqual(event_, event)

    def test_plot_2d(self):
        event_1 = SimpleEvent({self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)})
        event_2 = SimpleEvent({self.x: Interval(SimpleInterval(1, 2)), self.y: Interval(SimpleInterval(1, 2))})
        event = Event(event_1, event_2)
        fig = go.Figure(event.plot(), event.plotly_layout())
        self.assertIsNotNone(fig)  # fig.show()

    def test_plot_3d(self):
        event_1 = SimpleEvent(
            {self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1), self.z: SimpleInterval(0, 1)})
        event_2 = SimpleEvent(
            {self.x: SimpleInterval(1, 2), self.y: SimpleInterval(1, 2), self.z: SimpleInterval(1, 2)})
        event = Event(event_1, event_2)
        fig = go.Figure(event.plot(), event.plotly_layout())
        self.assertIsNotNone(fig)  # fig.show()

    def test_union(self):
        event = Event(SimpleEvent({self.a: TestEnum.A, self.x: open(-float("inf"), 2)}))
        second_event = SimpleEvent({self.a: Set(TestEnum.A, TestEnum.B), self.x: open(1, 4)}).as_composite_set()
        union = event | second_event
        result = Event(SimpleEvent({self.a: TestEnum.A, self.x: open(-float("inf"), 4)}),
                        SimpleEvent({self.a: TestEnum.B, self.x: open(1, 4)}))
        self.assertEqual(union, result)


if __name__ == '__main__':
    unittest.main()
