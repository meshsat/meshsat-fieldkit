"""A third `kind: tool` entry in v2/docs/evidence/COMPATIBILITY.md, for edge_length.py (27 September 2026, MESHSAT-1357,
the release finalizer of layers 1 to 3, branch fnd/rel2 rebased onto main 91894cd7).

The second release attempt's requirements validator change in rules_lib.py moves the code bundle of every writer that
imports it. On 953f5658 the two writers with current readings were intent_checks.py and derate.py, answered by two
entries. On 91894cd7 the consolidated re-take (8ea7867e, 5ca81eea) made edge_length.py's SI-001 readings on boards A,
B, C, D, E and P current too (bundle 9882ad1bc5620724, with rules_lib.py c0458c53923d7925), and a render of the rebased
branch reads all six TOOL_CHANGED. This script runs v2/docs/records/rel2/tool_compat.py over those readings (it exits
non-zero if any file of the bundle but rules_lib.py moved, or if any file of the bundle reaches a changed or added name
of rules_lib), writes its output beside itself, and adds the entry and a paragraph with asserted anchors. Run from
the worktree root. Taken by the session under the owner's standing rule of 26 September 2026."""
import subprocess, sys

BOARDS = ['pcb-a-power-a23', 'pcb-b-compute-b19', 'pcb-c-display-c8', 'pcb-d-aprs-d9', 'pcb-e1-dock-e7', 'pcb-p-pack-p2']
V = ['v2/ecad/%s/%s/edge_length.verdict.json' % (b, d) for b in BOARDS for d in ('out', 'routed')]
r = subprocess.run([sys.executable, 'v2/docs/records/rel2/tool_compat.py', '91894cd7'] + V, capture_output=True, text=True)
assert r.returncode == 0, r.stdout + r.stderr
OUT = 'v2/docs/records/rel2f/tool_compat_edge_length.out'
open(OUT, 'w', encoding='utf-8').write(r.stdout)
line = r.stdout.strip()
assert line.startswith('edge_length.py then 9882ad1bc5620724 now ') and line.endswith('reached by the bundle: none'), line
now = line.split(' now ')[1].split(';')[0]

P = 'v2/docs/evidence/COMPATIBILITY.md'
s = open(P, encoding='utf-8').read()


def sub(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); assert a != b
    return s.replace(a, b)


s = sub(s, "## Tool entries of 27 September 2026: two, and why\n", "## Tool entries of 27 September 2026: three, and why\n")
s = sub(s, """pin both bundles by content, so any later edit of any file of either bundle stops them applying by themselves. Taken by
the session under the owner's standing rule of 26 September 2026.

<!-- evidence-register: compatibility -->""", """pin both bundles by content, so any later edit of any file of either bundle stops them applying by themselves. Taken by
the session under the owner's standing rule of 26 September 2026.

**A third entry, for `edge_length.py` (the release finalizer of layers 1 to 3, the same day).** The change was rebased
onto main `91894cd7`, where the consolidated re-take (`8ea7867e`, `5ca81eea`) had made the SI-001 readings of boards A,
B, C, D, E and P current (`edge_length.py`, bundle 9882ad1bc5620724, with `rules_lib.py` at c0458c53923d7925); a render
of the rebased branch read all six TOOL_CHANGED. `v2/docs/records/rel2/tool_compat.py 91894cd7` over those twelve
verdict files (`out/` and `routed/` of each board; output `v2/docs/records/rel2f/tool_compat_edge_length.out`) shows the
same: `rules_lib.py` is the only file of the bundle that moved (c0458c53923d7925 to 6154bd6c15bdfa6b, the same change as
above), and no file of the bundle reaches a changed or added name (`edge_length.py:384` and `:440` call only
`board_facts()`, unchanged). With it, every reading the rules_lib.py change reaches on `91894cd7` reads VALID_HISTORICAL
and counts as current: SI-001 on boards A, B, C, D, E and P through this entry, PWR-001 on the same six and CMP-001 on
all seven through the two above (81 current rows before the rebase, 81 after: 62 CURRENT_CANDIDATE and 19 VALID_HISTORICAL).

<!-- evidence-register: compatibility -->""")

s = sub(s, """    method: "v2/docs/records/rel2/tool_compat.py 953f5658 with E5's derate verdict; output v2/docs/records/rel2/tool_compat.out"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
```""", """    method: "v2/docs/records/rel2/tool_compat.py 953f5658 with E5's derate verdict; output v2/docs/records/rel2/tool_compat.out"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
  - kind: tool
    tool: edge_length.py
    then: 9882ad1bc5620724
    now: %s
    summary: "rules_lib.py gained the requirements validator's SC- id check; nothing edge_length.py's bundle reaches moved"
    rationale: "The only file of the bundle that moved is rules_lib.py (c0458c53923d7925, the file at 91894cd7, to 6154bd6c15bdfa6b: validate_requirements and main changed, six names added, none removed, as in the two entries above). edge_length.py:384 and :440 call the module's board_facts() only, which did not change, and no file of the bundle takes a changed or added name from it."
    method: "v2/docs/records/rel2/tool_compat.py 91894cd7 with the edge_length verdicts of boards A, B, C, D, E and P (out and routed); output v2/docs/records/rel2f/tool_compat_edge_length.out; script v2/docs/records/rel2f/apply_compat.py"
    ruled_by: session
    ruled_on: 2026-09-27
    authority: "taken by the session under the owner's standing rule of 26 Sep 2026"
```""" % now)
open(P, 'w', encoding='utf-8').write(s)
print('apply_compat (rel2f): edge_length.py 9882ad1bc5620724 ->', now)
