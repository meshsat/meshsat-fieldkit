#!/usr/bin/env python3
"""A comment appended to a code line that ate the code after it (MESHSAT-862, 13 September 2026).

Section 8 of the handover has warned about this since 5 September, when `# ...` after `ina219("U14", ...)`
swallowed the two `c()` calls sharing that line and the generator died at layout while the chain quietly
rebuilt from the previous schematic. It has happened five more times since, three of them on 13 September in
one sitting, and the reason it keeps happening is that it is INVISIBLE to the gate the chains use: when the
eaten code sat after a semicolon the line still parses, so `python3 -W error -c compile(...)` and even
`ast.parse` are both happy. Only running the generator finds it, and only if something downstream notices.

It left a live defect in three generators. `gen_pcb_{c,d,e}3.py` each read

    nu = pcbnew.NETCLASS("USB"); cls(nu, ...); nu.SetDiffPairGap(FromMM(0.2))   # ... ; ns.SetNetclass("USB", nu)

so the USB net class was built and configured on C, D and E and never registered with the board's net
settings. The project JSON writes the class too, which is why nothing had failed, but the board's own copy
carried three classes where the design names four.

The rule: a comment that FOLLOWS CODE on its own line may not contain a call with a quoted argument. Prose
does not write `foo("`. A comment on a line of its own may quote code freely, which is how the eight other
comments in this tree that mention `idc("2x10")` or `cl.get("via_diameter")` stay legal, and it is also the
fix: when a trailing comment needs to name code, it goes on its own line above.
"""
import glob, os, re, tokenize

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALL = re.compile(r"[A-Za-z_][A-Za-z_0-9]*\(\s*[\"']")


def trailing_comments_with_calls(path):
    src = open(path).read().splitlines()
    out = []
    with open(path, "rb") as fh:
        try: toks = list(tokenize.tokenize(fh.readline))
        except Exception: return out
    for tok in toks:
        if tok.type != tokenize.COMMENT: continue
        m = CALL.search(tok.string)
        if not m: continue
        before = src[tok.start[0] - 1][:tok.start[1]].strip()
        if not before: continue          # its own line: prose may quote code
        out.append("%s:%d a trailing comment carries %r" % (os.path.basename(path), tok.start[0], m.group(0)))
    return out


def t_no_trailing_comment_carries_a_call():
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "*.py")) + glob.glob(os.path.join(TOOLS, "tests", "*.py"))):
        bad += trailing_comments_with_calls(f)
    assert not bad, ("a comment appended to a code line looks like it ate the code after it:\n  " + "\n  ".join(bad))


def t_the_usb_class_is_registered_wherever_it_is_built():
    """The defect this rule was written for, asserted directly: a class that is built is registered."""
    import ast
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_pcb_*.py"))):
        src = open(f).read()
        tree = ast.parse(src)
        built, registered = set(), set()
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call): continue
            name = getattr(n.func, "attr", None) or getattr(n.func, "id", None)
            if name == "NETCLASS" and n.args and isinstance(n.args[0], ast.Constant): built.add(n.args[0].value)
            if name == "SetNetclass" and n.args and isinstance(n.args[0], ast.Constant): registered.add(n.args[0].value)
        for c in sorted(built - registered):
            bad.append("%s builds net class %r and never registers it" % (os.path.basename(f), c))
    assert not bad, "\n  ".join(bad)


def t_the_rule_catches_its_own_fixture():
    import tempfile
    src = 'x = 1; foo(2)   # a note; bar("EATEN", y)\n'
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(src); p = fh.name
    try:
        assert trailing_comments_with_calls(p), "the rule missed a comment that ate a call"
    finally:
        os.unlink(p)
    src2 = '# prose that quotes idc("2x10") on its own line\nx = 1\n'
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as fh:
        fh.write(src2); p2 = fh.name
    try:
        assert not trailing_comments_with_calls(p2), "an own-line comment quoting code was flagged"
    finally:
        os.unlink(p2)
