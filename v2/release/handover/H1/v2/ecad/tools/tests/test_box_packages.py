#!/usr/bin/env python3
"""A box built by `routeflow/cloud/onstart.sh` can run `build_sch.sh` to the end (MESHSAT-1357, 26 September 2026).

THE DEFECT, measured on box 52646493 on 25 September 2026 (finding W7-R2-03). `build_sch.sh` exited 3 on boards A
to E: `sch_pages.py:25` runs `pdftoppm`, which comes from poppler-utils, and `onstart.sh` installs mupdf-tools and
not poppler-utils, so the schematic was never paged and the BOM export on the line after it never ran. Board P
passed only because its sheet is one page and `sch_pages.py` copies a one-page sheet without calling either tool.
The same file imports PIL three lines later, and nothing installed that either.

So the rule is stated on the programs and modules the build actually calls, read by PARSING the tools rather than
by a list someone keeps: every command word of `build_sch.sh`, every Python tool it runs, every program those tools
start through `subprocess` and every third-party module they import must come from a package `onstart.sh` installs.
A name this file does not know is a failure that asks for its package, never a pass.
"""
import ast, os, shlex, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONSTART = os.path.join(TOOLS, "routeflow", "cloud", "onstart.sh")

# Which Ubuntu 24.04 package provides each program. None means the ubuntu:24.04 base image carries it (coreutils,
# bash builtins). Declared with the reason, because the mapping is a fact about Ubuntu and not about this tree.
PROGRAM_PACKAGE = {
    "kicad-cli": "kicad",          # the KiCad 9 PPA package, onstart.sh's second apt line
    "python3": "python3",
    "mutool": "mupdf-tools",       # sch_pages.py cuts the sheet into A3 tiles with `mutool poster` and merges with `mutool merge`
    "pdftoppm": "poppler-utils",   # sch_pages.py renders the tiles at 6 dpi to find the ones that carry ink
    "cp": None, "rm": None, "mkdir": None, "cd": None, "set": None, "echo": None, "exit": None,
    "true": None, "if": None, "then": None, "fi": None, "else": None, "!": None,
}
# Which package provides each third-party Python module (stdlib and this tree's own modules need none).
MODULE_PACKAGE = {
    "PIL": "python3-pil",          # sch_pages.py reads each tile's ink fraction with Pillow
    "numpy": "python3-numpy", "scipy": "python3-scipy", "yaml": "python3-yaml",
    "pcbnew": "kicad",             # KiCad's own Python module
}
SEPARATORS = {";", "&&", "||", "|", "(", ")", "{", "}", "then", "else", "do", "if", "!", "elif"}


def _commands(shell_src):
    """(command word, whole command tokens) for every simple command in a shell source, comments dropped."""
    for line in shell_src.splitlines():
        s = line.strip()
        if not s or s.startswith("#"): continue
        lx = shlex.shlex(s, posix=True, punctuation_chars=True); lx.whitespace_split = True; lx.commenters = "#"
        try: toks = list(lx)
        except ValueError: continue
        cmd, start = [], True
        for t in toks + [";"]:
            if t in SEPARATORS or set(t) <= set(";&|()"):
                if cmd: yield cmd[0], cmd
                cmd = []
                if t in ("if", "then", "else", "do", "elif", "!"): start = True
                continue
            if start and "=" in t and not t.startswith("-") and t.split("=")[0].isidentifier():
                continue                                    # a variable assignment, not a command
            cmd.append(t); start = False


def _python_tools(shell_src):
    """The tools/*.py files a shell script runs, by name."""
    out = []
    for word, cmd in _commands(shell_src):
        if word in ("python3", "python"):
            for t in cmd[1:]:
                if t.endswith(".py"):
                    out.append(os.path.basename(t)); break
    return out


def _needs_of_python(path):
    """(programs started through subprocess, third-party modules imported) by one Python tool, from its AST."""
    tree = ast.parse(open(path, encoding="utf-8").read())
    progs, mods = set(), set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name in ("run", "call", "check_call", "check_output", "Popen") and n.args:
                a = n.args[0]
                if isinstance(a, (ast.List, ast.Tuple)) and a.elts and isinstance(a.elts[0], ast.Constant) \
                        and isinstance(a.elts[0].value, str):
                    progs.add(a.elts[0].value)
        elif isinstance(n, ast.Import):
            mods |= {x.name.split(".")[0] for x in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            mods.add(n.module.split(".")[0])
    local = {m for m in mods if os.path.exists(os.path.join(TOOLS, m + ".py")) or os.path.isdir(os.path.join(TOOLS, m))}
    third = {m for m in mods if m not in sys.stdlib_module_names and m not in local}
    return progs, third


def _installed(onstart_src):
    """Every package any `apt-get install` in the setup script names."""
    pk = set()
    for word, cmd in _commands(onstart_src):
        if word == "apt-get" and "install" in cmd:
            for t in cmd[cmd.index("install") + 1:]:
                if t.startswith((">", "<")) or t.isdigit(): break     # a redirection ends the package list
                if t.startswith("-"): continue
                pk.add(t)
    return pk


def required_packages(shell_path):
    """{package: [why]} that a shell tool needs on a box, or raises naming what nobody has declared."""
    src = open(shell_path, encoding="utf-8").read()
    need, unknown = {}, []

    def want(kind, name, why):
        table = PROGRAM_PACKAGE if kind == "program" else MODULE_PACKAGE
        if name not in table: unknown.append("%s %s (%s)" % (kind, name, why)); return
        if table[name]: need.setdefault(table[name], []).append("%s %s (%s)" % (kind, name, why))

    for word, _cmd in _commands(src):
        if "$" in word or word.startswith("/"): continue    # a path or a variable, resolved at run time
        want("program", word, os.path.basename(shell_path))
    for tool in _python_tools(src):
        p = os.path.join(TOOLS, tool)
        progs, mods = _needs_of_python(p)
        for g in sorted(progs): want("program", g, tool)
        for m in sorted(mods): want("module", m, tool)
    if unknown:
        raise AssertionError("no package is declared for: %s. Add the Ubuntu package that provides each to this "
                             "file, with the reason, and install it in onstart.sh" % "; ".join(unknown))
    return need


def t_the_parser_reads_the_programs_a_tool_starts_and_the_modules_it_imports():
    progs, mods = _needs_of_python(os.path.join(TOOLS, "sch_pages.py"))
    assert {"mutool", "pdftoppm"} <= progs, progs
    assert "PIL" in mods, mods


def t_the_parser_reads_the_packages_of_every_apt_line():
    got = _installed("apt-get update && apt-get install -y --no-install-recommends a b || { echo x; exit 1; }\n"
                     "apt-get install -y c >/dev/null 2>&1 || exit 1\n")
    assert got == {"a", "b", "c"}, got


def t_a_box_built_by_onstart_can_run_the_whole_schematic_build():
    """DEFECTIVE before 26 September 2026: poppler-utils (pdftoppm, sch_pages.py:25) and python3-pil (PIL,
    sch_pages.py:28) were needed and not installed. ACCEPTABLE after: every package the build needs is installed."""
    need = required_packages(os.path.join(TOOLS, "build_sch.sh"))
    have = _installed(open(ONSTART, encoding="utf-8").read())
    missing = {p: w for p, w in sorted(need.items()) if p not in have}
    assert not missing, "onstart.sh does not install what build_sch.sh needs: %s" % \
        "; ".join("%s for %s" % (p, ", ".join(w)) for p, w in missing.items())
