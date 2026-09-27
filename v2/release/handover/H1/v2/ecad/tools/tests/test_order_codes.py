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
from harness import need, Skip

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
    need(os.path.join(TOOLS, "..", "..", "release", "revA", "boards"), "the lands that reach a shipped BOM are read from the deliverable folders")
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


def t_the_fab_note_reads_the_copper_weight_and_the_stackup_off_the_board():
    """13 September 2026. Two claims in the order notes were CONSTANTS and both were wrong on a board in the tree.

    `export_jlc.sh` named a stackup only when the board had four layers, so A24 and B16, which are built on
    JLC06161H-3313, went out asking JLCPCB to "tune for 90 ohm differential on the 7628 stackup", a stack
    they are not on; and the copper weight was the literal "1 oz", which owner ruling 7 of 12 September
    contradicts for P and E5, both of which carry 0.070 mm in their own stackup block. A note that asserts a
    fabrication property instead of reading it will drift from the board every time a stackup decision is
    taken, and the fab reads the note.

    Two halves. The constants must be gone from the note lines, and the expressions that replaced them must
    produce the right answer on the boards in the tree, which is checked without pcbnew by reading the same
    stackup block the script reads.
    """
    src = open(os.path.join(TOOLS, "export_jlc.sh")).read()
    # comments are excluded on purpose: the comment that records this defect quotes the old text verbatim,
    # and a rule that reads its own explanation as the defect can never be satisfied.
    note = "\n".join(l for l in src.split("\n")
                     if not l.lstrip().startswith("#") and ('"- Board:' in l or 'tune for 90 ohm' in l))
    assert note.strip(), "the fab-note lines were not found; this rule is looking at the wrong file"
    assert "1 oz outer copper" not in note, "the fab note still asserts a copper weight instead of reading it: %s" % note[:200]
    assert "on the 7628 stackup" not in note, "the fab note still names one stackup for every board: %s" % note[:200]

    REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
    want = {"meshsat-pcb-a-revA-A24": ("1 oz", "JLC06161H-3313"),
            "meshsat-pcb-d-revA-D10": ("1 oz", "JLC04161H-7628"),
            "meshsat-pcb-e-revA-E7": ("1 oz", "JLC04161H-7628"),
            "meshsat-pcb-p-revA-P3": ("2 oz", None),      # owner ruling 7
            "meshsat-pcb-e5-revA-E5": ("2 oz", None)}     # owner ruling 7
    for folder, (oz, stack) in want.items():
        b = glob.glob(os.path.join(REPO, "v2", "release", "revA", "boards", folder, "*.kicad_pcb"))
        if not b: continue                                 # a folder not in this clone is not this rule's business
        st = open(b[0], errors="replace").read()
        # BOTH s-expression forms, through the one reader (16 September 2026). KiCad writes a stackup layer
        # on one line when a tool writes the block and across several when pcbnew saves the file, and this
        # rule's own single-line expression would have failed on any folder cut from a board in the expanded
        # form, which boards A, D and E are in today.
        import stackup_read
        cu_mm = stackup_read.outer_copper_mm(st)
        assert cu_mm, "%s carries no stackup, so the note cannot read its copper weight" % folder
        got = "%g oz" % round(cu_mm / 0.035)
        assert got == oz, "%s reads %s where the record says %s" % (folder, got, oz)
        pp = re.findall(r'\(material "FR4 prepreg ([0-9]+)"', st)
        nl = len(re.findall(r'\(layer "(?:F|B|In\d+)\.Cu" \(type "copper"\)', st))
        got_stack = "JLC%02d161H-%s" % (nl, pp[0]) if pp else None
        assert got_stack == stack, "%s reads stackup %s where the record says %s" % (folder, got_stack, stack)


def t_a_manufacturers_prefix_on_an_order_code_is_the_same_part():
    """13 September 2026. An order code carries the manufacturer at the FRONT as well as the reel at the back.

    `same_part` compared suffixes and common prefixes from character one, so asking for 74LVC08APW and being
    answered SN74LVC08APWR, TI's own full order code, scored a common prefix of ZERO and two of board B's rows
    read WRONG_MODEL for exactly the part they asked for. The containment test that fixes it needs a floor or
    it pairs anything with anything; eight characters of letters and digits is the floor, and the rule must
    still refuse the real mismatches the certification found, which is what the second half checks.
    """
    for want, got in (("74LVC08APW", "SN74LVC08APWR"),      # TI prefix and reel
                      ("LM74700-Q1", "LM74700QDBVRQ1"),     # suffix in the middle
                      ("TPS2065CDBV", "TPS2065CDBVR")):     # the reel
        assert jc.same_part(want, got), "%s and %s are the same part and were not matched" % (want, got)
    # 26 September 2026 (MESHSAT-1357, finding W6-F3 of v2/docs/ARCHITECTURE.md's known design findings): TPS2065DBVR was in the list above until today. It is the
    # non-C TPS2065, a different family on a different datasheet (SLVS490K against SLVSAU6I), and this rule held
    # the defect as the expected answer. It is a mismatch.
    for want, got in (("ATECC608B-SSHDA-T", "BMI270"),      # the secure element against an IMU
                      ("1-2199119-5", "HYCW01B-05NGFF-420B"),   # TE M.2 socket against a house brand
                      ("MDT420M02001", "HYCW25M-05NGFF-230B"),
                      ("SMCJ15A", "SMCJ18A"),               # one digit apart and a different clamp voltage
                      ("TPS2065CDBV", "TPS2065DBVR"),       # the C part against the non-C family
                      ("1k", "X1kY")):                      # too short to be contained credibly
        assert not jc.same_part(want, got), "%s and %s are NOT the same part and were matched" % (want, got)


def t_a_maker_and_a_part_number_inside_parentheses_name_the_part():
    """Board B's HDMI receptacle reads "HDMI type A receptacle (Molex 208658-1001): cable to the Xenarc
    709GNK pass-through on the face plate". Parentheses are blanked before the search, for the good reason
    that they usually hold an explanation full of net names, so the only part number in the row was thrown
    away and the tool reached past it to 709GNK, which is the MONITOR the cable goes to. A correct order
    code read WRONG_MODEL for a fortnight.

    The refinement has to stay narrow: a bare `(RFBOUT2)` and a bare `(SX1262)` are still explanations, and
    position still decides, so `Ebyte E72-2G4M20S1E CC2652P` still means the module and not the chip in it.
    """
    import importlib.util, os
    spec = importlib.util.spec_from_file_location("jc", os.path.join(TOOLS, "jlc_certify.py"))
    jc = importlib.util.module_from_spec(spec); spec.loader.exec_module(jc)
    cases = [
        ("HDMI type A receptacle (Molex 208658-1001): cable to the Xenarc 709GNK pass-through on the face plate",
         "208658-1001", "the maker's part number inside the parentheses"),
        ("10.0k 1% (RFBOUT2)", None, "a bare parenthetical is a net name, not a part"),
        ("Ebyte E22-900M30S 1 W LoRa (SX1262)", "E22-900M30S", "the module, not the silicon inside it"),
        ("Ebyte E72-2G4M20S1E CC2652P", "E72-2G4M20S1E", "the first token still wins"),
        ("100nF 50V X7R (decoupling for U5)", None, "a jellybean with a lower-case explanation stays a jellybean"),
    ]
    for comment, want, why in cases:
        got = jc.intended_part(comment)
        if got != want:
            raise AssertionError("%s: asked for %r, the tool says %r (%s)" % (why, want, got, comment[:60]))


def t_a_hole_is_not_a_bom_line():
    """C17's deliverable was refused for 'every BOM designator is in the CPL (142 of 144; missing CAM_H1, CAM_H2)': the
    two camera holes are Mechanical:MountingHole symbols on the library MountingHole footprint, which KiCad keeps out
    of the position file, so they reached the BOM and not the CPL (15 Sep 2026). A mechanical hole declares in_bom=False."""
    import re
    src = open(os.path.join(TOOLS, "gen_sch_c.py")).read()
    line = next(l for l in src.split("\n") if 'part("CAM_H%d"' in l)
    assert "in_bom=False" in line, "the camera holes still reach the BOM"
    k = open(os.path.join(TOOLS, "kisch.py")).read()
    assert 'in_bom=p.get("in_bom", True)' in k and "or not in_bom else" in k, "kisch does not carry a part's in_bom flag into the symbol"


def t_no_placement_generator_writes_a_literal_phase_into_a_legend():
    """C17's folder was refused by the final gate for 'no other phase of this board on the silk (stale: C7)': gen_pcb_c3.py
    wrote the legend 'C7 BACKER RING: ...' as a literal while the title text took its phase from the chain (15 Sep 2026).
    The phase reaches the silk through PHASE and silk_fix_all.py, never as a literal in a legend."""
    import re
    for L in "abcdep":
        p = os.path.join(TOOLS, "gen_pcb_%s3.py" % L)
        if not os.path.exists(p): continue
        for line in open(p):
            if line.lstrip().startswith("#"): continue
            # a phase token is the BOARD'S OWN letter with digits (C7 on C); F3 on E is a fuse's designator, not a phase
            m = re.search(r'text\("(' + L.upper() + r'\d{1,2}) ', line)
            assert not m, "%s writes the literal phase %s into a legend: %s" % (os.path.basename(p), m.group(1), line.strip()[:90])


# 16 September 2026: A VALUE IS THE BOM'S COMMENT COLUMN, AND A COMMENT NOTHING MATCHES IS A BLANK LINE.
# Board A gained six charger sense filter parts whose values carried their reason: "10n (CDIFF across the
# input sense, 100 ns with the 10 R)". `lcsc_fill.py` matches its map with `re.match`, so `^10n$` misses that
# string, and the certified table is keyed on the comment exactly, so it misses it too: six blank BOM lines
# and a finish that refuses the board, discovered on a rented box rather than here. The reasoning belongs in
# a comment beside the call. This rule is the general form, and it costs nothing to keep true.
_PASSIVE = re.compile(r'\b([rc])\(\s*"([^"]+)"\s*,\s*"([^"]*)"(?P<rest>[^\n]*)')


def _fill_routes():
    """The three ways a BOM comment gets a code: the map's regexes, the certified table, an allow line."""
    src = open(os.path.join(TOOLS, "lcsc_fill.py"), encoding="utf-8").read()
    # the slice ends at the line that reads the BOM path, wherever it now sits: a door added above it for a
    # board that places no part moved it away from the MAP's closing brace (17 September 2026).
    body = src[src.index("MAP = {"):src.index("path = sys.argv[1]")]
    pats = [p for p, _fp in re.findall(r'\(r"([^"]+)"\s*,\s*"([^"]+)"\)', body)]
    cert = set()
    table = os.path.join(os.path.dirname(TOOLS), "..", "release", "revA", "order", "JLC-CERTIFIED.tsv")
    if os.path.exists(table):
        for row in csv.DictReader(open(table, errors="replace"), delimiter="\t"):
            if (row.get("verdict") or "").strip() == "CERTIFIED" and (row.get("code") or "").strip():
                cert.add((row.get("comment") or "").strip())
    allow = []
    for f in glob.glob(os.path.join(os.path.dirname(TOOLS), "pcb-*", "lcsc-allow.txt")):
        for line in open(f, errors="replace"):
            line = line.split("#")[0].strip()
            if line:
                allow.append(line)
    return pats, cert, allow


def _unfillable(src, pats, cert, allow):
    out = []
    for m in _PASSIVE.finditer(src):
        ref, val, rest = m.group(2), m.group(3), m.group("rest")
        if re.search(r'"C\d{4,}"', rest):            # the call names its own code
            continue
        if val in cert or any(re.match(p, val) for p in pats) or any(a in val for a in allow):
            continue
        out.append((ref, val))
    return out


def t_every_passive_value_a_generator_writes_can_be_given_a_code():
    need(os.path.join(os.path.dirname(TOOLS), "..", "release", "revA", "order", "JLC-CERTIFIED.tsv"),
         "the certified table is not in this tree")
    pats, cert, allow = _fill_routes()
    bad = []
    for path in GEN:
        bad += [(os.path.basename(path),) + row for row in
                _unfillable(open(path, encoding="utf-8").read(), pats, cert, allow)]
    assert bad == [], "values no code rule and no certified row can fill: %s" % bad[:8]
    # The defective fixture: the six calls as they were written this morning. Every one of them must be
    # refused, or the rule passes on the tree it was written against.
    before = ('r("R146", "10R (ACN filter, BQ25731 10.2.2.2)", "CH_ACN", "CH_ACN_F")\n'
              'c("C121", "10n (CDIFF across the input sense, 100 ns with the 10 R)", "CH_ACP_F", "CH_ACN_F")\n'
              'c("C122", "100n (across the charge sense resistor, BQ25731 pin 19)", "CH_SRP_F", "CH_SRN_F")\n')
    caught = _unfillable(before, pats, cert, allow)
    assert len(caught) >= 2, "the rule does not refuse the values it was written against: %s" % caught


def t_every_board_of_the_set_gets_a_contracts_verdict_even_when_nothing_names_it():
    """16 September 2026. The cross-board contracts were written for the five boards that share connectors, so
    board P, whose pack leads are two 12 AWG wires to board E's XT60, was not in the set at all and rule
    SCH-003 read INCONCLUSIVE on it for want of a verdict rather than for want of agreement. A wire is a
    conductor. And board E5 has no schematic by construction, its targets being generated from board A's own
    BOARD file, so it cannot be judged here and now says that instead of producing nothing."""
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    assert '"P": "pcb-p-pack"' in src, "board P is not in the contract set"
    assert 'check_contracts_e5' in src, "board E5 gets no verdict at all"
    assert "W_P" in src and "J_BATT" in src, "the pack's two wires are not checked against the XT60 they land on"
    # the polarity contract is the one that matters: getting it wrong destroys a board rather than failing a test
    i = src.index("the pack pair is not crossed")
    assert "boards={\"E\", \"P\"}" in src[i - 400:i + 200], "the polarity check does not name both boards"


def t_a_value_that_names_a_frequency_is_checked_against_the_part_that_was_found():
    """Board D's two crystals read "6 MHz 3225" and carried C448646, which JLCPCB's own catalogue calls
    NX3225SA-25MHz. Both were CERTIFIED, because same_part compares a manufacturer PART NUMBER and a
    jellybean row names none, so the row was decided on package and stock alone. A hub whose PLL wants 6 MHz
    does not enumerate at 25."""
    import jlc_certify as J
    bad = J.frequency_conflict("6 MHz 3225 (CL 20 pF; C1 = C2 = 27 pF)",
                               dict(desc="NX3225SA 25MHz 8pF", model="NX3225SA-25MHz-STD-CSR-6", code="C448646"))
    assert bad and "6 MHz" in bad and "25 MHz" in bad, bad
    ok = J.frequency_conflict("12 MHz ABM8-272-T3 (3225): 1 XIN, 3 XOUT",
                              dict(desc="12MHz 30ppm 10pF", model="ABM8-272-T3", code="C20625731"))
    assert ok is None, ok


def t_a_frequency_that_is_a_condition_is_not_a_part_number():
    """A ferrite is specified AT a frequency and an inductor's catalogue line may name its self-resonance:
    neither is the part. Only a value that BEGINS with a frequency is one."""
    import jlc_certify as J
    assert J.frequency_conflict("600R@100MHz", dict(desc="600Ohm@100MHz 0603", model="X", code="C1002")) is None
    assert J.frequency_conflict("68nH 0805 (LPF, 145 MHz 5th order)",
                                dict(desc="68nH 1.2A SRF 1.5GHz", model="LQW2BAN68NG00L", code="C2044803")) is None


def t_the_frequency_guard_is_applied_to_the_result_and_not_at_each_return():
    """certify() has four places that write CERTIFIED. A guard repeated at each of them is one a fifth return
    will miss, so it is applied once, to what certify returns."""
    src = open(os.path.join(TOOLS, "jlc_certify.py"), encoding="utf-8").read()
    assert "def _certify(" in src, "the guarded implementation is not separated from the guard"
    i = src.index("def certify(")
    w = src[i:i + 900]
    assert "_certify(" in w and "frequency_conflict(" in w, "certify does not apply the guard to its result"


def t_the_certification_decides_each_board_on_its_own_rows():
    """One board's wrong part was failing two BLOCKER rules on all seven, 17 September 2026.

    Board D asks for two 6 MHz crystals that do not exist in the land it draws and was certified against a
    25 MHz part (owner decision 37). `jlc_certify` wrote ONE verdict for the whole set, and rules CMP-002 (the
    package on the land is the package ordered) and SUP-001 (every placed part is buyable) are PER BOARD and
    read it: four boards that carry no crystal at all failed both. It is the composite-verdict shape the set
    gate and the contract check were each split for, one rule further on.

    A row already names the boards it sits on, so each board is asked about its own rows and nobody else's.
    A board in the manifest whose deliverable carries no component row gets a DECLARED zero, because an
    undeclared zero reads as an absence and both rules would go INCONCLUSIVE on a bare board that cannot fail
    them."""
    src = open(os.path.join(TOOLS, "jlc_certify.py"), encoding="utf-8").read()
    assert 'verdict.write("jlc_certify_%s" % _l' in src, "the certification writes no per-board verdict"
    assert "a declared zero, not an absence" in src, "a board with no rows is left silent"
    cov = open(os.path.join(TOOLS, "pcb_rules_coverage.yaml"), encoding="utf-8").read()
    assert "jlc_certify_<letter>" in cov, "the rules still read the set's certification verdict"
    assert 'verdict: "jlc_certify,' not in cov, "a rule still names the set verdict directly"


def t_the_per_board_certification_was_written_for_every_board_of_the_manifest():
    """Executed against whatever this tree holds: if the verdicts are there, every manifest board has one."""
    import json, glob
    ecad = os.path.dirname(TOOLS)
    found = {os.path.basename(p)[len("jlc_certify_"):-len(".verdict.json")]
             for p in glob.glob(os.path.join(ecad, "out", "jlc_certify_*.verdict.json"))}
    if not found: raise Skip("the certification has not run in this tree")
    sys.path.insert(0, TOOLS)
    import rules_status as _rs
    want = {b.lower() for b in (_rs.manifest().get("boards") or {})}
    assert want <= found, "no certification verdict for %s" % sorted(want - found)


def t_a_rotation_is_asked_only_of_a_part_the_assembler_places():
    """17 September 2026. The first form of the assembly check listed every polarised footprint in the
    netlist, which is 41 across the seven boards, and many of them are parts JLCPCB never sees: board A's
    blind-mate receptacles and spring pins, board C's plate switches and sounder and camera, board E's blade
    holders and pack lands, board P's wire joints. Asking the ordering session to compare those with an
    assembler's preview is asking it to verify a rotation nobody will apply.

    The bench-fit table is a literal in make_handoff.py, which is on the never-auto floor and needs pcbnew, so
    it is read by TEXT and never imported, the way the rotation offsets already are."""
    import sys as _s
    _s.path.insert(0, TOOLS)
    import assembly_set as A
    a = A.bench_fitted("pcb-a-power")
    assert "J_DOCK" in a and "J_BM11" in a and "J_CP4" in a, sorted(a)[:10]
    assert "F1" in a, "the blade holder is bench-fitted on board A"
    assert A.bench_fitted("pcb-b-compute") == set(), "board B declares no bench-fitted part"
    assert A.bench_fitted("pcb-nonesuch") == set(), "an unknown board must yield nothing, not everything"
    src = open(os.path.join(TOOLS, "assembly_set.py"), encoding="utf-8").read()
    assert "import make_handoff" not in src, "the table is imported rather than read, and that file needs pcbnew"
    assert "are bench-fitted and never reach the" in src, "the exclusion is silent"


def t_a_board_is_certified_from_the_folder_it_declares_and_never_from_the_newest():
    """THE NEWEST FOLDER IS NOT THE BOARD (17 September 2026).

    `newest_boms` took the highest phase number per letter, so board A was certified from the A24 folder while
    the board this tree holds is A32, and board D from D11 against a tree holding D12. CMP-002 and SUP-001 are
    per-board rules, so both boards were being answered about a board this project is not building: one of
    them read PASS and the other read a failure, and neither was about the board in the tree. `gate_sweep.sh`
    already refuses that case in as many words; the set gate supplied it, so the two disagreed.

    Executed on a temporary release tree with a temporary board table: a folder at the declared phase is
    chosen, a newer folder at another phase is NOT, and a board with no folder at its declared phase comes
    back named as missing rather than certified from whatever exists.
    """
    import os, sys, json, tempfile, shutil
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLS)
    import jlc_certify as J
    d = tempfile.mkdtemp(prefix="certify-folder-")
    try:
        boards = os.path.join(d, "boards"); tools = os.path.join(d, "tools", "boards")
        os.makedirs(tools)
        for phase in ("X7", "X9"):
            f = os.path.join(boards, "meshsat-pcb-x-revA-%s" % phase); os.makedirs(f)
            open(os.path.join(f, "pcb-x-bom.csv"), "w").write("Comment,Designator,Footprint,LCSC Part #\n")
        f = os.path.join(boards, "meshsat-pcb-y-revA-Y3"); os.makedirs(f)
        open(os.path.join(f, "pcb-y-bom.csv"), "w").write("Comment,Designator,Footprint,LCSC Part #\n")
        json.dump({"phase": "X7"}, open(os.path.join(tools, "x.json"), "w"))
        json.dump({"phase": "Y4"}, open(os.path.join(tools, "y.json"), "w"))   # the tree holds no Y4 folder

        got = J.newest_boms(boards_dir=boards, tools=os.path.dirname(tools))
        assert "x" in got and got["x"][1].endswith("X7"), \
            "board x declares X7 and was certified from %r, the newest folder rather than its own" % (got.get("x"),)
        assert "y" not in got, "board y has no folder at its declared phase Y4 and was certified from Y3 anyway"
        miss = J.newest_boms.missing
        assert "y" in miss and miss["y"][0] == "Y4" and "Y3" in miss["y"][1], \
            "the missing folder is not named with the phase that was wanted and the phases that exist: %r" % (miss,)
        assert "x" not in miss
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_a_row_the_declared_folder_carries_without_a_code_is_not_given_an_older_folders_code():
    """A DECLARED FOLDER'S BLANK IS AN ANSWER (26 September 2026, the decision 41 re-take).

    The declared folder went first so that its code would win, and a BLANK in it did not: the first non-empty code
    won, so a row the declared folder carries with no code took the code an older folder of the same board had.
    Board C's sixteen 3 mm panel lamps carry no code in C24, where they are bench-fitted and allow-listed, and
    C2089 (an 8550SS transistor in TO-92-3) in C17; the per-board verdict failed C24 NOT_IDENTIFIED sixteen times
    for a code C24 does not order.

    DEFECTIVE, on a temporary release: X9 is declared and carries the row blank, X7 carries it with a code; the
    row must come back with no code. ACCEPTABLE: a row only the older folder carries keeps its code, because the
    table is also this project's knowledge of what can be bought."""
    import tempfile, shutil, json
    sys.path.insert(0, TOOLS)
    import jlc_certify as J
    d = tempfile.mkdtemp(prefix="certify-blank-")
    try:
        boards = os.path.join(d, "boards"); tools = os.path.join(d, "tools", "boards"); os.makedirs(tools)
        rows = {"X7": 'Comment,Designator,Footprint,LCSC Part #\n"3 mm lamp",D1,LED_D3.0mm,C2089\n"old only 10k",R9,R_0603_1608Metric,C25804\n',
                "X9": 'Comment,Designator,Footprint,LCSC Part #\n"3 mm lamp",D1,LED_D3.0mm,\n'}
        for ph, text in rows.items():
            f = os.path.join(boards, "meshsat-pcb-x-revA-%s" % ph); os.makedirs(f)
            open(os.path.join(f, "pcb-x-bom.csv"), "w").write(text)
        json.dump({"phase": "X9"}, open(os.path.join(tools, "x.json"), "w"))
        got = J.rows_to_check(boards_dir=boards, tools=os.path.dirname(tools))
        lamp = got[("3 mm lamp", "LED_D3.0mm")]
        assert lamp["code"] == "", "the declared folder's blank took an older folder's code: %r" % lamp["code"]
        old = got[("old only 10k", "R_0603_1608Metric")]
        assert old["code"] == "C25804", "a row only an older folder carries lost its code: %r" % old
        decl = J.rows_to_check(declared_only=True, boards_dir=boards, tools=os.path.dirname(tools))
        assert set(decl) == {("3 mm lamp", "LED_D3.0mm")}, sorted(decl)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def t_no_allow_line_covers_a_part_on_a_passive_land_of_a_declared_folder():
    """AN ALLOW LINE NAMES WHAT IT COVERS, NOT A WORD IT SHARES (26 September 2026).

    Board C's and board E's `BOOTSEL` line was written for the solder jumper ("BOOTSEL: short while powering...")
    and, being a substring, also covered "1k (BOOTSEL)", the RP2040's boot resistor, a real part JLCPCB places:
    C24's BOM carries that resistor with no code and every gate read it as declared. The line is `BOOTSEL:` now.

    The property, on every folder at its board's declared phase: no blank row on a resistor, capacitor or inductor
    land is covered by an allow line of its own board. DEFECTIVE fixture: the old line against the resistor.
    ACCEPTABLE: the narrowed line covers the jumper and not the resistor."""
    passive = re.compile(r"^(?:R|C|L)_(?:0201|0402|0603|0805|1206|1210|1812|2010|2512)_")
    def covered(allow, comment): return [a for a in allow if a in comment]
    assert covered(["BOOTSEL"], "1k (BOOTSEL)"), "the defective fixture no longer reproduces the defect"
    assert not covered(["BOOTSEL:"], "1k (BOOTSEL)") and covered(["BOOTSEL:"], "BOOTSEL: short while powering")
    sys.path.insert(0, TOOLS)
    import jlc_certify as J, rules_status as RS
    ecad = os.path.dirname(TOOLS)
    bad = []
    for letter, (bom, folder) in sorted(J.newest_boms().items()):
        try: pd = RS._phase_dir(letter, RS.manifest())
        except Exception: continue
        ap = os.path.join(pd, "lcsc-allow.txt")
        if not os.path.exists(ap): continue
        allow = [l.split("#", 1)[0].strip() for l in open(ap, errors="replace") if "#" in l and l.split("#", 1)[0].strip()]
        for r in csv.DictReader(open(bom, errors="replace")):
            if (r.get("LCSC Part #") or "").strip() or not passive.match(r.get("Footprint") or ""): continue
            hit = covered(allow, r.get("Comment") or "")
            if hit: bad.append("%s %s %r covered by %r" % (folder, r.get("Designator"), r.get("Comment"), hit))
    assert not bad, "an allow line covers a real part on a passive land: %s" % bad[:6]


def t_a_run_about_one_board_does_not_rewrite_the_set_s_certification_table():
    """`JLC-CERTIFIED.tsv` IS THE ORDER SET'S RECORD AND A SCOPED RUN WAS OVERWRITING IT (17 September 2026).

    The table is 720 rows over every deliverable folder and it is what this project reads to know whether a
    value can be bought at all. `jlc_certify.py --boards c` wrote 88 rows over it: every other board's parts
    disappeared from the file a person reads while placing an order, and nothing said so. Same shape as the
    scoped readiness run of the same morning, same answer: a narrowed run writes its own table beside its own
    verdicts and leaves the set's alone.

    Executed against the source, because running the real certification needs the network: the guard must be
    there, keyed on the scope and on the table being the set's own.
    """
    import os
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src = open(os.path.join(TOOLS, "jlc_certify.py"), errors="replace").read()
    i = src.find("def main(")
    assert i > 0
    body = src[i:]
    j = body.find("rows = rows_to_check(")
    assert j > 0, "the certification no longer builds its rows where this rule looks"
    head = body[:j]
    assert "if only and os.path.abspath(a.table) == os.path.abspath(TABLE):" in head, \
        ("a run scoped with --boards still writes the set's table: %s" % TOOLS)
    assert "a.table = os.path.join(a.out_dir" in head, \
        "the scoped run has no table of its own to write instead"
