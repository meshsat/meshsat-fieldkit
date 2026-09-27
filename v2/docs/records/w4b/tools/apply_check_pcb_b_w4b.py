#!/usr/bin/env python3
"""Stream w4b (MESHSAT-1357, 27 September 2026): a DRAFT for the owner of v2/ecad/tools/check_pcb_b.py, not applied in the
stream's worktree. Usage: apply_check_pcb_b_w4b.py <path to check_pcb_b.py> [--check]

Board B's gate asserts round 8's EMCON topology net by net, and stream w4b's three circuit changes move three of its
assertions. Each edit states the new topology with the maker's bounds, as the round 8 lines do; none relaxes a check:
  W4B-D1  EMCON_HW's IC loads gain U536 pin 1 (the RockBLOCK's I_EN gate) and, W4B-D3, U116, U216 and U316 pin 1; and a
          new check: J_RB9704 pin 3 (RB_IEN) is driven only by U536 = EMCON_HW AND RB_SW_IEN, with one pull-down to GND,
          and RB_SW_IEN carries U6 pin 19, U536 pin 2 and one pull-down to GND.
  W4B-D2  the enables of U23, U24 and U21 sit on their own nodes (LIME_UVLO, RB_UVLO, E22_UVLO) at 0.6 of the gate
          output: the gate output net carries the gate and one series resistor; the node carries that resistor, the
          switch's EN pin and one pull-down to GND; the ratio keeps the node under the switches' 1.08 V turn-off minimum
          with the gate's output at its 1.65 V band edge, over 1.30 V with it at 2.4 V (VOH, 16 mA, VCC 3 V), and the
          pull-down holds the node under 0.5 V against the gate's 10 uA Ioff plus the pin's 0.1 uA. E72_EN keeps round
          8's form.
  W4B-D3  each slot's card buck EN (S{s}A_EN) carries exactly the buck's EN pin and U{s}16's output, U{s}16 = EMCON_HW AND
          PCIE_PWR_EN{s} run from +5V_S{s} (the buck's own input), and U{s}15's 2A is on GND.
Every edit asserts the text it replaces and the file is re-parsed after. --check applies nothing."""
import sys, ast

EMCON_IN_OLD = '''    _EMCON_IN = {"U112": "2", "U212": "2", "U312": "2", "U501": "1", "U503": "1", "U504": "1", "U505": "1", "U506": "2"}'''
EMCON_IN_NEW = '''    # Stream w4b (27 September 2026): U536 pin 1 (the RockBLOCK's I_EN gate, W4B-D1) and each slot's card-buck enable gate U116,
    # U216, U316 pin 1 (W4B-D3, run from the slot's own 5 V) read the line as well.
    _EMCON_IN = {"U112": "2", "U212": "2", "U312": "2", "U501": "1", "U503": "1", "U504": "1", "U505": "1", "U506": "2",
                 "U536": "1", "U116": "1", "U216": "1", "U316": "1"}'''
CARD_EN_OLD = '''        _en = "S%dA_EN" % _sl
        check(_pads.get(_u15, {}).get("3") == _eon and _pads.get(_u15, {}).get("4") == _en and ("U%d03" % _sl, "3") in bypad.get(_en, set())
              and _one_r(_en) == ["PCIE_PWR_EN%d" % _sl],
              "%s: the card buck U%d03's EN comes from PCIE_PWR_EN%d through one resistor and %s 2Y pulls it low under EMCON (one resistor away %s)"
              % (_en, _sl, _sl, _u15, _one_r(_en)))'''
CARD_EN_NEW = '''        _en = "S%dA_EN" % _sl
        # Stream w4b (W4B-D3, 27 September 2026): the card buck's EN is driven only by U{s}16 = EMCON_HW AND PCIE_PWR_EN{s}, an
        # SN74LV1T08 run from +5V_S{s}, the buck's own input (U{s}03 pin 2), so the enable is held whenever the buck has an input;
        # R{s}64 and U{s}15's 2Y are off the node, and U{s}15's 2A sits on GND (SCES307J 6.3 note 1).
        _u16 = "U%d16" % _sl
        check(sorted(bypad.get(_en, set())) == sorted([("U%d03" % _sl, "3"), (_u16, "4")])
              and {k: v for k, v in _pads.get(_u16, {}).items()} == {"1": "EMCON_HW", "2": "PCIE_PWR_EN%d" % _sl, "3": "GND", "4": _en, "5": "+5V_S%d" % _sl}
              and _pads.get("U%d03" % _sl, {}).get("2") == "+5V_S%d" % _sl and _pads.get(_u15, {}).get("3") == "GND",
              "%s: the card buck U%d03's EN is driven only by %s = EMCON_HW AND PCIE_PWR_EN%d, run from the buck's own input +5V_S%d, "
              "and %s's 2A is on GND (pads on the net %s; %s pads %s)"
              % (_en, _sl, _u16, _sl, _sl, _u15, sorted(bypad.get(_en, set())), _u16, _pads.get(_u16)))'''
EN_OLD = '''    _R_MAX = 0.50 / (10e-6 + 0.1e-6); _R_MIN = 2.4 / 12e-3
    for _en, _drv, _load in (("LIME_EN", ("U502", "4"), ("U23", "3")), ("RB_EN", ("U503", "4"), ("U24", "3")),
                             ("E22_EN", ("U504", "4"), ("U21", "5")), ("E72_EN", ("U505", "4"), ("U22", "5"))):'''
EN_NEW = '''    _R_MAX = 0.50 / (10e-6 + 0.1e-6); _R_MIN = 2.4 / 12e-3
    # L4 CASE (2), stream w4b (W4B-D2, 27 September 2026): the LimeSDR's, RockBLOCK's and E22's switch enables sit on their own
    # node at about 0.6 of the gate's output. The gate's net carries the gate output and one series resistor; the node carries
    # that resistor, the switch's EN pin and one pull-down to GND (a test point may share either). Bounds, 1 percent parts: with
    # the gate at its band edge, 1.65 V (VO 0 to VCC, SCES217AA 5.3), the node stays under 1.08 V, the TPS259631's VUVLO(F) and
    # the TPS22810's VENF minimum (SLVSET8A 7.5, SLVSDH0C 7.5); with the gate high, VOH 2.4 V at 16 mA and VCC 3 V (SCES217AA 5.5),
    # it exceeds 1.30 V, both parts' rising maximum; and the pull-down holds the node under 0.5 V (VSHUTF, VSD) against the gate's
    # 10 uA Ioff plus the pin's 0.1 uA.
    def _tol_ohms(v):
        return (_ohms(v), 0.01 if "1%" in (v or "") else 0.05)
    for _en, _node, _drv, _load in (("LIME_EN", "LIME_UVLO", ("U502", "4"), ("U23", "3")), ("RB_EN", "RB_UVLO", ("U503", "4"), ("U24", "3")),
                                    ("E22_EN", "E22_UVLO", ("U504", "4"), ("U21", "5"))):
        _ser = sorted(r for r in bynet.get(_en, set()) & bynet.get(_node, set()) if r.startswith("R"))
        _dn = sorted(r for r in bynet.get(_node, set()) if r.startswith("R") and sorted(_pads.get(r, {}).values()) == sorted([_node, "GND"]))
        _oth_en = sorted(p for p in bypad.get(_en, set()) if p != _drv and p[0] not in _ser and not p[0].startswith("TP"))
        _oth_nd = sorted(p for p in bypad.get(_node, set()) if p != _load and p[0] not in _ser + _dn and not p[0].startswith("TP"))
        _ok = len(_ser) == 1 and len(_dn) == 1 and _drv in bypad.get(_en, set()) and _load in bypad.get(_node, set()) and not _oth_en and not _oth_nd
        if _ok:
            (_rs, _ts), (_rd, _td) = _tol_ohms(byval.get(_ser[0])), _tol_ohms(byval.get(_dn[0]))
            _ok = _rs is not None and _rd is not None
        if _ok:
            _k_hi = _rd * (1 + _td) / (_rd * (1 + _td) + _rs * (1 - _ts)); _k_lo = _rd * (1 - _td) / (_rd * (1 - _td) + _rs * (1 + _ts))
            _ok = _k_hi * 1.65 < 1.08 and _k_lo * 2.4 > 1.30 and (10e-6 + 0.1e-6) * _rd * (1 + _td) < 0.50
        check(_ok, "%s: %s.%s reaches %s.%s at about 0.6 of its output through one series resistor, one pull-down on the node, "
                   "under 1.08 V at the gate's 1.65 V band edge and over 1.30 V at 2.4 V (series %s, pull-down %s, values %s, other "
                   "pads %s %s)" % (_node, _drv[0], _drv[1], _load[0], _load[1], _ser, _dn,
                                    [byval.get(r) for r in _ser + _dn], _oth_en, _oth_nd))
    # W4B-D1: the RockBLOCK's I_EN (J_RB9704 pin 3) is driven only by U536 = EMCON_HW AND RB_SW_IEN, with one pull-down to GND
    # that holds it with U536 unpowered (10 uA Ioff into 10 k, 0.1 V), and U6's request carries its own 4.7 k pull-down (S-08).
    _rb = sorted(bypad.get("RB_IEN", set())); _rbr = [p[0] for p in _rb if p[0].startswith("R")]
    check(("J_RB9704", "3") in _rb and ("U536", "4") in _rb and len(_rbr) == 1 and sorted(_pads.get(_rbr[0], {}).values()) == ["GND", "RB_IEN"]
          and len(_rb) == 3 and _pads.get("U536", {}) == {"1": "EMCON_HW", "2": "RB_SW_IEN", "3": "GND", "4": "RB_IEN", "5": "+3V3_DEV"}
          and sorted(p for p in bypad.get("RB_SW_IEN", set()) if not p[0].startswith("R")) == [("U536", "2"), ("U6", "19")]
          and len([r for r in bynet.get("RB_SW_IEN", set()) if r.startswith("R") and sorted(_pads.get(r, {}).values()) == ["GND", "RB_SW_IEN"]]) == 1,
          "RB_IEN: J_RB9704.3 is driven only by U536 = EMCON_HW AND RB_SW_IEN with one pull-down to GND, and U6.19 only asks "
          "(RB_IEN pads %s; U536 %s; RB_SW_IEN pads %s)" % (_rb, _pads.get("U536"), sorted(bypad.get("RB_SW_IEN", set()))))
    for _en, _drv, _load in (("E72_EN", ("U505", "4"), ("U22", "5")),):'''

EDITS = [("_EMCON_IN", EMCON_IN_OLD, EMCON_IN_NEW), ("card buck EN", CARD_EN_OLD, CARD_EN_NEW), ("enable nets", EN_OLD, EN_NEW)]


def main(a):
    if not a:
        print(__doc__); return 2
    p = a[0]; check = "--check" in a
    s = open(p, encoding="utf-8").read(); o = s; bad = []
    for name, old, new in EDITS:
        n = s.count(old); print("%-14s anchor found %d time(s)" % (name, n))
        if n != 1: bad.append(name); continue
        if not check: s = s.replace(old, new, 1)
    if bad:
        print("REFUSED: anchors not found exactly once: %s" % bad); return 1
    if check: return 0
    assert s != o; ast.parse(s)
    open(p, "w", encoding="utf-8").write(s); print("applied to %s" % p); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
