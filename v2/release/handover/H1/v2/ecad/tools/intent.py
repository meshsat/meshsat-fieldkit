#!/usr/bin/env python3
"""Design intent as data (MESHSAT-862 Stage C, 8 Sep 2026, appendix 32.64 W2). The schematic generators used to emit reference, symbol, value,
footprint and a pin-to-net map and nothing else, so no gate could ask "is this capacitor near the pin it bypasses", "does this rail's copper
carry its current" or "is this pair at its impedance". Each gen_sch_*.py now collects:
  bypass(cap_ref, part_ref, pin)            the pin a decoupling capacitor serves (through c(..., bypass=(part, pin)))
  rail(net, volts, amps_typ, amps_peak, source_ref, loads={ref: amps})   the currents a rail carries, from the record (appendix 32.55 for A22)
  pair_class(class_name, z_diff=None, z_se=None)   the impedance target of a net class (the class itself is assigned in the project file)
and writes out/<name>-intent.json beside the netlist. The gates read it with load(); a missing file is a FAIL there (fail closed), an empty
list is reported with its zero denominator ("bypass 0 of 0 checked"), never hidden."""
import json, os, sys, time
import re as _re

Z_DEFAULT = {"USB": {"z_diff": 90.0, "z_se": 50.0}, "DIFF100": {"z_diff": 100.0, "z_se": 50.0}, "PCIE": {"z_diff": 100.0}, "HDMI": {"z_diff": 100.0}, "RF": {"z_se": 50.0}}

_I = {"bypass": [], "rails": {}, "nodes": {}, "pair_classes": dict(Z_DEFAULT), "pass_through": {}}

def pass_through(ref, basis):
    """A part current passes THROUGH that no shape test can recognise (20 September 2026, appendix 32.253).

    `power_path` walks a rail out through the parts on its source and its loads, and it knows two shapes:
    a two-terminal part (a shunt, an inductor, a fuse, a ferrite) and a power transistor, whose drain and
    source are multi-pad lands so it has more PADS than NETS. Board E's input filter is a Bourns SRF1260
    DUAL-WINDING choke on a four-pin land, winding 1 on the line and winding 2 on the return: four pads, four
    nets, two pass-throughs in one package, and the shape test sees a four-pin connector. Four conductors
    carrying 8 A were invisible because of it.

    The obvious widening, counting only the nets that are not declared at zero, was swept across six boards
    and refused: it took board C from one flagged net to eleven and every new one was false, because an ESD
    array has the transistor's shape once its ground pin is dropped. So the answer here is the one this
    project uses everywhere else: a DECLARATION rather than a heuristic. The generator knows what it drew.

    `basis` says why, in words, because a part declared a conductor without a reason is the thing this rule
    exists to stop.
    """
    if not str(basis).strip():
        raise SystemExit("intent: pass_through %s declares no basis" % ref)
    _I["pass_through"][str(ref)] = str(basis)


def bypass(cap_ref, part_ref, pin, net=None):
    _I["bypass"].append({"cap": cap_ref, "part": part_ref, "pin": str(pin), "net": net})

# WHAT amps_typ AND amps_peak MEAN TO THE RULES THAT READ THEM (20 September 2026, appendix 32.245).
# They are not two decorations of one number: the two halves of the power rule set read DIFFERENT ones.
#   amps_typ   the rail's continuous load. `dc_drop` solves the mesh at this and judges both the voltage
#              drop (PI-002) and the conductor's current density (PI-001) from it, because IPC's 10 K rise
#              is a STEADY-STATE thermal limit and a transient does not set it.
#   amps_peak  the worst the rail ever carries. `via_current` and `rail_crossings` judge every BARREL at
#              this (PI-003), because a barrel has almost no thermal mass and a far higher current density
#              than the conductor feeding it, so its worst case is the one that decides it.
# So a via on VBAT is judged at 18 A while the track feeding it is judged at 10, on the same board and from
# this same declaration, and the two rules' numbers are not comparable. Declaring a peak that is really a
# FAULT current therefore makes PI-003 pessimistic without making PI-001 stricter, and declaring a service
# current as a peak does the reverse: whichever one it is belongs in the rail's `note`.
def rail(net, volts, amps_typ, amps_peak, source, loads=None, note="", budget=None, source_ic="", share=None,
         efficiency=None, switch=None, always_on=None, always_on_why="", enable_net=None, v_work=None,
         converted=None, series_of=None, returns=None, fed_from=None, v_max=None):
    """source: the reference the rail enters the board at, or a LIST of them (a ground returns to several).

    budget: this rail's own drop budget as a fraction (default the judge's 2 percent; a 3.3 V logic rail at 1 A over long 0.4 mm tracks is fine at 3, 8 Sep 2026).

    efficiency: the converter's efficiency at this rail's current, as a fraction, WITH ITS BASIS IN THE NOTE
    (rule THM-001, 16 September 2026). `thermal.py` turns it into the watts this board has to get rid of; a
    rail that declares none is listed as unknown rather than estimated at a figure nobody wrote down.

    share: THIS BOARD'S PART of a rail that crosses to another board (16 September 2026). `+5V_D8` is one
    conductor from board A's eFuse, out through the mezzanine connector, into board D's loads, and each board
    was measuring its own half against the WHOLE budget: A read 2.68 percent against the 2 percent default and
    D read its half against the 3 percent it declares, so the two halves could sum past the rail's real budget
    and both boards would pass. A rail that leaves the board declares what fraction of the end-to-end budget
    this board's copper may spend, `check_contracts` adds the shares up, and `dc_drop` judges this board
    against its share rather than against the whole."""
    # 13 September 2026 (MESHSAT-862): a rail without loads is not declarable. `dc_drop` used to split the
    # current evenly over every U and J on the net when nothing was declared, and that guess decided boards
    # for five days (A24's CELL+ at 2.21 percent through a SENSE pin; VBUS20's 6 A through two more). The
    # tool refuses such a rail at measurement time now; this refuses it where the fix belongs, in the
    # generator, so the next rail cannot be written without saying where its current goes.
    # THE SOURCE IS THE POWER PATH, NOT THE PART THAT CONTROLS IT (13 September 2026). `dc_drop` holds the
    # source part's pads at 0 V and takes the rail's whole current out of them, so naming a switching
    # controller sends that current through its output SENSE pin: A24's VBUS20 put 2.90 A of 6 down a locked
    # 0.200 mm escape and read 3.90 against IPC, on copper that was never carrying it. The current of a buck
    # or a buck-boost leaves through the INDUCTOR and the sense SHUNT beside it, not through the chip. Four
    # rails named a controller (A's VBUS20, +12V_HF and +54V_POE, B's +3V3_DEV). A part whose output pin is a
    # real power pin, an LDO for instance, says so with `source_ic="<why>"`.
    _sr = source if isinstance(source, (list, tuple)) else [source]
    for _s in _sr:
        if _re.match(r"^U\d", str(_s)) and not source_ic:
            raise SystemExit("intent: rail %s names %s as its source, and a multi-pin IC's pad on its own output net is a "
                             "SENSE pin: dc_drop would take the rail's %.2f A out of it. Name the inductor or the sense "
                             "shunt the current really leaves through, or pass source_ic=\"<why this part's pin is a "
                             "power pin>\"." % (net, _s, amps_typ))
    # A SEGMENT OF A PATH IS NOT A SECOND POWER SOURCE (20 September 2026, rule THM-001). One conductor run
    # is often several nets: VBUS20 leaves R11, crosses R16's shunt and continues as CH_ACN to Q7; each LM5176
    # stage's output leaves the boost-side FET as <p>_OUT and becomes its rail past the ISNS shunt; the USB-C
    # outlet is PD_OUT, PD_VPWR, PD_SW and PD_VBUS in series. Every one of those segments needs a rail
    # declaration, because a NODE is judged by no power rule and that is how sixteen DC conductors on this
    # board came to be measured by nothing. But `thermal.py` sums every declared rail's volts times amps, so
    # declaring the segments without saying what they are counts one path's watts two, three or four times:
    # `series_of` says the power is already counted at the named rail, and thermal excludes the segment while
    # dc_drop, derate, via_current and rail_crossings go on judging its copper exactly as they judge any rail.
    # It must name a RAIL, never a node, because a node carries no watts and excluding a segment against one
    # would take the path's power out of the total altogether; and a segment may not declare MORE current than
    # the path it belongs to, which is the arithmetic that makes the exclusion safe.
    if series_of is not None:
        _p = _I["rails"].get(str(series_of).lstrip("/")) or _I["rails"].get("/" + str(series_of).lstrip("/"))
        if _p is None:
            raise SystemExit("intent: rail %s says it is a series segment of %s, and %s is not a declared rail. "
                             "A segment's power is counted at the rail it belongs to, so that rail has to exist "
                             "and be counted; if this conductor is the one place the path's power is counted, "
                             "declare it as a plain rail and point the other segments at IT."
                             % (net, series_of, series_of))
        if float(amps_peak) > float(_p.get("amps_peak") or 0) + 1e-9:
            raise SystemExit("intent: rail %s declares %.2f A peak as a series segment of %s, which declares "
                             "%.2f A. A segment of a path cannot carry more than the path."
                             % (net, float(amps_peak), series_of, float(_p.get("amps_peak") or 0)))
    # A RETURN'S DROP IS JUDGED AGAINST THE RAIL IT RETURNS, NOT AGAINST ITS OWN POTENTIAL (20 September 2026,
    # rule PI-002; board P's `PACK_N`, the third of the sixteen and the biggest current in the kit).
    #
    # `PACK_N` runs from the 12 AWG lead land to the 2 mOhm coulomb-counting shunt at the pack's whole 10.0 A
    # typical and 18.0 A peak, and it was a node, so no power rule had looked at it. Declaring it as an
    # ordinary rail produces a NONSENSE NUMBER, which is worse than no number: `dc_drop` judges the drop as a
    # PERCENTAGE OF THE NET'S OWN VOLTAGE, and a return's own voltage is 50 mV by construction, so a 2 percent
    # budget is a bar of one millivolt and every return on every board fails it. Declaring `volts` as the
    # pack's 14.4 to get a sensible bar is not available either, because `derate` takes the WORST of everything
    # declared about a net and would judge the 100 R sense resistor sitting on this net against 14.4 V instead
    # of the 50 mV it really sees.
    #
    # So the net keeps its own `volts` (50 mV, which is what a part on it sees and what CMP-001 must use) and
    # `returns` names the rail whose voltage and budget the DROP is judged against. It also carries the
    # thermal exclusion `series_of` carries, for the same reason and more obviously: a return is the other
    # half of one loop and its watts are that loop's watts.
    if returns is not None:
        if series_of is not None:
            raise SystemExit("intent: rail %s declares both series_of and returns; a conductor is a segment of "
                             "a path or the return of one, and the two are judged differently" % net)
        _rp = _I["rails"].get(str(returns).lstrip("/")) or _I["rails"].get("/" + str(returns).lstrip("/"))
        if _rp is None:
            raise SystemExit("intent: rail %s says it returns %s, and %s is not a declared rail. A return's "
                             "drop is judged against the rail it returns, so that rail has to be declared "
                             "first." % (net, returns, returns))
        if float(amps_peak) > float(_rp.get("amps_peak") or 0) + 1e-9:
            raise SystemExit("intent: rail %s returns %.2f A peak where %s carries %.2f A. A return carries "
                             "the current of the rail it returns and no more."
                             % (net, float(amps_peak), returns, float(_rp.get("amps_peak") or 0)))
    # WHAT A RAIL TAKES OUT OF THE RAIL BEHIND IT (20 September 2026, appendix 32.246). Board A's `VBAT` is
    # declared 10.0 A typical, and the nine converters that draw from it add up to 15.18 A from this same
    # file, using each one's own declared voltage, current and efficiency: the pack node's declaration
    # understates its own loads by 52 percent, and nothing checked it, on any board. `dc_drop` then solves
    # VBAT at the declared 10.0 and already reads 3.69 times its density limit, so the board's largest
    # conductor question is understated by its own intent.
    # `fed_from` names the rail a converter's input sits on, which the generator knows at the moment it
    # writes the stage (`lm5176`'s own `vin` argument, `buck5`'s VBAT), so the arithmetic needs no guessing
    # about which pins of a controller are its inputs. `power_path` adds them up and reports a rail that
    # declares less than its children draw.
    if fed_from is not None:
        # the self-reference first, because a rail that names ITSELF is also not yet in the table and the
        # existence check would answer it with the wrong sentence.
        if str(fed_from).lstrip("/") == net.lstrip("/"):
            raise SystemExit("intent: rail %s says it is fed from itself" % net)
        _ff = _I["rails"].get(str(fed_from).lstrip("/")) or _I["rails"].get("/" + str(fed_from).lstrip("/"))
        if _ff is None:
            raise SystemExit("intent: rail %s says it is fed from %s, and %s is not a declared rail. The rail "
                             "behind a converter is a rail: declare it first." % (net, fed_from, fed_from))
    if not loads: raise SystemExit("intent: rail %s declares no loads. Name where its current goes: "
                                   "loads={\"<ref>\": <amps>, ...}, summing to at most the rail's %.2f A peak. "
                                   "Undeclared, dc_drop would split %.2f A evenly over every U and J on the net, "
                                   "which is a guess and not a measurement." % (net, amps_peak, amps_typ))
    _bad = [k for k, v in loads.items() if not isinstance(v, (int, float)) or v <= 0]
    if _bad: raise SystemExit("intent: rail %s gives a load no current: %s" % (net, sorted(_bad)))
    _tot = sum(loads.values())
    if _tot > amps_peak * 1.02: raise SystemExit("intent: rail %s declares a %.2f A peak and its loads sum to %.2f A. "
                                                 "The loads are a claim about the same current as the peak: correct one of them." % (net, amps_peak, _tot))
    _I["rails"][net] = {"volts": volts, "amps_typ": amps_typ, "amps_peak": amps_peak, "source": source, "loads": loads or {}, "note": note,
                        **({"budget": budget} if budget else {}), **({"share": share} if share else {}),
                        # WHAT SWITCHES THIS RAIL (rule PWR-002, 16 September 2026). `switch` is the part whose
                        # enable pin turns it on; `always_on` says there is no such part and WHY, because a rail
                        # nobody switches is a design statement and not an absence. power_sequence.py checks the
                        # declaration against the netlist and finds the deadlock a schematic cannot show: a rail
                        # whose enable is driven only by a device powered from that same rail.
                        **({"switch": switch} if switch else {}),
                        # the enable NET, where its name is not EN-shaped: the BQ4050 turns the pack terminal on
                        # through DSG_G, which no pattern over names would find and which is the truth
                        **({"enable_net": enable_net} if enable_net else {}),
                        **({"always_on": True, "always_on_why": always_on_why} if always_on else {}),
                        **({"efficiency": efficiency} if efficiency else {}),
                        # v_work: the highest voltage this rail reaches in NORMAL SERVICE where that differs
                        # from `volts`. `volts` is the NOMINAL, which is the right number for a drop budget
                        # and the wrong one for a part's rating: VBAT is declared 14.4 V and a 4S pack
                        # terminates at 16.8, and VIN_RAW is declared 12 V and the vehicle input it comes
                        # from is specified 9 to 36. A transient suppressor is judged on this number, because
                        # a clamp that stands off less than the line's own working maximum conducts in service.
                        **({"v_work": float(v_work)} if v_work is not None else {}),
                        # converted: is there a CONVERSION on this rail, or is it switched through a pass
                        # element? `switch` names what turns a rail on, and that is a FET as often as it is a
                        # controller: board E's VIN_RAW is switched by a hot-swap FET and board P's PACK_P by
                        # the protector's own, and neither converts anything. A converter's loss is
                        # P_out * (1/eff - 1) and a pass element's is I2R in one part, which is the
                        # `dissipators` list's business, so the two cannot share one question (16 September
                        # 2026, rule THM-001).
                        **({"converted": bool(converted)} if converted is not None else {}),
                        **({"series_of": str(series_of).lstrip("/")} if series_of is not None else {}),
                        **({"returns": str(returns).lstrip("/")} if returns is not None else {}),
                        **({"fed_from": str(fed_from).lstrip("/")} if fed_from is not None else {}),
                        # v_max: THE PEAK A PART ON THIS RAIL CAN SEE, which is not `v_work` and not `volts`
                        # (20 September 2026). `node()` has carried this since 16 September and `rail()` had
                        # not, and the gap bit within minutes of using it: board E's vehicle input is 9 to
                        # 36 V in service and its SMCJ40A clamps a transient at about 64.5 V at peak pulse
                        # current, so a part on it must be rated for the clamp's let-through while the
                        # PROTECTOR itself is judged against the service maximum. Declaring 53.3 as `v_work`
                        # to keep the derating strict made `derate` refuse the SMCJ40A for standing off 40 V
                        # on a line it was told runs to 53.3 in normal service, which is a true sentence
                        # about a false input. `derate` takes the worst of `volts`, `v_max` and `v_work` for
                        # a part's rating and reads `v_work` alone for the standoff rule, so the two numbers
                        # belong in the two fields and the conversion of a node to a rail keeps both.
                        **({"v_max": float(v_max)} if v_max is not None else {})}

def node(net, v_max, basis, v_min=0.0, rides_on=None, bias_v=None, vendor_reference=None, v_work=None):
    """A NET THAT IS NOT A RAIL, and the largest voltage a part on it can see (rule CMP-001, 16 September 2026).

    `rail()` describes a supply: a voltage, a current, a source and its loads. A switching node, a bootstrap
    capacitor's top plate, a charge pump's output and a power amplifier's drain are none of those things, and
    they are exactly where a part meets a voltage higher than any rail on the board. Nothing declared them, so
    `derate.py` reported them as UNDECLARED and judged nothing: board A had twenty-nine such nets, board C had
    ten and judged NO part at all, and board D's power amplifier output, which swings to about 55 V peak into
    50 ohm at 30 W, was one of them.

    v_max is the peak a part on this net can see in normal operation, and `basis` is where that number comes
    from, in words, because a voltage nobody can trace is the thing this rule exists to stop. v_min is the
    lowest (a negative charge pump, a node that swings below ground).
    """
    if not str(basis).strip(): raise SystemExit("intent: node %s declares no basis for %.1f V" % (net, v_max))
    # A PART SEES THE VOLTAGE ACROSS IT, NOT THE POTENTIAL OF ONE END. A bootstrap capacitor sits between
    # BOOT and SW and both ends move together: the node reaches 43 V above ground and the capacitor never sees
    # more than the driver's own 7.5 V bias, which is why every one of them on this board is a 25 V part and
    # why judging it against the node's peak would refuse a correct design. A net that RIDES ON another says
    # so and declares the bias between them; a part whose two nets are that pair is judged against the bias.
    if (rides_on is None) != (bias_v is None):
        raise SystemExit("intent: node %s declares rides_on without bias_v or the other way round" % net)
    # A NET WHOSE VOLTAGE THIS PROJECT CANNOT STATE, ON WHICH THE PART MAKER STATES THE PART. The e-paper's
    # charge pumps are the case: their peaks live inside a panel driver whose datasheet is not published, and
    # the panel maker's own driving-circuit note specifies the capacitor instead ("Capacitors 25V 0603", PDI
    # rev 02). Inventing a voltage to compare against would be the invention this rule exists to stop, and
    # reporting the net as unknown loses a real, citable comparison. `vendor_reference` records that the part
    # on this net is the one the part's own maker specifies for that pin, with the citation; derate counts it
    # as judged by that authority and names it, and it is the only way a part passes without a number.
    if v_max is None and not vendor_reference:
        raise SystemExit("intent: node %s declares no voltage and no vendor reference" % net)
    # v_work: the highest voltage this net reaches in NORMAL SERVICE, where v_max is the peak including the
    # transient a clamp lets through. The two differ wherever a suppressor is involved, and the difference is
    # the only honest way to ask whether that suppressor stands the line off instead of conducting in service.
    _I["nodes"][net] = {"v_max": None if v_max is None else float(v_max), "v_min": float(v_min), "basis": basis,
                        **({"v_work": float(v_work)} if v_work is not None else {}),
                        **({"rides_on": rides_on, "bias_v": float(bias_v)} if rides_on else {}),
                        **({"vendor_reference": vendor_reference} if vendor_reference else {})}

def rail_volts(net, default=None):
    """The declared voltage of a rail, for a generator that needs to derive a node's peak from it.

    A stage's switching node reaches its input rail and its bootstrap reaches that plus the driver supply, so
    the numbers belong to the stage's own helper rather than to twenty hand-written lines that can drift from
    the topology they describe."""
    r = _I["rails"].get(net.lstrip("/")) or _I["rails"].get("/" + net.lstrip("/"))
    if r is None:
        if default is not None: return float(default)
        raise SystemExit("intent: rail_volts(%s): no such declared rail" % net)
    return float(r.get("volts") or 0)

def rail_amps(net):
    """The declared (typical, peak) current of a rail, for a generator deriving a series segment's own.

    A conductor run is several nets and every segment carries the SAME current: writing that current out by
    hand at each segment is how a table of numbers gets one wrong, so a segment reads it from the rail it
    belongs to and the two cannot drift."""
    r = _I["rails"].get(net.lstrip("/")) or _I["rails"].get("/" + net.lstrip("/"))
    if r is None: raise SystemExit("intent: rail_amps(%s): no such declared rail" % net)
    return float(r.get("amps_typ") or 0), float(r.get("amps_peak") or 0)

def net_volts(net, default=None):
    """The declared voltage of a net, rail or node, for a stage that derives its own switching nodes.

    A stage's output is not always a rail: the USB-C PD supply is regulated to 5, 9 or 15 V on request and is
    declared as a node with the profile it can reach. Looking only at rails would make a helper raise on it,
    and giving the helper a silent default is how a number nobody wrote down gets into a verdict."""
    n = net.lstrip("/")
    if n in _I["rails"] or "/" + n in _I["rails"]: return rail_volts(n)
    d = _I["nodes"].get(n)
    if d is not None: return max(abs(float(d.get("v_max") or 0)), abs(float(d.get("v_min") or 0)))
    if default is not None: return float(default)
    raise SystemExit("intent: net_volts(%s): neither a declared rail nor a declared node" % net)

def pair_class(name, z_diff=None, z_se=None):
    _I["pair_classes"][name] = {k: v for k, v in (("z_diff", z_diff), ("z_se", z_se)) if v is not None}

def write(sch_path, project, parts=None):
    """Writes out/<project>-intent.json next to the schematic; the bypass entries are checked against the part list when given."""
    out = os.path.join(os.path.dirname(os.path.abspath(sch_path)), "out", project + "-intent.json"); os.makedirs(os.path.dirname(out), exist_ok=True)
    if parts is not None:
        refs = {p["ref"] for p in parts}; nets = {p["ref"]: p["nets"] for p in parts}
        for b in _I["bypass"]:
            if b["cap"] not in refs or b["part"] not in refs: raise SystemExit("intent: bypass %s -> %s.%s names a reference that is not in the schematic" % (b["cap"], b["part"], b["pin"]))
            if b["pin"] not in nets[b["part"]]: raise SystemExit("intent: bypass %s -> %s.%s: the part has no pin %s" % (b["cap"], b["part"], b["pin"], b["pin"]))
            if b["net"] is None: b["net"] = nets[b["part"]][b["pin"]]
            if b["net"] not in nets[b["cap"]].values(): raise SystemExit("intent: bypass %s -> %s.%s: the capacitor is not on that pin's net %s" % (b["cap"], b["part"], b["pin"], b["net"]))
        for net in _I["nodes"]:
            # A declared node that is not a net of this schematic is a typo that would read as coverage.
            if not {p["ref"] for p in parts if net in p["nets"].values()}:
                raise SystemExit("intent: node %s is not a net of the schematic" % net)
        for net, r in _I["rails"].items():
            on_net = {p["ref"] for p in parts if net in p["nets"].values()}
            if not on_net: raise SystemExit("intent: rail %s is not a net of the schematic" % net)
            for _sr in (r["source"] if isinstance(r["source"], (list, tuple)) else [r["source"]]):
                if _sr not in on_net: raise SystemExit("intent: rail %s names source %s, which is not on that net (refs on it: %s)" % (net, _sr, sorted(on_net)[:8]))
            for ref in r["loads"]:
                if ref not in on_net: raise SystemExit("intent: rail %s names load %s, which is not on that net" % (net, ref))
    d = dict(board=project, written=time.strftime("%Y-%m-%d %H:%M"), **_I)
    json.dump(d, open(out, "w"), indent=1)
    print("intent: %s (%d bypass, %d rails, %d nodes, %d pair classes)"
          % (out, len(_I["bypass"]), len(_I["rails"]), len(_I["nodes"]), len(_I["pair_classes"])))
    return out

def load(board_path):
    """The intent file for a board file (<dir>/out/<stem>-intent.json), or None."""
    stem = os.path.splitext(os.path.basename(board_path))[0]; p = os.path.join(os.path.dirname(os.path.abspath(board_path)), "out", stem + "-intent.json")
    if not os.path.exists(p): return None
    return json.load(open(p))
