#!/usr/bin/env python3
"""packfit_west.py: a second 4S3P block in the west pocket, judged with adjudication A06's own tool (stream energy,
MESHSAT-1357, 28 September 2026). PROTOTYPE DESIGN: nothing built; an AI review of a committed geometry study.

It imports v2/docs/records/adj/A06-pack-geometry/drafts/pack_fit.py UNCHANGED (pinned by sha256, refused if changed;
importing it runs A06's own search, about 0.3 s, and prints nothing) and reuses its pockets, obstruction zones (board B's
committed underside), heater-mat bases and placement search, for four arrangements A06 did not print:
  1  the 4S3P 18650 block alone (3x2 section, shrink-wrapped, no board P), in the west pocket;
  2  the block with board P on top of it (0.5 mm gap, board 1.6 mm), at board P's tallest part 16.17 mm (the Keystone
     3568 holder with its MINI blade, A06's P_TALL), 9.8 mm (the JST XH, A06's P_XH) and 6.4 mm (the 8 mm assembled
     board the first issue of this record assumed, less the 1.6 mm board);
  3  board P beside the block in the west pocket, at the block's end or side (A06's 'end' and 'side' arrangements);
  4  a second board P in the east pocket beside the ruled group (block, 2 mm, board P), by the free length A06 leaves.
Stdout only; deterministic. Usage: packfit_west.py
"""
import hashlib
import importlib.util
import io
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL = os.path.normpath(os.path.join(HERE, "..", "adj", "A06-pack-geometry", "drafts", "pack_fit.py"))
TOOL_SHA256_PIN = "a2a050dc24c461f207bb0485ef98851f238641f449f30151605042970bccf02c"


def main():
    got = hashlib.sha256(open(TOOL, "rb").read()).hexdigest()
    if got != TOOL_SHA256_PIN:
        sys.stderr.write("packfit_west: %s changed (sha256 %s), refusing to run\n" % (os.path.relpath(TOOL, os.path.join(HERE, "..", "..", "..", "..")), got[:16]))
        return 3
    spec = importlib.util.spec_from_file_location("pack_fit", TOOL)
    pf = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(pf)
    out = []
    out.append("WEST POCKET, A06's tool (pack_fit.py sha256 %s, unchanged). B underside Z %.2f; bases nominal %.2f / worst %.2f (heater mat and pads)." % (
        got[:16], pf.B_UNDER, pf.BASE["nom"], pf.BASE["worst"]))
    c = pf.CELLS["18650"]
    k, W, H = pf.sections(c["D"])["3x2"]
    n_sec = -(-12 // k)
    Lb = n_sec * (c["L"] + pf.JOINT) + 2 * pf.WRAP
    Wb = W + 2 * pf.WRAP
    Hb = H + 2 * pf.WRAP
    out.append("the 4S3P block: 3x2 section, %d sections, W %.2f x L %.2f x H %.2f (A06's wrap %.1f and joint %.1f)" % (n_sec, Wb, Lb, Hb, pf.WRAP, pf.JOINT))
    for bname in ("nom", "worst"):
        base = pf.BASE[bname]
        zb = base + Hb
        # 1 the block alone
        r = pf.place(pf.WEST, (((0, Wb, 0, Lb, zb),),), Wb, Lb)
        out.append("1 block alone        base=%-5s top Z %.2f  X spare %6.2f  Y spare %6.2f  Z clear %6.2f at %s  => %s" % (
            bname, zb, r["sx"], r["sy"], r["z"], r["who"][:58], "FITS" if r["fit_xy"] and r["z"] >= 0 else "NO"))
        # 2 board P on top, three part heights
        for tall, why in ((pf.P_TALL, "Keystone 3568 with its blade"), (pf.P_XH, "JST XH"), (6.4, "the first issue's 8 mm board")):
            zt = zb + 0.5 + pf.P_BOARD["T"] + tall
            variants = tuple(((0, Wb, 0, Lb, zb), (0, pf.P_BOARD["W"], y0, y0 + pf.P_BOARD["L"], zt)) for y0 in (0.0, Lb - pf.P_BOARD["L"]))
            r = pf.place(pf.WEST, variants, max(Wb, pf.P_BOARD["W"]), Lb)
            out.append("2 board P on top     base=%-5s parts %5.2f (%s): top Z %.2f  Z clear %6.2f at %s  => %s" % (
                bname, tall, why, zt, r["z"], r["who"][:58], "FITS" if r["fit_xy"] and r["z"] >= 0 else "NO"))
        # 3 board P beside the block: A06's own end and side arrangements
        for bms in ("end", "side"):
            rr = pf.boxes_for("18650", 12, "3x2", bms, "minimal", base)
            variants, OW, OL, info = rr
            r = pf.place(pf.WEST, variants, OW, OL)
            if r["fit_xy"]:
                verdict = "FITS" if r["z"] >= 0 else "NO (height)"
                out.append("3 board P %-5s      base=%-5s group %.2f x %.2f  X spare %6.2f  Y spare %6.2f  Z clear %6.2f  => %s" % (bms, bname, OW, OL, r["sx"], r["sy"], r["z"], verdict))
            else:
                out.append("3 board P %-5s      base=%-5s group %.2f x %.2f  X spare %6.2f  Y spare %6.2f  => NO (%s)" % (
                    bms, bname, OW, OL, r["sx"], r["sy"], "width" if r["sx"] < 0 else "length"))
    # 4 a second board P in the east pocket, beside the ruled group
    ex = pf.EAST["x"][1] - pf.EAST["x"][0]
    ey = pf.EAST["y"][1] - pf.EAST["y"][0]
    grp = Lb + 2.0 + pf.P_BOARD["L"]
    free_y = ey - grp
    out.append("4 east pocket %.0f x %.0f: the ruled group (block, 2.0, board P) is %.2f long, leaving %.2f in Y; a second board P needs %.1f (its short side) plus 2.0: %s" % (
        ex, ey, grp, free_y, pf.P_BOARD["W"], "FITS in length" if free_y >= pf.P_BOARD["W"] + 2.0 else "NO"))
    out.append("  and beside the block in X: pocket %.1f less block %.2f = %.2f against board P's %.1f + 1.6 + %.2f on edge: NO" % (
        ex, Wb, ex - Wb, 1.0, pf.P_TALL))
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
