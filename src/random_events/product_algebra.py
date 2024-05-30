from sortedcontainers import SortedDict, SortedKeysView, SortedValuesView
from typing_extensions import Union, Any

from .variable import *
from .sigma_algebra import *
from .variable import Variable


class VariableMap(SortedDict[Variable, Any]):
    """
    A map of variables to values.

    Accessing a variable by name is also supported.
    """

    @property
    def variables(self) -> SortedKeysView[Variable]:
        return self.keys()

    def variable_of(self, name: str) -> Variable:
        """
        Get the variable with the given name.
        :param name: The variable's name
        :return: The variable itself
        """
        variable = [variable for variable in self.variables if variable.name == name]
        if len(variable) == 0:
            raise KeyError(f"Variable {name} not found in event {self}")
        return variable[0]

    def __getitem__(self, item: Union[str, Variable]):
        if isinstance(item, str):
            item = self.variable_of(item)
        return super().__getitem__(item)

    def __setitem__(self, key: Union[str, Variable], value: Any):
        if isinstance(key, str):
            key = self.variable_of(key)

        if not isinstance(key, Variable):
            raise TypeError(f"Key must be a Variable if not already present, got {type(key)} instead.")

        super().__setitem__(key, value)

    def __copy__(self):
        return self.__class__({variable: value for variable, value in self.items()})


class SimpleEvent(AbstractSimpleSet, VariableMap[Variable, AbstractCompositeSet]):
    """
    A simple event is a set of assignments of variables to values.

    A simple event is logically equivalent to a conjunction of assignments.
    """

    @property
    def assignments(self) -> SortedValuesView[AbstractCompositeSet]:
        return self.values()

    def intersection_with(self, other: Self) -> Self:
        variables = self.keys() | other.keys()
        result = SimpleEvent()
        for variable in variables:
            if variable in self and variable in other:
                result[variable] = self[variable].intersection_with(other[variable])
            elif variable in self:
                result[variable] = self[variable]
            else:
                result[variable] = other[variable]

        return result

    def complement(self) -> SortedSet[Self]:

        # initialize result
        result = SortedSet()

        # initialize variables where the complement has already been computed
        processed_variables = []

        # for every key, value pair
        for variable, assignment in self.items():

            # initialize the current complement
            current_complement = SimpleEvent()

            # set the current variable to its complement
            current_complement[variable] = assignment.complement()

            # for every other variable
            for other_variable in self.variables:

                # skip this iteration if the other variable is the same as the current one
                if other_variable == variable:
                    continue

                # if it has been processed, set copy its assignment from this
                if other_variable in processed_variables:
                    current_complement[other_variable] = self[other_variable]

                # otherwise, set it to its domain (set of all values)
                else:
                    current_complement[other_variable] = other_variable.domain

            # memorize the processed variables
            processed_variables.append(variable)

            # if the current complement is not empty, add it to the result
            if not current_complement.is_empty():
                result.add(current_complement)

        return result

    def is_empty(self) -> bool:
        if len(self) == 0:
            return True

        for assignment in self.values():
            if assignment.is_empty():
                return True

        return False

    def contains(self, item: Tuple) -> bool:
        for assignment, value in zip(self.assignments, item):
            if not assignment.contains(value):
                return False
        return True

    def __hash__(self):
        return hash(tuple(self.items()))

    def __lt__(self, other: Self):
        for variable, assignment in self.items():
            if assignment < other[variable]:
                return True
        return False

    def non_empty_to_string(self) -> str:
        return "{" + ", ".join(f"{variable.name} = {assignment}" for variable, assignment in self.items()) + "}"


class Event(AbstractCompositeSet):
    """
    An event is a disjoint set of simple events.

    Every simple event added to this event that is missing variables that any other event in this event has, will be
    extended with the missing variable. The missing variables are mapped to their domain.

    """

    simple_sets: SortedSet[SimpleEvent]

    def simplify(self) -> Self:
        simplified, changed = self.simplify_once()
        while changed:
            simplified, changed = simplified.simplify_once()
        return simplified

    def simplify_once(self) -> Tuple[Self, bool]:
        """
        Simplify the event once. This simplification is not guaranteed to as simple as possible.

        :return: The simplified event and a boolean indicating whether the event has changed or not.
        """

        for event_a, event_b in itertools.combinations(self.simple_sets, 2):
            different_variables = SortedSet()

            # get all events where these two events differ
            for variable in event_a.variables:
                if event_a[variable] != event_b[variable]:
                    different_variables.add(variable)

                # if the pair of simple events mismatches in more than one dimension it cannot be simplified
                if len(different_variables) > 1:
                    break

            # if the pair of simple events mismatches in more than one dimension skip it
            if len(different_variables) > 1:
                continue

            # get the dimension where the two events differ
            different_variable = different_variables[0]

            # initialize the simplified event
            simplified_event = SimpleEvent()

            # for every variable
            for variable in event_a.variables:

                # if the variable is the one where the two events differ
                if variable == different_variable:
                    # set it to the union of the two events
                    simplified_event[variable] = event_a[variable].union_with(event_b[variable])

                # if the variable has the same assignment
                else:
                    # copy to the simplified event
                    simplified_event[variable] = event_a[variable]

            # create a new event with the simplified event and all other events
            result = Event(
                [simplified_event] + [event for event in self.simple_sets if event != event_a and event != event_b])
            return result, True

        # if nothing happened, return the original event and False
        return self, False

    def new_empty_set(self) -> Self:
        return Event()

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("Complement of an empty Event is not yet supported.")
