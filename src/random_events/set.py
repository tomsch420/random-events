from __future__ import annotations

from functools import cached_property

from typing_extensions import Union, Hashable

from .sigma_algebra import *
import random_events_lib as rl

HashMap: Dict[int, Hashable]
AllElements: Tuple[Hashable]

class SetElement(AbstractSimpleSet):
    """
    Represents a SetElement.
    """

    _cpp_object: rl.SetElement
    all_elements: AllElements

    def __init__(self, element: Optional[Hashable], all_elements: Iterable[Hashable]):
        """
        Create a new set element.
        :param element: The element of the set.
        :param all_elements: The set of all elements.
        """
        self.all_elements = tuple(all_elements)

        if element is not None and element not in self.all_elements:
            raise ValueError(f"Element {element} is not in the set of all elements. "
                             f"All elements: {self.all_elements}")
        else:
            self.element = element

        if element is None:
            self.element_index = -1
            self._cpp_object = rl.SetElement(set())
        else:
            self.element_index = self.all_elements.index(element)
            self._cpp_object = rl.SetElement(self.element_index, set(self.hash_map.keys()))

    @cached_property
    def hash_map(self) -> HashMap:
        """
        :return:A map that maps the hashes of each element in all_elements to the element.
        """
        return {hash(elem): elem for elem in self.all_elements}

    def _from_cpp(self, cpp_object):
        if cpp_object.element_index == -1:
            return SetElement(None, set())
        return SetElement(self.all_elements[cpp_object.element_index], self.all_elements)

    def contains(self, item: Self) -> bool:
        return self == item

    def non_empty_to_string(self) -> str:
        return str(self.element)

    def __hash__(self):
        return hash(self.element)

    def __eq__(self, other):
        return self.element == other.element

    def __repr__(self):
        return self.non_empty_to_string()

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(), "value": self.element, "content": list(self.all_elements)}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(data["value"], data["content"])

    def as_composite_set(self) -> AbstractCompositeSet:
        return Set(self)

    def __deepcopy__(self):
        return SetElement(self.element, self.all_elements)

class Set(AbstractCompositeSet):
    """
    Represents a set.
    """

    simple_set_example: SetElement
    _cpp_object: rl.Set
    all_elements: Tuple[Hashable]

    def __init__(self, *simple_sets):
        """
        Create a new set.
        :param simple_sets: The simple sets that make up the set.
        """
        if len(simple_sets) > 0:
            self.simple_set_example = simple_sets[0]
            self._cpp_object = rl.Set({simple_set._cpp_object for simple_set in simple_sets},
                                      self.simple_set_example._cpp_object.all_elements)
            self.all_elements = simple_sets[0].all_elements

        else:
            self._cpp_object = rl.Set(set(), set())
            self.all_elements = tuple()

    def _from_cpp(self, cpp_object):
        return Set(*[self.simple_set_example._from_cpp(cpp_simple_set) for cpp_simple_set in cpp_object.simple_sets])

    @classmethod
    def from_iterable(cls, iterable: Iterable) -> Self:
        all_elements = set(iterable)
        return cls(*[SetElement(elem, all_elements) for elem in all_elements])

    @property
    def hash_map(self) -> HashMap:
        return {hash(elem): elem for elem in self.all_elements}



# Type definitions
if TYPE_CHECKING:
    SetElementContainer = SortedSet[SetElement]
else:
    SetElementContainer = SortedSet
