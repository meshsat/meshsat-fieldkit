#!/usr/bin/env python3
"""The hardware control lines across boards C, B, A, D and E, drawn from the committed netlists (MESHSAT-1357, layer 4).

Writes:
  v2/docs/diagrams/src/control-lines.mmd   the Mermaid source of the diagram (rendered by tools/render.sh)
  v2/docs/diagrams/control-lines.md        every node of every line on every board, the pulls, the connector pins
                                           against v2/ecad/tools/pcb_interfaces.yaml, and each netlist's sha256/16

The lines: TX_INHIBIT_n, EMCON_HW, EMCON_ON1..3 (EMCON; board B makes one EMCON_ON per slot since its round 8, each on
that module's own 3.3 V), ZEROIZE_SW, ZEROIZE_HW (ZEROIZE), SLOT_EN1..3, PI_KILL, SHORE_INHIBIT.
Every part, pin and net is read from the netlist; nothing about the circuit is typed here except the direction of the
drawing (a netlist carries no signal direction: every pin of these parts is "passive" in it), which follows one rule
stated below, and the chain of boards the lines cross (the four board-to-board contracts named in LINKS).

Direction rule: on board C (the source of every line) an edge runs from a switch, a gate output or, where the net has
no other driver, the panel controller's pin, toward the ribbon. On every other board an edge runs from the connector
the line arrives on toward each part it reaches; a FET whose drain sits on the line (an inverter or a level stage)
drives it. A microcontroller pin on a line that has another driver is drawn dotted: the netlist cannot say whether
firmware makes it an input or an output, which is exactly EMCON's shared-line item L1 (v2/docs/feasibility/EMCON.md).

What the tool refuses (exit status 1, the problems listed on the page): a connector pin that differs between a cable's two
ends or from pcb_interfaces.yaml; a logic part (value text starting SN74, 74LVC, 74AUP, 74AHC or 74HC) on a line with no
pin map in netlist.GATES, because it would be drawn as a plain IC and the line would stop there unnoticed; and a FET on a
line whose symbol does not name exactly one G, S and D pin, or that is not N-channel by its library symbol and its value
text, because the drawing's wording ("high pulls low", "level stage") holds for an N-channel FET only.

Stdlib and PyYAML only; runner-safe. Usage: python3 v2/docs/diagrams/tools/control_lines.py [--check]
(--check writes nothing and exits 1 if the committed outputs differ from what the netlists give now)."""
import os, re, sys
sys.dont_write_bytecode = True   # nothing written into the tree beside the sources read
import yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as N

OUT_MMD = os.path.join(N.REPO, "v2/docs/diagrams/src/control-lines.mmd")
OUT_MD = os.path.join(N.REPO, "v2/docs/diagrams/control-lines.md")
INTERFACES = "v2/ecad/tools/pcb_interfaces.yaml"

LINES = [("TX_INHIBIT_n", "emcon"), ("EMCON_HW", "emcon"), ("EMCON_ON1", "emcon"), ("EMCON_ON2", "emcon"),
         ("EMCON_ON3", "emcon"), ("ZEROIZE_SW", "zeroize"),
         ("ZEROIZE_HW", "zeroize"), ("SLOT_EN1", "slot"), ("SLOT_EN2", "slot"), ("SLOT_EN3", "slot"), ("PI_KILL", "kill"),
         ("SHORE_INHIBIT", "shore")]
FAMILY_COLOUR = {"emcon": "#c62828", "zeroize": "#6a1b9a", "slot": "#1565c0", "kill": "#e65100", "shore": "#2e7d32",
                 "mixed": "#212121"}
BOARD_ORDER = ["C", "B", "A", "D", "E"]
# the board each line arrives on through which connector, and the four contracts it crosses (pcb_interfaces.yaml)
ENTRY = {"B": "J_PANEL", "A": "J_AB1", "D": "J_HARN1", "E": "J_BLK"}
LINKS = [("IF-BC-PANEL", ("C", "J_PANEL"), ("B", "J_PANEL"), "26-way ribbon"),
         ("IF-AB-RIBBON", ("B", "J_AB1"), ("A", "J_AB1"), "26-way ribbon"),
         ("IF-AD-HARNESS", ("A", "J_MEZZ1"), ("D", "J_HARN1"), "16-way harness"),
         ("IF-AE-DOCK", ("A", "J_DOCK"), ("E", "J_BLK"), "spring pins onto E5, wires to E")]
MCU = ("RP2040", "STM32")
LINE_NETS = {n for n, _ in LINES}


def rail_hint(value):
    m = re.search(r"(\+\d+V\d*(?:_[A-Z0-9]+)*)", value)
    return m.group(1) if m else ""


MAKERS = ("Amphenol", "NiceRF", "Quectel", "Microchip", "TI", "Diodes", "Molex", "TE", "Hirose")


def what(nl, ref):
    """A short identity for a part: its MPN and, where the value names one, the rail it makes."""
    v = nl.value(ref); mpn = nl.mpn(ref); r = rail_hint(v)
    if mpn in MAKERS:
        mpn = re.split(r"[ :,(]", v.split(" ", 1)[1], 1)[0] if " " in v else mpn
        slot = re.search(r"slot (S\d)", v)
        if "receptacle" in v and slot:
            return "%s CM5 %s receptacle" % (ref, slot.group(1))
    return "%s %s%s" % (ref, mpn, (" (" + r + ")") if r and mpn not in ("R", "C") else "")


def kind(nl, ref, pin, fn):
    if ref.startswith("TP"): return "tp"
    if ref.startswith("J"): return "conn"
    if ref.startswith("SW"): return "switch"
    if ref[0] in "RC" and len(nl.pins.get(ref, {})) == 2: return "passive"
    if ref.startswith("Q"):
        k = {"G": "fet_gate", "D": "fet_drain", "S": "fet_source"}.get(fn, "fet")
        gate = N.short(nl.pins.get(ref, {}).get(nl.fet_pin(ref, "G") or "") or "")
        return "fet_level" if k in ("fet_drain", "fet_source") and gate.startswith("+") else k
    g = N.gate_output(nl, ref, pin)
    if g: return "gate_in"
    for key, (gates, _) in N.GATES.items():
        if nl.value(ref).startswith(key) and int(pin) in [o for _, o in gates]: return "gate_out"
    if nl.value(ref).startswith(MCU) or " RP2040" in nl.value(ref): return "mcu"
    return "ic"


def downstream(nl, net, depth=3, seen=None):
    """What a net reaches, following logic gates and FET gates, stopping at anything else: a list of short strings."""
    seen = set() if seen is None else seen
    if net in seen or depth == 0: return []
    seen.add(net); out = []
    for d in nl.nets.get(net, []):
        k = kind(nl, d["ref"], d["pin"], d["fn"])
        if k == "passive" and d["ref"].startswith("R"):
            far = series_far(nl, d)
            if far and far not in seen:          # a series resistor (an enable divider's top leg): followed, no depth used
                sub = downstream(nl, far, depth, seen)
                if sub:
                    out.append("%s (series) to %s: %s" % (d["ref"], N.short(far), ", ".join(sub)))
            continue
        if k in ("tp", "passive", "gate_out", "fet_drain", "fet_level"): continue
        if k == "gate_in":
            g, o, _ = N.gate_output(nl, d["ref"], d["pin"])
            sub = downstream(nl, o, depth - 1, seen)
            out.append("%s to %s%s" % (d["ref"], N.short(o), (" to " + ", ".join(sub)) if sub else ""))
        elif k == "fet_gate":
            dn = nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "D"))
            sub = downstream(nl, dn, depth - 1, seen)
            out.append("%s pulls %s%s" % (d["ref"], N.short(dn), (" to " + ", ".join(sub)) if sub else ""))
        elif k == "conn":
            out.append("%s.%s" % (d["ref"], d["pin"]))
        else:
            out.append("%s %s" % (what(nl, d["ref"]), d["fn"] or ""))
    return out


def series_far(nl, d):
    """The far net of a two-pin resistor on a line when it is a series element, not a pull: the far net is no rail (a name
    starting with '+'), no ground and no line of LINES, and carries a pin of something other than passives, test
    points and LEDs (an indicator's resistor is not followed), and it is no power conductor (below). None otherwise."""
    if len(nl.pins.get(d["ref"], {})) != 2:
        return None
    far = [n for p, n in nl.pins[d["ref"]].items() if p != d["pin"]][0]
    sf = N.short(far)
    if sf.startswith("+") or sf.startswith("GND") or sf in LINE_NETS or far.startswith("unconnected"):
        return None
    nodes = nl.nets.get(far, [])
    active = [x for x in nodes if kind(nl, x["ref"], x["pin"], x["fn"]) not in ("passive", "tp")]
    if not active or all(x["ref"].startswith("LED") for x in active):     # an indicator's series resistor: not followed
        return None
    # a power conductor is not a signal: a far net of more than eight nodes or with a power-package FET on it (the resistor
    # is then a shunt or a divider's top leg on a rail, such as board E's R19 to R22 on DC_P) is not followed
    if len(nodes) > 8 or any(x["ref"].startswith("Q") and len(nl.pins.get(x["ref"], {})) >= 5 for x in nodes):
        return None
    return far


def pulls(nl, net):
    res = []
    for d in nl.nets.get(net, []):
        if kind(nl, d["ref"], d["pin"], d["fn"]) == "passive":
            other = [N.short(n) for p, n in nl.pins[d["ref"]].items() if p != d["pin"]]
            res.append("%s %s to %s" % (d["ref"], nl.value(d["ref"]), other[0] if other else "?"))
    return res


def drives_a_line(nl, d, k):
    """True when this node of a line is itself the driver of another line of LINES (a gate whose output, or a FET whose
    drain, is a line): such a part is drawn as its own node, never grouped, so the two lines' edges meet at it."""
    if k == "gate_in":
        g = N.gate_output(nl, d["ref"], d["pin"])
        return bool(g) and N.short(g[1]) in LINE_NETS
    if k == "fet_gate":
        return N.short(nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "D")) or "") in LINE_NETS
    return False


def unmapped_logic(nl, ref):
    v = nl.value(ref)
    return v.startswith(N.LOGIC_PREFIXES) and not any(v.startswith(k) for k in N.GATES)


def refusals(nl, b, net, name, seen, depth=3):
    """Why the drawing of this net (and of what it reaches through gates and FET gates, to the depth the diagram follows)
    cannot be trusted: an unmapped logic part, or a FET the wording does not fit. Empty when there is nothing to refuse."""
    out = []
    if name in seen or depth == 0:
        return out
    seen.add(name)
    for d in nl.nets.get(name, []):
        r = d["ref"]
        if kind(nl, r, d["pin"], d["fn"]) == "passive":
            far = series_far(nl, d) if r.startswith("R") else None
            if far:
                out.extend(refusals(nl, b, net, far, seen, depth))
            continue
        if unmapped_logic(nl, r):
            out.append("board %s, line %s: %s (%s) is a logic part with no pin map in netlist.GATES; add its map from the "
                       "maker's sheet" % (b, net, r, nl.mpn(r)))
        elif r.startswith("Q"):
            gsd = [nl.fet_pin(r, f) for f in "GSD"]
            if None in gsd:
                out.append("board %s, line %s: FET %s's symbol does not name exactly one G, S and D pin" % (b, net, r))
            elif not nl.n_channel(r) or re.search(r"P-FET|P-channel|P-Channel", nl.value(r)):
                out.append("board %s, line %s: FET %s is not N-channel by its symbol and value text; the drawing's wording "
                           "holds for N-channel FETs only" % (b, net, r))
            elif nl.fn.get((r, d["pin"])) == "G":
                out.extend(refusals(nl, b, net, nl.pins[r][gsd[2]], seen, depth - 1))
        else:
            g = N.gate_output(nl, r, d["pin"]) if d["pin"].isdigit() else None
            if g and g[1]:
                out.extend(refusals(nl, b, net, g[1], seen, depth - 1))
    return out


def build():
    nls = N.load_all(tuple(BOARD_ORDER))
    iface = yaml.safe_load(open(os.path.join(N.REPO, INTERFACES), encoding="utf-8"))["board_to_board"]["contracts"]
    nodes = {}       # node id -> dict(board, label lines, cls)
    edges = []       # (src, dst, label, family, dotted)
    table = []       # rows for the md
    pull_rows = {b: [] for b in BOARD_ORDER}
    problems = []
    seen_edges = set()

    def node(b, ref, text, cls):
        nid = "%s_%s" % (b, re.sub(r"[^A-Za-z0-9]", "_", ref))
        n = nodes.setdefault(nid, dict(board=b, head=text, lines=[], cls=cls))
        return nid, n

    for net, fam in LINES:
        for b in BOARD_ORDER:
            nl = nls[b]; name, nds = nl.net(net)
            if not nds: continue
            kinds = [(d, kind(nl, d["ref"], d["pin"], d["fn"])) for d in nds]
            for d, k in kinds:
                table.append((net, b, d["ref"], d["pin"], d["fn"] or "", k, nl.value(d["ref"])[:110]))
            problems.extend(refusals(nl, b, net, name, set()))
            p = pulls(nl, name)
            if p: pull_rows[b].append((net, p))
            # the drivers of this net on this board
            if b == "C":
                drv = [d for d, k in kinds if k in ("switch", "gate_out")] or [d for d, k in kinds if k == "mcu"]
            else:
                drv = [d for d, k in kinds if (k == "conn" and d["ref"] == ENTRY.get(b)) or k in ("fet_drain", "gate_out")]
            drv_ids = []
            for d in drv:
                k = kind(nl, d["ref"], d["pin"], d["fn"])
                if k == "conn":
                    nid, _ = node(b, d["ref"], "%s %s" % (b, d["ref"]), "conn")
                elif k == "fet_drain":
                    g = N.short(nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "G"))); s_ = N.short(nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "S")))
                    nid, n = node(b, d["ref"], what(nl, d["ref"]), "part")
                    if g not in LINE_NETS:
                        n["lines"].append("inverter: gate %s, source %s, drain drives %s" % (g, s_, net))
                elif k == "gate_out":
                    key = [k2 for k2 in N.GATES if nl.value(d["ref"]).startswith(k2)][0]
                    ins = [N.short(nl.pins[d["ref"]].get(str(i))) for gi, o in N.GATES[key][0] if str(o) == d["pin"] for i in gi]
                    nid, n = node(b, d["ref"], what(nl, d["ref"]), "part")
                    if not all(i in LINE_NETS for i in ins):
                        n["lines"].append("drives %s from %s" % (net, " and ".join(ins)))
                elif k == "switch":
                    other = sorted(set(N.short(x) for p_, x in nl.pins[d["ref"]].items() if p_ != d["pin"] and not x.startswith("unconnected")))
                    nid, n = node(b, d["ref"], "%s %s" % (d["ref"], nl.value(d["ref"]).split("(")[0].strip()[:40]), "switch")
                    n["lines"].append("closed: %s to %s" % (net, "/".join(other)))
                else:
                    nid, n = node(b, d["ref"], what(nl, d["ref"]), "mcu")
                    n["lines"].append("%s drives %s" % (d["fn"], net))
                drv_ids.append((nid, d))
            # everything else on the net; parts of one kind on one pin with the same MPN share a node
            groups, pinsets = {}, {}
            for d, k in kinds:
                if k in ("tp", "passive") or d in drv: continue
                pinsets.setdefault(d["ref"], set()).add(d["pin"])
            for d, k in kinds:
                if k in ("tp", "passive") or d in drv: continue
                gk = (k, nl.mpn(d["ref"]), tuple(sorted(pinsets[d["ref"]]))) if k != "conn" else (k, d["ref"])
                if drives_a_line(nl, d, k):      # it also drives a line drawn in its own right: one node, so its edges meet
                    gk = (k, d["ref"])
                groups.setdefault(gk, []).append((d, k))
            for gk, members in groups.items():
                refs = list(dict.fromkeys(d["ref"] for d, _ in members))
                k = members[0][1]
                if k == "conn":
                    nid, n = node(b, refs[0], "%s %s" % (b, refs[0]), "conn"); dotted = False
                else:
                    cls = "mcu" if k == "mcu" else "part"
                    head = what(nl, refs[0]) if len(refs) == 1 else "%s %s" % (", ".join(refs), nl.mpn(refs[0]))
                    nid, n = node(b, "_".join(refs), head, cls)
                    dotted = k in ("mcu", "fet_level")
                    for d, _ in members:
                        tag = "" if len(refs) == 1 else d["ref"] + ": "
                        if k == "gate_in":
                            g, o, _ = N.gate_output(nl, d["ref"], d["pin"])
                            sub = [] if N.short(o) in LINE_NETS else downstream(nl, o, 2, {name})
                            n["lines"].append("%s%s gates %s%s" % (tag, net, N.short(o), (", to " + "; ".join(sub)) if sub else ""))
                        elif k == "fet_gate":
                            dn = nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "D"))
                            sub = [] if N.short(dn) in LINE_NETS else downstream(nl, dn, 2, {name})
                            n["lines"].append("%s%s high pulls %s low%s" % (tag, net, N.short(dn), (", to " + "; ".join(sub)) if sub else ""))
                        elif k in ("fet_level", "fet_source", "fet", "fet_drain"):
                            g = N.short(nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "G"))); s_ = N.short(nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "S")))
                            far = [x for x in downstream(nl, nl.pins[d["ref"]].get(nl.fet_pin(d["ref"], "S")), 1, {name})]
                            n["lines"].append("%slevel stage on %s: gate %s, source %s%s" % (tag, net, g, s_, (" to " + ", ".join(far)) if far else ""))
                        elif k == "mcu":
                            n["lines"].append("%s%s on %s" % (tag, d["fn"], net))
                        else:
                            pinname = d["fn"] if d["fn"] and d["fn"] != name.lstrip("/") and d["fn"] != net else "pin " + d["pin"]
                            n["lines"].append("%s%s at %s" % (tag, net, pinname))
                for sid, sd in drv_ids:
                    if sid != nid and (sid, nid, net) not in seen_edges:
                        seen_edges.add((sid, nid, net)); edges.append((sid, nid, net, fam, dotted))

    # the links between boards, and each end's pin read against the other end and against pcb_interfaces.yaml
    link_rows = []
    for cid, (ba, ra), (bb, rb), how in LINKS:
        pins_iface = (iface.get(cid) or {}).get("pins") or {}
        carried = []
        for net, fam in LINES:
            pa = [d["pin"] for d in nls[ba].net(net)[1] if d["ref"] == ra]
            pb = [d["pin"] for d in nls[bb].net(net)[1] if d["ref"] == rb]
            if not pa and not pb: continue
            ok = pa == pb
            ifp = [str(k) for k, v in pins_iface.items() if v == net]
            iok = (sorted(ifp) == sorted(pa)) if pins_iface else None
            link_rows.append((cid, net, "%s %s.%s" % (ba, ra, ",".join(pa) or "-"), "%s %s.%s" % (bb, rb, ",".join(pb) or "-"),
                              "yes" if ok else "NO", ("yes" if iok else "NO") if iok is not None else "no pin map"))
            if not ok: problems.append("%s: %s on %s %s pin %s but %s %s pin %s" % (cid, net, ba, ra, pa, bb, rb, pb))
            if iok is False: problems.append("%s: %s on pin %s in the netlist, %s in %s" % (cid, net, pa, ifp, INTERFACES))
            carried.append("%s %s" % (",".join(pa), net))
        if carried:
            ida, _ = node(ba, ra, "%s %s" % (ba, ra), "conn"); idb, _ = node(bb, rb, "%s %s" % (bb, rb), "conn")
            edges.append((ida, idb, "%s, %s: pins %s" % (cid, how, "; ".join(carried)), "link", False))
    return nls, nodes, edges, table, pull_rows, link_rows, problems


def esc(s):
    """Mermaid label text: no double quotes, no angle brackets (the drawing uses words, not arrows, inside a label)."""
    return s.replace('"', "'").replace("<", "(").replace(">", ")")


def mermaid(nls, nodes, edges, pull_rows, head):
    L = ["---", "title: \"Control lines across the boards, read from the netlists named in each board's box (design diagram of an unbuilt prototype)\"",
         "---", "flowchart LR"]
    for b in BOARD_ORDER:
        nl = nls[b]
        L.append("  subgraph %s[\"%s, netlist %s at %s\"]" % ("brd" + b, N.BOARD_TITLES[b], nl.sha, nl.commit))
        L.append("    direction TB")
        for nid, n in nodes.items():
            if n["board"] != b: continue
            body = [n["head"]] + sorted(set(n["lines"]), key=n["lines"].index)
            L.append("    %s[\"%s\"]:::%s" % (nid, "<br/>".join(esc(x) for x in body), n["cls"]))
        if pull_rows[b]:
            txt = ["pulls and filters on %s (what the line reads with its source gone)" % b] + ["%s: %s" % (net, ", ".join(p)) for net, p in pull_rows[b]]
            L.append("    %s_pulls[\"%s\"]:::pulls" % (b, "<br/>".join(esc(x) for x in txt)))
        L.append("  end")
    L.append("  E5[\"E5 dock block: no schematic, its board file names the nets (pin 8 SHORE_INHIBIT passes through)\"]:::conn")
    merged = {}                        # one edge per (source, target, style): a ribbon's pass-through carries many lines
    for s, d, lab, fam, dotted in edges:
        m = merged.setdefault((s, d, dotted), [[], []])
        m[0].append(lab); m[1].append(fam)
    edges = [(s, d, ", ".join(labs), fams[0] if len(set(fams)) == 1 else "mixed", dotted)
             for (s, d, dotted), (labs, fams) in merged.items()]
    link_styles = []
    for i, (s, d, lab, fam, dotted) in enumerate(edges):
        if fam == "link" and s == "A_J_DOCK":
            L.append("  %s ---|\"%s\"| E5" % (s, esc(lab))); L.append("  E5 --> %s" % d)
            link_styles += [("link", False), ("link", False)]
            continue
        arrow = "-.->" if dotted else ("===" if fam == "link" else "-->")
        L.append("  %s %s|\"%s\"| %s" % (s, arrow, esc(lab), d))
        link_styles.append((fam, dotted))
    for i, (fam, dotted) in enumerate(link_styles):
        col = FAMILY_COLOUR.get(fam, "#455a64")
        L.append("  linkStyle %d stroke:%s,stroke-width:%s%s" % (i, col, "3px" if fam == "link" else "2px",
                                                                ",stroke-dasharray:4 3" if dotted else ""))
    L += ["  classDef conn fill:#eceff1,stroke:#455a64,color:#000",
          "  classDef part fill:#ffffff,stroke:#37474f,color:#000",
          "  classDef switch fill:#fff3e0,stroke:#e65100,color:#000",
          "  classDef mcu fill:#e3f2fd,stroke:#1565c0,color:#000",
          "  classDef pulls fill:#f5f5f5,stroke:#9e9e9e,color:#333,stroke-dasharray:3 3"]
    L.append("  NOTE[\"Colours: red EMCON (TX_INHIBIT_n, EMCON_HW, EMCON_ON1..3); purple ZEROIZE; blue SLOT_EN1..3; orange PI_KILL; "
             "green SHORE_INHIBIT; black several families on one edge (a ribbon passing lines through); grey the board-to-board links. Dotted: a microcontroller pin or a level stage on a line "
             "that has another driver (direction set by firmware, EMCON item L1). NOT SHOWN: test points (see control-lines.md), "
             "PI_SHDN_REQ, HDMI selects, heartbeats, the kit I2C bus, timing, and the SLOT_EN hold across a panel reset, "
             "which is in no generator (ARCHITECTURE.md 4.3). Nothing here is built or measured.\"]:::pulls")
    return "\n".join(L) + "\n"


def markdown(nls, table, pull_rows, link_rows, problems, head, dirty):
    L = ["# Control lines across the boards: the netlist reading behind the diagram", "",
         "Generated by `v2/docs/diagrams/tools/control_lines.py` from the committed netlists; do not edit by hand. "
         "Design diagram of an unbuilt prototype: no V2 board has been fabricated, ordered or powered, and nothing below is "
         "measured. The diagram is `svg/control-lines.svg` (source `src/control-lines.mmd`).", "",
         N.tree_line(head, dirty), "",
         "| Board | Netlist | sha256/16 | Last changed |", "|---|---|---|---|"]
    for b in BOARD_ORDER:
        nl = nls[b]; L.append("| %s | `%s` | `%s` | `%s` |" % (b, nl.path, nl.sha, nl.commit))
    L += ["", "Pin maps used to follow a line through a logic gate (from the maker's sheet held in the tree):", ""]
    for k, (_, src) in N.GATES.items():
        L.append("- `%s`: `%s`" % (k, src))
    L += ["", "## The board-to-board links", "",
          "Each line's pin at both ends, read from the two netlists, and the same pin in `v2/ecad/tools/pcb_interfaces.yaml`.", "",
          "| Contract | Line | End 1 | End 2 | Ends agree | Contract agrees |", "|---|---|---|---|---|---|"]
    for r in link_rows:
        L.append("| %s |" % " | ".join(r))
    L += ["", "Problems found: %s" % ("none" if not problems else ""), ""] + ["- %s" % p for p in problems]
    L += ["", "## Pulls and filters: what each line reads with its source gone", "",
          "Every two-pin resistor or capacitor on the line; a resistor to a rail or ground is a pull, a capacitor is a filter "
          "(listed because it sets the line's edge, not because it holds a level).", "", "| Board | Line | Pull or filter |", "|---|---|---|"]
    for b in BOARD_ORDER:
        for net, p in pull_rows[b]:
            L.append("| %s | %s | %s |" % (b, net, "; ".join(p)))
    L += ["", "## Every node", "", "Kind is the tool's reading of the part and pin (the netlist marks these pins passive): conn, tp (test "
          "point), passive, switch, gate_in, gate_out, fet_gate, fet_drain, fet_source, mcu or ic.", "",
          "| Line | Board | Ref | Pin | Pin name | Kind | Value (first 110 characters) |", "|---|---|---|---|---|---|---|"]
    for r in table:
        L.append("| %s |" % " | ".join(x.replace("|", "/") for x in r))
    L += ["", "## What this reading does not show", "",
          "- Direction and timing: a netlist has no signal direction; the diagram's direction follows the rule in the tool's header.",
          "- Firmware: which way the panel controller, the three supervisors and board E's sensor controller set their pins on these lines.",
          "- The SLOT_EN hold across a panel reset (ARCHITECTURE.md section 4.3): in no generator at this revision.",
          "- Whether a line's state is proved: the EMCON items L1 to L4 and L7 and SD-EMC-1 are drawn in these netlists on boards A, B, C "
          "and D since their round 8 (the buffers, the single gates, the per-slot EMCON_ON1..3, the 5G supply removal; board D's "
          "U21, which no control line drives, is on the power tree); their status, CLOSED at desk or OPEN, with the bench rows owed, is v2/docs/feasibility/EMCON.md sections 3, 4a and 4b, not this drawing.",
          "- Board E5: no schematic; its board file names the nets it passes."]
    return "\n".join(L) + "\n"


def main():
    check = "--check" in sys.argv
    head, dirty = N.git_rev([N.BOARDS[b] for b in BOARD_ORDER] + [INTERFACES])
    nls, nodes, edges, table, pull_rows, link_rows, problems = build()
    mmd = mermaid(nls, nodes, edges, pull_rows, head)
    md = markdown(nls, table, pull_rows, link_rows, problems, head, dirty)
    if check:
        same = all(os.path.exists(p) and open(p, encoding="utf-8").read().split("\n", 3)[3:] == t.split("\n", 3)[3:]
                   for p, t in ((OUT_MMD, mmd),))
        print("control-lines: %s" % ("current" if same else "STALE against the netlists")); return 0 if same else 1
    os.makedirs(os.path.dirname(OUT_MMD), exist_ok=True)
    open(OUT_MMD, "w", encoding="utf-8").write(mmd)
    open(OUT_MD, "w", encoding="utf-8").write(md)
    print("control-lines: %d nodes, %d edges, %d link rows, problems: %s" % (len(nodes), len(edges), len(link_rows), problems or "none"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
