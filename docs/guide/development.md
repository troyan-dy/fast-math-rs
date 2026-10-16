# Development

← [Documentation](../../README.md#documentation)

You need [uv](https://docs.astral.sh/uv/) and a stable Rust toolchain with `rustfmt` and `clippy`
([rustup](https://rustup.rs)). `uv sync` builds the extension through maturin and installs it into `.venv`;
`uv run` rebuilds it whenever a file under `src/`, `Cargo.toml` or `pyproject.toml` changes, so there is no
separate build step.

```bash
make install   # uv sync --locked: the venv and the extension
make check     # everything CI runs: the linters, the type checkers and both test suites
make test      # the Python tests
make rust-test # the Rust unit tests of the core, without Python
make cov       # the Python tests with coverage (terminal + htmlcov/)
make test-all  # the Python tests on CPython 3.11-3.14
make test-free-threaded  # the Python tests on free-threaded CPython 3.14t
make bench     # the benchmarks, see docs/benchmarks.md
```

## Layout

| path | what |
| --- | --- |
| `src/arith.rs`, `src/theory.rs`, `src/number.rs` | the core: plain Rust, no Python, unit-tested by `cargo test` |
| `src/python.rs` | the bindings: argument conversion, errors into exceptions, the `fast_math._core` module; built with the `python` cargo feature, which maturin turns on |
| `python/fast_math/` | the Python package: `__init__.py` re-exports the extension, `_core.pyi` types it |
| `tests/` | the Python tests: every operation against Python itself, with hypothesis |
| `benchmarks/run.py` | fast_math against the builtins and plain Python |
| `scripts/version.py` | the release checks of CI |

A new function is written in the core first, with a Rust unit test of its edge cases, then exported from
`src/python.rs`, re-exported in `python/fast_math/__init__.py`, typed in `_core.pyi` and tested against its
Python counterpart. `stubtest` fails when the stub and the module disagree, and
`tests/test_arguments.py` when `__all__` misses a function.

## Checks

- Python: `ruff check`, `ruff format --check`, `mypy` (strict), `pyright`, `stubtest fast_math`.
- Rust: `cargo fmt --check`, `cargo clippy --all-targets --all-features -- -D warnings` with the pedantic
  lints, `cargo test`.
- Coverage of the Python package is 100%, and CI fails below that (`fail_under = 100` in `pyproject.toml`). The
  Rust core is covered by its own unit tests and, through the bindings, by the property tests.

`HYPOTHESIS_PROFILE=thorough make test` runs every property on 5000 examples instead of 300.

## Releases

Every merge into `master` is a release. The `Release` workflow builds the wheels of every platform and the
sdist, publishes them to PyPI, tags the version `vX.Y.Z` and creates a GitHub release from its section of
`CHANGELOG.md`. A pull request therefore carries its own version: raise it with `uv version --bump
patch|minor|major` and turn `## [Unreleased]` into `## [X.Y.Z] - YYYY-MM-DD` with a compare link at the bottom.
CI checks this on every pull request, and `make check-version` checks it locally. The version lives in
`pyproject.toml` only: `Cargo.toml` keeps `0.0.0`, since the crate is never published.

Every pull request also builds the wheels of every target, so a platform that stops building fails before the
merge, not in the release.

PyPI publishing uses [Trusted Publishing](https://docs.pypi.org/trusted-publishers/): the `pypi` environment
of the repository and a trusted publisher on PyPI for `troyan-dy/fast_math`, workflow `release.yml`,
environment `pypi`. No token is stored.
