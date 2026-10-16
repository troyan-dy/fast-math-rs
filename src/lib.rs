//! The core of `fast_math`: the operations are plain Rust in `arith` and `theory`, free of Python, so
//! `cargo test` runs them without an interpreter. The bindings in `python` are built only with the `python`
//! feature, which maturin turns on.

pub mod arith;
pub mod number;
pub mod theory;

#[cfg(feature = "python")]
mod python;
