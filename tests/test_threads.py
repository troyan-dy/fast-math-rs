"""
Calls from many threads at once give the results of one thread; on a free-threaded interpreter the extension
keeps the GIL off (ADR-0004).
"""

import sys
import sysconfig
from concurrent.futures import ThreadPoolExecutor

import pytest

import fast_math

THREADS = 8

FREE_THREADED = bool(sysconfig.get_config_var("Py_GIL_DISABLED"))


def work(n: int) -> tuple[int, int, bool, int]:
    primes = fast_math.primes_up_to(200_000 + n)
    return len(primes), fast_math.gcd(n * 6, 4), fast_math.is_prime(2**61 - 1), fast_math.add(n, n)


def test_concurrent_calls() -> None:
    with ThreadPoolExecutor(THREADS) as pool:
        results = list(pool.map(work, range(64)))
    assert results == [work(n) for n in range(64)]


@pytest.mark.skipif(not FREE_THREADED, reason="the GIL is only off on a free-threaded interpreter")
def test_gil_stays_off() -> None:
    assert not sys._is_gil_enabled()  # type: ignore[attr-defined,unused-ignore]  # new in 3.13
