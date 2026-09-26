#!/usr/bin/env python3
"""besc1_timesplit.py <results dir>: EXPERIMENTAL (Q-B-ESC-1). Splits each arm's job wall time into input load, time
blocked on Freerouting's modal import warning, and active routing, from files filed beside it only, and writes
<results dir>/analysis/time-split.csv plus a per-pass table.

Clock: the box runs UTC and fr.log's timestamps are the box's clock (its first line follows route.log's start by about
one second). Marks used, per arm:
  job start       route.log "start HH:MM:SS" (route_part.sh launching the router under timeout)
  load end        fr.log's last line of the import (the last "[main]" line: the normalization warnings of the DSN reader)
  routing start   fr.log "Starting auto-routing" (the moment the modal warning was dismissed; the journal's operator line
                  records Return sent at 19:47:02)
  pass k          fr.log "session written after pass k"
  job end         a6: route.log "PART-DONE S3 124 HH:MM:SS" (exit 124 is GNU timeout's cap); a8: the watcher's kill, at
                  job start plus the wall_s of its last row in watch/passes.csv (the kill follows that reading).
"""
import sys, os, re, csv, json, datetime as dt

R = sys.argv[1]
DAY = "2026-09-26 "


def t(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")


rows, passes = [], []
for arm in ("a6", "a8"):
    rl = open(os.path.join(R, arm, "route.log")).read()
    start = t(DAY + re.search(r"start (\d\d:\d\d:\d\d)", rl).group(1) + ".000")
    lines = [(t(l[:23]), l[24:]) for l in open(os.path.join(R, arm, "run", "S3", "fr.log")).read().splitlines()
             if re.match(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3} ", l)]
    load_end = [x for x, m in lines if m.startswith("[main]")][-1]
    route0 = [x for x, m in lines if "Starting auto-routing" in m][0]
    sess = [x for x, m in lines if "session written after pass" in m]
    done = re.search(r"PART-DONE S3 (\d+) (\d\d:\d\d:\d\d)", rl)
    if done:
        end = t(DAY + done.group(2) + ".000"); how = "job cap (exit %s)" % done.group(1)
    else:
        last = list(csv.DictReader(open(os.path.join(R, arm, "watch", "passes.csv"))))[-1]
        end = start + dt.timedelta(seconds=float(last["wall_s"]))
        how = "plateau kill by the watcher (%s)" % json.load(open(os.path.join(R, arm, "watch", "watch.json")))["stop"]
    s = lambda a, b: round((b - a).total_seconds(), 1)
    wall = s(start, end)
    rows.append({"arm": arm, "job_start_utc": start.strftime("%H:%M:%S"), "job_end_utc": end.strftime("%H:%M:%S.%f")[:12],
                 "ended_by": how, "job_wall_s": wall,
                 "input_load_s": s(start, load_end), "blocked_on_dialog_s": s(load_end, route0),
                 "active_routing_s": s(route0, end), "completed_passes": len(sess),
                 "active_in_completed_passes_s": s(route0, sess[-1]), "active_after_last_session_lost_s": s(sess[-1], end),
                 "blocked_share_of_wall": round(s(load_end, route0) / wall, 3)})
    prev = route0
    for k, x in enumerate(sess, 1):
        passes.append({"arm": arm, "pass": k, "active_s_at_session": s(route0, x), "pass_s": s(prev, x)})
        prev = x
os.makedirs(os.path.join(R, "analysis"), exist_ok=True)
with open(os.path.join(R, "analysis", "time-split.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
with open(os.path.join(R, "analysis", "pass-times.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(passes[0].keys())); w.writeheader(); w.writerows(passes)
for r in rows:
    print(r)
