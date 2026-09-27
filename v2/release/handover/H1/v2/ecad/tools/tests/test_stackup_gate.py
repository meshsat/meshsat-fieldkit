"""The stackup rule's own instrument (rule STK-001, MESHSAT-862, 18 September 2026).

Before this gate existed, STK-001 was a BLOCKER decided entirely by verdicts about other questions: boards C,
D and E read PASS from `impedance_check PASS of 0`, a pair measurement that judged zero pairs, and boards B
and P read FAIL for a missed impedance target and for design classes under the fabricator's capability, which
are PAIR-001's and RTE-001's criteria. No board's stackup had been compared with anything.

The fixtures are board TEXT, because a stackup is text in the board file and this gate reads it without KiCad.
"""
import os, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import stackup_gate as G
import stackup_read as SR
import rules_status as S

TWO_LAYER = """(kicad_pcb (version 20240108)
  (setup
    (stackup
      (layer "F.SilkS" (type "Top Silk Screen"))
      (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
      (layer "F.Cu" (type "copper") (thickness 0.07))
      (layer "dielectric 1" (type "core") (thickness 1.44) (material "FR4 core") (epsilon_r %s) (loss_tangent 0.02))
      (layer "B.Cu" (type "copper") (thickness 0.07))
      (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
      (copper_finish "ENIG")
    )
  )
)
"""
NO_STACKUP = '(kicad_pcb (version 20240108)\n  (setup\n    (pad_to_mask_clearance 0)\n  )\n)\n'


def _board(text):
    fd, p = tempfile.mkstemp(suffix=".kicad_pcb"); os.write(fd, text.encode()); os.close(fd); return p


def _judge(text, declared="2L-2oz"):
    p = _board(text)
    try:
        # the repo's own root, because the RECORD the fixture is compared against lives in the tree; the
        # fixture's letter has no order folder, so the paperwork clause reads nothing and says so
        return G.judge(p, "fixture", declared=declared)
    finally:
        os.unlink(p)


def t_a_board_whose_dielectric_constant_is_not_the_records_is_refused():
    """THE DEFECTIVE FIXTURE, and it is not hypothetical: both two-layer boards in this tree carry 4.6 on
    their core where the fabricator's own capability document says 4.5, because their files were written
    before the 16 September correction that read the number off the capability page instead of the impedance
    page. Nothing computed moves on either board today, which is exactly why it needed a gate and not a
    memory: the board and the record disagreed in silence."""
    r = _judge(TWO_LAYER % "4.6")
    assert r["compared"] >= 7, "the fixture was not compared against the record at all: %s" % r["notes"]
    assert any("dielectric constant" in b for b in r["bad"]), \
        "a board carrying a dielectric constant the named stack does not have is not refused: %s" % r


def t_the_same_board_at_the_records_number_passes():
    """THE ACCEPTABLE FIXTURE: one number different, and nothing else about the board changes."""
    r = _judge(TWO_LAYER % "4.5")
    assert r["compared"] >= 7 and not r["bad"], "a board that IS the record it declares is refused: %s" % r["bad"]


def t_a_board_with_no_stackup_block_is_inconclusive_and_never_a_pass():
    """Absence is never a pass, which is the whole reason this rule needed its own instrument: the verdict it
    used to be decided by could return PASS on a denominator of zero."""
    r = _judge(NO_STACKUP)
    assert r["compared"] == 0 and r["board_copper"] == 0
    assert any("no stackup" in n for n in r["notes"]), r["notes"]


def t_a_stack_this_project_holds_no_record_of_is_inconclusive_and_says_so():
    r = _judge(TWO_LAYER % "4.5", declared="SOME-OTHER-STACK")
    assert r["compared"] == 0 and any("no transcribed record" in n for n in r["notes"]), r["notes"]


def t_the_reader_reads_both_forms_of_the_block():
    """KiCad writes the block on one line per layer when a tool writes it and across several when pcbnew saves
    the file; three tools carried a single-line regular expression and read "no stackup" on three boards (16
    September 2026). The reader is one place now and this holds it to both forms."""
    one = SR.copper_layers(TWO_LAYER % "4.5")
    many = SR.copper_layers((TWO_LAYER % "4.5").replace(") (", ")\n        ("))
    assert len(one) == 2 and len(many) == 2, "the reader does not read both forms: %d and %d" % (len(one), len(many))
    assert [d["epsilon_r"] for d in SR.dielectrics(TWO_LAYER % "4.5")] == [4.5]


def t_the_stackup_rule_is_decided_by_its_own_instrument():
    """The mapping is the other half of the fix: while `impedance_check` decided STK-001, a board with no
    differential pair at all was credited with a verified stackup."""
    cov = S.coverage()["STK-001"]
    names = [n.strip() for n in str((cov.get("verification") or {}).get("verdict") or "").split(",") if n.strip()]
    assert "stackup_gate" in names, "STK-001 does not name the gate that reads a stackup: %s" % names
    assert "impedance_check" not in names, \
        "STK-001 is still decided by the pair measurement, which returns PASS of 0 on a board with no pair: %s" % names
