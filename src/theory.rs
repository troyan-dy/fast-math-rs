//! Number theory on 64-bit integers.

use crate::number::{INT_OVERFLOW, MathError, MathResult};

// The first 12 primes are witnesses enough for every n below 3.3 * 10**24
const WITNESSES: [u64; 12] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37];

const SIEVE_TOO_LARGE: MathError = MathError::Memory("the sieve does not fit into memory");

/// `math.gcd(a, b)`: never negative
pub fn gcd(a: i64, b: i64) -> MathResult<i64> {
    // gcd(i64::MIN, 0) is 2**63, one above i64::MAX
    i64::try_from(gcd_u64(a.unsigned_abs(), b.unsigned_abs())).map_err(|_| INT_OVERFLOW)
}

/// `math.lcm(a, b)`: never negative, 0 when either is 0
pub fn lcm(a: i64, b: i64) -> MathResult<i64> {
    if a == 0 || b == 0 {
        return Ok(0);
    }
    let (a, b) = (a.unsigned_abs(), b.unsigned_abs());
    (a / gcd_u64(a, b))
        .checked_mul(b)
        .and_then(|lcm| i64::try_from(lcm).ok())
        .ok_or(INT_OVERFLOW)
}

/// `math.factorial(n)`; 20! is the largest that fits
pub fn factorial(n: i64) -> MathResult<i64> {
    if n < 0 {
        return Err(MathError::Domain("factorial() not defined for negative values"));
    }
    (2..=n).try_fold(1i64, i64::checked_mul).ok_or(INT_OVERFLOW)
}

/// The n-th Fibonacci number, F(0) = 0 and F(1) = 1; F(92) is the largest that fits
pub fn fibonacci(n: i64) -> MathResult<i64> {
    if n < 0 {
        return Err(MathError::Domain("fibonacci() not defined for negative values"));
    }
    // Starts from F(-1) = 1, so that the last step computes F(n) and nothing past it
    let (mut previous, mut current) = (1i64, 0i64);
    for _ in 0..n {
        (previous, current) = (current, previous.checked_add(current).ok_or(INT_OVERFLOW)?);
    }
    Ok(current)
}

/// Whether `n` is prime: a deterministic Miller–Rabin test, exact for every 64-bit integer
#[must_use]
pub fn is_prime(n: i64) -> bool {
    let Ok(n) = u64::try_from(n) else {
        return false;
    };
    if n < 2 {
        return false;
    }
    for p in WITNESSES {
        if n % p == 0 {
            return n == p;
        }
    }
    let s = (n - 1).trailing_zeros();
    let d = (n - 1) >> s;
    'witness: for a in WITNESSES {
        let mut x = pow_mod(a, d, n);
        if x == 1 || x == n - 1 {
            continue;
        }
        for _ in 1..s {
            x = mul_mod(x, x, n);
            if x == n - 1 {
                continue 'witness;
            }
        }
        return false;
    }
    true
}

/// Every prime up to and including `n`, ascending: a sieve of Eratosthenes over the odd numbers
pub fn primes_up_to(n: i64) -> MathResult<Vec<i64>> {
    if n < 2 {
        return Ok(Vec::new());
    }
    let n = usize::try_from(n).map_err(|_| SIEVE_TOO_LARGE)?;
    // composite[i] is for the odd number 2 * i + 1
    let size = n / 2 + 1;
    let mut composite = Vec::new();
    composite.try_reserve_exact(size).map_err(|_| SIEVE_TOO_LARGE)?;
    composite.resize(size, false);
    let mut i = 3;
    while i * i <= n {
        if !composite[i / 2] {
            for multiple in (i * i..=n).step_by(2 * i) {
                composite[multiple / 2] = true;
            }
        }
        i += 2;
    }
    let mut primes = vec![2];
    primes.extend(
        (1..size)
            .filter(|&k| !composite[k] && 2 * k < n)
            .map(|k| (2 * k + 1) as i64),
    );
    Ok(primes)
}

fn gcd_u64(mut a: u64, mut b: u64) -> u64 {
    while b != 0 {
        (a, b) = (b, a % b);
    }
    a
}

fn mul_mod(a: u64, b: u64, m: u64) -> u64 {
    (u128::from(a) * u128::from(b) % u128::from(m)) as u64
}

fn pow_mod(mut base: u64, mut exp: u64, m: u64) -> u64 {
    let mut result = 1;
    base %= m;
    while exp > 0 {
        if exp & 1 == 1 {
            result = mul_mod(result, base, m);
        }
        base = mul_mod(base, base, m);
        exp >>= 1;
    }
    result
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gcd_and_lcm() {
        assert_eq!(gcd(12, -18), Ok(6));
        assert_eq!(gcd(0, 0), Ok(0));
        assert_eq!(gcd(i64::MIN, 0), Err(INT_OVERFLOW));
        assert_eq!(gcd(i64::MIN, 6), Ok(2));
        assert_eq!(lcm(4, -6), Ok(12));
        assert_eq!(lcm(0, 5), Ok(0));
        assert_eq!(lcm(i64::MAX, i64::MAX - 1), Err(INT_OVERFLOW));
    }

    #[test]
    fn factorial_and_fibonacci_limits() {
        assert_eq!(factorial(0), Ok(1));
        assert_eq!(factorial(20), Ok(2_432_902_008_176_640_000));
        assert_eq!(factorial(21), Err(INT_OVERFLOW));
        assert_eq!(fibonacci(0), Ok(0));
        assert_eq!(fibonacci(92), Ok(7_540_113_804_746_346_429));
        assert_eq!(fibonacci(93), Err(INT_OVERFLOW));
        assert!(matches!(factorial(-1), Err(MathError::Domain(_))));
    }

    #[test]
    fn primality_agrees_with_the_sieve() {
        let sieve = primes_up_to(10_000).unwrap();
        let tested: Vec<i64> = (-10..=10_000).filter(|&n| is_prime(n)).collect();
        assert_eq!(tested, sieve);
        assert_eq!(&sieve[..5], &[2, 3, 5, 7, 11]);
    }

    #[test]
    fn primality_of_large_numbers() {
        // The largest prime below 2**63, 2**63 - 1 = 7**2 * 73 * ..., and a strong pseudoprime to the bases 2..=23
        // that only the witnesses 29, 31 and 37 tell from a prime
        assert!(is_prime(9_223_372_036_854_775_783));
        assert!(!is_prime(9_223_372_036_854_775_807));
        assert!(!is_prime(3_825_123_056_546_413_051));
    }

    #[test]
    fn sieve_edges() {
        assert_eq!(primes_up_to(1), Ok(vec![]));
        assert_eq!(primes_up_to(2), Ok(vec![2]));
        assert_eq!(primes_up_to(3), Ok(vec![2, 3]));
        assert_eq!(primes_up_to(9), Ok(vec![2, 3, 5, 7]));
        assert_eq!(primes_up_to(11), Ok(vec![2, 3, 5, 7, 11]));
    }
}
