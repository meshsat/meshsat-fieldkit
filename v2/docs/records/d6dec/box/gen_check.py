#!/usr/bin/env python3
"""The six schematic generators run once under this branch's intent.py (T5), outside every tree's out/.

Usage (on the KiCad box): gen_check.py <checkout root> <out.json>
For each board the project folder is copied to <checkout>/v2/ecad/gencheck-<letter> (inside the box clone, so the
generator's `../meshsat.pretty` and `../tools` resolve as in full.sh), the generator runs there as full.sh runs it
(`gen_sch_<x>.py <stem>.kicad_sch <stem>`, PHASE from the board table), and the intent it writes is compared with the
committed phase folder's intent, `written` left out. The question is whether `intent.write` now refuses any of the six,
and whether it writes what is committed. The copies are removed afterwards."""
import os, sys, json, shutil, subprocess

BOARDS = [("a", "pcb-a-power-a23", "pcb-a-power"), ("b", "pcb-b-compute-b19", "pcb-b-compute"),
          ("c", "pcb-c-display-c8", "pcb-c-display"), ("d", "pcb-d-aprs-d9", "pcb-d-aprs"),
          ("e", "pcb-e1-dock-e7", "pcb-e1-dock"), ("p", "pcb-p-pack-p2", "pcb-p-pack")]


def main(a):
    root, out = a[0], a[1]; ecad = os.path.join(root, "v2", "ecad"); rows = []
    for L, phase, stem in BOARDS:
        d = os.path.join(ecad, "gencheck-" + L); shutil.rmtree(d, ignore_errors=True)
        shutil.copytree(os.path.join(ecad, stem), d)
        cfg = json.load(open(os.path.join(ecad, "tools", "boards", L + ".json")))
        env = dict(os.environ); env["PYTHONDONTWRITEBYTECODE"] = "1"
        if cfg.get("phase") and not env.get("PHASE"): env["PHASE"] = str(cfg["phase"])
        os.makedirs(os.path.join(d, "out"), exist_ok=True)
        r = subprocess.run([sys.executable, os.path.join(ecad, "tools", "gen_sch_%s.py" % L), stem + ".kicad_sch", stem],
                           cwd=d, env=env, capture_output=True, text=True, timeout=1800)
        o = r.stdout + r.stderr
        ip = os.path.join(d, "out", stem + "-intent.json")
        new = json.load(open(ip)) if os.path.exists(ip) else None
        old = json.load(open(os.path.join(ecad, phase, "out", stem + "-intent.json")))
        row = {"board": L, "exit": r.returncode, "intent_written": new is not None,
               "refused": [l for l in o.splitlines() if "decision 42, T5" in l and "without a ruled class" in l],
               "noted": [l for l in o.splitlines() if "noted, not refused" in l],
               "tail": o.splitlines()[-4:]}
        if new is not None:
            for x in (new, old): x.pop("written", None)
            row["same_as_committed"] = new == old
            if new != old:
                row["keys_differing"] = sorted(k for k in set(new) | set(old) if new.get(k) != old.get(k))
                nb = {e.get("cap"): e for e in new.get("bypass", [])}; ob = {e.get("cap"): e for e in old.get("bypass", [])}
                row["bypass_only_new"] = sorted(set(nb) - set(ob)); row["bypass_only_committed"] = sorted(set(ob) - set(nb))
                row["bypass_changed"] = sorted(c for c in set(nb) & set(ob) if nb[c] != ob[c])[:40]
        rows.append(row)
        print("%s exit %d, intent written %s, same as committed %s, %d refused line(s), %d noted line(s)%s" % (
            L, r.returncode, new is not None, row.get("same_as_committed"), len(row["refused"]), len(row["noted"]),
            ("; differing keys %s" % row.get("keys_differing")) if row.get("keys_differing") else ""))
        if r.returncode != 0: print("   " + " | ".join(row["tail"])[:600])
        shutil.rmtree(d, ignore_errors=True)
    json.dump({"what": "the six schematic generators under this branch's intent.py; intents compared with the committed ones",
               "rows": rows}, open(out, "w"), indent=1)
    return 0 if all(r["exit"] == 0 for r in rows) else 1


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
