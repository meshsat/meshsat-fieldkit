#!/usr/bin/env python3
"""Every open item of the requirements registry either has a record waiting on it or carries a justified disposition
(MESHSAT-1357, 28 September 2026: the reassessment of handover H3, correction 2, and the owner's review of the restart
plan, point 5). At the set 6 integration 31 open items were in no record's `waits_on` (30 before apply_con010_redecide.py
linked S-92). This script, run by the registry's writer, gives each one of the two:

  a LINK: `waits_on: [item]` added to the record(s) whose verdict the item can move (each read from the item's text and
  the record's statement; the record's evidence_result is left as it is, the link says only that the item bears on it);
  a DISPOSITION: `disposition: <kind>` and `disposition_why` on the item, for an item that changes no record's verdict
  (a process, tooling, procurement, firmware, layout-stage or hold-tracking item, or a circuit or declaration item that
  no record judges by rule, which its generator owner applies in the circuit round).

It changes no statement, acceptance, status or evidence_result, re-parses the file, asserts that only these fields
changed, and refuses a second run. rules_lib.validate_requirements refuses an open item with neither from this commit on.
Run from the repository root before rules_status: python3 <this file>."""
import os, re, subprocess, sys, textwrap

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")

LINKS = {
    "S-13": ["CON-025"],                 # the eSIM build's order code: CON-025 protects the SIM interfaces of that module
    "S-47": ["REQ-016"],                 # board E's LT8705A solar stage: R5's place in the current path
    "S-56": ["REQ-042", "REQ-052"],      # the battery-bay SGP41's rating against the inside air of the reduced mode
    "S-60": ["REQ-017"],                 # the 54 V PoE rail's INA226 over its absolute maximum
    "S-62": ["REQ-041", "REQ-043"],      # the Geiger pulse input and the fan switches on board E
    "S-63": ["FEA-007"],                 # the QMX lid tray is a part of the case set FEA-007 judges
    "S-66": ["REQ-045"],                 # the pre-charge resistor's pulse rating is a protective element's sizing
    "S-69": ["FEA-004"],                 # VBAT's declared currents against its loads: the all-transmit bound
    "S-71": ["REQ-039"],                 # the LG290P's antenna bias against the maker's reference
    "S-72": ["REQ-039"],                 # the LG290P's V_BCKP protection
    "S-73": ["FEA-006"],                 # the TPS23861's VPWR bypass and DEC-001's seat
    "S-74": ["REQ-018", "REQ-045"],      # the dock's VIN_RAW pins and E5's targets are stages of the pack path
    "S-75": ["REQ-018"],                 # the dock's ground return shared between two contact families
    "S-84": ["REQ-004", "FEA-003"],      # PI_KILL held by a powered module: the failover fabric
    "S-87": ["FEA-002"],                 # FEA-002's own statement is stale
    "S-88": ["REQ-015", "REQ-017", "REQ-029", "CON-018"],            # the records TRN-001 on board A satisfies
    "S-89": ["REQ-022", "REQ-024", "REQ-026", "REQ-028", "REQ-064"],  # the records REL-001 satisfies
}
DISPOSITIONS = {
    "L-01": ("PROCUREMENT", "A fabrication quote taken before an order (decision 43, D-09). It changes no record's "
             "evidence; the order set is gated by it, not a requirement's verdict."),
    "S-23": ("HOLD_TRACKED", "Board A's decision-31 hold lives in tools/pcb_board_holds.yaml and gates layout entry "
             "through rules_status.layout_entry; the records TRN-001 on board A satisfies wait on S-88, which the "
             "hold's review closes. This item tracks the hold's lifting condition C-A31, not a verdict."),
    "S-61": ("CIRCUIT_ITEM", "A board D circuit item (a current limit on the hub port J_USB3 that the monitor's touch USB "
             "takes, SC-63) that no registry record judges by rule. Board D's generator owner applies it in the circuit "
             "round; PWR-001 on D reads the result then."),
    "S-65": ("CIRCUIT_ITEM", "Board A's +3V3 clamp D3 above the rail's parts' absolute maximum is an internal-rail "
             "protection finding for board A's generator owner. No record's acceptance names the rail's clamp "
             "coordination, and decision 31's review covers exposed conductors, not internal rails. The circuit round "
             "applies it and TRN-001 and PWR-001 on A are re-taken then."),
    "S-67": ("DECLARATION", "Board A's intent file declares its switching nodes at VBAT's nominal and not its working "
             "maximum. The figure feeds the spacing and derating instruments, not a record's acceptance directly; board "
             "A's generator owner corrects the declaration in the circuit round and those instruments re-read."),
    "S-68": ("LAYOUT_STAGE", "A netclass pattern list of board A's KiCad project, applied when the layout is drawn. No "
             "schematic-phase record rests on it."),
    "S-70": ("FIRMWARE", "A panel-firmware duty (read EMCON_EF_FLT, log the overvoltage, treat the PA and HF rails as "
             "unavailable) owed to HW-FW-CONTRACT.md and PANEL.md. The hardware record REQ-030 reads its EMCON evidence "
             "from the netlist; the duty changes no hardware verdict."),
    "S-81": ("PROCESS", "A wording defect of v2/docs/PRODUCT-BRIEF.md's open-items row (FEA-002's counts as EMCON.md "
             "states them), for the product brief's writer. CON-010 and FEA-002 carry their own counts."),
    "S-82": ("TOOLING", "The instrument rows RF-002's walk gained from stream w4b are in the tool and in the set 6 "
             "re-take's readings. The item asks for the instrument's own fixtures and record, not a circuit change; a "
             "defect those fixtures found would re-open through RF-002's re-take."),
    "S-83": ("DECLARATION", "Board C's +3V3 peak declaration against its child EPD_VCC is a declaration for board C's "
             "generator owner. PWR-001 on C reads the declaration and is re-taken when it changes; no record allocated "
             "to board C rests on PWR-001."),
    "S-86": ("PROCESS", "Documents that cite pcb_pack_protection.yaml by line numbers that moved (the battery packet). A "
             "citation refresh for the documents' writer, changing no reading."),
    "S-90": ("TOOLING", "The rule audit's absolute paths (rules_status.py) are a portability defect of the audit files; "
             "the audit is re-taken by rules_status in whichever tree judges the pages, so no verdict depends on it."),
    "S-91": ("PROCESS", "The answers owed to handover H3's two fresh checks (H3-RESPONSE.md). It lists corrections whose "
             "engineering halves are their own items (S-88, S-89 and S-92 among them) and changes no verdict itself."),
}


def refuse(msg):
    print("apply_waits_on_dispositions: REFUSED: %s" % msg); sys.exit(1)


def span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def main():
    t = open(P, encoding="utf-8").read()
    if "\n    disposition: " in t: refuse("the registry already carries a disposition (a second run)")
    before = yaml.safe_load(t)
    recs = {r["id"]: r for r in before["records"]}
    items = {i["id"]: i for i in before["open_items"]}
    waited = {x for r in before["records"] for x in (r.get("waits_on") or [])}
    unlinked = [i for i in items if i not in waited]
    planned = set(LINKS) | set(DISPOSITIONS)
    if set(unlinked) != planned:
        refuse("the unlinked open items are %s; this script plans for %s" % (sorted(unlinked), sorted(planned)))
    for iid, targets in LINKS.items():
        for rid in targets:
            if rid not in recs: refuse("%s: record %s does not exist" % (iid, rid))
            if recs[rid].get("status") == "SUPERSEDED": refuse("%s: %s is superseded" % (iid, rid))
    for iid, (kind, why) in DISPOSITIONS.items():
        if len(why) < 40 or "—" in why or "–" in why: refuse("%s: disposition_why too short or carries a dash" % iid)

    out = t
    # links: a record's waits_on gains the item (a new list before `status:` where the record has none)
    for iid, targets in LINKS.items():
        for rid in targets:
            i, j = span(out, rid); r = out[i:j]
            m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", r)
            if m:
                have = [x.strip() for x in m.group(1).split(",") if x.strip()]
                if iid in have: refuse("%s already waits on %s" % (rid, iid))
                r2 = r[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + [iid]) + r[m.end():]
            else:
                if "\n    status: " not in r: refuse("%s: no status line to anchor waits_on" % rid)
                r2 = r.replace("\n    status: ", "\n    waits_on: [%s]\n    status: " % iid, 1)
            out = out[:i] + r2 + out[j:]
    # dispositions: the item gains disposition and disposition_why after its status line
    for iid, (kind, why) in DISPOSITIONS.items():
        i, j = span(out, iid); it = out[i:j]
        body = "\n".join("      " + l for l in textwrap.wrap(why, 114, break_on_hyphens=False, break_long_words=False))
        it2 = it.replace("\n    status: OPEN\n", "\n    status: OPEN\n    disposition: %s\n    disposition_why: >-\n%s\n" % (kind, body), 1)
        if it2 == it: refuse("%s: status line not found" % iid)
        out = out[:i] + it2 + out[j:]
    if out == t: refuse("nothing changed")

    after = yaml.safe_load(out)
    ra, rb = recs, {r["id"]: r for r in after["records"]}
    if list(ra) != list(rb): refuse("the record list changed")
    linked_recs = {rid for ts in LINKS.values() for rid in ts}
    for k in ra:
        diff = {f for f in set(ra[k]) | set(rb[k]) if ra[k].get(f) != rb[k].get(f)}
        if k in linked_recs:
            if diff != {"waits_on"}: refuse("%s: fields changed %s" % (k, diff))
            want = list(ra[k].get("waits_on") or []) + [i for i, ts in LINKS.items() if k in ts]
            if rb[k]["waits_on"] != want: refuse("%s: waits_on is %s, expected %s" % (k, rb[k]["waits_on"], want))
        elif diff: refuse("record %s changed: %s" % (k, diff))
    oa, ob = items, {i["id"]: i for i in after["open_items"]}
    if list(oa) != list(ob): refuse("the open item list changed")
    for k in oa:
        diff = {f for f in set(oa[k]) | set(ob[k]) if oa[k].get(f) != ob[k].get(f)}
        if k in DISPOSITIONS:
            if diff != {"disposition", "disposition_why"}: refuse("%s: fields changed %s" % (k, diff))
            if (ob[k]["disposition"], ob[k]["disposition_why"]) != DISPOSITIONS[k]: refuse("%s did not round-trip" % k)
        elif diff: refuse("open item %s changed: %s" % (k, diff))
    for sec in before:
        if sec not in ("records", "open_items") and before[sec] != after[sec]: refuse("section %s changed" % sec)
    waited2 = {x for r in after["records"] for x in (r.get("waits_on") or [])}
    left = [i for i in ob if i not in waited2 and not ob[i].get("disposition")]
    if left: refuse("still unlinked and undisposed: %s" % left)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != after: refuse("the file written does not re-parse to what was checked")
    print("apply_waits_on_dispositions: %d items linked (%d record links), %d items disposed; every open item now has a "
          "record waiting on it or a disposition" % (len(LINKS), sum(len(v) for v in LINKS.values()), len(DISPOSITIONS)))
    for iid, ts in sorted(LINKS.items()): print("  link %s -> %s" % (iid, ", ".join(ts)))
    for iid, (k, _) in sorted(DISPOSITIONS.items()): print("  disposition %s: %s" % (iid, k))
    return 0


if __name__ == "__main__":
    sys.exit(main())
