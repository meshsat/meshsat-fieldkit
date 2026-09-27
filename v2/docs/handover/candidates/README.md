# Candidates left in worktrees, exported as patches (handover H1.1)

MESHSAT-1357, exported 27 September 2026 at about 07:40 CEST by the H1.1 editor. Agents were still working in some of
these worktrees when they were exported; each patch is its worktree's state at that moment, and a later state is not
in this package. **Every patch here is an UNACCEPTED candidate, not design.**
None of them is merged into the repository, none has passed its last review without a blocking finding except r8b,
and even r8b is a candidate until the integrator merges it with regeneration parity. Nothing in these patches changes
what `LAYER-STATUS.md` says a layer's status is. They are here so a recipient of the snapshot holds the work the
session had in flight and can apply it, review it or redo it, instead of meeting a branch name that was never pushed.

Prototype framing: no V2 board has been fabricated, ordered, assembled, powered or measured. Every review named below
is an AI review (an author agent and a separate checking agent), not an electrical or mechanical sign-off.

## How each patch was made, and how to apply it

Each patch is the worktree's full change against its base commit, untracked files included, taken through a temporary
git index (the worktree's own index was never written: `cp` of its index to a scratch file, `GIT_INDEX_FILE=<scratch>
git add -A`, `git diff --cached --binary --full-index <base>`). Left out, and listed per candidate below:

- the session's `drafts/` folder, except the files the candidate's own pages cite (its changed files, its drafts index
  page, and what those cite one level on); the drafts left out are scratch (pycache, per-run helpers);
- maker documents (`v2/vendor/**/*.pdf`, and the datasheets under r8b's `drafts/b/datasheets/`) and STL meshes, under
  the pack's own rules (maker documents are referenced by sha256, STL is a tessellation the `v2/cad` scripts
  regenerate); each is named below with its sha256. Where each document came from is in the patch itself: r8b's
  `drafts/b/datasheets/SOURCES.txt` and `SHA256SUMS`, hc5's `drafts/hc5/README.md` (its "New files" table), hc7's
  `drafts/hc7/sources.txt.patch`; the STL files are rebuilt by hc7's `v2/cad/build_case_release.sh`.

Apply to the base commit, never to a later one without re-deriving the drafts:

```
git clone https://github.com/meshsat/meshsat-fieldkit.git && cd meshsat-fieldkit
git switch -c cand/<name> <base>
sha256sum <snapshot>/v2/docs/handover/candidates/<name>.patch   # compare with the table below
git apply --index <snapshot>/v2/docs/handover/candidates/<name>.patch
```

Each patch was checked with `git apply --cached --check` against a fresh index of its base before it was filed.

| Candidate | Layer | Base commit | Patch | Bytes | sha256 | Files |
|---|---|---|---|---|---|---|
| r8b (`fnd/r8b`) | 8, schematics (board B only) | `fc144600` | `candidates/r8b.patch` | 9891575 | `03e6913763ed769ff80fb23c3d76b97d61b0784e3662b7e879abda29df8bdec8` | 67 |
| hc2 (`fnd/hc2`) | 2, concept of operations | `e3aedb25` | `candidates/hc2.patch` | 423221 | `7d1f127a33263bbdcd8bc564ffba08b4adecff41cc17e76ace6a58533aef1191` | 20 |
| hc3 (`fnd/hc3`) | 3, requirements | `e3aedb25` | `candidates/hc3.patch` | 980922 | `39e0c3be9b9c91de057def61726bb4c34dfb70823239272d32bc004e266230f5` | 24 |
| hc5 (`fnd/hc5`) | 5, partitioning and interfaces | `e3aedb25` | `candidates/hc5.patch` | 234158 | `cc3ff1c48ea9289542b6a5792d707bea3b493392b6e3ca7b7637f3e8751ea13c` | 15 |
| hc7 (`fnd/hc7`) | 7, mechanical and enclosure | `e3aedb25` | `candidates/hc7.patch` | 5436056 | `c4432a680b4b9068bc2815045e8a6a07325883786a002dfe60f1fcc37b8d6038` | 90 |

The full base ids: r8b `fc144600544c005c280d6614d26a94dfd3f88511`; hc2 `e3aedb25c849dbda931888b27093ac6c444621cb` (hc3, hc5 and hc7 share hc2's base). Both bases are on the public repository.

## r8b: layer 8, schematics (board B only)

**Status: UNACCEPTED candidate.** Branch `fnd/r8b` in a session worktree, never pushed; base `fc144600`.

**What it holds.** Board B's circuit round 8: the bank fabric's locked break-before-make (FAB-03) and power-good read through Schmitt buffers, the new M.2 B-key land `M2_B-Key_Socket_3052_TE2199119`, the regenerated schematic, netlist, intent and provenance of `pcb-b-compute-b19`, and the integrator's drafts under `drafts/b/` (patches to FAILOVER-FABRIC, ARCH-PCB-B-IOHA, EMCON, PANEL, CONOPS, DECOUPLING, V2-SPEC, the registry and the generated pages; the break-before-make simulator `drafts/b/tools/bbm_sim_r8b.py` and its outputs under `drafts/b/evidence/`) with the decision log `drafts/r8-decisions.md` that ENGINEERING-QUESTIONS EQ-20 cites.

**Last review state.** Independent check 2 (an AI review by an agent that did not write the change): mergeable, no blocking finding, 13 minor findings. Check 1 had found two blocking items (FAB-03 was not a true break-before-make; the integrated candidate failed the suite through `drafts/b/erc-allow-b-r8.patch`); author pass 2 answered both. The check notes that the drafts apply to `fc144600` while main has since moved: eight of the drafted page patches must be re-derived on the newer text before a merge. Source: the session's workflow journal wf_e9094eff-235 (author passes 1 and 2, independent checks 1 and 2).

That review has no blocking finding. Its minor findings, first line each:

- Q212 (AO3400A, C20917) is a FET on EMCON_ON2, yet the L7 row in drafts/b/EMCON-r8.patch section 0a says every EMCON stage on B is an SN74LVC2G06 open drain. The held sheet v2/vendor/power/aos-ao3400a-n-mosfet.pdf (Rev 3.1) gives VGS(th) 0.65 to 1.45 V and RDS(on) 48 mOhm at VGS 2.5 V at TJ 25 C only. L7's remedy asks for RDS(on) at 2.5 V or less over -40 to +85 C, and SD-EMC-1's latency bound depe ...
- The SD-EMC-1 bound (1.16 ms plus 1.84 ms per mF of the module's CINT, to the 3.135 V floor at which HD v1.1 3.3.1 says the module 'will power off automatically') is still conditional. CINT is unpublished (TBD, E-12), and the AP64500 disable delay is INFERRED as one switching period. I confirmed that period, 0.68 us at 1.47 MHz, from DS41979 Eq. 7 with R204 68 k. R204's own value text still says 'R ...
- F1: the order code C89647 resolves to Bourns MF-MSMF110-2 (LCSC: 1.1 A, 6 V, 100 A), which is not a row of the held v2/vendor/power/bourns-mf-msmf-pptc.pdf. The table has only the /8X, /16X, /16, /24X and /33X rows, and the 1.10 A hold, 2.20 A trip and the derating (0.85, 0.77, 0.71 A at 50, 60, 70 C) come from those siblings. It closes energy_chain_b on the integrated candidate. Either file a mak ...
- An undocumented race of a few ns at the end of a move (FAB-02 (b) with FAB-03). When BSEL{b}_D2 flips with ARM and REQ low, BBM{b} falls through the XOR and OR (U80/U81, U85) at about the same time PGSEL{b}_n settles through U513 to U515. U516 to U518 can then pass the previous host's dark flag for a few ns while the select already names the new host. Break-before-make is unaffected, because the s ...
- The allow parser in erc_gate.py (line.split('#', 1) at erc_gate.py:42) turns 'pin_to_pin|#FLG' into a rule that allows every pin_to_pin error. As a result the commit set passed ERC even without the QOD line. I listed all 7 ERC errors on the regenerated candidate: only the two QOD-to-VOUT errors on U21 and U22 are new (main has 5), and they are the maker's configuration (SLVSDH0C Pin Functions, 9.3 ...
- Suite: on exactly the commit set, my box run read 1647 passed, 8 failed, 3 skipped. The author reported 7 failed; my 8th is the rules_status evidence write that follows the failing render tests. The run also rewrote the 8 generated pages in the tree. On the integrated candidate (the 13 drafts applied, the maker documents filed, re-rendered and committed in a scratch clone of fc144600 with its hist ...
- All drafts apply to fc144600, but main has moved to 53a98a71. On that base, CONOPS-r8, DECOUPLING-r8, EMCON-r8, PANEL-r8, pcb_requirements-r8, sources-yaml-additions, generated-pages-r8 and other-boards-sidecars-r8 no longer apply. Boards A, D and E have new netlists on main, so after the merge the five other boards' sidecars (touched only because the new land changes every board's generator ident ...
- The new land v2/ecad/meshsat.pretty/M2_B-Key_Socket_3052_TE2199119.kicad_mod is correct against TE C-2199119 rev F sheet 3 (NPTH 1.1 mm at X -10 and 1.6 mm at X +10, on the line 6.05 below the odd row's outer edge and 3.05 above the even row's). It is written by drafts/b/mk_m2b_te2199119.py, which is outside tools/ and outside b.json's footprint_generator list, so the chain does not regenerate it: ...
- The drafted test_energy_chain.py change finds F1's value in gen_sch_b.py with a regex, which goes against the tree's rule that detectors parse and never grep.
- The docs still name the old RTC: the 0x68 row of PANEL.md (left as context in PANEL-r8.patch) says DS3231M, and ARCHITECTURE.md lines 561 and 699 say DS3231MZ. U9 is now DS3231SN# (C9866, SOIC-16W), with its pins checked against 19-5170 Rev 10: 5 to 12 to GND, 13 GND, 14 VBAT, 15 SDA, 16 SCL.
- U506 now drives EMCON_SUP push-pull onto the three supervisors' PC5 pins, which are TT_a (STM32H743 datasheet pin table). A supervisor unpowered by its bench jumper is therefore fed through the pin from U506, as main already fed it from board C's U9. This is not a regression, and L1's remedy is met as EMCON.md asked. A series resistor would bound the injection.
- SD-EMC-2 remains open, as the author lists, for the RockBLOCK, E22 and E72 lines (no series resistance drawn) and for the two AW7915 cards. With EMCON the cards' supplies are removed, but PERST# through 100 Ohm and REFCLK still reach them, there is no discharge path, and no maker floor exists to judge against. The RM520N case holds at desk: about 77 mA of back-feed into 15 Ohm is about 1.2 V, unde ...
- Verified with no finding against the makers' documents (worktree r8b): - FAB-01 on DS40068 Rev 5-2 3.3/3.4 (U101, U201, U301). - FAB-04: 23 lines at 10 k with the loads unchanged. - FAB-02 (b)/(c): TS3DV642 Table 1 and SEL2 port mapping, 74LVC1G157GW pinout and function (Nexperia Rev. 12 Tables 3, 4, 6), PG only into 74LVC1G17 (DS35124 has no transition limit). - FAB-03 lock: every move o ...

**Drafts kept in the patch:** 60. **Drafts left out:** 0.

**Held out of the patch (fetch and check by sha256):**

| Path in the worktree | Bytes | sha256 |
|---|---|---|
| `drafts/b/datasheets/adi-ds3231-19-5170.pdf` | 843828 | `dc81cd89bee82d0c57b654d6315e03dec913fb8fe753cc80b2a3f1cca71cbb34` |
| `drafts/b/datasheets/nexperia-74lvc1g157.pdf` | 245550 | `62f9b85c44785ca14f681958a44df1a1106f0006d050e93b20c56d738d15e789` |
| `drafts/b/datasheets/ti-sn74lvc2g06.pdf` | 1853733 | `b5533064ff102afca29c87df4ce5b6b1771dd5eb5f869ed787c07ef66ece5910` |
| `drafts/b/datasheets/ti-tpd4e001.pdf` | 1493613 | `e10f97586a1aa314c9e379a2afa0e8ce2c00e3428f53497b81164d52e121b677` |
| `drafts/b/datasheets/ti-tps3808.pdf` | 2046179 | `74d889c0f68af88032f1633c26381817cc03e10d9fd3b4c177a044ad3ed86eed` |

## hc2: layer 2, concept of operations

**Status: UNACCEPTED candidate.** Branch `fnd/hc2` in a session worktree, never pushed; base `e3aedb25`.

**What it holds.** The layer 2 closer's pass 2: `CONOPS.md`, `OPERATING-ENVELOPE.md`, `PANEL.md`, `TEST-PLAN.md`, `pcb_envelope.yaml`, the Review A layer 2 record `v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27.md`, and the drafts that record cites (registry, coverage, part_temps and gen_sch_b BANK-R1 patches, `pwr_red2.py` and its output, the layer status draft, the hand-offs).

**Last review state.** Review A, layer 2, pass 2 (an AI review): FAIL, 2 blocking findings, 15 minor. Pass 1 had 7 blocking findings (B1 to B7), which pass 2 of the closer answered. Source: the session's workflow journal wf_16294096-1dc (close L2 passes 1 and 2, Review A layer 2 passes 1 and 2).

Blocking findings of that review, as the reviewer wrote them:

- **P2-B1: an owner ruling that carries the session's choices without saying so (CONOPS.md line 938, section 7, row D-02b)**
  The owner's D-02b ruling cell adds, after 'As ruled; carried since 27 September 2026 by section 4c:', three of the session's own choices: the reduced mode on slots 2 and 3, the one-module heat stage, and the BANK-R1 hub-port exchange (SC-L2-01, 02 and 18). Nothing in the row says the session made them. The D-06 row in the same table does mark its 27 September addition as 'taken by the session', and so does OPERATING-ENVELOPE section 8. Read on its own, this row presents the session's choices as part of the owner's ruling. Fix: one clause, 'taken by the session under the owner's standing rule of 26 September 2026 (section 7a)', plus 'restated by the session' before the two consequences.
- **P2-B2: nothing protects the pack once the heat stage fails on an input (CONOPS lines 562-566, the Heat stage row at line 308, 4c lines 630-646, no row in 4e, TEST-PLAN E3-L at line 135)**
  Case: +40 C, lid closed, the independent bound's lowest conductance, the kit on vehicle or shore input. That is M2's own case.
  - Inside air: +60.6 C as generated and +62.1 C after BANK-R1 (pcb_envelope.yaml line 67).
  - On an input the pack carries no current, so the cells sit at about the inside air.
  - The charge hold (OTC 44 C) removes no heat, OTD acts only on discharge, and C1 has nothing left to shed. CONOPS says 'There is no stage after this one', and only the pack case is covered.
  - The cells therefore sit above the maker's +60 C, near the second level's 62.7 C trip (which blows F2) and the gauge's permanent SOT at 64.2 C.
  - THERMAL-COORDINATION on main already records 'nothing sheds the kit's own heat by cell temperature, and on shore L8 cannot either'.
  The layer closes its hot end on the claim that behaviour on measured temperatures makes it indifferent to the unmeasured conductance. That claim fails at the recorded low end, and 'no further stage' is this layer's decision resting on a bound that includes failure.
  Fix:
  - Define a final control on measured temperatures, on the pack and on an input: modules shut down, charge held, the operator told, restart below a stated margin. Record it as a session choice with its reversal.
  - Carry it into the Heat stage row, 4c, 4e, 4f, M2, OPERATING-ENVELOPE section 4 and pcb_envelope.yaml hot_end.
  - In E3-L, add its expected action and an abort at a cell surface of +59 C.
  - State that at this corner, closed-lid operation at +40 C is predicted to fail REQ-052 on any supply (a layer-4 item under FEA-004).
  No requirement or envelope limit is lowered.

**Drafts kept in the patch:** 14. **Drafts left out:** 0.

## hc3: layer 3, requirements

**Status: UNACCEPTED candidate.** Branch `fnd/hc3` in a session worktree, never pushed; base `e3aedb25`.

**What it holds.** The layer 3 closer's work: `pcb_requirements.yaml` (140 records at the closer's pass 1, every pass line settled, every rule given a parent), the regenerated `REQUIREMENTS-TRACE.md`, `pcb_board_facts.yaml`, `pcb_energy_chain.yaml`, `pcb_pack_protection.yaml`, the Review B layer 3 record `v2/docs/reviews/REVIEW-B-LAYER-3-2026-09-27.md`, and the drafts that record cites (the registry apply script, citation re-reads, the blocked questions, the transcribed standards and the PVGIS reading under `drafts/hc3/vendor/`).

**Last review state.** Review B, layer 3, pass 1 (an AI review): FAIL, 6 blocking findings, 18 minor. The closer's pass 2 was running when the patch was exported; its result is not in this package. The drafts number new open items from S-47, which H1 already uses (HC9-E1), so they renumber at merge. Source: the session's workflow journal wf_16294096-1dc (close L3 pass 1, Review B layer 3 pass 1; close L3 pass 2 had started and had written no result when this patch was exported, so the patch holds the worktree as it stood then).

Blocking findings of that review, as the reviewer wrote them:

- **B1. Hot end on an input: SC-17 'No further stage' (pcb_requirements.yaml:1111), CON-012, REQ-024, REQ-046, REQ-052, FEA-004**
  The registry adopts the heat stage as the last stage on a bound that includes failure. fnd/hc2's pcb_envelope.yaml (6333e5d2) gives the worst inside air at +40 C with the lid closed as 62.1 C (60.6 C as generated). On shore or vehicle input the idle cells sit near that air, above the cell maker's +60 C 'Don't leave, charge or use' limit (35E Ver. 1.1). REQ-052's own E3-L pass line (every cell at most +60 C, no permanent protection action) then fails on shore too. No core NEED-13 record requires the kit to act before idle cells pass +60 C, because REQ-046 covers only the charge and discharge windows. FEA-004's list of what it would reopen omits this. Layer 2's Review A pass 2 finding P2-B2 (06:50) found the same thing; this review confirmed it independently. Fix: carry layer 2's final thermal control into SC-17, CON-012 and REQ-024, and add a core requirement (shed and hold below a stated cell threshold, with an E3-L abort) listed under FEA-004.
- **B2. REQ-041 (line 5795, acceptance line 5805)**
  'its only alarm levels are REQ-042's' drops the lightning detector's mast-down alarm. The owner approved it in the 32.50 sensor walk-through (MESHSAT-709-geometry-appendix.md:2802, sensor 6), and V2-SPEC.md:65 states it. No other record carries it, so the closure drops an owner-approved function.
- **B3. REQ-034 (line 5291, acceptance line 5300)**
  The compatibility TBD was replaced by 'no document claims night-vision compatibility'. That leaves NEED-09's 'night-vision-compatible panel' with no design target for board C's indicators, light guides or the monitor. D-01 deferred the NVG claim, not the design ('every ruled function stays designed and fitted'), so this lowers the requirement. Fix: a need-level compatibility target (a filed public standard class, or a measurable intensifier viewing criterion) with 'no claim until tested'.
- **B4. REQ-016 (line 3414, statement line 3420) and SC-35 (line 749)**
  The window is claimed 'as generated' but allows up to 28 V open circuit, the SMCJ28A standoff. gen_sch_e.py lines 384-418 chose that standoff to sit 3 V above the '25 V a cold 36-cell panel reaches' and declare the panel entry v_max=25.0, the value derating judges PV_P's parts against. So the claim contradicts its source, and the requirement admits panels the design never considered. Fix: 25 V, or raise the generator's v_max and re-judge the parts.
- **B5. CONOPS M1 against REQ-016, REQ-072 and SC-36 (line 777)**
  fnd/hc2's CONOPS M1 (ab28e85b), the text integration takes, still says 'the LT8705A tracker's own limit is TBD', that 'REQ-016's panel class and input window follow' from layer 4, and that 'no insolation figure is held in this tree'. The registry makes REQ-016 DEFINED at 100 W and files PVGIS. SC-36 restricts M1 to April to September ('from October to March no solar-sustained mission duration is claimed'), a scope statement CONOPS does not carry. The drafted CONOPS-d11 patch does not touch M1. These are contradictions with the pinned needs document plus a scope narrowing made only in a session choice.
- **B6. CFL-010 (line 7087) kept CONFLICT_OPEN (core BLOCKER)**
  SC-12 and fnd/hc1's V2-SPEC settle the SIM description. What keeps CFL-010 open is board B's SIM TVS array (layer 8) and the eSIM variant's order code (layer 6), neither of which is a contradiction between sources. The layer-status draft still claims the contradictions item met. Layer 3 is held on a later board's work, which the owner's prompt section 1 forbids. Fix: resolve CFL-010 at integration and carry the TVS array (at most 10 pF) as a board B constraint that reads FAIL until it is drawn. Nothing is lowered.

**Drafts kept in the patch:** 18. **Drafts left out:** 16 (`drafts/hc3/CONOPS-pass2.on-hc2-d11.patch`, `drafts/hc3/SOURCES-hc1.yaml`, `drafts/hc3/SOURCES-hc3.yaml`, `drafts/hc3/TEST-PLAN-hotstop.on-hc2.patch`, `drafts/hc3/author.py`, `drafts/hc3/engine.py`, `drafts/hc3/fmt.py`, `drafts/hc3/ops_int.py`, `drafts/hc3/ops_l12.py`, `drafts/hc3/ops_l2.py`, `drafts/hc3/ops_l3.py`, `drafts/hc3/rebuild.sh` and more).

## hc5: layer 5, partitioning and interfaces

**Status: UNACCEPTED candidate.** Branch `fnd/hc5` in a session worktree, never pushed; base `e3aedb25`.

**What it holds.** The layer 5 closer's pass 2: `v2/docs/HW-FW-CONTRACT.md` (the hardware and firmware contract, version 1), the records under `v2/docs/records/hc5/` (the kit I2C budget and the contract field check with their outputs, the USB 2.0 clauses cited), the two worktree drafts filed as records (`records/w5/`, `records/r4a/r4-hwfw-contract.md`), and the apply scripts under `drafts/hc5/` with their README (eighteen new interface contracts, ARCHITECTURE section 12, the registry and index edits).

**Last review state.** Review 2 (an AI review): FAIL, 2 blocking findings, 13 minor. Review 1 had been PASS_WITH_FIXES with three blocking items, which author pass 2 answered. Source: the session's workflow journal wf_e740f6f9-ca3 (hc5 author passes 1 and 2, reviews 1 and 2).

Blocking findings of that review, as the reviewer wrote them:

- **SC-HF-06 is not carried consistently: after the drafts are applied, the tree gives three different board ends for the monitor touch lead**
  IF-MON (pcb_interfaces-new-contracts.yaml) and SC-HF-06 put the touch USB on board D's J_USB3. Three places contradict that once the drafts apply to 84e52461. (a) drafts/hc5/ARCHITECTURE-section-12.md line 73 (ARCHITECTURE.md line 1181 after apply_architecture.py) lists 'board D's spare hub port J_USB3 (no lead is defined)' under 'Not given a contract, deliberately'. The same section's IF-MON row, at line 54, names D J_USB3 as the touch end. Section 12 is the text review item 1 was about. (b) ASSEMBLY.md build step 9 (line 73) still routes the monitor's 'USB touch ... to ... the slot hub header' on B16. apply_docs.py corrects only the section 4 leads row. (c) PANEL.md section 1, the Pass-throughs row at line 50, still says the monitor's 'HDMI, USB touch and 12 V leads go below the plate to B16 and A22'. The owner's L5 item 'harnesses defined and consistent' is therefore not met for this lead. Fix: remove J_USB3 from the not-contracted list in the section 12 draft. Add outside-ownership patch lines, each with its reason, for ASSEMBLY.md step 9 and PANEL.md section 1, and rebind the readings bound to those pages as apply_docs.py already does.
- **IF-BA-RF says board E's D-07 clamp is in no generator, which main 84e52461 contradicts**
  The RM520N-GL path note in pcb_interfaces-new-contracts.yaml reads: 'ANT3 under owner ruling D-07 needs board A's site at X +46 and board E's clamp: in no generator'. Pass 2 says IF-BA-RF was filled and re-read at 84e52461. At 84e52461, gen_pcb_e.py (commit 45f6d83f) draws the twelfth cavity at X 46: RF_SITES includes (46.0, "5G ANT3"), and check_pcb_e.py requires it. The closer's own section 12 IF-AE-RF row also says the clamp bar is drawn in round 8. Only board A's site at X +46 is undrawn. As written, the note tells a recipient that the board E half of D-07 is still owed. Fix: 'board A's site at X +46 is in no generator; board E's cavity at X 46 is drawn since 45f6d83f'. The IF-BA-RF tbd entry and findings should read the same way.

**Drafts kept in the patch:** 6. **Drafts left out:** 9 (`drafts/hc5/ARCHITECTURE-section-12.md`, `drafts/hc5/connectors-e3aedb25.txt`, `drafts/hc5/hc5-shared-files.on-84e52461.patch`, `drafts/hc5/pcb_interfaces-new-contracts.yaml`, `drafts/hc5/tools/netread.py`, `drafts/hc5/tools/show.py`, `drafts/hc5/zer/run-100kHz.txt`, `drafts/hc5/zer/run-90kHz.txt`, `drafts/hc5/zer/zer_budget.py`).

**Held out of the patch (fetch and check by sha256):**

| Path in the worktree | Bytes | sha256 |
|---|---|---|
| `v2/vendor/connectors/3m-3365-flat-cable-ts0080.pdf` | 1328131 | `1dc900fe684bd6c20713123178dc80544e7c0cef1faf8f268aa6e2f653e28aa3` |
| `v2/vendor/standards/nxp-um10204-rev6-i2c-bus-specification.pdf` | 1395785 | `b7619700e8bb9dd4d2c1e7bae7238db9c579d399c45bc32c4ff037bc800ec044` |

## hc7: layer 7, mechanical and enclosure

**Status: UNACCEPTED candidate.** Branch `fnd/hc7` in a session worktree, never pushed; base `e3aedb25`.

**What it holds.** The layer 7 closer's pass 2: the case set C1 to C6 from one geometry source (`v2/cad/` generators: face plate, frame legs, connector plate, RF entry plates, the Z stack `zstack.py`/`zstack.json`, drawings and the release script), `v2/docs/CASE-FIT-UNCERTAINTIES.md`, `panel1450.py`, `z_budget.py`, `case_wall_cutouts.py`, `test_case_geometry.py`, the release folder `v2/release/case-2026-09-27/` (STEP, DXF, dimensioned PDFs, board envelopes), and the drafts its pages cite (`drafts/hc7/`: CASE-MARGINS, ASSEMBLY, READY-TO-ACT and CONOPS patches, the check_pcb_c, rules_status and stage_chain patches, box readings under `drafts/hc7/records/`).

**Last review state.** Review 2 (an AI review): FAIL, 2 blocking findings, 12 minor. Review 1 had been PASS_WITH_FIXES with three blocking items, which author pass 2 answered. Source: the session's workflow journal wf_e740f6f9-ca3 (hc7 author passes 1 and 2, reviews 1 and 2).

Blocking findings of that review, as the reviewer wrote them:

- **Mock-up timing across the drafted live specs (closer claims: 'ASSEMBLY, CASE-MARGINS, READY-TO-ACT and CONOPS drafts aligned to ... the new mock-up timing'; 'the CASE-MARGINS section 7, READY-TO-ACT 6.1 and CONOPS patches bring those files in line')**
  Contradicted by the patched files. I applied every draft to an archive of current main a8652172. Four places still carry the old timing. (1) drafts/hc7/ASSEMBLY.md.patch, note (13) (ASSEMBLY.md:36) and the section 3 pack paragraph (ASSEMBLY.md:109), both say the mock-up is 'recommended before the outlines of boards A, B, C, E and P freeze, CASE-MARGINS.md section 7, seventh revision'. (2) v2/docs/reviews/READY-TO-ACT.md after its patch still has S-8 (line 671): 'it does not gate their layout entry ... no layout-entry gate depend on an unauthorised purchase'. (3) It also keeps section 1 (lines 48-55): 'None of the following waits on an item of section 0: ... the per-board path into layout'. (4) 6.1's retained first sentence says 'CASE-MARGINS.md section 7 recommends it for the build stage'. In addition, CASE-MARGINS.md's opening 'Why this document exists' paragraph (line 25) still reads 'recommends before ... boards A, B, C, E and P are frozen for routing'. Against these, CASE-MARGINS section 7 (patched), CASE-FIT-UNCERTAINTIES.md sections 1/2/7 and FEA-007 say the checks are REQUIRED before layout entry of A, B, E and P only, BLOCKED on D-09. After landing, the live specs contradict each other on whether the mock-up gates layout entry (owner prompt section 6). Fix: bring those five passages to option (a), or state in each that the 27 Sep allocation supersedes it.
- **QMX lid tray: a made part in layer 7 scope, and the closed acceptance 'dimensioned drawings of every made part'**
  The audit named 'tray position' among the missing drawings. The rebuilt v2/release/case-2026-09-27/ contains no tray files and no sheet that draws the tray or its place on the lid. I checked the README Contents table and the text of all 13 sheets: only rows M3 and M19 mention it. The only released tray files are v2/release/revA/case/lid-bracket-qmx/*.step/.stl. The closer's new HISTORICAL banner covers that folder: 'Do not make, cut, drill or order anything from this folder', and it lists 'the QMX tray at X 103.5 (now 102.0)' as replaced by the new set. Yet the ASSEMBLY patch's QMX row (ASSEMBLY.md:55) still sends the builder to `case/lid-bracket-qmx/`. The closer's closed item lists plate, legs, connector plate, entry plates, Z stack, plan and envelopes, and still_open does not mention the tray. Fix: either add lid_bracket_qmx.py's STEP/STL and a placement sheet (X 102.0 to 171.0, the four M3 into bonded nuts) to the release, or exempt lid-bracket-qmx/ in the banner, point ASSEMBLY at the editable source, and move the tray drawing to still_open.

**Drafts kept in the patch:** 24. **Drafts left out:** 2 (`drafts/hc7/frame_seat.out.diff`, `drafts/hc7/frame_seat.py.diff`).

**Held out of the patch (fetch and check by sha256):**

| Path in the worktree | Bytes | sha256 |
|---|---|---|
| `v2/release/case-2026-09-27/connector-plate/connector-plate.stl` | 633484 | `4cb9e066089e58ec5a39c6ab522f21c27413d127447d238e26bbc3614a8fb9dd` |
| `v2/release/case-2026-09-27/face-plate/face-plate.stl` | 1416484 | `66061f07767c11c442345c4ae28eaffb34caf7a4c83bfcb6aa85e063a21c095c` |
| `v2/release/case-2026-09-27/frame-legs/frame-leg.stl` | 5084 | `d2f7004da65dd909c6188eb5da56e236a9146bdb6cd68aa8cf88bdcb44f1a24d` |
| `v2/release/case-2026-09-27/frame-legs/leg-locator.stl` | 9884 | `5d40b356cd7991ee710d0f07bb6ab4e08867b6be2f8ff603a8f26e93265a3d62` |
| `v2/release/case-2026-09-27/frame-legs/wedge.stl` | 4284 | `8c49cb7a62813694d4d8970d6b3761e14bbeac6381128b189d8078195c2e3bcb` |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-east.stl` | 482484 | `e661e592c85b202a3796ce0e4bc3a67cdad394bc712c72dbe4a01a86c76923b3` |
| `v2/release/case-2026-09-27/rf-entry-plates/rf-entry-plate-west.stl` | 583684 | `b18d4738036caebfbaf7aa6ac8bbfecf8db63dcc955eef9529d4b4ae7ff3b439` |
| `v2/vendor/connectors/hro-type-c-31-m-12.pdf` | 118176 | `6ae33d50ac47820114661138dc4e4659f40fdc5d4f485b46685dfec338da1a9e` |
| `v2/vendor/connectors/jst-vh-catalogue.pdf` | 122881 | `d51e669c597988b20c0963daf5bef7356cbd2104c1f867e9107c6fa6cd2b899c` |

## Where the pages point here

`LAYER-STATUS.md` ("Candidates left in worktrees"), `CONTINUATION-BRIEF.md` sections 0 and 4, and
`ENGINEERING-QUESTIONS.md` EQ-20 name these patches. A step that says "merge r8b" means: apply `r8b.patch` to
`fc144600`, re-derive its drafted page patches on the current text, regenerate board B on a KiCad 9.0.9 host with
parity (REGENERATE.md sections 2 and 3), and only then commit it as design.
