#!/usr/bin/env python3
"""Safe-low pull-downs of board B's control plane, judged at datasheet leakage (read-only; MESHSAT-1357 stream FAB,
26 Sep 2026, the checker's FAB-04 / FB-FAB-5 item).

Usage: pulldowns.py <netlist> [<netlist> ...]

The designators are ENUMERATED from the generator's rule, not discovered from the nets, so a line that dropped out
(renamed, deleted, or left at another value) shows as a FAIL instead of vanishing from the count:
  controller outputs: R(480 + 3j + i) on net <CTRL_BITS[j]>_<"ABC"[i]>, CTRL_BITS as gen_sch_b.py:1229 (candidate)
                      and :904 (main) spell it: SEL1 SEL2 SEL3 HUBRST1 HUBRST2 HUBRST3 WSEC (7 x 3 = 21);
  display selects:    R15 on HDMI_SEL1, R16 on HDMI_SEL2 (gen_sch_b.py:903 candidate, :658 main).
For each: the resistor must exist, join exactly its net and GND, and be the only resistor on the net; the net's
worst-case input leakage is summed from the loads the netlist puts on it, with these datasheet maxima:
  SN74LVC08A input        5 uA      TI SCAS283W 5.7, PDF p.7 (II, -40 to +85 C)        threshold VIL 0.8 V (5.4, p.6)
  STM32H743/H753 GPIO     10.25 uA  ST DS12110 Rev 10 (H743, the candidate's value text) Table 60 and DS12117 Rev 9
                                  (H753, B21's value text) Table 59, PDF p.138 in both: Ilkg +-250 nA for FT_xx and
                                  TT_xx, powered, 0 < VIN <= Max(VDDXXX); note 4 in both: "This parameter represents
                                  the pad leakage of the I/O itself. The total product pad leakage is provided by the
                                  following formula: ITotal_Ikg_max = 10 uA + [number of I/Os where VIN is applied on
                                  the pad] x Ilkg(Max)". ST does not say which pad carries the 10 uA product term, so
                                  this judge takes the bounding reading and puts all of it on the one supervisor pin
                                  each line carries: 10 uA + 1 x 0.25 uA (round 6's O-08 counted the same 10 uA per
                                  device). Pin types, DS12110 Table 9 and DS12117 Table 8, PDF pp.68, 69, 71 in both,
                                  LQFP100 pins 22-25, 28, 29, 37: PA0 FT_a, PA1 FT_ha, PA2 FT_a, PA3 FT_ha, PA4 TT_a,
                                  PA5 TT_ha, PE7 TT_ha
  TS3DV642 SEL1/SEL2/EN   10 uA     TI SCDS343F 6.5, PDF p.7 (IIL/IIH)                   threshold VIL 0.5 V (same table)
  test pad, connector pin 0         (no silicon on board B; the panel's own pin is board C's, absent in this state)
Any other load is reported as UNKNOWN and fails the line. The voltage is leakage x R; PASS when below the lowest VIL
of the net's logic loads. It prints the result at the netlist's value and at 10 kOhm (FAB-04's taken value).
No fitted constant, no write.
"""
import re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from netparse import parse, sha256

CTRL_BITS = ("SEL1", "SEL2", "SEL3", "HUBRST1", "HUBRST2", "HUBRST3", "WSEC")
EXPECTED = [("R%d" % (480 + 3 * j + i), "%s_%s" % (bit, t)) for j, bit in enumerate(CTRL_BITS) for i, t in enumerate("ABC")]
EXPECTED += [("R15", "HDMI_SEL1"), ("R16", "HDMI_SEL2")]
# (substring of the part's value, leakage in A, VIL in V or None when the part does not decide the level)
LOADS = (("SN74LVC08A", 5e-6, 0.8), ("STM32H7", 10e-6 + 0.25e-6, None), ("TS3DV642", 10e-6, 0.5))


def ohms(v):
    m = re.match(r"\s*(\d+(?:\.\d+)?)\s*([kKM]?)", v or "")
    return float(m.group(1)) * {"": 1.0, "k": 1e3, "K": 1e3, "M": 1e6}[m.group(2)] if m else None


def judge(path):
    comps, nets, pinnet = parse(path)
    print("== %s  %s" % (sha256(path), path))
    fails = 0
    for ref, net in EXPECTED:
        nodes = nets.get(net, [])
        rs = sorted({r for (r, p, f, t) in nodes if r.startswith("R")})
        pads = sorted(pinnet.get((ref, q)) for q in ("1", "2")) if ref in comps else None
        leak, vil, unknown, loads = 0.0, [], [], []
        for (r, p, f, t) in nodes:
            if r == ref or r.startswith("TP") or r.startswith("J_"):
                continue
            v = comps.get(r, {}).get("value") or ""
            hit = next((l for l in LOADS if l[0] in v), None)
            if hit is None:
                unknown.append("%s.%s" % (r, p))
                continue
            leak += hit[1]
            loads.append("%s.%s" % (r, p))
            if hit[2] is not None:
                vil.append(hit[2])
        ok_shape = ref in comps and pads == sorted([net, "GND"]) and rs == [ref] and not unknown and vil
        val = comps.get(ref, {}).get("value")
        r_ohm = ohms(val)
        v_now = leak * r_ohm if r_ohm else None
        v_10k = leak * 10e3
        th = min(vil) if vil else None
        ok_now = bool(ok_shape and v_now is not None and v_now < th)
        fails += not ok_now
        print("%-5s %-11s value %-5s pads %-24s loads %-40s leak %5.2f uA  VIL %s  V@value %s  V@10k %.3f  %s%s" % (
            ref, net, val, pads, ",".join(loads), leak * 1e6, th, "%.3f" % v_now if v_now is not None else "n/a", v_10k,
            "PASS" if ok_now else "FAIL", "" if not unknown else "  UNKNOWN LOADS " + ",".join(unknown)))
    print("lines %d (21 controller outputs + 2 display selects), FAIL %d" % (len(EXPECTED), fails))


if __name__ == "__main__":
    for p in sys.argv[1:]:
        judge(p)
