# W6 findings: independent verification and manufacturing (MESHSAT-1357), round 2

Draft for the integrator. Round 1 was written on 25 September 2026 against tree `e6291404`; this round-2 revision
reads tree `82dd1e4d` (the generators, `jlc_certify.py`, `lcsc_fill.py`, `JLC-CERTIFIED.tsv` and `v2/vendor/` are
byte-identical between the two). Worktree `fnd/w6`. Prototype work: nothing here has been built, and no finding
below is a test result on hardware.

**Legend.** VERIFIED: I opened the artefact and read the cited line, table or page. INFERRED: taken from a record,
a file name or reasoning, not re-read against the artefact. PROVISIONAL: a verdict that stands on today's evidence
but is held open by a named condition (owner condition 1 and 2 language). Every "CERTIFIED" below is the literal
verdict label of `v2/ecad/tools/jlc_certify.py` in `v2/release/revA/order/JLC-CERTIFIED.tsv`, an internal
buyability check; nothing in this draft is a certification. Page numbers are the document's own.

**Method.** Held datasheets read with `pdftotext -layout`, and page renders where a table's layout matters.
JLCPCB parts API readings at 2026-09-25 20:44, 21:50 and 21:57 UTC (the endpoint `jlc_certify.py:40` uses; raw
responses in `drafts/w6-scratch/jlc-r2/`). LCSC detail API readings at 21:53 UTC (same folder).
`jlc_certify.same_part`, `intended_part` and `norm_pkg` exercised as pure functions (round 1). A read-only
mask-bridge scan of the seven committed phase boards (`drafts/w6-scratch/mask_bridge_scan.py`, outputs in
`drafts/w6-scratch/maskscan/`). No gate, no suite run, no KiCad step, no box. The settled adjudications of
25 September (A01 to A11, `drafts/w6-scratch/r2_adjudications.json`) override round-1 claims where they differ; the
evidence of the two I rely on most is copied into `drafts/box/a08/` (5G socket) and `drafts/box/a10/` (JLCPCB
stackups).

## Summary

| ID | Severity | Status | Finding |
|---|---|---|---|
| W6-F1 | major | **PROVISIONAL** | STM32H753 (schematic, the owner's baseline) against STM32H743VIT6 (bought): no incompatibility found against the current documents; **not closable** until the owner rules on supervisor secure boot and decision 30 is ruled. Two reopen conditions are live today. The mismatch stays open (condition 1). |
| W6-F2 | critical | VERIFIED | Board P's BQ4050RSMR (VQFN-32 4 x 4 mm, 0.4 mm pitch) sits on a 5 x 5 mm, 0.5 mm pitch land. The P8 evidence behind decision 28 was taken on that land and must be retaken on the correct land before it is reused (owner notice, not a question). |
| W6-F3 | major | VERIFIED | `jlc_certify.py` accepts sibling parts (six-character prefix), strips grade letters on its wider search and compares packages without size or pitch. Three live consequences: the supervisor MCU, board D's hub grade, and the 5G socket key (F13). |
| W6-F4 | major | VERIFIED | The supervisors' kit I2C lands on PB1/PB2, which have no I2C alternate function on either the H743 or the H753. |
| W6-F5 | major | VERIFIED | Board D's hub: TUSB2046BI in LQFP-32 does not exist; the code bought is the 0 to 70 C TUSB2046BVFR, outside the -20 C envelope. |
| W6-F6 | resolved | VERIFIED | TPS2065C: the fitted variant's datasheet (SLVSAU6I) is held; pin map and enable polarity match; SLVS490K must not be cited. Current limit stated with its temperature condition. |
| W6-F7 | minor | VERIFIED | Supervisor decoupling: VDDA lacks the 1 uF and 100 nF AN4938 asks for. The VBAT 100 nF is only AN4938's example and is withdrawn as a shortfall. |
| W6-F8 | info | VERIFIED | The 13 WRONG_MODEL rows reach no current generator; seven wrong codes remain in non-superseded order folders; four latent entries (not three) remain in `lcsc_fill.py` and `gen_sch_a.py`. |
| W6-F9 | info | VERIFIED | TMUXHS4212 wiring is consistent with SLLA552 and the later SLASEP7A; designators now given per slot. |
| W6-F10 | minor | VERIFIED | Record corrections in `research-io-supervisor-2026-09-09.md` section 4 and `ARCH-PCB-B-IOHA.md:160`. |
| W6-F11 | info | VERIFIED | Board B routes PCIe at the CM5's 90 ohm; the 100 ohm `PCIE` default in `intent.py:13` is latent. |
| W6-F12 | minor | VERIFIED | Document hygiene: two KSZ9897R revisions, a non-A TS3USB221 sheet, stale Ebyte metadata, unpinned SA868 (three bands) and RM520N-GL order codes, a stale PARTS.md verdict, and a held TE file misnamed as a B-key drawing. |
| **W6-F13** | **critical** | VERIFIED | Board B's 5G socket TE 1-2199119-5 (C574849), labelled CERTIFIED as "M.2 B-key", is a **key M** connector; the RM520N-GL is key B only. SIM 2 is also wired to the wrong socket pins. |
| **W6-F14** | major | VERIFIED | Surge-clamp makers settled: C224052 is **Littelfuse** SMCJ40A (not Vishay); the Littelfuse sheet and the PESD5V0S1BA (board D) datasheet are now filed with hash and revision. |
| **W6-F15** | major | VERIFIED | Board A's LTC2954 purchase code C683782 resolves to LTC2954CTS8-1#TRPBF, 0 to 70 C (confirms W2 F-SQ-03); an I-grade code exists at JLC (C580654, stock 195 in one reading). |
| **W6-F16** | info | VERIFIED | DFM mask-bridge scan at matte black mask: no footprint on A32, B21, C24, D12 or E17 has two pads of different nets closer than JLCPCB's 0.13 mm black-mask floor; the closest are board B's 0.4 mm-pitch LQFP/TQFP-128 at 0.15 mm. Board P's wrong land is already below the 2 oz floor; the correct land sits exactly on it. |
| **W6-F17** | major | VERIFIED | `JLC-CERTIFIED.tsv` has no row for the codes that entered the generators after 20 September (C224052, C224047, C19224): the buyability table does not cover boards E's and D's current clamps. |

## Round-2 changes against the challenger's defects

| Challenger defect | Fixed how |
|---|---|
| SOURCES.yaml cellular-module entry passed the 5G socket as "partial" | Split into `cellular-socket` (identity MISMATCH, key M, TE drawing C-2199119 rev F filed as `v2/vendor/m2/te-2199119-customer-drawing-revF.pdf`) and `cellular-module`; new finding F13 |
| JLC inquiry premise "all published stackups are 1 oz outer" | Premise withdrawn (adjudication A10); the inquiry is reduced to one land question for P and one Dk/coupon question for B; the published 4-layer 2 oz and 8-layer rows are transcribed in `v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md` |
| F1 stated as settled | F1 is PROVISIONAL, not closable, names the owner-set baseline and the two live reopen conditions, and orders the rename after the owner's rulings |
| Owner question option B rested on an unsourced premise | Rewritten: every option's premise is cited to DS12110, DS12117 or a dated stock reading; what no held document says is labelled so; tied to decision 30 |
| SOURCES.yaml pointed at unpushed drafts | Every `drafts/` reference removed; findings inlined |
| "20 critical parts" with no criterion; no TUSB2046 entry | Criterion stated in the header; 32 entries now, including TUSB2046, LTC2954, H5007NL, TCAN334, CSD17570Q5B, the 4S cells, the RA30H1317M1, the TVS family with makers, PESD5V0S1BA, USBLC6 and the XT60; what is deliberately left out is named with the reason |
| F2 asserted the four-layer choice independent of U1's land | Withdrawn; F2 now says P8 must be retaken on the correct land before decision 28's evidence is reused, as an owner notice |
| F9 designators were slot-relative | Real references per slot |
| F7 VBAT counted as a shortfall | Downgraded to AN4938's example |
| Citation slips | FDCAN2 on DS12110 p.90; API at `jlc_certify.py:40`; TPS2065C limit with its TJ condition; SA868 has a 320 to 400 MHz variant; F8 counts four latent items |
| Inquiry did not state B's copper and mask; absolute paths | Stated (1 oz outer, matte black); mask-bridge floor answered from the capability page and scanned (F16); repo-relative paths |
| Missing: challenge of W1 to W5 and W7 | Done: `drafts/w6-peer-challenge.md` |
| Missing: DFM beyond the BQ4050 land | F16 (mask bridges on every committed board); via-in-pad default recorded from the capability page |

---

## W6-F1. STM32H753 against STM32H743: an open component mismatch, verdict PROVISIONAL

**The mismatch, as it stands in the tree (VERIFIED).**
- The owner set the supervisor baseline: "The owner set the baseline at three STM32H753" (`v2/docs/research-io-supervisor-2026-09-09.md:3-4`).
- Schematic symbol `STM32H753VI`, description "STM32H753VITx I/O supervisor", LCSC `C114409`: `v2/ecad/tools/gen_sch_b.py:829`. The substitution reason lives only in that line's code comment.
- Pin table `H753` (100 entries): `gen_sch_b.py:257-261`.
- BOM line in the newest B folder: `v2/release/revA/boards/meshsat-pcb-b-revA-B19-quote/pcb-b-compute-bom.csv:171,176,181`.
- `JLC-CERTIFIED.tsv:482-484`: label CERTIFIED, model **STM32H743VIT6**, read 2026-09-14, accepted by the six-character prefix rule (F3).
- Architecture text names the H753: `v2/docs/ARCH-PCB-B-IOHA.md:94,157`; `v2/docs/V2-SPEC.md:82`.

**What the supervisor design uses, capability by capability (VERIFIED against both datasheets).**

| Capability | Used by the design? | Evidence | On the H743VIT6? |
|---|---|---|---|
| Two FDCAN | yes, two heartbeat fabrics | `gen_sch_b.py:819-820`; `ARCH-PCB-B-IOHA.md:96` | yes (DS12110 Rev 10 p.2) |
| FDCAN pins | FDCAN1 PD0/PD1, FDCAN2 PB12/PB13, AF9 | `gen_sch_b.py:819-820` | yes: DS12110 Rev 10 Table 13 p.92 (Port D) and Table 11 continued p.90 (PB12/PB13) |
| HSE 25 MHz, IWDG, BOR, GPIO, SWD | yes | `gen_sch_b.py:794, 818, 821-828, 833-835` | yes (identical pins, see below) |
| I2C slave on the kit bus | yes, by the architecture | `ARCH-PCB-B-IOHA.md:96` | the pins drawn have no I2C on either part (F4) |
| CRYP and HASH | no use found | grep of `v2/docs`, `v2/ecad/tools` and the sibling MeshSat repos | **no**: H753 only (DS12117 Rev 9 section 3.28 p.41); DS12110's revision history "Removed CRYP peripheral" |
| Secure access mode: ST Root Secure Services, user secure services, secure firmware install | no use found | same search | **no**: H753 only (DS12117 Rev 9 section 3.3.2 p.25, p.1 "secure firmware upgrade support, Secure access mode"); DS12110's revision history "Removed secure firmware upgrade support" |
| RDP, PCROP, active tamper | not specified by any requirement | none | yes on both (DS12110 p.1 "ROP, PC-ROP, active tamper"; DS12117 3.3.2 calls RDP and PCROP the "other typical memory protection mechanism") |
| Supervisor firmware | none exists | no `.ioc`, firmware directory or source in this repo or its siblings | not applicable |

**Package and pinout (VERIFIED, 100 of 100 pins).** `drafts/w6-scratch/lqfp100_pin_parity.py` compares every pin of
the generator's table with DS12110 Rev 10 Figure 5 and DS12117 Rev 9 Figure 4 (p.55 each): 0 mismatches on both, and
a planted PB1/PB2 swap is caught.

**Availability (VERIFIED, dated readings, JLCPCB parts API 2026-09-25T21:57Z).** C114409 STM32H743VIT6 **4335**;
C5271084 STM32H743VIT6TR 897; C730206 STM32H753VIT6 **0**; C7324976 STM32H753VIT6TR **0**. Need 15 (3 per board, 5 boards).

**Verdict: PROVISIONAL.** No incompatibility was found between the STM32H743VIT6 and the supervisor as the current
documents specify it: same package and pinout, same FDCAN, clock, watchdog and GPIO resources, and the capabilities
it lacks are used by no requirement, no generator line and no firmware. **This is not a closure.** The mismatch stays
open under condition 1, and it cannot be closed yet, because two of its own reopen conditions are live:

1. **Secure boot is an open gap, not an absent requirement.** The red team's S2 records that no secure-boot requirement
   exists anywhere in the pack while flashing is deliberately exposed (`v2/docs/RED-TEAM-2026-09-09.md:363`). Whether the
   supervisors need verified boot or authenticated update is unanswered; the H753's Secure access mode is exactly the
   capability that question would call on.
2. **Decision 30 (ZEROIZE) is open, and one of its options gives the supervisors ZEROIZE work.** W5's option Z-C routes
   `ZEROIZE_HW` into each IOCTRL supervisor (`drafts/w5-hw-fw-contract.md`, options table, round-1 line 246); `PANEL.md:112`
   already says the drives "are wiped by the supervisor". If decision 30 lands on Z-C or anything like it, the
   supervisor's security scope changes whatever the secure-boot answer is.

A third condition would reopen it later: authenticated heartbeats or leases on the CAN fabrics using hardware HMAC.

**Order of actions (engineering, for the integrator).** (1) Owner answers the supervisor secure-boot question below.
(2) Decision 30 is ruled. (3) Only then is the record made consistent: either rename the symbol, description and pin
table to `STM32H743VIT6` with the substitution reason moved from the code comment into `SOURCES.yaml` and the
architecture text, or keep the H753 with a purchase route that exists. Until (1) and (2), nothing is renamed.

### Owner decision candidate: supervisor secure boot (every premise sourced)

**Question.** Must the three I/O supervisors verify their own firmware (verified boot or authenticated update) in the
first prototype?

**What is established, and from where.**
- The STM32H753 adds "Secure access mode", with "STMicroelectronics Root Secure Services ... a secure solution for
  firmware and third-party modules installation ... based on a device unique private key" and user-defined secure
  services "executed just after a reset" that "preempt all other applications" (DS12117 Rev 9 section 3.3.2 p.25), plus
  CRYP and HASH accelerators (section 3.28 p.41).
- The STM32H743 has none of these (DS12110 Rev 10 revision history: "Removed CRYP peripheral", "Removed secure firmware
  upgrade support"); it keeps "ROP, PC-ROP, active tamper" (DS12110 p.1).
- Buyability today, one reading each (JLCPCB API 2026-09-25T21:57Z): H743 4335 and 897 in stock; H753 0 and 0.
- The owner set the H753 as the baseline on 9 September (`research-io-supervisor-2026-09-09.md:3-4`).
- No secure-boot requirement exists (red team S2, `RED-TEAM-2026-09-09.md:363`), and decision 30 may assign ZEROIZE work
  to the supervisors (option Z-C).

**What no held document establishes, stated as such.** Whether a boot-time signature check written in user firmware
on the H743 and protected by RDP and PCROP would meet the kit's need is an engineering judgement that ST's datasheets
do not make; its strength is weaker than the H753's hardware-isolated secure services by the H753 datasheet's own
description (secure services that preempt all other code and become inaccessible after they run, DS12117 3.3.2), but
how much weaker, and whether that matters here, is **TBD**. The price and lead time of an H753 purchase outside JLC's
stock are **TBD** (not read).

| Option | What it means | Consequence |
|---|---|---|
| A | No secure-boot requirement on the supervisors for the first prototype, recorded as a deferred requirement with a production trigger | The H743 can be accepted once decision 30 is also ruled without supervisor ZEROIZE work; the record is then renamed |
| B | Hardware root of trust on the supervisors now | The H753's Secure access mode is the ST-documented mechanism; JLC shows 0 stock on both H753 codes today, so a hand-fit or consigned purchase route is needed (cost TBD) |
| C | Authenticated firmware on the supervisors now, implemented in user firmware on the H743 behind RDP and PCROP | Buyable today; its assurance is the weaker, software-only kind described above (TBD how much weaker); the rename proceeds once decision 30 is ruled |

**Recommendation.** A, with its production trigger written into the requirement record. Reason: nothing in the pack
uses the H753-only features today, and the red team's S2 gap is a kit-level requirement question (CM5 flashing is the
exposed path it names) that W1's requirement records must answer first. This recommendation does not close the
mismatch; decision 30 must also be ruled.

## W6-F2. Board P: the BQ4050 is on the wrong land (critical), and decision 28's evidence was taken on it

- Part: BQ4050RSMR, **VQFN (RSM) 32, 4.00 x 4.00 mm, 0.4 mm pitch**: SLUSC67B p.1, orderable addendum, RSM0032A p.51,
  example board layout p.52 (32 pads 0.6 x 0.2 mm at 0.4 mm pitch), stencil p.53. The held file is byte-identical to
  ti.com on 25 Sep 2026.
- Land drawn: `gen_sch_p.py:71` maps `QFN32` to `Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm`, used by `U1` at
  `gen_sch_p.py:109`. Present since commit `751200aa` (7 Sep).
- Propagated to: `v2/release/revA/boards/meshsat-pcb-p-revA-P4/pcb-p-pack-bom.csv:20` and `-bom-full.csv:20`;
  `order/PCB-P-PACK-P1` (BOM and upload); `v2/ecad/pcb-p-pack/pcb-p-pack.kicad_pcb:4543`;
  `v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_pcb:6181`.
- Why nothing caught it: `norm_pkg` reduced both sides to QFN-32 and VQFN-32 and `package-aliases.txt:10` equates them,
  so body size and pitch were never compared (F3).
- **Consequence for decision 28 (owner notice, not a question).** Decision 28's ruling cites P8 ("0 hard and 0 unrouted
  at the fabricator's 0.16 mm floor", `pcb_decisions.yaml`, decision 28 outcome). P8 was routed on the wrong U1 land.
  Round 1 said the four-layer choice did not depend on the land; that was asserted without evidence and is withdrawn.
  The P8 number must be retaken on the RSM0032A land before decision 28's evidence is reused. The ruling itself is not
  reopened here; its evidence is void until the retake.
- **Manufacturing, settled by the fabricator's own pages (adjudication A10, read 2026-09-25).** At 2 oz outer copper
  JLCPCB publishes 0.15/0.15 mm minimum track and space (multilayer), a 0.20 mm minimum pad spacing for a solder mask
  bridge (any colour), and a 0.25 x 0.25 mm minimum SMD pad (`drafts/box/a10/text_capabilities_2026-09-25.txt`). TI's
  land has 0.20 mm pads with 0.20 mm gaps: exactly on the bridge floor and narrower than the minimum SMD pad; at 0.4 mm
  pitch no land can meet both rows (0.25 + 0.20 = 0.45 mm). The wrong 5 x 5 mm land is already below the 2 oz bridge
  floor at its exposed-pad corner (0.177 mm between pin 24 and the exposed pad, F16). This is the one board-P question
  that still has to go to JLCPCB (`drafts/w6-jlc-inquiry.md`).
- Recommendation: change U1's footprint key to a land drawn from RSM0032A (TI p.52), re-run board P's generator,
  placement and the P8-equivalent arm on a box, and re-take every P verdict, after JLCPCB answers the land question.

## W6-F3. The buyability tool accepts sibling parts and ignores body size, pitch and key

All three mechanisms are in `v2/ecad/tools/jlc_certify.py` (VERIFIED by reading and by calling the functions):

1. **Common-prefix identity.** `same_part` (`jlc_certify.py:236-264`, the rule at :247-251) returns True when two part
   numbers share six leading characters: `("TPS2065CDBV","TPS2061CDBVR")` (active-low enable), `("TPS2065CDBV","TPS2069CDBVR")`
   (1.5 A), `("TPS2065CDBV","TPS2065DBVR")` (the non-C part), `("E22-900M30S","E22-900M33S")`, `("ATECC608B","ATECC608A-SSHDA")`,
   `("BQ25731","BQ25730RSNR")`, `("STM32H753VITx","STM32H743VIT6")`, `("TUSB2046BI","TUSB2046BVFR")`: all True.
2. **The wider search strips grade letters.** `_certify` retries with trailing letters removed (`jlc_certify.py:690-709`):
   `TUSB2046BI` became `TUSB2046` and the commercial TUSB2046BVFR was accepted "on the wider search" (commit `07c57b30`).
3. **Packages without dimensions or key.** `norm_pkg` (`jlc_certify.py:138-191`) reduces a 5 x 5 mm 0.5 mm land and a
   4 x 4 mm VQFN to QFN-32 and VQFN-32, which the alias file equates (F2). Nothing compares an M.2 key letter: row 424
   passed "M.2 B-key 3052 socket, TE 1-2199119-5" on the model string, and the part is key M (F13).

**Recommendation (tool owner; not a W6 file).** Identity: compare the base part number exactly after removing only
packing suffixes declared per maker (R, T, TR, -T, G4, #PBF, #TRPBF), treating grade and variant letters as identity.
Package: compare body size and pitch when both sides state them. Keyed connectors: compare the key when the row's
description names one. Defective fixtures: the eight pairs above, the BQ4050 land, and row 424 (description B-key,
part key M). Acceptable fixture: `74LVC08APW` against `SN74LVC08APWR`. Until then the CERTIFIED label is not evidence
of identity, grade, land or key.

## W6-F4. The supervisors' I2C pins have no I2C peripheral

- `gen_sch_b.py:824` maps LQFP pin 35 to `SDA` and 36 to `SCL`; the pin table gives 35 = **PB1**, 36 = **PB2**
  (`gen_sch_b.py:261`; ST's p.55 figure agrees).
- DS12110 Rev 10 Table 11 p.89 (H743) and DS12117 Rev 9 Table 10 (H753) list no I2C function on PB1 or PB2. PB6/PB7
  (pins 92/93, I2C1/I2C4) and PB10/PB11 (pins 46/47, I2C2) are I2C-capable and unused in `gen_sch_b.py:816-828`.
  Second source: Zephyr `hal_stm32` `stm32h743vitx-pinctrl.dtsi` (commit `176078511fc2`, sha256 `58d80810...`).
- It breaks `ARCH-PCB-B-IOHA.md:96` (supervisors as I2C slaves 0x30 to 0x32 on the kit bus). W5 found the same
  independently (W5 F3). Common to both parts; independent of F1.
- Recommendation: move SDA/SCL to PB7/PB6 or PB11/PB10, and add a check that every declared I2C net on an MCU lands on
  an I2C-capable pin.

## W6-F5. Board D's USB hub: the grade named is not the grade bought

- Generator: "TUSB2046BI four-port USB 2.0 full-speed hub (LQFP-32 ...)", no LCSC code (`gen_sch_d.py:178`).
- SLLS413L (held `v2/vendor/ti/ti-tusb2046b.pdf`, same revision as ti.com on 25 Sep): TUSB2046BI exists **only as VQFN
  (RHB) 32** (orderable addendum: TUSB2046BIRHBR, TUSB2046BIRHBT); the LQFP-32 (VF) parts are TUSB2046BVF/BVFR at 0 to
  70 C and TUSB2046IBVF/IBVFR at -40 to 85 C (p.6 recommended operating conditions).
- Bought: C167642 = TUSB2046BVFR (`JLC-CERTIFIED.tsv:539`; `boards/meshsat-pcb-d-revA-D11/pcb-d-aprs-bom.csv:56`),
  **0 to 70 C** (JLC API 2026-09-25T21:50Z, stock 375). Envelope: in use -20 to +40 C (`pcb_envelope.yaml:24`).
- Available: C702369 TUSB2046IBVFR, LQFP-32, -40 to +85 C, stock **16** (21:50Z; need 5).
- `pcb_part_temps.yaml` (CMP-001's table) has no TUSB2046 row, so CMP-001 cannot see this.
- Recommendation: name `TUSB2046IBVFR` with its code after the TUSB2046I against TUSB2046B difference is read in
  SLLS413L; add a TUSB2046 row to `pcb_part_temps.yaml`. Until then board D's hub is a mismatch (SOURCES.yaml
  `board-d-usb-hub`).

## W6-F6. TPS2065C: fitted variant documented, generator verified (resolved)

- Fetched: TI SLVSAU6I (Rev. I, revised May 2026), `https://www.ti.com/lit/ds/symlink/tps2065c.pdf`, filed as
  `v2/vendor/ti/ti-tps2065c-slvsau6i.pdf`, sha256 `898c0934...4be3fcd`; byte-identical to ti.com on 25 Sep.
- TPS2065CDBVR, SOT-23 DBV 5, marking VCAQ; Table 5-2 p.4: 1 OUT, 2 GND, 3 FLT, 4 EN (active high), 5 IN, which
  matches the generator's map (`gen_sch_b.py:313`).
- Only instance: board B's U28 (`gen_sch_b.py:707`), EN 100k pull-down, FLT 10k pull-up, 0.25 A budget (`gen_sch_b.py:75`).
- Current limit, 1 A rated output, TPS20xxC: **1.3 / 1.55 / 1.8 A at TJ = TA = 25 C (section 6.6)** and **1.2 / 1.55 /
  1.9 A over -40 to 125 C (section 6.7)**.
- `ti/ti-tps2065-tps2066-tps2067.pdf` is SLVS490K, the family without the C suffix; it must not be cited for this part.

## W6-F7. Supervisor decoupling against AN4938 (for decision 42, W2)

- AN4938 Rev 7 section 2.2 p.12: 4.7 uF minimum per package plus 100 nF per VDD pin; VDDA 100 nF plus 1 uF; VCAP1/VCAP2
  2.2 uF each. For VBAT, AN4938 makes only the connection mandatory and gives the 100 nF as an example.
- Fitted per controller (`gen_sch_b.py:805-806, 830`): 10 uF and five 100 nF on the 3.3 V rail (five VDD pins), two
  2.2 uF on VCAP; VBAT tied to the 3.3 V rail.
- Short: **one 1 uF and one 100 nF dedicated to VDDA.** Met: bulk, per-VDD 100 nF, VCAP, and the mandatory VBAT
  connection. The round-1 claim of a missing VBAT 100 nF is withdrawn (optional, AN4938's example).

## W6-F8. The 13 WRONG_MODEL rows against the current generators

| Row | Part asked | Code, and what it resolves to | On a current generator? | Where the code still lives |
|---|---|---|---|---|
| 709, 710 | 6 MHz 3225 crystals (D Y1, Y2) | C448646 = NX3225SA 25 MHz | no (decision 37 replaced the part with C252308) | D10 and D11 BOMs; blocked in `lcsc-blocked.txt:50` |
| 711 | EL817S / PC817 (E) | C109227 = LTV-817S-TA1-C | no | `lcsc_fill.py:150` (latent); E4 folder |
| 712 | FE1.1s (B) | C2848, answered as D82C284-8 | no | `lcsc_fill.py:59` (latent); superseded folders |
| 713 | INA219AIDCN (A, B) | C138024 = RC0402FR-0725R5L, a resistor (cache) | no instance; `gen_sch_a.py:135` defines an uncalled `ina219()` with it | `gen_sch_a.py:135`, `lcsc_fill.py:59`; superseded folders |
| 714 to 719 | PCA9555PW (A, B, D) | C5626 = 74HC245PW | the part is current with C2864778 (PCA9555PWR); C5626 blocked (`lcsc-blocked.txt:27`) | non-superseded `order/PCB-A-POWER-A22` (U27, U28), `order/PCB-B-COMPUTE-B16` (U6, U7), `order/PCB-D-APRS-D8` (U16) |
| 720 | SMCJ18A (A D1) | C1973072 = SMCJ15A | no: `gen_sch_a.py:167` carries C374030 | `order/PCB-A-POWER-A22` BOM and upload |
| 721 | Si1308EDL class N-FET (C Q6) | C8545 = 2N7002 | no | `order/PCB-C-DISPLAY-C7` BOM and upload |

**Answer.** No WRONG_MODEL row reaches a part instance on a current generator. The non-superseded `order/` folders carry
**seven** wrong-code instances of three codes (C5626 five times, C1973072, C8545), not four. **Four** latent items would
re-introduce a wrong code: `lcsc_fill.py:59` (INA219 to a resistor), `lcsc_fill.py:59` (FE1.1s to C2848),
`lcsc_fill.py:150` (EL817S to a substitute) and the uncalled `ina219()` at `gen_sch_a.py:135`. The WRONG_MODEL list is
not the whole problem: F3 shows CERTIFIED rows carrying a wrong grade, a wrong land and a wrong key.

## W6-F9. TMUXHS4212 against its schematic checklist (consistent)

- SLLA552 (March 2021), filed `v2/vendor/ti/ti-slla552-tmuxhs4212-schematic-checklist.pdf`, sha256 `5258cb80...0a4182e`.
- Checked against `gen_sch_b.py:541-555`. Designators are per slot s = 1, 2, 3 (`gen_sch_b.py:364`: C(n) = C(100s+n)):
  - VCC decoupling: C192/C193, C292/C293, C392/C393 (100 nF and 1 uF on `+3V3_DEV`). Consistent.
  - Thermal pad to GND (pin 21). Consistent.
  - 100 nF AC coupling on the host TX pairs: on the CM5 module ("NB AC coupling capacitor included on CM5",
    `cm5-datasheet.pdf` p.22). The hub's TX pair is coupled by C159/C160, C259/C260, C359/C360 on the hub side of the
    mux (`gen_sch_b.py:528`). Consistent. (Board B's global C59/C60 are different parts, on the CP2102.)
  - OEn: the checklist's EVM adds 1 uF to GND; the design drives OEn from the voted edge detector with 100k pull-downs
    R161, R261, R361 (`gen_sch_b.py:558`). A deliberate difference (INFERRED from `ARCH-PCB-B-IOHA.md:89`).
  - RSVD1/RSVD2: checklist "leave open"; SLASEP7A p.3 (revised May 2022, later) "Connect both pins to VCC"; the
    generator ties both to `+3V3_DEV` (`gen_sch_b.py:544`). Consistent with the later document.

## W6-F10. Record corrections (text owned by others)

- `research-io-supervisor-2026-09-09.md:72-73`: "The crypto accelerator is the only difference" omits Secure access mode
  (DS12117 3.3.2 p.25); "the kit's secure element is the ATECC608B on another board": it is U8 on board B
  (`gen_sch_b.py:750`).
- `ARCH-PCB-B-IOHA.md:160` and `gen_sch_b.py:259-260`: the FDCAN alternate functions are now confirmed from ST's own
  tables (F1); the "to be confirmed" wording can go.
- `v2/vendor/PARTS.md:118-119` shows ATECC608B as WRONG_MODEL C2836813 while the table has CERTIFIED C1518769; PARTS.md
  is generated (`kb/kb_inventory.py`), so it needs a regeneration.
- `v2/vendor/sources.txt:36` "TE 1-2199119-5 (key to be read from the drawing)" and appendix line 2884's conditional
  pick: the drawing says key M, so the appendix's else-branch applies (F13). The appendix is append-only history: a new
  entry records the outcome.
- `v2/vendor/open-picks.txt:23` misreads Table 32 of the RM520N hardware design (it puts UHB TX0/PRX on ANT0; that path
  is on ANT2) and places Table 32 on p.59 (it starts on printed p.58).

## W6-F11. PCIe impedance target (for W3)

The CM5 datasheet asks for 90 ohm PCIe pairs (p.9). Board B puts every `PCIE*`, `NVME*` and `CARD*` pair in the `USB`
class (`gen_pcb_b3.py:574`), 90 ohm (`intent.py:13`). The `PCIE` entry of `intent.py:13` (100 ohm) is declared by no
board's `pair_classes`, so it is a latent default. The PI7C9X2G404SL's 80 to 120 ohm figure (DS40068 Rev 5-2) is a DC
termination limit, so it only weakly supports "the switch tolerates either" as a channel impedance. W3: state 90 ohm
for PCIe on both ends and retire or correct the default.

## W6-F12. Document hygiene

- KSZ9897R: `microchip/microchip-ksz9897-datasheet.pdf` is revision D, `cluster/ksz9897.pdf` is revision E. Cite E.
- `cluster/ts3usb221.pdf` is SCDS220M (TS3USB221, no A suffix); the fitted part is TS3USB221A (`ti/ti-ts3usb221a.pdf`).
- `ebyte/e22-900m30s-spec-zh.pdf` and `zigbee/ebyte-e72-2g4m20s1e-user-manual.pdf` carry the stale PDF title "E01-2G4M27D".
- The SA868 has three band variants (VHF 134 to 174, UHF 400 to 480, 350 band 320 to 400 MHz, held V1.3 sheet) and the
  generator names no order code; the RM520N-GL regional order code is not pinned either. Both TBD with effects in
  `SOURCES.yaml`.
- `m2/te-2199119-m2-b-key.pdf` is not a drawing and not a B-key document: it is TE's Quick Reference Guide 1-1773702-1
  (01/2014). The drawing is now filed as `m2/te-2199119-customer-drawing-revF.pdf`.
- The ATECC608B document held is the summary sheet (DS40002239A).

## W6-F13. Board B's 5G socket is key M; the module is key B (critical)

- Generator: `J_M2C2`, "M.2 B-key 3052 socket, TE 1-2199119-5 ...", footprint key `M2B`, LCSC `C574849`
  (`gen_sch_b.py:479`); the committed B19 netlist (`8ce0b892`) carries the same value and code.
- **The part is key M (VERIFIED).** TE customer drawing C-2199119 rev F (ECR-19-011878, 19 March 2020), sheet 2
  part-number table: key M = 1-2199119-3/-4/-5/-6; key B = 2199119-1, 3-2199119-1, 2199119-3, 2199119-5, 1-2199119-0
  (read by me on the render `drafts/box/a08/te_cd_p2_table.png`). TE's product page for 1-2199119-5 reads "KEY M 15U'' AU,
  Connector & Keying Code: M" (Wayback 2025-06-09 and 2025-12-12; `drafts/box/a08/wb_1-2199119-5_20251212.dec.html`).
  The drawing is filed as `v2/vendor/m2/te-2199119-customer-drawing-revF.pdf` (sha256 `ef35dbf8...`).
- **The module is key B only (VERIFIED).** RM520N series hardware design V1.1: "standard M.2 Key-B WWAN module" (p.15),
  Table 4 "M.2 Key-B", 30.0 x 52.0 x 2.3 mm (p.17), pins 12 to 19 notch and 59 to 66 live (Figure 2 p.20).
- **The requirement was conditional and the condition fails.** Appendix line 2884: "TE 1-2199119-5 ... if its drawing
  confirms key B, else Amphenol MDT420B01001". The table row 424 is a defective CERTIFIED (its own text says B-key).
  `lcsc-blocked.txt:34` blocks C41430835 "where the schematic names TE 1-2199119-5 (M.2 B-key)": the premise is false,
  and C41430835 is itself a B-key part (LCSC "Interface Form = M.2-B Key").
- **Replacement (a part change, a mismatch until its land is proven).** TE 2199119-3 (key B, same drawing and 3.2 mm
  height): C590866, stock 1432 (JLC API 2026-09-25T21:50Z). Alternatives: TE 2199119-5 (C4797645, stock 1), Amphenol
  MDT420B01001 (C4594496, 4.2 mm height, stock 4025; the held Amphenol file is a family brochure that does not print this
  part number), HOAUC HYCW01B-05NGFF-420B (C41430835, stock 661). The M2B land has no locating holes where drawing
  sheet 3 draws 1.1 and 1.6 mm holes.
- **SIM 2 is miswired on the same socket (VERIFIED: generator side read by me at `gen_sch_b.py:477`; module side by the socket adjudication against hardware design V1.1).**
  The generator puts SIM2_CLK on 40, SIM2_IO on 42, SIM2_RST on 44 and SIM2_VCC on 46; the module has 40 USIM2_DET,
  42 USIM2_DATA, 44 USIM2_CLK, 46 USIM2_RST and 48 USIM2_VDD (Figure 2, Table 6), and pin 48 is unconnected.
- **Antennas.** No file records which ANTx goes to which jack; the RM520N-GL has no MAIN or DIV connectors (EG25-G names).
  A two-jack build must use ANT0 + ANT2 (engineering, settled by Table 32); the jack count is the owner's (A08).
- Owner of the fix: W3 (generator and land). W6 records identity in `SOURCES.yaml` (`cellular-socket`, `cellular-module`).

## W6-F14. Surge-clamp makers and the board D ESD clamp datasheet

- **C224052 is Littelfuse SMCJ40A, not Vishay (VERIFIED).** JLC API 2026-09-25T21:50Z: "C224052 | SMCJ40A | Littelfuse |
  DO-214AB | ... Unidirectional"; LCSC detail 21:53Z: Vrwm 40 V, Vbr 49.1 V, clamping 64.5 V at 23.3 A, Polarity
  Unidirectional. The same holds for C224047 (SMCJ28A) and C374030 (SMCJ18A). The maker's sheet attached to the code
  (Littelfuse SMCJ series, "Revised: 11/20/15"; SMCJ40A row VR 40.0, VBR 44.40 to 49.10 V at 1 mA, VC 64.5 V at 23.3 A)
  is now filed as `v2/vendor/power/littelfuse-smcj-series-tvs.pdf`, sha256 `6e610db9...5093ea`, fetched 21:56Z from
  LCSC's datasheet link for C224052. The Vishay 88394 and 88392 sheets stay valid as the family's polarity reference
  (cathode band on unidirectional parts, CA suffix for bidirectional) but no fitted code is Vishay.
- **All makers of the one-way clamps**, from the clamp adjudication's LCSC records: Littelfuse (C224052, C224047,
  C374030, C151256, C83270), MDD (C113974, C364296), Diodes (C135085); E D3 has no code (the older E BOM row carried
  C151906, BORN). All are unidirectional; all sixteen are drawn with KiCad's bidirectional `Device:D_TVS` symbol; seven
  are generated reversed (E D1 to D4 and D10, P D1, D D1). Recorded in `SOURCES.yaml` (`tvs-surge-clamps`).
- **PESD5V0S1BA (board D D9 to D14), VERIFIED and now filed.** Nexperia "Bidirectional ESD protection diode",
  PESD5V0S1BA v.6, 26 April 2024 (supersedes v.5 of 23 August 2018), fetched 2026-09-25T21:56Z from
  `https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf` (HTTP 200), byte-identical to LCSC's datasheet for
  C19224, filed as `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf`, sha256 `6546e415b8885ea3...`. Figures: SOD323; VRWM
  5 V max; VBR 5.5 to 9.5 V at 1 mA; IRM 5 nA typ, 100 nA max at 5 V and 25 C; Cd 35 pF typ, 45 pF max; VCL 14 V max at
  12 A; IEC 61000-4-2 contact 30 kV; Tamb -55 to 150 C. C19224 = PESD5V0S1BA,115, Nexperia, SOD-323, Bidirectional,
  stock 39189 (JLC API 21:50Z).
- **Application check at the 5 V mic bias (for W7's disposition and W2).** HS1_MIC and HS2_MIC carry a 5 V electret bias
  from `+5V_D8` through R43 2.2k when JP1 is closed (`gen_sch_d.py:236, 251`). With no headset plugged the conductor sits
  at the rail, which equals VRWM max (5 V); margin to VBR min is 0.5 V; leakage above VRWM is not specified. `+5V_D8`'s
  tolerance is TBD (effect: a rail above 5.0 V runs the clamp past its rated standoff). The speaker conductors swing
  below ground, which a bidirectional part handles (the generator's stated reason).
- **Substitution against decision 31.** Decision 31's text names PESD5V0S2BT (C49338 = Nexperia PESD5V0S2BT,215, SOT-23,
  JLC 21:50Z); the generator fits six PESD5V0S1BA with its reason in `gen_sch_d.py:255-263`. Same maker and standoff;
  the substitution must be recorded in decision 31's record (a record change, not a part defect).

## W6-F15. Board A's power-button controller code is the commercial grade

- `gen_sch_a.py:171` names `LTC2954CTS8-1` with `C683782`. C683782 = **LTC2954CTS8-1#TRPBF**, Analog Devices, TSOT-23-8,
  **0 to +70 C** (JLC API and LCSC detail, 2026-09-25T21:50Z and 21:53Z; `JLC-CERTIFIED.tsv:423`). The held sheet
  (`power/ltc2954.pdf`, 2954fb) gives LTC2954C-1 0 to 70 C and LTC2954I-1 -40 to 85 C. This confirms W2 F-SQ-03 and
  answers its open question.
- I grade at JLC (one reading, 21:50Z): C580654 LTC2954ITS8-1#TRMPBF, stock 195; C2657885 (#TRPBF) and C107801 (#PBF)
  stock 0. Changing the code is a part change: same sheet, same package and pinout (order information table).

## W6-F16. DFM: solder-mask bridges on every committed board

- Rule: JLCPCB capability page (read 2026-09-25, `drafts/box/a10/text_capabilities_2026-09-25.txt`): minimum pad spacing
  for a mask bridge at 1 oz is 0.10 mm (green, red, yellow, blue, purple) and **0.13 mm (black, white)**; at 2 oz,
  **0.20 mm (any colour)**. Every order note specifies matte black mask; every board sets `pad_to_mask_clearance 0`
  (so the bridge equals the copper gap at the fabricator's 1:1 opening) and `solder_mask_min_width 0.1`, which is below
  the 0.13 mm black floor, so KiCad's own DRC would not catch a 0.10 to 0.13 mm bridge.
- Scan: `drafts/w6-scratch/mask_bridge_scan.py` over the seven committed phase boards (A32, B21, C24, D12, E17 at 1 oz;
  P4 and E5 at 2 oz), smallest gap between two copper-and-mask SMD pads of different nets within one footprint.
  Outputs: `drafts/w6-scratch/maskscan/<board>.json`.
- Result: **no footprint on A32, B21, C24, D12 or E17 is below 0.13 mm.** The closest are board B's 0.4 mm-pitch
  LQFP-128 (U101, U201, U301) and TQFP-128 (U1) at **0.15 mm** (0.02 mm margin), A's LTC2954 (TSOT-23-8) and D's U8
  (VSSOP-8) at 0.15 mm. The RP2040 lands on C and E are at 0.20 mm. **P4 U1 (the wrong 5 x 5 mm land) is at 0.177 mm,
  below the 2 oz floor;** the correct RSM land is at exactly 0.20 mm (F2).
- Limits of the scan: it does not look at gaps between different footprints, it skips same-net pairs, and it ignores
  pad corner rounding (which only understates corner gaps). The CM5 receptacle lands were not among the closest ten on B.
- Via-in-pad, from the same page: epoxy or copper-paste filled and capped is the default at six layers and above
  (vias 0.15 to 0.55 mm); blind and buried vias are not supported.

## W6-F17. The certification table does not cover the current clamps

`JLC-CERTIFIED.tsv` (taken 2026-09-20 from the deliverable folders) has no row for C224052 (E D1, D2, D10; A D2 in the
netlist), C224047 (E D4) or C19224 (D D9 to D14). Those codes entered the generators after the folders the table reads
were cut (the suppressor change is commit `23c53a96`, 16 Sep; the PESD change is decision 31). So CMP-002 and SUP-001,
which read the table, cannot have judged these parts. Recommendation (tool owner): the table must be re-taken from the
current netlists, not from the last deliverable folders, before any buyability verdict is used.

## Documents added, and currency

| File | Document | Source | sha256 |
|---|---|---|---|
| `v2/vendor/ti/ti-tps2065c-slvsau6i.pdf` | TI SLVSAU6I, Rev. I, May 2026 | ti.com direct | `898c0934...4be3fcd` |
| `v2/vendor/st/st-an4938-rev7.pdf` | ST AN4938 Rev 7, 29 Oct 2024 | Wayback id_ capture 2025-07-26 (st.com refuses this host) | `217b5dcb...69592bb8b3` |
| `v2/vendor/ti/ti-slla552-tmuxhs4212-schematic-checklist.pdf` | TI SLLA552, March 2021 | ti.com direct | `5258cb80...0a4182e` |
| `v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf` | Nexperia PESD5V0S1BA v.6, 26 Apr 2024 | assets.nexperia.com, 2026-09-25T21:56Z | `6546e415...8dc49a` |
| `v2/vendor/power/littelfuse-smcj-series-tvs.pdf` | Littelfuse SMCJ series, revised 11/20/15 | LCSC datasheet link for C224052, 2026-09-25T21:56Z | `6e610db9...5093ea` |
| `v2/vendor/m2/te-2199119-customer-drawing-revF.pdf` | TE customer drawing C-2199119 rev F | Wayback id_ capture 2024-06-29 (te.com refuses this host) | `ef35dbf8...4bff` |

Not filed, offered to the integrator: the SJK 6CS06000F20UCG crystal sheet behind board D's C252308 (ESR 80 ohm max,
CL 20 pF, -40 to 85 C, drive 100 uW typical), fetched from LCSC's datasheet link, `drafts/box/sjk/`, sha256
`0f9adada...655654`. It is the source of TEST-PLAN F10's 400 ohm margin figure, which today cites only the generator.

## Dependent evidence to invalidate or re-take

1. `JLC-CERTIFIED.tsv` CERTIFIED labels for rows 482-484 (STM32), 539 (TUSB2046), 368 (BQ4050 land), 424 (5G socket key)
   and every row accepted only by the prefix rule; and the missing rows of F17. Re-take from the current netlists after
   the tool is fixed.
2. Board P: everything involving U1's land, including the P8 arm behind decision 28 (owner notice, F2).
3. `v2/vendor/PARTS.md` verdict columns (regenerate after 1).
4. Non-superseded `order/` folders A22, B16, C7, D8 for the seven wrong codes of F8 (decision 41 already quarantines them).
5. Board D deliverables D10 and D11 for C448646 and C167642.
6. Any readiness or FMEA statement that assumes the supervisors' I2C status path works (F4) or that the 5G module mates (F13).
7. Board B's M2B land and the SIM 2 map before any B layout candidate (F13).
