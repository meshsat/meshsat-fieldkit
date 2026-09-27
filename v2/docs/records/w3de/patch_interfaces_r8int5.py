"""r8int5: the IF-AE-DOCK contract after EQ-16, stream w3de's patch_interfaces_if_ae_dock.py plus the two corrections
w3de check 2's first blocking item asks for, done exactly as stated: a_declares and e_declares read the one figure both
ends now carry (14.10 A) and say R8E-N01 is answered; ends[a].src cites the lines of this set's gen_sch_a.py. Also (the
same checks' minors): pack_pins.rating cites the held Mill-Max page instead of 'no datasheet held (TBD)', the ground
return records the 2:1 contact spread case, and the drafts/w3de/ paths name the filed records. Usage: <tree root>"""
import os, subprocess, sys
root = sys.argv[1]; K = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(root, "v2", "ecad", "tools", "pcb_interfaces.yaml")
if "pins_history: \"1 to 4 carried VIN_RAW until EQ-16" not in open(p).read():
    subprocess.run([sys.executable, os.path.join(K, "patch_interfaces_if_ae_dock.py"), root], check=True)
s = open(p, encoding="utf-8").read(); o = s
i = s.index("\n    IF-AE-DOCK:\n"); j = s.index("\n    IF-PE-PACK:\n")
blk = s[i:j]
EDITS = [
 ('''        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1, J_VR1-4, J_VN1-4], src: "v2/ecad/tools/gen_sch_a.py:206-210, 226-227 and the EQ-16 pins after J_PRE1 (drafts/w3de/patch_gen_sch_a_dock.py)"}''',
  '''        - {board: a, refs: [J_DOCK, J_CP1-4, J_CN1-4, J_PRE1, J_VR1-4, J_VN1-4], src: "v2/ecad/tools/gen_sch_a.py:216-219 (J_CP1-4, J_CN1-4, J_PRE1), 235-237 (J_VR1-4, J_VN1-4), 265-266 (J_DOCK) at the set 5 integration (fnd/r8int5)"}'''),
 ('''        - {board: e, refs: [J_BLK, P_CP, P_CN, P_VR, P_VN], src: "v2/ecad/tools/gen_sch_e.py: P_CP and P_CN at the pack entry, J_BLK, P_VR and P_VN at the block lands (EQ-16)"}''',
  '''        - {board: e, refs: [J_BLK, P_CP, P_CN, P_VR, P_VN], src: "v2/ecad/tools/gen_sch_e.py:242-243 (P_CP, P_CN), 660-663 (J_BLK, P_VR, P_VN) at the set 5 integration (fnd/r8int5)"}'''),
 ('''                a_declares: "12.31 A typical and peak: board E's vehicle entry at its hot swap's maximum limit (6.15 A) and
                  its solar tracker (6.16 A) ORed onto one bus, which A's front end can draw (gen_sch_a.py:49-66)",''',
  '''                a_declares: "14.10 A typical and peak since R8E-N01 (EQ-16, set 5, fnd/r8int5, 27 September 2026): board
                  E's figure, this board's own front end at its ISNS limit drawing from a 9.0 V bus (R4A-N12), with J_VR1 to
                  J_VR4 as its source (gen_sch_a.py:69-70 at the set 5 integration). Until then 12.31 A, the sum of E's two
                  earlier figures (the vehicle entry's 6.15 A and the tracker's 6.16 A)",'''),
 ('''                  9.0 V bus at its ISNS limit (5.7 A at 20.7 V over 0.93 is 126.9 W, SNVSAI1D VSNS 57 mV maximum). A's own
                  12.31 A (the sum of E's two earlier figures) is below it: R8E-N01, board A's item",''',
  '''                  9.0 V bus at its ISNS limit (5.7 A at 20.7 V over 0.93 is 126.9 W, SNVSAI1D VSNS 57 mV maximum). Both
                  ends carry this one figure since set 5 (board A declares 14.10 A too): R8E-N01 is answered (EQ-16)",'''),
 ('''      pack_pins: {rating: "9 A per pin per the generator description (gen_sch_a.py:208-209); no Mill-Max datasheet held (TBD)",''',
  '''      pack_pins: {rating: "9 A per pin: 'Rated Current (Free air): Continuous 9 amps @ 10 C temperature rise', 'Contact Resistance: 20 mOhm max' (v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf, VERIFIED; the series statement, the 0858 being on the held product page)",'''),
 ('''        86 to 90 C under the assumed 60 K rise at 3.5 A (the maker publishes none), over its 85 C; a bench measurement''',
  '''        86 to 90 C under the assumed 60 K rise at 3.5 A (the maker publishes none), over its 85 C; with a 2:1 resistance
        spread among the eight 813 ground contacts (the independent check of w3de) the lowest carries 2.44 A, 2.58 A with
        one open, which reads 80.3 and 83.6 C at the 51 C inside air and 94 to 98 C at the +55 C margin; a bench measurement'''),
]
for old, new in EDITS:
    if new in blk: continue
    if blk.count(old) != 1: raise SystemExit("patch_interfaces_r8int5: not there once: %r" % old[:90])
    blk = blk.replace(old, new)
blk = blk.replace("drafts/w3de/dock_contacts.py", "v2/docs/records/w3de/dock_contacts.py")
s = s[:i] + blk + s[j:]
import yaml
c = yaml.safe_load(s)["board_to_board"]["contracts"]["IF-AE-DOCK"]
assert "14.10 A" in c["vin_raw"]["a_declares"] and "R8E-N01 is answered" in c["vin_raw"]["e_declares"]
if s != o: open(p, "w", encoding="utf-8").write(s)
print("patch_interfaces_r8int5: done")
