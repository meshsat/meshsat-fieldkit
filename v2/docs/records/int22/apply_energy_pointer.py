#!/usr/bin/env python3
"""Item 3 of the unified independent review of the Layer 3 amendment (MESHSAT-1357, 1 October 2026,
v2/docs/records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md): "Maintain the current energy-evidence pointer. Layer 3 still labels
the retained-window Layer 4 result as pending. Link the checked Layer 4 result through the current status/evidence
documentation while retaining the historical P-03 qualification."

The pointer goes where the accepted baseline does not bind it: REQ-072's notes (commentary, outside
render_l3r2.requirements_projection) and LAYER-STATUS.md's layer 3 section (a view). Not as an evidence entry: REQ-072's
last evidence entry is its baseline evidence (test_l3r5, a file the amendment's closure binds, reads the runtime figures
there, and the notes call it "this record's latest evidence entry"), and L4-E2's result is a layer 4 reading that changes
no verdict. l3r2.yaml's
solar_case and the three Layer 3 pages keep naming the result pending, as accepted at 3b4b92cf: they are the acceptance
policy and its views, and a change there would need the baseline accepted again.

Nothing is written until every check passes: each target is located by its own words and asserted once; the registry is
re-parsed and compared with the parsed original (only REQ-072's notes may differ, by the appended sentences); the
requirements digest and the acceptance's verdict are unchanged; no dash character and no claim
word of claims_check.py is written. A second run is refused. Usage: apply_energy_pointer.py [--check]
"""
import copy
import os
import re
import sys
import textwrap

sys.dont_write_bytecode = True
TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
for p in ("v2/docs/handover/layer3", "v2/ecad/tools"): sys.path.insert(0, os.path.join(TOP, p))
import yaml  # noqa: E402
import render_l3r2 as RL  # noqa: E402
import rules_lib as R  # noqa: E402
from claims_check import CLAIM  # noqa: E402

REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
PAGE = os.path.join(TOP, "v2/docs/handover/LAYER-STATUS.md")
MARK = "Pointer maintained on 1 October 2026"
NOTE = (
    " " + MARK + " (item 3 of the unified independent review of the amendment, "
    "v2/docs/records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md): L4-E2's result on the retained window is filed and checked in "
    "v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (its figures printed in l4e_replay.out; the coordinator's check "
    "v2/docs/records/l4e/checks/check-l4e2-3.md accepted it, and the owner's independent reviewer reproduced its replay "
    "companion offline). With the stage's input clipped at REQ-016's 100 W instead of the 200 W window of proposal P-03's "
    "array, neither architecture meets 48 hours: A2 on the hypothetical corrected path stops at 05 UTC of the first night, "
    "270.1 / 286.3 Wh unserved at 48 h (06 / 18 UTC starts); A1 stops 2 or 13 h in. It is a layer 4 reading, not this "
    "record's evidence: the verdict and the latest evidence entry stay as accepted, and l3r2.yaml's solar_case and the "
    "Layer 3 pages keep naming the result pending as accepted at 3b4b92cf.")
PARA = (
    "**The unified independent review of the amendment, and the current energy evidence (1 October 2026, "
    "`v2/docs/records/l3am/REVIEW-UNIFIED-AS-RECEIVED.md`).** The owner's independent reviewer reproduced the compact "
    "package `MESHSAT-L3-AMENDMENT-f8514c0b` offline in a second environment (140 tests passed, 0 failed, 0 skipped) and "
    "reads the layer READY as an accepted requirements baseline for Layer 4 work and engineering handover, L3-R01 to "
    "L3-R05 CLOSED against their criteria; the accepted revision stays `3b4b92cf` and none of the accepted content "
    "changed. Its new nonblocking finding L3-N01 (the helper `ver()` of `v2/docs/records/l3am/checks/verify_l3am.py` "
    "read the verifier's revision return as a refusal, so its one negative probe could not fail) is fixed in that "
    "checking tool (`v2/docs/records/int22/`). Its item 3, the energy-evidence pointer: the result on REQ-016's retained "
    "window, which `l3r2.yaml`'s solar case and the three Layer 3 pages name as pending under L4-E2 as accepted, is filed "
    "and checked in `v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md` (the coordinator's checks `checks/check-l4e2-3.md` "
    "and `check-l4e3-2.md` accepted; the replay companion reproduced by the reviewer, L4-R03 closed). With the stage's "
    "input clipped at REQ-016's 100 W, neither architecture meets 48 hours: A2 on the hypothetical corrected path stops "
    "at 05 UTC of the first night, 270.1 / 286.3 Wh unserved at 48 h; A1 stops 2 or 13 h in. These are not the "
    "historical results of proposal P-03's array (400 Wp into the model's 200 W stage window), which keep their label "
    "wherever they are stated. REQ-072's notes carry the pointer; it reads FAIL at desk as before, design risk "
    "DR-01.")
PAGE_BEFORE = "\n\n**The completion gate (D-21, and the fifth condition of D-26).**"
PAGE_AFTER = "**Now (1 October 2026): Layer 3 accepted baseline, accepted again at `3b4b92cf` after the amendment;"


class Refused(Exception):
    pass


def refuse(why):
    raise Refused(why)


def once(text, old, new, what):
    if text.count(old) != 1: refuse("%s: %d occurrences of %r, one expected" % (what, text.count(old), old[:70]))
    return text.replace(old, new)


def fold(text, indent):
    return textwrap.fill(text, width=120, initial_indent=" " * indent, subsequent_indent=" " * indent,
                         break_on_hyphens=False, break_long_words=False)


def build_registry(raw):
    if MARK in raw: refuse("apply_energy_pointer has run (REQ-072 already carries the pointer)")
    a = raw.index("\n  - id: REQ-072\n") + 1
    b = raw.index("\n  - id: ", a) + 1
    blk = raw[a:b]
    end = "      FAIL at desk either way (DR-01).\n"
    lines = fold("FAIL at desk either way (DR-01)." + NOTE, 6) + "\n"
    new = once(blk, end, lines, "REQ-072's notes end")
    return raw[:a] + new + raw[b:]


def build_page(text):
    if "**The unified independent review of the amendment, and the current energy evidence" in text:
        refuse("apply_energy_pointer has run (the page carries the paragraph)")
    if text.count(PAGE_AFTER) != 1: refuse("the layer 3 'Now' paragraph is not on the page once")
    i = text.index(PAGE_AFTER)
    j = text.index(PAGE_BEFORE, i)
    return text[:j] + "\n\n" + PARA + text[j:]


def check_registry(raw, out):
    y0 = yaml.load(raw, Loader=yaml.CSafeLoader); y1 = yaml.load(out, Loader=yaml.CSafeLoader)
    r0 = {r["id"]: r for r in y0["records"]}; r1 = {r["id"]: r for r in y1["records"]}
    if list(r0) != list(r1): refuse("the records' ids or order changed")
    for k in y0:
        if k != "records" and y0[k] != y1.get(k): refuse("the registry's %s changed" % k)
    for rid in r0:
        if rid == "REQ-072": continue
        if r0[rid] != r1[rid]: refuse("%s changed" % rid)
    a, b = copy.deepcopy(r0["REQ-072"]), copy.deepcopy(r1["REQ-072"])
    if b["notes"] != a["notes"] + NOTE: refuse("REQ-072's notes are not the old notes plus the pointer")
    a.pop("notes"); b.pop("notes")
    if a != b: refuse("REQ-072 changed outside its notes")
    if RL.requirements_digest(y0) != RL.requirements_digest(y1): refuse("the requirements digest changed")
    return y1


def main(argv):
    check = "--check" in argv
    raw = open(REG, encoding="utf-8").read(); page = open(PAGE, encoding="utf-8").read()
    for t in (NOTE, PARA):
        if any(c in t for c in ("–", "—")): refuse("a dash character in the text")
        m = CLAIM.search(t)
        if m: refuse("the claim word %r in the text" % m.group(0))
    out = build_registry(raw); y1 = check_registry(raw, out)
    pout = build_page(page)
    if pout.replace(PARA + "\n\n", "", 1) != page: refuse("the page changed outside the paragraph")
    data = RL.load_data()
    ok0 = RL.acceptance_ok(R.load_requirements(), data)[0]; ok1 = RL.acceptance_ok(y1, data)[0]
    if not (ok0 and ok1): refuse("the acceptance does not validate before and after (%s, %s)" % (ok0, ok1))
    if check:
        print("apply_energy_pointer: CHECK PASS (nothing written)"); return 0
    open(REG, "w", encoding="utf-8").write(out); open(PAGE, "w", encoding="utf-8").write(pout)
    print("apply_energy_pointer: REQ-072's notes and LAYER-STATUS.md written")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Refused as e:
        print("apply_energy_pointer: REFUSED: %s" % e); sys.exit(2)
