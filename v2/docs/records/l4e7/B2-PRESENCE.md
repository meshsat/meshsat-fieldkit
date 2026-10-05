# Route B2: the solar receptacle's presence pair feeding U21's INP (P0-7, MESHSAT-1357; an unapproved PARTIAL proposal)

Prepared 5 October 2026 by task P0-7 at the coordinator's instruction of 17:12 CEST (route B2 selected by the coordinator as the
bounded PROVISIONAL desk route for D-10's port-level residual, under the owner's rules of 21 September and 5 October part 19, with
`SUPPLIER-P1-1-P0SOL.md` as its validation). Prototype design: nothing is built, bought, mated or measured. Every figure below is
printed by `l4e7_p0sol.py` (section 5 of `l4e7_p0sol.out`). Correspondence and orders: none; this page is drafts only.

**Standing of this route (the owner's review of checkpoint 4, part 23):** D-10 is an UNRESOLVED PROTECTION DEFECT in the present
model, carried as the receiving company's remaining engineering item E-1 (`SUPPLIER-P1-1-P0SOL.md`). Route B2 is an unapproved
PARTIAL interface proposal: it would prevent the guard-on step only for a source that arrives through a mating point of the
presence loop, it does not change the port's response when a step happens, and adopting or declining it does not resolve D-10.

## 1. Authority: is the receptacle's contact arrangement protected?

- **reserved.json** (`v2/ecad/tools/reserved.json`, the never-auto floor): nine classes (impedance targets, net class widths, fab
  rules, layer count and stackup, the intra-pair gap, the packer's regions, the DRC policy, the order set, the design record's 32.x
  headings). **None names a connector, an insert or a contact arrangement.** The board E draft touches no reserved line.
- **The owner's rulings on the connector plate:** ruling 6 of appendix 32.13 (4 September 2026) puts shore DC on "a keyed sealed
  circular wall connector" (MIL-DTL-38999); 32.32 closes ruling 4 with the panel "an accessory of the owner's choice ... on the shore
  plug's second pair" (BUILD.md); the part picks of 32.21, which the owner accepted on 4 September, name the Glenair
  D38999/20FC4PN receptacle and D38999/26FC4SN plug, shell 13, insert 13-4, four size 16 contacts. The insert is already reopened by
  D-06's consequence R-129 (the DC pair to size 12 contacts, insert 17-6 or 13-26; MISSING DRAFT).
- **The owner's two-part test (21 September 2026):** B2 changes what the kit is claimed to accept at its solar input (a panel then
  charges only through a plug that bridges the presence pair, where the accepted text says a panel of the owner's choice on the
  plug's second pair), changes an owner-accepted pick (the insert's contact count) and adds cost; and more than one option is still
  standing after the measurement (B2, or the drawn interface with the guard-on residual left to the supplier's S1). **Both halves
  hold: the interface decision is the owner's.** B2 therefore stands as a PROPOSAL, with the owner item of section 2. What is not
  the owner's and is taken here as SESSION decisions (section 6): how board E implements the loop.

## 2. The owner item (the smallest concrete decision, with its consequences)

**Decision asked:** may the kit's solar input carry a presence contact pair, so that a source arriving through the solar lead's
mating points arrives with the guard off? (A partial measure: D-10 stays an unresolved protection defect either way, E-1.)

| | (a) Adopt the presence pair (recommended) | (b) Keep the drawn interface |
|---|---|---|
| What changes | The wall receptacle's insert gains two contacts: with R-129's size 12 DC pair, insert 17-6 (six size 12 contacts, Amphenol's insert table, MAKER) carries DC A/B, solar C/D and the presence pair E/F with no further count change; the DC lead's cable goes from four to six cores; the solar tail ends in a connector whose presence contacts make last; the panel connects through a kit-supplied adapter lead that bridges the pair; board E gains J_SOLP and C80 and moves R96 (section 6) | nothing |
| What it would prevent | the guard-on step for a source that arrives through a mating point of the loop: such an arrival meets the cold connection, whose absolute ratings hold over the whole envelope (0.30 to 10.20 uH, section 5d of the .out); D-10 is not resolved by it (E-1) | nothing; the guard-on step stays a modelled absolute-rating violation below the port's floors (PV_F over 100 V below about 2.4 uH), E-1 |
| What stays | D-10 as an unresolved protection defect (E-1): the port's response to any step that still happens, a second stiff source added on the same lead while a panel holds the loop closed (OPEN, S1); the arriving source's slew margin line under 0.33 uH and PV_F over the recommended 80 V row under 0.78 uH (inside the absolute ratings; S2) | everything of D-10's port residual (S1) |
| Cost | not quoted: one insert size up (shell 13 to 17 is already R-129's question), two crimp contacts, two cable cores, a 4-pole sequenced connector at the solar tail and an adapter lead per panel, an XH socket, a capacitor and a lead on board E (ASSUMPTION: tens of euros a kit) | none now; the residual's validation (S1) stays |
| Claim change | "a panel through the kit's adapter lead" instead of "a panel of the owner's choice on the plug's second pair" | none |

Recommendation: (a), as a partial measure beside E-1's correction, never in place of it. Until the owner rules, the board E draft
is a PROPOSAL and nothing of it is released.

## 3. R-180 rewritten: the contact requirement (Layer 7, a named prerequisite of Layer 4's power gate)

**Text for L4-E9's change list (R-180, replacing "a stiff source's loop at J_SOLAR bounded and measured"):**

> R-180 (Layer 7, the harness and the external connectors; a named prerequisite of the Layer 4 power gate under the owner's P0
> instruction of 5 October 2026, section 4; PROPOSAL until the owner rules section 2's item): **every mating point that the solar
> input's presence loop passes (the wall receptacle and the solar tail's connector) closes the presence pair only after both of the
> solar pair's power contacts carry the source (make-last).** The lead: at least 1 mm of engagement travel, or a maker's stated
> first-mate-last-break sequence; no presence contact closes before either power contact. Where a mating point cannot sequence its
> contacts (the held D38999 sheets print no first-mate-last-break contact), that point is declared not a field mating point: the
> kit's DC lead stays mated at the wall, its coupling secured, and the requirement applies at the solar tail, where sources are
> connected. The presence pair is a twisted pair inside the lead, 22 to 24 AWG, insulated for the lead's voltage, with no
> connection to either power conductor or the shell; the panel adapter lead bridges it inside its plug.
> **Reason:** with the pair making last, the source is on PV_F before INP can rise, so U21's OV (at most 31.06 V, within 4 us)
> holds Q12 off for any source above the cut-off, and a source under it starts the stage through the gate slew; the guard is never
> closed when a stiff source arrives through a mating point of the loop (part of D-10, B6, L4-F01; D-10 itself stays E-1's).
> **Acceptance:** on three specimens of each mating point, fifty mating cycles each at the fastest hand speed: the presence pair's
> closure measured at least 1 ms after both power contacts (a four-channel continuity recorder), and on the assembled kit (S2) a
> 36 V source mated at the solar tail through a 0.30 uH loop leaves Q12's gate below its threshold and PV_F inside its absolute
> ratings.

## 4. The Layer 6 row for the receptacle (draft)

| Item | Selection | Basis | Owed |
|---|---|---|---|
| Wall receptacle | MIL-DTL-38999 series III, wall mount, the insert carrying six contacts: 17-6 (six size 12, MAKER: Amphenol series III insert table) with R-129's size 12 DC pair; or 17-8 (eight size 16) if the DC pair stays on paralleled size 16 contacts | ruling 6 of 32.13 (the 38999 family); R-129 (D-06's insert) | the MPN (CASE-MARGINS.md section 6), the plate cut-out for shell 17, the contacts' installed rating (R-129) |
| Plug | the matching D38999/26 straight plug, shell 17, socket contacts, with its M85049 strain relief | 32.32 (the plug family) | the MPN |
| Presence contacts | E and F of the insert, crimped on 22 to 24 AWG with the size's reducing sleeve or the insert's own contact size; not sequenced at the wall (section 3) | R-180 | the contacts' wire range |
| DC lead cable | six cores: the DC pair and the solar pair at the gauge R-129 and R-29 set, the presence pair as a twisted pair | R-180 | the cable's MPN |
| Solar tail connector | a 4-pole connector, IP67 mated, whose presence contacts make last by at least 1 mm (a first-mate-last-break family), keyed so that the DC tail's plug cannot mate it | R-180 | the family and MPN (not selected here) |
| Panel adapter lead | the tail connector's mate, the presence pair bridged inside it, to the panel's own connector | R-180 | the panel's connector (PANEL-ACC) |
| Board E | J_SOLP, JST-XH 1x2 B2B-XH-A (C158012, J_TAMP's part); C80 10 nF C0G 100 V 1206 (C184799, C127's part); R96 and R97 as drafted (R97 24.9k C136967) | `apply_gen_sch_e_p0sol_b2.py` | R96's LCSC code (owed since round 5) |

## 5. The board E draft and its checks (the .out's section 5)

`apply_gen_sch_e_p0sol_b2.py` (4 edits), composed in L4-E9's order after `apply_gen_sch_e_p0sol.py`: all seventeen drafts apply, the
draft refuses a second application, the generator runs (298 parts). Four predicates hold in the netlist on top of section 2a's nine
(R96 from PV_F to the loop net and not to INP; J_SOLP the loop's only path to INP; INP's net exactly U21, R97, C80 and J_SOLP; U21's
OV and UVLO dividers as drafted). Four mutations each fail (R96 straight onto INP, the loop bridged on the board, R97 off INP, C80
off INP). The withdrawn plug: INP falls from its highest 6.20 V under V(INP_L)'s least 0.8 V in at most 0.543 ms and Q12 is off at
most 0.544 ms after the pair opens. The arriving source (the record's cold connection over its whole grid, 608 events, the worst
equal to the record's): every absolute rating held (PV_F 84.62 V of 100 V, slew 56.10 V/us of 60, INP 16.90 V of 20, EN 12.48 V of
20, PV_F's least 0 V); the 90 V, 18 V lines held everywhere; the 54 V/us slew line holds from 0.33 uH and the recommended 80 V VS
row from 0.78 uH (PROVISIONAL, S2).

## 6. SESSION decisions of the board E implementation

| Decision | Reason | How to reverse | authority | ruled_by | ruled_on |
|---|---|---|---|---|---|
| The loop sits between R96 and INP (R96 stays on PV_F; the pair carries the divider's node, not PV_F) | a shorted or broken presence core can only hold INP low (the guard off), and the loop carries at most PV_F / 100 kOhm, never the port's current; R96's top on the contact would put PV_F itself on the lead | move R96's top to the loop's return (the coordinator's literal wording) if a layout or EMC reason prefers it, with the fault current through a damaged core bounded first | SESSION | P0-7 (Claude), under the owner's rule of 21 September 2026 | 5 October 2026 |
| C80 10 nF C0G at INP | filters what the external pair picks up while keeping the withdrawn-plug turn-off under 0.6 ms | a larger C80 also delays INP's rise (a means if a mating point cannot sequence), at the cost of a slower turn-off | SESSION | P0-7 | 5 October 2026 |
| J_SOLP a JST-XH 1x2 (J_TAMP's part) | a signal pair, microamps; a part board E already carries | any 2-pole signal socket the harness prefers | SESSION | P0-7 | 5 October 2026 |
| U21's turn-on stays at INP (10.05 V at the most) | no change of the window; the loop only adds a series switch | none needed | SESSION | P0-7 | 5 October 2026 |

## 7. What B2 does not cover (OPEN)

- **A second stiff source added on the same lead while a panel holds the presence loop closed** (a parallel connection behind the
  plug, or a source spliced onto the panel's own lead): the guard is on and the step is section 2b's guard-on case (at the reference
  loop every rating but PV_F's recommended row holds; at the least loop the port fails). OPEN; validation P1-1's S1.
- **A stiff source below the stage's voltage arriving after a withdrawal:** while the guard is off, PV_P back-feeds PV_F through Q12's
  body diode, so such a source draws the stage's charge back through it (the reverse of the step; it would flow through the closed
  channel without B2). Not computed here; validation P1-1's S1 (row added).
- **The presence loop under CS114** (bulk cable injection on the lead now covers the pair): C80 is a means, not evidence; M3 reads
  INP on the specimen (S2 row added).
