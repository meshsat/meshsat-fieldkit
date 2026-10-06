"""W21's dated notes in the set 30 blocks of the layer-status page (MESHSAT-1357), held as predicates on their text and on the
commits they cite: v2/docs/handover/LAYER-STATUS.md, the paragraph "After set 30, at the integration's tip" under the set 30 head
paragraph and the notes added to the "After set 30" blocks of Layers 4, 8, 9 and 12.

Slot I's fold (branch fnd/lstat31, 87c5fb08, held by test_lstat31 at 7070f106) is kept as written; W21 (branch fnd/lstat32)
adds, beside it, what the integration's committed tip c4492dd3 and the drafts of W10, W12, W15, W16 (through W18) and W18 say. Its
citations read `<commit>:<path>:<line>` at the commit they name, a code span right after one being the words quoted from that line,
so this module reads every cited file AT ITS COMMIT (git show), never a working tree.

The predicates: Slot I's lines of the head paragraph and of the four blocks are all still on the page, in order, each block
inside its own; every dated citation names a commit in the object store, a file at that commit and lines inside it, and each quote
right after one is found in those lines; every sha the notes name is a commit; the branch containments the notes state hold, the
eight next-set tips are not in the integration's tip, the integration's tip carries the chain the notes name, and fnd/lstat31's tip
is this branch's base; the placeholders __CANDIDATE__ and __PROMOTED__ stand once each in Layer 4's chain and the DESK-gate cell
keeps its placeholder; the three completion claims each stand once with their own state word, W18's table gives the same, and no
percentage is written; the counts the notes copy are their sources' (W15's 38 commits and 13 REVIEWED-INPUT CHANGED rows with the
six that do not only narrow, W12's K table 19 standing, 13 restated only on next-set branches, 6 unrestated and 9 not standing,
the ledger's twelve RE items of cx46 and its counts line at the tip against Slot I's at 7070f106, D-10 as E-1 and D-17 as RE-2, the
connected output's 118 changes against 117, 17 of the eighteen DIGESTS-cr3 outputs differing at the tip with l9t5_f01_drafts.out
alone equal, no generator, CURRENT-EVIDENCE.md or HW-FW-CONTRACT.md changed since set 29 and no contract row FW-B20 to FW-B22 in
it); the next set's merge order is W18's and, where the run folder exists, W10's plan's; and the added text carries no em or en
dash, no straight double quote and no acceptance word. These are software predicates on record text: they establish no electrical
or thermal property and close nothing.

Runs under the suite's runner (`python3 v2/ecad/tools/tests/run.py test_lstat32.`) and under pytest (each t_ function has a test_
alias). Without git, or without a cited commit in the object store (the worker branches live in the runner's worktrees), the
rules that read it skip with their reason; the run folder's plan is read only where it exists."""
import hashlib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
PAGE = os.path.join(ROOT, "v2", "docs", "handover", "LAYER-STATUS.md")
REL = "v2/docs/handover/LAYER-STATUS.md"
SLOTI = "87c5fb08d85cd48afc583fd96c8ebc592a83f58a"   # fnd/lstat31, Slot I's fold and this branch's base
SLOTI_BASE = "7070f1060a69735632338d39d744d3340ce75568"
TIP = "c4492dd370c592e9899a8e526113958f4dc20554"     # fnd/p0pwr when W21 folded
SET29 = "aa76c89448ec943e3a37357ebc11ce3322fa4020"
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip, need  # noqa: E402

DASHES = (chr(0x2013), chr(0x2014))  # the en dash and the em dash, by code point
HEAD = "**After set 30 (6 October 2026, the P0 power candidate's integration, MESHSAT-1357).**"
W21HEAD = "**After set 30, at the integration's tip (dated 6 October 2026, folded by W21"
DESK = "[COORDINATOR: the DESK-gate assessment]"
LAYERS = {"4": "## Layer 4. System architecture\n", "8": "## Layer 8. Schematics\n",
          "9": "## Layer 9. Pre-layout design analysis\n",
          "12": "## Layer 12. Firmware, bring-up, test plans and build documentation\n"}
DCITE = re.compile(r"`([0-9a-f]{7,40}):([^`\s:]+):(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*)`(?:\s+`([^`]+)`)?")
SHA = re.compile(r"`([0-9a-f]{7,40})`")
WORK = re.compile(r"`<worktrees>/([^`\s:]+)(?::(\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*))?`")
CL = "57bcdbfc"
R3 = "b8912eef"
DG = "150e908b"
REM = "v2/docs/records/l4close/REMAINING-ENGINEERING.md"
CON = "v2/docs/records/l9t5/l9t5_connected.out"
DIG = "v2/docs/records/l9t5/stability/DIGESTS-cr3.txt"
SIX = ["7070f106", "bbba3e53", "14082416", "17ce29d5", "53a68c7c", "3088ee79"]
ORDER = [("fnd/w4l4e7", "786aed2f"), ("fnd/w5l8p", "cd19df59"), ("fnd/w14l5", "910f08ef"), ("fnd/w11l9t5", "85b6f258"),
         ("fnd/w13l4e9", "56ab0d01"), ("fnd/w15class", "57bcdbfc"), ("fnd/dgate2", "150e908b"), ("fnd/w3annex", "686de0a2")]
CONTAINS = [("1ab30f35", "910f08ef"), ("02b0d30d", "85b6f258"), ("3e566c55", "56ab0d01")]
CHAIN = ["4d0ff8a2", "3d2746c9", "7070f106", "bbba3e53", "d83d9f2d", "33efca07", "2d4f6df5", "6ab17e21", "3c118b43",
         "99bbc0c6", "5c414310", "2f74beb5", "2ccf0f20", "3088ee79", "14082416", "53a68c7c"]
CLAIMS = (("- engineering-handover readiness: NOT YET ASSESSED", "NOT YET ASSESSED"),
          ("- power-design closure at the integration's tip: BLOCKED", "BLOCKED"),
          ("- fabrication release at the integration's tip: BLOCKED", "BLOCKED"))
STATE_WORDS = ("NOT YET ASSESSED", "BLOCKED", "OPEN", "PASS", "FAIL", "CONDITIONAL", "MET")
_C = {}


def _norm(t):
    return " ".join(t.split())


def _git(*a):
    try:
        r = subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True)
    except OSError as e:
        raise Skip("no git on this host (%s)" % e)
    return r


def _have(sha):
    k = ("c", sha)
    if k not in _C:
        _C[k] = _git("cat-file", "-e", sha + "^{commit}").returncode == 0
    return _C[k]


def _need(*shas):
    for s in shas:
        if not _have(s):
            raise Skip("commit %s is not in this object store" % s)


def _show(sha, path):
    """The text of path at sha, or None when the commit has no such file."""
    _need(sha)
    k = ("f", sha, path)
    if k not in _C:
        r = _git("show", "%s:%s" % (sha, path))
        _C[k] = r.stdout.decode("utf-8") if r.returncode == 0 else None
    return _C[k]


def _anc(a, b):
    _need(a, b)
    return _git("merge-base", "--is-ancestor", a, b).returncode == 0


def _page():
    if "p" not in _C:
        _C["p"] = open(need(PAGE, "the layer-status page"), encoding="utf-8").read()
    return _C["p"]


def _section(t, n):
    i = t.index(LAYERS[n])
    j = min(x for x in (t.find("\n---\n", i), t.find("\n## ", i + 1), len(t)) if x >= 0)
    return t[i:j]


def _block(t, n):
    s = _section(t, n)
    i = s.index("\n**After set 30 (6 October 2026): IN_PROGRESS") + 1
    j = s.index("\n**After set 29 (4 October 2026): IN_PROGRESS", i) + 1
    return s[i:j]


def _head(t):
    i = t.index(HEAD)
    return t[i:t.index("\n", i)]


def _w21head(t):
    assert t.count(W21HEAD) == 1, "W21's head paragraph is missing or doubled"
    i = t.index(W21HEAD)
    return t[i:t.index("\n\n", i)]


def _slot_i():
    t = _show(SLOTI, REL)
    assert t is not None, "the page at Slot I's tip"
    return t


def _notes():
    """W21's text: its head paragraph and every line of the four blocks that Slot I's blocks do not carry."""
    if "n" not in _C:
        t, old = _page(), _slot_i()
        parts = [_w21head(t)]
        for n in LAYERS:
            keep = set(_block(old, n).splitlines())
            parts.append("\n".join(x for x in _block(t, n).splitlines() if x not in keep))
        _C["n"] = "\n".join(parts)
    return _C["n"]


def _ranges(spec):
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out.append((int(a), int(b) if b else int(a)))
    return out


def t_slot_is_lines_are_kept_in_order_inside_their_blocks():
    t, old = _page(), _slot_i()
    assert _head(t) == _head(old), "Slot I's head paragraph changed"
    h, w, r = t.index(HEAD), t.index(W21HEAD), t.index("**How to read this page after H2.**")
    assert h < w < r, "W21's head paragraph is not between the set 30 head and the reading guide"
    for n in LAYERS:
        cur = _block(t, n).splitlines()
        k = 0
        for line in _block(old, n).splitlines():
            while k < len(cur) and cur[k] != line:
                k += 1
            assert k < len(cur), "layer %s: Slot I's line is gone or out of order: %r" % (n, line[:80])
            k += 1


def t_every_dated_citation_resolves_and_its_quote_is_found():
    s = _notes()
    bad, n, q = [], 0, 0
    for m in DCITE.finditer(s):
        sha, path, spec, quote = m.groups()
        if not _have(sha):
            raise Skip("commit %s is not in this object store" % sha)
        text = _show(sha, path)
        if text is None:
            bad.append("%s:%s: no such file" % (sha, path)); continue
        ls = text.splitlines()
        n += 1
        got = []
        for a, b in _ranges(spec):
            if not (1 <= a <= b <= len(ls)):
                bad.append("%s:%s:%d-%d outside 1..%d" % (sha, path, a, b, len(ls))); continue
            got.extend(ls[a - 1:b])
        if quote is not None:
            q += 1
            if _norm(quote) not in _norm(" ".join(got)):
                bad.append("%s:%s:%s lacks %r" % (sha, path, spec, _norm(quote)[:60]))
    assert n >= 60, "the notes cite less than written: %d" % n
    assert q >= 50, "the notes quote less than written: %d" % q
    assert not bad, "; ".join(bad[:6])


def t_every_sha_named_is_a_commit():
    s = _notes()
    shas = set(SHA.findall(s)) | {m.group(1) for m in DCITE.finditer(s)}
    assert len(shas) >= 30, "the notes name fewer commits than written: %d" % len(shas)
    missing = sorted(x for x in shas if not _have(x))
    if missing and all(not _have(x) for x in (CL, R3, DG)):
        raise Skip("the worker branches are not in this object store")
    assert not missing, "named shas that are not commits here: %s" % missing


def t_the_chain_and_the_branch_containments_hold():
    _need(TIP, SLOTI, *[s for _, s in ORDER])
    assert _anc(SLOTI, "HEAD"), "fnd/lstat31's tip is not this branch's base"
    assert _anc("bbba3e53", SLOTI) and _anc("bbba3e53", TIP), "Slot I's fold and the tip do not share commit 2a"
    for c in CHAIN:
        assert _anc(c, TIP), "%s is not in the integration's tip" % c
    for a, b in CONTAINS:
        assert _anc(a, b), "%s is not contained in %s" % (a, b)
    for name, sha in ORDER:
        assert not _anc(sha, TIP), "%s %s is in the integration's tip, not only prepared" % (name, sha)
    assert not _anc(SLOTI, TIP), "Slot I's fold is already in the tip"


def t_the_placeholders_stand():
    t = _page()
    l4 = _block(t, "4")
    for p in ("__CANDIDATE__", "__PROMOTED__"):
        assert t.count(p) == 1, "%s stands %d times on the page" % (p, t.count(p))
        assert p in l4, "%s is not in Layer 4's block" % p
    assert "INTEGRATED: `__CANDIDATE__`" in _norm(l4) and "PROMOTED: `__PROMOTED__`" in _norm(l4)
    assert t.count(DESK) == 1 and ("**The Layer 4 DESK gate:** " + DESK) in l4, "the DESK-gate cell lost its placeholder"
    assert "[COORDINATOR:" not in _notes(), "the notes write a coordinator placeholder"


def t_the_three_claims_each_with_their_own_state_word():
    l4 = _block(_page(), "4")
    lines = [x for x in l4.splitlines() if x.startswith("- ")]
    for prefix, word in CLAIMS:
        hit = [x for x in lines if x.startswith(prefix)]
        assert len(hit) == 1, "the claim line is missing or doubled: %s" % prefix
    i = l4.index("**The three completion claims at the integration's tip, each with its own state**")
    block = l4[i:l4.index("**Layout entry after set 30:**", i)]
    words = [x for x in block.splitlines() if x.startswith("- ")]
    assert len(words) == 3, "three claim lines, not %d" % len(words)
    firsts = [next(w for w in STATE_WORDS if (": " + w) in x.split(" (")[0]) for x in words]
    assert firsts == ["NOT YET ASSESSED", "BLOCKED", "BLOCKED"], firsts
    r3 = _show(R3, "v2/docs/records/int30/RESULT.draft3.md").splitlines()
    rows = {c[1]: c[2] for c in ([y.strip() for y in x.split("|")] for x in r3[305:308]) if len(c) > 3}
    assert rows == {"Engineering-handover readiness": "NOT YET ASSESSED", "Power-design closure": "BLOCKED",
                    "Fabrication release": "BLOCKED"}, rows
    assert not re.search(r"\d\s*(?:%|per ?cent)", _notes()), "a percentage in the notes"


def t_w15s_classification_counts_and_the_six():
    t = _show(CL, "v2/docs/records/int30/CLASSIFICATION.draft.md")
    rows = [[c.strip() for c in x.split("|")] for x in t.splitlines() if re.match(r"^\| \d+ \| `", x)]
    assert len(rows) == 38, "W15's table has %d numbered rows" % len(rows)
    ric = [r for r in rows if r[7].startswith("REVIEWED-INPUT CHANGED")]
    assert len(ric) == 13
    six = re.findall(r"`([0-9a-f]{8})`", t.splitlines()[87])
    assert six == SIX, six
    r3 = _show(R3, "v2/docs/records/int30/RESULT.draft3.md").splitlines()
    nn = [re.search(r"`([0-9a-f]{8})`", x).group(1) for x in r3[69:82] if "NOT ONLY NARROWING" in x]
    assert nn == SIX, nn
    l4 = _block(_page(), "4")
    subs = re.findall(r"^  - `([0-9a-f]{8})`: ", l4, re.M)
    assert subs == SIX, subs
    assert "REVIEWED-INPUT CHANGED in 13" in _norm(l4) and "the 13 as UNREVIEWED CHANGES" in _norm(l4)


def t_w12s_k_table_counts():
    t = _show(DG, "v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft2.md")
    rows = [[c.strip() for c in x.split("|")] for x in t.splitlines() if re.match(r"^\| K-\d\d \|", x)]
    assert len(rows) == 28
    yes = [r for r in rows if r[4].startswith("yes")]
    no = [r for r in rows if r[4] == "no"]
    nxt = [r for r in yes if r[5].startswith("next set:")]
    none = [r for r in yes if r[5].startswith("none")]
    assert (len(yes), len(no), len(nxt), len(none)) == (19, 9, 13, 6), (len(yes), len(no), len(nxt), len(none))
    s = _norm(_block(_page(), "4"))
    assert ("So 19 stand on the candidate, 13 of them restated only on next-set branches and 6 unrestated, and 9 are carried by "
            "the candidate's own text") in s


def t_the_ledger_and_l4e9_at_the_tip():
    rem = _show(TIP, REM).splitlines()
    assert sum(1 for x in rem if re.match(r"^### RE-\d+ \(cx46 item \d+\)", x)) == 12, "the ledger's cx46 items"
    assert rem[668] == "Counts: remaining engineering 20; qualification 1; external architecture fact 3; closed 4; conditional 2."
    old = _show(SLOTI_BASE, REM).splitlines()
    assert old[584].startswith("Counts: remaining engineering 19;"), "Slot I's count at 7070f106"
    assert rem[498].startswith("### HO-F: D-10 / E-1") and rem[124].startswith("### RE-2 (cx46 item 2)")
    l4o = _show(TIP, "v2/docs/records/l4e9/l4e9_power_path.out").splitlines()
    assert "D-10 (E-1) and D-17 (RE-2)" in l4o[559] and "criterion 2 FAIL with 2 defects open" in l4o[1016]
    s = _norm(_block(_page(), "4"))
    assert "the count of 19 quoted above is the ledger at `7070f106`, dated history" in s


def t_the_connected_count_and_the_stability_digests_at_the_tip():
    assert "117 changes" in _show(SLOTI_BASE, CON).splitlines()[61]
    assert "118 changes" in _show(TIP, CON).splitlines()[61]
    rx = re.compile(r"^(v2/\S+) pass 1: sha256=([0-9a-f]{64}); pass 2: sha256=([0-9a-f]{64}); equal$")
    rows = [m.groups() for m in (rx.match(x) for x in _show(TIP, DIG).splitlines()) if m]
    assert len(rows) == 18
    eq = [p for p, h1, _ in rows if hashlib.sha256(_show(TIP, p).encode("utf-8")).hexdigest() == h1]
    assert eq == ["v2/docs/records/l9t5/l9t5_f01_drafts.out"], eq
    _need("ac8efbca", "d83d9f2d", "33efca07")
    moved = _git("diff", "--name-only", "ac8efbca", "d83d9f2d", "--", *[p for p, _, _ in rows]).stdout.decode().split()
    assert sorted(moved) == sorted(p for p, _, _ in rows if p not in eq), "the 17 did not all change between ac8efbca and 2b"
    assert "v2/docs/records/l6r2/l6r2_passives.out" in _git("show", "--name-only", "--format=", "33efca07").stdout.decode().split()
    s = _norm(_block(_page(), "9"))
    assert "17 of the eighteen DIGESTS-cr3 outputs differ from their digest and `v2/docs/records/l9t5/l9t5_f01_drafts.out` alone" in s
    assert "the 17 changed between CANDIDATE 3's `ac8efbca` and commit 2b `d83d9f2d`" in s


def t_no_generator_evidence_or_contract_changed_since_set_29():
    _need(SET29, TIP)
    r = _git("diff", "--name-only", SET29, TIP, "--", "v2/ecad/tools/gen_*", "v2/docs/CURRENT-EVIDENCE.md",
             "v2/docs/HW-FW-CONTRACT.md", "v2/docs/PCB-BRING-UP.md")
    assert r.returncode == 0 and not r.stdout.strip(), r.stdout.decode()[:200]
    hw = _show(TIP, "v2/docs/HW-FW-CONTRACT.md")
    for x in ("FW-B20", "FW-B21", "FW-B22", "V-B23"):
        assert x not in hw, "%s is in HW-FW-CONTRACT.md at the tip" % x
    _need(SLOTI_BASE)
    assert not _git("diff", "--name-only", SLOTI_BASE, TIP, "--", "v2/docs/HW-FW-CONTRACT.md").stdout.strip()


def t_the_next_sets_order_is_the_plans():
    s = _norm(_w21head(_page()))
    want = ", ".join("%s `%s`" % p for p in ORDER)
    flat = re.sub(r" \(it contains [^)]*\)", "", s)
    assert want in flat, "the eight merges are not written in the plan's order"
    for w in ("one conflict, TP-E11-29.md, resolved to W3's whole file", "28 first-order moved pins",
              "145 tests expected to fail before regeneration"):
        assert w in s, w
    r3 = _show(R3, "v2/docs/records/int30/RESULT.draft3.md").splitlines()
    got = [(c[2], c[3].split()[0].strip("`")) for c in ([y.strip() for y in x.split("|")] for x in r3[319:327])]
    assert got == ORDER, got
    plan = os.path.join(os.path.dirname(ROOT), "_runs", "int31", "PLAN.draft.md")
    if os.path.isfile(plan):
        p = open(plan, encoding="utf-8").read().splitlines()
        assert _norm(" ".join(p[74:76])).find(", ".join(n for n, _ in ORDER)) >= 0, "the plan's order"
        assert "w3annex 1" in p[66] and "28 on 2b" in p[135] and "145" in " ".join(p[243:245])
        assert "the whole file at fnd/w3annex's bytes" in p[100]
    for m in WORK.finditer(_notes()):
        f = os.path.join(os.path.dirname(ROOT), m.group(1))
        if os.path.isfile(f) and m.group(2):
            n = len(open(f, encoding="utf-8").read().splitlines())
            for a, b in _ranges(m.group(2)):
                assert 1 <= a <= b <= n, "%s:%d-%d outside 1..%d" % (m.group(1), a, b, n)


def t_the_notes_carry_no_dash_no_double_quote_and_no_acceptance_word():
    s = _notes()
    assert not any(d in s for d in DASHES), "a dash in the notes"
    assert '"' not in s, "a straight double quote in the notes"
    for w in ("ACCEPTED", "ACCEPTS", "PASSES", "QUALIFIED:", "RELEASED"):
        assert w not in s, "the notes say %s" % w
    assert "CLOSED" not in re.sub(r"NOT CLOSED", "", s), "a CLOSED outside NOT CLOSED"
    assert not re.search(r"\|\s*MET\s*\|", s)
    for w in ("prepared for the next set, not in the candidate", "at `c4492dd3`"):
        assert s.lower().count(w.lower()) >= 8, "fewer dated notes than written: %s" % w
    m = open(os.path.abspath(__file__), encoding="utf-8").read()
    assert not any(d in m for d in DASHES), "a dash in this module"


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
