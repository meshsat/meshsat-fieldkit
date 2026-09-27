#!/usr/bin/env python3
"""FEA-006, the inventory: what of DECOUPLING.md's T1 to T10, G1 to G14 and the five circuit gaps is in the tree.

MESHSAT-1357, stream d6dec, 27 September 2026. Prototype design: nothing built, ordered or measured.

It reads, and writes nothing in the tree but its own two outputs beside this file:
  * the six committed netlists (v2/ecad/pcb-*-<phase>/out/*.net), PARSED by tools/netlist_sexp.py;
  * the six committed intent files beside them;
  * the tools named by section 8.1, by their AST (what a function is called with, which names a file defines);
  * the registry entry of DEC-001 (pcb_rules.yaml) and the six live bypass-allow.txt files.

Each row says DONE, PARTLY or NOT DONE and carries the evidence it was decided on. A row is DONE only when the thing
the page asks for is read back on the netlist, the intent or the tool; "the generator's comment says so" is not read.

Usage: inventory.py [--ecad <v2/ecad>] [--out <dir>]      (default: this worktree's v2/ecad, this folder)"""
import os, sys, json, ast, re, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.normpath(os.path.join(HERE, "..", "..", "..", "ecad"))
BOARDS = {"a": ("pcb-a-power-a23", "pcb-a-power"), "b": ("pcb-b-compute-b19", "pcb-b-compute"),
          "c": ("pcb-c-display-c8", "pcb-c-display"), "d": ("pcb-d-aprs-d9", "pcb-d-aprs"),
          "e": ("pcb-e1-dock-e7", "pcb-e1-dock"), "p": ("pcb-p-pack-p2", "pcb-p-pack")}
LIVE = {"a": "pcb-a-power", "b": "pcb-b-compute", "c": "pcb-c-display", "d": "pcb-d-aprs", "e": "pcb-e1-dock",
        "p": "pcb-p-pack"}


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def load(ecad):
    sys.path.insert(0, os.path.join(ecad, "tools"))
    import netlist_sexp as ns
    out = {}
    for L, (d, s) in BOARDS.items():
        np_, ip = os.path.join(ecad, d, "out", s + ".net"), os.path.join(ecad, d, "out", s + "-intent.json")
        doc = ns.load(np_); it = json.load(open(ip, encoding="utf-8"))
        out[L] = {"doc": doc, "intent": it, "netlist": os.path.relpath(np_, ecad), "netlist_sha": sha16(np_),
                  "intent_sha": sha16(ip), "ns": ns}
    return out


def val(b, ref): return b["doc"]["components"].get(ref, {}).get("value", "")
def parts(b, pat): return sorted((r for r, c in b["doc"]["components"].items() if re.search(pat, c["value"])
                                  and re.match(r"^U\d", r)), key=lambda r: (len(r), r))
def entries(b, part=None, pin=None):
    return [e for e in b["intent"].get("bypass", []) if (part is None or e["part"] == part)
            and (pin is None or str(e["pin"]) == str(pin))]
def uF(b, ref):
    f = b["ns"].farads(val(b, ref)); return None if f is None else f * 1e6
def fmt(b, e):
    x = {k: v for k, v in e.items() if k not in ("cap", "part", "pin", "net", "class", "basis", "provisional")}
    return "%s (%s) at %s.%s net %s class %s%s" % (e["cap"], val(b, e["cap"]), e["part"], e["pin"], e["net"],
                                                     e.get("class"), (" " + json.dumps(x, sort_keys=True)) if x else "")
def on_net(b, ref, net): return any(v["net"] == net for v in b["doc"]["pins"].get(ref, {}).values())


def need(b, part, pin, min_uF, max_uF=None, cls=None, n=1):
    """The declared capacitors at one pin with a value in [min, max] and the class asked: (ok, evidence lines)."""
    got = []
    for e in entries(b, part, pin):
        u = uF(b, e["cap"])
        if u is None or u < min_uF * 0.999 or (max_uF is not None and u > max_uF * 1.001): continue
        if cls and e.get("class") not in (cls if isinstance(cls, (list, tuple)) else (cls,)): continue
        if not on_net(b, e["cap"], b["doc"]["pin_net"].get((part, str(pin)))): continue
        got.append(e)
    return len(got) >= n, [fmt(b, e) for e in got]


# ------------------------------------------------------------------------------------------------ the G items
def g1(B):
    b = B["a"]; ev = []; ok = True
    lm = parts(b, r"^LM5176")
    ev.append("%d LM5176 stages on the netlist: %s" % (len(lm), ", ".join(lm)))
    visns = [fmt(b, e) for u in lm for e in entries(b, u, 3)]
    ok &= not visns; ev.append("declared against VISNS (pin 3): %s" % (visns or "none"))
    loops = b["intent"].get("power_loops", [])
    for u in lm:
        o1, e1 = need(b, u, 2, 0.1, 1.0, "D"); o2, e2 = need(b, u, 24, 0.1, 0.1, "D")
        o3, e3 = need(b, u, 23, 1.0, 4.7, "L")
        li = [l for l in loops if l["converter"] == u and l["loop"] == "input"]
        lo = [l for l in loops if l["converter"] == u and l["loop"] == "output"]
        cin_at_pin = [fmt(b, e) for e in entries(b, u, 2) if (uF(b, e["cap"]) or 0) > 1.0]
        ok &= o1 and o2 and o3 and bool(li) and bool(lo) and not cin_at_pin
        ev.append("%s: VIN pin 2 %s; BIAS pin 24 %s; VCC pin 23 %s; input loop %s; output loop %d capacitor(s); "
                  "a CIN above 1 uF declared at the VIN pin: %s"
                  % (u, e1 or "NONE", e2 or "NONE", e3 or "NONE",
                     (li[0]["caps"] + li[0]["parts"]) if li else "NONE", len(lo[0]["caps"]) if lo else 0,
                     cin_at_pin or "none"))
    return ok, ev


def g2(B):
    b = B["a"]; ev = []; ok = True
    for u in parts(b, r"^TPS62933"):
        o1, e1 = need(b, u, 3, 0.1, 0.1, "R"); o2, e2 = need(b, u, 3, 4.7, None, "R")
        ok &= o1 and o2; ev.append("%s (%s): 0.1 uF at VIN pin 3 %s; input capacitor %s"
                                   % (u, val(b, u)[:40], e1 or "NONE", e2 or "NONE"))
    return ok, ev


def g3(B):
    b = B["a"]; u = (parts(b, r"^BQ25731") or [None])[0]
    l = [x for x in b["intent"].get("power_loops", []) if x["converter"] == u and x["loop"] == "input"]
    caps = l[0]["caps"] if l else []
    ok = bool(l) and {"C190", "C191"} <= set(caps) and l[0].get("class") == "R"
    return ok, ["%s input loop: caps %s (%s), parts %s, class %s, same_side %s"
                % (u, caps, ", ".join("%s %s" % (c, val(b, c)) for c in caps), l[0]["parts"] if l else None,
                   l[0].get("class") if l else None, l[0].get("same_side") if l else None)]


def g4(B):
    b = B["b"]; ev = []; ok = True; us = parts(b, r"^TPS62933")
    for u in us:
        o1, e1 = need(b, u, 3, 0.1, 0.1, "R"); ok &= o1
        ev.append("%s: 0.1 uF at VIN pin 3 %s" % (u, e1 or "NONE"))
    ok &= len(us) == 7; ev.insert(0, "%d TPS62933 on the netlist (the page counts seven)" % len(us))
    return ok, ev


def g5(B):
    b = B["b"]; ev = []; ok = True
    for u in parts(b, r"TS3DV642"):
        o, e = need(b, u, 1, 0.1, 0.1, "D"); ok &= o; ev.append("%s VCC pin 1: %s" % (u, e or "NONE"))
    at_poe = [fmt(b, e) for u in parts(b, r"TPS23861") for e in entries(b, u, 1)]
    ev.append("declared at the PoE controller's pin 1: %s" % at_poe)
    ok &= all("C37" not in x and "C38" not in x for x in at_poe)
    return ok, ev


def g6(B):
    b = B["b"]; ev = []; ok = True
    for fam in ("STM32H743", "PI7C9X2G404SL", "TUSB8041", "KSZ9897", "TMUXHS4212", "TS3USB221A", "CP2102N"):
        us = parts(b, fam); n = sum(len(entries(b, u)) for u in us)
        noclass = [e["cap"] for u in us for e in entries(b, u) if not e.get("class") or not e.get("basis")]
        ok &= bool(us) and n > 0 and not noclass
        ev.append("%s: %d part(s) %s, %d declaration(s), without class or basis: %s"
                  % (fam, len(us), ",".join(us), n, noclass or "none"))
    return ok, ev


def g7(B):
    b = B["b"]; ev = []; ok = True
    for u in parts(b, "STM32H743"):
        o1, e1 = need(b, u, 21, 0.1, 0.1, "D"); o2, e2 = need(b, u, 21, 1.0, 1.0, "D")
        ok &= o1 and o2; ev.append("%s VDDA pin 21: %s; %s" % (u, e1 or "NO 100 nF", e2 or "NO 1 uF"))
    for u in parts(b, "TUSB8041"):
        vdd = [p for p, v in b["doc"]["pins"][u].items() if v["function"] == "VDD"]
        miss = [p for p in vdd if not need(b, u, p, 0.1, 0.1, "D")[0]]
        ok &= len(vdd) == 8 and not miss
        ev.append("%s: %d pins the netlist names VDD, without a 0.1 uF of their own: %s" % (u, len(vdd), miss or "none"))
    for u in parts(b, "KSZ9897"):
        fn = {}
        for p, v in b["doc"]["pins"][u].items():
            if v["function"] in ("DVDDL", "AVDDL", "AVDDH", "VDDIO"): fn.setdefault(v["function"], []).append(p)
        small = {k: [p for p in ps if need(b, u, p, 0.1, 0.1, "D")[0]] for k, ps in fn.items()}
        bulk = {k: [fmt(b, e) for p in ps for e in entries(b, u, p) if (uF(b, e["cap"]) or 0) >= 10] for k, ps in fn.items()}
        n01 = sum(len(v) for v in small.values())
        want = {"DVDDL": 22, "AVDDL": 22, "AVDDH": 22, "VDDIO": 10}
        okb = all(any(abs((uF(b, x.split(" ")[0]) or 0) - want[k]) < 0.01 for x in bulk.get(k, [])) for k in want)
        ok &= n01 == 27 and okb
        ev.append("%s: supply pins by the netlist's pin names %s; with a 0.1 uF of their own %d (the maker's figure "
                  "draws 27); bulk %s" % (u, {k: len(v) for k, v in fn.items()}, n01,
                                          {k: [x.split(" at ")[0] for x in v] for k, v in bulk.items()}))
    for u in parts(b, "CP2102N"):
        o1, e1 = need(b, u, 7, 4.7, 4.7, "D"); o2, e2 = need(b, u, 7, 0.1, 0.1, "D")
        ok &= o1 and o2; ev.append("%s VREGIN pin 7: %s; %s" % (u, e1 or "NO 4.7 uF", e2 or "NO 0.1 uF"))
    return ok, ev


def g8(B):
    b = B["p"]; es = entries(b)
    ok = {e["cap"] for e in es} == {"C1", "C6", "C8", "C14"} and all(e.get("class") == "A" and e.get("basis")
                                                                     and e.get("provisional") for e in es)
    return ok, [fmt(b, e) + " provisional: %s" % bool(e.get("provisional")) for e in es]


def g9(B):
    b = B["c"]; u = parts(b, "^RP2040")[0]
    o1, e1 = need(b, u, 43, 0.1, 0.1, "D"); o2, e2 = need(b, u, 48, 0.1, 0.1, "D")
    return o1 and o2, ["%s ADC_AVDD pin 43: %s" % (u, e1 or "NONE"), "%s USB_VDD pin 48: %s" % (u, e2 or "NONE")]


def g10(B):
    b = B["b"]; ev = []; ok = True
    u = parts(b, "^AP63203")[0]
    at_en, at_fb = [fmt(b, e) for e in entries(b, u, 2)], [fmt(b, e) for e in entries(b, u, 1)]
    o1, e1 = need(b, u, 3, 10, None, "R")
    ok &= o1 and not at_en and not at_fb
    ev.append("%s: at VIN pin 3 %s; at EN pin 2 %s; at FB pin 1 %s" % (u, e1 or "NONE", at_en or "none", at_fb or "none"))
    out_net = [e for e in entries(b) if e["cap"] in ("C5", "C6")]
    ok &= len(out_net) == 2 and all(e["part"].startswith("L") and e.get("class") == "R" for e in out_net)
    ev.append("the output capacitors: %s" % [fmt(b, e) for e in out_net])
    u27 = parts(b, r"^AP2112K-2\.5")[0]
    c12 = [e for e in entries(b, u27) if e["cap"] == "C12"]; c13 = [e for e in entries(b, u27) if e["cap"] == "C13"]
    ok &= bool(c12) and c12[0].get("class") == "L" and bool(c13) and c13[0].get("class") == "D"
    ev.append("%s: %s" % (u27, [fmt(b, e) for e in c12 + c13]))
    return ok, ev


def g11(B):
    b = B["e"]; u = parts(b, "^AP63205")[0]
    at_en = [fmt(b, e) for e in entries(b, u, 2)]; o, e = need(b, u, 3, 10, None, "R")
    c31 = [x for x in entries(b) if x["cap"] == "C31"]
    ok = o and not at_en and bool(c31) and str(c31[0]["pin"]) == "3"
    return ok, ["%s: at VIN pin 3 %s; at EN pin 2 %s" % (u, e or "NONE", at_en or "none")]


def g12(B, ecad):
    b = B["d"]; u = parts(b, "TPA6132A2")[0]; ev = []
    o1, e1 = need(b, u, 12, 2.2, 2.2, "L"); o2, e2 = need(b, u, 14, 2.2, 2.2, "D"); o3, e3 = need(b, u, 14, 10, None, "B2")
    mm = [e.get("maker_mm") for e in entries(b, u) if e["cap"] in ("C31", "C32")]
    src = open(os.path.join(ecad, "tools", "gen_sch_d.py"), encoding="utf-8").read()
    full = [(i + 1, l.strip()) for i, l in enumerate(src.splitlines()) if "SLOS553" in l]
    stale = [c for c in full if "which read SLOS553" not in c[1]]
    cites = [(i, l[:150]) for i, l in full]
    ok = o1 and o2 and o3 and mm == [5.0, 5.0] and not stale
    ev += ["%s HPVDD pin 12: %s" % (u, e1 or "NONE"), "%s VDD pin 14: %s; optional bulk %s" % (u, e2 or "NONE", e3 or "NONE"),
           "maker_mm on C31, C32: %s" % mm,
           "gen_sch_d.py lines naming SLOS553: %s (a line that records the correction is not a citation)" % (cites or "none"),
           "dielectric and land read back on the netlist: %s" % ["%s %s %s" % (c, val(b, c), b["doc"]["components"][c]["footprint"]) for c in ("C31", "C32")]]
    return ok, ev


def g13(B):
    ev = []; ok = True
    for L in ("c", "e"):
        b = B[L]; u = parts(b, "^RP2040")[0]
        o1, e1 = need(b, u, 45, 1.0, 1.0, "L"); o2, e2 = need(b, u, 23, 0.1, 0.1, "D"); o3, e3 = need(b, u, 50, 0.1, 0.1, "D")
        o4, e4 = need(b, u, 44, 1.0, 1.0, "D")
        net = b["doc"]["pin_net"][(u, "45")]
        on = sorted((r, val(b, r)) for r, p, f, t in b["doc"]["nets"][net] if r.startswith("C"))
        ok &= o1 and o2 and o3 and o4 and len(on) == 3
        ev.append("board %s %s: VREG_VOUT pin 45 %s; DVDD pin 23 %s; DVDD pin 50 %s; VREG_VIN pin 44 %s; capacitors "
                  "on net %s: %s" % (L.upper(), u, e1 or "NONE", e2 or "NONE", e3 or "NONE", e4 or "NONE", net, on))
    return ok, ev


def g14(B):
    ev = []; ok = True
    for L in ("c", "d", "e"):
        b = B[L]; es = entries(b)
        bad = [e["cap"] for e in es if e.get("class") not in ("R", "D", "L", "A", "B1", "B2") or not str(e.get("basis") or "").strip()]
        ok &= bool(es) and not bad
        ev.append("board %s: %d declarations, without a ruled class or a basis: %s" % (L.upper(), len(es), bad or "none"))
    b = B["d"]
    for cap, cls in (("C8", "L"), ("C9", "L"), ("C17", "B1")):
        e = [x for x in entries(b) if x["cap"] == cap]
        ok &= bool(e) and e[0].get("class") == cls; ev.append("board D %s" % (fmt(b, e[0]) if e else cap + " NOT DECLARED"))
    e17 = [x for x in entries(b) if x["cap"] == "C17"]
    ok &= bool(e17) and re.search(r"TLV758", val(b, e17[0]["part"])) is not None
    ev.append("C17's declared part is %s" % (val(b, e17[0]["part"])[:60] if e17 else None))
    return ok, ev


# --------------------------------------------------------------------------- the schema the generators write (T5)
CANON = {"value_floor", "esr_max", "same_side", "maker_mm", "provisional", "value_ceiling", "regulator"}
def schema(B):
    rows = []
    for L, b in B.items():
        es = entries(b); keys = {}
        for e in es:
            for k in e:
                if k not in ("cap", "part", "pin", "net", "class", "basis"): keys[k] = keys.get(k, 0) + 1
        ncls = {}
        for e in es: ncls[e.get("class")] = ncls.get(e.get("class"), 0) + 1
        l_nofloor = [e["cap"] for e in es if e.get("class") == "L"
                     and not any(e.get(k) not in (None, "") for k in ("value_floor", "floor", "floor_uF"))]
        r_noside = [e["cap"] for e in es if e.get("class") == "R" and e.get("same_side") is not True]
        l_noesr = [e["cap"] for e in es if e.get("class") == "L" and not any(k in e for k in ("esr_max", "esr", "esr_bound"))]
        rows.append({"board": L, "entries": len(es), "classes": ncls, "extra_keys": keys,
                     "not_canonical": sorted(k for k in keys if k not in CANON),
                     "class_L_without_a_floor": l_nofloor, "class_L_without_an_esr_statement": l_noesr,
                     "class_R_without_same_side": r_noside})
    return rows


# ------------------------------------------------------------------------------------------------ the T items
def _ast(path): return ast.parse(open(path, encoding="utf-8").read())
def _defs(tree): return {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
def _assigns(tree):
    out = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant):
            for t in n.targets:
                if isinstance(t, ast.Name): out[t.id] = n.value.value
    return out
def _imports(tree):
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): names |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module: names.add(n.module)
    return names
def _calls(tree, attr):
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if name == attr: out.append(n)
    return out


def tools(ecad):
    T = os.path.join(ecad, "tools"); rows = []
    esc, bs, bp = _ast(os.path.join(T, "escape.py")), _ast(os.path.join(T, "bypass_slots.py")), _ast(os.path.join(T, "bypass_place.py"))
    ic, it = _ast(os.path.join(T, "intent_checks.py")), _ast(os.path.join(T, "intent.py"))
    own = {"escape.py": sorted(_defs(esc) & {"is_fine", "min_pitch"}), "bypass_slots.py": sorted(_defs(bs) & {"_needs_fan"}),
           "bypass_place.py": sorted(n for n in _imports(bp) if n == "bypass_slots")}
    shared = sorted((_imports(esc) & _imports(bs) & _imports(bp)) - {"sys", "os", "json", "math", "pcbnew", "re"})
    rows.append(("T1", "one selection function for the escape pass and both placers", bool(shared) and not own["escape.py"] and not own["bypass_slots.py"],
                 ["escape.py defines its own %s; bypass_slots.py defines its own %s; bypass_place.py takes the fan from %s; "
                  "tools-local modules all three import: %s" % (own["escape.py"], own["bypass_slots.py"], own["bypass_place.py"], shared or "none")]))
    lim = {"bypass_place.py": _assigns(bp).get("LIMIT"), "bypass_slots.py": _assigns(bs).get("LIMIT")}
    src_ic = open(os.path.join(T, "intent_checks.py"), encoding="utf-8").read()
    val_key = [i + 1 for i, l in enumerate(src_ic.splitlines()) if "loop = 6.0 if any(u in val.lower()" in l]
    rows.append(("T2", "one limit function keyed by the class, rail pad to pin in all three tools", not any(v is not None for v in lim.values()) and not val_key,
                 ["module constants LIMIT: %s; intent_checks.py decides 6.0 or 3.0 from the value string at line %s"
                  % (lim, val_key or "none")]))
    rot = []
    for name, tree in (("bypass_slots.py", bs),):
        for c in _calls(tree, "place"):
            if len(c.args) >= 4 and isinstance(c.args[3], ast.Constant): rot.append("%s:%d place(..., rotation %r, ...)" % (name, c.lineno, c.args[3].value))
    setrot = [n.lineno for n in ast.walk(bp) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr in ("SetOrientationDegrees", "SetOrientation", "Rotate")]
    rows.append(("T3", "the placers try the four rotations", False if rot and not setrot else None,
                 ["%s; bypass_place.py calls that turn a footprint: %s" % (rot or "no constant rotation found", setrot or "none")]))
    src_bs = open(os.path.join(T, "bypass_slots.py"), encoding="utf-8").read(); src_bp = open(os.path.join(T, "bypass_place.py"), encoding="utf-8").read()
    src_esc = open(os.path.join(T, "escape.py"), encoding="utf-8").read()
    reads_class = {n: bool(re.search(r'\.get\(\s*"class"\s*\)|\[\s*"class"\s*\]', s)) for n, s in
                   (("bypass_slots.py", src_bs), ("bypass_place.py", src_bp), ("escape.py", src_esc))}
    rows.append(("T4", "the fan opened for a class R entry's own converter and a class D or L entry's own-pin window; escapes lost printed per cause",
                 all(reads_class.values()), ["which of the three reads an entry's class: %s" % reads_class]))
    bdef = next(n for n in it.body if isinstance(n, ast.FunctionDef) and n.name == "bypass")
    args = [a.arg for a in bdef.args.args]
    rows.append(("T5", "intent.bypass takes a class and a basis and intent.write refuses an entry without one",
                 "cls" in args or "klass" in args or "class_" in args,
                 ["intent.py:%d def bypass(%s)" % (bdef.lineno, ", ".join(args))]))
    allow = {}
    for L, d in LIVE.items():
        p = os.path.join(ecad, d, "bypass-allow.txt")
        lines = [l.strip() for l in open(p, encoding="utf-8").read().splitlines() if l.strip() and not l.startswith("#")] if os.path.exists(p) else []
        allow[L] = {"lines": len(lines), "naming_a_capacitor": sum(1 for l in lines if re.match(r"^C\d+\s*:", l))}
    first = [i + 1 for i, l in enumerate(src_ic.splitlines()) if "allowed[0][:56]" in l]
    rows.append(("T6", "an allow line names its capacitor; allowed entries counted as justified, never as pass; the blanket lines deleted",
                 not first and all(v["lines"] == v["naming_a_capacitor"] for v in allow.values()),
                 ["intent_checks.py quotes the file's first line for every far capacitor at line %s; live allow files: %s" % (first or "none", allow)]))
    import yaml
    rules = yaml.safe_load(open(os.path.join(T, "pcb_rules.yaml"), encoding="utf-8"))
    dec = next(r for r in rules["rules"] if r["id"] == "DEC-001")
    cov = yaml.safe_load(open(os.path.join(T, "pcb_rules_coverage.yaml"), encoding="utf-8"))["coverage"]["DEC-001"]
    rows.append(("T7", "DEC-001's registry text: sources, status, acceptance and rationale",
                 dec["source_status"] != "SOURCE_UNVERIFIED" and bool(dec["sources"]),
                 ["pcb_rules.yaml DEC-001: source_status %s, %d source(s); coverage gap_category %s"
                  % (dec["source_status"], len(dec["sources"] or []), cov.get("gap_category"))]))
    rows.append(("T8", "PCB-OPEN-PAIRS.md re-rendered in the commit that merges the ruling", None,
                 ["a step of the merge commit, the integrator's: it has nothing to render until T7's text is in the registry"]))
    # the gate's decoupling block alone: the rest of intent_checks.py is the return-path and rail rules
    i0, i1 = src_ic.find("    # 2. decoupling"), src_ic.find("    # 3. rails exist")
    assert 0 < i0 < i1, "intent_checks.py: the decoupling block was not found between its two comments"
    dec_block = src_ic[i0:i1]
    far = {n: bool(re.search(r"allowance|far.side|two.sided", s, re.I)) for n, s in (("bypass_slots.py", src_bs), ("bypass_place.py", src_bp), ("intent_checks.py decoupling block", dec_block))}
    rows.append(("T9", "the other side: which boards, where refused, the via allowance, the maker's same side", all(far.values()),
                 ["which tool names a via allowance or a far side: %s" % far]))
    own_via = bool(re.search(r"own via|shares? (a|the) via", dec_block, re.I))
    rows.append(("T10", "the ground pad's own via named, its copper length printed", own_via,
                 ["intent_checks.py's reach test `closes()` accepts any via of the net within NEAR_VIA or a pour; a test of the via's other landings: %s" % own_via]))
    return rows


def main(a):
    ecad = a[a.index("--ecad") + 1] if "--ecad" in a else ECAD
    out = a[a.index("--out") + 1] if "--out" in a else HERE
    B = load(ecad)
    try: head = subprocess.run(["git", "-C", ecad, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    except Exception: head = "unknown"
    G = [("G1", "A", "LM5176: no VISNS declaration, a VIN-pin capacitor on every stage, CIN against the power loop, VCC class L", g1(B)),
         ("G2", "A", "TPS62933: 0.1 uF at VIN and GND, class R, on U12 and U33", g2(B)),
         ("G3", "A", "BQ25731: C190 and C191 declared class R against the input loop", g3(B)),
         ("G4", "B", "TPS62933: 0.1 uF at VIN and GND on all seven, class R (circuit gap 1)", g4(B)),
         ("G5", "B", "C37 and C38 declared at the TS3DV642s' VCC, not at the PoE controller", g5(B)),
         ("G6", "B", "the capacitors of the seven fine-pitch families declared with their classes", g6(B)),
         ("G7", "B", "STM32H743 VDDA 100 nF + 1 uF; TUSB8041 eight 0.1 uF on the core; KSZ9897R per its maker's figure; CP2102N VREGIN 4.7 uF + 0.1 uF (circuit gaps 2 to 5)", g7(B)),
         ("G8", "P", "C1, C6, C8 and C14 class A with their clauses, provisional", g8(B)),
         ("G9", "C", "RP2040 ADC_AVDD and USB_VDD 100 nF each, class D", g9(B)),
         ("G10", "B", "AP63203: C4 at VIN, C5 and C6 against the output loop; AP2112K: C12 class L, C13 class D", g10(B)),
         ("G11", "E", "AP63205: C31 at VIN pin 3", g11(B)),
         ("G12", "D", "TPA6132A2: 2.2 uF at HPVDD and VDD, the maker's 5 mm carried, C33 class B2, the citation", g12(B, ecad)),
         ("G13", "C, E", "RP2040: 1 uF at VREG_VOUT class L, 100 nF at each DVDD pin, the VREG_VIN 1 uF class D", g13(B)),
         ("G14", "C, D, E", "a class on every entry; D: C8 and C9 class L, C17 class B1", g14(B))]
    Trows = tools(ecad); S = schema(B)
    rec = {"what": "FEA-006 inventory, read on the set 6 netlists", "tree": head,
           "inputs": {L: {"netlist": b["netlist"], "netlist_sha256_16": b["netlist_sha"], "intent_sha256_16": b["intent_sha"],
                          "netlist_date": b["doc"]["date"]} for L, b in B.items()},
           "generator_items": [{"item": i, "board": bd, "asks": w, "status": "DONE" if r[0] else "NOT DONE", "evidence": r[1]} for i, bd, w, r in G],
           "tool_items": [{"item": i, "asks": w, "status": "DONE" if ok else ("NOT DONE" if ok is False else "NOT APPLICABLE YET"), "evidence": ev} for i, w, ok, ev in Trows],
           "schema": S}
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "inventory.json"), "w", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
    for r in rec["generator_items"] + rec["tool_items"]:
        print("%-4s %-9s %s" % (r["item"], r["status"], r["asks"][:110]))
        for e in r["evidence"]: print("       " + e[:260])
    for s in S: print("schema", json.dumps(s, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
