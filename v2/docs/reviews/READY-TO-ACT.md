# Ready to act: the external reviews and the bench work, costed

MESHSAT-1357, round 8. Written on 26 September 2026 from 23:00 CEST, on main `fc144600`
(`fc144600544c005c280d6614d26a94dfd3f88511`, on `origin/main`), and corrected at about 23:50 CEST after an independent
check found three errors (the DIP switch of section 11 S-4 and table 3.3, the R-PWR packet of section 2.3, and the
currency of one price in table 4.3). It executes the review of the 22:35 progress report
(`v2/docs/reviews/2026-09-26-second-checkpoint-review.md`), section 2G ("Complete a costed, ready-to-act packet for the
reviewer engagements and development hardware; then request only the authorization still genuinely missing. Continue
unrelated engineering meanwhile") and item 5 of its section 5 ("A ready-to-act external/bench packet: current design
files, review scope, supplier/reviewer options, costs, lead times and exact authorization needed").

**Prototype framing.** The MeshSat field kit V2 is an unbuilt prototype design. No V2 board has been fabricated,
ordered, assembled or tested, and no bench experiment below has run. Every review so far is by AI agent sessions.

**What this page is not.** Nobody has been contacted, nothing is ordered, contracted or paid, and no account was logged
into. Every request text here or in the files it points to is a draft, **NOT SENT**. Contacting a reviewer or a supplier,
spending money and buying hardware stay with the owner (house rules; owner ruling D-09, `v2/docs/CONOPS.md` section 7;
the standing rule of 26 September 2026 keeps orders, payments and outside contacts off limits to the session). Where
more than one engineering option stood, the session took the recommended one under the owner's standing rule of 26
September 2026 and says so (section 11); none of those choices spends money or contacts anyone.

**How figures are marked.** Every price, stock and lead-time figure is **VERIFIED** (read from the public page named, at
the UTC time given in section 10, in the currency and with the VAT note the page itself shows) or **TBD**. No currency is
converted. A product of VERIFIED figures (a quantity times a price) is labelled arithmetic. Engineering figures quoted
from this repository carry their file and section at `fc144600`. A company named below was found on its own public page
and has not been approached.

## 0. The authorisations still missing, in one list

This is the request the review asks for: only what is genuinely missing. Everything else on this page is prepared.

| # | Item | What is missing, exactly | Kind | Amount known today | Unblocks | Prepared |
|---|---|---|---|---|---|---|
| 1 | R-BAT, battery and pack protection review | the owner sends the prepared request to the three shortlisted firms, then approves one quote | outreach, then spend (approved in principle by D-09, amount by quote) | TBD by quote | FB-BAT; board P's fabrication release and the pack build | the packet passes its release check at `fc144600` (section 2.1); request text in the packet |
| 2 | R-SEC, ZEROIZE and key-fill security review | the owner files SIDN fonds' voucher request form (to `projecten@sidnfonds.nl`); optionally, the owner asks Microchip for the ATECC608B's NDA data sheet | outreach (the fund's page shows no price) | a voucher is "een dagdeel" (half a day) of an expert's advice, VERIFIED [W13] | FB-ZER-1's review half; residuals R1 to R7 | texts T1 and T4 (section 9) |
| 3 | R-PWR, the complex power design | the decision to commission it at all, a spend amount, and the request sent | engagement and spend (not covered by D-09) | TBD by quote | FB-PWR's review half; board A's circuit before its layout is committed | request text in `REVIEW-ROUTES.md`; board A's calculation record `v2/docs/records/r4a/`; provider list section 2.3 |
| 4 | R-HSD, board B's high-speed digital fabric | the decision to commission it, a spend amount, and the request sent | engagement and spend (not covered by D-09) | TBD by quote | FB-FAB's review half; board B's layout commitment | statement of work T2 (section 9) |
| 5 | R-EMC, pre-compliance of the built kit | nothing now; a booking and a quote once a prototype exists | spend at the build (approved in principle by D-09) | TBD | characterisation of MIL-STD-461 rows | provider list section 2.5 |
| 6 | ZEROIZE bench Z-EXP-A to C | the purchase (list section 3.3); who wires the rig; which lab host the session may reach by ssh to run it | purchase and people | VERIFIED in part: USD 11.04 and GBP 3.80 (USD 69.04 with the MikroE socket board); the DM320118 and the instruments TBD (section 3.4) | FB-ZER-1 on the fitted part; board B's U8 site; the proposed REQ-035 pass lines | procedure `v2/docs/feasibility/ZEROIZE.md` section 5 |
| 7 | EMCON development bench (E-01 row 5, E-05, E-12 parts) | the purchase (list section 4.3); the RM520N-GL and SA868 order codes pinned first (parts stream); an operator SIM; the licensed operator of D-04 for the SA868 keying | purchase and people | analyser VERIFIED (EUR 159.46 excl. VAT, or EUR 6,509 for a bench unit); the rest TBD | SD-EMC-1's fallback and its T_off and T_cut values on board B; board D's PTT divider | section 4 |
| 8 | Empty-case heat-balance test | buying the prototype's own case and frame now instead of at the build, plus consumables; who runs it | purchase and people | case EUR 168.90 and frame EUR 29.66 excl. VAT, logger GBP 349, all VERIFIED; plate blank, heaters, fans TBD | FB-PWR's enclosure conductance and the PA patch (PWR-F15) | section 5 |
| 9 | Case mock-up | machining quotes for the made parts once their drawings exist; buying prototype parts early (arrestors, monitor, connector-plate items); who assembles and measures | purchase and people | arrestors 12 x USD 78.99 and monitor USD 569.00 VERIFIED; machining and the connector-plate items TBD | the 35 OPEN case margins; board outlines and connector places of A, B and E before they are costly to change | section 6 |

Items 8 and 9 use one case, in that order (section 11, S-1). The case, its frame, the arrestors, the monitor and the
connector-plate items are parts the prototype needs anyway (`v2/docs/CASE-MARGINS.md` section 7, "each a part the
prototype needs anyway"), so for them the decision is **when** to buy, not **whether**.

## 1. What proceeds without any of this

The review asks that unrelated engineering continue meanwhile. None of the following waits on an item of section 0:
the round 8 circuit corrections on every board (EMCON remedies, failover fabric, address conflicts, board E,
decoupling); regeneration and parity; the evidence re-take; board B's bounded escape experiment; the per-board path
into layout; the golden image of the pack gauge (`v2/docs/review-packets/battery/PRIMARY-CONFIGURATION.md`); the panel
firmware's wipe sequence (MESHSAT-837); the drawings the mock-up needs (section 6.2); and the review packets owed for
boards A, B, D and P at the round 8 merge (section 7).

What does wait, item by item, is stated in each section below as "Waits on it".

## 2. The qualified review routes

The routes, their questions and the request texts are in `v2/docs/reviews/REVIEW-ROUTES.md` (at `fc144600`, last changed
in `ccf5808e`). This section adds, per route: the exact files to send at the current commit, what is still owed before
sending, public provider options, cost and lead time, and the authorisation still missing.

### 2.1 R-BAT: battery pack protection (approved in principle by D-09)

- **Send.** The folder `v2/docs/review-packets/battery/` at `fc144600` (the packet merged in `d90f30e4`; last touched in
  `428c697c`). Start at `REVIEW-REQUEST.md`. Link form once the owner sends it:
  `https://github.com/meshsat/meshsat-fieldkit/tree/fc144600544c005c280d6614d26a94dfd3f88511/v2/docs/review-packets/battery`.
- **Checked by this stream at `fc144600`:** `python3 v2/docs/review-packets/battery/evidence/check_manifest.py` prints
  `checked 132 rows of MANIFEST.md` and `RELEASE CHECK PASS` (run in an isolated worktree of `fc144600`,
  26 September 2026, about 23:15 CEST). The packet's `candidate/pcb-p-pack.net` and `candidate/pcb-p-pack.kicad_sch`
  are byte-identical to main's `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` and `v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch`
  (sha256 `4342c4cb...` and `2dba8588...`), so the circuit the reviewer reads is the committed board P.
- **Send condition (taken by the session, S-2):** both checks above hold at the commit whose link is sent. Round 8 has a
  board P stream; if it changes `gen_sch_p.py`, the battery stream re-issues `candidate/` and `MANIFEST.md` first, or the
  link stays at `fc144600` and says so. It does change it (stream p: R8P-01 to R8P-03, with R8P-05 and R8P-06 as
  packet questions), and so did the battery stream's round 8 (THERMAL-COORDINATION.md, TEST-PLAN.md): both were merged
  at the integration of 27 September 2026, where `candidate/` and `MANIFEST.md` were re-issued with board P's rebuild
  script in board P's commit. The two checks above are run again at the commit whose link is sent, and the link moves
  to it; `fc144600` is no longer the revision to send.
- **Not to send:** `v2/release/review-packets/P-P4-1f614233/` (superseded by `d90f30e4`; it records `1f614233`). Board P's
  committed layout (P4) predates every correction and is not a review input.
- **Owed, not blocking the send:** board P's `review_packet.py` packet at the sending revision (the change table against
  `1f614233`; section 7). The battery packet already carries the schematic PDF, native files, BOM, netlist diffs and
  calculations.
- **Scope.** The twenty-three questions of `REVIEW-REQUEST.md` section 3 (Q-P0 to Q-P99; round 8 added Q-P15 to Q-P18
  from the battery stream and Q-P19 to Q-P21 from board P's stream), the first review's section 2 list
  (protection architecture, secondary temperature decision, fuse interpretation, FET and gate behaviour, commissioning
  jumper, the charger with its controller crashed as a state sequence), and the second review's point B (the 62.7 to
  77.5 C secondary window against the 60 C cell limit). Transport (UN 38.3, ADR) is outside it by the packet's own
  statement.
- **Reviewer options.** The packet's shortlist, read from public pages on 26 September 2026 by the battery stream and
  not contacted (`REVIEW-REQUEST.md` section 5; URLs and snapshot hashes in `MANIFEST.md`, "Route evidence and the
  session's record"): Accutronics Ltd (UK, smart batteries, a 4S SMBus pack in its range), Engineering Spirit B.V.
  (the Netherlands, BMS and UN 38.3 / IEC 62133-2 certification), Jauch Quartz GmbH battery technology (Germany, custom
  packs with BMS). TI's partner directory is the fourth source it names.
- **Cost.** TBD by quote; no candidate publishes a review price.
- **Lead time.** TBD by quote.
- **Proceeds before it:** the golden image, board P's re-placement at 4 layers and 2 oz (decision 28) as a draft,
  everything outside board P.
- **Waits on it:** freezing board P's placement and the pack design (second review, point B), board P's fabrication
  release, the pack build, the extended protection test of `POWER-THERMAL.md` PWR-F12.
- **Authorisation missing:** the owner sends the prepared request (`REVIEW-REQUEST.md`, "Ready-to-send request") to the
  shortlist, then approves one quote. Nothing else.

### 2.2 R-SEC: ZEROIZE and key fill (approved by D-09: the SIDN fonds voucher)

- **Send, ready at `fc144600`:**
  - `v2/docs/feasibility/ZEROIZE.md` (FB-ZER-1; the slot map, the key lifecycle, the wipe and its time budget, the
    bench experiments, the alternative, residuals R1 to R7);
  - `v2/docs/records/rv-zer/` (`zeroize/zer_config.py`, `zeroize/zer_budget.py`, `datasheets/SOURCES.md`,
    `ZEROIZE-integration.md`);
  - `v2/release/review-packets/C-C24-1f614233/` (board C, the toggle's sense and buffer). Board C's generator is
    unchanged since `faf8c981` and its committed netlist is unchanged between `1f614233` and `fc144600` (checked: no
    diff), and `review_packet.py verify` reads the packet OK, so it still describes main's board C;
  - `v2/docs/PANEL.md` section 6 (the hardware lines that work with the controller dead).
- **Owed before sending:** board B's packet (the secure element U8 and the shared kit bus of residual R7 are on board B),
  built by `review_packet.py` at the round 8 merge (section 7). Until it exists the reviewer can read main's committed
  `v2/ecad/pcb-b-compute-b19/pcb-b-compute.kicad_sch` and `out/pcb-b-compute.net` at `fc144600`, but no schematic PDF of the current board B candidate is in the tree (older
  revisions' PDFs under `v2/release/revA/boards/` are superseded).
- **Scope, fitted to the voucher (S-3):** SIDN fonds' voucher buys "een dagdeel advies van een expert uit ons netwerk"
  (half a day), and its expert pool includes technical expertise including privacy and security, VERIFIED [W13]. For
  half a day the session sets the scope to the four questions of `REVIEW-ROUTES.md` R-SEC and residual R7 with its
  attested-verification candidate (`ZEROIZE.md` sections 1, 3, 5 and 8), not the whole packet; the rest is optional
  reading.
- **Reviewer.** The expert SIDN fonds assigns from its network; no name is known or chosen.
- **Cost.** TBD: the fund's page shows no price and no cost to the project [W13]. Any time beyond the half
  day is TBD and needs a quote and the owner's approval (D-09).
- **Lead time.** TBD; the page states none [W13].
- **Also owed, outside the session's reach:** Microchip's full ATECC608B data sheet, released under NDA
  (`v2/vendor/SOURCES.yaml`, `owed` list). The bench experiment Z-EXP-A shows the same properties on the part without
  it (section 3).
- **Proceeds before it:** Z-EXP-A to C (section 3), the panel firmware, every board.
- **Waits on it:** closing residuals R1 to R7 as reviewed rather than stated; nothing on a board.
- **Authorisation missing:** the owner files the voucher form (text T1); optionally requests the NDA data sheet (text
  T4).

### 2.3 R-PWR: the corrected complex power design (needs the owner's decision and spend)

- **Send, ready at `fc144600`:**
  - `v2/release/review-packets/E-E17-1f614233/` (the input stage board A is fed from). Board E's generator is unchanged
    since `faf8c981` and its netlist is unchanged between `1f614233` and `fc144600`, and the packet verifies OK;
  - `v2/docs/feasibility/POWER-THERMAL.md` (PROVISIONAL budget, PWR-F01 to PWR-F15, the proposed experiment) and
    `v2/docs/records/rv-pwr/` (`pwr_budget.py`, `pwr-chain-redeclaration.yaml`);
  - `v2/docs/feasibility/DECOUPLING.md` (decision 42, for question 7);
  - `v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md` (for question 2);
  - **board A's calculation record**, `v2/docs/records/r4a/r4-decisions.md` and `v2/docs/records/r4a/r4-open-items.md`
    (on main since `428c697c`, unchanged at `fc144600`; sha256 `2e5a0c20...` and `0c58f8a3...` as
    `v2/docs/records/README.md` lists them). For each of the seven LM5176 stages (FE, S2, SD, PA, HF, PoE, PD) it gives
    the stage's own compensation (Rc1, Cc1, Cc2 with their LCSC codes), phase and gain margin, the minimum of
    abs(1+T), the crossover band and the closed-loop output impedance against the stage's bound, and the worst per-part
    ripple current of its bulk against the part's rating (section 4, B2, the table as amended by sections 5 and 6). It
    also holds the front end's bulk ripple over its whole bands (B3, sections 5 and 6), the front end's soft start
    against board E's LM5069 limit of 4.85 to 6.15 A (B4), the restart guard for a restart into a charged VBUS20
    (section 7, R4A-N15), power-up (S-08), and the open items O-01 to O-37, among them the bench readings owed (O-19,
    O-37). The record's final state is the board A generator main has carried since `458b2873` (sha256 `a0452054...`;
    the records README's row for the `fixup4-run3` netlist reads "main's since `458b2873`"); at `fc144600` that generator differs from it only by the one-way
    clamp symbols of `3a1f6576` (D1 to D4 drawn by `kisch.tvs()`, with nets, values, lands and codes unchanged, read
    in the diff), so the record describes main's board A circuit. REVIEW-ROUTES.md, written at `ccf5808e` before
    `428c697c` filed this record, still lists these calculations as owed; a correction is drafted for its writer
    (section 12).
- **Owed before sending:** board A's packet and board B's packet (for the TPS23861 PoE PSE and its port), both built by
  `review_packet.py` at the round 8 merge, since round 8 has a board A stream (section 7). The scripts and run outputs
  behind the record's figures, which are **not in the tree**: `drafts/scripts/loop_design.py`, `bulk_ripple.py`,
  `ripple_dense.py`, `softstart.py`, `restart.py` and `comp9_corners.py`, the runs `drafts/box/loop/`,
  `drafts/box/loop2/` and `drafts/box/ripple/`, and the record's companions `r4-hwfw-contract.md` (the bench list
  FW-A15), `r4-interfaces.md` and `r4-netlist-diff.md`. They are held in the round 4 board A author's working folder
  (`fnd/r4a` `drafts/`, never pushed); the records README's closing paragraph names `loop_design.py` among the scripts
  not filed, because the tools and board streams that own the comments citing them would have to re-point those
  comments in the same change. Without them a reviewer can check each figure by hand from the datasheet equations the
  record names (SNVSAI1D, SLUSE66A) but cannot re-run the searches; filing them is the records writer's, with those
  owners. Also owed: `SOURCES.yaml` entries for board A's other regulators (`REVIEW-ROUTES.md`, R-PWR "Owed"). Board
  A's committed `.kicad_pcb` predates the corrected netlist and is not a review input.
- **Scope.** The eight questions of `REVIEW-ROUTES.md` R-PWR; PWR-F12 (the pack chain at 18 A for 60 s) and PWR-F02 on
  board A's side.
- **Provider options (public pages, not contacted):**
  - **Elteknik P.C.**, Thessaloniki, Greece, https://elteknik.gr/ : "Specialist Power Electronics Engineering
    Consultancy", "DC/DC and AC/DC converter design, EMC compliance", "Serving clients across Europe", a "Technical
    Consulting" service, one senior engineer ("We do not subcontract") [W9]. What to ask first: a review-only engagement
    and four-switch buck-boost (LM5176 class) and NVDC charger experience.
  - **VDL Sintecs**, Sintecs B.V., Hengelo (O), the Netherlands [W8]: its power integrity service covers "number and
    location of decoupling capacitors", DC drop and current density [W7]. A fit for questions 6 and 7 (VBAT copper,
    decoupling), not for converter compensation.
  - **How2Power's Consultants Corner**, https://www.how2power.com/consultants/ : a public directory of power-supply
    consultants, several in Europe, one of whose listings reads "Analysis and design review services are also
    available" [W10]. A source for further names, which the owner may use.
  - **TI's partner directory**, https://www.ti.com/design-development/partner-directory.html (named in the battery
    packet): design-service partners filtered by product domain.
  - The R-BAT candidate, where one covers both (the charger sits in both scopes; `REVIEW-ROUTES.md`).
- **Cost.** TBD by quote; none of the pages publishes a price.
- **Lead time.** TBD by quote.
- **Proceeds before it:** board A's round 8 corrections, its regeneration and parity, placement studies.
- **Waits on it:** `REVIEW-ROUTES.md` times it before board A enters layout, and `ARCHITECTURE.md` section 14.2 lists it
  among board A's holds. Because the spend is not approved, that timing is a dependency on an owner decision; how it is
  staged (layout entry against fabrication release) belongs to the review's item 2 (no circular gates), which its own
  stream handles. This page does not change it.
- **Authorisation missing:** the decision to commission R-PWR; a spend ceiling or an approved quote; the request sent
  (`REVIEW-ROUTES.md`, R-PWR request text, with the attachments above).

### 2.4 R-HSD: board B's high-speed digital fabric (needs the owner's decision and spend)

- **Send, ready at `fc144600`:** `v2/docs/ARCH-PCB-B-IOHA.md` (sections 9, 12, 13, 15 and 15a),
  `v2/ecad/tools/pcb_interfaces.yaml`, `v2/docs/feasibility/FAILOVER-FABRIC.md` (the lane, pin and clock map; FB-FAB-1 to
  FB-FAB-8), `v2/docs/B-FEASIBILITY.md` (the escape diagnosis and trial specification), the stackup record
  `v2/vendor/fabricator/jlcpcb-stackups-2026-09-25.md`, and `v2/docs/feasibility/DECOUPLING.md`.
- **Owed before sending:** board B's packet at the round 8 merge (section 7; the current board B candidate has no schematic PDF in the tree); the
  concluded board B escape experiment with its stated limits (the second review's item 4); FB-FAB-2 to FB-FAB-5's netlist
  changes where round 8 makes them.
- **Scope.** The six questions of `REVIEW-ROUTES.md` R-HSD. As a statement of work for a pre-layout signal-integrity
  review: text T2 (section 9), written to the inputs a provider below publishes.
- **Provider options (public pages, not contacted):**
  - **VDL Sintecs**, Sintecs B.V., Hengelo (O), the Netherlands, published channel `info@sintecs.nl` and a sales form
    [W8]. Its signal-integrity page: "Even when working with standard technologies like DDR, USB, and PCI-E high speeds
    and timing issues are becoming more common", "from a full-wave solver or a power-aware crosstalk analysis", and, for
    "pre-layout SI Analysis", it expects "Clear statement of work for pre layout Signal Integrity Analysis", "Schematic
    (PDF)" and "Preliminary Layout Information (PLI) if available" [W6]. It also offers power integrity analysis [W7].
  - **The fabricator's impedance engineering**, for the stackup question (question 5) alone: JLCPCB publishes a
    controlled-impedance calculator, https://jlcpcb.com/pcb-impedance-calculator [W28]; the eight-layer stack of decision
    43 is recorded in the stackup file above.
  - Provider types from `REVIEW-ROUTES.md` (independent SI consultants, design bureaus with SI tools, a university
    group).
- **Cost.** TBD by quote.
- **Lead time.** TBD by quote.
- **Proceeds before it:** the escape experiment, FB-FAB-2 to FB-FAB-5's netlist corrections, board B's regeneration.
- **Waits on it:** `REVIEW-ROUTES.md` times it before a board B layout is committed; the same staging note as R-PWR
  applies.
- **Authorisation missing:** the decision to commission R-HSD; a spend ceiling or an approved quote; the request sent
  (`REVIEW-ROUTES.md` R-HSD request text with T2 attached).

### 2.5 R-EMC: pre-compliance of the built kit (approved by D-09 once a prototype exists)

- **Send:** nothing now. At the build: the prototype, `v2/docs/TEST-PLAN.md` (section 3, the MIL-STD-461 rows as
  characterisation under D-04), `v2/docs/GROUNDING-AND-SHIELDS.md`, the board packets at the built revision, and
  `v2/docs/feasibility/EMCON.md` section 6.
- **Provider options (public pages, not contacted):**
  - **Kiwa Dare (DARE!!)**, https://www.dare.eu/emc : measurements under the Radio Equipment Directive and others, "also
    performed in accordance to Military and FCC regulations", and "the so called Quick Scans or engineering measurements
    (pre-compliant) can be performed" [W12].
  - **SGS Netherlands**, Spijkenisse, https://www.sgs.com/en-nl/services/electromagnetic-compatibility-emc-testing :
    "Our experts can support early with pre-compliance reviews", "end-to-end services from pre-compliance evaluation to
    certification" [W11].
- **Cost and lead time.** TBD; neither page states a price or a booking time.
- **Authorisation missing:** none now; a booking and an approved quote at the build.

### 2.6 A funding route the owner may consider

SIDN fonds' pioneers grant is "up to EUR 10,000" for a project "into a demo, pilot or experimental design", applied for
at any time, with an answer "Binnen 6 weken" (within six weeks), VERIFIED [W14] [W15]. In 2026 it funds only projects that
contribute to "Sterk internet", "rechtstreeks relevant voor de Nederlandse internetinfrastructuur" [W15]. Whether R-PWR,
R-HSD or R-EMC fit that focus is the owner's judgement; the session reads the fit as doubtful (INFERRED) and drafts no
application.

## 3. ZEROIZE bench: Z-EXP-A, Z-EXP-B and Z-EXP-C

### 3.1 What, and what it decides

Procedures: `v2/docs/feasibility/ZEROIZE.md` section 5 at `fc144600`, with the image and budget scripts
`v2/docs/records/rv-zer/zeroize/zer_config.py` and `zer_budget.py`. Z-EXP-A shows the mechanism on the fitted
ATECC608B-SSHDA-T in the configuration of `ZEROIZE.md` section 3.1 (about 2 h). Z-EXP-B cuts power during GenKey
1,000 times on each of two parts (a few hours to build, about 10 minutes of run per part) and first times GenKey (step
B0). Z-EXP-C runs the panel's own wipe sequence with power cuts and the held-bus cases C-H1 to C-H3 (needs the panel
firmware, MESHSAT-837).

They decide FB-ZER-1's four OPEN rows (`ZEROIZE.md` section 7: the mechanism on the fitted part, Z-EXP-A; interrupted power, Z-EXP-B; panel resume and slot gating, Z-EXP-C; and the factory address 0x60, Z-EXP-A step A0), and with them whether board B's U8 site keeps the ATECC608B or switches
to the SLB 9673 TPM (switch conditions S1, S2), and whether the proposed REQ-035 pass lines (1.5 s, 3.0 s) hold on the
part. None is a test of the built kit.

- **Proceeds before it:** everything except board B's U8 site layout; the switch changes that one site only
  (`ZEROIZE.md` section 6).
- **Waits on it:** board B's layout entry for the U8 site (A and B); the panel firmware's wipe acceptance (C).

### 3.2 Hands and host

The session cannot touch hardware. Someone receives the parts and wires the rig per section 5 (the owner, or an
assembler he names), and connects it by USB to a Linux lab host the session may reach by ssh; the session then runs the
scripts and files the pass records under `v2/docs/feasibility/evidence/` (the closing evidence `ZEROIZE.md` section 7
names). Who, and which host, is part of item 6 of section 0.

### 3.3 Hardware list

| Item | Exact part | Qty | Supplier page | Price | Stock or lead |
|---|---|---|---|---|---|
| Secure element samples, the fitted order code | Microchip ATECC608B-SSHDA-T (LCSC C1518769) | 10 | JLCPCB parts library (`v2/docs/records/rv-zer/prices/jlc-ATECC608B-SSHDA-T.json`) | USD 0.9955 each at 1 to 9, USD 0.8088 at 10 to 29, VERIFIED [W29]; 10 at USD 8.09 (arithmetic). A loose purchase from LCSC or a distributor: TBD | 2,344 in stock at the reading [W29] |
| Host board for Z-EXP-A | Microchip DM320118 CryptoAuth Trust Platform; its own DIP switch SW2 selects the mikroBUS header or the on-board devices, and `ZEROIZE.md` section 5 sets it to mikroBUS only (SW2_1 ON, SW2_2 OFF) [W30] | 1 | Microchip and its distributors (every distributor page refused the runner on 26 September 2026) | TBD | TBD |
| Socket board for Z-EXP-A | MikroElektronika Secure SOIC Click, MIKROE-3788 | 1 | https://www.mikroe.com/secure-soic-click | USD 58.00, VERIFIED only as archived [W2] | **"This product is no longer in stock"** in the archived page of 18 November 2025 [W2]; current stock TBD (the live page refused the runner) |
| Fallback for the socket board only (S-4); the DM320118's SW2 setting stays as above | Adafruit 1212, SMT breakout PCB for SOIC-8, 6 pack; one sample per breakout, wired to the mikroBUS header one at a time | 1 pack | https://www.adafruit.com/product/1212 | USD 2.95 per pack, VERIFIED [W22] | "In stock" [W22] |
| Rig controller for Z-EXP-B and C | Raspberry Pi Pico, SC0915 (RP2040, the panel controller's own MCU) | 1 (2 with a spare) | https://thepihut.com/products/raspberry-pi-pico | GBP 3.80 incl. VAT, VERIFIED [W3] | "In stock" [W3] |
| SE supply switch | a high-side load switch the Pico drives, with an output that falls below 0.2 V within the off-time `ZEROIZE.md` section 5 sets | 1 | TBD | TBD | TBD |
| Scope, for the one-off off-time check (B) | any oscilloscope of at least two channels | 1 | the owner's own if one exists (none is recorded in this tree) | TBD | TBD |
| Logic analyser, for C-H1 to C-H3 (C) | any logic analyser of at least four channels | 1 | as above | TBD | TBD |
| Decoupling at the part, jumpers | 100 nF capacitor per part as `C69` on board B; jumper wires | as needed | any | TBD | TBD |

The prepared list in `ZEROIZE.md` section 5 ("one DM320118, one MikroElektronika Secure SOIC click, ten
ATECC608B-SSHDA-T, one Raspberry Pi Pico, one load-switch breakout, jumpers") is the same list; this table adds its
supplier pages, prices and the socket board's stock finding. The DIP switch belongs to the DM320118, not to the socket
board: "The switch is used to select between the on-board ATECC608A Trust Platform devices and the mikroBUS header. The
switches disconnect the SDA lines of the I2C interface to prevent conflict in case two I2C addresses are the same"
(DS50002921A p. 5; "Dual SPST DIP Switch", item 6 of the board overview on p. 3), and the on-board ATECC608A-MAHDA's
default 7-bit address is 0x60 (p. 4), the address `ZEROIZE.md` A0 expects of every sample (byte 16 = 0xC0) [W30]. So
SW2_1 ON, SW2_2 OFF holds whichever carrier the samples sit on.

### 3.4 Cost

VERIFIED parts: USD 8.09 (10 secure elements at the library price break) + USD 2.95 (breakouts) + GBP 3.80 (Pico);
USD 58.00 more if the MikroE board is still obtainable. TBD: the DM320118, the load switch, the instruments if the owner
has none. **Lead time:** TBD for every line except the three read "In stock" or "no longer in stock" above.

### 3.5 Authorisation missing

The purchase of this list (D-09: "nothing is spent beyond the voucher without a quote and the owner's approval",
`ZEROIZE.md` section 5); who wires the rig; which host the session may run it from.

## 4. EMCON bench: E-01 to E-12

### 4.1 What can run before any board exists, and what it decides

`v2/docs/feasibility/EMCON.md` section 6 defines twelve rows, every one with an external receiver because EMCON removes
the kit SDR's supply. The review allows a development-board test to gate a risky architecture decision, and forbids a
test on the final PCB from blocking the design of that PCB (second review, point A). Read that way (S-5):

| Row | Radio | Before any board, on development hardware | Needs the built kit | What the early part decides |
|---|---|---|---|---|
| E-01 | SA868 | row 5 of `v2/docs/records/r6d/r6-decisions.md` section 5: pin 5's "1" threshold and its input current, on a bare module into a dummy load | rows 1 to 4 (U1 fitted, unfitted, shorted; U16 forced) | board D's PTT divider: "If E-01 finds the threshold above 2.677 V, the divider is re-ratioed" (`EMCON.md` 4.1) |
| E-02 | 30 W PA and the common element | no | all | nothing early |
| E-03 | QMX | possible on the bare unit (12 V absent, USB host attached, VBUS current) | the kit's `+12V_HF` and `VBUS_QMX` | whether board A's `VBUS_QMX` feed needs switching; low value, optional |
| E-04 | RockBLOCK 9704 | no (back-feed through board B's drivers) | all | nothing early |
| E-05 | RM520N-GL, W_DISABLE1# | **all of (a) to (d) and (f), and (g) per firmware**, on an M.2 evaluation board with the pin driven directly; (e) over USB; (e) over PCIe only if the evaluation board gives a PCIe host (TBD) | none: E-05 measures the pin alone by its own text; repeated on the kit's module if its firmware differs | SD-EMC-1's fallback (iii): whether the fitted firmware misses a pin that falls while it boots; the provisioning values of `AT+QCFG` |
| E-06 | LimeSDR | no | all | nothing early |
| E-07 | AW7915-AED x 2 | no (board B's card rails) | all | nothing early |
| E-08 | CM5 WiFi and BT x 6 | no (the pins are on board B's receptacles) | all | nothing early |
| E-09 | E22-900M30S | no | all | nothing early |
| E-10 | E72 x 2 | no | all | nothing early |
| E-11 | the lines | no | all | nothing early |
| E-12 | RM520N-GL, FULL_CARD_POWER_OFF# and supply | **(a), (b), (c)**, **(e)** on the pin sequence, **(f)**'s Tpr, and in **(i)** the boot time per cause for turn-on, warm reset, hard reset and AT+CFUN=1,1, the probes for a socket pin that marks a firmware restart, and PERST# pulsed alone | (d) as built, (g), (h), and (i)'s causes through `PCIE_PWR_EN2`, slot 2's CM5 and an EMCON release | T_off (from (c)) and a bound on T_cut (from (a) and (b)); T_boot for the fallback; whether a socket pin marks a restart board B cannot see today (which would close a residual of SD-EMC-1) |

Why early: E-05 and E-12's early parts set component values and one topology choice on board B (SD-EMC-1's stages and
fallback), and E-01's sets a divider on board D. Board B's layout entry is held by larger items anyway
(`ARCHITECTURE.md` section 14.2), so this bench runs in parallel with them. The pass lines, the resolution bandwidth and
the cycle count stay the TEST-PLAN owner's (`EMCON.md` section 8, TEST-PLAN writer).

**Order within E-12 (S-6):** Quectel warns that removing the supply out of order can corrupt the module's flash
(`EMCON.md` section 0). E-12 (e)'s withheld cycles run last, so the one bench module serves every other row first.

### 4.2 Before buying: two order codes and one check

- The RM520N-GL's regional or firmware order code is not pinned ("no regional or firmware order code is named for the
  RM520N-GL", `v2/vendor/SOURCES.yaml`, the key-B socket entry; the `owed` list: "the SA868 and RM520N-GL order codes").
  A bench module of another order code tests another firmware configuration, which E-05 (g) and owner condition 1 both
  treat as a different part. `SOURCES.yaml` lists both codes as owed with the note "owner-side purchases"; which code
  carries the bands and firmware the kit needs is an engineering pick the session's parts work makes before the
  purchase, and buying it is the owner's.
- The SA868's order code is not pinned either (same `owed` line; `v2/release/review-packets/README.md`: "board D's U2
  (SA868, order code not pinned)"). Its VHF variant is the one board D needs.
- The Quectel 5G-M2 evaluation kit (5GM2EVB-KIT) lists the RM520N series among its applicable modules and names
  "Switches and button" and "Test points" among its features [W5]. Whether W_DISABLE1#, FULL_CARD_POWER_OFF#, RESET#,
  PERST# and the module's VCC can each be driven or cut from outside is in its user guide, which this tree does not hold:
  TBD, asked in text T3 before buying.

### 4.3 Hardware list for the early rows

| Item | Exact part | Qty | Supplier page | Price | Stock or lead |
|---|---|---|---|---|---|
| 5G module | Quectel RM520N-GL, order code as pinned (4.2) | 1 | Quectel or an EU distributor; one public bundle below | TBD | TBD |
| M.2 evaluation board | Quectel 5G-M2 EVB kit, 5GM2EVB-KIT | 1 | https://www.quectel.com/product/5g-m2-evb-kit/ [W5] (no price on the page) | TBD | TBD |
| For comparison only | "Quectel x62 RM520N-GL 5G Modem with USB3 to M.2 Key B 4G 5G Modem Adapter Enclosure with SIM Card Slot - V7" (SKU USB3M2ADENC4G5G-V7-RM520NGL), a module in a USB enclosure | not recommended | https://store.thewirelesshaven.com/products/usb3-m-2-4g-5g-modem-adapter-enclosure-with-rm520n-gl-modem | USD 325.00 in the store's product JSON (its base currency); EUR 289.95 as the page was served to a Netherlands visitor (selector "Netherlands, EUR"); both VERIFIED [W4] [W4b]; VAT not stated (the page reads "Shipping calculated at checkout"). The served currency follows the store's reading of the visitor's country: a later fetch from this host was served "US" and USD 325.00 [W4b]. Its module order code and pin access are not stated | the store states it "will be closed from October 1st to October 15th 2026" [W4] |
| SIM and antennas | a data SIM of an EU operator with 5G coverage at the lab; sub-6 GHz antennas for ANT0 to ANT3 | 1 SIM, 4 antennas | the operator; the kit's own antenna pick (open) | TBD | TBD |
| VHF module | NiceRF SA868, VHF variant, order code as pinned | 1 | NiceRF (its page refused the runner) | TBD | TBD |
| Spectrum analyser, development tier (S-7) | tinySA Ultra+ ZS-407: "Ultra mode enabled up to 7.3 GHz, level calibrated up to 7.3GHz" [W19]; Eleshop product number ELE007983, a seller the tinySA project lists for Europe [W20] | 1 | https://eleshop.eu/tinysa-ultra-zs-407-spectrum-analyser.html | EUR 159.46 excl. VAT, VERIFIED [W21] | stock not read ("Loading stock info") [W21] |
| Spectrum analyser, bench tier (alternative) | Siglent SSA3075X Plus, 9 kHz to 7.5 GHz | 1 | https://www.siglenteu.com/spectrum-analyzers/ssa3000x-plus/ | EUR 6,509, VERIFIED [W18] (VAT treatment not stated in the text read); an EMI option SSA3000XP-EMI is listed [W18] | TBD |
| RF parts | a 50 ohm dummy load of at least 5 W for the SA868; fixed attenuators to keep the analyser's input in range; a directional coupler or splitter (600 MHz to 6 GHz) so the 5G module registers through its antenna while its uplink is measured | 1 each | TBD by the TEST-PLAN owner's method | TBD | TBD |
| Scope | at least four channels (VCC, W_DISABLE1#, FULL_CARD_POWER_OFF#, RESET#) | 1 | the owner's own if one exists | TBD | TBD |
| Supplies | a bench supply; an adjustable source for the SA868's pin 5 | 1 each | the owner's own if they exist | TBD | TBD |
| Optional, E-03 | QRP Labs QMX, the lid unit the kit fits | 1 | a kit part bought for the prototype anyway | TBD | TBD |

Who operates: the SA868 keys only into the dummy load, by the licensed operator of owner ruling D-04; the 5G module
transmits on a public network only under its own approval, with the operator's SIM. The session runs the scripts on a
lab host (as in 3.2).

### 4.4 Cost, lead time, authorisation

VERIFIED: the analyser (EUR 159.46 excl. VAT, or EUR 6,509 for the bench tier). Everything else TBD, the module and
the evaluation board by quote (text T3). **Authorisation missing:** the purchase, once the parts work has pinned the two
order codes; a SIM; the licensed operator's time; who wires the evaluation board; the lab host.

## 5. Empty-case heat-balance test (`POWER-THERMAL.md` section 10)

### 5.1 What, and what it decides

Set-up as specified at `fc144600`: "a current-moulding Peli 1450 with a 3 mm aluminium face plate blank and the 1450PF
frame, 20, 40 and 60 W of resistive heat spread on a dummy stack, the fans running (and not), and thermocouples on
air, plate, walls and a dummy pack block"; and on the same plate "a 45 to 83 W resistive block bolted with thermal
compound where the PA's flange sits, run for 20, 30 and 60 s from a warm plate, with thermocouples under it and at 50
and 100 mm". It measures the conductance for lid open and closed, fans on and off, and the patch rise under the PA.

It closes what `POWER-THERMAL.md` calls "W4 T9" (a workstream item there, not source W4 of section 10) and the 2.3 x spread that decides the hot end, appendix 32.56's patch figure, and the numbers PWR-F15's
flange thresholds and repeat rate need (`POWER-THERMAL.md` section 10), "weeks before a populated build". The second
review asks for it before freezing affected placement and pack design (point B).

- **Proceeds before it:** every circuit and layout draft; the thermal limits stay PROVISIONAL meanwhile.
- **Waits on it:** freezing the placement of the pack and the PA's flange site; the +35 C and +25 C controls leaving
  "proposed"; PWR-F15's thresholds.

### 5.2 Hardware list

| Item | Exact part | Qty | Supplier page | Price | Stock or lead |
|---|---|---|---|---|---|
| Case, current moulding (D-08a; `CASE-MARGINS.md` T1 identity check on receipt) | Peli 1450 Protector case, the listing "Peli Protector 1450" | 1 | https://flight-cases.eu/peli-1450.html (Guardique Products A/S, Denmark) | EUR 168.90 excl. VAT, EUR 211.13 incl. VAT, VERIFIED [W1] (the page's two figures; their ratio is Denmark's 25 %) | "Normal in stock"; "60 days free Returns" [W1] |
| Panel frame | Peli 1450PF Special Application Panel Frame Kit | 1 | same page's listing [W1] | EUR 29.66 excl. VAT, EUR 37.08 incl. VAT, special price (regular EUR 32.96 / 41.20), VERIFIED [W1] | stock not shown in the listing |
| Face plate blank | 3 mm aluminium, the outline of `CASE-MARGINS.md` C1 (377.2 x 263.0, R16 corners, ten 4.6 mm holes at Peli's insert bores); a blank without the monitor window unless the power stream says otherwise | 1 | a sheet-metal service, for example JLCCNC (aluminium 5052 listed for sheet metal, "Lead time from 2 days") [W27] | TBD by quote; its drawing is owed first (section 6.2) | "from 2 days" (sheet metal), VERIFIED [W27] |
| Stack heaters | aluminium-housed wirewound resistors, 50 W class; three of 6.8 ohm at 12.0 V give 21.2 W each, so one, two or three give about 21, 42 and 64 W (arithmetic) | 3 | TBD | TBD | TBD |
| PA patch block | one aluminium-housed or flange resistor, 100 W class, 2.2 ohm: 45 W at 9.95 V (4.5 A) and 83 W at 13.5 V (6.1 A) (arithmetic) | 1 | TBD | TBD | TBD |
| Mixer fans | Same Sky CFM-6025BG68, 12 V, the -22 variant (tachometer and PWM) recommended in `v2/vendor/open-picks.txt`; its speed code is still a pick (Same Sky lists, for example, CFM-6025BG68-170-434-22 at 540 mA and CFM-6025BG68-1100-535-22 at 1060 mA [W26]) | 2 | https://www.sameskydevices.com/ [W26] | TBD | TBD |
| Cooler fans | the three 40 mm cooler fans are an open pick (D-18, `open-picks.txt` ip68-fans); stand-ins of the same class | 3 | TBD | TBD | TBD |
| Temperature logger | Pico Technology PicoLog TC-08, SKU PP222, 8 thermocouple inputs | 1 | https://www.picotech.com/data-logger/tc-08/thermocouple-data-logger | GBP 349, VERIFIED [W17] (VAT treatment not stated in the text read) | "Currently In Stock" [W17] |
| Thermocouples | type K, fine wire; eight channels per run (air 2, plate 2, walls 2, pack block 1, outside air 1), reused for the patch run | 10 | TBD | TBD | TBD |
| Supply | a bench supply of at least 15 V and 7 A (the patch block's 6.1 A) | 1 | the owner's own if one exists | TBD | TBD |
| Dummy stack and pack block, thermal compound | plywood or aluminium blanks at the stack's outline; an aluminium block at the 4S3P pack's outline | 1 set | TBD | TBD | TBD |

### 5.3 Cost, lead time, authorisation

VERIFIED: EUR 198.56 excl. VAT for the case and frame (arithmetic: 168.90 + 29.66), prototype parts bought early; GBP
349 for the logger. TBD: the plate blank, the heaters, the fans, the thermocouples, the supply. **Lead time:** case in
stock at the seller; plate "from 2 days" at JLCCNC before shipping; the rest TBD. **Authorisation missing:** buying the
case and frame now; the consumables; who runs the test and where (the session cannot); the logger's data reaches the
session by a file the runner can read.

## 6. Case mock-up (`CASE-MARGINS.md` sections 5 and 7)

### 6.1 What, and what it decides

A targeted, unpowered mock-up on the new case of the current moulding, running checks T1 to T11. It closes the OPEN
margins that rest on Peli's unstated tolerances, the frame's seat, the jumper route and the arrestor's O-ring (35 of the
70 computed rows are OPEN, none NOT MET; `CASE-MARGINS.md`, its opening summary and finding 23 of section 0).
`CASE-MARGINS.md` section 7 recommends it for the build stage; the second review asks for it "before affected PCB
outlines and connector placements become expensive to change, rather than waiting until boards are ready for
population" (its section 3). This page takes the review's
timing (S-8): before the outlines and connector places of boards A (the RF jacks and the connector bay), B (the tall
parts and the heatsink over which M1 is measured) and E (the float clamps the jumpers reach) are frozen. Layout entry
does not wait on it: the mock-up needs a purchase the owner has not authorised, and the review's item 2 asks that no
layout-entry gate depend on such a step.

- **Proceeds before it:** circuit work on every board; the made parts' drawings; the picks listed below.
- **Waits on it:** the OPEN rows' verdicts; the connector plate and entry plates being drilled for the prototype; the
  outlines and connector places of A, B and E being committed.

### 6.2 Owed before it can be quoted

- **Drawings of the made parts.** The released face-plate drawing (`v2/release/revA/case/face-plate/`, from
  `1f46cf83`, 7 September 2026) and its generators (`v2/cad/face_plate.py`, `v2/ecad/tools/panel1450.py`) predate C1
  (377.2 x 263.0 x 3.0, 4.6 mm holes, the rebate, the relief pocket, face top 106.52). The four setting legs with their
  locator and wedges (C6), the connector plate 114.0 x 68.3 x 5.0 (C3), the two 6.0 mm RF entry plates with twelve holes
  spot-faced 26.0 x 1.5 (C4) and the lid tray (C5) have no drawing in the tree. Owner: the case writer, as a design task
  that needs no money.
- **Picks that decide rows** (`CASE-MARGINS.md` section 6): the jumpers' right-angle SMA plug for RG-316 (M17g, M17x);
  the sealed RJ45 in the MIL-DTL-38999 shell 15 class rated for the 54 V PoE feed (the recommended Bulgin PX0833 fails
  both on its own sheet); the sealed USB-C's 45 W PD rating (Bulgin PXP4043/C); the ground stud; the M8 receptacle's
  sheet; the arrestor's O-ring height (PolyPhaser). Owner: the session's parts work, by lookup.

### 6.3 Hardware list

Made parts (after 6.2), quoted from their drawings:

| Item | Source of its numbers | Qty | Supplier options | Price | Lead |
|---|---|---|---|---|---|
| Face plate, 3 mm aluminium | C1; the Xenarc window 205.75 x 140.09 R15 (`ASSEMBLY.md` table, line 41) | 1 (the heat test's blank is a separate, simpler part) | JLCCNC CNC machining: aluminium 6061 and 7075 listed, "Lead time from 3 business days" [W27]; or a local workshop | TBD by quote | from 3 business days at JLCCNC, VERIFIED [W27] |
| Setting legs, locator and wedge set | C6 | 4 legs, 1 set | CNC or 3D printing | TBD | TBD |
| Connector plate | C3 | 1 | CNC | TBD | TBD |
| RF entry plates | C4 | 2 | CNC | TBD | TBD |
| Lid tray | C5 | 1 | CNC or sheet metal | TBD | TBD |

Bought parts, each one the prototype needs anyway:

| Item | Exact part | Qty | Supplier page | Price | Stock or lead |
|---|---|---|---|---|---|
| Case and frame | as in section 5.2 (the same case, S-1) | 1 | [W1] | as in 5.2 | as in 5.2 |
| Antenna bulkhead arrestors | PolyPhaser GTH-SFF-AL, SMA female to female, DC to 6 GHz, 150 W, 10 kA | 12 (D-07's three 5G jacks make twelve bulkheads, `CASE-MARGINS.md` C2) | https://www.polyphaser.com/sma-surge-protector-6ghz-gas-discharge-tube-gth-sff-al | USD 78.99 each at 1+, "All Prices are in US Dollars and do not include duties", VERIFIED [W23]; 12 at USD 947.88 (arithmetic). A US retailer lists USD 73.45 "(Inc. Tax)" [W24] | "QTY available: Call us" [W23] |
| Jumper plugs and cable | right-angle SMA male crimp plug for RG-316 (pick owed, 6.2); RG-316 | 12 plugs; at most 5.2 m of cable (twelve jumpers cut 252 to 432 mm, `CASE-MARGINS.md` section 6) | TBD | TBD | TBD |
| DC receptacle and plug | D38999/20FC4PN wall-mount receptacle (shell 13, insert 13-4, `v2/docs/respin-research-plugs-2026-09-04.md`); Glenair D38999/26FC4SN plug (`ASSEMBLY.md` external cables) | 1 each | Glenair or a distributor | TBD | TBD |
| USB feed-through and plug | Glenair 233-370 M 00-15 2AANH (shell 15; `v2/docs/respin-research-plugs-2026-09-04.md`, sheet `v2/vendor/d38999/glenair-233-370.pdf`); Glenair 233-340 plug with 770-028 boot | 1 each | Glenair | TBD | TBD |
| Sealed RJ45 | pick owed (6.2) | 1 | TBD | TBD | TBD |
| Sealed USB-C | Bulgin PXP4043/C (recommended; 45 W rating owed) | 1 | Bulgin or a distributor | TBD | TBD |
| M8 pod receptacle | binder 86 6618 1121 00004 (recommended; sheet not held) | 1 | binder or a distributor | TBD | TBD |
| Ground stud | M6 class, pick owed | 1 | TBD | TBD | TBD |
| Monitor | Xenarc 709GNK, 7 in, IP67 | 1 | https://www.xenarcdirect.com/ (search result for 709GNK) | USD 569.00, VERIFIED [W16] | TBD |
| CM5 heatsink, for M1 | Raspberry Pi Compute Module 5 Passive Cooler, SC1752; whether it is the "CM5 Cooler" `ASSEMBLY.md` names (with a fan lead in `J_FAN1..3`) is TBD | 1 | https://thepihut.com/products/raspberry-pi-compute-module-5-passive-cooler | GBP 4.80 incl. VAT, VERIFIED [W25] | "In stock" [W25] |
| Stand-ins | blanks at the outlines and stack heights of A22, B16 and E6 on their spacers; blocks at B16's tall parts (RockBLOCK, LimeSDR, heatsinks, U51); the 4S3P pack block (shared with the heat test) | 1 set | TBD | TBD | TBD |
| Tools for T2 to T11 | height gauge, feeler gauges, chalk, a torque driver | 1 set | the owner's own if they exist | TBD | TBD |

### 6.4 Cost, lead time, authorisation

VERIFIED: USD 947.88 excl. duties for the arrestors and USD 569.00 for the monitor (prototype parts bought early);
GBP 4.80 for the heatsink. TBD: every made part (by quote, once drawn), the connector-plate items, the jumpers and the
stand-ins. **Authorisation missing:** approving the machining quotes once the drawings exist; buying the prototype's
bought parts early; who assembles and measures (the session cannot; the owner withdrew the earlier request that he
measure his old case, D-08 reversed, and nothing here asks him to).

## 7. Review packets owed at the round 8 merge

The review asks that a packet be issued for each actual review candidate and obsolete versions be labelled
(its section 3). State at `fc144600`, from `v2/release/review-packets/` (every folder there reads OK under
`review_packet.py verify`, run by this stream at `fc144600`):

| Board | Packet at `fc144600` | Still the committed circuit? | Needed by | Owed |
|---|---|---|---|---|
| A | none | no packet | R-PWR | built at the round 8 merge, compared with `1f614233` |
| B | none | no packet | R-SEC (U8, the kit bus), R-PWR (the PSE), R-HSD | as above |
| C | `C-C24-1f614233` | yes: generator unchanged since `faf8c981`, netlist unchanged `1f614233` to `fc144600` | R-SEC | rebuilt only if round 8 changes board C |
| D | `D-D12-1f614233` | **no**: superseded by `458b2873` | none of the routes above | the superseded label on the folder (a writer of that folder), and a packet at the round 8 merge |
| E | `E-E17-1f614233` | yes: generator unchanged since `faf8c981`, netlist unchanged | R-PWR | rebuilt only if round 8 changes board E |
| P | `P-P4-1f614233` | **no**: superseded by `d90f30e4` | R-BAT (the battery packet stands on its own; see 2.1) | the superseded label, and a packet at the sending revision |

Round 8 runs a circuit stream on every board, so the practical rule is one build of every changed board's packet at the
round 8 merge, on the KiCad host, by the integrator (`review_packet.py` needs KiCad 9). Board artefacts are not this
stream's to write.

## 8. Spend and lead-time summary

| Line | VERIFIED amounts (native currency, VAT as the page shows) | TBD lines | New spend, or a prototype part bought early |
|---|---|---|---|
| R-BAT | none | the quote | new spend (approved in principle, D-09) |
| R-SEC | the voucher: no project cost shown [W13] | time beyond half a day | none within the voucher |
| R-PWR | none | the quote | new spend (not approved) |
| R-HSD | none | the quote | new spend (not approved) |
| R-EMC | none | the quote, at the build | at the build |
| Z-EXP-A to C | USD 8.09, USD 2.95, GBP 3.80; USD 58.00 if the MikroE board is obtainable | DM320118, load switch, instruments | new spend (bench) |
| EMCON early rows | EUR 159.46 excl. VAT (or EUR 6,509) | module, evaluation board, SA868, SIM, RF parts, instruments | new spend (bench); the module and SA868 are prototype parts |
| Heat test | EUR 198.56 excl. VAT (case and frame); GBP 349 | plate blank, heaters, fans, thermocouples, supply | case and frame are prototype parts; the rest new spend |
| Mock-up | USD 947.88 excl. duties; USD 569.00; GBP 4.80 | made parts, connector-plate items, jumpers, stand-ins, tools | mostly prototype parts bought early; made parts partly new (the face plate is the prototype's own if it passes) |

Lead times VERIFIED today: SIDN fonds pioneers answer within six weeks [W15]; JLCCNC "from 3 business days" (CNC) and
"from 2 days" (sheet metal) [W27]; in stock: the case [W1], the Pico [W3], the breakouts [W22], the logger [W17], the
heatsink [W25]; not in stock at its last archived reading: the MikroE socket board [W2]; one comparison store closed 1 to
15 October 2026 [W4]. Every reviewer's lead time is TBD by quote.

## 9. Prepared texts (NOT SENT)

Existing, in the tree at `fc144600`, each for the owner to send or not:
- R-BAT request: `v2/docs/review-packets/battery/REVIEW-REQUEST.md`, "Ready-to-send request".
- Questions to TI (Q-TI-1 to Q-TI-7) and to the cell supplier (Q-S1): the same file, section 4. To Eaton (Q-E1 to Q-E5):
  `FUSE-INTERPRETATION.md` section 7.
- R-SEC, R-PWR and R-HSD request texts: `v2/docs/reviews/REVIEW-ROUTES.md`.
- To AsiaRF, Xenarc and Lime Microsystems: `v2/docs/records/rv-pwr/pwr-maker-questions.md`.

New here:

### T1. SIDN fonds voucher request (NOT SENT; the content for the fund's form, mailed to `projecten@sidnfonds.nl`)

> Project: MeshSat, open-hardware field communications kit (supported by SIDN fonds). Voucher topic: technical
> expertise, security. We ask for half a day of a hardware-security expert's time to review the ZEROIZE design of our
> prototype: crypto-erase by destroying two key-encryption keys held in a Microchip ATECC608B (GenKey over updatable
> slots after the zones are locked), triggered by a covered toggle held five seconds and completed after a power loss,
> with key fill over a sealed console port. The design is unbuilt and has so far been reviewed only by AI agent
> sessions. The reviewer would answer four questions and one stated residual risk (a second firmware-bearing part on the
> secure element's bus). The material is public: `v2/docs/feasibility/ZEROIZE.md` and its records in the
> meshsat-fieldkit repository, at [commit link].

### T2. Statement of work for a pre-layout signal-integrity review of board B (NOT SENT; attach to the R-HSD request)

> **Object.** MeshSat field kit V2, board B (compute), an unbuilt prototype under CERN-OHL-S-2.0: three Raspberry Pi
> Compute Module 5 slots on board-to-board receptacles; per slot a PCIe Gen 2 packet switch (Diodes PI7C9X2G404SL), a
> USB 3 hub (TI TUSB8041), SuperSpeed and USB 2 host-select switches (TMUXHS4212, TS3USB221A), an M.2 NVMe socket and an
> M.2 card socket; a display switch cascade (TS3DV642); a KSZ9897 Ethernet switch with capacitively coupled module links.
> **Inputs supplied.** Schematic PDF and native KiCad 9 files at [commit] (the board B review packet); the interface
> numbers with their sources (`v2/ecad/tools/pcb_interfaces.yaml`); the lane, pin and clock map
> (`v2/docs/feasibility/FAILOVER-FABRIC.md`); the fabric architecture and its FMEA (`v2/docs/ARCH-PCB-B-IOHA.md`); the
> escape diagnosis and trial (`v2/docs/B-FEASIBILITY.md`); the fabricator's stackup record, including the eight-layer
> stack under study; the filed data sheets (`v2/vendor/SOURCES.yaml`). No preliminary layout exists for the corrected
> circuit; an older placement is available as context only.
> **Questions.** The six of `REVIEW-ROUTES.md`, R-HSD: lanes, polarity and AC coupling per slot; the reference clock;
> the USB 3 loss budget through the host-select switches and the connectors; the capacitively coupled Ethernet links and
> the display cascade; whether 2D field-solver results suffice for Gen 2 and 5 Gb/s at these lengths and which
> simulation is proportionate before a first build; the escape at 0.4 mm pitch on eight layers with return paths and
> decoupling at the fine-pitch parts.
> **Deliverable.** Written findings against the named revision, each classified acceptable, acceptable with a change, or
> blocking, with the file and the reason; the items you would block layout commitment on. **Please quote** hours, price
> and earliest date. The design and its reviews so far are the work of AI agent sessions.

### T3. Request for quote and pin access, 5G evaluation kit (NOT SENT; to Quectel sales or an EU distributor)

> We would like a quote for one Quectel 5G-M2 EVB kit (5GM2EVB-KIT) and one RM520N-GL module of order code [code], for
> delivery to the Netherlands. Before ordering: on the 5G-M2 EVB, can W_DISABLE1#, FULL_CARD_POWER_OFF#, RESET# and
> PERST# each be driven from an external logic signal, and can the module's 3.3 V supply be switched from outside the
> board? Does the EVB give a PCIe host connection, or only USB? Please include the lead time.

### T4. ATECC608B full data sheet (NOT SENT; the owner's Microchip account or sales contact)

> We are designing a prototype that uses the ATECC608B-SSHDA-T to hold key-encryption keys that are destroyed by GenKey
> (mode 0x04) on updatable slots after the configuration and data zones are locked. We request the complete ATECC608B
> data sheet under NDA, in particular the configuration-zone encodings and the behaviour of GenKey when power fails during
> its write.

Machining quotes need no text: JLCCNC and similar services quote online from uploaded drawings once section 6.2's
drawings exist; that upload needs the owner's account.

## 10. Sources read for this page

Read on 26 September 2026 between 21:02 and 21:19 UTC (23:02 to 23:19 CEST); W4b and W30 were read at 21:44 to 21:45
UTC for the corrections. "runner, sha256" means the
page was fetched by the runner and the hash is of the bytes received; the snapshots are third-party pages kept in the
session's scratch record, not published. "reader" means the session's web reader, which keeps no bytes.

| ID | Page | Read (UTC) | How | What was read |
|---|---|---|---|---|
| W1 | https://flight-cases.eu/peli-1450.html | 21:04 | runner, `24511c808c73c730` | "Peli Protector 1450", "€211.13 €168.90", "Normal in stock", "Excl. Tax Incl. Tax"; "Peli 1450PF Special Application Panel Frame Kit", "Special Price €37.08 €29.66 Regular Price €41.20 €32.96"; "60 days free Returns"; seller Guardique Products A/S, Denmark |
| W2 | https://web.archive.org/web/20251118140325/https://www.mikroe.com/secure-soic-click (the live page answered 403) | 21:06 | runner, `5e7e419743c7c30c` | "PID: MIKROE-3788", "$58.00", "This product is no longer in stock"; "comes with three ATSHA204A ICs, and one ATECC608B" |
| W3 | https://thepihut.com/products/raspberry-pi-pico | 21:06 | runner, `6b94d0e6b2eb3485` | "SKU: SC0915", "£3.80 incl. VAT", "Stock: In stock" |
| W4 | https://store.thewirelesshaven.com/products/usb3-m-2-4g-5g-modem-adapter-enclosure-with-rm520n-gl-modem | 21:07 | runner, `3776800f529044ba` | served localised: `Shopify.country = "NL"`, `Shopify.currency = {"active":"EUR","rate":"0.89106444"}`, selector "Netherlands \| EUR €", variant `{"amount":289.95,"currencyCode":"EUR"}`, `og:price:amount` "289,95" with currency "EUR"; SKU USB3M2ADENC4G5G-V7-RM520NGL; "Shipping calculated at checkout."; "The Wireless Haven will be closed from October 1st to October 15th 2026" |
| W4b | the same URL with `.json` (the store's product JSON), and the page again | 21:45 | runner, `ef47b38b806fb67e` (JSON), `32664db5eda298d9` (page) | JSON: variant SKU USB3M2ADENC4G5G-V7-RM520NGL, `"price": "325.00"`, `"price_currency": "USD"`, `"taxable": true`; the page this time served `Shopify.country = "US"`, `{"amount":325.0,"currencyCode":"USD"}`, `price:"325.00"`, and the same closure notice |
| W5 | https://www.quectel.com/product/5g-m2-evb-kit/ | 21:05 | runner, `4f69a4fc29aa9d40` | applicable modules include "RM520N series"; "5GM2EVB-KIT"; key features include "Switches and button" and "Test points"; no price |
| W6 | https://sintecs.eu/services/signal-integrity-analysis/ | 21:07 | runner, `b46604b0df188b04` | the quotes in section 2.4 |
| W7 | https://sintecs.eu/services/power-integrity-analysis/ | 21:07 | runner, `0a4f75fe1f0120cc` | decoupling, DC drop, current density |
| W8 | https://sintecs.eu/contact/ | 21:18 | runner, `d3b5e39e2c2f2e3f` | "Sintecs B.V.", "Hengelo (O)", "THE NETHERLANDS", `info@sintecs.nl` |
| W9 | https://elteknik.gr/ | 21:07 | runner, `610282711c6445c5` | the quotes in section 2.3; Thessaloniki, Greece |
| W10 | https://www.how2power.com/consultants/ | 21:07 | runner, `3ec17cdab1941c99` | directory; "Analysis and design review services are also available" in one listing |
| W11 | https://www.sgs.com/en-nl/services/electromagnetic-compatibility-emc-testing | 21:08 | runner, `a8840eca545ff2e1` | the quotes in section 2.5; SGS Netherlands, Spijkenisse |
| W12 | https://www.dare.eu/emc | 21:19 | runner, `0457ca8691d30217` | the quotes in section 2.5 |
| W13 | https://www.sidnfonds.nl/vouchers | about 21:02 | reader | "een dagdeel advies van een expert uit ons netwerk"; for supported projects; the request form mailed to `projecten@sidnfonds.nl`; expert domains include technical expertise including privacy and security; no cost or lead time stated |
| W14 | https://www.sidnfonds.nl/pioneers | 21:09 | runner, `74f7cab4cf0a069c` | "a grant up to € 10,000 for a pioneering project in the Stronger internet focus area", "Applications can be made any time" |
| W15 | https://www.sidnfonds.nl/aanvragen/pioniers | 21:09 | runner, `ccc70164efe03b20` | "tot max. 10.000 euro", "Binnen 6 weken", the 2026 'Sterk internet' focus |
| W16 | https://www.xenarcdirect.com/index.php?main_page=advanced_search_result&keyword=709GNK | 21:11 | runner, `08ecbbaa11cfb3a3` | "709GNK 7" IP67 Sunlight Readable Capacitive Touchscreen LCD Display Monitor with HDMI Input", "$569.00" |
| W17 | https://www.picotech.com/data-logger/tc-08/thermocouple-data-logger | 21:09 | runner, `50031e57075784cf` | "SKU: PP222", "£ 349", "Currently In Stock", "8 input channels + CJC" |
| W18 | https://www.siglenteu.com/spectrum-analyzers/ssa3000x-plus/ | 21:10 | runner, `4b44f9aaa0369860` | "SSA3021X Plus 9 kHz ~ 2.1 GHz ... €1,469", "SSA3032X Plus ... €2,439", "SSA3075X Plus 9 kHz ~ 7.5 GHz ... €6,509"; option SSA3000XP-EMI |
| W19 | https://tinysa.org/wiki/ | 21:10 | runner, `91063200bcca6b44` | "tinySA Ultra+ ZS407 ... with Ultra mode enabled up to 7.3 GHz, level calibrated up to 7.3GHz" |
| W20 | https://tinysa.org/wiki/pmwiki.php?n=Main.Buying | 21:10 | runner, `7a236ef7de902923` | "Where to buy the tinySA Ultra or Ultra+": "Eleshop in Europe" |
| W21 | https://eleshop.eu/tinysa-ultra-zs-407-spectrum-analyser.html | 21:13 | runner, `e4b020eb05495c89` | "tinySA Ultra+ ZS-407 spectrum analyser", "€159.46 Excl. VAT", "Product number: ELE007983", "Loading stock info" |
| W22 | https://www.adafruit.com/product/1212 | 21:11 | runner, `33425297c95fa1cd` | "SMT Breakout PCB for SOIC-8, MSOP-8 or TSSOP-8 - 6 Pack!", "$2.95", "In stock" |
| W23 | https://www.polyphaser.com/sma-surge-protector-6ghz-gas-discharge-tube-gth-sff-al | 21:11 | runner, `b854e661255ae11f` | "SKU GTH-SFF-AL", "QTY available Call us", "1 + $78.99", "All Prices are in US Dollars and do not include duties" |
| W24 | https://www.radioparts.com/polyphaser-gth-sff-al | 21:11 | runner, `763966fd1b1c4366` | "MSRP: $82.15", "Now: $73.45", "(Inc. Tax)" |
| W25 | https://thepihut.com/products/raspberry-pi-compute-module-5-passive-cooler | 21:19 | runner, `713598b29ea8ab87` | "SKU: SC1752", "£4.80 incl. VAT", "Stock: In stock" |
| W26 | https://www.sameskydevices.com/product/thermal-management/dc-fans/axial-fans/cfm-6025bg68-series | 21:13 | runner, `08d49da2d691df44` | the 12 V IP68 -22 rows named in section 5.2; no price |
| W27 | https://jlccnc.com/ | 21:15 | runner, `571ba6f513c53c7a` | "Lead time from 3 business days" (CNC); "Lead time from 2 days" (sheet metal); "Aluminum 6061", "Aluminum 7075", sheet metal "Aluminum 5052" |
| W28 | https://jlcpcb.com/pcb-impedance-calculator | 21:15 | runner, `4dd22b28f3b3998c` | "Controlled Impedance Calculator - JLCPCB" |
| W29 | `v2/docs/records/rv-zer/prices/jlc-ATECC608B-SSHDA-T.json` (in the tree) | 12:27, read by the ZEROIZE stream | JLCPCB parts API | C1518769 ATECC608B-SSHDA-T, stock 2344, USD 0.9955 at 1 to 9, 0.8088 at 10 to 29, 0.7162 at 30 to 99 |
| W30 | Microchip DS50002921A, CryptoAuth Trust Platform User's Guide (DM320118), the Wayback capture 20240510124055 that `v2/docs/records/rv-zer/datasheets/SOURCES.md` lists | 21:44 | runner, `6951ca754fad1f9e` (equal to the sha256 SOURCES.md records) | p. 3, board overview item 6 "Dual SPST DIP Switch"; p. 4, "ATECC608A-MAHDA" at default 7-bit I2C address "0x60"; p. 5, "DIP Switch: The switch is used to select between the on-board ATECC608A Trust Platform devices and the mikroBUS header. The switches disconnect the SDA lines of the I2C interface to prevent conflict in case two I2C addresses are the same", and the table "SW2_1 ON, SW2_2 OFF": mikroBUS header Yes, on-board devices No |

Pages that refused the runner on 26 September 2026 (so their figures are TBD above): peli.com and pelican.com (403),
mikroe.com (403), RS, Farnell, DigiKey, TME and Microchip's product pages for the DM320118 (403), NiceRF (403),
raspberrypi.com (403). One domain named in a public directory, `convertertechnology.co.uk`, now serves unrelated
content and is not cited.

## 11. Choices taken by the session under the owner's standing rule of 26 September 2026

None spends money or contacts anyone; each is reversible by the owner or by a later measurement.

- **S-1.** One Peli 1450 serves the heat-balance test first (undrilled, sealed) and then the mock-up, which drills it;
  it is the prototype's own case (D-08a). Why: the heat test needs the sealed skin, the mock-up needs the holes, and a
  second case buys nothing the first cannot show.
- **S-2.** R-BAT's send condition: the release check passes and the packet's candidate netlist and schematic equal main's
  board P at the linked commit. Why: the reviewer must read the circuit that will be built.
- **S-3.** R-SEC's scope is fitted to the voucher's half day (the four questions and R7). Why: a half day cannot cover
  the whole packet, and these are the items only a security reviewer can close.
- **S-4.** If MIKROE-3788 cannot be bought, only the socket board is replaced: the secure-element samples go on
  Adafruit 1212 breakouts, one part per breakout, and a breakout is wired to the DM320118's mikroBUS header for Z-EXP-A
  and to the Pico for Z-EXP-B and C. The DM320118's own DIP switch SW2 stays at mikroBUS only (SW2_1 ON, SW2_2 OFF), as
  `ZEROIZE.md` section 5 sets it: the switch is on the DM320118, and it is what keeps the on-board ATECC608A-MAHDA,
  which also answers at 0x60, off the bus the sample uses (DS50002921A pp. 3 to 5, [W30]). Only one breakout is on
  the header at a time, because every sample is expected at 0x60 too (`ZEROIZE.md` A0). Every step of `ZEROIZE.md`
  section 5 is unchanged. Why: the archived page reads "no longer in stock", and three breakouts carry the three parts
  A needs, two of which B reuses.
- **S-5.** The EMCON rows split as in section 4.1: early on development hardware where the row decides a board circuit
  (E-01 row 5, E-05, E-12's early parts), at the built kit otherwise. Why: the second review's point A.
- **S-6.** E-12 (e)'s withheld cycles run last on the one bench module. Why: they can corrupt its flash.
- **S-7.** The development tier of analyser (tinySA Ultra+ ZS-407) for the early rows; the acceptance instrument for the
  built kit stays the TEST-PLAN owner's, and R-EMC's lab may supply it. Why: the early rows decide circuit values and a
  topology choice, not acceptance, and the instrument reaches 7.3 GHz for EUR 159.46 excl. VAT against EUR 6,509.
- **S-8.** The mock-up runs before the outlines and connector places of boards A, B and E are frozen, not at the build
  stage that `CASE-MARGINS.md` section 7 recommends, and it does not gate their layout entry. Why: the second review's
  section 3 asks for it before those become expensive to change, and its item 2 asks that no layout-entry gate depend on
  an unauthorised purchase. `CASE-MARGINS.md` is
  not changed by this page; its writer carries the timing.

## 12. What this page does not settle, and hand-offs

- It judges no design, releases no board and authorises nothing. The packets it points to are review inputs.
- Staging R-PWR and R-HSD against layout entry and fabrication release: the review's item 2 stream (no circular gates).
- The superseded labels on `D-D12-1f614233` and `P-P4-1f614233`, and the packets owed at the round 8 merge: the
  integrator, on the KiCad host (section 7).
- The RM520N-GL and SA868 order codes, and the mock-up's open picks: the parts work (sections 4.2, 6.2).
- The drawings of C1 to C6: the case writer (section 6.2).
- `REVIEW-ROUTES.md` still says the battery packet and the ZEROIZE, POWER-THERMAL and DECOUPLING pages are "pending
  merge"; all are on main (`d90f30e4`, `9b0635d1`, `eadbe571`, `9d566e8b`, filed citations `428c697c`). Its R-PWR
  "Owed" line still lists the per-stage calculations (compensation, ripple current per bulk capacitor, inrush), which
  `428c697c` filed as `v2/docs/records/r4a/` (section 2.3). A pointer to this page and a correction of that line are
  drafted for its writer (a patch that applies to `fc144600`).
- Filing the scripts and runs behind board A's calculation record (section 2.3): the records writer, with the tools and
  board streams that own the comments citing them.
