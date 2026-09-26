#!/usr/bin/env python3
"""Is every part on the board the part the netlist names? Value and footprint per reference (MESHSAT-1357,
26 September 2026). The companion of `netlist_board.py`; rule SCH-002 reads the worst of the two.

WHY IT EXISTS. `netlist_board.py` compares references, pad nets and net names (its docstring's "Three comparisons" and `_main`). It never
asks what a reference IS, so a board placed from an older schematic passes it whenever the change was a value or a
land. The regeneration parity run of 25 September 2026 (W7, box 52646493, commit 82dd1e4d, KiCad 9.0.9) measured
exactly that on three of the six boards: A32's C11 and C12 (100 V in the netlist, 50 V on the board) and D2 (SMCJ40A
against SMCJ33A, the VIN_RAW entry clamp decision 31's criterion fails on); B21's U10 value and the SWD header on
U42, U52 and U62 (the SMD land in the netlist, the through-hole one on the board, finding W7-R2-01); D12's C26, C27,
R11, Y1 and Y2 values and the Y1 and Y2 lands. SCH-002 could see none of them.

WHAT IT COMPARES, for every reference both files carry (a reference on one side only is `netlist_board`'s question
and is counted here, never decided twice):
  1. the value, as KiCad wrote it on each side (the netlist's `(value ...)`, the board's `(property "Value" ...)`);
  2. the footprint NAME: the board file carries the bare name that gen_pcb writes and the netlist the
     library-qualified one, so `Resistor_SMD:R_0603_1608Metric` and `R_0603_1608Metric` are the same land and the
     library nickname is not compared.
The denominator is two comparisons per shared reference. An LCSC code the board carries is compared and REPORTED;
it does not decide, because the rule's two properties are the value and the land and the order code has its own
rules (CMP-002, SUP-001).

HOW IT READS. Both files are parsed as S-expressions (only the board's top-level footprints are built, so a 15 MB
board is read in one pass); nothing is grepped and no KiCad is needed, so it runs on the runner and on a box alike.

Usage: netlist_parts.py <board.kicad_pcb> [<netlist.net>] [--out-dir DIR]
       exit 0 every shared reference agrees, 1 a value or a land differs, 3 nothing to compare
"""
import os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verdict

_TOK = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')
_UNESC = re.compile(r'\\(.)')


def _str(tok):
    """A token as text: a quoted string unescaped the way KiCad escapes it, anything else as written."""
    if len(tok) >= 2 and tok[0] == '"' and tok[-1] == '"': return _UNESC.sub(r"\1", tok[1:-1])
    return tok


def top_level(text, heads):
    """Every node directly under the root whose head is in `heads`, as nested lists of raw tokens. Nodes with any
    other head are walked past without being built."""
    out, depth, stack, expect_head = [], 0, None, False
    for m in _TOK.finditer(text):
        t = m.group(0)
        if expect_head:
            expect_head = False
            if t in heads:
                stack = [[t]]; continue
        if t == "(":
            depth += 1
            if stack is not None: stack.append([])
            elif depth == 2: expect_head = True
        elif t == ")":
            depth -= 1
            if stack is not None:
                node = stack.pop()
                if stack: stack[-1].append(node)
                else: out.append(node); stack = None
        elif stack is not None:
            stack[-1].append(t)
    return out


def _child(node, head):
    return next((c for c in node[1:] if isinstance(c, list) and c and c[0] == head), None)


def read_components(net_path):
    """{ref: {"value", "footprint", "lcsc"}} from a KiCad netlist's components section."""
    txt = open(net_path, encoding="utf-8", errors="replace").read()
    out = {}
    for comps in top_level(txt, {"components"}):
        for c in comps[1:]:
            if not (isinstance(c, list) and c and c[0] == "comp"): continue
            ref = _child(c, "ref"); val = _child(c, "value"); fp = _child(c, "footprint")
            if not ref or len(ref) < 2: continue
            lcsc = ""
            fields = _child(c, "fields")
            for f in (fields or [])[1:]:
                if isinstance(f, list) and f and f[0] == "field":
                    nm = _child(f, "name")
                    if nm and len(nm) > 1 and _str(nm[1]) == "LCSC" and len(f) > 2 and not isinstance(f[2], list):
                        lcsc = _str(f[2])
            out[_str(ref[1])] = {"value": _str(val[1]) if val and len(val) > 1 else None,
                                 "footprint": _str(fp[1]) if fp and len(fp) > 1 else None, "lcsc": lcsc}
    return out


def read_footprints(board_path):
    """{ref: {"value", "footprint", "lcsc"}} from a KiCad board's top-level footprints (KiCad 7 to 9 write
    `(property "Reference" ...)`; KiCad 6 wrote `(fp_text reference ...)`, read as the fallback)."""
    txt = open(board_path, encoding="utf-8", errors="replace").read()
    out = {}
    for fp in top_level(txt, {"footprint", "module"}):
        props = {}
        for c in fp[1:]:
            if isinstance(c, list) and len(c) >= 3 and c[0] == "property":
                props[_str(c[1])] = _str(c[2]) if not isinstance(c[2], list) else ""
            elif isinstance(c, list) and len(c) >= 3 and c[0] == "fp_text" and c[1] in ("reference", "value"):
                props.setdefault(c[1].capitalize(), _str(c[2]))
        ref = props.get("Reference")
        if not ref: continue
        out[ref] = {"value": props.get("Value"), "footprint": _str(fp[1]) if len(fp) > 1 and not isinstance(fp[1], list) else None,
                    "lcsc": props.get("LCSC", "")}
    return out


def _name(fp):
    return (fp or "").split(":")[-1]


def compare(comps, fps):
    """The per-reference differences and the counts, as one record (regen_compare reads this too)."""
    shared = sorted(set(comps) & set(fps))
    r = {"shared_refs": len(shared), "only_netlist": sorted(set(comps) - set(fps)),
         "only_board": sorted(set(fps) - set(comps)), "value": [], "footprint": [], "lcsc": []}
    for ref in shared:
        n, b = comps[ref], fps[ref]
        if (n["value"] or "") != (b["value"] or ""): r["value"].append([ref, n["value"], b["value"]])
        if _name(n["footprint"]) != _name(b["footprint"]): r["footprint"].append([ref, n["footprint"], b["footprint"]])
        if b.get("lcsc") and (n.get("lcsc") or "") != b["lcsc"]: r["lcsc"].append([ref, n.get("lcsc"), b["lcsc"]])
    return r


def main(argv):
    out_dir = verdict.opt(argv, "--out-dir", None)
    a = [x for i, x in enumerate(argv) if not x.startswith("--") and (i == 0 or argv[i - 1] != "--out-dir")]
    if not a: print(__doc__); return verdict.USAGE
    board_path = a[0]
    stem = os.path.splitext(os.path.basename(board_path))[0]
    net_path = a[1] if len(a) > 1 else os.path.join(os.path.dirname(os.path.abspath(board_path)), "out", stem + ".net")
    kw = {"out_dir": out_dir} if out_dir else {}
    inputs = {"board": board_path, "netlist": net_path}
    if not os.path.exists(net_path) or not os.path.exists(board_path):
        missing = [p for p in (board_path, net_path) if not os.path.exists(p)]
        print("netlist_parts: nothing to compare, %s absent" % ", ".join(missing))
        return verdict.write("netlist_parts", verdict.INCONCLUSIVE, denominator=0, inputs=inputs,
                             missing_input="%s absent, so no part was compared" % ", ".join(missing), **kw)
    comps = read_components(net_path)
    if not comps:
        print("netlist_parts: %s carries no component records" % net_path)
        return verdict.write("netlist_parts", verdict.INCONCLUSIVE, denominator=0, inputs=inputs,
                             missing_input="the netlist carries no component records (no value or footprint to compare)", **kw)
    fps = read_footprints(board_path)
    r = compare(comps, fps)
    if not r["shared_refs"]:
        print("netlist_parts: the board and the netlist share no reference")
        return verdict.write("netlist_parts", verdict.INCONCLUSIVE, denominator=0, inputs=inputs,
                             missing_input="the board carries none of the netlist's %d references" % len(comps), **kw)
    ev = (["%s value: netlist %r, board %r" % tuple(x) for x in r["value"]]
          + ["%s footprint: netlist %s, board %s" % tuple(x) for x in r["footprint"]])
    for e in ev[:40]: print("netlist_parts: FAIL " + e)
    for x in r["lcsc"][:10]: print("netlist_parts: reported, not decided: %s LCSC netlist %s, board %s" % tuple(x))
    denom = 2 * r["shared_refs"]; bad = len(r["value"]) + len(r["footprint"])
    print("netlist_parts: %d of %d comparisons agree (%d shared references; %d only in the netlist and %d only on the "
          "board are netlist_board's to judge)" % (denom - bad, denom, r["shared_refs"], len(r["only_netlist"]), len(r["only_board"])))
    return verdict.write("netlist_parts", verdict.FAIL if bad else verdict.PASS,
                         counts={"value_differs": len(r["value"]), "footprint_differs": len(r["footprint"]),
                                 "agree": denom - bad, "shared_refs": r["shared_refs"],
                                 "only_netlist": len(r["only_netlist"]), "only_board": len(r["only_board"]),
                                 "lcsc_differs_reported": len(r["lcsc"])},
                         denominator=denom, evidence=ev, inputs=inputs,
                         note="value and footprint name per shared reference, board against the netlist it was placed from", **kw)


if __name__ == "__main__":
    sys.exit(verdict.guard("netlist_parts", main, sys.argv[1:]))
