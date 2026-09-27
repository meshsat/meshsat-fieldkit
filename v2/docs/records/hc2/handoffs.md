# Hand-offs from the layer-2 closer (fnd/hc2, 27 September 2026, MESHSAT-1357)

The files this closer owns and changed: `v2/docs/CONOPS.md`, `v2/docs/OPERATING-ENVELOPE.md`,
`v2/ecad/tools/pcb_envelope.yaml`, `v2/docs/PANEL.md` (section 9 only: S-19, S-32, S-39), `v2/docs/TEST-PLAN.md`.
Everything below is another owner's file: each item says what, why, and the exact text or patch where one is ready.
Nothing here is committed. Figures are PROVISIONAL, from `v2/docs/records/rv-pwr/pwr_budget.py` and this closer's
`drafts/pwr_red2.py` (which imports it unchanged).

**Pass 2 (later on 27 September 2026).** Review A's first pass (`v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`, AI
review, FAIL with seven blocking findings B1 to B7 and twelve minor m1 to m12) is answered in the five files above.
This file is rewritten for it: new items are 3.6's restatements, 3.8 (new records), 13 (BANK-R1 for board B's owner),
14 (`ASSEMBLY.md`), and the integration notes of section 1 against main `53a98a71` (Review A m12). The shas to pin are
in `drafts/final-shas.txt`.

**Pass 3 (later on 27 September 2026, the targeted fixer c23).** Review A's second pass (the same record, FAIL with
two blocking findings, P2-B1 and P2-B2) and the ConOps side of Review B of layer 3 (fnd/hc3's
`v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md`, B1 to B5) are answered in CONOPS (sections 3, 4, 4c, 4e, 4f, 7 and
7a), TEST-PLAN (a new row E3-H, the hot stop's acceptance with the abort at +59 C; E3-A's and E3-L's rows unchanged),
OPERATING-ENVELOPE (sections 3 and 4, re-pinned) and `pcb_envelope.yaml` (`hot_end.hot_stop`, `document_sha256`).
What changes for the other owners: (1) the ENV-001 patch now pins the pass-3 OPERATING-ENVELOPE
(`354bc222868bbfa9...`); (2) item 12's filing adds `drafts/hotstop_bounds.py` and `drafts/hotstop_bounds.out` to
`v2/docs/records/hc2/` (CONOPS cites them there; sha256 in `drafts/final-shas.txt`); (3) the registry side (the hot
stop's requirement, HOT-R1, the two open items, and the texts of REQ-024, REQ-046, REQ-052, CON-012, FEA-004 and the
heat-stage choice) is carried by fnd/hc3's apply script, which also takes this TEST-PLAN at `652353b9cb624cf3` and
fills E3-H's placeholder with the hot stop's record id; `drafts/pcb_requirements.pin-and-rebind.patch` of this worktree
is superseded by that script, which re-reads on the merged files; (4) boards A and E's owners: HOT-R1 before their
layout entry (item 16 below); (5) the panel controller's and the sensor controller's firmware contracts (`PANEL.md`,
layer 5): the hot stop's four line states and its two steps (CONOPS section 4c), not written into PANEL.md by this
pass. fnd/hc3's `CONOPS-d11.on-hc2.patch` is rebased onto this CONOPS; the second pass's CONOPS and TEST-PLAN patches
in fnd/hc3 are retired.

## 1. The integrator: merge order and conflicts (against main `53a98a71`, Review A m12)

- **`v2/docs/TEST-PLAN.md`: take fnd/hc2's file whole.** Main `53a98a71`'s TEST-PLAN is byte-identical to
  `drafts/r8bat-TEST-PLAN.lead.md` (sha256/16 86742b72d44adce6), which is fnd/hc2's base for this file, so every
  hunk in fnd/hc2 is a deliberate change on top of round 8's text: the stored state with the pack fitted (SC-L2-03),
  E3-S and E4-S as deviations, E3-T and E4-T for the stored and transport configurations, a Purpose and a Verifies
  column on every table, section 4's trace, sections 8 (T-H1 to T-H3) and 9 (the CASE-MARGINS fit checks), Records
  renumbered to 10, and pass 2's E3-L (E3-A's whole pass line with the lid closed, the owner's example set at every
  level, an SGP41 above +55 C a failure: Review A B4 and B5) and E4-O (round 8's +1.0 C and -9.0 C restored, m10; the
  link required after the cold warm-up, B7). The three-way merge conflicts in sections 1, 2, 3, 5, 6 and 7: resolve by
  taking fnd/hc2's side. If round 8 changed its TEST-PLAN after `53a98a71`, carry only those later changes.
- **`v2/docs/CONOPS.md`:** main's two edits of section 4b's table (the SA868 and QMX rows) are untouched by fnd/hc2:
  keep main's. Main's Transport and Storage rows (round 8's "Restriction, 26 September 2026 (SC-12)" and "the pack is
  stored apart ... (round 8, SC-12)") conflict with fnd/hc2's rows: **take fnd/hc2's rows**. They keep the cell maker's
  restriction in the Transport row's own words and carry the storage decision SC-L2-03, which supersedes SC-12's
  storage clause (item 3.3 below). fnd/hc2 also edits section 4's mode table (Transport, Deploy, Startup, Normal,
  Reduced, Heat stage, Degraded, EMCON power state, Shutdown, Storage, Service, Commissioning) and sections 3, 4a, 4c
  to 4f, 5, 6, 7 and 7a.
- **`v2/docs/PANEL.md`:** main edits sections 6 and 7 (its 0x48 row); fnd/hc2 edits section 9 only. Clean.
- **`v2/docs/OPERATING-ENVELOPE.md` and `v2/ecad/tools/pcb_envelope.yaml`:** untouched on main since `e3aedb25`. Clean.
- **Same commit, or the tools read a superseded basis (Review A m8):** `drafts/part_temps.patch` (item 8) lands in
  the integration commit that lands `pcb_envelope.yaml`, together with `drafts/pcb_rules_coverage.ENV-001.patch`
  (item 2) and the registry items of section 3. Then, per the integration recipe, commit the config inputs before
  `rules_status`.
- **Records filed in the same commit (Review A m11):** `records/hc2/` (item 12) and `records/w1/`, or CONOPS cites files
  that are not in the tree.

## 2. `v2/ecad/tools/pcb_rules_coverage.yaml` (ENV-001 re-pin): apply `drafts/pcb_rules_coverage.ENV-001.patch`

`OPERATING-ENVELOPE.md` changed, and `pcb_envelope.yaml`'s `document_sha256` is re-pinned in the same change. The
patch sets ENV-001's `verified_sha` to the new document (pass 2's sha, `drafts/final-shas.txt`) and `verified_on` to
2026-09-27, with a 24-character note: the fixture `tests/test_envelope_data.py` looks for the pin within 3000
characters of `ENV-001:`, and the original entry had 93 characters of headroom (a longer note moves the pin out of the
window; a limit the tools owner may want to lift). With the patch, `tests/run.py test_envelope_data` passes. Per the
integration recipe, commit the config inputs before `rules_status`.

## 3. The requirements registry (`v2/ecad/tools/pcb_requirements.yaml`; registry writer, or the layer-3 closer)

1. **Re-pin the needs document:** `needs_document_sha256` to the committed `CONOPS.md`'s sha256 (the needs table of
   section 2 is unchanged, so `needs` needs no edit). `drafts/final-shas.txt` holds fnd/hc2's side of each file; the
   integrated files differ wherever main's own edits merge in (CONOPS 4b, PANEL 6 and 7), so every pin and binding is
   taken from the integrating commit's files, not copied from that list.
2. **Rebind the readings** whose bound documents changed (seven at `e3aedb25`, eight on main) (`rules_lib.py requirements` reports them). Each reading's
   subject is in a section fnd/hc2 did not change in substance, so a re-read is expected to confirm it, but the
   rebinder reads it:
   - REQ-005 (CONOPS section 2a: unchanged);
   - CFL-001 (PANEL section 1 and the pin table: unchanged);
   - CON-018 (TEST-PLAN M7: "at decision 34's ruled level, IEC 61000-4-2 level 4", verifying REQ-029 and CON-018);
   - CFL-005 (PANEL section 7: unchanged by fnd/hc2; main changes it);
   - CFL-016 (PANEL 1, 6, 7; CONOPS sections 4 and 4b; OPERATING-ENVELOPE sections 2 to 4; TEST-PLAN section 4: the
     S-07 corrected statements are kept verbatim in each);
   - CFL-014 (PANEL 10, CONOPS Charging row, OPERATING-ENVELOPE section 3's corrected hold-off paragraph: kept);
   - CFL-015 (PANEL 10: unchanged);
   - and on main since `53a98a71`, **CFL-008** (bound to TEST-PLAN at round 8's text: E5 and E8, kept as fnd/hc2 wrote
     them in pass 1, with the valve and without the vent).
   `drafts/pcb_requirements.pin-and-rebind.patch` carries the re-pin and the seven rebinds at pass 2's shas, against
   `e3aedb25`'s registry; on top of main's registry apply it by value (the strings are unique). With it applied in a
   scratch copy: `rules_lib.py requirements` 132 records, 0 errors; `rules_render.py --requirements --check` current
   after `--requirements`; `tests/run.py test_requirements` passing (the numbers of the pass-2 run are in the closer's
   report). **Main `53a98a71` adds bindings of its own** (S-43 closed on `dd39fb15`'s TEST-PLAN, and others round 8
   rebound): every reading bound to TEST-PLAN, CONOPS, PANEL or OPERATING-ENVELOPE on main is rebound the same way.
3. **Session choices:** add SC records from `drafts/sc.md` (SC-L2-01 to SC-L2-18; numbers are the registry's).
   SC-L2-03 supersedes the storage clause of SC-12 (on main since `53a98a71`): amend SC-12's `taken` to drop "+71 C
   and -33 C storage with the pack out" and point at the new record, keeping the rest.
4. **Open items:** close S-24 (SC-L2-01), S-26 (SC-L2-07, definition), S-37 (SC-L2-09), S-19, S-39 and S-32's operator
   half (SC-L2-14; S-32 keeps the message format and recipient list); reclassify L-02 from OWNER_ACTION to SESSION
   with the standing rule as the reason and close it by SC-L2-05. **S-43** is closed on main by `dd39fb15`'s TEST-PLAN
   (pack out in storage): rebind its closing evidence to the integrating commit's TEST-PLAN sections 1 and 6 (stored
   with the pack fitted, E3-S and E4-S as deviations, E3-T and E4-T for the stored configuration). D-18 stays
   CONDITIONAL (the parts stream's fit check; no layer-2 item waits on it).
5. **Conflicts:** CFL-011 resolved (one definition, a named trigger source: SC-L2-01); CFL-008 resolved (TEST-PLAN E5
   and E8 as written); CFL-009 stays resolved and its evidence is now true on its source (TEST-PLAN section 1 state
   "deployed closed-lid" and E3-L); CFL-007 resolved on its source (every row states its purpose); **CFL-017 restated**
   (main's text says "the reading ... the session did not take"; it now did): the stored product has its pack fitted,
   so BAT-F19 covers the +71 C and -33 C storage margins as well as +55 C operation and E5's +60 C dwell, left open as
   the product-level conflict it is, its routes (cells beyond +60 C, which reopens D-06 and costs money; the owner's
   reading of D-02a that its margins apply to the kit without its cells; T-H1) outside the session's authority;
   CFL-003 waits on item 7 below.
6. **Records to restate** (pass 2 changes are marked):
   - REQ-004 acceptance (pass 2): "every device of the moved bank back in service (IOHA section 7 step 12, application
     access resumed, by a bridge instance already running on the adopting module) within 30 s of its home module's
     loss, plus the device's own start-up where its maker states a longer one; the bridge's own service back on a
     surviving module within 60 s of the loss" in place of "TBD, measured on hardware".
   - REQ-003 acceptance: the kit's own hand-off within 10 s; end-to-end per bearer recorded as characterisation.
   - A new NEED-02 requirement (the layer-3 closer's action): with any one long-range bearer declared down (device
     lost, or no hand-off accepted for 60 s while one is pending), its queue delivered over the next bearer that is up
     within 10 s of the declaration.
   - REQ-014: "aged" = 80 % of the specification minimum capacity (SC-L2-07); PROVISIONAL 2.5 h and 1.7 h.
   - REQ-016 (pass 2): waits_on the new layer-4 finding's second half (the solar path's rating against M1), not L-02;
     its tbd_effect already names the day and night balance.
   - REQ-017, REQ-018, CON-019: the outlets' minimum contract is 0 W, the outlets off (SC-L2-08); REQ-017 "on battery,
     inside the outlet budget" (PWR-F13).
   - REQ-018 and REQ-059: every PA key-down at most 60 s (K1), with K2 to K5 and C4 (PWR-F14).
   - REQ-024 statement (pass 2): the "+35 C" carve-out becomes "the kit sheds to the reduced mode and then its heat
     stage on measured inside-air (+50 C) and cell (+55 C) temperatures; the ambient at which it does is a bound
     (OPERATING-ENVELOPE section 3)", and gains "below 0 C inside air the WiFi link cards and the SDR are powered only
     once the kit's cold warm-up has brought the air to 0 C (CONOPS section 4c; the bound above about 3.6 W/K OPEN)".
   - REQ-025 acceptance: the storage state of charge is the cells' ex-factory state, 3.49 to 3.69 V per cell, every input
     unplugged and the pack in the gauge's shutdown (SC-L2-03).
   - REQ-051's last sentence: "the margins run on the kit less its pack as stated deviations, and the stored product's
     result is BAT-F19" in place of "with the pack removed (SC-09)".
   - **REQ-052 (pass 2, NOT restated down; Review A B5):** keep the statement's example set. Statement: "With the lid
     closed the kit operates in a defined reduced mode (slots 2 and 3, CONOPS section 4c), entered when the lid is
     sensed closed; when C1's triggers recur there it runs one module that carries the owner's example (GNSS, the LoRa
     mesh, Iridium and APRS beacons) with the SOS path." Acceptance: "TEST-PLAN E3-L: E3-A's pass line with the lid
     closed; at every level up to the envelope's +40 C at least the owner's example set with the SOS path passes
     traffic, and the reduced mode's set up to the ambient at which C1 acts; every part inside its published range (an
     SGP41 above +55 C fails)." waits_on: the new finding below (BANK-R1) and FEA-004.
   - CON-012 (pass 2): "one module above +35 C" restated as the heat stage on measured temperatures, the ambient a bound
     (from +20.1 C lid closed at the independent bound's worst corner); **its `residual_risk_accepted: OWNER` is not
     carried over to the new ambients** (Review A m7): record the owner's acceptance as given at +35 C (D-02b), and the
     new figures as reported to him at the next checkpoint, not accepted.
   - CON-013: already TBD until measured; add that on 32.53's conductance the hold-off is +19.5 to +21.6 C.
   - ASM-004 (10 K and 16 K): superseded by `feasibility/POWER-THERMAL.md` section 9.1 and OPERATING-ENVELOPE section 3.
   - REQ-028: "no service-life requirement for prototype 1 (D-02c); the duty cycle is CONOPS section 5's profile".
   - REQ-035: gains the ZEROIZE success and incomplete indications of PANEL section 9 (S-19).
   - REQ-050: a DESK_REVIEW reading bound to the committed TEST-PLAN (every row now traces and states its purpose).
7. Then `rules_render.py --requirements` to regenerate `REQUIREMENTS-TRACE.md` (it refuses while items 1 and 2 are
   pending, which is why `--check` could not pass in fnd/hc2's own tree).
8. **New records (pass 2), each with its source in the committed CONOPS:**
   - a **finding: REQ-052 not met by board B as generated** (its one-module stage, slot 2, lacks the LoRa mesh and APRS;
     CONOPS section 4c), closed by BANK-R1 (SC-L2-18, item 13), reported to the owner at the next checkpoint; affected:
     board B, REQ-052, E3-L;
   - a **layer-4 finding: M1's energy** (CONOPS section 3, M1): binding, the aged pack's ~108 Wh bridges 2.5 to 5.0 h of
     darkness against nights of about 7 to 16 h at 52 N, so on pack and solar alone M1 fails every night whatever the
     solar rating (D-06's one pack, D-01's deferred second pack); second, the solar path's rating (about 1.0 kWh a day
     through a ~100 W front end). Routes: an overnight input on the 9 to 36 V entry, D-01's deferred second pack, a
     larger pack (D-06). Reported to the owner, not asked;
   - an **open bound at the cold end (PWR-F09's remainder)**: the cold warm-up brings the inside air to 0 C at -20 C only
     up to about 3.6 W/K lid open with fans; above it the kit-to-kit link (a critical peripheral, A11) is lost at -20 C
     and E4-O fails. Decided by T-H1 and an extended-grade card and SDR (layer 6), before board B's layout entry where a
     socket or supply changes;
   - a **finding for the parts stream and FEA-004**: the SGP41 (board E U17, rated to +55 C) at the worst inside air of
     62.1 C lid closed (after BANK-R1; 60.6 C as generated), which `part_temps.py` reports once item 8 lands.

## 4. `v2/docs/feasibility/POWER-THERMAL.md` (power and thermal stream)

The reduced mode is slots 2 and 3 and the heat stage is one module carrying the owner's example with the SOS path:
slot 3 once board B carries BANK-R1, slot 2 as generated (CONOPS section 4c, SC-L2-01, 02 and 18). Replace:
- section 1, the convention "**The reduced mode's one module is slot 3**, because the LoRa mesh ... is on slot 3's SPI"
  with "The reduced mode is slots 2 and 3 (CONOPS section 4c). Its heat stage is one module: slot 3 alone once board
  B's hub ports are exchanged (BANK-R1), which is this page's PS-RED with the APRS beacons (PS-SURV-R); slot 2 alone as
  board B is generated (PS-SURV), because there slot 3 alone has no host for Iridium or the SOS path.";
- section 9.3, C1: "shed to one module (slot 3)" with "shed to the reduced mode (slots 2 and 3), and, if the triggers
  are reached again there, to the heat stage (one module: slot 3 after BANK-R1, slot 2 as generated)";
- add PS-RED2 (31.4 W, 17.6 to 55.6; aged 3.5 h), PS-SURV-R (23.3 W, 12.8 to 46.9; aged 4.7 h) and PS-SURV (21.7 W,
  12.4 to 42.0; aged 5.0 h) to sections 4, 6, 9.1 and 9.2 from `v2/docs/records/hc2/pwr_red2.out` (or carry the states
  in `pwr_budget.py` itself); PS-EMCON as generated since `458b2873` is 47.1 W (37.3 to 80.6): the model's EMCON state
  still gives the WiFi link cards 4.0 and 1.0 W, the circuit before `458b2873`;
- add the cold warm-up (section 7.1's cold rows): PS-TYP with the link cards and the SDR off, the regulated heater at
  8.5 W and the three modules loaded, 71.1 W, +2.0 to +4.2 C inside air at -20 C on 32.53's conductance, failing above
  about 3.6 W/K; and correct section 7.1's cold rows, which carry the unregulated 10.8 W mat and so overstate the
  warming at the cold end (`pwr_red2.out`, COLD block).

## 5. `v2/docs/ARCHITECTURE.md` (integrator)

Line 832's row "PS-RED, slot 3 only, monitor off (the closed-lid reduced mode of D-02b)" becomes "PS-RED2, slots 2 and 3,
monitor off (the closed-lid reduced mode of D-02b, CONOPS section 4c) | lid closed, fans | 31.4 (17.6 to 55.6) | 31.7",
with the heat stage's two rows: PS-SURV-R, slot 3 alone after BANK-R1: 23.3 (12.8 to 46.9), heat 23.4; PS-SURV, slot 2
alone as board B is generated: 21.7 (12.4 to 42.0), heat 21.9.

## 6. `v2/docs/V2-SPEC.md` (integrator)

- Line 23 (run time): the PROVISIONAL figures are PWR-F07's: 2.5 h (PS-IDLE-SPEC) and 1.7 h (PS-TYP) for an aged pack,
  "aged" being 80 % of the specification minimum capacity (CONOPS section 6).
- Line 73: "estimated inside-air rise about 10 K with one module and 16 K with three loaded modules" becomes "the
  inside-air rise per state is bounded, not measured (OPERATING-ENVELOPE section 3): for three typical modules lid open,
  19.46 to 21.41 K on the design record's conductance and 22.54 to 52.65 K on the independent bound; the kit sheds on
  measured temperatures (CONOPS section 4c)".

## 7. `v2/ecad/tools/pcb_board_facts.yaml` `_product` (CFL-003; integrator, follow the integration recipe)

- `operating_modes`: `[normal (three modules, lid open), reduced (slots 2 and 3, lid closed or C1/C3), heat stage (one
  module: slot 3 after BANK-R1, slot 2 as generated), blackout, NVG, EMCON, charging, transport and storage (pack in
  the gauge's shutdown), service, commissioning]`, citing `CONOPS.md` section 4.
- `environment`: "field portable, unconditioned, vehicle transport; the adopted envelope (decision 34):
  v2/docs/OPERATING-ENVELOPE.md at sha256 <the committed document's>" in place of "no temperature range ruled yet".
Board facts change checker fingerprints: commit the config inputs before `rules_status`, re-take affected readings by
retake or `--out-dir`, never a gate by hand in the tree.

## 8. `v2/ecad/tools/part_temps.py` and its fixture (tools owner): apply `drafts/part_temps.patch`, in the same commit

`pcb_envelope.yaml` now carries `worst_inside_air_c` (pass 2: 59.2 C lid open, 62.1 C lid closed, the required heat
stage after BANK-R1 at the independent bound's lowest conductance; the generated board's 57.9 and 60.6 C beside it under
`as_generated`). The old `inside_air_rise_k` (10, 16) and the `above_c: 35` carve-out are kept, marked superseded, only
so the tool and `test_part_temps` stay green until this patch lands; **land the patch in the same integration commit**
(Review A m8), or THM-001 keeps reading the SGP41 as in range on the superseded 51 C bar. The patch makes
`inside_air_max` read the new figure when present and moves the fixture to a copy without it. Verified in a throwaway
copy at pass 2 (the result is in the closer's report); `part_temps.py` then reports **board E's SGP41 (U17, rated to
+55 C) outside its range at 62.1 C inside air** besides board B's H5007NL cold end: a real finding for the parts stream
(layer 6) and FEA-004 (item 3.8), not a defect of the patch. After it lands, the two superseded entries can be removed
from `pcb_envelope.yaml` (and the document's section 3 record paragraph can stay).

## 9. `v2/docs/PANEL.md` line 5 (outside fnd/hc2's three items)

"The bridge sees the panel move hosts, never disappear, unless two modules are gone." Add: "In the reduced mode (slots 2
and 3) the panel's bank is hosted by slot 2 (bank 1, failed over) as board B is generated, or by slot 3 (bank 3, its
home) once board B carries BANK-R1 (`CONOPS.md` section 4c); with both hosts of the panel's bank lost (slots 1 and 2 as
generated, slots 3 and 1 after BANK-R1) the panel has no host and SOS shows 'SOS NOT SENT: NO HOST' (section 9)."

## 10. `v2/docs/feasibility/ZEROIZE.md` section 3.4 step 8 (ZEROIZE page owner)

"sounds 3 s and refreshes the e-paper" is the DONE case. For INCOMPLETE, PANEL section 9 now sets: MASTER WARN keeps
flashing, three 200 ms pulses every 5 s, e-paper "ZEROIZE INCOMPLETE: SLOTS HELD OFF, RETRYING". Carry both in step 8.
Once BANK-R1 lands, section 3.3 and risk R4 name bank 3, not bank 1, as the panel controller's bank (item 13).

## 11. `v2/docs/review-packets/battery/THERMAL-COORDINATION.md` section 9 (battery stream; on main since `53a98a71`)

Its storage reading ("a stored kit has its pack out, and the pack is stored apart") is superseded by the ConOps's
storage decision (SC-L2-03): stored with the pack fitted, every input unplugged, in the gauge's shutdown at the
ex-factory state. Option C otherwise stands. Section 9a's BAT-F19 third part ("if the owner were to rule that a stored
kit keeps its pack") is now unconditional, by a session decision rather than an owner ruling. The E3-S and E4-S rows of
its option table read "stored: pack out"; TEST-PLAN now runs them on the kit less its pack as deviations.

## 12. Records to file (records integrator), per `v2/docs/records/README.md`

- `drafts/hotstop_bounds.py` and `drafts/hotstop_bounds.out` to `v2/docs/records/hc2/` (pass 3; the hot stop's
  thresholds against the battery packet's error budget and the ambients at which it acts, arithmetic on
  `pwr_red2.out`; cited by CONOPS sections 4 and 4c, OPERATING-ENVELOPE section 4 and `pcb_envelope.yaml`).
- `drafts/pwr_red2.py` and `drafts/pwr_red2.out` to `v2/docs/records/hc2/` (sha256 in `drafts/final-shas.txt`; pass 2
  adds PS-SURV-R, the COLD block and PS-EMCON's aged-60 % runtime, and leaves every pass-1 figure unchanged; cited by
  CONOPS sections 4a, 4c, 5 and OPERATING-ENVELOPE sections 3 and 4; the script finds `../rv-pwr/pwr_budget.py` from
  there).
- W1's `w1-decisions.md` and `w1-conflicts.md` to `v2/docs/records/w1/` (the layer-1 closer's action; CONOPS cites those
  paths at its sources paragraph and section 7).
- The adjudications A01 to A11 (scratchpad `adj/`, about 41 MB with PDFs and box runs): the markdown adjudications and
  their scripts under `v2/docs/records/adj/`, maker documents to `v2/vendor/` per the README's rule. CONOPS and
  OPERATING-ENVELOPE name A06 as "to be filed" and carry its finding through `ASSEMBLY.md` section 3 and
  `CASE-MARGINS.md`.
- The Review A record (`v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`, the first pass, untracked in fnd/hc2) and the
  brief (`drafts/REVIEW-A-BRIEF.md`, to `v2/docs/reviews/2026-09-27-review-A-layer2-brief.md`).

## 13. Board B's owner: BANK-R1 (SC-L2-18; Review A B5), before board B's layout entry

- **The change:** `drafts/gen_sch_b.BANK-R1.patch` (against `e3aedb25`'s `gen_sch_b.py`, lines 764 to 766, `PORTS`):
  the RockBLOCK's `RB_DP/RB_DM` with the QMX's `QMX_DP/QMX_DM` (port 4 of banks 1 and 2), and the panel controller's
  `USB_PNL_P/N` with the wall port's `USB_WALL_P/N` (bank 1 port 2, bank 3 port 3). No part is added or moved.
- **Why:** slot 3 alone (bank 3 home, bank 2 failover, the LoRa module on its SPI) then carries the owner's D-02b
  example with the SOS path, so REQ-052's one-module closed-lid set is met; ARCH-PCB-B-IOHA section 8's rule holds
  (bank 1 HF, bank 2 Iridium, bank 3 APRS; desk-checked on the table against `check_pcb_b.py`'s BEARERS invariant,
  lines 424 to 431); three of D-01's four bearers survive any one module loss.
- **For the owner to do and show:** regenerate with parity; the BEARERS invariant on the netlist; the contracts that
  name `USB_PNL` and `USB_WALL` (`check_contracts.py` item 11 and the J_AB2 and J_PANEL pair routes, `pair_preroute.py`
  line 456, `idc_pads.py`); the descriptive strings that name the old banks (`gen_sch_b.py` the section comments at
  lines 939 and 952, `J_QMX` "bank 2 hub, port 4", `J_AB2` "bank 3 hub port 3", the D-12 comment at line 1080); the
  acceptance tests A1 to A14 as written. If a reason is found that the exchange cannot be made, try the other one that
  keeps section 8's rule (the panel controller with the 5G management link, bank 3 port 4); if neither can, report it,
  and the finding of item 3.8 goes to the owner as a trade.
- **Documents that follow once it lands:** `ARCH-PCB-B-IOHA.md` sections 4 (the ring's contents), 15 (the table's bank,
  port and owner columns for the four devices) and 15a (the bearer count per loss, the two-module SOS pair);
  `feasibility/ZEROIZE.md` section 3.3 and R4 (bank 3 is the panel's); `feasibility/EMCON.md` section 4.5 (the hosts
  that learn of EMCON through the panel); `PANEL.md` line 5 (item 9); CONOPS section 4c then drops its "as generated"
  columns (the layer-2 owner's, at that time).

## 14. `v2/docs/ASSEMBLY.md` section 8 (its owner): apply `drafts/ASSEMBLY.step10-and-lamp-test.patch`

Step 10's ten minutes of key-down at 30 W is forbidden by K1 (every key-down at most 60 s; PWR-F15 puts the flange at
about 95 C after one 60 s key-down at 45 W of heat from a +50 C plate, against the RA30H1317M1's +100 C case maximum);
the patch makes it T-H3's 60 s key-downs inside K2 and C4 with the flange logged. Step 7's "all 17 LEDs" becomes PANEL
section 9's seventeen controller-lit indicators. CONOPS section 4d already states the supersession (Review A B6).

## 15. Not done by this closer, and why

- **The pack's dangerous-goods classification (REQ-069)** from the ADR's own text: the UNECE site answered HTTP 403 to
  this host on 27 September 2026 and no copy is in `v2/vendor/`; the battery stream's item, with a SOURCES entry. No
  layer-2 decision waits on it, because no route is claimed.
- **D-18** (the Delta 40 mm IP68 fan against the CM5 Cooler): the parts stream's desk check; the fan drawing is not
  filed. No layer-2 behaviour changes with the part.
- **The empty-case heat-balance test (T-H1)**: needs the owner's purchase authorisation (READY-TO-ACT section 5). It
  now also decides the cold end's open bound (item 3.8).
- **The bridge's own failover (60 s) and the PCIe AT channel on the CM5:** software items of the Bridge (MESHSAT-835
  to 848), outside this repository; CONOPS states the bounds and the effect until they are shown.
- **TEST-PLAN items of other layers:** the carried-mass weighing (REQ-023), the antenna return-loss check and the
  E1 end-wall drop guard (layer 7) are not in the plan yet.

## 16. Boards A and E's owners: HOT-R1 (pass 3, the targeted fixer c23), before their layout entry

The hot stop (CONOPS section 4c) needs a path from board E's sensor controller, the pack gauge's only SMBus host, to the
panel controller that needs no compute module. The contact and the receiving input exist: board E's `J_BLK` pin 12
(`BLK_SPARE`, only `TP7` as generated, `gen_sch_e.py` lines 562 and 693 at `a8652172`) runs through the dock block to
board A's `J_DOCK` pin 12 (`DOCK_SPARE`, `gen_sch_a.py` line 226), which lands on `U27` pin 18 (line 1262), whose
`EXP_INT` (`R110`, line 1267) reaches the panel controller's GPIO24. The change: on board E, `U10` GPIO19 (pin 30, not
connected) through a series 100 R to the gate of a 2N7002 (the part `Q8` to `Q10` already use) with a 100 k gate
pull-down, drain on `BLK_SPARE`, source on `GND`; on board A, a 10 k pull-up from `DOCK_SPARE` to `+3V3` beside `U27`;
`IF-AE-DOCK` (`pcb_interfaces.yaml`) names pin 12 for it. Regenerate both boards with parity and re-run their gates;
`check_contracts.py` compares the dock map (the alias `DOCK_SPARE`/`BLK_SPARE`). The registry's REQ-077 reads FAIL on
the generated boards until then (open item S-57 on main).

