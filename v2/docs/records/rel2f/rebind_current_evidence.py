"""CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md (27 September 2026, MESHSAT-1357, the release finalizer
of layers 1 to 3, branch fnd/rel2 rebased onto main 391d8579). After rules_status has run three times and rules_render
twice on the committed tree, this script asserts that the rows each reading rests on are unchanged against HEAD's page
(board D's RF-002 and SCH-004 rows for CON-010, board P's BAT-001 row for REQ-044; the note says which other rows
moved), then rebinds each with an evidence entry that starts with the path. The evidence_result is not touched.

Usage (from the worktree root, after the render and before its commit):
  rebind_current_evidence.py "<where the render was taken>" "<what moved on the page>"
"""
import hashlib, subprocess, sys

where, moved = sys.argv[1], sys.argv[2]
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P, encoding='utf-8').read()
CE = 'v2/docs/CURRENT-EVIDENCE.md'
old_page = subprocess.run(['git', 'show', 'HEAD:' + CE], capture_output=True, text=True, check=True).stdout
new_page = open(CE, encoding='utf-8').read()
old16 = hashlib.sha256(old_page.encode()).hexdigest()[:16]; new16 = hashlib.sha256(new_page.encode()).hexdigest()[:16]
assert old16 != new16, 'the page did not change; nothing to rebind'
for key in ('| D | RF-002', '| D | SCH-004', '| P | BAT-001'):
    a = [l for l in old_page.split('\n') if l.startswith(key)]; b = [l for l in new_page.split('\n') if l.startswith(key)]
    assert a == b and len(a) == 1, key


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def wrap(s):
    words = s.split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur += ' ' + w
    return '\n'.join(lines + [cur]) + '\n'


WHY = {'CON-010': "board D's RF-002 and SCH-004 rows keep the class and cause read above, so this constraint's own "
                  "reasons are unchanged and it stays INCONCLUSIVE",
       'REQ-044': "board P's BAT-001 row, which this reading rests on, its netlist 085f833362fbbda8 and every reason "
                  "given above are unchanged (the board P rows that moved are named above and none is BAT-001), so it "
                  "stays INCONCLUSIVE"}
for rid, why in WHY.items():
    i, j = rec(t, rid); r = t[i:j]
    a = '"%s@%s"' % (CE, old16); assert r.count(a) == 1, (rid, a)
    r = r.replace(a, '"%s@%s"' % (CE, new16))
    k = r.index('    evidence_bound_to:')
    note = "%s re-read at %s: %s; %s, on the file at %s" % (CE, where, moved, why, new16)
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]
open(P, 'w', encoding='utf-8').write(t); print("rebind_current_evidence: CON-010 and REQ-044 from", old16, "to", new16)
