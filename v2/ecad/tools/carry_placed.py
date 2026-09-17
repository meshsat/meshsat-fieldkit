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

Usage: carry_placed.py <placed.kicad_pcb> <routed.kicad_pcb> <out_dir> <routed_dir> [--verdicts a,b,c]
Exit 0 carried, 1 refused (a part moved), 3 the boards could not be read.
"""
import os, sys, json, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

CARRY = ("hardset-placed", "place_audit", "regionfit")
TOL_NM = 1000          # one micrometre: a rewrite of the same file can round, a moved part cannot hide here


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def positions(path):
    """{reference: (x_nm, y_nm, orientation_deg, side)} for every footprint on a board. Needs pcbnew."""
    import pcbnew
    b = pcbnew.LoadBoard(path)
    out = {}
    for f in b.GetFootprints():
        p = f.GetPosition()
        out[f.GetReference()] = (int(p.x), int(p.y), round(float(f.GetOrientationDegrees()), 3),
                                 "B" if f.IsFlipped() else "F")
    return out


def differences(placed, routed, tol_nm=TOL_NM):
    """What the route did to the placement, as a list of sentences. Empty means nothing moved.

    Pure, so the rule that decides a carry can be tested where KiCad is not."""
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
    return out


def rewrite(rec, measured_sha, board_sha, board_name, n_footprints):
    """The carried verdict: the same result, now naming the board it is evidence FOR and the board it was
    read ON. Nothing about the judgement itself changes; only its attribution becomes checkable."""
    rec = json.loads(json.dumps(rec))
    ins = rec.setdefault("inputs", {})
    ins["measured_board"] = {"sha256_16": measured_sha, "stage": "placed"}
    ins["board"] = {"path": board_name, "sha256_16": board_sha}
    rec["carried"] = {"from": "placed", "to": "routed", "footprints_compared": n_footprints,
                      "moved": 0, "by": "carry_placed.py"}
    rec["note"] = ((rec.get("note") or "") +
                   " | carried to the routed board after comparing all %d footprint positions, orientations "
                   "and sides: none moved, so the placement measured is the placement that shipped"
                   % n_footprints).strip(" |")
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
    carried, skipped = [], []
    if not moved:
        for n in names:
            src = os.path.join(out_dir, n + ".verdict.json")
            if not os.path.isfile(src): skipped.append(n); continue
            try: rec = json.load(open(src, encoding="utf-8"))
            except Exception: skipped.append(n); continue
            rec = rewrite(rec, sha16(placed), sha16(routed), os.path.basename(routed), len(P))
            os.makedirs(routed_dir, exist_ok=True)
            json.dump(rec, open(os.path.join(routed_dir, n + ".verdict.json"), "w"), indent=1, sort_keys=True)
            carried.append(n)
    print("carry_placed: %d footprint(s) compared, %d moved; carried %s%s"
          % (len(P), len(moved), ", ".join(carried) or "nothing",
             ("; not written by this chain: " + ", ".join(skipped)) if skipped else ""))
    for m in moved[:8]: print("  MOVED %s" % m)
    return _v.write("carry_placed", _v.FAIL if moved else (_v.PASS if carried else _v.INCONCLUSIVE),
                    counts={"footprints": len(P), "moved": len(moved), "carried": len(carried),
                            "not_written": len(skipped)},
                    denominator=len(P), evidence=moved[:12],
                    inputs={"placed": {"path": os.path.basename(placed), "sha256_16": sha16(placed)},
                            "board": {"path": os.path.basename(routed), "sha256_16": sha16(routed)}},
                    note=("the placement's evidence is carried to the routed board only while every footprint "
                          "is where the placement put it; a part that moved after routing means the routed "
                          "board's placement was never measured" if not moved else
                          "a part moved between the placed and the routed board, so the placement measurement "
                          "is about a different board and is not carried"),
                    rules=["PLC-001"], out_dir=out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
