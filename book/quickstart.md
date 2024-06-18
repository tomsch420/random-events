# Quickstart
This is a quickstart guide to get you up and running with the `random_events` library.

## Installation

To install the library, run the following command:

[//]: # (```bash)

[//]: # (pip install random_events)

[//]: # (```)

Next, import the necessary functionality:

```{code-cell} ipython3
:tags: []

from random_events.variable import Symbolic, Continuous
from random_events.product_algebra import SimpleEvent, Event
from random_events.interval import SimpleInterval, Interval, closed, closed_open
from random_events.set import SetElement, Set
import plotly
import plotly.graph_objects as go
plotly.offline.init_notebook_mode()
````

## Intervals

Intervals are a fundamental concept in the `random_events` library. 
They are used to represent the range of possible values that a variable can take. 
There are two classes to interact with intervals: `SimpleInterval` and `Interval`.
However, it is **strongly recommended** to use the `Interval` class,
as it provides an API implementing all set operations.

First, create two simple intervals:

```{code-cell} ipython3
:tags: []

si1 = SimpleInterval(0, 1)
si2 = SimpleInterval(0.5, 1.5)

si1, si2
````


## Sets

## Variables

## Events