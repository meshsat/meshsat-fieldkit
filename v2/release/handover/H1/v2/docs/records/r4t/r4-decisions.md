# r4t decisions and results (MESHSAT-1357 round 4, shared helpers and checks, 26 September 2026)

Author: r4t. Worktree `fnd/r4t`, fast-forwarded in round 6 from main 82dd1e4d to main faf8c981, in round 6's fourth
pass to main 458b2873 and in its fifth pass to main 01469100 (none of r4t's files changed on main in between; the uncommitted r4t changes ride on top). The sixth pass stays at 01469100: main is at eadbe571, which adds two pages under v2/docs/feasibility and changes nothing under v2/ecad. The seventh pass stays there too (main is still eadbe571, whose six netlists are byte-identical to the worktree's), and so does the eighth (main moved to 44cfa045 during it, round 7b's integration of r4t's other tools, with the six netlists unchanged; section 4). Files written: `v2/ecad/tools/kisch.py`,
`port_protect.py`, `check_contracts.py`, the new `tx_inhibit.py` (S-02 allows a new tool), `assembly_set.py` (assigned
to r4t in round 6), and the tests `tests/test_port_protect.py`, `tests/test_kisch_tvs.py`, `tests/test_tx_inhibit.py`,
`tests/test_smbus_lead_contract.py`, `tests/test_assembly_set.py`; drafts under `drafts/`. Nothing committed or pushed;
the main checkout was not touched; on the box nothing outside `/root/r4/t` (round 4), `/root/r5/t` and `/root/r5/t2`
(both removed since) and `/root/r6/t` (round 6, its second pass and its third pass, removed since), except the removal
of the box's whole `/tmp` in round 6's second pass, a cleanup error recorded in section 4b with what it may have hit. The
third pass kept every temporary file under `/root/r6/t/tmp` (TMPDIR) and removed nothing outside `/root/r6/t`; the fourth
pass worked in `/root/r7/t` only, with TMPDIR under it, and removed `/root/r7` after the fetch. The fifth pass
regenerated board P only, in `/root/r7/t10` with TMPDIR under it, and removed `/root/r7/t10` (and the then empty
`/root/r7`) after the fetch: main's d90f30e4 changed P's generator during the pass, while kisch.py, the only r4t file in
a generator's identity, did not change, so the fourth pass's regenerations of A to E stay current under the r4t tree and
were read on the runner, in copies under the session scratchpad (section 4f). The sixth pass used no box, nor did the seventh or the eighth: only tx_inhibit.py
and its tests changed, neither is in a generator's identity, and the fifth pass's scratch trees were re-made on the runner.

This file is final after ROUND 6'S EIGHTH PASS. Review T (three blocking items) was answered by the first fix-up, the
review of that fix-up (four) by the second, the review of the second fix-up (APPROVE_WITH_FIXES, two blocking items:
the pins' own leakage in the fail-safe model, and R4T-F9 ruled in scope) by round 6, the review of round 6
(APPROVE_WITH_FIXES, two blocking items: fail_safe() powered down only the source's board, and the redone tap example sat
at VIL) by round 6's second pass, and the review of the second pass (APPROVE_WITH_FIXES, one blocking item: a reader
whose supply net has no leading '+' was never judged) by round 6's third pass, and the review of the third pass
(APPROVE_WITH_FIXES, two blocking items: census() took a supply known only by its name as a harmless pull on a net EMCON
holds high, and _second_sources() missed a feed from a pin-map supply and every transistor) by round 6's fourth pass,
which also read main 458b2873's boards with the tools, and the review of the fourth pass (two blocking items:
_second_sources() read a resistor's far end only through the three supply tests, so a feed behind a link onto a net no
test knew, a firmware pin on the rail and board A's power stage behind its sense resistor went unread; and R4T-D46's
fixture did not test the state R4T-D46 adds) by round 6's fifth pass, and the review of the fifth pass (one blocking item:
_second_sources() passed a firmware part's pin on a gated rail as a load by its NAME, so a Compute Module 5's regulator
outputs, a CP2102N's VDD with its regulator powered and a name only ending in a supply word read PASS) by round 6's sixth
pass, and the review of the sixth pass (APPROVE_WITH_FIXES, two blocking items: an STM32H7's and a Compute Module 5's
VBAT counted as plain loads although firmware can switch on a charger that drives current out of each; and a part whose
value only mentions the Compute Module read with the module's pin numbers, a pin number deciding an input whatever the
symbol called it) by round 6's seventh pass, and the review of the seventh pass (three blocking items: anchoring the
firmware class left a firmware part whose value begins with a descriptor a silent load on a gated rail; the split and
tied-partner checks dropped a sibling pin whose symbol name disagreed with the maker's number; and the STM32H7's VDD was
read as a load with its VBAT on another live net) by round 6's eighth pass. Section 1b holds round 6's decisions, 1c the second pass's, 1d the third pass's, 1e the fourth pass's, 1f the fifth
pass's, 1g the sixth pass's, 1h the seventh pass's, 1i the eighth pass's, section 2 the findings, section 3 how each item was
resolved, section 4 the eighth pass's results (4h the seventh pass's, 4g the sixth pass's, 4f the fifth pass's, 4a the fourth pass's, 4b the third pass's and 4c the second pass's, kept). Prototype framing throughout: nothing here has been built or measured.

## 1. Decisions taken by the session under the owner's standing rule of 26 Sep 2026

Each one had more than one option standing; the evidence recommends the one taken. Every one is "taken by the session
under the owner's standing rule of 26 Sep 2026".

**R4T-D1. The K/A symbol for a one-way clamp is `Device:D_Zener`.** Options: (a) `Device:D_Zener` (pins K = 1,
A = 2); (b) the Diode library's per-part one-way TVS symbols (`SM6T*`, `SMAJ*A`); (c) a synthesised
`D_TVS_Unidirectional` in the board's SYNTH table; (d) `Device:D`. Reason: KiCad 9.0.9's Device library has no
unidirectional TVS symbol (read on the box: `D_TVS` is "Bidirectional transient-voltage-suppression diode", pins
A1/A2), and (b) names its pins A1/A2 as well. (a) names K and A, KiCad exports them as `pinfunction` (round-trip
fixture on the box), and its pin numbering is the same as `D_TVS`, so the NINE clamps that were already the right way
round (A D1 to D4, B D1, D2, D101, D201, D301) change no pad's net (the demonstration netlists differ only in
libsource, properties and pinfunction for those nine). (c) adds a symbol no library carries; (d) draws a suppressor
as a rectifier.

**R4T-D2. A one-way part on an A1/A2 symbol FAILS TRN-001.** Options: FAIL, warn only, INCONCLUSIVE. Reason: S-09's
finding is that no reader and no tool could see the polarity; the helper that removes it exists this round.

**R4T-D3. Every two-pin clamp on the board is judged, declared external port or not.** Reason: board P declares no
external port and its D1 across the pack terminals had the band on PACK_N (A03).

**R4T-D4 (revised in the fix-up). The direction of a clamp comes from its part number, for the families whose makers'
sheets are held (SMBJ and SMCJ: a C in the suffix is bidirectional, Littelfuse, Diodes Inc DS19002 and MDD
Rev:2025A7; Nexperia PESD..S1B: bidirectional), or from the generator's declaration, which `kisch.tvs()` accepts
only with `basis=` naming the maker's statement. Never from the drawing.** A part read from neither is UNJUDGED and
makes TRN-001 INCONCLUSIVE, whatever its symbol. Reason: owner condition 1 (a claim is a mismatch until its source
proves it) and review T blocking 3 (the round-4 version fell back to the drawing).

**R4T-D5. RF-002's instrument runs from check_contracts in its `inhibit` group** (verdict `inhibit_chain_<letter>`,
unchanged), with its logic in the new module `tx_inhibit.py`. Options: a new verdict (needs registry rows owned by
another writer this round); the existing group. See R4T-D22 for how its results are recorded.

**R4T-D6. An RF-disable pin counts as a hardware gate only when its maker states what it does.** The AW7915-AED's
W_DISABLE1# does not count (AsiaRF's datasheet does not mention it; the mainline mt7915 driver has no code for it,
A11), consistent with owner ruling D-05 ("gate or prove the AW7915 W_DISABLE").

**R4T-D7 (extended in the fix-up, see D15). A gate net with a second active driver is not a hardware gate.**

**R4T-D8 (narrowed in the fix-up). The walk crosses only parts whose pin map a held datasheet gives, and only on the
package that map is for**: TI 74LVC08A, 74LVC00A, 74LVC07A (14-pin SOIC/SSOP/TSSOP), 74LVC1G08, 1G00, 1G04, 1G06,
1G07, 1G34 (SOT-23-5/SC-70-5), 74LVC2G07 (SOT-23-6); an N-channel FET by its netlist pin names G/S/D; a two-pin
resistor. The value patterns match LVC only (the round-4 version also matched 74HC and 74AHC, whose sheets are not
held; review minor 6).

**R4T-D9 (extended in the fix-up, see D21). A "power" gate counts when every supply of the anchor is the output of a
known switch whose enable EMCON forces to its off level.** Switch pin maps: TPS22810 (SLVSDH0C), TPS25963x
(SLVSET8A), LM5176 (SNVSAI1D), AP64500 (DS41979).

**R4T-D10. The 30 W VHF PA is judged on board A's J_PA supply (+13V8_PA, LM5176 EN from U26), not on board D's
J_VGG bias.** The LM5176's shutdown is stated in its datasheet; what the RA30H1317M1 does with no VGG was not read.

**R4T-D11 (widened in the fix-up). The pack SMBus lead contract lets board E leave P's PRES pin open OR ground it.**
Open is A07's sketch; grounded is TI's own host arrangement (SLUSC67B 8.2.2.2.3, "In the host system, this pin is
grounded"; review minor 4). A signal on it fails.

**R4T-D12. P's SMBus return must be the net of P's own negative lead W_N (PACK_N)** (A07; TI SLUSC67B Figures 21,
29 and 30).

**R4T-D13. The classification half of RF-002 also writes `inhibit_chain_e` and `inhibit_chain_p`.** RF-002's
`boards_affected` is left for the registry writer (drafts/r4-coverage-rows.yaml says when to widen it).

Fix-up decisions (26 September 2026, after review T):

**R4T-D14. The Compute Module 5's WL_nDisable (pin 89) and BT_nDisable (pin 91) take only open-drain drive.** Their
table options carry `drive="open_drain"`: the last element before the pin, series resistors aside, must be an
open-drain output (74LVC1G07, 1G06, 2G07, 74LVC07A) or an N-channel FET with its source on ground and its gate
driven; a push-pull AND, NAND, inverter or buffer FAILS there, so does an N-channel level shifter (it passes its other
side's push-pull drive), and so does a carrier pull-up on the pin. Options: accept any path that forces the pin low
(round 4); the drive constraint. Basis: Raspberry Pi CM5 datasheet release 3, sections 2.1.1 and 2.1.2 ("may only be
driven low; it can't be driven high"; "internally pulled up through 1.8 kOhm to CM5_3.3V"), owner ruling D-05
("open-drain, may only be driven low"). Review T blocking 1.

**R4T-D15. Every net of an accepted path is a conductor with one driver, the asserted lines included.** From each net,
across the four mated ribbons (J_AB1, J_AB2, J_PANEL, J_MEZZ1 to J_HARN1, whose maps check_contracts proves
identical), through series resistors, beads, N-channel channels (both ways: a level shifter's body diode conducts
from source to drain) and any diode that can pull the net away from its EMCON level, every pin found must only read:
a logic input on its held land, a FET gate, a switch enable, a maker-documented input (`PIN_READERS`: the RM520N-GL's
W_DISABLE1#, Quectel Hardware Design v1.0 pin table "DI"), a protection array, or a tap declared in `READER_TAPS`. A
pin whose direction firmware sets (STM32, RP2040, PCA95xx, ...) FAILS the path; any other pin no document shows to be
an input leaves it UNDECIDED, which is never a pass. The two asserted lines are judged once each over the set and a
path inherits its line's answer. Options offered by the review: fail, or at least UNJUDGED; taken: FAIL for a
software-direction pin (the exact case RF-002 exists for), UNDECIDED for an unproved one. Diodes are no longer
readers by default. Review T blocking 2.

**R4T-D16. A firmware-direction pin on a gate net is accepted only as a declared tap** (`READER_TAPS`: board, ref,
pin, the series resistor it sits behind, the minimum value, and the arithmetic that shows the gate's driver wins).
None is declared today; the board authors' remedies go there (drafts/r4-helper-api.md has a worked example against
TI SCES519O's VOL and SCAS283W's VIL).

**R4T-D17. A classification that rests on an inference is OWED and UNDECIDED, not an accessory.** Board B's J_QMX
(the QMX's USB lead): the QMX operating manual 1.04.004 gives the DC connector's range ("The supply voltage range for
QMX is 6.0 to 12.0V") and describes the USB-C port only as a sound card and serial port; nothing says 5 V on USB
cannot run the transmitter, and VBUS_QMX stays live under EMCON. Re-checked on 26 September 2026 by searching the
manual's text for every USB mention: no power statement. Review minor 7.

**R4T-D18. Every `kisch.tvs()` call is declared in the board's intent** (`clamps`: direction, basis, protected,
return, symbol), and the gate cross-checks the declaration against the part number and against the netlist; a
direction said for an unread part number needs `basis=`. The declared-return check looks up both keys intent.py
stores (`X`, `/X`). Review T blocking 3 and minor 11.

**R4T-D19. Every clamp on P's SMBus clock and data lines must return to W_N's net as well**, and each line must carry
one (TI SLUSC67B Figure 30 returns the connector's VSS and the lines' ESD clamps to PACK-). Options: check it, or name
it as a board P item only (review minor 5 allowed either); taken: check it, because a contract that holds the lead's
return pin and not its clamps certifies half of Figure 30. It FAILS at main (board P's USBLC6-2SC6 D2 pin 2 on the
cell-side GND) until the board P author moves the clamp return.

**R4T-D20. `check()` has an UNDECIDED state** (`ok=None`): judged on every input and not decided. It is not an absent
board, so the guard that keeps a reading taken with more input does not apply. A verdict with an undecided result and
no failure is INCONCLUSIVE.

**R4T-D21. A gated rail must have no second feed.** Every supply of the anchor is read (a `+` rail, or a pin whose
function names a supply), and anything else that could feed the rail (another switch output, a diode or inductor from
another net, an output pin, a connector whose far end is not on the netlist) fails the gate or leaves it UNDECIDED.
Review minor 8.
*Corrected in round 6's fourth pass (the review of the third pass, blocking 2; R4T-F15, R4T-D43).* "Anything else that
could feed the rail fails the gate or leaves it UNDECIDED" did not hold at 5aece264: a resistor was a feed only when its
far end was a '+' rail, so a 0 Ohm or 100 Ohm resistor from VBAT, the gated switch's own VIN, read PASS; and there was
no branch for a transistor at all, so a P-channel FET from +5V_DEV or VBAT around the switch, gate on a GPIO, read PASS.
Since R4T-D43 a resistor from a '+' rail or a pin-map supply FAILS, one from a net only named like a supply or carrying a
supply pin is UNDECIDED unless everything on it is a load, a transistor channel onto the rail FAILS (UNDECIDED when its
gate is the gated switch's own drive), and since R4T-D47 every net of the conductor from the switch to the rail is read.
*Corrected again in round 6's fifth pass (the review of the fourth pass, blocking 1; R4T-F18, R4T-D49).* Two statements
above did not hold at b3d645da. "Anything else that could feed the rail" still missed everything behind a resistor to a
net no supply test knows (a second switch output or a P-channel FET behind a 0 Ohm or 1 Ohm link onto X_ALT, an RP2040
GPIO behind 0 Ohm) and a firmware pin on the rail itself; and "every net of the conductor" was only the nets from the
switch to the rail, so where the switch is found by a sense pin on the rail (board A's LM5176s, VOSNS) the stage's own
node behind its sense resistor was never read. Since R4T-D49 both are read.

**R4T-D22. The transmitter walk's results are recorded in the `inhibit` group ALONE** (`check(..., only_group=True)`):
they decide `inhibit_chain_<letter>` (RF-002) and move neither `check_contracts_<letter>` (SCH-003) nor the set
verdict `check_contracts` (read by INT-001). Found by the fix-up author, not by the review: in round 4 the walk's
results were counted like contracts, so SCH-003 read FAIL on A, B, C and D and the set verdict FAILED 22 of 103 for
reasons that are RF-002's, which is a rule decided by another rule's question (the class recorded on 18 September).
Options: keep counting them in both; group only. Proved both ways by
`test_tx_inhibit.t_the_walk_decides_rf002_and_no_contract` (the same two-board tree with and without an unlisted
radio: inhibit_chain_e turns PASS to FAIL, check_contracts_e and the set verdict do not move; with the old
attribution the test fails). **What D22 did not see, found by the review of the first fix-up:** RF-002 applies only
where the fact rf_transmit holds, which is B and D, so from D22 on the results the walk writes for A (the PA's and the
QMX's supply gates, the panel's line), C (the line) and the classification on E and P landed in verdicts no rule reads.
In round 4 a PA gate regression on A had at least failed SCH-003; after D22 it failed nothing. R4T-D23 closes it.

Second fix-up decisions (26 September 2026, after the review of the first fix-up):

**R4T-D23. RF-002 must apply on every board with a netlist: `boards_affected [a, b, c, d, e, p]`, `condition
{fact: has_schematic, op: truthy}`, and the acceptance criteria name the transmitters, the one-driver nets, the
fail-safe states and the classification.** Options (the review named the first two): (a) UNIVERSAL, which also
makes e5 a pair, a board with no netlist and no parts that nothing can judge and that would sit INCONCLUSIVE for good;
(b) new facts naming a transmitter's supply gate and the EMCON line, which leave E and P out, where the classification
of every radio-named part is the only check that would ever find a radio added there; (c) `has_schematic`, the fact
every board with a netlist already declares (a to p true, e5 false), so rules_lib.validate() stays clean. Taken: (c).
The registry is not r4t's to write, so the change is handed to its writer in drafts/r4-coverage-rows.yaml, and two tests
prove it: `t_a_pa_gate_failure_on_board_a_decides_rf002_once_its_row_reads_every_board` (board A's PA enable moved
from the EMCON AND gate to an expander turns inhibit_chain_a PASS to FAIL, and under the proposed row rules_lib applies
RF-002 to a, b, c, d, e, p and not e5, and rules_status.result_for reads RF-002 on A as PASS then FAIL) and
`t_the_tree_registry_applies_rf002_on_every_board_the_walk_writes_for` (the guard: it SKIPS in this tree, naming a,
c, e and p as the boards whose results decide no rule, and asserts once the row lands). Taken by the session under the
owner's standing rule of 26 Sep 2026.

**R4T-D24. Each asserted line is judged in its fail-safe states, on its own pull-downs, against everything that can
source current, and must stay under 0.8 V.** The states: every subset of the ribbons the line crosses unplugged, and
the line's source's board unpowered (its locally made rails down and its parts inert; a rail it receives over a
plugged ribbon from a powered board stays up, so board C's +5V from B stays live while its +3V3 is down, which is what
the panel losing its own 3.3 V looks like). A fragment where no powered gate reads the line is not judged (the panel
alone after it is unplugged, where only U3's sense pin sits on EMCON_HW). The network: pull-downs to ground; pull-ups
to live rails; a maker-stated internal pull-up (the RM520N-GL's 100 kOhm to 1.8 V, the row PIN_READERS already cites);
a firmware pin at its supply (3.3 V); a push-pull output at its VCC; and every FET or diode that can pass current toward
the line as an ideal one-way element with no forward drop. Options for the element model: the datasheet's diode drop
(the JSCJ 2N7002 states VSD 0.55 V to 1.2 V only at IS 115 mA, nothing at the microamps a pull-up passes, and its
channel conducts once VGS exceeds Vth(GS), 1.0 V to 2.5 V), or no drop. Taken: no drop, the bound that holds for every
part; each result says it is the bound. The threshold: VIL 0.8 V, TI SCAS283W (SN74LVC08A, VCC 2.7 V to 3.6 V: A U26, B
U19 and U20) and SCES217AA (74LVC1G08, VCC 3 V to 3.6 V: D U12), the gates on both lines today. A line that nothing
holds low FAILS as floating; a pin no document bounds leaves it UNDECIDED unless the known sources already lift it.
Proved by fixtures both ways: the panel pair as the kit has it passes both lines; no pull-down floats; the board B
shifter shape (a 2N7002 with its drain on the line and a 10 kOhm pull-up on its source) FAILS; the same FET turned round
FAILS through its channel; a 74LVC1G07 in its place PASSES; a declared 10 kOhm tap FAILS at 3.0 V and a declared 1 MOhm
tap PASSES at 0.3 V. Taken by the session under the owner's standing rule of 26 Sep 2026.
CORRECTED IN ROUND 6 (review of the second fix-up, blocking 1): "no drop, the bound that holds for every part" was true
of the one-way elements and not of the model, which took every CMOS input as drawing no current. With the pins' own
currents (R4T-D28) the 74LVC1G07 remedy PASSES only with 10 kOhm pull-downs (it FAILS at 100 kOhm, 2.0 V in the
fixture), the 10 kOhm tap FAILS at 1.7 V against 10 kOhm, the 1 MOhm tap PASSES at 0.18 V against 10 kOhm, and the
panel pair passes at 10 kOhm and FAILS at 100 kOhm (1.5 V). The fixtures are changed to match (tests/test_tx_inhibit.py).
CORRECTED AGAIN IN ROUND 6'S SECOND PASS (review of round 6, blocking 1): "the source's board unpowered" was the only
power state the tool took; every other board was powered, and the result said that "can only add sources". It can also
remove current, because an unpowered LVC1G part passes its Ioff (10 uA), twice its powered II, and an unpowered
SN74LVC08A is not bounded at all. The states are now bounded part by part (R4T-D37), and the numbers in this entry are
superseded by those of section 1c and R4T-F8's third statement.

**R4T-D25. A diode on a gate net whose far side is a rail or ground is judged by its orientation.** It FAILS when it
can pull the net toward its far side against EMCON's level (anode on a rail and cathode on a net forced low; anode on a
net forced high and cathode on ground or a lower rail), passes as a clamp the other way round, and is UNDECIDED when its
drawing names no cathode and PROTECTION does not match it. Options: this, or the round's first answer (a diode to a
fixed net is a clamp or a load and never a threat). Review blocking 3. Taken by the session under the owner's standing
rule of 26 Sep 2026.

**R4T-D26. The anchor pin is the target of the census of every net on a path**, not only the last one, so a series
resistor in front of the anchor (a CM5 pin, the SA868 PTT) is accepted, as the docstring and the helper API always said.
No options stood: the target is one fixed (board, ref, pin). Review blocking 4.

**R4T-D27. The pulls against a forced level on one conductor (the net and what the census follows from it, through a
level shifter's channel included) may ask at most 4 mA of its gate, a resistor from another rail
onto a gated rail is a second feed, and a pull-up anywhere after a Compute Module pin's last open-drain element, to any
supply however named, fails the pin.** The 4 mA: every held LVC sheet guarantees VOL at most 0.45 V at 4 mA even at VCC
1.65 V (SCES519O, SCES296AG), and at the kit's 3.3 V SCAS283W guarantees 0.4 V at 12 mA; options were a per-family
IOL table (more exact, and it would need every family's table held and read) or one floor under all of them. Taken:
the floor. Review minors 1 to 3. Taken by the session under the owner's standing rule of 26 Sep 2026.

## 1b. Round 6 decisions

Round 6 decisions (26 September 2026, after the review of the second fix-up, APPROVE_WITH_FIXES with two blocking
items). The worktree was fast-forwarded from 82dd1e4d to main faf8c981 before this round's edits (none of r4t's files
changed on main in between), so everything below is judged against the boards as main carries them now: C, D, E and P
with their round-4 corrections, A and B as held.

**R4T-D28. Every pin a held net meets passes its sheet's adverse-sign maximum current into the fail-safe network, read
from the -40 to +85 C column.** Review blocking 1: the model of the second fix-up took every CMOS input as drawing
nothing, and the line's own pull-downs are 100 kOhm. Now: II for a powered logic input, Ioff for any pin of an unpowered
logic part that states one, a switch enable's stated current (TPS22810 IEN/UVLO 0.1 uA; TPS2596x IENLKG 0.1 uA; LM5176
IEN(STBY) 3 uA sourced in standby; AP64500 IEN 2 uA out of the pin, which floats high), and the pull a module's maker
states for its own pin (the Compute Module 5's 1.8 kOhm to 3.3 V; the RM520N-GL's 100 kOhm to 1.8 V). The sign is the
adverse one: into a net that must stay low, out of one that must stay high. Each value and its sheet is in the LOGIC and
SWITCHES tables of tx_inhibit.py. Options for the column: 25 C (SN74LVC08A II 1 uA), -40 to +85 C (5 uA), -40 to +125 C
(20 uA). Taken: -40 to +85 C, because it covers the envelope and its qualification margin (-20 to +40 C in use, +55 C
operating, owner ruling D-02a), a 25 C figure does not, and the +125 C column asks for pull-downs the envelope does not
need. A current stated at one voltage is used as the bound where the sheet states it at or across the threshold the net
is judged against: a pin that cannot push the net past the threshold with the current it passes at the threshold cannot
push it there at all. Taken by the session under the owner's standing rule of 26 Sep 2026.
AMENDED IN ROUND 6'S SECOND PASS (review of round 6, minor 1): an enable that is ON when its gate dies is dragged down
THROUGH its threshold from above, so the bound is the current the part passes there while it still counts as on. The
LM5176 then sources IEN(STBY) 3 uA plus dIHYS(OP) 4.25 uA (SNVSAI1D 6.5 and 7.3.3, Equation 2), 7.25 uA, not 3 uA; the
AP64500 states 5.5 uA TYPICAL, no maximum, at VEN 1.5 V (DS41979 Rev. 5-2), so its enable current is not bounded and a
hold of it is UNDECIDED (R4T-D29). Board A's PA_EN reads 0.16 V with it (and board D's U14 at its Ioff, R4T-D37).

**R4T-D29. A pin whose current no held sheet bounds leaves the state UNDECIDED unless the known currents already decide
it.** This covers: an unpowered SN74LVC08A or SN74LVC00A (their TI sheets have no Ioff row, and SCAS283W 7.3.3 gives the
outputs positive and negative clamp diodes, so they are not specified for partial power down: a VCC back-fed through
another pin can half-power them); a FET whose sheet states IGSS and IDSS at 25 C only (the fitted JSCJ 2N7002, C8545);
a diode's reverse current (no held BAT54 sheet); a clamp's reverse current toward the net (none tabulated); an
unpowered controller or module pin; a powered open-drain output's off-state current (the LVC1G07 sheet states none).
Options: take the unpowered SN74LVC08A as high impedance (what the review assumed), take a sibling part's Ioff (the
LVC1G sheets' 10 uA), or say it is not bounded. Taken: not bounded, because TI positions Ioff as the feature that makes a
part safe to power down and does not claim it for this one. The consequence is stated in R4T-F9 below: board A's PA and
HF enables and board B's three enables read UNDECIDED, not PASS, even with their pull-downs, until their gates are parts
that state Ioff. Taken by the session under the owner's standing rule of 26 Sep 2026.

**R4T-D30. R4T-F9 is judged: every element on an accepted path is taken down with its own supply, and what it drove must
still be held at EMCON's level.** Ruled in scope by the review of the second fix-up (blocking 2); taken as the evidence
recommends under the owner's standing rule of 26 Sep 2026. For each element with a supply of its own (a logic gate's
rail, a level shifter's gate rail), one rail at a time with the rails a bead or a 0 Ohm link joins to it and across the
ribbons, the path is followed again: an element that is down drives nothing, so the net it drove is solved as a network
(its pulls, every pin's current from R4T-D28, the dead element's own Ioff) and judged at the threshold of whatever reads
it next: the next gate's VIL or VIH (0.8 V and 2.0 V, TI's LVC sheets at VCC 3 V to 3.6 V; Diodes DS35124 VT- minimum and
VT+ maximum at 3 V), a switch enable's stated off level (TPS22810 VENF 1.08 V; TPS2596x VUVLO(F) 1.08 V; LM5176 VEN(OP)
1.17 V; AP64500 VEN_L 1.03 V), a FET gate's Vth(GS) minimum to be off and the VGS its on resistance is stated at to be on,
or the level the transmitter's maker states for its pin. A reader that is itself down leaves the question to the next
element. The state is not judged when the transmitter loses its supply with the element: a rail it shares with it, or
for a supply switch the switch's own input (board B's E72 switch U22 is fed from +3V3_DEV, the rail its gate U19 loses,
so E72_EN needs nothing, as the review said). Options for the anchor with no stated threshold (the SA868's PTT): a
generic CMOS level, the level the design's own driver produces, or UNDECIDED. Taken: UNDECIDED, and FAIL where no level
could matter (the pin floats, or it is held only by its maker's own pull, which is the maker's "left floating").
AMENDED IN ROUND 6'S SECOND PASS (review of round 6, minors 4 and 5). (a) The FET reader's threshold is the JSCJ
2N7002's Vth(GS), 1.0 V to 2.5 V, which its sheet states at Ta 25 C only, like the IGSS R4T-D28 refuses. Vth falls as the
part warms, so a gate held under the 25 C minimum is not proved off over the envelope: level 0 (FET to be off) never
passes now and fails only at or above the 25 C maximum; level 1 (SW_GND, the gate held high so the FET pulls its drain
low, the only case a path produces today) passes only at the VGS the on resistance is stated at (5 V) and fails under
the 25 C minimum. Neither can produce a false pass; a level-1 FAIL can refuse a FET that would still conduct when
warm, which is the conservative side. (b) A transmitter pin with no stated threshold that is held at or above its
maker's own pull-up level reads UNDECIDED, though that is the maker's "left floating" level and could read FAIL; this
is conservative, not wrong, and is left as it is. (c) The held net is solved with the per-part bound of R4T-D37, and
open-drain elements EMCON releases are judged in a released state of their own (R4T-D38).

**R4T-D31. A failure that rests only on a part whose orientation is not drawn is UNDECIDED.** The fail-safe network takes
such a diode the adverse way, which is right for a pass (it passes whichever way it points) and wrong for a failure (it
fails only if it points the way nobody drew). The network is solved again without it; a state that fails only with it is
UNDECIDED and names it. No options stood: the census already treats an undrawn orientation as UNDECIDED.

**R4T-D32. A pull against a level a FET forces is UNDECIDED unless its gate is driven to the VGS its sheet states the
on resistance at** (review minor 1). The 4 mA floor (R4T-D27) rests on the LVC sheets' VOL; a level shifter or a switch
to ground holds its level through its channel, and the JSCJ 2N7002 states RDS(on) only at VGS 5 V and 10 V, so at a
3.3 V gate the channel drop is not bounded. Options: cite a separate bound (none is held), or lower the limit (to what,
the sheet does not say). Taken: UNDECIDED, named. Taken by the session under the owner's standing rule of 26 Sep 2026.

**R4T-D33. The walk knows board C's 74LVC1G17 from its maker's sheet.** Round 4 made C's U9 (EMCON_HW's buffer) and U12
Diodes Incorporated 74LVC1G17W5-7 (LCSC C151394). At main faf8c981 the walk did not know it, so it neither found
EMCON_HW's source nor read TX_INHIBIT_n at U9's input (the TX_INHIBIT_n line read UNDECIDED on main for that alone). The
LOGIC table gains it from Diodes DS35124 Rev. 8-2 (SOT25: NC 1, A 2, GND 3, Y 4, VCC 5; II 5 uA, IOFF 10 uA). No options
stood.

**R4T-D34. The part-number reader lists part numbers one by one where the maker's sheet for exactly that part is held**
(`kisch._HELD_DIRECTION`). Board D's D10 and D13 became Nexperia PESD12VL1BA (C38558) in round 4; the reader returned
None and port_protect judged them UNJUDGED. Options (the review named two): add the part to the reader, or have board D
pass direction='bi' with its basis when it moves to tvs(). Taken: the reader, from Nexperia's own sheet for the part
("Low capacitance bidirectional ESD protection diode", 14 April 2023), because D draws D10 and D13 with `part()`, not
`tvs()`, so only the reader reaches them; Nexperia's naming is not read as a rule (PESD12VS1UA stays unread). Taken by
the session under the owner's standing rule of 26 Sep 2026.

**R4T-D35. assembly_set.py: a package family anywhere in the footprint name at a word boundary, and any part with three
or more pins, is polarised** (assigned to r4t this round). The families were matched only at the start of the name, so
maker-named lands dropped out of DFA-001's checklist (board P's gauge on Texas_RSM0032A_VQFN-32 left it in round 4;
board E's SGP41 on Sensirion_DFN-6 and board P's three-terminal Eaton_SCF9550 were never on it). Options: add the
makers' names to the list (Texas, Sensirion, Eaton, and the next maker nobody lists), match the families anywhere, or
count pins. Taken: the families anywhere plus the pin count, because a three-terminal part cannot be turned without a
terminal landing on another net whatever its name, and a two-pin part is polarised only by its family (which keeps the
symmetric passives out). The checklist grows from 43 to 78 footprints (drafts/ROTATION-CHECKLIST.r6.md). Taken by the
session under the owner's standing rule of 26 Sep 2026.

## 1c. Round 6 second pass decisions

Taken after the review of round 6 (APPROVE_WITH_FIXES, two blocking items and nine minor ones). Each is taken by the
session under the owner's standing rule of 26 Sep 2026.

**R4T-D37. The fail-safe line is judged against every part on its conductor at the worse of its powered and unpowered
states, one reader at a time.** Review of round 6, blocking 1: fail_safe() only ever powered down the board carrying the
line's source, and said that taking every other board as powered "can only add sources". It is false twice: an
unpowered LVC1G part passes Ioff (10 uA; SCES217AA, SCES296AG, DS35124), twice its powered II (5 uA), and an unpowered
SN74LVC08A is not bounded (R4T-D29). On the review's own fixture (47k/22k, B's gates as 1G08) round 6 read PASS (worst
0.67 V) while boards B and C unpowered with A powered read 1.05 V (1.10 V at the adverse tolerance, R4T-D36). Options:
(a) the review's enumeration, every subset of the carrier boards unpowered with every subset of the ribbons unplugged,
pruned by "a board that only gets power through an unpowered board goes down with it"; (b) the same without the
pruning; (c) bound each part on its own. Taken: (c) for the verdict, with (b) solved exactly whenever the bound does not
pass, to name the physical state and to fail the line if an exact state fails. Why: (a)'s pruning is not physical
here, because a board can lose ONE rail and keep the others. Board A makes +3V3 (its buck through L7, U26's supply)
apart from the +5V_DEV its eFuse U23 hands to board B, so A's gates can be unpowered while B's read the line, a state
the pruning (B goes down with A) removes; and board B's slot rails (+3V3_S1A to S3A, the 74LVC1G07 remedy's supplies)
are made apart from +3V3_DEV (U19 and U20). Whole boards cannot express that; parts can. The bound: for each reader
(a logic input, a switch enable, a FET gate), the reader's own supply is up and every other part is taken at the worse
of its two states (max(II, Ioff) for a logic input, UNDECIDED where the part states no Ioff, a firmware pin as a source
AND as an unpowered pin nobody bounds, a module input's own pull AND its unpowered current, a level shifter's channel on
AND off with its unstated off-state current); the source's board keeps its locally made rails down (the panel
unpowered) and every rail it receives up. It is at least every whole-board state, which a fixture checks
(t_the_bound_covers_every_whole_board_state_the_review_named). The same bound holds a net in own_supply(): the reader and
the transmitter run, the dead or released element is off, anything else on the net is bounded (board D's U14 on PA_EN,
over the harness, is taken at its Ioff).
*Corrected in round 6's third pass (the review of the second pass, blocking 1; R4T-F14, R4T-D41).* "It is at least every
whole-board state" held only for readers on a net whose name starts with '+'. The reader's own supply was read from its
'+' rails alone, so a gate or a switch whose supply pin sits on VBAT, VCC_X or 3V3_DEV had none, fell into the empty
domain whose run reused the network in which it was only "either", and was never judged by the bound, while _fs_state
judged it (the review's probe_bound_vs_exact: the bound PASS with "no gate that can be powered reads EMCON_HW", the state
C unpowered and B powered FAIL, floating). The reader's supply is now read from its pin map (R4T-D41), and the fixture
t_the_bound_covers_every_whole_board_state_the_review_named carries that kit both ways (no pull-down: the bound and the
state FAIL; 100 kOhm: both UNDECIDED at 1.58 V, the bound no lower). A switch reader's domain is its input rail only,
not its output (the review's minor on the switch domain).

**R4T-D36. Resistors to a fixed node at the adverse end of their tolerance, rails 5 percent the adverse way, and the
result says what is nominal.** Review of round 6, minor 2: the fail-safe and own-supply solves used nominal values and
called the result "the bound". Options: apply each value's tolerance and each rail's declared maximum, or keep nominal
values and require a stated margin under VIL. Taken: the first, as far as the netlists carry it. A resistor from the net
to ground or to a rail is taken at the end of its tolerance that hurts (a pull toward the level the net must hold at its
maximum, one against it at its minimum); the tolerance is read from the value ("62k 1%") and is TOL_DEFAULT, 5 percent,
where the value states none. Every rail is taken RAIL_TOL, 5 percent, the adverse way (higher against a net held low,
lower under a net held high), which is wider than the accuracy of the regulator sheets held in v2/vendor for rails
these lines meet (TI TLV755P, SBVS320D: 1 percent maximum from -40 to +85 C; the Diodes AP64500's reference, DS41979
Rev. 5-2, 792 to 808 mV, before its 1 percent divider); not every rail's regulator sheet is held, which is one reason
one allowance was taken. The intents do not declare a maximum for most rails, so one allowance above all of them was taken over a
per-rail figure. A resistor between two unfixed nodes (a series tap), a ribbon, a bead and a maker's own pull (no maker
here states a tolerance for one) stay nominal, and every result says so.

**R4T-D38. An open-drain output EMCON releases is followed, and its net is judged on what holds it.** Found while
judging the board D author's round-6 draft: SA_PTT_n becomes an open-drain 74LVC1G06 (U13) with R88 1.2k from +5V_SA and
R89 2k to ground, so under EMCON (KEY low) U13 RELEASES the pin and the divider sets it to receive. The walk stopped at a
released output and read "EMCON does not reach it", a false FAIL. Options: leave the walk and let D's design read FAIL,
treat the released net as forced (a false pass: nothing checks the divider), or follow it and judge the hold. Taken: the
third. The input level that releases each open-drain kind is known (a 1G07 at 1, a 1G06 at 0), the released net takes
the level its pulls set at their nominal values (none, or a level between VIL and VIH, and it is not reached), and
own_supply() judges a "released" state like a dead element's: the pulls against every pin's current, the released
output's own powered off-state current included, at the reader's threshold. No held LVC sheet states that current (only
Ioff, at VCC 0), so a released hold is UNDECIDED at best until a sheet or the bench states it. On a released net the
census does not count the pulls as a load on a driver, since they are what sets the level.

**R4T-D39. A reader whose supply is outside 3 V to 3.6 V is not judged at 0.8 V or 2.0 V.** Review of round 6, minor 3:
VIL_LOW and VIH_HIGH are the LVC figures at VCC 3 V to 3.6 V (0.35 VCC at 1.65 V to 1.95 V, 0.3 VCC at 4.5 V to 5.5 V),
and the reader's own rail was never checked. Taken: the reader's supply voltage is read from its rail's name; outside
the range, or unnamed, the state is UNDECIDED and the reader is named. No board has one today; a fixture has one both
ways (+5V and an unnamed rail).
*Corrected in round 6's third pass (the review of the second pass, blocking 1; R4T-F14, R4T-D41).* The claim held only
for a supply whose name starts with '+': the fixture used "+VCC_X". A reader on "VCC_X" or "3V3_DEV" was not UNDECIDED,
it was not judged at all, and with no pull-down its line read PASS. Its supply is now its VCC pin's net, whatever the
net is called: such a reader FAILS when the line floats at it (nothing holds it at any VCC) and is UNDECIDED otherwise,
never PASS, since only a '+' name that states a voltage places it in 3 V to 3.6 V (fixture
t_a_reader_whose_supply_net_has_no_plus_is_judged). A line that reads above 0.8 V at such a reader is UNDECIDED, not
FAIL: the same LVC sheets let VIL reach 0.3 x 5.5 V = 1.65 V at an unstated VCC.

**R4T-D40. The series-resistor sense tap is withdrawn as a remedy; the buffer is the only one.** Review of round 6,
blocking 2: the redone example (220 kOhm per tap with R58 at 10 kOhm) sat at VIL at nominal values. Options: redo the
arithmetic with tolerance and the +3V3_IOCA maximum and say that an unpowered supervisor leaves it UNDECIDED, or
withdraw it. Taken: withdraw, with the arithmetic recorded. With R58 at 4.7 kOhm 1% (R4T-F8, third statement) the
powered sums can be met (R above 97 kOhm per 1 percent tap at 3.465 V; 100 kOhm reads 0.785 V, 120 kOhm 0.73 V), but
each supervisor's LDO can be down while a gate on another rail reads the line, and then PC5 is an unpowered controller
pin whose current no held ST sheet states, so any tap leaves the line UNDECIDED (drafts/box/tap_probe.py). The same holds
for board C's RP2040 (unpowered in every fail-safe state that carries the panel). READER_TAPS stays in the tool for a
controller whose off-state current is one day cited.

## 1d. Round 6 third pass decisions

Taken after the review of round 6's second pass (APPROVE_WITH_FIXES, one blocking item and eight minor ones). Taken by
the session under the owner's standing rule of 26 Sep 2026.

**R4T-D41. A part's supply is read from its maker's pin map, and a supply is a supply whatever its name.** The review of
the second pass, blocking 1 (R4T-F14): the per-reader bound grouped readers by the '+' rails on their pins, so a reader
whose supply pin sits on a net named VBAT, VCC_X, 3V3_DEV, ZBA_3V3 or SAU_3V3 was never judged, and a line with nothing
holding it read PASS. Options: (a) the review's first: such a reader is a reader in every run, like a FET gate,
UNDECIDED at best, FAIL if it floats or rises past 0.8 V; (b) the review's second: the empty supply gets a run of its
own, with every part on that board that has no '+' rail taken powered; (c) each reader's supply is read from its
maker's pin map (a logic part's VCC pin, from the Pin Functions tables LOGIC already cites: VCC 5 on every LVC1G part
and the 74LVC2G07, VCC 14 on the quads; a switch's input pins, VIN or IN, from SWITCHES), whatever the net is called,
and a reader none of whose supply is on the netlist is a domain of its own. Taken: (c). Why: (a) keeps a reader powered
in runs where its own supply may be down, so the reader and its neighbours are not each taken at the worse of their two
states; (b) takes every such part on the board powered together, so a second one reads at its powered II (5 uA) where
it may be unpowered at its Ioff (10 uA), which is not a bound; (c) powers together exactly the parts that share a supply
net, as they are, and it answers the review's minor on the switch domain in the same stroke (a switch's domain is its
input, never the output EMCON switches). Thresholds: a logic reader on a supply whose name states no voltage FAILS when
the line floats at it and is UNDECIDED otherwise (R4T-D39, corrected); option (a)'s "FAIL above 0.8 V" was not taken for
it, because the LVC sheets give VIL up to 0.3 x 5.5 V = 1.65 V at an unstated VCC. A switch enable's off level is stated
absolutely (VENF, VEN(OP), VEN_L), so it is judged at 0.8 V whatever its input is called.
And a supply is a supply whatever its name: a '+' rail, a net whose name says so (_supply_name: VDD, VCC, VIO, VBUS,
3V3, 1V8, 5V0 or 5V) unless the name also carries a control word (EN, ON, PG, SW, SEL, KEY, PTT, RST and the like, the
list _CONTROL_WORD: an enable named after the rail it switches, "EN_3V3", is the signal EMCON drives, and taking it for
a supply would stop the walk at it), or a net a logic VCC pin or a switch input sits on. None of the six netlists has a
supply-like name with a control word in it (checked in memory). It is never walked as a signal. Only a '+'
name is read for a voltage, so in the fail-safe and own-supply solves a live supply whose name states none leaves the
state UNDECIDED (it used to be a floating node: a 10 kOhm pull-up from EMCON_HW to 3V3_AUX lifted nothing and the line
read PASS); in the census a resistor to one is a pull (a 0 Ohm link from 3V3_AUX onto an enable EMCON forces low FAILS,
where it used to be followed as a conductor and read PASS; a 10 kOhm one is UNDECIDED, its voltage unknown); the walk
does not push into one; a released open-drain net pulled to one has no level (the review's minor 7), and the result
says why (_released_why). Left as it was: _second_sources() takes only a '+' rail at a resistor's far end as a second
feed, because a net only NAMED like a supply there can be an indicator's anode (board B's LED_5V_A1 is LED11's anode
behind R101, 1k), a load and not a feed.
*Corrected in round 6's fourth pass (the review of the third pass, blocking items 1 and 2; R4T-F15).* Three sentences
above were wrong about 5aece264. (1) "It is never walked as a signal": that was the defect, not a property. In the
census a supply known only by its name then stopped the walk, and on a net EMCON holds HIGH any supply was a harmless
pull, so a 0 Ohm or 1 kOhm link from SA_PTT_n to VCC_SENSOR or GPS_3V3 (an RP2040 GPIO on it) or to SIM1_VCC (an M.2
UIM-PWR pin) read PASS where e88aa46b read FAIL or UNDECIDED; the 0 Ohm test sat after the harmless `continue`. R4T-D42
replaces it: the census judges a supply by how it is known, and walks a name-only one for its drivers as well. (2) "A
supply is a supply whatever its name" claims more than the code does: the name test knows VDD, VCC, VIO, VBUS, 3V3,
1V8, 5V0 and 5V, so at main 458b2873 board A's and board E's VIN_RAW, board B's VBAT, board D's PCM_VIN and board E's
VIN_MON are supplies only where a logic VCC or switch VIN pin sits on them, and are otherwise walked as conductors, which
meets their parts and can only FAIL or leave a path UNDECIDED (tx_inhibit's docstring now says so). (3) "Left as it was:
_second_sources() takes only a '+' rail" left the second-feed gap of R4T-F15 open; R4T-D43 closes it, and board B's
LED_5V_A1 is handled by reading what is on the far net (_load_only), not by ignoring every name. On the six netlists at main faf8c981 nothing moves: every logic part's VCC pin
is already on a '+' rail, judge(), fail_safe() and the walk give output identical to e88aa46b's (in memory, scratchpad
r7t/dump.py), and leak_probe2, board_remedy_probe and tap_probe read byte for byte as before, on the committed
netlists and on the box's regeneration (section 4b).

## 1e. Round 6 fourth pass decisions

Taken after the review of the third pass (APPROVE_WITH_FIXES, two blocking items and six minor ones), and after main moved
to 458b2873 (boards A, B and D corrected) beneath the tools. Taken by the session under the owner's standing rule of
26 Sep 2026: every option below was an engineering judgement with a measurement or a maker's statement behind the one
taken, and none spends money, changes what the kit is claimed to be or accepts a residual risk.

**R4T-D42. The census judges a supply by how it is known (blocking 1, minors 1 and 4).** `_supply_test()` now says how a
net is a supply (`is_supply.kind`): "rail" (a '+' name, the only kind read for a voltage), "pinmap" (a logic VCC or a
switch VIN pin sits on it) or "name" (its name alone). For a resistor or a P-channel switch from a forced net to a
supply: on a net EMCON holds LOW, any supply is against the level (v / R summed to PULL_MA_MAX, as before); on a net EMCON
holds HIGH, a '+' rail is harmless only at or above V_FIRMWARE_HIGH (3.3 V, the level the census already took a
driven-high net at against a pull to ground), and a lower one is a pull against it, (3.3 V - v) / R, with a 0 Ohm link or
a switch channel to it FAILING; a supply whose voltage no name states is UNDECIDED at either level and a 0 Ohm link or a
P-channel switch to it FAILS at either level (the 0 Ohm test now comes before any harmless `continue`); and a supply known
only by its name is ALSO walked as a conductor, so a firmware pin on it FAILS the path and names the pin, as e88aa46b did.
A released open-drain net still takes its pulls to ground and to a '+' rail that states its voltage as what sets its
level; a pull to any other supply there is judged as above. Options: the review's rule without the walk (a name-only
supply UNDECIDED, never FAIL); the walk without the rule (e88aa46b's behaviour, which read a 1 kOhm link to an undriven
supply-named net as PASS); both. Taken: both, because the rule alone loses e88aa46b's FAIL on a GPIO-powered rail (the
review's minor 1) and the walk alone passes a pull to a supply whose driver the netlist hides behind an unknown part.
Why the harmless bar is 3.3 V and not the reader's VIH (the review's "preferably at or above the reader's threshold"):
the census asks whether the driver keeps its level, and a CMOS driver holding 3.3 V against a pull to a lower rail keeps
it within its sheet's VOH as long as the current stays under PULL_MA_MAX; a pull below the reader's threshold matters
once the driver is gone, which own_supply() and fail_safe() judge at the reader's own threshold. The bar is therefore
stricter than the review's (a 10 kOhm pull to +1V8 reads 0.15 mA against the driver, a 330 Ohm one 4.5 mA and FAILS, a
0 Ohm one FAILS). Not modelled, and named: the census takes every '+' rail as up, so a '+' rail firmware can switch off,
linked to a net EMCON holds high, is judged only as the rail it names; on the six netlists at main 458b2873 the only
nets EMCON holds high are board A's OUTLET_OK (no pull) and board D's SA_PTT_n (R88 to +5V_SA, the exciter's own
rail), so no path meets one.

**R4T-D43. A second feed is any supply by pin map and any transistor channel (blocking 2).** In `_second_sources()`: a
resistor of any value from the gated rail to a '+' rail or to a pin-map supply FAILS (VBAT on a TPS22810's own VIN, WSON
pin 6, SLVSDH0C); one to a net only named like a supply, or to a net a pin whose function names a supply sits on
(SUPPLY_FN: VIN_RAW or VBAT on a board with no logic VCC or switch VIN pin on it), is UNDECIDED unless everything else on
that net is shown to be a load (`_load_only`: a capacitor, a resistor to ground, a diode or LED with its anode there and
its cathode on ground; board B's LED_5V_A1 behind R101 is one); a transistor with a channel pin on the rail FAILS unless
its other channel pin is on ground or on nothing (a discharge FET), and is UNDECIDED when its gate is driven by the gated
switch itself (an LM5176's HDRV on a boost-leg FET: no table here states the gate drive is off with the enable); a FET's
gate on the rail only reads it; a transistor fet_of() cannot read (a BJT, an unmarked FET) is UNDECIDED unless its pin
on the rail is named G. Options for a name-only far end: FAIL, UNDECIDED, or judged by what is on the far net; taken the
last, UNDECIDED unless shown to be a load, because FAIL would refuse board B's slot indicators and silence was the gap.
Checked, as the review asked: board A's R50, R55, R60, R65, R163 and R165 end on PA_FB, PA_OUT, HF_FB, HF_OUT, PA_ISNS_N
and HF_ISNS_N, none a supply by any of the three tests and none carrying a SUPPLY_FN pin, so A's result does not move;
no FET channel sits on any gated transmitter rail of the six netlists at main 458b2873.
*Corrected in round 6's fifth pass (the review of the fourth pass, blocking 1; R4T-F18).* Two sentences above said more
than the code did. "A resistor to ground, to a feedback or sense node or to nothing is not a feed": the code took a
resistor to ANY net no supply test knew as not a feed, whatever was on it, so a second TPS22810's output or an AO3401A's
drain behind a 0 Ohm or 1 Ohm link onto X_ALT or LORA_PWR_B read PASS where the same parts on +5V_ALT FAILED
(rv9t/probe_feed_via_link), and an RP2040 GPIO on the rail, directly or behind 0 Ohm or 100 Ohm, read PASS
(rv9t/probe_gpio_on_rail). And "Checked: board A's R55 and R65 end on PA_OUT and HF_OUT, none a supply, so A's result does
not move" was true of the names and silent on the nets: PA_OUT and HF_OUT carry the boost-leg FETs Q14 and Q24, and neither
net was read. R4T-D49 reads them, and every net behind such a resistor.

**R4T-D44. A transmitter's supplies are read by pin function, and a backup pin is not one (minor 5).** `_judge_option()`
no longer filters the anchor's supply nets by the name test: a net on the anchor's SUPPLY_FN pin whose name carries a
control word (RF_3V3_SW) is its supply, as the maker's pin function says, so own_supply() skips the states in which the
transmitter is itself off. The guard that makes this safe: an option may list `backup_pins`, pins whose maker says they
only keep something alive while the part is off, and those are left out; the three Compute Module 5 options list pin 76,
"VBAT ... RTC battery input 2.5 V to 3.5 V; typically 3 V" and "Provides backup power for RTC so that it can keep time even
when the board is off" (CM5 datasheet release 3, pin table and 2.12.2), whose "main power input" is its 5V pins 77 to 87.
Without the guard, an element running from board B's RTC cell net would have had its supply-down state skipped as one
in which the module is off. Options: keep the name filter (the review's false FAIL), take every SUPPLY_FN net (the
false skip), or the pin function with a cited backup list; taken the last. On the six netlists nothing moves (no path
element runs from VBAT, and no anchor supply net carries a control word).

**R4T-D45. A line no supply voltage reads as low FAILS whatever its reader's supply (minor 2).** Each LOGIC family carries
`vil_ceiling`, the highest input level its sheet still reads as LOW at any VCC it allows: 1.65 V for the TI single and
dual gates and the SN74LVC07A (VIL 0.3 x VCC at 4.5 V to 5.5 V, operating to 5.5 V: SCES217AA, SCES214AF, SCES519O,
SCES212AC, SCES296AG, SCES295AB, SCES308L, SCAS595W), 0.8 V for the SN74LVC08A, SN74LVC00A and SN74LVC32A (operating to
3.6 V: VIL 0.35 x VCC, 0.7 V, 0.8 V; SCAS283W, SCAS279U, SCAS286U), and 1.45 V for the Diodes 74LVC1G17, whose Schmitt input
reads LOW below VT-, highest at VCC 5.5 V (DS35124 Rev. 8-2, both columns). A reader whose supply states no voltage, or
one outside 3 V to 3.6 V, FAILS the line at or above its ceiling and stays UNDECIDED between 0.8 V and it; the same
ceiling is the level-0 fail threshold where a gate on a path has lost its supply (_threshold). Options: the review's
single 1.65 V, or per family; taken per family, because 1.65 V is too lenient for two of them: a 74LVC1G17 is sure to read
LOW only below its VT- minimum, at most 1.45 V (at VCC 5.5 V), so a line at 1.5 V is LOW at no VCC it allows; and the
quads, which stop at VCC 3.6 V, read nothing above 0.8 V as LOW. Found while fixing it (R4T-F16): a node carrying one
reader off the range exempted every reader on it from the 0.8 V test; readers are now judged one by one.

**R4T-D46. A FET EMCON holds off releases its drain, and the SN74LVC32A OR is walked (main 458b2873, board B's S-01).**
Board B inverts EMCON_HW once with Q11 (a 2N7002 switch to ground, drain EMCON_ON, R513 10 kOhm to +3V3_DEV) and gates
each module radio with an SN74LVC32APWR OR (U111, U211, U311: KILL = OFF OR EMCON_ON) into an open-drain 2N7002 on the pin.
The third pass's walk followed an N-channel switch to ground only when EMCON held its gate high, and had no OR, so all six
module radios read "EMCON does not reach it". Now an N-channel switch to ground whose gate EMCON holds LOW releases its
drain to the level its pulls set, exactly as an open-drain output EMCON releases (R4T-D38), with the hop kind OD_REL; its
"supply" in own_supply() is the rails its released net is pulled up to (a state with that rail down leaves the net held by
nothing), and it stays off (in `released`) in every state in which what drives its gate is up; in the network a FET held
off passes only its off-state channel current, which the fitted JSCJ 2N7002 states at 25 C only (R4T-D28), so a path
through one is UNDECIDED at best until a sheet states it over the envelope. The OR family carries TI SCAS286U's pin map
(Table 4-1, D/DB/NS/PW: gates 1-2-3, 4-5-6, 9-10-8, 12-13-11, VCC 14), II +-5 uA (5.7, -40 to +85 C) and no Ioff row. Options:
leave board B's S-01 unwalked (the description of the tool, not the board), or treat the held-off FET as a forced driver
(it drives nothing: its level is its pull-up's); taken the release. The results on the six netlists do not move (every
board B transmitter already FAILS on its line, EMCON_HW); the details now name board B's own findings (section 5).

**R4T-D47. A gated rail is traced to its switch through one current-sense shunt, and every net of that conductor is
checked for a second feed.** Board B's card sockets take +3V3_M2C1, +3V3_M2C2 and +3V3_M2C3 through 5 mOhm shunts (R165,
R265, R365) from the AP64500 bucks' outputs, so `_source_switch()` answered "no switch this file knows has its output"
for both AW7915 cards' supplies. It now follows one resistor under SHUNT_MAX_OHM (1 Ohm) to the net where the switch's
output or its inductor is, and returns the path (nets and parts); `_second_sources()` reads each net of it with the path's
own parts excluded (before, every inductor on the rail was excluded, whoever it came from). Options: a shunt as any
resistor (a 10 Ohm series part would have hidden a feed), or under a stated bound; taken 1 Ohm, above every shunt on the
set (2 to 10 mOhm) and below any resistor a designer would call a feed path. No result moves on the six netlists.
*Corrected in round 6's fifth pass (the review of the fourth pass, blocking 1; R4T-F18).* "Every net of that conductor is
checked" held only for the nets from the switch to the rail. `_source_switch()` finds board A's LM5176s by VOSNS (pin 12)
on +13V8_PA and +12V_HF themselves, with an empty path, so R55 (6 mOhm) and R65 (10 mOhm) were read as resistors to a
non-supply net and PA_OUT and HF_OUT, the power stages' own nodes, were never read (rv9t/probe_board_a_pa). Since R4T-D49
a shunt or a 0 Ohm link joins the net on its other side to the conductor in either direction.

**R4T-D48. Board A's D22 is read from its maker's sheet.** Main 458b2873 added D22, a BZT52C12-7-F on Device:D_Zener (the
restart guard's pull-up clamp, cathode on FE_VZ, anode on ground), and kisch.tvs_direction() could not read it, so the
polarity pass left it UNJUDGED and would hold TRN-001 INCONCLUSIVE on A once A's four symbol mismatches are answered. It
is added to `_HELD_DIRECTION` one part at a time with Diodes DS18004 Rev. 38-2's own words ("SURFACE MOUNT ZENER DIODE",
"Polarity: Cathode Band", type BZT52C12, ordered as "(Type Number)-7-F", LCSC C124196), the sheet copied unchanged from the
board A author's drafts into r4t's drafts/datasheets (sha256 0fbd7d13...). A sibling type (BZT52C15-7-F) is not read by
family. kisch.py is in every generator's identity, so this moves every board's provenance (section 4a), not a netlist.

## 1f. Round 6 fifth pass decisions

**R4T-D49. What sits behind a resistor on a gated rail is read, the rail's conductor runs through its shunts both ways,
and a firmware pin on it is named (the review of the fourth pass, blocking 1).** Taken by the session under the owner's
standing rule of 26 Sep 2026. `_second_sources()` now takes the rail, or the list of nets `_source_switch()` returns, and:
(1) THE CONDUCTOR. Every net a resistor under SHUNT_MAX_OHM (a current-sense shunt, or a 0 Ohm link) joins to a conductor
net, in either direction, is on the conductor, unless it is a supply by one of the three tests or a net a SUPPLY_FN pin
sits on (a link to those stays a feed, judged as before). At main 458b2873 this adds board A's PA_OUT (behind R55) and
HF_OUT (behind R65); board B's card rails do not change (their shunts were already on the path). (2) READ THROUGH. A
resistor on the conductor whose far net is not ground, not dead, not a supply by the three tests and carries no SUPPLY_FN
pin has its far net read with the rail's own rules: a second switch output or SW pin, a FET channel whose other end is not
ground (UNDECIDED when the gated switch drives its gate), a transistor fet_of cannot read, an OUTPUT_FN pin, a diode with
its cathode toward the rail, an inductor or bead to another net, a connector not declared an accessory; a resistor on that
net to a supply is judged as one on the rail is; and a resistor to a further net is read through the same way, until a
ground, a dead end, a supply or a net already read. (3) FIRMWARE PINS. A pin of a SOFTWARE_IO part on the conductor FAILS,
unless its maker's pin table gives it as a supply input, in which case the part runs from the rail and is a load; where
its function is only its net's name (a generated symbol) it is UNDECIDED; behind a resistor of 1 Ohm or more any such pin
is UNDECIDED. *Corrected in the sixth pass (R4T-D50, R4T-F21):* the fifth pass took "a supply input" from the pin's NAME
(`_POWER_FN`), and this text listed CM5_3.3V among the supplies such a part runs from. The Compute Module 5 datasheet says
the opposite: section 3.4, "Regulator outputs", gives CM5_+3.3V and CM5_+1.8V as regulators that "can each deliver up to
600 mA of current to external devices", and its pin table gives pins 84 and 86 as "CM5_3.3V (Output)" and 88 and 90 as
"CM5_1.8V (Output)", 300 mA per pin. The same pattern passed a CP2102N's VDD, which is its regulator's output whenever
VREGIN is powered (Rev 1.5, Table 3.6 and note 1), and, by its `(\w+_)?` prefix, any name only ending in a supply word
(GPIO24_VBUS, ADC_VIN, SENSE_3V3). Since R4T-D50 the maker's table decides, family by family.
(4) Board A's Q14 and Q24 are UNDECIDED, named with the U13 and U15 pins their other pins share (19, HDRV2; 18, SW2).
Options, and why these: (a) one resistor hop, as the review's simulation (rv9t/probe_farend_sim), or every chain: taken
every chain, because a feed behind two resistors in series is the same feed; on the six netlists nothing is found beyond
the first hop (r10t far_census). (b) A firmware pin on the conductor UNDECIDED or FAIL: taken FAIL, because the census
fails the same pin on a forced net and a 0 Ohm link to a net firmware drives is a link to a supply firmware switches; and
UNDECIDED behind a resistor, because the resistor bounds the current and whether that current can hold a transmitter up is
not judged here. (c) A shunt to a net carrying a supply pin: kept a feed (UNDECIDED unless loads) and not joined, because
joining it would pass a 0 Ohm link to a regulator input whose own source the netlist does not show. (d) Board A's power
stage UNDECIDED or accepted as U13's and U15's own: UNDECIDED, because SNVSAI1D 7.4.1 (v2/vendor/ti/lm5176-datasheet.pdf)
gives shutdown as "VCC off, No switching" and standby as "VCC on, No switching" and states no level for HDRV1 or HDRV2 (the
nearest row, 6.5's VUV(BOOT1,2), 3.4 V typical, "HDRV1,2 shut off", says the driver stops when its bootstrap supply falls,
not what holds the gate once VCC and BOOT are gone), so the citation the review allowed cannot be written from the held
sheet; and a stated low HDRV2 would still leave Q14's body
diode from PA_SW2, whose feed from VBAT runs through Q11's channel, the stage's own H-bridge, which this check does not model.
What moves: judge() on main 458b2873's six netlists, and check_contracts on the fourth pass's box regeneration, give the same
results and the same details as b3d645da (section 4f). With the asserted lines stubbed clean, board A's PA and HF stay
UNDECIDED and now name Q14 and Q24, and board B's two E72 radios move from PASS to UNDECIDED (R4T-F19).

## 1g. Round 6 sixth pass decisions

**R4T-D50. A pin of a part firmware sets is a load on a gated rail only by its maker's row (the review of the fifth pass,
blocking 1).** Taken by the session under the owner's standing rule of 26 Sep 2026. `_POWER_FN` is gone. `FW_PIN_TABLES`
holds, per family, the pins its maker's table gives as supply inputs, supply outputs, pins tied to another pin, and
grounds, each row in the maker's words, and `fw_pin_role()` reads a pin with it (`fw_family()` finds the row):
- RP2040 (Raspberry Pi RP2040 Datasheet, build-version 3184e62-clean, 1.4.2 Table 1): inputs IOVDD, DVDD, ADC_AVDD,
  USB_VDD, VREG_VIN; output VREG_VOUT ("Power output for the internal core voltage regulator, nominal voltage 1.1V, 100mA
  max current"); ground GND.
- STM32H7 (DS12110 Rev 10, 3.5.1 and 6.3.22 Table 91): inputs VDD, VDDLDO, VDDA, VDD50USB, VBAT; output VCAP (the VCORE
  regulator's); VREF+ tied to VDDA; grounds VSS, VSSA, VREF-. *Corrected in the seventh pass (R4T-D51, R4T-F24):* VBAT
  is not an input: it is tied to VDD (DS12110 6.3.24 Table 95, the battery charger firmware can switch on), and the row
  stands for the STM32H742, H743 and H753 only (DS12110 Rev 10 and DS12117 Rev 9, both held).
- PCA9555 (TI SCPS131J, Table 5-1): input VCC, "Supply voltage" (KiCad's symbol calls it VDD); ground GND (VSS).
- CP2102N (Rev. 1.5, 5.1 QFN28 Pin Definitions, Table 3.6 and its note 1): inputs VREGIN ("5V Regulator Input") and VBUS
  ("Digital Input. VBUS Sense Input"); VDD ("Supply Power Input / 5V Regulator Output") tied to VREGIN; ground GND.
- Compute Module 5 (datasheet release 3, 4.2 Table 4 and 3.4), by the module's own pin numbers, which board B's
  receptacles carry: inputs 5V (77 to 87 odd), VBAT (76, "RTC battery input") and GPIO_VREF (78; 2.9: "The GPIO bank is
  powered by the GPIO_VREF supply"); outputs CM5_3.3V (84, 86) and CM5_1.8V (88, 90); ground GND. *Corrected in the
  seventh pass (R4T-D51, R4T-D52, R4T-F24, R4T-F25):* VBAT (76) is not an input: it is tied to the module's 5V (the
  RTC's 3 mA charger, rtc_bbat_vchg); and a row read by pin number counts only where the symbol names the same row.
On a gated rail's conductor such a pin is a load when its row is an input (for the Compute Module only when its pin
number is that row). It FAILS when its row is an output, named as "a supply OUTPUT by its maker's table" with the row's
words; when it is tied and its partner sits on another live net (a CP2102N's VDD with VREGIN on +5V_DEV is its
regulator's 3.1 to 3.6 V at up to 100 mA; an STM32H7's VREF+ with VDDA elsewhere is the VREFBUF output firmware can enable,
up to VDDA at 4 mA static); and when it is the part's ground, which returns the part's supply current onto the rail. A
tied pin is a load when its partner shares its net and UNDECIDED when the partner is unconnected or not drawn. A pin
named only after its net stays UNDECIDED, except a Compute Module pin, which its number decides first (pin 84 so named
FAILS). A pin whose whole name is a supply word (`_SUPPLY_WORD`, anchored at both ends) and which no table places, on a
known family or on a part with no table, is UNDECIDED; a ground-named pin FAILS; every other name is a pin firmware can
drive and FAILS as before (GPIO24_VBUS, GPIO29_VSYS, ADC_VIN, SENSE_3V3 and VIN_MON among them). Behind a resistor every
firmware pin stays UNDECIDED (R4T-D49, unchanged). A family is found by the part's library symbol first (CM5A, CM5B), then
by the family named earliest in its value, so board B's PI7C9X2G404SL, TUSB8041 and KSZ9897, whose values mention the
CM5, are not read with the module's pin numbers (R4T-F22). *Corrected in the seventh pass (R4T-F25):* "earliest in its
value" still took a value that mentions "Compute Module 5" anywhere, so a PCIe switch whose value named the module WAS
read with its numbers; since R4T-D52 the family is found by the part itself.
Options, and why these: (a) the review's simplest form, a per-family list of input names, or a table that also names the
outputs, the tied pins and the grounds: taken the table, because a name list cannot say why a pin fails, and two of the
review's own cases are conditional (a CP2102N's VDD is an input or an output by where its VREGIN is). (b) The review
listed STM32 VREF+ among the inputs; taken tied to VDDA instead, because DS12110's Table 91 gives the pin as VREFBUF_OUT,
"Voltage Reference Buffer Output", which firmware enables, and IDDA(VREFBUF) is its "consumption from VDDA": with VDDA on
the same net the buffer is down whenever the rail is, with VDDA elsewhere it can drive the rail. (c) GPIO_VREF, which the
review's list does not name: taken as a Compute Module input, on 2.9's words and pin 78's row ("Must be connected to
CM5_3.3V (pins 84 and 86) ... or CM5_1.8V"). (d) A supply word no table places: UNDECIDED, not FAIL (it names a supply,
and nothing held says which way it goes) and not a load (a false load is silent); a firmware part's ground on the rail:
FAIL, where the fifth pass read it as a load, because the part's supply current returns through it onto the rail. (e)
The Compute Module by pin number, the other four by name: the module's numbering is its maker's and is the same on every
carrier, while the symbols' names are ours; the other families come in several packages, so their rows go by name.
What moves: nothing on the six netlists. On main 458b2873's and main's current netlists (01469100's, the same under v2/ecad
as main eadbe571), judge() and every option with the asserted lines stubbed clean give the same results and details with
bd3e93d5 and with the final file, and check_contracts on the r4t regenerations gives the same verdicts (section 4). The
walk meets four firmware pins on or behind a gated conductor on the six netlists, U16's and U17's RTS and DTR, all behind
R28 to R31 (R4T-F19), so fw_pin_role() is never asked about a pin on a conductor there. The supply outputs the tables name
on the boards sit on +3V3_CM1 to 3 and +1V8_CM1 to 3 (the Compute Modules), GNSS_3V3, ZBA_3V3, ZBB_3V3, RB_3V3 and board
D's SAU_3V3 (the CP2102N VDDs), IOCA_VCAP to IOCC_VCAP (the STM32H7 VCAPs) and C_DVDD (the RP2040's VREG_VOUT), none a
gated transmitter conductor (drafts/r11t/role_census.*), which is the review's own scan.

## 1h. Round 6 seventh pass decisions

**R4T-D51. Each part's VBAT is tied to the supply its charger runs from (the review of the sixth pass, blocking 1).** Taken
by the session under the owner's standing rule of 26 Sep 2026. `FW_PIN_TABLES` moves VBAT from the inputs to the tied pins
of two families:
- STM32H7: VBAT tied to VDD. DS12110 Rev 10 (v2/vendor/st/st-stm32h743xi-datasheet.pdf) says on page 1 "VBAT battery
  operating mode with charging capability"; its power supply scheme, Figure 15, draws "VBAT charging" from VDD; 6.3.24
  Table 95, "VBAT charging characteristics", gives RBC, the "Battery charging resistor", as 5 kOhm with VBRS = 0 in PWR_CR3
  and 1.5 kOhm with VBRS = 1. DS12117 Rev 9, the STM32H753's sheet (v2/vendor/st/st-stm32h753xi-datasheet.pdf), has the
  same rows as Figure 14 and Table 94. So firmware can connect VDD to VBAT through 1.5 kOhm, about 2.2 mA from 3.3 V.
- Compute Module 5: pin 76 tied to the module's 5V (pins 77 to 87 odd). The held datasheet calls VBAT only an "RTC battery
  input" (4.2 Table 4, 2.12.2 Table 3). Raspberry Pi documents the charger elsewhere: the RTC page
  (computers/raspberry-pi/rtc.adoc) says "The RTC is equipped with a constant-current (3 mA) constant-voltage charger.
  Charging of the battery is disabled by default", with charging_voltage_max 4400000; the firmware overlay README gives
  rtc_bbat_vchg, "If set to 0 or not specified, the trickle charger is disabled. (2712 only)"; and the module's own device
  tree, bcm2712-rpi-cm5.dtsi (compatible "raspberrypi,5-compute-module"), includes bcm2712-rpi.dtsi, which declares
  rpi_rtc with trickle-charge-microvolt and the rtc_bbat_vchg parameter (raspberrypi/linux rpi-6.18.y, the default
  branch). The four files are staged in drafts/datasheets/cm5/ for v2/vendor/cm5/, with their rows and README lines in
  drafts/vendor-rows-r4t.yaml (cm5_vbat_charger); tx_inhibit.py cites the v2/vendor/cm5 paths.
On a gated rail's conductor a VBAT is a load only when its partner sits on that conductor; with the partner on another live
net it FAILS, naming the charger; with the partner on ground, unconnected or not drawn it is UNDECIDED; behind a resistor it
is UNDECIDED as every firmware pin (R4T-D49). With it, three further changes of the same class:
(c) the STM32H7 row stands for the three parts whose sheets are held, STM32H742, H743 and H753 (the pattern was
`\bSTM32H7\d\d`, which also took the H72x and H73x lines, whose sheets add VDDSMPS, VLXSMPS and VFBSMPS and are not held):
a part outside them has no table, and its supply words are UNDECIDED (the review's minor 6);
(d) a tied pin's partner is looked for on the rail's whole conductor, the nets the caller walked as the conductor (the
switch-to-rail path and what its shunts and 0 Ohm links join) and every net a resistor under SHUNT_MAX_OHM joins to the
pin's own net, either way (minor 3); a partner on ground is named as such (minor 4);
(e) a supply input whose other pins of the same row sit on a live net off the conductor is UNDECIDED: a part's pins of one
supply are joined inside it (DS12110 Figure 15 draws the VDD pins as one domain), so it can carry that net onto the rail.
Options, and why these: (a) a VBAT whose partner is elsewhere: FAIL, or UNDECIDED because the charger is itself a resistor
(1.5 kOhm) or a 3 mA source and the behind-a-resistor convention could apply. Taken FAIL, because it is the same class as
an STM32H7's VREF+ and a CP2102N's VDD, which FAIL at 4 mA and at 100 mA: the rule asks whether anything but the switch can
feed the rail, not how much, and back-powering is an explicit EMCON proof item of the 26 Sep review. (b) The Compute
Module's partner: its 5V, or none (always UNDECIDED). Taken its 5V, because the module's only main power input is its 5V (4.2 Table 4,
pins 77 to 87 "5V (Input) ... main power input"), so a charger that runs while the module is powered can run only from what
the 5V brings in, and with the 5V on the rail it is down whenever the rail is. (c)
Narrow the pattern, or keep it and say which sheets the row stands for: taken narrowing, because a row believed for a part
whose sheet is not held is a load without a row. (d) The caller's conductor only (the review's suggestion), or also the
pin's own linked nets: taken both, because a VDDA across a 0 Ohm link sits on a net a supply pin is on, which the conductor
walk does not join (R4T-D49 (c)). (e) Split pins of one supply: PASS as before, FAIL, or UNDECIDED: taken UNDECIDED,
because the internal join is the plain reading of one supply but no held sheet states what current it passes.
What moves: nothing on main eadbe571's six netlists (section 4). Board B's STM32H743s have VBAT on the same net as VDD
(+3V3_IOCA to +3V3_IOCC), the Compute Modules' VBAT net is not a gated conductor, and the walk meets no firmware pin on a
gated conductor.

**R4T-D52. A part is read by what it is, not by what its value mentions, and a row read by the maker's pin number needs the
symbol to agree (the review of the sixth pass, blocking 2; closes R4T-F22).** Taken by the session under the owner's
standing rule of 26 Sep 2026.
(a) fw_family() and the new software_io() (which replaces the three `SOFTWARE_IO.search(value + lib)` calls in census(),
_network() and _second_sources()) find a part by its library symbol's name, anchored at its start, else by its value's first
words after at most a maker's name (Raspberry Pi, Microchip, Diodes, TI, ST, NXP, Silicon Labs and a few more), else, for
the Compute Module, by a receptacle's "(CM5 pins" form. The Compute Module is named in a value by its ordering code (CM5
and three digits), by "Compute Module 5", or by "CM5" followed by socket, receptacle, module or connector. A value that only
mentions the module or the panel controller does not make the part one.
(b) SOFTWARE_IO keeps its families and adds board B's three by their own part numbers, each on its maker's words for a pin
software sets: KSZ9897 (DS00002330D, 5.1.2.6 LED Override Register: "each LEDx_0 and LEDx_1 pin will function as an LED or
General Purpose Output (GPO)"), PI7C9X2G404SL (revision 5, GPIO[7:0] "programmed as either input-only or bi-directional pins
by writing the GPIO output enable control register"), TUSB8041 (SLLSEE4E, PWRCTL1 to PWRCTL4, and a hub "switches power on
or off to each downstream port as requested by the USB host").
(c) An input or a tied pin read by the maker's pin number counts as that row only when the symbol's pin function names the
same row, or is only its net's name; otherwise it is UNDECIDED, naming the number, the row and the symbol's name. An output
read by number still FAILS whatever the symbol calls it, and says so when they disagree.
Options, and why these: (a) the review offered two ways for the family: require the value to name the part, or apply the
numbers only to a symbol whose pins span the A side's 1 to 100. Taken the first, with (c), because a B-side symbol wrongly
numbered 1 to 100 also spans 1 to 100, and only the name check catches it. (b) SOFTWARE_IO anchored with the three part
numbers added, or anchored alone: taken with them, because anchoring alone takes board B's KSZ9897, PI7C9X2G404SL and
TUSB8041 out of the firmware class, and on a gated rail such a part's pins are then not read at all (R4T-F23), a silent load
where the sixth pass read UNDECIDED. *Corrected in the eighth pass (R4T-F26, R4T-D53):* the same holds for every family,
not only those three: anchoring took every firmware part whose value begins with a descriptor out of the class, and on a
gated rail its pins were silent loads. Since R4T-D53 such a part is UNDECIDED wherever an active pin of it is met, named. (c) The number decides (the sixth pass), the name decides, or both must agree: taken
both, because either can be wrong (our symbols are generated, the module's numbering is its maker's) and a disagreement is a
drawing error the tool should name, not resolve. (d) The words after "CM5": added because the review's own probe "CM5
socket" (a generic 2x50 symbol) FAILED on CM5_3.3V only through the mention-based SOFTWARE_IO; without them it would pass
silently.
What moves: nothing on the six netlists. Seven parts leave the firmware class: board B's six PCIe coupling capacitors C151,
C152, C251, C252, C351 and C352 ("CM5 datasheet 2.3.1"), which every walk skips by their reference, and J_PANEL (its value
mentions the RP2040), which every walk handles as a connector before it asks whether firmware sets a pin
(drafts/r12t/class_census.txt). Every other part reads the same class and family with both files.

## 1i. Round 6 eighth pass decisions

**R4T-D53. A part whose value or library symbol only mentions a firmware family is named wherever an active pin of it is
met, and never passed (the review of the seventh pass, blocking 1).** Taken by the session under the owner's standing rule
of 26 Sep 2026. fw_family() and software_io() stay anchored (R4T-D52): which rows are loads, and which parts a path FAILS
on, are still decided by the part itself. New: fw_mention() returns the part number a part's value or library symbol
mentions anywhere (SOFTWARE_IO searched over both, as the sixth pass searched it, and reported as the whole token,
"STM32H743VIT6", "CM5108032") when software_io() does not read the part as one. Where a walk meets an active pin of such a
part it is UNDECIDED, and the result names the family mentioned and says the part is not read as one: in _second_sources()
on the conductor and behind a resistor (before: not read at all, R4T-F23), in census() and in _network() (before:
UNDECIDED without the family). Options, and why this: (a) the review's first way, UNDECIDED for a mention; (b) its second,
the mention-based search for the firmware class with only the family anchored. Taken (a), because (b) puts board B's
J_PANEL and a level shifter "for the RP2040" back in the firmware class, where on a path each FAILS as a firmware pin
(R4T-F22's false FAILs), and it still reads a descriptor-led part with no family, so its supply-named pins are UNDECIDED
anyway and only its other pins FAIL; (a) answers the whole class the same way and says why. UNDECIDED and not FAIL,
because the tool does not know which pin of a part it does not read is an output, and a FAIL would claim what no table
has shown; RF-002 cannot read PASS either way. Board authors are told to begin every firmware part's value with its part
number (helper API point 1): the part is then read as what it is, and the UNDECIDED becomes its row's answer. A supply
input of such a part (a descriptor-led RP2040's IOVDD on the rail) moves PASS to UNDECIDED: a false UNDECIDED, seen, where
the alternative is a silent load.
What moves: nothing on main eadbe571's six netlists. The one part there that only mentions a family is board B's J_PANEL,
which every walk reads as a connector first, and the walks reach the mention test only for R4T-F23's four parts (board A's
INA226 U14, board B's E72s U13 and U14 and USBLC6 U33), none of which names a family (drafts/r13t/class_census.txt,
trace_mention.txt).

**R4T-D54. A supply row's other pins are every pin the maker's number places in it, whatever the symbol calls them (the
review of the seventh pass, blocking 2).** Taken by the session under the owner's standing rule of 26 Sep 2026. In
fw_pin_role() the split check (R4T-D51 (e)) and the tied-partner lookup (R4T-D51) read, for a row, every other pin of the
part the table places there: by the maker's pin number whatever the symbol calls it, else by the symbol's name. The
seventh pass kept only the pins whose symbol agreed, so a sibling misnamed ('+5V') or unnamed on another net was dropped
and the split read PASS. Now a pin that disagrees with the symbol and sits on a live net off the conductor makes the pin
judged UNDECIDED, naming the pin, its number, the row and the symbol's name ("pin 81 (the symbol calls it '+5V') on
+5V_S1 in its 5V row"). A partner on the conductor makes a tied pin a load whatever the symbol calls it (such a partner is
itself UNDECIDED where the walk meets it on the rail, R4T-D52 (c)); a partner the symbol agrees on, on another live net,
still FAILS the tied pin; one only the maker's number places there, on another live net, leaves it UNDECIDED. Options:
count a disagreeing sibling as if it agreed (the split's own UNDECIDED text), name it apart, or FAIL. Taken named apart,
because R4T-D52 (c) holds that a number-name disagreement is a drawing error the tool names and does not resolve, and the
review asked for that. What moves: nothing; board B's receptacles name every pin by function and put all six 5V pins of
each module on its slot's rail.

**R4T-D55. An STM32H7's VDD is a load only with its VBAT on the rail's conductor, on ground, unconnected or not drawn (the
review of the seventh pass, blocking 3; corrects limit (2) of R4T-D51 and R4T-D52, section 5).** Taken by the session under
the owner's standing rule of 26 Sep 2026. R4T-D51 read the tie one way: VBAT on the rail needs VDD there. The other way
round, VDD (with VDDA) on a gated rail and VBAT on another live net read PASS, and limit (2) justified it by saying that
DS12110 "states no path from VBAT to VDD". The held sheet contradicts that: DS12110 Rev 10 Figure 15 (page 103, the held
PDF sha256 9b27d1d9...) draws "VBAT charging" between the VDD and VBAT pins with no direction marked, and Table 95 (DS12117
Table 94 is the same) names it RBC, "Battery charging resistor", 5 or 1.5 kOhm by VBRS. Neither held sheet says the
resistor opens when VDD falls: 3.19's "VBAT power is switched when the PDR detects that VDD dropped below the PDR level" is
the backup domain's supply switch, not the charger, and RM0433 is not held. So once firmware has switched charging on, a
cell or a live net on VBAT can feed the gated rail through 1.5 kOhm after EMCON has opened the rail's switch: the path
R4T-D51 (a) counts as a feed ("whether anything but the switch can feed the rail, not how much"), and back-powering is an
EMCON proof item of the 26 Sep review. FW_PIN_TABLES gains a `reverse` key, set on the STM32H7 row as {"VDD": ("VBAT",
the words)}: a VDD on the conductor with VBAT on another live net is UNDECIDED, citing Figure 15 and Table 95 and saying
that the held sheets do not state the direction. VBAT on ground or unconnected is read as no path, as the review
required; DS12110 Table 21 note 1 (page 104) asks every main power pin, VBAT included, to be connected to the supply, so
the helper API gives the design answer as VBAT on the rail with VDD. Options: FAIL, UNDECIDED, or a load. Taken UNDECIDED, because the path is
drawn and its direction is not documented; a FAIL would claim a direction no held sheet states, and a load was the silent
answer the contradicted sentence justified. Scope: the STM32H7 row only. A Compute Module 5's 5V on the rail with its VBAT
on a live cell stays a load, named in limit (2): its held documents draw no element between the two pins; the Raspberry
Pi RTC page calls the cell "suitable for powering the RTC when the main power supply for the board is disconnected" and
the charger "a constant-current (3 mA) constant-voltage charger", a regulated source toward the cell, and says nothing of
a path from VBAT back to 5V (drafts/r13t/ds_excerpts.txt). One `reverse` entry adds it the day a held document or a
review reads those pages otherwise. What moves: nothing; board B's U41, U51 and U61 have VBAT on the same net as VDD
(+3V3_IOCA to +3V3_IOCC).

## 2. Findings made while doing the items

**R4T-F1. `port_protect.netlist()` and `check_contracts.load()` never read the last net of a KiCad netlist.** KiCad
9.0.9 closes the nets section on the last net's own line (`...)))))`). Measured on the committed netlists: A 282 nets,
281 read; B 1852/1851; C 144/143; D 172/171; E 118/117; P 39/38. Fixed in both (and `tx_inhibit.parse_netlist`) with
a regression fixture. The same look-ahead is still in five files r4t does not own, unchanged at main 26b80900:
`derate.py:87`, `clock_check.py:51`, `ground_system.py:39`, `power_sequence.py:44`, `netlist_board.py:62`. The
one-line fix is `(?=\(net \(code|\Z)`.

**R4T-F2. `kisch.py` is part of every board's generator identity.** The change makes every committed netlist
"UNKNOWN GENERATOR" until regenerated. The second fix-up's box run (/root/r5/t2) proves regeneration is
PARITY_AFTER_NOISE on all six, with 0 differing components and nets by an independent comparison.

**R4T-F3 (for the board A author). Four 62k resistors on board A have both pins on one net: R58 (PA_EN), R124
(HF_EN), R133 (PD_EN), R74 (POE_EN).** `gen_sch_a.py:243` (inside `lm5176()`) draws `r(ret, "62k 1%", en, N("EN"))`
and the four callers pass `en` equal to `N("EN")`. The rails still enable and still turn off under EMCON; had the
divider been formed as drawn, 3.3 V x 10k/72k = 0.46 V sits between the 0.4 V shutdown and the 1.22 V enable
threshold (SNVSAI1D), so the converter would have stayed in standby. Confirmed by review T.

**R4T-F4 (for the board B author), from the fix-up census on main 82dd1e4d:** (a) EMCON_HW runs straight to U41, U51
and U61 pin 33 (PC5 of the three STM32H753 supervisors): a firmware pin-direction error fights board C's U9 buffer and
can defeat hardware EMCON; this fails the EMCON_HW line and with it every transmitter on A and B. (b) Q106 and Q306
are bidirectional level shifters, so the AW7915-AED slots' W_DISABLE1# (J_M2C1 and J_M2C3 pin 56, undocumented by
AsiaRF) sit on EMCON_HW's conductor. (c) The six CM5 disable pins are driven by U6 (PCA9555) and EMCON does not reach
them (S-01). (d) VBUS_QMX is live under EMCON (R4T-D17). Remedies in drafts/r4-helper-api.md.

**R4T-F5 (for the board C author):** EMCON_HW runs straight to U3 pin 32 (RP2040 GPIO21), and TR_APRS reaches U3
pin 35 (an RP2040 GPIO) from board D's KEY through only R48 (100 Ohm).

**R4T-F6 (for the board D author):** KEY reaches U16 IO0_3 (PCA9555) through Q6 (G on +3V3_D8, S on KEY, D on
X_KEY), and TR_APRS is driven from KEY through R48 (100 Ohm) to board C's U3. Either lets firmware fight the SA868
keying gate; the SA868 FAILS RF-002 on it. Q7 on PA_KEY is the same shape on the PA bias path.

**R4T-F8 (for the board B author; second fix-up, from the review of the first fix-up): board B's three level
shifters Q106, Q206 and Q306 defeat EMCON_HW in its fail-safe states.** Each 2N7002 (JSCJ, LCSC C8545) has its drain on
EMCON_HW and its source on the module side, pulled up to +3V3_S1A, +3V3_S2A or +3V3_S3A through R137, R237 or R337
(10 kOhm), and 5G_W_DIS_n also carries the RM520N-GL's own 100 kOhm pull-up to 1.8 V. With the panel unplugged or its
3.3 V down, U9 no longer drives the line, and each body diode (anode on S, cathode on D, the sheet's Equivalent
Circuit) sources EMCON_HW from its slot rail against the 50 kOhm of R102 and R58. With the STM32 pins taken off (in
memory, drafts/box/second-fix-up/shifter_demo.txt) the line reads 3.05 V by the bound, and 2.4 to 2.5 V with a 0.55 to 0.7 V drop
assumed, against the gates' 0.8 V VIL: every EMCON gate on A and B reads "released" with the panel out, which RF-002
forbids ("asserted by the unpowered and disconnected states"). The remedy is a one-way open-drain buffer (74LVC1G07,
input on EMCON_HW, output on the module side with the existing pull-up) for ALL THREE, Q206 included: the first fix-up's
helper API wrongly accepted Q206 as it stood. Turning the FET round is not a remedy: with its gate on the slot rail its
channel conducts while EMCON_HW sits below 3.3 V minus Vth(GS), so R237 still lifts the line, up to 2.3 V at the sheet's
1.0 V minimum. Both remedies were run in memory on the regenerated board B: the buffers pass, the turned FET fails.
This supersedes R4T-F4 (b), which named only Q106 and Q306 and only as a driver-census question. Reported to the
board B author through this file and the round's report.

**R4T-F8, corrected in round 6 (for the board A and board B authors): the shifter remedy needs BOTH the buffers and
smaller pull-downs.** The 74LVC1G07 in place of Q106, Q206 and Q306 removes the body-diode path and adds three inputs of
5 uA each (TI SCES296AG 5.5, II) to a line whose pull-downs are 100 kOhm. With every pin's stated current in (R4T-D28),
board B's remedy measured in memory on the netlists at main faf8c981 (the STM32 PC5 pins and board C's RP2040 pin taken
off the line as R4T-F4 and F5 ask; drafts/box/leak_probe.py and leak_probe.txt): at A R102 and B R58 100 kOhm the line reads 2.75 V
with the panel unpowered (A, B and C: nine inputs and C's U9 IOFF, 55 uA on 50 kOhm), 4.50 V with J_AB1 unplugged and
the panel unpowered (B and C: 45 uA on 100 kOhm), 3.50 V with board B alone and 1.00 V with board A alone; at 22 kOhm on
both it still reads 0.99 V (B and C); at **10 kOhm on BOTH boards every state passes** (worst 0.45 V, B and C). Each
board's own pull-down must hold that board's own inputs alone, because of the unplugged states: 10 kOhm on A with
100 kOhm on B fails at 3.50 V, and 100 kOhm on A with 10 kOhm on B fails at 1.00 V. So: **board B, R58 10 kOhm and the
three 74LVC1G07; board A, R102 10 kOhm.** C's U9 then drives 3.3 V into 5 kOhm when EMCON is released, 0.66 mA. The
second fix-up's "the whole line then passes" with the buffers alone was wrong, and so was its tap example
(r4-helper-api.md is corrected).

**R4T-F8, stated a third time in round 6's second pass (for the board A and board B authors): 10 kOhm on B is not
enough, and the gates must state Ioff.** With every part at the worse of its powered and unpowered states (R4T-D37) and
the resistors and rails the adverse way (R4T-D36), measured in memory on the netlists at main faf8c981 with every remedy
applied (drafts/box/leak_probe2.py and leak_probe2.txt: B's STM32 PC5 pins behind one 74LVC1G34, C's RP2040 pin behind
one 74LVC1G34, Q106, Q206 and Q306 replaced by 74LVC1G07): with the SN74LVC08A quads kept (A's U26, B's U19 and U20) the
line is UNDECIDED at every pull-down tried (no Ioff row, and A's +3V3 or B's +3V3_DEV can be down while another rail's
gate reads the line); with one SN74LVC1G08 per EMCON_HW input it FAILS at 10 kOhm on both boards (1.00 V: J_AB1
unplugged, the panel unpowered, one slot rail up, 95 uA of Ioff and II on 10.5 kOhm) and at 10 kOhm 1% (0.96 V), and
PASSES at R102 10 kOhm 1% with R58 4.7 kOhm 1% (worst 0.45 V; all plugged 0.37 V, A alone 0.10 V, B alone 0.36 V).
So: **board B, R58 4.7 kOhm 1%, the three 74LVC1G07, a 74LVC1G34 for the STM32 taps, and one SN74LVC1G08 per EMCON_HW
input in place of U19's three sections and U20's one; board A, R102 10 kOhm 1% and two SN74LVC1G08 in place of U26's two
EMCON_HW sections; board C, U3's GPIO21 behind a 74LVC1G34.** C's U9 then drives 3.3 V into 3.2 kOhm when EMCON is
released, 1.0 mA. The round-6 statement "10 kOhm on BOTH boards, every state passes" is withdrawn: it held only in the
states round 6 solved.

**R4T-F9 (the second fix-up recorded it as an observation; ruled in scope by the review of that fix-up and judged by
tx_inhibit.own_supply() since round 6, R4T-D30).** A gate whose own supply fails drives nothing, and the enable or keying
pin it drove is then held only by what else is on its net. Measured on the netlists at main faf8c981, and with the
remedies in memory (drafts/box/f9_probe.txt):
- Board B, LIME_EN, RB_EN and E22_EN (U23 and U24 TPS25963x and U21 TPS22810, fed from +5V_DEV; their gate U19, an
  SN74LVC08A, on +3V3_DEV): FAIL, each floats with +3V3_DEV down, which TI forbids ("This pin cannot be left floating",
  SLVSDH0C 9.3.1; "Do not leave floating", SLVSET8A). With a 10 kOhm pull-down on each: UNDECIDED, not PASS, because the
  SN74LVC08A's sheet has no Ioff row (R4T-D29). With the pull-downs AND each gate an SN74LVC1G08 (Ioff 10 uA, SCES217AA,
  held): all three PASS (0.10 V against the 1.08 V off level). Recommended to the board B author: both. E72_EN needs
  nothing: U22's input is +3V3_DEV, the rail U19 loses.
- Board D, SA_PTT_n (U13, a 74LVC1G04 on +3V3_D8 from the LDO U1; the SA868 on +5V_SA through FB1): FAIL, the pin floats
  with the exciter powered. A pull-up on +3V3_D8 still FAILS (it dies with the driver). A 10 kOhm pull-up on +5V_SA holds
  it at 4.90 V against U13's IOFF and reads UNDECIDED, because the SA868 v1.3 sheet states neither an input current nor a
  '1' level for PTT, nor whether PTT takes 5 V; the board D author chooses the pull's rail and level, and what closes it
  is a NiceRF statement or a bench measurement. Powering the keying logic from +5V_SA would clear this check and break
  the circuit: at VCC 5 V the LVC inputs' VIH is 0.7 VCC (3.5 V) and TX_INHIBIT_n's released level is 3.3 V.
- Board A, PA_EN and HF_EN (U26, an SN74LVC08A on +3V3; R59 and R125, 10 kOhm): UNDECIDED at 0.07 V and 0.03 V from the
  known currents, because U26 states no Ioff and PA_EN also reaches board D's Q1 gate over the mezzanine harness, whose
  JSCJ 2N7002 states IGSS at 25 C only. Two SN74LVC1G08 in place of U26 close the first; the second needs a 2N7002 sheet
  that states IGSS over the envelope.
- Board B, the Compute Module 5 pins (S-01, not drawn yet): the open-drain element has to run from the module's own
  3.3 V output. On a carrier rail it FAILS: with that rail down the pin is held only by the module's own 1.8 kOhm pull-up,
  which is the pin "left floating", Wi-Fi on.
- ROUND 6 SECOND PASS, the board authors' drafts of this round judged in memory on main faf8c981 by the second-pass tool
  (drafts/box/board_remedy_probe.py and .txt; read from their worktrees' generators, not from a regeneration): board B
  (r4b: R514 to R517, 10k, on LIME_EN, RB_EN, E22_EN and E72_EN) takes LIME_EN, RB_EN and E22_EN from FAIL (floating) to
  UNDECIDED, the SN74LVC08A's missing Ioff being the only open item (0.00 V from the known currents), and E72 PASSES;
  board D (r6d: U13 an open-drain SN74LVC1G06, R88 1.2k from +5V_SA and R89 2k to ground) takes SA_PTT_n from FAIL to
  UNDECIDED in both the dead-U1 state (2.85 V from the known currents) and the released state (2.86 V), because the
  SA868 states no '1' level or input current for PTT and the LVC1G06 no powered off-state output current; its path is
  followed since R4T-D38 ("U13 INV_OD 2->4 released, held at 3.12 V by R88 1.2k to +5V_SA, R89 2k to GND"). The
  open-drain choice also answers the review's back-feed point (minor 6): a direct 5 V pull on a push-pull U13 on
  +3V3_D8 would back-feed that rail through U13's output, about 0.17 mA at 10 kOhm, and put 5 V on a PTT input whose
  range the SA868 sheet does not state; an open-drain U13 drives nothing against the divider, and the pin never sees
  more than 3.13 V.

**R4T-F12 (round 6 second pass; the review of round 6, blocking 1): the fail-safe states never took a board other than
the source's unpowered, and a line failed there that round 6 passed.** The review's probe5 (the test's own 47k/22k kit
with B's gates as 74LVC1G08) read PASS at 0.67 V at worst, while boards B and C unpowered with A powered read 1.05 V;
the recommended 10k/10k remedy read PASS, while the same state was UNDECIDED (B's U19 and U20 are SN74LVC08A). Both
reproduced and closed by R4T-D37: the probe5 kit now FAILS and names "boards B, C unpowered and A powered 1.10 V", the
10k/10k remedy with the quads is UNDECIDED, and with one SN74LVC1G08 per input it PASSES in the fixture (0.79 V at
worst, 10 kOhm at 5 percent) and FAILS on the real board B at 10 kOhm (R4T-F8, third statement). Round 6's "every state
passes with 10 kOhm on both boards" and the RF-002 row's "gap NONE with round 6's tx_inhibit.py" are withdrawn.

**R4T-F13 (round 6 second pass): the walk stopped at an open-drain output EMCON releases.** Board D's round-6 SA_PTT_n
(an open-drain 74LVC1G06 with a divider to receive) read "EMCON does not reach it", a FAIL that rested on the tool's walk,
not on the board. Closed by R4T-D38; fixtures both ways (the divider UNDECIDED, nothing pulling it FAIL, a divider
between VIL and VIH FAIL, and a released output with a pull-up onto a switch enable FAIL, "does not force off").

**R4T-F14 (round 6 third pass; the review of round 6's second pass, blocking 1): a supply whose name had no leading '+'
was not a supply to the tool.** (1) The per-reader bound never judged a reader running from one. The review's probes
(scratchpad rv7t), each read on e88aa46b and on round 6's first pass 0795c5de: probe_norail, U19 (a 74LVC1G08) on VCC_X
or 3V3_DEV with no pull-down, read PASS on e88aa46b and FAIL on 0795c5de; probe_bound_vs_exact, the same kit, the bound
PASS ("no gate that can be powered reads EMCON_HW") and the whole-board state C unpowered, B powered FAIL; probe_e2e, a
TPS22810 on VBAT with its EN/UVLO on EMCON_HW and no pull-down, powering the E22: the line and the LoRa PASS. It
contradicted R4T-D37 ("at least every whole-board state"), R4T-D39 (the fixture used "+VCC_X" only) and the RF-002 row's
gap NONE, which was tied to e88aa46b. (2) Found while fixing it, the same test in four more places: a pull-up to such a
supply lifted nothing in the fail-safe and own-supply solves (the net was walked as a floating signal: a 10 kOhm
pull-up from EMCON_HW to 3V3_AUX read PASS); a 0 Ohm link from one onto an enable EMCON forces low read PASS in the census
(followed as a conductor into a net holding nothing); _released_level skipped a pull it could not read, so a released
74LVC1G07 on an enable, pulled up to 3V3_AUX through 10 kOhm against 100 kOhm to ground, counted as forced OFF
(UNDECIDED only for the output's own current, where the switch is in fact held ON); and a logic element on a path whose
VCC had no '+' was "no supply pin on the netlist" to own_supply(). No board is affected today: every reader of an
asserted line is on a '+' rail (A U26 +3V3; B U19 and U20 +3V3_DEV; D U12 +3V3_D8) and nothing on a path pulls to an
unplussed supply, and the tool's output on the six netlists is unchanged. The trees do carry such supplies (A: VBAT,
the input of the LM5176s U13, U15, U16 and U19, the eFuses U21 and U22 and the AP64500s U4 to U7, and VIN_RAW, U2's; B: RB_3V3,
ZBA_3V3, ZBB_3V3, GNSS_3V3, PANEL_5V; D: SAU_3V3), so an eFuse enable or an S-01 gate on the module's own 3.3 V would
have passed unjudged. Closed by R4T-D41. Seven new fixtures and one extended fixture fail on e88aa46b and pass now
(t_a_reader_whose_supply_net_has_no_plus_is_judged, t_a_reader_with_no_supply_pin_on_the_netlist_is_its_own_domain,
t_a_switch_enable_on_the_line_whose_input_has_no_plus_is_judged, t_a_switch_readers_domain_is_its_input_rail_not_its_output,
t_a_pull_up_to_a_supply_whose_name_has_no_plus_is_not_ignored,
t_a_link_from_a_supply_whose_name_has_no_plus_onto_a_forced_enable_fails,
t_a_released_enable_pulled_to_a_supply_whose_name_has_no_plus_is_not_forced_off, and
t_the_bound_covers_every_whole_board_state_the_review_named with the VCC_X kit); t_board_a_pa_enable_with_its_pull_down
now takes the LM5176's domain from the tool's own _supply_nets (VBAT, its input), which e88aa46b does not have.

**R4T-F15 (round 6 fourth pass; the review of the third pass, blocking items 1 and 2): the third pass read four kinds of
EMCON defeat as PASS.** (1) In census(), a supply known only by its name stopped the walk and, on a net EMCON holds HIGH,
counted as a harmless pull, as did every other supply and any '+' rail whatever its voltage. The review's probes (scratchpad
rv8t), re-run on the final file: probe_level1b's four 0 Ohm and 1 kOhm links from SA_PTT_n to VCC_SENSOR, GPS_3V3 or
SIM1_VCC with an RP2040 GPIO on them FAIL (the GPIO named), the 0 Ohm link to SIM1_VCC on an M.2 UIM-PWR pin FAILS and the
1 kOhm one is UNDECIDED (5aece264: all eight PASS); probe_level1's links to +1V8, VCC_X, VDD_1V8, SIM1_VCC (0 Ohm and
1 kOhm, a GPIO on it) and a plain net FAIL and the 0 Ohm link to +3V3_X PASSES (at the level EMCON holds; 5aece264: every
one PASS but the plain net); probe_switched_rail
at level 1 reads EPD_VCC 0 Ohm FAIL and 1 kOhm UNDECIDED (5aece264: PASS, PASS) and EPD_RAIL PASS (a rail the P-FET
switches from +5V_SA, which only lifts the net EMCON's way, and nothing on it pulls down), and at level 0 all four FAIL
(5aece264: UNDECIDED for EPD_VCC 10 kOhm); probe_highline's U19 on VCC_X at 2.83 V FAILS (5aece264: UNDECIDED; R4T-D45).
Readings on the old and the final file side by side: drafts/box/r9t/review-probes/. (2) _second_sources() missed a resistor from a pin-map supply and every
transistor: probe_second_feed's VBAT on U21's VIN with 0 Ohm or 100 Ohm onto +5V_X FAIL (5aece264: PASS, PASS), and
probe_second_feed2's P-FET from +5V_DEV or VBAT with its gate on a GPIO FAIL (5aece264: PASS, PASS). Closed by R4T-D42 and
R4T-D43. No board is affected: on the six netlists at main 458b2873 judge(), fail_safe() and the walk give the same
results as 5aece264 (section 4a), and no forced net carries such a link.

**R4T-F16 (found while fixing the review's minor 2): a node with one reader off VCC_RANGE exempted every reader on it.**
_judge_fs() took a node as "in range" only if ALL its logic readers were, so an in-range gate or a switch enable beside a
reader on VCC_X at 1.4 V read UNDECIDED instead of FAIL. Readers are now judged one by one (fixture: the review's
probe_highline kit with a second 74LVC1G08 on +3V3_DEV, FAIL at 1.4 V; 5aece264 UNDECIDED).

**R4T-F17 (main moved to 458b2873 beneath the tools): board B's S-01 and board A's D22 were read as the tools' gaps.**
With 5aece264, board B's six module radios read "EMCON does not reach it, it is driven by Q109" (the walk had no OR and
did not follow a FET EMCON holds off), both AW7915 cards' supplies "no switch this file knows has its output on
+3V3_M2C1" (the 5 mOhm shunts), and board A's new D22 was UNJUDGED in the polarity pass. Closed by R4T-D46, R4T-D47 and
R4T-D48. What the walk now finds on board B, for its author (none moves a result, every B transmitter FAILS on its line):
(a) with +3V3_DEV down (R513's rail, and U111 to U311's supply) EMCON_ON floats and every KILL sits at 0 V, so the
W_DISABLE1# open drains and the module kill FETs release under EMCON: FAIL, the class of open item O-14; (b) the Compute
Modules' PCIE_PWR_EN pins (U30B and U32B pin 106) reach S1A_EN and S3A_EN through R164 and R364, 10 kOhm, against Q111 and
Q311: a pin whose direction firmware sets on a gated enable, FAIL until it is removed or declared a READER_TAPS entry
with the arithmetic that the FET wins (the 2N7002's on resistance is stated at VGS 5 V only, and the gate here is 3.3 V);
(c) even with both answered, a path through a 2N7002 EMCON holds off is UNDECIDED, because the fitted part states its
off-state current at 25 C only, and a net a 2N7002 forces low with a pull-up on it (5G_W_DIS_n with R237) is UNDECIDED
for the same sheet's on resistance.

**R4T-F18 (the review of the fourth pass, blocking 1): the second-feed check read a resistor's far end only through the
three supply tests, and R4T-D43's and R4T-D47's texts said more than the code did.** On b3d645da: probe_feed_via_link's
eight cases (a second TPS22810's output, EN on a GPIO, or an AO3401A's drain from +5V_DEV, gate on a GPIO, behind 0 Ohm or
1 Ohm onto X_ALT or LORA_PWR_B) PASS; probe_gpio_on_rail's three (an RP2040 GPIO on +5V_X directly, behind 0 Ohm, behind
100 Ohm) PASS; and board A's PA_OUT and HF_OUT, behind R55 and R65, are never read (probe_board_a_pa). No board result
moved, because board A's PA and HF FAIL on EMCON_HW and read UNDECIDED on U26's own supply with the line stubbed clean;
once board A's held U26 remedy lands both could have read PASS with their power stage unread. Closed by R4T-D49; R4T-D21,
R4T-D43 and R4T-D47 are corrected in place.

**R4T-F19 (for the board B author, found by R4T-D49): the E72 radios' gated rail +3V3_ZB is fed back through its reset and
bootloader pull-ups.** R28 to R31 (10 kOhm) pull ZBA_RST_n, ZBB_RST_n, ZBA_BSL and ZBB_BSL up to +3V3_ZB, and each of those
nets is driven by a CP2102N's RTS or DTR (U16 and U17, pins 24 and 28). The bridges run from +5V_DEV through their own
regulators (VREGIN and VBUS on +5V_DEV, VDD on ZBA_3V3 and ZBB_3V3), which EMCON does not switch, so with U22 off a bridge
holding RTS or DTR high feeds +3V3_ZB through 10 kOhm, and drives the E72's own RST and BSL pins directly (a pin of the
transmitter itself, outside this check, but the back-powering item of the review's EMCON table). R4T-D49 reads each of the
four as UNDECIDED, named. No result moves today (both E72s FAIL on EMCON_HW), but with the lines stubbed clean they read
UNDECIDED where b3d645da read PASS, so this is what stands once EMCON_HW is fixed. The remedy is the board B author's: the
pull-ups and the bridges' drive on a rail that is off whenever +3V3_ZB is off, or the bridge outputs gated, with the
back-powering of the E72's own pins answered in the same change.

**R4T-F20 (the review of the fourth pass, blocking 2): R4T-D46's fixture did not test the state R4T-D46 adds.** Its
DEFECTIVE case put R513 and the OR U111 on the same +3V3_DEV, where own_supply() stops at U111's own supply (KILL at 0 V
under Q109's 1 V), so the FAIL came from the OR and not from EMCON_ON losing its pull-up; with the pull-up-rail state
removed (rv9t/probe_d46_isolation's patch of _element) all eight S-01 and pull-up fixtures still passed. Closed by the split
case (R513 on +3V3_DEV, U111 on +3V3_CM1: FAIL, "the rail Q11's released net is pulled up to", "EMCON_ON floats") and a
power-path variant (a 2N7002 EMCON_HW holds off, pulled up on +3V3_P, gating a second 2N7002 onto a load switch's enable:
FAIL with +3V3_P down); both FAIL as fixtures with the state removed and pass as written (section 4f).

**R4T-F21 (the review of the fifth pass, blocking 1): R4T-D49 passed a firmware part's supply OUTPUT on a gated rail as a
load, and its decision text rested on a wrong reading of the CM5 datasheet.** `_POWER_FN` read any pin name that looked
like a supply as the supply the part runs from, and R4T-D49's text listed CM5_3.3V among those. The held datasheet says
the opposite (3.4 "Regulator outputs", up to 600 mA to external devices; pins 84 and 86 "CM5_3.3V (Output)", 88 and 90
"CM5_1.8V (Output)", 300 mA per pin); a CP2102N's VDD is its regulator's output whenever VREGIN is powered (Rev 1.5, Table
3.6, note 1); and the pattern's `(\w+_)?` prefix accepted any name ending in a supply word. On bd3e93d5 (rv10's
probe_supply_outputs and drafts/r11t/case_table) these read PASS on +5V_X: CM5_3.3V and CM5_1.8V at pins 84, 86, 88 and 90,
CM5_3.3V behind a 0 Ohm link, a CP2102N's VDD with VREGIN on +5V_DEV, RP2040 pins named GPIO24_VBUS, GPIO29_VSYS, ADC_VIN
and SENSE_3V3, an STM32H7's VREF+ with its VDDA on +3V3, an RP2040's GND, a Compute Module "5V" at a pin its maker gives
no 5V, a PCIe switch's VDDR and an SC16IS740's VDD. Each is a source of up to 100 to 600 mA, or an unread part, on a rail
EMCON switches off. Not a regression (b3d645da had no firmware-pin branch and passed them too), and no board result moves
(no firmware pin sits on a gated conductor on the six netlists). Closed by R4T-D50; R4T-D49's text is corrected in place.

**R4T-F22 (for the record, no board effect): SOFTWARE_IO's `\bCM5\d*` alternative matches any part whose value mentions
the Compute Module.** On board B that is the KSZ9897 U1, the PI7C9X2G404SL U101, U201 and U301, the TUSB8041 U102, U202 and
U302 ("ports 1-3 the CM5 slots", "up = CM5 lane", "upstream the CM5 USB3-0 port") and six PCIe coupling capacitors
("CM5 datasheet 2.3.1", skipped by their reference). The walks read those parts' pins as pins firmware sets: on a path
such a pin FAILS where an unproved active pin would read UNDECIDED, and on a gated rail a supply-named one is UNDECIDED
(R4T-D50). No walk meets any of them on the six netlists (no result names them; drafts/r11t/trace_firmware_pins.txt).
R4T-D50's family lookup does not share the fault (it finds the Compute Module by its library symbol, by "CM5" and a model
number, by "Compute Module 5" or by "(CM5 pins"). SOFTWARE_IO itself is left as it is, because narrowing it would turn a
FAIL into an UNDECIDED on a path and no review asked for that; whoever next edits it should anchor it the same way.
*Corrected in the seventh pass (R4T-F25):* the family lookup DID share the fault: it matched "Compute Module 5" anywhere in
a value, so a PCIe switch whose value named the module was read with the module's pin numbers. *Closed in the seventh pass
by R4T-D52:* the family lookup and software_io() read the part itself, and the KSZ9897, PI7C9X2G404SL and TUSB8041 stay
firmware parts by their own part numbers, so no path answer moves.

**R4T-F23 (named, not closed): the second-feed walk does not read a pin of a part that is none of the classes it knows.** In
_second_sources() a pin on a gated conductor or behind a resistor is judged when its part is a resistor, a transistor, a
switch this file knows, a diode, an inductor, a bead, a fuse or a connector, when its function is an OUTPUT_FN name, or when
firmware sets the part's pins. Any other pin is taken as a load without a word. At main eadbe571 the walk meets ten such
pins (drafts/r12t/trace/trace_new.txt, the same with 4836c42c): board A's INA226 U14 (three pins on PA_OUT and +13V8_PA,
named after their nets), board B's E72 modules U13 and U14 (each one's +3V3_ZB pin while the other is judged, and the RST
and BSL pins behind R28 to R31, R4T-F19) and board B's USBLC6 U33 (VBUS on +5V_LIME). None is shown by the tool to be a
load. Closing the class would judge every active pin on a gated rail, which moves board A's accepted sense network (fixture
_pa_sensed); it is for its own pass. R4T-D52 (b) keeps the parts whose pins software sets out of it. *Narrowed in the eighth
pass (R4T-D53):* a part whose value or library symbol mentions a firmware family anywhere is no longer in this class; an
active pin of it is UNDECIDED, named. The ten pins on the six netlists are unchanged (none of those parts mentions one).

**R4T-F24 (the review of the sixth pass, blocking 1): R4T-D50 passed an STM32H7's and a Compute Module 5's VBAT on a gated
rail as loads, although firmware can switch on a charger that drives current out of each.** On 4836c42c an STM32H753 or
STM32H743 with VBAT on +5V_X and VDD on +3V3, and a Compute Module 5's pin 76 on +5V_X with its 5V elsewhere or not drawn,
read PASS (drafts/r12t/case_table.oldtree.txt; the review's probe2). Not a regression (every earlier file passed them too),
and no board result moves. Closed by R4T-D51.

**R4T-F25 (the review of the sixth pass, blocking 2): R4T-D50's family lookup read a part whose value mentions the Compute
Module with the module's pin numbers, and the number decided an input whatever the symbol called it.** On 4836c42c a
PI7C9X2G404SL whose value says "on the Compute Module 5 PCIe lane" passed its pin 77 'VDDR' and pin 78 'VDD33' as the
module's 5V and GPIO_VREF, a KSZ9897 naming the module the same, and a receptacle-B symbol numbered 1 to 100 passed pin 77
'PCIE_CLK_P' as 5V. R4T-F22's sentence that the lookup did not share the fault was false and is corrected in place. Closed
by R4T-D52.

**R4T-F26 (the review of the seventh pass, blocking 1): R4T-D52's anchoring made a firmware part whose value begins with a
descriptor a silent load on a gated rail.** A regression against the sixth pass. software_io() read a part as firmware
only by its symbol's name or its value's first words, and _second_sources() reads no pin of a part outside the classes it
knows (R4T-F23), so on +5V_X these read PASS on 7fa144a0 where 4836c42c read FAIL (drafts/r13t/case_table.*.txt, and the
review's probes, rv12_probe.*.txt): an 'I/O supervisor STM32H743VIT6' on meshsat_ic:U41 with PA0, VCAP (DS12110 3.5.1),
or VREF+ with VDDA on +3V3 (Table 91); a 'Panel controller RP2040' on meshsat_ic:U10 (board E's own symbol style) with
VREG_VOUT or GPIO0; a 'USB-UART bridge CP2102N-A02-GQFN28' with VDD on the rail and VREGIN on +5V_DEV (Table 3.6); an 'I2C
expander PCA9555PW' with IO0_0; 'Slot S1 compute: CM5108032' with pin 84 CM5_3.3V (CM5 datasheet 3.4); a 'WeAct
STM32H743VIT6 core board' with PA0; a 'Seeed XIAO ESP32S3' with D0 (its 3V3 pin read UNDECIDED on 4836c42c). The same
STM32H743 with VBAT on the rail and VDD on +3V3 read PASS on both files: the review lists it as FAIL on 4836c42c, and its
own probe output reads PASS there (rv12_probe.4836c42c.txt), because the sixth pass counted VBAT as a plain input. On the
gate path the same MCU on EMCON_HW and the expander on the enable went from FAIL to UNDECIDED without the family (probe2).
No board result moves. Closed by R4T-D53.

**R4T-F27 (the review of the seventh pass, blocking 2): R4T-D51 (e)'s split check and the tied-partner lookup dropped a
sibling pin whose symbol name disagreed with the maker's pin number.** nets_of() kept only pins whose _row() agreed, so on
7fa144a0 (and on 4836c42c, which had no split check) a Compute Module's pins 77 and 79 named '5V' on +5V_X with 81 to 87
named '+5V' or unnamed on +5V_S1 read PASS, and so did VBAT (76) and pin 77 on the rail with 79 to 87 misnamed on +5V_S1
(probe4). CM5 datasheet 4.2 Table 4 makes pins 77 to 87 one supply, "5V (Input) ... main power input", so +5V_S1 reached
the gated rail through the module and the RTC charger ran from it. Named with the 5V pins named after their own net (the
split caught those, UNDECIDED); only the disagreeing-name path was open. No board result moves. Closed by R4T-D54.

**R4T-F28 (the review of the seventh pass, blocking 3): the reverse of the STM32H7's VBAT-VDD tie read as a load, and
limit (2) justified it with a sentence the held sheet's own figure contradicts.** An STM32H753's VDD and VDDA on +5V_X
with VBAT on +3V3_AON read PASS on both files (probe3). DS12110 Figure 15 draws the charging resistor between the two pins
with no direction marked (R4T-D55). No board result moves. Closed by R4T-D55; limit (2) is corrected in place, marked.

**R4T-F10 (round 6): board C's U9 and U12 have been 74LVC1G17 since main faf8c981, and the walk did not know them.** On
main the TX_INHIBIT_n line read UNDECIDED for U9's input alone and EMCON_HW's source was not found. Fixed in the tool
(R4T-D33); with it the TX_INHIBIT_n line PASSES in every fail-safe state (0.50 V with the panel unpowered: D's U12 input,
5 uA, and U9's IOFF, 10 uA, on 33 kOhm). The Diodes DS35124 sheet goes to v2/vendor (drafts/vendor-rows-r4t.yaml).

**R4T-F11 (round 6): the DFA-001 checklist missed 35 polarised footprints** (R4T-D35): every maker-named land (Texas
VQFN and UQFN, Sensirion DFN, Winbond USON, Bosch LGA, Skyworks MLPD, Vishay, Quectel, Ebyte), every package whose name
carries a prefix (HTSSOP-28, TQFP, TSOT, WQFN, TDSON, PowerPAK SO-8), the three-terminal Eaton SCF9550, and the
multi-pin connectors (the CM5 receptacles, the M.2 sockets, HDMI, RJ45, nanoSIM, U.FL, SMA). None has a rotation row, so
DFA-001 stays INCONCLUSIVE with 78 footprints to compare instead of 43. The list is drafts/ROTATION-CHECKLIST.r6.md; the
tracked v2/release/revA/order/ROTATION-CHECKLIST.md must be re-rendered with `assembly_set.py --checklist` when this
lands (the suite's test_assembly_set writes the same content into the tree).

**R4T-F7 (for the board E author; review minor 12, corrected on reading the generator):** D10 (SMCJ40A on DC_F) sits
AHEAD of the LM74700 ideal diode Q1 (`gen_sch_e.py`: J_DCIN, F1, DC_F, Q1, DC_P), so once it is drawn the right way
round a reversed source forward-biases it and it crowbars the 10 A blade F1. D1 (on DC_P) is behind Q1, whose body
diode is reverse-biased by a reversed source, so D1 is not reached. Acceptable only as a stated choice (D-16 makes
no surge claim); otherwise D10 moves behind Q1 or becomes a bidirectional part.

## 3. Review T: how each item was resolved

Blocking 1 (push-pull drive on the CM5 pins): fixed, R4T-D14. Fixtures in `tests/test_tx_inhibit.py`: a 74LVC1G08
straight onto pin 89 FAILS, a 74LVC1G34 FAILS, a 2N7002 level shifter FAILS, a carrier pull-up FAILS, a 74LVC1G07
open-drain buffer PASSES, the S-01 NAND plus N-FET-to-ground shape PASSES and FAILS with the expander still on the pin.

Blocking 2 (the driver rule only on the last net): fixed, R4T-D15 and D16. Fixtures: an expander behind a pass FET on
an intermediate net FAILS, an expander behind a series resistor FAILS, a GPIO on the asserted line fails the line and
every path from it, a software pin on the line on another board fails this board's transmitter, a diode that can lift
an enable brings its MCU in, a diode that can only pull the enable low is no threat, a declared tap counts only behind
its resistor, a module pin nobody documents behind a level shifter leaves the line UNDECIDED, an absent board the line
crosses is named. Board-side consequences reported: R4T-F4, F5, F6.

Blocking 3 (clamps the polarity pass could not see): fixed, R4T-D4 and D18. Fixtures in `tests/test_port_protect.py`:
a reversed SMAJ18A on D_TVS does not pass (UNJUDGED, not N/A), a reversed P6KE18A on D_Zener is a row and FAILS, an
unread part on D_Zener the right way is UNDECIDED without a declaration, a declared direction with its basis is read
from the intent, a declaration contradicting the part number FAILS; in `tests/test_kisch_tvs.py`: a direction said
for an unread part needs `basis=`, every call is declared in the intent, a declared return is found under either key.

Minor items: (1) counts corrected to seven reversed and nine right way round in kisch.py, port_protect.py, both
test files, the coverage rows and this file; (2) the MDD sheet for the fitted C113974 and C364296 was fetched (MDD
SMBJ5.0(C)A THRU SMBJ440(C)A, Rev:2025A7: SMBJ5.0A and SMBJ20A in the Unidirectional column), so the direction rests
on the maker's sheet for every fitted SMBJ/SMCJ code; (3) the drafts' datasheets are listed with target paths and
SOURCES.yaml rows in `drafts/vendor-rows-r4t.yaml` for the integrator (v2/vendor is not r4t's to write); (4) PRES
grounded accepted, R4T-D11; (5) the SMBus clamp return checked, R4T-D19; (6) LVC-only patterns, R4T-D8; (7) J_QMX
OWED and UNDECIDED, R4T-D17; (8) second feeds and supply pins, R4T-D21; (9) the inhibit_chain note now describes the
transmitter walk and the classification; (10) the RF-002 coverage row stays ENFORCED with gap NONE now that the three
blocking fixes are in, which is the file's own definition (an executable gate, a machine-readable verdict, fixtures
both ways); (11) both intent keys, R4T-D18; (12) board E, R4T-F7 (D10 only); (13) board B and C, R4T-F4 and F5.


### The review of the first fix-up (APPROVE_WITH_FIXES, four blocking items): how each was resolved

Blocking 1 (the PA, the QMX and the classification on A, C, E and P decide no rule since D22): resolved by R4T-D23, the
RF-002 row handed to the registry writer (boards_affected [a, b, c, d, e, p], condition has_schematic, acceptance
criteria naming the fail-safe states), with the E/P sentence of the coverage draft and the "RF-002 fails on A, B, C and
D" statements corrected here and in the report: until the row lands, inhibit_chain reads FAIL on A, B, C and D and RF-002
reads only B and D. Tests: the PA-gate case end to end through check_contracts, rules_lib.rules_for and
rules_status.result_for, and the guard that SKIPS in this tree naming a, c, e and p.

Blocking 2 (the disconnected and unpowered states are not measured; the helper API accepted Q206; the tap example):
resolved by R4T-D24 (fail_safe() in tx_inhibit.py) and R4T-F8 (board B's three shifters, Q206 included, remedy a
74LVC1G07 each; turning the FET round fails through its channel). The tap example is redone against the 50 kOhm
pull-downs: three taps need about 470 kOhm or more each, and the recommended remedy is the buffer. The JSCJ 2N7002
sheet for the fitted C8545 was fetched (drafts/datasheets, sha256 7941fb42...), for the body diode's direction (the
Equivalent Circuit), VSD (0.55 V to 1.2 V at 115 mA) and Vth(GS) (1.0 V to 2.5 V). Fixtures: the two the review asked
for (a 2N7002 shifter with a 10 kOhm pull-up on its far side, a 10 kOhm tap, each FAIL with 100 kOhm pull-downs only),
plus a floating line, the turned FET, the 74LVC1G07 remedy, a 1 MOhm tap and the kit's panel pair as it stands.

Blocking 3 (a diode to a rail or ground skipped before its orientation): resolved by R4T-D25. Fixtures both ways: a
BAT54 with its anode on +3V3_SW and its cathode on LORA_EN FAILS and the clamp the other way round passes; a forward
diode from SA_PTT_n (held high) to ground FAILS and the clamp passes; a diode on A1/A2 pins to a rail is UNDECIDED.

Blocking 4 (a series resistor in front of the anchor pin failed a correct path): resolved by R4T-D26. Fixtures: the S-01
NAND plus N-FET shape and a 74LVC1G07, each with 33 Ohm before pin 89, PASS; the SA868 key path with 100 Ohm before pin
5 PASSES. The reviewer's own probes (scratchpad rev5/edge.py and edge2.py) were re-run against the patched tool and read
as required.

Every new DEFECTIVE fixture was run against the tool as the first fix-up left it and fails there (13 in test_tx_inhibit,
3 in test_port_protect and test_kisch_tvs), and passes against this one.

Minor items: (1) the pull floor, R4T-D27; (2) a resistor from another rail onto a gated rail is a second feed,
R4T-D27; (3) a Compute Module pull-up after the last open-drain element and to a supply named without a '+',
R4T-D27; (4) vendor-rows-r4t.yaml corrected: board D's 74LVC1G08 (U12, U14) and 74LVC1G04 (U13) and board C's
74LVC1G34 (U9) are on boards today, so their sheets are needed in v2/vendor now; (5) kisch.py's tvs() comment and a
SOURCES.yaml note for the integrator say board E's D3 SMCJ18A (no code, maker TBD) is read by the family's numbering
convention, not its own maker's sheet; (6) r4-helper-api.md tells the board authors that every part on Device:D_Zener
is a clamp row and how to draw an ordinary Zener; (7) kisch.tvs() refuses a negative protected conductor and
port_protect judges a clamp on one with its cathode on the return (fixtures both ways); (8) port_protect judges a
suppressor whatever its reference prefix, leaving out only references that are never a diode by their exact prefix
(so CR1 is judged and R9 is not). Also found and fixed while doing blocking 2: tx_inhibit._ohms read "2m" (board P's
2 mOhm shunt) as 2 MOhm, because it lower-cased the unit.

### The review of the second fix-up (APPROVE_WITH_FIXES, two blocking items): how each was resolved, round 6

Blocking 1 (fail_safe() modelled no input leakage, so its result was not a bound, and the R4T-F8 remedy it proved does
not hold): resolved by R4T-D28 and R4T-D29 in tx_inhibit.py (every pin's adverse-sign maximum current from its sheet,
recorded in the LOGIC and SWITCHES tables with the sheet's words; a pin no sheet bounds leaves the state UNDECIDED), and
R4T-F8 corrected: the remedy is the three 74LVC1G07 AND R58 at 10 kOhm on board B AND R102 at 10 kOhm on board A. The
reviewer's arithmetic is reproduced by the tool on the netlists (A alone 1.00 V, B alone 3.50 V, A+B+C unpowered 2.75 V
at 100 kOhm; every state under 0.8 V at 10 kOhm on both). Fixtures both ways: the kit's own input count at 100 kOhm FAILS
and at 10 kOhm PASSES, and a pull-down changed on one board only FAILS either way round
(t_the_kit_emcon_line_with_the_shifter_remedy_needs_smaller_pull_downs); the lines as drawn fail on their inputs alone
(1.50 V with the panel out); the 74LVC1G07 remedy fixture FAILS at 100 kOhm (2.0 V) and PASSES at 10 kOhm; the panel pair
of the second fix-up FAILS at 100 kOhm (1.5 V, B's one input and C's U9 IOFF) and PASSES at 10 kOhm; TX_INHIBIT_n holds
at 0.50 V with the kit's inputs. The helper API's remedy and tap example are redone (taps: 220 kOhm or more each with
R58 at 10 kOhm; the buffer is still the recommendation). Sent to the board A and board B authors through this file, the
helper API and the round's report (no live author session was listed to message).

Blocking 2 (R4T-F9 ruled in scope): resolved by R4T-D30, tx_inhibit.own_supply(), run on every accepted path. Fixtures:
board A's PA_EN shape with R59 and a gate that states Ioff PASSES, with the SN74LVC08A board A carries it is UNDECIDED
(no Ioff row), and with no R59 it FAILS (t_board_a_pa_enable_with_its_pull_down); board B's E22_EN shape with no pull-down
FAILS and with 10 kOhm and a gate that states Ioff PASSES; a switch fed from the gate's own rail needs no pull (E72);
board D's SA_PTT_n FAILS with no pull and with a pull on +3V3_D8, is UNDECIDED with a pull on +5V_SA, and PASSES with the
keying logic on the exciter's own rail; the S-01 shapes on a carrier rail FAIL. On the boards: B's LIME_EN, RB_EN and
E22_EN FAIL (float) and D's SA_PTT_n FAILS (floats); A's PA_EN and HF_EN are UNDECIDED; E72_EN is not judged (shared
rail). Reported to the board B author (pull-downs, and gates that state Ioff) and the board D author (a pull on
SA_PTT_n toward '1' from a rail live whenever the SA868 is; what the tool reads with each choice). The RF-002 coverage
row keeps ENFORCED with gap NONE only together with round 6's tx_inhibit.py, and says so (drafts/r4-coverage-rows.yaml).

Also in the task: the part-number reader reads PESD12VL1BA (R4T-D34; board D's D10 and D13 now judged two-way, fixture
t_board_ds_microphone_clamp_is_judged_two_way_from_its_own_sheet), and assembly_set.py's POLARISED gap is closed
(R4T-D35, R4T-F11; fixtures t_a_land_named_after_its_maker_is_still_polarised and t_the_pin_count_is_read_from_the_netlist).
Found on the way: board C's 74LVC1G17 was unknown to the walk (R4T-D33, R4T-F10).

Minor items: (1) a pull against a FET-forced level is UNDECIDED (R4T-D32); (2) every fail-safe result says that a board
not named unpowered is taken as powered even where the state cuts its feed, which can only add sources; (3) the handed
RF-002 change also replaces false_positive_analysis (undocumented pins, unbounded leakage, unstated thresholds and
undrawn orientations are the new sources of a refusal that is not a pass); (4) tx_inhibit.py's report prints UNJUDGED,
naming the absent board, for a result that needed one (each result carries `absent`), with a fixture; (5) the kit's real
input count is a fixture (_kit, four boards). Also: a failure that rests only on an undrawn orientation is UNDECIDED
(R4T-D31), and the census's diode rule is unchanged.

Every new or changed fixture was run against the tools as the second fix-up left them and fails there (15 in
test_tx_inhibit, the new round-6 cases and the old ones whose expected answer the pin currents change, 2 in test_kisch_tvs and test_port_protect; the two assembly_set fixtures fail against the old file, whose
anchored POLARISED matches none of Texas_RSM0032A_VQFN-32, Sensirion_DFN-6, Eaton_SCF9550 and HTSSOP-28).

### The review of round 6 (APPROVE_WITH_FIXES, two blocking items): how each was resolved, round 6 second pass

Blocking 1 (fail_safe() powered down only the board carrying the line's source, and its "can only add sources" was
false): resolved by R4T-D37 (every other part at the worse of its powered and unpowered states, one reader at a time,
with the whole-board states solved exactly and named when the bound does not pass) and R4T-D36 (tolerances and rails
the adverse way). (a) The lines 580-584 comment and _state_name() no longer claim that a powered board can only add
sources; the tool's comment says why it was false (Ioff above II; an unpowered SN74LVC08A unbounded). (b) Fixtures both
ways: the review's probe5 kit, built as the probe built it, FAILS and names "boards B, C unpowered and A powered 1.10 V"
(it read PASS on round 6's tool, checked); the 10k/10k remedy with B's SN74LVC08A is UNDECIDED; the same with one
SN74LVC1G08 per input PASSES (0.79 V at worst in the fixture); the bound reads at least every whole-board state
(t_the_bound_covers_every_whole_board_state_the_review_named, t_the_kit_emcon_line_with_the_shifter_remedy_needs_smaller
_pull_downs). (c) R4T-F8 is stated a third time (board B: R58 4.7 kOhm 1%, the 74LVC1G07s, a 74LVC1G34 for the STM32
taps, one SN74LVC1G08 per EMCON_HW input; board A: R102 10 kOhm 1% and two SN74LVC1G08; board C: a 74LVC1G34 for U3), and
the helper API with it; on board B, U19 and U20 on EMCON_HW need parts that state Ioff or the line stays UNDECIDED. (d)
The RF-002 row's gap NONE is tied to the second-pass tx_inhibit.py by its sha256, and must read
SOURCE_OR_APPLICABILITY_UNRESOLVED with round 6's first-pass file. No netlist change. (Re-tied to the third pass's file
since: the review of the second pass found that e88aa46b never judged a reader whose supply net has no leading '+',
R4T-F14.)

Blocking 2 (the redone tap example sat at VIL): resolved by R4T-D40, the tap withdrawn and the buffer kept, with the
arithmetic recorded in the helper API (1 percent taps, 3.465 V: above 97 kOhm per tap with R58 at 4.7 kOhm; the tool
reads 0.785 V at 100 kOhm and 0.73 V at 120 kOhm, drafts/box/tap_probe.txt) and the reason it cannot PASS (each
supervisor's LDO can be down while another rail's gate reads the line, and an unpowered PC5's current is stated by no
held ST sheet: UNDECIDED at any value). Board C's tap option is withdrawn for the same reason. Text only.

Minor items: (1) the LM5176's enable current is 7.25 uA at the threshold from above (IEN(STBY) plus dIHYS(OP)), and the
AP64500's is not bounded (5.5 uA typical, no maximum), so a hold of it is UNDECIDED (R4T-D28 amended; fixtures
t_board_a_pa_enable_with_its_pull_down, 0.18 V, and t_an_enable_whose_current_at_the_threshold_no_sheet_bounds_is_undecided);
(2) tolerances and rails the adverse way, what stays nominal said in every result (R4T-D36; fixture
t_resistor_tolerance_and_rails_are_taken_the_adverse_way); (3) a reader outside VCC 3 V to 3.6 V is UNDECIDED, not
judged at 0.8 V (R4T-D39; fixture t_a_reader_on_a_rail_outside_the_lvc_range_is_not_judged_at_its_vil); (4) the FET
threshold's 25 C basis is recorded in R4T-D30, and a level-0 FET reader can no longer pass on it; (5) the held-at-the-
maker's-pull-up case stays UNDECIDED, recorded as conservative (R4T-D30 (b)); (6) the two test names now match their
assertions (t_a_documented_disable_pin_behind_a_level_shifter_is_accepted_and_the_fet_held_pull_leaves_it_undecided,
t_a_diode_that_can_only_pull_the_enable_low_drives_nothing_and_its_reverse_current_is_undecided); (7) the SA_PTT_n
remedy now prefers a divider and names the back-feed of a direct 5 V pull (about 0.17 mA through a push-pull U13 at
10 kOhm) and the unstated PTT input range, for the board D author, whose round-6 draft (an open-drain 74LVC1G06 with
R88 1.2k and R89 2k) avoids both and reads UNDECIDED with the tool (R4T-F9, round 6 second pass bullet); (8)
test_assembly_set's bare-flag test writes into a temporary file through MESHSAT_ROTATION_CHECKLIST, a default override
added to assembly_set.py, and asserts that the tracked ROTATION-CHECKLIST.md is unchanged; (9) nothing to do.

Found on the way: the walk stopped at an open-drain output EMCON releases, which would have read the board D author's
new SA_PTT_n as "EMCON does not reach it" (R4T-F13, R4T-D38, fixtures both ways).

Every new or changed fixture of this pass was run against round 6's first-pass tx_inhibit.py (kept in the session
scratchpad): 13 of test_tx_inhibit's fixtures fail there and pass now (the probe5 kit, the 10k/10k remedy both ways, the
panel pair and the one-way buffer at the adverse tolerance, the tap at 1 MOhm, the undrawn FET off state, the VCC range,
the AP64500, the LM5176's 7.25 uA, the tolerance fixture, the kit's drawn line and TX_INHIBIT_n readings, and the
open-drain release with a divider, which read "EMCON does not reach it" there). The release onto an enable with a
pull-up passes on both tools: it guards against the new walk turning that FAIL into a pass.

### The review of round 6's second pass (APPROVE_WITH_FIXES, one blocking item): how each was resolved, round 6 third pass

Blocking 1 (R4T-D37's per-reader bound never judged a reader whose supply net has no leading '+'): resolved by R4T-D41,
the review's option (b) in a sharper form: every reader's supply is read from its pin map (a logic part's VCC pin, a
switch's input pins), whatever the net is called, and a reader with none of its supply on the netlist is a domain of its
own. The fixtures the review asked for, each failing on e88aa46b: _panel(pull_down=None, u19_rail="VCC_X") and
"3V3_DEV" FAIL (floats at B U19 pin 1); the same with R58 10k UNDECIDED (0.16 V, "U19 pin 1 (VCC not named)"); the
end-to-end TPS22810 on VBAT with VOUT LORA_5V and EN/UVLO on EMCON_HW FAILS the line and the transmitter with no
pull-down and PASSES both with 10 kOhm (C's IOFF 10 uA and the enable's 0.1 uA on 10.5 kOhm, 0.11 V against VENF
1.08 V); t_the_bound_covers_every_whole_board_state_the_review_named carries the VCC_X kit. R4T-D37 and R4T-D39 are
corrected in place, the RF-002 row's gap NONE is re-tied to the third pass's tx_inhibit.py (its sha256 in section 4b),
with SOURCE_OR_APPLICABILITY_UNRESOLVED for e88aa46b and every earlier file. The review's probes read, on the third
pass's tool: probe_norail FAIL for every no-pull-down case and UNDECIDED for VCC_X at 100 kOhm (1.58 V, VCC not
named); probe_bound_vs_exact the bound FAIL and the exact state FAIL (both "floats at B U19 pin 1"); probe_e2e the VBAT
switch with no pull-down line FAIL and LoRa FAIL, the +5V_DEV switch FAIL and FAIL, and the VBAT switch with 10 kOhm PASS
and PASS. leak_probe2, tap_probe and board_remedy_probe read byte for byte as they did on e88aa46b. No netlist change.

Found on the way (R4T-F14 (2), closed by R4T-D41): a pull-up to a supply named without '+' lifted nothing, a 0 Ohm link
from one onto a forced enable read PASS in the census, and a released open-drain enable pulled up to one counted as
forced OFF; fixtures both ways.

Minor items: (1) and (2) verification notes, nothing to change. (3) A switch reader's domain is its input rail only,
not its output (R4T-D41; fixture t_a_switch_readers_domain_is_its_input_rail_not_its_output: U21's domain is
{+5V_DEV}, and a 74LVC1G08 on its output +3V3_LORA passes its Ioff, 10 uA, in that run instead of its II). (4) The helper
API's step 5 now names board C's U9 as the Diodes 74LVC1G17 (DS35124 Rev. 8-2: "IOFF Supports Partial-Power-Down Mode
Operation", IOFF +-10 uA). (5) The TR_APRS option "or R48 grows to a value declared as a tap" is withdrawn in the helper
API, with the reason: census() accepts a READER_TAPS entry only when its resistor is on the pin's own board (R48 is on D,
the pin on C), and an unpowered RP2040 pin would leave the line UNDECIDED anyway (R4T-D40). (6) A level-1 case is added
to t_resistor_tolerance_and_rails_are_taken_the_adverse_way: board D's round-6 divider (R88 1.2k 1% from +5V_SA, R89 2k
to ground) with a 74LVC1G08 input on it, held high: the pull-up at +1 percent, the pull-down at -5 percent, +5V_SA 5
percent low and the input's 5 uA out of the net, 2.90 V; it passes on e88aa46b as well (it covers what own_supply()
relies on, it found nothing new). (7) _released_level() reads a pull to a supply whose name states no voltage as "no
level" (the path is not reached, conservative), and the unreached result now carries why ("EMCON releases the open-drain
U5 and leaves LORA_EN to its pulls: pulled to 3V3_AUX through R70, a supply whose name states no voltage"; fixture
t_a_released_enable_pulled_to_a_supply_whose_name_has_no_plus_is_not_forced_off). (8) The box incident of the second pass
stays recorded in section 4b; this pass ran with TMPDIR under /root/r6/t and removed nothing outside it.

### The review of the third pass (APPROVE_WITH_FIXES, two blocking items): how each was resolved, round 6 fourth pass

Blocking 1 (R4T-D41 in census(): a supply known only by its name stopped the walk, and on a net EMCON holds HIGH counted
as a harmless pull): resolved by R4T-D42, taking both of the review's remedies. A pull to a supply is harmless at level 1
only to a '+' rail that states a voltage at or above 3.3 V; a pull to a supply whose voltage no name states is UNDECIDED at
either level; a 0 Ohm link to any such supply FAILS at either level, the test now ahead of the harmless `continue`; a
name-only supply is also walked, so a firmware pin on it FAILS as on e88aa46b; the P-channel branch takes the same rule.
The fixtures the review asked for: the four probe_level1b cases FAIL (the GPIO ones) or FAIL and UNDECIDED (the M.2 SIM
supply at 0 Ohm and 1 kOhm), and SA_PTT_n with a pull-up to +5V_SA still PASSES
(t_a_link_from_a_net_emcon_holds_high_to_a_supply_no_name_gives_a_voltage_is_not_harmless). R4T-D41's census sentence is
corrected in place. The five r4t test files and the six-board dump were re-run: no board result moves (section 4a).

Blocking 2 (_second_sources(): a transmitter rail fed around its EMCON-gated switch read PASS): resolved by R4T-D43. A
resistor from a '+' rail or a pin-map supply FAILS whatever its value; one to a name-only supply or a supply-pin net is
UNDECIDED unless its far net is only loads; a FET channel onto the rail FAILS, UNDECIDED only when the gated switch drives
its gate; an unreadable transistor is UNDECIDED. The fixtures: VBAT on U21's VIN with a 0R (and 100R) onto +5V_X FAILS
(t_a_feed_around_the_gated_switch_from_its_own_input_fails); a P-FET from +5V_DEV (and from VBAT) with its gate on a GPIO
FAILS (t_a_transistor_channel_onto_the_gated_rail_is_a_second_feed, which also carries the LM5176 gate-drive case, the
PNP and the acceptable discharge FET and gate); the existing +5V_DEV resistor fixture still FAILS. The checks the review
made are repeated on main 458b2873: board A's R50, R55, R60, R65, R163 and R165 end on no supply, and no FET channel
sits on a gated transmitter rail. The RF-002 row stays SOURCE_OR_APPLICABILITY_UNRESOLVED with 5aece264 and every
earlier file, gap NONE is re-tied to the fourth pass's file (sha256 in section 4a), and R4T-D21 and R4T-D41's "Left as
it was" sentence are corrected in place.

Minor items: (1) level 0 is recovered by the name-only walk: EMCON_HW with 10 kOhm to EPD_VCC, which a P-FET switches
from +3V3_DEV with its gate on a GPIO, FAILS naming Q5 (fixture t_a_pull_to_a_supply_known_only_by_its_name_is_walked_for_
its_drivers, on LORA_EN, the same walk). (2) R4T-D45: a logic reader whose supply states no voltage FAILS at or above its
family's vil_ceiling (probe_highline's 2.83 V FAILS; fixture t_a_line_at_a_level_no_supply_voltage_reads_as_low_fails_
whatever_the_readers_supply, with the own-supply threshold and R4T-F16's mixed node). (3) The claim is corrected: the
docstring says which nets the name test does not know and that they are walked as conductors, as the review measured
(at main 458b2873 board A's VIN_RAW is among them too); the second-feed check now also reads a supply-pin net at a
resistor's far end (R4T-D43). (4) Folded into R4T-D42: a pull to a '+' rail below the level EMCON holds is a load on the
driver and a 0 Ohm link to it FAILS (+1V8 in probe_level1). (5) R4T-D44: the anchor's supplies are read by pin function,
with the Compute Module 5's RTC pin 76 declared a backup pin from the maker's pin table (fixtures t_a_transmitter_supply_
whose_name_carries_a_control_word_is_still_its_own and t_a_backup_supply_pin_is_not_the_transmitters_own_supply). (6)
Verification notes, nothing to change.

Main moved to 458b2873 during the pass (boards A, B and D corrected). Reading its boards with the tools found three
more places where the tools, not the boards, decided the answer (R4T-F17): board B's S-01 walked (R4T-D46), its card
rails traced through their shunts (R4T-D47), and board A's D22 read from its sheet (R4T-D48). Each has fixtures both
ways that fail on the third pass's files.

### The review of the fourth pass (two blocking items): how each was resolved, round 6 fifth pass

Blocking 1 (_second_sources() read a resistor's far end only through the three supply tests; board A's PA and HF power
stages behind R55 and R65 never read): resolved by R4T-D49, the review's three required changes as written: the far net of
every resistor that is not ground, dead or a supply is read with the rail's rules (and so is every net behind it); a
SOFTWARE_IO pin is UNDECIDED behind a resistor and FAILS on the conductor itself; a resistor under SHUNT_MAX_OHM joins its
other side to the conductor both ways, so PA_OUT and HF_OUT are read and Q14 and Q24 are named UNDECIDED (not accepted:
SNVSAI1D states no gate-drive level in shutdown). The fixtures the review asked for, each run on b3d645da and on the final
file (section 4f): probe_feed_via_link's (a) and (b), 0 Ohm and 1 Ohm, to X_ALT and to LORA_PWR_B, FAIL (b3d645da: PASS),
with a feed behind two 1 kOhm resistors (b3d645da: PASS); a GPIO on +5V_X directly or through 0 Ohm FAILS and through
100 Ohm is UNDECIDED (b3d645da: PASS, PASS, PASS), with VIN_MON read as a GPIO; the _lm5176_stage case with Q4 behind a 6
mOhm shunt on PA_OUT reads UNDECIDED like Q4 on the rail (b3d645da: PASS behind the shunt, UNDECIDED on the rail), with
board A's own Q14 drawing and a P-FET from VBAT onto PA_OUT (FAIL); ACCEPTABLE, passing on both files: LED_5V_A1, the
feedback divider and the INA226 sense filter (the full sense network of board A in _pa_sensed), a 100 kOhm bleed and an LED
behind a 1 Ohm link, and an RP2040 running from the rail by its IOVDD and VREG_VIN pins. R4T-D43's and R4T-D47's texts, and
R4T-D21's, are corrected in place. The RF-002 row stays SOURCE_OR_APPLICABILITY_UNRESOLVED with b3d645da and every earlier
file, and its gap NONE is tied to the fifth pass's file (sha256 bd3e93d538c0f2ffbb701e77a8019954a767ad6a16990844c776b8de9a688c00;
since the sixth pass, to 4836c42cef8f700ec5bf29e8fdc1d00f9e8b57fbcab65bcce8f8e98bfa755cc2: R4T-F21).

Blocking 2 (t_board_bs_s01_fet_inverter_is_walked_and_judged_on_its_pull_up passed with R4T-D46's state removed): the split
case is added to that fixture (R513 on +3V3_DEV, U111 on +3V3_CM1: FAIL with "EMCON_ON floats" and "the rail Q11's released
net is pulled up to", and without "U111's supply"), its docstring now says which case the OR decides, and a power-path
variant is added (t_a_held_off_fets_pull_up_rail_down_floats_the_power_path: Q20 held off by EMCON_HW, INV_N pulled up by
R71 to +3V3_P, gating Q21 onto LORA_EN; FAIL with +3V3_P down; ACCEPTABLE with R71 on the switch's own +5V_DEV, UNDECIDED
for the 2N7002's figures with nothing floating). Both fixtures pass as written and FAIL with the state removed
(r10t d46_fixtures; R4T-F20).

### The review of the fifth pass (one blocking item): how it was resolved, round 6 sixth pass

Blocking 1 (R4T-D49's `_POWER_FN` passed a firmware part's supply OUTPUT on a gated rail as a load, and R4T-D49's text read
the CM5 datasheet the wrong way round): resolved by R4T-D50 as required. In `_second_sources()` a SOFTWARE_IO pin whose
maker's table makes it a supply output is a feed, FAIL on the conductor and UNDECIDED behind a resistor as for every other
firmware pin: the Compute Module 5's CM5_3.3V and CM5_1.8V, by their pin numbers 84, 86, 88 and 90 (datasheet 3.4 and 4.2
Table 4), and a CP2102N's VDD whenever its VREGIN sits on a different net (Rev 1.5, Table 3.6 and note 1). A supply-named
pin is passed as a load only when it is a supply input by its maker's table, per family (RP2040 IOVDD, DVDD, ADC_AVDD,
USB_VDD, VREG_VIN; STM32H7 VDD, VDDLDO, VDDA, VDD50USB, VBAT, and VREF+ only with its VDDA on the same net; PCA9555
VCC/VDD; CP2102N VREGIN and VBUS; CM5 5V, VBAT and GPIO_VREF), matched as the whole name, so a name only ending in a supply
word is not a load. The fixtures the review asked for, each run on bd3e93d5 and on the final file (section 4): CM5 pin 84
"CM5_3.3V" on +5V_X FAILS directly and through 0 Ohm (bd3e93d5: PASS, PASS), and so do pins 86, 88 and 90; a CP2102N's
VDD on +5V_X with VREGIN on +5V_DEV FAILS (bd3e93d5: PASS), and with VREGIN tied to VDD on the rail it PASSES as a load
(both files); an RP2040 pin "GPIO24_VBUS" on +5V_X FAILS (bd3e93d5: PASS), and so do GPIO29_VSYS, ADC_VIN and SENSE_3V3;
the RP2040's IOVDD and VREG_VIN on the rail still PASS (both files). R4T-D49's text and the helper API's point 1 are
corrected. judge() and the stubbed-clean dump on the six netlists of main 458b2873 and of main now: no result and no
detail moves. The RF-002 row stays SOURCE_OR_APPLICABILITY_UNRESOLVED with bd3e93d5 and every earlier file, and its gap
NONE is tied to the sixth pass's file (sha256 4836c42cef8f700ec5bf29e8fdc1d00f9e8b57fbcab65bcce8f8e98bfa755cc2).
*Corrected in the seventh pass (R4T-F24, R4T-F25):* the list above counted an STM32H7's VBAT and a Compute Module 5's
VBAT as supply inputs; each is tied (R4T-D51), and a row read by pin number needs the symbol to agree (R4T-D52). RF-002's
gap NONE is now tied to the seventh pass's file (section 4).

### The review of the sixth pass (two blocking items): how each was resolved, round 6 seventh pass

Blocking 1 (an STM32H7's and a Compute Module 5's VBAT counted as plain loads): resolved by R4T-D51 as required. VBAT is a
tied pin of both families, partnered with VDD and with the module's 5V: a load only with the partner on the rail's
conductor, FAIL with the partner on another live net (the message names DS12110 Table 95, RBC 5 or 1.5 kOhm by VBRS in
PWR_CR3, and for the module the 3 mA charger and rtc_bbat_vchg), UNDECIDED with the partner on ground or not drawn, and
UNDECIDED behind a resistor. The Raspberry Pi overlay README entry, the RTC page and the two device-tree files that put
the charger on the Compute Module 5 are staged in drafts/datasheets/cm5/ for v2/vendor/cm5/ with their rows
(drafts/vendor-rows-r4t.yaml, cm5_vbat_charger; v2/vendor is not r4t's to write). Fixtures both ways
(t_a_vbat_pin_is_tied_to_the_supply_its_charger_runs_from): DEFECTIVE, each reading PASS on 4836c42c: an STM32H753's and
an STM32H743's VBAT on the rail with VDD on +3V3 (FAIL now), the module's pin 76 with its 5V on +5V_S1 (FAIL), pin 76
alone on the rail (UNDECIDED), a VBAT with its VDD on ground (UNDECIDED); ACCEPTABLE, PASS on both: VBAT with VDD on the
rail, pin 76 with the module's 5V pins on the rail. R4T-D50's row list and the helper API's point 1 are corrected (the
first in place with a marked note), and so is the sixth pass's resolution text above (marked). RF-002's gap NONE is
re-tied to the seventh pass's file, and 4836c42c is listed as must-not-read-NONE. judge(), the stubbed-clean dump on the
six netlists and the suite are re-run (sections 4 and 6).

Blocking 2 (a part whose value mentions the module read with the module's pin numbers, and a pin number deciding an input
whatever the symbol said): resolved by R4T-D52, both of the review's changes. An input or a tied pin read by pin number is
that row only where the symbol names the same row or only the net, else UNDECIDED naming the disagreement; and the family,
and whether firmware sets the part's pins, are found by the part itself (its library symbol, its value's first words, or a
receptacle's "(CM5 pins" form). Fixtures (t_a_part_is_read_by_what_it_is_not_by_what_its_value_mentions): DEFECTIVE, each
reading PASS on 4836c42c: a PI7C9X2G404SL whose value names "Compute Module 5" with pin 77 'VDDR' or pin 78 'VDD33' on the
rail, a KSZ9897 naming the module with pin 77 'VDDIO', a receptacle-B symbol numbered 1 to 100 with pin 77 'PCIE_CLK_P', a
receptacle-A symbol with pin 77 'GPIO5' and one with pin 76 'PCIE_CLK_P' (all UNDECIDED now, named); ACCEPTABLE: the 5V
pins 77 to 87 still PASS, named '5V' (the sixth pass's fixture) or named after the net. R4T-F22's sentence and the limits
of section 5 are corrected.

Minor items: (1) and (2) record the review's reproduction. (3) The tied partner is looked for on the rail's conductor and on
every net a 0 Ohm link or a shunt joins to the pin's net (R4T-D51 (d)): the CP2102N whose VREGIN is across a 0 Ohm link now
PASSES (4836c42c: FAIL); an STM32H7's VREF+ with VDDA across one no longer FAILS as the VREFBUF output and stays UNDECIDED for
the link itself (a named limit, section 5); fixture t_a_tied_pin_is_judged_on_the_rails_conductor_and_a_grounded_partner_is_named.
(4) A partner on ground is named: "its VREGIN is on ground (GND)". (5) The module docstring now says pins 84, 86, 88 and 90.
(6) The STM32H7 row is narrowed to the H742, H743 and H753 and cites DS12110 and DS12117, both held (R4T-D51 (c));
fixture t_a_supply_input_split_across_nets_is_not_a_load reads an STM32H723 as having no table. (7) A CP2102N's VREGIN on
the rail with its VDD on another powered net stays PASS and is a named limit (section 5), with the STM32H7's VDD50USB beside
a VDD33USB elsewhere, the same shape. (8) The helper API's point 1 now says GPIO_VREF must be tied to CM5_3.3V or CM5_1.8V,
so on any gated rail it breaks the datasheet though the tool reads it as an input. (9) R4T-F22 is closed with blocking 2
(R4T-D52 (b)). (10) The commit subject is the integrator's; one that keeps the prototype framing and describes the tool:
"fix(tools): tx_inhibit ties each VBAT to its charger's supply and reads a part by what it is [MESHSAT-1357]".

### The review of the seventh pass (three blocking items): how each was resolved, round 6 eighth pass

Blocking 1 (R4T-D52's anchoring left a firmware part whose value begins with a descriptor a silent load on a gated rail):
resolved by R4T-D53, the review's first way. fw_family() and software_io() stay anchored; where software_io() is false and
SOFTWARE_IO finds a family anywhere in the value or the library symbol, _second_sources() (on the conductor and behind a
resistor), census() and _network() read the pin UNDECIDED, naming the family ("its value or library symbol mentions
STM32H743VIT6, a family whose pins firmware sets, and the part is not read as one"). Fixture
t_a_part_that_only_mentions_a_firmware_family_is_named_and_never_passed, run both ways: DEFECTIVE, each reading FAIL on
4836c42c and PASS on 7fa144a0 and UNDECIDED now: a descriptor-led STM32H743 with PA0 and with VCAP on +5V_X, 'Slot S1
compute: CM5108032' pin 84, a descriptor-led CP2102N's VDD with VREGIN on +5V_DEV, the review's RP2040, PCA9555, WeAct and
XIAO cases, and the MCU's PA0 behind 10 Ohm (4836c42c: UNDECIDED); the MCU on EMCON_HW is named by census() and by the
fail-safe network; the value led by the part number still FAILS. J_PANEL, the C151 capacitors and 'TXS0102 level shifter
for the RP2040' stay outside the firmware class (software_io False), and the level shifter's pin on a rail is named,
UNDECIDED, never FAILED as a firmware pin. Helper API point 1 tells board authors to begin every firmware part's value with
its part number; limit (5) is rewritten (section 5).

Blocking 2 (the split and tied-partner checks dropped a sibling whose symbol name disagreed with the maker's number):
resolved by R4T-D54 as required. Fixture t_a_supply_rows_pins_are_every_pin_its_maker_numbers_there, run both ways:
DEFECTIVE, each reading PASS on 4836c42c and on 7fa144a0: pins 77 and 79 on the rail with 81 to 87 named '+5V' on +5V_S1,
the same with 81 to 87 unnamed, and VBAT with pin 77 on the rail and 79 to 87 misnamed on +5V_S1, all UNDECIDED now,
naming each pin, its number, the row and the symbol's name; VBAT alone on the rail with every 5V pin misnamed on +5V_S1
now names the pins (7fa144a0: UNDECIDED, "not on this netlist"). ACCEPTABLE: every 5V pin on the rail, alone or with
VBAT, PASSES on all three files.

Blocking 3 (the STM32H7's VDD on the rail with VBAT on another live net read as a load): resolved by R4T-D55 as required,
UNDECIDED and not FAIL, citing Figure 15 and Table 95 and saying the held sheets do not state the direction. Fixture
t_an_stm32h7_vdd_is_a_load_only_with_its_vbat_on_the_rail_on_ground_or_nowhere, run both ways: DEFECTIVE, PASS on both
files: VDD and VDDA on +5V_X with VBAT on +3V3_AON (the STM32H753) and on +VBAT_CELL (board B's STM32H743); ACCEPTABLE,
PASS on all three: VDD with VBAT on the rail, VBAT on ground, VBAT unconnected, VBAT not drawn. Limit (2) and helper API
point 1 are corrected. The Compute Module 5's reverse (its 5V on the rail, VBAT on a live cell) stays a load, named in
limit (2) with the held Raspberry Pi pages' words.

Also: RF-002's gap NONE is re-tied to the eighth pass's file (sha256 dd584cc9b726d777276e0d341f8234f7c8d5e025f8bcdef6a13502f2e379edcd), and 7fa144a0 is
listed as must-not-read-NONE (drafts/r4-coverage-rows.yaml). judge(), the stubbed-clean options, check_contracts and the
suite are re-run (sections 4 and 6). A commit subject for the integrator that keeps the prototype framing: "fix(tools):
tx_inhibit names a part that only mentions a firmware family and reads a supply row by its maker's numbers [MESHSAT-1357]".

## 4. Results (round 6's eighth pass, runner)

Worktree r4t at 01469100 with its ten files uncommitted; main is at eadbe571, which changes nothing under v2/ecad since
01469100 (the six committed netlists, from `git show eadbe571:`, are in drafts/r13t/nmain/ and read A 2e8923d6, B 6048ee56,
C 2834f0d8, D f13d8b70, E d910e49c, P 4342c4cb), so every reading below holds for main as it stands. Only tx_inhibit.py and
tests/test_tx_inhibit.py changed in this pass, besides the drafts. Final: **tx_inhibit.py sha256
dd584cc9b726d777276e0d341f8234f7c8d5e025f8bcdef6a13502f2e379edcd** (the file RF-002's gap NONE is tied to), test_tx_inhibit.py sha256
cef8e3bf8a7b435e1736240e99a465168b8ff4e663a204fafdde7f3f00690e13. No box: neither file is in any generator's identity. Evidence in
drafts/r13t/ (README.txt there lists it).

- **Fixtures, both ways** (run_fixtures.py: the final test file against each tool file): against 4836c42c 89 passed, 7
  failed, 1 skipped; against 7fa144a0 93 passed, 3 failed, 1 skipped, the three being this pass's new fixtures, each at
  its first case (the descriptor-led STM32H743's PA0 read PASS; pins 81 to 87 misnamed on +5V_S1 read PASS; VDD with VBAT
  on +3V3_AON read PASS); against the final file 96 passed, 1 skipped (the RF-002 applicability guard)
  (fixtures_on_{4836c42c,7fa144a0,final}.log).
- **Case by case** (case_table.py, 29 cases, the three files, case_table.*.txt): blocking 1's 12 DEFECTIVE cases read
  UNDECIDED on the final file; on 7fa144a0 all 12 read PASS; on 4836c42c 10 read FAIL, the VBAT case PASS and the case
  behind 10 Ohm UNDECIDED. The CONTROL (value led by the part number) FAILS on all three. The level shifter 'for the
  RP2040' and a descriptor-led RP2040's IOVDD are named, UNDECIDED (7fa144a0: PASS on both); the PCIe coupling capacitor
  PASSES on all three. Blocking 2's 4 DEFECTIVE cases read UNDECIDED (7fa144a0: 3 PASS, 1 UNDECIDED; 4836c42c: 4 PASS);
  its 2 ACCEPTABLE cases PASS on all three. Blocking 3's 2 DEFECTIVE cases read UNDECIDED (PASS on both earlier files); its
  4 ACCEPTABLE cases PASS on all three. One NOTE case, the Compute Module 5's 5V on the rail with VBAT on a live cell,
  reads PASS on all three (limit (2), named).
- **The review's probes** (the scratchpad's rv12/probe.py to probe4.py, run on the three files, rv12_*.txt): every case
  the review called defective moves to UNDECIDED; the controls stay (the value-led STM32H743 FAILS, the value-led MCU and
  expander on the gate path FAIL); "RP2040 value led by descriptor, IOVDD on rail" moves PASS to UNDECIDED (R4T-D53, a
  false UNDECIDED by design); the other probe3 cases read as on 7fa144a0.
- **judge() on main eadbe571's committed netlists**: 25 results (6 PASS, 17 FAIL, 2 UNDECIDED), identical in result and
  detail with 4836c42c, with 7fa144a0 and with the final file; with the asserted lines stubbed clean (20 options: 12 FAIL, 8
  UNDECIDED), the same (dump.py, dump_main_{4836c42c,7fa144a0,final}.json). Per board (per_board.py, per_board_main.txt,
  equal to 7fa144a0's but the header): A 3 FAIL, 2 PASS (the EMCON_HW line FAIL, the TX_INHIBIT_n line PASS, the 30 W VHF
  PA and the QMX HF FAIL, the radio classification PASS); B 15 FAIL, 1 PASS, 1 UNDECIDED (EMCON_HW FAIL, TX_INHIBIT_n PASS,
  all fourteen transmitters FAIL: the LimeSDR, the RockBLOCK 9704, the E22, both E72s, the RM520N-GL, both AW7915 cards and
  the six on-module Compute Module radios; the classification UNDECIDED); C 1 FAIL, 2 PASS (EMCON_HW FAIL, TX_INHIBIT_n
  PASS, classification PASS); D 2 PASS, 1 UNDECIDED (TX_INHIBIT_n PASS, the SA868 exciter's keying UNDECIDED,
  classification PASS); E 1 PASS and P 1 PASS (the classification; neither carries a transmitter).
- **check_contracts on the r4t regenerations** (the seventh pass's scratch tree re-made in the session scratchpad with the
  final file, VERDICT_DIR there): **PASS of 96**; inhibit_chain A FAIL (fail 3, pass 6), B FAIL (15, 4, undecided 1), C FAIL
  (1, 5), D INCONCLUSIVE (pass 7, undecided 1), E PASS, P PASS; all thirteen verdict files equal to the seventh pass's in
  every field but tools and ts, and the log equal line for line (cc-final.log, verdicts/).
- **Main moved during the pass, to 44cfa045** (round 7b's integration: 93138ac1 merges r4t's kisch.py, port_protect.py,
  assembly_set.py and their tests byte-identical to the worktree's, and a check_contracts.py that runs the walk only where
  tx_inhibit.py is in the tree; tx_inhibit.py itself is not on main). Its six committed netlists are byte-identical to
  eadbe571's (the hashes above), so every reading in this section holds at 44cfa045. Main 44cfa045's own v2/ecad (git
  archive) with the final tx_inhibit.py added and main's check_contracts.py run there, VERDICT_DIR in the scratchpad:
  **PASS of 96**, RF-002's walk 17 FAIL, 2 UNDECIDED, 6 PASS, the log equal line for line to the regeneration run's but the
  verdict line, inhibit_chain A FAIL, B FAIL, C FAIL, D INCONCLUSIVE, E PASS, P PASS with the same counts
  (cc-mainhead.log, verdicts-mainhead/). The final test_tx_inhibit.py run in the same archive with run.py: 96 passed, 0
  failed, 1 skipped, the RF-002 applicability guard (fixtures_on_mainhead.log).
- **What the walks meet** (trace_mention.py: fw_mention() wrapped, judge and the clean options on the six netlists): the
  mention test is reached for four parts only, board A's INA226 U14, board B's E72s U13 and U14 and USBLC6 U33 (R4T-F23's
  ten pins), and none of them names a family, so no board result can move by R4T-D53.
- **Which parts are firmware parts, and which only mention one** (class_census.py, the six netlists): 30 firmware parts,
  class and family identical with 7fa144a0; one part only mentions a family, board B's J_PANEL ('the RP2040 panel
  controller's USB'), read as a connector by every walk first.
- Runner suite: section 6.

## 4h. Results (round 6's seventh pass, runner; kept for the record)

Worktree r4t at 01469100 with its ten files uncommitted; main is at eadbe571, whose two commits since 01469100 add
v2/docs/feasibility/EMCON.md and POWER-THERMAL.md and change nothing under v2/ecad (the six committed netlists are
byte-identical to `git show eadbe571:` of each, drafts/r12t/nmain/), so every reading below holds for main as it stands.
Only tx_inhibit.py and tests/test_tx_inhibit.py changed in this pass, besides the drafts and drafts/datasheets/cm5/. Final:
**tx_inhibit.py sha256 7fa144a099723bca060340e015889cb04e48d53fc50928db91790ca6c6b81b7a** (the file RF-002's gap NONE was tied to in the seventh pass), test_tx_inhibit.py
sha256 d958a82912e66a1183e9bea10e51452acbc7c7d98b391232a07c66c25868dc4b. No box: neither file is in any generator's identity. Evidence in
drafts/r12t/ (README.txt there lists it). *Since the eighth pass* RF-002's gap NONE is tied to dd584cc9... (section 4, R4T-F26 to
R4T-F28), and this file is must-not-read-NONE.

- **Fixtures, both runs.** test_tx_inhibit.py (final) against 4836c42c: 89 passed, 4 failed, 1 skipped, the four being the
  seventh pass's new fixtures, each failing at its first case: the STM32H753's VBAT with VDD on +3V3 read PASS
  (t_a_vbat_pin_is_tied_to_the_supply_its_charger_runs_from); the CP2102N tied across a 0 Ohm link read FAIL, minor 3's
  false FAIL (t_a_tied_pin_is_judged_on_the_rails_conductor_and_a_grounded_partner_is_named); the PI7C9X2G404SL naming the
  module read PASS (t_a_part_is_read_by_what_it_is_not_by_what_its_value_mentions); the split VDD read PASS
  (t_a_supply_input_split_across_nets_is_not_a_load). Against the final file: 93 passed, 1 skipped (the RF-002
  applicability guard) (fixtures_on_oldtree.log, fixtures_on_newtree.log).
- **Case by case** (case_table.py, 23 cases, both files): of 15 DEFECTIVE cases, 13 read PASS on 4836c42c and FAIL (3: the
  STM32H753's and STM32H743's VBAT with VDD elsewhere, the module's pin 76 with its 5V on +5V_S1) or UNDECIDED (10) on the
  final file, and 2 read UNDECIDED on both (pin 76 behind 10 Ohm; a CP2102N's VREGIN on ground, whose text now says so). Of
  7 ACCEPTABLE cases, 5 PASS on both, the CP2102N tied across a 0 Ohm link moves FAIL to PASS, and the VREF+ with VDDA across
  a 0 Ohm link moves FAIL to UNDECIDED. One NOTE case, GPIO_VREF on the rail with the 5V elsewhere, reads PASS on both, as
  the review allowed (minor 8).
- **The review's probes** (the scratchpad's rv11/probe.py, probe2.py and probe3.py, run on both files, rv11_*.txt): every
  case the review called defective moves: an STM32H7's VBAT on the rail (PASS to UNDECIDED with VDD not drawn, PASS to FAIL
  with VDD on +3V3), the module's pin 76 alone (PASS to UNDECIDED), the receptacle-B symbol numbered 1 to 100 (PASS to
  UNDECIDED), the PI7C9X2G404SL naming the module at pins 77 and 78 (PASS to UNDECIDED) and 84 (FAIL as CM5_3.3V to
  UNDECIDED: it has no table), the CP2102N across 0 Ohm (FAIL to PASS), the VREF+ across 0 Ohm (FAIL to UNDECIDED). Two
  cases move the other way, each because the part is now found as what it is: "CM5 socket" pin 77 '5V' (UNDECIDED to PASS:
  the value names the module's socket, so pin 77 is the module's 5V by number and by name), and a CP2102N whose value
  begins "RP2040 bridge:" (UNDECIDED to FAIL: its library symbol makes it a CP2102N, and its VDD with VREGIN on +5V_DEV is
  the regulator's output). The other 30 cases read the same on both.
- **judge() on main eadbe571's committed netlists** (A 2e8923d6, B 6048ee56, C 2834f0d8, D f13d8b70, E d910e49c, P
  4342c4cb): 25 results (6 PASS, 17 FAIL, 2 UNDECIDED), identical in result and detail with 4836c42c and with the final
  file, and equal to the sixth pass's reading; with the asserted lines stubbed clean (20 options: 12 FAIL, 8 UNDECIDED), the
  same (dump.py, dump_main_*.json). Per board (per_board.py, per_board_main.txt): A 3 FAIL, 2 PASS (the EMCON_HW line FAIL,
  the TX_INHIBIT_n line PASS, the 30 W VHF PA and the QMX HF FAIL, the radio classification PASS); B 15 FAIL, 1 PASS, 1
  UNDECIDED (EMCON_HW FAIL, TX_INHIBIT_n PASS, all fourteen transmitters FAIL: the LimeSDR, the RockBLOCK 9704, the E22,
  both E72s, the RM520N-GL, both AW7915 cards and the six on-module Compute Module radios; the classification UNDECIDED); C
  1 FAIL, 2 PASS (EMCON_HW FAIL, TX_INHIBIT_n PASS, classification PASS); D 2 PASS, 1 UNDECIDED (TX_INHIBIT_n PASS, the SA868
  exciter's keying UNDECIDED, classification PASS); E 1 PASS and P 1 PASS (the classification; neither carries a
  transmitter).
- **check_contracts on the r4t regenerations** (the sixth pass's scratch tree re-made with the final file, VERDICT_DIR in the
  scratchpad): **PASS of 96**; inhibit_chain A FAIL (fail 3, pass 6), B FAIL (15, 4, undecided 1), C FAIL (1, 5), D
  INCONCLUSIVE (pass 7, undecided 1), E PASS, P PASS; all thirteen verdict files equal to the sixth pass's in every field
  but tools and ts, and the log equal line for line (cc-final.log, verdicts/).
- **What the walk meets** (trace/: traced copies of both files, judge and the clean options on the six netlists): the same
  fourteen pins with both files, the four firmware pins behind resistors (U16's and U17's RTS and DTR, R4T-F19) and the ten
  pins of R4T-F23, so fw_pin_role() is never asked about a pin on a conductor there and no board result can move.
- **Which parts are firmware parts, and of which family** (class_census.py, both files, the six netlists): seven parts move
  out of the firmware class, board B's C151, C152, C251, C252, C351, C352 and J_PANEL (R4T-D52); every other part reads
  the same class and family with both files, board B's three STM32H743s included (STM32H7).
- Runner suite: section 6.

## 4g. Results (round 6's sixth pass, runner; kept for the record)

Worktree r4t at 01469100 with its ten files uncommitted; main is at eadbe571, which adds v2/docs/feasibility/EMCON.md and
POWER-THERMAL.md and changes nothing under v2/ecad, so every reading below holds for main as it stands. Only
tx_inhibit.py and tests/test_tx_inhibit.py changed in this pass; the other eight files are the fourth pass's (hashes in
section 4f). Final: **tx_inhibit.py sha256 4836c42cef8f700ec5bf29e8fdc1d00f9e8b57fbcab65bcce8f8e98bfa755cc2** (the file RF-002's gap NONE was
tied to in the sixth pass; in the seventh pass it was 7fa144a0..., section 4h, R4T-F24 and R4T-F25; since the eighth pass dd584cc9..., section 4), test_tx_inhibit.py sha256 85d2085cb842a72a47adb12bbfa08e46dbb558350aa966e88fce9bd2eb812418. No box: neither file is in
any generator's identity and kisch.py did not change, so the regenerations of section 4f (the fourth pass's A to E, the
fifth pass's P at 01469100) are still the current ones. Evidence in drafts/r11t/ (README.txt there lists it).

- **Fixtures, both runs.** test_tx_inhibit.py (final) against bd3e93d5: 87 passed, 2 failed, 1 skipped, the two being
  R4T-D50's new fixtures (t_a_supply_output_of_a_part_firmware_sets_is_a_second_feed, t_a_pin_is_a_load_only_by_its_
  makers_row), each failing at its first DEFECTIVE case (CM5 pin 84 and GPIO24_VBUS read PASS); against the final file:
  89 passed, 1 skipped (the RF-002 applicability guard) (fixtures_on_oldtree.log, fixtures_on_newtree.log). Case by case
  (case_table.py, 31 cases, both files): of the 22 DEFECTIVE cases, 16 read PASS on bd3e93d5 and FAIL (12) or UNDECIDED
  (4: a "5V" at pin 12, a CP2102N with VREGIN unconnected, the PCIe switch's VDDR, the SC16IS740's VDD) on the final file;
  4 read FAIL on both (VREG_VOUT, VCAP, VIN_MON, GPIO5; the first two now named as outputs); the Compute Module's pin 84
  named after its net moves from UNDECIDED to FAIL; CM5_3.3V behind 10 Ohm reads UNDECIDED on both, by design. All 9
  ACCEPTABLE cases PASS on both. The review's probe (rv10/probe_supply_outputs.py, run on both files,
  probe_supply_outputs.*.txt): its eight supply-output and name cases move from PASS to FAIL; its four other cases (a
  P-FET whose gate is the switch's EN net, 10 kOhm to LORA_BUSY read by a GPIO, two pull-ups on one signal, a monitor
  divider into an ADC pin) read the same on both files (UNDECIDED, UNDECIDED, FAIL, UNDECIDED).
- **judge() on the committed netlists** of main 458b2873 (A 2e8923d6..., B 6048ee56..., C 2834f0d8..., D f13d8b70...,
  E d910e49c..., P 3c925191...) and of main now (P 4342c4cb..., the rest the same): 25 results (6 PASS, 17 FAIL,
  2 UNDECIDED), the same results and details with bd3e93d5 and with the final file, and equal to the fifth pass's
  reading. With the asserted lines stubbed clean (20 options: 12 FAIL, 8 UNDECIDED), the same with both files and equal
  to the fifth pass's drafts/r10t/new_clean.json (dump.py, dump_*.json, dump_summary.txt).
- **What the walk meets** (trace_boards.py on a traced copy of each file, trace_firmware_pins.txt): on both netlist sets
  and with both files, four firmware pins on or behind a gated conductor, U16's and U17's RTS and DTR behind R28 to R31
  (R4T-F19), all behind a resistor, so fw_pin_role() is never asked about a pin on a conductor and no board result can
  move. Where the tables' supply outputs sit (role_census.py, the same on both netlist sets): the Compute Modules'
  CM5_3.3V and CM5_1.8V on +3V3_CM1 to 3 and +1V8_CM1 to 3, the five CP2102N VDDs on GNSS_3V3, ZBA_3V3, ZBB_3V3, RB_3V3
  and board D's SAU_3V3, the STM32H7 VCAPs on IOCA_VCAP to IOCC_VCAP and the RP2040's VREG_VOUT on C_DVDD; the supply
  words it cannot place are all on board B's KSZ9897, PI7C9X2G404SL and TUSB8041 (R4T-F22). None is on a gated
  transmitter conductor.
- **check_contracts on the r4t regenerations at 01469100** (the fifth pass's two scratch trees re-made, one with
  bd3e93d5 and one with the final file, VERDICT_DIR in the scratchpad): **PASS of 96** with both; inhibit_chain A FAIL
  (fail 3, pass 6), B FAIL (15, 4, undecided 1), C FAIL (1, 5), D INCONCLUSIVE (pass 7, undecided 1), E PASS, P PASS;
  every verdict file equal between the two files in every field but `tools` and `ts`, and the log byte-identical between
  them and to the fifth pass's (cc-oldtree.log, cc-newtree.log, verdicts-*/).
- Runner suite: section 6.

## 4f. Results (round 6's fifth pass, runner; kept for the record)

Worktree r4t with its ten files uncommitted, at main 458b2873 for the first half of the pass and fast-forwarded to main
01469100 for the second (main moved eight commits during the pass: b69f20db to 01469100, documents, review packets, the
evidence classing in rules_status.py and its tests, and ONE generator change, d90f30e4, board P's BQ7720700 TS pin on its
own thermistor: J_TS2, R34, TP15 added and R33 10k to 18k; none of them touches an r4t file or one of the four coverage
rows r4t replaces). Only tx_inhibit.py and tests/test_tx_inhibit.py changed in this pass; the other eight files are the
fourth pass's (kisch.py 98229aef..., check_contracts.py 52aac3f7..., port_protect.py 3f6d8b72..., assembly_set.py
721d3b56..., test_kisch_tvs.py fd47bffb..., test_port_protect.py f06d08c9..., test_smbus_lead_contract.py 43781679...,
test_assembly_set.py 5d01e9b5...). Final: **tx_inhibit.py sha256 bd3e93d538c0f2ffbb701e77a8019954a767ad6a16990844c776b8de9a688c00** (the file RF-002's gap NONE was
tied to in the fifth pass; since the sixth pass it is 4836c42c..., section 4, R4T-F21), test_tx_inhibit.py sha256 25bedf877a639841e4a21bfc01841143b34c7807c9be230c974e0f11a85b4ca2. Evidence under
the session scratchpad's r10t/ and copied to drafts/r10t/.

- **At main 458b2873: no box run, and why that was enough there.** Neither changed file is in any generator's identity,
  and kisch.py did not change, so the fourth pass's regeneration of main 458b2873 with the r4t files (netlists at parity
  with main, 0 differing components and nets in eighteen pairs, section 4a) is the current one. Its regenerated netlists, intents and provenance
  sidecars (drafts/box/r9t/out/r9t/<board>/regen/) were placed in two scratch copies of the worktree's v2/ecad, one with
  b3d645da and one with the final file, and check_contracts.py ran in each with VERDICT_DIR in the scratchpad: **PASS of 96
  in both; inhibit_chain_<letter> (RF-002): A FAIL (fail 3, pass 6), B FAIL (fail 15, pass 4, undecided 1), C FAIL (fail 1,
  pass 5), D INCONCLUSIVE (pass 7, undecided 1), E PASS (1), P PASS (1), identical in both apart from provenance**, and equal
  to the fourth pass's box reading. The tool's table (`tx_inhibit.py` on those netlists) is byte-identical between the two
  files and equal to the box's r9t-final table.
- **judge() on the committed netlists of main 458b2873**: the same 25 results (6 PASS, 17 FAIL, 2 UNDECIDED) and the same
  details with b3d645da and with the final file. With the asserted lines stubbed clean (r10t dump_clean): board A's PA and
  HF stay UNDECIDED and now name Q14 and Q24 behind R55 and R65; board B's E72 coordinator and RCP move from PASS to
  UNDECIDED (R4T-F19); every other option reads as before.
- **Fixtures, both runs.** test_tx_inhibit.py (final) against b3d645da: 84 passed, 3 failed, 1 skipped, the three being
  R4T-D49's new fixtures (t_a_feed_behind_a_link_onto_a_net_no_supply_test_knows_is_read_through, t_a_firmware_pin_on_the_
  gated_rail_is_named, t_a_power_stage_behind_its_sense_shunt_is_read_like_the_rail); against the final file: 87 passed, 1
  skipped (the RF-002 applicability guard). Case by case (r10t case_table, both files): every DEFECTIVE case of R4T-D49
  reads PASS on b3d645da and FAIL or UNDECIDED on the final file, except the control case of Q4 on the rail, UNDECIDED on
  both; every ACCEPTABLE case PASSES on both. R4T-D46's fixtures (r10t d46_fixtures): t_board_bs_s01_fet_inverter_is_walked_
  and_judged_on_its_pull_up and t_a_held_off_fets_pull_up_rail_down_floats_the_power_path PASS as written and FAIL with the
  pull-up-rail state removed; the three other open-drain and OR fixtures pass either way, as they should.
- **The review's probes** (r10t probes, old and new): probe_feed_via_link, the eight X_ALT and LORA_PWR_B cases FAIL
  (b3d645da: PASS), +5V_ALT unchanged (FAIL); probe_gpio_on_rail FAIL, FAIL, UNDECIDED (b3d645da: PASS x3);
  probe_board_a_pa names Q14 and Q24 from the rail's own call; probe_d46_isolation reads as before (it patches the tool,
  whose behaviour did not change). probe_pa_line_clean's "as written" half reads PA and HF UNDECIDED naming Q14 and Q24;
  its simulation half and probe_farend_sim's wrap `_second_sources()` with a single-net signature and stop with a
  TypeError on the final file, which now takes the conductor's list of nets in one call (so a resistor between two nets of
  the path is not read as a feed); their simulation is what R4T-D49 does.
- **At main 01469100: board P regenerated on the box, the rest re-read.** `sch_prov.current` in the r4t tree at 01469100
  accepts the fourth pass's regenerations of A to E and refuses P's (changed input: gen_sch_p.py), so P alone was
  regenerated (`drafts/box/r10t_box.sh`, vast.ai 52646493, KiCad 9.0.9, 2026-09-26 16:31:49Z to 16:32:15Z, in two trees:
  `base-01469100.tgz`, git archive of main 01469100, sha256 33c86426..., and `r10t.tgz`, the same with the ten r4t files
  over it, sha256 2aef3b2f...; `diff -rq` names exactly the ten). gen_sch and build_sch exit 0 in both, at P's committed
  phase label; **netlist: PARITY_AFTER_NOISE for committed against each regeneration and for base against r10t, and the
  independent comparison (`drafts/box/netlist_par_p.py`) finds 0 differing components and 0 differing nets in all three
  pairs, 85 components and 55 nets**; intent DIFFERENT in the key `clamps` alone (S-09, R4T-D18) and provenance in
  `generator_sha` and `generator_file_sha` alone (R4T-F2); BOM PARITY, ERC PARITY_AFTER_NOISE. P's schematic-phase gates:
  TRN-001 (port_protect) PASS in both trees (base: of 0, no polarity pass; r10t: of 3, D1 OK, D2 and D3 two-way). Results
  `r10t-results.tgz` sha256 eb6516e7..., unpacked in `drafts/box/r10t/out/` (its SHA256SUMS verifies). Then, on the runner,
  with P's new regeneration beside the fourth pass's A to E in scratch copies of the worktree at 01469100: check_contracts
  **PASS of 96** with both files (the five P and E SMBus lead contracts among them, PASS); **inhibit_chain A FAIL (3/6), B
  FAIL (15/4/1), C FAIL (1/5), D INCONCLUSIVE (7 pass, 1 undecided), E PASS, P PASS, the same as at 458b2873 and the
  same with both files**; the tool's table identical between the two files and to the one at 458b2873; judge() on the
  committed netlists of 01469100 the same 25 results and details with both files. The evidence is in
  `drafts/r10t/at-01469100/`. assembly_set's checklist was not re-rendered: it reads the layouts, which d90f30e4 did not
  regenerate (P4 stands), and needs pcbnew, which the runner lacks.
- Runner suite: section 6.

## 4a. Results (round 6's fourth pass, box run and runner suite; kept for the record)

Worktree r4t moved from main faf8c981 to main 458b2873 by a fast-forward of its own branch (fnd/r4t): none of the ten r4t
files is touched by 1f614233 or 458b2873, so the uncommitted changes carried over unchanged. Main moved again during the
pass, to b69f20db (the case margins, the D-08 reversal and the transport correction): it touches documents, v2/vendor/peli,
pcb_envelope.yaml and ENV-001's coverage row only, no netlist, generator or r4t file and none of the four coverage rows
r4t replaces, so the ten files apply onto it unchanged; the runs below are on 458b2873. Box `/root/r7/t` (vast.ai
52646493, KiCad 9.0.9, Python 3.12.3, pdftoppm present; disk at 41 percent before and after), `drafts/box/r9t_box.sh` from
2026-09-26 15:19:56Z to 15:28:06Z, then `drafts/box/r9t_final.sh` (to 15:33:11Z) with the last tx_inhibit.py (R4T-D46,
R4T-D47), test_tx_inhibit.py and board_remedy_probe.py (it unpacks `_source_switch()`'s new fourth value). None of those
three is part of any generator's identity, so the regeneration and its parity stand. Two trees: `base-458b2873.tgz` (git
archive of main 458b2873: v2/docs, v2/ecad, the order folder's ROTATION-CHECKLIST.md and jlc-rotations.csv; sha256
7a23887f...) and `r9t.tgz` (the same paths with the ten r4t files over them, sha256 c31a0f80...); `diff -rq` names exactly
the ten. Every temporary file went under `/root/r7/t/tmp`, nothing outside `/root/r7/t` was touched, and `/root/r7` was
removed after the fetch. Results `r9t-results.tgz` sha256 8976237e3b9f99ba5259e0a8c9642d0b13d2aeb8c3a8e0a0cda43f4c8ece535b,
unpacked in `drafts/box/r9t/` (both SHA256SUMS verify). Tool hashes on the box (`out/r9t-final/files.sha256`) equal the
worktree's final files, test_tx_inhibit.py df0cf499..., kisch.py 98229aef..., check_contracts.py 52aac3f7...,
port_protect.py 3f6d8b72..., assembly_set.py 721d3b56..., test_port_protect.py f06d08c9..., test_kisch_tvs.py fd47bffb...,
except tx_inhibit.py: the box and the runner suite ran 82b0c499..., and the final file is
**b3d645da5d0c47f09126c80ba61f00b0f6858b6af716158e78f8e8006d2e0b25** (the file the RF-002 row's gap NONE was tied to in the fourth pass; in the fifth pass bd3e93d5..., section 4f; since the sixth pass 4836c42c..., section 4), which
differs from it in two comments and one sentence of the module docstring only (two statements about boards B and D and
the logic families that main 458b2873 had made stale): their syntax trees without the module docstring are equal, the
five r4t test files read 153 passed, 3 skipped with it on the runner, and the six-board dump is byte-identical.

- Regeneration: gen_sch exit 0 and build_sch exit 0 on all six boards in both trees, each at its committed Phase label.
- **Netlists: no difference, so no finding ID applies to any netlist line.** Committed (main 458b2873) against each
  tree's regeneration, and base regeneration against r9t regeneration: PARITY_AFTER_NOISE on A, B, C, D, E and P
  (regen_compare.py pair netlist); the independent comparison (`drafts/box/netlist_par_r9t.py`) finds 0 differing
  components and 0 differing nets in all eighteen pairs: A 576/341, B 1103/1929, C 204/146, D 227/180, E 179/124, P 82/54
  (`drafts/box/netlist_par_r9t.txt`).
- **The other artefacts, base regeneration against r9t regeneration, every difference with its finding:** intent, boards D
  and P: DIFFERENT in the key `clamps` alone (S-09, R4T-D18); provenance, all six: DIFFERENT in `generator_sha` and
  `generator_file_sha` alone (R4T-F2, and R4T-D48 changed kisch.py again); intent on A, B, C and E, BOM and ERC on all six:
  PARITY or PARITY_AFTER_NOISE.
- Schematic-phase gates, identical in both trees except TRN-001 (the power_path logs differ in the tree path of a
  SyntaxWarning only): ERC gate PASS on all six (A 1450, B 2398, C 300, D 413, E 355, P 120 violations, none blocking);
  pin_map_lands, derate, safe_lines, power_sequence, power_path and ground_system PASS on all six; clock_check PASS on B,
  C, D, E and INCONCLUSIVE on A and P.
- TRN-001 (port_protect), r9t tree: A FAIL of 26 (4 symbol mismatches, A's O-13; D22 now OK), B FAIL of 17 (6 symbol
  mismatches, B's own, D520 SMBJ5.0A among them), C PASS (4), D PASS (21), E PASS (13), P PASS (3); 0 reversed and 0
  unjudged on every board. Base: PASS on all six (main's port_protect has no polarity pass).
- check_contracts: r9t PASS of 96, base PASS of 91.
- `inhibit_chain_<l>` (RF-002), r9t tree, final files: **A FAIL** (fail 3, pass 6), **B FAIL** (fail 15, pass 4, undecided
  1), **C FAIL** (fail 1, pass 5), **D INCONCLUSIVE** (pass 7, undecided 1: the SA868, R4T-D38's released divider, whose '1'
  level NiceRF does not state), E PASS (1), P PASS (1). What decides each: EMCON_HW fails (board B's three STM32 PC5 pins
  and board C's RP2040 GPIO21 on it); TX_INHIBIT_n passes; every transmitter on A and B fails through that line, and B's
  also through R4T-F17's (a) and (b); B's classification is UNDECIDED (J_QMX).
- **No board result moves against the third pass's tool.** On the committed netlists of main 458b2873, judge() with
  5aece264 and with the final file give the same 25 results (6 PASS, 17 FAIL, 2 UNDECIDED) and fail_safe() is identical;
  the details differ for nine board B transmitters only (the six module radios, the 5G module and both WiFi cards), which
  the walk now follows (R4T-D46, R4T-D47). The tool's table on the box's regenerated netlists (`out/r9t-final/tx_inhibit.log`)
  equals the runner's on the committed ones line for line.
- Probes on the box's regeneration (`out/r9t-final/`): leak_probe2, board_remedy_probe and tap_probe equal the runner's
  readings on the committed netlists and read the same with 5aece264 (their remedy kits are the faf8c981 shapes); the
  review's six (probe_level1b, probe_level1, probe_switched_rail, probe_second_feed, probe_second_feed2, probe_highline)
  read as R4T-F15 says, and the earlier three (probe_norail, probe_bound_vs_exact, probe_e2e) as in the third pass.
- assembly_set (DFA-001): INCONCLUSIVE in both trees, 47 footprints to compare in the base (main's tracked list) and 82
  in r9t; `drafts/ROTATION-CHECKLIST.r9t.md` is the r9t list, equal to the runner's render.
- Tests on the box, the five r4t test files: 152 passed, 1 skipped with the first files, 155 passed, 1 skipped with the
  final ones (the skip is the RF-002 applicability guard; the two KiCad round-trips run and pass there).
- Runner, the five files with the final files: 153 passed, 0 failed, 3 skipped (the two KiCad round-trips and the guard).
  Against the third pass's files (tx_inhibit 5aece264, kisch 88b20565, rebuilt byte for byte), 14 of the new or extended
  fixtures fail and pass now: the twelve new ones in test_tx_inhibit, t_the_part_number_reader and
  t_board_as_restart_guard_zener_is_judged_one_way_from_its_own_sheet. The logs of both runs are in
  drafts/box/r9t/fixture-runs/ (test_tx_inhibit on 5aece264: 71 passed, 12 failed, 1 skipped; test_kisch_tvs and
  test_port_protect on 88b20565: 49 passed, 2 failed, 2 skipped; the five files on the final files: 153 passed, 3
  skipped). Every defective fixture among them is one the old file read PASS (or UNDECIDED, for the VIL ceiling); the
  acceptable ones pass on the final file, and on the old file those that need what this pass added fail as well (the OR
  and the shunt read "EMCON does not reach it" and "no switch", D22 UNJUDGED, the control-word supply a FAIL of a board
  that works), while the rest (the +5V_SA pull-up, the 10 kOhm pull to +1V8, the bleed to ground, the discharge FET)
  pass on both.

## 4b. Results (round 6's third pass, box run and runner suite; kept for the record)

Box `/root/r6/t` (vast.ai 52646493, KiCad 9.0.9, Python 3.12.3, pdftoppm present), `drafts/box/r7t_box.sh` from
2026-09-26 13:31:04Z to 13:38:51Z, then `drafts/box/r7t_final.sh` (to 13:40:16Z) re-running the set checks, the five r4t
test files and the six probes with the last edit (tx_inhibit.py: a supply-like name that carries a control word stays a
signal; test_tx_inhibit.py: its assertion). Neither file is part of any generator's identity, so the regeneration and
its parity stand. Two trees: `base-faf8c981.tgz` (git archive of main faf8c981, sha256 6ab06c86..., the file round 6
used) and `r7t.tgz` (the worktree's same paths, sha256 8b966bdf...); `diff -rq` names exactly the ten r4t files. Every
temporary file went under `/root/r6/t/tmp` (TMPDIR), nothing outside `/root/r6/t` was removed, and `/root/r6/t` was
removed after the fetch (`/root/r6` holds only the board A author's `a/`). Results `r7t-results.tgz` sha256
c1d6ad7fecb60eedf8754469ef4163ed3f2fbc68fcacba9fba0d02263c92e488, unpacked in `drafts/box/r7t/out/` (SHA256SUMS verify,
and `r7t-final/` its own). Tool hashes on the box (`r7t-final/files.sha256`) equal the worktree's final files:
**tx_inhibit.py 5aece264d28252515ff3119ad7d2742d1fdf8250b8cc7e316b725335a4c06001** (the file the RF-002 row's gap NONE
is tied to), test_tx_inhibit.py d592a3d8..., check_contracts.py 529edb06..., kisch.py 88b20565..., port_protect.py
3f6d8b72..., assembly_set.py 721d3b56....

- Regeneration: gen_sch exit 0 and build_sch exit 0 on all six boards in both trees.
- **Netlists: no difference, so no finding ID applies to any netlist line.** Committed (main faf8c981) against each
  tree's regeneration, and base regeneration against r7t regeneration: PARITY_AFTER_NOISE on A, B, C, D, E and P
  (regen_compare.py pair netlist); the independent comparison (`drafts/box/netlist_par_r7t.py`, every component's record
  and every net's nodes with pinfunction and pintype) finds 0 differing components and 0 differing nets in all eighteen
  pairs: A 428/282, B 931/1852, C 204/146, D 221/174, E 179/124, P 82/54 (`drafts/box/netlist_par_r7t.txt`).
- **The other artefacts, base regeneration against r7t regeneration, every difference with its finding:**
  - intent, boards D and P: DIFFERENT in the key `clamps` alone (S-09, R4T-D18): with r4t's kisch.py the generators take
    their `kisch.tvs()` branch and the helper declares each call (D's D1; P's D1, D2 and D3); the netlists do not move.
  - provenance, all six boards: DIFFERENT in `generator_sha` and `generator_file_sha` alone (R4T-F2: kisch.py is part of
    every board's generator identity).
  - intent on A, B, C and E, BOM and ERC on all six: PARITY or PARITY_AFTER_NOISE.
  These are round 6's differences exactly: this pass changed no file a generator reads (kisch.py is 88b20565... as in
  round 6).
- Schematic-phase gates, identical in both trees except TRN-001, and identical to round 6's second pass: ERC gate PASS on
  all six (A 1089 violations, B 2044 with 6 allow-listed, C 300, D 386, E 355, P 120; no blocking error); SCH-005
  (pin_map_lands), CMP-001 (derate), safe_lines, power_sequence, power_path and ground_system PASS on all six;
  clock_check PASS on B, C, D, E and INCONCLUSIVE on A and P in both trees.
- TRN-001 (port_protect), r7t tree: A FAIL (of 25), B FAIL (of 16), C PASS (4), D PASS (21, the two PESD12VL1BA read
  from their own sheet, R4T-D34), E PASS (13), P PASS (3); base PASS on all six. Every log is byte-identical to the second
  pass's; A and B are A03's calls still owed by their authors.
- check_contracts: r7t PASS of 78 (A 32, B 42, C 7, D 11, E 12, P 9); base PASS of 73.
- `inhibit_chain_<l>` (RF-002), r7t tree: **A FAIL** (fail 3, pass 6), **B FAIL** (fail 15, pass 4, undecided 1),
  **C FAIL** (fail 2, pass 5), **D FAIL** (fail 1, pass 7), E PASS (1), P PASS (1), the same as the second pass; the
  tool's table (`r7t-final/tx_inhibit.log`) is byte-identical to the second pass's final one. What decides each is
  unchanged from section 4b: the EMCON_HW line fails (B's PC5 pins and C's GPIO21; the fail-safe states), TX_INHIBIT_n
  passes, every transmitter on A, B and D fails, B's classification is UNDECIDED (J_QMX). The boards' own remedies (B's
  pull-downs on LIME_EN, RB_EN and E22_EN, D's pull on SA_PTT_n) are their authors' and are not in main faf8c981.
- Probes on the box's regeneration (`r7t-final/`): leak_probe2, board_remedy_probe and tap_probe byte-identical to the
  second pass's and to the readings on the committed netlists (drafts/box/*.txt). The review's three: probe_norail FAIL
  for all three no-pull-down cases and UNDECIDED for VCC_X at 100 kOhm (1.58 V); probe_bound_vs_exact the bound FAIL and
  the exact state FAIL; probe_e2e FAIL and FAIL for both no-pull-down switches, PASS and PASS for the VBAT switch at
  10 kOhm.
- assembly_set (DFA-001): INCONCLUSIVE in both trees, 43 footprints to compare in the base and 78 in r7t (R4T-F11);
  `out/r7t/ROTATION-CHECKLIST.md` equals drafts/ROTATION-CHECKLIST.r6.md.
- Tests on the box, the five r4t test files with the final files: 142 passed, 0 failed, 1 skipped (the RF-002
  applicability guard); the KiCad round-trip fixtures run and pass there. The whole suite is not run on the box: it
  launches the Freerouting jar through route_one.sh (section 4b), and routing is not this round's to run.

## 4c. Results (round 6's second pass, box run and runner suite; kept for the record)

Box `/root/r6/t` (vast.ai 52646493, KiCad 9.0.9, Python 3.12.3, pdftoppm present), `r6t2_box.sh` from 2026-09-26
12:34:48Z, then `r6t2_final.sh` (12:48Z) re-running the set checks, the r4t tests and the three probes with the last
edit of tx_inhibit.py and test_tx_inhibit.py (the open-drain release, R4T-D38); neither file is part of any generator's
identity. Two trees: `base-faf8c981.tgz` (git archive of main faf8c981, sha256 6ab06c86...) and `r6t-v2.tgz` (the
worktree, sha256 1959ce82...); `diff -rq` names exactly the ten r4t files. Results `r6t2-results.tgz` sha256
4f390386...8c57, unpacked in `drafts/box/r6t2/out/` (SHA256SUMS verify; `r6t2-final/` has its own). Tool hashes on the
box (`r6t2-final/files.sha256`) equal the worktree's for test_tx_inhibit.py de8b7316..., kisch.py 88b20565...,
port_protect.py 3f6d8b72..., check_contracts.py d9712ec1... and assembly_set.py 721d3b56.... tx_inhibit.py ran on the box
and in the runner suite as 8fdd6898...; the worktree's final file is
e88aa46be6fe43058d2bdba43d5d14a43e17174ff82965ceac127038a1cbe830 (the file the RF-002 row's gap NONE was tied to until
the third pass, which withdrew it for R4T-F14), which
differs only in the comment above RAIL_TOL (its regulator citations narrowed to the sheets v2/vendor holds): reversing
that edit reproduces 8fdd6898... byte for byte, and the two files' code tokens are equal. The five r4t test files were
re-run on the runner with the final file (133 passed, 3 skipped, the KiCad round-trips skipping there). Round 6's
first-pass run is kept in `drafts/box/out/`.

- Regeneration: gen_sch exit 0 and build_sch exit 0 on all six boards in both trees.
- **Netlists: no difference, so no finding ID applies to any netlist line.** Committed (main faf8c981) against each
  tree's regeneration and base regeneration against r6t regeneration: PARITY_AFTER_NOISE on A, B, C, D, E and P
  (regen_compare.py pair netlist); an independent comparison on the runner (drafts/box/netlist_par.py, every
  component's record and every net's nodes with pinfunction and pintype) finds 0 differing components and 0 differing
  nets in all eighteen pairs: A 428/282, B 931/1852, C 204/146, D 221/174, E 179/124, P 82/54
  (drafts/box/netlist_par.txt).
- **The other artefacts, base regeneration against r6t regeneration, every difference with its finding:**
  - intent, boards D and P: DIFFERENT in the key `clamps` alone (S-09, R4T-D18): with r4t's kisch.py in the tree,
    gen_sch_d.py and gen_sch_p.py take their `kisch.tvs()` branch and the helper declares each call (D's D1; P's D1, D2
    and D3); symbols and pin maps equal the fallback's, so the netlists do not move.
  - provenance, all six boards: DIFFERENT in `generator_sha` and `generator_file_sha` alone (R4T-F2): kisch.py is part of
    every board's generator identity.
  - intent on A, B, C and E, BOM and ERC on all six: PARITY or PARITY_AFTER_NOISE.
  These are round 6's differences exactly; this pass changed no file that a generator reads.
- Schematic-phase gates, identical in both trees except TRN-001: ERC gate PASS on all six (A 1089 violations, B 2044 with
  6 allow-listed, C 300, D 386, E 355, P 120; no blocking error); SCH-005 (pin_map_lands), CMP-001 (derate), safe_lines,
  power_sequence, power_path and ground_system PASS on all six; clock_check PASS on B, C, D, E and INCONCLUSIVE on A and
  P in both trees.
- TRN-001 (port_protect), r6t tree: A FAIL (4 one-way clamps on the A1/A2 symbol), B FAIL (5), C PASS, D PASS (7
  clamps, the two PESD12VL1BA read from their own sheet, R4T-D34), E PASS (5), P PASS (3). Base: PASS on all six. A and
  B are A03's calls still owed by their authors.
- check_contracts: r6t PASS of 78 (A 32, B 42, C 7, D 11, E 12, P 9); base PASS of 73.
- `inhibit_chain_<l>` (RF-002), r6t tree, final pass: **A FAIL** (fail 3, pass 6), **B FAIL** (fail 15, pass 4,
  undecided 1), **C FAIL** (fail 2, pass 5), **D FAIL** (fail 1, pass 7), E PASS (1), P PASS (1); base (main's line
  contracts only): PASS on A, B, C and D. The tool's table (`r6t2-final/tx_inhibit.log`): the EMCON_HW line FAILS (the
  census: B's three PC5 pins and C's GPIO21; the fail-safe states: 3.46 V, the firmware pins at 3.3 V plus RAIL_TOL); the
  TX_INHIBIT_n line PASSES (worst 0.53 V at the bound: D's U12 at II and C's U9 at Ioff on 35 kOhm); every transmitter
  on A, B and D FAILS as in round 6 (the line, and R4T-F9's floating enables on B and D, R4T-F6 on D); B's
  classification is UNDECIDED (J_QMX).
- The probes on the box's regeneration (`r6t2-final/leak_probe2.txt`, `board_remedy_probe.txt`, `tap_probe.txt`) read
  the same as on the committed netlists (drafts/box/*.txt): R4T-F8's third statement, the B and D drafts' readings in
  R4T-F9, R4T-D40's tap readings.
- assembly_set (DFA-001): INCONCLUSIVE in both trees, 43 footprints to compare in the base and 78 in r6t (R4T-F11);
  `out/r6t/ROTATION-CHECKLIST.md` equals drafts/ROTATION-CHECKLIST.r6.md.
- Tests on the box, the five r4t test files with the final edits: 135 passed, 0 failed, 1 skipped (the RF-002
  applicability guard); the KiCad round-trip fixtures run and pass there.
- **The whole suite was started on the box and stopped (12:47Z)**: it reached test_plane_nets_guard, which runs
  route_one.sh on a fixture project and so launched the Freerouting jar the box holds (it failed to open a window and
  waited); routing is not this round's to run, so the whole suite ran on the runner instead (section 6), as in round 6.
  Its partial log is `drafts/box/r6t2/out/suite.log` (taken with the tools as they stood before the open-drain release
  edit; not a result).
- **Incident on the box, for the integrator and the other box users:** removing this run's own temporary test folders
  from `/tmp` at about 12:52:20Z, a `find /tmp -maxdepth 1 -name "tmp*"` also matched `/tmp` itself, and `rm -rf` removed
  the whole `/tmp` directory. It was recreated at once with mode 1777 (12:52:3xZ). Two other jobs had started minutes
  before and were running: `/root/r6/d` (the board D author's round-6 run, from 12:51:54Z) and `/root/rv/pkt`
  (review_packet.py for boards C, D and E, from about 12:52:05Z); any file they had put in `/tmp` by then is gone, and
  either may have failed on it, so both should be re-run or their logs read for temporary-file errors. Older contents
  of `/tmp` (other agents' leftover test folders of earlier runs, KiCad's own cache) are gone as well; nothing under
  `/root` was touched. `/root/r6/t` itself was removed as planned.

## 5. Open items (not faked)

As of main eadbe571 (the same under v2/ecad as 01469100: board P's TS network since d90f30e4; boards A, B and D corrected
at 458b2873, C, E and P earlier) and r4t's eighth pass:

- **Board B (the board B author):** (a) R4T-F17 (a): EMCON_ON (R513) and the three module kill ORs U111 to U311 run from
  +3V3_DEV, so with it down EMCON_ON floats and every KILL falls to 0 V: the W_DISABLE1# open drains, the card supply
  switches and the module kill FETs release under EMCON (FAIL; open item O-14's class). (b) R4T-F17 (b): PCIE_PWR_EN1 and
  PCIE_PWR_EN3, Compute Module pins, reach S1A_EN and S3A_EN through R164 and R364 (10 kOhm) against Q111 and Q311: a
  firmware pin on a gated enable (FAIL until moved behind a gate or declared a READER_TAPS entry with the arithmetic that
  the FET wins at its actual gate drive, which the JSCJ 2N7002 sheet does not state at 3.3 V). (c) The STM32 PC5 pins on
  EMCON_HW (one 74LVC1G34 for them, R4T-D40). (d) The SN74LVC08A quads U19 and U20 on EMCON_HW state no Ioff, so the
  enables they drive stay UNDECIDED even with R514 to R517 (now on main); one SN74LVC1G08 per input answers it. (e) The
  six clamp symbols (TRN-001, D520 SMBJ5.0A the new one). (f) J_QMX. Even with (a) to (e) answered, a path through a
  2N7002 EMCON holds off reads UNDECIDED until a sheet states its off-state current over the envelope (R4T-D46), and
  5G_W_DIS_n (R237 pull-up against Q206 at a 3.3 V gate drive) UNDECIDED for the same sheet's on resistance. (g) R4T-F19:
  +3V3_ZB is fed back through R28 to R31 from the unswitched CP2102N bridges' RTS and DTR, UNDECIDED once EMCON_HW holds,
  with the bridges' direct drive of the E72s' RST and BSL pins as the same back-powering question.
- **Board D (the board D author):** SA_PTT_n (the open-drain 74LVC1G06 U13 with R88 1.2k and R89 2k, on main) reads
  UNDECIDED: NiceRF states neither PTT's '1' level nor its input current, and no LVC sheet held states a powered open-drain
  output's off-state current. KEY's readback and TR_APRS (R4T-F6) no longer fail it on main (the SA868 reads UNDECIDED,
  not FAIL); what closes it is the NiceRF statement or a bench measurement (a TEST-PLAN item).
- **Board A (the board A author):** R102 10 kOhm 1% (R4T-F8); two SN74LVC1G08 in place of U26's EMCON_HW sections, which also
  make PA_EN and HF_EN decidable; the four A03 clamp calls (TRN-001's four symbol mismatches; D22 is read now, R4T-D48);
  R4T-F3. Once U26's remedy lands, the PA's and the HF unit's supplies still read UNDECIDED on Q14 and Q24, the boost-leg
  FETs on PA_OUT and HF_OUT (R4T-D49): what closes it is a maker statement of the LM5176's gate-drive level in shutdown
  (SNVSAI1D states "VCC off, No switching" only) together with the stage's own feed path, or the rail switched downstream
  of the stage.
- **Board C:** U3 GPIO21 behind a 74LVC1G34 on the panel's +3V3 (R4T-F5; the tap is withdrawn, R4T-D40).
- **Held evidence owed:** the four Raspberry Pi documents behind the Compute Module 5's VBAT charger, staged in
  drafts/datasheets/cm5/ for v2/vendor/cm5/ (drafts/vendor-rows-r4t.yaml, cm5_vbat_charger: their SOURCES.yaml rows and
  README lines; tx_inhibit.py cites the v2/vendor/cm5 paths, so they land in the same commit); a 2N7002 sheet that states IGSS, IDSS and RDS(on) at 3.3 V over the envelope (the fitted JSCJ
  states 25 C and VGS 5 V only; it now also decides board B's S-01, R4T-D46); the SA868's PTT threshold and current; a
  powered open-drain LVC output's off-state current; an ST statement of an unpowered STM32 pin's current (only if a tap is
  ever wanted); the vendor rows in drafts/vendor-rows-r4t.yaml, and the Diodes DS18004 sheet (drafts/datasheets, sha256
  0fbd7d13...) for v2/vendor/diodes, for the SOURCES.yaml writer.
- **Registry and coverage** (`drafts/r4-coverage-rows.yaml`): RF-002's applicability, acceptance criteria and
  false_positive_analysis in pcb_rules.yaml; the RF-002, TRN-001, SCH-003 and DFA-001 coverage rows. RF-002's row keeps
  gap NONE only with the EIGHTH pass's tx_inhibit.py (sha256 dd584cc9..., section 4), SOURCE_OR_APPLICABILITY_UNRESOLVED
  otherwise, the seventh pass's 7fa144a0 (R4T-F26 to R4T-F28), the sixth pass's 4836c42c (R4T-F24, R4T-F25), the fifth pass's bd3e93d5, the fourth pass's b3d645da, the third pass's 5aece264 and the second pass's
  e88aa46b included (R4T-F21, R4T-F18, R4T-F15, R4T-F14).
- **Every board author (R4T-D41, R4T-D42):** a supply that feeds a gate on an EMCON path, or that a pull on a path goes
  to, is named with a leading '+' and its voltage ("+3V3_DEV", "+5V_SA"). A name like "3V3_DEV", "VCC_X" or "SAU_3V3"
  is read as a supply but states no voltage: a reader on it is never passed at the LVC VIL, a pull to it leaves the state
  UNDECIDED, and a 0 Ohm link to it FAILS. No path on the six netlists meets one today.
- **When this lands:** kisch.py is in every board's generator identity, so the integrator regenerates all six
  (provenance sidecars change; D's and P's intents gain `clamps`; netlists do not move, proved again on main 458b2873),
  re-renders ROTATION-CHECKLIST.md with `assembly_set.py --checklist` (47 to 82 footprints), and re-runs check_contracts
  (RF-002's per-rule digest changes once its row lands).
- **Still open from before:** R4T-F1 in five tools r4t does not own (derate, clock_check, ground_system, power_sequence,
  netlist_board); the RA30H1317M1 VGG semantics (R4T-D10); the census's model of a '+' rail as always up, which cannot see a
  firmware-switched '+' rail linked to a net EMCON holds high (R4T-D42; no path meets one).
- **Limits of R4T-D49, named:** a firmware pin whose symbol names it after its net is UNDECIDED on the conductor, never
  judged a load or a feed (since R4T-D50 a Compute Module pin is decided by its pin number first); the second-feed check follows resistors, not FET channels or diodes, past the first part (a
  FET or diode on a far net is judged there and not walked through); and a transmitter's own signal pins driven by an
  unswitched part (R4T-F19's RST and BSL) are outside it.
- **Limits of R4T-D50, named:** a firmware part is judged by a held pin table only for the five families of
  FW_PIN_TABLES (RP2040, the STM32H742, H743 and H753, PCA9555, CP2102N, Compute Module 5); any other part's supply-named pin on a gated rail
  is UNDECIDED until its family's rows are added from its maker's table. The rows of the four families other than the
  Compute Module go by name, so a symbol that misnames a pin is believed there. A tied pin is judged by where its partner
  is drawn, not by whether the partner's net is live while the rail is off. And a firmware pin behind a resistor is
  UNDECIDED whatever its row, a supply input included (a false UNDECIDED, seen). SOFTWARE_IO's CM5 alternative (R4T-F22)
  is closed by R4T-D52.
- **Limits of R4T-D51 and R4T-D52, named:** (1) a charger's current is not judged: a VBAT whose partner is elsewhere FAILS
  at 2.2 mA as a regulator output does at 600 mA. (2) The reverse of a tied pair is read as a load except where R4T-D55
  reads it: a CP2102N's VREGIN on the rail with its VDD on another powered net PASSES (Rev 1.5 says nothing either way
  about reverse conduction through the regulator), and so do an STM32H7's VDD50USB beside a VDD33USB elsewhere, an
  STM32H7's VDDA on the rail with VREF+ on an external reference elsewhere, and a Compute Module 5's 5V on the rail with its
  VBAT on a live cell (the held Raspberry Pi pages draw no element between the two pins, call the cell "suitable for
  powering the RTC when the main power supply for the board is disconnected" and the charger "a constant-current (3 mA)
  constant-voltage charger", and say nothing of a path from VBAT back to 5V). Each is one `reverse` entry in
  FW_PIN_TABLES the day a held document or a review puts a path there. On the six netlists this decides nothing today and
  would decide something on board B if a power option were added: the three modules' pin 76 share one net, VBAT, while
  their 5V pins sit on +5V_S1, +5V_S2 and +5V_S3, and no TRANSMITTERS option gates a slot rail (the on-module radios are
  reached by WL_nDisable and BT_nDisable only). *Corrected in the eighth pass (R4T-F28, R4T-D55):*
  this limit also passed an STM32H7's VDD on the rail with its VBAT on a battery, saying DS12110 "states no path from VBAT
  to VDD"; its own Figure 15 draws the charging resistor between the two pins with no direction marked, so that case is
  UNDECIDED now. (3) An STM32H7's VREF+ with its VDDA across a 0 Ohm link is UNDECIDED for the link, because R4T-D49 (c) judges a
  link to a net a supply pin sits on by _load_only(), which does not ask the makers' tables (a false UNDECIDED, seen). (4)
  GPIO_VREF on a gated rail reads as an input, though 4.2's pin 78 requires it on CM5_3.3V or CM5_1.8V (the helper API
  says so). (5) A part is read as a firmware part, and by its family's rows, only by its library symbol or by its value's
  first words after a maker's name from a fixed list. *Rewritten in the eighth pass (R4T-F26, R4T-D53):* this limit said a
  part whose value begins with another word is "not read on a gated rail", while the tool printed PASS for it. Now a part
  that only mentions a family in its value or symbol ("I/O supervisor STM32H743VIT6", "Slot S1 compute: CM5108032", "Seeed
  XIAO ESP32S3") is UNDECIDED wherever a walk meets an active pin of it, naming the family, on a path and on a gated rail
  alike. It is never read by its family's rows, so its supply input is UNDECIDED too (a false UNDECIDED, seen) and its
  GPIO is UNDECIDED where a value led by the part number FAILS (a weaker answer, never a PASS). A firmware part whose
  value and symbol name no family SOFTWARE_IO knows (a custom symbol with the value "I/O supervisor A") is not found at
  all and is one of R4T-F23's unread parts on a gated rail: helper API point 1 tells board authors to begin every
  firmware part's value with its part number. (6) R4T-F23 itself: ten pins on the six
  netlists are taken as loads because no class reads them.
- **Limits of R4T-D53 to R4T-D55, named:** (1) fw_mention() is SOFTWARE_IO searched anywhere in the value and the symbol,
  so a part that mentions a family for another reason (a level shifter "for the RP2040") is UNDECIDED on a rail where it
  may be a plain load: a false UNDECIDED, seen. Board B's J_PANEL is the one such part on the six netlists, and every walk
  reads it as a connector first. (2) The rows of the four families other than the Compute Module go by name (a limit of
  R4T-D50), so R4T-D54's pins by number apply to the Compute Module only: an STM32H7 VDD pin the symbol calls "VCC" on
  another net is still outside its row. (3) A receptacle's declared range is not checked: a receptacle-B symbol ("CM5 pins
  101-200") numbered 1 to 100 whose pin 77 is named only after its net reads as the module's 5V (the review's probe3, PASS
  on all three files). Board B's receptacles are numbered 1 to 100 and 101 to 200, as their values say. (4) R4T-D55's
  reverse reading is set for the STM32H7 row only (limit (2) above).

## 6. Full suite in the worktree

Round 6 eighth pass, on the runner in the worktree at 01469100 plus r4t (main eadbe571 differs only in two
v2/docs/feasibility pages), run once with the final files of section 4 (tx_inhibit.py dd584cc9..., test_tx_inhibit.py
cef8e3bf...), 18:40:45Z to 18:43:36Z: **1600 passed, 0 failed, 74 skipped** (drafts/r13t/suite-r13t.log, TMPDIR in the
session scratchpad). The three new fixtures are the rise from the seventh pass's 1597, and the 74 skips are the seventh
pass's, by name (drafts/r13t/skips_r12t.txt and skips_r13t.txt are equal), with the reasons given below. The worktree's
git status, and the hashes of every tool, every test and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md, are the
same before and after the run (drafts/r13t/st_*_suite.txt, hashes_*_suite.txt); no run wrote this tree's own evidence,
and the check_contracts run of section 4 wrote only into the scratchpad.

Round 6 seventh pass, on the runner in the worktree at 01469100 plus r4t (main eadbe571 differs only in two
v2/docs/feasibility pages), run once with the final files of section 4 (tx_inhibit.py 7fa144a0..., test_tx_inhibit.py
d958a829...), 18:01:52Z to 18:04:35Z: **1597 passed, 0 failed, 74 skipped** (drafts/r12t/suite-r12t.log, TMPDIR in the
session scratchpad). The four new fixtures are the rise from the sixth pass's 1593, and the 74 skips are the sixth pass's,
by name (drafts/r12t/skips_r11t.txt and skips_r12t.txt are equal), with the reasons given below. The worktree's git
status, and the hashes of every tool, every test and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md, are the same
before and after the run (drafts/r12t/st_*_suite.txt, hashes_*_suite.txt); no run wrote this tree's own evidence, and the
check_contracts run of section 4 wrote only into the scratchpad.

Round 6 sixth pass, on the runner in the worktree at 01469100 plus r4t (main eadbe571 differs only in two
v2/docs/feasibility pages), run once with the final files of section 4 (tx_inhibit.py 4836c42c..., test_tx_inhibit.py
85d2085c...), 17:10:15Z to 17:13:00Z: **1593 passed, 0 failed, 74 skipped** (drafts/r11t/suite-r11t.log, TMPDIR in the
session scratchpad). R4T-D50's two new fixtures are the rise from the fifth pass's 1591, and the 74 skips are the fifth
pass's at 01469100, by name, with the same reasons (below). The worktree's git status, and the hashes of every tool, every
test and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md (905b40c6..., main's), are the same before and after the
run (drafts/r11t/st_before_suite.txt, st_after_suite.txt); no run wrote this tree's own evidence, and the check_contracts
runs of section 4 wrote only into the scratchpad.

Round 6 fifth pass, on the runner, with the final files of section 4f (tx_inhibit.py bd3e93d5..., test_tx_inhibit.py
25bedf87...), run twice because main moved under the pass: the evidence has to bind to the revision the files land on.
- **At main 01469100 plus r4t** (the worktree's state as handed over), 16:33:15Z to 16:36:05Z: **1591 passed, 0 failed,
  74 skipped** (log `drafts/suite-r4t.log`). Main's own new tests are the rise from 1540. The one skip more than at
  458b2873 is main's new test_pack_secondary_ts.t_the_current_netlist_holds_the_property: in the r4t tree the committed P
  netlist names main's kisch.py in its provenance, so the test finds no P netlist this tree's generator wrote and skips.
  It is not a pass by skipping: run on the r4t regeneration of P from the box (section 4f), the whole file reads 10 passed,
  0 skipped (`drafts/r10t/at-01469100/test_pack_secondary_ts_on_r4t_regen.log`). When this lands and the integrator
  regenerates the six boards, the committed P netlist is current again and the skip goes.
- **At main 458b2873 plus r4t**, 16:23:42Z to 16:26:14Z: **1540 passed, 0 failed, 73 skipped**
  (`drafts/r10t/suite-458b2873.log`). The fourth pass read 1536; the four new fixtures are the difference, and the 73 skips
  are the same tests, by name, as the fourth pass's, with the same reasons (below).
The worktree's git status is the same before and after each run, and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md
is unchanged by either (sha256 c71ac73d... at 458b2873, 905b40c6... at 01469100, main's own at each); no run wrote this
tree's own evidence, and the check_contracts and test runs of section 4f wrote only into the scratchpad.

Round 6 fourth pass, on the runner in the worktree at main 458b2873 plus r4t, run once with the files of section 4a
(tx_inhibit.py 82b0c499..., whose code equals the final b3d645da...; every tool and test file hashed before and after,
unchanged): **1536 passed, 0 failed, 73 skipped**, from
15:32:19Z to about 15:35Z (log `drafts/suite-r4t.log`, TMPDIR in the session scratchpad; the third pass read 1521 and 73
at faf8c981, and the difference is r4t's thirteen new fixtures and main's two new schematic-page tests). The worktree's
git status is the same before and after, and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md is unchanged
(sha256 c71ac73d..., main 458b2873's); no run wrote this tree's own evidence. **The 73 skips are not passes**, by reason:
61 need KiCad (53 "no pcbnew here", 3 pre-lay pair enumerations, 2 "pcbnew is not importable", 1 pre-router occupancy
module, 2 KiCad round-trips of test_kisch_tvs, which ran and passed on the box); 10 need evidence this tree does not hold
(4 rule audits, 1 set-level readiness evidence, 2 routeflow journals for the ETA page, 1 assembly_set or final_gate page,
1 certification run, 1 git worktree check); 1 needs numba; and 1 is test_tx_inhibit's RF-002 applicability guard, which
skips by design until the registry writer applies r4t's RF-002 row (it leaves RF-002's results on A, C, E and P deciding
no rule until then).

Round 6 third pass, on the runner in the worktree at main faf8c981 plus r4t: **1521 passed, 0 failed, 73 skipped** (log
`drafts/suite-r4t.log`, TMPDIR in the session scratchpad; the second pass read 1514 and 73, and the seven new fixtures
are the difference). It ran with tx_inhibit.py 6ebff9ee..., which differs from the final 5aece264... in one comment line
only (reversing that edit reproduces 6ebff9ee... byte for byte); test_tx_inhibit.py was final. The worktree's git status
is the same before and after, and the tracked v2/release/revA/order/ROTATION-CHECKLIST.md is unchanged (sha256
161a3578..., main's). The five r4t test files with the final files: 140 passed, 3 skipped on the runner (the KiCad
round-trips skip there), 142 passed, 1 skipped on the box. Against the second pass's tx_inhibit.py (e88aa46b), eight of
test_tx_inhibit's fixtures fail on behaviour (section 2, R4T-F14) and one more on the new _supply_nets API; the level-1
tolerance case passes on both.

Round 6 second pass, for the record: 1514 passed, 0 failed, 73 skipped.
