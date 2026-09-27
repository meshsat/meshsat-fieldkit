"""The requirements registry baselined (27 September 2026, MESHSAT-1357, the targeted fix of layers 1 and 3, branch
fnd/h2 from main 62f26a44). Run from the repository root on the commit after the targeted fix (cecfd0f1); every edit
asserts the text it replaces, by record id.

What it writes, and nothing else in the registry:
- baseline_state: BASELINED at cecfd0f1, the commit that carries the content Review B's records read (the reviewed
  eb9f9030 as renumbered on main, with the differences the header states and registry_difference.out lists), and
  baseline_reviews naming Review B's three records by sha256/16;
- a header paragraph saying so, with the reversal;
- S-51 (Review B held and baseline_state set) closed by commit cecfd0f1 on those records;
- S-77 (layer 1, R2-B1) closed by commit cecfd0f1 on the brief's three edits;
- S-78 (layer 3, B-1) closed by commit cecfd0f1 on the header's statement of the difference and the baseline written
  here;
- S-79 (layer 3, B-2) kept open, its title saying the H2 snapshot answers it.
"""
import hashlib, subprocess, textwrap

import yaml

P = "v2/ecad/tools/pcb_requirements.yaml"
BASE = "cecfd0f1"
t = open(P, encoding="utf-8").read()
t0 = t
head = subprocess.run(["git", "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
assert head == BASE, head
assert hashlib.sha256(t.encode()).hexdigest()[:16] == "f25e17d7d698ecf8", "not the registry of %s" % BASE


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


REVIEWS = ["v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md", "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md",
           "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md"]
WANT = ["7a6c679f446b1baa", "1c3bc2d99f9efb51", "cf8c73fb288be2fb"]
assert [sha16(p) for p in REVIEWS] == WANT
BRIEF16 = sha16("v2/docs/PRODUCT-BRIEF.md")
assert BRIEF16 == "c1bb3fe5e082b57e"
DIFF16 = sha16("v2/docs/records/h2/registry_difference.out")


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


# 1. the state and the records
a = "baseline_state: READY_FOR_REVIEW_B\n"
assert t.count(a) == 1
t = t.replace(a, 'baseline_state: "BASELINED at %s"\nbaseline_reviews:\n%s' % (
    BASE, "".join('  - "%s@%s"\n' % (p, s) for p, s in zip(REVIEWS, WANT))))

# 2. the header paragraph
anchor = "#\n# PART NAMES IN STATEMENTS."
assert t.count(anchor) == 1
para = ("THE BASELINE (27 September 2026, the commit after the targeted fix, MESHSAT-1357). baseline_state names "
        "cecfd0f1, the commit that carries the content Review B's records read: the reviewed eb9f9030 as it reached main, "
        "renumbered and with the differences the paragraph above states, which "
        "v2/docs/records/h2/registry_difference.py computes entry by entry (its output registry_difference.out, sha256/16 "
        "%s: no record's statement, acceptance, applicability, allocation, verification or release effect differs). "
        "baseline_reviews names Review B's three records by sha256/16 (SC-46: an AI review, never a qualified review): "
        "the first pass, whose findings B1 to B6 were answered and closed; the first release check, its re-check on the "
        "merged registry (R1 to R5); and the second release check, the fresh confirmation R1 asks for (R2 to R5 answered, "
        "no finding of substance left). S-51 is closed by that commit on those records. Taken by the session under the "
        "owner's standing rule of 26 September 2026 and the method change of his execution prompt, section 4 (after two "
        "attempts, a targeted fix and a narrow verification). Reverse: if the narrow verification of the targeted fix "
        "finds a registry difference the paragraph above does not state, baseline_state returns to READY_FOR_REVIEW_B "
        "and S-51 and S-78 reopen. A later change to a record's statement, acceptance, applicability, allocation, "
        "verification or release effect is a change to the baseline and needs its own review; readings, notes and open "
        "items move without one." % DIFF16)
t = t.replace(anchor, "#\n" + comment(para) + anchor)

# 3. the items: S-51, S-77 and S-78 leave the open list, S-79's title gains one sentence
i, j = cut(t, "open_items", "S-51")
s51 = t[i:j]
assert s51.startswith("  - id: S-51\n    class: SESSION\n    status: OPEN\n    title: >-\n")
t = t[:i] + t[j:]
i, j = cut(t, "open_items", "S-77")
s77 = t[i:j]
assert s77.startswith("  - id: S-77\n    class: SESSION\n    status: OPEN\n    title: >-\n")
t = t[:i] + t[j:]
i, j = cut(t, "open_items", "S-78")
s78 = t[i:j]
assert s78.startswith("  - id: S-78\n    class: SESSION\n    status: OPEN\n    title: >-\n")
t = t[:i] + t[j:]

i, j = cut(t, "open_items", "S-79")
s79 = t[i:j]
old79 = yaml.safe_load(s79)[0]["title"]
assert old79.endswith("the same snapshot carries layer 1's item 14 and layer 2's baselined CONOPS.")
new79 = old79 + (" The baseline commit of S-78 exists since the targeted fix of 27 September 2026 (branch fnd/h2: "
                 "baseline_state names cecfd0f1); the package is the H2 handover snapshot the handover workflow cuts "
                 "next from the pushed commit that carries it.")
t = t[:i] + "  - id: S-79\n    class: SESSION\n    status: OPEN\n    title: >-\n" + folded(new79) + t[j:]


def closed(rid, title, evidence):
    return ("  - id: %s\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s"
            % (rid, BASE, folded(evidence), folded(title)))


t51 = yaml.safe_load(s51)[0]["title"]
t77 = yaml.safe_load(s77)[0]["title"]
t78 = yaml.safe_load(s78)[0]["title"]
k77 = t77.index(" Open until the brief carries the reviewer's fix")
k78 = t78.index(" Open until a reviewer who wrote none of it confirms that difference")
e51 = ("v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md (sha256/16 7a6c679f446b1baa, Review B's first pass as SC-46 defines "
       "it; its B1 to B6 answered by the targeted fixer c23 and closed), v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md "
       "(1c3bc2d99f9efb51, its re-check on the merged registry: B1 to B6 closed in substance, R1 to R5 raised) and "
       "v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md (cf8c73fb288be2fb, the fresh confirmation R1 asks for: R2 "
       "to R5 answered at eb9f9030, no finding of substance left, B-1 and B-2 procedural); the registry at commit "
       "cecfd0f1 (sha256/16 f25e17d7d698ecf8) differs from the one that record read only as its header states and "
       "v2/docs/records/h2/registry_difference.out lists. baseline_state names cecfd0f1 and baseline_reviews the three "
       "records since the commit that closes this item.")
e77 = ("v2/docs/PRODUCT-BRIEF.md at commit cecfd0f1 (sha256/16 %s) carries the three edits of "
       "v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md's R2-B1 fix: 'Seven feasibility blockers on the core', "
       "FEA-001 to FEA-007 with FEA-007 core under the session's SC-04; an open-items row for FEA-007 (35 of 70 case "
       "margins OPEN, M17g and M17x failing as laid out, M4a and M5 OPEN on S-27, the layout entry of A, B, D, E, E5 and "
       "P held, the mock-up BLOCKED on L-07 or the owner's acceptance of the residual, why layer 1 can close with it "
       "open and the reissue rule); and the east plug layout (M17g, FEA-007) in the D-07 row. Closed on that targeted "
       "fix under the method change of the owner's execution prompt, section 4 (after two attempts, a targeted fix and "
       "a narrow verification); the narrow verification of those lines by a reviewer who wrote none of them, and the "
       "brief's BASELINED state in the commit that files it, are layer 1's remaining release steps "
       "(v2/docs/handover/LAYER-STATUS.md layer 1, ENGINEERING-QUESTIONS EQ-27). If that verification finds the fix "
       "incomplete, this item reopens." % BRIEF16)
e78 = ("v2/ecad/tools/pcb_requirements.yaml at commit cecfd0f1 (sha256/16 f25e17d7d698ecf8): its header states the "
       "difference from the file v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md read (SC-51 to SC-56 of "
       "eb9f9030 are SC-58 to SC-63 here and EQ-25 is EQ-26, renumbered by the rebase because set 5 had taken those ids; "
       "set 5's entries; the consolidated re-take's re-read notes; S-77 to S-79 and the CONOPS rebinds) and marks n1's "
       "three gen_sch_b.py pointers in SC-58 and SC-63 '(as read at e3aedb25)'; "
       "v2/docs/records/h2/registry_difference.py computes that difference entry by entry and its output "
       "registry_difference.out (sha256/16 %s) finds no record's statement, acceptance, applicability, allocation, "
       "verification or release effect changed and the six renumbered choices identical to the reviewed ones; "
       "baseline_state names cecfd0f1 and S-51 is closed on the three Review B records since the commit that closes "
       "this item, which re-renders v2/docs/REQUIREMENTS-TRACE.md and updates the layer 3 integrator line, and changes "
       "nothing else in the registry but baseline_reviews, the header's paragraph on the baseline, S-77's closing and "
       "S-79's title. The difference is confirmed by the narrow "
       "verification of the targeted fix (the owner's execution prompt, section 4); if it finds a difference the header "
       "does not state, baseline_state returns to READY_FOR_REVIEW_B and this item and S-51 reopen." % DIFF16)
block = (closed("S-51", t51, e51) + closed("S-77", t77[:k77], e77) + closed("S-78", t78[:k78], e78))
a = "  - id: L-02\n    closed_by: SC-21\n"
assert t.count(a) == 1
t = t.replace(a, block + a)

assert t != t0
d = yaml.safe_load(t)
assert d["baseline_state"] == "BASELINED at " + BASE
ids_open = {x["id"] for x in d["open_items"]}
ids_closed = {x["id"] for x in d["closed_items"]}
assert {"S-51", "S-77", "S-78"} <= ids_closed and not ({"S-51", "S-77", "S-78"} & ids_open) and "S-79" in ids_open
open(P, "w", encoding="utf-8").write(t)
print("apply_baseline: baseline_state BASELINED at %s; S-51, S-77 and S-78 closed by commit %s; S-79 kept open" % (BASE, BASE))
