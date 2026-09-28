#!/usr/bin/env python3
"""The pages that quote the wrong-sign 0.89 A, and set 8's lead-drop wording, corrected (MESHSAT-1357, integration set 9,
stream s99reg, 29 September 2026). AI engineering text; prototype design, nothing built, ordered or measured.

TPS2596 equation 7 (TI SLVSET8A, May 2019, revised August 2019, printed p.28) is RILM = 903 / (ILIM - 0.0112); its
worked example 903 / (1 - 0.0112) = 913.2 fixes the sign. So U32 at 1.00 kOhm limits at 903 / 1000 + 0.0112 = 0.9142 A
nominal, not 0.89 A (stream s99a corrected the generator; its independent check reproduced it).

  v2/docs/HW-FW-CONTRACT.md  FW-A07: "eFuse U32 (0.89 A)" becomes the 0.9142 A nominal limit.
  v2/docs/ASSEMBLY.md        section 4, the Wall USB host row: the same, and its generator cite (gen_sch_a.py:1151-1167,
                             stale) READ from the generator by `ast` (J_USBW's part call to the end of VBUS_WALL's rail
                             call). Records bound to ASSEMBLY.md by sha (CFL-015) are rebound with one evidence entry;
                             the script asserts that the Wall USB host row is the only line that changes.
  v2/docs/records/s98/README.md R3 and v2/docs/records/s98/LAYER-ROWS.md row 4.10: "0.225 V" was written as the 16 AWG
                             pair plus four VH contacts; 5.63 x 4 x 0.010 = 0.2252 V is the contacts alone. With the copper
                             model of v2/docs/records/cx1/ANALYSIS.md (150 mm supply plus 150 mm return, 1.25 mm2, rho20
                             1.72e-8 ohm m: 4.128 mOhm; 0.00393/C to 60 C) the lead's drop is 5.63 x (0.004128 + 0.040) =
                             0.248441 V, 4.87 percent of 5.1 V; the figures are computed here and asserted.

NOT EDITED: v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md line 244 ("limit 0.89 A"). Its sha256 is pinned three
times in tools/pcb_board_holds.yaml (the review requirement of boards A, D and E), and the pinning script
(records/d8dec31/apply_holds_review_pin.py) refuses to re-pin unless the netlists in the tree are the ones the review
read, which board A's is not any more; editing the review would turn the three holds' review requirement to "re-review
it". The correction is filed beside it instead: v2/docs/records/int10/ERRATA-DECISION-31-REVIEW.md (this script asserts
it is present and that the review is byte-identical to its pin).

Every old text occurs exactly once, every new text differs and passes int7's screen, the registry re-parses and only
the rebound records change. Refuses a second run. Usage: python3 <this file> [--root <tree>] [--check]."""
import os, sys, textwrap
from decimal import Decimal as D

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _int10 as H
from _int10 import A

NAME = "apply_pages_s99"
HWFW, ASM = "v2/docs/HW-FW-CONTRACT.md", "v2/docs/ASSEMBLY.md"
S98R, S98L = "v2/docs/records/s98/README.md", "v2/docs/records/s98/LAYER-ROWS.md"
REVIEW = "v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md"
HOLDS = "v2/ecad/tools/pcb_board_holds.yaml"
ERRATA = "v2/docs/records/int10/ERRATA-DECISION-31-REVIEW.md"
GA = "v2/ecad/tools/gen_sch_a.py"
LIMIT = "0.9142 A nominal limit (TPS2596 equation 7, SLVSET8A p.28)"


def lead_figures():
    """the lead's drop, computed from the inputs records/cx1/ANALYSIS.md names"""
    i = D("5.63")
    rpair20 = D("1.72e-8") * D("0.300") / D("1.25e-6")
    rpair60 = rpair20 * (1 + D("0.00393") * 40)
    contacts = 4 * D("0.010")
    f = {"contacts_v": i * contacts, "lead20_v": i * (rpair20 + contacts), "lead60_v": i * (rpair60 + contacts), "rpair20": rpair20}
    q = lambda x, n: str(x.quantize(D(1).scaleb(-n)))
    out = {"rpair20": q(rpair20, 6), "contacts_v": q(f["contacts_v"], 4), "contacts_pct": q(f["contacts_v"] / D("5.1") * 100, 2),
           "lead20_v": q(f["lead20_v"], 6), "lead20_pct": q(f["lead20_v"] / D("5.1") * 100, 2),
           "lead60_v": q(f["lead60_v"], 6), "lead60_pct": q(f["lead60_v"] / D("5.1") * 100, 2)}
    if out["lead20_v"] != "0.248441" or out["contacts_v"] != "0.2252" or out["rpair20"] != "0.004128":
        H.refuse(NAME, "the lead figures do not reproduce: %s" % out)
    return out


def texts(root):
    sa = H.read(root, GA)
    usbw = H.one_call(NAME, sa, ("part",), "J_USBW", GA)
    vbw = H.one_call(NAME, sa, ("rail",), "VBUS_WALL", GA)
    u32 = H.one_call(NAME, sa, ("efuse",), "U32", GA)
    xa = [getattr(x, "value", None) for x in u32[2].args]
    if xa[:3] != ["U32", "+5V_DEV", "VBUS_WALL"] or "1k" not in str(xa[6]) or "0.91 A" not in str(xa[6]):
        H.refuse(NAME, "U32's call is not the 1k-set eFuse from +5V_DEV to VBUS_WALL: %s" % xa[:7])
    block = H.span_text([(usbw[0], vbw[1])])
    L = lead_figures()
    r3_old = ("- **R3** The lead's own drop (16 AWG pair 300 mm plus four VH contacts at their 10 mOhm maximum: 0.225 V at 5.63 A, 4.4\n"
              "  percent of 5.1 V) is in no board's share of the 2 percent budget (both checks); a contract or budget item, no id.\n")
    r3_new_text = ("**R3** The lead's own drop is in no board's share of the 2 percent budget (both checks); a contract or budget item, "
                   "no id. At 5.63 A the four VH contacts alone at their 10 mOhm initial maximum give 5.63 x 4 x 0.010 = %s V (%s "
                   "percent of 5.1 V); with the pair's copper (150 mm supply and 150 mm return of 16 AWG, 1.25 mm2 at the tree's "
                   "rho20: %s ohm, `records/cx1/ANALYSIS.md`) the lead gives 5.63 x (%s + 0.040) = %s V, %s percent of 5.1 V "
                   "(%s V, %s percent, with the copper at 60 C). Corrected at integration set 9 (stream s99reg, "
                   "`records/int10/apply_pages_s99.py`): this item first gave 0.225 V as the wire plus the contacts, which is "
                   "the contacts alone."
                   % (L["contacts_v"], L["contacts_pct"], L["rpair20"], L["rpair20"], L["lead20_v"], L["lead20_pct"], L["lead60_v"], L["lead60_pct"]))
    r3_new = textwrap.fill(r3_new_text, width=120, initial_indent="- ", subsequent_indent="  ", break_long_words=False,
                           break_on_hyphens=False) + "\n"
    lr_old = ("the leads' own drop (16 AWG pair 300 mm plus four VH contacts at their 10 mOhm maximum, 0.225 V at 5.63 A, 4.4 percent "
              "of 5.1 V) is in no board's share")
    lr_new = ("the leads' own drop (the 16 AWG pair's 300 mm of copper plus four VH contacts at their 10 mOhm initial maximum: 5.63 x "
              "(%s + 0.040) = %s V at 5.63 A, %s percent of 5.1 V; the 0.225 V first written here is the four contacts alone, "
              "corrected at integration set 9) is in no board's share" % (L["rpair20"], L["lead20_v"], L["lead20_pct"]))
    return block, [
        (HWFW, "FW-A07", "into eFuse U32 (0.89 A), held off by R190", "into eFuse U32 (0.9142 A nominal limit, TPS2596 equation 7, SLVSET8A p.28), held off by R190"),
        (ASM, "Wall USB host row", "VBUS from the eFuse `U32`, 0.89 A, switched by A22's expander; `gen_sch_a.py:1151-1167`)",
         "VBUS from the eFuse `U32`, %s, switched by A22's expander; `gen_sch_a.py:%s`)" % (LIMIT, block)),
        (S98R, "R3", r3_old, r3_new),
        (S98L, "row 4.10", lr_old, lr_new),
    ]


def main(argv):
    root = H.root_of(argv)
    block, edits = texts(root)
    # the review stays as filed and pinned; its erratum is beside it
    import hashlib
    rv = hashlib.sha256(open(H.rel(root, REVIEW), "rb").read()).hexdigest()
    holds = yaml.safe_load(H.read(root, HOLDS))
    pins = [x.get("sha256") for h in holds["holds"].values() for x in (h.get("layout_entry_requires") or []) if x.get("document") == REVIEW]
    if len(pins) != 3 or set(pins) != {rv}: H.refuse(NAME, "the review is not byte-identical to its three pins (%s, pins %s): re-read it" % (rv[:16], pins))
    if not os.path.exists(H.rel(root, ERRATA)): H.refuse(NAME, "%s is not in the tree" % ERRATA)
    if "limit 0.89 A" not in H.read(root, REVIEW): H.refuse(NAME, "the review no longer says 'limit 0.89 A': re-read the erratum")

    cur = {}
    for p, _nm, _o, _n in edits: cur.setdefault(p, H.read(root, p))
    done = [cur[p].count(n) == 1 and cur[p].count(o) == 0 for p, _nm, o, n in edits]
    if all(done): H.refuse(NAME, "already applied (a second run)")
    if any(done): H.refuse(NAME, "applied in part: %s" % [nm for (p, nm, o, n), dd in zip(edits, done) if dd])
    new = dict(cur)
    for p, nm, old, nw in edits:
        if nw == old: H.refuse(NAME, "%s: the new text does not differ" % nm)
        A.screen(nw, "%s %s" % (p, nm))
        if new[p].count(old) != 1: H.refuse(NAME, "%s %s: the old text occurs %d times, once expected" % (p, nm, new[p].count(old)))
        new[p] = new[p].replace(old, nw, 1)
    # ASSEMBLY.md: exactly one line changed, the Wall USB host row
    a0, a1 = cur[ASM].split("\n"), new[ASM].split("\n")
    diff = [k for k in range(max(len(a0), len(a1))) if (a0[k] if k < len(a0) else None) != (a1[k] if k < len(a1) else None)]
    if len(a0) != len(a1) or len(diff) != 1 or not a1[diff[0]].startswith("| Wall USB host"):
        H.refuse(NAME, "ASSEMBLY.md: lines changed %s, only the Wall USB host row expected" % [k + 1 for k in diff])
    if not (new[HWFW].count("\n| FW-A07 |") == 1 and "0.89 A" not in [l for l in new[HWFW].split("\n") if l.startswith("| FW-A07 |")][0]):
        H.refuse(NAME, "HW-FW-CONTRACT.md's FW-A07 row still carries 0.89 A")

    # the records bound to ASSEMBLY.md
    was16, now16 = H.sha16_text(cur[ASM]), H.sha16_text(new[ASM])
    rq = H.read(root, H.REG)
    rb = yaml.safe_load(rq)
    bound = H.bound_records(rb, ASM)
    stale = {r: v for r, v in bound.items() if v != was16}
    if stale: H.refuse(NAME, "records bound to another version of ASSEMBLY.md than the tree's %s: %s" % (was16, stale))
    rq2 = rq
    for rid in sorted(bound):
        entry = ("v2/docs/ASSEMBLY.md re-read at integration set 9 (stream s99reg's v2/docs/records/int10/apply_pages_s99.py, "
                 "MESHSAT-1357, 29 September 2026): only section 4's Wall USB host row changed, U32's limit 0.89 A written as "
                 "the 0.9142 A nominal limit of TPS2596 equation 7 with its sign corrected (SLVSET8A printed p.28) and its "
                 "generator cite brought to gen_sch_a.py:%s; every other line is byte-identical, the rows and steps this "
                 "reading cites among them, which the script asserts line by line; so this reading stands on "
                 "v2/docs/ASSEMBLY.md@%s" % (block, now16))
        A.screen(entry, "%s's entry" % rid)
        i, j = A.span(rq2, rid)
        r = H.add_evidence(NAME, rq2[i:j], rid, entry)
        r = H.rebind_line(NAME, r, rid, ASM, was16, now16)
        rq2 = rq2[:i] + r + rq2[j:]
    if bound:
        after = yaml.safe_load(rq2)
        H.compare_records(NAME, rb, after, {rid: {"evidence", "evidence_bound_to"} for rid in bound})
        for sec in rb:
            if sec != "records" and rb[sec] != after[sec]: H.refuse(NAME, "registry section %s changed" % sec)
    msg = ("%s, %s, %s and %s corrected; ASSEMBLY.md %s -> %s; %s; the review of decision 31 left as filed (pinned %s), "
           "its erratum %s" % (HWFW, ASM, S98R, S98L, was16, now16,
                               ("rebound: %s" % ", ".join(sorted(bound))) if bound else "no record bound to ASSEMBLY.md", rv[:16], ERRATA))
    if "--check" in argv:
        print("%s: CHECK ONLY, nothing written: %s" % (NAME, msg)); return 0
    for p in cur:
        H.write(root, p, new[p])
        if H.read(root, p) != new[p]: H.refuse(NAME, "%s read back differs" % p)
    if bound:
        H.write(root, H.REG, rq2)
        if H.read(root, H.REG) != rq2: H.refuse(NAME, "the registry read back differs")
    print("%s: %s%s" % (NAME, msg, "\nOWED: rules_render.py --requirements (the registry changed by the rebind)" if bound else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
