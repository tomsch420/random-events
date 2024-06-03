from typing_extensions import Self, Type, Dict, Any, Union

from .interval import Interval, SimpleInterval, reals
from .set import Set, SetElement
from .sigma_algebra import AbstractCompositeSet
from .utils import SubclassJSONSerializer


class Variable(SubclassJSONSerializer):
    name: str
    domain: AbstractCompositeSet

    def __init__(self, name: str, domain: AbstractCompositeSet):
        self.name = name
        self.domain = domain

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

    def to_json(self) -> Dict[str, Any]:
        return {
            **super().to_json(),
            "name": self.name,
            "domain": self.domain.to_json()
        }

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        return cls(data["name"], AbstractCompositeSet.from_json(data["domain"]))


class Continuous(Variable):
    """
    Class for continuous random variables.

    The domain of a continuous variable is the real line.
    """
    domain: Interval

    def __init__(self, name: str, domain=None):
        super().__init__(name, reals())


class Symbolic(Variable):
    """
    Class for unordered, finite, discrete random variables.

    The domain of a symbolic variable is a set of values from an enumeration.
    """
    domain: Set

    def __init__(self, name: str, domain: Union[Type[SetElement], SetElement]):
        """
        Construct a symbolic variable.
        :param name: The name.
        :param domain: The enum class that lists all elements of the domain.
        """
        if isinstance(domain, type) and issubclass(domain, SetElement):
            super().__init__(name, Set(*[value for value in domain if value != domain.EMPTY_SET]))
        else:
            super().__init__(name, domain)


class Integer(Variable):
    """
    Class for ordered, discrete random variables.

    The domain of an integer variable is the number line.
    """
    domain: Interval

    def __init__(self, name: str, domain=None):
        super().__init__(name, reals())
