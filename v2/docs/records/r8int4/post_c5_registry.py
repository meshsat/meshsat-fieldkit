"""After fnd/hc5's scripts on the r8int4 tree: REQ-052's IOHA binding (apply_docs printed REBIND NOT DONE), and the
IOHA change note corrected to what changed on this tree (board B's round 8 had already written the address block and
the section 6 part; only the FW-B08 and SC-HF-02 sentences and 10a's per-controller part were added). Edits by record
id with asserted old text. Run from the worktree root."""
import hashlib
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))
def sub_in(t, rid, a, b, n=1):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == n, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]
IO = hashlib.sha256(open('v2/docs/ARCH-PCB-B-IOHA.md', 'rb').read()).hexdigest()[:16]
OLDNOTE = ("it changed sections 6 and 10a only (the address block, the corrected PB1/PB2 finding with the FW-B08 "
           "pointer and the segment choice SC-HF-02 added, and 10a's per-controller part; on a tree before 99cde56b also "
           "the supervisors' part in section 6 and 10a's two H743 sentences)")
NEWNOTE = ("it changed sections 6 and 10a only (after section 6's corrected PB1/PB2 heading, the FW-B08 pointer and the "
           "segment choice SC-HF-02; 10a's per-controller part; the address block and the supervisors' part were board "
           "B's round 8 text already and are unchanged, r8int4)")
for rid in ('REQ-005', 'CFL-001'):
    i, j = rec(t, rid); r = t[i:j]
    # the note is wrapped by the yaml folded style; compare with whitespace normalised
    flat = ' '.join(r.split())
    assert ' '.join(OLDNOTE.split()) in flat, rid
    # rebuild: replace the wrapped occurrence by locating its words in the raw text
    words = OLDNOTE.split(); k0 = r.index(words[0] + ' ' + words[1] + ' ' + words[2])
    k = k0
    for w in words:
        k = r.index(w, k) + len(w)
    r = r[:k0] + ' '.join(NEWNOTE.split()) + r[k:]
    t = t[:i] + r + t[j:]
t = sub_in(t, 'REQ-052', '"v2/docs/ARCH-PCB-B-IOHA.md@08d44b37fa8e2717"', '"v2/docs/ARCH-PCB-B-IOHA.md@%s"' % IO)
t = sub_in(t, 'REQ-052', """          at af6e5821e21b70ef
""", """          at af6e5821e21b70ef
      - >-
          v2/docs/ARCH-PCB-B-IOHA.md re-read at the r8int4 integration of 27 September 2026 after the layer 5 closer's
          edit (hc5-layer5): it changed sections 6 and 10a only (the FW-B08 pointer and the segment choice SC-HF-02
          after section 6's corrected PB1/PB2 heading, and 10a's per-controller part); sections 4 and 15, which this
          reading rests on, are byte-identical to the file at 08d44b37fa8e2717, so it stands on the file at %s
""" % IO)
open(P, 'w').write(t)
print("post_c5_registry: REQ-052 on ARCH-PCB-B-IOHA.md %s; REQ-005 and CFL-001 notes corrected" % IO)
