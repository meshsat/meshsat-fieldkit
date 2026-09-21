#!/usr/bin/env python3
"""A pre-lay group's pairs come from the BOARD, never from a capped report (21 September 2026).

`full.sh` runs the DRC over the whole placed board and hands the report to `stub_router.py`, which takes its
work list from `unconnected_items`. **KiCad's DRC export lists at most about 499 of them**, and board A's
placed board is AT that cap, so which of a group's pairs appear is decided by a truncation.

Measured on two arms launched in the same minute from the same tools, A99 and A99C: identical placements
(436 footprints at the same positions and orientations, 1,225 tracks, `place_audit` 0 of 19 on both), DSNs
differing by exactly the 85 fence areas the arm is about, and yet the switching pre-lay closed **16 of 16 on
one and 19 of 20 on the other**. Re-running the DRC on both placed boards read-only gives 499 entries and
SIXTEEN switching pairs on each, `/FE_SW2`, `/HF_SW2`, `/PA_SW2` and `/PD_SW2` with four apiece and
**`/POE_SW2` absent from both**: in one run those four pairs fell inside the cap and were given copper, in the
other they did not. Two arms then differ by four pre-laid connections for a reason that is neither board's.

The fix is to ask the board rather than the report. Every pad, track, via and zone whose net is NOT one of
the group's is set to NO NET in a COPY, so it can raise no unconnected item of its own; the DRC over that
copy therefore lists the group's pairs and nothing else, far under the cap. The geometry is untouched, the
copy is thrown away, and what comes back is a report of the same shape `stub_router` already reads, so
nothing downstream changes. A net absent from the board is named and skipped rather than assumed empty.

Usage: prelay_pairs.py <board.kicad_pcb> <out.json> <net,net,...>   -> writes the report; exit 0.
       The nets may be given with or without their leading slash."""
import json
import os
import subprocess
import sys
import tempfile

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))


def _norm(n):
    return (n or "").strip().lstrip("/")


def strip_to(board_path, nets, out_pcb):
    """A copy of the board on which only `nets` carry a net at all. Returns (kept items, board)."""
    b = pcbnew.LoadBoard(board_path)
    want = {_norm(n) for n in nets if _norm(n)}
    zero = b.FindNet("")
    if zero is None:                       # without it nothing is stripped and the report is the whole
        raise SystemExit("prelay_pairs: this KiCad has no no-net item to assign, so the board cannot be "
                         "stripped; refusing rather than answering from the capped report in silence")
    kept = 0
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if _norm(p.GetNetname()) in want:
                kept += 1
            elif zero is not None:
                p.SetNet(zero)
    for t in b.GetTracks():
        if _norm(t.GetNetname()) in want:
            kept += 1
        elif zero is not None:
            t.SetNet(zero)
    for z in b.Zones():
        if _norm(z.GetNetname()) in want:
            kept += 1
        elif zero is not None and not z.GetIsRuleArea():
            z.SetNet(zero)
    b.BuildConnectivity()
    b.Save(out_pcb)
    return kept, b


def pairs_from_board(board_path, nets, keep_dir=None):
    """The group's unconnected pairs, as KiCad reports them on a board carrying only those nets."""
    d = keep_dir or tempfile.mkdtemp()
    stem = os.path.splitext(os.path.basename(board_path))[0]
    out_pcb = os.path.join(d, stem + ".kicad_pcb")
    pro = os.path.splitext(board_path)[0] + ".kicad_pro"
    if os.path.exists(pro):                                   # a board judged without its project file is
        open(os.path.join(d, stem + ".kicad_pro"), "w").write(open(pro).read())   # judged at the default class
    kept, _ = strip_to(board_path, nets, out_pcb)
    rep = os.path.join(d, "drc.json")
    subprocess.run([os.path.join(HERE, "drc.sh"), out_pcb, rep], capture_output=True, text=True, timeout=1800)
    if not os.path.exists(rep):
        raise SystemExit("prelay_pairs: the DRC wrote no report for the stripped board at %s" % out_pcb)
    return json.load(open(rep)), kept


def main(argv):
    if len(argv) < 3:
        print("usage: prelay_pairs.py <board.kicad_pcb> <out.json> <net,net,...>")
        return 2
    board, out, nets = argv[0], argv[1], [n for n in argv[2].split(",") if n.strip()]
    rep, kept = pairs_from_board(board, nets)
    un = rep.get("unconnected_items", [])
    want = {_norm(n) for n in nets}
    seen = set()
    for v in un:
        for it in v.get("items", []):
            t = it.get("description") or ""
            if "[" in t and "]" in t:
                seen.add(_norm(t.split("[")[1].split("]")[0]))
    json.dump(rep, open(out, "w"))
    missing = sorted(w for w in want if w not in seen)
    print("prelay_pairs: %d item(s) of %d net(s) kept; the stripped board reports %d unconnected pair(s)"
          % (kept, len(want), len(un)))
    print("prelay_pairs: nets with no open pair on this board: %s" % (", ".join(missing) or "(none)"))
    if len(un) >= 490:
        print("prelay_pairs: WARNING the stripped board is still near KiCad's own list cap (%d): the report "
              "this writes may itself be truncated, which is the defect this tool exists to remove" % len(un))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
