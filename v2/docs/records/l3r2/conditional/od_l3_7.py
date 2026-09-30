#!/usr/bin/env python3
"""Row L3-OD7 of OWNER-DECISIONS-L3.md: M1's runtime and its store, with HF and the tablet kept. PREPARED, NOT APPLIED.
No prerequisite; answered before rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6, whose scripts refuse until it is (D-27,
cond.runtime_first). HELD by the owner's addendum (D-27) until stream l3batt's runtime comparison is filed with its
accepted check (l3r2.yaml `runtime_comparison`, filed: fnd/l3batt 83577a13, CHECK-2); every figure it writes is row
L3-OD7's table, verified against the filed runtime.out by exact keys before anything is written (cond.runtime_figures).

D-27, the owner: "Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment
conditions." As relayed: "He also said to preserve HF and the tablet functionality."

  --option 72-required               Option B: 72 hours required, as REQ-072 states it; the figure becomes the owner's in
                                     place of the session's SC-21 (REQ-072's statement names the ruling)
  --option 48-required-72-desired    Option A: 48 hours required, 72 hours desired: REQ-072's statement and acceptance
                                     restated to 48 hours, the 72 hours a design objective beside it
  --hf available|listening           HF during M1: powered, not receiving (the approved profile), or the receiver on
                                     (1.14 W more), written into REQ-072's load
  --external authorise-vbat|authorise-dc-entry|no
                                     an external battery arrangement joined at VBAT (reopens D-06) or through the DC
                                     entry (revisits D-20), recorded as feasibility item FI-07 with its size for the
                                     runtime and load chosen; or none: M1 recorded as not met with HF and the tablet kept,
                                     REQ-072 reading FAIL (D-20), feasibility item FI-08, M-02 carrying the answer
  --tablet-charging no|yes           the tablet charged from the USB-C outlet through M1: unquantified until a tablet
                                     model is named (SC-45), feasibility item FI-09

Usage: python3 od_l3_7.py --option <option> --hf <hf> --external <external> --tablet-charging <yes|no>
       --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cond as C  # noqa: E402

E = C.E
ROW = "L3-OD7"
OPTIONS = ("72-required", "48-required-72-desired")
PAGE = "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md"
OLD_ST = "the pack plus the solar input keep the kit running in PS-IDLE-SPEC for M1's 72 hours (SC-21)"
OLD_ACC = {"load": "the PS-IDLE-SPEC load of POWER-THERMAL.md section 4,", "store": "the aged pack of REQ-014",
           "desk": "ends the 72 hours above the graceful shutdown threshold",
           "proto": "the kit runs PS-IDLE-SPEC for 72 hours from a full pack"}
RUNTIME = {"72-required": "M1's runtime is 72 hours required (Option B), as REQ-072 states it; the figure is the owner's own "
                          "setting in place of the session's SC-21, which D-20 had preserved with M1's specified duration",
           "48-required-72-desired": "M1's runtime is 48 hours required, with 72 hours desired (Option A); REQ-072 is restated "
                                     "to 48 hours"}
HF = {"available": "HF is available during M1, powered and not receiving (the approved profile)",
      "listening": "HF is listening during M1, the QMX receiver on (1.14 W more than PS-IDLE-SPEC)"}
EXT = {"authorise-vbat": "an external battery arrangement is authorised, a separately protected external pack joined at "
                         "VBAT through a new wall connector, which reopens D-06",
       "authorise-dc-entry": "an external battery arrangement is authorised, joined through the 9 to 36 V DC entry, which "
                             "revisits D-20's 'requiring it overnight is not an acceptable substitute'",
       "no": "no external battery arrangement is authorised: M1 is recorded as not met with HF and the tablet kept, "
             "REQ-072 reading FAIL (D-20: unmet criteria stay visible)"}
TAB = {"no": "the tablet is not charged during M1 (the approved profile)",
       "yes": "the tablet is charged from the USB-C outlet during M1, an allowance unquantified until a tablet model is "
              "named (SC-45)"}


def sub(a, key):
    v = a["extra"].get(key)
    if v not in C.RUNTIME_SUB[key]:
        E.refuse("--%s must be one of %s: the owner's sub-choice on row L3-OD7" % (key, ", ".join(C.RUNTIME_SUB[key])))
    return v


def need(t, hours, hf):
    """The addition the both-kept store needs, as row L3-OD7's table gives it for the runtime and load chosen."""
    rows = {r["case"]: r for r in t["rows"] if r["hours"] == hours}
    if hf == "listening":
        return ("+%s Wh usable at NOM and +%s at WE (TYP, the receiver on)" % (rows["NOM"]["listening_wh"], rows["WE"]["listening_wh"]))
    return ("+%s Wh usable at NOM, +%s at WE and +%s at NOM at the 0.90 bracket (TYP), +%s to +%s with WAB"
            % (rows["NOM"]["typ_wh"], rows["WE"]["typ_wh"], rows["NOM90"]["typ_wh"],
               min((rows[c]["wab_wh"] for c in rows), key=float), max((rows[c]["wab_wh"] for c in rows), key=float)))


def build(a, raw, d):
    op = a["option"]
    hf, ext, tab = sub(a, "hf"), sub(a, "external"), sub(a, "tablet-charging")
    C.require(d, ROW, [])
    C.hold(a, ROW)
    t = C.runtime_figures()
    recs = {r["id"]: r for r in d["records"]}
    sc = next((c for c in d.get("session_choices") or [] if c["id"] == "SC-21"), None)
    if sc is None or "72 hours" not in " ".join(str(sc.get("taken")).split()):
        E.refuse("SC-21 does not take M1's 72 hours: the provenance this row states is not the registry's")
    st = " ".join(recs["REQ-072"]["statement"].split())
    if st.count(OLD_ST) != 1: E.refuse("REQ-072's statement does not carry %r once" % OLD_ST)
    acc = " ".join(recs["REQ-072"]["acceptance"].split())
    for o in OLD_ACC.values():
        if acc.count(o) != 1: E.refuse("REQ-072's acceptance does not carry %r once" % o)
    ruling = ("Row L3-OD7 of %s decided: %s; %s; %s; %s. HF and the tablet are kept (D-27)." % (
        PAGE, RUNTIME[op], HF[hf], EXT[ext], TAB[tab]))
    raw, rid = C.add_ruling(raw, d, ROW, op, "M1's runtime answered, %s, HF %s, external %s, tablet charging %s (row L3-OD7)"
                            % (op, hf, ext, tab), ruling, a["words"], a["date"],
                            extra={C.RUNTIME_FIELDS["hf"]: hf, C.RUNTIME_FIELDS["external"]: '"%s"' % ext,
                                   C.RUNTIME_FIELDS["tablet-charging"]: '"%s"' % tab})
    stamp = "%s (row L3-OD7, %s)" % (rid, a["date"])
    P = C.runtime_phrases(rid, op, hf, ext, tab)
    new_st = st.replace(OLD_ST, "the pack%s plus the solar input keep the kit running in PS-IDLE-SPEC%s for %s" % (
        P["store"], P["load"], P["duration"]))
    new_acc = acc
    if P["load"]: new_acc = new_acc.replace(OLD_ACC["load"], OLD_ACC["load"][:-1] + P["load"])
    if P["store"]: new_acc = new_acc.replace(OLD_ACC["store"], OLD_ACC["store"] + P["store"][:-1])
    if P["hours"] != "72": new_acc = new_acc.replace(OLD_ACC["desk"], OLD_ACC["desk"].replace("72", P["hours"]))
    if P["load"] or P["hours"] != "72":
        new_acc = new_acc.replace(OLD_ACC["proto"], "the kit runs PS-IDLE-SPEC%s for %s hours from a full pack" % (P["load"], P["hours"]))
    raw = C.restate(raw, "REQ-072", stamp, statement=new_st, acceptance=(new_acc if new_acc != acc else None))
    notes = ["Row L3-OD7 (%s, %s), on the runtime comparison of stream l3batt (fnd/l3batt 83577a13, CHECK-2): %s." % (
        rid, a["date"], RUNTIME[op])]
    if op.startswith("48"):
        notes.append("The 72 hours desired are a design objective beside the requirement, not its pass line.")
    notes.append("With HF and the tablet kept the studied store, Option A(i)'s base 4S6P and lid 4S9P (%s Wh usable aged at +20 C), "
                 "stops the kit at 05 UTC of the first night (hour %s from a 06 UTC start, hour %s from an 18 UTC start) in "
                 "every case and carries %s of 864 past September windows; for %s hours it needs %s over the both-kept lid "
                 "(runtime.out 2 to 4)." % (t["store"]["usable_20"], t["rows"][0]["stops"].split("/")[0],
                                            t["rows"][0]["stops"].split("/")[1], t["rows"][0]["coverage"], P["hours"],
                                            need(t, P["hours"], hf)))
    if hf == "listening": notes.append("HF listening: the QMX receiver's 1.14 W is added to PS-IDLE-SPEC, which powers only its USB and HDMI 5 V.")
    notes.append({"authorise-vbat": "The external battery arrangement is joined at VBAT through a new wall connector, which reopens D-06 (EQ-13 route (d)); feasibility item FI-07 records its size and its open engineering.",
                  "authorise-dc-entry": "The external battery arrangement is joined through the 9 to 36 V DC entry, which revisits D-20's 'requiring it overnight is not an acceptable substitute' (EQ-13 route (b)); feasibility item FI-07 records its size and its open engineering.",
                  "no": "No external battery arrangement: M1 is recorded as not met with HF and the tablet kept and this record keeps reading FAIL (D-20); feasibility item FI-08; M-02 carries the answer."}[ext])
    if tab == "yes": notes.append("The tablet is charged from the USB-C outlet through M1: an allowance unquantified until a tablet model is named (SC-45); feasibility item FI-09.")
    note = " ".join(notes)
    E.screen(note, "REQ-072's note")
    raw = E.replace_entry(raw, "REQ-072", lambda b: C.add_ruling_ref(E.append_folded(b, "notes", note), rid))
    exp = {("owner_rulings", rid, "added"), ("records", "REQ-072", "changed")}
    if ext == "no":
        raw, fid = C.feasibility_item(raw, "FI-08", [rid, "D-20", "D-27"], candidate=(
            "FAIL: at %s hours with HF %s the studied both-kept store (%s Wh usable) stops the kit at 05 UTC of the first "
            "night in every case, the corrected path included, and carries %s of 864 past September windows; no in-case "
            "cell choice adds energy (SHORTLIST.md 3)" % (P["hours"], hf, t["store"]["usable_20"], t["rows"][0]["coverage"])))
        raw = E.replace_entry(raw, "M-02", lambda b: E.append_folded(b, "title",
            "The owner answered row L3-OD7 on %s (%s): no external battery arrangement; M1 is recorded as not met with HF "
            "and the tablet kept (%s)." % (a["date"], rid, fid)), "open_items")
        exp |= {("records", fid, "added"), ("open_items", "M-02", "changed")}
    else:
        raw, fid = C.feasibility_item(raw, "FI-07", [rid, "D-27"], candidate=(
            "CONDITIONAL: the studied both-kept store (%s Wh usable) stops the kit at 05 UTC of the first night in every "
            "case; at %s hours with HF %s it is met on the model with an external store of at least %s over the both-kept "
            "lid, on the corrected path (runtime.out 3), joined %s" % (
                t["store"]["usable_20"], P["hours"], hf, need(t, P["hours"], hf),
                "at VBAT (reopens D-06)" if ext == "authorise-vbat" else "through the DC entry (revisits D-20)")))
        exp |= {("records", fid, "added")}
    if tab == "yes":
        raw, fid9 = C.feasibility_item(raw, "FI-09", [rid, "D-27"])
        exp |= {("records", fid9, "added")}
    return raw, exp


if __name__ == "__main__":
    sys.exit(C.run("od_l3_7", build, OPTIONS, sys.argv[1:]))
