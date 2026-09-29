#!/usr/bin/env python3
"""S-119's U3B finding: the session decision on Option A(i)'s drafted lid charger U3B, for tools/pcb_decisions.yaml
(stream s119, second round after its independent check, MESHSAT-1357, 29 September 2026). DRAFT for the integrator,
run before apply_registry_s119.py, then decisions_render.py; the author ran --check.

It appends one decision, numbered one above the register's highest at the time it runs (58 on the tree this stream
started from), ruled by the SESSION under the owner's rulings of 21 and 26 September 2026 (engineering decisions are the
session's), with its authority fields. The text passes int7's screen (no claim word, no dash), the result parses, and
nothing but the new entry moves. A second run refuses (a decision already carries the mark "(S-119 U3B)" in its title).

Usage: python3 apply_decision_s119.py [--check]"""
import argparse
import os
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
DEC = os.path.join(TOP, "v2/ecad/tools/pcb_decisions.yaml")
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A  # noqa: E402

MARK = "(S-119 U3B)"
TITLE = ("Option A(i)'s drafted lid charger U3B on U3's 400 kHz row with the FET pair of decision 57: Q7B and Q9B "
         "CSD17578Q5A, Q8B and Q10B CSD17577Q5A, L2B XAL1010-472ME, R16B 10 mOhm " + MARK)
AUTHORITY_WHY = (
    "it changes no line the never-auto floor protects (U3B is a draft in v2/docs/records/a1elec/TOPOLOGY.md and CHARGER.md, "
    "on no generator; no class of tools/reserved.json names those pages), spends nothing the owner decides (part numbers "
    "and values inside a drafted function; no purchase), changes no claim about the kit (Option A(i) is not adopted and its "
    "four owner decisions stay open; the lid charger's function, charge voltage and charge current are unchanged), and "
    "accepts no residual risk a measurement in this tree cannot remove (the switch node, the loop, the temperatures and "
    "REGN's current are bench items). After the measurement one option stands clear: the drafted CSD18510Q5B ask REGN 120 "
    "to 240 mA against its 50 mA minimum limit, the drafted 800 kHz row with CSD17578Q5A in all four positions asks 49.9 mA "
    "at the makers' maxima (inside the limit with no margin), and the 400 kHz row asks 32.6 mA with lower losses.")
OUTCOME = (
    "U3B TAKES U3'S ROW: L2B COILCRAFT XAL1010-472ME (4.7 uH), 191 k 1 PERCENT ON IADPT (SLUSE66A TABLE 9-4, PRINTED PAGE "
    "27), THE COMPENSATION OF TABLE 9-5'S 400 kHz ROW (PAGES 27 AND 28), PWM_FREQ AT ITS POWER-ON 1b (TABLE 9-8, PAGE 43: "
    "'Recommend 800 kHz with 2.2 uH, and 400 kHz with 4.7 uH'), R16B 10 mOhm (RSNS_RAC = 0b) AND R17B 5 mOhm, IIN_HOST 6.2 "
    "A NOMINAL (6.3 A MAXIMUM, UNDER THE 6.35 A CLAMP OF 9.3.5, PAGE 25), THE ILIM_HIZ DIVIDER FROM VDDA SET FOR 3.48 V "
    "(1 V + 40 x 6.2 A x 10 mOhm, THE PIN TABLE, PAGE 6), AND Q7B AND Q9B CSD17578Q5A WHERE EACH LEG HARD-SWITCHES, Q8B "
    "AND Q10B CSD17577Q5A ON THE SYNCHRONOUS SIDE (TI SLPS526 AND SLPS516). REGN then supplies 10.5 mA typical in buck mode "
    "and 32.6 mA at the makers' maxima in buck-boost at 460 kHz against its 50 mA minimum limit (SLUSE66A 8.5, printed page "
    "11; v2/docs/records/s117/efficiency.out section 5). By TI's Equations 6 to 22 (pages 86 to 88) U3B reads 0.974 at the "
    "model's peak hour and 0.972 over the model's own hours, weighted by energy (0.963 to 0.978 across the readings; the "
    "800 kHz row reads 0.957 the same way; v2/docs/records/s119/u3b_hourly.out). The inductor at 400 kHz over the lid's "
    "12.0 to 16.8 V (v2/docs/records/s119/inductor_u3b.out; Coilcraft 804-1 page 1): ripple 1.16 to 2.44 A at the "
    "nominal inductance (15 to 31 percent of the 7.936 A charge current, inside TI's 20 to 40 percent guidance at the "
    "worst points, page 85), up to 3.62 A at 340 kHz with the inductance 20 percent low; peak at most 9.74 A against Isat "
    "25.4 A (typical, 30 percent drop); RMS at most 8.00 A against 17.5 A for a 20 C rise. The model's largest U3B input "
    "is 4.08 A, under the 6.2 A limit. One inductor, IADPT value, compensation and FET pair then serve U3 and U3B.")
REVERSED_BY = (
    "restore TOPOLOGY.md 3b's and CHARGER.md's U3B parts and settings from the parent of this stream's commit that draws "
    "them, or take way (a) of v2/docs/records/s117/U3B-NOTE.md (the 800 kHz row with CSD17578Q5A in all four positions, "
    "L2B XAL1010-332ME, 169 k, R16B 5 mOhm, IIN_HOST 8.0 A), with eta_u3b restated from "
    "v2/docs/records/s119/u3b_hourly.py's 800 kHz row (0.957 over the model's hours) and the chain re-run.")
ASK = ("keep U3B's drafted CSD18510Q5B, which its REGN cannot drive, or draw FETs it can drive: the drafted 800 kHz row "
       "with CSD17578Q5A in all four positions, or U3's 400 kHz row")
RECOMMENDATION = (
    "U3'S 400 kHz ROW. REGN keeps 17 mA of margin at the makers' maxima where the 800 kHz row keeps none, U3B reads 0.972 "
    "over the model's hours against 0.957, and U3 and U3B share their inductor, IADPT resistor, compensation and FET pair; "
    "the 6.35 A input clamp is above the model's largest U3B input. The independent check of stream s119 read the same "
    "REGN figures and supported this row.")
EVIDENCE = (
    "TI SLUSE66A (v2/vendor/ti/bq25731-datasheet.pdf): the pin table pp.5 and 6 (ILIM_HIZ, VDDA), 8.5 pp.11, 15 and 16 "
    "(REGN, VOCP_lim_ACX, FSW), 9.3.5 and Table 9-1 pp.25 and 26, Tables 9-4 and 9-5 pp.27 and 28, Table 9-8 p.43, "
    "10.2.2.3 p.85, 10.2.2.6 pp.86 to 88; TI SLPS526 and SLPS516 (pinned by sha256 in v2/vendor/sources.txt); Coilcraft "
    "804-1 and 804-2 (v2/vendor/power/coilcraft-xal1010.pdf); v2/docs/records/s117/efficiency.py and its .out, sections 4, 5 "
    "and 7; v2/docs/records/s119/u3b_hourly.py, inductor_u3b.py and reconcile_s119.py with their outputs; the independent "
    "check of stream s119 (its item 4 and minor item M1).")
HOLDS = ("it releases no rule-board pair: U3B is on no generator and Option A(i) is not adopted; it lets S-119 close with "
         "its U3B finding answered in the draft, and REQ-072 keeps waiting on S-53, M-02 and S-114.")


def refuse(m):
    print("apply_decision_s119: REFUSED: %s" % m)
    sys.exit(2)


def block(n):
    def f(key, text):
        return "    %s: >-\n%s" % (key, A.fold(text, 6, 120))
    return ("  - n: %d\n" % n + f("title", TITLE) + "    asked: 2026-09-29\n    status: ruled\n    authority: SESSION\n"
            + f("authority_why", AUTHORITY_WHY) + "    ruled_by: SESSION\n    ruled_on: 2026-09-29\n" + f("outcome", OUTCOME)
            + f("reversed_by", REVERSED_BY) + f("ask", ASK) + f("recommendation", RECOMMENDATION) + f("evidence", EVIDENCE)
            + "    blocks: {}\n" + f("holds_nothing_today", HOLDS))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    t = open(DEC, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if any(MARK in str(x.get("title", "")) for x in d["decisions"]):
        refuse("a decision already carries the mark %s (a second run)" % MARK)
    if not any("(S-117 F1)" in str(x.get("title", "")) for x in d["decisions"]):
        refuse("decision 57 (S-117 F1), whose FET pair this takes, is not in the register")
    for what, text in (("title", TITLE), ("authority_why", AUTHORITY_WHY), ("outcome", OUTCOME), ("reversed_by", REVERSED_BY),
                       ("ask", ASK), ("recommendation", RECOMMENDATION), ("evidence", EVIDENCE), ("holds", HOLDS)):
        A.screen(text, "the decision's %s" % what)
    n = max(int(x["n"]) for x in d["decisions"]) + 1
    if not t.endswith("\n"):
        refuse("the register does not end with a newline")
    out = t + block(n)
    after = yaml.safe_load(out)
    if after["decisions"][:-1] != d["decisions"]:
        refuse("an existing decision moved")
    new = after["decisions"][-1]
    for k, v in (("n", n), ("status", "ruled"), ("authority", "SESSION"), ("ruled_by", "SESSION"), ("blocks", {})):
        if new.get(k) != v:
            refuse("the new entry's %s reads %r" % (k, new.get(k)))
    for k in ("authority_why", "reversed_by", "outcome", "ask", "recommendation", "evidence", "holds_nothing_today"):
        if len(str(new.get(k) or "")) < 60:
            refuse("the new entry's %s is short" % k)
    if ".py" not in new["reversed_by"]:
        refuse("the way back names no script")
    if new["title"] != TITLE or new["outcome"] != OUTCOME:
        refuse("the new entry does not read back as written")
    print("apply_decision_s119: decision %d appended (%s...); %d decisions to %d; nothing else moved" % (
        n, TITLE[:60], len(d["decisions"]), len(after["decisions"])))
    if a.check:
        print("CHECK ONLY: pcb_decisions.yaml not written. Next after the write: python3 v2/ecad/tools/decisions_render.py")
        return 0
    open(DEC, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(DEC, encoding="utf-8").read()) != after:
        refuse("re-parse differs")
    print("APPLIED: decision %d in v2/ecad/tools/pcb_decisions.yaml. Next: python3 v2/ecad/tools/decisions_render.py" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
