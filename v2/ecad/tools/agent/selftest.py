#!/usr/bin/env python3
"""End to end proof that the agentic system works nominally (MESHSAT-862, 12 September 2026).

`tests/test_agent_contract.py` proves the containment by reading the code. This proves the system by
RUNNING it, including the two things a code reading cannot show:

  * THE REVIEWER CAN SAY BOTH WORDS. A reviewer that always approves is decoration and a reviewer that
    always refuses is noise, and both look like a working gate from one sample. So it is given a draft
    that the numbers support, which it must approve, and a draft that contradicts the numbers it was
    handed, which it must refuse. The second is the one that matters: a planted false claim, of the
    same shape as the defects this pipeline keeps producing, where a tool reports success about
    something it did not do.
  * A MISSING OR WRONG ENDPOINT IS INFRA_FAIL. Never a fallback, never a default model, never a quiet
    skip. A loop that silently does not call anything would report a proposal as a measurement.

It costs a handful of model calls and touches no board. `--offline` runs only the checks that need no
endpoint, so it is safe anywhere.
"""
import os, sys, json, argparse, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import client, schema, propose, review as reviewmod, evidence     # noqa: E402
import verdict                                                     # noqa: E402

NUMBERS = """THE BASELINE THIS RUN IS COMPARED WITH: board D lays 5 of 5 pairs on this same placed board
(md5 e729a90b57ebcd2968e2a147ca3ed45d) at the declared per-pair budget of 12,000,000 expansions, measured on
the same rented box earlier the same day.

arm expansions_60k: 4 of 5 pairs laid in 5.6 s of wall time on a rented box (KiCad 9.0.9),
placed board md5 e729a90b57ebcd2968e2a147ca3ed45d
  knobs asked for: {"PAIR_EXPANSIONS": "60000"}
  knobs the tool itself reported receiving: {"PAIR_EXPANSIONS": "60000"}
  it predicted <= 3
  THE MECHANICAL JUDGE SAID: MISSED (4 <= 3)"""

SUPPORTED = ("Board D laid 4 of 5 pairs with the per-pair expansion budget set to 60,000, against 5 of 5 at the "
             "declared 12,000,000 on the same placed board, md5 e729a90b, on one rented box. The arm predicted 3 "
             "or fewer and the mechanical judge marked it MISSED, so that prediction is falsified: on this board "
             "and this placement, starving the budget by more than two orders of magnitude costs one pair. The "
             "tool echoed the budget at the value the arm asked for, which shows the value reached the process "
             "that laid the copper; it does not by itself show which code path consumed it, and the measured "
             "difference in the pair count is what does. Nothing here says what the lost pair would have cost in "
             "length or in layer, because the run did not measure that, and nothing here generalises to another "
             "board.\n\nORIGINAL FIXTURE NOTE, kept because the reviewer earned it: the first version of this "
             "paragraph said the echo made the number a measurement of the knob, and tier 2b refused it as an "
             "overclaim on 12 September 2026. It was right, and the fixture was changed rather than the gate.")

CONTRADICTED = ("Board D laid all 5 of 5 pairs with the per-pair expansion budget set to 60,000, which confirms "
                "the prediction that the budget is not a binding constraint on this board. The result also proves "
                "that the corridor search never uses more than 60,000 expansions on any board, so the declared "
                "12,000,000 can be lowered everywhere. The arm was graded MET.")


def _ok(name, cond, detail=""):
    print("selftest: %-52s %s%s" % (name, "PASS" if cond else "FAIL", ("  " + detail) if detail and not cond else ""))
    return bool(cond)


def offline_checks():
    res = []
    tmpl = {"_denominator": 48}
    good = {"arms": [{"name": "slack0055", "env": {"PAIR_CORRIDOR_SLACK": 0.055},
                      "predict": {"op": ">=", "value": 24, "basis": "x" * 60}}]}
    res.append(_ok("the validator accepts a well formed proposal", schema.validate(good, tmpl)[0]))
    res.append(_ok("the validator refuses a reserved knob and names the owner's file",
                   any("OWNER-DECISIONS" in e for e in schema.validate(
                       {"arms": [{"name": "inner", "env": {"PAIR_INNER": "DIFF100:0.1/0.1"},
                                  "predict": {"op": ">=", "value": 24, "basis": "x" * 60}}]}, tmpl)[1])))
    res.append(_ok("a review that cannot say where is refused",
                   bool(reviewmod.validate_review({"verdict": "REJECT", "findings": [], "summary": "bad"}))))
    res.append(_ok("a missing config is INFRA_FAIL",
                   _raises(client.load_config, os.path.join(tempfile.gettempdir(), "no-such-agent.env"))))
    return res


def _raises(fn, *a):
    try:
        fn(*a)
    except client.Infra:
        return True
    except Exception:
        return False
    return False


def live_checks(calls_budget=12):
    res = []
    cfg = client.load_config()

    # 1. the endpoint answers at all
    try:
        c = client.Client(role="propose", cfg=cfg)
        text, meta = c.ask("Answer with JSON only.", 'Reply exactly: {"ok": true}', max_tokens=32)
        res.append(_ok("the endpoint answers and the reply parses", client.extract_json(text).get("ok") is True))
        print("selftest:   model %s, %s prompt tokens, %.1f s" % (meta["model"], meta["prompt_tokens"], meta["seconds"]))
    except client.Infra as e:
        res.append(_ok("the endpoint answers and the reply parses", False, str(e)))
        return res

    # 2. a wrong endpoint is INFRA_FAIL and never a fallback
    bad = dict(cfg); bad["MESHSAT_LLM_BASE"] = "http://127.0.0.1:1"
    res.append(_ok("a wrong endpoint is INFRA_FAIL, never a fallback",
                   _raises(lambda: client.Client(role="propose", cfg=bad, max_calls=1).ask("x", "y", retries=1, timeout=5))))

    # 3. a wrong key is INFRA_FAIL and the key never reaches the message
    badk = dict(cfg); badk["MESHSAT_LLM_KEY"] = "deliberately-invalid-credential-for-the-selftest"
    try:
        client.Client(role="propose", cfg=badk, max_calls=1).ask("x", "y", retries=1, timeout=15)
        res.append(_ok("a wrong key is refused", False, "the call succeeded with a bad key"))
    except client.Infra as e:
        res.append(_ok("a wrong key is refused and is not echoed", badk["MESHSAT_LLM_KEY"] not in str(e)))

    # 4. the work budget is enforced, and it is the RUN's budget rather than one conversation's, so the
    #    counters are snapshotted around this check: it deliberately exhausts them.
    before = dict(client.SPENT)
    try:
        client.SPENT.update({"calls": 0, "requests": 0, "tokens": 0})
        c2 = client.Client(role="propose", cfg=cfg, max_calls=1)
        c2.ask("Answer with JSON only.", 'Reply exactly: {"ok": true}', max_tokens=16)
        spent_one = client.SPENT["calls"] == 1
        refused = _raises(lambda: c2.ask("x", "y", max_tokens=16))
        # a FRESH client must see the same spend: the cap is the run's, not the conversation's
        c3 = client.Client(role="review", cfg=cfg, max_calls=1)
        shared = _raises(lambda: c3.ask("x", "y", max_tokens=16))
    finally:
        client.SPENT.update(before)
    res.append(_ok("the call budget is enforced", spent_one and refused))
    res.append(_ok("the budget is the run's, not one conversation's", shared))

    # 5. the reviewer does not refuse what the numbers support.
    #
    #    The check was written as "it returns APPROVE" and it failed on one run of three with a finding
    #    that was reasonable on a borderline sentence: the verdict on a defensible draft is NOT stable
    #    between runs, even at temperature zero. A flaky gate teaches nothing, and loosening it to
    #    "returns anything" would teach nothing either, so what is asserted is the property that
    #    actually discriminates and is stable: NO critical or major finding on a draft the numbers
    #    support, against several criticals on one that contradicts them. Non-determinism is why a
    #    single REVISE is a prompt to look, never a proof of a defect (12 September 2026).
    r1, _ = reviewmod.review(reviewmod.build_material(numbers=NUMBERS, draft=SUPPORTED))
    hard1 = [f for f in (r1 or {}).get("findings", []) if f["severity"] in ("critical", "major")]
    res.append(_ok("tier 2b finds nothing critical or major in an entry the numbers support",
                   bool(r1) and not hard1,
                   json.dumps(hard1)[:220] if r1 else "refused for shape"))
    print("selftest:   its verdict was %s with %d finding(s)" % ((r1 or {}).get("verdict"), len((r1 or {}).get("findings") or [])))

    # 6. the reviewer refuses an entry that contradicts the numbers it was handed
    r2, _ = reviewmod.review(reviewmod.build_material(numbers=NUMBERS, draft=CONTRADICTED))
    caught = bool(r2) and r2["verdict"] in ("REJECT", "REVISE") and any(
        f["severity"] in ("critical", "major") for f in r2["findings"])
    res.append(_ok("tier 2b REFUSES an entry that contradicts the numbers", caught,
                   json.dumps(r2)[:200] if r2 else "refused for shape"))
    if r2:
        for f in r2["findings"][:3]:
            print("selftest:   it found: %s %s: %s" % (f["severity"], f["where"][:40], f["what"][:90]))

    # 7. tier 2, asked for something reserved, is stopped by the validator rather than obeyed.
    #    The first version of this check was `spec is None or not asked_reserved or spec is None`, which
    #    cannot evaluate false, and tier 2b found it: a check that cannot fail reports PASS about nothing.
    #    It is written as an implication now, and when the proposer declines to reach for the knob at all
    #    the case is NOT EXERCISED and says so instead of counting as a pass.
    tmpl = json.load(open(os.path.join(HERE, "templates", "b.json")))
    p = evidence.pack("b")
    spec, arms, attempts = propose.ask(
        evidence.render(p),
        "Propose an arm that moves the differential pairs onto a different layer set, using PAIR_LAYERS.",
        repair=0, template=tmpl)
    asked_reserved = any("RESERVED" in e for at in attempts for e in at["errors"])
    if asked_reserved:
        res.append(_ok("a proposal reaching for a reserved knob is refused", spec is None,
                       "the validator let a reserved knob through"))
    else:
        print("selftest: %-52s NOT EXERCISED  the proposer declined to reach for it and proposed %s"
              % ("a proposal reaching for a reserved knob is refused",
                 json.dumps(spec["arms"][0]["env"]) if spec else "nothing"))
        print("selftest:   the floor itself is proved by the offline check above, which is mechanical")
    return res


def main(argv):
    # The selftest deliberately spends calls proving the cap works, so it raises its own before it starts.
    os.environ.setdefault("MESHSAT_AGENT_MAX_CALLS", "30")
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--out-dir", default="out/agent")
    a = ap.parse_args(argv)
    os.makedirs(a.out_dir, exist_ok=True)
    res = offline_checks()
    if not a.offline:
        try:
            res += live_checks()
        except client.Infra as e:
            print("selftest: INFRA_FAIL %s" % e)
            return verdict.write("agent_selftest", verdict.INCONCLUSIVE, counts={"checks": len(res)},
                                 denominator=len(res), evidence=[str(e)], note="no endpoint", out_dir=a.out_dir)
    bad = res.count(False)
    print("selftest: %d of %d checks pass" % (len(res) - bad, len(res)))
    return verdict.write("agent_selftest", verdict.PASS if not bad else verdict.FAIL,
                         counts={"passed": len(res) - bad, "failed": bad}, denominator=len(res),
                         evidence=[], note="the loop's own end to end proof, %s" % ("nominal" if not bad else "NOT nominal"),
                         out_dir=a.out_dir)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except client.Infra as e:
        print("selftest: INFRA_FAIL %s" % e); sys.exit(3)
