#!/usr/bin/env python3
"""apply_panel1450_coolers_r2.py: DRAFT for v2/cad's owner and the case geometry's writer (Layer 7 record l7r2, MESHSAT-1357, 3 October
2026; record l7pwr's F-L7-03). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the test writes one).

What it changes in v2/ecad/tools/panel1450.py's B16_MODULES, and nothing else:
  the three CM5 heatsink envelopes: 21.0 (the render scene's figure, 'TBD a Raspberry Pi drawing') becomes 18.56, the module stack's
      5.86 (panel1450's own 4.62 + 1.24) plus the Raspberry Pi Cooler's 12.7 (product brief RP-008184-DS-1, December 2024, filed by record
      l7pwr): the drawing the comment asked for;
  the three CM5 fan envelopes: the 30 x 30 x 30 class at Y 48 to 78 becomes the selected Sanyo Denki 9WPA0412P6G001 (40 x 40 x 20, record
      l7pwr) on its bracket over the cooler: X the cooler's centre +-20, Y 46.745 to 86.745 (1.0 north of the Xenarc body's edge at Y
      45.745, 1.255 south of the backer's top strip at Y 88.0), 39.56 above board B (5.86 + 12.7 + the bracket's 1.0 frame + 20.0).
Why (record l7r2 section 4): the fan stands on the cooler, not beside it, and its top at Z 90.16 keeps 3.46 under the PA's underside (slots
1 and 2) and 13.36 under the plate (slot 3); the Y band is the one place between the Xenarc and the backer's strip where nothing hangs
lower. Every gate that reads B16_TALL (check_pcb_c.py, z_budget.py, frame_seat.py through zstack.json) must be re-run on the box after it.

RELEASE GUARD: it refuses to write the repository's own panel1450.py unless the environment names this draft's release
(MESHSAT_L7R2_RELEASE=apply_panel1450_coolers_r2), which the integrator sets when the box run that re-reads zstack.json is staged.
Usage:  apply_panel1450_coolers_r2.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused."""
import ast
import os
import sys

NAME = "apply_panel1450_coolers_r2"
HS_OLD = ('    ((-93.0, 32.0, -52.0, 88.0), 21.0, "CM5 slot 1 heatsink", "CM5 on U30A/U30B with its cooler: 21.0 from the render scene, TBD a '
          'Raspberry Pi drawing (CASE-MARGINS.md section 6)"),')
HS_NEW = ('    ((-93.0, 32.0, -52.0, 88.0), 18.56, "CM5 slot 1 heatsink", "CM5 on U30A/U30B with its cooler: the module stack 5.86 and the '
          'Raspberry Pi Cooler 12.7 (product brief RP-008184-DS-1; records l7pwr, l7r2)"),')
EDITS = [
    (HS_OLD, HS_NEW),
    ('    ((-23.0, 32.0, 18.0, 88.0), 21.0, "CM5 slot 2 heatsink", "CM5 on U31A/U31B with its cooler: as slot 1"),',
     '    ((-23.0, 32.0, 18.0, 88.0), 18.56, "CM5 slot 2 heatsink", "CM5 on U31A/U31B with its cooler: as slot 1"),'),
    ('    ((47.0, 32.0, 88.0, 88.0), 21.0, "CM5 slot 3 heatsink", "CM5 on U32A/U32B with its cooler: as slot 1"),',
     '    ((47.0, 32.0, 88.0, 88.0), 18.56, "CM5 slot 3 heatsink", "CM5 on U32A/U32B with its cooler: as slot 1"),'),
    ('    ((-87.5, 48.0, -57.5, 78.0), 30.0, "CM5 slot 1 fan", "30 mm class fan on the cooler (appendix 32.85; the fan part is open, W4-F9)"),',
     '    ((-92.5, 46.745, -52.5, 86.745), 39.56, "CM5 slot 1 fan", "Sanyo Denki 9WPA0412P6G001 40 x 40 x 20 on its bracket over the cooler '
     '(record l7r2): 5.86 + 12.7 + 1.0 + 20.0"),'),
    ('    ((-17.5, 48.0, 12.5, 78.0), 30.0, "CM5 slot 2 fan", "as slot 1"),',
     '    ((-22.5, 46.745, 17.5, 86.745), 39.56, "CM5 slot 2 fan", "as slot 1"),'),
    ('    ((52.5, 48.0, 82.5, 78.0), 30.0, "CM5 slot 3 fan", "as slot 1"),',
     '    ((47.5, 46.745, 87.5, 86.745), 39.56, "CM5 slot 3 fan", "as slot 1"),'),
]


def main(argv):
    if not argv:
        print(__doc__); return 2
    target = argv[0]; write = "--write" in argv[1:]
    here = os.path.dirname(os.path.abspath(__file__))
    own = os.path.abspath(os.path.join(here, "..", "..", "..", "..", "v2", "ecad", "tools", "panel1450.py"))
    if write and os.path.abspath(target) == own and os.environ.get("MESHSAT_L7R2_RELEASE") != NAME:
        print("%s: REFUSED, the repository's own panel1450.py is named before the draft is released" % NAME); return 3
    src = open(target, encoding="utf-8").read()
    for old, new in EDITS:
        if src.count(old) != 1:
            print("%s: REFUSED, an anchor occurs %d times (already applied, or the target moved): %s" % (NAME, src.count(old), old[:70])); return 3
        if new in src:
            print("%s: REFUSED, the new text is already present: %s" % (NAME, new[:70])); return 3
        src = src.replace(old, new)
    ast.parse(src)
    if write:
        open(target, "w", encoding="utf-8").write(src)
        print("%s: written (%d edits)" % (NAME, len(EDITS)))
    else:
        print("%s: checked (%d edits apply and the result parses)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
