from collections import deque

import numpy as np
import polytope
from ortools.linear_solver import pywraplp
from scipy.spatial import ConvexHull
from typing_extensions import Self

from .interval import closed_open
from .product_algebra import Event, SimpleEvent, Continuous


class Polytope(polytope.Polytope):

    @classmethod
    def from_polytope(cls, polytope_: polytope.Polytope) -> Self:
        """
        Create a polytope from a polytope object.

        :param polytope_: The polytope object.
        """
        return cls(polytope_.A, polytope_.b)

    @classmethod
    def from_2d_points(cls, points: np.ndarray) -> Self:
        """
        Create a polytope from a set of 2D points, by computing the convex hull of the points and then creating the
        linear inequalities from the convex hull.

        :param points: A numpy array with shape (n, 2) containing the points.
        """

        # create the convexhull
        convex_hull = ConvexHull(points)
        hull_points = np.vstack([points[convex_hull.vertices], points[convex_hull.vertices[0]]])

        # calculate the inequalities
        constraints = []
        for i in range(hull_points.shape[0] - 1):
            p1 = hull_points[i]
            p2 = hull_points[i + 1]
            a = p2[1] - p1[1]
            b = p1[0] - p2[0]
            c = a * p1[0] + b * p1[1]
            constraints.append((a, b, c))
        constraints = np.array(constraints)
        result = cls(constraints[:, :2], constraints[:, 2])
        return result

    def inner_box_approximation(self, epsilon: float = 0.1) -> Event:
        """
        Compute an inner box approximation of the polytope.

        Similar to algorithm 5.

        :param epsilon: The epsilon for the approximation.
        If a box is created in the induction with lower volume than epsilon, it will not be split further.

        :return: The inner box approximation of the polytope as a random event.
        """
        # initialize a queue with polytopes that need to be approximated
        working_queue = deque([self])
        resulting_boxes = []

        while working_queue:
            current_polytope = working_queue.popleft()
            inner_box = current_polytope.maximum_inner_box()
            resulting_boxes.append(inner_box)

            # if the inner box is too small, we do not split it further
            if inner_box.volume < epsilon:
                continue

            # append the polytope without the inner box to the queue
            diff = polytope.mldivide(current_polytope, inner_box)
            working_queue.extend([self.__class__.from_polytope(p) for p in diff.list_poly])

        return Event(*[box.to_simple_event() for box in resulting_boxes]).make_disjoint()

    def outer_box_approximation(self) -> Event:
        ...

    def maximum_inner_box(self) -> Self:
        """
        Compute the maximum single inner box approximation of the polytope.

        This implements Algorithm 2 in https://cse.lab.imtlucca.it/~bemporad/publications/papers/compgeom-boxes.pdf

        :return: The maximum inner box of the polytope.
        """

        # calculate bounding box
        minima, maxima = self.bounding_box
        minima = minima.flatten()
        maxima = maxima.flatten()

        solver = pywraplp.Solver.CreateSolver("GLOP")

        # create variables for the dimensions of the inner box approximation (x_0, x_1, ..., x_n)
        dimension_variables = [solver.NumVar(minimum, maximum, f"x_{i}") for i, (minimum, maximum) in
                               enumerate(zip(minima, maxima))]

        # create the scale variable (lambda in the paper)
        scale = solver.NumVar(0, 1, "scale")

        # set the goal to maximize lambda
        solver.Maximize(scale)

        # create the guess for the r vector
        scale_of_box = maxima - minima

        # create the matrix A^+
        a_positive = np.maximum(0, self.A)

        # create the constraints from proposition 2
        for a, a_positive, b in zip(self.A, a_positive, self.b):
            solver.Add(sum(a * dimension_variables) + sum(a_positive * scale_of_box * scale) <= b)

        # solve the problem
        status = solver.Solve()
        assert status == pywraplp.Solver.OPTIMAL, "The solver did not find an optimal solution."

        # calculate the inner box
        box = [[dimension.solution_value(), dimension.solution_value() + scale_of_dimension * scale.solution_value()]
               for dimension, scale_of_dimension in zip(dimension_variables, scale_of_box)]
        return self.__class__.from_box(box)

    def to_simple_event(self) -> SimpleEvent:
        """
        Convert the polytope to a simple event by using its bounding box.
        """
        minima, maxima = self.bounding_box
        minima = minima.flatten()
        maxima = maxima.flatten()
        return SimpleEvent({Continuous(f"x_{i}"): closed_open(minimum, maximum) for i, (minimum, maximum) in
            enumerate(zip(minima, maxima))})
