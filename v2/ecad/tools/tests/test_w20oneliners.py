"""W20 (MESHSAT-1357, 6 October 2026): the next set's small items, held as predicates on one patch file.

The file: v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md (rows W20-01 to W20-24 and the NEEDS THE COORDINATOR items W20-N1 to
W20-N3, for the next set's coordinator). Nothing is applied by this branch: every file a row names is the integration's or another
record's, read here at the integration's commit through git. The predicates:

- every row's Old text occurs exactly once in its file at the integration's commit, on the line the row names, and once at the
  branch tip a row waits for; every NEEDS THE COORDINATOR Old text likewise; each New text differs from its Old and the pairs agree;
- every commit the file names exists in the object store;
- the [OWN:n] rows: the new line of the owner file carries the quoted words and the old line does not (part 26 moved them by one);
- the proposed test lines hold where they say: W20-19's per-row RE item on the register (a swapped item fails it), W20-21's phrase in
  D-10's state; the cited readings of sections 4 and 5 (the l4e7 pages at 786aed2f, 83.47 and 83.48 V, the dated heading of line 975);
- no em or en dash, and the prototype framing.

Predicates on record text: they establish no electrical or thermal property, close nothing and accept nothing.
"""
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need  # noqa: E402

PATCH = "v2/docs/records/int30/NEXT-SET-SMALL-ITEMS.patch.md"
C = "c4492dd370c592e9899a8e526113958f4dc20554"
W4 = "786aed2fb32e45e1fba04a516e04c8eff8e89c3a"
DASHES = (chr(0x2013), chr(0x2014))
_G = {}


def _patch():
    return open(need(os.path.join(ROOT, PATCH), "the patch file"), encoding="utf-8").read()


def _show(rev, rel):
    k = (rev, rel)
    if k not in _G:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (rev, rel)], capture_output=True)
        assert r.returncode == 0, "git show %s:%s failed: %s" % (rev, rel, r.stderr.decode()[:200])
        _G[k] = r.stdout.decode("utf-8")
    return _G[k]


def _fences(block):
    return re.findall(r"```text\n(.*?)\n```", block, re.S)


def _rows():
    t = _patch()
    out = []
    for m in re.finditer(r"^### (W20-\d\d)\. (.*?)\n(.*?)(?=^### |^## )", t, re.S | re.M):
        rid, body = m.group(1), m.group(3)
        f = dict(re.findall(r"^- (File|Line|Kind|After|Pairs with|Source|Class|Regeneration): (.*)$", body, re.M))
        old, new = _fences(body)
        out.append(dict(id=rid, rel=f["File"].strip("`"), line=f["Line"], after=f["After"], pairs=f["Pairs with"], klass=f["Class"],
                        old=old, new=new))
    return out


def _needs():
    t = _patch()
    out = []
    for m in re.finditer(r"^- \*\*(W20-N\d[a-z])\*\*, `([^`]+)` line (\S+), Old:\n(.*?)(?=^- \*\*W20-N|^## |^### )", t, re.S | re.M):
        fs = _fences(m.group(4))
        out.append(dict(id=m.group(1), rel=m.group(2), line=m.group(3), old=fs[0], a=fs[1], b=fs[2]))
    return out


def _branch_changes(tip, rel):
    """Whether the branch at tip changes rel since its merge base with the integration (else the merge keeps the integration's)."""
    base = subprocess.run(["git", "-C", ROOT, "merge-base", tip, C], capture_output=True).stdout.decode().strip()
    r = subprocess.run(["git", "-C", ROOT, "diff", "--quiet", base, tip, "--", rel], capture_output=True)
    return r.returncode == 1


def _line_of(text, old):
    i = text.index(old)
    a = text[:i].count("\n") + 1
    b = a + old.count("\n")
    return "%d" % a if a == b else "%d to %d" % (a, b)


def t_every_row_stands_once_where_it_says():
    rows = _rows()
    assert [r["id"] for r in rows] == ["W20-%02d" % i for i in range(1, 25)], [r["id"] for r in rows]
    bad = []
    for r in rows:
        t = _show(C, r["rel"])
        if t.count(r["old"]) != 1:
            bad.append("%s: old text %d times in %s" % (r["id"], t.count(r["old"]), r["rel"]))
            continue
        if _line_of(t, r["old"]) != r["line"]:
            bad.append("%s: line %s, the row says %s" % (r["id"], _line_of(t, r["old"]), r["line"]))
        if r["new"] == r["old"]:
            bad.append("%s: new equals old" % r["id"])
        if r["new"] in t and r["new"] not in r["old"]:
            bad.append("%s: the new text is already in the file" % r["id"])
        m = re.search(r"\(([0-9a-f]{8,40})", r["after"])
        if m and _branch_changes(m.group(1), r["rel"]):
            # the branch rewrites this file, so the row must still find its Old text once after the merge
            tip = _show(m.group(1), r["rel"])
            if tip.count(r["old"]) != 1:
                bad.append("%s: old text %d times at the branch tip %s" % (r["id"], tip.count(r["old"]), m.group(1)))
    assert not bad, "; ".join(bad)


def t_the_pairs_agree():
    rows = {r["id"]: r for r in _rows()}
    for a, b in (("W20-01", "W20-02"), ("W20-05", "W20-09"), ("W20-06", "W20-10"), ("W20-07", "W20-11"), ("W20-08", "W20-12")):
        assert rows[a]["old"] == rows[b]["old"] and rows[a]["new"] == rows[b]["new"], (a, b)
        assert rows[a]["pairs"] == b and rows[b]["pairs"] == a, (a, b)


def t_every_needs_item_stands_once_with_two_candidates():
    ns = _needs()
    assert [n["id"] for n in ns] == ["W20-N1a", "W20-N2a", "W20-N2b", "W20-N2c", "W20-N3a", "W20-N3b"], [n["id"] for n in ns]
    for n in ns:
        t = _show(C, n["rel"])
        assert t.count(n["old"]) == 1, (n["id"], t.count(n["old"]))
        assert _line_of(t, n["old"]) == n["line"], (n["id"], _line_of(t, n["old"]), n["line"])
        assert n["a"] != n["b"] and n["a"] and n["b"], n["id"]
    assert _patch().count("NEEDS THE COORDINATOR") >= 3


def t_every_commit_named_exists():
    t = _patch()
    shas = set(re.findall(r"`([0-9a-f]{8,40})`", t)) | set(re.findall(r"\b(?:at|fnd/\w+) ([0-9a-f]{8,40})\b", t))
    shas |= set(re.findall(r"\(([0-9a-f]{8,40})[,)]", t))
    missing = []
    for s in sorted(shas):
        r = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", s + "^{commit}"], capture_output=True)
        if r.returncode != 0:
            missing.append(s)
    assert len(shas) >= 15, sorted(shas)
    assert not missing, missing


def t_the_own_rows_read_the_moved_line():
    own = _show(C, "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md").splitlines()
    rows = [r for r in _rows() if r["old"].startswith("[OWN:")]
    assert len(rows) == 10, len(rows)
    for r in rows:
        o = int(r["old"][5:-1]); n = int(r["new"][5:-1])
        assert n == o + 1, r["id"]
        words = re.search(r"reads \"(.*?)\"; the file's line", [x for x in _patch().split("### ") if x.startswith(r["id"] + ".")][0]).group(1)
        assert words in own[n - 1], (r["id"], words)
        assert words not in own[o - 1], (r["id"], "the old line still reads the words")
    # part 26's row is the file's line 26 (REVIEW-2B finding 6, W20-22)
    d = subprocess.run(["git", "-C", ROOT, "diff", "-U0", "0d5f855e", "b0a67a45", "--", "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"],
                       capture_output=True).stdout.decode()
    assert "@@ -25,0 +26 @@" in d and "+| 26. The MeshSat communications bootstrap" in d, d[:300]


def t_the_proposed_test_lines_hold_where_they_say():
    reg = _show(C, "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md").splitlines()
    rows = {}
    for l in reg:
        m = re.match(r"\| (R-2\d\d) \|", l)
        if m:
            rows[m.group(1)] = [c.strip() for c in l.strip().strip("|").split(" | ")]
    ns = {}
    exec(compile("\n".join(x[12:] for x in [r for r in _rows() if r["id"] == "W20-19"][0]["new"].splitlines()
                           if x.lstrip().startswith(("RE_OF", "\"R-244\""))), "w20-19", "exec"), {}, ns)
    re_of = ns["RE_OF"]

    def holds(r9, rid):
        return (r9.startswith("ASSIGN to the receiving company's remaining engineering %s (records/l4close/REMAINING-ENGINEERING.md "
                              "section 5): " % re_of[rid]) and "the draft itself stays in its step" in r9 and r9.endswith("(DRAFTED)"))
    for rid in re_of:
        assert rows[rid][8] == "KNOWN ENGINEERING DEFECT" and holds(rows[rid][9], rid), rid
    assert not holds(rows["R-225"][9].replace("item RE-4", "item RE-2"), "R-225"), "a swapped RE item must fail"
    assert sorted({x for v in re_of.values() for x in re.findall(r"RE-\d+", v)}, key=lambda s: int(s[3:])) == \
        ["RE-2", "RE-4", "RE-5", "RE-6", "RE-7", "RE-10"], "SET31-CHANGES.md row 17's union"
    assert "RE-2, RE-4, RE-5 to RE-7 and RE-10" in _show(C, "v2/docs/records/l4e9/SET31-CHANGES.md").splitlines()[47]
    gen = _show(C, "v2/docs/records/l4e9/l4e9_power_path.py")
    i = gen.index('"id": "D-10"'); j = gen.index('"id": "D-11"', i)
    state = re.sub(r'"\s*\n\s*"', "", gen[i:j])
    assert "WITHDRAWN AS DRAFTED, with no protection credit" in state
    cx = _show(C, "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md").splitlines()
    assert "D-10 itself remains OPEN REMAINING ENGINEERING" in cx[187]
    assert "it does not resolve D-10" in _show(C, "v2/docs/records/l4e7/L4E7-P0SOL.md").splitlines()[141]
    assert "it does not resolve D-10" in _show(W4, "v2/docs/records/l4e7/L4E7-P0SOL.md").splitlines()[186]


def t_the_readings_of_sections_4_and_5():
    b2 = _show(W4, "v2/docs/records/l4e7/B2-PRESENCE.md").splitlines()
    p11 = _show(W4, "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md").splitlines()
    assert "below the stage's voltage" not in " ".join(b2[167:170]) and "below the stage's voltage" in b2[180]
    norm = lambda s: " ".join(s.split())
    assert "back-feeding PV_F through Q12's body diode" not in norm(" ".join(p11[119:123]))
    assert "back-feeding PV_F through Q12's body diode" in p11[159]
    cb2 = _show(C, "v2/docs/records/l4e7/B2-PRESENCE.md").splitlines()
    assert "below the stage's voltage" in norm(" ".join(cb2[167:170])), "the cited lines read at the integration"
    p0 = _show(W4, "v2/docs/records/l4e7/L4E7-P0SOL.md").splitlines()
    assert "It is REMAINING ENGINEERING inside E-1" in norm(" ".join(p0[143:145]))
    assert "E-1 also carries one OPEN" in p0[140] and "lower-source back-feed case" in p0[148]
    assert "OWNER-INSTRUCTION-2026-10-05.md:680" in p0[147]
    cd = _show(C, "v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md").splitlines()
    assert "83.47 V" in cd[619] and "83.47 V" in cd[1023]
    assert "PV_F 83.48 V" in _show(C, "v2/docs/records/l4e7/SUPPLIER-P1-1-P0SOL.md").splitlines()[32]
    out = _show(C, "v2/docs/records/l4e9/l4e9_power_path.out").splitlines()
    assert out[943].startswith("13. UPDATE ROUND 3 (2 October 2026)") and "criterion 2 CONDITIONAL" in out[974]
    assert out[977].startswith("14. UPDATE ROUND 5") and "criterion 2 FAIL" in out[1016]
    assert not any(re.match(r"^\d+[a-z]?\. ", l) for l in out[944:974]), "no other heading between 944 and 975"
    con = _show(C, "v2/docs/records/l9t5/l9t5_connected.out").splitlines()
    assert "until the integrator applies it" in con[61] and "118 changes" in con[61] and "rev X stays on V-B20" in con[215]
    led = _show(C, "v2/docs/records/l4close/REMAINING-ENGINEERING.md").splitlines()
    assert "Line numbers are those of the tip read (`1c6d56f5`)" in led[45] and led[47].startswith("`6fe398e9`")
    hw = _show(C, "v2/docs/HW-FW-CONTRACT.md")
    assert "TRK_VIN" not in hw and "IMON_IN" not in hw


def t_no_dashes_and_the_prototype_framing():
    t = _patch()
    for ch in DASHES:
        assert ch not in t
        assert ch not in open(os.path.abspath(__file__), encoding="utf-8").read()
    assert "nothing in the kit is built, bought, powered or measured" in t
    assert t.startswith("**DONE:**") and "**NOT DONE:**" in t and "**NEXT:**" in t
