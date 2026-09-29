#!/usr/bin/env python3
"""The integrator's answers to the third check of set 14 (MESHSAT-1357, 29 September 2026; `checks/check-int15-3.md`).
  B1  S-122's sentence of apply_check15b said close_s122.py refuses unless "the five sentences are corrected", while its gate
      checked five literal strings and a declared token: five other wrong parts passed, and one header line set the token.
      This script replaces gate_set14 with an instrument:
        (a) the finder itself (s122lib.names) is run on probe sentences that name only a maker's part number, and must
            return each part number under a `parts` key (today's finder has none, so the gate refuses);
        (b) verdicts.out must carry an assertion naming each generated part the corrected sentences name: board B's U3 or
            U4 as TS3DV642, board E's U6 as LM5069, board D's U6 as PCM2912A, board B's J_M2C2 as TE 2199119;
        (c) the five ROWS (not the whole files, p1) no longer name the parts: V2-SPEC.md's B16, APRS and E6 rows,
            OPERATING-ENVELOPE.md's TRACO and Amphenol rows;
        (d) the filed check names check-int15-1 and was added on a line that carries 097d2517, its path resolved against
            the repository (p2);
      and appends to S-122 exactly what the gate checks, and that confirming each correction's substance is the filed
      check's job (p3's wording corrected in the same sentence).
  p4  close_s122.py appends S-122 at the END of closed_items.
  p5, p6  the records index row's word "enforced"; a filing note heading every filed check of int15 and s120.
Refuses a second run. Run: python3 <this file>."""
import ast, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

TAG = "apply_check15c_fixes"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CLOSE = os.path.join(TOP, "v2/docs/records/s122/close_s122.py")
SCRATCH = os.path.join(os.path.expanduser("~"), "worktrees", "meshsat-fieldkit", "_scratch")
DASHES = ("\u2014", "\u2013")

GATE = '''def gate_set14(chk):
    """Set 14's gate (v2/docs/records/int15/apply_check15c_fixes.py, answering check-int15-3 B1): S-122 closes only when
    the finder reads makers' part numbers (probed), the verdicts assert the generated parts the corrected sentences name,
    the five rows no longer name the parts check-int15-1 found, and the check is filed after 097d2517."""
    probes = (("the WM8960 codec", "WM8960"), ("a TRACO TEN 40-2412WIN converter", "TEN 40-2412WIN"),
              ("an Amphenol M.2 B-key socket, MDT420B01001", "MDT420B01001"), ("the TMDS341A display switch", "TMDS341A"),
              ("two TS3DV642 switches", "TS3DV642"))
    nets = L.all_nets(L.netlists())
    for sent, part in probes:
        got = L.names(sent, nets)
        if part not in " ".join(str(x) for x in (got.get("parts") or [])):
            refuse("the finder does not read the part number %s in %r (S-122's set 14 extension)" % (part, sent))
    ver = open(os.path.join(L.TOP, "v2/docs/records/s122/verdicts.out"), encoding="utf-8").read()
    for label, pat in (("board B's U3 or U4 as TS3DV642", r"\\bB U[34] value has '[^']*TS3DV642"),
                       ("board E's U6 as LM5069", r"\\bE U6 value has '[^']*LM5069"),
                       ("board D's U6 as PCM2912A", r"\\bD U6 value has '[^']*PCM2912A"),
                       ("board B's J_M2C2 as TE 2199119", r"\\bB J_M2C2 value has '[^']*2199119")):
        if not re.search(pat, ver): refuse("verdicts.out asserts no %s" % label)
    spec = open(os.path.join(L.TOP, "v2/docs/V2-SPEC.md"), encoding="utf-8").read().split("\\n")
    env = open(os.path.join(L.TOP, "v2/docs/OPERATING-ENVELOPE.md"), encoding="utf-8").read().split("\\n")
    def row(lines, head): return [l for l in lines if l.startswith(head)]
    left = []
    if any("TMDS341A" in l for l in row(spec, "| B16 |")): left.append("V2-SPEC.md's B16 row names the TMDS341A")
    if any("WM8960" in l for l in row(spec, "| APRS and VHF voice |")): left.append("V2-SPEC.md's APRS row names the WM8960")
    if any("LM5176" in l and "A22" not in l for l in row(spec, "| E6 |")): left.append("V2-SPEC.md's E6 row puts the LM5176 on E6")
    if row(env, "| TRACO TEN 40"): left.append("OPERATING-ENVELOPE.md keeps its TRACO TEN 40 row")
    if row(env, "| Amphenol M.2 B-key socket |"): left.append("OPERATING-ENVELOPE.md keeps its Amphenol M.2 B-key row")
    if left: refuse("check-int15-1's sentences still stand: %s" % "; ".join(left))
    path = chk if os.path.isabs(chk) else os.path.join(L.TOP, chk)
    if not os.path.exists(path): refuse("no check at %s" % chk)
    if "check-int15-1" not in open(path, encoding="utf-8").read(): refuse("the check does not name check-int15-1")
    added = subprocess.run(["git", "-C", L.TOP, "log", "--diff-filter=A", "--format=%H", "--", os.path.relpath(path, L.TOP)],
                           capture_output=True, text=True).stdout.split()
    if not added or subprocess.run(["git", "-C", L.TOP, "merge-base", "--is-ancestor", "097d2517", added[-1]]).returncode:
        refuse("the check was not committed on a line that carries 097d2517 (set 14's extension of S-122)")
'''

S122_ADD = (
    "Correction at set 14's third check (v2/docs/records/int15/checks/check-int15-3.md, blocking B1): the previous sentence "
    "overstated the closing script. What v2/docs/records/s122/close_s122.py checks, since v2/docs/records/int15/"
    "apply_check15c_fixes.py: the finder returns a maker's part number from probe sentences that name only one; verdicts.out "
    "asserts board B's U3 or U4 as TS3DV642, board E's U6 as LM5069, board D's U6 as PCM2912A and board B's J_M2C2 as "
    "2199119; V2-SPEC.md's B16, APRS and E6 rows and OPERATING-ENVELOPE.md's TRACO and Amphenol rows no longer name the "
    "parts check-int15-1 found; and the filed check names check-int15-1 and was committed on a line that carries 097d2517. "
    "Confirming that each correction is true in substance remains the filed check's job. check-int15-2 found lines 82 and "
    "86 false at their stated date; lines 47, 77 and 83 carry no date.")
NOTE = ("<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> "
        "(records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->\n")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m)); sys.exit(2)


def scrub(t):
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*?/_scratch/", "<scratch>/", t)
    t = re.sub(r"(?<![<\w/])_scratch/", "<scratch>/", t)
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*", "<local path>", t)
    return t.replace("`claude-runner`", "the runner's account name").replace("claude-runner", "the runner's account")


def main():
    reg = open(REG, encoding="utf-8").read()
    cs = open(CLOSE, encoding="utf-8").read()
    if TAG in reg or "L.names(sent, nets)" in cs: refuse("already applied")
    A.screen(S122_ADD, TAG)
    if any(d in S122_ADD for d in DASHES): refuse("a dash")
    c = scrub(open(os.path.join(SCRATCH, "chk-int15", "CHECK-3.md"), encoding="utf-8").read())
    if not c.startswith("mergeable: no") or re.search(r"/(home|root|tmp)/|claude-runner", c): refuse("the check's text")
    open(os.path.join(HERE, "checks", "check-int15-3.md"), "w", encoding="utf-8").write(c)
    # the gate replaced; S-122 appended at the end of closed_items (p4)
    i = cs.index("def gate_set14(chk):"); j = cs.index("\n\ndef main():")
    cs = cs[:i] + GATE.rstrip("\n") + cs[j:]
    o = '    ci = out.index("\\nclosed_items:\\n") + len("\\nclosed_items:\\n")\n'
    if cs.count(o) != 1: refuse("close_s122.py's closed_items insertion")
    cs = cs.replace(o, '    ci = out.index("\\nrecords:\\n") + 1   # the end of closed_items (check-int15-3 p4)\n', 1)
    ast.parse(cs)
    open(CLOSE, "w", encoding="utf-8").write(cs)
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
    # p5, p6
    rp = os.path.join(TOP, "v2/docs/records/README.md"); rt = open(rp, encoding="utf-8").read()
    o5 = "S-122's closure withdrawn as premature and its extension enforced in its closing script, the checks |"
    if rt.count(o5) != 1: refuse("the int15/ index row")
    open(rp, "w", encoding="utf-8").write(rt.replace(o5, "S-122's closure withdrawn as premature and its closing script gated on a part-number finder and the corrected rows, the substance left to the filed check, the checks |"))
    for d in ("v2/docs/records/int15/checks", "v2/docs/records/s120/checks"):
        for f in sorted(os.listdir(os.path.join(TOP, d))):
            p = os.path.join(TOP, d, f); s = open(p, encoding="utf-8").read()
            if NOTE not in s: open(p, "w", encoding="utf-8").write(s.rstrip("\n") + "\n\n" + NOTE)   # at the end: the first line stays "mergeable: ..."
    print("%s: gate_set14 replaced by an instrument; S-122 corrected; closed_items order; check-int15-3 filed; notes" % TAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
