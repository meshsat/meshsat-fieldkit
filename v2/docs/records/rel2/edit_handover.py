"""LAYER-STATUS.md after the second release attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357, fnd/rel2 from
953f5658): the paragraph that says what the attempt did, and each affected layer's integrator line extended with what it
closed and what remains, the list it gives replacing the one before it. Ids from apply_registry.py's JSON (the argument).
Asserted anchors; run from the worktree root."""
import json, sys

IDS = json.load(open(sys.argv[1])); SC, M, EQ, PT = IDS['SC'], IDS['M'], IDS['EQ'], IDS['PT']
S1, S6 = SC['SC-HF-01'], SC['SC-HF-06']
L = 'v2/docs/handover/LAYER-STATUS.md'
s = open(L, encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:90]); s = s.replace(a, b)


rep("referred to here by id. **After H1.1 (set 4):** EQ-22 to EQ-24 are added and EQ-05 carries the hot stop.",
    "referred to here by id. **After H1.1 (set 4):** EQ-22 to EQ-24 are added and EQ-05 carries the hot stop. **The second "
    "release attempt (27 September 2026):** EQ-13 is rewritten as what the session took (SC-21) and %s is added." % EQ)

LEAD = "**Release check of layers 1, 2 and 3 (27 September 2026).**"
i = s.index(LEAD); j = s.index("\n", i)
s = s[:j] + ("\n\n**Second release attempt of layers 1, 2 and 3 (27 September 2026, branch `fnd/rel2` from `953f5658`).** Every "
             "blocking item the release checks left open is answered at desk, without lowering a requirement, dropping a "
             "function, weakening protection or narrowing scope: layer 2's B2 and layer 3's R4 (REQ-077's forced trigger at "
             "room temperature, `TEST-PLAN.md` %s, and E3-H's stepped run beyond the envelope), layer 2's B3 (the first "
             "Review A pass cited by its filed name wherever a page still named pass 2's file for it, and both filed "
             "records in `records/README.md` with their sha256), layer 2's B4 (C1 defined one way in POWER-THERMAL, "
             "ARCHITECTURE and HW-FW-CONTRACT, which gains the hot stop's and HOT-R1's rows; EQ-13; %s for BAT-F19), "
             "layer 3's R2 (SC-21 governs M1's duration; the owner's part of M1's failing balance is the owner action %s) "
             "and R5 (%s to %s, and the validator refusing an SC- id no registry entry defines), and layer 1's completion "
             "of B3 with the release check's minors m1, m4, m5, m7 and m8. The scripts and their records are "
             "`v2/docs/records/rel2/`. Session choices are the session's under the owner's standing rule of 26 September "
             "2026. No fresh reviewer has seen these fixes yet, so **layers 1, 2 and 3 stay IN_PROGRESS**; each integrator "
             "line says what was done and what remains." % (PT, EQ, M, S1, S6)) + s[j:]

rep("re-read the five layer 1 pages in every integration that touches EMCON, the case or CONOPS; (6) the fresh usability check of the snapshot (owner's prompt section 7). Owner: the integrator.",
    "re-read the five layer 1 pages in every integration that touches EMCON, the case or CONOPS; (6) the fresh usability check of the snapshot (owner's prompt section 7). Owner: the integrator. "
    "**Second release attempt (27 September 2026, branch `fnd/rel2` from `953f5658`, the commit that carries this sentence):** B1 to B3 of the release check were checked against the reviewer's exact fixes as applied in `08f3665a`: B1 and B2 are complete as applied (the brief, `README.md`, `v2/README.md`, `v2/BUILD.md` and V2-SPEC lines 10, 23, 24, 59 and 76 with correction 30 say what `feasibility/EMCON.md` section 0a and the case release say); B3 is completed here: the brief's power bullet points at the night finding, its L-02 row names SC-21 as governing M1's duration under the standing rule (the session's, replaced by the owner's own setting), its REQ-072 row names the owner's part as the registry's owner action %s, and EQ-13 is reconciled with SC-21 (this line's remaining item (4), with layer 3's R2). Minors taken: m1 (SC-13's reason no longer says CFL-010 stays open), m4 (the brief's closing rule in SC-16's words, \"re-checked once\"), m5 (the FEA-002 row: the lamp's light-guide hole is in the made face plate, not the Peli case), m7 (the ruling of 21 September 2026 located at the design appendix's section 32.362, near its line 18606), m8 (the two key-encryption keys named as SC-08's in the brief). **Status now: IN_PROGRESS** (no fresh reviewer has seen these). Remaining, replacing the list above: (1) a re-check of B1 to B3 and of these completions by a reviewer who wrote none of the changed lines, at one pinned commit, then the brief set to BASELINED in the commit that files it; (2) the snapshot from a pushed branch (acceptance item 14); (3) the minors m2, m3, m6 and m9, and I7; (4) the method change of the reviewer's section 4 (EMCON and the generators' state stated by reference, or the five layer 1 pages re-read at every integration that touches EMCON, the case or CONOPS); (5) the usability check of the snapshot. Owner: the integrator." % M)

rep("BANK-R1 on board B (S-54) and the cold end's 3.6 W/K bound (S-55). Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors.",
    "BANK-R1 on board B (S-54) and the cold end's 3.6 W/K bound (S-55). Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors. "
    "**Second release attempt (27 September 2026, `fnd/rel2`, the commit that carries this sentence):** remaining item (1), B2, answered: `TEST-PLAN.md` %s forces the hot stop at room temperature on the pack and on shore (one cell thermistor input substituted by a make-before-break decade resistance, read back in the gauge's `DAStatus2()` and never at its OTD of +57.5 C, because the gauge's own temperature offsets reach at most 12.7 K; H1 and its release, H2 through `PI_KILL` and MAIN, MASTER WARN and the e-paper, HOT-R1's four states, the TMP117 stand-in), E3-H gains its stepped run beyond the envelope (+40 C by 2 K an hour to at most +55 C, the +59 C abort kept) and the rule that a step that acted in no run reads NOT_VERIFIED, E3-L's pass line is unchanged, and REQ-077's prototype acceptance says the same (layer 3's R4 is this item). B3 completed: the first Review A pass is cited by its filed name at CONOPS lines 20 and 1138, TEST-PLAN line 3 and OPERATING-ENVELOPE line 36 (CONOPS lines 45 to 48 already did), and `records/README.md` carries both filed files with their sha256 (`e854c2a46ea3d542`, `fe6ca95b6c6356a8`); no record of the c23 verifier exists, as stated above. B4 completed: C1 is defined one way, as CONOPS 4c and SC-17 (the layer 2 closer's reduced-mode choice, `records/hc2/sc.md` row 1) state it: shed to the reduced mode on slots 2 and 3, then, reached again, to the heat stage's one module, which is slot 3 after BANK-R1 and slot 2 as board B is generated (CONOPS 4c's own text and SC-18; no source read contradicts it), in `feasibility/POWER-THERMAL.md` sections 1, 9.1, 9.2 and 9.3, `ARCHITECTURE.md` section 8 and `HW-FW-CONTRACT.md` FW-C09, which also gains FW-C13, FW-C14, FW-E10 and V-C13 for the hot stop and HOT-R1; (c) EQ-13 rewritten with SC-21 governing (layer 3's R2); (e) %s written for BAT-F19 (CFL-017) in group C, with its three routes, the evidence, the session's recommendation and the cost. Fifteen readings rebound, the needs pin and the envelope's two pins re-taken (`records/rel2/post_docs_registry.py`). **Status now: IN_PROGRESS.** Remaining, replacing the list above: (1) a re-check of B1 to B4 as now fixed by a reviewer who wrote none of the changed lines, limited to the difference from the release review's sha256 values, then CONOPS marked baselined in the commit that files it; (2) the release review's minors m1 to m16; (3) the later-stage items listed above (HOT-R1 on boards A and E, S-57 and EQ-22; S-58 and EQ-23; FEA-004, EQ-05 and T-H1; BANK-R1, S-54; S-55). Owner: the integrator, the TEST-PLAN owner, the registry writer and the board A, B and E authors." % (PT, EQ))

rep("(7) from the earlier list, REQ-077 FAIL until HOT-R1 (S-57) and GND-002 unruled (layer 4, `records/hc3/blocked-questions-layer-3.md` item 6). Owner: the integrator as registry writer.",
    "(7) from the earlier list, REQ-077 FAIL until HOT-R1 (S-57) and GND-002 unruled (layer 4, `records/hc3/blocked-questions-layer-3.md` item 6). Owner: the integrator as registry writer. "
    "**Second release attempt (27 September 2026, `fnd/rel2`, the commit that carries this sentence; `records/rel2/apply_registry.py`, by record id with asserted old text and next-free numbering):** R2 answered: SC-21 governs M1's duration under the owner's standing rule of 26 September 2026, recorded as the session's and replaced by the owner's own setting; the registry header's L-02 sentence, L-02 and SC-21 say so, and ENGINEERING-QUESTIONS EQ-13 states what the session took and what the owner may reverse or decide, no longer an open owner question; the owner's part of M1's failing balance is the owner action %s (the second pack, a larger pack, or accepting the residual; REQ-072 waits on it), S-53 keeps the session's part (the input path's rating), and REQ-016 and REQ-072 record that they cannot both hold on D-06's architecture; REQ-072's FAIL at desk is carried as it stands. R4 answered with layer 2's B2 (REQ-077's forced trigger %s and E3-H's stepped run). R5 answered: SC-HF-01 to SC-HF-06 are %s to %s, each with question, taken, why with its \"Reverse by\", and `drafted_as`; HW-FW-CONTRACT.md section 8 and S-59 and S-61 name them; `rules_lib.py requirements` refuses any SC- id cited in the registry or a page of `v2/docs/` or `v2/docs/handover/` that no entry defines by id or `drafted_as`, with fixtures both ways in `tests/test_requirements.py`; the rules_lib.py change moved two writers' code bundles, answered by two `kind: tool` entries in `v2/docs/evidence/COMPATIBILITY.md` (`records/rel2/tool_compat.py`). Layer 1's m1 (SC-13) is also in the registry. **Status now: IN_PROGRESS**; `baseline_state` stays READY_FOR_REVIEW_B and S-51 open. Remaining, replacing the list above: (1) R1: a fresh reviewer confirms R2 to R5 on one commit, then `baseline_state` names that commit and S-51 closes; (2) R3's last step, the anchor commit on the public repository once the integrating session pushes; (3) the release review's minors m1 to m10 and its section 6 notes (the 43 PROTOTYPE_MEASUREMENT records no TEST-PLAN row names, 25 of them core BLOCKERs; E5's INT-001 binding; the hot stop's firmware rows are now FW-C13, FW-C14 and FW-E10, while IF-AE-DOCK names pin 12 only when HOT-R1 lands, S-57); (4) REQ-077 FAIL until HOT-R1 (S-57), and GND-002 unruled (layer 4). Owner: the integrator as registry writer." % (M, PT, S1, S6))

rep("REQ-072's night finding (the energy architecture, S-53).",
    "REQ-072's night finding (the energy architecture, S-53). **Second release attempt (27 September 2026, `fnd/rel2`):** "
    "`feasibility/POWER-THERMAL.md` sections 1, 9.1, 9.2 and 9.3 (and one hand-off line of section 11) and "
    "`ARCHITECTURE.md` section 8 now take C1 as CONOPS 4c defines it (the reduced mode of slots 2 and 3, then the heat "
    "stage's one module; PS-RED named the one-module stage and PS-RED2 the reduced mode), so that part of the list "
    "above is done; `feasibility/EMCON.md` section 5a row 5 and REQ-072's night (S-53, and the owner's part %s) remain." % M)

rep("nor PANEL.md the reduced mode's and the hot stop's panel duties (layer 2's m13). Owner: the integrator and the board A, B, D and E authors.",
    "nor PANEL.md the reduced mode's and the hot stop's panel duties (layer 2's m13). Owner: the integrator and the board A, B, D and E authors. "
    "**Second release attempt (27 September 2026, `fnd/rel2`):** item (5) done: SC-HF-01 to 06 are the registry's %s to %s "
    "(each recording its draft name as `drafted_as`), and the validator refuses an SC- id no entry defines; item (7) done "
    "for the contract: FW-C09 takes C1 as CONOPS 4c defines it, and FW-C13, FW-C14, FW-E10 and V-C13 carry the hot stop, "
    "HOT-R1's four line states and the panel controller's read of the line at boot. PANEL.md's reduced-mode and "
    "hot-stop panel duties (layer 2's m13) and IF-AE-DOCK's pin 12 (with HOT-R1, S-57) remain." % (S1, S6))

open(L, 'w', encoding='utf-8').write(s)
print('edit_handover: LAYER-STATUS.md updated')
