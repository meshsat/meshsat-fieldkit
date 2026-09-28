#!/usr/bin/env python3
"""The contract pcb_interfaces.yaml after decision 55 (MESHSAT-1357, integration set 9, stream s99reg, 29 September 2026).
AI engineering text; prototype design, nothing built, ordered or measured.

It WRAPS v2/docs/records/s99a/apply_if_ab_power_dev.py (whose --check passes): that script's two replacements are
imported and applied verbatim (IF-AB-POWER's +5V_DEV currents row restated after the split, and IF-AB-WALL's "limit
0.89 A" made "limit 0.9142 A nominal, TPS2596 equation 7"). Run THIS script, not that one; if that one has already been
run, this one finds its two new texts in place and applies the rest.

The rest are the generator cites of the three interfaces this touches, which were stale (the carried set 8 finding:
IF-AB-POWER's `ends` named gen_sch_a.py:967-968, 1038 and gen_sch_b.py:434, 831, 875; the S-99 lines moved board A's
again). Every line number written here is READ from the tree it runs on by parsing the generators (`ast`), never typed:
the call that defines the named connector, eFuse or rail, and it must be exactly one call.

  IF-AB-POWER   ends (A: J_5V_S1..3, J_5V_DEV, J_54V; B: the same); the currents rows' cites of board A's slot rails, of
                Q28's VBAT load and of +54V_POE; board B's cites are asserted current and kept.
  IF-AD-HARNESS ends (A: J_MEZZ1 and J_MEZZ_PWR1 with U23; D: J_HARN1 and J_PWR1); power_lead's `from`, which names
                U23's input now: +5V_D8IN from the buck U41 (asserted on U23's call: in +5V_D8IN, out +5V_D8, enable
                D8_EN, ILM 453R "2.0 A").
  IF-AB-WALL    ends (A: J_AB2; B: J_AB2) and the usb text's cite of the D-12 port block (J_USBW, U32, VBUS_WALL;
                asserted: U32 from +5V_DEV to VBUS_WALL, ILM text "0.91 A", VBUS_WALL's peak 0.9142 A).

Every old text must occur exactly once; the result parses; only those three interfaces change, and in them only the
fields named. Refuses a second run (every new text already present). Usage: python3 <this file> [--root <tree>] [--check]."""
import importlib.util, os, sys

import yaml

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _int10 as H

NAME = "apply_if_ab_power_s99"
F = "v2/ecad/tools/pcb_interfaces.yaml"
GA, GB, GD = "v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_b.py", "v2/ecad/tools/gen_sch_d.py"
FIELDS = {"IF-AB-POWER": {"ends", "currents"}, "IF-AD-HARNESS": {"ends", "power_lead"}, "IF-AB-WALL": {"ends", "usb"}}


def s99a_changes():
    p = os.path.join(H.CODE, "v2/docs/records/s99a/apply_if_ab_power_dev.py")
    spec = importlib.util.spec_from_file_location("s99a_if_ab_power_dev", p)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return [(n, o, w) for n, o, w in m.CHANGES]


def derived(root):
    """{what: text} of the cites, read from the generators, and the facts they stand for, asserted"""
    sa, sb, sd = H.read(root, GA), H.read(root, GB), H.read(root, GD)
    P, V, E, R = ("part",), ("vh2",), ("efuse",), ("rail",)
    a_s = H.one_call(NAME, sa, V, "J_5V_S%s", GA); a_dev = H.one_call(NAME, sa, V, "J_5V_DEV", GA); a_54 = H.one_call(NAME, sa, V, "J_54V", GA)
    b_s = H.one_call(NAME, sb, P, "J_5V_S%d", GB); b_dev = H.one_call(NAME, sb, P, "J_5V_DEV", GB); b_54 = H.one_call(NAME, sb, P, "J_54V", GB)
    a_mezz = H.one_call(NAME, sa, P, "J_MEZZ1", GA); a_mpwr = H.one_call(NAME, sa, V, "J_MEZZ_PWR1", GA)
    u23 = H.one_call(NAME, sa, E, "U23", GA)
    d_harn = H.one_call(NAME, sd, P, "J_HARN1", GD); d_pwr = H.one_call(NAME, sd, P, "J_PWR1", GD)
    a_ab2 = H.one_call(NAME, sa, P, "J_AB2", GA); b_ab2 = H.one_call(NAME, sb, P, "J_AB2", GB)
    usbw = H.one_call(NAME, sa, P, "J_USBW", GA); u32 = H.one_call(NAME, sa, E, "U32", GA)
    vbw = H.one_call(NAME, sa, R, "VBUS_WALL", GA)
    rs_a = H.one_call(NAME, sa, R, "+5V_S%s", GA); rpoe_a = H.one_call(NAME, sa, R, "+54V_POE", GA); vbat = H.one_call(NAME, sa, R, "VBAT", GA)
    rs_b = H.one_call(NAME, sb, R, "+5V_S%d", GB); rdev_b = H.one_call(NAME, sb, R, "+5V_DEV", GB); rpoe_b = H.one_call(NAME, sb, R, "+54V_POE", GB)

    # the facts the texts stand for
    ua = [getattr(x, "value", None) for x in u23[2].args]
    if ua[:4] != ["U23", "+5V_D8IN", "+5V_D8", "D8_EN"] or "2.0 A" not in str(ua[6]):
        H.refuse(NAME, "U23's call is not the eFuse from +5V_D8IN to +5V_D8 on D8_EN at 2.0 A: %s" % ua[:7])
    if u23[0] != a_mpwr[0]: H.refuse(NAME, "U23 and J_MEZZ_PWR1 are no longer on one line (%d, %d): re-read the cite" % (u23[0], a_mpwr[0]))
    xa = [getattr(x, "value", None) for x in u32[2].args]
    if xa[:3] != ["U32", "+5V_DEV", "VBUS_WALL"] or "0.91 A" not in str(xa[6]): H.refuse(NAME, "U32's call is not the eFuse from +5V_DEV to VBUS_WALL at 0.91 A: %s" % xa[:7])
    if getattr(vbw[2].args[3], "value", None) != 0.9142: H.refuse(NAME, "VBUS_WALL's declared peak is not 0.9142 A")
    loads = H.kw(vbat[2], "loads")
    q28 = H.dict_key_line(loads, "Q28") if loads is not None else None
    if q28 is None: H.refuse(NAME, "Q28 is not a key of VBAT's loads")
    q28v = [v.value for k, v in zip(loads.keys, loads.values) if getattr(k, "value", None) == "Q28"][0]
    if q28v != 2.22: H.refuse(NAME, "Q28's VBAT load is %s, the row says 2.22 A" % q28v)
    for c, want in ((rs_b, 85), (rdev_b, 111), (rpoe_b, 271)):
        if c[0] != want: H.refuse(NAME, "board B's rail call moved to line %d (the row cites %d): re-read the row" % (c[0], want))
    return {
        "a_ends_power": H.span_text([(a_s[0], a_s[0]), (a_dev[0], a_dev[0]), (a_54[0], a_54[0])]),
        "b_ends_power": H.span_text([(b_s[0], b_s[0]), (b_dev[0], b_dev[0]), (b_54[0], b_54[0])]),
        "a_ends_harn": H.span_text([(a_mezz[0], a_mezz[1]), (u23[0], u23[0])]),
        "d_ends_harn": H.span_text([(d_harn[0], d_harn[1]), (d_pwr[0], d_pwr[1])]),
        "u23": "%d" % u23[0],
        "a_ends_wall": H.span_text([(a_ab2[0], a_ab2[1])]),
        "b_ends_wall": H.span_text([(b_ab2[0], b_ab2[1])]),
        "wall_block": H.span_text([(usbw[0], vbw[1])]),
        "slot_a": "%d" % rs_a[0], "q28": "%d" % q28, "poe_a": "%d" % rpoe_a[0],
    }


def changes(L):
    return [
        ("IF-AB-POWER ends A", '{board: a, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: "v2/ecad/tools/gen_sch_a.py:967-968, 1038"}',
         '{board: a, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: "v2/ecad/tools/gen_sch_a.py:%s"}' % L["a_ends_power"]),
        ("IF-AB-POWER ends B", '{board: b, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: "v2/ecad/tools/gen_sch_b.py:434, 831, 875"}',
         '{board: b, refs: [J_5V_S1, J_5V_S2, J_5V_S3, J_5V_DEV, J_54V], src: "v2/ecad/tools/gen_sch_b.py:%s"}' % L["b_ends_power"]),
        ("IF-AB-POWER slots 1 and 3", '(gen_sch_a.py:113, slots 1 and 3;', '(gen_sch_a.py:%s, slots 1 and 3;' % L["slot_a"]),
        ("IF-AB-POWER +5V_S2", '(gen_sch_a.py:113; the VBAT load Q28 2.22 A,\n             gen_sch_a.py:48)',
         '(gen_sch_a.py:%s; the VBAT load Q28 2.22 A,\n             gen_sch_a.py:%s)' % (L["slot_a"], L["q28"])),
        ("IF-AB-POWER +54V_POE", '(gen_sch_a.py:147, gen_sch_b.py:271)', '(gen_sch_a.py:%s, gen_sch_b.py:271)' % L["poe_a"]),
        ("IF-AD-HARNESS ends A", '{board: a, refs: [J_MEZZ1, J_MEZZ_PWR1], src: "v2/ecad/tools/gen_sch_a.py:1290-1291, 1171"}',
         '{board: a, refs: [J_MEZZ1, J_MEZZ_PWR1], src: "v2/ecad/tools/gen_sch_a.py:%s"}' % L["a_ends_harn"]),
        ("IF-AD-HARNESS ends D", '{board: d, refs: [J_HARN1, J_PWR1], src: "v2/ecad/tools/gen_sch_d.py:220-222"}',
         '{board: d, refs: [J_HARN1, J_PWR1], src: "v2/ecad/tools/gen_sch_d.py:%s"}' % L["d_ends_harn"]),
        ("IF-AD-HARNESS power_lead", 'from: "A U23 eFuse, ILM 2.0 A, enable D8_EN (gen_sch_a.py:1171)"',
         'from: "A U23 eFuse, ILM 2.0 A, enable D8_EN, its input +5V_D8IN from board A\'s buck U41 on VBAT since decision 55 '
         '(gen_sch_a.py:%s)"' % L["u23"]),
        ("IF-AB-WALL ends A", '{board: a, ref: J_AB2, part: "IDC 2x5 vertical box header", src: "v2/ecad/tools/gen_sch_a.py:1288-1289"}',
         '{board: a, ref: J_AB2, part: "IDC 2x5 vertical box header", src: "v2/ecad/tools/gen_sch_a.py:%s"}' % L["a_ends_wall"]),
        ("IF-AB-WALL ends B", '{board: b, ref: J_AB2, part: "IDC 2x5", src: "v2/ecad/tools/gen_sch_b.py:1083-1085"}',
         '{board: b, ref: J_AB2, part: "IDC 2x5", src: "v2/ecad/tools/gen_sch_b.py:%s"}' % L["b_ends_wall"]),
        ("IF-AB-WALL usb block", "458b2873: gen_sch_a.py:1293-1309)", "458b2873; now gen_sch_a.py:%s)" % L["wall_block"]),
    ]


def main(argv):
    root = H.root_of(argv)
    orig = H.read(root, F)
    L = derived(root)
    ours = changes(L)
    theirs = s99a_changes()
    state = [(orig.count(o), orig.count(n)) for _nm, o, n in theirs]
    if all(s == (1, 0) for s in state): todo = theirs + ours; s99a_done = False
    elif all(s == (0, 1) for s in state): todo = list(ours); s99a_done = True
    else: H.refuse(NAME, "s99a's two replacements are neither both pending nor both applied: %s" % state)
    if all(orig.count(n) == 1 and orig.count(o) == 0 for _nm, o, n in ours): H.refuse(NAME, "already applied (a second run)")
    res = orig
    for nm, old, new in todo:
        if new == old: H.refuse(NAME, "%s: the new text does not differ" % nm)
        if res.count(old) != 1: H.refuse(NAME, "%s: the old text occurs %d times, once expected" % (nm, res.count(old)))
        res = res.replace(old, new, 1)
    if res == orig: H.refuse(NAME, "nothing changed")
    before, after = yaml.safe_load(orig), yaml.safe_load(res)
    if set(before) != set(after): H.refuse(NAME, "top-level keys changed")
    # the contracts live under a nested key: find the dict holding IF-AB-POWER
    def holder(o):
        if isinstance(o, dict):
            if "IF-AB-POWER" in o: return o
            for v in o.values():
                h = holder(v)
                if h is not None: return h
        return None
    hb, ha = holder(before), holder(after)
    if hb is None or ha is None or list(hb) != list(ha): H.refuse(NAME, "the contracts' list changed")
    for name in hb:
        d = {f for f in set(hb[name]) | set(ha[name]) if hb[name].get(f) != ha[name].get(f)} if isinstance(hb[name], dict) else set()
        want = FIELDS.get(name, set())
        if not d <= want: H.refuse(NAME, "%s: fields changed %s, allowed %s" % (name, sorted(d), sorted(want)))
        if name in FIELDS and not d: H.refuse(NAME, "%s did not change" % name)
    # everything outside the contracts' holder is unchanged: compare with the holder blanked
    def blank(o, h):
        if o is h: return "<contracts>"
        if isinstance(o, dict): return {k: blank(v, h) for k, v in o.items()}
        if isinstance(o, list): return [blank(v, h) for v in o]
        return o
    if blank(before, hb) != blank(after, ha): H.refuse(NAME, "text outside the contracts changed")
    row = [r for r in ha["IF-AB-POWER"]["currents"] if r.get("rail") == "+5V_DEV"][0]
    if set(row) != {"rail", "a_declares", "b_declares", "status"} or "6.9142" not in row["a_declares"]: H.refuse(NAME, "the +5V_DEV row is not s99a's")
    if "0.89 A" in H.one_space(str(ha["IF-AB-WALL"]["usb"])): H.refuse(NAME, "IF-AB-WALL still says 0.89 A")
    msg = ("%d replacement(s)%s; cites read from the generators: IF-AB-POWER A %s, B %s, slot rails %s, Q28 %s, +54V_POE %s; "
           "IF-AD-HARNESS A %s, D %s, U23 %s; IF-AB-WALL A %s, B %s, the D-12 block %s"
           % (len(todo), " (s99a's two already applied)" if s99a_done else " (s99a's two included)", L["a_ends_power"], L["b_ends_power"],
              L["slot_a"], L["q28"], L["poe_a"], L["a_ends_harn"], L["d_ends_harn"], L["u23"], L["a_ends_wall"], L["b_ends_wall"], L["wall_block"]))
    if "--check" in argv:
        print("%s: CHECK ONLY, nothing written: %s" % (NAME, msg)); return 0
    H.write(root, F, res)
    if yaml.safe_load(H.read(root, F)) != after: H.refuse(NAME, "the file written does not re-parse to what was checked")
    print("%s: %s -> %s; %s\nOWED: the readings that record pcb_interfaces.yaml by sha (interfaces.py, rules_status CONFIG_INPUTS) are re-taken"
          % (NAME, H.sha16_text(orig), H.sha16_text(res), msg))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
