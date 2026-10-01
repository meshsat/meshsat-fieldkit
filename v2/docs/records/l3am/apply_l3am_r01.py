#!/usr/bin/env python3
"""L3-R01 of the independent review the owner relayed on 1 October 2026, with the finding carried from the engineering
collaborator's layer 4 check of 30 September 2026 (MESHSAT-1357; v2/docs/records/l3am/DISPOSITIONS.md): label layer 3's
solar-assisted figures with what they were computed with.

The figures (the kit stopping at 05 UTC of the first night; 266.7 / 494.7 Wh unserved as drawn and 102.2 / 165.7 Wh on
the hypothetical corrected path at 48 / 72 hours; 0 of 864 September windows) were computed with proposal P-03's array,
400 Wp in 2S2P into a 200 W stage window (v2/docs/records/l3batt/runtime.out lines 27 to 28), on proposal P-01's store,
and retained REQ-016 (D-34) does not admit that array. The inherited counter they come from
(v2/docs/records/a1elec/energy_two_pack.py lines 257 to 280) credits the sun twice in an hour the kit is stopped: with the
load at 0 W the hour's solar power is subtracted from the counted shortfall (line 259) and the same power charges the packs
(lines 262 to 280), so the unserved figures are understated. They are labelled as historical results of P-03 with an
understated shortfall; the retained window's result awaits layer 4 task L4-E2, whose record will be
v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md (cited as pending, not read). The evidence and the figures stay as written;
the conclusion is unchanged: REQ-072 reads FAIL at desk, DR-01 stands.

What it writes, each located by its own words and asserted once:
  - l3r2.yaml: `solar_case`, the machine-readable case (pack, load profile, array, voltage window, stage limit, the
    retained window, the figures, what is understated and what is pending), after `baseline_statement`, which is kept
    byte for byte; render_l3r2.py verifies it against runtime.out and ARRAY.md and prints its label wherever a page
    states such a figure (section 2.3, DR-01, the rows, the feasibility items, the four cases, row L3-OD7, the basis);
  - the registry: one dated sentence closing REQ-072's notes (its evidence entry is kept as written);
  - OWNER-INSTRUCTION-2026-09-30.md: the current owner brief's honest state names the case beside its stop hour;
  - handover/DEFINITION-STATUS.md: one paragraph after the rows the draft proposes (the approved change record and
    draft are not rewritten, D-38), and CFL-016's binding to that page carried with one evidence entry, as the round 5
    fix round did (the change inserts lines only; the section the s122 verdicts read is byte identical).
It refuses a second run. No dash character is written.

Usage: python3 v2/docs/records/l3am/apply_l3am_r01.py [--check]"""
import hashlib
import os
import sys
import textwrap

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l3amlib as L  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r5"))
import apply_definition_status_l3r5 as DS  # noqa: E402

BRIEF = os.path.join(L.TOP, "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md")
STATUS = os.path.join(L.TOP, "v2/docs/handover/DEFINITION-STATUS.md")
STATUS_REL = "v2/docs/handover/DEFINITION-STATUS.md"
RUNTIME = "v2/docs/records/l3batt/runtime.out"
ARRAY = "v2/docs/records/a1solar/ARRAY.md"
MODEL = "v2/docs/records/a1elec/energy_two_pack.py"
PENDING = "v2/docs/records/l4e/L4-ENERGY-ARCHITECTURE.md"
LABEL = ("historical results of proposal P-03's array (400 Wp in 2S2P into the model's 200 W stage window), which "
         "retained REQ-016 (D-34) does not admit, their unserved energy understated")
FIGS = ("the stop at 05 UTC of the first night, 266.7 / 494.7 Wh unserved as drawn, 102.2 / 165.7 Wh on the "
        "hypothetical corrected path at 48 / 72 hours, 0 of 864 windows")
BRIEF_OLD = "(11 to 23 hours), as drawn and on the hypothetical corrected path, and D-06's pack alone"
BRIEF_NEW = ("(11 to 23 hours), as drawn and on the hypothetical corrected path (historical results of proposal P-03's "
             "array, 400 Wp in 2S2P into a 200 W stage, which REQ-016 does not admit, the unserved energy understated; the "
             "retained window's result is layer 4 task L4-E2's; L3-R01), and D-06's pack alone")
STATUS_BEFORE = "\n## What the two documents carried at their baselines\n"


def sha16(path):
    return hashlib.sha256(open(os.path.join(L.TOP, path), "rb").read()).hexdigest()[:16]


def case_block():
    return (
        "# L3-R01 of the independent review the owner relayed on 1 October 2026 (v2/docs/records/l3am/): what every layer 3\n"
        "# solar-assisted figure was computed with. render_l3r2.solar_case verifies it (the quote at its lines of runtime.out,\n"
        "# the window's in ARRAY.md, the figures against runtime.out by exact keys, the retained window in REQ-016's statement)\n"
        "# and prints its label wherever a page states such a figure (solar_guard refuses a page that does not).\n"
        "solar_case:\n"
        "  id: SAC-P03\n"
        "  state: HISTORICAL\n"
        "  finding: L3-R01\n"
        "  record: v2/docs/records/l3am/DISPOSITIONS.md\n"
        "  relayed_on_text: \"1 October 2026\"\n"
        "  proposal: P-03\n"
        "  store_proposal: P-01\n"
        "  short: \"400 Wp in 2S2P into the model's 200 W stage window\"\n"
        "  source: {record: %s, sha16: %s, lines: \"27 to 28\"}\n"
        "  pack: \"proposal P-01's store (Option A(i)): a base 4S6P and a lid 4S9P of the Samsung INR18650-35E, 544.4 Wh "
        "usable aged at +20 C; at the start of the solar-assisted runs 218.4 Wh in the base at +20 C and 284.2 Wh in the lid "
        "at 13.23 C, 502.6 Wh together, both full and aged\"\n"
        "  load_profile: \"REQ-072's objective_profile: PS-IDLE-SPEC, 42.8 W at the pack terminals over its 39 loads, HF "
        "available and not receiving, the tablet not charged; SC-37's mean September day at Leiden on one plane, 40 degrees "
        "facing south, TYP (WAB a sensitivity); starts at 06 and 18 UTC\"\n"
        "  array: \"proposal P-03's: 400 Wp, four Renogy RNG-100DB-H panels in 2S2P (runtime.out section 2; ENERGY-BASIS.md "
        "section 6b)\"\n"
        "  voltage_window: \"the 2S2P array's: the stage's input held at the FBIN set point, 34.29 V in TYP and 33.05 or "
        "35.57 V in WAB (ENERGY-BASIS.md section 6b); operating 26 to 44 V at maximum power over the envelope and up to 51.3 V "
        "open circuit at -20 C cells (ARRAY.md section 3)\"\n"
        "  window_source: {record: %s, sha16: %s, quote: \"operating 26 to 44 V at maximum power over the envelope (section "
        "1), the set point held whenever the stage asks more than the array gives; open circuit up to 51.3 V at -20 C cells\"}\n"
        "  stage_limit: \"a 200 W stage window, the energy model's clip; board E as generated implements no 200 W limit "
        "(ARRAY.md section 3)\"\n"
        "  retained: {record: REQ-016, ruling: D-34, decides: \"L3-OD3:unchanged\", quotes: [\"an open-circuit voltage of at most 25 V at the panel's coldest "
        "operating temperature\", \"the panel held at 17.6 V by the stage's input regulation\", \"at most 100 W into the "
        "stage\"]}\n"
        "  figures: {stops: \"05 UTC of the first night\", drawn_unserved_48_72: \"266.7 / 494.7\", corrected_unserved_48_72: "
        "\"102.2 / 165.7\", windows: \"0 of 864\"}\n"
        "  understated: \"the inherited counter of %s (lines 257 to 280, sha256/16 %s) credits the sun twice in an hour the "
        "kit is stopped: with the load at 0 W the hour's solar power is subtracted from the counted shortfall (line 259) and "
        "the same power charges the packs (lines 262 to 280). The engineering collaborator's layer 4 check of 30 September "
        "2026 found it; layer 4 recomputes the figures.\"\n"
        "  pending: {task: L4-E2, record: %s}\n"
        "  conclusion: \"The conclusion stands: REQ-072 reads FAIL at desk, design risk DR-01.\"\n"
        "  design_risks: [DR-01]\n" % (RUNTIME, sha16(RUNTIME), ARRAY, sha16(ARRAY), MODEL, sha16(MODEL), PENDING))


def req072_sentence():
    return ("Amended on 1 October 2026 (finding L3-R01 of the independent review the owner relayed, "
            "v2/docs/records/l3am/DISPOSITIONS.md): the solar-assisted figures of this record's latest evidence entry (%s) "
            "are %s: %s lines 257 to 280 credit the sun twice in an hour the kit is stopped (the engineering collaborator's "
            "layer 4 check of 30 September 2026). The entry is kept as written; the result on the retained window awaits "
            "layer 4 task L4-E2 (%s, pending). REQ-072 reads FAIL at desk either way (DR-01)." % (FIGS, LABEL, MODEL, PENDING))


def status_paragraph():
    return ("**The solar-assisted figures in the row DC-L3-M1 above and in the draft's passage S03** (%s) are %s (finding "
            "L3-R01 of the independent review the owner relayed on 1 October 2026, with the engineering collaborator's layer "
            "4 check of 30 September 2026; `handover/layer3/REQUIREMENTS-L3-R2.md` section 2.3 states the case, "
            "`v2/docs/records/l3am/DISPOSITIONS.md` the disposition). The approved change record and draft are not rewritten "
            "(D-38): the re-stamp (L3-C63) carries this label into `CONOPS.md` and `PRODUCT-BRIEF.md`, and until then it "
            "reads beside them. The result on the retained window awaits layer 4 task L4-E2 (`%s`, pending)." % (
                FIGS, LABEL, PENDING))


def rebind(raw, old_sha, new_sha, added):
    want = "%s@%s" % (STATUS_REL, old_sha)
    entry = ("v2/docs/handover/DEFINITION-STATUS.md re-read at the layer 3 amendment (MESHSAT-1357, 1 October 2026; "
             "v2/docs/records/l3am/apply_l3am_r01.py, %s to %s): the change inserts %d lines and removes none, one "
             "paragraph after the rows the draft proposes, labelling the solar-assisted figures of row DC-L3-M1 and of the "
             "draft's passage S03 (finding L3-R01); the section of CONOPS's current circuit values, the only section of this "
             "page the s122 verdicts read, is byte-identical, its DC rows unchanged; none of the places this record's "
             "evidence names in this document is among the changed ones. This entry does not re-read the rest of this "
             "record's argument; rebound to %s. This entry changes no result." % (old_sha, new_sha, added, new_sha))
    L.screen(entry, "CFL-016's entry")

    def f(block):
        if block.count('      - "%s"' % want) != 1: L.refuse("CFL-016's binding line to %s is not in its block once" % want)
        block = block.replace('      - "%s"' % want, '      - "%s@%s"' % (STATUS_REL, new_sha))
        return L.E.add_list_entry(block, "evidence", entry)
    return L.E.replace_entry(raw, "CFL-016", f, "records")


def build():
    data_old = open(L.DATA, encoding="utf-8").read()
    reg_old = open(L.REGISTRY, encoding="utf-8").read()
    brief_old = open(BRIEF, encoding="utf-8").read()
    status_old = open(STATUS, encoding="utf-8").read()
    if L.E.parse(data_old).get("solar_case"): L.refuse("solar_case is filed: this script has run")
    # l3r2.yaml: the case after baseline_statement (kept byte for byte)
    blk = case_block()
    L.screen(blk, "solar_case")
    lines = data_old.split("\n")
    k = [i for i, l in enumerate(lines) if l.startswith("baseline_statement:")]
    if len(k) != 1: L.refuse("l3r2.yaml does not hold one baseline_statement line")
    data_new = "\n".join(lines[:k[0] + 1] + blk.rstrip("\n").split("\n") + lines[k[0] + 1:])
    a, b = L.only_keys_changed(data_old, data_new, {"solar_case": "added"})
    if a["baseline_statement"] != b["baseline_statement"]: L.refuse("the baseline statement moved")
    # the registry: REQ-072's notes, one sentence
    s = req072_sentence()
    L.screen(s, "REQ-072's notes")
    reg_new = L.E.replace_entry(reg_old, "REQ-072", lambda blk_: L.E.append_folded(blk_, "notes", s), "records")
    # the brief's honest state: the lines from the paragraph's head to the one that ends the phrase are re-wrapped at 120
    # columns with the label in them; every other line of the file stays byte for byte
    i = brief_old.index("**The honest state (D-28, D-31).**")
    lines = brief_old[i:].split("\n")
    k = next(n for n in range(len(lines)) if BRIEF_OLD in " ".join(" ".join(lines[:n + 1]).split()))
    chunk = L.once(" ".join(" ".join(lines[:k + 1]).split()), BRIEF_OLD, BRIEF_NEW, "the brief's honest state")
    L.screen(BRIEF_NEW, "the brief's label")
    wrapped = textwrap.wrap(chunk, 120, break_on_hyphens=False, break_long_words=False)
    brief_new = brief_old[:i] + "\n".join(wrapped + lines[k + 1:])
    h = brief_new.index("## Current owner brief"); e = brief_new.index("\n## ", h + 5)
    n = len(brief_new[h:e].strip().split("\n"))
    if n > 55: L.refuse("the current owner brief would run to %d lines (at most 55)" % n)
    if " ".join(brief_new.split()).replace(BRIEF_NEW, "") != " ".join(brief_old.split()).replace(BRIEF_OLD, ""):
        L.refuse("the brief changed beyond the honest state's label")
    # DEFINITION-STATUS.md: one paragraph after the proposed rows, and CFL-016 rebound
    sp = status_paragraph()
    L.screen(sp, "the status paragraph")
    status_new = L.once(status_old, STATUS_BEFORE, "\n" + sp + "\n" + STATUS_BEFORE, "DEFINITION-STATUS.md")
    if not DS.only_inserts(status_old, status_new): L.refuse("the status page change removes or reorders a line")
    if DS.status_section(status_old) != DS.status_section(status_new): L.refuse("the section of CONOPS's current values changed")
    h16 = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]
    added = len(status_new.split("\n")) - len(status_old.split("\n"))
    reg_new = rebind(reg_new, h16(status_old), h16(status_new), added)
    L.only_fields_changed(reg_old, reg_new, {("records", "REQ-072"): ["notes"],
                                             ("records", "CFL-016"): ["evidence", "evidence_bound_to"]})
    return (data_old, data_new), (reg_old, reg_new), (brief_old, brief_new), (status_old, status_new)


def main(argv):
    try:
        d, r, b, s = build()
    except L.Refused as e:
        print("apply_l3am_r01: REFUSED: %s" % e); return 2
    print("apply_l3am_r01: solar_case filed; REQ-072's notes, the owner brief's honest state and DEFINITION-STATUS.md "
          "labelled; CFL-016 rebound%s" % (" (check only, nothing written)" if "--check" in argv else ""))
    if "--check" in argv: return 0
    L.write(BRIEF, *b)
    L.write(STATUS, *s)
    L.write(L.DATA, *d)
    L.write(L.REGISTRY, *r)
    L.validate_registry(r[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
