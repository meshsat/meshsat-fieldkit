#!/usr/bin/env python3
"""Draft by w3g (MESHSAT-1357, 27 September 2026): the handover pages' lines that still say the diagrams were drawn at
e3aedb25, before round 8, brought to the rebuild at 38dcd764. These files are owned by the handover editor, so the
change is a draft: run it from the root of the tree it is applied to, after the w3g diagram rebuild is integrated.

Each edit asserts the old text exactly and that it occurs once, and refuses the whole run otherwise (nothing written).
Usage: python3 drafts/w3g/apply_handover_labels.py [--dry-run]"""
import os, sys

EDITS = [
    ("v2/docs/handover/START-HERE.md",
     "- **Diagrams** (`v2/docs/diagrams/`) were drawn at `e3aedb25`, before round 8; their README says what that means.",
     "- **Diagrams** (`v2/docs/diagrams/`) are drawn at `38dcd764`, with round 8 on all six boards; their README says how\n"
     "  they were made and checked, and what the power tree's attribution check does not cover."),
    ("v2/docs/handover/LAYER-STATUS.md",
     "| 4. System architecture | IN_PROGRESS | diagrams of hc4 (drawn at `e3aedb25`, stale against round 8);",
     "| 4. System architecture | IN_PROGRESS | diagrams of hc4, rebuilt on round 8 by w3g (drawn at `38dcd764`);"),
    ("v2/docs/handover/LAYER-STATUS.md",
     "FEA-001 to FEA-006; BAT-F20; the diagrams rebuilt on round 8; Review C |",
     "FEA-001 to FEA-006; BAT-F20; Review C |"),
    ("v2/docs/handover/LAYER-STATUS.md",
     "(`v2/docs/diagrams/`, hc4; drawn at `e3aedb25`, before round 8, and not rebuilt: `build.py --check` reads 0 of 11 "
     "current, and `power_tree.py`'s attribution check is not complete, as its README says)",
     "(`v2/docs/diagrams/`, hc4; rebuilt by w3g at `38dcd764` on the round 8 netlists: `build.py --check` reads 11 of 11 "
     "current, and `power_tree.py`'s attribution check is not complete, measured on every build, as its README says)"),
    ("v2/docs/handover/LAYER-STATUS.md",
     "Remaining: FEA-001 to FEA-006 as in this section; the diagrams rebuilt on the round 8 netlists after `power_tree.py`'s "
     "TREE follows board D; Review C.",
     "Remaining: FEA-001 to FEA-006 as in this section; Review C."),
    ("v2/docs/handover/pack.yaml",
     "their Mermaid sources, the tools that draw and check them and MANIFEST.json; drawn at e3aedb25, before round 8 (the "
     "folder's README states the status)",
     "their Mermaid sources, the tools that draw and check them and MANIFEST.json; drawn at 38dcd764, with round 8 (the "
     "folder's README states the status)"),
    ("v2/docs/handover/CONTINUATION-BRIEF.md",
     "readable diagrams (`v2/docs/diagrams/`, drawn before round 8)",
     "readable diagrams (`v2/docs/diagrams/`, drawn at `38dcd764` with round 8)"),
]


def main():
    dry = "--dry-run" in sys.argv
    texts = {}
    for path, old, new in EDITS:
        if path not in texts:
            texts[path] = open(path, encoding="utf-8").read()
        n = texts[path].count(old)
        if n != 1:
            sys.exit("REFUSED: %s: the old text occurs %d times, expected once: %r" % (path, n, old[:90]))
        assert new != old and "—" not in new
        texts[path] = texts[path].replace(old, new)
    for path, text in texts.items():
        if path.endswith(".yaml"):
            import yaml
            yaml.safe_load(text)          # the edited spec must still parse
        if not dry:
            open(path, "w", encoding="utf-8").write(text)
        print("%s %s" % ("would write" if dry else "wrote", path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
