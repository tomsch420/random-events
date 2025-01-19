from abc import abstractmethod

from typing_extensions import Self, Type, Dict, Any, Union, Optional

from random_events.before_bindings.interval_old import Interval, reals

from random_events.before_bindings.sigma_algebra_old import *
from random_events.utils import SubclassJSONSerializer


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

    @property
    @abstractmethod
    def is_numeric(self):
        """
        :return: Rather, this variable has a numeric domain or not.
        """
        raise NotImplementedError


class Continuous(Variable):
    """
    Class for continuous random variables.

    The domain of a continuous variable is the real line.
    """
    domain: Interval

    def __init__(self, name: str, domain=None):
        super().__init__(name, reals())

    @property
    def is_numeric(self):
        return True


# class Symbolic(Variable):
#     """
#     Class for unordered, finite, discrete random variables.
#
#     The domain of a symbolic variable is a set of values from an enumeration.
#     """
#     domain: Set
#
#     def __init__(self, name: Optional[str] = None, domain: Union[Type[SetElement], Set] = None):
#         """
#         Construct a symbolic variable.
#         :param name: The name.
#         :param domain: The enum class that lists all elements of the domain.
#         """
#
#         if domain is None:
#             raise ValueError("The domain of a symbolic variable must be specified.")
#
#         if isinstance(domain, Set):
#             domain = domain.simple_sets[0].__class__
#
#         assert isinstance(domain, type) and issubclass(domain, SetElement), ("The domain must be a subclass of "
#                                                                              "SetElement.")
#         if name is None:
#             name = domain.__name__
#
#         super().__init__(name, Set(*[value for value in domain if value != domain.EMPTY_SET]))
#
#     def domain_type(self) -> Type[SetElement]:
#         return self.domain.simple_sets[0].all_elements
#
#     @property
#     def is_numeric(self):
#         return False
#

class Integer(Variable):
    """
    Class for ordered, discrete random variables.

    The domain of an integer variable is the number line.
    """
    domain: Interval

    def __init__(self, name: str, domain=None):
        super().__init__(name, reals())

    @property
    def is_numeric(self):
        return True