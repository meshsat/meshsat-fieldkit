"""r8int6: CON-010 and REQ-044 are bound to v2/docs/CURRENT-EVIDENCE.md. After the r8int6 integration's evidence phase
(main's gitignored evidence copied in by main's ignored-file list, claims_check re-taken from v2/ecad, rules_status three
times and rules_render twice on the committed integration), this script reads the rows each reading rests on in the old
page (HEAD's) and the new one (board D's RF-002 and SCH-004 rows for CON-010, board P's BAT-001 row for REQ-044) and
writes what each row says now into the note, then rebinds each with an evidence entry that starts with the path. The
evidence_result is not touched: the note says whether the rows it rests on moved, and if they did, what they read.

Usage (from the worktree root, after the render and before its commit):
  rebind_current_evidence_r8int6.py "<where the render was taken>" "<what moved on the page>" <base commit>
The rows are compared with the page at the base commit (main's), which the integration's readings were copied from.
"""
import hashlib, subprocess, sys

where, moved, BASE = sys.argv[1], sys.argv[2], sys.argv[3]
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P, encoding='utf-8').read()
CE = 'v2/docs/CURRENT-EVIDENCE.md'
old_page = subprocess.run(['git', 'show', BASE + ':' + CE], capture_output=True, text=True, check=True).stdout
new_page = open(CE, encoding='utf-8').read()
new16 = hashlib.sha256(new_page.encode()).hexdigest()[:16]


def rows(page, key):
    return [" ".join(l.split()) for l in page.split('\n') if l.startswith(key)]


def said(key):
    a, b = rows(old_page, key), rows(new_page, key)
    if a == b: return "%s as at %s (%s)" % (key.strip('| '), BASE, "; ".join(x[:160] for x in b) or "no row")
    return "%s now reads %s (it read %s at %s)" % (key.strip('| '), "; ".join(x[:200] for x in b) or "no row",
                                                  "; ".join(x[:200] for x in a) or "no row", BASE)


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def wrap(s):
    words = s.split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur += ' ' + w
    return '\n'.join(lines + [cur]) + '\n'


import re
WHY = {'CON-010': [said('| D | RF-002'), said('| D | SCH-004')],
       'REQ-044': [said('| P | BAT-001')]}
for rid, why in WHY.items():
    i, j = rec(t, rid); r = t[i:j]
    m = re.search(r'"%s@([0-9a-f]{16})"' % re.escape(CE), r); assert m, rid
    old16 = m.group(1)
    if old16 == new16: print(rid, "already bound to", new16); continue
    res = re.search(r'(?m)^    evidence_result: (\S+)', r).group(1)
    r = r.replace('"%s@%s"' % (CE, old16), '"%s@%s"' % (CE, new16))
    k = r.index('    evidence_bound_to:')
    note = ("%s re-read at %s (the file at %s before): %s; the rows this reading rests on: %s; the reading itself is "
            "not re-taken by the integration, so it stands %s on the file at %s" % (CE, where, old16, moved, "; ".join(why), res, new16))
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]
    print(rid, "from", old16, "to", new16)
open(P, 'w', encoding='utf-8').write(t)
