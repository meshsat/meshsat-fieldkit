#!/usr/bin/env python3
"""The one verdict writer (MESHSAT-862, 10 September 2026; round-two red teams, and the estate's own pattern).

Every gate in this pipeline decided something and said so on stdout, and every driver read that decision with `grep`. Fifteen
gates, zero machine-readable verdicts, flag files rewritten ten times per finish, and a board gate run twice because nothing
could be asked twice cheaply. That is the channel the two red teams call untrustworthy, and it is the one an agent would have
to read.

Four sibling projects on this estate arrived at the same shape before us, each pairing the rule with the thing that enforces
it (finops-agora's constitution calls that the omoikane pattern: "an invariant survives only when a script or a CHECK guards
it"). What they agree on, and what this module is:

  * ONE writer per verdict. finops-agora: "only verdict.py/scalper_eod.py write verdicts"; logos: "the SOLE writer of
    verdicts"; Territory Grounder: "the acting agent has NO write path to its own outcome verdict". Here: a tool writes its
    own verdict and no other tool's, and the thing that proposes a change never writes the verdict on it.
  * THREE values, not two. PASS, FAIL and INCONCLUSIVE, because a bar that was skipped is not a bar that held. TG's eval gate
    states the invariant this module copies: `ok` is true for PASS and for nothing else, and there is never a truthy spelling
    of INCONCLUSIVE.
  * THE DENOMINATOR TRAVELS WITH THE VERDICT, always, including at zero. "0 of 3,383 is evidence; 0 alone is what a broken
    query, an unwired store and a healthy system all produce identically."
  * THE EXIT CODE IS THE VERDICT. 0 PASS, 1 FAIL, 3 INCONCLUSIVE, 2 for a usage or tooling error. No caller greps.

Usage from a gate:

    import verdict
    ...
    return verdict.write("check_pcb_b", verdict.PASS if not fails else verdict.FAIL,
                         counts={"fail": len(fails), "checked": n}, denominator=n,
                         evidence=fails[:20], inputs={"board": board_path})

`write()` returns the exit code, so `sys.exit(verdict.write(...))` is the whole contract.

Usage from a driver, in place of a grep:

    verdict.py read out/check_pcb_b.verdict.json     -> prints one line, exits with that verdict's code
"""
import sys, os, json, time, hashlib, subprocess

PASS, FAIL, INCONCLUSIVE = "PASS", "FAIL", "INCONCLUSIVE"
CODE = {PASS: 0, FAIL: 1, INCONCLUSIVE: 3}
USAGE = 2


def sha256_file(path, n=16):
    """A short content hash of an input, so a verdict names the thing it judged rather than a filename that moved on."""
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
        return h.hexdigest()[:n]
    except Exception:
        return None


def _version():
    """The tools tree's git sha, so a verdict says which code produced it. Unknown is written as unknown, never omitted."""
    try:
        d = os.path.dirname(os.path.abspath(__file__))
        r = subprocess.run(["git", "-C", d, "rev-parse", "--short=12", "HEAD"], capture_output=True, text=True, timeout=15)
        sha = r.stdout.strip() if r.returncode == 0 else ""
        dirty = subprocess.run(["git", "-C", d, "status", "--porcelain", "--", d], capture_output=True, text=True, timeout=15).stdout.strip()
        return (sha or "unknown") + ("+dirty" if dirty else "")
    except Exception:
        return "unknown"


def write(tool, result, counts=None, denominator=None, evidence=None, inputs=None, note="", out_dir=None, quiet=False):
    """Write out/<tool>.verdict.json and return the exit code that equals the verdict.

    `result` must be PASS, FAIL or INCONCLUSIVE; anything else is a usage error, because a verdict this module does not
    recognise must not resolve to a pass by falling through."""
    if result not in CODE:
        print("verdict: %s reported %r, which is not a verdict" % (tool, result)); return USAGE
    # `out` beside the board is the house default; a driver that runs a gate from elsewhere sets VERDICT_DIR
    # rather than teaching every gate an argument it would otherwise never take.
    out_dir = out_dir or os.environ.get("VERDICT_DIR") or "out"
    rec = {
        "tool": tool,
        "version": _version(),
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": result,
        "counts": dict(counts or {}),
        "denominator": denominator,
        "inputs": dict(inputs or {}),
        "evidence": list(evidence or [])[:50],
        "note": note,
    }
    # An input given as a path is recorded by its hash as well as its name: the verdict then names the bytes it judged.
    for k, v in list(rec["inputs"].items()):
        if isinstance(v, str) and os.path.exists(v):
            rec["inputs"][k] = {"path": v, "sha256_16": sha256_file(v)}
    try:
        os.makedirs(out_dir, exist_ok=True)
        tmp = os.path.join(out_dir, "%s.verdict.json.part" % tool)
        with open(tmp, "w") as f: json.dump(rec, f, indent=1, sort_keys=True)
        os.replace(tmp, os.path.join(out_dir, "%s.verdict.json" % tool))   # atomic: a reader never sees a half-written verdict
    except Exception as e:
        print("verdict: %s could not write its verdict (%s)" % (tool, e)); return USAGE
    if not quiet:
        d = "" if denominator is None else " of %s" % denominator
        c = (" " + json.dumps(rec["counts"], sort_keys=True)) if rec["counts"] else ""
        print("verdict: %-22s %-12s%s%s%s" % (tool, result, d, c, (" | " + note) if note else ""))
    return CODE[result]


def read(path):
    """Read a verdict back. A missing or unparseable verdict is INCONCLUSIVE, never a pass."""
    try:
        rec = json.load(open(path))
    except Exception as e:
        return {"tool": os.path.basename(path), "verdict": INCONCLUSIVE, "note": "unreadable verdict (%s)" % e}, CODE[INCONCLUSIVE]
    v = rec.get("verdict")
    if v not in CODE:
        rec["note"] = "verdict field is %r, which is not a verdict" % v
        return rec, CODE[INCONCLUSIVE]
    return rec, CODE[v]


def collect(out_dir="out", require=(), since=None):
    """Every verdict in a directory, and the worst of them (MESHSAT-862, 11 September 2026).

    There was no collector. `kb_confidence.py` aggregates five gates from a hardcoded list and nothing does it for the
    other nineteen, so no caller could ask "did every gate that ran on this board pass" without knowing the answer's
    shape in advance. Two rules make the answer mean something:

      * a REQUIRED verdict that is absent is INCONCLUSIVE, not missing-and-ignored. A gate that did not run is the
        case this pipeline keeps mistaking for a gate that passed.
      * the worst verdict wins, and INCONCLUSIVE is worse than PASS. There is no truthy spelling of INCONCLUSIVE.

    `since` is a horizon: a UTC timestamp in the form verdict.now() writes, and any verdict older than it is
    ignored. Verdict files live in the board's out/ directory across stages and rounds, so without a horizon a
    stage is judged partly by files an EARLIER stage wrote. On 11 September 2026 board E's second pre-route was
    blocked by a check_contracts verdict its first round's FINISH had written, which is a judgement about a
    different moment and a different question. A verdict with no timestamp is kept, because dropping it would
    turn an unreadable record into a silent pass.

    Returns (worst_code, {tool: record}, [missing tools]).
    """
    found = {}
    try: names = sorted(os.listdir(out_dir))
    except Exception: names = []
    for fn in names:
        if not fn.endswith(".verdict.json"): continue
        rec, _code = read(os.path.join(out_dir, fn))
        if since and rec.get("ts") and rec["ts"] < since: continue
        found[rec.get("tool") or fn[:-len(".verdict.json")]] = rec
    missing = [t for t in require if t not in found]
    # No verdicts at all is not "everything passed": it is a directory nothing wrote to, which is what an
    # unrun chain, a wrong out_dir and a healthy board all produce identically. Found by a reviewer reading
    # this against the rule it was written to enforce, 11 September 2026.
    if not found: return CODE[INCONCLUSIVE], found, missing
    worst = 0
    for rec in found.values(): worst = max(worst, CODE.get(rec.get("verdict"), CODE[INCONCLUSIVE]))
    if missing: worst = max(worst, CODE[INCONCLUSIVE])
    return worst, found, missing


def main(a):
    if len(a) >= 2 and a[0] == "collect":
        req = tuple(x for x in (a[a.index("--require") + 1].split(",") if "--require" in a else []) if x)
        worst, found, missing = collect(a[1], req)
        for t, rec in sorted(found.items()):
            d = "" if rec.get("denominator") is None else " of %s" % rec["denominator"]
            print("verdict: %-24s %-12s%s%s" % (t, rec.get("verdict"), d, (" | " + rec["note"]) if rec.get("note") else ""))
        for t in missing: print("verdict: %-24s %-12s did not run, and a gate that did not run is not a gate that passed" % (t, INCONCLUSIVE))
        print("verdict: %d verdict(s) in %s, %d required and absent; worst %s"
              % (len(found), a[1], len(missing), {v: k for k, v in CODE.items()}.get(worst, "PASS")))
        return worst
    if len(a) == 2 and a[0] == "read":
        rec, code = read(a[1])
        d = "" if rec.get("denominator") is None else " of %s" % rec["denominator"]
        print("verdict: %-22s %-12s%s%s" % (rec.get("tool", "?"), rec.get("verdict"), d, (" | " + rec["note"]) if rec.get("note") else ""))
        return code
    print(__doc__); return USAGE


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
