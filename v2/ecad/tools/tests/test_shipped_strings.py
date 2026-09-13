#!/usr/bin/env python3
"""A string that was meant to be formatted and was not (MESHSAT-862, 13 September 2026).

`value` is what reaches the silk, the schematic, the BOM's Comment column and the operator who matches parts
at JLCPCB. B19 carries three values reading "1.1 V hub core S%d": the per-slot loop formats every other
argument it passes and nobody appended `% s` to that one, so the three 1.1 V hub core bucks all describe a
slot that has no number. It is the same defect as the footprint `%.2f` of 5 September, where a label
placeholder left unfilled made `FootprintLoad` return None with no message, and `write()` has refused a
footprint containing `%.` ever since.

Two floors, because the string can be born in two places: `kisch.part` refuses it at the source, and
`verify_deliverable` refuses a folder whose BOM carries one, which is the last point before a fab reads it.

A tolerance is not a conversion: "26.7k 1%" ends at the percent sign, and "50% duty" has a space after it.
Only a percent followed by its own flags and a type letter is matched.
"""
import os, re, csv, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V2 = os.path.dirname(os.path.dirname(TOOLS))
RX = re.compile(r"%[-+#0]*[0-9]*(?:\.[0-9]+)?[diouxXeEfFgGcrs]")


def t_the_pattern_matches_a_conversion_and_not_a_tolerance():
    for v in ("1.1 V hub core S%d", "REV A (%s)", "%.2f mm", "board %03d"):
        assert RX.search(v), "a real placeholder went unmatched: %r" % v
    for v in ("26.7k 1%", "50% duty", "100u 10V X7R 1210", "SMBJ5.0A", "74LVC08APW", "90.9k 1%"):
        assert not RX.search(v), "a legitimate value was matched: %r" % v


def t_kisch_refuses_an_unformatted_placeholder_in_a_part_value():
    import kisch
    n = len(kisch.P)
    try:
        kisch.part("U9999", "Device", "R", "TPS62933DRLR buck 1.1 V hub core S%d", "R", {"1": "A", "2": "B"})
    except SystemExit as e:
        assert "unformatted placeholder" in str(e), "refused for the wrong reason: %s" % e
        assert len(kisch.P) == n, "the part was appended before the refusal"
        return
    raise AssertionError("kisch.part accepted a value with an unformatted placeholder; it would reach the BOM")


def t_kisch_accepts_a_tolerance():
    import kisch
    kisch.part("R9999", "Device", "R", "26.7k 1%", "R", {"1": "A", "2": "B"})
    kisch.P[:] = [p for p in kisch.P if p["ref"] != "R9999"]


def t_verify_deliverable_gates_the_bom_comment():
    src = open(os.path.join(TOOLS, "verify_deliverable.py")).read()
    assert "unformatted placeholder" in src, "the deliverable gate does not read its BOM comments for one"
    assert "diouxXeEfFgGcrs" in src, "the gate is not matching a conversion"


def t_no_shipped_deliverable_carries_one():
    """The scope stated honestly: every folder under release/, which is what a fab is given."""
    bad = []
    for f in sorted(glob.glob(os.path.join(V2, "release", "*", "boards", "*", "*-bom.csv"))
                    + glob.glob(os.path.join(V2, "release", "*", "order", "*", "*.csv"))):
        try: rows = list(csv.DictReader(open(f, errors="replace")))
        except Exception: continue
        for r in rows:
            c = r.get("Comment", "") or ""
            if RX.search(c): bad.append("%s: %s" % (os.path.basename(os.path.dirname(f)), c[:60]))
    assert not bad, "a shipped BOM carries an unformatted placeholder:\n  " + "\n  ".join(bad[:10])
