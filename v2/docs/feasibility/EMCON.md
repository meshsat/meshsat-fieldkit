# EMCON feasibility: the transmitter inhibit table

MESHSAT-1357. This answers the EMCON item of the review of 26 September 2026
(`v2/docs/reviews/2026-09-26-foundation-progress-review.md:66`): "provide a transmitter-by-transmitter inhibit table:
physical control, active level, reset/default state, controller-failure behavior, powering/back-powering paths and proof
required.
The words airplane mode or W_DISABLE do not establish a guaranteed hardware inhibit for an unspecified module configuration" (review section 3).

**Prototype framing.** Nothing in this kit has been built, powered or measured. Every statement below is a reading of a
netlist or of a maker's document. "CLOSED at desk" means the reading is complete for that question; it is never a
physical result, and every row still owes the bench test named in section 6. First written 26 September 2026, 14:40
CEST; revised 15:20 CEST after the first checker's four blocking items, 16:55 CEST after the second checker's two,
17:19 CEST after the third checker's one, and 18:28 CEST after the fourth checker's one (section 9 lists what changed
in each). Written by the EMCON stream of the review's execution (worktree branch `fnd/rv-emc` at `1f614233`; main has
since moved to `01469100`, section 1.1).

What EMCON has to do is ruled: owner ruling D-05 (26 September 2026), "radios dark": every radio with an emission path
is powered off or RF-disabled in hardware; the VHF path keeps listening behind a transmit-only gate; GNSS, DCF77 and the
lightning sensor continue (`v2/docs/CONOPS.md:307` at main `b69f20db`, unchanged at `01469100`). The rule that judges it
is RF-002: "Every transmitter can be inhibited by a hardware path that does not depend on software, and the inhibit is
asserted by the unpowered and disconnected states" (`v2/ecad/tools/pcb_rules.yaml:1456`). The need is NEED-08, "Silence
every transmitter with one operator action that does not depend on software", and its requirement REQ-030 asks for "a
hardware line that needs no processor" (pending registry, i1 `v2/ecad/tools/pcb_requirements.yaml:114` and `:2585`).
Both are part of prototype 1's core (owner ruling D-01).

## 0. The answer

- **The kit has 17 transmitters**: the SA868 VHF exciter, the RA30H1317M1 30 W PA, the QMX HF unit, the RockBLOCK 9704,
  the RM520N-GL 5G module, two AW7915-AED WiFi link cards, the three Compute Module 5 WiFi radios and their three
  Bluetooth radios, the E22-900M30S LoRa module, two E72 (CC2652P) Zigbee/Thread radios and the LimeSDR Mini 2.4. A
  census of every radio part name on the six candidate netlists finds no other (section 4.18).
- **No transmitter's EMCON is closed on the bench, and one row closes at desk: the 30 W PA**, on path (b) alone
  (gate bias and keying on board D) in the states RF-002 names. Its two paths share one element, the `SW_EMCON`
  toggle and the `TX_INHIBIT_n` conductor, so the PA is single-fault tolerant only for faults downstream of that
  conductor. A fault at the shared element releases both paths. SD-EMC-6 accepts it, on condition that board C gets
  an EMCON lamp that is driven from the line state with no processor in its path. As drawn, no indication of the
  lines is independent of firmware: the TX lamp's supply exists only while the panel controller drives `PANEL_PWM`.
- **Shared items on the EMCON lines** (section 3: L1 to L4 and L7 open in the circuit, L6 open in the instrument, L5
  closed for the inhibit) hold every row that depends on `EMCON_HW`. They are read against the tools author's final
  record (r4t: R4T-D40, R4T-F8 third statement, R4T-F9). The line's own fail-safe hold is UNDECIDED on the candidates,
  because its quad gates state no Ioff, and the remedy needs 4.7 k on board B, not 10 k (L2). The FETs board B uses
  on `EMCON_ON` are driven at about 3.3 V, and their sheet states RDS(on) only at 5 V and 10 V (L7).
- **Radio by radio, on the round-6 netlists (merged on main in `458b2873`, section 1.1):** the radio-specific chain is
  complete at desk for the PA, the QMX, the LimeSDR, the six CM5 radios, and the power gates of the RockBLOCK, the
  E22, the two E72 and the two AW7915 cards. It stays open for the SA868 (the maker publishes no "receive" threshold for its PTT pin) and for the
  RM520N-GL: as drawn, its only inhibit is a firmware-mediated mode, and SD-EMC-1 now requires a circuit change on
  board B. The back-feed into the power-gated radios (RockBLOCK, E22, both E72, both AW7915, and the RM520N-GL once its
  supply is removable) from parts that stay powered is also open.
- **What the documents state for the two named modules.**
  - RM520N-GL: Quectel states that W_DISABLE1# LOW sets airplane mode, "the RF function will be disabled", in every
    AT+CFUN state (Hardware Design v1.1, section 4.4.1 and Table 22). Quectel does not state the time to RF off, the
    behaviour while the module boots or while its firmware is hung, or that no configuration can override the pin.
    Quectel's own documents show that in its LTE firmware the pin's function is a stored setting, disabled by default and
    host-writable (section 4.5). The released RM5xxN AT manual lists no such setting, and its own AT+QCFG=? response
    ends in an ellipsis. The maker's turn-off pin, FULL_CARD_POWER_OFF#, turns the module off "only after" a host
    AT+CFUN=0 handshake, and the supply is to be removed only after that turn-off. **The only inhibit the documents
    give that does not depend on the module's firmware is removal of its supply**, which Quectel warns can corrupt the
    module's flash when it is not done in that order.
  - AW7915-AED: AsiaRF's datasheet does not mention W_DISABLE1# at all, and the mainline Linux mt7915 driver has no
    rfkill code. Nothing is guaranteed, so the pin is not counted. The candidate board B removes the card's supply
    instead (section 4.6).
- **Feasibility verdict.** "Radios dark" is feasible with the ruled architecture, with two conditions. For 16 of the
  17 rows, each open item has a named circuit remedy on the board that owns it: a few passive parts, a single gate or
  buffer, or a FET per line (section 7). None of those changes a board-to-board interface, the stackup or a radio's
  part.
  - **The 5G row is feasible only at a cost.** Its firmware-independent inhibit is SD-EMC-1's supply removal. Both
    stages it adds hang on `EMCON_ON`, so what follows holds subject to L3 (a loss of +3V3_DEV releases them).
    - If EMCON asserts before the module has been turned on, both hardware stages act at once and hold. The module is
      never powered under EMCON, and no handshake is owed. This covers every power-up of the kit with the locking
      toggle already at EMCON, which is routine.
    - If EMCON asserts on a module that has been turned on, the stages follow the maker's turn-off order:
      W_DISABLE1# at once; the host's handshake; FULL_CARD_POWER_OFF# by hardware after a delay T_off that is sized
      for the handshake; the supply after a further T_cut. When the host's sequence finishes within T_off, the order
      is the maker's.

    The cost falls on two cases. In the fault case, the host's sequence fails. In the booting case, the module is
    booting when EMCON asserts, or restarts while the delays run, so the host cannot run the sequence until the module
    answers. The booting case is defined by the module's state, whatever started the boot: an EMCON release, a
    power-up with EMCON released, slot 2's CM5 cycling `PCIE_PWR_EN2`, a warm or hard reset through U6, AT+CFUN=1,1
    from either host, or a restart the module's own firmware starts (section 4.5). A power-up with EMCON released is at
    least as routine as a reversal. In either case:
    - the backstop turns the module off without the handshake, and the supply removal can corrupt its flash;
    - a module that does not honour W_DISABLE1# can emit until T_off + T_cut after EMCON. That is at least 15.9 s
      plus the software's reaction time, from the maker's 15 s AT+CFUN bound and its 900 ms Tpd. The delays run to
      the end whatever the module does, so the bound holds for every cause. In the fault case this needs a second
      failure. In the booting case it needs only one: the module misses a pin that falls while it boots, or one
      that is already low when it restarts. No document rules that out.

    The session accepted these in SD-EMC-1. It named a fallback in advance: if bench test E-05 shows that the fitted
    firmware misses that pin, the supply is removed at once when EMCON meets a boot that board B can see. Board B
    cannot see a restart started by AT+CFUN=1,1 or by the module's own firmware. For those the bound stays
    T_off + T_cut, which SD-EMC-1 states as a residual. The size of each is unknown until bench tests E-05 and E-12
    have run.
  - **Every row shares one element**, the toggle and the `TX_INHIBIT_n` conductor. SD-EMC-6 accepts it, on condition
    of a hardware EMCON lamp on board C. That adds a lamp, a gate and a FET to board C and one light-guide hole to the
    face plate. In BLACKOUT the lamp is dark, as every emissive indicator is.

  The physical proof is twelve bench tests (section 6). None of them can use the kit's own SDR, because EMCON removes
  the SDR's supply.

## 1. Evidence base

### 1.1 Netlists read

Boards C, E and P are read at main. Boards A, B and D are read at their round-6 candidates, which were in review when
this file's first three versions were written. Main merged them in `458b2873` (16:48 CEST), and they equal the copies
read here (below). The A and D candidates are filed in
`v2/docs/records/rv-emc/netlists/` with `SHA256SUMS`; the B candidate is rebuilt by command N1 and main's six are in git at the commits `v2/docs/records/README.md` names. This stream did not regenerate: each candidate's author regenerated on the build
host with parity against the committed files, and the provenance sidecars below name the generator that wrote each one.

| Board | Netlist | sha256 (first 16) | Generator | State |
|---|---|---|---|---|
| A | r4a round 6, `drafts/box/fixup3-run2/x6main/pcb-a-power.net` (written on main `faf8c981`, 12:04 UTC; filed as `v2/docs/records/rv-emc/netlists/A-r6cand-pcb-a-power.net`) | `e7c50a4f212a510a` | `gen_sch_a.py` sha256 `17c204ad4fb0cddb`, sidecar `eb0a7ee75f73015b` | candidate; merged on main in `458b2873` |
| B | r4b round 6 integration tree, `drafts/box/r6-run6/tint/regen/pcb-b-compute.net` (on `faf8c981`, 11:15 UTC; rebuilt by command N1 of `v2/docs/records/README.md`) | `af8a9186f981210c` | `gen_sch_b.py` sha256 `6e3d880901fd3030`, sidecar `ffaaf9606f526757` | candidate; merged on main in `458b2873` |
| C | main, `v2/ecad/pcb-c-display-c8/out/pcb-c-display.net` | `2834f0d8c4071d56` | sidecar `f917034bde25de83` | merged in `faf8c981` |
| D | r6d round 6, `drafts/box/run/new/pcb-d-aprs.net` (on `faf8c981`, 12:12 UTC; filed as `v2/docs/records/rv-emc/netlists/D-r6cand-pcb-d-aprs.net`) | `9aae5bf93a104abc` | `gen_sch_d.py` sha256 `08a7c08f0f13a71d`, sidecar `e410df300bb6b57a` | candidate; merged on main in `458b2873` |
| E | main, `v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net` | `d910e49c5f5f50b2` | sidecar `51c527e30704671d` | merged |
| P | main, `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` | `3c925191447136ac` | sidecar `0a73ba784f3d409d` | merged; changed on main in `d90f30e4` (3 nets, 5 parts, no radio; below) |

Board D was regenerated after the first version of this file (r6d `drafts/box/run/new/pcb-d-aprs.net`, 12:53 UTC,
sha256 `88aee4e209809f9e`, rebuilt by command N2 of `v2/docs/records/README.md`) with generator `39c5713b`, whose code lines equal `08a7c08f` (only comments changed, r6d
`v2/docs/records/r6d/r6-decisions.md` header). Its netlist differs from the copy read here in the `(date ...)` line alone (`diff`,
15:08 CEST), so every board D citation below stands on either file.

Board A took a fourth fix-up after this file's second version: r4a's final regeneration is now
`drafts/box/fixup4-run3/x6main/pcb-a-power.net` (sha256 `f0258b5ba24d21f0`, generator `a0452054`, rebuilt by command N3 of `v2/docs/records/README.md`), for the front end's
restart guard (r4a R4A-N15). The round-6 integration tree (`r6int`, netlists written 16:08 and 16:29 CEST) carries it.
Compared net by net and part by part with the copies read here (16:43 CEST,
`v2/docs/records/rv-emc/readings/candidates-vs-r6int-1629.txt`):
- the integrator's B, C and D are identical in every net and every part value;
- the integrator's A differs in 16 nets, all of them the front end's (`FE_*`, `VBUS20`, `VIN_RAW`, `GND` and three
  U34 no-connects), and in 24 parts on those nets. `R14` and `C7` sit on `FE_UVS`, `FE_SS` and `VIN_RAW`.

No net or part this file cites moved, so every board A citation stands. Its line numbers are those of the copy in
`v2/docs/records/rv-emc/netlists/`.

**Merged on main, `458b2873` (16:48 CEST).** Main then took boards A, B and D's round-4 and round-6 corrections.
Compared net by net and part by part with the copies read here (17:15 CEST, `git show 458b2873:<path>`,
`v2/docs/records/rv-emc/readings/candidates-vs-main-458b2873.txt`, tool `v2/docs/records/rv-emc/tools/netcompare.py`):
- main's B, C and D equal them in every net and every part value;
- main's A differs in the same 16 front-end nets and 24 parts as the integration tree's (above).

`netcompare.py` compares each net's set of (ref, pin) nodes and each part's value string. A footprint or pin-type
change would pass it unseen. That is enough for the claim made here, that no net or part this file cites moved; a
reuse for any wider claim has to add those fields.

Main's generators at `458b2873` are byte-identical to the ones cited here: A `a0452054`, B `6e3d8809`, C `5f1ce2dd`, D
`39c5713b` (sha256, first 8). So every citation stands on main, and no row rests on an unmerged candidate any more.

**Main at `b69f20db` (17:21 CEST), re-checked at 18:14 CEST** (`v2/docs/records/rv-emc/readings/main-b69f20db-drift.txt`). That commit
records the case margins (`CASE-MARGINS.md`) and changes no netlist and no generator: the four generators still hash to
the values above (`git show b69f20db:<path> | sha256sum`). `PANEL.md`, `TEST-PLAN.md`, `pcb_rules.yaml`, the review, the
vendor folders cited here and the C, E and P netlists are unchanged from `1f614233` (`git diff --stat`). It does change
`CONOPS.md`. Section 4b moved down 14 lines with its text unchanged (`:294` to `:319`, was `:280` to `:305`; `diff` of
the two ranges is empty), and section 2a now records SC-02 (`:104` to `:116`). The CONOPS citations below are to main at
`b69f20db`.

**Main at `ccf5808e` (18:13 CEST), checked at 18:25 CEST.** Six more commits landed while this version was written
(`26e847bc` to `ccf5808e`: current evidence, ZEROIZE, the failover fabric, decision 42, the review packets). They
change none of the files this document cites: `git diff --stat b69f20db ccf5808e` over the generators, the netlists,
`PANEL.md`, `TEST-PLAN.md`, `CONOPS.md`, `pcb_rules.yaml`, the review and the cited vendor folders is empty for every
modified file (`v2/docs/records/rv-emc/readings/main-ccf5808e-drift.txt`). They add sheets to `v2/vendor/`, and some are now cited
from there: the JSCJ 2N7002 (section 1.2, the same bytes as r4b's copy), and in L4 the LVC single gates that r6d and
r4t had cited by document number, among them the SN74LVC1G04, whose Ioff row this version reads. The new
`FAILOVER-FABRIC.md` agrees with section 4.5: slot 2's card buck runs "on `PCIE_PWR_EN2` alone"
(`v2/docs/feasibility/FAILOVER-FABRIC.md:348`).

**Main at `01469100` (18:25 CEST), checked at 18:28 CEST** (`v2/docs/records/rv-emc/readings/main-01469100-drift.txt`). Two more
commits: `d90f30e4` restores board P's secondary over-temperature, and `01469100` is a plan checkpoint. Of the cited
files only board P's netlist changed: 3 nets (`TS_SEC`, `TS_SEC_J`, `GND`) and 5 parts (the thermistor socket
`J_TS2`, R33, R34, TP15 and U2's value text), none of them a radio. So section 4.18's census for board P stands.
The generators and every other cited file are as at `ccf5808e`.

Main's A23, B19 and D9 netlists from before `458b2873` (`faf8c981`) are also copied for contrast, as
`drafts/netlists/main-*` (the same bytes as the commits `v2/docs/records/README.md` names). Those A and B are the state adjudication A11 read on 25 September: no hardware path to the CM5 radios, and W_DISABLE1# only on the WiFi cards. Main's D, regenerated in
`faf8c981`, still has the push-pull SA868 PTT driver and the Q6 and Q7 read-back paths that r6d replaces. `CONOPS.md`
section 4b describes main before `458b2873`, not the candidates.

Netlist citations below are `file:line` in `v2/docs/records/rv-emc/netlists/` (B's candidate as N1 rebuilds it, main's C from git), the line being the net's `(net (code ...)` line
(`v2/docs/records/rv-emc/tools/netline.py`); the dumps behind every row are in `v2/docs/records/rv-emc/readings/`.

Generator citations `gen_sch_X.py:N` are line numbers in each board's current generator, re-checked line by line at
16:44 CEST: A in r4a's `gen_sch_a.py` `a0452054` (its fourth fix-up; the netlist copy read here was written by
`17c204ad`, and the two differ only in the front end, above); B in r4b's `6e3d880901fd3030`; C in main's at `b69f20db`
(`5f1ce2dd`, unchanged since `faf8c981`); D in r6d's `39c5713b`. A, B and D's are the files now on main (above). The
second version of this file cited board A and D lines of the earlier generators; r6d's comment-only edit moved board D's
cited lines by 25 or 26, and they are re-cited here.

**Other writers' records, and the state this text was read against** (read 15:00 to 15:19 CEST; re-read 16:39 to
16:43 CEST; cited by decision or item ID, not by line number, because these files are still being edited):

| Record | sha256 (first 16) | Modified (CEST) | State |
|---|---|---|---|
| r4t `drafts/r4-decisions.md` (tools; not kept at this hash, a later edition is filed as `v2/docs/records/r4t/r4-decisions.md`: see `v2/docs/records/README.md`) | `e5efdc619832e46a` | 15:43:16 | "final after ROUND 6'S THIRD PASS" (its header) |
| r4t `v2/ecad/tools/tx_inhibit.py` | `5aece264d2825251` | 15:37:32 | the file the r4t record's section 4 names as final and ties RF-002's evidence to |
| r6d `v2/docs/records/r6d/r6-decisions.md` (board D) | `959ee8c6b9bf4e66` | 15:01:11 | round 6 after two re-reviews (unchanged) |
| r4b `v2/docs/records/r4b/r4-decisions.md` (board B) | `27023b76fce3d48d` | 13:37:34 | round 6 (unchanged) |
| r4a `v2/docs/records/r4a/r4-decisions.md` (board A) | `2e5a0c20fc9d4f25` | 15:41:01 | round 4 fourth fix-up (front end only, above) |
| i1 `v2/ecad/tools/pcb_requirements.yaml` (registry, pending merge) | `9389d2960ce3d49c` | 02:26:58 | pending merge (unchanged) |

The second version of this file read r4t at `1e3fe2800c3b33db` (14:55:01), whose header then said "final after round
6's second pass", with the tool at `e88aa46be6fe4305`. r4t's third pass (R4T-F14, R4T-D41) changed how the tool reads
a reader's supply, and corrected R4T-D37 and R4T-D39 in place for a reader whose supply net has no leading '+'. R4T-F14
records that every reader of an asserted line is on a '+' rail (A U26 +3V3; B U19 and U20 +3V3_DEV; D U12 +3V3_D8), so
nothing this file takes from those two moves. The statements and figures quoted below from R4T-D29, D30 (amended),
D32, D36, D38, D40, F5, F8 (third statement), F9 and F12 were re-read in the third-pass record and stand. r4t records
that the third-pass tool's output on the six netlists at main is byte-identical to `e88aa46b`'s, and it re-ties
RF-002's evidence to the third-pass file.

### 1.2 Maker documents

Held in `v2/vendor/` (sha256 first 16; full values in `v2/docs/records/rv-emc/datasheets/SHA256SUMS` for fetched files and by
`sha256sum` on the vendor paths). Page numbers below are the printed page numbers in each document's footer.

| Document | Path | Revision | sha256 |
|---|---|---|---|
| Quectel RM520N Series Hardware Design | `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` | v1.1, 2023-03-16 | `2bae882148b45172` |
| Quectel RM520N-GL Hardware Design | `v2/vendor/quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf` | v1.0, 2022-07-15 | `139583b38ce1fd47` |
| Quectel EG25-G Mini PCIe Hardware Design | `v2/vendor/lte/quectel-eg25-g-mini-pcie-hardware-design-v1.0.pdf` | V1.0, 2019-01-03 | `1da4b73b676b7b54` |
| Raspberry Pi CM5 datasheet | `v2/vendor/cm5/cm5-datasheet.pdf` | release 3, build 08/06/2026 | `80070fefd8db6e8a` |
| AsiaRF AW7915-AED datasheet | `v2/vendor/wifi/asiarf-AW7915-AED-datasheet.pdf` | "Last Updated: 04/22/2026", one page | `babcddfd36fe3655` |
| NiceRF SA868 datasheet | `v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf` | Rev 1.3 | `938ef5ef5007df6b` |
| Mitsubishi RA30H1317M1 | `v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf` | as held | `9fda757ab1acfb6b` |
| QRP Labs QMX operating manual | `v2/vendor/qrp-labs/qmx-operating-manual-1_04_004.pdf` | firmware 1_04_004 | `7d2616cdcadd2f7c` |
| Ground Control RockBLOCK 9704 schematic | `v2/vendor/rockblock/rb9704-sch-2B1.pdf` | rev 2B | `8151ea31acd15568` |
| Ground Control RockBLOCK 9704 datasheet | `v2/vendor/rockblock/rb9704-datasheet-RB9704-001-JUN26.pdf` | RB9704-001-JUN26 | `d48acbea28ee2a7d` |
| Ebyte E22-900M30S user manual | `v2/vendor/lora/ebyte-e22-900m30s-user-manual-en-v1.20.pdf` | v1.20 | `d864e9ca390f15c9` |
| Ebyte E72-2G4M20S1E user manual | `v2/vendor/zigbee/ebyte-e72-2g4m20s1e-user-manual.pdf` | 1.1, 2021-02-20 | `4bae5b3e67483b0b` |
| TI LM5176 | `v2/vendor/ti/lm5176-datasheet.pdf` | SNVSAI1D | `98191bec36d43771` |
| TI TPS2596 (TPS259631) | `v2/vendor/power/tps2596.pdf` | SLVSET8A | `66f6bae4494f7bfe` |
| TI TPS22810 | `v2/vendor/ti/ti-tps22810-load-switch.pdf` | SLVSDH0C | `10450eedecbc4542` |
| TI SN74LVC08A | `v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf` | SCAS283W | `9cefbf42c72e4aff` |
| TI SN74LVC32A | `v2/vendor/ti/ti-sn74lvc32a-quad-or.pdf` | SCAS286U | `807f6fff79777360` |
| Diodes AP64500 | `v2/vendor/diodes/diodes-ap64500.pdf` | DS41979 Rev 5-2 | `d3bcdc7dd4ca44cb` |
| Diodes PI7C9X2G404SL | `v2/vendor/diodes/diodes-pi7c9x2g404sl.pdf` | DS40068 Rev 5-2 | `675fa7ee40c91ad6` |
| TI PCA9555 | `v2/vendor/ti/ti-pca9555.pdf` | SCPS131J | `9b5cc24c3c9e286a` |
| Silicon Labs CP2102N | `v2/vendor/silabs/silabs-cp2102n.pdf` | Rev. 1.5 | `32fbab0ba17f3945` |
| Raspberry Pi RP2040 datasheet | `v2/vendor/rp2040/rpi-rp2040-datasheet.pdf` | as held | `be56fbb75ba0ae9e` |
| JSCJ 2N7002 (LCSC C8545) | `v2/vendor/power/jscj-2n7002-c8545.pdf` on main since `ccf5808e` (SOURCES.yaml `logic-nfet-2n7002`); first read as r4b `drafts/datasheets/cj-2N7002_C8545.pdf`, the same bytes | as held | `7941fb423af7c6c6` |

Fetched by this stream on 26 September 2026 and kept in `drafts/datasheets/` of `fnd/rv-emc`, listed for `v2/vendor/` in `v2/docs/records/README.md` (full sha256 in `v2/docs/records/rv-emc/datasheets/SHA256SUMS`, URLs
and fetch dates in `v2/docs/records/rv-emc/datasheets/SOURCES.txt`):

| Document | URL | Revision | sha256 (first 16) |
|---|---|---|---|
| Quectel RG520N&RG525F&RG5x0F&RM5x0N&RM521F Series AT Commands Manual | https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6382/Quectel_RG520NRG525FRG5x0FRM5x0NRM521F_Series_AT_Commands_Manual_V1.0.pdf | V1.0, 2024-02-07, Released | `6ed74e7e61da5521` |
| Quectel RG520N&RG52xF&RG530F&RM520N&RM530N Series AT Commands Manual | https://files.waveshare.com/upload/8/8a/Quectel_RG520N&RG52xF&RG530F&RM520N&RM530N_Series_AT_Commands_Manual_V1.0.0_Preliminary_20220812.pdf | V1.0.0, 2022-08-12, Preliminary | `0e940dbc5957dbda` |
| Quectel EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual (hosted by Sixfab) | https://sixfab.com/wp-content/uploads/2023/11/Quectel_EC2xEG2xEG9xEM05_Series_QCFG_AT_Commands_Manual_V1.1.pdf | Version 1.1, 2023-06-27, Released | `0280b1af1cfa627e` |
| Quectel RG50xQ&RM5xxQ Series AT Commands Manual (Quectel forum upload) | https://forums.quectel.com/uploads/short-url/avUSxfJeKqWJzAie8wEZCshlXjm.pdf | Version 1.1.1, 2020-10-09, Preliminary | `ef90013314f828b8` |
| QRP Labs, Schematics for QMX PCB Rev 5 | https://qrp-labs.com/images/qmx/manuals/schematics_rev5.pdf | PDF created 2025-11-20 | `83e911e666e6cfba` |
| QRP Labs, Schematics for QMX PCB Rev 3/Rev 4 | https://qrp-labs.com/images/qmx/manuals/schematics_rev3.pdf | PDF created 2024-03-06 | `6a1072939603ea9b` |
| QRP Labs, Schematics for QMX PCB Rev 2 | https://qrp-labs.com/images/qmx/manuals/schematics_rev2.pdf | as served | `36a1941918e59e59` |
| QRP Labs, Schematics for QMX PCB Rev 1 | https://qrp-labs.com/images/qmx/manuals/schematics_rev1_a.pdf | PDF created 2023-07-09 | `11be4f699e85f039` |
| QMX Rev 1 searchable schematic (G4GIR, hosted by QRP Labs) | https://qrp-labs.com/images/qmx/manuals/QMX_Rev1_Searchable_Schematic_1b.pdf | 1b, 2025-02-17 | `dd7c32c85ffc2586` |

The QMX schematics are image-only PDFs; they were read from renders, and the crops that carry the reading are kept in
`drafts/datasheets/qmx-crops/` of `fnd/rv-emc` (listed for `v2/vendor/` in `v2/docs/records/README.md`). Re-read from adjudication A11's fetch of 25 September 2026 and re-fetched here with
identical sha256: Linux `torvalds/linux` at `f14572c203d57492e1d4e5d7851a3b143e083b82`,
`drivers/net/wireless/mediatek/mt76/mt7915/mcu.c` (`e3cc6c75c355e7e2`) and `mt7915/mt7915.h` (`b11e1fc5910e4a70`),
and the MyriadRF LimeSDR Mini 2.0 page (https://myriadrf.org/projects/limesdr-mini-2-0, A11's copy `f1146105a3c09ebc`).
The two LTE and RM5xxQ manuals are Quectel documents served from a distributor's and from Quectel's forum host; they are
used here only as precedent for how Quectel firmware treats W_DISABLE#, never as a statement about the RM520N-GL.

### 1.3 Tool reading (informational)

`tx_inhibit.py`, the RF-002 instrument in the unmerged tools round, was run in its final r4t form (sha256
`5aece264d2825251`, round 6's third pass) on the candidate set above, in 0.41 s on the runner (16:40 CEST):
`v2/docs/records/rv-emc/readings/tx_inhibit_r4t-5aece264_on_candidate_set.txt`. Its output is byte-identical to the second version's
reading with `e88aa46b` (`v2/docs/records/rv-emc/readings/tx_inhibit_r4t-e88aa46b_on_candidate_set.txt`, which differs only in the
timing lines appended to it); the first version's reading with `853f3082` is kept beside them. It reads the `EMCON_HW` line FAIL (the firmware pins of L1; the bound is 3.46 V with rails 5 percent high,
R4T-D36), the `TX_INHIBIT_n` line PASS, the SA868 UNDECIDED (it now follows the open-drain release, R4T-D38: 2.85 V and
2.86 V from the known currents, no maker threshold), every other transmitter FAIL on the line or on a part it does not
model (L6), and board B's census UNDECIDED on `J_QMX` alone. Part of that is real and part is the tool's model, so its
verdict does not decide this table.

## 2. The two EMCON lines on the candidates

Both lines are LOW when EMCON is asserted.

- **Source.** `SW_EMCON` on board C, an APEM 5636ADKB-2V locking toggle, single pole ON-NONE-ON (lug 1
  `TX_INHIBIT_n`, lug 2 GND, lug 3 unconnected; `gen_sch_c.py:115` to `117`, `:211`). Closed pulls `TX_INHIBIT_n` low
  against R14 (10 k to C's +3V3) and C24 (10 nF) (`gen_sch_c.py:150`; `main-pcb-c-display.net:4113`).
- **`TX_INHIBIT_n` is one conductor across four boards and three ribbons:** board C (R14, C24, TP10, U9's input) to
  `J_PANEL` pin 11, board B (R59), `J_AB1` pin 16, board A (R145), `J_MEZZ1` pin 8, board D (R2, U12 pin 2)
  (`main-pcb-c-display.net:4113`, `B-r6cand-pcb-b-compute.net:22317`, `A-r6cand-pcb-a-power.net:10816`,
  `D-r6cand-pcb-d-aprs.net:4514`). Its neighbours on the flat cables are `ZEROIZE_HW` and `HDMI_SEL1` (panel ribbon
  pins 10 and 12), `EMCON_HW` and `SLOT_EN1` (`J_AB1` pins 15 and 17), `TR_APRS` and `PA_EN` (`J_MEZZ1` pins 7 and 9)
  (`v2/docs/records/rv-emc/readings/tx-inhibit-conductor.txt`).
- **`EMCON_HW`** follows through U9, a 74LVC1G17 Schmitt buffer on board C (`gen_sch_c.py:166`;
  `main-pcb-c-display.net:3702`), and runs over `J_PANEL` pin 8 and `J_AB1` pin 15 to boards B and A. It is derived
  from the `TX_INHIBIT_n` node, so the two lines are not independent upstream of U9.
- **Pull-downs that assert the lines with the source gone:** `TX_INHIBIT_n` has 100 k on A (R145), B (R59) and D (R2).
  `EMCON_HW` has B's R58 at 10 k (candidate) and A's R102 at 100 k (`B-r6cand-pcb-b-compute.net:19944`,
  `A-r6cand-pcb-a-power.net:9736`).
- **Hardware readers of `EMCON_HW`:**
  - A's U26 pins 1 and 4 (SN74LVC08A);
  - B's U19 pins 1, 9, 12 and U20 pin 1 (SN74LVC08A);
  - B's Q11 gate, a JSCJ 2N7002 that inverts it into `EMCON_ON` with R513 (10 k to +3V3_DEV) (`gen_sch_b.py:1029`;
    `B-r6cand-pcb-b-compute.net:19957`).
- **Firmware readers of `EMCON_HW`:** B's U41, U51, U61 pin 33 (PC5 of the three STM32H743 supervisors) and C's U3 pin
  32 (RP2040 GPIO21). See L1.
- **Readers of `EMCON_ON`:** Q106, Q206, Q306 (open drains onto the three M.2 W_DISABLE1# pins); Q111 and Q311 (pull
  the two WiFi card buck enables low); U111, U211, U311 pins 2 and 5 (the CM5 radio kill ORs, SN74LVC32A).
- **Reader of `TX_INHIBIT_n`:** D's U12 pin 2, the KEY gate.

## 3. Shared items on the lines

Every row that depends on `EMCON_HW` inherits L1 to L4, and every row that depends on `EMCON_ON` also inherits L7. The
PA's path (b) and the SA868 depend on `TX_INHIBIT_n` only, which the tool reads PASS in every fail-safe state
(`v2/docs/records/rv-emc/readings/tx_inhibit_r4t-5aece264_on_candidate_set.txt` line 3).

Read against the r4t record at sha256 `e5efdc619832e46a` ("final after ROUND 6'S THIRD PASS") and its tool at
`5aece264d2825251` (section 1.1 says what the third pass changed). The r4t figures were taken on main `faf8c981` with remedies applied in memory, not on the r4b
candidate, which carries Q11 on `EMCON_HW` in place of main's three level shifters; where that matters it is said.

| Id | Item | Status | Bound and evidence | Owner and remedy |
|---|---|---|---|---|
| L1 | Four firmware-direction pins sit on `EMCON_HW`: B's U41, U51, U61 pin 33 (PC5) and C's U3 pin 32 (GPIO21). A pin set as an output by a firmware error fights U9 while EMCON is asserted, and with the panel unpowered it lifts the line against the pull-downs. | OPEN | The tool bounds the panel-unpowered state at 3.46 V against the gates' 0.8 V VIL (tool output line 2). In reset both parts are benign: the STM32 pin is analog with no pull (r4b O-06, DS12110). The RP2040 pad resets with its input and pull-down enabled (RP2040 datasheet, section 2.19.6.3, Table 341: IE 0x1, PDE 0x1), and no function drives its output: GPIOx_CTRL's FUNCSEL resets to 0x1f, "31 == NULL" (section 2.19.6.1, Table 285); the processors drive a pin only through the SIO function (section 2.19.2, Table 280), whose output enable resets to input (section 2.3.1.7, Table 24, GPIO_OE reset 0). Table 341's OD bit resets to 0x0, which leaves the output enable to the selected function; it does not disable the output. The failure is a running firmware that sets the pin as an output. | Buffers only. The series-resistor tap the first version of this file offered is withdrawn by R4T-D40: an unpowered supervisor or RP2040 pin passes a current no held sheet states, so any tap leaves the line UNDECIDED. Board B author: one 74LVC1G34 for the three PC5 pins (R4T-F8 third statement, R4T-D40). Board C author: U3's GPIO21 behind a 74LVC1G34 on the panel's +3V3 (R4T-F5, R4T-D40). |
| L2 | The line's hold when its source is gone (panel unpowered or unplugged, `J_AB1` unplugged, one board's rail down while another board's gate reads the line). | OPEN | **As drawn: UNDECIDED.** A's U26 and B's U19 and U20 are SN74LVC08A, whose sheet has no Ioff row (SCAS283W; R4T-D29), and B's Q11 gate is the JSCJ 2N7002, whose IGSS is stated at 25 C only (sha `7941fb42`; R4T-D29). Board A alone with `J_AB1` unplugged holds the line with R102 (100 k) alone: 10 uA into 100 k is 1.0 V, above 0.8 V (r4b O-08). **The r4t arithmetic with the remedies** (R4T-F8, third statement, by R4T-D36 and R4T-D37): with one SN74LVC1G08 per `EMCON_HW` input, 10 k on both boards FAILS at 1.00 V (`J_AB1` unplugged, panel unpowered, one slot rail up) and at 0.96 V with 1 percent parts; R102 10 k 1% with R58 4.7 k 1% PASSES, worst 0.45 V. The round-6 statement "10 kOhm on BOTH boards, every state passes", which the first version of this file cited, is withdrawn by that third statement and by R4T-F12. The candidate B's own sum (Q11's gate instead of the in-memory 74LVC1G07s) is not yet taken. | Board A author: R102 10 k 1%, and two SN74LVC1G08 in place of U26's two `EMCON_HW` sections (R4T-F8 third statement). Board B author: R58 4.7 k 1%, one SN74LVC1G08 per `EMCON_HW` input in place of U19's three sections and U20's one (R4T-F8 third statement); Q11's gate bounded by a sheet that states IGSS over the envelope, or Q11 replaced by a part whose input current is stated; the candidate's own sum by R4T-D37's method. |
| L3 | Loss of +3V3_DEV on B while a slot runs. | OPEN | Two consequences. (1) **Fail-open, by construction:** R513 no longer holds `EMCON_ON` high, so the six CM5 kills, the three W_DISABLE1# open drains, the two card-supply pull-downs, and SD-EMC-1's two new stages once built, all release (r4b O-14 and SD-B-14; R4T-F9's CM5 bullet: an open-drain element fed from a carrier rail FAILS with that rail down). (2) **The eFuse and load-switch enables** `LIME_EN`, `RB_EN`, `E22_EN`, held by R514 to R516 (10 k) while their gate U19, an SN74LVC08A, is unpowered: UNDECIDED, 0.00 V from the known currents but no Ioff row (R4T-F9, R4T-D29); PASS once each gate is an SN74LVC1G08 (0.10 V against the 1.08 V off level, R4T-F9). The first version of this file called state (2) safe; that is withdrawn. `E72_EN` PASSES: U22's input is +3V3_DEV itself (R4T-D30, R4T-F9). | Board B author: O-14's remedy, an `EMCON_ON` source that does not share +3V3_DEV, or per-slot elements run from each module's own 3.3 V output (R4T-F9's CM5 bullet); the single-gate SN74LVC1G08s of L2 also close (2). |
| L4 | Gate supplies outside the LVC families' specified range, where the outputs are unspecified. | OPEN | Two cases. (1) **Parts with no Ioff row**, unspecified from 0 V up to 1.65 V because nothing specifies them for partial power down (R4T-D29): A's U26 and B's U19 and U20 (SN74LVC08A, SCAS283W), and B's U111, U211, U311 (SN74LVC32A, SCAS286U: no Ioff row either). This is why state (2) of L3, +3V3_DEV at 0 V, is UNDECIDED. (2) **Parts that state Ioff**, specified at 0 V (output high-impedance) and unspecified above 0 V and below 1.65 V: D's U9, U10, U12, U14 (TECH PUBLIC C19829591, IOFF 10 uA, r6d R6D-6), U13 (TI SN74LVC1G06, SCES295AB Ioff, R6D-5), U18 to U20 (Diodes 74LVC1G34, DS36108 IOFF, R6D-1), C's U9 (Diodes 74LVC1G17, DS35124 IOFF, R4T-D33), and D's U11 (TI SN74LVC1G04, SCES214AF section 5.5: Ioff ±10 uA at VCC 0, VI or VO 5.5 V; r6d R6D-5, "NOT PROVEN: above 0 and below 1.65 V"). These sheets are filed on main since `ccf5808e` (`v2/vendor/techpublic/`, `v2/vendor/ti/ti-sn74lvc1g04.pdf`, `ti-sn74lvc1g06.pdf`, `v2/vendor/diodes/diodes-74lvc1g17.pdf`, `diodes-74lvc1g34.pdf`, and `v2/vendor/SOURCES.yaml`); U11's row was read there for this version. An output in the band at up to its own 1.65 V supply would sit above the LM5176's 1.17 V minimum operating threshold (SNVSAI1D, VEN(OP)) and the eFuses' 1.22 V maximum rising threshold (SLVSET8A, VUVLO(R)). | Board B author (O-24, with O-14; the SN74LVC1G08s of L2 move U19 and U20's sections into case (2)); board D author and bench rows E-01, E-11; board A author for U26 (the same SN74LVC1G08s). |
| L5 | Slow edges: `EMCON_ON` asserts as an RC edge (tau about 3 us) into the SN74LVC32A's 7 ns/V limit (r4b O-23); `TX_INHIBIT_n` releases with R14 and C24 into D's non-Schmitt U12 (r6d R6D-N1). | CLOSED for the inhibit | Both settle in the inhibit direction on assert; the U12 chatter happens only on release, while a PTT is held (r6d R6D-N1 also records a transient re-key during contact bounce on assert, not a steady-state bypass). Kept as circuit items O-23 and R6D-N1, not as EMCON blockers. | Board B and D authors (hygiene) |
| L6 | The RF-002 instrument (`5aece264`, whose output here equals `e88aa46b`'s) does not yet model: the Q11 inverter feeding the `EMCON_ON` open drains; a socket rail fed through a Kelvin shunt (R165, R265, R365); the SN74LVC32A OR; the TLV75801P enable (the walk stops at D's U15 pin 4). Its PA entry has no option for the gate bias and keying on board D, which is the path that closes row 2 (r4t section 5 carries the VGG semantics, R4T-D10, as open). `J_QMX` is declared OWED. Modelled since the first version of this file: an open-drain output EMCON releases (R4T-D38), which is why the SA868 now reads UNDECIDED rather than FAIL. | OPEN (tool) | Tool output lines 4 to 37 give each transmitter's reason and lines 45 to 53 each stop of the walk. Section 4.3 answers `J_QMX`'s OWED with QRP Labs' own schematics. | Tools author (r4t) |
| L7 | Every FET on `EMCON_ON` is the JSCJ 2N7002 (LCSC C8545): Q11, Q106, Q206, Q306, Q111, Q311, and Q109, Q110, Q209, Q210, Q309, Q310. The sheet (sha `7941fb42`) states every characteristic at Ta 25 C only: Vth(GS) 1.0 to 2.5 V at 250 uA, and RDS(on) at VGS 10 V (500 mA) and 5 V (50 mA). Its "Typical Characteristics" page also draws output curves at VGS 3 V and 4 V, at Ta 25 C and pulsed; they are typical curves, not limits, so they do not bound the channel at 3.3 V over the envelope. The gates are driven at about 3.3 V (R513 to +3V3_DEV, or U{s}11's outputs). | OPEN | On the tools author's own rules, a FET held on below the VGS its RDS(on) is stated at is UNDECIDED, and a FET held off below the 25 C Vth minimum is not proved off over the envelope (R4T-D30 amended (a), R4T-D32). The loads are small (a CM5 pin's 1.8 kOhm pull-up, 1.8 mA; W_DISABLE1#, about 0.35 mA, r4b part table for Q106 to Q306; an AP64500 enable, microamps), but the channel resistance at VGS 3.1 to 3.5 V is TBD. Its effect: that each pin reaches its low level is not proved at desk for rows 5 to 13. The r4b part table records the 3.3 V drive without a bound. | Board B author: a logic-level N-channel part whose held sheet states RDS(on) at VGS 2.5 V or less over -40 to +85 C, or an open-drain LVC buffer (74LVC1G07, whose VOL is stated at IOL over temperature), or a held 2N7002 sheet that states the 3.3 V figures. Bench E-07 and E-08 record the pin levels. |

## 4. The table

"Gate" is the radio-specific hardware chain. "Back-feed" asks whether anything that stays powered can raise the radio's
supply while its gate is off. "Shared" lists the section 3 items the row inherits.

| # | Transmitter (board, ref) | Hardware inhibit | Gate | Back-feed | Shared | Status |
|---|---|---|---|---|---|---|
| 1 | SA868 VHF exciter (D, U2) | PTT forced to "receive" by `TX_INHIBIT_n`; supply kept (D-05) | OPEN: no maker "1" level (tool UNDECIDED) | not applicable | L4 (D) | OPEN |
| 2 | RA30H1317M1 30 W PA (plate; A `J_PA`, D `J_VGG`) | (a) drain rail off (A); (b) gate bias off, relay at rest (D) | CLOSED at desk on (b) in RF-002's states; (a) a second path | not applicable (see 4.2) | common element `SW_EMCON` and `TX_INHIBIT_n` (SD-EMC-6: accepted on condition of a hardware EMCON lamp on C, not yet drawn); (a) also L1, L2, L4 (A) | CLOSED at desk; single-fault tolerant only downstream of `TX_INHIBIT_n` |
| 3 | QMX HF (lid; A `J_HF`, B `J_QMX`) | DC input rail off | CLOSED at desk | CLOSED: USB VBUS not connected inside the QMX | L1, L2, L4 (A) | OPEN on L1, L2, L4 |
| 4 | RockBLOCK 9704 (B, `J_RB9704`) | eFuse off | CLOSED at desk | OPEN | L1, L2, L3, L4 | OPEN |
| 5 | RM520N-GL 5G (B, `J_M2C2`, M.2 key B) | as drawn: W_DISABLE1# low (firmware-mediated airplane mode), supply kept. Required by SD-EMC-1: if EMCON asserts before the module has been turned on (every power-up under EMCON), FULL_CARD_POWER_OFF# low and supply removed at once, so the module is never powered under EMCON; on a module that has been turned on, in the maker's order: W_DISABLE1# at once, FULL_CARD_POWER_OFF# by hardware after T_off (sized for the host's AT+CFUN=0 handshake), supply removed after a further T_cut, whether or not the module is booting or restarts meanwhile (the booting case) | OPEN: circuit owed on B | OPEN once the supply is removable | L1, L2, L3, L7 | OPEN |
| 6 | AW7915-AED, slot 1 (B, `J_M2C1`) | card buck off (and W_DISABLE1# low, not counted) | CLOSED at desk | OPEN (small, one term TBD) | L1, L2, L3, L7 | OPEN |
| 7 | AW7915-AED, slot 3 (B, `J_M2C3`) | as row 6 | CLOSED at desk | OPEN (as row 6) | L1, L2, L3, L7 | OPEN |
| 8 to 10 | CM5 WiFi, slots 1 to 3 (B, U30A, U31A, U32A pin 89) | `WL_nDisable` pulled low by an open drain | CLOSED at desk | not applicable | L1, L2, L3, L4, L7 | OPEN |
| 11 to 13 | CM5 Bluetooth, slots 1 to 3 (pin 91) | `BT_nDisable` pulled low by an open drain | CLOSED at desk | not applicable | L1, L2, L3, L4, L7 | OPEN |
| 14 | E22-900M30S LoRa (B, U12) | load switch off | CLOSED at desk | OPEN | L1, L2, L3, L4 | OPEN |
| 15, 16 | E72 CC2652P Zigbee and Thread (B, U13, U14) | load switch off | CLOSED at desk | OPEN | L1, L2 | OPEN |
| 17 | LimeSDR Mini 2.4 (B, `J_LIME`) | eFuse on its USB VBUS off | CLOSED at desk | CLOSED: bounded | L1, L2, L3, L4 | OPEN on the shared items |

### 4.1 SA868 VHF exciter (board D, U2)

- **Physical control.** `KEY = PTT_ANY AND TX_INHIBIT_n` in U12, a 74LVC1G08 (TECH PUBLIC C19829591)
  (`gen_sch_d.py:532`; `D-r6cand-pcb-d-aprs.net:4271`). U13, a TI SN74LVC1G06 open-drain inverter, pulls `SA_PTT_n` (U2
  pin 5) low only while KEY is high (`gen_sch_d.py:533`; `D-r6cand-pcb-d-aprs.net:4492`). Otherwise R88 (1.2 k from
  +5V_SA) and R89 (2.0 k to GND) hold the pin at 2.677 to 3.317 V, both ends including r6d's stand-in for U13's
  leakage (`gen_sch_d.py:346`; r6d R6D-2, R6D-5). The exciter's
  supply +5V_SA is not gated: D-05 keeps VHF listening.
- **Active level.** `TX_INHIBIT_n` LOW gives KEY LOW, U13 off, and pin 5 at the divider's level. The SA868 v1.3 pin
  table gives pin 5 as "0" TX and "1" RX, with no level stated for either.
- **Default.** `TX_INHIBIT_n` follows the toggle. With the panel unpowered or any ribbon cut, R2, R145 and R59 hold it
  low (tool: the `TX_INHIBIT_n` line PASS). R84 (10 k) holds KEY low against the gates' leakage when their own rail is at
  0 V: 0.43 V at most against U19's 0.8 V VIL, 0.51 V with the harness +3V3 down too (`gen_sch_d.py:592`; r6d R6D-3).
- **Controller failure.** No controller can drive KEY:
  - D's PCA9555 U16 reads KEY and PA_KEY through the one-way buffers U19 and U20 and 1 k (R86, R87);
  - board C's RP2040 sees the PTT mirror only through U18 and R48 (220 Ohm);
  - the CP2102N's software PTT enters ahead of U12 and is ANDed with `TX_INHIBIT_n`
  (`D-r6cand-pcb-d-aprs.net`, nets `X_KEY`, `X_PA_KEY`, `PTT_MIR`; `v2/docs/records/rv-emc/readings/D-nets.txt`). The r4t record's
  open item "KEY's readback and TR_APRS (R4T-F6) still fail the SA868" describes main's board D; on the candidate, r6d's
  R6D-1 removed those paths and the tool reads UNDECIDED, not FAIL.

  If U1, the +3V3_D8 regulator, fails, U13 is in Ioff and R88 and R89 alone set the pin. The rail back-fed to between
  0 V and 1.65 V is not specified by any held sheet (L4, case 2).
- **Powering and back-powering.** The exciter stays powered by design; no inhibit rests on its supply.
- **What the maker states.** Pin 5 "0" TX and "1" RX. The command set lists five instructions (DMOCONNECT,
  DMOSETGROUP, DMOSETVOLUME, RSSI, SETFILTER), none of which transmits. No VOX is documented. No input threshold, input
  current or internal pull is stated for pin 5.
- **Proof required.** Bench E-01: pin 5's "1" threshold and current, and the U1 fault states.
- **Status: OPEN.** The design holds pin 5 at 2.677 V or more in every specified state; whether 2.677 V reads as "1" is
  published nowhere. If E-01 finds the threshold above 2.677 V, the divider is re-ratioed; the cap is the 3.333 V the
  pin has always been driven with, which is this design's own ceiling, not an SA868 limit (r6d R6D-2).

### 4.2 RA30H1317M1 30 W VHF power amplifier (face plate)

- **Physical control, two paths.**
  - (a) Drain supply. `+13V8_PA` comes from the LM5176 U13 on board A. Its EN/UVLO is `PA_EN = EMCON_HW AND PA_SW_EN`
    (U26 gate 1), with R59 (10 k) to GND (`A-r6cand-pcb-a-power.net:10088`, `:9574`). Below VEN(STBY) (0.55 V minimum)
    the LM5176 is "held in a low power shutdown mode" (SNVSAI1D, section 7.3.3 and the electrical table).
  - (b) Gate bias and drive. On board D, `PA_KEY = KEY AND PA_EN` (U14), and KEY is forced low by `TX_INHIBIT_n`.
    `PA_KEY` low turns off the VGG regulator U15 (TLV75801P, EN pin 4) and Q2, the relay coil driver
    (`D-r6cand-pcb-d-aprs.net:4340`, `:4564`, `:4456`). The Omron G6K-2F-Y then rests with antenna joined to exciter
    (contacts 6-7 and 3-2, `gen_sch_d.py:597`, terminal arrangement read by A11 on the G6K sheet page 6), so the PA's
    input and output are both disconnected. The RA30H1317M1 is an enhancement-mode module: "IDD≅0 @ VDD=12.5V, VGG=0V",
    and output rises only around VGG = 3.5 V (datasheet, features and "Output Power Control"). Path (b) closes on U15
    alone: with EMCON asserted U14 drives `PA_KEY` low, and with D's gates unpowered R85 holds it at 0.11 V, both
    under U15's VEN(LO) of 0.3 V (r6d R6D-3, with the typical EN current SBVS351D gives and a 20 uA margin). So path (b)
    does not rest on the FET Q2.
- **Active level.** `EMCON_HW` LOW for (a); `TX_INHIBIT_n` LOW for (b).
- **Default.** `PA_SW_EN` is held low by R103 (4.7 k) until firmware sets it (`gen_sch_a.py:1112`); `PA_KEY` is held low
  by R85 (10 k).
- **The shared element.** Both paths start at the same operator contact and the same node: `SW_EMCON` pulls
  `TX_INHIBIT_n` low, and `EMCON_HW` is U9's buffered copy of that node (section 2). A fault there releases both paths
  at once. Examples: the contact fails to close (a worn contact, a broken lug joint, or the cover forcing the other lever
  position, which `gen_sch_c.py:207` to `209` leaves as an assembly item); the conductor held above VIL while the toggle
  is at EMCON, by a short to a supply or a driven neighbour that the contact's path does not overcome (the ribbon
  neighbours are listed in section 2). RF-002's named states are not among these: unpowered and disconnected, the
  pull-downs assert both lines. SD-EMC-6 accepts this element, on condition that board C gets an EMCON lamp driven
  from the lines' state with no processor in its path. As drawn, nothing indicates such a fault without firmware
  (SD-EMC-6).
- **Controller failure and single faults downstream of the `TX_INHIBIT_n` node.** Each leaves one path:
  - A's expander U27 dead: `PA_SW_EN` low, rail off (path (a) holds).
  - A's U26 unpowered: `PA_EN` sits at 0.07 V from the known currents but is UNDECIDED, because U26 states no Ioff and
    `PA_EN` also reaches D's Q1 gate over the harness, whose IGSS is stated at 25 C only (R4T-F9, R4T-D29). Path (b)
    holds.
  - A firmware pin on `EMCON_HW` (L1), or the line's hold (L2): path (a) only. Path (b) holds.
  - D's rail in the unspecified band (L4, case 2): path (b) only. Path (a) holds.
- **Powering and back-powering.** The drain rail is inhibited at its converter; the PA has no other supply. Whether the
  four-switch stage passes any VBAT to `+13V8_PA` in shutdown is not stated by the LM5176 sheet (INFERRED no, from the
  topology). It does not matter here, because path (b) alone leaves the PA with no bias and no drive.
- **Proof required.** Bench E-02, which now includes the shared-element cases.
- **Status: CLOSED at desk** on the candidates A and D, on RF-002's terms: path (b) is a hardware path with no firmware
  driver on `TX_INHIBIT_n` or KEY, asserted in the unpowered and unplugged states. Path (a) is a second path subject to
  L1, L2 and L4 (A). The row is single-fault tolerant only for faults downstream of the `TX_INHIBIT_n` node; `SW_EMCON`
  and that conductor are its common element. The physical proof E-02 is owed.

### 4.3 QMX HF transceiver (lid tray)

- **Physical control.** `+12V_HF` comes from the LM5176 U15 on board A. Its EN/UVLO is
  `HF_EN = EMCON_HW AND HF_SW_EN` (U26 gate 2), with R125 (10 k) to GND (`A-r6cand-pcb-a-power.net:9921`, `:9561`).
- **Active level.** `EMCON_HW` LOW gives EN below 0.55 V: shutdown.
- **Default.** `HF_SW_EN` is held low by R104 (4.7 k) (`gen_sch_a.py:1112`).
- **Controller failure.** U27 dead: off (R104). U26 unpowered: `HF_EN` at 0.03 V from the known currents, UNDECIDED
  because U26 states no Ioff (R4T-F9, R4T-D29). A firmware pin on `EMCON_HW` can enable it, and this radio has no second
  path (L1). With `J_AB1` unplugged, board A's line can read undefined (L2). U26 with its supply in the unspecified band
  is L4, case 1.
- **Powering and back-powering.**
  - The USB lead's `VBUS_QMX` is +5V_DEV through the 0.5 A polyfuse F3 and is not gated
    (`B-r6cand-pcb-b-compute.net:22459`; `gen_sch_b.py:959`).
  - QRP Labs' own schematics show the USB-C connector J201's VBUS pin with no connection, on every published PCB
    revision: Rev 1, Rev 2, Rev 3/4 and Rev 5 (page 2, `drafts/datasheets/qmx-crops/` of `fnd/rv-emc`, listed in `v2/docs/records/README.md`). In Rev 2 and later, CC1 and CC2
    carry 5.1 k to ground. Page 1 of Rev 5 (power supplies) derives +12V, VCC and VDD from V_IN at the DC jack J101 only.
    So VBUS does not power the QMX. This is VERIFIED from the maker's drawings, read from renders because the PDFs are
    images. It answers the tool's OWED item (R4T-D17), which asked for "a QRP Labs statement that USB VBUS does not power
    the QMX's transmitter".
  - D+ and D- go from hub U202 port 4 to the STM32's PA11 and PA12. A downstream hub port drives the pair only after a
    device signals attach with its own pull-up, which an unpowered QMX cannot do. That bound is INFERRED from USB 2.0
    attach behaviour; bench E-03 measures it.
  - Condition: the fitted unit's PCB revision is recorded at intake. A revision whose schematic is not among the four
    reopens the row.
- **What the maker states.** "The supply voltage range for QMX is 6.0 to 12.0V" (operating manual 1_04_004, DC
  connector); the USB-C port is described only as a sound card, serial port and bootloader drive.
- **Proof required.** Bench E-03.
- **Status.** The radio-specific chain is CLOSED at desk. The row is OPEN on L1, L2 and L4 (board A's U26).

### 4.4 RockBLOCK 9704 (board B, `J_RB9704`)

- **Physical control.** `+5V_RB` comes from U24, a TPS259631 eFuse on +5V_DEV. Its EN/UVLO is
  `RB_EN = EMCON_HW AND RB_SW_EN` (U19 gate 3), with R515 (10 k) to GND (`gen_sch_b.py:951`, `:1002`;
  `B-r6cand-pcb-b-compute.net:21545`, `:19456`). The FET turns off below VUVLO(F), 1.08 V minimum (SLVSET8A, electrical
  table). Pin 15 (V_EXT_RAW) is the module's only supply wired: pins 12 (V_BATT), 2, 5, 9 and 11 and the module's own
  USB-C are not connected (`v2/docs/records/rv-emc/readings/B-rb-lime.txt`; A11 read Ground Control's schematic rev 2B for the pin
  functions).
- **Active level.** `EMCON_HW` LOW gives `RB_EN` LOW: supply off.
- **Default.** `RB_SW_EN` is held low by R51 (4.7 k). The PCA9555 U6 powers up with every I/O an input (SCPS131J,
  description: "At power on, the I/Os are configured as inputs").
- **Controller failure.** U6 dead: off. +3V3_DEV lost: U19 unpowered and R515 holds `RB_EN`, UNDECIDED until U19's
  section is a part that states Ioff (L3, state (2); R4T-F9). L1, L2 and L4 apply.
- **Powering and back-powering.** Four sources stay live while +5V_RB is off:
  - `RB_IEN` (pin 3) and `RB_CTRL` (pin 6) from U6 on +3V3_DEV: push-pull when set as outputs, and the PCA9555's internal
    100 k pull-up when inputs (`B-r6cand-pcb-b-compute.net:21553`, `:21536`);
  - `RB_RXD` (pin 14) from U18's TXD, a CP2102N on +5V_DEV that is not gated (`:21559`);
  - `RB_STATUS` and `RB_XMTG` (pins 7, 8), pulled up by R41 and R42 (10 k) to +3V3_DEV.

  Ground Control's schematic rev 2B notes that the enable buffer behind J3 (a 74AUP1G125) "is POWERED from Iridium 3V3
  so it doesn't drive unless 9704 IO is powered". That covers the enable path only. How the UART transceiver and the
  other J3 pins behave with the module unpowered is not stated. Bound: TBD. Effect: whether a live host line can raise
  the modem's internal 3.3 V domain is unknown.
- **What the maker states.** Power "4.0-5.3 V DC; 3.6-4.5 V battery; 5 V USB-C" (RB9704-001-JUN26); nothing about
  back-feed.
- **Proof required.** Bench E-04, or the hardware bound of SD-EMC-2.
- **Status.** The gate is CLOSED at desk. The back-feed is OPEN.

### 4.5 RM520N-GL 5G module (board B, `J_M2C2`, M.2 key B)

- **Physical control, as drawn.** Q206, a 2N7002 open drain with its gate on `EMCON_ON`, pulls W_DISABLE1# (socket pin
  8) low. R237 (10 k) pulls it up to the card rail (`gen_sch_b.py:644`; `B-r6cand-pcb-b-compute.net:19565`). Inside the
  module the pin is pulled up to 1.8 V through 100 k behind a diode level shifter (HD v1.1, pin table page 22 and
  Figure 23).
- **Supply, as drawn.** `+3V3_S2A` is made by U203, an AP64500 whose EN is `PCIE_PWR_EN2` directly, from slot 2's CM5
  only, with R206 (100 k) to GND (`B-r6cand-pcb-b-compute.net:21439`); it reaches the socket's five 3.3 V pins through the
  Kelvin shunt R265 as `+3V3_M2C2` (`:19156`). EMCON leaves it on: that is r4b's SD-B-03, citing Quectel's warning
  against cutting power while the module works. FULL_CARD_POWER_OFF# (pin 6, `5G_PWROFF_n`) comes only from Q207, driven
  by U6's `5G_OFF` (`gen_sch_b.py:645`; `:19554`). RESET# (pin 67) comes only from Q208, an open drain from U6's
  `5G_RESET` (`:19558`). U6 is a PCA9555 on the kit I2C bus (`SDA` `:21967`, `SCL` `:21943`, over `J_PANEL` pins 4 and
  5), whose master is the panel's RP2040 (`gen_sch_c.py:124`, U3 "the kit I2C master"). So both pins are written by the
  panel controller's firmware at the bridge's request.
- **Who can talk to the module.** Its PCIe link is slot 2's (U201, slot 2's switch). Its USB 2.0 pair goes to U302
  port 4, bank 3's hub (`USB_5G_P` `:22362`). r4b's generator says that link is kept "for firmware and AT access", and
  that on a hub it "also gives it the bank's failover" (`gen_sch_b.py:755` to `759`). HD v1.1 section 3.2 (page 28):
  in USB-AT-based PCIe mode the module "Supports MBIM/QMI/QRTR/AT over PCIe interface" and "Supports AT over USB
  interface"; in eFuse-based PCIe mode it supports the same four over PCIe; in USB mode, over USB. So slot 2's host
  over PCIe can send AT commands and QMI or MBIM requests. So can bank 3's host over USB (slot 3's CM5, or the
  neighbour that adopts bank 3 on failover, ARCH-PCB-B-IOHA), in USB mode and in USB-AT-based PCIe mode.
- **How a host learns of EMCON.** No CM5 has a hardware input from EMCON on the candidate. On board B, `EMCON_HW`
  reaches only the gates U19 and U20, Q11's gate, the three supervisors' PC5, R58 and a test point (`:19944`). A host
  learns of EMCON in software, from the panel controller's report of the line (`PANEL.md:176`).
- **Required by SD-EMC-1 (section 5), not yet drawn.** What the stages do depends on whether the module has been
  turned on, meaning `PCIE_PWR_EN2` is high, `+3V3_S2A` is up, and FULL_CARD_POWER_OFF# has been let rise after the
  release's Tpr hold. Both stages hang on `EMCON_ON`, so all of this holds subject to L3.
  - **EMCON asserted before the module has been turned on:** FULL_CARD_POWER_OFF# low and `+3V3_S2A` removed at once,
    both latched for as long as EMCON stays asserted. The rail never rises under EMCON, so no handshake is owed. This
    covers:
    - every power-up of board B with EMCON already asserted, which is routine, because the toggle locks and holds its
      position through a power loss (section 5, SD-EMC-1);
    - EMCON asserted while slot 2's CM5 is off or holds `PCIE_PWR_EN2` low;
    - EMCON re-asserted inside the release's Tpr hold.
  - **EMCON asserted on a module that has been turned on,** in the maker's turn-off order:
    - W_DISABLE1# low at once (as drawn);
    - the host's own sequence, best effort: AT+CFUN=0, its OK, then PERST# through slot 2's switch, then RESET# and
      `5G_OFF` through U6 (Figure 11's order);
    - FULL_CARD_POWER_OFF# driven low by hardware at T_off after EMCON, with T_off sized for that handshake;
    - `+3V3_S2A` removed by hardware at T_off + T_cut, with T_cut at least 900 ms.

    Once started, the delays run to the end while EMCON stays asserted; nothing the module or a host does restarts
    or cancels them. This includes a module that is booting when EMCON asserts, or restarts while the delays run,
    whatever started the boot (SD-EMC-1's booting case).
  - On release: the rail comes back first, and the pin is released at least Tpr (100 ms) after it.
- **Active level.** W_DISABLE1# LOW: airplane mode. FULL_CARD_POWER_OFF# LOW (at most 0.2 V): turn off. Supply below
  3.135 V: outside the module's operating range (HD v1.1 section 3.3.1, page 29).
- **Default.** EMCON released: R237 holds the pin high. EMCON asserted: the pin is low as soon as +3V3_DEV is up, which
  is before any CM5 can raise `PCIE_PWR_EN2` (R206 holds it low until then). FULL_CARD_POWER_OFF# is high through R238
  once the rail is up, since `5G_OFF` is held low by R61 (4.7 k). So, as drawn, the module turns on whenever its rail is
  up, EMCON or not. R238 goes to `+3V3_S2A`, the module's own supply (`B-r6cand-pcb-b-compute.net`, net `+3V3_S2A`:
  R238 pin 2), so the pin rises with VCC. Figure 9 and Table 10 give Tpr, "Power-on time of the module before system
  turning-on and booting", as 100 ms minimum between VCC and the pin going high. Found while doing this, for the board B
  author: as drawn, every cold power-up has Tpr near 0. SD-EMC-1 makes every EMCON release such a power-up.

  **Default required by SD-EMC-1, subject to L3** (with +3V3_DEV lost, `EMCON_ON` falls and both stages release, as
  every open drain on that net does).
  - EMCON asserted at power-up: both stages hold from the moment +3V3_DEV is up. The rail cannot rise before then
    (SD-EMC-1 traces the sequence through boards A, B and C), so `+3V3_S2A` never rises and the module is never
    powered.
  - EMCON released at power-up: both stages are released. The rail rises when slot 2's CM5 raises `PCIE_PWR_EN2`, and
    the pin rises at least Tpr after the rail. The module then boots, and an EMCON that asserts during that boot is
    SD-EMC-1's booting case.
- **Controller failure.**
  - Slot 2's or bank 3's host crashed, or sending AT+CFUN=1: Table 22 keeps RF disabled while the pin is LOW.
  - **Either host writes a persistent configuration that turns the pin's function off.** Quectel's LTE firmware has
    exactly such a setting, saved automatically and disabled by default (below). Whether the RM520N-GL has one is not
    documented. A host that writes it once changes every later EMCON. Both hosts that reach an AT port can do it.
  - **Host software asks for the online state while the pin is LOW.** In Quectel's LTE firmware, a request over QMI is
    refused only at `airplanecontrol` value 2; at value 1 only AT+CFUN=1 is refused (below). That manual does not name
    MBIM, though the RM520N-GL offers MBIM on both links (HD v1.1 section 3.2). How MBIM is treated with the pin LOW
    is therefore a bench case of E-05, not a documented behaviour.
  - U6 dead, or the panel controller dead: no effect on W_DISABLE1#. The host's sequence cannot write `5G_OFF` or
    `5G_RESET`, so it cannot finish, and SD-EMC-1's hardware stages do the turn-off (the fault case).
  - +3V3_DEV lost: `EMCON_ON` falls, Q206 releases the pin, and the module returns to full function (L3, fail-open).
  - The module's own firmware hung or booting: not stated by the maker (below).
  - **A host, or the module's own firmware, restarts the module while EMCON is asserted and the delays run**: by
    AT+CFUN=1,1, by a warm or hard reset through U6 (before T_off, while the backstop has not yet taken the pin), or
    by a restart the firmware starts itself. The rail stays up, so the module boots with W_DISABLE1# already low.
    Whether it honours the pin then is not stated (below). The delays still end it at T_off + T_cut (SD-EMC-1's
    booting case).
- **Powering and back-powering.** Not applicable as drawn (the module stays powered). Under SD-EMC-1 the rail becomes
  removable, and these lines stay live while it is off (`B-r6cand-pcb-b-compute.net`; dumps in
  `v2/docs/records/rv-emc/readings/B-m2c2-sdemc1.txt`): `USB_5G_P` and `USB_5G_N` from
  U302 port 4, slot 3's TUSB8041 hub (`:22362`); PERST# from U201's DWNRST_L2 (`:21345`), the same TBD drive as the
  AW7915 rows; REFCLK from U201 through R283 (33.2 Ohm) with R285 (49.9 Ohm) to ground (`:19842`); the PCIe TX pair
  `CARD2_TX` from U201; PEWAKE# through R232 (10 k) to `+3V3_S2B` (`:21369`). CLKREQ# (R234), W_DISABLE1# (R237),
  FULL_CARD_POWER_OFF# (R238) and the LED (R239) are pulled to the dead `+3V3_S2A`. SD-EMC-2 applies.
- **What the documents state.**
  - HD v1.1 section 4.4.1 (page 49): "W_DISABLE1# is pulled up by default. Driving it LOW will set the module to
    airplane mode. In airplane mode, the RF function will be disabled."
  - HD v1.1 Table 22: pin LOW gives "Disabled / Airplane mode" for AT+CFUN=0, 1 and 4. Table 7: AT+CFUN=4 or pin LOW,
    "the RF function is invalid". Table 24 (page 52): LED_WWAN# off when "W_DISABLE1# is at low level (airplane mode
    enabled)". HD v1.0 carries the same text.
  - HD v1.1 section 3.5 (page 33), turn-off: "driving FULL_CARD_POWER_OFF# pin LOW (≤ 0.2 V) or tri-stating the pin
    will turn off the module. Sending the command AT+CFUN=0 is necessary before shutting down the module. The following
    is a proper shutdown handshake for FULL_CARD_POWER_OFF#, which complies with the M.2 specification. **Only after this
    process is completed, can the module be successfully turned off by pulling down FULL_CARD_POWER_OFF#.** 1. The host
    sends AT+CFUN=0 to the module. 2. The module will do the essential shutdown tasks. 3. The module responds OK." HD
    v1.0 carries the same sentences (page 31).
  - HD v1.1 Figure 11 (page 33) draws the order: "Execute AT+CFUN=0, and the module responds OK"; then the host pulls
    PCIE_RST_N low; after Toff1 (100 ms typical) RESET#; after Toff2 (0 ms minimum, 100 ms typical) FULL_CARD_POWER_OFF#;
    after Tpd the module is OFF. Table 11 (page 34) gives Tpd, "The period from the host pulling down
    FULL_CARD_POWER_OFF# to the module turning off", as 900 ms minimum, with no typical or maximum: "It is recommended to
    cut off VCC when the module has been powered off completely." Toff1 and Toff2 are periods the host sets.
  - HD v1.1 Figure 9 and Table 10 (page 32), turn-on: VCC first, then FULL_CARD_POWER_OFF# high after Tpr, "Power-on
    time of the module before system turning-on and booting depending on the host", 100 ms minimum.
  - HD v1.1 section 3.3.2 note (page 31): "To avoid corrupting the data in the internal flash, DO NOT cut off the power
    supply before the module is completely turned off by pulling down FULL_CARD_POWER_OFF# pin for more than 900 ms,
    and DON'T cut off power supply directly when the module is working."
  - HD v1.1 section 3.6 (page 34): RESET# "When this pin is asserted, the module will immediately enter reset
    condition"; nothing about RF or about holding it. Figures 12 and 13 (page 35) draw the pin's only pull-up inside
    the module as a 1.5 uA source to its internal 1.8 V.
  - **Resets end in a boot with the supply up.** HD v1.1 Figure 14 and Table 13 (page 36), the warm reset: "when only
    the reset signal is pulled LOW ... the power of the module will not be turned off"; TRST# 200 ms minimum, 400 ms
    typical, "Reset baseband chip IC only"; VCC and FULL_CARD_POWER_OFF# stay high, and the module status runs Active,
    Baseband Resetting, Booting. Figure 15 and Table 14 (page 37), the hard reset: "Sending the command AT+CFUN=0 is
    necessary before resetting the module" (page 36); then PCIE_RST_N, RESET#, and FULL_CARD_POWER_OFF# held low for
    Toff (900 ms minimum, "Ensure that the module has been turned off completely") and raised again with VCC kept up;
    the status runs Active, Resetting, Booting. On board B, RESET# is Q208's drain alone (`5G_RST_n`, 2 nodes,
    `B-r6cand-pcb-b-compute.net:19562`), driven by U6's `5G_RESET` (`:19558`, with R62 4.7 k), so a warm reset is
    U6's, and a hard reset is U6's `5G_RESET` and `5G_OFF` together.
  - AT Commands Manual V1.0 (2024-02-07), section 2.22 (page 29): `<fun>` 4 is "Disable both transmitting and receiving
    RF signal"; AT+CFUN's maximum response time is "15 s, determined by the network"; "When the module searches or
    registers the network, it may write data to NVM if executing AT+CFUN=1"; and `<rst>` 1 is "Reset UE. The device is
    fully functional after the reset", available only with `<fun>` 1, so AT+CFUN=1,1 restarts the module from software
    with VCC and FULL_CARD_POWER_OFF# up.
  - The same manual, section 3.3.6 notes 5 and 6 (page 43): "When rebooting the module (For example: 5 seconds after
    upgrading firmware via FOTA or host connection) ...", which names a restart that follows a firmware upgrade; and
    "It is not recommended to execute AT+CFUN=1,1 to restart the module with the PCIe interface ... It is recommended
    to restart the module by hardware method instead."
- **What they do not state.**
  - The time from pin LOW to RF off.
  - Whether the pin is honoured from the first instant of power-up, before the firmware reads it.
  - Whether it is honoured while the module's firmware is hung, booting or rebooting (airplane mode is a firmware
    operating mode), including a pin that falls while the module boots, and a pin already low when a reset ends.
  - **The module's boot time**, after a turn-on or after any reset. Figure 9 (page 32) draws a "Booting" phase between
    FULL_CARD_POWER_OFF# rising and "Active", with no duration, and Figures 14 and 15 end in the same phase with none.
    Table 10's Ton ("Typ. Ton is 3 s" in USB-AT-based PCIe mode) is "The period when the host GPIO controls the module
    to exit the PCIe reset state", which is a period the host sets, not the boot. Footnote 17 to Tables 10 and 14:
    "At booting stage, the host must not drive RESET# low after FULL_CARD_POWER_OFF# is de-asserted." So a host cannot
    run Figure 11's sequence on a booting module; it can start only once the module answers AT. SD-EMC-1's booting
    case rests on this.
  - **Whether any socket pin marks a restart the module's own firmware carries out** (AT+CFUN=1,1, the restart after a
    firmware upgrade, or a crash or watchdog restart, which no held document describes and none rules out). RESET# is
    an input with an internal 1.5 uA pull-up; no document says the module drives it, or CLKREQ#, PEWAKE# or the LED
    pin, during such a restart. So board B, as far as the documents go, cannot see one. Nor do they say whether
    PERST# (PCIE_RST_N) alone restarts the module; Figures 9, 11 and 15 draw it only beside a turn-on, a turn-off or
    a hard reset.
  - **Whether any stored setting can disable the pin's function.** Quectel's own documents show that such a setting
    exists in its firmware family:
    - EG25-G Mini PCIe Hardware Design V1.0, section 3.8.3 (page 26, held in `v2/vendor/lte/`): "W_DISABLE# signal
      function is disabled by default, and AT+QCFG="airplanecontrol",1 can be used to enable this function." That is
      the maker's statement of the default. Its
      Table 11 on the same page still shows "Low Level ... Disabled" without restating that condition, so a maker's
      table of the pin's effect can be conditional on a setting the table does not name.
    - EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual V1.1, section 5.12 (pages 61 and 62): `airplanecontrol` takes
      0 (disabled), 1 or 2; "The configurations are saved automatically"; at 1 "It is not allowed to exit airplane mode
      by AT+CFUN=1 when W_DISABLE# pin is active", and only at 2 "by AT+CFUN=1 or QMI". The manual names QMI and never
      MBIM in this section. Its example is a query, not a default statement: it reads `+QCFG: "airplanecontrol",0,0`
      before the setting is enabled.
    - At 1 and 2 the module will "Enter airplane mode when W_DISABLE# pin changes to active and exit airplane mode when
      W_DISABLE# pin changes to inactive". That wording describes an edge. The example also shows the module entering
      airplane mode when the setting is enabled with the pin already low ("Enter airplane mode because W_DISABLE# pin is
      pulled down"). After a reboot, it shows only a later pull-down. None of these cases is a boot with the pin
      already low, nor a pin that falls while the module boots. Under SD-EMC-1 a power-up with the pin already low
      arises only when a stage has failed, because the module is never powered under EMCON. A boot with the pin
      already low still arises when a running module restarts while the delays run (a reset through U6, AT+CFUN=1,1,
      or a restart of its own). A pin that falls while the module boots arises whenever EMCON asserts during a boot,
      whatever started it. Both are SD-EMC-1's booting case. Bench E-05 (b), (c) and (d) test them.
    - Section 5.27 (page 75) adds `AT+QCFG="airplane"` with 2 "Force to exit airplane mode", also saved
      automatically; how it interacts with the pin is not stated.

    For the RM5xxN family, the released AT manual lists twelve AT+QCFG parameters and none concerns airplane mode or
    W_DISABLE1# (0 occurrences of either word in the whole manual), and so do the preliminary RM520N manual of 2022 and
    the RM5xxQ manual V1.1.1 (0 occurrences). The released manual's documented AT+QCFG=? response ends in "…" (page 37),
    as the RM5xxQ manual's does (page 38): the maker presents its list as incomplete. So the manual does not rule such a
    setting out; only AT+QCFG=? on the fitted firmware can say which settings exist.
  - Whether W_DISABLE1# also stops the module's GNSS receiver. W_DISABLE2# controls GNSS (section 4.4.2), and board B
    leaves it pulled up, so the module's GNSS keeps receiving, which D-05 allows.
- **Proof required.** Bench E-05 (the W_DISABLE1# stage, repeated per firmware revision and per configuration) and bench
  E-12 (FULL_CARD_POWER_OFF# with and without the handshake, the handshake's time with the pin already low, the staged
  EMCON as built, flash integrity in the cooperating case and in the fault case, the release's Tpr, the back-feed, the
  power-up under EMCON, and the booting case for each of its causes). A module whose firmware revision and recorded
  configuration have not passed E-05 is not counted as inhibited by its pin. The kit's provisioning verifies that
  configuration at every boot, from each host that reaches an AT port (section 8).
- **Status: OPEN.** As drawn, the inhibit is a maker-documented firmware mode that may rest on a stored, host-writable
  setting. It is not a supply cut or an RF-path cut, and RF-002 and REQ-030 exclude that dependence. SD-EMC-1's supply
  removal is the only option the documents allow that does not depend on the module's firmware. Also L1, L2, L3 and L7.

### 4.6 and 4.7 AW7915-AED WiFi link cards (board B, `J_M2C1` slot 1 and `J_M2C3` slot 3)

- **Physical control.** The card's supply is removed. Q111 (Q311), a 2N7002 with its gate on `EMCON_ON`, pulls
  `S1A_EN` (`S3A_EN`) low. That is the EN of U103 (U303), the AP64500 buck that makes `+3V3_S1A` (`+3V3_S3A`), which
  reaches the socket's four 3.3 V pins through the Kelvin shunt R165 (R365) (`gen_sch_b.py:451`, `:478`;
  `B-r6cand-pcb-b-compute.net:21586`, `:21829`, `:19147`). Q106 (Q306) also pulls W_DISABLE1# (pin 56) low
  (`:22508`, `:22484`), but that is not counted (below).
- **Active level.** EN below VEN_L, 1.03 V minimum: regulator off (AP64500 DS41979 Rev 5-2, electrical table and pin
  description).
- **Default.** `PCIE_PWR_EN1` (`PCIE_PWR_EN3`) is a CM5 output held low by R106 (100 k), and `S1A_EN` follows it through
  R164 (10 k). The AP64500's EN starts the regulator when left open ("leave floating for automatic startup"), so its EN
  current is sourced. DS41979 gives that current as 5.5 uA TYPICAL at VEN 1.5 V, with no maximum, so a hold against it
  is UNDECIDED at desk (R4T-D28 amended, R4T-D29). At the typical figures the hold is 0.22 V against VEN_L 1.03 V, and
  0.61 V at 5.5 uA. With EMCON asserted, Q111 pulls the node low (L7).
- **Controller failure.** CM5 crashed with `PCIE_PWR_EN` high: EMCON still wins through Q111. +3V3_DEV lost: `EMCON_ON`
  falls, Q111 releases, and the card powers if its CM5 asks (L3, fail-open).
- **Powering and back-powering.** With `+3V3_S1A` off, three live lines reach the card:
  - PEWAKE0# (pin 55), 10 k (R132) to `+3V3_S1B`: 0.33 mA at most (`:21308`);
  - PERST0# (pin 52) from the PCIe switch's DWNRST_L2 on `+3V3_S1B` (`:21284`). DS40068 Table 12-2 gives VOH 2.4 V
    minimum and no output current, so this term is TBD. Its effect: the back-fed current is bounded only by the switch's
    unstated drive;
  - REFCLK (pins 47, 49), an HCSL source with 33.2 Ohm series and 49.9 Ohm to ground at the switch (`:19807`).

  CLKREQ0#, both W_DISABLE# pulls and the LED's anode resistor all go to the card's own dead rail. The card needs host-
  loaded RAM firmware to run: the mt7915 driver loads a ROM patch and the WM and WA RAM images at every start
  (`mt7915/mcu.c:2142` to `2170`, `mt7915/mt7915.h:29` to `31`), and a collapsed rail loses them. That the card cannot
  emit on the bounded currents is INFERRED, not published.
- **What the documents state.** Nothing about W_DISABLE1#: the AsiaRF datasheet does not mention the pin; mainline
  mt7915 has no rfkill code (0 occurrences in `mt7915/main.c` at `f14572c2`), while mt7921 polls the pin
  (`mt7921/main.c:1536`). The pin is therefore not counted, as D-05's gap fix and r4b's SD-B-02 require.
- **Proof required.** Bench E-07: the rail collapse, back-feed and RF with EMCON asserted. A series resistor on PERST0#
  (SD-EMC-2) removes the TBD term.
- **Status.** The gate is CLOSED at desk on the candidate. The back-feed is OPEN (one TBD term). Also L1, L2, L3 and L7.

### 4.8 to 4.13 Compute Module 5 WiFi and Bluetooth, slots 1 to 3 (board B, U30A, U31A, U32A pins 89 and 91)

- **Physical control.** `WL_nDIS{s}` and `BT_nDIS{s}` each carry exactly two nodes: the CM5 pin and the drain of
  Q{s}09 or Q{s}10, a 2N7002 open drain to GND (`B-r6cand-pcb-b-compute.net:22515`, `:19693`). The gate is
  `KILL = OFF request OR EMCON_ON`, from U{s}11 (SN74LVC32A on +3V3_DEV), with 100 k (R{s}73, R{s}74) to GND
  (`gen_sch_b.py:723` to `741`; `:22518`, `:22522`).
- **Active level.** CM5 pin LOW: disabled. The CM5 datasheet (release 3, section 2.1) says the two pins "allow
  hardware-level shut down of Wi-Fi and Bluetooth". The pin table (pins 89, 91) says "if driven low, the Wi-Fi interface
  will be disabled" (Bluetooth likewise), and both pins are "internally pulled up through 1.8 kΩ to CM5_3.3V". The pins
  "may only be driven low" (sections 2.1.1 and 2.1.2): the open drain satisfies that in every state (r4b SD-B-01).
- **Default.** The OFF requests are pulled up by R{s}62 and R{s}63 (10 k) to +3V3_DEV, and U6 powers up as inputs, so
  KILL is high and every CM5 radio is disabled until firmware writes the request low (`gen_sch_b.py:740`). EMCON forces
  KILL high regardless of U6.
- **Controller failure.**
  - U6 hung on the bus: its outputs stay latched, and `EMCON_ON` still forces KILL.
  - The CM5 crashed: the pin is held low from outside. The datasheet's note that "the software driver drives it high
    internally when required" is the case the open drain was chosen for; the maker permits driving low.
  - +3V3_DEV lost: U{s}11 and R513 are unpowered, KILL falls through R{s}73, and the radios are released. This is L3,
    fail-open, and U6 is unpowered in the same state. U{s}11 in the unspecified supply band is L4, case 1.
- **Powering and back-powering.** Not applicable: the module stays powered. With the panel absent, board A's slot
  enables are pulled low and no CM5 runs (`PANEL.md:147`).
- **What the maker states.** A hardware disable pin with the words above. Section 2.1.1's bullet reads "prevents
  Wi-Fi from powering up". Whether asserting it on a radio already transmitting stops it at once is covered by "hardware-
  level shut down" and "will be disabled", but no time is given.
- **Proof required.** Bench E-08, which includes asserting EMCON on a radio in AP mode, beaconing, and records each
  pin's low level (L7).
- **Status.** The chain is CLOSED at desk on the candidate (it closes W1-F01). The rows are OPEN on L1, L2, L3, L4 and
  L7.

### 4.14 E22-900M30S LoRa (board B, U12)

- **Physical control.** `+5V_LORA` comes from U21, a TPS22810 on +5V_DEV. Its EN/UVLO is
  `E22_EN = EMCON_HW AND LORA_ON` (U19 gate 4), with R516 (10 k) to GND (`gen_sch_b.py:925`, `:1002`;
  `B-r6cand-pcb-b-compute.net:19933`, `:19449`). "A voltage V(EN/UVLO) < V(ENF) on this pin turns off the internal FET,
  thus disconnecting VIN from VOUT" (SLVSDH0C section 9.3.3; VENF 1.08 V minimum in the electrical table).
- **Active level.** `EMCON_HW` LOW: supply off.
- **Default.** `LORA_ON` is held low by R52 (4.7 k).
- **Controller failure.** U6 dead: off. +3V3_DEV lost: R516 holds `E22_EN`, UNDECIDED until U19's section states Ioff
  (L3, state (2); R4T-F9). TXEN comes only from slot 3's GPIO4 and is not on EMCON; it matters only while the module is
  powered. L1, L2 and L4 apply.
- **Powering and back-powering.** Slot 3's CM5 keeps driving the SPI and control lines while `+5V_LORA` is off:
  - `SPI3_SCLK`, `SPI3_MOSI`, `SPI3_CE1` (the last also 10 k, R25, to `+3V3_S3B`);
  - GPIO26 (NRST), GPIO4 (TXEN), GPIO5 (RXEN) (`:22159`, `:21074`; `v2/docs/records/rv-emc/readings/B-e22-e72.txt`).

  The module operates from 2.5 V ("Support 2.5V~5.5V power supply", manual v1.20). A 3.3 V line through an input clamp
  can sit above that. U21's quick output discharge pin is left open (`unconnected-(U21-QOD-Pad2)`), so nothing pulls the
  dead rail down. Bound: TBD. Its effect: whether the SX1262 inside can wake on the back-fed rail is unknown, and so is
  whether it would emit through an unpowered PA.
- **Proof required.** Bench E-09, or the hardware bound of SD-EMC-2.
- **Status.** The gate is CLOSED at desk. The back-feed is OPEN.

### 4.15 and 4.16 E72 CC2652P, Zigbee coordinator and Thread RCP (board B, U13, U14)

- **Physical control.** `+3V3_ZB` comes from U22, a TPS22810 on +3V3_DEV, and feeds pin 20 of both modules. Its EN is
  `E72_EN = EMCON_HW AND ZB_ON` (U20 gate 1), with R517 (10 k) (`gen_sch_b.py:938`, `:1002`;
  `B-r6cand-pcb-b-compute.net:19940`, `:19366`).
- **Active level.** `EMCON_HW` LOW: supply off.
- **Default.** `ZB_ON` is held low by R53 (4.7 k).
- **Controller failure.** U6 dead: off. +3V3_DEV lost: the switch's own input is gone, so off (PASS, R4T-D30 and
  R4T-F9). L1 and L2 apply. L4 does not, since the rail cannot exceed a sagging +3V3_DEV, which in that band is under the
  E72's 1.9 V minimum.
- **Powering and back-powering.** Each module is driven by a CP2102N (U16, U17) whose VREGIN and VBUS are +5V_DEV, not
  gated: TXD to DIO_12, RTS to RESET_N and DTR to DIO_15 (`:22607`, `:22602`, `:22583`; `v2/docs/records/rv-emc/readings/B-e22-e72.txt`).
  - R28 to R31 (10 k) pull RESET_N and DIO_15 up to the gated `+3V3_ZB`, so a high RTS or DTR also feeds the dead rail
    through a resistor, 0.33 mA each at most.
  - The CP2102N sources at least 7 mA at VIO minus 0.7 V in push-pull, with no maximum stated. Its GPIO pins default to
    open-drain with a 10 to 30 uA weak pull-up (datasheet Rev. 1.5, Table 3.7 and section 4.3.1). The default mode of
    the UART and modem pins is not stated there: TBD.
  - The E72 operates from 1.9 V ("Support 1.9 ~ 3.8V power supply", user manual), so a back-fed rail can be inside its
    range.

  Bound: TBD. Its effect: whether a CC2652P can boot and emit on the back-fed rail is unknown.
- **Proof required.** Bench E-10, or the hardware bound of SD-EMC-2.
- **Status.** The gate is CLOSED at desk. The back-feed is OPEN.

### 4.17 LimeSDR Mini 2.4 (board B, `J_LIME`)

- **Physical control.** `+5V_LIME` (J_LIME VBUS) comes from U23, a TPS259631 eFuse. Its EN/UVLO is
  `LIME_EN = EMCON_HW AND LIME_HW_EN AND LIME_SW_EN` (U19 gates 1 and 2), with R514 (10 k) (`gen_sch_b.py:946`;
  `B-r6cand-pcb-b-compute.net:21032`, `:19443`).
- **Active level.** `EMCON_HW` LOW: supply off (VUVLO(F) 1.08 V minimum).
- **Default.** `LIME_SW_EN` is held low by R50 (4.7 k). `LIME_HW_EN` is the hub's port power control PWRCTL1.
- **Controller failure.** U6 dead: off. +3V3_DEV lost: R514 holds `LIME_EN`, UNDECIDED until U19's sections state Ioff
  (L3, state (2); R4T-F9). L1, L2 and L4 apply.
- **Powering and back-powering.**
  - The maker gives "Input Voltage 5 V DC Via USB Type-A connector; Maximum Power 4.5 W USB 3.0 power limit"
    (MyriadRF page, A11's copy), so VBUS is its only input.
  - The SuperSpeed TX pair is AC-coupled on B (C161, C162), and the RX pair ends at the hub's receiver.
  - D+ and D- pass a USBLC6-2SC6 whose VBUS pin is `+5V_LIME`, so a driven data line can feed the dead VBUS through the
    array's steering diode. The hub drives the pair only while a device is attached. Detach follows the loss of the
    device's own pull-up, which falls with VBUS. The feed is therefore a transient bounded by a USB 2.0 driver, against
    an SDR of up to 4.5 W. INFERRED from USB 2.0; bench E-06 records it.
- **Proof required.** Bench E-06.
- **Status.** The chain and back-feed are CLOSED at desk. The row is OPEN on L1, L2, L3 and L4.

### 4.18 Receivers, and what is outside the kit

- **Receive-only parts, which continue under EMCON as D-05 rules:** the LG290P GNSS (B, U11); the RM520N-GL's GNSS
  (W_DISABLE2# only pulled up; under SD-EMC-1 it also stops when the module's supply is removed, which D-05 does not
  forbid, because the kit's GNSS is the LG290P); the DCF77 receiver (E, `J_DCF`); the AS3935 lightning sensor (E,
  `J_LTG`).
- **Census.** Every part whose value names a radio is claimed by a transmitter entry, declared an accessory, or
  declared receive-only on all six candidate netlists: A, C, D, E and P PASS, and B UNDECIDED only on `J_QMX`, which
  section 4.3 answers (tool output lines 38 to 44). Limit: the census matches part value text against a vocabulary
  (`tx_inhibit.py`, `RADIO`), so a radio whose value names none of it would be missed.
- **Outside the kit (SD-EMC-3).** Equipment on the kit's outlets is not a kit transmitter: the PoE output, the USB-C
  power outlet, the Glenair host port and Ethernet. The kit cannot silence a device it does not power or control, for
  example a tablet on the lid bracket or a phone on the outlet.

## 5. Decisions taken by the session under the owner's standing rule of 26 September 2026

Each had more than one option and no owner judgement standing. None spends money or changes what the kit is claimed to
be; SD-EMC-1 and SD-EMC-6 each accept a residual risk, stated with its bound.

- **SD-EMC-1 (restated in the third cycle; power-up rule added in the fourth; booting case defined by state in the
  fifth): the module is never powered under EMCON, and a running module's EMCON follows the maker's turn-off order,
  with a hardware backstop at each step.**
  - History.
    - The first version took W_DISABLE1# alone, with FULL_CARD_POWER_OFF# as a fallback. The maker's own words refute
      both parts (section 4.5).
    - The second version took option (e) below, which drives FULL_CARD_POWER_OFF# low at the same instant as
      W_DISABLE1#. That puts the pin ahead of the host's AT+CFUN=0 in every EMCON, even when the firmware cooperates.
      It is the reverse of HD v1.1 section 3.5 ("Only after this process is completed") and of Figure 11. So its
      claim that the flash risk fell only on the fault case was wrong, and it was withdrawn in the third version.
    - The third version timed both delays from EMCON, whatever the module's state. So every power-up with EMCON
      already asserted ended in the backstop with no handshake, and its bound of both residual risks to the fault case
      was too narrow. The fourth version added the power-up rule below.
    - The fourth version bounded the exposure of a booting module to a "reversal case", EMCON re-asserted while the
      module boots after a release. Every boot of a module that has been turned on carries the same exposure, whatever
      started it, and the fallback it named, keyed to the rail and the pin, could not see a boot after a reset. The
      fifth version defines the booting case by the module's state, names its causes, and keys the fallback to every
      boot start board B can see, with the restarts it cannot see stated as a residual.
  - Options:
    - (a) W_DISABLE1# only (as drawn, r4b SD-B-03);
    - (b) supply removed at once;
    - (c) FULL_CARD_POWER_OFF# driven from EMCON, supply kept;
    - (d) RESET# held low;
    - (e) W_DISABLE1# and FULL_CARD_POWER_OFF# low at once, supply removed after T_cut (the second version);
    - (f) the maker's order, with hardware backstops: W_DISABLE1# low at once; the host's sequence, best effort
      (AT+CFUN=0, its OK, then PERST#, RESET# and `5G_OFF`); FULL_CARD_POWER_OFF# driven low by hardware at T_off,
      sized for that handshake; supply removed by hardware at T_off + T_cut;
    - (g) keep (e) and accept the flash risk at every EMCON until E-12 shows otherwise.
  - Taken: (f).
  - Why:
    - NEED-08, REQ-030 and RF-002 exclude software. (a), (c) and (d) each end in the module's own firmware: (a) and (c)
      as quoted in section 4.5, and (d) because the maker states nothing about RF in reset. Only (b), (e), (f) and (g)
      remove the supply in hardware, whatever the firmware does.
    - (b), (e) and (g) take the module out of the maker's order in every EMCON: (b) cuts VCC with no turn-off, and (e)
      and (g) drive the pin before the handshake. No held document states what the module does when the pin is low
      before AT+CFUN=0: whether it acts at once, waits, or still accepts the handshake. So each of the three exposes the
      flash (HD v1.1 section 3.3.2 note) at every EMCON, and EMCON is a routine operating mode.
    - On a module that has been turned on, (f) keeps the maker's order whenever the host's sequence finishes within
      T_off. The handshake completes, the host pulls RESET# and the pin, the backstop then falls on a pin that is
      already low, and the rail is cut at least T_cut later. The backstop drives the pin without the handshake only
      when that sequence fails, whether in the host, the bridge, the panel controller or the module's firmware (the
      fault case), or cannot finish on a module that is booting (the booting case, below). The flash risk falls
      there.
      On a module that has not been turned on, no sequence is owed at all (the power-up rule, below).
    - What (f) costs is the emission bound in those two cases (below). In the fault case it bites only when the
      module's firmware also ignores W_DISABLE1#, which E-05 and the provisioning check are there to exclude. (e) and
      (g) expose the flash at every EMCON. The session judged a longer bound in a double fault to cost less than an
      unmeasured chance of losing the module in routine use. The booting case adds a single-condition exposure,
      bounded and with a fallback named in advance (below). E-05 and E-12 measure both.
  - T_off, the backstop's delay from EMCON to FULL_CARD_POWER_OFF# low, must exceed the host's sequence. That sequence
    takes:
    - the software's reaction time. No CM5 has a hardware input from EMCON (section 4.5). The panel controller reads
      `EMCON_HW` on GPIO21 and reports it over its CDC port (`PANEL.md:176`), and the bridge on the host that holds an
      AT port acts on it;
    - AT+CFUN's maximum response time, "15 s, determined by the network" (AT Commands Manual V1.0, section 2.22);
    - the PERST# and RESET# steps (Toff1 and Toff2, 100 ms typical each, set by the host).

    No maker figure is shorter. Whether AT+CFUN=0 answers faster with the pin already low (RF off, no network to leave)
    is not stated, and E-12 (c) measures it. So T_off is at least the software's reaction time plus 15 s until E-12
    shows otherwise. The reaction time is TBD, and the bridge software owner bounds it (section 8).
  - T_cut is at least 900 ms after the backstop pin falls (Tpd minimum, HD v1.1 Table 11 and the 3.3.2 note). The maker
    gives no maximum. It is TBD; E-12 (a) and (b) measure the fitted module's Tpd.
  - **Power-up, and a module not yet turned on (added in the fourth cycle).**
    - The problem with the third version. It timed both delays from `EMCON_ON`, which R513 pulls up to +3V3_DEV
      (`gen_sch_b.py:1029`). At a cold power-up with EMCON asserted, both delays therefore started when +3V3_DEV rose.
      That power-up is routine:
      - `SW_EMCON` is the APEM 5636ADKB-2V (`gen_sch_c.py:207` to `211`), the same part as `SW_ZERO`. Board C's
        generator says of that part, in its ZEROIZE notes: "single pole ON-NONE-ON, both positions locked (appendix
        32.13 ruling 1), so the level holds through a power loss" (`gen_sch_c.py:115` to `116`).
      - U203's EN is `PCIE_PWR_EN2` directly. That net holds only U203's EN, R206 (100 k to GND) and slot 2's CM5 pin
        (U31B pin 106, `B-r6cand-pcb-b-compute.net:21439`). So the rail rises as soon as the CM5 raises that pin
        during its boot.
      - R238 then raises FULL_CARD_POWER_OFF# with VCC, and R61 holds `5G_OFF` low (`:19550`), so the module boots.
      - The host's sequence can finish within T_off only if the panel controller, slot 2's CM5, the bridge and the
        module are all up and acting within T_off of +3V3_DEV rising. T_off is sized from the panel's EMCON report
        (above), which leaves boot time out.

      So every such power-up ended in the backstop with no handshake, possibly mid-boot. A module that does not honour
      a pin already low at boot (the LTE precedent's edge wording, section 4.5) could emit until T_off + T_cut. Both
      residual risks arose in routine use, and the third version bounded them to a double fault.
    - Options:
      - (i) the delays run from EMCON whatever the module's state (the third version);
      - (ii) both stages act at once whenever EMCON asserts before the module has been turned on, and hold for as long
        as EMCON stays asserted; the delays apply only when EMCON asserts on a module that has been turned on;
      - (iii) as (ii), and a module whose last boot started less than a window T_boot ago is also treated as not yet
        on, so its supply is removed at once. (The fourth version keyed this window to the module's turn-on alone; the
        fifth keys it to every boot start board B can see, below.)
    - Taken: (ii). (i) is withdrawn for the problem above. "Turned on" means `PCIE_PWR_EN2` is high, `+3V3_S2A` is
      up, and FULL_CARD_POWER_OFF# has been let rise after the release's Tpr hold. Figure 9 draws the module OFF until
      that pin rises, so a module that has not been turned on has never left the OFF state, and no handshake is owed.
      `PCIE_PWR_EN2` is part of the definition (added in the fifth cycle) so that a cycle of that pin by slot 2's CM5
      is seen whatever the rail does in between, and the pin gets its Tpr after it too.
    - Why (ii) covers every cold power-up. The stage logic is on +3V3_DEV, and the rail cannot rise before it:
      - U25 makes +3V3_DEV from +5V_DEV. Board B's generator: "U25 is an AP63203 whose EN pin is tied to its own
        input" (`gen_sch_b.py:120`; pins 2 and 3 both on +5V_DEV at `:833`).
      - U203's input, pin 2, is `+5V_S2` itself, and that net's only source on board B is `J_5V_S2` pin 1, the lead
        from board A (`B-r6cand-pcb-b-compute.net:19488`; its other nodes are capacitors, the clamp D201, an LED
        resistor, the fan, the three converters' inputs and the CM5's 5 V pins). On board A that net is the output of
        U5, an LM5176, through its shunt R35 (`A-r6cand-pcb-a-power.net:9538`). U5 runs only while `SLOT_EN2` is high:
        it is U5's pin 1, EN/UVLO (`gen_sch_a.py:873`; `A-r6cand-pcb-a-power.net:10803`), and R34, 100 k, holds
        `SLOT_EN2` low (`gen_sch_a.py:879`). So U203 has no input before `SLOT_EN2` rises, whatever slot 2's CM5
        does with `PCIE_PWR_EN2`.
      - `SLOT_EN2` comes from the panel RP2040, "so no slot powers until firmware drives a pin high"
        (`gen_sch_c.py:118` to `119`). The panel is powered by `PANEL_5V`, which is +5V_DEV through F1
        (`gen_sch_b.py:1053`; `B-r6cand-pcb-b-compute.net:21248`).

      So +3V3_DEV and the stage logic are up for at least the panel controller's boot before the rail can have an
      input, and in practice for the CM5's boot too before it can rise. L4's unspecified band of the logic's own
      supply is crossed while the rail cannot rise. All of this holds subject to L3: the stages hang on `EMCON_ON`,
      and a loss of +3V3_DEV alone releases them while `+5V_DEV`, the panel and the slot can stay up.
    - What (ii) gives. The module is never powered under EMCON: no handshake, no exposure of its flash, no emission
      from a module booting under EMCON. At a re-assertion inside the release's Tpr hold, the rail is removed from a
      module that is still OFF. No document states whether VCC may be removed from that state within 900 ms. The 3.3.2
      note speaks of a module turned off by the pin. E-12 (i) records it with (e)'s checks.
    - **The booting case, which (ii) leaves on the delays.** The module has been turned on, and it is booting when
      EMCON asserts, or it restarts while the delays run. The case is defined by the module's state, not by what
      started the boot. Its causes:
      - an EMCON release, which turns the module on again;
      - a power-up of the kit, or of slot 2 alone, with EMCON released: the module boots once slot 2's CM5 raises
        `PCIE_PWR_EN2` (`B-r6cand-pcb-b-compute.net:21439`);
      - slot 2's CM5 lowering and re-raising `PCIE_PWR_EN2`, in its own restart or from its software;
      - a warm reset, `5G_RESET` through U6 and Q208 (HD v1.1 Figure 14), or a hard reset, `5G_RESET` and `5G_OFF`
        together (Figure 15), each written by the panel controller at a host's request;
      - AT+CFUN=1,1 from either host that reaches an AT port (AT manual section 2.22);
      - a restart the module's own firmware starts: the restart after a firmware upgrade that the AT manual names
        (section 3.3.6 note 5), or a crash or watchdog restart, which no held document describes and none rules out.

      The list is what the held documents name; it is not proved complete. A restart by any means they do not name
      (for example, whether PERST# alone restarts the module, which HD v1.1 does not say) is treated as one board B
      cannot see: the same bound, T_off + T_cut, applies to it (below). A power-up with EMCON released is at least as
      routine as a reversal: the operator can set EMCON at any moment after switching the kit on.
      - The maker gives no boot time after a turn-on or a reset (section 4.5). Footnote 17 bars RESET# low at the
        booting stage. So the host's sequence can start only once the module answers AT.
      - If EMCON asserts during a boot, W_DISABLE1# falls at once. If the module restarts while the delays run, it
        boots with the pin already low. Whether a module honours either is not stated (section 4.5).
      - Either way the delays run to the end. They started when EMCON asserted on a module that had been turned on,
        and a boot or a restart changes none of `PCIE_PWR_EN2`, the rail or the release hold. A CM5 that lowers
        `PCIE_PWR_EN2` while EMCON is asserted makes the module "not turned on", so both stages act at once and latch.
      - If the boot and the host's sequence together exceed T_off, the backstop acts without the handshake, possibly
        mid-boot.
      - So in this case residual risk (1) needs one condition: the module misses the pin while it boots, or when it
        boots with the pin already low. Residual risk (2) needs none beyond a boot that is slow against T_off. Both
        are stated below. E-05 (b) to (d) and E-12 (i) measure it, cause by cause.
    - Why not (iii). It would close the booting case's emission only for the boots board B can see (below), it needs a
      boot window the maker does not give, and it removes the supply from a booting module at every EMCON inside that
      window, which the 3.3.2 note advises against ("DON'T cut off power supply directly when the module is working").
      Under (ii), W_DISABLE1# still falls at once in that case.
    - **Fallback, named in advance.** If E-05 (b), (c) or (d) shows that the fitted firmware misses a pin that falls
      while it boots, or one already low when a reset ends, (iii) is taken, keyed to every boot start board B can see.
      - The boot window T_boot restarts at each of these, all on board B:
        - FULL_CARD_POWER_OFF# rising at the socket (`5G_PWROFF_n`), whichever driver releases last. This marks every
          boot from the OFF state: an EMCON release, a power-up or a `PCIE_PWR_EN2` cycle with EMCON released (the pin
          rises when the Tpr hold ends), and a hard reset through `5G_OFF` (Figure 15). The backstop only ever pulls
          the pin low, so it never starts a window itself.
        - `5G_RESET` falling at U6's output: the end of a warm reset (Figure 14). It is read there and not at RESET#,
          because the module's only pull-up on RESET# is a 1.5 uA source (Figure 12), which an input's leakage could
          overcome and so hold the module in reset.
      - While the window runs, the module is treated as not yet turned on: EMCON removes its supply at once, and the
        stages latch. A reset that ends while EMCON is asserted and the delays run starts a window too, so the supply is
        removed at once when that reset ends.
      - T_boot is the longest time from a boot's start to the module's first AT answer that E-12 (i) measures over
        every cause, plus a margin.
      - For the boots board B sees, the booting case's emission bound then becomes the rail's own fall, and its flash
        exposure becomes certain at every EMCON inside T_boot.
      - **The restarts board B cannot see.** AT+CFUN=1,1, a restart the module's own firmware starts, and any restart
        the documents do not name leave `PCIE_PWR_EN2`, the rail, the pin and `5G_RESET` as they were, and no held
        document says that any socket pin marks them (section 4.5). Two ways were weighed: restart the window on a
        hardware-visible reset, or state these restarts as a residual with their bound. Either alone falls short. The
        first alone would imply a coverage no document supports, and the second alone would leave the visible resets
        on the longer bound. **Taken: both.** The window restarts on every boot start board B can see (above), and the
        restarts it cannot see are a named residual:
        - bound: T_off + T_cut after EMCON, because the delays still run (above);
        - condition: one event, such a restart within T_boot before EMCON or between EMCON and T_off, on firmware that
          E-05 has already shown to miss the pin;
        - narrowed, as care and not as the inhibit, by the bridge rule below: the bridge restarts the module only by
          hardware, which Quectel recommends in PCIe mode anyway (AT manual section 3.3.6 note 6). What remains is a
          restart the firmware starts itself, and a host that breaks the rule;
        - measured: E-12 (i) records whether any socket pin marks such a restart. If one does, reliably, the window
          restarts on it too and the residual closes.
      - A third way closes every restart: whenever E-05 fails, take (e), the pin and then the supply cut on every
        EMCON. It exposes the flash at every EMCON, the cost this decision was taken to avoid, in order to close a
        residual that needs a restart to coincide with EMCON. The session did not take it. It is the named next step
        if E-12 sees the module restart with no host command, since such restarts cannot be excluded by a bridge
        rule.
  - The emission bound this costs, in two cases:
    - the fault case, where the module's firmware ignores W_DISABLE1# and the host's sequence fails;
    - the booting case, whatever started the boot, where the module misses a pin that falls while it boots, or one
      already low when it restarts.

    In either, the module can emit until T_off + T_cut after EMCON. That is at least 15.9 s plus the software's
    reaction time, against at least 0.9 s under (e). The EMCON latency limit is the TEST-PLAN owner's, and none is
    fixed. If one is fixed below T_off + T_cut, this row meets it only while the module honours W_DISABLE1# while it
    runs, while it boots and when it restarts, and the row says so. At a power-up under EMCON, and whenever EMCON
    asserts before the module has been turned on, the bound does not arise, because the rail never rises.
  - The residual risks, accepted, in the fault case and in the booting case:
    - (1) the module can emit for up to T_off + T_cut. In the fault case this needs two conditions, and in the
      booting case one, until E-05 (b) to (d) have run on the fitted firmware. If they fail, the fallback bounds the
      boots board B sees by the rail's fall, and a restart by AT+CFUN=1,1 or by the module's own firmware keeps
      T_off + T_cut on one event (above);
    - (2) the backstop can corrupt the module's flash. In the fault case this follows a failed sequence. In the
      booting case it follows whenever the boot and the host's sequence together exceed T_off, and under the fallback
      it follows every EMCON inside T_boot. The bound is TBD until E-12's cycle count has run. Effect: a module that
      fails E-12 is replaced, and the 5G bearer is down until then. SC-02 already records cellular data as going down
      with its module, as a named exception to NEED-03 for prototype 1 (`CONOPS.md:104` to `:116` at `b69f20db`).

    Neither arises at a power-up under EMCON. The cooperating case on a running module follows the maker's order.
    E-12 (e) still checks its flash over the same cycle count, because the order as built is a design claim until it
    is measured.
  - Release. The delay nodes discharge quickly. The rail comes back first, and the pin is released at least Tpr
    (100 ms) after it (HD v1.1 Figure 9 and Table 10), because R238 would otherwise raise the pin with VCC (section 4.5).
    E-12 (f) records it.
  - The requirement for the board B author (candidate levers, not choices):
    - **Not turned on: both stages at once.** EMCON may assert while `PCIE_PWR_EN2` is low, while `+3V3_S2A` is not
      up, or while the release's Tpr hold still holds FULL_CARD_POWER_OFF# low. Then both stages assert at once and
      latch until EMCON is released. The cases are every power-up of board B with EMCON asserted, EMCON while slot 2's
      CM5 is off or holds `PCIE_PWR_EN2` low, a CM5 that lowers `PCIE_PWR_EN2` while EMCON is asserted, and a
      re-assertion inside the Tpr hold. The rail never rises under EMCON.
    - **Turned on: the delays.** Only EMCON asserting while `PCIE_PWR_EN2` is high, the rail is up and the pin has been
      let rise starts the delays: FULL_CARD_POWER_OFF# at T_off, the supply at T_off + T_cut. Once started, they run
      to the end while EMCON stays asserted. Nothing the module or a host does restarts or cancels them; a restart of
      the module does not.
    - The "not turned on" level is read from `PCIE_PWR_EN2`, the rail and the release hold, never from the pin the
      backstop itself pulls, nor from U203's EN node, which the supply stage pulls. So the supply is never removed
      sooner than T_cut after the backstop's pin on a module that has been on, except under fallback (iii).
    - FULL_CARD_POWER_OFF#: Q207's gate from `5G_OFF` OR (`EMCON_ON` AND (T_off elapsed OR not turned on)). U211's
      gates 3 and 4 are spare with their inputs grounded (`gen_sch_b.py:733`; U211 pins 8 to 13), so one of them can
      form the outer OR without a new part.
    - Supply: U203's EN is `PCIE_PWR_EN2` directly. Slots 1 and 3 already use a pattern that applies here: a 10 k
      series resistor from `PCIE_PWR_EN` into a separate EN node, and a FET from `EMCON_ON` pulling that node low
      (`gen_sch_b.py:451`, `:478`). The FET's gate takes `EMCON_ON` AND (T_off + T_cut elapsed OR not turned on).
    - One candidate for "not turned on": a voltage supervisor on `+3V3_S2A` with a manual-reset input on
      `PCIE_PWR_EN2` and a delayed output on its own node. The node reads low while the rail is dead (for example,
      pulled up to `+3V3_S2A` itself). Through its own open drain it holds FULL_CARD_POWER_OFF# low while
      `PCIE_PWR_EN2` is low or the rail is below threshold, and for at least Tpr after. One part then gives three
      things: the release's Tpr, the Tpr that R238 lacks as drawn at every power-up and every `PCIE_PWR_EN2` cycle
      (section 4.5), and the level the stages read. The logic input that reads it must state Ioff, because
      `+3V3_S2A` can be up while +3V3_DEV is lost (L3).
    - If fallback (iii) is taken: a T_boot window, made in hardware like the delays, restarted by FULL_CARD_POWER_OFF#
      rising at the socket and by `5G_RESET` falling at U6's output, and read as "not turned on" while it runs. The
      input on `5G_PWROFF_n` states Ioff, and its leakage over the envelope is small against R238's 10 k and the pin's
      1.19 V VIH. Nothing is connected to RESET# (`5G_RST_n`), whose only pull-up is the module's 1.5 uA.
    - Each delay is made in hardware with no processor, and its tolerance over -40 to +85 C is stated from held
      sheets. At 15 s and more, an RC's leakage matters, so a timer or counter part is a candidate lever. Each
      delay's single faults are stated. A fault that shortens a delay fails toward the inhibit, and toward the flash
      risk. A fault that cancels a stage leaves the row on W_DISABLE1# alone, and it must be named.
    - Release order: the supply first, then the pin after Tpr.
    - Both stages hang on `EMCON_ON`, so they inherit L3 and L7, and L7's FET choice applies to the new FETs.
    - Once the rail is removable, SD-EMC-2 applies to the socket's live lines (section 4.5).
    - On release, the module boots again and slot 2's CM5 re-enumerates it, which E-07 already asks of the WiFi cards.
  - The requirement for the bridge software (outside this repository). This is care of the module's flash; the inhibit
    does not rest on it. On EMCON, the host that holds the module's AT port sends AT+CFUN=0 and waits for OK. It then
    pulls PERST# through slot 2's switch, and has the display owner write `5G_RESET` and then `5G_OFF` through U6
    (Figure 11's order). Its reaction time is bounded and given to the TEST-PLAN owner for T_off. If the module is
    booting when EMCON asserts, whatever started the boot (the booting case), the host runs the sequence as soon as
    the module answers AT, and it never drives RESET# low while the module boots (footnote 17 to Tables 10 and 14).
    At a power-up under EMCON the module never appears, and no sequence is owed. The bridge restarts the module only
    by hardware (the warm reset through `5G_RESET`, or the hard reset of Figure 15 through `5G_RESET` and `5G_OFF`),
    never by AT+CFUN=1,1, as Quectel recommends in PCIe mode (AT manual section 3.3.6 note 6). It starts no restart
    while EMCON is asserted, other than Figure 11's turn-off. A hardware restart is one board B can see, which
    fallback (iii) needs.
  - r4b's SD-B-03 (supply not gated by EMCON) is superseded for the EMCON case by this decision. `5G_OFF`'s software
    path stays as drawn and becomes the host's half of the sequence. The integrator carries this into r4b's record and
    into the board B generator's comment at `gen_sch_b.py:645` (section 8).
  - Taken by the session under the owner's standing rule of 26 Sep 2026.
- **SD-EMC-2: back-feed into a power-gated radio is bounded in hardware, not by a firmware contract.**
  - Options: (a) a firmware rule that every line into an unpowered radio is driven low or released (r4b O-06 (3)
    takes that route for PERST#); (b) a hardware bound on each line; (c) measure first and decide after.
  - Taken: (b). RF-002 excludes software. The E22 and E72 operate at 2.5 V and 1.9 V, inside what a 3.3 V line can
    lift a dead rail to, and the project's standing practice is to make the design indifferent to a COTS unknown before
    measuring it.
  - The requirement for the board B author: every line that a part powered during EMCON drives into a gated radio
    carries series resistance, a buffer powered from the gated rail, or a driver moved onto the gated rail, with
    arithmetic from held figures showing the rail stays below the radio's minimum operating voltage (for the RM520N-GL,
    3.135 V). Candidate levers, not choices:
    - tie each TPS22810's QOD to VOUT (RPD 250 to 400 Ohm at 5 V, SLVSDH0C electrical table), so a disabled switch
      actively holds its output down;
    - series resistors on the UART, modem, SPI and GPIO lines, sized against each bus's edge rate;
    - a series resistor on each card's PERST# (slots 1, 2 and 3);
    - moving each CP2102N's supply onto its radio's gated rail.
  - Bench E-04, E-07, E-09, E-10 and E-12 then confirm.
  - Taken by the session under the owner's standing rule of 26 Sep 2026.
- **SD-EMC-3: EMCON covers the kit's own transmitters; equipment on the outlets is outside it.**
  - Options: (a) gate the PoE and USB-C outlets by `EMCON_HW` on board A (U26's four gates are all used, so one more
    gate); (b) state the boundary in CONOPS and the operating procedure.
  - Taken: (b). D-05 speaks of the kit's radios; a self-powered device on a cable cannot be silenced by the kit
    whatever it does to the outlet.
  - The procedure line owed: "under EMCON, switch off or disconnect any external transmitter".
  - Taken by the session under the owner's standing rule of 26 Sep 2026.
- **SD-EMC-4: the QMX's USB VBUS is not a power path.** QRP Labs' schematics show VBUS unconnected on every published
  PCB revision (section 4.3), so `VBUS_QMX` stays ungated, on the condition that the fitted unit's revision is recorded
  at intake. The alternative, gating `VBUS_QMX` from EMCON on board B, adds a switch that protects nothing. Taken by the
  session under the owner's standing rule of 26 Sep 2026.
- **SD-EMC-5: the AW7915's W_DISABLE1# is never counted.** The inhibit is the supply removal (r4b's SD-B-02). No bench
  effort is owed to prove the pin, and E-07 tests the supply only. Taken by the session under the owner's standing rule
  of 26 Sep 2026.
- **SD-EMC-6 (re-decided in the third cycle): the EMCON toggle and the `TX_INHIBIT_n` conductor are accepted as the
  common element of every inhibit, on condition of a hardware EMCON lamp on board C.**
  - What it is: `SW_EMCON`, a single-pole toggle (`gen_sch_c.py:115` to `117`, `:211`), and the one conductor from
    board C through the panel ribbon, board B, `J_AB1`, board A and the mezzanine harness to board D (section 2). Every
    transmitter's inhibit starts there, the PA's two paths included (section 4.2).
  - **What the second version got wrong.** It called the TX lamp a hardware detection path, and it treated the panel's
    EMCON indication as a firmware reading of U9's copy of the line. It concluded that the two would expose a toggle at
    EMCON with the line not asserted. On the netlist (`v2/docs/records/rv-emc/readings/C-lamp-nets.txt`):
    - The TX lamp's sink is hardware: Q3's gate is `TR_APRS` through 1 k (`gen_sch_c.py:198`;
      `main-pcb-c-display.net:3962`). Its anode is not. D3's anode is `LED_RAIL` through R36, 300R
      (`gen_sch_c.py:197`; `:4110`). `LED_RAIL` exists only while the P-FET Q1 conducts (`:3812`). Q1 conducts only
      while Q2 is on (`Q1_G` through R18 to `Q2_D`, `:3951`, `:3955`). Q2's gate is the panel RP2040's `PANEL_PWM`
      (U3 pin 11, GPIO8) through R19, with R20 at 100 k to GND (`gen_sch_c.py:185` to `187`; `:3911`, `:3958`). So
      Q2 is off whenever the controller is not driving the pin. In reset, no function drives the pin and the pad's
      pull-down is enabled (RP2040 datasheet, section 2.19.6.3, Table 341, which covers GPIO0 to GPIO29: PDE 0x1; and
      FUNCSEL's reset to NULL, section 2.19.6.1, Table 285, as L1 reads for GPIO21), so the lamp is dark.
    - The rail also passes the LIGHTING toggle, pole 1, which is open in BLACKOUT (`gen_sch_c.py:182` to `184`;
      `LED_RAIL_SW` `:3833`).
    - The other indication, "show EMCON on the e-paper, MASTER CAUT steady", is part of the software hold
      (`PANEL.md:164`). It is sent by the bridge on the slot that owns the display (`PANEL.md:176`), and MASTER CAUT's
      anode is the same `LED_RAIL` (R22 to `MCAUT_A`, `:3883`).

    So as drawn, both indications need the panel RP2040 running. The e-paper and MASTER CAUT also need the
    display-owning bridge. Every emissive one is dark in BLACKOUT. None is independent of software, which NEED-08's
    "does not depend on software" asks of the action it is meant to confirm. With the controller dead, in reset, or
    with the kit in BLACKOUT, a common-element fault is not indicated at all.
  - Options:
    - (a) accept the element with the existing indications, stating the bound above;
    - (b) a two-pole toggle and a second, separately routed inhibit conductor to board D. That changes the panel part,
      the panel ribbon, `J_AB1` and the mezzanine harness contracts, and the flat cables would still carry both
      conductors side by side;
    - (c) a hardware EMCON lamp on board C, lit from the lines' state with no processor in its path, and fed from
      `LED_RAIL_SW` (after the LIGHTING toggle, ahead of Q1). The MAIN ring is already fed that way (R39, 470R, from
      `LED_RAIL_SW` to `MAINRING_A`, `gen_sch_c.py:202`; `:3862`), and `PANEL.md:113` calls it "alive whenever the LED
      rail is present";
    - (d) move the TX lamp's feed to `LED_RAIL_SW`. That still detects only after a PTT press keys a transmitter
      through the fault, and only on VHF.
  - Taken: (c). Why: the fault that matters is a toggle at EMCON with the line not asserted, and only (c) indicates
    it without firmware. The second version rejected (c) because it "duplicates the first indication". That rested on
    the wrong premise: (c) is the only indication that does not depend on the controller. (a) leaves detection to
    firmware and the bridge. (d) detects only after emission. (b) costs three interface contracts and still does not
    separate the conductors physically. (c) changes board C and the face plate only: both lines are already on board
    C, and no board-to-board interface, stackup or radio part changes.
  - The requirement for the board C author (candidate levers, not choices):
    - The lamp lights only while BOTH `TX_INHIBIT_n` and `EMCON_HW` read LOW at board C. For example, a 74LVC1G02 NOR
      on board C's +3V3 drives an N-channel sink whose on-resistance is stated at that drive (L7's rule). Reading
      both lines means the lamp also exposes U9's output stuck high, which would release every row on `EMCON_HW`
      while the PA's path (b) and the SA868 stay inhibited.
    - The lamp is fed from `LED_RAIL_SW` through its own resistor, not from `LED_RAIL`, so it lights with the controller
      dead or in reset. Its current is fixed at a level the PANEL.md writer sets against the NVG mode, which dims only
      what `PANEL_PWM` feeds. The MAIN ring is the precedent of an undimmed lamp on `LED_RAIL_SW`. Its colour is red
      or amber, because NVG mode shows "red and amber indicators only" (`PANEL.md:155`).
    - Its inputs load both lines. They are parts that state Ioff, and they are counted in R4T-D37's sums for
      `TX_INHIBIT_n` and `EMCON_HW` with the panel unpowered.
    - It sits beside `SW_EMCON` and needs one light-guide hole in the face plate. That is the plate owner's change.
  - Residual risk, accepted, with its true bound. With the lamp built, a common-element fault is indicated without
    firmware whenever board C has its +5 V and LIGHTING is at DAY or NIGHT. It is not indicated in two cases:
    - in BLACKOUT, where the lamp is dark by the operator's choice, as every emissive indicator is. The e-paper's
      EMCON page is non-emissive, but it needs the panel RP2040 and the display-owning bridge;
    - with board C's +5 V gone, where the whole panel is dark.

    So a fault that arises after the operator has checked the lamp and selected BLACKOUT stays hidden until lighting is
    restored. Until the lamp is built, the bound is the as-drawn one above: no indication without the panel controller.
  - The procedure lines owed: "after setting EMCON, confirm the EMCON lamp before relying on it", and "set EMCON and
    confirm the lamp before selecting BLACKOUT".
  - Bench E-02 adds the shared-element cases and the lamp's independence from the controller (section 6).
  - Taken by the session under the owner's standing rule of 26 Sep 2026.

## 6. Bench tests owed (for TEST-PLAN; none has run, nothing is built)

The functional check in `TEST-PLAN.md:46` reads "EMCON silences every transmitter (measured with the SDR)". EMCON as
ruled removes the SDR's supply (section 4.17), so that line cannot be met with the kit's own SDR.

Every row below uses an external spectrum analyser or RF power meter. Each antenna port connects through an attenuator
or to a dummy load, where the band plan requires it. The pass line in every row is "no emission above the instrument's
noise floor in any band the radio supports", at a resolution bandwidth the TEST-PLAN owner fixes. Record the module
firmware revisions, the RM520N-GL's recorded configuration and the fitted QMX PCB revision.

| Id | Radio | Procedure | Pass |
|---|---|---|---|
| E-01 | SA868 | r6d's bench rows (`v2/docs/records/r6d/r6-decisions.md` section 5): U1 fitted, unfitted and shorted; U16 bits forced high under EMCON; pin 5's "1" threshold and input current measured | no carrier in any state; the threshold is at or below 2.677 V |
| E-02 | 30 W PA and the common element | EMCON asserted with PTT held, then each downstream single fault: A's `J_AB1` unplugged; D's U1 unfitted; a firmware image that drives A's `PA_SW_EN` high. Then the shared-element cases of SD-EMC-6, into a dummy load, each with LIGHTING at DAY and at NIGHT: (1) the toggle at EMCON with its lug 1 lead open, PTT held; (2) the toggle at EMCON with U9's output forced high; (3) EMCON correctly asserted with the panel RP2040 held in reset (`C_RUN` low) and then with it unflashed; (4) EMCON released with the controller in reset. Then (1) with LIGHTING at BLACKOUT | downstream faults: no RF at the PA output; `+13V8_PA`, VGG and K1 recorded. (1): both paths release, as the design predicts, and the EMCON lamp stays dark; the e-paper shows EMCON not asserted when the controller and the display owner run. (2): the EMCON lamp dark. (3): the EMCON lamp lit, with the controller not running. (4): the lamp dark. BLACKOUT: every lamp dark, as the design intends; recorded, not a failure. The TX lamp's behaviour is recorded in each case; it is not a pass condition, because its feed needs `PANEL_PWM` |
| E-03 | QMX | EMCON asserted: +12V_HF off, VBUS_QMX live, USB enumeration attempted from the host; current into VBUS | no RF at the BNC; VBUS current under 1 mA |
| E-04 | RockBLOCK 9704 | EMCON asserted with `RB_IEN`, `RB_CTRL` and `RB_RXD` driven high by U6 and U18; V_EXT_RAW and every reachable module rail read; a 10 min watch covering a ring-alert slot | no RF at the SMA; the module rails stay below the level SD-EMC-2 sets |
| E-05 | RM520N-GL, W_DISABLE1# stage | (a) registered, full uplink, then W_DISABLE1# low: time to silence; (b) power-up with the pin already low, watched from rail-up to 120 s (the LTE precedent describes the pin's effect as an edge, section 4.5; under SD-EMC-1 a power-up with the pin low arises only when a stage has failed); then the pin driven low at instants during boot, each watched to 120 s, in boots started four ways: FULL_CARD_POWER_OFF# rising (a turn-on), the end of a warm reset (RESET# pulsed for TRST#, HD v1.1 Figure 14), the end of a hard reset (Figure 15), and AT+CFUN=1,1; the instants run from the boot's start to the module's first AT answer (at least 0.5 s, 2 s, 5 s and 10 s after the start, and at the first answer). This is SD-EMC-1's booting case, which decides its fallback; (c) AT+CFUN=1 and AT+CFUN=1,1 sent with the pin low; (d) a warm reset and a hard reset with the pin low. (c)'s AT+CFUN=1,1 and (d) are the booting case's restart with the pin already low, each watched to 120 s from the restart; (e) a host request to go online over QMI and over MBIM, as a connection manager issues it, with the pin low, from slot 2's host over PCIe and from bank 3's host over USB; (f) AT+QCFG=? recorded on the fitted firmware; for `airplanecontrol`, `airplane` and any other listed parameter that names airplane mode, W_DISABLE or RF, the value read, then each documented value set in turn, with (a) to (e) repeated under each and the original values restored; (g) each case per firmware revision fitted. Run with both of SD-EMC-1's hardware stages disabled (the FULL_CARD_POWER_OFF# backstop and the supply removal, in their at-once and delayed forms), or with W_DISABLE1# driven directly, so the pin alone is measured | no emission in (b) to (e) under the configuration the kit will ship with, and in (b)'s boot instants none after the time to silence that TEST-PLAN sets for (a); a boot instant or a restart in (b) to (d) that fails takes SD-EMC-1's fallback (iii); in (a) silence within the time TEST-PLAN sets; AT+CFUN? and `+QIND` reports recorded; the configuration values that pass are written into the provisioning record |
| E-06 | LimeSDR | EMCON while streaming TX; `+5V_LIME` and USB D+ transient recorded | no RF at either port |
| E-07 | AW7915-AED (x2) | EMCON while the kit-to-kit link carries traffic; `+3V3_M2C{1,3}` recorded with PERST0#, PEWAKE0# and REFCLK live; S{1,3}A_EN's low level recorded (L7); release, then re-enumeration | no RF on either IPEX; the rail below the SD-EMC-2 level; the card re-enumerates |
| E-08 | CM5 WiFi and BT (x6) | each radio in AP mode, beaconing and BLE advertising, then EMCON; each pin's low level recorded (L7); then the +3V3_DEV fault of L3 once its remedy exists | beacons and advertising stop within the time TEST-PLAN sets; they stay stopped; each pin under the CM5's input-low level |
| E-09 | E22-900M30S | EMCON with slot 3 clocking SPI and TXEN high; `+5V_LORA` recorded | no RF at the LoRa jack; the rail below 2.5 V less a margin |
| E-10 | E72 (x2) | EMCON with each CP2102N sending and RTS and DTR high; `+3V3_ZB` recorded | no RF at 2.4 GHz from either module; the rail below 1.9 V less a margin |
| E-11 | the lines | panel unplugged; `J_AB1` unplugged on A alone; +3V3_DEV, +3V3_D8 and A's +3V3 held at 0 V and in their 0 to 1.65 V bands; each STM32 and the RP2040 loaded with a firmware that drives its `EMCON_HW` pin high; `EMCON_ON` and each open drain's gate and drain recorded | every gate reads EMCON asserted (after L1 to L4 and L7 are remedied) |
| E-12 | RM520N-GL, FULL_CARD_POWER_OFF# and supply stages (SD-EMC-1) | (a) registered, full uplink, then FULL_CARD_POWER_OFF# driven low with no AT+CFUN=0 and W_DISABLE1# left high: whether RF stops, and the time to RF off and to module off; (b) the same after AT+CFUN=0 and its OK: Tpd; (c) with W_DISABLE1# already low, AT+CFUN=0's response time, and the host's whole sequence from EMCON (panel report, AT+CFUN=0, OK, PERST#, RESET#, `5G_OFF`) timed over repeated runs, registered and unregistered: this sets T_off; (d) the staged EMCON as built, cooperating (the host's sequence runs) and withheld (no handshake): times to silence, to the pin falling, and to the supply removal; T_off and T_cut recorded; (e) flash integrity: the cooperating case of (d) and the withheld case each repeated for a cycle count the TEST-PLAN owner fixes, then the module booted after every cycle: firmware revision, IMEI, the AT+QCFG values of E-05 and a registration checked; (f) release: the rail and the pin recorded, Tpr measured, the module re-enumerated; (g) `+3V3_M2C2` recorded with PERST#, REFCLK, the PCIe TX pair, USB D+/D- and PEWAKE# live; (h) power-up under EMCON: the kit powered with the toggle locked at EMCON, +3V3_DEV, `SLOT_EN2`, `PCIE_PWR_EN2`, `+3V3_S2A`, FULL_CARD_POWER_OFF#, W_DISABLE1# and RF recorded from power-on until slot 2's CM5 has booted and 120 s beyond; then, from a power-up with EMCON released, EMCON asserted while slot 2's CM5 is booting, before it raises `PCIE_PWR_EN2`; (i) the booting case, cause by cause, with the host's sequence running: (1) continuing from (h)'s cold start under EMCON, and repeated after an EMCON on a running module, EMCON released and then re-asserted inside the release's Tpr hold; (2) EMCON asserted at the boot instants of E-05 (b) and at the first AT answer, in boots started by an EMCON release, by a cold start of the kit with EMCON released, by slot 2's CM5 lowering and re-raising `PCIE_PWR_EN2` (a short cycle and a long one), by a warm reset through `5G_RESET`, by a hard reset through `5G_RESET` and `5G_OFF`, and by AT+CFUN=1,1 from slot 2's host and from bank 3's; (3) EMCON asserted on a running module, and then, before T_off, each of the resets of (2) and a lowering of `PCIE_PWR_EN2`; in every run `PCIE_PWR_EN2`, `+3V3_S2A`, FULL_CARD_POWER_OFF#, W_DISABLE1#, `5G_RESET` and RF recorded, with the time from the boot's start to the first AT answer and whether the host's sequence finished before T_off; in the AT+CFUN=1,1 runs also RESET#, CLKREQ#, PEWAKE# and the LED pin, with RESET# probed at an input current far below its 1.5 uA pull-up, to find whether any socket pin marks a restart the module starts; one run with PERST# pulsed alone through slot 2's switch records whether that restarts the module; (e)'s flash checks after each, over the same cycle count | (a) to (c) recorded as found (they set T_cut and T_off, not a pass); (d) the cooperating sequence completes before T_off, and there is no emission after T_off + T_cut in either case; (e) the module boots and every recorded value is unchanged after every cycle, in both cases; (f) the pin rises at least 100 ms after the rail, and the module re-enumerates; (g) the rail stays below 3.135 V less a margin; (h) `+3V3_S2A` never rises and there is no RF, in both parts; (i) (1) the pin never rises, the rail falls at once and there is no RF, and the module then boots with every value of (e) unchanged; (2) and (3) no emission after T_off + T_cut in any cause; after a lowering of `PCIE_PWR_EN2` under EMCON the rail does not rise again; emission before T_off + T_cut, the boot time and every flash check recorded per cause as the bound of SD-EMC-1's residual risks in the booting case (T_boot of the fallback is taken from here, over every cause); whether a socket pin marks the AT+CFUN=1,1 restart, and whether PERST# alone restarts the module, recorded, not a pass |

## 7. What remains open

| Item | Bound | Owner |
|---|---|---|
| L1 firmware pins on `EMCON_HW` | 3.46 V worst case against 0.8 V VIL (tool `5aece264`) | board B author (one 74LVC1G34 for U41, U51, U61's taps); board C author (U3's GPIO21 behind a 74LVC1G34); R4T-D40 |
| L2 the line's hold with its source gone | UNDECIDED as drawn (no Ioff rows; Q11's IGSS at 25 C only); A alone 1.0 V against 0.8 V; with single-gate remedies, 10 k on both boards fails at 1.00 V and R102 10 k 1% with R58 4.7 k 1% passes at 0.45 V (R4T-F8 third statement) | board A author (R102, two SN74LVC1G08); board B author (R58, four SN74LVC1G08, Q11, the candidate's own sum) |
| L3 +3V3_DEV loss on B | fail-open for 9 radios (6 CM5, 2 AW7915, 1 RM520N-GL); `LIME_EN`, `RB_EN`, `E22_EN` UNDECIDED (0.00 V, no Ioff row) until single gates; `E72_EN` PASS | board B author (O-14; R4T-F9) |
| L4 gate supplies outside the specified range | quads: 0 to 1.65 V unspecified; single gates: above 0 and below 1.65 V unspecified | board B author (O-24); board D author and E-01, E-11; board A author (U26) |
| L6 RF-002 instrument model gaps; `J_QMX` declaration | the tool's FAILs are not all real | tools author (r4t) |
| L7 2N7002 on `EMCON_ON` driven at about 3.3 V | RDS(on) limits stated only at VGS 5 V and 10 V, all at 25 C (the 3 V and 4 V output curves are typical, 25 C); channel resistance at 3.1 to 3.5 V TBD | board B author; bench E-07, E-08, E-11 |
| SA868 pin 5 "1" threshold | the design gives 2.677 V or more; the maker states nothing | bench E-01 |
| RM520N-GL: SD-EMC-1's circuit | not drawn; subject to L3 once drawn (both stages hang on `EMCON_ON`). EMCON before the module has been turned on (every power-up under EMCON, slot 2 off or `PCIE_PWR_EN2` low, a re-assertion inside the Tpr hold): both stages at once and latched, the rail never rises. EMCON on a module that has been turned on: T_off at least the software's reaction time plus 15 s (AT+CFUN's maximum) until E-12 (c) measures the handshake; T_cut at least 0.9 s, no maker maximum (Tpd has none); once started the delays run to the end whatever the module does. On release, the pin at least Tpr (100 ms) after the rail | board B author; bridge software (reaction time, section 8); bench E-12 (h) and (i) for the power-up rule |
| RM520N-GL: emission in the fault case (firmware ignores W_DISABLE1# and the host's sequence fails) and in the booting case (the module booting when EMCON asserts, or restarting while the delays run, whatever started the boot: an EMCON release, a power-up with EMCON released, slot 2's CM5 cycling `PCIE_PWR_EN2`, a warm or hard reset through U6, AT+CFUN=1,1 from either host, a restart the firmware starts itself; and the module misses the pin while booting) | up to T_off + T_cut after EMCON, at least 15.9 s plus the software's reaction time, for every cause; two conditions in the fault case, one in the booting case; none at a power-up under EMCON; accepted in SD-EMC-1, with fallback (iii) named in advance if E-05 (b) to (d) fail | TEST-PLAN owner (the latency limit); bench E-05 (b) to (d), E-12 (i) |
| RM520N-GL: flash integrity | TBD in the fault case, and in the booting case whenever the boot and the host's sequence exceed T_off (Quectel warns of corruption), accepted in SD-EMC-1; certain at every EMCON inside T_boot if the fallback is taken; none owed at a power-up under EMCON; the cooperating case on a running module follows the maker's order, checked by E-12 (e) over the same cycle count; VCC removed from the OFF state inside the Tpr hold is unstated, recorded by E-12 (i) | bench E-12 |
| RM520N-GL: boot time | the maker states none after a turn-on or a reset (Figures 9, 14 and 15 draw a Booting phase with no duration); it sets how often the booting case costs a handshake, and T_boot if the fallback is taken | bench E-12 (i), over every cause |
| RM520N-GL: restarts board B cannot see (only if fallback (iii) is taken) | AT+CFUN=1,1 from either host, a restart after a firmware upgrade, a crash or watchdog restart: no held document says a socket pin marks them, so the fallback's window cannot restart on them; bound T_off + T_cut after EMCON, on one event (such a restart within T_boot before EMCON or before T_off after it); narrowed by the bridge's hardware-restart rule to restarts the firmware starts itself; closed if E-12 (i) finds a socket pin that marks them | bench E-12 (i); bridge software (section 8); if E-12 sees the module restart with no host command, option (e) is the named next step |
| RM520N-GL: W_DISABLE1# behaviour and configuration | maker-documented firmware mode; untimed; unstated in boot and hang; a stored setting may disable it (LTE precedent), writable from slot 2's host over PCIe or bank 3's over USB | bench E-05; provisioning owner (section 8) |
| RM520N-GL: FULL_CARD_POWER_OFF# rises with VCC as drawn (R238 to `+3V3_S2A`) | Tpr near 0 against the maker's 100 ms minimum, at every cold power-up and every `PCIE_PWR_EN2` cycle, and, under SD-EMC-1, at every EMCON release | board B author (one supervisor on `+3V3_S2A` with its manual reset on `PCIE_PWR_EN2`, SD-EMC-1); bench E-12 (f) |
| PA and every row: the common element | accepted on condition of a hardware EMCON lamp on board C (SD-EMC-6). As drawn, no indication is independent of the panel controller. With the lamp, no indication in BLACKOUT or with board C unpowered | board C author (the lamp); face plate owner (one light-guide hole); PANEL.md writer (its current against NVG); procedure owner; bench E-02 |
| Back-feed: RockBLOCK, E22, E72 x2 | TBD; module minimum operating voltages 2.5 V (E22) and 1.9 V (E72) inside a 3.3 V line's reach | board B author (SD-EMC-2); bench E-04, E-09, E-10 |
| Back-feed: AW7915 x2, and the RM520N-GL once removable | PEWAKE 0.33 mA; PERST# drive TBD (DS40068 states none); REFCLK HCSL; for the RM520N-GL also USB from slot 3's hub and the PCIe TX pair, against its 3.135 V minimum | board B author (SD-EMC-2); bench E-07, E-12 |
| Candidate merge | closed: main `458b2873` merged A, B and D; B and D equal the copies read here in every net and part, and A differs only in its front end (section 1.1) | none |

## 8. Hand-offs to other writers (this stream writes only this file and `drafts/`)

- **Board B author.**
  - SD-EMC-1's stages for slot 2:
    - the power-up rule: if EMCON asserts before the module has been turned on (`PCIE_PWR_EN2` low, the rail not up,
      or the release's Tpr hold still on), both stages act at once and latch until EMCON is released, so the rail
      never rises under EMCON. That is every power-up of board B with the toggle locked at EMCON;
    - on a module that has been turned on, the maker's order: the FULL_CARD_POWER_OFF# backstop at T_off through a
      spare U211 gate into Q207, and the supply removed at T_off + T_cut on the slot 1 and 3 pattern. Once started,
      the delays run to the end while EMCON stays asserted; a restart of the module does not cancel them;
    - the "not turned on" level read from `PCIE_PWR_EN2`, the rail and the release hold, never from the backstop's own
      pin or U203's EN node;
    - the release order, with the pin at least Tpr after the rail;
    - the as-drawn Tpr of `5G_PWROFF_n` at every power-up and `PCIE_PWR_EN2` cycle (R238 to the module's own rail).
      One supervisor on `+3V3_S2A`, with its manual reset on `PCIE_PWR_EN2`, can serve this, the release's Tpr and the
      "not turned on" level (SD-EMC-1);
    - all of it subject to L3 (the stages hang on `EMCON_ON`), with O-14's remedy;
    - if E-05 (b), (c) or (d) fails, fallback (iii): a T_boot window restarted by FULL_CARD_POWER_OFF# rising at the
      socket and by `5G_RESET` falling at U6, read as "not turned on" while it runs; nothing connected to RESET#,
      whose only pull-up is the module's 1.5 uA. Restarts by AT+CFUN=1,1 or by the module's own firmware stay a
      named residual (SD-EMC-1).
  - L2's R58 4.7 k 1%, four SN74LVC1G08 and Q11; L7's FET choice; L1's 74LVC1G34; O-14 for L3.
  - SD-EMC-2's back-feed bounds, now including `J_M2C2`.
  - SD-B-03 is superseded for the EMCON case.
- **Board A author.** L2's R102 10 k 1% and two SN74LVC1G08 in place of U26's `EMCON_HW` sections (R4T-F8 third
  statement).
- **Board C author.**
  - L1's 74LVC1G34 in front of U3's GPIO21 (R4T-F5, R4T-D40).
  - SD-EMC-6's EMCON lamp: lit only while both `TX_INHIBIT_n` and `EMCON_HW` read LOW, no processor in its path, fed
    from `LED_RAIL_SW`, with inputs that state Ioff.
  - Found while doing this, and not decided here, because the TX lamp is the RF hazard lamp and not an EMCON
    inhibit: `PANEL.md:5` reads "The lines that act without any software are MAIN PWR, EMCON and the TX lamp", and
    `:113` lists the TX lamp under "Hardware LEDs, no software". Its sink is hardware, but its feed is `LED_RAIL`,
    which exists only while firmware drives `PANEL_PWM` (`gen_sch_c.py:182` to `187`, `:197`). Either the feed moves
    to `LED_RAIL_SW`, as the MAIN ring's is, or the text says the lamp needs the controller.
- **Face plate owner.** One light-guide hole for the EMCON lamp beside `SW_EMCON`.
- **Bridge software and provisioning (outside this repository).**
  - On EMCON, run HD v1.1 Figure 11's sequence from the host that holds the module's AT port: AT+CFUN=0, wait for
    its OK, then PERST#, then `5G_RESET` and `5G_OFF` through the display owner. This protects the module's flash; the
    inhibit does not rest on it. If the module is booting when EMCON asserts, whatever started the boot (SD-EMC-1's
    booting case), run it as soon as the module answers AT, and never drive RESET# low while the module boots
    (footnote 17 to Tables 10 and 14).
  - Restart the module only by hardware: the warm reset through `5G_RESET`, or the hard reset of Figure 15 through
    `5G_RESET` and `5G_OFF`. Never use AT+CFUN=1,1, which Quectel does not recommend in PCIe mode (AT manual section
    3.3.6 note 6). Start no restart while EMCON is asserted, other than Figure 11's turn-off. A hardware restart is
    one board B can see; this is care, and the inhibit does not rest on it.
  - Bound the reaction time from the panel controller's EMCON report to AT+CFUN=0, and give it to the TEST-PLAN owner
    for T_off.
  - Record the RM520N-GL's firmware revision and the values E-05 lists. Verify both at every boot, from each host that
    reaches an AT port (slot 2 over PCIe, bank 3 over USB). Report the 5G module as not inhibited by its pin if either
    differs. This is a detection rule; it does not replace SD-EMC-1's hardware stages.
- **CONOPS writer.** B and D are merged (`458b2873`). Neither that commit nor `b69f20db`, which moved section 4b down
  14 lines, changed its text, so section 4b (`:294` to `:319` at `b69f20db`) still describes the B19 and D9 from
  before the merge:
  - the CM5 row becomes "open drain from the EMCON line";
  - the WiFi card row becomes "supply removed";
  - once SD-EMC-1 is drawn, the 5G row becomes "never powered under EMCON; on a running module, W_DISABLE1# at once,
    FULL_CARD_POWER_OFF# by hardware after T_off, supply removed after a further T_cut".

  Add SD-EMC-3's boundary, SD-EMC-6's lamp, and the procedure lines of SD-EMC-3 and SD-EMC-6.
- **PANEL.md writer.**
  - `PANEL.md:35` names U9 a 74LVC1G34; main's board C carries a 74LVC1G17 (`gen_sch_c.py:166`). `PANEL.md:128`
    describes the pre-candidate state.
  - Add the EMCON lamp's semantics: lit in hardware while both lines are LOW, at a fixed current set against the NVG
    mode, dark in BLACKOUT.
  - Correct the TX lamp text above once the board C author has chosen.
- **TEST-PLAN writer.** Take in E-01 to E-12. Correct `TEST-PLAN.md:46`'s "measured with the SDR". Fix the EMCON
  latency limits E-05, E-08 and E-12 refer to, E-12's cycle count, T_off from E-12 (c), and the boot instants of E-05 (b)
  and E-12 (i), which are run for every boot cause SD-EMC-1 names.
- **Requirements registry (i1).** S-01 closes on the candidate B for the CM5 radios and the card supplies, subject to
  L1, L2, L3 and L7. S-02 is the tools item L6. REQ-030 and REQ-032 are not met for the 5G module until SD-EMC-1 is
  drawn. Cite this file from NEED-08's verification.
- **Tools (r4t).** Model the Q11 to `EMCON_ON` inverter and open drains, the shunt-fed socket rail, the LVC32A OR, the
  TLV75801P enable and path (b) of the PA. Move `J_QMX` from OWED to ACCESSORIES, citing QRP Labs' schematics for PCB
  Rev 1, 2, 3/4 and 5.
- **Integrator.**
  - Carry SD-EMC-1's supersession of r4b's SD-B-03 into r4b's record and into the board B generator's comment at
    `gen_sch_b.py:645`, so that the two records agree after the merge.
  - The round-6 candidates are merged (`458b2873`). Section 1.1 records that main's B, C and D equal the copies read
    here and that its A differs in the front end only, so no row waits on a merge.
- **SOURCES.yaml writer.** File the four Quectel AT and QCFG manuals and the four QMX schematic PDFs from
  `drafts/datasheets/` of `fnd/rv-emc` (listed in `v2/docs/records/README.md`), with their URLs and sha256. The JSCJ 2N7002 sheet is filed since `ccf5808e`
  (`logic-nfet-2n7002`), so that part of this hand-off is done.

## 9. What changed in the fifth cycle (the fourth checker's one blocking item and seven minor ones)

1. **The exposure of a booting module was bounded to a reversal (blocking 1).** The checker was right on the defect.
   Section 0 and SD-EMC-1 named only EMCON re-asserted while the module boots after a release. Under option (ii),
   every boot of a module that has been turned on carries the same single-condition exposure. Fallback (iii) was
   keyed to the rail and the pin, so it could not see a boot after a reset.
   - Checked against the maker. HD v1.1 Figure 14 and Table 13 (printed page 36): the warm reset keeps VCC and
     FULL_CARD_POWER_OFF# high, "Reset baseband chip IC only", and ends in Booting. Figure 15 and Table 14 (printed page
     37): the hard reset also ends in Booting, but it holds FULL_CARD_POWER_OFF# low for Toff (900 ms minimum) and
     raises it again with VCC up. So on board B a hard reset is `5G_RESET` and `5G_OFF` together, and the pin does
     pass through a rising edge. That does not change the checker's conclusion, because "turned on" was read from the
     rail and the release hold, which neither reset touches. The AT manual's `<rst>` 1, "Reset UE", is on page 29.
     Its section 3.3.6 notes 5 and 6 (page 43) add a restart after a firmware upgrade, and Quectel's advice to restart
     by hardware in PCIe mode, not by AT+CFUN=1,1.
   - Fixed as the checker set out. The booting case is defined by the module's state, and each cause is named: an
     EMCON release; a power-up of the kit or of slot 2 with EMCON released; slot 2's CM5 cycling `PCIE_PWR_EN2`; a
     warm or hard reset through U6; AT+CFUN=1,1 from either host; and a restart the firmware starts itself. The case
     covers a boot with the pin already low (a restart while the delays run) as well as a pin that falls during a
     boot. The list is stated as what the held documents name, not as complete. Any other restart takes the bound of
     a restart board B cannot see; PERST# alone, which HD v1.1 does not describe as a restart, is the one E-12 (i)
     now checks.
   - The delays are now required to run to the end whatever the module does, so the T_off + T_cut bound holds for
     every cause.
   - "Turned on" also reads `PCIE_PWR_EN2`, so a CM5 cycle is seen whatever the rail does. The supervisor candidate
     takes that pin as its manual reset, which also gives Tpr after every such cycle.
   - Restated in: section 0; 4.5 (the required stages, the default subject to L3, a new controller-failure bullet,
     the maker's reset statements, what the documents do not state, the QCFG bullet, proof); table row 5; SD-EMC-1
     (history, the booting case, why not (iii), the fallback, the emission bound, residual risks (1) and (2), and the
     board B and bridge requirements); E-05 (b) to (d); E-12 (i); section 7 (four rows restated, one added); and
     section 8.
   - Fallback (iii) takes both of the checker's options. Its window restarts on every boot start board B can see:
     FULL_CARD_POWER_OFF# rising at the socket (every turn-on, a hard reset included) and `5G_RESET` falling at U6
     (a warm reset). It reads `5G_RESET` and not RESET#, because RESET#'s only pull-up is the module's 1.5 uA
     (Figure 12).
   - Restarts by AT+CFUN=1,1 or by the module's own firmware are invisible to board B, as far as any held document
     says. They are a named residual: bound T_off + T_cut on one event, narrowed by the bridge's new hardware-restart
     rule, and closed if E-12 (i) finds a socket pin that marks them. Option (e) on every EMCON is the named next
     step if E-12 sees the module restart with no host command.
   - E-05 (b) runs its boot instants after a turn-on, a warm reset, a hard reset and AT+CFUN=1,1. (c) and (d) are
     named as the restart with the pin already low. E-12 (i) now:
     - runs EMCON at the boot instants for every cause;
     - adds each reset, and a lowering of `PCIE_PWR_EN2`, after EMCON on a running module;
     - looks for a socket pin that marks a restart the module starts.
2. **Minor items.**
   - (1) L1 no longer reads OD 0x0 as "output disabled". The RP2040 pin's output is off at reset for two reasons:
     FUNCSEL resets to NULL (section 2.19.6.1, Table 285), and SIO's output enable resets to input (Table 24). OD 0x0
     leaves the output enable to the selected function.
   - (2) The SA868's bottom level is 2.677 V, as r6d's table gives it with its leakage stand-in. Corrected in 4.1,
     E-01 and section 7.
   - (3) Section 0, 4.5's required default and SD-EMC-1's stages now say "subject to L3".
   - (4) SD-EMC-1's power-up trace adds U203's input. That input is `+5V_S2`, whose only source on board B is
     `J_5V_S2` from board A's U5 (B:19488, A:9538). So the rail has no input before `SLOT_EN2` rises, whatever the
     CM5 does.
   - (5) claims_check is re-run on this version. Its sidecar `v2/docs/records/rv-emc/readings/claims_check_on_EMCON.judged.txt`
     records the sha256 of the document it judged.
   - (6) Section 1.1 states `netcompare.py`'s limit: it compares net nodes and part values only.
   - (7) Section 1.1's board C generator citation is re-pointed to main.
3. **Drift since the fourth version, checked.** Main moved to `b69f20db` (case margins and records). That commit
   changes no netlist or generator, and none of `PANEL.md`, `TEST-PLAN.md`, `pcb_rules.yaml` or the review. In
   `CONOPS.md`, section 4b moved down 14 lines with its text unchanged, and section 2a now records SC-02. The CONOPS
   citations are re-anchored to `:307`, `:294` to `:319` and `:104` to `:116`. The check is in
   `v2/docs/records/rv-emc/readings/main-b69f20db-drift.txt`. Main then moved on to `ccf5808e` while this version was written. Its
   six commits modify no cited file. They file the JSCJ 2N7002 and the LVC single-gate sheets in `v2/vendor/`, so
   section 1.2, L4 and the SOURCES.yaml hand-off now cite them there, and L4 reads U11's Ioff row
   (`v2/docs/records/rv-emc/readings/main-ccf5808e-drift.txt`). Then `d90f30e4` changed board P in 3 nets and 5 parts, none a radio,
   and `01469100` is a plan checkpoint (`v2/docs/records/rv-emc/readings/main-01469100-drift.txt`).

## 9b. What changed in the fourth cycle (the third checker's one blocking item)

The "reversal case" below was widened to the booting case in the fifth cycle (section 9).

1. **SD-EMC-1 did not say what the stages do when the kit powers up with EMCON already asserted (blocking 1).** The
   checker was right. Both delays ran from `EMCON_ON`, which rises with +3V3_DEV at a cold power-up. `SW_EMCON` is a
   locking toggle whose level holds through a power loss (`gen_sch_c.py:115` to `116`, `:207` to `211`), so such a
   power-up is routine. The module would have booted under EMCON, since U203's EN is `PCIE_PWR_EN2` directly
   (`B-r6cand-pcb-b-compute.net:21439`) and R238 raises FULL_CARD_POWER_OFF# with VCC. The backstop would then have
   fired with no handshake at every such power-up, and the third version's bound of both residual risks to the fault
   case was too narrow. This is the same defect class as the second checker's blocking 1.
   - The fix taken is the checker's recommended one, option (ii) of SD-EMC-1's new power-up block. If EMCON asserts
     before the module has been turned on (the rail not up, or the release's Tpr hold still on), both stages act at
     once and hold. The module is never powered under EMCON, and no handshake is owed. The delays apply only to a
     module that has been turned on.
   - The sequence that makes every cold power-up this case is traced on the netlists. U25's EN is tied to +5V_DEV,
     and `PANEL_5V` is +5V_DEV through F1. `SLOT_EN2` is held low by board A's R34 until the panel firmware raises it,
     and R206 holds `PCIE_PWR_EN2` low until the CM5 does.
   - The reversal case is named and bounded. EMCON may be re-asserted while the module boots after a release. There
     the delays still apply, because the maker gives no boot time and footnote 17 bars RESET# during boot. Residual
     risk (1) then needs one condition, and residual risk (2) needs a boot that is slow against T_off. Both are
     widened to name it, in section 0, SD-EMC-1 and section 7.
   - Fallback (iii), removing the supply at once in a boot window T_boot, is named in advance. It is taken if
     E-05 (b) shows that the fitted firmware misses a pin that falls while it boots.
   - The review's reset/default state for the 5G row is now specified for the design SD-EMC-1 requires (section 4.5,
     "Default required by SD-EMC-1").
   - E-05 (b) adds the pin falling at instants during boot. E-12 adds (h), the power-up under EMCON, and (i), the
     reversal inside and after the Tpr hold.
   - The board B requirement reads the "not turned on" level from the rail and the release hold, never from the
     backstop's own pin, so the supply is never removed sooner than T_cut after that pin on a running module. One
     candidate supervisor on `+3V3_S2A` serves this, the release's Tpr and the cold power-up's Tpr that R238 lacks.
   - The bridge's hand-off adds the reversal case: run the sequence once the module answers AT, and never drive RESET#
     during boot.
   - Changed: section 0, 4.5 (the stage list, Default, what the documents do not state, proof), table row 5, SD-EMC-1,
     E-05, E-12, section 7 and section 8.
2. **Drift since the third version, checked.** Main merged boards A, B and D in `458b2873` (16:48 CEST). Compared net by
   net and part by part (section 1.1): main's B, C and D equal the copies read here, and A differs in its front end
   only. Main's four generators are byte-identical to the ones cited. The "candidate merge" item of section 7 is
   closed, and section 1.1 and the integrator and CONOPS hand-offs say so.

## 9c. What changed in the third cycle (the second checker's two blocking items and eight minor ones)

1. **SD-EMC-1 put the pin before the handshake (blocking 1).** The checker was right. HD v1.1 section 3.5 says the
   module turns off "Only after this process is completed", and Figure 11 and Table 11 draw the pin falling after the
   OK. Option (e) drove the pin at the same instant as W_DISABLE1#, so ahead of the handshake in every EMCON. Its claim
   that the flash risk fell only on the fault case is withdrawn. SD-EMC-1 is re-decided as (f), the maker's order with
   hardware backstops. W_DISABLE1# acts at once. The host runs the handshake and pulls the pin. The hardware pulls the
   pin at T_off (the software's reaction time plus 15 s, until E-12 measures it) and cuts the supply T_cut (at least
   0.9 s) later. The cost is stated: in the fault case the module can emit for at least 15.9 s plus the reaction time,
   against 0.9 s before. The flash risk now falls only when the host's sequence has failed. (Both bounds were
   corrected in the fourth cycle: they also apply in the reversal case, and neither arises at a power-up under EMCON;
   section 9b. The fifth cycle widened the reversal case to the booting case; section 9.) E-12 checks flash integrity
   in the cooperating case as well, over the same cycle count. Changed: section 0, 4.5, table row 5, SD-EMC-1, E-05,
   E-12, section 7, section 8.
   - Found on the way: the module's USB AT port is on bank 3's hub, and HD v1.1 section 3.2 offers AT, QMI and MBIM
     on both links. So two hosts can write the configuration (checker minor 3). No CM5 has a hardware input from
     EMCON. U6, which drives `5G_OFF` and `5G_RESET`, is mastered by the panel controller. As drawn,
     FULL_CARD_POWER_OFF# rises with VCC through R238, against Tpr's 100 ms minimum (Figure 9, Table 10), and that is
     handed to the board B author.
2. **SD-EMC-6 called the TX lamp a hardware detection path (blocking 2).** The checker was right, confirmed on the
   netlist: the lamp's feed `LED_RAIL` needs `PANEL_PWM` (Q2, Q1) and passes the LIGHTING toggle; MASTER CAUT is on the
   same rail; the e-paper indication also needs the display-owning bridge. SD-EMC-6 is re-decided as (c): a hardware
   EMCON lamp on board C, lit only while both lines read LOW, fed from `LED_RAIL_SW` as the MAIN ring is. The residual
   risk's bound now names BLACKOUT and an unpowered board C, and the procedure line tells the operator to set EMCON
   and check the lamp before BLACKOUT. E-02 tests the lamp with the controller in reset and with U9's output forced
   high. The TX lamp's own "no software" text in PANEL.md is handed to the board C author and the PANEL.md writer.
3. **Minor items.**
   - (1) r4t is re-read at its third pass (`e5efdc61`, tool `5aece264`). The tool's output on the candidate set is
     byte-identical to `e88aa46b`'s. The cited statements stand, and section 1.1 says what the third pass changed.
   - (2) E-05 disables both delayed stages.
   - (3) Bank 3's host is named in the controller-failure bullets, E-05 (e) and the provisioning hand-off.
   - (4) The QCFG manual's edge wording is stated in 4.5 and tied to E-05 (b).
   - (5) MBIM is a test case, not a documented behaviour.
   - (6) The default is attributed to EG25-G HD section 3.8.3.
   - (7) L7 names the 2N7002's typical 3 V and 4 V curves.
   - (8) The integrator carries SD-B-03's supersession.
4. **Drift since the second version, checked.** Board A took r4a's fourth fix-up, and the round-6 integration tree
   was written at 16:29 CEST. Both were compared net by net with the copies read here (section 1.1): only board A's
   front end moved. Board A and D generator line citations are re-cited to the current generators; r6d's comment edit
   had moved board D's by 25 or 26 lines.

## 9d. What changed in the second cycle (the first checker's four blocking items)

1. **RM520N-GL configuration (4.5, SD-EMC-1, E-05).** Added the EG25-G precedent (HD V1.0 section 3.8.3, held) and
   Quectel's LTE QCFG manual (section 5.12: a stored `airplanecontrol` setting, disabled by default per the EG25-G's
   section 3.8.3, with QMI still allowed to leave airplane mode at value 1), and the fact that the RM5xxN manual's own AT+QCFG=? list ends in an ellipsis.
   Added to the controller-failure list: a host writing a persistent configuration that turns the pin off, and a host
   going online over QMI or MBIM. E-05 now records AT+QCFG=? and exercises every airplane-related value, repeating its
   cases under each. The provisioning owner verifies the configuration at every boot. SD-EMC-1's rationale is
   restated.
2. **FULL_CARD_POWER_OFF# (4.5, SD-EMC-1, section 0, E-12).** Quoted HD v1.1 section 3.5's "Only after this process is
   completed" and Tpd's 900 ms minimum with no maximum. Named supply removal as the only inhibit independent of the
   module's firmware, with its flash-corruption cost, and took the staged option (e). E-12 is new: it covers
   FULL_CARD_POWER_OFF# without AT+CFUN=0, the time to off, and flash integrity. Section 0's feasibility verdict now
   carries a condition for the 5G row until E-05 and E-12 have run.
3. **The PA's single-fault claim (4.2, table row 2, section 0, SD-EMC-6, E-02).** The claim is now limited to faults
   downstream of the `TX_INHIBIT_n` node. `SW_EMCON` and that conductor are named as the common element and accepted
   with detection (SD-EMC-6). E-02 has the shared-element case. The row stays CLOSED at desk on RF-002's terms, now on
   path (b) alone.
4. **L1 to L4 and section 7 against r4t.** Rewritten against r4t at sha256 `1e3fe2800c3b33db`, cited by decision ID.
   The tap remedy is withdrawn (R4T-D40). The "10 k on both boards passes" figure is replaced by R4T-F8's third
   statement. L3's "+3V3_DEV loss is safe for the LimeSDR, RockBLOCK and E22" is replaced by R4T-F9's UNDECIDED. L4
   now separates the quads without Ioff (0 V included) from the single gates that state it, which removes the conflict
   with L3. Found while doing this: L7, the 2N7002 gate drive on the tools author's own rules R4T-D30 (amended) and
   R4T-D32. The instrument reading is re-taken with the final tool (section 1.3).
