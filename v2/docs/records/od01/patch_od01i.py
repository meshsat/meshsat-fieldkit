#!/usr/bin/env python3
"""The integrator's answers to check 9's wording items t1 to t5 (MESHSAT-1357, 29 September 2026; `checks/check-9.md`,
acceptable yes, no blocking item). Text only: the patch runs' two limits named wherever one was (t1, t2), their record
columns (t3), section 8's CH5 and CH6 rows qualified to the steady-state steps (t4), and the account name in the filed
check 8 generalised (t5). Old texts matched with any whitespace between words, each exactly once; refuses a second run.
Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")
ACCOUNT = "claude" + "-runner"


def refuse(m):
    print("patch_od01i: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t or any(d in t2 for d in DASHES): refuse("%s unchanged or a dash" % path)
    open(p, "w", encoding="utf-8").write(t2)


def main():
    if os.path.exists(os.path.join(TOP, OD, "checks/check-9.md")): refuse("already applied (check-9 filed)")
    edit(OD + "TEST-PROCEDURE.md", [
        ("section 8's 110 C limit on the HS100 is the operator's.",
         "section 8's limits for the patch runs (110 C at CH7, 70 C at CH4) are the operator's."),
        ("and stop at the patch stop of 110 C,", "and stop at the patch stops (110 C at CH7, 70 C at CH4),"),
        ("`pulse, watts, seconds, plate_start_C, peak_C, time_to_110C_s`",
         "`pulse, watts, seconds, plate_start_C, peak_C, time_to_stop_s, stopped_by` (CH7 or CH4; empty\n  when the pulse ran its full time)"),
        ("| Case floor or wall (CH5) | 70 C |", "| Case floor or wall (CH5, steady-state steps) | 70 C |"),
        ("| H2 (CH6) | 100 C |", "| H2 (CH6, steady-state steps) | 100 C |"),
    ])
    p = os.path.join(TOP, OD, "checks/check-8.md")
    t = open(p, encoding="utf-8").read()
    if t.count('"%s"' % ACCOUNT) != 1: refuse("check-8: the account name")
    open(p, "w", encoding="utf-8").write(t.replace('"%s"' % ACCOUNT, "the runner's account name"))
    print("patch_od01i: t1 to t5 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
