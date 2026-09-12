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
import os, re, sys, glob, datetime

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
