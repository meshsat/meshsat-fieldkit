#!/usr/bin/env python3
"""The two minors the independent check of stream rf2walk (round 3, set 12's CHECK-3) carried on RF-002's walk
(`v2/ecad/tools/tx_inhibit.py`, MESHSAT-1357, 29 September 2026):
  m1  the EMCON toggle's declaration named no lugs, so a toggle wired across lugs that never close together (1 and 3 of
      the APEM 5636ADKB-2V) or across the other lever position's contact (2 and 3) read as the line's source: every
      declaration now names the contact lug pair, and the predicate requires the two live pins to be exactly that pair;
  m2  the board key defaulted to None, and a call without it matched a declaration on any board: the key is now
      required through the predicate and the four functions that pass it on, and the predicate refuses a missing key and
      a declaration without its lugs.
Each old text asserted exactly once, the result re-parsed with `ast`; refuses a second run. Run: python3 <this file>."""
import ast, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TX = os.path.join(TOP, "v2/ecad/tools/tx_inhibit.py")

PAIRS = [
    ('''    dict(board="C", ref="SW_EMCON", value=r"EMCON locking toggle", line="TX_INHIBIT_n",
         why="the panel's EMCON toggle, its contact between TX_INHIBIT_n and GND: the one element that asserts the inhibit "
             "(gen_sch_c.py, the SW_EMCON part line; PANEL.md, the Switches row)"),''',
     '''    dict(board="C", ref="SW_EMCON", value=r"EMCON locking toggle", line="TX_INHIBIT_n", lugs=("1", "2"),
         why="the panel's EMCON toggle, its contact between TX_INHIBIT_n and GND: the one element that asserts the inhibit "
             "(gen_sch_c.py, the SW_EMCON part line; PANEL.md, the Switches row)",
         lugs_src="APEM 5000 series sheet, page 6, the 5636 row: lugs 1 and 2 closed in lever position I, 2 and 3 in "
                  "position III, lug 2 the common (v2/vendor/seals/apem-5000-series-datasheet-rs-copy.pdf; gen_sch_c.py's "
                  "note above SW_SOS). Which position the hinged cover forces is an assembly item"),'''),
    ('''def _is_toggle(k, nl, ref):
    """The declaration (EMCON_TOGGLES, or a fixture's through judge) when `ref` on board `k` is a declared EMCON toggle:
    its board (when `k` is given; a direct call with k None reads the rest only), its reference, its value, one pin on the
    declared line, one on ground and every other pin unconnected; else None. A part that matches a reference but is wired
    otherwise is not the toggle."""
    if ref not in nl["comps"]: return None
    for d in _TOGGLES_NOW:
        if ref != d["ref"] or (k is not None and k != d["board"]): continue
        if not re.search(d["value"], value(nl, ref), re.I): continue
        live = [x for x in (nl["pin"].get((ref, p), "") for p in pins_of(nl, ref)) if not _dead(x)]
        if len(live) == 2 and live.count(d["line"]) == 1 and sum(1 for x in live if is_ground(x)) == 1:
            return d
    return None''',
     '''def _is_toggle(k, nl, ref):
    """The declaration (EMCON_TOGGLES, or a fixture's through judge) when `ref` on board `k` is a declared EMCON toggle:
    its board, its reference, its value, and its declared contact lugs (`lugs`, the pair the maker's sheet closes
    together) carrying the declared line and ground, one each in either order, with every other pin unconnected; else
    None. A part that matches a reference but is wired otherwise is not the toggle: a line on a lug outside the pair (the
    other lever position's throw, or two throws that never close together) is not. THE BOARD KEY AND THE LUGS ARE
    REQUIRED (the independent check of stream rf2walk, round 3, minors): a call without `k` matched a declaration on any
    board, and a declaration without lugs let a miswired toggle read as the source, so both are refused, not defaulted."""
    if k is None: raise ValueError("_is_toggle: the board key is required")
    if ref not in nl["comps"]: return None
    for d in _TOGGLES_NOW:
        if len(d.get("lugs") or ()) != 2: raise ValueError("EMCON toggle declaration %s/%s names no contact lug pair" % (d.get("board"), d.get("ref")))
        if ref != d["ref"] or k != d["board"]: continue
        if not re.search(d["value"], value(nl, ref), re.I): continue
        live = {p: x for p, x in ((p, nl["pin"].get((ref, p), "")) for p in pins_of(nl, ref)) if not _dead(x)}
        if set(live) != set(d["lugs"]): continue
        nets = list(live.values())
        if nets.count(d["line"]) == 1 and sum(1 for x in nets if is_ground(x)) == 1:
            return d
    return None'''),
    ("def _switch_board(nl, k=None):", "def _switch_board(nl, k):"),
    ("def _source_output(nl, ref, pin, s, k=None):", "def _source_output(nl, ref, pin, s, k):"),
    ("def drive_net(nl, n, k=None):", "def drive_net(nl, n, k):"),
    ("def _line_sources(nl, s, k=None):", "def _line_sources(nl, s, k):"),
]


def main():
    t = open(TX, encoding="utf-8").read()
    if 'lugs=("1", "2")' in t: print("apply_walk_minors: REFUSED: already applied"); return 2
    t2 = t
    for old, new in PAIRS:
        if t2.count(old) != 1: print("apply_walk_minors: REFUSED: expected once, found %d: %r" % (t2.count(old), old[:70])); return 2
        t2 = t2.replace(old, new)
    assert t2 != t
    ast.parse(t2)
    open(TX, "w", encoding="utf-8").write(t2)
    print("apply_walk_minors: m1 the toggle's contact lug pair declared and required; m2 the board key required")
    return 0


if __name__ == "__main__":
    sys.exit(main())
