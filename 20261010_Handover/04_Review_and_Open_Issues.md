# Final review of Layers 1 to 3 and the open issues (handover of 10 October 2026)

**Scope of this review.** A bounded final read (about 30 minutes) by the coordinating agent session, from existing
evidence:
- Layer 1: purpose, users, scope and exclusions.
- Layer 2: scenarios, modes, interactions and the environment.
- Layer 3: identifiable requirements, acceptance criteria and traceability.
- Contradictions, missing files, broken links and later owner rulings.

It is an AI check, not a qualified engineering review. It re-uses the acceptance evidence named in `00_START_HERE.md`; it
does not repeat it. No requirement was changed and no source document was edited for this handover.

## 1. Findings on the baseline itself

- **Present and identifiable:**
  - Purpose, users, prototype scope and exclusions are stated (Layer 1 acceptance items 1.1 to 1.12, `LAYER-STATUS.md`).
  - The normal, degraded, startup, charging, shutdown, storage, service and fault scenarios, the envelope and the modes are stated (Layer 2 items 2.1 to 2.17).
  - Every requirement record has an identifier, a source link, an acceptance criterion where one is defined, an allocation, and a verification method and phase (Layer 3 items 3.1 to 3.18). `REQUIREMENTS-TRACE.md` carries the trace.
  - REQ-072 (runtime) is the registry's only design objective; every other record is mandatory.
- **Links:** every markdown link of the supplied core documents resolves inside this folder (checked by script at packaging). Citations written as repository paths in backticks are not links and resolve in the repository at the source commit.
- **Missing files:** none of the files the requirement pages link to is missing at the source commit.

## 2. Material issues

Kind: **INFO** = missing information or a record not yet updated; **FAIL** = an established design shortfall or failure
against a valid requirement; **PKG** = a packaging limitation of this handover.

| ID | Kind | Source | Affected | Practical consequence | Next engineering action |
|---|---|---|---|---|---|
| I-01 | INFO | `DEFINITION-CHANGE-RECORD-L3.md`; closure item L3-C63 | `PRODUCT-BRIEF.md`, `CONOPS.md` | The baselined texts still predate the owner's Layer 3 rulings D-32 to D-37; the change record governs where they differ (amendment A-2) | Write the change record's texts into both documents (re-stamp), keeping the accepted baselines as history |
| I-02 | INFO | `03_Requirements/APPROVED-AMENDMENTS.md` A-1 | D-06, D-01; `l3r2.yaml`, `REQUIREMENTS-L3-R2.md`, the definition texts | The second pack is approved (two identical, interchangeable complete 4S3P packs in the unchanged Peli 1450) but the registry and texts still read "D-06's one pack" | Add the approval to the registry as an amendment of D-06 with its exact scope; treat the one-pack restriction as superseded |
| I-03 | INFO | `REQUIREMENTS-L3-R2.md` section 2.6, rendered from `l3r2.yaml` (the `statuses` list) | the page's status table | It still reads the Layer 3 baseline "DRAFTED ... Not yet validated and accepted", although `baseline_acceptance` records acceptance at `3b4b92cf` (and `LAYER-STATUS.md` agrees). Editing it here would break the registry's content-bound acceptance | Read `baseline_acceptance` as governing; correct the status entry at the next registry revision and re-render |
| I-04 | FAIL (objective) | record l4rt (fnd/l4rt `3964c68a`), its two-pack coverage (fnd/l4rt72 `667c297e`, checked W360/W362); MODEL figures | REQ-072, 48 to 72 h at PS-IDLE-SPEC (42.8 W) | One pack runs about 2.5 h on battery; two packs about 5.04 h at +20 C and 2.08 h at -10 C; a September night is short by about 255 Wh; all 42 full-service rows FAIL (December 46 of 46). Only a reduced night mode (not approved; as drawn it hosts neither Iridium nor the SOS path) reaches zero, at +20 C only. The bus-voltage basis is the model's most favourable (feasibility finding F-01) | Keep REQ-072 as written; the runtime against service is the owner's scope question (section 3) |
| I-05 | FAIL | `REQUIREMENTS-L3-R2.md` 2.6 (DR-02, DR-03); Layer 4 records | power path, outlet contracts | Board A's power path as drawn fails (DR-02) and the outlet trips below its contracts (DR-03); Layer 4's desk gate is not passed and power closure is blocked | Re-architect or correct the power path in Layer 4 against the requirements |
| I-06 | FAIL (coverage) + INFO | record l4e12 section 21 (fnd/l4cfl `1eaf9d55`, checked W363 then W366) | REQ-042 battery-bay VOC sensing (CHO-001, SC-41) | The SGP41 covers VOC only to +50 C against bay air up to about 70 C. A Layer 4 working selection adds the Honeywell BES Series (-40 to +85 C, 0 to 90 %RH), CONDITIONAL: no printed trip concentration or maximum current, its bay fit, its CAN interface and the closed-bay test are open, and its maker states it is not a safety or emergency stop device | Verify the selection's conditions; answer the safety-device question (section 3) |
| I-07 | INFO | record l4e12 (closed-lid thermal arrangement), U-02, T-H1 | thermal requirements | The closed-lid arrangement is conditional on a physical thermal test (T-H1) that has not run | Run or commission T-H1 before thermal closure |
| I-08 | INFO | U-01 (bench E-01); record l4pk2; appendix 32.62 vs the pocket-fit check | cells, pack fit | Cell suitability is unqualified; the second pack's fit is unproven; the buildable store is recorded as 268.9 Wh in one source and 215.8 Wh in another | Qualify the cell; resolve the volume conflict from the case model; prove the two-pack fit |
| I-09 | FAIL (drafted fixes) | records l4checkb, l4emc (checked W373/W376), l4seat | board B EMCON lines; layout entry | Three EMCON circuit defects (U544 in fault F6, U543's pull-up, RB_IEN during U543's reset delay) have drafted corrections, unapplied. A further window (RB_IEN while +5V_DEV is under 2.6 V) is open. Board B's seating is incomplete (the last placed board had 6 hard violations and 178 decoupling-distance failures) | Apply or redesign in the board B round; do not start layout before it places clean |
| I-10 | PKG | repository state | Layer 4 working material | The unintegrated Layer 4 branches exist only in the programme's runner repository (not published) | Request the bundle named in `05_Engineer_Takeover.md` if that material is wanted |
| I-11 | PKG | all acceptance records | Layers 1 to 3 | Every acceptance rests on AI reviews and AI checks; none is a qualified engineering review | Hold the engineer's own review of the baseline as part of the takeover |

## 3. Product-scope questions (for the owner; they do not block the takeover)

1. **REQ-072, runtime against service.** No studied configuration meets 48 h at full service, including the approved two packs. The routes on record each reopen an owner ruling:
   - accept the shortfall (excluded by D-20 as recorded);
   - a reduced night mode, which turns services off;
   - a larger store, which is limited by the unchanged case.

   The record's plain-language restatement is in fnd/l4rt72 `L4RT.md` section 9.4.
2. **REQ-042, the gas shutdown's safety basis.** Whether the battery-bay gas shutdown needs a rated safety device. Both sensor makers disclaim safety use; the pack's own hardware protection does not depend on either sensor.

Routine technical choices (copper, stackup, components, routing, methods, test setups) are the receiving engineer's and are not listed here.
