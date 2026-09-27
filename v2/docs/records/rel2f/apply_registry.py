"""The registry half of the release finalizer of layers 1 to 3 (27 September 2026, MESHSAT-1357, branch fnd/rel2 rebased
onto main 391d8579 and then 91894cd7), after the second release check at eb9f9030 (v2/docs/reviews/REVIEW-LAYER-{1,2,3}-RELEASE-2-2026-09-27.md).

This was the second attempt on layers 1 and 3, so no blocking item is fixed a third time (the owner's execution prompt
of 27 September 2026, section 4): each item the second check left is written as an open item here, at the next free
S- number of the file it runs on, and as an engineering question at the next free EQ- number of
v2/docs/handover/ENGINEERING-QUESTIONS.md (written by edit_docs.py from the JSON this script writes, its only argument).
Layer 2's reviewer found no blocking item; its baseline is edit_docs.py's and post_docs_registry.py's. Every edit
asserts its anchor; run from the worktree root. Taken by the session under the owner's standing rule of 26 September
2026; nothing here is the owner's.

  layer 1, R2-B1   the brief's six core feasibility blockers against the registry's seven (FEA-007 missing)
  layer 3, B-1     the baseline not recorded (3.14), and the rebase's registry difference the reviewer did not read
  layer 3, B-2     no versioned package (3.18)
"""
import json, re, sys

P = 'v2/ecad/tools/pcb_requirements.yaml'
EQP = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
t = open(P, encoding='utf-8').read()


def next_free(prefix, text):
    return max(int(m) for m in re.findall(r'\n  - id: %s-(\d{2})\n' % prefix, text)) + 1


def wrap(text, indent=6, width=120):
    words = text.split(); lines = []; cur = ' ' * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = ' ' * indent + w
        else: cur = (cur + ' ' + w) if cur.strip() else cur + w
    lines.append(cur)
    return '\n'.join(lines) + '\n'


def sub(t, a, b):
    assert t.count(a) == 1, (t.count(a), a[:90]); assert a != b
    return t.replace(a, b)


s0 = next_free('S', t)
S1, S2, S3 = ('S-%02d' % (s0 + k) for k in range(3))
eq0 = max(int(x) for x in re.findall(r'^### EQ-(\d{2})\.', open(EQP, encoding='utf-8').read(), re.M)) + 1
E1, E2, E3 = ('EQ-%02d' % (eq0 + k) for k in range(3))
print('apply_registry (rel2f): open items', S1, S2, S3, 'questions', E1, E2, E3)

R1 = 'v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md'
R3 = 'v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md'
ITEMS = [
    (S1, "(Layer 1, the second release check of 27 September 2026 at eb9f9030, %s, finding R2-B1; left open by the "
         "release finalizer because it was the second attempt, the owner's execution prompt section 4; ENGINEERING-QUESTIONS "
         "%s) v2/docs/PRODUCT-BRIEF.md lines 256 to 258 state six feasibility blockers on the core (FEA-001 to FEA-006) where "
         "this registry holds seven kind: feasibility records, every one prototype_1: core and release_effect: BLOCKER: "
         "FEA-007, the kit's fit in the Peli 1450 on the case choices C1 to C6 (core under SC-04), holding the layout entry "
         "of boards A, B, D, E, E5 and P and BLOCKED on the owner's purchase L-07 or his acceptance of the residual, with "
         "bounds that include failure (35 of 70 case margins OPEN; M17g and M17x fail as laid out until the jumper plug is "
         "picked; the pack's M4a and M5 OPEN on the undesigned hold-down S-27), is absent from the brief's open items, and "
         "the brief's D-07 row (line 289) names the board E clamp fit but not the east plug layout (M17g). Open until the "
         "brief carries the reviewer's fix (the sentence naming seven blockers with FEA-007, an open-items row for FEA-007 "
         "with the reason layer 1 can close while it is open, and the east plug layout in the D-07 row), a reviewer who "
         "wrote none of the changed lines re-checks the difference at one pinned commit, and the brief is set BASELINED "
         "in the commit that files that re-check. Wording only: no owner answer, purchase or test is needed. Layer 1 "
         "stays IN_PROGRESS." % (R1, E1)),
    (S2, "(Layer 3, the second release check of 27 September 2026 at eb9f9030, %s, finding B-1, acceptance item 3.14; "
         "left open by the release finalizer, the second attempt; ENGINEERING-QUESTIONS %s) baseline_state still reads "
         "READY_FOR_REVIEW_B and S-51 is open, although that record confirms R2 to R5 of the first release check "
         "answered with no finding of substance left, on the registry at sha256/16 fb819e939f2895da. Its fix is one "
         "commit that sets baseline_state to a baselined value naming the commit that carries the reviewed content, "
         "closes S-51 on that record, marks the three gen_sch_b.py pointers of the choices it read as SC-51 and SC-56 "
         "(SC-58 and SC-63 here: :257, :822 and :764-766) '(as read at e3aedb25)' or renumbers them to 267 and 464, 978 "
         "and 903 to 905, re-renders the trace page and updates the layer 3 integrator line, with no other registry "
         "change. Since the review the branch was rebased onto main 391d8579 and then 91894cd7: the registry at its head also "
         "carries set 5's records (SC-51 to SC-57, S-64 to S-76 and their readings) and the consolidated re-take's "
         "re-read notes (8ea7867e to 91894cd7), the reviewed SC-51 to SC-56 are SC-58 to SC-63 "
         "and EQ-25 is EQ-26, and %s, %s and %s are added, which the record says need a review of their own. Open "
         "until a reviewer who wrote none of it confirms that difference and the baseline commit is made as the "
         "record describes. Layer 3 stays IN_PROGRESS." % (R3, E2, S1, S2, S3)),
    (S3, "(Layer 3, the second release check of 27 September 2026 at eb9f9030, %s, finding B-2, acceptance item 3.18; "
         "ENGINEERING-QUESTIONS %s) No versioned package carries the reviewed registry: the reviewed commit was on no "
         "remote branch (GitLab and GitHub main were at 953f5658 when it was read) and no handover snapshot has been cut "
         "from a commit carrying its content. The anchor 08f3665a is already on the public main, so LAYER-STATUS layer "
         "3's earlier remaining item on it is met. Open until the integrating session pushes the baseline commit of "
         "%s to main and cuts the next handover snapshot from it, its manifest naming that commit; the same snapshot "
         "carries layer 1's item 14 and layer 2's baselined CONOPS." % (R3, E3, S2)),
]

anchor = '  - id: M-02\n    class: OWNER_ACTION\n'
assert t.count(anchor) == 1
i = t.index('\n  - id: S-%02d\n' % (s0 - 1)) + 1
j = t.index('\n  - id: ', i + 5) + 1
assert t[j:].startswith(anchor), t[j:j + 40]
block = ''.join('  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s' % (sid, wrap(title)) for sid, title in ITEMS)
t = t[:j] + block + t[j:]

t = sub(t, """# entered as SC-58 to SC-63 with their draft names, and the validator refusing an SC- id no entry defines (layer 3, R5).
#
# PART NAMES IN STATEMENTS.""", """# entered as SC-58 to SC-63 with their draft names, and the validator refusing an SC- id no entry defines (layer 3, R5).
#
# THE RELEASE FINALIZER OF LAYERS 1 TO 3 (27 September 2026, MESHSAT-1357, after the second release check at eb9f9030,
# v2/docs/reviews/REVIEW-LAYER-{1,2,3}-RELEASE-2-2026-09-27.md; branch fnd/rel2 rebased onto main 391d8579, where set 5
# had taken SC-51 to SC-57 and EQ-25, so the second release attempt's choices are SC-58 to SC-63, and then onto main
# 91894cd7, the consolidated re-take). Through v2/docs/records/rel2f/apply_registry.py: the items the second check left
# on layers 1 and 3, not fixed a third time (the owner's execution prompt, section 4), as %s (layer 1, R2-B1), %s (layer
# 3, B-1, the baseline) and %s (layer 3, B-2, the package); through post_docs_registry.py: the needs pin re-taken on
# CONOPS's status line, which records layer 2 BASELINED, and the three readings bound to CONOPS rebound on that header
# change alone.
#
# PART NAMES IN STATEMENTS.""" % (S1, S2, S3))

open(P, 'w', encoding='utf-8').write(t)
out = {'S': [S1, S2, S3], 'EQ': [E1, E2, E3]}
json.dump(out, open(sys.argv[1], 'w'), indent=1)
print(json.dumps(out))
