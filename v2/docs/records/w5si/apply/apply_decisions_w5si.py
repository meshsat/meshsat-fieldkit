#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, MESHSAT-1357, layer 9): the session decisions
of this stream as rows of v2/ecad/tools/pcb_decisions.yaml. That file is the integrator's; this script makes the change
and the integrator runs it, or does not: the independent check asked that it be CONSIDERED, because three of the
decisions change what rule SI-001 counts as decided and until now they were written only in a data file's header.

WHAT IT ADDS: four rows, appended after the last decision, numbered from the NEXT FREE number of the tree it runs in
(other streams of this wave take numbers too, so none is typed here). Each is `status: ruled`, `authority: SESSION`,
with authority_why, ruled_by, ruled_on, outcome and reversed_by, under the owner's ruling of 21 September 2026
(engineering decisions are the session's) and his standing rule of 26 September 2026. None is the owner's.

  A  what counts as a driver's edge, and which edge governs a net      (ER-D8, ER-D9, ER-D12 as corrected, ER-D13)
  B  a specification's minimum, and the two edges of an open-drain net (ER-D14)
  C  board B's RF switch ports, and BOB's class                        (W5SI-D1, W5SI-D2 as replaced)
  D  the power-stage nodes stay on their bound until a rule covers them (W5SI-D3)

HOW: the rows are appended as text in the file's own style; the result is parsed and COMPARED WITH THE OLD ONE AS
STRUCTURE before anything is written: every decision the file held is there, unchanged and in the same order, and
exactly four follow it. A second run is refused.

AFTER IT, the integrator owes what any new decision owes: v2/docs/OWNER-DECISIONS-OPEN.md is generated from this file
(decisions_render.py) and a test refuses a stale page.

Applied by the integrator on the integrated tree, from anywhere:
    python3 v2/docs/records/w5si/apply/apply_decisions_w5si.py [--root <tree>] [--dry-run]
"""
import os, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
if "--root" in sys.argv: ROOT = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
TARGET = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_decisions.yaml")

WHY = ("it changes no line the never-auto floor protects, spends nothing, claims nothing new about the kit and accepts no "
       "residual risk that a measurement in this tree could remove: ")
ALL = ["a", "b", "c", "d", "e", "p"]
ROWS = [
    {"title": "rule SI-001: what counts as a driver's edge, and which edge governs a net",
     "authority_why": WHY + "it makes SI-001's reading STRICTER (40 nets that read as held by a maker's figure read as decided "
                            "by a bound) and turns no reading towards a pass. SI-001's readings were INCONCLUSIVE on all six "
                            "boards before it and are INCONCLUSIVE after it.",
     "outcome": "ONLY A PUBLISHED MINIMUM IS A MAKER'S FIGURE, AND ONE DRIVER WITHOUT ONE DECIDES THE NET. A driver's edge is a "
                "maker's IBIS model at its fastest corner, a minimum the maker prints in its own table, or a specification's "
                "minimum the part's own datasheet claims; a typical or a maximum is refused; where a maker publishes none the "
                "bound is instantaneous and is named a bound. The governing edge of a net is the fastest edge any driver on it "
                "can produce, so a net that carries even one driver with no published minimum is decided by a bound, whatever "
                "the makers of the other drivers publish. A layout-bound net a bound decides is named BOUND_DECIDES and holds "
                "the reading INCONCLUSIVE. An answered net decided by a bound counts as decided, under the bound's count. "
                "tools/pcb_edge_rates.yaml holds the figures (ER-D8, ER-D9, ER-D12, ER-D13 in its header) and "
                "tools/edge_length.py is the criterion (net_edge).",
     "reversed_by": "in tools/edge_length.py, make net_edge take the fastest candidate's kind as the net's and restore the "
                    "maker-held test the first pass had; 40 nets then read as held by a maker's figure again, which the "
                    "independent check of 27 September 2026 refused.",
     "ask": "count a layout-bound net as held by a maker's figure when ANY maker's figure on it gives a length, or only when "
            "EVERY driver on it has a published minimum",
     "recommendation": "ONLY WHEN EVERY DRIVER HAS ONE. The critical length is what a layout is handed; with a driver of "
                       "unknown edge on the net that length is the bound's, and naming the net by another driver's figure "
                       "hands a layout a number that does not govern it.",
     "evidence": "the independent check (AI review) of the first pass, 27 September 2026, from its own run of the tool on the "
                 "netlists at c23c5e76: 40 of the 83 nets the records called maker-held had a bound as their fastest "
                 "candidate and a critical length of 0.0 mm in the tool's own table (v2/docs/records/w5si/check-1/). After "
                 "the change the readings hold 43 nets by a maker's figure and 281 by a bound, of 324 layout-bound "
                 "(v2/docs/records/w5si/readings/si001-c23c5e76.txt); the same on the set 6 netlists.",
     "blocks": {},
     "holds_nothing_today": "it holds no rule-board pair that was not held: SI-001 read INCONCLUSIVE on all six boards before "
                            "it. What it changes is which nets a reading names under which figure."},
    {"title": "rule SI-001: a specification's minimum binds only a part that claims it, and an open-drain net's fall governs",
     "authority_why": WHY + "it admits one published figure (10 ns for one pin of one part) on the maker's own written claim and "
                            "refuses the same figure for three parts that make no such claim, and it moves no net from a bound "
                            "to a maker's figure.",
     "outcome": "AN OPEN-DRAIN NET HAS TWO EDGES AND THE FALL GOVERNS. The fall is the driver's pull-down; the rise is the "
                "pull-up charging the net (0.8473 Rp Cb, UM10204 Rev. 6 section 7.1) and is stated beside it, never taken as "
                "the governing edge. UM10204 Rev. 6's minimum output fall (Table 9, Fast-mode, 20 ns x VDD / 5.5 V; Table "
                "11, Hs-mode, 10 ns; Standard-mode states none) is a published figure ONLY for a part whose own datasheet "
                "claims the specification's timing. Of the parts on the kit bus the KSZ9897R does (DS00002330 section 6.4). "
                "The DS3231 and the TPS23861 print their own minimum. The BQ25731, the ATECC608B and the VEML7700 call "
                "themselves compatible and print only a maximum or an input requirement, so they keep their bound, and the "
                "RP2040, the bus master, publishes nothing: SCL and SDA stay decided by a bound on all four boards.",
     "reversed_by": "remove the STANDARD row from the KSZ9897R's record in tools/pcb_edge_rates.yaml; its data pin takes the "
                    "instantaneous bound again and no count moves.",
     "ask": "give every part on an I2C bus the specification's minimum fall, give it to none, or give it to the parts whose "
            "own datasheets claim the specification",
     "recommendation": "TO THE PARTS THAT CLAIM IT. A specification binds a part through the maker's claim and through "
                       "nothing else, and Standard-mode, which this bus runs, states no minimum at all.",
     "evidence": "UM10204 Rev. 6 pages 47, 51 and 55, and each maker's own words, cited with page and sha256/16 in "
                 "tools/pcb_edge_rates.yaml and checked on every run of the tool.",
     "blocks": {},
     "holds_nothing_today": "no count moves by it: the kit bus is decided by a bound with or without the one figure it admits."},
    {"title": "board B: the RF switch ports are RF lines, and BOB keeps its class until a class that fits it is ruled",
     "authority_why": WHY + "it corrects two declarations to say what the nets are and widens no rule's exemption: BOB stays in "
                            "the class it had, which both return rules judge.",
     "outcome": "SW?_IN AND SW?_O? ARE DECLARED RF LINES; BOB KEEPS CLOCKED_DIGITAL AND GETS A TRUE BASIS. The two patterns "
                "match only the SKY13351 antenna changeovers' ports; they become HIGH_SPEED_DIGITAL in boards/b.json and, "
                "with the card RF lines and GNSS_RF_IN, take the RF net class in gen_pcb_b3.py. BOB is the common node of "
                "the wall Ethernet port's line-side termination. No signal class asks the right question of it: three ask "
                "for an adjacent reference, which the switch maker's checklist says to keep away from the line side, and "
                "the fourth is skipped by return_via.py and ref_change.py. So its class is left as committed, and the class "
                "that fits is PROPOSED in v2/docs/records/w5si/F-BOB-common-mode-termination.md.",
     "reversed_by": "restore the three entries of boards/b.json and the three classes and remove the added pattern in "
                    "gen_pcb_b3.py (v2/docs/records/w5si/apply/apply_board_b_declarations.py names them).",
     "ask": "move BOB to LOW_SPEED_OR_DC, move it to a faster class, or leave its class and propose the class that fits",
     "recommendation": "LEAVE IT AND PROPOSE. A class is the scope of the return rules, and a stream that corrects a basis "
                       "has no business narrowing or widening a rule's scope on the way.",
     "evidence": "the committed netlist of board B (sha256/16 8b78c59754a6a0c7), gen_sch_b.py line 1151, and the makers' "
                 "words in v2/docs/records/w5si/evidence/cable-side-termination.yaml, held to their pages.",
     "blocks": {},
     "holds_nothing_today": "the net classes take effect at board B's next layout generation; no reading of the declared "
                            "phase moves."},
    {"title": "rule SI-001: the power-stage nodes stay on their bound until a rule covers them",
     "authority_why": WHY + "it declines to write a declaration and so leaves 82 nets holding SI-001's reading, which is the "
                            "stricter of the two options.",
     "outcome": "NO EDGE_ALLOW DECLARATION IS WRITTEN FOR A GATE, BOOTSTRAP OR SWITCH NODE. 82 such nets are decided by a bound "
                "and layout-bound on boards A, B, C and E. No maker of their nine controllers publishes a minimum edge and no "
                "registry rule states a length, a loop area or a copper area for a power stage. A declaration names what "
                "holds a net's length; nothing holds these, so none is written, and the rule that should govern them and "
                "the way SI-001 would leave them to it are PROPOSED in v2/docs/records/w5si/F-Q1-power-stage-nodes.md.",
     "reversed_by": "once a power-stage layout rule is in the registry and names these nets in its own reading, exclude them "
                    "from SI-001 by declaration as the finding's section 5 describes.",
     "ask": "declare the 82 nets as held by the makers' layout guidance, or leave them on their bound until a rule states "
            "what holds them",
     "recommendation": "LEAVE THEM. The makers' guidance gives three numbers in nine documents and all three are widths; a "
                       "declaration written on it would turn a reading on a sentence.",
     "evidence": "v2/docs/records/w5si/evidence/power-stage-layout-guidance.yaml: 46 citations of 9 held documents, each held "
                 "to its page by v2/docs/records/w5si/tools/verify_citations.py.",
     "blocks": {"SI-001": ["a", "b", "c", "e"]},
     "holds_nothing_today": ""},
]
ORDER = ("title", "asked", "status", "authority", "authority_why", "ruled_by", "ruled_on", "outcome", "reversed_by", "ask",
         "recommendation", "evidence", "blocks", "holds_nothing_today")
DAY = "2026-09-27"


def folded(key, text):
    body = textwrap.wrap(text, width=104, break_long_words=False, break_on_hyphens=False)
    return "    %s: >-\n%s\n" % (key, "\n".join("      " + ln for ln in body))


def row_text(n, r):
    out = "  - n: %d\n" % n
    for k in ORDER:
        if k == "asked": out += "    asked: %s\n" % DAY
        elif k == "status": out += "    status: ruled\n"
        elif k == "authority": out += "    authority: SESSION\n"
        elif k == "ruled_by": out += "    ruled_by: SESSION\n"
        elif k == "ruled_on": out += "    ruled_on: %s\n" % DAY
        elif k == "blocks":
            b = r["blocks"]
            out += "    blocks: {}\n" if not b else "    blocks: {%s}\n" % ", ".join("%s: [%s]" % (kk, ", ".join(v)) for kk, v in b.items())
        elif k == "holds_nothing_today":
            if r[k]: out += folded(k, r[k])
        else: out += folded(k, r[k])
    return out


def main():
    import yaml, datetime
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    old = before["decisions"]
    titles = {d.get("title") for d in old}
    assert not any(r["title"] in titles for r in ROWS), "already applied"
    n0 = max(d["n"] for d in old) + 1
    assert s.endswith("\n")
    out = s + "".join(row_text(n0 + i, r) for i, r in enumerate(ROWS))
    d = yaml.safe_load(out)
    # THE STRUCTURE, before against after
    assert set(d) == set(before)
    for k in before:
        if k != "decisions": assert d[k] == before[k]
    new = d["decisions"]
    assert new[:len(old)] == old, "a decision the file held changed"
    assert len(new) == len(old) + len(ROWS)
    for i, r in enumerate(ROWS):
        x = new[len(old) + i]
        assert x["n"] == n0 + i and x["status"] == "ruled" and x["authority"] == "SESSION" and x["ruled_by"] == "SESSION", x
        assert x["asked"] == datetime.date(2026, 9, 27) and x["ruled_on"] == datetime.date(2026, 9, 27), x
        for k in ("title", "authority_why", "outcome", "reversed_by", "ask", "recommendation", "evidence"):
            assert x[k] == r[k], "row %d: %s is not the text written (%r)" % (n0 + i, k, x[k][:60])
        assert x["blocks"] == r["blocks"]
        assert x.get("blocks") or str(x.get("holds_nothing_today") or "").strip(), "row %d says neither what it holds nor that it holds nothing" % (n0 + i)
    what = "decisions %d to %d" % (n0, n0 + len(ROWS) - 1)
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: pcb_decisions.yaml would gain %s" % what); return
    open(TARGET, "w", encoding="utf-8").write(out)
    print("pcb_decisions.yaml: %s added (SESSION, ruled). Owed by the integrator: regenerate v2/docs/OWNER-DECISIONS-OPEN.md "
          "with decisions_render.py" % what)


if __name__ == "__main__":
    main()
