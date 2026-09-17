#!/usr/bin/env python3
"""A clearance between two net CLASSES in the DSN (17 September 2026, rule ANA-001, appendix 32.222).

A sense line beside a switching net is the thing ANA-001 refuses, and nothing this pipeline gives Freerouting could ask
for that: KiCad's custom rules never reach the DSN, and a class clearance of 0.50 mm cannot escape the sense pins
themselves. The DSN structure section carries `class_class` rules, which apply between two classes and not inside
either; `route_one.sh` writes them from FR_CLASS_CLEAR. This holds the edit's shape on a fixture DSN: the rule lands
inside the structure section, a class the DSN does not carry is skipped and named, and nothing is written when the
knob is unset."""
import os, re, subprocess, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = """(pcb fixture
  (parser (string_quote ") (space_in_quoted_tokens on))
  (structure
    (layer F.Cu (type signal))
    (rule (width 250) (clearance 127))
  )
  (placement)
  (library)
  (network
    (net POE_CS (pins U16-16))
    (class SENSE POE_CS (rule (width 250) (clearance 180)))
    (class SW POE_SW2 (rule (width 500) (clearance 127)))
  )
  (wiring)
)
"""


def _edit(spec):
    """Run route_one.sh's PYCC block alone on the fixture, the way the script runs it."""
    src = open(os.path.join(TOOLS, "route_one.sh"), encoding="utf-8").read()
    i = src.index("<<'PYCC'") + len("<<'PYCC'\n"); j = src.index("\nPYCC", i)
    code = src[i:j]
    d = tempfile.mkdtemp(prefix="class-clear-"); fn = os.path.join(d, "x.dsn"); open(fn, "w").write(FIXTURE)
    r = subprocess.run([sys.executable, "-", fn, spec], input=code, capture_output=True, text=True)
    return r.stdout + r.stderr, open(fn).read()


def t_a_class_pair_rule_lands_inside_the_structure_section():
    out, dsn = _edit("SENSE:SW:0.5")
    assert "1 rule(s) written" in out, out
    st = dsn[dsn.index("(structure"):dsn.index("(placement")]
    assert "(class_class (classes SENSE SW) (rule (clearance 0.5000)))" in st, "the rule is not inside the structure section:\n" + dsn


def t_a_class_the_dsn_does_not_carry_is_named_and_skipped():
    out, dsn = _edit("SENSE:HV:0.5")
    assert "0 rule(s) written" in out and "HV not in the DSN" in out, out
    assert "class_class" not in dsn


def t_the_knob_is_read_by_the_launcher_and_is_off_by_default():
    s = open(os.path.join(TOOLS, "route_one.sh"), encoding="utf-8").read()
    assert 'if [ -n "${FR_CLASS_CLEAR:-}" ]' in s, "route_one.sh does not read FR_CLASS_CLEAR, or reads it unconditionally"
    doc = open(os.path.join(TOOLS, "route_one.sh"), encoding="utf-8").read()
    assert "class_class" in doc and "ANA-001" in doc, "the knob does not say which rule it serves"


def t_board_a_gives_its_declared_sensitive_nets_a_class_of_their_own_ahead_of_the_switching_patterns():
    """A class cannot be kept away from itself: POE_CS sat in SW beside POE_SW2, the very net ANA-001 asks it to
    keep 0.50 mm from. The placement generator reads the board's sensitive list and puts every declared net in a
    SENSE class, listed BEFORE the pattern table so the sensitive net wins over a switching pattern that names it."""
    s = open(os.path.join(TOOLS, "gen_pcb_a3.py"), encoding="utf-8").read()
    assert '"SENSE": (' in s, "gen_pcb_a3.py declares no SENSE class"
    assert "pcb_sensitive.yaml" in s, "the SENSE class does not take its nets from the board's sensitive list"
    assert 'PATTERNS = [(n, "SENSE") for n in _sens_nets] + PATTERNS' in s, \
        "the sensitive patterns are not put ahead of the table, so a switching pattern naming the same net would win"


def t_board_e_gives_its_declared_sensitive_nets_a_class_of_their_own_too():
    s = open(os.path.join(TOOLS, "gen_pcb_e3.py"), encoding="utf-8").read()
    assert 'NETCLASS("SENSE")' in s, "gen_pcb_e3.py declares no SENSE class"
    assert "pcb_sensitive.yaml" in s and 'PATTERNS = [(n, "SENSE") for n in _sens_nets] + PATTERNS' in s, \
        "board E's sensitive nets do not take the SENSE class ahead of the power patterns (TRK_LSENSE would stay in PWR beside TRK_SW2)"
