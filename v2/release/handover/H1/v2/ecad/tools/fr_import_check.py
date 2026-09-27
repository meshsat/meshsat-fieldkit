#!/usr/bin/env python3
"""fr_import_check.py: what Freerouting 1.9.0 said about the DSN it imported, whether that is understood, and whether the
board it routed is the board the DSN declares (MESHSAT-1357 round 8, review finding F of 26 September 2026).

    classify <fr.log> <dsn> [--title T] [--stage dialog|import] [--exited] [--json OUT]
        exit 0: every warning of the import is a KNOWN one whose consequence is bounded, so the DSN reader's dialog
        may be dismissed; exit 3: refuse (an unknown warning, any error, or a dialog that nothing in the log explains;
        an import ended by "Couldn't create window frame"; with --exited, the router having ended, an import that
        never reached a line that ends it).
    survive <dsn> <ses> [--ignore-classes a,b] [--warned-nets n1,n2] [--json OUT]
        exit 0: the router's session carries every user-fixed wire and via the DSN declares (KiCad's locked copper,
        type fix, is never written to a session; `import` checks that), names no net the DSN does not declare, and
        lays its own copper at its class's width, on its class's layers and with its class's vias, and none on a net
        whose class the job ignores; exit 3: something the DSN declares was lost; exit 2: an input could not be read.
    timing <fr.log> [--events EV.jsonl] [--json OUT] [--label L]
        the stage timing of one run (input load, time blocked on a dialog, active routing, optimiser, the error lines
        logged while routing), one line for the run log and the whole record as JSON. Run it on the router's host: the
        log's timestamps are in the JVM's local time and the watcher's events in epoch seconds of the same clock.
    import <dsn> <written-back dsn> [--json OUT]
        exit 0: the board the router holds after importing <dsn> (its own DSN export, fr_import_probe) carries every
        layer, net with its pins, class with its width, clearance, layers and vias, keep-out, plane, wire and via the
        DSN declares; exit 3: something was lost; exit 2: unreadable.
    probe-dsn <in.dsn> <out.dsn>
        the probe's copy: one settings block that turns the autorouter and the optimiser off.
    probe-rules <in.rules> <out.rules>
        the same for a rules file passed with -dr, which is read after the import and would switch them back on.
    event <EV.jsonl> key=value ...
        append one JSON event line (the watcher's record; the shell cannot quote a window title safely itself).

WHY THIS EXISTS. On 26 September 2026 both arms of board B's escape trial sat 57 minutes on Freerouting's "DSN file
reader" dialog. The watcher was changed to find that window by its title and press Return, and the review of the same
evening asked that it stop pressing Return on a warning nobody had read. What the dialog is, from the source of the jar
this project runs (freerouting v1.9.0, interactive/BoardHandling.java:836-878):

  * `import_design` clears FRLogger's in-memory entries, reads the DSN (DsnFile.read) and runs
    `reduce_nets_of_route_items`, and if any WARNING or ERROR entry was collected meanwhile it shows ALL the entries in
    a JOptionPane titled "DSN file reader - Freerouting" (resource dsn_reader_modal_title), as ERROR_MESSAGE when an
    error was among them and WARNING_MESSAGE otherwise. The call blocks the main thread until the dialog is closed, and
    the autorouter is started by that same thread afterwards (gui/MainApplication.java:470-532), so nothing is routed
    while it is open.
  * Every entry FRLogger collects is ALSO written by log4j (logger/FRLogger.java; src/main/resources/log4j2.xml sends
    INFO and above to standard output with the pattern `yyyy-MM-dd HH:mm:ss.SSS [thread] LEVEL message`), and every
    launcher sends standard output to its fr.log. So the entries that RAISE the dialog, the warnings and the errors,
    are all in the log before the dialog appears; the dialog additionally lists DEBUG and TRACE entries the log omits,
    and those raise nothing. Reading the log is reading the dialog's decisive content.

WHICH WARNINGS ARE HARMLESS, and why only these (the table KNOWN below). The DSN reader has about 270 warn and error
calls (designforms/specctra/*.java). Almost every one of them means something the DSN declares was DROPPED: a wire with
a corner outside the board (Wiring.java:482 returns null), a via whose net or padstack is unknown (Wiring.java:604, 610),
a net class whose via rule or layer is not found (Network.java:439-515), a class pair that names a missing class
(Network.java:550-558). Continuing past any of those routes a board that is not the one declared, so they are refused.
Two are understood and bounded:

  FR-NORMALISE-NET  "The normalization of net '<net>' failed." (Wiring.java:341-347). After the whole wiring scope is
      read, `board.normalize_traces(net)` runs for every net; PolylineTrace.normalize throws past its depth limit of 16
      (PolylineTrace.java:33, 675-679) and the reader logs this and carries on. The wires themselves are already on the
      board (read_wire_scope inserts with `insert_trace_without_cleaning`, "Traces are not yet normalized here",
      Wiring.java:489-493), and the net, its pins, its class and its rules were read in the structure and network
      scopes before the wiring. What is left undone is splitting the net's fixed wires at their junctions and merging
      collinear pieces. The direction of the error is known: a trace touches another trace only at a SHARED END CORNER
      (board/Trace.java:167-203, get_normal_contacts), so an unsplit junction is a contact the router does not see,
      never a contact it invents. The router may therefore lay a wire it did not need; it cannot take a missing
      connection for a made one, and the routed board is judged by KiCad's own connectivity afterwards in any case.
      CONDITION: the net's fixed copper must reach the router's session (the `survive` check, which every launcher runs).
  FR-NO-HELP-JAR  "Online-Help deactivated because system file jh.jar is missing" (gui/BoardFrame.java:166). The GUI
      help system is not in the jar. It is logged by the frame's constructor, BEFORE import_design clears the entries,
      so it is never part of the dialog; it is listed so that reading the whole import window does not refuse on it.

Anything else, at WARN or ERROR, is refused, and so is an ERROR entry of any text: the dialog is an error dialog then,
and the reader returned something it could not read. A dialog with no WARN or ERROR line in the log since this DSN was
opened is refused as well, because what it says cannot be established.

MEASURED on the KiCad box, 26 September 2026 (box clock UTC 21:02 to 22:02), board B's committed pre-route board
(sha256 62facf09...), S3 confined as the escape trial ran it: the dialog listed exactly the seven FR-NORMALISE-NET lines
the log holds (/ETH2_P2_N, /ETH3_P2_N, /HOST3_1D_N, /LIME_SSRX_P, /LIME_SSTX_N, /PCIE3_CLK_N, /SWP4_C_N) and nothing
else; the board the jar held afterwards carried all 844 nets with their 3,959 pins, 25 classes, 178 keep-outs, 4,011
wires and 2,218 vias of the DSN, the seven nets' copper included; pass 1's session kept every class. Two things the same
night showed that a quiet import is not a sound one, both caught here: a settings scope placed after a keep-out makes
1.9.0 drop everything after the structure WITHOUT A WORD (structure_lint), and normalisation shortens a wire that
overshoots a pad or via centre by 20 to 45 um (_in_pad), which is not a loss.
"""
import json, math, os, re, sys, time

LOG_LINE = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}) \[([^\]]*)\] (TRACE|DEBUG|INFO|WARN|ERROR|FATAL)\s+(.*)$")
DSN_DIALOG = "DSN file reader - Freerouting"      # interactive/BoardHandling_en.properties: dsn_reader_modal_title
MAIN_FRAME = "Board Layout - Freerouting"          # the board frame; never a dialog

KNOWN = [
    {"id": "FR-NORMALISE-NET", "level": "WARN",
     "pattern": r"^The normalization of net '(?P<net>.*)' failed\.$",
     "source": "designforms/specctra/Wiring.java:341-347 (freerouting v1.9.0)",
     "consequence": "the net's fixed wires stay on the board as read, not split at junctions or merged; a missing "
                    "contact is possible, an invented one is not (board/Trace.java:167-203)",
     "condition": "survive: the net's fixed copper must reach the router's session"},
    {"id": "FR-NO-HELP-JAR", "level": "WARN",
     "pattern": r"^Online-Help deactivated because system file jh\.jar is missing$",
     "source": "gui/BoardFrame.java:166",
     "consequence": "none on the board; logged before the import clears its entries, so never part of the dialog",
     "condition": None},
]
# Raw lines (not log4j's pattern) that are known and carry nothing: log4j's own status line under a non-multi-release
# classpath. Any other raw line inside the import window that looks like an exception or an error is refused.
RAW_KNOWN = [r"^WARNING: Runtime environment or build system does not support multi-release JARs"]
RAW_BAD = re.compile(r"Exception|Error|SEVERE|FATAL|Caused by")
IMPORT_END = ("Starting auto-routing...", "Multi-threaded route optimization is broken", "Couldn't create window frame")


# ---------------------------------------------------------------------------------------------------- the log
def read_log(path):
    """Entries as dicts {ts, level, thread, msg, extra[]}; a raw line becomes an entry of level RAW."""
    out = []
    try: lines = open(path, errors="replace").read().splitlines()
    except OSError: return None
    for ln in lines:
        m = LOG_LINE.match(ln)
        if m:
            out.append({"ts": m.group(1), "thread": m.group(2), "level": m.group(3), "msg": m.group(4), "extra": []})
        elif out and (ln.startswith("\t") or ln.startswith("java.") or ln.startswith("Caused by") or ln.startswith("...")):
            out[-1]["extra"].append(ln)
        elif ln.strip():
            out.append({"ts": None, "thread": None, "level": "RAW", "msg": ln, "extra": []})
    return out


def _same_dsn(path_in_log, dsn):
    a = path_in_log.strip().strip("'\"")
    return a == dsn or os.path.basename(a) == os.path.basename(dsn) or os.path.abspath(a) == os.path.abspath(dsn)


def import_window(entries, dsn):
    """The entries from the LAST "Opening '<dsn>'..." line to the first line that ends the import (or the log's end).
    Returns (window, opened, ended): ended is None while the import (or its dialog) is still in progress."""
    start = None
    for i, e in enumerate(entries):
        m = re.match(r"^Opening '(.*)'\.\.\.$", e["msg"]) if e["level"] == "INFO" else None
        if m and _same_dsn(m.group(1), dsn): start = i
    if start is None: return [], None, None
    end = None
    for j in range(start + 1, len(entries)):
        if entries[j]["level"] != "RAW" and entries[j]["msg"].startswith(IMPORT_END): end = j; break
    win = entries[start + 1:end] if end is not None else entries[start + 1:]
    return win, entries[start], (entries[end] if end is not None else None)


def classify_entries(win):
    """Each WARN/ERROR/RAW entry of the window with its verdict. Returns (rows, allowed, reasons)."""
    rows = []; reasons = []
    for e in win:
        if e["level"] in ("INFO", "DEBUG", "TRACE"): continue
        if e["level"] == "RAW":
            if any(re.search(p, e["msg"]) for p in RAW_KNOWN): rows.append({"level": "RAW", "msg": e["msg"], "known": "RAW-KNOWN"}); continue
            if RAW_BAD.search(e["msg"]):
                rows.append({"level": "RAW", "msg": e["msg"], "known": None}); reasons.append("an exception or error line outside the log format: %s" % e["msg"][:160])
            continue
        hit = None
        for k in KNOWN:
            if k["level"] == e["level"] and re.match(k["pattern"], e["msg"]): hit = k; break
        row = {"level": e["level"], "ts": e["ts"], "msg": e["msg"], "known": hit["id"] if hit else None}
        if e["extra"]: row["trace"] = e["extra"][:6]
        if hit and hit["id"] == "FR-NORMALISE-NET":
            row["net"] = re.match(hit["pattern"], e["msg"]).group("net")
        rows.append(row)
        if e["level"] in ("ERROR", "FATAL"):
            reasons.append("an ERROR entry (the dialog is an error dialog; the reader returned something it could not read): %s" % e["msg"][:160])
        elif not hit:
            reasons.append("an UNKNOWN warning: %s" % e["msg"][:160])
    return rows, not reasons, reasons


def cmd_classify(a):
    log, dsn = a[0], a[1]; title = _opt(a, "--title"); stage = _opt(a, "--stage") or "dialog"; out = _opt(a, "--json")
    exited = "--exited" in a
    entries = read_log(log)
    rec = {"tool": "fr_import_check classify", "log": log, "dsn": dsn, "title": title, "stage": stage,
           "router_exited": exited, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if entries is None:
        rec.update(decision="REFUSE", reasons=["the router's log could not be read, so the dialog's content is unknown"])
    else:
        win, opened, ended = import_window(entries, dsn)
        rows, ok, reasons = classify_entries(win)
        rec.update(opened=opened and opened["ts"], import_end=ended and ended["ts"], entries=rows,
                   warnings=sum(1 for r in rows if r["level"] == "WARN"), errors=sum(1 for r in rows if r["level"] in ("ERROR", "FATAL")))
        if opened is None:
            ok = False; reasons = ["the log has no \"Opening '%s'...\" line, so the lines the dialog shows cannot be told from any other" % os.path.basename(dsn)]
        elif stage == "dialog" and not any(r["level"] in ("WARN", "ERROR", "FATAL") for r in rows):
            ok = False; reasons = ["a dialog is open and no WARN or ERROR line since the DSN was opened explains it"]
        # the import's own end line can be its failure: create_board_frame returned null (the DSN was not read, or its
        # input stream could not be opened) and MainApplication logs this at WARN and calls System.exit(1)
        # (gui/MainApplication.java:372-376, freerouting v1.9.0). The window stops before that line, so it is judged here.
        if ended is not None and ended["msg"].startswith("Couldn't create window frame"):
            ok = False; reasons = reasons + ["the router could not build its board from the DSN and exited (%s %s)" % (ended["level"], ended["msg"][:120])]
        # read after the router ended (the watcher's last reading): an import that never reached a line that ends it
        # was cut short, by a crash or a kill, and what it would have said next is unknown
        if exited and opened is not None and ended is None:
            ok = False; reasons = reasons + ["the router ended during its import: no line that ends an import (%s) follows the Opening line" % ", ".join(IMPORT_END)]
        known = sorted({r["known"] for r in rows if r.get("known") and r["known"] != "RAW-KNOWN"})
        rec.update(decision="CONTINUE" if ok else "REFUSE", reasons=reasons, known=known,
                   warned_nets=sorted({r["net"] for r in rows if r.get("net")}),
                   conditions=sorted({k["condition"] for k in KNOWN if k["id"] in known and k["condition"]}))
    _write(out, rec)
    if rec["decision"] == "CONTINUE":
        print("fr_import_check: %s: %d warning(s), all known (%s)%s" % (stage, rec.get("warnings", 0), ", ".join(rec["known"]) or "none",
              ("; nets " + ", ".join(rec["warned_nets"][:8]) + (" ..." if len(rec["warned_nets"]) > 8 else "")) if rec.get("warned_nets") else ""))
        return 0
    print("fr_import_check: %s: REFUSED: %s" % (stage, "; ".join(rec["reasons"][:4])))
    return 3


# ---------------------------------------------------------------------------------------------------- s-expressions
def sexp(text):
    """Parse a Specctra file into nested lists. A token is a run of quoted and bare pieces with no space between them,
    so Freerouting's `"T_SIG"-1` reads as the pin `T_SIG-1`, the way KiCad writes it bare."""
    # the parser scope declares the quote character as a bare '"', which a string pattern would read as an opening
    # quote running to the next one; KiCad and Freerouting both write exactly this form
    text = re.sub(r'\(string_quote\s+"\s*\)', "(string_quote QUOTE)", text)
    tok = re.compile(r'\(|\)|(?:"[^"]*"|[^\s()"]+)+')
    stack = [[]]
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(": stack.append([])
        elif t == ")":
            if len(stack) == 1: raise ValueError("unbalanced ')'")
            x = stack.pop(); stack[-1].append(x)
        else: stack[-1].append(t.replace('"', "") if '"' in t else t)
    if len(stack) != 1: raise ValueError("unbalanced '('")
    return stack[0][0] if stack[0] else []


def kids(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def kid(node, key):
    k = kids(node, key); return k[0] if k else None


UNIT_MM = {"um": 1e-3, "mm": 1.0, "mil": 0.0254, "inch": 25.4, "cm": 10.0}


def _res_mm(node):
    """(resolution um 10) -> (mm per unit, subdivisions)."""
    r = kid(node, "resolution")
    if not r: return None, None
    return UNIT_MM[r[1]], float(r[2])


def _num(x):
    try: return float(x)
    except (TypeError, ValueError): return None


def _intersect(l1, l2):
    """Corner of two lines, each given by two points (Freerouting's polyline_path)."""
    (x1, y1), (x2, y2) = l1; (x3, y3), (x4, y4) = l2
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(d) < 1e-12: return None
    a = x1 * y2 - y1 * x2; b = x3 * y4 - y3 * x4
    return ((a * (x3 - x4) - (x1 - x2) * b) / d, (a * (y3 - y4) - (y1 - y2) * b) / d)


def _path_points(pth, k):
    """Corner points in mm of a (path L W x y ...) or a (polyline_path L W ax ay bx by ...) whose every four numbers are
    one LINE through two points; a polyline's corners are the crossings of consecutive lines (geometry/planar/Polyline)."""
    nums = [_num(x) for x in pth[3:] if isinstance(x, str)]
    nums = [v * k for v in nums if v is not None]
    if pth[0] == "path": return list(zip(nums[0::2], nums[1::2]))
    lines = [((nums[i], nums[i + 1]), (nums[i + 2], nums[i + 3])) for i in range(0, len(nums) - 3, 4)]
    pts = []
    for a, b in zip(lines, lines[1:]):
        c = _intersect(a, b)
        if c is not None and (not pts or abs(c[0] - pts[-1][0]) > 1e-9 or abs(c[1] - pts[-1][1]) > 1e-9): pts.append(c)
    return pts


def _kind(ty):
    """A wiring item's fixed state as Freerouting reads it (Wiring.calc_fixed): fix is SYSTEM_FIXED, shove_fixed is
    SHOVE_FIXED, normal (or no type) is UNFIXED, and any other word is USER_FIXED, which it writes back as protect."""
    if ty in (None, "normal"): return "unfixed"
    if ty == "fix": return "fix"
    if ty == "shove_fixed": return "shove"
    return "protect"


def read_dsn(path):
    """Layers, nets with pins, classes with their rules, keep-outs, planes and wiring of a DSN written by KiCad or by
    Freerouting (which writes nets as `(net "N" 1 (pins "R"-1 ...))`, classes with a clearance class and a via rule, and
    wires as polyline_path). Coordinates in mm."""
    raw = open(path, errors="replace").read(); lint = structure_lint(raw)[0]
    t = sexp(raw)
    u = kid(t, "unit"); per, _n = _res_mm(t)
    k = UNIT_MM[u[1]] if u else (per or 1e-3)       # DSN coordinates are decimals in the file's (unit)
    st = kid(t, "structure") or []
    layers = {}
    for L in kids(st, "layer"):
        ty = kid(L, "type"); layers[L[1]] = ty[1] if ty else "signal"
    dvia = [x for v in kids(st, "via") for x in v[1:] if isinstance(x, str)]
    drule = kid(st, "rule"); dwidth = _width(drule, k)
    named_clear = {}
    for R in kids(st, "rule"):
        for c in kids(R, "clearance"):
            ty = kid(c, "type")
            if ty and len(ty) > 1 and _num(c[1]) is not None: named_clear[ty[1]] = _num(c[1]) * k
    keep = {}
    for kw in ("keepout", "via_keepout", "wire_keepout"):
        for K in kids(st, kw):
            shp = next((x for x in K[1:] if isinstance(x, list) and x and x[0] in ("polygon", "rect", "circle", "path")), None)
            lay = shp[1] if shp and len(shp) > 1 else "?"
            keep[(kw, lay)] = keep.get((kw, lay), 0) + 1
    planes = {}
    for P in kids(st, "plane"):
        shp = next((x for x in P[2:] if isinstance(x, list) and x), None)
        lay = shp[1] if shp and len(shp) > 1 else "?"
        planes[(P[1], lay)] = planes.get((P[1], lay), 0) + 1
    net = kid(t, "network") or []
    nets = {}
    for N in kids(net, "net"):
        p = kid(N, "pins"); nets.setdefault(N[1], set()).update(x for x in (p[1:] if p else []) if isinstance(x, str))
    via_def = {V[1]: V[2] for V in kids(net, "via") if len(V) > 2 and isinstance(V[2], str)}   # Freerouting: (via NAME PADSTACK CLEARANCE)
    via_rule = {R[1]: [x for x in R[2:] if isinstance(x, str)] for R in kids(net, "via_rule") if len(R) > 1}
    classes = {}; net_class = {}
    for C in kids(net, "class"):
        name = C[1]; members = [x for x in C[2:] if isinstance(x, str) and x != ""]
        circ = kid(C, "circuit") or []
        uv = [x for v in kids(circ, "use_via") for x in v[1:] if isinstance(x, str)]
        vr = kid(C, "via_rule")
        if vr and len(vr) > 1: uv = uv + [via_def.get(x, x) for x in via_rule.get(vr[1], [])]
        ul = [x for v in kids(circ, "use_layer") for x in v[1:] if isinstance(x, str)]
        rule = kid(C, "rule"); w = _width(rule, k)
        cl = None
        if rule:
            for c in kids(rule, "clearance"):
                if not kid(c, "type") and _num(c[1]) is not None: cl = _num(c[1]) * k
        cc = kid(C, "clearance_class")
        classes[name] = {"nets": members, "use_via": sorted(set(uv)), "use_layer": ul, "width": w if w is not None else dwidth,
                         "clearance": cl, "clearance_class": cc[1] if cc and len(cc) > 1 else None}
        for m in members: net_class[m] = name
    class_pairs = len(kids(net, "class_class"))
    lib = kid(t, "library") or []
    pads = {}                                       # padstack -> layer -> (offset x, offset y, inscribed radius) in mm
    for P in kids(lib, "padstack"):
        for sh in kids(P, "shape"):
            g = next((x for x in sh[1:] if isinstance(x, list) and x), None)
            if g: pads.setdefault(P[1], {})[g[1]] = _inscribed(g, k)
    pin_pads = _pin_pads(t, lib, pads, nets, list(layers), k)
    wires = []; vias = []
    wr = kid(t, "wiring") or []
    for W in kids(wr, "wire"):
        pth = kid(W, "path") or kid(W, "polyline_path")
        if not pth: continue
        nm = kid(W, "net"); ty = kid(W, "type")
        wires.append({"net": nm[1] if nm else None, "layer": pth[1], "width": float(pth[2]) * k,
                      "pts": _path_points(pth, k), "type": ty[1] if ty else "normal"})
    for V in kids(wr, "via"):
        nm = kid(V, "net"); ty = kid(V, "type")
        vias.append({"net": nm[1] if nm else None, "padstack": V[1], "x": float(V[2]) * k, "y": float(V[3]) * k,
                     "type": ty[1] if ty else "normal"})
    return {"layers": layers, "default_vias": dvia, "default_width": dwidth, "nets": nets, "classes": classes,
            "net_class": net_class, "wires": wires, "vias": vias, "named_clearance": named_clear, "keepouts": keep,
            "planes": planes, "class_pairs": class_pairs, "pads": pads, "pin_pads": pin_pads, "lint": lint}


def _inscribed(g, k):
    """A pad shape's centre offset and the radius of a circle inside it, in mm: exact for a circle and a rectangle, the
    smaller half-side of the bounding box for a polygon or a path (a pad polygon is a rounded rectangle here)."""
    nums = [v for v in (_num(x) for x in g[2:] if isinstance(x, str)) if v is not None]
    if g[0] == "circle" and nums:
        ox, oy = (nums[1], nums[2]) if len(nums) >= 3 else (0.0, 0.0)
        return (ox * k, oy * k, nums[0] * k / 2)
    if g[0] == "rect" and len(nums) >= 4:
        x1, y1, x2, y2 = nums[:4]
        return ((x1 + x2) / 2 * k, (y1 + y2) / 2 * k, min(abs(x2 - x1), abs(y2 - y1)) / 2 * k)
    pts = nums[1:] if g[0] in ("polygon", "path") else nums
    xs, ys = pts[0::2], pts[1::2]
    if not xs or not ys: return (0.0, 0.0, 0.0)
    extra = nums[0] / 2 if g[0] == "path" else 0.0
    return ((min(xs) + max(xs)) / 2 * k, (min(ys) + max(ys)) / 2 * k, (min(max(xs) - min(xs), max(ys) - min(ys)) / 2 + extra) * k)


def _pin_pads(t, lib, pads, nets, layer_order, k):
    """(net, layer) -> [(x, y, r)]: every pin's pad centre and inscribed radius on the board. A component placed on the
    back is mirrored in x before its rotation and its outer layers swap, as Specctra places it; the transform was
    checked on board B's DSN, where it puts 1,727 of 5,876 pre-laid wire ends exactly on a same-net pad centre and the
    other three conventions put fewer (1,686, 1,291 and 1,250)."""
    netof = {pn: n for n, pins in nets.items() for pn in pins}
    imgs = {I[1]: I for I in kids(lib, "image")}
    front, back = (layer_order[0], layer_order[-1]) if layer_order else ("F.Cu", "B.Cu")
    out = {}
    for C in kids(kid(t, "placement") or [], "component"):
        img = imgs.get(C[1])
        if not img: continue
        for P in kids(C, "place"):
            if len(P) < 6 or _num(P[2]) is None: continue
            ref, x, y, side, rot = P[1], _num(P[2]) * k, _num(P[3]) * k, P[4], _num(P[5]) or 0.0
            a = math.radians(rot); ca, sa = math.cos(a), math.sin(a)
            for pin in kids(img, "pin"):
                rest = [q for q in pin[2:] if not isinstance(q, list)]
                if len(rest) < 3: continue
                net = netof.get("%s-%s" % (ref, rest[0]))
                if not net: continue
                px, py = _num(rest[1]) * k, _num(rest[2]) * k
                pr = kid(pin, "rotate"); b = math.radians(_num(pr[1]) or 0.0) if pr else 0.0
                for L, (ox, oy, r) in pads.get(pin[1], {}).items():
                    qx, qy = px + ox * math.cos(b) - oy * math.sin(b), py + ox * math.sin(b) + oy * math.cos(b)
                    if side == "back":
                        qx = -qx; L = back if L == front else front if L == back else L
                    out.setdefault((net, L), []).append((x + qx * ca - qy * sa, y + qx * sa + qy * ca, r))
    return out


def _width(rule, k):
    if not rule: return None
    w = kid(rule, "width")
    return float(w[1]) * k if w else None


def read_ses(path):
    t = sexp(open(path, errors="replace").read())
    routes = kid(t, "routes") or []
    per, n = _res_mm(routes)
    k = per / n if per else 1e-4                    # session integers are in 1/resolution of the unit
    nets = {}
    for N in kids(kid(routes, "network_out") or [], "net"):
        ws = []; vs = []
        for W in kids(N, "wire"):
            pth = kid(W, "path")
            if not pth: continue
            ty = kid(W, "type"); pts = [float(x) * k for x in pth[3:] if isinstance(x, str)]
            ws.append({"layer": pth[1], "width": float(pth[2]) * k, "pts": list(zip(pts[0::2], pts[1::2])),
                       "type": ty[1] if ty else "normal"})
        for V in kids(N, "via"):
            ty = kid(V, "type")
            vs.append({"padstack": V[1], "x": float(V[2]) * k, "y": float(V[3]) * k, "type": ty[1] if ty else "normal"})
        nets[N[1]] = {"wires": ws, "vias": vs}
    return {"nets": nets}


# ---------------------------------------------------------------------------------------------------- survive
TOL = 0.002                   # mm: 2 um, twenty times the session's 0.1 um grid


def _seg_dist(p, a, b):
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
    if L2 == 0: return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _probe_points(pts):
    out = list(pts)
    for a, b in zip(pts, pts[1:]): out.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
    return out


def _pad_index(d):
    """(net, layer) -> [(x, y, r)]: every same-net copper that is a pad, pins and declared vias alike."""
    vpad = {key: list(v) for key, v in d["pin_pads"].items()}
    for v in d["vias"]:
        for L, (ox, oy, r) in d["pads"].get(v["padstack"], {}).items(): vpad.setdefault((v["net"], L), []).append((v["x"] + ox, v["y"] + oy, r))
    return vpad


def _in_pad(vpad, net, layer, pt, width):
    """The whole width of the copper at pt lies inside a same-net pad on that layer.

    NORMALISATION SHORTENS A SPIKE, AND THAT IS NOT A LOSS (measured on board B, 26 September 2026): a wire that
    overshoots a via's or a pad's centre and a stub that comes back along the same line are merged by
    PolylineTrace.combine, the 180-degree reversal collapses, and 20 to 45 um of overshoot are gone (vias of
    /NVME2_TX_P and /USB_5G_N, pad C281-1 of /ETH2_P3_P). Copper inside a same-net pad is copper the pad already is."""
    return any(math.hypot(pt[0] - x, pt[1] - y) + width / 2 <= r + TOL for x, y, r in vpad.get((net, layer), []))


def _ignored(d, tokens):
    """The classes a job's -inc list names, and the tokens that name no class. Freerouting splits -inc on commas
    (gui/StartupOptions.java:188-190) and KiCad 9 joins a net's classes with commas ("SENSE,Default"), so such a class
    is named by several tokens and matched by none: the router does NOT ignore it."""
    named = {c for c in tokens if c in d["classes"]}
    comma = {c for c in d["classes"] if "," in c and all(x in tokens for x in c.split(","))}
    used = set(named) | {x for c in comma for x in c.split(",")}
    return named, comma, [t for t in tokens if t not in used]


def survive(d, s, ignore=(), warned=()):
    """What the router WROTE (a session) against what the DSN declares. The findings, each {check, net, detail};
    empty means nothing the DSN declares was lost. Checked:
      net-declared   every net in the session is a DSN net (a renamed or invented net is a misread DSN)
      fixed          every USER_FIXED wire and via of the DSN (any wiring type but fix, shove_fixed and normal, which
                     1.9.0 writes back as protect) is on the session's protected copper; SYSTEM_FIXED copper (type
                     fix, KiCad's locked tracks) is never written to a session, so it is `import`'s to check
      class-layer    the router's wires lie on the layers the net's class allows (use_layer, else every signal layer)
      class-width    no router wire is wider than its class's width, and a routed net carries its class's width at all
                     (the automatic neck-down only narrows a wire at a pin)
      class-via      the router's vias are padstacks the class lists (use_via, else the structure's via list)
      ignored-class  a net whose class the job ignores (-inc) and that had no copper in the DSN has none now"""
    bad = []; info = {}
    named, comma, stray = _ignored(d, list(ignore))
    ignored_nets = {n for c in named | comma for n in d["classes"][c]["nets"]}
    info.update(ignored_classes=sorted(named), comma_classes_not_ignorable=sorted(comma), ignore_tokens_matching_no_class=stray)
    for n in s["nets"]:
        if n not in d["nets"]: bad.append({"check": "net-declared", "net": n, "detail": "the session carries copper on a net the DSN does not declare"})
    fixed_w = [w for w in d["wires"] if _kind(w["type"]) == "protect"]; fixed_v = [v for v in d["vias"] if _kind(v["type"]) == "protect"]
    info.update(dsn_user_fixed_wires=len(fixed_w), dsn_user_fixed_vias=len(fixed_v),
                dsn_system_fixed=sum(1 for x in d["wires"] + d["vias"] if _kind(x["type"]) == "fix"))
    sw = [dict(w, net=n) for n, sn in s["nets"].items() for w in sn["wires"] if _kind(w["type"]) == "protect"]
    grid = _cover_index(sw); vpad = _pad_index(d); lost_w = 0
    for w in fixed_w:
        for pt in _probe_points(w["pts"]):
            if _on(grid, w["net"], w["layer"], pt) or _in_pad(vpad, w["net"], w["layer"], pt, w["width"]): continue
            lost_w += 1
            if lost_w <= 20: bad.append({"check": "fixed-wire", "net": w["net"], "detail": "a fixed %s wire from (%.3f, %.3f) is not on the session's protected copper" % (w["layer"], w["pts"][0][0], w["pts"][0][1])})
            break
    sv = {}
    for n, sn in s["nets"].items():
        for v in sn["vias"]:
            if _kind(v["type"]) == "protect": sv.setdefault((n, v["padstack"], int(math.floor(v["x"] * 100)), int(math.floor(v["y"] * 100))), []).append((v["x"], v["y"]))
    lost_v = 0
    for v in fixed_v:
        cx, cy = int(math.floor(v["x"] * 100)), int(math.floor(v["y"] * 100))
        if not any(abs(x - v["x"]) <= TOL and abs(y - v["y"]) <= TOL
                   for i in (-1, 0, 1) for j in (-1, 0, 1) for x, y in sv.get((v["net"], v["padstack"], cx + i, cy + j), [])):
            lost_v += 1
            if lost_v <= 20: bad.append({"check": "fixed-via", "net": v["net"], "detail": "a fixed via %s at (%.3f, %.3f) is not in the session" % (v["padstack"], v["x"], v["y"])})
    if lost_w > 20 or lost_v > 20: bad.append({"check": "fixed-copper", "net": None, "detail": "%d fixed wire(s) and %d fixed via(s) lost in all" % (lost_w, lost_v)})
    info.update(fixed_wires_lost=lost_w, fixed_vias_lost=lost_v)
    routed_nets = 0; wrong_w = 0
    pre_laid = {w["net"] for w in d["wires"]} | {v["net"] for v in d["vias"]}
    for n, sn in s["nets"].items():
        if n not in d["nets"]: continue
        cname = d["net_class"].get(n); cls = d["classes"].get(cname, {})
        cw = cls.get("width") if cls else d["default_width"]
        free = [w for w in sn["wires"] if _kind(w["type"]) == "unfixed"]
        freev = [v for v in sn["vias"] if _kind(v["type"]) == "unfixed"]
        if n in ignored_nets:
            if n not in pre_laid and (free or freev):
                bad.append({"check": "ignored-class", "net": n, "detail": "the job ignores this net's class %s and the router laid %d wire(s) and %d via(s) on it%s" % (
                    cname, len(free), len(freev), " (a class whose name holds a comma cannot be ignored by -inc)" if cname in comma else "")})
            continue
        if not free and not freev: continue
        routed_nets += 1
        allowed = set(cls.get("use_layer") or []) or {L for L, ty in d["layers"].items() if ty == "signal"}
        off = sorted({w["layer"] for w in free if w["layer"] not in allowed})
        if off: bad.append({"check": "class-layer", "net": n, "detail": "router wires on %s, which the net's class %s does not allow" % (", ".join(off), cname)})
        if cw is not None and free:
            by = {}
            for w in free:
                ln = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(w["pts"], w["pts"][1:]))
                by[round(w["width"], 4)] = by.get(round(w["width"], 4), 0.0) + ln
            wider = [x for x in by if x > cw + TOL]
            at = [x for x in by if abs(x - cw) <= TOL]
            if wider or (not at and sum(by.values()) > 1.0):
                wrong_w += 1
                if wrong_w <= 20:
                    bad.append({"check": "class-width", "net": n, "detail": "the net's class %s declares %.4f mm and the router laid %s" % (
                        cname, cw, ", ".join("%.4f mm over %.2f mm" % kv for kv in sorted(by.items())))})
        uv = set(cls.get("use_via") or []) or set(d["default_vias"])
        odd = sorted({v["padstack"] for v in freev if uv and v["padstack"] not in uv})
        if odd: bad.append({"check": "class-via", "net": n, "detail": "router vias %s, which the net's class %s does not list (%s)" % (", ".join(odd), cname, ", ".join(sorted(uv))[:120])})
    info.update(routed_nets=routed_nets, session_nets=len(s["nets"]), dsn_nets=len(d["nets"]), dsn_classes=len(d["classes"]),
                ignored_nets=len(ignored_nets))
    wn = {}
    for n in warned:
        lost = [b for b in bad if b["net"] == n and b["check"].startswith("fixed")]
        wn[n] = {"user_fixed_wires": sum(1 for w in fixed_w if w["net"] == n), "user_fixed_vias": sum(1 for v in fixed_v if v["net"] == n),
                 "system_fixed": sum(1 for x in d["wires"] + d["vias"] if x["net"] == n and _kind(x["type"]) == "fix"), "survived": not lost}
    info["warned_nets"] = wn
    return bad, info


def cmd_survive(a):
    dsn, ses = a[0], a[1]; out = _opt(a, "--json")
    ign = [x for x in (_opt(a, "--ignore-classes") or "").split(",") if x]
    warned = [x for x in (_opt(a, "--warned-nets") or "").split(",") if x]
    rec = {"tool": "fr_import_check survive", "dsn": dsn, "ses": ses, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    try:
        t0 = time.time(); d = read_dsn(dsn); s = read_ses(ses)
    except Exception as e:
        rec.update(decision="UNREADABLE", reasons=["%s: %s" % (type(e).__name__, e)]); _write(out, rec)
        print("fr_import_check: survive: UNREADABLE: %s" % rec["reasons"][0]); return 2
    bad, info = survive(d, s, ign, warned)
    rec.update(info, findings=bad, decision="SURVIVED" if not bad else "LOST", seconds=round(time.time() - t0, 2))
    _write(out, rec)
    if bad:
        print("fr_import_check: survive: LOST: %d finding(s): %s" % (len(bad), "; ".join("%s %s: %s" % (b["check"], b["net"] or "", b["detail"]) for b in bad[:3])))
        return 3
    print("fr_import_check: survive: nothing declared was lost: %d user-fixed wire(s) and %d via(s) of the DSN on the session's protected "
          "copper, %d routed net(s) at their class width, layers and vias, %d session net(s) all declared (%.1f s)%s" % (
              info["dsn_user_fixed_wires"], info["dsn_user_fixed_vias"], info["routed_nets"], info["session_nets"], rec["seconds"],
              ("; NOT ignored by -inc because their names hold a comma: " + ", ".join(info["comma_classes_not_ignorable"])) if info["comma_classes_not_ignorable"] else ""))
    return 0


# ---------------------------------------------------------------------------------------------------- import
def _cover_index(items):
    """(net, layer) -> 1 mm cell -> segments, for a coverage test that does not scan the whole board per point."""
    grid = {}
    for w in items:
        g = grid.setdefault((w["net"], w["layer"]), {})
        for a, b in zip(w["pts"], w["pts"][1:]):
            for cx in range(int(math.floor(min(a[0], b[0]))), int(math.floor(max(a[0], b[0]))) + 1):
                for cy in range(int(math.floor(min(a[1], b[1]))), int(math.floor(max(a[1], b[1]))) + 1):
                    g.setdefault((cx, cy), []).append((a, b, w))
    return grid


def _on(grid, net, layer, p):
    """The wires of (net, layer) whose copper passes through point p."""
    g = grid.get((net, layer), {}); hit = []
    cx, cy = int(math.floor(p[0])), int(math.floor(p[1]))
    for i in (-1, 0, 1):
        for j in (-1, 0, 1):
            for a, b, w in g.get((cx + i, cy + j), []):
                if _seg_dist(p, a, b) <= TOL: hit.append(w)
    return hit


def compare_import(d, p):
    """Findings of the board Freerouting holds after the import (its own DSN export, `p`) against the DSN it read (`d`).
    Each finding is {check, what, detail}. What is compared, and why each is a loss and not a difference of dialect:
      layers      every layer with its type (a power layer that came back signal is a plane the router may route over)
      nets        every net with exactly its pins (a pin that did not come back is a connection nobody will route)
      classes     every class with its nets, its width, its clearance (as the class's own clearance class, which
                  1.9.0 writes for every named class but the last, Rule.java write_named_clearance_rules), its layers
                  (use_layer; none declared means every signal layer) and its via padstacks (use_via, written back
                  as a via rule)
      keep-outs   the count per kind and layer, and the planes per net and layer
      wiring      every wire's copper (corners and mid-points) on a wire of the same net and layer with the same fixed
                  state, and every via at its place with its padstack, net and fixed state. Normalisation may split
                  and merge wires, so this is a coverage test and not a count."""
    bad = []
    def f(check, what, detail):
        bad.append({"check": check, "what": what, "detail": detail})
    for x in d.get("lint", []): f("structure", None, x)
    for L, ty in d["layers"].items():
        if L not in p["layers"]: f("layer", L, "the layer did not come back")
        elif p["layers"][L] != ty: f("layer", L, "declared %s, holds %s" % (ty, p["layers"][L]))
    for n, pins in d["nets"].items():
        if n not in p["nets"]:
            if pins: f("net", n, "the net (%d pins) did not come back" % len(pins))
            continue
        miss = sorted(pins - p["nets"][n])
        if miss: f("net-pins", n, "%d pin(s) did not come back: %s" % (len(miss), ", ".join(miss[:6])))
    sig = sorted(L for L, ty in d["layers"].items() if ty == "signal")
    unwritten_clear = []
    for c, cd in d["classes"].items():
        pc = p["classes"].get(c)
        if pc is None: f("class", c, "the class did not come back"); continue
        miss = sorted(set(cd["nets"]) - set(pc["nets"]))
        if miss: f("class-nets", c, "%d net(s) left the class: %s" % (len(miss), ", ".join(miss[:6])))
        if cd["width"] is not None and (pc["width"] is None or abs(pc["width"] - cd["width"]) > TOL):
            f("class-width", c, "declared %.4f mm, holds %s" % (cd["width"], "none" if pc["width"] is None else "%.4f mm" % pc["width"]))
        want = sorted(cd["use_layer"]) if cd["use_layer"] else sig
        have = sorted(pc["use_layer"]) if pc["use_layer"] else sig
        if want != have: f("class-layers", c, "declared %s, holds %s" % (" ".join(want), " ".join(have)))
        wv = set(cd["use_via"]) or set(d["default_vias"]); hv = set(pc["use_via"])
        if hv and wv != hv: f("class-vias", c, "declared %s, holds %s" % (", ".join(sorted(wv)), ", ".join(sorted(hv))))
        if cd["clearance"] is not None:
            cc = pc.get("clearance_class") or c
            if cc in p["named_clearance"]:
                if abs(p["named_clearance"][cc] - cd["clearance"]) > TOL:
                    f("class-clearance", c, "declared %.4f mm, holds %.4f mm" % (cd["clearance"], p["named_clearance"][cc]))
            else: unwritten_clear.append(c)
    for key, n in d["keepouts"].items():
        if p["keepouts"].get(key, 0) < n: f("keepout", "%s on %s" % key, "declared %d, holds %d" % (n, p["keepouts"].get(key, 0)))
    for key, n in d["planes"].items():
        if p["planes"].get(key, 0) < n: f("plane", "%s on %s" % key, "declared %d, holds %d" % (n, p["planes"].get(key, 0)))
    grid = _cover_index(p["wires"]); lost = 0; kind_changed = 0; in_pad = 0; vpad = _pad_index(d)
    for w in d["wires"]:
        want = _kind(w["type"]); gone = False; changed = False
        for pt in _probe_points(w["pts"]):
            hit = _on(grid, w["net"], w["layer"], pt)
            if not hit:
                if _in_pad(vpad, w["net"], w["layer"], pt, w["width"]): in_pad += 1; continue   # a shortened spike (_in_pad)
                gone = True; break
            if not any(_kind(h["type"]) == want for h in hit): changed = True
        if gone:
            lost += 1
            if lost <= 20: f("wire", w["net"], "a %s %s wire from (%.3f, %.3f) did not come back" % (want, w["layer"], w["pts"][0][0], w["pts"][0][1]))
        elif changed:
            kind_changed += 1
            if kind_changed <= 20: f("wire-fixed", w["net"], "a %s %s wire from (%.3f, %.3f) came back with another fixed state" % (want, w["layer"], w["pts"][0][0], w["pts"][0][1]))
    pv = {}
    for v in p["vias"]:
        pv.setdefault((v["net"], v["padstack"], int(math.floor(v["x"] * 100)), int(math.floor(v["y"] * 100))), []).append(v)
    vlost = 0
    for v in d["vias"]:
        cx, cy = int(math.floor(v["x"] * 100)), int(math.floor(v["y"] * 100))
        hits = [h for i in (-1, 0, 1) for j in (-1, 0, 1) for h in pv.get((v["net"], v["padstack"], cx + i, cy + j), [])
                if abs(h["x"] - v["x"]) <= TOL and abs(h["y"] - v["y"]) <= TOL]
        if not hits or not any(_kind(h["type"]) == _kind(v["type"]) for h in hits):
            vlost += 1
            if vlost <= 20: f("via", v["net"], "a %s via %s at (%.3f, %.3f) did not come back%s" % (_kind(v["type"]), v["padstack"], v["x"], v["y"], "" if not hits else " with its fixed state"))
    if lost > 20 or vlost > 20 or kind_changed > 20:
        f("wiring", None, "in all %d wire(s) lost, %d wire(s) with another fixed state, %d via(s) lost" % (lost, kind_changed, vlost))
    info = {"layers": len(d["layers"]), "nets": len(d["nets"]), "pins": sum(len(x) for x in d["nets"].values()),
            "classes": len(d["classes"]), "class_pairs_not_compared": d["class_pairs"],
            "clearance_not_written_back": unwritten_clear, "keepouts": sum(d["keepouts"].values()),
            "planes": sum(d["planes"].values()), "wires": len(d["wires"]), "vias": len(d["vias"]),
            "wires_lost": lost, "wires_fixed_state_changed": kind_changed, "vias_lost": vlost,
            "points_inside_same_net_via_pad": in_pad}
    return bad, info


def cmd_import(a):
    dsn, back = a[0], a[1]; out = _opt(a, "--json")
    rec = {"tool": "fr_import_check import", "dsn": dsn, "written_back": back, "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    try:
        t0 = time.time(); d = read_dsn(dsn); p = read_dsn(back)
    except Exception as e:
        rec.update(decision="UNREADABLE", reasons=["%s: %s" % (type(e).__name__, e)]); _write(out, rec)
        print("fr_import_check: import: UNREADABLE: %s" % rec["reasons"][0]); return 2
    bad, info = compare_import(d, p)
    rec.update(info, findings=bad, decision="SURVIVED" if not bad else "LOST", seconds=round(time.time() - t0, 2))
    _write(out, rec)
    if bad:
        print("fr_import_check: import: LOST: %d finding(s): %s" % (len(bad), "; ".join("%s %s: %s" % (b["check"], b["what"] or "", b["detail"]) for b in bad[:4])))
        return 3
    print("fr_import_check: import: the router holds what the DSN declares: %d layer(s), %d net(s) with %d pin(s), %d class(es) with "
          "their widths, clearances, layers and vias, %d keep-out(s), %d plane(s), %d wire(s) and %d via(s) with their fixed state "
          "(%.1f s)%s" % (info["layers"], info["nets"], info["pins"], info["classes"], info["keepouts"], info["planes"], info["wires"],
                          info["vias"], rec["seconds"],
                          ("; not compared: %d class-pair rule(s), which 1.9.0 does not write back" % info["class_pairs_not_compared"]) if info["class_pairs_not_compared"] else ""))
    return 0


# ---------------------------------------------------------------------------------------------------- timing
def _t(ts):
    return time.mktime(time.strptime(ts[:19], "%Y-%m-%d %H:%M:%S")) + float(ts[19:]) if ts else None


def cmd_timing(a):
    log = a[0]; ev = _opt(a, "--events"); out = _opt(a, "--json"); label = _opt(a, "--label") or "router"
    entries = read_log(log) or []
    def first(pred):
        for e in entries:
            if e["level"] != "RAW" and pred(e["msg"]): return e["ts"]
        return None
    def last(pred):
        r = None
        for e in entries:
            if e["level"] != "RAW" and pred(e["msg"]): r = e["ts"]
        return r
    jvm = entries[0]["ts"] if entries and entries[0]["ts"] else None
    opened = first(lambda m: m.startswith("Opening '"))
    started = first(lambda m: m.startswith("Starting auto-routing"))
    passes = [e for e in entries if e["level"] == "INFO" and e["msg"].startswith("MeshSat: session written after pass")]
    auto_done = first(lambda m: m.startswith("Auto-routing was completed"))
    opt_start = first(lambda m: m.startswith("Starting route optimization"))
    opt_done = first(lambda m: m.startswith("Route optimization was completed"))
    # the last line logged before the import ended: the moment a dialog (if any) went up
    import_last = None
    for e in entries:
        if e["ts"] and opened and _t(e["ts"]) >= _t(opened):
            if started and _t(e["ts"]) >= _t(started): break
            if not e["msg"].startswith(IMPORT_END): import_last = e["ts"]
    events = []
    if ev and os.path.exists(ev):
        for ln in open(ev, errors="replace"):
            try: events.append(json.loads(ln))
            except ValueError: pass
    dialogs = [e for e in events if e.get("event") in ("dialog-dismissed", "dialog-refused", "dialog-stuck", "window-refused")]
    # blocked = from the moment the dialog went up (the last line the import logged before it, in the box's own clock,
    # which is the clock the watcher's wall times are in) to its dismissal; the watcher's own figure is the time from
    # SEEING it, which misses up to one poll
    blocked = 0.0
    for e in dialogs:
        at = e.get("answered_wall") or e.get("wall")                  # the key press that closed it, else the event
        if e.get("event") == "dialog-dismissed" and import_last and at:
            e["blocked_from_log_s"] = round(float(at) - _t(import_last), 1); blocked += max(0.0, e["blocked_from_log_s"])
        else: blocked += float(e.get("blocked_s", 0) or 0)
    end_ev = [e for e in events if e.get("event") == "end"]
    end_wall = end_ev[-1].get("wall") if end_ev else None
    start_ev = [e for e in events if e.get("event") == "start"]
    t_start_wall = start_ev[0].get("wall") if start_ev else None
    def d(a_, b_): return round(_t(b_) - _t(a_), 1) if a_ and b_ else None
    last_ts = entries[-1]["ts"] if entries and entries[-1]["ts"] else None
    for e in reversed(entries):
        if e["ts"]: last_ts = e["ts"]; break
    # errors logged while routing raise no dialog (only import_design shows one); they are recorded, once each (log4j
    # writes an ERROR to both of its console appenders, and both reach the one log), and the routed board is judged
    # by KiCad afterwards. Board B, 26 September 2026: "The normalization of net '/PCIE3_CLK_N' failed" from
    # InsertFoundConnectionAlgo.java:83 while the router kept routing.
    rerr = []
    if started:
        seen = set()
        for e in entries:
            if e["level"] in ("ERROR", "FATAL") and e["ts"] and _t(e["ts"]) >= _t(started) and (e["ts"], e["msg"]) not in seen:
                seen.add((e["ts"], e["msg"])); rerr.append("%s %s" % (e["ts"], e["msg"]))
    rec = {"label": label, "log": log, "routing_errors": len(rerr), "routing_error_lines": rerr[:50],
           "jvm_to_open_s": d(jvm, opened),
           "input_load_s": d(opened, import_last) if import_last else None,
           "import_to_routing_s": d(import_last, started) if import_last else None,
           "blocked_on_dialog_s": round(blocked, 1), "dialogs": dialogs,
           "active_routing_s": d(started, auto_done or (passes[-1]["ts"] if passes else last_ts)) if started else None,
           "routing_finished": bool(auto_done), "passes": len(passes),
           "pass_times": [e["ts"] for e in passes][:400],
           "optimiser_s": d(opt_start, opt_done or last_ts) if opt_start else None,
           "wall_s": round(end_wall - t_start_wall, 1) if (end_wall and t_start_wall) else None,
           "decision": next((e.get("decision") for e in reversed(events) if e.get("decision")), None),
           "events": events}
    _write(out, rec)
    f = lambda v: "-" if v is None else ("%.1f s" % v)
    print("fr_stage %s: JVM start %s, input load %s, blocked on a dialog %s (%d), import end to routing %s, active routing %s "
          "over %d pass(es)%s, optimiser %s, wall %s%s" % (
              label, f(rec["jvm_to_open_s"]), f(rec["input_load_s"]), f(rec["blocked_on_dialog_s"]), len(dialogs),
              f(rec["import_to_routing_s"]), f(rec["active_routing_s"]), rec["passes"],
              ("" if rec["routing_finished"] else " (not finished)") + (", %d error line(s) while routing" % rec["routing_errors"] if rec["routing_errors"] else ""),
              f(rec["optimiser_s"]), f(rec["wall_s"]),
              (", decision " + rec["decision"]) if rec["decision"] else ""))
    return 0


PROBE_SETTINGS = "(autoroute_settings (fanout off) (autoroute off) (postroute off))"


def _scope_end(text, start):
    """Index of the ')' closing the scope that opens at text[start] == '(' (quoted strings skipped; the parser scope's
    bare '"' in (string_quote ") is not a string)."""
    depth = 0; i = start; n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            if re.match(r'"\s*\)', text[i:i + 4]) and re.search(r"\(string_quote\s*$", text[max(0, i - 20):i]): i += 1; continue
            j = text.find('"', i + 1); i = (j if j >= 0 else n) + 1; continue
        if c == "(": depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0: return i
        i += 1
    return -1


def _children(text, start):
    """The direct child scopes of the scope opening at text[start], as (keyword, begin, end) with end the index of the
    child's closing bracket."""
    out = []; e = _scope_end(text, start); i = start + 1
    while i < e:
        if text[i] == "(":
            ce = _scope_end(text, i)
            if ce < 0: break
            m = re.match(r"\(\s*([^\s()]+)", text[i:i + 80])
            out.append((m.group(1) if m else "", i, ce)); i = ce + 1; continue
        if text[i] == '"':
            j = text.find('"', i + 1); i = (j if j >= 0 else e) + 1; continue
        i += 1
    return out


AREA_FIRST = ("keepout", "via_keepout", "place_keepout", "plane")


def structure_lint(text):
    """What 1.9.0's Structure.read_scope (designforms/specctra/Structure.java:891-896) does with an autoroute_settings
    scope: it reads it ONLY while no keepout, via_keepout, place_keepout or plane has been read (they create the layer
    structure it tests for). Otherwise the scope is neither read nor skipped: its entries are skipped one by one as
    unknown scopes, its closing bracket ends the STRUCTURE, and the structure's own bracket then ends the whole PCB
    scope, so placement, library, network and wiring are never read. There is no warning; the router routes an empty
    board. Measured on the box on 26 September 2026 with this tool's first probe copy of board E5, which put the block
    at the end of the structure: the jar imported without a word and its export failed on "board.library.packages is
    null". Returns (findings, position to insert a block at, the existing block's span or None)."""
    m = re.search(r"\(structure\b", text)
    if not m: return ["the DSN has no structure scope"], None, None
    kids_ = _children(text, m.start()); bad = []; seen_area = None; block = None
    for kw, b, e in kids_:
        if kw in AREA_FIRST and seen_area is None: seen_area = kw
        if kw == "autoroute_settings":
            if seen_area: bad.append("an autoroute_settings scope follows a %s in the structure: 1.9.0 does not read it, and its closing "
                                     "bracket ends the structure, so placement, library, network and wiring are silently dropped" % seen_area)
            if block is None: block = (b, e)
    first_other = next((b for kw, b, e in kids_ if kw != "layer"), None)
    return bad, first_other, block


def cmd_probe_dsn(a):
    """probe-dsn <in.dsn> <out.dsn>: the DSN with its settings turned to autoroute off (BatchAutorouterThread then skips
    autoroute_passes) and postroute off (it skips the optimiser): the job imports, routes nothing, and writes back the
    board it holds through -do. An existing autoroute_settings scope is replaced in place; otherwise one is written
    directly after the layers, the only place 1.9.0 is sure to read it (structure_lint). Exit 3 when the DSN itself
    carries a settings scope 1.9.0 would not read: that DSN loses everything after its structure, and a probe that
    repaired it would confirm a board the real run never sees."""
    src, dst = a[0], a[1]
    text = open(src, errors="replace").read()
    bad, at, block = structure_lint(text)
    if bad:
        print("fr_import_check: probe-dsn: LOST: %s" % "; ".join(bad)); return 3
    if at is None and block is None: print("fr_import_check: probe-dsn: no place in the structure for the settings"); return 2
    if block: out = text[:block[0]] + PROBE_SETTINGS + text[block[1] + 1:]
    else: out = text[:at] + PROBE_SETTINGS + "\n    " + text[at:]
    with open(dst, "w") as f: f.write(out)
    return 0


def cmd_probe_rules(a):
    """probe-rules <in.rules> <out.rules>: a Freerouting rules file (-dr) with every autoroute_settings scope set to
    autoroute off and postroute off, and nothing else changed. RulesFile.read runs after the DSN is imported and
    AutorouteSettings.read_scope takes autoroute and postroute as ON unless a scope says otherwise."""
    src, dst = a[0], a[1]
    text = open(src, errors="replace").read(); out = []; i = 0; n = 0
    while True:
        j = text.find("(autoroute_settings", i)
        if j < 0: out.append(text[i:]); break
        e = _scope_end(text, j)
        if e < 0: print("fr_import_check: probe-rules: an autoroute_settings scope of %s does not close" % src); return 2
        blk = text[j:e]
        for kw in ("autoroute", "postroute"):
            blk, k = re.subn(r"\(%s\s+(on|off)\s*\)" % kw, "(%s off)" % kw, blk)
            if not k: blk += " (%s off)" % kw
        out.append(text[i:j]); out.append(blk + ")"); i = e + 1; n += 1
    with open(dst, "w") as f: f.write("".join(out))
    return 0


def cmd_event(a):
    path = a[0]; rec = {}
    for kv in a[1:]:
        k, _, v = kv.partition("=")
        try: rec[k] = json.loads(v) if v[:1] in "[{0123456789-" or v in ("true", "false", "null") else v
        except ValueError: rec[k] = v
    rec.setdefault("wall", time.time()); rec.setdefault("at", time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    with open(path, "a") as f: f.write(json.dumps(rec, sort_keys=True) + "\n")
    return 0


def _opt(a, name):
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else None


def _write(path, rec):
    if not path: return
    tmp = path + ".part"
    with open(tmp, "w") as f: json.dump(rec, f, indent=1, sort_keys=True)
    os.replace(tmp, path)


def main(argv):
    cmds = {"classify": cmd_classify, "import": cmd_import, "survive": cmd_survive, "timing": cmd_timing, "event": cmd_event,
            "probe-dsn": cmd_probe_dsn, "probe-rules": cmd_probe_rules}
    if len(argv) < 2 or argv[1] not in cmds:
        print(__doc__.split("\n\n")[0]); print("usage: %s ..." % "|".join(cmds)); return 2
    return cmds[argv[1]](argv[2:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
