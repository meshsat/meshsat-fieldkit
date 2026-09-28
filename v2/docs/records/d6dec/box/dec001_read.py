#!/usr/bin/env python3
"""What DEC-001 reads on each board's committed candidate under decision 42's rules (stream d6dec, T1 to T10).

INFORMATION FOR THE INTEGRATOR, NOT EVIDENCE. It runs outside every tree's out/: each phase folder of the checkout
is copied whole to <work>/<phase>, and this checkout's intent_checks.py runs there, so the verdicts it writes land
in the copy. Nothing here is a reading the rule registry may count: the checkout is a branch, not main, and the
readings are not re-taken by the tree's own helpers.

Usage (on the KiCad box): dec001_read.py <checkout root> <work dir> <out.json>
For each board it records the gate's decoupling summary line, the intent_decoupling verdict's counts, and every
bypass line by result: pass, justified (with why), recorded (classes A and B1), and every FAIL line grouped by cause."""
import os, sys, json, shutil, subprocess, re, hashlib

BOARDS = [("a", "pcb-a-power-a23", "pcb-a-power"), ("b", "pcb-b-compute-b19", "pcb-b-compute"),
          ("c", "pcb-c-display-c8", "pcb-c-display"), ("d", "pcb-d-aprs-d9", "pcb-d-aprs"),
          ("e", "pcb-e1-dock-e7", "pcb-e1-dock"), ("p", "pcb-p-pack-p2", "pcb-p-pack")]


def cause(line):
    """The cause of one FAIL line of the decoupling rule, from the gate's own wording."""
    if "pads found on the board" in line: return "declared, not on this board (the intent is newer than the placement)"
    if "shares the pin's net" in line: return "the capacitor is not on the pin's net on this board"
    if "no ruled class" in line or "is not one of" in line: return "no ruled class"
    if "refused" in line and "side opposite" in line: return "far side refused (%s)" % (
        "one-sided board" if "one side only" in line else "inside a fan" if "escape fan" in line else
        "over a through-hole part" if "through-hole" in line else "maker names the same side" if "same side" in line else "other")
    if "past its maker's" in line: return "past its maker's own distance"
    if "past the" in line and "screen" in line: return "past the class screen, no allowance names it"
    if "reaches no via or pour" in line: return "a pad reaches no via or pour within 1.5 mm"
    return "other"


def main(a):
    root, work, out = a[0], a[1], a[2]
    tool = os.path.join(root, "v2", "ecad", "tools", "intent_checks.py")
    rows = []
    for letter, phase, stem in BOARDS:
        src = os.path.join(root, "v2", "ecad", phase); d = os.path.join(work, phase)
        shutil.rmtree(d, ignore_errors=True); shutil.copytree(src, d)
        vd = os.path.join(d, "out")
        for f in os.listdir(vd):
            if f.endswith(".verdict.json"): os.remove(os.path.join(vd, f))     # only this run's verdicts are read
        env = dict(os.environ); env.pop("ESCAPE_SKIP", None); env["PYTHONDONTWRITEBYTECODE"] = "1"
        r = subprocess.run([sys.executable, tool, stem + ".kicad_pcb"], cwd=d, env=env, capture_output=True, text=True, timeout=3600)
        o = r.stdout + r.stderr
        open(os.path.join(d, "intent_checks.log"), "w").write(o)
        lines = [l for l in o.splitlines() if re.match(r"^(PASS|FAIL)  bypass ", l)]
        summary = [l for l in o.splitlines() if l.startswith("intent_checks: decoupling,") or "bypass-allow.txt line" in l]
        vp = os.path.join(vd, "intent_decoupling.verdict.json")
        v = json.load(open(vp)) if os.path.exists(vp) else {}
        fails = {}
        for l in lines:
            if l.startswith("FAIL"): fails.setdefault(cause(l), []).append(l[6:])
        just = [l[6:] for l in lines if l.startswith("PASS") and "counted as JUSTIFIED" in l]
        rec = [l[6:] for l in lines if l.startswith("PASS") and "counted as RECORDED" in l]
        board_sha = hashlib.sha256(open(os.path.join(src, stem + ".kicad_pcb"), "rb").read()).hexdigest()[:16]
        intent_sha = hashlib.sha256(open(os.path.join(src, "out", stem + "-intent.json"), "rb").read()).hexdigest()[:16]
        rows.append({"board": letter, "phase": phase, "board_sha256_16": board_sha, "intent_sha256_16": intent_sha,
                     "exit": r.returncode, "result": v.get("verdict") or v.get("result"), "counts": v.get("counts"), "denominator": v.get("denominator"),
                     "summary": summary, "fail_by_cause": {k: len(x) for k, x in fails.items()}, "fail_lines": fails,
                     "justified_lines": just, "recorded_lines": rec, "bypass_lines": len(lines)})
        print("%s %-20s %s %s | %s" % (letter, phase, v.get("verdict") or v.get("result"), json.dumps(v.get("counts"), sort_keys=True),
                                       "; ".join(summary)[:400]))
        for k, x in sorted(fails.items()): print("     FAIL %3d  %s" % (len(x), k))
    json.dump({"what": "DEC-001 (intent_decoupling) on each board's committed candidate under decision 42's tools; "
                       "NOT EVIDENCE: read outside the tree", "checkout": root, "rows": rows}, open(out, "w"), indent=1)
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
