"""
Tests for the determine_package utility.
"""
from __future__ import division, print_function, with_statement

import nose
from nose.tools.trivial import eq_

from orges.tests.util.integer_functions import INTEGER_FUNCTIONS
from orges.invoker.util.determine_package import determine_package


def local_function():
    """Stub function that is located in the same package of the tests."""
    pass


class LocalClass(object):
    """Stub class as determination target."""

    def local_method(self):
        """Stub method as determination target."""
        pass


def test_determine_local_function():
    eq_(determine_package(local_function),
        "orges.tests.unit.invoker.util.test_determine_package")


def test_determine_local_class():
    eq_(determine_package(LocalClass),
        "orges.tests.unit.invoker.util.test_determine_package")


def test_determine_local_method():
    eq_(determine_package(LocalClass.local_method),
        "orges.tests.unit.invoker.util.test_determine_package")


def test_determine_imported():
    for function in INTEGER_FUNCTIONS:
        eq_(determine_package(function),
            "orges.tests.util.integer_functions")

if __name__ == '__main__':
    nose.runmodule()