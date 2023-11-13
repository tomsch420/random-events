from typing import Any, Iterable, Dict, Tuple

import portion

from . import utils


class Variable:
    """
    Abstract base class for all variables.
    """

    name: str
    """
    The name of the variable. The name is used for comparison and hashing.
    """

    domain: Any
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

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Variable':
        """
        Create the correct instanceof the subclass from a json dict.

        :param data: The json dict
        :return: The correct instance of the subclass
        """
        for subclass in utils.recursive_subclasses(Variable):
            if utils.get_full_class_name(subclass) == data["type"]:
                return subclass._from_json(data)

        raise ValueError("Unknown type for variable. Type is {}".format(data["type"]))


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


class Symbolic(Discrete):
    """
    Class for unordered, finite, discrete random variables.
    """
    ...


class Integer(Discrete):
    """Class for ordered, discrete random variables."""
    ...
