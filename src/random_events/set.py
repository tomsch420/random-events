from __future__ import annotations
import enum

from sortedcontainers import SortedSet
from typing_extensions import Self, TYPE_CHECKING, Dict, Any

from .sigma_algebra import *


class SetElement(AbstractSimpleSet, int, enum.Enum):
    """
    Base class for enums that are used as elements in a set.

    Classes that inherit from this class have to define an attribute called EMPTY_SET.
    It is advisable to define EMPTY_SET as -1 to correctly work with indices.
    The empty set of the class is used to access all other elements of the class.
    """

    @property
    @abstractmethod
    def EMPTY_SET(self):
        """
        :return: The empty set of the class.
        """
        raise NotImplementedError("The EMPTY_SET attribute has to be defined.")

    @property
    def all_elements(self):
        return self.__class__

    def intersection_with(self, other: Self) -> Self:
        if self == other:
            return self
        else:
            return self.all_elements.EMPTY_SET

    def complement(self) -> SimpleSetContainer:
        result = SortedSet()
        for element in self.all_elements:
            if element != self and element != self.all_elements.EMPTY_SET:
                result.add(element)
        return result

    def is_empty(self) -> bool:
        return self == self.EMPTY_SET

    def contains(self, item: Self) -> bool:
        return self == item

    def non_empty_to_string(self) -> str:
        return self.name

    def __hash__(self):
        return enum.Enum.__hash__(self)

    def __lt__(self, other):
        return self.value < other.value

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(), "value": self.value}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(data["value"])

    def as_composite_set(self) -> AbstractCompositeSet:
        return Set(self)


class Set(AbstractCompositeSet):
    simple_sets: SetElementContainer

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("I don't know how to do this yet.")

    def simplify(self) -> Self:
        return self

    def new_empty_set(self) -> Self:
        return Set()

    def make_disjoint(self) -> Self:
        return self


# Type definitions
if TYPE_CHECKING:
    SetElementContainer = SortedSet[SetElement]
else:
    SetElementContainer = SortedSet
