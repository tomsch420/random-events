# Technical Guide

This document guides through the structure of the `random_events` package and explains how to expand it.

## New Algebras

Algebraic structures are the main concern of this package. 
When you want to add a new algebra, you need to create a new class that inherits from
`AbstractSimpleSet` and `AbstractCompositeSet`.

`SimpleInterval` and `Interval` provide an easy to grasp example of such an implementation.

## New Variables

Describing a multidimensional algebra needs variables that describe the type of dimensions.
In more applied scenarios, it may happen that more information is needed to describe a variable.
Achieving this requires the creation of a new class that inherits from the respective variable.

## Serialization
The `SubClassJSONSerializer` is a class that automatically serializes and deserializes subclasses of a said class.
I strongly recommended getting familiar with this class when adding new classes to the package.