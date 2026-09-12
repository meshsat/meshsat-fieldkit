#!/usr/bin/env python3
"""The evidence pack tier 2 is given, and nothing else (MESHSAT-862, 12 September 2026).

The plan's tier 2 reads verdict JSONs and the design record, never a log. That is not tidiness: every
wrong reading this project has recorded came from prose. The five-short-opens reading of C10 came from
a tool's own summary line; "the staircase costs five pairs" came from two runs under different box
loads; "the pairs are a floor-plan problem" came from a classification nobody had counted. So what
goes in here is counted artefacts with denominators, plus the parts of the record that carry rulings.

What the pack contains, and why each piece is in it:

  * THE BOARD'S OWN DECLARATIONS (`boards/<letter>.json`), because a value there is a measurement with
    its `_why` beside it, and a proposal that ignores what the board already declares is not aimed.
  * THE GRADED LEDGER, every previous arm with its prediction, its outcome and its grade. This is the
    only thing that stops the loop proposing what has already been measured, and it is also the
    honest record of how often a written prediction was wrong here, which is most of the time.
  * THE MEASURED KNOB TABLE from the knob document, which is the design record for this tool.
  * THE FAILURE PROFILE as counts (`pair_report.py --json`), so "what stops a pair" is a number per
    reason and per part rather than a story.
  * THE KNOBS IT MAY PROPOSE, from the typed registry `agent/knobs.json` and its `experiment` category,
    filtered to the stage this run executes. Reading a name from the source told us the name exists,
    never that it is a lever, and the red team was right that this reversed the authority.
  * THE STANDING LAW measured on 12 September: on a greedy pass with no rip-up, removing a bar moves
    the failure rather than the pair, unless the bar was the last one. Six arms measured it.
"""
import os, re, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ECAD = os.path.dirname(TOOLS)
DOCS = os.path.join(os.path.dirname(ECAD), "docs")

LAW = ("Measured on 12 September 2026 over six arms: on a greedy pass with no rip-up, removing a bar moves the "
       "failure rather than the pair, UNLESS the bar was the last one. Six knobs each removed a real, named bar "
       "(the via arithmetic, the contention order, the end emissions, the via candidates, the leg retry, the leg "
       "cover) and five of the six laid zero extra pairs because the next bar was waiting one step along. The one "
       "that paid was a PLACEMENT change, the couple gap, which removed the last bar for the pairs it touched.")


def _read(path, limit=None):
    if not os.path.exists(path):
        return ""
    t = open(path, errors="replace").read()
    return t[:limit] if limit else t


def measured_table(path=None):
    """The '## Measured' rows of the knob document: the design record for this tool, as text."""
    txt = _read(path or os.path.join(DOCS, "PAIR-PREROUTER-KNOBS.md"))
    if "## Measured" not in txt:
        return ""
    body = txt.split("## Measured", 1)[1]
    return body.split("\n## ", 1)[0].strip()


class EvidenceCorrupt(Exception):
    """The ledger this evidence would be drawn from does not verify. Never a partial pack."""


def graded_rows(ledger_paths, verify=True):
    """Every arm row ever appended, oldest first, from a ledger whose CHAIN VERIFIES FIRST.

    The chain was tamper-evident only when somebody called the verifier, and the agent is the one
    consumer that decides things from it: which experiments are already measured, what the evidence pack
    says, whether a proposal is a repeat. A malformed row used to be skipped silently, which is exactly
    how a measured arm disappears and gets proposed again (red team, 12 September 2026). A broken chain
    is EVIDENCE_CORRUPT and stops the cycle; it does not yield a partially reconstructed pack.
    """
    sys.path.insert(0, TOOLS)
    import ledger as _ledger
    rows = []
    for p in ledger_paths:
        if not os.path.exists(p):
            continue
        if verify:
            ok, _n, problems = _ledger.verify(p)
            if not ok:
                raise EvidenceCorrupt("%s does not verify: %s" % (p, "; ".join(map(str, problems))[:300]))
        for n, line in enumerate(open(p, errors="replace"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except ValueError:
                raise EvidenceCorrupt("%s line %d is not JSON, and a skipped row is a measurement that "
                                      "disappears from the evidence" % (p, n))
            rows.append(r.get("rec", r))
    return rows


def signatures(rows):
    """The knob signatures already graded, so the validator can refuse a repeat."""
    out = set()
    for r in rows:
        env = r.get("env") or {}
        if env:
            out.add(json.dumps({k: str(v) for k, v in sorted(env.items())}, sort_keys=True))
    return out


def summarise_rows(rows, limit=40):
    """One line per graded arm. Deliberately terse: the pack is evidence, not a narrative."""
    out = []
    for r in rows[-limit:]:
        p = r.get("predict") or {}
        out.append("%-16s %-6s of %-5s  %-11s predicted %s %-5s  knobs %s  basis: %s" % (
            r.get("arm", "?"), r.get("pairs", "-"), r.get("of", "-"), r.get("verdict", "-"),
            p.get("op", ""), p.get("value", ""), json.dumps(r.get("env", {}))[:70],
            (p.get("basis") or "")[:90]))
    return "\n".join(out)


def pack(letter, board_json=None, profile=None, ledgers=(), knobs=None, extra=(), spec_template=None):
    """Everything tier 2 sees, as one dict. Nothing here is a log and nothing here is a secret."""
    import schema
    bj = board_json or os.path.join(TOOLS, "boards", "%s.json" % letter)
    rows = graded_rows(ledgers)
    reg = schema.registry()
    run = (spec_template or {}).get("_runs", "pair") if spec_template else "pair"
    stages = schema.STAGES.get(run, ("pair",))
    proposable = sorted(k for k, v in reg.items()
                        if v.get("category") == "experiment" and v.get("stage") in stages)
    types = schema.knob_types()
    return {
        "letter": letter,
        "board_declarations": json.loads(_read(bj) or "{}"),
        "measured_knob_table": measured_table(),
        "graded_arms": summarise_rows(rows),
        "graded_count": len(rows),
        "best_pairs": max([r["pairs"] for r in rows if isinstance(r.get("pairs"), int)] or [None]) if rows else None,
        "worst_pairs": min([r["pairs"] for r in rows if isinstance(r.get("pairs"), int)] or [None]) if rows else None,
        "failure_profile": json.loads(_read(profile) or "{}") if profile else {},
        "proposable_knobs": proposable,
        "knob_types": {k: types.get(k, {"type": "unknown", "default": "", "note": ""}) for k in proposable},
        "reserved_knobs": schema.RESERVED_KNOBS(reg),
        "basis_locked_knobs": schema.BASIS_KNOBS(reg),
        "run_stage": run,
        "law": LAW,
        "notes": list(extra),
        "_signatures": sorted(signatures(rows)),
    }


def render(p):
    """The pack as the text the proposer is given. One function, so a test can read exactly what was sent."""
    L = []
    L.append("BOARD %s. %d arms have been graded on this problem already." % (p["letter"].upper(), p["graded_count"]))
    if p.get("best_pairs") is not None:
        L.append("The best graded row on this board lays %s and the worst lays %s. A prediction of `>=` at or "
                 "below %s is REFUSED: an arm that changed nothing would meet it."
                 % (p["best_pairs"], p["worst_pairs"], p["best_pairs"]))
    L.append("\n=== THE LAW MEASURED ON THIS PROBLEM ===\n" + p["law"])
    if p["board_declarations"]:
        L.append("\n=== WHAT THE BOARD ALREADY DECLARES (boards/%s.json), each value with the measurement behind it ===\n%s"
                 % (p["letter"], json.dumps(p["board_declarations"], indent=1)[:6000]))
    if p["measured_knob_table"]:
        L.append("\n=== THE MEASURED KNOB TABLE (the design record for this tool) ===\n" + p["measured_knob_table"][:9000])
    if p["graded_arms"]:
        L.append("\n=== EVERY ARM GRADED SO FAR, with what it predicted and what it got ===\n" + p["graded_arms"])
    if p["failure_profile"]:
        L.append("\n=== THE FAILURE PROFILE, counted (pair_report.py --json) ===\n" + json.dumps(p["failure_profile"], indent=1)[:4000])
    L.append("\n=== KNOBS YOU MAY PROPOSE at the %r stage, with the type the tool reads ===" % p.get("run_stage", "pair"))
    L.append("A knob's type is read from the line that reads it. A FLAG is 1 or 0 and nothing else: giving it a")
    L.append("number sets it ON, which is usually its default, and the arm then measures nothing.")
    for k in p["proposable_knobs"]:
        t = (p.get("knob_types") or {}).get(k, {})
        L.append("  %-24s %-16s default %-12s %-10s %s"
                 % (k, t.get("type", "unknown"), t.get("default", ""), t.get("unit", ""), t.get("note", "")))
    L.append("\n=== KNOBS THAT ARE REFUSED, and why ===")
    for k, why in sorted(p["reserved_knobs"].items()):
        L.append("  RESERVED %-18s %s" % (k, why))
    for k, why in sorted(p["basis_locked_knobs"].items()):
        L.append("  BASIS    %-18s %s" % (k, why))
    for n in p["notes"]:
        L.append("\n=== NOTE ===\n" + n)
    return "\n".join(L)


if __name__ == "__main__":
    import sys
    sys.path.insert(0, HERE)
    letter = sys.argv[1] if len(sys.argv) > 1 else "b"
    prof = sys.argv[2] if len(sys.argv) > 2 else None
    print(render(pack(letter, profile=prof, ledgers=[os.path.join(ECAD, "out/arms/arms.jsonl")])))
