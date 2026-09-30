#!/usr/bin/env python3
"""Set 15's re-check (records/int16/checks/check-int16-2.md) answered (MESHSAT-1357, 30 September 2026). Every edit is
staged and asserted before any file is written:
  R1  the registry's S-125 names the identity reading by sha256; apply_panjit_held_w5identc.py re-took that reading, so
      the sha is re-read from the file and written in; "ruled by apply_decision_decoded.py" becomes "written by", since
      decision 59's ruled_by is the session, not the script.
  m1  apply_check16_fixes.py matches TI's en dash through the escape \\u2013, not a literal one.
  m2  records/int16/README.md step 4 names the script that recorded decision 59 and rebound CFL-016.
Refuses a second run. Run: python3 <this file>, then rules_render.py --requirements."""
import hashlib, os, re, subprocess, sys
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PENDING = {}


def refuse(m):
    print("apply_check16b_fixes: REFUSED: %s" % m); sys.exit(2)


def edit(rel, old, new, parse=None):
    p = os.path.join(TOP, rel); t = PENDING.get(p, open(p, encoding="utf-8").read())
    if t.count(old) != 1: refuse("%s: the old text appears %d times" % (rel, t.count(old)))
    u = t.replace(old, new); assert u != t
    if parse: parse(u)
    PENDING[p] = u


def main():
    rd = os.path.join(TOP, "v2/docs/records/w5identc/readings/check-board-c-b874b744.json")
    now = hashlib.sha256(open(rd, "rb").read()).hexdigest()[:16]
    reg = "v2/ecad/tools/pcb_requirements.yaml"
    t = open(os.path.join(TOP, reg), encoding="utf-8").read()
    if "decision 59, written by apply_decision_decoded.py" in t: refuse("already applied")
    m = re.search(r"check-board-c-b874b744\.json, sha256 ([0-9a-f]{16})\)", t)
    if not m: refuse("S-125 names no reading sha")
    if m.group(1) == now: refuse("S-125 already names the reading's sha %s" % now)
    edit(reg, "check-board-c-b874b744.json, sha256 %s)" % m.group(1), "check-board-c-b874b744.json, sha256 %s)" % now, parse=yaml.safe_load)
    edit(reg, "decision 59, ruled by apply_decision_decoded.py", "decision 59, written by apply_decision_decoded.py", parse=yaml.safe_load)
    edit("v2/docs/records/int16/apply_check16_fixes.py", '"TJ Junction temperature \u201340 125",', '"TJ Junction temperature \\u201340 125",',
         parse=lambda u: compile(u, "apply_check16_fixes.py", "exec"))
    edit("v2/docs/records/int16/README.md",
         "| 4 | `records/w5identc/apply_identities_c.py` | decision 59 recorded, CFL-016 rebound, S-125 opened |",
         "| 4 | `records/w5identc/apply_decision_decoded.py`, `records/w5identc/apply_identities_c.py` | decision 59 recorded and CFL-016 rebound (the first); S-125 opened (the second) |")
    for p, u in PENDING.items(): open(p, "w", encoding="utf-8").write(u)
    print("apply_check16b_fixes: S-125 names the reading at %s (was %s) and decision 59 as written by its script; the en dash escaped; README step 4 corrected" % (now, m.group(1)))


if __name__ == "__main__":
    main()
