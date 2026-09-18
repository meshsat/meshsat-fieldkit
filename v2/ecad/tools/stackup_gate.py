#!/usr/bin/env python3
"""The board's stackup against the named, dated fabricator record (rule STK-001, MESHSAT-862, 18 September 2026).

STK-001 is a BLOCKER and it had no instrument of its own. The coverage map pointed it at two verdicts about
other questions, and where a rule names several the worst decides, so:

  * boards C, D and E read **STK-001 PASS "impedance_check PASS of 0"**. Their stackup was credited by a pair
    measurement that judged ZERO pairs. Absence is never a pass, and this was absence wearing a PASS.
  * board B read STK-001 FAIL because seventeen differential pairs missed their impedance target, which is
    PAIR-001's criteria, not this rule's.
  * board P read STK-001 FAIL because five of its design classes are under the fabricator's capability, which
    is RTE-001's criteria, not this rule's either.

So no board's stackup had ever been compared with anything. This gate asks what the rule actually asks: the
copper layer count, the per-layer copper weight, the dielectric thicknesses and the dielectric constants are
present in the board file and match a named, dated fabricator stackup, and the order paperwork names the same
one. The record it compares against is `stackup_write.STACKS`, which is the transcription of the fabricator's
own pages into this tree, and the two documents behind those pages are named in every verdict this writes.

It found board P on its first run: P's board file carries epsilon_r 4.6 on its core where the record says 4.5,
because the file was written before the 16 September correction that read the number off the fabricator's
capability document instead of its impedance page. Nothing computed moves on P today, which is exactly why
this needed a gate rather than a memory: the board and the record disagreed for two days in silence.

A board with no stackup block, or with no declared stack name, or whose declared name this project holds no
record of, is INCONCLUSIVE and says which of the three it is.

Usage: stackup_gate.py <board.kicad_pcb> --board <letter> [--json]
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import stackup_read as SR
from stackup_write import STACKS

# Which document each named stack was transcribed from, with the date it was read. The multilayer stacks come
# from the fabricator's impedance page, the two-layer dielectric constant from its capability page: two pages,
# two numbers, and the 16 September correction happened because one had been read for the other.
DOCS = {
    "JLC04161H-7628": "v2/vendor/fabricator/jlcpcb-impedance-stackups-2026-09-16.md",
    "JLC06161H-3313": "v2/vendor/fabricator/jlcpcb-impedance-stackups-2026-09-16.md",
    "2L": "v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md",
    "2L-2oz": "v2/vendor/fabricator/jlcpcb-pcb-capabilities-2026-09-16.md",
}
ORDER_PREFIX = {"a": "PCB-A-", "b": "PCB-B-", "c": "PCB-C-", "d": "PCB-D-", "e": "PCB-E1-", "e5": "PCB-E5-", "p": "PCB-P-"}
TOL_MM = 0.0005          # the file writes three or four decimals; this is a transcription check, not a measurement
TOL_DK = 0.001


def expected(name):
    """The named stack as (copper thicknesses, dielectrics) in file order, from the transcribed record."""
    rows = STACKS.get(name)
    if rows is None: return None
    cu = [(r[0], r[1]) for r in rows if str(r[0]).endswith(".Cu")]
    di = [(r[1], r[2], r[3]) for r in rows if r[0] in ("pp", "core")]
    return cu, di


def order_notes(letter, root):
    """Every order note that belongs to this board, as (folder, text)."""
    pre = ORDER_PREFIX.get(letter)
    if not pre: return []
    base = os.path.join(root, "v2", "release", "revA", "order")
    out = []
    if not os.path.isdir(base): return out
    for d in sorted(os.listdir(base)):
        if not d.startswith(pre): continue
        f = os.path.join(base, d, "ORDER-NOTES.txt")
        if os.path.isfile(f): out.append((d, open(f, encoding="utf-8", errors="replace").read()))
    return out


def judge(path, letter, root=None, declared=None):
    """`declared` is for a FIXTURE, which has no entry in the board facts; a board's own run always reads the
    fact, because the point of this rule is that the stack a board is judged against is the one it declares."""
    root = root or os.path.dirname(os.path.dirname(os.path.dirname(HERE)))   # v2/ecad/tools -> the repo root
    if declared is None:
        import rules_lib as R
        declared = ((R.facts() or {}).get(letter) or {}).get("stackup")
    board_cu = SR.copper_layers(path)
    board_di = SR.dielectrics(path)
    r = dict(declared=declared, board_copper=len(board_cu), compared=0, bad=[], notes=[], order=[])
    if not board_cu:
        r["notes"].append("the board file carries no stackup block at all, so nothing in it can be compared")
        return r
    if not declared:
        r["notes"].append("this board declares no stackup in pcb_board_facts.yaml, so there is no named stack to compare it with")
        return r
    exp = expected(declared)
    if exp is None:
        r["notes"].append("this project holds no transcribed record of the stack this board declares (%s): the record is stackup_write.STACKS" % declared)
        return r
    doc = DOCS.get(declared)
    if not doc or not os.path.isfile(os.path.join(root, doc)):
        r["notes"].append("the document the named stack was transcribed from is not in the tree (%s)" % doc)
        return r
    exp_cu, exp_di = exp
    n = 0

    def cmp_num(what, have, want, tol):
        nonlocal n
        n += 1
        if have is None: r["bad"].append("%s is absent from the board file (the record says %.4f)" % (what, want))
        elif abs(float(have) - float(want)) > tol:
            r["bad"].append("%s is %.4f in the board and %.4f in %s" % (what, float(have), float(want), declared))

    n += 1
    if len(board_cu) != len(exp_cu):
        r["bad"].append("the board carries %d copper layer(s) and %s is a %d-layer stack" % (len(board_cu), declared, len(exp_cu)))
    else:
        for (bn, want), got in zip(exp_cu, board_cu):
            if got.get("name") != bn:
                r["bad"].append("copper layer %d is %s in the board and %s in %s" % (n, got.get("name"), bn, declared))
            cmp_num("%s copper thickness" % bn, got.get("thickness"), want, TOL_MM)
    n += 1
    if len(board_di) != len(exp_di):
        r["bad"].append("the board carries %d dielectric layer(s) and %s has %d" % (len(board_di), declared, len(exp_di)))
    else:
        for i, ((mat, th, dk), got) in enumerate(zip(exp_di, board_di), 1):
            cmp_num("dielectric %d (%s) thickness" % (i, mat), got.get("thickness"), th, TOL_MM)
            cmp_num("dielectric %d (%s) dielectric constant" % (i, mat), got.get("epsilon_r"), dk, TOL_DK)
            n += 1
            if got.get("material") != mat:
                r["bad"].append("dielectric %d is \"%s\" in the board and \"%s\" in %s" % (i, got.get("material"), mat, declared))

    # THE THIRD CLAUSE: the order paperwork names the same stack. A board with no folder yet is not a failure
    # of this rule (that is DOC-001 and the promotion freeze); a folder naming a DIFFERENT stack is, because
    # the fabricator builds what the paperwork says and not what the board file carries.
    two_layer = len(exp_cu) == 2
    for folder, text in order_notes(letter, root):
        n += 1
        if two_layer:
            oz = "2 oz" if exp_cu[0][1] > 0.05 else "1 oz"
            ok = oz in text
            r["order"].append("%s: copper weight %s %s" % (folder, oz, "named" if ok else "NOT named"))
            if not ok: r["bad"].append("the order note in %s does not name this board's %s copper weight" % (folder, oz))
        else:
            ok = declared in text
            r["order"].append("%s: %s %s" % (folder, declared, "named" if ok else "NOT named"))
            if not ok: r["bad"].append("the order note in %s does not name the stack this board declares (%s)" % (folder, declared))
    if not r["order"]: r["notes"].append("no order note for this board yet, so the paperwork clause has nothing to read")
    r["compared"] = n
    r["document"] = doc
    return r


def main(argv):
    if not argv: print(__doc__); return 2
    path = argv[0]
    letter = _v.opt(argv, "--board", None)
    if not letter:
        print("stackup_gate: --board <letter> is required: the named stack is a board fact"); return 2
    r = judge(path, letter)
    print("stackup_gate: board %s declares %s, board file carries %d copper layer(s), %d propert(ies) compared against %s"
          % (letter, r.get("declared") or "NOTHING", r["board_copper"], r["compared"], r.get("document") or "no record"))
    for o in r["order"]: print("  order note %s" % o)
    for nte in r["notes"]: print("  NOTE %s" % nte)
    for b in r["bad"][:20]: print("  FAIL %s" % b)
    if "--json" in argv: print(json.dumps(r, indent=1))
    if not r["compared"]:
        return _v.write("stackup_gate", _v.INCONCLUSIVE, denominator=0,
                        inputs={"board": path, "declared": r.get("declared")},
                        evidence=r["notes"], missing_input="stackup" if not r["board_copper"] else None,
                        note="; ".join(r["notes"])[:200] or "nothing to compare")
    return _v.write("stackup_gate", _v.FAIL if r["bad"] else _v.PASS,
                    counts={"compared": r["compared"], "disagreements": len(r["bad"]), "copper_layers": r["board_copper"]},
                    denominator=r["compared"], evidence=r["bad"][:20] or r["order"],
                    inputs={"board": path, "declared": r["declared"], "document": r["document"]},
                    note=("the board's stackup is the one it declares, property by property, and the order paperwork "
                          "names it" if not r["bad"] else
                          "the board's stackup and the named fabricator record disagree"))


if __name__ == "__main__":
    import verdict as _vg   # a gate that crashes writes INCONCLUSIVE, never nothing (18 September 2026)
    sys.exit(_vg.guard("stackup_gate", main, sys.argv[1:]))
