#!/usr/bin/env python3
"""Tier 2b: fresh eyes on a change, in a context that never saw it being made (MESHSAT-862, 12 Sep 2026).

The plan calls this the only tier that could have caught the three electrical criticals of 9 September,
which no gate measured and two people found by reading. Under unattended operation it is not optional.

Two properties make it a reviewer rather than a second opinion from the same head:

  * A FRESH CLIENT. It is constructed here, never handed the proposer's conversation, and is given the
    artefacts only: the diff, the verdict JSONs, the measured numbers, the appendix draft. It cannot
    see why the change was made, which is the point.
  * IT CANNOT MOVE THE GRADE. The mechanical judge has already decided whether the prediction was met
    before this runs, and nothing the reviewer says changes that number. What the reviewer gates is
    the WRITE-UP and the commit: whether this goes into the record and the tree as it stands.

The review is graded by its own shape, not believed on sight: a verdict outside the allowed set, a
finding without a location, or a REJECT with no finding is refused here, because a reviewer that
cannot say where is not reviewing.
"""
import os, re, sys, json, time, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import client                                                     # noqa: E402
import verdict, ledger                                            # noqa: E402

SEV = {"critical", "major", "minor"}
VERDICTS = {"APPROVE", "REJECT", "REVISE"}

SYSTEM = """You are tier 2b of a hardware pipeline's control plane: a reviewer with fresh eyes.

You did not make this change and you are not told why it was made. You are given the diff, the verdict
files the gates wrote, the measured numbers and the draft record entry. You judge whether this should
go into the tree and into the design record AS IT STANDS.

This project's own history says what to look for, in this order:
  1. A TOOL THAT REPORTS SUCCESS ABOUT SOMETHING IT DID NOT DO. Four of six defects found on 12
     September were this: a closure that closed nothing counted as a closure; a hard-coded net list
     that meant a net was never searched for; a gate that stamped the wrong phase.
  2. A NUMBER THAT CANNOT SUPPORT ITS CLAIM. A measurement taken under a different placement, a
     different tree or a different wall clock is not comparable. Say so when you see one.
  3. AN ELECTRICAL ERROR THE GATES DO NOT MEASURE. Polarity, a part that cannot be bought in the land
     drawn for it, a rating below the rail it sits on, a signal that leaves no return path.
  4. A RULE THAT PASSES ON THE TREE IT WAS WRITTEN TO FAIL. A test that would not have caught the
     defect it was written for is worse than no test.
  5. Anything the change claims in prose that the diff does not do.

Answer with one JSON object and no prose outside it:
{"verdict": "APPROVE" | "REVISE" | "REJECT",
 "findings": [{"severity": "critical"|"major"|"minor", "where": "<file:line or artefact name>",
               "what": "<what is wrong, one sentence>", "why": "<the consequence, one sentence>"}],
 "summary": "<two sentences at most>"}

REJECT only with at least one critical or major finding. APPROVE with no critical and no major
finding. An empty findings list with APPROVE is a legitimate answer if you find nothing."""


def collect_diff(rng=None, paths=(), cwd=None, limit=200000):
    """The change under review, as the tree reports it. Truncated with a marker, never silently."""
    cmd = ["git", "diff"] + ([rng] if rng else []) + (["--"] + list(paths) if paths else [])
    d = subprocess.run(cmd, cwd=cwd or TOOLS, capture_output=True, text=True).stdout
    if len(d) > limit:
        d = d[:limit] + "\n... TRUNCATED at %d characters: the reviewer was NOT shown the rest ...\n" % limit
    return d


def validate_review(r):
    """A review is refused for its shape before it is read for its content."""
    errs = []
    if not isinstance(r, dict):
        return ["the review is %s, not an object" % type(r).__name__]
    v = r.get("verdict")
    if v not in VERDICTS:
        errs.append("verdict %r is not one of %s" % (v, sorted(VERDICTS)))
    fs = r.get("findings")
    if not isinstance(fs, list):
        errs.append("findings is %s, not a list" % type(fs).__name__); fs = []
    for i, f in enumerate(fs, 1):
        if not isinstance(f, dict):
            errs.append("finding %d is not an object" % i); continue
        if f.get("severity") not in SEV:
            errs.append("finding %d severity %r is not one of %s" % (i, f.get("severity"), sorted(SEV)))
        for k in ("where", "what", "why"):
            if not str(f.get(k) or "").strip():
                errs.append("finding %d has no %s: a reviewer that cannot say where is not reviewing" % (i, k))
    hard = [f for f in fs if isinstance(f, dict) and f.get("severity") in ("critical", "major")]
    if v == "REJECT" and not hard:
        errs.append("REJECT with no critical or major finding")
    if v == "APPROVE" and hard:
        errs.append("APPROVE with %d critical or major finding(s)" % len(hard))
    if not str(r.get("summary") or "").strip():
        errs.append("no summary")
    return errs


def review(material, cfg=None, repair=1, max_tokens=3000):
    """One fresh reviewer. Returns (review, attempts)."""
    c = client.Client(role="review", cfg=cfg)
    user = material
    attempts = []
    for i in range(repair + 1):
        text, meta = c.ask(SYSTEM, user, max_tokens=max_tokens)
        try:
            r = client.extract_json(text); errs = validate_review(r)
        except Exception as e:
            r, errs = {}, ["%s: %s" % (type(e).__name__, e)]
        attempts.append({"attempt": i + 1, "ok": not errs, "errors": errs, "meta": meta, "review": r})
        if not errs:
            return r, attempts
        user = material + "\n\n=== YOUR PREVIOUS REVIEW WAS REFUSED FOR ITS SHAPE ===\n" + "\n".join("- " + e for e in errs)
    return None, attempts


def build_material(diff="", verdicts=None, numbers="", draft="", extra=()):
    L = []
    if numbers:
        L.append("=== THE MEASURED RESULT (already graded mechanically; you cannot change this grade) ===\n" + numbers)
    if verdicts:
        L.append("=== THE VERDICT FILES THE GATES WROTE ===\n" + json.dumps(verdicts, indent=1)[:20000])
    if draft:
        L.append("=== THE DRAFT RECORD ENTRY ===\n" + draft[:20000])
    for e in extra:
        L.append("=== CONTEXT ===\n" + e)
    if diff:
        L.append("=== THE DIFF UNDER REVIEW ===\n" + diff)
    return "\n\n".join(L)


def main(argv):
    ap = argparse.ArgumentParser(description="tier 2b: fresh eyes, before done")
    ap.add_argument("--diff-range", default=None, help="a git range, e.g. HEAD~1..HEAD; default is the working tree")
    ap.add_argument("--path", action="append", default=[], help="limit the diff to these paths")
    ap.add_argument("--diff-file", default=None, help="review this diff instead of asking git")
    ap.add_argument("--numbers", default=None, help="file holding the measured result")
    ap.add_argument("--draft", default=None, help="file holding the draft appendix entry")
    ap.add_argument("--verdict-dir", default=None, help="collect verdict JSONs from here")
    ap.add_argument("--context", action="append", default=[])
    ap.add_argument("--out-dir", default="out/agent")
    a = ap.parse_args(argv)

    os.makedirs(a.out_dir, exist_ok=True)
    vs = {}
    if a.verdict_dir and os.path.isdir(a.verdict_dir):
        for f in sorted(os.listdir(a.verdict_dir)):
            if f.endswith(".verdict.json"):
                try: vs[f] = json.load(open(os.path.join(a.verdict_dir, f)))
                except ValueError: pass
    diff = open(a.diff_file, errors="replace").read() if a.diff_file else collect_diff(a.diff_range, a.path)
    material = build_material(diff, vs, open(a.numbers, errors="replace").read() if a.numbers else "",
                              open(a.draft, errors="replace").read() if a.draft else "", a.context)
    if not material.strip():
        print("review: nothing to review")
        return verdict.write("review", verdict.INCONCLUSIVE, counts={"material": 0}, denominator=1,
                             evidence=[], note="no diff, no numbers, no draft", out_dir=a.out_dir)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    open(os.path.join(a.out_dir, "review-material-%s.txt" % stamp), "w").write(material)
    try:
        r, attempts = review(material)
    except client.Infra as e:
        print("review: INFRA_FAIL %s" % e)
        return verdict.write("review", verdict.INCONCLUSIVE, counts={"attempts": 0}, denominator=1,
                             evidence=[str(e)], note="the endpoint or its config", out_dir=a.out_dir)

    open(os.path.join(a.out_dir, "review-%s.json" % stamp), "w").write(json.dumps(attempts, indent=1, default=str))
    ledger.append(os.path.join(a.out_dir, "agent.jsonl"),
                  {"kind": "review", "stamp": stamp, "verdict": (r or {}).get("verdict"),
                   "findings": len((r or {}).get("findings") or []), "calls": [at["meta"] for at in attempts],
                   "material_sha": client.sha(material)})
    if not r:
        for e in attempts[-1]["errors"]:
            print("review: REFUSED %s" % e)
        return verdict.write("review", verdict.FAIL, counts={"attempts": len(attempts)}, denominator=len(attempts),
                             evidence=attempts[-1]["errors"], note="the review was refused for its shape", out_dir=a.out_dir)

    hard = [f for f in r["findings"] if f["severity"] in ("critical", "major")]
    print("review: %s, %d finding(s), %d critical or major" % (r["verdict"], len(r["findings"]), len(hard)))
    for f in r["findings"]:
        print("  %-8s %-42s %s" % (f["severity"], f["where"][:42], f["what"]))
        print("           why: %s" % f["why"])
    print("review: %s" % r["summary"])
    return verdict.write("review", verdict.PASS if r["verdict"] == "APPROVE" else verdict.FAIL,
                         counts={"findings": len(r["findings"]), "critical_or_major": len(hard)},
                         denominator=len(r["findings"]) or 1,
                         evidence=["%s %s: %s" % (f["severity"], f["where"], f["what"]) for f in r["findings"]],
                         note=r["verdict"] + ": " + r["summary"], out_dir=a.out_dir)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except client.Infra as e:
        print("review: INFRA_FAIL %s" % e); sys.exit(3)
