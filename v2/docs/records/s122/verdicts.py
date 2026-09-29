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
A judgement is keyed by the sentence's digest (sha256/10 of its whitespace-normalised text), so a corrected sentence is a
new text that needs its own judgement, and a line shift moves nothing.

Writes only `verdicts.out` beside this file (or prints with --stdout). Exit 0; the counts are in the last lines.
Run: python3 verdicts.py [--stdout]."""
import os, re, subprocess, sys

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
        import yaml
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


def judge(inv, nls):
    rows = []
    for sid, rel, key, kind, line, s, nm in inv:
        d = L.sid_digest(s)
        j = J.J.get(d)
        if j is None:
            rows.append((sid, d, "UNJUDGED", ["no judgement for this text"], s)); continue
        f1, n1 = check_names(s, nm, nls, j)
        f2, n2 = check_gens(s, nm, nls, j)
        f3, n3 = [], []
        for a in j.get("a", ()):
            ok, msg = run_assert(a, nls)
            (n3 if ok else f3).append(msg)
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
        if v == "S":
            verdict = "STALE"
        elif f4:
            verdict = "UNJUDGED"
        elif v == "B":
            # a baseline value may name parts or lines the netlists and generators no longer carry: that is why it is kept
            # on the status page; the names and citation checks are reported, not held against it. Its assertions, which
            # state the current value, are (round 3: any failing one makes it STALE)
            verdict = "BASELINE" if kept_ok and not f3 else "STALE"
        elif f1 or f2 or f3:
            verdict = "STALE" if v == "T" else "NOT DERIVABLE"
        else:
            verdict = {"T": "TRUE", "N": "NOT DERIVABLE"}[v]
        det = []
        if why: det.append("judgement: " + why)
        if v == "B": det.append("baseline value (CONOPS.md's head and handover/DEFINITION-STATUS.md): its current value is "
                                "kept on the status page, row %s, which this script judges directly"
                                % (", ".join(j["kept"]) if isinstance(j.get("kept"), list) else j.get("kept")))
        if f1 or f2 or f3 or f4: det += ["FAILS: " + x for x in f1 + f2 + f3 + f4]
        det.append("names looked up: %d parts, %d nets%s" % (len(nm["refs"]), len(nm["nets"]), ("; " + "; ".join(n1)) if n1 else ""))
        if n2: det.append("citations: " + "; ".join(n2))
        if n3: det.append("asserted (%d): " % len(n3) + "; ".join(n3))
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
