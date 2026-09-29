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
                    r"(?P<vref>[\w#+-]+)~(?P<val>.+)|(?P<nnet>[^>\s]+)>(?P<members>[\w,#+-]+)|(?P<eref>[\w#+-]+)\?)$")
GASSERT = re.compile(r"^G@(?P<c>[0-9a-f]+|HEAD):(?P<f>[\w./-]+):(?P<a>\d+)(?:-(?P<b>\d+))?~(?P<w>.+)$")
DOCASSERT = re.compile(r"^DOC:(?P<f>[\w./-]+)~(?P<w>.+)$")
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


def run_assert(a, nls):
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
    nv = re.match(r"^([ABCDEP]):!~(.+)$", a.strip())
    if nv:
        hits = sorted(r for r in nls[nv.group(1)]["comps"] if nv.group(2) in L.TX.value(nls[nv.group(1)], r))
        return not hits, "board %s has no part whose value holds %r (found: %s)" % (nv.group(1), nv.group(2), ",".join(hits) or "none")
    sm = re.match(r"^SHA:([ABCDEP])=([0-9a-f]+)$", a.strip())
    if sm:
        got = nls[sm.group(1)]["sha16"]
        return got == sm.group(2), "board %s netlist sha256/16 %s (read: %s)" % (sm.group(1), sm.group(2), got)
    dm = DOCASSERT.match(a.strip())
    if dm:
        txt = " ".join(open(os.path.join(L.TOP, dm.group("f")), encoding="utf-8").read().split())
        ok = all(" ".join(w.split()) in txt for w in dm.group("w").split("|"))
        return ok, "%s says %r" % (dm.group("f"), dm.group("w")[:80])
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
        if v == "S":
            verdict = "STALE"
        elif f1 or f2 or f3:
            verdict = "STALE" if v == "T" else "NOT DERIVABLE"
        else:
            verdict = {"T": "TRUE", "N": "NOT DERIVABLE"}[v]
        det = []
        if why: det.append("judgement: " + why)
        if f1 or f2 or f3: det += ["FAILS: " + x for x in f1 + f2 + f3]
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
        c = counts.setdefault(doc, {"sentences": 0, "TRUE": 0, "STALE": 0, "NOT DERIVABLE": 0, "UNJUDGED": 0, "asserted": 0})
        c["sentences"] += 1; c[v] += 1
        c["asserted"] += sum(int(re.match(r"asserted \((\d+)\)", x).group(1)) for x in det if x.startswith("asserted ("))
        out.append("%s [%s] %s" % (sid, d, v))
        out.append("    " + s)
        for x in det: out.append("    " + x)
    out.append("")
    out.append("# counts per document (sentences, TRUE, STALE, NOT DERIVABLE, UNJUDGED, assertions evaluated)")
    tot = {"sentences": 0, "TRUE": 0, "STALE": 0, "NOT DERIVABLE": 0, "UNJUDGED": 0, "asserted": 0}
    for rel, _s in L.SCOPE:
        doc = os.path.basename(rel)
        c = counts.get(doc, {k: 0 for k in tot})
        for k in tot: tot[k] += c[k]
        out.append("%s: %d sentences, %d TRUE, %d STALE, %d NOT DERIVABLE, %d UNJUDGED, %d assertions" % (
            doc, c["sentences"], c["TRUE"], c["STALE"], c["NOT DERIVABLE"], c["UNJUDGED"], c["asserted"]))
    out.append("total: %d sentences, %d TRUE, %d STALE, %d NOT DERIVABLE, %d UNJUDGED, %d assertions" % (
        tot["sentences"], tot["TRUE"], tot["STALE"], tot["NOT DERIVABLE"], tot["UNJUDGED"], tot["asserted"]))
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
        print("verdicts.py: %d sentences: %d TRUE, %d STALE, %d NOT DERIVABLE, %d UNJUDGED" % (
            tot["sentences"], tot["TRUE"], tot["STALE"], tot["NOT DERIVABLE"], tot["UNJUDGED"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
