#!/usr/bin/env python3
"""Q-55 (MESHSAT-1357, set 32; W40 on branch fnd/s32small from main eff28be3, 6 October 2026): V-E16's row 3 in
v2/docs/HW-FW-CONTRACT.md takes N1a's annotation at the place the register's R-176 row 3 carries it, and test_w8l5's
live check then reads V-E16 from the TREE equal to the live register; test_l5pwr's reading of L5-F09 d admits N1a's
words, once, in V-E16 (the third edit, found by the sweep below).

THIS MOVES l4e11_power.out AND THE l4e7 KEY. HW-FW-CONTRACT.md is pinned by l4e11_power.out (its `hwfw` line), which is one
of the l4e7 KEY's files, so set 32 needs a re-key after this script runs. Also pinned at set 31's tip d5d9c252: the PINS
tables of l4e11_power.py (line 54) and l4e9_power_path.py (line 75) hard-code the page's sha256 (tool-moved pins, re-pinned
by the L4 chain), and l4e9_power_path.out, l5r2_interfaces.out, l5r3_panel.out, l8gnd_drafts.out and l9t5_t10.out print it
(re-pinned by set 32's dependency pass). The script prints the page's sha256 before and after.

The decision: the coordinator's of 6 October 2026 15:22 CEST (QUEUE line Q-55, authority SESSION): carrying the annotation
into V-E16 is set 32's, because in set 31 it would have invalidated the re-key then running. The record's own invariant:
V-E16's rows 2 and 3 mirror the register's R-176 rows 2 and 3 verbatim (record l5pwr's L5-F09 d wrote them so).

WHY A SCRIPT AND NOT AN EDIT ON THE BRANCH (authority SESSION, W40, 6 October 2026; reversed by applying the two edits by
hand, three edits): the branch's base, main eff28be3, holds none of what the edit stands on. N1a's annotation of the register (b2564b59),
W8's restatement of V-E16 (8840adda) and test_w8l5.py itself (W8, restated by the coordinator at f0748b49) are all set 31's
(fnd/int31regen). An edit of V-E16's row here would conflict line for line with W8's edit of the same row at set 32's
merge, and the test does not exist here to edit. So the integrator runs this script on set 32's merged tree, after set
31's promotion, and commits its three files with the re-key.

What it does, all checks first and nothing written unless every one holds:
  1. the register (v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md): exactly one `| R-176 | TEST |` row, whose third cell
     carries N1A_WORDS exactly once, right after "U5's CSPIN to CSNIN within +-0.240 V" (N1a is in the tree);
  2. HW-FW-CONTRACT.md: exactly one `| V-E16 |` row; OLD found exactly once in it and nowhere else in the page; the row
     with NEW in its place differs; every other line of the page and every cell but the last unchanged; the cell count
     kept; V-E16's rows 2 and 3 (from "(2) " to " (PROVISIONAL until E-1's correction", W8's wording) then equal the
     register's R-176 rows 2 and 3 (from "(2) " to "; (4) ") verbatim; no em or en dash;
  3. test_w8l5.py: the three lines of the coordinator's live check (f0748b49) found exactly once; the new check
     appended after them; the module parses (ast);
  4. test_l5pwr.py: W14's two lines of the L5-F09 reading found exactly once; the Q-55 reading put in their place (N1a's
     words, where a restated field carries them, exactly once in V-E16 right after U5's line, then taken out before the
     script's values are read; nothing else of the reading changes); the module parses (ast).
A second run finds N1A_WORDS in V-E16 and the Q-55 marker in both tests and exits 3, writing nothing; a partial state is
refused (exit 2).

THE SWEEP (6 October 2026, a scratch clone of set 31's tip d5d9c252, v2/docs and v2/ecad checked out): run.py over the 11
light modules that read HW-FW-CONTRACT.md (test_w8l5, test_l5pwr, test_l5r2, test_l5r4, test_lstat31, test_lstat32,
test_requirements, test_w14l5, test_w20oneliners, test_w24l4e9, test_fw_panel) before and after the apply: 156 passed, 26
failed, 2 skipped before (the 26 the clone's environment: no firmware tree, no vendor files); after, the same 26 plus two,
both pins: test_l5r2.t_r3_output_reproduced_and_every_finding_resolved (l5r3_panel.out prints the page's sha256) and
test_w24l4e9.t_the_four_typed_in_pins_equal_their_files (l4e9_power_path.py:75). With the two PINS re-pinned and
l5r3_panel.out regenerated on the clone (one line moved, the pin) both pass. The heavy modules test_l4e5, test_l4e9,
test_l4e11 and test_l9t5 were read, not run: none reads V-E16; their page reads (FW-C08, the keyed outlets, FW-B rows, a
fixed commit) do not move, and their generators' PINS are the chain's re-pin.

Usage (from anywhere): apply_q55_ve16.py [--root <repository root>] [--check]
  --root   the tree to patch (default: this file's repository)
  --check  every check, nothing written
Exit 0 written (or, with --check, would write); 2 refused, nothing written; 3 already applied, nothing written.
"""
import argparse, ast, hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REG_REL = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
HWFW_REL = "v2/docs/HW-FW-CONTRACT.md"
TEST_REL = "v2/ecad/tools/tests/test_w8l5.py"

N1A_WORDS = " (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5)"
U5 = "U5's CSPIN to CSNIN within +-0.240 V"
OLD = U5 + ", U21 turning Q12 off"
NEW = U5 + N1A_WORDS + ", U21 turning Q12 off"
W8_END = " (PROVISIONAL until E-1's correction"

TEST_OLD = (
    '    need(REG, "the register")\n'
    '    live = r176_rows(open(REG, encoding="utf-8").read())\n'
    '    assert live.count(N1A_WORDS) == 1 and live.replace(N1A_WORDS, "") == want, "the live register\'s R-176 rows 2 and 3 '
    'differ from W8\'s by more than N1a\'s annotation"\n')
MARK = "# Q-55 (set 32"
TEST_ADD = (
    '    # Q-55 (set 32, record s32small, applied by apply_q55_ve16.py): V-E16\'s row 3 carries N1a\'s annotation at the place the\n'
    '    # register\'s R-176 row 3 carries it, so V-E16 read from the TREE equals the live register\'s rows 2 and 3 verbatim; the\n'
    '    # fixture form above stays for W8\'s own change. Basis: the record\'s own invariant, V-E16 mirrors the register (record\n'
    '    # l5pwr\'s L5-F09 d wrote it so), and the coordinator\'s decision of 6 October 2026 15:22 CEST (QUEUE line Q-55).\n'
    '    ve16 = [cells(ln) for ln in tree(HWFW_REL).split("\\n") if ln.startswith("| V-E16 |")]\n'
    '    assert len(ve16) == 1, "%d V-E16 rows in the tree" % len(ve16)\n'
    '    v = ve16[0][-1]\n'
    '    assert v[v.index("(2) "):v.index(" (PROVISIONAL until E-1\'s correction")] == live, "V-E16\'s rows 2 and 3 in the tree '
    'are not the live register\'s R-176 rows 2 and 3"\n')

# test_l5pwr (W14's restated reading of record l5pwr's L5-F09 d): the script printed V-E16's rows 2 and 3 before N1a, so with
# N1a's words in V-E16 its row 3 value is no longer a verbatim substring of the row. Found by running test_l5pwr on set 31's tip
# with the two edits above applied (a scratch clone of d5d9c252): t_the_contract_restatement_of_l5f09_and_l5f10_is_in_the_tree_
# and_idempotent failed with "L5-F09 d: a value the script printed is gone". The restatement admits exactly N1a's words, once,
# right after U5's line, and nothing else; every other property of the reading is unchanged.
L5PWR_REL = "v2/ecad/tools/tests/test_l5pwr.py"
L5PWR_OLD = (
    '        if i in W8_RESTATED:\n'
    '            assert a.flat(new) not in live, "%s: the script\'s text stands verbatim, so W8 did not restate it" % i\n'
    '            assert _w14_restated(a.flat, i, new, live, quotes, V.values(), "no loop is claimed to pass"), i\n')
L5PWR_NEW = (
    '        if i in W8_RESTATED:\n'
    '            # Q-55 (set 32, record s32small, applied by apply_q55_ve16.py): V-E16\'s row 3 carries N1a\'s annotation of the\n'
    '            # register\'s R-176 row 3 (set 31, b2564b59), which this script printed before N1a. Where a restated field carries\n'
    '            # N1a\'s words they must stand exactly once, in V-E16, right after U5\'s line, and the script\'s values are read with\n'
    '            # those words taken out. Basis: N1a is the one intended difference (test_w8l5 states it so for the register, f0748b49),\n'
    '            # and the coordinator\'s decision of 6 October 2026 15:22 CEST (QUEUE line Q-55).\n'
    '            n1a = " (under R-240, drafted, not applied: under 10 mV in magnitude, a layout check, L4E7-P0SOL.md section 5)"\n'
    '            if n1a in live:\n'
    '                assert where == "| V-E16 |" and live.count(n1a) == 1 and live.count("U5\'s CSPIN to CSNIN within +-0.240 V" + n1a) == 1, \\\n'
    '                    "%s: N1a\'s words stand elsewhere than once after U5\'s line in V-E16" % i\n'
    '                live = live.replace(n1a, "")\n'
    '            assert a.flat(new) not in live, "%s: the script\'s text stands verbatim, so W8 did not restate it" % i\n'
    '            assert _w14_restated(a.flat, i, new, live, quotes, V.values(), "no loop is claimed to pass"), i\n')
L5PWR_MARK = "# Q-55 (set 32"


class Refused(Exception):
    pass


class Done(Exception):
    pass


def cells(line):
    s = line.strip()
    return [c.strip() for c in s[1:-1].split("|")] if s.startswith("|") and s.endswith("|") else None


def one_row(text, prefix, what):
    rows = [ln for ln in text.split("\n") if ln.startswith(prefix)]
    if len(rows) != 1:
        raise Refused("%d rows start with %r in %s" % (len(rows), prefix, what))
    return rows[0]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def plan(root):
    reg = open(os.path.join(root, REG_REL), encoding="utf-8").read()
    hw = open(os.path.join(root, HWFW_REL), encoding="utf-8").read()
    tp = os.path.join(root, TEST_REL)
    if not os.path.isfile(tp):
        raise Refused("%s is not in this tree (set 31's file): run on set 32's merged tree" % TEST_REL)
    tt = open(tp, encoding="utf-8").read()
    lp = os.path.join(root, L5PWR_REL)
    if not os.path.isfile(lp):
        raise Refused("%s is not in this tree" % L5PWR_REL)
    lt = open(lp, encoding="utf-8").read()

    ve = one_row(hw, "| V-E16 |", HWFW_REL)
    applied = [N1A_WORDS in ve, MARK in tt, L5PWR_MARK in lt]
    if all(applied):
        raise Done("already applied: V-E16 carries N1a's words, test_w8l5 the Q-55 check and test_l5pwr the Q-55 reading")
    if any(applied):
        raise Refused("half applied (V-E16 %s, test_w8l5 %s, test_l5pwr %s): mend by hand"
                      % tuple("yes" if a else "no" for a in applied))

    # 1. N1a is in the tree's register
    r176 = cells(one_row(reg, "| R-176 | TEST |", REG_REL))
    if r176[2].count(N1A_WORDS) != 1 or r176[2].count(U5 + N1A_WORDS) != 1:
        raise Refused("the register's R-176 row 3 does not carry N1a's annotation after %r once (N1a, b2564b59, is set 31's)" % U5)
    want = r176[2][r176[2].index("(2) "):r176[2].index("; (4) ")]

    # 2. the page
    if ve.count(OLD) != 1 or hw.count(OLD) != 1:
        raise Refused("OLD is %d times in V-E16 and %d times in the page, not once" % (ve.count(OLD), hw.count(OLD)))
    if W8_END not in ve:
        raise Refused("V-E16 lacks W8's wording %r: run after set 31's promotion" % W8_END)
    ve_new = ve.replace(OLD, NEW, 1)
    hw_new = hw.replace(ve, ve_new, 1)
    if hw_new == hw or ve_new == ve:
        raise Refused("the new page does not differ")
    a, b = hw.split("\n"), hw_new.split("\n")
    moved = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(a) != len(b) or len(moved) != 1:
        raise Refused("the edit moved %d lines of the page, not one" % len(moved))
    ca, cb = cells(a[moved[0]]), cells(b[moved[0]])
    if ca is None or cb is None or len(ca) != len(cb) or ca[:-1] != cb[:-1]:
        raise Refused("V-E16's cells other than the last moved, or its cell count changed")
    v = cb[-1]
    if v[v.index("(2) "):v.index(W8_END)] != want:
        raise Refused("after the edit V-E16's rows 2 and 3 are not the register's R-176 rows 2 and 3 verbatim")
    if chr(0x2014) in hw_new or chr(0x2013) in hw_new:
        raise Refused("an em or en dash in the page")

    # 3. the test
    if tt.count(TEST_OLD) != 1:
        raise Refused("the coordinator's live check (f0748b49) is %d times in %s, not once" % (tt.count(TEST_OLD), TEST_REL))
    tt_new = tt.replace(TEST_OLD, TEST_OLD + TEST_ADD, 1)
    if tt_new == tt:
        raise Refused("the new test does not differ")
    ast.parse(tt_new, TEST_REL)
    if chr(0x2014) in tt_new or chr(0x2013) in tt_new:
        raise Refused("an em or en dash in the test")

    # 4. test_l5pwr's reading of L5-F09 d
    if lt.count(L5PWR_OLD) != 1:
        raise Refused("W14's L5-F09 reading is %d times in %s, not once" % (lt.count(L5PWR_OLD), L5PWR_REL))
    lt_new = lt.replace(L5PWR_OLD, L5PWR_NEW, 1)
    if lt_new == lt:
        raise Refused("the new test_l5pwr does not differ")
    ast.parse(lt_new, L5PWR_REL)
    if chr(0x2014) in lt_new or chr(0x2013) in lt_new:
        raise Refused("an em or en dash in test_l5pwr")
    return [(HWFW_REL, hw, hw_new), (TEST_REL, tt, tt_new), (L5PWR_REL, lt, lt_new)]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    root = a.root or subprocess.run(["git", "-C", HERE, "rev-parse", "--show-toplevel"], capture_output=True,
                                    text=True, check=True).stdout.strip()
    try:
        edits = plan(root)
    except Done as e:
        print("apply_q55_ve16: %s; nothing written" % e); return 3
    except Refused as e:
        print("apply_q55_ve16: REFUSED: %s; nothing written" % e); return 2
    for rel, old, new in edits:
        print("apply_q55_ve16: %s %s -> %s" % (rel, sha(old.encode())[:16], sha(new.encode())[:16]))
    if a.check:
        print("apply_q55_ve16: CHECK ONLY, every check held, nothing written"); return 0
    for rel, old, new in edits:
        p = os.path.join(root, rel)
        tmp = p + ".q55.tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        os.replace(tmp, p)
    # re-read what was written
    for rel, old, new in edits:
        got = open(os.path.join(root, rel), encoding="utf-8").read()
        assert got == new, "%s reads back different" % rel
    for rel, _old, new in edits[1:]:
        ast.parse(new, rel)
    hw_sha = sha(open(os.path.join(root, HWFW_REL), "rb").read())
    print("apply_q55_ve16: written; %s sha256 now %s: re-pin l4e11_power.py's and l4e9_power_path.py's PINS[\"hwfw\"], "
          "re-key the l4e7 KEY, then the dependency pass" % (HWFW_REL, hw_sha))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
