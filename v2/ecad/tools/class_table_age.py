#!/usr/bin/env python3
"""Every committed board's net-class table against the class table its own generator writes (20 September 2026).

A REPORT, not a gate, and it decides no rule.

WHY IT EXISTS. `check_pcb_*`, `dc_drop`, `impedance_check`, `rf_line` and the DSN export all read the classes
out of the PROJECT FILE, which is what the placement generator writes (18 September's finding: the API's own
class table is lost on SaveBoard, so the `.kicad_pro` is the one that counts). A board cut before a class was
added is therefore routed at DEFAULT geometry on every net that class was meant to govern, and every gate
reading that board reads the wrong width, the wrong clearance and the wrong via. The register cannot see it:
it reads a verdict and not a date.

WHAT IT FOUND ON ITS FIRST RUN, and this is the reason it is worth keeping: four of the six boards with a
schematic are routed at a class table their generator has moved past, and in three of them the MISSING class
is exactly the one whose rule fails on the readiness page.

    board A predates SENSE   -> ANA-001 is judged on a board whose 19 sensitive nets have no class at all
    board B predates PANEL   -> PWR-003, the 2 A polyfuse on a 0.4 mm track, is answered by PANEL at 0.8 mm
    board B predates RF      -> RF-001's four antenna nets sit in the USB class
    board D predates SENSE   -> latent: board D's own sensitive rules pass today
    board P predates PACK    -> PI-001 at 1.03 of its limit is answered by PACK at 0.80 mm

Boards C and E match their generators.

It parses both shapes the generators use (a list of tuples and a dict keyed by name) and it never guesses: a
generator whose table it cannot find is REPORTED as unreadable rather than silently passing.

Usage: class_table_age.py [<ecad dir>]
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

PAIRS = [("a", "gen_pcb_a3.py", "pcb-a-power-a23", "pcb-a-power"),
         ("b", "gen_pcb_b3.py", "pcb-b-compute-b19", "pcb-b-compute"),
         ("c", "gen_pcb_c3.py", "pcb-c-display-c8", "pcb-c-display"),
         ("d", "gen_pcb_d3.py", "pcb-d-aprs-d9", "pcb-d-aprs"),
         ("e", "gen_pcb_e3.py", "pcb-e1-dock-e7", "pcb-e1-dock"),
         ("p", "gen_pcb_p3.py", "pcb-p-pack-p2", "pcb-p-pack")]


def generator_classes(path):
    """The class NAMES a placement generator declares, from a list of tuples or a dict keyed by name."""
    src = open(path, encoding="utf-8").read()
    m = re.search(r"CLASSES\s*=\s*([\[\{])", src)
    if not m:
        return None
    op = m.group(1); cl = "]" if op == "[" else "}"
    i = m.end() - 1; d = 0; j = i
    while j < len(src):
        if src[j] == op: d += 1
        elif src[j] == cl:
            d -= 1
            if d == 0: break
        j += 1
    blk = src[i:j + 1]
    return re.findall(r'\(\s*"([A-Za-z0-9_]+)"', blk) if op == "[" else re.findall(r'"([A-Za-z0-9_]+)"\s*:', blk)


def project_classes(path):
    p = json.load(open(path, encoding="utf-8"))
    return [c.get("name") for c in ((p.get("net_settings") or {}).get("classes") or [])]


def rows(ecad):
    out = []
    for letter, gen, pdir, stem in PAIRS:
        g = os.path.join(ecad, "tools", gen)
        pro = os.path.join(ecad, pdir, stem + ".kicad_pro")
        if not os.path.exists(g) or not os.path.exists(pro):
            out.append(dict(board=letter, readable=False, why="no generator or no project file here"))
            continue
        gn = generator_classes(g)
        if gn is None:
            out.append(dict(board=letter, readable=False, why="no CLASSES table found in %s" % gen))
            continue
        cn = project_classes(pro)
        out.append(dict(board=letter, readable=True, generator=gn, board_classes=cn,
                        predates=[x for x in gn if x not in cn]))
    return out


def main(argv):
    ecad = argv[0] if argv else os.path.dirname(HERE)
    rs = rows(ecad)
    behind = [r for r in rs if r.get("predates")]
    for r in rs:
        if not r.get("readable"):
            print("class_table_age: %s UNREADABLE, %s" % (r["board"], r["why"])); continue
        print("class_table_age: %s generator %-38s board %-36s %s"
              % (r["board"], ",".join(r["generator"]), ",".join(r["board_classes"]),
                 ("PREDATES " + ",".join(r["predates"])) if r["predates"] else "match"))
    print("class_table_age: %d of %d board(s) are routed at a class table their generator has moved past"
          % (len(behind), len([r for r in rs if r.get("readable")])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
