#!/usr/bin/env python3
"""apply_set28_repins.py: L5-F01 (MESHSAT-1357, set 28, 3 October 2026). Layer 5's power pass (records/l5pwr) wrote into
v2/docs/HW-FW-CONTRACT.md, v2/docs/PANEL.md section 10 and v2/ecad/tools/pcb_interfaces.yaml, and three Layer 4 readers pin those
files by sha256 and refuse: l4e5_source_control.py (the contract), l4e11_power.py (the contract and PANEL.md) and l4e9_power_path.py
(the contract and the interfaces). This script brings the three readers to the merged tree and regenerates the outputs, in the order
L4-E5, L4-E7, L4-E11, L4-E9 (L4-E11 pins the L4-E5 output; L4-E9 pins both), every regeneration through _bin/regen_out.py. Nothing of any
record's prose or figures changes: pins, one reading mechanism and need() texts only. Every sha it writes is READ from the tree at run
time, never typed, so the coordinator re-runs it after re-basing the branch onto set 27's final commit.

What it does, per reader:
  L4-E5   Its reader needs four pre-draft texts of FW-A16 and FW-E04 ("as written") and captures the record's figures from them
          (0.80, 4.80 A, 0.93, 20.7 V, the 9/12/24 V figures, O-33's 54 and 93 W, FW-E04's 1 s); Layer 5 applied L4-E5's OWN draft
          apply_fw_a16.py (register row R-23), so the merged contract no longer carries them and re-pinning the CONTRACT key to the
          merged file would refuse at "FW-A16's rule not found". So the contract is read where the record analysed it: the tree's
          file while it is the pinned one, else the pinned bytes at CONTRACT_COMMIT (the FROM_COMMIT mechanism L4-E9 and L4-E11
          already use); the pin is unchanged and the output is byte-identical (it prints no pin). This is a reading mechanism, not
          a figure: authority SESSION, reason above, reversed by restating L4-E5's need() texts in a round of its own.
  L4-E11  PINS hwfw, panel, reqs, l4e5 and arch (L4-E9's page, stale since the consolidation round 3 at f08e1342 re-wrote the page
          after L4-E11 pinned it; the same re-pin _bin/freeze_l4_chain.sh makes, so this is idempotent with the freeze) re-pinned to the tree; its need() texts for FW-C08, FW-A14 and PANEL.md's cold-hold
          sentence (the three texts its own E11-03 asked Layer 5 to restate) replaced by the texts Layer 5 wrote, quoted from the
          merged files (the behaviour cell of each row, the section 10 sentence that carries "below 0 C" and "above 3 C"); the
          section 10 sentence "high = the shore ... nothing charges." is unchanged and its need() is kept after a check.
  L4-E9   PINS hwfw, ifaces, reqs, l4e5, l4e11 and l4e7r re-pinned to the tree (l4e5, l4e7 and l4e11 after their regeneration).
  L5, L7  records/l5pwr/l5pwr_contracts.out and records/l7pwr/l7pwr_fans_th1.out regenerated last: their readers print the shas of
          L4-E9's and L4-E11's outputs and of the registry in their section 0 (no pin refusal, a printed binding), so the test
          "output reproduced byte for byte" of each fails until they are regenerated after the L4 outputs and the rebind.
  L4-E7   One consequential re-pin outside the three named readers: l4e7_stage_settings.py pins L4-E5's SCRIPT (L4E5_PY; it re-runs
          it as its reproduction 0b), which the L4-E5 mechanism above changes; its output prints no pin and stays byte-identical, which
          its regeneration proves. Nothing else of L4-E7 is touched.
The reqs key (pcb_requirements.yaml) is re-pinned too because apply_set28_rebind.py (L5-F02) changes that file: run the rebind first,
then this script (apply_set28.py does both in order). The pins of pcb_requirements.yaml in l4e10_cell_thermal.py, l4e12_thermal.py
and l4e13_panel.py are NOT touched here (the brief: the three named readers only); they refuse after the rebind and are the
coordinator's freeze (RESULT.md names them).

Usage, from anywhere:  apply_set28_repins.py [--check | --write] [--no-regen]
  --check (default) prints every pin and text that --write would change, writes nothing, regenerates nothing.
  --write patches the readers and regenerates the four outputs (L4-E5, L4-E7, L4-E11, L4-E9) through regen_out.py (REGEN_OUT in the environment, else
          <worktrees>/_bin/regen_out.py beside this worktree); --no-regen patches only.
Refuses (exit 3): "already applied" when no pin, mechanism or text differs from the tree; a row or sentence not found once in the
merged files; a pattern that does not match the merged text exactly once; a patched file that does not parse; regen_out refusing.
Every write asserts the new text differs and re-parses the file (ast). Exit 0 written (or checked)."""
import ast
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()

L4E5_PY, L4E5_OUT = "v2/docs/records/l4e5/l4e5_source_control.py", "v2/docs/records/l4e5/l4e5_source_control.out"
L4E11_PY, L4E11_OUT = "v2/docs/records/l4e11/l4e11_power.py", "v2/docs/records/l4e11/l4e11_power.out"
L4E9_PY, L4E9_OUT = "v2/docs/records/l4e9/l4e9_power_path.py", "v2/docs/records/l4e9/l4e9_power_path.out"
L4E7_PY, L4E7_OUT = "v2/docs/records/l4e7/l4e7_stage_settings.py", "v2/docs/records/l4e7/l4e7_stage_settings.out"
L4E9_MD = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
# The Layer 5 and 7 readers print the shas of what they read (L4-E9's and L4-E11's outputs; the registry) in their section 0 and
# bind their outputs through regen_out, so they are regenerated last; Layer 6's reads none of the files this set changes
LATER = (("v2/docs/records/l5pwr/l5pwr_contracts.py", "v2/docs/records/l5pwr/l5pwr_contracts.out"),
         ("v2/docs/records/l7pwr/l7pwr_fans_th1.py", "v2/docs/records/l7pwr/l7pwr_fans_th1.out"))   # L4-E11 pins L4-E9's page; stale since the consolidation round 3 (f08e1342), the freeze helper's L4-E11 step
HWFW, PANEL = "v2/docs/HW-FW-CONTRACT.md", "v2/docs/PANEL.md"
IFACES, REQS = "v2/ecad/tools/pcb_interfaces.yaml", "v2/ecad/tools/pcb_requirements.yaml"
CONTRACT_COMMIT = "2c240414"      # the last commit carrying HW-FW-CONTRACT.md as L4-E5 analysed it (before apply_fw_a16.py)

# ---- L4-E5: the contract read where the record analysed it (text anchors in l4e5_source_control.py)
L4E5_OLD_LOOP = ('    for rel, want in PINS.items():\n'
                 '        if sha(rel) != want:\n'
                 '            refuse(2, "%s is not the pinned file" % rel)\n')
L4E5_NEW_LOOP = ('    for rel, want in PINS.items():\n'
                 '        if (hashlib.sha256(contract_bytes()).hexdigest() if rel == CONTRACT else sha(rel)) != want:\n'
                 '            refuse(2, "%s is not the pinned file" % rel)\n')
L4E5_OLD_READ = '    ct = open(os.path.join(TOP, CONTRACT), encoding="utf-8").read()\n'
L4E5_NEW_READ = '    ct = contract_bytes().decode("utf-8")\n'
L4E5_ANCHOR = 'def pg(rel, n, layout=True):\n'
L4E5_HELPER = '''CONTRACT_COMMIT = "%s"   # the last commit carrying HW-FW-CONTRACT.md as this record analysed it (set 28: Layer 5 applied apply_fw_a16.py)


def contract_bytes():
    """HW-FW-CONTRACT.md as this record analysed it: the tree's file while it is the pinned one, else the pinned bytes at
    CONTRACT_COMMIT (L4-E9's FROM_COMMIT mechanism). Layer 5's power pass (set 28, 3 October 2026, records/l5pwr) applied this
    record's own draft apply_fw_a16.py to the tree (register row R-23), so the pre-draft FW-A16 and FW-E04 rows this record reads
    "as written" are no longer the tree's; the figures it captures from them are the record's and are read where they were written.
    The pin is unchanged (set 28, records/int28/apply_set28_repins.py)."""
    p = os.path.join(TOP, CONTRACT)
    b = open(p, "rb").read()
    if hashlib.sha256(b).hexdigest() == PINS[CONTRACT]:
        return b
    r = subprocess.run(["git", "show", "%%s:%%s" %% (CONTRACT_COMMIT, CONTRACT)], cwd=TOP, capture_output=True)
    if r.returncode != 0:
        refuse(3, "%%s is not at %%s" %% (CONTRACT, CONTRACT_COMMIT))
    return r.stdout


''' % CONTRACT_COMMIT


def refuse(msg):
    print("apply_set28_repins: REFUSED: %s" % msg)
    sys.exit(3)


def sha(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def text(rel):
    return open(os.path.join(TOP, rel), encoding="utf-8").read()


def flat(t):
    return " ".join(t.split())


def regen_path():
    for p in (os.environ.get("REGEN_OUT"), os.path.join(os.path.dirname(TOP), "_bin", "regen_out.py")):
        if p and os.path.isfile(p):
            return p
    refuse("regen_out.py not found: set REGEN_OUT to its path (it lives in <worktrees>/_bin beside the worktrees)")


def lit(pat):
    """A Python source literal for a regex pattern: a raw string when it can be one, else repr(). re.escape's escaped spaces are
    written as spaces (the same pattern, readable)."""
    pat = pat.replace("\\ ", " ")
    if '"' not in pat and "\n" not in pat and not pat.endswith("\\"):
        return 'r"%s"' % pat
    return repr(pat)


def once(pat, hay, what):
    hits = list(re.finditer(pat, hay))
    if len(hits) != 1:
        refuse("%s: the pattern matches %d time(s) in the merged text, one expected" % (what, len(hits)))
    return hits[0]


def row_cells(doc, rid):
    rows = [l for l in doc.split("\n") if l.startswith("| %s |" % rid)]
    if len(rows) != 1:
        refuse("%s: %d row(s) in %s, one expected" % (rid, len(rows), HWFW))
    cells = [c.strip() for c in rows[0].strip().strip("|").split(" | ")]
    return cells


def repin(src, key, rel, cur, who):
    """Re-pin PINS[key] = (rel, sha) in src to cur; (new src, (key, old16, new16) or None)."""
    m = re.search(r'("%s": \("%s", ")([0-9a-f]{64})(")' % (re.escape(key), re.escape(rel)), src)
    if not m:
        refuse("%s: no PINS entry %r for %s" % (who, key, rel))
    if m.group(2) == cur:
        return src, None
    return src[:m.start(2)] + cur + src[m.end(2):], (key, m.group(2)[:16], cur[:16])


def repin_const(src, name, rel, cur, who):
    """Re-pin the constant-style entry `    NAME: "<sha>",` (NAME = "<rel>" above it) in src to cur; (new src, change or None)."""
    m = re.search(r'(\n    %s: ")([0-9a-f]{64})(",)' % re.escape(name), src)
    if not m or ('%s = "%s"' % (name, rel)) not in src:
        refuse("%s: no constant-style pin %s for %s" % (who, name, rel))
    if m.group(2) == cur:
        return src, None
    return src[:m.start(2)] + cur + src[m.end(2):], (name, m.group(2)[:16], cur[:16])


def set_line(src, prefix, new_line, who):
    """Replace the one source line that starts with prefix by new_line; (new src, changed)."""
    lines = src.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        refuse("%s: %d line(s) start with %r, one expected" % (who, len(idx), prefix))
    if lines[idx[0]] == new_line:
        return src, False
    lines[idx[0]] = new_line
    return "\n".join(lines), True


def write(rel, old, new, who):
    if new == old:
        refuse("%s: the new text does not differ" % who)
    ast.parse(new, filename=rel)
    with open(os.path.join(TOP, rel), "w", encoding="utf-8") as fh:
        fh.write(new)
    if text(rel) != new:
        refuse("%s: the file written does not read back" % who)


def regen(py, out, do_it):
    if not do_it:
        print("regen   %s: skipped (--no-regen)" % out)
        return
    r = subprocess.run([sys.executable, regen_path(), TOP, py, out], capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    print("regen   %s" % tail)
    if r.returncode != 0:
        for l in r.stdout.strip().splitlines()[:-1]:
            print("        %s" % l)
        refuse("regen_out refused %s (exit %d); the committed output is unchanged" % (out, r.returncode))


# --------------------------------------------------------------------------------------------------------- the three plans
def plan_l4e5():
    src = text(L4E5_PY)
    changes, new = [], src
    if "def contract_bytes():" not in new:
        if L4E5_OLD_LOOP not in new or L4E5_OLD_READ not in new or new.count(L4E5_ANCHOR) != 1:
            refuse("l4e5_source_control.py: the pin loop, the contract read or the anchor is not the text this script was written against")
        new = new.replace(L4E5_OLD_LOOP, L4E5_NEW_LOOP).replace(L4E5_OLD_READ, L4E5_NEW_READ).replace(L4E5_ANCHOR, L4E5_HELPER + L4E5_ANCHOR)
        changes.append(("mechanism", "the contract read at %s when the tree's file is not the pinned one" % CONTRACT_COMMIT, ""))
    m = re.search(r'    CONTRACT: "([0-9a-f]{64})",', new)
    if not m:
        refuse("l4e5_source_control.py: no CONTRACT pin")
    at = subprocess.run(["git", "show", "%s:%s" % (CONTRACT_COMMIT, HWFW)], cwd=TOP, capture_output=True)
    if at.returncode != 0 or hashlib.sha256(at.stdout).hexdigest() != m.group(1):
        refuse("the contract at %s is not L4-E5's pinned file %s" % (CONTRACT_COMMIT, m.group(1)[:16]))
    return src, new, changes


def plan_l4e7():
    """L4-E7 pins L4-E5's script (it re-runs it as its reproduction 0b); the mechanism above changes that script, so this is the one
    consequential re-pin outside the three readers the brief names: L4-E7's output prints no pin, so it stays byte-identical."""
    src = text(L4E7_PY)
    new, ch = repin_const(src, "L4E5_PY", L4E5_PY, sha(L4E5_PY), "l4e7_stage_settings.py")
    return src, new, ([ch] if ch else [])


def plan_l4e11():
    src = text(L4E11_PY)
    new, changes = src, []
    for key, rel in (("hwfw", HWFW), ("panel", PANEL), ("reqs", REQS), ("l4e5", L4E5_OUT), ("arch", L4E9_MD)):
        new, ch = repin(new, key, rel, sha(rel), "l4e11_power.py")
        if ch:
            changes.append(ch)
    hw, pn = text(HWFW), text(PANEL)
    fhw, fpn = flat(hw), flat(pn)
    c08 = row_cells(hw, "FW-C08")[2]
    a14 = row_cells(hw, "FW-A14")[2]
    pat_c08 = r"\| FW-C08 \| (.*?) \| (" + re.escape(c08) + r") \|"
    pat_a14 = r"\| FW-A14 \| (CHG_INHIBIT .*?) \| (" + re.escape(a14) + r") \|"
    if once(pat_c08, fhw, "FW-C08").group(2) != c08 or once(pat_a14, fhw, "FW-A14").group(2) != a14:
        refuse("the FW-C08 or FW-A14 pattern does not capture the behaviour cell")
    i = pn.find("\n## 10. ")
    j = pn.find("\n## 11. ", i + 1)
    if i < 0 or j < 0:
        refuse("PANEL.md: section 10 not delimited")
    sents = re.split(r"(?<=\.) (?=[A-Z*`])", flat(pn[i:j]))
    cold = [s for s in sents if "below 0 C" in s and "above 3 C" in s]
    if len(cold) != 1:
        refuse("PANEL.md section 10: %d sentence(s) carry 'below 0 C' and 'above 3 C', one expected" % len(cold))
    pat_cold = re.escape(cold[0])
    once(pat_cold, fpn, "PANEL.md's cold hold")
    pat_hi = r"high = the shore and vehicle inputs are held off at the front end, so nothing charges\."
    once(pat_hi, fpn, "PANEL.md section 10")
    for prefix, line, what in (
            ('    R["fwc08"] = need(', '    R["fwc08"] = need(flat(T["hwfw"]), %s, "FW-C08").group(2)' % lit(pat_c08), "FW-C08"),
            ('    R["fwa14"] = need(', '    R["fwa14"] = need(flat(T["hwfw"]), %s, "FW-A14").group(2)' % lit(pat_a14), "FW-A14"),
            ('    R["panel10"] = need(', '    R["panel10"] = need(flat(T["panel"]), %s, "PANEL.md section 10").group(0)' % lit(pat_hi), "PANEL.md section 10"),
            ('    R["panel10_cold"] = need(', '    R["panel10_cold"] = need(flat(T["panel"]), %s, "PANEL.md\'s cold hold").group(0)' % lit(pat_cold), "PANEL.md's cold hold")):
        new, ch = set_line(new, prefix, line, "l4e11_power.py")
        if ch:
            changes.append(("need()", what, (c08 if what == "FW-C08" else a14 if what == "FW-A14" else cold[0] if "cold" in what else "unchanged")[:90] + "..."))
    return src, new, changes


def plan_l4e9():
    src = text(L4E9_PY)
    new, changes = src, []
    for key, rel in (("hwfw", HWFW), ("ifaces", IFACES), ("reqs", REQS), ("l4e5", L4E5_OUT), ("l4e11", L4E11_OUT), ("l4e7r", L4E7_OUT)):
        new, ch = repin(new, key, rel, sha(rel), "l4e9_power_path.py")
        if ch:
            changes.append(ch)
    return src, new, changes


def show(who, changes):
    for c in changes:
        if c[0] in ("mechanism", "need()"):
            print("%-7s %-24s %-10s %s %s" % (c[0], who, "", c[1], c[2]))
        else:
            print("repin   %-24s %-10s %s -> %s" % (who, c[0], c[1], c[2]))


def main(argv):
    mode = "--write" if "--write" in argv else "--check"
    do_regen = "--no-regen" not in argv
    for rel in (L4E5_PY, L4E11_PY, L4E9_PY, HWFW, PANEL, IFACES, REQS, L4E5_OUT, L4E11_OUT, L4E9_OUT):
        if not os.path.isfile(os.path.join(TOP, rel)):
            refuse("%s is missing" % rel)
    # a dry pass over all three, on the tree as it is (L4-E9's l4e5 and l4e11 pins are judged on the committed outputs here)
    s5, n5, c5 = plan_l4e5()
    s7, n7, c7 = plan_l4e7()
    s11, n11, c11 = plan_l4e11()
    s9, n9, c9 = plan_l4e9()
    if not (c5 or c7 or c11 or c9):
        print("apply_set28_repins: already applied: every pin is the tree's, L4-E5 reads the contract where it analysed it and every "
              "need() text is the merged files'; nothing written (regen_out.py re-proves the outputs by hand if wanted)")
        return 3
    if mode == "--check":
        print("apply_set28_repins: --check, nothing written; --write would make these changes and regenerate the outputs (L4-E5, L4-E7, L4-E11, L4-E9, then Layer 5's and 7's):")
        show("l4e5_source_control.py", c5); show("l4e7_stage_settings.py", c7); show("l4e11_power.py", c11); show("l4e9_power_path.py", c9)
        return 0
    # L4-E5
    if c5:
        write(L4E5_PY, s5, n5, "l4e5_source_control.py"); show("l4e5_source_control.py", c5)
    regen(L4E5_PY, L4E5_OUT, do_regen)
    # L4-E7 (its pin of L4-E5's script; the output is expected byte-identical)
    s7, n7, c7 = plan_l4e7()
    if c7:
        write(L4E7_PY, s7, n7, "l4e7_stage_settings.py"); show("l4e7_stage_settings.py", c7)
    regen(L4E7_PY, L4E7_OUT, do_regen)
    # L4-E11 (its l4e5 pin read after L4-E5's regeneration)
    s11, n11, c11 = plan_l4e11()
    if c11:
        write(L4E11_PY, s11, n11, "l4e11_power.py"); show("l4e11_power.py", c11)
    regen(L4E11_PY, L4E11_OUT, do_regen)
    # L4-E9 (its l4e5 and l4e11 pins read after their regeneration)
    s9, n9, c9 = plan_l4e9()
    if c9:
        write(L4E9_PY, s9, n9, "l4e9_power_path.py"); show("l4e9_power_path.py", c9)
    regen(L4E9_PY, L4E9_OUT, do_regen)
    # the Layer 5 and 7 outputs (they print the shas of L4-E9's and L4-E11's outputs and of the registry)
    for py, out in LATER:
        if os.path.isfile(os.path.join(TOP, py)):
            regen(py, out, do_regen)
    print("apply_set28_repins: done; stale after this and NOT touched here (the coordinator's freeze): the pins of %s in "
          "l4e10_cell_thermal.py, l4e12_thermal.py and l4e13_panel.py once apply_set28_rebind.py has run, and L4-E9's pins of their "
          "outputs once those are regenerated" % REQS)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
