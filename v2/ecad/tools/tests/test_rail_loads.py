#!/usr/bin/env python3
"""Every declared rail names where its current goes (MESHSAT-862, 13 September 2026).

`dc_drop` does not leave a rail without loads unsolved: it splits the current evenly over every U and J
footprint on the net. That guess decided boards for five days. On 12 September it made CELL+ read 2.21 percent
by pushing 10 A through the charger's SENSE pin and its 0.20 mm escape; CELL+ was given its load and the tool
was left alone. When owner ruling 16 made the current density a verdict, FIVE of the ten failing rails turned
out to declare nothing, and the guesses were wrong in ways that mattered:

  * A24's `VBUS20`: 6 A into U3, whose only pads on the net are 0.13 and 0.20 mm sense pins. The real path is
    the whole charge current through R16, a 10 mOhm 2512 shunt.
  * E7's `CELL_F`: the guess MISSED the load carrying almost all of it, because `P_CP` starts with a P and the
    fallback only considers U and J references.
  * E7's `VIN_RAW`: half the rail into U4, which is the ideal diode FEEDING the bus, so current was being
    pulled backwards through a source.

The tool refuses such a rail now. This rule is the other half: it refuses the DECLARATION, in the generator,
where the fix belongs, so the next rail cannot be written without saying where its current goes.
"""
import os, re, sys, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAIL = re.compile(r'_intent\.rail\(\s*(.*?)\)\s*(?:#|$)', re.S)


def _calls(src):
    """Every `_intent.rail(...)` call's argument text, brackets balanced."""
    out = []
    for m in re.finditer(r'_intent\.rail\(', src):
        i = m.end(); depth = 1; j = i
        while j < len(src) and depth:
            if src[j] == "(": depth += 1
            elif src[j] == ")": depth -= 1
            j += 1
        out.append((src[:m.start()].count("\n") + 1, src[i:j - 1]))
    return out


def t_every_rail_declares_its_loads():
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py"))):
        src = open(f).read()
        for line, args in _calls(src):
            if "loads=" not in args:
                net = (re.search(r'"([^"]+)"', args) or [None, "?"])[1]
                bad.append("%s:%d rail %s declares no loads, so dc_drop would GUESS them"
                           % (os.path.basename(f), line, net))
    assert not bad, ("a rail without loads is a rail whose current dc_drop invents:\n  " + "\n  ".join(bad))


def t_a_rails_loads_sum_to_about_its_declared_current():
    """A split that does not add up is a different claim from the one in the rail's own amps_typ."""
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py"))):
        src = open(f).read()
        for line, args in _calls(src):
            m = re.search(r'loads\s*=\s*\{(.*?)\}', args, re.S)
            if not m: continue
            nums = [float(x) for x in re.findall(r':\s*([0-9.]+)', m.group(1))]
            amps = re.match(r'\s*"[^"]+"\s*,\s*[0-9.]+\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)', args)
            if not amps or not nums: continue
            typ = float(amps.group(1)); peak = float(amps.group(2)); tot = sum(nums)
            # A rail may be apportioned at its typical draw or at its PEAK, and declaring the peak is the
            # conservative choice (A24's +13V8_PA puts all 6 A of its peak into J_PA, where the record's
            # typical is 5). What is refused is a sum ABOVE the peak, which is a current the rail's own
            # record does not carry, and a token sum under half the typical, which measures nothing.
            if tot > peak * 1.02 or tot < typ * 0.5:
                net = (re.search(r'"([^"]+)"', args) or [None, "?"])[1]
                bad.append("%s:%d rail %s declares %.2f A typical and %.2f A peak, and its loads sum to %.2f A"
                           % (os.path.basename(f), line, net, typ, peak, tot))
    assert not bad, ("a rail's loads do not account for its current:\n  " + "\n  ".join(bad))


def t_intent_refuses_a_rail_that_declares_no_loads():
    """The floor in the declaration, not only in the rule above: the generator dies where the fix belongs."""
    import intent
    try:
        intent.rail("T_NOLOADS", 5.0, 1.0, 2.0, "J1")
    except SystemExit as e:
        assert "declares no loads" in str(e), "refused for the wrong reason: %s" % e
        return
    raise AssertionError("intent.rail accepted a rail with no loads, so dc_drop would invent its current")


def t_intent_refuses_loads_that_exceed_the_rails_own_peak():
    """The loads and the peak are two statements about one current; they may not contradict each other."""
    import intent
    try:
        intent.rail("T_OVER", 5.0, 1.0, 2.0, "J1", loads={"U1": 3.0})
    except SystemExit as e:
        assert "peak" in str(e)
        return
    raise AssertionError("intent.rail accepted loads summing above the rail's declared peak")


def t_intent_refuses_a_load_with_no_current():
    import intent
    for bad in ({"U1": 0}, {"U1": -0.5}, {"U1": "a lot"}):
        try:
            intent.rail("T_ZERO", 5.0, 1.0, 2.0, "J1", loads=bad); raise AssertionError("accepted %r" % bad)
        except SystemExit:
            pass


def t_a_rail_may_declare_several_sources():
    """A ground returns through every connector it leaves by. Holding one of B19's four JST-VH grounds at 0 V
    would put all 21 A through one pin and measure a board that does not exist."""
    import intent
    src = open(os.path.join(TOOLS, "dc_drop.py")).read()
    assert "srcrefs" in src and "isinstance(r[\"source\"], (list, tuple))" in src, \
        "dc_drop resolves one source reference only, so a ground cannot be declared honestly"
    assert 'f.GetReference() in srcrefs' in src, "dc_drop still compares the source with a single =="
    assert 'f.GetReference() not in srcrefs' in src, "the load guess still excludes one source reference only"


def t_no_rail_names_a_controller_as_its_source():
    """dc_drop holds the source's pads at 0 V and takes the rail's whole current out of them. A multi-pin IC's
    pad on its own output net is a SENSE pin: A24's VBUS20 put 2.90 A of 6 down a locked 0.200 mm escape that
    way and read 3.90 against IPC, on copper that was never carrying it."""
    bad = []
    for f in sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py"))):
        src = open(f).read()
        for line, args in _calls(src):
            if "source_ic=" in args: continue
            q = re.findall(r'"([^"]+)"', args)
            if len(q) < 2: continue
            net = q[0]
            # the source is the 5th positional argument: net, volts, typ, peak, source
            m = re.match(r'\s*"[^"]+"\s*,\s*[0-9.]+\s*,\s*[0-9.]+\s*,\s*[0-9.]+\s*,\s*("([^"]+)"|\[[^]]*\])', args)
            if not m: continue
            srcs = re.findall(r'"([^"]+)"', m.group(1))
            for s_ in srcs:
                if re.match(r"^U\d", s_):
                    bad.append("%s:%d rail %s names the controller %s as its source" % (os.path.basename(f), line, net, s_))
    assert not bad, ("a rail's current would be taken out of a sense pin:\n  " + "\n  ".join(bad))


def t_intent_refuses_a_controller_source_and_accepts_a_declared_one():
    import intent
    try:
        intent.rail("T_IC", 5.0, 1.0, 2.0, "U25", loads={"X1": 0.9}); raise AssertionError("a controller source was accepted")
    except SystemExit as e:
        assert "SENSE pin" in str(e)
    intent.rail("T_IC2", 5.0, 1.0, 2.0, "U40", loads={"X1": 0.9}, source_ic="an LDO: pin 5 is a real power pin")
    for good in ("L1", "R11", "J_DOCK", "F1"):
        intent.rail("T_OK_" + good, 5.0, 1.0, 2.0, good, loads={"X1": 0.9})


def t_a_rail_that_crosses_a_connector_declares_its_share_of_one_budget():
    """One conductor, one budget (MESHSAT-862, 16 September 2026).

    `+5V_D8` runs from board A's eFuse, out through the mezzanine connector, into board D's loads. Each board
    measured its own half against the WHOLE budget: A read 2.68 percent against the 2 percent default while D
    read its half against the 3 percent it declares with a reason, so the two halves could sum past the rail's
    real budget and both boards would pass. The share is what each board's copper may spend, dc_drop judges
    against it, and check_contracts adds them up."""
    import os, re
    tools = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    it = open(os.path.join(tools, "intent.py"), encoding="utf-8").read()
    assert "share=None" in it and '"share": share' in it, "the rail declaration cannot carry a share"
    dd = open(os.path.join(tools, "dc_drop.py"), encoding="utf-8").read()
    assert 'r.get("share")' in dd, "dc_drop still judges a shared rail against the whole budget"
    cc = open(os.path.join(tools, "check_contracts.py"), encoding="utf-8").read()
    assert "the shares sum to" in cc, "nothing adds the shares up"
    for f, want in (("gen_sch_a.py", "share=0.015"), ("gen_sch_d.py", "share=0.015")):
        s = open(os.path.join(tools, f), encoding="utf-8").read()
        i = s.index('_intent.rail("+5V_D8"')
        assert want in s[i:i + 400], "%s does not declare its share of the mezzanine rail" % f

def t_an_unsplit_shared_rail_is_an_open_question_and_not_a_failed_contract():
    """Six rails cross a connector with no share declared (MESHSAT-862, 16 September 2026).

    Declaring a share is an engineering judgement about where the drop is allowed to fall, not a fact the tree
    already holds: writing 50/50 for each of them would be a number with no basis, which this registry refuses
    everywhere else. So an unsplit rail makes the contract set INCONCLUSIVE, the way an absent netlist does,
    and it is named every run until someone splits it. Shares that ARE declared and sum past the budget remain
    a failure."""
    import os
    src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "check_contracts.py"),
               encoding="utf-8").read()
    assert "UNSPLIT" in src, "an unsplit rail is not tracked"
    i = src.index("UNSPLIT.append")
    assert "check(" not in src[i - 400:i], "an unsplit rail is still counted as a failed contract"
    assert "rails_unsplit" in src, "the verdict does not carry how many rails are unsplit"
    assert "the shares sum to" in src, "the sum rule is gone, so a declared split could exceed the budget"
