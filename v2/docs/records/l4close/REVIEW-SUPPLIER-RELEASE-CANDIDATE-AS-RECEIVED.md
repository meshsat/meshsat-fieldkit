# MeshSat supplier handover — release-candidate review

Date: 3 October 2026  
Package: `MESHSAT-SUPPLIER-HANDOVER-RELEASE-CANDIDATE-761677ca.zip`  
Named revision: `761677ca67a836f81a23684738148cf9ec6d0edd`  
Comparison: the previously reviewed provisional package `d48becdc`.

## Decision

**READY for an initial supplier engineering review and quotation. Power-design closure and fabrication release remain BLOCKED.**

The package correctly defines “release candidate” as a handover-package state, not a fabrication approval. It preserves the previous handover corrections, exposes the open solar defects, adds the VBUS20 protection defect, and includes more concrete downstream work in a separately labelled set 28 snapshot.

Two bounded issues remain: a reproducible weakness in the new sentence-based scan, and imprecise claims about the revision and type of replay that passed. Neither requires another broad design review before approaching a supplier. Correct them through the normal integration process and provide precise handover wording.

## Verification performed

- ZIP size: **19,786,993 bytes**, matching the `.size` companion and quotation.
- SHA-256: `565b9f9ece0e6826a834d8dee050ccd414a2f67c33ca7da7883f7bdbc1ee70be`, matching the companion and quotation.
- 752 extracted files; all 751 manifest entries match. The manifest itself is the remaining file.
- All 183 Python files parse without syntax errors.
- Both copies of the supplier entry page match.
- The twelve existing base schematic/board/netlist files are unchanged from the previous package. Draft changes and branch material must not be mistaken for applied circuit changes.
- Inspected the new cache, its dependency-key functions and targeted tests. The recorded source fingerprint matches the supplied script; all 54 cache input files present in this archive match their recorded hashes. The other 118 recorded inputs are absent from this compact archive, which is not advertised as self-contained numerical replay.
- Ran isolated probes using the supplied `lead_scan()` and `src_part()` functions, extracted with Python AST. These probes do not import the full project or execute the electrical solver.

**Limits:** no full numerical recomputation, project suite, hardware generation, firmware build or physical testing was performed. An attempt to inspect the public GitHub commit through the web retrieval tool failed with a retrieval-service error; publication was therefore not independently confirmed here. That error is not evidence that the commit is absent. Reported project suite results remain the project's evidence.

## Findings

### L4-RC01 — P2, confirmed: an approved sentence exempts additional claims in the same table cell

**Location:** `v2/docs/records/l4e7/l4e7_stage_settings.py:556–581`, especially 572–576; the scan contributes to `scan_part()` and the cache key.

The scan searches for panel/solar lead-length statements. It then treats a match as approved whenever the surrounding Markdown table cell contains any complete sentence in `LEAD_STATEMENTS`.

That permits a second, unreviewed statement in the same cell to inherit the first statement's approval. I reproduced this by appending:

> The selected panel lead is 9 m.

to the same cell as the existing approved statement, which refers to 5 m. The scan returned no unreviewed hits and exactly the same cited-statement result as before.

| Probe | Observed result |
|---|---|
| Add unrelated editorial text | Scan unchanged, as intended |
| Change the approved statement's `5 m` to `9 m` | Scan changes and reports an unreviewed hit |
| Add the new 9 m statement in a separate cell | Scan changes and reports an unreviewed hit |
| Add the new 9 m statement in the same cell as the approved statement | **Scan unchanged; no unreviewed hit** |
| Change the numerical constant `EA2_FLOOR_DIV` | Source key changes, as intended |

**Consequence:** the scan does not establish its claimed “any other lead statement” condition. A changed engineering assertion can leave this portion of the cache key unchanged. This does not demonstrate that the current cached electrical results are wrong; it demonstrates a hole in the guard against future relevant document changes.

**Small fix:** recognize the exact approved statement span, then independently inspect remaining statements. The presence of an approved sentence must not exempt its entire table cell or document. Preserve the compute/render separation and numerical dependency tracking.

**Acceptance:** add the same-cell counterexample to the existing scan tests. It must produce a hit and change the scan key; unrelated prose must still avoid a solver rerun. This parser test needs no full electrical recomputation. Do not build a new general-purpose document-analysis framework for it.

### L4-RC02 — P2, verification gap: replay wording does not identify the tested revision and execution mode precisely

**Evidence:**

- `README.md` names package commit `761677ca`, but describes the gated suite as running on design commit `94971c8c`.
- `v2/docs/records/l4close/checks/check-l4close-3.md` likewise names `94971c8c` as the candidate read.
- `SUPPLIER-HANDOVER.md:160–166` says the release suite ran on the package's “exact commit.” The supplied evidence does not substantiate that phrasing.
- `v2/ecad/tools/tests/test_l4e7.py` separately defines cached-render checks and an opt-in `t_recompute_reproduces_the_committed_output()` guarded by `L4E7_RECOMPUTE=1`.

There may be only documentation or bookkeeping changes between the tested design and the packaged revision. That would not itself invalidate the numerical evidence. However, it must be stated and demonstrated rather than described as the same commit.

**Small fix:** identify the tested design commit, packaged commit, relevant changes between them, and which checks covered those changes. Distinguish cache validation/output rendering from a fresh solver run. Cite the existing recomputation result and its numerical-input fingerprint if that is the intended evidence.

Do not rerun an entire suite solely to change a sentence when the intervening changes are demonstrably irrelevant to its results. Conversely, changed numerical inputs or acceptance code require the corresponding checks.

**Disposition:** recipient numerical replay remains **unverified by this review**. Publication and a documented acquisition route improve accessibility; they do not by themselves demonstrate replay success.

## Quotation: accurate archive metadata, one paragraph to clean up

The filename, byte count, checksum and full revision all match the uploaded package. The previously agreed three-phase scope remains intact.

The new package paragraph contains a sentence splice ending “carried separately in the package and labelled of the public repository.” More importantly, “every calculation can be re-run from a clone at that commit” is too broad for a package that also contains unpromoted set 28 work and requires additional inputs.

Retain the verified filename, size, checksum and revision, then use this explanation:

> This package contains the project's published baseline and a separately labelled snapshot of unpromoted set 28 work. The entry page distinguishes those states and lists the checkout, tools and maker documents required for numerical replay. The branch snapshot is included for review and is not covered by the baseline's release-suite results.

“Published” is the project's statement; this review could not independently check remote availability. No correspondence was sent.

## Closure matrix and engineering status

| Item | Current disposition |
|---|---|
| L4-SH01, thermal uncertainty sign | **CLOSED.** Correct lower-bound acceptance remains in the summary. |
| L4-SH02, replay prerequisites | **CLOSED as the original instruction defect.** Git/history and external inputs remain explicit. The stronger new exact-revision claim is addressed separately by L4-RC02. |
| L4-SH03, overstated defect closure | **CLOSED.** Open engineering defects and blocked release remain explicit. |
| Compute/render efficiency | **Implemented in source.** Cache/source checks behave as described in the probes above; the sentence guard needs L4-RC01. Reported timing improvements were not independently benchmarked. |
| Solar D-10 and D-16 | **OPEN.** Their known design failures remain correctly exposed. |
| Board B fan supply | Correction now present as a **draft** in the included branch work, not a qualified implementation. |
| VBUS20 single-fault protection | Newly exposed as P10/S-111, with a drafted correction awaiting review and application. |
| Power-design closure / fabrication | **BLOCKED.** Document promotion and passed software tests do not close these gates. |

The added set 28 snapshot includes Layer 5 interfaces, Layer 6 part-selection work, Layer 7 mechanical/test preparation, Layer 8 circuit drafts, bring-up material and panel firmware source/tests. These are tangible deliverables. I have not independently accepted their full technical content or credited any additional layer as complete.

The later status update mentions set 29 findings L9P-F01 and L9P-F02. Those identifiers were not found in this package's supplier entry page or included set 28 records. Keep their current disposition available as a short handover delta when the supplier starts its review; do not interpret their absence from this earlier snapshot as closure.

## Next action

Continue the supplier quotation process and the existing set 28/29 work. Make the scan correction with its narrow regression, make the replay evidence precise, and clean up the quotation paragraph. Carry those changes in a small normal delta. No new full-project plan or broad review cycle is required to begin supplier engagement.
