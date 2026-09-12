#!/usr/bin/env python3
"""Whether a packer region is big enough for the parts assigned to it.

12 September 2026 (MESHSAT-862). Every placement generator printed `WARNING region X overflows by N mm`
and carried on placing the parts that did not fit OUTSIDE the rectangle, on top of whatever stood there.
Nothing read the line. B19's committed placement overflows six regions, `IOCA` by 10.2 mm, and has since
the day the regions were drawn; moving the coin cell into `GAP12` under owner decision 11 added 22.9 mm
more and the hard violations the loop's legality guard found on the placed board are what that looks like
downstream. A warning that is followed by the action it warns about is not a warning.

So an overflow BLOCKS. A board that has a reason to overflow declares it in `tools/boards/<letter>.json`
as `region_overflow_allow_mm` with its number, which is the `placed_hard_allowance` idiom: a declared
number with a reason beside it, never a default that hides the measurement.

Region rectangles are on the never-auto floor (`reserved.json`, "region definitions in the packer"), so
the fix for an overflow this does not permit is an owner decision, not an edit.
"""
import atexit, json, os, sys

_SEEN = []
_ALLOW = None


def allowance(letter):
    """The declared overflow this board may have, in millimetres, default zero."""
    global _ALLOW
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(here, "boards", "%s.json" % letter), encoding="utf-8") as fh:
            _ALLOW = float(json.load(fh).get("region_overflow_allow_mm", 0.0))
    except Exception:
        _ALLOW = 0.0
    return _ALLOW


def note(name, mm):
    """One region that did not hold its parts. Printed as it happens, judged at exit."""
    _SEEN.append((name, float(mm)))
    print("WARNING region %s overflows by %.1f mm" % (name, mm))


@atexit.register
def _judge():
    if not _SEEN:
        return
    allow = _ALLOW if _ALLOW is not None else 0.0
    over = [(n, m) for n, m in _SEEN if m > allow + 0.001]
    worst = max(m for _, m in _SEEN)
    print("region fit: %d region(s) overflow, worst %.1f mm, declared allowance %.1f mm"
          % (len(_SEEN), worst, allow))
    if not over:
        return
    print("BLOCK %d region(s) are smaller than the parts assigned to them, and the packer puts what does"
          % len(over))
    print("      not fit OUTSIDE the rectangle, on top of whatever is there:")
    for n, m in sorted(over, key=lambda t: -t[1]):
        print("        %-10s %.1f mm" % (n, m))
    print("      A region rectangle is reserved to the owner (reserved.json, region definitions in the")
    print("      packer), so this is a decision with evidence and not an edit. Declare the number in")
    print("      tools/boards/<letter>.json as region_overflow_allow_mm with its reason to carry on.")
    sys.stdout.flush()
    os._exit(1)
