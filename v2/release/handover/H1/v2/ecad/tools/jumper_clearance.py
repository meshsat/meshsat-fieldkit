#!/usr/bin/env python3
"""A solder jumper's pads carry the board's class clearance (15 September 2026, MESHSAT-862, D12's grid route). KiCad's
SolderJumper footprints declare a local pad clearance of zero so their two pads may sit 0.3 mm apart without a violation;
the DSN export hands that zero to the router, which then runs another net's track against the pad, and KiCad's DRC judges
that track at ITS class clearance: D12 read one hard clearance item, /PCM_XTI against JP2 pad 1. Every pad of a footprint
whose library name contains "SolderJumper" gets the board's minimum clearance as its local clearance; the two pads of one
jumper are 0.3 mm apart, which is over 0.127, so nothing inside the part changes.

Usage: jumper_clearance.py <board.kicad_pcb>      run by full.sh after the placement, on every board."""
import sys
import pcbnew


def main(a):
    b = pcbnew.LoadBoard(a[0]); clr = max(b.GetDesignSettings().m_MinClearance, pcbnew.FromMM(0.127)); n = 0; parts = []
    for fp in b.GetFootprints():
        if "SolderJumper" not in str(fp.GetFPID().GetLibItemName()): continue
        for p in fp.Pads():
            p.SetLocalClearance(int(clr)); n += 1
        parts.append(fp.GetReference())
    if n: pcbnew.SaveBoard(a[0], b)
    print("jumper_clearance: %d pad(s) of %d solder jumper(s) set to %.3f mm (%s)" % (n, len(parts), clr / 1e6, ", ".join(parts) or "none"))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
