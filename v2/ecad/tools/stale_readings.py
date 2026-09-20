#!/usr/bin/env python3
"""Which readings in this tree were taken under a tool that has changed since (a report, 20 September 2026).

THE GAP THIS CLOSES, and it cost nineteen hours. Since 17 September staleness is asked RULE BY RULE, from the
per-rule digests a verdict carries, and that catches a change to `pcb_rules.yaml`. It cannot catch a change to
the TOOL, because a tool change moves no fingerprint: `check_pcb_b` was corrected on 19 September to REPORT a
half-routed pair rather than fail it, board B's MEC-001 went on reading FAIL on 21 of them until 20 September
08:04, and nothing on any page could say the reading predated the fix. The rule-set fingerprint was current,
the per-rule digests were current, and the reading was nineteen hours out of date.

IT ANNOUNCES AND IT DECIDES NOTHING, deliberately. A tool change is not evidence about a board: it says a
reading is owed, not that it would come out differently, and the only honest answer is to re-take it
(`retake_gate.sh`, or the board's own chain). Turning this into a gate would refuse boards for the age of
their paperwork.

TWO INSTRUMENTS, AND THE WEAKER ONE SAYS SO. A verdict written since 20 September carries `writer`, the FILE
that wrote it and that file's own content hash, so the question is a comparison and the answer is exact.
Every verdict written before that carries no such field, so the fallback compares the verdict's timestamp
with the deciding tool's last COMMIT DATE, which is a proxy: it is right about the order of events and says
nothing about whether the change touched what this reading measures. Each row is labelled with which
instrument answered it.

Usage: stale_readings.py [<dir> ...] [--json]     (default: every project directory of this tree)
"""
import os, sys, json, glob, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import verdict as _v

_COMMIT_CACHE = {}


def tool_last_change(path):
    """The last commit date of a tool file, as an ISO string, or None when git cannot say."""
    if path in _COMMIT_CACHE: return _COMMIT_CACHE[path]
    out = None
    try:
        r = subprocess.run(["git", "-C", HERE, "log", "-1", "--format=%cI", "--", path],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip(): out = r.stdout.strip()
    except Exception:
        pass
    _COMMIT_CACHE[path] = out
    return out


def file_sha16(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except Exception:
        return None


def judge_one(rec):
    """(state, said) for one verdict record: 'STALE', 'CURRENT', or 'UNKNOWN' with the reason."""
    w = rec.get("writer") or {}
    name, sha = w.get("file") or "", w.get("sha16") or ""
    if name and sha:
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            return "UNKNOWN", "the file that wrote it, %s, is not in this tools directory" % name
        now = file_sha16(p)
        if now is None:
            return "UNKNOWN", "%s could not be read" % name
        if now == sha:
            return "CURRENT", "%s is byte for byte the file that wrote it" % name
        return "STALE", "%s has changed since this reading (wrote %s, now %s)" % (name, sha, now)
    # the proxy, for every verdict written before the writer field existed
    tool = str(rec.get("tool") or "")
    cand = os.path.join(HERE, tool + ".py")
    if not os.path.exists(cand):
        # A PER-BOARD LABEL NAMES A SHARED TOOL. `final_gate_b` and `jlc_certify_b` are one file each, written
        # once per board under the board's own name, and the suffix is stripped ONLY when the letter is one
        # this project has and the stripped file really exists, so nothing is guessed into being answerable.
        head, _, suf = tool.rpartition("_")
        if head and suf in ("a", "b", "c", "d", "e", "e5", "p") and os.path.exists(os.path.join(HERE, head + ".py")):
            tool, cand = head, os.path.join(HERE, head + ".py")
    if not os.path.exists(cand):
        return "UNKNOWN", ("this reading names no writer and no tools/%s.py exists, so the deciding file "
                           "cannot be named" % tool)
    when, ts = tool_last_change(cand), str(rec.get("ts") or "")
    if not when or not ts:
        return "UNKNOWN", "no commit date for %s.py or no timestamp on the reading" % tool
    if ts < when[:len(ts)] or (ts[:19] < when[:19]):
        return "STALE", ("BY PROXY: %s.py was last changed %s and this reading was taken %s, so the reading "
                         "predates the change; whether the change touched what it measures is not said"
                         % (tool, when[:19], ts[:19]))
    return "CURRENT", "BY PROXY: %s.py has not changed since this reading was taken" % tool


def scan(dirs):
    rows = []
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "**", "*.verdict.json"), recursive=True)):
            try:
                rec = json.load(open(p, encoding="utf-8"))
            except Exception as e:
                rows.append((p, "UNKNOWN", "unreadable: %s" % e, None)); continue
            state, said = judge_one(rec)
            rows.append((p, state, said, rec.get("tool")))
    return rows


def open_pair_rows(res=None):
    """THE QUESTION THAT FOUND THE NINETEEN-HOUR READING, asked mechanically (20 September 2026).

    535 readings taken under a changed tool is a list, not a work item, and the proxy over-counts anyway: a
    tool file moves for a comment as readily as for a criterion. The readings that MATTER are the ones
    deciding a pair that is still open, and `open_pairs.collect` already carries each pair's evidence PATH.
    So the register is asked of itself: of the pairs still open, which are decided by a reading taken under a
    tool that has changed since. That is the question that was asked by hand at 08:04 and found board B's
    MEC-001 nineteen hours out of date."""
    if res is None:
        try:
            import open_pairs
            res = open_pairs.collect()
        except Exception as e:
            print("stale_readings: the open-pair register could not be read (%s)" % e); return None
    seen, rows = {}, []
    for pr in res.get("pairs") or []:
        ev = pr.get("evidence")
        if not ev or not os.path.exists(ev): continue
        if ev not in seen:
            try: seen[ev] = judge_one(json.load(open(ev, encoding="utf-8")))
            except Exception as e: seen[ev] = ("UNKNOWN", "unreadable: %s" % e)
        st, said = seen[ev]
        rows.append((pr.get("board"), pr.get("rule"), pr.get("result"), pr.get("category"), st, said, ev))
    return rows


def main(argv):
    if "--open-pairs" in argv:
        rows = open_pair_rows()
        if rows is None: return _v.INCONCLUSIVE
        stale = [r for r in rows if r[4] == "STALE"]
        print("stale_readings: %d open pair(s) with a reading beside them; %d are decided by a reading taken "
              "under a tool that has changed since" % (len(rows), len(stale)))
        for b, rule, res_, cat, _st, said, ev in sorted(stale):
            print("  %-3s %-9s %-13s %-18s %s" % (b, rule, res_, cat, said[:104]))
        return _v.write("stale_readings", _v.PASS, counts={"pairs": len(rows), "stale": len(stale)},
                        denominator=len(rows), advisory=True,
                        evidence=["%s %s %s: %s" % (b, r, res_, said[:110]) for b, r, res_, _c, _s, said, _e in stale][:20],
                        note="open pairs whose deciding reading was taken under a tool that has changed since; "
                             "a REPORT, because a tool change says a reading is OWED and not that it would "
                             "come out differently")
    dirs = [a for a in argv if not a.startswith("--")]
    if not dirs:
        dirs = [d for d in sorted(glob.glob(os.path.join(ECAD, "pcb-*"))) if os.path.isdir(d)]
        dirs += [os.path.join(ECAD, "out")]
    rows = scan([d for d in dirs if os.path.isdir(d)])
    stale = [r for r in rows if r[1] == "STALE"]
    unknown = [r for r in rows if r[1] == "UNKNOWN"]
    print("stale_readings: %d reading(s); %d taken under a tool that has changed since, %d that cannot be asked"
          % (len(rows), len(stale), len(unknown)))
    # GROUPED BY TOOL, because 311 rows is a list and not a work item. The exact instrument is named per group:
    # an EXACT row was answered by the writer's own hash and a PROXY row by the tool's last commit date, which
    # is right about the order of events and silent about whether the change touched this measurement.
    want = set((_v.opt(argv, "--tools", "") or "").split(",")) - {""}
    by_tool = {}
    for pth, _s, said, tool in stale:
        k = tool or "?"
        if want and k not in want: continue
        g = by_tool.setdefault(k, {"n": 0, "exact": 0, "paths": [], "said": said})
        g["n"] += 1; g["paths"].append(os.path.relpath(pth, ECAD))
        if not said.startswith("BY PROXY"): g["exact"] += 1
    for k in sorted(by_tool, key=lambda k: -by_tool[k]["n"]):
        g = by_tool[k]
        print("  %-26s %2d reading(s)%s   %s" % (k, g["n"],
              (" (%d answered exactly)" % g["exact"]) if g["exact"] else " (all by proxy)", g["said"][:96]))
        if "--rows" in argv or want:
            for q in g["paths"]: print("        %s" % q)
    if "--verbose" in argv:
        for p, _s, said, tool in unknown:
            print("  UNKNOWN %-26s %s" % (tool or "?", said))
    if "--json" in argv:
        print(json.dumps([{"path": p, "state": s, "why": w, "tool": t} for p, s, w, t in rows], indent=1))
    # IT DECIDES NOTHING: the verdict is advisory and PASS whatever it found, because a tool change is not
    # evidence about a board and a gate that refused one for the age of its paperwork would be wrong.
    return _v.write("stale_readings", _v.PASS, counts={"readings": len(rows), "stale": len(stale),
                    "not_asked": len(unknown)}, denominator=len(rows), advisory=True,
                    evidence=["%s: %s" % (t or "?", w) for _p, _s, w, t in stale][:20],
                    note="readings taken under a tool that has changed since; a REPORT, because a tool change "
                         "says a reading is OWED and not that it would come out differently")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
