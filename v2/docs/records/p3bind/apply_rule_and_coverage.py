#!/usr/bin/env python3
"""Register constraints_bound.py: the rule it serves, its coverage, its declared inputs and the drivers that run it
(p3bind, MESHSAT-1357, 27 September 2026). FOR THE INTEGRATOR: the files it patches have one writer, and it is not
this worker.

WHAT IT REGISTERS. `v2/ecad/tools/constraints_bound.py` writes one verdict per board, `constraints_bound_<letter>`,
and nothing in the registry names it, so it decides no rule and no page reads it. It serves handover layer 9's
criterion 9.8 ("constraints handed to layout written per board", v2/docs/handover/LAYER-STATUS.md) under the rule of
the independent review of H2: derived data a designer will follow names the inputs it was computed from, and a check
fails when the committed inputs move.

THE RULE ID: DOC-003, the next free id of DOCUMENTATION_CONTROL. DOC-001 holds a deliverable folder to the phase the
tree declares and DOC-002 asks that a number a DOCUMENT OF THE RELEASE PACKAGE asserts carry its artefact's hash
(its documents in scope are the order notes, its phase RELEASE_PACKAGE). This rule is their sibling one stage
earlier: the document is the constraint sheet, the artefacts are the declared phase's netlist and intent file, and
the phase is SCHEMATIC, because the sheet is what LAYOUT ENTRY is handed. It is not PI-001: PI-001 judges the copper
of a routed board against the model, and this judges a page against the calculation. Its full text is RULE below.

THE FIVE PATCHES, each asserting its anchor stands exactly once, that the new text is absent (a second run is
refused, file by file, before anything is written), that the file changed, and re-parsing what it wrote:
  1. tools/pcb_rules.yaml             the rule DOC-003, after DOC-002 (YAML re-read; the registry validated);
  2. tools/pcb_rules_coverage.yaml    DOC-003's coverage entry after DOC-002's, and the `rule_set_fingerprint` stamp
                                      moved from the registry's fingerprint before the patch to the one after it
                                      (tests/test_rule_gate_mapping.py holds the stamp to the registry);
  3. tools/rules_status.py            CONFIG_INPUTS["constraints_bound.py"], and ONE WORD of `_config_state`: the
                                      template gains `{LETTER}`, the board's letter in capitals, because a sheet is
                                      A.md and a template could only say `{letter}`. Without it the entry would be the
                                      glob `*.md`, and an edit of board B's sheet would stale board A's reading;
  4. tools/retake_schematic_phase.py  WRITERS["constraints_bound_<letter>"], the command the re-take runs;
  5. tools/gate_sweep.sh              the same command in the sweep, and its verdict in the list the sweep clears
                                      (left out with --no-sweep).

WHAT THE INTEGRATOR DOES AFTER IT (this script does none of it; each writes the tree's evidence or pages). TRIED IN
THIS ORDER in a throwaway clone on the box at 91f4bab6 (box/trial.sh, box/trial-91f4bab6.log):
  * `python3 v2/ecad/tools/rules_lib.py validate`: 60 rules, 0 errors, 0 warnings;
  * the re-take on the box in a throwaway clone (retake_schematic_phase.py --run --in-place --routed), which now runs
    `constraints_bound.py --board <letter>` on every board (80 commands where there were 73) and leaves
    constraints_bound_<letter>.verdict.json in each phase directory's routed/. In the trial DOC-003 then read PASS,
    CURRENT_CANDIDATE, BOUND on all seven boards;
  * `rules_render.py`: fourteen pages change (CURRENT-EVIDENCE.md, PCB-GAP-REGISTER.md, PCB-GOLDEN-RULES.md,
    PCB-OPEN-PAIRS.md, PCB-PROTOTYPE-UNKNOWNS.md, PCB-RULE-COVERAGE.md, the seven PCB-RULE-STATUS pages and
    REQUIREMENTS-TRACE.md): 60 rules where there were 59, 345 rule-board pairs where there were 338. Until the
    re-take lands DOC-003 is a rule with no reading, one more layout-entry line per board;
  * `decisions_render.py`: OWNER-DECISIONS-OPEN.md states the number of pairs (338 to 345). WITHOUT IT THE SUITE FAILS
    on test_decision_register.t_the_page_is_generated_and_not_hand_maintained, and on nothing else: the trial's suite
    read 2049 passed, 1 failed, 3 skipped before it and that test's file 5 passed, 0 failed after it
    (box/trial-91f4bab6-decisions-render.txt);
  * v2/docs/handover/LAYER-STATUS.md row 9.8 and known gap 8 name the check (records/p3bind/README.md, O6).

Usage: apply_rule_and_coverage.py [--root <repository>] [--check] [--no-sweep]
  --check   reads, asserts every anchor and prints what would change; writes nothing
Exit: 0 applied (or, with --check, applicable), 1 an assertion failed and NOTHING was written, 2 usage.
"""
import os, sys, ast, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

RULE = '''
 - id: DOC-003
   false_positive_analysis: >
     A WRONG REFUSAL here looks like this: a sheet is failed although a layout following it would lay the same
     copper. Three shapes. (1) An input moved and no row did: a netlist or an intent file is regenerated with a
     new part that carries no rail, or with nothing but a new `written` stamp, the hashes part, and the sheet
     fails with every width unchanged (set 6 did exactly this to four boards of seven). That refusal is kept on
     purpose: nothing can know that no row moved until the calculation has been run again, running it takes
     under a second, and `constraints_bound.py --emit <letter> --sheet` prints the sheet re-bound with the rows
     that moved marked, which is none. (2) The commit a sheet names for an input is not the one git names, in a clone
     whose history was cut short: the comparison is made only where git answers for the tree and the clone is not
     shallow, and an extraction with no history is told apart and not failed for it. (3) A cell that differs in
     form and not in value (11.9 for 11.92): cells are compared as the tool prints them, because a sheet that
     rounds is a sheet typed by hand, and a sheet typed by hand is the defect. What is NOT protected against and
     is written here rather than hidden: a table's note column is the sheet's own words and is not compared, so
     a number quoted in a note can go stale; the other sections of a sheet (pairs, placement, spacing, thermal)
     are bound by nothing yet, and the sheet says so in its `older` line; and the check proves that the sheet
     equals the calculation, never that the calculation's model is right, which is PI-001's question and
     decision 35's.
   domain: DOCUMENTATION_CONTROL
   short_name: a constraint sheet is bound to its inputs
   requirement: >
     Every figure a layout constraint sheet hands to layout as a number to follow (a band width, a barrel count,
     the current a conductor is judged at) is the output of a committed calculation on the committed netlist and
     intent file of the board's declared phase (its board file, for a board with no schematic); the sheet names
     those inputs by path, sha256 and commit, with the model and the stack the figures were computed on; and the
     sheet says, where it is used, which of its sections were re-read on that candidate and which are readings
     of an older one.
   classification: PROJECT_DECISION
   applicability: UNIVERSAL_FOR_THIS_PROJECT
   risk_class: [DOCUMENTATION, THERMAL, RELIABILITY]
   release_effect: BLOCKER
   source_status: NOT_REQUIRED_FOR_PROJECT_DECISION
   sources:
     - title: "Independent review of MeshSat handover H2, section 3 A, 'Stale electrical constraints could guide the next design incorrectly'"
       issuer: "the independent reviewer of handover H2, saved as the owner pasted it"
       revision: "27 September 2026"
       clause: "section 3 A, and section 6 item 2"
       url_or_path: v2/docs/reviews/2026-09-27-h2-independent-review.md
       accessed: "2026-09-27"
       note: >
         "H3 should regenerate them against its actual inputs, or mark them superseded exactly where the
         engineer would use them. The supplied old widths must not become current layout requirements." It is a
         review of a delivered package and no standard: the rule is this project's decision, taken on it.
   acceptance_criteria: >
     Per board, on the tree as committed. (1) The sheet's opening carries one `bound` block naming at least one
     input. (2) Every input it names has the sha256/16 of the committed file, is the file the calculation reads
     and the declared phase's artefact, and names the commit git gives for the file's last change; every input
     the calculation reads is named. (3) The model (function, decision, temperature rise, hole plating) and the
     stack (name, outer and inner copper) the sheet states are the calculation's, and the calculation's copper is
     the stack table's. (4) Every cell of the sheet's power tables but the note equals what the calculation prints
     on those inputs, row for row, and section 2 holds no table of widths the calculation does not print. (5) The
     committed output of the calculation equals a fresh run. (6) No typed list of the calculation names a rail the
     intent file no longer declares. (7) No row's note still opens with the mark a re-binding by machine leaves on
     a row that moved or is new: each such row is explained from the intent file's own text.
   rationale: >
     At handover H2 board A's sheet gave VIN_RAW as 12.31 A and 11.92 mm on one outer face while the committed
     intent file declared 14.10 A, which the same model sizes at 15.29 mm. The sheet had been written on one
     candidate, the boards had moved, and nothing compared the page with its inputs. It was re-bound by hand, and
     set 6 moved every board's netlist again within hours. A page a designer follows is derived data, and derived
     data is as current as the last time somebody compared it with its source.
   failure_mode: "A power band is laid at the width an older declaration asked for, carries more than its copper is rated for in a sealed case, and the page that said so still reads as the constraint record."
   verification_method: [SCRIPT, CALCULATION]
   verification_phase: SCHEMATIC
   automation_feasibility: AUTOMATABLE
   boards_affected: [ALL]
   interfaces_affected: [NONE]
   implementation_location: "v2/docs/layout-constraints/calc/rail_widths.py (the calculation), v2/docs/layout-constraints/<sheet>.md (the bound block and section 2), constraints_bound.py (the check)"
   evidence_scope: [schematic_sha256, configuration_sha, stackup, tools_tree_sha, rule_set_fingerprint]
   owner: SESSION
   waiver_policy: {allowed: false, authority: OWNER, evidence: "", scope: "", expiry: "", residual_risk: ""}
   maturity_at_writing: ENFORCED
'''
RULE_ANCHOR = "\n - id: OUT-001\n"

COVERAGE = '''
 DOC-003: {implementation: "v2/docs/layout-constraints/calc/rail_widths.py, and each sheet's bound block and section 2",
   verification: {tool: constraints_bound.py, verdict: "constraints_bound_<letter>", fixtures: tests/test_constraints_bound.py},
   maturity: ENFORCED, gap_category: NONE,
   note: "27 September 2026 (MESHSAT-1357, stream p3bind; the independent review of handover H2, section 3 A). ONE VERDICT PER BOARD
     from the first day: a sheet is a board's, and a set reading would fail board A for board B's stale table, the defect this map
     has split six rules for. constraints_bound.py reads each sheet's bound block (its inputs by path, sha256/16 and commit, the
     model, the stack), the committed files, calc/rail_widths.out and the calculation itself run in memory, and compares the
     sheet's power tables cell by cell with what the calculation prints now. It parses (a table reader that splits on the pipe
     character, a block reader, json, PyYAML for board E5's chain stage, an S-expression reader for E5's nets) and uses no regular
     expression. Its fixtures are a tree of their own: the H2 defect with its own numbers (an intent file moved from 12.31 A to
     14.10 A under a sheet that says 11.92 mm, where the model says 15.29), a width narrowed by hand, a sheet with no declaration
     and a stale output fail, and a consistent tree passes; one test judges the real tree. It records the netlist by sha and by
     content, the intent file, the sheet, the output and the calculation by sha, so a re-take binds to the candidate
     (rules_status._bound) and goes stale when any of them moves (CONFIG_INPUTS). On the set 6 candidate at the binding of
     27 September it reads PASS on the seven boards. A sheet re-bound by machine (--emit --sheet) carries a mark on every row
     that moved or is new and fails on the mark until the row is explained. WHAT IT DOES NOT DO, named rather than implied: a
     table's note column is not compared beyond that mark; sections 1 and 3 onward of a sheet are bound by nothing and each
     sheet's `older` line says so;
     calc/stack_solves.out (the pair and RF line solves, atlc) has no check of this kind; and it says nothing about whether the
     model is right, which is PI-001 and decision 35. The set verdict constraints_bound (the output file byte for byte) is written
     beside the boards' and decides no rule."}
'''
COVERAGE_ANCHOR = "\n OUT-001: {implementation:"

CONFIG = '''# constraints_bound.py (27 September 2026, MESHSAT-1357 stream p3bind; rule DOC-003). What `judge` reads beyond the netlist, which it
# only hashes (recorded by sha and content16, phase_artefacts.record): the board's sheet, where the declaration and the tables it
# judges are (recorded as `sheet`; {LETTER} is the letter in capitals, A.md, E5.md); calc/rail_widths.py, RUN in memory and loaded by
# path, so the code bundle does not see it (recorded as `rail_widths`), and its committed output (`rail_widths_out`); the intent file
# the calculation reads the rails from (`intent`); the committed board file a sheet declares (`board_file`: on E5 it is the design
# and binds the reading; on the six others it is the layout the sheet's older sections were read on, and is compared by the sha the
# reading recorded); the energy chain, read for board E5's stage alone (`chain`, recorded on E5; on the six other boards it is
# compared by its commit's date, conservative, because one template serves every board). stackup_write.STACKS, track_current and
# via_current are imported modules and are in the reading's code bundle. phase_artefacts finds the declared phase through the
# manifest and the routeflow profiles, which is finding an artefact and not configuration (as block_contract.py's entry says).
CONFIG_INPUTS["constraints_bound.py"] = ("../docs/layout-constraints/{LETTER}.md", "../docs/layout-constraints/calc/rail_widths.py",
                                         "../docs/layout-constraints/calc/rail_widths.out", "{phase}/out/{stem}-intent.json",
                                         "{phase}/{stem}.kicad_pcb", "tools/pcb_energy_chain.yaml")
'''
CONFIG_ANCHOR = ('CONFIG_INPUTS["check_pcb_c.py"] = ("tools/boards/c.json", "../cad/zstack.json") + '
                 'CONFIG_INPUTS["intent_checks.py"]\n')
FORMAT_OLD = "tmpl.format(letter=letter, phase=d, stem=stem)"
FORMAT_NEW = "tmpl.format(letter=letter, LETTER=letter.upper(), phase=d, stem=stem)"

WRITER = '''    # constraints_bound.py (rule DOC-003, 27 September 2026, stream p3bind): the board's layout constraint sheet against the
    # committed inputs of THE TREE THE TOOL SITS IN (it takes no netlist argument: a sheet is bound to the committed files, and the
    # staged copies of a --verdict-dir run are those files). It writes through VERDICT_DIR alone; E5 has no netlist and needs none.
    "constraints_bound_<letter>": ("constraints_bound.py", ["{T}/constraints_bound.py", "--board", "{L}"], None),
'''
WRITER_ANCHOR = '    "interfaces_<letter>":      ("interfaces.py", ["{T}/interfaces.py"], None),\n'

SWEEP_CLEAR_OLD = "          sensitive_nodes assembly_set rf_line ledger_verify; do\n"
SWEEP_CLEAR_NEW = "          sensitive_nodes assembly_set rf_line ledger_verify constraints_bound_$L; do\n"
SWEEP_RUN = '''# THE SHEET LAYOUT IS HANDED IS THE CANDIDATE'S (rule DOC-003, 27 September 2026). It judges the committed sheet against
# the committed netlist and intent file of the tree, never this sweep's regenerated copies: a sheet names what is committed.
run "constraint sheet" python3 $T/constraints_bound.py --board $L --out-dir out
'''
SWEEP_RUN_ANCHOR = "# THE NODES WHERE MILLIVOLTS DECIDE (rule ANA-001)."


class Refused(Exception):
    pass


def need(cond, why):
    if not cond: raise Refused(why)


def insert_before(text, anchor, new, name, mark):
    need(mark not in text, "%s already carries %r: this script has run on it" % (name, mark))
    need(text.count(anchor) == 1, "%s: the anchor %r stands %d time(s), not once" % (name, anchor.strip()[:60], text.count(anchor)))
    out = text.replace(anchor, new + anchor)
    need(out != text, "%s: the patch changed nothing" % name)
    return out


def insert_after(text, anchor, new, name, mark):
    need(mark not in text, "%s already carries %r: this script has run on it" % (name, mark))
    need(text.count(anchor) == 1, "%s: the anchor %r stands %d time(s), not once" % (name, anchor.strip()[:60], text.count(anchor)))
    out = text.replace(anchor, anchor + new)
    need(out != text, "%s: the patch changed nothing" % name)
    return out


def swap(text, old, new, name):
    need(new not in text, "%s already carries %r: this script has run on it" % (name, new.strip()[:60]))
    need(text.count(old) == 1, "%s: %r stands %d time(s), not once" % (name, old.strip()[:60], text.count(old)))
    out = text.replace(old, new)
    need(out != text, "%s: the patch changed nothing" % name)
    return out


def fingerprint_of(tools, registry_text):
    """The registry's fingerprint for a text, computed by the tree's own rules_lib in a process of its own."""
    code = ("import sys, json; sys.path.insert(0, %r); import rules_lib as R; "
            "reg = R._yaml().safe_load(sys.stdin.read()); print(R.fingerprint(reg))" % tools)
    r = subprocess.run([sys.executable, "-c", code], input=registry_text, capture_output=True, text=True, timeout=120)
    need(r.returncode == 0 and len(r.stdout.strip()) == 16, "rules_lib could not fingerprint the registry: %s" % r.stderr[-300:])
    return r.stdout.strip()


def main(argv):
    known = {"--root": 1, "--check": 0, "--no-sweep": 0}
    i = 0
    while i < len(argv):
        if argv[i] not in known or (known[argv[i]] and i + 1 >= len(argv)):
            print(__doc__.split("Usage:")[1].split("Exit:")[0].rstrip()); return 2
        i += 1 + known[argv[i]]
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else ROOT
    tools = os.path.join(root, "v2", "ecad", "tools")
    paths = {k: os.path.join(tools, k) for k in ("pcb_rules.yaml", "pcb_rules_coverage.yaml", "rules_status.py",
                                                 "retake_schematic_phase.py", "gate_sweep.sh")}
    try:
        import yaml
        need(os.path.isfile(os.path.join(tools, "constraints_bound.py")), "%s holds no constraints_bound.py" % tools)
        need(os.path.isfile(os.path.join(tools, "tests", "test_constraints_bound.py")), "the fixtures are not in %s" % tools)
        old = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}
        new = dict(old)
        # 1. the rule
        new["pcb_rules.yaml"] = insert_before(old["pcb_rules.yaml"], RULE_ANCHOR, RULE.rstrip("\n") + "\n", "pcb_rules.yaml",
                                              " - id: DOC-003\n")
        reg = yaml.safe_load(new["pcb_rules.yaml"])
        ids = [r["id"] for r in reg["rules"]]
        need(ids.count("DOC-003") == 1 and len(ids) == len(yaml.safe_load(old["pcb_rules.yaml"])["rules"]) + 1,
             "pcb_rules.yaml does not re-parse with exactly one more rule")
        need(ids.index("DOC-003") == ids.index("DOC-002") + 1, "DOC-003 does not stand after DOC-002")
        # 2. its coverage, and the stamp
        before, after = fingerprint_of(tools, old["pcb_rules.yaml"]), fingerprint_of(tools, new["pcb_rules.yaml"])
        need(before != after, "the registry's fingerprint did not move with a new rule")
        c = insert_before(old["pcb_rules_coverage.yaml"], COVERAGE_ANCHOR, COVERAGE.rstrip("\n") + "\n",
                          "pcb_rules_coverage.yaml", " DOC-003: {")
        c = swap(c, 'rule_set_fingerprint: "%s"' % before, 'rule_set_fingerprint: "%s"' % after, "pcb_rules_coverage.yaml")
        new["pcb_rules_coverage.yaml"] = c
        cov = yaml.safe_load(c)
        e = cov["coverage"]["DOC-003"]
        need(e["verification"]["verdict"] == "constraints_bound_<letter>" and e["maturity"] == "ENFORCED"
             and cov["rule_set_fingerprint"] == after and set(cov["coverage"]) == set(ids),
             "pcb_rules_coverage.yaml does not re-parse with DOC-003's entry and every rule covered")
        # 3. the declared inputs
        s = swap(old["rules_status.py"], FORMAT_OLD, FORMAT_NEW, "rules_status.py")
        s = insert_after(s, CONFIG_ANCHOR, CONFIG, "rules_status.py", 'CONFIG_INPUTS["constraints_bound.py"]')
        new["rules_status.py"] = s
        tree = ast.parse(s)
        need(any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Subscript)
                 and getattr(n.targets[0].value, "id", "") == "CONFIG_INPUTS"
                 and getattr(n.targets[0].slice, "value", None) == "constraints_bound.py" for n in tree.body),
             "rules_status.py does not re-parse with the entry")
        # 4. the re-take's command
        w = insert_after(old["retake_schematic_phase.py"], WRITER_ANCHOR, WRITER, "retake_schematic_phase.py",
                         '"constraints_bound_<letter>"')
        new["retake_schematic_phase.py"] = w
        ast.parse(w)
        # 5. the sweep
        if "--no-sweep" in argv:
            del new["gate_sweep.sh"]
        else:
            g = swap(old["gate_sweep.sh"], SWEEP_CLEAR_OLD, SWEEP_CLEAR_NEW, "gate_sweep.sh")
            g = insert_before(g, SWEEP_RUN_ANCHOR, SWEEP_RUN, "gate_sweep.sh", "constraints_bound.py --board")
            new["gate_sweep.sh"] = g
            r = subprocess.run(["bash", "-n"], input=g, capture_output=True, text=True, timeout=60)
            need(r.returncode == 0, "gate_sweep.sh does not parse after the patch: %s" % r.stderr[-300:])
    except Refused as e:
        print("apply_rule_and_coverage: REFUSED, nothing written: %s" % e)
        return 1
    for k in sorted(new):
        print("apply_rule_and_coverage: %-28s %+d line(s)" % (k, new[k].count("\n") - old[k].count("\n")))
    print("apply_rule_and_coverage: rule set fingerprint %s -> %s" % (before, after))
    if "--check" in argv:
        print("apply_rule_and_coverage: --check, nothing written")
        return 0
    for k, text in sorted(new.items()):
        tmp = paths[k] + ".part"
        with open(tmp, "w", encoding="utf-8") as f: f.write(text)
        if k.endswith(".sh"): os.chmod(tmp, os.stat(paths[k]).st_mode)
        os.replace(tmp, paths[k])
    # re-read what was written, from the files
    for k in sorted(new):
        need(open(paths[k], encoding="utf-8").read() == new[k], "%s on disk is not what was written" % k)
    r = subprocess.run([sys.executable, os.path.join(tools, "rules_lib.py"), "validate"], capture_output=True, text=True,
                       timeout=300, cwd=tools)
    print("apply_rule_and_coverage: rules_lib.py validate, exit %d: %s" % (r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1][:200]))
    print("apply_rule_and_coverage: applied. Next, the integrator's: the re-take on the box, rules_render.py, LAYER-STATUS 9.8")
    return 0 if r.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
