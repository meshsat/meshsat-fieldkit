# EQ-16 / R8E-N01: how VIN_RAW crosses the dock (board E stream w3de, 27 September 2026, MESHSAT-1357)

A session decision under the owner's standing rule of 26 September 2026, recorded for the integrator and for the owners
of the files it touches outside board E. Desk arithmetic only: nothing of the V2 kit has been built, ordered, powered or
measured. The numbers are `drafts/w3de/dock_contacts.py`'s output; every input is a maker's document held in this tree
or a declaration in a generator.

## 1. The question

Board E declares VIN_RAW at 14.10 A typical and peak since round 8 (R4A-N12, `gen_sch_e.py`): board A's front end at
its ISNS limit (5.7 A at 20.7 V over 0.93, SNVSAI1D VSNS 57 mV maximum) drawing from a 9.0 V bus, which the vehicle
entry (at most 6.15 A, the LM5069's VCL maximum over 10 mOhm) and the panel tracker (10.33 A, the panel's 93 W at 9 V)
can supply together. The bus crossed the dock on four Preci-Dip 813 spring contacts (board A's J_DOCK pins 1 to 4, E5's
targets, four 24 AWG wires to board E's J_BLK lands 1 to 4): 3.53 A each with even sharing against the maker's
"OPERATING CURRENT Max. 3.5 A", 101 percent at nominal (R8E-N01) and 4.70 A with one of the four open (R4A-N13).

## 2. What the makers' documents give

| Contact | Current | Resistance | Temperature | Held at |
|---|---|---|---|---|
| Preci-Dip 813 (S1, 2.54 mm, double row, music-wire spring) | "OPERATING CURRENT Max. 3.5 A" (p.34) | "10 mOhm (static measurement, halfway position)" (p.34) | "-55 ... +125 C (-55 ... +85 C with music wire spring)" (p.31); spring "Music wire DIN 17223, gold plated" (p.34) | `v2/vendor/precidip/precidip-813-spring-loaded-connector-pages-31-34.pdf` (sha256 d630c8a9) |
| Mill-Max 085x power spring pin (the 0858 class board A's J_CP and J_CN use) | "Rated Current (Free air): Continuous 9 amps @ 10 C temperature rise" (page 28) | "Contact Resistance: 20 mOhm max" | "Operating temperature range: -55/+125 C" | `v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf` |

**Temperature derating from the maker sheets.** Preci-Dip publishes no current-temperature curve and no rise at 3.5 A:
the only temperature statement is the 85 C limit of the music-wire spring. The rating therefore cannot be shown at desk
to hold at the envelope's 51 C inside air (the bar `part_temps.py` resolves from `pcb_envelope.yaml`: +35 C with three
modules +16 K, +40 C with one module +10 K) or at the +55 C qualification margin (owner ruling D-02a; 65 C inside in the
reduced mode). `dock_contacts.py` bounds it with a stated assumption: the 3.5 A rating read at a 25 C reference cannot
put the contact above its own 85 C, so its rise at 3.5 A is at most 60 K, scaled as I squared. Mill-Max states its rise:
10 K at 9 A, scaled the same way. As a screen, ECSS-Q-ST-30-11C Rev.2 Table 6-10 (connectors: 50 percent of the rated
current, 30 C below the maximum rated temperature; transcription owed, the clause read from the ECSS PDF of sha256
10cf7066, the same file `v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md` already cites for 6.17): 1.75 A and
55 C for the 813, 4.5 A and 95 C for the Mill-Max pin. A space screen, reported as the fuse screen is, never a limit
this project claims the standard sets.

## 3. The options, with the one-open-contact case

| Option | Per contact, even | One open | 2:1 spread, one open | Contact at 51 C / 65 C air (one open) | Verdict |
|---|---|---|---|---|---|
| Four 813 (as drawn) | 3.53 A, 101 % | 4.70 A, 134 % | 7.05 A | 159 / 173 C | over the rating at nominal |
| Five 813 (the spare pin 12 joins) | 2.82 A, 81 % | 3.53 A, 101 % | 5.64 A | 112 / 126 C | fails one open |
| Eight 813 (a 2x8 813, 813-S1-016-10-016101) | 1.76 A, 50 % | 2.01 A, 58 % | 3.53 A, 101 % | 71 / 85 C even, 112 / 126 C at the spread | holds only with even sharing, on an assumed rise; the maker bounds neither |
| Four Mill-Max 0858-class pins (TAKEN) | 3.53 A, 39 % | 4.70 A, 52 % | 7.05 A, 78 % | 54 / 68 C even, 57 / 71 C at the spread | holds with margin on the maker's own rise |
| Hardware input-current bound | | | | | see below |
| Reduced declared maximum | | | | | see below |

**A hardware bound on board E** cannot bound the bus while the vehicle holds it: board A's front end sets the demand,
so limiting the tracker (its LT8705A output loop needs an output sense resistor and IMON_OUT) moves the current to the
vehicle path until the hot-swap limits and retries. **A hardware bound on board A** (its front end's input current) at
the 10.5 A three contacts carry would cut the front end's input from 127 W to about 95 W at a 9 V bus, and at 3.5 A
with the temperature bound (2.6 A per contact, three carrying) to about 71 W: a narrowing of the vehicle and solar
charging function, which the owner's rules forbid, and a board A change either way. **A reduced declared maximum**
cannot be justified from the input path: at a 9.0 V vehicle measured at the connector the bus sits about 0.2 V lower and
the same state is 14.4 A, so 14.10 A is not an upper bound either. The host's IIN_HOST limit is firmware and does not
meet the rule (EQ-16's own text).

## 4. The decision (a session choice, under the owner's standing rule of 26 September 2026; apply_registry.py takes the next free SC-nn)

**VIN_RAW crosses the dock on four Mill-Max 0858-class power pins with four more for its return, as the pack's CELL+
does; the four Preci-Dip 813 contacts that carried it become ground.**

- Board A: J_VR1 to J_VR4 on VIN_RAW and J_VN1 to J_VN4 on GND (the MMPIN land); J_DOCK pins 1 to 4 on GND; VIN_RAW's
  declared source the four power pins, and board A declares board E's 14.10 A (R8E-N01; the hunk was optional in pass 1
  and is unconditional since pass 2, so both ends of IF-AE-DOCK carry one figure). Drafted: `patch_gen_sch_a_dock.py`,
  and delivered as ready files in `a-half/` (installed by `a-half/install_a_half.py`, every file's sha256 asserted before
  and after): regenerated on the KiCad box with main's chain (`handover_exports.py regen --letters a`), whose run on
  main's own extraction reproduced main's committed files, the netlist differs from main's only by the eight pins,
  J_DOCK pins 1 to 4 (VIN_RAW to GND) and J_DOCK's value text (`parity/a-draft/`).
- Board E (drawn in `gen_sch_e.py`): P_VR (VIN_RAW) and P_VN (GND), the pack pads' 12 AWG land; J_BLK pins 1 to 4 on GND;
  VIN_RAW's load P_VR.
- E5 (for its owner, `gen_pcb_e5.py`, layer 7): eight Mill-Max targets under board A's new pins, a 12 AWG wire hole for
  each of P_VR and P_VN, a VIN_RAW pour and a return pour, and the 813 targets 1 to 4 on their new net. The block is 43 x
  26 mm with nine power targets and a 2x6 signal field today; eight more targets at the 4.0 mm pitch need about 16 x 10
  mm, so the block grows or its field is re-laid. Whether board A's underside and the strip give that room is the open
  layer 7 item this decision rests on (EQ-08's class).
- IF-AE-DOCK (`patch_interfaces_if_ae_dock.py`) and `check_contracts.py` (`patch_check_contracts_dock.py`: four VIN_RAW
  pins and four return pins on A, P_VR and P_VN on E, no VIN_RAW on any 813 contact).
- Board E's placement (`patch_gen_pcb_e3.py`): P_VR and P_VN need FIXED places under E5's new holes; the draft leaves a
  marker that stops the placement until they are chosen.
- `v2/docs/ARCHITECTURE.md` (for its owner, not drafted here): its IF-AE-DOCK lines, the E5 arrow ("4 x VIN_RAW (12.31 A
  declared)"), the "VIN_RAW at the dock" row of its current table (the four 813 contacts at 3.08 A) and the interface
  table's IF-AE-DOCK row, describe the dock as it was; at the integration they read VIN_RAW on J_VR1 to J_VR4 and
  J_VN1 to J_VN4 at 14.10 A on both boards, and the 813 contacts 1 to 4 on ground.

Proved at desk: with both halves regenerated (A from the draft, D and E from this worktree), `check_contracts.py` with
the drafted checks reads PASS 99 of 99 (A 34, E 14), and the drafted checks read FAIL on main's netlists (the negative
control). **The two halves land in ONE integration** (pass 2 of the independent check): board E's half alone reads the
dock map check FAIL, DIFFERENT on pins 1 to 4 (A VIN_RAW, E GND), which would commit board A's VIN_RAW joined to board
E's GND across four 813 contacts; `apply_registry.py` refuses to rebind unless board A's regenerated files are in the tree
beside D's and E's, and rebinds board A's five records (CON-018, CON-019, CFL-005, CFL-014, CFL-016) with them.

**Why this one.** It is the only option that meets the nominal case, the one-open case and the temperature question on
figures the makers publish, without narrowing a function: the power pins' rating is stated with its rise, the 813's is
not. It is also the design's own pattern: the pack's 10 A and 18 A cross the same dock on the same pins.

**Reverse by** a Preci-Dip current-temperature derating for the 813 that carries 14.10 A on a count of contacts that fits
the block with one open inside 85 C, or by a layer 7 finding that the block cannot carry eight more power targets, in
which case the fallback is the 2x8 813 with eight VIN_RAW contacts and a bench measurement of their sharing before the
kit is powered.

## 5. The return beside it (finding W3DE-DOCK-R1)

The ground current from A to E shares every ground contact of the dock: the Mill-Max return pins behind their pours and
12 AWG wires and the 813 ground contacts behind their 24 AWG wires, in the ratio of the two groups' resistances, which
the makers bound only from above. **As drawn before this decision** (4 CN pins and 4 x 813 GND), with every Mill-Max pin at
its 20 mOhm maximum an 813 ground contact carries 3.06 A at 24.1 A of ground current (VIN_RAW's 14.10 A and the pack's
10.0 A) and 4.08 A at 32.1 A (the pack's 18.0 A peak): 88 and 117 percent of 3.5 A, a finding that stood unmeasured
beside R8E-N01. **With the decision** (4 CN, 4 VN, 8 x 813 GND) the same case is 1.57 and 2.09 A, 2.24 A with one 813
open (64 percent). The coincidence of both currents at their maxima is the conservative bound, not an operating point.
Residual: at the +55 C margin, the 32.1 A peak and the Mill-Max pins at their maximum, an 813 ground contact reaches 86
to 90 C on the assumed rise, over its 85 C. Owed to TEST-PLAN.md: the dock's contact resistances (each group) and one
813 ground contact's temperature at the declared currents.

## 6. What this does not claim

No contact has been measured. The 813's rise is an assumption bounded by its own temperature limit; the sharing is
bounded by the makers' maxima; the E5 layout is not drawn. Nothing here is a qualification result.
