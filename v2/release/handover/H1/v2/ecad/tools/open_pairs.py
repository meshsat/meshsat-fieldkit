#!/usr/bin/env python3
"""What every open rule-board pair is waiting on, classified from the registry rather than by hand
(MESHSAT-862, 19 September 2026).

The readiness number says how many of the 333 applicable pairs are verified. It does not say what the rest
are waiting on, and that question has been answered by hand four times in three days (17 September 16:25,
17 September 17:50, 18 September, and this morning board by board). A hand count goes stale the moment a
route lands, and two of the four disagreed with each other about which rules were "engineering". So the
classification is computed here, from data that already exists, and the document is its rendering.

The ladder, in priority order, and why it is that order:

  DECISION         an OPEN decision in pcb_decisions.yaml names this rule and this board in its `blocks` map.
                   This wins over everything below it INCLUDING a measured failure, because the ACTION that
                   moves the pair is the ruling; the measurement is reported beside it and never lost.
  AUTHORITY        the coverage map's maturity is SOURCE_UNVERIFIED: the limit may be right and nobody can
                   check it. Not this session's to close.
  DECISION_UNCLAIMED  maturity OWNER_DECISION_REQUIRED and NO open decision claims the pair. This is a hole
                   in the registry, not a state of the board: the page names it so it is fixed rather than
                   read as "a decision is open" by a reader who then cannot find which one.
  NO_INSTRUMENT    maturity OPEN, DOCUMENTED_ONLY or GENERATED_ONLY: nothing verifies it.
  MISSING_INPUT    the deciding verdict declared its own input absent (`missing_input`), which since
                   17 September is how a reading taken with less input refuses to stand.
  MEASURED_FAILURE the tool looked and the board failed. The only category that is engineering work here.
  NOT_JUDGED       anything else INCONCLUSIVE, carrying the reading's own words.

`measured` travels beside the category and is true whenever the row's result is FAIL, so the count of
measured failures is the same number whichever cut of the table is read.

  open_pairs.py                 write out/open_pairs.json from out/rule-audit/*.json
  open_pairs.py --print         the same, to stdout, grouped
"""
import os, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

DECISION = "DECISION"
AUTHORITY = "AUTHORITY"
DECISION_UNCLAIMED = "DECISION_UNCLAIMED"
NO_INSTRUMENT = "NO_INSTRUMENT"
MISSING_INPUT = "MISSING_INPUT"
MEASURED_FAILURE = "MEASURED_FAILURE"
VENDOR_WAIT = "VENDOR_WAIT"
OWNER_WORK = "OWNER_WORK"
NOT_JUDGED = "NOT_JUDGED"

ORDER = (DECISION, DECISION_UNCLAIMED, AUTHORITY, NO_INSTRUMENT, MISSING_INPUT, MEASURED_FAILURE,
         VENDOR_WAIT, OWNER_WORK, NOT_JUDGED)

# A decision that has been ruled or closed claims nothing: its blocks map is history. Only these count.
OPEN_STATUS = ("open", "asked", "reopened")

HEADLINE = {
    DECISION: "an owner decision by name",
    DECISION_UNCLAIMED: "a rule that says a decision is open while no decision claims it",
    AUTHORITY: "an authority this project does not have",
    NO_INSTRUMENT: "nothing verifies it",
    MISSING_INPUT: "an input the reading declared absent",
    MEASURED_FAILURE: "the tool looked and the board failed",
    VENDOR_WAIT: "a fabricator or a standards body, and nobody here",
    OWNER_WORK: "work only the owner or the ordering session can do",
    NOT_JUDGED: "not judged, for the reason the reading gives",
}


def decisions(path=None):
    """The open decisions, as {(rule, letter): (n, title)}. A decision with no `blocks` map claims nothing."""
    import rules_lib as R
    y = R._yaml()
    path = path or os.path.join(HERE, "pcb_decisions.yaml")
    with open(path) as fh: ds = (y.safe_load(fh) or {}).get("decisions") or []
    out = {}
    for d in ds:
        if str(d.get("status", "")).lower() not in OPEN_STATUS: continue
        for rid, letters in (d.get("blocks") or {}).items():
            for letter in (letters or []):
                out.setdefault((rid, str(letter)), (d.get("n"), d.get("title", "")))
    return out


def executions(cov=None):
    """{rule: who EXECUTES its remediation}, from the coverage map (19 September 2026).

    The ladder above answers from the registry's maturity and the verdict's own fields, and it left two kinds
    of pair in the "not judged" bucket that are not unattributed at all: VIA-002 on board P waits on the
    fabricator publishing its annular rows at 2 oz, and DFA-001 on every board waits on the assembler's own
    2D preview, which lives behind a login this repo forbids the runner to use. Both are recorded in the
    coverage map already, as `remediation.execution`, and the ETA has been reading them for days. A register
    whose job is to say what is REACHABLE must say that neither is."""
    import rules_status as S
    cov = cov if cov is not None else S.coverage()
    out = {}
    for rid, e in (cov or {}).items():
        out[rid] = ((e or {}).get("remediation") or {}).get("execution")
    return out


def _missing_input(row):
    """What the deciding verdict said it was missing, or None. The row carries the verdict's path as evidence."""
    p = row.get("evidence")
    if not p or not str(p).endswith(".json") or not os.path.exists(p): return None
    try:
        with open(p) as fh: v = json.load(fh)
    except Exception:
        return None
    mi = v.get("missing_input")
    if not mi: return None
    return str(mi)


def classify(row, letter, claims, execs=None):
    """One open pair. Returns {category, detail, measured}; a PASS or NOT_APPLICABLE row returns None."""
    if row.get("result") not in ("FAIL", "INCONCLUSIVE"): return None
    rid = row.get("rule"); maturity = row.get("maturity")
    measured = row.get("result") == "FAIL"
    claim = claims.get((rid, letter))
    if claim:
        n, title = claim
        return dict(category=DECISION, detail="decision %s: %s" % (n, title), measured=measured, decision=n)
    if maturity == "OWNER_DECISION_REQUIRED":
        return dict(category=DECISION_UNCLAIMED, detail=row.get("why", ""), measured=measured, decision=None)
    if maturity == "SOURCE_UNVERIFIED":
        return dict(category=AUTHORITY, detail=row.get("why", ""), measured=measured, decision=None)
    if maturity in ("OPEN", "DOCUMENTED_ONLY", "GENERATED_ONLY"):
        return dict(category=NO_INSTRUMENT, detail=row.get("why", ""), measured=measured, decision=None)
    mi = _missing_input(row)
    if mi and not measured:
        return dict(category=MISSING_INPUT, detail=mi, measured=False, decision=None)
    if measured:
        return dict(category=MEASURED_FAILURE, detail=row.get("why", ""), measured=True, decision=None)
    ex = (execs or {}).get(rid)
    if ex == "VENDOR_OR_STANDARD_WAIT":
        return dict(category=VENDOR_WAIT, detail=row.get("why", ""), measured=False, decision=None)
    if ex == "OWNER":
        return dict(category=OWNER_WORK, detail=row.get("why", ""), measured=False, decision=None)
    return dict(category=NOT_JUDGED, detail=row.get("why", ""), measured=False, decision=None)


def audits(out_dir=None):
    """Every board's audit, newest on disk, as {letter: {board, rows}}."""
    out_dir = out_dir or os.path.join(os.path.dirname(HERE), "out", "rule-audit")
    found = {}
    for p in sorted(glob.glob(os.path.join(out_dir, "*.json"))):
        letter = os.path.basename(p)[:-5]
        if "." in letter: continue          # rules_status.verdict.json and friends are not boards
        try:
            with open(p) as fh: d = json.load(fh)
        except Exception:
            continue
        rows = d.get("rows")
        if not isinstance(rows, list): continue
        found[letter] = dict(board=d.get("board") or d.get("subject"), rows=rows, path=p)
    return found


def collect(out_dir=None, decisions_path=None):
    claims = decisions(decisions_path)
    execs = executions()
    data = audits(out_dir)
    pairs = []
    for letter in sorted(data):
        for row in data[letter]["rows"]:
            c = classify(row, letter, claims, execs)
            if c is None: continue
            c.update(board=letter, rule=row.get("rule"), release_effect=row.get("release_effect"),
                     result=row.get("result"), phase=row.get("verification_phase"),
                     evidence=row.get("evidence"))
            pairs.append(c)
    # ONE SET-LEVEL READING IS NOT SEVEN FAILURES (19 September 2026). OUT-001 and DFA-001 are decided by a
    # verdict written ONCE for the whole set (`final_gate`, `assembly_set` in v2/ecad/out/), while PI-003 and
    # the rest read each board's own phase directory. Counting pairs is right, because a pair is what a board
    # has to satisfy; reporting 43 measured failures without saying that seven of them are one gate's single
    # answer overstates how many separate things are wrong. The test is the evidence PATH, which the audit
    # already carries: a path that serves more than one board is one reading.
    _by_path = {}
    for p in pairs:
        if p.get("evidence"): _by_path.setdefault(p["evidence"], set()).add(p["board"])
    shared = {k for k, v in _by_path.items() if len(v) > 1}
    for p in pairs:
        p["set_reading"] = bool(p.get("evidence") in shared)
    counts = {k: sum(1 for p in pairs if p["category"] == k) for k in ORDER}
    _m = [p for p in pairs if p["measured"]]
    return dict(pairs=pairs, counts=counts, open=len(pairs),
                measured=len(_m),
                measured_distinct=len({p.get("evidence") or (p["rule"], p["board"]) for p in _m}),
                set_readings=sorted({(p["rule"], len(_by_path[p["evidence"]])) for p in pairs
                                     if p.get("set_reading")}),
                measured_claimed=sum(1 for p in pairs if p["measured"] and p["category"] == DECISION),
                boards=sorted(data), decisions=sorted({p["decision"] for p in pairs if p.get("decision")}))


def main(argv):
    res = collect()
    out = os.path.join(os.path.dirname(HERE), "out", "open_pairs.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as fh: json.dump(res, fh, indent=1, sort_keys=True)
    print("open_pairs: %d open pair(s) over %d board(s); %d measured failure(s) which are %d distinct reading(s), "
          "%d of them claimed by an open decision"
          % (res["open"], len(res["boards"]), res["measured"], res["measured_distinct"], res["measured_claimed"]))
    for rid, n in res["set_readings"]:
        print("  %-9s one set-level reading, counted on %d board(s)" % (rid, n))
    for k in ORDER:
        if res["counts"][k]: print("  %-19s %3d   %s" % (k, res["counts"][k], HEADLINE[k]))
    if "--print" in argv:
        for k in ORDER:
            rows = [p for p in res["pairs"] if p["category"] == k]
            if not rows: continue
            print("\n== %s (%d): %s" % (k, len(rows), HEADLINE[k]))
            for p in rows:
                print("   %-9s %-3s %-12s %s" % (p["rule"], p["board"], p["result"], str(p["detail"])[:90]))
    return 0


if __name__ == "__main__":
    import verdict
    sys.exit(verdict.guard("open_pairs", main, sys.argv[1:]))
