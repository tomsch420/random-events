from __future__ import annotations

import enum

from typing_extensions import Type

from .sigma_algebra import *
from .utils import get_full_class_name


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

    @classmethod
    def cls_to_json(cls) -> Dict[str, Any]:
        return {"class_name": cls.__name__, "content": dict(map(lambda item: (item.name, item.value), cls))}

    @classmethod
    def cls_from_json(cls, data: Dict[str, Any]) -> Type[enum.Enum]:
        return cls(data["class_name"], data["content"])

    def to_json(self) -> Dict[str, Any]:
        return {"type": get_full_class_name(SetElement), "value": self.value,
                **self.cls_to_json()}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        deserialized_class = cls.cls_from_json(data)
        return deserialized_class(data["value"])

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

    def to_json(self) -> Dict[str, Any]:
        return {**SubclassJSONSerializer.to_json(self),
                "simple_set_class": self.simple_sets[0].cls_to_json(),
                "simple_set_indices": list(map(lambda item: int(item), self.simple_sets))}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        simple_set_class = SetElement.cls_from_json(data["simple_set_class"])
        simple_sets = [simple_set_class(index) for index in data["simple_set_indices"]]
        return cls(*simple_sets)


# Type definitions
if TYPE_CHECKING:
    SetElementContainer = SortedSet[SetElement]
else:
    SetElementContainer = SortedSet
