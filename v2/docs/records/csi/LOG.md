# Stream csi, log (29 September 2026, CEST; `date` read before each label)

- 14:38 Brief read. Worktree `/home/claude-runner/worktrees/meshsat-fieldkit/csi`, branch `fnd/csi` from `fnd/int13`
  (`e553e43a`). The thirteen IBIS models copied from `w5si2` as ignored files; `ibis_fetch.py --check`: 13 present.
- 14:40 SI-001 on board C re-taken in scratch with the base tool: the committed reading reproduced exactly (23
  layout-bound, all BOUND_DECIDES, 1 undecided: EMCON_HW_DRV, no class entry). Per net, its governing drivers listed from
  the table.
- 14:42 Read `edge_length.py` (what answers a net: an impedance target, a 10 to 150 ohm series resistor between two
  signal nets, an `edge_allow` entry), `pcb_edge_rates.yaml` (RPI-RP2040, LVC1G34-BUFFER, TI-PCA9555 with INT flagged,
  POWER-STAGE-NODES, OSCILLATOR-NODES, FAR-BENCH-PROBE, the kit far ends), w5si2's README section 6 and finding F-Q1
  (W5SI-D3: no declaration for a power-stage node while no rule holds its copper).
- 14:45 The makers searched (`readings/maker-search-2026-09-29.txt`): no RP2040 IBIS model anywhere Raspberry Pi
  publishes; no Diodes 74LVC1G34 model (its page through the Internet Archive; diodes.com refuses the runner);
  raspberrypi.com's documentation site refuses the runner, its source repository and portal answer. Raspberry Pi's
  minimal KiCad design fetched to scratch (MIT, sha256 recorded, not committed).
- 14:48 The hardware design guide read (p. 10 QSPI "wired directly ... short connections", p. 11 crystal "as short as
  possible" with the 3 pF stray, p. 12 USB 27 ohm series termination) and the datasheet's SWD section (p. 62).
- 14:50 Decided: a series resistor is against the maker's QSPI guidance, so QSPI takes an allowance; a bare allowance
  is a sentence (W5SI-D3's objection), so the tool is changed first to hold an allowance's basis (CSI-D1) and the length
  it declares (CSI-D2). EPD_SW stays open under W5SI-D3; HB1 to HB3, SCL, SDA and EXP_INT are not closable on board C.
- 14:52 `edge_length.py` changed; `run.py edge_length`: 41 passed, 1 failed, the old test passing a board on a bare
  sentence (the failing case, `readings/tests-2026-09-29.txt`). Test brought to CSI-D1, three tests added; the one on
  the committed tables failed on the base table ("no board table carries an edge_allow entry").
- 14:54 `tools/measure_minimal.py` written: the maker's board file parsed, lengths per net summed (QSPI 8.20 to 22.73 mm,
  XIN 11.23, XOUT 2.76, its crystal node 5.26, SWCLK 25.92, SWD 24.34). A first run refused its own file: the sha was
  taken over the text read with newline translation; fixed to hash the bytes.
- 14:56 Board C's table: Q3_G and EMCON_HW_DRV declared LOW_SPEED_OR_DC on content, eight `edge_allow` entries with
  their citations and lengths. `load_allow("c")`: 8 held, 0 refused. SI-001 with the declarations: 11 layout-bound.
- 14:57 27R chosen over 33R for the e-paper lines: the maker's own series value on this chip, and a part the tree
  already codes (lcsc_fill.py C25190); 33R had no code in the tree and none was read from a maker here.
- 14:58 `apply/apply_board_c_epd_series.py`, `apply/readback_board_c_epd_series.py`, `tools/sim_netlist_c.py`
  written. Read-back FAILS 16 of 16 on the committed netlist, HOLDS 16 of 16 on the stand-in.
- 14:59 Test runs: 80 passed, 0 failed on six test files. `test_requirements` 5 failures and `test_verdict_channel`
  failures seen; the latter only under `VERDICT_DIR` (45 of 45 without it), the former the same on the base.
- 15:00 Commit `a18e90e9` behind the pre-commit check's PASSED line.
- 15:00 Scratch views built with `w5si2/tools/scratch_tree.py`; the draft applied in one (written, then refused on
  the second run); SI-001 taken: C before 23, declarations 11, after 7 layout-bound; B identical before and after.
- 15:04 README, LOG and the readings written.
