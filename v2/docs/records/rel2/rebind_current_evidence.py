"""CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md. After rules_status ran three times and rules_render
twice on the committed tree of the second release attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357, fnd/rel2),
the rows each reading rests on are asserted unchanged against HEAD's page (board D's RF-002 and SCH-004 rows for CON-010,
board P's BAT-001 row for REQ-044) and each is rebound with an evidence entry that starts with the path. The
evidence_result is not touched. Run from the worktree root, after the render and before its commit."""
import hashlib, subprocess
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P, encoding='utf-8').read()
CE = 'v2/docs/CURRENT-EVIDENCE.md'
old_page = subprocess.run(['git', 'show', 'HEAD:' + CE], capture_output=True, text=True, check=True).stdout
new_page = open(CE, encoding='utf-8').read()
old16 = hashlib.sha256(old_page.encode()).hexdigest()[:16]; new16 = hashlib.sha256(new_page.encode()).hexdigest()[:16]
assert old16 != new16
for key in ('| D | RF-002', '| D | SCH-004', '| P | BAT-001'):
    a = [l for l in old_page.split('\n') if key in l]; b = [l for l in new_page.split('\n') if key in l]
    assert a == b and len(a) == 1, key


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def wrap(s):
    words = s.split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur += ' ' + w
    return '\n'.join(lines + [cur]) + '\n'


MOVED = ("rendered after rules_status ran three times on the committed tree of the second release attempt of layers 1 to 3 "
         "(fnd/rel2, d535c17e), PWR-001 on boards A, D and E and CMP-001 on E5 move from CURRENT_CANDIDATE to "
         "VALID_HISTORICAL (the two kind: tool entries of v2/docs/evidence/COMPATIBILITY.md for rules_lib.py's validator "
         "change), SI-001's first failing cause on six boards moves to TOOL_CHANGED (edge_length.py's bundle holds "
         "rules_lib.py; the class is unchanged, awaiting revalidation), and the counts, the class-change note and the "
         "register's entry count follow")
WHY = {'CON-010': "board D's RF-002 and SCH-004 rows keep the class and cause read above, so this constraint's own "
                  "reasons are unchanged and it stays INCONCLUSIVE",
       'REQ-044': "board P's BAT-001 row, its netlist 085f833362fbbda8 and every reason given above are unchanged (board "
                  "P's SI-001 row moves its first cause only, a row this reading does not rest on)"}
for rid, why in WHY.items():
    i, j = rec(t, rid); r = t[i:j]
    a = '"%s@%s"' % (CE, old16); assert r.count(a) == 1, (rid, a)
    r = r.replace(a, '"%s@%s"' % (CE, new16))
    k = r.index('    evidence_bound_to:')
    note = "%s re-read at the second release attempt of layers 1 to 3 of 27 September 2026: %s; %s, so it stands on the file at %s" % (CE, MOVED, why, new16)
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]
open(P, 'w', encoding='utf-8').write(t); print("rebind_current_evidence: CON-010 and REQ-044 to", new16)
