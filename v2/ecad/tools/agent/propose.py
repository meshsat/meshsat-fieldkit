#!/usr/bin/env python3
"""Tier 2: propose the next arm, with a written prediction, and never actuate (MESHSAT-862, 12 Sep 2026).

This file asks a model for ONE arm and hands back a job spec. It contains no subprocess call, no exec,
no file execution and no path outside `out/agent/`, and `tests/test_agent_contract.py` asserts that by
reading it, because "the proposer never actuates" is a property of the code and not of an intention.

The shape follows the plan's tier 2 exactly: the next arm as a job spec with a prediction. The two
other things tier 2 may produce (a tool change as a merge request, an appendix entry) are separate
entry points; this one is the measurement loop, because that is the loop the boards are waiting on.

WHAT MAKES A PROPOSAL GOOD HERE, written into the prompt because the record earned each line:
  * A prediction that cannot fail is worthless. Of the arms this project has graded, most predictions
    were wrong, and every one of those taught something. A safe prediction teaches nothing.
  * The basis must name the evidence it rests on. "It should help" is refused by the validator.
  * One variable. Two knobs in one arm and the result names neither.
  * The law of the day: removing a bar moves the failure unless the bar was the last one. So a
    proposal that removes a named bar should say which bar it expects to be LAST, and why.
"""
import os, sys, json, time, argparse

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, HERE); sys.path.insert(0, TOOLS)
import client, schema, evidence                                   # noqa: E402
import verdict, ledger                                            # noqa: E402

SYSTEM = """You are tier 2 of a hardware pipeline's control plane: you PROPOSE and you never actuate.

You are given counted evidence about a differential-pair pre-router on one printed circuit board. You
return ONE experiment, called an arm, as JSON and nothing else. A deterministic runner executes it, a
mechanical judge grades it against your own written prediction, and a separate reviewer reads the
result. You never see a shell, a file or a board.

You own exactly three fields: the arm's name, its env knobs and its prediction. Everything else about
the run (which board, which project, which passes, which timeout) is filled in from the board's own
declaration file and is NOT yours to set. A proposal that sets any of those is refused.

RULES, each of which a validator enforces mechanically:
  1. Exactly one arm unless told otherwise. One variable: two knobs in one arm and the result names
     neither of them.
  2. name: lowercase letters, digits and underscores, at most 32 characters. It becomes a directory.
  3. env: only knobs from the proposable list you are given. A knob that is reserved or basis-locked
     is refused with its reason, and so is a knob no tool reads.
  4. predict: {"metric": "pairs", "op": one of >= > == <= <, "value": a number, "basis": at least 40
     characters naming the evidence you reasoned from}. The prediction is graded against the pair
     count the runner measures. It must be falsifiable: if your arm does nothing, your prediction
     should be wrong. Most predictions on this project have been wrong, and each wrong one taught
     more than a safe one would have.
  5. why: a list of short sentences, the argument for this arm, naming what you expect to be the LAST
     bar for the pairs you are aiming at.

Answer with one JSON object: {"arms": [{"name": ..., "env": {...}, "predict": {...}}], "why": [...]}
No prose outside the JSON. No markdown fence is required but one is tolerated."""


def ask(pack_text, ask_text, cfg=None, repair=2, max_arms=1, graded=(), template=None, max_tokens=2500):
    """Ask, validate, and on a refusal hand the refusal back once or twice. Returns (spec, arms, meta)."""
    c = client.Client(role="propose", cfg=cfg)
    user = pack_text + "\n\n=== WHAT TO PROPOSE ===\n" + ask_text
    attempts = []
    for i in range(repair + 1):
        text, meta = c.ask(SYSTEM, user, max_tokens=max_tokens)
        try:
            proposal = client.extract_json(text)
            parse_error = None
        except Exception as e:
            proposal, parse_error = {}, "%s: %s" % (type(e).__name__, e)
        ok, errs, arms = (False, [parse_error], []) if parse_error else schema.validate(
            proposal, template or {}, graded=graded, max_arms=max_arms)
        attempts.append({"attempt": i + 1, "accepted": ok, "errors": errs, "meta": meta,
                         "proposal": proposal if not parse_error else {"_unparseable": text[:800]}})
        if ok:
            return schema.build_spec(proposal, template or {}, arms), arms, attempts
        user = (user + "\n\n=== YOUR PREVIOUS ANSWER WAS REFUSED ===\n" +
                "\n".join("- " + e for e in errs) +
                "\nAnswer again with one JSON object that satisfies every rule. Do not argue with the refusal.")
    return None, [], attempts


def main(argv):
    ap = argparse.ArgumentParser(description="tier 2: propose one arm, never actuate")
    ap.add_argument("--letter", default="b")
    ap.add_argument("--template", required=True, help="the arms.py spec template this board's runs use")
    ap.add_argument("--profile", default=None, help="pair_report.py --json output, the counted failure profile")
    ap.add_argument("--ledger", action="append", default=[], help="arms.jsonl to read as graded history")
    ap.add_argument("--ask", default="Propose the single arm most likely to lay more pairs than the board's current best.")
    ap.add_argument("--note", action="append", default=[], help="extra evidence line for the pack")
    ap.add_argument("--out-dir", default="out/agent")
    ap.add_argument("--repair", type=int, default=2)
    ap.add_argument("--allow-repeat", action="store_true")
    a = ap.parse_args(argv)

    os.makedirs(a.out_dir, exist_ok=True)
    template = json.load(open(a.template))
    p = evidence.pack(a.letter, profile=a.profile, ledgers=a.ledger, extra=a.note)
    graded = () if a.allow_repeat else p["_signatures"]
    text = evidence.render(p)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    open(os.path.join(a.out_dir, "pack-%s.txt" % stamp), "w").write(text)

    try:
        spec, arms, attempts = ask(text, a.ask, repair=a.repair, graded=graded, template=template)
    except client.Infra as e:
        print("propose: INFRA_FAIL %s" % e)
        return verdict.write("propose", verdict.INCONCLUSIVE, counts={"attempts": 0}, denominator=1,
                             evidence=[str(e)], note="the endpoint or its config, not the proposal", out_dir=a.out_dir)

    for at in attempts:
        print("propose: attempt %d %s%s" % (at["attempt"], "ACCEPTED" if at["accepted"] else "REFUSED",
                                            "" if at["accepted"] else ":"))
        for e in at["errors"]:
            print("    %s" % e)
    open(os.path.join(a.out_dir, "attempts-%s.json" % stamp), "w").write(json.dumps(attempts, indent=1, default=str))

    row = {"kind": "proposal", "letter": a.letter, "stamp": stamp, "accepted": bool(spec),
           "attempts": len(attempts), "calls": [at["meta"] for at in attempts],
           "arms": [{"name": x["name"], "env": x.get("env"), "predict": x["predict"]} for x in arms]}
    ledger.append(os.path.join(a.out_dir, "agent.jsonl"), row)

    if not spec:
        print("propose: no acceptable proposal in %d attempts" % len(attempts))
        return verdict.write("propose", verdict.FAIL, counts={"accepted": 0, "attempts": len(attempts)},
                             denominator=len(attempts), evidence=attempts[-1]["errors"],
                             note="the validator refused every attempt; the refusals are the evidence", out_dir=a.out_dir)

    out = os.path.join(a.out_dir, "proposal-%s.json" % stamp)
    json.dump(spec, open(out, "w"), indent=1)
    print("propose: wrote %s" % out)
    for x in spec["arms"]:
        print("  arm %-16s env %s" % (x["name"], json.dumps(x["env"])))
        print("      predict %s %s, basis: %s" % (x["predict"].get("op"), x["predict"].get("value"), x["predict"].get("basis")))
    return verdict.write("propose", verdict.PASS, counts={"arms": len(spec["arms"]), "attempts": len(attempts)},
                         denominator=len(attempts), evidence=[out],
                         note="proposed, not run: tier 2 never actuates", out_dir=a.out_dir)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except client.Infra as e:
        print("propose: INFRA_FAIL %s" % e); sys.exit(3)
