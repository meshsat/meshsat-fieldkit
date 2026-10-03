"""Layer 5's round 4 (MESHSAT-1357, set 29, 3 October 2026; v2/docs/records/l5r4/): the panel firmware's finding F-14 decided, one
slot-fault rule for a compute module lost at start-up and one lost while running.

The predicates: CONOPS.md (section 4e's row "a compute module lost", section 3's M5, section 4's Startup row) and PANEL.md section 5
agree: the same hold-off, one cycle, the same rail-off time, left off until the operator acts, and PANEL.md's rule covers the slot lost
while running as well as at start-up, citing CONOPS as its source; HW-FW-CONTRACT.md's FW-C05 states the same rule and FW-C02 keeps a
slot left off across a controller reset; REQ-062's start-up case is one case of the rule; the round's apply script reads already
applied on the tree, applies once to the files it was written against and is idempotent; the rebind script for the integrator checks
or reads already applied; no em or en dash in the record. Software predicates on text: they establish no electrical property and
accept nothing.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
DOCS = os.path.join(ROOT, "v2", "docs")
REC = os.path.join(DOCS, "records", "l5r4")
APPLY = os.path.join(REC, "apply_l5r4.py")
REBIND = os.path.join(REC, "apply_l5r4_rebind.py")
BASE = "92a5c7d8"          # set 28's line before this round: the files apply_l5r4.py was written against
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402


def _flat(s):
    return " ".join(s.split())


def _page(name):
    return open(need(os.path.join(DOCS, name), name), encoding="utf-8").read()


def _section(text, start, end):
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i:j]


def _panel5():
    return _flat(_section(_page("PANEL.md"), "## 5. Compute slots seen from the panel", "## 6."))


def _conops_rows():
    t = _page("CONOPS.md")
    row = [ln for ln in t.split("\n") if ln.startswith("| a compute module lost |")]
    assert len(row) == 1, "CONOPS.md section 4e's row 'a compute module lost' is not there once"
    cells = [c.strip() for c in row[0].strip()[1:-1].split("|")]
    start = [ln for ln in t.split("\n") if ln.startswith("| Startup |")]
    assert len(start) == 1, "CONOPS.md section 4's Startup row is not there once"
    m5 = _flat(_section(t, "### M5. Degraded operation during a mission", "\n### ")) if "### M5." in t else ""
    return cells, _flat(start[0]), m5


def _run(args):
    return subprocess.run([sys.executable, "-B"] + args, capture_output=True, text=True)


def t_conops_and_panel_agree_on_the_slot_fault_rule():
    cells, startup, m5 = _conops_rows()
    recovery = _flat(cells[3])
    assert "cycled once and then left off until the operator acts" in recovery and "`PANEL.md` section 5" in recovery, recovery
    mm = re.search(r"a slot whose heartbeat stays flat for (\d+) s is power-cycled once and then left off until the operator acts", m5)
    ms = re.search(r"a slot with a flat heartbeat after (\d+) s is marked faulty, cycled once, then left off", startup)
    assert mm and ms, "CONOPS.md's M5 or Startup sentence on the slot cycle moved: re-read F-14"
    s5 = _panel5()
    # PANEL.md section 5: one rule for both cases, CONOPS the source
    assert "one rule for a module lost at start-up and one lost while running" in s5
    assert "the source is `CONOPS.md` section 4e's row \"a compute module lost\"" in s5
    hold = re.search(r"has had no edge for (\d+) s, counted from its rail coming up or from its last edge, whichever is later", s5)
    flat_start = re.search(r"or when it stays flat for (\d+) s after its rail came up", s5)
    off = re.search(r"the first time it power-cycles the slot once \(rail off (\d+) s\), which spends the slot's one retry", s5)
    assert hold and flat_start and off, "PANEL.md section 5's rule moved: re-read F-14"
    assert int(hold.group(1)) == int(mm.group(1)) == int(ms.group(1)) == int(flat_start.group(1)), \
        "the hold-off differs: PANEL.md %s s, CONOPS M5 %s s, Startup %s s" % (hold.group(1), mm.group(1), ms.group(1))
    assert "then leaves it off until the operator acts" in s5 and "each of the three re-arms the slot's retry" in s5
    # the old start-up-only trigger is gone: no sentence cycles a slot only for a heartbeat flat after its rail came up
    assert "A slot whose heartbeat stays flat for 60 s after its rail came up is shown as a slot fault" not in s5
    assert "lost when its heartbeat has had no edge for 3 s after an edge" in s5


def t_fw_c05_states_the_same_rule_and_fw_c02_keeps_a_slot_left_off():
    t = _page("HW-FW-CONTRACT.md")
    rows = {}
    for ln in t.split("\n"):
        m = re.match(r"^\| ((FW|V)-C\d\d) \|", ln)
        if m:
            rows[m.group(1)] = _flat(ln)
    c05, c02, v05 = rows["FW-C05"], rows["FW-C02"], rows["V-C05"]
    s5 = _panel5()
    hold5 = re.search(r"has had no edge for (\d+) s, counted from", s5).group(1)
    off5 = re.search(r"\(rail off (\d+) s\)", s5).group(1)
    hold = re.search(r"at (\d+) s without an edge, counted from the later of its rail coming up and its last edge", c05)
    off = re.search(r"power-cycle it once \(SLOT_EN low (\d+) s\), its one retry", c05)
    assert hold and off and hold.group(1) == hold5 and off.group(1) == off5, (hold and hold.group(1), off and off.group(1), hold5, off5)
    for s in ("declare it lost after 3 s without an edge", "leave it off until the operator acts", "each act re-arming the retry",
              "CHIP_RESET HAD_POR", "`CONOPS.md` section 4e governs", "F-14"):
        assert s in c05, s
    assert "a slot left off stays off across the reset, F-14" in c02
    assert "60 s after its last edge" in v05 and "stays off across a panel watchdog reset and a RUN reset" in v05


def t_req_062_is_one_case_of_the_rule():
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_requirements.yaml"), encoding="utf-8").read())
    r = [x for x in d["records"] if x["id"] == "REQ-062"][0]
    st = _flat(r["statement"])
    assert r["parent"] == "NEED-03"
    m = re.search(r"a slot whose heartbeat stays flat for (\d+) s after its rail came up is shown as a slot fault, power-cycled once "
                  r"\(rail off (\d+) s\), then left off until the operator acts", st)
    assert m, "REQ-062 moved: re-read F-14"
    s5 = _panel5()
    assert ("stays flat for %s s after its rail came up" % m.group(1)) in s5 and ("(rail off %s s)" % m.group(2)) in s5
    assert "is shown as a slot fault" in s5 and "then leaves it off until the operator acts" in s5


def _base_copies(d):
    out = {}
    for rel in ("v2/docs/PANEL.md", "v2/docs/HW-FW-CONTRACT.md"):
        g = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, rel)], capture_output=True)
        if g.returncode != 0:
            raise Skip("commit %s is not in this repository" % BASE)
        p = os.path.join(d, os.path.basename(rel))
        open(p, "wb").write(g.stdout)
        out[rel] = p
    return out


def t_the_apply_script_is_applied_and_idempotent():
    need(APPLY, "the round's script")
    r = _run([APPLY, "--check"])
    assert r.returncode == 0 and "already applied" in r.stdout, (r.returncode, r.stdout[-200:], r.stderr[-300:])
    d = tempfile.mkdtemp(prefix="l5r4-apply-")
    try:
        c = _base_copies(d)
        args = ["--panel", c["v2/docs/PANEL.md"], "--hwfw", c["v2/docs/HW-FW-CONTRACT.md"]]
        r = _run([APPLY, "--check"] + args)
        assert r.returncode == 0 and "CHECK OK" in r.stdout, r.stderr[-300:]
        r = _run([APPLY, "--write"] + args)
        assert r.returncode == 0 and "WRITTEN" in r.stdout, r.stderr[-300:]
        r = _run([APPLY, "--write"] + args)
        assert r.returncode == 0 and "already applied" in r.stdout, r.stderr[-300:]
        t = open(c["v2/docs/PANEL.md"], encoding="utf-8").read()
        open(c["v2/docs/PANEL.md"], "w", encoding="utf-8").write(t + "\nA slot whose heartbeat stays flat for 60 s after its rail came up "
                                                               "is shown as a slot fault (MASTER CAUT, the e-paper names the slot); the controller power-cycles it once (rail off 5 s) and then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol (owed with MESHSAT-837; the panel firmware's F-02 and S-04), or by restarting the kit with MAIN, after which every slot is raised again (decided 3 October 2026, F-09, record l5r2, `L5-PANEL-R3.md`: the sentence named no control).\n")
        r = _run([APPLY, "--check"] + args)
        assert r.returncode == 3 and "not in the state" in r.stderr, r.stderr[-300:]
    finally:
        shutil.rmtree(d)


def t_the_rebind_script_checks_or_reads_already_applied():
    need(REBIND, "the rebind script")
    r = _run([REBIND, "--check"])
    if r.returncode == 3:
        assert "already applied" in r.stdout, r.stdout[-300:]
    else:
        assert r.returncode == 0, r.stdout[-300:]
        for rid in ("CFL-001", "CFL-005", "CFL-014", "CFL-015", "CFL-016"):
            assert re.search(r"rebinds %s [0-9a-f]{16} -> [0-9a-f]{16}, evidence_result \S+ unchanged" % rid, r.stdout), rid


def t_no_dashes_in_the_record():
    files = [os.path.join(dp, f) for dp, _dn, fs in os.walk(REC) for f in fs if f.endswith((".md", ".py", ".out", ".txt"))]
    files += [os.path.abspath(__file__)]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "%s carries an em or en dash" % os.path.relpath(p, ROOT)
