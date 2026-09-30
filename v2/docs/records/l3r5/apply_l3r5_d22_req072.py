#!/usr/bin/env python3
"""Carry owner ruling D-22's supply-range rule into REQ-072's acceptance (MESHSAT-1357, layer 3 round 5's last fix round,
30 September 2026). The classification row "an M1 energy claim holds across the charge bus's steady-state supply range
with every load-holding limit at its minimum, the basis's brackets below that range stated beside the result" was
labelled REQUIREMENT while no record carried it: the restatement that would have written it (P-06) went with P-01 to
layer 4 when row L3-OD1 closed as layer 4 architecture. D-22 stands ("Establish the applicable supply range under load
and temperature. If 19.08 V is permitted, mission claims must account for it."), so its rule is written into REQ-072's
desk acceptance as one sentence. It carries an owner ruling that stands; it is no new requirement, and the record's
history says so.

The figures are read from the checked energy basis, v2/docs/records/l3plane/ENERGY-BASIS.md section 2, held at the sha
l3r2.yaml's energy_basis names (the basis CHECK-5 accepted), never typed: the steady-state minimum of VBUS20 across the
in-use envelope, the three brackets beside it, and U3's input-current minimum with its bracket. Only REQ-072's acceptance
changes among its requirement fields; its history keeps the old text and D-22 joins its rulings. Applied once: a second
run refuses.

Usage: python3 apply_l3r5_d22_req072.py [--check] [--registry PATH]
"""
import os
import re
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2", "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402

RID = "REQ-072"
BASIS = "v2/docs/records/l3plane/ENERGY-BASIS.md"
L3DATA = "v2/docs/handover/layer3/l3r2.yaml"
D22_WORDS = "Establish the applicable supply range under load and temperature. If 19.08 V is permitted, mission claims must account for it."
ANCHOR = "on the power path as drawn and on any corrected path named beside it as hypothetical."
MARK = "(D-22:"
STAMP = ("layer 3's closure, round 5's last fix round (2026-09-30), which carries owner ruling D-22 into the acceptance: "
         "an owner ruling that stands, not a new requirement")
BASE_FIELDS = ("kind", "parent", "statement", "acceptance", "allocated_to", "verification_method", "verification_phase",
               "final_phase", "prototype_1", "prototype_1_basis", "release_effect", "status", "obligation", "objective_profile")


def figures():
    """The figures, read from the checked basis by exact patterns; refused if the file is not the checked one."""
    want = yaml.safe_load(E.read(L3DATA))["energy_basis"]
    if want.get("record") != BASIS: E.refuse("l3r2.yaml's energy_basis is not %s" % BASIS)
    if E.sha16(os.path.join(E.TOP, BASIS)) != str(want.get("sha16")):
        E.refuse("%s is not held at the checked basis's sha %s" % (BASIS, want.get("sha16")))
    t = E.read(BASIS)
    sec = t[t.index("## 2. VBUS20 at U3's input"):t.index("\n## 3.")]
    pats = {"min": r"\*\*min ([\d.]+) V, nominal [\d.]+ V, max [\d.]+ V\*\*",
            "rise": r"\| The divider 20 K above the inside air \| ([\d.]+) V \|",
            "endurance": r"\| Both resistors at their endurance limits \| \*\*([\d.]+) V\*\* \|",
            "both": r"\| Both brackets together \| ([\d.]+) V \|",
            "u3": r"The records'\s+([\d.]+) A minimum is INFERRED",
            "u3b": r"\(the maximum mirrored\), with ([\d.]+) A as a bracket"}
    out = {}
    for k, pat in pats.items():
        m = re.findall(pat, sec)
        if len(m) != 1: E.refuse("%s section 2 does not state %s once (pattern %r)" % (BASIS, k, pat))
        out[k] = m[0]
    return out


def clause(f):
    return ("The solar-assisted endurance is computed with the charge bus at U3's input (VBUS20) at its lowest "
            "established steady-state voltage, %s V across the in-use envelope, and every load-holding limit at its "
            "minimum, U3's input current limit at %s A, with the checked energy basis's brackets below that range stated "
            "beside the result: %s V (the divider 20 K above the inside air, an assumption), %s V (both divider resistors "
            "at their makers' endurance limits, a bound) and %s V (both together), and U3's %s A bracket (D-22: \"%s\"; "
            "the figures are ENERGY-BASIS.md section 2's)." % (f["min"], f["u3"], f["rise"], f["endurance"], f["both"],
                                                              f["u3b"], D22_WORDS))


def build(raw):
    d = E.parse(raw)
    rec = next((r for r in d["records"] if r["id"] == RID), None)
    if rec is None: E.refuse("%s is not in the registry" % RID)
    acc = " ".join(str(rec.get("acceptance")).split())
    if MARK in acc: E.refuse("%s's acceptance already carries D-22's clause: this script has run" % RID)
    if rec.get("obligation") != "OBJECTIVE": E.refuse("%s is not the design objective: run apply_l3r5_closure.py first" % RID)
    r22 = next((r for r in d["owner_rulings"] if r["id"] == "D-22"), None)
    if r22 is None or D22_WORDS not in " ".join(str(r22.get("ruling")).split()): E.refuse("D-22 does not carry %r" % D22_WORDS)
    if acc.count(ANCHOR) != 1: E.refuse("%s's acceptance does not read %r once" % (RID, ANCHOR))
    new_acc = acc.replace(ANCHOR, ANCHOR + " " + clause(figures()))
    raw = C.restate(raw, RID, STAMP, acceptance=new_acc)
    return E.replace_entry(raw, RID, lambda b: C.add_ruling_ref(b, "D-22"), "records")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        got = set(E.diff_entries(E.parse(old), E.parse(new)))
        if got != {("records", RID, "changed")}: E.refuse("the entries changed are not the list: %s" % sorted(got))
        fields = E.changed_fields(E.parse(old), E.parse(new), "records", RID)
        if [f for f in fields if f in BASE_FIELDS] != ["acceptance"]:
            E.refuse("the requirement fields changed are %s, not acceptance alone" % fields)
        if fields != ["acceptance", "history", "rulings"]: E.refuse("the fields changed are %s" % fields)
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r5_d22_req072: REFUSED: %s" % e)
        return 2
    print("records  %s  changed (acceptance, with D-22's clause; history; rulings)" % RID)
    print("apply_l3r5_d22_req072: 1 entry, validator 0 errors, %d warnings%s" % (
        len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r5_d22_req072: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
