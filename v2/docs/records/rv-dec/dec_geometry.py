#!/usr/bin/env python3
"""Decision 42 geometry, read from committed board TEXT with no pcbnew (MESHSAT-1357, 26 September 2026).

For every declared decoupling entry (cap, part, pin) of a board's intent file, this reads the part's footprint and the
capacitor's footprint from the .kicad_pcb s-expression and answers four questions the placement tools never printed:

  1. fan_now   : does bypass_slots._needs_fan give the part a fan (>= 8 SMD pads, closest two <= 1.0 mm), counting
                 EVERY smd pad as the tool does (paste-only apertures included)?
  2. fan_cu    : the same test counting only NUMBERED pads that carry copper (F-DC-02's proposed fix).
  3. dmin_fan  : the smallest pin-to-capacitor-CENTRE distance at which the capacitor's courtyard box (board frame,
                 rotation 0 as bypass_slots places it) clears the part's fan box (courtyard bbox grown by 2.2 mm).
                 This is a lower bound set by geometry alone: if it exceeds 3.0 mm, no floor plan can seat the
                 capacitor within the placers' 3.0 mm, which is decision 42's conflict.
  4. gate_lim  : the limit intent_checks.py applies to that capacitor's value (3.0 mm, or 6.0 mm for microfarad
                 values), which the placers (LIMIT = 3.0 for every value) do not share.

It mirrors bypass_slots._courtyard (courtyard bbox, falling back to the footprint's pads when a footprint has no
courtyard), _fan_box and _needs_fan; it is a REPORT for the decision record and decides nothing.
Usage: dec_geometry.py <board.kicad_pcb> <intent.json> [--json out.json]"""
import sys, json, math, re

def tokens(s):
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in " \t\r\n": i += 1; continue
        if c == "(" or c == ")": yield c; i += 1; continue
        if c == '"':
            j = i + 1; buf = []
            while j < n and s[j] != '"':
                if s[j] == "\\" and j + 1 < n: buf.append(s[j + 1]); j += 2; continue
                buf.append(s[j]); j += 1
            yield ("S", "".join(buf)); i = j + 1; continue
        j = i
        while j < n and s[j] not in " \t\r\n()": j += 1
        yield ("A", s[i:j]); i = j

def parse(s):
    st = [[]]
    for t in tokens(s):
        if t == "(": st.append([])
        elif t == ")": x = st.pop(); st[-1].append(x)
        else: st[-1].append(t[1])
    return st[0][0]

def kids(node, name): return [k for k in node if isinstance(k, list) and k and k[0] == name]
def kid(node, name):
    k = kids(node, name); return k[0] if k else None

def rot(x, y, deg):   # KiCad: positive angle turns counter-clockwise on screen, y axis down
    a = math.radians(deg); return (x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a))

def footprints(board):
    out = {}
    for fp in kids(board, "footprint"):
        ref = None; value = ""
        for p in kids(fp, "property"):
            if len(p) > 2 and p[1] == "Reference": ref = p[2]
            if len(p) > 2 and p[1] == "Value": value = p[2]
        for t in kids(fp, "fp_text"):
            if len(t) > 2 and t[1] == "reference": ref = t[2]
        if not ref: continue
        at = kid(fp, "at"); X, Y = float(at[1]), float(at[2]); R = float(at[3]) if len(at) > 3 else 0.0
        layer = kid(fp, "layer")[1]
        pads = []
        for p in kids(fp, "pad"):
            num, typ = p[1], p[2]
            pa = kid(p, "at"); px, py = float(pa[1]), float(pa[2])
            sz = kid(p, "size"); w, h = float(sz[1]), float(sz[2])
            lays = kid(p, "layers")[1:] if kid(p, "layers") else []
            cu = any(l.endswith(".Cu") or l == "*.Cu" for l in lays)
            nn = kid(p, "net"); net = nn[2] if nn and len(nn) > 2 else (nn[1] if nn and len(nn) > 1 else "")
            ax, ay = rot(px, py, R); pads.append({"net": net, "num": num, "type": typ, "x": X + ax, "y": Y + ay, "w": w, "h": h, "cu": cu})
        cys = []
        cyl = "F.CrtYd" if layer == "F.Cu" else "B.CrtYd"
        for g in [k for k in fp if isinstance(k, list) and k and k[0] in ("fp_line", "fp_rect", "fp_poly", "fp_circle", "fp_arc")]:
            gl = kid(g, "layer")
            if not gl or gl[1] != cyl: continue
            pts = []
            for key in ("start", "end", "mid", "center"):
                e = kid(g, key)
                if e: pts.append((float(e[1]), float(e[2])))
            pl = kid(g, "pts")
            if pl:
                for xy in kids(pl, "xy"): pts.append((float(xy[1]), float(xy[2])))
            for (x, y) in pts:
                ax, ay = rot(x, y, R); cys.append((X + ax, Y + ay))
        if cys:
            bb = (min(p[0] for p in cys), min(p[1] for p in cys), max(p[0] for p in cys), max(p[1] for p in cys))
        else:
            bb = (min(p["x"] - p["w"] / 2 for p in pads), min(p["y"] - p["h"] / 2 for p in pads),
                  max(p["x"] + p["w"] / 2 for p in pads), max(p["y"] + p["h"] / 2 for p in pads)) if pads else (X, Y, X, Y)
        out[ref] = {"value": value, "lib": fp[1], "x": X, "y": Y, "rot": R, "layer": layer, "pads": pads, "cy": bb, "has_cy": bool(cys)}
    return out

def needs_fan(pads, numbered_cu_only):
    ps = [(p["x"], p["y"]) for p in pads if p["type"] == "smd" and (not numbered_cu_only or (p["num"] not in ("", '""') and p["cu"]))]
    if len(ps) < 8: return False, None
    best = min(math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(ps) for b in ps[i + 1:] if (a != b))
    return best <= 1.0 + 1e-9, round(best, 3)

# THE FAN AS RULED (decision 42, T1 as corrected in the check of the 16:42 version (26 September 2026)). The fan protects the room an
# ESCAPED part's vias need, so the set that gets one must contain every part escape.py escapes, and it must keep every
# part today's _needs_fan fans for a reason other than a paste aperture. escape.py (v2/ecad/tools/escape.py:34-42, :176-177)
# escapes a part when its FPID names SOT-23-6/8 or its closest two SMD pads (every SMD pad, paste apertures included, as
# pcbnew's PAD_ATTRIB_SMD counts them) are 0.7 mm apart or less, with NO pad-count floor; it skips a J part whose pitch is
# over 0.6 mm and the references in the board's ESCAPE_SKIP (tools/boards/<x>.json, escape_env). So the ruled set is
#   fan_as_ruled = needs_fan(numbered copper pads, >= 8, <= 1.0 mm)  OR  escaped(part)
# The first term keeps the 0.8 mm TQFP/LQFP fans the 9 September D10 lesson added (escape.py does not escape them); the
# second restores what T1 alone would have cut (the WSON-6-1EP lands, whose ninth and eighth SMD pads are paste
# apertures) and adds the six-pad parts escape.py escapes that no placer protects today (SOT-23-6, TSOT-23-6, MLPD-6).

def smd_min_pitch(pads):
    ps = [(p["x"], p["y"]) for p in pads if p["type"] == "smd"]
    ds = [math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(ps) for b in ps[i + 1:]]
    ds = [d for d in ds if d > 1e-9]
    return min(ds) if ds else 1e9

def escaped(ref, f, skip=()):
    """Mirror of escape.py's selection (is_fine at :34-42, the J and ESCAPE_SKIP exemptions at :176-177)."""
    fine = bool(re.search(r"SOT-23-[68]", f["lib"])) or smd_min_pitch(f["pads"]) <= 0.7 + 1e-6
    if not fine: return False
    if ref.startswith("J") and smd_min_pitch(f["pads"]) > 0.6 + 1e-6: return False
    return ref not in set(skip)

def fan_as_ruled(ref, f, skip=()):
    return needs_fan(f["pads"], True)[0] or escaped(ref, f, skip)

def escape_skip(board_path):
    """ESCAPE_SKIP of the board a project directory belongs to, read from tools/boards/<letter>.json (escape_env)."""
    import os
    d = os.path.basename(os.path.dirname(os.path.abspath(board_path)))       # pcb-b-compute-b19
    letter = d.split("-")[1][0] if d.startswith("pcb-") else ""
    tools = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(board_path))), "tools", "boards", letter + ".json")
    try:
        env = json.load(open(tools)).get("escape_env", {}) or {}
    except Exception:
        return set()
    return set(filter(None, str(env.get("ESCAPE_SKIP", "")).split(",")))

SKIP = set()

def main(a):
    bp, ip = a[0], a[1]
    b = parse(open(bp, encoding="utf-8").read()); fps = footprints(b)
    global SKIP; SKIP = escape_skip(bp)
    it = json.load(open(ip)); rows = []
    for e in it.get("bypass", []):
        cap, part, pin = e["cap"], e["part"], str(e["pin"])
        P = fps.get(part); C = fps.get(cap)
        if not P or not C: rows.append({"cap": cap, "part": part, "pin": pin, "note": "not on this board"}); continue
        pad = next((q for q in P["pads"] if q["num"] == pin), None)
        if not pad: rows.append({"cap": cap, "part": part, "pin": pin, "note": "no such pin"}); continue
        fan_now, pitch_now = needs_fan(P["pads"], False); fan_cu, pitch_cu = needs_fan(P["pads"], True)
        fan_ruled = fan_as_ruled(part, P, SKIP); esc = escaped(part, P, SKIP)
        # the capacitor as bypass_slots places it: rotation 0 in the board frame; its courtyard size from its own frame
        cw = C["cy"][2] - C["cy"][0]; ch = C["cy"][3] - C["cy"][1]
        if abs((C["rot"] % 180) - 90) < 1: cw, ch = ch, cw     # back to its own frame
        l, t, r, bt = P["cy"]; f = 2.2
        box = (l - f - cw / 2, t - f - ch / 2, r + f + cw / 2, bt + f + ch / 2)
        cby = (l - cw / 2, t - ch / 2, r + cw / 2, bt + ch / 2)
        px, py = pad["x"], pad["y"]
        dmin_fan = min(px - box[0], box[2] - px, py - box[1], box[3] - py)
        dmin_cy = min(px - cby[0], cby[2] - px, py - cby[1], cby[3] - py)
        dnow = math.hypot(C["x"] - px, C["y"] - py)
        # the GATE's own measure (intent_checks.py:252-253): the capacitor pad on the pin's net, to the pin
        rail = [q for q in C["pads"] if q["net"] == pad["net"]]
        d_gate = round(math.hypot(rail[0]["x"] - px, rail[0]["y"] - py), 2) if rail else None
        val = C["value"]
        # intent_checks.py's own value rule (the gate): 6.0 mm for a microfarad value, 3.0 mm otherwise
        gate_lim = 6.0 if any(u in val.lower() for u in ("u ", "uf", "u,", "\u00b5")) and not val.lower().startswith(("0.1u", "0.01u")) else 3.0
        gate_fail_without_allow = (d_gate is None) or (d_gate > gate_lim)
        rows.append({"cap": cap, "value": val, "cap_fp": C["lib"], "part": part, "part_value": P["value"][:40], "part_fp": P["lib"], "pin": pin, "part_pads": len(P["pads"]), "gate_lim": gate_lim,
                     "fan_now": fan_now, "pitch_now": pitch_now, "fan_cu": fan_cu, "pitch_cu": pitch_cu, "escaped": esc, "fan_ruled": fan_ruled,
                     "cap_courtyard": [round(cw, 3), round(ch, 3)], "part_has_courtyard": P["has_cy"],
                     "dmin_outside_fan": round(dmin_fan, 3), "dmin_outside_courtyard": round(dmin_cy, 3),
                     "d_now_centre": round(dnow, 2), "d_gate_pad_to_pin": d_gate, "over_gate_limit": gate_fail_without_allow})
    return rows

if __name__ == "__main__":
    rows = main(sys.argv[1:])
    if "--json" in sys.argv: json.dump(rows, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    for r in rows:
        if "note" in r: print("%-6s %-6s pin %-3s %s" % (r["cap"], r["part"], r["pin"], r["note"])); continue
        print("%-6s %-22s %-6s %-26s pin %-3s gate %.0f fan_now %-5s (%s) fan_cu %-5s (%s) fan_ruled %-5s cap_cy %s  dmin_fan %5.2f  dmin_cy %5.2f  now %6.2f  gate_pad %s over %s"
              % (r["cap"], r["value"][:22], r["part"], r["part_fp"].split(":")[-1][:26], r["pin"], r["gate_lim"], r["fan_now"], r["pitch_now"], r["fan_cu"], r["pitch_cu"], r["fan_ruled"], r["cap_courtyard"],
                 r["dmin_outside_fan"], r["dmin_outside_courtyard"], r["d_now_centre"], r["d_gate_pad_to_pin"], r["over_gate_limit"]))
