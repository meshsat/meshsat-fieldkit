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

def _text(path_or_text):
    t = path_or_text
    if "\n" not in t and len(t) < 4096:
        try: t = open(path_or_text, encoding="utf-8", errors="replace").read()
        except OSError: return ""
    return t


def _region(text, head="(stackup"):
    """The balanced s-expression that starts at `head`, or "" when the board carries none.

    A paren walk and not a regular expression, because the block nests and KiCad writes it in two forms; the
    16 September finding is that one regular expression in three places read "no stackup" on three boards."""
    i = text.find(head)
    if i < 0: return ""
    depth = 0; j = i; q = False
    while j < len(text):
        c = text[j]
        if c == '"' and text[j - 1] != "\\": q = not q
        elif not q:
            if c == "(": depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0: return text[i:j + 1]
        j += 1
    return text[i:]


def layers(path_or_text):
    """Every stackup layer as a dict: name, type, thickness (mm), material, epsilon_r. Order is the file's.

    This is the reader the STACKUP rule needs and the one `outer_copper_mm` above always implied: a board's
    copper layer count, its per-layer copper weight and its dielectric constants are all in this block, and
    until 18 September 2026 nothing in this project read them as a set (rule STK-001 was decided by two
    verdicts about other things, and on three boards by a pair measurement with a denominator of zero)."""
    region = _region(_text(path_or_text))
    if not region: return []
    out = []; i = 0
    while True:
        i = region.find('(layer "', i)
        if i < 0: break
        blk = _region(region[i:], "(layer")
        if not blk: break
        d = {"name": re.search(r'\(layer\s+"([^"]*)"', blk).group(1)}
        for key, rx in (("type", r'\(type\s+"([^"]*)"'), ("material", r'\(material\s+"([^"]*)"')):
            m = re.search(rx, blk)
            if m: d[key] = m.group(1)
        for key, rx in (("thickness", r'\(thickness\s+([0-9.]+)'), ("epsilon_r", r'\(epsilon_r\s+([0-9.]+)')):
            m = re.search(rx, blk)
            if m: d[key] = float(m.group(1))
        out.append(d); i += len(blk)
    return out


def copper_layers(path_or_text):
    """The copper layers of the stackup, in order, or [] where the board carries no stackup."""
    return [L for L in layers(path_or_text) if L.get("type") == "copper"]


def dielectrics(path_or_text):
    """The dielectric layers (core and prepreg) of the stackup, in order."""
    return [L for L in layers(path_or_text) if L.get("type") in ("core", "prepreg")]
