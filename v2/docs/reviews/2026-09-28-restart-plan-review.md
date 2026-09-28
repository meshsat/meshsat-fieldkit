# Review of the restart plan, 28 September 2026

<!-- Saved on 28 September 2026 as the owner pasted it (MESHSAT-1357): an outside reviewer's focused review of the session's restart plan of 15:40 CEST (the plan itself is local to the session and not in the repository; what it led to is v2/docs/EXECUTION-PLAN.md's checkpoints and v2/docs/records/int7/). The paste arrived with its line breaks removed; they are restored at its headings, paragraphs, table rows and list items. 4 en dashes in ranges are written as "to" and 4 curly quotation marks as straight ones (the repository's no-dash rule); every other word is as pasted. The reviewer's own title is kept as the first heading below. Its amendments XH-01 to XH-04 and its six pasted points are what the registry and the records cite as "the owner's review of the restart plan". The owner approved the amended plan and, at 16:27 CEST, withdrew the relaunch and workflow-configuration prerequisites of XH-01 and asked for execution in the running session. -->

# MeshSat xhigh restart plan: focused approval review

28 September 2026. Reviewed the supplied Claude plan dated 15:40 CEST against the xhigh restart prompt and H3 companion reassessment.

## Verdict

**CONDITIONAL: amend the existing plan, then approve execution. Choose option 3, "Tell Claude what to change," for now.** The recovery and integration approach is substantially sound. A new general planning cycle is unnecessary.

The strongest parts are preservation of unfinished author files before execution, recognition that main must first be reconciled into int7, exact-candidate testing, fresh review, the three-agent ceiling, and keeping H3/Layers 1 to 3 accepted. Claude also correctly distinguishes integration success from electrical readiness.

The live repository, processes, account and backups were not available to this review. Their reported observations have not been independently verified here. Findings below concern the supplied plan's own statements and their consistency, not an assertion that its commands or current circuits were tested by me.

## Amendments required

| ID | Priority / type | Evidence in the supplied plan | Required correction |
|---|---|---|---|
| XH-01 | P1, confirmed execution-setting mismatch | Section 1 reports workflows enabled and a launch with permission bypass. Section 7.1 recommends proceeding by promising not to invoke workflows. | Apply the requested workflow disable setting and verify the effective state. Preserve xhigh and ordinary explicitly assigned workers. Keep plan approval separate from granting blanket permission bypass. |
| XH-02 | P1, confirmed dependency/scheduling conflict | Section 2 calls w5ident unrelated to C's path and holds it. Section 5 requires w5ident's C selections for C's packet. w5si/C edge work has no explicit execution slot. Slot B is both scheduled for p3bind after int7 and immediately reassigned to d6dec after int7. | Name the complete C dependency chain and assign the necessary bounded C work, including exact parts, SI and p3bind. Reconcile the reviewer-slot order. Keep unrelated portions queued. |
| XH-03 | P1, resource-authority and measurement gap | Section 6 raises the recorded approximate USD 10 cap to USD 20 using a broader credit ruling, without supplying its delegation text. It says LLM usage cannot be measured beyond wall time, while the session uses Fable 5.1. | Cite the specific authority to change the task cap, or present the increase for approval. Inspect available usage/account data and identify the billing route. Separate model usage from host cost. Do not treat credit balance or elapsed time as a spending authorization or token measurement. |
| XH-04 | P1, verification gap in the proposed verdict change | Section 3.4 prescribes CON-010 FAIL to INCONCLUSIVE and an expected total of 35 reasons; section 3.7 repeats INCONCLUSIVE as the expected review result. The supporting candidate evidence is not attached. | Make the result conditional on the complete current evidence and the actual acceptance predicate. Show why the previous demonstrated failure is resolved, identify remaining uncertainty and retain FAIL if any applicable failure remains. Expected counts are checks, not targets. |

### What the workflow correction means

Anthropic documents a real disable control: `CLAUDE_CODE_DISABLE_WORKFLOWS=1` at startup, or Dynamic workflows off through configuration. Disabling workflows removes their tools/trigger; a statement that the agent will avoid them is a different control. Existing runs are not stopped by this setting, so the reported zero-running state still matters. See the [official workflow documentation](https://code.claude.com/docs/en/workflows#turn-workflows-off).

The permission-bypass flag is not what creates workflows. It is a separate setting. This plan can be approved without choosing the menu option that simultaneously grants blanket permission bypass.

### Why the cost correction matters

On the plan's figures, USD 0.41 remains under its approximate USD 10 cap, covering about 2.9 host-hours at USD 0.1422/hour. Its sequential integration estimates total approximately 3.1 to 4.7 hours. A small cap adjustment may be entirely reasonable; its authority needs to be explicit.

The more relevant sustainability question is model usage. The [official cost documentation](https://code.claude.com/docs/en/costs#using-the-usage-command) describes `/usage` token statistics and subscription usage information. Its dollar estimate is not necessarily an invoice. [Fable can consume usage credits depending on the plan/account](https://code.claude.com/docs/en/model-config#fable-and-usage-credits). This does not prove this account incurs extra charges, but it makes the billing route worth checking before another long run. If the installed client or harness cannot expose the figures, record that specific limitation and use the available account view; do not invent measurements.

### Avoid creating the next stale status page

Section 3.2 should make the new REL-001/TRN-001 limitation notices depend on the relevant open finding and evidence state. Permanently hard-coding "LIMITED" would recreate the stale-baseline-sentence problem once those repairs land.

Before promotion, demonstrate that the exact candidate plus the intended ignored-evidence archive produces the accepted views in an isolated checkout. Preserve the post-promotion cleanliness check too. This verifies the evidence installation path before publishing it rather than discovering a material mismatch afterward. Use the existing test/check machinery; no new framework is needed.

The Layer 3 correction also needs a bounded disposition of the other unlinked items, not only the addition of S-64. It remains a minor correction to the accepted definition baseline, not a reason to reopen all three completed layers.

## Paste this into option 3

Keep this plan and its recovered work. Amend only the following points; do not start another general planning or review cycle.

1. **Enforce the selected operating mode.** Replace section 7.1's recommendation to proceed with enabled workflows. Apply the documented disable control, relaunching if needed, and verify workflows disabled, xhigh applied and zero old workers. Preserve the saved plan and checkpoints. Do not bundle approval of this engineering plan with a new grant of blanket permission bypass. Retain one integrator plus at most two workers and no nested delegation.
2. **Repair C's dependency schedule.** Section 2 holds w5ident off C's path, but section 5 requires its C rows. Schedule the smallest complete C component-selection/review slice, or show current accepted evidence making it unnecessary. Explicitly assign C's four SI edge-rate decisions and the p3bind check/integration. Resolve whether slot B does p3bind or d6dec after int7. Keep the remaining identity work queued. Give the int7 review priority when its candidate is ready, without creating a second reviewer outside the cap.
3. **State the real resource authority and usage.** Quote the standing delegation that specifically permits changing the task cap to USD 20; otherwise leave it as a proposed increase requiring my approval. Available credit alone does not establish that authority. Check the installed usage/account facilities and identify how the current Fable 5.1 session and workers are billed. Record a baseline and a checkpoint after the first completed assignment. Distinguish tokens, subscription allowance, credit/API charges and server cost; label unavailable metrics explicitly. Do not change the model, increase concurrency or enable extra billing without the applicable authority.
4. **Make CON-010's re-decision evidence-driven.** Show the original failure, the integrated change that resolves it, coverage of all applicable paths, remaining unknowns and the resulting predicate. Use INCONCLUSIVE only if justified by that evidence; retain FAIL for a remaining demonstrated violation. The expected 35 reasons must not become a target. The fresh reviewer checks the derivation, not agreement with a preselected status. Bind CON-010 and REQ-044 to the actual final evidence hashes.
5. **Make status corrections survive later fixes.** Derive limitation notices from finding/evidence state rather than permanent strings. Give all verdict-changing unlinked open items a dependency or justified disposition; do not claim that linking S-64 alone closes the whole traceability exception. Before promotion, verify the final candidate with the intended ignored-evidence archive in an isolated checkout and confirm its generated views. Keep the post-promotion check.
6. **Keep the delivery goal intact.** C's reviewed packet is a valid bounded milestone. It does not complete the multi-board foundation layers. Name the earliest remaining Layer 4 to 9 acceptance closure advanced by this batch and keep the other engineering work checkpointed. Preserve the first action of backing up all twelve unfinished files, H3's immutability and the accepted Layers 1 to 3.

Return only the amended paragraphs, corrected worker/dependency order and any genuinely unresolved authorization. Then present the revised plan for approval. After approval, execute it without another general planning round.

## Review boundary

This is a focused review of the supplied text, not a new electrical audit or a live verification of Claude's claimed recovery actions. The proposed CON-010 result may be correct; the plan needs a defensible acceptance test. The broader spending delegation may exist; its specific scope is not established by the pasted excerpt.
