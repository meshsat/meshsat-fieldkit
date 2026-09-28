#!/usr/bin/env python3
"""Power band widths and barrel counts per declared rail, per board: the numbers the layout constraint sheets quote.

MESHSAT-1357, 27 September 2026 (handover layer 9; re-run and bound to the H2 line after H2, the same day; re-run on
the set 6 candidate and given its check, `v2/ecad/tools/constraints_bound.py`, that night). A VIEW, never an
authority: every current comes from the board's committed intent file
(`v2/ecad/<project>/out/<board>-intent.json`, the declaration dc_drop and via_current read), and each table names that
file's sha256/16 and the sha256/16 of the committed netlist beside it, so a table says which candidate it was read on;
every width from `v2/ecad/tools/track_current.width_for_current` (decision 35's ruled model, the most conservative of
the three ECSS-Q-ST-70-12C Annex D fits, at a 10 K rise), and every barrel count from
`v2/ecad/tools/via_current.barrels_for` (the fabricator's 18 um hole plating, the same model). The numbers this script
types for itself, each named where it stands: the copper thickness per board, from the stack the board is declared
or ruled to be built on (`stackup_write.STACKS` rows, named per board below with the ruling behind each, and held
equal to that table by constraints_bound.py); the pack path's service current (PWR-F12); and the maker's figures of
SIZED_TO, which are findings of `v2/docs/feasibility/POWER-THERMAL.md` and not declarations.

WHICH CURRENT GOVERNS, as the rules in the tree state it:
  * a conductor (PI-001, dc_drop.py lines 258 to 264): the rail's TYPICAL current, IPC's 10 K rise being a
    steady-state limit;
  * a barrel (PI-003, via_current.py): the PEAK current, a barrel having almost no thermal mass;
  * the PACK PATH (the session's ruling PWR-F12 of 26 September 2026, v2/docs/feasibility/POWER-THERMAL.md section 10,
    draft v2/docs/records/rv-pwr/pwr-chain-redeclaration.yaml): 18 A for 60 s is a SERVICE current for every PA
    key-down, so its conductors are judged at 18 A, "unless a transient thermal analysis of that copper at 60 s shows
    otherwise". No such analysis exists at e3aedb25, at the H2 line or on the set 6 candidate, so the steady-state
    width at 18 A is the constraint. The ruling
    names board A's pack path; the same chain stages cross boards E, E5 and P (pcb_energy_chain.yaml DOCK_ENTRY,
    DOCK_BLOCK, PACK_CELLS, PACK_FETS), so the sheets carry it there too and say so.

WHICH RAILS ARE THE PACK PATH (27 September 2026, set 6; taken by the session under the owner's standing rule of
26 September 2026, authority SESSION). The list per board below names the ROOTS. A rail the intent file itself
declares a series segment (`series_of`) or the return (`returns`) of a pack-path rail, AT THAT RAIL'S OWN TYPICAL AND
PEAK CURRENTS, is pack path too. Why: set 6 declared board P's SW, "the common drain of Q1 and Q2 ... the pack's
whole current: 10 A typical and 18 A peak as SCP_OUT and PACK_P carry it" (its own note, `series_of: SCP_OUT`), and
the typed list did not know it, so the first run on set 6 sized the conductor between the pack's two FETs at 10 A
(4.08 mm at 2 oz) where every other segment of the same conductor is sized at 18 A (11.95 mm). A typed list goes
stale each time a generator names a new segment; the declaration does not. The currents must be equal because
`series_of` is also written on a branch behind a fuse (board B's PANEL_5V is `series_of` +5V_DEV at 0.6 A of its
3.8 A), and a branch is judged at its own current. Reverse by making `pack_path` return the roots alone.

A BOARD WITH NO INTENT FILE (E5, the dock block: copper, plated targets and wire lands, no schematic). Its design is
its board file and its currents are the energy chain's declaration of the stage that crosses it
(`v2/ecad/tools/pcb_energy_chain.yaml`, stage DOCK_BLOCK: `continuous_a` and `peak_a`), on the two nets of its board
file that carry the pack pair. The chain declares no voltage, so that cell says so. Reading the chain needs PyYAML;
the six boards with an intent file need the standard library and the two tool modules alone.

Pure stdlib plus the two tool modules (and PyYAML for E5); no KiCad, runs in well under a second on any host. The
output depends on the committed files alone: no date, no host name, no git, so a second run is the same bytes.
Usage: rail_widths.py [--board a|b|c|d|e|e5|p] [--markdown]
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))          # the repository root
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
import track_current as tc          # noqa: E402
import via_current as vc            # noqa: E402

# THE MODEL'S IDENTITY, stated in every table and in every sheet's `bound` block, and compared by constraints_bound.py.
RISE_K = 10.0                       # decision 35's rise; IPC's steady-state 10 K
MODEL = {"function": "track_current.width_for_current", "decision": 35, "rise_k": RISE_K,
         "plating_um": vc.PLATING_UM}

# board: (intent file, stack name, outer copper mm, inner copper mm, the source of the stack, pack-path ROOT rails)
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
# A board with no schematic and no intent file: its board file is its design, and the currents are the energy chain's
# declaration of the stage that crosses it. `rails` are nets of the board file: (net, the rail it returns or None).
NO_INTENT = {
    "e5": {"board_file": "v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb",
           "chain": "v2/ecad/tools/pcb_energy_chain.yaml", "stage": "DOCK_BLOCK",
           "stack": "2L-2oz", "cu_out": 0.070, "cu_in": None,
           "why": "two layers at 2 oz, owner ruling 7 of 12 September 2026 (STACKUP-DECISIONS.md section 3.7)",
           "rails": (("CELL+", None), ("CELL_N", "CELL+"))},
}
ORDER = ("a", "b", "c", "d", "e", "e5", "p")
PACK_SERVICE_A = 18.0          # PWR-F12, 60 s
DRILLS = (0.3, 0.4, 0.5)

# RAILS WHOSE MAKER ASKS MORE THAN THE BOARD DECLARES (v2/docs/feasibility/POWER-THERMAL.md section 10, findings
# PWR-F01, PWR-F03 and PWR-F05, each VERIFIED there against the maker's own sheet). The declaration stays the committed
# input and the first table is read from it; this second table sizes the same rails at the maker's figure, so the
# width a layout follows until the declaration is corrected is the model's output and not a number typed into a
# sheet. board: ((rail, amps, the finding and what it says), ...). A row whose declaration has reached the maker's
# figure is refused by constraints_bound.py, so an entry cannot outlive the finding it answers.
SIZED_TO = {
    "b": (
        ("+3V3_S1A", 3.0, "PWR-F01: AsiaRF asks a 3.3 V supply of 3 A (2.5 A minimum) for the AW7915-AED"),
        ("+3V3_M2C1", 3.0, "PWR-F01, the same conductor past its Kelvin shunt"),
        ("+3V3_S3A", 3.0, "PWR-F01"),
        ("+3V3_M2C3", 3.0, "PWR-F01, the same conductor past its Kelvin shunt"),
        ("+1V2_KSZ", 1.21, "PWR-F03: KSZ9897R at 1000 Mb/s draws 1.21 A typical on its 1.2 V rails"),
        ("+2V5_KSZ", 0.33, "PWR-F03: 330 mA on AVDDH"),
        ("+1V1_S1", 0.778, "PWR-F05: TUSB8041's four-SS-devices row, 778 mA on VDD; the kit's mix uses the 395 mA row"),
        ("+1V1_S2", 0.778, "PWR-F05"),
        ("+1V1_S3", 0.778, "PWR-F05"),
    ),
}

HEAD = ("rail", "V (working)", "typ / peak A", "governing A", "outer mm", "two outer faces, each mm", "inner mm",
        "barrels at the larger of peak and governing, 0.3 / 0.4 / 0.5 mm drill")
HEAD_SIZED = ("rail", "declared typ / peak A", "sized at, A", "outer mm", "two outer faces, each mm", "inner mm",
              "barrels at the larger of the declared peak and the sized current, 0.3 / 0.4 / 0.5 mm drill",
              "the maker's figure and its finding")
ALIGN = {"outer mm": "---:", "two outer faces, each mm": "---:", "inner mm": "---:"}
NO_INNER = "no inner layer"
NO_VOLTS = "not declared by the chain"


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def w(amps, cu_mm, internal):
    return tc.width_for_current(amps, oz=cu_mm / 0.035, dT=RISE_K, internal=internal)


def barrels(amps):
    return {d: vc.barrels_for(amps, d, rise_k=RISE_K) for d in DRILLS}


def pack_path(rails, roots):
    """{rail: why} of the rails judged at the pack's service current: the roots this board's entry names that the
    intent file declares, and every rail the intent file declares a series segment or the return of one of them at
    that rail's own typical and peak currents (the module docstring, WHICH RAILS ARE THE PACK PATH)."""
    pack = {n: "" for n in roots if n in rails}
    moved = True
    while moved:
        moved = False
        for net, r in rails.items():
            if net in pack: continue
            for key, word in (("series_of", "series of"), ("returns", "return of")):
                parent = r.get(key)
                if parent in pack and all(float(r.get(k) or 0) == float(rails[parent].get(k) or 0)
                                          for k in ("amps_typ", "amps_peak")):
                    pack[net] = "%s %s" % (word, parent); moved = True
                    break
    return pack


def _row(net, volts, v_work, typ, peak, returns, pack_why, cu_out, cu_in):
    is_pack = pack_why is not None
    gov_a = PACK_SERVICE_A if is_pack else typ
    basis = "typical (PI-001)"
    if is_pack: basis = "PWR-F12 18 A / 60 s" + ((", " + pack_why) if pack_why else "")
    return {"net": net, "volts": volts, "v_work": v_work, "typ": typ, "peak": peak, "returns": returns,
            "pack": is_pack, "gov_a": gov_a, "gov_basis": basis,
            "w_out": w(gov_a, cu_out, False), "w_in": w(gov_a, cu_in, True) if cu_in else None,
            "w_out_split2": w(gov_a / 2.0, cu_out, False), "barrels": barrels(max(peak, gov_a))}


def _chain_stage(path, stage):
    try:
        import yaml
    except ImportError:
        raise SystemExit("rail_widths: a board with no intent file takes its currents from %s, and reading it needs "
                         "PyYAML on this host" % os.path.basename(path))
    d = yaml.safe_load(open(path, encoding="utf-8")) or {}
    for s in d.get("stages") or []:
        if isinstance(s, dict) and s.get("id") == stage: return s
    raise SystemExit("rail_widths: %s declares no stage %s" % (path, stage))


def rows(letter, root=None):
    """One board's table as data: its inputs by path and sha256/16, the model, the stack and a row per declared rail.
    `root` is the repository the FILES are read from (default: the one this script sits in)."""
    root = os.path.abspath(root or ROOT)
    if letter in NO_INTENT:
        b = NO_INTENT[letter]
        st = _chain_stage(os.path.join(root, b["chain"]), b["stage"])
        typ, peak = float(st.get("continuous_a") or 0), float(st.get("peak_a") or 0)
        out = [_row(net, None, None, typ, peak, ret, "chain stage %s" % b["stage"], b["cu_out"], b["cu_in"])
               for net, ret in b["rails"]]
        return {"letter": letter, "kind": "declared",
                "inputs": [("board_file", b["board_file"], sha16(os.path.join(root, b["board_file"]))),
                           ("chain", b["chain"], sha16(os.path.join(root, b["chain"])))],
                "written": None, "stage": b["stage"], "stack": b["stack"], "cu_out": b["cu_out"], "cu_in": b["cu_in"],
                "stack_why": b["why"], "pack_roots": [n for n, _r in b["rails"]], "rows": out, "sized": []}
    ipath, stack, cu_out, cu_in, why, roots = BOARDS[letter]
    full = os.path.join(root, ipath)
    it = json.load(open(full, encoding="utf-8"))
    rails = it.get("rails") or {}
    pack = pack_path(rails, roots)
    out = []
    for net, r in rails.items():
        typ, peak = float(r.get("amps_typ") or 0), float(r.get("amps_peak") or 0)
        if typ <= 0 and peak <= 0:
            continue
        out.append(_row(net, r.get("volts"), r.get("v_work"), typ, peak, r.get("returns"), pack.get(net), cu_out, cu_in))
    sized = []
    for net, amps, src in SIZED_TO.get(letter, ()):
        r = rails.get(net) or {}
        typ, peak = float(r.get("amps_typ") or 0), float(r.get("amps_peak") or 0)
        sized.append({"net": net, "declared": net in rails, "typ": typ, "peak": peak, "amps": float(amps), "source": src,
                      "w_out": w(amps, cu_out, False), "w_in": w(amps, cu_in, True) if cu_in else None,
                      "w_out_split2": w(amps / 2.0, cu_out, False), "barrels": barrels(max(peak, amps))})
    npath = ipath.replace("-intent.json", ".net")
    nfull = os.path.join(root, npath)
    return {"letter": letter, "kind": "intent",
            "inputs": [("netlist", npath, sha16(nfull) if os.path.exists(nfull) else None),
                       ("intent", ipath, sha16(full))],
            "written": it.get("written"), "stack": stack, "cu_out": cu_out, "cu_in": cu_in, "stack_why": why,
            "pack_roots": list(roots), "rows": out, "sized": sized}


def bound_lines(t):
    """The fixed-form lines that name a table's inputs, model and stack: the body of its `bound` block, and the lines a
    sheet's own block repeats (v2/docs/layout-constraints/README.md, "The bound block")."""
    L = ["board      %s" % t["letter"]]
    for role, path, sha in t["inputs"]:
        L.append("%-10s %s sha256/16 %s" % (role, path, sha or "absent"))
    L.append("model      %s decision %d rise %g K plating %g um"
             % (MODEL["function"], MODEL["decision"], MODEL["rise_k"], MODEL["plating_um"]))
    L.append("stack      %s outer %.4f mm inner %s" % (t["stack"], t["cu_out"],
                                                       ("%.4f mm" % t["cu_in"]) if t["cu_in"] else "none"))
    return L


def _mm(v):
    return "%.2f" % v


def cells(r):
    """One rail's row as the eight cells of HEAD, as text."""
    if r.get("volts") is None: vw = NO_VOLTS
    elif r.get("v_work"): vw = "%.1f (%.1f)" % (r["volts"], r["v_work"])
    else: vw = "%.2f" % r["volts"]
    if r["w_in"] is None: inner = NO_INNER
    else: inner = _mm(r["w_in"]) + (" (over 40 mm)" if r["w_in"] > 40 else "")
    return [r["net"] + (" (return of %s)" % r["returns"] if r.get("returns") else ""), vw,
            "%.2f / %.2f" % (r["typ"], r["peak"]), "%.2f, %s" % (r["gov_a"], r["gov_basis"]),
            _mm(r["w_out"]), _mm(r["w_out_split2"]), inner, " / ".join(str(r["barrels"][d]) for d in DRILLS)]


def cells_sized(r):
    """One sized-to row as the eight cells of HEAD_SIZED, as text."""
    if r["w_in"] is None: inner = NO_INNER
    else: inner = _mm(r["w_in"]) + (" (over 40 mm)" if r["w_in"] > 40 else "")
    return [r["net"], ("%.2f / %.2f" % (r["typ"], r["peak"])) if r["declared"] else "not declared",
            "%.3f" % r["amps"], _mm(r["w_out"]), _mm(r["w_out_split2"]), inner,
            " / ".join(str(r["barrels"][d]) for d in DRILLS), r["source"]]


def _line(cs):
    return "| " + " | ".join(str(c).replace("|", "\\|") for c in cs) + " |"


def table(head, body):
    return [_line(head), "|" + "|".join(ALIGN.get(h, "---") for h in head) + "|"] + [_line(c) for c in body]


def markdown(t):
    L = ["```bound"] + bound_lines(t) + ["```", ""]
    says = []
    if t.get("written"): says.append("Intent written %s." % t["written"])
    if t.get("stage"): says.append("Currents: the chain's stage %s." % t["stage"])
    says.append("Stack: %s." % t["stack_why"])
    pk = [r["net"] for r in t["rows"] if r["pack"]]
    if pk: says.append("Pack path, judged at %g A (PWR-F12): %s." % (PACK_SERVICE_A, ", ".join(pk)))
    L.append(" ".join(says))
    L.append("")
    L += table(HEAD, [cells(r) for r in t["rows"]])
    if t["sized"]:
        L.append("")
        L.append("Sized at a maker's figure above the declaration (SIZED_TO; POWER-THERMAL.md section 10):")
        L.append("")
        L += table(HEAD_SIZED, [cells_sized(r) for r in t["sized"]])
    return "\n".join(L)


def render(letters=None, root=None):
    """The whole output as text, exactly what `--markdown` prints (calc/rail_widths.out is this, for every board)."""
    out = []
    for letter in ORDER:
        if letters and letter not in letters: continue
        out.append("### Board %s\n\n%s\n\n" % (letter.upper(), markdown(rows(letter, root))))
    return "".join(out)


def main(a):
    only = a[a.index("--board") + 1].lower() if "--board" in a and a.index("--board") + 1 < len(a) else None
    if "--board" in a and only not in ORDER:
        print("rail_widths: no board %r; the boards are %s" % (only, ", ".join(ORDER))); return 2
    if "--markdown" in a:
        sys.stdout.write(render([only] if only else None))
        return 0
    for letter in ORDER:
        if only and letter != only: continue
        print(json.dumps(rows(letter), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
