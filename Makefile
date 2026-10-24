.DEFAULT_GOAL := help

PY_VERSIONS := 3.11 3.12 3.13 3.14
# Not a dev dependency: uvx keeps it out of uv.lock; the same pin is in .github/workflows/ci.yml
PYRIGHT := pyright@1.1.414

.PHONY: help
help: ## Show available targets
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: install
install: ## Install the dev dependencies and build the extension into .venv
	uv sync --locked

.PHONY: lint
lint: ## Run ruff, wemake-python-styleguide, mypy, pyright and stubtest on Python; rustfmt and clippy on Rust
	uv run ruff check .
	uv run ruff format --check .
	uv run flake8 . --select=WPS
	uv run mypy
	uvx $(PYRIGHT)
	uv run stubtest fast_math
	cargo fmt --check
	cargo clippy --all-targets --all-features -- -D warnings

.PHONY: format
format: ## Autofix lint issues and format the Python and Rust code
	uv run ruff check --fix .
	uv run ruff format .
	cargo fmt

.PHONY: test
test: ## Run the Python tests
	uv run pytest

.PHONY: rust-test
rust-test: ## Run the Rust unit tests of the core
	cargo test

.PHONY: cov
cov: ## Run the Python tests with a coverage report
	uv run pytest --cov --cov-report=term --cov-report=html

.PHONY: test-all
test-all: ## Run the Python tests on every supported Python version
	@for v in $(PY_VERSIONS); do \
		echo "==> Python $$v"; \
		uv run --isolated --python $$v pytest || exit 1; \
	done

.PHONY: test-free-threaded
test-free-threaded: ## Run the Python tests on free-threaded Python 3.14t, as CI does; the GIL must stay off by itself
	uv run --python 3.14t --isolated --no-default-groups --with pytest --with hypothesis pytest -p no:cacheprovider

.PHONY: bench
bench: ## Run the benchmarks, see docs/benchmarks.md
	uv run python benchmarks/run.py

.PHONY: check-version
check-version: ## Check that the version is bumped against origin/master, as CI does for a pull request
	git fetch --quiet --tags origin master
	uv run --no-project python scripts/version.py check origin/master

.PHONY: check
check: lint rust-test test ## Run everything CI runs

.PHONY: wheels
wheels: ## Build the release wheels of this platform (abi3 and 3.14t) and the sdist into dist/
	uvx maturin build --release --out dist --interpreter 3.11 3.14t
	uvx maturin sdist --out dist

.PHONY: clean
clean: ## Remove build artifacts and caches; the extension built into python/fast_math/ stays, `uv run` needs it
	rm -rf build dist target *.egg-info htmlcov .coverage coverage.xml .pytest_cache .mypy_cache .ruff_cache .hypothesis
	find . -type d -name __pycache__ -not -path './.venv/*' -exec rm -rf {} +
