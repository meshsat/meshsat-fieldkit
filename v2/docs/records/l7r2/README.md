# l7r2: the Layer 7 items other layers assigned, round 2 (MESHSAT-1357)

3 October 2026, the Layer 7 author, worktree `l7r2` on branch `fnd/l7r2` from `fnd/int28` at `a1f696de`. Prototype design, desk
arithmetic: nothing has been bought, built or measured. The items: the sealed RJ45 and its shield path (record l8gnd F01), the bonding
strap, lugs and stud (l8gnd F07), the right-angle SMA plug (CASE-MARGINS M17g, M17x), the fans' lead terminations, the cooler fan's fit
and bracket (record l7pwr F-L7-03), the fans' leads, and J_AB2 and the MAIN lead's lengths with W4-F17 (Layer 5 round 2's TBD rows).

| File | What it is |
|---|---|
| `L7-R2-ITEMS.md` | The page: per item the decision or the finding with its exact missing fact, the dimension chains, what transfers to T-H1's mock-up, the prices read, the LAYER-STATUS rows proposed, the findings and the decisions |
| `l7r2_items.py`, `l7r2_items.out` | The script (`python3 v2/docs/records/l7r2/l7r2_items.py` from the root, two seconds) and its output; it pins 21 inputs by sha256, reads the makers' figures from the transcription and re-reads the ones in the tree's held sheets, and prints the predicates the test reads |
| `apply_panel1450_coolers_r2.py` | DRAFT for v2/cad's owner: the cooler fans' envelopes in panel1450.py's B16_MODULES (40 x 40 x 20 on a bracket, Y 46.745 to 86.745, 39.56 above board B) and the heatsink at the maker's 12.7; refuses the tree's own file before its release |
| `fetch_held_back.py` | Fetches the seven makers' documents into `held/` (to be ignored, F-R2-11), each checked by sha256 |
| `inputs/` | The inputs copied from other branches with their commit, path and sha256; the makers' drawings transcribed; the FindChips readings |
| `clarification/` | Drafts for the owner to send: Glenair (233-330), Amphenol LTW (RCP-5SPFFH-SCM7001), Sanyo Denki (the fans' leads and PWM); nothing sent |

The predicates are held by `v2/ecad/tools/tests/test_l7r2.py`: `env -C v2/ecad/tools/tests python3 run.py test_l7r2 test_public_hygiene`.
