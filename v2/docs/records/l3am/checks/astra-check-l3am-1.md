accepted: no

# Layer 3 amendment: the one check by the engineering collaborator (an AI review, read-only)

Collaborator job `cx10-l3am-check`, run `20260930T235755Z-972100`, model `gpt-6-astra` at effort `xhigh` (the client's own
record), on branch fnd/l3am at commit `29947b279165`. The launcher's computed outcome is DONE_CANDIDATE. The content below is the
collaborator's result as returned; the coordinator evaluated it before acting on it.

## Summary

AMENDMENT: NOT YET. Read-only AI review completed. L3-R01, L3-R02 and the amended REQ-016 wording meet their closure criteria. Two implementation defects remain in acceptance binding and findings closure. No owner decision is required.

## Blocking discrepancies

- B1, L3-R04: The requirements hash omits content that changes the governing demands. render_l3r2.py:54, :407 and :418 include selected record fields but exclude owner_rulings/session_choices, residual_risk_accepted and stages[].requires/needs/holds. Concrete examples are D-11's simultaneous-transmission ruling at pcb_requirements.yaml:554, CON-012's accepted operating exception at :16701, and the release conditions at :7545. A valid bound acceptance would survive changes confined to these fields because neither its requirements digest nor its other manifest members would change. Extend the projection to normative authority, exceptions and stage conditions while continuing to exclude observations and closure evidence; add focused mutation tests.
- B2, findings closure: apply_l3am_findings_closed.py:26 checks only that the supplied record is the newest verified ACCEPTED check. The current newest record, l3r2.yaml:594, is check-l3r5-3.md, whose :5 explicitly limits it to the earlier B2 correction on 30 September. By inspection, naming that existing record satisfies the closing script without an amendment check. The acceptance writer subsequently checks only the OPEN state. test_l3am.py:137 and :145 use that same old check and merely toggle CLOSED, so they do not detect this gap. Require a new accepted check explicitly bound to this amendment's scope and reviewed revision, and reject reuse of the pre-amendment check.

## Classification

- **MODELLING_ASSUMPTION**: L3-R01 historical solar case Evidence: l3r2.yaml:1123 identifies the historical array and model stage window; :1131 distinguishes the retained requirement.
- **IMPLEMENTATION_DEFECT**: Carried stopped-hour solar double count Evidence: energy_two_pack.py:257 sets stopped load to zero; :259 subtracts solar from shortfall; :262 uses that solar for charging. The amendment labels the consequence and assigns recomputation to L4-E2.
- **DESIGN_OBJECTIVE**: REQ-072 runtime target Evidence: OWNER-INSTRUCTION-2026-09-30.md:11 identifies 48 to 72 hours as a design objective; its missed target remains DR-01.
- **OWNER_REQUIREMENT**: REQ-042 detection and shutdown Evidence: pcb_requirements.yaml:12947 preserves the required function; :12949 supplies its amended outcome acceptance.
- **MISSING_EVIDENCE**: REQ-042 remaining stimulus and coverage derivations Evidence: pcb_requirements.yaml:4044 assigns sourced alarm levels, test gases and covered states to S-128, Layer 4.
- **IMPLEMENTATION_DEFECT**: B1 incomplete normative manifest Evidence: render_l3r2.py:418 projects only needs and BASELINE_KEYS, omitting the normative examples identified in B1.
- **IMPLEMENTATION_DEFECT**: B2 pre-amendment check can close findings Evidence: apply_l3am_findings_closed.py:26 accepts the newest check without amendment identity; l3r2.yaml:594 still names the earlier B2-only check.
- **OWNER_REQUIREMENT**: REQ-016 retained input window Evidence: pcb_requirements.yaml:976 records D-34; :7692 is byte-identical to b45d1705.
- **COMPONENT_LIMITATION**: SMCJ28A protection limits Evidence: Held Littelfuse SMCJ series sheet, revised 11/20/15, page 2: maximum clamping is 45.4 V at 33.1 A, above the protected capacitors' 35 V rating.
- **MISSING_EVIDENCE**: Panel surge and sustained over-voltage qualification Evidence: pcb_requirements.yaml:7711 leaves disturbance levels and their derivation open, with no protection claim pending Layers 4 and 8.

## Smallest next action

B1: extend the existing compact digest to normative authority, accepted exceptions and stage conditions, with mutation tests that preserve downstream-evidence positives. B2: require a new amendment-specific accepted check with reviewed revision, reject the existing pre-amendment check, and test the closing script's bounded changes.

## Closure criterion

B1: changing an authoritative ruling, accepted exception or stage requirement invalidates a previously valid acceptance for a requirements-manifest mismatch; unchanged content, added readings/notes, unrelated downstream files and acceptance history remain valid. B2: the current check-l3r5-3 record cannot close findings; a new verified accepted amendment check can close them, changes only checked_by/state/status, and permits subsequent acceptance only after the integration checks. Preserve the passing L3-R01, L3-R02 and L3-R05 dispositions.

## Owner decision required

no

## Checks

- Scope and retained requirements: PASS. HEAD matches the specified base commit. The 25 changed files belong to the amendment. All requirement-record statements, owner_rulings and session_choices are unchanged. REQ-016's literal window statement is byte-identical to b45d1705. No owner-approved number changed. LAYER-STATUS.md:298 contains the required 'Layer 3 accepted baseline; independent review findings open (L3-R01 to L3-R05)' wording. The worktree remains clean.
- L3-R01 solar attribution: PASS. No requested occurrence lacks a case label in its current section or adjoining qualification. The labels identify historical P-03, 400 Wp 2S2P into the model's 200 W window, incompatibility with retained REQ-016, understated unserved energy and pending L4-E2. REQUIREMENTS-L3-R2.md:63 and l3r2.yaml:1125 identify the same pack, load profile, array, voltage window and stage limit. runtime.out:27 and ARRAY.md:76 support that case. energy_two_pack.py:257 shows solar credited against stopped-hour shortfall and then used for charging. Original runtime, energy and array evidence, REQ-072 evidence entries, and the approved definition texts are unchanged.
- L3-R02 detection and shutdown specification: PASS. pcb_requirements.yaml:12949 requires separate end-to-end tests for water, hydrogen and VOC, defines stimulus and threshold bases, power/environmental states, timing start, MASTER WARN, both FETs opening within the retained 10 s, and persistence until service. S-49 closes selection only; S-128 at :4040 allocates remaining derivations to Layer 4. No concentration or alarm threshold is invented. Statement, prototype scope, verification methods and phases are unchanged. test_l3am.py:263 checks the selection-only boundary and rejects the former acceptance text.
- L3-R04 supplied binding tests: PASS. By inspection, the supplied negative cases reach their stated boundaries: zero/a revisions fail commit existence; the root commit lacks reviewed files; b4b199d0 differs from the manifest; REQ-016 at 500 W changes the requirements digest; brief/change-record byte changes fail current-content comparison; policy changes fail acceptance_policy comparison; a legacy record fails for no manifest. Positive fixtures preserve acceptance for unchanged content, evidence/note additions, unrelated files and acceptance history. Both acceptance fields are excluded from the policy hash, avoiding circularity. All explicitly named example categories from the received review are represented; the semantic omissions identified in B1 are not tested.
- L3-R04 completeness of requirements binding: FAIL. B1: render_l3r2.py:407 and :418 omit authoritative rulings/session choices, accepted-risk terms and stage-specific requirements. These are not all downstream observations. A material change confined to such content leaves the manifest unchanged.
- L3-R05 operating window and protection: PASS. pcb_requirements.yaml:7692 preserves the window. Its acceptance at :7703 separates protection and requires disturbance current/source impedance, waveform, duration, tolerance and the protected-node limit. The held Littelfuse SMCJ series sheet, revised 11/20/15, page 2, supports 28 V standoff, 1 uA leakage, 31.10 to 34.40 V breakdown at 1 mA and 45.4 V clamping at 33.1 A. DECISION-31-PROTECTION-TOPOLOGY.md:504 supports the cited bounded ESD result and reversed-panel constraint. Surge and sustained over-voltage remain unresolved at :7711; no part number closes them.
- Acceptance refusal and findings-closing script: FAIL. apply_l3r5_accept.py:101 correctly refuses OPEN findings. apply_l3am_findings_closed.py:35 bounds its edits to checked_by, state and status. However, its evidence predicate accepts the existing pre-amendment check, so the combined closure route is unsound as described in B2.
- Executable tests and integration checks: NOT_RUN. No tests, gates, renderers or verdict writers were run. In particular, l3amfix.py:34 writes temporary indexes and Git objects, and the acceptance tests invoke a writer on fixtures. No runtime test result is claimed.

## Evidence and minors

- MINOR: gen_sch_e.py:446 and :478 still contain the old breakdown-based protection implication; :446 also says 22 A instead of the held maker row's 33.1 A. This unchanged generator is explicitly assigned to board E in DISPOSITIONS.md:25. Correct its comment and value text in that bounded downstream change; do not treat the part as protection proof.
- MINOR: DISPOSITIONS.md:34 records that verify_acceptance.py still expects a manifest-free record to validate. Update that legacy scenario to expect DRAFTED before reusing the coordinator's acceptance-guard check.
- L3-R03 export reproduction remains the coordinator's separate obligation under DISPOSITIONS.md:16. This review does not establish clean-unpack reproduction or close that evidence obligation.
