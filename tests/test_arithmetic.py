"""
Every arithmetic operation gives what the Python operator gives, for every pair of 64-bit ints and floats.
"""

import math
import operator
from collections.abc import Callable
from typing import Any

import pytest
from hypothesis import example, given

import fast_math
from tests.reference import I64_MAX, I64_MIN, expected, int64s, numbers, outcome, same

Binary = Callable[[Any, Any], Any]

BINARY: tuple[tuple[Binary, Binary], ...] = (
    (fast_math.add, operator.add),
    (fast_math.sub, operator.sub),
    (fast_math.mul, operator.mul),
    (fast_math.div, operator.truediv),
    (fast_math.floordiv, operator.floordiv),
    (fast_math.mod, operator.mod),
)


@pytest.mark.parametrize(("operation", "reference"), BINARY, ids=lambda f: getattr(f, "__name__", ""))
@given(a=numbers, b=numbers)
@example(a=I64_MAX, b=1)
@example(a=I64_MIN, b=-1)
@example(a=0, b=-5)
@example(a=2**53 + 1, b=3)
@example(a=1.0, b=0.1)
@example(a=-1.0, b=math.inf)
@example(a=0.0, b=-0.0)
def test_binary_operation(operation: Binary, reference: Binary, a: int | float, b: int | float) -> None:
    assert same(outcome(lambda: operation(a, b)), expected(lambda: reference(a, b)))


@given(a=int64s, b=int64s)
def test_int_division_is_correctly_rounded(a: int, b: int) -> None:
    """Beyond 2**53, float(a) / float(b) would round twice; Python's int division rounds once."""
    assert same(outcome(lambda: fast_math.div(a, b)), expected(lambda: a / b))


def python_pow(base: int | float, exp: int | float) -> object:
    # An int power that is far beyond 64 bits would take Python long to compute
    if isinstance(base, int) and isinstance(exp, int) and abs(base) >= 2 and exp >= 64:
        return 2**64
    # The one departure: Python gives a complex number (or an OverflowError of complex pow), the core raises
    # ValueError as math.pow() does
    if math.isfinite(base) and math.isfinite(exp) and base < 0 and exp != math.floor(exp):
        raise ValueError("negative number to a fractional power")
    return base**exp


@given(base=numbers, exp=numbers)
@example(base=2, exp=62)
@example(base=-2, exp=63)
@example(base=2, exp=63)
@example(base=-1, exp=I64_MAX)
@example(base=0, exp=-1)
@example(base=-8.0, exp=1 / 3)
@example(base=10.0, exp=400.0)
@example(base=0.0, exp=-math.inf)
@example(base=math.nan, exp=0)
@example(base=1, exp=math.nan)
@example(base=-math.inf, exp=3.0)
def test_pow(base: int | float, exp: int | float) -> None:
    assert same(outcome(lambda: fast_math.pow(base, exp)), expected(lambda: python_pow(base, exp)))


@given(x=numbers)
@example(x=I64_MIN)
@example(x=-0.0)
def test_abs(x: int | float) -> None:
    assert same(outcome(lambda: fast_math.abs(x)), expected(lambda: abs(x)))


@given(x=numbers)
@example(x=-0.0)
@example(x=-1)
@example(x=-math.inf)
def test_sqrt(x: int | float) -> None:
    assert same(outcome(lambda: fast_math.sqrt(x)), expected(lambda: math.sqrt(x)))


@pytest.mark.parametrize(
    ("call", "error"),
    [
        (lambda: fast_math.add(I64_MAX, 1), OverflowError),
        (lambda: fast_math.mul(2**32, 2**32), OverflowError),
        (lambda: fast_math.pow(2, 63), OverflowError),
        (lambda: fast_math.div(1, 0), ZeroDivisionError),
        (lambda: fast_math.mod(1.5, 0), ZeroDivisionError),
        (lambda: fast_math.floordiv(1, 0), ZeroDivisionError),
        (lambda: fast_math.pow(0, -1), ZeroDivisionError),
        (lambda: fast_math.pow(-8.0, 0.5), ValueError),
        (lambda: fast_math.pow(10.0, 400), OverflowError),
        (lambda: fast_math.sqrt(-1), ValueError),
    ],
)
def test_errors(call: Callable[[], object], error: type[Exception]) -> None:
    with pytest.raises(error):
        call()


def test_results_keep_the_kind_of_number() -> None:
    assert type(fast_math.add(1, 2)) is int
    assert type(fast_math.add(1, 2.0)) is float
    assert type(fast_math.div(4, 2)) is float
    assert type(fast_math.pow(2, 3)) is int
    assert type(fast_math.pow(2, -1)) is float
    assert type(fast_math.floordiv(7.0, 2)) is float
    assert type(fast_math.abs(True)) is int
