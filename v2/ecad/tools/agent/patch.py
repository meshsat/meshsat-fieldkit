#!/usr/bin/env python3
"""Tier 2's third product: a tool change as a branch, never as a file copy (MESHSAT-862, 12 Sep 2026).

The plan's tier 2 produces three things and this is the last of them. The rule it is built around is
the plan's own: **run in a git worktree at a stated sha and never a file copy**, because a change that
is applied into the working tree cannot be told apart from the change someone else is making in it,
and this project has already lost an evening to two sessions editing one tree.

The flow, and every step after the first is mechanical:

  1. tier 2 is given a defect, the evidence for it and the file it lives in, and returns a unified diff
  2. a worktree is cut at a stated sha, in a temporary directory, and the diff is applied THERE
  3. `reserved.py` reads the diff: a reserved line and the whole thing is refused and written up for
     the owner instead
  4. the test suite runs IN THE WORKTREE. A patch that does not keep the suite green is refused, and
     the output of the failure is what goes back to the proposer
  5. tier 2b reviews the diff in a context that never saw it being made
  6. what lands is a BRANCH and a review, never a commit on main. The owner merges or does not

Nothing here writes to the working tree, and the worktree is removed whatever happens.
"""
import os, re, sys, json, time, shutil, argparse, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REPO = subprocess.run(["git", "-C", TOOLS, "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import client, review as reviewmod                                # noqa: E402
import verdict, ledger, reserved                                  # noqa: E402

SYSTEM = """You are tier 2 of a hardware pipeline's control plane, proposing a change to a TOOL.

You are given a defect, the evidence for it, and the relevant source. You return a unified diff and
nothing else. A worktree is cut at a stated commit, your diff is applied there, the never-auto floor
reads it, the test suite runs, and a separate reviewer reads it. You never touch the working tree.

RULES:
  1. Answer with one JSON object: {"diff": "<a unified diff, git apply -p1 clean>", "why": ["..."],
     "test": "<the name of the test that fails before this change and passes after, or the words NEW
     TEST NEEDED>"}
  2. The diff must apply with `git apply -p1` against the stated commit. Use the exact paths given.
  3. SMALL. One defect. A diff that changes three things cannot be reviewed or reverted as one.
  4. A fix ships with the test that proves it. A rule that passes on the tree it was written to fail is
     worse than no rule, so say which test fails before your change.
  5. Never change a number that is an impedance target, a net class width or clearance, a fabrication
     rule, a board minimum, a layer count or a region definition. Those are the owner's. If the fix
     needs one, say so in "why" and return an empty diff.
  6. No em dashes in any comment or string you add."""


def run(cmd, cwd=None, timeout=1800):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def _worktree(sha, tmp):
    """A worktree at a stated sha. Never a copy, never the working tree."""
    wt = os.path.join(tmp, "wt")
    r = run(["git", "-C", REPO, "worktree", "add", "--detach", wt, sha])
    if r.returncode:
        raise client.Infra("could not cut a worktree at %s: %s" % (sha, r.stderr.strip()[:200]))
    return wt


def _cleanup(wt):
    run(["git", "-C", REPO, "worktree", "remove", "--force", wt])
    run(["git", "-C", REPO, "worktree", "prune"])


def try_patch(diff, sha, tmp, test_cmd):
    """Apply, check the floor, run the suite. Returns (ok, report) and leaves nothing behind."""
    report = {}
    wt = _worktree(sha, tmp)
    try:
        dp = os.path.join(tmp, "proposed.diff")
        open(dp, "w").write(diff if diff.endswith("\n") else diff + "\n")
        r = run(["git", "-C", wt, "apply", "-p1", "--whitespace=nowarn", dp])
        report["applies"] = (r.returncode == 0)
        if r.returncode:
            report["apply_error"] = r.stderr.strip()[:1200]
            return False, report
        r = run(["git", "-C", wt, "diff", "-U0"])
        touched = []
        cur = None
        classes = reserved.load()
        for line in r.stdout.splitlines():
            if line.startswith("+++ b/"): cur = line[6:]; continue
            if line[:1] in "+-" and cur and not line.startswith(("+++", "---")):
                for name, why in reserved._matches(cur, line[1:], classes):
                    touched.append({"file": cur, "class": name, "why": why, "line": line[:120]})
        report["reserved"] = touched
        if touched:
            return False, report
        rt = run(test_cmd, cwd=wt, timeout=2400)
        report["tests_rc"] = rt.returncode
        report["tests_tail"] = (rt.stdout + rt.stderr).strip().splitlines()[-12:]
        return rt.returncode == 0, report
    finally:
        _cleanup(wt)


def main(argv):
    ap = argparse.ArgumentParser(description="tier 2: a tool change as a branch, proved in a worktree")
    ap.add_argument("--defect", required=True, help="what is wrong, and the evidence for it")
    ap.add_argument("--file", action="append", default=[], help="source the proposer is shown, repo-relative")
    ap.add_argument("--sha", default="HEAD")
    ap.add_argument("--test", default="v2/ecad/tools/tests/run_tests.sh",
                    help="the suite that must stay green, repo-relative")
    ap.add_argument("--branch", default=None, help="the branch to leave the change on when it passes")
    ap.add_argument("--repair", type=int, default=2)
    ap.add_argument("--out-dir", default="out/agent")
    ap.add_argument("--no-review", action="store_true")
    a = ap.parse_args(argv)

    os.makedirs(a.out_dir, exist_ok=True)
    sha = run(["git", "-C", REPO, "rev-parse", a.sha]).stdout.strip()
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    src = []
    for f in a.file:
        p = os.path.join(REPO, f)
        src.append("=== %s ===\n%s" % (f, open(p, errors="replace").read()[:60000]))
    user = ("THE COMMIT YOU ARE PATCHING: %s\n\n=== THE DEFECT ===\n%s\n\n%s" % (sha, a.defect, "\n\n".join(src)))

    c = client.Client(role="propose")
    tmp = tempfile.mkdtemp(prefix="meshsat-agent-patch-")
    attempts = []
    ok = False
    try:
        for i in range(a.repair + 1):
            text, meta = c.ask(SYSTEM, user, max_tokens=4000)
            try:
                d = client.extract_json(text)
                diff = d.get("diff") or ""
            except Exception as e:
                attempts.append({"attempt": i + 1, "ok": False, "error": "%s: %s" % (type(e).__name__, e), "meta": meta})
                user += "\n\n=== YOUR PREVIOUS ANSWER DID NOT PARSE ===\nAnswer with one JSON object."
                continue
            if not diff.strip():
                attempts.append({"attempt": i + 1, "ok": False, "error": "empty diff", "why": d.get("why"), "meta": meta})
                print("patch: the proposer returned no diff. Its reason: %s" % json.dumps(d.get("why"))[:400])
                break
            ok, report = try_patch(diff, sha, tmp, ["bash", os.path.join(REPO, a.test)])
            attempts.append({"attempt": i + 1, "ok": ok, "report": report, "why": d.get("why"),
                             "test": d.get("test"), "meta": meta, "diff": diff})
            print("patch: attempt %d %s" % (i + 1, "PASSES THE SUITE IN A WORKTREE" if ok else "refused"))
            if report.get("reserved"):
                for t in report["reserved"]:
                    print("    RESERVED %s in %s: %s" % (t["class"], t["file"], t["why"][:100]))
                print("    this belongs in v2/docs/OWNER-DECISIONS-2026-09-11.md, not in a patch")
                break
            if not report.get("applies"):
                print("    it does not apply: %s" % report.get("apply_error", "")[:300])
                user += "\n\n=== YOUR DIFF DID NOT APPLY ===\n%s\nReturn a diff that applies with git apply -p1." % report.get("apply_error", "")[:800]
                continue
            if ok:
                break
            print("    the suite failed in the worktree:")
            for l in report.get("tests_tail", []):
                print("      %s" % l[:150])
            user += "\n\n=== YOUR PATCH APPLIED BUT THE SUITE FAILED ===\n%s\nFix it." % "\n".join(report.get("tests_tail", []))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    open(os.path.join(a.out_dir, "patch-%s.json" % stamp), "w").write(json.dumps(attempts, indent=1, default=str))
    ledger.append(os.path.join(a.out_dir, "agent.jsonl"),
                  {"kind": "patch", "stamp": stamp, "sha": sha, "accepted": ok, "attempts": len(attempts),
                   "calls": [at["meta"] for at in attempts if "meta" in at],
                   "diff_sha": client.sha(attempts[-1].get("diff", "")) if attempts else ""})

    if not ok:
        return verdict.write("agent_patch", verdict.FAIL, counts={"attempts": len(attempts), "accepted": 0},
                             denominator=len(attempts) or 1,
                             evidence=[json.dumps(at.get("report", at.get("error")))[:300] for at in attempts],
                             note="no patch both applied, cleared the floor and kept the suite green",
                             out_dir=a.out_dir)

    diff = attempts[-1]["diff"]
    open(os.path.join(a.out_dir, "patch-%s.diff" % stamp), "w").write(diff)
    rev = None
    if not a.no_review:
        rev, rattempts = reviewmod.review(reviewmod.build_material(
            diff=diff, numbers="The suite ran green in a worktree cut at %s." % sha,
            extra=["This diff was written by an automated tier 2 to fix a named defect and has already been "
                   "proved to apply and to keep the test suite green. You are judging whether it should land."]))
        open(os.path.join(a.out_dir, "patch-review-%s.json" % stamp), "w").write(json.dumps(rattempts, indent=1, default=str))
        if rev:
            print("patch: review %s, %d finding(s)" % (rev["verdict"], len(rev["findings"])))
            for f in rev["findings"]:
                print("    %-8s %-34s %s" % (f["severity"], f["where"][:34], f["what"]))

    if a.branch and (not rev or rev["verdict"] == "APPROVE"):
        tmp2 = tempfile.mkdtemp(prefix="meshsat-agent-branch-")
        try:
            wt = _worktree(sha, tmp2)
            dp = os.path.join(tmp2, "p.diff"); open(dp, "w").write(diff)
            run(["git", "-C", wt, "apply", "-p1", dp])
            run(["git", "-C", wt, "checkout", "-b", a.branch])
            run(["git", "-C", wt, "add", "-A"])
            run(["git", "-C", wt, "-c", "user.name=Kyriakos Papadopoulos",
                 "-c", "user.email=ncpjfuzl@mxmx.email", "commit", "-q", "-m",
                 "fix(tools): %s [MESHSAT-862]\n\nProposed by tier 2, proved in a worktree at %s, reviewed by tier 2b."
                 % (a.defect.splitlines()[0][:60], sha[:12])])
            print("patch: left on branch %s. Nothing was committed to main" % a.branch)
        finally:
            _cleanup(os.path.join(tmp2, "wt")); shutil.rmtree(tmp2, ignore_errors=True)

    return verdict.write("agent_patch", verdict.PASS if (not rev or rev["verdict"] == "APPROVE") else verdict.FAIL,
                         counts={"attempts": len(attempts), "findings": len((rev or {}).get("findings") or [])},
                         denominator=len(attempts),
                         evidence=[(rev or {}).get("summary", "not reviewed")],
                         note="applied, cleared the floor, kept the suite green in a worktree at %s" % sha[:12],
                         out_dir=a.out_dir)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except client.Infra as e:
        print("patch: INFRA_FAIL %s" % e); sys.exit(3)
