"""The definition re-issue on the owner's layer 3 answers is prepared and follows the recorded answers (MESHSAT-1357,
layer 3 round 4, 30 September 2026; closure item L3-C26; round 4b on CHECK-1 of round 4).

`v2/docs/records/l3r4/reissue.py` maps every passage of the baselined CONOPS.md and PRODUCT-BRIEF.md that an answer to
rows L3-OD1 to L3-OD6 makes inconsistent with the requirements, restated (DEFINITION) or read through
DEFINITION-STATUS.md as the design as generated (CURRENT: the QMX, the one pack's chain, board A's front end, the held
cell), and once the registry records the answers it writes the proposed re-issue and its change record. These tests
hold the passage map to the baselined files, run the prepared owner-decision scripts of L3-R2
(v2/docs/records/l3r2/conditional/) on COPIES of the registry in the pattern of its dry runs, and check the generator on
the session's recommended answers, on two other coherent combinations, and its refusals: rows undecided, an incoherent
set, a write into a baselined file or through a link, and a rewrite once the re-issue is approved (the approval leaves
the draft and the record current and the renderer accepts them). `apply_layer_status_l3_r4.py` is run on a copy of
LAYER-STATUS.md. Nothing here writes into the tree.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l3r4")
COND = os.path.join(ROOT, "v2", "docs", "records", "l3r2", "conditional")
L3DATA = os.path.join(ROOT, "v2", "docs", "handover", "layer3", "l3r2.yaml")
GEN = os.path.join(REC, "reissue.py")
LSTAT = os.path.join(REC, "apply_layer_status_l3_r4.py")
BASE = {"v2/docs/CONOPS.md": None, "v2/docs/PRODUCT-BRIEF.md": None}
DASHES = ("\u2013", "\u2014")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402
import claims_check as CC  # noqa: E402

# The session's recommended answers (OWNER-DECISIONS-L3.md): approve at the kit loads (sub-choice 1b), 2s2p, adopt,
# reading-c and the mean day. Rows L3-OD2 (which lid item leaves), L3-OD6's build and row L3-OD4's operator push are the
# owner's with no recommendation; the fixture takes the QMX out, TYP and a push of 10 N as STAND-INS (dryrun.py's), not
# as recommendations.
# D-27: row L3-OD7 (M1's runtime and its store) is answered first; 72-required with HF available, no external store and the
# tablet not charged, the one answer whose passages are mapped, is a STAND-IN for the owner's answer in every chain.
R7 = ("od_l3_7.py", "72-required", "--hf", "available", "--external", "no", "--tablet-charging", "no")
RECOMMENDED = [R7, ("od_l3_6.py", "mean-day", "--build", "TYP"), ("od_l3_1.py", "approve", "--pass-line", "kit-loads"),
               ("od_l3_2.py", "qmx-out"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt", "--push-n", "10"),
               ("od_l3_5.py", "reading-c")]
# D-26: row L3-OD1 rejected is a valid answer; row L3-OD2 then does not apply, and a 2 degree slope stands in for the
# owner's own figure for the lid with no lid pack.
REJECTED = [R7, ("od_l3_1.py", "reject"), ("od_l3_3.py", "2s2p"), ("od_l3_4.py", "adopt", "--push-n", "10", "--slope-deg", "2"),
            ("od_l3_5.py", "reading-c"), ("od_l3_6.py", "mean-day", "--build", "TYP")]
OTHER = [R7, ("od_l3_6.py", "mean-day", "--build", "WAB"), ("od_l3_1.py", "approve", "--pass-line", "kit-loads"), ("od_l3_2.py", "qmx-outside"),
         ("od_l3_3.py", "1s4p"), ("od_l3_4.py", "reject"), ("od_l3_5.py", "measure")]
THIRD = [R7, ("od_l3_6.py", "mean-day", "--build", "TYP"), ("od_l3_1.py", "approve", "--pass-line", "kit-loads"), ("od_l3_2.py", "tablet-out"),
         ("od_l3_3.py", "keep", "--array-wp", "1100", "--entry-a", "80", "--evidence", "EV"), ("od_l3_4.py", "reject"),
         ("od_l3_5.py", "cells")]
# The one pack's generated chain by its designators: every baselined line naming one lies in a PACK passage (B1).
PACK_DESIGNATORS = re.compile(r"BQ25731|BQ7720700|\bR17\b|ADCVBAT|ADCIDCHG|0x6B|0x0010|SLUSE66A|SLUUAQ3A|CHRG_INHIBIT|"
                              r"\bCHG_INHIBIT\b|CELL_F|J_SMB|pack node|\bK3\b|\bVBAT\b|\bF2\b|\bJP1\b|gen_sch_p\.py|"
                              r"pcb_pack_protection")
_CHAINS = {}


def _run(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd or tempfile.gettempdir())


def _mod():
    need(GEN, "the re-issue generator is not in this tree")
    sys.path.insert(0, REC)
    import reissue as RI
    return RI


def _sha(rel):
    import hashlib
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


def _tree_undecided():
    import yaml
    d = yaml.safe_load(open(os.path.join(TOOLS, "pcb_requirements.yaml"), encoding="utf-8"))
    rows = [str(r.get("decides")).split(":")[0] for r in d["owner_rulings"] if str(r.get("decides") or "").startswith("L3-OD")]
    if rows: raise Skip("rows %s are decided in this tree; the fixtures start from undecided rows" % ", ".join(rows))


def _chain(steps):
    """A copy of the registry with the steps applied by the prepared scripts, as dryrun.py applies them; each chain
    is built once per run and handed out as a fresh copy."""
    need(COND, "the conditional scripts of L3-R2 are not in this tree")
    _tree_undecided()
    key = tuple(tuple(s) for s in steps)
    if key not in _CHAINS:
        d = tempfile.mkdtemp(prefix="l3r4-reg-")
        reg = os.path.join(d, "pcb_requirements.yaml")
        shutil.copy(os.path.join(TOOLS, "pcb_requirements.yaml"), reg)
        ev = os.path.join(d, "basis-fixture.md")
        open(ev, "w", encoding="utf-8").write("FIXTURE, not the energy basis: array 1100 Wp, entry 80 A.\n")
        for s in steps:
            extra = [ev if x == "EV" else x for x in s[2:]]
            r = _run([os.path.join(COND, s[0]), "--option", s[1], "--words", "test words", "--date", "2026-10-01",
                      "--registry", reg] + extra, cwd=d)
            assert r.returncode == 0, "%s --option %s exit %d:\n%s" % (s[0], s[1], r.returncode, (r.stdout + r.stderr)[-500:])
        _CHAINS[key] = reg
    d = tempfile.mkdtemp(prefix="l3r4-reg-")
    reg = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(_CHAINS[key], reg)
    return d, reg


def _generate(reg, expect=0, out=None, extra=()):
    out = out or tempfile.mkdtemp(prefix="l3r4-out-")
    before = {k: _sha(k) for k in BASE}
    r = _run([GEN, "--registry", reg, "--out-dir", out] + list(extra))
    assert r.returncode == expect, "reissue.py exit %d (expected %d):\n%s" % (r.returncode, expect, (r.stdout + r.stderr)[-600:])
    assert {k: _sha(k) for k in BASE} == before, "a baselined file changed while reissue.py ran"
    return out, r.stdout


def _read(out):
    RI = _mod()
    return (open(os.path.join(out, RI.DRAFT), encoding="utf-8").read(),
            open(os.path.join(out, RI.RECORD), encoding="utf-8").read())


def _flat(text):
    return " ".join(re.sub(r"^> ?", "", text, flags=re.M).split())


def _section(draft, pid):
    m = re.search(r"^### %s\. .*?(?=^### |^## )" % pid, draft, re.M | re.S)
    return m.group(0) if m else ""


def _common(reg, out, rows=None):
    """What holds for every generated re-issue: each passage names its rows and rulings, every ruling of the answers is
    cited, the change record binds the draft by its sha, M1's reading is stated plainly with its status row, and the
    texts carry no dash and no unqualified claim."""
    import yaml
    RI = _mod()
    draft, rec = _read(out)
    d = yaml.safe_load(open(reg, encoding="utf-8"))
    rids = {str(r["decides"]).split(":")[0]: r["id"] for r in d["owner_rulings"] if str(r.get("decides") or "").startswith("L3-OD")}
    assert sorted(rids) == sorted(rows or RI.ROWS), "the fixture does not decide its rows: %s" % sorted(rids)
    heads = re.findall(r"^### ([CB]\d\d)\. .*$", draft, re.M)
    cites = re.findall(r"^Rows and rulings: (.*)\.$", draft, re.M)
    assert heads and len(heads) == len(cites), "a restated passage has no 'Rows and rulings' line"
    for h, c in zip(heads, cites):
        assert re.search(r"L3-OD\d `[a-z0-9-]+`, D-\d+", c), "passage %s names no row and ruling: %r" % (h, c)
    for row, rid in rids.items():
        assert "%s `" % row in draft and rid in draft, "the draft does not cite %s's ruling %s" % (row, rid)
    import hashlib
    assert hashlib.sha256(draft.encode("utf-8")).hexdigest()[:16] in rec, "the change record does not name the draft's sha"
    assert "PROPOSED" in draft and "PROPOSED" in rec and "definition_reissue" in rec
    r72 = next(r for r in d["records"] if r["id"] == "REQ-072")
    assert "REQ-072 reads %s" % r72["evidence_result"] in _flat(draft), "the draft does not state REQ-072's reading"
    assert "| DC-L3-M1 |" in draft, "the draft proposes no status row for M1's reading"
    if r72["evidence_result"] == "FAIL":
        assert "Does not meet mission M1 as the design stands." in _flat(_section(draft, "B15")), "B15 is softer than FAIL"
    for t in (draft, rec):
        assert not any(x in t for x in DASHES), "a generated text carries a dash character"
    assert "\n\nStatements of the design as generated" in rec and "\n\nWhere a passage the re-issue does not restate" in rec, \
        "the change record runs its paragraphs together"
    n, bad = CC.check([os.path.join(out, RI.DRAFT), os.path.join(out, RI.RECORD)])
    assert not bad, "a generated text carries an unqualified claim: %s" % bad[:2]
    r = _run([GEN, "--registry", reg, "--out-dir", out, "--check"])
    assert r.returncode == 0, "--check reads the files it has just written as out of date:\n%s" % r.stdout
    return draft, rec, rids


def _proposed(RI, reg):
    """The re-issue applied in memory, and the baselined texts: outside the restated passages nothing moves."""
    import yaml
    docs = RI.baselined()
    c = RI.answers(yaml.safe_load(open(reg, encoding="utf-8")), RI.RL.load_data())
    applied, cur = RI.apply_all(docs, c)
    for k, (text, edits) in applied.items():
        back = text
        for p, old, new in edits:
            assert back.count(new) >= 1, "%s's proposed text is not in the proposed document" % p.pid
            back = back.replace(new, old, 1)
        assert back == docs[k], "%s outside the restated passages moved" % k
    return c, applied, cur


def _groups(cur):
    out = {}
    for p in cur: out.setdefault(p.group, []).append(p.a)
    return out


# ------------------------------------------------------------------------------------------------ the map
def t_l3r4_the_passage_map_is_generated_from_the_baselined_files():
    RI = _mod()
    r = _run([GEN, "--map", "--check"])
    assert r.returncode == 0, "PASSAGE-MAP.md is not what reissue.py --map writes:\n%s" % r.stdout
    body = open(RI.MAP, encoding="utf-8").read()
    docs = RI.baselined()
    for p in RI.PASSAGES:
        off, end, old = RI.locate(docs[p.doc], p)
        assert RI.quote(old) in body, "the map does not quote %s whole" % p.pid


def t_l3r4_every_passage_is_found_once_where_the_map_says():
    RI = _mod()
    docs = RI.baselined()
    ids = [p.pid for p in RI.PASSAGES]
    assert len(ids) == len(set(ids)), "a passage id repeats"
    for p in RI.PASSAGES:
        off, end, old = RI.locate(docs[p.doc], p)
        line = docs[p.doc][:off].count("\n") + 1
        assert line == p.a, "%s starts on line %d, not %d" % (p.pid, line, p.a)
        assert (p.new is None) == (p.kind == "CURRENT"), "%s: a CURRENT passage has no proposed text, a DEFINITION one does" % p.pid
        assert (p.group is None) == (p.kind == "DEFINITION"), "%s: only a CURRENT passage has a group" % p.pid
        assert p.when == RI.ALL or set(p.when) <= set(RI.ROWS), "%s names a row that is not L3-OD1 to L3-OD7" % p.pid


def t_l3r4_every_line_of_the_one_pack_chain_is_a_current_passage():
    """CHECK-1 of round 4, B1: a baselined line of the definition that names the one pack's charge, measurement or
    protection chain by a designator lies in a PACK passage, except the rulings table of section 7 (history)."""
    RI = _mod()
    docs = RI.baselined()
    text = docs["CONOPS"]
    lines = text[:text.index("\n## Appendix")].split("\n")
    covered = {n for p in RI.PASSAGES if p.group == "PACK" for n in range(p.a, p.b + 1)}
    rulings = [i for i, l in enumerate(lines, 1) if l.startswith("| D-")]
    miss = [i for i, l in enumerate(lines, 1) if PACK_DESIGNATORS.search(l) and i not in covered and i not in rulings]
    assert not miss, "lines naming the one pack's chain are in no PACK passage: %s" % miss
    brief = docs["BRIEF"][:docs["BRIEF"].index("\n## Appendix")]
    assert not PACK_DESIGNATORS.search(brief), "the brief names the pack's chain by a designator the map does not hold"


def t_l3r4_every_line_naming_the_chain_or_the_cell_in_words_is_mapped():
    """CHECK-2 of round 4, minors 1 and 4, and CHECK-3, minors 1 and 2: VOCAB_RX itself (not only the phrases the
    group's passages already carry) matches no line of either document, before its appendix, outside the group's
    passages, section 7's rulings table and the reasoned EXEMPT list; every EXEMPT line carries a match; and the CELL
    pattern holds the cell sheet's ageing figures."""
    RI = _mod()
    docs = RI.baselined()
    for g in ("PACK", "CELL"):
        rx = re.compile(RI.VOCAB_RX[g])
        assert RI.vocabulary(g, docs), "the %s passages carry none of their vocabulary" % g
        left = RI.uncovered(g, docs)
        assert not left, "lines the %s pattern matches are in none of its passages: %s" % (g, left[:5])
        for (k, n), why in RI.EXEMPT[g].items():
            ls = docs[k].split("\n")
            assert why and any(m.start() <= len(ls[n - 1]) for m in rx.finditer("\n".join(ls[n - 1:n + 1]))), \
                "the %s exemption of %s line %d matches nothing: a stale exemption" % (g, k, n)
    pv = RI.vocabulary("PACK", docs)
    assert any(v.startswith("the charger") for v in pv) and any(v.startswith("the gauge") for v in pv), \
        "the PACK vocabulary lost the chain's parts"
    cv = RI.vocabulary("CELL", docs)
    assert "60 % after 500 cycles" in cv and "the cell's specification minimum" in cv, "the CELL group lost the ageing"


def t_l3r4_removing_a_group_passage_is_caught():
    """CHECK-3 of round 4, minor 1: each PACK and CELL passage, taken out of the list, leaves a line its group's pattern
    (or, for PACK, a designator) matches and no other passage holds, so no passage can be dropped silently; and the
    passage list is pinned against the committed map's headings."""
    RI = _mod()
    docs = RI.baselined()
    keep = list(RI.PASSAGES)
    try:
        for p in [x for x in keep if x.group in ("PACK", "CELL")]:
            RI.PASSAGES[:] = [x for x in keep if x is not p]
            left = RI.uncovered(p.group, docs)
            if p.group == "PACK" and not left:
                cov = {n for x in RI.PASSAGES if x.group == "PACK" for n in range(x.a, x.b + 1)}
                left = [n for n in range(p.a, p.b + 1) if n not in cov and
                        PACK_DESIGNATORS.search(docs[p.doc].split("\n")[n - 1])]
            assert left, "removing %s (%s lines %d to %d) is not caught" % (p.pid, p.doc, p.a, p.b)
    finally:
        RI.PASSAGES[:] = keep
    body = open(RI.MAP, encoding="utf-8").read()
    heads = re.findall(r"^### (\w+)\. (\S+), lines? (\d+)(?: to (\d+))? \((DEFINITION|CURRENT)(?:, (\w+))?\)$", body, re.M)
    pinned = [(h[0], h[1], int(h[2]), int(h[3] or h[2]), h[4], h[5] or None) for h in heads]
    have = [(p.pid, os.path.basename(RI.DOCS[p.doc]), p.a, p.b, p.kind, p.group) for p in RI.PASSAGES]
    assert pinned == have, "the passage list differs from the committed map: run reissue.py --map and review the diff"


def t_l3r4_the_baselines_are_the_files_l3r2_names():
    RI = _mod()
    data = RI.RL.load_data()
    for rel in BASE:
        assert _sha(rel) == str(data["baseline_definition"][rel]), "%s is not the baselined text: the map reads another" % rel


# ------------------------------------------------------------------------------------------------ the answers
def t_l3r4_the_recommended_answers_give_the_reissue():
    RI = _mod()
    d, reg = _chain(RECOMMENDED)
    out, msg = _generate(reg)
    draft, rec, rids = _common(reg, out)
    c, applied, cur = _proposed(RI, reg)
    got = {p.pid for k in applied for p, o, n in applied[k][1]}
    for pid in ("C03", "C05", "C06", "C07", "C09", "C14", "C17", "C19", "C21", "C29", "C31", "B03", "B06", "B08", "B13",
                "B15", "B18"):
        assert pid in got, "the recommended answers leave %s unrestated" % pid
    g = _groups(cur)
    assert len(g["HF"]) == len(RI.CURRENT["HF"][0]) and len(g["PACK"]) == len(RI.CURRENT["PACK"][0]), \
        "the QMX out and two packs leave %s as the design as generated" % {k: len(v) for k, v in g.items()}
    assert set(g) == {"HF", "PACK", "SOLAR"} and g["SOLAR"] == [991], "the recommended answers touch %s" % sorted(g)
    for row in ("HF", "PACK", "SOLAR"):
        assert "| DC-L3-%s |" % row in draft, "the status row DC-L3-%s for the design as generated is missing" % row
    head = _flat(_section(draft, "C02"))
    assert "states a requirement, an intention or a condition about \"the pack\"" in head and \
        "states the circuit as generated for one pack" in head, "the head note reads every passage as two packs"
    rq = c.deploy_req()
    flat = _flat(draft)
    assert rq in draft and c.stmt(rq) in flat, "the deployment condition is not quoted from %s" % rq
    assert c.stmt("REQ-072") in flat, "M1's energy passage does not quote REQ-072 as restated"
    assert "4S15P lid pack" in draft, "the QMX out of the lid does not give the 4S15P lid pack"
    assert "an %s tablet in the lid bracket" % c.tablet_size() in flat and c.tablet_size() in c.stmt("REQ-011")
    assert c.array_phrase() in flat and "2S2P" in c.text("L3-OD3"), "the array is not the ruling's"
    cell, base = c.od1_store()
    assert cell in c.text("L3-OD1") and base in c.text("L3-OD1") and c.store() in flat, "the store is not row L3-OD1's ruling's"
    assert "reopens" not in c.store(), "the store calls the cell reopened without row L3-OD5 answered cells"
    assert "of the %s cells: a base %s" % (cell, base) in _flat(_section(draft, "B06")), "B06 lost its cells"
    assert "HF has left the kit (owner ruling %s on row L3-OD2)" % rids["L3-OD2"] in draft
    assert "(CFL-017 resolved)" in flat, "reading-c resolves CFL-017 and the D-02a row does not say so"


def t_l3r4_another_coherent_combination_gives_its_own_reissue():
    """The QMX carried outside with HF kept, 1S4P, no deployment condition and CFL-017 kept open; and the tablet out
    with REQ-016 kept and cells above +60 C: other passages, other rows for the design as generated."""
    RI = _mod()
    d, reg = _chain(OTHER)
    out, msg = _generate(reg)
    draft, rec, rids = _common(reg, out)
    c, applied, cur = _proposed(RI, reg)
    got = {p.pid for k in applied for p, o, n in applied[k][1]}
    assert {"B09", "C03", "C21", "C29"} <= got, "the QMX outside or CFL-017 kept open leaves a passage unrestated"
    assert not ({"C05", "C06", "C10", "C13", "B05", "B13"} & got), "HF kept or no deployment condition restates a passage"
    g = _groups(cur)
    assert g.get("HF") == [1095] and g.get("SOLAR") == [991] and "CELL" not in g, "the groups read %s" % g
    assert "1S4P" in draft and "deployment condition (owner ruling" not in draft and "4S15P lid pack" in draft
    for pid in ("C29", "B18"):
        sec = _flat(_section(draft, pid)).split("Proposed text:")[-1]
        assert "answered" not in sec.lower() and "kept open" in sec, "%s says CFL-017 was answered under measure" % pid
    d3, reg3 = _chain(THIRD)
    out3, msg3 = _generate(reg3)
    draft3, rec3, rids3 = _common(reg3, out3)
    c3, applied3, cur3 = _proposed(RI, reg3)
    got3 = {p.pid for k in applied3 for p, o, n in applied3[k][1]}
    g3 = _groups(cur3)
    assert {"C04", "B04", "C08", "B12"} <= got3 and set(g3) == {"PACK", "CELL"}, "the tablet out and cells read %s" % sorted(g3)
    assert "4S14P lid pack" in draft3 and "the tablet bracket has left the kit" in draft3
    assert "| DC-L3-CELL |" in draft3 and "reopens; CFL-017 is kept open in the requirements registry" in _flat(draft3)
    assert c3.array_phrase() in _flat(draft3) and "1100 Wp" in c3.text("L3-OD3")
    for pid in ("C07", "C23", "B06", "B15"):
        sec = _flat(_section(draft3, pid)).split("Proposed text:")[-1]
        assert "as held, the cell of D-06 that owner ruling %s on row L3-OD5 reopens (CFL-017 kept open)" % rids3["L3-OD5"] \
            in sec, "%s names the cell as settled under cells" % pid
    assert "CFL-017 is kept open in the requirements registry" in _flat(draft3), "the cell sentence types CFL-017's state"


def t_l3r4_the_approval_leaves_the_reissue_current_and_unwritten():
    """CHECK-1 of round 4, minor 1: decide the rows, generate, record the owner's approval (a ruling that decides
    definition_reissue, and l3r2.yaml's definition_reissue naming the record at its sha); the draft and the record read
    current, a write is refused and leaves them unchanged, and the renderer accepts the re-issue."""
    import yaml
    RI = _mod()
    d, reg = _chain(RECOMMENDED)
    out, msg = _generate(reg)
    draft, rec = _read(out)
    req = yaml.safe_load(open(reg, encoding="utf-8"))
    n = max(int(r["id"].split("-")[1]) for r in req["owner_rulings"] if re.match(r"^D-\d+$", str(r["id"])))
    req["owner_rulings"].append({"id": "D-%d" % (n + 1), "authority": "OWNER", "ruled_on": "2026-10-02",
                                 "title": "The definition re-issue approved (test)", "decides": "definition_reissue",
                                 "words": "test words", "ruling": "The change record is approved (a test fixture).",
                                 "source": ["owner ruling D-%d" % (n + 1)]})
    reg2 = os.path.join(d, "approved.yaml")
    open(reg2, "w", encoding="utf-8").write(yaml.safe_dump(req, allow_unicode=True, sort_keys=False))
    data = yaml.safe_load(open(L3DATA, encoding="utf-8"))
    recp = os.path.join(out, RI.RECORD)
    data["definition_reissue"] = {"record": recp, "sha16": RI.RL.sha16_bytes(open(recp, "rb").read()),
                                  "approved_by": "D-%d" % (n + 1)}
    data2 = os.path.join(d, "l3r2-approved.yaml")
    open(data2, "w", encoding="utf-8").write(yaml.safe_dump(data, allow_unicode=True, sort_keys=False))
    r = _run([GEN, "--registry", reg2, "--data", data2, "--out-dir", out, "--check"])
    assert r.returncode == 0, "the approval made the draft or the record out of date:\n%s" % r.stdout
    _generate(reg2, expect=2, out=out, extra=["--data", data2])
    assert _read(out) == (draft, rec), "a refused rewrite changed the approved draft or record"
    dec = RI.RL.decided(req, data)
    ok, why = RI.RL.reissue_ok(req, data, dec)
    assert ok, "the renderer refuses the approved re-issue: %s" % why
    r72 = next(r for r in req["records"] if r["id"] == "REQ-072")
    r72["notes"] = str(r72.get("notes") or "") + " A note added after the approval (a test fixture)."
    open(reg2, "w", encoding="utf-8").write(yaml.safe_dump(req, allow_unicode=True, sort_keys=False))
    r = _run([GEN, "--registry", reg2, "--data", data2, "--out-dir", out, "--check"])
    assert r.returncode == 0, "a change to a cited record after the approval made the approved files out of date:\n%s" % r.stdout
    open(os.path.join(out, RI.DRAFT), "a", encoding="utf-8").write("\n")
    r = _run([GEN, "--registry", reg2, "--data", data2, "--out-dir", out, "--check"])
    assert r.returncode == 1, "an approved draft changed on disk still reads current:\n%s" % r.stdout


# ------------------------------------------------------------------------------------------------ the refusals
def t_l3r4_refuses_while_a_row_is_undecided():
    _mod()
    _tree_undecided()
    r = _run([GEN, "--out-dir", tempfile.mkdtemp(prefix="l3r4-out-")])
    assert r.returncode == 2 and "undecided" in r.stdout, "the tree's undecided rows were not refused:\n%s" % r.stdout
    d, reg = _chain(RECOMMENDED[:4])
    out, msg = _generate(reg, expect=2)
    assert "L3-OD3, L3-OD4 and L3-OD5 are undecided" in msg, "the refusal does not name the undecided rows: %s" % msg
    assert not os.listdir(out), "a refused run wrote a file"


def t_l3r4_refuses_only_a_contradictory_set():
    """D-26: rulings written into a decided copy. Row L3-OD2 standing with row L3-OD1 rejected sets requirements that
    cannot both hold, and the generator refuses it, naming why; a band-less adopt on 1S4P, which the scripts once refused,
    is a valid target and generates."""
    _mod()
    d, reg = _chain(RECOMMENDED)
    raw = open(reg, encoding="utf-8").read()
    a, b = 'decides: "L3-OD1:approve"', 'decides: "L3-OD1:reject"'
    assert raw.count(a) == 1, "the fixture does not carry %s once" % a
    bad = os.path.join(d, "contradictory.yaml")
    open(bad, "w", encoding="utf-8").write(raw.replace(a, b))
    out, msg = _generate(bad, expect=2)
    assert "cannot both hold" in msg and "row L3-OD2 answered" in msg, "the contradiction was not refused for its reason: %s" % msg
    assert not os.listdir(out), "a refused run wrote a file"
    d2, reg2 = _chain([s_ if s_[0] != "od_l3_3.py" else ("od_l3_3.py", "1s4p") for s_ in RECOMMENDED])
    _generate(reg2)


def t_l3r4_a_runtime_answer_other_than_72_hours_is_refused():
    """D-27: row L3-OD7's answers other than 72-required change M1's runtime or its store, whose passages are mapped with
    the runtime comparison's figures; a decided copy whose row L3-OD7 ruling is rewritten to 48 hours, with the rows
    prepared for 72 hours standing, is refused as requirements that cannot both hold, and nothing is written. The map
    names both answers as not mapped yet."""
    RI = _mod()
    d, reg = _chain(RECOMMENDED)
    raw = open(reg, encoding="utf-8").read()
    a = 'decides: "L3-OD7:72-required"'
    assert raw.count(a) == 1, "the fixture does not carry %s once" % a
    bad = os.path.join(d, "runtime48.yaml")
    open(bad, "w", encoding="utf-8").write(raw.replace(a, 'decides: "L3-OD7:48-required-72-desired"'))
    out, msg = _generate(bad, expect=2)
    assert "L3-OD7" in msg and "cannot both hold" in msg, "a 48 hour runtime beside rows prepared for 72 was not refused: %s" % msg
    assert not os.listdir(out), "a refused run wrote a file"
    m = open(os.path.join(os.path.dirname(GEN), "PASSAGE-MAP.md"), encoding="utf-8").read()
    for o in ("`48-required-72-desired`", "`72-required` with HF listening, an external store or the tablet charged"):
        assert "| L3-OD7 | %s | not mapped yet" % o in m, "the map does not name %s as not mapped" % o
    assert RI.RUNTIME_MAPPED == ("72-required",)


def t_l3r4_a_rejected_store_gives_its_own_reissue():
    """D-26: row L3-OD1 rejected is valid: the generator writes the re-issue with row L3-OD2 not applicable, D-06's one
    pack named as kept with its feasibility item FI-01, no two-pack passage restated and no one-pack circuit statement
    read as the design before a ruling that was not given."""
    RI = _mod()
    d, reg = _chain(REJECTED)
    out, msg = _generate(reg)
    draft, rec, rids = _common(reg, out, rows=[r for r in RI.ROWS if r != "L3-OD2"])
    c, applied, cur = _proposed(RI, reg)
    got = {p.pid for k in applied for p, o, n in applied[k][1]}
    assert {"C07", "C17", "C18", "B08", "B15"} <= got, "the reject variants are not restated: %s" % sorted(got)
    assert not (got & RI.APPROVE_ONLY), "a two-pack passage is restated on a reject: %s" % sorted(got & RI.APPROVE_ONLY)
    assert not [p for p in cur if p.group in ("PACK", "HF")], "a group that needs row L3-OD1 approved or row L3-OD2 fired"
    flat = _flat(draft)
    assert "| L3-OD2 | not applicable |" in draft and "feasibility item FI-01" in flat and "kept by owner ruling" in flat


def _docs_copy():
    """A temporary directory holding copies of the two baselined files at their paths: the link tests link these, never
    the tree's own files (CHECK-3 of round 4, minor 4)."""
    root = tempfile.mkdtemp(prefix="l3r4-docs-")
    for rel in BASE:
        os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
        shutil.copy(os.path.join(ROOT, rel), os.path.join(root, rel))
    return root


def t_l3r4_never_writes_a_baselined_file():
    """CHECK-1 of round 4, minor 3, and CHECK-2, minor 3: the guard compares real paths and the same file, and refuses
    a symbolic or hard link before anything is written; every link here points at a copy of the baselined files, which
    the generator reads as its baseline through --docs-root."""
    RI = _mod()
    root = _docs_copy()
    for rel in BASE:
        try:
            RI.guard_out([os.path.join(root, rel)], root)
        except RI.E.Refused:
            continue
        raise AssertionError("the generator would write into %s" % rel)
    src = open(GEN, encoding="utf-8").read()
    writes = re.findall(r"open\(([^,]+), \"w\"", src)
    assert sorted(writes) == ["MAP", "q"], "the generator opens another file for writing: %s" % writes
    d, reg = _chain(RECOMMENDED)
    brief = os.path.join(root, "v2", "docs", "PRODUCT-BRIEF.md")
    sha = lambda: RI.RL.sha16_bytes(open(brief, "rb").read())
    before = sha()
    out = tempfile.mkdtemp(prefix="l3r4-out-")
    os.symlink(brief, os.path.join(out, RI.DRAFT))
    o, msg = _generate(reg, expect=2, out=out, extra=["--docs-root", root])
    assert "link" in msg, "a draft path linked to the brief was not refused before writing: %s" % msg
    assert not os.path.exists(os.path.join(out, RI.RECORD)), "a refused run wrote the change record"
    assert sha() == before, "a refused run wrote into the copy of the brief"
    out2 = tempfile.mkdtemp(prefix="l3r4-out-")
    try:
        os.link(brief, os.path.join(out2, RI.DRAFT))
    except OSError as e:
        raise Skip("no hard link across these file systems (%s)" % e)
    o, msg = _generate(reg, expect=2, out=out2, extra=["--docs-root", root])
    assert "hard link" in msg, "a draft path hard linked to the brief was not refused before writing: %s" % msg
    assert sha() == before, "a refused run wrote into the copy of the brief"
    shutil.rmtree(root, ignore_errors=True)


# ------------------------------------------------------------------------------------------------ LAYER-STATUS
def t_l3r4_layer_status_row_brought_current_on_a_copy():
    need(LSTAT, "apply_layer_status_l3_r4.py is not in this tree")
    page = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
    t = open(page, encoding="utf-8").read()
    sys.path.insert(0, REC)
    import apply_layer_status_l3_r4 as A
    if A.MARK in t:
        assert A.OLD not in t and A.CHECKER not in t, "the page carries an old text beside the new one"
        r = _run([LSTAT, "--check"])
        assert r.returncode == 2 and "has run" in r.stdout, "a second run was not refused:\n%s" % r.stdout
        t = t.replace(t[t.index(A.MARK):t.index("\n", t.index(A.MARK))], A.OLD)
        t = t.replace(A.CHECKER_AT, A.CHECKER_AT + A.CHECKER, 1)
    cp = os.path.join(tempfile.mkdtemp(prefix="l3r4-ls-"), "LAYER-STATUS.md")
    open(cp, "w", encoding="utf-8").write(t)
    r = _run([LSTAT, "--page", cp])
    assert r.returncode == 0, "the row was not restated on a copy:\n%s" % r.stdout
    new = open(cp, encoding="utf-8").read()
    assert A.MARK in new and A.OLD not in new and "check-l3r2-5.md" in new
    assert A.CHECKER not in new and "A checker:" not in new, "the check still reads as a remaining item"
    back = new.replace(new[new.index(A.MARK):new.index("\n", new.index(A.MARK))], A.OLD)
    assert back.replace(A.CHECKER_AT, A.CHECKER_AT + A.CHECKER, 1) == t, "the page moved elsewhere"
    r = _run([LSTAT, "--page", cp])
    assert r.returncode == 2, "a second run on the copy was not refused"
