#!/usr/bin/env python3
"""The open items of the review of decision 31, into the requirements registry, and the closure of S-88 when its
condition is met (MESHSAT-1357, worker d8dec31, 28 September 2026). The integrator runs it on
v2/ecad/tools/pcb_requirements.yaml, its file.

STAGE 1 (default). It appends the items below to `open_items`, each at the next free S- number AT APPLY TIME (read by
the same regex the earlier registry scripts of this programme use, so the ids depend on what the integrator applies
first; the mapping finding -> id is PRINTED and written under the root it is given as
v2/docs/records/d8dec31/ids-registry.json, never beside this script; the fresh check's item M5), class SESSION, status
OPEN, in the registry's own shape. EVERY ITEM IS LINKED: each is added to the `waits_on` of the records whose verdict
it can move (LINKS below, read from the registry's records: REQ-029 for every finding about a conductor a person
touches, REQ-015 for the vehicle entry, REQ-009 for the headset jacks, REQ-041 for the sensor pod, REQ-058 for the
arrestors, REQ-007 for the panel's buttons, CHO-003 for the surge notes), so `rules_lib.py requirements` passes after
it (the validator refuses an open item that no record waits on and that carries no disposition). It asserts the review
is in the tree, asserts the new text differs, re-parses the file, checks every id and every link once, and refuses a
second run by a marker. IT CLOSES NOTHING.

STAGE 2 (--close-s88 <commit>). S-88 (finding H3-02 of the independent review of handover H3; erratum f of
RELEASE-H3.md) closes only when TRN-001 has been RE-TAKEN on board A on the corrected declaration, which is the
integrator's on the KiCad host. This stage REFUSES unless, in the tree it is given: v2/ecad/out/port_protect_a.verdict.json
reads PASS; its inputs.netlist.sha256_16 is the sha256/16 of board A's declared-phase netlist in the tree; its
writer and code bundle name port_protect.py at the sha256/16 of the tree's port_protect.py, and that module carries the
reviewed-set reconciliation (its syntax tree defines `reconcile`, `reviews` and `cover`; a parse, not a grep); its
counts read 0 declarations refused, 0 uncovered pins and 0 review disagreements; boards/a.json declares J_VR1 and
`internal_ports` (apply_port_declarations.py applied); and pcb_port_reviews.json holds board A. It then moves S-88 from
`open_items` to `closed_items` with `closed_by: commit <commit>` (the commit that landed the re-take, which must be in
the tree's history when git can answer) and a `closing_evidence` naming the reading, and takes S-88 out of every
record's `waits_on` (a record never waits on a closed item). The item's `limits_reading` goes with it: the limit on
TRN-001's reading of board A is lifted by the re-take it names.

The items (the finding ids are the review's, v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md):
  A-F2   board A: the maker's network at the LTC2954's PB pin (apply_gen_sch_a_mainpb.py)
  X-C1   board C: the MAIN button's clamp refers to a rail that is off while the button is live
  D-F1   board D: the push-to-talk clamp does not clamp below the gate behind it (apply_gen_sch_d_ptt.py)
  D-F2   board D: the speaker conductors, not judged at the desk
  D-F3   board D: the touch lead J_USB3 carries no clamp and none of the hub maker's port parts
  D-F4   board D: C41 and C42 carry no voltage in their value text on a conductor whose clamp reaches 37 V
  E-F1   board E: the ideal diode controller's input capacitor (apply_gen_sch_e_cin.py)
  E-F2   board E: F1 is rated 32 V DC on a line specified to 36 V
  E-F3   board E: the pod's 3.3 V conductor, by a conservative bound (apply_gen_sch_e_pod.py)
  E-F4   board E: the pod's lead has no series element and shares the bus with five parts inside
  D-N1   the arrestor's turn-on against the antenna conductor's transmit peak: a question for the maker
  A-N1 and E-N2   the clamps' rated pulse against U2's and U3's ratings: for R-PWR
  T-2    boards B and C read INCONCLUSIVE under the changed tool until their tables name their internal connectors and a
         review enumerates their external pins into pcb_port_reviews.json
  T-3    an off_board entry is believed on its text

Usage: apply_registry_d31.py <tree root> [--check]
       apply_registry_d31.py <tree root> --close-s88 <commit> [--check]
"""
import ast, hashlib, json, os, re, subprocess, sys

import yaml

MARK = "the review of decision 31 (stream d8dec31, 28 September 2026)"
REVIEW = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"

# the records whose verdict each item can move (their ids in pcb_requirements.yaml's records)
LINKS = {
    "A-F2": ["REQ-029", "REQ-007"], "X-C1": ["REQ-007", "REQ-029"], "D-F1": ["REQ-009", "REQ-029"],
    "D-F2": ["REQ-009", "REQ-029"], "D-F3": ["REQ-029"], "D-F4": ["REQ-009"], "E-F1": ["REQ-015", "REQ-029"],
    "E-F2": ["REQ-015"], "E-F3": ["REQ-041", "REQ-029"], "E-F4": ["REQ-041", "REQ-029"], "D-N1": ["REQ-058"],
    "A-N1": ["REQ-015", "CHO-003"], "T-2": ["REQ-029"], "T-3": ["REQ-029", "REQ-058"],
}

ITEMS = [
    ("A-F2", "Board A: the MAIN button's lead runs from the face to the LTC2954's PB pin with nothing on this board "
             "(the net is J_MAINSW.1 and U1.2). ADI 2954fb p.12 and p.13 ask for 5.1 k and 0.1 uF at the pin for a button "
             "far from the chip; the lead's clamp is board C's U10 at the switch. Finding A-F2 of %s, section 4.3; the "
             "change is v2/docs/records/d8dec31/apply_gen_sch_a_mainpb.py, for board A's generator owner in the next "
             "circuit round, with apply_interfaces_mainsw.py for the contract IF-AC-MAINSW after it. Closed by the parts "
             "on board A's netlist and a re-review on it."),
    ("X-C1", "Board C: U10 (USBLC6-2SC6), the clamp of the MAIN button's pair, has its rail pin on board C's +3V3, "
             "which is off while the kit is off and the PB conductor is live at 1 to 2 V from a source of 1 to 15 uA "
             "(2954fb p.3). If the array's upper diode holds under the PB threshold (0.6 to 1.0 V) at those currents, "
             "the LTC2954 reads a pressed button while the kit is off. Not judged at the desk: ST gives the forward "
             "voltage at 10 mA only (DS4260 Table 2). Finding X-C1 of %s, section 4.4; the same question stands for "
             "U11 on the PI button's pair. For board C's owner: the array's characteristic at microamps from ST, or a "
             "bench measurement, or a clamp that refers to no rail (a substitution to prove)."),
    ("D-F1", "Board D: the push-to-talk clamps D11 and D14 (PESD5V0S1BA, VBR 5.5 to 9.5 V, VCL 10 to 14 V) stand on "
             "the same net as U9's inputs (74LVC1G08GV, -0.5 to 6.5 V, IIK -50 mA) and Q4, Q5's sources with nothing in "
             "series: positive, the clamp does not clamp below the gate's rating and C49, C50 hold what it left for a "
             "millisecond; negative, the gate's own input conducts first. Finding D-F1 of %s, section 5.3; the change is "
             "v2/docs/records/d8dec31/apply_gen_sch_d_ptt.py (1 k and two BAT46W per line), for board D's generator "
             "owner. Closed by the parts on board D's netlist and a re-review on it."),
    ("D-F2", "Board D: the speaker clamps D9 and D12 stand on U7's outputs (TPA6132A2) with nothing in series; the "
             "amplifier's output conducts from about 2.5 V, before the clamp's 5.5 V, and TI gives the outputs a human "
             "body model figure only (SLOS597B p.4). Not judged at the desk. Finding D-F2 of %s, section 5.3. Decided "
             "by TI's IEC 61000-4-2 figure for these outputs or by test M7; removed by a series element between the "
             "jack's clamp and the output, sized by the headset's impedance, which is board D's owner's."),
    ("D-F3", "Board D: J_USB3 is the touch lead of the monitor on the face (SC-HF-06) and carries no clamp on its pair "
             "and none of the port parts its hub's maker asks for (TI SLLS413L p.17: 22 uF on the port's VBUS, a bead "
             "with 100 nF on the connector side). Not judged at the desk, the lead staying inside the case. Finding "
             "D-F3 of %s, section 5.3. Removed by the USBLC6-2SC6 the set already buys at the header and the maker's two "
             "port parts, for board D's owner, with HF-F06's port limit."),
    ("D-F4", "Board D: C41 and C42 (value '1u', no code) stand on the microphone conductors behind D10 and D13, whose "
             "clamp reaches 37 V at 5 A and whose breakdown is 16.7 V at most, and their value text states no voltage. "
             "Finding D-F4 of %s, section 5.3. Closed by a value text naming 50 V or more, so the bill carries it."),
    ("E-F1", "Board E: U3 (LM74700-Q1) has no input capacitor; TI SNOSD17G 10.1.1.2.3 (p.17) requires 22 nF at the "
             "least, and DC_F carries only the VCAP capacitor C4. With none, a negative discharge at the receptacle "
             "drives DC_F to D10's clamping voltage and puts that plus DC_P's voltage across Q1 (60 V) and U3 (75 V), "
             "TI's own criterion (10.1.1.3, p.18). Finding E-F1 of %s, section 6.3; the change is "
             "v2/docs/records/d8dec31/apply_gen_sch_e_cin.py (1 uF 100 V, board A's C207's part and code C382212; board "
             "E's C6 and C7 have the same value text and no code), for board E's generator owner. Closed by the part on "
             "board E's netlist and a re-review on it."),
    ("E-F2", "Board E: F1 is a MINI blade of the class the Keystone 3568 holder takes, and the series the record holds "
             "(Littelfuse 297) is rated 32 V DC with an interrupting rating of 1000 A at 32 V DC, on a line specified to "
             "36 V whose hot swap admits 40 V. Finding E-F2 of %s, section 6.3. Closed by a fuse of the same form rated "
             "above 40 V, with its maker's sheet filed: the 58 V MINI series is the candidate and its sheet is not held "
             "(littelfuse.com answered 403; the Internet Archive held no copy at the addresses tried on 27 September "
             "2026); that its series number is 997 is INFERRED. For board E's owner and R-PWR."),
    ("E-F3", "Board E, by a conservative bound and not a demonstrated defect: J_POD.1 is the rail +3V3_E6 out of the "
             "case; D9's VBUS element breaks down at 6 V at the least, above the absolute maximum supply of every part "
             "on the rail (SGP41 3.6 V, RP2040 3.63 V, BMI270 4 V, BME688 4.25 V), and the rail's 4.3 uF lets the whole "
             "charge of the IEC 61000-4-2 network lift it to 3.61 V at 8 kV and 3.86 V at 15 kV from the regulator's "
             "3.333 V maximum (the bound: nothing into the loads, which take the excess in microseconds). Finding E-F3 "
             "of %s, section 6.3; the change is v2/docs/records/d8dec31/apply_gen_sch_e_pod.py (two 10 uF 25 V at the "
             "header, which puts the same bound at 3.38 and 3.43 V), for board E's generator owner. Closed by the parts "
             "on board E's netlist and a re-review on it, or by a measurement under test M7 that reads the rail under "
             "the ratings."),
    ("E-F4", "Board E: the pod's lead has no series element, so a short of its 3.3 V conductor outside takes the sensor "
             "controller's rail and the hot stop line with it, and SDA1 and SCL1 run from the pod's pins to five parts "
             "inside (U10, U14, U15, U17 and the module on J_LTG) with D9 on them and nothing in series. Not judged at "
             "the desk. Finding E-F4 of %s, section 6.3. Options: series resistors between D9 and the bus inside, or the "
             "pod on a bus of its own; a series element on the feed, sized by the pod's supply current, which waits for "
             "the pod's part (IF-E-POD). For board E's owner."),
    ("D-N1", "The antenna bulkheads' arrestor (PolyPhaser GTH-SFF-AL) is rated for surge (10 kA, no waveform stated) "
             "with a 90 V turn-on and a 60 V DC operating maximum, and its sheet states no IEC 61000-4-2 figure and no "
             "let-through; the VHF conductor's transmit peak with the wave wholly reflected is the intent's own 110 V. "
             "Eleven antenna conductors of board A and board D's antenna path are therefore not judged at the desk "
             "(%s, sections 4.5 and 5.3). The question for the maker is prepared in section 9.3 and not sent; sending "
             "it is the owner's. Decided by the maker's answer, by each radio's antenna-port rating, or by test M7."),
    ("A-N1", "For R-PWR: at their rated pulse the VIN_RAW clamps (SMCJ40A, 64.5 V at 23.3 A) carry board A's front-end "
             "controller U2 (LM5176, VIN and VISNS rated 60 V) outside its rating, and board E's D10 carries U3's ANODE "
             "(65 V) to within 0.5 V; no surge level is ruled (D-16), so nothing fails, and the coordination of board E's "
             "hot swap (stops above 40 V) with the four SMCJ40 parts between the receptacle and U2 is the qualified "
             "power review's to compute. Notes A-N1 and E-N2 of %s, sections 4.3 and 6.3."),
    ("T-2", "With port_protect.py's change of stream d8dec31 (a connector pin carrying a supply or a signal that no "
            "entry of the declaration covers makes TRN-001 INCONCLUSIVE, and so does a declaration whose external pins "
            "no review has enumerated into v2/ecad/tools/pcb_port_reviews.json), boards B and C read INCONCLUSIVE until "
            "their tables carry `internal_ports` naming where each internal lead goes (290 connector pins on board B and "
            "39 on board C in the scratch reading, %s, section 10) and a review of their exposed conductors, as decision "
            "31's for A, D and E, writes their reviewed sets. For the owners of boards/b.json and boards/c.json; the "
            "shape is boards/a.json, d.json and e.json after apply_port_declarations.py and the three records of "
            "pcb_port_reviews.json."),
    ("T-3", "port_protect.py believes an `off_board` entry on its text: it cannot ask what the part named in the wall "
            "is rated for, so an arrestor rated for surge answers a rule about electrostatic discharge, and TRN-001's "
            "PASS on board A after apply_port_declarations.py believes 12 of its 18 entries on that text (the eleven "
            "antenna conductors, not judged at the desk, and J_MAINSW, read on board C's netlist). A declaration form "
            "that names the part, its document and the level it is rated to, read by the tool, is owed (%s, section "
            "10, T-3). For the tools stream."),
]

RECORD_ID = re.compile(r"^  - id: ([A-Z][A-Z][A-Z]-\d\d\d)$", re.M)


def wrap(text, indent=6, width=118):
    words, lines, cur = text.split(), [], " " * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = " " * indent + w
        else: cur = (cur + " " + w) if cur.strip() else cur + w
    lines.append(cur)
    return "\n".join(lines) + "\n"


def _record_blocks(text):
    """{record id: (start, end)} of every record block of the `records:` section, by position in the text."""
    j = text.index("\nrecords:\n")
    starts = [(m.start(), m.group(1)) for m in RECORD_ID.finditer(text, j)]
    out = {}
    for k, (s, rid) in enumerate(starts):
        e = starts[k + 1][0] if k + 1 < len(starts) else len(text)
        assert rid not in out, "record %s twice" % rid
        out[rid] = (s, e)
    return out


def _waits_line(block):
    return re.search(r"^    waits_on: \[(.*?)\]\n", block, re.M)


def _add_waits(text, rid, sids):
    """The record's `waits_on` extended by `sids` (a new line before `status:` when it has none)."""
    s, e = _record_blocks(text)[rid]
    block = text[s:e]
    m = _waits_line(block)
    if m:
        have = [x.strip() for x in m.group(1).split(",") if x.strip()]
        assert not set(have) & set(sids), (rid, have, sids)
        block2 = block[:m.start()] + "    waits_on: [%s]\n" % ", ".join(have + list(sids)) + block[m.end():]
    else:
        m = re.search(r"^    status: ", block, re.M)
        assert m, "%s has no status line" % rid
        block2 = block[:m.start()] + "    waits_on: [%s]\n" % ", ".join(sids) + block[m.start():]
    assert block2 != block
    return text[:s] + block2 + text[e:]


def _drop_wait(text, rid, sid):
    s, e = _record_blocks(text)[rid]
    block = text[s:e]
    m = _waits_line(block)
    assert m, (rid, sid)
    have = [x.strip() for x in m.group(1).split(",") if x.strip()]
    assert sid in have, (rid, have, sid)
    rest = [x for x in have if x != sid]
    new = ("    waits_on: [%s]\n" % ", ".join(rest)) if rest else ""
    return text[:s] + block[:m.start()] + new + block[m.end():] + text[e:]


def stage_items(root, dry):
    reg = os.path.join(root, "v2", "ecad", "tools", "pcb_requirements.yaml")
    if not os.path.exists(os.path.join(root, REVIEW)):
        raise SystemExit("apply_registry_d31: %s is not in the tree" % REVIEW)
    old = open(reg, encoding="utf-8").read()
    if MARK in old:
        raise SystemExit("apply_registry_d31: already applied (its marker is in the file)")
    d0 = yaml.safe_load(old)
    top = max(int(m) for m in re.findall(r"\n  - id: S-(\d+)\n", old))
    ids = ["S-%d" % (top + 1 + k) for k in range(len(ITEMS))]
    assert not any(x.get("id") in ids for x in d0["open_items"] + d0["closed_items"])
    recs = {r["id"]: r for r in d0["records"]}
    for fid, _t in ITEMS:
        assert fid in LINKS and LINKS[fid], "%s has no record to wait on it" % fid
        for rid in LINKS[fid]: assert rid in recs, "%s: %s is not a record of this registry" % (fid, rid)
    block = ""
    for sid, (fid, title) in zip(ids, ITEMS):
        block += "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n" % sid + wrap(
            "%s: " % fid + (title % MARK) + " (finding %s)" % fid if fid not in title else "%s: " % fid + (title % MARK))
    # the items go at the END of open_items, just before closed_items (an older script's anchor, the comment "Items
    # that left the open list", now sits in the middle of the open list and is not used here)
    head = "\nclosed_items:\n"
    assert old.count(head) == 1, "the closed list's start is not where this script expects it"
    t = old.replace(head, "\n" + block.rstrip("\n") + "\n" + head.lstrip("\n"))  # integrator fix (check 2, B2): the block starts on its own line whether or not a blank line precedes closed_items
    # every item linked from the record(s) whose verdict it can move
    by_rec = {}
    for sid, (fid, _t) in zip(ids, ITEMS):
        for rid in LINKS[fid]: by_rec.setdefault(rid, []).append(sid)
    for rid, sids in sorted(by_rec.items()): t = _add_waits(t, rid, sids)
    assert t != old
    d1 = yaml.safe_load(t)
    got = {x["id"]: x for x in d1["open_items"]}
    for sid in ids:
        assert sid in got and got[sid]["status"] == "OPEN" and got[sid]["class"] == "SESSION", sid
        assert sum(1 for x in d1["open_items"] if x["id"] == sid) == 1
    assert len(d1["open_items"]) == len(d0["open_items"]) + len(ITEMS)
    assert d1["closed_items"] == d0["closed_items"]
    r1 = {r["id"]: r for r in d1["records"]}
    for rid, sids in by_rec.items():
        assert all(s in (r1[rid].get("waits_on") or []) for s in sids), (rid, r1[rid].get("waits_on"))
        assert {k: v for k, v in r1[rid].items() if k != "waits_on"} == {k: v for k, v in recs[rid].items() if k != "waits_on"}, rid
    assert all(r1[k] == recs[k] for k in recs if k not in by_rec), "a record this script does not link moved"
    waited = {x for r in d1["records"] for x in (r.get("waits_on") or [])}
    assert all(s in waited for s in ids)
    mapping = {fid: sid for sid, (fid, _t) in zip(ids, ITEMS)}
    if not dry:
        with open(reg, "w", encoding="utf-8") as f: f.write(t)
        yaml.safe_load(open(reg, encoding="utf-8"))
        outp = os.path.join(root, "v2", "docs", "records", "d8dec31", "ids-registry.json")
        os.makedirs(os.path.dirname(outp), exist_ok=True)
        json.dump({"registry_top_before": "S-%d" % top, "ids": mapping, "links": by_rec},
                  open(outp, "w", encoding="utf-8"), indent=1)
    print("apply_registry_d31: %d open items, %s to %s, each linked from its record(s)%s"
          % (len(ITEMS), ids[0], ids[-1], " (checked, not written)" if dry else ""))
    for sid, (fid, _t) in zip(ids, ITEMS): print("   %-6s %-5s waited on by %s" % (sid, fid, ", ".join(LINKS[fid])))
    return 0


def _sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _refuse(why):
    raise SystemExit("apply_registry_d31: REFUSED, " + why)


def stage_close_s88(root, commit, dry):
    reg = os.path.join(root, "v2", "ecad", "tools", "pcb_requirements.yaml")
    old = open(reg, encoding="utf-8").read()
    d0 = yaml.safe_load(old)
    if any(x["id"] == "S-88" for x in d0["closed_items"]): raise SystemExit("apply_registry_d31: S-88 is already closed")
    item = [x for x in d0["open_items"] if x["id"] == "S-88"]
    assert item and "H3-02" in item[0]["title"], "S-88 is not the open item this script expects (finding H3-02)"
    if not commit or len(commit) < 8 or len(commit) > 40 or any(ch not in "0123456789abcdef" for ch in commit):
        raise SystemExit("apply_registry_d31: --close-s88 needs the commit (8 to 40 hex digits) that landed the re-take")
    tools = os.path.join(root, "v2", "ecad", "tools")
    # the re-taken reading, in the tree
    vp = os.path.join(root, "v2", "ecad", "out", "port_protect_a.verdict.json")
    if not os.path.exists(vp): _refuse("%s is not in the tree: TRN-001 has not been re-taken on board A here" % os.path.relpath(vp, root))
    v = json.load(open(vp, encoding="utf-8"))
    if v.get("verdict") != "PASS": _refuse("the re-taken reading is %s, not PASS: %s" % (v.get("verdict"), (v.get("evidence") or [])[:3]))
    sys.path.insert(0, tools)
    import phase_artefacts as PA
    net = PA.netlist("a")
    want = _sha16(net) if net and os.path.exists(net) else None
    ni = (v.get("inputs") or {}).get("netlist")
    got = ni.get("sha256_16") if isinstance(ni, dict) else None
    if not want or got != want: _refuse("the reading judged netlist %s and board A's declared phase's netlist is %s" % (got, want))
    pp = os.path.join(tools, "port_protect.py")
    tool_sha = _sha16(pp)
    w = (v.get("writer") or {}).get("sha16"); cb = ((v.get("code_bundle") or {}).get("files") or {}).get("port_protect.py")
    if w != tool_sha or cb != tool_sha: _refuse("the reading was written by port_protect.py %s (bundle %s) and the tree's is %s" % (w, cb, tool_sha))
    names = {n.name for n in ast.walk(ast.parse(open(pp, encoding="utf-8").read())) if isinstance(n, ast.FunctionDef)}
    need = {"reconcile", "reviews", "cover"}
    if not need <= names: _refuse("the tree's port_protect.py does not carry the reviewed-set reconciliation (%s)" % sorted(need - names))
    c = v.get("counts") or {}
    for k in ("declarations_refused", "uncovered_pins", "review_disagreements"):
        if c.get(k) != 0: _refuse("the reading's counts.%s is %r, not 0" % (k, c.get(k)))
    a = json.load(open(os.path.join(tools, "boards", "a.json"), encoding="utf-8"))
    refs = [e.get("ref") for e in a.get("external_ports") or []]
    if "J_VR1" not in refs or "J_DOCK" in refs or "internal_ports" not in a:
        _refuse("boards/a.json is not the corrected declaration (apply_port_declarations.py)")
    pr = json.load(open(os.path.join(tools, "pcb_port_reviews.json"), encoding="utf-8"))
    if "a" not in (pr.get("boards") or {}): _refuse("pcb_port_reviews.json holds no record for board A")
    # the commit, when git can answer here
    try:
        r = subprocess.run(["git", "-C", root, "cat-file", "-e", "%s^{commit}" % commit], capture_output=True, timeout=20)
        probe = subprocess.run(["git", "-C", root, "rev-parse", "--git-dir"], capture_output=True, timeout=20)
        if probe.returncode == 0 and r.returncode != 0: _refuse("commit %s is not in this tree's history" % commit)
        if probe.returncode != 0: print("apply_registry_d31: git cannot say here whether %s exists (not a checkout); the validator will warn" % commit)
    except (OSError, subprocess.SubprocessError):
        print("apply_registry_d31: git cannot say here whether %s exists; the validator will warn" % commit)
    # move the item: cut its block out of open_items, write the closed entry at the end of closed_items
    s = old.index("\n  - id: S-88\n") + 1
    nxt = re.compile(r"^  - id: S-\d+$|^closed_items:$", re.M)
    e = nxt.search(old, s + 1).start()
    blk = old[s:e]
    tm = re.search(r"^    title: >-\n", blk, re.M)
    assert tm, "S-88 has no folded title"
    title_lines = blk[tm.end():].rstrip("\n")
    waiters = [r["id"] for r in d0["records"] if "S-88" in (r.get("waits_on") or [])]
    ev = ("TRN-001 re-taken on board A on the corrected declaration (v2/ecad/out/port_protect_a.verdict.json, PASS of %s, "
          "netlist %s, written by port_protect.py %s, %d ports, %d pins declared internal, 0 declarations refused, 0 "
          "uncovered pins, 0 disagreements with the reviewed set of pcb_port_reviews.json), landed by commit %s. The "
          "declaration names VIN_RAW's entry (J_VR1 to J_VR4, apply_port_declarations.py); the checker refuses a declared "
          "port whose pins carry no supply or signal and reports every connector pin no entry covers (port_protect.py "
          "cover, d3125b1e); the regression that an entry moved onto ground pins, out of the declaration, into "
          "internal_ports or narrowed by pins demands reconciliation is tests/test_port_protect.py's reviewed-set tests "
          "on fixtures and v2/docs/records/d8dec31/readings/regress-reclassify.txt on the three real tables. The limit "
          "this item put on TRN-001's reading of board A is lifted by this reading. The review of decision 31 "
          "(v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md) is the record; its own findings are open items of "
          "their own and are not closed by this."
          % (v.get("denominator"), got, tool_sha, c.get("ports", 0), c.get("internal_pins", 0), commit))
    closed = "  - id: S-88\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s\n" % (commit, wrap(ev), title_lines)
    t = old[:s] + old[e:]
    tail = "\nrecords:\n"
    assert t.count(tail) == 1
    t = t.replace(tail, closed + tail)
    for rid in waiters: t = _drop_wait(t, rid, "S-88")
    assert t != old
    d1 = yaml.safe_load(t)
    assert not any(x["id"] == "S-88" for x in d1["open_items"]) and len(d1["open_items"]) == len(d0["open_items"]) - 1
    cl = [x for x in d1["closed_items"] if x["id"] == "S-88"]
    assert len(cl) == 1 and cl[0]["closed_by"] == "commit %s" % commit and cl[0]["title"] == item[0]["title"], cl
    assert len(d1["closed_items"]) == len(d0["closed_items"]) + 1
    assert not any("S-88" in (r.get("waits_on") or []) for r in d1["records"])
    r0, r1 = {r["id"]: r for r in d0["records"]}, {r["id"]: r for r in d1["records"]}
    for k in r0:
        assert {kk: vv for kk, vv in r0[k].items() if kk != "waits_on"} == {kk: vv for kk, vv in r1[k].items() if kk != "waits_on"}, k
    if not dry:
        with open(reg, "w", encoding="utf-8") as f: f.write(t)
        yaml.safe_load(open(reg, encoding="utf-8"))
    print("apply_registry_d31: S-88 closed by commit %s on the re-taken reading (PASS of %s, netlist %s, tool %s); "
          "waits_on dropped from %s%s" % (commit, v.get("denominator"), got, tool_sha, ", ".join(waiters),
                                          " (checked, not written)" if dry else ""))
    return 0


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    if "--close-s88" in argv:
        k = argv.index("--close-s88")
        return stage_close_s88(root, argv[k + 1] if k + 1 < len(argv) and not argv[k + 1].startswith("-") else "", dry)
    return stage_items(root, dry)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
