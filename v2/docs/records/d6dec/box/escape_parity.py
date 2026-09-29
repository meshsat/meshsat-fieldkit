#!/usr/bin/env python3
"""The escape pass lays the same copper after the selection moved and the cost report was added (T1, T4).

Usage (on the KiCad box): escape_parity.py <base checkout> <new checkout> <work dir> <out.json>
For each of the six committed boards of the phase folders: the board is loaded, every track and via is taken off
it, and that bare placed board is saved twice with its project file and its intent file. The escape pass of the
base checkout (73ae2f21) runs on one copy and this branch's on the other, each from its own tools directory and
under the board's own escape environment (tools/boards/<letter>.json). The two results are compared copper item by
copper item: every via by position, net, size and drill, every track by its ends, width, layer and net.

A bare board is not the placed stage of the chain (its zones are the routed board's), and it does not have to be:
the question is whether two programs given the SAME board lay the SAME copper."""
import os, sys, json, shutil, subprocess, hashlib

BOARDS = [("a", "pcb-a-power-a23", "pcb-a-power"), ("b", "pcb-b-compute-b19", "pcb-b-compute"),
          ("c", "pcb-c-display-c8", "pcb-c-display"), ("d", "pcb-d-aprs-d9", "pcb-d-aprs"),
          ("e", "pcb-e1-dock-e7", "pcb-e1-dock"), ("p", "pcb-p-pack-p2", "pcb-p-pack")]


def _sub(*args):
    """One board per process: a second LoadBoard in one KiCad 9.0.9 process came back as a bare SwigPyObject here
    (28 September 2026), so every read and every write of a board is its own run of this file."""
    r = subprocess.run([sys.executable, os.path.abspath(__file__)] + list(args), capture_output=True, text=True, timeout=1800)
    if r.returncode != 0: raise SystemExit("escape_parity: %s failed:\n%s" % (" ".join(args[:2]), (r.stdout + r.stderr)[-800:]))
    return r.stdout


def copper(path):
    v, t = json.loads(_sub("--copper", path).strip().splitlines()[-1])
    return [tuple(x) for x in v], [tuple(x) for x in t]


def _copper(path):
    import pcbnew
    b = pcbnew.LoadBoard(path); vias, tracks = [], []
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            vias.append((t.GetPosition().x, t.GetPosition().y, t.GetNetname(), t.GetWidth(pcbnew.F_Cu), t.GetDrill(), bool(t.IsLocked())))
        else:
            tracks.append((t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetWidth(), t.GetLayerName(), t.GetNetname(), bool(t.IsLocked())))
    print(json.dumps([sorted(vias), sorted(tracks)]))


def bare(src, dst):
    _sub("--bare", src, dst)


def _bare(src, dst):
    import pcbnew
    b = pcbnew.LoadBoard(src)
    for t in list(b.GetTracks()): b.Remove(t)
    pcbnew.SaveBoard(dst, b)


def main(a):
    base, new, work, out = a[0], a[1], a[2], a[3]
    rows = []
    for letter, phase, stem in BOARDS:
        src = os.path.join(new, "v2", "ecad", phase)
        env = dict(os.environ); env.pop("ESCAPE_SKIP", None); env["PYTHONDONTWRITEBYTECODE"] = "1"
        table = json.load(open(os.path.join(new, "v2", "ecad", "tools", "boards", letter + ".json")))
        for k, v in (table.get("escape_env") or {}).items(): env[k] = str(v)
        res = {}
        seed = os.path.join(work, "seed", phase); shutil.rmtree(seed, ignore_errors=True); os.makedirs(os.path.join(seed, "out"))
        bare(os.path.join(src, stem + ".kicad_pcb"), os.path.join(seed, stem + ".kicad_pcb"))
        for f in (stem + ".kicad_pro", "out/" + stem + "-intent.json"):
            if os.path.exists(os.path.join(src, f)): shutil.copy(os.path.join(src, f), os.path.join(seed, f))
        seed_sha = hashlib.sha256(open(os.path.join(seed, stem + ".kicad_pcb"), "rb").read()).hexdigest()[:16]
        for label, root in (("before", base), ("after", new)):
            d = os.path.join(work, label, phase); shutil.rmtree(d, ignore_errors=True); shutil.copytree(seed, d)
            r = subprocess.run([sys.executable, os.path.join(root, "v2", "ecad", "tools", "escape.py"), stem + ".kicad_pcb"],
                               cwd=d, env=env, capture_output=True, text=True, timeout=3600)
            o = r.stdout + r.stderr
            open(os.path.join(d, "escape.log"), "w").write(o)
            v, t = copper(os.path.join(d, stem + ".kicad_pcb"))
            res[label] = {"exit": r.returncode, "vias": len(v), "tracks": len(t),
                          "copper_sha": hashlib.sha256(json.dumps([v, t]).encode()).hexdigest()[:16],
                          "summary": [l for l in o.split("\n") if l.startswith("escape: ") and "escapes added" in l],
                          "cost": [l for l in o.split("\n") if l.startswith("escape: ") and ("decoupling cost" in l or " lost " in l or "left to the router" in l or "refused by the far-side" in l)],
                          "no_escape": sorted(l.split("  lost to")[0].strip() for l in o.split("\n") if l.strip().startswith("no escape for")),
                          "_v": v, "_t": t}
        same = res["before"]["_v"] == res["after"]["_v"] and res["before"]["_t"] == res["after"]["_t"] \
            and res["before"]["no_escape"] == res["after"]["no_escape"] and res["before"]["exit"] == res["after"]["exit"] == 0
        for k in ("before", "after"): res[k].pop("_v"); res[k].pop("_t"); res[k]["no_escape"] = len(res[k]["no_escape"])
        rows.append({"board": letter, "phase": phase, "escape_env": table.get("escape_env") or {}, "bare_board_sha256_16": seed_sha,
                     "same_copper": same, "before": res["before"], "after": res["after"]})
        print("%s %-20s same copper %s | before %d vias %d tracks %s | after %d vias %d tracks %s" % (
            letter, phase, same, res["before"]["vias"], res["before"]["tracks"], res["before"]["copper_sha"],
            res["after"]["vias"], res["after"]["tracks"], res["after"]["copper_sha"]))
        for l in res["after"]["cost"][:12]: print("     " + l[:240])
    json.dump({"what": "escape.py before and after, on the six committed boards stripped of their copper", "rows": rows}, open(out, "w"), indent=1)
    return 0 if all(r["same_copper"] for r in rows) else 1


if __name__ == "__main__":
    if sys.argv[1:2] == ["--copper"]: _copper(sys.argv[2]); sys.exit(0)
    if sys.argv[1:2] == ["--bare"]: _bare(sys.argv[2], sys.argv[3]); sys.exit(0)
    sys.exit(main(sys.argv[1:]))
