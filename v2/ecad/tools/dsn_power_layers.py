#!/usr/bin/env python3
"""The power-layer treatment of a DSN, as a tool, with the keep-out kinds told apart (21 September 2026).

`route_one.sh` has carried this as an inline heredoc since 5 September 2026 (B15): a plane layer becomes a
POWER layer in the DSN, so Freerouting lays no wire there and lets vias pass, and the board-wide keep-outs on
that layer are dropped, because a board-wide wire keep-out polygon on a plane made the router thrash for its
whole time limit (the B14 In1 test and B15 run 1).

**It matched one spelling of three and the sense fence writes another.** KiCad exports a rule area that
forbids TRACKS as `(wire_keepout ...)`, one that forbids VIAS as `(via_keepout ...)`, and one that forbids
BOTH as `(keepout ...)`. `sense_fence.py` sets both, so its areas leave KiCad as `(keepout` and the inline
drop, which searches for `(wire_keepout`, never sees them. Measured on E38's own DSN, the fence arm of board
E: 34 `(keepout`, 2 `(wire_keepout`, 0 `(via_keepout`, and the eleven the fence added are all of the first
kind. Nothing in flight is hurt by that, because both fencing boards (A and E) fence F.Cu and B.Cu and
neither is a power layer; what it means is that the FIRST board to fence an inner plane layer would hand the
router the polygon this block exists to remove, and the failure would look like a route that thrashes.

**The three kinds are not one question, so this does not simply drop more.** On a power layer Freerouting
routes no wire at all, so a wire keep-out there is redundant and is dropped, as before. A via keep-out is NOT
redundant: vias cross a power layer, and forbidding one there is a real instruction of the board's, so it
stands. A keep-out that forbids both is redundant in its wire half and real in its via half, so it is
REWRITTEN to a via keep-out rather than dropped, which keeps the instruction and removes the polygon that
makes the router thrash. A block naming both a power layer and a signal layer is left alone and reported;
KiCad writes one polygon per keep-out block (checked on E38's DSN: every one of the 36 blocks names exactly
one layer), so that branch is a guard and not a case anyone has met.

Usage: dsn_power_layers.py <file.dsn> <layer> [<layer> ...]   -> rewrites the file in place; exit 0.
       --dry-run prints what it would do and writes nothing."""
import re
import sys

TOKENS = ("(keepout", "(wire_keepout", "(via_keepout")


def _block(s, j):
    """The balanced-parenthesis block starting at s[j] == '('; returns its end index inclusive."""
    depth = 0
    k = j
    while k < len(s):
        if s[k] == "(":
            depth += 1
        elif s[k] == ")":
            depth -= 1
            if depth == 0:
                return k
        k += 1
    return len(s) - 1


def _next_keepout(s, i):
    """(index, token) of the earliest keep-out of any kind at or after i, or (-1, None)."""
    best, tok = -1, None
    for t in TOKENS:
        j = s.find(t, i)
        if j >= 0 and (best < 0 or j < best):
            best, tok = j, t
    return best, tok


def layer_types(s, layers):
    """Every named layer's (type signal) becomes (type power). Returns the new text and the count."""
    n = 0
    for lay in layers:
        s, k = re.subn(r"(\(layer %s\s*\(type )signal(\))" % re.escape(lay), r"\1power\2", s)
        n += k
    return s, n


def keepouts(s, layers):
    """Drop the wire keep-outs on a power layer, rewrite the full ones there to via keep-outs.

    Returns (text, dropped, rewritten, kept_via, mixed)."""
    out = []
    i = 0
    dropped = rewritten = kept = mixed = 0
    while True:
        j, tok = _next_keepout(s, i)
        if j < 0:
            out.append(s[i:])
            break
        k = _block(s, j)
        block = s[j:k + 1]
        on = re.findall(r"\(polygon (\S+)", block)
        power = [lay for lay in on if lay in layers]
        out.append(s[i:j])
        if not power:                                        # nothing of it is on a power layer
            out.append(block)
        elif len(power) != len(on):                          # a block over both kinds of layer: never guessed at
            mixed += 1
            out.append(block)
        elif tok == "(wire_keepout":                         # redundant where no wire is routed (B14, B15)
            dropped += 1
        elif tok == "(keepout":                              # the wire half is redundant, the via half is not
            rewritten += 1
            out.append("(via_keepout" + block[len(tok):])
        else:                                                # a via keep-out on a plane is a real instruction
            kept += 1
            out.append(block)
        i = k + 1
    return "".join(out), dropped, rewritten, kept, mixed


def main(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if len(argv) < 2:
        print(__doc__.strip().splitlines()[-2].strip())
        return 2
    fn, layers = argv[0], argv[1:]
    s = open(fn, encoding="utf-8", errors="replace").read()
    s, n1 = layer_types(s, layers)
    s, dropped, rewritten, kept, mixed = keepouts(s, layers)
    if not dry:
        open(fn, "w", encoding="utf-8").write(s)
    print("power layers in the DSN: %s (%d layer types changed, %d wire keep-outs dropped)"
          % (", ".join(layers), n1, dropped))
    print("power layers in the DSN: %d full keep-out(s) rewritten to via keep-outs, %d via keep-out(s) kept, "
          "%d block(s) over a power and a signal layer left alone" % (rewritten, kept, mixed))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
