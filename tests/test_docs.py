"""
The examples of the README and the guide run as written, and every relative link lands on a file and a heading
that exist.
"""

import doctest
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DOCUMENTS = sorted(
    [
        ROOT / "README.md",
        ROOT / "docs" / "benchmarks.md",
        *(ROOT / "docs" / "guide").glob("*.md"),
        *(ROOT / "docs" / "adr").glob("*.md"),
    ]
)


def ids(path: Path) -> str:
    return str(path.relative_to(ROOT))


@pytest.mark.parametrize("path", DOCUMENTS, ids=ids)
def test_examples(path: Path) -> None:
    result = doctest.testfile(str(path), module_relative=False, optionflags=doctest.ELLIPSIS, verbose=False)
    assert result.failed == 0


def anchor(heading: str) -> str:
    # GitHub's slug: lower case, punctuation dropped, spaces as dashes
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def prose(text: str) -> str:
    return re.sub(r"^```.*?^```", "", text, flags=re.MULTILINE | re.DOTALL)


@pytest.mark.parametrize("path", DOCUMENTS, ids=ids)
def test_links(path: Path) -> None:
    text = prose(path.read_text(encoding="utf-8"))
    for link in re.findall(r"\]\((?![a-z]+:)([^)\s]+)\)", text):
        target, _, fragment = link.partition("#")
        file = (path.parent / target).resolve() if target else path
        assert file.exists(), f"{link} in {ids(path)}: no such file"
        if fragment and file.suffix == ".md":
            headings = re.findall(r"^#+ (.+)$", prose(file.read_text(encoding="utf-8")), flags=re.MULTILINE)
            assert fragment in {anchor(heading) for heading in headings}, f"{link} in {ids(path)}: no such heading"
