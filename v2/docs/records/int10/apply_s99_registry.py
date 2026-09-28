#!/usr/bin/env python3
"""S-99 re-stated and its two follow-ups opened in the requirements registry (MESHSAT-1357, integration set 9, stream
s99reg, 29 September 2026). AI engineering text; prototype design, nothing built, ordered or measured.

  S-99   re-stated from v2/docs/records/s99a/REGISTRY-DRAFT.md section 1 (which supersedes records/s99/REGISTRY-DRAFT.md):
         the declared-demand question answered by decision 55 and the circuit, and the still-open items (a) to (g) with
         what decides each. Its title only: REQ-018 keeps `waits_on: S-99`, so S-99 carries no disposition. Two edits
         against the draft's words: "not a guaranteed 1 kOhm maximum" is written "no maximum at 1 kOhm is published" (the
         claims screen refuses the word), and item (d) gains the PFM ripple and the load-step overshoot that stream
         s99a's README section 9 item (5) put under it (the independent check of s99a, minor item 5) and names C231 and
         C232's part (minor item 10).
  S-115  board A's layout generator after decision 55 (v2/docs/records/s99a/OPEN-ITEM-LAYOUT-A.md): disposition
         LAYOUT_STAGE with its reason; no schematic-phase record rests on it.
  S-116  board D's codec supply floor at the +5V_D8 peak (v2/docs/records/s99a/OPEN-ITEM-CODEC-FLOOR.md), linked from
         the records whose verdict it can move: REQ-018 (PS-ALLTX with every rail in regulation: the codec's supply is
         lowest when the exciter keys), REQ-009 (both headset jacks key the VHF path and carry receive audio on their
         codec channels) and REQ-002 (a VHF voice exchange over a headset, whose transmit and receive audio pass the
         same codec). No disposition, as no record waiting on an item carries one; the draft's DECLARATION word is not
         written for that reason.

Asserted: S-115 is the next free S id (the highest S id in open and closed items is S-114); S-99 is open with no
disposition and REQ-018 waits on it before and after; every new text passes int7's screen (claims_check's CLAIM
pattern, no dash); the file re-parses; only S-99's title, the two new items and the three records' waits_on change.
Refuses a second run (S-115 or S-116 present). Usage: python3 <this file> [--root <tree>] [--check]."""
import os, sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _int10 as H
from _int10 import A

NAME = "apply_s99_registry"
NEW = ("S-115", "S-116")
LINK = {"REQ-018": "S-116", "REQ-009": "S-116", "REQ-002": "S-116"}

T99 = (
    "(cx1 I-03; analysed by stream s99, applied by stream s99a, v2/docs/records/s99a/README.md) THE DECLARED-DEMAND "
    "QUESTION IS ANSWERED BY DECISION 55 AND THE CIRCUIT. The D8 mezzanine left board A's +5V_DEV for its own TPS62933 "
    "buck U41 from VBAT (rail +5V_D8IN, 56.2k over 10.7k at 0.1 percent: 5.002 V nominal, 4.872 to 5.133 V over VFB 784 "
    "to 816 mV, both tolerances, 25 ppm/C over 65 K and the FB leakage, SLUSEA4D p.6), with U23 kept as its eFuse. Board "
    "A's LM5176 device stage U7 now carries board B's 6.0 A and the wall host port's 0.9142 A (U32 at 1.00 kOhm: TPS2596 "
    "equation 7 is RILM = 903 / (ILIM - 0.0112), SLVSET8A printed p.28, so ILIM = 0.9142 A nominal; the generator had the "
    "sign as + and read 0.89 A): 6.9142 A declared against the average loop's conditional minimum of 7.056897 A (43 mV "
    "over R43 6 mOhm at +1 percent and an assumed 50 K at +/-110 ppm/K; SNVSAI1D p.7, Vishay 30100 pp.1-2), a margin of "
    "0.142697 A (0.181510 A at the initial 7.095710 A; 0.100853 A and 0.091314 A with the wall at the 909 ohm row's "
    "extrapolated 0.956044 A and with R186 at -1 percent, which are estimates from a ratio of the maker's rows: no maximum "
    "at 1 kOhm is published). STILL OPEN, each with what decides it: (a) the M and P tiers against the loop: M 5.942235 A "
    "passes by 1.114661 A as a conditional allocation, P 8.171220 A (8.180759 A with R186 tolerance) exceeds the minimum "
    "by 1.114324 A (1.123863 A) on board B's declared child peaks; decided by board B's reconciliation of its +5V_DEV "
    "children (I-03's M/P adequacy: the supervisor LDOs' 0.12 A entries with their ground current, U26 against the "
    "maker's 0.34 A, U25's 2.0 A peak) or a document that makes the peaks non-coincident, and at the bench by the "
    "coincident current at R43 and J_5V_DEV under PS-ALLTX (PT-4); (b) timing and capacitor support: no closed-loop time "
    "constant or onset bound is published (CSS/gm = 47 us is a dimensional ratio); simultaneous SS, rail voltage and "
    "branch current through actual bursts and controlled steps (PT-2 for +5V_S2, PT-4 here); (c) collapse and recovery: "
    "current against falling voltage, dropout, UVLO and restart with the fitted loads (PT-4); (d) the new buck U41: its "
    "loss and temperature (only JEDEC and EVM RthJA are published, SLUSEA4D p.6), the output capacitors' DC-bias derating "
    "at 5 V (C231 and C232 map to C2918511, a 25 V 1210 part; no curve held), the 0.90 efficiency (a project figure), by "
    "calculation on the routed copper and by measurement on the prototype, and its PFM ripple at light load and its "
    "load-step overshoot at the exciter's unkey, which the 4.872 to 5.133 V DC set-point band does not include (SLUSEA4D "
    "9.3.2; PT-4); (e) the stage's FET and shunt temperatures and switching waveforms (the 112 C figure is a scenario, "
    "SLPS414B p.3), PT-4 over VBAT, load and ambient including the 60 s key-down; (f) board A's layout generator does not "
    "yet place the ten new parts nor re-derive +5V_DEV's outlet island (S-115, layout stage); (g) board D's codec supply: "
    "from U41's 4.872 V bottom, U23's on resistance (SLVSET8A p.7) and the 6 percent budget leave the PCM2912A 4.44 to "
    "4.48 V at the 1.0 A typical (0.09 to 0.13 V over its 4.35 V), 0.007 to -0.009 V with +5V_D8IN's own 2 percent "
    "spent, and under 4.35 V at the 2.0 A peak, which predates the split (S-116). Closes when: board A is regenerated "
    "from fnd/s99a on the box and its intent, netlist and ERC are read; PWR-001 and INT-001 are re-taken on it; the "
    "IF-AB-POWER +5V_DEV row reads the new figures; (a) is decided by board B's declarations or a document. (b), (c), (d) "
    "and (e) are prototype verification in TEST-PLAN rows PT-2 and PT-4 (proposed in "
    "v2/docs/records/s99/RAILS-ACTIONABLE.md), kept separate from the desk closure. Record: "
    "v2/docs/records/s99/ANALYSIS.md, CORRECTION.md, checks/check-2-claude.md; v2/docs/records/s99a/README.md.")

W115 = (
    "Board A's layout generator, run when board A's layout is drawn. No schematic-phase record rests on it: the "
    "schematic, netlist and intent of board A carry the new parts and nets from gen_sch_a.py (stream s99a).")
T115 = (
    "(S-99, decision 55, stream s99a) Board A's layout generator gen_pcb_a3.py does not know the D8 mezzanine's own buck. "
    "Two consequences, both at its next run: (1) it refuses the board, because its placement ends with `missing = [r for "
    "r in comps if r not in placed ...]; if missing: raise SystemExit(\"unplaced: ...\")` (line 312 on set 8's line) and "
    "none of the ten new parts U41, L13, C227 to C232, R217 and R218 has a region or a fixed site (the fixed table at "
    "line 208 places U21, U22 and U23 at (70, 66), (80, 66) and (90, 66); the region list \"EFS\" at line 280 holds the "
    "eFuse passives); (2) the +5V_DEV outlet-cluster island of lines 583 to 586 (`bank_col(out, [\"R100\", \"C103\", "
    "\"U23\"])` on F.Cu and `pads_rect(net_pads(out, [\"R100\", \"C103\", \"U23\", \"U18\"]), ...)` on In3, inside the "
    "`n == \"D\"` branch where out is +5V_DEV) names three parts whose +5V_DEV pads moved to +5V_D8IN (U23 pin 4 IN, R100 "
    "the OVLO divider's top, C103 the input capacitor), so `net_pads` refuses or the island is built on the wrong net. The "
    "owner is board A's layout generator owner in board A's layout phase: place U41's buck (U41, L13, C227 to C232, R217, "
    "R218) beside U23 with the input loop C229/C230 at U41 pin 3 (SLUSEA4D 12.1 p.40, the bypass pairs the generator "
    "declares), re-derive the outlet-cluster island for +5V_DEV from the parts still on it (U32's input, U18 pin 17 and "
    "the J_5V_DEV path) and give +5V_D8IN its own island from L13 to U23 pin 4, then run the pre-route and read /+5V_DEV "
    "and /+5V_D8IN at PREROUTE-DONE. Also at layout: dc_density on +5V_DEV at its 6.9142 A declared peak and on +5V_D8IN "
    "at 2.0 A, and U41's loss and temperature on the routed copper (SLUSEA4D gives RthJA 112.2 C/W JEDEC and 60.2 C/W on "
    "TI's EVM only, p.6). Closed by a gen_pcb_a3.py run that places every part of board A's netlist and reads both rails "
    "at PREROUTE-DONE, and by the layout-phase copper and thermal readings above.")
T116 = (
    "(stream s99a, S-99 follow-up) Board D's +5V_D8 supply at the PCM2912A codec falls under the codec's 4.35 V "
    "recommended minimum (TI SLES230A, revised August 2015, 7.3 p.5) at the declared 2.0 A peak once U23's drop and the "
    "budgets are counted. The chain from U41's regulation point: U41's DC set-point minimum 4.872 V (56.2k over 10.7k at "
    "0.1 percent, SLUSEA4D p.6), +5V_D8IN's copper (declared budget 2 percent, 0.100 V), U23's pass FET (SLVSET8A printed "
    "p.7, VIN above 4 V: 89 mOhm typical, 115.3 mOhm maximum over -40 to 85 C, 131 mOhm maximum to 125 C), and +5V_D8's "
    "copper on boards A and D (declared budget 6 percent, 0.300 V). At the 1.0 A typical the codec gets 4.44 to 4.48 V, "
    "0.09 to 0.13 V over 4.35 V; with +5V_D8IN's whole 2 percent spent, 0.007 V (U23 at its 85 C maximum) to -0.009 V "
    "(125 C). At the 2.0 A peak, reading each budget as a fixed bar: 4.341 V (-0.009 V) with the 6 percent alone at U23's "
    "85 C maximum, 4.241 V (-0.109 V) with +5V_D8IN's 2 percent too; dc_drop judges each budget at the rail's typical "
    "current (dc_drop.py lines 258 to 264), so a copper drop that spends its budget at 1.0 A doubles at 2.0 A and the floor "
    "reads 3.84 V. The shortfall PREDATES the split: U23 was in series before it, and the LM5176 source's bottom was 4.875 "
    "V (VREF 0.788 V, SNVSAI1D p.5, 53.6k over 10k at 1 percent, 100 ppm/C over 65 K), which gives 4.344 V (-0.006 V) at "
    "2.0 A with the 6 percent bar alone. Owners: board A (U41's set point, +5V_D8IN's budget and its layout reading) and "
    "board D (its +5V_D8 declarations and the codec's supply). Options for them, each with its figure at 2.0 A, the 6 "
    "percent bar and U23 at its 85 C maximum: (1) tighten +5V_D8IN's drop budget to about 0.5 percent (0.025 V) and add "
    "its reading at layout to S-115: 4.316 V (-0.034 V) at 2.0 A, 4.432 V (+0.082 V) at 1.0 A, so it closes the typical "
    "case and not the peak alone; (2) raise U41's set point within the 5.23 V ceiling (board D's v_work; the codec's 5.25 "
    "V recommended maximum): with this resistor class a top of 5.23 V gives a bottom of 4.964 V; the 53.6k over 10k pair "
    "at 0.1 percent (4.956 to 5.221 V, neither code in the project's parts certification today) gives 4.401 V (+0.051 V) "
    "at 2.0 A with option 1's 0.5 percent and 4.326 V (-0.024 V) with the present 2 percent, and 4.369 V (+0.019 V) at "
    "U23's 125 C maximum with 0.5 percent; the top then sits 9 mV under 5.23 V as a DC band, before ripple and overshoot; "
    "(3) show by board D's declarations or a document that the codec's operation does not coincide with the 2.0 A peak: "
    "2.0 A is U23's current limit, not a load; board D's own heaviest figure in stream s99's P-tier is 1.59 A "
    "(v2/docs/records/s99/ANALYSIS.md 3b), where the floor is 4.389 V (+0.039 V) with the 6 percent bar alone and 4.289 V "
    "(-0.062 V) with +5V_D8IN's 2 percent. On the fixed-bar reading (1) with (2) clears 4.35 V at U23's 85 and 125 C "
    "maxima, and (1) with (3) only to 85 C (+0.014 V at 1.59 A, -0.012 V at 125 C); every option also needs the routed "
    "boards' drop at the peak current (the budgets are judged at the typical), which board A's layout (S-115) and board "
    "D's layout reading supply. REQ-018, REQ-009 and REQ-002 wait on it: the codec is in every headset and VHF voice path "
    "and its supply is lowest while the exciter keys. Figures: v2/docs/records/s99a/codec_floor.out (codec_floor.py). "
    "Closed by the owners' declarations and those readings giving the codec at least 4.35 V at the declared peak, or by a "
    "document or a board D declaration that bounds the peak the codec must operate through.")


def main(argv):
    root = H.root_of(argv)
    t = H.read(root, H.REG)
    for iid in NEW:
        if "\n  - id: %s\n" % iid in t: H.refuse(NAME, "%s exists already (a second run)" % iid)
    before = yaml.safe_load(t)
    items = {i["id"]: i for i in before["open_items"]}
    recs = {r["id"]: r for r in before["records"]}
    ids = [i["id"] for i in before["open_items"]] + [i["id"] for i in before["closed_items"]]
    top = max(int(x[2:]) for x in ids if x.startswith("S-"))
    if top != int(NEW[0][2:]) - 1: H.refuse(NAME, "%s is not the next free S id (the highest is S-%d)" % (NEW[0], top))
    s99 = items.get("S-99")
    if not s99 or set(s99) != {"id", "class", "status", "title"} or s99["class"] != "SESSION":
        H.refuse(NAME, "S-99 is not the open SESSION item with a title only that this script re-states: %s" % (sorted(s99 or {})))
    if "S-99" not in (recs["REQ-018"].get("waits_on") or []): H.refuse(NAME, "REQ-018 no longer waits on S-99")
    for rid in LINK:
        if rid not in recs: H.refuse(NAME, "%s is not a record" % rid)
    for txt, what in ((T99, "S-99"), (T115, "S-115"), (W115, "S-115 why"), (T116, "S-116")): A.screen(txt, what)
    if len(W115) < 40: H.refuse(NAME, "S-115's disposition_why is under 40 characters")
    if H.one_space(T99) == H.one_space(s99["title"]): H.refuse(NAME, "S-99's new title does not differ")

    out = t
    # S-99: the title block only
    i, j = A.span(out, "S-99")
    lines = out[i:j].split("\n")
    idx = [n for n, l in enumerate(lines) if l == "    title: >-"]
    if len(idx) != 1: H.refuse(NAME, "S-99 has %d title blocks" % len(idx))
    a, b = A.block_at(out[i:j], idx[0] + 1, lines, 6)
    blk = "\n".join(lines[:a] + A.fold(T99, 6, 120).rstrip("\n").split("\n") + lines[b:])
    out = out[:i] + blk + out[j:]
    # the three records wait on S-116
    for rid, iid in LINK.items():
        i, j = A.span(out, rid)
        out = out[:i] + H.add_waits(NAME, out[i:j], rid, iid) + out[j:]
    # the two items, before closed_items
    k = out.index("\nclosed_items:\n")
    block = ("  - id: S-115\n    class: SESSION\n    status: OPEN\n    disposition: LAYOUT_STAGE\n    disposition_why: >-\n%s"
             "    title: >-\n%s" % (A.fold(W115, 6, 120), A.fold(T115, 6, 120)))
    block += "  - id: S-116\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % A.fold(T116, 6, 120)
    out = out[:k + 1] + block + out[k + 1:]
    if out == t: H.refuse(NAME, "nothing changed")

    after = yaml.safe_load(out)
    want = {rid: {"waits_on"} for rid in LINK}
    H.compare_records(NAME, before, after, want)
    rb = {r["id"]: r for r in after["records"]}
    for rid, iid in LINK.items():
        if rb[rid]["waits_on"] != list(recs[rid].get("waits_on") or []) + [iid]: H.refuse(NAME, "%s's waits_on is %s" % (rid, rb[rid]["waits_on"]))
    ob = {x["id"]: x for x in after["open_items"]}
    if list(ob) != list(items) + list(NEW): H.refuse(NAME, "the open item list changed beyond %s" % ", ".join(NEW))
    for kk in items:
        d = {f for f in set(items[kk]) | set(ob[kk]) if items[kk].get(f) != ob[kk].get(f)}
        if d != ({"title"} if kk == "S-99" else set()): H.refuse(NAME, "open item %s: fields changed %s" % (kk, sorted(d)))
    if ob["S-99"]["title"] != H.one_space(T99) or "disposition" in ob["S-99"]: H.refuse(NAME, "S-99 did not round-trip")
    if ob["S-115"] != {"id": "S-115", "class": "SESSION", "status": "OPEN", "disposition": "LAYOUT_STAGE",
                       "disposition_why": H.one_space(W115), "title": H.one_space(T115)}: H.refuse(NAME, "S-115 did not round-trip")
    if ob["S-116"] != {"id": "S-116", "class": "SESSION", "status": "OPEN", "title": H.one_space(T116)}: H.refuse(NAME, "S-116 did not round-trip")
    if "S-99" not in rb["REQ-018"]["waits_on"]: H.refuse(NAME, "REQ-018 lost S-99")
    for sec in before:
        if sec not in ("records", "open_items") and before[sec] != after[sec]: H.refuse(NAME, "section %s changed" % sec)
    if "--check" in argv:
        print("%s: CHECK ONLY, nothing written: S-99's title re-stated, S-115 (LAYOUT_STAGE) and S-116 would open, %s would wait on S-116"
              % (NAME, ", ".join(LINK)))
        return 0
    H.write(root, H.REG, out)
    if yaml.safe_load(H.read(root, H.REG)) != after: H.refuse(NAME, "the file written does not re-parse to what was checked")
    print("%s: S-99's title re-stated (no disposition; REQ-018 still waits on it); S-115 opened (LAYOUT_STAGE); S-116 opened and %s wait on it"
          % (NAME, ", ".join(LINK)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
