#!/usr/bin/env python3
"""A04 (MESHSAT-1357): read-only part-for-part comparison of board A's COMMITTED netlist and COMMITTED board
for every part on a conductor that boards/a.json declares external.

SCH-002 (netlist_board.py) compares references, pad nets and net names. It never compares a VALUE or a
FOOTPRINT, so a clamp whose rating changed between the netlist and the board passes it. This script asks the
three questions per part (value, footprint, every pad's net), plus land geometry against the library footprint
the netlist names, and TVS polarity from the footprint's own silk mark.

Reads only. Inputs are taken with `git show <commit>:<path>` so the working tree cannot stand in for them.
Usage: a04_compare.py <repo clone> <commit> <out dir>
Writes: <out>/inputs/* (the git-show copies), <out>/a04_compare.json, <out>/a04_compare.txt,
        <out>/pcb-a-power.board-values.net (the committed netlist with each value replaced by the board's).
"""
import sys, os, re, json, hashlib, subprocess, math

REPO, COMMIT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
P_NET = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
P_INT = "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json"
P_PCB = "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb"
P_BJ = "v2/ecad/tools/boards/a.json"
P_PRETTY = "v2/ecad/meshsat.pretty"
KICAD_FP = "/usr/share/kicad/footprints"
os.makedirs(os.path.join(OUT, "inputs"), exist_ok=True)


def git_show(path):
    data = subprocess.check_output(["git", "-C", REPO, "show", "%s:%s" % (COMMIT, path)])
    dst = os.path.join(OUT, "inputs", os.path.basename(path))
    open(dst, "wb").write(data)
    wt = os.path.join(REPO, path)
    wt_sha = hashlib.sha256(open(wt, "rb").read()).hexdigest() if os.path.exists(wt) else None
    last = subprocess.check_output(["git", "-C", REPO, "log", "-1", "--format=%h %cI", COMMIT, "--", path]).decode().strip()
    return dst, {"path": path, "sha256": hashlib.sha256(data).hexdigest(), "worktree_sha256": wt_sha,
                 "last_commit": last}


net_f, net_id = git_show(P_NET)
int_f, int_id = git_show(P_INT)
pcb_f, pcb_id = git_show(P_PCB)
bj_f, bj_id = git_show(P_BJ)
IDS = {"netlist": net_id, "intent": int_id, "board": pcb_id, "board_table": bj_id,
       "commit": subprocess.check_output(["git", "-C", REPO, "rev-parse", COMMIT]).decode().strip()}


# ---------- netlist, parsed as an s-expression (not by regex) ----------
TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')


def sexp(txt):
    st = [[]]
    for m in TOK.finditer(txt):
        t = m.group(0)
        if t == "(": st.append([])
        elif t == ")":
            x = st.pop(); st[-1].append(x)
        elif t[0] == '"': st[-1].append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\"))
        else: st[-1].append(t)
    return st[0][0]


def kids(node, key):
    return [x for x in node[1:] if isinstance(x, list) and x and x[0] == key]


def one(node, key, default=None):
    k = kids(node, key)
    return k[0][1] if k and len(k[0]) > 1 else default


root = sexp(open(net_f, encoding="utf-8").read())
NL = {}
for comp in kids(kids(root, "components")[0], "comp"):
    ref = one(comp, "ref")
    props = {one(p, "name"): one(p, "value") for p in kids(comp, "property")}
    ls = kids(comp, "libsource")
    NL[ref] = {"value": one(comp, "value", ""), "footprint": one(comp, "footprint", ""),
               "lcsc": props.get("LCSC"), "libsource": ("%s:%s" % (one(ls[0], "lib"), one(ls[0], "part"))) if ls else None,
               "pins": {}}
NL_NETS = {}
for net in kids(kids(root, "nets")[0], "net"):
    name = one(net, "name", "").lstrip("/")
    for node in kids(net, "node"):
        r, p = one(node, "ref"), one(node, "pin")
        NL_NETS.setdefault(name, set()).add((r, p))
        if r in NL: NL[r]["pins"][p] = name

# ---------- board, through pcbnew ----------
import pcbnew
BRD = pcbnew.LoadBoard(pcb_f)


def pad_geom(p):
    try: sz = p.GetSize(pcbnew.F_Cu)
    except TypeError: sz = p.GetSize()
    try: shp = p.GetShape(pcbnew.F_Cu)
    except TypeError: shp = p.GetShape()
    d = p.GetDrillSize()
    return {"size": (round(sz.x / 1e6, 4), round(sz.y / 1e6, 4)), "shape": int(shp),
            "drill": (round(d.x / 1e6, 4), round(d.y / 1e6, 4)), "attr": int(p.GetAttribute())}


BD = {}
for fp in BRD.GetFootprints():
    ref = fp.GetReference()
    fields = {}
    for f in fp.GetFields():
        fields[f.GetName()] = f.GetText()
    pads = {}
    for p in fp.Pads():
        n = p.GetNetname().lstrip("/")
        pads.setdefault(p.GetNumber(), []).append({"net": n, "pos": (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6),
                                                   **pad_geom(p)})
    BD[ref] = {"value": fp.GetValue(), "fpid": fp.GetFPIDAsString(), "fpname": fp.GetFPIDAsString().partition(":")[2] or fp.GetFPIDAsString(),
               "layer": fp.GetLayerName(), "pos": (round(fp.GetPosition().x / 1e6, 3), round(fp.GetPosition().y / 1e6, 3)),
               "rot": fp.GetOrientationDegrees(), "fields": fields, "pads": pads, "fp": fp}
BD_NETS = {}
for ref, b in BD.items():
    for num, lst in b["pads"].items():
        for q in lst:
            if q["net"]: BD_NETS.setdefault(q["net"], set()).add((ref, num))

# board-level texts naming a phase
phase_texts = []
for d in BRD.GetDrawings():
    if isinstance(d, pcbnew.PCB_TEXT):
        t = d.GetText()
        if re.search(r"\bA\d{2}[A-Z]?\b", t): phase_texts.append({"text": t[:160], "layer": d.GetLayerName()})
for fp in BRD.GetFootprints():
    for it in fp.GraphicalItems():
        if isinstance(it, pcbnew.PCB_TEXT) and re.search(r"\bA\d{2}[A-Z]?\b", it.GetText()):
            phase_texts.append({"text": it.GetText()[:160], "layer": it.GetLayerName(), "in": fp.GetReference()})

# ---------- external conductors from boards/a.json ----------
BJ = json.load(open(bj_f))
GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)
PROTECT = re.compile(r"(TVS|ESD|SMBJ|SMCJ|SMAJ|USBLC|PESD|SP\d{4}|GDT|arrest|polyfuse|PTC|common.?mode|"
                     r"choke|magnetic|transformer|isolat|opto|clamp|varistor|\bMOV\b|limiter|D_TVS)", re.I)
ext_nets, conductors, in_part = {}, [], {}
for e in BJ["external_ports"]:
    ref = e["ref"]
    wanted = [str(x) for x in e.get("pins") or []]
    ip = e.get("protected_in_part") or {}
    for pin, net in sorted(NL[ref]["pins"].items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 999):
        if GROUND.match(net) or net.startswith("unconnected-") or not net: continue
        # a declared pin list narrows the conductors; a pin of the same connector on the SAME net is the same
        # conductor, so it is kept and flagged rather than dropped
        declared = (not wanted) or (pin in wanted)
        same_net = any(NL[ref]["pins"].get(w) == net for w in wanted)
        if not declared and not same_net: continue
        conductors.append({"port": ref, "pin": pin, "net": net, "declared_pin": declared})
        ext_nets.setdefault(net, []).append("%s.%s" % (ref, pin))
        if pin in [str(x) for x in ip.get("pins") or []]: in_part[net] = ip.get("part")

# ---------- part-for-part rows ----------
def role(ref, val):
    if any(ref == e["ref"] for e in BJ["external_ports"]): return "port connector"
    if ref in in_part.values(): return "protection inside part (decision 31 declaration)"
    if PROTECT.search(val or "") or PROTECT.search(ref): return "PROTECTION"
    return "on the conductor"


def lib_land(fpstr):
    nick, _, name = fpstr.partition(":")
    lib = os.path.join(REPO, P_PRETTY) if nick == "meshsat" else os.path.join(KICAD_FP, nick + ".pretty")
    if not os.path.isdir(lib): return None, "library %s not found at %s" % (nick, lib)
    try: f = pcbnew.FootprintLoad(lib, name)
    except Exception as ex: return None, "FootprintLoad raised %s" % ex
    if f is None: return None, "footprint %s not in %s" % (name, lib)
    return f, lib


def land_sig(fp):
    """Rotation-, translation- and mirror-invariant land signature: per pad number its size, shape, drill and
    attribute, and the sorted distances between every pair of pad centres."""
    pads = []
    for p in fp.Pads():
        g = pad_geom(p)
        pads.append((p.GetNumber(), g["size"], g["shape"], g["drill"], g["attr"], (p.GetPosition().x / 1e6, p.GetPosition().y / 1e6)))
    pads.sort(key=lambda x: (x[0], x[5]))
    per = [(a, b, c, d, e) for a, b, c, d, e, _ in pads]
    dist = []
    for i in range(len(pads)):
        for j in range(i + 1, len(pads)):
            (x1, y1), (x2, y2) = pads[i][5], pads[j][5]
            dist.append((pads[i][0], pads[j][0], round(math.hypot(x2 - x1, y2 - y1), 3)))
    dist.sort()
    return per, dist


def polarity(ref):
    """Which pad the footprint's cathode mark sits beside, read from the footprint's own silk: the silk segment
    that crosses the pad axis (perpendicular to the line pad 2 -> pad 1), and which side of centre it lies."""
    fp = BD[ref]["fp"]
    p1 = [p for p in fp.Pads() if p.GetNumber() == "1"]
    p2 = [p for p in fp.Pads() if p.GetNumber() == "2"]
    if not p1 or not p2: return {"error": "no pads 1 and 2"}
    a = p1[0].GetPosition(); b = p2[0].GetPosition()
    ux, uy = (a.x - b.x), (a.y - b.y); L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
    cx, cy = (a.x + b.x) / 2, (a.y + b.y) / 2
    marks = []
    for it in fp.GraphicalItems():
        if not isinstance(it, pcbnew.PCB_SHAPE): continue
        if it.GetLayerName() not in ("F.SilkS", "B.SilkS", "F.Silkscreen", "B.Silkscreen"): continue
        if it.GetShape() != pcbnew.SHAPE_T_SEGMENT: continue
        s, e = it.GetStart(), it.GetEnd()
        dx, dy = e.x - s.x, e.y - s.y; l = math.hypot(dx, dy)
        if l == 0: continue
        if abs((dx * ux + dy * uy) / l) < 0.1:          # perpendicular to the pad axis
            mx, my = (s.x + e.x) / 2, (s.y + e.y) / 2
            t = ((mx - cx) * ux + (my - cy) * uy) / 1e6
            marks.append(round(t, 3))
    side = ("pad 1" if marks and all(t > 0 for t in marks) else
            "pad 2" if marks and all(t < 0 for t in marks) else "ambiguous")
    return {"perpendicular_silk_offsets_toward_pad1_mm": marks, "cathode_mark_beside": side}


rows = []
refs = sorted({r for n in ext_nets for r, _ in NL_NETS.get(n, set())} | {r for n in ext_nets for r, _ in BD_NETS.get(n, set())})
for ref in refs:
    n, b = NL.get(ref), BD.get(ref)
    row = {"ref": ref, "role": role(ref, (n or {}).get("value", "") or (b or {}).get("value", "")),
           "on_nets": sorted({x for x in ext_nets if any(r == ref for r, _ in NL_NETS.get(x, set()) | BD_NETS.get(x, set()))})}
    if not n or not b:
        row.update({"in_netlist": bool(n), "on_board": bool(b), "verdict": "DIFFERENT (missing on one side)"}); rows.append(row); continue
    nl_fpname = n["footprint"].partition(":")[2] or n["footprint"]
    bpads = {k: sorted({q["net"] for q in v}) for k, v in b["pads"].items()}
    pad_diffs = []
    for pin, net in sorted(n["pins"].items()):
        bn = bpads.get(pin)
        want = "" if net.startswith("unconnected-") else net
        got = [x for x in (bn or []) if x]
        if (want and got != [want]) or (not want and got):
            pad_diffs.append("pin %s: netlist %s, board %s" % (pin, net, got or "no net"))
    for pad, nets in sorted(bpads.items()):
        if pad not in n["pins"] and pad != "" and any(nets):
            pad_diffs.append("pad %s on board carries %s, no such pin in netlist" % (pad, nets))
    lib, where = lib_land(n["footprint"])
    if lib is not None:
        s_lib, s_brd = land_sig(lib), land_sig(b["fp"])
        land = "IDENTICAL to %s" % n["footprint"] if s_lib == s_brd else "DIFFERS from %s" % n["footprint"]
        land_detail = None if s_lib == s_brd else {"lib_pads": s_lib[0][:8], "board_pads": s_brd[0][:8]}
    else:
        land, land_detail = "NOT CHECKED (%s)" % where, None
    row.update({
        "netlist_value": n["value"], "board_value": b["value"], "value_equal": n["value"] == b["value"],
        "netlist_footprint": n["footprint"], "board_fpid": b["fpid"], "footprint_name_equal": nl_fpname == b["fpname"],
        "land_vs_library": land, "land_detail": land_detail,
        "netlist_lcsc": n["lcsc"], "board_lcsc": b["fields"].get("LCSC"),
        "pad_net_diffs": pad_diffs, "pins_compared": len(n["pins"]),
        "board_layer": b["layer"], "board_pos_mm": b["pos"], "board_rot": b["rot"],
    })
    if re.match(r"^D\d", ref) and re.search(r"SM[ABC]J\d", n["value"] + " " + b["value"]):
        pol = polarity(ref)
        pol["netlist_pad1"] = n["pins"].get("1"); pol["netlist_pad2"] = n["pins"].get("2")
        pol["board_pad1"] = bpads.get("1"); pol["board_pad2"] = bpads.get("2")
        lib_pol = None
        if lib is not None:
            # the same silk question asked of the library footprint as loaded (orientation 0)
            BD["__lib__"] = {"fp": lib}
            lib_pol = polarity("__lib__")["cathode_mark_beside"]
            del BD["__lib__"]
        pol["library_cathode_mark_beside"] = lib_pol
        row["polarity"] = pol
    ok = row["value_equal"] and row["footprint_name_equal"] and not pad_diffs and land.startswith("IDENTICAL")
    row["verdict"] = "SAME" if ok else "DIFFERENT"
    rows.append(row)

# nodes on each external conductor, netlist against board
node_sets = {}
for net in sorted(ext_nets):
    a_ = sorted("%s.%s" % x for x in NL_NETS.get(net, set()))
    b_ = sorted("%s.%s" % x for x in BD_NETS.get(net, set()))
    node_sets[net] = {"conductor_pins": ext_nets[net], "netlist_nodes": a_, "board_nodes": b_,
                      "equal": a_ == b_, "netlist_only": sorted(set(a_) - set(b_)), "board_only": sorted(set(b_) - set(a_))}

# ---------- TRN-001's own walk on the BOARD's connectivity and values ----------
sys.path.insert(0, os.path.join(REPO, "v2/ecad/tools"))
import port_protect as pp
b_by_net, b_by_ref, b_vals = {}, {}, {}
for ref, b in BD.items():
    if ref.startswith("__"): continue
    b_vals[ref] = b["value"]
    for num, lst in b["pads"].items():
        for q in lst:
            if not q["net"] or q["net"].startswith("unconnected-"): continue
            b_by_net.setdefault(q["net"], set()).add((ref, num)); b_by_ref.setdefault(ref, set()).add((num, q["net"]))
_orig = pp.netlist
pp.netlist = lambda path: (b_by_net, b_by_ref, b_vals)
b_rows, b_bad, b_missing, b_nd = pp.judge(net_f.replace("pcb-a-power.net", "pcb-a-power.net"), "a")
pp.netlist = _orig
n_rows, n_bad, n_missing, n_nd = pp.judge(net_f, "a")
trn = {"on_committed_netlist": {"fail_lines": n_bad, "missing": n_missing, "declared": n_nd,
                                "in_part": [x for r in n_rows for x in r.get("in_part") or []]},
       "on_board_connectivity_and_values": {"fail_lines": b_bad, "missing": b_missing, "declared": b_nd,
                                            "in_part": [x for r in b_rows for x in r.get("in_part") or []]}}

# ---------- the netlist rewritten with the BOARD's values (for CMP-001 on the part as built) ----------
txt = open(net_f, encoding="utf-8").read()
swapped = []


def _sub(m):
    ref = m.group(1)
    b = BD.get(ref)
    if b and NL.get(ref) and b["value"] != NL[ref]["value"]:
        swapped.append({"ref": ref, "netlist": NL[ref]["value"], "board": b["value"]})
        v = b["value"].replace("\\", "\\\\").replace('"', '\\"')
        return '(comp (ref "%s")\n      (value "%s")' % (ref, v)
    return m.group(0)


txt2 = re.sub(r'\(comp \(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)', _sub, txt)
bvn = os.path.join(OUT, "pcb-a-power.board-values.net")
open(bvn, "w", encoding="utf-8").write(txt2)
import shutil
shutil.copy(int_f, os.path.join(OUT, "pcb-a-power.board-values-intent.json"))

res = {"ids": IDS, "phase_texts": phase_texts, "board_table_phase": BJ.get("phase"),
       "external_ports": BJ["external_ports"], "conductors": conductors, "node_sets": node_sets, "rows": rows,
       "trn001": trn, "values_swapped_into_board_values_net": swapped,
       "counts": {"netlist_refs": len(NL), "board_footprints": len([r for r in BD if not r.startswith("__")]),
                  "rows": len(rows), "rows_different": sum(1 for r in rows if r["verdict"] != "SAME")},
       "pcbnew_version": pcbnew.Version()}
json.dump(res, open(os.path.join(OUT, "a04_compare.json"), "w"), indent=1, default=str)

L = []
L.append("A04 part-for-part comparison, board A, commit %s, pcbnew %s" % (IDS["commit"], pcbnew.Version()))
for k in ("netlist", "board", "intent", "board_table"):
    L.append("  %-11s %s sha256 %s (worktree %s) last %s" % (k, IDS[k]["path"], IDS[k]["sha256"][:16],
                                                          (IDS[k]["worktree_sha256"] or "none")[:16], IDS[k]["last_commit"]))
L.append("  board phase texts: %s ; boards/a.json phase %s" % ([p["text"][:60] for p in phase_texts][:6], BJ.get("phase")))
L.append("conductors: " + ", ".join("%s.%s=%s%s" % (c["port"], c["pin"], c["net"], "" if c["declared_pin"] else "(same net, undeclared pin)") for c in conductors))
L.append("")
L.append("%-11s %-10s %-9s | netlist value || board value | footprint nl / board | land | pad nets" % ("ref", "verdict", "role"))
for r in rows:
    if "netlist_value" not in r:
        L.append("%-11s %-10s %s in_netlist=%s on_board=%s" % (r["ref"], r["verdict"], r["role"], r["in_netlist"], r["on_board"])); continue
    L.append("%-11s %-10s %-26s | %s || %s | %s / %s | %s | %s" % (
        r["ref"], r["verdict"], r["role"], r["netlist_value"][:70], r["board_value"][:70], r["netlist_footprint"],
        r["board_fpid"], r["land_vs_library"][:40], ("; ".join(r["pad_net_diffs"]) or "all %d equal" % r["pins_compared"])))
    if r.get("polarity"): L.append("            polarity: %s" % json.dumps(r["polarity"]))
    L.append("            lcsc netlist %s board %s; board %s at %s rot %s" % (r["netlist_lcsc"], r["board_lcsc"], r["board_layer"], r["board_pos_mm"], r["board_rot"]))
L.append("")
for net, s in node_sets.items():
    L.append("net %-11s equal=%s netlist_only=%s board_only=%s nodes=%s" % (net, s["equal"], s["netlist_only"], s["board_only"], s["netlist_nodes"]))
L.append("")
L.append("TRN-001 walk on committed netlist: fail=%s in_part=%d" % (n_bad, len(trn["on_committed_netlist"]["in_part"])))
L.append("TRN-001 walk on the BOARD's own connectivity and values: fail=%s in_part=%d" % (b_bad, len(trn["on_board_connectivity_and_values"]["in_part"])))
L.append("values swapped into board-values netlist: %d, e.g. %s" % (len(swapped), [s["ref"] for s in swapped][:60]))
open(os.path.join(OUT, "a04_compare.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
