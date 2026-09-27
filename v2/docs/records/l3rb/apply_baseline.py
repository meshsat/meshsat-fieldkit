"""The re-baseline of layer 3 applied to the requirements registry (27 September 2026, MESHSAT-1357, branch fnd/l3rb).
Run from the repository root on a54b793b, the commit that carries S-80's wording fix (apply_fix.py); every edit asserts
the text it replaces.

What it writes, and nothing else in the registry:
- baseline_state "BASELINED at a54b793b";
- baseline_reviews: Review B's three records and the narrow verification of the targeted fix, each by sha256/16, with
  the comment above them restated;
- a header paragraph on the baseline, the session's reason for taking it without S-80's fourth step, and its reversal;
- S-51, S-78 and S-80 moved from the open to the closed items, closed by commit a54b793b with their evidence; their
  titles keep their definitions and reopening history and drop the sentences that said when they would close.
The difference this makes is computed entry by entry by rebaseline_difference.py (its output rebaseline_difference.out).
"""
import hashlib, subprocess, textwrap

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
FIX = "a54b793b"
t = open(P, encoding="utf-8").read()
t0 = t
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == FIX, head
assert hashlib.sha256(t.encode()).hexdigest()[:16] == "c8fded5cb0a165d6", "not the registry of %s" % FIX


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


REVIEWS = ["v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md", "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md",
           "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md",
           "v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md"]
H = [sha16(p) for p in REVIEWS]
assert H == ["7a6c679f446b1baa", "1c3bc2d99f9efb51", "cf8c73fb288be2fb", "ae70b1a7811ecea1"], H
TRACE_AT_FIX = hashlib.sha256(subprocess.run(["git", "show", "%s:v2/docs/REQUIREMENTS-TRACE.md" % FIX],
                                             capture_output=True, check=True).stdout).hexdigest()[:16]
assert TRACE_AT_FIX == "285612fedd4cf81d", TRACE_AT_FIX


def sub(old, new):
    global t
    assert t.count(old) == 1, "anchor found %d times: %r" % (t.count(old), old[:90])
    assert old != new
    t = t.replace(old, new)


def cut(start, end):
    """Remove the block from `start` (inclusive) up to `end` (exclusive) and return it."""
    global t
    assert t.count(start) == 1 and t.count(end) == 1
    i, j = t.index(start), t.index(end)
    assert i < j
    block = t[i:j]
    t = t[:i] + t[j:]
    return block


def reflow(lines, prefix):
    """Re-wrap a run of lines that share `prefix` to 120 columns; the words are unchanged."""
    words = " ".join(l[len(prefix):] for l in lines).split()
    return textwrap.wrap(" ".join(words), width=120, initial_indent=prefix, subsequent_indent=prefix,
                         break_long_words=False, break_on_hyphens=False)


def reflow_block(text, start, prefix):
    """Re-wrap the run of `prefix` lines that begins at the line starting with `start`."""
    ls = text.split("\n")
    i = [k for k, l in enumerate(ls) if l.startswith(start)]
    assert len(i) == 1, start
    j = i[0]
    while j < len(ls) and ls[j].startswith(prefix) and ls[j].strip() not in ("#",):
        j += 1
    new = reflow(ls[i[0]:j], prefix)
    assert " ".join(l[len(prefix):] for l in new).split() == " ".join(l[len(prefix):] for l in ls[i[0]:j]).split()
    return "\n".join(ls[:i[0]] + new + ls[j:])


# (1) baseline_state and baseline_reviews.
sub("""baseline_state: READY_FOR_REVIEW_B
# baseline_reviews is kept after the reversal of 27 September 2026 (the header's paragraph on the narrow
# verification): the Review B records the re-baseline names, with the record of S-80's re-check.
baseline_reviews:
  - "v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb"
""", """baseline_state: "BASELINED at a54b793b"
# baseline_reviews: Review B's three records and the narrow verification of the targeted fix, each an AI review or
# check and never a qualified review (SC-46), named by the re-baseline of 27 September 2026 (the header's paragraph on
# it); no re-check of S-80's two edits by a reviewer who wrote neither is among them.
baseline_reviews:
  - "v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb"
  - "v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md@ae70b1a7811ecea1"
""")

# (2) The header paragraph on the baseline.
sub("""# under the owner's standing rule of 26 September 2026.
#
# PART NAMES IN STATEMENTS.""", """# under the owner's standing rule of 26 September 2026.
#
# THE BASELINE, AGAIN (27 September 2026, the commit after S-80's wording fix, branch fnd/l3rb, MESHSAT-1357).
# baseline_state names a54b793b, the commit that carries the content Review B's records read, with the differences the
# paragraph on the targeted fix states (79963b3b's re-take now among them) and S-80's two wording edits.
# v2/docs/records/l3rb/rebaseline_difference.py compares this file entry by entry at 3e4799eb (the file the narrow
# verification read), ef144760, a54b793b and this commit, comment lines included; its output
# rebaseline_difference.out (its sha256 in v2/docs/records/README.md) finds from ef144760 only CON-010's newest evidence
# entry changed at its end, S-81 added and header lines, then only baseline_state, baseline_reviews, S-51, S-78 and S-80
# moved to the closed items and header lines, and from 3e4799eb no record's kind, statement, acceptance,
# applicability, allocation, verification, status, evidence_result or release effect changed. baseline_reviews names
# Review B's three records and the narrow verification (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md,
# sha256/16 ae70b1a7811ecea1), each by sha256/16; each is an AI review or check, never a qualified review (SC-46). S-51, S-78 and S-80 are closed by
# a54b793b. S-80's fourth step named a re-check of the two edits by a reviewer who wrote neither, filed in the baseline
# commit; the session took the re-baseline without it, on the entry-by-entry difference above and the verification's
# own finding that everything else B-1 asks for is in place, because the owner's execution prompt, section 4, bounds
# the loop at two attempts, a targeted fix and a narrow verification (no unbounded author and check loop), and the two
# edits are wording the verification itself wrote out. Taken by the session under the owner's standing rule of 26
# September 2026, not by the owner. Reverse: if a re-check of the two edits by a reviewer who wrote neither finds
# either short of the verification's section 3, or finds a registry difference the paragraphs above do not state,
# baseline_state returns to READY_FOR_REVIEW_B and S-51, S-78 and S-80 reopen. A later change to a record's statement,
# acceptance, applicability, allocation, verification or release effect is a change to the baseline and needs its own
# review; readings, notes and open items move without one.
#
# PART NAMES IN STATEMENTS.""")

t = reflow_block(t, "# THE BASELINE, AGAIN (27 September 2026", "# ")

# (3) S-51, S-78 and S-80 leave the open list.
s51 = cut("  - id: S-51\n", "  - id: S-52\n")
s78 = cut("  - id: S-78\n", "  - id: S-79\n")
s80 = cut("  - id: S-80\n", "  - id: S-81\n")
def flat(s):
    return " ".join(s.split())


assert "Open until S-80 closes; then the re-baseline commit" in flat(s51)
assert "Open until S-80 closes and baseline_state names the content commit again" in flat(s78)
assert "Open until four steps, wording only" in flat(s80)

CLOSED = """  - id: S-51
    closed_by: commit a54b793b
    closing_evidence: >-
      v2/ecad/tools/pcb_requirements.yaml at commit a54b793b (sha256/16 c8fded5cb0a165d6) carries S-80's wording fix,
      and since the commit that closes this item baseline_state names a54b793b and baseline_reviews names Review B's three
      records, v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md (7a6c679f446b1baa), its re-check
      v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md (1c3bc2d99f9efb51) and the fresh confirmation
      v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md (cf8c73fb288be2fb), with the narrow verification
      v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md (ae70b1a7811ecea1), which found every condition of B-1 in
      place but the one difference S-80 fixes; each an AI review or check (SC-46), never a qualified review. Closed by
      the session under the owner's standing rule of 26 September 2026 without the re-check of the two edits S-80's
      fourth step names (the header's paragraph on the baseline, again, says why); if such a re-check finds either
      edit short of the verification's section 3, or a registry difference the header does not state, this item
      reopens.
    title: >-
      Review B held as SC-46 defines it (an AI review by one fresh reviewer, never a qualified review), recorded as
      v2/docs/reviews/REVIEW-B-LAYER-3-<date>.md, its findings answered, and baseline_state set to name the commit it
      baselines. Reopened on 27 September 2026 by the narrow verification of the targeted fix
      (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md, section 3), under the reversal the registry header
      states: commit 3e4799eb had closed this item by commit cecfd0f1 on Review B's three records and set baseline_state
      to BASELINED at cecfd0f1, and the verification found a registry difference the header does not state (S-80).
  - id: S-78
    closed_by: commit a54b793b
    closing_evidence: >-
      v2/ecad/tools/pcb_requirements.yaml at commit a54b793b (sha256/16 c8fded5cb0a165d6): its header's paragraph on
      the targeted fix states the difference from the file v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md read,
      now with 79963b3b's re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010 and REQ-044, and
      CON-010's newest evidence entry agrees with its FAIL; the rest of that difference is as the narrow verification
      found it (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md section 3: the renumbering mechanical and
      complete, every other difference typed correctly); v2/docs/records/l3rb/rebaseline_difference.out (its sha256
      in v2/docs/records/README.md) finds nothing else changed since the file that verification read and no record's kind, statement,
      acceptance, applicability, allocation, verification, status, evidence_result or release effect changed from it;
      v2/docs/REQUIREMENTS-TRACE.md at a54b793b (285612fedd4cf81d) is re-rendered. baseline_state names a54b793b and
      S-51 is closed since the commit that closes this item, which re-renders the trace page again. Closed by the
      session under the owner's standing rule of 26 September 2026 without the re-check S-80's fourth step names; if
      such a re-check finds a difference the header does not state, baseline_state returns to READY_FOR_REVIEW_B and
      this item, S-51 and S-80 reopen.
    title: >-
      (Layer 3, the second release check of 27 September 2026 at eb9f9030,
      v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md, finding B-1, acceptance item 3.14; left open by the
      release finalizer, the second attempt; ENGINEERING-QUESTIONS EQ-28) baseline_state still reads READY_FOR_REVIEW_B
      and S-51 is open, although that record confirms R2 to R5 of the first release check answered with no finding of
      substance left, on the registry at sha256/16 fb819e939f2895da. Its fix is one commit that sets baseline_state to a
      baselined value naming the commit that carries the reviewed content, closes S-51 on that record, marks the three
      gen_sch_b.py pointers of the choices it read as SC-51 and SC-56 (SC-58 and SC-63 here: :257, :822 and :764-766)
      '(as read at e3aedb25)' or renumbers them to 267 and 464, 978 and 903 to 905, re-renders the trace page and
      updates the layer 3 integrator line, with no other registry change. Since the review the branch was rebased onto
      main 391d8579 and then 91894cd7: the registry at its head also carries set 5's records (SC-51 to SC-57, S-64 to
      S-76 and their readings) and the consolidated re-take's re-read notes (8ea7867e to 91894cd7), the reviewed SC-51
      to SC-56 are SC-58 to SC-63 and EQ-25 is EQ-26, and S-77, S-78 and S-79 are added, which the record says need a
      review of their own. Reopened on 27 September 2026 by the narrow verification of the targeted fix
      (v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md, section 3), under the reversal the registry header
      states: commit 3e4799eb had closed this item on the header's statement of the difference from the reviewed file,
      and the verification found one difference that statement misses, the reviewed attempt's own CURRENT-EVIDENCE
      re-read on CON-010 and REQ-044 replaced at 79963b3b, with CON-010's newest entry contradicting its FAIL (S-80,
      ENGINEERING-QUESTIONS EQ-30). Everything else B-1 asks for is in place (the verification's five other conditions
      PASS).
  - id: S-80
    closed_by: commit a54b793b
    closing_evidence: >-
      Steps (1) to (3) in commit a54b793b, read in the files: in v2/ecad/tools/pcb_requirements.yaml (sha256/16
      c8fded5cb0a165d6) CON-010's newest evidence entry reads 'it stays FAIL on W3T-F1 (S-64, EQ-25), on the file at
      7a834fe55aea6ccd' at its end, followed by the mark of its correction, and its evidence_result and history read FAIL; the header's paragraph
      on the targeted fix names 79963b3b's re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on CON-010
      and REQ-044; v2/docs/REQUIREMENTS-TRACE.md at a54b793b (285612fedd4cf81d) is current and shows CON-010's entry
      ending FAIL. v2/docs/records/l3rb/apply_fix.py asserts each anchor it replaced, and
      v2/docs/records/l3rb/rebaseline_difference.out (its sha256 in v2/docs/records/README.md) finds only those edits
      and S-81 changed from ef144760. v2/docs/CURRENT-EVIDENCE.md did not move (7a834fe55aea6ccd, after claims_check was re-taken on
      a54b793b and rules_status ran three times), so CON-010 and REQ-044 stay bound to it. Step (4), the re-check by
      a reviewer who wrote neither edit, was not held: the session re-baselined without it under the owner's standing
      rule of 26 September 2026 and the bound of his execution prompt, section 4 (the header's paragraph on the
      baseline, again), and the reopen rule stated there stands in its place. baseline_state names a54b793b and S-51
      and S-78 are closed since the commit that closes this item.
    title: >-
      (Layer 3, the narrow verification of the targeted fix of 27 September 2026 at 3e4799eb,
      v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md, section 3: B-1 NOT_CLOSED; an AI check, not a qualified
      review; ENGINEERING-QUESTIONS EQ-30) The registry header's statement of the difference from the file layer 3's
      second release check read misses one: when the reviewed attempt landed on main at 79963b3b (the rebased eb9f9030),
      its own re-read of v2/docs/CURRENT-EVIDENCE.md on CON-010 and REQ-044, bound to
      CURRENT-EVIDENCE.md@6351a72c7966c4b9, was replaced by a note of the rebase bound to @7a834fe55aea6ccd. On REQ-044
      the note is consistent (it stays INCONCLUSIVE). On CON-010 it is not: the note, the record's newest evidence
      entry, ends 'this constraint's own reasons are unchanged and it stays INCONCLUSIVE', while the entry of the
      consolidated re-take moved the reading from INCONCLUSIVE to FAIL on W3T-F1 (S-64, EQ-25) and the record's
      evidence_result and history read FAIL; v2/docs/REQUIREMENTS-TRACE.md shows the contradiction under CON-010. S-78's
      closure rested on the header stating the whole difference, so under the header's reversal baseline_state is
      READY_FOR_REVIEW_B again and S-51 and S-78 are open. Not fixed by the finalizer that recorded it (the owner's
      execution prompt, section 4: no unbounded author and check loop). The fix it names, in four steps, wording only,
      none changing a statement, acceptance, verification or reading: (1) CON-010's newest entry ends with the record's
      actual state, its reasons unchanged and the reading FAIL on W3T-F1, on the file at 7a834fe55aea6ccd; (2) the
      header's difference paragraph names 79963b3b's re-take of the reviewed attempt's own CURRENT-EVIDENCE re-read on
      CON-010 and REQ-044; (3) the trace page re-rendered; (4) a reviewer who wrote neither edit re-checks the two at
      one pinned commit, and baseline_state names the content commit again in the commit that files that re-check (S-51,
      S-78).
"""

_c = CLOSED.split("\n")
_out, k = [], 0
while k < len(_c):
    _out.append(_c[k])
    if _c[k] == "    closing_evidence: >-":
        j = k + 1
        while _c[j].startswith("      "): j += 1
        _out += reflow(_c[k + 1:j], "      ")
        k = j
        continue
    k += 1
CLOSED = "\n".join(_out)

# the reviewed titles are kept word for word up to the sentence that said when each would close
assert flat(s51).split("title: >- ")[1].split(" Open until S-80 closes;")[0] in flat(CLOSED)
assert flat(s78).split("title: >- ")[1].split(" Open until S-80 closes and")[0] in flat(CLOSED)
_s80 = flat(s80).split("title: >- ")[1]
assert _s80.replace("Open until four steps, wording only,", "The fix it names, in four steps, wording only,") in flat(CLOSED)

# S-77 stays as it is; the three closed items go after it, before L-02
i = t.index("  - id: L-02\n    closed_by: SC-21\n")
assert t.count("  - id: L-02\n    closed_by: SC-21\n") == 1
t = t[:i] + CLOSED + t[i:]

d = yaml.safe_load(t)
assert d["baseline_state"] == "BASELINED at a54b793b"
assert len(d["baseline_reviews"]) == 4
op = [o["id"] for o in d["open_items"]]
cl = {c["id"]: c for c in d["closed_items"]}
assert not {"S-51", "S-78", "S-80"} & set(op) and "S-81" in op
assert all(cl[x]["closed_by"] == "commit a54b793b" for x in ("S-51", "S-78", "S-80"))
assert t != t0
open(P, "w", encoding="utf-8").write(t)
print("wrote %s, sha256/16 %s" % (P, hashlib.sha256(t.encode()).hexdigest()[:16]))
