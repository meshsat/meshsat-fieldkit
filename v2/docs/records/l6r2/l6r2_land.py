#!/usr/bin/env python3
"""l6r2_land.py: the shared logic of record l6r2's two LAND drafts (round 3, MESHSAT-1357, 3 October 2026), Layer 8 drafts on
the footprint key of three Coilcraft inductor rows (criterion 6.4, a part on the land of its own body).

Board B draws its 4.7 uH XAL4030-472ME (L1) on the footprint key "L4020" (Inductor_SMD:L_Coilcraft_XAL4020-XXX) and its six
3.3 uH XAL6030-332ME (L101, L102, L201, L202, L301, L302, the AP64500 3.3 V stages of buck33) on "L6060"
(L_Coilcraft_XAL6060-XXX); board E draws its 4.7 uH XAL4030-472ME (L3, the +5V_E6 buck) on "L4020". The value is right in
each case and the footprint names the wrong body: Coilcraft's sheets list no 4.7 uH XAL4020 (that series ends at -222, 2.2 uH)
and no 3.3 uH XAL6060 (that series starts at -472, 4.7 uH), so each value names the only part of its inductance in its series,
and no Layer 4 record selected these inductors: they come with the generators' own buck recipes (L6R2-PASSIVES.md section 8.2).
The copper is the same: Coilcraft draws ONE recommended land per series (XAL40xx 0.98 x 3.4 mm pads at 2.37 mm; XAL60xx 1.43 x 5.50 mm pads at
4.04 mm), and KiCad 9.0.9's footprints of each pair carry identical pads, courtyard, fab and silk outlines
(inputs/kicad-xal-footprints-9.0.9.json). What differs is the body: the footprint's description and its 3D model, which the
z-stack reads (v2/cad/zstack.py): XAL4020 2.1 mm against the XAL4030's 3.1 mm (1.0 mm under), XAL6060 6.1 mm against the
XAL6030's 3.1 mm (3.0 mm over). The correction is therefore the footprint key, not the value: B's and E's FP maps gain the
"L4030" (and on B the "L6030") key with the KiCad footprint of the named part, and the three part calls take it. The keys
"L4020" and "L6060" stay in the maps (B's other XAL4020-222ME rows keep "L4020"). Designators, values, nets and codes are not
touched; the land's copper does not change, so a placement or a route of the regenerated board needs no move.

RELEASE GUARD: a draft refuses the repository's own generator until v2/docs/records/l6r2/RELEASE.md reads `released: yes` and
names an accepted check (l6r2_apply.released); it writes scratch copies freely. Each old text must occur exactly once and each
new text must not occur yet (a second application is refused); the result must differ and parse (ast)."""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_apply  # noqa: E402

FP4020 = '"L4020": "Inductor_SMD:L_Coilcraft_XAL4020-XXX",'
FP4030 = '"L4030": "Inductor_SMD:L_Coilcraft_XAL4030-XXX",'
FP6060 = '"L6060": "Inductor_SMD:L_Coilcraft_XAL6060-XXX",'
FP6030 = '"L6030": "Inductor_SMD:L_Coilcraft_XAL6030-XXX",'
# per board: (what the edit is, the old text, the new text); applied in this order
EDITS = {
    "b": [
        ("the FP map gains the XAL4030 and XAL6030 footprints", FP4020 + " " + FP6060, FP4020 + " " + FP4030 + " " + FP6060 + " " + FP6030),
        ("buck33's docstring names the part its inductor is", "31.6k/10k on the 0.8 V reference, 3.3 uH XAL6060, meant",
         "31.6k/10k on the 0.8 V reference, 3.3 uH XAL6030, meant"),
        ("buck33's inductor (L101, L102, L201, L202, L301, L302) on the XAL6030 footprint",
         'part(L, "Device", "L", "3.3uH XAL6030-332ME", "L6060",', 'part(L, "Device", "L", "3.3uH XAL6030-332ME", "L6030",'),
        ("L1 on the XAL4030 footprint", 'part("L1", "Device", "L", "4.7uH XAL4030-472ME", "L4020",',
         'part("L1", "Device", "L", "4.7uH XAL4030-472ME", "L4030",'),
    ],
    "e": [
        ("the FP map gains the XAL4030 footprint", FP4020, FP4020 + " " + FP4030),
        ("L3 on the XAL4030 footprint", 'part("L3", "Device", "L", "4.7uH XAL4030-472ME", "L4020",',
         'part("L3", "Device", "L", "4.7uH XAL4030-472ME", "L4030",'),
    ],
}
# the rows each board's draft moves, and the footprint they move from and to (the tests and the record read these)
ROWS = {
    "b": {"L1": ("L_Coilcraft_XAL4020-XXX", "L_Coilcraft_XAL4030-XXX", "XAL4030-472ME"),
          **{r: ("L_Coilcraft_XAL6060-XXX", "L_Coilcraft_XAL6030-XXX", "XAL6030-332ME") for r in ("L101", "L102", "L201", "L202", "L301", "L302")}},
    "e": {"L3": ("L_Coilcraft_XAL4020-XXX", "L_Coilcraft_XAL4030-XXX", "XAL4030-472ME")},
}


def apply_text(text, board):
    """(state, new text, why): OK, or REFUSED with the reason; pure, nothing written."""
    new = text
    for what, old, rep in EDITS[board]:
        if rep == old:
            return "REFUSED", None, "an edit's new text equals its old text (%s)" % what
        if new.count(rep) != 0:
            return "REFUSED", None, "already applied: the new text of '%s' is present" % what
        if new.count(old) != 1:
            return "REFUSED", None, "the old text of '%s' occurs %d times, not once" % (what, new.count(old))
        new = new.replace(old, rep, 1)
    if new == text:
        return "REFUSED", None, "the result does not differ"
    try:
        ast.parse(new)
    except SyntaxError as e:
        return "REFUSED", None, "the result does not parse: %s" % e
    return "OK", new, "%d edit(s): %s" % (len(EDITS[board]), "; ".join(e[0] for e in EDITS[board]))


def main(board, argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        print(__doc__.split("\n")[0]); return 3
    target = os.path.realpath(args[0])
    own = os.path.realpath(os.path.join(l6r2_apply._top(), "v2", "ecad", "tools", "gen_sch_%s.py" % board))
    if target == own and not l6r2_apply.released():
        print("apply_gen_sch_%s_xal_land: REFUSED: the repository's own generator, and v2/docs/records/l6r2/RELEASE.md does not read "
              "'released: yes' with an accepted check" % board)
        return 3
    st, new, why = apply_text(open(target, encoding="utf-8").read(), board)
    if st != "OK":
        print("apply_gen_sch_%s_xal_land: REFUSED: %s" % (board, why)); return 3
    if flags == ["--write"]:
        open(target, "w", encoding="utf-8").write(new)
        back = open(target, encoding="utf-8").read()
        if back != new:
            print("apply_gen_sch_%s_xal_land: REFUSED: the written file does not read back as the patched text" % board); return 3
        print("apply_gen_sch_%s_xal_land: WRITTEN, %s" % (board, why))
    else:
        print("apply_gen_sch_%s_xal_land: checked, not written: %s" % (board, why))
    return 0
