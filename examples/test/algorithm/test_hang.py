"""
Tests for the hangmodule C extension.
"""

from __future__ import division, print_function, with_statement

from examples.algorithm.hang import hang

if __name__ == '__main__':
    AMOUNT_OF_SECONDS_TO_HANG = 3
    hang(AMOUNT_OF_SECONDS_TO_HANG)