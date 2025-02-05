from __future__ import annotations

from typing_extensions import Union

from .sigma_algebra import *
import random_events_lib as rl


class SetElement(AbstractSimpleSet):
    """
    Represents a SetElement.
    """

    def __init__(self, element, all_elements: Union[Set, SortedSet]):
        """
        Create a new set element.
        :param element: The element of the set. Can be a string, integer, float, or double.
        :param all_elements: The set of all elements.
        """
        self.all_elements = SortedSet(all_elements)
        self.hash_map = {hash(elem): elem for elem in self.all_elements}
        if element == EMPTY_SET_SYMBOL or element == -1:
            self.element = EMPTY_SET_SYMBOL
            self._cpp_object = rl.SetElement(set(self.hash_map.keys()))
        elif element not in self.all_elements:
            raise ValueError(f"Element {element} is not in the set of all elements.")
        else:
            self.element = element
            self.element_index = self.all_elements.index(element)
            self._cpp_object = rl.SetElement(self.element_index, set(self.hash_map.keys()))

    def _from_cpp(self, cpp_object):
        if cpp_object.element_index == -1:
            return SetElement(-1, set())
        return SetElement(list(self.hash_map.values())[cpp_object.element_index], self.all_elements)

    def contains(self, item: Self) -> bool:
        return self == item

    def non_empty_to_string(self) -> str:
        return str(self.element)

    def __hash__(self):
        return hash(self.element)

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
        return {**super().to_json(), "value": self.element, "content": list(self.all_elements)}

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


    def _from_cpp(self, cpp_object):
        return Set(*[self.simple_sets[0]._from_cpp(cpp_simple_set) for cpp_simple_set in cpp_object.simple_sets])

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("I don't know how to do this yet.")

    def new_empty_set(self) -> Self:
        return Set()

    @classmethod
    def from_iterable(cls, iterable: Iterable) -> Self:
        all_elements = set(iterable)
        return cls(*[SetElement(elem, all_elements) for elem in all_elements])

    @property
    def hash_map(self):
        """
        :return: A map that maps the hashes of each simple set in this to the simple set.
        """
        return {hash(elem): elem for elem in self.simple_sets}

    @property
    def all_elements(self):
        if not self.is_empty():
            return self.simple_sets[0].all_elements
        else:
            raise ValueError("The set is empty. All elements are only avialable for non-empty composite sets.")



# Type definitions
if TYPE_CHECKING:
    SetElementContainer = SortedSet[SetElement]
else:
    SetElementContainer = SortedSet
