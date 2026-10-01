"""Layer 3's baseline accepted again after the amendment (MESHSAT-1357, 1 October 2026): the layer status page and the
acceptance record agree (the page names the accepted revision and the check that closed the findings, and keeps the
open status once, as what the layer read until the acceptance), and the status script refuses what it must. The tests hold before and
after the acceptance is filed (a test pinned to one state would be a test about history): before it, the page reads the
amendment's open status and the script refuses for want of an acceptance; after it, the page names the revision the
record names and the script refuses a second run. Nothing here writes into the tree.
"""
import os
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
L3 = os.path.join(ROOT, "v2", "docs", "handover", "layer3")
AM = os.path.join(ROOT, "v2", "docs", "records", "l3am")
SCRIPT = os.path.join(AM, "apply_layer_status_reaccept.py")
PAGE = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
sys.path.insert(0, L3)
sys.path.insert(0, AM)
from harness import need  # noqa: E402


def _state():
    """(revision or None, valid): the acceptance at the amendment's revision when one is filed, else (None, False)."""
    import render_l3r2 as RL
    import rules_lib as R
    d = RL.load_data()
    ba = d.get("baseline_acceptance") or {}
    if not ba.get("manifest"): return None, False
    return str(ba["revision"]), RL.acceptance_ok(R.load_requirements(), d)[0]


def _section(text):
    return text.split("## Layer 3. Requirements\n", 1)[1].split("\n### History: layer 3 at H2 and H3", 1)[0]


def t_the_page_states_the_acceptance_the_record_holds():
    need(SCRIPT, "apply_layer_status_reaccept.py is not in this tree")
    import apply_layer_status_reaccept as A
    rev, ok = _state()
    l3 = _section(open(PAGE, encoding="utf-8").read())
    if rev is None:
        assert A.NOW_OPEN in l3 and A.MARK not in l3, "no bound acceptance is filed, yet the page does not read the open status"
    else:
        assert ok, "the filed acceptance does not validate"
        assert (A.AGAIN % rev[:8]) in l3 and A.NOW_OPEN not in l3, "the page does not name the accepted revision %s" % rev[:8]
        assert l3.count(A.OPEN) == 1, "the open status is not kept once, as what the layer read until the acceptance"
        import render_l3r2 as RL
        chk = RL.load_data()["review_findings"]["checked_by"]
        assert chk in l3, "the page does not name the check that closed the findings (%s)" % chk
    assert "\"design compliance verified\"" in l3 and "\"fab-ready\"" in l3


def t_the_script_refuses_a_second_run_and_a_page_it_did_not_prepare():
    need(SCRIPT, "apply_layer_status_reaccept.py is not in this tree")
    import apply_layer_status_reaccept as A
    page = open(PAGE, encoding="utf-8").read()
    rev = "0123456789abcdef0123456789abcdef01234567"
    if A.NOW_OPEN in page:
        done = A.build(page, rev)
        assert (A.AGAIN % rev[:8]) in done and A.NOW_OPEN not in done and done.count(A.OPEN) == 1
    else:
        done = page
    for text, why in ((done, "has run"), (page.replace(A.NOW_OPEN, "**Now:**") if A.NOW_OPEN in page else
                                          done.replace(A.MARK, "Layer 3 baseline, "), "has not run")):
        try:
            A.build(text, rev)
        except A.L.Refused as e:
            assert why in str(e), "refused for another reason: %s" % e
        else:
            raise AssertionError("a page the script must refuse (%s) was accepted" % why)


def t_the_script_writes_only_after_the_acceptance_and_once():
    need(SCRIPT, "apply_layer_status_reaccept.py is not in this tree")
    d = tempfile.mkdtemp(prefix="reaccept-"); p = os.path.join(d, "LAYER-STATUS.md")
    open(p, "w", encoding="utf-8").write(open(PAGE, encoding="utf-8").read())
    r = subprocess.run([sys.executable, SCRIPT, "--page", p, "--check"], capture_output=True, text=True, cwd=d)
    rev, _ok = _state()
    want = "has run" if rev is not None else "not accepted again"
    assert r.returncode == 2 and want in r.stdout, "expected a refusal (%s):\n%s" % (want, r.stdout)
