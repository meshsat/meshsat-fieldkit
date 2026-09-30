accepted: yes
tip: 83577a13aaa7a4809b156e9e6d037270aa1a70aa

# CHECK-2 of fnd/l3batt: delta check of the second issue (stream l3batt, MESHSAT-1357)

**An AI check, not a qualified review.** 30 September 2026, 14:40 CEST.
- **The branch** is `fnd/l3batt`, tip `83577a13` (confirmed), one commit on CHECK-1's `05ba0cf0`.
- **Scope:** `git diff 05ba0cf0..83577a13` only, against CHECK-1's minors 1 to 7.
- **The clone.** A `--no-local --single-branch` clone (`_scratch/chk-l3batt2`, removed after the check), with
  `int18-evidence-1f34bf92.tar` extracted and the l3batt worktree's ignored vendor files copied in. `git status` stayed
  clean.

## Files verified at the tip (working tree equal to the blob)

```
226e422a184a52f4255502d8355f6482330ff91ab71970ebf0040be9bb9d24ba  .gitignore
6b6ee53ea01e908ca3c78a0f00ab6ba6d386176b1398d4f3e2b60518c7799c8b  v2/docs/records/l3batt/COMPARISON.md
9b92e4213445652a3a1d5d693b727338b5e88f7e943536047b20814d45820695  v2/docs/records/l3batt/PROVENANCE.md
6a943a1fb0d47edf1977e39b0c1801f9319abdb8087015ccbea3a1c4a784e28c  v2/docs/records/l3batt/SHORTLIST.md
366e06ae4fcf6c010669b790093c11d16e8ae71bf24b8c41e1d78ead9868e55f  v2/docs/records/l3batt/fetch_held_back.py
9da1e3e99762403f7ae341d3be91c4d9e0286fa90f6f7e3d86c4913c758a19fd  v2/docs/records/l3batt/lid_21700.out
f89ab31eb940f9da78b24b79424f60320e494e5b41dd61478657fb3cf33bf5f5  v2/docs/records/l3batt/lid_21700.py
e35e62483b67fbe71bf89b819f6be46173ce708a8a62c683905d55a37ad4c218  v2/docs/records/l3batt/load_trace.out
a70dad44bf7098af3d3198d0eb82a8d82f4b31a5149636c6c780bd0e01350484  v2/docs/records/l3batt/load_trace.py
87d9c1ee590597638c57aa97c384c217af9eb36044a2db39e27194a88047fc13  v2/docs/records/l3batt/runtime.out
885bd4fadf9000cf45f7f66e2ba518b7b390e1092e9a0246e6f6a52c760897ee  v2/docs/records/l3batt/runtime.py
8b08963c0a198fd391ed7e62388be12cbd14c38d7b587982f9800b15c6821b4a  v2/vendor/battery/molicel-inr21700-p45b-v1.2.pdf
78f9f6bc39617fa6fa70c67dd67bda65140bc9136877d68aea399758edb6124f  v2/vendor/sources.txt
```

## Blocking items

None.

## Minors

None new.

## What holds

**1. HF receiving, in Wh.**
- **Where it now appears:** section 2c, the options table's store row and section 5 item 2 carry +84.2 / +94.9 Wh (NOM)
  and +122.2 / +187.1 Wh (WE), for 48 / 72 h. `runtime.out` 3 prints them beside the cells.
- **Recomputed** on the checker's balance at the printed lid counts and each run's own load (42.8 W plus 1.14 W, plus the
  WE drain): +84.3, +95.1, +122.2 and +186.9 Wh. The checker's figures use the lid counts rounded to two places, where
  one hundredth of a P is worth about 0.3 Wh, which accounts for the differences.

**2. The profile's limits.**
- **The functions row** now reads "kept in the kit and available ... HF is not receiving and the tablet is not charged in
  this profile".
- **Tablet charging is marked UNQUANTIFIED.** REQ-011's acceptance reads "A tablet model is named ... the tablet charges
  from the USB-C outlet", and SC-45 leaves "the model is a part pick" (registry lines 1368 and 6844 to 6848): no model is
  named.
- **The one bound held** is the outlet's contract, 15 V at 3 A, 45 W (`pwr_budget.py` line 303; the PDO stage at 0.93,
  line 139, gen_sch_a.py's declared floor). 45 / 0.93 is 48.4 W at VBAT: the stated "about 48 W", labelled INFERRED,
  above the whole 42.8 W profile.

**3. The join wording.**
- Section 3 and section 5 item 2 now read "Neither way of joining it satisfies D-20; each is the owner's ruling to
  reopen".
- Through the DC entry, it "falls under D-20's clause". This is cited to EQ-13 route (b), whose "an external battery
  included" is quoted correctly.
- Joined at VBAT, it "reopens D-06". This is cited to EQ-13 route (d), with D-20's "the pack of D-06".
- The ambiguous "meets D-20" is gone.

**4. The baseline.**
- The options table reads "Baseline: Option A(i)'s base 4S6P + lid 4S9P ... It is not the ruled pack", with D-06's
  4S3P, D-20's constraint and "A(i) itself awaits the owner's L3-OD1".
- It reads "Every upgrade below is added on top of A(i)".
- Section 5 repeats "The baseline itself is pending".

**5. The provenance additions.**
- **Row 2a** names `de59686e` (27 Sep 07:48) and `v2/docs/handover/candidates/hc2.patch`, with its README's "Every patch
  here is an UNACCEPTED candidate, not design".
- **SC-L2-05** is named as the layer 2 closer's session choice that became SC-21.
- **Review A** is named as "an AI review".
- The finding text now says the figure first appears at 07:48 as SC-L2-05. Row 2 is scoped to CONOPS and the registry
  "themselves". The finding is unchanged.

**6. The scratch cache.**
- `v2/ecad/tools/__pycache__/` is gone from the l3batt worktree. Its ignored files, less the held vendor sheets, now
  equal the evidence archive's list exactly (0 extra).
- The worktree is clean at `83577a13`.
- Nothing in the tree claims "touched nothing": `git grep` finds only "a scratch re-run" in `runtime.py`, which is
  accurate.

**7. The cost labels.** The column is headed "a distributor page read on 30 Sep 2026, not filed", with a note below the
table.

**The output and hygiene.**
- **`runtime.out`:** its only change is one line, the HF-receiving sensitivity with the Wh added. It reruns byte
  identical at the tip.
- **The added lines** carry no U+2013 or U+2014, no host names and no user paths.
- **The diff** touches only five files in `v2/docs/records/l3batt/`. Nothing in `v2/ecad`, `v2/vendor` or `.gitignore`
  changed, so no held file is committed and `pcb_requirements.yaml` is untouched.
- **The commit** is in the owner's name with no trailer.

## Figures beside theirs

| Figure | Theirs | Checker |
|---|---|---|
| HF receiving, 48 h NOM / WE | +84.2 / +122.2 Wh | +84.3 / +122.2 Wh |
| HF receiving, 72 h NOM / WE | +94.9 / +187.1 Wh | +95.1 / +186.9 Wh |
| The outlet's bound at VBAT | about 48 W | 45 / 0.93 = 48.4 W |
