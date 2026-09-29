#!/usr/bin/env python3
"""S-117's read-back on a board A netlist (stream s117, MESHSAT-1357, 29 September 2026). Read-only.

It PARSES the netlist as the S-expression it is (v2/ecad/tools/netlist_sexp.py; nothing is grepped, no KiCad is needed)
and asks of it what apply_gen_sch_a_s117.py drew, part by part and net by net:
  L2    the XAL1010-472ME on the XAL1010 land, between CH_SW1 and CH_SW2
  IADPT exactly U3 pin 8, TP19, the detection resistor and its capacitor; the resistor 191 or 187 kOhm (SLUSE66A Table
        9-4, printed page 27) at 1 percent or better on an 0603 land, to GND; the capacitor 100 pF or less (the pin table,
        page 6; CIADPT_MAX, page 12), to GND
  COMP1 U3 pin 16 with R25 and C234 only; R25 40.2 kOhm 1 percent to CH_COMP1C; CH_COMP1C holds R25 and C26 only; C26
        4.7 nF and C234 33 pF to GND (Table 9-5's 400 kHz row, page 27, as Figure 9-2 draws it, page 28)
  COMP2 U3 pin 17 with R220 and C27 only; R220 15 kOhm to CH_COMP2C; CH_COMP2C holds R220 and C235 only; C235 680 pF and
        C27 15 pF to GND
  CDIFF C121 10 nF across CH_ACP_F and CH_ACN_F (10.2.2.2, page 84: 10 nF at 400 kHz)
Values are compared as numbers read from the value text (the leading figure and its multiplier), never as strings.

With --against <old.net> it also compares the two parsed netlists and refuses any difference beyond the S-117 change:
the references added must be exactly R219, R220, C233, C234 and C235, none removed, the parts whose value or land moved
exactly L2, R25, C26 and C27, and the nets whose members moved exactly IADPT, CH_COMP1, CH_COMP2, CH_COMP2C and GND, each by
exactly the pins the change draws (the regeneration parity check for this one board).

With --fets (stream s117's second issue, S-117's finding F1, apply_gen_sch_a_fets_s117.py) it also asks for the charger's
four FETs: Q7 CSD17578Q5A, Q8 to Q10 CSD17577Q5A, each on the PowerPAK SO-8 land with its pads on the nets they had (1 to
3 source, 4 gate, 5 drain; gen_sch_a.py's nfet()), and --against then also allows Q7 to Q10 among the changed parts.

Usage: readback_s117.py [<netlist.net>] [--fets] [--against <old.net>]   (default: board A's committed netlist,
       v2/ecad/pcb-a-power-a23/out/pcb-a-power.net)
Exit 0 every check holds, 1 a check fails, 3 a netlist cannot be read."""
import hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import netlist_sexp as N

DEFAULT = os.path.join(TOP, "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net")
MULT = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6, "R": 1.0, "": 1.0}
_NUM = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*([pnumkMR]?)(\d*)")


def number(value):
    """The leading figure of a value text in base units: '40.2k 1%' -> 40200, '4.7n' -> 4.7e-9, '4R7' -> 4.7."""
    m = _NUM.match(value or "")
    if not m: return None
    whole, mult, frac = m.groups()
    x = float(whole + ("." + frac if frac and "." not in whole else ""))
    return x * MULT[mult]


def tolerance_pct(value):
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", value or "")
    return float(m.group(1)) if m else None


def close(a, b, rel=0.005): return a is not None and abs(a - b) <= rel * abs(b)


def members(doc, net):
    return sorted((r, p) for r, p, *_ in doc["nets"].get(net, []))


def refs_on(doc, net): return sorted({r for r, _ in members(doc, net)})


def pins(doc, ref):
    return {p: n for (r, p), n in doc["pin_net"].items() if r == ref}


def two_pin(doc, ref, a, b):
    """The part's two pins sit on nets a and b, in either order."""
    got = sorted(pins(doc, ref).values())
    return got == sorted([a, b]), "%s pins on %s" % (ref, got)


def check(doc):
    res = []

    def add(name, ok, detail): res.append((name, bool(ok), detail))
    comp = doc["components"]

    def val(ref): return (comp.get(ref) or {}).get("value", "")

    def fp(ref): return (comp.get(ref) or {}).get("footprint", "")
    # L2
    add("L2 is the XAL1010-472ME", "XAL1010-472ME" in val("L2"), "value %r" % val("L2"))
    add("L2 on the XAL1010 land", fp("L2").endswith("L_Coilcraft_XAL1010-XXX"), "footprint %r" % fp("L2"))
    add("L2 between CH_SW1 and CH_SW2", *two_pin(doc, "L2", "CH_SW1", "CH_SW2"))
    add("L2 is 4.7 uH", close(number(val("L2")), 4.7e-6), "value %r" % val("L2"))
    # U3's three pins
    u3 = pins(doc, "U3")
    add("U3 pins 8, 16, 17 on IADPT, CH_COMP1, CH_COMP2", (u3.get("8"), u3.get("16"), u3.get("17")) == ("IADPT", "CH_COMP1", "CH_COMP2"),
        "pin 8 %s, 16 %s, 17 %s" % (u3.get("8"), u3.get("16"), u3.get("17")))
    # IADPT
    on = refs_on(doc, "IADPT")
    rs = [r for r in on if r.startswith("R")]; cs = [r for r in on if r.startswith("C")]
    add("IADPT holds U3, TP19, one resistor and one capacitor", sorted(set(on) - set(rs) - set(cs)) == ["TP19", "U3"]
        and len(rs) == 1 and len(cs) == 1, "IADPT: %s" % members(doc, "IADPT"))
    if len(rs) == 1:
        r = rs[0]; v = number(val(r)); t = tolerance_pct(val(r))
        add("IADPT resistor %s is 191 or 187 kOhm" % r, close(v, 191e3) or close(v, 187e3), "value %r" % val(r))
        add("IADPT resistor %s at 1 percent or better" % r, t is not None and t <= 1.0, "value %r" % val(r))
        add("IADPT resistor %s on an 0603 land" % r, fp(r).endswith("R_0603_1608Metric"), "footprint %r" % fp(r))
        add("IADPT resistor %s to GND" % r, *two_pin(doc, r, "IADPT", "GND"))
    if len(cs) == 1:
        c = cs[0]; v = number(val(c))
        add("IADPT capacitor %s is 100 pF or less" % c, v is not None and 0 < v <= 100e-12 * 1.0001, "value %r" % val(c))
        add("IADPT capacitor %s to GND" % c, *two_pin(doc, c, "IADPT", "GND"))
    # COMP1 and COMP2 (Table 9-5, 400 kHz, 4.7 uH)
    add("CH_COMP1 holds U3, R25 and C234 only", refs_on(doc, "CH_COMP1") == ["C234", "R25", "U3"], "CH_COMP1: %s" % members(doc, "CH_COMP1"))
    add("CH_COMP1C holds R25 and C26 only", refs_on(doc, "CH_COMP1C") == ["C26", "R25"], "CH_COMP1C: %s" % members(doc, "CH_COMP1C"))
    add("R25 is 40.2 kOhm", close(number(val("R25")), 40.2e3), "value %r" % val("R25"))
    add("C26 is 4.7 nF to GND", close(number(val("C26")), 4.7e-9) and two_pin(doc, "C26", "CH_COMP1C", "GND")[0], "value %r, %s" % (val("C26"), two_pin(doc, "C26", "CH_COMP1C", "GND")[1]))
    add("C234 is 33 pF to GND", close(number(val("C234")), 33e-12) and two_pin(doc, "C234", "CH_COMP1", "GND")[0], "value %r, %s" % (val("C234"), two_pin(doc, "C234", "CH_COMP1", "GND")[1]))
    add("CH_COMP2 holds U3, R220 and C27 only", refs_on(doc, "CH_COMP2") == ["C27", "R220", "U3"], "CH_COMP2: %s" % members(doc, "CH_COMP2"))
    add("CH_COMP2C holds R220 and C235 only", refs_on(doc, "CH_COMP2C") == ["C235", "R220"], "CH_COMP2C: %s" % members(doc, "CH_COMP2C"))
    add("R220 is 15 kOhm", close(number(val("R220")), 15e3), "value %r" % val("R220"))
    add("C235 is 680 pF to GND", close(number(val("C235")), 680e-12) and two_pin(doc, "C235", "CH_COMP2C", "GND")[0], "value %r, %s" % (val("C235"), two_pin(doc, "C235", "CH_COMP2C", "GND")[1]))
    add("C27 is 15 pF to GND", close(number(val("C27")), 15e-12) and two_pin(doc, "C27", "CH_COMP2", "GND")[0], "value %r, %s" % (val("C27"), two_pin(doc, "C27", "CH_COMP2", "GND")[1]))
    # CDIFF
    add("C121 is 10 nF across CH_ACP_F and CH_ACN_F", close(number(val("C121")), 10e-9) and two_pin(doc, "C121", "CH_ACP_F", "CH_ACN_F")[0],
        "value %r, %s" % (val("C121"), two_pin(doc, "C121", "CH_ACP_F", "CH_ACN_F")[1]))
    return res


NEW_REFS = {"R219", "R220", "C233", "C234", "C235"}
CHANGED_PARTS = {"L2", "R25", "C26", "C27"}
# (net, reference, pin) added or removed by the change; r() and c() draw pin 1 on their first net and pin 2 on the second
NET_DELTA = {("IADPT", "R219", "1"), ("GND", "R219", "2"), ("IADPT", "C233", "1"), ("GND", "C233", "2"),
             ("CH_COMP1", "C234", "1"), ("GND", "C234", "2"), ("CH_COMP2", "R220", "1"), ("CH_COMP2C", "R220", "2"),
             ("CH_COMP2C", "C235", "1"), ("GND", "C235", "2")}


FETS = {"Q7": ("CSD17578Q5A", {"1": "CH_SW1", "2": "CH_SW1", "3": "CH_SW1", "4": "CH_HIDRV1", "5": "CH_ACN"}),
        "Q8": ("CSD17577Q5A", {"1": "GND", "2": "GND", "3": "GND", "4": "CH_LODRV1", "5": "CH_SW1"}),
        "Q9": ("CSD17577Q5A", {"1": "GND", "2": "GND", "3": "GND", "4": "CH_LODRV2", "5": "CH_SW2"}),
        "Q10": ("CSD17577Q5A", {"1": "CH_SW2", "2": "CH_SW2", "3": "CH_SW2", "4": "CH_HIDRV2", "5": "VBAT"})}


def check_fets(doc):
    """[(name, ok, detail)]: the charger's four FETs as apply_gen_sch_a_fets_s117.py draws them."""
    res = []
    for ref, (part, pinmap) in FETS.items():
        c = doc["components"].get(ref) or {}
        v, fp = c.get("value", ""), c.get("footprint", "")
        res.append(("%s is the %s" % (ref, part), v.split()[:1] == [part], "value %r" % v))
        res.append(("%s on the PowerPAK SO-8 land, pads on their nets" % ref,
                    fp.endswith("PowerPAK_SO-8_Single") and pins(doc, ref) == pinmap, "footprint %r, pads %s" % (fp, pins(doc, ref))))
    return res


def against(new, old, fets=False):
    """[(name, ok, detail)]: the difference between two parsed netlists, held to exactly the S-117 change (and, with
    fets, the F1 change of the four FETs' values)."""
    res = []
    changed = CHANGED_PARTS | (set(FETS) if fets else set())
    nc, oc = new["components"], old["components"]
    added, removed = set(nc) - set(oc), set(oc) - set(nc)
    res.append(("parts added are exactly the five new ones", added == NEW_REFS, "added %s" % sorted(added)))
    res.append(("no part removed", not removed, "removed %s" % sorted(removed)))
    moved = {r for r in set(nc) & set(oc) if (nc[r]["value"], nc[r]["footprint"]) != (oc[r]["value"], oc[r]["footprint"])}
    res.append(("parts changed are exactly %s" % ", ".join(sorted(changed)), moved == changed, "changed %s" % sorted(moved)))
    def triples(doc): return {(n, r, p) for n, ms in doc["nets"].items() for r, p, *_ in ms}
    tn, to = triples(new), triples(old)
    delta = (tn - to) | (to - tn)
    res.append(("net members moved exactly by the change's pins", delta == NET_DELTA,
                "beyond the change: %s; missing: %s" % (sorted(delta - NET_DELTA)[:12], sorted(NET_DELTA - delta)[:12])))
    return res


def main(argv):
    args = [a for a in argv[1:]]
    fets = "--fets" in args
    args = [a for a in args if a != "--fets"]
    old_path = None
    if "--against" in args:
        k = args.index("--against")
        if k + 1 >= len(args): print("readback_s117: --against needs the old netlist"); return 3
        old_path = args[k + 1]; del args[k:k + 2]
    path = args[0] if args else DEFAULT
    try:
        doc = N.load(path)
        old = N.load(old_path) if old_path else None
    except Exception as e:  # a netlist that cannot be read decides nothing
        print("readback_s117: INCONCLUSIVE: a netlist cannot be read (%s)" % e)
        return 3
    res = check(doc) + (check_fets(doc) if fets else []) + (against(doc, old, fets) if old is not None else [])
    sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
    print("readback_s117: %s (sha256/16 %s)" % (os.path.relpath(path, TOP) if path.startswith(TOP) else path, sha[:16]))
    for name, ok, detail in res:
        print("  %-4s %-52s %s" % ("PASS" if ok else "FAIL", name, detail))
    bad = sum(1 for _, ok, _ in res if not ok)
    print("readback_s117: %s, %d of %d checks hold" % ("PASS" if not bad else "FAIL", len(res) - bad, len(res)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
