# Board B failover fabric: lane, pin and clock map, contracts and feasibility blockers

MESHSAT-1357, review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`), section 3,
third item: "For three-slot compute failover, retain a reviewed lane/pin/clock map, cross-board contracts and a
feasible Board B escape strategy." Written 26 September 2026, 14:45 CEST, by the FAB stream of the session; revised
15:19 CEST after the checker's first review (FAB-04 and FB-FAB-5 now count 21 controller outputs, R480 to R500, and
23 safe-low lines, where the first version said 18 and 20) and 16:39 CEST after its second (FAB-04 reads the
supervisor's pin types pin by pin, `PA5` is TT_ha; the H753 that `main` carries is cited from its own datasheet,
[MCU-53]; the supervisor pin's leakage now includes DS12110 Table 60 note 4's 10 uA product term, which moves no
verdict).

**Prototype design.** No V2 board has been fabricated, ordered, assembled or powered, and board B has never been routed
to completion. This page is a desk review of netlists against manufacturer documents. It is not a bench result, it is
not electrical sign-off, it authorises no layout (owner condition 7 of 25 September 2026) and it changes no generator.

Evidence labels, as in `B-FEASIBILITY.md`: **VERIFIED** (read in the cited artefact), **RECORDED** (a measurement written
into the tree whose run is not re-read here), **INFERRED** (reasoned from verified facts, and the reasoning is given),
**TBD** (no source held; its effect is stated instead of a convenient value).

## 1. The short answer

1. **The corrected netlist wires every fabric lane the way the parts' own documents ask.** The candidate of round 6
   (section 2) was checked row by row against the far-end pin each datasheet calls for: 202 of its 341 rows carry an
   expected far end and all 202 read OK; the committed B21 netlist on `main` misses 28 of the same rows (the crossed PCIe
   downstream links and LimeSDR SuperSpeed pairs, W3-F01 and W3-F02), carries no reference clock termination or
   coupling (W3-F03) and leaves the supervisors' I2C pins unconnected (W5-F3). The seven voted control bits evaluate
   as 2-of-3 majorities on both netlists (VERIFIED, section 4.9).
2. **This review found eight items the round-6 record does not carry** (section 9): four major (FAB-01 to FAB-04),
   two minor (FAB-05, FAB-06), one evidence gap (FAB-07) and one placement item (FAB-08). The six that bear on what the
   fabric does, one of them in every PCIe switch, are:
   - FAB-01: the PI7C9X2G404SL `TEST2` strap is pulled low where the datasheet requires 5.1 kOhm to 3.3 V, on all three
     switches, on `main` and in the candidate;
   - FAB-02: the always-on fabric applies voltage to the pins of an unpowered compute module, which the module's
     datasheet forbids, at every kit power-up and whenever a slot is off;
   - FAB-03: the hardware break-before-make changes the select first and disables the switch one gate delay later, so
     IOHA test A10's pass criterion cannot be met as generated;
   - FAB-04: the 100 kOhm pull-downs that are meant to hold a dark controller's votes (all 21 controller outputs,
     seven voted bits times three controllers, R480 to R500) and an absent panel's two display selects (R15, R16) low
     do not hold any of those 23 lines below the logic threshold at the parts' datasheet leakage;
   - FAB-05: the CAN transceiver fitted is specified to 1 Mbps, while the design text claims 5 Mbps;
   - FAB-08: the escape trial's own limit understates the corrected switch pocket: 18 parts per pocket are to be seated
     beside the switch, in pockets that had 0.0 mm of room, and the trial does not include them.
3. **What is validated** is connectivity, direction, polarity, coupling location, termination and strap values against
   datasheet clauses, on a netlist. **What is not validated** is everything that needs copper or silicon: impedance and
   loss at routed length, the reference clock's jitter through the switch's buffer, the escape strategy, the power-state
   behaviour on a bench, and every IOHA acceptance test A1 to A14 (section 7).
4. **Board B's escape strategy is diagnosed, not demonstrated.** `B-FEASIBILITY.md` (pending merge) finds the failure
   is not shown to be physical and names the floor plan, a single escape pattern and the stackup's use as the causes.
   The bounded trial Q-B-ESC-1 is box-ready and has not been run; the eight-layer whole-board run of decision 43 has not
   been run (section 8).
5. **The fabric's feasibility blockers are listed in section 10 with the evidence that closes each.** None is closed by
   this page. Two of them (FAB-02, FAB-03) sit on functions of prototype 1's named core (D-01: the three-slot failover
   fabric, IOHA A1 to A14).

## 2. What was read

| Artefact | Identity | Read for |
|---|---|---|
| **Board B round-6 candidate netlist** | `drafts/box/r6-run6/tint/regen/pcb-b-compute.net` of worktree `fnd/r4b` (rebuilt by command N1 of `v2/docs/records/README.md`), sha256 `af8a9186f981210c48104eaf5742fb4cd4f80d12aa0f13bc5d887e75c922a380`; written by `gen_sch_b.py` sha256 `6e3d880901fd30306c0fa8bda35a86da6450d7e4bb15217f9cc3225da8d5faef` (uncommitted in worktree `fnd/r4b` on base `82dd1e4d`, applied to `main` `faf8c981` on the box, run 6, 26 Sep 2026 10:51 to 11:33 UTC); the `t6` regeneration of the same generator is PARITY_AFTER_NOISE with it (content hash `142fe788dabbaf58`, `v2/docs/records/r4b/box/r6-run6/parity_netlist_t6_tint.json`). It is byte for byte the file the round-6 integration set (O-18) commits as `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` (`v2/docs/records/r4b/box/r6-run6/tint/set.sha256`) | every row of the map |
| Board B B21 netlist on `main` | `v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net` at `1f614233`, sha256 `0e72edb5d755316f6a55ce915c1c23103ecc11054904f813ec2942aca7e975c9`, generator sha `66e68fe66ab81617`, schematic sha256 `eac5845f...` | the "B21" column |
| B21 pre-route board | `v2/ecad/pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb` at `1f614233`, sha256 `62facf0952ff4c01...` | footprint origins for the distance screen (section 8.3) |
| Board A netlists | A23 on `main`: `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`, sha256 `aa1372ba3932610f...`; round-6 candidate: `drafts/box/fixup3-run2/repo/pcb-a-power.net` of worktree `fnd/r4a` (rebuilt by command N4 of `v2/docs/records/README.md`), sha256 `daf132b22fad9854...` (`gen_sch_a.py` sha256 `17c204ad4fb0cddb...`) | cross-board pins and enables (section 6) |
| Board C netlist | C24 on `main`: `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net`, sha256 `2834f0d8c4071d56...` | the panel end of `J_PANEL` |
| Round-6 author records | `v2/docs/records/r4b/r4-decisions.md` (sha256 `27023b76...`), `v2/docs/records/r4b/r4-interfaces.md` (`dafa398f...`), `v2/docs/records/r4b/box/r6-run6/` (README, run log, gate emulation; the rest of the run directory is listed in `v2/docs/records/README.md`) | what the candidate changed and why; open items O-01 to O-24 |
| Feasibility and architecture pages, pending merge | `scratchpad/wt/i3/v2/docs/B-FEASIBILITY.md` sha256 `5a46e459d6b3f241...`, `ARCHITECTURE.md` sha256 `5f7534a8e4cf8633...`, trial scripts `v2/ecad/tools/routeflow/experiments/b_esc1/` (`run.sh` `a7e32b81...`, `judge.py` `0d849b25...`) | escape strategy and Q-B-ESC-1 (section 8) |
| IOHA architecture note | `v2/docs/ARCH-PCB-B-IOHA.md` at `1f614233` | the intended behaviour the map is judged against |
| Raspberry Pi CM5 IO board design files | `v2/vendor/cm5/cm5io-kicad.zip` (its `CM5IO.kicad_pcb` and `PCIe-M2.kicad_sch`) | the module maker's own wiring of PCIe and its clock |

Manufacturer documents, every one read in this session (text extracted with `pdftotext -layout`; page numbers are PDF
page numbers):

| Ref | Document | File, sha256 |
|---|---|---|
| [CM5] | Raspberry Pi Compute Module 5 datasheet, release 3, build date 08/06/2026 | `v2/vendor/cm5/cm5-datasheet.pdf`, `80070fef...` |
| [SW] | Diodes PI7C9X2G404SL, DS40068 Rev 5-2, July 2025 | `v2/vendor/diodes/diodes-pi7c9x2g404sl.pdf`, `675fa7ee...` |
| [HUB] | TI TUSB8041, SLLSEE4E, June 2016 | `v2/vendor/ti/ti-tusb8041.pdf`, `b715bce7...` |
| [MUX] | TI TMUXHS4212, SLASEP7A, May 2022; and SLLA552 schematic checklist, March 2021 | `v2/vendor/ti/ti-tmuxhs4212.pdf`, `34fa7c38...`; `ti-slla552-tmuxhs4212-schematic-checklist.pdf`, `5258cb80...` |
| [U2M] | TI TS3USB221A, SCDS277C, revised October 2024 | `v2/vendor/ti/ti-ts3usb221a.pdf`, `cccebf8c...` |
| [HDS] | TI TS3DV642, SCDS343F, revised August 2018 | `v2/vendor/ti/ti-ts3dv642.pdf`, `31e45a07...` |
| [KSZ] | Microchip KSZ989x hardware design checklist DS00004151A | `v2/vendor/cluster/ksz989x-hw-design-checklist.pdf`, `2a9d8093...` |
| [CAN] | TI TCAN33x, SLLSEQ7F, revised May 2025 | `v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf`, `bb89f067...` |
| [MCU] | ST STM32H743, DS12110 Rev 10, March 2023: the supervisor the candidate carries (value "STM32H743VIT6") | `v2/vendor/st/st-stm32h743xi-datasheet.pdf`, `9b27d1d9...` |
| [MCU-53] | ST STM32H753, DS12117 Rev 9, March 2023: the supervisor B21 on `main` carries (value "STM32H753VITx"). The clauses this page cites stand on the same PDF pages with table numbers one lower than DS12110's: Table 8 for Table 9 (pin/ball definition), Tables 10 and 12 for Tables 11 and 13 (ports B and D alternate functions), Table 59 for Table 60 (I/O static characteristics) | `v2/vendor/st/st-stm32h753xi-datasheet.pdf`, `3bf346d8a511843ac6f5397a0e1c59d83e7ed70c7835fde72669fa545f4bd9d7` |
| [5G] | Quectel RM520N series hardware design V1.1 | `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf`, `2bae8821...` |
| [AND], [OR] | TI SN74LVC08A SCAS283W (July 2024); SN74LVC32A SCAS286U | `v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf`, `9cefbf42...`; `ti-sn74lvc32a-quad-or.pdf`, `807f6fff...` |
| [XOR-TI] | TI SN74LVC86A, SCAS288R, revised August 2024. **Fetched by this session**: https://www.ti.com/lit/ds/symlink/sn74lvc86a.pdf, 26 Sep 2026 12:31 UTC | `v2/vendor/ti/ti-sn74lvc86a.pdf`, `8115c852d23ce42a0a2518462474171d809c6d6ad5ed28f21c110bdb5a60a334` |
| [XOR-NX] | Nexperia 74LVC86A, Rev. 8, 25 January 2024. **Fetched by this session**: https://assets.nexperia.com/documents/data-sheet/74LVC86A.pdf, 26 Sep 2026 12:31 UTC | `v2/vendor/nexperia/nexperia-74lvc86a.pdf`, `aa449c7949d141d555967710a235c7686a6ece02468f783f8c8cf924a1fc926a` |

**How the map was read.** `fab/fabmap.py` (sha256 `5b2bb0cf...`, with `tracer.py` `b624e4f6...` and
`netparse.py` `f1ebef1f...`) starts at a named pin, follows two-pin passives in series and records shunts, on both
netlists; each row that has one carries the far-end pin the documents call for, and the script prints OK or MISMATCH.
`render.py` (`9a1c6353...`) turns its JSON into Appendix A. `voters.py` (`8d8f5d85...`) evaluates the voters from the
netlist; `lengths.py` (`af726f49...`) is the distance screen; `pulldowns.py` (`daf62816...`) judges the 23 safe-low
pull-downs of FAB-04 at datasheet leakage, enumerating their designators from the generator's rule
(`out/pulldowns.txt`, `895f8df0...`), and `pulldowns_mut.py` (`f4aae148...`) is its mutation set
(`out/pulldowns-mutations.txt`, `7510bd67...`). All read-only. They were written in the session's worktree `fnd/rv-fab` (`drafts/fab/`) and are filed, byte for byte,
in `v2/docs/feasibility/fab/` beside this page (integration of 26 September 2026), with the outputs this page cites in
`fab/out/` and the scripts' sha256 in `fab/out/SHA256SUMS-scripts.txt`. They are the page's working files, not
repository tools: no test or gate runs them. The root rule `out/` (`.gitignore:20`) would drop the cited outputs;
`fab/.gitignore` (`!out/`) re-includes them. The text extractions of the datasheets (`drafts/fab/txt/`) are not
filed: they derive from the PDFs held in `v2/vendor/`.

**A note on the brief.** The brief for this page names "HDMI through TMDS341A". The fitted display switch is the
TS3DV642 (two in cascade); the TMDS341A is NOT_FITTED (`v2/vendor/SOURCES.yaml`, entries `hdmi-switch` and
`tmds341a`; VERIFIED in both netlists). The map uses the TS3DV642.

## 3. The fabric in one table

| | Slot 1 | Slot 2 | Slot 3 |
|---|---|---|---|
| CM5 receptacles (A: pins 1 to 100, B: 101 to 200) | U30A, U30B | U31A, U31B | U32A, U32B |
| PCIe switch (upstream the module's Gen 2 x1) | U101 | U201 | U301 |
| Port 1 (NVMe, M.2 key M) / port 2 (card) / port 3 | J_M2N1 / J_M2C1 key E, AW7915-AED / unused | J_M2N2 / J_M2C2 key B, RM520N-GL / unused | J_M2N3 / J_M2C3 key E, second AW7915-AED / unused |
| USB3-0 is the home host of | bank 1 (hub U102, muxes U109, U110) | bank 2 (U202, U209, U210) | bank 3 (U302, U309, U310) |
| USB3-1 is the failover host of | bank 3 | bank 1 | bank 2 |
| HDMI0 enters | U3 port A | U3 port B | U4 port B (U3's output is U4's port A) |
| Ethernet enters KSZ9897R U1 | port 1 | port 2 | port 3 |
| Heartbeat (GPIO16) | HB1 | HB2 | HB3 |

The ring is bank b to slot `b % 3 + 1` on the loss of its home module (`gen_sch_b.py:788` in the candidate, `:543` on
`main`), which both netlists carry (VERIFIED, Appendix A, "USB failover host").

## 4. The map

Every row below is read from the candidate netlist; Appendix A gives each pin separately, with the B21 comparison.
"Coupling" names where the series capacitor sits; "Clause" is the requirement it answers.

### 4.1 PCIe upstream, module to switch (per slot s = 1, 2, 3)

| Signal | CM5 pin (U30B/U31B/U32B) | Net | In series | Switch pin (U101/U201/U301) | Coupling | Clause |
|---|---|---|---|---|---|---|
| module TX+ / TX- | 122 `PCIe_TX_P` / 124 `PCIe_TX_N` | `PCIE{s}_TX_P/N` | none on board B | 128 `PERP0` / 127 `PERN0` | on the CM5 | [CM5] pin table, PDF p.21: pins 122/124 "AC coupling capacitor included on CM5"; 2.3.1, PDF p.9: "Direct IC connection ... swap the transmit (TX) and receive (RX) differential pairs" |
| module RX+ / RX- | 116 `PCIe_RX_P` / 118 `PCIe_RX_N` | `PCIE{s}_RX_P/N`, switch side `PCIE{s}_RXSW_P/N` | C{s}51 / C{s}52, 220 nF 16 V 0402 | 124 `PETP0` / 123 `PETN0` | on board B, to be placed at the switch (layout) | [CM5] 2.3, PDF p.9: "external AC coupling capacitors are required for PCIe_RX signals, close to the driving source (the peripheral's TX)"; 2.3.1: "an AC coupling capacitor (220 nF) before it enters the IC" |

Polarity: P to P and N to N on all twelve upstream wires (VERIFIED); [CM5] 2.3.1 would also allow a swap within a pair.
Identical on `main` (the upstream capacitors were added on 16 September, `gen_sch_b.py` comment at candidate
`:490-497`).

### 4.2 PCIe control and the module's clock (per slot)

| Signal | CM5 pin | Far end | Parts | Clause and reading |
|---|---|---|---|---|
| `PCIe_CLK_P/N` (module 100 MHz out) | 110 / 112 | switch 74 `REFCLKI_P` / 73 `REFCLKI_N` | none: DC coupled, no board termination | [SW] Table 8-1 note 4, PDF p.75: "If the reference clock input is HCSL type, it should use DC coupling". [CM5] says only "PCIe clock-out positive (100 MHz)" (pin table, PDF p.21): its output standard, swing and spread spectrum are not published (TBD, section 5.3). Raspberry Pi's own carrier wires the same pins straight to an M.2 socket with no series part and no termination (`CM5IO.kicad_pcb`: `PCIE_CLK_P` Module1.110 to J4.55, `PCIE_CLK_N` Module1.112 to J4.53; VERIFIED), which is the module maker's practice for this output |
| `PCIe_CLK_nREQ` | 102 | none | R{s}29 1 kOhm to GND | [CM5] 2.3.2, PDF p.9: "PCIe_CLK_nREQ must be connected to enable clock output from CM5"; tied low, so the clock always runs. The switch cannot forward CLKREQ (candidate `:569` comment) and the sockets' CLKREQ# pins only carry pull-ups (R{s}33 10 kOhm to `+3V3_S{s}B` at the NVMe, R{s}34 10 kOhm to the card rail; VERIFIED) |
| `PCIe_nRST` | 109 | switch 10 `PERST_L` | none | [SW] 3.1, PDF p.12: `PERST_L` input; `DWNRST_L1/L2` (pins 5/6) reset the two sockets |
| `PCIE_nWAKE` | 104 | NVMe 54 `PEWAKE#`; card 55 (key E) or 54 (key B) | R{s}32 10 kOhm to `+3V3_S{s}B` | [CM5] 2.3.2: "available, but currently unsupported in software". A card whose rail is off sees this pull-up on its pin (round-6 O-06) |
| `PCIE_PWR_EN` | 106 | slots 1, 3: R{s}64 10 kOhm to the card buck's EN and Q{s}11 (EMCON); slot 2: U203 EN directly | R{s}06 100 kOhm to GND | [CM5] pin table, PDF p.21 |

### 4.3 The reference clock tree (per slot)

```text
CM5 PCIe_CLK_P/N (110/112) --- DC, no board termination ---> switch REFCLKI_P/N (74/73) -> clock buffer (CLKBUF_PD open)
switch REFCLKO0 (85/83) -- Rs 33.2R --+-- 100 nF --> switch's own REFCLKP/N (110/111)
                                      +-- Rp 49.9R to GND
switch REFCLKO1 (81/80) -- Rs 33.2R --+-----------> NVMe socket REFCLKp/n (55/53)
                                      +-- Rp 49.9R to GND
switch REFCLKO2 (78/77) -- Rs 33.2R --+-----------> card socket REFCLKp/n (key E 47/49, key B 55/53)
                                      +-- Rp 49.9R to GND
switch REFCLKO3 (76/75) unused, open
```

| Item | Slot 1 / 2 / 3 parts | Clause |
|---|---|---|
| Source | the module's own clock, common to the whole slot (`SLOTCLK` pulled up, R{s}19 5.1 kOhm) | [SW] 3.2, PDF p.13: "When SLOTCLK is high, the platform reference clock is employed"; section 8, PDF p.75: "One of the integrated reference clock buffer output pairs of the Switch can be connected to the Switch through REFCLKP/N pins, and the other two ... can be used by downstream devices" |
| Buffer enable | `CLKBUF_PD` (60) left open | [SW] 3.1, PDF p.12: internal pull-down, "If no board trace is connected to this pin, the internal pull-down resistor of this pin is enough" |
| Output current | `IREF` (86): R{s}17 475 Ohm 1% to GND | [SW] 3.1: "External resistor (475 Ohm +/- 1%)" |
| PHY bias | `REXT` (116): R{s}18 1.43 kOhm 1% to `REXT_GND` | [SW] 3.1: "1.43K Ohm +/- 1%" |
| Output termination, all three used pairs | Rs R{s}75/76, R{s}79/80, R{s}83/84 33.2 Ohm; Rp R{s}77/78, R{s}81/82, R{s}85/86 49.9 Ohm to GND (36 resistors, round-6 fix-up B-1) | [SW] Table 8-1 note 1, PDF p.75: "Test configuration is Rs=33.2Ω, Rp=49.9Ω, and 2pF" |
| AC coupling into the switch's PHY clock | C{s}95 / C{s}96, 100 nF | [SW] 3.1, PDF p.12: "must be delivered to the clock buffer cell through an AC-coupled interface ... It is recommended that a 0.1uF be used"; Table 8-2 note 4, PDF p.76 |
| Sockets' REFCLK | straight from the Rp node to the socket, no coupling | the M.2 endpoint's input; the RM520N reference circuit puts only 0 Ohm links there ([5G] Figure 21, PDF p.48) |

On `main` (B21) all nine used output pairs have neither Rs nor Rp and `REFCLKO0` drives `REFCLKP/N` directly (W3-F03;
Appendix A shows every row as "differs").

### 4.4 PCIe downstream (per slot and port)

| Link | Switch transmitter | Series part | Socket pin (host-view name) | Socket pin back | Switch receiver |
|---|---|---|---|---|---|
| port 1, NVMe (key M) | 100 `PETP1` / 101 `PETN1` | C{s}53 / C{s}54, 220 nF | 49 `PETp0` / 47 `PETn0` | 43 `PERp0` / 41 `PERn0` | 97 `PERP1` / 98 `PERN1` |
| port 2, card key E (slots 1, 3) | 106 `PETP2` / 107 `PETN2` | C{s}55 / C{s}56, 220 nF | 35 `PETp0` / 37 `PETn0` | 41 `PERp0` / 43 `PERn0` | 102 `PERP2` / 103 `PERN2` |
| port 2, card key B (slot 2, RM520N-GL) | 106 / 107 | C255 / C256, 220 nF | 49 `PETp0` / 47 `PETn0` | 43 `PERp0` / 41 `PERn0` | 102 / 103 |
| port 3 | 118/117, 122/121 open | | | | |
| resets | `DWNRST_L1` (5) to NVMe 50; `DWNRST_L2` (6) to card 52 (key E) or 50 (key B) | | | | |

Clauses. Direction: [SW] 3.1, PDF p.12 (`PETP` type O "transmit", `PERP` type I); [CM5] 2.3.1: "If using a PCIe
connector, the signals are labelled from the host's point of view". Physical pin function, from primary sources: the
RM520N pin table gives 41/43 as the module's `PCIE_TX` (AO) and 47/49 as its `PCIE_RX` (AI) ([5G] PDF p.24);
Raspberry Pi's carrier wires its key M socket's 41/43 to the module's receive pins and 47/49 to its transmit pins
(`CM5IO.kicad_pcb`, J4; VERIFIED). Coupling at the switch's transmitter: [5G] 4.3.3, PDF p.48: "AC coupling capacitors
C3 and C4 should be placed close to the host on PCB. C1 and C2 have been integrated inside the module"; [CM5] 2.3, PDF
p.9: "PCIe and NVMe cards include these capacitors on board". Polarity is P to P on every link (VERIFIED);
`RXPOLINV_DIS` (24) is left open, so the switch's receive polarity detection stays enabled ([SW] 3.2, PDF p.13).

**Symbol libraries name these pins from opposite sides.** KiCad's `Bus_M.2_Socket_M` (the candidate's symbol) names
pin 43 `PERp0` and 49 `PETp0`; Raspberry Pi's own `CM5IO:Bus_M.2_Socket_M` names pin 43 `PETp0` and 49 `PERp0`
(`PCIe-M2.kicad_sch`, VERIFIED). The physical function above is the same in both, so the only safe reading is by pin
function from the device's pin table, never by the symbol's name. This is the mechanism behind W3-F01.

**Key E has no primary pin table in this tree** (FAB-07): the E-key assignment (35/37 host transmit, 41/43 host
receive, 47/49 clock) comes from KiCad's symbol and the M.2 convention only; the AW7915-AED datasheet held
(`v2/vendor/wifi/asiarf-AW7915-AED-datasheet.pdf`) has no pin table and TE's 2199230 drawing is mechanical. A wrong
reading would recreate W3-F01 on slots 1 and 3.

B21 on `main` has all 24 downstream data wires reversed (transmitter to transmitter) and no downstream capacitors
(W3-F01; Appendix A, 24 MISMATCH rows).

### 4.5 The switch's straps and test pins (per slot)

| Pin | Net and part | Datasheet requirement ([SW] 3.2 to 3.4, PDF pp.13-14) | Reading |
|---|---|---|---|
| `TEST1` (9) | R{s}23 5.1 kOhm to `+3V3_S{s}B` | "tied to 3.3V through a 5.1K-ohm pull-up resistor for normal operation" | OK |
| **`TEST2` (16)** | **`S{s}_TESTL`, R{s}24 330 Ohm to GND** | **"Test2 should be tied to 3.3V through a 5.1K-ohm pull-up resistor."** | **WRONG on all three switches, B21 and candidate (FAB-01)** |
| `TEST3`, `TEST5`, `TEST6` (17, 25, 51) | `S{s}_TESTL`, 330 Ohm to GND | "tied to ground through a 330-ohm pull-down resistor" | OK |
| `TEST4` (22) | `S{s}_TESTL` | "tied to ground through a 330-ohm pull-down resistor for normal operation" | OK |
| `VC1_EN` (18) | `S{s}_TESTL` | low disables VC1; 330 Ohm recommended if a trace is attached | OK |
| `TMS` (92), `TRST_L` (94) | `S{s}_JTAGL`, R{s}28 330 Ohm to GND | "pulled low through a 330-Ohm pull-down resistor" | OK |
| `TCK` (89), `TDI` (93) | `S{s}_JTAGL`, 330 Ohm to GND | "should be left open (NC)" when JTAG is not implemented | deviation, minor (FAB-01) |
| `PRSNT1`, `PRSNT2` (19, 20) / `PRSNT3` (21) | GND / R{s}21 5.1 kOhm up | low = device present | ports 1, 2 present, 3 absent: OK |
| `SLOT_IMP1/2` (45/46) / `SLOT_IMP3` (47) | R{s}20 5.1 kOhm up / open | high = port wired to a slot | OK |
| `PWR_SAV` (28) | R{s}22 330 Ohm to GND | low: power saving off, "330-ohm pull-down" | OK |
| `SMBCLK`, `SMBDATA` (26, 27) | 5.1 kOhm up each | "requires an external 5.1K-ohm pull-up" | OK (no SMBus host) |
| `EEPD` (71) | R{s}27 4.7 kOhm to GND, no EEPROM | autoload needs the signature 1516h ([SW] 6.1.3) | INFERRED harmless: with the line low no signature reads |

`check_pcb_b.py` does not judge these straps (it checks nets and directions); nothing in the tree compares a strap to
the datasheet's table.

### 4.6 USB banks: home and failover hosts (per bank b; home slot b, failover slot f = b % 3 + 1)

| Path | Module pin (home: slot b / failover: slot f) | Mux pin (home B / failover C) | Mux common side | Hub pin (U{b}02) | Coupling |
|---|---|---|---|---|---|
| module TX to hub RX, SuperSpeed | home 142/140 `USB3-0-TX_P/N`; failover 171/169 `USB3-1-TX_P/N` | U{b}09 B0p 19 / B0n 18; C0p 15 / C0n 14 | A0p 3 / A0n 4, net `BANK{b}_UPTX_P/N` | 58 `USB_SSRXP_UP` / 59 `USB_SSRXM_UP` | on the CM5 ([CM5] pin table, PDF pp.22-23: "AC coupling capacitor included on CM5") |
| hub TX to module RX, SuperSpeed | home 130/128 `USB3-0-RX_P/N`; failover 159/157 `USB3-1-RX_P/N` | B1p 17 / B1n 16; C1p 13 / C1n 12 | A1p 7 / A1n 8 (`MUX{b}_A1P/N`) | 55 `USB_SSTXP_UP` / 56 `USB_SSTXM_UP`, through C{b}59 / C{b}60 100 nF on the hub side of the mux | [HUB] 11.1.1 item 3, PDF p.38: "The 100 nF capacitors on the SSTXP and SSTXM nets"; one pair of capacitors serves either host |
| USB 2.0 | home 134/136 `USB3-0-DP/DM`; failover 163/165 `USB3-1-DP/DM` | U{b}10 1D+ 1 / 1D- 2; 2D+ 3 / 2D- 4 | D+ 8 / D- 7 | 53 `USB_DP_UP` / 54 `USB_DM_UP` | none (USB 2.0) |
| select and enable | | `SEL` (9) and `S` (9) on `BSEL{b}`; `OEn` (2) and `OEn` (6) on `BOE{b}_n` | | | |

Clauses. [MUX] Table 8-1 "Port Select Control Logic", PDF p.10: with `SEL = L` port A's channels connect to port B's,
with `SEL = H` to port C's, so `BSEL` low is home; [U2M] Table 7-1 "Truth Table", PDF p.13 (columns S, OE): "L L D =
1D", "H L D = 2D", "X H Disconnect". Biasing: [MUX] 8.3.2, PDF p.10: "To avoid double biasing, ensure
that the appropriate ac coupling capacitors are on either side of the device"; SLLA552 Table 1-1, PDF p.2: the
transmit channel needs its 100 nF on the B/C side ("Need 100-nf AC cap"), which the module's on-board capacitors are,
and the receive channel is "Biased by host controller", which it is, since C{b}59/60 sit on the hub side. The
TMUXHS4212 carries no USB 2.0 because its common-mode range is 0 to 1.8 V ([MUX] 6.3, PDF p.4), hence the TS3USB221A.
[CM5] 2.4, PDF p.9: USB 3.0 pairs may be P/N swapped, USB 2.0 pairs may not; every wire here is P to P (VERIFIED).
[MUX] Table 8-1 note 1: the mux tolerates polarity inversion.

Hub side, per bank: `USB_VBUS` (48) from a 90.9 kOhm / 10 kOhm divider on **`+5V_DEV`** (R{b}43/R{b}44), which is the
divider [HUB] asks for on its pin table (PDF p.5: "USB_VBUS must be connected to VBUS through a 90.9-KΩ ±1% resistor,
and to ground through a 10-kΩ ±1% resistor") but fed from the always-on rail, not from a host (FAB-02). `GRSTz` (50):
R{b}41 10 kOhm to `+3V3_DEV` and C{b}63 1 uF, pulled low by the voted Q3/Q4/Q5. The hub, its 1.1 V core (U{b}06 from
`+5V_DEV`) and both muxes are on the device rails, so a bank outlives its home module (IOHA section 10a).

Bank 1's only SuperSpeed downstream port goes to the LimeSDR: hub 3/4 `USB_SSTXP/M_DN1` through C161/C162 to `J_LIME`
9/8 `SSTX+/-`, and `J_LIME` 6/5 `SSRX+/-` back to hub 6/7. B21 has both pairs crossed (W3-F02; Appendix A).

### 4.7 HDMI through the two TS3DV642

| Stage | Inputs | Output | Select | Enable |
|---|---|---|---|---|
| U3 | port A: slot 1 HDMI0; port B: slot 2 HDMI0 | common side `HDMIM_*` to U4 port A | `SEL2` (17) = `HDMI_SEL1`, panel GPIO16, R15 100 kOhm to GND | `EN` (2) and `SEL1` (16) tied together, R14 10 kOhm to `+3V3_DEV` |
| U4 | port A: U3's output; port B: slot 3 HDMI0 | common side to `J_HDMI` (TMDS 1/3, 4/6, 7/9, 10/12; DDC 15/16 with R17/R18 2.2 kOhm to `+5V_HDMI`; HPD 19 through R19 15 kOhm with R20 22 kOhm to GND; CEC 13) | `SEL2` = `HDMI_SEL2`, panel GPIO17, R16 100 kOhm to GND | as U3 |

Every CM5 pin reaches its port P to P: `HDMI0_TX2/TX1/TX0/CLK` (170/172, 176/178, 182/184, 188/190) to `D2/D1/D0/D3`,
`HDMI0_SDA/SCL` (199/200), `HDMI0_HOTPLUG` (153), `HDMI0_CEC` (151) (VERIFIED, 36 rows, Appendix A). HDMI1 of every
module is unused. Clauses: [HDS] Table 1, PDF p.16: "H H L: All A channels are enabled", "H H H: All B channels are
enabled", "L X X: Switch disabled. All channels are Hi-Z"; so with `EN` and `SEL1` high, `SEL2` alone chooses, and the
default (both selects low) is slot 1. [HDS] 9.2.3.2, PDF p.21: "Pull-up resistors to 5 V must be placed on the source
side DDC clock and data lines ... A weak pull-down resistor must be placed on the source side HPD line": the modules
carry both internally ([CM5] pin table, PDF p.23: `HDMI0_SDA` "internally pulled up with a 1.8 kΩ. 5 V tolerant";
`HDMI0_HOTPLUG` "internally pulled down 100 kΩ"). [CM5] 2.5.1, PDF p.10: 100 Ohm pairs, 0.15 mm within a pair, 25 mm
between pairs.

### 4.8 Ethernet to the KSZ9897R

Per slot, the module's four pairs reach switch port s through one 100 nF per wire, pair 0 to lane A, 1 to B, 2 to C,
3 to D, P to P: slot 1 `U30A` 12/10, 4/6, 11/9, 3/5 to U1 1/2, 4/5, 6/7, 8/9 through C175 to C182; slot 2 to U1
12/13, 15/16, 17/18, 20/21 (C275 to C282); slot 3 to U1 24/25, 26/27, 28/29, 31/32 (C375 to C382) (VERIFIED, 24 rows).
Clauses: [KSZ] 6.6, PDF p.12: "A single DC blocking 0.1 μF capacitor is placed in series on each of the eight signals
... Keep auto-negotiation enabled when 1000M speed is used"; [CM5] 2.2, PDF p.8: "Automatic MDI crossover, pair skew
correction, and pair polarity correction", "100 Ω differential pairs". This is decision 29, ruled by the session on
21 September 2026, with its firmware condition (never force speed or duplex on ports 1 to 3).

### 4.9 The control plane: votes, read-back, break-before-make, heartbeats, CAN

**Controller outputs and voters** (candidate; the three supervisors U41, U51, U61 are STM32H743VIT6 in LQFP-100 on
private 3.3 V rails from U40/U50/U60, AP2112K from `+5V_DEV`):

| Voted bit | Controller pin (same on A, B, C) | Pull-down per controller | Voter (SN74LVC08A ANDs, SN74LVC32A ORs) | Voted net and its loads | Read back on |
|---|---|---|---|---|---|
| bank 1 select | PA0 (22) `SEL1_A/B/C` | R480, R481, R482, 100 kOhm | U70 gates 1 to 3, U76 gates 1 and 2 | `BSEL1`: U109 `SEL`, U110 `S`, U80 pin 1, R474 to `BSEL1_D` | PE8 (38) on all three |
| bank 2 select | PA1 (23) | R483 to R485 | U70 gate 4, U71 gates 1 and 2, U76 gates 3 and 4 | `BSEL2`: U209, U210, U80 pin 4 | PE9 (39) |
| bank 3 select | PA2 (24) | R486 to R488 | U71 gates 3 and 4, U72 gate 1, U77 gates 1 and 2 | `BSEL3`: U309, U310, U80 pin 10 | PE10 (40) |
| hub 1 reset | PA3 (25) | R489 to R491 | U72 gates 2 to 4, U77 gates 3 and 4 | `HUBRST1_VOTE` to Q3 gate (pulls `HUB1_RST_n` low), R477 100 kOhm | not read back |
| hub 2 reset | PA4 (28) | R492 to R494 | U73 gates 1 to 3, U78 gates 1 and 2 | `HUBRST2_VOTE` to Q4 | not read back |
| hub 3 reset | PA5 (29) | R495 to R497 | U73 gate 4, U74 gates 1 and 2, U78 gates 3 and 4 | `HUBRST3_VOTE` to Q5 | not read back |
| WiFi changeover | PE7 (37) | R498 to R500 | U74 gates 3 and 4, U75 gate 1, U79 gates 1 and 2 | `WIFI_SEC`: Q10, U82/U83 control | PE11 (41) |

`voters.py` evaluated all seven voted nets for all eight states of their three inputs on both netlists: **7 of 7 are
2-of-3 majorities** (VERIFIED, pinout per [AND] and [OR] pin tables). "Each controller reads the
four voted bits back" (FMEA row 6 of IOHA section 12) holds (BSEL1 to 3 and WIFI_SEC on all three controllers).
Every controller output has its own 100 kOhm to GND, **21 resistors, R480 to R500** (seven bits times three
controllers, designator 480 + 3j + i for bit j of `CTRL_BITS` and controller i, `gen_sch_b.py:1229-1232` in the
candidate, `main :904-907`), each the only resistor on its net, with two SN74LVC08A inputs and the controller's pin on
it, and in the candidate a test pad TP514 to TP534 (VERIFIED on both netlists, `out/pulldowns.txt`). IOHA's text says
"Six voters" and "eighteen controller outputs" (`ARCH-PCB-B-IOHA.md:175` and `:178` at `1f614233`), which predates
`WIFI_SEC`; section 9 lists it for the integrator.

**Break-before-make.** U80 (quad XOR, value "74LVC86APW") drives `BOE{b}_n` = `BSEL{b}` XOR `BSEL{b}_D`, where
`BSEL{b}_D` is `BSEL{b}` through R474/R475/R476 10 kOhm into C481/C482/C483 10 nF (tau 100 us). The muxes' `SEL`/`S`
take `BSEL{b}` itself. See FAB-03 for what that ordering does.

**Module heartbeats.** GPIO16 of each module (`U3xA` pin 29, net `HB_CM{s}`, R{s}57 10 kOhm to the module's own
3.3 V) drives the shared `HB{s}` line through the bidirectional stage Q{s}05 (2N7002, gate on `+3V3_CM{s}`); `HB{s}`
has 10 kOhm to `+3V3_DEV` (R158, R258, R358) and is read by all three supervisors (PA6 30, PA7 31, PC4 32) and by the
panel (`J_PANEL` 18 to 20, board C `U3` GPIO10 to 12). A dark module leaves the line HIGH through the pull-up, the same
level as a live module holding GPIO16 high, so **liveness is the toggle**, which is what `PANEL.md` section 3 states
("a slot toggles its line at 1 Hz"). The same stage type on `PI_KILL` and `PI_SHDN_REQ` is round-6 O-21.

**The two CAN fabrics** (heartbeat and quorum between the supervisors):

| Fabric | Controller pins | West end (controller A) | Break link | Controllers B and C | Termination | Test pads |
|---|---|---|---|---|---|---|
| A | FDCAN1: PD0 (81) RX, PD1 (82) TX | U43 on `CANH_A1/CANL_A1` | R508/R509 0 Ohm | U53, U63 on `CANH_A/CANL_A` | west R470 + R471 60.4 Ohm, C460 4.7 nF; east R504 + R505, C506 | TP535, TP536 |
| B | FDCAN2: PB12 (51) RX, PB13 (52) TX | U44 on `CANH_B1/CANL_B1` | R511/R512 | U54, U64 | west R472 + R473, C461; east R506 + R507, C507 | TP537, TP538 |

Transceiver pins: 1 `TXD`, 4 `RXD`, 3 `VCC` on the controller's private rail, 2 GND, 6/7 `CANL/CANH`; pin 5 is left
open and pin 8 is tied to GND (FAB-06). The alternate functions are VERIFIED in [MCU] Table 11 (Port B, PDF p.90:
`PB12` "FDCAN2_RX", `PB13` "FDCAN2_TX"; p.89: `PB6` "I2C1_SCL", `PB7` "I2C1_SDA") and Table 13 (Port D, PDF p.92: `PD0`
"FDCAN1_RX", `PD1` "FDCAN1_TX"); B21's H753 has the same AF9 and AF4 entries in [MCU-53] Tables 10 and 12 on the same
pages. A
split termination at both physical ends is the arrangement the generator records (`main :847-849`: "Each fabric is
terminated at BOTH physical ends"); the
break links and pads are round 6's SD-B-09 (B21 has the same terminations without them). The CAN pairs are not in a
controlled-impedance class, by the ruling in IOHA section 6.

**Kit I2C.** The supervisors' `PB6` (92) `I2C1_SCL` and `PB7` (93) `I2C1_SDA` join the kit bus (R54/R55 2.2 kOhm to
`+3V3_DEV`), mastered by the panel RP2040 (board C GPIO0/1). On B21 both pins are unconnected (W5-F3). The intended
supervisor address 0x30 collides with the TPS23861's broadcast address (I3-F01, `ARCHITECTURE.md` section 5.5).

## 5. Power states: what the fabric drives into a module that is off

### 5.1 The domains

| Domain | Rail | Source and enable | Fabric parts on it |
|---|---|---|---|
| always-on | `+5V_DEV` | board A over `J_5V_DEV`; A's `DEV_EN`: 100 kOhm to GND on A23 (`main`), 100 kOhm to `+3V3` in A's round-6 candidate | U25 (`+3V3_DEV`), the three hub cores U{s}06, the supervisors' LDOs U40/U50/U60, F2 (`+5V_HDMI`), the hubs' `USB_VBUS` dividers |
| always-on | `+3V3_DEV` | U25 AP63203 on B | hubs' `VDD33`, all six host-select muxes, the voters U70 to U80, both TS3DV642, the HB and kit I2C pull-ups |
| supervisor | `+3V3_IOCA/B/C` | U40/U50/U60, EN 100 kOhm to `+5V_DEV` (R66/R78/R90), bench jumper `J_IOCOFF_x` | one controller and its two transceivers |
| slot | `+5V_S{s}` | board A over `J_5V_S{s}`, enabled by `SLOT_EN{s}` (panel GPIO13 to 15, through B to A; A holds 100 kOhm to GND) | the module |
| slot fabric | `+3V3_S{s}B`, `+1V0_S{s}` | U{s}04, U{s}05 from `+5V_S{s}`, enable `EN33_S{s}` = module 3.3 V through R{s}11/R{s}12 100k/100k | the switch, the NVMe socket, the WAKE pull-up |
| slot card | `+3V3_S{s}A` | U{s}03; slots 1, 3 on `PCIE_PWR_EN` and EMCON (Q{s}11), slot 2 on `PCIE_PWR_EN2` alone | the card socket |

So the PCIe switch is off whenever its module is off (the upstream pins then face an unpowered part through capacitors
or a dead clock), while the hubs, muxes, display switches and voters are always on. That is the design intent
(a bank must outlive its module), and it is what creates FAB-02.

### 5.2 The paths that reach an unpowered module (FAB-02)

[CM5] 3.1, PDF p.16: "No pins should be powered before the 5 V rail is active." [CM5] 4.2.1, PDF p.24: "when CM5 is
powered-down or off, there must be no external voltage applied to any pin, otherwise CM5 might not power up again."

| Path | When | Mechanism | Evidence |
|---|---|---|---|
| USB 2.0 D+ of the selected host | every bank at kit power-up (slots come up after `+5V_DEV`, by the panel's `SLOT_EN`); any bank whose selected host is off (a slot turned off, the one-module reduced mode of D-02b, a module lost before quorum moves its bank, two supervisors dark) | the hub is a USB device on its upstream port; with `USB_VBUS` fed from `+5V_DEV` it always sees upstream power, and a full-speed or high-speed device signals attach with a pull-up on D+ to about 3.3 V, which the TS3USB221A (on, `OEn` low at rest) passes to the module's `USB3-x-DP` pin | netlist VERIFIED (R{b}43 to `+5V_DEV`, U{b}10 `OEn` low at rest); the attach pull-up is USB 2.0 device behaviour (USB 2.0 specification 7.1.5, not held: INFERRED) and [HUB] describes `USB_VBUS` as the "upstream port power monitor" (PDF p.5) |
| HDMI0 DDC of the selected slot | at power-up (both selects default to slot 1, which is off until `SLOT_EN1`); whenever the displayed module is off | R17/R18 2.2 kOhm to `+5V_HDMI` (always on through F2) reach the selected module's `SDA/SCL` through two TS3DV642 (enabled at rest); the module's internal 1.8 kOhm pull-ups lead into an unpowered rail | netlist VERIFIED; the current, roughly 1 mA per line, is INFERRED (5 V over 2.2 k plus 1.8 k, less the switch's own drop, not published for the DDC channels) |
| HDMI0 HOTPLUG | a monitor that drives HPD from its 5 V while the selected module is off | about 3 V from the R19/R20 divider through the switches into `HDMI0_HOTPLUG` (100 kOhm internal pull-down) | netlist VERIFIED; the pin is "5 V tolerant" ([CM5] PDF p.23), which is a statement about a powered module |
| SuperSpeed pairs | never with DC | the module's transmit pins are coupled on the module; its receive pins meet C{b}59/60 on the far side of the mux; the mux's own bias is 1 MOhm and 20 kOhm to GND ([MUX] 8.3.2) | VERIFIED: no DC source |
| Ethernet | whenever a slot is off and its KSZ port is enabled | link pulses through 100 nF into the unpowered PHY's pins (AC only) | INFERRED small; the port can be powered down by management (firmware contract) |

Effect: Raspberry Pi says the module "might not power up again". The magnitudes are small (milliamps at most,
INFERRED) and no document in this tree gives a tolerated injection, so the size of the risk is TBD; the condition is
not rare, it is every boot. Remedies are in FAB-02.

### 5.3 The reference clock across power states

The switch's `REFCLKI` receives the module's clock DC-coupled, and the whole slot runs on it (common clock). What [SW]
publishes: `REFCLKI`/`REFCLKO` swing, crossing and duty (Table 8-1, PDF p.75) and, for `REFCLKP/N`, accuracy of
+-300 ppm, jitter limits and spread spectrum of 30 to 33 kHz (Table 8-2, PDF pp.75-76). What is not published: the
module's clock output standard, swing and whether it spreads ([CM5]); the buffer's additive jitter (Table 8-1 gives
none). So the endpoints' clock quality is TBD, and closes only by measurement at the sockets or a statement from the
makers.

## 6. Cross-board contracts the fabric depends on

Pin identity was compared pin by pin on `J_AB1` (26 pins), `J_AB2` (10), `J_PANEL` (26), `J_5V_S1..3` and `J_5V_DEV`
across the B candidate, B21, A23, A's round-6 candidate and C24: **every pin carries the same net name at both ends**
(VERIFIED; `J_PANEL` pins 1/2 are `PANEL_5V` on B and `+5V` on C, the same conductor). The semantics are the contracts:

| Contract | Ends | What the fabric needs | State |
|---|---|---|---|
| Slot power | A `J_5V_S1..3` (A's slot converters, enabled by `SLOT_EN1..3`, 100 kOhm to GND on A) to B | each slot's module and its PCIe domain | pins match; `+5V_S2` current: B declares 4.2 A typical, 5.63 A coincident peak, A declares less (round-6 I-03, open) |
| Device rail | A `J_5V_DEV` to B | the whole always-on fabric; a failure is FMEA row 11's common mode | `DEV_EN` defaults OFF on A23 (R42 to GND, finding A01) and ON in A's round-6 candidate (R42 to `+3V3`, I-12); current per I-07 |
| Slot enables | C RP2040 GPIO13 to 15 over `J_PANEL` 21 to 23, through B, over `J_AB1` 17 to 19 to A | the only way a module powers; the panel is a whole-compute dependency (IOHA section 10) | pins match; firmware boot order in `PANEL.md` section 5 |
| Heartbeats | B `HB1..3` to C GPIO10 to 12 and the three supervisors | module liveness as a 1 Hz toggle | pins match; contract in `PANEL.md` section 3 |
| Display selects | C GPIO16/17 over `J_PANEL` 12/13 to U3/U4 `SEL2` | which module drives the monitor; "the lowest slot with a live heartbeat" by default (`PANEL.md` section 5) | pins match; FAB-02 and FAB-04 |
| Panel USB | B bank 1 hub port 2 over `J_PANEL` 15/16 to C's RP2040 | the cluster's view of the panel and of the supervisors' status | pins match; the panel follows bank 1 on failover |
| Kit I2C | C master, B supervisors as targets, A and B devices | supervisor status; secure element; switch management | pins match; I3-F01 address collision open |
| Safety lines through B | `PI_KILL`, `PI_SHDN_REQ`, `EMCON_HW`, `ZEROIZE_HW`, `SHORE_INHIBIT`, `TX_INHIBIT_n` over `J_PANEL` and `J_AB1` | not fabric payload, but the level stages on `PI_KILL`/`PI_SHDN_REQ` are the fabric's module interface | round-6 O-21 (the stages can lift `PI_KILL`), A's I-02 recommends a unidirectional buffer |
| Bank 3 peripherals on other boards | bank 3 ports 1, 2 over `J_AB1` 1/2 and 25/26 (`USB_D8`, `USB_E6`); port 3 over `J_AB2` 1/2 (`USB_WALL`) | the APRS board, the sensor controller and the sealed wall port follow bank 3 | pins match |
| Firmware | the bridge on each module, the three supervisors, the panel | GPIO16 toggle; never force Ethernet speed on ports 1 to 3 (decision 29); FDCAN at or below 1 Mbps (FAB-05); the failover sequence of IOHA section 7; PC5 input only (round-6 O-06) | none of this firmware exists |

## 7. What is validated, by what, and what is not

| Item | Validated by | State |
|---|---|---|
| Connectivity, direction and polarity of every fabric lane | `fabmap.py` against datasheet-derived far ends: 202 of 202 OK on the candidate; round-6 gate emulation of `check_pcb_b.py` (sha256 `28904a37...`) on the same netlist: 170 checks, 0 FAIL (`v2/docs/records/r4b/box/r6-run6/check_pcb_b/emul-r6-gate-on-round6.txt`, RECORDED) | VERIFIED on the candidate; B21 on `main` fails 28 rows |
| AC coupling location and values | netlist plus [CM5], [5G], [HUB], [MUX], [SW], [KSZ] clauses (section 4) | VERIFIED; placement "close to the driving source" is a layout instruction, owed (round-6 O-02) |
| Clock termination and coupling | netlist plus [SW] Table 8-1 note 1 and 3.1 | VERIFIED |
| Switch straps | netlist plus [SW] 3.2 to 3.4 | VERIFIED, with FAB-01 wrong |
| Voter logic | `voters.py`, 7 of 7 majorities, both netlists | VERIFIED |
| Supervisor alternate functions | [MCU] Tables 11, 13 and [MCU-53] Tables 10, 12; pin identity 100 of 100 on both H743 and H753 (round-6 `v2/docs/records/r4b/pin_parity.py`, RECORDED) | VERIFIED |
| Crystals (hubs, KSZ, supervisors) | `clock_check` PASS of 7 on the round-6 regeneration (`v2/docs/records/r4b/box/r6-run6/run.log`, RECORDED) | RECORDED |
| Safe states with a dark control plane | netlist: home selected, muxes enabled, hubs out of reset, primary WiFi card; `pulldowns.py` on the 23 safe-low lines (R480 to R500, R15, R16) at datasheet leakage | VERIFIED as intent; not guaranteed at datasheet leakage, 23 of 23 lines above `VIL` on both netlists (FAB-04) |
| Break-before-make | netlist; [U2M] 5.8, [MUX] 6.7, [XOR-TI], [XOR-NX] | the ordering is not break-before-make (FAB-03) |
| Power-state behaviour | netlist against [CM5] 3.1 and 4.2.1 | fails (FAB-02) |
| Impedance of any fabric pair | nothing: IMP-001 is SOURCE_UNVERIFIED; inner-layer pairs on the six-layer stack solve to 140.5 Ohm against 100 (`B-FEASIBILITY.md` 3.2, RECORDED) | UNVALIDATED |
| Loss and eye at routed length | nothing: no routed candidate; no USB 3.x, PCIe CEM or HDMI channel budget document is held; lengths are a placement screen only (section 8.3) | UNVALIDATED |
| Reference clock jitter at the endpoints | nothing (section 5.3) | UNVALIDATED |
| Escape strategy | `place_audit` PLC-001 FAIL, about 10 collisions of 75 fine-pitch parts; B21 stopped at 416 open (RECORDED) | UNVALIDATED (section 8) |
| IOHA acceptance tests A1 to A14 | nothing built | NOT_YET_TESTED |

## 8. Board B's escape strategy: status

### 8.1 What `B-FEASIBILITY.md` establishes (pending merge, sha256 `5a46e459...`)

- **Not shown to be physically impossible, and not shown to be possible.** Three causes are tangled: a floor plan
  that sends each slot's high-speed traffic 85 to 90 mm beyond the M.2 row and back, with switch pockets at 0.0 mm of
  room on at least three sides; an escape method with one pattern (a surface stub to a through via outside the pad,
  fixed via sizes, no via-in-pad for signal pads), independent of layer count; and a six-layer stack with two of its four
  routing layers usable for controlled-impedance pairs (its sections 1 and 3).
- **Where it fails:** U101 38 of 99 and U301 34 of 99 pads without an escape, the three hubs 14 to 21, the slot 2
  SuperSpeed mux 15 of 21 (its 3.1, VERIFIED on the B21 pre-route board); PLC-001 reads 10 with the board's declared
  `ESCAPE_SKIP`.
- **Options** A1 (eight layers, decision 43), A2 (six layers re-assigned, In3 a plane), A3 (via-in-pad escapes, the
  fabricator's default process from six layers), A4 (floor plan: fabric beside each receptacle's B half), A5
  (partition method), A6 (larger outline, bounded by the 1450 frame window), A7 (pin mapping using the allowed P/N
  swaps), A8 (feature reductions, excluded by the owner's D-01 except 5G to USB 3) (its section 5).
- **Recommended order:** fix the schematic first; run Q-B-ESC-1; study A4 with A2 and A7 on paper; run decision 43's
  eight-layer whole-board experiment under its own caps, labelled EXPERIMENTAL; send (through the owner's ordering
  session) the via-in-pad questions to JLCPCB (its section 6).

### 8.2 The bounded trial Q-B-ESC-1 (specification; box-ready; **not run**)

- **Question:** in slot 3's pocket (U301, U302, U309, U310, U32A/U32B, J_M2N3, J_M2C3), is the failure to break out a
  layer-capacity limit that two more routing layers remove, or a geometric limit that layer count does not change?
- **Arms:** A6, the B21 pre-route board as is (sha256 `62facf09...`); A8, the same board with its copper layer count set
  to 8 in the trial tree only (more routing than any real eight-layer B). One job per arm (the router is
  deterministic).
- **Caps:** 20 passes, 9,000 s per job, a plateau of three observed sessions without a new minimum, 90 min to a first
  pass, and the smaller of 6 box-hours and 10 USD for the whole trial; about 3.5 box-hours and 4 USD expected.
- **Decisive number:** the S3 open count from `pcbnew` connectivity (pass 0: 290 on both arms, smoke test of 25 Sep
  2026 22:03 UTC at `82dd1e4d`, prepare-only; RECORDED in `B-FEASIBILITY.md` 7.6).
- **Outcomes:** REGION-CLOSES-ON-6, LAYERS-HELP, LAYERS-PARTIAL, LAYERS-NOT-THE-LEVER, INCONCLUSIVE, each with its
  stated meaning; none authorises layout.
- **Stated limits:** it routes the B21 netlist with its defects; only group S3 is routed; one sample per arm; sessions
  can be missed; A8 is generous.

**This review adds to limit 1** (FAB-08): the corrected slot 3 does not add six capacitors to the pocket, it adds
eighteen parts at the switch (C353 to C356, C395, C396 and the twelve clock resistors R375 to R386, all seated "beside
U{s}01" by round-6 O-02) and fourteen more elsewhere in the slot block (U311, Q309 to Q311, R362 to R365, R373, R374,
C397, TP301 to TP303), 32 in all against B21 (VERIFIED by netlist difference: 173 parts added, one removed, R240). A
reading of the trial on the B21 board is therefore more optimistic than its page says, and a REGION-CLOSES-ON-6
reading would be weaker still.

### 8.3 A placement screen of the fabric's long runs (INFERRED; not lengths)

Manhattan distance between footprint origins on the B21 pre-route board (`lengths.py`); pads, escapes and detours are
not in it, so a routed run is usually longer. It says which runs need a channel budget.

| Run | Screen | Limit held in the tree |
|---|---|---|
| PCIe upstream, receptacle to switch | 117.6 / 140.0 / 129.0 mm (slots 1/2/3) | none published ([CM5] gives impedance and matching only) |
| switch to NVMe; switch to card | 53.9 / 44.5 / 57.7; 81.1 / 70.7 / 88.5 mm | RM520N: "maximum trace length no more than 200 mm" ([5G] 4.3.3, PDF p.48), met by slot 2's 70.7 mm screen |
| USB home: receptacle, mux, hub | 185.2 / 117.9 / 196.6 mm | none held |
| USB failover: receptacle (USB3-1), neighbour's mux, hub | slot 1 to bank 3: 241.6; slot 2 to bank 1: 255.2; slot 3 to bank 2: 187.9 mm, plus the mux's insertion loss (-1.3 dB at 5 GHz, [MUX] p.1) | none held (a USB 3.x channel budget is owed) |
| HDMI: receptacle to `J_HDMI` through the switches | 396.2 / 326.2 / 256.2 mm, through two or one TS3DV642 (insertion loss at DC -0.75 dB port A, -1.0 dB port B, [HDS] p.1) | none held |
| LimeSDR: bank 1 hub to `J_LIME` | 217.0 mm | none held |
| Ethernet: receptacle to U1 | 92.8 / 162.8 / 232.8 mm | [CM5] 2.2.1: pair-to-pair matching "not required if differences are less than 50 mm" |

The longest SuperSpeed path is slot 2's failover edge into bank 1, not the slot 1 to bank 3 edge the feasibility page
names; both cross a module column.

## 9. Findings of this review

Each finding names who changes what. Decisions are **taken by the session under the owner's standing rule of
26 Sep 2026**; none is applied here, because `gen_sch_b.py` and `check_pcb_b.py` belong to the board B author.

**FAB-01 (major; all three PCIe switches; `main` and candidate). `TEST2` is pulled low.** `gen_sch_b.py:525`
(candidate; `:431` on `main`) puts pin 16 `TEST2` on `S{s}_TESTL` with `TEST3`, `TEST4`, `TEST5`, `TEST6` and `VC1_EN`,
and `:568` (`:445`) pulls that net to GND through R{s}24 330 Ohm. [SW] 3.3, PDF p.14: "Test2: The pin is for internal
test purpose. Test2 should be tied to 3.3V through a 5.1K-ohm pull-up resistor." Effect: the switch's behaviour with a
test pin in the wrong state is not documented (TBD), which on a board whose three switches carry every PCIe device is a
risk to the whole PCIe side of the fabric. Also `TCK` (89) and `TDI` (93) sit on the 330 Ohm pull-down where 3.4 says
"should be left open (NC)"; the effect is INFERRED small (a static low on an idle TAP), the fix is free. **Taken:** pin
16 to its own 5.1 kOhm pull-up to `+3V3_S{s}B` (one resistor per slot, the value `TEST1` already uses), pins 89 and 93
to no connection; and `check_pcb_b.py` gains an assertion of [SW] 3.2 to 3.4's strap table for every strap
pin, with a mutation that pulls `TEST2` low. Owner: board B author. No placement effect beyond one resistor per switch.

**FAB-02 (major; core function; `main` and candidate). The always-on fabric powers pins of modules that are off.**
Section 5.2. **Options:** (a) derive each hub's `USB_VBUS` divider from the selected host's slot 5 V through a small
2:1 analog switch on `BSEL{b}`, so the hub detaches from a dark host (this recreates IOHA section 5's fourth
mechanism, the USB4715's auto-revert, on the TUSB8041; INFERRED from device attach behaviour, owed a TI confirmation);
(b) qualify each bank's `OEn` with the selected host's power: `BOE{b}_n` becomes the break-before-make pulse OR NOT
(power-good of the selected slot), the power-good taken from `+3V3_CM{s}` into an LVC input on `+3V3_DEV` (such an
input draws at most +-5 uA, [AND] 5.7, and "Inputs accept voltages to 5.5V", [AND] p.1; with `+3V3_DEV` down the gate
has no published Ioff, round-6 O-24, but then the whole fabric is dark), selected by a 2:1 logic mux on `BSEL{b}`;
this disconnects the USB 2.0 path and the SuperSpeed path together; (c) qualify the display switches' `EN` with the
displayed slot's power-good the same way, which also removes the power-up case; (d) keep the circuit and obtain
Raspberry Pi's written tolerance for the currents of section 5.2 (question drafted in Appendix B, not sent). **Taken:** (b) and (c), in the same change as FAB-03's rework (they share the enable network), because they
remove the condition in every state without depending on a maker's answer or on firmware; (d)'s question is kept as a
parallel route. Owner: board B author; the panel firmware's display rule stays as `PANEL.md` section 5 states it.

**FAB-03 (major; core, IOHA A10; `main` and candidate). The break-before-make makes before it breaks, and its RC edge
violates the XOR's input rule.** The voted `BSEL{b}` drives the muxes' `SEL`/`S` directly; `BOE{b}_n` rises one XOR
delay later (at most 4.6 ns, [XOR-TI] p.1). [U2M] 5.8, PDF p.6 gives `S` to output enable at most 30 ns and disable at
most 12 ns, `OE` disable at most 10 ns, and no minimum and no break-before-make between ports 1 and 2; [MUX] 6.7, PDF
p.6 gives `SEL` switching at most 100 ns (5 us with a common-mode shift) and publishes no `OEn` timing. So nothing in
the documents guarantees that the old path is off before the new one conducts, while IOHA section 5 describes the
opposite order ("The voted OE is de-asserted, a delay elapses, the voted SEL changes") and test A10 passes only if "the
enable is low for the whole select transition, with no overlap". Separately, `BSEL{b}_D` reaches the XOR through a
100 us RC: [XOR-TI] 5.4 (PDF p.5) limits the input transition rate to 9 ns/V and [XOR-NX] Table 5 (PDF p.3) to
10 ns/V at 2.7 to 3.6 V, so the XOR output may chatter as the delayed copy crosses its threshold (the same class as
round-6 O-23). And the schematic's value "74LVC86APW" is Nexperia's type number while its order code C350562 resolves to
TI's SN74LVC86APWR (`JLC-CERTIFIED.tsv:304`), a component mismatch under owner condition 1 (same function and pinout
per both datasheets, VERIFIED). **Taken:** a true sequence in hardware: `SEL` from a Schmitt-buffered first delay
(74LVC1G17, as board C's U9), `OEn` from the XOR of `BSEL{b}` and a Schmitt-buffered second, longer delay, so the enable
drops within a gate delay of the vote, the select moves tens of microseconds later and the enable returns later still,
with margins far above [U2M]'s and [MUX]'s switching times; the value text aligned to the ordered part. Rejected:
rewriting A10 to fit the circuit, because no document bounds the overlap. Owner: board B author; `ARCH-PCB-B-IOHA.md`
section 5 then describes the circuit (integrator).

**FAB-04 (major; `main` and candidate). Safe-state pull-downs do not hold a guaranteed low.** Each of the **21
controller outputs**, seven voted bits times three controllers (`SEL1_A/B/C`, `SEL2_A/B/C`, `SEL3_A/B/C`,
`HUBRST1_A/B/C`, `HUBRST2_A/B/C`, `HUBRST3_A/B/C`, `WSEC_A/B/C`), has its own 100 kOhm to GND, **R480 to R500**
(`gen_sch_b.py:1229-1232` in the candidate, `main :904-907`: one loop, one value literal), and feeds two SN74LVC08A
inputs (section 4.9; VERIFIED on both netlists, 21 of 21 at 100k, `out/pulldowns.txt`). [AND] 5.7, PDF p.7: `II`
+-5 uA at -40 to +85 C (+-1 uA at 25 C); [AND] 5.4, PDF p.6: `VIL` 0.8 V at VCC 2.7 to 3.6 V. The controller's own
pin, powered and in reset: [MCU] Table 60, PDF p.138 ([MCU-53] Table 59, same page) gives `Ilkg` +-250 nA for FT_xx and
TT_xx at 0 < VIN <= Max(VDDXXX), and its note 4 reads "This parameter represents the pad leakage of the I/O itself. The
total product pad leakage is provided by the following formula: ITotal_Ikg_max = 10 uA + [number of I/Os where VIN
is applied on the pad] x Ilkg(Max)". The pins are, [MCU] Table 9 ([MCU-53] Table 8), PDF pp.68, 69, 71, LQFP100 pins
22 to 25, 28, 29 and 37: `PA0` FT_a, `PA1` FT_ha, `PA2` FT_a, `PA3` FT_ha, `PA4` TT_a, `PA5` TT_ha, `PE7` TT_ha, so
every one is an FT_xx or TT_xx pin at +-250 nA. ST does not say which pad carries the 10 uA product term. **Taken
(session, under the owner's standing rule of 26 Sep 2026):** the bounding reading, all 10 uA on the one supervisor
pin each line carries, 10.25 uA per pin; it is the reading round 6 used for R58 (O-08, "a 10 uA product-level term
per device"). Rejected: the pad term alone (0.25 uA), because nothing in the datasheet bounds how the product term
divides between pads. Two inputs at 5 uA plus 10.25 uA give 20.25 uA, which through 100 kOhm is 2.025 V, above
`VIL` (with the pad term alone it would be 10.25 uA and 1.025 V, also above `VIL`), before any leakage from an
unpowered STM32 pin (unspecified below VDD = 0, the round-6 O-16 caveat). So "a controller that is absent, unpowered
or in reset is read as a definite no" (IOHA section 10a) holds at typical leakage and not at the datasheet's limit, on
all 21 lines. FMEA rows 4 and 20 and tests A4, A6 and A12 rest on it, and so does the dark-plane default of the WiFi changeover: `WIFI_SEC` low (the primary card) needs R498 to R500 on `WSEC_A/B/C` to
hold as firmly as the bank selects. The same arithmetic applies to `HDMI_SEL1/2`: 100 kOhm (R15, R16) against the
TS3DV642's `IIL` of +-10 uA ([HDS] 6.5, PDF p.7) gives 1.0 V against its `VIL` of 0.5 V, so with the panel absent the
display's default is not guaranteed; TI's own HDMI design uses 10 kOhm on the selects ([HDS] Table 4, PDF p.21). This is
round 6's SD-B-21 (R58 from 100 kOhm to 10 kOhm) on **23 more nets: the 21 controller outputs and `HDMI_SEL1/2`**.
**Taken:** 10 kOhm on all 23: R480 to R500 (the value literal of the loop at candidate `:1232`, `main :907`) and R15, R16
(candidate `:903`, `main :658`). At 10 kOhm the controller lines sit at 0.2025 V against 0.8 V, leaving about 60 uA
(80 uA less 20.25 uA) for an unpowered controller's pin, and the display selects at 0.10 V against 0.5 V, leaving
40 uA (`out/pulldowns.txt`, column V@10k, printed to three places). Cost: 0.33 mA per output while driven high, at most 2.3 mA per controller with all seven high, from its own AP2112K
rail. **Check:** the candidate's `check_pcb_b.py:381-388` (sha256 `28904a37...`) asks only that some resistor sit on
each controller output, so a 100 kOhm, or any value, passes. It gains the assertion SD-B-21 used, with its designators
enumerated from the generator's rule rather than discovered from the nets found: for bit j of `CTRL_BITS` and
controller i, R(480 + 3j + i), that is **R480 to R500**, exists, joins exactly `<bit>_<controller>` and GND, is the
only resistor on that net, and its value times the net's summed datasheet leakage (read from the loads the netlist
puts on it: 5 uA per SN74LVC08A input, 10.25 uA for the supervisor's pin, note 4's product term included) is
below 0.8 V; the same for R15 on `HDMI_SEL1` and R16 on `HDMI_SEL2` at 10 uA against 0.5 V. So `WSEC_A/B/C`, or any other of the 21, cannot drop out by
a rename, a deletion or a value left at 100 kOhm. Its mutations: R500 (`WSEC_C`) back to 100 kOhm, and R498 (`WSEC_A`)
under another designator, each expected to FAIL. The session's reading of this rule, `pulldowns.py`, gives 23 FAIL of
23 on both netlists as generated, FAIL 0 with the 23 values at 10 kOhm, and FAIL 1 on each mutation
(`out/pulldowns-mutations.txt`); it is a draft, not the repository check. Owner: board B author.

**FAB-05 (minor; contract and documents). The CAN transceiver is a 1 Mbps part.** The fitted TCAN334DR ([CAN] Device
Options, PDF p.3: "TCAN334 ... 1 Mbps", "TCAN334G ... 5 Mbps"; description, PDF p.1: "TCAN330, TCAN332, TCAN334 and TCAN337
are specified for data rates up to 1Mbps") against the generator's comment "CAN FD to 5 Mbps" (candidate `:1160`,
`main :843`) and IOHA section 6's "at 5 Mbps the bus is electrically short". `v2/vendor/SOURCES.yaml`'s note that
"the G variants (TCAN334G) are a different pin function" is contradicted by the same table (both: pin 5 `SHDN`, pin 8
`STB`). **Taken:** keep the TCAN334D and make "nominal and data bit rate at most 1 Mbps" a supervisor firmware
contract; heartbeat traffic needs far less, and IOHA's reason for leaving the CAN pairs out of an impedance class holds
more strongly at 1 Mbps. The document corrections are the integrator's (IOHA section 6, `SOURCES.yaml`, the generator
comment). A part change to TCAN334GDR (same pins) is the option if a faster data phase is ever wanted.

**FAB-06 (minor; symbol). The transceiver's symbol names pin 5 "NC" and pin 8 "GND".** [CAN] Table 4-1, PDF p.4:
pin 5 `SHDN` ("Drive high for shutdown mode. Internal pull-down"), pin 8 `STB` ("Drive high for low power standby
mode, integrated pull down"). Electrically the part is in normal mode (STB grounded, SHDN held low inside). **Taken:**
name the pins as the datasheet does and tie `SHDN` to GND on the board rather than rely on the internal pull-down.
Owner: board B author.

**FAB-07 (evidence gap). No primary document for the M.2 key E pinout.** Section 4.4. **Taken:** ask AsiaRF for the
AW7915-AED's pin assignment (text in Appendix B, not sent); until it is filed, the key E rows are
secondary-source readings.

**FAB-08 (placement). 18 parts per switch pocket to seat.** Section 8.2. The pockets had 0.0 mm of room on B23
(RECORDED). The HCSL rule is to place Rs and Rp at the source and the capacitors near the transmitter ([SW] Table 8-1
note 1; [5G] 4.3.3), so moving them away is not free. Owner: the placement owner (round-6 O-02), with the escape
strategy (section 8).

**Documentation items (integrator):** IOHA section 5 item 2 says the output enables "pull to disconnected" with the
plane dark, while the netlist pulls `BOE{b}_n` low (enabled), and FMEA rows 4 and 20 and test A12 describe the
netlist's behaviour; IOHA section 5 item 4 (the USB4715's auto-revert) is not present in the design, whose hubs are
TUSB8041 with `USB_VBUS` on `+5V_DEV`; IOHA section 5 item 3 describes an ordering the circuit does not have (FAB-03);
the "5 Mbps" text (FAB-05); IOHA's "Six voters" and "Every one of the eighteen controller outputs carries a
pull-down" (`ARCH-PCB-B-IOHA.md:175` and `:178` at `1f614233`; the same text in the pending copies,
`scratchpad/wt/i3/v2/docs/ARCH-PCB-B-IOHA.md:175/:178` and `scratchpad/wt/i1/v2/docs/ARCH-PCB-B-IOHA.md:163/:166`),
which predates `WIFI_SEC`: the netlists carry seven voters and 21 controller outputs (section 4.9).

## 10. The fabric's feasibility blockers, and the evidence that closes each

| Id | Blocker | Closing evidence | Owner | State |
|---|---|---|---|---|
| FB-FAB-1 | The corrected fabric netlist (W3-F01, W3-F02, W3-F03, W5-F3, S-13 and round 6) is not on `main` | integration commit O-18 with regeneration parity on `main`, then this page's `fabmap.py` and `check_pcb_b.py` rerun on the committed netlist: 0 MISMATCH, 0 FAIL | integrator | OPEN; the evidence exists for the candidate (sections 4, 7) |
| FB-FAB-2 | `TEST2` strap (FAB-01) | regenerated netlist with pin 16 on 5.1 kOhm to `+3V3_S{s}B` and 89/93 open; the strap assertion in `check_pcb_b.py` and its mutation | board B author | OPEN |
| FB-FAB-3 | Back-power of unpowered modules (FAB-02) | the gate network of FAB-02 (b)/(c) in the netlist, and a power-state check over the netlist that finds no fabric net able to source current into a slot whose `+3V3_CM{s}` is absent; or Raspberry Pi's written tolerance for the currents of section 5.2 | board B author; owner's outreach session for the question | OPEN |
| FB-FAB-4 | Break-before-make ordering and edge rate (FAB-03) | the two-delay Schmitt sequence in the netlist, a timing budget against [U2M] 5.8 and [MUX] 6.7, then A10 on the bench | board B author | OPEN |
| FB-FAB-5 | Dark-plane and panel-absent safe states (FAB-04) | a regenerated netlist with 10 kOhm on all 23 safe-low lines, **R480 to R500** (the 21 controller outputs `SEL1..3_A/B/C`, `HUBRST1..3_A/B/C`, `WSEC_A/B/C`) and R15, R16 (`HDMI_SEL1/2`); the leakage-bound assertion in `check_pcb_b.py` that enumerates those 23 designators, with its mutations (R500 at 100 kOhm, R498 renamed) failing; then A6 and A12 on the bench | board B author | OPEN |
| FB-FAB-6 | Escape and placement: 54 new parts in three full pockets; PLC-001 FAIL; no complete route | Q-B-ESC-1's reading (EXPERIMENTAL), the paper floor-plan study of A4 with A2 and A7, a placement that seats every part with `region_room` read, and decision 43's whole-board run; none of these authorises layout | board B author; integrator for the run order | OPEN; nothing run |
| FB-FAB-7 | Signal integrity at routed length: impedance, loss, the longest USB 3 edges (up to about 255 mm by the screen plus a mux), HDMI up to about 400 mm through two switches | a channel budget per link from a primary document (USB 3.x, PCIe CEM, HDMI, or the makers' layout guides), routed-length extraction from a placed and routed candidate, a field-solver impedance on the chosen stack, and the fabricator's impedance record; then IOHA A13 and link training on the bench | board B author; the qualified high-speed review the 26 September review asks to be named | OPEN |
| FB-FAB-8 | Reference clock quality at the endpoints | Raspberry Pi's statement of the clock output (standard, swing, spread spectrum) and a bench measurement at each socket with the switch's buffer in the path; all six downstream links training at Gen 2 | bring-up; Raspberry Pi question drafted | OPEN |

Contract items that do not block the fabric but must be carried: FDCAN at or below 1 Mbps (FAB-05); the 1 Hz heartbeat
toggle; auto-negotiation on KSZ ports 1 to 3 (decision 29); a KSZ port powered down while its slot is off (section
5.2); the key E pin table (FAB-07); the symbol names (FAB-06); round-6 O-06, O-14, O-21 and O-23 on the same circuits.

## 11. What this page does not claim

- It does not claim the fabric works, that board B is feasible or infeasible, or that any board is ready for layout.
- It reads netlists and documents. No copper, no simulation and no hardware stand behind any row.
- The candidate netlist is an uncommitted round-6 artefact; if the netlist `main` commits does not have sha256
  `af8a9186...`, the map must be re-read (the scripts take the netlist as their argument).
- The placement screen is a distance between footprint origins on the B21 board, not a length.
- The fetched TI and Nexperia datasheets are read on the date given; the Raspberry Pi, TI and AsiaRF questions are
  drafts, sent by nobody.

## Appendix A. Every fabric pin, candidate and B21

Generated by `render.py` from `fabmap.json` (both in `v2/docs/feasibility/fab/`, written in worktree `fnd/rv-fab`), on the candidate netlist
sha256 `af8a9186...` and the B21 netlist sha256 `0e72edb5...`. Columns: the start pin; the candidate's net; the series
parts crossed to the far end ("direct" when none); the far-end pins; the shunt parts on the start net; "Check" is OK
when the far end is the pin the documents call for (section 4 gives the clause) and n/a where no far end is expected;
"B21 (main)" is "same" when the committed netlist agrees in net, path and shunts, otherwise it shows B21's path, in bold
when B21 misses the expected far end. The supervisor pins and the CAN fabrics are tabulated in section 4.9, because a
series walk through a split termination does not describe a bus.

<!-- generated by render.py from fabmap.json; candidate af8a9186f981210c, B21 0e72edb5d755316f -->
### A.1 PCIe upstream

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | PCIe TX+ (module transmit) | U30B.122 PCIe_TX_P | PCIE1_TX_P | direct | U101.128 PERP0 | - | OK | same |
| 1 | PCIe TX- | U30B.124 PCIe_TX_N | PCIE1_TX_N | direct | U101.127 PERN0 | - | OK | same |
| 1 | PCIe RX+ (module receive) | U30B.116 PCIe_RX_P | PCIE1_RX_P | C151 220n 16V | U101.124 PETP0 | - | OK | same |
| 1 | PCIe RX- | U30B.118 PCIe_RX_N | PCIE1_RX_N | C152 220n 16V | U101.123 PETN0 | - | OK | same |
| 2 | PCIe TX+ (module transmit) | U31B.122 PCIe_TX_P | PCIE2_TX_P | direct | U201.128 PERP0 | - | OK | same |
| 2 | PCIe TX- | U31B.124 PCIe_TX_N | PCIE2_TX_N | direct | U201.127 PERN0 | - | OK | same |
| 2 | PCIe RX+ (module receive) | U31B.116 PCIe_RX_P | PCIE2_RX_P | C251 220n 16V | U201.124 PETP0 | - | OK | same |
| 2 | PCIe RX- | U31B.118 PCIe_RX_N | PCIE2_RX_N | C252 220n 16V | U201.123 PETN0 | - | OK | same |
| 3 | PCIe TX+ (module transmit) | U32B.122 PCIe_TX_P | PCIE3_TX_P | direct | U301.128 PERP0 | - | OK | same |
| 3 | PCIe TX- | U32B.124 PCIe_TX_N | PCIE3_TX_N | direct | U301.127 PERN0 | - | OK | same |
| 3 | PCIe RX+ (module receive) | U32B.116 PCIe_RX_P | PCIE3_RX_P | C351 220n 16V | U301.124 PETP0 | - | OK | same |
| 3 | PCIe RX- | U32B.118 PCIe_RX_N | PCIE3_RX_N | C352 220n 16V | U301.123 PETN0 | - | OK | same |

### A.2 PCIe control and the module clock

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | PCIe_CLK_P (module 100 MHz out) | U30B.110 PCIe_CLK_P | PCIE1_CLK_P | direct | U101.74 REFCLKI_P | - | OK | same |
| 1 | PCIe_CLK_N | U30B.112 PCIe_CLK_N | PCIE1_CLK_N | direct | U101.73 REFCLKI_N | - | OK | same |
| 1 | PCIe_CLK_nREQ | U30B.102 PCIe_CLK_nREQ | PCIE1_CLKREQ_n | - | (none) | R129 1k to GND | n/a | same |
| 1 | PCIe_nRST | U30B.109 PCIe_nRST | PCIE1_nRST | direct | U101.10 PERST_L | - | OK | same |
| 1 | PCIE_nWAKE | U30B.104 PCIE_nWAKE | PCIE1_nWAKE | direct | J_M2C1.55 ~{PEWAKE0}; J_M2N1.54 ~{PEWAKE} | R132 10k to +3V3_S1B | OK | same |
| 1 | PCIE_PWR_EN | U30B.106 PCIE_PWR_EN | PCIE_PWR_EN1 | R164 10k | Q111.3 D; U103.3 S1A_EN | R106 100k to GND | n/a | differs: direct to U103.3 PCIE_PWR_EN1; R106 100k to GND |
| 2 | PCIe_CLK_P (module 100 MHz out) | U31B.110 PCIe_CLK_P | PCIE2_CLK_P | direct | U201.74 REFCLKI_P | - | OK | same |
| 2 | PCIe_CLK_N | U31B.112 PCIe_CLK_N | PCIE2_CLK_N | direct | U201.73 REFCLKI_N | - | OK | same |
| 2 | PCIe_CLK_nREQ | U31B.102 PCIe_CLK_nREQ | PCIE2_CLKREQ_n | - | (none) | R229 1k to GND | n/a | same |
| 2 | PCIe_nRST | U31B.109 PCIe_nRST | PCIE2_nRST | direct | U201.10 PERST_L | - | OK | same |
| 2 | PCIE_nWAKE | U31B.104 PCIE_nWAKE | PCIE2_nWAKE | direct | J_M2C2.54 ~{PEWAKE}; J_M2N2.54 ~{PEWAKE} | R232 10k to +3V3_S2B | OK | same |
| 2 | PCIE_PWR_EN | U31B.106 PCIE_PWR_EN | PCIE_PWR_EN2 | direct | U203.3 PCIE_PWR_EN2 | R206 100k to GND | n/a | same |
| 3 | PCIe_CLK_P (module 100 MHz out) | U32B.110 PCIe_CLK_P | PCIE3_CLK_P | direct | U301.74 REFCLKI_P | - | OK | same |
| 3 | PCIe_CLK_N | U32B.112 PCIe_CLK_N | PCIE3_CLK_N | direct | U301.73 REFCLKI_N | - | OK | same |
| 3 | PCIe_CLK_nREQ | U32B.102 PCIe_CLK_nREQ | PCIE3_CLKREQ_n | - | (none) | R329 1k to GND | n/a | same |
| 3 | PCIe_nRST | U32B.109 PCIe_nRST | PCIE3_nRST | direct | U301.10 PERST_L | - | OK | same |
| 3 | PCIE_nWAKE | U32B.104 PCIE_nWAKE | PCIE3_nWAKE | direct | J_M2C3.55 ~{PEWAKE0}; J_M2N3.54 ~{PEWAKE} | R332 10k to +3V3_S3B | OK | same |
| 3 | PCIE_PWR_EN | U32B.106 PCIE_PWR_EN | PCIE_PWR_EN3 | R364 10k | Q311.3 D; U303.3 S3A_EN | R306 100k to GND | n/a | differs: direct to U303.3 PCIE_PWR_EN3; R306 100k to GND |

### A.3 reference clock tree

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | REFCLKO_P0 to own REFCLKP | U101.85 REFCLKO_P0 | PCIE1_RCLK0_SRC_P | R175 33.2R 1% + C195 100n 16V | U101.110 REFCLKP | R177 49.9R 1% to GND | OK | differs: direct to U101.110 REFCLKP; - |
| 1 | REFCLKO_N0 to own REFCLKN | U101.83 REFCLKO_N0 | PCIE1_RCLK0_SRC_N | R176 33.2R 1% + C196 100n 16V | U101.111 REFCLKN | R178 49.9R 1% to GND | OK | differs: direct to U101.111 REFCLKN; - |
| 1 | REFCLKO_P1 to NVMe REFCLKp | U101.81 REFCLKO_P1 | NVME1_CLK_SRC_P | R179 33.2R 1% | J_M2N1.55 REFCLKp | R181 49.9R 1% to GND | OK | differs: direct to J_M2N1.55 REFCLKp; - |
| 1 | REFCLKO_N1 to NVMe REFCLKn | U101.80 REFCLKO_N1 | NVME1_CLK_SRC_N | R180 33.2R 1% | J_M2N1.53 REFCLKn | R182 49.9R 1% to GND | OK | differs: direct to J_M2N1.53 REFCLKn; - |
| 1 | REFCLKO_P2 to card REFCLKp | U101.78 REFCLKO_P2 | CARD1_CLK_SRC_P | R183 33.2R 1% | J_M2C1.47 REFCLKp0 | R185 49.9R 1% to GND | OK | differs: direct to J_M2C1.47 REFCLKp0; - |
| 1 | REFCLKO_N2 to card REFCLKn | U101.77 REFCLKO_N2 | CARD1_CLK_SRC_N | R184 33.2R 1% | J_M2C1.49 REFCLKn0 | R186 49.9R 1% to GND | OK | differs: direct to J_M2C1.49 REFCLKn0; - |
| 1 | REFCLKO_P3 (unused) | U101.76 REFCLKO_P3 | unconnected-(U101-REFCLKO_P3-Pad76) | - | (none) | - | n/a | same |
| 1 | IREF | U101.86 IREF | S1_IREF | - | (none) | R117 475 1% to GND | n/a | same |
| 1 | REXT | U101.116 REXT | S1_REXT | - | (none) | R118 1.43k 1% to GND | n/a | same |
| 1 | CLKBUF_PD | U101.60 CLKBUF_PD | unconnected-(U101-CLKBUF_PD-Pad60) | - | (none) | - | n/a | same |
| 1 | SLOTCLK | U101.33 SLOTCLK | S1_SLOTCLK | - | (none) | R119 5.1k to +3V3_S1B | n/a | same |
| 2 | REFCLKO_P0 to own REFCLKP | U201.85 REFCLKO_P0 | PCIE2_RCLK0_SRC_P | R275 33.2R 1% + C295 100n 16V | U201.110 REFCLKP | R277 49.9R 1% to GND | OK | differs: direct to U201.110 REFCLKP; - |
| 2 | REFCLKO_N0 to own REFCLKN | U201.83 REFCLKO_N0 | PCIE2_RCLK0_SRC_N | R276 33.2R 1% + C296 100n 16V | U201.111 REFCLKN | R278 49.9R 1% to GND | OK | differs: direct to U201.111 REFCLKN; - |
| 2 | REFCLKO_P1 to NVMe REFCLKp | U201.81 REFCLKO_P1 | NVME2_CLK_SRC_P | R279 33.2R 1% | J_M2N2.55 REFCLKp | R281 49.9R 1% to GND | OK | differs: direct to J_M2N2.55 REFCLKp; - |
| 2 | REFCLKO_N1 to NVMe REFCLKn | U201.80 REFCLKO_N1 | NVME2_CLK_SRC_N | R280 33.2R 1% | J_M2N2.53 REFCLKn | R282 49.9R 1% to GND | OK | differs: direct to J_M2N2.53 REFCLKn; - |
| 2 | REFCLKO_P2 to card REFCLKp | U201.78 REFCLKO_P2 | CARD2_CLK_SRC_P | R283 33.2R 1% | J_M2C2.55 REFCLKp | R285 49.9R 1% to GND | OK | differs: direct to J_M2C2.55 REFCLKp; - |
| 2 | REFCLKO_N2 to card REFCLKn | U201.77 REFCLKO_N2 | CARD2_CLK_SRC_N | R284 33.2R 1% | J_M2C2.53 REFCLKn | R286 49.9R 1% to GND | OK | differs: direct to J_M2C2.53 REFCLKn; - |
| 2 | REFCLKO_P3 (unused) | U201.76 REFCLKO_P3 | unconnected-(U201-REFCLKO_P3-Pad76) | - | (none) | - | n/a | same |
| 2 | IREF | U201.86 IREF | S2_IREF | - | (none) | R217 475 1% to GND | n/a | same |
| 2 | REXT | U201.116 REXT | S2_REXT | - | (none) | R218 1.43k 1% to GND | n/a | same |
| 2 | CLKBUF_PD | U201.60 CLKBUF_PD | unconnected-(U201-CLKBUF_PD-Pad60) | - | (none) | - | n/a | same |
| 2 | SLOTCLK | U201.33 SLOTCLK | S2_SLOTCLK | - | (none) | R219 5.1k to +3V3_S2B | n/a | same |
| 3 | REFCLKO_P0 to own REFCLKP | U301.85 REFCLKO_P0 | PCIE3_RCLK0_SRC_P | R375 33.2R 1% + C395 100n 16V | U301.110 REFCLKP | R377 49.9R 1% to GND | OK | differs: direct to U301.110 REFCLKP; - |
| 3 | REFCLKO_N0 to own REFCLKN | U301.83 REFCLKO_N0 | PCIE3_RCLK0_SRC_N | R376 33.2R 1% + C396 100n 16V | U301.111 REFCLKN | R378 49.9R 1% to GND | OK | differs: direct to U301.111 REFCLKN; - |
| 3 | REFCLKO_P1 to NVMe REFCLKp | U301.81 REFCLKO_P1 | NVME3_CLK_SRC_P | R379 33.2R 1% | J_M2N3.55 REFCLKp | R381 49.9R 1% to GND | OK | differs: direct to J_M2N3.55 REFCLKp; - |
| 3 | REFCLKO_N1 to NVMe REFCLKn | U301.80 REFCLKO_N1 | NVME3_CLK_SRC_N | R380 33.2R 1% | J_M2N3.53 REFCLKn | R382 49.9R 1% to GND | OK | differs: direct to J_M2N3.53 REFCLKn; - |
| 3 | REFCLKO_P2 to card REFCLKp | U301.78 REFCLKO_P2 | CARD3_CLK_SRC_P | R383 33.2R 1% | J_M2C3.47 REFCLKp0 | R385 49.9R 1% to GND | OK | differs: direct to J_M2C3.47 REFCLKp0; - |
| 3 | REFCLKO_N2 to card REFCLKn | U301.77 REFCLKO_N2 | CARD3_CLK_SRC_N | R384 33.2R 1% | J_M2C3.49 REFCLKn0 | R386 49.9R 1% to GND | OK | differs: direct to J_M2C3.49 REFCLKn0; - |
| 3 | REFCLKO_P3 (unused) | U301.76 REFCLKO_P3 | unconnected-(U301-REFCLKO_P3-Pad76) | - | (none) | - | n/a | same |
| 3 | IREF | U301.86 IREF | S3_IREF | - | (none) | R317 475 1% to GND | n/a | same |
| 3 | REXT | U301.116 REXT | S3_REXT | - | (none) | R318 1.43k 1% to GND | n/a | same |
| 3 | CLKBUF_PD | U301.60 CLKBUF_PD | unconnected-(U301-CLKBUF_PD-Pad60) | - | (none) | - | n/a | same |
| 3 | SLOTCLK | U301.33 SLOTCLK | S3_SLOTCLK | - | (none) | R319 5.1k to +3V3_S3B | n/a | same |

### A.4 PCIe downstream

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | port 1 switch TX+ to NVMe | U101.100 PETP1 | NVME1_RX_SW_P | C153 220n 16V | J_M2N1.49 PETp0/SATA-A+ | - | OK | **differs: J_M2N1.43 PERp0/SATA-B-** (NVME1_RX_P) |
| 1 | port 1 switch TX- | U101.101 PETN1 | NVME1_RX_SW_N | C154 220n 16V | J_M2N1.47 PETn0/SATA-A- | - | OK | **differs: J_M2N1.41 PERn0/SATA-B+** (NVME1_RX_N) |
| 1 | port 1 switch RX+ from NVMe | U101.97 PERP1 | NVME1_TX_P | direct | J_M2N1.43 PERp0/SATA-B- | - | OK | **differs: J_M2N1.49 PETp0/SATA-A+** (NVME1_TX_P) |
| 1 | port 1 switch RX- | U101.98 PERN1 | NVME1_TX_N | direct | J_M2N1.41 PERn0/SATA-B+ | - | OK | **differs: J_M2N1.47 PETn0/SATA-A-** (NVME1_TX_N) |
| 1 | port 1 PERST# | U101.5 DWNRST_L1 | PCIE1_RST1_n | direct | J_M2N1.50 ~{PERST} | - | OK | same |
| 1 | port 2 switch TX+ to card (key E) | U101.106 PETP2 | CARD1_RX_SW_P | C155 220n 16V | J_M2C1.35 PETp0 | - | OK | **differs: J_M2C1.41 PERp0** (CARD1_RX_P) |
| 1 | port 2 switch TX- | U101.107 PETN2 | CARD1_RX_SW_N | C156 220n 16V | J_M2C1.37 PETn0 | - | OK | **differs: J_M2C1.43 PERn0** (CARD1_RX_N) |
| 1 | port 2 switch RX+ from card | U101.102 PERP2 | CARD1_TX_P | direct | J_M2C1.41 PERp0 | - | OK | **differs: J_M2C1.35 PETp0** (CARD1_TX_P) |
| 1 | port 2 switch RX- | U101.103 PERN2 | CARD1_TX_N | direct | J_M2C1.43 PERn0 | - | OK | **differs: J_M2C1.37 PETn0** (CARD1_TX_N) |
| 1 | port 2 PERST# | U101.6 DWNRST_L2 | PCIE1_RST2_n | direct | J_M2C1.52 ~{PERST0} | - | OK | same |
| 1 | port 3 TX+ (unused) | U101.118 PETP3 | unconnected-(U101-PETP3-Pad118) | - | (none) | - | n/a | same |
| 1 | port 3 RX+ (unused) | U101.122 PERP3 | unconnected-(U101-PERP3-Pad122) | - | (none) | - | n/a | same |
| 2 | port 1 switch TX+ to NVMe | U201.100 PETP1 | NVME2_RX_SW_P | C253 220n 16V | J_M2N2.49 PETp0/SATA-A+ | - | OK | **differs: J_M2N2.43 PERp0/SATA-B-** (NVME2_RX_P) |
| 2 | port 1 switch TX- | U201.101 PETN1 | NVME2_RX_SW_N | C254 220n 16V | J_M2N2.47 PETn0/SATA-A- | - | OK | **differs: J_M2N2.41 PERn0/SATA-B+** (NVME2_RX_N) |
| 2 | port 1 switch RX+ from NVMe | U201.97 PERP1 | NVME2_TX_P | direct | J_M2N2.43 PERp0/SATA-B- | - | OK | **differs: J_M2N2.49 PETp0/SATA-A+** (NVME2_TX_P) |
| 2 | port 1 switch RX- | U201.98 PERN1 | NVME2_TX_N | direct | J_M2N2.41 PERn0/SATA-B+ | - | OK | **differs: J_M2N2.47 PETn0/SATA-A-** (NVME2_TX_N) |
| 2 | port 1 PERST# | U201.5 DWNRST_L1 | PCIE2_RST1_n | direct | J_M2N2.50 ~{PERST} | - | OK | same |
| 2 | port 2 switch TX+ to card (key B) | U201.106 PETP2 | CARD2_RX_SW_P | C255 220n 16V | J_M2C2.49 PETp0/SATA-A+ | - | OK | **differs: J_M2C2.43 PERp0/SATA-B-** (CARD2_RX_P) |
| 2 | port 2 switch TX- | U201.107 PETN2 | CARD2_RX_SW_N | C256 220n 16V | J_M2C2.47 PETn0/SATA-A- | - | OK | **differs: J_M2C2.41 PERn0/SATA-B+** (CARD2_RX_N) |
| 2 | port 2 switch RX+ from card | U201.102 PERP2 | CARD2_TX_P | direct | J_M2C2.43 PERp0/SATA-B- | - | OK | **differs: J_M2C2.49 PETp0/SATA-A+** (CARD2_TX_P) |
| 2 | port 2 switch RX- | U201.103 PERN2 | CARD2_TX_N | direct | J_M2C2.41 PERn0/SATA-B+ | - | OK | **differs: J_M2C2.47 PETn0/SATA-A-** (CARD2_TX_N) |
| 2 | port 2 PERST# | U201.6 DWNRST_L2 | PCIE2_RST2_n | direct | J_M2C2.50 ~{PERST} | - | OK | same |
| 2 | port 3 TX+ (unused) | U201.118 PETP3 | unconnected-(U201-PETP3-Pad118) | - | (none) | - | n/a | same |
| 2 | port 3 RX+ (unused) | U201.122 PERP3 | unconnected-(U201-PERP3-Pad122) | - | (none) | - | n/a | same |
| 3 | port 1 switch TX+ to NVMe | U301.100 PETP1 | NVME3_RX_SW_P | C353 220n 16V | J_M2N3.49 PETp0/SATA-A+ | - | OK | **differs: J_M2N3.43 PERp0/SATA-B-** (NVME3_RX_P) |
| 3 | port 1 switch TX- | U301.101 PETN1 | NVME3_RX_SW_N | C354 220n 16V | J_M2N3.47 PETn0/SATA-A- | - | OK | **differs: J_M2N3.41 PERn0/SATA-B+** (NVME3_RX_N) |
| 3 | port 1 switch RX+ from NVMe | U301.97 PERP1 | NVME3_TX_P | direct | J_M2N3.43 PERp0/SATA-B- | - | OK | **differs: J_M2N3.49 PETp0/SATA-A+** (NVME3_TX_P) |
| 3 | port 1 switch RX- | U301.98 PERN1 | NVME3_TX_N | direct | J_M2N3.41 PERn0/SATA-B+ | - | OK | **differs: J_M2N3.47 PETn0/SATA-A-** (NVME3_TX_N) |
| 3 | port 1 PERST# | U301.5 DWNRST_L1 | PCIE3_RST1_n | direct | J_M2N3.50 ~{PERST} | - | OK | same |
| 3 | port 2 switch TX+ to card (key E) | U301.106 PETP2 | CARD3_RX_SW_P | C355 220n 16V | J_M2C3.35 PETp0 | - | OK | **differs: J_M2C3.41 PERp0** (CARD3_RX_P) |
| 3 | port 2 switch TX- | U301.107 PETN2 | CARD3_RX_SW_N | C356 220n 16V | J_M2C3.37 PETn0 | - | OK | **differs: J_M2C3.43 PERn0** (CARD3_RX_N) |
| 3 | port 2 switch RX+ from card | U301.102 PERP2 | CARD3_TX_P | direct | J_M2C3.41 PERp0 | - | OK | **differs: J_M2C3.35 PETp0** (CARD3_TX_P) |
| 3 | port 2 switch RX- | U301.103 PERN2 | CARD3_TX_N | direct | J_M2C3.43 PERn0 | - | OK | **differs: J_M2C3.37 PETn0** (CARD3_TX_N) |
| 3 | port 2 PERST# | U301.6 DWNRST_L2 | PCIE3_RST2_n | direct | J_M2C3.52 ~{PERST0} | - | OK | same |
| 3 | port 3 TX+ (unused) | U301.118 PETP3 | unconnected-(U301-PETP3-Pad118) | - | (none) | - | n/a | same |
| 3 | port 3 RX+ (unused) | U301.122 PERP3 | unconnected-(U301-PERP3-Pad122) | - | (none) | - | n/a | same |

### A.5 switch test straps

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | TEST1 | U101.9 TEST1 | S1_TEST1 | - | (none) | R123 5.1k to +3V3_S1B | n/a | same |
| 1 | TEST2 | U101.16 TEST2 | S1_TESTL | direct | U101.17 TEST3; U101.18 VC1_EN; U101.22 TEST4; U101.25 TEST5; U101.51 TEST6 | R124 330 to GND | n/a | same |
| 1 | TCK | U101.89 TCK | S1_JTAGL | direct | U101.92 TMS; U101.93 TDI; U101.94 TRST_L | R128 330 to GND | n/a | same |
| 1 | TDI | U101.93 TDI | S1_JTAGL | direct | U101.89 TCK; U101.92 TMS; U101.94 TRST_L | R128 330 to GND | n/a | same |
| 2 | TEST1 | U201.9 TEST1 | S2_TEST1 | - | (none) | R223 5.1k to +3V3_S2B | n/a | same |
| 2 | TEST2 | U201.16 TEST2 | S2_TESTL | direct | U201.17 TEST3; U201.18 VC1_EN; U201.22 TEST4; U201.25 TEST5; U201.51 TEST6 | R224 330 to GND | n/a | same |
| 2 | TCK | U201.89 TCK | S2_JTAGL | direct | U201.92 TMS; U201.93 TDI; U201.94 TRST_L | R228 330 to GND | n/a | same |
| 2 | TDI | U201.93 TDI | S2_JTAGL | direct | U201.89 TCK; U201.92 TMS; U201.94 TRST_L | R228 330 to GND | n/a | same |
| 3 | TEST1 | U301.9 TEST1 | S3_TEST1 | - | (none) | R323 5.1k to +3V3_S3B | n/a | same |
| 3 | TEST2 | U301.16 TEST2 | S3_TESTL | direct | U301.17 TEST3; U301.18 VC1_EN; U301.22 TEST4; U301.25 TEST5; U301.51 TEST6 | R324 330 to GND | n/a | same |
| 3 | TCK | U301.89 TCK | S3_JTAGL | direct | U301.92 TMS; U301.93 TDI; U301.94 TRST_L | R328 330 to GND | n/a | same |
| 3 | TDI | U301.93 TDI | S3_JTAGL | direct | U301.89 TCK; U301.92 TMS; U301.94 TRST_L | R328 330 to GND | n/a | same |

### A.6 USB home host (USB3-0)

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | USB3-0 TX+ (home host of bank 1) | U30B.142 USB3-0-TX_P | HOST1_0TX_P | direct | U109.19 B0p | - | OK | same |
| 1 | USB3-0 TX- | U30B.140 USB3-0-TX_N | HOST1_0TX_N | direct | U109.18 B0n | - | OK | same |
| 1 | USB3-0 RX+ | U30B.130 USB3-0-RX_P | HOST1_0RX_P | direct | U109.17 B1p | - | OK | same |
| 1 | USB3-0 RX- | U30B.128 USB3-0-RX_N | HOST1_0RX_N | direct | U109.16 B1n | - | OK | same |
| 1 | USB3-0 D+ (USB 2.0 half) | U30B.134 USB3-0-DP | HOST1_0D_P | direct | U110.1 1Dp | - | OK | same |
| 1 | USB3-0 D- | U30B.136 USB3-0-DM | HOST1_0D_N | direct | U110.2 1Dn | - | OK | same |
| 2 | USB3-0 TX+ (home host of bank 2) | U31B.142 USB3-0-TX_P | HOST2_0TX_P | direct | U209.19 B0p | - | OK | same |
| 2 | USB3-0 TX- | U31B.140 USB3-0-TX_N | HOST2_0TX_N | direct | U209.18 B0n | - | OK | same |
| 2 | USB3-0 RX+ | U31B.130 USB3-0-RX_P | HOST2_0RX_P | direct | U209.17 B1p | - | OK | same |
| 2 | USB3-0 RX- | U31B.128 USB3-0-RX_N | HOST2_0RX_N | direct | U209.16 B1n | - | OK | same |
| 2 | USB3-0 D+ (USB 2.0 half) | U31B.134 USB3-0-DP | HOST2_0D_P | direct | U210.1 1Dp | - | OK | same |
| 2 | USB3-0 D- | U31B.136 USB3-0-DM | HOST2_0D_N | direct | U210.2 1Dn | - | OK | same |
| 3 | USB3-0 TX+ (home host of bank 3) | U32B.142 USB3-0-TX_P | HOST3_0TX_P | direct | U309.19 B0p | - | OK | same |
| 3 | USB3-0 TX- | U32B.140 USB3-0-TX_N | HOST3_0TX_N | direct | U309.18 B0n | - | OK | same |
| 3 | USB3-0 RX+ | U32B.130 USB3-0-RX_P | HOST3_0RX_P | direct | U309.17 B1p | - | OK | same |
| 3 | USB3-0 RX- | U32B.128 USB3-0-RX_N | HOST3_0RX_N | direct | U309.16 B1n | - | OK | same |
| 3 | USB3-0 D+ (USB 2.0 half) | U32B.134 USB3-0-DP | HOST3_0D_P | direct | U310.1 1Dp | - | OK | same |
| 3 | USB3-0 D- | U32B.136 USB3-0-DM | HOST3_0D_N | direct | U310.2 1Dn | - | OK | same |

### A.7 USB failover host (USB3-1)

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | USB3-1 TX+ (failover host of bank 3) | U30B.171 USB3-1-TX_P | HOST1_1TX_P | direct | U309.15 C0p | - | OK | same |
| 1 | USB3-1 TX- | U30B.169 USB3-1-TX_N | HOST1_1TX_N | direct | U309.14 C0n | - | OK | same |
| 1 | USB3-1 RX+ | U30B.159 USB3-1-RX_P | HOST1_1RX_P | direct | U309.13 C1p | - | OK | same |
| 1 | USB3-1 RX- | U30B.157 USB3-1-RX_N | HOST1_1RX_N | direct | U309.12 C1n | - | OK | same |
| 1 | USB3-1 D+ | U30B.163 USB3-1-DP | HOST1_1D_P | direct | U310.3 2Dp | - | OK | same |
| 1 | USB3-1 D- | U30B.165 USB3-1-DM | HOST1_1D_N | direct | U310.4 2Dn | - | OK | same |
| 2 | USB3-1 TX+ (failover host of bank 1) | U31B.171 USB3-1-TX_P | HOST2_1TX_P | direct | U109.15 C0p | - | OK | same |
| 2 | USB3-1 TX- | U31B.169 USB3-1-TX_N | HOST2_1TX_N | direct | U109.14 C0n | - | OK | same |
| 2 | USB3-1 RX+ | U31B.159 USB3-1-RX_P | HOST2_1RX_P | direct | U109.13 C1p | - | OK | same |
| 2 | USB3-1 RX- | U31B.157 USB3-1-RX_N | HOST2_1RX_N | direct | U109.12 C1n | - | OK | same |
| 2 | USB3-1 D+ | U31B.163 USB3-1-DP | HOST2_1D_P | direct | U110.3 2Dp | - | OK | same |
| 2 | USB3-1 D- | U31B.165 USB3-1-DM | HOST2_1D_N | direct | U110.4 2Dn | - | OK | same |
| 3 | USB3-1 TX+ (failover host of bank 2) | U32B.171 USB3-1-TX_P | HOST3_1TX_P | direct | U209.15 C0p | - | OK | same |
| 3 | USB3-1 TX- | U32B.169 USB3-1-TX_N | HOST3_1TX_N | direct | U209.14 C0n | - | OK | same |
| 3 | USB3-1 RX+ | U32B.159 USB3-1-RX_P | HOST3_1RX_P | direct | U209.13 C1p | - | OK | same |
| 3 | USB3-1 RX- | U32B.157 USB3-1-RX_N | HOST3_1RX_N | direct | U209.12 C1n | - | OK | same |
| 3 | USB3-1 D+ | U32B.163 USB3-1-DP | HOST3_1D_P | direct | U210.3 2Dp | - | OK | same |
| 3 | USB3-1 D- | U32B.165 USB3-1-DM | HOST3_1D_N | direct | U210.4 2Dn | - | OK | same |

### A.8 USB control pins

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | VBUS_EN | U30B.111 VBUS_EN | unconnected-(U30B-VBUS_EN-Pad111) | - | (none) | - | n/a | same |
| 1 | USB_OTG_ID | U30B.101 USB_OTG_ID | unconnected-(U30B-USB_OTG_ID-Pad101) | - | (none) | - | n/a | same |
| 2 | VBUS_EN | U31B.111 VBUS_EN | unconnected-(U31B-VBUS_EN-Pad111) | - | (none) | - | n/a | same |
| 2 | USB_OTG_ID | U31B.101 USB_OTG_ID | unconnected-(U31B-USB_OTG_ID-Pad101) | - | (none) | - | n/a | same |
| 3 | VBUS_EN | U32B.111 VBUS_EN | unconnected-(U32B-VBUS_EN-Pad111) | - | (none) | - | n/a | same |
| 3 | USB_OTG_ID | U32B.101 USB_OTG_ID | unconnected-(U32B-USB_OTG_ID-Pad101) | - | (none) | - | n/a | same |

### A.9 bank side

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | hub SS receiver + (upstream) | U102.58 USB_SSRXP_UP | BANK1_UPTX_P | direct | U109.3 A0p | - | OK | same |
| 1 | hub SS receiver - | U102.59 USB_SSRXM_UP | BANK1_UPTX_N | direct | U109.4 A0n | - | OK | same |
| 1 | hub SS transmitter + (upstream) | U102.55 USB_SSTXP_UP | BANK1_UPRX_P | C159 100n | U109.7 A1p | - | OK | same |
| 1 | hub SS transmitter - | U102.56 USB_SSTXM_UP | BANK1_UPRX_N | C160 100n | U109.8 A1n | - | OK | same |
| 1 | hub D+ (upstream) | U102.53 USB_DP_UP | BANK1_UPD_P | direct | U110.8 Dp | - | OK | same |
| 1 | hub D- (upstream) | U102.54 USB_DM_UP | BANK1_UPD_N | direct | U110.7 Dn | - | OK | same |
| 1 | hub USB_VBUS (upstream detect) | U102.48 USB_VBUS | HUB1_VBUS | - | (none) | R143 90.9k 1% to +5V_DEV; R144 10k 1% to GND | n/a | same |
| 1 | hub GRSTz | U102.50 GRSTz | HUB1_RST_n | direct | Q3.3 D | C163 1u to GND; R141 10k to +3V3_DEV | n/a | same |
| 1 | TMUXHS4212 SEL | U109.9 SEL | BSEL1 | R474 10k; direct | U80.2 BSEL1_D; TP504.1 1; U110.9 S; U41.38 PE8; U51.38 PE8; U61.38 PE8; U76.6 BSEL1; U80.1 BSEL1 | R160 100k to GND; C481 10n to GND | OK | differs: R474 10k; direct to U80.2 BSEL1_D; U110.9 S; U41.38 PE8; U51.38 PE8; U61.38 PE8; U76.6 BSEL1; U80.1 BSEL1; R160 100k to GND; C481 10n to GND |
| 1 | TMUXHS4212 OEn | U109.2 OEn | BOE1_n | direct | TP507.1 1; U110.6 OEn; U80.3 BOE1_n | R161 100k to GND | OK | differs: direct to U110.6 OEn; U80.3 BOE1_n; R161 100k to GND |
| 2 | hub SS receiver + (upstream) | U202.58 USB_SSRXP_UP | BANK2_UPTX_P | direct | U209.3 A0p | - | OK | same |
| 2 | hub SS receiver - | U202.59 USB_SSRXM_UP | BANK2_UPTX_N | direct | U209.4 A0n | - | OK | same |
| 2 | hub SS transmitter + (upstream) | U202.55 USB_SSTXP_UP | BANK2_UPRX_P | C259 100n | U209.7 A1p | - | OK | same |
| 2 | hub SS transmitter - | U202.56 USB_SSTXM_UP | BANK2_UPRX_N | C260 100n | U209.8 A1n | - | OK | same |
| 2 | hub D+ (upstream) | U202.53 USB_DP_UP | BANK2_UPD_P | direct | U210.8 Dp | - | OK | same |
| 2 | hub D- (upstream) | U202.54 USB_DM_UP | BANK2_UPD_N | direct | U210.7 Dn | - | OK | same |
| 2 | hub USB_VBUS (upstream detect) | U202.48 USB_VBUS | HUB2_VBUS | - | (none) | R243 90.9k 1% to +5V_DEV; R244 10k 1% to GND | n/a | same |
| 2 | hub GRSTz | U202.50 GRSTz | HUB2_RST_n | direct | Q4.3 D | C263 1u to GND; R241 10k to +3V3_DEV | n/a | same |
| 2 | TMUXHS4212 SEL | U209.9 SEL | BSEL2 | R475 10k; direct | U80.5 BSEL2_D; TP505.1 1; U210.9 S; U41.39 PE9; U51.39 PE9; U61.39 PE9; U76.11 BSEL2; U80.4 BSEL2 | R260 100k to GND; C482 10n to GND | OK | differs: R475 10k; direct to U80.5 BSEL2_D; U210.9 S; U41.39 PE9; U51.39 PE9; U61.39 PE9; U76.11 BSEL2; U80.4 BSEL2; R260 100k to GND; C482 10n to GND |
| 2 | TMUXHS4212 OEn | U209.2 OEn | BOE2_n | direct | TP508.1 1; U210.6 OEn; U80.6 BOE2_n | R261 100k to GND | OK | differs: direct to U210.6 OEn; U80.6 BOE2_n; R261 100k to GND |
| 3 | hub SS receiver + (upstream) | U302.58 USB_SSRXP_UP | BANK3_UPTX_P | direct | U309.3 A0p | - | OK | same |
| 3 | hub SS receiver - | U302.59 USB_SSRXM_UP | BANK3_UPTX_N | direct | U309.4 A0n | - | OK | same |
| 3 | hub SS transmitter + (upstream) | U302.55 USB_SSTXP_UP | BANK3_UPRX_P | C359 100n | U309.7 A1p | - | OK | same |
| 3 | hub SS transmitter - | U302.56 USB_SSTXM_UP | BANK3_UPRX_N | C360 100n | U309.8 A1n | - | OK | same |
| 3 | hub D+ (upstream) | U302.53 USB_DP_UP | BANK3_UPD_P | direct | U310.8 Dp | - | OK | same |
| 3 | hub D- (upstream) | U302.54 USB_DM_UP | BANK3_UPD_N | direct | U310.7 Dn | - | OK | same |
| 3 | hub USB_VBUS (upstream detect) | U302.48 USB_VBUS | HUB3_VBUS | - | (none) | R343 90.9k 1% to +5V_DEV; R344 10k 1% to GND | n/a | same |
| 3 | hub GRSTz | U302.50 GRSTz | HUB3_RST_n | direct | Q5.3 D | C363 1u to GND; R341 10k to +3V3_DEV | n/a | same |
| 3 | TMUXHS4212 SEL | U309.9 SEL | BSEL3 | R476 10k; direct | U80.9 BSEL3_D; TP506.1 1; U310.9 S; U41.40 PE10; U51.40 PE10; U61.40 PE10; U77.6 BSEL3; U80.10 BSEL3 | R360 100k to GND; C483 10n to GND | OK | differs: R476 10k; direct to U80.9 BSEL3_D; U310.9 S; U41.40 PE10; U51.40 PE10; U61.40 PE10; U77.6 BSEL3; U80.10 BSEL3; R360 100k to GND; C483 10n to GND |
| 3 | TMUXHS4212 OEn | U309.2 OEn | BOE3_n | direct | TP509.1 1; U310.6 OEn; U80.8 BOE3_n | R361 100k to GND | OK | differs: direct to U310.6 OEn; U80.8 BOE3_n; R361 100k to GND |
| 1 | hub DN1 SS TX+ to LimeSDR | U102.3 USB_SSTXP_DN1 | HUB1_D1TX_P | C161 100n | J_LIME.9 SSTX+ | - | OK | **differs: J_LIME.6 SSRX+** (HUB1_D1TX_P) |
| 1 | hub DN1 SS TX- | U102.4 USB_SSTXM_DN1 | HUB1_D1TX_N | C162 100n | J_LIME.8 SSTX- | - | OK | **differs: J_LIME.5 SSRX-** (HUB1_D1TX_N) |
| 1 | hub DN1 SS RX+ from LimeSDR | U102.6 USB_SSRXP_DN1 | LIME_SSRX_P | direct | J_LIME.6 SSRX+ | - | OK | **differs: J_LIME.9 SSTX+** (LIME_SSTX_P) |
| 1 | hub DN1 SS RX- | U102.7 USB_SSRXM_DN1 | LIME_SSRX_N | direct | J_LIME.5 SSRX- | - | OK | **differs: J_LIME.8 SSTX-** (LIME_SSTX_N) |

### A.10 HDMI0

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | HDMI0_TX2_P | U30B.170 HDMI0_TX2_P | HDMI1_D2_P | direct | U3.34 D2P_A | - | OK | same |
| 1 | HDMI0_TX2_N | U30B.172 HDMI0_TX2_N | HDMI1_D2_N | direct | U3.33 D2N_A | - | OK | same |
| 1 | HDMI0_TX1_P | U30B.176 HDMI0_TX1_P | HDMI1_D1_P | direct | U3.36 D1P_A | - | OK | same |
| 1 | HDMI0_TX1_N | U30B.178 HDMI0_TX1_N | HDMI1_D1_N | direct | U3.35 D1N_A | - | OK | same |
| 1 | HDMI0_TX0_P | U30B.182 HDMI0_TX0_P | HDMI1_D0_P | direct | U3.38 D0P_A | - | OK | same |
| 1 | HDMI0_TX0_N | U30B.184 HDMI0_TX0_N | HDMI1_D0_N | direct | U3.37 D0N_A | - | OK | same |
| 1 | HDMI0_CLK_P | U30B.188 HDMI0_CLK_P | HDMI1_CK_P | direct | U3.32 D3P_A | - | OK | same |
| 1 | HDMI0_CLK_N | U30B.190 HDMI0_CLK_N | HDMI1_CK_N | direct | U3.31 D3N_A | - | OK | same |
| 1 | HDMI0_SDA | U30B.199 HDMI0_SDA | HDMI1_SDA | direct | U3.41 SDA_A | - | OK | same |
| 1 | HDMI0_SCL | U30B.200 HDMI0_SCL | HDMI1_SCL | direct | U3.42 SCL_A | - | OK | same |
| 1 | HDMI0_HOTPLUG | U30B.153 HDMI0_HOTPLUG | HDMI1_HPD | direct | U3.19 HPD_A | - | OK | same |
| 1 | HDMI0_CEC | U30B.151 HDMI0_CEC | HDMI1_CEC | direct | U3.18 CEC_A | - | OK | same |
| 2 | HDMI0_TX2_P | U31B.170 HDMI0_TX2_P | HDMI2_D2_P | direct | U3.25 D2P_B | - | OK | same |
| 2 | HDMI0_TX2_N | U31B.172 HDMI0_TX2_N | HDMI2_D2_N | direct | U3.24 D2N_B | - | OK | same |
| 2 | HDMI0_TX1_P | U31B.176 HDMI0_TX1_P | HDMI2_D1_P | direct | U3.27 D1P_B | - | OK | same |
| 2 | HDMI0_TX1_N | U31B.178 HDMI0_TX1_N | HDMI2_D1_N | direct | U3.26 D1N_B | - | OK | same |
| 2 | HDMI0_TX0_P | U31B.182 HDMI0_TX0_P | HDMI2_D0_P | direct | U3.29 D0P_B | - | OK | same |
| 2 | HDMI0_TX0_N | U31B.184 HDMI0_TX0_N | HDMI2_D0_N | direct | U3.28 D0N_B | - | OK | same |
| 2 | HDMI0_CLK_P | U31B.188 HDMI0_CLK_P | HDMI2_CK_P | direct | U3.23 D3P_B | - | OK | same |
| 2 | HDMI0_CLK_N | U31B.190 HDMI0_CLK_N | HDMI2_CK_N | direct | U3.22 D3N_B | - | OK | same |
| 2 | HDMI0_SDA | U31B.199 HDMI0_SDA | HDMI2_SDA | direct | U3.39 SDA_B | - | OK | same |
| 2 | HDMI0_SCL | U31B.200 HDMI0_SCL | HDMI2_SCL | direct | U3.40 SCL_B | - | OK | same |
| 2 | HDMI0_HOTPLUG | U31B.153 HDMI0_HOTPLUG | HDMI2_HPD | direct | U3.21 HPD_B | - | OK | same |
| 2 | HDMI0_CEC | U31B.151 HDMI0_CEC | HDMI2_CEC | direct | U3.20 CEC_B | - | OK | same |
| 3 | HDMI0_TX2_P | U32B.170 HDMI0_TX2_P | HDMI3_D2_P | direct | U4.25 D2P_B | - | OK | same |
| 3 | HDMI0_TX2_N | U32B.172 HDMI0_TX2_N | HDMI3_D2_N | direct | U4.24 D2N_B | - | OK | same |
| 3 | HDMI0_TX1_P | U32B.176 HDMI0_TX1_P | HDMI3_D1_P | direct | U4.27 D1P_B | - | OK | same |
| 3 | HDMI0_TX1_N | U32B.178 HDMI0_TX1_N | HDMI3_D1_N | direct | U4.26 D1N_B | - | OK | same |
| 3 | HDMI0_TX0_P | U32B.182 HDMI0_TX0_P | HDMI3_D0_P | direct | U4.29 D0P_B | - | OK | same |
| 3 | HDMI0_TX0_N | U32B.184 HDMI0_TX0_N | HDMI3_D0_N | direct | U4.28 D0N_B | - | OK | same |
| 3 | HDMI0_CLK_P | U32B.188 HDMI0_CLK_P | HDMI3_CK_P | direct | U4.23 D3P_B | - | OK | same |
| 3 | HDMI0_CLK_N | U32B.190 HDMI0_CLK_N | HDMI3_CK_N | direct | U4.22 D3N_B | - | OK | same |
| 3 | HDMI0_SDA | U32B.199 HDMI0_SDA | HDMI3_SDA | direct | U4.39 SDA_B | - | OK | same |
| 3 | HDMI0_SCL | U32B.200 HDMI0_SCL | HDMI3_SCL | direct | U4.40 SCL_B | - | OK | same |
| 3 | HDMI0_HOTPLUG | U32B.153 HDMI0_HOTPLUG | HDMI3_HPD | direct | U4.21 HPD_B | - | OK | same |
| 3 | HDMI0_CEC | U32B.151 HDMI0_CEC | HDMI3_CEC | direct | U4.20 CEC_B | - | OK | same |

### A.11 HDMI switch control and output

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 0 | SEL2 (HDMI_SEL1) | U3.17 SEL2 | HDMI_SEL1 | direct | J_PANEL.12 Pin_12; TP18.1 1 | R15 100k to GND | OK | same |
| 0 | SEL2 (HDMI_SEL2) | U4.17 SEL2 | HDMI_SEL2 | direct | J_PANEL.13 Pin_13; TP19.1 1 | R16 100k to GND | OK | same |
| 0 | EN | U3.2 EN | HDMI_SW_EN | direct | U3.16 SEL1; U4.16 SEL1; U4.2 EN | R14 10k to +3V3_DEV | n/a | same |
| 0 | D0P common to J_HDMI | U4.5 D0P | HDMIO_D0_P | direct | J_HDMI.7 D0+ | - | OK | same |
| 0 | SDA common | U4.4 SDA | HDMIO_SDA | direct | J_HDMI.16 SDA | R18 2.2k to +5V_HDMI | OK | same |
| 0 | SCL common | U4.3 SCL | HDMIO_SCL | direct | J_HDMI.15 SCL | R17 2.2k to +5V_HDMI | OK | same |
| 0 | HPD common | U4.14 HPD | HDMIO_HPD | R19 15k | J_HDMI.19 HPD | R20 22k to GND | OK | same |

### A.12 Ethernet

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | Ethernet_Pair0_P | U30A.12 Ethernet_Pair0_P | ETH1_P0_P | C175 100n | U1.1 TXRX1P_A | - | OK | same |
| 1 | Ethernet_Pair0_N | U30A.10 Ethernet_Pair0_N | ETH1_P0_N | C176 100n | U1.2 TXRX1M_A | - | OK | same |
| 1 | Ethernet_Pair1_P | U30A.4 Ethernet_Pair1_P | ETH1_P1_P | C177 100n | U1.4 TXRX1P_B | - | OK | same |
| 1 | Ethernet_Pair1_N | U30A.6 Ethernet_Pair1_N | ETH1_P1_N | C178 100n | U1.5 TXRX1M_B | - | OK | same |
| 1 | Ethernet_Pair2_P | U30A.11 Ethernet_Pair2_P | ETH1_P2_P | C179 100n | U1.6 TXRX1P_C | - | OK | same |
| 1 | Ethernet_Pair2_N | U30A.9 Ethernet_Pair2_N | ETH1_P2_N | C180 100n | U1.7 TXRX1M_C | - | OK | same |
| 1 | Ethernet_Pair3_P | U30A.3 Ethernet_Pair3_P | ETH1_P3_P | C181 100n | U1.8 TXRX1P_D | - | OK | same |
| 1 | Ethernet_Pair3_N | U30A.5 Ethernet_Pair3_N | ETH1_P3_N | C182 100n | U1.9 TXRX1M_D | - | OK | same |
| 2 | Ethernet_Pair0_P | U31A.12 Ethernet_Pair0_P | ETH2_P0_P | C275 100n | U1.12 TXRX2P_A | - | OK | same |
| 2 | Ethernet_Pair0_N | U31A.10 Ethernet_Pair0_N | ETH2_P0_N | C276 100n | U1.13 TXRX2M_A | - | OK | same |
| 2 | Ethernet_Pair1_P | U31A.4 Ethernet_Pair1_P | ETH2_P1_P | C277 100n | U1.15 TXRX2P_B | - | OK | same |
| 2 | Ethernet_Pair1_N | U31A.6 Ethernet_Pair1_N | ETH2_P1_N | C278 100n | U1.16 TXRX2M_B | - | OK | same |
| 2 | Ethernet_Pair2_P | U31A.11 Ethernet_Pair2_P | ETH2_P2_P | C279 100n | U1.17 TXRX2P_C | - | OK | same |
| 2 | Ethernet_Pair2_N | U31A.9 Ethernet_Pair2_N | ETH2_P2_N | C280 100n | U1.18 TXRX2M_C | - | OK | same |
| 2 | Ethernet_Pair3_P | U31A.3 Ethernet_Pair3_P | ETH2_P3_P | C281 100n | U1.20 TXRX2P_D | - | OK | same |
| 2 | Ethernet_Pair3_N | U31A.5 Ethernet_Pair3_N | ETH2_P3_N | C282 100n | U1.21 TXRX2M_D | - | OK | same |
| 3 | Ethernet_Pair0_P | U32A.12 Ethernet_Pair0_P | ETH3_P0_P | C375 100n | U1.24 TXRX3P_A | - | OK | same |
| 3 | Ethernet_Pair0_N | U32A.10 Ethernet_Pair0_N | ETH3_P0_N | C376 100n | U1.25 TXRX3M_A | - | OK | same |
| 3 | Ethernet_Pair1_P | U32A.4 Ethernet_Pair1_P | ETH3_P1_P | C377 100n | U1.26 TXRX3P_B | - | OK | same |
| 3 | Ethernet_Pair1_N | U32A.6 Ethernet_Pair1_N | ETH3_P1_N | C378 100n | U1.27 TXRX3M_B | - | OK | same |
| 3 | Ethernet_Pair2_P | U32A.11 Ethernet_Pair2_P | ETH3_P2_P | C379 100n | U1.28 TXRX3P_C | - | OK | same |
| 3 | Ethernet_Pair2_N | U32A.9 Ethernet_Pair2_N | ETH3_P2_N | C380 100n | U1.29 TXRX3M_C | - | OK | same |
| 3 | Ethernet_Pair3_P | U32A.3 Ethernet_Pair3_P | ETH3_P3_P | C381 100n | U1.31 TXRX3P_D | - | OK | same |
| 3 | Ethernet_Pair3_N | U32A.5 Ethernet_Pair3_N | ETH3_P3_N | C382 100n | U1.32 TXRX3M_D | - | OK | same |

### A.13 heartbeat

| Slot/bank | Signal | Start pin | Net (candidate) | In series | Far end | Shunt | Check | B21 (main) |
|---|---|---|---|---|---|---|---|---|
| 1 | GPIO16 heartbeat | U30A.29 GPIO16 | HB_CM1 | direct | Q105.2 S | R157 10k to +3V3_CM1 | n/a | same |
| 2 | GPIO16 heartbeat | U31A.29 GPIO16 | HB_CM2 | direct | Q205.2 S | R257 10k to +3V3_CM2 | n/a | same |
| 3 | GPIO16 heartbeat | U32A.29 GPIO16 | HB_CM3 | direct | Q305.2 S | R357 10k to +3V3_CM3 | n/a | same |


## Appendix B. Questions drafted for outside parties (not sent)

The session never writes to a supplier. These are prepared for the owner's outreach or ordering session.

**Q-FAB-RPI-1 (Raspberry Pi, Compute Module 5)**

Our carrier (a prototype, nothing built) keeps USB hubs, USB 2.0 host-select switches and an HDMI switch powered while
a CM5 on it may be unpowered. In that state, and at every carrier power-up before the CM5's 5 V rises, it can apply:
(1) a USB 2.0 device attach pull-up (about 1.5 kOhm to 3.3 V) to USB3-0-DP or USB3-1-DP (pins 134, 163); (2) about 5 V
through 2.2 kOhm to HDMI0_SDA and HDMI0_SCL (pins 199, 200); (3) about 3 V through 15 kOhm to HDMI0_HOTPLUG (pin 153).
The datasheet says no pin should be powered before the 5 V rail is active and that a CM5 with external voltage on a
pin might not power up again. Is there a current or voltage that these pins tolerate while the CM5 is unpowered, and
for how long? Separately: what is the electrical standard of PCIe_CLK_P/N (pins 110/112) (HCSL or other, swing, source
termination on the module), and does the CM5 enable spread spectrum on it? What is the common-mode voltage of the USB
3.0 receive pins (128/130, 157/159)?

**Q-FAB-ASIARF-1 (AsiaRF, AW7915-AED)**

Please send the M.2 key A/E pin assignment of the AW7915-AED, in particular which pins carry the module's PCIe
transmit pair, its receive pair, REFCLK, PERST#, CLKREQ#, PEWAKE#, W_DISABLE1# and W_DISABLE2#.

**Q-FAB-TI-1 (Texas Instruments, TUSB8041)**

With USB_VBUS held above its detection threshold (the 90.9 kOhm / 10 kOhm divider on a permanent 5 V) and no host on
the upstream port, does the TUSB8041 keep its upstream D+ pull-up connected? If USB_VBUS is instead taken from the
selected host's 5 V, does the hub remove the pull-up within a bounded time when that 5 V falls?
