#!/usr/bin/env python3
"""What each board turns into heat, and where (rule THM-001, MESHSAT-862, 16 September 2026).

The registry has carried THM-001 as a BLOCKER with the coverage note "no dissipation estimate exists for any
board; the enclosure is sealed by ruling and holds a 30 W transmitter". This is the first half of the answer:
a per-board table of what dissipates, how much, and on what copper, built from data the tree already holds.

WHERE EVERY NUMBER COMES FROM:
  * the RAILS and their currents are the board's own intent file, the same source `dc_drop` reads;
  * a converter's LOSS is P_out * (1 / efficiency - 1), and the efficiency is DECLARED per rail in the intent
    (`efficiency=`) with its basis in the note. Nothing is assumed: a rail whose efficiency nobody has written
    down is listed as unknown and the verdict says so;
  * a part that dissipates for another reason (a power amplifier, a shunt, a linear regulator, a load switch)
    is declared per board in `boards/<letter>.json` as `dissipators`, each with its watts and the sentence that
    justifies it;
  * the THERMAL PATH is measured from the board: the copper area of the part's own pads plus any zone of its
    net around it, and the count of vias inside its courtyard, because that is what carries heat out of a
    package on a sealed board with no airflow of its own.

WHAT IT DOES NOT DO. It does not compute a junction temperature: that needs the envelope's maximum ambient,
which is ENV-001 and is an owner decision that does not exist yet. The rule stays short of its acceptance
criteria until then, and this says which half is missing rather than inventing the other.

Usage: thermal.py <board.kicad_pcb> [--json]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import boardtable as _bt


def main(a):
    if not a: print(__doc__); return _v.USAGE
    path = a[0]
    import pcbnew, intent
    mm = lambda v: v / 1e6
    b = pcbnew.LoadBoard(path)
    it = intent.load(path) or {}
    rails = it.get("rails") or {}
    letter = _bt.letter_for(path)
    declared = _bt.value(letter, "dissipators", []) or []
    out_dir = os.path.join(os.path.dirname(os.path.abspath(path)), "out")
    if not rails and not declared:
        print("thermal: this board declares no rail and no dissipator, so nothing can be estimated")
        return _v.write("thermal", _v.INCONCLUSIVE, denominator=0, inputs={"board": path},
                        note="no rail and no declared dissipator: nothing to estimate", out_dir=out_dir)

    fps = {f.GetReference(): f for f in b.GetFootprints()}

    def path_of(ref):
        """The copper a part can push heat into: its own pad area, and the vias inside its courtyard."""
        f = fps.get(ref)
        if f is None: return None
        area = sum(mm(p.GetSize().x) * mm(p.GetSize().y) for p in f.Pads())
        bbox = f.GetBoundingBox(False, False)
        vias = sum(1 for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and bbox.Contains(t.GetPosition()))
        return dict(pad_mm2=round(area, 1), vias_in_courtyard=vias)

    rows, unknown = [], []
    total_out = total_loss = 0.0
    for net, r in sorted(rails.items()):
        v = float(r.get("volts") or 0); i = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if v <= 0 or i <= 0: continue
        p_out = v * i; total_out += p_out
        eff = r.get("efficiency")
        src = r.get("source"); src = src[0] if isinstance(src, (list, tuple)) and src else src
        row = dict(rail=net, volts=v, amps=i, watts_out=round(p_out, 2), source=src, efficiency=eff,
                   thermal_path=path_of(src) if src else None)
        if eff:
            loss = p_out * (1.0 / float(eff) - 1.0); row["watts_lost"] = round(loss, 2); total_loss += loss
        else:
            unknown.append("%s: %.1f W out of %s and no efficiency declared, so its loss is unknown"
                           % (net, p_out, src or "an unnamed source"))
        rows.append(row)
    for d in declared:
        w = float(d.get("watts") or 0); total_loss += w
        rows.append(dict(part=d.get("ref"), watts_lost=w, why=(d.get("why") or "")[:120],
                         thermal_path=path_of(d.get("ref"))))

    print("thermal: %d rail(s) delivering %.1f W; estimated loss %.1f W from %d declared efficiency/dissipator "
          "figure(s); %d rail(s) with no efficiency declared"
          % (len([r for r in rows if r.get("rail")]), total_out, total_loss,
             len([r for r in rows if r.get("watts_lost") is not None]), len(unknown)))
    for r in rows:
        if r.get("watts_lost") is None: continue
        tp = r.get("thermal_path") or {}
        print("  %-14s %6.2f W into %s" % (r.get("rail") or r.get("part"), r["watts_lost"],
              ("%.0f mm2 of pad and %d via(s) in its courtyard" % (tp.get("pad_mm2", 0), tp.get("vias_in_courtyard", 0)))
              if tp else "a part this board does not carry"))
    for u in unknown[:12]: print("  unknown %s" % u)
    if "--json" in a: print(json.dumps(rows, indent=1))
    missing_path = [r for r in rows if r.get("watts_lost") and not r.get("thermal_path")]
    res = _v.INCONCLUSIVE if (unknown or not rows) else _v.PASS
    return _v.write("thermal", res,
                    counts={"rails": len([r for r in rows if r.get("rail")]), "watts_out": round(total_out, 1),
                            "watts_lost_estimated": round(total_loss, 1), "efficiency_undeclared": len(unknown),
                            "declared_dissipators": len(declared), "no_thermal_path": len(missing_path)},
                    denominator=len(rows), evidence=unknown[:20] + ["%s names a part this board does not carry" % (r.get("part") or r.get("rail")) for r in missing_path][:5],
                    inputs={"board": path},
                    note=("a dissipation table exists for this board; the junction temperature needs the "
                          "envelope's maximum ambient, which is ENV-001 and is not written yet" if not unknown else
                          "%d rail(s) carry no declared efficiency, so this board's loss is a floor and not an "
                          "estimate" % len(unknown)),
                    out_dir=out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
