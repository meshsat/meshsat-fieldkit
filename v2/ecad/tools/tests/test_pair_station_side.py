#!/usr/bin/env python3
"""Which way is "out" of a pair's station, and the footprint origin that is not a centre.

Measured on D's /USB_D8, 11 September 2026 (MESHSAT-862). The pre-router decides which side of a station the
corridor leaves from by taking the vector from the footprint's centre to the station midpoint and dotting it
with the normal of the P-N line. It read that centre from `GetPosition()`, which is the footprint's ORIGIN, and
on every connector in this tree the origin is PIN 1. For a pair on the END row of a header the origin therefore
lies exactly ON the station line, the dot product is zero, no flip happens and the default direction points
straight INTO the pin field: the corridor end came out at (58.80, 85.35), between J_HARN1's two columns, and
the fan into the pads had no path. With the pads' own centre the same pair lays, and D goes 4 of 5 to 5 of 5.

The rule is mechanical and reads the source, because the failure is a silent geometric default: no exception,
no log line, just a pair that does not lay and a message about smoothing."""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.environ.get("PAIR_SIDE_SRC", os.path.join(TOOLS, "pair_preroute.py"))


def t_the_centre_of_a_footprint_is_its_pads():
    s = open(SRC, errors="replace").read()
    assert re.search(r"^def fp_centre\(fp\):", s, re.M), "pair_preroute.py has no fp_centre helper"


def t_no_station_side_test_uses_the_footprint_origin():
    """The exact shape that was wrong, four times over: averaging two parent footprints' GetPosition()."""
    s = open(SRC, errors="replace").read()
    bad = [ln.strip()[:120] for ln in s.splitlines()
           if re.search(r"GetPosition\(\)\.x \+ \w+\.GetPosition\(\)\.x", ln)]
    assert not bad, "a station-side test still averages two footprint origins:\n  " + "\n  ".join(bad)


def t_the_helper_falls_back_when_a_footprint_has_no_pad():
    """A footprint with no pad (a logo, a mechanical marking) must not divide by zero here."""
    s = open(SRC, errors="replace").read()
    parts = s.split("def fp_centre(fp):", 1)
    assert len(parts) == 2, "pair_preroute.py has no fp_centre helper to check"
    body = parts[1].split("\ndef ", 1)[0]
    assert "if not pts:" in body, "fp_centre has no empty-pad fallback"
