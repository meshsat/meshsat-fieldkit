#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, RE-ISSUED 28 September 2026 by stream w5si2,
MESHSAT-1357, layer 9): the session decisions of the two streams as rows of v2/ecad/tools/pcb_decisions.yaml. That file is the integrator's; this script makes the change
and the integrator runs it, or does not: the independent check asked that it be CONSIDERED, because three of the
decisions change what rule SI-001 counts as decided and until now they were written only in a data file's header.

RE-ISSUED on the drafts check (AI review, 28 September 2026):
  B3   the third row cited board B's netlist by a sha256/16 and gen_sch_b.py by a line number that were TYPED, and both
       were stale on the integration line (8b78c59754a6a0c7 and line 1151, where the tree had 028997a6c5e8810f and line
       1191). NOW THE CITATION IS DERIVED from the tree the draft runs on and the FACTS IT STANDS FOR ARE ASSERTED: the
       netlist's sha256/16 is computed, the net BOB must carry exactly R9 pin 2, R10 pin 2 and C33 pin 1 with the values
       75, 75 and 1n 2kV, and the generator's lines are the calls that name the net BOB, found in the parsed source.
  M1   a requirements record bound to pcb_decisions.yaml by its sha256/16 stops validating when this file changes (one
       did: CFL-016). THE REBIND IS PART OF THIS DRAFT: every record of pcb_requirements.yaml bound to the file at the
       sha256/16 it had is rebound to the sha256/16 it gets, with a re-read sentence added to its evidence that says
       what changed and that the decisions the record reads are unchanged, which the draft has asserted as structure.
       Both files' new texts are built and checked before either is written.
  and three rows are added for the decisions of 28 September (E, F, G below).

WHAT IT ADDS: seven rows, appended after the last decision, numbered from the NEXT FREE number of the tree it runs in
(other streams of this wave take numbers too, so none is typed here). Each is `status: ruled`, `authority: SESSION`,
with authority_why, ruled_by, ruled_on, outcome and reversed_by, under the owner's ruling of 21 September 2026
(engineering decisions are the session's) and his standing rule of 26 September 2026. None is the owner's.

  A  what counts as a driver's edge, and which edge governs a net      (ER-D8, ER-D9, ER-D12 as corrected, ER-D13)
  B  a specification's minimum, and the two edges of an open-drain net (ER-D14)
  C  board B's RF switch ports, and BOB's class                        (W5SI-D1, W5SI-D2 as replaced)
  D  the power-stage nodes stay on their bound until a rule covers them (W5SI-D3)
  E  a [Ramp] cell is held to its model's own V-t table                 (ER-D16)
  F  the makers' models are pinned by a tracked manifest, not held      (ER-D17)
  G  board C's four copies of the EMCON inhibit are LOW_SPEED_OR_DC     (W5SI2-D1)

HOW: the rows are appended as text in the file's own style; the result is parsed and COMPARED WITH THE OLD ONE AS
STRUCTURE before anything is written: every decision the file held is there, unchanged and in the same order, and
exactly seven follow it. A second run is refused.

AFTER IT, the integrator owes what any new decision owes: v2/docs/OWNER-DECISIONS-OPEN.md is generated from this file
(decisions_render.py) and a test refuses a stale page; and the requirements trace page is rendered from
pcb_requirements.yaml, which this draft changes by the rebind. What it prints says both.

Applied by the integrator on the integrated tree, from anywhere:
    python3 v2/docs/records/w5si/apply/apply_decisions_w5si.py [--root <tree>] [--dry-run]
"""
import os, sys, ast, hashlib, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _apply as AP

ROOT = AP.root_of(HERE) if "--root" not in sys.argv or sys.argv.index("--root") + 1 < len(sys.argv) else os.path.abspath(".")
TARGET = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_decisions.yaml")
REQS = os.path.join(ROOT, "v2", "ecad", "tools", "pcb_requirements.yaml")
BOUND = "v2/ecad/tools/pcb_decisions.yaml@"
BOB_NODES = {("R9", "2"), ("R10", "2"), ("C33", "1")}
BOB_VALUES = {"R9": "75", "R10": "75", "C33": "1n 2kV"}
BOB_EVIDENCE = "@BOB_EVIDENCE@"          # replaced when the draft runs, by what the tree it runs on holds

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
                    "independent check (AI review) of 27 September 2026 refused.",
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
     "evidence": BOB_EVIDENCE,
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
    {"day": "2026-09-28",
     "title": "rule SI-001: a [Ramp] cell is held to its model's own V-t table, and a pin whose cell it contradicts takes the bound",
     "authority_why": WHY + "it can only take a maker's figure away and never give one: a pin it flags takes the instantaneous "
                            "bound, the strictest figure the rule has. No count of any reading moves by it.",
     "outcome": "A [RAMP] CELL THE MODEL'S OWN TABLE CONTRADICTS IS NOT A MAKER'S FIGURE. An IBIS [Ramp] cell is dV/dt, dV "
                "being by the keyword's definition the 20 to 80 percent swing. Where the same model carries a V-t table of "
                "that edge in the [Ramp]'s own fixture, dV must be 50 to 70 percent of the table's swing and dt within 25 "
                "percent of the time the table itself takes from 20 to 80 percent. A pin any of whose admitted driven cells "
                "fails either reads FLAGGED: it has no figure, takes the instantaneous bound, and its net is decided by a "
                "bound. A family's figure is its fastest pin that has one, and its record names the flagged pins and is held "
                "to the model on that. tools/ibis_read.py is the criterion (cell_check, RAMP_DV, RAMP_DT); ER-D16 in the "
                "header of tools/pcb_edge_rates.yaml.",
     "reversed_by": "in tools/ibis_read.py widen RAMP_DV and RAMP_DT until no cell is flagged, or remove pin_edge's FLAGGED "
                    "branch, and restore the two records' figures (TI-PCA9555 0.121 ns, TI-TMP117 7.6757 ns) in "
                    "tools/pcb_edge_rates.yaml.",
     "ask": "read a [Ramp] cell as the file writes it, leave a contradicted cell out and read the next, or give a pin with a "
            "contradicted cell no figure",
     "recommendation": "NO FIGURE. Reading it as written is right only by luck (both cells found erred short); leaving it out "
                       "and reading the next cell would give a slower figure than the table the cell was contradicted by may "
                       "hold.",
     "evidence": "two AI reviews of 27 and 28 September 2026 (the first lens's M5, the drafts check's M8), and the measurement "
                 "on the thirteen models the manifest pins: of 585 driven cells 537 have a table of their edge, 522 of them "
                 "hold and 15 do not, all of TI's PCA9555 INT models (dt at 0.14 to 0.49 of the table's time) and TMP117 SDA "
                 "models (dV at 11 to 39 percent of the swing); 48 have no table and cannot be contradicted "
                 "(tools/tests/test_edge_length.py holds the two records to their models where the models are in the tree).",
     "blocks": {},
     "holds_nothing_today": "no count moves by it: both flagged pins sit on nets a bound already decided (EXP_INT, and the kit "
                            "bus's SDA)."},
    {"day": "2026-09-28",
     "title": "rule SI-001: the makers' IBIS models are pinned by a tracked manifest and are not in the repository",
     "authority_why": WHY + "it publishes nothing and decides nothing about publication, which is the owner's and stays held "
                            "back; it is how the instrument works while the models are withheld, and it makes a tree without "
                            "them read STRICTER (more nets undecided), never towards a pass.",
     "outcome": "A MODEL IS READ ONLY WHEN THE MANIFEST PINS THE FILE PRESENT, AND A MODEL THAT IS ABSENT DECIDES NOTHING. "
                "v2/vendor/ibis-manifest.yaml names each model's maker, address, how the .ibs is taken out of what the "
                "address serves, the sha256 of the extracted file and the words of its header on copying; "
                "tools/ibis_fetch.py fetches the models from the makers' own addresses and verifies each; .gitignore keeps "
                "them out of the repository. A net that waits on an absent model reads UNDECIDED naming the file, the "
                "reading is INCONCLUSIVE and records the state it was taken in; a record's own edge_ns is never used in its "
                "model's place. The manifest is a configuration input dated like any other, and rules_status holds a "
                "reading to the models through it (PINNED_INPUTS). ER-D17 in the header of tools/pcb_edge_rates.yaml.",
     "reversed_by": "the owner decides to publish the models: they are committed, the ignore rule is dropped, and they may be "
                    "declared as ordinary configuration inputs; the manifest may stay as the record of where they came from.",
     "ask": "commit the models, declare them as inputs and leave them uncommitted, or pin them by a tracked manifest",
     "recommendation": "PIN THEM. Committing publishes files whose headers forbid it or grant nothing; declaring them "
                       "uncommitted makes the only state that reads current the one that publishes.",
     "evidence": "the drafts check of 28 September 2026 (AI review), blocking item B1, with its simulation of the three "
                 "states; the headers' own words, quoted per file with their lines in v2/vendor/ibis-manifest.yaml (five "
                 "forbid distribution, eight carry a copyright line and no grant); and the fetch proven once into a scratch "
                 "folder (v2/docs/records/w5si2/readings/ibis-fetch-scratch-2026-09-28.txt).",
     "blocks": {},
     "holds_nothing_today": "it holds no rule-board pair that was not held: SI-001 reads INCONCLUSIVE on all six boards with "
                            "the models and without them."},
    {"day": "2026-09-28",
     "title": "board C: the four copies of the EMCON inhibit are declared by what they carry, LOW_SPEED_OR_DC",
     "authority_why": WHY + "the class is the one boards A, B and C already give the line these nets copy (EMCON_HW), it turns "
                            "no reading to a pass (board C reads INCONCLUSIVE before and after, and in the other class too), "
                            "and each entry says that its driver is fast.",
     "outcome": "EMCLAMP_Y, EMCLAMP_G, EMCON_RD AND EMCON_RD_R ARE LOW_SPEED_OR_DC ON THEIR CONTENT, NOT ON A SLOW DRIVER. "
                "They are copies of the EMCON inhibit, a level that moves when a person moves the panel's locking toggle; "
                "nothing samples them on their edge (a FET's gate behind 100R, a pin read as a level behind 1 k). The "
                "class is defined by what a net carries (tools/signal_class.py) and SI-001 asks no edge of it "
                "(tools/edge_length.py, LOW_CLASS). THE DRIVERS ARE FAST and each entry's basis says so: U14's output moves "
                "in 0.221 ns by its maker's IBIS model, and the makers of U13 and of the RP2040 publish no output "
                "transition.",
     "reversed_by": "change `class` to CLOCKED_DIGITAL in the four entries of tools/boards/c.json and re-take SI-001: "
                    "EMCLAMP_Y and EMCLAMP_G are then answered by R48, and EMCON_RD and EMCON_RD_R are layout-bound and "
                    "decided by a bound (R46's 1 k is outside the series screen).",
     "ask": "declare the four nets by what they carry (a level), or by what drives them (a fast gate)",
     "recommendation": "BY WHAT THEY CARRY, as the class is defined and as the line they copy is declared on three boards; "
                       "and say in the basis that the driver is fast, so that nobody reads the class as a slow edge.",
     "evidence": "board C's netlist and tools/gen_sch_c.py, read again when v2/docs/records/w5si/apply/"
                 "apply_board_c_declarations.py runs; TI SCES414P p. 3 and p. 6, Diodes DS35124 Rev. 8-2 p. 1 and p. 6, the "
                 "RP2040 datasheet (build 2025-02-20) p. 303, each held to its page by that draft; the three readings of "
                 "board C it prints (before, after, and in the class not taken).",
     "blocks": {},
     "holds_nothing_today": "it releases no rule-board pair: SI-001 on board C stays INCONCLUSIVE, held by 23 layout-bound nets "
                            "a bound decides."},
]
ORDER = ("title", "asked", "status", "authority", "authority_why", "ruled_by", "ruled_on", "outcome", "reversed_by", "ask",
         "recommendation", "evidence", "blocks", "holds_nothing_today")


def folded(key, text):
    body = textwrap.wrap(text, width=104, break_long_words=False, break_on_hyphens=False)
    return "    %s: >-\n%s\n" % (key, "\n".join("      " + ln for ln in body))


def row_text(n, r):
    out = "  - n: %d\n" % n
    DAY = r.get("day") or "2026-09-27"
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


def bob_evidence():
    """The third row's evidence, from the tree this runs on: the facts are asserted, the pointers derived."""
    tools = AP.tools_on_path(ROOT)
    import edge_length as E, phase_artefacts as PA
    net = PA.netlist("b", os.path.join(ROOT, "v2", "ecad"))
    AP.need(net and os.path.exists(net), "board B's declared phase has no netlist in this tree (%s)" % net)
    nets, values = E.read_netlist(net)
    AP.need("BOB" in nets, "board B's netlist has no net BOB: the third row describes a node that is gone, re-read the board")
    got = {(r, p) for r, p, _f, _t in nets["BOB"]["nodes"]}
    AP.need(got == BOB_NODES, "the net BOB is not as the third row describes it (it carries %s, the row says %s): re-read it"
            % (sorted(got), sorted(BOB_NODES)))
    for ref, val in BOB_VALUES.items():
        AP.need(str(values.get(ref, "")).strip() == val, "%s is %r on board B's netlist and the third row says %s" % (ref, values.get(ref), val))
    gen = os.path.join(tools, "gen_sch_b.py")
    AP.need(os.path.exists(gen), "v2/ecad/tools/gen_sch_b.py is not in this tree")
    tree = ast.parse(open(gen, encoding="utf-8").read())
    lines = sorted({n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                    and any(isinstance(c, ast.Constant) and c.value == "BOB" for x in list(n.args) + [k.value for k in n.keywords] for c in ast.walk(x))})
    AP.need(lines, "no call of gen_sch_b.py names the net BOB")
    return ("the netlist of board B's declared phase (%s, sha256/16 %s), on which BOB carries R9 pin 2 and R10 pin 2 (75 ohm each, "
            "from MCT3 and MCT4) and C33 pin 1 (1n 2kV, to GND); gen_sch_b.py line%s %s, the calls that name the net; and the "
            "makers' words in v2/docs/records/w5si/evidence/cable-side-termination.yaml, held to their pages. The sha256/16 and "
            "the line were read from the tree this row was written on, when it was written."
            % (os.path.relpath(net, os.path.join(ROOT, "v2", "ecad")), hashlib.sha256(open(net, "rb").read()).hexdigest()[:16],
               "s" if len(lines) > 1 else "", ", ".join(str(x) for x in lines)))


def rebind(reqs_text, was16, now16, first, last, old_count):
    """(new text of pcb_requirements.yaml, [record ids rebound]): every record bound to pcb_decisions.yaml at the sha256/16
    it had is bound to the one it gets, with a re-read sentence added to its evidence."""
    import yaml
    before = yaml.safe_load(reqs_text)
    lines = reqs_text.split("\n")
    hits = [i for i, l in enumerate(lines) if l.strip() == '- "%s%s"' % (BOUND, was16)]
    done, out_ids = 0, []
    for i in reversed(hits):
        k = i
        while k >= 0 and lines[k].strip() != "evidence_bound_to:": k -= 1
        assert k >= 0, "a binding of pcb_decisions.yaml stands outside an evidence_bound_to list (line %d)" % (i + 1)
        h = k
        while h >= 0 and not lines[h].startswith("  - id: "): h -= 1
        assert h >= 0, "no record above line %d" % (k + 1)
        rid = lines[h][len("  - id: "):].strip()
        rec = [r for r in before["records"] if r.get("id") == rid]
        assert len(rec) == 1 and isinstance(rec[0].get("evidence"), list), "record %s has no evidence list" % rid
        cited = sorted(int(x) for x in ((rec[0].get("satisfied_by") or {}).get("decisions") or []))
        AP.need(all(x <= old_count for x in cited) or not cited, "record %s reads a decision this draft adds: re-read it" % rid)
        text = ("v2/ecad/tools/pcb_decisions.yaml re-read at the application of stream w5si2's decisions draft "
                "(v2/docs/records/w5si/apply/apply_decisions_w5si.py, MESHSAT-1357, layer 9): decisions %d to %d are APPENDED after "
                "the last decision the file held (seven session decisions of 27 and 28 September 2026 on rule SI-001's edge rates, "
                "the makers' IBIS models and the signal classes of boards B and C); every decision the file held is unchanged and in "
                "the same order, which the draft asserts on the parsed file before it writes%s; so this reading stands on "
                "v2/ecad/tools/pcb_decisions.yaml@%s" % (
                    first, last, (", decisions %s, which this record reads, among them" % " and ".join(str(x) for x in cited)) if cited else "",
                    now16))
        body = textwrap.wrap(text, width=108, break_long_words=False, break_on_hyphens=False)
        lines[i] = lines[i].replace(was16, now16)
        lines[k:k] = ["      - >-"] + ["          " + ln for ln in body]
        done += 1; out_ids.append((rid, text))
    out = "\n".join(lines)
    after = yaml.safe_load(out)
    assert set(after) == set(before)
    for key in before:
        if key != "records": assert after[key] == before[key], "the top-level key %s of pcb_requirements.yaml changed" % key
    assert [r.get("id") for r in after["records"]] == [r.get("id") for r in before["records"]]
    ids = dict(out_ids)
    for x, y in zip(before["records"], after["records"]):
        if x["id"] not in ids:
            assert x == y, "record %s changed and was not to" % x["id"]; continue
        for key in x:
            if key not in ("evidence", "evidence_bound_to"): assert y[key] == x[key], (x["id"], key)
        assert y["evidence"][:-1] == x["evidence"] and " ".join(y["evidence"][-1].split()) == " ".join(ids[x["id"]].split()), x["id"]
        assert y["evidence_bound_to"] == [b.replace(was16, now16) if b == BOUND + was16 else b for b in x["evidence_bound_to"]], x["id"]
    assert BOUND + was16 not in out, "a binding to the old file is left"
    return out, [r for r, _t in out_ids]


def main():
    import yaml, datetime
    AP.need_stream(ROOT)
    AP.need_files(ROOT, ["v2/ecad/tools/pcb_decisions.yaml", "v2/ecad/tools/pcb_requirements.yaml"], "this draft changes it")
    s = open(TARGET, encoding="utf-8").read()
    before = yaml.safe_load(s)
    old = before["decisions"]
    titles = {d.get("title") for d in old}
    AP.need(not any(r["title"] in titles for r in ROWS), "already applied" if all(r["title"] in titles for r in ROWS) else
            "applied in part: some of the seven rows are in pcb_decisions.yaml and some are not; re-read the file")
    rows = [dict(r) for r in ROWS]
    ev = bob_evidence()
    assert sum(1 for r in rows if r["evidence"] == BOB_EVIDENCE) == 1
    for r in rows:
        if r["evidence"] == BOB_EVIDENCE: r["evidence"] = ev
        for k, v in r.items():
            assert not isinstance(v, str) or ("\u2014" not in v and "\u2013" not in v and "@BOB" not in v), (r["title"][:40], k)
    n0 = max(d["n"] for d in old) + 1
    AP.need(s.endswith("\n"), "pcb_decisions.yaml does not end in a newline, so rows cannot be appended to it as text")
    out = s + "".join(row_text(n0 + i, r) for i, r in enumerate(rows))
    assert out != s, "the new text does not differ from the old"
    d = yaml.safe_load(out)
    # THE STRUCTURE, before against after
    assert set(d) == set(before)
    for k in before:
        if k != "decisions": assert d[k] == before[k]
    new = d["decisions"]
    assert new[:len(old)] == old, "a decision the file held changed"
    assert len(new) == len(old) + len(rows)
    for i, r in enumerate(rows):
        x = new[len(old) + i]
        day = datetime.date.fromisoformat(r.get("day") or "2026-09-27")
        assert x["n"] == n0 + i and x["status"] == "ruled" and x["authority"] == "SESSION" and x["ruled_by"] == "SESSION", x
        assert x["asked"] == day and x["ruled_on"] == day, x
        for k in ("title", "authority_why", "outcome", "reversed_by", "ask", "recommendation", "evidence"):
            assert x[k] == r[k], "row %d: %s is not the text written (%r)" % (n0 + i, k, x[k][:60])
        assert x["blocks"] == r["blocks"]
        assert x.get("blocks") or str(x.get("holds_nothing_today") or "").strip(), "row %d says neither what it holds nor that it holds nothing" % (n0 + i)
    # THE REBIND (M1): the records of pcb_requirements.yaml bound to this file at the sha256/16 it had
    was16 = hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
    now16 = hashlib.sha256(out.encode("utf-8")).hexdigest()[:16]
    rq = open(REQS, encoding="utf-8").read()
    bound_any = sorted({l.strip().strip('-').strip().strip('"')[len(BOUND):] for l in rq.split("\n") if l.strip().startswith('- "' + BOUND)})
    stale = [x for x in bound_any if x != was16]
    rq2, ids = (rebind(rq, was16, now16, n0, n0 + len(rows) - 1, max(x["n"] for x in old)) if was16 in bound_any else (rq, []))
    what = "decisions %d to %d" % (n0, n0 + len(rows) - 1)
    owed = ("  pcb_requirements.yaml: %s\n"
            "  OWED after this draft: `decisions_render.py` (v2/docs/OWNER-DECISIONS-OPEN.md is generated from pcb_decisions.yaml and a "
            "test refuses a stale page)%s%s" % (
                ("%d record(s) bound to pcb_decisions.yaml@%s rebound to @%s, each with a re-read sentence added to its evidence: %s"
                 % (len(ids), was16, now16, ", ".join(ids))) if ids else
                "no record is bound to pcb_decisions.yaml at the sha256/16 it had (%s), so none is rebound" % was16,
                "; and `rules_render.py --requirements`, because v2/docs/REQUIREMENTS-TRACE.md is rendered from pcb_requirements.yaml, "
                "which the rebind changed: until then two tests of test_requirements refuse the stale page" if ids else "",
                ("\n  NOT REBOUND, because they were bound to ANOTHER version of the file than the one this draft found (%s): bindings at %s. "
                 "They did not validate before this draft either; re-read them" % (was16, ", ".join(stale))) if stale else ""))
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: pcb_decisions.yaml would gain %s\n%s" % (what, owed)); return 0
    AP.write(TARGET, out)
    if ids: AP.write(REQS, rq2)
    assert yaml.safe_load(open(TARGET, encoding="utf-8").read()) == d, "pcb_decisions.yaml read back is not the text that was written"
    assert hashlib.sha256(open(TARGET, "rb").read()).hexdigest()[:16] == now16
    print("pcb_decisions.yaml: %s added (SESSION, ruled)\n%s" % (what, owed))
    return 0


if __name__ == "__main__":
    AP.run(main)
