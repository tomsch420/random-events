import json
from typing import Any, Union, Iterable

import portion
import pydantic


class Variable(pydantic.BaseModel):
    """
    Abstract base class for all variables.
    """

    name: str
    """
    The name of the variable. The name is used for comparison and hashing.
    """

    domain: Any = pydantic.Field(repr=False)
    """
    The set of possible events of the variable.
    """

    def __init__(self, name: str, domain: Any):
        super().__init__(name=name, domain=domain)

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


class Continuous(Variable):
    """
    Class for real valued random variables.
    """

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)

    domain: portion.Interval = pydantic.Field(portion.open(-portion.inf, portion.inf), repr=False)

    def __init__(self, name: str, domain: portion.Interval = portion.open(-portion.inf, portion.inf)):
        super().__init__(name=name, domain=domain)

    @pydantic.field_serializer("domain")
    def serialize_domain(self, interval: portion.Interval) -> str:
        """
        Serialize the domain of this variable to a string.
        :param interval: The domain
        :return: A json string of it
        """
        return json.dumps(portion.to_data(interval))

    @pydantic.field_validator("domain", mode="before")
    def validate_domain(cls, interval: Union[portion.Interval, str]) -> portion.Interval:
        if isinstance(interval, str):
            return portion.from_data(json.loads(interval))
        elif isinstance(interval, portion.Interval):
            return interval
        else:
            raise ValueError("Unknown type for domain. Type is {}".format(type(interval)))


class Discrete(Variable):
    """
    Class for discrete countable random variables.
    """
    domain: tuple = pydantic.Field(repr=False)

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
