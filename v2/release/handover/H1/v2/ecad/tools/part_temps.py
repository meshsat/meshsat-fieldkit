#!/usr/bin/env python3
"""Every part this project has a temperature for, against the envelope this project adopted (21 September 2026).

WHY IT EXISTS. Decision 34 adopted the operating envelope on 21 September and `pcb_envelope.yaml` carries it as
data. Reading the Ethernet documents an hour later found that board B's T1, the Pulse H5007NL magnetics, is a
0 to +70 C part on a kit whose envelope goes to -20 C, and that NO RULE IN THIS PROJECT compares the two:
CMP-001 is written about absolute maximum ratings and `derate.py` reads voltage alone. This is the comparison,
and it is the first day it could be made at all.

WHAT IT JUDGES, per board, from the committed netlist:

  * the COLD end against the envelope's ambient minimum, because nothing in the kit warms the air below
    ambient: a part whose minimum is above -20 C is outside its own range at the envelope's floor.
  * the HOT end against the envelope's INSIDE AIR, for a part that sits inside: the envelope's own carve-out
    says the kit runs the reduced mode above +35 C ambient, so the worst inside air is the larger of
    (40 + the one-module rise) and (35 + the three-module rise), which is 51 C on today's numbers. A part in
    the plate, on the outside face or in the pack bay is judged against the ambient maximum, and the tool
    SAYS it has no solar figure for the plate rather than inventing one.
  * a declared CARVE-OUT is reported with the envelope's own words and never silently passed.

WHAT IT DOES NOT DO. It does not invent a range for a part whose sheet this tree does not hold: those are
counted as UNDECLARED and named, and the pack cells are in the declaration's `owed` list with the reason. It
is ADVISORY today, like `via_current` was when it could not tell a transition from a via that carries nothing:
thirteen declared parts of a set that carries hundreds is a beginning and not a denominator, and a rule that
failed a board on a denominator of thirteen would be claiming more than it knows.

Usage: part_temps.py [--board <letter>] [--json]
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ENVELOPE = os.path.join(HERE, "pcb_envelope.yaml")
PARTS = os.path.join(HERE, "pcb_part_temps.yaml")
ECAD = os.path.dirname(HERE)
BOARDS = {"a": "pcb-a-power", "b": "pcb-b-compute", "c": "pcb-c-display", "d": "pcb-d-aprs",
          "e": "pcb-e1-dock", "e5": "pcb-e5-block", "p": "pcb-p-pack"}


def _yaml(path):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8"))


def inside_air_max(env):
    """The worst inside air the envelope's own numbers allow, and the sentence that explains it."""
    a = env["ambient_c"]["in_use"]
    rise = env["inside_air_rise_k"]
    reduced_above = None
    for co in env["ambient_c"]["carve_outs"]:
        if "above_c" in co and "reduced mode" in str(co.get("what", "")):
            reduced_above = co["above_c"]
    full = a["max"] + rise["one_module_lid_open"] if reduced_above is not None else \
        a["max"] + rise["three_modules_loaded_lid_open"]
    loaded = (reduced_above + rise["three_modules_loaded_lid_open"]) if reduced_above is not None else full
    why = ("the envelope's carve-out runs the reduced mode above %s C ambient, so the worst inside air is the "
           "larger of %d + %d and %s + %d" % (reduced_above, a["max"], rise["one_module_lid_open"],
                                              reduced_above, rise["three_modules_loaded_lid_open"])) \
        if reduced_above is not None else "no reduced-mode carve-out is declared, so the loaded rise applies at the ambient maximum"
    return max(full, loaded), why


def _components(letter):
    """[(ref, value, lcsc)] from the board's committed netlist, or [] when there is none."""
    import glob
    stem = BOARDS[letter]
    cands = glob.glob(os.path.join(ECAD, stem + "*", "out", stem + ".net"))
    if not cands:
        return []
    t = open(sorted(cands)[0], encoding="utf-8", errors="replace").read()
    out = []
    for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)(.*?)\(tstamps ', t, re.S):
        blk = m.group(3)
        lc = re.search(r'\(field \(name "LCSC"\) "([^"]*)"\)', blk)
        out.append((m.group(1), m.group(2), (lc.group(1) if lc else "")))
    return out


def judge(env=None, parts=None, only=None):
    env = env or _yaml(ENVELOPE)
    decl = parts or _yaml(PARTS)
    amb = env["ambient_c"]["in_use"]
    inside_max, inside_why = inside_air_max(env)
    rows_by_board = {}
    for letter in sorted(BOARDS):
        if only and letter != only:
            continue
        comps = _components(letter)
        rows, fails, notes, undeclared = [], [], [], []
        for ref, value, lcsc in comps:
            d = None
            for p in decl["parts"]:
                if p.get("lcsc") and lcsc and p["lcsc"] == lcsc:
                    d = p
                    break
                m = p.get("match")
                if m and m.lower() in value.lower():
                    d = p
                    break
            if d is None:
                undeclared.append(ref)
                continue
            where = d.get("where", "inside")
            bar_max = inside_max if where == "inside" else amb["max"]
            row = dict(board=letter, ref=ref, part=d["name"], where=where,
                       min_c=d["min_c"], max_c=d["max_c"],
                       ambient_min=amb["min"], bar_max=bar_max, carve_out=d.get("carve_out"))
            rows.append(row)
            cold = d["min_c"] > amb["min"]
            hot = d["max_c"] < bar_max
            if (cold or hot) and d.get("carve_out"):
                notes.append("%s %s (%s): %s to %s C against %s to %s C, and the envelope declares it: %s"
                             % (letter.upper(), ref, d["name"], d["min_c"], d["max_c"], amb["min"], bar_max,
                                d["carve_out"].strip()))
                row["declared"] = True
                continue
            if cold:
                fails.append("%s %s (%s) is rated from %s C and the envelope's ambient minimum is %s C, so it is "
                             "outside its own range over the coldest %d K" % (letter.upper(), ref, d["name"],
                                                                              d["min_c"], amb["min"],
                                                                              d["min_c"] - amb["min"]))
            if hot:
                fails.append("%s %s (%s) is rated to %s C and this board's worst air is %s C (%s)"
                             % (letter.upper(), ref, d["name"], d["max_c"], bar_max, inside_why))
        rows_by_board[letter] = dict(rows=rows, fails=fails, notes=notes,
                                     undeclared=undeclared, components=len(comps))
    return rows_by_board, inside_max, inside_why


def main(argv):
    only = _v.opt(argv, "--board", None)
    res, inside_max, inside_why = judge(only=only)
    judged = sum(len(v["rows"]) for v in res.values())
    fails = [f for v in res.values() for f in v["fails"]]
    notes = [n for v in res.values() for n in v["notes"]]
    undec = sum(len(v["undeclared"]) for v in res.values())
    comps = sum(v["components"] for v in res.values())
    print("part_temps: %d part instance(s) judged of %d on %d board(s) against the adopted envelope; "
          "%d outside it, %d declared carve-out(s), %d with no range in this tree"
          % (judged, comps, len(res), len(fails), len(notes), undec))
    print("  the worst inside air this envelope allows is %d C: %s" % (inside_max, inside_why))
    for f in fails[:20]:
        print("  OUTSIDE %s" % f)
    for n in notes[:8]:
        print("  carve-out %s" % n[:200])
    if "--json" in argv:
        print(json.dumps(res, indent=1))
    # ADVISORY, and the reason is the denominator: thirteen declared parts on boards that carry hundreds is a
    # beginning. A rule that failed a board on that denominator would claim more than it knows, which is the
    # defect this project met in `via_current` on 18 September and in STK-001's PASS of zero pairs before that.
    note = ("every part with a published operating range in this tree, against the envelope decision 34 adopted; "
            "ADVISORY: %d of %d part instances carry a range here, so a board's silence is this file's gap and "
            "not the board's answer" % (judged, comps))
    for letter, v in sorted(res.items()):
        _v.write("part_temps_%s" % letter,
                 _v.FAIL if v["fails"] else (_v.INCONCLUSIVE if not v["rows"] else _v.PASS),
                 counts={"judged": len(v["rows"]), "outside": len(v["fails"]),
                         "carve_outs": len(v["notes"]), "undeclared": len(v["undeclared"]),
                         "components": v["components"]},
                 denominator=len(v["rows"]), evidence=(v["fails"][:10] or v["notes"][:4]),
                 inputs={"envelope": os.path.basename(ENVELOPE), "parts": os.path.basename(PARTS)},
                 note=note, advisory=True, quiet=True)
    return _v.write("part_temps", _v.FAIL if fails else (_v.INCONCLUSIVE if not judged else _v.PASS),
                    counts={"judged": judged, "components": comps, "outside": len(fails),
                            "carve_outs": len(notes), "undeclared": undec},
                    denominator=judged, evidence=fails[:20],
                    inputs={"envelope": os.path.basename(ENVELOPE), "parts": os.path.basename(PARTS)},
                    note=note, advisory=True)


if __name__ == "__main__":
    sys.exit(_v.guard("part_temps", main, sys.argv[1:]))
