# Round 4: what board B (r4b) needs from board A (r4a), and what B now declares

MESHSAT-1357, 26 September 2026. From the board B author to the board A author. Read against r4a's working copy of
`gen_sch_a.py` as it stood at 01:45 CEST. Prototype design: nothing is built.

## I-01 D-12, the wall data path to the Glenair 233-370: nothing changes on B

- **B sends:** USB_WALL_P and USB_WALL_N from bank 3 hub (U302) port 3. They leave on J_AB2 pins 1 and 2 (the 2x5 end
  row), and pins 3 to 10 are GND. U29 (USBLC6-2SC6) sits at B's end, referenced to +3V3_DEV. The pins and nets are
  unchanged; only J_AB2's value text now names the Glenair.
- **B does not send:** VBUS. The port's 5 V is board A's. r4a's draft has `VBUS_WALL` behind eFuse U32 (0.89 A),
  out on J_USBW with U29 re-referenced to VBUS_WALL. That matches what B expects.
- **The hub side:** TUSB8041 U302's PWRCTL3 (pin 33) and OVERCUR3z (pin 44) are not connected on B, so the hub neither
  switches nor senses the wall port's power. A's eFuse is the only protection.
- **Open, for the contract owner:** if U32's fault should reach the hub's over-current input, a line is needed. J_AB2
  has eight grounds, and one of them could carry it, but only with both ends agreed. B has not changed J_AB2.
- **Console and key fill (S-21):** these go on this port. On B it is an ordinary downstream port of bank 3.

## I-02 D-07, the 5G antennas: B carries no RF, and A owns every blind-mate net

- The RM520N-GL's antenna ports are IPEX 20579-001E receptacles on the module itself (HD v1.1 5.2.1). The M.2 socket
  J_M2C2 has no RF pins.
- The pigtails run from the module to A's sites:
  - ANT0 to A's `RF_5G1` (today named "5G-MAIN");
  - ANT2 to `RF_5G2` (today "5G-DIV");
  - ANT3 to a new `RF_5G3` at A's free site X +46 (W4), **only if** the owner's case measurement (D-08) confirms that
    site and board E's clamp fit. Otherwise two jacks.
- MAIN and DIV are the EG25-G mini PCIe names (A08). A's RF table and ASSEMBLY.md:99 should name ANT0, ANT2 and ANT3.
- Nothing on B changes with the third jack.

## I-03 F-PR-05, slot 2's 5 V rail: B's current is larger than A declares

B now declares `+5V_S2` at **4.2 A typical** (4.1 A in the first fix-up; fix-up pass 2 raised slot 2's card buck to
3.456 V, SD-B-18, so its 3.0 A draws 2.31 A at 5.1 V instead of 2.21 A). A still declares 2.5 A typical and 5.0 A peak for all three slots
(`gen_sch_a.py` line 87 in r4a's copy). The 4.2 A adds up as follows:
- `power_path` on B sums slot 2's three converters at 3.16 A. The RM520N-GL's 3.0 A continuous at 3.456 V is 2.31 A
  of that (3.0 x 3.456 / 0.88 / 5.1), through a 0.88-efficient buck.
- The CM5 module draws 0.9 A (datasheet Table 9), and the fan 0.1 A.
- Total: 4.16 A.

**Peak, all at once:**

| Load | Current at 5.1 V |
|---|---|
| RM520N at 4 A (3.456 x 4 / 0.88 / 5.1) | 3.08 A |
| Module under stress | 1.6 A |
| NVMe and switch | 0.7 A |
| Switch core | 0.15 A |
| Fan | 0.1 A |
| **Total** | **5.63 A** |

B keeps the peak declaration at A's 5.0 A and carries the 5G burst in 2 x 220 uF polymer at the socket. r4a's draft
moves slot 2 to an LM5176 stage like +5V_DEV, which can deliver more.

**Asked of A:**
- (a) Declare +5V_S2 at 4.2 A typical, so `dc_drop` on A judges its copper at that current.
- (b) Decide whether the slot 2 peak becomes about 5.7 A. If it does, B will raise its peak and move U203's apportioned
  load to 3.08 A in the same change.
- The shares are untouched: B 1.5 percent, A 0.5 percent.

## I-04 S-01 and D-05: EMCON on B, for A's reading of the line

**Corrected in fix-up pass 3 (26 September 2026).** Until then this section said "With the panel absent, B's radios
are dark", and that was false. The round-5 re-review found it, and B's circuit is now fixed. Taken by the session under
the owner's standing rule of 26 September 2026 (drafts/r4-decisions.md, section 1d, SD-B-20 and SD-B-21).

- **What was wrong, on B and therefore on A.** From B14 on, each card's W_DISABLE1# stage (Q106, Q206, Q306) had its
  gate on the card rail, its source on W_DISABLE1# with 10 k up to that rail, and its drain on EMCON_HW. The body diode
  (anode at the source) sourced current per live card rail into EMCON_HW whenever nothing drove it (about 50 uA against
  the 50 k, up to 0.35 mA into a line at 0 V): ribbon out, or
  board C's U9 unpowered. Against B's R58 and A's R102 (100 k each) that lifted the line to about 2.3 to 2.5 V, a HIGH
  at every EMCON gate, **including A's U26**. Slot 2's card rail is not EMCON-gated, so a booted slot 2 alone was enough
  to release the PA and the HF rails on A with no panel present. The committed B21 netlist has the same wiring.
- **What B has now.** Nothing on B can source EMCON_HW. It carries only U19 (three inputs), U20 (one), the three
  supervisors' PC5 inputs, Q11's gate, R58 to GND, a test pad and the two ribbons. The W_DISABLE1# stages are open
  drains Q{s}06 from EMCON_ON (gate EMCON_ON, source GND, drain on the socket pin). check_pcb_b.py asserts both.
- **R58 is 10 k now, not 100 k.** C7 drives EMCON_HW with its buffer U9 (push-pull), so no pull-up needs the pull-down
  to be weak. At the datasheet maxima (-40 to +85 C) the line's readers can leak 30.8 uA: six SN74LVC08A inputs at
  +-5 uA (B's four and A's two), three STM32H743 TT_a inputs at +-250 nA, and Q11's gate at 80 nA. At 50 k (100 k on
  each board) that is 1.54 V, above the LVC08's VIL of 0.8 V. At 9.09 k (B's 10 k with A's 100 k) it is 0.28 V.
- **With the panel absent, B's radios are dark (proven on B's netlist).**
  - EMCON_HW sits at no more than 0.28 V at the datasheet maxima. U19 and U20 read LOW, so the LimeSDR, RockBLOCK,
    LoRa and E72 enables are off.
  - Q11 is off (its threshold is at least 1.0 V), so R513 holds EMCON_ON high. The module WiFi and Bluetooth are
    killed (U{s}11, Q{s}09, Q{s}10), the slot 1 and 3 card supplies are off (Q{s}11), and all three W_DISABLE1# pins
    are pulled low (Q{s}06).
  - The condition: +3V3_DEV must be up. With +3V3_DEV lost and a slot rail up, EMCON_ON falls and the module radios,
    the slot 1 and 3 card supplies and now W_DISABLE1# are released. That is open item O-14, whose scope grows to cover
    W_DISABLE1#; for W_DISABLE1# it is a narrow regression of SD-B-20 (B21's stage held the 5G pin low in that state),
    recorded in O-14 with the pass-3 re-review's candidate remedy. The LimeSDR, RockBLOCK and LoRa switches are no
    longer in it: since round 6 their enables carry 10 k to GND (SD-B-22).
- **Asked of A (r4a):**
  - (a) Read the corrected statement above. A's U26 was released by B's back-feed, and that is fixed on B's side.
  - (b) R102 to 10 k, for the same arithmetic when J_AB1 is unplugged. A alone then holds only 100 k against U26's
    two inputs, and 10 uA at the maximum gives 1.0 V there, above VIL. That is A's to decide.
  - (c) Nothing on A may source EMCON_HW. On A23 today that holds: U26's two inputs, R102, TP15 and J_AB1.

## I-05 S-08: B's side of the power-up states

- R48 and R50 to R53 are 4.7 k pull-downs (A01).
- R60 to R62 are 4.7 k as well, so the Ethernet switch is out of reset and the 5G module is not held off at power-up.
- The module radios are OFF at power-up by 10 k pull-ups on their requests.
- Round 6 (R4T-F9, SD-B-22): LIME_EN, RB_EN, E22_EN and E72_EN, the EMCON gates' outputs into the LimeSDR and
  RockBLOCK eFuses and the LoRa and E72 load switches, carry 10 k to GND (R514 to R517). With +3V3_DEV lost and +5V_DEV
  up those three +5V_DEV switches now read OFF instead of floating. Nothing on J_AB1 or J_AB2 changes, so A sees none of it.
- Nothing here depends on A's DEV_EN fix, but the kit only reaches B's defined states once +5V_DEV is up. So r4a's R42
  pull-up to +3V3 is what makes the whole sequence deterministic.

## I-06 For the integrator, not board A: what has to land in one commit with gen_sch_b.py (fix-up pass, 26 September 2026)

**Round 6 supersedes every earlier list (the pass-3 re-review's blocking item, rebuilt on main faf8c981).** One commit,
every file from `drafts/box/r6-run6/tint/set/` (sha256 in `set.sha256`, PCB-BRING-UP.md's in the run README):
- `v2/ecad/tools/gen_sch_b.py` (6e3d8809...) and `v2/ecad/tools/check_pcb_b.py` (28904a37...);
- `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_sch` and `out/pcb-b-compute.net`, `out/pcb-b-compute-intent.json`,
  `out/pcb-b-compute.net.prov.json`, regenerated on faf8c981 (its sch_prov identity includes the lands C, D, E and P added);
- the O-19 patch as applied: `v2/ecad/tools/build_sch.sh`, `sch_pages.py`, `tests/test_schematic_pages.py`;
- `v2/release/revA/order/ROTATION-CHECKLIST.md` (assembly_set.py --checklist: two rows, C520's `CP_EIA-3528-21_Kemet-B`
  and J_IOCOFF_A's `PinHeader_1x02_P2.54mm_Vertical_SMD_Pin1Left`, and 43 to 45);
- `v2/docs/PCB-BRING-UP.md` (rules_render.py --no-refresh; PCB-ETA.md stays at HEAD).
The full suite on exactly that tree: 1472 passed, 0 failed, 12 skipped, and it left the tree's status unchanged. Board A
sees nothing new from round 6: R514 to R517 sit on B's own enables (I-05), and J_AB1/J_AB2 are unchanged. The b.json
EMCON_HW text is still stale (O-22), and the suite owner is asked to give test_assembly_set a temporary path (O-18).

**Fix-up pass 3 superseded pass 2's integration set (kept for the record):** `v2/ecad/tools/gen_sch_b.py` (sha256 9b85ada8...) and
`v2/ecad/tools/check_pcb_b.py` (sha256 720892ae...) from this worktree, the regenerated outputs from
`drafts/box/r6-run4/t29/regen/` (main 29f00554 plus the two files), and `drafts/sch_pages-popups-r5.patch` unchanged.
The one thing board A sees from pass 3 is I-04: B no longer lifts EMCON_HW, R58 is 10 k, and A is asked for the same
on R102. `tools/boards/b.json`'s EMCON_HW text is stale (O-22).

**Fix-up pass 2 supersedes the first two bullets below:** `check_pcb_b.py` is now edited in the worktree itself (this
pass made the board B author its writer; the content is the patch's, sha256 5d52b0e2...), the regenerated outputs
come from `drafts/box/r5-run3/t26/regen/` (generator sha256 8a980c57...), and `drafts/sch_pages-popups-r5.patch`
(O-19) should land with them. The first fix-up's text follows for the record.

- **check_pcb_b.py.** Apply `drafts/check_pcb_b-r4.patch`. It is written against 82dd1e4d, and `git apply --check` is
  clean.
  - Without it, board B's gate fails 13 net checks on the round-4 netlist. The reason is that the gate has not caught
    up, not a fault on the board.
  - With it, the gate judges each PCIe lane and the LimeSDR SuperSpeed legs by direction at pad level, plus the new
    REFCLKO termination: 0 FAIL of 159 on the round-4 netlist.
  - On the committed B21 board it FAILs the 46 crossed or unterminated items. That is the truth about B21, and it holds
    until a placement seats the new parts.
  - Evidence: `drafts/r4-decisions.md` section 1b and `drafts/box/check_pcb_b/`.
  - The file is W6/W7's, so the patch is only a proposal until they accept it.
- **The regenerated outputs.** From `drafts/box/out/regen/`, all from generator sha256 b24e88ce... (sch_prov
  `22077343dbc6bcbb`): `pcb-b-compute.kicad_sch`, `out/pcb-b-compute.net`, `out/pcb-b-compute-intent.json` and
  `out/pcb-b-compute.net.prov.json`. Without them, check_contracts reads board B's netlist as UNKNOWN GENERATOR.
- **Nothing changes for board A.** The HCSL termination, SIM 2's 0 Ohm links and the SMD jumper land are all inside
  board B. No J_AB1, J_AB2 or rail declaration changed in the fix-up.
- **Fix-up pass 2:** the only change A sees is I-03's numbers (4.2 A typical, a 5.63 A coincident peak). R240's
  removal, the card buck's set point and compensation, and the O-16 reading are inside board B.
