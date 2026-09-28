#!/usr/bin/env python3
"""A maker's IBIS model, read for the one number rule SI-001 needs from it: how fast a pin's output can move
(MESHSAT-1357, 27 September 2026, layer 9).

WHY THIS EXISTS. SI-001's edge rate is a property of the DRIVER, and for most parts on this board set the maker
publishes no rise time in the datasheet (the STM32H743 publishes only MAXIMUM rise times per speed setting, the LVC
logic datasheets publish propagation delays, the RP2040 a slew-rate bit). What several makers DO publish is an IBIS
model, the industry's behavioural model of each I/O buffer, and its [Ramp] keyword states the output's transition
in the model's own terms: dV/dt_r and dV/dt_f, each as "dV/dt" where dV is the 20 to 80 percent voltage swing and dt
the time it takes, into the stated R_load, at three corners (typ, min, max). So the number is the maker's, read out
of the maker's file, never typed in by this project.

WHAT IT RETURNS, per pin of one [Component]: the model the pin uses (through a [Model Selector] when the pin names
one, every selectable model the caller's filter admits), the model's type, and the FASTEST driven transition over the
admitted models, both edges and all three corners, as the 20 to 80 percent time in nanoseconds. Choices, each stated:
  * a pin whose model is an input, a terminator, power, ground or no-connect drives nothing and returns no edge;
  * an open-drain or open-sink output drives only its falling edge (its rising edge in the model is the test
    fixture's pull-up, not the part), an open-source output only its rising edge;
  * the 20 to 80 percent time is used as it stands, without stretching it to 10 to 90 percent: a linear ramp's
    10 to 90 percent time is 4/3 of it and a real edge's is longer still, so leaving it short can only shorten the
    critical length computed from it (the conservative direction for SI-001);
  * the fastest corner is taken whatever the corner is called: in ST's STM32H743 file the typ column is faster than
    the max column on the falling edge, so no corner is assumed to be the fast one.
IT FAILS CLOSED (27 September 2026, second pass, on the independent check's findings): a model the file defines with
no Model_type is UNKNOWN, never an input (an untyped model would otherwise read as a pin that drives nothing), and the
keyword is read as IBIS allows it to be written, with spaces or with underscores ([Model Selector], [Model_Selector]).

A [Ramp] CELL IS HELD TO THE MODEL'S OWN V-t TABLE (28 September 2026, stream w5si2, on two AI reviews' findings: the
first lens's M5 and the drafts check's M8). A cell is "dV/dt": dV is by the keyword's definition the 20 to 80 percent
swing and dt the time that swing takes. Where the same model carries a [Rising Waveform] or [Falling Waveform] table
of that edge in the [Ramp]'s own fixture (R_fixture equal to R_load), the cell is compared with it, corner by corner:
  * dV must be 50 to 70 percent of the table's swing (RAMP_DV: "about 60 percent");
  * dt must be within 25 percent of the time the table itself takes from 20 to 80 percent of its swing (RAMP_DT).
A cell that fails either is CONTRADICTED by its own model: it is not read as a transition time, and a pin any of whose
admitted driven cells is contradicted reads FLAGGED, never DRIVES, so it gives no maker's figure and governs no net
(edge_length.py takes the instantaneous bound for it, ER-D16). Measured on the thirteen models held on 28 September
2026: of 585 driven cells 537 have a table to be held to; 522 of them hold (504 with dt within 10 percent), and 15 do
not: TI's PCA9555 INT models (dV about 60 percent, dt a seventh to a half of the table's time) and TI's TMP117 SDA
models (dV 11 to 39 percent of the swing). 48 cells have no table of their edge (ST's reset and VBUS models, TI's
USB 3 and PCIe transmitter models): nothing in the file can contradict them, they are read as before and
`unchecked` says so. The two tolerances are this stream's (session decision ER-D16): they sit in the gap the
measurement shows, and they can only take a figure away, never give one.
Nothing here judges a board. edge_length.py asks it for the pins a netlist puts on a net.

Usage: ibis_read.py <file.ibs> [component] [model-regex]   prints each pin's model and fastest edge
"""
import os, re, sys, hashlib

SCALE = {"T": 1e12, "G": 1e9, "M": 1e6, "k": 1e3, "K": 1e3, "m": 1e-3, "u": 1e-6, "n": 1e-9, "p": 1e-12, "f": 1e-15}
# the IBIS model types that drive a pin, and which edges each drives
DRIVES = {"output": "rf", "i/o": "rf", "3-state": "rf", "i/o_open_drain": "f", "open_drain": "f", "i/o_open_sink": "f",
          "open_sink": "f", "i/o_open_source": "r", "open_source": "r", "output_ecl": "rf", "i/o_ecl": "rf",
          "3-state_ecl": "rf"}
NOT_A_MODEL = {"power", "gnd", "nc"}
RAMP_DV = (0.5, 0.7)      # a cell's dV over its V-t table's swing: the keyword defines it as 60 percent (20 to 80)
RAMP_DT = (0.75, 1.25)    # a cell's dt over the table's own 20 to 80 percent time
R_LOAD_DEFAULT = 50.0     # IBIS: a [Ramp] that states no R_load was taken into 50 ohm


def num(s):
    """An IBIS number with its scale suffix (IBIS: M is mega, m milli), or None."""
    m = re.match(r"^\s*([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)([TGMkKmunpf]?)", s or "")
    if not m: return None
    return float(m.group(1)) * SCALE.get(m.group(2), 1.0)


def _strip(text):
    """The file without comments. IBIS's comment character is | unless [Comment Char] says otherwise."""
    cc = "|"
    m = re.search(r"(?im)^\[Comment Char\]\s+(\S)_char", text)
    if m: cc = m.group(1)
    return "\n".join(line.split(cc, 1)[0].rstrip() for line in text.splitlines())


def _sections(text):
    """[(keyword lower, argument, body)] in file order. IBIS treats a space and an underscore in a keyword as the same
    character, so both spellings are read as the one with spaces."""
    out = []
    ms = list(re.finditer(r"(?m)^\[([^\]]+)\]([^\n]*)$", text))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        out.append((" ".join(m.group(1).replace("_", " ").split()).lower(), m.group(2).strip(), text[m.end():end]))
    return out


def parse(text):
    """{"components": {name: {pin: (signal, model)}}, "selectors": {name lower: [model]}, "models": {name lower: {...}}}"""
    t = _strip(text)
    comps, sels, models = {}, {}, {}
    cur_comp, cur_model = None, None
    for kw, arg, body in _sections(t):
        if kw == "component":
            cur_comp = arg.split()[0] if arg else None
            comps.setdefault(cur_comp, {})
            cur_model = None
        elif kw == "pin" and cur_comp:
            for line in body.splitlines():
                f = line.split()
                if len(f) >= 3: comps[cur_comp][f[0]] = (f[1], f[2])
        elif kw == "model selector":
            sels[arg.split()[0].lower()] = [line.split()[0] for line in body.splitlines() if line.split()]
        elif kw == "model":
            cur_model = arg.split()[0].lower()
            d = models.setdefault(cur_model, {"name": arg.split()[0]})
            mt = re.search(r"(?im)^\s*Model_type\s+(\S+)", body)
            if mt: d["type"] = mt.group(1).lower()
        elif kw == "ramp" and cur_model:
            d = models[cur_model]
            for edge in ("r", "f"):
                x = re.search(r"(?im)^\s*dV/dt_%s\s+(\S+)\s+(\S+)\s+(\S+)" % edge, body)
                if not x: continue
                trip = []
                for cell in x.groups():
                    if "/" in cell:
                        dv, dt = cell.split("/", 1)
                        trip.append((num(dv), num(dt)))
                    else:
                        trip.append(None)
                d[edge] = trip
                d[edge + "_cells"] = list(x.groups())        # the cells as the file writes them, for a citation
            rl = re.search(r"(?im)^\s*R_load\s*=\s*(\S+)", body)
            if rl: d["r_load"] = num(rl.group(1))
        elif kw in ("rising waveform", "falling waveform") and cur_model:
            w = {"edge": kw[0], "rows": []}
            for line in body.splitlines():
                m = re.match(r"^\s*([RVCL]_fixture(?:_min|_max)?)\s*=\s*(\S+)", line)
                if m: w[m.group(1).lower()] = num(m.group(2)); continue
                f = line.split()
                if len(f) >= 4 and num(f[0]) is not None:
                    w["rows"].append(tuple(None if x.upper() == "NA" else num(x) for x in f[:4]))
            models[cur_model].setdefault("waves", []).append(w)
        elif kw in ("voltage range",) and cur_model:
            v = arg.split()
            if len(v) >= 3: models[cur_model]["vrange"] = tuple(num(x) for x in v[:3])
    return {"components": comps, "selectors": sels, "models": models}


def _t2080(rows, col):
    """(the time one column of a V-t table takes from 20 to 80 percent of its own swing, the swing), or (None, None)
    when the column has fewer than two values or does not move. Each level is taken at its FIRST crossing, by linear
    interpolation between the table's rows."""
    pts = [(r[0], r[col]) for r in rows if r[0] is not None and r[col] is not None]
    if len(pts) < 2 or pts[0][1] == pts[-1][1]: return None, None
    v0, v1 = pts[0][1], pts[-1][1]

    def cross(frac):
        target = v0 + frac * (v1 - v0)
        for (ta, va), (tb, vb) in zip(pts, pts[1:]):
            if va != vb and (va - target) * (vb - target) <= 0: return ta + (target - va) / (vb - va) * (tb - ta)
        return None
    a, b = cross(0.2), cross(0.8)
    if a is None or b is None or b <= a: return None, None
    return b - a, abs(v1 - v0)


def cell_check(d, edge, i):
    """(state, why) for the [Ramp] cell of one model, `edge` "r" or "f", corner `i` (0 typ, 1 min, 2 max):
    HOLDS         a V-t table of that edge agrees with the cell (RAMP_DV and RAMP_DT);
    CONTRADICTED  the model has such tables and none agrees: `why` gives the nearest table's numbers;
    NO_TABLE      the model carries no table of that edge with a value in that corner, so nothing can hold the cell.
    The tables used are those in the [Ramp]'s own fixture (R_fixture within 1 percent of R_load); a model none of whose
    tables is in that fixture is held to the tables it has, and `why` says so."""
    c = ((d or {}).get(edge) or [None, None, None])[i]
    if not c or not c[0] or not c[1]: return "NO_TABLE", "the cell is not a number"
    tabs = [w for w in (d.get("waves") or []) if w["edge"] == edge]
    rl = d.get("r_load") or R_LOAD_DEFAULT
    same = [w for w in tabs if w.get("r_fixture") and abs(w["r_fixture"] - rl) <= 0.01 * rl]
    near = None
    for w in (same or tabs):
        t, swing = _t2080(w["rows"], i + 1)
        if t is None: continue
        rv, rt = abs(c[0]) / swing, c[1] / t
        if RAMP_DV[0] <= rv <= RAMP_DV[1] and RAMP_DT[0] <= rt <= RAMP_DT[1]: return "HOLDS", ""
        score = abs(rv - 0.6) + abs(rt - 1.0)
        if near is None or score < near[0]: near = (score, rv, rt, swing, t, w.get("r_fixture"), w.get("v_fixture"))
    if near is None: return "NO_TABLE", "the model carries no V-t table of this edge with a value in this corner"
    _s, rv, rt, swing, t, rf, vf = near
    return "CONTRADICTED", ("dV %.4g V is %.0f percent of its own V-t table's swing (%.4g V) and dt %.4g ns is %.2f of the "
                            "time that table takes from 20 to 80 percent (%.4g ns), R_fixture %s ohm, V_fixture %s V%s" % (
                                abs(c[0]), 100.0 * rv, swing, c[1] * 1e9, rt, t * 1e9,
                                ("%g" % rf) if rf is not None else "not stated", ("%g" % vf) if vf is not None else "not stated",
                                "" if same else " (no table is in the [Ramp]'s own fixture of %g ohm)" % rl))


def model_flags(d):
    """[(which, why)] every DRIVEN [Ramp] cell of one model that its own V-t table contradicts ("f max" and the
    like); [] when none does or the model drives nothing."""
    out = []
    for e in DRIVES.get((d or {}).get("type") or "") or "":
        for i, c in enumerate(d.get(e) or []):
            if not (c and c[1] and c[1] > 0): continue
            st, why = cell_check(d, e, i)
            if st == "CONTRADICTED": out.append(("%s %s" % (e, ("typ", "min", "max")[i]), why))
    return out


def model_unchecked(d):
    """["f max", ...] the driven [Ramp] cells of one model that no V-t table of the model can hold (NO_TABLE)."""
    out = []
    for e in DRIVES.get((d or {}).get("type") or "") or "":
        for i, c in enumerate(d.get(e) or []):
            if c and c[1] and c[1] > 0 and cell_check(d, e, i)[0] == "NO_TABLE": out.append("%s %s" % (e, ("typ", "min", "max")[i]))
    return out


def model_edge(d):
    """(dt_ns, "r|f corner") the fastest DRIVEN 20-80 transition of one model, or None when it drives nothing."""
    edges = DRIVES.get((d or {}).get("type") or "")
    if not edges: return None
    best = None
    for e in edges:
        for i, c in enumerate(d.get(e) or []):
            if c and c[1] and c[1] > 0:
                v = c[1] * 1e9
                if best is None or v < best[0]: best = (v, "%s %s" % (e, ("typ", "min", "max")[i]))
    return best


def model_cell(d, which):
    """The [Ramp] cell of a model as the file writes it, for `which` = "r max" and the like, or None."""
    try:
        e, corner = which.split()
        return (d.get(e + "_cells") or [])[("typ", "min", "max").index(corner)]
    except (ValueError, IndexError, AttributeError):
        return None


_CACHE = {}


def load(path):
    """parse(path), cached by content."""
    raw = open(path, "rb").read()
    h = hashlib.sha256(raw).hexdigest()
    if h not in _CACHE: _CACHE[h] = parse(raw.decode("utf-8", errors="replace"))
    return _CACHE[h]


def pin_edge(ib, component, pin, model_re=None, by="number"):
    """(status, edge_ns or None, how) for one pin of one component.
    status: DRIVES (edge_ns the fastest admitted model's driven 20-80 time), INPUT (the pin's models drive nothing),
            FLAGGED (the pin drives, and a [Ramp] cell of an admitted model is contradicted by the model's own V-t
            table, so the file gives no transition time that can be relied on for this pin: no edge is returned),
            UNKNOWN (no such component or pin, a model the file does not define, or a filter that admits nothing).
    A FLAGGED pin is flagged whichever of its cells is the fastest: leaving the contradicted cell out and reading the
    next one would give a slower figure than the table the cell was contradicted by may hold."""
    comp = ib["components"].get(component)
    if comp is None: return "UNKNOWN", None, "the file has no [Component] %s" % component
    row = None
    if by == "name":
        row = next(((p, s, m) for p, (s, m) in comp.items() if s.upper() == str(pin).upper()), None)
    elif str(pin) in comp:
        s, m = comp[str(pin)]
        row = (str(pin), s, m)
    if row is None: return "UNKNOWN", None, "pin %s is not in [Component] %s" % (pin, component)
    ipin, sig, mname = row
    if mname.lower() in NOT_A_MODEL: return "INPUT", None, "pin %s %s is %s" % (ipin, sig, mname)
    names = ib["selectors"].get(mname.lower()) or [mname]
    rx = re.compile(model_re) if model_re else None
    admitted = [n for n in names if (rx is None or rx.search(n))]
    if not admitted: return "UNKNOWN", None, "no model of %s is admitted by %r" % (mname, model_re)
    best, drives, missing, untyped, flagged = None, False, [], [], []
    for n in admitted:
        d = ib["models"].get(n.lower())
        if d is None: missing.append(n); continue
        if not d.get("type"): untyped.append(n); continue
        e = model_edge(d)
        if e is None: continue
        drives = True
        flagged += ["[Model] %s [Ramp] dV/dt_%s: %s" % (d["name"], which, why) for which, why in model_flags(d)]
        if best is None or e[0] < best[0]: best = (e[0], "%s %s" % (d["name"], e[1]))
    if missing: return "UNKNOWN", None, "pin %s %s names model(s) %s the file does not define" % (ipin, sig, ", ".join(missing))
    if untyped: return "UNKNOWN", None, "pin %s %s: model(s) %s carry no Model_type, so what they drive is not known" % (ipin, sig, ", ".join(untyped))
    if not drives: return "INPUT", None, "pin %s %s: model %s drives nothing" % (ipin, sig, "/".join(admitted))
    if best is None: return "UNKNOWN", None, "pin %s %s: model %s drives but carries no [Ramp]" % (ipin, sig, "/".join(admitted))
    if flagged:
        return "FLAGGED", None, ("pin %s %s: %d [Ramp] cell(s) of its admitted model(s) are contradicted by the model's own "
                                 "V-t table, so the file gives this pin no transition time: %s" % (ipin, sig, len(flagged), flagged[0]))
    return "DRIVES", best[0], "pin %s %s, %s" % (ipin, sig, best[1])


def fastest(ib, component, model_re=None):
    """(edge_ns, how) the fastest driving pin of the component under the filter, or (None, why)."""
    comp = ib["components"].get(component)
    if comp is None: return None, "the file has no [Component] %s" % component
    best = None
    for p in comp:
        st, e, how = pin_edge(ib, component, p, model_re)
        if st == "DRIVES" and (best is None or e < best[0]): best = (e, how)
    return best if best else (None, "no pin of %s drives" % component)


def flagged_pins(ib, component, model_re=None):
    """[(pin, how)] the pins of the component that read FLAGGED under the filter, in pin order."""
    comp = ib["components"].get(component) or {}
    out = []
    for p in sorted(comp, key=lambda x: (len(x), x)):
        st, _e, how = pin_edge(ib, component, p, model_re)
        if st == "FLAGGED": out.append((p, how))
    return out


def fastest_cite(ib, component, model_re=None):
    """(keyword, cell) WHERE in the file the fastest driving pin's number is, as a record cites it:
    "[Model] <name> [Ramp] dV/dt_<r|f> <typ|min|max>" and the cell as the file writes it ("1.99/0.255n"); or
    (None, None) when no pin drives."""
    e, how = fastest(ib, component, model_re)
    if e is None: return None, None
    name, edge, corner = how.split(", ", 1)[1].rsplit(" ", 2)
    d = ib["models"].get(name.lower()) or {}
    return "[Model] %s [Ramp] dV/dt_%s %s" % (name, edge, corner), model_cell(d, "%s %s" % (edge, corner))


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    ib = load(sys.argv[1])
    comps = [sys.argv[2]] if len(sys.argv) > 2 else list(ib["components"])
    rx = sys.argv[3] if len(sys.argv) > 3 else None
    for c in comps:
        print("[Component] %s: fastest %s" % (c, fastest(ib, c, rx)))
        for p in sorted(ib["components"].get(c, {}), key=lambda x: (len(x), x)):
            st, e, how = pin_edge(ib, c, p, rx)
            print("  %-5s %-7s %-10s %s" % (p, st, "%.4f ns" % e if e is not None else "-", how))
