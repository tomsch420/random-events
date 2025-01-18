from __future__ import annotations
import numpy as np
import itertools
from random_events.interval import SimpleInterval
from sortedcontainers import SortedDict, SortedKeysView, SortedValuesView
from typing_extensions import List, TYPE_CHECKING
import plotly.graph_objects as go

from .sigma_algebra import *
from .variable import *
from .variable import Variable


# Type definitions
if TYPE_CHECKING:
    VariableMapSuperClassType = SortedDict[Variable, Any]
else:
    VariableMapSuperClassType = SortedDict


class VariableMap(VariableMapSuperClassType):
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


class SimpleEvent(AbstractSimpleSet, VariableMap):
    """
    A simple event is a set of assignments of variables to values.

    A simple event is logically equivalent to a conjunction of assignments.
    """

    def __init__(self, *args, **kwargs):
        VariableMap.__init__(self, *args, **kwargs)
        for key, value in self.items():
            self[key] = value

        self._cpp_object = rl.SimpleEvent({variable._cpp_object: value._cpp_object for variable, value in self.items()})

    @classmethod
    def _from_cpp(cls, cpp_object):
        variables = cpp_object.variable_map.items()
        result = {}
        for variable, value in variables:
            variable_back = Variable._from_cpp(variable)
            if isinstance(variable_back, Continuous):
                value_back = Interval._from_cpp(value)
            else:
                value_back = Set._from_cpp(value)
            result[variable_back] = value_back
        return cls(result)

    def as_composite_set(self) -> Event:
        return Event(self)

    @property
    def assignments(self) -> SortedValuesView:
        return self.values()

    def contains(self, item: Tuple) -> bool:
        for assignment, value in zip(self.assignments, item):
            if not assignment.contains(value):
                return False
        return True

    def __hash__(self):
        return hash(tuple(self.items()))

    def __setitem__(self, key: Variable, value: Union[AbstractSimpleSet, AbstractCompositeSet]):
        if isinstance(value, AbstractSimpleSet):
            super().__setitem__(key, value.as_composite_set())
        elif isinstance(value, AbstractCompositeSet):
            super().__setitem__(key, value)
        else:
            raise TypeError(f"Value must be a SimpleSet or CompositeSet, got {type(value)} instead.")

    def __lt__(self, other: Self):
        if len(self.variables) < len(other.variables):
            return True
        for variable in self.variables:
            if variable not in other:
                return True
            if self[variable] == other[variable]:
                continue
            else:
                return self[variable] < other[variable]

    def marginal(self, variables: VariableSet) -> SimpleEvent:
        """
        Create the marginal event, that only contains the variables given..

        :param variables: The variables to contain in the marginal event
        :return: The marginal event
        """
        return self._from_cpp(self._cpp_object.marginal({variable._cpp_object for variable in variables}))
        # result = self.__class__()
        # for variable in variables:
        #     result[variable] = self[variable]
        # for_cpp = self.__class__(result)
        # return for_cpp

    def non_empty_to_string(self) -> str:
        return "{" + ", ".join(f"{variable.name} = {assignment}" for variable, assignment in self.items()) + "}"

    def variables_to_json(self) -> List:
        return [variable.to_json() for variable in self.keys()]

    def assignments_to_json(self) -> List:
        return [assignment.to_json() for assignment in self.values()]

    def to_json(self) -> Dict[str, Any]:
        return {**super().to_json(),
                "variables": self.variables_to_json(),
                "assignments": self.assignments_to_json()}

    def to_json_assignments_only(self) -> Dict[str, Any]:
        return {**super().to_json(),
                "assignments": self.assignments_to_json()}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        variables = [Variable.from_json(variable) for variable in data["variables"]]
        assignments = [AbstractCompositeSet.from_json(assignment) for assignment in data["assignments"]]
        return cls({variable: assignment for variable, assignment in zip(variables, assignments)})

    @classmethod
    def from_json_given_variables(cls, data: Dict[str, Any], variables: List[Variable]) -> Self:
        assignments = [AbstractCompositeSet.from_json(assignment) for assignment in data["assignments"]]
        return cls({variable: assignment for variable, assignment in zip(variables, assignments)})

    def plot(self) -> Union[List[go.Scatter], List[go.Mesh3d]]:
        """
        Plot the event.
        """
        assert all(isinstance(variable, Continuous) for variable in self.keys()), \
            "Plotting is only supported for events that consist of only continuous variables."
        if len(self.keys()) == 1:
            return self.plot_1d()
        if len(self.keys()) == 2:
            return self.plot_2d()
        elif len(self.keys()) == 3:
            return self.plot_3d()
        else:
            raise NotImplementedError("Plotting is only supported for two and three dimensional events")

    def plot_1d(self) -> List[go.Scatter]:
        """
        Plot the event in 1D.
        """
        xs = []
        ys = []

        interval: Interval = list(self.values())[0]
        for simple_interval in interval.simple_sets:
            simple_interval: SimpleInterval
            xs.extend([simple_interval.lower, simple_interval.upper, None])
            ys.extend([0, 0, None])

        return [go.Scatter(x=xs, y=ys, mode="lines", name="Event", fill="toself")]

    def plot_2d(self) -> List[go.Scatter]:
        """
        Plot the event in 2D.
        """

        # form cartesian product of all intervals
        intervals = [value.simple_sets for value in self.values()]
        interval_combinations = list(itertools.product(*intervals))

        xs = []
        ys = []

        # for every atomic interval
        for interval_combination in interval_combinations:

            # plot a rectangle
            points = np.asarray(list(itertools.product(*[[axis.lower, axis.upper] for axis in interval_combination])))
            y_points = points[:, 1]
            y_points[len(y_points) // 2:] = y_points[len(y_points) // 2:][::-1]
            xs.extend(points[:, 0].tolist() + [points[0, 0], None])
            ys.extend(y_points.tolist()+ [y_points[0], None])

        return [go.Scatter(x=xs, y=ys, mode="lines", name="Event", fill="toself")]

    def plot_3d(self) -> List[go.Mesh3d]:
        """
        Plot the event in 3D.
        """

        # form cartesian product of all intervals
        intervals = [value.simple_sets for _, value in sorted(self.items())]
        simple_events = list(itertools.product(*intervals))
        traces = []

        # shortcut for the dimensions
        x, y, z = 0, 1, 2

        # for every atomic interval
        for simple_event in simple_events:

            # Create a 3D mesh trace for the rectangle
            traces.append(go.Mesh3d(
                # 8 vertices of a cube
                x=[simple_event[x].lower, simple_event[x].lower, simple_event[x].upper, simple_event[x].upper,
                   simple_event[x].lower, simple_event[x].lower, simple_event[x].upper, simple_event[x].upper],
                y=[simple_event[y].lower, simple_event[y].upper, simple_event[y].upper, simple_event[y].lower,
                   simple_event[y].lower, simple_event[y].upper, simple_event[y].upper, simple_event[y].lower],
                z=[simple_event[z].lower, simple_event[z].lower, simple_event[z].lower, simple_event[z].lower,
                   simple_event[z].upper, simple_event[z].upper, simple_event[z].upper, simple_event[z].upper],
                # i, j and k give the vertices of triangles
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                flatshading=True
            ))
        return traces

    def plotly_layout(self) -> Dict:
        """
        Create a layout for the plotly plot.
        """
        if len(self.variables) == 1:
            result = {"xaxis_title": self.variables[0].name}
        elif len(self.variables) == 2:
            result = {"xaxis_title": self.variables[0].name,
                      "yaxis_title": self.variables[1].name}
        elif len(self.variables) == 3:
            result = dict(scene=dict(
                xaxis_title=self.variables[0].name,
                yaxis_title=self.variables[1].name,
                zaxis_title=self.variables[2].name)
            )
        else:
            raise NotImplementedError("Plotting is only supported for two and three dimensional events")

        return result

    def fill_missing_variables(self, variables: VariableSet):
        """
        Fill this with the variables that are not in self but in `variables`.
        The variables are mapped to their domain.

        :param variables: The variables to fill the event with
        """
        for variable in variables:
            if variable not in self:
                self[variable] = variable.domain
                self._cpp_object[variable._cpp_object] = variable.domain._cpp_object

    def __deepcopy__(self):
        return self.__class__({variable: assignment.__deepcopy__() for variable, assignment in self.items()})


class Event(AbstractCompositeSet):
    """
    An event is a disjoint set of simple events.

    Every simple event added to this event that is missing variables that any other event in this event has, will be
    extended with the missing variable. The missing variables are mapped to their domain.

    """

    simple_sets: SimpleEventContainer

    def __init__(self, *simple_sets):
        super().__init__(*simple_sets)
        self.fill_missing_variables()

        self._cpp_object = rl.Event({simple_set._cpp_object for simple_set in self.simple_sets})

    @classmethod
    def _from_cpp(cls, cpp_object):
        return cls(*[SimpleEvent._from_cpp(cpp_simple_set) for cpp_simple_set in cpp_object.simple_sets])

    @property
    def all_variables(self) -> VariableSet:
        result = SortedSet()
        return result.union(*[SortedSet(simple_set.variables) for simple_set in self.simple_sets])

    def fill_missing_variables(self):
        """
        Fill all simple sets with the missing variables.
        """
        all_variables = self.all_variables
        for simple_set in self.simple_sets:
            simple_set.fill_missing_variables(all_variables)

    def simplify_once(self) -> Tuple[Self, bool]:
        """
        Simplify the event once. This simplification is not guaranteed to as simple as possible.

        :return: The simplified event and a boolean indicating whether the event has changed or not.
        """
        simplified = self._cpp_object.simplify_once()
        return self._from_cpp(simplified[0]), simplified[1]

    def new_empty_set(self) -> Self:
        return Event()

    def complement_if_empty(self) -> Self:
        raise NotImplementedError("Complement of an empty Event is not yet supported.")

    def marginal(self, variables: VariableSet) -> Event:
        """
        TODO: Something wrong with add_simple_set
        Create the marginal event, that only contains the variables given..

        :param variables: The variables to contain in the marginal event
        :return: The marginal event
        """
        return self._from_cpp(self._cpp_object.marginal({variable._cpp_object for variable in variables}))
        # result = self.__class__()
        # for simple_set in self.simple_sets:
        #     result.add_simple_set(simple_set.marginal(variables))
        # updated_result = self.__class__(*result.simple_sets)
        # y = updated_result.make_disjoint()
        # return y

    def bounding_box(self) -> SimpleEvent:
        """
        Compute the bounding box of the event.
        The bounding box is the smallest simple event that contains this event. It is computed by taking the union
        of all simple events variable wise.

        :return: The bounding box as a simple event
        """
        result = SimpleEvent()
        for variable in self.all_variables:
            for simple_set in self.simple_sets:
                if variable not in result:
                    result[variable] = simple_set[variable].__deepcopy__()
                else:
                    result[variable] = result[variable].union_with(simple_set[variable].__deepcopy__())
        return result

    def plot(self, color="#636EFA") -> Union[List[go.Scatter], List[go.Mesh3d]]:
        """
        Plot the complex event.

        :param color: The color to use for this event
        """
        traces = []
        show_legend = True
        for index, event in enumerate(self.simple_sets):
            event_traces = event.plot()
            for event_trace in event_traces:
                if len(event.keys()) == 2:
                    event_trace.update(name="Event", legendgroup=id(self), showlegend=show_legend,
                                       line=dict(color=color))
                if len(event.keys()) == 3:
                    event_trace.update(name="Event", legendgroup=id(self), showlegend=show_legend, color=color)
                show_legend = False
                traces.append(event_trace)
        return traces

    def plotly_layout(self) -> Dict:
        """
        Create a layout for the plotly plot.
        """
        return self.simple_sets[0].plotly_layout()

    def add_simple_set(self, simple_set: AbstractSimpleSet):
        """
        Add a simple set to this event.

        :param simple_set: The simple set to add
        """
        super().add_simple_set(simple_set)
        self.fill_missing_variables()

    def to_json(self) -> Dict[str, Any]:
        variables = [variable.to_json() for variable in self.all_variables]
        simple_sets = [simple_set.to_json_assignments_only() for simple_set in self.simple_sets]
        return {**SubclassJSONSerializer.to_json(self),
                "variables": variables, "simple_sets": simple_sets}

    @classmethod
    def _from_json(cls, data: Dict[str, Any]) -> Self:
        variables = [Variable.from_json(variable) for variable in data["variables"]]
        simple_sets = [SimpleEvent.from_json_given_variables(simple_set, variables) for simple_set in data["simple_sets"]]
        return cls(*simple_sets)


# Type definitions
if TYPE_CHECKING:
    SimpleEventContainer = SortedSet[SimpleEvent]
    EventContainer = SortedSet[Event]
    VariableSet = SortedSet[Variable]
else:
    SimpleEventContainer = SortedSet
    EventContainer = SortedSet
    VariableSet = SortedSet
