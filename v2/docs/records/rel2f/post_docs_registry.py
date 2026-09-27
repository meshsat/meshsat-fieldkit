"""After edit_docs.py (the release finalizer of layers 1 to 3, 27 September 2026, MESHSAT-1357, fnd/rel2 rebased onto
main 391d8579 and then 91894cd7): CONOPS changed in its status header only (line 3, the status line, and lines 48 to 49, the Review A
paragraph's last sentence), which records layer 2 BASELINED. This script ASSERTS that against HEAD (the same line
count, only those three lines differ, everything from section 1 on byte-identical), re-pins `needs_document_sha256`
(the validator compares the needs table itself), and rebinds each reading bound to CONOPS with an evidence entry that
starts with the path. Nothing else in a record changes. Run from the worktree root, before the commit that carries the
edits (it reads HEAD)."""
import hashlib, re, subprocess

P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P, encoding='utf-8').read()
C = 'v2/docs/CONOPS.md'
old = subprocess.run(['git', 'show', 'HEAD:' + C], capture_output=True, text=True, check=True).stdout
new = open(C, encoding='utf-8').read()
oL, nL = old.split('\n'), new.split('\n')
assert len(oL) == len(nL)
changed = [k + 1 for k in range(len(oL)) if oL[k] != nL[k]]
assert changed == [3, 48, 49], changed
first = next(k for k, l in enumerate(oL) if l.startswith('## 1.'))
assert oL[first:] == nL[first:] and first > 49
o64 = hashlib.sha256(old.encode()).hexdigest(); n64 = hashlib.sha256(new.encode()).hexdigest()
a = 'needs_document_sha256: %s\n' % o64
assert t.count(a) == 1, 'the needs pin is not HEAD\'s CONOPS'
t = t.replace(a, 'needs_document_sha256: %s\n' % n64)


def wrap(s):
    words = s.split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur += ' ' + w
    return '\n'.join(lines + [cur]) + '\n'


o16, n16 = o64[:16], n64[:16]
ids = []
for m in list(re.finditer(r'\n  - id: (\S+)\n', t)):
    rid = m.group(1)
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); j = j + 1 if j > 0 else len(t)
    r = t[i:j]; b = '"%s@%s"' % (C, o16)
    if b not in r: continue
    assert r.count(b) == 1, rid
    r = r.replace(b, '"%s@%s"' % (C, n16))
    k = r.index('    evidence_bound_to:')
    note = ("%s re-read at the release finalizer of layers 1 to 3 of 27 September 2026 (fnd/rel2 rebased onto main "
            "91894cd7, after the second release check at eb9f9030): only its status header changes, line 3 (the status "
            "line: layer 2 BASELINED at 79963b3b on v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md) and lines 48 "
            "to 49 (the Review A paragraph's last sentence), with the line count kept; every section from section 1 on, which "
            "this reading rests on, is byte-identical to the file at %s, so it stands on the file at %s" % (C, o16, n16))
    r = r[:k] + '      - >-\n' + wrap(note) + r[k:]
    t = t[:i] + r + t[j:]; ids.append(rid)
assert ids, 'no reading was bound to CONOPS'
open(P, 'w', encoding='utf-8').write(t)
print('post_docs_registry (rel2f): needs pin %s to %s; rebound %s' % (o16, n16, ', '.join(ids)))
