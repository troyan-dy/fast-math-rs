#!/usr/bin/env bash
# Install the wheels of a directory into a fresh environment of CPython 3.11 and of 3.14t each, and run a few
# calls; on 3.14t the GIL must stay off after the import. Used by .github/workflows/wheels.yml.
#
#     scripts/smoke.sh dist
set -euo pipefail

wheels="${1:?usage: scripts/smoke.sh WHEEL_DIR}"

for python in 3.11 3.14t; do
  echo "==> CPython ${python}"
  uv run --no-project --isolated --no-index --find-links "${wheels}" --with fast-math-rs --python "${python}" \
    python - <<'EOF'
import sys
import sysconfig

import fast_math as fm

assert fm.add(2, 3) == 5
assert fm.floordiv(-7, 2) == -4
assert fm.is_prime(2**61 - 1)
assert len(fm.primes_up_to(1_000_000)) == 78_498
if sysconfig.get_config_var("Py_GIL_DISABLED"):
    assert not sys._is_gil_enabled(), "the extension turned the GIL on"
print(f"fast-math-rs {fm.__version__} on {sys.version.split()[0]}: {fm.__file__}")
EOF
done
