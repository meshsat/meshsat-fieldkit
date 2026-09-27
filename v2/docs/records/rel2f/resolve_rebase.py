"""Resolve the rebase of fnd/rel2 (the second release attempt of layers 1 to 3, d535c17e) onto main 391d8579 (set 5),
27 September 2026, MESHSAT-1357, by the release finalizer (second attempt). Run from the worktree root while the
rebase is stopped on d535c17e with conflicts in the registry, ENGINEERING-QUESTIONS.md and LAYER-STATUS.md.

Set 5 took the ids the second release attempt had taken on 953f5658: session choices SC-51 to SC-57 and engineering
question EQ-25. Main's ids stand; the second release attempt's SC-51 to SC-56 become SC-58 to SC-63 and its EQ-25
becomes EQ-26 (next free on main). M-02 and TEST-PLAN P15 are free on main and keep their ids. Only lines the second
release attempt wrote are renumbered: a line of main's file is never touched.

  - registry: main's session choices SC-51 to SC-57 kept whole, the attempt's six appended as SC-58 to SC-63; the open
    items hunk keeps main's S-64 to S-76 and appends M-02; each evidence hunk keeps main's entries, appends the
    attempt's, and binds each file at the sha256/16 its current worktree content has (the side that matches);
  - ENGINEERING-QUESTIONS.md: main's header sentence for set 5 kept and the attempt's sentence appended; both index rows
    kept, the attempt's as EQ-26;
  - LAYER-STATUS.md: the layer 4 integrator line is main's with the attempt's appended tail (the two changed different
    parts of the line);
  - then every line the attempt added (a line in the file that is not in main's file) in these files and in
    HW-FW-CONTRACT.md and GLOSSARY.md is renumbered.
"""
import hashlib, re, subprocess, sys

MAIN = '391d8579'
MARK_A, MARK_M, MARK_B = '<<<<<<< ', '=======', '>>>>>>> '
SCMAP = {'SC-%d' % n: 'SC-%d' % (n + 7) for n in range(51, 57)}
EQMAP = {'EQ-25': 'EQ-26'}


def git_show(rev, path):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True, text=True, check=True).stdout


def sha16(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()[:16]


def hunks(text):
    """Split into a list of str (plain) and tuples (ours, theirs)."""
    out = []; lines = text.split('\n'); i = 0; buf = []
    while i < len(lines):
        if lines[i].startswith(MARK_A):
            out.append('\n'.join(buf)); buf = []
            j = i + 1; ours = []
            while lines[j] != MARK_M: ours.append(lines[j]); j += 1
            k = j + 1; theirs = []
            while not lines[k].startswith(MARK_B): theirs.append(lines[k]); k += 1
            out.append((ours, theirs)); i = k + 1
        else:
            buf.append(lines[i]); i += 1
    out.append('\n'.join(buf))
    return out


def join(parts):
    s = []
    for p in parts:
        s.append(p if isinstance(p, str) else '\n'.join(p))
    return '\n'.join(s)


def renum_line(line, maps):
    for a, b in maps.items():
        line = re.sub(r'\b%s\b' % re.escape(a), b, line)
    return line


# ---------------------------------------------------------------- registry
P = 'v2/ecad/tools/pcb_requirements.yaml'
C = open(P, encoding='utf-8').read()
main_reg = git_show(MAIN, P)
mine_reg = git_show('d535c17e', P)
END = '\n# What is still open.'
i0 = C.index('\n  - id: SC-51\n') + 1; i1 = C.index(END)
assert C[i0:i1].count(MARK_A) == 6, C[i0:i1].count(MARK_A)
m0 = main_reg.index('\n  - id: SC-51\n') + 1; m1 = main_reg.index(END)
r0 = mine_reg.index('\n  - id: SC-51\n') + 1; r1 = mine_reg.index(END)
main_sc = main_reg[m0:m1].rstrip('\n') + '\n'
mine_sc = mine_reg[r0:r1].rstrip('\n') + '\n'
assert mine_sc.count('\n  - id: SC-') + mine_sc.startswith('  - id: SC-') == 6
assert main_sc.count('\n  - id: SC-') + main_sc.startswith('  - id: SC-') == 7
mine_sc = '\n'.join(renum_line(l, SCMAP) for l in mine_sc.split('\n'))
for n in range(58, 64): assert ('  - id: SC-%d\n' % n) in mine_sc
C = C[:i0] + main_sc + mine_sc + '\n' + C[i1 + 1:] if C[i1 - 1] == '\n' else None
assert C is not None

parts = hunks(C); res = []
for p in parts:
    if isinstance(p, str): res.append(p); continue
    ours, theirs = p
    if ours and ours[0].startswith('  - id: S-64'):
        # open items: main's S-64 to S-76, then the attempt's M-02
        assert theirs[0].startswith('  - id: M-02'); res.append('\n'.join(ours + theirs)); continue
    ko = ours.index('    evidence_bound_to:'); kt = theirs.index('    evidence_bound_to:')
    ent = ours[:ko] + ['      - >-'] + theirs[:kt]
    bo = ours[ko + 1:]; bt = theirs[kt + 1:]
    def pairs(b):
        out = []
        for l in b:
            m = re.match(r'^      - "(.+)@([0-9a-f]{16})"$', l); assert m, l; out.append((m.group(1), m.group(2)))
        return out
    po = pairs(bo); pt = dict(pairs(bt)); merged = []
    for path, h in po:
        cur = sha16(path)
        if h == cur: merged.append((path, h))
        elif pt.get(path) == cur: merged.append((path, cur))
        else: raise SystemExit('no side binds %s at its current %s (%s / %s)' % (path, cur, h, pt.get(path)))
    for path, h in pt.items():
        if path not in dict(po):
            assert h == sha16(path), (path, h); merged.append((path, h))
    res.append('\n'.join(ent + ['    evidence_bound_to:'] + ['      - "%s@%s"' % x for x in merged]))
C = '\n'.join(res)
assert MARK_A not in C and '\n=======\n' not in C
# the attempt's own lines outside the session choices: renumber lines that main's file does not have
main_lines = set(main_reg.split('\n'))
C = '\n'.join(l if l in main_lines else renum_line(l, {**SCMAP, **EQMAP}) for l in C.split('\n'))
open(P, 'w', encoding='utf-8').write(C)
print('registry resolved')

# ---------------------------------------------------------------- ENGINEERING-QUESTIONS.md
E = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
C = open(E, encoding='utf-8').read(); main_eq = git_show(MAIN, E)
parts = hunks(C); res = []; n = 0; done = set()
for p in parts:
    if isinstance(p, str): res.append(p); continue
    ours, theirs = p; n += 1
    if ours[0].startswith('design file those questions cite)'):
        SEP = " **The second release attempt of layers 1 to 3 (27 September 2026, branch `fnd/rel2`)**"
        TAIL = " Internal names are defined in `v2/docs/handover/GLOSSARY.md`."
        a = theirs[0].index(SEP); b = theirs[0].index(TAIL)
        mine_sentence = theirs[0][a:b]
        k = ours[0].index(TAIL)
        merged = ours[0][:k] + renum_line(mine_sentence, EQMAP) + ours[0][k:]; done.add(merged); res.append(merged)
    elif ours[0].startswith('| EQ-25 |'):
        assert theirs[0].startswith('| EQ-25 |'); res.append(ours[0] + '\n' + renum_line(theirs[0], EQMAP))
    else:
        raise SystemExit('unexpected EQ hunk')
assert n == 2
C = '\n'.join(res)
main_lines = set(main_eq.split('\n'))
C = '\n'.join(l if (l in main_lines or l in done) else renum_line(l, {**SCMAP, **EQMAP}) for l in C.split('\n'))
open(E, 'w', encoding='utf-8').write(C)
print('engineering questions resolved')

# ---------------------------------------------------------------- LAYER-STATUS.md
L = 'v2/docs/handover/LAYER-STATUS.md'
C = open(L, encoding='utf-8').read(); main_ls = git_show(MAIN, L)
parts = hunks(C); res = []; n = 0
for p in parts:
    if isinstance(p, str): res.append(p); continue
    ours, theirs = p; n += 1
    assert len(ours) == 1 and len(theirs) == 1 and ours[0].startswith('> **INTEGRATOR LINE, layer 4:**')
    KEY = "REQ-072's night finding (the energy architecture, S-53)."
    assert ours[0].endswith(KEY), ours[0][-120:]
    add = theirs[0][theirs[0].index(KEY) + len(KEY):]
    assert add.startswith(' **Second release attempt')
    assert not re.search(r'\b(SC-5[1-7]|EQ-25)\b', ours[0] + add); res.append(ours[0] + add)
assert n == 1
C = '\n'.join(res)
main_lines = set(main_ls.split('\n'))
C = '\n'.join(l if l in main_lines else renum_line(l, {**SCMAP, **EQMAP}) for l in C.split('\n'))
open(L, 'w', encoding='utf-8').write(C)
print('layer status resolved')

# ---------------------------------------------------------------- pages only the attempt cites SC-51 to SC-56 on
for F in ('v2/docs/HW-FW-CONTRACT.md', 'v2/docs/handover/GLOSSARY.md'):
    C = open(F, encoding='utf-8').read(); main_f = set(git_show(MAIN, F).split('\n'))
    new = '\n'.join(l if l in main_f else renum_line(l, SCMAP) for l in C.split('\n'))
    assert new != C, F; open(F, 'w', encoding='utf-8').write(new); print('renumbered', F)
