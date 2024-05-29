import itertools
from abc import abstractmethod
from typing import Tuple

from typing_extensions import Self, Set, Iterable, Optional
from sortedcontainers import SortedSet

EMPTY_SET_SYMBOL = "∅"


class AbstractSimpleSet:
    """
    Abstract class for simple sets.

    Simple sets are sets that can be represented as a single object.
    """

    @abstractmethod
    def intersection_with(self, other: Self) -> Self:
        """
        Form the intersection of this object with another object.

        :param other: The other SimpleSet
        :return: The intersection of this set with the other set
        """
        raise NotImplementedError

    @abstractmethod
    def complement(self) -> SortedSet[Self]:
        """
        :return: The complement of this set as disjoint set of simple sets.
        """
        raise NotImplementedError

    @abstractmethod
    def is_empty(self) -> bool:
        """
        :return: Rather this set is empty or not.
        """
        raise NotImplementedError

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

    def difference_with(self, other: Self) -> SortedSet[Self]:
        """
        Form the difference of this object with another object.

        :param other: The other SimpleSet
        :return: The difference as disjoint set of simple sets.
        """

        # if the intersection is empty
        intersection = self.intersection_with(other)
        if intersection.is_empty():
            # then the difference is the set itself
            return SortedSet([self])

        # form the complement of the intersection
        complement_of_intersection = intersection.complement()

        # for every element in the complement of the intersection
        result = SortedSet()
        for element in complement_of_intersection:

            # if it intersects with this set
            intersection = element.intersection_with(self)
            if not intersection.is_empty():

                # add the intersection to the result
                result.add(intersection)

        return result

    def to_string(self):
        """
        :return: A string representation of this set.
        """
        if self.is_empty():
            return EMPTY_SET_SYMBOL
        return self.non_empty_to_string()

    def __str__(self):
        return self.to_string()

    @abstractmethod
    def __lt__(self, other):
        raise NotImplementedError


class AbstractCompositeSet:
    """
    Abstract class for composite sets.

    AbstractCompositeSet is a set that is composed of a disjoint union of simple sets.
    """

    simple_sets: SortedSet[AbstractSimpleSet]

    def __init__(self, simple_sets: Optional[Iterable[AbstractSimpleSet]] = None):
        self.simple_sets = SortedSet(simple_sets)

    @abstractmethod
    def simplify(self) -> Self:
        """
        Simplify this set into an equivalent, more compact version.

        :return: The simplified set
        """
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
        result = self.new_empty_set()
        result.simple_sets.update(self.simple_sets)
        result.simple_sets.update(other.simple_sets)
        return result.make_disjoint()

    def __or__(self, other: Self):
        return self.union_with(other)

    def intersection_with_simple_set(self, other: AbstractSimpleSet) -> Self:
        """
        Form the intersection of this object with a simple set.

        :param other: The simple set
        :return: The intersection of this set with the simple set
        """
        result = self.new_empty_set()
        [result.add_simple_set(simple_set.intersection_with(other)) for simple_set in self.simple_sets]
        return result

    def intersection_with(self, other: Self) -> Self:
        """
        Form the intersection of this object with another object.
        :param other: The other set
        :return: The intersection of this set with the other set
        """
        result = self.new_empty_set()
        [result.simple_sets.update(self.intersection_with_simple_set(other_simple_set).simple_sets)
         for other_simple_set in other.simple_sets]
        return result

    def __and__(self, other):
        return self.intersection_with(other)

    def difference_with_simple_set(self, other: AbstractSimpleSet) -> Self:
        """
        Form the difference with another composite set.
        :param other: The other set
        :return: The difference of this set with the other set
        """
        result = self.new_empty_set()
        [result.simple_sets.update(simple_set.difference_with(other)) for simple_set in self.simple_sets]
        return result.make_disjoint()

    def difference_with(self, other: Self) -> Self:
        """
        Form the difference with another composite set.
        :param other: The other set
        :return: The difference of this set with the other set
        """

        # initialize the result
        result = self.new_empty_set()

        # for every simple set in this set
        for own_simple_set in self.simple_sets:

            # initialize the current difference
            current_difference = self.new_empty_set()
            first_iteration = True

            # for every simple set in the other set
            for other_simple_set in other.simple_sets:

                # form the element wise difference
                difference_with_other_simple_set = own_simple_set.difference_with(other_simple_set)

                # if this is the first iteration
                if first_iteration:
                    # just copy the element wise difference
                    current_difference.simple_sets.update(difference_with_other_simple_set)
                    first_iteration = False
                    continue

                # form the intersection of the current difference with the element wise difference
                difference = self.new_empty_set()
                difference.simple_sets.update(difference_with_other_simple_set)
                current_difference = current_difference.intersection_with(difference)

            # add the current difference to the result
            result.simple_sets.update(current_difference.simple_sets)

        return result.make_disjoint()

    def __sub__(self, other):
        return self.difference_with(other)

    def complement(self) -> Self:
        """
        :return: The complement of this set
        """
        result = self.new_empty_set()
        first_iteration = True
        for simple_set in self.simple_sets:
            if first_iteration:
                result = simple_set.complement()
                first_iteration = False
            else:
                result = result.intersection_with(simple_set.complement())
        return result.make_disjoint()

    def __invert__(self):
        return self.complement()

    def is_empty(self) -> bool:
        """
        Check if this set is empty.
        """
        return len(self.simple_sets) == 0

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
        return "{" + " u ".join([simple_set.to_string() for simple_set in self.simple_sets]) + "}"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()

    def is_disjoint(self):
        """
        :return: Rather if the simple sets are disjoint or not.
        """
        for a, b in itertools.combinations(self.simple_sets, 2):
            if not a.intersection_with(b).is_empty():
                return False
        return True

    def split_into_disjoint_and_non_disjoint(self) -> Tuple[Self, Self]:
        """
        Split this composite set into disjoint and non-disjoint parts.

        This method is required for making the composite set disjoint.
        The partitioning is done by removing every other simple set from every simple set.
        The purified simple sets are then disjoint by definition and the pairwise intersections are (potentially) not
        disjoint yet.

        This method requires:
            - the intersection of two simple sets as a simple set
            - the difference of a simple set (A) and another simple set (B) that is completely contained in A (B ⊆ A).
            The result of that difference has to be a composite set with only one simple set in it.

        :return: A tuple of the disjoint and non-disjoint set.
        """

        # initialize result for disjoint and non-disjoint sets
        disjoint = self.new_empty_set()
        non_disjoint = self.new_empty_set()

        # for every simple set (a)
        for simple_set_a in self.simple_sets:

            # initialize the difference of a with every b
            difference = simple_set_a

            # for every other simple set (b)
            for simple_set_b in self.simple_sets:

                # skip symmetric iterations
                if simple_set_a == simple_set_b:
                    continue

                # get the intersection of a and b
                intersection = simple_set_a.intersection_with(simple_set_b)

                # if the intersection is not empty add it to the non-disjoint set
                non_disjoint.add_simple_set(intersection)

                # get the difference of the simple set with the intersection.
                difference_with_intersection = difference.difference_with(intersection)

                # if the difference is empty
                if len(difference_with_intersection) == 0:
                    # skip the rest of the loop and mark the set for discarding
                    difference = None
                    continue

                # the now should contain only 1 element
                assert len(difference_with_intersection) == 1
                difference = difference_with_intersection[0]

            # if the difference has become None
            if difference is None:
                # skip the rest of the loop
                continue

            # append the simple_set_a without every other simple set to the disjoint set
            disjoint.simple_sets.add(difference)

        return disjoint, non_disjoint

    def make_disjoint(self) -> Self:
        """
        Create an equal composite set that contains a disjoint union of simple sets.

        :return: The disjoint set.
        """

        disjoint, intersection = self.split_into_disjoint_and_non_disjoint()

        # while the intersection is not empty
        while not intersection.is_empty():
            # split the intersection into disjoint and non-disjoint parts
            current_disjoint, intersection = intersection.split_into_disjoint_and_non_disjoint()

            # add the disjoint intersection to the disjoint set
            disjoint.simple_sets.update(current_disjoint.simple_sets)

        return disjoint.simplify()

    def add_simple_set(self, simple_set: AbstractSimpleSet):
        """
        Add a simple set to this composite set if it is not empty.

        :param simple_set: The simple set to add
        """
        if simple_set.is_empty():
            return
        self.simple_sets.add(simple_set)

    def __eq__(self, other: Self):
        return self.simple_sets._list == other.simple_sets._list
