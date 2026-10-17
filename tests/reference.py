"""
Python itself is the reference: fast_math gives what the Python operator or `math` function gives, or the
exception the 64-bit core raises instead (ADR-0002, ADR-0003).
"""

import math
from collections.abc import Callable

from hypothesis import strategies as st

I64_MIN = -(2**63)
I64_MAX = 2**63 - 1

# The value of a call, or the type of the exception it raised
Outcome = object | type[BaseException]

# Where 64-bit arithmetic and the conversion to a float break first
EDGES = [0, 1, -1, 2, -2, 3, I64_MIN, I64_MAX, I64_MIN + 1, I64_MAX - 1, 2**31, 2**32, 2**53, 2**53 + 1, -(2**53) - 1]

int64s = st.one_of(st.integers(I64_MIN, I64_MAX), st.sampled_from(EDGES), st.integers(-1000, 1000))
small_floats = st.floats(-1e6, 1e6).map(lambda x: round(x, 2))
floats = st.one_of(st.floats(), st.sampled_from([0.0, -0.0, 0.5, -0.5, 1.0, -1.0, math.inf, -math.inf]), small_floats)
numbers = st.one_of(int64s, floats, st.booleans())


def outcome(call: Callable[[], object]) -> Outcome:
    try:
        return call()
    except (ArithmeticError, ValueError, TypeError, MemoryError) as error:
        return type(error)


def expected(call: Callable[[], object]) -> Outcome:
    """
    The outcome of the Python reference, as the 64-bit core has it.
    """
    result = outcome(call)
    if isinstance(result, complex):
        # A negative base to a fractional power: math.pow() raises, as the core does
        return ValueError
    if isinstance(result, int) and not isinstance(result, bool) and not I64_MIN <= result <= I64_MAX:
        return OverflowError
    return result


def same(actual: Outcome, reference: Outcome) -> bool:
    """
    Equal values of the same type; a float NaN equals a NaN, and 0.0 differs from -0.0.
    """
    if type(actual) is not type(reference):
        return False
    if isinstance(actual, float) and isinstance(reference, float):
        if math.isnan(reference):
            return math.isnan(actual)
        return actual == reference and math.copysign(1.0, actual) == math.copysign(1.0, reference)
    return actual == reference
