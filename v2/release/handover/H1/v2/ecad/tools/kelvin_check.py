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


# THE KEYS A DECLARATION MAY CARRY, and it is not a style rule (20 September 2026). `judge` reads
# `full_scale_mv` to turn an error in millivolts into a SHARE, and a row with no share is never added to
# `fails`: it prints its millivolts and passes. So a single mistyped key turns a failing tap into a silent
# one, which is the shape `sensitive_nodes` refuses for its own node entries and this file did not refuse for
# these. Every key is named and an entry carrying any other, or missing any required one, is refused BEFORE
# any of it is believed.
KEYS_REQUIRED = ("sense", "rail", "element", "tap", "full_scale_mv", "why")
KEYS_OPTIONAL = ("board",)


def check_declaration(decls):
    """The complaints about the declaration itself, before any board is read."""
    bad = []
    for k in decls:
        where = "board %s, %s" % (k.get("board", "?"), k.get("sense", "<no sense>"))
        for f in KEYS_REQUIRED:
            if k.get(f) in (None, ""):
                bad.append("%s: no %s, so the reading would be about nothing" % (where, f))
        for f in k:
            if f not in KEYS_REQUIRED and f not in KEYS_OPTIONAL:
                bad.append("%s: the key %r is not one this file reads, and a mistyped full_scale_mv makes a "
                           "failing tap a silent one" % (where, f))
        for f in ("element", "tap"):
            v = str(k.get(f) or "")
            if v and ("." not in v or not v.split(".")[1]):
                bad.append("%s: %s is %r and must be <ref>.<pad>" % (where, f, v))
        if k.get("element") and k.get("element") == k.get("tap"):
            bad.append("%s: the element and the tap are the same pad, so the error is zero by construction" % where)
        try:
            if k.get("full_scale_mv") is not None and float(k["full_scale_mv"]) <= 0:
                bad.append("%s: full_scale_mv is not positive, so the share is not a share" % where)
        except (TypeError, ValueError):
            bad.append("%s: full_scale_mv is not a number" % where)
    return bad


def judge(decls, pots, intent=None):
    """(rows, fails): one row per declared sense, the error in mV and as a share of full scale.

    `intent` is the board's own declaration, and it is here to tell two silences apart (20 September 2026).
    `dc_drop` solves a potential only on a declared RAIL, so a tap whose reference conductor is declared a
    NODE, or not declared at all, can never be measured however good the mesh is, and saying "the mesh solved
    no pad" about it points at the wrong thing. Board E's tracker pair is the case that produced this: both
    its taps reference TRK_LSENSE and TRK_SW2, which board E declares as SWITCHING NODES, so the two rows
    written this morning read as a tool problem when they are a declaration problem. Board P's R8 and board
    A's five CS shunts are refused for the same reason on the ground side, which makes it EIGHT shunt halves
    on three boards sensed through copper no power rule solves: the question is about the declaration and not
    about any board's layout."""
    rows, fails = [], []
    nets = (pots or {}).get("nets") or {}
    rails = set((intent or {}).get("rails") or {})
    nodes = set((intent or {}).get("nodes") or {})
    for k in decls:
        rail = k.get("rail")
        got = nets.get(rail) or nets.get("/" + str(rail)) or []
        if not got:
            if intent is not None and rail not in rails:
                why = ("%s is declared a NODE on this board, so dc_drop solves no potential on it and this "
                       "tap can never be measured: a DECLARATION question" % rail if rail in nodes else
                       "%s is declared neither a rail nor a node on this board, so nothing solves it: a "
                       "DECLARATION question" % rail)
            else:
                why = "the mesh solved no pad of %s on this board" % rail
            rows.append((k, None, why)); continue
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
    letter = _v.opt(argv, "--board", None)
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
    bad = check_declaration(decls)
    if bad:
        for b in bad: print("kelvin_check: REFUSED %s" % b)
        return _v.write("kelvin_check", _v.INCONCLUSIVE, counts={"declared": len(decls), "refused": len(bad)},
                        denominator=len(decls), advisory=True, evidence=bad[:10],
                        inputs={"board": os.path.basename(board)},
                        missing_input="the declaration itself is malformed: %s" % bad[0],
                        note="a declaration is refused before it is believed, because a row with no usable "
                             "full scale prints millivolts and never fails")
    pots, path = _potentials(board)
    if pots is None:
        print("kelvin_check: no solved pad potentials beside this board (%s); run dc_drop first" % path)
        return _v.write("kelvin_check", _v.INCONCLUSIVE, counts={"declared": len(decls)}, denominator=len(decls),
                        advisory=True, inputs={"board": os.path.basename(board)},
                        missing_input="the solved pad potentials are not beside this board: %s" % path,
                        note="the share of a current-sense signal that is the copper's own drop")
    try:
        sys.path.insert(0, HERE); import intent as _intent
        _decl = _intent.load(board)
    except Exception:
        _decl = None
    rows, fails = judge(decls, pots, _decl)
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
