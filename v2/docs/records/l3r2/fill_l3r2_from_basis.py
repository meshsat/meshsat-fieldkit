#!/usr/bin/env python3
"""Fill l3r2.yaml's HELD figures from the filed, checked energy basis by exact keys (L3-R2, MESHSAT-1357, 30 September
2026). PREPARED, NOT RUN: it refuses until set_energy_basis.py has named the basis with an accepted check.

What it writes, and nothing else:
  1. row L3-OD6's table (`quantified.rows`): each row's figures from weather_basis.out B by the exact key of its basis
     (mean-day, 50, 80, 95) and build (TYP, WAB), with `evidence` naming the output and its section; every row's old line
     is asserted to carry null figures first;
  2. `basis_figures`: the reference plane per lid and case (energy_basis.out 5), the modelled historical coverage per lid
     and case (weather_basis.out A), the lids' current stores and the allowances between nominal and usable
     (weather_basis.out B), with the files' paths and shas.
Every figure is the text the output prints (basis_reader.py). The result is re-parsed and read back against the reader's
output; a second run is refused. The rows' prose (recommendations, consequences, the R11 table's conditional column,
finding F-01) is restated by the session from these figures afterwards, cited to their sections; this script writes no
prose.

Usage: python3 fill_l3r2_from_basis.py [--check] [--data PATH --root DIR]   (a copy and its tree: the tests)
"""
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402
import basis_reader as BR  # noqa: E402

ORDER = ("id", "option", "share", "build", "asks", "limits", "usable_wh", "lid_block", "cells", "nominal_wh", "mass_kg",
         "volume_cyl_l", "volume_box_l", "x_wh", "x_cells", "fits", "evidence")
PLAIN = ("id", "option", "build")


def flow(row):
    out = []
    for k in ORDER:
        v = row.get(k)
        if v is None: s = "null"
        elif isinstance(v, list): s = "[%s]" % ", ".join(v)
        elif isinstance(v, int) or k in PLAIN: s = str(v)
        else: s = json.dumps(v, ensure_ascii=False)
        out.append("%s: %s" % (k, s))
    return "        - {%s}" % ", ".join(out)


def arg(argv, k, default=None):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else default


def main(argv):
    import yaml
    data_path = arg(argv, "--data", C.L3DATA)
    root = arg(argv, "--root", E.TOP)
    try:
        raw = open(data_path, encoding="utf-8").read()
        data = yaml.safe_load(raw)
        ok, why = C.basis_state(data, root)
        if not ok: E.refuse("the energy basis is not filed with an accepted check: %s" % why)
        if data.get("basis_figures") is not None: E.refuse("basis_figures is filled: this script has run")
        v = data["energy_basis"]
        outs = {os.path.basename(str(o["path"])): o for o in v["outputs"]}
        for need in ("weather_basis.out", "energy_basis.out"):
            if need not in outs: E.refuse("energy_basis names no %s" % need)
        wpath, epath = outs["weather_basis.out"]["path"], outs["energy_basis.out"]["path"]
        w = open(os.path.join(root, wpath), encoding="utf-8").read()
        e = open(os.path.join(root, epath), encoding="utf-8").read()
        try:
            siz, cov, sto, alw, ref = BR.sizing(w), BR.coverage(w), BR.stores(w), BR.allowances(w), BR.reference_plane(e)
        except BR.BasisError as x:
            E.refuse("the filed outputs do not read: %s" % x)
        q = next(x for x in data["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]
        new = raw
        for r in q:
            key = ("mean-day" if r["option"] == "mean-day" else str(r["share"]), r["build"])
            if key not in siz: E.refuse("weather_basis.out B has no row %s for %s" % (key, r["id"]))
            if any(r.get(k) is not None for k in C.FIGS): E.refuse("row %s already carries figures" % r["id"])
            old = flow(r)
            if new.count(old + "\n") != 1: E.refuse("row %s's line is not where fill expects it" % r["id"])
            filled = dict(r, **siz[key], evidence="%s B" % wpath)
            new = new.replace(old + "\n", flow(filled) + "\n", 1)
        figs = {"source": {"weather_basis": {"path": wpath, "sha16": outs["weather_basis.out"]["sha16"]},
                           "energy_basis": {"path": epath, "sha16": outs["energy_basis.out"]["sha16"]},
                           "record": v["record"], "tip": v.get("tip")},
                "reference_plane": {"%s|%s" % k: val for k, val in sorted(ref.items())},
                "coverage": {"%s|%s" % k: val for k, val in sorted(cov.items())},
                "stores": sto, "allowances": alw}
        block = "basis_figures:\n" + "".join("  " + l + "\n" for l in yaml.safe_dump(
            figs, default_flow_style=False, sort_keys=True, width=4096, allow_unicode=True).rstrip("\n").split("\n"))
        if new.count("basis_figures: null\n") != 1: E.refuse("basis_figures: null is not where fill expects it")
        new = new.replace("basis_figures: null\n", block, 1)
        d2 = yaml.safe_load(new)
        q2 = next(x for x in d2["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]
        for r in q2:
            key = ("mean-day" if r["option"] == "mean-day" else str(r["share"]), r["build"])
            for k, val in siz[key].items():
                if r.get(k) != val: E.refuse("read back: %s %s is %r, the basis prints %r" % (r["id"], k, r.get(k), val))
        if d2["basis_figures"]["reference_plane"] != figs["reference_plane"]: E.refuse("read back: basis_figures differs")
        for dch in E.DASHES:
            if dch in new: E.refuse("the result carries a dash character")
    except E.Refused as x:
        print("fill_l3r2_from_basis: REFUSED: %s" % x)
        return 2
    print("fill_l3r2_from_basis: %d rows of L3-OD6 filled from %s; basis_figures: %d reference-plane cases, %d coverage "
          "cases, %d stores, %d allowances%s" % (len(q), wpath, len(ref), len(cov), len(sto), len(alw),
                                                   " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(data_path, "w", encoding="utf-8").write(new)
        print("fill_l3r2_from_basis: written %s" % os.path.relpath(data_path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
