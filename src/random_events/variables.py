from typing import Any, Iterable, Dict, Tuple

import portion
from typing_extensions import Union

from . import utils

AssignmentType = Union[portion.Interval, Tuple]


class Variable(utils.SubclassJSONSerializer):
    """
    Abstract base class for all variables.
    """

    name: str
    """
    The name of the variable. The name is used for comparison and hashing.
    """

    domain: AssignmentType
    """
    The set of possible events of the variable.
    """

    def __init__(self, name: str, domain: Any):
        self.name = name
        self.domain = domain

    def __lt__(self, other: "Variable") -> bool:
        """
        Returns True if self < other, False otherwise.
        """
        return self.name < other.name

    def __gt__(self, other: "Variable") -> bool:
        """
        Returns True if self > other, False otherwise.
        """
        return self.name > other.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name and self.domain == other.domain

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.domain})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def encode(self, value: Any) -> Any:
        """
        Encode an element of the domain to a representation that is usable for computations.

        :param value: The element to encode
        :return: The encoded element
        """
        return value

    def decode(self, value: Any) -> Any:
        """
        Decode an element to the domain from a representation that is usable for computations.

        :param value: The element to decode
        :return: The decoded element
        """
        return value

    def encode_many(self, elements: Iterable) -> Iterable[Any]:
        """
        Encode many elements of the domain to representations that are usable for computations.

        :param elements: The elements to encode
        :return: The encoded elements
        """
        return elements

    def decode_many(self, elements: Iterable) -> Iterable[Any]:
        """
        Decode many elements from the representations that are usable for computations to their domains.

        :param elements: The encoded elements
        :return: The decoded elements
        """
        return elements

    def to_json(self) -> Dict[str, Any]:
        return {"name": self.name, "type": utils.get_full_class_name(self.__class__), "domain": self.domain}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> 'Variable':
        """
        Create a variable from a json dict.
        This method is called from the from_json method after the correct subclass is determined.

        :param data: The json dict
        :return: The variable
        """
        return cls(name=data["name"], domain=data["domain"])

    def complement_of_assignment(self, assignment: AssignmentType, encoded: bool = False) -> AssignmentType:
        """
        Returns the complement of the assignment for the variable.

        :param assignment: The assignment
        :param encoded: If the assignment is encoded
        :return: The complement of the assignment
        """
        raise NotImplementedError

    @staticmethod
    def intersection_of_assignments(assignment1: AssignmentType,
                                    assignment2: AssignmentType,
                                    encoded: bool = False) -> AssignmentType:
        """
        Returns the intersection of two assignments

        :param assignment1: The first assignment
        :param assignment2: The second assignment
                :param encoded: If the assignment is encoded
        :return: The intersection of the assignments
        """
        raise NotImplementedError

    @staticmethod
    def union_of_assignments(assignment1: AssignmentType,
                             assignment2: AssignmentType,
                             encoded: bool = False) -> AssignmentType:
            """
            Returns the union of two assignments

            :param assignment1: The first assignment
            :param assignment2: The second assignment
            :param encoded: If the assignment is encoded
            :return: The union of the assignments
            """
            raise NotImplementedError

    def assignment_to_json(self, assignment: AssignmentType) -> Any:
        """
        Convert an assignment to a json serializable object.
        """
        raise NotImplementedError

    def assignment_from_json(self, data: Any) -> AssignmentType:
        """
        Convert an assignment from a json serializable object.
        """
        raise NotImplementedError

    @property
    def encoded_domain(self):
        return self.encode_many(self.domain)


class Continuous(Variable):
    """
    Class for real valued random variables.
    """

    domain: portion.Interval

    def __init__(self, name: str, domain: portion.Interval = portion.open(-portion.inf, portion.inf)):
        super().__init__(name=name, domain=domain)

    def to_json(self) -> Dict[str, Any]:
        return {"name": self.name, "type": utils.get_full_class_name(self.__class__),
                "domain": portion.to_data(self.domain)}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> 'Variable':
        return cls(name=data["name"], domain=portion.from_data(data["domain"]))

    def complement_of_assignment(self, assignment: portion.Interval, encoded: bool = False) -> portion.Interval:
        return self.domain - assignment

    @staticmethod
    def intersection_of_assignments(assignment1: portion.Interval,
                                    assignment2: portion.Interval,
                                    encoded: bool = False) -> portion.Interval:
        return assignment1 & assignment2

    @staticmethod
    def union_of_assignments(assignment1: portion.Interval,
                             assignment2: portion.Interval,
                             encoded: bool = False) -> portion.Interval:
        return assignment1 | assignment2

    def assignment_to_json(self, assignment: portion.Interval) -> Any:
        return portion.to_data(assignment)

    def assignment_from_json(self, data: Any) -> portion.Interval:
        return portion.from_data(data)


class Discrete(Variable):
    """
    Class for discrete countable random variables.
    """
    domain: Tuple

    def __init__(self, name: str, domain: Iterable):
        super().__init__(name=name, domain=tuple(sorted(set(domain))))

    def encode(self, element: Any) -> int:
        """
        Encode an element of the domain to its index.

        :param element: The element to encode
        :return: The index of the element
        """
        return self.domain.index(element)

    def decode(self, index: int) -> Any:
        """
        Decode an index to its element of the domain.

        :param index: The elements index
        :return: The element itself
        """
        return self.domain[index]

    def encode_many(self, elements: Iterable) -> Iterable[int]:
        """
        Encode many elements of the domain to the indices of the elements.

        :param elements: The elements to encode
        :return: The encoded elements
        """
        return tuple(map(self.encode, elements))

    def decode_many(self, elements: Iterable[int]) -> Iterable[Any]:
        """
        Decode many elements from indices to their domains.

        :param elements: The encoded elements
        :return: The decoded elements
        """
        return tuple(map(self.decode, elements))

    def complement_of_assignment(self, assignment: Tuple, encoded: bool = False) -> Tuple:
        if not encoded:
            return tuple(sorted(set(self.domain) - set(assignment)))
        else:
            return tuple(sorted(set(range(len(self.domain))) - set(assignment)))

    @staticmethod
    def intersection_of_assignments(assignment1: Tuple,
                                    assignment2: Tuple,
                                    encoded: bool = False) -> Tuple:

        return tuple(sorted(set(assignment1) & set(assignment2)))

    @staticmethod
    def union_of_assignments(assignment1: Tuple,
                             assignment2: Tuple,
                             encoded: bool = False) -> Tuple:
        return tuple(sorted(set(assignment1) | set(assignment2)))

    def assignment_to_json(self, assignment: Tuple) -> Tuple:
        return assignment

    def assignment_from_json(self, data: Any) -> AssignmentType:
        return tuple(data)


class Symbolic(Discrete):
    """
    Class for unordered, finite, discrete random variables.
    """
    ...


class Integer(Discrete):
    """Class for ordered, discrete random variables."""
    ...
