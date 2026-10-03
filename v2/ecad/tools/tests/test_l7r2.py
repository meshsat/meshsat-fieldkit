"""Layer 7 record l7r2 (MESHSAT-1357, 3 October 2026; v2/docs/records/l7r2/): the Layer 7 items other layers assigned, round 2, held as
predicates on what l7r2_items.py computes.

The predicates: the committed .out is what the script prints and every input is pinned at its current sha256; the plate method reproduces
CASE-MARGINS' M14k at the worst before it judges a candidate; no RJ45 candidate read is picked (the PX0833's 42 V, the 233-330's fit
everywhere searched, the LTW's unread shield path) and the page says so; the bond's lugs fit H1's land and the stud's stack its 12; the
Radiall plug meets M17x, needs 5G MAIN's turn and IRIDIUM's move for M17g, and fails M18 at the worst (a finding); JST PH replaces SH and
the pin header; the cooler fans clear what hangs over them; W4-F17 stands; the CAD draft applies to a copy and refuses the tree's own
file before its release and a second run; the copied inputs name their commit and sha256; the record's files carry no long dashes and
no claim words; the clarifications are plain-ASCII drafts that send nothing. Software predicates on the record's own text and
arithmetic: they establish no property of any part, cable or case.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l7r2")
SCRIPT = os.path.join(REC, "l7r2_items.py")
OUT = os.path.join(REC, "l7r2_items.out")
PAGE = os.path.join(REC, "L7-R2-ITEMS.md")
DRAFT = os.path.join(REC, "apply_panel1450_coolers_r2.py")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l7r2 record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l7r2_items_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l7r2 record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l7r2_items.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _p(key):
    _M()
    assert key in _C["R"]["pred"], "no predicate %r" % key
    return _C["R"]["pred"][key]


def t_output_reproduced_and_inputs_pinned():
    m = _M()
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l7r2_items.out is not what the script prints"
    for rel in m.PINS.values():
        sha = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel


def t_the_rj45_is_not_picked_on_unread_or_failing_rows():
    assert _p("the shell 15 class reproduces CASE-MARGINS' M14j/M14k tightest worst within 0.02 (1.11 to 1.13)")
    assert _p("the PX0833 is rated under the PoE feed's 57 V")
    assert _p("the Glenair 233-330 shell 17 at A's place fails the plate")
    assert _p("no re-laid low row fits the 233-330 shell 17 (the least spare under 0)")
    assert _p("the LTW receptacle prints the PoE range")
    page = open(PAGE, encoding="utf-8").read()
    assert "no part read meets all three needs, so the coupler is not decided" in page


def t_the_bond_parts_fit():
    assert _p("the M4 lug fits H1's 12.0 ring with 1.0 to spare or more")
    assert _p("the stud's inside stack keeps within the 12 of the wall")
    assert _p("the strap at the drafted H1 site is over 250 mm, the alternative under 100 mm")


def t_the_jumper_plug_rows():
    assert _p("the Radiall plug's cable axis meets M17x's 1.38")
    assert _p("the Radiall plug at 30 degrees lands MAIN's cable below its place")
    assert _p("MAIN turned 26.5 degrees lands at or above its place")
    assert _p("the Radiall plug's crimp ferrule exceeds 2.58")
    assert _p("the Radiall plug's inner end lies beyond the class's 10.0 and M18 fails at the worst")
    s = _C["R"]["sma"]
    assert abs(s["land16"] - 49.33) < 0.01, "the landing model does not reproduce CASE-MARGINS' Z 49.33 at the class's 16.0 reach"


def t_the_fans():
    assert _p("JST PH covers -40 C and AWG 24, SH stops at AWG 28 and -25 C")
    assert _p("every cooler fan clears what hangs above it by 2.0 or more on the cooler's own height")
    assert _p("the cooler fan sits between the Xenarc and the top strip with under 1.5 on a side")
    assert _p("J_AB2 on board A stands inside D's rectangle and into D's underside")


def t_the_cad_draft_applies_to_a_copy_and_is_guarded():
    src = os.path.join(TOOLS, "panel1450.py")
    need(src, "panel1450.py")
    with tempfile.TemporaryDirectory() as d:
        cp = os.path.join(d, "panel1450.py"); shutil.copy(src, cp)
        r = subprocess.run([sys.executable, "-B", DRAFT, cp], capture_output=True, text=True)
        assert r.returncode == 0 and "checked" in r.stdout, r.stdout + r.stderr
        r = subprocess.run([sys.executable, "-B", DRAFT, cp, "--write"], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout
        t = open(cp, encoding="utf-8").read()
        assert '((-92.5, 46.745, -52.5, 86.745), 39.56, "CM5 slot 1 fan"' in t and '18.56, "CM5 slot 3 heatsink"' in t
        r = subprocess.run([sys.executable, "-B", DRAFT, cp], capture_output=True, text=True)
        assert r.returncode == 3, "a second run must refuse"
    env = dict(os.environ); env.pop("MESHSAT_L7R2_RELEASE", None)
    r = subprocess.run([sys.executable, "-B", DRAFT, src, "--write"], capture_output=True, text=True, env=env)
    assert r.returncode == 3 and "before the draft is released" in r.stdout


def t_copied_inputs_name_their_source():
    for f, commit in (("l5r2-tbd-layer7-rows-6902db8f.md", "6902db8f"), ("l8gnd-h1-f01-f07-226e9143.md", "226e9143"), ("l8r2-cooler-header-a441651a.md", "a441651a")):
        t = open(os.path.join(REC, "inputs", f), encoding="utf-8").read()
        assert t.startswith("<!-- COPIED INPUT") and ("at commit %s" % commit) in t and re.search(r"sha256 at that commit is [0-9a-f]{64}", t), f


def t_record_hygiene():
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(REC) for f in fs if not dp.endswith("held") and f.endswith((".md", ".py", ".txt", ".out"))]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert "—" not in t and "–" not in t, "a long dash in %s" % os.path.relpath(p, REC)
        if p.endswith(".md") and "inputs" not in p:
            m = CLAIM.search(t)
            assert not m, "a claim word %r in %s" % (m.group(0), os.path.relpath(p, REC))
    for f in os.listdir(os.path.join(REC, "clarification")):
        c = open(os.path.join(REC, "clarification", f), encoding="utf-8").read()
        assert all(ord(ch) < 128 for ch in c) and c.startswith("Draft for the owner to send (the session contacts no outside party)."), f
