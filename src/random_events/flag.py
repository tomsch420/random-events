from __future__ import annotations

from typing_extensions import Type

from .sigma_algebra import *
from .utils import get_full_class_name

from enum import Flag, IntFlag


class Set(AbstractCompositeSet, IntFlag):
    """
    Experimental flag implementation.
    """

    # int flag overload block
    __init__ = IntFlag.__init__
    __or__ = IntFlag.__or__
    __and__ = IntFlag.__and__
    __sub__ = IntFlag.__sub__
    __xor__ = IntFlag.__xor__
    __eq__ = IntFlag.__eq__
    __hash__ = IntFlag.__hash__
    __contains__ = IntFlag.__contains__

    @classmethod
    @property
    def EMPTY_SET(cls) -> Self:
        return cls(0)

    def to_string(self):
        return IntFlag.__str__(self)

    def complement_if_empty(self) -> Self:
        return ~self.EMPTY_SET

    def intersection_with(self, other: Self) -> Self:
        return self & other

    def complement(self) -> Self:
        result = self.EMPTY_SET
        for element in self.__class__:
            if element not in self:
                result |= element
        return result

    def union_with(self, other: Self) -> Self:
        return self | other

    @property
    def simple_sets(self) -> SortedSet[AbstractSimpleSet]:
        return SimpleSetContainer([element for element in self.__class__ if element in self])

    def is_empty(self) -> bool:
        return self == self.EMPTY_SET

    def __lt__(self, other):
        return int(self) < int(other)

    def as_composite_set(self) -> Self:
        return self

    def simplify(self) -> Self:
        return self

    def new_empty_set(self) -> Self:
        raise NotImplementedError("This method should not be called due to Flag operations.")

    def make_disjoint(self) -> Self:
        return self

    def to_json(self) -> Dict[str, Any]:
        return {**SubclassJSONSerializer.to_json(self),
                "simple_set_class": self.simple_sets[0].cls_to_json(),
                "simple_set_indices": list(map(lambda item: int(item), self.simple_sets))}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        simple_set_class = SetElement.cls_from_json(data["simple_set_class"])
        simple_sets = [simple_set_class(index) for index in data["simple_set_indices"]]
        return cls(*simple_sets)
