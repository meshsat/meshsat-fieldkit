#!/usr/bin/env python3
"""apply_l4small_layer6.py: register task L4A-60 (RE-8), Layer 6's rows for record l9t5's SESSION decision L9T5-D11 (revision X NOT
ADMITTED; MESHSAT-1357, worker W133, branch fnd/l4small, 7 October 2026). UNAPPLIED on its branch: the set 33 integrator runs it.

WHAT IT DOES: L9T5-F23 (T10-ROUND5.md section 10) and section 3 (6)'s Layer 6 row asked the part identity and the procurement line to
name revision V only. This restates them:
  v2/docs/parts/STM32H743-COMPATIBILITY.md  F1, the five matrix rows that name "revision V or X", and the session choice HC6-SC-1:
                                            each by insertion (the erratum's bound V or X stays written, the selection inside it,
                                            revision V only, is added with L9T5-D11);
  v2/docs/parts/PROCUREMENT.md              the STM32H743VIT6 line (U41, U51, U61): "revision V ONLY", HC6-SC-1's V or X named as
                                            narrowed, and the lot's revision named as not read (no query sent);
  v2/ecad/tools/pcb_requirements.yaml       CON-017's evidence pin of the page rebound to the patched page's sha256/16, with one
  v2/docs/REQUIREMENTS-TRACE.md             sentence in its evidence item (3) saying why; the trace page, which rules_render.py
                                            generates from the registry, gets the same two changes (its --check is the integrator's).
CON-017's statement and acceptance are NOT changed: clause (5), revision V or X, is the erratum's bound, which revision V meets.
No part, net, value, land or order code changes; nothing is bought or asked of a supplier. Nothing in this kit has been built,
bought, powered or measured. Engine and its checks E1 to E6: v2/docs/records/l4small/l4small_edit.py.
Usage:  apply_l4small_layer6.py [ROOT] [--check | --write]   (default ROOT: this tree; default --check: nothing is written)
Exit 0: checked or written; 2: usage; 3: refused (already applied, an anchor missing or not unique, a pin not the page's digest, or
the result does not parse)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l4small"))
import l4small_edit as E  # noqa: E402

NAME = "apply_l4small_layer6"
CMP = "v2/docs/parts/STM32H743-COMPATIBILITY.md"
PRC = "v2/docs/parts/PROCUREMENT.md"
REQ = "v2/ecad/tools/pcb_requirements.yaml"
TRC = "v2/docs/REQUIREMENTS-TRACE.md"
D = "SESSION L9T5-D11"
FIT = " [revision V only is fitted: %s, record l9t5]" % D

EDITS = [
    (CMP, "REV_ID 0x2003 or 0x2001 in DBGMCU_IDC (ES0392 Table 2, p.1;\n  RM0433 p.3208). Checked at goods-in",
          "REV_ID 0x2003 or 0x2001 in DBGMCU_IDC (ES0392 Table 2, p.1;\n  RM0433 p.3208) [the erratum's bound; the selection inside it "
          "is revision V ONLY, marking V and REV_ID 0x2003, %s of 7 October 2026 (record l9t5, `T10-ROUND5.md` section W133): revision "
          "X is NOT ADMITTED and a lot marked X is refused]. Checked at goods-in" % D, True),
    (CMP, "Session choice HC6-SC-1.\n", "Session choice HC6-SC-1, narrowed to revision V by %s.\n" % D, True),
    (CMP, "MATCH, and silicon revision V or X avoids erratum 2.2.14 (F1) |",
          "MATCH, and silicon revision V or X avoids erratum 2.2.14 (F1)%s |" % FIT, True),
    (CMP, "without bit-rate switching; revision V or X only (ES0392 2.24.2, F1) |",
          "without bit-rate switching; revision V or X only (ES0392 2.24.2, F1)%s |" % FIT, True),
    (CMP, "MATCH on revision V or X (ES0392 2.2.8 PCROP may be unprotected on revision Y) |",
          "MATCH on revision V or X (ES0392 2.2.8 PCROP may be unprotected on revision Y)%s |" % FIT, True),
    (CMP, "| revision V or X only: goods-in marking check (ASSEMBLY)",
          "| revision V or X only [revision V ONLY since 7 October 2026, %s: a lot marked X is refused]: goods-in marking check "
          "(ASSEMBLY)" % D, True),
    (CMP, "| D-13's verified boot | revision V or X (F1) |", "| D-13's verified boot | revision V or X (F1)%s |" % FIT, True),
    (CMP, "| the dark-controller case (IOHA A4, A6) | revision V or X (F1) |",
          "| the dark-controller case (IOHA A4, A6) | revision V or X (F1)%s |" % FIT, True),
    (CMP, "| HC6-SC-1 | The supervisors are bought and accepted only as silicon revision V or X; the firmware",
          "| HC6-SC-1 | The supervisors are bought and accepted only as silicon revision V or X [narrowed to revision V ONLY by %s, "
          "7 October 2026, record l9t5 `T10-ROUND5.md` section W133: revision X is NOT ADMITTED and a lot marked X is refused at "
          "goods-in; that narrowing is reversed only by reversing L9T5-D11]; the firmware" % D, True),
    (PRC, "| revision V or X only (HC6-SC-1); franchised stock thin |",
          "| revision V ONLY (%s, 7 October 2026: HC6-SC-1's revision V or X narrowed, revision X NOT ADMITTED; no stock figure here "
          "reads a lot's revision, so an order names revision V; no query sent); franchised stock thin |" % D, False),
    (REQ, "firmware stage's (final_phase), so they do not decide this SCHEMATIC reading\n",
          "firmware stage's (final_phase), so they do not decide this SCHEMATIC reading. Rebound on 7 October 2026 (W133,"
          " records/l9t5/apply_l4small_layer6.py): the page's F1, its matrix rows naming revision V or X and HC6-SC-1 now add that the"
          " fitted revision is V only (%s, record l9t5); clause (5)'s bound and every reading of (1) to (3) unchanged\n" % D, True),
    (TRC, "firmware stage's (final_phase), so they do not decide this SCHEMATIC reading",
          "firmware stage's (final_phase), so they do not decide this SCHEMATIC reading. Rebound on 7 October 2026 (W133,"
          " records/l9t5/apply_l4small_layer6.py): the page's F1, its matrix rows naming revision V or X and HC6-SC-1 now add that the"
          " fitted revision is V only (%s, record l9t5); clause (5)'s bound and every reading of (1) to (3) unchanged" % D, True),
]


def rebind(before, after):
    """CON-017's pin of the compatibility page: it must be the unpatched page's digest; it becomes the patched page's."""
    old = "%s@%s" % (CMP, E.sha16(before[CMP]))
    new = "%s@%s" % (CMP, E.sha16(after[CMP]))
    for rel in (REQ, TRC):
        if after[rel].count(old) != 1:
            raise E.Refused("%s does not pin the unpatched %s once (%s)" % (rel, CMP, old))
    return [(REQ, old, new, False), (TRC, old, new, False)]


if __name__ == "__main__":
    sys.exit(E.main(NAME, HERE, EDITS, (), rebind))
