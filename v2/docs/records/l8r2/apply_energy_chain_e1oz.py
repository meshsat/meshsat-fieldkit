#!/usr/bin/env python3
"""apply_energy_chain_e1oz.py: a text correction of v2/ecad/tools/pcb_energy_chain.yaml for the integrator (Layer 8 record l8r2,
round 3, item 6, MESHSAT-1357, 3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The finding (record l9stk at 7388a84b, section 12): the energy chain says board E's bands are 2 oz, in two stages, while record
l9stk decides board E at 1 oz outer and 0.5 oz inner with the high-current conductors shared by both outer faces (its decision
"(L9STK E)", pending integration). The two texts:
  DOCK_ENTRY  conductor  "board E's 2 oz power bands to the dock block pads", basis "gen_pcb_e3.py bands; IPC-2221 at 2 oz"
  SHORE_INPUT conductor  "board E's input bands at 2 oz", basis "gen_pcb_e3.py"
What it writes: the two conductor texts at 1 oz on both outer faces, each with the width its declared rating needs at 1 oz by
decision 35's model (track_current.width_for_current, 10 K; this record's l8r2_drafts.out section 11 computes them and the test
holds the texts to that computation): 25 A needs 12.26 mm on each of two 1 oz faces, 10 A needs 2.76 mm on each of two or 8.15 mm
on one. The ratings (25.0 and 10.0 A), every protective element, every other stage and every other line are unchanged, so the
chain's four coordination checks read the same numbers; whether the copper as laid meets the widths is a finding this record files
(l8r2 section 3f), not a number this correction changes. Board A's BOARD_A_NODE already reads "1 oz outer and 0.5 oz inner".

What a run checks: the decision register carries l9stk's board E decision, ruled, at 1 oz outer (a title carrying "(L9STK E)"),
so that the correction follows the decision and never precedes it; each old text occurs exactly once (or, once the new texts are
all present and no old text is, the file is already corrected: nothing is written and the run exits 0, so a second run is a no-op);
the result re-parses as YAML; every stage reads back identical to the original but the two conductors' `what` and `basis`, and
those two read back as written; after a write the file is read back and parsed again.

Usage:  apply_energy_chain_e1oz.py [--chain PATH] [--registry PATH] [--check | --write]
  --chain     the chain file to correct (default v2/ecad/tools/pcb_energy_chain.yaml of this tree)
  --registry  the decision register read for l9stk's decision (default v2/ecad/tools/pcb_decisions.yaml of this tree)
  --check     (default) compute and verify, write nothing
Exit 0: checked, written, or already corrected; 3: refused (l9stk's decision is not in the register, an old text is not found
exactly once, or the result does not parse or read back)."""
import copy
import os
import sys

import yaml

NAME = "apply_energy_chain_e1oz"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
CHAIN = os.path.join(REPO, "v2", "ecad", "tools", "pcb_energy_chain.yaml")
REGISTRY = os.path.join(REPO, "v2", "ecad", "tools", "pcb_decisions.yaml")
MARK = "(L9STK E)"

# (stage id, old text, new text, the conductor's what and basis after the correction)
_DOCK_OLD = ('   conductor: {what: "board E\'s 2 oz power bands to the dock block pads", rating_a: 25.0,\n'
             '               basis: "gen_pcb_e3.py bands; IPC-2221 at 2 oz"}\n')
_DOCK_WHAT = "board E's power bands to the dock block pads, 1 oz on both outer faces (record l9stk), the In2 pour at 0.5 oz"
_DOCK_BASIS = ("gen_pcb_e3.py power copper; record l9stk decides board E at 1 oz outer with the pack path shared by both faces; "
               "25 A at 10 K needs 12.26 mm on each of two 1 oz faces (decision 35's model, track_current.width_for_current); "
               "dc_drop measures the copper itself on the routed board")
_DOCK_NEW = ('   conductor: {what: "%s", rating_a: 25.0,\n'
             '               basis: "%s"}\n' % (_DOCK_WHAT, _DOCK_BASIS))
_SHORE_OLD = '   conductor: {what: "board E\'s input bands at 2 oz", rating_a: 10.0, basis: "gen_pcb_e3.py"}\n'
_SHORE_WHAT = "board E's input bands, 1 oz on both outer faces (record l9stk)"
_SHORE_BASIS = ("gen_pcb_e3.py; record l9stk decides board E at 1 oz outer; 10 A at 10 K needs 2.76 mm on each of two 1 oz faces "
                "or 8.15 mm on one (decision 35's model, track_current.width_for_current)")
_SHORE_NEW = '   conductor: {what: "%s", rating_a: 10.0,\n               basis: "%s"}\n' % (_SHORE_WHAT, _SHORE_BASIS)

EDITS = [("DOCK_ENTRY", _DOCK_OLD, _DOCK_NEW, _DOCK_WHAT, _DOCK_BASIS),
         ("SHORE_INPUT", _SHORE_OLD, _SHORE_NEW, _SHORE_WHAT, _SHORE_BASIS)]
WIDTHS = {"DOCK_ENTRY": (25.0, "12.26 mm on each of two 1 oz faces"),
          "SHORE_INPUT": (10.0, "2.76 mm on each of two 1 oz faces or 8.15 mm on one")}


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def decided(registry):
    """l9stk's board E decision is in the register, ruled, at 1 oz outer."""
    d = yaml.safe_load(open(registry, encoding="utf-8"))
    hits = [x for x in (d or {}).get("decisions") or [] if MARK in str(x.get("title", ""))]
    if len(hits) != 1:
        refuse("the register %s carries %d decisions marked %s, not one: l9stk's board E decision is not integrated, and this "
               "correction follows it" % (os.path.relpath(registry, REPO) if registry.startswith(REPO) else os.path.basename(registry), len(hits), MARK))
    if str(hits[0].get("status")) != "ruled" or "1 oz outer" not in str(hits[0].get("title")):
        refuse("the decision marked %s is not ruled at 1 oz outer" % MARK)


def stages(text):
    d = yaml.safe_load(text)
    if not isinstance(d, dict) or not isinstance(d.get("stages"), list):
        refuse("the chain does not parse to a mapping with a stages list")
    return d


def patched(text):
    """(new text, already corrected?)"""
    news = [text.count(n) for _s, _o, n, _w, _b in EDITS]
    olds = [text.count(o) for _s, o, _n, _w, _b in EDITS]
    if all(n == 1 for n in news) and not any(olds):
        return text, True
    new = text
    for sid, old, rep, _w, _b in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("%s: the old text occurs %d times, not once" % (sid, new.count(old)))
        if new.count(rep) != 0:
            refuse("%s: the new text is already present beside the old" % sid)
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    a, b = stages(text), stages(new)
    if {k: v for k, v in a.items() if k != "stages"} != {k: v for k, v in b.items() if k != "stages"}:
        refuse("a top-level entry other than the stages changed")
    if [s.get("id") for s in a["stages"]] != [s.get("id") for s in b["stages"]]:
        refuse("the stages' order or ids changed")
    want = {sid: (w, bs) for sid, _o, _n, w, bs in EDITS}
    for sa, sb in zip(a["stages"], b["stages"]):
        if sa.get("id") in want:
            exp = copy.deepcopy(sa)
            exp["conductor"]["what"], exp["conductor"]["basis"] = want[sa["id"]]
            if sb != exp:
                refuse("%s does not read back as the old stage with its conductor's what and basis corrected" % sa["id"])
            if "2 oz" in str(sb["conductor"]) or float(sb["conductor"]["rating_a"]) != float(sa["conductor"]["rating_a"]):
                refuse("%s still names 2 oz or its rating moved" % sa["id"])
        elif sb != sa:
            refuse("stage %s changed, and only DOCK_ENTRY's and SHORE_INPUT's conductors may" % sa.get("id"))
    return new, False


def main(argv):
    flags = [a for a in argv if a in ("--check", "--write")]
    chain = CHAIN if "--chain" not in argv else argv[argv.index("--chain") + 1]
    registry = REGISTRY if "--registry" not in argv else argv[argv.index("--registry") + 1]
    known = {"--check", "--write", "--chain", "--registry", chain, registry}
    if len(flags) > 1 or any(a not in known for a in argv):
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    write = flags == ["--write"]
    decided(registry)
    text = open(chain, encoding="utf-8").read()
    new, done = patched(text)
    if done:
        print("%s: ALREADY CORRECTED, nothing to write (%s)" % (NAME, ", ".join(s for s, *_r in EDITS)))
        return 0
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(chain, "w", encoding="utf-8").write(new)
    back = open(chain, encoding="utf-8").read()
    if back != new:
        refuse("the written file does not read back as the corrected text")
    stages(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
