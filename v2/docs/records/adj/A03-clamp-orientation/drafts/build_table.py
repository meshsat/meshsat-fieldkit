# Builds the clamp/diode table from primary artefacts only:
#   committed generator netlists (v2/ecad/<phase dir>/out/*.net at 82dd1e4d, clamp-level parity with a HEAD regeneration: box/regen_clamp_parity.json)
#   committed phase boards (runner text parse runner/board_<b>.json; pcbnew read box/pcbnew_clamps.json)
#   LCSC product records (lcsc/C*.json, fetched this session) and maker datasheets (ds/)
import sys, json, csv, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from net_diodes import load
REPO = "$REPO/v2/ecad"
BOARDS = [("a", "A32", "pcb-a-power-a23", "pcb-a-power"), ("b", "B21", "pcb-b-compute-b19", "pcb-b-compute"),
          ("c", "C24", "pcb-c-display-c8", "pcb-c-display"), ("d", "D12", "pcb-d-aprs-d9", "pcb-d-aprs"),
          ("e", "E17", "pcb-e1-dock-e7", "pcb-e1-dock"), ("p", "P4", "pcb-p-pack-p2", "pcb-p-pack")]
RETURNS = {"GND", "GND_V", "PACK_N"}
# expected cathode net for rectifiers, with the source that fixes it
RECT = {("c", "D17"): ("TX_LAMPTEST", "PANEL.md:85 'TX_LAMPTEST (output): low lights the TX lamp through the BAT54 tie D17'"),
        ("c", "D19"): ("EPD_VGH", "PDi EPD Driving Circuit Rev.02 p.3 figure: SS2040FL anode on the L1/MOSFET switch node, cathode on VGH (pin 21) with 1uF to GND"),
        ("c", "D20"): ("GND", "PDi Rev.02 p.3 figure: pump diode anode on the pump node, cathode on GND"),
        ("c", "D21"): ("EPD_PUMP", "PDi Rev.02 p.3 figure: VGL diode cathode on the pump node, anode on VGL (pin 23, 'Negative Gate driving voltage', p.7)"),
        ("d", "D2"): ("+5V_D8", "relay flyback: K1 coil pin 1 on +5V_D8, pin 8 RLY_K switched low by Q2 (gen_sch_d.py:286-288)"),
        ("e", "D5"): ("TRK_BOOST1", "LT8705A bootstrap: INTVCC -> BOOST1 (gen_sch_e.py:292 label; C17 BOOST1-SW1)"),
        ("e", "D6"): ("TRK_BOOST2", "LT8705A bootstrap: INTVCC -> BOOST2 (gen_sch_e.py:292 label; C18 BOOST2-SW2)"),
        ("e", "D7"): ("CELL_F", "fan flyback: fan between CELL_F and FAN1_SW, Q9 low side (gen_sch_e.py:376-379)"),
        ("e", "D8"): ("CELL_F", "fan flyback: fan between CELL_F and FAN2_SW, Q10 low side (gen_sch_e.py:376-379)")}
LCSC_FILL = {"SMBJ5.0A": "C113974", "SMBJ18A": "C151256", "SMCJ33A": "C42371548", "BAT54": "C7502705", "SS14": "C51897884",
             "SS2040FL": "C268712", "USBLC6-2SC6": "C7519"}   # lcsc_fill.py:45,53,59,117,138-140
BOM_P4 = {"D1": "C364296"}   # release/revA/boards/meshsat-pcb-p-revA-P4/pcb-p-pack-bom.csv
LSUM = json.load(open(os.path.join(H, "lcsc", "lcsc_summary.json")))["records"]
def lcsc_rec(code):
    r = LSUM.get(code)
    if not r or "productModel" not in r: return None
    return "%s %s (%s)" % (r["brand"], r["productModel"], r.get("polarity") or r.get("config") or "?")
pcbn = json.load(open(os.path.join(H, "box", "pcbnew_clamps.json")))
rows = []
for b, phase, pdir, name in BOARDS:
    net = load(os.path.join(REPO, pdir, "out", name + ".net"))
    brd = json.load(open(os.path.join(H, "runner", "board_%s.json" % b)))
    pk = [k for k in pcbn if k.startswith(pdir + "/")][0]; pb = pcbn[pk]["parts"]
    refs = sorted(set(r for r, c in net.items() if (c["part"] in ("D_TVS", "D_Schottky", "1N4148W", "USBLC6-2SC6"))) |
                  set(r for r in brd["parts"] if r in net or r.startswith("D")), key=lambda s: (s[0], int("".join(ch for ch in s if ch.isdigit()) or 0)))
    for ref in refs:
        n = net.get(ref); bd = brd["parts"].get(ref); pc = pb.get(ref)
        if n is None and bd is None: continue
        if n and n["part"] not in ("D_TVS", "D_Schottky", "1N4148W", "USBLC6-2SC6"): continue
        val = (n or {}).get("value") or bd["value"]; short = val.split(" ")[0].rstrip(":")
        lcsc = (n or {}).get("fields", {}).get("LCSC") or ""
        src = "netlist"
        if not lcsc and b == "p" and ref in BOM_P4: lcsc, src = BOM_P4[ref], "P4 BOM"
        if not lcsc and short in LCSC_FILL: lcsc, src = LCSC_FILL[short], "lcsc_fill.py"
        board_val = bd["value"].split(" ")[0] if bd else "ABSENT"
        sym = ("%s:%s" % (n["lib"], n["part"])) if n else "?"
        fp = (n or {}).get("footprint") or ("?:" + bd["lib"])
        npins = {p: v[0].lstrip("/") for p, v in (n["pins"] if n else {}).items()}
        bpins = {p: (v["net"] or "").lstrip("/") for p, v in (bd["pads"] if bd else {}).items()}
        cath_pad = None
        if bd and set(bd["pads"]) == {"1", "2"}:
            fab = [a[0] for a in pc["fab_apex_nearest_pad"]] if pc else []
            silk = (pc.get("silk_centroid_nearest_pad") or [None])[0] if pc else None
            cath_pad = "1" if (fab == ["1"] and silk == "1" and bd.get("silk_vertical_on_pad1_side")) else "CHECK"
        elif n and n["part"] != "USBLC6-2SC6":
            cath_pad = "1 (library D_SOD-323/D_SMC land, not on this board)"
        # uni/bi
        if n and n["part"] == "USBLC6-2SC6": kind = "array (ST DS4260 Rev 7 pinout)"
        elif "PESD5V0S1BA" in val: kind = "BIDIRECTIONAL (Nexperia PESD5V0S1BA v.6 2024-04-26; LCSC C19224 'Bidirectional')"
        elif short.startswith(("SMBJ", "SMCJ")): kind = "UNIDIRECTIONAL (A suffix; CA = bidirectional: Vishay 88392/88394 rev 09-Jan-2024, Littelfuse SMCJ rev 11/20/15)"
        else: kind = "rectifier (K = symbol pin 1)"
        rec = lcsc_rec(lcsc)
        # verdicts
        orient = sym_v = ""
        pin1 = npins.get("1") if n else bpins.get("1")
        if n and n["part"] == "USBLC6-2SC6":
            ok = npins.get("2") == "GND" and npins.get("1") == npins.get("6") and npins.get("3") == npins.get("4") and npins.get("5") not in RETURNS
            orient = "PIN MAP OK" if ok else "PIN MAP WRONG"; sym_v = "OK"
            expected = "pin2 GND, pin5 VBUS supply, pins 1=6 and 3=4 I/O"
        elif "PESD5V0S1BA" in val:
            orient = "N/A (bidirectional)"; sym_v = "OK (D_TVS is the bidirectional symbol)"; expected = "either pad"
        elif short.startswith(("SMBJ", "SMCJ")):
            rail = [x for x in (npins or bpins).values() if x not in RETURNS]
            expected = "cathode (pad 1) on %s" % (rail[0] if rail else "?")
            orient = "CORRECT" if pin1 not in RETURNS else "REVERSED"
            sym_v = "WRONG (Device:D_TVS is 'Bidirectional', pins A1/A2, no cathode; a unidirectional part needs a K/A symbol)"
        else:
            exp, why = RECT[(b, ref)]
            expected = "cathode (pad 1) on %s: %s" % (exp, why)
            orient = "CORRECT" if pin1 == exp else "REVERSED"; sym_v = "OK (K = pin 1)"
        rows.append(dict(board=b.upper(), phase=phase, ref=ref, part=short, value_netlist=(n or {}).get("value", "ABSENT"),
                         value_board=board_val, lcsc=lcsc, lcsc_source=src, lcsc_record=rec or "TBD (no LCSC record)", polarity=kind,
                         symbol=sym, footprint=fp, netlist_pins=json.dumps(npins) if n else "ABSENT",
                         board_pads=json.dumps(bpins) if bd else "ABSENT on %s" % phase,
                         cathode_pad_on_footprint=cath_pad or "n/a", expected=expected, orientation_verdict=orient, symbol_verdict=sym_v,
                         board_line=("%s/%s.kicad_pcb:%d" % (pdir, name, bd["line"])) if bd else ""))
# E5: no schematic, no netlist, no diode footprint
rows.append(dict(board="E5", phase="E5", ref="(none)", part="", value_netlist="no netlist", value_board="no diode footprint (17 footprints: Mill-Max targets, holes, pogo target, wire lands)",
                 lcsc="", lcsc_source="", lcsc_record="", polarity="", symbol="", footprint="", netlist_pins="", board_pads="", cathode_pad_on_footprint="",
                 expected="", orientation_verdict="NO PARTS", symbol_verdict="", board_line="pcb-e5-block/pcb-e5-block.kicad_pcb (686b29a734c55b9a)"))
with open(os.path.join(H, "..", "clamp_table.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
json.dump(rows, open(os.path.join(H, "..", "clamp_table.json"), "w"), indent=1)
for r in rows:
    print("%-2s %-4s %-5s %-12s %-9s %-10s %-26s | n:%s | b:%s | cath:%s | %s | %s" % (r["board"], r["phase"], r["ref"], r["part"], r["lcsc"], r["value_board"][:10], r["symbol"], r["netlist_pins"][:70], r["board_pads"][:60], r["cathode_pad_on_footprint"][:6], r["orientation_verdict"], r["symbol_verdict"][:5]))
