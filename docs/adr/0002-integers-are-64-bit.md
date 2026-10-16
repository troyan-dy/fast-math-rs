# Integers are 64-bit, and an overflow raises

A Python `int` has no upper bound; a machine integer has. fast_math computes on `i64`, the width at which the
core is fast, and every integer operation is checked: a result outside `[-2**63, 2**63 - 1]` raises
`OverflowError`, and so does an `int` argument outside that range. The result of an operation is therefore
either exactly Python's result or an exception, never a different number.

This makes `factorial` stop at 20 and `fibonacci` at 92, which is the honest limit of a 64-bit library. A
caller that needs bigger numbers needs Python's own arbitrary-precision integers, which are already fast at
that size.

## Considered Options

- **Wrap around**, as Rust's release builds and NumPy do: a wrong number with no sign of it.
- **Saturate at the bounds**: a wrong number too, only a less surprising one.
- **Fall back to `float`** past 64 bits: changes the type of a result with the value of its arguments, and
  loses precision silently.
- **Arbitrary precision through `num-bigint`**: a second implementation of what Python's `int` already does in
  C, at a conversion cost on every call, for no gain over the operator.
- **`i128`**: a slower conversion of every argument for a limit that moves but stays (`factorial` would stop
  at 33, `fibonacci` at 184); 64 bits is also the integer of NumPy, databases and most data.
