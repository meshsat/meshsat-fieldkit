#!/usr/bin/env python3
"""The board's own stackup, read in BOTH s-expression forms (MESHSAT-862, 16 September 2026).

KiCad writes a stackup layer on ONE line when a tool writes the block and across SEVERAL when pcbnew saves the
file itself, so a board that has been through `SaveBoard` since its stackup was written does not match a
single-line regular expression. Three places in this tree carried that regular expression, and on boards A, D
and E, whose files are in the expanded form, all three read "no stackup at all":

  * `fab_limits.py` reported rules RTE-001 and STK-001 as unanswerable on three boards that carry a stackup;
  * `export_jlc.sh` would have written "copper weight NOT DECLARED in the board file (ask before quoting)"
    into the fabricator's own order note for those boards;
  * the rule in `tests/test_order_codes.py` that checks the note against the board would have failed on them.

A reader in one place is the answer, which is the lesson `netclass.py` carries for the net-class map.
"""
import re

COPPER_OZ_MM = 0.035     # one ounce of copper is 0.035 mm; two is 0.070


def layer_thickness(text, name):
    """The thickness in mm of one named stackup layer, or None. Whitespace and line breaks do not matter."""
    for m in re.finditer(r'\(layer\s+"%s"' % re.escape(name), text):
        tail = text[m.end():m.end() + 400]
        nxt = tail.find('(layer "')          # never take a thickness from the NEXT layer's block
        if nxt >= 0: tail = tail[:nxt]
        t = re.search(r'\(thickness\s+([0-9.]+)', tail)
        if t: return float(t.group(1))
    return None


def outer_copper_mm(path_or_text):
    """The thicker of F.Cu and B.Cu in mm, or None where the board carries no stackup."""
    text = path_or_text
    if "\n" not in text and len(text) < 4096:
        try: text = open(path_or_text, encoding="utf-8", errors="replace").read()
        except OSError: return None
    th = [t for t in (layer_thickness(text, "F.Cu"), layer_thickness(text, "B.Cu")) if t]
    return max(th) if th else None


def outer_copper_oz(path_or_text):
    """The outer copper weight in ounces, read to the nearer half ounce, or None."""
    mm = outer_copper_mm(path_or_text)
    return None if mm is None else round(mm / COPPER_OZ_MM * 2) / 2.0
