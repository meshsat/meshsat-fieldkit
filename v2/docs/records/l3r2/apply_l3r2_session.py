#!/usr/bin/env python3
"""The session's own closures of layer 3's second issue (L3-R2), applied to the requirements registry (MESHSAT-1357,
30 September 2026, branch fnd/l3r2; second round, after the independent check CHECK-1 and the owner's review of the
draft table).

The owner's instructions of 30 September 2026 (v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md) ask layer 3 to
be finished for the current target configuration, and hold rows L3-OD1, L3-OD2 and L3-OD4 until a corrected, independently
checked energy comparison arrives. What the session may close without an owner judgement is closed here, in one run,
each edit found by its id and its own text (never by a line number):

  1. D-21 and D-22, the owner's instruction and his review of the draft table, added to owner_rulings after the last
     ruling, each quoting the filed page (the page is read and every quoted sentence asserted before it is written).
  2. S-114 closed by commit 1b9f543c: the reconciliation it asks for is filed and REQ-072 was re-read on it (both
     asserted); its closing evidence states that the two-pack figures are the model's at its 20.7 V bus. REQ-016 and
     REQ-072 stop waiting on it.
  3. A new open item (the next free S number, S-127 on integration set 15) carries the energy basis every M1 figure
     waits on: the charge bus's supply range at U3's input under load and temperature, the current limits and losses
     with their brackets, and the cases named by their exact weather and operating assumptions, independently checked.
     REQ-072 waits on it, and gains one evidence entry that qualifies the two-pack figures its s119 entry quotes (the
     model's 20.7 V bus against the bus's stated band; the files asserted and bound).
  4. M-02's title gains the rows it now carries and D-22's hold; S-53's title gains Option A(i)'s state (the three
     candidate branches of board E's 200 W stage are resolved as local or remote refs and asserted not merged).
  5. CFL-006 re-read by read_cfl006.py (every fact asserted, every binding equal to the files read): one evidence entry
     and one note sentence; its FAIL stands on the enclosure, a layer 7 item (S-27).
  6. CFL-002's note that REQ-042 carries a TBD corrected (REQ-042's acceptance is asserted to carry none).
  7. Seven acceptances made measurable from the record's own statement, with no limit added or removed and the old text
     kept in `history`: REQ-008, REQ-012, REQ-029, REQ-054 (its 27 dBm allowance on 869.4 to 869.65 MHz kept), REQ-057,
     REQ-068 and CHO-003.
  8. A header paragraph stating the L3-R2 changes, above the paragraph on stable ids.

Nothing that awaits an owner decision is changed: no statement, acceptance, applicability, allocation, verification or
release effect of REQ-011, REQ-014, REQ-016, REQ-051, REQ-072, REQ-075, CFL-017 or any record OWNER-DECISIONS-L3
names; their restatements are the conditional scripts of conditional/, not applied.

Refuses a second run (D-21 present), any anchor that does not match, any text with a dash character or a claim word of
claims_check.py, and any result that does not validate (rules_lib.validate_requirements: 0 errors) or that changes an
entry this list does not name.

Usage: python3 apply_l3r2_session.py [--check] [--registry PATH]
  --check     build and validate in memory, print what would change, write nothing
  --registry  apply to a copy (the default is v2/ecad/tools/pcb_requirements.yaml)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3edit as E  # noqa: E402

S114_COMMIT = "1b9f543ce4695519ba3b5f41b503a07dc7d99124"
INSTR = "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md"
DATE = "30 September 2026"
MARK = "(layer 3's second issue, L3-R2, v2/docs/records/l3r2/apply_l3r2_session.py)"
BASIS_MARK = "(L3-R2; the owner's review of 30 September 2026, D-22) The energy basis of every M1 figure"

# ------------------------------------------------------------------------------------------------- 1. D-21, D-22
INSTR_QUOTES = [
    "finish Layer 3, Requirements for the current target configuration before advancing Layer 4",
    "For every requirement-changing proposal, record whether it is approved, rejected or awaiting a decision.",
    "Distinguish requirements from implementation choices that properly belong in later layers. Battery and solar remain "
    "mandatory. Preserve the approved 72-hour mission and approved functions unless I explicitly authorize a change. "
    "Recommendations are not approvals",
    "Layer 3 reaches 100% only when the target is unambiguous, requirement-changing owner decisions are resolved, "
    "contradictions and requirement-level TBDs are closed, and an independent check accepts the handover. Completed "
    "circuits and physical test results belong to later verification stages; do not make them prerequisites for "
    "completing the requirements document or mark planned tests as passed.",
    "The voltage is an engineering input, not an author's preference. Establish the applicable supply range under load "
    "and temperature. If 19.08 V is permitted, mission claims must account for it. Independently check how voltage, "
    "current limits and losses affect the energy calculation.",
    "Preserve your mission requirements. Narrower deployment angles, reduced functionality or different operating "
    "conditions must be proposed explicitly for your approval. They cannot become accepted requirements simply because "
    "they make this candidate pass.",
    "Define 'adverse.' A model based on a September average day does not establish performance across unspecified "
    "adverse weather. The corrected table must identify the exact weather and operating assumptions.",
    "Hold decisions 1, 2 and 4 until the corrected, independently checked comparison arrives. Battery and solar remain "
    "mandatory; moving equipment out of the lid must not silently remove its function from the kit.",
    "The next useful result is one consistent decision table and an updated requirements package.",
]
RULING = '''  - id: {rid}
    authority: OWNER
    ruled_on: "2026-09-30"
    title: "{title}"
    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{instr}"]
'''
D21_TITLE = "finish layer 3 for the current target configuration (the owner's instruction of 30 September 2026)"
D21_RULING = (
    "The owner's instruction of 30 September 2026, quoted in part in " + INSTR + " (its omissions are the quoting "
    "session's and this entry's, marked). In his words: \"finish Layer 3, Requirements for the current target "
    "configuration before advancing Layer 4 [...] For every requirement-changing proposal, record whether it is approved, "
    "rejected or awaiting a decision. [...] Distinguish requirements from implementation choices that properly belong in "
    "later layers. Battery and solar remain mandatory. Preserve the approved 72-hour mission and approved functions unless "
    "I explicitly authorize a change. Recommendations are not approvals [...] Layer 3 reaches 100% only when the target is "
    "unambiguous, requirement-changing owner decisions are resolved, contradictions and requirement-level TBDs are "
    "closed, and an independent check accepts the handover. Completed circuits and physical test results belong to later "
    "verification stages; do not make them prerequisites for completing the requirements document or mark planned tests "
    "as passed.\"")
D22_TITLE = "the owner's review of the draft layer 3 decision table (30 September 2026)"
D22_RULING = (
    "The owner's review of the draft decision table of layer 3's second issue, 30 September 2026, as quoted in " + INSTR +
    ". In his words: \"The voltage is an engineering input, not an author's preference. Establish the applicable supply "
    "range under load and temperature. If 19.08 V is permitted, mission claims must account for it. Independently check "
    "how voltage, current limits and losses affect the energy calculation.\" \"Preserve your mission requirements. "
    "Narrower deployment angles, reduced functionality or different operating conditions must be proposed explicitly for "
    "your approval. They cannot become accepted requirements simply because they make this candidate pass.\" \"Define "
    "'adverse.' A model based on a September average day does not establish performance across unspecified adverse "
    "weather. The corrected table must identify the exact weather and operating assumptions.\" \"Hold decisions 1, 2 and "
    "4 until the corrected, independently checked comparison arrives. Battery and solar remain mandatory; moving "
    "equipment out of the lid must not silently remove its function from the kit.\" \"The next useful result is one "
    "consistent decision table and an updated requirements package.\"")

# ------------------------------------------------------------------------------------------------------ 2. S-114
S114_EVIDENCE = (
    "The reconciliation this item asked for is filed: v2/docs/records/energy/ENERGY-RECONCILIATION.md sections 1 to 9, "
    "with its options sheet v2/docs/records/energy/DECISION-OPTIONS.md and v2/docs/records/energy/DECISION-PARAGRAPH.md, "
    "and the Option A(i) records under v2/docs/records/a1elec/, a1mech/, a1solar/ and a1int/. REQ-072 was re-read on it "
    "in two evidence entries, the second on the charger rows of stream s119 (v2/docs/records/s119/README.md) in the "
    "commit this item names, and reads FAIL on both; its statement and acceptance are not rewritten. Section 9 derives M1 "
    "from the requirement side: D-06's one 4S3P pack allows at most 9.1 W for M1 against PS-IDLE-SPEC's 42.8 W, which no "
    "bus voltage raises, and on the model's charge bus of 20.7 V (v2/docs/records/a1elec/energy_two_pack.py, V_BUS20) the "
    "architecture that meets the reference day is two packs with a 200 W solar stage, which the options sheet presents "
    "as its Option A. That 20.7 V is above the bus's nominal regulation of 20.000 V and its stated DC band of 19.080 to "
    "20.960 V (v2/docs/records/s120/vbus20_bound.out section 2): the two-pack figures are the model's most favourable "
    "bus, not the kit's across its supply range, which the energy basis of the open item this closure opens "
    "establishes (the owner's review of 30 September 2026, D-22). What remains is the owner's: the rows of "
    "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md that M-02 names. Closed by the author of L3-R2 on " + DATE +
    " under the owner's standing rule of 26 September 2026.")
S114_ASSERT = {
    "v2/docs/records/energy/ENERGY-RECONCILIATION.md": ["## 9. M1 from the requirement side",
                                                        "D-06's one 4S3P: 9.1 W, whatever the panel or window"],
    "v2/docs/records/energy/DECISION-OPTIONS.md": ["**A. Full mission (recommended).**"],
    "v2/docs/records/s119/README.md": ["U3B"],
}
BUS_ASSERT = {
    "v2/docs/records/s120/vbus20_bound.out": ["nominal 20.000 V", "19.080 to 20.960 V <- the DC band"],
    "v2/docs/records/a1elec/energy_two_pack.py": ["V_BUS20 = 20.7"],
}
REQ072_READS = ["v2/docs/records/energy/ENERGY-RECONCILIATION.md (stream energy, 28 September 2026",
                "v2/docs/records/s119/README.md (stream s119, S-119, 29 September 2026"]

# ------------------------------------------------------------------------------------------------ 3. the energy basis
BASIS_TITLE = (
    BASIS_MARK + ": board A's charge bus VBUS20 at U3's input across its supply range under load and temperature, from "
    "makers' pages (the regulated node, the loop's load regulation and the drop to U3's input), U3's input current limit "
    "with its bracket, the chargers' efficiencies with their brackets and the inductors' core loss, and each case the "
    "energy model runs named by its exact weather and operating assumptions in place of 'typical' and 'adverse'; then an "
    "independent check of how voltage, current limits and losses move the energy calculation. Stream l3plane writes it "
    "(v2/docs/records/l3plane/ENERGY-BASIS.md, on branch fnd/l3plane). Until it is filed and checked, rows L3-OD1, "
    "L3-OD2 and L3-OD4 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md are held (D-22), the L3 pages state no M1 energy "
    "figure as the design's, and REQ-072 reads FAIL as before. Closed when the basis and its check are filed and REQ-072 "
    "is re-read on them.")
REQ072_NOTE = (
    "v2/docs/records/a1elec/energy_two_pack.py and v2/docs/records/s120/vbus20_bound.out read on " + DATE + " (L3-R2, on "
    "the owner's review of that day, D-22): the Option A(i) figures of the entry above convert U3's input current limit "
    "into power at the model's V_BUS20 of 20.7 V, above the bus's nominal regulation of 20.000 V and its stated DC band of "
    "19.080 to 20.960 V; they are the model's most favourable bus, not the kit's across its supply range, which the "
    "energy basis of the open item that carries it establishes. This entry changes no result, statement or acceptance: "
    "the verdict stays FAIL.")

# ------------------------------------------------------------------------------------------------------ 4. M-02, S-53
M02_ASSERT = ["move to engineering Option A(i), within existing authorizations",
              "No purchases or requirement changes are authorized by this instruction"]
M02_ADD = (
    "Since the owner's instruction of 29 September 2026 (v2/docs/EXECUTION-PLAN.md, set 10's milestone: engineer "
    "Option A(i) within existing authorisations, with M1 and REQ-072 unchanged and no purchase or requirement change "
    "authorised), D-21 and D-22 of " + DATE + ", the decision this item carries is rows L3-OD1 to L3-OD4 of "
    "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md: Option A(i)'s two packs (routes (c) and (d) of EQ-13 together), where "
    "each approved lid function goes and whether it stays in the kit, the solar input's stage and array, and M1's "
    "deployment conditions. Rows L3-OD1, L3-OD2 and L3-OD4 are held by D-22 until the corrected, independently checked "
    "energy comparison is filed. Route (e), accepting that prototype 1 does not meet M1, is excluded by D-20 " + MARK + ".")
S53_ASSERT = {"v2/docs/records/a1elec/README.md": ["at least **5.57 A (115.4 W)** into U3"]}
S53_BRANCHES = ["fnd/e200c", "fnd/e200r", "fnd/e200r2"]
S53_ADD = (
    "Under Option A(i), which the owner has not adopted (OWNER-DECISIONS-L3 rows L3-OD1 and L3-OD3): board A's entry "
    "re-rate is drafted in v2/docs/records/a1elec/README.md and CHARGER.md (at least 5.57 A into U3 with its input limit "
    "at its minimum, on the model's 20.7 V bus), and board E's 200 W stage exists only on the candidate branches "
    "fnd/e200c, fnd/e200r and fnd/e200r2, not merged, gated by REQ-016's restatement; this item's judgement is made on the "
    "architecture the owner adopts and on the energy basis the owner's review of 30 September 2026 asks for " + MARK + ".")

# ------------------------------------------------------------------------------------------------------ 5. CFL-006
CFL006_NOTE = (
    "Layer 3 (L3-R2, " + DATE + "): the requirement-level question this conflict raised, which cell and which parallel "
    "count, is settled by D-06 in every requirement-level source the reading of that day names; what still fails is an "
    "enclosure design that does not exist yet (layer 7, S-27), so the FAIL is carried as a layer 7 item and does not "
    "hold layer 3. If the owner adopts row L3-OD1 of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md (two packs), the "
    "acceptance becomes per pack (v2/docs/records/l3r2/conditional/od_l3_1.py).")

# ------------------------------------------------------------------------------------------------------ 6. CFL-002
CFL002_ADD = ("Corrected on " + DATE + " " + MARK + ": REQ-042 carries no TBD since 27 September 2026; the hydrogen "
              "half of its battery-bay sensing is met once S-49 names its part.")

# ------------------------------------------------------------------------------------------------------ 7. acceptances
ACCEPT = {
    "REQ-008": (
        "Inspection with the kit unpowered: the e-paper page shows the kit's identity, battery and shore state, GPS fix, "
        "UTC, the last message, and bearer and slot health. Firmware review: the page is refreshed at most once in any "
        "60 s, the enrolment QR is drawn only while TEST is held after a UI request, and the QR's payload holds no key "
        "material. Prototype: after power is removed the page still shows every listed field."),
    "REQ-012": (
        "Netlist: a trace from board D's KEY line to the TX lamp's driver with no processor in the path, and the lamp "
        "test's own tie to the lamp. Bench, with the panel controller held in reset: the lamp is lit while KEY is "
        "asserted and dark when KEY is released. Bench, with the panel controller running: outside blackout the lamp's "
        "drive duty is never below 10 %, and the lamp test lights it."),
    "REQ-029": (
        "TEST-PLAN M7 on the powered kit, every bearer up, at IEC 61000-4-2 level 4 (8 kV contact, 15 kV air), applied "
        "at the plate, the toggles, the display bezel, every bulkhead shell, both headset jacks, the USB-C outlet, the "
        "Ethernet port and the pod lead: after every discharge no upset, no reset, no bearer lost, no secure-element key "
        "lost and no damage, and the functional check (TEST-PLAN section 4) passes at the end."),
    "REQ-054": (
        "Configuration review: meshtasticd's region, channel, transmit power and duty-cycle settings, with the antenna "
        "gain applied, give at most 14 dBm ERP on every configured channel outside 869.4 to 869.65 MHz, and at most 27 "
        "dBm ERP at a duty cycle of at most 10 % on a channel inside 869.4 to 869.65 MHz. Prototype: the conducted output "
        "measured at each configured channel, plus the antenna's gain, is at or under the limit of the band the channel "
        "is in, and the duty cycle measured on 869.4 to 869.65 MHz is at most 10 %."),
    "REQ-057": (
        "TEST-PLAN M6 on the prototype: each core transmitter (the RockBLOCK 9704, the RM520N-GL, the E22 LoRa module, the "
        "SA868 with its 30 W PA and the live WiFi link card) keyed in turn at full power with every receiver listening. "
        "It passes when, for every key-down, no receiver is damaged (each passes its part of the functional check "
        "afterwards), no EMCON, ZEROIZE or sensor is falsely triggered, and GNSS keeps its fix or regains it within 10 s "
        "of the key-up."),
    "REQ-068": (
        "TEST-PLAN M6 on the prototype: each transmitter outside prototype 1's core (the QMX HF unit, the LimeSDR's "
        "transmit path, the two E72 radios and the three compute modules' own WiFi and Bluetooth) keyed in turn at full "
        "power with every receiver listening. It passes when, for every key-down, no receiver is damaged (each passes its "
        "part of the functional check afterwards), no EMCON, ZEROIZE or sensor is falsely triggered, and GNSS keeps its "
        "fix or regains it within 10 s of the key-up."),
    "CHO-003": (
        "Inspection: in no public or shipped document is a vehicle surge level (IEC 61000-4-5, ISO 7637-2 or a military "
        "vehicle standard) claimed for the prototype's vehicle and shore entry (D-16), and the design record names the "
        "long-lead clamps by their part and pulse figure (SMCJ40A, 1500 W at 10/1000 us)."),
}
ACCEPT_OLD = {   # the text each acceptance must read before it is restated (asserted)
    "REQ-008": "Inspection of the page with the kit unpowered; firmware review of the refresh limit and the QR payload.",
    "REQ-012": "Netlist trace from D's KEY line to the lamp driver with no processor in the path; bench check with the "
               "panel controller in reset.",
    "REQ-029": "TEST-PLAN M7 on the powered kit, every bearer up, at the plate, toggles, display bezel, every bulkhead "
               "shell, both headset jacks, USB-C, Ethernet and the pod lead.",
    "REQ-054": "Conducted output and duty cycle measured at each configured channel with the antenna gain applied; "
               "configuration review of meshtasticd.",
    "REQ-057": "TEST-PLAN M6 on the prototype, for the core transmitters.",
    "REQ-068": "TEST-PLAN M6 on the prototype, for these transmitters.",
    "CHO-003": "n/a (describes the design): no vehicle surge standard is claimed for the prototype (D-16); an "
               "installation level would be a new owner ruling.",
}
# the statement facts each new acceptance is taken from (asserted in the record's own statement)
ACCEPT_FROM_STATEMENT = {
    "REQ-008": ["identity, battery and shore state, GPS fix, UTC, last message, bearer and slot health",
                "refreshes at most once a minute", "only while TEST is held after a UI request", "never carries key material"],
    "REQ-012": ["follows the VHF path's real KEY line in hardware", "never dimmed below 10 % duty except in blackout",
                "a lamp test lights it through its own tie"],
    "REQ-029": ["IEC 61000-4-2 level 4 (8 kV contact, 15 kV air)", "no upset, reset, lost bearer, lost secure-element key or damage"],
    "REQ-054": ["14 dBm ERP generally", "27 dBm ERP on 869.4 to 869.65 MHz at 10 % duty"],
    "REQ-057": ["damages no receiver", "falsely triggers no EMCON, ZEROIZE or sensor", "recovering it within 10 s"],
    "REQ-068": ["damage no receiver", "falsely trigger no EMCON, ZEROIZE or sensor", "recovering it within 10 s"],
    "CHO-003": ["SMCJ40A, 1500 W at 10/1000 us", "not constrained to an IEC 61000-4-5 level"],
}

HEADER = """#
# LAYER 3'S SECOND ISSUE, L3-R2 (30 September 2026, MESHSAT-1357, branch fnd/l3r2 on integration set 15's line). On the
# owner's instruction of that day and his review of the draft table (owner rulings D-21 and D-22,
# v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md) the session closed what needs no owner judgement, through
# v2/docs/records/l3r2/apply_l3r2_session.py: D-21 and D-22 recorded; S-114 closed (the reconciliation filed and REQ-072
# re-read on it) and the energy basis every M1 figure waits on opened as its own item, which REQ-072 waits on; M-02 and
# S-53 restated to the decisions they now wait on; CFL-006 re-read (its FAIL stands on the enclosure, a layer 7 item);
# CFL-002's stale TBD sentence corrected; and seven acceptances made measurable from their own statements (REQ-008,
# REQ-012, REQ-029, REQ-054, REQ-057, REQ-068, CHO-003), each keeping its old text in `history`. These acceptances are a
# change to the baseline of a54b793b and are judged by the independent check of L3-R2; baseline_state keeps naming the
# last reviewed baseline until that check accepts the issue. What awaits the owner (v2/docs/handover/layer3/
# OWNER-DECISIONS-L3.md) is not changed here: its restatements are prepared, not applied, under
# v2/docs/records/l3r2/conditional/. The consolidated specification is v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md,
# generated from this file.
"""


def resolve_branch(br):
    for ref in (br, "origin/" + br, "refs/remotes/origin/" + br):
        r = E.git("rev-parse", "--verify", "-q", ref + "^{commit}")
        if not r.returncode: return ref
    E.refuse("branch %s is in this repository neither as a local nor as an origin ref" % br)


def build(raw):
    d0 = E.parse(raw)
    if any(r["id"] == "D-21" for r in d0["owner_rulings"]): E.refuse("D-21 is already in the registry: this script has run")
    for t in (D21_RULING, D22_RULING, S114_EVIDENCE, BASIS_TITLE, REQ072_NOTE, M02_ADD, S53_ADD, CFL006_NOTE, CFL002_ADD,
              HEADER, D21_TITLE, D22_TITLE) + tuple(ACCEPT.values()):
        E.screen(t, "an added text")

    # 1. D-21 and D-22
    E.assert_in(INSTR, INSTR_QUOTES)
    last = d0["owner_rulings"][-1]["id"]
    text = (RULING.format(rid="D-21", title=D21_TITLE, ruling=E.fold(D21_RULING, 6), instr=INSTR) +
            RULING.format(rid="D-22", title=D22_TITLE, ruling=E.fold(D22_RULING, 6), instr=INSTR))
    raw = E.insert_after_entry(raw, last, text, "owner_rulings")

    # 2. S-114
    for rel, needles in S114_ASSERT.items(): E.assert_in(rel, needles)
    for rel, needles in BUS_ASSERT.items(): E.assert_in(rel, needles)
    r072 = next(r for r in d0["records"] if r["id"] == "REQ-072")
    for head in REQ072_READS:
        if not any(str(e).startswith(head) for e in r072.get("evidence") or []): E.refuse("REQ-072 carries no re-read %r" % head)
    if r072.get("evidence_result") != "FAIL": E.refuse("REQ-072 no longer reads FAIL")
    if E.git("merge-base", "--is-ancestor", S114_COMMIT, "HEAD").returncode: E.refuse("commit %s is not in this history" % S114_COMMIT[:8])
    it = next((x for x in d0["open_items"] if x["id"] == "S-114"), None)
    if it is None: E.refuse("S-114 is not an open item")
    raw, _old = E.remove_entry(raw, "S-114", "open_items")
    closed = ("  - id: S-114\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s"
              % (S114_COMMIT, E.fold(S114_EVIDENCE, 6), E.fold(it["title"], 6)))
    raw = E.insert_at_section_end(raw, "closed_items", closed)

    # 3. the energy basis, an open item REQ-072 waits on
    sid = E.next_id(d0, "S", ("open_items", "closed_items"))
    raw = E.insert_at_section_end(raw, "open_items",
                                  "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (sid, E.fold(BASIS_TITLE, 6)))
    for rid in ("REQ-016", "REQ-072"):
        def waits(b, rid=rid):
            w = E.flow_items(b, "waits_on")
            if "S-114" not in w: E.refuse("%s does not wait on S-114" % rid)
            w = [x for x in w if x != "S-114"]
            return E.set_flow(b, "waits_on", w + ([sid] if rid == "REQ-072" else []))
        raw = E.replace_entry(raw, rid, waits, "records")
    binds = ["%s@%s" % (p, E.sha16(os.path.join(E.TOP, p))) for p in BUS_ASSERT]
    def note072(b):
        b = E.add_list_entry(b, "evidence", REQ072_NOTE)
        items = [x.strip() for x in (E.field_text(b, "evidence_bound_to") or "").strip("[]").split(",") if x.strip()]
        lines, a, z = E._field_lines(b, "evidence_bound_to")
        cur = [l.strip()[2:].strip() for l in lines[a + 1:z]] if items == [] else items
        new = cur + ['"%s"' % x for x in binds if x not in cur and '"%s"' % x not in cur]
        return "\n".join(lines[:a] + ["    evidence_bound_to:"] + ["      - %s" % x for x in new] + lines[z:])
    raw = E.replace_entry(raw, "REQ-072", note072, "records")

    # 4. M-02 and S-53
    E.assert_in("v2/docs/EXECUTION-PLAN.md", M02_ASSERT)
    raw = E.replace_entry(raw, "M-02", lambda b: E.append_folded(b, "title", M02_ADD), "open_items")
    for rel, needles in S53_ASSERT.items(): E.assert_in(rel, needles)
    for br in S53_BRANCHES:
        ref = resolve_branch(br)
        if not E.git("merge-base", "--is-ancestor", ref, "HEAD").returncode: E.refuse("branch %s is merged into HEAD" % br)
    raw = E.replace_entry(raw, "S-53", lambda b: E.append_folded(b, "title", S53_ADD), "open_items")

    # 5. CFL-006
    import read_cfl006 as RC
    fs = RC.facts()
    bad = [f for f, ok, _ in fs if not ok]
    if bad: E.refuse("read_cfl006.py: facts %s do not hold" % ", ".join(bad))
    c006 = next(r for r in d0["records"] if r["id"] == "CFL-006")
    want = ["%s@%s" % (p, RC.sha16(p)) for p in RC.FILES.values()]
    if sorted(c006.get("evidence_bound_to") or []) != sorted(want):
        E.refuse("CFL-006's bindings are not the files read now: %s against %s" % (c006.get("evidence_bound_to"), want))
    ev = ("v2/docs/records/l3r2/read_cfl006.py re-read the four bound files on " + DATE + " (L3-R2; its output "
          "v2/docs/records/l3r2/read_cfl006.out): the protection table, the energy chain and the board facts each name "
          "D-06's one 4S3P block of the Samsung INR18650-35E of about 145 Wh (the protection table with parallel_min and "
          "parallel_max 3); v2/cad/pack_4s.py opens SUPERSEDED in its own docstring, names D-06's block and S-27, still "
          "draws the wrapped 4S4P box (its CELLS constant) and says the block's hold-down is not designed yet. The FAIL "
          "stands on the enclosure alone, on the files at %s; the runtime pages were not re-read here."
          % ", ".join(RC.sha16(p) for p in RC.FILES.values()))
    E.screen(ev, "CFL-006's evidence entry")
    raw = E.replace_entry(raw, "CFL-006", lambda b: E.append_folded(E.add_list_entry(b, "evidence", ev), "notes", CFL006_NOTE), "records")

    # 6. CFL-002
    r042 = next(r for r in d0["records"] if r["id"] == "REQ-042")
    if "TBD" in str(r042.get("acceptance")) or r042.get("status") == "TBD": E.refuse("REQ-042 carries a TBD")
    if "S-49 names its part" not in " ".join(str(r042.get("acceptance")).split()): E.refuse("REQ-042's acceptance no longer names S-49")
    raw = E.replace_entry(raw, "CFL-002", lambda b: E.append_folded(b, "notes", CFL002_ADD), "records")

    # 7. acceptances
    recs0 = {r["id"]: r for r in d0["records"]}
    for rid, new in ACCEPT.items():
        r = recs0[rid]
        if " ".join(str(r["acceptance"]).split()) != " ".join(ACCEPT_OLD[rid].split()):
            E.refuse("%s's acceptance is not the text this script restates" % rid)
        st = " ".join(str(r["statement"]).split())
        for f in ACCEPT_FROM_STATEMENT[rid]:
            if f not in st: E.refuse("%s's statement does not carry %r" % (rid, f))
        hist = ("Acceptance restated on " + DATE + " " + MARK + " to a measurable criterion taken from the record's own "
                "statement, with no limit added or removed. It read: '" + " ".join(ACCEPT_OLD[rid].split()) + "'")
        E.screen(hist, "%s's history" % rid)
        def edit(b, new=new, hist=hist):
            b = E.set_folded(b, "acceptance", new)
            return E.append_folded(b, "history", hist, after="source_check")
        raw = E.replace_entry(raw, rid, edit, "records")

    # 8. header
    anchor = "\n#\n# IDS ARE STABLE."
    if raw.count(anchor) != 1: E.refuse("the header anchor '# IDS ARE STABLE.' occurs %d times" % raw.count(anchor))
    raw = raw.replace(anchor, "\n" + HEADER.strip("\n") + anchor, 1)
    return raw, sid


ALLOWED_FIELDS = {"REQ-016": {"waits_on"}, "REQ-072": {"waits_on", "evidence", "evidence_bound_to"}, "M-02": {"title"},
                  "S-53": {"title"}, "CFL-006": {"evidence", "notes"}, "CFL-002": {"notes"}}


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new, sid = build(old)
        before, after = E.parse(old), E.parse(new)
        expected = {("owner_rulings", "D-21", "added"), ("owner_rulings", "D-22", "added"), ("open_items", "S-114", "removed"),
                    ("closed_items", "S-114", "added"), ("open_items", sid, "added"), ("records", "REQ-016", "changed"),
                    ("records", "REQ-072", "changed"), ("open_items", "M-02", "changed"), ("open_items", "S-53", "changed"),
                    ("records", "CFL-006", "changed"), ("records", "CFL-002", "changed")} | \
                   {("records", r, "changed") for r in ACCEPT}
        got = set(E.diff_entries(before, after))
        if got != expected: E.refuse("the entries changed are not the list: extra %s, missing %s"
                                     % (sorted(got - expected), sorted(expected - got)))
        for (sec, eid, kind) in got:
            if kind != "changed": continue
            f = set(E.changed_fields(before, after, sec, eid))
            allowed = ALLOWED_FIELDS.get(eid, {"acceptance", "history"})
            if not f <= allowed: E.refuse("%s changed fields %s beyond %s" % (eid, sorted(f), sorted(allowed)))
        for k in ("baseline_state", "needs_document_sha256", "sources_read_at"):
            if before.get(k) != after.get(k): E.refuse("%s moved" % k)
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r2_session: REFUSED: %s" % e)
        return 2
    for sec, eid, kind in sorted(got):
        print("%-14s %-8s %s %s" % (sec, eid, kind, ",".join(E.changed_fields(before, after, sec, eid)) if kind == "changed" else ""))
    print("apply_l3r2_session: %d entries, the energy basis item is %s, validator 0 errors, %d warnings%s"
          % (len(got), sid, len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_session: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
