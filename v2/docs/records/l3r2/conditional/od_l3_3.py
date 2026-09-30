#!/usr/bin/env python3
"""Row L3-OD3 of OWNER-DECISIONS-L3.md: the solar input, its stage, its array and REQ-016's window. PREPARED, NOT APPLIED.
Requires row L3-OD1 decided, approved or rejected (battery and solar stay mandatory either way, D-26). This row alone
fixes the array and the stage (row L3-OD1 fixes only the store), and it replaces the marked phrase od_l3_1.py leaves in
REQ-072's acceptance with the array it decides, or, after a reject, adds the array to REQ-072 as a note, so REQ-072,
REQ-016 and the ruling can only name one array (CHECK-1, B1). The answer approves the topology and the voltage class; it
verifies no rating (D-26: "Approve topology separately from electrical compliance"): every option records feasibility
item FI-06, the interface's derivations and obligations O-1 to O-7 of the checked feasibility record.

  --option 2s2p   four 100 W panels in two series pairs, 400 Wp at STC, into a 200 W stage: REQ-016 restated
                  (v2/docs/records/a1solar/ARRAY.md section 5, its fuse and connector at 20 A)
  --option 1s4p   the four panels in parallel, 400 Wp, into a 200 W stage: REQ-016 restated (the same section's
                  alternative, its entry at 40 A and a fuse per panel)
  --option keep   REQ-016's 100 W window kept; the array REQ-072 names and REQ-016's fuse and connector clause come from the
                  checked energy basis for the lid chosen (--array-wp, --entry-a and --evidence, each figure asserted in
                  the evidence file, exactly, and on the tree that file is the filed basis); the 1600 Wp of DECISION-OPTIONS.md A (ii) is for 4S18P and is not used

Every figure written is first asserted in the file it comes from. The array's panels and stand travel outside the case
(v2/docs/records/a1solar/SELECTION.md), which each ruling states.

Usage: python3 od_l3_3.py --option 2s2p|1s4p|keep --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
       [--array-wp N --entry-a N --evidence PATH]   (keep only)
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD3"
ARRAY_MD = "v2/docs/records/a1solar/ARRAY.md"
SELECTION_MD = "v2/docs/records/a1solar/SELECTION.md"
STOW = (" The array's panels and their folding stand travel outside the case, beside it (v2/docs/records/a1solar/SELECTION.md); "
        "the array is part of the kit's claimed form. It authorises no purchase.")
TEXT = {
    "2s2p": {
        "assert": ["at most 200 W into the stage; the array's open-circuit voltage at most 51.3 V at -20 C cells",
                   "(54.1 V at -40 C), every part on the panel entry rated above 56.3 V; the array held at 34.3 V (33.0 to 35.6 V)",
                   "F2 20 A and at least 56.3 V DC with an interrupting rating above the kit-side fault current",
                   "J_SOLAR, the wall pair and the lead at least 20 A"],
        "statement": ("The solar input charges {store} through board E's stage from the kit's array inside its declared "
                      "window: at most 200 W into the stage; the array's open-circuit voltage at most 51.3 V at -20 C cells "
                      "(54.1 V at -40 C), every part on the panel entry rated above 56.3 V; the array held at 34.3 V (33.0 "
                      "to 35.6 V) by the stage's input regulation ({rid})."),
        "acceptance": ("Netlist (board E): the panel entry (PV_IN and PV_P) declared at 56.3 V (v_max) in the generator's "
                       "intent and every part on it rated above 56.3 V; the input regulation's divider sets 34.3 V, 33.0 to "
                       "35.6 V with its tolerances; F2 rated 20 A and at least 56.3 V DC, with an interrupting rating at or "
                       "above the kit-side prospective fault current; J_SOLAR, the wall's solar pair and the array's lead "
                       "rated 20 A or more; the 200 W window implemented by the stage's input or output current regulation, "
                       "or every part downstream of the stage carrying a rating at or above what its inductor current limit lets through. "
                       "Prototype: a bench supply set to an array curve with a 51.3 V open circuit and its maximum-power "
                       "point above the set point charges {store} through the stage at 200 W with the stage holding its "
                       "input at the set point, and the power the stage takes is measured."),
        "ruling": ("Row L3-OD3 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: REQ-016 is restated for the 2S2P "
                   "array at 200 W (v2/docs/records/a1solar/ARRAY.md section 5)."),
    },
    "1s4p": {
        "assert": ["at most 200 W; open-circuit voltage at most 25.6 V at -20 C cells (27.0 V at -40 C; 28.1 V by the clause);",
                   "the array held at 16.7 to 17.6 V; the entry rated at least 40 A; a fuse of 10 to 15 A per panel."],
        "statement": ("The solar input charges {store} through board E's stage from the kit's array inside its declared "
                      "window: at most 200 W into the stage; the array's open-circuit voltage at most 25.6 V at -20 C cells "
                      "(27.0 V at -40 C), every part on the panel entry rated above 28.1 V; the array held at 16.7 to 17.6 V "
                      "by the stage's input regulation ({rid})."),
        "acceptance": ("Netlist (board E): the panel entry (PV_IN and PV_P) declared at 28.1 V (v_max) in the generator's "
                       "intent and every part on it rated above 28.1 V; the input regulation's divider holds 16.7 to 17.6 V "
                       "with its tolerances; F2 rated 40 A with an interrupting rating at or above the kit-side prospective "
                       "fault current, and a fuse of 10 to 15 A for each panel; J_SOLAR, the wall's solar pair and the "
                       "array's lead rated 40 A or more; the 200 W window implemented by the stage's input or output current "
                       "regulation, or every part downstream of the stage carrying a rating at or above what its inductor "
                       "current limit lets through. Prototype: a bench supply set to an array curve with a 25.6 V open circuit and its "
                       "maximum-power point above the set point charges {store} through the stage at 200 W with the stage "
                       "holding its input inside 16.7 to 17.6 V, and the power the stage takes is measured."),
        "ruling": ("Row L3-OD3 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: REQ-016 is restated for the four "
                   "panels in parallel (1S4P) at 200 W (v2/docs/records/a1solar/ARRAY.md section 5)."),
    },
}


def build(a, raw, d):
    dec = C.require(d, ROW, ["L3-OD1:approve|reject"])
    op = a["option"]
    two = dec["L3-OD1"][0] == "approve"
    store = "the packs" if two else "the kit's pack"
    COMPLY = (" Approving the topology and the voltage class verifies no rating of the interface: feasibility item FI-06 "
              "carries its derivations and obligations O-1 to O-7 (D-26).")
    E.assert_in("v2/docs/records/l3feas/L3-FEASIBILITY.md", ["**Pinning the revision is therefore an engineering obligation (O-1).**",
                                                             "**O-2:** implement the window"])
    import od_l3_1 as O1
    if op in TEXT:
        E.assert_in(ARRAY_MD, TEXT[op]["assert"])
        E.assert_in(SELECTION_MD, ["four panels of 1219 x 549 mm travel flat beside the case", "a folding stand is part of the array"])
        raw, rid = C.add_ruling(raw, d, ROW, op, "The solar input: REQ-016 restated for the 200 W stage, %s (row L3-OD3)" % op.upper(),
                                TEXT[op]["ruling"] + STOW + COMPLY, a["words"], a["date"])
        stamp = "%s (row L3-OD3, %s)" % (rid, a["date"])
        raw = C.restate(raw, "REQ-016", stamp, statement=TEXT[op]["statement"].format(rid=rid, store=store),
                        acceptance=TEXT[op]["acceptance"].format(store=store))
        raw = E.replace_entry(raw, "REQ-016", lambda b: E.append_folded(C.add_ruling_ref(b, rid), "notes",
            ("Restated by %s for Option A(i)'s 200 W stage; the conflict with REQ-072 on D-06's architecture that the "
             "notes above record is answered by the owner's rows L3-OD1 and L3-OD3." % stamp) if two else
            ("Restated by %s for a 200 W stage; the store stays D-06's one pack (row L3-OD1 rejected), whose open problem "
             "is feasibility item FI-01." % stamp)), "records")
        array = "the kit's array of 400 Wp at STC (%s)" % rid
    else:
        wp, ia, ev = a["extra"].get("array-wp"), a["extra"].get("entry-a"), a["extra"].get("evidence")
        if not (wp and ia and ev):
            E.refuse("keep needs --array-wp, --entry-a and --evidence: the array REQ-016's 100 W window needs for the "
                     "chosen lid and its entry current, from the checked energy basis (the 1600 Wp of DECISION-OPTIONS.md "
                     "is for 4S18P, not for the lids offered)")
        et = C.evidence_path(a, ev)          # on the tree: the filed basis only (CHECK-2 of L3-R2, minor 6)
        for x, unit in ((wp, "Wp"), (ia, "A")):
            if not C.exact_token(et, x, unit): E.refuse("%s does not carry '%s %s' as a figure of its own" % (ev, x, unit))
        ruling = ("Row L3-OD3 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md decided: REQ-016's 100 W window is kept; the "
                  "kit's array is %s Wp at STC in parallel, of panels inside the window's 25 V at their coldest, sized for "
                  "the lid of row L3-OD2 by the energy basis (%s), and the entry carries a rating of %s A or more." % (wp, ev, ia))
        raw, rid = C.add_ruling(raw, d, ROW, op, "The solar input: REQ-016's 100 W window kept (row L3-OD3)",
                                ruling + STOW + COMPLY, a["words"], a["date"])
        old_fuse = ("and the input fuse F2 and connector J_SOLAR are rated 10 A, above the 5.68 A the window's 100 W draws "
                    "at 17.6 V.")
        new_fuse = ("and the input fuse F2, the connector J_SOLAR, the wall's solar pair and the array's lead are rated %s A "
                    "or more, the array's entry current (%s), F2 with an interrupting rating at or above the kit-side "
                    "prospective fault current." % (ia, rid))
        raw = E.replace_entry(raw, "REQ-016", lambda b: E.append_folded(C.add_ruling_ref(
            C.replace_in_field(b, "acceptance", old_fuse, new_fuse), rid), "history",
            "The fuse and connector clause restated by %s (row L3-OD3, %s) for the kit's %s Wp array; it read '%s'"
            % (rid, a["date"], wp, old_fuse), after="source_check"), "records")
        array = "the kit's array of %s Wp at STC in parallel (%s)" % (wp, rid)
    if O1.ARRAY in " ".join(str(next(r for r in d["records"] if r["id"] == "REQ-072")["acceptance"]).split()):
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(C.replace_in_field(b, "acceptance", O1.ARRAY, array),
                                                                         rid), "records")
    else:                                    # row L3-OD1 rejected: REQ-072 keeps its text and gains the array as a note
        raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes",
            "M1's array under row L3-OD3 (%s, %s): %s." % (rid, a["date"], array)), rid), "records")
    cand = None if op == "2s2p" else (
        "INCONCLUSIVE: the interface derivations for %s are owed; the checked feasibility record derives 2S2P only "
        "(v2/docs/records/l3feas/L3-FEASIBILITY.md section 3)" % ("1S4P" if op == "1s4p" else "the kept 100 W window's array"))
    raw, fid = C.feasibility_item(raw, "FI-06", [rid, "D-26"], candidate=cand)
    exp = {("owner_rulings", rid, "added"), ("records", "REQ-016", "changed"), ("records", "REQ-072", "changed"),
           ("records", fid, "added")}
    raw, _ = C.close_m02_if_done(raw, rid)
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_3", build, ("2s2p", "1s4p", "keep"), sys.argv[1:]))
