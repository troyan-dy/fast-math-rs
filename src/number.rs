//! The numbers of the core and the errors of its operations, free of Python.

/// A Python `int` that fits into 64 bits, or a Python `float`.
#[derive(Clone, Copy, Debug, PartialEq)]
pub enum Number {
    Int(i64),
    Float(f64),
}

impl Number {
    /// The value as Python's `float(x)` gives it: an `i64` is rounded to the nearest `f64`, ties to even.
    #[must_use]
    pub fn to_f64(self) -> f64 {
        match self {
            Number::Int(value) => value as f64,
            Number::Float(value) => value,
        }
    }
}

/// Why an operation has no result; each kind is the Python exception the bindings raise.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum MathError {
    /// `OverflowError`: an integer result does not fit into 64 bits, or a float result is infinite from finite
    /// operands
    Overflow(&'static str),
    /// `ZeroDivisionError`
    DivisionByZero(&'static str),
    /// `ValueError`: the operation is not defined for the argument
    Domain(&'static str),
    /// `MemoryError`: the result does not fit into memory
    Memory(&'static str),
}

pub type MathResult<T> = Result<T, MathError>;

pub(crate) const INT_OVERFLOW: MathError = MathError::Overflow("integer result does not fit into 64 bits");
