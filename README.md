# B-Tree Implementation

This project implements a B-tree in Python.

## Features

- insertion
- deletion
- search
- node split and promotion
- sibling redistribution
- node merging

## Description

A B-tree is a balanced multi-way search tree that stores multiple keys per node.
It is commonly used in database indexes and file systems.

## Parameters

- `m`: maximum number of children / branching factor

## Example

```python
from btree import Btree

tree = Btree(m=3)

for key in [10, 20, 5, 6, 12, 30, 7, 17]:
    tree.insert(key)

print(tree.dump())
