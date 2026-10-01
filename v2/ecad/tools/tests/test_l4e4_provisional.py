"""L4-E4's component values stay provisional until the source-control and fault-handling decisions release them (MESHSAT-1357,
1 October 2026, the owner's instruction: "Keep L4-E4 component changes explicitly provisional until the relevant
source-control and fault-handling decisions support them"). The two draft apply scripts refuse to write this repository's
board A generator until v2/docs/records/l4e4/RELEASE.md reads "released: yes" and names an accepted check of each decision;
a copy elsewhere may be written. The tests run the scripts in a scratch mirror of the repository's layout, so the tree's
generator is never a target; nothing here writes into the tree.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4e4")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
SCRIPTS = ("apply_gen_sch_a_r11.py", "apply_gen_sch_a_r138.py")
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _mirror(name):
    d = tempfile.mkdtemp(prefix="l4e4-prov-")
    os.makedirs(os.path.join(d, "v2", "docs", "records", "l4e4")); os.makedirs(os.path.join(d, "v2", "ecad", "tools"))
    for k in ("l4e5", "l4e6"): os.makedirs(os.path.join(d, "v2", "docs", "records", k, "checks"))
    shutil.copyfile(os.path.join(REC, name), os.path.join(d, "v2", "docs", "records", "l4e4", name))
    shutil.copyfile(GEN_A, os.path.join(d, "v2", "ecad", "tools", "gen_sch_a.py"))
    return d


def _run(d, name, target, *flags):
    return subprocess.run([sys.executable, "-B", os.path.join(d, "v2", "docs", "records", "l4e4", name), target] + list(flags),
                          capture_output=True, text=True, cwd=d)


def t_the_tree_holds_no_release_while_the_decisions_are_open():
    """While no RELEASE.md is filed, the page says PROVISIONAL; once one is, each check it names is accepted."""
    page = open(os.path.join(REC, "L4E4-CURRENT-LIMITS.md"), encoding="utf-8").read()
    rel = os.path.join(REC, "RELEASE.md")
    if not os.path.isfile(rel):
        assert "PROVISIONAL" in page.split("\n## ", 1)[0], "the page does not state that its values are provisional"
    else:
        lines = open(rel, encoding="utf-8").read().split("\n")
        assert lines[0] == "released: yes"
        for key in ("source-control", "fault-handling"):
            path = [l.split(":", 1)[1].strip() for l in lines if l.startswith(key + ":")][0]
            assert open(os.path.join(ROOT, path), encoding="utf-8").readline().rstrip("\n") == "accepted: yes"


def t_writing_the_repository_generator_is_refused_until_both_decisions_release_the_values():
    need(GEN_A, "board A's generator")
    before = _sha(GEN_A)
    for name in SCRIPTS:
        need(os.path.join(REC, name), "the draft apply script")
        d = _mirror(name)
        try:
            gen = os.path.join(d, "v2", "ecad", "tools", "gen_sch_a.py"); rel = os.path.join(d, "v2", "docs", "records", "l4e4", "RELEASE.md")
            orig = _sha(gen)
            r = _run(d, name, gen, "--write")
            assert r.returncode == 3 and "PROVISIONAL" in r.stderr and _sha(gen) == orig, (name, "no release", r.stderr)
            assert _run(d, name, gen, "--check").returncode == 0 and _sha(gen) == orig, (name, "--check must still work")
            c5 = os.path.join(d, "v2", "docs", "records", "l4e5", "checks", "c.md"); c6 = os.path.join(d, "v2", "docs", "records", "l4e6", "checks", "c.md")
            open(c5, "w").write("accepted: yes\n"); open(c6, "w").write("accepted: no\n")
            open(rel, "w").write("released: yes\nsource-control: v2/docs/records/l4e5/checks/c.md\nfault-handling: v2/docs/records/l4e6/checks/c.md\n")
            r = _run(d, name, gen, "--write")
            assert r.returncode == 3 and "fault-handling" in r.stderr and _sha(gen) == orig, (name, "a check not accepted", r.stderr)
            open(rel, "w").write("released: no\nsource-control: v2/docs/records/l4e5/checks/c.md\nfault-handling: v2/docs/records/l4e6/checks/c.md\n")
            open(c6, "w").write("accepted: yes\n")
            r = _run(d, name, gen, "--write")
            assert r.returncode == 3 and "released: yes" in r.stderr and _sha(gen) == orig, (name, "not released", r.stderr)
            open(rel, "w").write("released: yes\nsource-control: v2/docs/records/l4e5/checks/c.md\nfault-handling: v2/docs/records/l4e6/checks/c.md\n")
            r = _run(d, name, gen, "--write")
            assert r.returncode == 0 and _sha(gen) != orig, (name, "released", r.stderr)
            other = os.path.join(d, "elsewhere.py"); shutil.copyfile(GEN_A, other); os.remove(rel)
            r = _run(d, name, other, "--write")
            assert r.returncode == 0 and _sha(other) != _sha(GEN_A), (name, "a copy elsewhere", r.stderr)
        finally:
            shutil.rmtree(d, ignore_errors=True)
    assert _sha(GEN_A) == before, "the test changed the tree's generator"
