"""After edit_docs.py (the second release attempt of layers 1 to 3, 27 September 2026, MESHSAT-1357, fnd/rel2 from
953f5658): every reading whose bound file those edits changed is re-read against what it rests on, which this script
first ASSERTS is byte-identical to the committed file (sections by heading, table rows by their first cell), and then
rebinds with an evidence entry that starts with the path; then the CONOPS needs pin (the needs table is asserted
unchanged) and the envelope's two pins (OPERATING-ENVELOPE changed in one header citation only). Edits by record id
with asserted old text. Run from the worktree root, before the commit that carries the edits (it reads HEAD)."""
import hashlib, re, subprocess, sys
sys.path.insert(0, 'v2/ecad/tools')
import rules_lib as R

P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P, encoding='utf-8').read()
full = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
head = lambda p: subprocess.run(['git', 'show', 'HEAD:' + p], capture_output=True, text=True, check=True).stdout
now = lambda p: open(p, encoding='utf-8').read()


def section(text, title):
    """The lines under the heading that starts with `title`, up to the next heading of the same or a higher level."""
    L = text.split('\n'); i = next(k for k, l in enumerate(L) if l.startswith('#') and l.lstrip('#').strip().startswith(title))
    lvl = len(L[i]) - len(L[i].lstrip('#')); j = i + 1
    while j < len(L) and not (L[j].startswith('#') and len(L[j]) - len(L[j].lstrip('#')) <= lvl): j += 1
    return '\n'.join(L[i:j])


def row(text, first):
    """Every table row whose first cell is `first` (a name can head a row in more than one table)."""
    hits = [l for l in text.split('\n') if l.startswith('| %s |' % first)]
    assert hits, first; return '\n'.join(hits)


def same(p, *parts):
    a, b = head(p), now(p)
    for kind, key in parts:
        f = section if kind == 's' else row
        assert f(a, key) == f(b, key), (p, kind, key)


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == 1, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]


def rebind(t, rid, path, text):
    old = hashlib.sha256(head(path).encode()).hexdigest()[:16]; new = full(path)[:16]
    t = sub_in(t, rid, '"%s@%s"' % (path, old), '"%s@%s"' % (path, new))
    i, j = rec(t, rid); r = t[i:j]; k = r.index('    evidence_bound_to:')
    words = (text % {'old': old, 'new': new}).split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur = cur + ' ' + w
    lines.append(cur)
    entry = '      - >-\n' + '\n'.join(lines) + '\n'
    assert entry.split('\n')[1].strip().startswith(path), (rid, path)
    return t[:i] + r[:k] + entry + r[k:] + t[j:]


I = ("re-read at the second release attempt of layers 1 to 3 of 27 September 2026 (fnd/rel2 from 953f5658, after the "
     "release reviews at f2b7fa66): ")
C = 'v2/docs/CONOPS.md'; T = 'v2/docs/TEST-PLAN.md'; O = 'v2/docs/OPERATING-ENVELOPE.md'
PW = 'v2/docs/feasibility/POWER-THERMAL.md'
CON_CH = ("the status header (lines 20 and 48: the first Review A pass cited by its filed name, and the release check's "
          "second step), M1's routes (the owner action and EQ-13 named), section 4's Reduced row (the three documents "
          "now follow it) and Hot stop row (the forced trigger named), section 4c's opening hand-off sentence and "
          "section 7a's opening and L-02 row change, and no number changed; ")
TP_CH = ("line 3 (the first Review A pass cited by its filed name, and the second release attempt's note), section 6's "
         "opening, row E3-H (its stepped run beyond the envelope and the NOT_VERIFIED rule) and section 7's opening "
         "change, and section 7 gains row P15 (the hot stop forced at room temperature); E3-L is unchanged; ")
OE_CH = "only line 36 changes (the first Review A pass cited by its filed name); no number changed; "
PW_CH = ("sections 1 (the reduced mode is slots 2 and 3 and the heat stage one module), 9.1, 9.2 and 9.3 (C1 and C3 shed "
         "to the reduced mode and then the heat stage; PS-RED named the one-module stage) and one hand-off line of "
         "section 11 change, with the line count and every figure unchanged; ")

# the readings, each asserted to rest on text that did not change
same(C, ('s', '2a.'))
t = rebind(t, 'REQ-005', C, C + " " + I + CON_CH + "section 2a, which this reading rests on, is byte-identical to the "
           "file at %(old)s, so it stands on the file at %(new)s")
same(C, ('s', 'M4.'), ('s', '4a.'), ('s', '4b.'), ('s', '4b.1'), ('s', '4f.'), ('s', '5.'), ('r', 'EMCON'),
     ('r', 'Charging'), ('r', 'Normal (full)'), ('r', 'Heat stage'))
t = rebind(t, 'CFL-016', C, C + " " + I + CON_CH + "M4, section 4's EMCON row, sections 4a, 4b, 4b.1 and 4f and section 5, "
           "which this reading rests on, are byte-identical to the file at %(old)s, so it stands on the file at %(new)s")
t = rebind(t, 'CFL-014', C, C + " " + I + CON_CH + "section 4's Charging row and section 5's case S4, which this reading "
           "rests on, are byte-identical to the file at %(old)s, so it stands on the file at %(new)s")
same(T, ('r', 'M7'), ('s', '4.'), ('r', 'E5'), ('r', 'E8'), ('s', '1.'), ('r', 'E3-L'))
t = rebind(t, 'CON-018', T, T + " " + I + TP_CH + "the M7 row, which this reading rests on, is byte-identical to the file "
           "at %(old)s, so it stands on the file at %(new)s")
t = rebind(t, 'CFL-016', T, T + " " + I + TP_CH + "section 4 and its EMCON sentence (measured with a receiver outside the "
           "kit, never the kit's own SDR), which this reading rests on, are byte-identical, so it stands on the file at "
           "%(new)s")
t = rebind(t, 'CFL-008', T, T + " " + I + TP_CH + "rows E5 (the sealed kit) and E8 (Peli's pressure valve), which this "
           "reading rests on, are byte-identical to the file at %(old)s, so it stands on the file at %(new)s")
t = rebind(t, 'CFL-009', T, T + " " + I + TP_CH + "section 1's deployed closed-lid state and section 6's closed-lid "
           "thermal test E3-L, which this reading rests on, are byte-identical to the file at %(old)s, so it stands on "
           "the file at %(new)s")


# every row of every table with a Purpose and a Verifies column states both (REQ-050, CFL-007)
def purpose_rows(text):
    L = text.split('\n'); out = []; i = 0
    while i < len(L):
        if L[i].startswith('|') and 'Purpose' in L[i] and 'Verifies' in L[i]:
            h = [c.strip() for c in L[i].strip().strip('|').split('|')]; pi, vi = h.index('Purpose'), h.index('Verifies')
            i += 2
            while i < len(L) and L[i].startswith('|'):
                c = [x.strip() for x in L[i].strip().strip('|').split('|')]; out.append((c[0], c[pi], c[vi])); i += 1
            continue
        i += 1
    return out
rows = purpose_rows(now(T)); before = purpose_rows(head(T))
assert len(rows) == len(before) + 1 == 47 and all(p and v for _, p, v in rows), (len(rows), len(before))
assert [r for r in rows if r[0] not in ('E3-H', 'P15')] == [r for r in before if r[0] != 'E3-H']
assert dict((r[0], r) for r in rows)['P15'][2] == 'REQ-077 (the hot stop)'
t = rebind(t, 'REQ-050', T, T + " " + I + TP_CH + "every table still carries its Purpose and Verifies columns, each "
           "filled on every row (47 rows now, P15 added with its purpose, acceptance, and REQ-077, a live record; E10 out "
           "of scope), E3-H's purpose and trace gain its stepped run and P15 and no other row's purpose or trace changed, "
           "and section 4 still states its purpose and the requirements it verifies, so it stands on the file at %(new)s")
t = rebind(t, 'CFL-007', T, T + " " + I + TP_CH + "every test row still states its purpose and the requirements it "
           "verifies (47 rows now, P15 added; E3-H's purpose and trace gain its stepped run and P15), which is this "
           "record's acceptance, so it stands on the file at %(new)s")
same(O, ('s', '4.'), ('s', '2.'), ('s', '3.'))
t = rebind(t, 'CFL-016', O, O + " " + I + OE_CH + "sections 2, 3 and 4, which this reading rests on, are byte-identical "
           "to the file at %(old)s, so it stands on the file at %(new)s")
t = rebind(t, 'CFL-014', O, O + " " + I + OE_CH + "section 3's paragraph beginning '**Corrected 26 September 2026.** This "
           "pa', which this reading rests on, is byte-identical, so it stands on the file at %(new)s")
same(PW, ('s', '0.'), ('s', '9.4'), ('s', '4.'), ('s', '6.'))
t = rebind(t, 'FEA-004', PW, PW + " " + I + PW_CH + "section 0's runtime and hot-end statements are byte-identical, and "
           "section 11 changes only in item 3's quoted hand-off (the one-module stage named), not in what this reading "
           "cites, so the record stays INCONCLUSIVE on the file at %(new)s")
t = rebind(t, 'REQ-072', PW, PW + " " + I + PW_CH + "section 4's PS-IDLE-SPEC row (42.8 W PLAN, 33.1 to 82.8), which this "
           "reading rests on, is byte-identical to the file at %(old)s, so the FAIL stands on the file at %(new)s")
t = rebind(t, 'CON-009', PW, PW + " " + I + PW_CH + "section 9.4, which this reading cites, is byte-identical to the file "
           "at %(old)s, so the record stays FAIL on the file at %(new)s")

# the CONOPS needs pin: the needs table (section 2) is unchanged
assert section(head(C), '2. Needs') == section(now(C), '2. Needs')
pin = re.search(r'needs_document_sha256: ([0-9a-f]{64})', t).group(1)
assert pin == hashlib.sha256(head(C).encode()).hexdigest()
t = t.replace('needs_document_sha256: ' + pin, 'needs_document_sha256: ' + full(C))
open(P, 'w', encoding='utf-8').write(t)

# the envelope's two pins: OPERATING-ENVELOPE changed in one header citation only
OLDF = hashlib.sha256(head(O).encode()).hexdigest(); NEWF = full(O)
for p, a, b in (('v2/ecad/tools/pcb_envelope.yaml',
                 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after the release check of layer 2 (' % OLDF,
                 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the second release attempt of layers 1 to 3 (line 36 cites the first Review A pass by its filed name; no number changed), before it by the integrator after the release check of layer 2 (' % NEWF),
                ('v2/ecad/tools/pcb_rules_coverage.yaml', 'verified_sha: "%s",' % OLDF, 'verified_sha: "%s",' % NEWF)):
    s = open(p, encoding='utf-8').read(); assert s.count(a) == 1, p; open(p, 'w', encoding='utf-8').write(s.replace(a, b))
print("post_docs_registry: 15 rebinds, the needs pin and the envelope's two pins re-taken")
