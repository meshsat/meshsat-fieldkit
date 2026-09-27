# Handover release H2: what it is and how to check it

Written 27 September 2026 (MESHSAT-1357), after the external review of the 18:00 progress report
(`v2/docs/reviews/2026-09-27-third-checkpoint-review.md`, section 3), which asked for the exact package, its checksum,
its revisions, its usability verdict and the layers it carries as COMPLETE. H2 is a partial handover: two of the nine
pre-PCB layers are COMPLETE in it, and the other seven carry their remaining acceptance items. Nothing in it has been
built, ordered, powered or measured.

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H2.zip` (with `H2.zip.sha256` and `H2.MANIFEST.tsv` beside it) |
| sha256 | `20072be74852ec56d818d094d150a382143d95527dd28599b22eee84c3a5cf35` |
| Size | 51,894,737 bytes; 2,234 entries |
| Snapshot commit | `174d8466` (adds the ZIP; its body gives the runner suite at the snapshot tree: 1936 passed, 0 failed, 63 skipped) |
| Source commit | `b89b50b4` (every file in the ZIP is this commit's blob; `H2.MANIFEST.tsv` lists each with its git blob sha and sha256) |
| Public | both commits are on `main` of `github.com/meshsat/meshsat-fieldkit` since 27 September 2026 |
| Retrieve | `git clone https://github.com/meshsat/meshsat-fieldkit && git -C meshsat-fieldkit checkout 174d8466`, or the ZIP alone from `https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/174d8466/v2/release/handover/H2.zip` |
| Check | `sha256sum -c H2.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H2.zip` (reads every manifest row) |

## Layers COMPLETE in H2, with the records they rest on

Every review below is an AI review, labelled as such in its own heading; none is a qualified engineering review. The
hashes are sha256/16 of each file at `174d8466`, and the commit is the last one that changed it.

| Layer | Status in H2 | Acceptance records |
|---|---|---|
| 1. Product definition | COMPLETE at `6b2a9965`; `v2/docs/PRODUCT-BRIEF.md` BASELINED (`d36bf76b3dea8b30`) | `REVIEW-A-LAYER-1-2026-09-27.md` (`d469a268fe0b8768`, `2ef6aa2a`), `REVIEW-LAYER-1-RELEASE-2026-09-27.md` (`2bd065d12f50298d`, `6209ec7e`), `REVIEW-LAYER-1-RELEASE-2-2026-09-27.md` (`a0d8e6be2dcebcf6`, `62f26a44`), `TARGETED-CHECK-LAYERS-1-3-2026-09-27.md` (`ae70b1a7811ecea1`, `6b2a9965`), all under `v2/docs/reviews/` |
| 2. Concept of operations | COMPLETE at `79963b3b`; `v2/docs/CONOPS.md` BASELINED (`4483209659dc391c`) | `REVIEW-A-LAYER-2-2026-09-27-pass1.md` (`e854c2a46ea3d542`, `08f3665a`), `REVIEW-A-LAYER-2-2026-09-27.md` (`77b20ca4042f0855`, `95e078a1`), `REVIEW-LAYER-2-RELEASE-2026-09-27.md` (`cb7c773b9b193e1f`, `6209ec7e`), `REVIEW-LAYER-2-RELEASE-2-2026-09-27.md` (`a4f0e88e48c304ee`, `62f26a44`) |
| 3 to 9 | IN_PROGRESS | `v2/docs/handover/LAYER-STATUS.md`, section "Status at handover H2", gives each layer's remaining acceptance items; layer 3's baseline was set and then reversed by the targeted check above (S-80) |

Layers 1 and 2 state intent: the product and its use, including an operating envelope and missions such as M1. They
do not claim the design meets them. Where the design does not yet meet a stated requirement (for example REQ-072, M1's
night on the pack and solar alone, which reads FAIL at desk), the failure stays visible in the requirements registry and
the affected implementation layers.

## The usability verdict

One fresh checker, who built none of the package, tested H2 from the ZIP and the dependencies it names:
`v2/docs/records/handover/H2-USABILITY-CHECK.md` holds its full result. It found H2 a usable partial handover, with no
blocking defect and 14 minor ones, and it read layers 1 and 2 as complete for their purpose. It answered all six of
the owner's questions from the package, reproduced the representative calculation and board P's regeneration, and
found PARITY on all six boards. It is a usability check, not an engineering review.

The two blocking findings of H1's check, stated for this package:

| H1 finding | State in H2 |
|---|---|
| B1: work existed only in unpushed branches | closed: board B's round 8 and the layer 2, 3, 5 and 7 candidates are merged on `main` (`b76c18cb`, `95e078a1`, `0da2778b`, `c351115d`); H2 lists the superseded candidate patches as referenced, not bundled |
| B2: no procedure for the consolidated re-take | closed in substance: the driver `v2/ecad/tools/retake_schematic_phase.py` and REGENERATE section 9 (`e5fde2ed`), run on the KiCad host (`8ea7867e`). The H2 checker could not follow section 9 from the public repository because H2's commits were not yet public; they are now. The route that builds a repository from the ZIP needs a `git add -A -f` step the page does not state (an H2 minor finding, answered for H3). |

The 14 minor findings are being answered in the editable pages (`v2/docs/handover/H2-RESPONSE.md` when it lands) and
carried into the next snapshot.

## Continuation and external dependencies

- `v2/docs/handover/CONTINUATION-BRIEF.md` in the ZIP: the decisions to preserve, the remaining work in dependency
  order, the constraints known today, the failed approaches and the specified experiments.
- `v2/docs/handover/ENGINEERING-QUESTIONS.md`: one block per open question, grouped into design work, physical evidence
  and external authorisation, with costed routes in `v2/docs/reviews/READY-TO-ACT.md`.
- `REFERENCED-SOURCES.tsv` in the ZIP lists every maker document referenced but not bundled, each with its path, sha256
  and URL. Each is retrievable at the exact revision from the public repository
  (`https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/174d8466/<path>`) and is checked against its sha256. The
  H2 checker fetched 29 such files this way and all matched.
- Tools outside the repository: KiCad 9.0.9 for regeneration and ERC, and Python 3 with PyYAML for the checks; versions
  are in `SOURCE.txt` and REGENERATE section 1.

## Known gaps of H2

- The readings behind the generated evidence pages live in gitignored folders and are not in the ZIP; the pages are,
  and the re-take driver re-creates the readings on a KiCad host.
- The full test suite needs a git checkout (some tests read the history); from the ZIP alone it reports the failures
  REGENERATE names.
- The ZIP is deterministic per host; across hosts compare `H2.MANIFEST.tsv`.
- The layout constraint sheets were written against the e3aedb25 netlists and are stale against H2's (an H2 minor
  finding, being regenerated for H3).
