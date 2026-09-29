#!/usr/bin/env python3
"""Set 15's integration check (records/int16/checks/check-int16-1.md) minors answered (MESHSAT-1357, 30 September 2026).
Each edit asserts its old text once, writes the new text, and re-parses what it touched:
  m6  records/w5identc/README.md: the reading and table shas re-pinned by apply_panjit_held_w5identc.py, and the PANJIT
      bindings' UNREAD state stated; the registry's S-125: decision 59 is ruled, not drafted.
  m7  NOT edited here: decision 59's ask says "20 part numbers" where the check counts 20 identities of 14 distinct part
      numbers; an edit to tools/pcb_decisions.yaml moves the file CFL-016's reading and S-122's outputs are bound to (a
      first run of this script did so and rules_lib refused CFL-016), so the correction is recorded in records/int16/README.md
      and carried to the next change of that file.
  m8  records/s122/apply_docs_s122_r4.py line 69: TI's en dash written as the escape \\u2013 (identical at run time).
Refuses a second run. Run: python3 <this file>, then the renders."""
import hashlib, os, subprocess, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()


def refuse(m):
    print("apply_check16_fixes: REFUSED: %s" % m); sys.exit(2)


PENDING = {}


def edit(rel, old, new, parse=None, flex=False):
    """Stage one edit; nothing is written until every edit has been found (main writes them together). With flex the
    old text matches across the line folds of a YAML block scalar (any run of whitespace)."""
    p = os.path.join(TOP, rel); t = PENDING.get(p, open(p, encoding="utf-8").read())
    if flex:
        import re
        pat = re.compile(r"\s+".join(re.escape(w) for w in old.split()))
        hits = pat.findall(t)
        if len(hits) != 1: refuse("%s: the old text appears %d times" % (rel, len(hits)))
        u = pat.sub(lambda m: new, t, count=1)
    else:
        if t.count(old) != 1: refuse("%s: the old text appears %d times" % (rel, t.count(old)))
        u = t.replace(old, new)
    assert u != t
    if parse: parse(u)
    PENDING[p] = u


def main():
    rd = os.path.join(TOP, "v2/docs/records/w5identc/readings/check-board-c-b874b744.json")
    tb = os.path.join(TOP, "v2/ecad/tools/pcb_part_identities.yaml")
    r16, t16 = hashlib.sha256(open(rd, "rb").read()).hexdigest()[:8], hashlib.sha256(open(tb, "rb").read()).hexdigest()[:8]
    if "re-pinned at integration set 15" in open(os.path.join(TOP, "v2/docs/records/w5identc/README.md"), encoding="utf-8").read():
        refuse("already applied")
    edit("v2/docs/records/w5identc/README.md",
         "verdict HOLDS** (reading `45d8f109...`, table `bea90e3c...`, tool `26c7862e...`). Without the fetched sheet it reads 13",
         "verdict HOLDS** (reading `%s...`, table `%s...`, tool `26c7862e...`, re-pinned at integration set 15 by "
         "`records/int16/apply_panjit_held_w5identc.py`, which marked the three PANJIT bindings of D19 to D21 held back; "
         "they read UNREAD likewise without PANJIT's sheet, fetched by `records/int16/fetch_held_back.py`). Without the fetched sheet it reads 13" % (r16, t16))
    edit("v2/ecad/tools/pcb_requirements.yaml",
         "the session's decision drafted by apply_decision_decoded.py;",
         "the session's decision 59, ruled by apply_decision_decoded.py;", parse=yaml.safe_load, flex=True)
    edit("v2/docs/records/s122/apply_docs_s122_r4.py",
         "TJ Junction temperature –40 125",
         "TJ Junction temperature \\u204040 125".replace("\\u2040", "\\u2013"),
         parse=lambda u: compile(u, "apply_docs_s122_r4.py", "exec"))
    for p, u in PENDING.items(): open(p, "w", encoding="utf-8").write(u)
    print("apply_check16_fixes: w5identc README re-pinned (reading %s, table %s); S-125 names decision 59 as ruled; "
          "apply_docs_s122_r4.py carries no literal en dash" % (r16, t16))


if __name__ == "__main__":
    main()
