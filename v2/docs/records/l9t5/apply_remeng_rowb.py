#!/usr/bin/env python3
"""apply_remeng_rowb.py: DRAFT apply script on v2/docs/records/l4close/REMAINING-ENGINEERING.md, section 4 (Layer 9 record l9t5, round
10; Layer 4 task L4A-61: "every claim of the ledger's section 4 that (b) weakens restated or kept PROVISIONAL"; MESHSAT-1357, 7 October
2026, W151). UNAPPLIED: the ledger is the coordinator's; this record runs the script only on scratch copies.

WHAT IT IS: one paragraph and one table after section 4's table, restating, for row (b)'s drafts (record l9t5's canmb, regstage, canen
and hodtest; records l4canen and l4hod; none applied, none checked until row (b)'s check L4A-62), the six claims of section 4 that row
(b) touches: the supervisors' LDOs' sustained bound, CON-004's quorum service, FW-B22, FW-B20 and the controller's survival, T10-A3,
and the connected final figures. Section 4's own rows are left as written (they read the tip `1c6d56f5`); every other section is
untouched; no state is raised: RE-5 to RE-8 stay NOT CLOSED as cx46 filed them, and each restated claim reads PROVISIONAL or
CONDITIONAL.
CITATIONS: the script finds each anchor in the tree's `l9t5_t10.out` and `l9t5_connected.out` WHEN IT IS APPLIED and writes the line
range it finds there (the aliases T10 and CON), so the table cites the outputs it is applied beside; it refuses if an anchor is absent
(the outputs without round 10's sections 11a). Its quotations are words of those outputs (test_remeng holds every quotation to a cited
file).
Usage:  apply_remeng_rowb.py [TARGET] [--check | --write]   (default TARGET: the tree's ledger; default --check: nothing is written)
Exit 0: checked (or written); 3: refused (already applied, an anchor or a cited output missing, or the result does not re-parse)."""
import os
import re
import sys

NAME = "apply_remeng_rowb"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = os.path.join(REPO, "v2", "docs", "records", "l4close", "REMAINING-ENGINEERING.md")
T10 = os.path.join(HERE, "l9t5_t10.out")
CON = os.path.join(HERE, "l9t5_connected.out")
SEC5 = "\n## 5. Summary\n"
HEADER = "**Row (b)'s drafts restate six of these claims (7 October 2026, Layer 4 task L4A-61"
T10_ANCHORS = {   # key: (the first line's start, the last line's start), each found after T10's "11a. ROUND 10" heading
    "d": ("   (d) RE-7, THE SUSTAINED BOUND AT CONSTANT MAXIMUM DISSIPATION", "     with IGND = 0: "),
    "e17": ("     E-17 (THE RECEIVING COMPANY'S MEASUREMENT", "       most "),
    "f": ("   (f) RE-6, THE RESPONSE ON PRINTED TIMING", "     ruled_on 7 October 2026"),
    "g4": ("     (4) T10-A3 with the limiter's", "       (+"),
    "h": ("   (h) L4A-57's ACCEPTANCE", "     L4A-57: "),
    "j": ("   (j) THE T10 ROWS ROW (b)'S DRAFTS CHANGE", "     by apply_remeng_rowb.py"),
}
CON_ANCHORS = {
    "b": ("   (b) THE SERVICE WINDOW ON THE COMPOSED CANDIDATE", "     MODEL, the drafts' records' figures"),
    "c": ("   (c) THE FINAL FIGURES RESTATED", "     L4A-57 reads "),
    "d": ("   (d) THE OPEN ROWS OF SECTION 11 UNDER ROW (b)", "     items 2, 4 and 10"),
}


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def span(path, heading, anchors, key):
    """the line range [first, last] of an anchored block after `heading` in an output (1-based)"""
    if not os.path.isfile(path):
        refuse("the cited output %s is absent" % os.path.basename(path))
    lines = open(path, encoding="utf-8").read().splitlines()
    try:
        h = next(i for i, l in enumerate(lines) if l.startswith(heading))
    except StopIteration:
        refuse("%s carries no %r" % (os.path.basename(path), heading[:30]))
    first, last = anchors[key]
    try:
        s = next(i for i in range(h, len(lines)) if lines[i].startswith(first))
        e = next(i for i in range(s, len(lines)) if lines[i].startswith(last))
    except StopIteration:
        refuse("%s: the anchor %r is not found after its heading" % (os.path.basename(path), first[:40]))
    return "%d-%d" % (s + 1, e + 1) if e > s else "%d" % (s + 1)


def block():
    t = {k: span(T10, "11a. ROUND 10", T10_ANCHORS, k) for k in T10_ANCHORS}
    c = {k: span(CON, "11a. ROW (b)'S DRAFTS", CON_ANCHORS, k) for k in CON_ANCHORS}
    tt = open(T10, encoding="utf-8").read()
    if "L4A-57: DONE AS CONDITIONAL on E-17." not in tt:
        refuse("T10's section 11a does not read L4A-57 as DONE AS CONDITIONAL on E-17")
    return (
        "\n" + HEADER + "; DRAFTED, none applied, unchecked until row (b)'s check L4A-62).** Row (b)'s drafts take the place of the "
        "containment that section 4's rows read (record l9t5 `apply_gen_sch_b_canmb.py`, `apply_gen_sch_b_regstage.py`, "
        "`apply_gen_sch_b_canen.py`, `apply_gen_sch_b_hodtest.py`). The rows above stand as the tip `1c6d56f5` read them; each claim row "
        "(b) touches reads as below with the drafts, and no state is raised: RE-5 to RE-8 stay NOT CLOSED as cx46 filed them. The line "
        "numbers below are those of the outputs this table was applied beside.\n\n"
        "| Claim (its row above) | Row (b)'s draft | State it reads with the drafts (cited) |\n"
        "|---|---|---|\n"
        "| The supervisors' LDOs' 125 C sustained bound | regstage (W138): a TPS2553-1 latch-off limiter ahead of a TPS73733DCQRM3 at each "
        "supervisor, the rail trip removed; hodtest (W146): the limiter's latent loss of its limit found by the peers' in-service test | "
        "SUPPORTED ON PRINTED FIGURES with the theta read as printed, CONDITIONAL on E-17 (the site's theta, its Zth at 10 ms and the "
        "ground current), PROVISIONAL until L4A-62: the junction at constant maximum dissipation at the limiter's printed maximum bounds "
        "every waveform under it, cx46's countermodel included ([T10:%s]); the printed theta is a JEDEC best case, so E-17 decides the "
        "condition ([T10:%s]); L4A-57 \"DONE AS CONDITIONAL on E-17\" ([T10:%s]); the output out of regulation excluded with its reason, "
        "W151-1 ([T10:%s]); a lost limit found within 3602.341 s (record l4hod, DRAFTED) |\n"
        "| CON-004's quorum service | canmb (W137, W143), canq (W139), canen (W143) | DRAFTED, PROVISIONAL until L4A-62: the peers' "
        "attribution and 2-of-2 votes hold the quorum on IOHA rows 3, 5 and 7, lost only with both fabrics broken (row 8) ([T10:%s]); the "
        "FMEA rows 21 to 24 drafted (record l9t5 `apply_ioha_fmea_rowb.py`) |\n"
        "| FW-B22, the quorum's schedule | canq's restated schedule (W139, W143) and the in-service test's restart exception | PROVISIONAL, "
        "DRAFTED (records l9t5 `apply_hw_fw_contract_canq.py` and `apply_hw_fw_contract_rowb.py`, none applied) |\n"
        "| FW-B20 and the controller's survival | regstage (the limiter's least is over VOS0's current, so it does not bound HO-E) | "
        "PROVISIONAL, unchanged by row (b): HO-E is L4A-59's with its check L4A-100 ([T10:%s]); FW-B20's enabled set restated with TIM3 "
        "and an ADC (record l9t5 `apply_hw_fw_contract_rowb.py`) |\n"
        "| T10-A3, the LDO input headroom at the hardware bound | regstage: the limiter's resistance in place of the sense resistor, at the "
        "limiter's maximum on all three | PROVISIONAL (V-T10-DROP extended, L4REG-F2; L4A-62): it holds on the 1 A dropout row taken as "
        "the bound and on the INFERRED linear dropout ([T10:%s]) |\n"
        "| The worst-case margin row and the final figures of the connected trace | the four drafts with their rail additions | restated "
        "in the connected output's section 11a: the service window with row (b)'s enabled set and the drafts' additions ([CON:%s]), the "
        "final figures and the worst-case margin row on the selected stage, CONDITIONAL on E-17 ([CON:%s]), section 11's rows 5, 6, 7 "
        "and 17 under row (b), each keeping cx46's state ([CON:%s]) |\n" % (
            t["d"], t["e17"], t["h"], t["f"], t["j"], t["j"], t["g4"], c["b"], c["c"], c["d"]))


def patched(text):
    if HEADER in text:
        refuse("the change is already applied")
    if text.count(SEC5) != 1 or "\n## 4. The claims a remaining item weakens" not in text:
        refuse("sections 4 and 5 are not the ones this draft was written against")
    head, tail = text.split(SEC5)
    new = head.rstrip("\n") + "\n" + block() + SEC5 + tail
    if new == text:
        refuse("the result does not differ")
    sec4 = new.split("\n## 4. The claims a remaining item weakens", 1)[1].split(SEC5, 1)[0]
    rows = [l for l in sec4.splitlines() if l.startswith("| ") and not l.startswith("|---")]
    sub = sec4.split(HEADER, 1)[1]
    srows = [l for l in sub.splitlines() if l.startswith("| ") and not l.startswith("|---")]
    if len(srows) != 7 or any(len(l.strip().strip("|").split(" | ")) != 3 for l in srows):
        refuse("the restated table does not parse into a heading and six rows of three cells")
    if len(rows) != len([l for l in head.split("\n## 4. The claims a remaining item weakens", 1)[1].splitlines()
                         if l.startswith("| ") and not l.startswith("|---")]) + 7:
        refuse("section 4's own table changed")
    if block().count('"') % 2 or re.search("[" + chr(0x2013) + chr(0x2014) + "]", block()):
        refuse("an unpaired quotation mark or a long dash in the new text")
    return new


def main(argv):
    target, mode = TREE, "--check"
    for a in argv:
        if a in ("--check", "--write"):
            mode = a
        else:
            target = os.path.abspath(a)
    if not os.path.isfile(target):
        refuse("no target %s" % target)
    old = open(target, encoding="utf-8").read()
    new = patched(old)
    if mode == "--write":
        tmp = target + ".rowb-tmp"
        open(tmp, "w", encoding="utf-8").write(new)
        os.replace(tmp, target)
        print("%s: WRITTEN, section 4's restated table (six claims)" % NAME)
    else:
        print("%s: CHECK OK, section 4's restated table (six claims) would be added (nothing written)" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
