#!/usr/bin/env python3
"""IF-AB-POWER's `currents` rows in tools/pcb_interfaces.yaml rewritten to the interim alignment of S-98 (stream s98,
MESHSAT-1357, 28 September 2026; finding I-03, the Codex pilot's record v2/docs/records/cx1/ and its two checks).

The integrator runs it (the contract file is the integrator's; this stream owns the two generators only), AFTER the two
generators carry the alignment (fnd/s98) and BEFORE the box re-take: the file is a configuration input of interfaces.py,
so INT-001 reads CONFIG_CHANGED until the set's box re-take.

What changes: the four rows under `currents` (the S1/S3 row's generator line numbers; the +5V_S2 row's both ends and its
status, DISAGREE to the aligned INTERIM statement with the mode figure INCONCLUSIVE; the +5V_DEV row's both ends and its
status, DISAGREE at the lead to the aligned INTERIM statement, the converter-side peak named as S-99's; the +54V_POE row's
generator line numbers). NOT changed, deliberately: the `converters` line and its "7.2 to 9.5 A average current limit",
which stream s99 computes from the LM5176 stage's actual limits (the nominal-shunt arithmetic reproduces, 43 and 57 mV
over 6 mOhm = 7.17 and 9.5 A, SNVSAI1D VSNS p.7; the +1 percent shunt figure 7.10 A is S-99's); the `ends` src line
numbers (stale before this stream, noted in the record's README); everything else in the contract.

Asserted: the IF-AB-POWER block and its `currents` span are found once; the old rows parse to exactly the rows this
script expects (a second run, or a file edited since, is refused); every generator line the new rows cite holds the
declaration text they describe (read from the generators at run time, so a later edit that moves a line is refused with
the line where the text now is); the new text parses; the parsed document differs from the old ONLY in
board_to_board.contracts.IF-AB-POWER.currents; the file written re-parses to what was checked; no em or en dash.

Usage: python3 apply_contract_i03.py [--root <repository root>]   (default: the git top level of this file)
"""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

OLD_ROWS = [
    {"rail": "+5V_S1, +5V_S3", "a_declares": "2.5 A typical, 5.0 A peak (gen_sch_a.py:106)", "b_declares": "2.5 A typical, 5.0 A peak (gen_sch_b.py:72)",
     "enable": "SLOT_ENx from the panel; OFF until the panel firmware drives it"},
    {"rail": "+5V_S2", "a_declares": "2.5 A typical, 5.0 A peak (gen_sch_a.py:106)",
     "b_declares": "4.2 A typical, 5.0 A peak, 5.63 A coincident peak with the 5G module at 4 A (gen_sch_b.py:66-72)",
     "status": "DISAGREE: the two ends declare different currents for one conductor (I-03, open); A's stage limits at 7.2 A"},
    {"rail": "+5V_DEV", "a_declares": "4.0 A typical, 6.9 A peak at the converter, of which 3.2 A apportioned to J_5V_DEV (gen_sch_a.py:110-115)",
     "b_declares": "3.8 A typical, 6.0 A peak arriving (gen_sch_b.py:90)",
     "status": "DISAGREE at the lead (A 3.2 A against B 3.8 A typical); enable DEV_EN, ON by design since 458b2873 (R42)"},
    {"rail": "+54V_POE", "declared": "0.3 A typical, 0.6 A peak on both ends (gen_sch_a.py:125, gen_sch_b.py:242)",
     "enable": "POE_EN = POE_SW_EN AND OUTLET_OK: OFF at power-up and while the PA keys (S-14)"},
]

# the generator lines the new rows cite, with the text each must hold (read at run time)
CITES = {
    ("gen_sch_a.py", 48): '"Q28": 2.22',
    ("gen_sch_a.py", 113): '_intent.rail("+5V_S%s" % _n, 5.1, 4.2 if _n == "2" else 2.5, 5.63 if _n == "2" else 5.0, _sh, loads={"J_5V_S%s" % _n: 5.63 if _n == "2" else 5.0}',
    ("gen_sch_a.py", 135): '_intent.rail("+5V_DEV", 5.0, 5.1, 6.9, "R43", loads={"J_5V_DEV": 3.8, "U23": 1.0, "U32": 0.3}',
    ("gen_sch_a.py", 147): '_intent.rail("+54V_POE", 54.0, 0.3, 0.6, "R71", loads={"J_54V": 0.3}',
    ("gen_sch_b.py", 85): '_intent.rail("+5V_S%d" % _n, 5.1, 4.2 if _n == 2 else 2.5, 5.63 if _n == 2 else 5.0, "J_5V_S%d" % _n',
    ("gen_sch_b.py", 111): '_intent.rail("+5V_DEV", 5.0, 3.8, 6.0, "J_5V_DEV", loads=_DEV_LOADS',
    ("gen_sch_b.py", 271): '_intent.rail("+54V_POE", 54.0, 0.30, 0.60, "J_54V"',
}

NEW = (
    '      currents:\n'
    '        - {rail: "+5V_S1, +5V_S3", a_declares: "2.5 A typical, 5.0 A peak (gen_sch_a.py:113, slots 1 and 3; the AP64500\'s 5 A rating)",\n'
    '           b_declares: "2.5 A typical, 5.0 A peak (gen_sch_b.py:85)",\n'
    '           enable: "SLOT_ENx from the panel; OFF until the panel firmware drives it"}\n'
    '        - {rail: "+5V_S2", a_declares: "4.2 A typical, 5.63 A peak, J_5V_S2 5.63 A (gen_sch_a.py:113; the VBAT load Q28 2.22 A,\n'
    '             gen_sch_a.py:48)",\n'
    '           b_declares: "4.2 A typical, 5.63 A peak, the CM5 at its 1.6 A allowance coincident with the 5G module at 4 A\n'
    '             (gen_sch_b.py:85)",\n'
    '           status: "AGREE since S-98 (28 September 2026), INTERIM: both ends carry the figures board B derives from the held\n'
    '             maker pages (the CM5\'s 0.9 A typical, release 3 Table 9, no maximum published; the RM520N-GL\'s 3 A continuous\n'
    '             and 4 A peak supply capability, Hardware Design v1.0 and v1.1; v2/docs/records/cx1/ANALYSIS.md, CORRECTION.md\n'
    '             B1). The PS-ALLTX mode current is INCONCLUSIVE at both ends: no held document decides it, the bench decides it\n'
    '             at J_5V_S2 (TEST-PLAN power tests). The all-peak conditional bound, 7.28 A, sits above the stage\'s average loop\n'
    '             minimum of 7.10 to 7.17 A (S-99 owns the stage limits)"}\n'
    '        - {rail: "+5V_DEV", a_declares: "5.1 A typical, 6.9 A peak at the converter, of which 3.8 A apportioned to J_5V_DEV,\n'
    '             1.0 A to the D8 mezzanine\'s eFuse U23 and 0.3 A to the wall port\'s eFuse U32 (gen_sch_a.py:135)",\n'
    '           b_declares: "3.8 A typical, 6.0 A peak arriving (gen_sch_b.py:111)",\n'
    '           status: "AGREE at the lead since S-98 (28 September 2026), INTERIM: A apportions 3.8 A to J_5V_DEV and B declares\n'
    '             3.8 A typical arriving; the PS-ALLTX mode current is INCONCLUSIVE at both ends (v2/docs/records/cx1/CORRECTION.md\n'
    '             B2). The converter-side peak is S-99\'s: A\'s 6.9 A is B\'s 6.0 A plus the wall port\'s 0.9 A with the D8 mezzanine at\n'
    '             zero, against 7.9 A (D8 at its 1.0 A typical) and 8.9 A (every declared limit) coincident, both above the LM5176\n'
    '             average loop\'s minimum. Enable DEV_EN, ON by design since 458b2873 (R42)"}\n'
    '        - {rail: "+54V_POE", declared: "0.3 A typical, 0.6 A peak on both ends (gen_sch_a.py:147, gen_sch_b.py:271)",\n'
    '           enable: "POE_EN = POE_SW_EN AND OUTLET_OK: OFF at power-up and while the PA keys (S-14)"}\n'
)


def refuse(msg):
    print("apply_contract_i03: REFUSED: %s" % msg); sys.exit(2)


def main(argv):
    root = argv[argv.index("--root") + 1] if "--root" in argv else subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
    P = os.path.join(root, "v2/ecad/tools/pcb_interfaces.yaml")
    if re.search("[\\u2013\\u2014]", NEW): refuse("the new text carries a dash")
    t = open(P, encoding="utf-8").read()
    before = yaml.safe_load(t)
    # the IF-AB-POWER block: from its key line to the next contract's key line at the same indentation
    m = re.search(r"(?m)^    IF-AB-POWER:\n", t)
    if not m: refuse("no IF-AB-POWER block")
    nxt = re.search(r"(?m)^    IF-[A-Z0-9-]+:\n", t[m.end():])
    i, j = m.start(), (m.end() + nxt.start()) if nxt else len(t)
    block = t[i:j]
    a = block.find("\n      currents:\n"); b = block.find("\n      contact_rating:")
    if a < 0 or b < 0 or b < a: refuse("the currents span is not found once between `currents:` and `contact_rating:` in the block")
    if block.count("\n      currents:\n") != 1: refuse("more than one currents key in the block")
    old_span = block[a + 1:b + 1]                       # from '      currents:' through the last row's line, inclusive of its newline
    if old_span == NEW: refuse("already applied (the rows carry the new text)")
    old_rows = yaml.safe_load(old_span)["currents"]
    if old_rows != OLD_ROWS: refuse("the old rows are not the rows this script expects (edited since, or a second run): %s" % old_rows)
    # every generator line the new rows cite holds its declaration
    for (fn, ln), text in CITES.items():
        lines = open(os.path.join(root, "v2/ecad/tools", fn), encoding="utf-8").read().split("\n")
        if ln > len(lines) or text not in lines[ln - 1]:
            where = [k + 1 for k, l in enumerate(lines) if text in l]
            refuse("%s:%d does not hold %r (found at line(s) %s): re-number the rows" % (fn, ln, text[:60], where or "none"))
    new_block = block[:a + 1] + NEW + block[b + 1:]
    out = t[:i] + new_block + t[j:]
    if out == t: refuse("the new text does not differ from the old")
    after = yaml.safe_load(out)
    # only board_to_board.contracts.IF-AB-POWER.currents may differ
    def strip(d):
        d = yaml.safe_load(yaml.safe_dump(d))            # a deep copy
        d["board_to_board"]["contracts"]["IF-AB-POWER"].pop("currents")
        return d
    if strip(before) != strip(after): refuse("something other than IF-AB-POWER's currents changed")
    ca, cb = before["board_to_board"]["contracts"]["IF-AB-POWER"], after["board_to_board"]["contracts"]["IF-AB-POWER"]
    if ca["converters"] != cb["converters"]: refuse("the converters line changed")
    if [r["rail"] for r in cb["currents"]] != [r["rail"] for r in ca["currents"]]: refuse("the rails of the rows changed")
    for r in cb["currents"][1:3]:
        if not r["status"].startswith("AGREE") or "INTERIM" not in r["status"] or "INCONCLUSIVE" not in r["status"]:
            refuse("a rewritten status does not say AGREE, INTERIM and INCONCLUSIVE: %s" % r["status"][:80])
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_contract_i03: IF-AB-POWER currents rows rewritten: +5V_S2 and +5V_DEV read AGREE (INTERIM, mode figures INCONCLUSIVE); "
          "generator lines re-numbered (A 48, 113, 135, 147; B 85, 111, 271); the converters line untouched")
    print("apply_contract_i03: pcb_interfaces.yaml is a configuration input of interfaces.py: INT-001 reads CONFIG_CHANGED until the box re-take")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
