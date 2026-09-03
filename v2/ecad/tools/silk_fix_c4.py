#!/usr/bin/env python3
"""Silk corrections on the routed C4 board (no re-route): LED labels west of the LEDs, toggle labels 13 mm from their switch, e-paper legend
and BACK WALL apart, battery bar numbers under their LEDs, nameplate text clear of the data-matrix square, title C4. Mirrors gen_pcb_c*.py."""
import sys, pcbnew
from pcbnew import VECTOR2I, FromMM
OX, OY = 297.0, 210.0
def P(x, y): return VECTOR2I(FromMM(OX + x), FromMM(OY - y))
b = pcbnew.LoadBoard(sys.argv[1])
LED_LABELS = {"MSTR WARN", "MSTR CAUT", "TX", "SOS ACTIVE", "SAT", "MESH", "LTE", "GPS", "SHORE", "CHARGE", "MSG"}
TOGGLES = {"SOS": 42.0, "EMCON": 0.0, "ZEROIZE": -42.0}
def add(txt, x, y, size, thick, halign="center"):
    t = pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetPosition(P(x, y)); t.SetLayer(pcbnew.F_SilkS); t.SetTextSize(VECTOR2I(FromMM(size), FromMM(size))); t.SetTextThickness(FromMM(thick))
    t.SetHorizJustify({"left": pcbnew.GR_TEXT_H_ALIGN_LEFT, "right": pcbnew.GR_TEXT_H_ALIGN_RIGHT}.get(halign, pcbnew.GR_TEXT_H_ALIGN_CENTER)); b.Add(t)
n = 0
for d in list(b.GetDrawings()):
    if not isinstance(d, pcbnew.PCB_TEXT) or d.GetLayer() != pcbnew.F_SilkS: continue
    s = d.GetText(); x, y = d.GetPosition().x / 1e6 - OX, OY - d.GetPosition().y / 1e6
    if s in LED_LABELS and abs(x + 114) < 3: d.SetPosition(P(-125.0, y)); d.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_RIGHT); n += 1
    elif s in TOGGLES and abs(x - 170) < 1: d.SetPosition(P(x, TOGGLES[s] + 13.0)); n += 1
    elif s == "guard closed = safe" and abs(x - 170) < 1:
        sw = min(TOGGLES.values(), key=lambda v: abs(y - (v - 20.0))); d.SetPosition(P(x, sw - 13.0)); n += 1
    elif s.startswith("E-PAPER: STATUS"): d.SetPosition(P(x, 130.0)); n += 1
    elif s == "BACK WALL (+Y)": d.SetPosition(P(-160.0, 145.6 - 6.0)); n += 1
    elif "REV A (C3)" in s: d.SetText(s.replace("(C3)", "(C4)")); n += 1
    elif s.startswith("BATT  20"): b.Remove(d); n += 1
    elif s.startswith("MESHSAT FIELD KIT   P/N"): d.SetText("MESHSAT FIELD KIT   P/N MS709-C   REV A   2026"); d.SetTextSize(VECTOR2I(FromMM(1.8), FromMM(1.8))); d.SetTextThickness(FromMM(0.3)); n += 1
    elif s.startswith("S/N ____"): d.SetText("S/N ____________   MFR MESHSAT"); d.SetTextSize(VECTOR2I(FromMM(2.0), FromMM(2.0))); d.SetTextThickness(FromMM(0.3)); n += 1
add("BATT %", -88.0, 123.0, 2.0, 0.3, "right")
for x, pct in zip((-82, -76, -70, -64, -58), ("20", "40", "60", "80", "100")): add(pct, x, 127.5, 1.5, 0.25)
pcbnew.SaveBoard(sys.argv[1], b); print("silk items changed:", n, "+ 6 added")
