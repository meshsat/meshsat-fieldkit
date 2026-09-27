"""r8int5: board A's half of EQ-16 on board A's w3a generator. Runs stream w3de's patch_gen_sch_a_dock.py (its hunks
match w3a's gen_sch_a.py, which changed none of the lines they touch), then corrects two comments the independent
checks of w3de found wrong or stale (check 1: the return pins do not keep VIN_RAW's return off the 813 ground contacts,
dock_contacts.py puts about half the ground current on them, and the residual at a 2:1 spread is higher; check 2: the
round 4 paragraph above _VIN_RAW_A still describes four 813 contacts carrying VIN_RAW), and points the comment at the
filed record. Comments only: the netlist is what the drafted patch alone makes. Usage: <tree root>"""
import os, subprocess, sys
root = sys.argv[1]
K = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(root, "v2", "ecad", "tools", "gen_sch_a.py")
if "J_VR%d" not in open(p).read():
    subprocess.run([sys.executable, os.path.join(K, "patch_gen_sch_a_dock.py"), root], check=True)
s = open(p, encoding="utf-8").read(); o = s
EDITS = [
 ("""# one open (52 percent, about 3 K of rise). The four return pins keep VIN_RAW's return off the 813 ground contacts and
# the pack's return pins: at the conservative 32.1 A of ground current (14.10 A and the pack's 18.0 A at once) an 813
# ground contact carries at most about 2.2 A with one open (drafts/w3de/dock_contacts.py). E5 carries their targets and
# two 12 AWG holes to board E's P_VR and P_VN.""",
  """# one open (52 percent, about 3 K of rise). The four return pins take part of the ground current, not all of it: the
# dock's ground current shares the pack's return pins, these four and the eight 813 ground contacts in the ratio of
# their resistances, which the makers bound only from above, so about half of it still crosses the 813 contacts. At the
# conservative 32.1 A of ground current (14.10 A and the pack's 18.0 A at once) an 813 ground contact carries about
# 2.1 A with even sharing and 2.2 A with one open, and 2.44 to 2.58 A at a 2:1 spread among the eight, which at the +55 C
# margin reaches about 94 to 98 C under the assumed 60 K rise at 3.5 A, over the 813's 85 C: finding W3DE-DOCK-R1, a
# bench measurement owed (v2/docs/records/w3de/dock_contacts.py and EQ16-dock-vin-raw.md). E5 carries their targets and
# two 12 AWG holes to board E's P_VR and P_VN."""),
 ("""# tracker's 10.33 A can supply together); the 12.31 A above was the sum of board E's two earlier figures.
""",
  """# tracker's 10.33 A can supply together); the 12.31 A above was the sum of board E's two earlier figures. The round 4
# paragraph above is that history: since EQ-16 the four 813 contacts of J_DOCK carry no VIN_RAW (J_VR1 to J_VR4 do), so
# R4A-N13's supply half and R8E-N01 are answered, and IF-AE-DOCK declares this one figure at both ends.
"""),
]
for old, new in EDITS:
    if new in s: continue
    if s.count(old) != 1: raise SystemExit("patch_gen_sch_a_dock_r8int5: the old text is not there once: %r" % old[:90])
    s = s.replace(old, new)
compile(s, p, "exec")
if s != o: open(p, "w", encoding="utf-8").write(s)
print("patch_gen_sch_a_dock_r8int5: done")
