#!/usr/bin/env python3
"""kisch: the KiCad 9 schematic engine of this project, in one place (10 September 2026, MESHSAT-862, red team C2).

Six `gen_sch_*.py` carried their own copy of these thirty functions and the copies had diverged in two lineages: twelve of the
twenty five shared functions differed, and the difference that mattered was `ic()`. The a/e lineage refused an IC with an unlisted
pin; the b/c/d/p lineage filled it with "NC" silently, on the boards with a 200-pin receptacle pair, a 128-pin switch and a
100-pin bridge. The engine below is the b/c/d/p version, which is the newer one (duplicate-reference check in `part()`, SYNTH
symbols in `ensure()`), with the a/e strictness restored in `ic()`.

A board file does:

    import kisch
    from kisch import part, ic, c, r, esd, nfet, noconn, ...
    kisch.configure(fp=FP, power=POWER, synth=SYNTH, stub=5.08)
    ...
    kisch.P            the parts, in order          kisch.out       the sheet body being written
    kisch.reset_body() start a fresh sheet body     kisch.libsyms   the lib_symbols block

The state is module level because one process generates one board. Nothing here knows anything about any board: every table
(`FP`, `POWER`, `SYNTH`) comes from the board file through `configure()`."""
import re, sys, os, uuid
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intent as _intent   # `c(..., bypass=(part, pin))` records the pin a decoupling capacitor serves; the engine owns that call


SYMDIR = os.environ.get("KICAD_SYMBOLS", "/usr/share/kicad/symbols/")
LIBCACHE = {}
libsyms = {}
out = []
P = []
pf_n = [0]
ROOT = str(uuid.uuid4())
STUB = 5.08
PROJECT = ""  # the KiCad project name written into every symbol instance, from the board file
FP = {}       # footprint key -> library footprint, from the board file
POWER = {}    # net name -> (library, symbol) for the nets drawn as power symbols
SYNTH = {}    # synthesised symbols (a module drawn as one big connector), from the board file


def configure(fp=None, power=None, synth=None, stub=None, symdir=None, root=None, seed=None, project=None):
    """The board file hands its tables to the engine once, before it starts adding parts."""
    global FP, POWER, SYNTH, STUB, SYMDIR, ROOT, PROJECT
    if project is not None: PROJECT = project
    if seed is not None: UUID_SEED[0] = str(seed); _UUID_N[0] = 0
    if fp is not None: FP = fp
    if power is not None: POWER = power
    if synth is not None: SYNTH = synth
    if stub is not None: STUB = stub
    if symdir is not None: SYMDIR = symdir
    if root is not None: ROOT = root


def reset_body():
    """Start a fresh sheet body; the parts and the symbol library survive (`layout()` is called more than once per run)."""
    global out
    out = []
    pf_n[0] = 0
    _UUID_N[0] = 0   # a fresh body starts the uuid sequence again, so two runs of one board agree
    return out


def parse(s):
    tok = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+', s)
    def rd(i):
        out = []
        while i < len(tok):
            t = tok[i]
            if t == "(":
                sub, i = rd(i + 1); out.append(sub)
            elif t == ")":
                return out, i + 1
            else:
                out.append(t); i += 1
        return out, i
    return rd(0)[0]

def ser(n, ind=0):
    if not isinstance(n, list): return n
    if all(not isinstance(x, list) for x in n): return "(" + " ".join(n) + ")"
    head = []
    i = 0
    while i < len(n) and not isinstance(n[i], list): head.append(n[i]); i += 1
    s = "(" + " ".join(head)
    for x in n[i:]:
        s += "\n" + "\t" * (ind + 1) + ser(x, ind + 1) if isinstance(x, list) else " " + x
    return s + "\n" + "\t" * ind + ")"

def find_sym(lib, name):
    for e in lib_tree(lib)[1:]:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]) == name: return e
    raise SystemExit("symbol not found: %s:%s" % (lib, name))

def flatten_raw(lib, name):
    import copy
    sym = copy.deepcopy(find_sym(lib, name))
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext: return flatten(lib, name)
    sym[1] = q(lib + ":" + name); return sym

def flatten(lib, name):
    sym = find_sym(lib, name)
    ext = [e for e in sym if isinstance(e, list) and e and e[0] == "extends"]
    if ext:
        parent = flatten_raw(lib, uq(ext[0][1]))
        child_props = {uq(e[1]): e for e in sym if isinstance(e, list) and e and e[0] == "property"}
        out = ["symbol", q(lib + ":" + name)]
        for e in parent[2:]:
            if isinstance(e, list) and e and e[0] == "property": e = child_props.get(uq(e[1]), e)
            out.append(e)
        for k, e in child_props.items():
            if not any(isinstance(x, list) and x and x[0] == "property" and uq(x[1]) == k for x in out): out.append(e)
        return rename_units(out, uq(ext[0][1]), name)
    return rename_units(flatten_raw(lib, name), name, name)

def rename_units(sym, oldname, newname):
    for e in sym:
        if isinstance(e, list) and e and e[0] == "symbol" and uq(e[1]).startswith(oldname + "_"): e[1] = q(newname + uq(e[1])[len(oldname):])
    return [e for e in sym if not (isinstance(e, list) and e and e[0] == "extends")]

def lib_tree(lib):
    if lib not in LIBCACHE: LIBCACHE[lib] = parse(open(SYMDIR + lib + ".kicad_sym").read())[0]
    return LIBCACHE[lib]

def pins_of(sym):
    pins = []
    def walk(n):
        for e in n:
            if isinstance(e, list) and e:
                if e[0] == "symbol": walk(e)
                elif e[0] == "pin":
                    at = [x for x in e if isinstance(x, list) and x and x[0] == "at"][0]
                    num = uq([x for x in e if isinstance(x, list) and x and x[0] == "number"][0][1])
                    nm = uq([x for x in e if isinstance(x, list) and x and x[0] == "name"][0][1])
                    pins.append((num, nm, float(at[1]), float(at[2]), int(float(at[3]))))
    walk(sym); return pins

def extents(sym):
    pins = pins_of(sym); xs = [p[2] for p in pins] or [0]; ys = [p[3] for p in pins] or [0]
    return min(xs), max(xs), min(ys), max(ys)

def synth_symbol(lib, name):
    pins = SYNTH[name]; n = len(pins); rows = (n + 1) // 2; first = min(pins)
    W = 30.48; H = rows * 2.54 + 2.54
    fx = lambda: ["effects", ["font", ["size", "1.27", "1.27"]]]
    sym = ["symbol", q(lib + ":" + name), ["pin_names", ["offset", "1.016"]], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
           ["property", q("Reference"), q("U"), ["at", "0", "%.2f" % (H / 2 + 1.27), "0"], fx()],
           ["property", q("Value"), q(name), ["at", "0", "%.2f" % (-H / 2 - 1.27), "0"], fx()],
           ["property", q("Footprint"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
           ["property", q("Datasheet"), q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]]]
    body = ["symbol", q(name + "_0_1"), ["rectangle", ["start", "%.2f" % (-W / 2), "%.2f" % (H / 2)], ["end", "%.2f" % (W / 2), "%.2f" % (-H / 2)],
            ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]]
    unit = ["symbol", q(name + "_1_1")]
    for num in sorted(pins):
        row = (num - first) // 2; y = H / 2 - 2.54 * (row + 1)
        if (num - first) % 2 == 0: at = ["at", "%.2f" % (-W / 2 - 2.54), "%.2f" % y, "0"]
        else: at = ["at", "%.2f" % (W / 2 + 2.54), "%.2f" % y, "180"]
        unit.append(["pin", "passive", "line", at, ["length", "2.54"], ["name", q(pins[num]), fx()], ["number", q(str(num)), fx()]])
    sym.append(body); sym.append(unit); return sym

def ensure(lib, name):
    key = lib + ":" + name
    if key not in libsyms: libsyms[key] = synth_symbol(lib, name) if name in SYNTH else flatten(lib, name)
    return libsyms[key]

def part(ref, lib, sym, value, fp, nets, lcsc=""):
    if any(p["ref"] == ref for p in P): raise SystemExit("duplicate reference " + ref)
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=FP.get(fp, fp), nets={str(k): v for k, v in nets.items()}, lcsc=lcsc))

def c(ref, val, a, b, fp="C", lcsc="", bypass=None):
    part(ref, "Device", "C", val, fp, {"1": a, "2": b}, lcsc)
    if bypass: _intent.bypass(ref, bypass[0], bypass[1])   # 8 Sep 2026 (MESHSAT-862): the pin this capacitor serves, for the decoupling gate

def r(ref, val, a, b, fp="R", lcsc=""): part(ref, "Device", "R", val, fp, {"1": a, "2": b}, lcsc)

def esd(ref, dp, dm, vbus): part(ref, "Power_Protection", "USBLC6-2SC6", "USBLC6-2SC6", "SOT236", {"1": dp, "6": dp, "3": dm, "4": dm, "5": vbus, "2": "GND"}, "C7519")

def noconn(x, y): out.append('(no_connect (at %.2f %.2f) (uuid "%s"))\n' % (x, y, U()))

def q(s): return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

def uq(s): return s[1:-1] if s.startswith('"') else s

UUID_NS = uuid.UUID("1b4e28ba-2fa1-11d2-883f-b9a761bde3fb")   # a fixed namespace; the values only have to be unique inside the file
UUID_SEED = ["meshsat"]
_UUID_N = [0]

def U():
    """A deterministic uuid, so the same board file regenerates byte for byte (10 September 2026).

    Every uuid used to be `uuid4()`, so no schematic could be diffed against its predecessor and the golden test the red team
    asks for could not exist. KiCad only needs them unique within the file. KISCH_RANDOM_UUID=1 restores random ones."""
    if os.environ.get("KISCH_RANDOM_UUID") == "1": return str(uuid.uuid4())
    _UUID_N[0] += 1
    return str(uuid.uuid5(UUID_NS, "%s:%d" % (UUID_SEED[0], _UUID_N[0])))

def tps22810(ref, vin, en, out, ct): part(ref, "Power_Management", "TPS22810DRV", "TPS22810DRV", "WSON6", {"6": vin, "5": en, "1": out, "2": "NC", "3": ct, "4": "GND", "7": "GND"})

def usb_c_recept(ref, dp, dm, vbus, cc1, cc2):
    part(ref, "Connector", "USB_C_Receptacle_USB2.0_16P", "USB-C 2.0 receptacle", "USBC",
         {"A1": "GND", "A12": "GND", "B1": "GND", "B12": "GND", "A4": vbus, "A9": vbus, "B4": vbus, "B9": vbus, "A5": cc1, "B5": cc2, "A6": dp, "B6": dp, "A7": dm, "B7": dm, "A8": "NC", "B8": "NC", "S1": "GND"}, "C165948")

def emit_pwr_flag(p, x, y):
    place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x, y); net = p["nets"]["1"]; wire(x, y, x, y + STUB)
    if net in POWER:
        lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", x, y + STUB); pf_n[0] += 1
    else: label(net, x, y + STUB, 270)

def place_symbol(lib, name, ref, value, fp, x, y, lcsc="", hide_props=False):
    sym = ensure(lib, name); pins = pins_of(sym); x0, x1, y0, y1 = extents(sym)
    s = '(symbol (lib_id %s) (at %.2f %.2f 0) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no) (fields_autoplaced yes) (uuid "%s")\n' % (
        q(lib + ":" + name), x, y, "no" if lib == "power" or name in ("TestPoint",) else "yes", "no" if lib == "power" else "yes", U())
    def prop(k, v, px, py, hide): return '\t(property %s %s (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (justify left)%s))\n' % (q(k), q(v), px, py, " (hide yes)" if hide else "")
    s += prop("Reference", ref, x + x1 + 1.27, y - y1 - 1.27, hide_props); s += prop("Value", value, x + x1 + 1.27, y - y1 + 1.27, hide_props)
    s += prop("Footprint", fp, x, y, True); s += prop("Datasheet", "", x, y, True); s += prop("Description", "", x, y, True)
    if lcsc: s += prop("LCSC", lcsc, x, y, True)
    for num, nm, px, py, rot in pins: s += '\t(pin %s (uuid "%s"))\n' % (q(num), U())
    s += '\t(instances (project %s (path "/%s" (reference %s) (unit 1))))\n)\n' % (q(PROJECT), ROOT, q(ref))
    out.append(s); return pins

def wire(x1, y1, x2, y2): out.append('(wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (x1, y1, x2, y2, U()))

def label(net, x, y, rot):
    just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
    out.append('(label %s (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (q(net), x, y, rot, just, U()))

def text(t, x, y, size=2.0): out.append('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f) bold) (justify left bottom)) (uuid "%s"))\n' % (q(t), x, y, size, size, U()))

def emit_part(p, x, y):
    pins = place_symbol(p["lib"], p["sym"], p["ref"], p["value"], p["fp"], x, y, p["lcsc"]); seen = set()
    for num, nm, px, py, rot in pins:
        sx, sy = x + px, y - py; key = (round(sx, 2), round(sy, 2)); net = p["nets"].get(num)
        if net is None: raise SystemExit("%s pin %s (%s) has no net assignment" % (p["ref"], num, nm))
        if key in seen: continue
        seen.add(key)
        if net == "NC": noconn(sx, sy); continue
        dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[rot]; ex, ey = sx + dx * STUB, sy + dy * STUB; wire(sx, sy, ex, ey)
        if net in POWER:
            lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", ex, ey); pf_n[0] += 1
        else: label(net, ex, ey, {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)])


def ic(ref, npins, value, fp, nets, lcsc=""):
    """An IC drawn as a numbered connector symbol (this project's pattern since A19): EVERY pin of the part is listed, and a
    deliberate no-connect is written "NC" by hand.

    10 September 2026 (red team C2): the a/e lineage refused an unlisted pin and the b/c/d/p lineage filled it with "NC"
    silently, so on the four boards that most need the check (B carries a 200-pin receptacle pair, a 128-pin PCIe switch and a
    100-pin Ethernet switch) a forgotten pin built clean. C's U9 is the EMCON buffer of the 9 September red team: dropping its
    output pin from the dictionary would have shipped the safety line floating. The strict version is the one that survives."""
    missing = [k for k in range(1, npins + 1) if str(k) not in nets and k not in nets]
    if missing:
        raise SystemExit("%s (%s, %d pins): pin%s %s ha%s no net. Write \"NC\" for a deliberate no-connect."
                         % (ref, value, npins, "" if len(missing) == 1 else "s", ", ".join(str(k) for k in missing), "s" if len(missing) == 1 else "ve"))
    part(ref, "Connector_Generic", "Conn_01x%02d" % npins, value, fp, nets, lcsc)
