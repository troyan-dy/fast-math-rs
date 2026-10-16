//! Arithmetic with the semantics of Python's operators: `int` with `int` gives an exact `int`, anything with a
//! `float` gives a `float`. The only departure is the width of an `int`, 64 bits (ADR-0002).

use crate::number::{
    INT_OVERFLOW, MathError, MathResult,
    Number::{self, Float, Int},
};

/// `a + b`
pub fn add(a: Number, b: Number) -> MathResult<Number> {
    match (a, b) {
        (Int(a), Int(b)) => a.checked_add(b).map(Int).ok_or(INT_OVERFLOW),
        _ => Ok(Float(a.to_f64() + b.to_f64())),
    }
}

/// `a - b`
pub fn sub(a: Number, b: Number) -> MathResult<Number> {
    match (a, b) {
        (Int(a), Int(b)) => a.checked_sub(b).map(Int).ok_or(INT_OVERFLOW),
        _ => Ok(Float(a.to_f64() - b.to_f64())),
    }
}

/// `a * b`
pub fn mul(a: Number, b: Number) -> MathResult<Number> {
    match (a, b) {
        (Int(a), Int(b)) => a.checked_mul(b).map(Int).ok_or(INT_OVERFLOW),
        _ => Ok(Float(a.to_f64() * b.to_f64())),
    }
}

/// `a / b`, always a `float`
pub fn div(a: Number, b: Number) -> MathResult<f64> {
    if let (Int(a), Int(b)) = (a, b) {
        return int_true_div(a, b);
    }
    let (a, b) = (a.to_f64(), b.to_f64());
    if b == 0.0 {
        return Err(MathError::DivisionByZero("float division by zero"));
    }
    Ok(a / b)
}

/// `a // b`
pub fn floordiv(a: Number, b: Number) -> MathResult<Number> {
    match (a, b) {
        (Int(a), Int(b)) => int_floordiv(a, b).map(Int),
        _ => float_divmod(a.to_f64(), b.to_f64()).map(|(quotient, _)| Float(quotient)),
    }
}

/// `a % b`: the remainder takes the sign of the divisor
pub fn rem(a: Number, b: Number) -> MathResult<Number> {
    match (a, b) {
        (Int(a), Int(b)) => int_rem(a, b).map(Int),
        _ => float_divmod(a.to_f64(), b.to_f64()).map(|(_, remainder)| Float(remainder)),
    }
}

/// `base ** exp`: an `int` for an `int` base and a non-negative `int` exponent, a `float` otherwise
pub fn pow(base: Number, exp: Number) -> MathResult<Number> {
    match (base, exp) {
        (Int(base), Int(exp)) if exp >= 0 => int_pow(base, exp).map(Int),
        _ => float_pow(base.to_f64(), exp.to_f64()).map(Float),
    }
}

/// `abs(x)`
pub fn abs(x: Number) -> MathResult<Number> {
    match x {
        Int(x) => x.checked_abs().map(Int).ok_or(INT_OVERFLOW),
        Float(x) => Ok(Float(x.abs())),
    }
}

/// `math.sqrt(x)`
pub fn sqrt(x: Number) -> MathResult<f64> {
    let x = x.to_f64();
    // -0.0 is not below zero: its root is -0.0, as in Python
    if x < 0.0 {
        return Err(MathError::Domain("math domain error"));
    }
    Ok(x.sqrt())
}

const INT_DIVISION_BY_ZERO: MathError = MathError::DivisionByZero("integer division or modulo by zero");

fn int_floordiv(a: i64, b: i64) -> MathResult<i64> {
    if b == 0 {
        return Err(INT_DIVISION_BY_ZERO);
    }
    // i64::MIN // -1 is the one quotient that does not fit
    let quotient = a.checked_div(b).ok_or(INT_OVERFLOW)?;
    // Rust truncates towards zero, Python floors
    if a % b != 0 && (a < 0) != (b < 0) {
        Ok(quotient - 1)
    } else {
        Ok(quotient)
    }
}

fn int_rem(a: i64, b: i64) -> MathResult<i64> {
    if b == 0 {
        return Err(INT_DIVISION_BY_ZERO);
    }
    // None only for i64::MIN % -1, whose remainder is 0
    let remainder = a.checked_rem(b).unwrap_or(0);
    if remainder != 0 && (remainder < 0) != (b < 0) {
        Ok(remainder + b)
    } else {
        Ok(remainder)
    }
}

/// `a / b` for two integers, correctly rounded as Python's `int.__truediv__` is, also beyond 2**53 where
/// `a as f64 / b as f64` would round twice.
fn int_true_div(a: i64, b: i64) -> MathResult<f64> {
    if b == 0 {
        return Err(MathError::DivisionByZero("division by zero"));
    }
    if a == 0 {
        // Signed like any other quotient: 0 / -5 is -0.0
        return Ok(if b < 0 { -0.0 } else { 0.0 });
    }
    // The numerator is shifted up to the top bit of a u128, so the quotient keeps at least 63 significant bits:
    // more than the 53 of an f64 plus a guard bit, and a sticky bit below them carries an inexact remainder
    let shift = u128::from(a.unsigned_abs()).leading_zeros();
    let numerator = u128::from(a.unsigned_abs()) << shift;
    let denominator = u128::from(b.unsigned_abs());
    let quotient = (numerator / denominator) | u128::from(numerator % denominator != 0);
    // One rounding in the cast; the scaling by a power of two is exact, the result is far from subnormal
    let magnitude = quotient as f64 * 2f64.powi(-(shift as i32));
    Ok(if (a < 0) == (b < 0) { magnitude } else { -magnitude })
}

/// Python's `divmod()` of two floats, as `float_divmod` of `CPython` computes it
fn float_divmod(a: f64, b: f64) -> MathResult<(f64, f64)> {
    if b == 0.0 {
        return Err(MathError::DivisionByZero("float divmod()"));
    }
    let mut remainder = a % b;
    let mut quotient = (a - remainder) / b;
    if remainder == 0.0 {
        remainder = 0f64.copysign(b);
    } else if (b < 0.0) != (remainder < 0.0) {
        remainder += b;
        quotient -= 1.0;
    }
    let floor = if quotient == 0.0 {
        0f64.copysign(a / b)
    } else {
        let floor = quotient.floor();
        if quotient - floor > 0.5 { floor + 1.0 } else { floor }
    };
    Ok((floor, remainder))
}

fn int_pow(base: i64, exp: i64) -> MathResult<i64> {
    match base {
        0 => Ok(i64::from(exp == 0)),
        1 => Ok(1),
        -1 => Ok(if exp % 2 == 0 { 1 } else { -1 }),
        _ => u32::try_from(exp)
            .ok()
            .and_then(|exp| base.checked_pow(exp))
            .ok_or(INT_OVERFLOW),
    }
}

fn is_odd_integer(x: f64) -> bool {
    x % 2.0 == 1.0 || x % 2.0 == -1.0
}

/// Python's `float.__pow__`, case by case as `float_pow` of `CPython`, with one departure: a negative base and
/// a fractional exponent give a complex number in Python, and a `ValueError` here, as in `math.pow()`
fn float_pow(base: f64, exp: f64) -> MathResult<f64> {
    if exp == 0.0 {
        return Ok(1.0);
    }
    if base.is_nan() {
        return Ok(base);
    }
    if exp.is_nan() {
        return Ok(if base == 1.0 { 1.0 } else { exp });
    }
    if exp.is_infinite() {
        let base = base.abs();
        return Ok(if base == 1.0 {
            1.0
        } else if (exp > 0.0) == (base > 1.0) {
            f64::INFINITY
        } else {
            0.0
        });
    }
    if base.is_infinite() {
        let odd = is_odd_integer(exp);
        return Ok(match (exp > 0.0, odd) {
            (true, true) => base,
            (true, false) => base.abs(),
            (false, true) => 0f64.copysign(base),
            (false, false) => 0.0,
        });
    }
    if base == 0.0 {
        if exp < 0.0 {
            return Err(MathError::DivisionByZero("zero to a negative power"));
        }
        return Ok(if is_odd_integer(exp) { base } else { 0.0 });
    }
    let mut magnitude = base;
    let mut negate = false;
    if base < 0.0 {
        if exp != exp.floor() {
            return Err(MathError::Domain("negative number to a fractional power"));
        }
        magnitude = -base;
        negate = is_odd_integer(exp);
    }
    let result = if magnitude == 1.0 { 1.0 } else { magnitude.powf(exp) };
    if result.is_infinite() {
        return Err(MathError::Overflow("float result too large"));
    }
    Ok(if negate { -result } else { result })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn int_operations_overflow_instead_of_wrapping() {
        assert_eq!(add(Int(i64::MAX), Int(1)), Err(INT_OVERFLOW));
        assert_eq!(sub(Int(i64::MIN), Int(1)), Err(INT_OVERFLOW));
        assert_eq!(mul(Int(i64::MAX), Int(2)), Err(INT_OVERFLOW));
        assert_eq!(abs(Int(i64::MIN)), Err(INT_OVERFLOW));
        assert_eq!(floordiv(Int(i64::MIN), Int(-1)), Err(INT_OVERFLOW));
        assert_eq!(pow(Int(2), Int(63)), Err(INT_OVERFLOW));
    }

    #[test]
    fn int_division_floors() {
        assert_eq!(floordiv(Int(7), Int(-2)), Ok(Int(-4)));
        assert_eq!(floordiv(Int(-7), Int(2)), Ok(Int(-4)));
        assert_eq!(rem(Int(7), Int(-2)), Ok(Int(-1)));
        assert_eq!(rem(Int(-7), Int(2)), Ok(Int(1)));
        assert_eq!(rem(Int(i64::MIN), Int(-1)), Ok(Int(0)));
    }

    #[test]
    fn int_true_division_rounds_once() {
        // float(2**53 + 1) / 3 rounds the numerator first and gives a different last bit
        let a = (1i64 << 53) + 1;
        assert_eq!(div(Int(a), Int(3)), Ok(3_002_399_751_580_331.0));
        assert_eq!(div(Int(1), Int(3)), Ok(1.0 / 3.0));
        assert_eq!(div(Int(-1), Int(i64::MIN)), Ok(2f64.powi(-63)));
    }

    #[test]
    fn pow_powers_of_one_and_zero_never_overflow() {
        assert_eq!(pow(Int(1), Int(i64::MAX)), Ok(Int(1)));
        assert_eq!(pow(Int(-1), Int(i64::MAX)), Ok(Int(-1)));
        assert_eq!(pow(Int(0), Int(0)), Ok(Int(1)));
        assert_eq!(pow(Int(0), Int(i64::MAX)), Ok(Int(0)));
    }

    #[test]
    fn errors() {
        assert!(matches!(div(Int(1), Int(0)), Err(MathError::DivisionByZero(_))));
        assert!(matches!(rem(Float(1.0), Int(0)), Err(MathError::DivisionByZero(_))));
        assert!(matches!(pow(Int(0), Int(-1)), Err(MathError::DivisionByZero(_))));
        assert!(matches!(pow(Float(-8.0), Float(1.0 / 3.0)), Err(MathError::Domain(_))));
        assert!(matches!(pow(Float(10.0), Float(400.0)), Err(MathError::Overflow(_))));
        assert!(matches!(sqrt(Int(-1)), Err(MathError::Domain(_))));
    }
}
