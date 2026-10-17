# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.0] - 2026-10-17

### Added

- The Rust core and its Python package `fast_math`:
  - arithmetic with the semantics of the Python operators: `add`, `sub`, `mul`, `div`, `floordiv`, `mod`,
    `pow`, `abs`, `sqrt`; an `int` with an `int` gives an `int`, anything with a `float` a `float`;
  - number theory on 64-bit integers: `gcd`, `lcm`, `factorial`, `fibonacci`, `is_prime` (a deterministic
    Miller-Rabin test, exact for every 64-bit integer) and `primes_up_to` (a sieve that releases the GIL).
- 64-bit integers with checked arithmetic: a result or an argument beyond 64 bits raises `OverflowError`.
- Type stubs, checked against the extension by `stubtest`, and `py.typed`.
- abi3 wheels for CPython 3.11+ and wheels for free-threaded CPython 3.14t, on which the module keeps the GIL
  off; Linux (glibc, musl; x86_64, aarch64), macOS (x86_64, arm64) and Windows (x64).
- Property tests of every function against Python itself with hypothesis, Rust unit tests of the core, and
  benchmarks against the builtins and plain Python (`docs/benchmarks.md`).

[Unreleased]: https://github.com/troyan-dy/fast_math/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/troyan-dy/fast_math/releases/tag/v0.1.0
