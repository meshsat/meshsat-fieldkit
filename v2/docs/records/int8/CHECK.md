mergeable: yes

Independent check of integration set 7, fnd/int8 at 7f6de345 onto main 6b419b02 (an AI review, not a qualified
review; 28 September 2026, 21:35 to 21:52 CEST). Working record: _scratch/chk-int8/CHECK.md; closure draft:
CLOSURE-draft.md; the registry dumps and five scenario logs beside them. Note: fnd/int8 moved to 38fd7cc9 at 21:36
(the box logs and the suite log filed, 6 files, no tool, page or registry change; clean on identity, tag, trailer and
dashes); everything below is read at 7f6de345 by hash.

Blocking items: none.

Items that fail a literal criterion of the brief, rated minor by me:
1. One added line carries the trailer's literal name: v2/docs/records/w5tray/pass1/RESULT-w5tray-check-1.json line
   27 ("... no the co-author trailer (its name is not written here) trailer in this repo.", a quoted suggested commit body, added by fb4a52eb "recovered
   from its transcripts, unchecked"). pre-commit-check.sh rule 7 greps ^\+.*the co-author trailer (its name is not written here) on the staged diff and
   exits 1, so that checkpoint went in without the check. It attributes no commit; a fast-forward runs no check.
   Fix if wanted: reword that sentence in a docs commit (the string stays in fb4a52eb's history either way).
2. Four em dashes in added lines, all inside two fetched third-party pages (v2/vendor/rf/amphenol-rf-132134-11-...
   and amphenol-rf-132134-part-page-wayback-...html), not drafted prose. No drafted line or commit message has one.

Minor items:
3. D-20 adds two sentences that are the session's reading, not the owner's words: "(the case that never changes,
   the pack of D-06, the required mission)" as the approved constraints, and "The routes (c) to (e) of EQ-13 are not
   taken" (also M-02's appended sentence and EQ-13's new row). The owner asked for changes to capacity, placement or
   modes to be presented explicitly, which is compatible with (c) and (d) returning as presented options; (e) is
   excluded by "keep unmet criteria visible". Suggest "not taken by this ruling; (c) and (d) return only as options
   the reconciliation presents". Everything else in D-19 and D-20 matches OD-01 and OD-02 as corrected, element by
   element; no external DC source and no option (e) is recorded as the mission's basis; REQ-072's statement,
   acceptance and evidence_result (FAIL) are unchanged from main; M-02 stays OPEN. "thermocouple logger" in D-19 is
   grounded (READY-TO-ACT.md line 429, PicoLog TC-08).
4. S-114 is a statement of owed work sourced from D-20, not a finding from a walk, check or pilot record; suggest
   its title start from the finding it rests on (EQ-13's arithmetic, M-02: the balance fails at desk) before the
   study it owes, so the item reads as finding plus work like S-95 to S-113 do.
5. S-88's and S-89's closing_evidence name commit aaed6daa (the first re-take) while the tree's readings are the
   second re-take's (9d89ffd3, ts 19:15Z to 19:17Z). Verdicts, denominators, counts, netlist and tool shas are
   identical in both versions (both opened), and no tool of these two rules changed between the re-takes; wording only.
6. Stream w5tray's draft apply_w5tray.py writes six documents before the registry and stops without rolling back
   when a vendor file it hashes is missing (my first run in a sparse clone left ASSEMBLY.md, CASE-MARGINS.md and
   ENGINEERING-QUESTIONS.md applied and the registry not). It ran once on the full tree and is not run again; for the
   drafts' template (write everything after every assertion).
7. The checks' unanswered minor items (d8dec31 N1 to N6, d6rel 2 to 5, w5si2 m2, m3, m7) are in the filed check
   records only; I found no carry list in EXECUTION-PLAN.md or the registry naming them with an owner.

Registry diff (main -> 7f6de345, PyYAML): owner_rulings 29 -> 31 (D-19, D-20); session_choices 74 -> 75 (SC-75);
open_items 65 -> 82 (S-95 to S-114 added; S-63, S-88, S-89 removed; L-07, M-02, S-92 titles extended);
closed_items 59 -> 62 (S-63 by SC-75; S-88 and S-89 by commit aaed6daa with closing_evidence); records 144, 28
changed: waits_on on 20 (links to the new items; five also cite S-89 in history), evidence plus evidence_bound_to on
9 (rebinding entries), REQ-072 rulings +D-20 and waits_on +S-114, FEA-007 choices +SC-75; no statement, acceptance,
evidence_result, allocation or phase changed on any record; needs_document_sha256 equals the sha256 of CONOPS.md at
7f6de345. Every new open item is waited on by a record or carries a disposition with a reason (S-97 TOOLING, S-98
DECLARATION); S-95 to S-113 state findings with their source record. The closures rest on readings in the tree:
port_protect_a PASS of 42, netlist 0a2b59087bcc2678, writer 7acd5333fc59f8d0 (= port_protect.py at 7f6de345),
port_reviews dcaa890424a8d15f, 0 refused, 0 uncovered, 0 disagreements; the seven reliability readings INCONCLUSIVE,
writer c50f2b8b35d1d57b (= reliability.py at 7f6de345), list 40f2a98323b1f9ce, bound, per-board artefact shas, counts
and held_by lists exactly as the evidence states, all after the floor 20:33:53+02:00; the r2 tray set present with
its check.out RESULT: PASS.

Page difference (35 -> 34): the "decision 31 | review: not met" rows left A, D and E (the review is in the tree,
pinned 094817023210d1b0, read on each board's netlist; the hold's layout-entry requirement reads met, the hold
stays); "TRN-001 INCONCLUSIVE" rows joined B and C (port_protect.py reads INCONCLUSIVE a declaration no review has
enumerated, S-112) and their TRN-001 PASS rows left the PASS table. Per board A 7->6, B 7->8, C 3->4, D 7->6, E 4->3,
P 5, E5 2. Consistent everywhere: PASS on either 71->69, UNBOUND 20->13 and DESK_REVIEW 21->28 (REL-001 on seven
boards now bound desk readings), historical PASS 209->200, the limits paragraph (S-88, S-89) gone. All 62 PASS rows
with a sha match the board table's declared phase (7 registry/package rows carry none, same as main). No tool under
v2/ecad/tools changed between the second re-take's HEAD 05af085c and 7f6de345; TOOL_CHANGED 176 on both pages
counts historical readings. SI-001 readings record model_state PRESENT (A 5, B 10, C 6, D 5 models, each at its
pinned sha; E and P NOT_ASKED); by rules_status._pinned_state a reading taken at the pinned sha stays BOUND in a
checkout without the models (state ABSENT is neither DIFFERS nor recorded-absent-now-present), so a clean clone
renders the same pages; a re-take there would read less.

Merge: main is an ancestor; all six stream tips (0ad773ab, f84243ba, 9057e668, 3d7c98d2, 3bfaa317, 900ba526) are
ancestors; the three append-append files keep every line of both parents at each of the merges that touched them
(comm on sorted lines, 0 lost, 7 merge-file pairs) and every line of main at 7f6de345. Answered minor items verified:
w5si2 m1 (apply_board_c_declarations.py:53, README, coverage), m4 (.gitignore:41, check-ignore matches), m5
(vendor-status.txt:57 folder-level standards line), m6 (records/w5si/check-edges-7f7721c4.md); d8dec31 B2
(apply_registry_d31.py:234) and B3 (lines 289 to 297); d6rel minor 1 by the writer sha above.

Apply scripts (each run on a shared sparse clone at the parent of the commit that ran it, the script copied from
7f6de345, result diffed against that commit, then run again): apply_carried_check3.py at 420f252a -> registry
identical to 5c8a6d22, second run "REFUSED: S-97 exists already"; apply_i03_items.py and
apply_contract_contact_rating.py at 5e765762 -> registry and pcb_interfaces.yaml identical to a8607eab, second runs
refused; apply_owner_rulings_2026_09_28.py then apply_needs_sha_conops.py at 038037ed -> registry, CONOPS.md and
ENGINEERING-QUESTIONS.md identical to c5430071, second runs refused; apply_rebind_page_int8.py at 15d23a3b (the
history branch: "the page at HEAD is 719cca08a0823263 and the records are bound to a46365d4112c54ba; comparing with
the bound page from history") -> registry identical to 69ab7cb3, second run refused, and at 9d89ffd3 with 7f6de345's
page it refuses (the page the records are bound to) with the registry equal to 7f6de345's; the tray drafts
(apply_w5tray.py of c7447456, apply_frame_seat_r2.py) then apply_tray_links.py at beaf7e3c -> ids SC-75, S-95, S-96,
EQ-31, registry and eleven documents identical to c7447456, second runs refused. Docstrings state what each did.

What I ran, exact last lines: env -C int8/v2/ecad/tools python3 rules_lib.py -> "rules_lib: 59 rule(s), 0
error(s), 0 warning(s), fingerprint 635ff031f210f48c"; python3 rules_lib.py requirements -> "rules_lib: 144
requirement record(s), 0 error(s), 0 warning(s)"; the suite log _scratch/int8-ev/suite-7f6de345.log (present,
21:36; filed in 38fd7cc9) -> "tests: 2171 passed, 0 failed, 3 skipped" / "EXIT 0" / "7f6de345fd41..."; git
merge-base --is-ancestor main fnd/int8 -> holds; comm on the three conflict files -> 0 lines lost at every merge; the
five scenario logs as above. The validator in my sparse clones prints 75 errors "evidence_bound_to names
.../pcb-b-compute.net, which is not in this tree": my clones' missing netlists, not the registry.

Not checked, and why: the pages were not re-rendered (verdict writers) and the suite was not run here (the box
did); of the 96 changed evidence files only the closures' and SI-001's were opened; the streams' engineering content
was not re-derived (their own checks did that; I read their verdict lines and minor items). Circuit changes: none in
this set (no schematic generator, schematic, netlist or board file changed; gen_pcb_b3.py's 5 lines are board B's
RF net-class patterns).
