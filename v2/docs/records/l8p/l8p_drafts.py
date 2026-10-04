#!/usr/bin/env python3
"""l8p_drafts.py: Layer 8 record l8p, W4DP-F2's breaker drafted for boards P, E and A, proved on scratch copies (MESHSAT-1357,
4 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the generators and the engine, every other draft it composes with, record l9stk's copies
     of 2c8b29fb, the committed netlists, the dock lands, the LM5069 sheet, this record's own files);
  2. the values: each value the drafts draw found in record l9stk's own text by its section (refused when a pattern no longer
     matches), and this record's SESSION choices;
  3. each draft on a scratch copy: checked, applied once, refused twice, and refused on the tree's own generator (NOT RELEASED);
  4. the composition of each board in L4-E9's change-list order with this record's draft inserted, then this record's draft
     first, and every other draft alone after this record's (their anchors still apply);
  5. the designators each draft adds, pairwise disjoint, and every literal part call drawn once in the composed generators;
  6. the regeneration on the runner (gen_netlist.py: the generator's own part table, no KiCad): the unpatched generators
     reproduce the committed KiCad netlists pin for pin; the netlist check (check_l8p_netlist.py) on the committed netlists
     (NOT DRAWN), on the three boards with this record's drafts alone and composed in L4-E9's order (DRAWN), and on two mutated
     netlists (FAIL);
  7. the declarations the patched board P generator writes into its intent for the new nets.
Run from the repository root:  python3 v2/docs/records/l8p/l8p_drafts.py  (l8p_drafts.out is its output, regenerated with
_bin/regen_out.py). Nothing here is built or measured: every statement is about generator text, netlists and record text."""
import ast
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import check_l8p_netlist as CHK  # noqa: E402
import gen_netlist as GN  # noqa: E402

GEN = {b: os.path.join(TOOLS, "gen_sch_%s.py" % b) for b in "pea"}
NET = {b: os.path.join(ROOT, p) for b, p in CHK.COMMITTED.items()}
PROJECT = {"p": "pcb-p-pack", "e": "pcb-e1-dock", "a": "pcb-a-power"}
MINE = {"p": os.path.join(HERE, "apply_gen_sch_p_breaker.py"), "e": os.path.join(HERE, "apply_gen_sch_e_enable.py"),
        "a": os.path.join(HERE, "apply_gen_sch_a_ptc.py")}
# L4-E9's change list (records/l4e9/L4-POWER-ARCHITECTURE.md section 3) for each board's round, in application order; d8dec31's
# drafts take the board's committed netlist as their second argument; Layer 6's l6r2 drafts are order-independent tables
ORDER = {
    "p": [("l6r2", "intent"), ("l6r2", "lcsc")],
    "e": [("l4e9", "q1"), ("l4e7", "u5_grade"), ("l4e7", "hold"), ("l4e7", "input_limit"), ("l4e7", "backstop"), ("l4e9", "f1"),
          ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin"), ("l6r2", "xal_land"),
          ("l6r2", "lcsc")],
    "a": [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
          ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "d8v3"), ("l8r2", "vbus20ov"), ("d8dec31", "mainpb"), ("l6r2", "lcsc")],
}
# where this record's draft goes in the forward order: after the board's circuit drafts, before the last-taker and the tables
SLOT = {"p": 0, "e": 10, "a": 11}
INPUT_FILES = {"page": "inputs/l9stk-section15-2c8b29fb.md", "out": "inputs/l9stk_protection-2c8b29fb.out.txt",
               "constants": "inputs/l9stk_protection-constants-2c8b29fb.txt"}
SOURCES_SHA = {"inputs/l9stk-section15-2c8b29fb.md": "4cfd6733c7d2e0429d9fc8ad18a71d4996e0d280b1c5b40f5ef31372e52ed3e2",
               "inputs/l9stk_protection-2c8b29fb.out.txt": "ca434347df8b322da9185412d84c10d1848697710aee99e0709e19850430e7f1",
               "inputs/l9stk_protection-constants-2c8b29fb.txt": "58bd120aa8ad01ca7faa4053d4fd9b98beac65c5ed1f58ec67bc379e4819420b"}
SESSION = [
    ("designators", "the free 100 block on board P (U101, Q101 to Q104, D101, R101 to R109, C101 to C105, TP101 to TP104); RT1 on board A, which carries no RT designator"),
    ("net names", "BRK_VIN (Q2's source, the breaker's input), BRK_SNS, BRK_GATE, BRK_TMR, BRK_PWR, BRK_UVLO, BRK_G2, BRK_DIS, BRK_CMID; DOCK_EN_OUT and DOCK_EN_RET on all three boards"),
    ("J_SMB pins", "a JST-XH 1x7 at both ends: 1 to 4 unchanged, 5 DOCK_EN_RET, 6 the return (the ground between), 7 DOCK_EN_OUT at the row's end"),
    ("dock positions", "J_DOCK and J_BLK pins 3 (DOCK_EN_RET) and 5 (DOCK_EN_OUT), pin 4 ground between them; pin 5's neighbours 4, 6 and 11 are all ground"),
    ("input bypass", "C104 and C105, 2.2 uF 50 V X7R in series (1.1 uF) at the sense pair: TI SNVS452G section 10 ('a 1-uF ceramic capacitor to ground close to the drain of the hot swap MOSFET') and 11.1.1; in series as C11 and C12 are (board P's O-12)"),
    ("PGD", "left open: IF-1's PGD option would need a conductor to board A, which is L4-E11's to decide"),
    ("test points", "TP101 BRK_VIN, TP102 BRK_UVLO, TP103 DOCK_EN_OUT, TP104 DOCK_EN_RET, for E-12's commissioning steps"),
    ("lands", "the VSSOP-10, SMC and 2512 lands the kit already uses for these parts; the 7-circuit XH header of the same row; RT1 on board P's 0402"),
]


# SCRATCH STAND-INS for run-time defects of OTHER records' drafts that stop the composed generators (section 8 lists them as
# findings for their owners). Each is applied to a scratch copy only when its old text is there; none is a draft, none is applied
# anywhere else, and each says only that the generator then runs on, so this record's loop can be judged in the whole composition.
STANDINS = {
    "e": [("L8P-F01", "l4e7's backstop draft: C66, C67 and C68 carry no G14 decoupling class",
           '_DEC_RULED = ("R", "D", "L", "A", "B1", "B2")',
           'for _e in _intent._I["bypass"]: _DEC_CLASS.setdefault(_e["cap"], ("D", "record l8p scratch stand-in, not a class"))\n'
           '_DEC_RULED = ("R", "D", "L", "A", "B1", "B2")'),
          ("L8P-F03", "l4e11's aux draft: +12V_FAN names L4 as its source, which is not on that net",
           '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "L4",', '_intent.rail("+12V_FAN", 12.0, 0.34, 0.34, "C143",')],
    "a": [("L8P-F02", "l4e11's charger draft: VSYS_DOCK names U42 as its source without source_ic, and is fed from VBAT before VBAT is declared",
           '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", always_on=True, v_work=17.4, converted=False, fed_from="VBAT",',
           '_intent.rail("VSYS_DOCK", 14.4, 1.32, 1.32, "U42", source_ic="record l8p scratch stand-in", always_on=True, v_work=17.4, converted=False,')],
}


def rel(p):
    return os.path.relpath(p, ROOT)


def sha(p, n=16):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l8p_drafts: REFUSED: %s\n" % msg)
    sys.exit(2)


def draft(rec, name, board):
    return os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target, board):
    """(returncode, the last line it printed): d8dec31's drafts take the committed netlist, the others --write."""
    args = [script, target, NET[board]] if "/d8dec31/" in script.replace(os.sep, "/") else [script, target, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True)
    out = (r.stdout.decode("utf-8", "replace").strip().splitlines() or [""])[-1] if r.returncode == 0 else \
        (r.stderr.decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, out


def scrub(s, d):
    return s.replace(d, "<scratch>")


def compose(board, seq, d, tag):
    p = os.path.join(d, tag + "_gen_sch_%s.py" % board)
    shutil.copy(GEN[board], p)
    res = []
    for s in seq:
        rc, msg = run(s, p, board)
        name = os.path.relpath(s, RECS)
        res.append((name, "OK" + (" (%s)" % msg if "/d8dec31/" in s.replace(os.sep, "/") and "mainpb" in s else "") if rc == 0 else "REFUSED (%s)" % scrub(msg, d)))
        if rc:
            break
    return p, res


STMT = re.compile(r'^\s*(ic|part|c|r|tp|nfet|vh2|synth|q|esd|efuse|pfet5|ph|_tvs)\(\s*"([A-Z#][A-Z0-9_]*)"')
TOKEN = re.compile(r"\b(RT\d{1,3}|[RCDLQUHF]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3}|W_[A-Z0-9]+)\b(?!-)")


def strip_comments(s):
    return "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())


def literal_calls(text):
    out = []
    for line in strip_comments(text).splitlines():
        for stmt in line.split(";"):
            m = STMT.match(stmt)
            if m:
                out.append(m.groups())
    return out


def tokens(text):
    """Designator strings where the generator DRAWS or LISTS a part: a call's first argument, or an element of a list or tuple,
    read with ast; prose and dict keys count for nothing."""
    out = set()
    for n in ast.walk(ast.parse(text)):
        cands = []
        if isinstance(n, ast.Call) and n.args:
            cands.append(n.args[0])
        elif isinstance(n, (ast.List, ast.Tuple)):
            cands.extend(n.elts)
        for c in cands:
            if isinstance(c, ast.Constant) and isinstance(c.value, str) and TOKEN.fullmatch(c.value):
                out.add(c.value)
    return out


def declared_adds(script):
    import importlib.util
    try:
        sp = importlib.util.spec_from_file_location("adds_" + re.sub(r"\W", "_", script), script)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        return set(getattr(m, "ADDS", ()))
    except Exception:
        return set()


def added(before, after, script):
    cb = {r for _h, r in literal_calls(before)}; ca = {r for _h, r in literal_calls(after)}
    return (ca - cb) | (tokens(after) - tokens(before)) | declared_adds(script)


def _draws(node):
    """{designator: count} of the literal part calls under an ast node; the two branches of an `if _tvs:` (the generators' one
    clamp drawn either by kisch.tvs or by its fallback) are alternatives, so a designator counts once across them."""
    from collections import Counter
    if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "_tvs":
        a, b = Counter(), Counter()
        for x in node.body:
            a += _draws(x)
        for x in node.orelse:
            b += _draws(x)
        return a | b
    c = Counter()
    if isinstance(node, ast.Call) and node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
        f = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else ""
        if f in ("ic", "part", "c", "r", "tp", "nfet", "pfet5", "ph", "q", "esd", "efuse", "synth", "vh2", "_tvs", "tvs") and TOKEN.fullmatch(node.args[0].value):
            c[node.args[0].value] += 1
    for ch in ast.iter_child_nodes(node):
        c += _draws(ch)
    return c


def duplicates(text):
    return sorted(r for r, n in _draws(ast.parse(text)).items() if n > 1)


def pins_of(nl):
    return {(r, p): n for r, d in nl["pins"].items() for p, n in d.items()}


def netlist_text(board, generator, d, tag):
    """(rc, netlist path or the generator's last line, table)."""
    out = os.path.join(d, "%s_%s.net" % (tag, board))
    rc, log, table = GN.run(generator, out, PROJECT[board])
    if rc:
        return rc, scrub((log.strip().splitlines() or [""])[-1], d), None
    return 0, out, table


def mutate(path, d, tag, swaps):
    """A copy of a netlist with the nets of two (ref, pin) nodes exchanged."""
    raw = open(path, encoding="utf-8").read()
    for (ra, pa), (rb, pb) in swaps:
        a = '(node (ref "%s") (pin "%s"))' % (ra, pa); b = '(node (ref "%s") (pin "%s"))' % (rb, pb)
        if raw.count(a) != 1 or raw.count(b) != 1:
            refuse("the mutation's nodes are not in the netlist once: %s %s" % (a, b))
        raw = raw.replace(a, "\0A").replace(b, a).replace("\0A", b)
    p = os.path.join(d, tag + ".net")
    open(p, "w", encoding="utf-8").write(raw)
    return p


def main():
    w = sys.stdout.write
    w("l8p_drafts: Layer 8 record l8p, W4DP-F2's breaker and its make-last dock enable loop drafted for boards P, E and A (MESHSAT-1357)\n")
    w("prototype design; nothing built, bought or measured; nothing applied to the tree; the values are record l9stk's (fnd/l9stk at 2c8b29fb)\n\n")
    # 1. inputs
    others = [draft(r, n, b) for b in "pea" for r, n in ORDER[b]]
    inputs = [GEN["p"], GEN["e"], GEN["a"], os.path.join(TOOLS, "kisch.py"), os.path.join(TOOLS, "intent.py"), os.path.join(TOOLS, "idc_pads.py")]
    inputs += others + [NET["p"], NET["e"], NET["a"]]
    inputs += [os.path.join(HERE, f) for f in sorted(SOURCES_SHA)] + [os.path.join(HERE, "inputs", "SOURCES.txt")]
    inputs += [os.path.join(CHK.PRETTY, l + ".kicad_mod") for l in sorted(set(CHK.LANDS.values()))]
    inputs += [os.path.join(ROOT, "v2", "vendor", "ti", "ti-lm5069.pdf")]
    inputs += [MINE["p"], MINE["e"], MINE["a"], os.path.join(HERE, "check_l8p_netlist.py"), os.path.join(HERE, "gen_netlist.py")]
    w("1. INPUTS, pinned by sha256\n")
    for p in inputs:
        if not os.path.isfile(p):
            refuse("input %s is missing" % rel(p))
        w("   %s %s\n" % (sha(p), rel(p)))
    for f, full in sorted(SOURCES_SHA.items()):
        if sha(os.path.join(HERE, f), 64) != full:
            refuse("the copy %s is not the file SOURCES.txt pins" % f)
    w("   record l9stk's copies equal the sha256 SOURCES.txt pins: yes\n\n")
    # 2. the values
    texts = {k: open(os.path.join(HERE, v), encoding="utf-8").read() for k, v in INPUT_FILES.items()}
    w("2. THE VALUES, each found in record l9stk's own text (fnd/l9stk at 2c8b29fb), and this record's SESSION choices\n")
    for b, ref, pre, src, pat, key in CHK.VALUES:
        if not re.search(pat, texts[key]):
            refuse("record l9stk no longer reads the %s value (%s)" % (ref, src))
        w("   %s %-5s %-16s l9stk %s\n" % (b.upper(), ref, pre, src))
    for pat, what in ((r"\*\*IF-6\*\* the gauge's PACK and VCC taps stay on Q2's source node, and the clamp and the controller return to PACK_N", "IF-6"),
                      (r"OVLO to ground", "the controller row: OVLO to ground"),
                      (r"a ground contact between them in J_SMB and on the block", "condition C2: the ground between, in J_SMB and on the block"),
                      (r"crosses the dock on two contacts 1 mm short of the power pins", "C-1b: two contacts 1 mm short (Layer 7's)"),
                      (r"its designator L4-E11's", "15.5: the third battery FET's designator is L4-E11's"),
                      (r"In the enable loop on the battery FETs' copper", "15.5: the PTC on the battery FETs' copper (board A)")):
        if not re.search(pat, texts["page"]):
            refuse("record l9stk no longer reads %s" % what)
        w("   l9stk reads: %s\n" % what)
    if not re.search(r"R_E1, R_E2 = 10e3, 22e3", texts["constants"]) or not re.search(r"R_DIS = 150\.0", texts["constants"]) \
            or not re.search(r"R_U = 200e3", texts["constants"]):
        refuse("l9stk_protection.py's constants no longer read R_E1, R_E2, R_DIS and R_U as the page states them")
    w("   l9stk_protection.py's constants agree with the page: R_E1 10 kOhm, R_E2 22 kOhm, R_DIS 150 ohm, R_U 200 kOhm; R_G 1 MOhm\n")
    for k, v in SESSION:
        w("   SESSION %-15s %s\n" % (k, v))
    w("\n")
    with tempfile.TemporaryDirectory(prefix="l8p_") as d:
        # 3. each draft alone
        w("3. EACH DRAFT ON A SCRATCH COPY (check, apply once, refuse twice, refuse the tree's own generator)\n")
        before = {b: sha(GEN[b], 64) for b in "pea"}
        for b in "pea":
            s = MINE[b]
            t = os.path.join(d, "alone_gen_sch_%s.py" % b); shutil.copy(GEN[b], t); pre = sha(t, 64)
            r1 = subprocess.run([sys.executable, "-B", s, t], capture_output=True)
            ok1 = r1.returncode == 0 and b"CHECK OK" in r1.stdout and sha(t, 64) == pre
            r2 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            ok2 = r2.returncode == 0 and b"WRITTEN" in r2.stdout
            r3 = subprocess.run([sys.executable, "-B", s, t, "--write"], capture_output=True)
            r4 = subprocess.run([sys.executable, "-B", s, GEN[b], "--write"], capture_output=True)
            w("   %s: check %s; applied %s; second application %s; the tree's gen_sch_%s.py %s\n" % (
                os.path.basename(s), "OK" if ok1 else "FAILED", "OK" if ok2 else "FAILED",
                "refused" if r3.returncode == 3 else "NOT REFUSED", b, "refused (NOT RELEASED)" if r4.returncode == 3 and b"NOT RELEASED" in r4.stderr else "NOT REFUSED"))
        if any(sha(GEN[b], 64) != before[b] for b in "pea"):
            refuse("a draft wrote into the tree")
        w("   the tree's generators are unchanged: yes\n\n")
        # 4. composition
        w("4. COMPOSITION IN L4-E9'S CHANGE-LIST ORDER (records/l4e9/L4-POWER-ARCHITECTURE.md section 3)\n")
        composed = {}
        for b in "pea":
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            fwd = seq[:SLOT[b]] + [MINE[b]] + seq[SLOT[b]:]
            p, res = compose(b, fwd, d, "fwd")
            composed[b] = p if all(v.startswith("OK") for _s, v in res) and len(res) == len(fwd) else None
            w("   board %s, this record's draft in its place:\n" % b.upper())
            for s, v in res:
                w("     %-44s %s\n" % (s, v))
            _p, res = compose(b, [MINE[b]] + seq, d, "rev")
            w("   board %s, this record's draft first, then the order: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1
                                                                      else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
            _p, res = compose(b, seq + [MINE[b]], d, "last")
            w("   board %s, the order, then this record's draft last: %s\n" % (b.upper(), "every step OK" if all(v.startswith("OK") for _s, v in res) and len(res) == len(seq) + 1
                                                                       else "; ".join("%s %s" % x for x in res if not x[1].startswith("OK"))))
        w("\n")
        # 5. designators
        w("5. DESIGNATORS EACH DRAFT ADDS (the forward order; part calls, listed tokens and each draft's declared ADDS)\n")
        for b in "pea":
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            fwd = seq[:SLOT[b]] + [MINE[b]] + seq[SLOT[b]:]
            p = os.path.join(d, "desig_gen_sch_%s.py" % b); shutil.copy(GEN[b], p)
            before_t = open(p, encoding="utf-8").read(); adds = {}
            for s in fwd:
                if run(s, p, b)[0] != 0:
                    break
                after_t = open(p, encoding="utf-8").read()
                adds[os.path.relpath(s, RECS)] = added(before_t, after_t, s)
                before_t = after_t
            mine = adds.get(os.path.relpath(MINE[b], RECS), set())
            w("   board %s, this record's: %s\n" % (b.upper(), ", ".join(sorted(mine, key=lambda x: (re.sub(r"\d", "", x), int(re.sub(r"\D", "", x) or 0)))) or "none (nets only)"))
            meets = {k: sorted(v & mine) for k, v in adds.items() if k != os.path.relpath(MINE[b], RECS) and v & mine}
            w("   board %s, this record's against every other draft's: %s\n" % (b.upper(), "DISJOINT" if not meets else "MEETS %s" % meets))
            dup = duplicates(before_t)
            w("   board %s, literal part calls drawn twice in the composed generator: %s\n" % (b.upper(), ", ".join(dup) if dup else "none"))
        w("\n")
        # 6. regeneration and the netlist check
        w("6. REGENERATION ON THE RUNNER (gen_netlist.py: the generator's own part table, no KiCad) AND THE NETLIST CHECK\n")
        for b in "pea":
            rc, path, _t = netlist_text(b, GEN[b], d, "base")
            if rc:
                refuse("board %s's own generator did not run: %s" % (b, path))
            a, k = CHK.read_netlist(open(path, "rb").read()), CHK.read_netlist(open(NET[b], "rb").read())
            pa, pk = pins_of(a), pins_of(k)
            diff = [x for x in sorted(set(pa) | set(pk)) if pa.get(x) != pk.get(x)]
            nc = [x for x in diff if pa.get(x) is None and str(pk.get(x)).startswith("unconnected-")]
            fpd = [r for r in sorted(set(a["comps"]) | set(k["comps"])) if a["comps"].get(r, {}).get("footprint") != k["comps"].get(r, {}).get("footprint")]
            w("   board %s unpatched: %d connected pins against the committed KiCad netlist's %d; differences %d, all KiCad's names for "
              "open pins: %s; footprints differing: %d\n" % (b.upper(), len(pa), len(pk), len(diff), "yes" if len(nc) == len(diff) else "NO", len(fpd)))
        w("   the netlist check on the committed netlists:\n")
        buf = io.StringIO(); kit, _v = CHK.run(NET, ROOT, buf)
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        alone = {}
        for b in "pea":
            t = os.path.join(d, "regen_gen_sch_%s.py" % b); shutil.copy(GEN[b], t)
            if run(MINE[b], t, b)[0] != 0:
                refuse("this record's board %s draft refused a clean copy" % b)
            rc, path, table = netlist_text(b, t, d, "mine")
            if rc:
                refuse("board %s's generator with this record's draft did not run: %s" % (b, path))
            alone[b] = (path, table)
            w("   board %s with this record's draft alone: the generator ran to its end (%d parts, %d unplaced, intent written: %s)\n"
              % (b.upper(), len(table["parts"]), len(table["unplaced"]), "yes" if table["intent_written"] else "NO"))
        buf = io.StringIO(); CHK.run({b: alone[b][0] for b in "pea"}, ROOT, buf, label=lambda x: "regenerated board %s, this record's draft alone" % x.upper())
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        comp = {}
        for b in "pea":
            if not composed[b]:
                w("   board %s composed in L4-E9's order: the composition refused (section 4), not regenerated\n" % b.upper())
                continue
            rc, path, table = netlist_text(b, composed[b], d, "composed")
            if rc == 0:
                comp[b] = path
                w("   board %s composed in L4-E9's order: the generator ran to its end (%d parts, intent written: %s)\n"
                  % (b.upper(), len(table["parts"]), "yes" if table["intent_written"] else "NO"))
                continue
            w("   board %s composed in L4-E9's order: the generator refused: %s\n" % (b.upper(), path))
            # the same composition without this record's draft: the refusal is the other drafts' (a finding for their owners)
            seq = [draft(r, n, b) for r, n in ORDER[b]]
            q, res = compose(b, seq, d, "without")
            rc2, line2, _t2 = netlist_text(b, q, d, "without")
            w("     without this record's draft the same composition's generator %s\n" % (
                "refuses with the same line: the refusal is another draft's (section 8)" if rc2 and line2 == path else
                "runs" if rc2 == 0 else "refuses otherwise: %s" % line2))
            # scratch stand-ins for the other drafts' run-time defects (never drafts, never applied), so this record's loop is
            # judged in the whole composition
            s = os.path.join(d, "standin_gen_sch_%s.py" % b); shutil.copy(composed[b], s)
            txt = open(s, encoding="utf-8").read(); used = []
            for fid, why, old, rep in STANDINS.get(b, ()):
                if txt.count(old) == 1:
                    txt = txt.replace(old, rep); used.append(fid)
            open(s, "w", encoding="utf-8").write(txt)
            rc3, path3, table3 = netlist_text(b, s, d, "standin")
            w("     with scratch stand-ins for %s (never drafts, never applied): %s\n" % (", ".join(used) or "none",
              "the generator ran to its end (%d parts, intent written: %s)" % (len(table3["parts"]), "yes" if table3["intent_written"] else "NO") if rc3 == 0 else "still refused: %s" % path3))
            if rc3 == 0:
                comp[b] = path3
        if comp:
            buf = io.StringIO(); CHK.run(comp, ROOT, buf, label=lambda x: "regenerated board %s, composed in L4-E9's order%s" % (x.upper(), "" if "standin" not in comp[x] else " with the stand-ins"))
            w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m1 = mutate(alone["p"][0], d, "mut_p", [(("J_SMB", "6"), ("J_SMB", "7"))])
        buf = io.StringIO(); CHK.run({"p": m1}, ROOT, buf, label=lambda x: "mutated board P (J_SMB pins 6 and 7 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        m2 = mutate(alone["a"][0], d, "mut_a", [(("J_DOCK", "3"), ("J_DOCK", "4"))])
        buf = io.StringIO(); CHK.run({"a": m2}, ROOT, buf, label=lambda x: "mutated board A (J_DOCK pins 3 and 4 exchanged)")
        w("".join("     " + l + "\n" for l in buf.getvalue().splitlines()))
        w("\n")
        # 7. intent
        w("7. THE INTENT THE PATCHED BOARD P GENERATOR WRITES FOR THE NEW NETS\n")
        it = alone["p"][1]["intent"]
        for n in ("PACK_P", "BRK_VIN", "BRK_SNS", "VCC_F"):
            r = it["rails"].get(n) or {}
            w("   rail %-8s source %s, loads %s, switch %s on %s%s%s\n" % (n, r.get("source"), json.dumps(r.get("loads"), sort_keys=True), r.get("switch", "-"),
                                                                      r.get("enable_net", "-"), ", series of %s" % r["series_of"] if r.get("series_of") else "",
                                                                      ", fed from %s" % r["fed_from"] if r.get("fed_from") else ""))
        for n in ("BRK_GATE", "BRK_UVLO", "BRK_G2", "BRK_CMID", "DOCK_EN_OUT", "DOCK_EN_RET"):
            r = it["nodes"].get(n) or {}
            w("   node %-11s v_max %s V%s\n" % (n, r.get("v_max"), ", rides on %s by %s V" % (r["rides_on"], r["bias_v"]) if r.get("rides_on") else ""))
        cl = it.get("clamps", {}).get("D101") or {}
        w("   clamp D101: %s, protected %s, return %s\n" % (cl.get("direction"), cl.get("protected"), cl.get("return")))
    w("\n8. FINDINGS FOR OTHER AUTHORS (run-time refusals of the composed generators that no text-level composition test reads)\n")
    for b in "ea":
        for fid, why, _o, _r in STANDINS[b]:
            w("   %s board %s: %s\n" % (fid, b.upper(), why))
    w("\nl8p_drafts: done\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
