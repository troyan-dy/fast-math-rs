# Python is the reference

Each function of fast_math has the semantics of a Python operator or `math` function, and its tests compare
the two on generated arguments rather than on expected values written by hand (`tests/reference.py`): the same
value, the same type, the same sign of a zero, NaN for NaN, and the same exception type. Where the core differs
on purpose, the test states the difference as a change of the reference, so every difference is written down
in one place and in `docs/guide/semantics.md`.

So `floordiv` and `mod` floor as Python does rather than truncate as Rust does, the float versions reproduce
CPython's `divmod()` algorithm, `div` of two ints is correctly rounded as `int / int` is, and `pow` follows the
special cases of CPython's `float_pow` one by one. The differences are two: integers are 64-bit (ADR-0002), and
a negative base to a fractional power raises `ValueError`, as `math.pow()` does, where `**` returns a
`complex`, since the core has no complex numbers.

A user can then swap `a // b` for `fast_math.floordiv(a, b)` without rereading what `//` means.

## Considered Options

- **Rust semantics** (truncating division, remainder with the sign of the dividend, `powf` as libm gives it):
  natural for the implementation, a trap for every Python caller.
- **Hand-written expected values only**: they test the cases their author thought of; hypothesis over the
  whole range found the sign of `0 / -5` and the overflow of a complex power before any user did.
