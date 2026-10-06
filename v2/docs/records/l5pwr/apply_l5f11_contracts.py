#!/usr/bin/env python3
"""apply_l5f11_contracts.py: finding L5-F11 closed, the last withdrawn Layer 4 claims taken out of the contracts for set 28
(MESHSAT-1357, 3 October 2026; record l5pwr, decision 10 of L5-POWER-CONTRACTS.md; authority SESSION, the Layer 5 author of these
rows and of record l5r2). The integrator's script, ORDER: after apply_l5pwr2_contracts.py (L5-F09, L5-F10), whose state it
requires. It edits v2/ecad/tools/pcb_interfaces.yaml and v2/docs/HW-FW-CONTRACT.md and nothing else.

L4-E11 section 18 (carried into set 27) moved the mixer fans off VSYS_E onto U22's regulated +12V_FAN, declared the dock branch
afresh (18b) and restated the stagger (18c); Layer 7's D-18 named the fans; L4-E9 8a reads D-10's guard-on case OPEN. Fourteen edits:

  F11-01  yaml IF-AE-DOCK pin1_vsys_dock: the auxiliary domain's members (D7 and D8 removed by R-177, U22 feeding the fans)
  F11-02  yaml pin1_vsys_dock: the declared current and the contact's share (18b, replacing 1.0 A and its share)
  F11-03  yaml pin1_vsys_dock: the drop at the supplement floor at the declared current (18b)
  F11-04  yaml pin1_vsys_dock: VSYS_E at the floor and at U42's least limit (18b); VSYS_MIN's start not restated there
  F11-05  yaml pin1_vsys_dock: THE FANS' START RULE as 18b states it (17a's per-fan currents on VSYS_E withdrawn)
  F11-06  yaml pin1_vsys_dock: record l5r2's round 2 clause that pointed at the superseded rule, now pointing at the restated one
  F11-07  yaml pin1_vsys_dock: the STATE's "no fan is named" (Layer 7's D-18 names them, cited through R-179)
  F11-08  yaml power_line_states FAN1_SW_FAN2_SW.start: the stagger as E11-39 states it, U42's room (18b)
  F11-09  yaml IF-EXT-DC l4_defects: D-10's guard-on case OPEN (L4-E9 8a), no longer "NOT CLOSED"
  F11-10  HW-FW-CONTRACT.md FW-E11's verification: R-188's acceptance with U22 settled too
  F11-11  HW-FW-CONTRACT.md V-E11: the same
  F11-12  HW-FW-CONTRACT.md section 4.1's R-177 row: U12 and U22 on VSYS_E (the fans on U22's rail), not the fans on VSYS_E
  F11-13  HW-FW-CONTRACT.md HF-F05 (section 7): the finding kept as raised, its answer since appended
  F11-14  HW-FW-CONTRACT.md change record: a row for these edits and apply_l5pwr2_contracts.py's (after the L5-R3 row)

Every figure written is parsed from the Layer 4 files (l4e11_power.out sections 18, 18a, 18b and E11-39; DOWNSTREAM-REGISTER.md
R-177, R-179, R-188; L4-POWER-ARCHITECTURE.md 8a), read through apply_l5pwr2_contracts.py's src() as they stood when this script was
applied (its L4_AT, a49a2b13, since record l5pwr's correction W1 of 6 October 2026: set 31 restated L4-E9's D-10, so the D-10
sentence quoted below is no longer in the tree; finding L5-F14): each source pattern carries no typed number and must match exactly
once. The old texts are patterns with their figures as placeholders, each matched exactly once before it is replaced.

Usage:  apply_l5f11_contracts.py [--check | --write] [--yaml PATH] [--hwfw PATH]     (default --check; default targets: the tree's)
IDEMPOTENT as apply_l5pwr2_contracts.py: all old texts once and no new text: CHECK OK or applied; all old texts gone and all new
texts present: "already applied", nothing written, exit 0; anything else refused. After patching the YAML re-parses, each edited
field carries its new text and none of its old, every edited table row keeps its cell count, L4-E11's dock draft keeps every anchor,
and no em or en dash appears. Exit 0: checked, written or already applied; 3: refused."""
import importlib.util
import os
import subprocess
import sys
import tempfile

NAME = "apply_l5f11_contracts"
HERE = os.path.dirname(os.path.abspath(__file__))
_sp = importlib.util.spec_from_file_location("apply_l5pwr2_contracts_lib", os.path.join(HERE, "apply_l5pwr2_contracts.py"))
A = importlib.util.module_from_spec(_sp)
_sp.loader.exec_module(A)
A.NAME = NAME            # refusals by the shared helpers carry this script's name
REPO, YAML, HWFW, DOCK_DRAFT = A.REPO, A.YAML, A.HWFW, A.DOCK_DRAFT
flat, rx, one, refuse, wrap_into, table_cells = A.flat, A.rx, A.one, A.refuse, A.wrap_into, A.table_cells
DOCK = ("board_to_board", "contracts", "IF-AE-DOCK", "pin1_vsys_dock")
FANSW = ("board_to_board", "power_line_states", "FAN1_SW_FAN2_SW", "start")
DEFECTS = ("board_to_board", "contracts", "IF-EXT-DC", "l4_defects")


def l4():
    V = {}
    # DOWNSTREAM-REGISTER.md R-177: the auxiliary domain's draft
    r177 = "| R-177 | IMPLEMENTATION |"
    V["rail_v"], = one("reg", r"on a regulated (\d+\.\d+ V) rail \+12V_FAN from U22", within=r177)
    V["d78"], = one("reg", r"(D7 and D8 removed)", within=r177)
    # R-179: the fans as Layer 7's D-18 named them
    r179 = "| R-179 | EVIDENCE |"
    V["fan"], V["fan_range"] = one("reg", r"after Layer 7's D-18 named them: (Sanyo Denki \w+), \d+ V, (\d+\.\d+ to \d+\.\d+ V)", within=r179)
    V["l7page"], = one("reg", r"from `(v2/docs/records/l7pwr/L7-FANS-AND-TH1\.md)` at", within=r179)
    if not os.path.isfile(os.path.join(REPO, V["l7page"])):
        refuse("Layer 7's page %s is not in the tree" % V["l7page"])
    # R-188's acceptance
    r188 = "| R-188 | IMPLEMENTATION |"
    V["acc"], = one("reg", r"(one fan ramping at a time, the other, U12 and U22 settled, and the current through J_DOCK pin 1 under \d+\.\d+ A at every start)",
                    within=r188)
    V["acc_i"], = one("reg", r"the current through J_DOCK pin 1 under (\d+\.\d+ A) at every start", within=r188)
    # L4-E11 18, 18a, 18b, E11-39
    V["u22_in"], V["u12"], V["decl"], V["was"] = one(
        "l4e11out", r"U22's input (\d+\.\d+ A) \([^)]*\), with U12's (\d+\.\d+ A): (\d+\.\d+ A) DECLARED on IF-AE-DOCK pin 1 \(was (\d+\.\d+ A)")
    V["least"], V["share_l"], V["room"] = one("l4e11out", r"against U42's least limit (\d+\.\d+ A): (\d+\.\d+) %, (\d+\.\d+ A) in hand")
    V["contact_pct"], V["contact_a"] = one("l4e11out", r"the contact at (\d+\.\d+) % of (\d+\.\d+ A)")
    V["dI"], V["drop"], V["vsyse"], V["vsyse_least"] = one(
        "l4e11out", r"the drop at the floor with (\d+\.\d+ A): (\d+\.\d+ V), VSYS_E (\d+\.\d+ V); at U42's least limit (\d+\.\d+ V)")
    if V["dI"] != V["decl"]:
        refuse("18b's drop is at %s, its declared branch %s" % (V["dI"], V["decl"]))
    V["floor"], = one("l4e11out", r"a buck cannot hold \d+\.\d+ V from the (\d+\.\d+ V) floor")
    V["room2"], V["start_w"] = one("l4e11out", r"with one fan running and U12 on, U42's room (\d+\.\d+ A) leaves (\d+\.\d+ W) at the rail for the other fan's start")
    if V["room2"] != V["room"]:
        refuse("18b's room is printed as %s and %s" % (V["room"], V["room2"]))
    V["stagger"], = one("l4e11out", r"(each by a PWM-duty ramp into the fan's PWM input, never both within \d+ s and never while U12 or U22 starts)",
                        within="E11-39 | FIRMWARE |")
    V["within"], = one("l4e11out", r"never both within (\d+ s) and never while U12 or U22 starts", within="E11-39 | FIRMWARE |")
    # L4-E9 8a D-10
    V["d10"], = one("l4e9md", r"OPEN for the guard-on case: (an absolute-rating violation at a connector fault) \(round 2's")
    return V


def edits(V):
    """(id, target, the yaml field's key path or the table row's first cell, old pattern, new text)."""
    pending = "PROVISIONAL: the start current NOT READ, E11-35, R-179"
    return [
        ("F11-01", "yaml", DOCK, r"the feed of board E's auxiliary domain \(U12, C31, the mixer fans, D7 and D8\),",
         "the feed of board E's auxiliary domain (U12, C31 and U22, whose regulated %s rail +12V_FAN feeds the mixer fans; %s: R-177, "
         "DRAFTED)," % (V["rail_v"], V["d78"])),
        ("F11-02", "yaml", DOCK, r"\d+\.\d+ A declared \(U12 \d+\.\d+ A, the fans \d+\.\d+ A each\), one Preci-Dip 813 contact at \d+\.\d+ percent of "
                                 r"its \d+\.\d+ A;",
         "%s declared (U12 %s, U22's input %s at the floor with both fans at full speed; L4-E11 18b, MODELED, DRAFTED R-177), one "
         "Preci-Dip 813 contact at %s percent of its %s;" % (V["decl"], V["u12"], V["u22_in"], V["contact_pct"], V["contact_a"])),
        ("F11-03", "yaml", DOCK, r"at the supplement floor \d+\.\d+ V with \d+\.\d+ A the drop is \d+\.\d+ V",
         "at the supplement floor %s with the declared %s (L4-E11 18b) the drop is %s" % (V["floor"], V["decl"], V["drop"])),
        ("F11-04", "yaml", DOCK, r"so VSYS_E at least \d+\.\d+ V, \d+\.\d+ V at VSYS_MIN's start \(L4-E11 16e; INFERRED\)",
         "so VSYS_E %s at the floor and at least %s at U42's least limit (L4-E11 18b; INFERRED); VSYS_E at VSYS_MIN's start is not "
         "restated by 18b (16e's value rests on the branch current 18b replaced)" % (V["vsyse"], V["vsyse_least"])),
        ("F11-05", "yaml", DOCK, r"THE FANS' START RULE \(E11-39, FW-E11\): against U42's least limit \d+\.\d+ A with U12's \d+\.\d+ A, both fans "
                                 r"together at most \d+\.\d+ A each, one at a time at most \d+\.\d+ A \(the other running at \d+\.\d+ A\), VSYS_E "
                                 r"at the least limit at least \d+\.\d+ V at the supplement floor, so the fans must start at or under it;",
         "THE FANS' START RULE (E11-39, FW-E11; L4-E11 18b, which withdraws 17a's per-fan currents on VSYS_E): with one fan running "
         "and U12 on, U42's room %s leaves %s at the rail for the other fan's start (%s), and VSYS_E at U42's least limit at least %s "
         "at the supplement floor;" % (V["room"], V["start_w"], pending, V["vsyse_least"])),
        ("F11-06", "yaml", DOCK, r"the start rule above \(\d+\.\d+ A and \d+\.\d+ A on VSYS_E\) is superseded by section 18b: with one fan running "
                                 r"and U12 on, U42 leaves \d+\.\d+ A of room, \d+\.\d+ W at the rail for the other fan's start, the start current "
                                 r"NOT READ \(E11-35\)",
         "the start rule above is section 18b's (17a's per-fan currents on VSYS_E withdrawn; restated in place for set 28 by record "
         "l5pwr, L5-F11)"),
        ("F11-07", "yaml", DOCK, r"a fan or U12 current over \d+\.\d+ A \(E11-35, R-179: no fan is named\)",
         "a fan's start read over U42's room at the declared branch (E11-35, R-179: the fans are named by Layer 7's D-18, %s at %s, "
         "%s; their start current NOT READ)" % (V["fan"], V["fan_range"], V["l7page"])),
        ("F11-08", "yaml", FANSW, r"one at a time with a PWM ramp, never both within \d+ s and never while U12 starts, under U42's least limit "
                                  r"\d+\.\d+ A \(DRAFTED under \(B1\)\); under L4-E11 section 18 \(b929d8be, PROVISIONAL\) Q9 and Q10 are "
                                  r"open-drain drivers of four-wire fans on \+12V_FAN, the ramp a PWM-duty ramp, never while U12 or U22 starts",
         "one at a time, %s (E11-39, L4-E11 18c), the dock branch under U42's least limit %s with %s of room (18b); Q9 and Q10 "
         "open-drain drivers of the four-wire fans' PWM inputs on +12V_FAN (L4-E11 section 18 at b929d8be; DRAFTED R-177, R-181; %s)"
         % (V["stagger"], V["least"], V["room"], pending)),
        ("F11-09", "yaml", DEFECTS, r"D-10's guard-on case NOT CLOSED \(B6-ENG-1\)",
         "D-10's guard-on case OPEN (L4-E9 8a: %s, no loop claimed to pass; PROVISIONAL: B6-ENG-1, B6-ENG-2)" % V["d10"]),
        ("F11-10", "hwfw", "| FW-E11 |",
         r"V-E11 \(R-188's acceptance: one fan ramping at a time, the other and U12 settled, the current through J_DOCK pin 1 under "
         r"\d+\.\d+ A at every start",
         "V-E11 (R-188's acceptance: %s" % V["acc"]),
        ("F11-11", "hwfw", "| V-E11 |",
         r"one fan ramping at a time, the other and U12 settled, never both within \d+ s, the current through J_DOCK pin 1 under "
         r"\d+\.\d+ A at every start",
         "one fan ramping at a time, the other, U12 and U22 settled, never both within %s, the current through J_DOCK pin 1 under %s "
         "at every start" % (V["within"], V["acc_i"])),
        ("F11-12", "hwfw", "| R-177 board E's auxiliary domain",
         r"the fans and U12 on VSYS_E behind U42's",
         "U12 and U22, whose regulated +12V_FAN feeds the fans (L4-E11 section 18, DRAFTED), on VSYS_E behind U42's"),
        ("F11-13", "hwfw", "| HF-F05 |",
         r"no fan part is picked, so the fan's rating against (\d+\.\d+ V is TBD)(?!; since)",
         ("keep", r"no fan part is picked, so the fan's rating against (\d+\.\d+ V is TBD)(?=; since)", hf05_new)),
        ("F11-14", "hwfw", "| 2 (L5-R3) |",
         r"(section \d+\.\d+ binds the panel firmware's adopted session choices with credit \|)(?!\n\| 2 \(L5-PWR, set 28\))",
         ("keep", r"(section \d+\.\d+ binds the panel firmware's adopted session choices with credit \|)(?=\n\| 2 \(L5-PWR, set 28\))",
          change_row)),
    ]


def change_row(kept, V):
    return kept + "\n| 2 (L5-PWR, set 28) | 3 October 2026 | By record l5pwr for set 28 (MESHSAT-1357, findings L5-F09 to L5-F11 of " \
        "`records/l5pwr/L5-POWER-CONTRACTS.md`; `apply_l5pwr2_contracts.py`, then `apply_l5f11_contracts.py`): V-E16's rows 2 and 3 and " \
        "section 4.1's R-173 row restated to R-176 as L4-E7's round 5 has them (D-10's guard-on case OPEN, no loop claimed to pass); " \
        "FW-E11's verification, V-E11 and section 4.1's R-177 row restated to L4-E11 section 18 (U12 and U22 on VSYS_E, the fans on " \
        "U22's rail; R-188's acceptance with U22 settled); HF-F05's answer appended; every figure parsed from the Layer 4 files, each " \
        "restated row PROVISIONAL with its trigger; `pcb_interfaces.yaml` restated in the same pass (IF-AE-DOCK `pin1_vsys_dock`, " \
        "IF-EXT-DC `protection`, `bench` and `l4_defects`, `power_line_states` `FAN1_SW_FAN2_SW`) |"


def hf05_new(old, V):
    return "no fan part is picked, so the fan's rating against %s; since set 27 answered: Layer 7's D-18 names the fans (%s, %s; R-179), which the pack node as generated does not " \
           "cover, and L4-E11 section 18 drafts U22's regulated +12V_FAN for them (R-177, DRAFTED, PROVISIONAL)" % (old, V["fan"], V["fan_range"])


def get(doc, path):
    for k in path:
        doc = doc[k]
    return flat(doc if isinstance(doc, str) else str(doc))


def main(argv):
    mode = "--check"
    paths = {"yaml": os.path.join(REPO, YAML), "hwfw": os.path.join(REPO, HWFW)}
    a = list(argv)
    while a:
        x = a.pop(0)
        if x in ("--check", "--write"):
            mode = x
        elif x in ("--yaml", "--hwfw") and a:
            paths[x[2:]] = os.path.abspath(a.pop(0))
        else:
            print(__doc__)
            return 2
    # ORDER: apply_l5pwr2_contracts.py must be applied to these files first: every old text of it gone. A later round may restate
    # its new texts in place (W8 restated L5-F09 a to d under L5-F14): that tree is applied, then restated, not unapplied, and
    # this script's own state below reads each of its edits as it stands (record l5pwr, W14 of 6 October 2026).
    import collections
    pre = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}
    left = [i for i, tg, _w, old, _n in A.edits(collections.defaultdict(str)) if rx(old).search(pre[tg])]
    if left:
        refuse("ORDER: apply_l5pwr2_contracts.py is not applied to these files (its old text still in them: %s)" % ", ".join(left))
    V = l4()
    texts = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}
    E = []
    for i, tg, where, old, new in edits(V):
        if isinstance(new, tuple):   # F11-13, F11-14: the target's own words kept (a capture), the new text appended to them
            _k, applied, build = new
            ms = list(rx(old).finditer(texts[tg]))
            if len(ms) == 1:
                kept = ms[0].group(1)
            else:   # already applied: read the kept words back from the appended form
                mm = list(rx(applied).finditer(texts[tg]))
                kept = mm[0].group(1) if len(mm) == 1 else "?"
            new = build(flat(kept), V)
        pipes_ok = i == "F11-14"   # a table row added: its pipes are the table's
        if '"' in new or "\\" in new or ("|" in new and not pipes_ok) or chr(0x2014) in new or chr(0x2013) in new:
            refuse("%s: the new text carries a quote, a backslash, a pipe or a dash" % i)
        E.append((i, tg, where, old, new))
    state = [(i, len(list(rx(old).finditer(texts[tg]))), flat(new) in flat(texts[tg])) for i, tg, _w, old, new in E]
    if all(n == 0 and h for _i, n, h in state):
        print("%s: already applied (every old text gone, every new text present); nothing written" % NAME)
        return 0
    bad = [(i, n, h) for i, n, h in state if not (n == 1 and not h)]
    if bad:
        refuse("not in the state this script applies to: %s" % "; ".join("%s: old text %d time(s), new text %s" % (i, n, "present" if h else "absent")
                                                                         for i, n, h in bad))
    new_texts = dict(texts)
    report = []
    for i, tg, where, old, new in E:
        m = list(rx(old).finditer(new_texts[tg]))[0]
        report.append((i, tg, flat(m.group(0)), new))
        if tg == "yaml":
            new_texts[tg] = A.wrap_into(new_texts[tg], m.start(), m.end(), new)
        else:
            ls = new_texts[tg].rfind("\n", 0, m.start()) + 1
            le = new_texts[tg].find("\n", m.end())
            if not new_texts[tg][ls:].startswith(where):
                refuse("%s: the old text is not in the row %r" % (i, where))
            before = table_cells(new_texts[tg][ls:le])
            new_texts[tg] = new_texts[tg][:m.start()] + new + new_texts[tg][m.end():]
            le2 = new_texts[tg].find("\n", ls)
            if before < 0 or table_cells(new_texts[tg][ls:le2]) != before:
                refuse("%s: the row's cell count changed" % i)
            if i == "F11-14":
                nxt = new_texts[tg].find("\n", le2 + 1)
                row = new_texts[tg][le2 + 1: nxt if nxt >= 0 else len(new_texts[tg])]
                if table_cells(row) != before:
                    refuse("%s: the added row has %d cells, its table %d" % (i, table_cells(row), before))
    import yaml
    try:
        doc = yaml.safe_load(new_texts["yaml"])
    except Exception as e:  # noqa: BLE001
        refuse("the patched YAML does not parse: %s" % e)
    for i, tg, where, old, new in E:
        body = get(doc, where) if tg == "yaml" else flat(new_texts[tg])
        if flat(new) not in body or rx(old).search(new_texts[tg]):
            refuse("%s: the field does not carry the new text alone after patching" % i)
    for k in new_texts:
        if new_texts[k] == texts[k]:
            refuse("%s is unchanged" % k)
        if chr(0x2014) in new_texts[k] or chr(0x2013) in new_texts[k]:
            refuse("%s carries an em or en dash" % k)
    d = tempfile.mkdtemp(prefix="l5f11-")
    try:
        y = os.path.join(d, "pcb_interfaces.yaml")
        h = os.path.join(d, "HW-FW-CONTRACT.md")
        open(y, "w", encoding="utf-8").write(new_texts["yaml"])
        open(h, "w", encoding="utf-8").write(new_texts["hwfw"])
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, DOCK_DRAFT), y, "--check"], capture_output=True, text=True)
        if r.returncode != 0 or "CHECK OK" not in r.stdout:
            refuse("L4-E11's dock draft no longer applies to the patched yaml: %s" % (r.stderr.strip().splitlines() or [""])[-1][:200])
        r = subprocess.run([sys.executable, "-B", os.path.join(HERE, "apply_l5pwr2_contracts.py"), "--check", "--yaml", y, "--hwfw", h],
                           capture_output=True, text=True)
        if r.returncode != 0 or "already applied" not in r.stdout:
            refuse("the patched files no longer read as apply_l5pwr2_contracts.py applied")
    finally:
        for f in os.listdir(d):
            os.unlink(os.path.join(d, f))
        os.rmdir(d)
    for i, tg, oldt, new in report:
        print("%s (%s)\n   old: %s\n   new: %s" % (i, os.path.basename(paths[tg]), oldt, new))
    if mode == "--write":
        for k in ("yaml", "hwfw"):
            open(paths[k], "w", encoding="utf-8").write(new_texts[k])
        print("%s: WRITTEN, %d edit(s) in %s and %s" % (NAME, len(E), paths["yaml"], paths["hwfw"]))
    else:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(E)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
