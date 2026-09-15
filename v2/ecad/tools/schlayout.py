#!/usr/bin/env python3
"""The schematic page engine: one A3 page per functional block, real wiring, no overlaps (MESHSAT-862, 15 September 2026).

Until today every board's schematic was one row of 92 mm columns, every part drawn as a numbered connector with a 5 mm stub
and a net label on each pin, passives stacked so their stubs read as one endless vertical line, and the ICs as single-column
Conn_01xNN symbols 250 mm tall. It was a netlist with pictures. The owner opened it and said so (15 September 2026, 16:40 CEST:
"one component connected to the next in straight endless lines, no engineer can read this"). This module replaces the layout
and changes NOTHING electrical: the parts, their pin-to-net maps and every net name are the generators' as before, and the
netlist is proved identical to the committed one on every net and node line after every regeneration.

What it draws, per SECTION of a generator (a titled list of references):

  * an IC (a part registered through `ic()`, drawn until now as a Conn_01xNN) becomes a BOX symbol of its own: its rails
    on the top edge, its grounds on the bottom edge, its signals on the left and right in pin order, every pin carrying its
    number and the name of the net it serves; no-connects on the right with the no-connect cross;
  * a two-pin passive (R, C, L, D, FB, F, LED, JP) is a SATELLITE of the pin it serves: a pull-up or pull-down stands at the
    end of that pin's lane with the rail above it (or the ground below), a series part sits inline on the lane with its far
    net labelled, a decoupling capacitor hangs from a rail bus in a row beside the part it bypasses (the intent's `bypass`
    declarations name the part; the rest join the first part in the block that carries the rail);
  * connectors, modules and other multi-pin parts keep their library symbols with a labelled lane per pin;
  * every net still carries a local label at every anchor pin, which is what keeps its name (`/NAME`) unchanged;
  * each block is packed into A3 landscape pages (420 x 297 mm cells of one user sheet: KiCad has no multi-page sheet
    without a hierarchy, and a hierarchy renames every net that lives on one sub-sheet), each page framed and titled, and
    `build_sch.sh` cuts the sheet along the cell grid into a multi-page A3 PDF.

Nothing is placed on top of anything else: every symbol body, every text and every wire is registered in a per-cell
occupancy list and a satellite that cannot find a free slot falls back to a plain label, never to an overlap. A wire may
cross a wire (which KiCad does not connect); a wire never crosses a body and a wire end never lands on another net's wire.
"""
import collections, math, os, re

import kisch

GRID = 1.27
CELL_W, CELL_H = 330 * GRID, 234 * GRID          # 419.1 x 297.18 mm: an A3 landscape cell whose corners sit on the 1.27 mm grid
MARGIN = 8 * GRID                                 # 10.16 mm inside the cell edge
TITLE_H = 12 * GRID                               # the title strip at the top of every page
MAX_COLS, MAX_ROWS = 7, 10                        # eeschema accepts a user page up to 3048 mm a side
PIN_LEN = 2 * GRID
LANE_MIN = 2 * GRID
PULL_LEN = 6 * GRID                               # a vertical pull item: 7.62 mm of body between its two pin tips
PULL_SLOT = 8 * GRID                              # x pitch between two pull items whose vertical spans overlap
DECAP_PITCH = 12 * GRID
FONT = 1.27
SAT_FONT = 0.9                                    # the reference and value of a passive, on one line
SAT_PREFIX = ("R", "C", "L", "D", "FB", "F", "LED", "JP", "TVS", "Z")   # a two-pin part with one of these prefixes is a satellite


def g(v): return round(v / GRID) * GRID


def text_w(s, size=FONT): return (0.95 * size + 0.3) * len(s)   # KiCad's stroke font at 1.27 mm advances about 1.5 mm a character


def text_h(size=FONT): return 1.35 * size


def short_value(v, compact=False):
    """What the drawing shows of a value: the part before its first parenthesis, colon or semicolon, at most 36 characters. The
    Value property keeps the whole string (it is the BOM comment) and is hidden when the short form differs. A compact form
    (a capacitor in a decoupling row, 15 mm from its neighbour) keeps the first two words: value and voltage."""
    v = str(v); cut = len(v)
    if compact:
        t = v.split(); v = " ".join(t[:2]) if len(" ".join(t[:2])) <= 10 else t[0]
    for sep in (" (", ": ", "; ", ", "):
        i = v.find(sep)
        if 0 < i < cut: cut = i
    s = v[:cut].strip()
    return s if len(s) <= 36 else s[:34].rstrip() + ".."


# ------------------------------------------------------------------ net classes
def base(net): return net[1:] if net.startswith("/") else net


def is_gnd(net):
    n = base(net)
    return n == "GND" or n.startswith("GND") or n.endswith("GND") or n in ("AGND", "PGND", "DGND", "CHASSIS")


_RAIL_RE = re.compile(r"^(\+|-\d|VBAT|VBUS|VIN|VSYS|VCC|VDD|AVDD|DVDD|PVDD|VREF|VLOGIC|PACK_P|CELL\+|CELL_F|VCORE|V\d+V)")
_RAIL_END = ("_VDD", "_VCC", "_VCCA", "_VCCL", "_VCCR", "_VCCP", "_HPVDD", "_AVDD", "VDDIO", "_VBAT", "_3V3", "_1V8", "_5V", "_VIN")


def is_rail(net, power, rails):
    n = base(net)
    if n == "NC" or is_gnd(n): return False
    return n in power or n in rails or bool(_RAIL_RE.match(n)) or n.endswith(_RAIL_END)


# ------------------------------------------------------------------ geometry registry
class Occ:
    """Rectangles that nothing else may touch, and wires with their nets (a wire end on another net's wire is a short)."""
    def __init__(self):
        self.rects = []; self.wires = []; self.anchors = []      # anchors: (x, y, net) of every label, a connection point

    def free(self, r, pad=0.0):
        x0, y0, x1, y1 = r
        for a0, b0, a1, b1 in self.rects:
            if x0 - pad < a1 and x1 + pad > a0 and y0 - pad < b1 and y1 + pad > b0: return False
        return True

    def add(self, r): self.rects.append(r)

    def seg_free(self, x0, y0, x1, y1, net):
        """An axis-parallel wire: no body in its way, no end on another net's wire, no other net's end on it."""
        return self.seg_why(x0, y0, x1, y1, net) is None

    def seg_why(self, x0, y0, x1, y1, net):
        lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
        for a0, b0, a1, b1 in self.rects:
            if lo_x < a1 and hi_x > a0 and lo_y < b1 and hi_y > b0: return "rect %s" % ((round(a0, 2), round(b0, 2), round(a1, 2), round(b1, 2)),)
        for (p0, q0, p1, q1, n) in self.wires:
            if n == net: continue
            for ex, ey in ((x0, y0), (x1, y1)):
                if min(p0, p1) - 1e-6 <= ex <= max(p0, p1) + 1e-6 and min(q0, q1) - 1e-6 <= ey <= max(q0, q1) + 1e-6: return "end on wire of %s %s" % (n, (p0, q0, p1, q1))
            for ex, ey in ((p0, q0), (p1, q1)):
                if lo_x - 1e-6 <= ex <= hi_x + 1e-6 and lo_y - 1e-6 <= ey <= hi_y + 1e-6: return "wire end of %s at %s" % (n, (ex, ey))
        for (ax, ay, n) in self.anchors:
            if n != net and lo_x - 1e-6 <= ax <= hi_x + 1e-6 and lo_y - 1e-6 <= ay <= hi_y + 1e-6: return "anchor of %s at %s" % (n, (ax, ay))
        return None

    def add_anchor(self, x, y, net): self.anchors.append((x, y, net))

    def add_seg(self, x0, y0, x1, y1, net): self.wires.append((x0, y0, x1, y1, net))


# ------------------------------------------------------------------ symbols
def sym_graphic_bbox(sym):
    """The bounding box of a symbol's drawn body and pin tips, in library coordinates (y up)."""
    xs, ys = [], []
    def walk(n):
        for e in n:
            if not (isinstance(e, list) and e): continue
            if e[0] == "symbol": walk(e); continue
            if e[0] in ("rectangle", "polyline", "circle", "arc", "pin", "text"):
                for f in e:
                    if isinstance(f, list) and f and f[0] in ("start", "end", "xy", "center", "at", "mid"):
                        xs.append(float(f[1])); ys.append(float(f[2]))
                    if isinstance(f, list) and f and f[0] == "pts":
                        for p in f[1:]:
                            if isinstance(p, list) and p and p[0] == "xy": xs.append(float(p[1])); ys.append(float(p[2]))
                if e[0] == "circle":
                    c = [f for f in e if isinstance(f, list) and f and f[0] == "center"][0]; r = float([f for f in e if isinstance(f, list) and f and f[0] == "radius"][0][1])
                    xs.extend([float(c[1]) - r, float(c[1]) + r]); ys.extend([float(c[2]) - r, float(c[2]) + r])
    walk(sym)
    if not xs: return -2.54, 2.54, -2.54, 2.54
    return min(xs), max(xs), min(ys), max(ys)


def box_symbol(lib, name, pins, power, rails):
    """A box symbol for an IC: pins as (num, net, pin_name). Rails top, grounds bottom, signals left and right in pin order,
    no-connects at the bottom of the right side. Library coordinates, y up, everything on the 1.27 mm grid."""
    def key(p):
        m = re.match(r"(\d+)", p[0]); return (int(m.group(1)) if m else 10 ** 6, p[0])
    top = sorted([p for p in pins if is_rail(p[1], power, rails)], key=key)
    bot = sorted([p for p in pins if is_gnd(p[1])], key=key)
    nc = sorted([p for p in pins if p[1] == "NC"], key=key)
    sig = sorted([p for p in pins if p not in top and p not in bot and p not in nc], key=key)
    half = (len(sig) + 1) // 2
    left, right = sig[:half], sig[half:] + nc
    def lab(p): return p[2] if p[2] else base(p[1])
    wl = max([text_w(lab(p)) for p in left] + [0.0]); wr = max([text_w(lab(p)) for p in right] + [0.0])
    W = max(12 * GRID, g(wl + wr + 8 * GRID), (max(len(top), len(bot)) + 1) * 2 * GRID)
    H = max(4 * GRID, (max(len(left), len(right)) + 2) * 2 * GRID)
    fx = lambda: ["effects", ["font", ["size", "1.27", "1.27"]]]
    sym = ["symbol", kisch.q(lib + ":" + name), ["pin_names", ["offset", "1.016"]], ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
           ["property", kisch.q("Reference"), kisch.q("U"), ["at", "0", "%.2f" % (H / 2 + 1.27), "0"], fx()],
           ["property", kisch.q("Value"), kisch.q(name), ["at", "0", "%.2f" % (-H / 2 - 1.27), "0"], fx()],
           ["property", kisch.q("Footprint"), kisch.q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]],
           ["property", kisch.q("Datasheet"), kisch.q(""), ["at", "0", "0", "0"], ["effects", ["font", ["size", "1.27", "1.27"]], ["hide", "yes"]]]]
    body = ["symbol", kisch.q(name + "_0_1"), ["rectangle", ["start", "%.2f" % (-W / 2), "%.2f" % (H / 2)], ["end", "%.2f" % (W / 2), "%.2f" % (-H / 2)],
            ["stroke", ["width", "0.254"], ["type", "default"]], ["fill", ["type", "background"]]]]
    unit = ["symbol", kisch.q(name + "_1_1")]
    def pin(num, nm, x, y, rot, typ="passive"):
        unit.append(["pin", typ, "line", ["at", "%.2f" % x, "%.2f" % y, str(rot)], ["length", "%.2f" % PIN_LEN], ["name", kisch.q(nm), fx()], ["number", kisch.q(num), fx()]])
    for i, p in enumerate(left): pin(p[0], lab(p), -W / 2 - PIN_LEN, H / 2 - 2 * GRID * (i + 1), 0)
    for i, p in enumerate(right): pin(p[0], lab(p), W / 2 + PIN_LEN, H / 2 - 2 * GRID * (i + 1), 180)
    def spread(n):
        return [g(-W / 2 + (W / (n + 1)) * (i + 1)) for i in range(n)]
    for p, x in zip(top, spread(len(top))): pin(p[0], lab(p), x, H / 2 + PIN_LEN, 270)
    for p, x in zip(bot, spread(len(bot))): pin(p[0], lab(p), x, -H / 2 - PIN_LEN, 90)
    sym.append(body); sym.append(unit); return sym


# ------------------------------------------------------------------ the engine
class Engine:
    def __init__(self, parts, sections, power, bypass, header, phase, board_title):
        self.P = parts; self.byref = {p["ref"]: p for p in parts}; self.sections = sections; self.power = power
        self.rails = set(); self.bypass = {b["cap"]: (b["part"], b["pin"]) for b in bypass}
        self.header = header; self.phase = phase; self.board_title = board_title
        self.pages = []          # list of dicts: title, section, items (emission closures with local coordinates)
        self.pf = [0]; self.oversize = []; self.all_ems = []; self.state = dict(page=None, cx=0.0, cy=0.0, row_h=0.0)

    # ---- classification
    def npins(self, p): return len(set((round(px, 2), round(py, 2)) for _, _, px, py, _ in kisch.pins_of(self.symbol(p))))

    def symbol(self, p):
        if p.get("_boxsym"): return kisch.libsyms[p["_boxsym"]]
        return kisch.ensure(p["lib"], p["sym"])

    def is_sat(self, p):
        return p["ref"].rstrip("0123456789") in SAT_PREFIX and self.npins(p) == 2 and p["sym"] != "PWR_FLAG"

    def is_ic_box(self, p):
        return p["sym"].startswith("Conn_01x") and p["ref"][:1] in ("U", "Q") and self.npins(p) >= 3   # an IC or a power FET registered through ic()

    def prepare(self):
        for p in self.P:
            for net in p["nets"].values():
                if is_rail(net, self.power, ()): self.rails.add(base(net))
        for p in self.P:
            if self.is_ic_box(p):
                key = "meshsat_ic:" + p["ref"]
                pins = [(num, net, "") for num, net in sorted(p["nets"].items(), key=lambda kv: (int(re.match(r"\d+", kv[0]).group()) if re.match(r"\d+", kv[0]) else 10 ** 6, kv[0]))]
                kisch.libsyms[key] = box_symbol("meshsat_ic", p["ref"], pins, self.power, self.rails); p["_boxsym"] = key
            elif p["sym"] in kisch.SYNTH:
                p["_boxsym"] = None

    # ---- emission helpers (local coordinates inside a cell; shifted at page assembly)
    def run(self):
        self.prepare()
        placed = set()
        for title, refs in self.sections:
            cells = self.section_cells(title, refs); placed.update(refs)
            self.pack(title, cells)
        missing = [p["ref"] for p in self.P if p["ref"] not in placed]
        if missing: raise SystemExit("schlayout: unplaced parts: %s" % missing)
        return self.emit()

    def section_cells(self, title, refs):
        parts = [self.byref[r] for r in refs]
        sats = [p for p in parts if self.is_sat(p)]
        anchors = [p for p in parts if not self.is_sat(p) and self.npins(p) >= 2 and p["sym"] != "PWR_FLAG"]
        tiny = [p for p in parts if p not in sats and p not in anchors]
        # net -> [(part, pin)] inside this block, anchors only
        apins = {}
        for a in anchors:
            for num, net in a["nets"].items():
                if net != "NC": apins.setdefault(net, []).append((a["ref"], num))
        attach = {a["ref"]: {} for a in anchors}     # ref -> pin -> [satellite plans]
        decaps = {a["ref"]: {} for a in anchors}     # ref -> rail -> [caps]
        loose = []
        far_of = {}                                  # net -> (anchor ref, pin) where a lane already ends on that net (chains)
        pending = list(sats)
        for _round in range(4):
            left = []
            for s in pending:
                (pa, na), (pb, nb) = sorted(s["nets"].items())[:2]
                ra, rb = is_rail(na, self.power, self.rails) or is_gnd(na), is_rail(nb, self.power, self.rails) or is_gnd(nb)
                if ra and rb:
                    rail = na if not is_gnd(na) else nb
                    host = None
                    if s["ref"] in self.bypass and self.bypass[s["ref"]][0] in attach: host = self.bypass[s["ref"]][0]
                    else:
                        for a in anchors:
                            if rail in a["nets"].values(): host = a["ref"]; break
                    if host is None: loose.append(s); continue
                    decaps[host].setdefault(rail, []).append(s); continue
                cands = []
                for (pin, net, other_pin, other_net, other_is_rail) in ((pa, na, pb, nb, rb), (pb, nb, pa, na, ra)):
                    if net in apins and not (is_rail(net, self.power, self.rails) or is_gnd(net)):
                        cands.append((len(apins[net]), apins[net][0], pin, other_pin, other_net, other_is_rail))
                    elif net in far_of:
                        cands.append((100, far_of[net], pin, other_pin, other_net, other_is_rail))
                if not cands: left.append(s); continue
                cands.sort(key=lambda c: c[0]); _, (aref, apin), pin, opin, onet, o_rail = cands[0]
                kind = "pull" if o_rail else "series"
                attach[aref].setdefault(apin, []).append(dict(part=s, near_pin=pin, far_pin=opin, far_net=onet, kind=kind))
                if kind == "series" and onet not in apins: far_of[onet] = (aref, apin)
            pending = left
            if not pending: break
        loose += pending
        cells = []
        for a in anchors:
            self.extra_cells = []
            cells.append(self.anchor_cell(a, attach[a["ref"]], decaps[a["ref"]])); cells.extend(self.extra_cells)
        for s in loose: cells.append(self.loose_cell(s))
        for t in tiny: cells.append(self.tiny_cell(t))
        return cells

    # ---- symbol placement in local coordinates
    def sym_pins(self, p, x, y, rot=0):
        """Sheet positions of a symbol's pins for a symbol at (x, y) with rotation rot (0, 90, 180, 270): (num, name, sx, sy, outward dx, dy)."""
        res = []
        for num, nm, px, py, prot in kisch.pins_of(self.symbol(p)):
            sx, sy = self.xform(px, py, rot); dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[prot]
            dx, dy = self.rot_dir(dx, dy, rot)
            res.append((num, nm, x + sx, y + sy, dx, dy))
        return res

    @staticmethod
    def xform(px, py, rot):
        # KiCad: library y is up, the sheet y is down; rotation counter-clockwise on the sheet
        if rot == 0: return px, -py
        if rot == 90: return -py, -px
        if rot == 180: return -px, py
        return py, px

    @staticmethod
    def rot_dir(dx, dy, rot):
        for _ in range(rot // 90): dx, dy = dy, -dx
        return dx, dy

    def orient(self, p, horizontal):
        """The rotation that puts a two-pin part's pins side by side (horizontal) or one above the other; a diode's library
        symbol lies flat, a resistor's stands, so this is read off the pins rather than assumed."""
        for rot in (0, 90):
            pins = self.sym_pins(p, 0.0, 0.0, rot)
            if len(pins) < 2: return rot
            same_y = abs(pins[0][3] - pins[1][3]) < 0.01
            if same_y == horizontal: return rot
        return 0

    def body_rect(self, p, x, y, rot=0):
        x0, x1, y0, y1 = sym_graphic_bbox(self.symbol(p))
        pts = [self.xform(px, py, rot) for px in (x0, x1) for py in (y0, y1)]
        xs = [x + a for a, _ in pts]; ys = [y + b for _, b in pts]
        return (min(xs), min(ys), max(xs), max(ys))

    # ---- cells
    def anchor_cell(self, a, attach, decaps):
        """Lay the anchor at the local origin, its lanes and satellites around it; return a cell dict with its bbox and emitters."""
        occ = Occ(); ems = []
        rot = 0
        pins = self.sym_pins(a, 0.0, 0.0, rot)
        body = self.body_rect(a, 0.0, 0.0, rot); occ.add(body)
        bx0, by0, bx1, by1 = body
        boxed = bool(a.get("_boxsym")) or a["sym"] in kisch.SYNTH
        # reference and value texts
        # beside the top-right corner: above every right-hand lane, right of every top pin's label (measured 15 Sep 2026: a value
        # under the body crossed a bottom pin's stub, one beside a small part sat on its right-hand pin's lane)
        ref_at = (bx1 + GRID, by0 - GRID - text_h() - 0.3); val_at = (bx1 + GRID, by0 - GRID)
        sv = short_value(a["value"])
        for (tx, ty), s in ((ref_at, a["ref"]), (val_at, sv)):
            occ.add((tx, ty - text_h(), tx + text_w(s), ty))
        ems.append(("symbol", a, 0.0, 0.0, rot, ref_at, val_at, sv != a["value"]))
        if sv != a["value"]: ems.append(("text", sv, val_at[0], val_at[1], FONT))
        seen = set()
        groups = {}   # (side, net) -> list of pin tips, for bussing rails on the top and bottom edges
        later = []    # lanes whose satellites are placed once every label of the part stands
        for num, nm, sx, sy, dx, dy in pins:
            key = (round(sx, 2), round(sy, 2))
            if key in seen: continue
            seen.add(key); net = a["nets"].get(num)
            if net is None: raise SystemExit("%s pin %s (%s) has no net assignment" % (a["ref"], num, nm))
            if net == "NC": ems.append(("noconn", sx, sy)); continue
            sats = attach.get(num, [])
            if (dy != 0) and (is_rail(net, self.power, self.rails) or is_gnd(net)) and not sats:
                groups.setdefault((dy, net), []).append((sx, sy)); continue
            r = self.lane(occ, ems, net, sx, sy, dx, dy, sats, place_sats=False)
            if r: later.append(r)
        for (net, cx, cy, dx, dy, sats) in later: self.lane_sats(occ, ems, net, cx, cy, dx, dy, sats)
        spans = {k: (min(t[0] for t in v), max(t[0] for t in v)) for k, v in groups.items()}
        for (dy, net), tips in groups.items():
            lo, hi = spans[(dy, net)]
            clash = any(k != (dy, net) and k[0] == dy and not (spans[k][1] < lo or spans[k][0] > hi) for k in spans)
            if clash:                                  # two rails' pins interleave along one edge: a bus each would cross
                for sx, sy in tips: self.lane(occ, ems, net, sx, sy, 0, dy, [])
            else: self.rail_bus(occ, ems, net, tips, dy)
        # decoupling rows to the right of everything so far
        cell_w = max(r[2] for r in occ.rects) - min(r[0] for r in occ.rects)
        if decaps and ((by1 - by0) > 100.0 or cell_w > 220.0):   # too tall or too wide to carry its rows
            self.extra_cells.append(self.decap_cell(a, decaps)); decaps = {}
        if decaps:
            x0 = g(max(r[2] for r in occ.rects) + 6 * GRID); x = x0; y = g(by0); row_bottom = y
            for rail, caps in decaps.items():
                for chunk in [caps[i:i + 12] for i in range(0, len(caps), 12)]:
                    w = DECAP_PITCH * len(chunk) + 4 * GRID
                    if x > x0 and x + w > x0 + 180.0: x = x0; y = g(row_bottom + 4 * GRID)
                    row_bottom = max(row_bottom, self.decap_row(occ, ems, rail, chunk, x, y)); x = g(x + w)
        c = self.finish_cell(occ, ems); c["ref"] = a["ref"]
        if os.environ.get("SCHLAYOUT_DEBUG"): print("cell %-8s %5.0f x %5.0f mm  sats %d  decap rails %d" % (a["ref"], c["x1"] - c["x0"], c["y1"] - c["y0"], sum(len(v) for v in attach.values()), len(decaps)))
        return c

    def decap_cell(self, a, decaps):
        """The decoupling of a part too tall to carry it beside itself: rows under a heading naming the part."""
        occ = Occ(); ems = []
        t = "decoupling of %s" % a["ref"]; ems.append(("text", t, 0.0, 0.0, FONT)); occ.add((0.0, -text_h(), text_w(t), 0.0))
        x0 = 0.0; x = x0; y = 4 * GRID; row_bottom = y
        for rail, caps in decaps.items():
            for chunk in [caps[i:i + 12] for i in range(0, len(caps), 12)]:
                w = DECAP_PITCH * len(chunk) + 4 * GRID
                if x > x0 and x + w > x0 + 180.0: x = x0; y = g(row_bottom + 4 * GRID)
                row_bottom = max(row_bottom, self.decap_row(occ, ems, rail, chunk, x, y)); x = g(x + w)
        c = self.finish_cell(occ, ems); c["ref"] = a["ref"] + "-decoupling"; return c

    def lane(self, occ, ems, net, sx, sy, dx, dy, sats, place_sats=True):
        """A pin's lane: a stub with the net label, then its satellites outward; falls back to a bare label when a satellite has no
        room. With place_sats False the satellites are returned for a later pass, so every label of the part stands first."""
        need = g(max(LANE_MIN, text_w(base(net)) + GRID)) if sats else LANE_MIN   # with satellites the label rides ON the stub, ahead of them
        lab_len = need
        while lab_len > LANE_MIN and not occ.seg_free(sx, sy, sx + dx * lab_len, sy + dy * lab_len, net): lab_len -= 2 * GRID
        if lab_len < need and sats and os.environ.get("SCHLAYOUT_DEBUG"):
            print("stub of %s shortened %.2f -> %.2f: %s" % (net, need, lab_len, occ.seg_why(sx, sy, sx + dx * need, sy + dy * need, net)))
        if lab_len < need:                       # no room for the label's own stub: the satellites are drawn on their own
            for s in sats: self.orphan_label(occ, ems, s)
            sats = []
        ex, ey = sx + dx * lab_len, sy + dy * lab_len
        ems.append(("wire", sx, sy, ex, ey)); occ.add_seg(sx, sy, ex, ey, net)
        pw = self.power.get(base(net)) if (is_rail(net, self.power, self.rails) or is_gnd(net)) and base(net) in self.power else None
        if pw and not sats and dy != 0:
            ems.append(("power", pw, ex, ey, 0 if dy < 0 else 180)); occ.add(self.power_rect(ex, ey, dx, dy)); return
        if pw and not sats:                       # a power net on a side pin: a global label keeps the symbol upright elsewhere and the net global
            ems.append(("glabel", base(net), ex, ey, 0 if dx > 0 else 180)); occ.add_anchor(ex, ey, base(net)); occ.add(self.label_rect(net, ex, ey, dx, dy, 3.0)); return
        lrot = {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)]
        lx, ly = (sx + dx * GRID, sy + dy * GRID) if sats else (ex, ey)
        ems.append(("label", net, lx, ly, lrot)); occ.add_anchor(lx, ly, net); occ.add(self.label_rect(net, lx, ly, dx, dy))
        if not sats: return None
        if not place_sats: return (net, ex, ey, dx, dy, sats)
        self.lane_sats(occ, ems, net, ex, ey, dx, dy, sats)

    def lane_sats(self, occ, ems, net, ex, ey, dx, dy, sats):
        cx, cy = ex, ey; broken = False
        for s in sats:
            if broken or s["part"]["nets"][s["near_pin"]] != net:          # the lane's net is not the one this part's near pin carries
                self.orphan_label(occ, ems, s); continue
            if dy != 0:                            # a satellite on a vertical pin: hang it straight on
                r = self.series_item(occ, ems, s, cx, cy, dx, dy, net)
                if r is None: broken = True; self.orphan_label(occ, ems, s); continue
                cx, cy = r; net = s["far_net"]; continue
            if s["kind"] == "series":
                r = self.series_item(occ, ems, s, cx, cy, dx, dy, net)
                if r is None: broken = True; self.orphan_label(occ, ems, s); continue
                cx, cy = r; net = s["far_net"]
            else:
                r = self.pull_item(occ, ems, s, cx, cy, dx, net)
                if r is None: self.orphan_label(occ, ems, s); continue
                cx, cy = r

    def series_item(self, occ, ems, s, cx, cy, dx, dy, net):
        """A two-pin part inline on the lane: wire on, body, wire off, the far net's label (or power symbol) at the end."""
        p = s["part"]; rot = self.orient(p, dy == 0)
        pins = self.sym_pins(p, 0.0, 0.0, rot); near = [q for q in pins if q[0] == s["near_pin"]][0]; far = [q for q in pins if q[0] == s["far_pin"]][0]
        # orient so the near pin faces the lane's incoming direction
        if (near[4], near[5]) != (-dx, -dy):
            rot = (rot + 180) % 360; pins = self.sym_pins(p, 0.0, 0.0, rot); near = [q for q in pins if q[0] == s["near_pin"]][0]; far = [q for q in pins if q[0] == s["far_pin"]][0]
        gap = 2 * GRID
        ox, oy = g(cx + dx * gap - near[2]), g(cy + dy * gap - near[3])
        body = self.body_rect(p, ox, oy, rot)
        ref_at, val_at, rects = self.sat_texts(p, body, dy == 0); rects = [body] + rects; sfont = SAT_FONT if dy == 0 else FONT
        nx, ny = ox + near[2], oy + near[3]; fx, fy = ox + far[2], oy + far[3]
        far_net = s["far_net"]
        lab_len = g(max(LANE_MIN, text_w(base(far_net)) + GRID)) if dy == 0 else LANE_MIN
        ex, ey = fx + dx * lab_len, fy + dy * lab_len
        if not all(occ.free(r) for r in rects) or not occ.seg_free(cx, cy, nx, ny, net) or not occ.seg_free(fx, fy, ex, ey, far_net):
            if os.environ.get("SCHLAYOUT_DEBUG"):
                why = ["rect %d %s" % (i, tuple(round(v, 2) for v in r)) for i, r in enumerate(rects) if not occ.free(r)]
                if not occ.seg_free(cx, cy, nx, ny, net):
                    why.append("lane seg (%.2f,%.2f)-(%.2f,%.2f) net %s" % (cx, cy, nx, ny, net))
                    why.append("wires near: %s" % [w for w in occ.wires if w[4] != net and min(w[0], w[2]) - 0.01 <= max(cx, nx) and max(w[0], w[2]) + 0.01 >= min(cx, nx) and min(w[1], w[3]) - 0.01 <= cy <= max(w[1], w[3]) + 0.01][:4])
                if not occ.seg_free(fx, fy, ex, ey, far_net): why.append("far seg (%.2f,%.2f)-(%.2f,%.2f)" % (fx, fy, ex, ey))
                hit = [tuple(round(v, 2) for v in q) for q in occ.rects if any(not (r[0] >= q[2] or r[2] <= q[0] or r[1] >= q[3] or r[3] <= q[1]) for r in rects)][:3]
                print("series %s refused: %s hits %s" % (p["ref"], why, hit))
            return None
        for r in rects: occ.add(r)
        ems.append(("wire", cx, cy, nx, ny)); occ.add_seg(cx, cy, nx, ny, net)
        ems.append(("symbol", p, ox, oy, rot, ref_at, val_at, False, sfont))
        ems.append(("wire", fx, fy, ex, ey)); occ.add_seg(fx, fy, ex, ey, far_net)
        pw = self.power.get(base(far_net)) if base(far_net) in self.power else None
        if pw and dy != 0: ems.append(("power", pw, ex, ey, 0 if dy < 0 else 180)); occ.add(self.power_rect(ex, ey, dx, dy))
        elif pw: ems.append(("glabel", base(far_net), ex, ey, 0 if dx > 0 else 180)); occ.add_anchor(ex, ey, base(far_net)); occ.add(self.label_rect(far_net, ex, ey, dx, dy, 3.0))
        else:
            lrot = {(-1, 0): 180, (1, 0): 0, (0, 1): 270, (0, -1): 90}[(dx, dy)]
            ems.append(("label", far_net, ex, ey, lrot)); occ.add_anchor(ex, ey, far_net); occ.add(self.label_rect(far_net, ex, ey, dx, dy))
        return ex, ey

    def pull_item(self, occ, ems, s, cx, cy, dx, net):
        """A pull-up or pull-down standing at the lane's end: the lane extends to a free slot, the part stands vertically, the rail
        (up) or ground (down) beyond it."""
        p = s["part"]; up = not is_gnd(s["far_net"]); vdir = -1 if up else 1
        for k in range(0, 10):                                   # ten slots, 100 mm of lane at most; beyond that the part is drawn on its own
            x = g(cx + dx * (2 * GRID + k * PULL_SLOT))
            rot = self.orient(p, False)
            pins = self.sym_pins(p, 0.0, 0.0, rot); near = [q for q in pins if q[0] == s["near_pin"]][0]; far = [q for q in pins if q[0] == s["far_pin"]][0]
            if (near[5] < far[5]) != (not up):   # the near pin faces the lane: it is the TOP pin of a pull-down and the BOTTOM pin of a pull-up
                rot = (rot + 180) % 360; pins = self.sym_pins(p, 0.0, 0.0, rot); near = [q for q in pins if q[0] == s["near_pin"]][0]; far = [q for q in pins if q[0] == s["far_pin"]][0]
            # the vertical run: from the lane up/down to the near pin, past any lane in the way
            for lift in range(0, 12):
                y_near = g(cy + vdir * (2 * GRID + lift * 2 * GRID))
                ox, oy = g(x - near[2]), g(y_near - near[3]); body = self.body_rect(p, ox, oy, rot)
                ref_at, val_at, rects = self.sat_texts(p, body, False); rects = [body] + rects
                fx, fy = ox + far[2], oy + far[3]; ex, ey = fx, fy + vdir * 2 * GRID
                far_net = s["far_net"]; pw = self.power.get(base(far_net)) if base(far_net) in self.power else None
                endr = self.power_rect(ex, ey, 0, vdir) if pw else self.label_rect(far_net, ex, ey, 0, vdir)
                ok = all(occ.free(r) for r in rects) and occ.free(endr) and occ.seg_free(cx, cy, x, cy, net) and occ.seg_free(x, cy, x, y_near, net) and occ.seg_free(fx, fy, ex, ey, far_net)
                if not ok: continue
                for r in rects: occ.add(r)
                occ.add(endr)
                if x != cx: ems.append(("wire", cx, cy, x, cy)); occ.add_seg(cx, cy, x, cy, net)
                ems.append(("wire", x, cy, x, y_near)); occ.add_seg(x, cy, x, y_near, net)
                ems.append(("symbol", p, ox, oy, rot, ref_at, val_at))
                ems.append(("wire", fx, fy, ex, ey)); occ.add_seg(fx, fy, ex, ey, far_net)
                if pw: ems.append(("power", pw, ex, ey, 0 if up else 180))
                else: ems.append(("label", far_net, ex, ey, 90 if up else 270)); occ.add_anchor(ex, ey, far_net)
                return x, cy
        return None

    def sat_texts(self, p, body, horizontal, stacked=False):
        """Reference and value of a satellite, in the small font: on one line above a horizontal part, to the right of a
        vertical one (stacked on two lines beside a decoupling capacitor, whose neighbours are 10 mm away)."""
        f = SAT_FONT if horizontal else FONT; h = text_h(f); wr = text_w(p["ref"], f); wv = text_w(short_value(p["value"], not horizontal), f)
        if horizontal:
            x0 = (body[0] + body[2]) / 2 - (wr + 1.0 + wv) / 2
            ref_at = (x0, body[1] - 0.15); val_at = (x0 + wr + 1.0, body[1] - 0.15)
            rects = [(ref_at[0], ref_at[1] - h, ref_at[0] + wr, ref_at[1]), (val_at[0], val_at[1] - h, val_at[0] + wv, val_at[1])]
        elif stacked:
            ref_at = (body[2] + 0.4, body[1] + h); val_at = (body[2] + 0.4, body[1] + 2 * h + 0.3)
            rects = [(ref_at[0], ref_at[1] - h, ref_at[0] + wr, ref_at[1]), (val_at[0], val_at[1] - h, val_at[0] + wv, val_at[1])]
        else:
            ref_at = (body[2] + 0.4, (body[1] + body[3]) / 2 + h / 2); val_at = (body[2] + 0.4 + wr + 1.0, ref_at[1])
            rects = [(ref_at[0], ref_at[1] - h, ref_at[0] + wr, ref_at[1]), (val_at[0], val_at[1] - h, val_at[0] + wv, val_at[1])]
        return ref_at, val_at, rects

    def orphan_label(self, occ, ems, s):
        """No room beside its pin: the satellite is drawn on its own with two labels, in rows under the cell (never on top of something)."""
        p = s["part"]
        if not hasattr(occ, "orphan_row"): occ.orphan_row = None
        n1, n2 = [base(v) for v in list(p["nets"].values())[:2]]
        tw1, tw2 = text_w(n1), text_w(n2)
        w = g(max(24 * GRID, tw1 + tw2 + 20 * GRID, text_w(short_value(p["value"])) + 16 * GRID))
        if occ.orphan_row is None or occ.orphan_row[0] + w > 200.0:
            y = g(max([r[3] for r in occ.rects] + [0]) + 8 * GRID); occ.orphan_row = [g(min(r[0] for r in occ.rects)) if occ.rects else 0.0, y]
        x, y = occ.orphan_row
        for _ in range(6):
            r = (x - 2 * GRID, y - 6 * GRID, x + w - 2 * GRID, y + 6 * GRID)
            if occ.free(r): break
            if os.environ.get("SCHLAYOUT_DEBUG"): print("orphan %s at (%.1f, %.1f) w %.1f blocked by %s" % (p["ref"], x, y, w, [tuple(round(v, 1) for v in q) for q in occ.rects if not (r[0] >= q[2] or r[2] <= q[0] or r[1] >= q[3] or r[3] <= q[1])][:3]))
            y = g(y + 10 * GRID); occ.orphan_row[1] = y
        self.loose_layout(p, occ, ems, g(x + tw1 + 8 * GRID), y); occ.orphan_row[0] = g(x + w)

    def rail_bus(self, occ, ems, net, tips, dy):
        """Consecutive rail pins on the top (or ground pins on the bottom) share one bus wire and one symbol."""
        tips = sorted(tips); xs = [t[0] for t in tips]; y = tips[0][1]; ey = y + dy * 2 * GRID
        for x, _ in tips: ems.append(("wire", x, y, x, ey)); occ.add_seg(x, y, x, ey, net)
        if len(tips) > 1: ems.append(("wire", xs[0], ey, xs[-1], ey)); occ.add_seg(xs[0], ey, xs[-1], ey, net)
        mx = g(sum(xs) / len(xs)) if len(tips) > 1 else xs[0]
        if len(tips) > 1 and mx not in xs:
            pass  # the symbol stands on the bus wire itself
        pw = self.power.get(base(net)) if base(net) in self.power else None
        top = ey + dy * (2 * GRID if len(tips) > 1 else 0)
        if len(tips) > 1: ems.append(("wire", mx, ey, mx, top)); occ.add_seg(mx, ey, mx, top, net)
        if pw: ems.append(("power", pw, mx, top, 0 if dy < 0 else 180)); occ.add(self.power_rect(mx, top, 0, dy))
        else: ems.append(("label", net, mx, top, 90 if dy < 0 else 270)); occ.add_anchor(mx, top, net); occ.add(self.label_rect(net, mx, top, 0, dy))

    def decap_row(self, occ, ems, rail, caps, x0, y0):
        """A row of decoupling capacitors between a rail bus (above, with its symbol) and ground symbols (below)."""
        n = len(caps); y_bus = y0 + 4 * GRID
        x1 = x0 + DECAP_PITCH * (n - 1)
        ems.append(("wire", x0, y_bus, x1 + 2 * GRID, y_bus)); occ.add_seg(x0, y_bus, x1 + 2 * GRID, y_bus, rail)
        ems.append(("wire", x0, y_bus, x0, y_bus - 2 * GRID)); occ.add_seg(x0, y_bus, x0, y_bus - 2 * GRID, rail)
        pw = self.power.get(base(rail)) if base(rail) in self.power else None
        if pw: ems.append(("power", pw, x0, y_bus - 2 * GRID, 0)); occ.add(self.power_rect(x0, y_bus - 2 * GRID, 0, -1))
        else: ems.append(("label", rail, x0, y_bus - 2 * GRID, 90)); occ.add_anchor(x0, y_bus - 2 * GRID, rail); occ.add(self.label_rect(rail, x0, y_bus - 2 * GRID, 0, -1))
        ybot = y_bus
        for i, c in enumerate(caps):
            x = x0 + DECAP_PITCH * i
            (pa, na), (pb, nb) = sorted(c["nets"].items())[:2]
            top_pin = pa if base(na) == base(rail) else pb; bot_pin = pb if top_pin == pa else pa; bot_net = nb if top_pin == pa else na
            rot = self.orient(c, False); pins = self.sym_pins(c, 0.0, 0.0, rot); tp = [q for q in pins if q[0] == top_pin][0]
            if tp[5] > 0: rot = (rot + 180) % 360; pins = self.sym_pins(c, 0.0, 0.0, rot); tp = [q for q in pins if q[0] == top_pin][0]
            bp = [q for q in pins if q[0] == bot_pin][0]
            ox, oy = g(x - tp[2]), g(y_bus + 2 * GRID - tp[3]); body = self.body_rect(c, ox, oy, rot)
            ref_at, val_at, rects = self.sat_texts(c, body, False, stacked=True); occ.add(body)
            for r in rects: occ.add(r)
            ems.append(("wire", x, y_bus, ox + tp[2], oy + tp[3])); occ.add_seg(x, y_bus, ox + tp[2], oy + tp[3], rail)
            ems.append(("symbol", c, ox, oy, rot, ref_at, val_at, False, FONT, True))
            bx, by = ox + bp[2], oy + bp[3]; ey = by + 2 * GRID
            ems.append(("wire", bx, by, bx, ey)); occ.add_seg(bx, by, bx, ey, bot_net)
            pwg = self.power.get(base(bot_net)) if base(bot_net) in self.power else None
            if pwg: ems.append(("power", pwg, bx, ey, 180)); occ.add(self.power_rect(bx, ey, 0, 1))
            else: ems.append(("label", bot_net, bx, ey, 270)); occ.add_anchor(bx, ey, bot_net); occ.add(self.label_rect(bot_net, bx, ey, 0, 1))
            ybot = max(ybot, ey + 4 * GRID)
        return ybot

    def loose_cell(self, s):
        occ = Occ(); ems = []; self.loose_layout(s, occ, ems, 0.0, 0.0); c = self.finish_cell(occ, ems)
        c["x0"] -= 2 * GRID; c["x1"] += 2 * GRID; return c

    def loose_layout(self, p, occ, ems, x, y):
        """A two-pin part on its own: horizontal, a labelled stub at each end."""
        rot = self.orient(p, True); pins = self.sym_pins(p, x, y, rot); body = self.body_rect(p, x, y, rot)
        sv = short_value(p["value"]); wv = text_w(sv); cx = (body[0] + body[2]) / 2
        ref_at = (cx - text_w(p["ref"]) / 2, body[1] - GRID); val_at = (cx - wv / 2, body[3] + GRID + text_h())
        occ.add(body); occ.add((ref_at[0], ref_at[1] - text_h(), ref_at[0] + text_w(p["ref"]), ref_at[1])); occ.add((val_at[0], val_at[1] - text_h(), val_at[0] + wv, val_at[1]))
        ems.append(("symbol", p, x, y, rot, ref_at, val_at)); seen = set()
        for num, nm, sx, sy, dx, dy in pins:
            key = (round(sx, 2), round(sy, 2))
            if key in seen: continue
            seen.add(key); net = p["nets"].get(num)
            if net == "NC": ems.append(("noconn", sx, sy)); continue
            self.lane(occ, ems, net, sx, sy, dx, dy, [])

    def tiny_cell(self, p):
        occ = Occ(); ems = []
        if p["sym"] == "PWR_FLAG":
            net = p["nets"]["1"]; ems.append(("flag", p, 0.0, 0.0)); occ.add((-2 * GRID, -6 * GRID, 2 * GRID, 0.0))
            ems.append(("wire", 0.0, 0.0, 0.0, 2 * GRID)); occ.add_seg(0.0, 0.0, 0.0, 2 * GRID, net)
            pw = self.power.get(base(net)) if base(net) in self.power else None
            if pw: ems.append(("power", pw, 0.0, 2 * GRID, 180)); occ.add(self.power_rect(0.0, 2 * GRID, 0, 1))
            else: ems.append(("label", net, 0.0, 2 * GRID, 270)); occ.add_anchor(0.0, 2 * GRID, net); occ.add(self.label_rect(net, 0.0, 2 * GRID, 0, 1))
            return self.finish_cell(occ, ems)
        pins = self.sym_pins(p, 0.0, 0.0, 0); body = self.body_rect(p, 0.0, 0.0, 0)
        sv = short_value(p["value"])
        ref_at = (body[2] + GRID, body[1] + text_h()); val_at = (body[2] + GRID, body[1] + 2 * text_h() + 0.5)
        occ.add(body); occ.add((ref_at[0], ref_at[1] - text_h(), ref_at[0] + text_w(p["ref"]), ref_at[1])); occ.add((val_at[0], val_at[1] - text_h(), val_at[0] + text_w(sv), val_at[1]))
        ems.append(("symbol", p, 0.0, 0.0, 0, ref_at, val_at, sv != p["value"])); seen = set()
        if sv != p["value"]: ems.append(("text", sv, val_at[0], val_at[1], FONT))
        for num, nm, sx, sy, dx, dy in pins:
            key = (round(sx, 2), round(sy, 2))
            if key in seen: continue
            seen.add(key); net = p["nets"].get(num)
            if net is None: raise SystemExit("%s pin %s has no net" % (p["ref"], num))
            if net == "NC": ems.append(("noconn", sx, sy)); continue
            self.lane(occ, ems, net, sx, sy, dx, dy, [])
        return self.finish_cell(occ, ems)

    def power_rect(self, x, y, dx, dy):
        if dy < 0: return (x - 2 * GRID, y - 4 * GRID, x + 2 * GRID, y)
        if dy > 0: return (x - 2 * GRID, y, x + 2 * GRID, y + 4 * GRID)
        if dx > 0: return (x, y - 2 * GRID, x + 4 * GRID, y + 2 * GRID)
        return (x - 4 * GRID, y - 2 * GRID, x, y + 2 * GRID)

    def label_rect(self, net, x, y, dx, dy, extra=0.0):
        w = text_w(base(net)) + GRID + extra; h = FONT * 1.2
        if dx > 0: return (x, y - h, x + w, y)
        if dx < 0: return (x - w, y - h, x, y)
        if dy < 0: return (x - h, y - w, x, y)
        return (x, y, x + h, y + w)

    def finish_cell(self, occ, ems):
        # a wire end on the interior of another wire of its net, or three or more wire ends meeting, needs a junction: KiCad
        # connects nothing there without one (measured 15 Sep 2026: the same tap connects with the dot and not without it)
        ends = {}
        for (x0, y0, x1, y1, n) in occ.wires:
            for ex, ey in ((x0, y0), (x1, y1)): ends.setdefault((round(ex, 2), round(ey, 2), n), 0); ends[(round(ex, 2), round(ey, 2), n)] += 1
        junctions = set()
        for (ex, ey, n), cnt in ends.items():
            if cnt >= 3: junctions.add((ex, ey))
            for (x0, y0, x1, y1, m) in occ.wires:
                if m != n: continue
                lo_x, hi_x, lo_y, hi_y = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1)
                inside = lo_x - 1e-6 <= ex <= hi_x + 1e-6 and lo_y - 1e-6 <= ey <= hi_y + 1e-6
                at_end = (abs(ex - x0) < 1e-6 and abs(ey - y0) < 1e-6) or (abs(ex - x1) < 1e-6 and abs(ey - y1) < 1e-6)
                if inside and not at_end: junctions.add((ex, ey))
        for (ex, ey) in sorted(junctions): ems.append(("junction", ex, ey))
        # KiCad connects a wire only at its own ends: a junction or a label on a wire's interior leaves everything past it
        # unconnected (measured 15 Sep 2026, U1's second rail pin), so every wire is split at those points
        lab_pts = {}
        for e in ems:
            if e[0] in ("label", "glabel"): lab_pts.setdefault(base(e[1]), set()).add((round(e[2], 2), round(e[3], 2)))
        ems[:] = [e for e in ems if e[0] != "wire"]
        for x0, y0, x1, y1, wnet in occ.wires:
            cuts = set(junctions) | lab_pts.get(base(wnet), set())
            pts = [(x0, y0)]
            inner = [c for c in cuts if min(x0, x1) - 1e-6 <= c[0] <= max(x0, x1) + 1e-6 and min(y0, y1) - 1e-6 <= c[1] <= max(y0, y1) + 1e-6
                     and not ((abs(c[0] - x0) < 1e-6 and abs(c[1] - y0) < 1e-6) or (abs(c[0] - x1) < 1e-6 and abs(c[1] - y1) < 1e-6))]
            inner.sort(key=lambda c: (c[0] - x0) ** 2 + (c[1] - y0) ** 2)
            pts += inner + [(x1, y1)]
            for (a, b), (c_, d) in zip(pts, pts[1:]): ems.append(("wire", a, b, c_, d))
        xs0 = [r[0] for r in occ.rects] + [w[0] for w in occ.wires] + [w[2] for w in occ.wires]
        xs1 = [r[2] for r in occ.rects] + [w[0] for w in occ.wires] + [w[2] for w in occ.wires]
        ys0 = [r[1] for r in occ.rects] + [w[1] for w in occ.wires] + [w[3] for w in occ.wires]
        ys1 = [r[3] for r in occ.rects] + [w[1] for w in occ.wires] + [w[3] for w in occ.wires]
        return dict(ems=ems, x0=min(xs0), y0=min(ys0), x1=max(xs1), y1=max(ys1))

    # ---- pages
    def pack(self, title, cells):
        """Shelf-pack the cells of one section onto the A3 pages, continuing the page the previous section left off on: each
        section opens a new row under its own heading, and a page carries the sections it holds."""
        usable_w = CELL_W - 2 * MARGIN; usable_h = CELL_H - MARGIN - TITLE_H
        GAP = 6 * GRID; HEAD = 7 * GRID
        st = self.state
        def new_page():
            st["page"] = dict(titles=[], cells=[], heads=[]); self.pages.append(st["page"]); st["cx"] = st["cy"] = st["row_h"] = 0.0
        def heading():
            if st["cx"] > 0: st["cy"] += st["row_h"]; st["cx"] = 0.0; st["row_h"] = 0.0
            first_h = (cells[0]["y1"] - cells[0]["y0"] + GAP) if cells else 0.0
            if st["page"] is None or st["cy"] + HEAD + first_h > usable_h: new_page()
            st["page"]["titles"].append(title); st["page"]["heads"].append((title, g(MARGIN), g(TITLE_H + st["cy"] + 4 * GRID))); st["cy"] += HEAD
        heading()
        for c in cells:
            w = c["x1"] - c["x0"] + GAP; h = c["y1"] - c["y0"] + GAP
            if w > usable_w or h > usable_h - HEAD:
                print("schlayout: WARNING cell %s of section %r is larger than a page (%.0f x %.0f mm)" % (c.get("ref", "?"), title[:40], w, h)); self.oversize.append(c.get("ref", "?"))
                new_page(); st["page"]["titles"].append(title); st["page"]["cells"].append((c, g(MARGIN - c["x0"]), g(TITLE_H - c["y0"]))); st["page"] = None; continue
            if st["page"] is None: new_page(); st["page"]["titles"].append(title); st["page"]["heads"].append((title + " (continued)", g(MARGIN), g(TITLE_H + 4 * GRID))); st["cy"] += HEAD
            if st["cx"] + w > usable_w:
                st["cy"] += st["row_h"]; st["cx"] = 0.0; st["row_h"] = 0.0
            if st["cy"] + h > usable_h:
                new_page(); st["page"]["titles"].append(title); st["page"]["heads"].append((title + " (continued)", g(MARGIN), g(TITLE_H + 4 * GRID))); st["cy"] += HEAD
            st["page"]["cells"].append((c, g(MARGIN + st["cx"] - c["x0"]), g(TITLE_H + st["cy"] - c["y0"])))
            st["cx"] += w; st["row_h"] = max(st["row_h"], h)

    def emit(self):
        cols = min(MAX_COLS, max(1, math.ceil(math.sqrt(len(self.pages) * CELL_H / CELL_W))))
        rows = math.ceil(len(self.pages) / cols)
        if rows > MAX_ROWS:
            cols = MAX_COLS; rows = math.ceil(len(self.pages) / cols)
            if rows > MAX_ROWS: raise SystemExit("schlayout: %d pages do not fit a %d x %d sheet" % (len(self.pages), MAX_COLS, MAX_ROWS))
        total = len(self.pages)
        for i, page in enumerate(self.pages):
            col, row = i % cols, i // cols; ox, oy = col * CELL_W, row * CELL_H
            self.frame(ox, oy, page, i + 1, total)
            for c, dx, dy in page["cells"]:
                for e in c["ems"]: self.emit_one(e, ox + dx, oy + dy)
        W = cols * CELL_W; H = rows * CELL_H
        return '"User" %.2f %.2f' % (W, H), total, cols, rows

    def frame(self, ox, oy, page, k, total):
        kisch.rect(ox + 2 * GRID, oy + 2 * GRID, ox + CELL_W - 2 * GRID, oy + CELL_H - 2 * GRID)
        kisch.rect(ox + 2 * GRID, oy + 2 * GRID, ox + CELL_W - 2 * GRID, oy + TITLE_H - 2 * GRID)
        titles = []
        for t in page["titles"]:
            if t not in titles: titles.append(t)
        t = "  |  ".join(x.split(":")[0].strip() for x in titles)
        kisch._text("%s   %s" % (self.board_title, self.phase), ox + 4 * GRID, oy + 6 * GRID, 2.0)
        kisch._text(t[:170], ox + 4 * GRID, oy + 9.5 * GRID, 1.5, bold=False)
        for ht, hx, hy in page.get("heads", []): kisch._text(ht[:160], ox + hx, oy + hy, 1.8)
        right = "page %d of %d   MeshSat field kit V2, CERN-OHL-S-2.0   PROTOTYPE, nothing built   %s" % (k, total, self.header.get("date", ""))
        kisch._text(right, ox + CELL_W - 4 * GRID - text_w(right, 1.5), oy + 6 * GRID, 1.5, bold=False)

    def emit_one(self, e, dx, dy):
        kind = e[0]
        if kind in ("wire", "label", "glabel", "power", "flag", "symbol"):
            sh = list(e); sh[2 if kind == "symbol" or kind in ("label", "glabel", "power", "flag") else 1] += 0
            if kind == "wire": sh = ["wire", e[1] + dx, e[2] + dy, e[3] + dx, e[4] + dy]
            elif kind in ("label", "glabel"): sh = [kind, e[1], e[2] + dx, e[3] + dy, e[4]]
            elif kind == "power": sh = ["power", e[1], e[2] + dx, e[3] + dy, e[4]]
            elif kind == "flag": sh = ["flag", e[1], e[2] + dx, e[3] + dy]
            else: sh = ["symbol", e[1], e[2] + dx, e[3] + dy, e[4]]
            self.all_ems.append(sh)
        if kind == "wire": kisch.wire(e[1] + dx, e[2] + dy, e[3] + dx, e[4] + dy)
        elif kind == "junction": kisch.junction(e[1] + dx, e[2] + dy)
        elif kind == "label": kisch.label(e[1], e[2] + dx, e[3] + dy, e[4])
        elif kind == "glabel": kisch.glabel(e[1], e[2] + dx, e[3] + dy, e[4])
        elif kind == "noconn": kisch.noconn(e[1] + dx, e[2] + dy)
        elif kind == "power":
            (lib, nm), x, y, rot = e[1], e[2], e[3], e[4]
            kisch.place_symbol(lib, nm, "#PWR%03d" % self.pf[0], nm, "", x + dx, y + dy, rot=rot); self.pf[0] += 1
        elif kind == "flag":
            p, x, y = e[1], e[2], e[3]; kisch.place_symbol("power", "PWR_FLAG", p["ref"], "PWR_FLAG", "", x + dx, y + dy, hide_props=True)
        elif kind == "text": kisch._text(e[1], e[2] + dx, e[3] + dy, e[4], bold=False)
        elif kind == "symbol":
            p, x, y, rot, ref_at, val_at = e[1], e[2], e[3], e[4], e[5], e[6]; hide_value = e[7] if len(e) > 7 else False
            lib, nm = (p["_boxsym"].split(":") if p.get("_boxsym") else (p["lib"], p["sym"]))
            sat = self.is_sat(p); font = e[8] if len(e) > 8 else FONT
            kisch.place_symbol(lib, nm, p["ref"], p["value"], p["fp"], x + dx, y + dy, p["lcsc"], in_bom=p.get("in_bom", True), rot=rot,
                               ref_at=(ref_at[0] + dx, ref_at[1] + dy), val_at=(val_at[0] + dx, val_at[1] + dy), hide_value=hide_value or (sat and short_value(p["value"], (e[9] if len(e) > 9 else False) or (sat and rot in (0, 180) and self.orient(p, False) == rot % 180)) != p["value"]),
                               font=font)
            shown = short_value(p["value"], (e[9] if len(e) > 9 else False) or (sat and rot in (0, 180) and self.orient(p, False) == rot % 180))
            if sat and shown != p["value"]: kisch._text(shown, val_at[0] + dx, val_at[1] + dy, font, bold=False)


def verify(eng):
    """The drawing's own connectivity against the generator's pin-to-net map, by KiCad's rules as measured on 15 Sep 2026: a wire
    joins its two ends; ends, pins, junctions and label anchors at one point are one node; nothing connects on a wire's interior.
    Every component must carry exactly one net name and every net a label or power symbol, or the generator stops here."""
    parent = {}
    def key(x, y): return (round(x, 2), round(y, 2))
    def find(a):
        while parent.setdefault(a, a) != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b): parent[find(a)] = find(b)
    names = {}; pins = []
    for e in eng.all_ems:
        k = e[0]
        if k == "wire": union(key(e[1], e[2]), key(e[3], e[4]))
        elif k in ("label", "glabel"): names.setdefault(key(e[2], e[3]), set()).add(base(e[1])); find(key(e[2], e[3]))
        elif k == "power": names.setdefault(key(e[2], e[3]), set()).add(e[1][1]); find(key(e[2], e[3]))
        elif k == "flag": pins.append((key(e[2], e[3]), e[1]["ref"], "1", base(e[1]["nets"]["1"])))
        elif k == "symbol":
            p, x, y, rot = e[1], e[2], e[3], e[4]
            for num, nm, sx, sy, dx, dy in eng.sym_pins(p, x, y, rot):
                net = p["nets"].get(num)
                if net and net != "NC": pins.append((key(sx, sy), p["ref"], num, base(net)))
    comp_names = {}; comp_pins = {}; comp_where = {}
    for pt, nms in names.items(): comp_names.setdefault(find(pt), set()).update(nms); comp_where.setdefault(find(pt), []).append((pt, tuple(sorted(nms))))
    for pt, ref, num, net in pins: comp_pins.setdefault(find(pt), []).append((ref, num, net)); comp_where.setdefault(find(pt), []).append((pt, ref + "." + num))
    bad = []
    drawn = collections.Counter(e[1]["ref"] for e in eng.all_ems if e[0] in ("symbol", "flag"))
    for p in eng.P:
        if drawn.get(p["ref"], 0) != 1: bad.append("PART %s drawn %d times" % (p["ref"], drawn.get(p["ref"], 0)))
    for c, plist in comp_pins.items():
        nets = set(n for _, _, n in plist); labs = comp_names.get(c, set())
        if len(nets | labs) > 1: bad.append("SHORT %s: pins %s labels %s at %s" % (sorted(nets | labs), [(r, n) for r, n, _ in plist][:6], sorted(labs)[:4], comp_where[c][:10]))
        elif not labs: bad.append("UNNAMED net %s: pins %s carry no label" % (sorted(nets), [(r, n) for r, n, _ in plist][:6]))
    for c, labs in comp_names.items():
        if len(labs) > 1 and c not in comp_pins: bad.append("SHORT between labels %s" % sorted(labs))
    if bad:
        for b in bad[:20]: print("schlayout verify:", b)
        raise SystemExit("schlayout: the drawing does not carry the netlist it was given (%d defect(s) above)" % len(bad))
    print("schlayout verify: %d pins in %d nets, every component one name" % (len(pins), len(comp_pins)))


def run(parts, sections, power, bypass, header, phase, board_title):
    """Lay the whole schematic out into kisch's body; returns (paper, pages, cols, rows)."""
    kisch.reset_body()
    eng = Engine(parts, sections, power, bypass, header, phase, board_title)
    res = eng.run(); verify(eng); return res
