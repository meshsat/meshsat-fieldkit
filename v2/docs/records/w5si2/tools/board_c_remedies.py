#!/usr/bin/env python3
"""WHAT SI-001 WOULD READ ON BOARD C after each remedy this stream proposes for its layout-bound nets, in both states
of the makers' models (stream w5si2, 28 September 2026, MESHSAT-1357). A SIMULATION, in memory and in a temporary
directory outside every tree: NOTHING of any tree is changed, no circuit is changed, no declaration is filed. A series
resistor here is a line added to a COPY of the netlist; the real one is a draft for the owner of gen_sch_c.py.

The steps are cumulative, in the order a reader can undo them:
  0  the tree as it is
  1  the four EMCON copy nets declared LOW_SPEED_OR_DC (decision W5SI2-D1, apply_board_c_declarations.py)
  2  Q3_G declared LOW_SPEED_OR_DC ahead of the glob Q?_G (proposed, W5SI2-D2): the TX lamp's gate behind R37, 1 k,
     from TR_APRS, which the table already declares a static level
  3  EPD_SW in the net class SW (the first author's finding F-Q1, item 5: gen_pcb_c3.py PATTERNS), which takes the
     boost converter's switch node out of the signal nets, where its 32 siblings on the set already are
  4  SWCLK and SWDIO named in edge_allow: the debug port is driven only while a bench probe is attached
  5  a series resistor of 33 ohm at each of the RP2040's four e-paper SPI pins (a circuit draft)
What is left after step 5 cannot be closed at the desk and is listed with what each net needs.

Usage: board_c_remedies.py <tree with the models> <the same tree's view without the models> [--json]
"""
import os, re, sys, json, shutil, tempfile

EMCON = ["EMCLAMP_Y", "EMCLAMP_G", "EMCON_RD", "EMCON_RD_R"]
EPD = [("EPD_CS", "7"), ("EPD_DC", "6"), ("EPD_SCL", "4"), ("EPD_SDA", "5")]      # net, the RP2040's pin
SERIES = "33R"
ALLOW = [{"pattern": "SWCLK", "why": "the SWD clock, driven only by a bench probe on TP1 while a person debugs the panel controller: in "
                                     "no state of the kit's use is the net driven, and the probe's clock rate is the person's to lower"},
         {"pattern": "SWDIO", "why": "the SWD data line between TP2 and the RP2040, alive only while a bench probe is attached: in no "
                                     "state of the kit's use does it carry an edge"}]


def netlist_with(text, sw_class=False, series=False):
    """A copy of the netlist's text with EPD_SW in the class SW and, or, a series resistor at four pins."""
    if sw_class:
        a = '(name "/EPD_SW") (class "Default")'
        assert text.count(a) == 1
        text = text.replace(a, '(name "/EPD_SW") (class "SW")')
    if series:
        lines = text.split("\n")
        comps, added = [], []
        for i, (net, pin) in enumerate(EPD):
            ref = "R9%d" % (i + 1)
            assert '(comp (ref "%s")' % ref not in text, ref
            head = [k for k, l in enumerate(lines) if l.strip().startswith('(net (code "') and '(name "/%s") ' % net in l]
            assert len(head) == 1, net
            k = head[0]
            end = k + 1
            while end < len(lines) and lines[end].strip().startswith("(node "): end += 1
            nodes = [l.strip() for l in lines[k + 1:end]]
            assert nodes and nodes[-1].endswith(")))"), (net, nodes[-1][-20:])
            nodes[-1] = nodes[-1][:-1]                                   # the last node's line also closed the net
            mine = [n for n in nodes if n.startswith('(node (ref "U3") (pin "%s") ' % pin)]
            assert len(mine) == 1 and len(nodes) == 2, (net, nodes)      # one driver's pin and the connector's
            rest = [n for n in nodes if n not in mine] + ['(node (ref "%s") (pin "2") (pintype "passive"))' % ref]
            side = mine + ['(node (ref "%s") (pin "1") (pintype "passive"))' % ref]
            block = [lines[k]] + ["      " + n for n in rest[:-1]] + ["      " + rest[-1] + ")"]
            block += ['    (net (code "%d") (name "/%s_U") (class "Default")' % (9000 + i, net)]
            block += ["      " + n for n in side[:-1]] + ["      " + side[-1] + ")"]
            lines[k:end] = block
            comps.append('    (comp (ref "%s")\n      (value "%s"))' % (ref, SERIES))
            added.append(net + "_U")
        text = "\n".join(lines)
        a = "  (components\n"
        assert text.count(a) == 1
        text = text.replace(a, a + "\n".join(comps) + "\n")
    return text


def main(a):
    tree, view = os.path.abspath(a[0]), os.path.abspath(a[1])
    tools = os.path.join(tree, "v2", "ecad", "tools")
    sys.path.insert(0, tools)
    import edge_length as E, phase_artefacts as PA, boardtable, signal_class
    net0 = PA.netlist("c")
    stem = os.path.splitext(os.path.basename(net0))[0]
    table0 = json.load(open(os.path.join(tools, "boards", "c.json"), encoding="utf-8"))
    text0 = open(net0, encoding="utf-8").read()
    tmp = tempfile.mkdtemp(prefix="w5si2-boardc-")
    ov, od = boardtable.value, signal_class.declarations

    def table_with(emcon=False, q3=False, allow=False, series=False):
        t = json.loads(json.dumps(table0))
        sc = t["signal_classes"]
        if emcon:
            i = [k for k, e in enumerate(sc) if e["pattern"] == "EMCON_HW"][0]
            sc[i + 1:i + 1] = [{"pattern": n, "class": "LOW_SPEED_OR_DC", "basis": "a copy of the EMCON inhibit (W5SI2-D1)"} for n in EMCON]
        if q3:
            i = [k for k, e in enumerate(sc) if e["pattern"] == "Q?_G"][0]
            sc.insert(i, {"pattern": "Q3_G", "class": "LOW_SPEED_OR_DC", "basis": "the TX lamp's gate behind R37 from TR_APRS (W5SI2-D2, proposed)"})
        if series:      # the RP2040's side of each resistor is a net of the same bus, named ahead of the glob EPD_*
            i = [k for k, e in enumerate(sc) if e["pattern"] == "EPD_SCL"][0]
            sc[i:i] = [{"pattern": n + "_U", "class": "CLOCKED_DIGITAL", "basis": "the e-paper's SPI line at the RP2040's pin, ahead of its series resistor"}
                       for n, _p in EPD]
        if allow: t["edge_allow"] = [dict(e) for e in ALLOW]
        return t

    def read(label, tab, text, repo):
        d = os.path.join(tmp, re.sub(r"\W+", "-", label), os.path.basename(os.path.dirname(os.path.dirname(net0))))
        os.makedirs(os.path.join(d, "out"))
        p = os.path.join(d, "out", stem + ".net")
        open(p, "w", encoding="utf-8").write(text)
        shutil.copy2(os.path.join(os.path.dirname(net0), stem + "-intent.json"), os.path.join(d, "out", stem + "-intent.json"))
        shutil.copy2(os.path.join(os.path.dirname(os.path.dirname(net0)), stem + ".kicad_pro"), os.path.join(d, stem + ".kicad_pro"))
        boardtable.value = lambda l, key, default=None: tab.get(key, default) if l == "c" else ov(l, key, default)
        signal_class.declarations = lambda l: ([(e["pattern"], e["class"], e["basis"]) for e in tab.get("signal_classes", [])], []) \
            if l == "c" else od(l)
        try: r = E.schematic_table(p, "c", repo=repo)
        finally: boardtable.value, signal_class.declarations = ov, od
        return r

    steps = [("0 the tree as it is", {}, {}),
             ("1 + the four EMCON copy nets declared slow (W5SI2-D1)", {"emcon": True}, {}),
             ("2 + Q3_G declared slow (proposed W5SI2-D2)", {"emcon": True, "q3": True}, {}),
             ("3 + EPD_SW in the net class SW (F-Q1 item 5, the generator's)", {"emcon": True, "q3": True}, {"sw_class": True}),
             ("4 + SWCLK and SWDIO in edge_allow (proposed)", {"emcon": True, "q3": True, "allow": True}, {"sw_class": True}),
             ("5 + 33 ohm in series at the four e-paper SPI pins (a circuit draft)", {"emcon": True, "q3": True, "allow": True, "series": True},
              {"sw_class": True, "series": True})]
    out = []
    print("BOARD C, SI-001 AT THE SCHEMATIC PHASE AFTER EACH PROPOSED REMEDY: a simulation in memory, nothing filed, no circuit changed.")
    print("netlist %s, sha256/16 %s; tools/pcb_edge_rates.yaml sha256/16 %s" % (os.path.relpath(net0, tree), E._sha16(net0), E.RATES.get("sha16")))
    print()
    print("step | models | result | signal | slow | by a published figure | by a bound | undecided (no declaration + model absent + other) | answered | layout-bound (figure-held + BOUND_DECIDES)")
    last = {}
    for label, tk, nk in steps:
        tab, text = table_with(**tk), netlist_with(text0, **nk)
        for state, repo in (("PRESENT", tree), ("ABSENT", view)):
            r = read(label + " " + state, tab, text, repo)
            c = r["counts"]
            assert r["inputs"]["model_state"]["state"] in (state, "NOT_ASKED"), r["inputs"]["model_state"]
            assert not r["fails"], r["fails"]
            print("%s | %s | %s | %d | %d | %d | %d | %d (%d + %d + %d) | %d | %d (%d + %d)" % (
                label, state, E.schematic_result(r), c["signal_nets"], c["low_speed_nets"], c["maker_edge_nets"], c["bound_edge_nets"],
                c["undecided_nets"], c["undecided_no_declaration_nets"], c["undecided_model_absent_nets"], c["undecided_other_nets"],
                c["answered_nets"], c["layout_bound_nets"], c["maker_held_nets"], c["bound_decided_nets"]))
            last[state] = r
            out.append({"step": label, "models": state, "result": E.schematic_result(r), "counts": c})
    for state in ("PRESENT", "ABSENT"):
        r = last[state]
        lb = sorted(n for row in r["rows"] for n in row.get("layout_bound") or [])
        un = sorted((n, row["undecided_kind"][n]) for row in r["rows"] for n in row.get("undecided") or {})
        print()
        print("AFTER STEP 5, models %s: %d layout-bound net(s) hold the reading: %s" % (state, len(lb), ", ".join(lb)))
        if un: print("  and %d undecided: %s" % (len(un), ", ".join("%s (%s)" % x for x in un)))
        ans = sorted((n, a) for row in r["rows"] for n, a in (row.get("answered") or {}).items())
        print("  answered (%d): %s" % (len(ans), "; ".join("%s: %s" % (n, a[:70]) for n, a in ans)))
    shutil.rmtree(tmp)
    if "--json" in a: print(json.dumps(out, indent=1))


if __name__ == "__main__":
    if len(sys.argv) < 3: print(__doc__); sys.exit(2)
    main(sys.argv[1:])
