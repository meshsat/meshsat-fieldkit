#!/usr/bin/env python3
"""The integrator's answers to the re-check of set 14 (MESHSAT-1357, 29 September 2026; `checks/check-int15-2.md`).
  B1  S-122's extension was only in its title, and `records/s122/close_s122.py` never read it: run on this line with the
      filed check-s122-3, it closed S-122 again. This script inserts a gate into close_s122.py that refuses unless
      (a) the inventory declares that it reads makers' part numbers (its header carries "# Part numbers read: yes"),
      (b) the five sentences no longer name the parts check-int15-1 found (V2-SPEC.md: no TMDS341A, no WM8960, no LM5176 on
          its E6 row; OPERATING-ENVELOPE.md: no TEN 40, no Amphenol M.2 B-key); the re-check found all five false at their
          own stated dates, so none may close as dated,
      (c) the filed check names check-int15-1 and was committed on a line that carries 097d2517;
      and appends to S-122's title that a sentence closes as dated only if its parts are shown in the generators at that date.
  n3, n4, n5, n6  the records index row for int15/; the s120 README's note on the filed copies; the wording "stale sentences
      corrected"; the dash guard of apply_check15_fixes.py written as escapes. n1 and n2 in this directory's README.
Refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

TAG = "apply_check15b_fixes"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CLOSE = os.path.join(TOP, "v2/docs/records/s122/close_s122.py")
SCRATCH = os.path.join(os.path.expanduser("~"), "worktrees", "meshsat-fieldkit", "_scratch")
DASHES = ("\u2014", "\u2013")

GATE = '''

def gate_set14(chk):
    """Set 14's gate (v2/docs/records/int15/apply_check15b_fixes.py, answering check-int15-2 B1): S-122 closes only on a
    part-number inventory, with the five sentences check-int15-1 found corrected, and on a check filed after 097d2517."""
    head = open(os.path.join(L.TOP, "v2/docs/records/s122/inventory.out"), encoding="utf-8").read().split("\\n")[:12]
    if "# Part numbers read: yes" not in head:
        refuse("the inventory does not declare that it reads makers' part numbers (S-122's set 14 extension)")
    spec = open(os.path.join(L.TOP, "v2/docs/V2-SPEC.md"), encoding="utf-8").read()
    env = open(os.path.join(L.TOP, "v2/docs/OPERATING-ENVELOPE.md"), encoding="utf-8").read()
    left = [n for n, hit in (("V2-SPEC.md names the TMDS341A", "TMDS341A" in spec),
                             ("V2-SPEC.md names the WM8960", "WM8960" in spec),
                             ("V2-SPEC.md's E6 row names the LM5176",
                              any(l.startswith("| E6 |") and "LM5176" in l for l in spec.split("\\n"))),
                             ("OPERATING-ENVELOPE.md names a TEN 40", "TEN 40" in env),
                             ("OPERATING-ENVELOPE.md names an Amphenol M.2 B-key socket", "Amphenol M.2 B-key" in env)) if hit]
    if left: refuse("check-int15-1's sentences still stand: %s" % "; ".join(left))
    body = open(chk, encoding="utf-8").read()
    if "check-int15-1" not in body: refuse("the check does not name check-int15-1")
    added = subprocess.run(["git", "-C", L.TOP, "log", "--diff-filter=A", "--format=%H", "--", os.path.relpath(os.path.abspath(chk), L.TOP)],
                           capture_output=True, text=True).stdout.split()
    if not added or subprocess.run(["git", "-C", L.TOP, "merge-base", "--is-ancestor", "097d2517", added[-1]]).returncode:
        refuse("the check was not committed on a line that carries 097d2517 (set 14's extension of S-122)")
'''

S122_ADD = (
    "Added at set 14's re-check (v2/docs/records/int15/checks/check-int15-2.md, blocking B1): a sentence closes as dated only "
    "if the parts it names are shown in the generators at the date it states; the re-check found the five sentences above "
    "false at their own dates, so they close only corrected. v2/docs/records/s122/close_s122.py refuses unless the "
    "inventory declares that it reads part numbers, the five sentences are corrected, and the filed check names "
    "check-int15-1 and was committed on a line that carries 097d2517.")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m)); sys.exit(2)


def scrub(t):
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*?/_scratch/", "<scratch>/", t)
    t = re.sub(r"(?<![<\w/])_scratch/", "<scratch>/", t)
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*", "<local path>", t)
    return t.replace("`claude-runner`", "the runner's account name").replace("claude-runner", "the runner's account")


def edit(rel, pairs):
    p = os.path.join(TOP, rel); s = open(p, encoding="utf-8").read(); s0 = s
    for o, n in pairs:
        if s.count(o) != 1: refuse("%s: %r found %d times" % (rel, o[:60], s.count(o)))
        s = s.replace(o, n)
    if s == s0: refuse("%s unchanged" % rel)
    open(p, "w", encoding="utf-8").write(s)


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg or "def gate_set14" in open(CLOSE, encoding="utf-8").read(): refuse("already applied")
    for t in (S122_ADD,):
        A.screen(t, TAG)
        if any(d in t for d in DASHES): refuse("a dash")
    src = os.path.join(SCRATCH, "chk-int15", "CHECK-2.md")
    c = scrub(open(src, encoding="utf-8").read())
    if not c.startswith("mergeable: no") or re.search(r"/(home|root|tmp)/|claude-runner", c): refuse("the check's text")
    open(os.path.join(HERE, "checks", "check-int15-2.md"), "w", encoding="utf-8").write(c)
    # the gate, called first in main
    cs = open(CLOSE, encoding="utf-8").read()
    o_def = "\n\ndef main():\n"
    o_call = '    chk = sys.argv[1]\n'
    if cs.count(o_def) != 1 or cs.count(o_call) != 1: refuse("close_s122.py's anchors")
    cs = cs.replace(o_def, GATE + o_def, 1).replace(o_call, o_call + "    gate_set14(chk)\n", 1)
    if "import subprocess" not in cs and not re.search(r"(?m)^import [^\n]*\bsubprocess\b", cs):
        cs = cs.replace("import yaml", "import subprocess\n\nimport yaml", 1) if "import yaml" in cs else refuse("close_s122.py imports")
    import ast; ast.parse(cs)
    open(CLOSE, "w", encoding="utf-8").write(cs)
    # S-122's title
    before = yaml.safe_load(reg)
    out = reg
    i, j = A.span(out, "S-122")
    t = out[i:j]
    m = re.search(r"(?m)^    title: >-\n((?:      .*\n)+)", t)
    t = t[:m.end()] + A.fold(S122_ADD, 6, 120) + t[m.end():]
    out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if any(oi[x] != ai[x] for x in oi if x != "S-122") or before["records"] != after["records"] or before["closed_items"] != after["closed_items"]:
        refuse("something other than S-122's title moved")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    # the s122 README's closure step; n3, n4, n5, n6
    edit("v2/docs/records/s122/README.md", [("5. `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>`",
          "5. `python3 v2/docs/records/s122/close_s122.py v2/docs/records/s122/checks/<the check>` (since set 14 it refuses unless the\n"
          "   inventory declares that it reads part numbers, check-int15-1's five sentences are corrected, and the check names\n"
          "   check-int15-1 and was committed on a line that carries 097d2517: `records/int15/apply_check15b_fixes.py`)")])
    rt = open(os.path.join(TOP, "v2/docs/records/README.md"), encoding="utf-8").read()
    edit("v2/docs/records/README.md", [(
        "stale sentences corrected, CONOPS restored to its baseline text with its current values on the status page; S-122 open until part numbers are inventoried (set 14's check) |",
        "the stale sentences its inventory found corrected, CONOPS restored to its baseline text with its current values on the status page; S-122 open until part numbers are inventoried and five more sentences corrected (set 14's checks) |"),
        ("| `int14/` | integration set 13",
         "| `int15/` | integration set 14 (29 September 2026, branch `fnd/int15`): s120 and s122 merged, their registry scripts run, S-122's closure withdrawn as premature and its extension enforced in its closing script, the checks |\n"
         "| `int14/` | integration set 13")])
    edit("v2/docs/records/int15/README.md", [(
        "  - The stale sentences are corrected.",
        "  - The stale sentences its inventory found are corrected; five more, found by set 14's check, stay with S-122.")])
    s120 = os.path.join(TOP, "v2/docs/records/s120/README.md")
    st = open(s120, encoding="utf-8").read()
    st = st.rstrip("\n") + ("\n\n## The checks, filed\n\nThe four independent checks of this stream are filed as `checks/check-s120-1.md` to "
                            "`check-s120-4.md` by `records/int15/apply_check15_fixes.py`; they differ from the reports the checker wrote "
                            "only where a local path became `<scratch>/`. Where this README or LOG.md cites a check at its scratch path, "
                            "the filed copy is the record.\n")
    open(s120, "w", encoding="utf-8").write(st)
    p15 = os.path.join(HERE, "apply_check15_fixes.py")
    s15 = open(p15, encoding="utf-8").read()
    lit = 'DASHES = ("' + "\u2014" + '", "' + "\u2013" + '")'
    if s15.count(lit) != 1: refuse("apply_check15_fixes.py's dash guard")
    s15 = s15.replace(lit, 'DASHES = ("\\u2014", "\\u2013")')
    ast.parse(s15); open(p15, "w", encoding="utf-8").write(s15)
    print("%s: close_s122.py gated; S-122's title extended; check-int15-2 filed; n3, n4, n5, n6 fixed" % TAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
