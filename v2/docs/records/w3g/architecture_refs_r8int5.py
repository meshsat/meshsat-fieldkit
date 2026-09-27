"""r8int5, stream w3g: its eight ARCHITECTURE.md diagram reference lines, applied line by line (the page moved under
them at r8int4 and at set 5's w3de commit, so the stream's diff is re-applied by content, each old line found once),
naming the tree the rebuild at this integration ran at (argv[1], the short sha) instead of 38dcd764, and set 5 beside
round 8. Run from the worktree root."""
import os, re, sys
K = os.path.dirname(os.path.abspath(__file__))
TREE = sys.argv[1]
P = 'v2/docs/ARCHITECTURE.md'
d = open(os.path.join(K, 'architecture-w3g.diff')).read().split('\n')
olds = [l[1:] for l in d if l.startswith('-') and not l.startswith('---')]
news = [l[1:] for l in d if l.startswith('+') and not l.startswith('+++')]
assert len(olds) == len(news) == 8, (len(olds), len(news))
SUB = [("drawn at `38dcd764` with round 8,", "drawn at `%s` with round 8 and set 5," % TREE),
       ("as committed at `38dcd764`, with round 8 on all six boards", "as committed at `%s`, with round 8 on all six boards and set 5 on A, B, D and E" % TREE),
       ("as committed at `38dcd764`, with round 8 on every board", "as committed at `%s`, with round 8 on every board and set 5 on A, B, D and E" % TREE),
       ("drawn at `38dcd764`: round 8 changed none", "drawn at `%s`: round 8 and set 5 changed none" % TREE),
       ("(the build's own substitution sweep at `38dcd764`:", "(the build's own substitution sweep at `%s`:" % TREE)]
t = open(P).read()
for o, n in zip(olds, news):
    for a, b in SUB: n = n.replace(a, b)
    assert '38dcd764' not in n, n[:120]
    if n in t: continue
    assert t.count(o) == 1, o[:100]
    t = t.replace(o, n)
open(P, 'w').write(t)
print('architecture_refs_r8int5: 8 lines at', TREE)
