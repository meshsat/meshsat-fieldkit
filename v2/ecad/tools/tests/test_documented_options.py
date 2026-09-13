#!/usr/bin/env python3
"""An option a tool's own usage line offers must be read by that tool (MESHSAT-862, 13 September 2026).

`dc_drop.py` has offered `--png out.png` in its usage line since it was written on 8 September, and until
today no line of it ever looked for `--png`: a run that asked for the picture got a silent nothing, exit 0,
and no file. It is the same family as the four dead paths of 32.153 to 32.156 and as owner ruling 10's fill
rule that could never fire: a promise in the tree that nothing keeps, which is worse than an absent feature
because a reader believes it.

The rule reads each tool's usage line, takes every `--name` it offers, and requires the source to look for
that string. A tool that deliberately documents an option it forwards to another program declares it here.
"""
import os, re, glob, io, ast, tokenize

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# an option a tool documents but does not itself parse, with the reason it is here
FORWARDED = {
    # ("tool.py", "--option"): "why it is not read in this file"
}


def _docstring(src):
    m = re.match(r'\s*(?:#![^\n]*\n)?\s*(?:"""|\'\'\')(.*?)(?:"""|\'\'\')', src, re.S)
    return (m.group(1), src[m.end():]) if m else ("", src)


def _usage(doc):
    """The usage BLOCK only: from a Usage: line to the first blank line after it. An option named in prose
    (kicad-cli's own `--format json`, the `python3 -m venv --system-site-packages` recipe) is a sentence
    about another program; an option on a usage line is this tool's promise to its caller."""
    out = []
    lines = doc.splitlines()
    for i, ln in enumerate(lines):
        if not re.match(r"\s*Usage:", ln, re.I): continue
        out.append(ln)
        for nxt in lines[i + 1:]:
            if not nxt.strip(): break
            out.append(nxt)
    return "\n".join(out)


def _literals(body):
    """The short string literals the CODE holds, which is what an option parser looks for. A mention inside
    a docstring or a comment is not a reader: `_draw`'s own docstring says the words `--png` and the first
    version of this rule passed on that alone. Tokenising and keeping the exact short literals is the
    difference between a tool that reads an option and a tool that talks about one."""
    out = set()
    try:
        for tok in tokenize.generate_tokens(io.StringIO(body).readline):
            if tok.type != tokenize.STRING: continue
            try: val = ast.literal_eval(tok.string)
            except Exception: continue
            if isinstance(val, str) and len(val) <= 40 and "\n" not in val: out.add(val.strip())
    except (tokenize.TokenError, IndentationError, SyntaxError):
        out.update(re.findall(r'["\'](--[a-z][a-z0-9-]{1,20})["\']', body))
    return out


def _tools():
    for p in sorted(glob.glob(os.path.join(TOOLS, "*.py"))):
        src = open(p, encoding="utf-8").read()
        doc, body = _docstring(src)
        use = _usage(doc)
        if not use: continue
        yield os.path.basename(p), _literals(body), use


def t_every_option_a_usage_line_offers_is_read_by_the_tool():
    dead = []
    for name, lits, use in _tools():                   # lits are the code's own string literals, not its prose
        for opt in sorted(set(re.findall(r"(?<![\w-])(--[a-z][a-z0-9-]{1,20})", use))):
            if (name, opt) in FORWARDED: continue
            if opt in lits or (opt + "=") in lits: continue   # a tool may parse `--opt=value` instead of `--opt value`
            dead.append("%s offers %s and never reads it" % (name, opt))
    assert not dead, "; ".join(dead)


def t_the_rule_can_tell_the_docstring_from_the_code():
    # a tool whose ONLY mention of the option is the usage line must fail: that is the defect being caught
    src = '#!/usr/bin/env python3\n"""t.py <board>\n\nUsage: t.py <board> [--zzz out.png]"""\nimport sys\nprint(sys.argv)\n'
    doc, body = _docstring(src)
    assert "--zzz" in _usage(doc), "the rule does not read the usage block"
    assert "--zzz" not in _literals(body), "the rule would read the docstring as code and pass everything"


def t_an_option_parsed_in_the_equals_form_counts_as_read():
    assert "--via=" in _literals('x = next(a.split("=", 1)[1] for a in sys.argv if a.startswith("--via="))\n')


def t_talking_about_an_option_in_a_comment_is_not_reading_it():
    body = 'def f(a):\n    """this is what --qqq has always meant"""\n    # --qqq is the option\n    return 1\n'
    assert "--qqq" not in _literals(body), "a docstring or comment mention counts as a reader"
    assert "--qqq" in _literals('x = a.index("--qqq")\n'), "a real option read is not recognised"


def t_prose_about_another_program_is_not_this_tool_s_promise():
    doc, _ = _docstring('"""t.py\n\nReads what `kicad-cli sch erc --format json` wrote.\n\nUsage: t.py <dir> <name>"""\nx = 1\n')
    assert "--format" not in _usage(doc), "a sentence about another program is being read as an option"


def t_dc_drop_reads_its_own_png_option():
    src = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    assert 'a.index("--png")' in src, "dc_drop no longer reads --png"
    assert "def _draw(" in src, "dc_drop has no drawing for the picture it offers"
