#!/usr/bin/env python3
"""apply_set28b_repins.py: the pins integration set 28 moves (MESHSAT-1357, 3 October 2026, branch fnd/int28b on set 27's frozen
candidate 94971c8c; records/int28b/README.md). Layer 5's rounds (l5pwr, l5r2) rewrote v2/docs/HW-FW-CONTRACT.md, v2/docs/PANEL.md
section 10 and v2/ecad/tools/pcb_interfaces.yaml; Layer 6's round 2 corrected v2/ecad/tools/lcsc_fill.py's table; L4-E7's R-176 round
(d562e75a) changed its page. The Layer 4 readers that pin those files refuse ("is not the pinned file"), and the outputs of Layers 5 to 9
that print their shas no longer bind. Every sha this script writes is READ from the tree at run time, never typed; nothing of any
record's prose or figures changes: pins and L4-E11's need() texts only. Every regeneration goes through _bin/regen_out.py.

  --stage pins  (before _bin/freeze_l4_chain.sh), in dependency order:
    L4-E8   ripple_dense.py: LCSC_FILL re-pinned (debt b); regenerated (its Cc2 search reads the 0603 lines of the table).
    L4-E5   l4e5_source_control.py reads the contract where it analysed it (2c240414, the mechanism of the superseded int28
            preparation, carried by the merge); nothing to re-pin (debt a); regenerated only if its output no longer binds.
    L4-E7   l4e7_stage_settings.py's pin of L4-E5's script (the int28 mechanism's one consequence); regenerated only if changed.
    L4-E11  l4e11_power.py: hwfw, panel, assembly (Layer 5's round 3, L5R3-F01), reqs, l4e5 and arch re-pinned (debt a); its need() texts for FW-C08, FW-A14 and PANEL.md's
            cold-hold sentence quoted from the merged files (E11-03, Layer 5's wording); regenerated.
    L4-E12  l4e12_thermal.py: LCSC_FILL and L4E8_OUT re-pinned (debt b); NOT regenerated here: the freeze re-pins its registry and
            L4-E10 pins and regenerates it.
    L4-E9   l4e9_power_path.py: hwfw, ifaces, reqs, l4e5, l4e11, l4e7r, l4e8, lcsc (debt b) and l4e7md (debt e, L4-E7's page at
            d562e75a: re-pin only, the wording of its R-176 note is the consolidation author's) re-pinned; regenerated. Its reader
            reads board E C5's fill code from lcsc_fill.py and need()s gen_sch_e.py to name it; a refusal is REPORTED, never forced
            (the generator is not edited here).
  --stage later (after the freeze): every output under records/l5*, l6*, l7*, l8* and v2/docs/test-procedures whose printed pins
            no longer bind (scan_printed_pins.py's test, regen_out's R4) is regenerated, in layer order (debt d is l8gnd's).

Usage, from anywhere:  apply_set28b_repins.py --stage pins|later [--check | --write]
  --check (default) prints what --write would change or regenerate; writes nothing.
Every write asserts the new text differs and re-parses the file (ast). A regen_out refusal leaves the committed output byte for byte
as it was, is printed with its reason, and the run continues; the exit is 1 when any regeneration refused, 3 when nothing was left
to do ("already applied"), 0 otherwise."""
import ast
import glob
import hashlib
import importlib.util
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = "v2/docs/records"
L4E5_PY, L4E5_OUT = REC + "/l4e5/l4e5_source_control.py", REC + "/l4e5/l4e5_source_control.out"
L4E7_PY, L4E7_OUT = REC + "/l4e7/l4e7_stage_settings.py", REC + "/l4e7/l4e7_stage_settings.out"
L4E7_MD = REC + "/l4e7/L4E7-CONTROL-DECISION.md"
L4E8_PY, L4E8_OUT = REC + "/l4e8/ripple_dense.py", REC + "/l4e8/ripple_dense.out"
L4E9_PY, L4E9_OUT = REC + "/l4e9/l4e9_power_path.py", REC + "/l4e9/l4e9_power_path.out"
L4E9_MD = REC + "/l4e9/L4-POWER-ARCHITECTURE.md"
L4E11_PY, L4E11_OUT = REC + "/l4e11/l4e11_power.py", REC + "/l4e11/l4e11_power.out"
L4E12_PY = REC + "/l4e12/l4e12_thermal.py"
HWFW, PANEL, ASSEMBLY = "v2/docs/HW-FW-CONTRACT.md", "v2/docs/PANEL.md", "v2/docs/ASSEMBLY.md"
IFACES, REQS, LCSC = "v2/ecad/tools/pcb_interfaces.yaml", "v2/ecad/tools/pcb_requirements.yaml", "v2/ecad/tools/lcsc_fill.py"
CONTRACT_COMMIT = "2c240414"      # L4-E5's mechanism: the last commit carrying the contract as L4-E5 analysed it
LATER_GLOBS = (REC + "/l5*/*.out", REC + "/l6*/*.out", REC + "/l7*/*.out", REC + "/l8*/*.out", "v2/docs/test-procedures/*.out")
REFUSED = []


def refuse(msg):
    print("apply_set28b_repins: REFUSED: %s" % msg)
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


def regen_mod():
    sp = importlib.util.spec_from_file_location("regen_out", regen_path())
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def unbound(out):
    """The printed pins of a committed output that are not the tree's (regen_out's R4, by its own patterns)."""
    R = regen_mod()
    bad = []
    for path, hx in R.pins(text(out)):
        p = os.path.join(TOP, path)
        if "@" in path or not os.path.isfile(p):
            continue
        if not sha(path).startswith(hx):
            bad.append((path, hx[:16], sha(path)[:16]))
    return sorted(set(bad))


def lit(pat):
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
    return [c.strip() for c in rows[0].strip().strip("|").split(" | ")]


def repin(src, key, rel, who):
    """PINS[key] = (rel, sha) in src set to the tree's sha; (new src, change or None)."""
    m = re.search(r'("%s": \("%s", ")([0-9a-f]{64})(")' % (re.escape(key), re.escape(rel)), src)
    if not m:
        refuse("%s: no PINS entry %r for %s" % (who, key, rel))
    cur = sha(rel)
    if m.group(2) == cur:
        return src, None
    return src[:m.start(2)] + cur + src[m.end(2):], (key, m.group(2)[:16], cur[:16])


def repin_const(src, name, rel, who):
    """The constant-style pin `    NAME: "<sha>",` (NAME = "<rel>" above it) set to the tree's sha; (new src, change or None)."""
    m = re.search(r'(\n    %s: ")([0-9a-f]{64})(",)' % re.escape(name), src)
    if not m or not re.search(r'(?m)^%s = "%s"' % (re.escape(name), re.escape(rel)), src):
        refuse("%s: no constant-style pin %s for %s" % (who, name, rel))
    cur = sha(rel)
    if m.group(2) == cur:
        return src, None
    return src[:m.start(2)] + cur + src[m.end(2):], (name, m.group(2)[:16], cur[:16])


def set_line(src, prefix, new_line, who):
    lines = src.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(idx) != 1:
        refuse("%s: %d line(s) start with %r, one expected" % (who, len(idx), prefix))
    if lines[idx[0]] == new_line:
        return src, False
    lines[idx[0]] = new_line
    return "\n".join(lines), True


def write(rel, old, new):
    if new == old:
        refuse("%s: the new text does not differ" % rel)
    ast.parse(new, filename=rel)
    with open(os.path.join(TOP, rel), "w", encoding="utf-8") as fh:
        fh.write(new)
    if text(rel) != new:
        refuse("%s: the file written does not read back" % rel)


def regen(py, out):
    r = subprocess.run([sys.executable, regen_path(), TOP, py, out], capture_output=True, text=True)
    lines = r.stdout.strip().splitlines() or [""]
    print("regen   %s" % lines[-1])
    if r.returncode != 0:
        for l in lines[:-1]:
            print("        %s" % l[:300])
        REFUSED.append((out, [l for l in lines[:-1] if "REFUSED" in l][:1]))
    return r.returncode == 0


def show(who, changes):
    for c in changes:
        if c[0] == "need()":
            print("need()  %-24s %s: %s" % (who, c[1], c[2]))
        else:
            print("repin   %-24s %-10s %s -> %s" % (who, c[0], c[1], c[2]))


# ------------------------------------------------------------------------------------------------------------------ plans
def plan_consts(rel, names, who):
    src = text(rel)
    new, ch = src, []
    for name, target in names:
        new, c = repin_const(new, name, target, who)
        if c:
            ch.append(c)
    return src, new, ch


def plan_l4e5():
    src = text(L4E5_PY)
    if "def contract_bytes():" not in src:
        refuse("l4e5_source_control.py does not carry the contract mechanism the int28 preparation added (merged with fnd/l5r2)")
    m = re.search(r'    CONTRACT: "([0-9a-f]{64})",', src)
    at = subprocess.run(["git", "show", "%s:%s" % (CONTRACT_COMMIT, HWFW)], cwd=TOP, capture_output=True)
    if not m or at.returncode != 0 or hashlib.sha256(at.stdout).hexdigest() != m.group(1):
        refuse("the contract at %s is not L4-E5's pinned file" % CONTRACT_COMMIT)
    return src, src, []


def plan_l4e11():
    src = text(L4E11_PY)
    new, changes = src, []
    for key, rel in (("hwfw", HWFW), ("panel", PANEL), ("assembly", ASSEMBLY), ("reqs", REQS), ("l4e5", L4E5_OUT), ("arch", L4E9_MD)):
        new, ch = repin(new, key, rel, "l4e11_power.py")
        if ch:
            changes.append(ch)
    hw, pn = text(HWFW), text(PANEL)
    fhw, fpn = flat(hw), flat(pn)
    c08, a14 = row_cells(hw, "FW-C08")[2], row_cells(hw, "FW-A14")[2]
    pat_c08 = r"\| FW-C08 \| (.*?) \| (" + re.escape(c08) + r") \|"
    pat_a14 = r"\| FW-A14 \| (CHG_INHIBIT .*?) \| (" + re.escape(a14) + r") \|"
    if once(pat_c08, fhw, "FW-C08").group(2) != c08 or once(pat_a14, fhw, "FW-A14").group(2) != a14:
        refuse("the FW-C08 or FW-A14 pattern does not capture the behaviour cell")
    i = pn.find("\n## 10. ")
    j = pn.find("\n## 11. ", i + 1)
    if i < 0 or j < 0:
        refuse("PANEL.md: section 10 not delimited")
    cold = [s for s in re.split(r"(?<=\.) (?=[A-Z*`])", flat(pn[i:j])) if "below 0 C" in s and "above 3 C" in s]
    if len(cold) != 1:
        refuse("PANEL.md section 10: %d sentence(s) carry 'below 0 C' and 'above 3 C', one expected" % len(cold))
    pat_cold = re.escape(cold[0])
    once(pat_cold, fpn, "PANEL.md's cold hold")
    pat_hi = r"high = the shore and vehicle inputs are held off at the front end, so nothing charges\."
    once(pat_hi, fpn, "PANEL.md section 10")
    for prefix, line, what, quoted in (
            ('    R["fwc08"] = need(', '    R["fwc08"] = need(flat(T["hwfw"]), %s, "FW-C08").group(2)' % lit(pat_c08), "FW-C08", c08),
            ('    R["fwa14"] = need(', '    R["fwa14"] = need(flat(T["hwfw"]), %s, "FW-A14").group(2)' % lit(pat_a14), "FW-A14", a14),
            ('    R["panel10"] = need(', '    R["panel10"] = need(flat(T["panel"]), %s, "PANEL.md section 10").group(0)' % lit(pat_hi), "PANEL.md section 10", "unchanged"),
            ('    R["panel10_cold"] = need(', '    R["panel10_cold"] = need(flat(T["panel"]), %s, "PANEL.md\'s cold hold").group(0)' % lit(pat_cold), "PANEL.md's cold hold", cold[0])):
        new, ch = set_line(new, prefix, line, "l4e11_power.py")
        if ch:
            changes.append(("need()", what, quoted[:90] + "..."))
    return src, new, changes


def plan_l4e9():
    src = text(L4E9_PY)
    new, changes = src, []
    for key, rel in (("hwfw", HWFW), ("ifaces", IFACES), ("reqs", REQS), ("l4e5", L4E5_OUT), ("l4e11", L4E11_OUT),
                     ("l4e7r", L4E7_OUT), ("l4e8", L4E8_OUT), ("lcsc", LCSC), ("l4e7md", L4E7_MD)):
        new, ch = repin(new, key, rel, "l4e9_power_path.py")
        if ch:
            changes.append(ch)
    return src, new, changes


def c5_report():
    """Debt b's question: L4-E9 reads board E C5's fill code from lcsc_fill.py and need()s gen_sch_e.py to name it."""
    lc = text(LCSC)
    m = re.search(r'\(r"\^100n", "C_0603"\): "(C\d+)"', lc)
    ge = text("v2/ecad/tools/gen_sch_e.py")
    want = "YAGEO CC0603KRX7R9BB104, LCSC %s" % (m.group(1) if m else "?")
    named = re.findall(r"YAGEO CC0603KRX7R\dBB104, LCSC (C\d+)", ge)
    line = [i + 1 for i, l in enumerate(ge.split("\n")) if "CC0603KRX7R" in l and "BB104, LCSC" in l]
    print("C5      lcsc_fill.py fills 100n 0603 with %s; L4-E9 needs gen_sch_e.py to say %r; the generator says LCSC %s at line(s) %s: %s"
          % (m.group(1) if m else "?", want, ", ".join(named) or "nothing", line, "it names it" if want in ge else "IT DOES NOT: L4-E9 refuses"))


# ------------------------------------------------------------------------------------------------------------------ stages
def stage_pins(write_it):
    plans = [
        ("l4e8", L4E8_PY, L4E8_OUT, lambda: plan_consts(L4E8_PY, (("LCSC_FILL", LCSC),), "ripple_dense.py"), True),
        ("l4e5", L4E5_PY, L4E5_OUT, plan_l4e5, True),
        ("l4e7", L4E7_PY, L4E7_OUT, lambda: plan_consts(L4E7_PY, (("L4E5_PY", L4E5_PY),), "l4e7_stage_settings.py"), True),
        ("l4e11", L4E11_PY, L4E11_OUT, plan_l4e11, True),
        ("l4e12", L4E12_PY, None, lambda: plan_consts(L4E12_PY, (("LCSC_FILL", LCSC), ("L4E8_OUT", L4E8_OUT)), "l4e12_thermal.py"), False),
        ("l4e9", L4E9_PY, L4E9_OUT, plan_l4e9, True),
    ]
    did = False
    for name, py, out, plan, do_regen in plans:
        old, new, ch = plan()
        stale = unbound(out) if out else []
        if not ch and not stale:
            print("ok      %-24s nothing to re-pin, its output binds" % os.path.basename(py))
            continue
        did = True
        show(os.path.basename(py), ch)
        if out and not ch:
            print("stale   %-24s its output prints %s" % (os.path.basename(out), ", ".join("%s at %s (tree %s)" % s for s in stale)))
        if not write_it:
            continue
        if ch:
            write(py, old, new)
        if out and do_regen:
            if name == "l4e9":
                c5_report()
            regen(py, out)
    if not did:
        print("apply_set28b_repins: --stage pins already applied: every pin is the tree's and every output binds")
        return 3
    return 0


def stage_later(write_it):
    outs = sorted({p for g in LATER_GLOBS for p in glob.glob(os.path.join(TOP, g))})
    tracked = set(subprocess.run(["git", "ls-files", "v2/docs"], cwd=TOP, capture_output=True, text=True, check=True).stdout.split())
    did = False
    for p in outs:
        out = os.path.relpath(p, TOP)
        py = out[:-4] + ".py"
        if out not in tracked or not os.path.isfile(os.path.join(TOP, py)):
            continue
        stale = unbound(out)
        if not stale:
            continue
        did = True
        print("stale   %-40s %s" % (out, ", ".join("%s (printed %s, tree %s)" % s for s in stale)))
        if write_it:
            regen(py, out)
    if not did:
        print("apply_set28b_repins: --stage later already applied: every output of Layers 5 to 9 binds to the tree")
        return 3
    return 0


def main(argv):
    if "--stage" not in argv or argv.index("--stage") + 1 >= len(argv):
        print(__doc__)
        return 2
    st = argv[argv.index("--stage") + 1]
    write_it = "--write" in argv
    rc = {"pins": stage_pins, "later": stage_later}[st](write_it)
    if REFUSED:
        print("apply_set28b_repins: %d regeneration(s) refused, their committed outputs unchanged: %s"
              % (len(REFUSED), "; ".join("%s (%s)" % (o, (w[0] if w else "")[:200]) for o, w in REFUSED)))
        return 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
