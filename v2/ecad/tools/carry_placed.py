#!/usr/bin/env python3
"""Carry the placement's evidence to the board that was routed from it, and prove it belongs (rule PLC-001,
MESHSAT-862, 17 September 2026).

THE QUESTION PLC-001 ASKS can only be answered on the PLACED board: was the placement legal before anything
was routed? The measurement happens in `full.sh`, in a tree that is later thrown away, so on 16 September the
finish began copying `hardset-placed`, `place_audit` and `regionfit` into the board's `routed/` snapshot. That
copy proved nothing. It moved a verdict about one file into a directory holding another file, and the only
thing tying the two together was that they sat in the same tree, which is the attribution defect this project
has now met five times.

WHAT MAKES THE CARRY HONEST. A route lays copper and moves no part: "never move parts after routing" is a
standing rule of this pipeline, and it is checkable. This compares every footprint of the placed board with
the routed board by reference, position, orientation and side. If every one is identical, the placement that
was measured IS the placement that shipped, and the verdict is carried with both shas recorded: the board it
was READ on, and the board it is EVIDENCE FOR. If any footprint moved, the carry is REFUSED and says which
ones, because then the routed board's placement was never measured and the honest reading is that it is
unknown.

THE PRE-ROUTER MOVES PARTS, AND THAT IS NOT A BREACH (17 September 2026, found by this tool's first run).
Board D's placed snapshot and its committed board differ by R20 and R21, 1.600 mm each: the two series
resistors of a USB pair, swapped by `pair_preroute`'s station swap, which runs BEFORE the router and is a
recorded, measured operation. So there are two boards before the route, and the question PLC-001 asks is about
the placement that SHIPPED:

  1. the placed snapshot matches the routed board  -> the placed measurements are the evidence and are carried;
  2. it does not, but the PRE-ROUTE board does     -> the pre-route DRC is the evidence, because it is the same
     fifteen-type hard set measured after every part move and before any routing, and a clean superset means a
     clean placement. It is carried under the name `hardset-placed`, because that is the name PLC-001 asks
     its question by, and what it really is travels inside it: the label, the stage and both shas.
     `place_audit` is NOT carried in this case: it was taken before the move, so it is about a placement that
     no longer exists;
  3. neither matches                               -> nothing is carried and the tool says which parts moved.

Usage: carry_placed.py <placed.kicad_pcb> <routed.kicad_pcb> <out_dir> <routed_dir> [--preroute <board>]
                       [--verdicts a,b,c]
Exit 0 carried, 1 refused (a part moved with no pre-route board to fall back on), 3 the boards could not be read.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

CARRY = ("hardset-placed", "place_audit", "regionfit")
# GEOMETRY ONLY. A seat exchange between two parts of the same land moves no courtyard, hole or clearance, so
# the hard set and the region fit are unchanged by it; the escape-fan predictor is NOT, because it reads the
# NETS at each seat and the exchange puts a different net in each. Board D's placed board predicts no
# collision and the board that shipped, with R20 and R21 exchanged, predicts one (17 September 2026).
CARRY_SWAPPED = ("hardset-placed", "regionfit")
CARRY_PREROUTE = ("hardset-pre-route-drc",)   # measured after every part move, before any routing
TOL_NM = 1000          # one micrometre: a rewrite of the same file can round, a moved part cannot hide here


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def positions(path):
    """{reference: (x_nm, y_nm, orientation_deg, side, footprint_id)} for every footprint on a board.

    The footprint id is part of the answer because of the swap below: two parts may exchange positions only if
    they are the same land, and nothing else in this comparison would notice a 0402 taking an 0805's seat."""
    import pcbnew
    b = pcbnew.LoadBoard(path)
    out = {}
    for f in b.GetFootprints():
        p = f.GetPosition()
        try: fpid = str(f.GetFPIDAsString())
        except Exception: fpid = str(f.GetFPID().GetLibItemName()) if hasattr(f, "GetFPID") else ""
        out[f.GetReference()] = (int(p.x), int(p.y), round(float(f.GetOrientationDegrees()), 3),
                                 "B" if f.IsFlipped() else "F", fpid)
    return out


def _same_seat(a, b, tol_nm=TOL_NM):
    """Is this the same seat: the same point within a micrometre, the same angle and the same side?"""
    return (abs(a[0] - b[0]) <= tol_nm and abs(a[1] - b[1]) <= tol_nm
            and abs(a[2] - b[2]) <= 0.01 and a[3] == b[3])


def swaps(placed, routed, moved_refs, tol_nm=TOL_NM):
    """The moved parts that merely EXCHANGED SEATS with each other, as sentences, or None if they did not.

    THE PRE-ROUTER SWAPS A PAIR'S TWO SERIES RESISTORS (`PAIR_SWAP`), which is a declared, measured operation
    that runs before the router: board D's R20 and R21 are each 1.600 mm from where the placed snapshot put
    them, and they are in each other's seats. Exchanging two parts of the SAME LAND between two seats changes
    no courtyard, no hole and no clearance relation on the board: the set of occupied seats is identical, so a
    placement measured before the swap is still a measurement of this board's placement. Any other move is a
    move."""
    if not moved_refs: return []
    seats_before = sorted((placed[r][:4], (placed[r][4] if len(placed[r]) > 4 else None)) for r in moved_refs)
    seats_after = sorted((routed[r][:4], (routed[r][4] if len(routed[r]) > 4 else None)) for r in moved_refs)
    if len(seats_before) != len(seats_after): return None
    for (gb, fb), (ga, fa) in zip(seats_before, seats_after):
        if not _same_seat(gb, ga, tol_nm) or fb != fa: return None
    out = []
    for r in sorted(moved_refs):
        other = [q for q in moved_refs if q != r and _same_seat(placed[q][:4], routed[r][:4], tol_nm)]
        out.append("%s took %s's seat" % (r, other[0] if other else "another part's"))
    return out


def differences(placed, routed, tol_nm=TOL_NM):
    """What happened to the placement, as a list of sentences. Empty means nothing moved.

    A pure exchange of seats between parts of the same land is NOT a move and is reported by `swaps`; this
    returns what is left. Pure, so the rule that decides a carry can be tested where KiCad is not."""
    out = []
    for ref in sorted(set(placed) - set(routed)):
        out.append("%s is on the placed board and not on the routed one" % ref)
    for ref in sorted(set(routed) - set(placed)):
        out.append("%s is on the routed board and was not placed" % ref)
    for ref in sorted(set(placed) & set(routed)):
        a, b = placed[ref], routed[ref]
        if abs(a[0] - b[0]) > tol_nm or abs(a[1] - b[1]) > tol_nm:
            out.append("%s moved %.3f mm" % (ref, ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 / 1e6))
        elif abs(a[2] - b[2]) > 0.01:
            out.append("%s turned %.2f degrees" % (ref, abs(a[2] - b[2])))
        elif a[3] != b[3]:
            out.append("%s changed side %s to %s" % (ref, a[3], b[3]))
    if out and all(" moved " in line for line in out):
        refs = [line.split(" ", 1)[0] for line in out]
        if swaps(placed, routed, refs, tol_nm) is not None:
            return []                     # every one of them is in another's seat: the same placement
    return out


def rewrite(rec, measured_sha, board_sha, board_name, n_footprints, stage="placed"):
    """The carried verdict: the same result, now naming the board it is evidence FOR and the board it was
    read ON. Nothing about the judgement itself changes; only its attribution becomes checkable."""
    rec = json.loads(json.dumps(rec))
    ins = rec.setdefault("inputs", {})
    ins["measured_board"] = {"sha256_16": measured_sha, "stage": stage}
    ins["board"] = {"path": board_name, "sha256_16": board_sha}
    rec["carried"] = {"from": stage, "to": "routed", "footprints_compared": n_footprints,
                      "moved": 0, "by": "carry_placed.py"}
    rec["note"] = ((rec.get("note") or "") +
                   " | carried to the routed board from the %s board after comparing all %d footprint "
                   "positions, orientations and sides: none moved, so the placement measured is the placement "
                   "that shipped" % (stage, n_footprints)).strip(" |")
    return rec


def main(argv):
    if len(argv) < 4 or argv[0] in ("-h", "--help"): print(__doc__); return 2
    placed, routed, out_dir, routed_dir = argv[0], argv[1], argv[2], argv[3]
    names = CARRY
    if "--verdicts" in argv: names = tuple(x for x in argv[argv.index("--verdicts") + 1].split(",") if x)
    try:
        P, R = positions(placed), positions(routed)
    except Exception as e:
        print("carry_placed: the boards could not be read (%s)" % str(e)[:120])
        return _v.write("carry_placed", _v.INCONCLUSIVE, denominator=0, inputs={"placed": os.path.basename(placed)},
                        note="the placed and routed boards could not both be read, so the placement's evidence "
                             "is not carried: %s" % str(e)[:160], out_dir=out_dir)
    moved = differences(P, R)
    # What differences() forgave: a pure exchange of seats. It is geometrically neutral and not net-neutral.
    _moved_refs = [ref for ref in sorted(set(P) & set(R))
                   if not _same_seat(P[ref][:4], R[ref][:4], TOL_NM)]
    swapped = swaps(P, R, _moved_refs) if (_moved_refs and not moved) else []
    stage, names_now = "placed", (tuple(n for n in names if n in CARRY_SWAPPED) if swapped else names)
    pre = argv[argv.index("--preroute") + 1] if "--preroute" in argv else None
    if pre is None:
        _guess = os.path.join(os.path.dirname(placed),
                              os.path.basename(placed).replace("-placed.kicad_pcb", "-preroute.kicad_pcb"))
        pre = _guess if os.path.isfile(_guess) else None
    moved_pre = None
    if moved and pre:
        try:
            moved_pre = differences(positions(pre), R)
        except Exception as e:
            moved_pre = ["the pre-route board could not be read (%s)" % str(e)[:80]]
        if not moved_pre:
            stage, names_now, moved = "pre-route", CARRY_PREROUTE, []
    carried, skipped = [], []
    names = names_now
    if not moved:
        for n in names:
            src = os.path.join(out_dir, n + ".verdict.json")
            if not os.path.isfile(src): skipped.append(n); continue
            try: rec = json.load(open(src, encoding="utf-8"))
            except Exception: skipped.append(n); continue
            _src_board = placed if stage == "placed" else pre
            rec = rewrite(rec, sha16(_src_board), sha16(routed), os.path.basename(routed),
                          len(P), stage=stage)
            # UNDER ONE NAME (17 September 2026). The pre-route judgement is carried as `hardset-placed`,
            # because that is the name the registry asks PLC-001's question by, and what it was is in the
            # verdict: its label, its stage and both shas. Adding a second NAME to the rule instead would make
            # the fallback mandatory for every board and let a stale copy of it answer for this one, which is
            # exactly what board P did with an 11 September file for ten minutes this morning.
            _as = "hardset-placed" if n in CARRY_PREROUTE else n
            os.makedirs(routed_dir, exist_ok=True)
            json.dump(rec, open(os.path.join(routed_dir, _as + ".verdict.json"), "w"), indent=1, sort_keys=True)
            carried.append("%s as %s" % (n, _as) if _as != n else n)
    for line in (swapped or [])[:6]:
        print("  SWAP %s: the same seats, the same land, a different net in each" % line)
    if swapped:
        print("  the escape-fan predictor is not carried across a swap: it reads the nets at each seat, and "
              "the exchange puts a different net in each")
    print("carry_placed: %d footprint(s) compared against the %s board, %d moved; carried %s%s"
          % (len(P), stage, len(moved), ", ".join(carried) or "nothing",
             ("; not written by this chain: " + ", ".join(skipped)) if skipped else ""))
    for m in moved[:8]: print("  MOVED %s" % m)
    if stage == "pre-route":
        print("  the pre-router moved %d part(s) after the placed snapshot, so the placement that shipped is "
              "the one the PRE-ROUTE DRC measured; place_audit is not carried because it was taken before "
              "that move" % len(differences(P, R)))
    _after_placement = differences(P, R)
    return _v.write("carry_placed", _v.FAIL if moved else (_v.PASS if carried else _v.INCONCLUSIVE),
                    counts={"footprints": len(P), "moved": len(moved), "carried": len(carried),
                            "not_written": len(skipped), "moved_after_the_placement": len(_after_placement),
                            "seats_exchanged": len(swapped or []), "stage": stage},
                    denominator=len(P), evidence=(moved or _after_placement)[:12],
                    inputs={"placed": {"path": os.path.basename(placed), "sha256_16": sha16(placed)},
                            "pre_route": ({"path": os.path.basename(pre), "sha256_16": sha16(pre)} if pre else None),
                            "board": {"path": os.path.basename(routed), "sha256_16": sha16(routed)}},
                    note=("the placement's evidence is carried to the routed board only while every footprint is "
                          "where that board put it. Nothing moved between the placed board and the routed one, "
                          "so the placed measurements are this board's" if (not moved and stage == "placed") else
                          "the PRE-ROUTER moved %d part(s) after the placed snapshot, which it is entitled to do "
                          "(the pair station swap runs before the router), so the placement that shipped is the "
                          "one the PRE-ROUTE DRC measured, over the same fifteen hard types and after every part "
                          "move; place_audit is not carried because it was taken before that move"
                          % len(_after_placement) if (not moved and stage == "pre-route") else
                          "a part moved between every board before the route and the routed one, so this board's "
                          "placement was never measured and nothing is carried"),
                    rules=["PLC-001"], out_dir=out_dir)


if __name__ == "__main__":
    # the coverage map names this tool as a rule's verification, so a crash here has to leave a reading
    # too (18 September 2026; the rule that finds this one reads the coverage map rather than a list)
    sys.exit(_v.guard("carry_placed", main, sys.argv[1:]))