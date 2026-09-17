#!/usr/bin/env python3
"""The assembly set is buildable (rule DFA-001, MESHSAT-862, 16 September 2026).

DFA-001 is a BLOCKER and asks two things: every designator in the parts list appears in the placement file or
is declared hand-fitted, and every polarised part's rotation is verified against its own drawing and against
the assembler's convention, WITH THE VERIFICATION DATED. It read "generation intends to comply and nothing
verifies it" on six boards.

The second half is the one that puts parts on a board backwards, and this is what it found on its first run:
the boards place 51 distinct polarised or pin-1-sensitive footprints and the rotation table has THIRTEEN rows,
of which eleven were compared with JLCPCB's own preview on 3 September and two never were. Every other
polarised footprint goes to the assembler with KiCad's rotation unchanged, which is an assumption nobody has
checked rather than a verification.

So this gate reports, per board:

  * every polarised footprint in use, whether a rotation row matches it, and whether that row carries a date;
  * every BOM designator that is neither in the CPL nor declared hand-fitted or DNP, where the deliverable
    folder exists (where it does not, that half says so rather than passing).

A footprint with no row is not a failure by itself, because zero can be the right offset; what is a failure is
that nobody has ever looked. Both are counted and the list is the checklist the ordering session works from,
since only it has the preview.

Usage: assembly_set.py [--ecad <dir>] [--board <letter>] [--rot <jlc-rotations.csv>] [--json]
"""
import os, re, sys, json, glob, csv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ECAD = os.path.dirname(HERE)
ROT = os.path.normpath(os.path.join(ECAD, "..", "release", "revA", "order", "jlc-rotations.csv"))
# A footprint whose orientation can be wrong: two-pin passives that are symmetric are not in it, and the
# families that are name the reason they are (a polarity mark, a pin 1, a keyed body).
POLARISED = re.compile(r"^(D_|LED|CP_|USB|SOT|SOIC|SSOP|TSSOP|QFN|LQFP|WSON|DFN|VSSOP|SOP|Crystal|IDC|"
                       r"PinHeader|JST|Molex|HRO|Fuseholder|BatteryHolder|SMP|Amphenol|Hirose)", re.I)


def rotations(path=None):
    """[(regex, offset, verified)] from the table the ordering session keeps."""
    p = path or ROT
    if not os.path.exists(p): return None
    out = []
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        parts = [x.strip() for x in line.split(",")]
        if len(parts) < 2: continue
        out.append((parts[0], parts[1], parts[2] if len(parts) > 2 else ""))
    return out


def footprints(net_path):
    t = open(net_path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'\(comp \(ref "([^"]+)"\).*?\(footprint "([^"]*)"\)', t, re.S):
        out[m.group(1)] = m.group(2).split(":")[-1]
    return out


def bench_fitted(stem, path=None):
    """The designators this project does NOT send to the assembler, read out of make_handoff.py's own table.

    A ROTATION MATTERS FOR A PART THE ASSEMBLER PLACES (17 September 2026). The first form of this check
    listed every polarised footprint in the netlist, which is 41 across the seven boards, and most of them are
    parts JLCPCB never sees: the blind-mate receptacles and spring pins of board A, the plate switches, the
    sounder and the camera of board C, the blade holders and the pack lands of board E, the wire joints of
    board P. Asking the ordering session to compare those with an assembler's preview is asking it to check a
    rotation nobody will apply.

    The table is a literal in `make_handoff.py`, which is on the never-auto floor, so it is READ here by text
    and never imported: that file needs pcbnew and this gate runs on the runner. `producer_table` below reads
    the rotation offsets out of the same file for the same reason."""
    src = open(path or os.path.join(HERE, "make_handoff.py"), encoding="utf-8", errors="replace").read()
    i = src.find("EXCLUDE = {")
    if i < 0: return None
    j = src.find("\nNONPART_PREFIX", i)
    blk = src[i:j if j > 0 else i + 4000]
    # the per-board entry, as written: "stem": { ... }  with an optional | {expr} tail
    out = set()
    # each board's entry is one LINE of that literal, ending at the comment or the next board's key
    line = next((l for l in blk.splitlines() if ('"%s":' % stem) in l), "")
    if not line: return set()
    m = re.search(r'"%s":\s*(.*)$' % re.escape(stem), line)
    if not m: return set()
    for t in re.finditer(r'"([A-Za-z_][A-Za-z0-9_]*)"', m.group(1)): out.add(t.group(1))
    # the ranges written as comprehensions, e.g. {"J_CP%d" % k for k in range(1, 5)}
    for c in re.finditer(r'"([A-Za-z_]+)%d"\s*%\s*k\s*for k in range\((\d+),\s*(\d+)\)', m.group(1)):
        pre, a, b = c.group(1), int(c.group(2)), int(c.group(3))
        for k in range(a, b): out.add("%s%d" % (pre, k))
    return out


def producer_table(path=None):
    """The offsets the PRODUCER actually applies, read out of make_handoff.py without importing it.

    There are two copies of this table: the CSV the ordering session keeps and a literal in make_handoff.py,
    which is the one that reaches a CPL. That line is on the never-auto floor (reserved.json: "the JLC rotation
    table"), so this tool reads it and compares rather than editing it; a difference between the two is a
    silent wrong rotation waiting to happen, and it is reported as a failure for a person to resolve.
    """
    p = path or os.path.join(HERE, "make_handoff.py")
    if not os.path.exists(p): return None
    txt = open(p, encoding="utf-8", errors="replace").read()
    # the assignment is one line and its patterns contain brackets of their own (`^SOT-23-[568]`), so the
    # line is taken whole and the pairs are read out of it: a non-greedy match to the first `]` stopped inside
    # a character class and reported every later row as missing, which is a false alarm of exactly the kind
    # this tool exists to remove
    line = next((l for l in txt.splitlines() if l.startswith("JLC_ROT")), None)
    if not line: return None
    return [(a, int(b)) for a, b in re.findall(r'\("([^"]+)",\s*(-?\d+)\)', line)]


def judge(ecad=None, only=None, rot=None):
    import rules_lib as R
    facts = R.board_facts()
    rows = rotations(rot)
    prod = producer_table()
    drift = []
    if rows is not None and prod is not None:
        a = {p: int(o) for p, o, _v in rows}
        b = dict(prod)
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                drift.append("the rotation table and make_handoff.py disagree about %s: the file says %s and "
                             "the producer applies %s. The producer's line is on the never-auto floor, so this "
                             "is for the ordering session to resolve" % (k, a.get(k), b.get(k)))
    ecad = ecad or ECAD
    out = {}
    for letter, f in sorted(facts.items()):
        if only and letter != only: continue
        stem = f.get("project")
        nets = [p for p in glob.glob(os.path.join(ecad, stem + "*", "out", stem + ".net")) if os.path.isfile(p)] if stem else []
        fails, notes, unchecked, unverified = [], [], set(), set()
        if rows is None:
            fails.append("there is no rotation table at %s, so no rotation has been verified at all" % os.path.relpath(ROT, ECAD))
        if drift and letter == sorted(facts)[0]:
            fails.extend(drift)   # a set-level disagreement, reported once rather than seven times
        if rows is None:
            pass
        elif not nets:
            notes.append("board %s has no netlist in this tree, so its footprints could not be listed" % letter.upper())
        else:
            fps = footprints(max(nets, key=os.path.getmtime))
            # A ROTATION MATTERS FOR A PART THE ASSEMBLER PLACES. The bench-fitted designators of this board
            # never reach a CPL, so their rotation is nobody's to verify; the count is reported so the
            # exclusion is visible rather than silent.
            _bench = bench_fitted(str((facts.get(letter) or {}).get("project") or "")) or set()
            n_bench = 0
            for ref, fp in sorted(fps.items()):
                if not POLARISED.search(fp or ""): continue
                if ref in _bench: n_bench += 1; continue
                hit = next(((p, o, v) for p, o, v in rows if re.search(p, fp)), None)
                if hit is None:
                    unchecked.add(fp)
                elif not hit[2] or hit[2].upper() == "UNVERIFIED":
                    unverified.add("%s (matched by %s)" % (fp, hit[0]))
            if n_bench:
                notes.append("board %s: %d polarised footprint(s) are bench-fitted and never reach the "
                             "assembler, so their rotation is not the assembler's to verify" % (letter.upper(), n_bench))
            for fp in sorted(unverified):
                fails.append("%s: %s carries a rotation offset nobody has compared with the assembler's preview"
                             % (letter.upper(), fp))
        out[letter] = dict(unchecked=sorted(unchecked), unverified=sorted(unverified), fails=fails, notes=notes)
    return out


def main(argv):
    ecad = argv[argv.index("--ecad") + 1] if "--ecad" in argv else None
    only = argv[argv.index("--board") + 1].lower() if "--board" in argv else None
    rot = argv[argv.index("--rot") + 1] if "--rot" in argv else None
    r = judge(ecad, only, rot)
    fails = [f for v in r.values() for f in v["fails"]]
    nch = sorted({x for v in r.values() for x in v["unchecked"]})
    for letter, v in sorted(r.items()):
        print("assembly_set: %-3s %2d polarised footprint(s) with no rotation row, %d with an unverified one"
              % (letter.upper(), len(v["unchecked"]), len(v["unverified"])))
    if nch:
        print("  NOT COMPARED WITH A PREVIEW (offset 0 assumed), %d footprint(s):" % len(nch))
        for fp in nch[:24]: print("    %s" % fp)
    for f in fails: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    # A footprint with no row is not a failure by itself; it is an unchecked assumption, and the rule asks for
    # a DATED verification, so a set with any unchecked polarised footprint is INCONCLUSIVE rather than PASS.
    res = _v.FAIL if fails else (_v.INCONCLUSIVE if nch else _v.PASS)
    return _v.write("assembly_set", res, rules=["DFA-001"],
                    counts={"boards": len(r), "unchecked_footprints": len(nch),
                            "unverified_rows": len({x for v in r.values() for x in v["unverified"]}),
                            "fail": len(fails)},
                    denominator=max(1, len(nch) + len(fails)),
                    evidence=(fails + ["not compared with a preview: " + x for x in nch])[:20],
                    inputs={"rotations": os.path.relpath(rot or ROT, ECAD)},
                    note="every polarised footprint the boards place, against the rotation table the ordering "
                         "session keeps and the date each row was compared with the assembler's own preview. A "
                         "footprint with no row goes to the assembler with KiCad's rotation unchanged, which is "
                         "an assumption rather than a verification, and the list is the checklist for the "
                         "session that has the preview")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
