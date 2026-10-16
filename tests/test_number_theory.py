import math

import pytest
from hypothesis import example, given
from hypothesis import strategies as st

import fast_math
from tests.reference import I64_MAX, I64_MIN, expected, int64s, outcome, same


def sieve(n: int) -> list[int]:
    if n < 2:
        return []
    composite = bytearray(n + 1)
    for i in range(2, math.isqrt(n) + 1):
        if not composite[i]:
            composite[i * i :: i] = b"\x01" * len(range(i * i, n + 1, i))
    return [i for i in range(2, n + 1) if not composite[i]]


SMALL_PRIMES = sieve(100_000)
PRIME_SET = set(SMALL_PRIMES)


@given(a=int64s, b=int64s)
@example(a=I64_MIN, b=0)
@example(a=I64_MIN, b=I64_MIN)
@example(a=0, b=0)
def test_gcd(a: int, b: int) -> None:
    assert same(outcome(lambda: fast_math.gcd(a, b)), expected(lambda: math.gcd(a, b)))


@given(a=int64s, b=int64s)
@example(a=I64_MAX, b=I64_MAX - 1)
@example(a=I64_MIN, b=1)
@example(a=0, b=I64_MIN)
def test_lcm(a: int, b: int) -> None:
    assert same(outcome(lambda: fast_math.lcm(a, b)), expected(lambda: math.lcm(a, b)))


@pytest.mark.parametrize("n", [*range(-3, 25), I64_MAX, I64_MIN])
def test_factorial(n: int) -> None:
    # math.factorial(I64_MAX) would run out of memory: everything past 20! overflows anyway
    reference = OverflowError if n > 20 else expected(lambda: math.factorial(n))
    assert same(outcome(lambda: fast_math.factorial(n)), reference)


def python_fibonacci(n: int) -> int:
    if n < 0:
        raise ValueError(n)
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@pytest.mark.parametrize("n", [*range(-3, 100), I64_MAX, I64_MIN])
def test_fibonacci(n: int) -> None:
    reference = OverflowError if n > 93 else expected(lambda: python_fibonacci(n))
    assert same(outcome(lambda: fast_math.fibonacci(n)), reference)


def test_is_prime_up_to_100_000() -> None:
    assert [n for n in range(-100, 100_001) if fast_math.is_prime(n)] == SMALL_PRIMES


@given(p=st.sampled_from(SMALL_PRIMES), q=st.sampled_from(SMALL_PRIMES))
def test_products_of_two_primes_are_composite(p: int, q: int) -> None:
    assert not fast_math.is_prime(p * q)


# Mersenne primes, the largest primes below 2**32 and 2**63, and 10**18 + 3
LARGE_PRIMES = [2**31 - 1, 2**61 - 1, 4_294_967_291, 9_223_372_036_854_775_783, 10**18 + 3]
# Carmichael numbers, strong pseudoprimes to base 2, one to every base up to 23, and 2**63 - 1
PSEUDOPRIMES = [561, 1105, 1729, 41041, 825_265, 321_197_185, 5_394_826_801, 232_250_619_601, 9_746_347_772_161]
STRONG_PSEUDOPRIMES = [2047, 3277, 4033, 4681, 8321, 3_825_123_056_546_413_051, I64_MAX]


@pytest.mark.parametrize("n", LARGE_PRIMES)
def test_large_primes(n: int) -> None:
    assert fast_math.is_prime(n)


@pytest.mark.parametrize("n", PSEUDOPRIMES + STRONG_PSEUDOPRIMES)
def test_pseudoprimes_are_composite(n: int) -> None:
    assert not fast_math.is_prime(n)


@given(n=st.integers(-10, 5000))
def test_primes_up_to(n: int) -> None:
    assert fast_math.primes_up_to(n) == [p for p in SMALL_PRIMES if p <= n]


def test_primes_up_to_a_million() -> None:
    primes = fast_math.primes_up_to(1_000_000)
    assert len(primes) == 78_498
    assert primes[-1] == 999_983


def test_sieve_too_large_for_memory() -> None:
    with pytest.raises(MemoryError):
        fast_math.primes_up_to(I64_MAX)


@pytest.mark.parametrize(("function", "n"), [(fast_math.factorial, -1), (fast_math.fibonacci, -1)])
def test_negative_argument(function: object, n: int) -> None:
    with pytest.raises(ValueError, match="not defined for negative values"):
        function(n)  # type: ignore[operator]
