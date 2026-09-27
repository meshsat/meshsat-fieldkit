"""Re-anchor the requirements registry's file:line citations from 95e078a1 to 08f3665a (the release check of layers 1
to 3, 27 September 2026, MESHSAT-1357; layer 3 release review, finding R3). The hc3 apply script's reanchor(), run as a
preview (records/r8int4/reanchor_preview.py), moved ten citations whose text only moved (PANEL.md two lines down after
0da2778b; ASSEMBLY.md 21 lines down after c351115d) and would also have appended a second "(as read at 95e078a1)" to
five citations that already name the commit they were read at, which is wrong: those are left as they are. This script
applies the ten moves by record id with asserted old text, sets sources_read_at, and then checks EVERY file:line
citation of the registry that names no commit of its own: the cited lines at 95e078a1 against the same citation's lines
at 08f3665a, printing each one whose text differs for a hand re-read. Usage: reanchor_release.py [--write] (from the
repository root, on a tree whose cited files equal 08f3665a's)."""
import re, subprocess, sys
P = 'v2/ecad/tools/pcb_requirements.yaml'
FRM, TO = '95e078a1', '08f3665a'
WRITE = '--write' in sys.argv
t0 = open(P, encoding='utf-8').read(); t = t0


def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))


def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == 1, (rid, r.count(a), a); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]


MOVES = [('REQ-012', '"v2/docs/PANEL.md:187"', '"v2/docs/PANEL.md:189"'),
         ('REQ-013', '"v2/docs/PANEL.md:191"', '"v2/docs/PANEL.md:193"'),
         ('CON-006', '"v2/docs/ASSEMBLY.md:81"', '"v2/docs/ASSEMBLY.md:102"'),
         ('REQ-033', '"v2/docs/PANEL.md:187"', '"v2/docs/PANEL.md:189"'),
         ('REQ-033', '"v2/docs/PANEL.md:185"', '"v2/docs/PANEL.md:187"'),
         ('REQ-034', '"v2/docs/PANEL.md:184"', '"v2/docs/PANEL.md:186"'),
         ('REQ-060', '"v2/docs/PANEL.md:191"', '"v2/docs/PANEL.md:193"'),
         ('REQ-060', '"v2/docs/PANEL.md:197"', '"v2/docs/PANEL.md:199"'),
         ('REQ-066', '"v2/docs/ASSEMBLY.md:159"', '"v2/docs/ASSEMBLY.md:180"'),
         ('REQ-066', '"v2/docs/ASSEMBLY.md:173"', '"v2/docs/ASSEMBLY.md:194"')]
for rid, a, b in MOVES:          # REQ-033's two are applied 187 first, so 185 -> 187 never meets an old 187
    t = sub_in(t, rid, a, b)
old = 'sources_read_at: %s' % FRM
assert t.count(old) == 1; t = t.replace(old, 'sources_read_at: %s' % TO)

# the check: every citation in every `source` field (the fields sources_read_at governs) that names no commit of its own,
# old registry at FRM against new registry at TO, record by record and position by position
import yaml
CITE = re.compile(r"(v2/[^\s:,;()\"']+\.(?:md|py|yaml|json|txt|net|tsv)):(\d+)(?:-(\d+))?")
cache = {}


def lines(commit, path):
    k = (commit, path)
    if k not in cache:
        s = subprocess.run(['git', 'show', '%s:%s' % (commit, path)], capture_output=True, text=True)
        cache[k] = s.stdout.split('\n') if s.returncode == 0 else None
    return cache[k]


def sources(text):
    d = yaml.safe_load(text); out = {}
    for k, v in d.items():
        if isinstance(v, list):
            for r in v:
                if isinstance(r, dict) and 'id' in r and r.get('source'):
                    src = r['source']; src = src if isinstance(src, list) else [src]
                    out[(k, r['id'])] = [str(x) for x in src]
    return out


so, sn = sources(t0), sources(t)
assert so.keys() == sn.keys()
checked = differ = explicit = 0
for key in so:
    assert len(so[key]) == len(sn[key]), key
    for eo, en in zip(so[key], sn[key]):
        mo, mn = list(CITE.finditer(eo)), list(CITE.finditer(en))
        assert len(mo) == len(mn), (key, eo, en)
        for x, y in zip(mo, mn):
            if re.search(r'\bat [0-9a-f]{7,}\b', eo[x.end():]):
                explicit += 1; continue
            lo, ln = lines(FRM, x.group(1)), lines(TO, y.group(1))
            if lo is None or ln is None:
                print('MISSING  %s %s' % (key[1], x.group(0))); continue
            a, b = int(x.group(2)), int(x.group(3) or x.group(2))
            a2, b2 = int(y.group(2)), int(y.group(3) or y.group(2))
            checked += 1
            if lo[a - 1:b] != ln[a2 - 1:b2]:
                differ += 1
                print('DIFFERS  %-8s %s -> %s' % (key[1], x.group(0), y.group(0)))
print('reanchor_release: %d moves applied; %d citations compared, %d differ; %d name their own commit (left)'
      % (len(MOVES), checked, differ, explicit))
if WRITE:
    open(P, 'w', encoding='utf-8').write(t); print('reanchor_release: written')
