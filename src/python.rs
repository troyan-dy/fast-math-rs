//! The Python bindings, built by maturin with the `python` feature: conversions between Python objects and
//! `Number`, `MathError` into exceptions, and the `fast_math._core` module.

use std::convert::Infallible;

use pyo3::exceptions::{PyMemoryError, PyOverflowError, PyTypeError, PyValueError, PyZeroDivisionError};
use pyo3::prelude::*;
use pyo3::types::{PyFloat, PyInt};

use crate::number::{MathError, Number};

impl From<MathError> for PyErr {
    fn from(error: MathError) -> Self {
        match error {
            MathError::Overflow(message) => PyOverflowError::new_err(message),
            MathError::DivisionByZero(message) => PyZeroDivisionError::new_err(message),
            MathError::Domain(message) => PyValueError::new_err(message),
            MathError::Memory(message) => PyMemoryError::new_err(message),
        }
    }
}

/// An `int` (a `bool` too, as everywhere in Python) or a `float`, subclasses included. An `int` beyond 64 bits
/// raises `OverflowError`; it is never rounded to a `float`.
impl<'py> FromPyObject<'_, 'py> for Number {
    type Error = PyErr;

    fn extract(obj: Borrowed<'_, 'py, PyAny>) -> PyResult<Self> {
        if let Ok(value) = obj.cast::<PyFloat>() {
            return Ok(Number::Float(value.value()));
        }
        if obj.is_instance_of::<PyInt>() {
            return Ok(Number::Int(obj.extract()?));
        }
        Err(PyTypeError::new_err(format!(
            "expected int or float, got {}",
            obj.get_type().name()?
        )))
    }
}

impl<'py> IntoPyObject<'py> for Number {
    type Target = PyAny;
    type Output = Bound<'py, PyAny>;
    type Error = Infallible;

    fn into_pyobject(self, py: Python<'py>) -> Result<Self::Output, Self::Error> {
        Ok(match self {
            Number::Int(value) => value.into_pyobject(py)?.into_any(),
            Number::Float(value) => PyFloat::new(py, value).into_any(),
        })
    }
}

// The module keeps no state and touches no Python object outside a call, so it runs without the GIL on a
// free-threaded interpreter
#[pymodule(gil_used = false)]
mod _core {
    use pyo3::prelude::*;

    use crate::number::Number;
    use crate::{arith, theory};

    /// a + b
    #[pyfunction]
    fn add(a: Number, b: Number) -> PyResult<Number> {
        Ok(arith::add(a, b)?)
    }

    /// a - b
    #[pyfunction]
    fn sub(a: Number, b: Number) -> PyResult<Number> {
        Ok(arith::sub(a, b)?)
    }

    /// a * b
    #[pyfunction]
    fn mul(a: Number, b: Number) -> PyResult<Number> {
        Ok(arith::mul(a, b)?)
    }

    /// a / b, always a float
    #[pyfunction]
    fn div(a: Number, b: Number) -> PyResult<f64> {
        Ok(arith::div(a, b)?)
    }

    /// a // b, rounded towards negative infinity
    #[pyfunction]
    fn floordiv(a: Number, b: Number) -> PyResult<Number> {
        Ok(arith::floordiv(a, b)?)
    }

    /// a % b, with the sign of b
    #[pyfunction(name = "mod")]
    fn rem(a: Number, b: Number) -> PyResult<Number> {
        Ok(arith::rem(a, b)?)
    }

    /// base ** exp
    #[pyfunction]
    fn pow(base: Number, exp: Number) -> PyResult<Number> {
        Ok(arith::pow(base, exp)?)
    }

    /// abs(x)
    #[pyfunction]
    fn abs(x: Number) -> PyResult<Number> {
        Ok(arith::abs(x)?)
    }

    /// The square root of x, as math.sqrt(x)
    #[pyfunction]
    fn sqrt(x: Number) -> PyResult<f64> {
        Ok(arith::sqrt(x)?)
    }

    /// The greatest common divisor of a and b, never negative
    #[pyfunction]
    fn gcd(a: i64, b: i64) -> PyResult<i64> {
        Ok(theory::gcd(a, b)?)
    }

    /// The least common multiple of a and b, never negative
    #[pyfunction]
    fn lcm(a: i64, b: i64) -> PyResult<i64> {
        Ok(theory::lcm(a, b)?)
    }

    /// n!
    #[pyfunction]
    fn factorial(n: i64) -> PyResult<i64> {
        Ok(theory::factorial(n)?)
    }

    /// The n-th Fibonacci number: fibonacci(0) == 0, fibonacci(1) == 1
    #[pyfunction]
    fn fibonacci(n: i64) -> PyResult<i64> {
        Ok(theory::fibonacci(n)?)
    }

    /// Whether n is a prime number
    #[pyfunction]
    fn is_prime(n: i64) -> bool {
        theory::is_prime(n)
    }

    /// Every prime up to and including n, ascending
    #[pyfunction]
    fn primes_up_to(py: Python<'_>, n: i64) -> PyResult<Vec<i64>> {
        // The sieve can run for seconds: other Python threads keep running meanwhile
        Ok(py.detach(|| theory::primes_up_to(n))?)
    }
}
