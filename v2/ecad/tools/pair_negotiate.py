#!/usr/bin/env python3
"""Negotiated-congestion pre-routing (10 September 2026, MESHSAT-862; appendix 32.98 named it and this is it).

The pre-router plateaus at 50 of B19's 113 pairs and the plateau is the greedy order: whichever pair is laid first takes
the room. Ripping the neighbours back does not pay (106 episodes, none kept, 32.98). PathFinder's answer, which is what
every real router uses, is not to fight over the room but to price it:

  * every pair searches its corridor as if it owned the board, so no pair is ever blocked by another pair's choice;
  * a cell two pairs both wanted carries a HISTORY cost from then on, and a cell already given away this iteration
    carries a PRESENT cost, so the second pair to ask pays and goes round;
  * the iteration repeats, the prices rise, and the pairs sort themselves onto disjoint corridors.

When no cell is contested the plan is legal by construction and `pair_preroute.py` lays it with its own end geometry.
This driver runs the halves: N planning iterations through `PAIR_PLAN_MODE=plan`, then one laying pass with the plan.

    pair_negotiate.py <board.kicad_pcb> <iterations> [pair_preroute arguments...]

Env: PAIR_HIST_INC (history added to a contested cell per iteration, default 8), PAIR_PRESENT0 and PAIR_PRESENT_MUL
(the present cost and how fast it rises, default 2 and 2). Everything else reaches the pre-router unchanged."""
import sys, os, re, json, shutil, subprocess

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair_preroute.py")


def main(a):
    if len(a) < 2: print(__doc__); return 2
    board, iters, rest = a[0], int(a[1]), a[2:]
    stem = os.path.splitext(board)[0]
    hist_inc = float(os.environ.get("PAIR_HIST_INC", "8"))
    present = float(os.environ.get("PAIR_PRESENT0", "2"))
    mul = float(os.environ.get("PAIR_PRESENT_MUL", "2"))
    hist = {}                                   # (layer index, i, j) -> cost
    hist_f = stem + "-neghist.npz"; plan_f = stem + "-negplan.json"; conf_f = stem + "-negconf.npz"
    best = None
    import numpy as np
    for k in range(1, iters + 1):
        env = dict(os.environ)
        env.update(PAIR_PLAN_MODE="plan", PAIR_PRESENT="%.3f" % present,
                   PAIR_PLAN_OUT=plan_f, PAIR_CONFLICT_OUT=conf_f)
        if hist: env["PAIR_HIST_IN"] = hist_f
        log = "%s-neg%d.log" % (stem, k)
        with open(log, "w") as fh:
            subprocess.run([sys.executable, "-u", TOOL, board] + rest, stdout=fh, stderr=subprocess.STDOUT, env=env)
        txt = open(log, errors="replace").read()
        m = re.search(r"PLAN (\d+) of (\d+) pairs have a corridor for every section, (\d+) contested cell", txt)
        if not m:
            print("pair_negotiate: iteration %d wrote no plan line, see %s" % (k, os.path.basename(log)), flush=True); return 1
        done, total, contested = int(m.group(1)), int(m.group(2)), int(m.group(3))
        print("pair_negotiate: iteration %d: %s of %s pairs have a corridor, %s contested cell(s), present cost %.1f"
              % (k, done, total, contested, present), flush=True)
        # The laying pass cares about CONTESTED cells first: a plan where every pair has a corridor but the corridors overlap
        # lays worse than one where a few pairs have none and the rest are disjoint, because an overlap is a pair lost anyway
        # and it takes its neighbour with it. Fewest contested first, then most corridors.
        if best is None or (contested, -done) < (best[1], -best[0]):
            best = (done, contested); shutil.copyfile(plan_f, plan_f + ".best")
        if contested == 0: break
        c = np.load(conf_f)                     # the cells two pairs both wanted: they cost more from now on
        for L, i, j, v in zip(c["L"], c["i"], c["j"], c["v"]):
            hist[(int(L), int(i), int(j))] = hist.get((int(L), int(i), int(j)), 0.0) + hist_inc * float(v)
        np.savez_compressed(hist_f, L=np.array([k[0] for k in hist], dtype=np.int16),
                            i=np.array([k[1] for k in hist], dtype=np.int32),
                            j=np.array([k[2] for k in hist], dtype=np.int32),
                            v=np.array(list(hist.values()), dtype=np.float32))
        present *= mul
    if best is None: return 1
    print("pair_negotiate: best plan: %d pairs with a corridor, %d contested cell(s); laying it" % best, flush=True)
    shutil.copyfile(plan_f + ".best", plan_f)
    env = dict(os.environ); env["PAIR_PLAN_IN"] = plan_f
    log = stem + "-neglay.log"
    with open(log, "w") as fh:
        subprocess.run([sys.executable, "-u", TOOL, board] + rest, stdout=fh, stderr=subprocess.STDOUT, env=env)
    txt = open(log, errors="replace").read()
    m = re.search(r"pair_preroute: (\d+) of (\d+) pairs laid", txt)
    print("pair_negotiate: laid %s -> %s" % (m.group(0).split(": ")[-1] if m else "?", board))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
