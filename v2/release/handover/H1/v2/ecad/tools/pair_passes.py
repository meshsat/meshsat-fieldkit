#!/usr/bin/env python3
"""Multi-pass pre-routing, best pass wins (10 September 2026, MESHSAT-862; appendix 32.98).

The order in which pairs are laid decides how many fit: a pair that fails in the pass lays when it is the only one on the
board (32.95). Taking the room back from its neighbours does not work, measured: 106 rip-up episodes and not one of them
paid (32.98). So the order is changed instead, the way a router with no cost history can: **the pairs that failed go first
next time.** Every pass starts from the same placed board, so a pass can only be judged as a whole, and the best pass wins.

    pair_passes.py <board.kicad_pcb> <passes> [pair_preroute arguments...]

The board is left as the best pass made it. Every pass writes its own log beside the board (pass-N.log) and the driver
prints one line per pass. Nothing is accepted that lays fewer pairs than the best so far, so the result is never worse
than the plain single pass, and the passes are independent: PAIR_* knobs reach the pre-router unchanged."""
import sys, os, re, shutil, subprocess

TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair_preroute.py")


def main(a):
    if len(a) < 2: print(__doc__); return 2
    board, passes, rest = a[0], int(a[1]), a[2:]
    stem = os.path.splitext(board)[0]
    src = stem + "-passsrc.kicad_pcb"
    shutil.copyfile(board, src)                      # the pristine placed board every pass starts from
    for ext in (".kicad_pro",):
        if os.path.exists(stem + ext): shutil.copyfile(stem + ext, stem + "-passsrc" + ext)
    best = (-1, None); order_file = stem + "-passorder.txt"
    if os.path.exists(order_file): os.remove(order_file)
    for k in range(1, passes + 1):
        shutil.copyfile(src, board)
        env = dict(os.environ)
        if k > 1: env["PAIR_ORDER_FILE"] = order_file
        log = "%s-pass%d.log" % (stem, k)
        with open(log, "w") as fh:
            subprocess.run([sys.executable, "-u", TOOL, board] + rest, stdout=fh, stderr=subprocess.STDOUT, env=env)
        txt = open(log, errors="replace").read()
        m = re.search(r"pair_preroute: (\d+) of (\d+) pairs laid", txt)
        laid = int(m.group(1)) if m else -1
        failed = []
        for ln in txt.splitlines():
            mm = re.match(r"pair_preroute: FAIL  (\S+):", ln)
            if mm and mm.group(1) not in failed: failed.append(mm.group(1))
        print("pair_passes: pass %d laid %s of %s, %d pair(s) failed -> %s" % (k, laid, m.group(2) if m else "?", len(failed), os.path.basename(log)), flush=True)
        if laid > best[0]:
            best = (laid, stem + "-passbest.kicad_pcb"); shutil.copyfile(board, best[1])
        if not failed: break                          # every pair laid: nothing left to reorder for
        with open(order_file, "w") as fh: fh.write("\n".join(failed) + "\n")
    if best[1]: shutil.copyfile(best[1], board)
    print("pair_passes: best pass laid %d pairs -> %s" % (best[0], board))
    return 0 if best[0] >= 0 else 1


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
