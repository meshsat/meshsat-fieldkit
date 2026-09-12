#!/usr/bin/env python3
"""Run many pre-router arms at once and grade each against its own written prediction (MESHSAT-862, 11 Sep 2026).

The ladders of 32.97 and 32.98 ran serially, one knob at a time, at twenty minutes an arm, and the answer to
"which of these eight ideas pays" took a day. A box with 128 cores runs eight arms in the time one takes, and the
pre-router is one thread per pass, so width is the whole of the speedup available here.

The shape is the one the control-plane programme settles on and it is deliberately small:

  * AN ARM IS {name, env, predict}. The env is the knobs; the prediction is written BEFORE the run, in the spec
    file, and is graded mechanically afterwards. An arm without a prediction is refused, because a run nobody
    predicted cannot disappoint and so cannot teach anything. That is the fail-closed prediction gate, here.
  * EVERY ARM GETS ITS OWN PROJECT DIRECTORY, copied from one source, with the same placed board restored into
    it. One experiment per project directory is a rule this project already paid for: routeflow experiments
    sharing a directory overwrote each other's pre-route board and three hours of "B15" rows were B14 routes
    (6 September, appendix). The board's md5 goes in every row, so a row names the bytes it measured.
  * THE JUDGE IS NOT THE PROPOSER. Grading is `pairs >= predicted`, computed here from the tool's own summary
    line, never from anything the arm reports about itself.
  * ROWS ARE CHAINED into a ledger, so the table can be regenerated and cannot be quietly edited.

Usage: arms.py <spec.json> [--parallel N] [--dry]
"""
import os, re, sys, json, time, shutil, hashlib, argparse, subprocess, concurrent.futures as cf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict, ledger

TOOLS = os.path.dirname(os.path.abspath(__file__))
# An arm's name is interpolated into a directory path that this file then removes with rmtree, so it is
# a slug or it is refused (12 September 2026, when tier 2 of the control plane began writing specs: a
# name is no longer always typed by hand, and "it has only ever been typed by hand" is not a guard).
ARM_NAME = re.compile(r"^[a-z0-9][a-z0-9_]*$")
ARM_NAME_MAX = 32


def safe_name(n):
    return isinstance(n, str) and bool(ARM_NAME.match(n)) and len(n) <= ARM_NAME_MAX


PAIRS = re.compile(r"pair_preroute: (\d+) of (\d+) pairs laid")
# The echo the pre-router prints before it lays anything: the knobs the PROCESS received. Tier 2b asked
# for it on the first cycle it reviewed, because a pair count under an arm's knob proves nothing about
# the knob unless something shows the knob arrived. A row whose arm knob is missing from this echo is
# INFRA_FAIL here and can never be read as a measurement (12 September 2026).
KNOBS = re.compile(r"pair_preroute: knobs this process received: (\{.*?\}) \|")
SECS = re.compile(r"pair_preroute: seconds (\d+) total, (\d+) in the occupancy maps")


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""): h.update(c)
    return h.hexdigest()


def _kicad_build():
    """The KiCad build this arm ran against, or "" when pcbnew is not importable here."""
    try:
        import pcbnew
        return pcbnew.GetBuildVersion()
    except Exception:
        return ""


def run_arm(spec, arm, ecad, out_dir):
    """One arm: its own copy of the project, the same placed board, the passes in order. Returns a row."""
    name = arm["name"]
    src = os.path.join(ecad, spec["source_project"])
    dst = os.path.join(ecad, "arm-%s-%s" % (spec["letter"], name))
    t0 = time.time()
    # The host and its KiCad build travel with every row, so a cross-host comparison can be checked rather than
    # assumed. This went in after B19's placed board came out at md5 27dd5bd0 on a rented box against fc27d67c
    # on the VM, which I first wrote up as a cross-host determinism failure. It is not one: gen_sch_b.py,
    # escape.py, boardorder.py, join_adjacent_pins.py and prefanout.py all changed on 11 September between the
    # two runs, so the two boards were never the same tree. NOTHING here shows determinism failing across hosts;
    # what the day showed is that a recorded md5 without the commit that produced it cannot answer the question.
    row = {"arm": name, "board": spec["board"], "letter": spec["letter"], "env": arm.get("env", {}),
           "predict": arm["predict"], "tools_sha": spec.get("tools_sha", ""),
           "host": os.uname().nodename, "kicad": _kicad_build()}
    try:
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(src, dst)
        placed = os.path.join(dst, spec["placed"])
        board = os.path.join(dst, spec["board"] + ".kicad_pcb")
        if not os.path.exists(placed):
            row.update(error="no placed board at %s" % spec["placed"]); return row
        row["placed_md5"] = md5(placed)
        laid = total = 0; secs = maps = 0; logs = []; seen = {}
        for i, ps in enumerate(spec["passes"], 1):
            shutil.copyfile(placed, board) if i == 1 else None   # pass 1 starts from the placed board; later passes read what the earlier laid
            env = dict(os.environ); env.update({k: str(v) for k, v in ps.get("env", {}).items()})
            env.update({k: str(v) for k, v in arm.get("env", {}).items()})
            log = os.path.join(out_dir, "arm-%s-pass%d.log" % (name, i))
            with open(log, "w") as fh:
                subprocess.run([sys.executable, os.path.join(TOOLS, "pair_preroute.py"), board,
                                "--classes", ps["classes"]], cwd=dst, stdout=fh, stderr=subprocess.STDOUT,
                               env=env, timeout=spec.get("timeout_s", 14400))
            txt = open(log, errors="replace").read(); logs.append(os.path.basename(log))
            m = PAIRS.search(txt)
            if m: laid += int(m.group(1)); total += int(m.group(2))
            t = SECS.search(txt)
            if t: secs += int(t.group(1)); maps += int(t.group(2))
            k = KNOBS.search(txt)
            if k:
                try: seen.update(json.loads(k.group(1)))
                except ValueError: pass
        row.update(pairs=laid, of=total, seconds=secs, map_seconds=maps, logs=logs, knobs_seen=seen)
        err = knobs_arrived(arm.get("env") or {}, seen)
        if err: row["error"] = err
        # THE PAIR COUNT ALONE IS A GAMEABLE OBJECTIVE (12 September 2026). An arm that lowers a legality
        # bar buys pairs with copper the board cannot have, and nothing in the count would say so: the
        # first arm an automated tier 2 ever proposed for board B reached for exactly such a knob. So the
        # pre-route DRC runs on the board the arm laid and its hard count travels in the row. The record
        # already states the rule this implements: the class number is judged once, on the copper that was
        # laid (appendix 32.135), and here that judgement is part of the measurement rather than a later
        # surprise. A board whose DRC cannot be read is UNMEASURED, never assumed clean.
        if not row.get("error"):
            row.update(_drc_of(board, dst, out_dir, name))
    except subprocess.TimeoutExpired: row["error"] = "timed out"
    except Exception as e: row["error"] = "%s: %s" % (type(e).__name__, e)
    finally:
        row["wall_s"] = round(time.time() - t0, 1)
        shutil.rmtree(dst, ignore_errors=True)
    return row


def _drc_of(board, cwd, out_dir, name):
    """The hard set on the board this arm laid: {hard, unrouted} or {drc_error} and never a guess."""
    rep = os.path.join(out_dir, "arm-%s-drc.json" % name)
    cnt = os.path.join(out_dir, "arm-%s-counts.txt" % name)
    try:
        r = subprocess.run(["bash", os.path.join(TOOLS, "drc.sh"), board, rep],
                           capture_output=True, text=True, timeout=1800, cwd=cwd)
        if r.returncode or not os.path.exists(rep):
            return {"drc_error": (r.stderr or r.stdout).strip()[-300:] or "drc.sh exit %d" % r.returncode}
        subprocess.run([sys.executable, os.path.join(TOOLS, "hardset.py"), rep, "pre", "--counts", cnt,
                        "--label", "arm-%s" % name], capture_output=True, text=True, timeout=600, cwd=cwd)
        hard, unrouted = open(cnt).read().split()
        return {"hard": int(hard), "unrouted": int(unrouted)}
    except Exception as e:
        return {"drc_error": "%s: %s" % (type(e).__name__, e)}


def knobs_arrived(want, seen):
    """"" if every knob the arm asked for is in the tool's own echo, else why the row is not a measurement."""
    want = {str(k): str(v) for k, v in (want or {}).items()}
    if not want:
        return ""
    if not seen:
        return ("the pre-router printed no knob echo, so nothing shows this arm's knobs reached it; that is a "
                "tool version mismatch, not a measurement")
    bad = {k: {"asked": v, "the tool saw": seen.get(k)} for k, v in want.items() if str(seen.get(k)) != v}
    if bad:
        return ("the arm's knobs did not reach the tool: %s. A pair count under a knob that never arrived is "
                "not a measurement" % json.dumps(bad, sort_keys=True))
    return ""


def grade(row, hard_baseline=0):
    """The mechanical judge. `pairs` against the arm's own written prediction, and nothing the arm said.

    Since 12 September the count is not the whole objective: an arm that lays MORE hard DRC violations
    than the baseline has bought its pairs with copper the board cannot have, and it is graded ILLEGAL
    whatever its number. A board whose DRC could not be read is UNMEASURED rather than assumed clean.
    """
    p = row.get("predict") or {}
    if row.get("error"): return "INFRA_FAIL", row["error"]
    if row.get("drc_error"): return "UNMEASURED", "the DRC on the arm's own board could not be read: %s" % row["drc_error"]
    if row.get("hard") is not None and row["hard"] > hard_baseline:
        return "ILLEGAL", ("%d hard DRC violation(s) against a baseline of %d: this arm's pairs are copper the "
                           "board cannot have, so the count is not a result" % (row["hard"], hard_baseline))
    got = row.get("pairs")
    if got is None: return "UNMEASURABLE", "the pass printed no 'pairs laid' line"
    op, val = p.get("op", ">="), p.get("value")
    if val is None: return "UNMEASURABLE", "no predicted value"
    ok = {">=": got >= val, ">": got > val, "==": got == val, "<=": got <= val, "<": got < val}.get(op)
    if ok is None: return "UNMEASURABLE", "unknown operator %r" % op
    return ("MET" if ok else "MISSED"), "%d %s %s (%s)" % (got, op, val, p.get("basis", "no basis given"))


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--parallel", type=int, default=8)
    ap.add_argument("--out-dir", default="out/arms"); ap.add_argument("--dry", action="store_true")
    a = ap.parse_args(argv)
    spec = json.load(open(a.spec))
    ecad = os.path.abspath(spec.get("ecad") or os.path.dirname(TOOLS))
    os.makedirs(a.out_dir, exist_ok=True)

    unsafe = [x.get("name") for x in spec["arms"] if not safe_name(x.get("name"))]
    if unsafe:
        print("arms: refused, these names are not slugs and become directories this file removes: %s" % unsafe)
        return verdict.write("arms", verdict.FAIL, counts={"unsafe_names": len(unsafe)}, denominator=len(spec["arms"]),
                             evidence=[str(u) for u in unsafe],
                             note="an arm name is a lowercase slug of at most %d characters" % ARM_NAME_MAX,
                             out_dir=a.out_dir)

    missing = [x.get("name", "?") for x in spec["arms"] if not x.get("predict", {}).get("value")]
    if missing:
        print("arms: refused, these carry no prediction: %s" % missing)
        print("arms: an arm nobody predicted cannot disappoint, so it cannot teach anything")
        return verdict.write("arms", verdict.FAIL, counts={"unpredicted": len(missing)}, denominator=len(spec["arms"]),
                             evidence=missing, note="every arm carries {metric, op, value, basis} before it runs",
                             out_dir=a.out_dir)
    if a.dry:
        for x in spec["arms"]: print("  %-14s env %-44s predict %s %s" % (x["name"], json.dumps(x.get("env", {})), x["predict"].get("op"), x["predict"].get("value")))
        return 0

    print("arms: %d arm(s), %d at a time, source %s" % (len(spec["arms"]), a.parallel, spec["source_project"]))
    rows = []
    with cf.ThreadPoolExecutor(max_workers=a.parallel) as ex:
        futs = {ex.submit(run_arm, spec, x, ecad, a.out_dir): x for x in spec["arms"]}
        for f in cf.as_completed(futs):
            row = f.result(); v, note = grade(row, spec.get("hard_baseline", 0))
            row["verdict"] = v; row["note"] = note
            rows.append(row)
            print("arms: %-14s %-12s %s  (%.0f s, maps %s s)" % (row["arm"], v, note, row.get("wall_s", 0), row.get("map_seconds", "?")))
            ledger.append(os.path.join(a.out_dir, "arms.jsonl"), row)
    rows.sort(key=lambda r: (r["verdict"] in ("ILLEGAL", "INFRA_FAIL", "UNMEASURED"), -(r.get("pairs") or -1), r["arm"]))
    print("\narms: ranked by pairs laid")
    for r in rows:
        print("  %-14s %-4s of %-4s  %-10s hard %-4s  maps %-5s s  wall %-6s s  %s"
              % (r["arm"], r.get("pairs", "-"), r.get("of", "-"), r["verdict"], r.get("hard", "?"),
                 r.get("map_seconds", "-"), r.get("wall_s", "-"), json.dumps(r.get("env", {}))[:60]))
    met = sum(1 for r in rows if r["verdict"] == "MET")
    bad = sum(1 for r in rows if r["verdict"] in ("INFRA_FAIL", "UNMEASURED"))
    illegal = sum(1 for r in rows if r["verdict"] == "ILLEGAL")
    best = rows[0] if rows else {}
    return verdict.write("arms", verdict.INCONCLUSIVE if bad == len(rows) else verdict.PASS,
                         counts={"arms": len(rows), "met": met, "missed": len(rows) - met - bad - illegal,
                                 "infra_fail": bad, "illegal": illegal, "best_pairs": best.get("pairs")},
                         denominator=len(rows), evidence=["%s %s %s" % (r["arm"], r["verdict"], r["note"]) for r in rows],
                         note="best %s with %s of %s; the judge is the pair count, never the arm" % (best.get("arm"), best.get("pairs"), best.get("of")),
                         out_dir=a.out_dir)


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
