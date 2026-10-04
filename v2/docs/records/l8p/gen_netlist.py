#!/usr/bin/env python3
"""gen_netlist.py: a schematic generator's part table written as a KiCad-form netlist, on a host without KiCad (record l8p,
MESHSAT-1357, 4 October 2026).

Usage:  gen_netlist.py GENERATOR OUT.net [PROJECT]

What it runs. GENERATOR (a scratch copy of v2/ecad/tools/gen_sch_X.py, patched or not) is copied into a fresh temporary
directory beside a stand-in `schlayout` module. The generator places every part through kisch exactly as on the box (kisch,
intent and idc_pads are the tree's own, from v2/ecad/tools); only the layout step is replaced: the stand-in's run() records
kisch's part table (every part's reference, value, footprint, LCSC field and pin-to-net map) and returns a one-page layout, and
the generator then runs to its end, intent.write included, so the generator's own checks of its rails, sources, loads, nodes
and bypass entries are taken on the patched text. The table becomes a netlist in KiCad's export form E: one comp per part and
one net per name with its nodes, the names with KiCad's leading "/" for a label (the readers strip it).

What it is not. It is not KiCad's netlist: no symbol library is read, no wire is drawn, no ERC is run. Pin-to-net maps are what
these generators write per pin (netlist style: every pin a stub and a label), so the connectivity is the generator's, and the
KiCad export on the box (kicad-cli sch export netlist) is the reading of record. The land check of kisch reads only the lands it
finds (the project library; KiCad's own footprints are absent on this host and are listed as unchecked).

Exit 0 on success; 2 on a usage error; the generator's own exit status when it refuses."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(REPO, "v2", "ecad", "tools")

STUB = '''"""stand-in schlayout for record l8p's gen_netlist.py: records the part table, lays out nothing"""
import json, os
def run(parts, sections, power, bypass, header, phase, board_title):
    placed = {r for _t, rs in sections for r in rs}
    json.dump(dict(parts=[dict(ref=p["ref"], value=p["value"], fp=p["fp"], lcsc=p.get("lcsc", ""), nets=p["nets"],
                               lib=p["lib"], sym=p["sym"], in_bom=p.get("in_bom", True)) for p in parts],
                   sections=[[t, list(rs)] for t, rs in sections], unplaced=[p["ref"] for p in parts if p["ref"] not in placed],
                   power=sorted(power)), open(os.environ["L8P_PARTS_JSON"], "w", encoding="utf-8"), indent=0)
    return ("A3", 1, 1, 1)
'''


RUNNER = '''import importlib.util, os, runpy, sys
_here = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("schlayout", os.path.join(_here, "l8p_stub_schlayout.py"))
_m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m); sys.modules["schlayout"] = _m
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
'''


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def netlist(table):
    """KiCad export form E from the recorded table."""
    nets = {}
    for p in table["parts"]:
        if p["ref"].startswith("#"):
            continue                       # a power flag is not a component of the netlist
        for pin, net in sorted(p["nets"].items(), key=lambda kv: (len(kv[0]), kv[0])):
            if net != "NC":
                nets.setdefault(net, []).append((p["ref"], pin))
    s = ['(export (version "E")', '  (design (tool "record l8p gen_netlist.py: the generator\'s part table, no KiCad"))', '  (components']
    for p in table["parts"]:
        if p["ref"].startswith("#"):
            continue
        s.append('    (comp (ref %s) (value %s) (footprint %s) (fields (field (name "LCSC") %s)))' % (q(p["ref"]), q(p["value"]), q(p["fp"]), q(p["lcsc"])))
    s.append('  )')
    s.append('  (nets')
    power = set(table.get("power") or ())
    for i, (net, nodes) in enumerate(sorted(nets.items()), 1):
        name = net if net in power else "/" + net
        s.append('    (net (code "%d") (name %s)%s)' % (i, q(name), "".join(" (node (ref %s) (pin %s))" % (q(r), q(n)) for r, n in nodes)))
    s.append('  ))')
    return "\n".join(s) + "\n"


def run(generator, out_net, project=None):
    """(returncode, generator output, the recorded table or None)."""
    project = project or os.path.splitext(os.path.basename(out_net))[0]
    with tempfile.TemporaryDirectory(prefix="l8p_gen_") as d:
        gen = os.path.join(d, os.path.basename(generator))
        shutil.copy(generator, gen)
        open(os.path.join(d, "l8p_stub_schlayout.py"), "w", encoding="utf-8").write(STUB)
        # kisch puts the tools directory first on sys.path when it is imported, so a stand-in beside the generator would lose
        # to the real schlayout: the runner registers the stand-in under that name before the generator starts
        open(os.path.join(d, "l8p_run.py"), "w", encoding="utf-8").write(RUNNER)
        js = os.path.join(d, "parts.json")
        env = dict(os.environ, PYTHONPATH=TOOLS, L8P_PARTS_JSON=js, KICAD_SYMBOLS=os.path.join(d, "no-kicad-symbols"), PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, "-B", os.path.join(d, "l8p_run.py"), gen, os.path.join(d, project + ".kicad_sch"), project],
                           capture_output=True, cwd=d, env=env)
        log = (r.stdout + r.stderr).decode("utf-8", "replace")
        if r.returncode != 0 or not os.path.isfile(js):
            return (r.returncode or 1), log, None
        table = json.load(open(js, encoding="utf-8"))
        intent = os.path.join(d, "out", project + "-intent.json")
        table["intent_written"] = os.path.isfile(intent)
        if table["intent_written"]:
            table["intent"] = json.load(open(intent, encoding="utf-8"))
    open(out_net, "w", encoding="utf-8").write(netlist(table))
    return 0, log, table


def main(argv):
    if len(argv) not in (2, 3):
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    rc, log, table = run(*argv)
    if rc:
        sys.stderr.write(log[-2000:])
        return rc
    print("gen_netlist: %s parts, %d unplaced, intent %s -> %s" % (len(table["parts"]), len(table["unplaced"]),
                                                                   "written" if table["intent_written"] else "NOT written", argv[1]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
