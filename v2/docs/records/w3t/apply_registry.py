#!/usr/bin/env python3
"""Stream w3t's registry change (EQ-18, MESHSAT-1357, 27 September 2026), applied BY RECORD ID with asserted old text.

Two files, both owned by the registry writer, not by stream w3t:
  v2/ecad/tools/pcb_rules_coverage.yaml  rule RF-002's row. Its note says "tx_inhibit.py's header holds the same list"; the
      header gained limits (13) and (14) and the SN74LVC1G57 row, so the note, the family list of _verdict_why, the pinned
      file of _gap_if_applied_alone, the remediation and a reading sentence are brought to it.
  v2/ecad/tools/pcb_requirements.yaml    one new SESSION open item for finding W3T-F1 (TX_INHIBIT_n's fail-safe state with
      board C's U14 on it), taking the next free S-nn in the tree it is applied to.

Run it from the repository root, AFTER tx_inhibit.py is in its final form in that tree: the coverage row pins that file's
sha256, read here, and the script refuses a tx_inhibit.py that does not carry limits (13) and (14). Idempotent: a block
already applied (found by its own marker text) is left alone. --dry-run prints the diff and writes nothing.
Then, in v2/ecad/tools: `python3 rules_lib.py requirements` (and the integration recipe's order: commit the config
inputs before rules_status/rules_render)."""
import difflib
import hashlib
import os
import re
import subprocess
import sys

import yaml

DRY = "--dry-run" in sys.argv
ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip() or os.getcwd()
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
COV = os.path.join(TOOLS, "pcb_rules_coverage.yaml")
REQ = os.path.join(TOOLS, "pcb_requirements.yaml")
TXI = os.path.join(TOOLS, "tx_inhibit.py")


class Refused(Exception):
    pass


def once(text, old, new, where):
    n = text.count(old)
    if n != 1:
        raise Refused("%s: expected the old text once, found it %d times: %r" % (where, n, old[:100]))
    out = text.replace(old, new)
    if out == text:
        raise Refused("%s: the replacement changed nothing" % where)
    return out


# ------------------------------------------------------------------ the RF-002 coverage row
def rf002_span(text):
    m = re.search(r"(?m)^ RF-002: \{", text)
    if not m: raise Refused("pcb_rules_coverage.yaml: no record RF-002")
    n = re.compile(r"(?m)^ [A-Z][A-Z0-9]*-\d+: \{").search(text, m.end())
    return m.start(), (n.start() if n else len(text))


def coverage(text, sha):
    a, b = rf002_span(text)
    row = text[a:b]
    if "NAMED WITH EQ-18" in row:
        return text, "RF-002 row: already applied"
    w = "RF-002 row"
    row = once(row, "through parts whose held pin maps give how they pass it (the 74LVC AND, OR, NAND, inverter, buffer and "
                    "open-drain\n     families,",
               "through parts whose held pin maps give how they pass it (the 74LVC AND, OR, NAND, inverter, buffer and "
               "open-drain\n     families, the SN74LVC1G57 configurable gate as a NOR in the one wiring its row holds (EQ-18),", w)
    row = once(row, "the second-feed check follows resistors, not FET channels or diodes, past the first part; a gate on a\n"
                    "     land its map is not for is UNDECIDED by any pin;",
               "the second-feed check follows resistors, not FET channels or diodes, past the first part; a gate on a\n"
               "     land its map is not for, or a configurable gate wired as its row does not hold (13), is UNDECIDED by any "
               "pin;", w)
    row = once(row, "all five SWITCHES rows\n     carry one. Also since the integration,",
               "all five SWITCHES rows\n     carry one. NAMED WITH EQ-18 (stream w3t, 27 September 2026): (13) a configurable "
               "gate is read in one wiring: the SN74LVC1G57 row holds Figure 7's NOR alone (SCES414P Table 1 with In1 L, Y = "
               "NOR(In0, In2)), In1 on the same net as the part's own GND pin, that net a ground; In1 to ground through a "
               "resistor or a link, on another ground net, on VCC, on a signal or floating, and every other configuration of "
               "its maker's Table 2, read UNDECIDED by any pin, a false UNDECIDED where that wiring would have held; its VCC "
               "pin is read from its pin map in any wiring; on the six committed netlists the only configurable gate is board "
               "C's U14, wired as Figure 7 draws. (14) A HIGH at a Schmitt input never passes: the 74LVC1G17 (DS35124) and "
               "the SN74LVC1G57 (SCES414P) state VT+ at VCC 3 V and 4.5 V only and their 4.5 V rows (2.74 V maximum) are "
               "above VIH_HIGH, so a net EMCON holds HIGH at such an input is UNDECIDED at 2.0 V or more and FAILS under it, "
               "a false UNDECIDED for a net driven to the reader's own rail; their VT- is read at the 3 V row over the band "
               "(0.80 V and 0.84 V minimum), an inference from rows that rise with VCC; no held net on the six committed "
               "netlists is read HIGH at either family. Also since the integration,", w)
    row = once(row, "Board C's and board P's round 8 netlists, committed after this, are read at the consolidated re-take. "
                    "The\n     instrument's declared tables",
               "Board C's and board P's round 8 netlists, committed after this, are read at the consolidated re-take. "
               "READING WITH EQ-18's ROW (stream w3t, 27 September 2026, verdicts written to the stream's scratch) on main "
               "38dcd764's six netlists (A 3a786cf3, B adcc3c67, C 11eabc2d, D 0dad82b4, E f3c1ad61, P 085f8333): "
               "inhibit_chain A FAIL (1 fail, 6 pass, 2 undecided), B FAIL (11 fail, 6 pass, 3 undecided), C FAIL (1 fail, 5 "
               "pass), D FAIL (2 fail, 6 pass), E PASS, P PASS, where the file before the row read A INCONCLUSIVE (5 pass, 4 "
               "undecided), B FAIL (10 fail, 3 pass, 7 undecided), C INCONCLUSIVE (4 pass, 2 undecided), D INCONCLUSIVE (6 "
               "pass, 2 undecided), E PASS, P PASS. The EMCON_HW line moves from UNDECIDED (board C's U14 pin 6) to PASS, and "
               "board B's RockBLOCK 9704 and E22-900M30S, which rode only on it, to PASS; the TX_INHIBIT_n line moves from "
               "UNDECIDED (U14 pin 3) to FAIL, and board D's SA868 keying with it: with board C unpowered its three 100 kOhm "
               "pull-downs (A R145, B R59, D R2) against 31 uA of stated pin current (C's U9 and U14 at Ioff 10 uA each, D's "
               "U12 10 uA, A's U35 and U37 0.5 uA each) reach 1.09 V over the gates' 0.8 V VIL, where without U14 the same "
               "state read 0.74 V. The FAIL rests on the walk's worst-case leakage convention (an unpowered part passes its Ioff; "
               "the three sheets also state II at VCC 0 V, and with U9, U14 and D's U12 at II the line reads about 0.42 V), "
               "and the walk applies VIL 0.8 V to every reader (TI states 0.9 V for A's SN74AUP1G08, 0.8 V for D's U12, which "
               "reads the line when only board C is off): a FAIL under that convention, not a demonstrated defect (open item "
               "W3T-F1 in pcb_requirements.yaml, corrected at the r8int5 integration from the independent check). The\n"
               "     instrument's declared tables", w)
    row = once(row, "AND with tx_inhibit.py as the integration of 27 September 2026 leaves it (sha256\n"
                    "     1d01e6d2999f0f7d3c4f6436b9e2b50c276108fcf054571a3133711e32909031: the twelfth pass's file with board "
                    "A's SN74AUP1G08 row,\n     the walk from each asserted line alone, the enable-row fallback and the named "
                    "limits (8) to (12)).",
               "AND with tx_inhibit.py as stream w3t leaves it for EQ-18 (sha256\n     %s: the integration's file of 27 "
               "September 2026 with the SN74LVC1G57 row read only in its wiring, the Schmitt families' vih_gap and the named "
               "limits (8) to (14)). The integration's file (sha256\n     1d01e6d2999f0f7d3c4f6436b9e2b50c276108fcf054571a3133711e32909031: "
               "the twelfth pass's file with board A's SN74AUP1G08 row,\n     the walk from each asserted line alone, the "
               "enable-row fallback and the named limits (8) to (12)) under-states nothing its note names but reads board "
               "C's U14 as a part it cannot walk, leaving both asserted lines UNDECIDED there, and passes a HIGH at a "
               "74LVC1G17 input at 2.0 V, which DS35124 states at VCC 3 V only." % sha, w)
    row = once(row, "and counts a supply net itself as a source\", owner: SESSION",
               "and counts a supply net itself as a source; limit (13) closes where a board's other wiring of a configurable "
               "gate gets its own configuration row from its maker's table and figure, and (14) where a held sheet states "
               "VT+ over VCC 3 V to 3.6 V\", owner: SESSION", w)
    return text[:a] + row + text[b:], "RF-002 row: applied (tx_inhibit.py sha256 %s)" % sha


# ------------------------------------------------------------------ the open item for finding W3T-F1
MARK = "Finding W3T-F1 (EQ-18's row, stream w3t"


def requirements(text):
    if MARK in text:
        return text, "open item W3T-F1: already present"
    nums = [int(x) for x in re.findall(r"(?m)^  - id: S-(\d+)\s*$", text)]
    if not nums: raise Refused("pcb_requirements.yaml: no S-nn record to number from")
    sid = "S-%02d" % (max(nums) + 1)
    lines = text.split("\n")
    try:
        ci = lines.index("closed_items:")
        oi = lines.index("open_items:")
    except ValueError:
        raise Refused("pcb_requirements.yaml: no open_items or closed_items section")
    if not oi < ci: raise Refused("pcb_requirements.yaml: open_items does not come before closed_items")
    k = ci
    while k > oi + 1 and (lines[k - 1].startswith("#") or not lines[k - 1].strip()):
        k -= 1                                    # the comment block that introduces closed_items belongs to it
    block = [
        "  - id: %s" % sid,
        "    class: SESSION",
        "    status: OPEN",
        "    title: >-",
        "      %s, 27 September 2026; v2/ecad/tools/tx_inhibit.py with the SN74LVC1G57 row): with board C" % MARK,
        "      unpowered, TX_INHIBIT_n's three 100 kOhm pull-downs (board A R145, board B R59, board D R2) hold it at up to",
        "      1.09 V against 31 uA of stated pin current (board C's U9 and U14 at Ioff 10 uA each, DS35124 Rev. 8-2 and",
        "      SCES414P 6.5; board D's U12 10 uA; board A's U35 and U37 0.5 uA each), over the 0.8 V VIL the walk applies",
        "      to the gates that read it (TI states 0.9 V for board A's SN74AUP1G08s, 0.8 V for board D's U12), so RF-002's",
        "      fail-safe state FAILS on boards A to D and board D's SA868 keying inherits it; before round 8's lamp gate U14",
        "      the same state read 0.74 V. The FAIL is under the walk's worst-case leakage convention (an unpowered part",
        "      passes its Ioff); the sheets also state II at VCC 0 V, and with U9, U14 and D's U12 at II the line reads",
        "      about 0.42 V, so it is not a demonstrated defect, and the remedy is margin. For board C's next circuit round.",
        "      Open until the line stays under 0.8 V in every fail-safe",
        "      state with its idle HIGH still above its readers' VIH: (a) board C: R14 10 k to 2.2 k 1 percent and a 10 k 1",
        "      percent pull-down on TX_INHIBIT_n (about 0.24 V failed safe, 2.37 V idle at the adverse ends), one board, the",
        "      session's recommendation; (b) board B's R59 to 10 k 1 percent with R14 to 2.2 k; (c) all three pull-downs to",
        "      47 k with R14 to 4.7 k. The arithmetic is in v2/docs/records/w3t/HANDOFF.md section 2 and",
        "      v2/docs/records/w3t/w3t-decisions.md section 5; engineering question EQ-25.",
    ]
    lines[k:k] = block
    return "\n".join(lines), "open item %s (finding W3T-F1): added" % sid


def main():
    for p in (COV, REQ, TXI):
        if not os.path.isfile(p): raise Refused("missing %s" % p)
    src = open(TXI, encoding="utf-8").read()
    for need in ("NAMED WITH EQ-18", "(13) A CONFIGURABLE GATE IS READ IN ONE WIRING", "(14) A HIGH AT A SCHMITT INPUT NEVER PASSES",
                 'name="74LVC1G57 configurable gate"'):
        if need not in src: raise Refused("tx_inhibit.py in this tree is not stream w3t's: it lacks %r" % need)
    sha = hashlib.sha256(src.encode("utf-8")).hexdigest()
    out, writes = [], []
    for path, fn in ((COV, lambda t: coverage(t, sha)), (REQ, requirements)):
        old = open(path, encoding="utf-8").read()
        new, what = fn(old)
        yaml.safe_load(new)                           # the file still parses
        out.append(what)
        if new != old: writes.append((path, old, new))
    for path, old, new in writes:                     # both computed before either is written (the check's minor)
        if DRY:
            sys.stdout.writelines(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
                                                       os.path.relpath(path, ROOT), os.path.relpath(path, ROOT), n=1))
        else:
            open(path, "w", encoding="utf-8").write(new)
    req = yaml.safe_load(open(REQ, encoding="utf-8").read()) if not DRY else None
    if req is not None:
        hits = [it["id"] for it in req.get("open_items") or [] if MARK in str(it.get("title"))]
        if len(hits) != 1: raise Refused("pcb_requirements.yaml: the W3T-F1 open item is there %d times" % len(hits))
    print("\n".join(out) + ("\n(dry run: nothing written)" if DRY else ""))


if __name__ == "__main__":
    try:
        main()
    except Refused as e:
        print("REFUSED: %s" % e); sys.exit(2)
