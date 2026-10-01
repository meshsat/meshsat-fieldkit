"""r11_dep.py, board A's front-end current-limit record (stream r11dep), reproduces its committed output in any clone
(MESHSAT-1357, 1 October 2026). Its historical check of revision A32 compared git's abbreviated hash (%h) with the recorded
eight characters; %h's length is the clone's choice, and a rented box's clone printed nine, so the record refused a
correct history and every L4-E4 test that reproduces it failed there. The lookup now compares the full hash by its
recorded prefix. These tests run the record in a child process with git's abbreviation forced longer and shorter than
the recorded prefix; nothing is written into the tree.
"""
import os
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "r11dep")
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402


def _run(abbrev):
    env = dict(os.environ, GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="core.abbrev", GIT_CONFIG_VALUE_0=str(abbrev),
               PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, os.path.join(REC, "r11_dep.py")], cwd=ROOT, capture_output=True, env=env)


def _need_history():
    r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", "b7e0d28f^{commit}"], capture_output=True)
    if r.returncode != 0: raise Skip("revision A32's commit is not in this clone's history")


def t_r11_dep_reproduces_its_output_whatever_the_hash_abbreviation():
    need(os.path.join(REC, "r11_dep.py"), "r11_dep.py is not in this tree")
    _need_history()
    want = open(os.path.join(REC, "r11_dep.out"), "rb").read()
    for abbrev in (7, 9, 12, 40):
        r = _run(abbrev)
        assert r.returncode == 0, "core.abbrev=%d: refused: %s" % (abbrev, r.stderr.decode()[-200:])
        assert r.stdout == want, "core.abbrev=%d: the output differs from r11_dep.out" % abbrev


def t_r11_dep_compares_the_full_hash_by_prefix():
    """The lookup asks git for the full hash (%H), never the abbreviation, and compares it by the recorded prefix."""
    need(os.path.join(REC, "r11_dep.py"), "r11_dep.py is not in this tree")
    import ast
    src = open(os.path.join(REC, "r11_dep.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    fmts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.startswith("--format=")]
    assert fmts and all("%h" not in f for f in fmts), "a git format asks for the abbreviated hash: %s" % fmts
    assert any(isinstance(n, ast.Attribute) and n.attr == "startswith" for n in ast.walk(tree)), "no prefix comparison"
