# The definition re-issue on the owner's layer 3 answers: DRAFT

**Status: PROPOSED, not approved.** Written by `v2/docs/records/l3r4/reissue.py` from the owner's rulings on rows L3-OD1 to L3-OD7 of `OWNER-DECISIONS-L3.md` as the requirements registry records them (answers digest `156a2e742bda1892`: the sha256/16 of the answered rows' rulings and of every record citing them). `CONOPS.md` and `PRODUCT-BRIEF.md` are unchanged and stay BASELINED (`6cb7b241cb84d729` and `85513b92ed0daf55`) until the owner approves the change record `DEFINITION-CHANGE-RECORD-L3.md` by a ruling that decides the re-issue; the documents are then issued again through their layers' review (`handover/DEFINITION-STATUS.md`, the rule). Prototype design: no V2 board has been fabricated, ordered or powered, and no kit has been field deployed.

## The answers

| Row | Option | Owner ruling | Ruled on | Title |
|---|---|---|---|---|
| L3-OD7 | `objective-48-72` | D-32 | 30 September 2026 | M1's runtime: 48 to 72 hours, a design objective under the stated profile (row L3-OD7) |
| L3-OD1 | closed as layer 4 architecture | none | none | At layer 3 the requirement is the store inside the Peli 1450, battery and solar required and no external battery (D-28; REQ-014). The store's size and arrangement is layer 4 architecture: D-06's one 4S3P pack stands as ruled, and Option A(i) (a base 4S6P and a lid pack) is carried to layer 4 as an architecture proposal (P-01), which changes D-06 and needs the owner's ruling there. It is not a layer 3 blocker. |
| L3-OD2 | `both-kept` | D-33 | 30 September 2026 | Both lid items kept, the QMX HF set and the tablet bracket (row L3-OD2) |
| L3-OD3 | `unchanged` | D-34 | 30 September 2026 | REQ-016's approved solar window unchanged (row L3-OD3) |
| L3-OD4 | `reject` | D-35 | 30 September 2026 | No deployment condition at layer 3 (row L3-OD4) |
| L3-OD5 | `layer4-obligation` | D-36 | 30 September 2026 | CFL-017 closed as a requirements conflict; the cell and thermal design a layer 4 obligation (row L3-OD5) |
| L3-OD6 | `mean-day` | D-37 | 30 September 2026 | M1's solar conditions: SC-37's mean day, one plane, TYP (row L3-OD6) |

## M1 as the registry reads it

Requirement REQ-072, part of prototype 1's core, reads FAIL (DESK_REVIEW, SCHEMATIC phase) when this re-issue is written: the design as it stands does not meet M1's runtime objective (design risk DR-01, layer 4); its current reading is kept in the requirements registry and `handover/DEFINITION-STATUS.md`.

## `CONOPS.md`

### C01. the status line of the head (line 3)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD2 `both-kept`, D-33; L3-OD3 `unchanged`, D-34; L3-OD4 `reject`, D-35; L3-OD5 `layer4-obligation`, D-36; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> **Status: layer 2 of the foundation baseline (MESHSAT-1357), BASELINED at `a9f212c7`,**

**Proposed text:**

> **Status: layer 2 of the foundation baseline (MESHSAT-1357), RE-ISSUED on the owner's rulings on layer 3 (the re-issue note below), pending its layer's review; BASELINED at `a9f212c7`,**

### C02. the head, after the rule of reopening: the re-issue note (line 15 to 16)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD2 `both-kept`, D-33; L3-OD3 `unchanged`, D-34; L3-OD4 `reject`, D-35; L3-OD5 `layer4-obligation`, D-36; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> a change to it alone does not reopen this
> document.

**Proposed text:**

> a change to it alone does not reopen this
> document.
>
> **Re-issue on the owner's rulings on layer 3 (30 September 2026).** The owner's clarifications D-28 and D-29 answer rows
> L3-OD2 to L3-OD7 of `handover/layer3/OWNER-DECISIONS-L3.md` (owner rulings D-32, D-33, D-34, D-35, D-36 and D-37); row
> L3-OD1's store is layer 4 architecture. They restate requirements this document traces to, which reopens it by the rule
> above: each passage they change is restated in place and names its row and ruling, the change record
> `handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` lists every passage, and its draft
> `handover/layer3/DEFINITION-REISSUE-DRAFT.md` keeps each one's baselined text. The owner's approval of that record is
> named in `handover/layer3/l3r2.yaml` (`definition_reissue`).

### S07. section 1, the local end users: the lid tablet (line 67)

Rows and rulings: L3-OD2 `both-kept`, D-33.

**Baselined text:**

> the lid tablet (ATAK class, fed by the USB-C outlet and the kit's WiFi, 32.50 item 16d)

**Proposed text:**

> the lid tablet (ATAK class, fed by the USB-C outlet and the kit's WiFi, 32.50 item 16d; kept by owner ruling D-33 on row L3-OD2, its charging optional and reducing endurance, D-28)

### S01. section 3, M1's title (line 152)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> ### M1. Remote site relay on pack and solar (72 hours)

**Proposed text:**

> ### M1. Remote site relay on pack and solar (48 to 72 hours, a design objective)

### S02. section 3, M1's duration and who set it (line 163 to 165)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> **The
> duration is 72 hours, taken by the session under the owner's standing rule of 26 September 2026 (section 7a) in
> place of the setting D-06 reserved for the owner, which replaces it whenever he gives one.**

**Proposed text:**

> **The duration is a design objective of 48 to 72 hours under the stated operating profile, not a mandatory minimum
> (owner ruling D-32 on row L3-OD7, applying the owner's clarification D-28), in place of the session's SC-21 (section
> 7a).**

### S03. section 3, M1's energy: the objective, its profile and the modelled baseline (line 167 to 198)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> **What that asks of the kit's energy, and what the
> design gives (a layer-4 finding, not a reason to shorten the mission; restated on 27 September 2026 after Review A,
> B3).** Two limits, and the first binds. (1) **The night.** Solar input stops in the dark, and an aged pack holds about
> 108 Wh usable (INFERRED: each state's aged runtime times its power, section 4a), which carries the kit through 2.5 h
> of darkness at PS-IDLE-SPEC, 3.5 h in the reduced mode and 4.7 to 5.0 h in the heat stage (3.2, 4.3 and 5.9 to 6.3 h
> on a new pack). At the Netherlands' latitude, about 52 N, the sun is down for about 7 hours at midsummer and about 16
> at midwinter (INFERRED from the latitude; no ephemeris is held in this tree); only near the Arctic Circle, at the EU's
> northern edge in summer, are nights as short as the pack, and a panel gives little near dawn and dusk. So across the
> market D-04 scopes, those northern summers apart, on its pack and solar alone the kit does not run through a night, in
> any state and at any solar rating, with the one pack of D-06 and the second pack D-01 defers: the shortest night at 52 N in the lightest state
> asks about 150 Wh (21.7 W for 7 hours) of the 108 Wh held. (2) **The day's
> energy.** 72 hours at 42.8 W is 3.08 kWh, so solar must supply about 1.0 kWh a day through the charge path; the kit's
> input front end regulates 20 V at up to 5 A, about 100 W (32.55), so the panel would have to deliver that full rating
> for about 10 to 11 hours of every 24, which a fixed panel does not do: on the design month's mean day (September at
> Leiden, 4.0 kWh/m2 a day on a panel inclined at the optimum 40 degrees, PVGIS-SARAH2 2015 to 2020,
> `v2/vendor/solar/pvgis-leiden-monthly-2015-2020.json`; the requirements registry's reference day, a session choice,
> section 7a) the 72 hours ask for a panel rated about 266 W; in the reduced mode (31.4 W, section 4a) about 7.5 to 8
> full hours a day, and in the heat stage (21.7 to 23.3 W) about 5 to 5.5. **The solar input's window is set**
> (REQ-016, a session choice of 27 September 2026, section 7a): a panel of at most 25 V open circuit at its coldest,
> held at 17.6 V by board E's LT8705A stage, and at most 100 W into it, as board E's generator declares the entry (its
> v_max of 25 V on the panel entry, against which every part on it is judged); whether the input path is re-rated to
> carry the day's energy is judged in layer 4, where the requirements registry's M1 balance record (REQ-072) reads FAIL
> at desk on both limits. September is the design month of that judgement, not a season M1 is limited to: M1 keeps the
> setting this section gives it, with no season taken off it, and a month with less sun asks more of the panel
> (December's mean on the same plane is about 1.1 kWh/m2 a day), which layer 4 records beside the design month. **The
> routes that carry the night, none of them taken here:** an overnight input on the 9 to 36 V vehicle and shore entry
> (a vehicle, a shore supply, or any DC source inside that entry's window, an external battery included, with no board
> change); the second pack that D-01 defers, which has no location found (section 2a); or a larger pack, which reopens
> D-06. The first changes M1's setting and the other two are the owner's rulings to reopen (with accepting the residual, the requirements registry's owner action M-02, decided before boards A, E and P enter layout; `handover/ENGINEERING-QUESTIONS.md` EQ-13), so M1 stays as set and the
> finding stands. **It is reported to the owner at the next checkpoint, not asked,** as a consequence of D-06's one pack
> together with the session's 72 hours: on pack and solar alone the kit does not hold M1 through a single night,
> whatever the solar rating.

**Proposed text:**

> **What M1 asks of the kit's energy, as the owner ruled it on layer 3** (the owner's clarification D-28, owner ruling
> D-32 on row L3-OD7; this replaces the layer-4 finding of 27 September 2026, whose text the re-issue's draft
> `handover/layer3/DEFINITION-REISSUE-DRAFT.md` keeps). M1's runtime is requirement REQ-072, a design objective: "Design
> objective (the owner's clarification D-28, not a mandatory minimum): under the operating profile stated in
> objective_profile, the kit's own store inside the Peli 1450 plus its solar input keep the kit serving its loads for 48
> to 72 hours of mission M1 (CONOPS section 3), 48 hours the lower end and 72 hours the upper end of the baseline design
> target, from a full, aged store (REQ-014). Battery-only and solar-assisted endurance are reported apart. Optional tablet
> charging and additional use, HF listening among it, reduce endurance, which the owner accepts (D-28)." Its stated
> operating profile: The essential loads of PS-IDLE-SPEC, 42.8 W at the pack terminals over its 39 loads (POWER-THERMAL.md
> section 4); the radio duty cycles of that state, HF available and not receiving (the QMX's USB and HDMI 5 V, 0.32 W), HF
> listening (1.14 W more) an additional use; the tablet not charged, the USB-C outlet off; a full store at the start, aged
> to 80 percent of the cells' specification minimum (REQ-014), each pack to its graceful line (5 percent relative state of
> charge, or its lowest cell at 3.00 V under load); battery-only at +20 C and -10 C; solar-assisted on SC-37's reference
> mean day at Leiden on one plane, 40 degrees facing south, in the typical array build (TYP), the worst array build (WAB)
> a sensitivity, from starts at 06 and 18 UTC. These are modelling assumptions, not owner-approved operating restrictions
> (D-28). Battery and solar are required, the store stays inside the Peli 1450, and no external battery is part of the kit
> (D-28). **The modelled baseline misses the objective even without tablet charging.** The present candidates miss the 48
> to 72 hour objective even without tablet charging. With HF and the tablet kept, battery-only from full: D-06's ruled
> 4S3P pack runs 2.52 h at +20 C (1.04 h at -10 C); the studied in-case candidate, Option A(i)'s base 4S6P and a 4S9P lid
> (544.4 Wh usable aged at +20 C), runs 12.71 h (5.24 h at -10 C). Solar-assisted on SC-37's mean day, one plane 40
> degrees facing south, TYP: D-06's pack does not carry a night (it allows at most 9.1 W for M1 against 42.8 W); the
> studied candidate stops at 05 UTC of the first night, hour 23 from a 06 UTC start and hour 11 from an 18 UTC start, as
> drawn (266.7 Wh unserved at 48 h, 494.7 Wh at 72 h) and on the hypothetical corrected path alike (102.2 Wh at 48 h,
> 165.7 Wh at 72 h, NOM), in 0 of 864 past September windows. The corrected path is not implemented. Optional tablet
> charging and HF listening reduce endurance further, which the owner accepts (D-28). This is design risk DR-01, assigned
> to layer 4; REQ-072 reads FAIL at desk. No figure of it is demonstrated capability, and nothing has been built.

### S04. section 3, M1: the owner's instruction D-20 (line 215 to 216)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> Until then REQ-072 reads FAIL and this section is not
> restated.

**Proposed text:**

> The owner answered it on layer 3 (the clarification D-28, owner ruling D-32 on row L3-OD7): M1's runtime is a design objective of 48 to 72 hours under the stated profile, and requirement REQ-072, part of prototype 1's core, reads FAIL (DESK_REVIEW, SCHEMATIC phase) when this re-issue is written: the design as it stands does not meet M1's runtime objective (design risk DR-01, layer 4); its current reading is kept in the requirements registry and `handover/DEFINITION-STATUS.md`.

### S11. section 4, the Storage row: D-02a's storage margins against the current cell (line 321)

Rows and rulings: L3-OD5 `layer4-obligation`, D-36.

**Baselined text:**

> D-02a's storage margins (+71 C, -33 C) are beyond the cells' ratings, so they run on the kit less its pack and on the pack at its cells' own limits

**Proposed text:**

> D-02a's storage margins (+71 C, -33 C) are beyond the current cells' ratings (the Samsung 35E, the current engineering selection): the margins stand unchanged, and with the pack fitted the current cell falls short of them, a layer 4 component-selection and thermal-design obligation (FEA-008, owner ruling D-36 on row L3-OD5 applying D-29); the runs on the kit less its pack and on the pack at its cells' own limits measure the rest of the kit and close nothing

### S05. section 6, missions longer than the pack and M1's night (line 1019 to 1024)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> Missions longer than the pack rely on vehicle or solar input: M1 is set at 72 hours (section 3,
> taken by the session under the owner's standing rule in place of the later setting D-06 reserved for the owner, whose
> own setting replaces it), and section 3 shows that on pack and solar alone the kit does not carry it through a single
> night, whatever the solar rating, because the aged pack bridges 2.5 to 5.0 h of darkness; the solar path's rating is
> a second limit. Both are a layer-4 finding, reported to the owner as a consequence of D-06's one pack with the
> session's 72 hours, not asked.

**Proposed text:**

> Missions longer than the pack rely on vehicle or solar input: M1's runtime is a design objective of 48 to 72 hours (section 3, owner ruling D-32 on row L3-OD7 applying the owner's clarification D-28), and section 3 shows that on pack and solar alone the kit does not carry it through a single
> night, whatever the solar rating, because the aged pack bridges 2.5 to 5.0 h of darkness; the solar path's rating is
> a second limit. Both are a layer-4 finding, reported to the owner as a consequence of D-06's one pack and of the studied in-case store, against the objective of D-28: design risk DR-01, assigned to layer 4.

### C29. section 7, the D-02a row (line 1040)

Rows and rulings: L3-OD5 `layer4-obligation`, D-36.

**Baselined text:**

> operate to specification inside the envelope; survive and recover at the margin |

**Proposed text:**

> operate to specification inside the envelope; survive and recover at the margin. **Decided on 30 September 2026 by owner ruling D-36 on row L3-OD5 (CFL-017 resolved):** Judged mode by mode against the project's maker sheets, CFL-017's collisions are between the requirements (D-02, D-02a, TEST-PLAN E5, with the pack fitted) and the current cell, the Samsung 35E, an engineering selection D-06's pack carries, with the current thermal design; the requirements are coherent. CFL-017 closes as a requirements conflict, FEA-008 carries the component-selection and thermal-design obligation to layer 4 mode by mode, and no temperature requirement is reduced, read as the kit's without its cells or reclassified. |

### C31. section 7, the D-20 row and the owner's rulings on layer 3 (line 1062)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD2 `both-kept`, D-33; L3-OD3 `unchanged`, D-34; L3-OD4 `reject`, D-35; L3-OD5 `layer4-obligation`, D-36; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> and the smallest justified changes presented for the owner's decision; unmet criteria stay visible |

**Proposed text:**

> and the smallest justified changes presented for the owner's decision; unmet criteria stay visible; the owner decided those changes on layer 3, in the eight rulings that follow (row L3-OD1's store is layer 4 architecture) |
> | D-28 | The owner's clarification of the energy and runtime requirement | RULED 30 Sep | quoted word for word in `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` and applied by the rulings that follow |
> | D-29 | The owner's clarification of CFL-017, the requirements apart from the current cell | RULED 30 Sep | quoted word for word in `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` and applied by the rulings that follow |
> | D-32 | M1's runtime: 48 to 72 hours, a design objective under the stated profile (row L3-OD7) | RULED 30 Sep | M1's runtime is 48 to 72 hours, the baseline design target under the explicitly stated operating profile of REQ-072, not a mandatory minimum; no external battery; HF and the tablet functions kept, HF available and not receiving in the profile, listening an additional use; the tablet's charging optional, consuming the kit's energy and reducing endurance, which the owner accepts. Neither Option A nor Option B of the runtime comparison is adopted, and no external store is recommended (D-28). |
> | D-33 | Both lid items kept, the QMX HF set and the tablet bracket (row L3-OD2) | RULED 30 Sep | Both approved lid items stay, the QMX HF set in its lid tray (appendix 32.50 item 16a) and the tablet bracket (item 16d); no function leaves the kit. The lid pack Option A(i) would add is layer 4 architecture (row L3-OD1). |
> | D-34 | REQ-016's approved solar window unchanged (row L3-OD3) | RULED 30 Sep | REQ-016's approved solar window stays unchanged; the 2S2P array into a 200 W stage is a layer 4 architecture proposal with Option A(i), which would need the owner's ruling to change REQ-016. |
> | D-35 | No deployment condition at layer 3 (row L3-OD4) | RULED 30 Sep | No deployment condition is stated at layer 3; the single benchmark plane is a modelling assumption of REQ-072's profile, not an operating restriction, and the open kit's stability goes with Option A(i)'s lid pack to layer 4. |
> | D-36 | CFL-017 closed as a requirements conflict; the cell and thermal design a layer 4 obligation (row L3-OD5) | RULED 30 Sep | Judged mode by mode against the project's maker sheets, CFL-017's collisions are between the requirements (D-02, D-02a, TEST-PLAN E5, with the pack fitted) and the current cell, the Samsung 35E, an engineering selection D-06's pack carries, with the current thermal design; the requirements are coherent. CFL-017 closes as a requirements conflict, FEA-008 carries the component-selection and thermal-design obligation to layer 4 mode by mode, and no temperature requirement is reduced, read as the kit's without its cells or reclassified. |
> | D-37 | M1's solar conditions: SC-37's mean day, one plane, TYP (row L3-OD6) | RULED 30 Sep | REQ-072 is judged under SC-37's reference mean day at Leiden on one plane, 40 degrees facing south, in the typical array build (TYP), the worst array build (WAB) a sensitivity; a benchmark, not a promise under every combination of loads and weather; no coverage target. |

### S06. section 7a, M1's mission duration row: its reversal (line 1101)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> Reversed by the owner's own setting |

**Proposed text:**

> Replaced by the owner's clarification D-28 (owner ruling D-32 on row L3-OD7): 48 to 72 hours, a design objective |


## `PRODUCT-BRIEF.md`

### B01. the status line of the head (line 3)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD2 `both-kept`, D-33; L3-OD3 `unchanged`, D-34; L3-OD4 `reject`, D-35; L3-OD5 `layer4-obligation`, D-36; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> **Status: layer 1 of the foundation baseline (MESHSAT-1357), BASELINED at `a9f212c7`,**

**Proposed text:**

> **Status: layer 1 of the foundation baseline (MESHSAT-1357), RE-ISSUED on the owner's rulings on layer 3 (the re-issue note below), pending its layer's review; BASELINED at `a9f212c7`,**

### B02. the head, after the rule of reopening: the re-issue note (line 15)

Rows and rulings: L3-OD7 `objective-48-72`, D-32; L3-OD2 `both-kept`, D-33; L3-OD3 `unchanged`, D-34; L3-OD4 `reject`, D-35; L3-OD5 `layer4-obligation`, D-36; L3-OD6 `mean-day`, D-37.

**Baselined text:**

> a change to it alone does not reopen this brief.

**Proposed text:**

> a change to it alone does not reopen this brief.
>
> **Re-issue on the owner's rulings on layer 3 (30 September 2026).** The owner's clarifications D-28 and D-29 answer rows
> L3-OD2 to L3-OD7 of `handover/layer3/OWNER-DECISIONS-L3.md` (owner rulings D-32, D-33, D-34, D-35, D-36 and D-37); row
> L3-OD1's store is layer 4 architecture. They restate requirements this brief traces to, which reopens it by the rule
> above: each passage they change is restated in place and names its row and ruling, the change record
> `handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` lists every passage, and its draft
> `handover/layer3/DEFINITION-REISSUE-DRAFT.md` keeps each one's baselined text. The owner's approval of that record is
> named in `handover/layer3/l3r2.yaml` (`definition_reissue`).

### S08. who it is for, the local end users: the tablet in the lid (line 60)

Rows and rulings: L3-OD2 `both-kept`, D-33.

**Baselined text:**

> and a rugged tablet (ATAK class) in the lid |

**Proposed text:**

> and a rugged tablet (ATAK class) in the lid, kept by owner ruling D-33 on row L3-OD2, its charging from the kit optional and reducing endurance (D-28) |

### S09. what it is not today: the night on the pack and solar input (line 171 to 179)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> - Not able to run through a night on its own pack and solar input. On the one pack of D-06 and the solar input alone
>   the kit does not run through a night at 52 N in any state: the aged pack holds about 108 Wh usable, which carries
>   the idle state of the runtime requirement (42.8 W) for about 2.5 h against nights of about 7 hours at midsummer and
>   about 16 at midwinter, and the shortest night in the lightest state asks about 150 Wh; and the 72 hours of mission
>   M1 ask for a panel of about 266 W on the design day, where the solar input takes at most about 100 W (`CONOPS.md`
>   M1; requirement REQ-072, part of prototype 1's core, reads FAIL at desk; the figures are PROVISIONAL or INFERRED
>   there). The routes that carry the night are an overnight input on the 9 to 36 V vehicle and shore entry, D-01's
>   deferred second pack, or a larger pack, which reopens D-06; until the owner rules on the last two, running through
>   a night needs that overnight input.

**Proposed text:**

> - Not able to run through a night on its own pack and solar input. On the one pack of D-06 and the solar input alone
>   the kit does not run through a night at 52 N in any state: the aged pack holds about 108 Wh usable, which carries
>   the idle state of the runtime requirement (42.8 W) for about 2.5 h against nights of about 7 hours at midsummer and
>   about 16 at midwinter, and the shortest night in the lightest state asks about 150 Wh; and the 72 hours of mission
>   M1 ask for a panel of about 266 W on the design day, where the solar input takes at most about 100 W (`CONOPS.md`
>   M1; requirement REQ-072, part of prototype 1's core, reads FAIL at desk; the figures are PROVISIONAL or INFERRED
>   there). Since the owner's clarification D-28 (owner ruling D-32 on row L3-OD7), M1's runtime is a design objective of 48 to 72
>   hours under a stated operating profile, the store stays inside the Peli 1450 with no external battery, and the
>   modelled baseline, the studied in-case candidate included, misses the objective even without tablet charging: design
>   risk DR-01, assigned to layer 4, where the store's arrangement is settled.

### B18. what the first prototype has to show: the qualification margins (line 207 to 209)

Rows and rulings: L3-OD5 `layer4-obligation`, D-36.

**Baselined text:**

> The test plan's hot and cold levels beyond the envelope are
> qualification margins with two pass lines: operate to specification inside the envelope, survive and recover at
> the margin.

**Proposed text:**

> The test plan's hot and cold levels beyond the envelope are
> qualification margins with two pass lines: operate to specification inside the envelope, survive and recover at
> the margin. The owner decided row L3-OD5 on them (owner ruling D-36 on row L3-OD5, CFL-017 resolved: "Judged mode by mode against the project's maker sheets, CFL-017's collisions are between the requirements (D-02, D-02a, TEST-PLAN E5, with the pack fitted) and the current cell, the Samsung 35E, an engineering selection D-06's pack carries, with the current thermal design; the requirements are coherent. CFL-017 closes as a requirements conflict, FEA-008 carries the component-selection and thermal-design obligation to layer 4 mode by mode, and no temperature requirement is reduced, read as the kit's without its cells or reclassified.").

### S10. the open items table: L-02, M1's duration (line 309)

Rows and rulings: L3-OD7 `objective-48-72`, D-32.

**Baselined text:**

> for which the session took 72 hours as a planning value under the owner's standing rule (SC-21, which governs it under that rule, is recorded as the session's and closes L-02 in the requirements registry; the owner's own setting replaces it; `handover/ENGINEERING-QUESTIONS.md` EQ-13)

**Proposed text:**

> for which the owner set 48 to 72 hours as a design objective under a stated operating profile (the clarification D-28, owner ruling D-32 on row L3-OD7), replacing the session's planning value SC-21 (`handover/ENGINEERING-QUESTIONS.md` EQ-13)

## Rows proposed for `handover/DEFINITION-STATUS.md`'s current values

The statements below name the design as generated before the answers; `handover/DEFINITION-STATUS.md`'s rule keeps them in the baseline and carries their current value on that page, as it carries M1's reading. The rows proposed for it:

| Row | Where | Current value |
|---|---|---|
| DC-L3-M1 | `CONOPS.md` section 3 (M1) and sections 6 and 7a; `PRODUCT-BRIEF.md`, the power bullet and the M1 bullet | REQ-072 reads FAIL (DESK_REVIEW, SCHEMATIC phase, release effect MUST_JUSTIFY) when the re-issue is written; its latest evidence entry in the requirements registry: "The modelled baseline (the owner's clarification D-28: reported honestly, the shortfall recorded prominently), read from v2/docs/records/l3batt/runtime.out, the output of v2/docs/records/l3batt/runtime.py (stream l3batt, checked), by v2/docs/records/l3r5/runtime_reader.py for D-32: with HF and the tablet kept and no tablet charging, battery-only from full, D-06's 4S3P pack runs 2.52 h at +20 C (1.04 h at -10 C) and the studied in-case candidate, Option A(i)'s base 4S6P and a 4S9P lid (544.4 Wh usable aged at +20 C), 12.71 h (5.24 h at -10 C); solar-assisted on the mean day in TYP the candidate stops at 05 UTC of the first night, hour 23 from a 06 UTC start and hour 11 from an 18 UTC start, as drawn (266.7 Wh unserved at 48 h, 494.7 Wh at 72 h) and on the hypothetical corrected path (102.2 Wh at 48 h, 165.7 Wh at 72 h, NOM) alike, in 0 of 864 past September windows at 48 h and 0 at 72 h. The objective's lower end is missed even without tablet charging: design risk DR-01, assigned to layer 4. The corrected path is not implemented. Reads FAIL." |


## The proposed documents

The re-issue applied in memory to the baselined files; nothing is written into them.

| Document | Baselined sha256/16 | Proposed sha256/16 | Passages restated |
|---|---|---|---|
| `v2/docs/CONOPS.md` | `6cb7b241cb84d729` | `d9ae0d8a30c9eb41` | 12 |
| `v2/docs/PRODUCT-BRIEF.md` | `85513b92ed0daf55` | `a567a7d696098d7e` | 6 |
