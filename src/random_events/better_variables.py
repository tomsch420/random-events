from dataclasses import dataclass

from typing_extensions import Self, Type

from .interval import Interval, SimpleInterval
from .set import Set, SetElement
from .sigma_algebra import AbstractCompositeSet


@dataclass
class Variable:
    name: str
    domain: AbstractCompositeSet

    def __lt__(self, other: Self) -> bool:
        """
        Returns True if self < other, False otherwise.
        """
        return self.name < other.name

    def __gt__(self, other: Self) -> bool:
        """
        Returns True if self > other, False otherwise.
        """
        return self.name > other.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.domain})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"


@dataclass
class Continuous(Variable):
    domain: Interval = Interval([SimpleInterval(-float("inf"), float("inf"))])


@dataclass
class Symbolic(Variable):
    """
    Class for unordered, finite, discrete random variables.
    """
    domain: Set

    def __init__(self, name: str, domain: Type):
        super().__init__(name, Set([value for value in domain if value != domain.EMPTY_SET]))


@dataclass
class Integer(Variable):
    """Class for ordered, discrete random variables."""
    domain: Interval = Interval([SimpleInterval(-float("inf"), float("inf"))])
