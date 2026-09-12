#!/usr/bin/env python3
"""The fail-closed gate between a proposal and anything that runs (MESHSAT-862, 12 September 2026).

Tier 2 proposes and never actuates. That sentence is only worth something if something mechanical
stands between the proposal and the runner, so this is that thing.

**CATEGORY IS THE AUTHORITY, and the red team was right that it used not to be.** The first version
derived the proposable set by scanning the tools for `os.environ.get("PAIR_...")`, which told us a name
exists and never that it is a lever: `PAIR_PLAN_OUT` (writes a file), `PAIR_DEBUG` (prints) and
`PAIR_NO_NUMBA` (chooses the kernel) were all proposable, and an arm on any of them is a meaningless
null that reads exactly like a knob that does not pay. `knobs.json` is the registry now: name, type,
category, stage, default, unit and one line of description each. The source scan survives as a
COMPLETENESS check, `t_every_knob_the_tools_read_is_in_the_registry`, which is the direction that is
safe: a knob nobody registered is a test failure, not a licence.

What the model owns and the rules that hold it:

  * THREE FIELDS: the arm's name, its env knobs and its prediction. The board, the letter, the source
    project, the placed board, the passes and the timeout come from the template. A proposal carrying
    one of those is REFUSED rather than stripped.
  * ONE VARIABLE, MECHANICALLY. The prompt said it and nothing enforced it, so two knobs in one arm
    passed every check and the result named neither. `_max_knobs` in the template, default 1.
  * THE METRIC IS CLOSED. The judge grades the pair count; a prediction that says it is predicting
    runtime and is then graded against pairs is a row whose prose and meaning disagree.
  * THE PREDICTION MUST BE ABLE TO BE WRONG. `>= 1` on a board that lays 22 is accepted by an operator
    check, runs nineteen minutes and is graded MET. For `>=` and `>` the value must beat the best row
    graded for this board and stage; for `<=` and `<` it must be under the worst.
  * A KNOB THIS RUN CANNOT EXECUTE IS REFUSED, by the stage in the registry against the template's.
  * A FLAG TAKES `0` OR `1`. The tools read a flag as `!= "0"`, so `false` arrives ON.
  * AN ARM NAME IS A SLUG, because it becomes a directory `arms.py` removes with rmtree.
  * A REPEAT IS NOT LEARNING.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
REGISTRY = os.path.join(HERE, "knobs.json")

MODEL_OWNS = {"name", "env", "predict", "why"}
SPEC_OWNS = {"board", "letter", "source_project", "placed", "passes", "timeout_s", "ecad", "tools_sha",
             "hard_baseline"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9_]*$")
SLUG_MAX = 32
OPS = {">=", ">", "==", "<=", "<"}
UP = {">=", ">"}
DOWN = {"<=", "<"}
# The files a knob may be read from, for the completeness check only.
KNOB_FILES = ("pair_preroute.py", "gen_pcb_b3.py", "pairsearch.py")
# What each run shape EXECUTES, so a knob's stage can be checked against it. A place run regenerates the
# placement and then runs the pair passes, so it can act on both; a pair run cannot act on a placement
# knob at all, because the board it is handed was placed hours earlier.
STAGES = {"pair": ("pair",), "place": ("place", "pair")}


def registry(path=REGISTRY):
    return json.load(open(path))["knobs"]


def by_category(cat, reg=None):
    reg = reg or registry()
    return {k: v for k, v in reg.items() if v.get("category") == cat}


# Kept as names for the older callers and the tests that read them.
def RESERVED_KNOBS(reg=None):
    return {k: v["description"] for k, v in by_category("reserved", reg).items()}


def BASIS_KNOBS(reg=None):
    return {k: v["description"] for k, v in by_category("basis", reg).items()}


def known_knobs(tools=TOOLS):
    """Every environment name the tools actually read. COMPLETENESS only: the registry is the authority."""
    pat = re.compile(r'(?:os\.environ\.get|os\.getenv)\(\s*"([A-Z][A-Z_0-9]*)"|os\.environ\[\s*"([A-Z][A-Z_0-9]*)"\s*\]')
    out = set()
    for f in KNOB_FILES:
        path = os.path.join(tools, f)
        if not os.path.exists(path):
            continue
        for m in pat.finditer(open(path, errors="replace").read()):
            out.add(m.group(1) or m.group(2))
    return {n for n in out if not n.startswith("_")}


def knob_types(tools=TOOLS):
    """The registry as the older shape (type, default, note), so the evidence pack needs no change."""
    return {k: {"type": v["type"], "default": v.get("default", ""), "file": v.get("stage", ""),
                "note": v.get("description", "")[:120], "category": v.get("category"),
                "unit": v.get("unit", "")} for k, v in registry().items()}


def _scalar(v):
    return isinstance(v, (str, int, float, bool))


def validate(proposal, spec_template, graded=(), reg=None, max_arms=1, allow_repeat=False,
             best=None, worst=None):
    """Returns (ok, errors, arms). Every refusal names the rule and what it saw."""
    errs = []
    reg = reg if reg is not None else registry()
    run = spec_template.get("_runs", "pair")
    max_knobs = int(spec_template.get("_max_knobs", 1))
    metric = spec_template.get("_metric", "pairs")
    if not isinstance(proposal, dict):
        return False, ["the proposal is %s, not an object" % type(proposal).__name__], []
    stray = sorted(set(proposal) & SPEC_OWNS)
    if stray:
        errs.append("the proposal sets fields it does not own: %s. The board, the project and the passes come "
                    "from the template, not from the proposer" % ", ".join(stray))
    arms = proposal.get("arms")
    if not isinstance(arms, list) or not arms:
        return False, errs + ['no arms: expected {"arms": [{name, env, predict}], "why": [...]}'], []
    if len(arms) > max_arms:
        errs.append("%d arms proposed against a cap of %d for this run" % (len(arms), max_arms))
    seen = set()
    for i, arm in enumerate(arms):
        tag = "arm %d" % (i + 1)
        if not isinstance(arm, dict):
            errs.append("%s is not an object" % tag); continue
        extra = sorted(set(arm) - MODEL_OWNS)
        if extra:
            errs.append("%s carries fields the proposer does not own: %s" % (tag, ", ".join(extra)))
        name = arm.get("name")
        if not isinstance(name, str) or not SLUG.match(name) or len(name) > SLUG_MAX:
            errs.append("%s name %r is not a slug: it becomes the directory arm-<letter>-<name>, which arms.py "
                        "removes with rmtree, so it is lowercase %s of at most %d characters"
                        % (tag, name, SLUG.pattern, SLUG_MAX))
        elif name in seen:
            errs.append("%s repeats the name %r inside one proposal" % (tag, name))
        else:
            seen.add(name)
        env = arm.get("env")
        if not isinstance(env, dict) or not env:
            errs.append("%s sets no knobs: an arm with an empty env measures nothing" % tag)
            env = {}
        elif len(env) > max_knobs:
            errs.append("%s sets %d knobs (%s) and this run allows %d. ONE VARIABLE: two knobs in one arm and "
                        "the result names neither of them. A deliberate interaction experiment raises _max_knobs "
                        "in the template and owes a factorial design" % (tag, len(env), ", ".join(sorted(env)), max_knobs))
        for k, v in env.items():
            spec = reg.get(k)
            if spec is None:
                errs.append("%s sets %s, which is in no registry entry. A knob nobody registered is not a lever: "
                            "add it to agent/knobs.json with its category, or it cannot be proposed" % (tag, k))
                continue
            cat = spec.get("category")
            if cat == "reserved":
                errs.append("%s sets the RESERVED knob %s. %s. This belongs in "
                            "v2/docs/OWNER-DECISIONS-2026-09-11.md with its evidence, not in a job"
                            % (tag, k, spec.get("description", "")))
            elif cat == "basis":
                errs.append("%s sets %s, which is basis-locked: %s" % (tag, k, spec.get("description", "")))
            elif cat != "experiment":
                errs.append("%s sets %s, which is categorised %s in the registry: %s. It is not a routing lever, "
                            "so an arm on it measures nothing about the board"
                            % (tag, k, cat, spec.get("description", "")))
            elif spec.get("stage") not in STAGES.get(run, ("pair",)):
                errs.append("%s sets %s, which runs at the %r stage while this run is %r and executes %s. That "
                            "knob cannot act here: the arm would measure nothing and the null would read exactly "
                            "like a knob that does not pay"
                            % (tag, k, spec.get("stage"), run, " then ".join(STAGES.get(run, ("pair",)))))
            if not _scalar(v):
                errs.append("%s: %s is %s, and a knob value must be a scalar" % (tag, k, type(v).__name__))
                continue
            if len(str(v)) > 200:
                errs.append("%s: %s is %d characters" % (tag, k, len(str(v)))); continue
            t = (spec or {}).get("type", "")
            if t == "flag" and str(v).strip() not in ("0", "1"):
                errs.append("%s: %s is a FLAG the tool reads as `!= \"0\"`, so %r sets it ON. A flag takes the "
                            "string 1 or the string 0 and nothing else: false, False, off and no all arrive ON"
                            % (tag, k, v))
            elif t.startswith("enum:"):
                allowed = t.split(":", 1)[1].split(",")
                if str(v) not in allowed:
                    errs.append("%s: %s takes one of %s, not %r" % (tag, k, allowed, v))
            elif t in ("number", "integer"):
                try:
                    fv = float(v)
                    if t == "integer" and float(int(fv)) != fv:
                        errs.append("%s: %s is an integer knob and %r is not one" % (tag, k, v))
                except (TypeError, ValueError):
                    errs.append("%s: %s is a %s and %r is not one" % (tag, k, t, v))
        p = arm.get("predict")
        if not isinstance(p, dict):
            errs.append("%s carries no prediction. An arm nobody predicted cannot disappoint, so it cannot "
                        "teach anything, and the runner refuses it" % tag)
        else:
            m = p.get("metric", metric)
            if m != metric:
                errs.append("%s predicts %r while the judge grades %r. A row whose prose and mechanical meaning "
                            "disagree is worse than no row" % (tag, m, metric))
            op = p.get("op")
            if op not in OPS:
                errs.append("%s prediction operator %r is not one of %s" % (tag, op, sorted(OPS)))
            val = p.get("value")
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                errs.append("%s predicts %r, which is not a number" % (tag, val))
            else:
                of = spec_template.get("_denominator")
                if of and not (0 <= val <= of):
                    errs.append("%s predicts %s of a denominator of %s" % (tag, val, of))
                # falsifiability: it must be able to be wrong in a way that matters
                if op in UP and best is not None and val <= best:
                    errs.append("%s predicts %s %s on a board whose best graded row is %s: an arm that changes "
                                "nothing would meet it. For %s the value must beat the best measured row"
                                % (tag, op, val, best, op))
                if op in DOWN and worst is not None and val >= worst:
                    errs.append("%s predicts %s %s on a board whose worst graded row is %s: an arm that changes "
                                "nothing would meet it" % (tag, op, val, worst))
            basis = (p.get("basis") or "").strip()
            if len(basis) < 40:
                errs.append("%s gives a basis of %d characters. The basis is what makes a missed prediction "
                            "informative; 'it should help' is not one" % (tag, len(basis)))
            elif re.fullmatch(r"[^a-zA-Z]*%s[^a-zA-Z]*" % re.escape(str(p.get("value"))), basis or ""):
                errs.append("%s restates its own number as its basis" % tag)
        if not allow_repeat and isinstance(env, dict) and env:
            sig = json.dumps({k: str(v) for k, v in sorted(env.items())}, sort_keys=True)
            if sig in set(graded):
                errs.append("%s repeats knobs already graded in the ledger (%s). A repeat is not learning; "
                            "pass --allow-repeat to measure reproducibility on purpose" % (tag, sig))
    return (not errs), errs, arms


def build_spec(proposal, spec_template, arms):
    """The runnable arms.py spec: the template's own fields, plus the three the proposer owns."""
    spec = {k: v for k, v in spec_template.items() if not k.startswith("_")}
    spec["_why"] = ["Proposed by tier 2 on %s." % spec_template.get("_stamp", "")] + list(proposal.get("why") or [])
    spec["runs"] = spec_template.get("_runs", "pair")
    spec["arms"] = [{"name": a["name"], "env": a.get("env", {}), "predict": a["predict"]} for a in arms]
    return spec


def main(a):
    """schema.py <proposal.json> <template.json> prints the refusals, so a fixture can prove each fires."""
    if len(a) < 2:
        print(__doc__); return 2
    ok, errs, arms = validate(json.load(open(a[0])), json.load(open(a[1])))
    print("schema: %s" % ("ACCEPTED %d arm(s)" % len(arms) if ok else "REFUSED"))
    for e in errs:
        print("  REFUSED: %s" % e)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
