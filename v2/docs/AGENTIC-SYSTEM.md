# The agentic system: what it is, what contains it, and how to run it

12 September 2026 (MESHSAT-862). The control-plane programme in `CONTROL-PLANE.md` names five tiers.
Tiers 0 and 1 (the deterministic runner and the supervisor) and stage 0 (the verdict channel, the
ledger, the never-auto floor, the execution pin) have been running since 11 September. **This
document is tiers 2 and 2b, the proposing agent and the reviewer, which is where a model enters the
loop for the first time.**

## The loop, in the order that is the contract

```
  counted evidence              verdict JSONs, the ledger, the board's declarations, the failure profile
    -> tier 2 proposes ONE arm with a written prediction        a model, contained by tools/agent/schema.py
    -> the validator accepts or refuses it                      mechanical, fail closed
    -> the deterministic runner executes it                     tools/arms.py, no model anywhere near it
    -> the mechanical judge grades it against the prediction    arms.grade, never the model
    -> tier 2 drafts the record entry from the numbers          a model
    -> tier 2b reviews it with fresh eyes                       a different context, artefacts only
    -> the ledger chains all of it                              tools/ledger.py
```

**The judge is never the proposer and the reviewer cannot move the grade.** Those two sentences are
the reason this is worth building. The width a model adds pays only against an objective that is
trustworthy, and the objective here is a pair count printed by a tool that has no idea a model exists.

## What contains it

Every property below is a property of the code, proved by a test that fails when the property is
removed (`tests/test_agent_contract.py`, 25 rules; `tests/mutate_agent.sh` re-proves the eight text
rules by putting each defect back into a copy of the tree and requiring its rule to fail).

| property | where it lives |
|---|---|
| the proposer cannot actuate | `propose.py`, `schema.py`, `evidence.py` and `client.py` contain no `subprocess`, `exec`, `eval`, `os.system` or delete, and a test reads them to say so |
| the model owns three fields | the arm's name, its env knobs and its prediction. The board, the project, the placed board, the passes and the timeout come from `agent/templates/<letter>.json`, which is the board's own declaration. A proposal that sets one of those is refused rather than stripped |
| a knob nobody reads is refused | the authority is `pair_preroute.py` parsed for its `os.environ` reads, never the knob document, which can drift |
| a reserved knob is refused with its reason | `PAIR_INNER`, `PAIR_INNER_GAP`, `PAIR_INNER_WIDTH`, `PAIR_LAYERS`, `PAIR_HOP_LAYERS`. These are impedance targets and layer decisions, which are the owner's under the never-auto floor; the refusal names `OWNER-DECISIONS-2026-09-11.md` |
| a basis-locked knob is refused | `PAIR_VENV`, `PAIR_FAST_SEARCH`, `PAIR_FAST_STUBS`, `PAIR_MAP_CHECK`. They choose which kernel runs, are proved equivalent, and a row that moves them is not comparable with one that does not |
| an arm with no prediction is refused | an arm nobody predicted cannot disappoint, so it cannot teach anything |
| a basis that says nothing is refused | at least 40 characters, and it may not restate its own number |
| an arm name is a slug | it becomes the directory `arm-<letter>-<name>` that `arms.py` removes with `rmtree`. `arms.py` refuses a non-slug name itself, whoever wrote the spec |
| a repeat is refused | an arm whose knobs are already in the ledger, unless `--allow-repeat` asks for reproducibility on purpose |
| a knob that never arrived is not a measurement | `pair_preroute.py` echoes the knobs its process received, `arms.py` compares them with what the arm asked for, and a mismatch is INFRA_FAIL. **This guard exists because tier 2b found its absence on the first cycle it ever reviewed** |
| a review must say where | a REJECT with no critical or major finding, an APPROVE carrying one, or a finding with no location is refused for its shape before it is read |
| nothing about the endpoint is in the tree | this repo mirrors publicly within minutes. The code carries no default base and no default key, and a test greps the agent for estate hosts, private addresses and key-shaped strings |
| the config is outside the tree and mode 600 | `~/.config/meshsat-fieldkit/agent.env`, the pattern `kb.env` already set. A world-readable config is refused before any call |
| a missing config is INFRA_FAIL | never a fallback, never a default model, never a quiet skip |
| no gate imports the agent | a model may inform a proposal and may never judge a board, the same separation the retrieval store runs under |
| the budget is counted in work | calls and tokens, never seconds. A clock has decided a result on this project twice and was wrong both times |
| every call is recorded | the sha256 of what was sent and what came back, the model, the token counts, chained into `out/agent/agent.jsonl` |

## Configuration

`~/.config/meshsat-fieldkit/agent.env`, mode 600, outside the tree:

```
MESHSAT_LLM_BASE=<the proxy's base URL>
MESHSAT_LLM_MODEL=<the model alias>
MESHSAT_LLM_REVIEW_MODEL=<the alias tier 2b uses>
MESHSAT_LLM_KEY=<a virtual key scoped to that alias alone>
```

The key in use is a LiteLLM virtual key **scoped to one model alias, with a budget and a rate limit**,
so the worst case of a leak is bounded and it is revocable in one call without touching anything else
on the estate. `MESHSAT_AGENT_ENV` points the tools at a different file; `MESHSAT_AGENT_MAX_CALLS` and
`MESHSAT_AGENT_MAX_TOKENS` cap one run.

## Running it

```
# the endpoint answers and the key works, with nothing else touched
python3 tools/agent/client.py check

# tier 2 alone: propose and stop. Tier 2 never actuates, so this is the whole of it
python3 tools/agent/propose.py --letter b --template tools/agent/templates/b.json \
    --profile out/b19-profile.json --ledger out/agent/arms.jsonl

# one full cycle, with the run happening where the boards are
python3 tools/agent/loop.py --letter b --template tools/agent/templates/b.json \
    --profile out/b19-profile.json --ledger out/agent/arms.jsonl \
    --exec "<a command that runs arms.py where KiCad is> {spec} {result}" \
    --result out/agent/arms.jsonl

# tier 2b alone, on a diff: fresh eyes before a commit
python3 tools/agent/review.py --diff-range HEAD~1..HEAD --verdict-dir out
```

`--exec` takes the command on the command line and it is never stored in the tree, because the machine
it names is not this repository's business. Without `--exec` the loop runs `arms.py` in process, which
needs `pcbnew`; on a host without it, the absence is INFRA_FAIL and never a silent skip.

## What it does not promise

That the boards get better because of the loop. What a model adds here is width of search, and the
reviews' own table says design quality does not move with it. What it does add, measurably, is a
second reader that has no stake in the change: on its first cycle tier 2b found that the pipeline was
reporting a pair count under a knob with nothing to show the knob had reached the tool, which is the
exact shape of four of the six defects that stood between A24's routed board and its deliverable.
