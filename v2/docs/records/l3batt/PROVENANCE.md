# The provenance of M1's 72 hours (stream l3batt, MESHSAT-1357, 30 September 2026)

The owner's instruction of 30 September 2026:

> "Establish the requirement's origin. Find the original instruction or explicit owner approval introducing 72 hours.
> Show the exact wording, date and source behind D-20 / M1 / REQ-072. Distinguish my statements from assistant
> recommendations and later summaries. If the originating approval cannot be found, mark its provenance unverified and
> continue the comparison."

## Finding

**No owner statement introducing 72 hours was found in the tree.** The figure first appears as the session's choice
SC-21 on 27 September 2026. It was taken under the owner's standing rule of 26 September 2026 in place of a setting that
D-06 reserved for the owner.
- **D-20 (28 September)** preserved M1 and REQ-072 "with their specified duration" without stating a number. The tree
  holds that ruling as the registry's summary, not in the owner's own words.
- **D-21 (30 September)** is the owner's own words, "the approved 72-hour mission". The instruction file records that
  phrase as the session's reading: "is read as approved by the owner".

**Provenance of 72 hours as the owner's: UNVERIFIED.** It is the session's figure, preserved by D-20 and referred to by
the owner on 30 September. The comparison continues on that basis.

## The sources, exactly

Who spoke is the classification: **OWNER** words, a **SESSION** choice, or a **SUMMARY** written later by a session.

| # | Date | Source (file, line) | Exact wording | Who |
|---|---|---|---|---|
| 1 | 26 Sep 2026 | `v2/ecad/tools/pcb_requirements.yaml` lines 475 to 486, owner ruling D-06 "pack size and runtime" | "Missions longer than the pack rely on vehicle or solar input. The runtime requirement is stated as battery-only hours in an idle and a typical mode at +20 C for an aged pack; the mission duration for the solar energy balance is set later by the owner." | OWNER ruling as the registry records it. It **reserves** the duration and sets no figure |
| 2 | 27 Sep 2026 12:34 CEST | commit `95e078a1` ("the layer 2 and 3 closers' registry change"), the first commit adding "72 hours" to `v2/docs/CONOPS.md` and the registry | CONOPS: "### M1. Remote site relay on pack and solar (72 hours)" | SESSION (the layer 2 and 3 closers) |
| 3 | 27 Sep 2026 | `pcb_requirements.yaml` lines 1635 to 1645, session choice SC-21, `authority: SESSION`, `under: standing-rule` | question: "M1's mission duration for the pack-plus-solar balance (L-02)." taken: "72 hours on the PS-IDLE-SPEC energy basis (42.8 W)." why: "The planning horizon of a relay site without infrastructure, chosen from the use case (not a sourced figure); D-06 left it for the owner to set later and the standing rule forbids asking." | **SESSION: the origin of the figure** |
| 4 | 27 Sep 2026 | `pcb_requirements.yaml` lines 4229 to 4235, L-02, `closed_by: SC-21` | "SC-21 governs it: under the owner's standing rule of 26 September 2026 the session set 72 hours, recorded as the session's, and the owner's own setting replaces it whenever he gives one" | SESSION record |
| 5 | 27 Sep 2026 on | `v2/docs/CONOPS.md` line 164 (M1) and line 1101 (section 7a) | "The duration is 72 hours, taken by the session under the owner's standing rule of 26 September 2026 (section 7a) in place of the setting D-06 reserved for the owner, which replaces it whenever he gives one." | SESSION |
| 6 | 27 Sep 2026 on | `pcb_requirements.yaml` line 7403, REQ-072 | "For mission M1 (CONOPS section 3), the pack plus the solar input keep the kit running in PS-IDLE-SPEC for M1's 72 hours (SC-21) on the reference day of SC-37, starting from a full, aged pack (REQ-014)." | SESSION requirement text, citing SC-21 |
| 7 | 28 Sep 2026 | `pcb_requirements.yaml` lines 697 to 712, owner ruling D-20 | "OD-02 of the decision sheet of 28 September 2026, as corrected by the owner the same evening: the original mission M1 and requirement REQ-072, with their specified duration and operating conditions, are preserved; an external DC source may remain optional, but requiring it overnight is not an acceptable substitute." | OWNER ruling as a registry **SUMMARY**. The tree holds no verbatim text of the correction. It preserves the duration and does not state it |
| 8 | 30 Sep 2026 | `v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md` line 24 (quoted, in part, by the coordinating session), owner ruling D-21 (registry lines 713 to 727) | "Preserve the approved 72-hour mission and approved functions unless I explicitly authorize a change." | **OWNER words**. The first place in the tree where the owner uses the figure. He calls it "approved"; no approval act is found before it |
| 9 | 30 Sep 2026 | the same file, line 127 | "M1's 72 hours, first taken by the session as SC-21 and preserved with M1's duration and operating conditions by D-20, is read as approved by the owner." | SESSION reading (a SUMMARY) |
| 10 | 30 Sep 2026 | the owner's instruction of this task (not yet filed in the tree) | "I am questioning the 72-hour requirement. Evaluate alternatives before asking me to sacrifice functions or accept restrictive deployment conditions." | OWNER words |

**Searched, with no owner statement of 72 hours found:**
- `v2/docs/MESHSAT-709-geometry-appendix.md`: no "72 hours", "72 h" or "72-hour" at all;
- `v2/docs/OWNER-DECISIONS-OPEN.md` and `OWNER-DECISIONS-2026-09-11.md`: no mention;
- the session's decision sheets (`records/energy/DECISION-OPTIONS.md` and `DECISION-PARAGRAPH.md`, "the 72-hour relay
  mission"; `handover/layer3/OWNER-DECISIONS-L3.md` row L3-OD6): these are session drafts using SC-21's figure;
- owner rulings D-22 to D-25 (registry lines 729 to 800);
- `v2/docs/handover/ENGINEERING-QUESTIONS.md` EQ-13, which calls it "the session's 72 hours (SC-21, which the owner may replace)".

## What follows for the comparison

- M1's duration is a **session figure the owner has since referred to**. It is not a sourced planning figure: SC-21
  itself says "not a sourced figure".
- **Option A (48 hours required, 72 desired) and Option B (72 hours required) are both open to the owner.** Neither
  changes any approval the tree shows him giving.
- **D-20's clause still binds either option** unless the owner revisits it: "an external DC source may remain optional,
  but requiring it overnight is not an acceptable substitute". It bears on the external battery proposals of
  `COMPARISON.md`.

The author's record, AI arithmetic on the tree's text. Not a qualified review and not the independent check.
