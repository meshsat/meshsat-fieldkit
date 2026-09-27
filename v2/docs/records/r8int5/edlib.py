"""Small helpers for the r8int5 integration's edit scripts: replace text exactly once (idempotent by a marker),
and rebind registry records to a file's new sha16 with a note that starts with the path."""
import hashlib, os, re

def sha16(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]

def once(path, old, new, marker=None):
    t = open(path, encoding='utf-8').read()
    if marker and marker in t:
        return False
    n = t.count(old)
    assert n == 1, "%s: expected the old text once, found %d: %r" % (path, n, old[:90])
    t2 = t.replace(old, new)
    assert t2 != t
    open(path, 'w', encoding='utf-8').write(t2)
    return True

def _rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1
    j = t.find('\n  - id: ', i + 5)
    k = t.find('\n\n# ', i)
    ends = [x for x in (j, k) if x > 0]
    e = min(ends) + 1 if ends else len(t)
    return i, e

def wrap(s, first='          ', rest='          ', width=120):
    words = s.split(); lines = []; cur = first.rstrip()
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip():
            lines.append(cur); cur = rest + w
        else:
            cur = (cur + ' ' + w) if cur.strip() else (first + w)
    return '\n'.join(lines + [cur]) + '\n'

def rebind(reqpath, rid, relpath, root, note, marker=None):
    """Move rid's evidence_bound_to entry for relpath to the tree's sha16 and add an evidence note (which must start
    with relpath) before evidence_bound_to. Returns the old sha16, or None when already bound to the current file."""
    assert note.startswith(relpath), note[:60]
    t = open(reqpath, encoding='utf-8').read()
    i, j = _rec(t, rid); r = t[i:j]
    new = sha16(os.path.join(root, relpath))
    m = re.search(r'"?%s@([0-9a-f]{16})"?' % re.escape(relpath), r)
    assert m, (rid, relpath)
    old = m.group(1)
    if old == new:
        return None
    r = r.replace('%s@%s' % (relpath, old), '%s@%s' % (relpath, new))
    k = r.index('    evidence_bound_to:')
    note = note.replace('{NEW}', new).replace('{OLD}', old)
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]
    open(reqpath, 'w', encoding='utf-8').write(t)
    return old
