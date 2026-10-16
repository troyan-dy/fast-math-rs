"""
Arithmetic and number theory on Python numbers, implemented in Rust.

Every operation behaves as the Python operator or `math` function of the same name, with one difference: an
`int` is a 64-bit integer, and a result that does not fit raises `OverflowError` instead of growing.
"""

from importlib.metadata import version as _version

from fast_math._core import (
    abs,
    add,
    div,
    factorial,
    fibonacci,
    floordiv,
    gcd,
    is_prime,
    lcm,
    mod,
    mul,
    pow,
    primes_up_to,
    sqrt,
    sub,
)

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

__version__ = _version("fast-math")
