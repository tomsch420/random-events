from __future__ import annotations
import enum
import math
from typing import Dict, Any
from sortedcontainers import SortedSet
from typing_extensions import Self
from . import sigma_algebra
import random_events_lib as rl


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

    def __init__(self, lower: float = 0, upper: float = 0, left: Bound = Bound.OPEN, right: Bound = Bound.OPEN):
        """
        Creates a new simple interval.
        :param lower: The lower bound of the interval.
        :param upper: The upper bound of the interval.
        :param left: The bound type of the lower bound.
        :param right: The bound type of the upper bound.
        """
        self.lower = lower
        self.upper = upper
        self.left = left
        self.right = right

        self._cpp_object = rl.SimpleInterval(lower, upper, left.value, right.value)

    @classmethod
    def _from_cpp(cls, cpp_object: rl.SimpleInterval) -> Self:
        return cls(cpp_object.lower, cpp_object.upper, Bound(cpp_object.left.value), Bound(cpp_object.right.value))

    def as_composite_set(self) -> Interval:
        return Interval(self)

    def __lt__(self, other: Self):
        if self.lower == other.lower:
            return self.upper < other.upper
        return self.lower < other.lower

    def __eq__(self, other: Self):
        return self.lower == other.lower and self.upper == other.upper and self.left == other.left and self.right == other.right

    def is_singleton(self) -> bool:
        """
        :return: True if the interval is a singleton (contains only one value), False otherwise.
        """
        return self.lower == self.upper and self.left == Bound.CLOSED and self.right == Bound.CLOSED

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
        return (self.lower + self.upper) / 2

    def contained_integers(self) -> int:
        """
        :return: Yield integers contained in the interval
        """

        rounded_lower = math.ceil(self.lower)
        if rounded_lower == self.lower and self.left == Bound.OPEN:
            rounded_lower += 1

        rounded_upper = math.floor(self.upper)
        if rounded_upper == self.upper and self.right == Bound.OPEN:
            rounded_upper -= 1

        yield from range(rounded_lower, rounded_upper + 1)

    def __deepcopy__(self):
        return self.__class__(self.lower, self.upper, self.left, self.right)


class Interval(sigma_algebra.AbstractCompositeSet):
    """
    Represents an interval.
    """
    simple_sets: SortedSet[SimpleInterval]

    def __init__(self, *simple_sets):
        """
        Creates a new interval.
        :param simple_sets: The simple intervals that make up the interval.
        """
        super().__init__(*simple_sets)
        self._cpp_object = rl.Interval({simple_set._cpp_object for simple_set in self.simple_sets})

    @classmethod
    def _from_cpp(cls, cpp_object: rl.Interval) -> Self:
        return cls(*[SimpleInterval._from_cpp(cpp_simple_interval) for cpp_simple_interval in cpp_object.simple_sets])

    def new_empty_set(self) -> Self:
        return Interval()

    def complement_if_empty(self) -> Self:
        return Interval([SimpleInterval(float('-inf'), float('inf'), Bound.OPEN, Bound.OPEN)])

    def is_singleton(self):
        """
        :return: True if the interval is a singleton (contains only one value), False otherwise.
        """
        return len(self.simple_sets) == 1 and self.simple_sets[0].is_singleton()

    def contained_integers(self) -> int:
        """
        :return: Yield integers contained in the interval
        """
        for simple_set in self.simple_sets:
            yield from simple_set.contained_integers()


def open(left: float, right: float) -> Interval:
    """
    Creates an open interval.

    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The open interval.
    """
    return Interval._from_cpp(rl.open(left, right))


def closed(left: float, right: float) -> Interval:
    """
    Creates a closed interval.

    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The closed interval.
    """
    return Interval._from_cpp(rl.closed(left, right))


def open_closed(left: float, right: float) -> Interval:
    """
    Creates an open-closed interval.

    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The open-closed interval.
    """
    return Interval._from_cpp(rl.open_closed(left, right))


def closed_open(left: float, right: float) -> Interval:
    """
    Creates a closed-open interval.

    :param left: The left bound of the interval.
    :param right: The right bound of the interval.
    :return: The closed-open interval.
    """
    return Interval._from_cpp(rl.closed_open(left, right))


def singleton(value: float) -> Interval:
    """
    Creates a singleton interval.

    :param value: The value of the interval.
    :return: The singleton interval.
    """
    return Interval._from_cpp(rl.singleton(value))


def reals() -> Interval:
    """
    Creates the set of real numbers.

    :return: The set of real numbers.
    """
    return Interval._from_cpp(rl.reals())
