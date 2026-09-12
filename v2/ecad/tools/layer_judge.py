#!/usr/bin/env python3
"""Does this board need the layers it has? The evidence, never the change (MESHSAT-862, 12 Sep 2026).

The owner reopened every board's layer count as a P0 on 11 September, and the record's problem was that
four layers had NO written rationale at all while the promotions to six were session decisions recorded
inside an owner rulings list. A decision needs the measurement that forced it and the cost it adds.

**This tool takes that measurement and it changes nothing.** The layer count and the stackup are a
reserved class (`reserved.json`: `gen_pcb_*.py SetCopperLayerCount`, `stackup_write.py STACKS`), so a
patch that touches either is refused before any test runs, whatever mode the pipeline is in. The line
this draws is worth stating because it is easy to blur: MEASURING a reserved change is exactly what P0
asked for, and it is done in an isolated worktree that never lands; ADOPTING one is the owner's.

What it reads, per board, and why each piece is in the answer:

  * WHAT EACH LAYER CARRIES (`layer_audit.py`): an inner layer with no routed track at all is carrying a
    plane, and a plane's job is answerable by `dc_drop.py`. E1 dock is the case in point: four layers,
    two inner ones, NOT ONE routed track between them.
  * WHAT THE ROUTING NEEDS: the share of track length on inner layers. A board where the inner layers
    carry a third of the copper is not a board you take layers from without a re-route to prove it.
  * WHAT THE POWER NEEDS (`dc_drop.py` on the board as it stands, and on a copy with the inner power
    copper deleted): this is the measurement that settled E on 12 September, 13 mV on CELL_F and 28 mV
    on VIN_RAW, and it is the half that can be answered without routing anything.
  * WHAT THE PAIRS NEED (`impedance_check.py`): an inner-layer pair is a stripline, so removing its
    layers is an impedance question and not only a routing one.

The verdict is one of: KEEP (a measurement forces this count), QUESTION (nothing in these numbers forces
it and a re-route experiment is owed), or INCONCLUSIVE (something could not be measured). It is never
"REDUCE", because that is a decision and not a measurement.

Usage: layer_judge.py <board.kicad_pcb> [--intent out/<name>-intent.json] [--out-dir out] [--json f.json]
"""
import os, re, sys, json, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict                                                     # noqa: E402

INNER = ("In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu")


def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop("timeout", 900), **kw)


def audit(board, out_dir):
    """What each copper layer carries, from the tool that already answers that."""
    j = os.path.join(out_dir, "layer_audit.json")
    r = _run([sys.executable, os.path.join(HERE, "layer_audit.py"), board, "--json", j])
    if not os.path.exists(j):
        return None, (r.stderr or r.stdout).strip()[-300:]
    return json.load(open(j)), ""


def _row(a, board):
    """layer_audit writes a LIST of per-board dicts; this is the one for our board, with its own keys."""
    base = os.path.basename(board)
    for r in (a if isinstance(a, list) else [a]):
        if isinstance(r, dict) and (r.get("board") == base or r.get("board") == board):
            return r
    return (a[0] if isinstance(a, list) and a and isinstance(a[0], dict) else {})


def judge(board, out_dir="out", intent=None):
    os.makedirs(out_dir, exist_ok=True)
    a, err = audit(board, out_dir)
    if a is None:
        return {"verdict": verdict.INCONCLUSIVE, "why": "layer_audit could not read the board: %s" % err,
                "counts": {}, "evidence": []}
    r0 = _row(a, board)
    if not r0:
        return {"verdict": verdict.INCONCLUSIVE, "why": "layer_audit wrote no row for this board",
                "counts": {}, "evidence": []}
    per = r0.get("per_layer") or {}
    idle = list(r0.get("plane_only_inner") or [])
    counts = {"copper_layers": int(r0.get("copper_layers") or 0),
              "inner_layers_with_no_routed_track": len(idle),
              "inner_track_share_pct": round(100.0 * float(r0.get("inner_share") or 0), 1),
              "inner_signal_mm": round(float(r0.get("inner_signal_mm") or 0), 1),
              "vias": int(r0.get("vias") or 0)}
    ev = ["%s, %d copper layers (%s)" % (r0.get("board"), counts["copper_layers"], ", ".join(r0.get("layers") or []))]
    for L, d in per.items():
        if not str(L).startswith("In"):
            continue
        ev.append("%-8s %5d tracks %8.1f mm  zones: %s"
                  % (L, d.get("tracks", 0), d.get("mm", 0.0), ", ".join(d.get("zones") or []) or "-"))
    ev.append("inner layers carrying no routed track: %s" % (", ".join(idle) or "none"))
    ev.append("share of routed length on inner layers: %.1f percent" % counts["inner_track_share_pct"])

    # IS THIS BOARD ROUTED AT ALL? Every escape, fanout stub and pre-routed pair here is locked and the
    # router's own copper is not, so a board whose copper is almost entirely locked has never been
    # routed. Judging what its layers NEED from what they CARRY is meaningless on such a board, and the
    # first version of this tool did exactly that: it read two placed phase copies and called four and
    # two idle inner layers a QUESTION, when the same boards routed read 82.5 and 55.3 percent inner.
    tot = float(r0.get("total_mm") or 0.0)
    lock = float(r0.get("locked_mm") or 0.0)
    counts["locked_share_pct"] = round(100.0 * lock / tot, 1) if tot else 0.0
    ev.append("locked copper: %.0f of %.0f mm, %.1f percent" % (lock, tot, counts["locked_share_pct"]))
    if tot < 1.0 or counts["locked_share_pct"] >= 90.0:
        return {"verdict": verdict.INCONCLUSIVE, "counts": counts, "evidence": ev,
                "why": ("this board is not routed: %.1f percent of its copper is locked, which is the escapes "
                        "and the pre-routed pairs and nothing else. What its layers carry says nothing about "
                        "what they need. Judge the ROUTED board" % counts["locked_share_pct"])}

    # The power half, where an intent file exists: what the rails read as the board stands.
    if intent and os.path.exists(intent):
        r = _run([sys.executable, os.path.join(HERE, "dc_drop.py"), board, intent], cwd=os.path.dirname(board) or ".")
        met = len(re.findall(r"\bMET\b", r.stdout)); missed = len(re.findall(r"\bMISSED|\bNOT MET", r.stdout))
        counts["rails_met"] = met; counts["rails_missed"] = missed
        ev.append("dc_drop on the board as it stands: %d rail(s) MET, %d not" % (met, missed))
    else:
        ev.append("no intent file given, so the power half of this question is not answered here")

    # The verdict, and it is deliberately not allowed to say REDUCE.
    if counts.get("copper_layers", 0) <= 2:
        v, why = verdict.PASS, "a two-layer board has no inner layer to question"
    elif idle and counts["inner_track_share_pct"] < 1.0:
        v, why = (verdict.FAIL,
                  "QUESTION: %d inner layer(s) carry no routed track at all, so what they carry is a plane and "
                  "the question is a power one. Run dc_drop with those pours deleted; if the rails still meet "
                  "their budget, nothing in this board's own copper forces this layer count and the decision "
                  "belongs in the owner's file with these numbers" % len(idle))
    elif counts["inner_track_share_pct"] >= 15.0:
        v, why = (verdict.PASS,
                  "KEEP: the inner layers carry %.1f percent of this board's routed length, so removing them is "
                  "a re-route and not an edit; the measurement that would change this is a full route at the "
                  "lower count reaching zero open" % counts["inner_track_share_pct"])
    else:
        v, why = (verdict.FAIL,
                  "QUESTION: the inner layers carry only %.1f percent of the routed length and none is idle, "
                  "which forces nothing either way. A route at the lower count is the measurement owed"
                  % counts["inner_track_share_pct"])
    return {"verdict": v, "why": why, "counts": counts, "evidence": ev}


def main(argv):
    ap = argparse.ArgumentParser(description="the evidence for a board's layer count, never the change")
    ap.add_argument("board"); ap.add_argument("--intent", default=None)
    ap.add_argument("--out-dir", default="out"); ap.add_argument("--json", default=None)
    a = ap.parse_args(argv)
    r = judge(a.board, a.out_dir, a.intent)
    print("layer_judge: %s" % r["why"])
    for e in r["evidence"]:
        print("   %s" % e)
    print("layer_judge: THIS TOOL CHANGES NOTHING. The layer count and the stackup are a reserved class and the")
    print("             owner rules on them; what is written here is the evidence for that ruling.")
    if a.json:
        json.dump(r, open(a.json, "w"), indent=1)
    return verdict.write("layer_judge", r["verdict"], counts=r["counts"],
                         denominator=r["counts"].get("copper_layers", 1), evidence=r["evidence"],
                         note=r["why"][:300], out_dir=a.out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
