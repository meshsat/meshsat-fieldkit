mergeable: no
<!-- Filed by the integrating session as the checker returned it (MESHSAT-1357, 29 September 2026). B1 (the walk rule's hole, CX9) and the circuit minors go to stream rf2walk's second round (fnd/rf2walk2); set 12 is not promoted until they are answered and checked. -->

# AI review: independent check of set 12's FEA-002 remedies and the RF-002 walk fix, fnd/rf2walk at a444cb37 (MESHSAT-1357)

This is an AI review, not a qualified engineering review. Read from a shared scratch clone detached at `a444cb3706477ffc5b516ab11e0db34e6db8d80a`, 29 Sep 2026 13:34 to 13:52 CEST (times from `date`). Nothing in any worktree or the main checkout was written; every rule tool ran from a scratch cwd with `VERDICT_DIR` in the scratchpad; `git status` of the clone shows only `_chk/` (my scripts: `netparse.py`, `netcmp.py`, `netshow.py`, `cx_walk.py`, `cx_main.py`, `cx5_debug.py`, `cx5b.py`, `fs_spy.py`). Makers' documents read with `pdftotext -layout` from `v2/vendor/`.

Counts: 1 blocking, 7 minor. Remedies: 5 of 5 on board B and 1 of 1 on board C do what their records claim at the stated worst case; netlist changes are exactly the drafted ones; every reading reproduces byte for byte.

## Blocking items

1. **`v2/ecad/tools/tx_inhibit.py` `drive_net` (line 1688), used by `_line_sources` (1713) and the census clause (1392), together with `fail_safe` line 2224 (`down = {k for k, _r in src if k in frag}`): the new rule hides a real back-drive path that the walk caught before the fix.** Counterexample CX9 (`_chk/cx_walk.py`, `_chk/cx_main.py`): on board B, a 74LVC1G34 on +3V3_DEV with its input on TX_INHIBIT_n drives EMCON_HW through its own 330R, and a second one with its input on EMCON_HW drives TX_INHIBIT_n through its own 330R. With board C down this pair is a latch that can hold both lines HIGH against R58 and R59 (every transmitter released). drive_net accepts both private nets, `_line_sources` makes each gate "the line's own source", and fail_safe then takes board B (the readers' board) down in every fragment, so the powered latch is never solved. Readings: fixed walk, both lines PASS and every RF-002 row PASS; main's walk (2c7730a4) and the unfixed walk (e41df395), both lines FAIL ("a second BUF output on the net"). The same pair wired directly on the lines passes on all three walks, so the hole is pre-existing in the on-net source rule; this fix extends it to the series-resistor form that used to fail. No set 12 board carries such a pair, so no set 12 reading changes. Fix: accept a gate as a line's own source (the census clause, `_line_sources`, `drive_net`) only on a board that carries the asserted pair's switch (board C's SW_EMCON here), or have fail_safe keep any other source-classified gate powered as a follower of its input's fail-safe level; add CX9 in both forms (on the lines and behind resistors) as defective fixtures.

## 1. The FEA-002 remedies

Generators: `apply_b_d4e.py` and `apply_c_d4e_f1.py` re-run on main's `gen_sch_b.py` / `gen_sch_c.py` give files byte-identical to 3115fc58, unchanged to HEAD; netlists unchanged since e41df395; `readback_d4e.py` re-run: B 60 PASS, C 4 PASS, rows identical to `records/int13/readback-*.txt`.

**Netlist comparison against main 2c7730a4 (own s-expression parser, parts and pin-to-net maps):** board B 1280 to 1335 parts (+18 C668 to C685, +19 R532 to R550, +18 U537 to U554), value changes only R41, R42 (10k to 2.2k 1%), R527 (15k 1%), R238 (100k 1%) and U536's text; pin moves only R41.2 and R42.2 to GND, U12 pins 6, 7, 13 to 19 to the LORA_* module nets, U16/U17 pins 24, 26, 28 and U18 pin 26 to the *_H nets, U221.1 to 5G_TPR_n, U536.4 to RB_IEN_DRV, U6.20 to RB_CTRL_H; 21 named nets and 7 NC stubs added, none removed. Board C: +R52, +D23, U9.4 to EMCON_HW_DRV, one net added. Exactly the drafted parts and nets. Pinouts checked: TPS3808 DBV (1 RESET, 2 GND, 3 MR, 4 CT, 5 SENSE, 6 VDD, SBVS050N Fig. 5-1), SN74LVC2G07 DBV (SCES308L sec. 5), CP2102N QFN28 (24 RTS, 25 RXD, 26 TXD, 28 DTR), E22 pins 6, 7, 13 to 19 (manual v1.20 table), RockBLOCK pins 3, 6, 7, 8, 13, 14 (hardware page), D23 pin 1 K on TX_INHIBIT_n (SOD-123 pad 1 cathode).

| Remedy | Claim | Source | Finding | Holds |
|---|---|---|---|---|
| B-1 RockBLOCK gating | RXD and P_EN pass only while RB_GO = RB_IEN AND I_BTD; 0.10 V unpowered; I_BTD/XMT_G 0.22 V off; TXD 0.30 V | GC hardware page (I_BTD "no voltage ... other than I_EN"; startup/shutdown lists; Logic In LOW 0.4 V, Out HIGH 2.9 to 3.4 V at 2 mA); SCES217AA Ioff 10 uA; SCPS131J IIL -100 uA; CP2102N IPU -10 to -30 uA | Quotes accurate. 10 uA x 10.1k = 0.10 V, 100 uA x 2.2k = 0.22 V, 30 uA x 10.1k = 0.30 V; module drives 3.4 V into 2.178k = 1.56 mA, inside 2 mA. Gate implements the maker's startup order. Departure stated correctly: the maker's shutdown order sets inputs low after I_BTD falls, the gate drops them with I_EN; P_EN low is the module's own default. Directions unchanged (TXD stays module to U18 RXD). | yes |
| B-2 E72 open drains | six lines through SN74LVC2G07 on +3V3_DEV, pulled up only to +3V3_ZB; dead rail 0.56 V under 1.9 V; 0.71 mA | SCES308L (VOL 0.1 V at 100 uA, Ioff 10 uA, VI/VO to 5.5 V); E72 manual (1.9 to 3.8 V); CP2102N IPU | 120 uA x 4.653k = 0.558 V; 3.3/4.653k = 0.709 mA. Polarity kept (non-inverting). 4.7k pull-up rise about 0.16 us into 15 pF, fine at 460800 baud. Only the CP2102N RXD pull-ups and Ioff feed the rail (LED and cJTAG nets checked). | yes |
| B-3 E22 gates | six host lines gated by LORA_GO on +3V3_CM3, three outputs buffered; VOL 0.1 V; MISO cost | E22 manual v1.20 (SPI 0 to 10 Mbps, 2.5 to 5.5 V, 3.3 V level); SCES217AA tpd 3.6 ns; DS36108 II 1 uA | Directions match the manual (DIO1, BUSY, MISO out; rest in). 25 mV on E22_EN checks (1 uA x 25.25k). One AND on SCK plus one buffer on MISO, under 8 ns at 10 MHz. SPI3_MISO now always driven; see minor 3. | yes |
| B-4 U543 on RB_IEN | holds RB_IEN at most 0.4 V in U536's 0 to 1.65 V band; released at least 2.08 V; EMCON 0.15 V; all rails lost 0.28 V | SBVS050N (VIT 2.79 V +-1.25 % at -40 to 85 C, VOL 0.4 V at 1 mA for VDD 1.8 to 6.5 V, IOH 300 nA, td 12 to 28 ms CT open, SENSE to RESET 20 us typ, MR 90k); GC I_EN divider 270k/430k (2.457 V, 166k at 4.0 V) | 1.65/2.178k = 0.76 mA; released (2.4/2.222k + 2.457/166k)/(sum of conductances) minus 5 uA = 2.08 V; U543 on +5V_DEV, U25's input (checked). Holds in the stated band; see minor 2 for 1.65 to 2.9 V and the td pulse. | yes |
| B-5 U554 on FULL_CARD_POWER_OFF# | held at most 0.1 V (36 uA); released 1.56 V over 1.19 V | Quectel RM520N HD v1.1 Table 9 (VIL 0.2 V, VIH 1.19 V, internal 100 k pull-down); SCES308L 100 uA row | 3.545/99k = 36 uA; 3.135 x 100/201 = 1.56 V at a nominal module pull-down (INFERRED, as stated). Sequencing holds: +3V3_S2A needs PCIE_PWR_EN2 from slot 2 (U216), so U554's +3V3_CM2 is up first. Q207 IDSS 80 nA (JSCJ sheet), negligible. Margin: minor 1. | yes |
| C D4E-F1 R52 + D23 | EMCON_HW at most VF (0.45 V at 10 mA) with C's +3V3 in band; released at least 2.13 V; stuck-high U9 now asserts | DS35124 (VOH 2.4 V at -16 mA, Ioff 10 uA); DS30044 (VF 0.45 V at 10 mA, 25 C) | 1.65/326.7 = 5.1 mA; 2.4 x 3.165/3.498 - 0.111 mA x 0.333k = 2.13 V; released, D23 forward-biased at about 0.2 mA and lifts TX_INHIBIT_n toward 2.9 V (harmless, more margin); assert latency unchanged. Cold VF inferred, as stated. | yes |

## 2. The walk fix (tx_inhibit.py at 14409f4b)

`env -C <clone>/v2/ecad/tools python3 tests/run.py test_tx_inhibit`: **136 passed, 0 failed, 0 skipped**, evidence untouched. Unfixed walk (e41df395's `tx_inhibit.py`, sha256/16 `326d0a4832273004`, in a scratch copy of HEAD's tools): the three new tests FAIL (`has no attribute 'drive_net'`; EMCON_HW "a second BUF output ... 3.36 V"; U543 unclassified), as the record says; the other test_tx_inhibit tests pass.

The three rules are stated as wiring properties with a defective and an acceptable fixture each, not as rules about board C's history (no reference is named; U543's ACCESSORIES entry is a declaration like U221's). REVERSE_IDEAL is sound as a bound: a passive diode's reverse current flows only from the higher node, so an ideal one-way element from the far line bounds the net from above, and failing only with it gives UNDECIDED, never PASS.

| Counterexample (fixed walk) | Expected | EMCON_HW | TX_INHIBIT_n |
|---|---|---|---|
| CX1 expander pin behind its own 330R onto EMCON_HW | FAIL | FAIL (firmware sets) | |
| CX2 2nd buffer on B, input a firmware net, behind 330R | FAIL | FAIL (second BUF) | |
| CX6 clamp diode on EMCON_HW_DRV to +3V3 | not a drive net | FAIL (second BUF) | |
| CX7 inverter, input TX_INHIBIT_n, behind 330R | FAIL | FAIL (second INV) | |
| CX4a BAT46 anode +3V3_DEV, cathode EMCON_HW | FAIL | FAIL | |
| CX4b BAT46 cathode +3V3_DEV, anode EMCON_HW | UNDECIDED | UNDECIDED | |
| CX5 10k pull-up EMCON_HW to +3V3_DEV, plus a reader of TX_INHIBIT_n on B (`_chk/cx5b.py`) | FAIL both | FAIL 1.89 V | FAIL 1.72 V (D23 forward; without a powered reader the fixture reads PASS, correctly n/a) |
| CX3b 2nd buffer on B, input TX_INHIBIT_n, behind 330R, plus 10k pull-up on TX_INHIBIT_n | FAIL both | **PASS** | FAIL |
| CX9 cross-coupled pair on B behind 330R each | FAIL both | **PASS** | **PASS** (blocking 1) |

CX3b is the same hole in a milder form: EMCON_HW reads PASS while the buffer drives it high with board C down, caught only through TX_INHIBIT_n's own FAIL (so board B's rows, which read EMCON_HW alone, would pass). The same wiring directly on the line (old rule) gives the same verdicts.

## 3. The 21 FAILs and the readings, reproduced

`check_contracts.py` into scratch, whole `v2/ecad` from `git archive` where needed; every output `cmp`-identical to the committed file in `records/rf2walk/readings/`:

| Tree / walk | RF-002 rows | inhibit_chain A / B / C / D / E / P | Record |
|---|---|---|---|
| set 12 fixed (HEAD) | 0 FAIL, 11 UNDECIDED, 15 PASS | INCONCL 7/2, INCONCL 12/8, PASS 6, INCONCL 8/1, PASS, PASS | identical |
| set 12 unfixed (e41df395) | 21 FAIL, 5 PASS | FAIL 4, FAIL 17, FAIL 2, FAIL 3, PASS, PASS | identical |
| main, main's walk | 0 FAIL, 7 UNDECIDED, 18 PASS | INCONCL 7/2, INCONCL 16/4, PASS 6, INCONCL 7/1, PASS, PASS | identical |
| main, set 12 unfixed walk | 0 FAIL, 11 UNDECIDED, 15 PASS | | identical |
| main, fixed walk | same bytes as the line above | as set 12 fixed | identical |

The fix moves nothing on main. The classing as instrument holds: the unfixed walk's 3.18 V is U9 powered (3.465 V x 3.229k/(3.229k + 0.3267k) = 3.147 V, plus 111 uA x 0.297k = 0.033 V), the census state, not a fail-safe one. Per-state bounds (`_chk/fs_spy.py`, max over reader domains): EMCON_HW 0.401 V (A, B, C; C down) and 0.584 V (J_AB1 unplugged), identical to main in every fragment; TX_INHIBIT_n 0.354 V (A to D, C down; main 0.243 V) and 0.339 V (ABC; main 0.178 V), worst 0.578 V (A and D alone), unchanged. D23's new path is bounded as stated, under every reader's 0.8 V.

## Minor items

1. B-5 (`gen_sch_b.py` 820): the release margin rests on the module's unstated pull-down tolerance: 1.56 V falls under 1.19 V if it is under about 62 k (-38 %). R238 at 39 k 1% keeps the held current at 92 uA (inside the 100 uA row) and gives 2.25 V nominal, above 1.19 V down to about 24 k.
2. B-4 (1595 to 1596): between 1.65 V and VIT+VHYS (2.90 V) U536 is specified and may drive high, so U543 sinks up to 2.50/2.178k + 17 uA = 1.16 mA, over the 1 mA VOL row; "low whenever under VIT" is shown only for the 0 to 1.65 V band. Also a dip under VIT gives an I_EN low of only td 12 to 28 ms, possibly shorter than the module's shutdown, which the maker says "may result in damage"; add it to bench E-11 or lengthen td with CT.
3. B-3: LORA_GO copies E22_EN, not the rail's power-good, so for U21's turn-on (CT 1 nF) the gates drive host levels (NSS high through R25) into a module whose +5V_LORA is still rising; smaller than as drawn, not claimed. J_SPI3 pins 8 and 9 (IO23, IO24) are also driven now (U552, U551), like MISO; the record names only MISO.
4. B-1: released RB_IEN has 80 mV over 2.0 V on the conservative 2.4 V VOH row. After boot P_EN follows U6 pin 20, an input with its 100 k pull-up (charger off) until firmware sets it; as drawn it was high from power-up, so a firmware item, not a regression.
5. Intent (`pcb-b-compute-intent.json`): +3V3_CM3 and +3V3_CM2 still say "nothing on the carrier draws from it beyond its own bypass network"; U544 to U553 and U554 now do. R538's 0.71 mA is not in +3V3_ZB's loads.
6. REVERSE_IDEAL is narrowed to the other asserted line for a wording reason (LOG 13:24). Harmless: a rail far node would give the same UNDECIDED.
7. `apply_c_d4e_f1.py`'s docstring figure for the unpowered hold (0.32 V) differs from the walk's 0.354 V; both under 0.8 V, the walk's is the one to cite.
