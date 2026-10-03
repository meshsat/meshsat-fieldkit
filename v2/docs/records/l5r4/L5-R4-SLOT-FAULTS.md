# L5-R4: a compute module lost while running, the panel firmware's finding F-14 (MESHSAT-1357, set 29, 3 October 2026)

Prototype design: nothing here has been built, powered or measured. Layer 5's round 4 decides one finding the panel firmware's author
raised after round 3 (`fnd/fw-r3` at `dea639a4`, its README's F-14) and writes the decision into the two files Layer 5 owns for the
panel: `v2/docs/PANEL.md` section 5 and `v2/docs/HW-FW-CONTRACT.md` (FW-C05, FW-C02, V-C05, the change record). Branch `fnd/l5r4` from
set 28's `92a5c7d8`. No requirement is changed and `CONOPS.md` is not edited: it is the source.

## 1. The finding

`CONOPS.md` section 4e's row "a compute module lost" recovers by "the slot is cycled once and then left off until the operator acts
(`PANEL.md` section 5)". `PANEL.md` section 5 triggered that cycle only for "a slot whose heartbeat stays flat for 60 s after its rail
came up", the start-up case. A module that stops while running was shown lost (FW-C05: 3 s without an edge; MASTER CAUT, F-07) and
never cycled. The firmware followed PANEL.md and waited on the decision.

## 2. The evidence, read in this order (the wiring from the generators and netlists, the behaviour from CONOPS and the requirements)

| Question | What decides it | What it says |
|---|---|---|
| How can the panel act on one slot? | the generators: `gen_sch_c.py` line 148 (GPIO13 to 15 are `SLOT_EN1..3`, GPIO10 to 12 `HB1..3`); `gen_sch_a.py` lines 1055, 1056 and 1088 (`SLOT_EN1` and `SLOT_EN3` enable the bucks `U4` and `U6`, `SLOT_EN2` the LM5176 `U5`, each a slot's 5 V) | the only per-slot control is the slot rail's enable; `PI_SHDN_REQ` reaches every module and `PI_KILL` the whole kit, so a cycle is `SLOT_EN` low and high again |
| What is a heartbeat? | `HW-FW-CONTRACT.md` section 2 (the netlist: `HB_CM1` is the module's GPIO16 through `Q105`, held high by `R158`) | liveness is the 1 Hz toggle, never a level; a dark module leaves its line high |
| When is a module lost? | FW-C05 | 3 s without an edge |
| What does the kit do for a lost module? | `CONOPS.md` section 4e, row "a compute module lost" | the bank moves to the neighbour (section 4c, 30 s); MASTER CAUT, the e-paper names the slot; the slot is cycled once and then left off until the operator acts |
| The same, during a mission | `CONOPS.md` section 3, M5 ("one compute module stops") | "a slot whose heartbeat stays flat for 60 s is power-cycled once and then left off until the operator acts (`PANEL.md` section 5)": the module that stops while running, with a 60 s flat window |
| The same, at start-up | `CONOPS.md` section 4, the Startup row | "a slot with a flat heartbeat after 60 s is marked faulty, cycled once, then left off" |
| The requirement | REQ-062 (parent NEED-03, source `PANEL.md` section 5) | statement: the start-up case (flat 60 s after the rail came up, power-cycled once with the rail off 5 s, then left off until the operator acts); acceptance: "a slot with its heartbeat forced flat is flagged ..., cycled once and left off; the other slots keep running", with no start-up condition |
| What the cycle must not disturb | REQ-004 and SC-25 (NEED-03) | the moved bank back in service within 30 s of the loss, the bridge within 60 s: both on the survivors, decided by the supervisors' vote on the heartbeat, not by the lost slot's rail |
| What a controller reset does to the slots | FW-C02 and record l8gnd section 3d (`records/l5r2/inputs/l8gnd-sections-2-3-226e9143.md`), the keeper `U43` with `R230` to `R232` (DRAFTED) | `SLOT_EN` is held at its last driven level across a watchdog, RUN, SWD or ROM-bootloader reset, not across a loss of the panel's supply; after a reset FW-C02 adopts the held level, then FW-C01's order raised every slot read low, a slot left off included |
| What survives which reset in the RP2040 | RP2040 datasheet (`v2/vendor/rp2040/rpi-rp2040-datasheet.pdf`) 2.12.7 and 4.7.4 | `CHIP_RESET`'s `HAD_POR` marks a power-on or brown-out reset, `HAD_RUN` a RUN reset; the watchdog's scratch registers survive a soft reset but are cleared by RUN or by cycling the digital supply, so the slot state is kept where the wipe-pending record is (FW-C01 step 3, the flash) |

CONOPS governs: section 4e, M5 and the Startup row all give one cycle, a 60 s flat window and the operator; M5 applies it to a
module that stops during a mission. PANEL.md section 5 had narrowed it to start-up. REQ-062's statement names the start-up case and
its acceptance does not restrict the forced flat heartbeat to start-up: the rule below meets both, so no requirement is restated
(layer 3 stays accepted).

## 3. The rule, as written in PANEL.md section 5 (and in FW-C05)

> **Slot faults, one rule for a module lost at start-up and one lost while running** (decided 3 October 2026, finding F-14 of the
> panel firmware, record l5r4, SESSION; the source is `CONOPS.md` section 4e's row "a compute module lost", with section 3's M5 and
> section 4's Startup row: the slot is cycled once and then left off until the operator acts). A slot is supervised while its
> `SLOT_EN` is high and the controller has asked nothing of it: no shutdown on `PI_SHDN_REQ`, no hot stop (FW-C13), no shed to the
> reduced mode or the heat stage (FW-C09), no ZEROIZE (section 6). It is lost when its heartbeat has had no edge for 3 s after an edge
> (FW-C05), or when it stays flat for 60 s after its rail came up; either way it is shown as a slot fault (MASTER CAUT, the e-paper
> names the slot). When a supervised slot's heartbeat has had no edge for 60 s, counted from its rail coming up or from its last edge,
> whichever is later, the controller acts on its rail: the first time it power-cycles the slot once (rail off 5 s), which spends the
> slot's one retry; the next time, whether the slot stayed flat after its cycle or came back and was lost later, it drops `SLOT_EN`
> and then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol (owed with
> MESHSAT-837; the panel firmware's F-02 and S-04), or by restarting the kit with MAIN, after which every slot is raised again
> (decided 3 October 2026, F-09, record l5r2, `L5-PANEL-R3.md`: the sentence named no control); each of the three re-arms the slot's
> retry. A controller reset (watchdog, RUN or SWD) is not an operator act: the controller keeps each slot's spent retry and left-off
> state where it keeps the wipe-pending record and after the reset raises only the slots that state allows (FW-C02); a power-on
> reset of the controller (`HAD_POR`, RP2040 datasheet 2.12.7, a power-on or a brown-out), which a MAIN restart or a loss of the
> panel's supply causes, clears it with every slot. A module that restarts on its own (its software, or a restart the bridge
> commands) is not told apart: it is cycled if it shows no edge for 60 s; a bridge message that suspends the supervision for a
> planned restart is owed with MESHSAT-837.

In short: **how many cycles:** one per slot, its retry; **the hold-off:** 60 s without a heartbeat edge, counted from the later of the
rail coming up and the last edge, the same in both cases; **what ends retries:** the retry is spent by the cycle and re-armed only by
an operator act (the touch UI, the bridge's retry command, MAIN); a second loss leaves the slot off; a controller reset neither
re-arms nor clears it, a power-on reset clears it.

## 4. The decision (authority: SESSION, under the owner's standing rule of 26 September 2026; finding F-14)

- **Why one rule.** CONOPS M5 gives the cycle to a module that stops during a mission; the hardware gives the panel one way to act on
  a slot, its rail; a hung module is the case a power cycle recovers, whether it hung at boot or after hours. Leaving the running case
  uncycled would leave the kit one module short for the rest of an unattended mission (M1, 72 hours) when one cycle could restore it.
- **Why 60 s from the last edge.** It is the window CONOPS and REQ-062 already give the start-up case, so a module that restarts on its
  own gets the time a cold start gets; it is longer than REQ-004's 30 s bank move, which the supervisors decide on the heartbeat, so
  the cycle never acts while the bank is still moving.
- **Why one retry until the operator acts.** CONOPS and REQ-062 both bound the automatic action to one cycle and hand the slot to the
  operator; no requirement asks for repeated unattended recovery; NEED-03 is met by the bank's move, not by the cycle; and a module
  that fails again after its cycle (a short on its rail, FAB-02's back-power into an unpowered module) is not cycled again unattended.
- **Why kept across a controller reset.** With the keeper (FW-C02) a controller reset leaves running slots up; without the kept state
  FW-C01's order would raise a slot left off, which is an automatic retry by another path.
- **Rejected:** a re-armed retry after a stable run (for example 30 minutes, as the hot stop's restore), because it would give more
  than CONOPS's "cycled once" and REQ-062 states once; it is the change to bring if the owner wants unattended repeated recovery.
- *Reverse:* revert this round's commit; `apply_l5r4.py`'s old texts are the round 3 sentences it asserts.

## 5. What changed

| File | Change |
|---|---|
| `v2/docs/PANEL.md` section 5 | the start-up-only sentence replaced by the rule of section 3 (one sentence block in the boot bullet) |
| `v2/docs/HW-FW-CONTRACT.md` FW-C05 | the rule in the obligation column; the why column cites CONOPS sections 3 (M5), 4 (Startup) and 4e, REQ-062 and F-14; the state "DRAWN; the slot-fault rule FIRMWARE (F-14)" |
| `v2/docs/HW-FW-CONTRACT.md` FW-C02 | "then FW-C01's order applies to every slot read low that FW-C05's slot-fault state allows (a slot left off stays off across the reset, F-14)" |
| `v2/docs/HW-FW-CONTRACT.md` V-C05 | both cases on the bench: a running slot's bridge stopped, cycled 60 s after its last edge, left off 60 s after its rail came back, off across a watchdog and a RUN reset; a slot flat from its start the same way; the three operator acts re-arm |
| `v2/docs/HW-FW-CONTRACT.md` change record | the row "2 (L5-R4)" |

Every sentence other records and tests read stays: the firmware's constants "stays flat for 60 s", "rail off 5 s" (PANEL.md) and
"declare it lost after 3 s without an edge" (FW-C05), round 3's F-09 excerpt ("then leaves it off until the operator acts: from the
touch UI, by a retry command over the bridge protocol"), section 5's HDMI encoding and section 9's MASTER CAUT and MASTER WARN lists.

## 6. The requirements registry (the integrator's file)

Five readings are bound to PANEL.md's content (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016); none rests on section 5.
`apply_l5r4_rebind.py` rebinds them, refusing if any section other than 5 differs or if a section a reading rests on differs;
`--check` on this branch rebinds all five from `9fd2b4e3c6edf86e` with every evidence_result unchanged. It is run by the integrator.
REQ-062 is not edited (layer 3 accepted; its statement is the start-up case of the rule and its acceptance is met by it).

## 7. What the panel firmware must change (for its author, the next round)

1. `slots_policy` in `panel_core.c`: a slot in `SLOT_RUNNING` whose heartbeat has had no edge for `PANEL_SLOT_FLAT_MS` since its last
   edge, while it is wanted and no shutdown, hot stop, shed or ZEROIZE is asked of it, takes the same branch as `SLOT_WAIT_HB`'s
   timeout: cycle once if `cycled` is false, else `SLOT_FAULT_OFF`. The timer runs from the later of `since` and `hb_edge`.
2. The slot fault shows at the loss: the 3 s loss of a running slot pushes `EV_SLOT_FAULT` (MASTER CAUT, the e-paper names the slot),
   not only the 60 s start-up timeout.
3. `cycled` is re-armed only by `panel_slot_operator_retry` (the touch UI and the bridge's retry) and by a power-on reset; it is never
   cleared when a cycled slot comes back.
4. `cycled` and `SLOT_FAULT_OFF` per slot are written beside the wipe-pending record and read at boot: after a watchdog, RUN or SWD
   reset (`HAD_POR` clear) a slot recorded off stays `SLOT_FAULT_OFF` when FW-C02 reads its line low, and a slot read high keeps its
   spent retry; after a power-on reset the record is cleared.
5. The constants stay (`PANEL_SLOT_FLAT_MS` 60000, `PANEL_SLOT_CYCLE_OFF_MS` 5000, `PANEL_HB_LOST_MS` 3000); a host test per case
   (lost at start-up, lost while running, lost again after a successful cycle, a controller reset with a slot left off, a power-on
   reset) cites FW-C05; the README's F-14 is closed against this record.

## 8. Checks

`test_l5r4.py`: CONOPS (4e, M5, Startup) and PANEL.md section 5 agree (the same hold-off parsed from each, one cycle, the rail-off
time, the operator), PANEL.md covers the running case and cites CONOPS; FW-C05 states the same figures and FW-C02 keeps a slot left
off; REQ-062's case is in the rule; `apply_l5r4.py` reads already applied on the tree, applies once to the files at `92a5c7d8`, is
idempotent and refuses a mixed state; the rebind script checks or reads already applied; no dash in the record.

## 9. What this record does not claim

Nothing is implemented or tested on hardware: the rule is a contract for the firmware, whose code still follows round 3 until its
author's next round. The bridge's message that would suspend supervision for a planned restart is not defined (MESHSAT-837).
