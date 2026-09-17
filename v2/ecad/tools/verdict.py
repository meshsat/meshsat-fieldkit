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


_TOOLS_CACHE = {}


def _tools():
    """The git head and the content hash of the tools tree, once per process (subprocess git, no import of arms.py)."""
    if _TOOLS_CACHE: return dict(_TOOLS_CACHE)
    here = os.path.dirname(os.path.abspath(__file__)); out = {"git_head": "", "tools_tree_sha": ""}
    try:
        out["git_head"] = subprocess.run(["git", "-C", here, "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip()[:12]
        h = hashlib.sha256()
        for root, dirs, files in os.walk(here):
            dirs[:] = sorted(d for d in dirs if d not in ("__pycache__", "out", "tests"))
            for f in sorted(files):
                if f.endswith((".py", ".sh", ".json")): h.update(open(os.path.join(root, f), "rb").read())
        out["tools_tree_sha"] = h.hexdigest()[:16]
    except Exception: pass
    _TOOLS_CACHE.update(out); return dict(out)


_RULESET = [None]


def _rule_set_fingerprint():
    """The identity of the rule registry this verdict was taken under (MESHSAT-862, 16 September 2026). Evidence
    that does not name its rule set cannot be shown to be current, and rules_status.py treats it as stale."""
    if _RULESET[0] is None:
        # BaseException, not Exception, and the difference is a live defect found on 16 September: rules_lib
        # raises SystemExit when PyYAML is absent, SystemExit does not descend from Exception, and so a gate on
        # a host without PyYAML EXITED at the moment it wrote its verdict. It printed its result, wrote no
        # verdict file and returned 1, which reads as a failing board. Stamping the rule set is evidence about
        # the verdict; it can never be allowed to decide whether the verdict exists.
        try:
            import rules_lib as _r; _RULESET[0] = _r.fingerprint()
        except BaseException as e: _RULESET[0] = ""; _RULESET_WHY[0] = "%s: %s" % (type(e).__name__, str(e)[:90])
    return _RULESET[0]


_RULESET_WHY = [""]
_BY_TOOL = [None]


def _rules_for_tool(tool):
    """Which rule ids this verdict decides, read from the coverage map rather than typed into twenty gates.
    The coverage map names, per rule, the verdict that carries its evidence; this is that mapping inverted,
    so the registry stays the single source and a gate cannot drift from it."""
    if _BY_TOOL[0] is None:
        m = {}
        try:
            import rules_lib as _r
            cov = (_r._yaml().safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                          "pcb_rules_coverage.yaml"))) or {}).get("coverage", {})
            for rid, c in cov.items():
                # A RULE MAY NAME SEVERAL VERDICTS, comma separated: a placement is judged by the DRC on the
                # placed board AND by the escape-fan predictor, a part by its code AND by asking the fabricator.
                # Splitting here is what makes each of those tools able to say which rule it decides.
                for name in str(((c or {}).get("verification") or {}).get("verdict") or "").split(","):
                    name = name.strip()
                    if name: m.setdefault(name, []).append(rid)
        except BaseException: m = {}          # as above: a coverage map this host cannot read is not a failure of the gate
        _BY_TOOL[0] = m
    m = _BY_TOOL[0]; out = set(m.get(tool, []))
    for name, ids in m.items():                      # check_pcb_<letter> and friends: the union, never the first match
        if "<letter>" in name and tool.startswith(name.split("<letter>")[0]): out |= set(ids)
    return sorted(out)


def _policy():
    d = {}
    try:
        import hardset as _h; d["hard_types"] = len(_h.HARD_POST)
    except Exception: pass
    fp = _rule_set_fingerprint()
    if fp: d["rule_set_fingerprint"] = fp
    elif _RULESET_WHY[0]:
        # Say WHY it is missing. Unstamped evidence is treated as stale by rules_status, and a reader has to be
        # able to tell "written before the registry existed" from "written on a host that could not read it".
        d["rule_set_fingerprint_absent"] = _RULESET_WHY[0]
    return d


def _with_board(inputs):
    """Record the board this gate was given, when it did not say so itself.

    A VERDICT THAT DOES NOT NAME ITS BOARD CAN ONLY BE ATTRIBUTED BY THE DIRECTORY IT SITS IN (17 September
    2026), and that is how a reading about one board came to answer for another: `rules_status` compares
    `inputs.board` with the boards the project directory holds and simply cannot check a verdict that names
    none. Twenty gates take the board as their first argument and pass it to nobody; this records what the
    process was actually given, with its sha256 and the fact that it was read off the command line, so a
    verdict is attributable without every gate having to learn a new argument. A gate that names its board
    itself is left exactly as it wrote it."""
    if "board" in inputs: return inputs      # the gate said which board, or said explicitly that it judges none
    try:
        import hashlib
        for a in sys.argv[1:]:
            if not isinstance(a, str) or not a.endswith(".kicad_pcb"): continue
            if not os.path.isfile(a): continue
            with open(a, "rb") as f:
                h = hashlib.sha256()
                for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
            inputs["board"] = {"path": os.path.basename(a), "sha256_16": h.hexdigest()[:16], "from": "argv"}
            break
    except BaseException:
        pass                                   # a verdict is never lost because its identity could not be read
    return inputs


def write(tool, result, counts=None, denominator=None, evidence=None, inputs=None, note="", out_dir=None,
          quiet=False, advisory=None, rules=None, applicable=True, missing_input=None):
    """Write out/<tool>.verdict.json and return the exit code that equals the verdict.

    `advisory` (or VERDICT_ADVISORY=1 in the environment) marks a verdict that is a MEASUREMENT for the record and
    not a bar: it is written, listed and hashed like any other, and `collect` leaves it out of the stage's worst.
    15 September 2026 (MESHSAT-862): B19's pre stage printed PREROUTE-DONE OK and routeflow read GATE_BLOCKED,
    because the pre-route DRC on the pair copper BEFORE the prune (hard 15, the number the prune acts on) and the
    placement predictor the board declares as a report had each written a FAIL the collector took as the stage's.

    `applicable=False` says the rule this tool decides does not apply to THIS board: the board carries none of
    the thing the rule is about. It stays INCONCLUSIVE, because absence is never a pass and a gate that could
    not judge must never read as one, and it carries `applicable: false` so a collector can tell "this board has
    no crystal" apart from "the crystal check did not run". Board P's route was blocked on 16 September 2026 by
    exactly that confusion: the pre-route gate refused the board because its crystal check and its exposed-port
    check both said, correctly, that there was nothing of theirs on the board. The registry remains the
    authority on applicability; this field is the tool reporting the board fact it observed, and
    `rules_status.py` compares the two.

    `missing_input` says the thing this tool judges was NOT THERE to be judged: no rotation table in this tree,
    no order folder, no netlist. It is a sentence, and it makes two things true at once. The verdict is
    INCONCLUSIVE, because a tool that could not read its input has not judged; and the record carries the
    declaration, so a reader can tell "there was nothing to check" apart from "everything checked was fine".

    WHY IT IS A FIELD AND NOT A NOTE (17 September 2026). A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE
    TAKEN WITH MORE is this project's own rule and it has been re-learnt five times: the cross-board contracts
    at both ends, the rotation table, the energy chain, the placement carry, and today `doc_provenance`, whose
    reading taken in a sweep tree that holds NO release folder at all (0 documents of 0 folders) is newer than
    the runner's reading of the seven real ones and stands in front of it on four boards. Each of those was
    fixed where it was found, which is four fixes and one that was missed. Written down here, a consumer can
    hold the rule once for every tool: `rules_status` prefers the reading that HAD its input, whatever the
    timestamps say, and a tool declares the absence rather than each reader guessing it from a zero.

    `result` must be PASS, FAIL or INCONCLUSIVE; anything else is a usage error, because a verdict this module does not
    recognise must not resolve to a pass by falling through."""
    if result not in CODE:
        print("verdict: %s reported %r, which is not a verdict" % (tool, result)); return USAGE
    # A tool whose input was absent has not judged, whatever it was about to say.
    if missing_input and result != INCONCLUSIVE:
        print("verdict: %s declares its input absent (%s) and reported %s; a judgement needs the thing it "
              "judges, so this is INCONCLUSIVE" % (tool, str(missing_input)[:70], result))
        result = INCONCLUSIVE
    # `out` beside the board is the house default; a driver that runs a gate from elsewhere sets VERDICT_DIR
    # rather than teaching every gate an argument it would otherwise never take.
    out_dir = out_dir or os.environ.get("VERDICT_DIR") or "out"
    if advisory is None: advisory = os.environ.get("VERDICT_ADVISORY", "0") not in ("0", "")
    rec = {
        "tool": tool,
        "version": _version(),
        "ts": now(),
        "tools": _tools(),         # the code that judged: git head and the tools tree's content hash (a StageResult field, 15 Sep 2026)
        "policy": _policy(),       # the hard set the judgement is under, so a verdict from an older policy is not read as today's
        "verdict": result,
        "advisory": bool(advisory),
        "applicable": bool(applicable),
        "counts": dict(counts or {}),
        "denominator": denominator,
        "inputs": _with_board(dict(inputs or {})),
        "evidence": list(evidence or [])[:50],
        "note": note,
        # The sentence saying the input was not there, or None. A reader prefers a verdict that had
        # its input over one that says it did not, whatever the two timestamps are.
        "missing_input": (str(missing_input) if missing_input else None),
        # THE RULE IDS THIS VERDICT DECIDES (MESHSAT-862, 16 September 2026). A gate with no rule id decides
        # something the registry does not know about, which is how this project came to enforce rules it had
        # never written down; tests/test_rule_gate_mapping.py holds the list.
        "rules": sorted(set(rules or _rules_for_tool(tool))),
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
        print("verdict: %-22s %-12s%s%s%s%s" % (tool, result, d, c, (" (advisory: a measurement, not a bar)" if advisory else ("" if applicable else " (this rule does not apply to this board)")), (" | " + note) if note else ""))
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


def now():
    """The one timestamp format in this channel: UTC, `2026-09-11T13:38:13Z`.

    It is a function rather than an inline strftime because a caller needs to build a comparable horizon for
    `collect(since=...)`, and the first version of that horizon passed routeflow's own `now()`, which is LOCAL
    time with a space separator. The string compare then put every record on the wrong side of it and the
    horizon excluded nothing at all (11 September 2026)."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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
    for rec in found.values():
        if rec.get("advisory"): continue   # a measurement for the record; it never decides the stage
        if rec.get("applicable") is False: continue   # the board carries none of what this rule is about
        worst = max(worst, CODE.get(rec.get("verdict"), CODE[INCONCLUSIVE]))
    if missing: worst = max(worst, CODE[INCONCLUSIVE])
    if not any((not r.get("advisory")) and r.get("applicable") is not False for r in found.values()):
        worst = max(worst, CODE[INCONCLUSIVE])   # only advisories and inapplicable rules is nothing judged
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
