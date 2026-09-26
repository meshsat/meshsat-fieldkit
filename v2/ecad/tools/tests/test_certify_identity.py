#!/usr/bin/env python3
"""CERTIFIED must mean the part we named on the land we drew (MESHSAT-1357, 26 September 2026).

Finding W6-F3 (25 September 2026, in the known design findings of v2/docs/ARCHITECTURE.md; confirmed by the
round-1 challenger calling the functions offline): `same_part` counted two parts as the same when they shared six
leading characters, or when one was contained in the other; the wider search stripped the grade letters the row
named; `norm_pkg` compared a package's family with no body size and no pitch; and a row carrying a code was taken
to be identified by it. Every fixture below is a row this project really certified, with the catalogue answer it
really got (JLC-CERTIFIED.tsv at 82dd1e4d, the line is named), or the sibling pair the challenger proved:

  BQ4050RSMR          the RSM package is 4 x 4 mm at 0.4 mm pitch; board P draws a 5 x 5 mm 0.5 mm QFN-32 land,
                      and QFN-32=VQFN-32 in package-aliases.txt let it through (table line 368, W6-F2);
  TE 1-2199119-5      on the M.2 B-key land of J_M2C2; TE's drawing C-2199119 rev F, sheet 2, gives -5 of the
                      1-2199119 series as KEY M (table line 424), and Quectel's RM520N-GL Hardware Design V1.0,
                      section 2.1, calls the module "a standard M.2 Key-B WWAN module"; and 2199119-5, the key B
                      part, was "the same" as 1-2199119-5 by containment, which is how a search for one answers the
                      other;
  TUSB2046BI          board D's hub; the catalogue part is TUSB2046BVFR, the commercial grade, and the wider search
                      stripped the "I" (table line 539, commit 07c57b30 "found on the wider search", W6-F5);
  STM32H753VITx       certified as STM32H743VIT6 on a seven-character prefix (table lines 482 to 484, W6-F1);
  LR2512-23R003F4     a 3 mOhm shunt certified as LR2512-23R005F4, a 5 mOhm one (table line 227);
  the fuse holders    rows naming no part on the Keystone 3568 land, certified on their codes: C4661, XSD's
                      "23.5*16*25" with no package (lines 194 to 196, boards A, E and P), and C10081, "GL5528(10-20)"
                      (lines 79 and 80, board E); C4661 first came from a search on a bare "25" (the table at
                      e0f3ef4f) and lcsc_fill then filled it into the BOMs;
  the panel LEDs      C2089, "8550SS-TA" in TO-92-3, certified as sixteen 3 mm LEDs on the class land LED_D3.0mm
                      (lines 228 to 243);
  the maker lands     SM04B-SRSS-TB on JST's BM04B-SRSS-TB land (line 374), Hirose U.FL-R-SMT(10) on the
                      U.FL-R-SMT-1 land (lines 543 to 548, passed by the reel code's "1"), and Q&J's CR2032-BS-6-1 on
                      the Keystone 3034 land, matched by the CELL size the row names (line 380).

The acceptable fixtures are the same table's rows whose land names the part they carry (JST B2P-VH, Hirose
U.FL-R-SMT-1(10), Amphenol 132134, Wuerth 692122030100, HRO TYPE-C-31-M-12): of the 63 CERTIFIED rows that carry a
code, name no part and have a package on one side only, those 34 must stay CERTIFIED.
"""
import os, sys, datetime

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import jlc_certify as jc

TODAY = datetime.date.today().isoformat()
ALIASES = jc.declared(jc.ALIASES)


def _answer(code, model, spec, stock=10000, brand="x"):
    return {"componentCode": code, "componentModelEn": model, "componentBrandEn": brand,
            "componentSpecificationEn": spec, "componentLibraryType": "expand", "stockCount": stock,
            "initialPrice": 1.0}


def _certify(comment, fp, code, answers, keyword=None, qty=1, more=None):
    cache = {(keyword or code): {"asked": TODAY, "list": answers}}
    for k, v in (more or {}).items(): cache[k] = {"asked": TODAY, "list": v}
    return jc.certify({"comment": comment, "fp": fp, "code": code, "qty": qty}, cache, {}, ALIASES)


# ---------------------------------------------------------------- same_part
NOT_THE_SAME = [
    ("TPS2065CDBV", "TPS2061CDBVR", "TPS2061C has an active-low enable (SLVSAU6I p.3)"),
    ("TPS2065CDBV", "TPS2069CDBVR", "TPS2069C is the 1.5 A part (SLVSAU6I p.3)"),
    ("TPS2065CDBV", "TPS2065DBVR", "the non-C family, a different datasheet (SLVS490K against SLVSAU6I)"),
    ("E22-900M30S", "E22-900M33S", "30 dBm against 33 dBm"),
    ("ATECC608B-SSHDA-T", "ATECC608A-SSHDA-T", "a different silicon revision"),
    ("BQ25731", "BQ25730RSNR", "a different charger"),
    ("STM32H753VITx", "STM32H743VIT6", "no CRYP, HASH or secure access mode (W6-F1)"),
    ("TUSB2046BI", "TUSB2046BVFR", "the commercial grade, 0 to 70 C (W6-F5)"),
    ("2199119-5", "1-2199119-5", "TE's leading digit is part of the number: key B against key M"),
    ("1-2199119-5", "2199119-5", "the same pair the other way round"),
    ("LR2512-23R003F4", "LR2512-23R005F4", "3 mOhm against 5 mOhm"),
    ("USB2517I-JZX", "USB2517-JZX", "the industrial grade against the commercial one"),
    ("132134-11", "132134", "the catalogue part names less than the row does"),
    ("1k", "X1kY", "too short to be contained credibly"),
    ("U.FL-R-SMT-1", "U.FL-R-SMT(10)", "Hirose's reel code (10) is not the -1 the land names"),
    ("BM04B-SRSS-TB", "SM04B-SRSS-TB(LF)(SN)", "JST's BM and SM are different parts"),
]
THE_SAME = [
    ("74LVC08APW", "SN74LVC08APWR", "TI's SN in front of a part named from its digits, and the reel"),
    ("74LVC86APW", "SN74LVC86APWR", "the same"),
    ("LM74700-Q1", "LM74700QDBVRQ1", "the ordering code sits before the qualifier the row named"),
    ("BQ34Z100-G1", "BQ34Z100PWR-G1", "the same shape on the gauge"),
    ("TPS2065CDBV", "TPS2065CDBVR", "the reel"),
    ("BQ4050RSMR", "BQ4050RSMR", "exactly"),
    ("TUSB2046BI", "TUSB2046BIRHBR", "every letter the row named, then the package and the reel"),
    ("U.FL-R-SMT-1", "U.FL-R-SMT-1(10)", "the reel code in parentheses"),
    ("B2P-VH", "B2P-VH-BL(LF)(SN)", "a suffix, then the finish codes in parentheses"),
]


def t_siblings_are_not_the_same_part():
    bad = [(w, g, why) for w, g, why in NOT_THE_SAME if jc.same_part(w, g)]
    assert not bad, "matched as the same part: %s" % "; ".join("%s = %s (%s)" % b for b in bad)


def t_the_same_part_under_its_order_code_is_still_the_same_part():
    bad = [(w, g, why) for w, g, why in THE_SAME if not jc.same_part(w, g)]
    assert not bad, "refused as a different part: %s" % "; ".join("%s != %s (%s)" % b for b in bad)


# ---------------------------------------------------------------- body and pitch
def t_the_bq4050_on_a_5x5_land_is_a_package_mismatch():
    """DEFECTIVE: board P's U1 as the table certified it (line 368)."""
    ev = _certify("BQ4050RSMR: SMBus 1.1 gas gauge, primary protection, 4S balancing (SLUSC67B)",
                  "QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm", "C157570",
                  [_answer("C157570", "BQ4050RSMR", "VQFN-32-EP(4x4)", 13771, "Texas Instruments")])
    assert ev["verdict"] == "PACKAGE_MISMATCH", ev
    assert "5 x 5" in ev["note"] and "4 x 4" in ev["note"], ev["note"]


def t_a_part_on_the_land_of_its_own_body_is_certified():
    """ACCEPTABLE: board A's BQ25731 on its 4 x 4 land (table line 365), and the BQ4050 on the land it needs."""
    ev = _certify("BQ25731RSNR 1 to 5 cell buck-boost charger, 4S from the 20 V bus, I2C 0x6B",
                  "QFN-32-1EP_4x4mm_P0.4mm_EP2.65x2.65mm", "C2871872",
                  [_answer("C2871872", "BQ25731RSNR", "QFN-32(4x4)", 1187, "Texas Instruments")])
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify("BQ4050RSMR: SMBus 1.1 gas gauge", "QFN-32-1EP_4x4mm_P0.4mm_EP2.8x2.8mm", "C157570",
                  [_answer("C157570", "BQ4050RSMR", "VQFN-32-EP(4x4)", 13771)])
    assert ev["verdict"] == "CERTIFIED", ev


def t_a_pitch_the_catalogue_states_is_compared():
    ev = _certify("JST-VH socket, 10 A: vehicle and shore DC in", "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "C274411",
                  [_answer("C274411", "B2P-VH-BL(LF)(SN)", "Plugin,P=3.96mm", 10946, "JST")])
    assert ev["verdict"] == "CERTIFIED", ev
    g = jc.pkg_geometry("QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm")
    assert g == {"body": (5.0, 5.0), "pitch": 0.5}, g
    assert jc.pkg_geometry("VQFN-32-EP(4x4)") == {"body": (4.0, 4.0), "pitch": None}
    assert jc.pkg_geometry("SMD,P=0.5mm")["pitch"] == 0.5


# ---------------------------------------------------------------- the M.2 key
B_KEY_ROW = ("M.2 B-key 3052 socket, TE 1-2199119-5, M2.5 standoff: Quectel RM520N-GL 5G module (PCIe or USB 2.0; "
             "two antenna leads to A22's 5G jacks)")


def t_a_key_m_socket_on_a_key_b_land_is_a_package_mismatch():
    """DEFECTIVE: board B's J_M2C2 as the table certified it (line 424); the key is TE's drawing's."""
    ev = _certify(B_KEY_ROW, "M2_B-Key_Socket_3052", "C574849",
                  [_answer("C574849", "1-2199119-5", "SMD,P=0.5mm", 8143, "TE Connectivity")])
    assert ev["verdict"] == "PACKAGE_MISMATCH", ev
    assert "key B" in ev["note"] and "key M" in ev["note"], ev["note"]


def t_a_key_b_socket_on_a_key_b_land_is_certified():
    ev = _certify("M.2 B-key 3052 socket, TE 2199119-3, M2.5 standoff", "M2_B-Key_Socket_3052", "C590866",
                  [_answer("C590866", "2199119-3", "SMD,P=0.5mm", 1432, "TE Connectivity")])
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify("M.2 E-key 2230 socket, TE 2199230-4, M2.5 standoff", "M2_E-Key_Socket_2230", "C2977809",
                  [_answer("C2977809", "2199230-4", "SMD,P=0.5mm,Surface Mount, Right Angle", 5000, "TE Connectivity")])
    assert ev["verdict"] == "CERTIFIED", ev
    ev = _certify("M.2 M-key 2242 socket, Amphenol MDT420M02001, M2.5 standoff", "M2_M-Key_Socket_2242", "C2927698",
                  [_answer("C2927698", "MDT420M02001", "SMD,P=0.5mm", 5000, "Amphenol ICC")])
    assert ev["verdict"] == "CERTIFIED", ev


def t_a_socket_whose_key_nothing_states_is_not_certified():
    ev = _certify("M.2 B-key 3052 socket, HOAUC HYCW01B-05NGFF-420B", "M2_B-Key_Socket_3052", "C41430835",
                  [_answer("C41430835", "HYCW01B-05NGFF-420B", "SMD", 661, "HOAUC")])
    assert ev["verdict"] == "NOT_CHECKED" and "key" in ev["note"], ev


def t_amphenol_s_key_is_read_from_its_own_order_code():
    ev = _certify("M.2 M-key 2242 socket, Amphenol MDT420B01001", "M2_M-Key_Socket_2242", "C4594496",
                  [_answer("C4594496", "MDT420B01001", "SMD,P=0.5mm", 4025, "Amphenol ICC")])
    assert ev["verdict"] == "PACKAGE_MISMATCH" and "key M" in ev["note"] and "key B" in ev["note"], ev


# ---------------------------------------------------------------- the grade letters and the wider search
TUSB = "TUSB2046BI four-port USB 2.0 full-speed hub (LQFP-32; BUSPWR low = self-powered, EXTMEM high, GANGED high, TSTMODE low)"


def t_the_commercial_hub_is_not_the_industrial_one_it_was_certified_as():
    """DEFECTIVE: board D's U4 as the table certified it today (line 539), by its code."""
    ev = _certify(TUSB, "LQFP-32_7x7mm_P0.8mm", "C167642",
                  [_answer("C167642", "TUSB2046BVFR", "LQFP-32(7x7)", 413, "Texas Instruments")])
    assert ev["verdict"] == "WRONG_MODEL", ev


def t_the_wider_search_keeps_the_letters_the_row_named():
    """DEFECTIVE: the same row before it carried a code (07c57b30): the search by the part answered the QFN
    industrial part and the LQFP commercial ones, and the wider search on TUSB2046 took the LQFP one."""
    first = [_answer("C2688010", "TUSB2046BIRHBR", "VQFN-32-EP(5x5)", 0), _answer("C167642", "TUSB2046BVFR", "LQFP-32(7x7)", 418),
             _answer("C167641", "TUSB2046BVF", "LQFP-32(7x7)", 10)]
    ev = _certify(TUSB, "LQFP-32_7x7mm_P0.8mm", "", first, keyword="TUSB2046BI", more={"TUSB2046": first})
    assert ev["verdict"] != "CERTIFIED", ev
    assert ev["verdict"] == "PACKAGE_MISMATCH", ev


def t_a_different_supervisor_and_a_different_shunt_are_wrong_models():
    ev = _certify("STM32H753VITx I/O supervisor A: 2-of-3 quorum on two CAN-FD fabrics, bank ownership and hub reset",
                  "LQFP-100_14x14mm_P0.5mm", "C114409",
                  [_answer("C114409", "STM32H743VIT6", "LQFP-100(14x14)", 4335, "STMicroelectronics")])
    assert ev["verdict"] == "WRONG_MODEL", ev
    ev = _certify("3 mOhm 1% 3 W 2512 shunt (RALEC LR2512-23R003F4): gauge SRP/SRN Kelvin (32.24 AV)",
                  "R_2512_6332Metric", "C154688", [_answer("C154688", "LR2512-23R005F4", "2512", 20000, "RALEC")])
    assert ev["verdict"] == "WRONG_MODEL", ev


# ---------------------------------------------------------------- a row that names nothing on a land that names nothing
def _without_board_allow_lists(fn):
    """Board A's lcsc-allow.txt declares the 25 A holder today, which is a later remedy for this row and not the
    mechanism; the fixture asks the certifier itself."""
    saved = jc.PROJECT_ALLOW; jc.PROJECT_ALLOW = {}
    try: return fn()
    finally: jc.PROJECT_ALLOW = saved


def t_a_search_answer_on_the_fuse_holder_land_is_not_the_holder():
    """DEFECTIVE: the pack's 25 A fuse holder before it carried a code (the table at e0f3ef4f). The search had a
    bare "25" to go on and C4661 came back CERTIFIED; the land names Keystone 3568, and C4661 is not that part."""
    c, f = "25 A mini blade (Keystone 3568 holder): the pack's fuse", "Fuse:Fuseholder_Blade_Mini_Keystone_3568"
    ev = _without_board_allow_lists(lambda: _certify(c, f, "", [_answer("C4661", "23.5*16*25", "-", 90000, "XSD")],
                                                     keyword=jc.jlc_keyword(c, f)))
    assert ev["verdict"] == "WRONG_MODEL" and "3568" in ev["note"], ev


# ---------------------------------------------------------------- a code is not its own identity
# The real rows, with the code each BOM carries and the catalogue's own line for it (JLC-CERTIFIED.tsv at
# 82dd1e4d). Each tuple: comment, land, code, model, brand, package, stock, table line.
WRONG_ON_THE_LAND = [
    ("25 A mini blade (Keystone 3568 holder): pack node to VBAT", "Fuseholder_Blade_Mini_Keystone_3568", "C4661",
     "23.5*16*25", "XSD", "-", 13016, 194),
    ("25 A mini blade (Keystone 3568 holder): pack to the block", "Fuseholder_Blade_Mini_Keystone_3568", "C4661",
     "23.5*16*25", "XSD", "-", 13016, 195),
    ("25 A mini blade (Keystone 3568 holder): the pack's fuse", "Fuseholder_Blade_Mini_Keystone_3568", "C4661",
     "23.5*16*25", "XSD", "-", 13016, 196),
    ("10 A mini blade (Keystone 3568 holder): panel input", "Fuseholder_Blade_Mini_Keystone_3568", "C10081",
     "GL5528(10-20)", "JCHL(Shenzhen Jing Chuang He Li Tech)", "Plugin,P=3.4mm", 30485, 79),
    ("10 A mini blade (Keystone 3568 holder): vehicle input", "Fuseholder_Blade_Mini_Keystone_3568", "C10081",
     "GL5528(10-20)", "JCHL(Shenzhen Jing Chuang He Li Tech)", "Plugin,P=3.4mm", 30485, 80),
    ("CM5 cooler fan (JST-SH 1.0): 5V GND TACHO PWM; 5 V from the Pi rail so the fan stops with the module",
     "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical", "C160404", "SM04B-SRSS-TB(LF)(SN)", "JST",
     "SMD,P=1mm,Surface Mount\uff0cRight Angle", 54085, 374),
    ("U.FL: MHF4 pigtail from the slot 1 WiFi card, chain A", "U.FL_Hirose_U.FL-R-SMT-1_Vertical", "C434808",
     "U.FL-R-SMT(10)", "HRS(Hirose)", "SMD", 19198, 543),
    ("CR2032 holder Keystone 3034: VBAT for the three modules' RTCs, the LG290P backup and the DS3231",
     "BatteryHolder_Keystone_3034_1x20mm", "C70377", "CR2032-BS-6-1", "Q&J", "-", 25141, 380),
]
NOTHING_IDENTIFIES = [
    ("3 mm BAT1 amber, sunlight viewable", "LED_D3.0mm", "C2089", "8550SS-TA(RANGE:160-300)",
     "Jiangsu Changjing Electronics Technology Co., Ltd.", "TO-92-3", 1357, 228),
    ("3 mm TX red (RF hazard), sunlight viewable", "LED_D3.0mm", "C2089", "8550SS-TA(RANGE:160-300)",
     "Jiangsu Changjing Electronics Technology Co., Ltd.", "TO-92-3", 1357, 243),
    ("panel ribbon from PCB-B (IDC 2x10, underside)", "IDC-Header_2x10_P2.54mm_Vertical_SMD", "C54803514",
     "JXT-IDC2.54-2X10P-A2", "JXTCONN", "SMD,P=2.54mm", 212, 590),
]
THE_LAND_S_OWN_PART = [
    ("JST-VH socket, 10 A: 5 V from A22 J_MEZZ_PWR1 (behind A22's 2 A eFuse U23): + -",
     "JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "C274411", "B2P-VH-BL(LF)(SN)", "JST", "Plugin,P=3.96mm", 10199, 407),
    ("SMA jack: PA output (coax from the RA30H1317M1 output on the plate)", "SMA_Amphenol_132134_Vertical",
     "C3174425", "132134", "Amphenol ICC", "Plugin", 1792, 457),
    ("U.FL socket: PA drive (coax to the RA30H1317M1 input on the plate)", "U.FL_Hirose_U.FL-R-SMT-1_Vertical",
     "C88373", "U.FL-R-SMT-1(10)", "HRS(Hirose)", "SMD", 10655, 540),
    ("USB 3.0 type A receptacle (Wuerth 692122030100 land): the LimeSDR Mini 2.4 in its bay",
     "USB3_A_Receptacle_Wuerth_692122030100", "C5355286", "692122030100", "Wurth Elektronik", "SMD", 120, 549),
    ("USB-C 2.0 receptacle", "USB_C_Receptacle_HRO_TYPE-C-31-M-12", "C165948", "TYPE-C-31-M-12",
     "Korean Hroparts Elec", "SMD", 116880, 551),
]


def _row(t, qty=1):
    comment, fp, code, model, brand, spec, stock, _line = t
    return _certify(comment, fp, code, [_answer(code, model, spec, stock, brand)], qty=qty)


def t_a_code_that_is_not_the_part_its_land_names_is_a_wrong_model():
    """DEFECTIVE: every row here was CERTIFIED on its code; each land names a maker's part the code is not."""
    got = [(t[7], _row(t)) for t in WRONG_ON_THE_LAND]
    bad = ["line %d: %s (%s)" % (ln, ev["verdict"], ev.get("note", "")[:80]) for ln, ev in got if ev["verdict"] != "WRONG_MODEL"]
    assert not bad, "still passed on a land drawn for another part: %s" % "; ".join(bad)


def t_a_code_on_a_class_land_with_a_one_sided_package_is_not_identified():
    """DEFECTIVE: a TO-92-3 part as the panel LEDs and a header nobody named, each CERTIFIED on its code alone."""
    got = [(t[7], _row(t)) for t in NOTHING_IDENTIFIES]
    bad = ["line %d: %s" % (ln, ev["verdict"]) for ln, ev in got if ev["verdict"] != "NOT_IDENTIFIED"]
    assert not bad, "certified with nothing identifying the answer: %s" % "; ".join(bad)


def t_a_code_that_is_the_part_its_land_names_is_certified():
    """ACCEPTABLE: the same kind of row (a code, no part in the prose, a package on one side at most) where the land
    names the part the code is. These must not move: a blanket rule on the row shape would flag all of them."""
    got = [(t[7], _row(t)) for t in THE_LAND_S_OWN_PART]
    bad = ["line %d: %s (%s)" % (ln, ev["verdict"], ev.get("note", "")[:80]) for ln, ev in got if ev["verdict"] != "CERTIFIED"]
    assert not bad, "refused the land's own part: %s" % "; ".join(bad)


def t_the_part_a_land_names_is_read_from_its_name():
    cases = {
        "Fuseholder_Blade_Mini_Keystone_3568": "3568",
        "Fuse:Fuseholder_Blade_Mini_Keystone_3568": "3568",
        "BatteryHolder_Keystone_3034_1x20mm": "3034",
        "JST_SH_BM04B-SRSS-TB_1x04-1MP_P1.00mm_Vertical": "BM04B-SRSS-TB",
        "JST_VH_B2P-VH_1x02_P3.96mm_Vertical": "B2P-VH",
        "U.FL_Hirose_U.FL-R-SMT-1_Vertical": "U.FL-R-SMT-1",
        "Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal": "FH12-22S-0.5SH",
        "Molex_PicoBlade_53047-1010_1x10_P1.25mm_Vertical": "53047-1010",
        "Radiall_SMPMAX_R222M00720": "R222M00720",
        "USB3_A_Receptacle_Wuerth_692122030100": "692122030100",
        # a class, a package or a family names no part
        "LED_D3.0mm": None, "IDC-Header_2x10_P2.54mm_Vertical_SMD": None, "R_0603_1608Metric": None,
        "Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm": None, "Oscillator_SMD_Abracon_ASE-4Pin_3.2x2.5mm": None,
        "Converter_DCDC_TRACO_TEN40-110xxWIRH_THT": None, "M2_B-Key_Socket_3052": None,
    }
    bad = ["%s -> %r, not %r" % (fp, jc.land_part(fp), want) for fp, want in cases.items() if jc.land_part(fp) != want]
    assert not bad, "; ".join(bad)


def t_a_jellybean_whose_answer_states_no_package_is_not_identified():
    """DEFECTIVE: "22u 50V X7R 1210" was certified as C165546 ("NXA50V22M5*11 LO", "Plugin,D5xL11mm"), because the
    catalogue line states no package this comparison reads and a one-sided package was skipped rather than compared
    (table row `22u 50V X7R 1210`). ACCEPTABLE: the same value answered in its 1210 package."""
    c, f = "22u 50V X7R 1210", "Capacitor_SMD:C_1210_3225Metric"
    ev = _without_board_allow_lists(lambda: _certify(c, f, "", [_answer("C165546", "NXA50V22M5*11 LO", "Plugin,D5xL11mm", 5000)],
                                                     keyword=jc.jlc_keyword(c, f)))
    assert ev["verdict"] == "NOT_IDENTIFIED", ev
    ev = _without_board_allow_lists(lambda: _certify(c, f, "", [_answer("C165546", "NXA50V22M5*11 LO", "Plugin,D5xL11mm", 5000),
                                                                _answer("C9999", "CL32B226KBJNNNE", "1210", 5000)],
                                                     keyword=jc.jlc_keyword(c, f)))
    assert ev["verdict"] == "CERTIFIED" and ev["code"] == "C9999", ev


# ---------------------------------------------------------------- a reading from before the change
def t_a_certification_taken_before_the_change_is_not_current_evidence():
    """DEFECTIVE: the tracked jlc_certify_c and jlc_certify_p verdicts (17 September 2026) read PASS over rows the
    corrected certifier refuses (sixteen LEDs certified as C2089 on board C, C4661 on board P's fuse land). Neither
    the rule's digest nor the evidence epoch moved, because the RULE did not change, so those readings would have
    stood as CMP-002 and SUP-001 PASS. ACCEPTABLE: a reading taken after the floor, and lcsc_fill, whose meaning did
    not change, are read as before."""
    import rules_status as S, rules_lib as R
    import datetime
    reg = R.load(); cov = S.coverage(); m = S.manifest(); fp = R.fingerprint(reg)
    for rid in ("CMP-002", "SUP-001"):
        rule = next(r for r in reg["rules"] if r["id"] == rid)
        floor = S._instant(cov[rid]["evidence_not_before"]["jlc_certify_<letter>"])
        after = (floor + datetime.timedelta(minutes=1)).astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        rec = lambda ts, res="PASS": {"ts": ts, "verdict": res, "denominator": 67, "counts": {},
                                      "policy": {"rule_set_fingerprint": fp}}
        old = {"jlc_certify_c": rec("2026-09-17T17:01:25Z"), "lcsc_fill": rec(after)}
        r = S.result_for(rule, "c", cov, old, m, fp)
        assert r["result"] == S.INCONCLUSIVE and "re-take" in r["why"], (rid, r)
        new = {"jlc_certify_c": rec(after), "lcsc_fill": rec("2026-09-17T17:01:25Z")}
        r = S.result_for(rule, "c", cov, new, m, fp)
        assert r["result"] == S.PASS, (rid, r)


def t_an_unreadable_floor_refuses_rather_than_passes():
    import rules_status as S
    ok, why = S._after_meaning_changed({"ts": "2026-09-27T00:00:00Z"}, "gate_x", {"evidence_not_before": {"gate_x": "soon"}}, "x")
    assert not ok and "cannot be read" in why, why
    ok, why = S._after_meaning_changed({"ts": "2026-09-27T00:00:00Z"}, "gate_x", {"evidence_not_before": "2026-09-26"}, "x")
    assert not ok, why
    ok, why = S._after_meaning_changed({}, "gate_x", {"evidence_not_before": {"gate_x": "2026-09-26T00:00:00Z"}}, "x")
    assert not ok, "a verdict with no time passed a floor"
    assert S._after_meaning_changed({"ts": "2026-09-01T00:00:00Z"}, "gate_y", {"evidence_not_before": {"gate_x": "2026-09-26T00:00:00Z"}}, "x")[0]
