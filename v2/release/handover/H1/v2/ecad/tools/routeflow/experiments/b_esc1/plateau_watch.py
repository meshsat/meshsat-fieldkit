#!/usr/bin/env python3
"""plateau_watch.py: the stop rules of the board B escape trial Q-B-ESC-1, enforced rather than written down
(v2/docs/B-FEASIBILITY.md section 7). EXPERIMENTAL.

Usage:
  plateau_watch.py --job-pid PID --ses <work>/S3/route.ses --out <dir> --count-cmd "<command>"
                   [--plateau 3] [--first-pass-max 5400] [--deadline EPOCH] [--stop-file PATH] [--poll 20]

What it watches. route_part.sh runs our Freerouting 1.9.0 build with -Dfreerouting.ses_per_pass=<work>/S3/route.ses,
which rewrites that ONE file after every pass (to <file>.part, then an atomic rename; tools/freerouting/README.md). A
reader that only looks at the end sees the last pass. This watcher polls the file's inode and mtime, copies every new
session to <out>/pass-NNN.ses the moment it appears, and runs --count-cmd on it with {ses} replaced by the copy; the
command prints a line containing "open <N>" (count_open.py does). Every reading goes to <out>/passes.csv.

The stop rules, each one a kill of the job it watches:
  PLATEAU             the last --plateau sessions (default 3) are all at or above the lowest count read before them:
                      three consecutive passes with no fall;
  FIRST_PASS_TIMEOUT  no session within --first-pass-max seconds (default 5400, 90 minutes) of the watcher's start;
  DEADLINE            the wall clock passed --deadline (the trial's box-hour and credit cap, computed by run.sh);
  TRIAL_STOP          --stop-file exists (run.sh writes it when the other arm's result stops the whole trial).
A job that ends by itself (its pass ceiling, its own timeout, or a closed route) is JOB_ENDED; the watcher then reads
the final session if it has not already and exits.

What it kills, and only that: the job's own process and every descendant of it, found by walking /proc parent links
from --job-pid (route_part.sh, its `timeout`, `xvfb-run`, Xvfb and the JVM). GNU timeout runs its child in a process
group of its own, so killing route_part.sh's group would leave the router running; the walk reaches it. SIGTERM
first, SIGKILL after 20 s for anything of the set still alive. No pattern match is used, so nothing another session
started can be hit.

Missed passes: a pass that ends while the previous copy is being counted is overwritten before it is seen. The
watcher records the gap (the session's pass number is not in the file), so the plateau is over observed sessions;
passes.csv says how many were observed. It writes <out>/watch.json with the stop reason and every reading."""
import sys, os, time, json, shutil, signal, subprocess, re


def opt(a, flag, default=None):
    if flag in a:
        i = a.index(flag)
        if i + 1 < len(a):
            return a[i + 1]
    return default


def children_map():
    kids = {}
    for d in os.listdir("/proc"):
        if not d.isdigit():
            continue
        try:
            stat = open("/proc/%s/stat" % d).read()
        except OSError:
            continue
        # the command name is in parentheses and may contain spaces; the ppid is the second field after it
        rest = stat[stat.rfind(")") + 2:].split()
        try:
            ppid = int(rest[1])
        except (IndexError, ValueError):
            continue
        kids.setdefault(ppid, []).append(int(d))
    return kids


def descendants(pid):
    kids = children_map()
    out, stack = [], [pid]
    while stack:
        p = stack.pop()
        for c in kids.get(p, []):
            out.append(c)
            stack.append(c)
    return out


def alive(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    try:
        return open("/proc/%d/stat" % pid).read().split(")")[-1].split()[0] != "Z"
    except OSError:
        return False


def kill_tree(pid, grace=20):
    victims = descendants(pid) + [pid]
    for p in reversed(victims):
        try:
            os.kill(p, signal.SIGTERM)
        except OSError:
            pass
    t = time.time()
    while time.time() - t < grace and any(alive(p) for p in victims):
        time.sleep(1)
    for p in victims:
        if alive(p):
            try:
                os.kill(p, signal.SIGKILL)
            except OSError:
                pass
    return victims


def plateaued(counts, k):
    """True when the last k readings are all at or above the minimum of the readings before them."""
    if len(counts) <= k:
        return False
    before = min(counts[:-k])
    return all(c >= before for c in counts[-k:])


def main(a):
    job = int(opt(a, "--job-pid", "0"))
    ses = opt(a, "--ses"); out = opt(a, "--out"); cmd = opt(a, "--count-cmd")
    k = int(opt(a, "--plateau", "3")); first_max = float(opt(a, "--first-pass-max", "5400"))
    deadline = float(opt(a, "--deadline", "0")); stop_file = opt(a, "--stop-file"); poll = float(opt(a, "--poll", "20"))
    if not (job and ses and out and cmd):
        print(__doc__)
        return 2
    os.makedirs(out, exist_ok=True)
    t0 = time.time(); last = None; counts = []; rows = []; reason = None; killed = []
    csv = open(os.path.join(out, "passes.csv"), "w")
    csv.write("observed,wall_s,ses_bytes,open,count_rc\n"); csv.flush()

    def read_new():
        nonlocal last
        try:
            st = os.stat(ses)
        except OSError:
            return False
        key = (st.st_ino, st.st_mtime_ns, st.st_size)
        if key == last or st.st_size == 0:
            return False
        last = key
        n = len(rows) + 1
        dst = os.path.join(out, "pass-%03d.ses" % n)
        shutil.copyfile(ses, dst)
        r = subprocess.run(cmd.replace("{ses}", dst), shell=True, capture_output=True, text=True)
        m = re.search(r"\bopen (\d+)\b", r.stdout)
        val = int(m.group(1)) if (m and r.returncode == 0) else None
        row = {"observed": n, "wall_s": round(time.time() - t0, 1), "ses_bytes": os.path.getsize(dst), "open": val,
               "count_rc": r.returncode}
        rows.append(row)
        open(os.path.join(out, "pass-%03d.log" % n), "w").write(r.stdout + r.stderr)
        csv.write("%d,%.1f,%d,%s,%d\n" % (n, row["wall_s"], row["ses_bytes"], "" if val is None else val, r.returncode))
        csv.flush()
        if val is not None:
            counts.append(val)
        return True

    while True:
        running = alive(job)
        read_new()
        if not running:
            reason = reason or "JOB_ENDED"
            read_new()
            break
        now = time.time()
        if counts and counts[-1] == 0:
            pass  # a closed route finishes by itself; the caps still bind
        elif plateaued(counts, k):
            reason = "PLATEAU"
        if not rows and now - t0 > first_max:
            reason = "FIRST_PASS_TIMEOUT"
        if deadline and now > deadline:
            reason = "DEADLINE"
        if stop_file and os.path.exists(stop_file):
            reason = "TRIAL_STOP"
        if reason:
            killed = kill_tree(job)
            time.sleep(2)
            read_new()
            break
        time.sleep(poll)
    res = {"label": "EXPERIMENTAL (Q-B-ESC-1)", "stop": reason, "job_pid": job, "killed": killed,
           "observed_sessions": len(rows), "counts": counts, "min_open": min(counts) if counts else None,
           "final_open": counts[-1] if counts else None, "plateau_k": k, "first_pass_max_s": first_max,
           "deadline": deadline, "seconds": round(time.time() - t0, 1), "rows": rows}
    json.dump(res, open(os.path.join(out, "watch.json"), "w"), indent=1)
    print("plateau_watch: stop %s after %d session(s), counts %s" % (reason, len(rows), counts))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
