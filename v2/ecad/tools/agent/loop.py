#!/usr/bin/env python3
"""The loop: evidence, propose, validate, run, grade, review, record (MESHSAT-862, 12 September 2026).

This is the whole agentic system in one file's worth of control flow, and the order is the contract:

    evidence (counted artefacts)
      -> tier 2 proposes ONE arm with a written prediction        [a model, contained by schema.py]
      -> the validator accepts or refuses it                      [mechanical, fail closed]
      -> the deterministic runner executes it                     [arms.py, no model anywhere near it]
      -> the mechanical judge grades it against the prediction    [arms.grade, never the model]
      -> tier 2 drafts the record entry from the numbers          [a model]
      -> tier 2b reviews the entry and the numbers with fresh eyes[a different context]
      -> the ledger chains all of it

THE JUDGE IS NEVER THE PROPOSER and the reviewer cannot move the grade. Those two sentences are the
reason this is worth building at all: the width a model adds only pays against an objective that is
trustworthy, and the objective here is a pair count printed by a tool that has no idea a model exists.

EXECUTION IS NOT DONE HERE WHEN KICAD IS NOT HERE. The runner host has no pcbnew, so `--exec` takes a
command template that runs `arms.py` where the boards are. The command is given on the command line
and never stored in the tree, because the machine it names is not this repo's business and this repo
is public within minutes.
"""
import os, sys, json, time, shlex, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import client, schema, evidence, propose, review as reviewmod     # noqa: E402
import verdict, ledger, arms as armsmod                           # noqa: E402

DRAFT_SYSTEM = """You write one entry for a hardware project's design record, from measurements only.

The record's rules, which are not stylistic:
  * Every number carries what it was measured on. A pair count without the board and the placement it
    came from answers nothing.
  * A missed prediction is reported as plainly as a met one, and what it falsifies is said out loud.
  * Never claim a cause the measurement does not carry. "X did not pay" is supported; "X does not
    work" usually is not.
  * No em dashes anywhere. Prototype framing: nothing has been built or field deployed.
  * Four to twelve sentences. No headings, no bullet list, no markdown.

You are given the arm, its written prediction, the measured result and the mechanical grade. Answer
with one JSON object: {"entry": "<the prose>", "headline": "<one sentence, at most 120 characters>"}"""


def run_spec(spec_path, exec_cmd, result_path, timeout=None):
    """Execute the spec. Either here (when pcbnew is importable) or through the caller's command."""
    if exec_cmd:
        # AN ARGV, NOT A SHELL STRING. `routeflow.sh()` refuses the construction this used, and this is
        # the loop's one actuation point: the operator authors the template, the model never does, and a
        # substituted string is still the wrong shape for the place where a run begins (red team,
        # 12 September 2026). Substitution happens per argument, after the split.
        argv = [a.replace("{spec}", spec_path).replace("{result}", result_path) for a in shlex.split(exec_cmd)]
        print("loop: executing %s" % " ".join(argv[:3] + (["..."] if len(argv) > 3 else [])))
        r = subprocess.run(argv, timeout=timeout)
        return r.returncode
    try:
        import pcbnew                                             # noqa: F401
    except Exception as e:
        raise client.Infra("no pcbnew here and no --exec given, so nothing can run the arm (%s). "
                           "This is INFRA_FAIL and never a fallback: a loop that quietly skips the run "
                           "would report a proposal as a measurement" % type(e).__name__)
    return armsmod.main([spec_path, "--parallel", "1", "--out-dir", os.path.dirname(result_path)])


def read_rows(path, names, after_seq=-1):
    """The rows the runner appended FOR THIS CYCLE: the name matches and the row is newer than the head
    the cycle started from. Tier 2b found the gap: selected by name alone, an older row carrying the same
    model-chosen name is read as this cycle's measurement, and the name is chosen by the model."""
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path, errors="replace"):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except ValueError:
            continue
        seq = rec.get("seq", -1)
        rec = rec.get("rec", rec)
        if rec.get("arm") in names and seq > after_seq:
            out.append(rec)
    return out


def numbers_text(rows, baseline=None):
    """The measurement, and the baseline it may be compared with, or the plain statement that there is none.

    Tier 2b found this gap on the second cycle it reviewed: the block handed to the draft carried the
    arm's pair count and no baseline, so every sentence comparing the two was drawing on a number that
    was not in front of it. A record entry whose comparison comes from memory is exactly how this
    project got "the staircase costs five pairs" (two runs under different box loads) and "C10 has five
    short opens" (a loose end measured against the wrong pad).
    """
    L = []
    if baseline:
        L.append("THE BASELINE THIS RUN IS COMPARED WITH: %s" % baseline)
    else:
        L.append("NO BASELINE WAS SUPPLIED TO THIS CYCLE. Do not compare this number with any other number: "
                 "you have not been shown one, and a comparison drawn from memory is not a measurement.")
    for r in rows:
        p = r.get("predict") or {}
        L.append("arm %s: %s of %s pairs laid in %s s of wall time on %s (KiCad %s), placed board md5 %s"
                 % (r.get("arm"), r.get("pairs"), r.get("of"), r.get("wall_s"), r.get("host"), r.get("kicad"),
                    r.get("placed_md5")))
        L.append("  knobs asked for: %s" % json.dumps(r.get("env", {})))
        L.append("  knobs the tool itself reported receiving: %s"
                 % json.dumps({k: v for k, v in (r.get("knobs_seen") or {}).items() if k in (r.get("env") or {})}
                              or (r.get("knobs_seen") or {})))
        L.append("  it predicted %s %s, basis: %s" % (p.get("op"), p.get("value"), p.get("basis")))
        L.append("  THE MECHANICAL JUDGE SAID: %s  (%s)" % (r.get("verdict"), r.get("note")))
    return "\n".join(L)


def draft_entry(nums, context="", cfg=None, repair=1):
    """The record entry, refused for its shape the way everything else here is refused."""
    c = client.Client(role="propose", cfg=cfg)
    user = (context + "\n\n" if context else "") + nums
    for _ in range(repair + 1):
        text, meta = c.ask(DRAFT_SYSTEM, user, max_tokens=1200)
        try:
            d = client.extract_json(text)
            missing = [k for k in ("entry", "headline") if not str(d.get(k) or "").strip()]
            if not missing and "—" not in d["entry"] and "--" not in d["headline"]:
                return d, meta
            why = ("the draft carries no %s" % ", ".join(missing)) if missing else "the draft used an em dash, which this record never does"
        except Exception as e:
            why = "%s: %s" % (type(e).__name__, e)
        user = (context + "\n\n" if context else "") + nums + "\n\n=== YOUR PREVIOUS DRAFT WAS REFUSED ===\n" + why
    raise ValueError(why)


def main(argv):
    ap = argparse.ArgumentParser(description="the agentic loop, tier 2 and 2b around a deterministic runner")
    ap.add_argument("--letter", default="b")
    ap.add_argument("--template", required=True)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--ledger", action="append", default=[])
    ap.add_argument("--ask", default="Propose the single arm most likely to lay more pairs than the board's current best.")
    ap.add_argument("--note", action="append", default=[])
    ap.add_argument("--out-dir", default="out/agent")
    ap.add_argument("--exec", dest="exec_cmd", default=None,
                    help="command that runs arms.py where the boards are; {spec} and {result} are substituted")
    ap.add_argument("--result", default=None, help="the arms.jsonl the runner appends to")
    ap.add_argument("--exec-timeout", type=int, default=None)
    ap.add_argument("--no-exec", action="store_true", help="propose and stop, which is tier 2 on its own")
    ap.add_argument("--no-review", action="store_true")
    ap.add_argument("--baseline", default=None,
                    help="the number this run is compared with, with the board and placement it came from")
    ap.add_argument("--revisions", type=int, default=1,
                    help="how many times a refused draft is rewritten against the findings and reviewed again")
    ap.add_argument("--allow-repeat", action="store_true")
    a = ap.parse_args(argv)

    os.makedirs(a.out_dir, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    template = json.load(open(a.template))
    template.setdefault("_stamp", stamp)
    p = evidence.pack(a.letter, profile=a.profile, ledgers=a.ledger, extra=a.note)
    pack_text = evidence.render(p)
    open(os.path.join(a.out_dir, "pack-%s.txt" % stamp), "w").write(pack_text)
    print("loop: evidence pack %d characters, %d arms already graded" % (len(pack_text), p["graded_count"]))

    # WIDTH. One arm per cycle made a loop whose stated argument is width serial by construction; the
    # runner has taken --parallel since it was written (red team, 12 September 2026). The template says
    # how many, each with its own prediction, and they are dispatched together.
    spec, arms, attempts = propose.ask(pack_text, a.ask, repair=2,
                                       graded=() if a.allow_repeat else p["_signatures"], template=template,
                                       max_arms=int(template.get("_max_arms", 1)),
                                       best=p.get("best_pairs"), worst=p.get("worst_pairs"))
    for at in attempts:
        print("loop: propose attempt %d %s" % (at["attempt"], "ACCEPTED" if at["accepted"] else "REFUSED"))
        for e in at["errors"]:
            print("      %s" % e)
    open(os.path.join(a.out_dir, "attempts-%s.json" % stamp), "w").write(json.dumps(attempts, indent=1, default=str))
    ledger.append(os.path.join(a.out_dir, "agent.jsonl"),
                  {"kind": "proposal", "stamp": stamp, "letter": a.letter, "accepted": bool(spec),
                   "attempts": len(attempts), "calls": [at["meta"] for at in attempts],
                   "arms": [{"name": x["name"], "env": x.get("env"), "predict": x["predict"]} for x in arms]})
    if not spec:
        print("loop: refused every attempt, nothing ran")
        return verdict.write("agent_loop", verdict.FAIL, counts={"accepted": 0, "attempts": len(attempts)},
                             denominator=len(attempts), evidence=attempts[-1]["errors"],
                             note="the validator refused every proposal", out_dir=a.out_dir)

    spec_path = os.path.join(a.out_dir, "proposal-%s.json" % stamp)
    json.dump(spec, open(spec_path, "w"), indent=1)
    for x in spec["arms"]:
        print("loop: arm %s env %s predict %s %s" % (x["name"], json.dumps(x["env"]), x["predict"]["op"], x["predict"]["value"]))
    if a.no_exec:
        print("loop: --no-exec, stopping at the proposal (tier 2 never actuates anyway)")
        return verdict.write("agent_loop", verdict.INCONCLUSIVE, counts={"arms": len(spec["arms"]), "ran": 0},
                             denominator=len(spec["arms"]), evidence=[spec_path],
                             note="proposed and not run", out_dir=a.out_dir)

    result = a.result or os.path.join(a.out_dir, "arms.jsonl")
    head_before = ledger.head(result)[0]          # every row after this one belongs to this cycle
    rc = run_spec(spec_path, a.exec_cmd, result, timeout=a.exec_timeout)
    names = {x["name"] for x in spec["arms"]}
    rows = read_rows(result, names, after_seq=head_before)
    if not rows:
        print("loop: the runner produced no row for %s (exit %s)" % (sorted(names), rc))
        return verdict.write("agent_loop", verdict.INCONCLUSIVE, counts={"rows": 0}, denominator=len(names),
                             evidence=["exit %s" % rc, result], note="the arm did not run to a row", out_dir=a.out_dir)

    # THE RUNNER IS THE JUDGE AND THERE IS ONLY ONE. This used to re-grade every row here, and on the
    # first cycle where the two could differ they did: the runner graded an arm ILLEGAL against the
    # baseline hard count it had measured, and this loop re-graded the same row UNMEASURED because it
    # had no baseline to hand. Two graders with two answers is worse than either. The runner's verdict
    # stands; a row that arrives without one is graded here and says so (12 September 2026).
    for r in rows:
        if not r.get("verdict"):
            v, note = armsmod.grade(r, r.get("hard_baseline"))
            r["verdict"], r["note"] = v, note
            r["graded_by"] = "the loop, because the row carried no verdict"
        else:
            r.setdefault("graded_by", "the runner that measured it")
    nums = numbers_text(rows, a.baseline)
    print("loop: measured\n" + nums)
    open(os.path.join(a.out_dir, "numbers-%s.txt" % stamp), "w").write(nums)

    draft, dmeta = draft_entry(nums, context="Board %s, the pair pre-router." % a.letter.upper())
    open(os.path.join(a.out_dir, "draft-%s-0.md" % stamp), "w").write(draft["entry"])
    print("loop: draft headline: %s" % draft.get("headline"))

    rev = None
    if not a.no_review:
        context = ["The arm was proposed by an automated tier 2 from counted evidence and executed by a "
                   "deterministic runner. You are judging whether the numbers support the draft entry."]
        for cycle in range(a.revisions + 1):
            # THE REVIEWER GETS THE ARTEFACTS, not a numbers block. It can only catch "the knob did not
            # reach the tool" if it can see knobs_seen against env, and only weigh legality if it can see
            # the hard count with its denominator (red team, 12 September 2026).
            vs = {}
            for f in sorted(os.listdir(a.out_dir)) if os.path.isdir(a.out_dir) else []:
                if f.endswith(".verdict.json"):
                    try: vs[f] = json.load(open(os.path.join(a.out_dir, f)))
                    except ValueError: pass
            vs["arm_rows"] = [{k: r.get(k) for k in ("arm", "env", "knobs_seen", "pairs", "of", "hard",
                                                     "verdict", "note", "tools", "placed_md5", "board_sha")}
                              for r in rows]
            material = reviewmod.build_material(diff="", verdicts=vs, numbers=nums, draft=draft["entry"], extra=context)
            rev, rattempts = reviewmod.review(material)
            open(os.path.join(a.out_dir, "review-%s-%d.json" % (stamp, cycle)), "w").write(
                json.dumps(rattempts, indent=1, default=str))
            if not rev:
                print("loop: the review was refused for its shape"); break
            print("loop: review %s, %d finding(s)" % (rev["verdict"], len(rev["findings"])))
            for f in rev["findings"]:
                print("      %-8s %-30s %s" % (f["severity"], f["where"][:30], f["what"]))
            if rev["verdict"] == "APPROVE" or cycle == a.revisions:
                break
            # REVISE and REJECT both mean the entry does not go in as it stands. The draft is rewritten
            # against the findings and reviewed again, by a fresh context that has not seen this exchange.
            print("loop: redrafting against %d finding(s)" % len(rev["findings"]))
            fixes = "\n".join("- %s (%s): %s. Why it matters: %s" % (f["severity"], f["where"], f["what"], f["why"])
                               for f in rev["findings"])
            draft, _ = draft_entry(nums, context=("Board %s, the pair pre-router.\n\nA reviewer refused your "
                                                  "previous entry for these reasons. Write it again so that every "
                                                  "sentence is supported by the measurement above, and DROP any "
                                                  "claim the run cannot carry rather than hedging it:\n%s\n\n"
                                                  "Your previous entry was:\n%s"
                                                  % (a.letter.upper(), fixes, draft["entry"])))
            open(os.path.join(a.out_dir, "draft-%s-%d.md" % (stamp, cycle + 1)), "w").write(draft["entry"])
            print("loop: redraft headline: %s" % draft.get("headline"))

    ledger.append(os.path.join(a.out_dir, "agent.jsonl"),
                  {"kind": "cycle", "stamp": stamp, "letter": a.letter,
                   "arms": [{"arm": r.get("arm"), "pairs": r.get("pairs"), "of": r.get("of"),
                             "verdict": r.get("verdict"), "env": r.get("env")} for r in rows],
                   "draft_sha": client.sha(draft["entry"]), "review": (rev or {}).get("verdict"),
                   "final_draft": draft["entry"],
                   "findings": len((rev or {}).get("findings") or [])})

    # FOUR QUESTIONS, FOUR FIELDS. One verdict used to answer "did the experiment measure anything",
    # "was the prediction met" and "was the write-up approved" at once, and `missed` was the remainder,
    # so an UNMEASURED or ILLEGAL arm counted as a missed prediction (red team, 12 September 2026).
    import collections as _c
    g = _c.Counter(r.get("verdict") for r in rows)
    met = g["MET"]
    bad = g["INFRA_FAIL"] + g["UNMEASURED"] + g["UNMEASURABLE"]
    # Tier 2b gates the WRITE-UP, and a verdict file that reads PASS over a refused entry is a claim the
    # code does not make good on (its own finding on the change that introduced it, 12 September 2026).
    # The measurement stands either way: the arm's grade is above and the reviewer never touched it.
    refused = bool(rev) and rev["verdict"] != "APPROVE"
    if refused:
        print("loop: tier 2b did not approve the entry (%s), so the cycle is FAIL: the number stands, the "
              "write-up does not go into the record as it is" % rev["verdict"])
    if rev is None and not a.no_review:
        print("loop: no usable review, so the cycle is INCONCLUSIVE rather than PASS")
    return verdict.write("agent_loop",
                         verdict.INCONCLUSIVE if (bad or (rev is None and not a.no_review))
                         else (verdict.FAIL if refused else verdict.PASS),
                         counts={"arms": len(rows), "met": g["MET"], "missed": g["MISSED"],
                                 "illegal": g["ILLEGAL"], "unmeasured": g["UNMEASURED"],
                                 "unmeasurable": g["UNMEASURABLE"], "infra_fail": g["INFRA_FAIL"],
                                 "best_pairs": max((r.get("pairs") or 0) for r in rows),
                                 "review_findings": len((rev or {}).get("findings") or []),
                                 "process_status": "PASS" if not bad else "INCONCLUSIVE",
                                 "measurement_status": ("MEASURED" if met + g["MISSED"] else "NOT MEASURED"),
                                 "review_status": (rev or {}).get("verdict", "none")},
                         denominator=len(rows),
                         evidence=[nums, (rev or {}).get("summary", "no review")],
                         note="one cycle: proposed, run, graded mechanically, reviewed by a separate context",
                         out_dir=a.out_dir)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except client.Infra as e:
        print("loop: INFRA_FAIL %s" % e); sys.exit(3)
