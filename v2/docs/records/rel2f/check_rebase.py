"""Check of resolve_rebase.py's result (27 September 2026, MESHSAT-1357, the release finalizer): for every file the
second release attempt (d535c17e) changed, every line of the resolved file is main's (391d8579), or a line d535c17e
wrote (renumbered SC-51..56 to SC-58..63 and EQ-25 to EQ-26), and every line of main's that is gone is one d535c17e
changed; the two hand-merged lines (ENGINEERING-QUESTIONS.md's header sentence and LAYER-STATUS.md's layer 4 line) are
the only ones it reports. Run from the worktree root during the rebase stop."""
import re, subprocess, sys
SCMAP = {'SC-%d' % n: 'SC-%d' % (n + 7) for n in range(51, 57)}; EQMAP = {'EQ-25': 'EQ-26'}
def renum(l):
    for a, b in {**SCMAP, **EQMAP}.items(): l = re.sub(r'\b%s\b' % re.escape(a), b, l)
    return l
def show(rev, p):
    r = subprocess.run(['git', 'show', '%s:%s' % (rev, p)], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ''
files = subprocess.run(['git', 'diff', '--name-only', '953f5658', 'd535c17e'], capture_output=True, text=True).stdout.split()
bad = 0
for p in files:
    base = set(show('953f5658', p).split('\n')); main = set(show('391d8579', p).split('\n'))
    mine = set(show('d535c17e', p).split('\n')); cur = set(open(p, encoding='utf-8').read().split('\n'))
    mine_added = {renum(l) for l in mine - base} | (mine - base)
    added = cur - main
    unexpl_add = [l for l in added if l not in mine_added]
    removed = main - cur
    unexpl_rem = [l for l in removed if not (l in base and l not in mine)]
    # mine's additions that did not make it
    lost = [l for l in (mine - base) if l not in cur and renum(l) not in cur]
    if unexpl_add or unexpl_rem or lost:
        print('==', p, 'unexplained added', len(unexpl_add), 'unexplained removed', len(unexpl_rem), 'lost', len(lost))
        for l in unexpl_add[:4]: print('  +', l[:220])
        for l in unexpl_rem[:4]: print('  -', l[:220])
        for l in lost[:4]: print('  L', l[:220])
        bad += 1
print('files', len(files), 'with unexplained lines', bad)
