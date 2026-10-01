#!/usr/bin/env python3
"""L3-N01's acceptance check (the unified independent review, 1 October 2026): "Verify that deliberately making the
verifier accept the stale check makes the negative probe fail." Writes a copy of v2/docs/records/l3am/checks/verify_l3am.py
into a temporary directory with apply_l3am_findings_closed.verify replaced by a verifier that accepts any record (it
answers every call with the real verifier's answer for the newest accepted check), runs it on the worktree, and requires
exit 1 with the pre-amendment probe reading WRONG. Writes nothing in the tree. Usage: l3n01_mutation.py <worktree>"""
import os
import subprocess
import sys
import tempfile

WT = os.path.abspath(sys.argv[1])
SRC = os.path.join(WT, "v2/docs/records/l3am/checks/verify_l3am.py")
HOOK = "import apply_l3am_findings_closed as CL\n"
MUTANT = ("_real = CL.verify\n"
          "CL.verify = lambda record, data, head='HEAD', req=None, allow_abs=False: "
          "_real(str(RL.handover_checks(data)[-1]['record']), data, head=head, req=req)  # MUTANT: accepts any record\n")
s = open(SRC, encoding="utf-8").read()
assert s.count(HOOK) == 1, "verify_l3am.py does not import the verifier once"
d = tempfile.mkdtemp(prefix="l3n01-")
p = os.path.join(d, "verify_l3am_mutant.py")
open(p, "w", encoding="utf-8").write(s.replace(HOOK, HOOK + MUTANT))
r = subprocess.run([sys.executable, p, WT], capture_output=True, text=True)
os.remove(p); os.rmdir(d)
print(r.stdout, end="")
wrong = [l for l in r.stdout.splitlines() if l.rstrip().endswith("WRONG")]
ok = r.returncode == 1 and len(wrong) == 1 and wrong[0].startswith("closing with the pre-amendment check-l3r5-3")
print("l3n01_mutation: %s (the mutant exits %d; %d row(s) WRONG)" % ("PASS" if ok else "FAIL", r.returncode, len(wrong)))
sys.exit(0 if ok else 1)
