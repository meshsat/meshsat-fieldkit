#!/usr/bin/env python3
"""routeflow: the supervisor around the board chains and Freerouting (v2/docs/routeflow-methodology.md, 5 Sep 2026).

It runs the EXISTING stage scripts of a board with fixed argument vectors (pre-route chain, route_parallel.sh, finish_*.sh), judges each
stage by its own artefacts (a `saved` line, a session file, a parseable DRC JSON, the clean flag), records every transition in an append-only
journal with a fixed status vocabulary, applies a small deterministic remedy table to the failure signatures of 5 Sep 2026 within a round
budget, and stops with a named state when the table ends. No model is in the loop; a stop is the session's cue to fix a generator.

Usage:
  routeflow.py preflight [--repo DIR]                 host checks (imports, binaries, jar, memory, load, services, git, lock)
  routeflow.py validate <profile.json> [--repo DIR]    the profile against the tree: nothing written, no host touched
  routeflow.py run <profile.json> [--rounds N] [--no-services] [--dry-run]
  routeflow.py status <project dir> [--markdown]      the journal
  routeflow.py selftest                               kill the predicates with empty inputs; every one must block
  routeflow.py experiment <exp.json> [--budget-hours H] [--no-services] [--parallel N]   one route per configuration (rules file knobs, jar) on one pre-route board, measured into bench/results.jsonl; N configurations at once

Profile (JSON): see tools/routeflow/*.json. Placeholders in argv: <PROJECT> (the project dir), <ECAD> (its parent), <NAME> (the board stem).
"""
import platform, sys, os, re, json, time, glob, hashlib, subprocess, shutil, collections, tempfile, datetime, fcntl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict   # one hash implementation, and the same one the gates write into their verdicts
import hardset   # the one DRC policy, for grading a profile's prediction
import ledger    # the journal is a chained ledger, not an append-only file

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hardset   # 10 September 2026: the supervisor used to carry its own six-type tuple while the finish refused on hardset's
                 # fifteen, so a board with only (say) track_width violations was journalled ROUTED_CLEAN here, refused there,
                 # and the remedy table had no case for the disagreement. One definition, imported (both red teams, C1/P0).
HARD = hardset.HARD_POST
LOCK = os.path.expanduser(os.environ.get("ROUTEFLOW_LOCK") or "~/.routeflow.lock")   # ROUTEFLOW_LOCK: another lock name, so several experiments run side by side on a big host (6 Sep 2026)

def _kicad_version():
    """pcbnew's build string, or the CLI's, or "unknown"; never an exception, this is bookkeeping."""
    try:
        import pcbnew; return pcbnew.GetBuildVersion()
    except Exception: pass
    try:
        import subprocess as _sp; return _sp.run(["kicad-cli", "version"], capture_output=True, text=True, timeout=30).stdout.strip() or "unknown"
    except Exception: return "unknown"


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
    hard = [v for v in drc["violations"] if v["type"] in HARD and not hardset.exempt(v)]; unr = len(drc.get("unconnected_items", []))   # hardset's own exemptions: a footprint against itself
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

def judge_verdicts(project, require=(), since=None):
    """What the gates themselves decided, read from their verdict JSONs rather than from their prose.

    The seam stage 0 left open (11 September 2026): every gate writes `out/<tool>.verdict.json` now, and the
    supervisor still judged stages by log markers, flag files and the DRC JSON. A gate could write FAIL and this
    would not notice unless its prose happened to match a grep. The log checks stay: they catch a crash, a missing
    marker and a generator that never saved, none of which a verdict can report because the tool never got that far.
    """
    out = os.path.join(project, "out")
    # Only the verdicts this stage wrote. Verdict files persist in out/ across stages and rounds, and boards P
    # and E were each blocked three times by a check_contracts verdict their OWN earlier finish had written.
    worst, found, missing = verdict.collect(out, require, since=since)
    bad = sorted("%s %s%s" % (t, r.get("verdict"), (" (%s)" % r["note"]) if r.get("note") else "")
                 for t, r in found.items() if r.get("verdict") != verdict.PASS)
    if missing: bad += ["%s did not run" % t for t in missing]
    if worst == 0:
        return "GATED", "%d gate verdict(s), all PASS" % len(found)
    return "GATE_BLOCKED", "%d of %d gate verdict(s) not PASS: %s" % (len(bad), len(found) + len(missing), "; ".join(bad[:6]))


def judge_expect(drc_path, exp):
    """The profile's own prediction, which until now was written in every profile and read by nothing.

    `expect: {hard, unrouted}` is a prediction in the sense the prediction gate means: written before the run,
    graded mechanically after it. Twelve profiles carry one."""
    if not exp or ("hard" not in exp and "unrouted" not in exp): return None, "no prediction in the profile"
    try: d = load_drc(drc_path)
    except Exception as e: return None, "no DRC to grade the prediction against (%s)" % e
    c = hardset.counts(d, "post")
    parts, met = [], True
    for k, got in (("hard", c["hard"]), ("unrouted", c["unrouted"])):
        if k not in exp: continue
        parts.append("%s %d against %s" % (k, got, exp[k]))
        if got > exp[k]: met = False
    return met, ", ".join(parts)


def judge_finish(finish_log, clean_flag, stub_log, deliverable):
    t = read(finish_log) or ""
    if "Traceback" in t or "CRASHED" in t or (stub_log and "Traceback" in (read(stub_log) or "")): return "TOOL_CRASH", "a finish stage crashed (see %s)" % finish_log
    flag = read(clean_flag)
    if flag is None: return "FINISH_REFUSED", "no clean flag written (%s)" % clean_flag
    if flag.strip() != "clean": return "FINISH_REFUSED", "flag says %r" % flag.strip()
    if deliverable and not glob.glob(os.path.join(deliverable, "*-gerbers.zip")): return "FINISH_REFUSED", "deliverable has no gerber zip: %s" % deliverable
    if "contracts: ALL PASS" not in t: return "FINISH_REFUSED", "the finish did not print 'contracts: ALL PASS' (check_contracts.py is part of every finish since 8 Sep 2026)"
    # 10 September 2026: this used to refuse only when REFUSED was also printed, so a finish that never ran the read-back at all
    # passed the gate. Absence of evidence is not evidence: the line must be there (both red teams, P1).
    if deliverable and "verify_deliverable: ALL PASS" not in t: return "FINISH_REFUSED", "the deliverable was not read back (verify_deliverable.py did not print ALL PASS)"
    m = re.search(r"routed-board gate: hard (\d+) unrouted (\d+)", t)
    return "CLEAN", ("routed-board gate: hard %s unrouted %s" % (m.group(1), m.group(2))) if m else "clean flag set"

# ---------------------------------------------------------------- remedies (profile changes, bounded)
def remedy(sig, prof, applied):
    r = dict(prof["route"])
    if sig == "INFRA_FAIL": return None, "the router supervisor failed; fix the host or the invocation, do not change the route"
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
# The board files a stage can produce or consume, by the board's name. A stage's row carries the hash of every one
# that exists at the moment the row is written, so "in" and "out" are the same field read on consecutive rows.
BOARD_FILES = ("%s.kicad_pcb", "out/%s-placed.kicad_pcb", "out/%s-preroute.kicad_pcb",
               "out/%s-par-routed.kicad_pcb", "out/%s-routed.kicad_pcb")


def board_hashes(project, name):
    """MESHSAT-862, stage 0c, 11 September 2026: a run recorded its configuration and never the bytes it acted on.

    provenance.json is written before the chain generates the board it names, so its board hash was the PREVIOUS
    run's board or nothing at all, and a journal row said which knobs were set and never which board they were set
    on. Two runs of one profile that produce different boards were indistinguishable in the record, which is also
    what made the determinism question (stage 0b) unanswerable from the journal."""
    out = {}
    for pat in BOARD_FILES:
        fn = os.path.join(project, pat % name)
        h = verdict.sha256_file(fn) if os.path.exists(fn) else None
        if h: out[os.path.basename(fn)] = h
    return out


def journal(project, rec):
    os.makedirs(os.path.join(project, "out", "routeflow"), exist_ok=True)
    rec = dict(ts=now(), **rec)
    if rec.get("board") and "boards" not in rec:
        try: rec["boards"] = board_hashes(project, rec["board"])
        except Exception as e: rec["boards"] = {"error": str(e)}
    # Chained (11 September 2026): each row carries the hash of the one before, so a row edited, removed or
    # reordered after the fact fails `ledger.py verify`. Append-only was never the same as tamper-evident.
    path = os.path.join(project, "out", "routeflow", "journal.jsonl")
    try: rec = ledger.append(path, rec)
    except Exception as e:
        rec["ledger_error"] = str(e)
        with open(path, "a") as f: f.write(json.dumps(rec) + "\n")
    print("[routeflow %s] %s %s  %s" % (rec["ts"][11:], rec.get("stage", ""), rec.get("status", ""), rec.get("note", "")), flush=True)

def fingerprint(repo, prof, project):
    """The deterministic identity of a run's INPUTS: the profile, the tools tree including uncommitted work, and the board it starts
    from. It indexes results; it does not name the run directory (10 September 2026, both red teams: a deterministic directory name
    let a second run append to the first one's logs and read its markers)."""
    h = hashlib.sha256(json.dumps(prof, sort_keys=True).encode())
    for argv in (["git", "rev-parse", "HEAD:v2/ecad/tools"], ["git", "diff", "HEAD", "--", "v2/ecad/tools"]):
        try: h.update(subprocess.run(argv, cwd=repo, capture_output=True, text=True).stdout.encode())   # the working tree counts: a run on an edited tool is a different input
        except Exception: pass
    pre = os.path.join(project, "out", "%s-preroute.kicad_pcb" % prof["board"])
    if os.path.exists(pre): h.update(open(pre, "rb").read())
    return h.hexdigest()[:12]

def new_run_dir(project, fp):
    """A fresh directory per invocation, never reused: <utc>-<fingerprint>[-n]."""
    base = os.path.join(project, "out", "routeflow"); os.makedirs(base, exist_ok=True)
    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for n in range(1, 100):
        d = os.path.join(base, "%s-%s" % (stamp, fp[:8]) if n == 1 else "%s-%s-%d" % (stamp, fp[:8], n))
        try: os.makedirs(d); return d
        except FileExistsError: continue
    raise RuntimeError("cannot make a run directory in %s" % base)

def provenance(repo, prof, project, fp):
    """What produced this run, recorded beside it: nothing here is inferred later from a filename."""
    def out(argv, cwd=repo):
        try: return subprocess.run(argv, cwd=cwd, capture_output=True, text=True, timeout=30).stdout.strip()
        except Exception: return ""
    pre = os.path.join(project, "out", "%s-preroute.kicad_pcb" % prof["board"])
    jar = os.path.expanduser(prof.get("route", {}).get("jar", "~/bin/freerouting-1.9.0.jar"))
    def sha(fn):
        try: return hashlib.sha256(open(fn, "rb").read()).hexdigest()[:16]
        except Exception: return None
    try:
        import pcbnew as _pcb; kicad = _pcb.GetBuildVersion()
    except Exception: kicad = out(["kicad-cli", "version"])
    return {"fingerprint": fp, "utc": datetime.datetime.utcnow().isoformat() + "Z", "host": os.uname().nodename,
            "git_head": out(["git", "rev-parse", "HEAD"]), "git_tools_tree": out(["git", "rev-parse", "HEAD:v2/ecad/tools"]),
            "git_dirty": bool(out(["git", "status", "--porcelain", "v2/ecad/tools"])), "git_dirty_sha": hashlib.sha256(out(["git", "diff", "HEAD", "--", "v2/ecad/tools"]).encode()).hexdigest()[:16],
            # NOT the board this run produces: provenance is written before the chain generates it, so this is
            # whatever was on disk from the previous run, or nothing. The board a stage acted on is in that
            # stage's journal row, under "boards" (stage 0c, 11 September 2026).
            "board_sha_before_run": sha(pre), "board_file": pre, "kicad": kicad, "python": sys.version.split()[0],
            "freerouting_jar": os.path.basename(jar), "freerouting_sha": sha(jar), "java": out(["java", "-version"]) or out(["bash", "-c", "java -version 2>&1 | head -1"])}

_LOCK_FH = []   # kept open for the life of the process: closing the handle releases the flock

def take_lock(board):
    """An exclusive flock on the lock file, not a check followed by a write: two routeflows could pass the existence test at the
    same time and both proceed (10 September 2026, both red teams). The JSON body stays, for the message."""
    fh = open(LOCK, "a+")
    try: fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.seek(0)
        try: o = json.loads(fh.read() or "{}")
        except Exception: o = {}
        fh.close(); return False, "router held by %s (pid %s since %s)" % (o.get("board"), o.get("pid"), o.get("since"))
    fh.seek(0); fh.truncate(); fh.write(json.dumps({"board": board, "pid": os.getpid(), "since": now()})); fh.flush()
    _LOCK_FH.append(fh); return True, "lock taken"

def services(script, action, log):
    if script and os.path.exists(os.path.expanduser(script)): sh([os.path.expanduser(script), action], os.path.expanduser("~"), log)

def expand(argv, project, ecad, name): return [a.replace("<PROJECT>", project).replace("<ECAD>", ecad).replace("<NAME>", name) for a in argv]

def validate(profile_fn, repo=None):
    """Everything about a profile that can be judged without a host, a board or a filesystem write.

    11 September 2026 (MESHSAT-862). `--dry-run` was not one: it still created the run directory, wrote
    provenance, ran preflight and took the lock, so a box profile could not be checked from the runner at all
    and the first thing that read it was an eight-hour wave. Five profiles were carrying a phase one behind the
    deliverable their own finish cuts when this was written; that is the class of defect this catches in a
    second. Prints one line per property and returns a verdict code."""
    prof = json.load(open(profile_fn)); b = os.path.basename(profile_fn)
    repo = repo or os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    ecad = os.path.join(repo, "v2", "ecad"); tools = os.path.join(ecad, "tools")
    fails, lines = [], []
    def ok(cond, text):
        lines.append(("PASS  " if cond else "FAIL  ") + text)
        if not cond: fails.append(text)

    for k in ("board", "project", "phase", "route", "finish"):
        ok(k in prof, "profile declares %s" % k)
    if fails:
        for l in lines: print("validate: " + l)
        return verdict.write("routeflow_validate", verdict.FAIL, denominator=len(lines), evidence=fails,
                             counts={"fail": len(fails)}, inputs={"profile": b})

    proj = os.path.basename(str(prof["project"]).rstrip("/")); phase = prof["phase"]
    fin = prof["finish"]; argv = fin.get("argv") or []
    ok(bool(argv), "the finish declares an argv")
    if argv:
        script = os.path.join(ecad, argv[0].lstrip("./"))
        ok(os.path.exists(script), "the finish script exists: %s" % argv[0])
        ok(fin.get("cwd") == "<ECAD>", "the finish runs from <ECAD>, which is the only place its relative argv[0] resolves")
        if os.path.basename(argv[0]) == "finish.sh" and len(argv) >= 6:
            _, _, aproj, letter, aphase, alog = argv[:6]
            ok(aproj == proj, "the finish runs in the profile's own project directory (%s against %s)" % (aproj, proj))
            ok(aphase == phase, "the finish cuts the profile's phase (%s against %s)" % (aphase, phase))
            ok(os.path.exists(os.path.join(tools, "boards", "%s.json" % letter)), "a board file exists for letter %s" % letter)
            want = "meshsat-pcb-%s-revA-%s" % (letter, aphase)
            ok(os.path.basename(prof.get("deliverable", "")) == want,
               "the deliverable is the one the finish writes (%s against %s)" % (os.path.basename(prof.get("deliverable", "")) or "-", want))
            ok(fin.get("clean_flag") == "out/%s-clean.txt" % aphase.lower(),
               "the clean flag is the phase's own (%s)" % fin.get("clean_flag"))
            ok(alog == (prof["route"].get("log") or alog), "the finish waits on the log the route writes (%s against %s)" % (alog, prof["route"].get("log")))
    pre = prof.get("pre") or {}
    # Two shapes exist for the same stage: `argv` (one command) and `steps` (a list of them). Both are checked,
    # because the profile that carried the stale generator log used `steps`, and the first version of this rule
    # looked only at `argv`, so it never ran on the one profile it was written for.
    cmds = ([pre["argv"]] if pre.get("argv") else []) + [c for c in (pre.get("steps") or []) if isinstance(c, list)]
    ok(bool(cmds), "the pre-route stage declares a command")
    for cmd in cmds:
        ps = cmd[1] if len(cmd) > 1 else ""
        cand = os.path.join(ecad, ps[3:]) if ps.startswith("../") else os.path.join(ecad, ps.lstrip("./"))
        ok(os.path.exists(cand), "the pre-route script exists: %s" % ps)
    if cmds: ok(bool(pre.get("must_contain")), "the pre-route stage names what its log must contain")
    # A declared generator log the chain never writes blocks every run of that board: c7 and c8 named
    # out/gen_pcb_c3.log, which no chain has written since full.sh replaced the clones, and C died on it twice
    # in one wave while its own chain printed PREROUTE-DONE OK.
    # The board's OWN letter, not any token: the first version of this rule used [a-z0-9]+ and so accepted
    # out/gen_pcb_c3.log, the very file it was written to catch.
    _L = (fin.get("argv") or [None] * 4)[3] or ""
    WRITES = {"out/gen_sch.log", "out/gen_fp.log", "out/gen3.log", "out/gen_pcb_%s.log" % _L}
    for g in pre.get("gen_logs") or []:
        f = g.get("file") if isinstance(g, dict) else g
        ok(f in WRITES, "the declared generator log is one the chain writes: %s (it writes %s)"
           % (f, ", ".join(sorted(WRITES))))
    ok(bool(prof.get("expect")), "the profile carries an expectation to be graded against")
    jar = str(prof["route"].get("jar", ""))
    ok(not jar or jar.endswith(".jar"), "the route names a jar file (%s)" % (jar or "the host default"))

    for l in lines: print("validate: " + l)
    print("validate: %s (%d of %d properties, %s)" % ("ALL PASS" if not fails else "%d FAIL" % len(fails),
                                                      len(lines) - len(fails), len(lines), b))
    return verdict.write("routeflow_validate", verdict.PASS if not fails else verdict.FAIL,
                         counts={"fail": len(fails), "pass": len(lines) - len(fails)},
                         denominator=len(lines), evidence=fails, inputs={"profile": b},
                         note="the profile against the tree, with nothing written and no host touched")


def run(profile_fn, rounds, use_services, dry):
    prof = json.load(open(profile_fn)); repo = prof.get("repo") or os.getcwd()
    project = os.path.abspath(os.path.join(repo, prof["project"])); ecad = os.path.dirname(project); name = prof["board"]
    os.makedirs(os.path.join(project, "out", "routeflow"), exist_ok=True)
    fp = fingerprint(repo, prof, project); rdir = new_run_dir(project, fp); rid = os.path.basename(rdir)
    json.dump(provenance(repo, prof, project, fp), open(os.path.join(rdir, "provenance.json"), "w"), indent=1)
    json.dump({"profile": prof, "profile_file": os.path.abspath(profile_fn), "rounds": rounds, "services": bool(use_services), "dry": bool(dry),
               "env": {k: v for k, v in sorted(os.environ.items()) if k.startswith(("PAIR_", "FR_", "ROUTEFLOW_", "PLACE_", "STUB_", "ESCAPE_", "BYPASS_"))}},
              open(os.path.join(rdir, "resolved-config.json"), "w"), indent=1)
    # 10 September 2026 (report 1, P2): preflight existed and was optional exactly where an expensive run begins. It runs here now;
    # ROUTEFLOW_SKIP_PREFLIGHT=1 is for a host that is deliberately not the build host, and it is journalled when it is used.
    if os.environ.get("ROUTEFLOW_SKIP_PREFLIGHT") != "1":
        prc = preflight(repo)
        journal(project, dict(run=rid, board=name, phase=prof["phase"], stage="preflight", status="PREFLIGHT_OK" if prc == 0 else "PREFLIGHT_FAIL", note="required checks %s" % ("pass" if prc == 0 else "FAIL, see the lines above")))
        if prc != 0: return 2
    else:
        journal(project, dict(run=rid, board=name, phase=prof["phase"], stage="preflight", status="PREFLIGHT_SKIPPED", note="ROUTEFLOW_SKIP_PREFLIGHT=1"))
    ok, msg = take_lock(name)
    journal(project, dict(run=rid, fingerprint=fp, board=name, phase=prof["phase"], stage="lock", status="LOCKED" if ok else "PREFLIGHT_FAIL", note=msg))
    if not ok: return 2
    applied = set(); status = None
    try:
        for rnd in range(1, rounds + 2):
            route = prof["route"]
            journal(project, dict(run=rid, round=rnd, board=name, stage="pre", status="GENERATING", note="expect %s" % json.dumps(prof.get("expect", {}))))
            pre = prof["pre"]; plog = os.path.join(rdir, "round%d-pre.log" % rnd)
            # The horizon for this stage's verdicts, and it has to be taken BEFORE the chain runs or it excludes
            # every verdict the chain writes. Set after, as it was for one commit, it would have hidden all of
            # them and read as "no verdicts at all" (11 September 2026; see verdict.collect).
            # A round starts with a clean verdict channel. The horizon alone is not enough: the stamp has
            # one-second resolution, so a verdict written in the same second as the stage began is not "before"
            # it, and P's round-two pre stage was blocked by a verify_deliverable its round-one finish had
            # written 0 seconds earlier. Clearing is also the honest thing: a gate that does not re-run this
            # round should read as absent, which verdict.collect already treats as INCONCLUSIVE when required.
            if not dry:
                for _v in glob.glob(os.path.join(project, "out", "*.verdict.json")):
                    try: os.remove(_v)
                    except OSError: pass
            pre_started = verdict.now()   # UTC in the verdict channel's own format, never routeflow's local now()
            rc = 0
            if not dry:
                for argv in (pre.get("steps") or [pre["argv"]]):   # fixed argument vectors, one process each, no shell string
                    rc = sh(expand(argv, project, ecad, name), project if pre.get("cwd", "<PROJECT>") == "<PROJECT>" else ecad, plog)
                    if rc != 0: break
            gen_logs = [dict(g, file=os.path.join(project, g["file"])) for g in pre.get("gen_logs", [])]
            st, note = judge_pre(read(plog), pre.get("must_contain", []), pre.get("min_all_pass", 1), gen_logs) if not dry else ("GATED", "dry run")
            if rc != 0 and st == "GATED": st, note = "TOOL_CRASH", "pre-route chain exit %d" % rc
            journal(project, dict(run=rid, round=rnd, board=name, stage="pre", status=st, note=note))
            if st == "GATED" and not dry:
                vst, vnote = judge_verdicts(project, prof.get("expect", {}).get("verdicts", ()), since=pre_started)
                journal(project, dict(run=rid, round=rnd, board=name, stage="pre", status=vst, note=vnote))
                if vst != "GATED": st, note = vst, vnote
            if st != "GATED": status = st; break
            env = {"FR_THREADS": str(route.get("threads", 2)), "FR_TIMEOUT": str(route.get("timeout", 4500))}
            if route.get("power_layers"): env["FR_POWER_LAYERS"] = " ".join(route["power_layers"])
            if route.get("plane_nets"): env["FR_PLANE_NETS"] = ",".join(route["plane_nets"])   # zones of these nets on the power layers stay in the DSN as planes (6 Sep 2026: GND by vias into In1, not as wires)
            if route.get("jar"): env["FR_JAR"] = os.path.expanduser(route["jar"])
            # the optimiser is where a route disappears: C8's auto-route finished in 14 min 21 s and the two default optimiser passes
            # then ran past a 90 minute limit with no session written, three times (8 Sep 2026 19:35). A profile may cap it.
            if route.get("optimiser_passes") is not None: env["FR_OIT"] = str(route["optimiser_passes"])
            if route.get("layer_rules"): env["FR_LAYER_RULES"] = ";".join("%s:%s" % (c, ",".join(ls)) for c, ls in route["layer_rules"].items())   # rule 2 of 32.67: a class only on layers with a plane next to them   # the router build (Stage 4: freerouting-2.4.1.jar beside 1.9.0)
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
                rc = sh(["./tools/route_parallel.sh", os.path.basename(project), name, " ".join(str(p) for p in route["attempts"])], ecad, rlog, env)   # the project directory, not the board name (a copy directory such as pcb-a-power-a23, 8 Sep 2026)
            scores = parse_scores(os.path.join(project, "out", "par")) if not dry else {}
            best = min(scores.items(), key=lambda kv: kv[1]) if scores else (None, (9999, 9999, 999999))
            mins = {k: autoroute_minutes(os.path.join(project, "out", "par", k, "fr.log")) for k in scores}
            if best[1][0] >= 9999 and rc != 0:
                # 10 September 2026 (both red teams, P0): route_parallel.sh's exit code was captured and then ignored, so a crashed
                # supervisor became NO_SESSION and the remedy doubled the timeout for what was never a routing problem.
                sig = "INFRA_FAIL"; note = "the router supervisor exited %d and wrote no session; this is not a routing outcome (see %s)" % (rc, rlog)
            elif best[1][0] >= 9999:
                # With our patched jar a session is written after EVERY pass, so "no session at all" stops being a
                # routing outcome and becomes something that went wrong: the job never started, the DSN was refused,
                # the host ran out of memory. Calling it NO_SESSION sends the remedy table off to double a timeout
                # that was never the problem, which is the two nights A23 lost. Round-two H5, 11 September 2026.
                _mesh = os.path.exists(os.path.expanduser("~/bin/freerouting-1.9.0-mesh.jar")) and not route.get("jar")
                if _mesh:
                    sig = "INFRA_FAIL"; note = ("the per-pass jar wrote NO session in %d attempts, so this is not a routing "
                                               "outcome: the job did not run. autoroute minutes %s" % (len(scores), mins))
                else:
                    sig = "NO_SESSION"; note = "no session in %d attempts on a jar that writes one only at the end; autoroute minutes %s" % (len(scores), mins)
            else:
                try: drc = load_drc(os.path.join(project, "out", "par", best[0], "drc.json")); sig, counts, unr = signature(drc)
                except RuntimeError as e: sig, counts, unr = "TOOL_CRASH", {}, None; note = str(e)
                if sig != "TOOL_CRASH":
                    nets = len(re.findall(r"^\s*\(net ", read(os.path.join(project, "out", "par", best[0], "%s.dsn" % name)) or "", re.M))
                    note = "winner attempt %s: hard %d of %d types %s, unrouted %d of %d nets, vias %d, autoroute minutes %s" % (best[0], best[1][0], len(HARD), dict(counts), unr, nets, best[1][2], mins)
            st = {"NO_SESSION": "NO_SESSION", "KNOT": "ROUTED_HARD", "HARD": "ROUTED_HARD", "EDGE": "ROUTED_HARD", "OPEN": "ROUTED_OPEN", "CLEAN": "ROUTED_CLEAN", "TOOL_CRASH": "TOOL_CRASH", "INFRA_FAIL": "INFRA_FAIL"}[sig]
            journal(project, dict(run=rid, round=rnd, board=name, stage="route", status=st, signature=sig, note=note))
            # The profile's own prediction, graded. `expect: {hard, unrouted}` is written in all twelve profiles and
            # was read by nothing until 11 September 2026; a prediction nobody grades is a comment.
            met, enote = judge_expect(os.path.join(project, "out", name + "-drc.json"), prof.get("expect", {}))
            if met is not None:
                journal(project, dict(run=rid, round=rnd, board=name, stage="expect",
                                      status="MET" if met else "MISSED", note="the profile predicted: " + enote))
            if sig in ("CLEAN", "OPEN", "HARD", "KNOT", "EDGE"):
                # the finish gets its chance on every routed board: cleanup, stub router, pairs, the routed-board gate
                fin = prof["finish"]; flog = os.path.join(rdir, "round%d-finish.log" % rnd)
                journal(project, dict(run=rid, round=rnd, board=name, stage="finish", status="FINISHING", note=" ".join(fin["argv"])))
                for stale in (os.path.join(project, fin["clean_flag"]), os.path.join(project, "out", "contracts.log")):   # 8 Sep 2026 (MESHSAT-862): a stale clean flag finished a board (register class 6)
                    try: os.remove(stale)
                    except OSError: pass
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
    sys.path.insert(0, tools); import bench_compare as _bc
    key = prof.get("baseline_key") or _bc.board_key(prof["board"])   # 10 Sep 2026: keyed by board; a phase key never matched (C3)
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
    project = os.path.abspath(os.path.join(repo, exp["project"])); ecad = os.path.dirname(project); name = exp["board"]
    _tools = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _tools); import bench_compare as _bc
    key = exp.get("board_key") or _bc.board_key(name)
    # 10 September 2026 (both red teams, C3): 66 of 81 measured router hours were thrown away by a dictionary lookup that ran
    # AFTER the route. The lookup runs first now: an experiment whose board has no baseline does not start.
    _base_fn = os.path.join(_tools, "routeflow", "bench", "baseline.json")
    _keys = sorted(json.load(open(_base_fn))) if os.path.exists(_base_fn) else []
    if key not in _keys:
        print("routeflow: experiment %s refused: no baseline for board key %r (have %s). Record one with `baseline`, or set board_key." % (os.path.basename(exp_fn), key, ", ".join(_keys)))
        return 2
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
            if cfg.get("plain"): rules = ""   # plain (6 Sep 2026 14:15): no settings block at all, the production configuration; a settings block, even with default values, costs the design's clearances on B15
            else: sh(argv, project, plog)
            route = dict(exp.get("route", {})); route.update({kk: cfg[kk] for kk in ("passes", "threads", "timeout", "power_layers") if kk in cfg})
            if cfg.get("planes"): route["plane_nets"] = list(cfg["planes"])
            timeout = int(route.get("timeout", 1800) * scale)
            env = {"FR_THREADS": str(route.get("threads", 1)), "FR_TIMEOUT": str(timeout), "FR_RULES": rules, "FR_RULES_INJECT": "1" if rules else "0", "FR_JAR": jar_path, "FR_FANOUT": "true" if cfg.get("fanout") else "false"}
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
            row = {"key": ckey, "board_key": key, "board": name, "config": cfg["name"], "cfg": cfg, "route": route, "rules_mode": RULES_MODE, "timeout_s": timeout, "starts": starts, "host": os.uname().nodename, "preroute_hash": pre_hash, "jar": os.path.basename(jar_path), "jar_sha": jar_sha, "wall_s": wall, "ts": now(), "finish_version": FINISH_VERSION,
                   # 10 September 2026 (report 2 M3): the tool versions belong in the row. A benchmark comparing two boxes or two
                   # months compares KiCad builds and Python versions too, and the record could not say which build a row was measured on.
                   "kicad": _kicad_version(), "python": platform.python_version(), "cpus": os.cpu_count()}
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
    held = False
    if os.path.exists(LOCK):
        try:
            with open(LOCK, "a+") as _fh:
                try: fcntl.flock(_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(_fh.fileno(), fcntl.LOCK_UN)
                except OSError: held = True
        except Exception: held = False
    # 11 September 2026: this is one lock for the whole host by default, which is the VM's memory rule (three
    # Freerouting attempts at 2 to 4 GB each filled its 31 GB on 5 September). On a 256-thread box four boards
    # are meant to route side by side, and the first wave lost three of them here with a message that did not
    # say how. ROUTEFLOW_LOCK is the answer and the message names it now.
    checks.append(("no other route running", not held,
                   ((read(LOCK) or "") + ("  [lock %s; set ROUTEFLOW_LOCK to a per-board path to route boards side by side on a host with the memory for it]" % LOCK if held else ""))))
    # The pin on which files may write a gerber, a BOM, a CPL or an order set. Cheap, and preflight runs where an
    # expensive run begins, which is the right place to notice that the actuation surface grew (11 September 2026).
    try:
        import execution_paths as _ep
        _found = _ep.producers()
        _unpinned = sorted(f for f in _found if f not in _ep.PIN and f not in _ep.READERS)
        _gone = sorted(f for f in _ep.PIN if f not in _found)
        checks.append(("fab-artefact producers match the pin", not _unpinned and not _gone,
                       ("unpinned %s" % _unpinned if _unpinned else "") + (" stale pin %s" % _gone if _gone else "")))
    except Exception as e: checks.append(("fab-artefact pin readable", False, str(e)[:60]))
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
    open(os.path.join(t, "deliv", "x-gerbers.zip"), "w").write("z"); chk("clean flag with a deliverable but no contracts line refuses", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "FINISH_REFUSED")
    # 10 September 2026: this row used to assert that a deliverable plus the contracts line PASSES, which is the hole report 1
    # names at this line: it codified "absence of evidence is evidence". The read-back line is required now.
    open(os.path.join(t, "fin.log"), "w").write("routed-board gate: hard 0 unrouted 0\ncontracts: ALL PASS\n"); chk("clean flag, deliverable and contracts but no read-back still refuses", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "FINISH_REFUSED")
    open(os.path.join(t, "fin.log"), "a").write("verify_deliverable: ALL PASS\n"); chk("with the read-back it passes", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "CLEAN")
    open(os.path.join(t, "fin.log"), "w").write("routed-board gate: hard 0 unrouted 0\ncontracts: FAIL (out/contracts.log)\n"); chk("a contracts FAIL line refuses", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "FINISH_REFUSED")
    open(os.path.join(t, "fin.log"), "w").write("routed-board gate: hard 0 unrouted 0\ncontracts: ALL PASS\nfinish_board: deliverable REFUSED, folder removed\n"); chk("a refused deliverable read-back refuses", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), None, os.path.join(t, "deliv"))[0] == "FINISH_REFUSED")
    open(os.path.join(t, "fin.log"), "w").write("routed-board gate: hard 0 unrouted 0\ncontracts: ALL PASS\n")
    try:   # 8 Sep 2026 (MESHSAT-862): the re-armed gates, each fed a broken input
        import hardset, erc_gate, verify_deliverable
        bad = {"violations": [{"type": "solder_mask_bridge", "items": [{"description": "Pad 1 [X] of U1 on F.Cu"}, {"description": "Track [Y] on F.Cu"}]}, {"type": "courtyards_overlap", "items": [{"description": "Footprint U9"}, {"description": "Footprint U9"}]}, {"type": "zones_intersect", "items": []}, {"type": "connection_width", "items": []}], "unconnected_items": []}   # drift-ok: a fixture fed to hardset.counts, not a policy
        c = hardset.counts(bad); chk("hardset: a pad-to-track mask bridge and a zone intersection are hard, the own-courtyard overlap exempt, connection_width reported", c["hard"] == 2 and c["exempt"] == {"courtyards_overlap": 1} and c["report"] == {"connection_width": 1})
        chk("hardset: fifteen types, pre and post the same", len(hardset.HARD_POST) == 15 and hardset.HARD_PRE == hardset.HARD_POST)
        try: hardset.load(os.path.join(t, "absent.json")); chk("hardset: a missing DRC JSON raises", False)
        except RuntimeError: chk("hardset: a missing DRC JSON raises", True)
        erc = {"sheets": [{"violations": [{"type": "pin_not_connected", "severity": "error", "description": "Pin 3 of U1", "items": []}, {"type": "power_pin_not_driven", "severity": "error", "description": "Input Power pin on +3V3_AB", "items": []}, {"type": "label_dangling", "severity": "warning", "description": "x", "items": []}]}]}
        blk, allowed, by = erc_gate.gate(erc, []); chk("erc_gate: two errors block with no allow-list, the warning does not", len(blk) == 2 and allowed == 0)
        blk, allowed, by = erc_gate.gate(erc, [("power_pin_not_driven", "+3V3_AB", "the gated rail comes over the harness")]); chk("erc_gate: an allow-listed error with a reason passes, the other still blocks", len(blk) == 1 and allowed == 1)
        chk("erc_gate: an allow line without a reason is ignored", erc_gate.allow_rules(os.path.join(t, "noallow.txt")) == [])
        open(os.path.join(t, "erc-allow.txt"), "w").write("pin_not_connected\npower_pin_not_driven|+3V3   # gated rail\n"); chk("erc_gate: only the reasoned line is a rule", erc_gate.allow_rules(os.path.join(t, "erc-allow.txt")) == [("power_pin_not_driven", "+3V3", "gated rail")])
        d = os.path.join(t, "deliv2"); os.makedirs(d); fails, lines = verify_deliverable.check_dir(d, "x", 4); chk("verify_deliverable: an empty folder fails every item", len(fails) >= len(verify_deliverable.ITEMS))
    except ImportError as e: chk("hardset, erc_gate and verify_deliverable importable (%s)" % e, False)
    open(os.path.join(t, "stub.log"), "w").write("Traceback (most recent call last):\n"); chk("stub router traceback is a tool crash", judge_finish(os.path.join(t, "fin.log"), os.path.join(t, "flag"), os.path.join(t, "stub.log"), os.path.join(t, "deliv"))[0] == "TOOL_CRASH")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        import bench_compare
        base = {"vias_router": 100, "length_mm": 1000.0, "tracks": 500, "hard": 0, "unrouted": 0}
        same = dict(base, hard_types_checked=len(hardset.HARD_POST), connections=300, pairs_over_1mm=0)
        v, note, q = bench_compare.compare(base, same); chk("board compared with itself is MET with Q 1.0", v == "MET" and abs(q - 1.0) < 1e-9)
        v, note, q = bench_compare.compare(base, dict(same, unrouted=1)); chk("a deleted track (one open) is INELIGIBLE, not ranked", v == "INELIGIBLE" and q is None)
        v, note, q = bench_compare.compare(base, dict(same, vias_router=110)); chk("router vias +10 percent is a REGRESSION", v == "REGRESSION")
        v, note, q = bench_compare.compare(base, dict(same, pairs_over_1mm=2)); chk("a pair over 1 mm is a REGRESSION", v == "REGRESSION")
        v, note, q = bench_compare.compare(base, dict(same, vias_router=80, length_mm=950.0, tracks=450)); chk("fewer vias, shorter, fewer segments is MET with Q under 1", v == "MET" and q < 1.0)
        v, note, q = bench_compare.compare(base, {"hard": None, "unrouted": None}); chk("metrics without DRC numbers are UNMEASURABLE", v == "UNMEASURABLE")
    except ImportError as e: chk("bench_compare importable", False)
    # 10 September 2026, the three predicates the red teams' P0 findings owe (C1, C3, the deliverable hole)
    tools_dir = os.path.dirname(os.path.abspath(__file__))
    strays = []
    # Every text file, not only Python: the six-type tuple had survived in 27 shell scripts while this predicate passed
    # (10 September 2026, both round-two red teams C1).
    for fn in sorted(glob.glob(os.path.join(tools_dir, "*.py")) + glob.glob(os.path.join(tools_dir, "*.sh"))):
        if os.path.basename(fn) in ("hardset.py",): continue
        for i, line in enumerate(open(fn, errors="replace"), 1):
            _q = sum(1 for _t in hardset.DRIFT_MARKERS if ('"%s"' % _t) in line or ("'%s'" % _t) in line)   # the names come from
            # the policy itself (or this predicate would be the second definition); quoted, so prose does not trip it
            if _q >= 2 and "hardset" not in line and not line.lstrip().startswith("#") and not re.search(r"drift-ok:\s*\S", line):
                strays.append("%s:%d" % (os.path.basename(fn), i))
    chk("one hard set: no second definition of the DRC policy in the tools (%s)" % (", ".join(strays[:4]) or "none"), not strays)
    d2 = os.path.join(t, "deliv3"); os.makedirs(d2); open(os.path.join(d2, "x-gerbers.zip"), "w").write("z")
    fl = os.path.join(t, "clean.txt"); open(fl, "w").write("clean\n")
    fg = os.path.join(t, "finish-nogate.log"); open(fg, "w").write("contracts: ALL PASS\nrouted-board gate: hard 0 unrouted 0\n")
    chk("a finish that never read the deliverable back is refused", judge_finish(fg, fl, None, d2)[0] == "FINISH_REFUSED")
    open(fg, "a").write("verify_deliverable: ALL PASS\n")
    chk("a finish that did read it back passes", judge_finish(fg, fl, None, d2)[0] == "CLEAN")
    chk("a supervisor failure is not a routing remedy", remedy("INFRA_FAIL", {"route": {}}, set())[0] is None)
    try:
        import bench_compare as _bc2
        base_all = json.load(open(os.path.join(tools_dir, "routeflow", "bench", "baseline.json")))
        chk("the baseline is keyed by board, not phase (%s)" % ", ".join(sorted(base_all)), all(len(k) <= 2 for k in base_all) and _bc2.board_key("pcb-b-compute-b19/pcb-b-compute.kicad_pcb") == "B")
    except Exception as e: chk("baseline readable and keyed by board (%s)" % e, False)
    # Stage 0c (11 September 2026): a journal row must name the bytes it is about, and must say nothing when
    # there are no bytes. A row that carried a board name and no hash was the shape that made two runs of one
    # profile indistinguishable in the record.
    jp = os.path.join(t, "proj"); os.makedirs(os.path.join(jp, "out"))
    journal(jp, dict(board="brd", stage="pre", status="GENERATING"))
    row = json.loads(open(os.path.join(jp, "out", "routeflow", "journal.jsonl")).read().splitlines()[-1])
    chk("a row about a board that does not exist yet claims no hash", row.get("boards") == {})
    open(os.path.join(jp, "brd.kicad_pcb"), "wb").write(b"(kicad_pcb)")
    journal(jp, dict(board="brd", stage="route", status="ROUTING"))
    row2 = json.loads(open(os.path.join(jp, "out", "routeflow", "journal.jsonl")).read().splitlines()[-1])
    chk("a row names the board file it acted on", list(row2.get("boards", {})) == ["brd.kicad_pcb"] and len(row2["boards"]["brd.kicad_pcb"]) == 16)
    open(os.path.join(jp, "brd.kicad_pcb"), "wb").write(b"(kicad_pcb changed)")
    journal(jp, dict(board="brd", stage="finish", status="CLEAN"))
    row3 = json.loads(open(os.path.join(jp, "out", "routeflow", "journal.jsonl")).read().splitlines()[-1])
    chk("a changed board changes the hash on the next row", row3["boards"]["brd.kicad_pcb"] != row2["boards"]["brd.kicad_pcb"])
    # The journal is a chained ledger: a row edited after the fact must fail the walk (11 September 2026).
    jl = os.path.join(jp, "out", "routeflow", "journal.jsonl")
    ok_, n_, probs_ = ledger.verify(jl)
    chk("the journal chain verifies (%d rows)" % n_, ok_ and n_ == 3)
    _rows = [json.loads(l) for l in open(jl) if l.strip()]
    _rows[1]["status"] = "CLEAN"
    open(jl, "w").write("\n".join(json.dumps(r, sort_keys=True) for r in _rows) + "\n")
    ok2_, _n, probs2_ = ledger.verify(jl)
    chk("a journal row edited after the fact is caught", (not ok2_) and any("content changed" in x for x in probs2_))
    shutil.rmtree(t, ignore_errors=True); ok = sum(1 for _, c in res if c)
    print("selftest: %d of %d predicates block on empty input as required" % (ok, len(res))); return 0 if ok == len(res) else 1

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    if a[0] == "preflight": sys.exit(preflight(a[a.index("--repo") + 1] if "--repo" in a else os.getcwd()))
    if a[0] == "selftest": sys.exit(selftest())
    if a[0] == "status": sys.exit(status(a[1], "--markdown" in a))
    if a[0] == "validate": sys.exit(validate(a[1], a[a.index("--repo") + 1] if "--repo" in a else None))
    if a[0] == "run": sys.exit(run(a[1], int(a[a.index("--rounds") + 1]) if "--rounds" in a else 2, "--no-services" not in a, "--dry-run" in a))
    if a[0] == "experiment": sys.exit(experiment(a[1], float(a[a.index("--budget-hours") + 1]) if "--budget-hours" in a else 6.0, "--no-services" not in a, int(a[a.index("--parallel") + 1]) if "--parallel" in a else 1))
    print(__doc__); sys.exit(2)
