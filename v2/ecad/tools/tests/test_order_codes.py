#!/usr/bin/env python3
"""Rows that reach a JLCPCB order, and the two ways one goes wrong without anybody noticing.

MESHSAT-862, 12 September 2026, written during the orderability pass before the draft order. Two real
defects and one reporting defect sat behind `jlc_certify.py`'s 21 non-certified rows:

1. **A connector land with no code at all.** Three JST-VH rows (E's J_DCIN and J_SOLAR, D's J_PWR1)
   carried no LCSC part, so the certifier fell back to searching the row's prose, and the prose names
   the D38999 wall receptacle the LEAD comes from. It answered with a 34 GBP Amphenol circular MIL
   connector at stock 0 and called the row NO_STOCK, which reads as a supply problem where the real
   fault is that the row never named its part.

2. **A code that is the right silicon in the wrong package.** E's U5 carried C674167, LT8705AIFE#PBF,
   a TSSOP-38, on the WQFN-38-1EP 5x7 land the QFN variant needs.

3. **The word "class" in a row's prose outranked its own part number.** The class test ran first, so a
   row whose part IS chosen was reported as unchosen, and a pin-header land whose comment describes the
   module that plugs into it was reported the same way, which buried both.
"""
import os, re, sys, glob, csv, datetime

_today = datetime.date.today().isoformat()

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import jlc_certify as jc

GEN = sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py")))
# a part() call's footprint key, then its net map, then an optional LCSC code as the last argument
CALL = re.compile(r'part\(\s*"(?P<ref>[^"]+)"\s*,.*?"(?P<fp>[A-Za-z0-9_]+)"\s*,\s*\{(?P<nets>[^{}]*)\}'
                  r'\s*(?:,\s*"(?P<lcsc>C\d+)"\s*)?\)', re.S)


def _fpmap(src):
    """{key: library footprint} out of a generator's own FP dict lines."""
    out = {}
    for k, v in re.findall(r'"([A-Z0-9_]+)"\s*:\s*"([^"]*:[^"]*)"', src):
        out.setdefault(k, v)
    return out


def _rows():
    for path in GEN:
        src = open(path, encoding="utf-8").read()
        fps = _fpmap(src)
        for m in CALL.finditer(src):
            fp = fps.get(m.group("fp"))
            if fp is None:                      # a footprint given in full rather than through the key
                fp = m.group("fp") if ":" in m.group("fp") else None
            if fp:
                yield os.path.basename(path), m.group("ref"), fp, m.group("lcsc")


def _rows_with_comment():
    """_rows(), plus each row's comment, for the rules that have to read the prose."""
    for path in GEN:
        src = open(path, encoding="utf-8").read()
        fps = _fpmap(src)
        for m in CALL.finditer(src):
            fp = fps.get(m.group("fp"))
            if not fp:
                continue
            cm = re.search(r'part\(\s*"[^"]+"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"([^"]*)"', m.group(0))
            yield (os.path.basename(path), m.group("ref"), fp, m.group("lcsc"), cm.group(1) if cm else "")


def t_every_connector_row_on_a_stocked_land_names_its_part():
    """A JST-VH, XT60, U.FL or SMA land is a component JLC can place, so the row must name a code.

    These four are the lands the 12 September pass found blank. The rule is deliberately a named list
    and not "every connector": several connector rows are bench-fitted leads and solder pads, declared
    in jlc-handfit.txt or stripped by make_handoff.py, and a rule that demanded a code from those would
    be answered by putting wrong codes in."""
    lands = ("JST_VH_B2P-VH", "AMASS_XT60-M", "U.FL_Hirose_U.FL-R-SMT-1", "SMA_Amphenol_132134")
    bad = ["%s %s on %s" % (f, ref, fp) for f, ref, fp, code in _rows()
           if any(x in fp for x in lands) and not code]
    assert not bad, ("a land JLCPCB stocks and places carries no LCSC code, so the certifier has only "
                     "the row's prose to search and will answer with something else:\n  " + "\n  ".join(bad))


def t_no_generator_names_a_code_the_block_list_refuses():
    blocked = {}
    for line in open(os.path.join(TOOLS, "lcsc-blocked.txt"), encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line.startswith("C") and len(line.split()) >= 2:
            blocked[line.split()[0]] = line.split()[1]
    bad = ["%s %s carries %s (blocked, use %s)" % (f, ref, code, blocked[code])
           for f, ref, fp, code in _rows() if code in blocked]
    assert not bad, "\n  ".join(bad)


def t_a_row_that_carries_a_code_is_never_reported_as_having_no_part_chosen():
    """E's J_SOLAR reads `bare 12 V class panel in ... (JST-VH, 10 A)`: the panel is a class, the
    connector on the board is a JST B2P-VH and it has a part number."""
    rec = {"comment": "JST-VH socket, 10 A: bare panel in (lead from the D38999 spare pair; a 36-cell "
                      "12 V class panel, up to about 22 V open circuit, 100 W): + -",
           "fp": "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "code": "C274411", "qty": 1}
    ev = jc.certify(rec, {"C274411": {"asked": _today, "list": [
        {"componentCode": "C274411", "componentModelEn": "B2P-VH-BL(LF)(SN)", "componentBrandEn": "JST",
         "componentSpecificationEn": "Plugin,P=3.96mm", "componentLibraryType": "expand",
         "stockCount": 10946, "initialPrice": 0.1073}]}}, {}, {})
    assert ev["verdict"] == "CERTIFIED", ev


def t_a_bench_header_whose_prose_names_a_class_says_both_things():
    """The header is the board part and it is answered; the module is an owner-side purchase. Saying
    only NO_PART_CHOSEN lost the first half, and saying only BENCH_FITTED would lose the second."""
    rec = {"comment": "Geiger counter module (RadiationD-v1.1 class): 5 V, GND, pulse",
           "fp": "PinHeader_1x03_P2.54mm_Vertical", "code": "", "qty": 1}
    ev = jc.certify(rec, {}, {}, {})
    assert ev["verdict"] == "BENCH_FITTED", ev
    assert "owner-side purchase" in ev["note"], ev["note"]


def t_a_row_with_no_code_that_names_a_class_is_still_unanswered():
    rec = {"comment": "12 V class mixer fan on the pack node", "fp": "Fan_2Pin", "code": "", "qty": 1}
    assert jc.certify(rec, {}, {}, {})["verdict"] == "NO_PART_CHOSEN"


def t_a_connector_rows_prose_names_the_part_on_THIS_board_first():
    """E's J_DCIN read `vehicle and shore DC in 9-36 V, lead from the D38999 wall receptacle DC pair
    (JST-VH, 10 A)`. The part on the board is the JST-VH socket; the D38999 is the wall receptacle at
    the other end of the lead, and because it came first the certifier searched for it and answered
    with a 34.57 GBP Amphenol circular MIL connector at stock 0. A row's head names its own part."""
    bad = []
    for path in GEN:
        src = open(path, encoding="utf-8").read()
        fps = _fpmap(src)
        for m in CALL.finditer(src):
            fp = fps.get(m.group("fp")) or ""
            # Every row on one of these lands, coded or not: keying this on the presence of a code made
            # the rule vacuous on the very tree it was written to fail, because the rows whose prose was
            # wrong were exactly the rows that had no code.
            if not any(x in fp for x in ("JST_VH", "U.FL", "SMA_")):
                continue
            comment = re.search(r'part\(\s*"[^"]+"\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*"([^"]*)"', m.group(0))
            if not comment:
                continue
            want = jc.intended_part(comment.group(1))
            if want:
                bad.append("%s %s: its prose is searched for %r, not for the socket it is"
                           % (os.path.basename(path), m.group("ref"), want))
    assert not bad, "\n  ".join(bad)


def t_a_declared_part_number_inside_parentheses_still_finds_its_purchase_route():
    """C's three APEM toggles are declared, bought and excluded from the CPL, and read NOT_CHECKED for
    a month because the only part number in the row sat inside the parentheses that `intended_part`
    strips."""
    rec = {"comment": "SOS locking toggle, maintained (APEM 5636ADKB-2V, both positions latched)",
           "fp": "meshsat:APEM_5636_Panel", "code": "", "qty": 1}
    hf = {"5636ADKB-2V": "APEM through Mouser"}
    ev = jc.certify(rec, {}, hf, {})
    assert ev["verdict"] == "HAND_FIT", ev


def t_a_purchase_route_does_not_hide_a_package_mismatch():
    """A hand-fit declaration answers "JLCPCB cannot supply this", never "the part fits this land".
    Running it before the code check is how a TSSOP-38 on a QFN land would have gone out declared."""
    rec = {"comment": "LT8705A buck-boost controller, 38-lead QFN 5x7; bench-fitted",
           "fp": "Package_DFN_QFN:WQFN-38-1EP_5x7mm_P0.5mm_EP3.15x5.15mm", "code": "C674167", "qty": 1}
    cache = {"C674167": {"asked": _today, "list": [
        {"componentCode": "C674167", "componentModelEn": "LT8705AIFE#PBF", "componentBrandEn": "Analog Devices",
         "componentSpecificationEn": "TSSOP-38-EP-4.4mm", "componentLibraryType": "expand",
         "stockCount": 1, "initialPrice": 19.06}]}}
    ev = jc.certify(rec, cache, {"LT8705A": "Analog Devices through Mouser"}, {})
    assert ev["verdict"] == "PACKAGE_MISMATCH", ev


def t_a_declared_part_JLCPCB_cannot_supply_in_quantity_is_hand_fit_not_no_stock():
    rec = {"comment": "LT8705A buck-boost controller, 38-lead QFN 5x7; bench-fitted",
           "fp": "Package_DFN_QFN:WQFN-38-1EP_5x7mm_P0.5mm_EP3.15x5.15mm", "code": "C674164", "qty": 1}
    cache = {"C674164": {"asked": _today, "list": [
        {"componentCode": "C674164", "componentModelEn": "LT8705AEUHF#TRPBF", "componentBrandEn": "Analog Devices",
         "componentSpecificationEn": "QFN-38-EP(5x7)", "componentLibraryType": "expand",
         "stockCount": 3, "initialPrice": 24.55}]}}
    ev = jc.certify(rec, cache, {"LT8705A": "Analog Devices through Mouser"}, jc.declared(jc.ALIASES))
    assert ev["verdict"] == "HAND_FIT" and "stock 3" in ev["note"], ev


def t_a_socket_on_the_board_is_not_a_lead():
    """An `lcsc-allow.txt` line says JLCPCB never places that part. It is right for a solder land and a
    wire pad and wrong for a connector body: P's `(JST-PH` line covered the B2B-PH-K socket its own
    thermistor lead plugs INTO, and D's covered four more (a 1x4 hub port, two 1x5 headset sockets and
    the PA gate-bias 1x2). Five placeable connectors, in stock, were allow-listed as wire.

    So a row whose footprint is a connector BODY must carry a code, whatever its prose calls it. The
    solder lands stay exempt by their footprint (`SolderPad`, `SolderWire`, `TestPoint`), which is what
    a land actually is."""
    bodies = ("JST_PH_B", "JST_XH_B", "JST_VH_B", "AMASS_XT60", "U.FL_Hirose", "SMA_Amphenol",
              "HDMI_A_Molex", "Molex_Pico")
    # A row may take its code from lcsc_fill.py's map instead of from the generator, keyed on the
    # comment and the land, so the rule asks both: it is about whether the BOM line ends up with a
    # part, not about where the part number is written down.
    # lcsc_fill.py runs its work at module level, so the map is read out of the source rather than
    # imported. The key is (regex, footprint substring) and the value the code.
    import ast
    src = open(os.path.join(TOOLS, "lcsc_fill.py"), encoding="utf-8").read()
    start = src.index("MAP = {")
    depth = 0
    for i in range(start + 6, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    fill_map = ast.literal_eval(src[start + len("MAP = "):end])
    def filled(comment, fp):
        for (rx, key), _code in fill_map.items():
            if key in fp and re.search(rx, comment):
                return True
        return False
    bad = ["%s %s on %s" % (f, ref, fp.split(":")[-1]) for f, ref, fp, code, comment in _rows_with_comment()
           if any(b in fp for b in bodies) and not code and not filled(comment, fp)]
    assert not bad, ("a connector body carries no LCSC code and a lead exemption cannot cover it:\n  "
                     + "\n  ".join(bad))


def t_a_declaration_matches_a_row_by_prefix_not_by_character_count():
    """`9 A spring pin, pack return (Mill-Max 0858 class, dock block)` is 61 characters and its twin on
    the CELL+ side is 55, so keying a declaration on `comment[:60]` declared one of a matched pair and
    left the other reading NO_PART_CHOSEN. A declaration that is a prefix of the row matches it."""
    hf = {"9 A spring pin, pack return (Mill-Max 0858 class, dock block)": "Mill-Max through Digi-Key"}
    for c in ("9 A spring pin, pack return (Mill-Max 0858 class, dock block)",
              "9 A spring pin, pack return (Mill-Max 0858 class, dock block), four of them"):
        ev = jc.certify({"comment": c, "fp": "meshsat:Mill-Max_0858_power_pin", "code": "", "qty": 1}, {}, hf, {})
        assert ev["verdict"] == "HAND_FIT", (c, ev)


def t_a_short_declaration_does_not_swallow_rows_nobody_declared():
    hf = {"5 V": "somewhere"}
    ev = jc.certify({"comment": "5 V rail decoupling, 10u 0805", "fp": "Capacitor_SMD:C_0805_2012Metric",
                     "code": "", "qty": 1}, {}, hf, {})
    assert ev["verdict"] != "HAND_FIT", ev


def t_every_fill_rule_names_a_land_this_project_draws():
    """`lcsc_fill.py`'s MAP is keyed on (value regex, footprint substring), and a substring that matches no
    land we ever draw is a rule that can never fire. Owner ruling 10's two capacitor entries were written
    with "C1210" where the land is `C_1210_3225Metric`, so A24's finish refused the deliverable for 22 blank
    BOM lines on the very part the ruling chose. A key that matches nothing is worse than no key: the code
    reads as present."""
    import ast
    s = open(os.path.join(TOOLS, "lcsc_fill.py"), encoding="utf-8").read()
    start = s.index("MAP = {")
    depth = 0
    for i in range(start + 6, len(s)):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    fill_map = ast.literal_eval(s[start + len("MAP = "):end])
    # The denominator is every land that actually reaches a BOM, because that is what lcsc_fill reads, plus
    # the strings the generators name. Several lands are built by helpers (`idc("2x10")`), so a scan of the
    # generator source alone reports rules as dead that three shipped BOMs use.
    import glob as _glob
    lands = set()
    for path in GEN + [os.path.join(TOOLS, f) for f in os.listdir(TOOLS) if f.startswith("gen_footprints")]:
        src = open(path, encoding="utf-8").read()
        lands |= set(re.findall(r'"([A-Za-z0-9_.\- ]+:[A-Za-z0-9_.\-]+)"', src))
        lands |= set(re.findall(r'write\("([A-Za-z0-9_.\-]+)"', src))
    boards = os.path.join(os.path.dirname(os.path.dirname(TOOLS)), "release", "revA", "boards")
    for bom in _glob.glob(os.path.join(boards, "*", "*bom*.csv")):
        try:
            for row in csv.DictReader(open(bom, newline="", encoding="utf-8", errors="replace")):
                fp = (row.get("Footprint") or "").strip()
                if fp:
                    lands.add(fp)
        except Exception:
            pass
    blob = " ".join(lands)
    dead = sorted({key for _rx, key in fill_map if key and key not in blob})
    assert not dead, ("these fill rules name a footprint substring no generator draws, so they can never "
                      "fire: %s" % ", ".join(dead))
