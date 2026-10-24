"""
What the functions accept: an int or a float, subclasses and bool included, and nothing else.
"""

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest

import fast_math
from fast_math import _core  # noqa: WPS458 - the test compares the package with its extension


class MyInt(int):  # noqa: WPS600 - the subclass of a builtin is what the test feeds in
    """An int subclass, which the functions accept as an int."""


class MyFloat(float):  # noqa: WPS600 - the subclass of a builtin is what the test feeds in
    """A float subclass, which the functions accept as a float."""


@pytest.mark.parametrize("argument", ["1", None, 1j, Decimal(1), Fraction(1, 2), [1]])
def test_other_types_raise_type_error(argument: Any) -> None:
    with pytest.raises(TypeError):
        fast_math.add(argument, 1)
    with pytest.raises(TypeError):
        fast_math.gcd(argument, 1)


def test_type_error_names_the_type() -> None:
    with pytest.raises(TypeError, match="expected int or float, got str"):
        fast_math.mul("2", 2)  # type: ignore[call-overload]


@pytest.mark.parametrize("argument", [2**63, -(2**63) - 1, 10**30])
def test_int_beyond_i64_raises_overflow_error(argument: int) -> None:
    with pytest.raises(OverflowError):
        fast_math.add(argument, 0)
    with pytest.raises(OverflowError):
        fast_math.is_prime(argument)


def test_integer_functions_reject_floats() -> None:
    with pytest.raises(TypeError):
        fast_math.gcd(4.0, 2)  # type: ignore[arg-type]


def test_subclasses_and_bools() -> None:
    assert fast_math.add(MyInt(2), MyFloat(0.5)) == 2.5  # noqa: WPS459 - 2.5 is exact in binary
    assert fast_math.add(True, True) == 2
    assert fast_math.gcd(MyInt(12), True) == 1


def test_keyword_arguments() -> None:
    assert fast_math.sub(b=1, a=3) == 2
    assert fast_math.pow(base=2, exp=5) == 32


def test_everything_in_the_extension_is_exported() -> None:
    public = {name for name in dir(_core) if not name.startswith("_")}  # noqa: WPS421 - what the extension defines
    assert set(fast_math.__all__) == public


def test_version() -> None:
    assert fast_math.__version__.count(".") == 2
