## Agent skills

### Issue tracker

Issues are tracked in GitHub Issues for troyan-dy/fast_math, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

The default five triage labels: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `GLOSSARY.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### README and guide

`README.md` is the landing page: the pitch, the installation, the Quick start, the table of functions and the
performance figures. The full documentation is the guide, one page per topic in `docs/guide/`, linked from the
README "Documentation" section, and `docs/benchmarks.md`. The documentation is in English only.

Every `>>>` example of the README, the guide, `docs/benchmarks.md` and the ADRs runs as a doctest, and every
relative link lands on a file and a heading that exist (`tests/test_docs.py`).

## Design principles

Python is the reference (`docs/adr/0003-python-is-the-reference.md`): a function gives what the Python operator
or `math` function of the same name gives, value, type, sign of zero and exception type. The tests compare the
two on hypothesis-generated arguments (`tests/reference.py`); a deliberate difference is written as a change of
the reference in the test and listed in `docs/guide/semantics.md`. Never fix a failing property by loosening
`same()` or narrowing the strategies.

Integers are `i64` with checked arithmetic (`docs/adr/0002-integers-are-64-bit.md`): a result or argument
beyond 64 bits raises `OverflowError`. No wrapping, saturating, silent `float` fallback or bigints.

The core (`src/arith.rs`, `src/theory.rs`, `src/number.rs`) stays free of PyO3, so `cargo test` runs it without
an interpreter; only `src/python.rs` knows Python, behind the `python` cargo feature.

A new function: the core with a Rust unit test of its edges, the export in `src/python.rs`, the re-export and
`__all__` in `python/fast_math/__init__.py`, the stub in `_core.pyi` (`stubtest` checks it), a property test
against its Python counterpart, a row in the README table and `docs/guide/semantics.md`, and an entry in
`CHANGELOG.md`.

Wheels are abi3 for CPython 3.11+ plus a free-threaded 3.14t wheel per platform, and the module declares
`gil_used = false` (`docs/adr/0004-abi3-and-free-threaded-wheels.md`): keep it free of global state.

## Releases

Every merge into `master` is a release: a pull request bumps `version` in `pyproject.toml` (`uv version --bump
...`) and adds its `CHANGELOG.md` section with a compare link (`scripts/version.py`, `make check-version`).
`Cargo.toml` keeps `0.0.0`. See `docs/guide/development.md`.

## Commands

`make install`, `make check` (everything CI runs), `make test`, `make rust-test`, `make test-free-threaded`,
`make bench`, `make wheels`.
