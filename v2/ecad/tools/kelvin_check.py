#!/usr/bin/env python3
"""How much of a current-sense signal is the copper's own drop, and not the shunt's (a report, 18 September 2026).

A current sense is only a measurement if the two taps meet the shunt at the shunt. Where a tap lands on a POUR
that carries the same current, the drop in the copper between the shunt's own pad and the tap is added to the
sensed voltage and read as current. Board A's charger is the case that produced this file: R16 is a 10 mOhm
input shunt, the BQ25731's high side taps `VBUS20` through R147 rather than R16's pad, and at the rail's 6.0 A
the shunt's whole signal is 60 mV. The same shape is open on board E's tracker and on board A's five LM5176
stages, whose CSG went to the plane until this morning.

THE NUMBER WAS UNASKABLE UNTIL TODAY. `dc_drop` solves a potential at every cell of every judged rail and
reported one of them, the worst drop; since 18 September it writes `<stem>-pad-potentials.json`, the solved
drop from the source at every pad. The error at a tap is then a subtraction between two pads of one net, which
is what this file does. Nothing here solves anything: give it a board whose mesh has not been solved and it
says so and decides nothing.

IT IS A REPORT AND IT DECIDES NOTHING YET. The registry has no rule that asks this question; ANA-001 asks about
a sense line's distance from switching copper, which is a different failure of the same circuit. What a
measurement without a rule is worth is that the rule can be written against a number instead of a fear, and
that the next board is drawn with the tap on the pad. The verdict is ADVISORY for that reason.

Declaration, per board, in `pcb_sensitive.yaml` under `kelvin:`

  - {sense: CH_ACP_F, rail: VBUS20, element: "R16.1", tap: "R147.1", full_scale_mv: 60.0,
     why: "the charger's input-current shunt; the high side taps the pour"}

`element` is the pad that defines the true node (the shunt's own terminal) and `tap` is where the sense line
actually connects. Both are pads of `rail`, because the error is the drop in that rail's copper between them.

Usage: kelvin_check.py <board.kicad_pcb> [--board <letter>] [--json]
"""
import os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

TOL_PCT = 1.0          # the share of full scale at which a tap stops being a Kelvin connection, per cent


def _potentials(board_path):
    """The solved drop at every pad, written beside the board by dc_drop, or None."""
    stem = os.path.splitext(os.path.basename(board_path))[0]
    for suf in ("-placed", "-preroute", "-par-routed", "-cleaned"):
        if stem.endswith(suf): stem = stem[: -len(suf)]
    d = os.path.dirname(os.path.abspath(board_path))
    if os.path.basename(d) == "out": d = os.path.dirname(d)
    p = os.path.join(d, "out", stem + "-pad-potentials.json")
    if not os.path.exists(p): return None, p
    return json.load(open(p, encoding="utf-8")), p


def _pad(rows, ref_pad):
    ref, _, pad = str(ref_pad).partition(".")
    for r in rows:
        if r.get("ref") == ref and str(r.get("pad")) == pad: return r
    return None


def judge(decls, pots):
    """(rows, fails): one row per declared sense, the error in mV and as a share of full scale."""
    rows, fails = [], []
    nets = (pots or {}).get("nets") or {}
    for k in decls:
        rail = k.get("rail")
        got = nets.get(rail) or nets.get("/" + str(rail)) or []
        if not got:
            rows.append((k, None, "the mesh solved no pad of %s on this board" % rail)); continue
        a, b = _pad(got, k.get("element")), _pad(got, k.get("tap"))
        if a is None or b is None:
            rows.append((k, None, "pad %s or %s is not on %s" % (k.get("element"), k.get("tap"), rail))); continue
        err_mv = abs(float(a["drop_v"]) - float(b["drop_v"])) * 1000.0
        fs = float(k.get("full_scale_mv") or 0) or None
        share = (err_mv / fs * 100.0) if fs else None
        rows.append((k, err_mv, share))
        if share is not None and share > TOL_PCT:
            fails.append("%s: the copper between %s and %s carries %.2f mV of the %.1f mV full scale, %.1f%% of "
                         "the reading, so the tap is not a Kelvin connection"
                         % (k.get("sense"), k.get("element"), k.get("tap"), err_mv, fs, share))
    return rows, fails


def main(argv):
    if not argv or argv[0].startswith("--"): print(__doc__); return 2
    board = argv[0]
    letter = argv[argv.index("--board") + 1] if "--board" in argv else None
    try:
        import yaml
        spec = yaml.safe_load(open(os.path.join(HERE, "pcb_sensitive.yaml"), encoding="utf-8"))
    except Exception as e:
        print("kelvin_check: the declaration could not be read (%s)" % e); return 3
    boards = (spec or {}).get("boards") or {}
    decls = []
    for L, blk in sorted(boards.items()):
        if letter and L != letter: continue
        for k in (blk or {}).get("kelvin") or []: decls.append(dict(k, board=L))
    if not decls:
        # A BOARD THAT DECLARES NO SENSE TAP IS NOT A BOARD WITH AN UNANSWERED QUESTION. The house law is that a
        # declared zero is a pass with its reason and an undeclared zero is inconclusive; this is neither, it is
        # a board the question does not arise on, so the reading says `applicable: false` and the chain carries
        # on. Board C's panel and board E5's contact block have no current sense at all.
        print("kelvin_check: board %s declares no current-sense tap, so there is nothing here to measure"
              % (letter or "?"))
        return _v.write("kelvin_check", _v.PASS, counts={"declared": 0}, denominator=0, advisory=True,
                        applicable=False, inputs={"board": os.path.basename(board)},
                        note="this board declares no current-sense tap in pcb_sensitive.yaml")
    pots, path = _potentials(board)
    if pots is None:
        print("kelvin_check: no solved pad potentials beside this board (%s); run dc_drop first" % path)
        return _v.write("kelvin_check", _v.INCONCLUSIVE, counts={"declared": len(decls)}, denominator=len(decls),
                        advisory=True, inputs={"board": os.path.basename(board)},
                        missing_input="the solved pad potentials are not beside this board: %s" % path,
                        note="the share of a current-sense signal that is the copper's own drop")
    rows, fails = judge(decls, pots)
    judged = [r for r in rows if r[1] is not None]
    print("kelvin_check: %d declared sense tap(s), %d measured, %d that are not Kelvin connections"
          % (len(decls), len(judged), len(fails)))
    for k, err, share in rows:
        if err is None: print("kelvin_check:   %s: %s" % (k.get("sense"), share)); continue
        print("kelvin_check:   %-12s %s -> %s: %.3f mV of copper drop%s"
              % (k.get("sense"), k.get("element"), k.get("tap"), err,
                 (", %.1f%% of the %.1f mV full scale" % (share, float(k["full_scale_mv"]))) if share is not None else ""))
    for f in fails: print("kelvin_check:   FAIL %s" % f)
    if "--json" in argv:
        print(json.dumps([{"sense": k.get("sense"), "err_mv": e, "share_pct": s} for k, e, s in rows], indent=1))
    return _v.write("kelvin_check", _v.FAIL if fails else (_v.INCONCLUSIVE if not judged else _v.PASS),
                    counts={"declared": len(decls), "measured": len(judged), "not_kelvin": len(fails)},
                    denominator=len(decls), evidence=fails[:10], advisory=True,
                    inputs={"board": os.path.basename(board), "tolerance_pct": TOL_PCT},
                    missing_input=(None if judged else "no declared tap could be measured on this board"),
                    note=("the share of a current-sense signal that is the copper's own drop between the shunt's "
                          "own pad and the point the sense line taps, from dc_drop's solved mesh; a REPORT, "
                          "because no rule asks this yet"))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
