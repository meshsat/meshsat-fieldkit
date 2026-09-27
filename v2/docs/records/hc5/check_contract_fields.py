#!/usr/bin/env python3
"""Every interface contract carries every field, as a value, as "n/a: reason" or as "TBD: ... effect" (layer 5 closer hc5,
MESHSAT-1357, 27 September 2026, pass 2).

WHY IT EXISTS. The first draft of the eighteen contracts the layer 5 closer added to `pcb_interfaces.yaml` claimed, in
ARCHITECTURE.md section 12 and in the closer's report, that every one named its levels, current, default state,
sequencing, mating and hot-plug rule and marked what was TBD with its effect. A review read the YAML and found seven of
them without some of those fields and nothing marked TBD in their place. A claim about a data file is settled by reading
the data file, so this reads it and prints the table the claim rests on.

WHAT IT CHECKS, per contract (read-only; stdlib plus PyYAML, which the tree's tools already use):
  * the fields REQUIRED below are present and not empty (`tbd` and `findings` may be an empty list: "nothing open");
  * every string anywhere in those fields that says "n/a" says why ("n/a: <reason>"), and every one that says "TBD" names
    the effect ("effect");
  * every entry of `tbd` names its effect;
  * every `ends` entry names its owner: a board end has `board`, `ref` or `refs`, `part` and `src`; a device, case or cable
    end has a text that names a part or says TBD with its effect; at least one end is a board end, and a
    board_to_board contract has two.
It does NOT judge whether a value is right: that is the netlists', the makers' documents' and check_contracts.py's.

SCOPE. By default the eighteen contracts of the layer 5 closer (NEW below), which must all pass; `--all` also reports the
first twelve contracts of 26 September 2026, whose missing fields are listed as information (they were written before
this field contract and are the integrator's re-anchor action, not this closer's).

Usage:  python3 check_contract_fields.py [--file v2/ecad/tools/pcb_interfaces.yaml] [--all]
Exit 0 when every NEW contract passes, 1 otherwise."""
import argparse, os, sys
import yaml

NEW = ["IF-EXT-DC", "IF-EXT-ETH", "IF-MON", "IF-BA-RF", "IF-DA-VHF", "IF-HS", "IF-CAM", "IF-E-POD", "IF-E-SENSORS",
       "IF-E-TAMP", "IF-E-WATER", "IF-E-FANS", "IF-A-HEAT", "IF-P-CELLS", "IF-B-FANS", "IF-B-LIME", "IF-B-RB9704",
       "IF-D-FLANGE"]
REQUIRED = ["title", "kind", "ends", "harness", "levels", "current", "default_state", "sequencing", "mating", "hot_plug",
            "judged_by", "tbd", "findings", "serves"]
MAY_BE_EMPTY = {"tbd", "findings"}
SHOWN = ["harness", "levels", "current", "default_state", "sequencing", "mating", "hot_plug", "judged_by"]


def strings(v):
    if isinstance(v, str): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from strings(x)
    elif isinstance(v, (list, tuple)):
        for x in v: yield from strings(x)


def kind_of(v):
    """How a field is filled: 'value', 'n/a' or 'TBD' (a value that also carries a TBD part reads 'value+TBD')."""
    ss = list(strings(v))
    if not ss: return "value"
    first = ss[0].strip().lower()
    if first.startswith("n/a"): return "n/a"
    if first.startswith("tbd"): return "TBD"
    return "value+TBD" if any("TBD" in s for s in ss) else "value"


def check(cid, c, strict):
    errs = []
    for f in REQUIRED:
        if f not in c:
            errs.append("%s: no `%s`" % (cid, f)); continue
        v = c[f]
        if v in (None, "") or (isinstance(v, (list, dict)) and not v and f not in MAY_BE_EMPTY):
            errs.append("%s: `%s` is empty" % (cid, f))
    for f in [x for x in REQUIRED if x in c]:
        for s in strings(c[f]):
            low = s.strip().lower()
            if low.startswith("n/a") and not (low.startswith("n/a:") and len(low) > 8):
                errs.append("%s: `%s` says n/a without a reason: %r" % (cid, f, s[:60]))
            if "TBD" in s and "effect" not in s:
                errs.append("%s: `%s` says TBD without its effect: %r" % (cid, f, s[:80]))
    for t in (c.get("tbd") or []):
        if "effect" not in str(t):
            errs.append("%s: tbd entry without its effect: %r" % (cid, str(t)[:80]))
    ends = c.get("ends") or []
    boards = 0
    for e in ends:
        if not isinstance(e, dict):
            errs.append("%s: an end is not a mapping" % cid); continue
        if "board" in e:
            boards += 1
            for k in ("part", "src"):
                if not e.get(k): errs.append("%s: board %s end has no `%s`" % (cid, e.get("board"), k))
            if not (e.get("ref") or e.get("refs")): errs.append("%s: board %s end names no ref" % (cid, e.get("board")))
        else:
            txt = " ".join(str(e.get(k, "")) for k in ("device", "case", "cable"))
            if not txt.strip(): errs.append("%s: an end names no board, device, case or cable" % cid)
            if "TBD" in txt and "effect" not in txt:
                errs.append("%s: a device/case/cable end says TBD without its effect" % cid)
    if boards < 1: errs.append("%s: no board end" % cid)
    if c.get("kind") == "board_to_board" and boards < 2: errs.append("%s: board_to_board with %d board end(s)" % (cid, boards))
    return errs


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="v2/ecad/tools/pcb_interfaces.yaml")
    ap.add_argument("--all", action="store_true", help="also report the first twelve contracts (information only)")
    a = ap.parse_args(argv)
    d = yaml.safe_load(open(a.file, encoding="utf-8"))
    cs = d["board_to_board"]["contracts"] if "board_to_board" in d else d
    print("check_contract_fields: %s, %d contracts in the file" % (a.file, len(cs)))
    bad = 0
    missing = [i for i in NEW if i not in cs]
    for i in missing:
        print("FAIL %s: not in the file" % i); bad += 1
    print("\n%-14s %s" % ("contract", "  ".join("%-10s" % f[:10] for f in SHOWN)))
    for cid in [i for i in NEW if i in cs]:
        c = cs[cid]
        print("%-14s %s" % (cid, "  ".join("%-10s" % (kind_of(c[f]) if f in c else "MISSING") for f in SHOWN)))
    print()
    for cid in [i for i in NEW if i in cs]:
        errs = check(cid, cs[cid], True)
        for e in errs: print("FAIL " + e)
        bad += bool(errs)
    print("NEW contracts: %d of %d pass the field contract" % (len(NEW) - bad, len(NEW)))
    if a.all:
        old = [i for i in cs if i not in NEW]
        print("\nINFORMATION, the first %d contracts (26 September 2026, written before this field contract). 'no key for' lists"
              "\nthe field names they lack; some of that content sits under their older keys (cable, power, cable_out_states,"
              "\nmap_identity.judged_by), which this does not read as the field:" % len(old))
        for cid in old:
            errs = check(cid, cs[cid], False)
            top = [e for e in errs if e.startswith(cid + ": no `")]
            gaps = sorted(set(e.split("`")[1] for e in top))
            other = [e for e in errs if e not in top]
            print("  %-14s %s%s" % (cid, ("no key for " + ", ".join(gaps)) if gaps else "carries every field",
                                   ("; " + "; ".join(x.split(": ", 1)[1] for x in other)) if other else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
