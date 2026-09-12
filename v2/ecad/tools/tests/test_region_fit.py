#!/usr/bin/env python3
"""A region that cannot hold its parts must stop the chain, not print a line.

MESHSAT-862, 12 September 2026. Every placement generator ended its packing loop with
`print("WARNING region %s overflows by %.1f mm")` and then placed the parts that did not fit outside
the rectangle anyway. Nothing read it. B19's committed placement has overflowed six regions since the
day they were drawn, `IOCA` by 10.2 mm; the hard violations on its placed board are what that looks
like three stages downstream, and the coin-cell move of owner decision 11 added 22.9 mm more.
"""
import os, sys, glob, json, subprocess, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import reserved


def t_no_placement_generator_only_warns_about_a_region_it_overflows():
    bad = [os.path.basename(p) for p in sorted(glob.glob(os.path.join(TOOLS, "gen_pcb_*3.py")))
           if 'print("WARNING region %s overflows' in open(p, encoding="utf-8").read()]
    assert not bad, ("these generators still only print the overflow they then act on: %s" % ", ".join(bad))


def t_every_placement_generator_arms_the_gate_for_its_own_board():
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "gen_pcb_*3.py"))):
        src = open(p, encoding="utf-8").read()
        letter = os.path.basename(p)[len("gen_pcb_"):-len("3.py")]
        armed = any(('regionfit.allowance(%s%s%s)' % (q, letter, q)) in src for q in ('"', "'"))
        if "import regionfit" not in src or not armed:
            bad.append("%s does not arm regionfit for board %s" % (os.path.basename(p), letter))
        if "regionfit.note(" not in src:
            bad.append("%s never reports an overflow to the gate" % os.path.basename(p))
    assert not bad, "\n  ".join(bad)


def t_an_overflow_above_the_declared_allowance_exits_non_zero():
    """Run the gate for real: a board with no declaration refuses, and one that declares the number
    carries on. The exit code is the contract, because full.sh blocks on it."""
    prog = ("import sys; sys.path.insert(0, %r); import regionfit\n"
            "regionfit.allowance(%%r)\n"
            "regionfit.note('GAP12', 22.9)\n" % TOOLS)
    r = subprocess.run([sys.executable, "-c", prog % "b"], capture_output=True, text=True, timeout=60)
    assert r.returncode != 0, "an undeclared 22.9 mm overflow did not block:\n%s" % r.stdout
    assert "GAP12" in r.stdout and "reserved" in r.stdout, r.stdout
    r2 = subprocess.run([sys.executable, "-c", prog.replace("22.9", "1.2") % "a"],
                        capture_output=True, text=True, timeout=60)
    assert r2.returncode == 0, "a 1.2 mm overflow blocked a board that declares 1.5 mm:\n%s" % r2.stdout


def t_a_declared_allowance_carries_its_reason():
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(p, encoding="utf-8"))
        if d.get("region_overflow_allow_mm"):
            why = d.get("region_overflow_allow_mm_reason", "")
            assert len(why) > 60, "%s permits an overflow without saying why: %r" % (os.path.basename(p), why)


def t_a_region_rectangle_is_the_owners_not_only_the_tables_first_line():
    """The floor named `^REGIONS\\s*=`, which is the line the table opens on. Every rectangle, which is
    the floor plan itself, sat outside it, so widening a region to stop an overflow would have gone
    through without a word."""
    classes = reserved.load()
    for line in ('REGIONS = [',
                 '    ("GAP12", (-50, 33, -32, 97), ["BT1", "U6"], False),',
                 '            ("IOCB", (-52.0, 32.0, -23.0, 88.0), _ioc(1), True),'):
        hits = reserved._matches("gen_pcb_b3.py", line, classes)
        assert any("region" in n for n, _ in hits), "not reserved and must be: %s" % line.strip()[:60]
