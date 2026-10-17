# fast-math-rs

Arithmetic and number theory on Python numbers, computed by a Rust core.

## Language

**Core**:
The Rust code that computes: `src/arith.rs`, `src/theory.rs` and `src/number.rs`. It knows nothing of Python and
is tested by `cargo test` on its own.
_Avoid_: Backend, engine, native code

**Bindings**:
`src/python.rs`: the conversion of Python objects into **Numbers**, of **Math errors** into exceptions, and the
`fast_math._core` module. Built only with the `python` cargo feature.
_Avoid_: Wrapper, glue, FFI layer

**Extension**:
The compiled module `fast_math._core` that maturin builds from the **Core** and the **Bindings**; the package
`fast_math` re-exports it.
_Avoid_: Shared library, `.so`

**Number**:
An argument or result of an arithmetic operation: an **Integer** or a **Float**.
_Avoid_: Value, scalar, numeric

**Integer**:
A Python `int` (or `bool`) in `[-2**63, 2**63 - 1]`, an `i64` in the **Core** (ADR-0002).
_Avoid_: Long, bigint, int64 (in prose)

**Float**:
A Python `float`, an `f64` in the **Core**.
_Avoid_: Double, real, decimal

**Overflow**:
An **Integer** result or argument outside 64 bits, or a finite **Float** `pow` whose result is infinite;
raises `OverflowError`. Never a wrapped, saturated or rounded result.
_Avoid_: Wrap-around, truncation

**Reference**:
The Python operator or `math` function whose semantics a fast_math function has; the tests compare the two
on generated arguments (ADR-0003).
_Avoid_: Oracle, spec, expected value

**Departure**:
A documented case where fast_math differs from its **Reference** on purpose: **Overflow** of **Integers**, and
`ValueError` for a negative base to a fractional power.
_Avoid_: Bug, incompatibility, quirk

**Math error**:
`MathError` of the **Core**: overflow, division by zero, domain or memory; each kind is one Python exception.
_Avoid_: Failure, exception (inside the Core)
