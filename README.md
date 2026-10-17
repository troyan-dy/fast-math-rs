# fast-math-rs

[![PyPI](https://img.shields.io/pypi/v/fast-math-rs)](https://pypi.org/project/fast-math-rs/)
[![Python](https://img.shields.io/pypi/pyversions/fast-math-rs)](https://pypi.org/project/fast-math-rs/)
[![CI](https://github.com/troyan-dy/fast_math/actions/workflows/ci.yml/badge.svg)](https://github.com/troyan-dy/fast_math/actions/workflows/ci.yml)
[![License](https://img.shields.io/pypi/l/fast-math-rs)](LICENSE)

Arithmetic and number theory on Python numbers, implemented in Rust.

Every function behaves as the Python operator or `math` function of the same name: `int` with `int` gives an
exact `int`, anything with a `float` gives a `float`, `-7 // 2` is `-4`, and the errors are Python's own. The one
difference is the width of an integer: 64 bits, and a result that does not fit raises `OverflowError` instead of
growing. The core is written in Rust with [PyO3](https://pyo3.rs), ships as one wheel per platform for every
CPython from 3.11 on, and runs without the GIL on free-threaded Python.

- [Installation](#installation) · [Quick start](#quick-start) · [Functions](#functions) · [Performance](#performance)
- [Documentation](#documentation)

## Installation

```bash
pip install fast-math-rs
```

The distribution is `fast-math-rs` (PyPI keeps `fast-math` for the older `fastmath`); the module it installs
is `fast_math`.

Requires CPython 3.11+. Wheels: Linux (x86_64, aarch64; glibc and musl), macOS (x86_64, arm64) and Windows
(x64), each an abi3 wheel plus one for free-threaded CPython 3.14t. Elsewhere pip builds the sdist, which needs
a Rust toolchain.

## Quick start

```pycon
>>> import fast_math as fm
>>> fm.add(2, 3)
5
>>> fm.add(2, 0.5)
2.5
>>> fm.div(7, 2)
3.5
>>> fm.floordiv(-7, 2), fm.mod(-7, 2)
(-4, 1)
>>> fm.pow(2, 10), fm.pow(2, -1)
(1024, 0.5)
>>> fm.gcd(12, 18), fm.lcm(4, 6)
(6, 12)
>>> fm.is_prime(2**61 - 1)
True
>>> fm.primes_up_to(30)
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

```

An integer result beyond 64 bits raises instead of wrapping around or losing precision:

```pycon
>>> fm.add(2**63 - 1, 1)
Traceback (most recent call last):
  ...
OverflowError: integer result does not fit into 64 bits
>>> fm.factorial(21)
Traceback (most recent call last):
  ...
OverflowError: integer result does not fit into 64 bits

```

## Functions

| function | Python equivalent | result |
| --- | --- | --- |
| `add(a, b)`, `sub(a, b)`, `mul(a, b)` | `a + b`, `a - b`, `a * b` | `int` for two ints, `float` otherwise |
| `div(a, b)` | `a / b` | always `float`, correctly rounded for two ints |
| `floordiv(a, b)`, `mod(a, b)` | `a // b`, `a % b` | floored: the remainder has the sign of `b` |
| `pow(base, exp)` | `base ** exp` | `int` for an int base and a non-negative int exponent |
| `abs(x)` | `abs(x)` | the type of `x` |
| `sqrt(x)` | `math.sqrt(x)` | `float` |
| `gcd(a, b)`, `lcm(a, b)` | `math.gcd(a, b)`, `math.lcm(a, b)` | `int`, never negative |
| `factorial(n)` | `math.factorial(n)` | `int`, up to `factorial(20)` |
| `fibonacci(n)` | — | `int`, `fibonacci(0) == 0`, up to `fibonacci(92)` |
| `is_prime(n)` | — | `bool`, exact for every 64-bit integer |
| `primes_up_to(n)` | — | `list[int]` of the primes `<= n`, without the GIL meanwhile |

Arguments are `int` (and `bool`) or `float`; anything else raises `TypeError`, an `int` beyond 64 bits
`OverflowError`. Every difference from Python is listed in [Semantics](docs/guide/semantics.md).

## Performance

A call into Rust costs about 20 ns more than a call of a C builtin, so `fast_math.add` is slower than `a + b`;
the core pays off where it does the work in a loop. On an Apple M-series CPU, Python 3.14:

| operation | fast_math | baseline | speedup |
| --- | ---: | --- | ---: |
| `add(2, 3)` | 48 ns | `operator.add`, 26 ns | 0.54x |
| `fibonacci(90)` | 66 ns | Python loop, 1.6 µs | 24x |
| `is_prime`, 1000 numbers near 10**18 | 0.90 ms | Python Miller-Rabin, 4.9 ms | 5.5x |
| `primes_up_to(10**6)` | 2.2 ms | Python sieve, 19.8 ms | 9.0x |

Every case and how to rerun them: [Benchmarks](docs/benchmarks.md).

## Documentation

- [Semantics](docs/guide/semantics.md): what Python semantics means here, the 64-bit integers, every error
- [Development](docs/guide/development.md): the toolchain, `make` targets, CI and releases
- [Benchmarks](docs/benchmarks.md)
- [Decisions](docs/adr/): why Rust, why 64 bits, why Python is the reference, why these wheels
- [Changelog](CHANGELOG.md)

## License

[MIT](LICENSE)
