#!/usr/bin/env python3
"""Decision 55 recorded in v2/ecad/tools/pcb_decisions.yaml (MESHSAT-1357, integration set 9, stream s99reg, 29 September
2026). AI engineering text; prototype design, nothing built, ordered or measured.

The decision is stream s99's (v2/docs/records/s99/REGISTRY-DRAFT.md section 2, option B of ANALYSIS.md section 5) with
the field changes of stream s99a (v2/docs/records/s99a/REGISTRY-DRAFT.md section 2): the outcome at 5.002 V nominal on
56.2k over 10.7k, 4.872 to 5.133 V, board D's 5.23 V standing; 6.9142 A declared with a margin of 0.142697 A;
reversed_by adds Q32's restoration; evidence adds SLVSET8A p.28, SLUSEA4D p.6, SLES230A 7.3 p.5 and
records/s99a/u41_divider.out. It carries the fields every SESSION decision of the file carries (decisions 48 to 54):
status ruled, authority SESSION, authority_why, ruled_by SESSION, ruled_on, outcome, reversed_by, ask, recommendation,
evidence, blocks, holds_nothing_today. It is the session's under the owner's ruling of 21 September 2026 (engineering
decisions are the session's) and his standing rule of 26 September 2026; none of it is the owner's.

Every record of pcb_requirements.yaml bound to pcb_decisions.yaml by its sha256/16 (CFL-016 on this line) is rebound to
the new sha256/16 with one evidence entry saying what changed and that the decisions the record reads are unchanged,
which is asserted on the parsed file. Both texts are built and checked before either is written.

AFTER IT the integrator owes: `decisions_render.py` (v2/docs/OWNER-DECISIONS-OPEN.md lists every decision that is not
open in its "Closed, for the record" table, so decision 55 adds a row and `--check` reads the page stale until it is
re-rendered), and `rules_render.py --requirements` for the trace page (the rebind changed the registry). Refuses a
second run (decision 55 present). Usage: python3 <this file> [--root <tree>] [--check]."""
import datetime, os, sys, textwrap

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _int10 as H
from _int10 import A

NAME = "apply_decision_55"
DEC = "v2/ecad/tools/pcb_decisions.yaml"
PAGE = "v2/docs/OWNER-DECISIONS-OPEN.md"
N = 55
DAY = "2026-09-28"
ROW = {
    "title": "board A: the D8 mezzanine leaves the +5V_DEV LM5176 stage for its own 5 V buck from VBAT",
    "authority_why": (
        "it changes no line the never-auto floor protects (no class of tools/reserved.json names gen_sch_a.py), spends "
        "nothing the owner decides (ten new component references inside the board's BOM; no purchase; the XAL6060-682ME "
        "order code and board A's use of C705784 and C861078 still need the parts stream's certification entry), changes "
        "no claim about the kit (the mezzanine keeps its 5.0 V and its 6 percent budget), and accepts no residual risk a "
        "measurement in this tree cannot remove (the remaining child-peak tier is board B's declarations and the bench "
        "test PT-4). The divider is the session's too: board D's alternative, raising its v_work to 5.29 V, is refused on "
        "the PCM2912A's 5.25 V recommended maximum (TI SLES230A 7.3 p.5)."),
    "outcome": (
        "THE MEZZANINE'S 5 V IS ITS OWN RAIL, +5V_D8IN, FROM A TPS62933 (U41) ON VBAT AT 5.002 V NOMINAL (56.2k / 10.7k, "
        "BOTH 0.1 PERCENT 25 ppm/C, THE CODES C705784 AND C861078 BOARD D ALREADY USES AS R80 AND R81), 4.872 TO 5.133 V "
        "OVER EVERY TOLERANCE, SO BOARD D'S DECLARED v_work OF 5.23 V ON +5V_D8 STANDS; 6.8 uH XAL6060-682ME, 500 kHz, "
        "ENABLED WITH THE 3.3 V LOGIC (RAIL_EN), AND U23 STAYS THE MEZZANINE'S EFUSE (D8_EN, 2.0 A, OVLO) FED FROM IT. "
        "The +5V_DEV stage's coincident PS-ALLTX demand returns to board B plus the wall host port: 6.9142 A declared (the "
        "wall port at U32's corrected 0.9142 A, TPS2596 equation 7), 0.142697 A under the average loop's conditional "
        "minimum of 7.056897 A, and 5.942235 A with the makers' figures, 1.114661 A under it (v2/docs/records/s99/ANALYSIS.md "
        "sections 3 to 5, dev_stage.out; v2/docs/records/s99a/README.md section 2); the tier with board B's declared child "
        "peaks, 8.171220 A, is above the minimum and stays open under S-99. The stage itself is unchanged: R43 6 mOhm stays "
        "because the loop's 9.6 A maximum must stay under the JST-VH lead's 10 A rating."),
    "reversed_by": (
        "delete U41, L13, C227 to C232, R217 and R218, return U23's input to +5V_DEV, restore the +5V_DEV loads (U23 1.0 A, "
        "as after S-98) and VBAT's map (no U41, and restore Q32's VBAT share to 2.0 A: it is 1.61 A after the split, U41 "
        "carrying 0.4 A), and re-take PWR-001 and INT-001: the five replacements of "
        "v2/docs/records/s99a/apply_d8_split_rebased.py in reverse, with the VBAT change of stream s99a's commit 80ebde44."),
    "ask": (
        "carry the mezzanine on the device rail (declare the 8.9 A bound with the fold-back named), re-rate the stage's "
        "average loop (5 or 5.6 mOhm), interlock the wall host port with the outlets, or give the mezzanine its own "
        "converter"),
    "recommendation": (
        "THE OWN CONVERTER. Both B and B plus the wall-port interlock remain standing configurations. Under the owner's "
        "standing rule of 26 September, SESSION may choose B because it meets the conditional declared demand without "
        "moving the lead protection point and preserves console availability. The interlock changes console behaviour and "
        "stays a fallback. M/P evidence, timing, collapse/recovery and thermal verification remain open; this choice is not "
        "acceptance of residual risk."),
    "evidence": (
        "board A's netlist at 2b7c9374 (sha256 0a2b5908...), the intents of boards A, B and D (sha256 3422910a..., "
        "96ee391b..., 8d9f3b22...), TI SNVSAI1D pp.3 to 7, 16 to 17, 23 to 26, TI SLPS414B p.3, Coilcraft 804-1 and 887-1, "
        "Vishay 30100 pp.1 to 2, TI SLVSET8A printed p.28 (equation 7 and its worked example), TI SLUSEA4D p.6 (VFB and "
        "IFB), TI SLES230A 7.3 p.5 (PCM2912A VBUS 4.35 to 5.25 V), NiceRF SA868 v1.3 p.4, Ebyte E22-900M30S v1.20, Ground "
        "Control's RockBLOCK 9704 hardware page (snapshot 2026-09-27), MyriadRF's LimeSDR Mini pages, Microchip "
        "DS00002330D p.169; v2/docs/records/s99/dev_stage.py (reproduced byte for byte, inputs refused by name when "
        "changed); v2/docs/records/s99a/u41_divider.out; the independent AI reviews v2/docs/records/s99/checks/"
        "check-2-claude.md and the check of stream s99a (accepted, no blocking item)."),
    "blocks": {},
    "holds_nothing_today": (
        "it releases no rule-board pair: PWR-001 and INT-001 on board A are re-taken after the regeneration; REQ-018 stays "
        "NOT_JUDGED under FEA-004 and S-99's closure conditions."),
}
ORDER = ("title", "asked", "status", "authority", "authority_why", "ruled_by", "ruled_on", "outcome", "reversed_by", "ask",
         "recommendation", "evidence", "blocks", "holds_nothing_today")


def folded(key, text):
    body = textwrap.wrap(text, width=104, break_long_words=False, break_on_hyphens=False)
    return "    %s: >-\n%s\n" % (key, "\n".join("      " + ln for ln in body))


def row_text():
    out = "  - n: %d\n" % N
    for k in ORDER:
        if k == "asked": out += "    asked: %s\n" % DAY
        elif k == "status": out += "    status: ruled\n"
        elif k == "authority": out += "    authority: SESSION\n"
        elif k == "ruled_by": out += "    ruled_by: SESSION\n"
        elif k == "ruled_on": out += "    ruled_on: %s\n" % DAY
        elif k == "blocks": out += "    blocks: {}\n"
        else: out += folded(k, ROW[k])
    return out


def main(argv):
    root = H.root_of(argv)
    s = H.read(root, DEC)
    before = yaml.safe_load(s)
    old = before["decisions"]
    if any(d.get("n") == N for d in old) or any(d.get("title") == ROW["title"] for d in old): H.refuse(NAME, "decision 55 is in the file (a second run)")
    if max(d["n"] for d in old) != N - 1: H.refuse(NAME, "decision %d is not the next number (the highest is %d)" % (N, max(d["n"] for d in old)))
    for k, v in ROW.items():
        if isinstance(v, str):
            A.screen(v, "decision 55 %s" % k)
            if v != H.one_space(v): H.refuse(NAME, "decision 55 %s carries a double space" % k)
    if len(ROW["reversed_by"]) <= 60 or ".py" not in ROW["reversed_by"]: H.refuse(NAME, "reversed_by names no script")
    if not s.endswith("\n"): H.refuse(NAME, "pcb_decisions.yaml does not end in a newline")
    out = s + row_text()
    d = yaml.safe_load(out)
    if set(d) != set(before) or any(d[k] != before[k] for k in before if k != "decisions"): H.refuse(NAME, "a top-level key changed")
    new = d["decisions"]
    if new[:len(old)] != old or len(new) != len(old) + 1: H.refuse(NAME, "a decision the file held changed")
    x = new[-1]
    day = datetime.date.fromisoformat(DAY)
    if not (x["n"] == N and x["status"] == "ruled" and x["authority"] == "SESSION" and x["ruled_by"] == "SESSION"
            and x["asked"] == day and x["ruled_on"] == day and x["blocks"] == {}):
        H.refuse(NAME, "decision 55's fixed fields did not round-trip: %s" % {k: x.get(k) for k in ("n", "status", "authority", "ruled_by", "asked", "ruled_on")})
    for k in ORDER:
        if k in ROW and k != "blocks" and x[k] != ROW[k]: H.refuse(NAME, "decision 55's %s did not round-trip" % k)
    if list(x) != ["n"] + list(ORDER): H.refuse(NAME, "decision 55's keys are %s" % list(x))

    # the rebind of every record bound to this file
    was16, now16 = H.sha16_text(s), H.sha16_text(out)
    rq = H.read(root, H.REG)
    rb = yaml.safe_load(rq)
    bound = H.bound_records(rb, DEC)
    stale = {r: v for r, v in bound.items() if v != was16}
    if stale: H.refuse(NAME, "records bound to another version of %s than the tree's %s: %s; re-read them first" % (DEC, was16, stale))
    rq2 = rq
    for rid in bound:
        rec = [r for r in rb["records"] if r["id"] == rid][0]
        cited = sorted(int(v) for v in ((rec.get("satisfied_by") or {}).get("decisions") or []))
        if N in cited: H.refuse(NAME, "%s reads decision 55 itself: re-read it by hand" % rid)
        entry = ("v2/ecad/tools/pcb_decisions.yaml re-read at integration set 9 (stream s99reg's "
                 "v2/docs/records/int10/apply_decision_55.py, MESHSAT-1357, 29 September 2026): decision 55 (board A's D8 "
                 "mezzanine on its own 5 V buck, a SESSION ruling of 28 September 2026) is APPENDED after the last decision "
                 "the file held; every decision the file held is unchanged and in the same order, which the script asserts "
                 "on the parsed file before it writes%s; so this reading stands on v2/ecad/tools/pcb_decisions.yaml@%s"
                 % ((", decisions %s, which this record reads, among them" % " and ".join(str(v) for v in cited)) if cited else "", now16))
        A.screen(entry, "%s's entry" % rid)
        i, j = A.span(rq2, rid)
        r = H.add_evidence(NAME, rq2[i:j], rid, entry)
        r = H.rebind_line(NAME, r, rid, DEC, was16, now16)
        rq2 = rq2[:i] + r + rq2[j:]
    if bound:
        after = yaml.safe_load(rq2)
        H.compare_records(NAME, rb, after, {rid: {"evidence", "evidence_bound_to"} for rid in bound})
        for sec in rb:
            if sec != "records" and rb[sec] != after[sec]: H.refuse(NAME, "registry section %s changed" % sec)
        ra = {r["id"]: r for r in after["records"]}
        for rid in bound:
            old_r = [r for r in rb["records"] if r["id"] == rid][0]
            if ra[rid]["evidence"][:-1] != old_r["evidence"]: H.refuse(NAME, "%s's earlier evidence moved" % rid)
            if ra[rid]["evidence_bound_to"] != [b if b != "%s@%s" % (DEC, was16) else "%s@%s" % (DEC, now16) for b in old_r["evidence_bound_to"]]:
                H.refuse(NAME, "%s's bindings are not the old ones with this file rebound" % rid)
    page = H.read(root, PAGE)
    owed = ("OWED: decisions_render.py (the page's closed table has %s row for decision 55 today, so --check reads it stale "
            "until it is re-rendered)%s" % ("no" if "\n| 55 |" not in page else "ALREADY A", "; rules_render.py --requirements (the "
            "registry changed by the rebind)" if bound else ""))
    if "\n| 55 |" in page: H.refuse(NAME, "%s already carries a row for decision 55: re-read it" % PAGE)
    msg = ("decision 55 appended (SESSION, ruled %s); %s@%s -> @%s; %s" % (DAY, DEC, was16, now16,
           ("%d record(s) rebound with an evidence entry: %s" % (len(bound), ", ".join(sorted(bound)))) if bound else "no record is bound to it"))
    if "--check" in argv:
        print("%s: CHECK ONLY, nothing written: %s\n%s" % (NAME, msg, owed)); return 0
    H.write(root, DEC, out)
    if bound: H.write(root, H.REG, rq2)
    if H.sha16_text(H.read(root, DEC)) != now16 or yaml.safe_load(H.read(root, DEC)) != d: H.refuse(NAME, "pcb_decisions.yaml read back differs")
    if bound and H.read(root, H.REG) != rq2: H.refuse(NAME, "the registry read back differs")
    print("%s: %s\n%s" % (NAME, msg, owed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
