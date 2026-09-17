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
_ANCHOR = [None]   # the column-defining x of the emission in progress: every item appended while a part is placed carries it
anchors = []


class Body(list):
    """The sheet body: a list of item strings that also remembers, per item, the x of the emission that wrote it. B19's
    banded page (15 Sep 2026, 32.194) moved each item by its OWN first coordinate, so a wide part's labels and wires
    crossed the band seam away from their symbol and 62 pins of U301 came loose; a band is a property of a column, and
    the column is the part's, so the anchor travels with every item."""
    def append(self, item):
        super().append(item); anchors.append(_ANCHOR[0])


out = Body()   # A and E never call reset_body(): the import-time body records anchors too
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


def reband(items, colw=92.0, w_max=2024.0, page_h=800.0, gap=60.0, x0=20.0, margin=30.0):
    """Fold the row of columns `layout()` drew into bands under a page that CONTAINS the drawing, and return the paper
    field for the sheet header.

    15 September 2026 (MESHSAT-862, appendix 32.194): every board's schematic was written on an A0 sheet and laid out
    as one row of 92 mm columns, 800 mm tall, as many columns as the parts needed: A's row is 2.8 m wide and B's 3.9 m.
    An exporter clips to the page, so the PDF a reviewer opened was an empty A0 frame with a title block. Eeschema takes
    a user page up to 3048 mm a side (tested on the box: 2100 x 1800 exports with its ink), so the row is folded into
    bands `w_max` wide, one under the other, and the paper is the drawing plus a margin. Positions only: no net, label
    or reference changes, and `build_sch` proves it by the netlist."""
    import re
    cols_per_band = max(1, int(w_max // colw)); band_w = cols_per_band * colw
    def first_x(item):
        m = re.search(r"\((?:at|xy) (-?[\d.]+) (-?[\d.]+)", item); return float(m.group(1)) if m else x0
    def shifted(item, dx, dy):
        return re.sub(r"\((at|xy) (-?[\d.]+) (-?[\d.]+)", lambda m: "(%s %.2f %.2f" % (m.group(1), float(m.group(2)) + dx, float(m.group(3)) + dy), item)
    bands = 0; new = []
    anc = anchors if len(anchors) == len(items) else [None] * len(items)
    for it, a in zip(items, anc):
        col = int((a - x0) // colw) if a is not None else int((first_x(it) - x0) // colw)   # the column is the emission's, never the item's own
        b = max(0, col // cols_per_band); bands = max(bands, b + 1)
        new.append(shifted(it, -b * band_w, b * (page_h + gap)) if b else it)
    items[:] = new
    W = band_w + x0 + margin if bands > 1 else max(first_x_max(items) + margin, 297.0)
    H = bands * (page_h + gap) - gap + margin + x0
    if W <= 1189 and H <= 841 and bands == 1: return '"A0"'
    return '"User" %.0f %.0f' % (min(W, 3048.0), min(H, 3048.0))


def first_x_max(items):
    import re
    xs = [float(m.group(1)) for it in items for m in re.finditer(r"\((?:at|xy) (-?[\d.]+) (-?[\d.]+)", it)]
    return max(xs) if xs else 0.0


def reset_body():
    """Start a fresh sheet body; the parts and the symbol library survive (`layout()` is called more than once per run)."""
    global out
    out = Body(); del anchors[:]
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

# A %-conversion left in a value is a string that was meant to be formatted and was not, and `value` is what
# reaches the silk, the schematic and the BOM's Comment column. B19 shipped three of them: the three 1.1 V hub
# core bucks all read "1.1 V hub core S%d", because that note was the one argument of the per-slot loop that
# nobody appended `% s` to. A tolerance ("26.7k 1%") ends at the percent sign and is untouched; this matches
# only a real conversion, a percent followed by its flags and a type letter.
_UNFORMATTED = __import__("re").compile(r"%[-+#0]*[0-9]*(?:\.[0-9]+)?[diouxXeEfFgGcrs]")

def part(ref, lib, sym, value, fp, nets, lcsc="", in_bom=True):
    if any(p["ref"] == ref for p in P): raise SystemExit("duplicate reference " + ref)
    _m = _UNFORMATTED.search(str(value))
    if _m: raise SystemExit("part %s: its value carries an unformatted placeholder %r and that string reaches the "
                            "silk, the schematic and the BOM: %r" % (ref, _m.group(0), value))
    _fp = FP.get(fp, fp); _nets = {str(k): v for k, v in nets.items()}
    check_land(ref, value, _fp, _nets)
    P.append(dict(ref=ref, lib=lib, sym=sym, value=value, fp=_fp, nets=_nets, lcsc=lcsc, in_bom=in_bom))

# ---------------------------------------------------------------- the pin map against the LAND (17 September 2026)
#
# `ic()` has refused an unlisted pin since 10 September, and every part that does not go through it was still trusted.
# Board E's Q7, the hot-swap pass FET on the shore and vehicle DC entry, is a CSD19532Q5B on a PowerPAK SO-8 land,
# whose pads are 1, 2, 3 SOURCE, 4 GATE and 5 DRAIN (the tab and the four right-hand pins all carry the number 5).
# It was written with the three-pin Q_NMOS_GDS map, so the gate net and the drain net landed on two SOURCE pins, the
# real gate and the whole drain tab carried nothing, and the assembled part would tie HS_GATE, HS_S and DC_HS
# together through its own source metal with no gate drive at all. Board A met the same trap on 7 September (32.36)
# and fixed its own helper; nothing stopped the next board repeating it.
#
# So the map is judged against the land itself: every distinct pad NUMBER the footprint carries on a copper layer
# must appear in the part's map, as a net or as the word NC, which is exactly what `ic()` asks for a listed pin.
_LANDS = {}
UNCHECKED = {}     # footprint id -> why it could not be read, printed and refused by the caller that runs where KiCad is


def _fp_dirs():
    # This project's own library sits beside the tools in the tree (v2/ecad/meshsat.pretty) and a generator runs
    # from the PROJECT directory beside it, which is what ${KIPRJMOD}/../meshsat.pretty means in fp-lib-table. A
    # staging copy of the tools (/root/localtools) has neither, so the cwd is asked as well.
    here = os.path.dirname(os.path.abspath(__file__))
    d = [os.path.join(here, "meshsat.pretty"), os.path.join(os.path.dirname(here), "meshsat.pretty"),
         os.path.join(os.getcwd(), "meshsat.pretty"),
         os.path.join(os.path.dirname(os.path.abspath(os.getcwd())), "meshsat.pretty")]
    for e in ("KICAD9_FOOTPRINT_DIR", "KICAD8_FOOTPRINT_DIR", "KISCH_FP_DIRS"):
        for part_ in filter(None, os.environ.get(e, "").split(os.pathsep)): d.append(part_)
    d += ["/usr/share/kicad/footprints", "/usr/local/share/kicad/footprints"]
    return d


def land_pads(fpid):
    """The distinct pad numbers a library footprint carries on a copper layer, or None when it cannot be read."""
    if not fpid: return None              # a power flag has no land and is not a part on the board
    if fpid in _LANDS: return _LANDS[fpid]
    ans = None
    if ":" in fpid:
        lib, name = fpid.split(":", 1)
        for d in _fp_dirs():
            cand = os.path.join(d, lib + ".pretty", name + ".kicad_mod") if os.path.basename(d) != lib + ".pretty" \
                else os.path.join(d, name + ".kicad_mod")
            if lib == "meshsat" and d.endswith("meshsat.pretty"): cand = os.path.join(d, name + ".kicad_mod")
            if not os.path.exists(cand): continue
            txt = open(cand, errors="replace").read()
            nums = set()
            for m in re.finditer(r'\(pad\s+"([^"]*)"\s+\S+\s+\S+(.*?)(?=\n\s*\(pad\s|\n\s*\)\s*$)', txt, re.S):
                num, body = m.group(1), m.group(2)
                if not num: continue                       # an unnumbered paste aperture is not a pin
                if not re.search(r'"(F|B|In\d+|\*)\.Cu"', body): continue
                nums.add(num)
            ans = nums or None
            break
    if ans is None: UNCHECKED[fpid] = "no library footprint found for %s" % fpid
    _LANDS[fpid] = ans
    return ans


PHANTOM = []   # (ref, value, fpid, pin, net) for a map pin the land does not carry; a warning, or a refusal below


def check_land(ref, value, fpid, nets):
    pads = land_pads(fpid)
    if pads is None: return
    # THE OTHER DIRECTION: a map pin the land does not carry lands nowhere. KiCad drops it silently, so the net
    # simply has one node fewer than the drawing says. That is harmless where the same net also sits on a pad this
    # land HAS (board E's TDSON-8 FETs name 5, 6, 7 and 8 for a drain the land merges into one pad 5, appendix
    # 32.219) and it is a REFUSAL where it does not, because then the net never reaches the part at all.
    ghost = sorted((k, v) for k, v in nets.items() if k not in pads)
    for k, v in ghost:
        if v == "NC": continue
        if not any(kk in pads for kk, vv in nets.items() if vv == v):
            raise SystemExit("%s (%s) on %s: pin %s carries %s and the land has no pad %s, so %s never reaches this "
                             "part. The land's pads are %s."
                             % (ref, value, fpid, k, v, k, v, ", ".join(sorted(pads))))
        PHANTOM.append((ref, value, fpid, k, v))
    missing = sorted(p for p in pads if p not in nets)
    if missing:
        raise SystemExit('%s (%s) on %s: its land carries pad%s %s and the map does not name %s. Every numbered '
                         'pad of the land takes a net or the word "NC" (17 September 2026: board E\'s Q7 put a gate '
                         'and a drain net on two SOURCE pins of a PowerPAK SO-8 and left the drain tab floating).'
                         % (ref, value, fpid, "" if len(missing) == 1 else "s", ", ".join(missing),
                            "it" if len(missing) == 1 else "them"))


def lands_report():
    """What could not be judged, for the caller that runs where the libraries are. Absence is never a pass."""
    return dict(checked=sum(1 for v in _LANDS.values() if v is not None), unchecked=dict(UNCHECKED),
                phantom=list(PHANTOM))


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
    _ANCHOR[0] = x
    place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x, y); net = p["nets"]["1"]; wire(x, y, x, y + STUB)
    if net in POWER:
        lib, nm2 = POWER[net]; place_symbol(lib, nm2, "#PWR%03d" % pf_n[0], net, "", x, y + STUB); pf_n[0] += 1
    else: label(net, x, y + STUB, 270)

def place_symbol(lib, name, ref, value, fp, x, y, lcsc="", hide_props=False, in_bom=True, rot=0, ref_at=None, val_at=None, hide_value=False, font=1.27):
    """rot is the symbol's orientation on the sheet (0, 90, 180, 270, counter-clockwise); ref_at and val_at place the two visible
    properties (sheet coordinates, left-justified text with its baseline at y), else they sit beside the top-right pin as before."""
    sym = ensure(lib, name); pins = pins_of(sym); x0, x1, y0, y1 = extents(sym)
    s = '(symbol (lib_id %s) (at %.2f %.2f %d) (unit 1) (exclude_from_sim no) (in_bom %s) (on_board %s) (dnp no)%s (uuid "%s")\n' % (
        q(lib + ":" + name), x, y, rot, "no" if lib == "power" or name in ("TestPoint",) or not in_bom else "yes", "no" if lib == "power" else "yes",
        "" if ref_at else " (fields_autoplaced yes)", U())
    def prop(k, v, px, py, hide): return '\t(property %s %s (at %.2f %.2f 0) (effects (font (size %.2f %.2f)) (justify left bottom)%s))\n' % (q(k), q(v), px, py, font, font, " (hide yes)" if hide else "")
    ra = ref_at or (x + x1 + 1.27, y - y1 - 1.27); va = val_at or (x + x1 + 1.27, y - y1 + 1.27)
    s += prop("Reference", ref, ra[0], ra[1], hide_props or lib == "power"); s += prop("Value", value, va[0], va[1], hide_props or hide_value)
    s += prop("Footprint", fp, x, y, True); s += prop("Datasheet", "", x, y, True); s += prop("Description", "", x, y, True)
    if lcsc: s += prop("LCSC", lcsc, x, y, True)
    for num, nm, px, py, rot in pins: s += '\t(pin %s (uuid "%s"))\n' % (q(num), U())
    s += '\t(instances (project %s (path "/%s" (reference %s) (unit 1))))\n)\n' % (q(PROJECT), ROOT, q(ref))
    out.append(s); return pins

def wire(x1, y1, x2, y2): out.append('(wire (pts (xy %.2f %.2f) (xy %.2f %.2f)) (stroke (width 0) (type default)) (uuid "%s"))\n' % (x1, y1, x2, y2, U()))

def label(net, x, y, rot):
    just = {0: "left bottom", 180: "right bottom", 90: "left bottom", 270: "right bottom"}[rot]
    out.append('(label %s (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s"))\n' % (q(net), x, y, rot, just, U()))

def glabel(net, x, y, rot):
    """A global label: the net keeps the global name a power symbol gives it (GND, +3V3), where an upright symbol has no room."""
    just = {0: "left", 180: "right", 90: "left", 270: "right"}[rot]
    out.append('(global_label %s (shape input) (at %.2f %.2f %d) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify %s)) (uuid "%s")\n\t(property "Intersheetrefs" "${INTERSHEET_REFS}" (at %.2f %.2f 0) (effects (font (size 1.27 1.27)) (hide yes)))\n)\n' % (q(net), x, y, rot, just, U(), x, y))


def text(t, x, y, size=2.0):
    _ANCHOR[0] = x + 16.0   # a section title sits 15 mm left of its column; the anchor is the column's
    return _text(t, x, y, size)


def _text(t, x, y, size=2.0, bold=True): out.append('(text %s (exclude_from_sim no) (at %.2f %.2f 0) (effects (font (size %.2f %.2f)%s) (justify left bottom)) (uuid "%s"))\n' % (q(t), x, y, size, size, " bold" if bold else "", U()))


def junction(x, y): out.append('(junction (at %.2f %.2f) (diameter 0) (color 0 0 0 0) (uuid "%s"))\n' % (x, y, U()))


def rect(x0, y0, x1, y1, width=0.25):
    """A graphic rectangle (a page frame); no electrical meaning."""
    out.append('(rectangle (start %.2f %.2f) (end %.2f %.2f) (stroke (width %.2f) (type default)) (fill (type none)) (uuid "%s"))\n' % (x0, y0, x1, y1, width, U()))

def emit_part(p, x, y):
    _ANCHOR[0] = x
    pins = place_symbol(p["lib"], p["sym"], p["ref"], p["value"], p["fp"], x, y, p["lcsc"], in_bom=p.get("in_bom", True)); seen = set()
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
