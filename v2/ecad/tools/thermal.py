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
    total_out = total_loss = total_loss_typ = 0.0
    for net, r in sorted(rails.items()):
        v = float(r.get("volts") or 0); i = float(r.get("amps_peak") or r.get("amps_typ") or 0)
        if v <= 0 or i <= 0: continue
        # TWO LOADS, TWO LOSSES (16 September 2026). This file already says that the sum of every rail's PEAK
        # is not a board power, because the peaks do not coincide; the dissipation figure was computed from
        # those same peaks and inherited exactly that, so board A's "36.6 W" was the loss with every rail at
        # its maximum at once. Both are computed now and both are labelled: the typical figure is what the
        # case has to get rid of continuously and the peak figure is the worst case that cannot last.
        i_typ = float(r.get("amps_typ") or 0) or i
        p_out = v * i; p_out_typ = v * i_typ; total_out += p_out
        eff = r.get("efficiency")
        src = r.get("source"); src = src[0] if isinstance(src, (list, tuple)) and src else src
        # A RAIL WITH NO CONVERTER HAS NO CONVERSION LOSS (16 September 2026). The first reading asked every
        # rail for an efficiency and 59 of them across five boards had none, but most of those are not
        # converter outputs at all: board P's PACK_P, CELL4 and FUSED are the pack node behind a fuse, board
        # E's CELL_F is the same node arriving on a wire, board D's +5V_D8 comes through a connector from
        # board A, and board A's VBAT and VIN_RAW are distribution. Their loss is the I2R of their own copper,
        # which `dc_drop` measures and this rule does not duplicate; asking them for an efficiency made the
        # gap look five times larger than it is and buried the converters that really do owe a number.
        # A rail declares its converter with `switch=` (rule PWR-002 put that there), so a rail with a switch
        # is a converted rail and a rail without one is distribution. `source_ic` marks the case where the
        # source part IS the power path, an LDO for instance, which is also a conversion.
        # The rail's own declaration first, because `switch` names what turns a rail ON and that is a pass FET
        # as often as it is a controller: board E's VIN_RAW is switched by a hot-swap FET and board P's PACK_P
        # by the protector's, and neither converts anything. Where the rail says nothing, a declared switch is
        # taken as a conversion and the rail is asked for its efficiency, which is the safe direction: it asks
        # a question that may not apply rather than assuming no heat.
        # ABSENCE IS NEVER A PASS, HERE TOO (16 September 2026, caught the same hour it was introduced). The
        # first version INFERRED conversion from `switch`, and that made board E pass with a dissipation of
        # zero: its 3.3 V and 5 V rails are made by an AP63205 and a linear regulator and declare no `switch`,
        # because nothing switches them off, so they read as distribution and were asked nothing at all. A
        # rail that does not SAY whether it converts is unknown, exactly like a rail with no efficiency, and
        # the verdict is INCONCLUSIVE until it says. `switch` names what turns a rail on and a pass FET is as
        # common there as a controller; it is not evidence of a conversion in either direction.
        converted = r.get("converted")
        row = dict(rail=net, volts=v, amps=i, watts_out=round(p_out, 2), source=src, efficiency=eff,
                   converted=converted, thermal_path=path_of(src) if src else None)
        if eff:
            loss = p_out * (1.0 / float(eff) - 1.0); row["watts_lost"] = round(loss, 2); total_loss += loss
            loss_typ = p_out_typ * (1.0 / float(eff) - 1.0); row["watts_lost_typ"] = round(loss_typ, 2)
            total_loss_typ += loss_typ
        elif converted is None:
            unknown.append("%s: %.1f W out of %s and the rail does not say whether it converts, so its loss is "
                           "unknown" % (net, p_out, src or "an unnamed source"))
        elif converted:
            unknown.append("%s: %.1f W out of %s through %s and no efficiency declared, so its loss is unknown"
                           % (net, p_out, src or "an unnamed source", r.get("switch") or r.get("source_ic")))
        else:
            row["watts_lost"] = 0.0
            row["why_no_loss"] = ("distribution or a pass element: this rail declares no conversion, so its "
                                  "loss is the I2R of its own copper, which dc_drop measures, plus whatever "
                                  "its pass part dissipates, which belongs in the board's dissipators list")
        rows.append(row)
    for d in declared:
        w = float(d.get("watts") or 0); total_loss += w; total_loss_typ += w
        rows.append(dict(part=d.get("ref"), watts_lost=w, why=(d.get("why") or "")[:120],
                         thermal_path=path_of(d.get("ref"))))

    # THE SUM OF EVERY RAIL'S PEAK IS NOT A BOARD'S POWER (16 September 2026). The first run printed 1,056 W
    # for board A and 777 for board P, which is what you get by adding the peak of every rail including the
    # pack node's fault-current capability and three slot rails that never peak together. A number like that in
    # a verdict is worse than no number. The per-rail figures stay, the board total is the DISSIPATION, which
    # is what this rule is about, and the throughput is printed as the sum of peaks with that said out loud.
    print("thermal: %d rail(s); estimated dissipation %.1f W at the TYPICAL load and %.1f W with every rail at "
          "its peak at once, from %d declared figure(s); %d rail(s) with no efficiency declared. The rails' "
          "peaks add to %.0f W of throughput, which is NOT a board power: the peaks do not coincide and a pack "
          "node's rating is not a load"
          % (len([r for r in rows if r.get("rail")]), total_loss_typ, total_loss,
             len([r for r in rows if r.get("watts_lost") is not None]), len(unknown), total_out))
    for r in rows:
        if r.get("watts_lost") is None: continue
        tp = r.get("thermal_path") or {}
        print("  %-14s %6.2f W typical, %6.2f W at peak into %s"
              % (r.get("rail") or r.get("part"), r.get("watts_lost_typ", r["watts_lost"]), r["watts_lost"],
              ("%.0f mm2 of pad and %d via(s) in its courtyard" % (tp.get("pad_mm2", 0), tp.get("vias_in_courtyard", 0)))
              if tp else "a part this board does not carry"))
    for u in unknown[:12]: print("  unknown %s" % u)
    if "--json" in a: print(json.dumps(rows, indent=1))
    missing_path = [r for r in rows if r.get("watts_lost") and not r.get("thermal_path")]
    res = _v.INCONCLUSIVE if (unknown or not rows) else _v.PASS
    return _v.write("thermal", res,
                    counts={"rails": len([r for r in rows if r.get("rail")]),
                            "watts_peak_sum_not_simultaneous": round(total_out, 1),
                            "watts_lost_typical": round(total_loss_typ, 1),
                            "watts_lost_all_peaks_at_once": round(total_loss, 1),
                            "efficiency_undeclared": len(unknown),
                            "declared_dissipators": len(declared), "no_thermal_path": len(missing_path)},
                    denominator=len(rows), evidence=unknown[:20] + ["%s names a part this board does not carry" % (r.get("part") or r.get("rail")) for r in missing_path][:5],
                    inputs={"board": path},
                    note=("a dissipation table exists for this board; the junction temperature needs the "
                          "envelope's maximum ambient, which is ENV-001 and is not written yet" if not unknown else
                          "%d rail(s) carry no declared efficiency, so this board's loss is a floor and not an "
                          "estimate" % len(unknown)),
                    out_dir=out_dir)


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("thermal", main, sys.argv[1:]))