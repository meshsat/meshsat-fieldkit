accepted: no

# Layer 3 amendment: the targeted recheck by the engineering collaborator (an AI review, read-only; the one follow-up)

Collaborator job `cx12-l3am-recheck`, run `20261001T003321Z-1017926`, model `gpt-6-astra` at effort `xhigh` (the client's
own record), on branch fnd/l3am at commit `932e0f7f0419`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

AMENDMENT: NOT YET. Read-only AI review completed. B1 still includes closure progress in the requirements digest. B2's pre-amendment-check reuse defect is corrected, with minor discrepancies noted below. Scope passes. B1 prevents filing this result as accepted: yes.

## Blocking discrepancies

- B1, IMPLEMENTATION_DEFECT: closure progress remains IN. render_l3r2.py:471 hashes records[].status, including FEASIBILITY_OPEN/CLOSED, and :476 hashes holds_layout_entry. For FEA-003, pcb_requirements.yaml:6160 currently holds [b]; rules_lib.py:1124 to :1131 requires a legitimate layout-stage closure to set status CLOSED, supply closed_by and clear holds_layout_entry. The demands in stages[].requires/needs/holds can remain identical, yet the requirements digest changes. Stage closed_by is also unclassified and therefore included by _keep at render_l3r2.py:501. test_l3am.py:177 misses this because it changes only status to the invalid value MET. Exclude the derived hold summary and stage closure evidence, handle feasibility closure status separately from normative status, and replace that positive fixture with a schema-valid closure update.

## Classification

- **IMPLEMENTATION_DEFECT**: B1 closure progress included in the requirements binding Evidence: render_l3r2.py:471, :476 and :501; pcb_requirements.yaml:6160; rules_lib.py:1124 to :1131; test_l3am.py:177.
- **IMPLEMENTATION_DEFECT**: B2 literal first-line format Evidence: MINOR: apply_l3am_findings_closed.py:83 accepts surrounding whitespace despite the exact format stated at :10.
- **IMPLEMENTATION_DEFECT**: B2 amendment test-file binding coverage Evidence: MINOR: l3amlib.py:29 omits the changed test_l3r5.py from the files compared by apply_l3am_findings_closed.py:104.

## Smallest next action

Correct only the B1 treatment of derived closure fields and its positive fixture: exclude stage closed_by and derived holds_layout_entry, and normalize or exclude feasibility closure status while retaining normative status distinctions.

## Closure criterion

A schema-valid stage closure, including CLOSED, closed_by and the required hold-summary update, and a feasibility closure leave the requirements digest and bound acceptance unchanged when demands are unchanged. All eight existing normative mutations still invalidate acceptance for a requirements mismatch. Preserve B2's refusals and the previously passing scope.

## Owner decision required

no

## Checks

- Revision and scope: PASS. HEAD matches the specified base commit and the worktree is clean. The ten changed files contain B1/B2 fixes, their tests, supporting documentation and the first check record. The registry and previously passing L3-R01, L3-R02 and L3-R05 content are unchanged.
- B1 field coverage and classification: FAIL. All current fields at the five classified levels are named with reasons: 16 top-level, 18 ruling, 16 choice, 46 record and 5 stage fields. Needs contain id and statement, both projected. The previously omitted authority, accepted risks and stage conditions are included. However, render_l3r2.py:471 includes feasibility closure status, and :476 includes holds_layout_entry, which rules_lib.py:1128 requires to become empty when LAYOUT_ENTRY closes. These progress changes alter the digest without changing the stage's demands.
- B1 listed mutation cases: PASS. Each of the eight listed normative mutations reaches a requirements-manifest mismatch: D-11, a choice answer, CON-012's exception, stage requires/needs/holds, record rulings and an added ruling. Each listed observation leaves the digest unchanged: evidence, notes, history, stage status, open-item closure, waits_on, resolved_by, satisfied_by and ruling source; acceptance history is also excluded. This does not establish a valid stage-closure positive: :177 uses status MET, whereas rules_lib.py:1124 permits only OPEN/CLOSED.
- B2 closure and acceptance verification: PASS. apply_l3am_findings_closed.py:76 verifies filed hashes and verdicts; :80 requires the newest entry; :84 requires amendment scope; :86 requires a 40-hex revision; :89 checks commit existence and :90 ancestry. Lines 92 to 96 reject every one of the eight pre-amendment check paths or basenames. Lines 98 to 108 compare projected requirements, brief, change record, policy and AMENDMENT_FILES. Lines 123 to 125 restrict closure changes to checked_by/state/status. apply_l3r5_accept.py:116 invokes the same verifier against the accepted revision. Minor format and binding-coverage discrepancies are recorded in evidence.
- B2 listed refusal cases: PASS. By inspection, each listed refusal reaches its stated boundary. Existing check-l3r5-3 fails amendment scope; a correctly formatted fixture using its basename fails the historical-check exclusion; accepted:no filed ACCEPTED fails verdict verification; wrong scope fails line 85; zero revision fails commit existence; the root-parented fixture fails ancestry; changed test_l3am.py fails content comparison; repeated closure fails the OPEN-state check. Acceptance refuses OPEN findings, hand-closed findings naming the old check, a nonexistent revision, a revision lacking the copy's policy content, empty supersession and repeated acceptance. The changed l3r5 tests retain missing-file, missing-newest-evidence and unmet-gate refusals. Positive fixtures cover the reviewed tip and acceptance at its descendant.
- Executable verification: NOT_RUN. No tests, gates, renderers, verdict writers, closing scripts or acceptance scripts were run. No runtime test result is claimed.

## Evidence and minors

- MINOR: apply_l3am_findings_closed.py:83 strips whitespace from the first line, so the documented exact header is not enforced literally. Compare the unstripped line and add a padded-header refusal fixture; the exact required header should remain accepted.
- MINOR: l3amlib.py:29 omits v2/ecad/tools/tests/test_l3r5.py from AMENDMENT_FILES although this recheck's diff changes its acceptance tests. A later change confined to that test file escapes the amendment-byte comparison. Add it to the list and extend the changed-file refusal fixture.
- The first check's passing dispositions remain preserved. This recheck does not reopen L3-R01, L3-R02 or L3-R05, or establish the coordinator's separate L3-R03 export reproduction.
