import enum
from abc import abstractmethod

from sortedcontainers import SortedSet
from typing_extensions import Self

from . import sigma_algebra


class SetElement(sigma_algebra.AbstractSimpleSet, enum.Enum):
    """
    Base class for enums that are used as elements in a set.

    Classes that inherit from this class have to define an attribute called EMPTY_SET.
    """

    @property
    @abstractmethod
    def EMPTY_SET(self):
        raise NotImplementedError

    @property
    def all_elements(self):
        return self.__class__

    def intersection_with(self, other: Self) -> Self:
        if self == other:
            return self
        else:
            return self.all_elements.EMPTY_SET

    def complement(self) -> SortedSet[Self]:
        result = SortedSet()
        for element in self.all_elements:
            if element != self and element != self.all_elements.EMPTY_SET:
                result.add(element)
        return result

    def is_empty(self) -> bool:
        return self is self.all_elements.EMPTY_SET

    def contains(self, item: Self) -> bool:
        return self == item

    def non_empty_to_string(self) -> str:
        return self.name

    def __hash__(self):
        return enum.Enum.__hash__(self)

    def __lt__(self, other):
        return self.value < other.value


class Set(sigma_algebra.AbstractCompositeSet):

    simple_sets: SortedSet[SetElement]

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("I don't know how to do this yet.")

    def simplify(self) -> Self:
        return self

    def new_empty_set(self) -> Self:
        return Set([])
