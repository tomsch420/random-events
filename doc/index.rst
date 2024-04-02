.. Random Events documentation master file, created by
   sphinx-quickstart on Mon Oct 23 15:23:00 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Random Events' documentation!
=========================================

Probabilistic Machine Learning frequently requires descriptions of random variables and events
that are shared among many packages.
This package provides a common interface for describing random variables and events, using
usable and easily extensible classes.

Install the package via

.. code-block:: bash

    pip install random-events

The formalism behind this package is the
`Product Measure <https://www.math.ucdavis.edu/~hunter/measure_theory/measure_notes_ch5.pdf>`_.

Introduction
============
The package contains two modules.

Variables
---------

The first one is Variables :mod:`random_events.variables` which contains the taxonomy and definitions
of random variables. Random Variables are described by their name and by their domain.
They are structured as follows

.. autoapi-inheritance-diagram:: random_events.variables


Variables are order-able and comparable by their name.

Variables split in two categories, :class:`random_events.variables.Discrete` and
:class:`random_events.variables.Continuous`.
Discrete variables are described by a (finite) set of possible values while continuous variables
are defined on the real line.

Continuous Variables are described using `portion <https://pypi.org/project/portion/>`_ intervals.
This allows to describe intervals with infinite bounds and to perform operations on them, such as
union, intersection, difference, etc.

Discrete Variables further split into integer variables and symbolic variables.
While integer variables are described by finite sets of order-able elements, symbolic
variables are described by a set of not order-able symbols.

The domains of discrete variables are stored as tuples and should not be modified after creation.


Events
------

While the literature describes events as arbitrary sets of outcomes, research has shown that there
is a limited number of events that are tractable to calculate on. These are the sets that
can be described by independent restrictions.
For example, the event that :math:`0 < x < 1` and :math:`y > 2` can be calculated by some models,
since the bounds for :math:`x` and :math:`y` are defined independently of each other.
Unfortunately, it turned out that calculations on dependent integrals, such as :math:`0 < x < y`, are
intractable for most (all) models. Further information on the reasons behind such limitations are
found in literature on `Probabilistic Circuits <http://starai.cs.ucla.edu/papers/ProbCirc20.pdf>`_.

The package contains the module :mod:`random_events.events` for the taxonomy and definitions of
random events.
Random events are structured as follows

.. autoapi-inheritance-diagram:: random_events.events
   :top-classes: collections.UserDict


Random events extend dictionary like functionality for easy access and modification.
The most basic class is the :class:`random_events.events.VariableMap` class, which is a dictionary
that assigns variables to arbitrary values. This can be used for storing distributions, for example.
The :class:`random_events.events.Event` class extends the :class:`random_events.events.VariableMap`
class by only allowing the assignment of variables to values that are in the domain of the variable.
These values are automatically converted to the correct type, if possible.
An event is interpreted as a restriction on the full set of the variables involved.
If, for example, :math:`\{ Dog, Cat \}` is assigned to a variable about animals, it describes
the event that the animal is either a dog or a cat.

Furthermore, intersections of events are possible. The intersection is done variable wise.

The next class is the :class:`random_events.events.EncodedEvent` class, which converts events to
representations that are usable for indexing. For discrete variables, the values are converted to
indices, while for continuous variables, the values are not changed.

The last class is the :class:`random_events.events.ComplexEvent` class. This class holds a list of disjoint
events. It can be seen as the result of operations where the result is not a single event, but a set of events.
Formally, it is the product outer measure.

Examples
========

.. nbgallery::
   examples/example
   examples/product_spaces
   examples/logo_generation
   examples/self_assessment

.. toctree::
   :maxdepth: 2
   :caption: Contents:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
