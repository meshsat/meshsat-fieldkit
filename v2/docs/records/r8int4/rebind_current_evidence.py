"""CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md; after each render at the r8int4 integration they are
re-read and rebound. Usage: rebind_current_evidence.py OLD16 "<what moved>" "<CON-010 read>" "<REQ-044 read>"
(run from the worktree root). Each note starts with the path; the evidence_result is not touched."""
import hashlib, sys
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
old, moved, con010, req044 = sys.argv[1:5]
new = hashlib.sha256(open('v2/docs/CURRENT-EVIDENCE.md', 'rb').read()).hexdigest()[:16]
def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))
def wrap(s):
    words = s.split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur += ' ' + w
    return '\n'.join(lines + [cur]) + '\n'
for rid, why in (('CON-010', con010), ('REQ-044', req044)):
    i, j = rec(t, rid); r = t[i:j]
    a = '"v2/docs/CURRENT-EVIDENCE.md@%s"' % old; assert r.count(a) == 1, (rid, a)
    r = r.replace(a, '"v2/docs/CURRENT-EVIDENCE.md@%s"' % new)
    k = r.index('    evidence_bound_to:')
    note = "v2/docs/CURRENT-EVIDENCE.md re-read at the r8int4 integration of 27 September 2026: %s; %s, so it stands on the file at %s" % (moved, why, new)
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]
open(P, 'w').write(t); print("rebind_current_evidence: CON-010 and REQ-044 to", new)
