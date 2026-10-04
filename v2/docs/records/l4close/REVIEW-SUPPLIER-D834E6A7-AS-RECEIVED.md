# MeshSat supplier handover: review of d834e6a7

Date: 4 October 2026, Europe/Amsterdam  
Archive: `MESHSAT-SUPPLIER-HANDOVER-RELEASE-CANDIDATE-d834e6a7.zip`  
Named revision: `d834e6a7be211d1cdd1b18ded54bec1c427048fd`  
Related document: `QUOTATION-REQUEST-DRAFT(4).md`  
Comparison: the previously reviewed release-candidate package `761677ca` and findings L4-RC01/L4-RC02.

## Decision

**READY for an initial supplier engineering quotation, accompanied by a short current-state correction sheet. Power-design closure and fabrication release remain BLOCKED.**

The earlier guard defect is corrected in the supplied code and passed this review's targeted probes. The package now explicitly identifies the reported tested revision and distinguishes cached rendering from fresh numerical recomputation. Its quotation correctly requests engineering review, correction, prototype qualification and design completion, with a named responsible engineer; it does not assume those services come with PCB fabrication.

One confirmed handover issue remains: the main supplier entry page describes superseded work as current and points to branch material that this ZIP no longer contains. The README discloses the newer state, but does not clearly supersede the contradictory entry-page rows. A brief addendum can fix the immediate communication problem without changing the tested design or delaying the quotation for another full suite.

The new LM5069-2 breaker, three-FET arrangement, LM5176 slot corrections and revised copper calculations are **not technically accepted by this review**. Their current calculations, drafts and check reports are absent from this ZIP; they appear only in its later-findings summary and the supplied progress message.

## Verification performed

| Check | Result |
|---|---|
| Archive byte count | **12,894,538**, matching the size companion and quotation |
| Archive SHA-256 | **29ed399ae8f7cb29801b9f6080725cc44cf06957430b8642440faf032e76cb7d**, matching the checksum companion and quotation |
| ZIP integrity | No corrupt member reported; 624 files extracted |
| Manifest | All **623 entries** match; no unlisted content except the manifest itself |
| Python syntax | All **135 Python files** parse |
| Shell syntax | All **3 shell files** pass `bash -n` |
| Supplier entry page copies | Root and repository-path copies are byte-identical |
| Existing circuit artifacts | All six schematics and six netlists are unchanged from the prior package's baseline |
| L4-E7 source fingerprint and stored cache key | Match the supplied source and recorded key components |
| L4-E7 recorded file dependencies | All **54 present inputs** match their hashes; **118 inputs** are absent from this compact package |
| Isolated regression probes | **13 of 13 pass**; details below |

The code probes extracted only the relevant supplied functions with Python AST and exercised them on temporary fixtures. They did not import the complete application, execute its electrical solver, alter the supplied archive, or run the project's test suite.

The README reports 2,845 passed, zero failed, 14 skipped, 228 modules and a guard check of 984 evidence files across three passes. Those remain **project-reported results**: the raw three-pass logs, aggregate gate receipt and full evidence manifest are not in this ZIP. `records/int28/RESULT.md` documents an earlier preparation run, not that final suite. There is no need to rerun tests merely to supply the existing final receipt if an engineer wants to audit it.

An attempt to open the named GitHub commit through web retrieval returned a retrieval error. This review therefore does not independently confirm publication; the error does not establish that the commit is unavailable.

No full solver recomputation, numerical replay from a complete checkout, KiCad generation, electrical simulation, firmware build or physical qualification was performed.

## Earlier findings

| Finding | Disposition | Evidence and boundary |
|---|---|---|
| L4-RC01: same-cell assertion bypass | **CLOSED for the demonstrated defect** | The current numeric guard refuses the contradictory statement even when it shares a cell with a consistent statement. It runs before cache use. The old requirement that this citation also move the expensive solver key is unnecessary when the run reliably refuses. |
| Archive-review exclusions | **Targeted mechanism verified** | A filename alone does not exempt a document; a designated matching fingerprint does; changing the file causes it to be scanned again; malformed designation data refuses. The actual `ARCHIVED-REVIEWS.yaml` is omitted from this package, so its production entries were not independently audited here. |
| L4-RC02: tested revision and replay wording | **CLOSED as the wording correction** | The README names the full packaged/tested revision and explicitly says L4-E7 uses cached rendering in the suite. Fresh recomputation is separately identified as opt-in. This does not convert project-reported suite results into independently reproduced results. |
| Prior thermal-uncertainty wording | **Correction retained** | Supplier entry P6 still uses the measured conductance minus uncertainty as the acceptance lower bound. |
| Prior replay-prerequisite disclosure | **Correction retained** | Full Git history/checkout and omitted maker documents are explicitly required for numerical replay. |
| Honest fabrication status | **Retained** | Known design defects, unapplied drafts and blocked fabrication release remain explicit. |

The 13 probes cover: a consistent statement; unrelated prose; changed length; contradictory assertions in the same and separate cells; an undesignated `-AS-RECEIVED` filename; matching and changed designated reviews; malformed designation data; recorded source fingerprint; encoded cache key; a changed numerical constant; and a presentation-only change.

## Confirmed finding: L4-RD01 — P2, supplier entry page is stale and misdirects the reader

**Type:** confirmed documentation/integration defect. Confidence: high. It affects the engineering handover, not the numerical validity of the tested commit.

Evidence:

- `README.md:15` discloses the newer LM5176 slot correction with full-speed coolers. The supplier entry's section 10, L9P-F02 row, still describes the withdrawn 70% fan cap as the drafted correction, without marking it withdrawn.
- Entry rows P8 and P10, at lines 117–118, direct the supplier to `records/l8r2` in the package's `branches/` material. `SOURCE.txt` says `branches none`; neither that directory nor `v2/docs/records/l8r2/` is supplied.
- Entry section 7 still explains how to review included branch folders. That instruction belongs to the earlier package shape.
- Entry section 3 says Layer 5's second pass is on branches, and section 4 says the eight older contracts' fields are running. This package now contains `records/l5r2/`, its completed pass-2 and pass-3 records, and the corresponding interface changes. These statements understate the delivered work.

**Impact:** an engineer following the advertised entry point can quote against a rejected fan approach, search for absent correction files, or misunderstand what has already been integrated. The top-level README's later-findings paragraph helps, but does not make the conflicting current-state descriptions unambiguous.

**Smallest correction:** issue a dated, checksum-bound `CURRENT-STATE-ADDENDUM.md` alongside this immutable ZIP. Explicitly supersede the affected entry-page rows; distinguish the tested baseline, later unintegrated candidates, omitted files available in a full checkout, and material still to be delivered. Give valid paths and commit references where known; do not claim a draft is included when it is not. Include the relevant drafts in the next normal supplier delta if the engineer needs to review them offline.

**Acceptance:** a supplier can identify the selected fan direction, its conditional/unimplemented state, where each correction can be read, and the actual Layer 5 delivery state without resolving contradictions between two entry documents. Check those links and statements directly. This editorial correction does not require reopening Layer 3, rerunning the electrical solver or recutting the frozen integration simply to send a quotation.

## What the new power update establishes—and what it does not

The update describes more concrete engineering corrections than the earlier firmware fan cap and coupon-only protection disposition. That is progress. However, the numbers below come from the progress report or README; the underlying new records are not supplied here.

| Item | Current review disposition |
|---|---|
| LM5176 stages for slots 1 and 3; full cooling retained | Reported draft correction, conditional on C4-1 to C4-6. The +1.66 A and +0.56 A margins were not independently reproduced here. |
| Revised copper widths and 1 oz fit failure on board E | Reported sizing result. This ZIP lacks the new stackup calculation, geometry and independent check, so neither 39 mm at 1 oz nor 19.6 mm at 2 oz is independently accepted here. |
| W4DP-F2 breaker and third battery FET | Reported conditional candidate. The threshold band, 1.29 ms clearance, thermal sharing and docking sequence cannot be verified from this archive. |
| DD-3, DD-5 and the device-rail finding | Remain open. A new breaker does not establish closure of these separate path defects. |
| Existing solar sense/protection defects P1/P2 | Remain openly recorded in the supplier package. No new correction proving their closure is included. |
| Schematics/BOMs | Existing baseline artifacts; these new corrections are not applied to them. |

### Two precise checks to retain in the existing protection work

These are checks on the new candidate, **not newly proven circuit defects**, because its full design and eleven E-series tests were not supplied. If the existing work already covers them, reference that evidence instead of creating another review round.

1. **LM5069-2 retries after faults.** TI distinguishes the latch-off `-1` from the automatic-retry `-2`; section 8.4.3 states that the fault/restart sequence repeats if the fault remains. The protection proof must therefore cover the repeated waveform and accumulated heating, as well as the first cutoff. A quoted 1.29 ms clearing time alone does not establish safety throughout a persistent fault. Confirm coverage in E-1 to E-11, including the added protection FET and all protected series components. Do not assume automatic retry is inherently unsuitable; demonstrate the selected behavior against the project's fault requirements. [TI LM5069 datasheet, sections 5 and 8.4.3](https://www.ti.com/lit/ds/symlink/lm5069.pdf).

2. **A third battery FET changes an already-open charger gate-drive qualification.** The supplied E11-37 procedure explicitly covers the Q39/Q40 pair and restricts transfer to that gate network and arrangement (`L4E11-SOURCE-ONLY-AND-ENTRY.md:1531–1543`). If the new third FET is added in parallel on BATDRV, rebind this existing check to the actual three-device network, including gate loading, sharing and thermal coupling. TI's BQ25730 selection guidance gives a battery-FET input-capacitance limit; the existing record already treats its interpretation and pair behavior as open. Thermal improvement alone cannot close that separate gate-drive question. [TI BQ25730 datasheet, page 92](https://www.ti.com/lit/ds/symlink/bq25730.pdf).

The earlier objection to a 24 A cutoff was based on the earlier two-FET thermal arrangement. A supported redesign of that path can change the safe sustained-current limit. Do not automatically reuse the old 21.4 A result to reject the new candidate, or accept the new candidate merely because a third FET was added: verify the new complete current/time/temperature envelope.

## Quotation and next delivery

The quotation's filename, byte count, full checksum and revision match the attachment. It discloses AI-assisted design/review, the absence of an in-house electronics engineer, the unbuilt state, proposed—not approved—experiments, phased costs and supplier capability confirmation. It is suitable for seeking a bounded Phase 1 quotation after filling the contact placeholders and removing the owner-only notes. No message was sent by this review.

Attach the current-state addendum so the supplier sees the withdrawn fan cap and the newly disclosed protection/copper work immediately. The fourteen experiments described by the frozen baseline are not a complete current count of every later C4/E-series qualification task; the addendum should identify those as additional or superseding proposed work, with overlap reconciled rather than simply adding the counts.

Continue set 29. For the next engineering review, send a small committed delta containing the new fan and breaker drafts, the copper/current-time calculation, the actual independent/coordinator verdicts and the C4/E-series procedures. A complete repository history or another large archive is unnecessary for that focused review.

For copper selection, obtain the fabricator's feasible stackups, layout implications and price difference before treating an option as purchased or qualified. A thicker-copper candidate can be developed and costed while qualification remains open; the reported width alone is not a manufacturing sign-off.

Layer acceptance remains as previously reported: Layers 1–3 accepted at their document baselines; later layers have deliverables and open work. This review does not credit another layer as 100% complete. Supplier engagement can proceed while those engineering corrections continue.
