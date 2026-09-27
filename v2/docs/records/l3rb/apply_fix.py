"""S-80's wording fix applied to the requirements registry (27 September 2026, MESHSAT-1357, the re-baseline of layer 3,
branch fnd/l3rb from main ef144760). Run from the repository root on ef144760; every edit asserts the text it replaces.

The narrow verification of the targeted fix of layers 1 and 3 (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md,
an AI check, not a qualified review) left layer 3's B-1 NOT_CLOSED on one registry difference the header does not state,
and gave the fix in its section 3 (open item S-80). This script applies exactly that fix and nothing else of B-1:
- CON-010's newest evidence entry (the CURRENT-EVIDENCE.md re-read of 79963b3b) ends with the record's actual state:
  its reasons unchanged, it stays FAIL on W3T-F1, on the file at 7a834fe55aea6ccd;
- the header's paragraph on the targeted fix (its statement of the difference from the reviewed file) names 79963b3b's
  re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010 and REQ-044;
- a header paragraph on this pass.
Separately, the verification's observation (c) (its section 4: the brief's FEA-002 row and W3T-F1) was checked against
v2/docs/PRODUCT-BRIEF.md, which is layer 1's and is not edited here; what the check found is added as open item S-81 for
layer 1's writer. The trace page is re-rendered afterwards by rules_render.py --requirements. No record's
evidence_result, statement, acceptance, applicability, allocation, verification or release effect changes, and no
session choice or owner ruling. The commit after the one this script's output goes into writes baseline_state
(apply_baseline.py).
"""
import hashlib, subprocess

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
BASE = "ef144760"
t = open(P, encoding="utf-8").read()
t0 = t
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == BASE, head
assert hashlib.sha256(t.encode()).hexdigest()[:16] == "9a3aed63341c8eaa", "not the registry of %s" % BASE


def sub(old, new):
    global t
    assert t.count(old) == 1, "anchor found %d times: %r" % (t.count(old), old[:90])
    assert old != new
    t = t.replace(old, new)


# (1) CON-010's newest evidence entry.
sub("""          class and cause read above, so this constraint's own reasons are unchanged and it stays INCONCLUSIVE, on the
          file at 7a834fe55aea6ccd
    evidence_bound_to:""",
    """          class and cause read above, so this constraint's own reasons are unchanged and it stays FAIL on W3T-F1 (S-64,
          EQ-25), on the file at 7a834fe55aea6ccd (corrected at the re-baseline of layer 3 on 27 September 2026, S-80:
          this entry had ended 'it stays INCONCLUSIVE', against the consolidated re-take's FAIL above)
    evidence_bound_to:""")

# (2) The header's difference paragraph names 79963b3b's re-take.
sub("""# notes (8ea7867e to 91894cd7, CON-010 read FAIL there), the release finalizer's S-77 to S-79 with the needs pin
# re-taken on CONOPS's status line and the three readings bound to CONOPS rebound on it (62f26a44), and this fix: the
# three gen_sch_b.py pointers""",
    """# notes (8ea7867e to 91894cd7, CON-010 read FAIL there), 79963b3b's re-take of the reviewed attempt's own re-read of
# v2/docs/CURRENT-EVIDENCE.md on CON-010 and REQ-044 (79963b3b is the reviewed eb9f9030 as it landed on main: the
# reviewed note, bound to CURRENT-EVIDENCE.md@6351a72c7966c4b9, was replaced by a note of the rebase onto 91894cd7,
# bound to @7a834fe55aea6ccd; on CON-010 that note ended 'it stays INCONCLUSIVE' where the record reads FAIL, which the
# re-baseline below corrects; this clause was added by that re-baseline, S-80), the release finalizer's S-77 to S-79
# with the needs pin re-taken on CONOPS's status line and the three readings bound to CONOPS rebound on it (62f26a44),
# and this fix: the three gen_sch_b.py pointers""")

# (3) A header paragraph on this pass.
sub("""# PART NAMES IN STATEMENTS. A part a statement names""",
    """# THE RE-BASELINE OF LAYER 3 (27 September 2026, MESHSAT-1357, branch fnd/l3rb from main ef144760). S-80's wording
# fix, exactly as the narrow verification gives it in its section 3, by v2/docs/records/l3rb/apply_fix.py (asserted
# anchors): CON-010's newest evidence entry, the CURRENT-EVIDENCE.md re-read of 79963b3b, ends with the record's actual
# state (its reasons unchanged, it stays FAIL on W3T-F1, on the file at 7a834fe55aea6ccd); the paragraph on the targeted
# fix names 79963b3b's re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010 and REQ-044; and
# v2/docs/REQUIREMENTS-TRACE.md is re-rendered. The verification's observation (c) was checked against
# v2/docs/PRODUCT-BRIEF.md, which is layer 1's and is not edited here, and is recorded as open item S-81 for layer 1's
# writer. No record's evidence_result, statement, acceptance, applicability, allocation, verification or release effect
# changes, and no session choice or owner ruling. The commit after this one writes baseline_state. Taken by the session
# under the owner's standing rule of 26 September 2026.
#
# PART NAMES IN STATEMENTS. A part a statement names""")

# (4) Open item S-81, after S-80.
sub("""      one pinned commit, and baseline_state names the content commit again in the commit that files that re-check (S-51,
      S-78).
  - id: M-02""",
    """      one pinned commit, and baseline_state names the content commit again in the commit that files that re-check (S-51,
      S-78).
  - id: S-81
    class: SESSION
    status: OPEN
    title: >-
      (Layer 1, for the product brief's writer; the narrow verification's observation (c),
      v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md section 4, checked at the re-baseline of layer 3 on 27
      September 2026) v2/docs/PRODUCT-BRIEF.md's open-items row for FEA-002 states EMCON's counts as
      v2/docs/feasibility/EMCON.md section 0a gives them (locally 15 of 17 closed at desk, end to end 0 of 17), and
      W3T-F1 does not move them: it is a finding on the shared TX_INHIBIT_n conductor, which every end-to-end row already
      waits on. The row does not name W3T-F1 (S-64, ENGINEERING-QUESTIONS EQ-25), under which RF-002's fail-safe state
      reads FAIL on boards A to D and CON-010 reads FAIL at desk, and its sentence 'One bound includes failure' names
      only the RockBLOCK 9704's, where W3T-F1's bound on TX_INHIBIT_n's fail-safe level with board C unpowered (about
      0.42 V with the stated II at VCC 0 V, 1.09 V with the stated Ioff, against the 0.8 V VIL the walk applies) also
      includes failure. The row's reason layer 1 can close stands (S-64's remedy is on board C and changes no ruled
      radio, the case or a board-to-board interface), so the session reads this as wording for the brief's next issue
      under its open-items rule, not as a reopening of layer 1. The page the row cites carries W3T-F1 in its section 4b
      only: its section 7 does not list it and its section 3 still reads the line PASS in every fail-safe state, which
      is that page's writer's. Open until the brief's next issue names W3T-F1 in the FEA-002 row and counts the bounds
      that include failure, or S-64 closes before that issue. The brief is not edited by the pass that recorded this.
  - id: M-02""")

yaml.safe_load(t)  # the file still parses
d = yaml.safe_load(t)
con = [r for r in d["records"] if r["id"] == "CON-010"][0]
assert con["evidence_result"] == "FAIL" and "stays FAIL on W3T-F1" in con["evidence"][-1]
assert "S-81" in [o["id"] for o in d["open_items"]]
assert t != t0
open(P, "w", encoding="utf-8").write(t)
print("wrote %s, sha256/16 %s" % (P, hashlib.sha256(t.encode()).hexdigest()[:16]))
