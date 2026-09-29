#!/usr/bin/env python3
"""Step 2 of stream s122 (S-122, MESHSAT-1357): judge every sentence of the inventory against the committed netlists of
all six netlisted boards (`tx_inhibit.parse_netlist`) and the generators, and write the verdicts to `verdicts.out`.

For each sentence the script itself performs, and records in the output:
  1. NAMES: every part reference the sentence names is looked up on the netlists (on the board the sentence attributes it
     to when it names one; otherwise on any board), and every net token is looked up; a part that is on no netlisted board
     fails unless the judgement names why (a part of the unnetlisted block E5, a module's own pin, an item of another
     document with a part-like name);
  2. CITATIONS: every generator line cited (`gen_sch_x.py:N-M`) is read at the commit the sentence dates it to
     (`at <sha>`) or, undated, in the generator at this commit, and must hold at least one part or net the sentence names;
  3. ASSERTIONS: the judgement's own list (`judgements.py`): a pin on a net, a value, a net's members, a part's absence;
     every one is evaluated here on the netlists;
  4. the VERDICT: TRUE (judged true on reading and every check of 1 to 3 holds), STALE (judged stale, or any check of 1 to
     3 fails; the text of the netlist is given), NOT DERIVABLE (the claim rests on a held document, a measurement, the
     firmware or a procedure, not on a netlist: left as it is and said so), or UNJUDGED (no judgement written for this
     text; the closure refuses on any).
  5. BASELINE (round 2): a CONOPS.md sentence whose value is the baseline's, its current value kept in the row(s) of the
     status page it names (`kept`); its assertions state the current value and must hold (round 3), or it is STALE.
  6. COUNTS (rounds 2 and 3): every spelled count of parts is covered: with one count, a count assertion (#) of the same
     number or a `counts_ok` reason; with several, `counts_ok` maps each count phrase to a reason that names what the
     phrase counts, or to 'asserted: <one of the judgement's own count assertions of the same number>'.
  7. ABSENT (round 3, check-s122-2 B1): every CONOPS.md sentence that states something absent, owed, not drawn or not
     connected is inventoried in any section and judged TRUE or BASELINE; a NOT DERIVABLE judgement of one binds each
     such word to a phrase of the sentence that is not about the circuit (`absent_ok`), or the sentence is UNJUDGED.
Assertion forms added in round 3: a netlist at a commit (`B@<commit>:U41@PB7=SDA`, parsed from `git show`), a document at
a commit and its negation (`DOC@<commit>:<path>~words`, `DOC@<commit>^:<path>!~words`), a net's exact members
(`B:NET>=ref1,ref2`), and open and closed items in `REG:` (their `status`).
  8. FIGURES (round 6, check-s122-5 B1): a judgement that declares `figures_ok` binds each figure-and-unit token of its
     sentence (`figure_tokens`) to one of its own assertions whose stated content carries the token's numbers
     (`figures_uncovered`); a key the sentence does not hold, a value naming no own assertion, or a token left uncovered
     fails it (`check_figs`). Only judgements that declare it are held to it; close_s122.py asks it of every sentence on
     the lines of its closing list. The role rule's four tests and the history tie can be switched off one at a time
     (`ROLE_TESTS`) for test_close_s122.py's mutation tests; a verdict is written with all on.
Assertion forms added in round 6, for figures: a board file beside the netlist (`PCB:A:layers=6`, `PCB:A:outline=240x160`,
an inner cutout `PCB:C:hole=240x176`, a zone's net on a layer `PCB:B:zone=In4.Cu~+5V`, and a count of zones by name
`PCB:E:zones~<text>=11`), a count of nets by the end of their name (`B:#net~_CA=7`), a count of a text in a file at a
commit (`CNT@<commit>:<path>~<text>=4`), and a field of a decision in pcb_decisions.yaml (`DEC:43.outcome~<words>`).
A judgement is keyed by the sentence's digest (sha256/10 of its whitespace-normalised text), so a corrected sentence is a
new text that needs its own judgement, and a line shift moves nothing.

Writes only `verdicts.out` beside this file (or prints with --stdout). Exit 0; the counts are in the last lines.
Run: python3 verdicts.py [--stdout]."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import judgements as J  # noqa: E402

BOARD_OF = [(re.compile(r"\b(?:A2\d|board A|A's)\b"), "A"), (re.compile(r"\b(?:B1\d|board B|B's)\b"), "B"),
            (re.compile(r"\b(?:C[5-8]|board C|C's|the backer)\b"), "C"), (re.compile(r"\b(?:D[6-9]|board D|D's)\b"), "D"),
            (re.compile(r"\b(?:E[67]|board E|E's|the dock strip)\b"), "E"), (re.compile(r"\b(?:P[2-9]|board P|P's)\b"), "P")]
ASSERT = re.compile(r"^(?P<b>[ABCDEP]):(?:(?P<absent>!)(?P<ar>[\w{}#+-]+)|(?P<ref>[\w#+-]+)\.(?P<pin>[\w]+)=(?P<net>\S+)|"
                    r"(?P<fref>[\w#+-]+)@(?P<func>[\w~{}]+)=(?P<fnet>\S+)|"
                    r"(?P<vref>[\w#+-]+)~(?P<val>.+)|(?P<nnet>[^>\s]+)>(?P<exact>=?)(?P<members>[\w,#+-]+)|(?P<eref>[\w#+-]+)\?)$")
GASSERT = re.compile(r"^G@(?P<c>[0-9a-f]+|HEAD):(?P<f>[\w./-]+):(?P<a>\d+)(?:-(?P<b>\d+))?~(?P<w>.+)$")
DOCASSERT = re.compile(r"^DOC(?:@(?P<c>[0-9a-f]+\^?))?:(?P<f>[\w./-]+)(?P<neg>!)?~(?P<w>.+)$")
_GIT = {}


def gen_text(rel, commit):
    k = (rel, commit)
    if k not in _GIT:
        if commit:
            r = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (commit, rel)], capture_output=True, text=True)
            _GIT[k] = r.stdout.split("\n") if r.returncode == 0 else None
        else:
            _GIT[k] = open(os.path.join(L.TOP, rel), encoding="utf-8").read().split("\n")
    return _GIT[k]


_AT_NL = {}
_GEO = {}


def _sexp_blocks(txt, head):
    i = 0
    while True:
        i = txt.find("(" + head, i)
        if i < 0: return
        d = 0
        for k in range(i, len(txt)):
            if txt[k] == "(": d += 1
            elif txt[k] == ")":
                d -= 1
                if d == 0: break
        yield txt[i:k + 1]
        i = k + 1


def board_geo(board):
    """The committed board file of a board (beside its netlist): copper layer count, the Edge.Cuts outline, the widths and
    heights between inner Edge.Cuts coordinates, and each zone's (layer, net)."""
    if board not in _GEO:
        net = L.NETLISTS[board]
        path = os.path.join(L.TOP, os.path.dirname(os.path.dirname(net)), os.path.basename(net).replace(".net", ".kicad_pcb"))
        if not os.path.exists(path):
            _GEO[board] = None
            return None
        txt = open(path, encoding="utf-8").read()
        pts = []
        for h in ("gr_line", "gr_rect", "gr_arc", "gr_poly", "gr_circle"):
            for b in _sexp_blocks(txt, h):
                if '(layer "Edge.Cuts")' in b:
                    pts += [(float(x), float(y)) for x, y in re.findall(r"\((?:start|end|mid|xy) ([-\d.]+) ([-\d.]+)\)", b)]
        xs, ys = sorted({round(p[0], 3) for p in pts}), sorted({round(p[1], 3) for p in pts})
        ins_x = [x for x in xs if xs[0] + 5 < x < xs[-1] - 5]
        ins_y = [y for y in ys if ys[0] + 5 < y < ys[-1] - 5]
        zones, names = [], []
        for z in _sexp_blocks(txt, "zone"):
            nn = re.search(r'\(net_name "([^"]*)"\)', z)
            zn = re.search(r'\(name "([^"]*)"\)', z)
            if zn: names.append(zn.group(1))
            for lay in re.findall(r'\(layers? ((?:"[^"]+"\s*)+)\)', z)[:1]:
                for l in re.findall(r'"([^"]+)"', lay): zones.append((l, nn.group(1) if nn else ""))
        _GEO[board] = {"layers": len(re.findall(r'\(\d+ "[^"]*\.Cu"', txt[:20000])),
                       "outline": (round(xs[-1] - xs[0], 2), round(ys[-1] - ys[0], 2)),
                       "inner_dx": {round(b - a, 2) for a in ins_x for b in ins_x if b > a},
                       "inner_dy": {round(b - a, 2) for a in ins_y for b in ins_y if b > a}, "zones": zones,
                       "zone_names": names}
    return _GEO[board]


# ------------------------------------------------------------------ round 6: figures on the closing list's lines
# (check-s122-5 B1: V2-SPEC.md line 47 named the SA868 a 1 W part while board D's U2 is its 2 W exciter). Not every figure
# of every sentence is judged: close_s122.py scans only the lines of the closing list, and each figure-and-unit token
# there (a number with W, V, A, Wh, dBm, mm, C and the like, a range or product of them, an 'N x M' size, a 'NxM' header,
# a spelled count) must lie inside a key of the judgement's `figures_ok` (or an 'asserted:' entry of `counts_ok`) whose
# value names one of its own assertions that carries the figure's numbers.
FIG_UNIT = r"(?:W|mW|kW|V|mV|A|mA|Wh|Ah|mAh|dBm|dB|mm|cm|C|Hz|kHz|MHz|GHz|ohm|oz)"
FIG_NUM = r"[-+]?\d+(?:\.\d+)?"
FIG_RX = re.compile(r"(?<![\w.+-])(%s(?:\s*(?:to|x)\s*%s)?)\s*%s\b|(?<![\w.])(\d+ x \d+)\b|(?<![\w.])(\d+x\d+)\b|\b(%s)\b"
                    % (FIG_NUM, FIG_NUM, FIG_UNIT, L.NUMW), re.I)
NUMWORD = {w: i + 2 for i, w in enumerate(L.NUMW.split("|"))}


def figure_tokens(s):
    """[(start, end, text, [numbers])] of the figure-and-unit tokens of a sentence (dates and designators are not)."""
    out = []
    for m in FIG_RX.finditer(s):
        txt = m.group(0)
        if m.group(4):
            if not re.match(r"^\s*[a-z]", s[m.end():m.end() + 2]) and not re.match(r"^\s*[A-Z0-9]", s[m.end():m.end() + 2]):
                continue
            out.append((m.start(), m.end(), txt, [str(NUMWORD[txt.lower()])]))
            continue
        nums = [re.sub(r"^[-+]", "", x) for x in re.findall(FIG_NUM, txt)]
        out.append((m.start(), m.end(), txt, nums))
    return out


def _content(x):
    """What an assertion states, after its subject: the text after the first '~' or '=' ('D:U2~VHF 2 W exciter' states
    'VHF 2 W exciter'; 'PCB:A:outline=240x160' states '240x160'), so a designator's or a path's digits carry no figure."""
    k = min([i for i in (x.find("~"), x.find("=")) if i >= 0] or [0])
    return x[k + 1:] if k else x


def _digits(x):
    """A text's number groups, with 13V8 and 3V3 read as 13.8 and 3.3 and a decimal point dropped: {'138', '33', ...}."""
    x = re.sub(r"(\d)V(\d)", r"\1\2", x)
    x = re.sub(r"(\d)\.(\d)", r"\1\2", x)
    return set(re.findall(r"\d+", x))


def figures_uncovered(s, j):
    """The figure tokens of a sentence that no `figures_ok` key (or 'asserted:' counts_ok key) covers with an own assertion
    carrying the token's numbers (a spelled count may be carried by its word or an '=N' count assertion)."""
    cover = dict(j.get("figures_ok") or {})
    cover.update({k: v for k, v in (j.get("counts_ok") or {}).items() if isinstance(v, str) and v.startswith("asserted: ")})
    spans = []
    for k, v in cover.items():
        if not v.startswith("asserted: "): continue
        x = v[len("asserted: "):]
        if x not in j.get("a", ()): continue
        for m in re.finditer(re.escape(k), s): spans.append((m.start(), m.end(), x))
    out = []
    for a, b, txt, nums in figure_tokens(s):
        ok = False
        for sa, sb, x in spans:
            if sa <= a and b <= sb:
                dg = _digits(_content(x))
                words = _content(x).lower()
                if all(n.replace(".", "") in dg or any(re.search(r"\b%s\b" % w, words) for w, i in NUMWORD.items() if str(i) == n)
                       for n in nums):
                    ok = True
                    break
        if not ok: out.append(txt)
    return out


def netlist_at(board, commit):
    """Board's committed netlist at a commit, parsed with tx_inhibit.parse_netlist from a temporary copy."""
    import tempfile
    k = (board, commit)
    if k not in _AT_NL:
        r = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (commit, L.NETLISTS[board])], capture_output=True)
        if r.returncode:
            _AT_NL[k] = None
        else:
            with tempfile.TemporaryDirectory() as d:
                f = os.path.join(d, "n.net")
                open(f, "wb").write(r.stdout)
                _AT_NL[k] = L.TX.parse_netlist(f)
    return _AT_NL[k]


def run_assert(a, nls):
    am = re.match(r"^([ABCDEP])@([0-9a-f]+):(.+)$", a.strip())
    if am:
        nl = netlist_at(am.group(1), am.group(2))
        if nl is None: return False, "board %s's netlist at %s not readable" % (am.group(1), am.group(2))
        ok, msg = run_assert("%s:%s" % (am.group(1), am.group(3)), dict(nls, **{am.group(1): nl}))
        return ok, "at %s: %s" % (am.group(2), msg)
    g = GASSERT.match(a.strip())
    if g:
        rel = g.group("f") if "/" in g.group("f") else "v2/ecad/tools/" + g.group("f")
        text = gen_text(rel, None if g.group("c") == "HEAD" else g.group("c"))
        if text is None: return False, "%s at %s not readable" % (rel, g.group("c"))
        lo, hi = int(g.group("a")), int(g.group("b") or g.group("a"))
        seg = "\n".join(text[lo - 1:hi])
        ok = all(w in seg for w in g.group("w").split("|"))
        return ok, "%s lines %d to %d at %s hold %s" % (os.path.basename(rel), lo, hi, g.group("c"), g.group("w").replace("|", ", "))
    av = re.match(r"^([ABCDEP]):\*~(.+)$", a.strip())
    if av:
        hits = sorted(r for r in nls[av.group(1)]["comps"] if av.group(2) in L.TX.value(nls[av.group(1)], r))
        return bool(hits), "board %s has a part whose value holds %r (%s)" % (av.group(1), av.group(2), ",".join(hits[:6]) or "none")
    nc = re.match(r"^([ABCDEP]):#net~(.+)=(\d+)$", a.strip())
    if nc:   # round 6: the count of a netlist's nets whose name ends in a text (board B's seven voters' CA products)
        hits = sorted(n for n in nls[nc.group(1)]["nets"] if n.lstrip("/").endswith(nc.group(2)))
        return len(hits) == int(nc.group(3)), "board %s: %s nets whose name ends in %r (read: %d, %s)" % (
            nc.group(1), nc.group(3), nc.group(2), len(hits), ",".join(h.lstrip("/") for h in hits[:12]))
    cm = re.match(r"^([ABCDEP]):#(fp|val|ref)~(.+)=(\d+)$", a.strip())
    if cm:
        nl, how, pat, want = nls[cm.group(1)], cm.group(2), cm.group(3), int(cm.group(4))
        if how == "fp": hits = [r for r in nl["comps"] if pat in nl["comps"][r]["fp"]]
        elif how == "val": hits = [r for r in nl["comps"] if pat in L.TX.value(nl, r)]
        else: hits = [r for r in nl["comps"] if r.startswith(pat)]
        return len(hits) == want, "board %s: %d parts whose %s holds %r (read: %d, %s)" % (
            cm.group(1), want, {"fp": "footprint", "val": "value", "ref": "designator"}[how], pat, len(hits),
            ",".join(sorted(hits)[:20]))
    nv = re.match(r"^([ABCDEP]):!~(.+)$", a.strip())
    if nv:
        hits = sorted(r for r in nls[nv.group(1)]["comps"] if nv.group(2) in L.TX.value(nls[nv.group(1)], r))
        return not hits, "board %s has no part whose value holds %r (found: %s)" % (nv.group(1), nv.group(2), ",".join(hits) or "none")
    rg = re.match(r"^REG:([A-Z]+-\d+)\.(\w+)(=|~)(.+)$", a.strip())
    if rg:
        if "reg" not in _ROWS:
            y = yaml.safe_load(L.read("v2/ecad/tools/pcb_requirements.yaml"))
            _ROWS["reg"] = {r["id"]: r for r in y["records"]}
            _ROWS["reg"].update({r["id"]: dict(r, status=r.get("status", "OPEN")) for r in y["open_items"]})
            _ROWS["reg"].update({r["id"]: dict(r, status="CLOSED") for r in y["closed_items"]})
        got = (_ROWS["reg"].get(rg.group(1)) or {}).get(rg.group(2))
        ok = (str(got) == rg.group(4)) if rg.group(3) == "=" else (rg.group(4) in str(got))
        return ok, "registry %s %s %s %s (read: %s)" % (rg.group(1), rg.group(2), rg.group(3), rg.group(4), got)
    fm = re.match(r"^FILE:([\w./-]+)@([0-9a-f]+)$", a.strip())
    if fm:
        got = L.sha16(fm.group(1))
        return got == fm.group(2), "%s sha256/16 %s (read: %s)" % (fm.group(1), fm.group(2), got)
    sm = re.match(r"^SHA:([ABCDEP])=([0-9a-f]+)$", a.strip())
    if sm:
        got = nls[sm.group(1)]["sha16"]
        return got == sm.group(2), "board %s netlist sha256/16 %s (read: %s)" % (sm.group(1), sm.group(2), got)
    cn = re.match(r"^CNT(?:@([0-9a-f]+))?:([\w./-]+)~(.+)=(\d+)$", a.strip())
    if cn:   # round 6: how many times a file (at a commit) holds a text (the four AP64500 rails of gen_sch_a.py at b2709118)
        lines = gen_text(cn.group(2), cn.group(1)) if cn.group(1) else open(os.path.join(L.TOP, cn.group(2)), encoding="utf-8").read().split("\n")
        if lines is None: return False, "%s at %s not readable" % (cn.group(2), cn.group(1))
        got = "\n".join(lines).count(cn.group(3))
        return got == int(cn.group(4)), "%s%s holds %r %s times (read: %d)" % (
            cn.group(2), (" at " + cn.group(1)) if cn.group(1) else "", cn.group(3), cn.group(4), got)
    dc = re.match(r"^DEC:(\d+)\.(\w+)~(.+)$", a.strip())
    if dc:   # round 6: a field of decision n in v2/ecad/tools/pcb_decisions.yaml, whitespace normalised
        ds = [d for d in yaml.safe_load(open(os.path.join(L.TOP, "v2/ecad/tools/pcb_decisions.yaml"), encoding="utf-8"))["decisions"]
              if str(d.get("n")) == dc.group(1)]
        if len(ds) != 1: return False, "pcb_decisions.yaml has %d decisions numbered %s" % (len(ds), dc.group(1))
        txt = " ".join(str(ds[0].get(dc.group(2), "")).split())
        return " ".join(dc.group(3).split()) in txt, "decision %s's %s says %r" % (dc.group(1), dc.group(2), dc.group(3)[:80])
    zc = re.match(r"^PCB:([ABCDEP]):zones~(.+)=(\d+)$", a.strip())
    if zc:   # round 6: the count of a board file's zones whose name holds a text (board E's float clamp keep-outs)
        g = board_geo(zc.group(1))
        if g is None: return False, "board %s's board file not readable" % zc.group(1)
        hits = [n for n in g["zone_names"] if zc.group(2) in n]
        return len(hits) == int(zc.group(3)), "board %s's board file: %s zones whose name holds %r (read: %d)" % (
            zc.group(1), zc.group(3), zc.group(2), len(hits))
    bm = re.match(r"^PCB:([ABCDEP]):(layers|outline|hole|zone)=(.+)$", a.strip())
    if bm:   # round 6: the committed board file beside the netlist (copper layers, the Edge.Cuts outline, an inner cutout,
        # a copper zone's net on a layer), for the rows' board figures
        g = board_geo(bm.group(1))
        if g is None: return False, "board %s's board file not readable" % bm.group(1)
        what, want = bm.group(2), bm.group(3)
        if what == "layers": return g["layers"] == int(want), "board %s has %d copper layers (asserted %s)" % (bm.group(1), g["layers"], want)
        if what == "outline":
            return "%gx%g" % g["outline"] == want, "board %s's outline is %gx%g mm (asserted %s)" % ((bm.group(1),) + g["outline"] + (want,))
        if what == "hole":
            w, h = (float(x) for x in want.split("x"))
            ok = w in g["inner_dx"] and h in g["inner_dy"]
            return ok, "board %s has an inner cutout %s mm: %s" % (bm.group(1), want, "yes" if ok else "no")
        lay, _, net = want.partition("~")
        hits = sorted({n for l, n in g["zones"] if l == lay and net in n})
        return bool(hits), "board %s has a zone on %s whose net holds %r (%s)" % (bm.group(1), lay, net, ",".join(hits) or "none")
    pm = re.match(r"^PDF:(?P<f>[\w./-]+\.pdf)~(?P<w>.+)$", a.strip())
    if pm:   # round 4: a held maker's sheet, read with pdftotext (the text layer), whitespace normalised
        r = subprocess.run(["pdftotext", "-layout", os.path.join(L.TOP, pm.group("f")), "-"], capture_output=True)
        if r.returncode: return False, "%s not readable by pdftotext" % pm.group("f")
        txt = " ".join(r.stdout.decode("utf-8", "replace").split())
        ok = all(" ".join(w.split()) in txt for w in pm.group("w").split("|"))
        return ok, "%s's text holds %r" % (pm.group("f"), pm.group("w")[:80])
    dm = DOCASSERT.match(a.strip())
    if dm:
        if dm.group("c"):   # round 3: a document at a commit (the commit's file, read with git show)
            lines = gen_text(dm.group("f"), dm.group("c"))
            if lines is None: return False, "%s at %s not readable" % (dm.group("f"), dm.group("c"))
            txt = " ".join("\n".join(lines).split())
        else:
            txt = " ".join(open(os.path.join(L.TOP, dm.group("f")), encoding="utf-8").read().split())
        has = all(" ".join(w.split()) in txt for w in dm.group("w").split("|"))
        ok = (not has) if dm.group("neg") else has
        return ok, "%s%s %s %r" % (dm.group("f"), (" at " + dm.group("c")) if dm.group("c") else "",
                                    "does not say" if dm.group("neg") else "says", dm.group("w")[:80])
    m = ASSERT.match(a.strip())
    if not m: return False, "unparsable assertion %r" % a
    nl = nls[m.group("b")]
    if m.group("absent"):
        r = m.group("ar")
        return (r not in nl["comps"]), "%s absent on %s" % (r, m.group("b"))
    if m.group("ref"):
        got = nl["pin"].get((m.group("ref"), m.group("pin")))
        return got == m.group("net"), "%s %s.%s on %s (netlist: %s)" % (m.group("b"), m.group("ref"), m.group("pin"), m.group("net"), got)
    if m.group("fref"):
        hits = sorted({nl["pin"][(r, p)] for (r, p), f in nl["func"].items() if r == m.group("fref") and f == m.group("func")})
        return hits == [m.group("fnet")], "%s %s %s on %s (netlist: %s)" % (
            m.group("b"), m.group("fref"), m.group("func"), m.group("fnet"), ",".join(hits) or "none")
    if m.group("vref"):
        v = L.TX.value(nl, m.group("vref"))
        return (m.group("val") in v), "%s %s value has %r (netlist: %r)" % (m.group("b"), m.group("vref"), m.group("val"), v[:60])
    if m.group("nnet"):
        on = {r for r, _p, *_x in nl["nets"].get(m.group("nnet"), [])}
        want = set(m.group("members").split(","))
        if m.group("exact"):
            return want == on, "%s net %s holds exactly %s (read: %s)" % (m.group("b"), m.group("nnet"), ",".join(sorted(want)), ",".join(sorted(on)))
        return want <= on, "%s net %s holds %s (missing: %s)" % (m.group("b"), m.group("nnet"), ",".join(sorted(want)), ",".join(sorted(want - on)) or "none")
    if m.group("eref"):
        return (m.group("eref") in nl["comps"]), "%s %s present" % (m.group("b"), m.group("eref"))
    return False, "assertion %r" % a


def check_names(s, nm, nls, j):
    """(failures, notes) of the NAMES check."""
    fails, notes = [], []
    boards = [k for rx, k in BOARD_OF if rx.search(s)]
    skip = set(j.get("not_parts", ()))
    for r in nm["refs"]:
        if r in skip: continue
        on = [k for k, nl in nls.items() if r in nl["comps"]]
        if not on:
            fails.append("%s is on no netlisted board" % r)
        elif boards and not set(on) & set(boards) and r not in j.get("any_board", ()):
            notes.append("%s on %s (sentence names %s)" % (r, "".join(on), "".join(boards)))
    return fails, notes


PART_KINDS = ("document", "case", "bought", "stock", "stackup", "withdrawn", "owed", "module", "elsewhere")


def part_boards(part, nls):
    """{board: [refs]} whose netlist value text holds the part number (with its series word, or the number alone)."""
    keys = [part] + ([part.split(" ", 1)[1]] if " " in part else [])
    out = {}
    for b, nl in sorted(nls.items()):
        refs = sorted(r for r, c in nl["comps"].items() if any(k in c["value"] for k in keys))
        if refs: out[b] = refs
    return out


HIST = re.compile(r"\b(?:had left|left|was|were|until|before|withdrawn|named|called|said|no longer|gone|replaced|"
                  r"line \d+'s|\d{1,2} Sep(?:tember)?|at `?[0-9a-f]{7,8}`?|in the device set|at its date|does not fit|"
                  r"did not fit)\b", re.I)


def history_excuse(why):
    """True for a parts_ok entry that excuses a part as history: withdrawn, or asserted at a commit (a part asserted absent
    now, an owed or withdrawn one, is not tied: its sentence names it as absent)."""
    if why.startswith("withdrawn:"): return True
    if why.startswith("asserted: "):
        return "@" in why[len("asserted: "):].split(":", 1)[0]
    return False


def check_parts(s, nm, nls, j):
    """Round 4 (set 14, check-int15-1 B1): every maker's part number the sentence names is judged against the part values
    of the six netlists. It is on a netlist (a board other than the one the sentence names is noted), or the judgement's
    `parts_ok` names it: 'asserted: <one of its own assertions that names the part>' (a generator at a commit, a
    document, a part value), or a reason that starts with one of PART_KINDS and a colon (a document number, a case item,
    a bought item, a stock code, a stackup, a part the sentence names as withdrawn or owed, a module on a socket).
    Returns (failures, notes)."""
    fails, notes = [], []
    ok = j.get("parts_ok") or {}
    boards = [k for rx, k in BOARD_OF if rx.search(s + " " + " ".join(nm.get("row") or []))]
    for part in nm.get("parts") or []:
        on = part_boards(part, nls)
        why = ok.get(part)
        if why is not None and j.get("v") == "T" and ROLE_TESTS["history"] and history_excuse(why):
            # round 6 (check-s122-5 m1 f): in a TRUE sentence a history excuse holds only in a clause that states the
            # history ('had left', 'on 7 September', 'at <commit>', a line's former text); the part put back as current
            # in another clause is not excused
            num = part.split(" ", 1)[-1]
            for mm in re.finditer(re.escape(num), s):
                lo = max(s.rfind(ch, 0, mm.start()) for ch in ";()")
                his = [s.find(ch, mm.end()) for ch in ";()"]
                hi = min([x for x in his if x >= 0] or [len(s)])
                if not HIST.search(s[lo + 1:hi]):
                    fails.append("%s is excused as history, and the clause %r names it as current" % (part, s[lo + 1:hi].strip()[:80]))
                    break
        if why is not None:
            if why.startswith("asserted: "):
                x = why[len("asserted: "):]
                num = part.split(" ", 1)[-1]
                if x not in j.get("a", ()) or num not in x: fails.append("%s: parts_ok names no own assertion of it (%s)" % (part, x))
                else: notes.append("%s asserted" % part)
            elif why.split(":", 1)[0] not in PART_KINDS or ":" not in why:
                fails.append("%s: parts_ok's reason does not start with one of %s" % (part, ", ".join(PART_KINDS)))
            elif why.startswith("elsewhere:") and not on:
                fails.append("%s: said to be elsewhere, and it is on no netlist" % part)
            else:
                notes.append("%s %s" % (part, why))
            continue
        if not on:
            fails.append("%s is on no netlist's part values" % part)
        elif len(boards) == 1 and boards[0] not in on:
            # the sentence (with its row label) names one board, and the part is not on it: the E6 row's LM5176
            fails.append("%s is on %s, not on board %s, the one board the sentence names" % (
                part, ", ".join("%s (%s)" % (b, ",".join(r[:4])) for b, r in on.items()), boards[0]))
        elif boards and not set(on) & set(boards):
            # a note when the sentence names several boards
            notes.append("%s on %s (the sentence names %s)" % (
                part, ", ".join("%s (%s)" % (b, ",".join(r[:4])) for b, r in on.items()), "".join(boards)))
        else:
            notes.append("%s on %s" % (part, ", ".join("%s (%s)" % (b, ",".join(r[:4])) for b, r in on.items())))
    for k in ok:
        if k not in (nm.get("parts") or []): fails.append("parts_ok names %s, which the sentence does not" % k)
    return fails, notes


# ------------------------------------------------------------------ round 5: a part named in a role (check-s122-4 B1)
ROLE_NOUN = (r"(?:switch(?:es)?|codecs?|hubs?|bridges?|chargers?|gauges?|bucks?|converters?|stages?|controllers?|"
             r"regulators?|LDOs?|amplifiers?|clocks?|supervisors?|sockets?|receptacles?|expanders?|monitors?|sensors?|"
             r"trackers?|hot swaps?|front ends?|exciters?|relays?|transceivers?|buffers?|mux(?:es)?|arrays?|supply|supplies|"
             r"drivers?)")
ROLE_STOP = {"and", "or", "with", "of", "the", "a", "an", "to", "on", "in", "for", "from", "at", "by", "as", "is", "its",
             "their", "each", "per", "two", "three", "four", "+"}
# the words a netlist value states a role by, for each role noun (a value that says "SPDT antenna changeover" states a
# switch; one that says "buck-boost controller" states a stage or a converter)
ROLE_SYN = {"switch": ("switch", "changeover", "spdt", "spst", "mux", "select"), "stage": ("stage", "controller", "converter",
            "buck", "boost", "regulator", "ldo"), "converter": ("converter", "buck", "boost", "controller", "regulator"),
            "ldo": ("ldo", "regulator"), "regulator": ("regulator", "ldo", "buck", "boost"), "clock": ("clock", "rtc"),
            "tracker": ("tracker", "mppt"), "amplifier": ("amplifier",), "buffer": ("buffer", "schmitt"),
            "mux": ("mux", "select", "switch"), "supply": ("supply", "ldo", "regulator", "buck", "boost", "converter"),
            "driver": ("driver",)}
CONVERTER = ("buck", "boost", "controller", "ldo", "regulator", "converter")
# the rails a boards table names, by the word before "rail" and the net a converter's value states it by (kit vocabulary)
RAIL_WORD = {"slot": r"\+5V_S\d", "device": r"\+5V_DEV", "PA": r"\+13V8_PA", "HF": r"\+12V_HF", "PoE": r"\+54V_POE"}


def _norm(x):
    return " ".join(x.lower().replace("-", " ").replace("_", " ").split())


def _sing(w):
    w = w.lower()
    for suf in ("es", "s"):
        if w.endswith(suf) and w[:-len(suf)] in ("switch", "mux") + tuple(n for n in ("codec", "hub", "bridge", "charger",
                "gauge", "buck", "converter", "stage", "controller", "regulator", "ldo", "amplifier", "clock", "supervisor",
                "socket", "receptacle", "expander", "monitor", "sensor", "tracker", "hot swap", "front end", "exciter", "relay",
                "transceiver", "buffer", "array", "driver")):
            return w[:-len(suf)]
    return w


def role_phrases(s, parts):
    """[(part, qualifier words, noun)] for each part named with a role: '<part> <up to three words> <noun>' (the TPS22810
    gate-bias switch, the PCM2912A USB codec), the words being no stop word and no other part number."""
    out = []
    body = L.PN_STRIP.sub(" ", s).replace("`", "")
    for p in parts:
        num = p.split(" ", 1)[-1]
        for m in re.finditer(re.escape(num) + r"((?:[ ][A-Za-z0-9.+/-]+){0,3}?)[ -](%s)\b" % ROLE_NOUN, body):
            q = m.group(1).split()
            if any(w.lower() in ROLE_STOP or L.is_partno(w) or w.startswith("(") for w in q): continue
            out.append((p, q, _sing(m.group(2))))
    return out


def rail_targets(text):
    """[(label, net regex)] of the rails or outlets a phrase names: slot numbers ('slots 1 and 3'), slot rails, the device,
    PA, HF and PoE rails, a rail by its voltage ('the 3.3 V logic rail'), the USB-C outlet."""
    out = []
    nums = re.findall(r"\bslots? ((?:\d(?:, | and |,? and )?)+)", text)
    for grp in nums:
        for n in re.findall(r"\d", grp): out.append(("slot %s" % n, r"\+5V_S%s\b" % n))
    if not nums and re.search(r"\bslot rails?\b", text): out.append(("slot", r"\+5V_S\d\b"))
    for w, net in RAIL_WORD.items():
        if w != "slot" and re.search(r"\b%s\b" % re.escape(w), text): out.append((w, net))
    if re.search(r"\bUSB-C outlet\b", text): out.append(("USB-C outlet", r"\bPD_VPWR\b"))
    if not out and re.search(r"\brails?\b|\blogic\b", text):
        for v in re.findall(r"(\d+(?:\.\d+)?) V\b", text):
            a_, _, b_ = v.partition(".")
            out.append(("%s V" % v, r"\b%s V (?:rail|logic)\b|\+%sV%s(?:_|\b)" % (re.escape(v), a_, b_)))
    return out


def _designators_for(nls, b, net, role):
    """(ref, value) of board b whose value states the net and holds the role: a converter or a monitor of it."""
    out = []
    for r, c in sorted(nls[b]["comps"].items()):
        v = c["value"]
        if not re.search(net, v): continue
        if role == "monitor" and "monitor" in v.lower(): out.append((r, v))
        elif role == "converter" and "monitor" not in v.lower() and any(k in v.lower() for k in CONVERTER): out.append((r, v))
    return out


CONV_NOUN = ("buck", "stage", "converter", "controller", "regulator", "ldo", "supply")


def rail_lists(s, parts):
    """[(part, role, [(label, net)])] for each parenthesised list after a phrase that names rails or an outlet ('three 5.1
    V slot rails and a device rail (AP64500, INA226 monitored)', 'the 13.8 V PA and 12 V HF rails (LM5176, EMCON
    gated)', 'the 45 W USB-C outlet (TPS25740A and an LM5176 stage; ...)'). Round 6 (check-s122-5 m1): every list is read,
    an item that is not a part ('EMCON gated') is skipped without dropping the rest, a leading article and a trailing
    role or qualifier word are stripped ('an LM5176 stage', 'INA226 monitored'); a plain part after rails is their
    converter, a part marked monitored their monitor, and after an outlet only a part named as a stage or converter is
    judged (the outlet's controller is not its converter)."""
    out = []
    body = s.replace("`", "")
    for m in re.finditer(r"([^,;:()]{0,90}\b(?:rails?|outlet)\b)\s*\(([^)]*)\)", body):
        targets = rail_targets(m.group(1))
        if not targets: continue
        outlet = m.group(1).rstrip().endswith("outlet")
        head = m.group(2).split(";")[0]
        for it in re.split(r",| and ", head):
            if " on " in " %s " % it: continue      # '<part> <noun> on <slot>' is judged by target_roles
            toks = [w for w in it.split() if w.lower() not in ("a", "an", "the")]
            if not toks or toks[0] not in parts: continue
            rest = " ".join(toks[1:]).lower()
            if "monitor" in rest: role = "monitor"
            elif any(w in rest for w in CONV_NOUN): role = "converter"
            elif outlet: continue
            else: role = "converter"
            out.append((toks[0], role, targets))
    return out


def target_roles(s, parts):
    """[(part, noun, [(label, net)])] for '<part> <noun> on <slots or a named rail>' ('the AP64500 buck on slots 1 and 3',
    'LM5176 stages on slot 2 and the device rail'): round 6 (check-s122-5 m1 b, c) judges them by those rails' converters."""
    out = []
    body = s.replace("`", "")
    for p in parts:
        num = p.split(" ", 1)[-1]
        for m in re.finditer(re.escape(num) + r"(?:[ -][A-Za-z0-9.+/-]+){0,2}?[ -](%s)s?\b on ([^,;()]{1,60})"
                             % "|".join(CONV_NOUN), body):
            tg = rail_targets(m.group(2))
            if tg: out.append((p, _sing(m.group(1)), tg))
    return out


# round 6 (check-s122-5 m2): the role rule's four tests and check_parts' history tie, each switchable so that a mutation
# test can turn one off and see the closing gate refuse (test_close_s122.py); a verdict is only ever written with all on
ROLE_TESTS = {"forward": True, "reverse1": True, "reverse2": True, "rails": True, "history": True}


def check_roles(s, nm, nls, j):
    """Round 5 (check-s122-4 B1: V2-SPEC.md line 84 called the TPS22810 the gate-bias switch; line 81 gave all four rails
    to the AP64500). A part named in a role must hold that role on its board, read from the netlists' values:
      * forward: a designator that carries the part states the role's noun in its value (a switch, a codec, a buck);
      * reverse: when the role's qualifier is specific (two words or more, 'gate bias'), no designator that does NOT carry
        the part states it while none that carries the part does;
      * rails: a plain list of parts after a phrase naming rails (slot, device, PA, HF, PoE) must be the part of every
        converter whose value states that rail's net, and a part marked 'monitored' of every monitor of it.
    `roles_ok` maps '<part> <noun>' to one of the judgement's own assertions on a designator that carries the part: its
    value's words ('X:REF~words') or a pin on the net that states the role ('X:REF.pin=NET', 'X:REF@FUNC=NET'), for a
    role the value states in other words or by its nets (the LM5176 as A22's front end, `U2` 'VBUS20 from VIN_RAW'; the
    LT8705A as the solar tracker, `U5` on `PV_P`). ROLE_SYN lists the words a value states a noun by. Returns (failures,
    notes)."""
    fails, notes = [], []
    ok = j.get("roles_ok") or {}
    parts = nm.get("parts") or []
    boards = [k for rx, k in BOARD_OF if rx.search(s + " " + " ".join(nm.get("row") or []))]
    def holders(p, bset):
        keys = [p] + ([p.split(" ", 1)[1]] if " " in p else [])
        return [(b, r, c["value"]) for b in bset for r, c in sorted(nls[b]["comps"].items()) if any(k in c["value"] for k in keys)]
    for p, q, noun in role_phrases(s, parts):
        on = part_boards(p, nls)
        bset = [b for b in on if not boards or b in boards] or list(on)
        hold = holders(p, bset)
        key = "%s %s" % (p, noun)
        if key in ok:
            x = ok[key]
            mm = re.match(r"^([ABCDEP]):([\w#+-]+)(?:~|\.\w+=|@\w+=)(.+)$", x)
            if x not in j.get("a", ()) or not mm: fails.append("%s: roles_ok names no own assertion (%s)" % (key, x)); continue
            val = nls[mm.group(1)]["comps"].get(mm.group(2), {}).get("value", "")
            if p.split(" ", 1)[-1] not in val: fails.append("%s: %s:%s does not carry %s" % (key, mm.group(1), mm.group(2), p))
            else: notes.append("%s on %s:%s (%s)" % (key, mm.group(1), mm.group(2), mm.group(3)))
            continue
        if not hold: continue      # the part check reports a part on no netlist
        if ROLE_TESTS["forward"] and not any(any(w in _norm(v) for w in ROLE_SYN.get(noun, (noun,))) for _b, _r, v in hold):
            fails.append("%s is named a %s%s; its designators state another role (%s)" % (
                p, (" ".join(q) + " ") if q else "", noun, "; ".join("%s:%s %s" % (b, r, v[:60]) for b, r, v in hold[:3])))
            continue
        qn = _norm(" ".join(q))
        if ROLE_TESTS["reverse1"] and len(qn.split()) == 1 and not any(qn in _norm(v) for _b, _r, v in hold):
            # round 6 (check-s122-5 m1 d): a one-word qualifier the part's own values do not state, while an active part
            # (U or Q) of the board states it, gives the part a function the netlist gives another part ('the TPS22810
            # bias switch': board D's bias is U15's)
            other = [(b, r, v) for b in bset for r, c in sorted(nls[b]["comps"].items())
                     for v in [c["value"]] if re.match(r"^[UQ]\d", r) and re.search(r"\b%s\b" % re.escape(qn), _norm(v))
                     and "%s %s" % (qn, noun) not in _norm(v) and (b, r, v) not in hold]
            # (a value that names '<qualifier> <noun>' as its load, 'buck 1.2 V Ethernet switch core', points at the part)
            if other:
                b, r, v = other[0]
                fails.append("%s is named the %s %s; the %s is %s:%s (%s), and %s is not" % (
                    p, " ".join(q), noun, " ".join(q), b, r, v[:70], p))
                continue
        if ROLE_TESTS["reverse2"] and len(qn.split()) >= 2 and not any(qn in _norm(v) for _b, _r, v in hold):
            other = [(b, r, v) for b in bset for r, c in sorted(nls[b]["comps"].items())
                     for v in [c["value"]] if qn in _norm(v) and (b, r, v) not in hold]
            if other:
                b, r, v = other[0]
                fails.append("%s is named the %s %s; the %s is %s:%s (%s), and %s is not" % (
                    p, " ".join(q), noun, " ".join(q), b, r, v[:70], p))
                continue
        notes.append("%s as %s%s" % (p, (" ".join(q) + " ") if q else "", noun))
    judged = [(p, role, tg, "list") for p, role, tg in rail_lists(s, parts)] + \
             [(p, "converter", tg, noun) for p, noun, tg in target_roles(s, parts)] if ROLE_TESTS["rails"] else []
    for p, role, targets, how in judged:
        for b in (boards or list(part_boards(p, nls)) or ["A"]):
            for label, net in targets:
                des = _designators_for(nls, b, net, role)
                wrong = [(r, v) for r, v in des if p.split(" ", 1)[-1] not in v]
                if wrong:
                    fails.append("%s is given the %s %s; %s" % (p, label, "monitor" if role == "monitor" else "converter",
                                 "; ".join("%s:%s is %s" % (b, r, v[:50]) for r, v in wrong)))
                elif des:
                    notes.append("%s on the %s: %s" % (p, label, ",".join(r for r, _v in des)))
    for k in ok:
        if k not in ["%s %s" % (p, n) for p, _q, n in role_phrases(s, parts)]: fails.append("roles_ok names %s, which the sentence does not" % k)
    return fails, notes


def check_gens(s, nm, nls, j):
    fails, notes = [], []
    if j.get("cite_ok"): return fails, ["citations judged: %s" % j["cite_ok"]]
    for g, spec in nm["gens"]:
        if not spec: continue
        rel = "v2/ecad/tools/" + g
        after = s[s.find(g) + len(g):]
        md = re.match(r"`?(?::\d+(?:-\d+)?`?(?:,|,? and)? ?`?)*\s*at `?([0-9a-f]{7,40})`?", after)
        commit = md.group(1) if md else None
        text = gen_text(rel, commit)
        if text is None:
            fails.append("%s at %s: not readable" % (g, commit)); continue
        want = set(nm["refs"]) | set(nm["nets"]) | set(j.get("cite_words", ()))
        for part in re.findall(r"(\d+)(?:-(\d+))?", spec):
            a = int(part[0]); b = int(part[1] or part[0])
            seg = "\n".join(text[a - 1:b])
            hit = sorted(w for w in want if re.search(r"(?<![\w])%s(?![\w])" % re.escape(w), seg))
            if not hit:
                fails.append("%s:%s%s holds none of %s" % (g, part[0] + ("-" + part[1] if part[1] else ""),
                                                           " at " + commit if commit else " (undated, this commit)", ",".join(sorted(want))[:120]))
            else:
                notes.append("%s:%s%s holds %s" % (g, part[0] + ("-" + part[1] if part[1] else ""), " at " + commit if commit else "", ",".join(hit[:6])))
    return fails, notes


_ROWS = {}
NUMS = L.NUMW.split("|")
ABSENT = L.ABSENT


def absent_rule(rel, s, j):
    """Round 3 (check-s122-2, B1): in a baselined document, a statement that something is absent, owed, not drawn or not
    connected as generated is judged against the netlists, TRUE or BASELINE, never NOT DERIVABLE. A NOT DERIVABLE
    judgement of such a sentence must bind every occurrence of those words to a phrase of the sentence (`absent_ok`, a
    dict: the phrase, quoted from the sentence, to why it is not a statement about the generated circuit)."""
    if rel not in L.BASELINED or j["v"] != "N": return []
    ok = j.get("absent_ok") or {}
    out = []
    for m in ABSENT.finditer(s):
        if not any(k in s and s.index(k) <= m.start() and m.end() <= s.index(k) + len(k) and ok[k] for k in ok):
            out.append("'%s' (at %d) states what is absent or owed; judged TRUE or BASELINE, or its phrase bound in absent_ok"
                       % (m.group(0), m.start()))
    return out


def count_rule(phrases, j):
    """Every count of parts a sentence states is covered, and the cover is checked (round 3, check-s122-2 m8: two
    excuses named the wrong thing and `counts_ok` was not read by the script). With one count: a count assertion (#)
    of the same number, or a `counts_ok` entry. With several: `counts_ok` is a dict keyed by a piece of each count
    phrase. An entry reading 'asserted: <assertion>' must name one of the judgement's own count assertions whose
    number is the phrase's; any other entry is a reason bound to that phrase, and it must name what the phrase counts
    (the phrase's noun), so an excuse cannot be filed against another count of the same sentence."""
    if not phrases: return []
    ok = j.get("counts_ok")
    a = list(j.get("a", ()))
    num = lambda p: NUMS.index(p.split()[0].lower()) + 2
    noun = lambda p: re.sub(r"(es|s)$", "", p.split()[-1].lower()) if p.split()[-1].lower() not in ("switches", "fuses") \
        else p.split()[-1].lower()[:-2]
    anum = lambda x: int(x.rsplit("=", 1)[1]) if re.match(r"^[ABCDEP](@[0-9a-f]+)?:#", x) and "=" in x else None
    out = []
    if isinstance(ok, str):
        if len(phrases) > 1:
            return ["one reason for several counts (%s): counts_ok must name each" % "; ".join(phrases)]
        ok = {phrases[0]: ok}
    ok = ok or {}
    for p in phrases:
        keys = [k for k in ok if k.lower() in p.lower()]
        if not keys:
            if len(phrases) == 1 and any(anum(x) == num(p) for x in a): continue
            out.append("no counts_ok entry for '%s'" % p)
            continue
        v = ok[keys[0]]
        if v.startswith("asserted: "):
            x = v[len("asserted: "):]
            if x not in a: out.append("'%s' names an assertion the judgement does not make (%s)" % (p, x))
            elif anum(x) != num(p): out.append("'%s' is covered by %s, whose number is not %d" % (p, x, num(p)))
        elif noun(p) not in v.lower():
            out.append("the reason for '%s' does not name what it counts (%s): %s" % (p, noun(p), v))
    return out


def status_rows():
    """The row keys (DC-nn) of the status page's table of CONOPS's current circuit values."""
    if "rows" not in _ROWS:
        txt = L.read("v2/docs/handover/DEFINITION-STATUS.md")
        _ROWS["rows"] = set(re.findall(r"(?m)^\| (DC-\d+) \|", txt))
    return _ROWS["rows"]


def check_figs(s, j):
    """Round 6: a judgement that declares `figures_ok` is held to it: each key is a phrase of the sentence, each value an
    'asserted: X' naming one of its own assertions, and no figure-and-unit token of the sentence is left uncovered
    (figures_uncovered). A judgement without `figures_ok` is not judged here: close_s122.py's scan asks it only of the
    lines of its closing list."""
    fig = j.get("figures_ok")
    if not fig: return [], []
    fails, notes = [], []
    for k, x in fig.items():
        if k not in s: fails.append("figures_ok names %r, which the sentence does not" % k); continue
        if not x.startswith("asserted: ") or x[len("asserted: "):] not in j.get("a", ()):
            fails.append("figures_ok: %r names no own assertion (%s)" % (k, x)); continue
        notes.append("%s by %s" % (k, x[len("asserted: "):]))
    un = figures_uncovered(s, j)
    if un: fails.append("figures no assertion covers: %s" % ", ".join(un))
    return fails, notes


def judge(inv, nls):
    rows = []
    for sid, rel, key, kind, line, s, nm in inv:
        d = L.sid_digest(s)
        j = J.J.get(d)
        if j is None:
            rows.append((sid, d, "UNJUDGED", ["no judgement for this text"], s)); continue
        f1, n1 = check_names(s, nm, nls, j)
        f5, n5 = check_parts(s, nm, nls, j)
        f6, n6 = check_roles(s, nm, nls, j)
        f5, n5 = f5 + f6, n5 + n6      # round 5: a part in a role it does not hold counts as a part failure
        f2, n2 = check_gens(s, nm, nls, j)
        f3, n3 = [], []
        for a in j.get("a", ()):
            ok, msg = run_assert(a, nls)
            (n3 if ok else f3).append(msg)
        f7, n7 = check_figs(s, j)
        f3 = f3 + f7
        v = j["v"]
        why = j.get("why", "")
        f4 = []
        f4 += count_rule(nm.get("counts") or [], j)
        # round 3 (check-s122-2, B1): a baselined document's statement that something is absent, owed, not drawn or not
        # connected is a statement about the circuit; it is judged against the netlists, TRUE or BASELINE, never NOT
        # DERIVABLE
        f4 += absent_rule(rel, s, j)
        kept_ok = None
        if v == "B":
            if rel not in L.BASELINED: f3.append("BASELINE is only for a baselined document")
            kept = j.get("kept") if isinstance(j.get("kept"), list) else [j.get("kept")]
            kept_ok = all(k in status_rows() for k in kept)
            if not kept_ok: f3.append("the status page keeps no row %s for it" % ", ".join(k for k in kept if k not in status_rows()))
        if v == "N" and f5:
            # round 4: NOT DERIVABLE (HISTORY among them) never excuses a part number the netlists do not carry; the
            # judgement names each in parts_ok, a history one by an assertion of the generator at its date
            f4 = f4 + ["a part number not on the netlists needs its parts_ok entry: " + "; ".join(f5)]
        if v == "S":
            verdict = "STALE"
        elif f4:
            verdict = "UNJUDGED"
        elif v == "B":
            # a baseline value may name parts or lines the netlists and generators no longer carry: that is why it is kept
            # on the status page; the names and citation checks are reported, not held against it. Its assertions, which
            # state the current value, are (round 3: any failing one makes it STALE)
            verdict = "BASELINE" if kept_ok and not f3 else "STALE"
        elif f1 or f2 or f3 or f5:
            verdict = "STALE" if v == "T" else "NOT DERIVABLE"
        else:
            verdict = {"T": "TRUE", "N": "NOT DERIVABLE"}[v]
        det = []
        if why: det.append("judgement: " + why)
        if v == "B": det.append("baseline value (CONOPS.md's head and handover/DEFINITION-STATUS.md): its current value is "
                                "kept on the status page, row %s, which this script judges directly"
                                % (", ".join(j["kept"]) if isinstance(j.get("kept"), list) else j.get("kept")))
        if f1 or f2 or f3 or f4 or f5: det += ["FAILS: " + x for x in f1 + f2 + f3 + f4 + (f5 if v != "N" else [])]
        det.append("names looked up: %d parts, %d nets%s" % (len(nm["refs"]), len(nm["nets"]), ("; " + "; ".join(n1)) if n1 else ""))
        if n2: det.append("citations: " + "; ".join(n2))
        if nm.get("parts"): det.append("part numbers (%d): %s" % (len(nm["parts"]), "; ".join(n5) or "none judged"))
        if n3: det.append("asserted (%d): " % len(n3) + "; ".join(n3))
        if n7: det.append("figures (%d): " % len(n7) + "; ".join(n7))
        rows.append((sid, d, verdict, det, s))
    return rows


def render(rows, nls):
    out = ["# Stream s122 verdicts: every inventoried sentence judged against the committed netlists and the generators.",
           "# Written by v2/docs/records/s122/verdicts.py (checks: names, citations, assertions; see its docstring).",
           "# Netlists: " + ", ".join("%s %s@%s" % (k, nl["path"], nl["sha16"]) for k, nl in sorted(nls.items())),
           "# Documents: " + ", ".join("%s@%s" % (rel, L.sha16(rel)) for rel, _s in L.SCOPE), ""]
    counts = {}
    for sid, d, v, det, s in rows:
        doc = sid.split("#")[0]
        c = counts.setdefault(doc, {"sentences": 0, "TRUE": 0, "STALE": 0, "BASELINE": 0, "NOT DERIVABLE": 0, "UNJUDGED": 0,
                                    "asserted": 0})
        c["sentences"] += 1; c[v] += 1
        c["asserted"] += sum(int(re.match(r"asserted \((\d+)\)", x).group(1)) for x in det if x.startswith("asserted ("))
        out.append("%s [%s] %s" % (sid, d, v))
        out.append("    " + s)
        for x in det: out.append("    " + x)
    out.append("")
    out.append("# counts per document (sentences, TRUE, STALE, BASELINE, NOT DERIVABLE, UNJUDGED, assertions evaluated)")
    tot = {"sentences": 0, "TRUE": 0, "STALE": 0, "BASELINE": 0, "NOT DERIVABLE": 0, "UNJUDGED": 0, "asserted": 0}
    for rel, _s in L.SCOPE:
        doc = os.path.basename(rel)
        c = counts.get(doc, {k: 0 for k in tot})
        for k in tot: tot[k] += c[k]
        out.append("%s: %d sentences, %d TRUE, %d STALE, %d BASELINE, %d NOT DERIVABLE, %d UNJUDGED, %d assertions" % (
            doc, c["sentences"], c["TRUE"], c["STALE"], c["BASELINE"], c["NOT DERIVABLE"], c["UNJUDGED"], c["asserted"]))
    out.append("total: %d sentences, %d TRUE, %d STALE, %d BASELINE, %d NOT DERIVABLE, %d UNJUDGED, %d assertions" % (
        tot["sentences"], tot["TRUE"], tot["STALE"], tot["BASELINE"], tot["NOT DERIVABLE"], tot["UNJUDGED"], tot["asserted"]))
    return "\n".join(out) + "\n", tot


def main():
    nls = L.netlists()
    inv = L.inventory(nls)
    rows = judge(inv, nls)
    text, tot = render(rows, nls)
    if "--stdout" in sys.argv:
        sys.stdout.write(text)
    else:
        open(os.path.join(HERE, "verdicts.out"), "w", encoding="utf-8").write(text)
        print("verdicts.py: %d sentences: %d TRUE, %d STALE, %d BASELINE, %d NOT DERIVABLE, %d UNJUDGED" % (
            tot["sentences"], tot["TRUE"], tot["STALE"], tot["BASELINE"], tot["NOT DERIVABLE"], tot["UNJUDGED"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
