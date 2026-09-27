# Handover release H3: what it is and how to check it

Prepared 27 September 2026 (MESHSAT-1357) as a draft, by the writer of the H3 pages, on the structure of
`RELEASE-H2.md`. H3 is a partial handover: **three of the nine pre-PCB layers are COMPLETE in it (1, product
definition; 2, concept of operations; 3, requirements), and the other six carry their remaining acceptance items.**
Nothing in it has been built, ordered, powered or measured. Every review and check it rests on is an AI review or an
AI check, labelled as one in its own heading; none is a qualified engineering review.

**Rows marked `TBD-BY-INTEGRATOR`.** A snapshot cannot carry its own checksum, so the figures of the build are written
into this page in the repository after the build, by the integrating session. **Inside the H3 ZIP this page is the
draft of the source commit and those rows are not filled in.** There, read the source commit in `SOURCE.txt`, the
file list in `MANIFEST.tsv`, and the checksum in `H3.zip.sha256` beside the ZIP.

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H3.zip` (with `H3.zip.sha256` and `H3.MANIFEST.tsv` beside it) |
| sha256 | TBD-BY-INTEGRATOR |
| Size | TBD-BY-INTEGRATOR (bytes and entries; included, excluded and referenced files) |
| Snapshot commit | TBD-BY-INTEGRATOR (the commit that adds the ZIP) |
| Source commit | TBD-BY-INTEGRATOR (every file in the ZIP is this commit's blob; `H3.MANIFEST.tsv` lists each with its git blob sha and sha256) |
| Suite on the source commit | TBD-BY-INTEGRATOR (passed, failed, skipped, and the host: a skip is not a pass) |
| Public | TBD-BY-INTEGRATOR (whether both commits are on `main` of `github.com/meshsat/meshsat-fieldkit`, and since when; `python3 v2/docs/records/h3/public_check.py <commit>` asks it) |
| Check | `sha256sum -c H3.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H3.zip` (reads every manifest row) |

## Layers COMPLETE in H3, with the records they rest on

The hashes are sha256/16 of each file as H3 carries it, printed by `v2/docs/records/h3/handover_counts.py`; the commit
is the last one that changed the file. All review records are under `v2/docs/reviews/`.

| Layer | Status in H3 | Baseline | Acceptance records |
|---|---|---|---|
| 1. Product definition | COMPLETE | definition baselined at `6b2a9965`; re-stamped BASELINED at `a9f212c7`, an editorial restructure with no definition change. `v2/docs/PRODUCT-BRIEF.md` is `85513b92ed0daf55` (`edd3c848`); it was `d36bf76b3dea8b30` in H2 | `REVIEW-A-LAYER-1-2026-09-27.md` (`d469a268fe0b8768`, `2ef6aa2a`), `REVIEW-LAYER-1-RELEASE-2026-09-27.md` (`2bd065d12f50298d`, `6209ec7e`), `REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` (`a0d8e6be2dcebcf6`, `62f26a44`), `TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` (`ae70b1a7811ecea1`, `6b2a9965`); for the re-stamp, `DEFINITION-RESTRUCTURE-CHECK-2026-09-27.md` (`4c09af64cb214448`, `a9f212c7`), CONTENT_PRESERVED |
| 2. Concept of operations | COMPLETE | definition baselined at `79963b3b`; re-stamped BASELINED at `a9f212c7` the same way. `v2/docs/CONOPS.md` is `6ebe6760c4312bca` (`edd3c848`), its needs table byte-identical; it was `4483209659dc391c` in H2 | `REVIEW-A-LAYER-2-2026-09-27-pass1.md` (`e854c2a46ea3d542`, `08f3665a`), `REVIEW-A-LAYER-2-2026-09-27.md` (`77b20ca4042f0855`, `95e078a1`), `REVIEW-LAYER-2-RELEASE-2026-09-27.md` (`cb7c773b9b193e1f`, `6209ec7e`), `REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` (`a4f0e88e48c304ee`, `62f26a44`); for the re-stamp, the same check of the restructure |
| 3. Requirements | COMPLETE since commit `24e7bf5a` | `v2/ecad/tools/pcb_requirements.yaml`, `baseline_state` BASELINED at `a54b793b` (the file there is `c8fded5cb0a165d6`), written in `2c12be91`. The file H3 carries is `6eb35694e300abff` (`6ec37197`): against the baselined file it differs in the baseline's own lines, the closure of S-51, S-78 and S-80, S-79's title, the pin on CONOPS and the readings of three records rebound to the restructured CONOPS (REQ-005, CFL-014, CFL-016), and in no record's statement, acceptance, allocation, verification or release effect (`v2/docs/records/h3/design_difference.out`) | the five records `baseline_reviews` names, each by the hash given here: `REVIEW-B-LAYER-3-2026-09-27.md` (`7a6c679f446b1baa`, `95e078a1`), `REVIEW-LAYER-3-RELEASE-2026-09-27.md` (`1c3bc2d99f9efb51`, `6209ec7e`), `REVIEW-LAYER-3-RELEASE-2-2026-09-27.md` (`cf8c73fb288be2fb`, `62f26a44`), `TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` (`ae70b1a7811ecea1`, `6b2a9965`), `TARGETED-RECHECK-LAYER-3-2026-09-27.md` (`7831358b96b6f5ca`, `24e7bf5a`): B-1 CLOSED at `2c12be91` |
| 4 to 9 | IN_PROGRESS | | `v2/docs/handover/LAYER-STATUS.md`, sections "Status at handover H3" and "Status at handover H2", give each layer's remaining acceptance items |

Layer 3's versioned package, its acceptance item 3.18, is this snapshot. The registry H3 carries still lists the item
that waits for it, S-79, as open: it is closed in the commit that files the snapshot.

Layers 1 to 3 state intent and requirements: what the kit is for, how it is used, what it must do and how each
requirement is to be verified. They do not claim that the design meets them. Where the design does not yet meet a
stated requirement (REQ-072, M1's night on the pack and solar alone, reads FAIL at desk; CON-010 reads FAIL on finding
W3T-F1), the failure stays visible in the requirements registry and in the implementation layers.

## H3's design content equals H2's

Between H2's source commit `b89b50b4` and the commit these pages were written on, no design file differs: no
schematic, committed netlist, intent, provenance sidecar, land, generator, board table, checking tool, export, CAD
source, case release file, diagram or maker document. `v2/docs/records/h3/design_difference.py` prints every file
that differs, by class, and asserts the statement (it reads git, so it needs a checkout with both commits). Under
`v2/ecad/` eleven files differ:

| File | What differs | Commit |
|---|---|---|
| `tools/handover_pack.py`, `tools/tests/test_handover_pack.py` | the packer's `repo` subcommand and its test | `a54b1f4d` |
| `tools/pcb_requirements.yaml` | the baseline, the open and closed items, the readings and notes of CON-010, REQ-005, CFL-014 and CFL-016 | `a54b793b`, `2c12be91`, `24e7bf5a`, `fa89c7c6`, `edd3c848` |
| `tools/pcb_interfaces.yaml` | the `read_at` block of `board_to_board`, re-anchored to the H2 line's netlists; no contract | `90314d99` |
| `pcb-*/routed/interfaces_<letter>.verdict.json`, seven files | INT-001's readings re-taken after that edit, each PASS as before on the same netlists | `ed988ba8` |

The exports under `v2/release/handover/_generated/` are H2's (boards A, B, D and E made at `763bccdf`, C and P at
`99cde56b`); each names the sha256 of the schematic and netlist it was made from, and both are the files H3 carries
(`v2/docs/records/h3/handover_counts.out`). The headline and the layout-entry reasons are H2's: 0 boards ready for
layout, 0 physically verified, 40 reasons (A 7, B 7, C 5, D 8, E 5, P 6, E5 2).

## What was repeated independently, and what was not

| | |
|---|---|
| Checked by a session that wrote none of what it checked | each layer's review records above (an author's text read by a separate checker); the narrow verification and the re-check of layer 3's re-baseline, each at one pinned commit; the check of the definition restructure, which used neither the restructure's map nor its scripts |
| Reproduced on H2 by a fresh checker from the ZIP and the tools it names | `v2/docs/records/handover/H2-USABILITY-CHECK.md` (an AI check of usability, not of engineering): the energy chain, the power and case scripts byte for byte, board P's regeneration, PARITY on all six boards, the exports, the suite's failures with their causes, the fetch of 29 referenced files, board P's re-take |
| Read from outside the project | `v2/docs/reviews/2026-09-27-h2-independent-review.md`, an independent review of H2 from its five delivered files, saved as the owner pasted it: it verified the archive and credits layers 1 and 2 as completed definition baselines, and names corrections, which H3's pages answer in part (the definition documents kept stable, three reproduction routes stated apart) |
| Not repeated for H3 when this page was written | no command of `REGENERATE.md` was run on an H3 build: its expected values are those of the H2 run. Regeneration, the exports and the consolidated re-take were not run again; their inputs are byte for byte H2's. No review read layers 1 to 3 again for H3: the H3 pages correct statements and add errata, and change no definition and no requirement |
| The two fresh checks of H3 | TBD-BY-INTEGRATOR (who checked, from which files, the verdict of each, and where each record is filed) |
| Never done, by anyone | a qualified engineering review of any layer or board; any physical test. R-BAT, R-PWR and R-HSD are not engaged |

## Three ways to use H3

`REGENERATE.md` states them with their prerequisites: (A) read the handover and continue from it, which needs the ZIP
and a reader; (B) reproduce the representative calculation or a schematic, which needs Python 3 with PyYAML, one maker
document restored first and, for a schematic, KiCad 9.0.9; (C) run the suite and the re-take, which needs a git
checkout with history and KiCad 9.0.9. **From the ZIP alone the full suite is not expected to pass**, and no page
claims it does.

## Errata of H3: what it knowingly does not fix

| # | What is not fixed | Effect on a reader | Where it will be fixed |
|---|---|---|---|
| a | Each layout constraint sheet's sections other than its power table are readings at `e3aedb25`, as the sheet's own head says; the power tables are current on H3's netlists | a placement, protection or test-access line of a sheet may describe an older netlist; where it and a record disagree, the record governs. One such row was found and corrected for H3 (board A, section 7) | each sheet re-derived on its netlist by its board stream, before that board's layout entry |
| b | `LAYER-STATUS.md` mixes status with history | the page is long; read its sections "Status at handover H3" and "Status at handover H2" and each layer's acceptance table, and use Appendix A only to trace an item | a restructure of the page after H3 |
| c | Re-taking one board in a repository built from the ZIP re-renders every other board's page as NO_EVIDENCE (`REGENERATE.md` section 9) | compare only the re-taken board's rows | the readings bundled with a later snapshot, or a re-take of every board |
| d | `ENGINEERING-QUESTIONS.md` was not re-read row by row for H3; five blocks found stale were corrected in place (EQ-01, EQ-04, EQ-10, EQ-16, EQ-17) | another block's options or recommended action may predate its own attempts row; the attempts row is the newer | the page's next edition |
| e | The set 6 circuit candidate (branch `fnd/r8int6`) is not in H3 | H3 lists as open several items for which a drawn candidate exists outside it (`START-HERE.md` section 1a) | the snapshot after set 6 is promoted |
| f | Board A's external-port declaration still names J_DOCK pins 1 and 2, which are ground since SC-55 moved VIN_RAW to J_VR1 to J_VR4 | TRN-001's PASS on board A does not judge VIN_RAW's entry (read in `port_protect.py`'s code, not re-run; `v2/docs/layout-constraints/A.md` section 7); the clamp D2 is on VIN_RAW in the netlist | board A's stream: the declaration moved, TRN-001 re-taken |

**An erratum about H2.** `RELEASE-H2.md` says H2's two commits are on `main` of the public repository, while H2's
own `SOURCE.txt` marks its source commit `public no`. Both are true of their time: `SOURCE.txt` records what the
building clone knew when H2 was built, and the commits were published after it. Asked on 27 September 2026 at 20:38
UTC, `b89b50b4` and `174d8466` are ancestors of `main` and the public repository serves both
(`v2/docs/records/h3/public_check.out`). H2's files are not edited.

## Known gaps carried from H2

- The readings behind the generated evidence pages live in gitignored folders and are not in the ZIP; the pages are,
  and the re-take driver re-creates the readings on a KiCad host.
- The full test suite needs a git checkout with history; from the ZIP alone it reports the failures `REGENERATE.md`
  section 7 names.
- The ZIP is deterministic per host; across hosts compare `H3.MANIFEST.tsv`.
- Maker documents are referenced by path, sha256 and URL (`REFERENCED-SOURCES.tsv`), not bundled, except those
  `pack.yaml` bundles; `REGENERATE.md` section 1a fetches one and checks it.

## Continuation and external dependencies

- `v2/docs/handover/CONTINUATION-BRIEF.md`: the decisions to preserve, the remaining work in dependency order, the
  constraints known today, the failed approaches and the specified experiments.
- `v2/docs/handover/ENGINEERING-QUESTIONS.md`: one block per open question, grouped into design work, physical evidence
  and external authorisation, with costed routes in `v2/docs/reviews/READY-TO-ACT.md`.
- Tools outside the repository: KiCad 9.0.9 for regeneration and ERC, and Python 3 with PyYAML for the checks; the
  versions used are in `SOURCE.txt` and `REGENERATE.md` section 1.
