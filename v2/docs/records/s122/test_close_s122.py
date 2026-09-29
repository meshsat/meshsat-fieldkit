#!/usr/bin/env python3
"""Stream s122, rounds 6 and 7 (S-122, MESHSAT-1357, 29 September 2026): the closing gate's fixture and mutation tests,
the answer to check-s122-5 B1, m1 and m2 (`checks/check-s122-5.md`) and to check-s122-6 m1 and m2 (`checks/check-s122-6.md`).

  T1 at this commit, with every test of verdicts.py on: close_s122.gate_fixtures refuses nothing (every mutant of
     close_s122.MUTANTS reads STALE, line 47 with the 1 W planted back is refused by (b) and by (f)'s scan alone), the
     closing list reads the eight lines, and close_s122.figure_scan covers every figure-and-unit token on them;
  T2 the mutation tests: each test of verdicts.ROLE_TESTS (forward, reverse1, reverse2, rails, history, wordmatch,
     load) turned off in turn; the mutants that then read TRUE are listed, at least one does for each test, and
     gate_fixtures REFUSES (check-s122-5 m2: with the forward test off the gate refuses);
  T3 verdicts.check_figs turned off (the judgement's own figure check): line 47 with the 1 W planted back is still
     refused by (b) and by the scan, which do not rest on it;
  T4 the scan on a copy of each closing-list sentence with one of its figures changed (the number plus one, a spelled
     count the next word) and the judgement's keys that span it rewritten to the new text, its assertions kept: every
     change is refused by the comparison of values (round 7, check-s122-6 m1), and so are the check's four plants and
     the 1 W with their keys rewritten (close_s122.KEYED);
  T5 the mutation of that comparison: verdicts._fig_match replaced by one that accepts everything; T4 must then fail
     and gate_fixtures refuse.
Reads the committed documents and netlists; writes nothing. Exit 0 when all hold, 1 otherwise.
Run: python3 test_close_s122.py"""
import contextlib, io, os, re, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402
import close_s122 as C  # noqa: E402

FAILS = []


def refused(fn, *a):
    """(True, the refusal) when fn refuses (close_s122.refuse exits 2), else (False, '')."""
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn(*a)
    except SystemExit as e:
        return e.code == 2, buf.getvalue().strip()
    return False, ""


def check(ok, what):
    print("%s %s" % ("PASS" if ok else "FAIL", what))
    if not ok: FAILS.append(what)


def t4(lines, nls):
    """T4: each figure token of the closing list's sentences changed by one (its first number plus one, a spelled count
    the next word), the judgement's figures_ok and counts_ok keys that span it rewritten to the new text and its
    assertions kept, so only the comparison of values can refuse it. Returns (tokens, the changes the scan passed)."""
    n, through = 0, []
    for x in lines:
        doc, line = x.split(" line ")
        for s in C.line_sentences(doc, int(line)):
            j = V.J.J.get(L.sid_digest(s))
            for a, b, txt, _vals in V.figure_tokens(s):
                m = re.search(r"\d+", txt)
                if m:
                    changed = txt[:m.start()] + str(int(m.group(0)) + 1) + txt[m.end():]
                else:
                    w = V.NUMWORD[txt.lower()]
                    changed = [k for k, i in V.NUMWORD.items() if i == (w + 1 if w < 20 else 19)][0]
                sp = s[:a] + changed + s[b:]
                j2 = dict(j)
                for f in ("figures_ok", "counts_ok"):
                    if not isinstance(j.get(f), dict): continue
                    keys = {}
                    for k, v in j[f].items():
                        nk = k
                        for km in re.finditer(re.escape(k), s):
                            if km.start() <= a and b <= km.end():
                                nk = s[km.start():a] + changed + s[b:km.end()]
                        keys[nk] = v
                    j2[f] = keys
                d = L.sid_digest(sp)
                had = V.J.J.get(d)
                V.J.J[d] = j2
                try:
                    bad = C.figure_uncovered(sp, {d: "TRUE"}, nls)
                    un = V.figures_uncovered(sp, j2)
                finally:
                    if had is None: del V.J.J[d]
                    else: V.J.J[d] = had
                n += 1
                if not bad or changed not in un: through.append("%s: %r to %r" % (x, txt, changed))
    return n, through


def main():
    nls = L.netlists()
    nets = L.all_nets(nls)
    rows = V.judge(L.inventory(nls), nls)
    lines = sorted(set(C.closing_list(rows)))
    check(len(lines) == 8, "T1 the closing list reads %d lines: %s" % (len(lines), ", ".join(lines)))
    r, msg = refused(C.gate_fixtures, nls, nets)
    check(not r, "T1 gate_fixtures refuses nothing with every test on%s" % ((": " + msg) if msg else ""))
    r, msg = refused(C.figure_scan, lines, nls, rows)
    check(not r, "T1 figure_scan covers every figure-and-unit token on the closing list%s" % ((": " + msg) if msg else ""))
    now = {}
    for key, title, kind, line, text, rk in L.md_blocks("v2/docs/V2-SPEC.md"):
        if kind == "cell:1" and title.startswith("Boards of this generation"):
            for s in L.sentences(text): now[rk] = (key, kind, line, s)
    for test in list(V.ROLE_TESTS):
        V.ROLE_TESTS[test] = False
        try:
            through = []
            for rk, old, new, label in C.MUTANTS:
                key, kind, line, s = now[rk]
                if C._judge_as(s.replace(old, new), V.J.J[L.sid_digest(s)], rk, key, kind, line, nls, nets)[2] == "TRUE":
                    through.append(label)
            r, msg = refused(C.gate_fixtures, nls, nets)
        finally:
            V.ROLE_TESTS[test] = True
        check(bool(through) and r, "T2 with the %s test off, %d mutant(s) read TRUE (%s) and the gate refuses: %s" % (
            test, len(through), "; ".join(through) or "none", msg or "it does NOT refuse"))
    keep = V.check_figs
    V.check_figs = lambda s, j: ([], [])
    try:
        r, msg = refused(C.gate_fixtures, nls, nets)
    finally:
        V.check_figs = keep
    check(not r, "T3 with verdicts.check_figs off, the planted 1 W is still refused by (b) and the scan (the fixtures pass)%s"
          % ((": " + msg) if msg else ""))
    n, through = t4(lines, nls)
    check(n > 0 and not through, "T4 %d figure tokens on the closing list, each changed by one with its keys rewritten and "
          "its assertions kept: every change refused by the scan's comparison%s" % (n, (": NOT " + "; ".join(through[:4])) if through else ""))
    kr = C.keyed_refused(nls)
    check(all(bad for _new, bad in kr), "T4 the check's plants with their keys rewritten (%s) refused by the scan"
          % ", ".join(new for new, _bad in kr))
    keep = V._fig_match
    V._fig_match = lambda tv, x: True
    try:
        n5, through5 = t4(lines, nls)
        r5, msg5 = refused(C.gate_fixtures, nls, nets)
    finally:
        V._fig_match = keep
    check(bool(through5) and r5, "T5 with the scan's comparison removed (verdicts._fig_match accepting everything), T4 "
          "fails (%d of %d changes pass) and the gate refuses: %s" % (len(through5), n5, msg5 or "it does NOT refuse"))
    print("test_close_s122: %s" % ("ALL PASS" if not FAILS else "%d FAIL" % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
