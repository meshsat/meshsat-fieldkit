# MeshSat V2 — unified independent Layer 3 amendment review

**Date:** 1 October 2026. **Scope:** requirements quality, the five original review findings, acceptance binding and handover reproducibility.

This report supersedes `meshsat-layer3-amendment-preliminary-review-f8514c0b.md`. It consolidates the first-batch inspection and the complete-package verification. The original review of `b45d1705` remains the historical record of the defects this amendment addresses.

| Identity | Revision |
|---|---|
| Exported project revision | `f8514c0b4d292741b6cd3123db92bf824914e3f5` |
| Accepted requirements revision | `3b4b92cf3707e00806ebdfa07b86819ce77c20aa` |
| Disclosed review-workspace commit | `fcaf5cf56ef89be102a41f3705f217dcc5df612e`, parented by the exported revision |
| Input | All 16 `MESHSAT-L3-AMENDMENT-f8514c0b` ZIPs, SHA256SUMS, DELIVERY-NOTES.txt and OFFLINE-PROOF.txt |

## Decision

**READY as an accepted Layer 3 requirements baseline for Layer 4 work and engineering handover. All five original findings, L3-R01 through L3-R05, are CLOSED against their stated criteria.**

The complete supplied package now reproduces independently offline. There is one new **P2, nonblocking check-helper defect**, L3-N01, detailed below. It does not invalidate the actual acceptance verifier or justify restarting Layer 3.

The baseline preserves the owner's instructions: internal battery storage in the Peli 1450, no external battery, battery and solar required, HF and tablet retained, optional tablet charging reducing endurance, and 48–72 hours as a design objective under a stated profile. It keeps the retained solar operating window and the unresolved design shortfalls visible.

The existing D-06 single-pack ruling remains in force. Alternative internal pack arrangements remain Layer 4 proposals, not silently adopted requirements.

This review does not establish circuit compliance, a feasible final battery/thermal architecture, achieved endurance, PCB readiness or fabrication readiness. Those are later engineering outcomes. A completed requirements baseline can state demanding requirements and openly identify that the current design does not meet them.

## Independent verification

### Complete package and provenance

- All **16 ZIP checksums** match SHA256SUMS; every ZIP passes its CRC check. Total compressed size is **166,098,285 bytes**.
- A fresh combined extraction contains **981 files**, including the manifest. All **980 manifest payloads** are present and match; there are no conflicting archive paths.
- The reproduction reconstructs the two chunked files and verifies their complete hashes: the ST RM0433 manual and the H3 handover ZIP.
- The disclosed review workspace has **876 tracked files**. I independently checked that its tree is an exact subset of the exported project's tree and that all 876 working-file blob identities match. Its parent is the exported revision; original project commit identities are retained.
- The workspace commit is deliberately a reduced review tree, not a new accepted project revision. This verifies the advertised Layer 3 replay; it is not a rerun of the entire project at the accepted commit.

### Reproduction results

| Check | Independent result |
|---|---|
| Requirements registry | 145 records; 0 errors, 0 warnings |
| Generated Layer 3 pages | All 3 current |
| Definition re-issue, passage map and requirements trace | Current; checks exit 0 |
| Decision-chain dry run | Reproduced byte for byte |
| Prior closure checker | 77 units; 0 findings; its 3 fixtures behaved as expected |
| Amendment checker | Reports 16/16; one negative-only helper limitation is documented as L3-N01 below |
| Acceptance guards | 18/18 |
| Rendered acceptance | VALIDATED; accepted revision 3b4b92cf; acceptance_ok true; findings CLOSED |
| Regression tests | **140 passed, 0 failed, 0 skipped** |
| Test completeness | All 140 source-declared names present exactly once; no missing, extra or duplicate results |
| Tracked-file changes | 0; independently rechecked after the run |
| Package integrity after the run | All 980 payload hashes still match |
| Final result | **REPRODUCE: PASS, exit 0** |

Regression coverage by module: `test_requirements` 66, `test_l3r2` 27, `test_l3r4` 15, `test_l3r5` 21, `test_l3am` 8 and `test_l3_reaccept` 3. I parsed the source declarations and matched them to the actual result log, rather than relying only on the totals line.

The successful replay ran from **15:26:30 to 15:46:25 CEST**, approximately **19 minutes 55 seconds**. The reproduction log's SHA-256 is `4874e391fa7ec8e5f59020fc2518fdf7c6f3e62840c43f2e189f8964094bb397`; the complete test log's is `bc9c86300a3f1e13d0033809c5805700aa47a3186a5c81a796d82d79289d2fe7`.

The full run used the supplied, unmodified `REPRODUCE.sh` and project sources in an initially empty working directory. Network socket operations were blocked for the process and its children, with IPv4, IPv6 and child-process denial checked first. No clone, download or earlier project export supplied dependencies to this run.

Environment: Python **3.12.14**, PyYAML **6.0.3**, Git **2.51.1**, `pdftotext` **24.02.0**, and `pdftoppm` **26.05.0**. This differs from the coordinator's recorded Debian/Python/Poppler versions and provides a second environment for reproduction.

Two local setup issues were corrected before the successful run: my ZIP extraction initially omitted executable permission bits, which were restored from the archive metadata; the bundled PDF renderer needed its existing library directory exposed to the loader. The first setup attempt correctly refused the mismatched working tree. These corrections changed neither the package's source bytes nor its tests. Network isolation used an inherited seccomp restriction rather than the coordinator's `unshare -rn` method.

### Additional targeted checks

The earlier first-batch review ran **32 targeted checks**, separately from the complete regression suite. They exercised the actual acceptance record, changed requirements and authority, invalid revisions, a missing manifest, changed acceptance policy, changed owner/change-record files, and positive evidence/commentary/history updates. They also checked historical solar attribution and the sensor-selection boundary. All passed.

I also visually inspected page 2 of the supplied Littelfuse SMCJ datasheet. Its SMCJ28A row confirms 28 V standoff, 31.10–34.40 V breakdown at 1 mA, and 45.4 V maximum clamping at 33.1 A. Those quantities support the amended distinction between operating-window acceptance and disturbance protection; they do not prove the implemented circuit protects its capacitors.

## Closure of the original findings

Paths below are relative to the project root inside the review workspace.

| Finding | Final disposition | Independent basis |
|---|---|---|
| **L3-R01 — unapproved solar configuration used in the headline** | **CLOSED: attribution corrected** | `v2/docs/handover/layer3/l3r2.yaml:1119` explicitly identifies SAC-P03 as historical: the pack, load profile, 400 Wp array, voltage window and 200 W model limit. It separates retained REQ-016 and identifies understated unserved energy. The generated summaries carry the qualification. Source matching and deliberately altered figures/removed labels exercise the refusal boundary. This closes the misleading attribution, not the energy objective. |
| **L3-R02 — naming a hydrogen part could satisfy detection/shutdown acceptance** | **CLOSED: requirement corrected** | `v2/ecad/tools/pcb_requirements.yaml:12943` now specifies end-to-end water, hydrogen and VOC tests separately: stimulus/threshold basis, applicable states, timing origin, alarm, both FETs opening and persistence until service. S-49 closes selection only. S-128 assigns the remaining engineering derivations downstream. The old selection-only acceptance is rejected by the regression. Physical verification remains downstream; the existing prototype applicability is preserved. |
| **L3-R03 — export could not reproduce closure** | **CLOSED: complete offline replay** | All dependencies required by the advertised Layer 3 checks are supplied. The clean reconstruction, validators, generated outputs, deterministic dry run, acceptance checks and 140-test run pass offline, with no skips or tracked changes. The prior missing-file/history barrier is resolved for this stated replay scope. |
| **L3-R04 — acceptance was metadata without binding to reviewed content** | **CLOSED: binding corrected and exercised** | `v2/docs/handover/layer3/render_l3r2.py:576` binds normative requirements, the owner brief, governing definition changes and acceptance policy. The accepted revision resolves and matches. Invalid/old revisions and material changes are refused. The complete fixtures also cover schema-valid downstream closures whose demands remain unchanged, preserving acceptance appropriately. The acceptance record and its history stay outside their own policy hash. |
| **L3-R05 — breakdown onset was treated as protection rationale** | **CLOSED: acceptance criterion corrected** | `v2/ecad/tools/pcb_requirements.yaml:7688` preserves the operating requirement and separately traces protection to TRN-001, disturbance current/source impedance, waveform, duration, tolerance and protected-node limits. The manufacturer table supports the distinction. Bounded ESD evidence is identified separately; surge/overvoltage obligations remain open. No protection circuit is approved by closing this wording defect. |

The amendment's closure mechanism additionally checks the review's scope, reviewed revision, ancestry and unchanged amendment files. An unrelated pre-amendment check cannot close it. The supplied tests exercise those boundaries, including altered headers and changed amendment/test files.

## New nonblocking finding: L3-N01

**P2 — confirmed test-helper defect; not a defect in the actual acceptance verifier.**

`v2/docs/records/l3am/checks/verify_l3am.py:63`, helper `ver()`, treats only `None`, `True` or a successful tuple as success. The function it wraps, `apply_l3am_findings_closed.verify()`, returns the verified 40-character commit ID on success. Consequently the helper returns false for a valid check too.

I reproduced this using the supplied accepted check: the actual verifier returned `8146b4cc09223c5486e7d553d8711854a3d7678c`, but the helper returned false. I then simulated a verifier incorrectly accepting the old review; the helper still returned false, allowing its sole negative assertion to report a pass. Thus the reported 16/16 coordinator check includes one ineffective negative-only probe.

**Bounded fix:** treat the successful, contract-conforming revision return as success, and add a positive case using a valid amendment check alongside the stale-check rejection. Verify that deliberately making the verifier accept the stale check makes the negative probe fail. This is maintenance for the checking tool, not a requirement change or an owner decision.

**Why it does not reopen L3-R04:** the actual verifier has separate positive/negative coverage in `test_l3am`, and my direct tests also exercise its successful current-review path and rejection of an unrelated earlier review. The requirements-content binding and the full package replay do not rest solely on this helper. Correct it in a bounded follow-up while Layer 4 continues.

## Acceptance attribution and practical meaning

Claude's `check-l3am-4.md`, reviewed at `8146b4cc09223c5486e7d553d8711854a3d7678c`, is the internal closing verification. Both Astra amendment reviews remain NOT ACCEPTED at their respective revisions. That history is accurately retained. This report supplies an independent reassessment of the amended package; it does not retroactively label the earlier Astra verdicts as passes.

The findings are closed against their stated criteria. This is not a claim that every electronics calculation or every requirement in the wider repository has received a new exhaustive review. The approximately 2,400-test whole-project suite, KiCad execution, public-file hygiene over the full tree, physical tests and the complete Layer 4 architecture were not rerun here.

## Proceed from this baseline

1. **Continue Layer 4.** Resolve the internal energy architecture, power-path limits, thermal/cell selection and the other explicit downstream obligations. Keep unmet objectives and unimplemented corrections visible.
2. **Hand over the controlling documents together.** Start with the current owner brief, REQUIREMENTS-L3-R2.md, the governing DEFINITION-CHANGE-RECORD-L3.md, the requirements registry/trace and this review. CONOPS and PRODUCT-BRIEF still have the tracked controlled re-stamp task L3-C63; where their wording differs, the approved change record governs.
3. **Maintain the current energy-evidence pointer.** Layer 3 still labels the retained-window Layer 4 result as pending. Link the checked Layer 4 result through the current status/evidence documentation while retaining the historical P-03 qualification. This does not require repeating the energy study or reopening settled requirements.
4. **Keep actual protection verification downstream.** REQ-042's sensing/shutdown implementation, S-128's derived levels and states, and REQ-016's disturbance protection still require engineering work and appropriate later verification.

**No Layer 3 restart or new owner decision is required by this review. Continue Layer 4 and carry L3-N01 as a small checking-tool maintenance task.**

## Method references

The Git object/tree verification uses the documented [git-cat-file](https://git-scm.com/docs/git-cat-file), [git-ls-tree](https://git-scm.com/docs/git-ls-tree), and [git-hash-object](https://git-scm.com/docs/git-hash-object) interfaces. Local renderer library resolution follows the Linux [dynamic-loader documentation](https://man7.org/linux/man-pages/man8/ld.so.8.html); the additional network restriction uses [libseccomp](https://man7.org/linux/man-pages/man3/seccomp_load.3.html). The electrical table cited above is the uploaded `v2/vendor/power/littelfuse-smcj-series-tvs.pdf`, page 2, revised 20 November 2015.
