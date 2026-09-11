#!/usr/bin/env python3
"""Does the board match the netlist it was placed from? (MESHSAT-862, round-two M4, 11 September 2026.)

Nothing in this pipeline compares the two. `check_contracts.py` reads netlists and never the board;
`verify_deliverable.py` reads the deliverable's files and never their contents against each other; the golden
schematic test compares a schematic with itself from a previous run. So a board placed from a STALE netlist
passes every gate: the chain's own history has the shape twice, once when a generator died and the next stage
rebuilt from the previous schematic (5 September, the 0x43 patch), and once when `build_sch.sh`'s exit code was
an echo nobody read (appendix 32.64). `full.sh` now deletes the netlist before regenerating it and blocks if it
is absent, which stops the file being stale; it does not check that the BOARD is the netlist's board.

Three comparisons, each with its denominator:

  1. every reference in the netlist is a footprint on the board, and every footprint that is a real component
     is in the netlist (a bench-fit land, a mounting hole and a test point are declared exceptions by prefix);
  2. every pad of a shared reference carries the net the netlist gives that pin;
  3. the net NAMES agree, once the root-sheet slash is stripped, because a board net that exists on no schematic
     pin is the phantom-net defect `check_zone_nets.py` catches from the other side.

Usage: netlist_board.py <board.kicad_pcb> [<netlist.net>]   exit 0 match, 1 mismatch, 3 nothing to compare
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

# Prefixes that exist on the board and never in the netlist as placeable parts: the same set the deliverable
# gate uses, and it is a declaration rather than a guess.
BENCH = ("H", "S_", "TP", "W_", "JP", "PAD", "P_", "#")


def read_netlist(path):
    """{ref: {pin: net}} from a KiCad netlist."""
    txt = open(path, encoding="utf-8", errors="replace").read()
    out = {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\n    \(net |\n  \)\n)', txt, re.S):
        net = m.group(1).lstrip("/")
        for n in re.finditer(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', m.group(2)):
            out.setdefault(n.group(1), {})[n.group(2)] = net
    return out


def main(a):
    if not a: print(__doc__); return verdict.USAGE
    board_path = a[0]
    stem = os.path.splitext(os.path.basename(board_path))[0]
    net_path = a[1] if len(a) > 1 else os.path.join(os.path.dirname(os.path.abspath(board_path)), "out", stem + ".net")
    if not os.path.exists(net_path):
        print("netlist_board: no netlist at %s, so the board was compared with nothing" % net_path)
        return verdict.write("netlist_board", verdict.INCONCLUSIVE, denominator=0, inputs={"board": board_path},
                             note="no netlist at %s" % net_path)
    nl = read_netlist(net_path)
    if not nl:
        print("netlist_board: %s parsed to no nodes at all" % net_path)
        return verdict.write("netlist_board", verdict.INCONCLUSIVE, denominator=0, inputs={"netlist": net_path},
                             note="the netlist parsed to no nodes")
    import pcbnew
    b = pcbnew.LoadBoard(board_path)
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    fails, checked = [], 0

    for ref in sorted(nl):
        checked += 1
        if ref not in fps: fails.append("%s is in the netlist and not on the board" % ref)
    board_only_dead = []
    for ref in sorted(fps):
        if ref.startswith(BENCH): continue
        checked += 1
        if ref in nl: continue
        # A footprint the netlist does not have is a part with no schematic behind it. If none of its pads carries
        # a net it is inert copper (a land, a bracket, a leftover of a placement list) and it is reported, not
        # blocked on; if any pad DOES carry a net, the board is wired to something the schematic does not know
        # about, which is the defect this gate exists for.
        live = sorted({p.GetNetname().lstrip("/") for p in fps[ref].Pads()
                       if p.GetNetname() and not p.GetNetname().lstrip("/").startswith("unconnected-")})
        if live: fails.append("%s is on the board and not in the netlist, and its pads carry %s" % (ref, ", ".join(live[:4])))
        else: board_only_dead.append(ref)

    for ref in sorted(set(nl) & set(fps)):
        pads = {}
        for p in fps[ref].Pads():
            n = p.GetNetname().lstrip("/")
            if n and not n.startswith("unconnected-"): pads.setdefault(p.GetNumber(), n)
        for pin, net in sorted(nl[ref].items()):
            checked += 1
            got = pads.get(pin)
            # KiCad gives every unconnected pin a synthetic net, `unconnected-(REF-PINNAME-PadN)`, and writes it
            # into the netlist as though it were a net. It is not one: the same pad on the board carries no net
            # at all, and the two agreeing is what a correct board looks like. Comparing the placeholder against
            # "no net" called 1,000 of B19's 6,716 comparisons a failure and blocked a board whose every other
            # gate passed, the first time this gate ran in a chain (11 September 2026).
            if net.startswith("unconnected-"):
                if got is not None:
                    fails.append("%s.%s carries %s on the board and is unconnected in the netlist" % (ref, pin, got))
                continue
            if got is None: fails.append("%s.%s is on net %s in the netlist and has no net on the board" % (ref, pin, net))
            elif got != net: fails.append("%s.%s is %s on the board and %s in the netlist" % (ref, pin, got, net))

    for f in fails[:30]: print("netlist_board: FAIL " + f)
    if board_only_dead:
        print("netlist_board: %d footprint(s) on the board that the netlist does not have and that carry no net "
              "at all: %s. Inert copper, reported and not blocked on; each is a placement list that has outlived "
              "its schematic part." % (len(board_only_dead), ", ".join(board_only_dead[:12])))
    print("netlist_board: %d of %d comparisons agree (%d references in the netlist, %d footprints on the board)"
          % (checked - len(fails), checked, len(nl), len(fps)))
    return verdict.write("netlist_board", verdict.PASS if not fails else verdict.FAIL,
                         counts={"fail": len(fails), "agree": checked - len(fails),
                                 "netlist_refs": len(nl), "board_footprints": len(fps),
                                 "board_only_inert": len(board_only_dead)},
                         denominator=checked, evidence=fails,
                         inputs={"board": board_path, "netlist": net_path},
                         note="the board against the schematic it was placed from")


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
