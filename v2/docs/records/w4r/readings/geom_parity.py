# w4r geometry parity: J_DOCK offsets from the library land mounted as block_contract.DOCK_MOUNT says, against the
# offsets of J_DOCK as placed on board A's committed board file; and the pin-under-target map both give on E5.
import sys, os
sys.path.insert(0, "/root/w4r/clone/v2/ecad/tools")
import pcbnew, block_contract as B
E = "/root/w4r/clone/v2/ecad"
lib, lf = B.dock_offsets("meshsat:PogoPins_2x6")
a = pcbnew.LoadBoard(os.path.join(E, "pcb-a-power-a23", "pcb-a-power.kicad_pcb"))
jd = a.FindFootprintByReference("J_DOCK"); o = jd.GetPosition()
brd = {B._key(p, o): int(p.GetNumber()) for p in jd.Pads()}
print("J_DOCK on board A: flipped", jd.IsFlipped(), "orientation", jd.GetOrientationDegrees(), "fpid", jd.GetFPIDAsString())
print("land-derived offsets == board-file offsets:", lib == brd, len(lib), len(brd))
e5 = pcbnew.LoadBoard(os.path.join(E, "pcb-e5-block", "pcb-e5-block.kicad_pcb"))
t = e5.FindFootprintByReference("T_SIG"); tp = t.GetPosition()
m1 = {int(p.GetNumber()): lib.get(B._key(p, tp)) for p in t.Pads()}
m2 = {int(p.GetNumber()): brd.get(B._key(p, tp)) for p in t.Pads()}
print("target -> pin (land):", sorted(m1.items())); print("same map from board file:", m1 == m2)
