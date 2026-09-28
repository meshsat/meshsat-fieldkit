#!/usr/bin/env python3
"""T7 of DECOUPLING.md 8.1: DEC-001's registry text of section 8.2, and its coverage row naming the new tools.

For the integrator (the one writer of both files), run from anywhere: python3 apply_dec001_registry.py <checkout root>
It changes two files and nothing else:
  v2/ecad/tools/pcb_rules.yaml           DEC-001's source_status, sources, acceptance_criteria and rationale become
                                         section 8.2's text. The two sha256 notes 8.2 printed as 16 digits and "..."
                                         (SCAA082A, AN 574) are written whole, read from the held files on 29 Sep 2026.
                                         Everything else in the entry stays: requirement, classification, waiver
                                         policy, boards, and DEC-001's own clause "The distance itself is derived per
                                         device ..." (T7 keeps it open).
  v2/ecad/tools/pcb_rules_coverage.yaml  DEC-001's row: `implementation` names the class rules and the fan selection,
                                         `verification.fixtures` the four test files, and a `_classes_why` says what
                                         moved; `maturity: ENFORCED` and `gap_category: HEURISTIC_AS_LAW` stay, as T7
                                         says, until the per-device derivation exists for classes D and L.
It asserts each old text is present exactly once, that the new text differs, re-parses both files as YAML, runs
rules_lib.validate() on the patched registry, and refuses a second run (the new text already present).

AFTERWARDS, IN THE SAME COMMIT (T8): `python3 v2/ecad/tools/rules_render.py` and commit the re-rendered pages
(PCB-OPEN-PAIRS.md and the rule pages carry DEC-001's text and its coverage row); `rules_render.py --check` fails the
suite's t_the_documents_are_generated_and_not_hand_maintained until they are. This script does not render: a render
writes the tree's generated pages, which is the integrator's act."""
import os, sys, hashlib

OLD_RULE = '''   source_status: SOURCE_UNVERIFIED
   sources: []
   acceptance_criteria: >
     Each declared decoupling entry states its pin, its distance, its via count and the loop it forms; an
     entry beyond the declared distance carries a written reason. The distance itself is derived per device
     from the current's spectral content, not taken as one project-wide number.
   rationale: >
     Loop inductance, not capacitance, decides high-frequency decoupling. The project's present 3 mm number is
     a heuristic and is recorded as one.
'''

NEW_RULE = '''   source_status: PARTIALLY_VERIFIED
   sources:
    - {title: "AN4938 Getting started with STM32H74xI/G and STM32H75xI/G MCU hardware development", issuer: STMicroelectronics,
       revision: "Rev 7, October 2024", clause: "2.2 (p.12), 7.4 (p.32), 9.3 and Figure 21 (pp.38-39)",
       url_or_path: "v2/vendor/st/st-an4938-rev7.pdf", accessed: "2026-09-26",
       note: "sha256 @an4938@; per-pin values, the 4.7 uF tied to the pins, no distance; same side as the MCU for every package except BGA (9.3, Figure 21)"}
    - {title: "TPA6132A2 25-mW DirectPath Stereo Headphone Amplifier", issuer: "Texas Instruments", revision: "SLOS597B, July 2017",
       clause: "9 and 9.1 (p.17)", url_or_path: "v2/vendor/ti/ti-tpa6132a2.pdf", accessed: "2026-09-26",
       note: "sha256 @tpa6132a2@; the only maker distance in the tree, 5 mm"}
    - {title: "High-Speed Layout Guidelines", issuer: "Texas Instruments", revision: "SCAA082A, August 2017", clause: "2.4 (p.13)",
       url_or_path: "v2/vendor/ti/ti-scaa082a-high-speed-layout-guidelines.pdf", accessed: "2026-09-26",
       note: "sha256 @scaa082a@; lowest value closest, pad directly to the plane with two or three vias"}
    - {title: "AN 574 Printed Circuit Board (PCB) Power Delivery Network (PDN) Design Methodology", issuer: "Altera (Intel)",
       revision: "AN-574-1.0, May 2009", clause: "pp.6, 13, 16", url_or_path: "v2/vendor/standards/intel-an574.pdf",
       accessed: "2026-09-26", note: "sha256 @an574@; location sensitivity against plane dielectric; top against bottom mounting"}
    - {title: "the part makers' layout clauses, one per class", issuer: "TI, Diodes, Microchip, Silicon Labs, Raspberry Pi",
       revision: "as listed in v2/docs/feasibility/DECOUPLING.md section 4", clause: "section 4 of that page",
       url_or_path: "v2/docs/feasibility/DECOUPLING.md", accessed: "2026-09-26",
       note: "one maker in the tree gives a millimetre figure (TPA6132A2, 5 mm); the class rules follow the makers' words"}
   acceptance_criteria: >
     Each declared decoupling entry states its pin, its distance, its via count and the loop it forms, and names its
     class, by the role its maker gives it and never by its value, and the maker clause behind it. Class R (a converter's own power-stage capacitor): on the IC's side, the input capacitor's rail
     pad within 3.0 mm of VIN and declared at VIN, no via in the loop, output capacitors declared against the output
     loop; the fan does not apply to the converter's own power-stage parts; never on the other side. Class D (a
     capacitor a maker ties to a supply pin, any value) and class L (a regulator's output or VCAP capacitor, with the
     maker's value floor and ESR bound): rail pad within 3.0 mm in the part's own-pin window, ground pad to the plane
     by its own via; where a maker states a distance, that distance is a hard limit; on a board already assembled
     with SMD parts on both sides, a seat on the other side is judged by its in-plane distance plus the stackup's via
     allowance, and is never inside the escape fan of a fanned part on either side, never over a through-hole part,
     and never used for a part whose maker names the same side; otherwise a justified deviation naming the
     capacitor, its distance and its loop estimate. Class A (a
     supply pin behind a series resistor, or a backup reservoir): the nearest free seat outside the fan at the pin end
     of its RC, with no high-current conductor between or alongside (provisional for the battery protection parts
     until the qualified review of review section 2). Class B1 (bulk the maker calls rail bulk): value and count, no
     pin distance, declared against the regulator that feeds the rail and seated toward it, its distance printed.
     Class B2 (bulk no maker places): 6.0 mm from the pin it is declared against. The 3.0 and 6.0 mm are project
     screens, not maker numbers. The distance itself is derived per device from the current's spectral content, not
     taken as one project-wide number; until that derivation exists for a device, its screen decides only between a
     pass and a justified deviation. A justified deviation is counted as such and never as a pass.
   rationale: >
     Loop inductance decides high-frequency decoupling, and what forms the loop differs by class: the switching
     loop of a converter, the track from a capacitor to its pin where the rail is not a plane, the far-side vias, and
     nothing that matters behind a series resistor. A regulator's output capacitor is also part of its stability. One
     maker document in the tree gives a distance (decision 42, ruled 26 September 2026).
'''

OLD_COV = ''' DEC-001: {implementation: "bypass_slots.py, bypass_place.py", verification: {tool: intent_checks.py, verdict: intent_decoupling, fixtures: tests/test_board_gates.py, report: bypass_seats.py},
   maturity: ENFORCED, gap_category: HEURISTIC_AS_LAW,
'''
NEW_COV = ''' DEC-001: {implementation: "decoupling_rules.py (the class rules, one limit per class, the allowance, the far side, the own via), fan_select.py (one fan selection with escape.py), bypass_search.py (one seat search), bypass_slots.py, bypass_place.py, escape.py with escape_cost.py (the per-part cost of the windows, the converter openings and the far side), intent.py (a declaration without a class or a basis is refused)", verification: {tool: intent_checks.py, verdict: intent_decoupling, fixtures: "tests/test_board_gates.py, tests/test_decoupling_rules.py, tests/test_decoupling_board.py, tests/test_escape_cost.py, tests/test_intent_bypass_class.py", report: bypass_seats.py},
   maturity: ENFORCED, gap_category: HEURISTIC_AS_LAW,
   _classes_why: "Decision 42 (26 September 2026, v2/docs/feasibility/DECOUPLING.md section 6) rules the seat of a decoupling capacitor by its CLASS, the role its maker gives it, and T1 to T10 of its section 8.1 put that in the tools (stream d6dec, 27 to 29 September 2026): the limit is the class's and is measured rail pad to pin in the gate and both placers, never read off the value string; the fan set is the escape pass's own; an allowance names its capacitor and is counted as a justified deviation, never as a pass; the other side is a seat only on a board already assembled on both sides, outside every fan box and every through-hole courtyard, at its in-plane distance plus the stackup's via allowance; a class D or L capacitor's ground pad is asked for a via of its own. The category stays HEURISTIC_AS_LAW (T7): the 3.0 mm screen still separates a pass from a justified deviation for classes D and L until the per-device distance is derived from SI-001's edge rates. bypass_seats.py, the report named here, still walks to a flat 3.0 mm measured to the capacitor's centre; it decides no rule, and moving it onto decoupling_rules.limit is an open item of stream d6dec.",
'''


def sha(root, rel):
    return hashlib.sha256(open(os.path.join(root, rel), "rb").read()).hexdigest()


def main(a):
    if len(a) != 1: print(__doc__); return 2
    root = os.path.abspath(a[0]); tools = os.path.join(root, "v2", "ecad", "tools")
    sys.path.insert(0, tools)
    import yaml
    rp = os.path.join(tools, "pcb_rules.yaml"); cp = os.path.join(tools, "pcb_rules_coverage.yaml")
    rules = open(rp, encoding="utf-8").read(); cov = open(cp, encoding="utf-8").read()
    if "source_status: PARTIALLY_VERIFIED\n   sources:\n    - {title: \"AN4938 Getting started" in rules or "_classes_why: \"Decision 42" in cov:
        raise SystemExit("apply_dec001_registry: already applied (the new text is present); refusing a second run")
    new_rule = NEW_RULE
    for k, rel in (("an4938", "v2/vendor/st/st-an4938-rev7.pdf"), ("tpa6132a2", "v2/vendor/ti/ti-tpa6132a2.pdf"),
                   ("scaa082a", "v2/vendor/ti/ti-scaa082a-high-speed-layout-guidelines.pdf"),
                   ("an574", "v2/vendor/standards/intel-an574.pdf")):
        new_rule = new_rule.replace("@%s@" % k, sha(root, rel))
    assert "@" not in new_rule
    # the old text must be DEC-001's: present once, and after the line that names it
    i = rules.find(" - id: DEC-001\n"); j = rules.find(OLD_RULE)
    if rules.count(OLD_RULE) != 1 or i < 0 or not (i < j < rules.find(" - id: ", i + 5)):
        raise SystemExit("apply_dec001_registry: DEC-001's old text is not in pcb_rules.yaml exactly once inside its entry")
    if cov.count(OLD_COV) != 1:
        raise SystemExit("apply_dec001_registry: DEC-001's old coverage row is not in pcb_rules_coverage.yaml exactly once")
    rules2 = rules.replace(OLD_RULE, new_rule); cov2 = cov.replace(OLD_COV, NEW_COV)
    assert rules2 != rules and cov2 != cov
    reg = yaml.safe_load(rules2); cmap = yaml.safe_load(cov2)
    r = next(x for x in reg["rules"] if x.get("id") == "DEC-001")
    assert r["source_status"] == "PARTIALLY_VERIFIED" and len(r["sources"]) == 5, r.get("sources")
    assert "derived per device" in r["acceptance_criteria"] and "justified deviation" in r["acceptance_criteria"]
    c = cmap["coverage"]["DEC-001"]
    assert c["gap_category"] == "HEURISTIC_AS_LAW" and c["maturity"] == "ENFORCED" and "decoupling_rules.py" in c["implementation"]
    for s in r["sources"]:
        if s["url_or_path"].startswith("v2/") and not os.path.exists(os.path.join(root, s["url_or_path"])):
            raise SystemExit("apply_dec001_registry: a source is not held: %s" % s["url_or_path"])
    import rules_lib
    errs, _w = rules_lib.validate(reg=reg)
    mine = [e for e in errs if "DEC-001" in e]
    if mine: raise SystemExit("apply_dec001_registry: the patched DEC-001 does not validate: %s" % mine)
    open(rp, "w", encoding="utf-8").write(rules2); open(cp, "w", encoding="utf-8").write(cov2)
    # re-read from disk, as a reader will
    yaml.safe_load(open(rp, encoding="utf-8")); yaml.safe_load(open(cp, encoding="utf-8"))
    print("apply_dec001_registry: DEC-001 patched in pcb_rules.yaml (5 sources, PARTIALLY_VERIFIED, section 8.2's criteria) "
          "and its coverage row in pcb_rules_coverage.yaml; %d other validation error(s) in the registry, none on DEC-001. "
          "Next, in the same commit: python3 v2/ecad/tools/rules_render.py (T8)." % len(errs))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
