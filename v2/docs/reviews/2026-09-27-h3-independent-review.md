# MeshSat H3: independent engineering and handover review

<!-- Saved verbatim on 27 September 2026 as the owner pasted it (MESHSAT-1357): an independent review of handover H3 from its three delivered files (H3.zip, H3.zip.sha256, H3.MANIFEST.tsv). 11 en dashes in ranges are written as hyphens and 3 em dashes as commas (the repository's no-dash rule); every other word is as pasted. It is executed as the earlier reviews were. -->

27 September 2026. Reviewed the supplied H3.zip, H3.zip.sha256 and H3.MANIFEST.tsv against H2, the restart plan and the five amendments to Claude's recovery plan.

## Decision

**CONDITIONAL acceptance as a usable partial engineering handover.** H3 delivers the completed product definition, concept of operations and requirements baseline. I credit **Layers 1-3 as completed definition layers within their recorded scope**. The final release-assurance records are not included in the three supplied attachments, so I cannot confirm every promised H3 release check.

**Layout/fabrication readiness remains BLOCKED.** H3 explicitly carries H2's circuit design, seven open feasibility records and zero boards ready for layout. The newer Set 6 circuit candidate is excluded. That is an appropriate release boundary: the completed foundations have been delivered without waiting for the next circuit wave.

The layered approach is now producing the owner's intended fallback. Another engineer can receive the product/use definitions, requirements, editable design material and continuation records without recovering the old chat. They still need to complete substantial architecture, component, mechanical, circuit and analysis work. Three completed definition layers must not be interpreted as one-third of the total engineering effort or as PCB readiness.

Two checker defects deserve focused repair in the next engineering candidate. They do not justify reopening the completed product/requirements baselines.

## 1. Integrity and verification completed

| Check | Independent result |
|---|---|
| ZIP size | 52,187,825 bytes |
| Archive SHA-256 | Matches the supplied checksum |
| Archive inventory | 2,275 entries, no duplicate paths |
| Manifest | 2,274 entries; MANIFEST.tsv itself is the sole unlisted file |
| Every listed size and SHA-256 | Matches |
| Recorded Git blob hashes | All 2,271 applicable entries match the supplied bytes |
| External/internal manifests | Byte-identical |
| Six root handover pages and repository-path originals | All byte-identical |
| H3 handover count script | Exit 0; output byte-identical to the committed reference |
| Five Layer 3 baseline review records | Every recorded hash matches its packaged file |
| Requirement comparison with H2 | Same 144 records, needs, owner rulings and session choices; only four records' evidence/bindings changed |
| Requirements' engineering definitions | No record's statement, acceptance, allocation, verification or release effect changed in that comparison |
| Definition restructure | All 119 designated retained blocks found in the new documents; CONOPS needs table byte-identical to H2 |
| Design comparison | No changes in the six committed netlists, six schematic generators, nine shared intent files or 42 shared export files; shared native schematics unchanged |
| Export provenance | Six boards' schematic and netlist hashes match the packaged inputs |
| Power-width calculation | Markdown output reproduced byte-for-byte from H3's inputs |
| Stored-energy example, ZIP-only route | Reproduced its documented 98-check result: exit 1 for the omitted Mill-Max source document |
| REL-001 targeted fixtures | Four isolated cases run; two demonstrate false PASS results, detailed below |
| Packaged source integrity after execution | Every manifest-listed file remains unchanged |

Archive SHA-256:

`6922a96d732442e99a65d8db3f0734378bd7ea636894fca283a4b3ca424dd07a`

`SOURCE.txt` identifies source commit `75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669`, dated 27 September 2026 at 23:05:52 CEST. Matching blob hashes establishes consistency of the supplied bytes; it does not independently establish the public Git history.

**Execution limits:** KiCad and pcbnew are unavailable here. I did not rerun schematic generation, ERC, the full suite, hardware tests or a qualified electrical review. The rail-width result is reproduction of the project's model, not independent validation of its thermal assumptions or fabrication suitability. The energy-chain example's missing-document failure is disclosed by the reproduction guide; it is not a newly demonstrated circuit failure. No missing vendor document was silently substituted.

The public release note and source-commit page could not be retrieved in this environment. Their publication remains unverified here; that retrieval limitation is not evidence that publication failed.

## 2. Why Layer 3 now earns credit

The requirements registry reads `BASELINED at a54b793b` (`v2/ecad/tools/pcb_requirements.yaml:259`). Its five baseline-review entries identify files that are present and whose hashes match.

The added `TARGETED-RECHECK-LAYER-3-2026-09-27.md` closes the specific B-1 finding at `2c12be91`. The packaged registry closes S-51, S-78 and S-80. CON-010's corrected evidence now agrees with its FAIL result. The other recorded evidence rebindings accompany the product/CONOPS restructure; my H2/H3 comparison found no altered requirement definition.

H3 also supplies the previously missing versioned package, Layer 3 acceptance item 3.18. Its source still lists S-79 as pending because the snapshot-filing commit closes that item; the release note explains this sequencing. That source-snapshot condition alone is not a reason to reopen the requirements definition.

The baseline still visibly includes unmet implementation requirements, including REQ-072 and REQ-077. This is the correct separation: defining what the system must achieve does not assert that the current circuits achieve it.

## 3. Prioritized findings

Paths and line numbers below refer to files inside the H3 archive root.

| ID | Priority / type | Confidence | Evidence and consequence | Fix and acceptance |
|---|---|---|---|---|
| H3-01 | **P1, confirmed checker defect** | High; reproduced | `reliability.py:34,69-90,131-139` can issue PASS with an unclassified RJ45 connector, or with the board's netlist absent. Its completeness claim exceeds what it actually inspected. | Make missing required inputs inconclusive; reconcile mechanically relevant parts against an explicit inventory/classification. Record inspected netlist identity and coverage. The four-case matrix below must reject both currently silent cases. |
| H3-02 | **P1, confirmed coverage defect, already disclosed in H3** | High; source and netlist inspected | `boards/a.json:507-517` declares J_DOCK pins 1/2 as the power entry; both are now ground. Actual VIN_RAW enters J_VR1-4, absent from that declaration. `port_protect.py:112-133` therefore omits the entry while the status page reports TRN-001 PASS. | Correct the declaration, re-take the reading and reconcile it with the current interface/netlist. Add a regression that moving the entry cannot silently remove the required coverage. Keep decision 31's remaining review/layout holds. |
| H3-03 | **P2, release-assurance evidence gap** | Confirmed absence from supplied files; execution elsewhere unknown | Packaged `RELEASE-H3.md:19-24,75` is explicitly a draft: exact-source suite and two fresh H3 checks are unspecified. The ZIP/manifest/checksum establish delivery and integrity, but do not prove those separate checks completed. | Supply the finalized companion release note and check records, bound to this archive/source revision. Reuse existing valid results; rerun only a genuinely missing required check. No need to alter H3 merely to embed its own checksum. |

### H3-01: REL-001's completeness can be false

The checker derives the population to inspect from a small regular expression over component value prose. It then checks that population against declared classes. Components missed by the first step disappear from the completeness denominator.

I ran the actual H3 CLI in isolated fixture directories, with outputs directed outside the supplied tree:

| Fixture | Observed result | Assessment |
|---|---|---|
| One declared JST connector | PASS, exit 0, one covered part | Valid control |
| Same connector plus an undeclared IDC header | FAIL, exit 1 | Valid rejection control |
| Same connector plus an undeclared `RJ45 MagJack` | **PASS, exit 0**, still one covered part | False completeness |
| Board A declaration, but no netlist | **PASS, exit 0**, zero covered parts | Missing input accepted |

This is relevant to the actual design. Board B's J_ETH is described as an RJ45 jack; J_SIM1/J_SIM2 are described as nano-SIM push-push parts. Board A's power dock pins are described as spring pins. Those values do not match the H3 wear-word expression. A separate scan found 54 J-prefixed components outside that expression; this is an inspection queue, not proof that every one needs the same mechanical treatment.

The recovery checkpoint already acknowledges a broader wear-classification problem and reports a Set 6 fix for false positives on logic gates whose descriptions mention a socket. That fix is outside H3, and correcting that false positive does not by itself address missing connectors or missing netlists.

The practical repair should cover input completeness and classification together. Explicitly dispose of relevant connector, socket, holder and mechanical-part candidates; keep justified exclusions visible. Use the declared board configuration rather than whichever matching netlist has the newest filesystem timestamp (`reliability.py:45-48`). Bind the result to the input actually inspected. Missing required evidence must propagate as inconclusive to its consumers.

**Scope:** I demonstrated an individual checker producing false acceptance. I did not demonstrate the top-level project falsely releasing a PCB. Other holds remain active, and H3 correctly reports no board ready for layout. REL-001's desk result also does not replace its later physical verification.

### H3-02: a current netlist does not guarantee complete coverage

The committed Board A netlist connects J_DOCK pins 1 and 2 to GND, J_VR1-4 to VIN_RAW, and D2 between VIN_RAW and GND. The problem established here is the declaration/checking boundary: the listed entry pins are skipped as ground, and the actual entry pins are never selected.

D2's presence means this finding is **not proof that the circuit lacks a clamp**. It proves the TRN-001 PASS does not establish coverage of the intended power entry. A netlist hash can be current while the declared population is wrong.

The release note's erratum f and the latest execution checkpoint openly acknowledge this. Preserve that disclosure, correct the board declaration, and verify the actual entry/protection path. Add a test in which the declared entry is moved or omitted: the checker must demand reconciliation rather than shrink its coverage silently.

## 4. Closure against the previous reviews

| Earlier requirement/finding | H3 assessment | Evidence and remaining work |
|---|---|---|
| Preserve Layers 1/2 | **CLOSED for this snapshot** | Accepted definitions and review chain retained; needs table and designated definition blocks preserved through the restructure. |
| Deliver Layer 3 | **CLOSED for definition/package delivery** | Registry baseline, closing re-check, matching review hashes and actual H3 archive. Release-assurance documentation remains H3-03. |
| Do not hold H3 behind the next circuit wave | **CLOSED** | H3 is delivered from the foundation line; Set 6 explicitly excluded. |
| Board A's stale power-table input | **CLOSED for H3's power table** | Current VIN_RAW input 14.10 A; the project's reproduced model yields the recorded 15.29 mm. This is a model result with stated copper/temperature assumptions, not a universal width prescription. |
| All layout constraints current and automatically checked against inputs | **PARTIAL** | Non-power sections explicitly retain older readings. The binding guard is recorded as later work. Re-derive applicable constraints before committed layout. |
| FEA-007 mechanical-hold contradiction | **CLOSED at the reviewed documentation level** | Current table distinguishes A/B/E/P physical mock-up dependencies, D/E5 desk work, and C outside the stated hold. A fully consolidated generated view remains future work. |
| Stable definitions separated from changing status | **PARTIAL** | DEFINITION-STATUS and preserved definition blocks improve stability. The broader handover still mixes current and historical strata; LAYER-STATUS is about 296 KB. Finish this incrementally without holding completed releases. |
| Explain reproduction prerequisites | **PARTIAL, materially improved** | Read-only, representative reproduction and history-dependent validation routes are distinct. ZIP-only energy example behaves as documented. Full history/KiCad route not independently run here. |
| Prevent one-board refresh from erasing other boards' evidence | **OPEN in H3** | Release erratum c still documents the problem; checkpoint says the guard is being developed. The guard must also invalidate genuinely stale readings. |
| Preserve recovery metadata and verify old-branch equivalence | **REPORTED ADDRESSED** | Latest checkpoint records archive/read-back before pruning and patch/content comparisons. I inspected those records, not the live recovery operation. |
| Checkpoint unfinished work durably | **REPORTED ADDRESSED** | Worker branch commits at least every 30 minutes; persistent worktree paths and hourly/integration bundles to the laptop are documented. Live restore behavior not independently verified. |
| Two failed reviews trigger changed method, not abandonment | **POLICY CORRECTED; EXECUTION UNVERIFIED** | Checkpoint says the item stays assigned. The recovering streams are still reported running. |
| Demonstrate parallel execution | **REPORTED, with concrete ledger** | Branches, start times and states are present for recovered parts, stackup, SI, I2C, tray and tool work. These are operational records, not independently observed live processes. |

## 5. What an incoming engineer can use now

**Completed definition deliverables:** product intent, operating scenarios/envelope, source-linked requirements and planned verification, with their acceptance history.

**Incomplete engineering candidates:** architecture and budgets, interfaces, component identities/procurement, mechanical design, native schematics, generators, calculations and layout constraints. These are useful starting material, explicitly subject to the listed open decisions and checks.

The reproduced H3 counts are:

- 144 requirement records and 58 open items: 50 session engineering items, six later/external-money items, one owner action and one conditional item.
- Seven feasibility records still open.
- Zero boards ready for layout; 40 recorded layout-entry reasons.
- 2,393 per-reference BOM rows; 1,630 without an LCSC code, including 1,446 R/C/L rows. These are not counts of unique component selections.
- No physical verification or qualified electrical sign-off established.

The layout-entry reason counts remain A 7, B 7, C 5, D 8, E 5, P 6 and E5 2. The copied status is consistent with H3's declared design boundary; it should not be used to assess the newer Set 6 candidate before that candidate's own evidence is collected.

## 6. Next actions for Claude

1. **Finish the H3 release record:** provide the completed companion note and promised fresh-check records for this exact archive. Keep H3 immutable and Layers 1-3 credited; avoid another general baseline review.
2. **Complete Set 6 integration and its evidence refresh** on the actual integrated revision. Preserve ongoing worker checkpoints and distinguish engineering closures from evidence-only refreshes.
3. **Repair H3-01 and H3-02 with targeted regressions.** Correct coverage and missing-input semantics, not only the currently observed wording examples. Track the affected results as limited until repaired.
4. **Continue the Layer 4-9 closing streams**, including actual interface, parts, battery/power, mechanical and analysis work. Keep source-backed decisions and physical/specialist dependencies visible.
5. **Issue the next handover from a coherent candidate** when it adds reviewed engineering progress. Carry concise current status, essential evidence and an actionable continuation brief; preserve prior releases.

The achieved result is substantial and specific: the owner now has three packaged, reviewed definition layers that survive another interrupted session or a stalled routing campaign. The next gain must come from closing engineering decisions and circuits, with trustworthy coverage checks, while retaining that transferable foundation.
