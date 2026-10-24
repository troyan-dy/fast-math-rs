#!/bin/bash
# Installs what `make check` needs in a Claude Code cloud session: the dev dependencies and the extension in
# .venv, the rustfmt and clippy components, and pyright, which the Makefile runs from uvx
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"

if command -v rustup >/dev/null 2>&1; then
  rustup component add rustfmt clippy
fi

# Builds fast_math._core too; a no-op when the lock and the Rust sources are unchanged
uv sync --locked

# The pin of the Makefile; the first run fetches pyright and its Node runtime
uvx "$(sed -n 's/^PYRIGHT := //p' Makefile)" --version

# clippy --all-features builds the bindings, which are configured against the interpreter of the venv, as in CI
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYO3_PYTHON=\"$PWD/.venv/bin/python\"" >> "$CLAUDE_ENV_FILE"
fi
