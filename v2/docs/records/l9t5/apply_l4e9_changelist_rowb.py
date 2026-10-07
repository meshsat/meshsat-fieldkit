#!/usr/bin/env python3
"""apply_l4e9_changelist_rowb.py: a TEXT DRAFT for the integrator (record l9t5, row (b)'s composite on fnd/l4hod, MESHSAT-1357, W159,
7 October 2026; finding W151-F1, judged "should fix" by row (b)'s focused check L4A-62, W157-F8). NOT APPLIED to the tree by this record:
L4-E9's change list is read by records that pin its page and its register by sha256 (L4-E11's l4e11_power.py and L4-E10's
l4e10_cell_thermal.py pin the page; Layer 6's l6r2_passives.py composes each board from the list), so the rows go in at integration with
those re-takes, as apply_l4e9_changelist_p0.py's did. Prototype design: nothing built, bought, powered or measured.

What it changes, and nothing else:
  1. v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md: rows R-247 to R-250 after R-246, one per draft of row (b) that the composite composes
     on board B and that had no row (W151-F1): record l9t5's canmb (W137, W143), regstage (W138), canen (W143) and hodtest (W146). Each
     names only its own apply script (L4-E9's cons_changes reads the script from the From cell, then the Item cell). Class SETTLED WORK
     with the house's next action for a drafted step B row (test_l9t5's rule for every row from R-220 that is not an RE row); each
     Acceptance cell says PROVISIONAL until row (b)'s check L4A-62. R-245 (iocguard, an RE row) is NOT restated here: its class follows
     row (b)'s verdict, the integrator's and the ledger's (apply_remeng_rowb.py).
  2. v2/docs/records/l4e9/l4e9_power_path.py: four CHANGE_ORDER tuples after R-245's and before R-236's (row (b) after iocguard, then
     R-236, R-237 and Layer 6, the order L4-E9 and record l9t5 compose in), and six ORDER_CONSTRAINTS after the containment's.
  3. v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md: the change-list table regenerated from the patched cons_changes, with a note.
Re-takes the integrator owes after it (as for the P0 round): l4e9_power_path.out, the L4 pin chain, l9t5_connected.out (its change
count), l6r2_passives.out (a content change: its change chain then composes the four drafts on board B), and the digest lines of the
records that pin the page. fnd/l4hoe's apply_gen_sch_b_vcoremon.py has no row either (HO-E's own task, not this record's).
Usage:  apply_l4e9_changelist_rowb.py [ROOT] [--check | --write]   (default: the repository this file sits in; --check writes nothing)
Exit 0: checked (or written); 3: refused (a file is not the expected text, the rows are already there, or the patched change list is
refused by L4-E9's own cons_changes)."""
import os
import re
import sys
import types

NAME = "apply_l4e9_changelist_rowb"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
L4 = os.path.join("v2", "docs", "records", "l4e9")
FROM = ("added to the change list by row (b)'s composite (record l9t5, W159, 7 October 2026, finding W151-F1; fnd/l4hod with fnd/l4small "
        "and fnd/l4lim)")
TAIL = "| Layer 8 board B generator owner | %s | DRAFTED | B | SETTLED WORK | DO: step B (DRAFTED), no open question; it continues while the open items are worked |\n"
ROWS = [
    "| R-247 | IMPLEMENTATION | Board B's CAN containment by method M-B (RE-5, HO-C): each supervisor's TXD buffered to its two peers "
    "and a 2-of-2 SHDN vote of the peers on each transceiver (twelve votes over both fabrics, CON-004's two fabrics kept), round 6's "
    "transmit-share limiters removed, their positions re-used: `apply_gen_sch_b_canmb.py`, AFTER R-245 | Layer 9's l9t5 rounds 7 and 9 "
    "(W137 and W143 on fnd/l4canmb at 664d4019; the quorum W139, T10-CANQ.md); " + FROM + " " + TAIL % (
        "In one release with R-248 to R-250; the regenerated netlist carries the buffers and votes as drafted (its mutations failing, "
        "l9t5_canmb.out); the quorum and the self-test as record l9t5's l9t5_canq.out states them; PROVISIONAL until row (b)'s check L4A-62"),
    "| R-248 | IMPLEMENTATION | Board B's supervisor regulator stage (RE-6, RE-7): a TPS2553-1 latch-off limiter at RILIM 49.9 kOhm 1 % "
    "ahead of a TPS73733DCQRM3 at each supervisor (new silicon only), round 6's rail trips removed (W138-2; their controller-protection "
    "role moves to HO-E, L4REG-F7): `apply_gen_sch_b_regstage.py`, AFTER R-245 | Layer 9's l9t5 record l4reg (W138, fnd/l4reg at "
    "86dbcdff); " + FROM + " " + TAIL % (
        "In one release with R-247, R-249 and R-250; the regenerated netlist carries each limiter ahead of its regulator, EN on pin 5 "
        "(l4reg_compare.out, l9t5_t10.out 11a (b)); the junction at constant maximum dissipation at the limiter's printed maximum "
        "CONDITIONAL on E-17; PROVISIONAL until row (b)'s check L4A-62"),
    "| R-249 | IMPLEMENTATION | Board B's restart route of a latched supervisor: the two peers' 2-of-2 vote on each limiter's EN through "
    "an SN74LVC1G08 and an AO3400A with an RC delay, the target reading its own gate (W139-F2): `apply_gen_sch_b_canen.py`, AFTER R-247 "
    "and R-248 | Layer 9's l9t5 round 9 (W143 on fnd/l4canmb at 664d4019; record l4canen); " + FROM + " " + TAIL % (
        "In one release with R-247, R-248 and R-250; the regenerated netlist carries the route as drafted (its mutations failing, "
        "l4canen.out); a latched supervisor restarted within 5.603 s; FW-B22's restart rule and its hold-off (W159-D3) with it (Layer 5); "
        "PROVISIONAL until row (b)'s check L4A-62"),
    "| R-250 | IMPLEMENTATION | Board B's in-service test of each supervisor's limiter (HO-D): a 3.0 Ohm load on the limiter's output "
    "through two series switches, one per peer, each peer reading the limiter's FAULT and output: `apply_gen_sch_b_hodtest.py`, AFTER "
    "R-248 and R-249 | Layer 9's l9t5 record l4hod (W146 on fnd/l4hod at 7ebca389); " + FROM + " " + TAIL % (
        "In one release with R-247 to R-249; the regenerated netlist carries the test path as drafted (its mutations failing, "
        "l4hod.out); FW-B24 with it (Layer 5); PROVISIONAL until row (b)'s check L4A-62, the supply's dip at the step PROVISIONAL (W146-F10)"),
]
REG_ANCHOR = "R-246"
CO_ANCHOR = ('    ("B", "R-245", GB, "AFTER R-235 and R-243 (it edits their lines: the transceivers\' SHDN and the LDOs\' inputs); in one release '
             'with R-234", G_L9T5_T10),\n')
CO_ADD = ('    ("B", "R-247", GB, "AFTER R-245 (it edits iocguard\'s lines: the share limiters\' parts re-used); in one release with R-248 to '
          'R-250", G_L9T5_T10),\n'
          '    ("B", "R-248", GB, "AFTER R-245 (it edits iocguard\'s lines: the rail trips removed); in either order with R-247", G_L9T5_T10),\n'
          '    ("B", "R-249", GB, "AFTER R-247 and R-248 (the restart route drives regstage\'s EN pin)", G_L9T5_T10),\n'
          '    ("B", "R-250", GB, "AFTER R-248 and R-249 (the test restores its target through canen\'s route)", G_L9T5_T10),\n')
OC_ANCHOR = '    ("the supervisors\' containment after T10\'s board B set point delta", "R-243", "R-245"),\n'
OC_ADD = ('    ("row (b)\'s CAN vote after the supervisors\' containment draft", "R-245", "R-247"),\n'
          '    ("row (b)\'s regulator stage after the supervisors\' containment draft", "R-245", "R-248"),\n'
          '    ("row (b)\'s restart route after its CAN vote", "R-247", "R-249"),\n'
          '    ("row (b)\'s restart route after its regulator stage", "R-248", "R-249"),\n'
          '    ("row (b)\'s in-service limiter test after its regulator stage", "R-248", "R-250"),\n'
          '    ("row (b)\'s in-service limiter test after its restart route", "R-249", "R-250"),\n')
NOTE = ("**Row (b) (record l9t5, W159, 7 October 2026; W151-F1).** Rows R-247 to R-250 add row (b)'s four board B drafts (canmb, regstage, "
        "canen, hodtest) after R-245 and before R-236; each is DRAFTED and PROVISIONAL until row (b)'s check L4A-62; nothing in this kit has "
        "been built.")
IDS = ["R-247", "R-248", "R-249", "R-250"]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patch_register(text):
    already = [i for i in IDS if re.search(r"^\| %s \|" % re.escape(i), text, re.M)]
    if already:
        refuse("the register already carries %s: applied before (no row is ever added twice)" % ", ".join(already))
    if re.search(r"^\| R-(2[5-9]\d|[3-9]\d\d) \|", text, re.M):
        refuse("the register carries a row numbered over R-250: renumber these rows first")
    m = re.search(r"^\| %s \|.*\n" % re.escape(REG_ANCHOR), text, re.M)
    if not m:
        refuse("the register has no row %s to follow" % REG_ANCHOR)
    for r in ROWS:
        if len(r.rstrip("\n").strip("|").split(" | ")) != 10 or len(re.findall(r"apply_[a-z0-9_]+\.py", r)) != 1:
            refuse("a row does not carry ten cells and exactly one apply script: %s" % r[:12])
        if re.search("[" + chr(0x2013) + chr(0x2014) + "]", r):
            refuse("a long dash in a row")
    return text[:m.end()] + "".join(ROWS) + text[m.end():]


def patch_script(text):
    new = text
    for old, add in ((CO_ANCHOR, CO_ADD), (OC_ANCHOR, OC_ADD)):
        if new.count(old) != 1:
            refuse("the script's anchor occurs %d times, not once: %r" % (new.count(old), old[:70]))
        new = new.replace(old, old + add)
    compile(new, "l4e9_power_path.py", "exec")
    return new


def module_of(source, path):
    """the patched script as a module whose __file__ is the target's own path (so it finds the target tree by git)"""
    m = types.ModuleType("l4e9_rowb_%d" % abs(hash(path)))
    m.__file__ = path
    exec(compile(source, path, "exec"), m.__dict__)
    return m


def patch_page(text, m, reg_text):
    ch = m.cons_changes(m.md_table(reg_text, "| ID | Kind |"))
    table = ["| # | Step | Row | Board and generator | Apply script | Depends on | Release guard | What it changes (the register's item) | State |",
             "|---|---|---|---|---|---|---|---|---|"] + ["| %d | %s | %s | %s | %s | %s | %s | %s | %s |" % c for c in ch]
    lines = text.split("\n")
    if any(l.startswith("**Row (b) (record l9t5, W159") for l in lines):
        refuse("the page already carries row (b)'s note: applied before")
    i = [k for k, l in enumerate(lines) if l.startswith("| # | Step | Row | ")]
    if len(i) != 1:
        refuse("the page has %d change-list tables, not one" % len(i))
    i = i[0]
    j = i
    while j < len(lines) and lines[j].startswith("|"):
        j += 1
    return "\n".join(lines[:i] + [NOTE, ""] + table + lines[j:]), ch


def patch_all(root):
    p_reg, p_py, p_page = (os.path.join(root, L4, f) for f in ("DOWNSTREAM-REGISTER.md", "l4e9_power_path.py", "L4-POWER-ARCHITECTURE.md"))
    reg = patch_register(open(p_reg, encoding="utf-8").read())
    py = patch_script(open(p_py, encoding="utf-8").read())
    try:
        m = module_of(py, p_py)
        page, ch = patch_page(open(p_page, encoding="utf-8").read(), m, reg)
    except SystemExit as e:
        if e.code == 3:
            raise
        refuse("L4-E9's own change list refuses the patched rows (exit %s)" % e.code)
    rows = [c[2] for c in ch]
    at = rows.index("R-245")
    if rows[at + 1:at + 5] != IDS or rows[at + 5] != "R-236":
        refuse("the patched list does not read R-245, R-247 to R-250, R-236 in order: %s" % rows[at:at + 6])
    return {p_reg: reg, p_py: py, p_page: page}, ch


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) > 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    root = os.path.abspath(args[0]) if args else REPO
    files, ch = patch_all(root)
    print("%s: %d changes in the patched list, R-247 to R-250 after R-245 and before R-236, every order constraint holds" % (NAME, len(ch)))
    if flags != ["--write"]:
        print("%s: CHECK OK, nothing written" % NAME)
        return 0
    for p, t in files.items():
        tmp = p + ".rowb-tmp"
        open(tmp, "w", encoding="utf-8").write(t)
        os.replace(tmp, p)
    for p, t in files.items():
        if open(p, encoding="utf-8").read() != t:
            refuse("%s does not read back as the patched text" % p)
    print("%s: WRITTEN, three files" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
