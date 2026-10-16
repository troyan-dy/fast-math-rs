# Benchmarks

← [Documentation](../README.md#documentation)

`benchmarks/run.py` times every fast_math function against what a Python program would use instead: the C
builtins of `operator` and `math` where the standard library has them, plain Python where it has not. Each
figure is the best of 7 rounds of about 0.2 s, one call; the script checks first that both sides give the same
result.

```bash
make bench                                     # the table
uv run python benchmarks/run.py --json out.json  # the figures as JSON too
```

## Results

Apple M-series, macOS, CPython 3.14.6, the release build of `uv sync`
([JSON](benchmarks/py3.14-arm64.json)):

| operation | fast_math, µs | baseline | baseline, µs | speedup |
| --- | ---: | --- | ---: | ---: |
| `add(2, 3)` | 0.048 | operator.add | 0.026 | 0.54x |
| `pow(3, 39)` | 0.064 | operator.pow | 0.111 | 1.72x |
| `gcd(2**40, 6**15)` | 0.072 | math.gcd | 0.062 | 0.86x |
| `factorial(20)` | 0.051 | math.factorial | 0.031 | 0.61x |
| `fibonacci(90)` | 0.066 | Python loop | 1.621 | 24.45x |
| `is_prime, 1000 numbers ~10**18` | 896 | Python Miller-Rabin | 4,938 | 5.51x |
| `primes_up_to(10**6)` | 2,208 | Python sieve | 19,848 | 8.99x |

## Reading them

- **One cheap operation per call loses.** `add`, `gcd` and `factorial` are a few nanoseconds of work in Rust
  and in C alike; what is left is the call. A call of a PyO3 function, with two arguments converted from Python
  objects and the result converted back, costs about 20 ns more than a call of a C builtin, which the
  interpreter dispatches without any conversion. `pow(3, 39)` wins because Python's `int` power goes through
  its arbitrary-precision code even for a small result.
- **A loop inside one call wins.** `fibonacci(90)` replaces 90 iterations of the bytecode loop with 90 machine
  additions; `is_prime` does its modular multiplications in `u128` instead of Python ints; `primes_up_to` sieves
  in a `Vec<bool>`, and most of its 2.2 ms is building the list of 78 498 Python ints at the end.
- Use fast_math where a call does real work: a sieve, a primality test, a loop of the core. For `a + b` in a
  Python loop, the operator stays faster.

CI runs `benchmarks/run.py --quick` on every push as a smoke test, so the suite keeps working; the figures of a
shared runner are too noisy to gate on, and this page holds the baseline.
