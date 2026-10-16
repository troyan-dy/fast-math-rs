# Semantics

← [Documentation](../../README.md#documentation)

Python is the reference: every function gives what the Python operator or `math` function gives for the same
arguments, down to the sign of a zero, NaN and the type of the exception. The tests check this property on
every pair of arguments that hypothesis generates over the whole 64-bit and `float` range
(`tests/test_arithmetic.py`, `tests/test_number_theory.py`). The differences are listed below, and each one is
a decision of its own ([ADR-0002](../adr/0002-integers-are-64-bit.md),
[ADR-0003](../adr/0003-python-is-the-reference.md)).

## Arguments

An argument is an `int` or a `float`, subclasses included; a `bool` is an `int`, as everywhere in Python. An
`int` outside `[-2**63, 2**63 - 1]` raises `OverflowError` before anything is computed: it is never rounded to
a `float` quietly. The exception carries a note that names the argument.

```pycon
>>> import fast_math as fm
>>> fm.add(True, True)
2
>>> fm.add(2**64, 0)
Traceback (most recent call last):
  ...
OverflowError: Python int too large to convert to C long
while processing 'a'
>>> fm.add("1", 2)
Traceback (most recent call last):
  ...
TypeError: expected int or float, got str
while processing 'a'

```

`Decimal`, `Fraction`, `complex` and NumPy integers raise `TypeError`; convert them with `int()` or `float()`
first. NumPy floats are `float` subclasses and are accepted. `gcd`, `lcm`, `factorial`, `fibonacci`, `is_prime`
and `primes_up_to` take integers only, as their `math` counterparts do.

## Integers are 64-bit

Two ints give an `int` whenever Python would, and an `int` result outside the 64-bit range raises
`OverflowError` where Python would return a bigger integer. That includes `abs(-2**63)`, `floordiv(-2**63, -1)`,
`pow(2, 63)`, `gcd(-2**63, 0)`, `factorial(21)` and `fibonacci(93)`. There is no wrap-around and no silent
switch to `float`.

## Floats follow IEEE 754, as in Python

`inf` and `nan` pass through as in Python; `mul(1e308, 10.0)` is `inf`, not an error, because `1e308 * 10.0`
is `inf` too. A mixed `int` and `float` operation converts the `int` to the nearest `float` first, as Python
does.

`div` of two ints is correctly rounded, as Python's `int / int`: `div(2**53 + 1, 3)` is the nearest `float` to
the exact quotient, not `float(2**53 + 1) / 3.0`, which rounds twice.

## Floor division and modulo

`floordiv` rounds towards negative infinity and `mod` takes the sign of the divisor, for ints and floats:
`floordiv(-7, 2) == -4`, `mod(-7, 2) == 1`, `mod(7.5, -2) == -0.5`. Float results match CPython's `divmod()`
bit for bit, including `floordiv(1.0, 0.1) == 9.0`.

## pow

| arguments | result |
| --- | --- |
| int base, int exponent `>= 0` | exact `int`, `OverflowError` beyond 64 bits |
| int base, int exponent `< 0` | `float`: `pow(2, -1) == 0.5` |
| a `float` on either side | `float` |
| `0` to a negative power | `ZeroDivisionError` |
| a negative base to a fractional power | `ValueError`, where Python returns a `complex` |
| a finite `float` result too large | `OverflowError`, as in Python |

The `ValueError` is the one place where the result differs from `**`: the core has no complex numbers, and
raises what `math.pow()` raises for the same arguments.

## Errors

| exception | when |
| --- | --- |
| `TypeError` | an argument is not an `int` or a `float`, or a `float` where an integer is required |
| `OverflowError` | an `int` argument or result beyond 64 bits; a `float` `pow` too large |
| `ZeroDivisionError` | `div`, `floordiv` or `mod` by zero; `0` to a negative power |
| `ValueError` | `sqrt` of a negative number; `factorial` or `fibonacci` of a negative number; a negative base to a fractional power |
| `MemoryError` | `primes_up_to(n)` when the sieve of `n / 2` bytes cannot be allocated |

## Threads

The extension keeps no state, so calls from any number of threads are safe. `primes_up_to` releases the GIL
while it sieves, so other Python threads run meanwhile. On free-threaded CPython 3.14t the module declares
that it does not need the GIL, and importing it does not turn the GIL back on
([ADR-0004](../adr/0004-abi3-and-free-threaded-wheels.md)).
