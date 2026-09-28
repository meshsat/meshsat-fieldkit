#!/usr/bin/env python3
"""UNEXECUTED DRAFT for the generator owners. See ANALYSIS.md.

No numeric replacement is justified by the held sources for the named mode.
CHANGES is deliberately empty. This version refuses execution, including a
second attempt, without writing anything. It is not a reconciliation by fiat.

If the owners later author supported changes, each entry must contain the
repository-relative file, exact old text and exact new text. The safeguards
below validate all replacements and ASTs before any generator is written.
"""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
CHANGES = []  # Required format: {"file": "...", "old": "exact text", "new": "exact text"}.
ALLOWED = {"v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_b.py"}
MARKER = Path(__file__).with_name("apply_declarations_draft.applied")


def main():
    if MARKER.exists():
        raise SystemExit("Refused: this draft has already been applied or attempted.")
    if not CHANGES:
        raise SystemExit("Refused: no sourced replacement currents; empty draft writes nothing.")
    originals = {}
    results = {}
    for change in CHANGES:
        name, old, new = change["file"], change["old"], change["new"]
        assert name in ALLOWED, name
        assert old and new != old, "Replacement must change nonempty old text"
        if name not in originals:
            originals[name] = (ROOT / name).read_text()
            results[name] = originals[name]
        assert originals[name].count(old) == 1, (name, "old text must occur exactly once in original")
        assert results[name].count(old) == 1, (name, "old text must occur exactly once at replacement")
        results[name] = results[name].replace(old, new, 1)
    for name, result in results.items():
        assert result != originals[name], (name, "no effective change")
        ast.parse(result, filename=name)
        assert (ROOT / name).read_text() == originals[name], (name, "file changed during validation")
    # Exclusive creation refuses every second run, including recovery from a partial write.
    # An owner would investigate a partial write; this draft never silently retries it.
    with MARKER.open("x") as marker:
        marker.write("Draft attempted. Do not run again.\n")
    for name, result in results.items():
        (ROOT / name).write_text(result)


if __name__ == "__main__":
    main()
