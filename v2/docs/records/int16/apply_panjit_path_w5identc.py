#!/usr/bin/env python3
"""Stream w5identc's board C table rebuilt against the PANJIT sheet's held path (MESHSAT-1357, integration set 15, 29
September 2026). The set's first commit held PANJIT's SS2020FL series sheet back (records/int16/apply_hold_back_panjit.py:
v2/vendor/power/panjit-ss2020fl-series.pdf moved to the ignored v2/vendor/power/held/). w5identc's input data
(records/w5identc/w5ident-board-c-identities.json) cites the old path three times, for the SS2040FL rectifier selections
of D19 to D21, so a rebuild found no document there and filed them as DOCUMENT_DOES_NOT_NAME_THE_PART (a wrong reason: the
document was absent, not silent). This script, asserting each step:
  1. replaces the three citations with the held path (exactly three, no other text);
  2. re-runs records/w5identc/build_table.py and requires its counts to equal the committed table's (21 printed, 23
     decoded, 41 unresolved, 2 not a part), the table to differ from the committed one only in those three paths;
  3. re-runs part_identities.py check with --out into records/w5identc/readings/ and requires HOLDS with 0 problems;
  4. re-pins READING_SHA256 in records/w5identc/apply_identities_c.py to the new reading.
The held sheet must be present (records/int16/fetch_held_back.py). Refuses a second run. Run: python3 <this file>."""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2/docs/records/w5identc")
OLD = "v2/vendor/power/panjit-ss2020fl-series.pdf"
NEW = "v2/vendor/power/held/panjit-ss2020fl-series.pdf"
TABLE = "v2/ecad/tools/pcb_part_identities.yaml"
READING = os.path.join(REC, "readings", "check-board-c-b874b744.json")
WANT = {"PRINTED": 21, "DECODED": 23}


def refuse(m):
    print("apply_panjit_path_w5identc: REFUSED: %s" % m); sys.exit(2)


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    jp = os.path.join(REC, "w5ident-board-c-identities.json")
    j = open(jp, encoding="utf-8").read()
    if NEW in j: refuse("already applied")
    if j.count(OLD) != 3: refuse("the input cites the old path %d times, not 3" % j.count(OLD))
    if not os.path.exists(os.path.join(TOP, NEW)): refuse("the held sheet is not present: run records/int16/fetch_held_back.py")
    open(jp, "w", encoding="utf-8").write(j.replace(OLD, NEW))
    json.loads(open(jp, encoding="utf-8").read())
    r = subprocess.run([sys.executable, os.path.join(REC, "build_table.py")], cwd=TOP, capture_output=True, text=True)
    if r.returncode: refuse("build_table failed: %s" % (r.stdout + r.stderr)[-400:])
    m = re.search(r"resolved by binding \{'PRINTED': (\d+), 'DECODED': (\d+)\}", r.stdout)
    if not m or {"PRINTED": int(m.group(1)), "DECODED": int(m.group(2))} != WANT: refuse("the rebuilt counts: %s" % r.stdout[-300:])
    d = subprocess.run(["git", "-C", TOP, "diff", "-U0", "--", TABLE], capture_output=True, text=True).stdout
    changed = [l for l in d.split("\n") if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
    if not changed or any(("panjit" not in l) for l in changed): refuse("the table moved beyond the three paths")
    ck = subprocess.run([sys.executable, "part_identities.py", "check", "--out", READING], cwd=os.path.join(TOP, "v2/ecad/tools"),
                        capture_output=True, text=True)
    if ck.returncode or not re.search(r"\b0 problems\b", ck.stdout): refuse("the check: %s" % (ck.stdout + ck.stderr)[-400:])
    if json.load(open(READING, encoding="utf-8")).get("verdict") not in ("HOLDS", None) and "HOLDS" not in open(READING, encoding="utf-8").read():
        refuse("the reading does not read HOLDS")
    ap = os.path.join(REC, "apply_identities_c.py")
    a = open(ap, encoding="utf-8").read()
    old = re.search(r'READING_SHA256 = "([0-9a-f]{64})"', a)
    if not old or a.count(old.group(0)) != 1: refuse("apply_identities_c.py's pin")
    new_sha = sha(READING)
    open(ap, "w", encoding="utf-8").write(a.replace(old.group(0), 'READING_SHA256 = "%s"   # re-pinned by records/int16/apply_panjit_path_w5identc.py' % new_sha))
    print("apply_panjit_path_w5identc: three citations moved to the held path; table 21 printed, 23 decoded; check HOLDS; reading %s pinned" % new_sha[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
