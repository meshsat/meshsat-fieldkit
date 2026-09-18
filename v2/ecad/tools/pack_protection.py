#!/usr/bin/env python3
"""The pack's protection against the cell maker's own numbers (rule BAT-001, MESHSAT-862, 18 September 2026).

BAT-001 is a BLOCKER on board P and it had no instrument at all: its coverage note read "the protection is
designed and its thresholds are configured in software; no check compares a threshold against the cell's own
limits". A data-flash configuration that exists nowhere is not a design, it is an intention, so
`pcb_pack_protection.yaml` writes the intended configuration down function by function and this judges it:

  * every protection the requirement names is present (over-voltage, under-voltage, over-current, short
    circuit, over-temperature), each naming the device that implements it, its threshold and delay, the cell
    limit it is derived from and the test that will demonstrate it on the prototype, which is the rule's own
    acceptance criteria word for word;
  * every threshold is inside that limit IN ITS OWN DIRECTION, computed at the pack's WORST parallel count,
    because three cells in parallel carry less than four and a limit that passes at 4P and fails at 3P is not
    a limit this pack meets;
  * every limit is QUOTED from the cell's specification and the quote is found in that document's own text,
    so a number typed from memory cannot survive (the rule the fuse derating table taught on 17 September,
    where nine of thirteen typed rows were shifted a column);
  * every device named is in board P's netlist by reference, because a protection implemented by a part the
    board does not carry is not a protection;
  * and the requirement's own words, IN HARDWARE AND INDEPENDENT OF ANY SOFTWARE, are asked of the pack: a
    pack whose every cell-level protection is one firmware-configured device fails with that sentence.

Usage: pack_protection.py [--netlist <board.net>] [--table <yaml>] [--check]
"""
import os, re, sys, json, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))     # v2/ecad/tools -> the repo root
TABLE = os.path.join(HERE, "pcb_pack_protection.yaml")
NETLIST = os.path.join(os.path.dirname(HERE), "pcb-p-pack-p2", "out", "pcb-p-pack.net")
REQUIRED = {"over-voltage": "CELL_OVER_VOLTAGE", "under-voltage": "CELL_UNDER_VOLTAGE",
            "over-current in discharge": "PACK_OVER_CURRENT_DISCHARGE",
            "over-current in charge": "PACK_OVER_CURRENT_CHARGE",
            "short circuit": "PACK_SHORT_CIRCUIT_DISCHARGE",
            "over-temperature in charge": "CHARGE_TEMPERATURE_WINDOW",
            "over-temperature in discharge": "DISCHARGE_TEMPERATURE_WINDOW"}


def load(path=TABLE):
    import yaml
    return yaml.safe_load(open(path, encoding="utf-8"))


def pdf_text(rel):
    """The document's own text, or None where this host cannot read a PDF. Absence is reported, never assumed
    to agree: a quote that could not be checked is a note and a quote that is checked and missing is a
    failure."""
    p = rel if os.path.isabs(rel) else os.path.join(ROOT, rel)
    if not os.path.isfile(p): return None
    try:
        return subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
    except (FileNotFoundError, OSError):
        try:
            import pypdf
            return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(p).pages)
        except Exception:
            return None


def _norm(s):
    return re.sub(r"[\s ]+", " ", (s or "")).replace("–", "-").replace("—", "-").strip().lower()


def judge(t, netlist=None):
    """Every check this rule makes, as (ok, text) pairs. Pure: the caller decides what to do with them."""
    fails, notes, checks = [], [], 0
    pack = t.get("pack") or {}; cell = t.get("cell") or {}; lims = cell.get("limits") or {}
    devs = t.get("devices") or {}; fns = {f["id"]: f for f in (t.get("functions") or [])}
    pmin = int(pack.get("parallel_min") or 0)

    # 1. every protection the requirement names
    for what, fid in sorted(REQUIRED.items()):
        checks += 1
        if fid not in fns: fails.append("no function for %s: the requirement names it and the table has no %s" % (what, fid))

    # 2. the quotes, re-read from the cell's own specification
    txt = pdf_text(cell.get("spec") or "")
    if txt is None:
        notes.append("the cell specification could not be read on this host (%s), so %d quoted limit(s) were "
                     "not re-checked against it" % (cell.get("spec"), len(lims)))
    else:
        low = _norm(txt)
        for k, v in sorted(lims.items()):
            checks += 1
            q = _norm(v.get("quote"))
            if not q: fails.append("limit %s carries no quote from the document it cites" % k)
            elif q not in low: fails.append("limit %s quotes %r and that string is not in %s" % (k, v.get("quote"), cell.get("spec")))

    # 3. every device is on the board's own netlist
    nl = ""
    if netlist and os.path.isfile(netlist): nl = open(netlist, encoding="utf-8", errors="replace").read()
    for ref, d in sorted(devs.items()):
        checks += 1
        if not nl: continue
        if not re.search(r'\(comp \(ref "%s"\)' % re.escape(ref), nl):
            fails.append("device %s (%s) is named as protection and board P's netlist has no such reference" % (ref, d.get("part")))
    if not nl: notes.append("no netlist was given or found, so the %d device reference(s) were not checked "
                            "against the board" % len(devs))

    # 4. each function: its device, its threshold, its basis, its test, and the derivation itself
    for fid, f in sorted(fns.items()):
        checks += 1
        dev = f.get("device")
        if dev not in devs: fails.append("%s names device %s and the table does not describe it" % (fid, dev))
        if len((f.get("test") or "")) < 40:
            fails.append("%s names no prototype test, which is half of this rule's acceptance criteria" % fid)
        base = f.get("derived_from")
        lim = lims.get(base)
        if lim is None:
            fails.append("%s derives from %s and the cell's limits carry no such entry" % (fid, base)); continue
        th = f.get("threshold") or {}
        d = f.get("direction")
        checks += 1
        if d == "above_limit_by_at_most":
            a = (f.get("allowance") or {})
            if not a.get("why"): fails.append("%s sits above the cell's own limit with no reason for the allowance" % fid)
            hi = float(lim["value"]) + float(a.get("value") or 0)
            if not (float(lim["value"]) < float(th["value"]) <= hi + 1e-9):
                fails.append("%s trips at %s and the cell's %s is %s: the trip must sit above it and within the "
                             "declared %s allowance" % (fid, th.get("value"), base, lim.get("value"), a.get("value")))
        elif d == "at_or_above_limit":
            if float(th["value"]) < float(lim["value"]) - 1e-9:
                fails.append("%s trips at %s, BELOW the cell maker's own %s of %s" % (fid, th.get("value"), base, lim.get("value")))
        elif d == "at_or_below_pack_limit":
            per_cell_a = float(lim["value"]) / 1000.0 if str(base).endswith("_ma") else float(lim["value"])
            cap = per_cell_a * pmin
            if float(th["value"]) > cap + 1e-9:
                fails.append("%s trips at %.1f A and %d cells in parallel are rated %.1f A (%s)" % (fid, float(th["value"]), pmin, cap, base))
            else:
                notes.append("%s: %.1f A against %.1f A for %d cells in parallel (%s)" % (fid, float(th["value"]), cap, pmin, base))
        elif d == "below_prospective_fault":
            lowf = float((pack.get("prospective_fault_a") or {}).get("low") or 0)
            if float(th["value"]) >= lowf:
                fails.append("%s trips at %.1f A and the lowest prospective fault at this node is %.1f A: a "
                             "threshold at or above the fault current never trips on it" % (fid, float(th["value"]), lowf))
        elif d == "inside_window":
            lo, hi = float(th["low"]), float(th["high"])
            if lo < float(lim["low"]) - 1e-9 or hi > float(lim["high"]) + 1e-9:
                fails.append("%s allows %s to %s and the cell maker allows %s to %s" % (fid, lo, hi, lim.get("low"), lim.get("high")))
        else:
            fails.append("%s has no comparison direction this gate understands (%s)" % (fid, d))

    # 5. the requirement's own words: in hardware, independent of any software
    checks += 1
    sec = (pack.get("secondary_protection") or {})
    soft_only = [fid for fid, f in sorted(fns.items()) if (devs.get(f.get("device")) or {}).get("software")]
    if not sec.get("present"):
        fails.append("BAT-001 asks for protection IN HARDWARE, INDEPENDENT OF ANY SOFTWARE, and %d of %d "
                     "functions are implemented by a device whose thresholds live in firmware, with no second "
                     "protector and no chemical fuse on this board: %s"
                     % (len(soft_only), len(fns), sec.get("why", "")[:160]))
    return dict(checks=checks, fails=fails, notes=notes, functions=len(fns), limits=len(lims),
                devices=len(devs), software_only=len(soft_only), quotes_checked=txt is not None)


def main(a):
    table = a[a.index("--table") + 1] if "--table" in a else TABLE
    netlist = a[a.index("--netlist") + 1] if "--netlist" in a else NETLIST
    t = load(table)
    r = judge(t, netlist)
    print("pack_protection: %d function(s) over %d cell limit(s) and %d device(s), %d check(s), %d failure(s)%s"
          % (r["functions"], r["limits"], r["devices"], r["checks"], len(r["fails"]),
             "" if r["quotes_checked"] else " (the cell specification could not be read here)"))
    for n in r["notes"]: print("  note %s" % n)
    for f in r["fails"]: print("  FAIL %s" % f)
    if "--check" not in a: return 0
    out_dir = os.environ.get("VERDICT_DIR") or os.path.join(os.path.dirname(HERE), "out")
    return _v.write("pack_protection", _v.FAIL if r["fails"] else _v.PASS,
                    counts={"functions": r["functions"], "limits": r["limits"], "devices": r["devices"],
                            "checks": r["checks"], "fail": len(r["fails"]), "software_only": r["software_only"]},
                    denominator=r["checks"], evidence=r["fails"][:20],
                    inputs={"table": os.path.relpath(table, ROOT), "netlist": os.path.relpath(netlist, ROOT) if os.path.isfile(netlist) else None,
                            "cell_spec": (t.get("cell") or {}).get("spec")},
                    note="every protection this requirement names, with the device that implements it, its "
                         "configured threshold, the cell limit it is derived from (quoted and re-read from the "
                         "cell maker's own specification) and the test that will demonstrate it on the "
                         "prototype; the currents are judged at the pack's worst parallel count",
                    out_dir=out_dir)


if __name__ == "__main__":
    sys.exit(_v.guard("pack_protection", main, sys.argv[1:]))
