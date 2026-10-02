"""Layer 4 records L4-E9 and L4-E11 (MESHSAT-1357, 2 October 2026): the safe-operating-area readers are independent of how
poppler serialises the SVG.

Both records read the CSD19532Q5B's Figure 10 (SLPS414B p.6) and L4-E11 also the CSD19536KTT's from the sheet's own vector
drawing, through `pdftocairo -svg`. Poppler 22 writes each stroke as a style property with no space after a comma
("stroke:rgb(0%,0%,0%)", "matrix(a,b,...)"); poppler 24 writes stroke attributes with a space after each comma
("stroke=\"rgb(0%, 0%, 0%)\"", "matrix(a, b, ...)"); the path coordinates are the same. The predicate: each reader returns
the same lines from the real drawing, from its poppler 22 form and from its poppler 24 form, both made here from the real
one by that rewrite, so the test means the same on either host. A software predicate on the readers; it establishes no
electrical property.
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True


def _load(rel, name):
    path = os.path.join(REC, rel)
    if not os.path.isfile(path):
        raise Skip("%s is not in this tree" % rel)
    if shutil.which("pdftocairo") is None or shutil.which("pdftotext") is None:
        raise Skip("pdftocairo and pdftotext are needed")
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def _as_poppler22(svg):
    def el(mo):
        t = re.sub(r",\s+", ",", mo.group(0))
        a = re.search(r' stroke="([^"]*)"', t)
        if a and ' style="' not in t:
            t = t.replace(a.group(0), ' style="stroke:%s;"' % a.group(1))
        return t
    return re.sub(r"<path[^>]*>", el, svg)


def _as_poppler24(svg):
    def el(mo):
        t = mo.group(0)
        st = re.search(r' style="([^"]*)"', t)
        if st:
            kv = [p.split(":", 1) for p in st.group(1).split(";") if ":" in p]
            t = t.replace(st.group(0), "".join(' %s="%s"' % (k.strip(), v.strip()) for k, v in kv))
        return re.sub(r",(?=\S)", ", ", t)
    return re.sub(r"<path[^>]*>", el, svg)


def _read_with(m, fn, rewrite):
    real = subprocess.run

    def fake(cmd, *a, **k):
        r = real(cmd, *a, **k)
        if cmd and cmd[0] == "pdftocairo" and "-svg" in cmd:
            r = subprocess.CompletedProcess(r.args, r.returncode, rewrite(r.stdout.decode("utf-8", "replace")).encode("utf-8"), r.stderr)
        return r
    m.subprocess.run = fake
    try:
        return getattr(m, fn)()
    except SystemExit as e:
        raise AssertionError("%s refused (exit %s) on the rewritten drawing" % (fn, e.code))
    finally:
        m.subprocess.run = real


def _check(rel, name, readers):
    m = _load(rel, name)
    for key in ("csd19532", "csd19536"):
        if key in m.PINS and "/held/" in m.PINS[key][0] and not os.path.exists(os.path.join(ROOT, m.PINS[key][0])):
            raise Skip("%s is held back" % m.PINS[key][0])
    for fn in readers:
        try:
            base = getattr(m, fn)()
        except SystemExit as e:
            raise AssertionError("%s.%s refused (exit %s) on this host's drawing" % (name, fn, e.code))
        assert base, "%s.%s read no line" % (name, fn)
        for rw in (_as_poppler22, _as_poppler24):
            got = _read_with(m, fn, rw)
            assert got == base, "%s.%s reads differently from the %s form" % (name, fn, rw.__name__[4:])


def t_l4e9_reads_figure_10_from_either_serialisation():
    _check(os.path.join("l4e9", "l4e9_power_path.py"), "l4e9_svg_under_test", ("soa_lines",))


def t_l4e11_reads_both_figures_from_either_serialisation():
    _check(os.path.join("l4e11", "l4e11_power.py"), "l4e11_svg_under_test", ("soa_lines", "soa_lines_ktt"))
