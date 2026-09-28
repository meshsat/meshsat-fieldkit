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
        elif kw in ("voltage range",) and cur_model:
            v = arg.split()
            if len(v) >= 3: models[cur_model]["vrange"] = tuple(num(x) for x in v[:3])
    return {"components": comps, "selectors": sels, "models": models}


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
            UNKNOWN (no such component or pin, a model the file does not define, or a filter that admits nothing)."""
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
    best, drives, missing, untyped = None, False, [], []
    for n in admitted:
        d = ib["models"].get(n.lower())
        if d is None: missing.append(n); continue
        if not d.get("type"): untyped.append(n); continue
        e = model_edge(d)
        if e is None: continue
        drives = True
        if best is None or e[0] < best[0]: best = (e[0], "%s %s" % (d["name"], e[1]))
    if missing: return "UNKNOWN", None, "pin %s %s names model(s) %s the file does not define" % (ipin, sig, ", ".join(missing))
    if untyped: return "UNKNOWN", None, "pin %s %s: model(s) %s carry no Model_type, so what they drive is not known" % (ipin, sig, ", ".join(untyped))
    if not drives: return "INPUT", None, "pin %s %s: model %s drives nothing" % (ipin, sig, "/".join(admitted))
    if best is None: return "UNKNOWN", None, "pin %s %s: model %s drives but carries no [Ramp]" % (ipin, sig, "/".join(admitted))
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
