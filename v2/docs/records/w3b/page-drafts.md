# Stream w3b: drafted text for pages this stream does not own

Why drafts: one owner per file. These pages state what board B's generator did not yet do; after w3b's merge they would
read wrong. The integrator applies each replacement to the file named, on the text as it stands at the merge (each OLD is
the text at main 38dcd764), and re-renders what is generated.

## 1. `v2/docs/feasibility/DECOUPLING.md`, section 10, row "G4 to G7, G10" (line 921 at 38dcd764)

OLD (the row's last sentences):

> Open: the classes. The round's author read `intent.py` as unable to carry them and filed the class of every declared
> capacitor in `v2/docs/records/r8b/decoupling-classes-b.json` (274 entries, intent `5af19ea259fba27b`); boards A, C, D, E
> and P now write `class` and `basis` into their intent from their own generators (T5's keys), and board B's generator
> does not yet, so B's classes stay in that record until it does. The seats wait for board B's next placement

NEW:

> The classes: board B's generator writes `class` and `basis` (with `value_floor` and `esr_max` on class L, `same_side` on
> class R) onto every declaration since stream w3b (27 September 2026), T5's keys as boards A, C, D, E and P write them, and
> an entry without a class stops it. They are the round's map (`v2/docs/records/r8b/decoupling-classes-b.json`) with four
> corrections, C65, C66, C508 and C509, which serve the SN74LVC1G08 gates U501 to U504 (class D, TI SCES217AA, where the map
> carried another part's clause and, for C508 and C509, class R), and three new class D entries, C72 to C74 at the LG290P's
> V_BCKP (W3B-F2); 277 entries (`v2/docs/records/w3b/evidence/`). The seats wait for board B's next placement

## 2. `v2/docs/handover/ENGINEERING-QUESTIONS.md`, EQ-19

In the row "Exact issue", after "B (28 supplies undeclared, 26 undecided)", add:

> ; board B's are declared since stream w3b (27 September 2026: 17 rails and 40 nodes, each from its maker's sheet, and
> PWR-001 read PASS of 59 in the stream's scratch on the candidate netlist, awaiting the consolidated re-take)

and in "Attempts and results", add:

> Board B (stream w3b): every one of the 28 undeclared and 26 undecided nets declared, a rail where it carries a current
> (VBAT, the three flashing VBUS, the SIM supplies, the GNSS antenna feed, the PoE port's feed and return conductors) and a
> node where it is one part's own supply or a signal (the fourteen bootstraps, the four CP2102N regulator outputs, the three
> STM32H743 VCAP, the resets, nRPIBOOT, the PWR-LED feeds, the RF pads, the PoE control lines); one more net, GNSS_RF_IN,
> became undecided once the antenna feed was declared and is declared too. Reading the TPS23861 and LG290P sheets for it
> found W3B-F1 and W3B-F2 (drawn) and S-48 to S-50 (open; numbers as the registry patch takes them).

## 3. `v2/docs/V2-SPEC.md` and `v2/docs/ARCH-PCB-B-IOHA.md`

Nothing: neither states the TPS23861's sense wiring, the V_BCKP decoupling or the SIM TVS as a fact the stream changes.

## 4. `v2/ecad/tools/gen_pcb_b3.py`, the board B class patterns (line 577 at 38dcd764)

W3B-R1 renames board B's coin-cell net VBAT to VBAT_RTC (board A's pack node is VBAT; `check_contracts` keys a rail by its
name and read the two as one conductor crossing A/B). The placement generator's class table matches the old name exactly:

OLD: `("VBUS*", "PWR"), ("GND", "PWR"), ("*_SW", "PWR"), ("VBAT", "PWR")]`

NEW: `("VBUS*", "PWR"), ("GND", "PWR"), ("*_SW", "PWR"), ("VBAT_RTC", "PWR")]`

Until it changes, the next placement gives VBAT_RTC the Default class (its current is at most 650 uA, so no width rule is at
stake, but the class is the project's statement that the net is power). The comments at lines 147, 232 and 488 name BT1's VBAT
land historically and need no change. The committed `pcb-b-compute.kicad_pro` carries `/VBAT` in its class assignments and
patterns until that placement rewrites it; an assignment naming a net the schematic no longer has matches nothing.

## 5. Tools (the tools owner): two readings this stream met

- `safe_lines.py <netlist>` writes `safe_lines.verdict.json` and `safe_lines_b.verdict.json` into the netlist's own `out/`
  directory even with `VERDICT_DIR` set (`out_dir` is computed beside the netlist at line 163 and the environment is read only
  on the board path at line 142), so running it on a tree's netlist writes that tree's evidence. The stream moved its two
  copies out of its worktree (`v2/docs/records/w3b/evidence/stray-safe-lines/`).
- `check_contracts.py` pairs two boards' rails by name alone (lines 634-653): a board-local net that shares a name with
  another board's rail reads as a crossing with no split. W3B-R1 removes the one case on the set; a check that the name also
  sits on a pin of a connector the two boards share would stop the next one.
