#!/usr/bin/env python3
"""The fail-closed gate between a proposal and anything that runs (MESHSAT-862, 12 September 2026).

Tier 2 proposes and never actuates. That sentence is only worth something if something mechanical
stands between the proposal and the runner, so this is that thing, and it is deliberately narrow:

  * THE MODEL OWNS THREE FIELDS AND NOTHING ELSE: the arm's name, its env knobs and its written
    prediction. The board, the letter, the source project, the placed board, the passes and the
    timeout are filled in here from `boards/<letter>.json` and the spec template. A proposal that
    carries any of those is REFUSED rather than stripped, because a model that tried to choose its
    own board is telling you something you want to see in a verdict file, not silently correct.
  * A KNOB THE TOOL DOES NOT READ IS REFUSED. The authority is `pair_preroute.py` itself, parsed,
    never the knob document, which can drift. An arm on a knob nobody reads produces a null result
    that reads exactly like a knob that does not pay, and this project has already spent a day on
    one of those (`bypass_place.py`, which no chain ran, 9 September).
  * RESERVED KNOBS ARE REFUSED WITH THEIR REASON and routed to the owner's decisions file. The
    never-auto floor is checked before anything else, the way `reserved.py` orders it.
  * BASIS-LOCKED KNOBS ARE REFUSED. `PAIR_VENV`, `PAIR_FAST_SEARCH` and `PAIR_FAST_STUBS` choose
    which kernel runs. They are proved equivalent, so an arm that moves them measures the clock and
    not the board, and its row is not comparable with any other row.
  * AN ARM NAME BECOMES A DIRECTORY that `arms.py` removes with `shutil.rmtree`. So the name must be
    a slug. This is not a hypothetical: the name is interpolated straight into a path.
  * A REPEAT IS NOT LEARNING. An arm whose knobs and values have already been graded in the ledger
    is refused unless the caller asks for a repeat on purpose.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)

MODEL_OWNS = {"name", "env", "predict", "why"}
SPEC_OWNS = {"board", "letter", "source_project", "placed", "passes", "timeout_s", "ecad", "tools_sha"}
SLUG = re.compile(r"^[a-z0-9][a-z0-9_]*$")
SLUG_MAX = 32
OPS = {">=", ">", "==", "<=", "<"}

# Knobs nobody may set automatically, with the reason and the reserved class they belong to.
# These mirror the classes of tools/reserved.json; a proposal that wants one is evidence for the
# owner's decisions file, never a job.
RESERVED_KNOBS = {
    "PAIR_INNER":       "pair class geometry: it sets the inner-layer width and gap, which is an impedance target (reserved.json: impedance targets and pair class geometry)",
    "PAIR_INNER_GAP":   "pair class geometry: the intra-pair gap is an impedance target and at 0.09 mm it also breaks KiCad's own clearance rule, so it is a fabrication decision",
    "PAIR_INNER_WIDTH": "pair class geometry: track width against the stackup is an impedance target",
    "PAIR_LAYERS":      "a pair moved to an inner layer becomes a stripline and needs its own geometry, which is reserved; 32.102 measured every impedance-correct variant at or below the two-layer number",
    "PAIR_HOP_LAYERS":  "same as PAIR_LAYERS: it decides which layers a pair may change on, and an inner hop is a stripline segment",
}

# Knobs that change WHICH implementation runs rather than what the board is asked. Proved equivalent,
# so moving them measures the clock; a row that moves them cannot be compared with one that does not.
BASIS_KNOBS = {
    "PAIR_VENV":        "chooses the numba venv or the plain kernel; 13x the wall time, 0 of 7,706 items different",
    "PAIR_FAST_SEARCH": "the compiled corridor search, proved identical by pairsearch selftest",
    "PAIR_FAST_STUBS":  "the compiled stub search, proved identical on B19 (0 of 7,706 items differ)",
    "PAIR_MAP_CHECK":   "an equivalence check, not a lever: it makes the pass slower and changes nothing",
    "_PAIR_REEXEC":     "internal re-exec marker, never a knob",
}


def known_knobs(tools=TOOLS):
    """Every environment name the tools actually read. The source is the source, never the document."""
    pat = re.compile(r'(?:os\.environ\.get|os\.getenv)\(\s*"([A-Z][A-Z_0-9]*)"|os\.environ\[\s*"([A-Z][A-Z_0-9]*)"\s*\]')
    out = set()
    for f in ("pair_preroute.py", "gen_pcb_b3.py", "pairsearch.py"):
        p = os.path.join(tools, f)
        if not os.path.exists(p):
            continue
        for m in pat.finditer(open(p, errors="replace").read()):
            out.add(m.group(1) or m.group(2))
    return out


def knob_types(tools=TOOLS):
    """Each knob's TYPE, default and the comment beside it, read from the line that reads it.

    A knob name on its own is not enough to reason about, and tier 2 proved it: the first arm an
    automated proposer ever wrote for board B set `PAIR_OWN_CLEAR=0.09`, reasoning carefully about
    millimetres, and the tool reads that name as a FLAG (`!= "0"`), so 0.09 means exactly what the
    default means and the arm could only ever measure nothing. The type is in the source, so it is
    read from the source (12 September 2026).
    """
    out = {}
    pat = re.compile(r'(?P<pre>[A-Za-z_]*\s*\(?\s*)?os\.environ\.get\(\s*"(?P<name>[A-Z][A-Z_0-9]*)"'
                     r"(?:\s*,\s*(?P<dflt>\"[^\"]*\"|'[^']*'))?\s*\)(?P<post>[^\n#]*)(?:#\s*(?P<why>.*))?")
    for f in ("pair_preroute.py", "gen_pcb_b3.py", "pairsearch.py"):
        path = os.path.join(tools, f)
        if not os.path.exists(path):
            continue
        for line in open(path, errors="replace"):
            m = pat.search(line)
            if not m or m.group("name") in out:
                continue
            pre, post = (m.group("pre") or ""), (m.group("post") or "")
            if "float(" in line[:m.start() + len(pre)]:
                kind = "number"
            elif "int(" in line[:m.start() + len(pre)]:
                kind = "integer"
            elif '!= "0"' in post or '== "1"' in post or '!= "0"' in line[m.end() - len(post):]:
                kind = "flag, 1 or 0 only: any other value reads as ON"
            elif '== "1"' in line or '.split(' in post:
                kind = "flag or list, read the comment"
            else:
                kind = "string"
            d = (m.group("dflt") or "").strip("\"'")
            out[m.group("name")] = {"type": kind, "default": d, "note": (m.group("why") or "").strip()[:120]}
    return out


def _scalar(v):
    return isinstance(v, (str, int, float, bool)) and not isinstance(v, type(None))


def validate(proposal, spec_template, graded=(), knobs=None, max_arms=1, allow_repeat=False, types=None):
    """Returns (ok, errors, arms). Every refusal names the rule and what it saw."""
    errs, knobs = [], (knobs if knobs is not None else known_knobs())
    types = knob_types() if types is None else types
    if not isinstance(proposal, dict):
        return False, ["the proposal is %s, not an object" % type(proposal).__name__], []
    stray = sorted(set(proposal) & SPEC_OWNS)
    if stray:
        errs.append("the proposal sets fields it does not own: %s. The board, the project and the passes come "
                    "from boards/<letter>.json, not from the proposer" % ", ".join(stray))
    arms = proposal.get("arms")
    if not isinstance(arms, list) or not arms:
        return False, errs + ["no arms: expected {\"arms\": [{name, env, predict}], \"why\": [...]}"], []
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
        for k, v in env.items():
            if k in RESERVED_KNOBS:
                errs.append("%s sets the RESERVED knob %s. %s. This belongs in "
                            "v2/docs/OWNER-DECISIONS-2026-09-11.md with its evidence, not in a job" % (tag, k, RESERVED_KNOBS[k]))
            elif k in BASIS_KNOBS:
                errs.append("%s sets %s, which is basis-locked: %s" % (tag, k, BASIS_KNOBS[k]))
            elif k not in knobs:
                errs.append("%s sets %s, which no tool in this tree reads. A knob nobody reads returns a null "
                            "result that reads exactly like a knob that does not pay" % (tag, k))
            if not _scalar(v):
                errs.append("%s: %s is %s, and a knob value must be a scalar" % (tag, k, type(v).__name__))
            elif len(str(v)) > 200:
                errs.append("%s: %s is %d characters" % (tag, k, len(str(v))))
            else:
                # A FLAG given a number reads as ON, which is usually its default, so the arm measures
                # nothing and its result is indistinguishable from "this knob does not pay". The first arm
                # an automated tier 2 wrote for board B did exactly this: PAIR_OWN_CLEAR=0.09, reasoned
                # about in millimetres, read by the tool as a boolean (12 September 2026).
                t = (types.get(k) or {}).get("type", "")
                if t.startswith("flag") and str(v).strip() not in ("0", "1", "True", "False", "true", "false"):
                    errs.append("%s: %s is a FLAG the tool reads as `!= \"0\"`, so %r sets it ON, which is %s. "
                                "A flag takes 1 or 0. If you meant a threshold, this is not the knob for it"
                                % (tag, k, v, "its default" if (types.get(k) or {}).get("default") != "0"
                                   else "the opposite of its default"))
        p = arm.get("predict")
        if not isinstance(p, dict):
            errs.append("%s carries no prediction. An arm nobody predicted cannot disappoint, so it cannot "
                        "teach anything, and the runner refuses it" % tag)
        else:
            if p.get("op") not in OPS:
                errs.append("%s prediction operator %r is not one of %s" % (tag, p.get("op"), sorted(OPS)))
            val = p.get("value")
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                errs.append("%s predicts %r, which is not a number" % (tag, val))
            else:
                of = spec_template.get("_denominator")
                if of and not (0 <= val <= of):
                    errs.append("%s predicts %s of a denominator of %s" % (tag, val, of))
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
