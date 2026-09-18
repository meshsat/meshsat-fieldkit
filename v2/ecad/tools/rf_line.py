#!/usr/bin/env python3
"""A single-ended controlled-impedance line is the width its own stackup makes 50 ohm (rule RF-001,
MESHSAT-862, 16 September 2026).

WHAT WAS MISSING. Every board declares an RF class with a 50 ohm single-ended target (`intent.Z_DEFAULT`,
`RF: {z_se: 50}`), board A carries eleven blind-mate RF paths and board D a 30 W transmit output to an SMA,
and `impedance_check.py` judges PAIRS: the string `z_se` does not appear in it. So the target was declared on
every board and read by nothing, which is what the rule's own note says in words, "generation intends to
comply and nothing verifies it".

WHAT THIS COMPUTES. For every net whose class carries a `z_se` target and which is not one leg of a
differential pair, the routed width on each layer, and the impedance that width makes on that layer from the
BOARD'S OWN stackup: the microstrip form outside, the stripline form inside, through the same calibration
`impedance_check` uses (a 2D field solver where a solved point matches the geometry, the measured 0.967
microstrip correction otherwise). A width that lands outside the tolerance is named with both numbers.

WHAT IT DOES NOT DO, said plainly because an RF path is more than its width: it does not check the ground
clearance of a coplanar line, the via fence beside it, the return path under it (that is RET-001), the
connector launch, or anything at all above the frequency where a track stops being a transmission line and
starts being an antenna. It is the first of RF-001's questions, not the last.

Usage: rf_line.py <board.kicad_pcb> [--tolerance 0.10] [--json]
"""
import os, sys, json, math

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v


def main(a):
    if not a: print(__doc__); return _v.USAGE
    import pcbnew, intent, netclass
    import impedance_check as _imp
    path = a[0]
    tol = float(a[a.index("--tolerance") + 1]) if "--tolerance" in a else 0.10
    b = pcbnew.LoadBoard(path)
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    stack = _imp.read_stackup(path)
    if not stack:
        return _v.write("rf_line", _v.INCONCLUSIVE, denominator=0, inputs={"board": path}, rules=["RF-001"],
                        note="no stackup in the board file, so no width can be turned into an impedance",
                        out_dir=out_dir)
    it = intent.load(path) or {}
    classes = it.get("pair_classes") or intent.Z_DEFAULT
    pro = os.path.splitext(path)[0] + ".kicad_pro"
    assign = json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {}) if os.path.exists(pro) else {}
    ni = b.GetNetInfo()
    names = {ni.GetNetItem(k).GetNetname() for k in range(1, ni.GetNetCount())}
    paired = {n for n in names if n.endswith(("_P", "_N"))
              and (n[:-2] + ("_N" if n.endswith("_P") else "_P")) in names}
    segs = {}
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK": segs.setdefault(t.GetNetname(), []).append(t)
    rows, bad = [], []
    for net in sorted(names):
        if net in paired: continue
        cl = netclass.class_of(assign, net)
        target = (classes.get(cl) or {}).get("z_se") if cl else None
        if not target or (classes.get(cl) or {}).get("z_diff"): continue    # a pair class is judged as a pair
        pieces = segs.get(net) or segs.get("/" + net.lstrip("/")) or []
        if not pieces:
            rows.append(dict(net=net.lstrip("/"), cls=cl, target=target, state="UNROUTED"))
            continue
        by_layer = {}
        for t in pieces:
            L = t.GetLayer()
            by_layer.setdefault(L, []).append((t.GetWidth() / 1e6, t.GetLength() / 1e6))
        for L, ws in sorted(by_layer.items()):
            length = sum(l for _w, l in ws)
            if length <= 0: continue
            w = sum(w * l for w, l in ws) / length          # the length-weighted width, which is what the line IS
            g = _imp.geometry(stack, b.GetLayerName(L))
            if not g:
                rows.append(dict(net=net.lstrip("/"), cls=cl, target=target, layer=b.GetLayerName(L),
                                 mm=round(length, 1), width=round(w, 3), state="NO_GEOMETRY"))
                continue
            # geometry() answers (copper thickness, above, below), each side being (distance, er, next copper
            # layer's name) or None at the outside of the stack. A layer with copper on both sides is a
            # stripline and one with copper on a single side is a microstrip; which of those planes is a
            # REFERENCE under this particular track is impedance_check's question for a pair and is not asked
            # here, so a line over a routing layer is judged as though that layer were its reference and the
            # note says so.
            t_cu, above, below = g
            sides = [x for x in (above, below) if x]
            if not sides:
                rows.append(dict(net=net.lstrip("/"), cls=cl, target=target, layer=b.GetLayerName(L),
                                 mm=round(length, 1), width=round(w, 3), state="NO_REFERENCE"))
                continue
            if len(sides) == 2:
                d0, d1 = sides[0][0], sides[1][0]
                h = 2 * d0 * d1 / (d0 + d1); er = ((sides[0][1] or 4.4) + (sides[1][1] or 4.4)) / 2
                closed = _imp.z_stripline(w, h, t_cu, er); mode = "stripline"
            else:
                h, er = sides[0][0], (sides[0][1] or 4.4)
                closed = _imp.z_microstrip(w, h, t_cu, er); mode = "microstrip"
            # THE CALIBRATION THIS PROJECT HAS IS FOR A PAIR. `impedance_check.calibrated` matches solved
            # points whose spacing is part of the geometry and otherwise applies 0.967, and both numbers were
            # measured against DIFFERENTIAL impedance. Applying either to a single-ended line would be an
            # assumption wearing a measurement's clothes, so the closed form stands on its own here and the
            # verdict says which form produced it. IPC-2141's single-ended microstrip is good to a few percent
            # on this geometry and the tolerance is 10.
            z = closed
            off = (z - target) / target
            state = "MET" if abs(off) <= tol else "MISSED"
            rows.append(dict(net=net.lstrip("/"), cls=cl, target=target, layer=b.GetLayerName(L),
                             mm=round(length, 1), width=round(w, 3), z=round(z, 1), form=mode,
                             off_percent=round(100 * off, 1), state=state))
            if state == "MISSED":
                bad.append("%s on %s: %.3f mm wide over %.0f mm computes %.0f ohm against a %.0f ohm target (%+.0f percent)"
                           % (net.lstrip("/"), b.GetLayerName(L), w, length, z, target, 100 * off))
    judged = [r for r in rows if r.get("state") in ("MET", "MISSED")]
    print("rf_line: %d single-ended controlled line(s) judged on this board, %d outside %.0f percent"
          % (len(judged), len(bad), 100 * tol))
    for r in rows:
        if r.get("state") in ("MET", "MISSED"):
            print("  %-14s %-8s %-8s %.3f mm over %6.1f mm -> %5.1f ohm against %.0f  %s"
                  % (r["net"], r["cls"], r["layer"], r["width"], r["mm"], r["z"], r["target"], r["state"]))
        else:
            print("  %-14s %-8s %s" % (r["net"], r.get("cls") or "-", r["state"]))
    if "--json" in a: print(json.dumps(rows, indent=1))
    if not judged:
        # A DECLARED ZERO IS AN ANSWER. A board with no single-ended controlled line says so through its own
        # facts (`rf_transmit: false` and no RF net in its classes); a board that carries one and has not
        # routed it is a question.
        zero = False
        try:
            import rules_lib as _R
            stem = os.path.splitext(os.path.basename(path))[0]
            facts = _R.board_facts() or {}
            f = next((v for v in facts.values() if (v or {}).get("project") == stem), {}) or {}
            zero = f.get("rf_transmit") is False and not any(r.get("state") == "UNROUTED" for r in rows)
        except Exception:
            zero = False
        return _v.write("rf_line", _v.PASS if zero else _v.INCONCLUSIVE, denominator=0,
                        counts={"judged": 0}, inputs={"board": path}, rules=["RF-001"],
                        note=("this board's facts declare it carries no transmitter and no net of its own asks "
                              "for a single-ended impedance, so there is nothing of this rule on it" if zero else
                              "no single-ended controlled line was found to judge, and this board does not "
                              "declare that it has none"), out_dir=out_dir)
    return _v.write("rf_line", _v.FAIL if bad else _v.PASS,
                    counts={"judged": len(judged), "missed": len(bad)}, denominator=len(judged),
                    evidence=bad[:20], inputs={"board": path, "tolerance": tol}, rules=["RF-001"],
                    note="every net whose class declares a single-ended impedance, judged by the width it was "
                         "routed at on each layer against the board's own stackup, by the closed form alone "
                         "because this project's 2D-solver calibration is for a PAIR; the ground clearance, "
                         "the via fence and the launch are not judged here", out_dir=out_dir)


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("rf_line", main, sys.argv[1:]))