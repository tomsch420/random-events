from __future__ import annotations

import itertools
from collections import UserDict

import numpy as np
import portion
import plotly.graph_objects as go

from typing_extensions import Set, Union, Any, TYPE_CHECKING, Iterable, List, Self, Dict, Tuple

from .variables import Variable, Continuous, Discrete


# Type hinting for Python 3.7 to 3.9
if TYPE_CHECKING:
    VariableMapType = UserDict[str, Variable]
else:
    VariableMapType = UserDict


class VariableMap(VariableMapType):
    """
    A map of variables to values.

    Accessing a variable by name is also supported.
    """

    def variable_of(self, name: str) -> Variable:
        """
        Get the variable with the given name.
        :param name: The variable's name
        :return: The variable itself
        """
        variable = [variable for variable in self.keys() if variable.name == name]
        if len(variable) == 0:
            raise KeyError(f"Variable {name} not found in event {self}")
        return variable[0]

    def __getitem__(self, item: Union[str, Variable]):
        if isinstance(item, str):
            item = self.variable_of(item)
        return super().__getitem__(item)

    def __setitem__(self, key: Union[str, Variable], value: Any):
        if isinstance(key, str):
            key = self.variable_of(key)

        if not isinstance(key, Variable):
            raise TypeError(f"Key must be a Variable, not {type(key)}")
        super().__setitem__(key, value)

    def __copy__(self):
        return self.__class__({variable: value for variable, value in self.items()})


# Type hinting for Python 3.7 to 3.9
if TYPE_CHECKING:
    EventMapType = VariableMap[str, Union[tuple, portion.Interval]]
else:
    EventMapType = VariableMap


class SupportsSetOperations:
    """
    A class that supports set operations.
    """

    def union(self, other: Self) -> Self:
        """
        Form the union of this object with another object.
        """
        raise NotImplementedError

    def __or__(self, other: Self):
        return self.union(other)

    def intersection(self, other: Self) -> Self:
        """
        Form the intersection of this object with another object.
        """
        raise NotImplementedError

    def __and__(self, other):
        return self.intersection(other)

    def difference(self, other: Self) -> Self:
        """
        Form the difference of this object with another object.
        """
        raise NotImplementedError

    def __sub__(self, other):
        return self.difference(other)

    def complement(self) -> Self:
        """
        Form the complement of this object.
        """
        raise NotImplementedError

    def __invert__(self):
        return self.complement()

    def is_empty(self) -> bool:
        """
        Check if this object is empty.
        """
        raise NotImplementedError


class Event(SupportsSetOperations, EventMapType):
    """
    A map of variables to values of their respective domains.
    """

    def check_same_type(self, other: Any):
        """
        Check that both self and other are of the same type.

        :param other: The other object
        """
        if type(self) is not type(other):
            raise TypeError(f"Cannot use operation on {type(self)} with {type(other)}")

    def intersection(self, other: EventType) -> EventType:

        # if the other is a complex event
        if isinstance(other, ComplexEvent):

            # flip the call
            return other.intersection(ComplexEvent([self]))

        self.check_same_type(other)
        result = self.__class__()

        variables = set(self.keys()) | set(other.keys())
        for variable in variables:
            assignment1 = self.get(variable, variable.domain)
            assignment2 = other.get(variable, variable.domain)
            intersection = variable.intersection_of_assignments(assignment1, assignment2)
            result[variable] = intersection

        return result

    def union(self, other: EventType) -> ComplexEvent:
        # create complex event from self
        complex_self = ComplexEvent([self])

        # if the other is a complex event
        if isinstance(other, ComplexEvent):

            # flip the call
            return other.union(complex_self)

        self.check_same_type(other)

        # form the intersection
        intersection = self.intersection(other)

        # if the intersection of the two events is empty
        if intersection.is_empty():

            # trivially mount it
            complex_self.events.append(other)
            return complex_self

        # form complement of intersection
        complement_of_intersection = intersection.complement()

        # intersect the other event with the complement of the intersection
        fragments_of_other = complement_of_intersection.intersection(ComplexEvent([other]))

        # add the fragments of the other event
        complex_self.events.extend(fragments_of_other.events)
        return ComplexEvent(complex_self.events)

    def difference(self, other: EventType) -> ComplexEvent:
        # if the other is a complex event
        if isinstance(other, ComplexEvent):

            # flip the call
            return other.complement().intersection(ComplexEvent([self]))

        self.check_same_type(other)

        # form the intersection
        intersection = self.intersection(other)

        # if the intersection of the two events is empty
        if intersection.is_empty():
            return ComplexEvent([self])

        # form complement of intersection
        complement_of_intersection = intersection.complement()

        # construct intersection of complement
        return ComplexEvent([event.intersection(self) for event in complement_of_intersection.events
                             if not event.is_empty()])

    def complement(self) -> ComplexEvent:
        # initialize events
        events = []

        # get variables as set
        variables: Set[Variable] = set(self.keys())

        # memorize processed variables
        processed_variables = []

        # for every assignment
        for variable, value in self.items():

            # create the current complementary event
            complement_event = self.__class__()

            # invert this variables assignment
            complement_event[variable] = variable.complement_of_assignment(
                value, encoded=isinstance(self, EncodedEvent))

            # for every other variable
            for other_variable in variables.difference({variable}):

                # if the other variable is already processed
                if other_variable in processed_variables:
                    # add the assignment to the current event
                    complement_event[other_variable] = self[other_variable]
                else:
                    # add the entire domain to the current event
                    other_domain = other_variable.domain

                    # encode if necessary
                    if isinstance(self, EncodedEvent):
                        other_domain = other_variable.encode_many(other_domain)
                    complement_event[other_variable] = other_domain

            # add to processed variables
            processed_variables.append(variable)

            # add to complex event
            if not complement_event.is_empty():
                events.append(complement_event)
        return ComplexEvent(events)

    def __eq__(self, other: Self) -> bool:
        """
        Check if two events are equal.

        If one variable is only in one of the events, it is assumed that the other event has the entire domain as
        default value.
        """

        variables = set(self.keys()) | set(other.keys())

        equal = True

        for variable in variables:
            if variable in self and variable not in other:
                value_equal = variable.domain == self[variable]
            elif variable in other and variable not in self:
                value_equal = variable.domain == other[variable]
            else:
                value_equal = self[variable] == other[variable]
            equal &= value_equal

        return equal

    @staticmethod
    def check_element(variable: Variable, element: Any) -> Union[tuple, portion.Interval]:
        """
        Check that elements can be regarded as elements of the variable's domain.

        Wrap a single element into a set or interval, depending on the variable type.
        For any Iterable type that is not a string, the element is converted to a tuple of that iterable.

        :param variable: The variable where the element should belong to
        :param element: The element to wrap
        :return: The wrapped element
        """

        if isinstance(element, Iterable) and not isinstance(element, (str, portion.Interval)):
            element = tuple(element)

        # if the element is already wrapped
        if isinstance(element, (tuple, portion.Interval)):

            # check that the element is in the variable's domain
            if isinstance(variable, Discrete):
                if not all(elem in variable.domain for elem in element):
                    # raise an error
                    raise ValueError(f"Element {element} not in domain {variable.domain}")

                element = tuple(sorted(element))

            # return the element directly
            return element

        # if the element is not in the variables' domain
        if element not in variable.domain:
            # raise an error
            raise ValueError(f"Element {element} not in domain {variable.domain}")

        # if the variable is continuous
        if isinstance(variable, Continuous):
            # return the element as a singleton interval
            return portion.singleton(element)

        # if the variable is discrete
        elif isinstance(variable, Discrete):
            # return the element as a set
            return (element,)
        else:
            raise TypeError(f"Unknown variable type {type(variable)}")

    def __setitem__(self, key: Union[str, Variable], value: Any):
        EventMapType.__setitem__(self, key, self.check_element(key, value))

    def encode(self) -> 'EncodedEvent':
        """
        Encode the event to an encoded event.
        :return: The encoded event
        """
        return EncodedEvent({variable: variable.encode_many(element) for variable, element in self.items()})

    def is_empty(self) -> bool:
        return any(len(value) == 0 for value in self.values()) or len(self.keys()) == 0

    def plot(self) -> Union[List[go.Scatter], List[go.Mesh3d]]:
        """
        Plot the event.
        """
        assert all(isinstance(variable, Continuous) for variable in self.keys()), "Can only plot continuous events"
        if len(self.keys()) == 2:
            return self.plot_2d()
        elif len(self.keys()) == 3:
            return self.plot_3d()
        else:
            raise ValueError("Can only plot 2D and 3D events")

    def plot_2d(self) -> List[go.Scatter]:
        """
        Plot the event in 2D.
        """

        # form cartesian product of all intervals
        intervals = [value._intervals for value in self.values()]
        simple_events = list(itertools.product(*intervals))
        traces = []

        # for every atomic interval
        for simple_event in simple_events:

            # plot a rectangle
            points = np.asarray(list(itertools.product(*[[axis.lower, axis.upper] for axis in simple_event])))
            y_points = points[:, 1]
            y_points[len(y_points) // 2:] = y_points[len(y_points) // 2:][::-1]
            traces.append(go.Scatter(x=np.append(points[:, 0], points[0, 0]), y=np.append(y_points, y_points[0]),
                                     mode="lines", name="Event", fill="toself"))
        return traces

    def plot_3d(self) -> List[go.Mesh3d]:
        """
        Plot the event in 3D.
        """

        # form cartesian product of all intervals
        intervals = [value._intervals for value in self.values()]
        simple_events = list(itertools.product(*intervals))
        traces = []

        # shortcut for the dimensions
        x, y, z = 0, 1, 2

        # for every atomic interval
        for simple_event in simple_events:

            # Create a 3D mesh trace for the rectangle
            traces.append(go.Mesh3d(
                # 8 vertices of a cube
                x=[simple_event[x].lower, simple_event[x].lower, simple_event[x].upper, simple_event[x].upper,
                   simple_event[x].lower, simple_event[x].lower, simple_event[x].upper, simple_event[x].upper],
                y=[simple_event[y].lower, simple_event[y].upper, simple_event[y].upper, simple_event[y].lower,
                   simple_event[y].lower, simple_event[y].upper, simple_event[y].upper, simple_event[y].lower],
                z=[simple_event[z].lower, simple_event[z].lower, simple_event[z].lower, simple_event[z].lower,
                   simple_event[z].upper, simple_event[z].upper, simple_event[z].upper, simple_event[z].upper],
                # i, j and k give the vertices of triangles
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                flatshading=True
            ))
        return traces

    def plotly_layout(self) -> Dict:
        """
        Create a layout for the plotly plot.
        """
        variables = list(self.keys())
        if len(variables) == 2:
            result = {"xaxis_title": variables[0].name,
                      "yaxis_title": variables[1].name}
        elif len(variables) == 3:
            result = dict(scene=dict(
                xaxis_title=variables[0].name,
                yaxis_title=variables[1].name,
                zaxis_title=variables[2].name)
            )
        else:
            raise NotImplementedError("Can only plot 2D and 3D events")

        return result

    def __hash__(self):
        return hash(tuple(sorted(self.items())))

    def fill_missing_variables(self, variables: Iterable[Variable]):
        """
        Fill missing variables with their entire domain.
        """
        for variable in variables:
            if variable not in self:
                self[variable] = variable.domain

    def decode(self):
        """
        Decode the event to a normal event.
        :return: The decoded event
        """
        return self.__copy__()

    def marginal_event(self, variables: Iterable[Variable]) -> Self:
        """
        Get the marginal event of this event with respect to a variable.
        """
        return self.__class__({variable: self[variable] for variable in variables if variable in self})


class EncodedEvent(Event):
    """
    A map of variables to indices of their respective domains.
    """

    @staticmethod
    def check_element(variable: Variable, element: Any) -> Union[tuple, portion.Interval]:

        # if the variable is continuous
        if isinstance(variable, Continuous):

            # if it's not an interval
            if not isinstance(element, portion.Interval):

                # try to convert it to one
                element = portion.singleton(element)

            return element

        # if its any kind of iterable that's not an interval convert it to a tuple
        if isinstance(element, Iterable) and not isinstance(element, portion.Interval):
            element = tuple(sorted(element))

        # if it is just an int, convert it to a tuple containing the int
        elif isinstance(element, int):
            element = (element, )

        if not isinstance(element, tuple):
            raise ValueError("Element for a discrete domain must be a tuple, not {}".format(type(element)))

        # if any element is not in the index set of the domain, raise an error
        if not all(0 <= elem < len(variable.domain) for elem in element):
            raise ValueError(f"Element {element} not in the index set of the domain {variable.domain}")

        return element

    def fill_missing_variables(self, variables: Iterable[Variable]):
        for variable in variables:
            if variable not in self:
                self[variable] = variable.encode_many(variable.domain)

    def decode(self) -> Event:
        return Event({variable: variable.decode_many(value) for variable, value in self.items()})

    def encode(self) -> Self:
        return self.__copy__()



class ComplexEvent(SupportsSetOperations):
    """
    A complex event is a set of mutually exclusive events.
    """
    events: List[Event]

    def __init__(self, events: Iterable[Event]):
        self.events = list(event for event in events if not event.is_empty())
        variables = self.variables
        for event in self.events:
            event.fill_missing_variables(variables)

    @property
    def variables(self) -> Tuple[Variable, ...]:
        """
        Get the variables of the complex event.
        """
        return tuple(sorted(set(variable for event in self.events for variable in event.keys())))

    def union(self, other: EventType) -> Self:
        if isinstance(other, Event):
            return self.union(ComplexEvent([other]))
        result = ComplexEvent(self.events + other.events)
        return result.make_events_disjoint().simplify()

    def make_events_disjoint(self) -> Self:
        """
        Make all events in this complex event disjoint.

        This is done by forming the intersection of all events recursively until no more intersections are found.
        Then, the original events are decomposed into their disjoint components.
        Finally, a complex event is formed from the disjoint components. Note that the result may not be the minimal
        representation of the complex event, so it is advised to call ``simplify`` afterward.
        """

        # initialize previous intersections
        previous_intersections = []

        # for every pair of events
        for index, event in enumerate(self.events):
            for other_event in self.events[index + 1:]:

                # append intersection of pairwise events
                intersection = event.intersection(other_event)
                if not intersection.is_empty() and intersection not in previous_intersections:
                    previous_intersections.append(intersection)

        # if there are no intersections, skip the rest
        if len(previous_intersections) == 0:
            return self

        # while
        while len(previous_intersections) > 0:

            # initialize new intersections
            new_intersections = []

            # form pairwise intersections of previous intersections
            for index, intersection in enumerate(previous_intersections):
                for other_intersection in previous_intersections[index + 1:]:
                    if not intersection.intersection(other_intersection).is_empty():
                        new_intersections.append(intersection)

            if len(new_intersections) == 0:
                break

            previous_intersections = new_intersections

        # sanity check
        complex_event_of_intersections = ComplexEvent(previous_intersections)
        assert complex_event_of_intersections.are_events_disjoint(), "Events are not disjoint"

        # initialize result
        result = ComplexEvent(complex_event_of_intersections.events)

        # for every original event
        for original_event in self.events:

            # initialize the difference of the original events with the intersection
            decomposed_original_events = set()

            # for every atomic intersection in the disjoint intersections
            for atomic_intersection in complex_event_of_intersections.events:

                # get the difference of the original event with the atomic intersection
                original_event_disjoint_component = original_event.difference(atomic_intersection)

                # unify the differences
                decomposed_original_events = decomposed_original_events.union(
                    set(original_event_disjoint_component.events))

            # add the differences to the result
            result.events.extend(decomposed_original_events)
        return result

    def simplify(self) -> Self:
        """
        Simplify the complex event such that sub-unions of events that can be expressed as a single events
        are merged.
        """

        if len(self.variables) == 1:
            return self.merge_if_one_dimensional()

        # for every pair of events
        for index, event in enumerate(self.events):
            for other_event in self.events[index + 1:]:

                # for every variable in the event
                for variable, value in event.items():

                    # if the events match in this dimension
                    if other_event[variable] == value:

                        # form the simpler union of the two events
                        unified_event = Event({variable: value})
                        for variable_ in event.keys():
                            if variable_ != variable:
                                unified_event[variable_] = variable.union_of_assignments(event[variable_],
                                                                                         other_event[variable_])
                        # recurse into the simpler complex event
                        result = ComplexEvent([])
                        result.events.append(unified_event)
                        result.events.extend([event__ for event__ in self.events if event__ != event
                                              and event__ != other_event])
                        return result.simplify()

        # if no simplification is possible, return the current complex event
        return self.__copy__()

    def intersection(self, other: EventType) -> Self:
        if isinstance(other, Event):
            return self.intersection(ComplexEvent([other]))
        intersections = [event.intersection(other_event) for other_event in other.events for event in self.events]
        return ComplexEvent(intersections)

    def difference(self, other: EventType) -> Self:
        if isinstance(other, Event):
            return self.difference(ComplexEvent([other]))
        return self.intersection(other.complement())

    def complement(self) -> Self:
        result = self.events[0].complement()
        for event in self.events[1:]:
            current_complement = event.complement()
            result = result.intersection(current_complement)
        return result.make_events_disjoint().simplify()

    def are_events_disjoint(self) -> bool:
        """
        Check if all events inside this complex event are disjoint.
        """
        for index, event in enumerate(self.events):
            for event_ in self.events[index + 1:]:
                if not event.intersection(event_).is_empty():
                    return False
        return True

    def __str__(self):
        return " u ".join(str(event) for event in self.events)

    def __repr__(self):
        return f"Union of {len(self.events)} events"

    def __eq__(self, other: ComplexEvent) -> bool:
        """
        Check if two complex events are equal.
        """
        return (all(event in other.events for event in self.events)
                and all(event in self.events for event in other.events))

    def __copy__(self):
        return self.__class__([event.copy() for event in self.events])

    def plot(self) -> Union[List[go.Scatter], List[go.Mesh3d]]:
        """
        Plot the complex event.
        """
        traces = []
        for event in self.events:
            traces.extend(event.plot())
        return traces

    def plotly_layout(self) -> Dict:
        """
        Create a layout for the plotly plot.
        """
        return self.events[0].plotly_layout()

    def is_empty(self) -> bool:
        return len(self.events) == 0

    def encode(self) -> 'ComplexEvent':
        """
        Encode the event to an encoded event.
        :return: The encoded event
        """
        return ComplexEvent([event.encode() for event in self.events])

    def decode(self) -> ComplexEvent:
        """
        Decode the event to a normal event.
        """
        return ComplexEvent([event.decode() for event in self.events])

    def marginal_event(self, variables: Iterable[Variable]) -> Self:
        """
        Get the marginal event of this complex event with respect to a variable.
        """
        return ComplexEvent([event.marginal_event(variables) for event in self.events]).simplify()

    def merge_if_one_dimensional(self) -> Self:
        """
        Merge all events into a single event if they are all one-dimensional.
        """
        if not len(self.variables) == 1:
            return self
        variable = self.variables[0]
        value = self.events[0][variable]

        for event in self.events[1:]:
            value = variable.union_of_assignments(value, event[variable])
        return ComplexEvent([Event({variable: value})])


EventType = Union[Event, EncodedEvent, ComplexEvent]
