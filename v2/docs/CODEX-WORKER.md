# The Codex worker: how a bounded job is given to a second model (MESHSAT-1357)

Written 28 September 2026. Prototype design: no V2 board has been built, ordered or measured. This note describes a
working arrangement, not a product feature. It changes nothing of the layered plan in `EXECUTION-PLAN.md`, of the stage
gates, or of who decides: the integrating session (the coordinator) commits, integrates and accepts; a worker of either
model family returns a candidate. An AI check is an AI review, never a qualified engineering review.

## 1. What is installed

| Item | Value |
|---|---|
| Tool | Codex CLI, installed for the coordinator's own operating-system user by the maker's standalone installer (`https://chatgpt.com/codex/install.sh`, read before it was run; its sha256 and the installed version are in the checkpoint of `EXECUTION-PLAN.md`), pinned to the installed version so that it does not update itself |
| Sign-in | the owner's ChatGPT sign-in by device code, completed by the owner in a browser. No API key is used and no API credit is spent. The credential stays where the tool stores it, readable by that user alone; it is never printed, copied or committed |
| Model | `gpt-6-astra` at reasoning effort `xhigh`, requested on every invocation; the tool's global defaults are left as installed |
| Launcher | `run_codex_task.py` with `codex-job-result.schema.json`, its tests and the worker's instruction template: local tooling of the coordinator, beside the box helpers, not in this repository |
| Run records | one new directory per launch, outside the repository and outside `/tmp`: the job, the prompt, the configuration and version, the event stream, the error stream, the result and the coordinator's assessment |

## 2. How a job is given

The coordinator writes a job specification: a job id, the owner, the kind (review or author), the base commit, the
absolute worktree, the requirements and open items it serves, the inputs with their sha256, the permitted files, the
deliverables, the acceptance checks, a time limit and the usage authorization. The prompt is small: the task, the
inputs, the makers' documents it needs by path. Missing evidence stays missing.

The launcher runs `codex exec` with an argument array and the prompt on standard input, never a shell line built from
task text: approval policy `never` (a blocked operation fails visibly instead of waiting for a person), the sandbox
`read-only` for a review and `workspace-write` with the network off for an authoring job in that job's own worktree,
the model and effort above, the JSON event stream, the result schema. It switches off the tool's own sub-agents,
plugins, skill discovery and goals for the job. It never uses the tool's unrestricted modes.

## 3. Ownership

- One author per worktree and per branch, whichever model writes. The launcher takes an atomic lock on the worktree; a
  lock is stale only when the process that took it is gone, never on a process id alone.
- A job's worktree is new, made from a recorded commit. No occupied worktree is lent to a job.
- A worker edits only its permitted files. It never commits, pushes, rebases or touches a shared registry: those are
  the coordinator's. The permitted files are enforced by inspection after the run, since a sandbox is not a per-file list.
- The author of an item never closes it. A candidate written by one model family is reviewed by a reviewer who did not
  see the author's reasoning and who reproduces the calculation or the check from the sources. Two models agreeing is
  not evidence by itself; the reproduced numbers are.

## 4. What counts as a result

The outcome is computed by the launcher, not taken from the worker's word. A job is a **candidate ready for review**
only if the child ended normally, the event stream carries a completed turn and no failed turn or error, the final
message is JSON that fits the schema and names this job and this base commit, the branch has not moved, every path
that changed, appeared or disappeared is inside the permitted files (none for a review), and every declared
deliverable exists. Anything else is a timeout, a failure, an invalid result or an out-of-scope run, whatever the
result file says. A candidate is never an accepted item: acceptance is the coordinator's, after the review, on the
integrated revision.

## 5. Limits

- One coordinator and at most two active workers across both model families, reviewers included. No worker starts
  another agent or calls another model.
- A time limit per job (five minutes for a fixture call, twenty for a bounded engineering job); at the limit the
  launcher ends the child's own process group, keeps what was written and records a timeout.
- Usage is read from the event stream per run and reconciled before the next job. A dollar figure computed from list
  prices is an estimate, not a bill; under the ChatGPT sign-in the usage draws on the plan's allowance.
- Two failures on the same fault change the diagnosis or return one precise blocker.
- This arrangement creates no authority to rent machines, buy credit, publish, or contact anyone.

## 6. Recovery

Every run directory is kept and never reused. A job that must continue is resumed by the session id its own run
recorded, never by "the last session", and only after its worktree and its earlier output are reconciled. If the tool
or the sign-in fails, new launches stop and the work continues with the coordinator's own workers; no worktree is
deleted and no accepted change is rolled back.
