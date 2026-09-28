# S-98: what closes it and what stays open (draft for the integrator's registry script, stream s98, 28 September 2026)

Prototype design; AI engineering work. The registry (`tools/pcb_requirements.yaml`) is the integrator's; this is the text
and the evidence list for the item's move from `open_items` to `closed_items` (fields as the closed items carry them:
`id`, `closed_by`, `closing_evidence`, `title`), to be run AFTER the box regeneration's pack is installed and the pages
re-rendered, never before.

## Preconditions (all four, in this order, in ONE integration set)

1. `fnd/s98` merged: the two generators carry the interim entries (commit `c098b8f3`: the four entries of
   `records/cx1/apply_declarations_draft.py`, the notes rewritten INTERIM, board B's M7 branches).
2. `python3 v2/docs/records/s98/apply_contract_i03.py` run from the integration worktree's root (it asserts the
   generator lines it cites and refuses if they moved), then `python3 v2/docs/records/s98/apply_architecture_i03.py`.
3. The box job `records/s98/box_regen_ab.sh` at the commit that carries 1 and 2, its pack installed with
   `_bin/install_pack.sh`. Until then the tree's `check_contracts` reads A and B MISSING (the netlists' provenance names
   the previous generators: `sch_prov: pcb-a-power.net was written by generator b3ba8f977ea264e2 and this tree's
   generator is 6fa6de3616f33dec`), so INT-001 and SCH-003 read INCONCLUSIVE on every board between 1 and 3.
4. The pack's `checks/lead-ends.txt` reads `5 of 5 leads AGREE`; `check_contracts` PASS with 0 fail on the six boards;
   `interfaces_a` PASS of 1 and `interfaces_b` PASS of 7 recording the rewritten `pcb_interfaces.yaml` as `spec`;
   `intent_rails` PASS on A and B (PWR-001); the parity of both netlists PARITY_AFTER_NOISE (the date only). A DIFFERENT
   netlist or a FAIL anywhere stops the closure.

## The closure

- `id: S-98`
- `closed_by: <the integration commit that installs the pack>` (the integrator fills it; the pattern of the closed items,
  a commit or the session choice that settled the item)
- `closing_evidence:` (one paragraph; the shas are read from the pack, never typed)
  > The interim alignment applied by the generator owners of boards A and B (fnd/s98, c098b8f3): board A's +5V_S2 4.2 A
  > typical and 5.63 A peak with J_5V_S2 5.63 A and the VBAT load Q28 2.22 A, board B's +5V_S2 peak 5.63 A, board A's
  > J_5V_DEV 3.8 A and +5V_DEV typical 5.1 A, the intent notes rewritten as INTERIM with the PS-ALLTX mode figures
  > INCONCLUSIVE; board B's M7 branches reconciled (U21 0.70 A, the child rail's declared burst bounding Ebyte's 650 mA
  > typical TX; U40, U50, U60 0.12 A, the child rails' typical; U25's comment corrected to the declared 1.2 A). Regenerated
  > on the KiCad box at <commit> (records/s98/box_regen_ab.sh): netlists PARITY_AFTER_NOISE (content unchanged), intents
  > intent_a <sha256/16> and intent_b <sha256/16>; lead_ends.py 5 of 5 AGREE; check_contracts PASS <n> of <n> re-taken;
  > interfaces_a PASS of 1 and interfaces_b PASS of 7 re-taken on the rewritten contract (spec <sha256/16>, the +5V_S2 and
  > +5V_DEV rows reading AGREE INTERIM, apply_contract_i03.py); intent_rails PASS on A and B (PWR-001). ARCHITECTURE.md's
  > IF-AB-POWER row brought to the same statement and to the held JST VH catalogue (apply_architecture_i03.py; the page is
  > bound by no registry record, checked). Declaration consistency only: the electrical adequacy of the two converters
  > against their loads is S-99's, and the mode currents are the bench's.
- `title:` the existing S-98 title, unchanged.

## What stays open (not closed by S-98)

- **S-99** (open, REQ-018 waits on it): the +5V_DEV converter's declared 6.9 A peak against the coincident 7.9 A (D8 at
  its typical) and 8.9 A (every declared limit) and the LM5176 average loop's 7.10 to 7.17 A minimum. Stream s99 decides
  it (sense resistor, an interlock, or the 8.9 A bound with the fold-back named); board A's generator then changes the
  peak, and PWR-001 and INT-001 are re-taken again.
- **The PS-ALLTX mode currents at J_5V_S2 and J_5V_DEV**: INCONCLUSIVE on every lead, decided by TEST-PLAN's power tests
  on a built board (prototype verification; FW-A15 in POWER-THERMAL.md). The INTERIM figures stand until then.
- **+5V_S2's 7.28 A all-peak conditional bound above the loop minimum**: a bound, named as one in the note; whether the
  loop acts on it depends on the burst duty and the soft-start time constant, computed nowhere in the tree (a bench item,
  both checks).
- **The U32 branch of board A's +5V_DEV (0.3 A) against VBUS_WALL's declared 0.5 A typical**: the parent allocation is
  S-98's own figure (5.1 = 3.8 + 1.0 + 0.3) and was not changed here; it belongs to S-99's re-sum of the branches
  (records/s98/README.md, residual R1).
- **The contract's `ends` src line numbers** (gen_sch_a.py:967-968, 1038; gen_sch_b.py:434, 831, 875) were stale before
  this stream and are outside apply_contract_i03.py's scope; the connectors are at gen_sch_a.py:1037-1038 and 1135 and
  gen_sch_b.py:551, 1119 and 1210 at c098b8f3 (residual R2).
- **The lead's own drop is in no board's share of the 2 percent budget** (records/cx1/ANALYSIS.md; both checks agree):
  a contract or budget item the integrator may open; no id.
