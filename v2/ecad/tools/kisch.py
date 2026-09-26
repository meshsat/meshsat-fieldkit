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
            ans = nums          # a land with no copper pad at all (a mounting hole, a panel jack's bore) reads as an empty set: judged, nothing to name
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


# ---------------------------------------------------------------- a clamp drawn with its polarity (S-09, 26 September 2026)
#
# Every one-way suppressor on the set (sixteen of them, adjudication A03 of MESHSAT-1357) was drawn with KiCad's
# Device:D_TVS, whose own description is "Bidirectional transient-voltage-suppression diode" and whose two pins are
# named A1 and A2. A drawing with no cathode cannot show which way a one-way part points, so nothing read it: seven of
# the sixteen were drawn with the cathode on the RETURN (board D's D1, board E's D1 to D4 and D10, board P's D1), where
# a unidirectional clamp is a forward-biased diode across its own rail; the other nine (board A's four, board B's five)
# were the right way round on the wrong symbol. KiCad 9.0.9's Device library has no unidirectional TVS symbol (checked
# on the box: D_TVS is the bidirectional one, and the Diode library's own one-way parts, SM6T* and SMAJ*A, also name
# their pins A1/A2), so a one-way part is drawn with Device:D_Zener: pin 1 is K and pin 2 is A, the bent-bar mark is
# the standard one-way suppressor symbol, and on KiCad's Diode_SMD lands (D_SMA, D_SMB, D_SMC, SOD-123, SOD-323) pad 1
# is the banded cathode, so the K pin lands on the band.
#
# The direction comes from the part number, because that is what is bought, and only for families whose makers'
# sheets say how their numbers read. SMBJ and SMCJ: a C in the suffix is the bidirectional part in every maker's sheet
# held for the codes the set buys. Every one of those sheets is filed in v2/vendor, with its source URL and sha256 in
# v2/vendor/SOURCES.yaml; the four sha256 prefixes below were read off the filed bytes on 26 September 2026 (ts-tvs,
# main 45bde541) and equal the SOURCES.yaml records:
#   - Littelfuse SMCJ series, Revised 11/20/15, v2/vendor/power/littelfuse-smcj-series-tvs.pdf (sha256 6e610db9...):
#     "Part Numbering System: SMCJ XXX C A", C = BI-DIRECTIONAL; SMCJ40A under "Part Number (Uni)", SMCJ40CA under
#     "(Bi)". The fitted C224052 (SMCJ40A), C224047 (SMCJ28A), C374030 (SMCJ18A) and C80273 (SMCJ40CA).
#   - Littelfuse SMBJ series, Revised JC.07/04/25, v2/vendor/power/littelfuse-smbj-series-tvs.pdf (sha256 d7df155b...):
#     the fitted C83270 (SMBJ6.0A) and C151256 (SMBJ18A).
#   - Diodes Incorporated DS19002 Rev. 20-2, v2/vendor/diodes/diodes-smbj-ds19002.pdf (sha256 752945fa...), note 8,
#     "Suffix C denotes Bi-directional device": board B's SMBJ58A-13-F, LCSC C135085.
#   - MDD SMBJ5.0(C)A THRU SMBJ440(C)A, Rev:2025A7, v2/vendor/power/mdd-smbj-series-tvs.pdf (sha256 95385273...), whose
#     table lists SMBJ5.0A and SMBJ20A under "Unidirectional" and SMBJ5.0CA and SMBJ20CA under "Bidirectional": the
#     fitted C113974 (SMBJ5.0A) and C364296 (SMBJ20A).
# The Vishay SMBJ and SMCJ sheets in v2/vendor/vishay number them the same way. The SMCJ18A on board E's D3 and board
# A's D1 carries C374030, the Littelfuse part the SMCJ sheet above covers (the second fix-up of round 4 wrote that E's
# D3 had no code: gen_sch_e.py has carried C374030 since; the older E deliverable BOM row jlc_certify reads carries
# C151906, a BORN SMCJ18A whose own sheet is not held). Nexperia's PESD5V0S1BA is "Bidirectional ESD protection diode"
# on the first line of its own datasheet (v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf, LCSC C19224). Any other part
# number is refused
# unless the caller says which it is AND names the datasheet that says so (`basis=`), and that declaration is written
# into the board's intent file under "clamps", where the gate (port_protect.py, TRN-001) reads it.
_UNI_FAMILY = re.compile(r"^(SMBJ|SMCJ)(\d+(?:\.\d+)?)(C?A?)\b", re.I)
_PESD = re.compile(r"^PESD\d+V\d+S1B[A-Z]\b", re.I)
# PART NUMBERS READ ONE BY ONE, where the maker's own sheet for exactly that part is held and says which it is (round 6,
# 26 September 2026). Board D's microphone clamps D10 and D13 moved from PESD5V0S1BA to Nexperia PESD12VL1BA (LCSC
# C38558) in round 4, and this reader returned None for it, so port_protect judged both UNJUDGED and TRN-001 read
# INCONCLUSIVE on D under r4t's tools. Nexperia's naming is not read as a rule from one sheet (a PESDxVL1BA is not
# asserted to be two-way because a PESDxVS1BA is): each part is listed with its own sheet's words. The sheet is filed
# at v2/vendor/nexperia/nexperia-pesd12vl1ba.pdf (sha256 3cc06cb0..., read off the filed bytes on 26 September 2026 and
# equal to its v2/vendor/SOURCES.yaml record).
#
# BOARD A's D22 SINCE MAIN 458b2873 (round 6 fourth pass, 26 September 2026): the restart guard's pull-up clamp, a
# BZT52C12-7-F on Device:D_Zener, cathode on FE_VZ and anode on ground. A zener is a one-way part, but that is read from
# its maker's sheet here as well, not from the symbol it is drawn with: Diodes Incorporated DS18004 Rev. 38-2 (the board
# A author's copy, sha256 0fbd7d13..., filed by the parts stream of this round at v2/vendor/diodes/diodes-bzt52c-ds18004.pdf
# with its v2/vendor/SOURCES.yaml record) is headed
# "BZT52C2V0 - BZT52C51 SURFACE MOUNT ZENER DIODE", states "Polarity: Cathode Band", lists type BZT52C12 (11.4 V to
# 12.7 V at 5 mA) and orders it as "(Type Number)-7-F". Without it the polarity pass read D22 UNJUDGED.
_HELD_DIRECTION = {
    "PESD12VL1BA": ("bi", "Nexperia PESD12VL1BA product data sheet, 14 April 2023: 'Low capacitance bidirectional ESD "
                          "protection diode', section 2 'Bidirectional ESD protection of one line', pins K1 and K2 "
                          "(LCSC C38558)"),
    "BZT52C12-7-F": ("uni", "Diodes Incorporated DS18004 Rev. 38-2, 'BZT52C2V0 - BZT52C51 SURFACE MOUNT ZENER DIODE', "
                            "'Polarity: Cathode Band', type BZT52C12 11.4 V to 12.7 V, ordered as '(Type Number)-7-F' "
                            "(LCSC C124196)"),
}
_GROUNDISH = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)


def tvs_direction(value):
    """("uni" | "bi" | None, basis): the direction of a suppressor, read from the part number its value starts with."""
    mpn = str(value).strip().split()[0] if str(value).strip() else ""
    held = _HELD_DIRECTION.get(re.sub(r",\d+$", "", mpn).upper())
    if held:
        return held[0], "%s: %s" % (mpn, held[1])
    m = _UNI_FAMILY.match(mpn)
    if m:
        return ("bi", "%s: a C in the suffix is the bidirectional part (Littelfuse, Diodes Inc and MDD number them alike)" % mpn) \
            if "C" in m.group(3).upper() else \
            ("uni", "%s: no C in the suffix, the unidirectional part (Littelfuse, Diodes Inc and MDD number them alike)" % mpn)
    if _PESD.match(mpn):
        return "bi", "%s: Nexperia's S1B type, 'Bidirectional ESD protection diode'" % mpn
    return None, "%s: not a part number this helper can read" % (mpn or "(empty value)")


def _declared_rail(net):
    """The intent's record of a rail under either of the two keys intent.py stores ('X' and '/X')."""
    rails = _intent._I.get("rails") or {}
    n = str(net).lstrip("/")
    return rails.get(n) or rails.get("/" + n) or {}


def tvs(ref, value, protected, ret, fp, lcsc="", direction=None, basis=""):
    """A transient clamp between a protected conductor and its return, drawn so its polarity can be read (S-09).

    One-way part: Device:D_Zener, K (pin 1) on `protected`, A (pin 2) on `ret`. Two-way part: Device:D_TVS, pin 1 on
    `protected`, pin 2 on `ret`. `direction` is read from the part number `value` starts with; a caller that gives
    one that contradicts it is refused, and a part number the helper cannot read needs `direction` said AND `basis`,
    the maker's datasheet statement of it. Every call is recorded in the board's intent (key "clamps": direction,
    basis, protected, return), so the gate judges what the generator declared as well as what it drew."""
    read, why_read = tvs_direction(value)
    if direction is not None and direction not in ("uni", "bi"):
        raise SystemExit("tvs %s: direction must be 'uni' or 'bi', not %r" % (ref, direction))
    if direction is not None and read is not None and direction != read:
        raise SystemExit("tvs %s (%s): the call says %s and the part number says %s (%s)" % (ref, value, direction, read, why_read))
    d = direction or read
    if d is None:
        raise SystemExit("tvs %s (%s): %s, so say direction='uni' or 'bi' with basis= naming the datasheet that says so"
                         % (ref, value, why_read))
    if read is None and not str(basis or "").strip():
        # A DIRECTION WITH NO SOURCE IS THE DRAWING'S CLAIM ALL OVER AGAIN (review fix-up of round 4, 26 September
        # 2026): the gate reads this declaration as the part's direction, so it has to carry where it came from.
        raise SystemExit("tvs %s (%s): direction=%r is said for a part number this helper cannot read, so give basis= "
                         "with the maker's datasheet statement of it" % (ref, value, direction))
    if str(protected).lstrip("/") == str(ret).lstrip("/"):
        raise SystemExit("tvs %s (%s): the protected conductor and the return are the same net %s" % (ref, value, ret))
    # THE HELPER DRAWS K ON THE PROTECTED CONDUCTOR, which is right when that conductor is positive with respect to its
    # return (second fix-up of round 4, 26 September 2026). On a negative rail the cathode belongs on the return, so a
    # negative conductor (a name that starts with '-', or a rail the intent declares below zero) is refused rather
    # than drawn the wrong way round. No board carries one today.
    _pv = _declared_rail(protected).get("volts")
    if str(protected).lstrip("/").startswith("-") or (_pv is not None and float(_pv) < 0):
        raise SystemExit("tvs %s (%s): %s is a negative conductor, and this helper draws the cathode on the protected "
                         "net, which is right only above the return; draw it with its cathode on %s" % (ref, value, protected, ret))
    # THE SWAPPED CALL IS THE DEFECT THIS HELPER EXISTS FOR: a clamp's protected conductor is never a ground, and a net
    # the board's intent already declares as a RETURN rail (board P's PACK_N, rail(..., returns="PACK_P")) is not one
    # either. The intent check sees only rails declared BEFORE this call; the gate (port_protect.py) judges the netlist
    # and the finished intent again, independently of this call, so a return declared later is still caught there.
    if _GROUNDISH.match(str(protected).lstrip("/")):
        raise SystemExit(("tvs %s (%s): the protected conductor %s is a ground and the return %s is not: the two "
                          "arguments are swapped" if not _GROUNDISH.match(str(ret).lstrip("/")) else
                          "tvs %s (%s): the protected conductor %s and the return %s are both grounds")
                         % (ref, value, protected, ret))
    _rail = _declared_rail(protected)
    if _rail.get("returns"):
        raise SystemExit("tvs %s (%s): %s is declared as the return of %s in this board's intent, so it cannot be the "
                         "conductor this clamp protects" % (ref, value, protected, _rail.get("returns")))
    _intent._I.setdefault("clamps", {})[str(ref)] = {
        "direction": d, "basis": why_read if read is not None else str(basis).strip(),
        "protected": str(protected).lstrip("/"), "return": str(ret).lstrip("/"),
        "symbol": "Device:D_Zener" if d == "uni" else "Device:D_TVS"}
    if d == "uni":
        part(ref, "Device", "D_Zener", value, fp, {"1": protected, "2": ret}, lcsc)
    else:
        part(ref, "Device", "D_TVS", value, fp, {"1": protected, "2": ret}, lcsc)

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
    # A MAP KEY THE SYMBOL DOES NOT HAVE IS DROPPED ON THE FLOOR, and nothing said so (17 September 2026). Board B's
    # U10, a TMP117 in WSON-6, wrote "7": "GND" for its thermal pad and the library symbol carries no pin 7, so the
    # entry reached no wire, no label and no netlist node, and the pad floats on the board that was cut. The
    # symbol is the only road from the map to the netlist: a key it cannot carry is refused here, where the
    # symbol's pins are known, with the same strictness the loop below applies in the other direction.
    _have = {num for num, _, _, _, _ in pins}
    # A key the symbol lacks but the LAND has may be written "NC": that is the declared no-connect for a mechanical
    # pad (an M.2 socket's standoff and retention tabs, a JST-SH header's tabs) which the land check above asks for
    # and which no library symbol carries a pin for. Anything else on such a key is a net that would reach nothing.
    _dead = sorted(k for k, v in p["nets"].items() if k not in _have and v != "NC")
    if _dead:
        raise SystemExit("%s (%s): the map names pin%s %s and the symbol %s:%s has no such pin (it has %s), so %s "
                         "would reach nothing. Use a symbol that carries the pad, or a numbered connector symbol "
                         "through ic()." % (p["ref"], p["value"], "" if len(_dead) == 1 else "s", ", ".join(_dead),
                                            p["lib"], p["sym"], ", ".join(sorted(_have, key=lambda v: (len(v), v))),
                                            "that net" if len(_dead) == 1 else "those nets"))
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
