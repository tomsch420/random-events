from __future__ import annotations
from .sigma_algebra import *
import random_events_lib as rl


class SetElement(AbstractSimpleSet):
    """
    Represents a SetElement.
    """

    def __init__(self, element: str, all_elements: set):
        """
        Create a new set element.
        :param element: The element of the set.
        :param all_elements: The set of all elements.
        """
        self.all_elements = SortedSet(all_elements)
        if element == EMPTY_SET_SYMBOL or element == -1:
            self.element = EMPTY_SET_SYMBOL
            self._cpp_object = rl.SetElement(list(self.all_elements))
        elif element not in self.all_elements:
            raise ValueError(f"Element {element} is not in the set of all elements.")
        else:
            self.element = element
            self._cpp_object = rl.SetElement(self.all_elements.index(element), list(self.all_elements))

    @classmethod
    def _from_cpp(cls, cpp_object):
        if cpp_object.element_index == -1:
            return SetElement(EMPTY_SET_SYMBOL, set())
        return cls(list(SortedSet(cpp_object.all_elements))[cpp_object.element_index], cpp_object.all_elements)

    def contains(self, item: Self) -> bool:
        return self == item

    def non_empty_to_string(self) -> str:
        return self.element

    def __hash__(self):
        return hash((self.element, tuple(self.all_elements)))

    def __lt__(self, other):
        return self.element < other.element

    def __eq__(self, other):
        if self.element == other.element:
            return True
        return False

    def __repr__(self):
        return self.non_empty_to_string()

    def __iter__(self):
        return iter(self.all_elements)

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(), "value": self.element, "content": self.all_elements}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(data["value"], data["content"])

    def as_composite_set(self) -> AbstractCompositeSet:
        return Set(self)


class Set(AbstractCompositeSet):
    """
    Represents a set.
    """

    simple_sets: SetElementContainer
    """
    The simple sets that make up the set.
    """

    def __init__(self, *simple_sets):
        """
        Create a new set.
        :param simple_sets: The simple sets that make up the set.
        """
        super().__init__(*simple_sets)
        if len(simple_sets) > 0:
            self._cpp_object = rl.Set({simple_set._cpp_object for simple_set in self.simple_sets},
                                      self.simple_sets[0]._cpp_object.all_elements)
        else:
            self._cpp_object = rl.Set(set(), set())


    @classmethod
    def _from_cpp(cls, cpp_object):
        return cls(*[SetElement._from_cpp(cpp_simple_set) for cpp_simple_set in cpp_object.simple_sets])

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("I don't know how to do this yet.")

    def new_empty_set(self) -> Self:
        return Set()


# Type definitions
if TYPE_CHECKING:
    SetElementContainer = SortedSet[SetElement]
else:
    SetElementContainer = SortedSet
