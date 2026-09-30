accepted: yes
tip: 05ba0cf0b39d4e5dc806d729bf1925e96c5305e2

# CHECK-1 of fnd/l3batt: the runtime-and-battery comparison (stream l3batt, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 14:30 CEST.
- **The branch** is `fnd/l3batt`, tip `05ba0cf0` (confirmed): one commit on main `db757e6b`.
- **The clone.** A `--no-local --single-branch` clone (`_scratch/chk-l3batt1`, removed after the check), with
  `int18-evidence-1f34bf92.tar` extracted and the l3batt worktree's 26 ignored vendor files copied in. All of them are
  ignored; `git status` stayed clean.
- **The checker's own figures:** `indep_l3batt.py` beside this file, output `indep_l3batt.out`. It uses the checker's
  `../chk-energy/indep_balance.py` and `indep_round2.py`, and imports no record script. The array ratios are a1solar's
  inputs.
- The checker wrote none of it. Prototype design: nothing is built, bought, powered or measured.

## Files verified at the tip (working tree equal to the blob)

```
226e422a184a52f4255502d8355f6482330ff91ab71970ebf0040be9bb9d24ba  .gitignore
339d8d0fb5af2c2653e56a17c984dbb3ecae889e9663b51cba28ae6ae5f09a0c  v2/docs/records/l3batt/COMPARISON.md
d2f9c2d9db177c03a57f8c60fd04cdb3b68dab6bdd512fe622123ba11ea35d7c  v2/docs/records/l3batt/PROVENANCE.md
940cc1d678989ee993b3fff141a7c863d11a4687e9b1ff9c8d06d24f7b3167a9  v2/docs/records/l3batt/SHORTLIST.md
366e06ae4fcf6c010669b790093c11d16e8ae71bf24b8c41e1d78ead9868e55f  v2/docs/records/l3batt/fetch_held_back.py
9da1e3e99762403f7ae341d3be91c4d9e0286fa90f6f7e3d86c4913c758a19fd  v2/docs/records/l3batt/lid_21700.out
f89ab31eb940f9da78b24b79424f60320e494e5b41dd61478657fb3cf33bf5f5  v2/docs/records/l3batt/lid_21700.py
e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218  v2/docs/records/l3batt/load_trace.out
a70dad44bf7098af3d3198d0eb82a8d82f4b31a5149636c6c780bd0e01350484  v2/docs/records/l3batt/load_trace.py
2eec9d5876b511b57982ecd3fd0f68bfc38af8a54f1e8ed43e1231656bdf7909  v2/docs/records/l3batt/runtime.out
9ae70f54463fa7d05b495c1cc0055b880709bd5d76c056682626773ac617ac96  v2/docs/records/l3batt/runtime.py
8b08963c0a198fd391ed7e62388be12cbd14c38d7b587982f9800b15c6821b4a  v2/vendor/battery/molicel-inr21700-p45b-v1.2.pdf
78f9f6bc39617fa6fa70c67dd67bda65140bc9136877d68aea399758edb6124f  v2/vendor/sources.txt
```

## Blocking items

None. Every decisive figure recomputes, and the provenance finding holds.

## Minors

1. **The HF-receiving sensitivity should be in the options table in Wh.** Section 2c gives it in cells only, and the
   owner's decision figures (about +80 Wh for A, +120 Wh for B) are for the approved profile, where the QMX receiver is
   unpowered. With the receiver's 1.14 W, the checker gets the author's lid counts and in usable Wh at the lid:

   | Requirement | NOM | WE |
   |---|---|---|
   | 48 h | +84 Wh | +122 Wh |
   | 72 h | +95 Wh | **+187 Wh** |

   So if the owner means HF to listen through M1, Option B's store is about 190 Wh at TYP, not 120 Wh. See also
   "What holds", item 2.
2. **Tablet charging is not quantified anywhere.** The tablet runs on its own battery; the kit's USB-C PD outlet, its
   only charge path, is off in every state. So over 48 or 72 hours the tablet's use lasts only as long as its own
   battery. The options table's "HF and the tablet kept; no duty reduced" is true against the approved profile (neither
   was ever powered in PS-IDLE-SPEC). The table should say in the row itself: "kept in the kit and available; HF not
   receiving and the tablet not charged in this profile". A tablet-charging allowance should be stated or explicitly
   left to the owner.
3. **An external pack joined at VBAT is not outside D-20 either.**
   - **The DC entry.** The tree's own EQ-13 route (b), which D-20 answered, is "an overnight input on the 9 to 36 V
     entry (a vehicle, a shore supply or any DC source inside the entry's window, an external battery included)". So an
     external pack through the DC entry is exactly D-20's "external DC source": the page is right that this revisits D-20.
   - **The VBAT join.** A pack joined at VBAT through a new wall connector is not in EQ-13's list. It is closest to route
     (d), "a larger pack: the owner's (it reopens D-06; the case never changes)". D-20 names "the pack of D-06" among the
     approved constraints.
   - **What to add.** Section 5 item 2 should say that the VBAT join reopens D-06 (EQ-13 (d)) and so is also the owner's
     ruling, and cite EQ-13 (b) for the DC-entry case.
   - **The wording.** Section 3's "it **meets** D-20" reads as "satisfies". "It falls under D-20's clause" says what is
     meant.
4. **The "present" store is itself a pending owner decision.** Base 4S6P plus lid 4S9P is Option A(i)'s arrangement A,
   not the ruled pack. D-06 is the one 4S3P, and D-20 lists "the pack of D-06" as an approved constraint. The options
   table's "Present: base 4S6P + lid 4S9P" should say it rests on the A(i) decision, and that the upgrade is added on top
   of that.
5. **The provenance table can add two facts.** Neither changes its finding.
   - **The first appearance.** "72 hours" first appears in the tree at `de59686e` (27 Sep 2026 07:48), before
     `95e078a1` (12:34). It sits in the H1.1 handover's candidate patches, "every patch is an UNACCEPTED candidate": the
     layer 2 closer's session choice SC-L2-05 ("72 hours on the PS-IDLE-SPEC energy basis"), which became SC-21.
     `95e078a1` is correctly the first commit to CONOPS and the registry.
   - **Review A.** The closer restated M1 "after Review A, B3", and Review A is an AI review (`REVIEW-A-LAYER-2`, "an AI
     review"). B3 concerned M1 and the night, not the duration; the 72 hours were already the closer's.
   - **Searched, nothing further found:**
     - `git log -S` over all refs for "72 hours", "72-hour", "72 h", "72h", "three days", "3 days" and "seventy": the
       earlier hits are adhesive cure times, JLC lead times and prose;
     - the appendix and the owner decision sheets;
     - EQ-13;
     - the fieldkit memory directory.
6. **The scratch command left a file in the worktree.** The l3batt worktree holds one ignored file that the evidence
   archive does not: `v2/ecad/tools/__pycache__/panel1450.cpython-311.pyc`, written 13:57:42 today, before the commit.
   It is a bytecode cache from importing the generator's `panel1450`: harmless, never committed, and nothing tracked
   changed (`git status` clean). But "touched nothing in the tree" is not literally true. Delete it, or say so.
7. **Cost and stock carry no label.** The figures (Battery Junction, IMR Batteries, Voltaplex, 30 Sep 2026) are readings
   of distributor pages that are not filed. The column header dates them; a "(read, not filed)" in the header completes
   the label set.

## What holds

**1. Provenance.**
- **The registry lines, quoted exactly:**
  - D-06 (lines 475 to 486): "the mission duration for the solar energy balance is set later by the owner";
  - SC-21 (1635 to 1645, `authority: SESSION`): "not a sourced figure";
  - D-20 (697 to 712): "with their specified duration", no number, a registry summary;
  - D-21 (713 to 727) with `OWNER-INSTRUCTION-2026-09-30.md` line 24: "Preserve the approved 72-hour mission" in the
    owner's words, and line 127, the session's reading.
- **The finding stands:** no owner statement introduces 72 hours, so its provenance as the owner's is UNVERIFIED. The
  figure is the session's, and the owner referred to it on 30 September. See minor 5.

**2. The load trace.**
- **The sum.** 39 rows sum to 42.82 W. By tier: S 16.79, R 11.34, D 6.29, T 8.40. Bounds 33.1 and 82.8 W
  (POWER-THERMAL.md section 4's PS-IDLE-SPEC row: "33.1 / **42.8** / 82.8").
- **HF.** In `pwr_budget.py` the "QMX HF" load has TYP and ALLTX entries and no IDLESPEC entry. So in PS-IDLE-SPEC only
  "QMX USB and HDMI 5 V" (0.32 W, declared) is powered, and the receiver's 0.96 W at the load (1.14 W at the battery) is
  PS-TYP.
- **The tablet** has no load row; the outlets are "off in every state".
- **What the profile preserves:** HF and the tablet as installed, available functions, not their operation through the
  mission. It is the approved profile the owner asked to use ("the same approved functions and operating profile"), so
  the basis is correct.
- **The fairer basis** if the owner means HF to listen is the receiver-on figure (minor 1). CONOPS M1 requires only "at
  least one bearer", so HF listening is the owner's call.

**3. The first-night finding: reproduced exactly on the checker's balance.**
- **The dusk store:** base 218.4 Wh at +20 C and lid 284.2 Wh at 13.23 C, 502.6 Wh together.
- **The night:** 14 hours at or under 60 W/m2 (UTC 17 to 06). The night's deficit at the node is 564.7 Wh (TYP, NOM),
  599 Wh at a flat 42.8 W.
- **The runs.** Every case, at 48 h and 72 h, stops at 05 UTC on the first night: hour 23 from 06 UTC, hour 11 from
  18 UTC. Unserved energy is identical to 0.1 Wh (48 h: 266.8, 102.2, 105.5, 104.6, 112.5 Wh TYP).
- **Coverage:** 0 of 864 windows at 48 h and at 72 h (NOM, TYP), recomputed.
- **The store needed** (least lid, base held at 4S6P, COMB, both starts):

  | Requirement | TYP | WAB |
  |---|---|---|
  | 48 h, NOM | 4S11.16P, +68.1 Wh | |
  | 72 h, NOM | 4S11.16P, +68.1 Wh | |
  | 48 h, WE | 4S11.52P, +79.5 Wh | 4S12.44P, +108.5 Wh |
  | 72 h, WE | 4S12.68P, +116.1 Wh | 4S14.49P, +173.5 Wh |
  | 72 h, NOM at 0.90 | 4S12.70P, +117.0 Wh | |

- **Why A and B differ so little.** At NOM TYP each day refills the packs, so only the first night binds and 48 h and
  72 h need the same +68 Wh. At WE or at the 0.90 bracket, the later nights start short, so 72 h asks about 36 Wh more.
  The author's explanation is right.

**4. Battery-only endurance.**
- **4S3P alone:** 107.9 / 44.5 Wh, 2.52 / 1.04 h. The checker's figures are identical.
- **Base plus lid:** 544.4 / 224.5 Wh, 12.71 / 5.24 h. The checker gets 546.1 / 225.2 Wh without the lid path's loss and
  drain, which the author charges.
- **The cold factor** is from the 35E sheet (`samsung-35e-orbtronic.pdf`, 7.5): "-10 C 40 %, 23 C 97 %" at 3,400 mA,
  so 0.4124. It is used as a lower bound at the kit's 0.2 A a cell, as the page says.

**5. The shortlist.**
- **P45B, filed** (sha `8b08963c`): 4300 mAh and 15.5 Wh minimum, 21.55 x 70.15 mm, 70 g max, discharge -40 to 60 C
  (Version 1.2). No rights text.
- **The held sheets are present and not committed** (`v2/vendor/battery/held/` is ignored, with a `.gitignore` line
  added):
  - 50E (`f2feac1f`): "SAMSUNG SDI Confidential Proprietary", 4,900 mAh min;
  - M50LT (`1408ad2c`): "pre-discussion", 17.6 Wh, -10 C at least 70 % of Whmin;
  - NH2054HD34 (`5be44725`): "Statement Of Confidentiality", 6136 mAh, OCD 8250 mA.
- **The lid count.** `lid_21700.out` reproduces a1mech's `lid_pack_a1.out` byte for byte, then 27 places and 4S6P for
  each 21700 (two layers 45.66 / 45.10 / 45.46 mm against 44.39 mm).
- **The base growth checks:** 2 x 70.15 + 3.0 against 133.5 is +9.8 mm; 3 x 21.55 + 1.0 against 56.65 is +9.0 mm; the
  height is +6.0 mm. The room checks against a1mech section 6's worst less 1.0: M5 east 0.77, M4b 6.38, M6 east
  2.66 mm.
- **Cell against pack:** 723.6 Wh of cells against 544.4 Wh usable (75 %).

**6. The options and the recommendation.**
- **Option A is correctly shown as no relief:** the first night fails at either length, and A saves about 36 Wh only at
  WE or 0.90, nothing at NOM TYP.
- **The recommendation** (B only with an authorised external store of about 120 Wh at TYP, or about 190 Wh with WAB, and
  the corrected path; otherwise M1 recorded not met) is quantified and marked PROPOSAL. See minors 1 and 3 on its figure
  and its D-20 framing.

**7. Labels, hygiene and reruns.**
- **Labels.** MAKER, MODELED and INFERRED are used correctly (minor 7 on cost).
- **The added lines** carry no U+2013 or U+2014, no host names and no user paths.
- **Nothing under `v2/ecad/` changed**, so `pcb_requirements.yaml` is untouched.
- **The commit** is in the owner's name with no trailer.
- **Reruns.** `runtime.out`, `lid_21700.out` and `load_trace.out` rerun byte identical in the clone.
- **The scratch command's residue:** see minor 6.

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| PS-IDLE-SPEC, 39 loads | 42.82 W; S 16.8, R 11.3, D 6.3, T 8.4 | 42.82 W; 16.79, 11.34, 6.29, 8.40 |
| Battery only, 4S3P | 107.9 / 44.5 Wh; 2.52 / 1.04 h | 107.9 / 44.5 Wh; 2.52 / 1.04 h |
| Battery only, base + lid 4S9P | 544.4 / 224.5 Wh; 12.71 / 5.24 h | 546.1 / 225.2 Wh without the lid path loss; 12.76 / 5.26 h |
| Dusk store | 218.4 + 284.2 = 502.6 Wh | 218.4 + 284.2 = 502.6 Wh |
| Night | 14 h at or under 60 W/m2 | 14 h; deficit 564.7 Wh at the node (TYP NOM) |
| First stop | 05 UTC, hours 23 / 11, every case | the same |
| 72 h unserved, NOM / WE / WE90 TYP | 165.7 / 169.2 / 184.1 Wh | 165.7 / 169.2 / 184.1 Wh |
| Need, 48 h NOM / WE TYP | +68.1 / +79.6 Wh | +68.1 / +79.5 Wh |
| Need, 72 h NOM / WE / NOM90 TYP | +68.1 / +116.2 / +117.0 Wh | +68.1 / +116.1 / +117.0 Wh |
| Need, WAB: 48 h WE / 72 h WE | +108.6 / +173.6 Wh | +108.5 / +173.5 Wh |
| HF receiving, 72 h WE TYP | 4S14.92P, +23.7 cells | 4S14.92P, +23.7 cells, +186.9 Wh |
| Coverage, 48 h and 72 h | 0 of 864 | 0 of 864 |
| 21700 base growth | +9.8 / +9.0 / +6.0 mm | +9.8 / +9.0 / +6.0 mm |
| NH2054HD34 usable | 67.2 Wh at +20 C | 6.136 x 14.4 x 0.80 x 0.95 = 67.2 Wh |

Rerun from this folder against a checkout of the tip with the archive and held sheets present:
`python3 indep_l3batt.py <checkout>`.
