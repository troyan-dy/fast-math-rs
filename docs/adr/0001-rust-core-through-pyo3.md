# The core is Rust, bound through PyO3 and built with maturin

fast_math exists to do the math in Rust and call it from Python. The operations live in plain Rust modules
(`src/arith.rs`, `src/theory.rs`) that know nothing of Python, and one module (`src/python.rs`) converts
arguments, maps errors to exceptions and declares `fast_math._core`. The bindings are behind the `python` cargo
feature, which maturin turns on: `cargo test` then runs the unit tests of the core without linking an
interpreter, which is what makes them run the same on every CI runner. The Python package `fast_math` is a thin
re-export with a typed stub, so the public names and their types are reviewed in Python, and `stubtest` holds
the stub to the module.

maturin is the build backend, so `pip install`, `uv sync` and `uv build` all build the extension with no
`setup.py`, and `uv run` rebuilds it when a Rust source changes (`cache-keys` in `pyproject.toml`).

## Considered Options

- **C extension or Cython**: no memory safety, no checked integer arithmetic in the language, and a C toolchain
  per platform all the same.
- **ctypes / cffi over a Rust `cdylib`**: every call pays the foreign-function marshalling of ctypes, several
  times the cost of a PyO3 call, and the types of the arguments are checked by hand.
- **rust-cpython, or raw `pyo3-ffi`**: unmaintained, or all the reference counting by hand.
