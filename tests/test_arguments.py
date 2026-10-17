"""
What the functions accept: an int or a float, subclasses and bool included, and nothing else.
"""

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest

import fast_math
from fast_math import _core


class MyInt(int):
    pass


class MyFloat(float):
    pass


@pytest.mark.parametrize("value", ["1", None, 1j, Decimal(1), Fraction(1, 2), [1]])
def test_other_types_raise_type_error(value: Any) -> None:
    with pytest.raises(TypeError):
        fast_math.add(value, 1)
    with pytest.raises(TypeError):
        fast_math.gcd(value, 1)


def test_type_error_names_the_type() -> None:
    with pytest.raises(TypeError, match="expected int or float, got str"):
        fast_math.mul("2", 2)  # type: ignore[call-overload]


@pytest.mark.parametrize("value", [2**63, -(2**63) - 1, 10**30])
def test_int_beyond_64_bits_raises_overflow_error(value: int) -> None:
    with pytest.raises(OverflowError):
        fast_math.add(value, 0)
    with pytest.raises(OverflowError):
        fast_math.is_prime(value)


def test_integer_functions_reject_floats() -> None:
    with pytest.raises(TypeError):
        fast_math.gcd(4.0, 2)  # type: ignore[arg-type]


def test_subclasses_and_bools() -> None:
    assert fast_math.add(MyInt(2), MyFloat(0.5)) == 2.5
    assert fast_math.add(True, True) == 2
    assert fast_math.gcd(MyInt(12), True) == 1


def test_keyword_arguments() -> None:
    assert fast_math.sub(b=1, a=3) == 2
    assert fast_math.pow(base=2, exp=5) == 32


def test_everything_in_the_extension_is_exported() -> None:
    public = {name for name in dir(_core) if not name.startswith("_")}
    assert set(fast_math.__all__) == public


def test_version() -> None:
    assert fast_math.__version__.count(".") == 2
