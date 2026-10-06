"""The set 30 blocks of the layer-status page (MESHSAT-1357), held as predicates on their text and on the files they cite:
v2/docs/handover/LAYER-STATUS.md, the head paragraph "After set 30" and the "After set 30" blocks of Layers 4, 8, 9 and 12.

The blocks were folded from the set 30 draft (branch fnd/lstat30, 4d84794a; its own test test_lstat30 held the draft). They
state what the P0 power candidate's records say at the candidate branch's commit 7070f106 (the L4-E9 change-list rows R-220
to R-245 applied to its change list, the remaining-engineering ledger merged), and the head paragraph names that commit as the
citations' base. So this module reads every cited file AT THAT COMMIT (git show), never the working tree: a later edit of a
cited record, or of this page itself, leaves the blocks' citations true of the revision they name. The commit is in this
branch's history (its integration commit 2a, bbba3e53, is its child).

The predicates: the head paragraph follows set 29's, names the base, what set 30 carries and that its promotion is a DESK
candidate, not design acceptance; each of the four layer blocks sits between its layer's heading and its "After set 29"
block, and no other layer carries one; every citation lies inside its file at the base and every path named exists; every
quotation of ten characters or more is found in a file the blocks cite; the decisive lines carry their anchors and the blocks
cite each of them; the three check verdicts are the filed JSON's own and cx46's item counts agree with it; the DESK-gate
verdict is the literal placeholder, once on the page, and the completion claims read as briefed; each block opens with its
state and carries its rows, and no row's state is raised to MET; the change list's rows R-220 to R-245 are DRAFTED and not
applied with no R-241 and FAN_OK's rows withdrawn, and board P's DD-5 draft has no row; the contract rows FW-B20 to FW-B22 are
not in HW-FW-CONTRACT.md and the PA cap's build check not in PCB-BRING-UP.md; record l8p's checks V1 and V2 are not filed; the
eighteen stability digests equal their files at the base; no generator and no CURRENT-EVIDENCE.md differ between set 29 and
the base; nothing outside a quotation reads as an acceptance; no em or en dash. These are software predicates on record
text: they establish no electrical or thermal property and close nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_lstat31.`) and under pytest (each t_ function has a
test_ alias). Without git, or without the base commit in the object store, the rules that read the base skip with their
reason."""
import hashlib
import json
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
PAGE = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
BASE = "7070f1060a69735632338d39d744d3340ce75568"
SET29 = "aa76c89448ec943e3a37357ebc11ce3322fa4020"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

CITE = re.compile(r"`((?:records|v2)/[^`\s:]+):(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)`")
PATH = re.compile(r"`((?:records|v2)/[^`\s:]+)`")
DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
PLACEHOLDER = "[COORDINATOR: the DESK-gate assessment]"
HEAD = "**After set 30 (6 October 2026, the P0 power candidate's integration, MESHSAT-1357).**"
HEAD29 = "**After set 29 (4 October 2026, integration sets 28 and 29, MESHSAT-1357).**"
CLAIMS = ("- documents and editable artifacts: on main as a DESK candidate",
          "- design reviewed and accepted: NO",
          "- implemented: NONE",
          "- qualified: NONE",
          "- fabrication release: BLOCKED",
          "- power-design closure: BLOCKED")
CX44 = "records/l4close/CHECK-CX44-F01-SELECTION-8c7c335f-AS-RECEIVED.md"
CX45 = "records/l4close/CHECK-CX45-P0-CANDIDATE-06077cee-AS-RECEIVED.md"
CX46 = "records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md"
V6 = "records/l4close/CHECK-V6-POWER-DRAFTS-7a82e82a-AS-RECEIVED.md"
L4P = "records/l4e9/L4-POWER-ARCHITECTURE.md"
REM = "records/l4close/REMAINING-ENGINEERING.md"
CON = "records/l9t5/l9t5_connected.out"
T10 = "records/l9t5/l9t5_t10.out"
ANX = "records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md"
P0L = "records/l4close/P0-POWER-LIST.md"
HWFW = "records/l9t5/apply_hw_fw_contract_t10.py"
DIG = "records/l9t5/stability/DIGESTS-cr3.txt"
OI05 = "v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md"
VERDICTS = {CX44: "F01 SELECTION: NOT SUPPORTED", CX45: "P0 CANDIDATE: NOT CONFIRMED",
            CX46: "P0 RECHECK: CORRECTIONS NOT CLOSED"}
# (cited file, line at the base, what that line must carry): the lines the blocks' states rest on
ANCHORS = [
    # the head paragraph
    ("records/l9t5/README.md", 1, "the claim-and-handover disposition after cx46"),
    ("v2/docs/EXECUTION-CONSTITUTION.md", 23, "A promoted integration set is none of those by itself."),
    (OI05, 788, "It must not claim technical closure of open defects."),
    (OI05, 81, "P0 power closure"),
    (REM, 11, "It is not an acceptance, a closure, a verdict, a check, a qualification or a release of anything."),
    # the layer blocks
    (CX46, 3, "the second negative on the method, which ends it"),
    (CX46, 10, "P0 RECHECK: CORRECTIONS NOT CLOSED."),
    (CX46, 183, "retain or reproduce successful byte-identical repeated output runs on these inputs"),
    (CX46, 188, "D-10 itself remains OPEN REMAINING ENGINEERING"),
    (CX45, 10, "P0 CANDIDATE: NOT CONFIRMED."),
    (CX45, 10, "P0-4: CONFIRMED AS CONDITIONAL"),
    (CX44, 10, "F01 SELECTION: NOT SUPPORTED"),
    (V6, 20, "**CONFIRMED AS CONDITIONAL**"), (V6, 21, "**CONFIRMED AS CONDITIONAL**"),
    (V6, 22, "**CONFIRMED AS CONDITIONAL"), (V6, 23, "**CONFIRMED AS CONDITIONAL**"),
    (V6, 24, "**CONFIRMED AS CONDITIONAL.**"), (V6, 25, "**CONFIRMED AS CONDITIONAL**"),
    (V6, 22, "but NOT on T10-A1 alone; the deficit is NOT corrected on the candidate"),
    (P0L, 31, "V6 (every item CONFIRMED AS CONDITIONAL; B1, B2, B3 blocking)"),
    (L4P, 401, "**None is APPLIED:**"),
    (L4P, 422, "Rows R-220 to R-245"),
    (L4P, 456, "WITHDRAWN (FAN_OK rejected; never applied)"),
    (L4P, 460, "L8P-D9 withdrawn"),
    (L4P, 465, "R98 at 511 R"),
    (L4P, 466, "replaces the withdrawn FAN_OK rows R-210 to R-212 as D-17's correction"),
    (L4P, 488, "D-16 corrected in draft"),
    (L4P, 492, "WITHDRAWN (FAN_OK rejected; never applied)"),
    (L4P, 505, "WITHDRAWN (FAN_OK rejected; never applied)"),
    (L4P, 972, "**Layer 4's power architecture closes: NO**"),
    (L4P, 972, "the power-design closure gate is BLOCKED"),
    (L4P, 974, "fabrication release BLOCKED"),
    (L4P, 978, "criteria 1 and 5 cannot read PASS while U-01, U-02 and U-04"),
    (REM, 14, "Power-design closure and fabrication release stay BLOCKED"),
    (REM, 15, "nothing in the kit has been built, bought, powered or measured"),
    (REM, 585, "Counts: remaining engineering 19; qualification 1; external architecture fact 3; closed 4; conditional 2."),
    (CON, 64, "board A: 26 drafts"), (CON, 67, "board B: 18 drafts"), (CON, 70, "board D: 4 drafts"),
    (CON, 73, "board E: 16 drafts"),
    (CON, 123, "15.1308 V (MODEL on PRINTED"),
    (CON, 124, "margin 0.3692 V; F01 / D-17 PROVISIONAL"),
    (CON, 174, "V6-B1: OPEN, REMAINING ENGINEERING for the receiving company"),
    (CON, 205, "D-16 CORRECTED in draft"),
    (CON, 215, "the acceptance reads REMAINING ENGINEERING while the sustained peaks and the latent rail trip are open"),
    (CON, 336, "THE CONNECTED ELECTRICAL VERDICT: REMAINING ENGINEERING."),
    (CON, 355, "check_l8p_netlist.py's round 8 reader does not admit the delta"),
    (CON, 365, "no R-241"),
    (CON, 373, "every record check reads DRAWN on the composed candidate"),
    (CON, 374, "every mutation fails its check"),
    (CON, 380, "U7 with I-03 carries C-DEV rev 2 (the active row) under its loop"),
    ("records/l9t5/README.md", 1, "Power-design closure and fabrication release stay BLOCKED."),
    ("records/l9t5/l9t5_case.out", 40, "need 15.5162 V rest at 18 A"),
    ("records/l9t5/l9t5_case.out", 82, "needs 16.0718 V"),
    ("records/l9t5/l9t5_f01.out", 212, "F01 / D-17 and every dependant"),
    ("records/l9t5/l9t5_f01.out", 240, "U5 (R-214, the rest voltage's fall in the 60 s) MISSING"),
    (T10, 584, "is WITHDRAWN (cx46 6)"),
    (T10, 585, "after 0.98 s (MODEL, the comparator's delay not counted)"),
    (T10, 620, "the universal sustained bound and its positive margin are WITHDRAWN"),
    (T10, 663, "CON-004's quorum service (OPEN), FW-B22 (PROVISIONAL), L9T5-F21 (OPEN)"),
    (T10, 670, "L9T5-F06 STAYS OPEN"),
    ("records/l9t5/T10-ROUND5.md", 226, "a drafted direction, not a closure"),
    ("records/l8p/L8P-BREAKER.md", 1398, "V6-m7 OPEN and NOT CLOSED"),
    ("records/l8p/L8P-BREAKER.md", 1399, "C-PROT rev 1 for the guard PROVISIONAL; L8P-R9-F1, F2 and F3 OPEN"),
    ("records/l8p/README.md", 159, "apply_gen_sch_p_idealdiode.py"),
    ("records/l8p/L8P-BREAKER.md", 774, "B-R2's route R1 DRAFTED on board P"),
    ("records/l8p/L8P-BREAKER.md", 778, "B-R2: CONFIRMED AS CONDITIONAL"),
    ("records/l8p/L8P-BREAKER.md", 779, "the ideal diode CONFIRMED AS CONDITIONAL"),
    ("records/l4e11/README.md", 11, "the loop ENDS"),
    ("records/l4e11/l4e11_power.out", 2066, "PROVISIONAL, not closed"),
    ("records/efuse/efuse_check.out", 615, "EF-F03 DESIGN DEFECT, OPEN"),
    ("records/efuse/EFUSE-SETTINGS.md", 165, "apply_assembly_rb_pads.py` (unapplied"),
    ("records/l4e7/L4E7-P0SOL.md", 101, "D-10 is an UNRESOLVED PROTECTION DEFECT in the present model"),
    ("records/l4e7/B2-PRESENCE.md", 4, "UNSELECTED and WITHDRAWN AS DRAFTED"),
    ("records/l4e7/B2-PRESENCE.md", 27, "no owner action rests on B2; the approved interface stands"),
    (P0L, 26, "| 3 ARCH |"), (P0L, 27, "| 3 ARCH |"), (P0L, 28, "| 3 ARCH |"),
    (P0L, 29, "| 3 (qualification, not ARCH) |"),
    (ANX, 96, "the handover carries the Saft option as a PROPOSAL with its evidence state"),
    (ANX, 101, "a QUALIFICATION, kept apart from the architecture blockers"),
    (ANX, 103, "NOT EXECUTABLE until L4-E9 restates R-159"),
    ("records/l4e9/DOWNSTREAM-REGISTER.md", 253, "45.88 K/W"),
    (HWFW, 3, "UNAPPLIED: the integrator runs it"),
    (HWFW, 11, "FW-B22 PROVISIONAL (a traffic model; L9T5-F21 OPEN); V-B23's 0.2 s withdrawn"),
    (HWFW, 80, "a traffic MODEL"),
    ("v2/docs/test-procedures/TP-E11-29.md", 19, "**NOT EXECUTABLE.**"),
    ("v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md", 45, "Report these separately"),
    ("v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md", 47, "Layer documents and editable artifacts complete."),
    ("v2/docs/handover/OWNER-INSTRUCTION-2026-10-02.md", 51, "Fabrication release approved."),
    ("v2/docs/EXECUTION-CONSTITUTION.md", 23, "power-design closure and fabrication release separately"),
    (OI05, 169, "Layer 4 is the active layer."),
    ("v2/docs/handover/LAYER-STATUS.md", 96, "0 boards ready for layout, 40 reasons"),
    ("v2/docs/handover/LAYER-STATUS.md", 530, "0 of 7; 40 reasons"),
    ("v2/docs/handover/LAYER-STATUS.md", 549, "| 12.5 |"),
    ("v2/docs/handover/LAYER-STATUS.md", 470, "8.1 and 8.9 stay MET for the committed generators"),
    (P0L, 25, "| 2 | unchanged |"),
    (DIG, 1, "pass 1 ended 22:36, pass 2 22:45"),
    ("records/l9t5/stability/RUN-cr3-pass1.log", 20, "exit 0"),
    ("records/l9t5/stability/RUN-cr3-pass2.log", 20, "exit 0"),
]
LAYERS = {"4": "## Layer 4. System architecture\n", "8": "## Layer 8. Schematics\n",
          "9": "## Layer 9. Pre-layout design analysis\n",
          "12": "## Layer 12. Firmware, bring-up, test plans and build documentation\n"}
OTHERS = ("## Layer 1.", "## Layer 2.", "## Layer 3.", "## Layer 5.", "## Layer 6.", "## Layer 7.")
ROWS = {"4": ["4.7", "4.8", "4.9", "4.10", "4.11", "4.12"] + ["4.13 to 4.18 (%s)" % c for c in "abcdef"],
        "8": ["8.10"], "9": ["9.1", "9.3", "9.4", "9.6", "9.20"], "12": ["12.1", "12.2", "12.3", "12.4", "12.5"]}
STATES = ("**OPEN**", "**OPEN** (EXTERNAL)", "PARTLY", "NOT MOVED")
_C = {}


def _norm(t):
    return " ".join(t.split())


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    if r.returncode != 0:
        raise Skip("git %s: %s" % (a[0], r.stderr.decode(errors="replace")[:100].strip()))
    return r.stdout.decode("utf-8")


def _base_ok():
    if "base" not in _C:
        _git("cat-file", "-e", BASE + "^{commit}")
        _C["base"] = True


def _repo(p):
    return "v2/docs/" + p if p.startswith("records/") else p


def _blob(p):
    """The bytes of a cited file at the base, or None when the base has no such file."""
    _base_ok()
    k = ("b", p)
    if k not in _C:
        r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, _repo(p))], capture_output=True)
        _C[k] = r.stdout if r.returncode == 0 else None
    return _C[k]


def _text(p):
    b = _blob(p)
    return None if b is None else b.decode("utf-8")


def _lines(p):
    t = _text(p)
    return None if t is None else t.splitlines()


def _page():
    if "p" not in _C:
        _C["p"] = open(need(PAGE, "the layer-status page"), encoding="utf-8").read()
    return _C["p"]


def _head():
    """The head paragraph "After set 30" (one line on the page)."""
    t = _page()
    assert t.count(HEAD) == 1, "the head paragraph After set 30 is missing or doubled"
    i = t.index(HEAD)
    return t[i:t.index("\n", i)]


def _section(n):
    """Layer n's section, from its heading to the next rule or heading of level 2."""
    t = _page()
    i = t.index(LAYERS[n])
    j = min(x for x in (t.find("\n---\n", i), t.find("\n## ", i + 1), len(t)) if x >= 0)
    return t[i:j]


def _block(n):
    """Layer n's After set 30 block: from its paragraph to its layer's After set 29 block."""
    s = _section(n)
    i = s.index("\n**After set 30 (6 October 2026): IN_PROGRESS") + 1
    j = s.index("\n**After set 29 (4 October 2026): IN_PROGRESS", i) + 1
    return s[i:j]


def _set30():
    """Every text of set 30 on the page: the head paragraph and the four layer blocks."""
    if "s" not in _C:
        _C["s"] = "\n\n".join([_head()] + [_block(n) for n in LAYERS])
    return _C["s"]


def _ranges(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out.append((int(a), int(b) if b else int(a)))
    return out


def _cites():
    """path -> list of (first, last) line ranges the set 30 text cites."""
    out = {}
    for m in CITE.finditer(_set30()):
        out.setdefault(m.group(1), []).extend(_ranges(m.group(2)))
    return out


def _json(p):
    t = _text(p)
    return json.loads(t.split("```json", 1)[1].split("```", 1)[0])


def _quotes(t):
    pos = [i for i, c in enumerate(t) if c == '"']
    assert len(pos) % 2 == 0, "an unpaired quotation mark"
    return pos


def _unquoted():
    t = _set30()
    pos = _quotes(t)
    out, k = [], 0
    for i, j in zip(pos[0::2], pos[1::2]):
        out.append(t[k:i]); k = j + 1
    out.append(t[k:])
    return _norm(" ".join(out))


def t_the_head_paragraph_follows_set_29s_and_names_what_set_30_carries():
    t = _page()
    h = _head()
    i29, i30 = t.index(HEAD29), t.index(HEAD)
    assert i29 < i30 < t.index("**How to read this page after H2.**"), "the head paragraph is out of its place"
    assert t[i29:i30].count("\n\n") == 1, "something sits between set 29's head paragraph and set 30's"
    for w in ("R-220 to R-245", "disposition after cx46", "the remaining-engineering ledger", "V6, cx44, cx45 and cx46",
              "is a DESK candidate, not design acceptance", "No item is raised to MET by set 30",
              "nothing has been built, bought or measured", "`7070f106`", "(`%s`)" % BASE,
              "this page's own lines as they stood there, before this fold", "v2/ecad/tools/tests/test_lstat31.py"):
        assert w in h, "the head paragraph lacks: %s" % w


def t_each_block_sits_between_its_heading_and_its_set_29_block_and_no_other_layer_has_one():
    t = _page()
    assert t.count("**After set 30 (6 October 2026") == 1 + len(LAYERS), "the page carries set 30 blocks it should not"
    for n in LAYERS:
        s = _section(n)
        assert s.count("**After set 30 (6 October 2026): IN_PROGRESS") == 1, "layer %s: no single set 30 block" % n
        assert s.count("**After set 29 (4 October 2026): IN_PROGRESS") == 1, "layer %s: no single set 29 block" % n
        assert s.split("**After set 30", 1)[0] == LAYERS[n] + "\n", "layer %s: text between the heading and set 30" % n
    for h in OTHERS:
        i = t.index("\n" + h) + 1
        j = t.find("\n---\n", i)
        assert "After set 30" not in t[i:j], "%s carries a set 30 block" % h


def t_every_citation_lies_inside_its_file_at_the_base():
    cites = _cites(); bad = []; n = 0
    for p, rs in cites.items():
        ls = _lines(p)
        if ls is None:
            bad.append("%s: no such file at the base" % p); continue
        for a, b in rs:
            n += 1
            if not (1 <= a <= b <= len(ls)):
                bad.append("%s:%d-%d outside 1..%d" % (p, a, b, len(ls)))
    assert n >= 150, "the set 30 text cites less than it did: %d citations" % n
    assert not bad, "; ".join(bad[:8])


def t_every_path_named_exists():
    paths = set(PATH.findall(_set30())) | set(_cites())
    bad = []
    for p in sorted(paths):
        rp = _repo(p)
        if p.endswith("/"):
            ok = os.path.isdir(os.path.join(ROOT, rp))
        else:
            ok = _blob(p) is not None or os.path.isfile(os.path.join(ROOT, rp))
        if not ok: bad.append(p)
    assert len(paths) >= 30, "the set 30 text names fewer paths than it did: %d" % len(paths)
    assert not bad, "paths naming nothing at the base or in the tree: %s" % bad


def t_every_quotation_is_found_in_a_cited_file():
    t = _set30()
    files = set(_cites()) | {p for p in PATH.findall(t) if not p.endswith("/")}
    corpus = [_norm(x) for x in (_text(p) for p in files) if x is not None]
    pos = _quotes(t)
    bad = []; n = 0
    for i, j in zip(pos[0::2], pos[1::2]):
        q = _norm(t[i + 1:j])
        if len(q) < 10: continue
        n += 1
        if not any(q in c for c in corpus): bad.append(q[:80])
    assert n >= 50, "fewer quotations than written: %d" % n
    assert not bad, "quotations found in no cited file: %s" % bad[:5]


def t_the_decisive_lines_carry_their_anchors_and_are_cited():
    cites = _cites(); bad = []
    for p, ln, s in ANCHORS:
        ls = _lines(p)
        if ls is None or ln > len(ls):
            bad.append("%s:%d missing at the base" % (p, ln)); continue
        if _norm(s) not in _norm(ls[ln - 1]):
            bad.append("%s:%d lacks %r" % (p, ln, s[:50])); continue
        if not any(a <= ln <= b for a, b in cites.get(p, [])):
            bad.append("%s:%d is not cited by the set 30 text" % (p, ln))
    assert not bad, "; ".join(bad[:8])


def t_the_verdicts_are_the_filed_ones_and_cx46_counts_agree():
    d = _norm(_set30())
    for p, v in VERDICTS.items():
        assert _json(p)["summary"].startswith(v), "%s's filed summary does not open with %s" % (p, v)
        assert '"%s"' % v in d, "the page does not quote %s as filed" % v
    st = {}
    for c in _json(CX46)["classification"]:
        st[int(c["item"].split(".", 1)[0])] = c["item"].rsplit(": ", 1)[1]
    assert len(st) == 18
    assert {n for n, s in st.items() if s == "NOT CLOSED"} == {1, 2, 4, 5, 6, 7, 8, 9, 10, 13, 17, 18}
    assert {n for n, s in st.items() if s == "CLOSED BY THE CORRECTION"} == {3, 11, 12, 15}
    assert {n for n, s in st.items() if s == "CLOSED AS CONDITIONAL"} == {14, 16}
    for w in ("twelve NOT CLOSED", "four CLOSED BY THE CORRECTION (3, 11, 12, 15)", "two CLOSED AS CONDITIONAL (14, 16)"):
        assert w in d, "the page's cx46 counts lack: %s" % w
    assert _json(CX46)["owner_decision_required"] is False


def t_the_desk_gate_is_the_placeholder_and_the_claims_read_as_briefed():
    """The placeholder is the coordinator's to replace at adoption; until then it stands once, literally, in Layer 4's
    block. After adoption this rule names the replacement as the reason it fails, so the coordinator restates it."""
    assert _page().count(PLACEHOLDER) == 1, "the DESK-gate placeholder must appear once, literally (replaced at adoption?)"
    l4 = _block("4")
    assert "**The Layer 4 DESK gate:** " + PLACEHOLDER in l4
    lines = [x for x in l4.splitlines() if x.startswith("- ")]
    for c in CLAIMS:
        assert sum(1 for x in lines if x.startswith(c)) == 1, "the claim line is missing or doubled: %s" % c
    assert "unchanged, 0 of 7 boards ready for layout, 40 reasons" in l4


def t_each_layer_block_opens_with_its_state_and_carries_its_rows():
    for layer, items in ROWS.items():
        s = _block(layer)
        assert s.startswith("**After set 30 (6 October 2026): IN_PROGRESS"), "layer %s's paragraph" % layer
        rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in s.splitlines()
                if r.startswith("| ") and not r.startswith("| Item ")]
        ids = [r[0] for r in rows]
        assert ids == items, "layer %s rows %s" % (layer, ids)
        for r in rows:
            assert len(r) == 4 and all(r), "layer %s row %s has an empty cell" % (layer, r[0])
            assert r[2] in STATES, "row %s reads %r: no state is raised here" % (r[0], r[2])
            assert CITE.search(r[3]), "row %s cites no line" % r[0]


def t_the_change_list_rows_are_drafted_and_not_applied():
    rows = {}
    for ln in _lines(L4P):
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) == 9 and re.match(r"^R-\d+$", c[2]):
            rows.setdefault(c[2], []).append(c[8])
    want = ["R-%d" % n for n in range(220, 246) if n != 241]
    for r in want:
        assert rows.get(r) == ["DRAFTED (not applied)"], "%s reads %s" % (r, rows.get(r))
    assert "R-241" not in rows, "R-241 is in the list"
    for r in ("R-210", "R-211", "R-212"):
        assert rows.get(r) == ["WITHDRAWN (FAN_OK rejected; never applied)"], "%s reads %s" % (r, rows.get(r))
    assert "apply_gen_sch_p_idealdiode.py" not in _text(L4P), "board P's DD-5 draft has a row at the base"
    assert _blob("records/l8p/apply_gen_sch_p_idealdiode.py") is not None


def t_the_contract_rows_are_not_applied_and_the_build_check_not_written():
    hw = _text("v2/docs/HW-FW-CONTRACT.md")
    assert hw is not None
    for r in ("FW-B20", "FW-B21", "FW-B22", "V-B23"):
        assert r not in hw, "%s is in HW-FW-CONTRACT.md at the base" % r
        assert r in _text(HWFW)
    bu = _text("v2/docs/PCB-BRING-UP.md")
    assert bu is not None and "6.3518" not in bu and "6.9259" not in bu, "the PA cap's build check is in PCB-BRING-UP.md"


def t_record_l8ps_checks_are_not_filed():
    """Layer 4's row (c) says of record l8p's checks V1 and V2 that neither is filed in the tree; hold that at the base."""
    names = _git("ls-tree", "-r", "--name-only", BASE, "--", "v2/docs").splitlines()
    hits = [x for x in names if re.search(r"(?i)check[-_]?v[12]\b|\bv[12]-as-received", os.path.basename(x))]
    assert not re.search(r"(?i)check[-_]?v[12]\b|\bv[12]-as-received", "REVIEW-SUPPLIER-ADDENDUM-REV2-AS-RECEIVED.md")
    assert re.search(r"(?i)check[-_]?v[12]\b|\bv[12]-as-received", "CHECK-V1-AS-RECEIVED.md"), "the pattern finds nothing"
    assert not hits, "a check the page calls unfiled is in the tree: %s" % hits
    filed = [x for x in names if x.startswith("v2/docs/records/l4close/CHECK-")]
    assert len(filed) == 4, "the filed checks under records/l4close are %s" % filed


def t_the_stability_digests_equal_their_files_at_the_base():
    rx = re.compile(r"^(v2/\S+) pass 1: sha256=([0-9a-f]{64}); pass 2: sha256=([0-9a-f]{64}); equal$")
    rows = [m.groups() for m in (rx.match(x) for x in _lines(DIG)) if m]
    assert len(rows) == 18, "DIGESTS-cr3 carries %d outputs, not eighteen" % len(rows)
    bad = []
    for p, h1, h2 in rows:
        b = _blob(p[len("v2/docs/"):] if p.startswith("v2/docs/records/") else p)
        if h1 != h2 or b is None or hashlib.sha256(b).hexdigest() != h1: bad.append(p)
    assert not bad, "outputs differing from DIGESTS-cr3 at the base: %s" % bad
    for log in ("records/l9t5/stability/RUN-cr3-pass1.log", "records/l9t5/stability/RUN-cr3-pass2.log"):
        assert _lines(log)[-1].strip() == "exit 0", "%s does not end in exit 0" % log


def t_no_generator_and_no_current_evidence_changed_since_set_29():
    names = _git("diff", "--name-only", SET29, BASE, "--", "v2/ecad/tools/gen_*", "v2/docs/CURRENT-EVIDENCE.md").split()
    assert not names, "changed between set 29 and the base: %s" % names
    t = _set30()
    assert "no generator file differs" in t and "does not change `v2/docs/CURRENT-EVIDENCE.md`" in t


def t_nothing_outside_a_quotation_reads_as_an_acceptance():
    u = _unquoted()
    for w in ("ACCEPTED", "ACCEPTS", "PASSES", "QUALIFIED:", "RELEASED"):
        assert w not in u, "the set 30 text says %s outside a quotation" % w
    rest = re.sub(r"NOT CLOSED|CLOSED BY THE CORRECTION|CLOSED AS CONDITIONAL", "", u)
    assert "CLOSED" not in rest, "a CLOSED outside the filed verdict words"
    assert not re.search(r"\|\s*MET\s*\|", u), "a row reads MET"


def t_no_em_or_en_dash():
    s = _set30()
    assert not any(d in s for d in DASHES), "a dash in the set 30 text"
    s = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in s for d in DASHES), "a dash in this module"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
