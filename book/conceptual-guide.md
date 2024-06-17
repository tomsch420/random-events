---
jupytext:
  cell_metadata_filter: -all
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.11.5
kernelspec:
  display_name: Python 3
  language: python
  name: python3
---

# Conceptual Guide

In probability theory, sigma algebras play a fundamental role by formalizing the notion of events within a sample space.
This chapter delves into the development and application of a specific sigma-algebra, the *product sigma algebra* 
tailored for the specific needs of tractable probabilistic inference.

This book walks through the motivation, definition and construction of an algebra that is suitable for tractable 
probabilistic reasoning.

## Motivation

While foundational concepts like sigma-algebras may appear abstract at first, a thorough understanding of their 
properties and, specifically, product sigma-algebras, is crucial for rigorous probability theory and its applications 
across various scientific disciplines, like robotics. Key motivating arguments are

- *Foundations of probability theory*: sigma algebras are the building blocks for defining probability in a rigorous 
way. By understanding them, a deeper understanding of how probabilities are assigned to events is gained.
- *Working with complex events:* In real-world scenarios, events can be intricate. Sigma algebras describe not just 
simple events but also unions, intersections, and complements of these events, and hence are a powerful tool to analyze 
probabilities of more complex situations.
- *Connection to advanced math:* Sigma algebras bridge the gap between set theory and advanced mathematical concepts 
like measure theory and integration. Studying them opens doors to these powerful tools used in various scientific 
fields.

Especially in robotics they are important, since
- *Reasoning with uncertainty:* Robots often operate in environments with uncertainty. 
 Sigma algebras provide a mathematical foundation to represent uncertain events and reason about the probability of 
different events happening (like sensor readings or obstacles appearing).
- *Decision-making under probability:* Many robotic tasks involve making decisions based on probabilities. By 
understanding sigma algebras, algorithms can be build that consider the chance of different outcomes and choose the 
action with the highest probability of success.
- *Planning and control under uncertainty:* Planning robot actions often requires considering various possibilities. 
Sigma algebras allow for the creation of probabilistic models of the environment, enabling robots to plan and control 
their movements while accounting for uncertainties.

Research has shown that events that are described by independent constraints (rules) are most likely the only events 
where probability estimation is tractable. {cite}`choi2020probabilistic`
Spaces that are constructed by independent constraints are called product spaces. Understanding the shape of such 
events is a key competence to building (new) tractable probabilistic models.

## Sigma Algebra

A sigma algebra ($sigma$-algebra) is a set of sets that contains all set differences that can be constructed by 
combining arbitrary subsets of the said set. Furthermore, it contains all countable unions of sets and all infinite 
intersections of the set.

````{prf:definition} Sigma Algebra
:label: def-sigma-algebra

Let {math}`E` be a space of elementary events. Consider the powerset {math}`2^E` and let {math}`\Im \subset 2^E` be a 
set of subsets of {math}`E`. Elements of {math}`\Im` are called random events. 
If {math}`\Im` satisfies the following properties, it is called a sigma-algebra ({math}`\sigma`-algebra).

```{math}
:label: eq-sigma-algebra
1. & \hspace{.5em}  E \in \Im \\
2. & \hspace{.5em}  (A, B) \in \Im \Rightarrow (A - B) \in \Im \\
3. & \hspace{.5em}  (A_1, A_2, ... \in \Im) \Rightarrow \left( \bigcup_{i=1}^\mathbb{N} A_i \in \Im \wedge 
\bigcap_{i=1}^\infty A_i \in \Im \right)
```

The tuple {math}`(E, \Im)` is called a **measurable space**.
````

An example of such a set of sets is the following:

```{code-cell} ipython3
:tags: []
from itertools import chain, combinations
    

def powerset(iterable):
    s = list(iterable)
    result = list(chain.from_iterable(combinations(s, r) for r in range(len(s) + 1)))
    return [set(x) for x in result]


E = {"a", "b", "c"}
powerset_of_E = powerset(E)
powerset_of_E
```

We can see that this is a correct sigma-algebra by verifying all axioms. First, check if it contains the space of 
elementary Events $E$:

```{code-cell} ipython3
:tags: []

E in powerset_of_E
```

Next, check if it contains all set differences:

```{code-cell} ipython3
:tags: []

for A, B in combinations(powerset_of_E, 2):
    if A - B not in powerset_of_E:
        print(f"Set difference {A - B} not in powerset")
```

Finally, check if it contains all countable unions and intersections:

```{code-cell} ipython3
:tags: []

for A, B in combinations(powerset_of_E, 2):
    if A.union(B) not in powerset_of_E:
        print(f"Union {A.union(B)} not in powerset")
    if A.intersection(B) not in powerset_of_E:
        print(f"Intersection {A.intersection(B)} not in powerset")
```

We have constructed a $\sigma$-algebra. This is a basic example, but it is important to understand the concept 
of such a system of sets.

The set operations union and difference can be constructed from complement and intersection.

## Intervals
A more advanced example is the set of intervals. Intervals are a common example of a sigma-algebra that is not trivial 
but yet easy to construct.

First, I introduce the concept of simple intervals and composite intervals in {prf:ref}`def-interval`.

````{prf:definition} Interval
:label: def-interval

A simple interval is a subset of  {math}`\mathbb{R}` denoted by

```{math}
:label: eq-interval
(a,b) &= \{x\in \mathbb{R} \mid a<x<b\},    \\
[a,b) &= \{x\in \mathbb{R} \mid a\le x<b\}, \\
(a,b] &= \{x\in \mathbb{R} \mid a<x\le b\}, \\
[a,b] &= \{x\in \mathbb{R} \mid a\le x\le b\}.
```

A composite interval, or just interval, is a union of simple intervals.

$$
I = I_1 \cup I_2 \cup ... \cup I_n
$$
````

According to {prf:ref}`def-sigma-algebra`, we now have to look at the intersection and complement of simple intervals.

The intersection of two simple intervals is a simple interval.

```{code-cell} ipython3
:tags: []
from random_events.interval import SimpleInterval, Interval, Bound

i1 = SimpleInterval(1, 3, Bound.CLOSED, Bound.CLOSED)
i2 = SimpleInterval(2, 4, Bound.OPEN, Bound.CLOSED)
i2.intersection_with(i1)
````

The complement of a simple interval is an interval.

```{code-cell} ipython3
:tags: []
Interval(*i2.complement())
````

Since every other set operation can be done using only the intersection, union and difference of two sets, we now 
investigate the last interesting property I would like to discuss. 

### Disjoint unions
[Sigma additivity](https://en.wikipedia.org/wiki/Sigma-additive_set_function) is an important property of measures.
Since probability is a measure, it would be nice to deal with disjoint unions of sets instead of regular unions.
An interval can be converted into a disjoint union of simple intervals using {prf:ref}`algo-make-disjoint` and 
{prf:ref}`algo-split-into-disjoint-and-non-disjoint`.

```{prf:algorithm} make_disjoint
:label: algo-make-disjoint

**Inputs** A union of sets  {math}`S = \bigcup_{i=1}^N s_i` that is not nescessarily dijsoint.

**Output**  A disjoint union of sets {math}`S^* = \bigcup_{i=1}^N s_i^*` such that  {math}`S = S^*`.

1. {math}`S^*, S^{'} \leftarrow` split_into_disjoint_and_non_disjoint({math}`S`)

2. while {math}`S^{'} \neq \emptyset`:

    3. disjoint, {math}`S^{'} \leftarrow` split_into_disjoint_and_non_disjoint {math}`(S^{'})`
    
    4. {math}`S^* \leftarrow S^* \cup` disjoint

return {math}`S^*`
```

```{prf:algorithm} split_into_disjoint_and_non_disjoint
:label: algo-split-into-disjoint-and-non-disjoint
TODO
```

As neither {prf:ref}`algo-make-disjoint` nor {prf:ref}`algo-split-into-disjoint-and-non-disjoint` use the fact that 
 {math}`S` is an interval,  we can use them to convert any set of sets into a disjoint union of sets.


## Product Sigma Algebra

In machine learning, problems a typically constructed over a set of variables and not just intervals or simple sets.
Hence, a multidimensional algebra is needed.

As you can probably imagine, it is very inefficient to work with powersets of sets due to their exponential size. 
That's why I introduce the concept of product sigma-algebras.

Product sigma-algebras are constructed by taking the cartesian product of sets and then constructing the 
sigma-algebra on the resulting set.

In this package, we generate product algebras from a viewpoint of classical machine learning. 
In machine learning scenarios, we typically have a set of variables that we want to reason about. Random Events also 
start there. Let's start by defining some variables.