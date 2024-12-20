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

    def test_marginal_event(self):
        event_1 = SimpleEvent({self.x: closed(0, 1), self.y: SimpleInterval(0, 1)})
        event_2 = SimpleEvent({self.x: closed(1, 2), self.y: Interval(SimpleInterval(3, 4))})
        event_3 = SimpleEvent({self.x: closed(5, 6), self.y: Interval(SimpleInterval(5, 6))})
        event = Event(event_1, event_2, event_3)
        marginal = event.marginal(SortedSet([self.x]))
        self.assertEqual(marginal, SimpleEvent({self.x: closed(0, 2) | closed(5, 6)}).as_composite_set())
        fig = go.Figure(marginal.plot())
        # fig.show()

    def test_to_json_multiple_events(self):
        event = SimpleEvent({self.x: closed(0, 1), self.y: SimpleInterval(3, 5),
                             self.a: Set(TestEnum.A, TestEnum.B)}).as_composite_set()
        event_ = AbstractSimpleSet.from_json(event.to_json())
        self.assertEqual(event_, event)

    def test_bounding_box(self):
        event_1 = SimpleEvent({self.x: closed(0, 1), self.y: SimpleInterval(0, 1)}).as_composite_set()
        event_2 = SimpleEvent({self.x: closed(1, 2), self.y: Interval(SimpleInterval(3, 4))}).as_composite_set()
        event = event_1 | event_2

        event_before_bounding_box = event.__deepcopy__()
        bounding_box = event.bounding_box()
        result = SimpleEvent({self.x: closed(0, 2),
                              self.y: SimpleInterval(0, 1).as_composite_set() | SimpleInterval(3, 4).as_composite_set()})
        self.assertEqual(bounding_box, result)
        self.assertEqual(event, event_before_bounding_box)

    def test_complex_event_bounding_box_with_references(self):
        event1 = SimpleEvent({self.x: closed(0, 1) |  closed(2, 3),
                             self.y: closed(0, 1) |  closed(2, 3)}).as_composite_set()
        event2 = SimpleEvent({self.x: closed(1, 2) |  closed(3, 4),
                             self.y: closed(1, 2) |  closed(3, 4)}).as_composite_set()
        event = event1 | event2
        event_before_bb = event.__deepcopy__()
        bb = event.bounding_box()
        self.assertEqual(event, event_before_bb)

class NoneTypeObjectInDifferenceTestCase(unittest.TestCase):
    x: Continuous = Continuous("x")
    y: Continuous = Continuous("y")
    event_1 = Event(SimpleEvent({x: SimpleInterval(0, 0.25, Bound.CLOSED, Bound.CLOSED),
                                 y: SimpleInterval(0.25, 1, Bound.CLOSED, Bound.CLOSED)}),
                    SimpleEvent({x: SimpleInterval(0.75, 1, Bound.CLOSED, Bound.CLOSED),
                                 y: SimpleInterval(0.75, 1, Bound.CLOSED, Bound.CLOSED)}))
    event_2 = SimpleEvent({x: SimpleInterval(0., 0.25, Bound.CLOSED, Bound.CLOSED),
                           y: SimpleInterval(0., 1, Bound.CLOSED, Bound.CLOSED)}).as_composite_set()

    def test_union(self):
        union = self.event_1 | self.event_2
        union_by_hand = Event(SimpleEvent({self.x: SimpleInterval(0, 0.25, Bound.CLOSED, Bound.CLOSED),
                                           self.y: SimpleInterval(0., 1, Bound.CLOSED, Bound.CLOSED)}),
                              SimpleEvent({self.x: SimpleInterval(0.75, 1, Bound.CLOSED, Bound.CLOSED),
                                           self.y: SimpleInterval(0.75, 1, Bound.CLOSED, Bound.CLOSED)}))
        self.assertEqual(union, union_by_hand)


class OperationsWithEmptySetsTestCase(unittest.TestCase):

    x: Continuous = Continuous("x")
    y: Continuous = Continuous("y")
    a: Symbolic = Symbolic("a", TestEnum)

    def test_empty_union(self):
        empty_event = SimpleEvent({self.x: SimpleInterval(0, 0), self.y: SimpleInterval(0, 0)}).as_composite_set()
        event = SimpleEvent({self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)}).as_composite_set()
        union = empty_event.union_with(event)
        self.assertEqual(union, event)

    def test_union_different_variables(self):
        event_1 = SimpleEvent({self.x: SimpleInterval(0, 1)}).as_composite_set()
        event_2 = SimpleEvent({self.y: SimpleInterval(0, 1)}).as_composite_set()
        union = event_1.union_with(event_2)
        # self.assertEqual(union, Event(event_1, event_2))

    def test_difference_with_empty_set(self):
        event = SimpleEvent({self.x: SimpleInterval(0, 1), self.y: SimpleInterval(0, 1)}).as_composite_set()
        empty_event = Event()
        diff = event.difference_with(empty_event)
        self.assertEqual(diff, event)

if __name__ == '__main__':
    unittest.main()
