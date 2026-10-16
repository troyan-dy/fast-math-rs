# abi3 wheels, plus one for free-threaded CPython

The extension is built against the stable ABI of CPython 3.11 (`abi3-py311` of PyO3), so one wheel per
platform serves CPython 3.11, 3.12, 3.13, 3.14 and every later version, without a new release when a new
Python comes out. The stable ABI does not cover free-threaded CPython, so every platform gets a second,
version-specific wheel for 3.14t; maturin builds both from one `--interpreter 3.11 3.14t` run.

The module declares `gil_used = false`: it keeps no state and touches no Python object outside the call that
owns it, so on 3.14t importing it leaves the GIL off (`tests/test_threads.py` checks this without
`PYTHON_GIL=0`, which would force the GIL off and prove nothing). `primes_up_to` releases the GIL while it
sieves, which also helps on a regular interpreter.

The platforms are the ones with GitHub runners or a maturin cross-compilation image: Linux x86_64 and aarch64
for glibc (manylinux) and musl (musllinux), macOS x86_64 and arm64, Windows x64. Anything else installs from
the sdist with a Rust toolchain.

## Considered Options

- **A wheel per Python version**: four to five times the wheels per platform, and a release for every new
  CPython, for a speed-up the stable ABI does not cost in this module (no object internals are touched).
- **No free-threaded wheel**: 3.14t users would build from source, and the GIL would come back on import.
