from __future__ import annotations
from abc import abstractmethod
from typing import Tuple, Dict, Any
import random_events_lib as rl
from sortedcontainers import SortedSet
from typing_extensions import Self, Iterable, Optional, TYPE_CHECKING, Set
from .utils import SubclassJSONSerializer

EMPTY_SET_SYMBOL = "∅"


class AbstractSimpleSet(SubclassJSONSerializer):
    """
    Abstract class for simple sets.

    Simple sets are sets that can be represented as a single object.
    """

    _cpp_object: rl.AbstractSimpleSet

    @abstractmethod
    def _from_cpp(self, cpp_object):
        """
        Create a new instance of this class from a C++ object.
        """
        raise NotImplementedError

    def intersection_with(self, other: Self) -> Self:
        """
        Form the intersection of this object with another object.

        :param other: The other SimpleSet
        :return: The intersection of this set with the other set
        """
        return self._from_cpp(self._cpp_object.intersection_with(other._cpp_object))

    def complement(self) -> SimpleSetContainer:
        """
        :return: The complement of this set as disjoint set of simple sets.
        """
        return SortedSet({self._from_cpp(cpp_simple_set) for cpp_simple_set in self._cpp_object.complement()})

    def is_empty(self) -> bool:
        """
        :return: Rather this set is empty or not.
        """
        return self._cpp_object.is_empty()

    @abstractmethod
    def contains(self, item) -> bool:
        """
        Check if this set contains an item.
        :param item: The item to check
        :return: Rather if the item is in the set or not
        """
        raise NotImplementedError

    @abstractmethod
    def __hash__(self):
        raise NotImplementedError

    def non_empty_to_string(self) -> str:
        """
        :return: A string representation of this set if it is not empty.
        """
        raise NotImplementedError

    def difference_with(self, other: Self) -> SimpleSetContainer:
        """
        Form the difference of this object with another object.

        :param other: The other SimpleSet
        :return: The difference as a disjoint set of simple sets.
        """
        return self._from_cpp(self._cpp_object.difference_with(other._cpp_object))

    def to_string(self):
        """
        :return: A string representation of this set.
        """
        if self.is_empty():
            return EMPTY_SET_SYMBOL
        return self.non_empty_to_string()

    def __str__(self):
        return self.to_string()

    def __lt__(self, other: Self):
        return self._cpp_object < other._cpp_object

    @abstractmethod
    def as_composite_set(self) -> AbstractCompositeSet:
        """
        Convert this simple set to a composite set.
        :return: The composite set
        """
        raise NotImplementedError

    @abstractmethod
    def __deepcopy__(self):
        raise NotImplementedError


class AbstractCompositeSet(SubclassJSONSerializer):
    """
    Abstract class for composite sets.

    AbstractCompositeSet is a set that is composed of a disjoint union of simple sets.
    """

    simple_sets: SimpleSetContainer
    _cpp_object: rl.AbstractCompositeSet

    def __init__(self, *simple_sets):
        self.simple_sets = SortedSet(simple_sets)

    @classmethod
    @abstractmethod
    def _from_cpp(cls, cpp_object):
        raise NotImplementedError

    @abstractmethod
    def new_empty_set(self) -> Self:
        """
        Create a new empty set.

        This method has to be implemented by the subclass and should take over all the relevant attributes to the new
        set.

        :return: A new empty set.
        """
        raise NotImplementedError

    def union_with(self, other: Self) -> Self:
        """
        Form the union of this object with another object.

        :param other: The other set
        :return: The union of this set with the other set
        """
        return self._from_cpp(self._cpp_object.union_with(other._cpp_object))

    def __or__(self, other: Self):
        return self.union_with(other)

    def intersection_with_simple_set(self, other: AbstractSimpleSet) -> Self:
        """
        Form the intersection of this object with a simple set.

        :param other: The simple set
        :return: The intersection of this set with the simple set
        """
        return self._from_cpp(self._cpp_object.intersection_with_simple_set(other._cpp_object))

    def intersection_with_simple_sets(self, other: SimpleSetContainer) -> Self:
        """
        Form the intersection of this object with a set of simple sets.

        :param other: The set of simple sets
        :return: The intersection of this set with the set of simple sets
        """
        result = self.new_empty_set()
        [result.simple_sets.update(self.intersection_with_simple_set(other_simple_set).simple_sets) for other_simple_set
         in other]
        return result

    def intersection_with(self, other: Self) -> Self:
        """
        Form the intersection of this object with another object.
        :param other: The other set
        :return: The intersection of this set with the other set
        """
        return self._from_cpp(self._cpp_object.intersection_with(other._cpp_object))

    def __and__(self, other):
        return self.intersection_with(other)

    def difference_with_simple_set(self, other: AbstractSimpleSet) -> Self:
        """
        Form the difference with another composite set.
        :param other: The other set
        :return: The difference of this set with the other set
        """
        return self._from_cpp(self._cpp_object.difference_with(other._cpp_object))

    def difference_with_simple_sets(self, other: SimpleSetContainer) -> Self:
        """
        Form the difference with a set of simple sets.
        :param other: The set of simple sets
        :return: The difference of this set with the other set
        """
        result = self.new_empty_set()
        [result.simple_sets.update(self.difference_with_simple_set(other_simple_set).simple_sets) for other_simple_set
         in other]
        return result

    def difference_with(self, other: Self) -> Self:
        """
        Form the difference with another composite set.
        :param other: The other set
        :return: The difference of this set with the other set
        """
        return self._from_cpp(self._cpp_object.difference_with(other._cpp_object))

    def __sub__(self, other):
        return self.difference_with(other)

    def complement(self) -> Self:
        """
        :return: The complement of this set
        """
        return self._from_cpp(self._cpp_object.complement())

    @abstractmethod
    def complement_if_empty(self) -> Self:
        """
        :return: The complement of this if it is empty.
        """
        raise NotImplementedError

    def __invert__(self):
        return self.complement()

    def is_empty(self) -> bool:
        """
        Check if this set is empty.
        """
        return self._cpp_object.is_empty()

    def contains(self, item) -> bool:
        """
        Check if this set contains an item.
        :param item: The item to check
        :return: Rather if the item is in the set or not
        """
        for simple_set in self.simple_sets:
            if simple_set.contains(item):
                return True
        return False

    def __contains__(self, item):
        return self.contains(item)

    def to_string(self):
        """
        :return: A string representation of this set.
        """
        if self.is_empty():
            return EMPTY_SET_SYMBOL
        return " u ".join([simple_set.to_string() for simple_set in self.simple_sets])

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def is_disjoint(self):
        """
        :return: Rather if the simple sets are disjoint or not.
        """
        return self._cpp_object.is_disjoint()

    def make_disjoint(self) -> Self:
        """
        Create an equal composite set that contains a disjoint union of simple sets.

        :return: The disjoint set.
        """
        return self._from_cpp(self._cpp_object.make_disjoint())

    def add_simple_set(self, simple_set: AbstractSimpleSet):
        """
        Add a simple set to this composite set if it is not empty.

        :param simple_set: The simple set to add
        """
        if simple_set.is_empty():
            return
        self.simple_sets.add(simple_set)
        self._cpp_object.add_new_simple_set(simple_set._cpp_object)

    def simplify(self) -> Self:
        """
        Simplify this set into an equivalent, more compact version.

        :return: The simplified set
        """
        return self._from_cpp(self._cpp_object.simplify())

    def __eq__(self, other: Self):
        return self.simple_sets._list == other.simple_sets._list

    def __hash__(self):
        return hash(tuple(self.simple_sets))

    def __iter__(self):
        return iter(self.simple_sets)

    def __lt__(self, other: Self):
        """
        Compare this set with another set.

        The sets are compared by comparing the simple sets in order.
        If the pair of simple sets are equal, the next pair is compared.
        If all pairs are equal, the set with the least amount of simple sets is considered smaller.

        ..note:: This does not define a total order in the mathematical sense. In the mathematical sense, this defines
            a partial order.

        :param other: The other set
        :return: Rather this set is smaller than the other set
        """
        for a, b in zip(self.simple_sets, other.simple_sets):
            if a == b:
                continue
            else:
                return a < b
        return len(self.simple_sets) < len(other.simple_sets)

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(), "simple_sets": [simple_set.to_json() for simple_set in self.simple_sets]}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(*[AbstractSimpleSet.from_json(simple_set) for simple_set in data["simple_sets"]])

    def __deepcopy__(self):
        return self.__class__(*[ss.__deepcopy__() for ss in self.simple_sets])


# Type definitions
if TYPE_CHECKING:
    SimpleSetContainer = SortedSet[AbstractSimpleSet]
else:
    SimpleSetContainer = SortedSet
