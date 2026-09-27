# Definition status: layers 1 and 2

The status page of the two completed definition baselines of the foundation baseline (MESHSAT-1357):
`v2/docs/PRODUCT-BRIEF.md`, layer 1, the product definition, and `v2/docs/CONOPS.md`, layer 2, the concept of operations. It exists so
that the baselines change only when the definition does (the independent review of handover H2, `v2/docs/reviews/2026-09-27-h2-independent-review.md` section 4). Prototype design: no V2 board has been fabricated,
ordered or powered, and no kit has been field deployed; nothing on this page is a claim about a built product.

## The rule

A definition baseline is reopened only when a requirement, the scope, the operating concept or a product decision
changes. A changed count or a circuit correction updates this page and the records it names, not the baseline. When a
change does reopen a baseline, the affected document is issued again through its layer's review, and the change is
stated in it; nothing is narrowed silently.

## The two baselines

| Layer | Document | BASELINED at | sha256/16 of the file baselined | Release record (AI reviews and checks, none a qualified engineering review) |
|---|---|---|---|---|
| 1, product definition | `v2/docs/PRODUCT-BRIEF.md` | `6b2a9965` | `d36bf76b3dea8b30` (unchanged through `31cd29b9`) | `v2/docs/reviews/TARGETED-CHECK-LAYERS-1-3-2026-09-27.md`, the narrow verification of the targeted fix, after `v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` |
| 2, concept of operations | `v2/docs/CONOPS.md` | `79963b3b` | `3ff59edc96a3f8f4` as the release check read it at `eb9f9030`; `4483209659dc391c` with its status line written (`62f26a44`, unchanged through `31cd29b9`), the file handover H2 carries | `v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` |

`v2/docs/handover/LAYER-STATUS.md`, layers 1 and 2, names every review record of both layers with its evidence.

## The restructure of 27 September 2026

On 27 September 2026 (branch `fnd/defstab`, from `31cd29b9`) both documents were restructured as the review asks.
Each keeps its definition, meaning its purpose, scope, users, prototype scope, exclusions, fixed constraints, operating
intentions, needs, missions, modes, scenarios and product decisions, with every sentence word for word, and states at
its head the rule above and one sentence per dependency naming where that dependency's current state lives. The
review history of the baseline attempts, and the notes that recorded each document's own revisions, moved to an
appendix at the end of the same file, headed "Appendix: review and status history (not part of the baseline)". The
changing implementation results that stood in running text (transmitter counts, circuit revisions, feasibility-blocker
counts, reading results, commit-by-commit status) moved to this page, word for word, below. Nothing was split or
reworded: a sentence that carries definition content and a result together stayed where it was, and so did every
table row but its revision notes; each document's head says that such a figure or remark is its value at the baseline.

The map of every move is `drafts/defstab/moves.json` in the branch's worktree, written with the build script that
asserts it (`drafts/defstab/build.py`, `cuts.py` and `heads.py`), to be filed under `v2/docs/records/defstab/` when the
branch is integrated. For every moved block it gives the old line range at `31cd29b9`, the new location and the
sha256; for every block of each definition it gives the sha256 before and after, and which moves closed it up. The
script checks that each kept block equals its original with the moved text removed, that every sentence of a kept
block is a sentence of the original, and that every moved text stands byte for byte at its new place. CONOPS's needs
table is byte-identical; the requirements registry's pin on the whole file (`needs_document_sha256`) is re-taken, and
the three readings bound to CONOPS (REQ-005, CFL-014 and CFL-016) are rebound, each with an entry naming what moved and
stating that the statements it rests on are unchanged. No reading is bound to the brief.

**Not re-stamped.** The restructure does not take either baseline again: each stands at its commit in the table above.
Whether the restructured text carries its baseline unchanged is for a check of the map by a session or person that
wrote none of the restructure. State: OWED.

## Where the current state lives

| Dependency | Where its current state is kept | Where the definition relies on it |
|---|---|---|
| What the design has shown, board by board, and each board's readiness for layout | `v2/docs/CURRENT-EVIDENCE.md` | the brief, "What it is not, today" |
| Every requirement with its reading; the feasibility blockers on the core, FEA-001 to FEA-007, each with its closing evidence and stage | the requirements registry `v2/ecad/tools/pcb_requirements.yaml` and `v2/docs/REQUIREMENTS-TRACE.md` | the brief, "What the first prototype has to show"; CONOPS section 2a |
| EMCON, transmitter by transmitter, against D-05 and REQ-071 | `v2/docs/feasibility/EMCON.md` section 0a; FEA-002, REQ-030 and REQ-071 in the registry | the brief, "What the V2 kit is" (emission discipline); CONOPS M4, sections 4b and 4b.1 |
| Power, thermal and runtime; the hot end; M1's energy balance | `v2/docs/feasibility/POWER-THERMAL.md`; FEA-004, REQ-014 and REQ-072 in the registry | the brief, "What it is not, today"; CONOPS M1 and sections 4a, 4c, 5 and 6 |
| The heat stage's required set on board B (BANK-R1) and the hot stop's path (HOT-R1 on boards A and E) | REQ-052 and REQ-077 in the registry | CONOPS section 4c |
| The kit's fit in the Peli 1450 and the case set the generators carry | `v2/docs/CASE-MARGINS.md`, `v2/docs/CASE-FIT-UNCERTAINTIES.md` and `v2/release/case-2026-09-27/`; FEA-007 in the registry | the brief, "What the V2 kit is" (the pack, the antenna entries); CONOPS section 4a (the pack) |
| ZEROIZE on the fitted secure element | `v2/docs/feasibility/ZEROIZE.md`; FEA-001 in the registry | the brief, "What the V2 kit is" (key protection); CONOPS section 4, ZEROIZE row |
| Each layer of the handover and its reviews | `v2/docs/handover/LAYER-STATUS.md` | the appendix of each document |

## What the two documents carried at their baselines

Moved here word for word on 27 September 2026 from the running text of the two documents at `31cd29b9` (for the
brief, the text baselined at `6b2a9965`; for CONOPS, the text it has carried since `62f26a44`). Each entry is the state
as it stood then, not a current reading: the current state is the source the table above names, and a later change is
recorded there, never by editing the baselines. Paths in the moved text are relative to `v2/docs/`, as in the
documents it came from.

### From `PRODUCT-BRIEF.md`

Eight entries, in the brief's order.

#### B-S1. From the head (the framing paragraph)

*`PRODUCT-BRIEF.md` lines 34 to 36 at `31cd29b9`: the evidence headline's counts, quoted.*

What the design has and has not shown
today is `CURRENT-EVIDENCE.md`, whose headline reads **"Foundations incomplete; 0 boards ready for layout; 0
physically verified."**

#### B-S2. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 116 to 121 at `31cd29b9`: what the EMCON line is drawn to do as generated, with board B's round 8.*

As generated at `45bde541` the line is drawn to remove the supply of the
  SDR, the RockBLOCK, the LoRa module, both Zigbee and Thread radios, the HF unit and both WiFi link cards, to turn off
  the PA's rail and keying while the VHF exciter keeps receiving, to pull the compute modules' own WiFi and Bluetooth
  disables low, and to put the 5G module in airplane mode through its disable pin, a mode its own firmware carries out;
  since board B's round 8 (27 September 2026) it also removes the 5G module's supply by hardware at once (SD-EMC-1r8,
  `feasibility/EMCON.md` section 4b; `CONOPS.md` section 4b).

#### B-S3. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 123 to 137 at `31cd29b9`: the transmitter counts (17, 15 of 17 local, 0 of 17 end to end) and their open rows.*

Read transmitter by
  transmitter against that (`feasibility/EMCON.md` section 0a, sixth revision, with board B's round 8), the kit has 17
  transmitters and **none is dark end to end, at desk or on a bench**:
  - Locally, the radio's own chain closes at desk for 15 of the 17 and is open for two. The SA868 VHF exciter: its
    maker publishes no receive threshold for the PTT pin the design holds at 2.677 V or more (bench E-01). The RockBLOCK
    9704: once its supply is cut it keeps running on its own supercapacitors, about 16 J, with its ENABLE held by a
    firmware-driven expander, so the ENABLE forced low by the EMCON hardware is owed, and what the Iridium module does
    when ENABLE falls is stated in no held document (section 4.4). The 5G module's chain closes at desk since board B's
    round 8: its supply is removed at once, with RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input
    capacitance, which no held document states (bench E-12), and the maker's warning that cutting a working module's
    supply can corrupt its flash accepted as a residual (section 4b).
  - End to end, 0 of 17 rows is closed: every row also waits on the items the rows share, the toggle and its conductor
    (accepted by SD-EMC-6 only with a hardware EMCON lamp on board C, drawn since board C's round 8 as `D22` with no
    processor in its path, and not yet visible, because its light-guide hole in the face plate is owed, open item
    S-44) and the EMCON line's own open items (sections 3 and 7), and no row is shown to meet the latency.

#### B-S4. From the section "What the V2 kit is" (emission and light discipline)

*`PRODUCT-BRIEF.md` lines 139 to 142 at `31cd29b9`: the bench state and the lamps as drawn (D22, the TX lamp's supply).*

No row has been shown on a bench; EMCON is feasibility blocker FEA-002 of the requirements registry. The one panel
  indication of EMCON that is independent of firmware is that lamp, lit while both EMCON lines read low, fed ahead of
  the panel's dimmer and dark in BLACKOUT (`PANEL.md` sections 1 and 4); the TX lamp's supply exists only while the
  panel controller drives its LED dimmer (`feasibility/EMCON.md` section 0; `PANEL.md` section 3, GPIO 8).

#### B-S5. From the section "What the V2 kit is" (antenna entries)

*`PRODUCT-BRIEF.md` lines 164 to 167 at `31cd29b9`: which commit's generators and release folders carry the case choices.*

The case generators carry C1 to C6
  since `c351115d`, and the current case set (CAD, drawings and 1:1 templates) is `v2/release/case-2026-09-27/`; the
  committed board files and the deliverable folders of `v2/release/revA/` predate it and still carry the earlier
  eleven coupler sites at 88 mm, which is history.

#### B-S6. From the section "What it is not, today" (not ready for layout)

*`PRODUCT-BRIEF.md` lines 181 to 184 at `31cd29b9`: board readiness and the circuit corrections the deliverable folders predate.*

No board of the set is ready for layout, and no layout of boards A, B, C, D, E
  or P carries its board's corrected schematic (board E5 has no schematic; its board file is its design): the
  deliverable folders of `v2/release/revA/boards/` predate the circuit corrections of `faf8c981`, `458b2873` and
  `d90f30e4` and every later one (`CURRENT-EVIDENCE.md`, the candidate table).

#### B-S7. From the section "What it is not, today" (runtime)

*`PRODUCT-BRIEF.md` lines 214 to 217 at `31cd29b9`: the power model's current runtime figures and the commit that aligned CONOPS.*

The current PROVISIONAL model
  gives an aged pack 2.5 h in the idle mode and 1.7 h in the typical mode, within bounds of 1.3 to 3.3 h and 0.9 to
  2.3 h (`feasibility/POWER-THERMAL.md` section 6, PWR-F07); `CONOPS.md` sections 4a and 6 carry the same
  PWR-F07 figures since the layer 2 merge (`95e078a1`).

#### B-S8. From the section "What the first prototype has to show"

*`PRODUCT-BRIEF.md` lines 261 to 265 at `31cd29b9`: the count of open feasibility blockers on the core.*

Seven feasibility blockers on the core are not closed (FEA-001 ZEROIZE, FEA-002 EMCON, FEA-003 the
failover fabric, FEA-004 power and thermal, FEA-005 pack protection, FEA-006 decoupling, and FEA-007 the kit's fit in
the Peli 1450 on the case choices C1 to C6, core as a condition of every core function under the session's SC-04;
requirements registry, kind feasibility); each names the evidence that closes it and the stage at which that evidence can exist
(`EXECUTION-PLAN.md`, stage gates).

### From `CONOPS.md`

Seven entries, in the document's order.

#### C-S1. From section 3, mission M4

*`CONOPS.md` lines 275 to 285 at `31cd29b9`: the gaps as generated, board B's round 8 and the transmitter counts.*

As
generated since `458b2873` the two gaps this mission first named are closed in the schematic: the compute modules'
own WiFi and Bluetooth are pulled off through open drains, and the WiFi link cards lose their supply. What remains is
session work under the ruling (S-01), read transmitter by transmitter in `feasibility/EMCON.md` section 0a: the 5G
module, whose only path was its disable pin, a firmware-mediated airplane mode, and the items every row of the EMCON
line shares (section 4b). **Since board B's round 8 (27 September 2026) the 5G module's supply is removed by hardware
at once and board B's shared items are drawn (section 4b)**, so the radio's own chain is closed at desk for 15 of the
17 transmitters and open for two: the SA868 (its PTT pin's receive threshold is unpublished) and the RockBLOCK 9704
(once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware). No row is closed end to
end, from the toggle to silence at the antenna port, so NEED-08 is not met for any transmitter until the design closes
it, and no row has been shown on a bench.

#### C-S2. From section 4b (the D-05 paragraph)

*`CONOPS.md` lines 455 to 468 at `31cd29b9`: the transmitter counts, board B's round 8 and the open shared items.*

Read transmitter by transmitter
(`feasibility/EMCON.md` section 0a, sixth revision), the radio's own chain meets that meaning at desk for 15 of the 17
transmitters. The 5G module's is among them since board B's round 8 (27 September 2026): its only EMCON path had been
its disable pin, and its supply is now removed by hardware at once with a bounded time to RF off (EMCON.md section 4b,
SD-EMC-1r8). Two stay open: the SA868, whose PTT pin's receive threshold its maker does not publish (bench E-01), and
the RockBLOCK 9704, whose own supercapacitors keep the module running after its supply gate opens, with its ENABLE held
by firmware (EMCON.md section 4.4). What every row
shares was open as well (EMCON.md section 7: the line's hold with its source gone, a loss of board B's `+3V3_DEV`
that released every gate hung on `EMCON_ON` or on `U{s}11`, gate supplies outside their range, the drive of the
2N7002s, and the back-feed paths of SD-EMC-2); on board B round 8 closes the hold, the `+3V3_DEV` loss and the drive at
desk, and the 5G module's back-feed, and leaves open the gate supplies of `U501` to `U505` and the back-feed into the
RockBLOCK, the E22 and the E72 (EMCON.md section 4b); end to end, from the toggle to silence at the antenna port within
the latency of REQ-071, no row is closed; and no row has been shown on a bench (EMCON.md section 6, twelve tests, none
of which can use the kit's own SDR, whose supply EMCON removes).

#### C-S3. From section 4b (its closing paragraph)

*`CONOPS.md` lines 473 to 474 at `31cd29b9`: the commits that drew the two switches.*

The WiFi cards' converter enables are drawn since `458b2873`; the 5G supply
switch, SD-EMC-1's, is drawn since board B's round 8 (SD-EMC-1r8, EMCON.md section 4b).

#### C-S4. From section 4b.1 (what the operator does with it)

*`CONOPS.md` lines 505 to 507 at `31cd29b9`: the transmitter counts against REQ-071.*

**State at this revision:** this is a requirement on the design (REQ-071), and no row meets it end to end at desk yet
(`feasibility/EMCON.md` sections 0a and 5a: locally 15 of the 17 rows close at desk, rows 1 and 4, the SA868 and the RockBLOCK 9704, are open, and every row inherits the shared items of
its section 3, so 0 of 17 close end to end).

#### C-S5. From section 4c (HOT-R1)

*`CONOPS.md` lines 677 to 679 at `31cd29b9`: the hot stop requirement's reading on the generated boards.*

**Until HOT-R1 is in both generators the hot stop's requirement reads FAIL on the generated boards,** a finding
reported to the owner, not asked: the stop then acts only where the bridge links the two controllers (the normal and
reduced modes, and the heat stage after BANK-R1, up to H1 itself), and falls back to the `TMP117` elsewhere.

#### C-S6. From section 4c (BANK-R1)

*`CONOPS.md` lines 738 to 740 at `31cd29b9`: REQ-052's reading on board B as generated.*

**Until BANK-R1 is in board B's generator,
REQ-052 is not met by board B as generated** (its one-module stage lacks the LoRa mesh and APRS): a finding against the
generated board, reported to the owner at the next checkpoint, not asked.

#### C-S7. From section 4c (the recovery and delivery targets)

*`CONOPS.md` lines 869 to 869 at `31cd29b9`: the registry items the targets closed.*

These close S-37 and REQ-003's latency TBD for the kit's part.
