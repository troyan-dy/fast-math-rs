"""
fast_math against what a Python program would use instead: the C builtins of `operator` and `math`, or plain
Python where the standard library has nothing.

    python benchmarks/run.py                     the table, see docs/benchmarks.md
    python benchmarks/run.py --quick             one short round, as CI runs it
    python benchmarks/run.py --json out.json     the figures as JSON too
"""

import argparse
import json
import math
import operator
import platform
import sys
import timeit
from collections.abc import Callable
from dataclasses import asdict, dataclass

import fast_math

# Odd numbers around 10**18: most composite, some prime, every one a full Miller-Rabin test for a prime
LARGE = list(range(10**18 + 1, 10**18 + 2001, 2))
WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def python_is_prime(n: int) -> bool:
    """The same deterministic Miller-Rabin test as the core, in Python."""
    if n < 2:
        return False
    for p in WITNESSES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d, s = d // 2, s + 1
    for a in WITNESSES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def python_primes_up_to(n: int) -> list[int]:
    """A sieve of Eratosthenes with bytearray slices, about as fast as Python gets without NumPy."""
    if n < 2:
        return []
    composite = bytearray(n + 1)
    for i in range(2, math.isqrt(n) + 1):
        if not composite[i]:
            composite[i * i :: i] = b"\x01" * len(range(i * i, n + 1, i))
    return [i for i in range(2, n + 1) if not composite[i]]


def python_fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@dataclass
class Case:
    name: str
    fast: Callable[[], object]
    baseline: Callable[[], object]
    baseline_name: str


CASES = [
    Case("add(2, 3)", lambda: fast_math.add(2, 3), lambda: operator.add(2, 3), "operator.add"),
    Case("pow(3, 39)", lambda: fast_math.pow(3, 39), lambda: operator.pow(3, 39), "operator.pow"),
    Case("gcd(2**40, 6**15)", lambda: fast_math.gcd(2**40, 6**15), lambda: math.gcd(2**40, 6**15), "math.gcd"),
    Case("factorial(20)", lambda: fast_math.factorial(20), lambda: math.factorial(20), "math.factorial"),
    Case("fibonacci(90)", lambda: fast_math.fibonacci(90), lambda: python_fibonacci(90), "Python loop"),
    Case(
        "is_prime, 1000 numbers ~10**18",
        lambda: [fast_math.is_prime(n) for n in LARGE],
        lambda: [python_is_prime(n) for n in LARGE],
        "Python Miller-Rabin",
    ),
    Case(
        "primes_up_to(10**6)",
        lambda: fast_math.primes_up_to(10**6),
        lambda: python_primes_up_to(10**6),
        "Python sieve",
    ),
]


@dataclass
class Result:
    name: str
    baseline: str
    fast_us: float
    baseline_us: float

    @property
    def speedup(self) -> float:
        return self.baseline_us / self.fast_us


def measure(call: Callable[[], object], repeat: int, budget: float) -> float:
    """The best time of one call in microseconds, over `repeat` rounds of about `budget` seconds each."""
    timer = timeit.Timer(call)
    number, elapsed = timer.autorange()
    number = max(1, int(number * budget / max(elapsed, 1e-9)))
    return min(timer.repeat(repeat=repeat, number=number)) / number * 1e6


def run(repeat: int, budget: float) -> list[Result]:
    results = []
    for case in CASES:
        assert case.fast() == case.baseline(), case.name
        results.append(
            Result(
                case.name,
                case.baseline_name,
                measure(case.fast, repeat, budget),
                measure(case.baseline, repeat, budget),
            )
        )
    return results


def show(value: float) -> str:
    return f"{value:,.3f}" if value < 10 else f"{value:,.0f}"


def table(results: list[Result]) -> str:
    lines = [
        "| operation | fast_math, µs | baseline | baseline, µs | speedup |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| `{result.name}` | {show(result.fast_us)} | {result.baseline} | {show(result.baseline_us)} "
            f"| {result.speedup:.2f}x |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="one short round per case")
    parser.add_argument("--repeat", type=int, default=7, help="rounds per case, the best one counts")
    parser.add_argument("--json", help="also write the figures to this file")
    args = parser.parse_args()

    repeat, budget = (1, 0.01) if args.quick else (args.repeat, 0.2)
    results = run(repeat, budget)
    print(f"Python {platform.python_version()} on {platform.machine()}, {platform.system()}\n")
    print(table(results))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "python": sys.version,
                    "machine": platform.machine(),
                    "system": platform.system(),
                    "results": [{**asdict(result), "speedup": result.speedup} for result in results],
                },
                file,
                indent=2,
            )
            file.write("\n")


if __name__ == "__main__":
    main()
