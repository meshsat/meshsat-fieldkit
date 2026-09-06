#!/usr/bin/env python3
"""routeflow: the supervisor around the board chains and Freerouting (v2/docs/routeflow-methodology.md, 5 Sep 2026).

It runs the EXISTING stage scripts of a board with fixed argument vectors (pre-route chain, route_parallel.sh, finish_*.sh), judges each
stage by its own artefacts (a `saved` line, a session file, a parseable DRC JSON, the clean flag), records every transition in an append-only
journal with a fixed status vocabulary, applies a small deterministic remedy table to the failure signatures of 5 Sep 2026 within a round
budget, and stops with a named state when the table ends. No model is in the loop; a stop is the session's cue to fix a generator.

Usage:
  routeflow.py preflight [--repo DIR]                 host checks (imports, binaries, jar, memory, load, services, git, lock)
  routeflow.py run <profile.json> [--rounds N] [--no-services] [--dry-run]
  routeflow.py status <project dir> [--markdown]      the journal
  routeflow.py selftest                               kill the predicates with empty inputs; every one must block
  routeflow.py experiment <exp.json> [--budget-hours H] [--no-services] [--parallel N]   one route per configuration (rules file knobs, jar) on one pre-route board, measured into bench/results.jsonl; N configurations at once

Profile (JSON): see tools/routeflow/*.json. Placeholders in argv: <PROJECT> (the project dir), <ECAD> (its parent), <NAME> (the board stem).
"""
import sys, os, re, json, time, glob, hashlib, subprocess, shutil, collections, tempfile, datetime

HARD = ("clearance", "shorting_items", "tracks_crossing", "hole_clearance", "hole_to_hole", "copper_edge_clearance")
LOCK = os.path.expanduser(os.environ.get("ROUTEFLOW_LOCK") or "~/.routeflow.lock")   # ROUTEFLOW_LOCK: another lock name, so several experiments run side by side on a big host (6 Sep 2026)

def now(): return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def sh(argv, cwd, log, env=None):
    """Run a fixed argv vector, capture everything to `log`, return the exit code. Never a shell string."""
    e = dict(os.environ); e.update(env or {})
    with open(log, "ab") as f:
        f.write(("\n=== %s  %s  (cwd %s)\n" % (now(), " ".join(argv), cwd)).encode())
        f.flush(); p = subprocess.run(argv, cwd=cwd, stdout=f, stderr=subprocess.STDOUT, env=e)
    return p.returncode

# ---------------------------------------------------------------- predicates (each reads an artefact; absence blocks)
def read(fn):
    try: return open(fn, errors="replace").read()
    except OSError: return None

def judge_pre(log_text, must_contain, min_all_pass, gen_logs):
    """The pre-route chain: its markers present, enough ALL PASS lines, no FAIL/BLOCK/Traceback, every generator saved."""
    if log_text is None: return "GATE_BLOCKED", "pre-route log missing"
    fails = [ln for ln in log_text.splitlines() if re.match(r"^FAIL\b|^\s*RESULT: \d+ FAIL|Traceback|PREROUTE-DONE BLOCK|BLOCK:", ln)]
    if fails: return "GATE_BLOCKED", "%d blocking lines: %s" % (len(fails), " | ".join(f[:100] for f in fails[:4]))
    missing = [m for m in must_contain if m not in log_text]
    if missing: return "GATE_BLOCKED", "markers missing: %s" % missing
    n = log_text.count("RESULT: ALL PASS")
    if n < min_all_pass: return "GATE_BLOCKED", "RESULT: ALL PASS %d of %d gates" % (n, min_all_pass)
    for g in gen_logs:
        t = read(g["file"])
        if t is None or g.get("must", "saved") not in t: return "GATE_BLOCKED", "generator %s has no '%s' line" % (g["file"], g.get("must", "saved"))
    return "GATED", "ALL PASS %d of %d gates, %d generator logs saved" % (n, min_all_pass, len(gen_logs))

def parse_scores(par_dir):
    """attempt -> (hard, unrouted, vias) from route_one's score files; a missing file scores out."""
    out = {}
    for d in sorted(glob.glob(os.path.join(par_dir, "*/"))):
        k = os.path.basename(d.rstrip("/")); t = read(os.path.join(d, "score.txt"))
        try: h, u, v = [int(x) for x in t.split()[:3]]
        except Exception: h, u, v = 9999, 9999, 999999
        out[k] = (h, u, v)
    return out

def autoroute_minutes(fr_log):
    t = read(fr_log) or ""
    m = re.search(r"Auto-routing was completed in (\d+) minute\(s\) ([\d.]+) seconds", t)
    return round(int(m.group(1)) + float(m.group(2)) / 60, 1) if m else None

def load_drc(fn):
    """A DRC JSON must parse and carry a violations list; anything else is a tool failure, never a pass."""
    t = read(fn)
    if t is None: raise RuntimeError("DRC report missing: %s" % fn)
    d = json.loads(t)
    if "violations" not in d or not isinstance(d["violations"], list): raise RuntimeError("DRC report has no violations list: %s" % fn)
    return d

def signature(drc):
    """Classify a routed board's hard violations: KNOT (one layer, two nets, fragments), EDGE (edge clearance dominates), HARD, OPEN, CLEAN."""
    hard = [v for v in drc["violations"] if v["type"] in HARD]; unr = len(drc.get("unconnected_items", []))
    counts = collections.Counter(v["type"] for v in hard)
    if not hard and unr == 0: return "CLEAN", counts, unr
    if not hard: return "OPEN", counts, unr
    if counts.get("copper_edge_clearance", 0) * 2 >= len(hard): return "EDGE", counts, unr
    layers, nets, lengths = set(), set(), []
    for v in hard:
        for it in v.get("items", []):
            d = it.get("description", "")
            layers.update(re.findall(r"on (\w+\.Cu)", d)); nets.update(re.findall(r"\[([^\]]+)\]", d))
            m = re.search(r"length ([\d.]+) mm", d)
            if m: lengths.append(float(m.group(1)))
    if len(layers) == 1 and len(nets) == 2 and lengths and max(lengths) < 0.5: return "KNOT", counts, unr
    return "HARD", counts, unr

def judge_finish(finish_log, clean_flag, stub_log, deliverable):
    t = read(finish_log) or ""
    if "Traceback" in t or "CRASHED" in t or (stub_log and "Traceback" in (read(stub_log) or "")): return "TOOL_CRASH", "a finish stage crashed (see %s)" % finish_log
    flag = read(clean_flag)
    if flag is None: return "FINISH_REFUSED", "no clean flag written (%s)" % clean_flag
    if flag.strip() != "clean": return "FINISH_REFUSED", "flag says %r" % flag.strip()
    if deliverable and not glob.glob(os.path.join(deliverable, "*-gerbers.zip")): return "FINISH_REFUSED", "deliverable has no gerber zip: %s" % deliverable
    m = re.search(r"routed-board gate: hard (\d+) unrouted (\d+)", t)
    return "CLEAN", ("routed-board gate: hard %s unrouted %s" % (m.group(1), m.group(2))) if m else "clean flag set"

# ---------------------------------------------------------------- remedies (profile changes, bounded)
def remedy(sig, prof, applied):
    r = dict(prof["route"])
    if sig == "NO_SESSION":
        if prof.get("plane_layers") and not r.get("power_layers") and "power_layers" not in applied: r["power_layers"] = list(prof["plane_layers"]); r["timeout"] = int(r.get("timeout", 4500)) * 2; return r, "plane layers to power layers, timeout x 2"
        if "timeout" not in applied: r["timeout"] = int(r.get("timeout", 4500)) * 2; return r, "timeout x 2"
        return None, "no session twice: needs the session (diagnostic route, route_audit.py)"
    if sig == "KNOT":
        if int(r.get("threads", 6)) != 1: r["threads"] = 1; return r, "single-thread optimiser (multi-thread knot)"
        return None, "knot with one thread: needs the session"
    if sig == "OPEN":
        if "via_costs" not in applied and not r.get("via_costs"): r["via_costs"] = 100; return r, "via_costs 100 through a rules file (a different solution; the router is deterministic, so more passes alone repeat the result)"
        if "passes" not in applied: r["attempts"] = [int(p * 1.3) for p in r["attempts"]]; return r, "passes +30 percent"
        return None, "opens survive a different via cost and more passes: needs the generators (escapes, joins) or the stub router"
    if sig == "EDGE": return None, "edge clearance dominates: an edge keep-out band belongs in the outline generator"
    return None, "hard violations of mixed kind: needs the session (route_audit.py)"

# ---------------------------------------------------------------- the run
def journal(project, rec):
    os.makedirs(os.path.join(project, "out", "routeflow"), exist_ok=True)
    rec = dict(ts=now(), **rec)
    with open(os.path.join(project, "out", "routeflow", "journal.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
    print("[routeflow %s] %s %s  %s" % (rec["ts"][11:], rec.get("stage", ""), rec.get("status", ""), rec.get("note", "")), flush=True)

def run_id(repo, prof, project):
    h = hashlib.sha256(json.dumps(prof, sort_keys=True).encode())
    try: h.update(subprocess.run(["git", "rev-parse", "HEAD:v2/ecad/tools"], cwd=repo, capture_output=True, text=True).stdout.encode())
    except Exception: pass
    pre = os.path.join(project, "out", "%s-preroute.kicad_pcb" % prof["board"])
    if os.path.exists(pre): h.update(open(pre, "rb").read())
    return h.hexdigest()[:12]

def take_lock(board):
    if os.path.exists(LOCK):
        try:
            o = json.load(open(LOCK))
            if os.path.exists("/proc/%d" % o.get("pid", -1)): return False, "router held by %s (pid %d since %s)" % (o.get("board"), o.get("pid"), o.get("since"))
        except Exception: pass
    json.dump({"board": board, "pid": os.getpid(), "since": now()}, open(LOCK, "w")); return True, "lock taken"

def services(script, action, log):
    if script and os.path.exists(os.path.expanduser(script)): sh([os.path.expanduser(script), action], os.path.expanduser("~"), log)

def expand(argv, project, ecad, name): return [a.replace("<PROJECT>", project).replace("<ECAD>", ecad).replace("<NAME>", name) for a in argv]

def run(profile_fn, rounds, use_services, dry):
    prof = json.load(open(profile_fn)); repo = prof.get("repo") or os.getcwd()
    project = os.path.abspath(os.path.join(repo, prof["project"])); ecad = os.path.dirname(project); name = prof["board"]
    os.makedirs(os.path.join(project, "out", "routeflow"), exist_ok=True)
    rid = run_id(repo, prof, project); rdir = os.path.join(project, "out", "routeflow", rid); os.makedirs(rdir, exist_ok=True)
    ok, msg = take_lock(name)
    journal(project, dict(run=rid, board=name, phase=prof["phase"], stage="lock", status="LOCKED" if ok else "PREFLIGHT_FAIL", note=msg))
    if not ok: return 2
    applied = set(); status = None
    try:
        for rnd in range(1, rounds + 2):
            route = prof["route"]
            journal(project, dict(run=rid, round=rnd, board=name, stage="pre", status="GENERATING", note="expect %s" % json.dumps(prof.get("expect", {}))))
            pre = prof["pre"]; plog = os.path.join(rdir, "round%d-pre.log" % rnd)
            rc = 0
            if not dry:
                for argv in (pre.get("steps") or [pre["argv"]]):   # fixed argument vectors, one process each, no shell string
                    rc = sh(expand(argv, project, ecad, name), project if pre.get("cwd", "<PROJECT>") == "<PROJECT>" else ecad, plog)
                    if rc != 0: break
            gen_logs = [dict(g, file=os.path.join(project, g["file"])) for g in pre.get("gen_logs", [])]
            st, note = judge_pre(read(plog), pre.get("must_contain", []), pre.get("min_all_pass", 1), gen_logs) if not dry else ("GATED", "dry run")
            if rc != 0 and st == "GATED": st, note = "TOOL_CRASH", "pre-route chain exit %d" % rc
            journal(project, dict(run=rid, round=rnd, board=name, stage="pre", status=st, note=note))
            if st != "GATED": status = st; break
            env = {"FR_THREADS": str(route.get("threads", 2)), "FR_TIMEOUT": str(route.get("timeout", 4500))}
            if route.get("power_layers"): env["FR_POWER_LAYERS"] = " ".join(route["power_layers"])
            if route.get("plane_nets"): env["FR_PLANE_NETS"] = ",".join(route["plane_nets"])   # zones of these nets on the power layers stay in the DSN as planes (6 Sep 2026: GND by vias into In1, not as wires)
            if route.get("jar"): env["FR_JAR"] = os.path.expanduser(route["jar"])   # the router build (Stage 4: freerouting-2.4.1.jar beside 1.9.0)
            if any(k in route for k in ("via_costs", "plane_via_costs", "ripup", "preferred", "inactive")) and not dry:   # the rules-file knobs the probe found the router honours
                tools = os.path.dirname(os.path.abspath(__file__)); pre = os.path.join(project, "out", name + "-preroute.kicad_pcb"); dsn0 = os.path.join(rdir, "round%d-rules.dsn" % rnd); rules = os.path.join(rdir, "round%d.rules" % rnd)
                sh(["python3", "-c", "import pcbnew,sys; b=pcbnew.LoadBoard(sys.argv[1]); [b.Remove(z) for z in list(b.Zones()) if not z.GetIsRuleArea()]; pcbnew.SaveBoard(sys.argv[1]+'.np.kicad_pcb', b); print(pcbnew.ExportSpecctraDSN(pcbnew.LoadBoard(sys.argv[1]+'.np.kicad_pcb'), sys.argv[2]))", pre, dsn0], project, os.path.join(rdir, "round%d-rules.log" % rnd))
                argv = ["python3", os.path.join(tools, "fr_rules.py"), dsn0, rules, "--via-costs", str(route.get("via_costs", 50)), "--plane-via-costs", str(route.get("plane_via_costs", 5)), "--ripup", str(route.get("ripup", 100))]
                if route.get("preferred"): argv += ["--preferred", route["preferred"]]
                if route.get("inactive"): argv += ["--inactive", route["inactive"]]
                if sh(argv, project, os.path.join(rdir, "round%d-rules.log" % rnd)) == 0 and os.path.exists(rules): env["FR_RULES"] = rules; env["FR_RULES_INJECT"] = "1"   # into the DSN, never -dr (6 Sep 2026 11:30)
            journal(project, dict(run=rid, round=rnd, board=name, stage="route", status="ROUTING", note="attempts %s threads %s timeout %s power %s planes %s rules %s jar %s" % (route["attempts"], env["FR_THREADS"], env["FR_TIMEOUT"], route.get("power_layers"), route.get("plane_nets") or "none", {k: route[k] for k in ("via_costs", "plane_via_costs", "ripup", "preferred", "inactive") if k in route} or "none", os.path.basename(route.get("jar", "freerouting-1.9.0.jar")))))
            if use_services: services(prof.get("services_script"), "stop", os.path.join(rdir, "services.log"))
            rlog = os.path.join(project, prof["route"].get("log", "out/parallel-routeflow.log"))
            if not dry:
                shutil.rmtree(os.path.join(project, "out", "par"), ignore_errors=True)
                rc = sh(["./tools/route_parallel.sh", name, name, " ".join(str(p) for p in route["attempts"])], ecad, rlog, env)
            scores = parse_scores(os.path.join(project, "out", "par")) if not dry else {}
            best = min(scores.items(), key=lambda kv: kv[1]) if scores else (None, (9999, 9999, 999999))
            mins = {k: autoroute_minutes(os.path.join(project, "out", "par", k, "fr.log")) for k in scores}
            if best[1][0] >= 9999:
                sig = "NO_SESSION"; note = "no session in %d attempts; autoroute minutes %s" % (len(scores), mins)
            else:
                try: drc = load_drc(os.path.join(project, "out", "par", best[0], "drc.json")); sig, counts, unr = signature(drc)
                except RuntimeError as e: sig, counts, unr = "TOOL_CRASH", {}, None; note = str(e)
                if sig != "TOOL_CRASH":
                    nets = len(re.findall(r"^\s*\(net ", read(os.path.join(project, "out", "par", best[0], "%s.dsn" % name)) or "", re.M))
                    note = "winner attempt %s: hard %d of %d types %s, unrouted %d of %d nets, vias %d, autoroute minutes %s" % (best[0], best[1][0], len(HARD), dict(counts), unr, nets, best[1][2], mins)
            st = {"NO_SESSION": "NO_SESSION", "KNOT": "ROUTED_HARD", "HARD": "ROUTED_HARD", "EDGE": "ROUTED_HARD", "OPEN": "ROUTED_OPEN", "CLEAN": "ROUTED_CLEAN", "TOOL_CRASH": "TOOL_CRASH"}[sig]
            journal(project, dict(run=rid, round=rnd, board=name, stage="route", status=st, signature=sig, note=note))
            if sig in ("CLEAN", "OPEN", "HARD", "KNOT", "EDGE"):
                # the finish gets its chance on every routed board: cleanup, stub router, pairs, the routed-board gate
                fin = prof["finish"]; flog = os.path.join(rdir, "round%d-finish.log" % rnd)
                journal(project, dict(run=rid, round=rnd, board=name, stage="finish", status="FINISHING", note=" ".join(fin["argv"])))
                if not dry: sh(expand(fin["argv"], project, ecad, name), project if fin.get("cwd", "<PROJECT>") == "<PROJECT>" else ecad, flog)
                fst, fnote = judge_finish(flog, os.path.join(project, fin["clean_flag"]), os.path.join(project, fin.get("stub_log", "out/%s-stub.log" % name)), os.path.join(repo, prof.get("deliverable", "")) if prof.get("deliverable") else None)
                journal(project, dict(run=rid, round=rnd, board=name, stage="finish", status=fst, note=fnote))
                if fst == "CLEAN":
                    exp = prof.get("expect", {}); met = all(m is None or m <= exp.get("autoroute_minutes_max", 1e9) for m in mins.values())
                    journal(project, dict(run=rid, round=rnd, board=name, stage="expect", status="MET" if met else "MISSED", note="autoroute minutes %s against max %s" % (mins, exp.get("autoroute_minutes_max"))))
                    quality(project, repo, prof, rid, rnd, name, mins)
                    status = "CLEAN"; break
                if fst == "TOOL_CRASH": status = fst; break
                if sig == "CLEAN": sig = "OPEN"   # the router was clean but the finish refused: treat as opens for the table
            if rnd > rounds: status = "STOPPED_BUDGET"; journal(project, dict(run=rid, round=rnd, board=name, stage="remedy", status=status, note="%d automatic rounds spent on %s" % (rounds, sig))); break
            new_route, why = remedy(sig, prof, applied)
            if new_route is None: status = "STOPPED_NEEDS_GENERATOR"; journal(project, dict(run=rid, round=rnd, board=name, stage="remedy", status=status, note=why)); break
            for k in ("power_layers", "timeout", "threads", "attempts", "via_costs"):
                if new_route.get(k) != route.get(k): applied.add("passes" if k == "attempts" else k)
            prof["route"] = new_route; journal(project, dict(run=rid, round=rnd, board=name, stage="remedy", status="REMEDY", note="%s -> %s" % (sig, why)))
    finally:
        if use_services: services(prof.get("services_script"), "start", os.path.join(rdir, "services.log"))
        try: os.remove(LOCK)
        except OSError: pass
    journal(project, dict(run=rid, board=name, stage="end", status=status or "UNKNOWN", note="see out/routeflow/%s/" % rid))
    return 0 if status == "CLEAN" else 1

# ---------------------------------------------------------------- quality (Stage 1 of the programme): metrics of the finished board against the baseline
def quality(project, repo, prof, rid, rnd, name, mins):
    tools = os.path.dirname(os.path.abspath(__file__)); board = os.path.join(project, name + ".kicad_pcb"); drc = os.path.join(project, "out", name + "-drc.json")
    mfile = os.path.join(project, "out", "routeflow", rid, "round%d-metrics.json" % rnd); base = os.path.join(tools, "routeflow", "bench", "baseline.json")
    argv = ["python3", os.path.join(tools, "route_metrics.py"), board, drc if os.path.exists(drc) else "-", "--json", mfile, "--tag", prof["phase"]]
    for k, m in mins.items():
        if m: argv += ["--autoroute", str(m)]; break
    rc = sh(argv, project, os.path.join(project, "out", "routeflow", rid, "round%d-quality.log" % rnd))
    if rc != 0 or not os.path.exists(mfile): journal(project, dict(run=rid, round=rnd, board=name, stage="quality", status="UNMEASURABLE", note="route_metrics exit %d" % rc)); return
    if not os.path.exists(base): journal(project, dict(run=rid, round=rnd, board=name, stage="quality", status="MEASURED", note="no baseline yet: " + (read(mfile) or "")[:200])); return
    out = os.path.join(project, "out", "routeflow", rid, "round%d-compare.json" % rnd)
    key = prof.get("baseline_key", prof["phase"])
    rc = sh(["python3", os.path.join(tools, "bench_compare.py"), base, mfile, "--board", key, "--json", out], project, os.path.join(project, "out", "routeflow", rid, "round%d-quality.log" % rnd))
    try: c = json.load(open(out)); st = {"MET": "QUALITY_MET", "REGRESSION": "QUALITY_REGRESSED", "INELIGIBLE": "QUALITY_INELIGIBLE"}.get(c["verdict"], "UNMEASURABLE"); note = c["note"]
    except Exception as e: st, note = "UNMEASURABLE", "compare failed: %s" % e
    journal(project, dict(run=rid, round=rnd, board=name, stage="quality", status=st, note=note))

# ---------------------------------------------------------------- experiment (Stage 2): one route per configuration on one pre-route board, measured, journaled, resumable
def experiment(exp_fn, budget_hours, use_services, parallel=1):
    """One route per configuration on one pre-route board, measured into bench/results.jsonl. `parallel` above 1 runs that many
    configurations at once, one worker thread each (the vast.ai box of 6 Sep 2026: 384 threads, 773 GB); every configuration owns its
    out/par/exp-<name> directory, so the only shared things are the DSN they all read and the results file, appended under a file lock.
    ROUTEFLOW_TIMEOUT_SCALE (float) stretches every route timeout for a slower core without changing a configuration's key; ROUTEFLOW_LOCK
    names the lock file, so several experiments run side by side on one host."""
    import threading, fcntl, concurrent.futures
    FINISH_VERSION = 2   # 2 (6 Sep 2026 02:00): the finish runs the stub router as production does and records the raw counts; rows of an older finish are re-finished from their session, never re-routed
    RULES_MODE = "inject"   # part of every configuration key since 6 Sep 2026 11:30: the settings go into the DSN; the -dr rows of the night before (which lost the design's clearances) have other keys and are never reused
    exp = json.load(open(exp_fn)); repo = exp.get("repo") or os.getcwd(); tools = os.path.dirname(os.path.abspath(__file__))
    project = os.path.abspath(os.path.join(repo, exp["project"])); ecad = os.path.dirname(project); name = exp["board"]; key = exp["board_key"]
    os.makedirs(os.path.join(project, "out"), exist_ok=True); results = os.path.join(tools, "routeflow", "bench", "results.jsonl"); os.makedirs(os.path.dirname(results), exist_ok=True)
    scale = float(os.environ.get("ROUTEFLOW_TIMEOUT_SCALE") or 1); jlock = threading.Lock()
    def jn(rec):
        with jlock: journal(project, rec)
    t_start = time.time(); ok, msg = take_lock(name + ":experiment")
    jn(dict(run="exp", board=name, phase=key, stage="lock", status="LOCKED" if ok else "PREFLIGHT_FAIL", note=msg))
    if not ok: return 2
    # the project lock (6 Sep 2026 03:50): two experiments on one project directory share out/<name>-preroute.kicad_pcb and out/par/exp-<config>; the
    # B14 strip overwrote the B15 pre-route board while both ran and every B row of that night had to be discarded. A busy project directory refuses.
    plock = os.path.join(project, "out", "routeflow", "experiment.lock"); os.makedirs(os.path.dirname(plock), exist_ok=True)
    try:
        o = json.load(open(plock))
        if os.path.exists("/proc/%d" % o.get("pid", -1)) and o.get("pid") != os.getpid():
            jn(dict(run="exp", board=name, phase=key, stage="lock", status="PREFLIGHT_FAIL", note="project directory busy: experiment %s (pid %d since %s); give this experiment its own project directory" % (o.get("exp"), o.get("pid"), o.get("since"))))
            try: os.remove(LOCK)
            except OSError: pass
            return 2
    except (OSError, ValueError): pass
    json.dump({"exp": os.path.basename(exp_fn), "pid": os.getpid(), "since": now()}, open(plock, "w"))
    try:
        # the pre-route board: "strip:<released board>" strips the router copper (locked copper stays); a path is used as is; nothing means out/<name>-preroute.kicad_pcb
        pre = os.path.join(project, "out", name + "-preroute.kicad_pcb"); src = exp.get("preroute")
        elog = os.path.join(project, "out", "experiment.log")
        if src and src.startswith("strip:"): sh(["python3", os.path.join(tools, "strip_route.py"), os.path.join(repo, src[6:]), pre], project, elog); shutil.copy(os.path.join(os.path.dirname(os.path.join(repo, src[6:])), name + ".kicad_pro"), os.path.join(project, name + ".kicad_pro"))
        elif src and os.path.abspath(os.path.join(repo, src)) != os.path.abspath(pre): shutil.copy(os.path.join(repo, src), pre)
        if not os.path.exists(pre): jn(dict(run="exp", board=name, stage="pre", status="GATE_BLOCKED", note="no pre-route board at " + pre)); return 1
        pre_hash = hashlib.sha256(open(pre, "rb").read()).hexdigest()[:12]
        done = set(); stale = {}
        if os.path.exists(results):
            for l in open(results):
                try: r = json.loads(l)
                except Exception: continue
                if r.get("verdict") == "NO_SESSION" and (r.get("wall_s") or 0) < 60: continue   # a router that died within a minute is a tool failure (no display, no Java), not a measurement: run it again
                if r.get("verdict") != "NO_SESSION" and r.get("finish_version", 1) < FINISH_VERSION: stale[r.get("key")] = r; continue   # routed under an older finish: re-finish from its session
                done.add(r.get("key"))
        def ident(cfg):
            """(jar path, jar sha, configuration key): the key is the pre-route board, the jar, the configuration and the route block; never the host, the timeout scale or the time"""
            jar_path = os.path.expanduser(cfg.get("jar", exp.get("jar", "~/bin/freerouting-1.9.0.jar")))
            if not jar_path.startswith("/"): jar_path = os.path.expanduser("~/bin/" + jar_path)
            jar_sha = hashlib.sha256(open(jar_path, "rb").read()).hexdigest()[:16] if os.path.exists(jar_path) else "nojar"
            return jar_path, jar_sha, hashlib.sha256((pre_hash + jar_sha + json.dumps(cfg, sort_keys=True) + json.dumps(exp.get("route", {}), sort_keys=True) + RULES_MODE).encode()).hexdigest()[:16]
        pending = []; refin = []
        for cfg in exp["configs"]:
            jar_path, jar_sha, ckey = ident(cfg)
            if jar_sha == "nojar": jn(dict(run="exp", board=name, stage="experiment", status="GATE_BLOCKED", note="%s: no jar at %s" % (cfg["name"], jar_path))); continue
            if ckey in done: jn(dict(run="exp", board=name, stage="experiment", status="MEASURED", note="%s already in results (skip)" % cfg["name"])); continue
            if ckey in stale and os.path.exists(os.path.join(project, "out", "par", "exp-" + cfg["name"], name + ".ses")): refin.append((cfg, stale[ckey])); continue
            pending.append(cfg)
        jn(dict(run="exp", board=name, phase=key, stage="experiment", status="EXPERIMENT", note="preroute %s, %d of %d configs to route, %d to re-finish from their sessions, %d at once, timeout scale %.1f, budget %.1f h, expect: %s" % (pre_hash, len(pending), len(exp["configs"]), len(refin), max(1, parallel), scale, budget_hours, exp.get("expect", "")[:160])))
        if use_services: services(exp.get("services_script"), "stop", elog)
        # one DSN for the rules file's layer list
        dsn0 = os.path.join(project, "out", name + "-experiment.dsn")
        sh(["python3", "-c", "import pcbnew,sys; b=pcbnew.LoadBoard(sys.argv[1]); [b.Remove(z) for z in list(b.Zones()) if not z.GetIsRuleArea()]; pcbnew.SaveBoard(sys.argv[1]+'.np.kicad_pcb', b); print(pcbnew.ExportSpecctraDSN(pcbnew.LoadBoard(sys.argv[1]+'.np.kicad_pcb'), sys.argv[2]))", pre, dsn0], project, elog)
        if not os.path.exists(dsn0) or os.path.getsize(dsn0) == 0: jn(dict(run="exp", board=name, stage="experiment", status="GATE_BLOCKED", note="no DSN from the pre-route board (see out/experiment.log)")); return 1
        def one(cfg, slot):
            if time.time() - t_start > budget_hours * 3600: jn(dict(run="exp", board=name, stage="experiment", status="STOPPED_BUDGET", note="budget spent before %s" % cfg["name"])); return None
            if slot: time.sleep(min(slot * 3, 240))   # stagger the starts: xvfb-run -a races on display numbers when many start in the same second
            jar_path, jar_sha, ckey = ident(cfg)
            k = "exp-" + cfg["name"]; w = os.path.join(project, "out", "par", k); shutil.rmtree(w, ignore_errors=True); os.makedirs(w); plog = os.path.join(w, "prep.log")
            rules = os.path.join(w, "config.rules"); argv = ["python3", os.path.join(tools, "fr_rules.py"), dsn0, rules, "--via-costs", str(cfg.get("via_costs", 50)), "--plane-via-costs", str(cfg.get("plane_via_costs", 5)), "--ripup", str(cfg.get("ripup", 100))]
            if cfg.get("preferred"): argv += ["--preferred", cfg["preferred"]]
            if cfg.get("inactive"): argv += ["--inactive", cfg["inactive"]]
            if cfg.get("only"): argv += ["--only", cfg["only"]]
            sh(argv, project, plog)
            route = dict(exp.get("route", {})); route.update({kk: cfg[kk] for kk in ("passes", "threads", "timeout", "power_layers") if kk in cfg})
            if cfg.get("planes"): route["plane_nets"] = list(cfg["planes"])
            timeout = int(route.get("timeout", 1800) * scale)
            env = {"FR_THREADS": str(route.get("threads", 1)), "FR_TIMEOUT": str(timeout), "FR_RULES": rules, "FR_RULES_INJECT": "1", "FR_JAR": jar_path, "FR_FANOUT": "true" if cfg.get("fanout") else "false"}
            if route.get("power_layers"): env["FR_POWER_LAYERS"] = " ".join(route["power_layers"])
            if route.get("plane_nets"): env["FR_PLANE_NETS"] = ",".join(route["plane_nets"])
            ses = os.path.join(w, name + ".ses"); t0 = time.time(); starts = 0; flog = os.path.join(w, "finish.log"); board = os.path.join(w, name + ".kicad_pcb")
            for attempt in (1, 2):
                starts += 1; sh(["../tools/route_one.sh", ".", name, k, str(route.get("passes", 60))], project, os.path.join(w, "route_one.log"), env)
                fr = read(os.path.join(w, "fr.log")) or ""
                if not os.path.exists(ses) and ("Xvfb failed to start" in fr or "Can't open display" in fr or "No protocol specified" in fr or "HeadlessException" in fr):
                    jn(dict(run="exp", board=name, stage="experiment", status="TOOL_CRASH", note="%s: no display for the router (attempt %d), retrying once" % (cfg["name"], attempt))); time.sleep(5); continue
                break
            wall = int(time.time() - t0)
            row = {"key": ckey, "board_key": key, "board": name, "config": cfg["name"], "cfg": cfg, "route": route, "rules_mode": RULES_MODE, "timeout_s": timeout, "starts": starts, "host": os.uname().nodename, "preroute_hash": pre_hash, "jar": os.path.basename(jar_path), "jar_sha": jar_sha, "wall_s": wall, "ts": now(), "finish_version": FINISH_VERSION}
            if not os.path.exists(ses) or os.path.getsize(ses) == 0:
                row.update(verdict="NO_SESSION", Q=None, metrics=None); jn(dict(run="exp", board=name, stage="experiment", status="NO_SESSION", note="%s: no session in %d s" % (cfg["name"], wall)))
            else: finish(row, cfg, w, board, ses, flog)
            return row
        def finish(row, cfg, w, board, ses, flog):
            """the production finish on the routed copy, every count recorded: the raw route (route_one's score), the dangling clean-up, the stub router
            (closes what the router left open, as finish_*.sh do), the DRC-gated quality pass, the final DRC, the metrics and the grade"""
            raw = (read(os.path.join(w, "score.txt")) or "").split()
            if len(raw) >= 3: row["raw"] = {"hard": int(raw[0]), "unrouted": int(raw[1]), "vias": int(raw[2])}
            shutil.copy(os.path.join(project, name + ".kicad_pro"), os.path.join(w, name + ".kicad_pro"))
            sh(["python3", os.path.join(tools, "cleanup_dangling.py"), board], project, flog)
            sh(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", os.path.join(w, "pre-stub-drc.json"), board], project, flog)
            sh(["python3", os.path.join(tools, "stub_router.py"), board, os.path.join(w, "pre-stub-drc.json")], project, os.path.join(w, "stub.log"), {"STUB_LAYERS": exp.get("stub_layers", "F.Cu,B.Cu"), "STUB_GRID": str(exp.get("stub_grid", "0.05"))})
            st = re.search(r"stub_router: closed (\d+) of (\d+)", read(os.path.join(w, "stub.log")) or "")
            row["stub_closed"], row["stub_open"] = (int(st.group(1)), int(st.group(2))) if st else (None, None)
            sh(["bash", os.path.join(tools, "quality_pass.sh"), w, name], project, flog)
            sh(["kicad-cli", "pcb", "drc", "--severity-all", "--format", "json", "-o", os.path.join(w, "final-drc.json"), board], project, flog)
            mfile = os.path.join(w, "metrics.json"); fr = read(os.path.join(w, "fr.log")) or ""
            m_auto = re.search(r"Auto-routing was completed in (\d+) minute\(s\) ([\d.]+) seconds", fr); m_opt = re.search(r"optimization was completed in (\d+) minute\(s\) ([\d.]+) seconds", fr)
            argv = ["python3", os.path.join(tools, "route_metrics.py"), board, os.path.join(w, "final-drc.json"), "--json", mfile, "--tag", key, "--wall", str(row["wall_s"])]
            if m_auto: argv += ["--autoroute", "%.2f" % (int(m_auto.group(1)) + float(m_auto.group(2)) / 60)]
            if m_opt: argv += ["--optimizer", "%.2f" % (int(m_opt.group(1)) + float(m_opt.group(2)) / 60)]
            sh(argv, project, flog)
            try:
                m = json.load(open(mfile)); base_all = json.load(open(os.path.join(tools, "routeflow", "bench", "baseline.json"))); bench_compare = __import__("bench_compare")
                v, note, q = bench_compare.compare(base_all[key], m) if key in base_all else ("UNMEASURABLE", "no baseline for " + key, None)
                row.update(verdict=v, Q=q, metrics=m, note=note); jn(dict(run="exp", board=name, stage="experiment", status="MEASURED", note="%s: %s (raw %s, stub closed %s of %s) %s" % (cfg["name"], v, row.get("raw"), row.get("stub_closed"), row.get("stub_open"), note[:160])))
            except Exception as e:
                row.update(verdict="UNMEASURABLE", Q=None, metrics=None, note=str(e)[:200]); jn(dict(run="exp", board=name, stage="experiment", status="UNMEASURABLE", note="%s: %s" % (cfg["name"], str(e)[:160])))
        def refinish(cfg, old):
            """a row routed under an older finish: the routed board again from the pre-route board and the kept session (the import is deterministic, as route_one.sh does it), then the finish; the route is not repeated"""
            jar_path, jar_sha, ckey = ident(cfg); k = "exp-" + cfg["name"]; w = os.path.join(project, "out", "par", k); ses = os.path.join(w, name + ".ses"); board = os.path.join(w, name + ".kicad_pcb"); flog = os.path.join(w, "finish.log")
            if not os.path.exists(ses) or os.path.getsize(ses) == 0: return None
            shutil.copy(pre, board); shutil.copy(os.path.join(project, name + ".kicad_pro"), os.path.join(w, name + ".kicad_pro"))
            sh(["python3", "-c", "import sys, pcbnew; b = pcbnew.LoadBoard(sys.argv[1]); ok = pcbnew.ImportSpecctraSES(b, sys.argv[2]); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); pcbnew.SaveBoard(sys.argv[1], b); print('SES import:', ok)", board, ses], project, flog)
            sh(["python3", os.path.join(tools, "net_tie.py"), board], project, flog)
            row = dict(old); row.update(ts=now(), finish_version=FINISH_VERSION, refinished=True, host=os.uname().nodename)
            finish(row, cfg, w, board, ses, flog); return row
            return row
        def write_row(row):
            if row is None: return
            with open(results, "a") as f:
                fcntl.flock(f, fcntl.LOCK_EX); f.write(json.dumps(row) + "\n"); f.flush(); fcntl.flock(f, fcntl.LOCK_UN)
        if parallel <= 1:
            for cfg, old in refin: write_row(refinish(cfg, old))
            for cfg in pending: write_row(one(cfg, 0))
        else:
            with concurrent.futures.ThreadPoolExecutor(max_workers=parallel) as ex:
                futs = {ex.submit(one, cfg, i): cfg for i, cfg in enumerate(pending)}
                futs.update({ex.submit(refinish, cfg, old): cfg for cfg, old in refin})
                for fut in concurrent.futures.as_completed(futs):
                    try: write_row(fut.result())
                    except Exception as e: jn(dict(run="exp", board=name, stage="experiment", status="TOOL_CRASH", note="%s: %s" % (futs[fut]["name"], str(e)[:160])))
    finally:
        if use_services: services(exp.get("services_script"), "start", os.path.join(project, "out", "experiment.log"))
        for lk in (LOCK, plock):
            try: os.remove(lk)
            except OSError: pass
    jn(dict(run="exp", board=name, stage="end", status="COMPLETE", note="results in %s" % results)); return 0

# ---------------------------------------------------------------- status, preflight, selftest
def status(project, markdown):
    fn = os.path.join(project, "out", "routeflow", "journal.jsonl"); t = read(fn)
    if t is None: print("no journal at", fn); return 1
    rows = [json.loads(ln) for ln in t.splitlines() if ln.strip()]
    if markdown:
        print("| time | run | round | stage | status | note |\n|---|---|---|---|---|---|")
        for r in rows: print("| %s | %s | %s | %s | %s | %s |" % (r["ts"], r.get("run", "")[:8], r.get("round", ""), r.get("stage", ""), r.get("status", ""), str(r.get("note", "")).replace("|", "/")[:160]))
    else:
        for r in rows: print(r["ts"], r.get("run", "")[:8], r.get("round", ""), r.get("stage", ""), r.get("status", ""), str(r.get("note", ""))[:160])
    print("%d journal lines" % len(rows)); return 0

def preflight(repo):
    checks = []
    for mod in ("pcbnew", "numpy", "PIL"):
        try: __import__(mod); checks.append((mod + " importable", True, ""))
        except Exception as e: checks.append((mod + " importable", False, str(e)[:60]))
    for b in ("kicad-cli", "java", "xvfb-run"): checks.append((b + " on PATH", shutil.which(b) is not None, ""))
    jar = os.path.expanduser("~/bin/freerouting-1.9.0.jar"); checks.append(("freerouting jar", os.path.exists(jar), jar))
    try:
        mem = {l.split(":")[0]: int(l.split()[1]) // 1024 for l in open("/proc/meminfo") if l.startswith(("MemTotal", "MemAvailable"))}
        checks.append(("memory available >= 8 GB", mem["MemAvailable"] >= 8192, "%d of %d MB free" % (mem["MemAvailable"], mem["MemTotal"])))
    except Exception as e: checks.append(("memory", False, str(e)[:60]))
    try: load = os.getloadavg()[0]; checks.append(("load average under 8", load < 8, "%.1f" % load))
    except Exception: pass
    svc = os.path.expanduser("~/meshsat-services.sh"); checks.append(("service group script", os.path.exists(svc), svc + (" (stop it before a route)" if os.path.exists(svc) else " absent: not the build host")))
    try:
        subprocess.run(["git", "fetch", "-q", "origin"], cwd=repo, capture_output=True, timeout=60)
        anc = subprocess.run(["git", "merge-base", "--is-ancestor", "origin/main", "HEAD"], cwd=repo).returncode == 0
        dirty = subprocess.run(["git", "status", "--porcelain", "v2/ecad/tools"], cwd=repo, capture_output=True, text=True).stdout.strip()
        checks.append(("tools tree at or past origin/main", anc, "" if anc else "HEAD behind origin/main")); checks.append(("tools tree clean", not dirty, dirty[:80]))
    except Exception as e: checks.append(("git state", False, str(e)[:60]))
    held = os.path.exists(LOCK) and os.path.exists("/proc/%d" % json.load(open(LOCK)).get("pid", -1)) if os.path.exists(LOCK) else False
    checks.append(("no other route running", not held, read(LOCK) or ""))
    ok = sum(1 for c in checks if c[1])
    for name_, good, note in checks: print("%s  %s  %s" % ("PASS" if good else "FAIL", name_, note))
    print("preflight: %d of %d checks pass" % (ok, len(checks)))
    required = [c for c in checks if not c[1] and c[0].split()[0] in ("pcbnew", "numpy", "kicad-cli", "java", "xvfb-run", "freerouting", "no")]
    return 0 if not required else 2

def selftest():
    """Every predicate is fed an empty or missing input and must answer with a blocking state, never a pass."""
    t = tempfile.mkdtemp(prefix="routeflow-selftest-"); res = []
    def chk(name_, cond): res.append((name_, cond)); print("%s  %s" % ("PASS" if cond else "FAIL", name_))
    chk("missing pre log blocks", judge_pre(None, [], 1, [])[0] == "GATE_BLOCKED")
    chk("empty pre log blocks", judge_pre("", ["PREROUTE-DONE OK"], 1, [])[0] == "GATE_BLOCKED")
    chk("two ALL PASS with a FAIL between still blocks", judge_pre("RESULT: ALL PASS\nFAIL U outline\nRESULT: ALL PASS\nPREROUTE-DONE OK\n", ["PREROUTE-DONE OK"], 2, [])[0] == "GATE_BLOCKED")
    chk("generator log without saved blocks", judge_pre("RESULT: ALL PASS\nPREROUTE-DONE OK\n", ["PREROUTE-DONE OK"], 1, [dict(file=os.path.join(t, "nolog"))])[0] == "GATE_BLOCKED")
    open(os.path.join(t, "gen.log"), "w").write("footprint X not found\n"); chk("generator log with a silent SystemExit message blocks", judge_pre("RESULT: ALL PASS\nPREROUTE-DONE OK\n", ["PREROUTE-DONE OK"], 1, [dict(file=os.path.join(t, "gen.log"))])[0] == "GATE_BLOCKED")
    open(os.path.join(t, "gen.log"), "w").write("saved board.kicad_pcb outline U\n"); chk("a healthy pre log passes", judge_pre("RESULT: ALL PASS\nRESULT: ALL PASS\nPREROUTE-DONE OK\n", ["PREROUTE-DONE OK"], 2, [dict(file=os.path.join(t, "gen.log"))])[0] == "GATED")
    os.makedirs(os.path.join(t, "par", "1")); chk("attempt without a score file scores out", parse_scores(os.path.join(t, "par"))["1"][0] == 9999)
    open(os.path.join(t, "par", "1", "score.txt"), "w").write("9999 9999 999999\n"); chk("9999 score is not a winner", min(parse_scores(os.path.join(t, "par")).values())[0] >= 9999)
    open(os.path.join(t, "empty.json"), "w").write("{}")
    try: load_drc(os.path.join(t, "empty.json")); chk("empty DRC JSON raises", False)
    except RuntimeError: chk("empty DRC JSON raises", True)
    try: load_drc(os.path.join(t, "absent.json")); chk("missing DRC JSON raises", False)
    except RuntimeError: chk("missing DRC JSON raises", True)
    knot = {"violations": [{"type": "clearance", "items": [{"description": "Track [+3V3] on In3.Cu, length 0.02 mm"}, {"description": "Track [/WIFI_DIS] on In3.Cu, length 0.03 mm"}]}] * 5, "unconnected_items": [1] * 5}
    chk("knot signature detected", signature(knot)[0] == "KNOT")
    edge = {"violations": [{"type": "copper_edge_clearance", "items": [{"description": "Segment on Edge.Cuts"}, {"description": "Track [/X] on F.Cu, length 4 mm"}]}] * 6 + [{"type": "clearance", "items": [{"description": "Track [/A] on B.Cu, length 4 mm"}, {"description": "Pad 1 [/B] of JP2 on B.Cu"}]}], "unconnected_items": []}
    chk("edge signature detected", signature(edge)[0] == "EDGE")
    chk("clean signature", signature({"violations": [{"type": "silk_overlap", "items": []}], "unconnected_items": []})[0] == "CLEAN")
    chk("opens signature", signature({"violations": [], "unconnected_items": [1, 2]})[0] == "OPEN")
    prof = {"route": {"attempts": [50], "threads": 2, "timeout": 4500}, "plane_layers": ["In1.Cu", "In4.Cu"]}
    r, why = remedy("NO_SESSION", prof, set()); chk("no session -> power layers and timeout x 2", r and r.get("power_layers") == ["In1.Cu", "In4.Cu"] and r["timeout"] == 9000)
    r, why = remedy("KNOT", prof, set()); chk("knot -> one thread", r and r["threads"] == 1)
    r, why = remedy("KNOT", {"route": {"attempts": [50], "threads": 1}}, set()); chk("knot with one thread stops", r is None)
    r, why = remedy("EDGE", prof, set()); chk("edge stops for the generator", r is None)
    r, why = remedy("OPEN", prof, set()); chk("opens -> via costs 100 first", r and r.get("via_costs") == 100)
    r, why = remedy("OPEN", {"route": {"attempts": [50], "via_costs": 100}}, {"via_costs"}); chk("opens after via costs -> more passes once", r and r["attempts"] == [65])
    r, why = remedy("OPEN", {"route": {"attempts": [65], "via_costs": 100}}, {"via_costs", "passes"}); chk("opens three times stops", r is None)
    chk("missing clean flag refuses", judge_finish(os.path.join(t, "nofinish.log"), os.path.join(t, "noflag"), None, None)[0] == "FINISH_REFUSED")
    open(os.path.join(t, "flag"), "w").write("open\n"); chk("open flag refuses", judge_finish(os.path.join(t, "nofinish.log"), os.path.join(t, "flag"), None, None)[0] == "FINISH_REFUSED")
    open(os.path.join(t, "flag"), "w").write("clean\n"); open(os.path.join(t, "fin.log"), "w").write("routed-board gate: hard 0 unrouted 0\n"); os.makedirs(os.path.join(t, "deliv"))
    chk("clean flag without a gerber zip refuses", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "FINISH_REFUSED")
    open(os.path.join(t, "deliv", "x-gerbers.zip"), "w").write("z"); chk("clean flag with a deliverable passes", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "CLEAN")
    open(os.path.join(t, "stub.log"), "w").write("Traceback (most recent call last):\n"); chk("stub router traceback is a tool crash", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), os.path.join(t, "stub.log"), os.path.join(t, "deliv"))[0] == "TOOL_CRASH")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import bench_compare
        base = {"vias_router": 100, "length_mm": 1000.0, "tracks": 500, "hard": 0, "unrouted": 0}
        same = dict(base, hard_types_checked=6, connections=300, pairs_over_1mm=0)
        v, note, q = bench_compare.compare(base, same); chk("board compared with itself is MET with Q 1.0", v == "MET" and abs(q - 1.0) < 1e-9)
        v, note, q = bench_compare.compare(base, dict(same, unrouted=1)); chk("a deleted track (one open) is INELIGIBLE, not ranked", v == "INELIGIBLE" and q is None)
        v, note, q = bench_compare.compare(base, dict(same, vias_router=110)); chk("router vias +10 percent is a REGRESSION", v == "REGRESSION")
        v, note, q = bench_compare.compare(base, dict(same, pairs_over_1mm=2)); chk("a pair over 1 mm is a REGRESSION", v == "REGRESSION")
        v, note, q = bench_compare.compare(base, dict(same, vias_router=80, length_mm=950.0, tracks=450)); chk("fewer vias, shorter, fewer segments is MET with Q under 1", v == "MET" and q < 1.0)
        v, note, q = bench_compare.compare(base, {"hard": None, "unrouted": None}); chk("metrics without DRC numbers are UNMEASURABLE", v == "UNMEASURABLE")
    except ImportError as e: chk("bench_compare importable", False)
    shutil.rmtree(t, ignore_errors=True); ok = sum(1 for _, c in res if c)
    print("selftest: %d of %d predicates block on empty input as required" % (ok, len(res))); return 0 if ok == len(res) else 1

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == "preflight": sys.exit(preflight(a[a.index("--repo") + 1] if "--repo" in a else os.getcwd()))
    if a[0] == "selftest": sys.exit(selftest())
    if a[0] == "status": sys.exit(status(a[1], "--markdown" in a))
    if a[0] == "run": sys.exit(run(a[1], int(a[a.index("--rounds") + 1]) if "--rounds" in a else 2, "--no-services" not in a, "--dry-run" in a))
    if a[0] == "experiment": sys.exit(experiment(a[1], float(a[a.index("--budget-hours") + 1]) if "--budget-hours" in a else 6.0, "--no-services" not in a, int(a[a.index("--parallel") + 1]) if "--parallel" in a else 1))
    print(__doc__); sys.exit(2)
