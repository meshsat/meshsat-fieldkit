#!/usr/bin/env python3
"""apply_gen_sch_b_gndret.py: DRAFT for board B's generator owner (Layer 8 record l8r2, round 7, task T5b, the owner's review of
4 October 2026 RSM-01, MESHSAT-1357). NOT APPLIED to the tree by this record; its author ran it only on scratch copies (the tests
write scratch copies).

The defect. gen_sch_b.py declares the board's return with typed figures:
  _intent.rail("GND", 0.0, 10.0, 21.0, ["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV"], loads=_GND_LOADS, ...,
               note="... 19.4 A with all four at their declared peak")
21.0 A was the sum of the four leads' declared peaks on 13 September (5.0 + 5.0 + 5.0 + 6.0). Slot 2's lead went to 5.63 A on
28 September (S-98) and this line did not move; this record's apply_gen_sch_b_fans12.py puts the coolers' step-ups on the slot rails
(0.69 A a slot where the fan header had 0.1 A; the three leads at 6.6 A), the loads then sum to 21.51 A and intent.rail stops the
generator (loads over 1.02 times the peak). Board B's composition in L4-E9's change-list order has not run to its end since, with
or without Layer 9's I-03 draft (record l9t5's apply_gen_sch_b_iocbuck.py), which adds a lead and its return.

The correction (the record's section 7, l8r2_gndret.out): the return's figures are DERIVED in the generator from the rails it
returns, so they cannot go stale when a lead is declared again:
  typical = the sum of the declared typical currents of every rail that arrives on one of the net's lead connectors;
  peak    = the sum of their declared peaks, an UPPER BOUND on what flows at one time, named so in the note;
  loads   = the leads' own allocations at their ground ends (_GND_LOADS, unchanged) plus the PoE port's return at the sense resistor
            R12, at +54V_POE's declared peak, which the list did not count; J_54V, whose pin 2 is on this net, becomes a source.
A lead connector whose rail is not declared, or a second rail on one connector, stops the generator. Nothing is typed: the figures
are 13.3 A and 22.23 A on the drawn generator, 13.3 A and 26.4 A with fans12, 13.3 A and 27.78 A with Layer 9's draft as well.
It is NOT a larger typed number: the same text on the drawn generator gives 22.23 A, and a lead declared lower lowers it.

What it does not correct (the record's finding L8R2-F31, OPEN): the return does not divide lead by lead. Boards A and B share one
ground, so the return divides between the five lead contacts and the seventeen ground conductors of the ribbons J_AB1 and J_AB2 by
resistance; l8r2_gndret.out section 3 gives the currents and what the makers' sheets do and do not bound.

What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else: the head of the GND rail call (a comment block, the helper
_gnd_return and its call in place of the typed _intent.rail head) and the call's note. The list of lead connectors and
"loads=_GND_LOADS" are left byte for byte, so record l9t5's draft, which extends that list and _GND_LOADS, applies before or after
this one; record l8gnd's GND-002 draft and this record's fans12, panel5v, ph4 and rt500 have their anchors elsewhere.

Usage:  apply_gen_sch_b_gndret.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the repository's
own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_b_gndret"
ADDS = ()
NETS = ()

_OLD_HEAD = '_intent.rail("GND", 0.0, 10.0, 21.0, '
_NEW_HEAD = '''# RECORD l8r2 ROUND 7 (task T5b, the owner's review of 4 October 2026, RSM-01; MESHSAT-1357): THE RETURN'S FIGURES ARE DERIVED
# FROM THE RAILS IT RETURNS, NOT TYPED. This call declared 10.0 A typical and 21.0 A peak. 21.0 was the sum of the four leads'
# peaks on 13 September (5.0 + 5.0 + 5.0 + 6.0); slot 2's lead went to 5.63 A on 28 September (S-98) and nothing moved this line,
# and with the coolers' step-ups on the slot rails (record l8r2's fans12 draft) the loads sum to 21.51 A, which intent.rail
# refuses. A larger typed number would go stale the same way, so the return reads its own leads:
#   typical  the sum of the typical currents of every rail that ARRIVES on one of this net's lead connectors;
#   peak     the sum of their declared peaks: an UPPER BOUND on what flows at one time (every lead at its own peak at once). The
#            largest state of Layer 9's budget and the coolers' bounded starts sit inside it; what board A's stages can push into
#            a fault is a fault current and belongs in the note, not in the peak (intent.py, "what amps_typ and amps_peak mean");
#   loads    the leads' own allocations at their ground ends (_GND_LOADS) plus the PoE port's return, which enters this net at
#            the sense resistor R12 and was not counted; its lead J_54V has pin 2 on this net and is a return lead as the others.
# A lead connector named here whose rail is not declared, or two rails on one connector, stops the generator.
# WHAT THIS DOES NOT SAY: that each lead's pin 2 carries its own rail's current. Boards A and B share one ground, so the return
# divides between the lead contacts and the seventeen ground conductors of the ribbons J_AB1 and J_AB2 by resistance (record
# l8r2 round 7, l8r2_gndret.out section 3, finding L8R2-F31, OPEN).
def _gnd_return(leads, loads, note, **kw):
    _srcs = list(leads) + ["J_54V"]
    _arr = sorted(n for n, r in _intent._I["rails"].items() if isinstance(r.get("source"), str) and r["source"] in _srcs
                  and not any(r.get(k) for k in ("fed_from", "series_of", "returns")))
    if sorted(_intent._I["rails"][n]["source"] for n in _arr) != sorted(_srcs):
        raise SystemExit("gen_sch_b: GND's return leads %s do not each carry exactly one arriving rail (found %s): declare the "
                         "lead's rail before the return, one rail a connector" % (sorted(_srcs), _arr))
    _typ = round(sum(_intent.rail_amps(n)[0] for n in _arr), 4); _peak = round(sum(_intent.rail_amps(n)[1] for n in _arr), 4)
    _l = dict(loads); _l["R12"] = _intent.rail_amps("+54V_POE")[1]
    _intent.rail("GND", 0.0, _typ, _peak, _srcs, loads=_l, note=note % (", ".join(_arr), _typ, _peak, sum(_l.values())), **kw)
_gnd_return('''

_OLD_NOTE = '             note="the return of every rail: the three slot rails and the device rail, 19.4 A with all four at their declared peak")\n'
_NEW_NOTE = ('             note="the return of every rail that arrives from board A (%s): %.2f A typical and %.2f A peak, the sums of "\n'
             '                  "those rails\' own declarations, the peak an UPPER BOUND on what flows at one time; the loads sum %.2f A, "\n'
             '                  "the leads\' allocations at their ground ends and the PoE port\'s return at R12. The return divides between "\n'
             '                  "the lead contacts and the ribbons\' ground conductors by resistance, not lead by lead (record l8r2 round 7)")\n')

EDITS = [(_OLD_HEAD, _NEW_HEAD), (_OLD_NOTE, _NEW_NOTE)]
# what must stay byte for byte, because record l9t5's draft anchors on it (its _OLD_GNDS and _OLD_GNDL)
KEPT = ('["J_5V_S1", "J_5V_S2", "J_5V_S3", "J_5V_DEV"', 'loads=_GND_LOADS', 'for _n in (1, 2, 3): _GND_LOADS.update(_SLOT_LOADS(_n))\n')


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "def _gnd_return(" in text:
        refuse("already applied (_gnd_return is defined in the target)")
    if "_gnd_return" in text:
        refuse("the name _gnd_return is already in use in the target")
    kept = {k: text.count(k) for k in KEPT}
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:60]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    for k, n in kept.items():
        if new.count(k) != n:
            refuse("the edit changed a text another draft anchors on: %r" % k[:50])
    if '_intent.rail("GND"' in new.replace('_intent.rail("GND", 0.0, _typ, _peak, _srcs', ""):
        refuse("a second GND rail call is left in the target")
    try:
        tree = ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "_gnd_return"]
    if len(calls) != 1 or len(calls[0].args) != 1 or sorted(k.arg for k in calls[0].keywords) != ["always_on", "always_on_why", "converted", "loads", "note"]:
        refuse("the patched call is not the one expected (one positional list, loads, converted, always_on, always_on_why, note)")
    return new


# NOT RELEASED: record l8r2 drafts this change for board B's generator owner and never applies it. Writing the repository's own
# gen_sch_b.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8r2's drafts wait on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
