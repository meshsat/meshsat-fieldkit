#!/usr/bin/env python3
"""L3-R02 of the independent review the owner relayed on 1 October 2026 (MESHSAT-1357; v2/docs/records/l3am/): REQ-042's
acceptance, corrected under the owner's relayed review instruction.

REQ-042's acceptance ended "the hydrogen half of the battery-bay sensing is met once S-49 names its part", so a component
selection could stand in for the required detection and shutdown, and its VOC half gave no repeatable stimulus and no
bounded way to set its level. The correction keeps REQ-042's statement, scope, verification method and phases, and
writes a controlled end-to-end verification specification: channel by channel, the stimulus and the basis of its
threshold, the environmental and power states, the timing's start point, the alarm, both protection FETs opened, and the
pack held open until service. It chooses no number a held document does not support: the 10 s is the acceptance's own,
the gauge sequences are SLUUAQ3A's, and every alarm level, test gas and concentration and the states each channel covers
are allocated to layer 4 as a new open item, S-128, which REQ-042 now waits on beside S-49 and S-56. S-49 closes the
hydrogen part's selection only. Physical testing stays downstream (final phase PROTOTYPE).

It writes, and asserts nothing else changes: REQ-042's `acceptance`, a new `history` field and `waits_on` (S-128
added); S-49's `title`; the open item S-128; in l3r2.yaml an `impacts` entry for REQ-042 (a changed record needs one)
and `open_items_layer` rows for S-128 (layer 4) and S-49 (its why). A second run is refused. No dash character is written.

Usage: python3 v2/docs/records/l3am/apply_l3am_r02.py [--check]"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l3amlib as L  # noqa: E402

STATEMENT = "Water on the case floor, and hydrogen or VOC in the battery bay, raise an alarm and shut the pack down."
OLD_TAIL = "the hydrogen half of the battery-bay sensing is met once S-49 names its part."
ACCEPTANCE = (
    "End to end, channel by channel: water on the case floor, hydrogen in the battery bay and VOC in the battery bay each "
    "pass only on their own test. Naming or fitting a sensing part closes that part's selection (S-49 for hydrogen), never "
    "this acceptance, and a sensor that is fitted but does not drive the shutdown fails. Stimulus and threshold basis: "
    "water on the case floor until it bridges the case-floor electrodes; for VOC and for hydrogen, a test gas of stated "
    "concentration, traceable to a reference instrument or a calibration gas mixture, delivered into the closed battery "
    "bay, once at the channel's alarm level and once at a concentration below it that must raise nothing. The VOC "
    "channel's alarm level is set at bring-up from the SGP41's own clean-air baseline as its datasheet defines the VOC "
    "index; the hydrogen channel's comes from the pack's venting hazard and the chosen part's documents. Each level, each "
    "test gas and concentration and the states each channel covers are derived with their sources at layer 4 (S-128), the "
    "hydrogen part is picked at layer 6 (S-49) and the procedure is written into TEST-PLAN.md at layer 9; a level no held "
    "document supports is not used. States: the pack alone and with an input present, with the compute modules and the "
    "panel controller running and with them off or in reset (SC-41), across the in-use envelope of OPERATING-ENVELOPE.md "
    "section 4; a state outside a sensing part's published range is reported as not covered by that channel, never "
    "assumed. Timing and response: from the moment the stimulus reaches the alarm level at the sensor (the reference "
    "reading, or the electrodes bridged), MASTER WARN is raised and the sensor controller commands the pack gauge over "
    "J_SMB to open both protection FETs within 10 s, whether or not an input is present (the gauge's SHUTDOWN with no "
    "input, its EMERGENCY SHUTDOWN through the Manual FET Control sequence with one, SLUUAQ3A 5.4.2 and 5.4.4.2), and both "
    "FETs read open at the pack. Persistence: the pack staying open until service, with the stimulus removed and any input "
    "applied or removed, restored only by the service procedure (CONOPS section 4d).")
HISTORY = (
    "Corrected on 1 October 2026 under the owner's relayed instruction on the independent review's finding L3-R02 "
    "(v2/docs/records/l3am/REVIEW-AS-RECEIVED.md, v2/docs/records/l3am/apply_l3am_r02.py): the acceptance read \"the "
    "hydrogen half of the battery-bay sensing is met once S-49 names its part\", a component selection standing in for "
    "the detection and shutdown, and gave its VOC half no repeatable stimulus or bounded way to set its level. The "
    "statement, its scope and its verification method and phases are unchanged; S-49 now closes the part's selection "
    "only, the levels, stimuli and covered states are allocated to layer 4 (S-128), and the physical test stays "
    "downstream (PROTOTYPE).")
S49_TITLE = (
    "A battery-bay hydrogen sensing part, its selection only: the SGP41's datasheet specifies its VOC and NOx responses "
    "and names hydrogen only as a background gas, so the hydrogen half of the battery-bay sensing approved in appendix "
    "32.54 has no specified part (REQ-042). Pick a hydrogen-rated sensor from its maker's documents for board E's "
    "battery-bay header, or hold Sensirion's written statement of the SGP41's hydrogen response. Closing this item closes "
    "the part's selection and nothing of REQ-042's acceptance, which is the channel's end-to-end detection and shutdown "
    "test (corrected on 1 October 2026, finding L3-R02 of the independent review).")
S128_TITLE = (
    "REQ-042's alarm levels and test stimuli, derived with their sources before its test is written: the VOC channel's "
    "alarm level from the SGP41's clean-air baseline and VOC index, the hydrogen channel's from the pack's venting hazard "
    "and the documents of the part S-49 picks, each gas channel's test gas with its concentration at the level and the "
    "lower concentration that must raise nothing, the water stimulus at the case-floor electrodes, and the states of the "
    "in-use envelope each channel covers (a state outside a part's published range reported as not covered). Allocated "
    "to layer 4 by the layer 3 amendment of 1 October 2026 (finding L3-R02); the procedure then goes into TEST-PLAN.md at "
    "layer 9.")
IMPACT = ("  REQ-042: {why: \"acceptance corrected on 1 October 2026 (the independent review's L3-R02, the owner's relayed "
          "instruction): S-49 closes the hydrogen part's selection only; each channel verified end to end (the stimulus "
          "and its threshold basis, the power and environmental states, the timing from the alarm level, MASTER WARN, both "
          "FETs open, the pack open until service); statement and scope unchanged\", layers: {4: \"the alarm levels, test "
          "stimuli and covered states derived with their sources (S-128)\", 6: \"the hydrogen part (S-49), a selection "
          "only\", 9: \"TEST-PLAN's end-to-end procedure per channel; the physical test at prototype\"}}\n")
LAYER_S128 = "  S-128: {layer: 4, why: \"REQ-042's alarm levels, test stimuli and covered states, derived with their sources (L3-R02)\"}\n"
LAYER_S49_OLD = "  S-49: {layer: 6, why: \"a battery-bay hydrogen sensing part\"}"
LAYER_S49_NEW = ("  S-49: {layer: 6, why: \"a battery-bay hydrogen sensing part, its selection only (REQ-042's acceptance is "
                 "the end-to-end test, L3-R02)\"}")


def build():
    reg_old = open(L.REGISTRY, encoding="utf-8").read()
    data_old = open(L.DATA, encoding="utf-8").read()
    req = L.E.parse(reg_old)
    if any(x["id"] == "S-128" for x in req["open_items"] + req["closed_items"]): L.refuse("S-128 exists: this script has run")
    r42 = next(r for r in req["records"] if r["id"] == "REQ-042")
    if L.E.parse(data_old).get("impacts", {}).get("REQ-042"): L.refuse("l3r2.yaml's impacts names REQ-042: this script has run")
    if " ".join(str(r42["statement"]).split()) != STATEMENT: L.refuse("REQ-042's statement is not the one this correction keeps")
    if not " ".join(str(r42["acceptance"]).split()).endswith(OLD_TAIL): L.refuse("REQ-042's acceptance does not end as the review read it")
    for t, w in ((ACCEPTANCE, "REQ-042's acceptance"), (HISTORY, "REQ-042's history"), (S49_TITLE, "S-49's title"),
                 (S128_TITLE, "S-128's title"), (IMPACT + LAYER_S128 + LAYER_S49_NEW, "l3r2.yaml's rows")):
        L.screen(t, w)
    if "TBD" in ACCEPTANCE: L.refuse("the acceptance would read TBD")

    def f(block):
        b = L.E.set_folded(block, "acceptance", ACCEPTANCE)
        b = L.E.set_folded(b, "history", HISTORY, after="notes")
        items = L.E.flow_items(b, "waits_on")
        if items != ["S-49", "S-56"]: L.refuse("REQ-042 waits on %s, not S-49 and S-56" % items)
        return L.E.set_flow(b, "waits_on", items + ["S-128"])
    reg_new = L.E.replace_entry(reg_old, "REQ-042", f, "records")
    reg_new = L.E.replace_entry(reg_new, "S-49", lambda b: L.E.set_folded(b, "title", S49_TITLE), "open_items")
    reg_new = L.E.insert_at_section_end(reg_new, "open_items", "  - id: S-128\n    class: SESSION\n    status: OPEN\n    title: >-\n"
                                        + L.E.fold(S128_TITLE, 6))
    a, b = L.only_fields_changed(reg_old, reg_new, {("records", "REQ-042"): ["acceptance", "history", "waits_on"],
                                                    ("open_items", "S-49"): ["title"], ("open_items", "S-128"): "added"})
    b42 = next(r for r in b["records"] if r["id"] == "REQ-042")
    if b42["statement"] != r42["statement"]: L.refuse("REQ-042's statement moved")
    data_new = L.insert_before_line(data_old, "  REQ-016:", IMPACT, "l3r2.yaml impacts")
    data_new = L.once(data_new, LAYER_S49_OLD + "\n", LAYER_S49_NEW + "\n" + LAYER_S128, "open_items_layer S-49")
    x, y = L.only_keys_changed(data_old, data_new, {"impacts": "changed", "open_items_layer": "changed"})
    if set(y["impacts"]) - set(x["impacts"]) != {"REQ-042"} or any(x["impacts"][k] != y["impacts"][k] for k in x["impacts"]):
        L.refuse("impacts changed beyond REQ-042's entry")
    ch = {k for k in set(x["open_items_layer"]) | set(y["open_items_layer"]) if x["open_items_layer"].get(k) != y["open_items_layer"].get(k)}
    if ch != {"S-49", "S-128"}: L.refuse("open_items_layer changed on %s" % sorted(ch))
    return (reg_old, reg_new), (data_old, data_new)


def main(argv):
    try:
        r, d = build()
        L.validate_registry(r[1])
    except L.Refused as e:
        print("apply_l3am_r02: REFUSED: %s" % e); return 2
    print("apply_l3am_r02: REQ-042's acceptance, history and waits_on; S-49's title; S-128 added; l3r2.yaml's impacts and "
          "open_items_layer%s" % (" (check only, nothing written)" if "--check" in argv else ""))
    if "--check" in argv: return 0
    L.write(L.REGISTRY, *r)
    L.write(L.DATA, *d)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
