# Independent review of MeshSat handover H2

<!-- Saved verbatim on 27 September 2026 as the owner pasted it (MESHSAT-1357): an independent review of handover H2 from its five delivered files. 1 en dashes in ranges are written as hyphens and 0 em dashes as commas (the repository's no-dash rule); every other word is as pasted. It is executed as the earlier reviews were. -->


27 September 2026. Inputs: the attached H2.zip, H2.zip.sha256, H2.MANIFEST.tsv, RELEASE-H2.md and H2-USABILITY-CHECK.md.

## Decision

**H2 delivers the first tangible result of the layered handover objective.** The product definition and concept of operations, their baseline declarations and their acceptance records are present in a versioned archive whose integrity I verified. I agree with treating Layers 1 and 2 as completed definition baselines within their stated scope.

This is a usable partial engineering handover with identified corrections. It does not establish a settled architecture, complete PCB design inputs or electrical approval. Layers 3-9 explicitly remain unfinished.

The earlier delivery objection is now closed for the files supplied here: there is an actual package to inspect and pass to another engineer. Public repository availability is a separate claim in RELEASE-H2; I did not independently verify its publication. Local delivery does not depend on that claim.

## 1. Checks independently completed

| Check | Result |
|---|---|
| Archive size | 51,894,737 bytes; agrees with RELEASE-H2 |
| Archive SHA-256 | Matches the attached checksum and release note |
| ZIP entries | 2,234 files; no duplicate paths |
| Manifest inventory | 2,233 listed files; MANIFEST.tsv itself is the only unlisted file, as expected |
| Listed file sizes and SHA-256 hashes | All match; zero discrepancies |
| Git blob hashes recorded in the manifest | All 2,230 applicable entries match the packaged bytes |
| External versus internal manifest | Byte-identical |
| Six root handover pages versus their repository-path copies | All byte-identical |
| Layer 1/2 documents and selected acceptance-record hashes | Match RELEASE-H2 |
| Export provenance versus packaged native schematics | All six schematic hashes match their export provenance |
| Read-only handover count script | Reproduced its committed output byte-for-byte, exit 0 |

Archive SHA-256:

`20072be74852ec56d818d094d150a382143d95527dd28599b22eee84c3a5cf35`

The archive records source commit `b89b50b4421fd882967b390a09c21dbd307ca98e`; the attached release note identifies `174d8466` as the commit containing the snapshot. Matching recorded blob hashes establishes consistency of the supplied bytes, not independent verification of the public Git history.

The reproduced counts include 144 requirement records, 60 open items, 40 layout-entry reasons, and 2,393 per-reference BOM rows, of which 1,630 lack an LCSC code. Missing distributor codes should not be confused with 1,630 distinct component selections.

**Scope of execution:** I inspected and ran the read-only `handover_counts.py`. I did not run the complete project suite, board generators or physical calculations. KiCad and pcbnew are unavailable in this environment. The attached checker reports those regeneration results; they remain that checker's evidence rather than tests I personally repeated.

## 2. Why Layers 1 and 2 can now be credited

The package contains substantive documents, not merely COMPLETE labels:

- `v2/docs/PRODUCT-BRIEF.md` defines the problem, intended users, prototype scope, fixed constraints, exclusions and open feasibility dependencies.
- `v2/docs/CONOPS.md` defines actors, needs, missions, modes, commissioning, faults, recovery and the intended behavior of core functions.
- The review chain is included and explicitly labeled AI review.
- The documents distinguish intended capabilities from demonstrated performance and record conditions that could reopen the baseline.

The actual document hashes match the release note:

| Document | SHA-256 prefix |
|---|---|
| PRODUCT-BRIEF.md | `d36bf76b3dea8b30` |
| CONOPS.md | `4483209659dc391c` |
| Targeted Layer 1/3 check | `ae70b1a7811ecea1` |
| Second Layer 2 release review | `a4f0e88e48c304ee` |

The remaining mission-energy failure is visible rather than concealed. M1 is defined as a 72-hour pack-and-solar mission, while REQ-072 remains a desk FAIL and the possible remedies are identified. That can be a completed definition of the desired mission while the proposed energy architecture remains inadequate. It must not be advertised as achieved endurance.

Similarly, the hot-end, EMCON, ZEROIZE and case-fit uncertainties remain implementation dependencies. Their presence does not automatically prevent recording a complete statement of product intent.

The qualification is important: these are completed **definition baselines**, not immutable proof that every selected implementation can meet them. A later necessary product change must reopen the affected definition transparently.

## 3. Two findings should be elevated above ordinary editorial cleanup

The attached usability check labels all 14 findings minor. That is defensible for understanding the project, but two have greater consequences when an engineer starts implementing it.

### A. Stale electrical constraints could guide the next design incorrectly

I independently confirmed:

- `v2/docs/layout-constraints/A.md:36` specifies VIN_RAW at 12.31 A and an outer width of 11.92 mm.
- The packaged current intent JSON declares VIN_RAW at **14.10 A**.
- `CONTINUATION-BRIEF.md:325` still calls the sheets “the constraint record to follow.”

The checker additionally reports that recalculating the current model changes that width to 15.29 mm. I have not independently validated that sizing model or repeated its calculation; the input mismatch alone establishes the stale-data problem.

RELEASE-H2 acknowledges the stale sheets, which helps recipients who keep the companion note. H3 should regenerate them against its actual inputs, or mark them superseded exactly where the engineer would use them. The supplied old widths must not become current layout requirements.

### B. The continuation brief contradicts the case-fit gates

The brief says D and E5 are not held by the mock-up/case-fit sequence and says E5 needs its rule evidence alone. The current registry and evidence pages include FEA-007 holds for D and E5.

Resolve the distinction explicitly:

- The physical mock-up holds A, B, E and P.
- D and E5 still have applicable desk-level case-fit work.
- C is outside those stated FEA-007 holds.

A missing physical-test dependency does not mean a board has no mechanical gate. Give the incoming engineer one current per-board dependency table.

Neither finding invalidates the purpose of Layers 1 and 2. Both need correction before the affected incomplete engineering material is used for implementation.

## 4. Make the completed layers stable and the current state easy to read

The product brief contains detailed changing implementation status, transmitter counts, circuit revisions and an extensive review history. Its opening alone recounts multiple baseline attempts. LAYER-STATUS.md is approximately 251 KB and mixes the initial audit with H1, H1.1 and H2 updates.

This coupling is already generating unnecessary review work: a change in the feasibility-blocker count caused another product-brief release failure.

Keep the baseline's purpose, scope, operating intentions and product decisions together. Put changing implementation results in a clearly identified current-status section or referenced status page. Keep older review history in an appendix or the existing records.

Then reopen a completed definition layer when a requirement, scope, operating concept or other relevant decision changes. A new circuit correction or changed count should update its engineering/status record without automatically making five product documents undergo another broad review.

This is an editorial and information-architecture correction to make the existing work usable. It should not become a new tooling project or hold the completed layers hostage to formatting.

## 5. Reproduction works with dependencies, but the routes need cleanup

The archive contains 483 referenced-but-unbundled entries. External dependencies are allowed by the agreed handover criteria when they are explicit and pinned.

The attached checker reports reproducing the representative calculations and KiCad regeneration after obtaining the necessary inputs. It also identifies:

- An unpublished source reference at the time of checking, which RELEASE-H2 says publication has since resolved.
- An undocumented step for constructing a usable local repository from the ZIP, involving tracked netlists under ignored output directories.
- Tests that require Git history and therefore fail in a history-free extraction.
- Missing evidence/source files affecting the default validation route.
- A one-board re-take that regenerates other boards' status without their original readings.

Do not present these as unexplained circuit failures or as a clean full-suite pass. Document and check the exact supported route.

For H3, include the small current evidence set and essential sources needed by the advertised acceptance commands where practical. Keep large optional CAD/vendor dependencies separately pinned. Clearly distinguish:

1. Reading and continuing the design from the package.
2. Reproducing a representative calculation or schematic.
3. Reproducing the full history-dependent validation suite.

Different prerequisites are acceptable; undisclosed prerequisites are the problem. H2 should travel with RELEASE-H2.md and H2-USABILITY-CHECK.md until their relevant errata are incorporated into the next snapshot.

## 6. What should happen next

1. Preserve H2 as the delivered baseline for Layers 1 and 2.
2. Correct the stale constraints and per-board gate table in the editable records and carry them into H3.
3. Close Layer 3 against a precise requirements-definition criterion, keeping unmet circuit requirements visible in the implementation layers.
4. Continue the already identified interface, component, mechanical and architecture work. Keep the prepared specialist and hardware requests actionable.
5. Issue H3 from one coherent candidate and verify its supported reproduction route; avoid another general planning reset.

**The owner's intended fallback now exists in an initial usable form:** another engineer can receive actual product/use definitions, native design material, review records and a structured list of unresolved work. That engineer still needs to complete significant architecture and circuit engineering before treating the set as ready for PCB layout.

## Evidence basis

The five supplied H2 attachments, direct inspection of the extracted archive, an independent manifest/hash audit, the included Layer 1/2 documents and review records, targeted checks of current versus stale handover statements, and reproduction of the read-only count script.

No electrical sign-off, fresh KiCad regeneration, public-repository audit or physical test is claimed.
