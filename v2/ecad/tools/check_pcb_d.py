#!/usr/bin/env python3
"""Numeric verification of PCB-D phase D1 against PCB-A's site and the DMR858M datasheet."""
import sys, pcbnew, itertools, math
OX, OY = 100.0, 100.0
def case(v): return (round(v.x / 1e6 - OX, 3), round(OY - v.y / 1e6, 3))
b = pcbnew.LoadBoard(sys.argv[1]); fails = []
def check(c, m):
    print(("PASS " if c else "FAIL ") + m)
    if not c: fails.append(m)
segs = [(case(d.GetStart()), case(d.GetEnd())) for d in b.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts and d.GetShape() == pcbnew.SHAPE_T_SEGMENT]
pts = [p for s in segs for p in s]
x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts); y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
check(abs(x1 - x0 - 80) < 0.005 and abs(y1 - y0 - 62) < 0.005 and abs(x0 + 40) < 0.005 and abs(y1 - 31) < 0.005, "outline 80 x 62 centred (X %.2f..%.2f Y %.2f..%.2f)" % (x0, x1, y0, y1))
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
holes = {r: (case(fp.GetPosition()), round(list(fp.Pads())[0].GetDrillSize().x / 1e6, 2)) for r, fp in fps.items() if r.startswith("H")}
def find(pos, drill): return any(abs(v[0][0] - pos[0]) < 0.01 and abs(v[0][1] - pos[1]) < 0.01 and abs(v[1] - drill) < 0.01 for v in holes.values())
for (x, y) in [(-35, -26), (35, -26), (-35, 26), (35, 26)]: check(find((x, y), 3.2), "M3 standoff hole 3.2 at (%d, %d) = PCB-A site (10/80, +-26)" % (x, y))
# module pads: 24, two rows 2.54 pitch, per datasheet V1.2 p.10 (rotated: SMA east)
u2 = fps.get("U2"); check(u2 is not None, "U2 DMR858M placed")
if u2:
    pads = {p.GetNumber(): case(p.GetPosition()) for p in u2.Pads() if p.GetNumber()}
    check(len(pads) == 24, "U2 has 24 pads (%d)" % len(pads))
    mc = case(u2.GetPosition()); ys = sorted(set(round(p[1], 2) for p in pads.values()))
    check(len(ys) == 2 and abs(ys[1] - ys[0] - 36.15) < 0.02, "two pin rows %.3f mm apart (module 38.69 wide, holes 1.27 mm inboard)" % (ys[1] - ys[0] if len(ys) == 2 else 0))
    for n in range(1, 12): check(abs(pads[str(n)][0] - pads[str(n + 1)][0] - 2.54) < 0.01 and pads[str(n)][1] > mc[1], "pin %d east of pin %d by 2.54 on the NORTH row (datasheet front-left row)" % (n, n + 1))
    for n in range(13, 24): check(abs(pads[str(n + 1)][0] - pads[str(n)][0] - 2.54) < 0.01 and pads[str(n)][1] < mc[1], "pin %d east of pin %d by 2.54 on the SOUTH row (datasheet front-right row)" % (n + 1, n))
    drills = {round(p.GetDrillSize().x / 1e6, 2) for p in u2.Pads() if p.GetNumber()}
    check(drills == {1.0}, "module pin holes drill 1.0 for 2.54 mm sockets (%s)" % sorted(drills))
    npth = [case(p.GetPosition()) for p in u2.Pads() if not p.GetNumber()]
    exp = [(mc[0] + 58.31 / 2 - 2.81, mc[1] + 38.69 / 2 - 2.96), (mc[0] - 58.31 / 2 + 2.86, mc[1] - 38.69 / 2 + 2.73)]
    check(len(npth) == 2 and all(any(abs(a[0] - e[0]) < 0.01 and abs(a[1] - e[1]) < 0.01 for a in npth) for e in exp), "two M2.5 standoff holes at the module's 3.00 mm holes (NE 2.81/2.96, SW 2.86/2.73)")
    check(abs(pads["1"][0] - pads["24"][0]) < 0.01 and abs(pads["12"][0] - pads["13"][0]) < 0.01, "rows aligned: pin 1 over pin 24, pin 12 over pin 13")
    check(abs(pads["1"][0] - (mc[0] + 14.095)) < 0.01, "pin 1 at 15.06 mm from the module's SMA edge (%.3f)" % (pads["1"][0] - mc[0]))
    check(mc[0] + 58.31 / 2 <= 41.5 and mc[0] - 58.31 / 2 >= -20.0, "module PCB (58.31 long) with its SMA end at most 1.5 mm past the east edge (centre X %.2f)" % mc[0])
# connectors where the harness expects them; everything inside the outline; nothing on a standoff face
for ref, (ex, ey) in {"J_HARN1": (-33, 6), "J_PWR1": (-33, -14)}.items():
    fp = fps.get(ref)
    if fp is None: check(False, "%s present" % ref); continue
    bb = fp.GetBoundingBox(False, False); cx = (bb.GetLeft() + bb.GetRight()) / 2e6 - OX; cy = OY - (bb.GetTop() + bb.GetBottom()) / 2e6
    check(abs(cx - ex) < 0.6 and abs(cy - ey) < 0.6, "%s body centred at (%.1f, %.1f) (got %.2f, %.2f)" % (ref, ex, ey, cx, cy))
bad = []
for ref, fp in fps.items():
    if ref.startswith("H"): continue
    bb = fp.GetBoundingBox(False, False); l, r_, t, bt = bb.GetLeft() / 1e6 - OX, bb.GetRight() / 1e6 - OX, OY - bb.GetTop() / 1e6, OY - bb.GetBottom() / 1e6
    if ref == "U2":   # the module body: 58.31 x 38.69 around its centre, SMA end may pass the edge by 1.5 mm
        mc = case(fp.GetPosition()); l, r_, bt, t = mc[0] - 29.155, min(mc[0] + 29.155, 39.7), mc[1] - 19.345, mc[1] + 19.345
    if l < -39.7 or r_ > 39.7 or bt < -30.7 or t > 30.7: bad.append(ref)
    for (sx, sy) in [(-35, -26), (35, -26), (-35, 26), (35, 26)]:
        cx = max(l, min(sx, r_)); cy = max(bt, min(sy, t))
        if math.hypot(cx - sx, cy - sy) < 3.75: bad.append(ref + "@standoff")
check(not bad, "all footprints inside the outline and off the standoff faces (%s)" % bad)
check(b.GetCopperLayerCount() == 4, "4 copper layers"); check(b.GetDesignSettings().GetBoardThickness() == pcbnew.FromMM(1.6), "1.6 mm thick")
# ---------------------------------------------------------------- D7 content (MESHSAT-804, appendix 32.38): the parts and nets that fit the DMR858M V1.0 board
def nets_of(ref):
    fp = fps.get(ref); return {pd.GetNumber(): pd.GetNetname() for pd in fp.Pads()} if fp else {}
def reach(net, ref):
    """True if a pad of footprint `ref` sits on `net`."""
    return net in nets_of(ref).values()
if "U5" in fps:   # only after the netlist import and placement (the D1 mechanical board carries just the module socket and the connectors)
    check("U7" in fps and "TSSOP-24" in fps["U7"].GetFPIDAsString(), "U7 is the PCA9555 (TSSOP-24), not the PCA9536")
    u7 = nets_of("U7")
    check(u7.get("21") == "GND" and u7.get("2") == "+3V3_AB" and u7.get("3") == "+3V3_AB", "U7 address pins A0 = 0, A1 = 1, A2 = 1: 0x26 (got A0 %s, A1 %s, A2 %s)" % (u7.get("21"), u7.get("2"), u7.get("3")))
    check("U8" in fps and "TSSOP-16" in fps["U8"].GetFPIDAsString(), "U8 the SC16IS740 bridge (TSSOP-16) present")
    u8 = nets_of("U8")
    check(u8.get("2") == "+3V3_AB" and u8.get("3") == "+3V3_AB" and u8.get("8") == "+3V3_AB" and u8.get("11") == "GND" and u8.get("15") == "MCLK", "U8 strapped for I2C at 0x48 (A0, A1, I2C/SPI high), CTS low, 24 MHz on XTAL1")
    check(not any(r in fps for r in ("JP1", "JP2", "JP3", "JP4", "JP5", "J_UART1")), "no channel jumpers and no bench UART header on the board")
    u2 = nets_of("U2")
    check(u2.get("16") == "RADIO_COS", "module pin 16 (SPKEN, receive indication output) on RADIO_COS (got %s)" % u2.get("16"))
    check(reach("RADIO_COS", "R42") and reach("RADIO_COS_IN", "R42") and reach("RADIO_COS_IN", "U7"), "carrier detect reaches U7 through R42")
    for pin, net, rr, rp in (("7", "CH8", "R43", "R49"), ("8", "CH4", "R44", "R50"), ("9", "CH2", "R45", "R51"), ("10", "CH1", "R46", "R52")):
        check(u2.get(pin) == net and reach(net, rr) and reach(net + "_IN", rr) and reach(net + "_IN", "U7") and reach(net + "_IN", rp) and reach("GND", rp), "channel code pin %s (%s) reaches U7 through %s with the pull-down %s" % (pin, net, rr, rp))
    check(u2.get("3") == "CS" and reach("CS", "R36") and reach("CS", "R48") and reach("CS_CTL", "U7"), "CS pulled up by R36 and driven by U7 through R48")
    check(u2.get("18") == "RADIO_TX" and u2.get("19") == "RADIO_RX" and reach("RADIO_TX", "R9") and reach("BR_RX", "R9") and reach("BR_RX", "U8") and reach("RADIO_RX", "R8") and reach("BR_TX", "R8") and reach("BR_TX", "U8"), "module control UART reaches U8 through R8 and R9")
    check(fps.get("R2") is not None and fps["R2"].GetValue().startswith("47k") and fps.get("R4") is not None and fps["R4"].GetValue().startswith("1k"), "mic divider R2 47k / R4 1k (got %s / %s)" % (fps["R2"].GetValue() if "R2" in fps else None, fps["R4"].GetValue() if "R4" in fps else None))
print("\nRESULT:", "ALL PASS" if not fails else "%d FAIL" % len(fails)); sys.exit(1 if fails else 0)
