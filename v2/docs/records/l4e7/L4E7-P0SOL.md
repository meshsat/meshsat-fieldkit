DONE: both failing cases reproduced on e132db0e; three alternatives compared; (C2) selected, drafted, composed in L4-E9's order, netlist-checked with four failing mutations; D-16 CORRECTED (one PROVISIONAL energy term); D-10 NARROWED and OPEN (U5 and INP corrected, the guard's port-level residual left with route B2 and the narrowed P1-1). NOT DONE: an independent check; the record's cache re-key (a box recompute). NEXT: the coordinator's merge, the L4-E9 rows below, the focused check.

# P0-7: the solar stage's D-10 (a stiff source with the guard on) and D-16 (the input sense out of range) by circuit alternatives

MESHSAT-1357, task P0-7 of the owner's P0 instruction of 5 October 2026 (part 15, sections 3 to 6; part 19, the scope
amendment). Branch `fnd/p0sol` from `fnd/p0base` at `e132db0e`. Prototype design, desk arithmetic: nothing is bought, built,
powered or measured, and no generator, registry or page outside this record is edited. Every figure is printed by
`l4e7_p0sol.py` into `l4e7_p0sol.out`; its bases are PRINTED LIMIT, TYPICAL, MEASURED (none exists), ASSUMPTION, MODELED,
INFERRED, SESSION, NETLIST and CATALOGUE. The lead-inductance method is ended: no loop is searched and none is claimed to pass;
the record's own transient model runs only at its 3.30 uH reference loop and at the envelope's ends, to check a changed circuit
against the same failure case.

## 1. Both failing cases reproduced on the base (the .out's section 0)

- The record's results cache: its KEY does not hold on this base, and the only differing input is
  `v2/docs/records/l4e11/l4e11_power.out` (L4-E11's rounds 12 to 16). The six figures `l4e7_stage_settings.py` reads from it
  (UVLO rising and falling, the start's slew, INP, the short-circuit and overcurrent thresholds) are equal in the cached version
  (set 29's freeze, `69921ce8`) and in this base's, so the cached results are this base's results. The cache is NOT re-keyed
  here: the record's own recompute takes 30 to 50 core-minutes and belongs on a rented box (the integrator's). Until then the
  record's tests, which read the cache through `results()`, recompute.
- `render(cache)` is byte-identical to the committed `l4e7_stage_settings.out`.
- **D-16**, recomputed by the record's own `sense_ripple` on its cached parameters: equal to every cached figure. At the 25 V
  corner RSENSE1's resistive peak is 0.1174 V at the regulation's highest current, the pins -0.1866 to +0.1863 V, and M1's 10 ns
  edges put -0.4329 V on them (past the -0.3 V absolute maximum).
- **D-10**, recomputed by the record's own `guard_event_b` with every ceramic bank rebuilt from Samsung's held curves at the
  record's bounds (60 events at the 3.30 uH reference loop): U5 0.2493 V resistive with the numerical error, the pins' complete
  budget -0.3021 to +0.2591 V at a connector fault and -0.2884 to +0.2486 V at the far end; equal to the cache. The cold
  connection at 0.30 uH: PV_F 84.62 V, slew 56.10 V/us, INP 18.54 V.

## 2. The comparison (at most three alternatives; the .out's section 1)

Both defects have one cause: RSENSE1 puts U5's own input amplifier (pins rated -0.3 to +0.3 V absolute, -100 to +100 mV
operating) in the path of currents nothing bounds on printed figures: the charge a stiff source pushes into the capacitance
behind it (D-10) and M1's pulsed draw (D-16).

| | Alternative | Fault case (D-10) | Normal case (D-16) | M2 (CS101, the accepted model) | Verdict |
|---|---|---|---|---|---|
| A | RSENSE1 ahead of every bank (route 3's wider form, R-187) | worse: U5 0.956 V resistive at 3.30 uH (3.2 times its absolute maximum) | meets: the flat input current, 0.045 V | fails: the loop holds the port current and pushes the bulk's CS101 current through the bank, 0.33 A filtered against 0.113 A | rejected |
| B | the guard-on event bounded or removed at the port: B1 a series choke (XAL1510-103), B2 a presence contact pair on the solar receptacle carrying U21's INP | B1: the cut current 31.1 A exceeds the choke's 26.3 A Isat; B2: removes the event for a source in the receptacle (any arrival is a cold connection) | untouched | B1: a resonance at 2.7 to 3.2 kHz inside M2's decided band | B1 rejected; B2 the route for D-10's port residual (needs Layer 7) |
| C | U5's input sense retired (CSPIN and CSNIN tied to VIN, 8705af p.12, p.29, p.31); the regulation fed into IMON_IN by an INA169 | U5 0 V by construction at every loop | U5 0 V by construction | depends on the sense point: C1 at R87 (U21's IMON) fails like A; C2 on the backstop's bank passes; C3 on RSENSE1 keeps the accepted topology | **C2 selected** |

**The selection (SESSION, the owner's rule: the simplest supported correction with useful margin and the fewest new uncertain
dependencies): C2.** U23, a second INA169 (U18's part, TI SBOS181F), sits on the backstop's bank R60 to R64 and drives U5's
IMON_IN into RIMON_IN R16 (34.0k) and CIMON_IN C65; RSENSE1 (R59) and the net TRK_VIN are removed; R97 becomes 24.9k for INP.
Why C2 over C3 (U23 reading the kept RSENSE1): C2's average does not depend on the INA169's typical-only bandwidth (C3 reads
+0.09 % high at the typical bandwidth but +7.1 % at ten times it and +10.1 % if it followed every edge; C2 at most +1.34 %), and
its CS101 margin is larger. C2's price, stated: the regulation and the 100 W trip share the bank, so a short across the bank,
which already defeats the trip (the record's single-fault list), now also defeats the regulation, which was never credited for
the 100 W bound. **Reversal:** to C3 (the same draft with U23 on R59's pads and R59 kept) if Layer 8's fault analysis rules the
shared shunt out; to the drafted A7 arrangement only with a measured or maker-stated bound keeping U5's pins inside +-0.3 V for
the declared envelope.

## 3. The selected circuit on both cases (the .out's section 2)

- **Composition, netlist, mutations (2a).** Board E's generator composed in L4-E9's change-list order with
  `apply_gen_sch_e_p0sol.py` after the solar guard (R-173) and before L4-E11's aux (R-177): all sixteen drafts apply, the draft
  refuses a second application, and the generator runs to its end (record l8p's `gen_netlist.py`, 296 parts). Nine predicates
  on the changed nets hold (U5's pins 32, 33 and 34 on one net; no R59 and no TRK_VIN; U23 on the bank's pads as U18; U23's
  output on IMON_IN with only R16 and C65; R16 34.0k and R97 24.9k; C79; M1's drain and every input ceramic on U5's input; U18
  and the trip unchanged). Four mutations (CSNIN on its own net, U23's VIN- off the bank, R59 restored, U23's output elsewhere)
  each fail the check. d8dec31's input capacitor still takes C149.
- **The fault case, D-10 (2b, 2c).** U5's CSPIN to CSNIN is 0 V in every state (NETLIST; a layout obligation for board E's
  constraints: pins 32 and 33 joined to pin 34 at the package by a trace that carries only their bias current, U23's Kelvin pair
  from the bank's pad centres beside U18's). On the record's model with RSENSE1's
  branch tied, at the reference loop every listed rating holds its line except PV_F against the TPS4811-Q1's recommended 80 V
  row (83.48 V; L6P-F10, unchanged): the bank's differential 0.483 V (corner search 0.548 V) of U18's and U23's 1.8 V line, INP
  16.67 V with R97 24.9k, Q12's VDS 74.85 V, TRK_VS 29.14 V, D4 no current. INP with R97 24.9k stays under 18 V for every PV_F up
  to 90.1 V, so it can no longer fail where PV_F holds; the cold connection's INP becomes 16.90 V. U21 now turns on by 10.05 V
  at the most (over the stage's own 9.5 V enable, under the hold's least 16.97 V: no operating point lost). IMON_IN stays under
  its 5 V absolute maximum at every loop listed (at most 3.40 V, a linear charge bound). At the envelope's least loop the port's
  own ratings still fail (PV_F 321.9 V; the bank 2.57 V over the INA169s' 2 V): D-10's port-level residual.
- **The normal case, D-16 (2d).** The periodic model written out reproduces the record's `sense_ripple` exactly, then takes the
  selected network: at the 25 V corner the bank's current never reverses (at least 0.43 A); U23's sense spans -167 to +165 mV
  with the bank's inductance at 5 nH unshared, its average inside the INA169's printed 10 to 150 mV rows and its peaks inside
  its 500 mV full scale; the negative inductive spikes it cannot follow make it read high by at most +1.34 %, so the regulation
  errs to a lower input current, never toward the trip. U5's operating range is met by construction. **D-16: CORRECTED.**
- **The regulation (2e).** On printed rows (EA2's 1.187 / 1.208 / 1.229 V and the record's design floor; the INA169's gm,
  nonlinearity, offset, CMR and PSR): nominal 2.5378 A, highest 2.9212 A, lowest 2.1839 A (the drafted A7 regulation: nominal
  2.5485 A, highest 2.9337 A). The trip reads the same bank, so the bank's tolerance, TCR, aging and heating cancel: the margin
  to the trip's least is 0.3645 A at its least over the input range (the accepted design's independent margin 0.1130 A). The
  record's trip reproduces exactly.
- **M2 (2f).** On the record's own CS101 model (reproduced over its 121 frequencies to 0): the filtered peak 0.1093 A at 1714 Hz
  against 0.3645 A, the loop branch's room 3.17 times its typical model (the accepted design: 0.0585 A against 0.1130 A, room
  2.51). HOLDS, CONDITIONAL on the typical loop rows as before.
- **The start, ratings, window (2g).** The start puts at most 1.762 A through the bank; U23 then holds IMON_IN at most 0.93 V,
  under its 1.55 V fault threshold. U23 sits on U18's nets pin for pin, so every rating the record gives for U18 holds for U23.
  RSENSE1's 0.133 W is gone. The 100 W bound, re-run: U23's VIN+ pin takes its output current and its input bias (the record's
  SESSION 1 mA) from ahead of the bank, as U18's does, so the static bound rises from 93.5521 W to 93.5783 W, and check (b)'s
  response allowance (C79's charge added) falls from 1.087 ms to 1.052 ms, still over the required 0.401 ms. The hold, the
  cut-off's band, the trip itself, REQ-016's window and D4 are unchanged.
- **The one new unprinted term (2h), PROVISIONAL under the scope amendment.** A7's own output with CSPIN = CSNIN: the sheet
  prints no current out of IMON_IN for a negative differential and no figure at zero; any current A7 sources lowers the
  regulation (about 3 % per uA), away from the trip. That it cannot sink is read from that text (INFERRED); a sink would raise the
  regulation, and the correlated margin falls to the accepted design's 0.1130 A only at 3.67 uA. Bounded provisional choice: the
  band above with A7 at 0 uA. Validation: item S3 of `SUPPLIER-P1-1-P0SOL.md` (five parts, 16 V and 25 V, -20, +25, +62 C, pass
  from -0.5 uA sinking to +1.0 uA sourcing); the question to Analog Devices is drafted,
  `clarification/analog-devices-lt8705a-p0sol.txt` (item 8), UNSENT.

## 4. What stays open, exactly

**D-10's port-level residual** (the guard's own transient, not U5): a stiff source stepping onto the port with the guard on
charges every capacitor behind Q12 at a rate only the source's loop sets. At the envelope's least loop PV_F, Q12's VDS, INP, EN,
D4, TRK_VS and the bank's two INA169s exceed their ratings; at the reference loop PV_F stays over the recommended 80 V row (under
it from 4.03 uH, L6P-F10). No arrangement with the guard closed bounds that charge without a series element (B1, not supported
on printed figures) or the event's removal (B2). **The cold connection** keeps 56.1 V/us at a connector fault on the least loop,
inside its 60 V/us absolute maximum, over the 54 V/us SESSION margin line (held from 0.53 uH). Both are PROVISIONAL under the
scope amendment, with the exact next actions:

1. **Route B2 (a desk route needing a Layer 7 decision):** the solar receptacle gains a presence contact pair that every plug
   for it bridges (the panel lead and any lead made for the receptacle); U21's INP divider is fed through it, so the plug's
   withdrawal pulls INP low and any arriving source is a cold connection (BST and OV hold Q12 off; the record shows the cold
   connection's absolute ratings held). The coordinator brings it forward as a named prerequisite of Layer 4's power gate (a
   Layer 7 decision on the receptacle; R-180 rewritten from a loop bound into a contact requirement), then a board E draft moves R96's top onto the contact. It does not cover a
   second stiff source added on the same lead while a panel is connected.
2. **The narrowed supplier request** `SUPPLIER-P1-1-P0SOL.md` (UNSENT): S1 the guard-on step (three specimens, 0.30, 1.0 and
   3.3 uH measured loops, three start voltages, two loads, five steps; PV_F under 80 V, INP under 18 V, slews under 54 V/us, the
   bank under 1.8 V, U5 under 10 mV), S2 the cold connection, S3 A7 at zero differential, S4 the regulation at 25 V.

## 5. Rows for L4-E9 and the register (the coordinator's; nothing of L4-E9's is edited here)

- **D-10** (8a and 8c): "NARROWED. U5's absolute-rating violation CORRECTED by P0-7's draft (R-NEW): CSPIN and CSNIN tied to VIN,
  0 V at every loop; INP's margin line CORRECTED by R97 24.9k (INP under 18 V for PV_F to 90.1 V). OPEN: the guard-on event's
  port-level residual (PV_F, Q12's VDS, EN, D4, TRK_VS, U18 and U23 below the port's floors; PV_F over the recommended 80 V row
  at 3.30 uH, L6P-F10) and the cold connection's slew margin line under 0.53 uH; next: route B2 at Layer 7, or P1-1 narrowed."
- **D-16** (8a and 8c): "CORRECTED in draft by P0-7 (R-NEW): U5's input sense not used (0 V by construction), the regulation's
  sense U23 on the bank, its average at most 1.34 % high (the safe side); PROVISIONAL in A7's zero-differential output (sourcing
  lowers the regulation; a sink, excluded by p.31's text, INFERRED, is covered up to 3.67 uA; S3)." B6-ENG-2 is answered at the desk; B6-ENG-1 narrows to the port.
- **IF-01:** the D-10 text above; "U5's pins" leaves the NOT MET list. **IF-02:** "the regulation 2.5378 A nominal, 2.9212 A
  highest (U23 on the bank, R16 34.0k); the margin to the trip 0.3645 A, correlated; the static bound 93.5783 W (U23's VIN+
  currents added) and check (b)'s allowance 1.052 ms; A7 at zero differential PROVISIONAL".
- **The change list (section 3), a new row R-NEW** after R-173 and before R-177: "board E, gen_sch_e.py,
  `apply_gen_sch_e_p0sol.py` (13 edits): R59 and TRK_VIN removed, U5's pins 32 to 34 on TRK_VS, U23 INA169 (C44322) on the bank
  into IMON_IN with C79, R16 34.0k (C705770), R97 24.9k (C136967); AFTER the input limit, the backstop and the solar guard;
  DRAFTED (not applied)". **R-20** (the input limit): its R59 and TRK_VIN superseded by R-NEW, R16 and C65 kept. **R-173**: its
  R97 superseded by R-NEW. **R-187** (route 3): "worked to the circuit by P0-7: alternative A rejected (D-10 worse, M2 fails);
  the sense arrangement changed instead (R-NEW)". **R-189** (B6-ENG-2's bench): replaced by S4 (the regulation at 25 V) and S3.
  **R-186** (a sense-pin filter): obsolete under R-NEW. **R-176 row 3**: U5's +-0.240 V line replaced by U5 under 10 mV (layout
  check); the port's rows stay. **R-180**: rewritten to route B2's contact requirement if the coordinator selects it. **P1-1**:
  narrowed to `SUPPLIER-P1-1-P0SOL.md`.
- **For other authors:** Layer 8's single-fault table (the record's "defeat" list) gains "a short across the sense bank now
  defeats the regulation as well" and "U23's output stuck high stops the stage (IMON_IN fault), stuck low leaves the regulation
  open, the trip unchanged"; record l9t5 and the energy budget: U23's supply at most 4.0 mW, RSENSE1's 0.133 W removed; Layer
  6's components: C705770, C136967 and a second C44322.

## Files

| File | What it is |
|---|---|
| `l4e7_p0sol.py`, `l4e7_p0sol.out` | the reproduction, the comparison, the selected circuit on both cases, the composition with its netlist check and mutations, the verdicts (about 70 s; the output through regen_out.py) |
| `apply_gen_sch_e_p0sol.py` | the DRAFT for board E's generator (13 edits; refuses a generator without the input limit, backstop and solar guard drafts, a second application, and the tree's generator until a RELEASE.md names an accepted check) |
| `SUPPLIER-P1-1-P0SOL.md` | the narrowed supplier request, UNSENT |
| `clarification/analog-devices-lt8705a-p0sol.txt` | item 8 for Analog Devices, UNSENT |
