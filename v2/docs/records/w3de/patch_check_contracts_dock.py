#!/usr/bin/env python3
"""DRAFT for the owner of v2/ecad/tools/check_contracts.py (w3de, 27 September 2026): the dock contract states the EQ-16
decision, so a later edit that puts VIN_RAW back on the 813 signal contacts, or drops a power pin, is refused.

Three checks join section 5 (the dock's power contacts):
  - board A carries four VIN_RAW power pins (J_VR*) and four return pins (J_VN*, GND) on the dock block;
  - board E carries the 12 AWG lands P_VR on VIN_RAW and P_VN on GND;
  - no 813 signal contact carries VIN_RAW at either end (J_DOCK and J_BLK pins 1 to 12).
Section 4's identity check (the 2x6 map the same on A and E) is unchanged: it reads the new map once both halves land.

Usage: patch_check_contracts_dock.py <tree root holding v2/ecad>"""
import os, sys
p = os.path.join(sys.argv[1], "v2", "ecad", "tools", "check_contracts.py")
s = open(p, encoding="utf-8").read(); o = s
old = '''check(B["E"][1].get(("P_CN", "1"), "") == "GND", "E6: the pack return lands on GND (the 14.4 V node's return is the ground plane, 32.56)", B["E"][1].get(("P_CN", "1"), "absent"), boards={"E"})
'''
new = '''check(B["E"][1].get(("P_CN", "1"), "") == "GND", "E6: the pack return lands on GND (the 14.4 V node's return is the ground plane, 32.56)", B["E"][1].get(("P_CN", "1"), "absent"), boards={"E"})
# 5a. EQ-16 / R8E-N01 (27 September 2026, drafted by board E's stream w3de): VIN_RAW CROSSES THE DOCK ON POWER PINS. At
# board E's 14.10 A the four Preci-Dip 813 contacts carried 3.53 A each against their 3.5 A maximum, and their maker
# publishes no current-temperature curve; the decision puts VIN_RAW on four Mill-Max 0858-class pins (9 A continuous at
# a 10 C rise) with four more for its return, and the 813 contacts that carried it become ground.
vr = [r for r, p in B["A"][0].get("VIN_RAW", set()) if r.startswith("J_VR")]
vn = [r for r, p in B["A"][0].get("GND", set()) if r.startswith("J_VN")]
check(len(vr) == 4 and len(vn) == 4, "A: four VIN_RAW power pins and four return pins on the dock block (EQ-16)",
      "VIN_RAW %s, return %s" % (sorted(vr), sorted(vn)), boards={"A"})
check(B["E"][1].get(("P_VR", "1"), "") == "VIN_RAW" and B["E"][1].get(("P_VN", "1"), "") == "GND",
      "E: the 12 AWG lands P_VR on VIN_RAW and P_VN on GND to the block's VIN_RAW pins (EQ-16)",
      "%s / %s" % (B["E"][1].get(("P_VR", "1"), "absent"), B["E"][1].get(("P_VN", "1"), "absent")), boards={"E"})
_vr813 = sorted(["A J_DOCK.%d" % k for k in range(1, 13) if ma.get(k) == "VIN_RAW"] +
                ["E J_BLK.%d" % k for k in range(1, 13) if me.get(k) == "VIN_RAW"])
check(not _vr813, "no Preci-Dip 813 signal contact of the dock carries VIN_RAW (EQ-16)", ", ".join(_vr813) or "none",
      boards={"A", "E"})
'''
if s.count(old) != 1: raise SystemExit("patch_check_contracts_dock: the old text is not there exactly once")
s = s.replace(old, new); assert s != o
compile(s, p, "exec")
open(p, "w", encoding="utf-8").write(s); print("patch_check_contracts_dock: %s edited" % p)
