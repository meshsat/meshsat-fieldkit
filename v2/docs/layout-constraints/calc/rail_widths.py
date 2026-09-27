#!/usr/bin/env python3
"""Power band widths and barrel counts per declared rail, per board: the numbers the layout constraint sheets quote.

MESHSAT-1357, 27 September 2026 (handover layer 9). A VIEW, never an authority: every current comes from the board's
committed intent file (`v2/ecad/<project>/out/<board>-intent.json`, the declaration dc_drop and via_current read),
every width from `v2/ecad/tools/track_current.width_for_current` (decision 35's ruled model, the most conservative of
the three ECSS-Q-ST-70-12C Annex D fits, at a 10 K rise), and every barrel count from
`v2/ecad/tools/via_current.barrels_for` (the fabricator's 18 um hole plating, the same model). This script adds no
number of its own except the copper thickness per board, which it takes from the stack the board is declared or ruled
to be built on (`stackup_write.STACKS` rows, named per board below with the ruling behind each).

WHICH CURRENT GOVERNS, as the rules in the tree state it:
  * a conductor (PI-001, dc_drop.py lines 258 to 264): the rail's TYPICAL current, IPC's 10 K rise being a
    steady-state limit;
  * a barrel (PI-003, via_current.py): the PEAK current, a barrel having almost no thermal mass;
  * the PACK PATH (the session's ruling PWR-F12 of 26 September 2026, v2/docs/feasibility/POWER-THERMAL.md section 10,
    draft v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml): 18 A for 60 s is a SERVICE current for every PA
    key-down, so its conductors are judged at 18 A, "unless a transient thermal analysis of that copper at 60 s shows
    otherwise". No such analysis exists at e3aedb25, so the steady-state width at 18 A is the constraint. The ruling
    names board A's pack path; the same chain stages cross boards E, E5 and P (pcb_energy_chain.yaml DOCK_ENTRY,
    DOCK_BLOCK, PACK_CELLS, PACK_FETS), so the sheets carry it there too and say so.

Pure stdlib plus the two tool modules; no KiCad, runs in well under a second on any host.
Usage: rail_widths.py [--board a|b|c|d|e|p] [--markdown]
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))          # the repository root
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
import track_current as tc          # noqa: E402
import via_current as vc            # noqa: E402

# board: (intent file, stack name, outer copper mm, inner copper mm, the source of the stack, pack-path rails)
BOARDS = {
    "a": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json", "JLC06161H-3313", 0.035, 0.0152,
          "six layers, measured (LAYER-DECISIONS-2026-09-11.md, A arm 345 open at four); copper weight OPEN",
          ("CELL+", "CELL_FUSED", "VBAT")),
    "b": ("v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json", "JLC06161H-3313", 0.035, 0.0152,
          "six layers as built; eight (JLC08161H-2116, the same copper) under decision 43's measurement", ()),
    "c": ("v2/ecad/pcb-c-display-c8/out/pcb-c-display-intent.json", "JLC06161H-3313", 0.035, 0.0152,
          "six layers, owner decision 27 (board file still four, JLC04161H-7628, the same copper)", ()),
    "d": ("v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json", "JLC04161H-7628", 0.035, 0.0152,
          "four layers, the RF ground-plane reason (LAYER-DECISIONS-2026-09-11.md)", ()),
    "e": ("v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock-intent.json", "JLC04161H-7628", 0.035, 0.0152,
          "four layers, the routing half and In1 (LAYER-DECISIONS-2026-09-11.md)", ("CELL+", "CELL_F")),
    "p": ("v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json", "JLC04162H-7628", 0.070, 0.0152,
          "four layers 2 oz outer, owner decision 28; inner weight OPEN (0.5 oz default shown)",
          ("PACK_P", "CELL4", "FUSED", "SCP_OUT", "PACK_N")),
}
PACK_SERVICE_A = 18.0          # PWR-F12, 60 s
DRILLS = (0.3, 0.4, 0.5)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def w(amps, cu_mm, internal):
    return tc.width_for_current(amps, oz=cu_mm / 0.035, internal=internal)


def rows(letter):
    ipath, stack, cu_out, cu_in, why, pack = BOARDS[letter]
    full = os.path.join(ROOT, ipath)
    it = json.load(open(full))
    out = []
    for net, r in (it.get("rails") or {}).items():
        typ, peak = float(r.get("amps_typ") or 0), float(r.get("amps_peak") or 0)
        if typ <= 0 and peak <= 0:
            continue
        is_pack = net in pack
        gov_a = PACK_SERVICE_A if is_pack else typ
        out.append({
            "net": net, "volts": r.get("volts"), "v_work": r.get("v_work"), "typ": typ, "peak": peak,
            "returns": r.get("returns"), "pack": is_pack, "gov_a": gov_a,
            "gov_basis": "PWR-F12 18 A / 60 s" if is_pack else "typical (PI-001)",
            "w_out": w(gov_a, cu_out, False), "w_in": w(gov_a, cu_in, True),
            "w_out_split2": w(gov_a / 2.0, cu_out, False),
            "barrels": {d: vc.barrels_for(max(peak, gov_a), d) for d in DRILLS},
        })
    return {"letter": letter, "intent": ipath, "intent_sha16": sha16(full), "written": it.get("written"),
            "stack": stack, "cu_out": cu_out, "cu_in": cu_in, "stack_why": why, "rows": out}


def markdown(t):
    L = []
    L.append("Intent `%s` sha256/16 %s (written %s); stack %s, outer %.4f mm, inner %.4f mm (%s)."
             % (t["intent"], t["intent_sha16"], t["written"], t["stack"], t["cu_out"], t["cu_in"], t["stack_why"]))
    L.append("")
    L.append("| rail | V (working) | typ / peak A | governing A | outer mm | two outer faces, each mm | inner mm | barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill |")
    L.append("|---|---|---|---|---:|---:|---:|---|")
    for r in t["rows"]:
        vw = ("%.1f (%.1f)" % (r["volts"], r["v_work"])) if r.get("v_work") else "%.2f" % r["volts"]
        inner = "%.2f" % r["w_in"]
        if r["w_in"] > 40:
            inner += " (over 40 mm)"
        L.append("| %s%s | %s | %.2f / %.2f | %.1f, %s | %.2f | %.2f | %s | %s |" % (
            r["net"], " (return of %s)" % r["returns"] if r.get("returns") else "", vw, r["typ"], r["peak"],
            r["gov_a"], r["gov_basis"], r["w_out"], r["w_out_split2"], inner,
            " / ".join(str(r["barrels"][d]) for d in DRILLS)))
    return "\n".join(L)


def main(a):
    only = a[a.index("--board") + 1] if "--board" in a else None
    for letter in BOARDS:
        if only and letter != only:
            continue
        t = rows(letter)
        if "--markdown" in a:
            print("### Board %s" % letter.upper()); print(); print(markdown(t)); print()
        else:
            print(json.dumps(t, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
