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
AROUND = 10**18
LARGE = tuple(range(AROUND + 1, AROUND + 2001, 2))
WITNESSES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)  # noqa: WPS221, WPS432 - the first twelve primes
# How long `measure` lets a timeit round run at the least, and microseconds in a second
MIN_ELAPSED = 1e-9
MICROSECONDS = 1e6


# One loop as in the core, with its names: a helper call per witness would slow down the baseline measured
def python_is_prime(n: int) -> bool:  # noqa: WPS231
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
            # The slice assignment is what makes a sieve fast in Python
            composite[i * i :: i] = b"\x01" * len(range(i * i, n + 1, i))  # noqa: WPS221, WPS362
    return [candidate for candidate in range(2, n + 1) if not composite[candidate]]


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


CASES = (
    Case(
        "add(2, 3)",
        lambda: fast_math.add(2, 3),
        lambda: operator.add(2, 3),
        "operator.add",
    ),
    Case(
        "pow(3, 39)",
        lambda: fast_math.pow(3, 39),
        lambda: operator.pow(3, 39),
        "operator.pow",
    ),
    Case(
        "gcd(2**40, 6**15)",
        lambda: fast_math.gcd(2**40, 6**15),
        lambda: math.gcd(2**40, 6**15),
        "math.gcd",
    ),
    Case(
        "factorial(20)",
        lambda: fast_math.factorial(20),
        lambda: math.factorial(20),
        "math.factorial",
    ),
    Case(
        "fibonacci(90)",
        lambda: fast_math.fibonacci(90),
        lambda: python_fibonacci(90),
        "Python loop",
    ),
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
)


@dataclass
class Measurement:
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
    scale = budget / max(elapsed, MIN_ELAPSED)
    number = max(1, int(number * scale))
    return min(timer.repeat(repeat=repeat, number=number)) / number * MICROSECONDS


def run(repeat: int, budget: float) -> list[Measurement]:
    measurements = []
    for case in CASES:
        assert case.fast() == case.baseline(), case.name
        measurements.append(
            Measurement(
                case.name,
                case.baseline_name,
                measure(case.fast, repeat, budget),
                measure(case.baseline, repeat, budget),
            )
        )
    return measurements


def show(micros: float) -> str:
    return format(micros, ",.3f") if micros < 10 else format(micros, ",.0f")


def table(measurements: list[Measurement]) -> str:
    lines = [
        "| operation | fast_math, µs | baseline | baseline, µs | speedup |",
        "| --- | ---: | --- | ---: | ---: |",
    ]
    lines.extend(row(measurement) for measurement in measurements)
    return "\n".join(lines)


def row(measurement: Measurement) -> str:
    fast = show(measurement.fast_us)
    baseline = show(measurement.baseline_us)
    speedup = format(measurement.speedup, ".2f")
    name = f"`{measurement.name}`"
    cells = " | ".join((name, fast, measurement.baseline, baseline, f"{speedup}x"))
    return f"| {cells} |"


def write_json(path: str, measurements: list[Measurement]) -> None:
    with open(path, "w", encoding="utf-8") as output:
        json.dump(
            {
                "python": sys.version,
                "machine": platform.machine(),
                "system": platform.system(),
                "results": [{**asdict(measurement), "speedup": measurement.speedup} for measurement in measurements],
            },
            output,
            indent=2,
        )
        output.write("\n")


def describe() -> str:
    python = platform.python_version()
    machine = platform.machine()
    system = platform.system()
    return f"Python {python} on {machine}, {system}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--quick", action="store_true", help="one short round per case")
    parser.add_argument("--repeat", type=int, default=7, help="rounds per case, the best one counts")
    parser.add_argument("--json", help="also write the figures to this file")
    args = parser.parse_args()

    repeat, budget = (1, 0.01) if args.quick else (args.repeat, 0.2)
    measurements = run(repeat, budget)
    print(describe(), end="\n\n")
    print(table(measurements))
    if args.json:
        write_json(args.json, measurements)


if __name__ == "__main__":
    main()
