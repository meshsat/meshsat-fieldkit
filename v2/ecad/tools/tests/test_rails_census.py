#!/usr/bin/env python3
"""PWR-001 on the six COMMITTED netlists: no supply net escapes the reading (third and fourth passes, 26 and 27
September 2026, MESHSAT-1357).

The second independent check of 26 September found two real supplies that the reading neither counted nor named: board
D's AMP_HPVSS (the TPA6132A2's HPVSS, typed P in TI's pin table) and board E's TRK_LDO33 (the LT8705A's 3.3 V regulator
output, a pin the symbol calls "Pin_4"). The third check of the same night found a third: board A's VMON, the output of
the eFuse U21 (TPS2596 pin 5, typed "Power Output" in TI's table), which runs straight to the monitor's two-pin lead and
carries neither a capacitor nor a two-terminal link on this board, so no mark reached it; and board P's cell taps
CELL1 to CELL3, which the schematic flags as driven. A board stream declaring exactly the nets the readings named would
have read PASS with each of them still undeclared.

Two kinds of rule hold that here. REGRESSION GUARDS re-read the tool's own premises on the committed netlists (the
decoupling and link sweep, the supply-name sweep, the named supplies, the replays, close and reopen): they catch a
change to the tool that loses what it finds today, and they are not independent evidence, because they share its
marks and its grammar. INDEPENDENT SWEEPS read a source the tool does not read: every held datasheet's own pin table
(each row carries every pin its table types power or ground, or describes as a supply), the generators' own PWR_FLAG
statements in the committed schematics, and the netlist's value fields and the intent's rail sources (every power part
on a board has a held row). Each rule is a property, and a net is named only where it is looked up if present."""
import os, re, sys, json, shutil, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.path.insert(0, TOOLS); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intent_checks as IC, phase_artefacts as PA, rules_lib as R
from harness import Skip


# THE FIXTURES' SCRATCH DIRECTORIES ARE REMOVED WHEN THE RUN ENDS (integration of 27 September 2026, the fourth
# independent check's hygiene item: every run left about ten directories of 230 KB under /tmp on the shared runner).
import atexit as _atexit
_TMPDIRS = []


def _mkdtemp(prefix):
    d = tempfile.mkdtemp(prefix=prefix)
    _TMPDIRS.append(d)
    return d


_atexit.register(lambda: [shutil.rmtree(d, ignore_errors=True) for d in _TMPDIRS])

CLASSES = ("counted", "declared node", "undecided", "settled", "unmarked", "ground", "unconnected")
# a pin name that names a supply, read here independently of the tool's own grammar: the supply families, the
# regulator, bootstrap and charge-pump pins, and a voltage; split on every character that is not a letter or a digit
STRICT = re.compile(r"^(?:[A-Z]{0,4}V(?:DD|CC|SS|EE)[A-Z0-9]*|V(?:IN|BAT|BUS|SYS|CAP|REG|AUX|TX)\d*|LDO\d*|BST\d?|"
                    r"BTST\d?|CP[PN]|PBI|\d+V\d*)$")
# a function that also carries one of these names the control or the sense of a supply, not the supply (an LDO's
# enable, a power-good, a VBUS detect): board B's IOCA_LDO_EN is the STM32 supervisors' regulator enable
QUALIFIER = {"EN", "ENABLE", "PG", "PGOOD", "GOOD", "DET", "SENSE", "SNS", "MON", "FB", "CTL", "CTRL"}
GROUND = re.compile(r"(^|_)GND[0-9]*$|^GND", re.I)
# the supplies the checks named, and the two more of the same shape the third pass found on board A
NAMED = {"d": ("AMP_HPVSS", "AMP_CPP", "AMP_CPN"), "e": ("TRK_LDO33",), "a": ("PD_VTX", "PD_VAUX", "VMON")}
# the conductors the third check named that sense a supply: undecided until a board declares them
SENSED = {"p": ("CELL1", "CELL2", "CELL3")}


def _boards():
    out = []
    for letter in PA.letters():
        if PA.no_schematic(letter): continue
        net = PA.netlist(letter)
        if net and os.path.exists(net) and os.path.exists(PA.intent(letter)): out.append((letter, net))
    if not out: raise Skip("no committed netlist with its intent file in this tree")
    return out


_READ = {}


def _read(letter, net):
    if letter not in _READ:
        nets, values = IC.read_netlist(net)
        _READ[letter] = (IC.rails_on_netlist(net), nets, values, IC.held_roles(values)[0])
    return _READ[letter]


def _pins_of(nets):
    out = {}
    for n, d in nets.items():
        for ref, pin, fn, pt in d["nodes"]:
            out.setdefault(ref, []).append((pin, fn, pt, n))
    return out


def _norm(text):
    return " ".join(text.split())


_TEXT = {}


def _text(doc):
    if not shutil.which("pdftotext"): raise Skip("pdftotext is not on this host; the held documents are not read")
    if doc not in _TEXT:
        path = os.path.join(REPO, doc)
        assert os.path.isfile(path), "PIN_ROLES names %s, which is not in this tree" % doc
        _TEXT[doc] = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout
    return _TEXT[doc]


def t_every_held_pin_role_is_read_from_the_words_of_its_own_document():
    """Each row of PIN_ROLES names a document filed under v2/vendor, and the words it quotes for a pin's number and for
    its role are in that document's text; the pin's own number stands in the words that give it (or inside a range
    they give). A role outside the vocabulary the reading acts on is refused."""
    missing = []
    vocab = {IC.ROLE_SUPPLY, IC.ROLE_GROUND, "SIGNAL", "SENSE", "TIMING", "COMPENSATION", "REFERENCE", "RESET",
             "CENTRE_TAP"} | set(IC.TRANSISTOR_ROLES)
    for row in IC.PIN_ROLES:
        assert row["document"].startswith("v2/vendor/"), row["document"]
        text = _norm(_text(row["document"]))
        if row.get("numbering") and row["numbering"] not in text:
            missing.append((row["part"], "numbering", row["numbering"]))
        for pin, (name, role, number_words, role_words) in row["pins"].items():
            assert role in vocab, (row["part"], pin, role)
            if number_words not in text: missing.append((row["part"], pin, number_words))
            if not _number_in(pin, number_words): missing.append((row["part"], pin, "number not in", number_words))
            if role_words and role_words not in _norm(_text(row.get("role_document") or row["document"])):
                missing.append((row["part"], pin, role_words))
    assert not missing, missing


def _number_in(pin, words):
    for m in re.finditer(r"(\d+)\s*[\u2013-]\s*(\d+)", words):
        if int(m.group(1)) <= int(pin) <= int(m.group(2)): return True
    return bool(re.search(r"(?<![\d.])%s(?![\d.])" % re.escape(pin), words))


# ---- INDEPENDENT SWEEP 1: every held row carries every power or ground pin of its own table ----------------------
# A TYPE CELL of a pin table as pdftotext -layout sets it: one of the words the makers type a power or a ground pin
# with (TI's P, PWR, I/P, I/O/P and G, its em dash where a table types a ground with it, Quectel's PI and PO, TI's Power
# and Ground, Microchip's GND), standing alone between runs of two or more spaces, where a description's words are set
# one space apart. A SUPPLY PHRASE is how a table with no type column (Diodes, Linear Technology, Nexperia) or one that
# types a supply I or O (TI's TPS25740, TPS22810, LM5069) says a pin supplies or is supplied. Both are this test's own
# reading of the document, not the tool's.
_CELL = re.compile(r"(?:^|\s{2,})(P|PWR|I/P|I/O/P|PI|PO|Power|G|GND|Ground|\u2014)(?=\s{2,}|\s*$)")
_PHRASE = re.compile(r"(?i)\b(power (?:input|output|ground|supply|switching output)|supplies (?:the|power)|input supply|"
                     r"positive supply|negative (?:power )?supply|supply (?:input|output|pin|voltage|for)|"
                     r"switch (?:input|output)|power-switch|regulator output|regulated (?:rail|output|supply|\d)|"
                     r"internally regulated|bypass pin|bootstrap|boost input|charge pump|bias (?:power|supply|"
                     r"regulator)|switching nodes?|switch nodes?|(?:power|analog|device|circuit|signal|digital) ground|"
                     r"ground (?:pin|connection)|input voltage|input pin\.|output voltage pin)\b")
# each document's pin table: the lines it runs between (a line that starts with the first words, "=" for a line that is
# exactly them, up to the first later line that starts with the second), the lines a row need not claim with the reason
# (a column header, a legend, an unnumbered exposed pad, a pin with no connection, a description that runs on across a
# column), and a pin assignment grid ("number name") whose every power or ground name must be carried
TABLES = {
    "v2/vendor/ti/ti-tpa6132a2.pdf": {"regions": [("Pin Functions", "Thermal Pad")],
                                      "exempt": {"I/O/P DESCRIPTION": "the column header"}},
    "v2/vendor/power/lt8705a.pdf": {"regions": [("Pin Functions (QFN/TSSOP)", "Block Diagram")], "exempt": {
        "to GATEVCC superimposed on the switch node voltages.": "the top gate drives' description (TG1, TG2)",
        "(\u2013) terminals of the bootstrap capacitors connect here.": "the switch nodes' description, run on",
        "put. This pin is pulled to ground when the input voltage": "SRVO_FBIN's open-drain logic output"}},
    "v2/vendor/ti/ti-tps25740.pdf": {"regions": [("Pin Functions", "PAD Connect PAD")]},
    "v2/vendor/ti/lm5176-datasheet.pdf": {"regions": [("Table 5-1. Pin Functions", "PowerPAD")], "exempt": {
        "Solder the PowerPAD to the analog ground.": "the exposed pad, which the table numbers in neither package"}},
    "v2/vendor/ti/ti-tps62933.pdf": {"regions": [("Table 7-1. Pin Functions", "(1) A = Analog")]},
    "v2/vendor/diodes/diodes-ap64500.pdf": {"regions": [("Pin Descriptions", "AP64500 3 of 26")]},
    "v2/vendor/diodes/diodes-ap63200-series-buck.pdf": {"regions": [("Pin Descriptions", "AP63200/AP63201")]},
    "v2/vendor/power/tps2596.pdf": {"regions": [("Pin Functions", "Thermal pad")]},
    "v2/vendor/power/ltc2954.pdf": {"regions": [("PIN FUNCTIONS (TSOT-23/DFN)", "BLOCK DIAGRAM")], "exempt": {
        "open or connected to device ground.": "the exposed pad of the DFN package; the TS8 package has none"}},
    "v2/vendor/ti/ti-tps22810-load-switch.pdf": {"regions": [("Pin Functions", "7 Specifications")]},
    "v2/vendor/ti/ti-lm5069.pdf": {"regions": [("Pin Functions", "7 Specifications")]},
    "v2/vendor/ti/bq25731-datasheet.pdf": {"regions": [("Table 7-1. Pin Functions", "8 Specifications")], "exempt": {
        "Thermal pad \u2013 \u2013 the thermal pad plane connecting to power ground planes.":
            "the exposed pad, which the table does not number"}},
    "v2/vendor/ti/ti-tusb8041.pdf": {"regions": [("Pin Functions", "7 Specifications")], "exempt": {
        "VSS PWR Ground. Thermal pad must be connected to ground.": "the exposed pad, which the table does not number",
        "NC 60 \u2014 No connect": "a pin with no connection"}},
    "v2/vendor/microchip/microchip-ksz9897-datasheet.pdf": {
        "regions": [("Power/Ground Pins", "3.2.1 CONFIGURATION")],
        "grids": [("TABLE 3-1: PIN ASSIGNMENTS", "Exposed Pad Must", ("VDDIO", "AVDDH", "AVDDL", "DVDDL", "GND"))]},
    "v2/vendor/pulse/pulse-h5007nl.pdf": {"drawing": "a magnetics drawing: windings and taps, no pin types"},
    "v2/vendor/battery/ti-bq4050.pdf": {
        "regions": [("Pin Functions", "(1) P = Power Connection"),
                    ("Pin Functions (continued)", "4 Submit Documentation Feedback")],
        "exempt": {"Not internally connected. Connect to VSS.": "a pin with no internal connection"}},
    "v2/vendor/battery/ti-bq77207.pdf": {"regions": [("12-Pin Functions", "(1) I = Input")]},
    "v2/vendor/battery/ti-csd17570q5b.pdf": {"drawing": "a MOSFET pin-out drawing, and the row carries every pin"},
    "v2/vendor/battery/ti-csd18510q5b.pdf": {"drawing": "a MOSFET pin-out drawing, and the row carries every pin"},
    "v2/vendor/power/ti-csd19532q5b-n-fet.pdf": {"drawing": "a MOSFET pin-out drawing, and the row carries every pin"},
    "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf": {"regions": [("Table 621. Power", "5.5.3. Pin Specifications")],
                                                  "lists": [("Table 621. Power", "5.5.3. Pin Specifications")]},
    "v2/vendor/ti/ti-pcm2912a.pdf": {"regions": [("Pin Functions", "7 Specifications")],
                                     "exempt": {"NC 14 \u2014 Not connected": "a pin with no connection"}},
    "v2/vendor/ti/ti-tusb2046b.pdf": {"regions": [("Pin Functions", "7 Specifications")]},
    "v2/vendor/ti/ti-tlv9062-op-amp.pdf": {"regions": [("Table 5-3. Pin Functions: TLV9062", "(1) I = input")]},
    "v2/vendor/nexperia/nexperia-74lvc86a.pdf": {"regions": [("Table 2. Pin description", "74LVC86A All information")]},
    "v2/vendor/quectel/lg290p03-hardware-design-v1.1.pdf": {
        "regions": [("=Table 6: Pin Description", "3 Power Management")],
        "exempt": {"PI Power Input": "the legend of the I/O column", "PO Power Output": "the legend of the I/O column"}},
    "v2/vendor/diodes/diodes-ap2112-ldo.pdf": {"regions": [("Pin Descriptions", "Functional Block Diagram")],
                                               "exempt": {"NC No Connection": "a pin with no connection"}},
    "v2/vendor/power/ti-tlv755p-ldo.pdf": {"regions": [("Table 4-1. Pin Functions", "5 Specifications")], "exempt": {
        "No internal connection.": "a pin with no connection",
        "Thermal pad Pad \u2014 Pad Pad \u2014": "the exposed pad of the other packages; the DBV package has none"}},
    "v2/vendor/ti/ti-tlv758p.pdf": {"regions": [("Table 4-1. Pin Functions", "5 Specifications")], "exempt": {
        "DNC 5 \u2014 Do not connect": "a pin that is not connected",
        "Thermal pad Pad \u2014 Connect the thermal pad": "the exposed pad, which the table does not number"}},
    "v2/vendor/ti/ti-lm74700-q1.pdf": {"regions": [("Table 5-1. Pin Functions", "(1) I = Input")]},
    "v2/vendor/ti/ti-tps2065c-slvsau6i.pdf": {"regions": [("Table 5-2. Pin Functions - 5 Pins", "6 Specifications")]},
    "v2/vendor/ti/tps23861-datasheet.pdf": {"regions": [("Pin Functions", "6 Specifications")]},
}


def _region(lines, frm, to):
    i = next(k for k, t in enumerate(lines) if (t == frm[1:] if frm.startswith("=") else t.startswith(frm)))
    j = next(k for k in range(i + 1, len(lines)) if lines[k].startswith(to))
    return i, j


def _claimed(lines, k, words):
    """The words occur in the lines around k, with a span that covers part of line k itself."""
    lo, hi = max(0, k - 3), min(len(lines), k + 4)
    joined, starts = "", []
    for t in lines[lo:hi]:
        starts.append(len(joined)); joined += t + " "
    a = starts[k - lo]; b = a + len(lines[k])
    return any(m.start() < b and m.end() > a for m in re.finditer(re.escape(words), joined))


def _unclaimed(row, spec):
    raw = _text(row["document"]).split("\n")
    lines = [_norm(x) for x in raw]
    cells = {k for k, x in enumerate(raw) if _CELL.search(x)}
    words = [nw for _n, _r, nw, _w in row["pins"].values()] + [w for _n, _r, _q, w in row["pins"].values() if w]
    words += list(spec.get("exempt") or {})
    bad = []
    for frm, to in spec["regions"]:
        i, j = _region(lines, frm, to)
        for k in range(i, j):
            if (k in cells or _PHRASE.search(lines[k])) and not any(_claimed(lines, k, w) for w in words):
                bad.append((row["part"], "line %d" % k, lines[k][:100]))
    for frm, to, names in spec.get("grids", ()):
        i, j = _region(lines, frm, to)
        txt = " ".join(lines[i:j])
        for nm in names:
            for m in re.finditer(r"(?<!\S)(\d+) %s(?!\S)" % re.escape(nm), txt):
                if m.group(1) not in row["pins"]: bad.append((row["part"], "grid", nm, m.group(1)))
    for frm, to in spec.get("lists", ()):
        i, j = _region(lines, frm, to)
        for t in lines[i:j]:
            m = re.match(r"^([A-Z][A-Z0-9_]+) ((?:\d+, )*\d+) ", t)
            if not m: continue
            for p in m.group(2).split(", "):
                if p not in row["pins"]: bad.append((row["part"], "list", m.group(1), p))
    return bad


def t_every_held_row_carries_every_pin_its_own_table_types_power_or_ground_or_describes_as_a_supply():
    """The blocking item of the third check: the TPS2596 row carried pin 2 only, so the eFuse's Power Output (pin 5,
    board A's VMON) was read by nothing. Every line of each held document's pin table that holds a power or ground type
    cell or a supply phrase must be claimed by a pin the row carries (its words cover part of that very line), or be
    one the table spec exempts with its reason; a grid or a list of pin numbers is carried number by number. A drawing
    with no pin types says so, and its row carries every pin it draws."""
    bad = []
    docs = {row["document"] for row in IC.PIN_ROLES}
    assert docs <= set(TABLES), sorted(docs - set(TABLES))
    for row in IC.PIN_ROLES:
        spec = TABLES[row["document"]]
        if spec.get("drawing"): continue
        bad += _unclaimed(row, spec)
    assert not bad, bad[:12]


def t_the_table_sweep_finds_the_tps2596_power_output_when_the_row_leaves_it_out():
    """The sweep both ways: the TPS2596 row with pin 5 taken out has one unclaimed line, and it is the Power Output."""
    row = next(r for r in IC.PIN_ROLES if r["document"].endswith("tps2596.pdf"))
    assert not _unclaimed(row, TABLES[row["document"]])
    cut = dict(row, pins={p: v for p, v in row["pins"].items() if p != "5"})
    bad = _unclaimed(cut, TABLES[row["document"]])
    assert len(bad) == 1 and "OUT 5 Power Power Output" in bad[0][2], bad


# ---- INDEPENDENT SWEEP 2: the generators' PWR_FLAG statements in the committed schematics --------------------------
def _pwr_flag_nets(sch):
    """{net} a PWR_FLAG symbol of the schematic sits on: the labels and power symbols its wires reach. The netlist drops
    the flag, so the reading never sees it: this is a statement of the schematic that the tool does not read."""
    txt = open(sch, encoding="utf-8").read()
    at = lambda x, y: (round(float(x), 2), round(float(y), 2))
    flags = [at(x, y) for x, y in re.findall(r'\(symbol \(lib_id "power:PWR_FLAG"\) \(at ([-\d.]+) ([-\d.]+)', txt)]
    adj = {}
    for x1, y1, x2, y2 in re.findall(r'\(wire \(pts \(xy ([-\d.]+) ([-\d.]+)\) \(xy ([-\d.]+) ([-\d.]+)\)\)', txt):
        a, b = at(x1, y1), at(x2, y2)
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    names = {}
    for nm, x, y in re.findall(r'\((?:label|global_label|hierarchical_label) "([^"]+)" \(at ([-\d.]+) ([-\d.]+)', txt):
        names.setdefault(at(x, y), set()).add(nm)
    for m in re.finditer(r'\(symbol \(lib_id "power:([^"]+)"\) \(at ([-\d.]+) ([-\d.]+)[^\n]*\n(?:[^\n]*\n)*?\s*'
                         r'\(property "Value" "([^"]*)"', txt):
        if m.group(1) != "PWR_FLAG": names.setdefault(at(m.group(2), m.group(3)), set()).add(m.group(4))
    out, lost = set(), []
    for f in flags:
        seen, todo, got = {f}, [f], set()
        while todo:
            p = todo.pop()
            got |= names.get(p, set())
            for q in adj.get(p, ()):
                if q not in seen: seen.add(q); todo.append(q)
        if len(got) != 1: lost.append((f, sorted(got)))
        out |= got
    return out, lost


def t_every_net_a_generator_flags_as_driven_is_counted_declared_or_undecided_on_the_committed_netlists():
    """The generators put a PWR_FLAG on every net they know a source drives from outside the sheet or through a part
    ERC cannot see through (gen_sch_a.py flags VMON, gen_sch_p.py the cell taps). Each such net is counted, declared
    or undecided in the reading, never settled or unmarked: the third check's replay found VMON and P's CELL1 to CELL3
    unmarked on the reading of that night, and this sweep reproduces it on that tool."""
    seen = 0
    for letter, net in _boards():
        sch = os.path.join(os.path.dirname(os.path.dirname(net)),
                           os.path.splitext(os.path.basename(net))[0] + ".kicad_sch")
        if not os.path.exists(sch): continue
        seen += 1
        flagged, lost = _pwr_flag_nets(sch)
        assert not lost, (letter, "a flag whose net was not resolved", lost[:3])
        r, _n, _v, _h = _read(letter, net)
        quiet = sorted((n, r["census"].get(n.lstrip("/"))) for n in flagged
                       if r["census"].get(n.lstrip("/")) not in ("counted", "declared node", "undecided", "ground"))
        assert not quiet, (letter, quiet)
    if not seen: raise Skip("no committed schematic beside the netlists in this tree")


# ---- INDEPENDENT SWEEP 3: every power part on a board is a held part ------------------------------------------------
# what a value field calls a power part, or a part a declared rail names as its source: an integrated circuit whose
# supply pins the reading can only see through its held row (a receptacle is a connector, whatever its prefix)
POWER_WORDS = re.compile(r"(?i)\b(e-?fuse|load switch|power[- ]switch|LDO|regulator|buck|boost|buck-boost|converter|"
                         r"charger|hot-swap|PSE controller|ideal[- ]diode|power path|gas gauge|protector|protection)\b")


def t_every_power_part_on_the_committed_netlists_has_a_held_row():
    """The class of the blocking item: a supply that a part of three or more pins delivers (an eFuse, a load switch, a
    regulator) is read only through that part's held row when nothing else on its net marks it. Every part a value field
    calls a power part, and every integrated circuit a declared rail names as its source, has a row of PIN_ROLES."""
    orphans = []
    for letter, net in _boards():
        _r, nets, values, held = _read(letter, net)
        it = json.load(open(PA.intent(letter), encoding="utf-8"))
        sources = set()
        for rv in (it.get("rails") or {}).values():
            s = rv.get("source"); sources |= set(s if isinstance(s, (list, tuple)) else ([s] if s else []))
        refs = {x[0] for d in nets.values() for x in d["nodes"]}
        held_refs = {r for r, _p in held}
        for ref in sorted(refs):
            pre, val = R.ref_prefix(ref), values.get(ref, "")
            if pre not in IC.MARK_IC or re.search(r"(?i)receptacle|connector|header|socket", val): continue
            if (POWER_WORDS.search(val) or ref in sources) and ref not in held_refs:
                orphans.append((letter, ref, val[:60]))
    assert not orphans, orphans


# ---- REGRESSION GUARDS: the tool's own premises, re-read on the committed netlists ---------------------------------
def t_the_census_of_every_committed_netlist_gives_each_net_one_disposition():
    for letter, net in _boards():
        r, nets, _v, _h = _read(letter, net)
        assert set(r["census"]) == set(nets), (letter, set(nets) ^ set(r["census"]))
        assert set(r["census"].values()) <= set(CLASSES), (letter, set(r["census"].values()))
        assert sum(r["census_tally"].values()) == len(nets), (letter, r["census_tally"])
        for n in r["undecided"]: assert r["census"][n] == "undecided", (letter, n)
        for n in r["settled"]: assert r["census"][n] == "settled", (letter, n)


def t_every_net_with_a_decoupling_capacitor_or_a_supply_link_is_decided_or_named_on_the_committed_netlists():
    """A regression guard on marks M1 and M3 (it re-reads the tool's own premises): a net with a two-pin capacitor to
    ground, or one that a fuse, inductor, ferrite, diode, jumper or two-pin switch joins to a counted net, is never left
    unmarked."""
    for letter, net in _boards():
        r, nets, _v, _h = _read(letter, net)
        it = json.load(open(PA.intent(letter), encoding="utf-8"))
        clamps = set((it.get("clamps") or {}).keys())
        counted = {n for n, c in r["census"].items() if c in ("counted", "declared node")}
        pins = _pins_of(nets)
        escaped = []
        for ref, pp in pins.items():
            if len(pp) != 2 or ref in clamps: continue
            (_p1, _f1, _t1, a), (_p2, _f2, _t2, b) = pp
            pre = R.ref_prefix(ref)
            for x, y in ((a, b), (b, a)):
                if r["census"].get(x) != "unmarked": continue
                if pre == "C" and GROUND.search(y): escaped.append((x, "capacitor %s to ground" % ref))
                if (pre in ("F", "L", "FB", "D", "JP") or pre.startswith("SW")) and y in counted:
                    escaped.append((x, "%s to the counted net %s" % (ref, y)))
        assert not escaped, (letter, escaped[:10])


def t_no_supply_named_or_held_pin_sits_on_a_net_the_reading_left_quiet_on_the_committed_netlists():
    """A regression guard on pin names (its grammar is wider than the tool's, and it is still a grammar): a net carrying
    a pin whose own name, or whose held datasheet name, names a supply is counted, declared or undecided; it is settled
    only by the held role of that very pin (a USB hub's VBUS detect, a codec's microphone VIN), and never unmarked."""
    for letter, net in _boards():
        r, nets, _v, held = _read(letter, net)
        quiet = []
        for n, d in nets.items():
            if r["census"][n] not in ("settled", "unmarked"): continue
            for ref, pin, fn, pt in d["nodes"]:
                names = [x for x in re.split(r"[^A-Za-z0-9]+", str(fn or "").upper()) if x]
                if QUALIFIER & set(names): names = []
                h = held.get((ref, pin))
                if h: names += [x for x in re.split(r"[^A-Za-z0-9]+", h[0].upper()) if x]
                if not any(STRICT.match(x) for x in names): continue
                if r["census"][n] == "settled" and h and h[1] not in (IC.ROLE_SUPPLY, IC.ROLE_GROUND) and \
                        ("%s.%s %s" % (ref, pin, h[0])) in r["settled"][n]:
                    continue
                quiet.append((n, r["census"][n], "%s.%s %s" % (ref, pin, fn)))
        assert not quiet, (letter, quiet[:10])


def t_every_held_supply_or_ground_pin_on_a_net_that_is_not_ground_is_counted_on_the_committed_netlists():
    """What the held rows say is what the reading does: a pin a row makes a supply or a ground, on a net that is not a
    ground, puts the net in the count (or a declaration), whatever else is on it."""
    for letter, net in _boards():
        r, nets, _v, held = _read(letter, net)
        quiet = sorted((n, "%s.%s" % (ref, pin), r["census"][n]) for n, d in nets.items()
                       for ref, pin, _f, _t in d["nodes"]
                       if (held.get((ref, pin)) or (None, None))[1] in (IC.ROLE_SUPPLY, IC.ROLE_GROUND)
                       and r["census"][n] not in ("counted", "declared node", "ground", "unconnected"))
        assert not quiet, (letter, quiet[:8])


def t_the_supplies_the_checks_named_are_power_nets_and_the_taps_are_named_on_the_committed_netlists():
    for letter, net in _boards():
        r, nets, _v, _h = _read(letter, net)
        for n in NAMED.get(letter, ()):
            if n in nets:
                assert r["census"][n] in ("counted", "declared node"), (letter, n, r["census"][n])
        for n in SENSED.get(letter, ()):
            if n in nets:
                assert r["census"][n] in ("counted", "declared node", "undecided"), (letter, n, r["census"][n])


def _copy(letter, net):
    d = _mkdtemp("pwr001-census-")
    os.makedirs(os.path.join(d, "out"))
    stem = os.path.splitext(os.path.basename(net))[0]
    p = os.path.join(d, "out", stem + ".net")
    shutil.copy(net, p)
    it = json.load(open(PA.intent(letter), encoding="utf-8"))
    return p, os.path.join(d, "out", stem + "-intent.json"), it


def _declare(it, n, why="declared by the census fixture"):
    it.setdefault("nodes", {})[n] = {"v_max": 5.0, "v_min": 0.0, "basis": why}


def _close(p, ip, it, rounds=8):
    """Declare every net the reading names (an undeclared power net or an undecided net as a node, a node refused for
    supplying two parts as a rail between two of them) until it names none; returns the last reading."""
    nets, _v = IC.read_netlist(p)
    for _ in range(rounds):
        json.dump(it, open(ip, "w"))
        r = IC.rails_on_netlist(p, ip)
        changed = False
        for ok, t in r["checks"]:
            if ok: continue
            m = re.match(r"power net (\S+) is a declared rail", t)
            if m: _declare(it, m.group(1)); changed = True
            m = re.match(r"node (\S+) supplies one part at most", t)
            if m:
                n = m.group(1)
                parts = sorted({x[0] for x in nets[n]["nodes"] if R.ref_prefix(x[0]) not in ("C", "R", "TP")})
                it["nodes"].pop(n, None)
                it["rails"][n] = {"volts": 3.3, "amps_typ": 0.001, "amps_peak": 0.001, "source": parts[0],
                                  "loads": {parts[1]: 0.001}}
                changed = True
        for n in r["undecided"]:
            _declare(it, n); changed = True
        if not changed: return r
    return r


def _replay(named, missed):
    """Declare exactly what an earlier reading named on a board, and the reading of this tree still does not pass,
    and names the supply that reading missed."""
    seen = 0
    for letter, net in _boards():
        if letter not in named: continue
        nets, _v = IC.read_netlist(net)
        if missed[letter] not in nets: continue
        seen += 1
        p, ip, it = _copy(letter, net)
        # THE REPLAY IS OF THE STATE THAT PASS SAW (27 September 2026, board A stream w3a): the committed intent may
        # declare the missed net by now (board A declares VMON as a rail since EQ-19), and a replay that starts from it
        # would test the fix, not the instrument. The missed net's own declaration is taken out first, so the fixture
        # still asks whether the reading names it when nobody has declared it.
        for sec in ("rails", "nodes"):
            for k in [k for k in (it.get(sec) or {}) if k.lstrip("/") == missed[letter]]:
                it[sec].pop(k)
        for n in named[letter]:
            if n in nets: _declare(it, n)
        json.dump(it, open(ip, "w"))
        r = IC.rails_on_netlist(p, ip)
        fails = [t for ok, t in r["checks"] if not ok]
        assert (fails and any(missed[letter] in t for t in fails)) or missed[letter] in r["undecided"], \
            (letter, fails[:6], sorted(r["undecided"])[:6])
    return seen


def t_the_nets_the_second_pass_named_do_not_close_boards_d_and_e_while_their_missed_supplies_stand():
    """The second check's blocking item, replayed on the committed netlists: declare exactly what the second pass named
    on D and E (the check's own simulation) and the reading does not pass, and names AMP_HPVSS and TRK_LDO33."""
    second = {"d": ("PCM_VDD", "PCM_VCCA", "PCM_VCCL", "PCM_VCCP", "PCM_VCCR", "AMP_HPVDD", "SAU_3V3", "PCM_VIN"),
              "e": ("E6_DVDD", "SGP_VDD", "TRK_LSENSE", "E6_BST", "TRK_CSP", "VIN_MON")}
    if not _replay(second, {"d": "AMP_HPVSS", "e": "TRK_LDO33"}):
        raise Skip("neither AMP_HPVSS nor TRK_LDO33 is on the committed netlists any longer")


def t_the_nets_the_third_pass_named_do_not_close_boards_a_and_p_while_their_missed_nets_stand():
    """The third check's blocking item, replayed: declare exactly what the third pass's readings named on A (its
    undeclared power nets and its undecided nets) and the reading does not pass, and names VMON; the same on P names
    the cell tap CELL1, undecided until the board declares it."""
    third = {"a": ("B33_BST", "HT_BST", "PD_DVDD", "PD_VAUX", "PD_VTX", "S1_BOOT", "S3_BOOT", "PD_CC1", "PD_CC2",
                   "PRECHG"),
             "p": ("BAT_F", "PBI", "SEC_VDD", "SW", "VCC_F", "FUSE_G", "FUSE_GQ")}
    if not _replay(third, {"a": "VMON", "p": "CELL1"}):
        raise Skip("neither VMON nor CELL1 is on the committed netlists any longer")


def t_declaring_every_net_the_reading_names_closes_it_and_leaving_one_supply_out_reopens_it():
    """Both ways on every committed netlist: once every net the reading names is declared, nothing is refused or
    undecided; take one named supply's declaration away and the reading refuses exactly that net again, and take a
    named tap's away and it is undecided again."""
    for letter, net in _boards():
        p, ip, it = _copy(letter, net)
        r = _close(p, ip, it)
        left = [t for ok, t in r["checks"] if not ok and t.startswith(("power net ", "node "))]
        assert not left and not r["undecided"], (letter, left[:5], sorted(r["undecided"])[:5])
        for n in NAMED.get(letter, ()) + SENSED.get(letter, ()):
            if n not in it.get("nodes", {}): continue
            it2 = json.loads(json.dumps(it)); it2["nodes"].pop(n)
            json.dump(it2, open(ip, "w"))
            r2 = IC.rails_on_netlist(p, ip)
            assert any(t.startswith("power net %s is" % n) for ok, t in r2["checks"] if not ok) or \
                n in r2["undecided"], (letter, n)
