"""After rules_status (three runs) and rules_render (two) at the release check of layers 1 to 3 (27 September 2026,
MESHSAT-1357, fnd/r8int4 after 116c432e): CON-010 and REQ-044, bound to the rendered CURRENT-EVIDENCE.md, re-read and
rebound. The page changed in two places only: the class-change note's count of rows whose first failing cause moved
(161 to 154), and the cause table, where ENV-002's reading on each of the seven boards moves from TOOL_CHANGED to
UNBOUND (claims_check re-taken under its current tool after f2b7fa66; a release-package reading records no artefact by
content). Edits by record id with asserted old text. Run from the worktree root."""
import hashlib
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
full = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == 1, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]


def rebind(t, rid, path, old, text):
    new = full(path)[:16]
    t = sub_in(t, rid, '"%s@%s"' % (path, old), '"%s@%s"' % (path, new))
    i, j = rec(t, rid); r = t[i:j]; k = r.index('    evidence_bound_to:')
    words = (text % new).split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur = cur + ' ' + w
    lines.append(cur)
    return t[:i] + r[:k] + '      - >-\n' + '\n'.join(lines) + '\n' + r[k:] + t[j:]


CE = 'v2/docs/CURRENT-EVIDENCE.md'
I = ("v2/docs/CURRENT-EVIDENCE.md re-read at the release check of layers 1 to 3 of 27 September 2026: rendered after "
     "rules_status ran three times on the committed tree (116c432e), only the class-change note's count (161 to 154 rows "
     "whose first failing cause moved) and the cause table change, ENV-002's reading on each of the seven boards moving "
     "from TOOL_CHANGED to UNBOUND (claims_check re-taken under its current tool after f2b7fa66); ")
t = rebind(t, 'CON-010', CE, '23ec56778cee856e', I + "board D's RF-002 and SCH-004 keep the class and cause read above, "
           "so this constraint's own reasons are unchanged and it stays INCONCLUSIVE, so it stands on the file at %s")
t = rebind(t, 'REQ-044', CE, '23ec56778cee856e', I + "board P's row, its netlist 085f833362fbbda8 and every reason given "
           "above are unchanged, so it stands on the file at %s")
open(P, 'w').write(t)
print("post_release_evidence: CON-010 and REQ-044 rebound to %s" % full(CE)[:16])
