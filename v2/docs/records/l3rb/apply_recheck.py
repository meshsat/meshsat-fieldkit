"""The re-check of layer 3's re-baseline, filed in the requirements registry (27 September 2026, MESHSAT-1357,
branch fnd/l3rb). Run from the repository root on 2c12be91, the baseline commit the re-check read; every edit asserts
the text it replaces, and the difference it makes is asserted entry by entry after the write.

The re-check (v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md, an AI check of named items by a session that
wrote neither of S-80's edits, filed with one phrase rewritten) finds B-1 CLOSED at 2c12be91, so the reversal in the header's paragraph on the baseline,
again, is not triggered and baseline_state keeps a54b793b. What this writes, and nothing else in the registry:
- baseline_reviews: the re-check record added by sha256/16, with the comment above the list restated;
- a header paragraph on the re-check, after the paragraph on the baseline, again (which is kept as written);
- one sentence appended to the closing evidence of S-51, S-78 and S-80 (closed items; their earlier text kept);
- one sentence appended to S-79's title (an open item): H2 was cut as option (b), and the package is the next snapshot.
Notes, closed items' evidence and an open item move without a review of the baseline (the header's own rule).
"""
import hashlib, subprocess, textwrap

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
BASE = "2c12be91"
REC = "v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md"
t = open(P, encoding="utf-8").read()
t0 = t
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == BASE, head
assert hashlib.sha256(t.encode()).hexdigest()[:16] == "0c87f065a2c9defd", "not the registry of %s" % BASE
REC16 = hashlib.sha256(open(REC, "rb").read()).hexdigest()[:16]
# filed with one phrase rewritten (records/README.md, the re-check section): the checker wrote ab9b3ec1e590a41a
assert REC16 == "7831358b96b6f5ca", REC16


def sub(old, new):
    global t
    assert t.count(old) == 1, "anchor found %d times: %r" % (t.count(old), old[:90])
    assert old != new
    t = t.replace(old, new)


def wrap(text, prefix):
    return "\n".join(textwrap.wrap(" ".join(text.split()), width=120, initial_indent=prefix, subsequent_indent=prefix,
                                   break_long_words=False, break_on_hyphens=False))


def flat(s):
    return " ".join(s.split())


# (1) baseline_reviews: the re-check added, the comment above it restated.
sub("""# baseline_reviews: Review B's three records and the narrow verification of the targeted fix, each an AI review or
# check and never a qualified review (SC-46), named by the re-baseline of 27 September 2026 (the header's paragraph on
# it); no re-check of S-80's two edits by a reviewer who wrote neither is among them.
baseline_reviews:
  - "v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb"
  - "v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md@ae70b1a7811ecea1"
""", wrap("baseline_reviews: Review B's three records, the narrow verification of the targeted fix and the re-check "
          "of S-80's two edits by a reviewer who wrote neither, each an AI review or check and never a qualified review "
          "(SC-46), named by the re-baseline of 27 September 2026 and its re-check (the header's paragraphs on them).",
          "# ") + """
baseline_reviews:
  - "v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md@7a6c679f446b1baa"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md@1c3bc2d99f9efb51"
  - "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md@cf8c73fb288be2fb"
  - "v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md@ae70b1a7811ecea1"
  - "%s@%s"
""" % (REC, REC16))

# (2) The header paragraph on the re-check, after the paragraph on the baseline, again.
PARA = wrap(
    "THE RE-CHECK OF THE BASELINE (27 September 2026, branch fnd/l3rb, MESHSAT-1357). The re-check S-80's fourth step "
    "names was held after the baseline, at 2c12be91, by one session that wrote neither edit, took no part in the fix "
    "or the baseline and held no earlier check: %s (sha256/16 %s, an AI check of named items, never a qualified review, "
    "SC-46), filed in the commit that carries this paragraph with one phrase rewritten (the trailer's name in its last "
    "observation, which the repository's pre-commit check refuses on any added line; the checker's own file had "
    "sha256/16 ab9b3ec1e590a41a, both hashes in v2/docs/records/README.md). It finds B-1 CLOSED: CON-010's newest "
    "evidence entry reads FAIL on W3T-F1 in agreement with its evidence_result and history; the paragraph on the "
    "targeted fix names 79963b3b's re-take on CON-010 and REQ-044; the trace page is re-rendered and current; "
    "baseline_state names a commit on the branch and baseline_reviews four records whose hashes match; S-51, S-78 and "
    "S-80 are closed with evidence; and its own entry-by-entry comparison, comment lines included, finds no registry "
    "difference from ef144760 or 3e4799eb that the paragraphs above do not state. So the reversal in the paragraph "
    "above is not triggered and baseline_state keeps a54b793b. By v2/docs/records/l3rb/apply_recheck.py (asserted "
    "anchors, run on 2c12be91) this commit adds the record to baseline_reviews, appends one sentence to the closing "
    "evidence of S-51, S-78 and S-80 and one to S-79's title (the package is the next snapshot, H3), and changes "
    "nothing else; these are notes, closed items' evidence and an open item, which move without a review of the "
    "baseline. The sentences above that say no such re-check was held describe the registry at 2c12be91 and are kept "
    "as written. Taken by the session under the owner's standing rule of 26 September 2026." % (REC, REC16), "# ")
sub("""# allocation, verification or release effect is a change to the baseline and needs its own review; readings, notes and
# open items move without one.
#
# PART NAMES IN STATEMENTS.""", """# allocation, verification or release effect is a change to the baseline and needs its own review; readings, notes and
# open items move without one.
#
""" + PARA + """
#
# PART NAMES IN STATEMENTS.""")

# (3) One sentence appended to three closed items' evidence and to S-79's title.
HELD = ("Held after this closure: the re-check of S-80's two edits by a reviewer who wrote neither, at 2c12be91 "
        "(%s, sha256/16 %s, an AI check, never a qualified review), finds B-1 CLOSED, neither edit short of the "
        "verification's section 3 and no registry difference the header does not state, so this item stays closed; "
        "the record is in baseline_reviews since the commit that files it." % (REC, REC16))
S79 = ("H2 was cut as option (b), carrying layer 3 IN_PROGRESS. The re-baseline (a54b793b, baselined in 2c12be91) and "
       "its re-check (%s, B-1 CLOSED) are on branch fnd/l3rb; the package is the next snapshot, H3, cut from the pushed "
       "commit that carries them, and this item closes with it." % REC)


def append_block(item, key, sentence, last_line_tail):
    """Append `sentence` to the folded block `key` of `item` and re-wrap the block; the earlier words are kept."""
    global t
    start = "  - id: %s\n" % item
    assert t.count(start) == 1, item
    i = t.index(start)
    j = t.index("\n  - id: ", i + 1) + 1
    entry = t[i:j]
    lines = entry.split("\n")
    k = lines.index("    %s: >-" % key)
    m = k + 1
    while m < len(lines) and lines[m].startswith("      "):
        m += 1
    body = lines[k + 1:m]
    assert flat(" ".join(body)).endswith(last_line_tail), (item, flat(" ".join(body))[-120:])
    new_body = wrap(" ".join(l.strip() for l in body) + " " + sentence, "      ").split("\n")
    assert flat(" ".join(new_body)) == flat(" ".join(body)) + " " + flat(sentence)
    new_entry = "\n".join(lines[:k + 1] + new_body + lines[m:])
    assert new_entry != entry
    t = t[:i] + new_entry + t[j:]


append_block("S-51", "closing_evidence", HELD, "or a registry difference the header does not state, this item reopens.")
append_block("S-78", "closing_evidence", HELD, "returns to READY_FOR_REVIEW_B and this item, S-51 and S-80 reopen.")
append_block("S-80", "closing_evidence", HELD, "S-78 are closed since the commit that closes this item.")
append_block("S-79", "title", S79, "this item closes with a snapshot cut from the pushed commit that carries the re-baseline.")

# (4) The difference, asserted entry by entry.
a, b = yaml.safe_load(t0), yaml.safe_load(t)
assert set(a) == set(b)
for key in a:
    if key in ("baseline_reviews", "open_items", "closed_items"):
        continue
    assert a[key] == b[key], key
assert b["baseline_state"] == "BASELINED at a54b793b"
assert b["baseline_reviews"] == a["baseline_reviews"] + ["%s@%s" % (REC, REC16)]


def by_id(lst):
    return {e["id"]: e for e in lst}


for sect, changed in (("open_items", {"S-79": "title"}),
                      ("closed_items", {"S-51": "closing_evidence", "S-78": "closing_evidence",
                                        "S-80": "closing_evidence"})):
    oa, ob = by_id(a[sect]), by_id(b[sect])
    assert [e["id"] for e in a[sect]] == [e["id"] for e in b[sect]], sect
    for i_, ea in oa.items():
        eb = ob[i_]
        assert set(ea) == set(eb), i_
        for f in ea:
            if changed.get(i_) == f:
                assert flat(eb[f]).startswith(flat(ea[f]) + " ") and flat(eb[f]) != flat(ea[f]), (i_, f)
            else:
                assert ea[f] == eb[f], (i_, f)
ca = [l for l in t0.split("\n") if l.startswith("#")]
cb = [l for l in t.split("\n") if l.startswith("#")]
removed = [l for l in ca if l not in cb]
added = [l for l in cb if l not in ca]
assert all("baseline_reviews" in l or "check and never a qualified review (SC-46), named by the re-baseline" in l
           or "it); no re-check of S-80's two edits" in l for l in removed), removed
assert t != t0
open(P, "w", encoding="utf-8").write(t)
print("comment lines removed %d, added %d" % (len(removed), len(added)))
print("records %d, all equal; baseline_reviews %d; changed: S-79 title, S-51 S-78 S-80 closing_evidence"
      % (len(b["records"]), len(b["baseline_reviews"])))
print("wrote %s, sha256/16 %s" % (P, hashlib.sha256(t.encode()).hexdigest()[:16]))
print("ALL ASSERTIONS HOLD")
