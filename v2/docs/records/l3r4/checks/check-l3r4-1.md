mergeable: no

# CHECK-1 of layer 3 round 4 (`fnd/l3r4` at `3afdc2d6`): the definition re-issue prepared (L3-C26)

An AI check by a session that wrote none of the round, not a qualified review. Written 30 September 2026, 08:30 CEST.
Scope: the one commit `3afdc2d6` on main `8fec0733` (nine files: `v2/docs/records/l3r4/` with `reissue.py`,
`PASSAGE-MAP.md`, `README.md` and `apply_layer_status_l3_r4.py`, `v2/ecad/tools/tests/test_l3r4.py`, and one row each
in `l3r2.yaml`, `L3-RECONCILIATION.md`, `LAYER-STATUS.md` and `v2/docs/records/README.md`). Everything below was run
in a `--no-local --single-branch` clone of `fnd/l3r4` with the set 17 evidence archive (`int17-evidence-de11cc4e.tar`)
installed, or read from it. Nothing was committed or pushed; the clone is removed.

## Verdict

One blocking item: the passage map leaves out the statements of the single pack's circuit as generated, and the head
note the draft adds turns them into statements about two packs that the generated circuit does not carry. The
generator, its refusals, the change record's binding, the layer status script, the gates and the integrator run order
all hold. Nine minors.

## Blocking

**B1. The single pack's circuit as generated is neither restated nor read through `DEFINITION-STATUS.md`, and the head
note makes it read as two packs.** The map treats the QMX case correctly: 19 statements of the design as generated
(its rail, EMCON enable, bank and port, load row, lid tray) are CURRENT, they stay, and the draft proposes the row
DC-L3 for the status page, as `DEFINITION-STATUS.md`'s rule asks ("a circuit correction updates this page and the
records it names, not the baseline"). Row L3-OD1 `approve` makes the same kind of statement inconsistent for the
store, and the map has no CURRENT passage for it. `CONOPS.md` states the one-pack circuit as generated in several places
the re-issue does not touch, for example (baselined line numbers, text read from the file):

- line 313, the Charging row: "the BQ25731 ... regulates the charge into the 4S pack beyond its sense resistor `R17`,
  and the kit's loads sit on the charger's system node" (C20 restates only the row's 4 A clause);
- lines 590 to 594: board E's `U10` is "the pack gauge's only SMBus host (`gen_sch_e.py` line 264, `J_SMB` ...)",
  on "the buck `U12`, line 565, its EN tied to the pack node `CELL_F`";
- lines 537 to 539: the pack's voltage and discharge current read "in place of the gauge" from the one charger's
  ADCVBAT and ADCIDCHG through `R17`;
- lines 930 to 933: K3's "pack current at most 9.0 A" and "the pack chain has to carry its short-time rating at 18 A
  for 60 s (PWR-F12)".

The proposed head note (C02, and B02 in the brief) says: "Where a passage this re-issue does not restate says 'the
pack', it reads as each of the two packs of owner ruling D-27 on row L3-OD1, as that ruling reads the requirements."
D-27's own clause is about requirements ("Where a requirement says 'the pack', it applies to each pack unless it names
one"); the note extends it to every passage. Read that way, line 313 has one BQ25731 charging each of two packs, against
D-27's "each with its own charger path and gauge", and lines 590 to 594 give a second gauge a host and a node the
generated circuit does not have. The change record repeats it ("Every other mention of 'the pack' reads as each of the
two packs"). An engineer approving the change record would be approving statements about a circuit that does not
exist, and the owner has no way to see it. This is item 1's "the single pack" and the DEFINITION versus CURRENT split.

Remedy (small): in C02 and B02, keep the reading of D-27 for passages that state a requirement, intention or condition,
and add the sentence the QMX already has: passages that state the circuit as generated for one pack (one charger, one
gauge, one pack node) state the design before owner ruling D-27, with the current values on `DEFINITION-STATUS.md`;
and either list those lines as CURRENT passages under L3-OD1 `approve` with a proposed DC row, as for the QMX, or at
least propose the DC row naming the sections (4 Charging row, 4a, 4c, 4e, 4f and 6's K3). Regenerate the map and rerun
the tests.

## Minors

1. **Recording the approval makes the bound draft out of date.** The draft names the whole registry's sha256/16, so the
   approving ruling itself changes it. On my recommended-answers copy, `reissue.py --check` read the draft and record
   current; after adding one ruling with `decides: definition_reissue` it read OUT OF DATE (exit 1), and a regeneration
   changed both files (draft `4500eed23b45bf6f` to `7dc3df6a31592763`, record `af982a2447311333` to
   `3bec68ed00118fd6`), only the registry sha differing. If the README's `reissue.py --check || reissue.py` is rerun
   after approval, the approved record is rewritten and, by `render_l3r2.filed()` as I read it, the renderer then
   refuses because `definition_reissue` names a sha the tree no longer holds. Bind the draft to the six rows' rulings
   and the records they restated (or leave rulings that decide `definition_reissue` out of the bound sha), or say in the
   README that the generator is not rerun after approval. Fix before the answers are applied.
2. **"Answered" where CFL-017 stays open.** Under `measure` and `cells`, C29 writes "**Answered on ... by owner ruling
   D-31 on row L3-OD5 (CFL-017):**" and B18 "The owner answered CFL-017 on them", while both rulings say CFL-017 stays
   open (my own chain with `cells`: "CFL-017 stays open until the cell is chosen and its sheet is held"). Word it by
   the row ("decided on row L3-OD5") or by the option.
3. **The output guard compares `abspath`, not the real path.** With an out-dir whose `DEFINITION-REISSUE-DRAFT.md` was
   a symlink to `PRODUCT-BRIEF.md`, the generator wrote through it and only then refused ("a baselined file changed
   while the re-issue ran"), leaving the baselined file modified (restored in the clone). Contrived, but the commit
   subject says "never writing a baselined file". Use `os.path.realpath` in `guard_out`, or refuse an existing link.
4. **LAYER-STATUS.md still lists the check as remaining.** The script brings the gate row to MET, but the paragraph
   "Whose each remaining item is" on the same page still ends "A checker: the independent check of L3-R2 (L3-C27)",
   while `L3-RECONCILIATION.md` reads L3-C27 CLOSED.
5. **REQ-072's FAIL leaves the definition without a status row.** C17, C18, C32 and B15 replace the plain "REQ-072
   reads FAIL at desk" with "REQ-072's reading in the requirements registry". On my decided copy REQ-072 still reads
   FAIL (`evidence_result: FAIL`, DESK_REVIEW). Moving a result out of the baseline follows `DEFINITION-STATUS.md`,
   but the draft proposes no status row carrying it, as it does DC-L3, and B15's "Not shown to hold mission M1" is
   softer than the registry. D-24 asks that an option that cannot meet the mission be flagged plainly. Propose a status
   row rendered from REQ-072's reading.
6. **Typed copies of registry text.** `solar_source()` types "four 100 W panels in two series pairs (2S2P, 400 Wp)
   into board E's 200 W stage" (and the 1S4P form), and C04 and B04 type "an 8 inch tablet". Today they match
   `l3r2.yaml`'s question for row L3-OD3 and D-28's ruling text, but they are not read from the registry. Read them from
   the ruling or the option, or assert them against it.
7. **The fixture's 20 N push is not a recommendation.** RECOMMENDED passes `--push-n 20`; row L3-OD4's recommendation
   leaves the push to the owner and records the QMX-out kit tipping under a 6.1 N press. The README calls the chain
   "the session's recommended answers, with the QMX out and TYP standing in"; name the push as a stand-in too.
8. **The change record's last section runs two paragraphs together.** "Statements of the design as generated ..." and
   "Every other mention of 'the pack' ..." are on consecutive lines with no blank line, so Markdown renders one
   paragraph.
9. **CURRENT passages are quoted by clause, not in full.** The map says it gives "every passage's baselined text"; for
   the 19 CURRENT passages it gives the clause `excerpt()` cuts (enough to find them, as the tests use it).

## What was verified

**1. The passage map.** `PASSAGE-MAP.md` has 70 passages, 51 DEFINITION and 19 CURRENT (counted from its headings).
`reissue.py --map --check` reads it current, and `locate()` refuses unless each passage's start is once on its stated
line, its end once on its end line and the whole text once in the file, so every passage is on its line in its full
text. The row by option table matches the README. My own search of both baselined documents for text not inside any
passage: on the QMX and HF only the needs table's source column (line 94, "32.50 item 16a (amateur bands, HF)"), which
the needs test keeps fixed; on the lid items only needs sources; on the solar input, deployment ("tailgate" appears
once, in C14) and the thermal margins nothing a row makes inconsistent; M1's energy is covered by C17, C18, C28, C32 and
B15, and the later mentions sit in the appendices, which are history. The pack is covered where it is a requirement or
an intention; the circuit as generated is B1. The brief's open-items table (appendix A3) is history.

**2. The generator.** Run on registry copies built by the prepared scripts with `--registry` and `--out-dir`:
- the recommended answers (QMX out and TYP standing in, push 20 N): 50 passages restated (33 CONOPS, 17 brief; B09 is
  `qmx-outside` only), 19 CURRENT statements, draft `4500eed23b45bf6f`, record `af982a2447311333`, registry copy
  `80870c867b408c45`; `--check` then reads both current;
- my own coherent set (mean day WAB, `approve`, `qmx-out`, `2s2p`, `adopt` at 6.1 N, `cells`): 50 and 19, draft
  `661b9b5eee3d48f8`, record `566be99dacc0515c`; the diff against the first draft is exactly the build, the push, the
  row 5 texts and the shas;
- my refusals: mean day WAB with the tablet out ("row L3-OD2's lid (tablet-out) does not carry row L3-OD6's
  mean-day-WAB store in the WAB build", exit 2; `od_l3_2.py` also recorded CFL-019); row 5 left undecided ("rows
  L3-OD5 are undecided", exit 2); `CONOPS.md` changed by one byte (refused as not the baselined text, by the generator
  and by `--map --check`).

I read the recommended draft end to end. Every proposed text names its row and ruling; the rulings, REQ-016, REQ-072,
REQ-078, REQ-011, REQ-014 and REQ-075 are quoted or restated from the copy's own text (checked against the copy); the
proposed CONOPS status line reads "RE-ISSUED ... pending its layer's review"; nothing is presented as approved ("Status:
PROPOSED, not approved"). I found no proposed text that changes a requirement the rulings do not change, apart from the
head note's extension (B1). The change record names the draft by its sha256/16 (matches the file), the registry by its
sha, the records citing each ruling, every passage's baselined and proposed sha, and the approval route: an owner
ruling with `decides: definition_reissue` dated on or after every row's ruling, named in `l3r2.yaml`'s
`definition_reissue`; `render_l3r2.reissue_ok()` refuses any other ruling. The generator re-checks the two baselined
shas before and after writing and never opens them for writing (minor 3 apart); its output names are fixed, so the
out-path guard can only matter through a link.

**3. `apply_layer_status_l3_r4.py`.** The row it writes is true: `check-l3r2-5.md` is held at `c1c9db881ededfe2` and
its first line reads "accepted: yes"; CHECK-1 to CHECK-4 did not accept; the row says MET for the handover as prepared
with the six decisions pending. On main after the run order, a second run (with and without `--check`) is refused:
"the page already carries ... this script has run", exit 2.

**4. D-21 to D-25.** The registry, `CONOPS.md`, `PRODUCT-BRIEF.md` and `v2/release/` are unchanged by the commit; no
requirement changes. No text recommends beyond the table: the tests name approve, 2s2p, adopt, reading-c and the mean
day as the table's recommendations (they are, in `l3r2.yaml`), and rows L3-OD2 and L3-OD6's build as the owner's with
stand-ins (minor 7 on the push). No proposal is presented as accepted. The proposed texts count no energy through the
inadequate path as capability ("no figure of it is demonstrated capability, and nothing has been built").

**5. Gates, on the clone of `fnd/l3r4` with the evidence.** `rules_lib.py requirements` 0 errors; `rules_render.py
--requirements --check` current; `render_l3r2.py --check` 0 out of date; `reissue.py --map --check` current;
`dryrun.py` byte identical; tests 102 passed, 0 failed, 0 skipped. The commit's added lines carry no en or em dash, no
internal host name and no absolute path (1766 added lines scanned), and neither generated draft does; the author is the
owner's identity with no trailer.

**6. The integrator run order on main.** On a branch from `8fec0733` in the clone, the README's six commands ran in
order with no failure (layer status script check then write, map check, render and render check, `rules_lib`, tests
102 passed); the resulting tree is byte identical to `fnd/l3r4` in every tracked file.

## For the delta check

B1 (the head note in C02 and B02, the new CURRENT passages or DC row, the map regenerated, tests), and whichever minors
are answered, at one pinned commit, with the generator rerun on the recommended answers and on one other set.
