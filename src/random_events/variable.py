from abc import abstractmethod
import random_events_lib as rl

from typing_extensions import Self, Type, Dict, Any, Union, Optional

from .interval import Interval, reals
from .set import Set, SetElement
from .sigma_algebra import AbstractCompositeSet, EMPTY_SET_SYMBOL
from .utils import SubclassJSONSerializer


class Variable(SubclassJSONSerializer):
    """
    Parent class for all random variables.
    """
    name: str
    domain: AbstractCompositeSet

    def __init__(self, name: str, domain: AbstractCompositeSet):
        """
        Construct a new random variable.
        :param name: The name of the variable.
        :param domain: The domain of the variable.
        """
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

    @classmethod
    @abstractmethod
    def _from_cpp(cls, cpp_object):
        if type(cpp_object) == rl.Symbolic:
            return Symbolic._from_cpp(cpp_object)
        elif type(cpp_object) == rl.Continuous:
            return Continuous._from_cpp(cpp_object)
        elif type(cpp_object) == rl.Integer:
            return Integer._from_cpp(cpp_object)


class Continuous(Variable):
    """
    Class for continuous random variables.

    The domain of a continuous variable is the real line.
    """

    def __init__(self, name: str, domain: AbstractCompositeSet = reals()):
        """
        Construct a continuous variable.
        :param name: The name.
        :param domain: The domain of the variable.
        """
        super().__init__(name, reals())

        self._cpp_object = rl.Continuous(self.name)

    @property
    def is_numeric(self):
        return True

    @classmethod
    def _from_cpp(cls, cpp_object):
        return cls(cpp_object.name)


class Symbolic(Variable):
    """
    Class for unordered, finite, discrete random variables.

    The domain of a symbolic variable is a set of values from an enumeration.
    """
    domain: Set

    def __init__(self, name: Optional[str] = None, domain: Union[Type[SetElement], Set] = None):
        """
        Construct a symbolic variable.
        :param name: The name.
        :param domain: The enum class that lists all elements of the domain.
        """

        if domain is None:
            raise ValueError("The domain of a symbolic variable must be specified.")

        if isinstance(domain, set):
            self.domain = Set(*[SetElement(value, domain) for value in domain if value != EMPTY_SET_SYMBOL])
        else:
            self.domain = domain

        super().__init__(name, self.domain)

        self._cpp_object = rl.Symbolic(self.name, self.domain._cpp_object)

    def domain_type(self) -> Type[SetElement]:
        return self.domain.simple_sets[0].all_elements

    @property
    def is_numeric(self):
        return False

    @classmethod
    def _from_cpp(cls, cpp_object):
        return cls(cpp_object.name, Set._from_cpp(cpp_object.get_domain()))


class Integer(Variable):
    """
    Class for ordered, discrete random variables.

    The domain of an integer variable is the number line.
    """

    def __init__(self, name: str, domain: AbstractCompositeSet = reals()):
        """
        Construct an integer variable.
        :param name: The name.
        :param domain: The domain of the variable.
        """
        super().__init__(name, reals())

        self._cpp_object = rl.Integer(self.name)

    @property
    def is_numeric(self):
        return True

    @classmethod
    def _from_cpp(cls, cpp_object):
        return cls(cpp_object.name)