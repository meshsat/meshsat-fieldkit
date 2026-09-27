# Layer 2 row for `v2/docs/handover/LAYER-STATUS.md` (draft by the layer-2 closer, fnd/hc2, 27 September 2026; pass 2)

| Layer | Status | Deliverables (at the integrating commit) | Remaining acceptance items | Next closing action |
|---|---|---|---|---|
| 2. Concept of operations | IN_PROGRESS: every layer-2 item the audit found doable now is carried out in the documents, and the seven blocking findings of Review A's first pass (`v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`, AI review, FAIL) are answered in them; the layer waits on the integration of its hand-offs and on Review A's second pass at that commit | `v2/docs/CONOPS.md`, `v2/docs/OPERATING-ENVELOPE.md`, `v2/ecad/tools/pcb_envelope.yaml`, `v2/docs/PANEL.md` section 9, `v2/docs/TEST-PLAN.md` (sections 1 to 4, 6 and 8); `v2/docs/records/hc2/pwr_red2.py` and `.out` | (1) the integration of `drafts/handoffs.md`: the registry re-pin, rebinds and records of its section 3 (SC-L2-01 to 18 from `drafts/sc.md`), the ENV-001 re-pin and `drafts/part_temps.patch` in the same commit (Review A m8), and the records the documents cite filed in that commit (`records/hc2/`, `records/w1/`; A06 is cited as to be filed; Review A m11); (2) Review A's second pass at the integrating commit (AI review, one fresh reviewer; brief `drafts/REVIEW-A-BRIEF.md` with its pass-2 section) finding no blocking item; then the layer is baselined at that commit | the integrator applies the hand-offs; then Review A pass 2; then baseline at that commit |

**Stated open, with why the layer can close without each (the owner's section 2 tests):**
- **The enclosure conductance (FEA-004)**: the ambient at which each shed stage acts, whether PS-TYP is sustained at
  +20 C, and whether the in-use +40 C holds on the pack at the pessimistic corner are bounds, not settled. No mode,
  trigger, bearer set or product decision of the ConOps changes with the number, because every control acts on a
  measured internal temperature or current; the thermal architecture may (layer 4). Decided by T-H1 before the pack
  and the PA flange site are placed. Engineering question: `audit.json` layer 2 blocked_questions[0] (options (a)
  behaviour on measured thresholds, taken; (b) the test, needs the owner's purchase; (c) lowering the envelope, not
  allowed).
- **The cold end's bound (Review A B7, PWR-F09's remainder)**: the cold warm-up brings the inside air to 0 C at -20 C
  only up to about 3.6 W/K lid open with fans; above it the kit-to-kit link (a critical peripheral, A11) is lost at
  -20 C and E4-O fails. The requirement (use to -20 C with the link) and the behaviour are set in the ConOps; whether
  the parts and the thermal path meet them is layer 6 (an extended-grade card and SDR) and layer 4 (T-H1), decided
  before board B's layout entry where a socket or supply changes. No layer-2 decision changes with the answer.
  Compact question: issue as stated; affected board B, E4-O, SC-02's link; evidence `records/hc2/pwr_red2.out` COLD
  block, POWER-THERMAL 9.4; attempts: the carve-out alone (fails in the idle and typical states), the warm-up (holds to
  3.6 W/K); options: (a) an extended-grade AW7915-class card and SDR, (b) measure the conductance (T-H1) and keep the
  warm-up if it is under 3.6 W/K, (c) a dedicated heater near the cards (a board change); recommended (a) searched now
  in layer 6 and (b) with T-H1; expertise: parts search, the T-H1 bench; cost: T-H1's (READY-TO-ACT section 5), a part
  TBD.
- **REQ-052 not met by board B as generated (Review A B5)**: its one-module stage lacks the LoRa mesh and APRS. The
  requirement is kept at the owner's example set; the fix is taken as a board B design item (BANK-R1, SC-L2-18, a hub
  port exchange with no part added; `drafts/gen_sch_b.BANK-R1.patch`), owed before board B's layout entry. A layer-4
  and layer-8 item for board B; layer 2's statement does not change with it. Reported to the owner, not asked.
- **M1 at 72 hours on pack and solar (Review A B3)**: set; on D-06's one pack the kit does not run through a single
  night on pack and solar alone, whatever the solar rating (binding), and the solar path's rating is the second limit:
  a layer-4 finding with its routes (an overnight input, D-01's deferred second pack, a larger pack), not a shorter
  mission. The routes are an operating condition that changes M1's setting or the owner's rulings to reopen; the layer
  states the mission and the finding, and no other layer-2 decision depends on the answer.
- **CFL-017 / BAT-F19 (Review A m6)**, widened by SC-L2-03 to the stored product's +71 C and -33 C margins: with its
  pack fitted the kit cannot meet D-02a's +55 C operating margin, E5's +60 C dwell or the storage margins, because the
  cells are rated to +60 C and -20 C (Samsung INR18650-35E Ver. 1.1 3.12, 3.13; at +55 C ambient the inside air is
  +61.6 to +74.2 C, OPERATING-ENVELOPE section 8). Affected: TEST-PLAN E3-S, E3-O, E4-S, E5; board P; D-06. Attempts:
  the margins run as stated deviations on the kit less its pack, which measures the rest of the kit and does not close
  it. Options, all outside the session's authority: (a) cells rated beyond +60 C (reopens D-06, money, R-BAT); (b) the
  owner's reading of D-02a that its margins apply to the kit without its cells; (c) a pack arrangement T-H1 and E3 show
  to keep the cells under OTD at +55 C (not expected: the air alone passes +60 C). Recommended: report to the owner with
  (b) as the reading the layer's text already runs, not asked. It is a qualification-margin conflict, not a layer-2
  mode or product decision: the use envelope and every state are set without it.
- **The pack's transport classification (REQ-069)**: no route is claimed, so no layer-2 decision depends on it; it can
  reopen layer 7 (a pack that must travel apart from the kit) or cost a UN 38.3 test (the owner's).
- **D-18 (the fans)**: no behaviour changes with the part; a stopped fan is a fault of CONOPS 4e.
- **EMCON's L_max**: a requirement the design does not meet at desk yet (layer 4 and 8, S-01); the ConOps states it.
- **The SGP41 at 62.1 C worst inside air** (found through `drafts/part_temps.patch`): a layer-6 and FEA-004 finding.
- **The bridge's own failover within 60 s and the PCIe AT channel on the CM5**: software items of the Bridge, outside
  this repository (MESHSAT-835 to 848); the ConOps states the bounds and their effect until shown.

**Changed consequences to report to the owner at the next checkpoint (not asked):** D-02b's "one module above +35 C"
and "no charge above about +25 C" now read, on the design record's own conductance, as C1 acting from +28.6 to +30.5 C
with three typical modules and the charge hold from +19.5 to +21.6 C, and on the independent bound at any ambient of
the envelope: the kit leaves its three-module redundancy from -6.3 C and runs one module from +20.1 C lid closed at
that bound's worst corner, so his acceptance of CON-012's residual risk, given at +35 C, is not carried to those
figures; the reduced mode is two modules, not one, and the one-module stage that carries his example needs board B's
hub ports exchanged (BANK-R1; as generated it lacks the LoRa mesh and APRS); on D-06's one pack M1 does not run through
a night on pack and solar alone; storage keeps the pack fitted (the round-8 choice had it out), which widens BAT-F19 to
the storage margins; and at the cold end the kit-to-kit link rests on a warm-up that fails above about 3.6 W/K until an
extended-grade card is found.

**Pass 3 (27 September 2026, the targeted fixer c23):** Review A's second pass (P2-B1, P2-B2) is answered: D-02b's row
marks the session's choices as the session's, and past the heat stage the hot stop acts on the pack's measured cell
temperature on every input state (CONOPS section 4c, TEST-PLAN E3-H). Still open from it: HOT-R1 on boards A and E
before their layout entry (the requirement reads FAIL on the generated boards until then); whether the stop fires
inside the envelope (FEA-004, OPEN until T-H1; at the independent bound's worst corner closed-lid operation at +40 C is
predicted to fail REQ-052 on any supply); and whether a non-destructive hardware stage is needed (the D-09 reviewer).
The layer still needs Review A's next pass at the integrating commit.

