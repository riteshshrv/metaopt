# -*- coding: utf-8 -*-
"""
A working function with integer parameters for testing purposes.
"""
# Future
from __future__ import absolute_import, division, print_function, \
    unicode_literals, with_statement

# First Party
from metaopt.core.paramspec.util import param


@param.int("a", interval=(1, 2))
@param.int("b", interval=(3, 4))
def f(a, b):
    """Function with two non-overlapping integer ranges."""
    return -(a + b)
