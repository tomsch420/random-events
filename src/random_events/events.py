from __future__ import annotations

from collections import UserDict
from typing import TYPE_CHECKING, Iterable
from typing import Union, Any

import portion

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


# Type hinting for Python 3.7 to 3.9
if TYPE_CHECKING:
    EventMapType = VariableMap[str, Union[tuple, portion.Interval]]
else:
    EventMapType = VariableMap


class Event(EventMapType):
    """
    A map of variables to values of their respective domains.
    """

    def intersection(self, other: 'Event') -> 'Event':
        """
        Get the intersection of this and another event.

        If one variable is only in one of the events, it is assumed that the other does not constrain it.

        :return: The intersection
        """
        result = Event()

        variables = set(self.keys()) | set(other.keys())

        for variable in variables:

            if isinstance(variable, Discrete):

                # get the entire domain
                value = set(variable.domain)

                # intersect with the constraint of self
                if variable in self:
                    value &= set(self[variable])

                # intersect with the constraint of other
                if variable in other:
                    value &= set(other[variable])

                # convert back to tuple
                value = tuple(sorted(value))

            # if the variable is continuous
            elif isinstance(variable, Continuous):

                # get the entire domain
                value = variable.domain

                # intersect with the constraint of self
                if variable in self:
                    value &= self[variable]

                # intersect with the constraint of other
                if variable in other:
                    value &= other[variable]

            else:
                raise TypeError(f"Unknown variable type {type(variable)}")

            result[variable] = value

        return result

    __and__ = intersection
    """Alias for intersection."""

    def union(self, other: 'Event') -> 'Event':
        """
        Get the union of this and another event.

        If one variable is only in one of the events, the union is the corresponding element.
        """
        result = Event()

        variables = set(self.keys()) | set(other.keys())

        for variable in variables:

            if isinstance(variable, Discrete):

                # get the entire domain
                value = set()

                # intersect with the constraint of self
                if variable in self:
                    value |= set(self[variable])

                # intersect with the constraint of other
                if variable in other:
                    value |= set(other[variable])

                # convert back to tuple
                value = tuple(sorted(value))

            # if the variable is continuous
            elif isinstance(variable, Continuous):

                # get the entire domain
                value = portion.empty()

                # intersect with the constraint of self
                if variable in self:
                    value |= self[variable]

                # intersect with the constraint of other
                if variable in other:
                    value |= other[variable]

            else:
                raise TypeError(f"Unknown variable type {type(variable)}")

            result[variable] = value

        return result

    __or__ = union
    """Alias for union."""

    def difference(self, other: 'Event') -> 'Event':
        """
        Get the difference of this and another event.

        If a variable appears only in `other`, it is assumed that `self` has the entire domain as default value.
        """
        result = Event()

        variables = set(self.keys()) | set(other.keys())

        for variable in variables:

            if isinstance(variable, Discrete):

                # intersect with the constraint of self
                if variable in self:
                    value = set(self[variable])
                else:
                    value = set(variable.domain)

                # intersect with the constraint of other
                if variable in other:
                    value -= set(other[variable])

                # convert back to tuple
                value = tuple(sorted(value))

            # if the variable is continuous
            elif isinstance(variable, Continuous):

                # intersect with the constraint of self
                if variable in self:
                    value = self[variable]
                else:
                    value = portion.open(-portion.inf, portion.inf)

                # intersect with the constraint of other
                if variable in other:
                    value -= other[variable]

            else:
                raise TypeError(f"Unknown variable type {type(variable)}")

            result[variable] = value

        return result

    __sub__ = difference
    """Alias for difference."""

    def complement(self) -> 'Event':
        """
        Get the complement of this event.
        """
        return Event() - self

    __invert__ = complement
    """Alias for complement."""

    def __eq__(self, other: 'Event') -> bool:
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
        super().__setitem__(key, self.check_element(key, value))

    def encode(self) -> 'EncodedEvent':
        """
        Encode the event to an encoded event.
        :return: The encoded event
        """
        return EncodedEvent({variable: variable.encode_many(element) if isinstance(variable, Discrete) else element for
                             variable, element in self.items()})

    def is_empty(self) -> bool:
        """
        Check if this event is empty
        """
        return any(len(value) == 0 for value in self.values())


class EncodedEvent(Event):
    """
    A map of variables to indices of their respective domains.
    """

    @staticmethod
    def check_element(variable: Variable, element: Any) -> Union[tuple, portion.Interval]:

        if isinstance(element, Iterable) and not isinstance(element, (str, portion.Interval)):
            element = tuple(element)

        # if the element is already wrapped
        if isinstance(element, (tuple, portion.Interval)):

            # check that the element is in the variable's domain
            if isinstance(variable, Discrete):
                if not all(0 <= elem < len(variable.domain) for elem in element):
                    # raise an error
                    raise ValueError(f"Element {element} not in domain {variable.domain}")

                element = tuple(sorted(element))
            # return the element directly
            return element

        # if the variable is continuous
        if isinstance(variable, Continuous):

            if element not in variable.domain:
                # raise an error
                raise ValueError(f"Element {element} not in domain {variable.domain}")

            # return the element as a singleton interval
            return portion.singleton(element)

        # if the variable is discrete
        elif isinstance(variable, Discrete):

            # if the element is not in the variables' domain
            if 0 <= element < len(variable.domain):
                # raise an error
                raise ValueError(f"Element {element} not in domain {variable.domain}")

            # return the element as a set
            return (element,)
        else:
            raise TypeError(f"Unknown variable type {type(variable)}")

    def decode(self) -> Event:
        """
        Decode the event to a normal event.
        :return: The decoded event
        """
        return Event(
            {variable: variable.decode_many(index) if isinstance(variable, Discrete) else index for variable, index in
             self.items()})
