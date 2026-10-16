# The stubs of the Rust extension, src/python.rs; `stubtest` checks them against the module.
#
# Every argument is an `int` (a `bool` too) or a `float`. An `int` beyond 64 bits raises `OverflowError`, any
# other type `TypeError`. An `int` result beyond 64 bits raises `OverflowError`.

from typing import Any, overload

__all__ = [
    "abs",
    "add",
    "div",
    "factorial",
    "fibonacci",
    "floordiv",
    "gcd",
    "is_prime",
    "lcm",
    "mod",
    "mul",
    "pow",
    "primes_up_to",
    "sqrt",
    "sub",
]

@overload
def add(a: int, b: int) -> int:
    """a + b"""

@overload
def add(a: float, b: float) -> float: ...
@overload
def sub(a: int, b: int) -> int:
    """a - b"""

@overload
def sub(a: float, b: float) -> float: ...
@overload
def mul(a: int, b: int) -> int:
    """a * b"""

@overload
def mul(a: float, b: float) -> float: ...
def div(a: float, b: float) -> float:
    """a / b, always a float; ZeroDivisionError when b is 0."""

@overload
def floordiv(a: int, b: int) -> int:
    """a // b, rounded towards negative infinity; ZeroDivisionError when b is 0."""

@overload
def floordiv(a: float, b: float) -> float: ...
@overload
def mod(a: int, b: int) -> int:
    """a % b, with the sign of b; ZeroDivisionError when b is 0."""

@overload
def mod(a: float, b: float) -> float: ...

# An int for a non-negative int exponent, a float for a negative one: Any, as for the builtin pow()
@overload
def pow(base: int, exp: int) -> Any:
    """
    base ** exp. ZeroDivisionError for 0 to a negative power, ValueError for a negative base to a fractional
    power, OverflowError when a float result is too large.
    """

@overload
def pow(base: float, exp: float) -> float: ...
@overload
def abs(x: int) -> int:
    """abs(x)"""

@overload
def abs(x: float) -> float: ...
def sqrt(x: float) -> float:
    """The square root of x, as math.sqrt(x); ValueError when x is negative."""

def gcd(a: int, b: int) -> int:
    """The greatest common divisor of a and b, never negative."""

def lcm(a: int, b: int) -> int:
    """The least common multiple of a and b, never negative; 0 when either is 0."""

def factorial(n: int) -> int:
    """n!; ValueError when n is negative, OverflowError above 20."""

def fibonacci(n: int) -> int:
    """The n-th Fibonacci number, fibonacci(0) == 0; ValueError when n is negative, OverflowError above 92."""

def is_prime(n: int) -> bool:
    """Whether n is a prime number, exact for every 64-bit integer."""

def primes_up_to(n: int) -> list[int]:
    """
    Every prime up to and including n, ascending. Releases the GIL while it sieves; MemoryError when the sieve
    of n / 2 bytes cannot be allocated.
    """
