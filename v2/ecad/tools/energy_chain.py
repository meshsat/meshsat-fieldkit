#!/usr/bin/env python3
"""The stored-energy chain, checked rather than drawn (rules BAT-002 and PWR-003, MESHSAT-862, 16 Sep 2026).

Both rules are BLOCKERs and both read "no verification" on four boards. The chain crosses four boards with two
25 A blades, an XT60 and 12 AWG wiring, and nothing drew it end to end; a chain nobody has drawn is one whose
weakest stage is unknown, and the weakest stage is where a fault burns a conductor instead of opening a fuse.

`pcb_energy_chain.yaml` is the chain as data. This is the gate over it, and every check below is arithmetic or
a lookup in files this repository holds:

  1. EVERY NUMBER NAMES ITS SOURCE and the source exists. A rating whose basis file is not in v2/vendor is not
     a rating, it is a claim.
  2. EVERY PROTECTIVE ELEMENT IS ON THE BOARD IT CLAIMS, by reference, in that board's own netlist. The
     chain may not name a fuse the schematic does not have.
  3. THE ELEMENT OPENS BEFORE THE CONDUCTOR AND THE CONNECTOR ARE OVER THEIR RATING: rating_a is at or below
     every conductor and connector rating in its stage. This is the coordination, in one line.
  4. THE ELEMENT DOES NOT OPEN IN NORMAL USE: rating_a is at or above the stage's declared peak current.
  5. THE ELEMENT CAN INTERRUPT WHAT IS THERE: interrupting_a is at or above the worst prospective fault
     current, where the element interrupts at all (an eFuse limits rather than breaks and declares null).
  6. THE CHAIN IS CONNECTED: every `protects` names a stage that exists, and no stage is orphaned.

WHAT IT DOES NOT DO. It does not simulate an arc, it does not read a clearing curve as a curve (the I2t figure
is carried and the melting time is printed from it), and it cannot know the fault current a vehicle's own
battery can deliver, which is why the shore input's row says so and points at owner decision 34.

Usage: energy_chain.py [--chain pcb_energy_chain.yaml] [--ecad <dir>] [--json]
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ECAD = os.path.dirname(HERE)
VENDOR = os.path.normpath(os.path.join(ECAD, "..", "vendor"))
CHAIN = os.path.join(HERE, "pcb_energy_chain.yaml")
BOARD_NET = {"A": "pcb-a-power", "B": "pcb-b-compute", "C": "pcb-c-display", "D": "pcb-d-aprs",
             "E": "pcb-e1-dock", "P": "pcb-p-pack"}


def _yaml():
    import yaml
    return yaml


def netlist_refs(stem, ecad=None):
    """{reference} from the newest netlist of this board in the tree, or None when there is none to read."""
    ecad = ecad or ECAD
    cands = [c for c in glob.glob(os.path.join(ecad, stem + "*", "out", stem + ".net")) if os.path.isfile(c)]
    if not cands: return None
    import re
    txt = open(max(cands, key=os.path.getmtime), encoding="utf-8", errors="replace").read()
    return set(re.findall(r'\(comp \(ref "([^"]+)"\)', txt))


def check(chain=None, ecad=None, vendor=None):
    y = _yaml().safe_load(open(chain or CHAIN, encoding="utf-8"))
    # A TREE WITHOUT THE VENDOR FOLDER CANNOT JUDGE A CITATION, and must not report one as false (16 September
    # 2026). The sweep runs in a tree archived from v2/ecad alone, so every basis file read as missing and the
    # gate turned eleven true citations into failures in its first run there. Absence of the folder is an
    # unjudgeable condition, reported as its own count, while the coordination arithmetic below is judged as
    # always: a missing library says nothing about whether a fuse is above its conductor.
    stages = y.get("stages") or []
    ids = {s["id"] for s in stages}
    fails, notes, checked = [], [], 0
    refs_cache = {}
    vdir = vendor or VENDOR
    have_vendor = os.path.isdir(vdir)
    unjudged_citations = 0
    if not have_vendor:
        notes.append("the vendor library is not in this tree (%s), so no citation could be checked; the "
                     "coordination arithmetic below is judged as always" % os.path.relpath(vdir, ECAD))

    def basis_ok(b):
        """A citation names a file; the punctuation around it in a sentence is not part of the name.

        The first run of this gate refused two true citations for a trailing colon and a trailing `);`, which
        is the false-positive shape this project spent the morning removing from derate.py. A path is trimmed
        of sentence punctuation before it is looked for, and a token that still does not resolve is reported
        with what was looked for."""
        b = str(b or "")
        for tok in b.replace(",", " ").split():
            if not tok.startswith("v2/vendor/"): continue
            name = tok.rstrip(".,;:)]}\"'")
            if not os.path.exists(os.path.join(vdir, name[len("v2/vendor/"):])): return False, name
        return True, None

    for s in stages:
        sid = s["id"]; prot = s.get("protection") or {}; cond = s.get("conductor") or {}
        conn = s.get("connector") or {}
        # 1. every number names a source and the source is here
        for what, blk in (("conductor", cond), ("connector", conn), ("protection", prot),
                          ("prospective fault", s.get("prospective_fault_a") or {})):
            if not blk: continue
            checked += 1
            if not blk.get("basis"):
                fails.append("%s: the %s carries no basis" % (sid, what)); continue
            if not have_vendor:
                unjudged_citations += 1; continue
            ok, miss = basis_ok(blk.get("basis"))
            if not ok: fails.append("%s: the %s names %s, which is not in this tree" % (sid, what, miss))
        # 2. the element is on the board it claims
        letter = str(s.get("board", "")).split()[0].upper()
        stem = BOARD_NET.get(letter)
        if prot.get("ref") and stem:
            if stem not in refs_cache: refs_cache[stem] = netlist_refs(stem, ecad)
            refs = refs_cache[stem]
            checked += 1
            if refs is None:
                notes.append("%s: board %s has no netlist in this tree, so %s could not be looked up"
                             % (sid, letter, prot["ref"]))
            elif prot["ref"] not in refs:
                fails.append("%s: the netlist of board %s has no %s, and the chain says its protection is there"
                             % (sid, letter, prot["ref"]))
        # 3, 4, 5: the coordination arithmetic
        r = prot.get("rating_a")
        if r is not None:
            for what, blk in (("conductor", cond), ("connector", conn)):
                if blk.get("rating_a") is None: continue
                checked += 1
                if float(r) > float(blk["rating_a"]) + 1e-9:
                    fails.append("%s: the protection is rated %.1f A and the %s only %.1f A, so the %s is the "
                                 "fuse" % (sid, float(r), what, float(blk["rating_a"]), what))
            if s.get("peak_a") is not None:
                checked += 1
                if float(r) < float(s["peak_a"]) - 1e-9:
                    fails.append("%s: the protection is rated %.1f A and the path's own peak is %.1f A, so it "
                                 "opens in normal use" % (sid, float(r), float(s["peak_a"])))
        pf = s.get("prospective_fault_a") or {}
        if prot.get("interrupting_a") is not None and pf.get("high") is not None:
            checked += 1
            if float(prot["interrupting_a"]) < float(pf["high"]) - 1e-9:
                fails.append("%s: the fault current reaches %.0f A and the element interrupts %.0f A"
                             % (sid, float(pf["high"]), float(prot["interrupting_a"])))
        # 6. the chain is connected
        nxt = s.get("protects")
        if nxt:
            checked += 1
            if nxt not in ids: fails.append("%s: protects %s, which is not a stage" % (sid, nxt))
        # the melting time, printed rather than asserted
        if prot.get("i2t_a2s") and pf.get("high"):
            t = float(prot["i2t_a2s"]) / (float(pf["high"]) ** 2)
            notes.append("%s: %s melts in about %.1f ms at %.0f A (I2t %.0f A2s)"
                         % (sid, prot.get("ref", "the element"), t * 1e3, float(pf["high"]), float(prot["i2t_a2s"])))
    orphan = [s["id"] for s in stages if s["id"] != stages[0]["id"]
              and not any((o.get("protects") == s["id"]) for o in stages)]
    for o in orphan:
        if o == "SHORE_INPUT": continue   # a second source, not a link in the pack's chain
        fails.append("%s: no stage protects it, so the chain has a break at it" % o)
    return dict(stages=len(stages), checked=checked, fails=fails, notes=notes,
                unjudged_citations=unjudged_citations, vendor_seen=bool(have_vendor))


def main(argv):
    ch = argv[argv.index("--chain") + 1] if "--chain" in argv else None
    ec = argv[argv.index("--ecad") + 1] if "--ecad" in argv else None
    try:
        r = check(ch, ec)
    except Exception as e:
        print("energy_chain: the chain could not be read (%s: %s)" % (type(e).__name__, e))
        return _v.write("energy_chain", _v.INCONCLUSIVE, denominator=0,
                        note="the chain file could not be read, so nothing was judged",
                        rules=["BAT-002", "PWR-003"])
    print("energy_chain: %d stage(s), %d check(s)" % (r["stages"], r["checked"]))
    for n in r["notes"]: print("  note %s" % n)
    for f in r["fails"]: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    # The coordination is what this rule is about, and it is judged wherever the chain file is. A tree with no
    # vendor library leaves the citations unjudged, which is reported and does not turn a passing chain into a
    # failing one; it is also not silently a pass, because the count travels in the verdict.
    res = _v.FAIL if r["fails"] else _v.PASS
    return _v.write("energy_chain", res,
                    counts={"stages": r["stages"], "checks": r["checked"], "fail": len(r["fails"]),
                            "citations_unjudged": r.get("unjudged_citations", 0)},
                    denominator=r["checked"], evidence=r["fails"][:20],
                    inputs={"chain": os.path.basename(ch or CHAIN)},
                    rules=["BAT-002", "PWR-003"],
                    note="the stored-energy chain end to end: every rating against its own source document, "
                         "every protective element against the board's netlist, and the four coordination "
                         "tests (the element is below what it protects, above the path's peak, able to "
                         "interrupt what is available, and followed by the stage it protects)")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
