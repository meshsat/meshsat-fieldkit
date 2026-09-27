#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/tests/test_rails_census.py (w3de, 27 September 2026): the replay test states a
property on a fixture instead of the history of the committed intent.

t_the_nets_the_second_pass_named_do_not_close_boards_d_and_e_while_their_missed_supplies_stand declares exactly what
the second pass named on D and E and asserts the reading still names AMP_HPVSS (D) and TRK_LDO33 (E). It read the
COMMITTED intent as the base, so it held only while those two stayed undeclared: once board D declares AMP_HPVSS and
board E TRK_LDO33 (w3de, EQ-19) the reading no longer names them and the test fails for the fix it asks for ("a rule
that fails when its subject is fixed is a rule about history"). The replay now takes the missed supply's own
declaration out of its COPY of the intent first, which is the state the second pass saw, so the property is the same
one (declaring only the named nets does not close the board while the missed supply is undeclared) and it holds on any
committed intent. The third pass's replay (A and P) shares the helper and gains the same footing.

Usage: patch_test_rails_census.py <tree root holding v2/ecad>"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "tests", "test_rails_census.py")
s = open(p, encoding="utf-8").read(); o = s
old = '''        seen += 1
        p, ip, it = _copy(letter, net)
        for n in named[letter]:
            if n in nets: _declare(it, n)'''
new = '''        seen += 1
        p, ip, it = _copy(letter, net)
        # THE STATE THE EARLIER READING SAW (27 September 2026, w3de): the missed supply undeclared. The committed intent
        # may declare it by now (board D's AMP_HPVSS and board E's TRK_LDO33 are, since EQ-19), and a replay that kept
        # that declaration would test the committed file's history instead of the property.
        for _k in ("nodes", "rails"): (it.get(_k) or {}).pop(missed[letter], None)
        for n in named[letter]:
            if n in nets: _declare(it, n)'''
if s.count(old) != 1: raise SystemExit("patch_test_rails_census: the old text is not there exactly once")
s = s.replace(old, new); assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s); print("patch_test_rails_census: %s edited" % p)
