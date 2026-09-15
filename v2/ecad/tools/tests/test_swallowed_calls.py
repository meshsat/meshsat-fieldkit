#!/usr/bin/env python3
"""A comment appended to a generator line must not carry the rest of that line (MESHSAT-862, 15 September 2026).

The 14 September certification pass (3457117) put a stock note after `J_FAN%d`'s `part(...)` call in `gen_sch_b.py`
and the note landed BEFORE the `; r(R(51), "10k", "FAN_PWM%d" % s, cm33)` that shared the line: the three fan PWM
pull-ups R151, R251 and R351 left the netlist without a word, and the schematic regeneration of 15 September was
the first thing to notice, as six net and node lines against the netlist committed the day before. The record has
this trap twice already (5 Sep, C18 and C19 on `ina219("U14", ...)`; 5 Sep 15:00, A21's boost jog tuple), each time
found by a chain dying. This one killed nothing: the generator ran, the board was placed, the gate passed, on a
design with three resistors fewer. A comment token that contains `; name(` is refused."""
import glob, io, os, re, tokenize

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def swallowed():
    hits = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_*.py"))):
        for tok in tokenize.generate_tokens(io.StringIO(open(f).read()).readline):
            if tok.type == tokenize.COMMENT and re.search(r";\s*[A-Za-z_][A-Za-z_0-9.]*\(", tok.string):
                hits.append("%s:%d %s" % (os.path.basename(f), tok.start[0], tok.string[:100]))
    return hits


def t_no_generator_comment_carries_a_call_after_a_semicolon():
    h = swallowed()
    assert not h, "a comment swallowed the call(s) that shared its line:\n" + "\n".join(h)


def t_the_rule_reads_the_comment_token_not_the_line():
    # a call BEFORE the comment on the same line is the normal shape and must pass
    src = 'r("R1", "10k", "A", "B"); r("R2", "10k", "C", "D")   # two parts, one line\n'
    toks = [t for t in tokenize.generate_tokens(io.StringIO(src).readline) if t.type == tokenize.COMMENT]
    assert toks and not re.search(r";\s*[A-Za-z_][A-Za-z_0-9.]*\(", toks[0].string)
