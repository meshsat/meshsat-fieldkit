"""The narrow verification of the targeted fix of layers 1 and 3 applied to the requirements registry (27 September 2026,
MESHSAT-1357, the finalizer, branch fnd/h2). Run from the repository root on the baseline commit 3e4799eb; every edit
asserts the text it replaces, by record id.

The verification is v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md (an AI check of named items, not a qualified
review). It closed layer 1's R2-B1 and R2-m1 and left layer 3's B-1 NOT_CLOSED on one registry difference the header
does not state: when the reviewed attempt landed on main at 79963b3b, its own CURRENT-EVIDENCE re-read on CON-010 and
REQ-044 (bound @6351a72c7966c4b9) was replaced by a rebase note bound @7a834fe55aea6ccd, and on CON-010 that note ends
'it stays INCONCLUSIVE' where the record reads FAIL.

What it writes, and nothing else in the registry:
- baseline_state back to READY_FOR_REVIEW_B, as the header's reversal says; baseline_reviews kept (the records the
  re-baseline names), with a comment saying so;
- a header paragraph on the verification and the reversal;
- S-51 and S-78 back on the open list (their titles with a reopening sentence; S-78 without its closed-state tail);
- S-79's last sentence restated (the baseline it named was reversed; H2 carries layer 3 IN_PROGRESS);
- S-80, the verification's finding, as a new open item (ENGINEERING-QUESTIONS EQ-30);
- S-77's closing evidence gains one sentence: the verification closed R2-B1 and R2-m1 and the brief is BASELINED.
The wording fix the verification gives for S-80 is NOT applied here (the owner's execution prompt, section 4: no
unbounded author and check loop). No record's reading, statement, acceptance, applicability, allocation, verification or
release effect changes, and no session choice or owner ruling changes.
"""
import hashlib, subprocess, textwrap

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
HEAD = "3e4799eb"
CHECK = "v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md"
t = open(P, encoding="utf-8").read()
t0 = t
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == HEAD, head
assert hashlib.sha256(t.encode()).hexdigest()[:16] == "58b77b5d15b2fc7d", "not the registry of %s" % HEAD


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


CHECK16 = sha16(CHECK)
assert CHECK16 == "ae70b1a7811ecea1", CHECK16
assert sha16("v2/docs/PRODUCT-BRIEF.md") == "c1bb3fe5e082b57e"   # the brief the verification read, before its status
assert sha16("v2/docs/CURRENT-EVIDENCE.md") == "7a834fe55aea6ccd"


def comment(s):
    return "\n".join("# " + l for l in textwrap.wrap(s, width=118, break_long_words=False, break_on_hyphens=False)) + "\n"


def folded(s, indent=6):
    return "\n".join(" " * indent + l for l in textwrap.wrap(s, width=120 - indent, break_long_words=False,
                                                              break_on_hyphens=False)) + "\n"


def cut(t, section_start, rid):
    """(i, j): the entry `  - id: rid` from its line to the next entry or the next top-level line."""
    i = t.index("\n  - id: %s\n" % rid, t.index("\n%s:\n" % section_start)) + 1
    ends = [x for x in (t.find("\n  - id: ", i + 5), t.find("\n\n", i)) if x > 0]
    return i, min(ends) + 1


def item(rid, title):
    return "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (rid, folded(title))


before = yaml.safe_load(t)

# 1. the state
a = 'baseline_state: "BASELINED at cecfd0f1"\nbaseline_reviews:\n'
assert t.count(a) == 1
t = t.replace(a, "baseline_state: READY_FOR_REVIEW_B\n"
                 "# baseline_reviews is kept after the reversal of 27 September 2026 (the header's paragraph on the narrow\n"
                 "# verification): the Review B records the re-baseline names, with the record of S-80's re-check.\n"
                 "baseline_reviews:\n")

# 2. the header paragraph
anchor = "#\n# PART NAMES IN STATEMENTS."
assert t.count(anchor) == 1
para = ("THE NARROW VERIFICATION AND THE REVERSAL (27 September 2026, MESHSAT-1357, the finalizer of the targeted fix, "
        "branch fnd/h2). %s (sha256/16 %s; an AI check of named items by a session that wrote none of the lines, not a "
        "qualified review) read this file at %s (sha256/16 58b77b5d15b2fc7d). It confirms the renumbering above as "
        "mechanical and complete and every other difference as typed correctly but one, which the paragraph on the "
        "targeted fix does not state: when the reviewed attempt landed on main at 79963b3b (the rebased eb9f9030), its "
        "own re-read of v2/docs/CURRENT-EVIDENCE.md on CON-010 and REQ-044 (bound to CURRENT-EVIDENCE.md@6351a72c7966c4b9) "
        "was replaced by a note of the rebase bound to @7a834fe55aea6ccd, and on CON-010 that note, the record's newest "
        "evidence entry, ends 'it stays INCONCLUSIVE' where the consolidated re-take moved the reading to FAIL (W3T-F1) "
        "and the record's evidence_result and history read FAIL. Under the reversal above, baseline_state returns to "
        "READY_FOR_REVIEW_B and S-51 and S-78 reopen; baseline_reviews is kept as the records the re-baseline names. The "
        "finding is open item S-80 (ENGINEERING-QUESTIONS EQ-30); its wording fix is not applied in this pass (the "
        "owner's execution prompt, section 4: no unbounded author and check loop). This commit also restates S-79's "
        "last sentence and adds one sentence to S-77's closing evidence (the verification closed layer 1's R2-B1 and "
        "R2-m1). No record's reading, statement, acceptance, applicability, allocation, verification or release "
        "effect changes, and no session choice or owner ruling. Taken by the session under the owner's standing rule "
        "of 26 September 2026." % (CHECK, CHECK16, HEAD))
t = t.replace(anchor, "#\n" + comment(para) + anchor)

# 3. S-51 and S-78 leave the closed list
i, j = cut(t, "closed_items", "S-51")
s51 = t[i:j]
assert s51.startswith("  - id: S-51\n    closed_by: commit cecfd0f1\n")
t = t[:i] + t[j:]
i, j = cut(t, "closed_items", "S-78")
s78 = t[i:j]
assert s78.startswith("  - id: S-78\n    closed_by: commit cecfd0f1\n")
t = t[:i] + t[j:]
t51 = yaml.safe_load(s51)[0]["title"]
t78 = yaml.safe_load(s78)[0]["title"]
assert t51.endswith("and baseline_state set to name the commit it baselines.")
assert t78.endswith("which the record says need a review of their own.")

REOPEN = ("Reopened on 27 September 2026 by the narrow verification of the targeted fix (%s, section 3), under the "
          "reversal the registry header states: " % CHECK)
n51 = t51 + " " + REOPEN + (
    "commit 3e4799eb had closed this item by commit cecfd0f1 on Review B's three records and set baseline_state to "
    "BASELINED at cecfd0f1, and the verification found a registry difference the header does not state (S-80). Open "
    "until S-80 closes; then the re-baseline commit, which files S-80's re-check, closes it again.")
n78 = t78 + " " + REOPEN + (
    "commit 3e4799eb had closed this item on the header's statement of the difference from the reviewed file, and the "
    "verification found one difference that statement misses, the reviewed attempt's own CURRENT-EVIDENCE re-read on "
    "CON-010 and REQ-044 replaced at 79963b3b, with CON-010's newest entry contradicting its FAIL (S-80, "
    "ENGINEERING-QUESTIONS EQ-30). Everything else B-1 asks for is in place (the verification's five other conditions "
    "PASS). Open until S-80 closes and baseline_state names the content commit again, in the commit that files S-80's "
    "re-check. Layer 3 stays IN_PROGRESS.")

a = "  - id: S-52\n"
assert t.count(a) == 1
t = t.replace(a, item("S-51", n51) + a)

# 4. S-79's last sentence, S-78 back before it, S-80 after it
i, j = cut(t, "open_items", "S-79")
s79 = t[i:j]
old79 = yaml.safe_load(s79)[0]["title"]
tail = (" The baseline commit of S-78 exists since the targeted fix of 27 September 2026 (branch fnd/h2: "
        "baseline_state names cecfd0f1); the package is the H2 handover snapshot the handover workflow cuts "
        "next from the pushed commit that carries it.")
assert old79.endswith(tail)
new79 = old79[:-len(tail)] + (
    " The targeted fix of 27 September 2026 wrote that baseline (branch fnd/h2, 3e4799eb: baseline_state BASELINED at "
    "cecfd0f1) and its narrow verification reversed it (S-80), so the H2 handover snapshot the handover workflow cuts "
    "next carries layers 1 and 2 baselined and layer 3 IN_PROGRESS (ENGINEERING-QUESTIONS EQ-29, option (b)); this item "
    "closes with a snapshot cut from the pushed commit that carries the re-baseline.")
s80 = (
    "(Layer 3, the narrow verification of the targeted fix of 27 September 2026 at 3e4799eb, %s, section 3: B-1 "
    "NOT_CLOSED; an AI check, not a qualified review; ENGINEERING-QUESTIONS EQ-30) The registry header's statement of "
    "the difference from the file layer 3's second release check read misses one: when the reviewed attempt landed on "
    "main at 79963b3b (the rebased eb9f9030), its own re-read of v2/docs/CURRENT-EVIDENCE.md on CON-010 and REQ-044, "
    "bound to CURRENT-EVIDENCE.md@6351a72c7966c4b9, was replaced by a note of the rebase bound to @7a834fe55aea6ccd. "
    "On REQ-044 the note is consistent (it stays INCONCLUSIVE). On CON-010 it is not: the note, the record's newest "
    "evidence entry, ends 'this constraint's own reasons are unchanged and it stays INCONCLUSIVE', while the entry of "
    "the consolidated re-take moved the reading from INCONCLUSIVE to FAIL on W3T-F1 (S-64, EQ-25) and the record's "
    "evidence_result and history read FAIL; v2/docs/REQUIREMENTS-TRACE.md shows the contradiction under CON-010. S-78's "
    "closure rested on the header stating the whole difference, so under the header's reversal baseline_state is "
    "READY_FOR_REVIEW_B again and S-51 and S-78 are open. Not fixed by the finalizer that recorded it (the owner's "
    "execution prompt, section 4: no unbounded author and check loop). Open until four steps, wording only, none "
    "changing a statement, acceptance, verification or reading: (1) CON-010's newest entry ends with the record's "
    "actual state, its reasons unchanged and the reading FAIL on W3T-F1, on the file at 7a834fe55aea6ccd; (2) the "
    "header's difference paragraph names 79963b3b's re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on "
    "CON-010 and REQ-044; (3) the trace page re-rendered; (4) a reviewer who wrote neither edit re-checks the two at "
    "one pinned commit, and baseline_state names the content commit again in the commit that files that re-check "
    "(S-51, S-78)." % CHECK)
t = t[:i] + item("S-78", n78) + item("S-79", new79) + item("S-80", s80) + t[j:]

# 5. S-77's closing evidence gains one sentence
i, j = cut(t, "closed_items", "S-77")
s77 = t[i:j]
e77 = yaml.safe_load(s77)[0]["closing_evidence"]
ttl77 = yaml.safe_load(s77)[0]["title"]
assert e77.endswith("If that verification finds the fix incomplete, this item reopens.")
e77n = e77 + (" The narrow verification (%s, sha256/16 %s, an AI check) found R2-B1 and R2-m1 CLOSED at 3e4799eb with no "
              "new contradiction in the lines touched, and the brief is BASELINED in the commit that files it." % (CHECK, CHECK16))
t = t[:i] + ("  - id: S-77\n    closed_by: commit cecfd0f1\n    closing_evidence: >-\n%s    title: >-\n%s"
             % (folded(e77n), folded(ttl77))) + t[j:]

# checks: only the named changes, and the file still parses
assert t != t0
d = yaml.safe_load(t)
assert d["baseline_state"] == "READY_FOR_REVIEW_B"
assert d["baseline_reviews"] == before["baseline_reviews"]
ids_open = [x["id"] for x in d["open_items"]]
ids_closed = [x["id"] for x in d["closed_items"]]
assert {"S-51", "S-78", "S-79", "S-80"} <= set(ids_open) and not ({"S-51", "S-78", "S-80"} & set(ids_closed))
assert "S-77" in ids_closed and "S-77" not in ids_open
assert len(ids_open) == len(set(ids_open)) and len(ids_closed) == len(set(ids_closed))
for k in ("needs", "owner_rulings", "session_choices", "records", "needs_document_sha256", "sources_read_at"):
    assert d[k] == before[k], k
bo = {x["id"]: x for x in before["open_items"]}
for x in d["open_items"]:
    if x["id"] not in ("S-51", "S-78", "S-79", "S-80"): assert x == bo[x["id"]], x["id"]
bc = {x["id"]: x for x in before["closed_items"]}
for x in d["closed_items"]:
    if x["id"] != "S-77": assert x == bc[x["id"]], x["id"]
    else: assert x["title"] == bc["S-77"]["title"] and x["closed_by"] == bc["S-77"]["closed_by"]
open(P, "w", encoding="utf-8").write(t)
print("apply_verification: baseline_state READY_FOR_REVIEW_B; S-51 and S-78 reopened; S-80 added; S-79 restated; "
      "S-77's closing evidence extended; the verification record %s" % CHECK16)
