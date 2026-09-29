#!/usr/bin/env python3
"""Stream s122, round 4 (S-122, MESHSAT-1357, 29 September 2026), for the integrator to run once fnd/s122c is merged on
set 14's line (`1bafab8c`, where `apply_registry_s122.py` has already run and refuses): the registry follows the
documents `apply_docs_s122_r4.py`, `apply_docs_s122_r5.py` and `apply_docs_s122_r6.py` changed (round 5 re-issued this
script for its diff: V2-SPEC.md lines 81, 83, 84 and 86 and correction 35, the role rule and the wider finder; round 6
re-issued it again for its diff: V2-SPEC.md line 47 and correction 36, the fixtures and the figure scan of the gate;
round 7 for correction 36's wording, the figure comparison, and the follow-up item of step 5).

It writes `v2/ecad/tools/pcb_requirements.yaml`, `v2/ecad/tools/pcb_envelope.yaml` and
`v2/ecad/tools/pcb_rules_coverage.yaml` and nothing else:
  1. REBIND: every record bound to V2-SPEC.md, OPERATING-ENVELOPE.md or handover/DEFINITION-STATUS.md at its set 14 sha
     gains one entry and moves to the new sha16. The entry's reason is read by this script (the helpers of
     `apply_registry_s122.py`) from the diff against `1bafab8c` (the new line numbers and their sections), from the
     sentence sets and the verdicts (`verdicts-set14.out`, the documents at `1bafab8c` judged by round 4's tools, and
     `verdicts.out`), and from the record's own text; it does not re-read the rest of the record's argument.
     CONOPS.md is not changed, so the needs pin does not move.
  2. CFL-016: one entry naming the round 4 inventory (makers' part numbers, judged against the netlists' part values;
     the sentences the finder found and their corrections; the counts this script reads from the verdict files), and a
     sentence appended to its `notes` recording the baseline reading on the record itself (check-int15-1 m7). CFL-016
     stays FAIL and waits on S-122.
  3. S-122's title: one appended sentence that states what `close_s122.py`'s gate checks since round 4 (the fourth
     check of set 14, q1 to q3), and what round 4 answered of check-s122-3's minors and check-int15-1's m7.
  4. OPERATING-ENVELOPE.md changed two rows of section 2 and no number of section 4: the envelope's pin
     (`pcb_envelope.yaml` document_sha256) and ENV-001's `verified_sha` move to the new file, after the script asserts
     that every number the envelope carries is still in the document.
  5. Round 7 (check-s122-6, the coordinator's ruling): one open item for the regression instrument's known escape
     classes, at the next free S number of the registry it runs on (the highest S number of the open and closed items,
     plus one; never hard-coded), class SESSION, disposition PROCESS with its reason, and in no record's waits_on.
Each new sentence is screened (claims_check's CLAIM words, dashes). Every other record, open item and closed item is
asserted unchanged, older evidence is kept as a prefix, and each file re-parses. Refuses a second run.
Run from anywhere: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import apply_registry_s122 as R1  # noqa: E402

A = R1.A
TAG = "apply_registry_s122_r4"
BASE = "1bafab8c"
R1.BASE = BASE             # the helpers' diff base
REG, ENV, COV = R1.REG, R1.ENV, R1.COV
DOCS = {"v2/docs/V2-SPEC.md": "1e1547e1462904f7", "v2/docs/OPERATING-ENVELOPE.md": "a8e65995c594546b",
        "v2/docs/handover/DEFINITION-STATUS.md": "2db0ad36da754fa4"}
REF = "v2/docs/records/s122/apply_docs_s122_r4.py, apply_docs_s122_r5.py, apply_docs_s122_r6.py and apply_docs_s122_r7.py"
FOLLOW_MARK = "(stream s122, the regression instrument's known escape classes"
FOLLOW_TITLE = (
    FOLLOW_MARK + "; the independent checks v2/docs/records/s122/checks/check-s122-5.md and check-s122-6.md, m2 and m4) "
    "Harden S-122's regression instrument (v2/docs/records/s122: s122lib.py's part-number finder, verdicts.py's role "
    "rule and figure scan, close_s122.py's gate) against the escape classes its scope statement names: a role noun "
    "outside ROLE_NOUN read as no role (check-s122-6's 'the TPS22810 bias FET', 'the TPS22810 bias source', 'the "
    "TLV75801 gate-bias generator'); a stale part in a clause that states a date or a history word ('the TUSB2046B hub "
    "fitted since 26 September 2026', 'the grade that was bought', 'named on the BOM'), for which a history excuse should "
    "tie to a past-tense verb on the part itself; a designator written beside a part it does not carry ('the TLV75801 "
    "gate-bias LDO on PA_KEY (U17', 'the AP64500 buck on slots 1 and 3, U5 and U7'), which needs a rule that pairs a "
    "list of parts with a list of designators in order ('the BME688 and BMI270 (U14, U15'); a number with no unit and "
    "any figure off the closing list ('an NVMe 2280 socket'); and the finder's conservative false hits and misses (an "
    "upper-case commit, 'SMBJ15A/BAT54' as one token, a DS code of four or five digits, the EMC test methods' names (CE102, RE102), "
    "'SMBJ15A-based', a plural 'SMBJ15As'). Open until each class is closed by a rule with a fixture that "
    "close_s122.py runs, or carried with its reason.")
FOLLOW_WHY = (
    "The documents S-122 names are the subject of S-122 and CFL-016; this item is about detecting a regression in them. "
    "The classes are escapes of the instrument under planted mutants, not stale text: of its role mutants "
    "check-s122-6 says 'None of these stands in the committed documents.' So no record's verdict waits on this item, "
    "and CFL-016 does not.")

M7_NOTE = (" Recorded on the record at stream s122's round 4 (check-int15-1 m7, the baseline reading, a SESSION reading "
           "under the owner's standing rule of 26 September 2026): for CONOPS.md, a baselined definition, 'describes the "
           "circuit as generated' is read through v2/docs/handover/DEFINITION-STATUS.md, whose section of CONOPS's current "
           "circuit values keeps the current value of each CONOPS passage that differs from the netlists (rows DC-01 to "
           "DC-10) and is itself judged against the netlists; this record's evidence entry 'The baseline rule' sets it out.")

S122_ADD4 = (
    " Correction at stream s122's round 4 (the fourth check of set 14, q1 to q3; v2/docs/records/s122/close_s122.py's "
    "gate_set14 as that round rewrote it): the gate finds the corrected sentences by what they say, not by a row's first "
    "cell: in V2-SPEC.md and OPERATING-ENVELOPE.md, outside their correction notes, every '<part> display switch', "
    "'<part> codec', '<part> hot swap', '<part> hot-swap controller' and '<part> M.2 B-key socket' must name the "
    "generated part (TS3DV642, PCM2912A, LM5069, LM5069, 2199119) and be TRUE in verdicts.out, not HISTORY, with its own "
    "assertion of that part on its board; a sentence there that names the TMDS341A, the WM8960, a TRACO part or the "
    "MDT420B, or a dock strip sentence that names the LM5176 other than as A22's, is refused; the finder is probed with "
    "part numbers made up at run time and refused if it reads made-up non-parts; and the filed check must carry the "
    "heading '## S-122 closing check' and name each such sentence there by its document and line. Round 4 also corrected "
    "V2-SPEC.md lines 82 (the DS3231M) and 84 (the TUSB2046B), which its finder found, and answered check-s122-3's "
    "minors (row DC-10, the absent rule's wordings, the README's CON-003 quote) and check-int15-1's m7 (CFL-016's notes). "
    "Round 5 (the independent check v2/docs/records/s122/checks/check-s122-4.md, B1: two parts named in roles they no "
    "longer hold read TRUE) added to the gate: the finder is also probed with every part number a semiconductor's, "
    "crystal's or relay's value in the six netlists starts with; the rows it corrected must stand TRUE with their "
    "assertions ('<part> gate-bias' the TLV75801 on D U15 and PA_KEY, '<part> buck on slots 1 and 3' the AP64500 on A U4 "
    "and U6, '<part> stages on slot 2 and the device rail' the LM5176 on A U5 and U7, '<n> LEDs under light guides' "
    "seventeen on board C); no dock strip sentence puts a magnetometer outside the pod; and the check's two sentences as "
    "they stood at edead832 must be refused by the role rule (verdicts.check_roles). The closing check names V2-SPEC.md "
    "lines 47, 81, 82, 83, 84 and 86 and OPERATING-ENVELOPE.md lines 77 and 83. "
    "Round 6 (the independent check v2/docs/records/s122/checks/check-s122-5.md, B1: V2-SPEC.md line 47 named the SA868 "
    "a 1 W part while board D's U2 is its VHF 2 W exciter, corrected by apply_docs_s122_r6.py as correction 36) and "
    "round 7 (the independent check v2/docs/records/s122/checks/check-s122-6.md, B1 and m1 to m6) added to the gate: "
    "'SA868 <n> W' must name 2 W with the assertion of D U2; seventeen mutants of the A22 and D8 rows as they stand (a "
    "non-part token in a parenthesis, converters named on rails they do not feed, a one-word and a two-word qualifier "
    "another part holds, role nouns the netlists never state, a history-excused part put back as current, the codec and "
    "the amplifier swapped, a part named a codec with no qualifier, a part named after its value's load, a qualifier "
    "read inside another word), each judged with the judgement its row carries, must read STALE; line 47 with the 1 W "
    "planted back must be refused; and a scan of the closing list's lines, each read whole from its document, refuses "
    "any figure with a unit (W, V, A, Wh, dBm, mm, C and the like, a range or product of two, an 'N x M' size, an 'NxM' "
    "header that is not a hex address) or spelled count from two to twenty that no assertion of its sentence's TRUE "
    "judgement states with the same values in the same order, their signs, and the unit where the source gives one: a "
    "netlist value, a board file's outline, layers, cutout or zones, a maker's page, a generator's text (gen_sch_p.py's "
    "declared cell node CELL4 at 14.4 V for line 81's node, gen_sch_a.py at b2709118 for its four AP64500 of 7 "
    "September) or a decision's record; the plants 160 x 240 mm, 2x2, +40 to +80 C, +40 to +125 C and the 1 W, with "
    "their keys rewritten and the assertions kept, must be refused by that comparison. test_close_s122.py turns each "
    "test of the role rule (forward, the one-word and two-word qualifiers, rails, word matching, the load phrase) and "
    "the history tie off in turn, and removes the comparison, and the gate then refuses. The instrument's known escape "
    "classes, which the gate does not catch: a number with no unit (a form factor such as 2242, a port such as USB 3) "
    "and any figure off the closing list; a role noun outside the rule's list (FET, source, generator, interface); a "
    "stale part in a clause that states a date or a history word ('the TUSB2046B hub fitted since 26 September 2026'); "
    "a designator written beside a part it does not carry ('the TLV75801 gate-bias LDO on PA_KEY (U17'), which needs "
    "lists of parts and designators paired in order ('the BME688 and BMI270 (U14, U15'); the one-word qualifier test "
    "takes only active parts (U and Q designators) as the holders of a function; a list item '<part> <noun> on <slot "
    "or rail>' is judged by the target rule, not the list rule; and the finder's shapes, which still read an upper-case "
    "commit, 'SMBJ15A/BAT54', a DS code of four or five digits (Maxim's DS3231 and DS12887 shapes among them) and the "
    "EMC test methods' names (CE102, RE102) as part numbers, which a judgement must then excuse, and do not read 'SMBJ15A-based' or "
    "a plural 'SMBJ15As'. These classes are carried by {FOLLOW}, which apply_registry_s122_r4.py opens at the next "
    "free S number with disposition PROCESS and in no record's waits_on: the documents do not hang on it. "
    "Confirming that each correction is true in substance remains the filed check's job.")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    if "apply_registry_s122.py" not in reg: refuse("apply_registry_s122.py has not run: this script follows it")
    before = yaml.safe_load(reg)
    new = {rel: L.sha16(rel) for rel in DOCS}
    for rel, s in DOCS.items():
        if new[rel] == s: refuse("%s is unchanged: merge fnd/s122c first" % rel)
    if L.sha16("v2/docs/CONOPS.md") != R1.CONOPS_BASELINE: refuse("CONOPS.md is not c5430071's file")
    rec = {r["id"]: r for r in before["records"]}
    R1.NLS = L.netlists()
    VB = R1.verdict_map(os.path.join(HERE, "verdicts-set14.out"))
    VA = R1.verdict_map(os.path.join(HERE, "verdicts.out"))
    nets = L.all_nets(R1.NLS)
    out, touched = reg, {}
    for rel, old16 in DOCS.items():
        base = os.path.basename(rel)
        oldb, newb = "%s@%s" % (rel, old16), "%s@%s" % (rel, new[rel])
        bound = sorted(r["id"] for r in before["records"] if oldb in (r.get("evidence_bound_to") or []))
        if not bound: refuse("no record is bound to %s" % oldb)
        _o, nl = R1.diff_lines(rel)
        secs = R1.sections_of(rel)
        sb, sa = R1.all_sentences(rel, BASE), R1.all_sentences(rel, None)
        gone, added = sorted(set(sb) - set(sa)), sorted(set(sa) - set(sb))
        change_txt = ("of the %d sentences the diff removes, verdicts-set14.out holds %s; of the %d it adds, verdicts.out "
                      "holds %s" % (len(gone), R1.tally(gone, VB), len(added), R1.tally(added, VA)))
        changed = sorted({R1.sec_at(secs, n) for n in nl}, key=lambda x: (len(x), x))
        names = set()
        for s in [sb[d] for d in gone] + [sa[d] for d in added]:
            nm = L.names(s, nets)
            names |= set(nm["refs"]) | set(nm["nets"]) | set(nm.get("parts") or [])
        for rid in bound:
            r = rec[rid]
            own = " ".join(str(r.get(f) or "") for f in ("title", "statement", "acceptance", "notes")) + " " + \
                  " ".join(str(e) for e in r.get("evidence") or [])
            hitp = sorted(x for x in names if re.search(r"(?<![\w+])%s(?![\w])" % re.escape(x), own))
            part_txt = ("the changed sentences name %d parts, nets and part numbers, and this record's own text names %s" % (
                len(names), "none of them" if not hitp else "%d of them (%s)" % (len(hitp), ", ".join(hitp))))
            named = R1.named_sections(r.get("evidence") or [], base)
            hit = sorted({x for x in named if not x.startswith("line ")} & set(changed))
            hitl = sorted({x for x in named if x.startswith("line ")} & {"line %d" % n for n in nl})
            if not named:
                rel_txt = "this record's evidence names no section or line of this document"
            elif hit or hitl:
                rel_txt = ("of the places this record's evidence names in this document, %s %s among the changed ones"
                           % (", ".join(["section " + x for x in hit] + hitl), "is" if len(hit) + len(hitl) == 1 else "are"))
            else:
                rel_txt = "none of the places this record's evidence names in this document is among the changed ones"
            entry = ("%s re-read at stream s122's round 4 (%s, %s to %s; MESHSAT-1357, open item S-122, the integration "
                     "checks of set 14): the diff against 1bafab8c, read by v2/docs/records/s122/apply_registry_s122_r4.py, "
                     "changes lines %s (sections %s); %s (the verdicts of v2/docs/records/s122 on set 14's netlists, "
                     "verdicts-set14.out on the documents at 1bafab8c and verdicts.out on these; the correcting script "
                     "asserted every part, value and generator text its new text names before it wrote); %s; %s. This "
                     "entry does not re-read the rest of this record's argument; rebound to %s. This entry changes no result."
                     % (rel, REF, old16, new[rel], ", ".join(str(x) for x in sorted(set(nl))), "; ".join(changed),
                        change_txt, rel_txt, part_txt, new[rel]))
            out = R1.append_entry(out, rid, entry, ('"%s"' % oldb, '"%s"' % newb))
            touched.setdefault(rid, []).append(base)
    # CFL-016: the round 4 inventory
    va, vb = R1.counts(os.path.join(HERE, "verdicts.out")), R1.counts(os.path.join(HERE, "verdicts-set14.out"))
    if not va or sum(v[2] for v in va.values()) or sum(v[5] for v in va.values()): refuse("verdicts.out holds STALE or UNJUDGED sentences")
    per = "; ".join("%s %d sentences (%d at 1bafab8c, %d of them STALE and %d UNJUDGED), %d TRUE, %d BASELINE and %d NOT "
                    "DERIVABLE after" % (d, va[d][0], vb.get(d, (0,) * 7)[0], vb.get(d, (0,) * 7)[2], vb.get(d, (0,) * 7)[5],
                                         va[d][1], va[d][3], va[d][4]) for d in va)
    entry = ("v2/docs/records/s122/inventory.out and verdicts.out (stream s122, round 4; the integration checks of set 14, "
             "v2/docs/records/int15/checks/check-int15-1.md to -3.md): since this round the inventory reads makers' part "
             "numbers by their shape (s122lib.partnos: letter-led tokens of upper-case letters and digits with a run of "
             "three digits, digit-led tokens with a capital and four digits, digit tokens with a dash and six digits, a "
             "series word with its number, and the same shapes in the file names of the makers' sheets a sentence cites), "
             "and verdicts.py judges each against the part values of boards A, B, C, D, E and P: a part number on no "
             "netlist, or not on the one board a sentence and its row name, makes a TRUE judgement STALE and a NOT "
             "DERIVABLE one UNJUDGED unless the judgement names it (a document number, a case or bought item, a stock "
             "code, a part the sentence names as withdrawn or owed or on another board, or an assertion of the generator or "
             "netlist at the date the sentence states); a dated heading excuses none. Judged on the documents at 1bafab8c "
             "(verdicts-set14.out) and after v2/docs/records/s122/apply_docs_s122_r4.py: %s. That script corrected "
             "check-int15-1's five sentences (V2-SPEC.md lines 47, 82 and 86; OPERATING-ENVELOPE.md lines 77 and 83) and "
             "two more its finder found (V2-SPEC.md line 82's DS3231M and line 84's TUSB2046B), asserting every part it "
             "names on set 14's netlists, in the generators at the commits it names and in the held makers' sheets. In "
             "check-int15-2's words (n1) the five named parts on no board, or not on the board the sentence names. The "
             "CONOPS.md sentences read for what is absent or owed were widened to the wordings check-s122-3 swept (m2), "
             "and CONOPS.md section 7's D-13 row is BASELINE on the status page's row DC-10 (m1). Round 5 (the independent "
             "check v2/docs/records/s122/checks/check-s122-4.md): the finder's shapes are wider (TI's single gates, "
             "BAT46W, USBLC6-2SC6, E72-2G4M20S1E, LIS3MDL, Si2300DS, all-digit numbers after a maker's name), and a part "
             "named in a role is judged against the designators whose values state that role (verdicts.check_roles): "
             "v2/docs/records/s122/apply_docs_s122_r5.py corrected V2-SPEC.md line 84 (the TPS22810 called the gate-bias "
             "switch; board D's gate bias is the TLV75801 U15 on PA_KEY and the TPS22810 is U21, the load switch of "
             "+5V_TX) and line 81 (all four rails given to the AP64500; board A's U5 and U7 are LM5176 stages), and in the "
             "same table line 83 (seventeen LEDs) and line 86 (the magnetometer is in the outside pod). Round 6 (the "
             "independent check v2/docs/records/s122/checks/check-s122-5.md, B1): "
             "v2/docs/records/s122/apply_docs_s122_r6.py corrected V2-SPEC.md line 47 (the SA868 named a 1 W part; board "
             "D's U2 is the SA868 VHF 2 W exciter, and the maker's sheet v1.3 gives 31 to 33 dBm on high power and 24 to "
             "26 dBm on low), and every figure-and-unit token on the lines of S-122's closing list is bound to one of its "
             "judgement's own assertions (verdicts.check_figs and close_s122.py's scan). Round 7 (the independent check "
             "v2/docs/records/s122/checks/check-s122-6.md): line 81's 14.4 V node is bound to gen_sch_p.py's declared cell "
             "node CELL4 (the BQ4050 sheet's test condition dropped), a figure is compared by its values in order with "
             "their signs and units, and V2-SPEC.md's correction 36 says the scan reads figures with a unit and spelled "
             "counts (apply_docs_s122_r7.py). This record stays FAIL and waits on S-122; this entry changes no result." % per)
    out = R1.append_entry(out, "CFL-016", entry)
    # CFL-016's notes: m7
    A_ = A
    R1.screen(M7_NOTE, "CFL-016")
    i, j = A_.span(out, "CFL-016")
    blk = out[i:j]
    if blk.count("    notes: >-\n") != 1: refuse("CFL-016's notes block")
    head, tail = blk.split("    notes: >-\n", 1)
    nlines = []
    rest = tail.split("\n")
    k = 0
    while k < len(rest) and rest[k].startswith("      "):
        nlines.append(rest[k].strip()); k += 1
    note_old = " ".join(nlines)
    if "check-int15-1 m7" in note_old: refuse("CFL-016's notes already carry the m7 sentence")
    blk = head + "    notes: >-\n" + A_.fold(note_old + M7_NOTE, 6, 120) + "\n".join(rest[k:])
    out = out[:i] + blk + out[j:]
    # round 7: the follow-up item of the instrument's escape classes, at the next free S number of THIS registry (never
    # hard-coded: the number is read from the open and closed items the script runs on)
    nums = [int(x["id"][2:]) for x in before["open_items"] + before["closed_items"] if re.fullmatch(r"S-\d+", str(x.get("id")))]
    follow = "S-%d" % (max(nums) + 1)
    if any(str(x.get("title", "")).startswith(FOLLOW_MARK) for x in before["open_items"] + before["closed_items"]):
        refuse("the follow-up item of the instrument's escape classes is already in the registry")
    add = S122_ADD4.replace("{FOLLOW}", follow)
    for txt in (add, FOLLOW_TITLE, FOLLOW_WHY): R1.screen(txt, follow)
    ci = out.index("\nclosed_items:\n") + 1
    out = out[:ci] + ("  - id: %s\n    class: SESSION\n    status: OPEN\n    disposition: PROCESS\n    disposition_why: >-\n%s"
                      "    title: >-\n%s" % (follow, A.fold(FOLLOW_WHY, 6, 120), A.fold(FOLLOW_TITLE, 6, 120))) + out[ci:]
    # S-122's title
    R1.screen(add, "S-122")
    i, j = A_.span(out, "S-122")
    blk = out[i:j]
    if "    title: >-\n" not in blk or "Correction at stream s122's round 4" in blk: refuse("S-122's block")
    title = " ".join(l.strip() for l in blk.split("    title: >-\n", 1)[1].split("\n") if l.strip())
    blk = blk.split("    title: >-\n", 1)[0] + "    title: >-\n" + A_.fold(title + add, 6, 120)
    out = out[:i] + blk + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        allowed = {"evidence", "evidence_bound_to"} if rid in touched else set()
        if rid == "CFL-016": allowed = {"evidence", "evidence_bound_to", "notes"}
        if not dd <= allowed: refuse("%s: %s moved" % (rid, dd))
        oe_, ae_ = ob[rid].get("evidence") or [], ab[rid].get("evidence") or []
        if oe_ != ae_[:len(oe_)]: refuse("%s: older entries not kept as a prefix" % rid)
    if " ".join(ab["CFL-016"]["notes"].split()) != " ".join((ob["CFL-016"]["notes"] + M7_NOTE).split()): refuse("CFL-016's notes")
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ai) - set(oi) != {follow} or set(oi) - set(ai) or any(oi[x] != ai[x] for x in oi if x != "S-122"):
        refuse("open items other than S-122 and the new %s moved" % follow)
    fu = ai[follow]
    if (fu.get("disposition") != "PROCESS" or fu.get("class") != "SESSION" or fu.get("status") != "OPEN"
            or " ".join(fu["title"].split()) != " ".join(FOLLOW_TITLE.split())
            or " ".join(fu["disposition_why"].split()) != " ".join(FOLLOW_WHY.split())):
        refuse("%s does not read back" % follow)
    if any(follow in (r.get("waits_on") or []) for r in after["records"]): refuse("a record waits on %s" % follow)
    if " ".join(ai["S-122"]["title"].split()) != " ".join((" ".join(oi["S-122"]["title"].split()) + add).split()):
        refuse("S-122's title")
    if {k: v for k, v in oi["S-122"].items() if k != "title"} != {k: v for k, v in ai["S-122"].items() if k != "title"}:
        refuse("S-122's other fields")
    if before["closed_items"] != after["closed_items"]: refuse("closed items moved")
    top = {k for k in set(before) | set(after) if k not in ("records", "open_items") and before.get(k) != after.get(k)}
    if top: refuse("top-level fields moved: %s" % top)
    # the envelope pin and ENV-001's verified_sha
    oe = "v2/docs/OPERATING-ENVELOPE.md"
    base_bytes = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (BASE, oe)], capture_output=True, check=True).stdout
    oldfull, newfull = hashlib.sha256(base_bytes).hexdigest(), R1.sha_full(oe)
    env = open(ENV, encoding="utf-8").read()
    envy = yaml.safe_load(env)
    if envy.get("document_sha256") != oldfull: refuse("pcb_envelope.yaml does not pin OPERATING-ENVELOPE.md at 1bafab8c")
    doc_txt = open(os.path.join(L.TOP, oe), encoding="utf-8").read()
    nums = set(re.findall(r"(?<![\w.])[-+]?\d+(?:\.\d+)?(?![\w.])",
                          yaml.safe_dump({k: v for k, v in envy.items() if k not in ("document_sha256", "adopted")})))
    base_txt = base_bytes.decode("utf-8")
    lost = sorted(x for x in nums if x.lstrip("+") in base_txt and x.lstrip("+") not in doc_txt)
    if lost: refuse("numbers of the envelope no longer in the document: %s" % lost)
    _o, nl = R1.diff_lines(oe)
    if any(R1.sec_at(R1.sections_of(oe), n) not in ("2",) for n in nl): refuse("the envelope's diff leaves section 2")
    old_line = next(l for l in env.split("\n") if l.startswith("document_sha256:"))
    new_line = ('document_sha256: "%s"   # re-read and re-pinned 29 September 2026 by stream s122\'s round 4 (S-122: '
                'section 2\'s TRACO and Amphenol rows replaced by board E\'s LM5069 and board B\'s TE 2199119-3 with their '
                'makers\' ranges; no number of section 4 changed), before it %s' % (
                    newfull, old_line.split("# ", 1)[1] if "# " in old_line else ""))
    env2 = env.replace(old_line, new_line, 1)
    if yaml.safe_load(env2).get("document_sha256") != newfull: refuse("the envelope pin does not read back")
    cov = open(COV, encoding="utf-8").read()
    if cov.count('verified_sha: "%s"' % oldfull) != 1: refuse("ENV-001's verified_sha")
    cov2 = cov.replace('verified_sha: "%s"' % oldfull, 'verified_sha: "%s"' % newfull, 1)
    if yaml.safe_load(cov) == yaml.safe_load(cov2): refuse("the coverage file did not change")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("the registry re-parse differs")
    open(ENV, "w", encoding="utf-8").write(env2)
    open(COV, "w", encoding="utf-8").write(cov2)
    print("%s: %d records rebound (%s); CFL-016 gained the round 4 inventory entry and the m7 sentence in its notes; "
          "S-122's title gained the round 4 correction; %s opened (the instrument's escape classes, PROCESS); the "
          "envelope and ENV-001 re-pinned to %s" % (
              TAG, len(touched), ", ".join("%s (%s)" % (k, "+".join(v)) for k, v in sorted(touched.items())), follow, newfull[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
