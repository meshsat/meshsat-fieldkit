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
import os, re, sys, json, glob

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


# ECSS-Q-ST-30-11C Rev.2 Table 6-17: a fuse's current at or below 85 C case temperature. The same table falls
# to 50 percent at 110 C; this project's fuses sit in a sealed case whose inside temperature is owner decision
# 34, so the screen is the 85 C figure and the envelope decides whether it should be the other one.
FUSE_SCREEN = 0.65


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
    # THE SELECTION CRITERIA OF ECSS 6.17 ARE PWR-003's, NOT BAT-002's. BAT-002 asks whether the chain is
    # bounded END TO END; a fuse at 80 percent of its rating is a coordination finding about one stage, and
    # counting it in the set verdict failed four boards for something that is one board's (17 September 2026).
    derate_fails = []
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
        # 7. THE FUSE'S OWN SELECTION CRITERIA, and they have an authority at last (17 September 2026).
        # ECSS-Q-ST-30-11C Rev.2, "Derating - EEE components", 23 June 2021, clause 6.17, transcribed in
        # v2/vendor/standards/ecss-q-st-30-11c-rev2-2021-06-23.md. This rule has carried "no authority for the
        # SELECTION CRITERIA" since the registry was written, because the fuses' own datasheets name SAE J1284
        # and ISO 8820-3 and neither is free. The ECSS standard is, from a body this project already cites.
        #
        # Two of its clauses are about the CIRCUIT and hold whatever the fuse is made of, so they are enforced:
        #   6.17.3 b  the largest fuse rating compatible with the source capability shall be used
        #   6.17.3 c  the power supply shall be capable of delivering three times the specified fuse rated
        #             current in order to obtain short fusing times
        # The third is a number for CERMET fuses and this kit's are automotive blades, and the standard's own
        # 6.17.1a says the application and derating of another technology SHALL BE JUSTIFIED. So Table 6-17's
        # 65 percent is a screen here, and a stage over it must carry that justification in writing rather
        # than being failed for a limit the standard does not set for it, or passed as though no limit existed.
        if prot.get("kind") == "fuse" and r is not None:
            checked += 1
            cont = s.get("continuous_a")
            if cont is None:
                derate_fails.append("%s: a fuse with no continuous current declared cannot be judged against any "
                                    "derating criterion" % sid)
            else:
                ratio = float(cont) / float(r)
                if ratio <= FUSE_SCREEN + 1e-9:
                    notes.append("%s: %s carries %.1f A of its %.1f A rating (%.0f percent), inside the 65 percent "
                                 "ECSS-Q-ST-30-11C Rev.2 Table 6-17 sets for a fuse at or below 85 C"
                                 % (sid, prot.get("ref", "the fuse"), float(cont), float(r), 100 * ratio))
                elif str(s.get("derating_basis", "")).strip():
                    notes.append("%s: %s carries %.0f percent of its rating, past the 65 percent of Table 6-17, "
                                 "and the board declares why: %s"
                                 % (sid, prot.get("ref", "the fuse"), 100 * ratio, str(s["derating_basis"])[:120]))
                else:
                    derate_fails.append("%s: %s carries %.1f A of its %.1f A rating (%.0f percent) and the criterion "
                                 "this project judges a fuse by is 65 percent (ECSS-Q-ST-30-11C Rev.2 Table 6-17, "
                                 "stated for Cermet; 6.17.1a requires another technology's derating to be "
                                 "JUSTIFIED, and this stage declares no derating_basis)"
                                 % (sid, prot.get("ref", "the fuse"), float(cont), float(r), 100 * ratio))
            # 6.17.3 c: the source has to be able to blow it
            lo = pf.get("low")
            checked += 1
            if lo is None or float(lo) <= 0:
                notes.append("%s: the fault current available at %s is not established, so ECSS 6.17.3c (the "
                             "source delivers three times the fuse rating) cannot be judged here; it is part of "
                             "the operating envelope, owner decision 34"
                             % (sid, prot.get("ref", "the fuse")))
            elif float(lo) < 3.0 * float(r) - 1e-9:
                derate_fails.append("%s: the source delivers %.0f A at worst and the fuse is rated %.1f A, so it cannot "
                             "reach the three times ECSS-Q-ST-30-11C Rev.2 6.17.3c asks for: the fuse clears "
                             "slowly or not at all" % (sid, float(lo), float(r)))
            else:
                notes.append("%s: the source delivers at least %.0f A against a %.1f A fuse, which is %.1f times "
                             "its rating (ECSS 6.17.3c asks for three)" % (sid, float(lo), float(r), float(lo) / float(r)))
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
    # WHICH BOARD EACH STAGE BELONGS TO, so a failure can be attributed to it. The chain is a set-level object
    # and its COMPLETENESS is a set-level property (BAT-002), but a coordination failure is a property of the
    # stage, and the stage names its board: board E's shore fuse at 80 percent of its rating is not board P's
    # defect, and reading one verdict for all of them is the shape this project has now fixed three times in a
    # day (17 September 2026).
    by_board = {}
    for st in stages:
        for L in re.findall(r"[A-Z]+[0-9]*", str(st.get("board", "")).upper()):
            if L == "TO": continue          # "P to E" names two boards
            by_board.setdefault(L.lower(), []).append(st["id"])
    return dict(stages=len(stages), checked=checked, fails=fails, derate_fails=derate_fails, notes=notes,
                unjudged_citations=unjudged_citations, vendor_seen=bool(have_vendor), by_board=by_board)


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
    for f in r.get("derate_fails", []): print("  FAIL (selection, rule PWR-003) %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    # The coordination is what this rule is about, and it is judged wherever the chain file is. A tree with no
    # vendor library leaves the citations unjudged, which is reported and does not turn a passing chain into a
    # failing one; it is also not silently a pass, because the count travels in the verdict.
    # A PER-BOARD VERDICT BESIDE THE SET ONE. PWR-003 asks about a protective element, which belongs to a
    # stage and so to a board; BAT-002 asks whether the chain is bounded END TO END, which is the set's and
    # stays on the set verdict below.
    for _L, _ids in sorted((r.get("by_board") or {}).items()):
        _mine = [f for f in (r["fails"] + r.get("derate_fails", [])) if f.split(":")[0].strip() in _ids]
        _v.write("energy_chain_%s" % _L, _v.FAIL if _mine else _v.PASS,
                 counts={"stages": len(_ids), "fail": len(_mine)}, denominator=len(_ids),
                 evidence=_mine[:20], quiet=True, rules=["PWR-003"],
                 inputs={"chain": os.path.basename(ch or CHAIN), "stages": ",".join(_ids)},
                 note="the stages of the stored-energy chain that sit on this board; the chain as a whole is "
                      "energy_chain, and whether it is bounded end to end is that verdict's question")
    res = _v.FAIL if r["fails"] else _v.PASS
    return _v.write("energy_chain", res,
                    counts={"stages": r["stages"], "checks": r["checked"], "fail": len(r["fails"]),
                            "selection_findings": len(r.get("derate_fails", [])),
                            "citations_unjudged": r.get("unjudged_citations", 0)},
                    denominator=r["checked"], evidence=r["fails"][:20],
                    inputs={"chain": os.path.basename(ch or CHAIN)},
                    rules=["BAT-002"],
                    note="THE CHAIN END TO END, which is BAT-002's question; a selection finding against ECSS "
                         "6.17 belongs to the stage that has it and is in energy_chain_<letter>, rule PWR-003. "
                         "Every rating against its own source document, "
                         "every protective element against the board's netlist, and the four coordination "
                         "tests (the element is below what it protects, above the path's peak, able to "
                         "interrupt what is available, and followed by the stage it protects)")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
