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

THREE INSTRUMENTS, AND THE WEAKER ONES SAY SO (26 September 2026, the review's finding D2). A verdict written since
that day carries `code_bundle`: the entry script and EVERY LOCAL MODULE it imported, transitively, each by its content
hash (verdict.code_bundle), so the question is a comparison and the answer is exact, including for a helper module the
entry script never changed. A verdict written from 20 September carries only `writer`, the entry file and its hash:
the entry is compared exactly and the modules it imports TODAY by their last COMMIT DATE against the reading. Every
verdict written before that carries neither, so the whole bundle is compared by commit date. A commit date is a proxy:
it is right about the order of events and says nothing about whether the change touched what this reading measures,
and a file that cannot be dated (uncommitted, untracked) counts as changed. Each row is labelled with which instrument
answered it.

Usage: stale_readings.py [<dir> ...] [--json]     (default: every project directory of this tree)
"""
import os, sys, json, glob, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import verdict as _v

_COMMIT_CACHE = {}
_DIRTY_CACHE = {}


def tool_last_change(path):
    """The last commit date of a tool file, as an ISO string, or None when git cannot say."""
    if path in _COMMIT_CACHE: return _COMMIT_CACHE[path]
    out = None
    try:
        r = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(path)), "log", "-1", "--format=%cI", "--",
                            os.path.basename(path)], capture_output=True, text=True, timeout=20)
        if r.returncode == 0 and r.stdout.strip(): out = r.stdout.strip()
    except Exception:
        pass
    _COMMIT_CACHE[path] = out
    return out


def _dirty(path):
    """True when this checkout's copy of `path` is not the version its last commit holds (modified or untracked)."""
    if path in _DIRTY_CACHE: return _DIRTY_CACHE[path]
    d = False
    try:
        r = subprocess.run(["git", "-C", os.path.dirname(os.path.abspath(path)), "status", "--porcelain", "--",
                            os.path.basename(path)], capture_output=True, text=True, timeout=20)
        d = r.returncode == 0 and bool(r.stdout.strip())
    except Exception:
        pass
    _DIRTY_CACHE[path] = d
    return d


def _instant(s):
    """One instant from a verdict's UTC stamp (`...Z`) or git's offset form. THE TWO WERE COMPARED AS TEXT until 26
    September 2026, which put a reading taken at 21:00Z after a commit at 22:52+02:00 (20:52Z) on the wrong side of it:
    `rules_status._instant` learnt this on 16 September and this report had not."""
    import datetime as _dt
    t = (s or "").strip().replace("Z", "+00:00")
    try: d = _dt.datetime.fromisoformat(t)
    except ValueError:
        try: d = _dt.datetime.fromisoformat(t[:19])
        except ValueError: return None
    if d.tzinfo is None: d = d.replace(tzinfo=_dt.timezone.utc)
    return d


def file_sha16(path):
    try:
        return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]
    except Exception:
        return None


def _after(paths, ts, root):
    """[(relative path, why)] of the files in `paths` that cannot be shown to predate the reading taken at `ts`: last
    committed after it, or not datable at all (uncommitted edits, untracked, no commit)."""
    t = _instant(ts)
    out = []
    for p in sorted(paths):
        rel = os.path.relpath(p, root)
        if _dirty(p):
            out.append((rel, "uncommitted in this checkout, so it cannot be dated")); continue
        when = tool_last_change(p)
        if not when:
            out.append((rel, "no commit holds it, so it cannot be dated")); continue
        w = _instant(when)
        if t is None or w is None:
            out.append((rel, "its date or the reading's cannot be read")); continue
        if w > t:
            import datetime as _dt
            out.append((rel, "last committed %s" % w.astimezone(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")))
    return out


def _resolve_tool(tool, root):
    """The tools file a reading's label names: `<tool>.py`, or a per-board label of a shared tool (`final_gate_b`)."""
    cand = os.path.join(root, tool + ".py")
    if not os.path.exists(cand):
        # A PER-BOARD LABEL NAMES A SHARED TOOL. `final_gate_b` and `jlc_certify_b` are one file each, written
        # once per board under the board's own name, and the suffix is stripped ONLY when the letter is one
        # this project has and the stripped file really exists, so nothing is guessed into being answerable.
        head, _, suf = tool.rpartition("_")
        if head and suf in ("a", "b", "c", "d", "e", "e5", "p") and os.path.exists(os.path.join(root, head + ".py")):
            tool, cand = head, os.path.join(root, head + ".py")
    return tool, cand


def judge_detail(rec, root=None, bundle=True):
    """{state, said, instrument, changed, then, now} for one verdict record. `state` is STALE, CURRENT or UNKNOWN.

    THREE INSTRUMENTS, AND EACH ROW SAYS WHICH ANSWERED IT (26 September 2026; the review's finding D2):
      EXACT_BUNDLE   the reading carries `code_bundle`: its entry script and every local module it imported, each by
                     sha256/16. The bundle is rebuilt here from the same entry and compared; any file that differs,
                     appeared or went is named. A helper module changed since the reading makes it STALE.
      WRITER+PROXY   the reading carries `writer` (20 September onward) and no bundle: the entry script is compared
                     exactly, and every other file of the entry's bundle AS IT IS NOW is compared by its last commit
                     date with the reading (conservative: a file that cannot be dated counts as changed).
      PROXY          the reading carries neither: the deciding tool's whole bundle by commit date.
    `bundle=False` is the entry-only instrument this report used until that day (the writer's hash, else the tool file's
    commit date); rules_status asks it only to say which readings changed class when the bundle arrived."""
    root = os.path.abspath(root or HERE)
    ts = str(rec.get("ts") or "")
    w = rec.get("writer") or {}
    name, sha = w.get("file") or "", w.get("sha16") or ""
    cb = rec.get("code_bundle") or {}

    def res(state, said, inst, changed=(), then=None, now=None):
        return {"state": state, "said": said, "instrument": inst, "changed": list(changed), "then": then, "now": now}
    if bundle and cb.get("sha16") and cb.get("entry"):
        entry = cb["entry"] if os.path.isabs(cb["entry"]) else os.path.join(root, cb["entry"])
        if not os.path.exists(entry):
            return res("UNKNOWN", "the entry script of its code bundle, %s, is not in this tools directory" % cb["entry"], "EXACT_BUNDLE")
        now = _v.code_bundle(entry, root)
        if now.get("sha16") == cb["sha16"]:
            return res("CURRENT", "the code bundle of %s (%d file(s)) is byte for byte the one that wrote it"
                       % (cb["entry"], len(now.get("files") or {})), "EXACT_BUNDLE", then=cb["sha16"], now=now["sha16"])
        a, b = cb.get("files") or {}, now.get("files") or {}
        changed = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        what = ", ".join(("%s (%s)" % (k, "new" if k not in a else "gone" if k not in b else "changed")) for k in changed[:6])
        return res("STALE", "the code bundle of %s has changed since this reading (wrote %s, now %s): %s%s"
                   % (cb["entry"], cb["sha16"], now.get("sha16") or "none", what,
                      "" if len(changed) <= 6 else " and %d more" % (len(changed) - 6)),
                   "EXACT_BUNDLE", changed, cb["sha16"], now.get("sha16"))
    if name and sha:
        p = os.path.join(root, name)
        if not os.path.exists(p):
            return res("UNKNOWN", "the file that wrote it, %s, is not in this tools directory" % name, "EXACT_WRITER")
        now16 = file_sha16(p)
        if now16 is None:
            return res("UNKNOWN", "%s could not be read" % name, "EXACT_WRITER")
        nb = _v.code_bundle(p, root) if bundle else {}
        if now16 != sha:
            return res("STALE", "%s has changed since this reading (wrote %s, now %s)" % (name, sha, now16),
                       "EXACT_WRITER", [name], sha, nb.get("sha16") if bundle else now16)
        if not bundle:
            return res("CURRENT", "%s is byte for byte the file that wrote it" % name, "EXACT_WRITER", then=sha, now=now16)
        helpers = [os.path.join(root, k) if not os.path.isabs(k) else k for k in (nb.get("files") or {}) if k != nb.get("entry")]
        late = _after(helpers, ts, root)
        if late:
            return res("STALE", ("BY PROXY FOR ITS HELPERS: %s is byte for byte the file that wrote it, and %d module(s) it "
                                 "imports cannot be shown to predate the reading (%s): %s; whether a change touched what "
                                 "it measures is not said" % (name, len(late), ts[:19] + "Z", "; ".join(
                                     "%s %s" % (r, why) for r, why in late[:5]) + ("" if len(late) <= 5 else "; and %d more" % (len(late) - 5)))),
                       "WRITER+PROXY", [r for r, _w in late], sha, nb.get("sha16"))
        return res("CURRENT", "%s is byte for byte the file that wrote it, and every module it imports was last committed "
                   "before the reading (BY PROXY for the helpers)" % name, "WRITER+PROXY", then=sha, now=nb.get("sha16"))
    # the proxy, for every verdict written before the writer field existed
    tool, cand = _resolve_tool(str(rec.get("tool") or ""), root)
    if not os.path.exists(cand):
        return res("UNKNOWN", ("this reading names no writer and no tools/%s.py exists, so the deciding file "
                               "cannot be named" % tool), "PROXY")
    if not ts:
        return res("UNKNOWN", "no timestamp on the reading", "PROXY")
    paths = [cand]
    if bundle:
        nb = _v.code_bundle(cand, root)
        paths = [os.path.join(root, k) if not os.path.isabs(k) else k for k in (nb.get("files") or {})] or [cand]
    late = _after(paths, ts, root)
    if late:
        return res("STALE", ("BY PROXY: %s.py%s cannot be shown to predate this reading (%s): %s; whether the change "
                             "touched what it measures is not said" % (tool, " or a module it imports" if bundle else "",
                                                                      ts[:19] + "Z", "; ".join("%s %s" % (r, why) for r, why in late[:5])
                                                                      + ("" if len(late) <= 5 else "; and %d more" % (len(late) - 5)))),
                   "PROXY", [r for r, _w in late])
    return res("CURRENT", "BY PROXY: %s.py%s has not changed since this reading was taken"
               % (tool, " and every module it imports" if bundle else ""), "PROXY")


def judge_one(rec, root=None, bundle=True):
    """(state, said) for one verdict record: 'STALE', 'CURRENT', or 'UNKNOWN' with the reason. See `judge_detail`."""
    d = judge_detail(rec, root, bundle)
    return d["state"], d["said"]


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
                        denominator=len(rows), advisory=True, out_dir=_v.opt(argv, "--out-dir", None),
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
    # `--out-dir` REACHES THE VERDICT (21 September 2026, 07:15 CEST): run from v2/ecad with --out-dir pointed at
    # a scratch directory, the report wrote its verdict into the tree's own out/ all the same, which is the 19
    # September incident's shape (a reading written by hand into this tree's evidence). The flag is honoured now.
    return _v.write("stale_readings", _v.PASS, counts={"readings": len(rows), "stale": len(stale),
                    "not_asked": len(unknown)}, denominator=len(rows), advisory=True,
                    out_dir=_v.opt(argv, "--out-dir", None),
                    evidence=["%s: %s" % (t or "?", w) for _p, _s, w, t in stale][:20],
                    note="readings taken under a tool that has changed since; a REPORT, because a tool change "
                         "says a reading is OWED and not that it would come out differently")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
