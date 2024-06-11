from __future__ import annotations
import enum
from dataclasses import dataclass
from typing import Dict, Any

from sortedcontainers import SortedSet
from typing_extensions import Self

from . import sigma_algebra
from .sigma_algebra import AbstractCompositeSet


class Bound(enum.Enum):
    """
    Enumerates the possible bounds for an interval.
    """

    CLOSED = 0
    """
    Represents a closed bound, i. e. the element is included from the interval.
    """

    OPEN = 1
    """
    Represents an open bound, i. e. the element is excluded in the interval.
    """

    def invert(self):
        return Bound.CLOSED if self == Bound.OPEN else Bound.OPEN

    def intersect(self, other: Self) -> Self:
        """
        Intersect with another border

        :param other: The other border
        :return: The intersection of the two borders
        """
        return Bound.OPEN if self == Bound.OPEN or other == Bound.OPEN else Bound.CLOSED


@dataclass
class SimpleInterval(sigma_algebra.AbstractSimpleSet):
    """
    Represents a simple interval.
    """

    lower: float = 0
    """
    The lower bound of the interval.
    """

    upper: float = 0
    """
    The upper bound of the interval.
    """

    left: Bound = Bound.OPEN
    """
    The bound type of the lower bound.
    """

    right: Bound = Bound.OPEN
    """
    The bound type of the upper bound.
    """

    def as_composite_set(self) -> Interval:
        return Interval(self)

    def __lt__(self, other: Self):
        if self.lower == other.lower:
            return self.upper < other.upper
        return self.lower < other.lower

    def is_empty(self) -> bool:
        return self.lower > self.upper or (
                self.lower == self.upper and (self.left == Bound.OPEN or self.right == Bound.OPEN))

    def is_singleton(self) -> bool:
        """
        :return: True if the interval is a singleton (contains only one value), False otherwise.
        """
        return self.lower == self.upper and self.left == Bound.CLOSED and self.right == Bound.CLOSED

    def intersection_with(self, other: Self) -> Self:

        # create new limits for the intersection
        new_lower = max(self.lower, other.lower)
        new_upper = min(self.upper, other.upper)

        # if the new limits are not valid, return an empty interval
        if new_lower > new_upper:
            return SimpleInterval()

        # create the new left bound
        if self.lower == other.lower:
            new_left = self.left.intersect(other.left)
        else:
            new_left = self.left if self.lower > other.lower else other.left

        # create the new right bound
        if self.upper == other.upper:
            new_right = self.right.intersect(other.right)
        else:
            new_right = self.right if self.upper < other.upper else other.right

        return SimpleInterval(new_lower, new_upper, new_left, new_right)

    def complement(self) -> SortedSet[Self]:

        # if the interval is empty
        if self.is_empty():
            # return the real line
            return SortedSet([SimpleInterval(float('-inf'), float('inf'), Bound.OPEN, Bound.OPEN)])

        # initialize the result
        result = SortedSet()

        # if this is the real line
        if self.lower == float('-inf') and self.upper == float('inf'):
            # return the empty set
            return result

        # if the lower bound is not negative infinity
        if self.lower > float('-inf'):
            # add the interval from minus infinity to the lower bound
            result.add(SimpleInterval(float('-inf'), self.lower, Bound.OPEN, self.left.invert()))

        # if the upper bound is not positive infinity
        if self.upper < float('inf'):
            # add the interval from the upper bound to infinity
            result.add(SimpleInterval(self.upper, float('inf'), self.right.invert(), Bound.OPEN))

        return result

    def contains(self, item: float) -> bool:
        return (self.lower < item < self.upper or (self.lower == item and self.left == Bound.CLOSED) or (
                self.upper == item and self.right == Bound.CLOSED))

    def __hash__(self):
        return hash((self.lower, self.upper, self.left, self.right))

    def non_empty_to_string(self) -> str:
        left_bracket = '[' if self.left == Bound.CLOSED else '('
        right_bracket = ']' if self.right == Bound.CLOSED else ')'
        return f'{left_bracket}{self.lower}, {self.upper}{right_bracket}'

    def __repr__(self):
        return sigma_algebra.AbstractSimpleSet.to_string(self)

    def __str__(self):
        return sigma_algebra.AbstractSimpleSet.to_string(self)

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(), 'lower': self.lower, 'upper': self.upper, 'left': self.left.name,
                'right': self.right.name}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(data['lower'], data['upper'], Bound[data['left']], Bound[data['right']])

    def center(self) -> float:
        """
        :return: The center point of the interval
        """
        return ((self.lower + self.upper) / 2) + self.lower


class Interval(sigma_algebra.AbstractCompositeSet):
    simple_sets: SortedSet[SimpleInterval]

    def simplify(self) -> Self:

        # if the set is empty, return it
        if self.is_empty():
            return self

        # initialize the result
        result = self.simple_sets[0].as_composite_set()

        # iterate over the simple sets
        for current_simple_interval in self.simple_sets[1:]:

            # get the last element in the result
            last_simple_interval = result.simple_sets[-1]

            # if the borders are connected
            if (last_simple_interval.upper > current_simple_interval.lower or (
                    last_simple_interval.upper == current_simple_interval.lower and not (
                    last_simple_interval.right == Bound.OPEN and current_simple_interval.left == Bound.OPEN))):

                # extend the upper bound of the last element
                last_simple_interval.upper = current_simple_interval.upper
                last_simple_interval.right = current_simple_interval.right
            else:

                # add the current element to the result
                result.simple_sets.add(current_simple_interval)

        return result

    def new_empty_set(self) -> Self:
        return Interval()

    def complement_if_empty(self) -> Self:
        return Interval([SimpleInterval(float('-inf'), float('inf'), Bound.OPEN, Bound.OPEN)])

    def is_singleton(self):
        """
        :return: True if the interval is a singleton (contains only one value), False otherwise.
        """
        return len(self.simple_sets) == 1 and self.simple_sets[0].is_singleton()


def open(left: float, right: float) -> Interval:
    """
    Creates an open interval.
    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The open interval.
    """
    return SimpleInterval(left, right, Bound.OPEN, Bound.OPEN).as_composite_set()


def closed(left: float, right: float) -> Interval:
    """
    Creates a closed interval.
    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The closed interval.
    """
    return SimpleInterval(left, right, Bound.CLOSED, Bound.CLOSED).as_composite_set()


def open_closed(left: float, right: float) -> Interval:
    """
    Creates an open-closed interval.
    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The open-closed interval.
    """
    return SimpleInterval(left, right, Bound.OPEN, Bound.CLOSED).as_composite_set()


def closed_open(left: float, right: float) -> Interval:
    """
    Creates a closed-open interval.
    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The closed-open interval.
    """
    return SimpleInterval(left, right, Bound.CLOSED, Bound.OPEN).as_composite_set()


def singleton(value: float) -> Interval:
    """
    Creates a singleton interval.
    :param value: The value of the interval.
    :return: The singleton interval.
    """
    return SimpleInterval(value, value, Bound.CLOSED, Bound.CLOSED).as_composite_set()


def reals() -> Interval:
    """
    Creates the set of real numbers.
    :return: The set of real numbers.
    """
    return SimpleInterval(float('-inf'), float('inf'), Bound.OPEN, Bound.OPEN).as_composite_set()
