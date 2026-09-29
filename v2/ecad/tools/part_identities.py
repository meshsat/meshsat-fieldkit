#!/usr/bin/env python3
"""Part identities per distinct selection (pre-PCB layer 6, EQ-21; MESHSAT-1357, stream w5ident 27 September 2026, and
stream w5identc 29 September 2026 for board C's slice on main b874b744).

WHAT THIS IS FOR. Layer 6 asks every fitted part for an exact identity: a maker, a manufacturer part number and a held
document that names that part number (LAYER-STATUS item 6.1; EXECUTION-PLAN review D, "exact part identities", before
each board's layout entry). The schematic generators write a value, a land and sometimes an LCSC order code, and no
manufacturer part number. Rows are not parts: a hundred "100n" 0603 capacitors on 3.3 V rails are one selection, and a
"100n" on a 3.3 V rail and one on a 20 V stage are two. So this tool groups the BOM parts into DISTINCT SELECTIONS by
every property that decides the part, and never merges rows whose ratings or constraints differ:

  capacitor  value, package, dielectric (stated, or the class rule below), the voltage rating it needs (the stated
             one, or the working voltage from the netlist and the intent declarations at the project's 20 percent
             derate margin), tolerance, the construction a value names (polymer, tantalum) and any named part
  resistor   value, package, tolerance, power rating (stated, or twice the dissipation bound from the netlist),
             temperature coefficient where stated, the kind (general, current sense, zero-ohm link) and any named part
  inductor   the named part where the value names one, else value, package, the current it carries and the use the
             value states (RF filter, bias tee, ferrite)

and every other row by its value and land (a copper land or a solder jumper is NOT_A_PART: there is nothing to buy).

THE ROWS COME FROM THE COMMITTED NETLIST (stream w5identc): every part the generator wrote that the schematic does not
mark exclude_from_bom, with the value, land and order code the netlist carries, read by parsing the S-expression
(netlist_sexp). The per-reference BOM export is compared and its differences recorded; it is never the source, because
an export older than the netlist misses parts (board C's at b874b744 misses eight).

THE IDENTITY of each selection lives in the table (`pcb_part_identities.yaml`, scoped to the boards it names) keyed by
the selection key this tool computes. RULE D-2 (stream w5identc, answering w5ident's second check ID-B1 to ID-B3): a
RESOLVED selection names a maker, a part number and a held document with a page, and `check` READS that page's text
layer (pdftotext; an HTML page through its parser) and refuses the binding unless the part number is printed there,
letter case aside and nothing else (a PRINTED binding), or unless the page is the maker's own ordering-code table and
decodes the part number field by field (a DECODED binding, the session's decision of 29 September 2026: every field's
code and its meaning on the cited page, the fields spelling the whole part number, and the decoded value, package,
tolerance, voltage and dielectric meeting the selection; a distributor's page is refused). A DECODED binding is never
counted as PRINTED. A series sheet read neither way leaves the selection UNRESOLVED (DOCUMENT_DOES_NOT_NAME_THE_PART).

WHY THE NETLIST AND NOT ONLY THE BOM. The voltage a capacitor must be rated for is the voltage ACROSS it, which is a
property of the two nets it joins, read with the board's committed intent file (<stem>-intent.json).

THE VOLTAGE ACROSS A PART (rule V-1, `Board.bound`). A declared net carries the worst of its `volts`, `v_max` and
`v_work` (derate.py's `_worst_declared`), a net that rides on another carries the declared bias, as derate.py judges
it. A net nobody declared is BOUNDED, not guessed: by the highest of every source that can set its level (the
declared voltages on an active part's other pins, a declared net reached through a resistor, a ferrite, a fuse, a
diode, a switch or a link, a pin level a maker's document gives), and only when every source is bounded. The bound is
conservative (an IC with a 54 V pin bounds its 3.3 V pins at 54 V) and is labelled BOUND wherever it is used. A bound
that cannot be conservative says so instead: GROUND AND A DECLARED RETURN ARE FLOORS AND NEVER CEILINGS (a net declared
at most RETURN_V_MAX above ground, or marked `returns`, as board P's PACK_N at 0.05 V), A CONNECTOR'S PIN IS SET ON ITS
FAR SIDE (a source of unknown level unless the net is declared), A SWITCH NODE BEHIND AN INDUCTOR IS DECLARED OR
UNBOUNDED (the project declares no ringing figure), and a net the intent declares with no maximum is UNBOUNDED. An
unstated capacitor on an UNBOUNDED net is an open item and gets no part; a stated rating there stands and is recorded
as NOT CHECKED. Rows whose requirement is unknown, or unchecked, share a selection only across the same nets of one
board.

WHAT IT DOES NOT DO. It does not judge DC-bias capacitance loss, ripple current, pulse withstand, surge or clamp
levels, SRF or temperature grade; it chooses no part (the table's builder records each choice with its reason); and it
orders nothing.

Usage:
  part_identities.py rows       [--board c] [--json]   the BOM parts with their derived properties and keys
  part_identities.py selections [--board c] [--json]   the distinct selections, their rows and requirements
  part_identities.py check [TABLE] [--out READING.json] [--unfetched-ok]
                                                       the table against the netlists, and rule D-2 read on every binding
  part_identities.py render [TABLE] --out PAGE.md      a page of the table
"""
import csv, json, math, os, re, sys, collections, hashlib, subprocess, shutil, html.parser

HERE = os.path.dirname(os.path.abspath(__file__))
ECAD = os.path.dirname(HERE)
V2 = os.path.dirname(ECAD)
REPO = os.path.dirname(V2)
sys.path.insert(0, HERE)
import netlist_sexp
from verdict import opt

TABLE = os.path.join(HERE, "pcb_part_identities.yaml")
PAGE = os.path.join(V2, "docs", "parts", "IDENTITIES.md")
GENERATED = os.environ.get("PART_IDENTITIES_EXPORTS") or os.path.join(V2, "release", "handover", "_generated")   # a later export set by env

# The six schematic boards, their phase directory and stem, as the H2 exports name them. A board table change
# (set 6 moves a phase) is one line here; `rows` refuses a netlist whose sha is not the one the export names.
BOARDS = [
    ("a", "pcb-a-power-a23", "pcb-a-power"),
    ("b", "pcb-b-compute-b19", "pcb-b-compute"),
    ("c", "pcb-c-display-c8", "pcb-c-display"),
    ("d", "pcb-d-aprs-d9", "pcb-d-aprs"),
    ("e", "pcb-e1-dock-e7", "pcb-e1-dock"),
    ("p", "pcb-p-pack-p2", "pcb-p-pack"),
]

DERATE_MARGIN = 0.20            # derate.py's MARGIN, the project's CMP-001 screen
POWER_FACTOR = 2.0              # a resistor is rated at least twice its dissipation bound (SESSION rule R-P, below)
STD_V = [4.0, 6.3, 10.0, 16.0, 25.0, 35.0, 50.0, 63.0, 100.0, 200.0, 250.0, 500.0, 630.0, 1000.0, 2000.0, 3000.0]
STD_P = [0.0625, 0.1, 0.125, 0.25, 0.333, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0]
PKG_P = {"0201": 0.05, "0402": 0.0625, "0603": 0.1, "0805": 0.125, "1206": 0.25, "1210": 0.5, "2010": 0.5, "2512": 1.0}

PASSIVE_2T = ("R", "L", "FB")   # a two-terminal series element a DC bound passes through
# Parts that CONNECT their pins rather than set a level (rule V-1 (e)): a thermistor, a fuse, a switch's contacts, a
# link, a diode or an LED. A bound passes through them to every other pin, as through a resistor.
CONDUCTS = ("RT", "TH", "NTC", "PTC", "F", "SW", "JP", "D", "LED")
# A connector whose value names a passive far end (a button, a reed switch, a thermistor) conducts between its pins as
# that part does (the functional constraint the generator states; rule V-1 (e)).
CONDUCTS_BY_VALUE = r"button lead|reed sensor lead|thermistor socket"
NOT_A_SOURCE = ("C", "Y", "TP", "H", "MH", "FID", "P", "PAD", "W", "LOGO", "NT")   # nothing a DC level comes from (a crystal is open at DC)
SWITCH = ("Q", "D", "U")        # parts that can switch a node (rule V-1 (b): an inductor on such a node is a companion bound only)
CONNECTOR = ("J", "CN", "X")    # rule V-1 (g): a connector's pins are set on its far side
RETURN_V_MAX = 0.5              # rule V-1 (a'): a declared net whose maximum is at most this is a return, a floor only

# RULE V-2 (SESSION, 27 September 2026, pass 2 of stream w5ident): the ROLE of a pin, read from its maker's document
# filed in the tree, where the netlist and the intent cannot say it. An input pin is not a source (a cell-sense input
# does not drive its filter node); an output pin's ceiling is the level the document gives; a pin the document says the
# device holds from its supply pins tracks them; a pin the device drives at a level the document does not state is a
# source of unknown level (the node reads UNBOUNDED, with the document's own words). Matched on the part's value and
# the netlist's pin function (or pin number for a connector). Reversal: declare the net in the board's intent, which
# always wins, or correct an entry against the document.
PIN_ROLES = [
    dict(part=r"^BQ4050", by="pinfunction", doc="v2/vendor/battery/ti-bq4050.pdf", cite="TI SLUSC67B",
         inputs=("VC1", "VC2", "VC3", "VC4", "SRN", "SRP", "TS1", "TS2", "TS3", "TS4", "PRES", "PTC", "PTCEN", "PACK",
                 "BAT", "VCC", "SMBD", "SMBC", "NC", "PAD", "VSS"),
         outputs={"FUSE": (8.65, "section 6.20: FUSE output high at most 8.65 V at VBAT of 8 V and above, VBAT - 0.1 V to VBAT below"),
                  "CHG": (32.0, "section 6.1: absolute maximum of CHG and DSG 32 V, taken as the ceiling because section 6.18 puts the pin ABOVE the pack (VCHG(ON) = VBAT + 10.5 to 12 V for VBAT of 4.92 to 18 V, so 28.8 V at the 16.8 V pack, which is over the 26 V that section 6.3 recommends for VO: finding W5I-F6)"),
                  "DSG": (32.0, "section 6.1: absolute maximum of CHG and DSG 32 V, taken as the ceiling because section 6.18 puts the pin ABOVE the pack (VDSG(ON) = VBAT + 10.5 to 12 V for VBAT of 4.92 to 18 V, so 28.8 V at the 16.8 V pack, which is over the 26 V that section 6.3 recommends for VO: finding W5I-F6)")},
         tracks={"PCHG": (("VCC",), "section 6.19: VPCHG(ON) = VVCC - VPCHG of 6 to 8 V, VPCHG(OFF) within 0.4 V of VCC: the pin sits at or below VCC"),
                 "PBI": (("BAT", "VCC"), "sections 5 and 6.3: PBI is the power supply backup input, in the same 2.2 to 26 V supply range as BAT and VCC; with only its capacitor on it, the device holds it from BAT and VCC")},
         unknown={"BTP_INT": "section 5: a digital output; no output-high level is tabled in 6.12 as read here",
                  "DISP": "section 5: display control, type not stated", "LEDCNTLA": "section 5: LED segment drive, type not stated",
                  "LEDCNTLB": "section 5: LED segment drive, type not stated", "LEDCNTLC": "section 5: LED segment drive, type not stated"}),
    dict(part=r"^BQ77207", by="pinfunction", doc="v2/vendor/battery/ti-bq77207.pdf", cite="TI SLUSEG7D",
         inputs=("VDD", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "TS", "VSS", "EP"),
         outputs={},
         tracks={"COUT": (("VDD",), "sections 5, 6.5 and 7: COUT is a CMOS output, active high with drive to 6 V (6 V is the tabled minimum; no maximum is tabled), so its ceiling is taken as its own supply VDD, which a push-pull output does not exceed"),
                 "DOUT": (("VDD",), "sections 5, 6.5 and 7: DOUT is a CMOS output, active high with drive to 6 V (6 V is the tabled minimum; no maximum is tabled), so its ceiling is taken as its own supply VDD, which a push-pull output does not exceed")},
         unknown={}),
    dict(part=r"E2370KS0C1", by="pin", doc="v2/vendor/pdi/pdi-epd-driving-circuit-rev02.pdf", cite="PDi EPD Driving Circuit Rev. 02 (Oct 2025)",
         # the panel's pins as the board sees them through the FH34 flex connector (section 3, Pin assignment)
         inputs=("3", "8", "10", "11", "12", "13", "15", "16", "17", "1", "4", "6", "7", "19", "25", "26"),
         outputs={},
         tracks={},
         unknown={"2": "section 3: GDR, the COG's N-channel MOSFET gate drive output; its level is not stated",
                  "9": "section 3: BUSY_N, the COG's busy output; its level is not stated",
                  "14": "section 3: SDA, serial data input/output; its level is not stated",
                  "5": "section 3: VDHR, a capacitor pin the COG drives (the positive gate voltage's regulator); no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "18": "section 3: VDDD, the COG's internal regulator output on a capacitor pin; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "20": "section 3: VDH, the positive source driving voltage on a capacitor pin the COG drives; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "21": "section 3: VGH, the positive gate driving voltage on a capacitor pin; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "22": "section 3: VDL, the negative source driving voltage on a capacitor pin the COG drives; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "23": "section 3: VGL, the negative gate driving voltage on a capacitor pin; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603",
                  "24": "section 3: VCOM on a capacitor pin the COG drives; no level stated; section 2 specifies the driving-circuit capacitors as 25 V 0603"}),
]


def ref_prefix(ref):
    return ref[:len(ref) - len(ref.lstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ_"))].rstrip("_")


def ref_class(ref):
    """The designator's class letters: SW_SOS is a switch (SW), J_W1A a connector (J), R470 a resistor (R)."""
    m = re.match(r"[A-Z]+", ref)
    return m.group(0) if m else ""


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 16), b""): h.update(blk)
    return h.hexdigest()


# ------------------------------------------------------------------------------------------------ the netlist
def netlist(path):
    """({net: {(ref, pin)}}, {ref: {pin: net}}), read by PARSING the S-expression (netlist_sexp), never by a pattern
    over its text (stream w5identc, 29 September 2026: w5ident's reader matched the text). The parsed document is kept
    on the function for the caller (components, their fields and properties)."""
    doc = netlist_sexp.load(path)
    by_net, on, fn = {}, {}, {}
    for name, nodes in doc["nets"].items():
        by_net[name] = set()
        for ref, pin, func, _t in nodes:
            by_net[name].add((ref, pin))
            on.setdefault(ref, {})[pin] = name
            if func: fn[(ref, pin)] = func
    netlist.pinfunction = fn
    netlist.doc = doc
    return by_net, on


def worst_declared(*entries):
    """derate.py's `_worst_declared`: the highest of volts, v_max and v_work, the lowest v_min."""
    hi, lo = None, None
    for d in entries:
        if not d: continue
        for k in ("volts", "v_max", "v_work"):
            v = d.get(k)
            if v is None: continue
            hi = float(v) if hi is None else max(hi, float(v))
        v = d.get("v_min")
        if v is not None: lo = float(v) if lo is None else min(lo, float(v))
    if hi is None and lo is None: return {}
    out = {}
    if hi is not None: out["hi"] = hi
    out["lo"] = lo if lo is not None else 0.0
    return out


class Board:
    def __init__(self, letter, phase, stem):
        self.letter, self.phase, self.stem = letter, phase, stem
        self.net_path = os.path.join(ECAD, phase, "out", stem + ".net")
        self.intent_path = os.path.join(ECAD, phase, "out", stem + "-intent.json")
        self.bom_path = os.path.join(GENERATED, phase, "NOT_FOR_FAB-%s-bom-per-reference.csv" % stem)
        self.prov_path = os.path.join(GENERATED, phase, "provenance.json")
        self.by_net, self.on = netlist(self.net_path)
        self.pinfn = dict(netlist.pinfunction)
        doc = netlist.doc
        self.comps = set(doc["components"])
        self.values = {r: c["value"] for r, c in doc["components"].items()}
        self.footprints = {r: c["footprint"] for r, c in doc["components"].items()}
        self.lcsc = {r: (c["fields"].get("LCSC") or c["properties"].get("LCSC") or "").strip() for r, c in doc["components"].items()}
        # a part the schematic marks exclude_from_bom (a test point, a screw of a bought module) is not bought for the board
        self.bom_excluded = {r for r, c in doc["components"].items() if "exclude_from_bom" in c["properties"]}
        it = json.load(open(self.intent_path))
        self.rails = {k.lstrip("/"): v for k, v in (it.get("rails") or {}).items()}
        self.nodes = {k.lstrip("/"): v for k, v in (it.get("nodes") or {}).items()}
        self._bound = {}

    @classmethod
    def from_data(cls, on, rails=None, nodes=None, values=None, pinfn=None, letter="x"):
        """A board from dictionaries, for fixtures: {ref: {pin: net}}, the intent's rails and nodes, {ref: value} and
        {(ref, pin): pin function}. No file is read."""
        b = cls.__new__(cls)
        b.letter, b.phase, b.stem = letter, None, None
        b.on = {r: dict(p) for r, p in on.items()}
        b.by_net = {}
        for r, pins in b.on.items():
            for p_, n in pins.items(): b.by_net.setdefault(n, set()).add((r, p_))
        b.comps = set(b.on)
        b.values = dict(values or {}); b.pinfn = dict(pinfn or {})
        b.rails = dict(rails or {}); b.nodes = dict(nodes or {})
        b._bound = {}
        return b

    def declared(self, net):
        return worst_declared(self.rails.get(net), self.nodes.get(net))

    def is_ground(self, net):
        return net == "GND" or net.startswith("GND") or net in ("AGND", "PGND", "DGND", "SGND")

    def is_floor(self, net):
        """A net that can only set a FLOOR (rule V-1 (a) and (a')): a ground, a net declared at or below 0 V, a net the
        intent marks as a return (`returns`), or a declared net whose maximum is at most RETURN_V_MAX (the pack
        negative PACK_N at 0.05 V is a return 50 mV above ground, not a ceiling of 50 mV on every net a diode or a
        connector reaches; w5ident's second check, blocking item W5I-C2-B1)."""
        if self.is_ground(net): return True
        d = (self.rails.get(net) or self.nodes.get(net) or {})
        if d.get("returns"): return True
        w = self.declared(net)
        return bool(w) and "hi" in w and w["hi"] <= RETURN_V_MAX

    def touches_switch(self, net, but=None):
        """True when a transistor, a diode or an IC has a pin on the net (a node such a part can switch)."""
        return any(ref_class(r) in SWITCH and r != but for r, _ in self.by_net.get(net, ()))

    def is_ferrite(self, ref):
        return ref_class(ref) == "FB" or bool(re.search(r"ferrite|600R|bead", self.values.get(ref, ""), re.I))

    def pin_role(self, ref, pin):
        """(role, detail, entry) from PIN_ROLES for this pin, or None: role is input, output, tracks or unknown."""
        v = self.values.get(ref, "")
        for e in PIN_ROLES:
            if not re.search(e["part"], v): continue
            key = self.pinfn.get((ref, pin), "") if e["by"] == "pinfunction" else pin
            if key in e["inputs"]: return ("input", None, e)
            if key in e["outputs"]: return ("output", e["outputs"][key], e)
            if key in e["tracks"]: return ("tracks", e["tracks"][key], e)
            if key in e["unknown"]: return ("unknown", e["unknown"][key], e)
            return None
        return None

    def is_dead(self, net):
        return net.startswith("unconnected-")

    def bound(self, net):
        """(hi, lo, how) for a net: DECLARED, GROUND, BOUND (over every source that can set its level) or UNBOUNDED.

        Rule V-1 as corrected on 27 September 2026 (after the independent check of pass 1 found a ground pin
        bounding an IC's other pins at 0.0 V on 83 row-nets, and a boost's switch node reading its input rail).
        The undeclared, non-ground nets are joined into GROUPS by the parts that conduct between them (a resistor, a
        ferrite, a thermistor, a fuse, a switch's contacts, a link, a diode, an LED, a transistor that nothing
        declared sets, a pin a maker's document says tracks another). Every net of a group has the group's ceiling:
        the highest of all its SOURCES, and only when every source is bounded.
          (a) GROUND IS A FLOOR, NEVER A CEILING. A ground net, and a net the intent declares at or below 0 V, is left
              out of every ceiling: out of an active part's declared set (intent files declare GND at v_max 0, so an
              IC whose only declared pin was ground bounded its other pins at 0.0 V) and out of a group's sources (a
              node whose only DC path is a resistor to ground may still be driven by a pin nobody declared, or carry
              a swing a capacitor couples in). A group that only ground reaches is UNBOUNDED;
          (b) A SWITCH NODE IS DECLARED OR IT IS UNBOUNDED. An inductor (not a ferrite) with either node on a Q, D or
              U passes nothing: the node may swing past the supply behind the inductor (a boost's reaches its output)
              and ring above it. The project states its switch nodes in the intent (`nodes`, v_max the larger rail the
              node reaches, v_min -1.0 V, as the twenty LM5176 and buck nodes of board A are) and states NO ringing
              figure: derate.py and rule CMP-001 judge against the declared steady voltage and say so. So a declared
              switch node reads DECLARED, and an undeclared net with such an inductor on it, or on a net of its
              group, is UNBOUNDED and its capacitors' voltage requirement is an open item, never a guess;
          (c) a source of unknown level makes the whole group UNBOUNDED: an active part with no declared pin above
              0 V (it may drive the net anywhere), a pin rule V-2 reads as driven at an unstated level, or a net the
              intent declares with no maximum (board C's e-paper pump nodes, which the intent leaves to the panel
              maker's own bill of materials);
          (d) the floor is the lowest declared v_min among the sources and ground (0 V when none is negative);
          (e) a crystal and a capacitor are not DC sources;
          (f) rule V-2 (PIN_ROLES) replaces the premise for a pin whose maker's document gives its role.
        The premise that remains (an active part's pin stays within the highest declared voltage on its other pins)
        cannot see a pin above its own supply; such a net must be declared, or given a V-2 role."""
        if self.is_ground(net): return (0.0, 0.0, "GROUND")
        d = self.declared(net)
        if d and "hi" in d: return (d["hi"], d["lo"], "DECLARED")
        if not self._bound: self._groups()
        return self._bound.get(net, (None, None, "UNBOUNDED (not on the netlist)"))

    def _groups(self):
        free = [n for n in self.by_net if not self.is_ground(n) and not ("hi" in (self.declared(n) or {})) and not self.is_dead(n)]
        parent = {n: n for n in free}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]; x = parent[x]
            return x

        def join(x, y):
            rx, ry = find(x), find(y)
            if rx != ry: parent[rx] = ry

        src = collections.defaultdict(list)       # net -> [(hi, lo, label)], hi above 0 V: what can set a ceiling
        flo = collections.defaultdict(list)       # net -> [(lo, label)]: ground and nets at or below 0 V, a floor only
        unk = collections.defaultdict(list)       # net -> [label]: a source of unknown level
        swn = collections.defaultdict(list)       # net -> [label]: an inductor at a switchable node

        def reach(n, o, label, stop=False):
            """a conducting path from free net n to net o"""
            if self.is_dead(o): return
            if stop: swn[n].append("%s->%s" % (label, o)); return            # (b)
            if self.is_ground(o): flo[n].append((0.0, label + "->GND")); return   # (a)
            if self.is_floor(o):                                                   # (a'): a return is a floor
                flo[n].append(((self.declared(o) or {}).get("lo", 0.0), "%s->%s (a return, a floor only)" % (label, o))); return
            dd = self.declared(o)
            if dd and "hi" in dd:
                if dd["hi"] > 0.0: src[n].append((dd["hi"], dd["lo"], label + "->" + o))
                else: flo[n].append((dd["lo"], "%s->%s (declared at or below 0 V)" % (label, o)))   # (a)
                return
            join(n, o)

        for n in free:
            nd = self.nodes.get(n) or self.rails.get(n)
            if nd is not None and "hi" not in (self.declared(n) or {}):      # (c): declared, and with no maximum
                unk[n].append("the intent declares %s with no maximum%s" % (n, (": " + str(nd.get("basis"))[:140]) if nd.get("basis") else ""))
            for ref, pin in sorted(self.by_net.get(n, ())):
                pre = ref_class(ref)
                pins = self.on.get(ref, {})
                others = sorted({x for p_, x in pins.items() if x != n})
                if pre in PASSIVE_2T and len(pins) == 2:
                    for o in others:
                        stop = pre == "L" and not self.is_ferrite(ref) and (self.touches_switch(n, ref) or self.touches_switch(o, ref))
                        reach(n, o, ref, stop)
                    continue
                if pre in NOT_A_SOURCE: continue
                if pre in CONDUCTS:
                    for o in others: reach(n, o, ref)
                    continue
                role = self.pin_role(ref, pin)
                if role:
                    kind, detail, e = role
                    fnm = self.pinfn.get((ref, pin), pin)
                    if kind == "input": continue
                    if kind == "output":
                        src[n].append((detail[0], 0.0, "%s.%s (%s %s)" % (ref, fnm, e["cite"], detail[1].split(":")[0])))
                    elif kind == "tracks":
                        tn = sorted({x for p_, x in pins.items() if self.pinfn.get((ref, p_)) in detail[0]})
                        if not tn: unk[n].append("%s.%s tracks %s, not on the netlist" % (ref, fnm, "/".join(detail[0])))
                        for o in tn: reach(n, o, "%s.%s tracks %s (%s)" % (ref, fnm, self.pinfn.get((ref, [p_ for p_, x in pins.items() if x == o][0])), e["cite"]))
                    else:
                        unk[n].append("%s pin %s (%s): %s" % (ref, pin, e["cite"], detail))
                    continue
                if pre in CONNECTOR and not re.search(CONDUCTS_BY_VALUE, self.values.get(ref, ""), re.I):
                    # (g) a connector's pin is set by what is on the far side of it, which this board's intent does
                    # not state: a source of unknown level unless the net is declared (w5ident's second check, W5I-C2-B1
                    # part (b): ten capacitor rows and 92 resistor rows took a bound from a connector read as an active part)
                    unk[n].append("%s pin %s (a connector: its level is set on the far side; declare the net)" % (ref, pin))
                    continue
                decl = [self.declared(o) for o in others if not self.is_floor(o)]            # (a), (a'): floors left out
                decl = [x for x in decl if x.get("hi") is not None]
                if any(x["hi"] > 0.0 for x in decl):                                          # (a): and a 0 V net sets no ceiling
                    src[n].append((max(x["hi"] for x in decl), min([x.get("lo", 0.0) for x in decl] + [0.0]), "%s(%s)" % (ref, pre)))
                elif pre == "Q":
                    # (e) a transistor nothing declared sets switches its channel (D-S, C-E) together; its gate or base
                    # draws no DC and sets nothing on the net it sits on. Pins named otherwise are all joined.
                    fnm = self.pinfn.get((ref, pin), "")
                    if fnm in ("G", "B"): continue
                    ch = [x for p_, x in pins.items() if x != n and self.pinfn.get((ref, p_), "") not in ("G", "B")]
                    for o in sorted(set(ch)): reach(n, o, ref)
                elif pre == "J" and re.search(CONDUCTS_BY_VALUE, self.values.get(ref, ""), re.I):
                    for o in others: reach(n, o, ref + " (its far end conducts)")
                else:
                    unk[n].append("%s (%s with no declared pin above 0 V)" % (ref, pre))

        members = collections.defaultdict(list)
        for n in free: members[find(n)].append(n)
        for root, ns in members.items():
            S = [x for n in ns for x in src[n]]
            F = [x for n in ns for x in flo[n]]
            U = sorted({x for n in ns for x in unk[n]})
            W = sorted({x for n in ns for x in swn[n]})
            if U:
                ans = (None, None, "UNBOUNDED (a source of unknown level: %s)" % "; ".join(U[:3]))
            elif W:
                ans = (None, None, "UNBOUNDED (a possible switch node, %s: the intent declares switch nodes and no ringing figure, "
                                   "and this one is not declared)" % ", ".join(W[:3]))
            elif not S:
                if F:
                    cpl = sorted("%s->%s" % (r, x) for n in ns for r, _ in self.by_net.get(n, ()) if ref_class(r) == "C"
                                 for x in set(self.on.get(r, {}).values()) if x not in ns and not self.is_ground(x))
                    ans = (None, None, "UNBOUNDED (only ground reaches it, %s: ground is a floor, never a ceiling%s)"
                           % (", ".join(sorted({f[1] for f in F})[:3]), ("; AC-coupled through %s" % ", ".join(cpl[:3])) if cpl else ""))
                else:
                    ans = (None, None, "UNBOUNDED (no source on the node)")
            else:
                via = sorted({x[2] for x in S})
                ans = (max(x[0] for x in S), min([x[1] for x in S] + [f[0] for f in F] + [0.0]), "BOUND via " + ",".join(via[:4]))
            for n in ns: self._bound[n] = ans
        self._groups_of = {n: find(n) for n in free}
        self._bound.setdefault("__done__", (None, None, ""))

    def stress(self, ref):
        """(volts across the part, how) for a two-terminal part; None volts when a side is UNBOUNDED."""
        pins = self.on.get(ref, {})
        nets = sorted(set(pins.values()))
        if len(nets) < 2:
            n = nets[0] if nets else None
            if n is None: return (None, "no net")
            h, l, how = self.bound(n)
            return (None if h is None else abs(h), "one net %s (%s)" % (n, how))
        # a net that rides on another: the declared bias (derate.py's first rule)
        for a in nets:
            for b in nets:
                if a == b: continue
                na = self.nodes.get(a) or {}
                if na.get("rides_on") == b and na.get("bias_v") is not None:
                    return (float(na["bias_v"]), "DECLARED bias of %s over %s" % (a, b))
        worst, hows, unb = 0.0, [], False
        for i, a in enumerate(nets):
            for b in nets[i + 1:]:
                ha, la, wa = self.bound(a)
                hb, lb, wb = self.bound(b)
                if ha is None or hb is None:
                    unb = True; hows.append("%s %s / %s %s" % (a, wa, b, wb)); continue
                v = max(abs(ha - lb), abs(hb - la))
                worst = max(worst, v)
                hows.append("%s [%s] to %s [%s]" % (a, wa.split(" ")[0], b, wb.split(" ")[0]))
        if unb: return (None, "; ".join(hows) + "; a side UNBOUNDED")          # rule V-1 (c): a partial maximum is no bound
        return (worst, "; ".join(hows))

    def current(self, ref):
        """The current a SERIES element (a shunt, a link, an inductor, a ferrite) carries: the smaller declared peak of
        the two rails it joins, or the one declared rail's peak (amps_peak, else amps_typ); None when neither side
        declares a current. Used only for parts that are in series by their nature, never for a pull-up that
        merely touches a rail."""
        vals = []
        for n in set(self.on.get(ref, {}).values()):
            r = self.rails.get(n)
            if not r: continue
            a = r.get("amps_peak", r.get("amps_typ"))
            if a is not None: vals.append(float(a))
        return min(vals) if vals else None

    def declared_across(self, ref):
        """The steady voltage across a two-terminal part between a DECLARED net and GROUND (the net's own worst
        declared voltage), else None. Between two declared nets the voltage across depends on which is up first,
        so that case is not judged here (a sequencing question, not a steady one)."""
        nets = sorted(set(self.on.get(ref, {}).values()))
        if len(nets) != 2: return None
        g = [n for n in nets if self.is_ground(n)]
        o = [n for n in nets if not self.is_ground(n)]
        if len(g) != 1 or len(o) != 1: return None
        d = self.declared(o[0])
        if not d or "hi" not in d: return None
        return max(abs(d["hi"]), abs(d["lo"]))

    def neighbours(self, ref):
        """Prefixes of parts sharing a net with ref (for the crystal-load test)."""
        out = set()
        for n in set(self.on.get(ref, {}).values()):
            if self.is_ground(n): continue
            for r, _ in self.by_net.get(n, ()):
                if r != ref: out.add((ref_prefix(r), r, n))
        return out


# ------------------------------------------------------------------------------------------------ value parsing
SI = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "k": 1e3, "K": 1e3, "M": 1e6, "": 1.0, "R": 1.0}


def _num(s):
    return float(s)


def pkg_of(fp):
    m = re.search(r"_(0201|0402|0603|0805|1206|1210|1812|2010|2512)_", fp or "")
    return m.group(1) if m else None


def cap_value(v):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([pnuµ])(\d*)", v)
    if not m: return None
    val = float(m.group(1)) * SI[m.group(2)]
    if m.group(3): val += float("0." + m.group(3)) * SI[m.group(2)]
    return val


def res_value(v):
    s = v.strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(m\s*Ohm|mOhm|mΩ)", s, re.I)
    if m: return float(m.group(1)) * 1e-3
    m = re.match(r"^(\d+)m(\d*)\b", s)                 # "2m 2512" = 2 milliohm
    if m and not re.match(r"^\d+M", s):
        return float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) * 1e-3
    m = re.match(r"^(\d+)([RkKM])(\d+)\b", s)           # 60R4, 4k7
    if m: return float(m.group(1) + "." + m.group(3)) * SI[m.group(2)]
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(R|Ohm|Ω)?\s*([kKM])?(?![a-zA-Z])", s)
    if m:
        mult = SI[m.group(3)] if m.group(3) else 1.0
        return float(m.group(1)) * mult
    m = re.match(r"^(\d+(?:\.\d+)?)([kKM])", s)
    if m: return float(m.group(1)) * SI[m.group(2)]
    return None


def ind_value(v):
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*(n|u|µ)H", v)
    if not m: return None
    return float(m.group(1)) * SI[m.group(2)]


def fmt_si(x, unit):
    if x is None: return "?"
    if x == 0: return "0" + unit
    for mult, p in ((1e6, "M"), (1e3, "k"), (1.0, ""), (1e-3, "m"), (1e-6, "u"), (1e-9, "n"), (1e-12, "p")):
        if abs(x) >= mult * 0.9999:
            s = ("%.4g" % (x / mult))
            return s + p + unit
    return "%.3g%s" % (x, unit)


VOLT = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(k?)V\b")
TOL = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*%")
WATT = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*W\b")
PPM = re.compile(r"(\d+)\s*ppm")
DIEL = re.compile(r"\b(C0G|NP0|X7R|X5R|X7S|X6S|X8R)\b", re.I)
NAMED = [  # a value that names a maker's part: (regex, maker)
    (re.compile(r"\b(EEH[A-Z0-9]+)\b"), "Panasonic"),
    (re.compile(r"\b(35SVPF39M)\b"), "Panasonic"),
    (re.compile(r"\b(T520B227M006ATE025)\b"), "KEMET"),
    (re.compile(r"\b(LR2512-23R005F4)\b"), "RALEC"),
    (re.compile(r"\b(XAL\d{4}-\d{3}ME)[BCD]?\b"), "Coilcraft"),
    (re.compile(r"\b(ATNR4010100MT)\b"), "Arlitech Electronic Corp."),   # the maker PDi's EPD Driving Circuit Rev. 02 names (section 2, 'ARLITECH') and
    #                                                                     whose ATNR Series specification lists it (jlc-handfit.txt's 'Abracon' is finding W5I-F3)
    (re.compile(r"\b(SRF1260-1R5Y)\b"), "Bourns"),
]


def split_note(v):
    """The value's own words: the head and any parenthesised note (a function the generator states)."""
    notes = re.findall(r"\(([^()]*)\)", v)
    head = re.sub(r"\([^()]*\)", "", v).strip()
    return head, notes


def props(board, ref, value, fp, lcsc):
    """Every property this row states or the netlist gives, for the selection key."""
    pre = ref_prefix(ref)
    head, notes = split_note(value)
    fpname = fp.split(":")[-1] if fp else ""
    p = dict(board=board.letter, ref=ref, prefix=pre, value=value, footprint=fp, land=fpname, package=pkg_of(fpname),
             generator_lcsc=lcsc or "", notes=notes,
             nets_key="%s:%s" % (board.letter, "+".join(sorted(set(board.on.get(ref, {}).values())))))
    named = None
    for rx, maker in NAMED:
        m = rx.search(value)
        if m: named = (maker, m.group(1)); break
    p["named_part"] = list(named) if named else None
    if pre == "C":
        p["kind"] = "capacitor"
        p["farads"] = cap_value(head)
        vs = [float(a) * (1000.0 if k else 1.0) for a, k in VOLT.findall(head)]
        p["v_stated"] = min(vs) if vs else None
        dm = DIEL.search(head)
        diel = dm.group(1).upper() if dm else None
        if diel == "NP0": diel = "C0G"
        p["dielectric_stated"] = diel
        tm = TOL.search(head)
        p["tol_stated"] = float(tm.group(1)) if tm else None
        if re.search(r"polymer", value, re.I) and re.search(r"tantalum", value, re.I): p["construction"] = "polymer tantalum"
        elif re.search(r"hybrid polymer", value, re.I): p["construction"] = "hybrid polymer aluminium"
        elif re.search(r"polymer", value, re.I): p["construction"] = "polymer aluminium"
        elif fpname.startswith("CP_"): p["construction"] = "electrolytic"
        else: p["construction"] = "MLCC"
        v, how = board.stress(ref)
        p["v_across"] = v; p["v_across_how"] = how
        nb = board.neighbours(ref)
        p["crystal_load"] = any(x[0] == "Y" for x in nb)
    elif pre == "R":
        p["kind"] = "resistor"
        p["ohms"] = res_value(head)
        tm = TOL.search(head)
        p["tol_stated"] = float(tm.group(1)) if tm else None
        wm = WATT.search(head)
        p["p_stated"] = float(wm.group(1)) if wm else None
        pm = PPM.search(head)
        p["tcr_stated"] = int(pm.group(1)) if pm else None
        v, how = board.stress(ref)
        p["v_across"] = v; p["v_across_how"] = how
        p["amps_rail"] = board.current(ref)
        text = value.lower()
        if p["ohms"] == 0.0: p["res_kind"] = "zero-ohm link"
        elif p["ohms"] is not None and p["ohms"] < 1.0: p["res_kind"] = "current sense"     # a shunt is below an ohm; "CS filter" and "HCSL shunt Rp" are not shunts
        else: p["res_kind"] = "general"
        p["v_declared_across"] = board.declared_across(ref)
    elif pre in ("L", "FB"):
        p["kind"] = "inductor"
        p["henries"] = ind_value(head)
        if re.search(r"ferrite|600R", value, re.I): p["ind_kind"] = "ferrite bead"
        elif re.search(r"choke", value, re.I): p["ind_kind"] = "common-mode choke"
        elif re.search(r"XAL|ATNR|boost inductor|Isat", value): p["ind_kind"] = "power inductor"
        elif p["henries"] is not None and p["henries"] < 1e-6: p["ind_kind"] = "RF inductor"
        else: p["ind_kind"] = "inductor"
        am = re.search(r"(\d+(?:\.\d+)?)\s*A\b", head)
        p["amps_stated"] = float(am.group(1)) if am else None
        p["amps_rail"] = board.current(ref)
    else:
        p["kind"] = "other"
        if pre == "F":
            # rule F-1: a fuse is its rated current (the value states it) and the voltage it must interrupt, which is the
            # highest the netlist and the intent put on either of its nets (the fuse's voltage rating is compared with
            # it; an UNBOUNDED side leaves the requirement open)
            am = re.search(r"(\d+(?:\.\d+)?)\s*A\b", head)
            p["fuse_amps"] = float(am.group(1)) if am else None
            his, hows = [], []
            for n in sorted(set(board.on.get(ref, {}).values())):
                h, l, how = board.bound(n)
                hows.append("%s %s" % (n, how.split(" (")[0] if how.startswith("UNBOUNDED") else how.split(" ")[0]))
                his.append(h)
            p["v_circuit_max"] = None if (not his or any(h is None for h in his)) else max(abs(h) for h in his)
            p["v_circuit_how"] = "; ".join(hows)
    return p


def std_ceil(x, table):
    for s in table:
        if s >= x - 1e-9: return s
    return None


def requirements(p):
    """The properties that decide the part, each with where it came from. The selection key is built from these."""
    req = collections.OrderedDict()
    why = {}
    if p["kind"] == "capacitor":
        req["value"] = fmt_si(p["farads"], "F")
        req["package"] = p["package"] or p["land"]
        req["construction"] = p["construction"]
        if p["named_part"]:
            req["named_part"] = "%s %s" % tuple(p["named_part"])
        # dielectric
        if p["construction"] == "MLCC":
            if p["dielectric_stated"]:
                req["dielectric"] = p["dielectric_stated"]; why["dielectric"] = "stated"
            elif p["crystal_load"]:
                req["dielectric"] = "C0G"; why["dielectric"] = "rule C-D1: a crystal's load capacitor (a crystal shares its net)"
            elif (p["farads"] or 0) <= 1.0e-9 + 1e-15 and (p["package"] or "") in ("0201", "0402", "0603", "0805"):
                req["dielectric"] = "C0G"; why["dielectric"] = "rule C-D2: 1 nF and below on a signal-size land (0805 and smaller), unstated"
            else:
                req["dielectric"] = "X7R"; why["dielectric"] = "rule C-D3: class 2 (above 1 nF, or a 1206 or larger land), unstated; X7R, X8R or C0G accepted; X5R only where stated or by rule C-D3b"
        # voltage rating
        need = None
        if p["v_across"] is not None:
            need = std_ceil(p["v_across"] * (1.0 + DERATE_MARGIN), STD_V)
        vs = p["v_stated"]
        bounded = "BOUND" in (p["v_across_how"] or "") or "UNBOUNDED" in (p["v_across_how"] or "")
        if vs is not None:
            req["v_rating_min"] = vs
            why["v_rating_min"] = "stated"
            if need is None:
                # rule V-1 (c): the stated rating stands (a stated rating is never lowered), but nothing here proves it.
                # Rule K-1: a rating that is checked and one that is not are not known to be the same requirement, so
                # the unchecked rows are their own selection, shared only across the same nets of one board
                why["v_rating_min"] += "; NOT CHECKED: a side is UNBOUNDED (%s)" % p["v_across_how"]
                p.setdefault("findings", []).append("V_UNBOUNDED")
                req["v_not_checked_on"] = p["nets_key"]
                why["v_not_checked_on"] = "rule K-1: a stated rating nothing checks is shared only by parts across the same nets of one board"
            if need is not None and need > vs:
                if bounded:
                    why["v_rating_min"] += "; the conservative BOUND on its nets (%.1f V) would need %g V: open until the net is declared" % (p["v_across"], need)
                    p.setdefault("findings", []).append("V_BOUND_ABOVE_STATED")
                else:
                    req["v_rating_min"] = need
                    why["v_rating_min"] = "DECLARED %.1f V across it needs %g V at the 20 percent margin, above the stated %g V (CMP-001 finding)" % (p["v_across"], need, vs)
                    p.setdefault("findings", []).append("V_DECLARED_ABOVE_STATED")
        elif need is not None:
            req["v_rating_min"] = max(need, 6.3)
            why["v_rating_min"] = "derived: %.2f V across it (%s) at the 20 percent margin" % (p["v_across"], "BOUND" if bounded else "DECLARED")
        else:
            req["v_rating_min"] = None
            why["v_rating_min"] = "UNRESOLVED: a side of the part is UNBOUNDED (%s)" % p["v_across_how"]
            p.setdefault("findings", []).append("V_UNBOUNDED")
            # rule K-1: two rows whose requirement is UNKNOWN are not known to share it. They are one selection only
            # where they sit across the same nets of the same board (whatever that voltage is, it is one voltage).
            req["v_open_on"] = p["nets_key"]
            why["v_open_on"] = "rule K-1: an open requirement is shared only by parts across the same nets of one board"
        # tolerance
        if p["tol_stated"] is not None:
            req["tolerance_max_pct"] = p["tol_stated"]; why["tolerance_max_pct"] = "stated"
        elif p["construction"] != "MLCC":
            req["tolerance_max_pct"] = 20.0; why["tolerance_max_pct"] = "rule C-T3: bulk polymer/electrolytic, unstated"
        elif req.get("dielectric") == "C0G":
            req["tolerance_max_pct"] = 5.0; why["tolerance_max_pct"] = "rule C-T1: class 1, unstated"
        elif (p["farads"] or 0) >= 10e-6 - 1e-12:
            req["tolerance_max_pct"] = 20.0; why["tolerance_max_pct"] = "rule C-T2: class 2 at 10 uF and above, unstated"
        else:
            req["tolerance_max_pct"] = 10.0; why["tolerance_max_pct"] = "rule C-T2: class 2 below 10 uF, unstated"
    elif p["kind"] == "resistor":
        req["value"] = fmt_si(p["ohms"], "Ohm")
        req["package"] = p["package"] or p["land"]
        req["resistor_kind"] = p["res_kind"]
        if p["named_part"]: req["named_part"] = "%s %s" % tuple(p["named_part"])
        if p["res_kind"] == "zero-ohm link":
            req["tolerance_max_pct"] = None; why["tolerance_max_pct"] = "a link has none"
        elif p["tol_stated"] is not None:
            req["tolerance_max_pct"] = p["tol_stated"]; why["tolerance_max_pct"] = "stated"
        else:
            req["tolerance_max_pct"] = 5.0; why["tolerance_max_pct"] = "rule R-T1: unstated, 5 percent (the widest standard thick-film grade)"
        if p["tcr_stated"] is not None:
            req["tcr_max_ppm"] = p["tcr_stated"]; why["tcr_max_ppm"] = "stated"
        elif p["res_kind"] == "current sense":
            req["tcr_max_ppm"] = 200; why["tcr_max_ppm"] = "rule R-S1: a shunt below 1 ohm, unstated: at most 200 ppm/K, so its reading moves at most 1.6 percent over an 80 K swing"
        # dissipation. A shunt and a link are series elements and carry the declared rail current (I^2 R); a general
        # resistor is rated as stated or at its package's standard rating, and that rating is CHECKED against V^2/R
        # only where both of its nets are declared or ground (an exact bound). A general resistor whose voltage is
        # only a BOUND is not judged on power here: the bound is too loose to say anything (a filter resistor between
        # two nodes at one rail reads the whole rail across it), and the selection says so.
        o = p["ohms"]; pkg_p = PKG_P.get(p["package"] or "", None)
        pb, how = None, None
        if p["res_kind"] == "current sense" and o and p["amps_rail"] is not None:
            pb, how = p["amps_rail"] ** 2 * o, "I^2 R at the declared %.2f A" % p["amps_rail"]
        elif p["res_kind"] == "general" and o and p["v_declared_across"] is not None:
            pb, how = p["v_declared_across"] ** 2 / o, "V^2/R at %.2f V, a DECLARED net to ground" % p["v_declared_across"]
        p["p_bound"] = pb; p["p_bound_how"] = how
        if p["res_kind"] == "zero-ohm link":
            req["power_min_w"] = None
            req["link_current_min_a"] = p["amps_rail"]
            why["link_current_min_a"] = ("the declared rail peak %.2f A" % p["amps_rail"]) if p["amps_rail"] is not None else "no current declared on its nets: a signal link"
        elif p["res_kind"] == "current sense":
            if pb is not None:
                need = std_ceil(POWER_FACTOR * pb, STD_P) or POWER_FACTOR * pb
                req["power_min_w"] = max(need, p["p_stated"] or 0.0)
                why["power_min_w"] = "derived: %.3g W (%s), rule R-P twice%s" % (pb, how, "; stated %g W" % p["p_stated"] if p["p_stated"] else "")
            else:
                req["power_min_w"] = p["p_stated"] if p["p_stated"] is not None else pkg_p
                why["power_min_w"] = ("stated" if p["p_stated"] is not None else "the package's standard rating") + "; UNDERIVED: no current declared on its nets"
                p.setdefault("findings", []).append("P_UNDERIVED")
        else:
            req["power_min_w"] = p["p_stated"] if p["p_stated"] is not None else pkg_p
            why["power_min_w"] = "stated" if p["p_stated"] is not None else "rule R-P0: the package's standard rating"
            if pb is not None:
                if POWER_FACTOR * pb > (req["power_min_w"] or 0) + 1e-12:
                    p.setdefault("findings", []).append("P_NOT_PROVED_AT_DECLARED_MAX")
                    why["power_min_w"] += "; NOT PROVED: %.3g W (%s) at twice is above it; the declared maximum is a bound, the steady voltage may be lower" % (pb, how)
                else:
                    why["power_min_w"] += "; checked: %.3g W (%s) at twice is inside it" % (pb, how)
            else:
                why["power_min_w"] += "; not checked (no exact voltage across it)"
        vmax = p["v_across"]
        req["v_working_bound"] = None if vmax is None else round(vmax, 2)
        why["v_working_bound"] = p["v_across_how"]
        if vmax is None:
            why["v_working_bound"] += "; the part's working voltage is NOT CHECKED on this row"
            p.setdefault("findings", []).append("V_UNBOUNDED")
    elif p["kind"] == "inductor":
        req["ind_kind"] = p["ind_kind"]
        req["land"] = p["land"]
        if p["named_part"]:
            req["named_part"] = "%s %s" % tuple(p["named_part"])
        else:
            req["value"] = fmt_si(p["henries"], "H") if p["henries"] is not None else re.sub(r"\s+", " ", split_note(p["value"])[0])
            if p["amps_stated"] is not None: req["current_min_a"] = p["amps_stated"]; why["current_min_a"] = "stated"
            elif p["amps_rail"] is not None: req["current_min_a"] = p["amps_rail"]; why["current_min_a"] = "the declared rail peak"
        req["use"] = "; ".join(p["notes"]) if p["notes"] else None
    else:
        req["value"] = p["value"]
        req["land"] = p["land"]
        if p["prefix"] == "F":
            req["fuse_current_a"] = p.get("fuse_amps")
            why["fuse_current_a"] = "stated in the value" if p.get("fuse_amps") is not None else "the value states no current"
            req["fuse_voltage_min_v"] = None if p.get("v_circuit_max") is None else round(p["v_circuit_max"], 2)
            why["fuse_voltage_min_v"] = "rule F-1: the highest voltage on its nets (%s)" % p.get("v_circuit_how")
            if p.get("v_circuit_max") is None:
                p.setdefault("findings", []).append("V_UNBOUNDED")
                req["v_open_on"] = p["nets_key"]; why["v_open_on"] = "rule K-1: an open requirement is shared only by parts across the same nets of one board"
    p["requirements"] = req
    p["requirement_basis"] = why
    return p


def key_of(p):
    r = p["requirements"]
    parts = [p["prefix"] if p["kind"] == "other" else p["kind"]]
    for k, v in r.items():
        if k in ("v_working_bound",): continue
        if k == "use" and p["kind"] == "inductor" and r.get("named_part"): continue
        parts.append("%s=%s" % (k, "" if v is None else (("%g" % v) if isinstance(v, float) else v)))
    return "|".join(parts)


def rows(boards=None, check_sha=True):
    """The per-reference rows of the named boards (default: every board in BOARDS), read from the COMMITTED NETLIST:
    every part the generator wrote that the schematic does not mark exclude_from_bom, with its value, land and order
    code as the netlist carries them (stream w5identc, 29 September 2026). The per-reference BOM export is COMPARED,
    never trusted: at b874b744 board C's export predates set 7's R50 and R51, set 12's R52 and D23, set 13's R53 to R56
    and R14's change of value, so rows read from it would miss eight parts. `meta` records the comparison per board.
    `check_sha` is kept for the call shape of w5ident's tool and has no effect: the netlist is the source now."""
    out, meta = [], []
    want = [b for b in BOARDS if boards is None or b[0] in boards]
    for letter, phase, stem in want:
        b = Board(letter, phase, stem)
        bom_rows = {}
        if os.path.exists(b.bom_path):
            for r in csv.DictReader(open(b.bom_path, encoding="utf-8")):
                if (r.get("DNP") or "").strip(): continue
                bom_rows[r["Reference"].rstrip("?")] = r      # KiCad's trailing "?" on a reference it left open
        mine = sorted(r for r in b.comps if r not in b.bom_excluded)
        diffs = []
        for ref in mine:
            e = bom_rows.get(ref)
            if e is None: diffs.append("%s is in the netlist and not in the BOM export" % ref); continue
            if e["Value"] != b.values[ref]: diffs.append("%s: the BOM export says %r, the netlist %r" % (ref, e["Value"], b.values[ref]))
            if e["Footprint"] != b.footprints[ref]: diffs.append("%s: the BOM export's land %r, the netlist's %r" % (ref, e["Footprint"], b.footprints[ref]))
        for ref in sorted(set(bom_rows) - set(mine)): diffs.append("%s is in the BOM export and not a BOM part of the netlist" % ref)
        meta.append(dict(board=letter, phase=phase, netlist=os.path.relpath(b.net_path, REPO), netlist_sha256=sha256(b.net_path),
                         intent=os.path.relpath(b.intent_path, REPO), intent_sha256=sha256(b.intent_path),
                         bom_export=os.path.relpath(b.bom_path, REPO),
                         bom_export_sha256=sha256(b.bom_path) if os.path.exists(b.bom_path) else None,
                         bom_export_agrees=not diffs, bom_export_differences=diffs,
                         rows=len(mine), excluded_from_bom=len(b.bom_excluded)))
        for ref in mine:
            p = props(b, ref, b.values[ref], b.footprints[ref], b.lcsc.get(ref, ""))
            requirements(p)
            p["key"] = key_of(p)
            out.append(p)
    return out, meta


def selections(rs):
    sel = collections.OrderedDict()
    for p in sorted(rs, key=lambda p: (p["key"], p["board"], p["ref"])):
        s = sel.setdefault(p["key"], dict(key=p["key"], kind=p["kind"], prefix=p["prefix"], requirements=p["requirements"],
                                          basis=collections.OrderedDict(), rows=[], values=set(), lands=set(),
                                          generator_lcsc=set(), findings=set(), finding_rows=collections.OrderedDict(),
                                          v_across_max=None, p_bound_max=None))
        s["rows"].append("%s:%s" % (p["board"], p["ref"]))
        for f in p.get("findings", []): s["finding_rows"].setdefault(f, []).append("%s:%s" % (p["board"], p["ref"]))
        s["values"].add(p["value"]); s["lands"].add(p["land"])
        if p["generator_lcsc"]: s["generator_lcsc"].add(p["generator_lcsc"])
        for f in p.get("findings", []): s["findings"].add(f)
        for k, v in p["requirement_basis"].items(): s["basis"].setdefault(k, set()).add(v)
        if p.get("v_across") is not None:
            s["v_across_max"] = p["v_across"] if s["v_across_max"] is None else max(s["v_across_max"], p["v_across"])
        if p.get("p_bound") is not None:
            s["p_bound_max"] = p["p_bound"] if s["p_bound_max"] is None else max(s["p_bound_max"], p["p_bound"])
    return sel


def selection_id(key):
    return "S-" + hashlib.sha256(key.encode()).hexdigest()[:10]


def _jsonable(o):
    if isinstance(o, set): return sorted(o)
    return str(o)


def load_table(path=TABLE):
    import yaml
    return yaml.safe_load(open(path))


# ------------------------------------------------------------------------------------------------ rule D-2
STATUSES = ("RESOLVED", "UNRESOLVED", "NOT_A_PART")
REASONS = ("DOCUMENT_OWED", "DOCUMENT_DOES_NOT_NAME_THE_PART", "REQUIREMENT_OPEN", "CHOICE_OWED", "PART_NUMBER_INFERRED",
           "PART_DOES_NOT_MEET_THE_REQUIREMENT")


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.parts, self._skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"): self._skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self._skip: self._skip -= 1

    def handle_data(self, data):
        if not self._skip: self.parts.append(data)


def page_count(path):
    """The pages of a PDF (pdfinfo); an HTML page is one page."""
    if not path.lower().endswith(".pdf"): return 1
    if not shutil.which("pdfinfo"): raise RuntimeError("pdfinfo is not on this host: a document cannot be read")
    out = subprocess.run(["pdfinfo", path], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("Pages:"): return int(line.split()[1])
    raise RuntimeError("pdfinfo gives no page count for %s" % path)


def page_text(path, page):
    """The text layer of one page of a held document: a PDF through pdftotext -layout (the project's reader, as
    pack_protection.py and the rails census use it), an HTML page through the standard library's parser. A page with
    no text layer returns empty text, which names nothing."""
    if path.lower().endswith((".html", ".htm")):
        if page != 1: return ""
        p = _Text(); p.feed(open(path, encoding="utf-8", errors="replace").read()); return " ".join(p.parts)
    if not shutil.which("pdftotext"): raise RuntimeError("pdftotext is not on this host: a document cannot be read")
    return subprocess.run(["pdftotext", "-f", str(page), "-l", str(page), "-layout", path, "-"],
                          capture_output=True, text=True).stdout


def names_part(text, mpn):
    """(True, the line) when the text names the part number exactly, letter case aside and nothing else: the characters
    before and after it are not letters or digits, so ABC12 does not name ABC123 and ABC123 does not name ABC12, and a
    series sheet that prints an ordering scheme (CC0603 x R NPO 9 B N ...) and not the part number names nothing."""
    if not mpn: return (False, None)
    rx = re.compile(r"(?<![A-Za-z0-9])" + re.escape(mpn) + r"(?![A-Za-z0-9])", re.I)
    for line in text.splitlines():
        if rx.search(line): return (True, " ".join(line.split())[:200])
    return (False, None)


def find_pages(path, mpn, limit=5):
    """The pages of a held document whose text layer names the part number (rule D-2), first `limit`."""
    got = []
    for pg in range(1, page_count(path) + 1):
        ok, _ = names_part(page_text(path, pg), mpn)
        if ok:
            got.append(pg)
            if len(got) >= limit: break
    return got


# ------------------------------------------------------------------------------------------------ rule D-2, DECODED
# A DECODED binding (the session's decision of 29 September 2026, drafted for pcb_decisions.yaml by stream w5identc):
# the maker's own ordering-code table, one page cited, decodes the part number field by field. Never counted as PRINTED.
DISTRIBUTORS = ("LCSC", "SZLCSC", "JLCPCB", "MOUSER", "DIGI-KEY", "DIGIKEY", "FARNELL", "NEWARK", "ARROW", "TME",
                "RS COMPONENTS", "AVNET", "FUTURE ELECTRONICS", "OCTOPART")
MEANING_KINDS = ("tolerance", "voltage", "power", "packaging", "quantity", "special")   # code = meaning, read in the row
LITERAL_KINDS = ("series", "process", "literal")                                        # a code the scheme prints as is
DIELECTRIC_ACCEPTS = {"X7R": ("X7R", "X8R", "C0G"), "C0G": ("C0G",), "X5R": ("X5R", "X7R", "X8R", "C0G"),
                      "X7S": ("X7S", "X7R", "X8R", "C0G"), "X6S": ("X6S", "X7R", "X8R", "C0G")}
_POW = {"J": -1, "K": -2, "L": -3, "M": -4, "N": -5, "P": -6}


def _flat(text):
    return " ".join(str(text).split())


def _alnum(s):
    return re.sub(r"[^A-Z0-9]", "", str(s).upper())


def _token(code, row):
    return re.search(r"(?<![A-Za-z0-9])" + re.escape(code) + r"(?![A-Za-z0-9])", row) is not None


def _pct(s):
    m = re.search(r"±\s*(\d+(?:\.\d+)?)\s*%", s)
    return float(m.group(1)) if m else None


def _volts(s):
    m = re.search(r"(\d+(?:\.\d+)?)\s*V\b", s)
    return float(m.group(1)) if m else None


def _watts(s):
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*W", s)
    if m: return float(m.group(1)) / float(m.group(2))
    m = re.search(r"(\d+(?:\.\d+)?)\s*W\b", s)
    return float(m.group(1)) if m else None


def _req_value(req):
    """The requirement's value as a number (farads, ohms): the table writes it with fmt_si ('100nF', '10kOhm')."""
    m = re.match(r"^(\d+(?:\.\d+)?)([pnumkM]?)(F|Ohm|H)$", str(req.get("value") or ""))
    if not m: return None
    mult = {"p": 1e-12, "n": 1e-9, "u": 1e-6, "m": 1e-3, "k": 1e3, "M": 1e6, "": 1.0}[m.group(2)]
    return float(m.group(1)) * mult


def _decode_value(code, rule):
    """(value, the table words the rule needs on its rows): pf_2sig (two significant digits and the number of zeros, in
    pF, R the decimal point), ohm_3sig (three significant digits and a power of ten, J K L ... negative powers)."""
    if rule == "pf_2sig":
        if "R" in code: return float(code.replace("R", ".")) * 1e-12
        if not re.match(r"^\d{3}$", code): return None
        return int(code[:2]) * 10 ** int(code[2]) * 1e-12
    if rule == "ohm_3sig":
        if not re.match(r"^\d{3}[0-9JKLMNP]$", code): return None
        p = int(code[3]) if code[3].isdigit() else _POW[code[3]]
        return int(code[:3]) * 10.0 ** p
    return None


# THE SCHEMES a DECODED binding may cite, written here in the tool (a table cannot edit one): the maker's document by its
# sha256 and page, the kind of part the scheme orders, and how the page lays the part number out. The layout is READ from
# the page each time: Yageo prints a scheme row whose placeholders are numbered by labels "(1) SIZE" to "(5) CAPACITANCE
# VALUE"; Uniroyal numbers its code positions ("1st~4th codes: Part name." to "14th code: Special features."). The tool
# slices the part number by that layout, so a field out of order, a padding character or a missing field is refused.
SCHEMES = {
    "yageo-cc-x7r-v26-p2": dict(
        sha256="61a606825ab314ea318cfb5362848a62fdffb851efa9818d642e9a541c56a648", page=2, kind="capacitor",
        maker_mark="YAGEO", layout="numbered_placeholders", scheme_row="CC XXXX X X X7R X BB XXX",
        labels={"SIZE": "size", "TOLERANCE": "tolerance", "PACKING STYLE": "packaging", "RATED VOLTAGE": "voltage",
                "CAPACITANCE VALUE": "value"},
        literals={"CC": "series", "X7R": "dielectric", "BB": "process"}, section_end="NOTE",
        construction=("MLCC", "Ceramic Multilayer Capacitors"), value_rule="pf_2sig"),
    "uniroyal-thick-film-p2": dict(
        sha256="11cd644d5d8a34a6d12775afb80bf58d8fc11f0c3b700dbd0f7a59942ceaa5ef", page=2, kind="resistor",
        resistor_kinds=("general",), maker_mark="UNI-ROYAL", layout="numbered_positions",
        labels={"Part name": "size", "Power rating": "power", "Tolerance": "tolerance", "Resistance Value": "value",
                "Packaging Type": "packaging", "Standard Packing Quantity": "quantity", "Special features": "special"},
        section_end="3. Ordering Procedure", value_rule="ohm_3sig"),
}
CAP_KEYS = {"value", "package", "construction", "dielectric", "v_rating_min", "tolerance_max_pct", "v_open_on", "v_not_checked_on"}
RES_KEYS = {"value", "package", "resistor_kind", "tolerance_max_pct", "power_min_w", "v_working_bound"}
MUST = {"capacitor": ("value", "package", "tolerance", "voltage", "dielectric", "construction"),
        "resistor": ("value", "package", "tolerance", "power")}
_ORD = r"(\d+)(?:st|nd|rd|th)"


def scheme_slots(sc, flat):
    """[(kind, width, literal or None)] in the order the page lays the part number out, read from the page; or a
    string saying why the page does not give the layout."""
    if sc["layout"] == "numbered_placeholders":
        if sc["scheme_row"] not in flat: return "the scheme row %r is not on the page" % sc["scheme_row"]
        out, k = [], 0
        for tok in sc["scheme_row"].split():
            if set(tok) == {"X"}:
                k += 1
                found = [lab for lab in sc["labels"] if "(%d) %s" % (k, lab) in flat]
                if len(found) != 1: return "placeholder %d of the scheme row has %s label on the page" % (k, "no" if not found else "more than one")
                out.append((sc["labels"][found[0]], len(tok), None, "(%d) %s" % (k, found[0])))
            elif tok in sc["literals"]:
                out.append((sc["literals"][tok], len(tok), tok, None))
            else:
                return "the scheme row's token %r is neither a placeholder nor a known literal" % tok
        return out
    if sc["layout"] == "numbered_positions":
        m = re.search(r"Part No\. includes (\d+) codes", flat)
        if not m: return "the page does not state how many codes the part number has"
        total, spans = int(m.group(1)), []
        for lab, kind in sc["labels"].items():
            m = re.search(_ORD + r"(?:~" + _ORD + r")? codes?: " + re.escape(lab) + r"\.", flat)
            if not m: return "the page does not give the position of %r" % lab
            a = int(m.group(1)); b = int(m.group(2)) if m.group(2) else a
            spans.append((a, b, kind, m.group(0)))
        spans.sort()
        pos = 1
        for a, b, kind, _lab in spans:
            if a != pos: return "the page's positions leave a gap or overlap at code %d" % pos
            pos = b + 1
        if pos != total + 1: return "the page's positions cover %d codes where it says %d" % (pos - 1, total)
        return [(kind, b - a + 1, None, lab) for a, b, kind, lab in spans]
    return "the scheme's layout %r is unknown" % sc["layout"]


def read_decoded(ds, mpn, maker, req, kind, text, first_page_text, doc_sha256):
    """Rule D-2's DECODED binding (decision 59) read on the cited page. Returns (state, why, detail)."""
    flat = _flat(text)
    sc = SCHEMES.get(ds.get("scheme"))
    if sc is None: return ("REFUSED", "the scheme %r is not one this tool knows" % ds.get("scheme"), {})
    if doc_sha256 != sc["sha256"] or int(ds.get("page") or 0) != sc["page"]:
        return ("REFUSED", "the scheme %s is written for another document or page" % ds["scheme"], {})
    pub = str(ds.get("publisher") or "")
    mark = sc["maker_mark"]
    if not pub: return ("REFUSED", "a DECODED binding names its publisher", {})
    if any(d in pub.upper() for d in DISTRIBUTORS):
        return ("REFUSED", "the publisher %r is a distributor: a distributor's page is not the maker's document" % pub, {})
    if _alnum(mark) not in _alnum(maker) or _alnum(mark) not in _alnum(pub):
        return ("REFUSED", "the maker's mark %r is not the identity's maker %r and the publisher %r" % (mark, maker, pub), {})
    both = (flat + " " + _flat(first_page_text)).upper()
    if mark.upper() not in both:
        return ("REFUSED", "neither the cited page nor page 1 prints the maker's mark %r" % mark, {})
    dist = [d for d in DISTRIBUTORS if re.search(r"(?<![A-Z])" + re.escape(d) + r"(?![A-Z])", both)]
    if dist: return ("REFUSED", "the document prints a distributor's name (%s): a distributor's page, not the maker's" % ", ".join(dist), {})
    # the kind: a capacitor scheme only for a capacitor selection, and nothing the kind does not know
    if kind != sc["kind"]:
        return ("REFUSED", "a %s scheme cannot resolve a %s selection" % (sc["kind"], kind), {})
    known = CAP_KEYS if kind == "capacitor" else RES_KEYS
    extra = sorted(k for k, v in (req or {}).items() if v is not None and k not in known)
    if extra: return ("REFUSED", "the selection has deciding properties the scheme cannot decode: %s" % ", ".join(extra), {})
    if kind == "resistor" and req.get("resistor_kind") not in sc["resistor_kinds"]:
        return ("REFUSED", "the scheme orders %s resistors, the selection is %s" % ("/".join(sc["resistor_kinds"]), req.get("resistor_kind")), {})
    # the layout, read from the page, and the part number sliced by it: whole, in order, nothing left over
    slots = scheme_slots(sc, flat)
    if isinstance(slots, str): return ("REFUSED", slots, {})
    if len(mpn) != sum(x[1] for x in slots):
        return ("REFUSED", "%s has %d characters where the page's layout gives %d" % (mpn, len(mpn), sum(x[1] for x in slots)), {})
    # each coded position's rows must lie in that position's own part of the page: from its label to the next label
    # (or the scheme's section end), so a row of another position cannot stand in for it
    starts = sorted(flat.index(x[3]) for x in slots if x[3])
    end_all = flat.find(sc["section_end"], max(starts)) if sc.get("section_end") else -1
    end_all = end_all if end_all > 0 else len(flat)
    def segment(label):
        a = flat.index(label)
        later = [b for b in starts if b > a]
        return flat[a:(later[0] if later else end_all)]
    fields = ds.get("fields") or []
    if len(fields) != len(slots):
        return ("REFUSED", "%d fields for the page's %d positions" % (len(fields), len(slots)), {})
    got, pos = {}, 0
    for (skind, width, lit, label), f in zip(slots, fields):
        piece = mpn[pos:pos + width]; pos += width
        code = str(f.get("code"))
        if f.get("field") != skind: return ("REFUSED", "position %d is %s on the page, the binding says %s" % (pos - width + 1, skind, f.get("field")), {})
        if code.upper() != piece.upper(): return ("REFUSED", "the %s position of %s is %r, the binding says %r" % (skind, mpn, piece, code), {})
        if lit is not None and piece.upper() != lit.upper(): return ("REFUSED", "the %s position must be %r and is %r" % (skind, lit, piece), {})
        if lit is None and skind != "value":
            row = _flat(f.get("row") or "")
            if not row or row not in flat: return ("REFUSED", "field %s (%s): its row %r is not on the cited page" % (skind, code, f.get("row")), {})
            if row not in segment(label): return ("REFUSED", "field %s (%s): its row is not under the page's %r" % (skind, code, label), {})
            if not _token(code, row): return ("REFUSED", "field %s: the code %r is not in its row %r" % (skind, code, row), {})
            if skind in MEANING_KINDS:
                means = _flat(f.get("means") or "")
                if not means or not re.search(r"(?<![A-Za-z0-9])" + re.escape(code) + r"\s*[=:：]?\s*" + re.escape(means), row):
                    return ("REFUSED", "field %s: the row does not map %r to %r" % (skind, code, means), {})
                if skind == "tolerance": got["tolerance_pct"] = _pct(means)
                if skind == "voltage": got["volts"] = _volts(means)
                if skind == "power": got["watts"] = _watts(means)
            if skind == "size": got["package"] = piece
        if skind == "dielectric": got["dielectric"] = piece.upper().replace("NP0", "C0G")
        if skind == "value":
            for r in [f.get("row")] + ([f["means_row"]] if f.get("means_row") else []):
                if not r or _flat(r) not in flat: return ("REFUSED", "field value: its row %r is not on the cited page" % r, {})
                if _flat(r) not in segment(label): return ("REFUSED", "field value: its row is not under the page's %r" % label, {})
            v = _decode_value(piece, sc["value_rule"])
            if v is None: return ("REFUSED", "field value: %r does not decode by the rule %r" % (piece, sc["value_rule"]), {})
            need = {"pf_2sig": "significant digits", "ohm_3sig": "significant figures"}[sc["value_rule"]]
            if need not in _flat(f["row"]).lower(): return ("REFUSED", "field value: its row does not state the rule (%r)" % need, {})
            if sc["value_rule"] == "ohm_3sig":
                p = piece[3]
                pw = ("%s=10%s" % (p, p)) if p.isdigit() else ("%s=10%d" % (p, _POW[p]))
                if pw not in _flat(f.get("means_row") or "").replace(" ", ""):
                    return ("REFUSED", "field value: the power code %s is not in the table's power of ten row" % p, {})
            got["value"] = v
    if pos != len(mpn): return ("REFUSED", "%s has characters the page's layout does not account for" % mpn, {})
    if sc.get("construction"):
        c, anchor = sc["construction"]
        if anchor in flat: got["construction"] = c
    # every deciding property of the kind decoded, and each meeting the selection
    bad, est = [], []
    rv = _req_value(req)
    if got.get("value") is None or rv is None: bad.append("the value is not decoded or not stated")
    elif abs(got["value"] - rv) > 1e-6 * rv: bad.append("value %g where the selection needs %g" % (got["value"], rv))
    else: est.append("value")
    if got.get("package") is None or not req.get("package"): bad.append("the package is not decoded or not stated")
    elif got["package"] != str(req["package"]): bad.append("package %s where the selection needs %s" % (got["package"], req["package"]))
    else: est.append("package")
    if got.get("tolerance_pct") is None or req.get("tolerance_max_pct") is None: bad.append("the tolerance is not decoded or not stated")
    elif got["tolerance_pct"] > float(req["tolerance_max_pct"]) + 1e-9:
        bad.append("tolerance ±%g%% where the selection allows at most %g%%" % (got["tolerance_pct"], req["tolerance_max_pct"]))
    else: est.append("tolerance")
    if kind == "capacitor":
        if got.get("volts") is None or req.get("v_rating_min") is None: bad.append("the rated voltage is not decoded or not required")
        elif got["volts"] + 1e-9 < float(req["v_rating_min"]): bad.append("rated %g V where the selection needs %g V" % (got["volts"], req["v_rating_min"]))
        else: est.append("voltage")
        if got.get("dielectric") is None or not req.get("dielectric"): bad.append("the dielectric is not decoded or not required")
        elif got["dielectric"] not in DIELECTRIC_ACCEPTS.get(req["dielectric"], (req["dielectric"],)):
            bad.append("dielectric %s where the selection needs %s" % (got["dielectric"], req["dielectric"]))
        else: est.append("dielectric")
        if got.get("construction") != req.get("construction"): bad.append("construction %s where the selection needs %s" % (got.get("construction"), req.get("construction")))
        else: est.append("construction")
    if kind == "resistor":
        if got.get("watts") is None or req.get("power_min_w") is None: bad.append("the power rating is not decoded or not required")
        elif got["watts"] + 1e-9 < float(req["power_min_w"]): bad.append("rated %g W where the selection needs %g W" % (got["watts"], req["power_min_w"]))
        else: est.append("power")
    missing = [m for m in MUST[kind] if m not in est]
    if bad or missing:
        return ("REFUSED", "the decoded part does not meet the selection: " + "; ".join(bad or ["%s not established" % ", ".join(missing)]), {})
    return ("DECODED", "page %s decodes it: %s" % (ds.get("page"), ", ".join(est)), dict(established=est, not_established=[]))


def read_binding(ds, mpn, root=REPO, maker=None, req=None, kind=None):
    """Rule D-2 on one binding {path, sha256, page, binding}: READ (PRINTED: the cited page prints the part number),
    DECODED (the cited page is the maker's ordering-code table and decodes it, read_decoded), REFUSED (the file is there
    and its sha256, its page or its decode does not agree), or UNREAD (held back and not fetched on this host)."""
    path = ds.get("path"); page = ds.get("page")
    if not path or not page: return dict(state="REFUSED", why="the binding cites no document path or no page")
    full = os.path.join(root, path)
    if not os.path.exists(full):
        if ds.get("held_back"):
            return dict(state="UNREAD", why="held back from the public tree and not fetched on this host (%s)" % ds.get("fetch", "no fetch script named"))
        return dict(state="REFUSED", why="%s is not in the tree" % path)
    got = sha256(full)
    if ds.get("sha256") and got != ds["sha256"]:
        return dict(state="REFUSED", why="%s is not the document bound: sha256 %s, the table %s" % (path, got[:16], ds["sha256"][:16]))
    if not ds.get("sha256"):
        return dict(state="REFUSED", why="the binding records no sha256 of %s" % path)
    bkind = ds.get("binding") or "PRINTED"
    if bkind == "DECODED":
        st, why, det = read_decoded(ds, mpn, maker or "", req or {}, kind, page_text(full, int(page)), page_text(full, 1), got)
        return dict(state=st, why=why, binding=bkind, **det)
    if bkind != "PRINTED":
        return dict(state="REFUSED", why="the binding kind %r is neither PRINTED nor DECODED" % bkind)
    pk = ds.get("packing")
    if pk:
        # a PRINTED part number whose packing code the page prints as a placeholder and keys on the same page (Hirose's
        # FH34SRJ-24S-0.5SH(##) with "(##) : (50)"); the code's meaning may sit on another page of the same document
        code, ph = str(pk.get("code") or ""), str(pk.get("placeholder") or "")
        if not code or not ph or not mpn.endswith(code):
            return dict(state="REFUSED", why="the packing code %r does not end the part number %s" % (code, mpn))
        printed = mpn[:len(mpn) - len(code)] + ph
        text = page_text(full, int(page))
        ok, line = names_part(text, printed)
        if not ok: return dict(state="REFUSED", why="page %s of %s does not print %s" % (page, path, printed))
        key = _flat(pk.get("key_row") or "")
        if not key or key not in _flat(text) or not re.search(re.escape(ph) + r"\s*:\s*" + re.escape(code), key):
            return dict(state="REFUSED", why="page %s does not key %s to %s" % (page, ph, code))
        if pk.get("means_page"):
            if _flat(pk.get("means_row") or "") not in _flat(page_text(full, int(pk["means_page"]))) or code not in str(pk.get("means_row")):
                return dict(state="REFUSED", why="page %s does not give the meaning of %s" % (pk["means_page"], code))
        return dict(state="READ", why="page %s prints %s and keys %s to %s" % (page, printed, ph, code), line=line, binding=bkind)
    ok, line = names_part(page_text(full, int(page)), mpn)
    if not ok:
        return dict(state="REFUSED", why="page %s of %s does not name %s" % (page, path, mpn))
    return dict(state="READ", why="page %s names it" % page, line=line, binding=bkind)


def _judged(req):
    """A selection's requirements as bindings are judged on them: v_working_bound is per row (it is left out of the
    key, K-1), so it is left out here too; everything else is the selection's."""
    return {k: v for k, v in (req or {}).items() if k != "v_working_bound"}


def check(argv):
    """The table against the committed netlists as they are now, and every RESOLVED binding against its document.

    Structure: every BOM part of the table's boards in exactly one selection, every key current, every id the digest
    of its key, the counts true, every UNRESOLVED selection with its reason class, reason and next action.
    Rule D-2: every RESOLVED selection names a maker, a part number and a held document with a page, the document's
    sha256 is the one bound, and the page's text layer names the part number (read here, not trusted); a binding that
    fails is REFUSED and is a problem. A held-back document that is not fetched on this host reads UNREAD and is a
    problem unless --unfetched-ok is given (the reading then says so).
    Usage: check [TABLE] [--out READING.json] [--unfetched-ok]"""
    table = argv[0] if argv and not argv[0].startswith("--") else TABLE
    out_path = opt(argv, "--out")
    unfetched_ok = "--unfetched-ok" in argv
    t = load_table(table)
    scope = [str(x) for x in (t.get("scope") or [])]
    if not scope: print("part_identities check: the table names no scope (its boards)"); return 1
    rs, meta = rows(boards=scope)
    now_key = {"%s:%s" % (p["board"], p["ref"]): p["key"] for p in rs}
    # the requirements every binding is judged against are DERIVED here from the committed netlist, the intent and the
    # generator's value text, never taken from the table (round 3's check, B1: a table whose C37 said 6.3 V held)
    now_req = {"%s:%s" % (p["board"], p["ref"]): (p["kind"], _judged(p["requirements"])) for p in rs}
    seen, bad, reading = {}, [], []
    inputs = {str(i.get("board")): i for i in (t.get("inputs") or [])}
    for m in meta:
        i = inputs.get(m["board"])
        if i is None: bad.append("board %s is in the scope and has no input record" % m["board"]); continue
        if i.get("netlist_sha256") != m["netlist_sha256"]:
            bad.append("board %s: the table was derived on netlist %s, the tree holds %s: re-derive"
                       % (m["board"], str(i.get("netlist_sha256"))[:16], m["netlist_sha256"][:16]))
        if i.get("intent_sha256") != m["intent_sha256"]:
            bad.append("board %s: the table was derived on intent %s, the tree holds %s: re-derive"
                       % (m["board"], str(i.get("intent_sha256"))[:16], m["intent_sha256"][:16]))
    for s in t["selections"]:
        if selection_id(s["key"]) != s["id"]: bad.append("%s: id is not the digest of its key" % s["id"])
        for r in s["rows"]:
            if r in seen: bad.append("%s is in %s and %s" % (r, seen[r], s["id"]))
            seen[r] = s["id"]
            if r not in now_key: bad.append("%s (in %s) is no longer a BOM part" % (r, s["id"]))
            elif now_key[r] != s["key"]: bad.append("%s moved: its key is now %s, the table resolved %s" % (r, now_key[r], s["key"]))
        if s.get("n_rows") != len(s["rows"]): bad.append("%s counts %s rows and lists %d" % (s["id"], s.get("n_rows"), len(s["rows"])))
        i = s["identity"]
        st = i.get("status")
        if st not in STATUSES: bad.append("%s has the status %r" % (s["id"], st)); continue
        row = dict(id=s["id"], status=st, rows=len(s["rows"]))
        if st == "RESOLVED":
            if not (i.get("maker") and i.get("mpn")): bad.append("%s is RESOLVED without a maker and a part number" % s["id"])
            derived = {json.dumps(now_req[x], sort_keys=True, default=str) for x in s["rows"] if x in now_req}
            if len(derived) != 1:
                bad.append("%s: its rows do not derive one requirement (%d)" % (s["id"], len(derived))); continue
            dkind, dreq = now_req[next(x for x in s["rows"] if x in now_req)]
            if _judged(s.get("requirements") or {}) != dreq or s.get("kind") != dkind:
                bad.append("%s: the table's requirements are not the ones the netlist and the intent derive (%s)"
                           % (s["id"], ", ".join(sorted(k for k in set(dreq) | set(_judged(s.get("requirements") or {}))
                                                         if dreq.get(k) != _judged(s.get("requirements") or {}).get(k))) or "the kind"))
            r = read_binding(i.get("datasheet") or {}, i.get("mpn"), maker=i.get("maker"), req=dreq, kind=dkind)
            if r["state"] in ("READ", "DECODED") and r.get("binding") != ((i.get("datasheet") or {}).get("binding") or "PRINTED"):
                bad.append("%s: its binding reads %s where the table says %s" % (s["id"], r.get("binding"), (i.get("datasheet") or {}).get("binding")))
            row.update(mpn=i.get("mpn"), document=(i.get("datasheet") or {}).get("path"), page=(i.get("datasheet") or {}).get("page"), **r)
            if r["state"] == "REFUSED": bad.append("%s: rule D-2 refuses its binding: %s" % (s["id"], r["why"]))
            if r["state"] == "UNREAD" and not unfetched_ok: bad.append("%s: %s" % (s["id"], r["why"]))
            if s["kind"] == "capacitor" and s["requirements"].get("v_rating_min") is None:
                bad.append("%s names a capacitor whose voltage requirement is open (rule V-1: never a guess)" % s["id"])
        else:
            if not i.get("reason"): bad.append("%s is %s without a reason" % (s["id"], st))
            if st == "UNRESOLVED":
                if i.get("reason_class") not in REASONS: bad.append("%s is UNRESOLVED with the reason class %r" % (s["id"], i.get("reason_class")))
                if not i.get("next_action"): bad.append("%s is UNRESOLVED without a next action" % s["id"])
            row.update(reason_class=i.get("reason_class"))
        reading.append(row)
    missing = sorted(set(now_key) - set(seen))
    for r in missing: bad.append("%s is a BOM part no selection covers" % r)
    c = t.get("counts") or {}
    by_status = dict(collections.Counter(s["identity"]["status"] for s in t["selections"]))
    if c.get("rows") != len(seen): bad.append("the table counts %s rows and lists %d" % (c.get("rows"), len(seen)))
    if c.get("selections") != len(t["selections"]): bad.append("the table counts %s selections and lists %d" % (c.get("selections"), len(t["selections"])))
    if (c.get("identity_status") or {}) != by_status:
        bad.append("the table's identity_status counts %s are not its selections' %s" % (c.get("identity_status"), by_status))
    by_reason = dict(collections.Counter(s["identity"].get("reason_class") for s in t["selections"] if s["identity"]["status"] == "UNRESOLVED"))
    if (c.get("unresolved_by_reason") or {}) != by_reason:
        bad.append("the table's unresolved_by_reason %s is not its selections' %s" % (c.get("unresolved_by_reason"), by_reason))
    by_binding = dict(collections.Counter(((s["identity"].get("datasheet") or {}).get("binding") or "PRINTED")
                                          for s in t["selections"] if s["identity"]["status"] == "RESOLVED"))
    if (c.get("resolved_by_binding") or {}) != by_binding:
        bad.append("the table's resolved_by_binding %s is not its selections' %s (a DECODED binding is never counted as "
                   "PRINTED)" % (c.get("resolved_by_binding"), by_binding))
    states = dict(collections.Counter(x.get("state") for x in reading if x["status"] == "RESOLVED"))
    print("part_identities check: boards %s, %d rows, %d selections, %d rows uncovered, RESOLVED bindings %s, %d problems"
          % (",".join(scope), len(rs), len(t["selections"]), len(missing), states, len(bad)))
    for b in bad[:60]: print("  " + b)
    if out_path:
        doc = dict(what="part_identities.py check: the table against the committed netlists, and rule D-2 read on every "
                        "RESOLVED binding (the cited page's text layer names the part number)",
                   table=os.path.relpath(os.path.abspath(table), REPO), table_sha256=sha256(table), scope=scope, inputs=meta,
                   rows=len(rs), selections=len(t["selections"]), identity_status=by_status, unresolved_by_reason=by_reason,
                   resolved_by_binding=by_binding,
                   resolved_bindings=states, problems=bad, unfetched_ok=unfetched_ok,
                   verdict="REFUSED" if bad else ("HOLDS_WITH_UNREAD" if states.get("UNREAD") else "HOLDS"), readings=reading,
                   tool_sha256=sha256(os.path.abspath(__file__)))
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True); fh.write("\n")
        print("part_identities check: reading written to %s" % out_path)
    return 1 if bad else 0


def _md(x):
    return str(x).replace("|", "/").replace("\n", " ")


def render(argv):
    """A page of the table: counts, then one line per selection. Usage: render [TABLE] --out PAGE.md"""
    table = argv[0] if argv and not argv[0].startswith("--") else TABLE
    out_path = opt(argv, "--out")
    if not out_path: print("part_identities render: --out PAGE.md is required"); return 2
    t = load_table(table)
    c = t["counts"]
    L = []
    w = L.append
    w("# Part identities of board%s %s" % ("s" if len(t["scope"]) > 1 else "", ", ".join(x.upper() for x in t["scope"])))
    w("")
    w("<!-- GENERATED by v2/ecad/tools/part_identities.py render from %s; edit the table's builder, not this page. -->"
      % os.path.relpath(os.path.abspath(table), REPO))
    w("")
    w("Prototype design: nothing is built, bought or deployed, and this page orders nothing. %s" % _md(t.get("taken_by", "")))
    w("")
    w("%d BOM parts in %d selections. RESOLVED %d (%s), UNRESOLVED %d, NOT_A_PART %d. UNRESOLVED by reason: %s."
      % (c["rows"], c["selections"], c["identity_status"].get("RESOLVED", 0),
         ", ".join("%s %d" % kv for kv in sorted((c.get("resolved_by_binding") or {}).items())),
         c["identity_status"].get("UNRESOLVED", 0),
         c["identity_status"].get("NOT_A_PART", 0), ", ".join("%s %d" % kv for kv in sorted(c["unresolved_by_reason"].items()))))
    w("")
    w("| Selection | Rows | Value, land | Requirement | State | Maker, part number | Document, page / reason and next action |")
    w("|---|---|---|---|---|---|---|")
    for s in t["selections"]:
        i = s["identity"]; ds = i.get("datasheet") or {}
        req = ", ".join("%s %s" % (k, v) for k, v in s["requirements"].items() if k not in ("value", "package", "land") and v is not None)
        st = i["status"] + (" (%s)" % i["reason_class"] if i.get("reason_class") else "")
        who = ("%s %s" % (i.get("maker") or "", i.get("mpn") or "")).strip()
        if i["status"] == "RESOLVED":
            last = "%s: `%s` p. %s%s" % (ds.get("binding") or "PRINTED", ds.get("path"), ds.get("page"), " (held back)" if ds.get("held_back") else "")
        else:
            last = "%s. Next: %s" % (i.get("reason", ""), i.get("next_action", ""))
        w("| %s | %s | %s | %s | %s | %s | %s |" % (s["id"], " ".join(r.split(":")[1] for r in s["rows"]), _md("%s, %s" % (s["values"][0], s["lands"][0])),
                                                   _md(req), st, _md(who), _md(last)))
    w("")
    open(out_path, "w", encoding="utf-8").write("\n".join(L))
    print("rendered %s (%d lines)" % (out_path, len(L)))
    return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    cmd = argv[0]
    boards = opt(argv, "--board")
    boards = boards.split(",") if boards else None
    if cmd == "rows":
        rs, meta = rows(boards)
        if "--json" in argv: print(json.dumps(dict(meta=meta, rows=rs), indent=1, default=_jsonable)); return 0
        for p in rs: print("%s:%s\t%s\t%s" % (p["board"], p["ref"], p["value"][:50], p["key"]))
        return 0
    if cmd == "selections":
        rs, meta = rows(boards)
        sel = selections(rs)
        if "--json" in argv:
            print(json.dumps(dict(meta=meta, selections=[dict(v, id=selection_id(k)) for k, v in sel.items()]), indent=1, default=_jsonable)); return 0
        for k, s in sel.items(): print("%d\t%s\t%s" % (len(s["rows"]), selection_id(k), k))
        print("%d rows, %d selections" % (len(rs), len(sel)))
        return 0
    if cmd == "check":
        return check(argv[1:])
    if cmd == "render":
        return render(argv[1:])
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
