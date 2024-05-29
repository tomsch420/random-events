from collections.abc import dict_keys, dict_values
from typing import Any

from sortedcontainers import SortedDict, SortedKeysView, SortedValuesView
from typing_extensions import Union, Any

from .better_variables import *
from .sigma_algebra import *
from .variables import Variable


class VariableMap(SortedDict[Variable, Any]):
    """
    A map of variables to values.

    Accessing a variable by name is also supported.
    """

    @property
    def variables(self) -> dict_keys[Variable]:
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

    @property
    def assignments(self) -> dict_values[AbstractCompositeSet]:
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
        pass

    def is_empty(self) -> bool:

        if len(self) == 0:
            return True

        for assignment in self.values():
            if assignment.is_empty():
                return True

        return False

    def contains(self, item) -> bool:
        pass

    def __hash__(self):
        return hash(tuple(self.items()))

    def __lt__(self, other):
        pass


class Event(AbstractCompositeSet):
    ...
