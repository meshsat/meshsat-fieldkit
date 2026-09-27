#!/usr/bin/env python3
"""Post-route title swap (5 Sep 2026): the chains reuse the board's silk text items from the first generation, so a routed board can still carry the phase
and date of an earlier phase (A21 said A18, D7 said D5, B13 said B12). Rewrites every "REV A (X99)" and 2026-09-0N date in the board's free text items to the
given phase and date, and sets the title block the same way. Usage: retitle.py <board.kicad_pcb> <phase, e.g. A21> <date YYYY-MM-DD> [extra: old=>new ...]"""
import re, sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1]); phase, date = sys.argv[2], sys.argv[3]; extra = [a.split("=>") for a in sys.argv[4:]]
n = 0
for d in b.GetDrawings():
    if d.Type() != pcbnew.PCB_TEXT_T: continue
    t = d.GetText(); s = re.sub(r"REV A \([A-Z]\d+\)", "REV A (%s)" % phase, t); s = re.sub(r"2026-09-0\d", date, s)
    for old, new in extra: s = s.replace(old, new)
    if s != t: d.SetText(s); n += 1; print("retitle:", repr(t[:70]), "->", repr(s[:70]))
tb = b.GetTitleBlock(); tb.SetRevision("A (%s)" % phase); tb.SetDate(date); b.SetTitleBlock(tb)
pcbnew.SaveBoard(sys.argv[1], b); print("retitle: %d text items rewritten, title block A (%s) %s" % (n, phase, date))
