#!/usr/bin/env python3
"""apply_l5pwr2_contracts.py: the contract texts of findings L5-F09 and L5-F10 restated to the Layer 4 text that replaced them
(MESHSAT-1357, set 28, 3 October 2026; record l5pwr, section 4a of L5-POWER-CONTRACTS.md; authority SESSION, the Layer 5 author of
these rows). The integrator's script: it edits v2/ecad/tools/pcb_interfaces.yaml and v2/docs/HW-FW-CONTRACT.md and nothing else.

Set 27 corrected two Layer 4 records after Layer 5's power pass wrote these rows: L4-E7's round 5 withdrew the solar guard's
reference loop as a passing floor (D-10's guard-on case OPEN, an absolute-rating violation at a connector fault, no loop claimed to
pass; R-176's rows 2 and 3 restated), and L4-E11 section 17a called the dock branch's hard-short figure a resistive extrapolation and
E11-38's test target, not a bound, while 18c restated the fans' stagger (a PWM-duty ramp, never while U12 or U22 starts). Six edits:

  L5-F10 a  pcb_interfaces.yaml IF-AE-DOCK pin1_vsys_dock: the hard short ("a ceiling") restated to L4-E11 17a
  L5-F10 b  pcb_interfaces.yaml IF-AE-DOCK pin1_vsys_dock: the fans' stagger restated to L4-E11's E11-39 (18c)
  L5-F09 a  pcb_interfaces.yaml IF-EXT-DC protection: the guard already on restated to L4-E9 4e and 8a D-10 (L4-E7 round 5)
  L5-F09 b  pcb_interfaces.yaml IF-EXT-DC bench: V-E16's row 3 restated to R-176
  L5-F09 c  HW-FW-CONTRACT.md section 4.1, the R-173 row: row 3 restated to R-176
  L5-F09 d  HW-FW-CONTRACT.md V-E16: rows 2 and 3 replaced by R-176's rows 2 and 3, verbatim from the register

Every figure written is parsed from the Layer 4 files in the tree (l4e11_power.out, L4-POWER-ARCHITECTURE.md, DOWNSTREAM-REGISTER.md):
each source pattern below carries no typed number, must match exactly once, and its groups are what the new text prints. The old
texts are patterns too (their figures as placeholders), each matched exactly once in its target before it is replaced.

Usage:  apply_l5pwr2_contracts.py [--check | --write] [--yaml PATH] [--hwfw PATH]     (default --check; default targets: the tree's)
IDEMPOTENT: every old text present once and no new text yet: --check prints CHECK OK, --write applies; every old text gone and every
new text present: "already applied", nothing written, exit 0; anything else (a mixed state, an old text twice, a Layer 4 text that
moved so the new text no longer matches what was applied): refused, nothing written. After patching (and before writing) the YAML
re-parses, each edited field carries its new text and none of its old, every edited table row keeps its cell count, L4-E11's dock
draft (apply_pcb_interfaces_dock.py) keeps every anchor, and no em or en dash appears. Exit 0: checked, written or already applied;
3: refused."""
import os
import re
import subprocess
import sys
import tempfile

NAME = "apply_l5pwr2_contracts"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
YAML = "v2/ecad/tools/pcb_interfaces.yaml"
HWFW = "v2/docs/HW-FW-CONTRACT.md"
SRC = {"l4e11out": "v2/docs/records/l4e11/l4e11_power.out",
       "l4e9md": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
       "reg": "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"}
DOCK_DRAFT = "v2/docs/records/l4e11/apply_pcb_interfaces_dock.py"
WIDTH = 132   # the yaml's wrapped line width


def refuse(msg):
    sys.stderr.write("%s: %s; refusing, nothing written\n" % (NAME, msg))
    sys.exit(3)


def flat(s):
    return " ".join(s.split())


def rx(p):
    """A pattern whose literal spaces match any whitespace (a match may cross a wrapped line)."""
    return re.compile(p.replace(" ", r"\s+"))


_SRC = {}


def src(key):
    if key not in _SRC:
        p = os.path.join(REPO, SRC[key])
        if not os.path.isfile(p):
            refuse("the Layer 4 file %s is missing" % SRC[key])
        _SRC[key] = open(p, encoding="utf-8").read()
    return _SRC[key]


def one(key, pat, within=None):
    """The one match of `pat` in a Layer 4 file (or in the one physical line of it holding `within`); its groups flattened."""
    text = src(key)
    if within is not None:
        lines = [ln for ln in text.split("\n") if within in ln]
        if len(lines) != 1:
            refuse("%s: %d lines hold %r (one expected)" % (SRC[key], len(lines), within))
        text = lines[0]
    ms = list(rx(pat).finditer(text))
    if len(ms) != 1:
        refuse("%s: the Layer 4 text is matched %d times (once expected): %r" % (SRC[key], len(ms), pat[:70]))
    return [flat(g) for g in ms[0].groups()] or [flat(ms[0].group(0))]


# ---------------------------------------------------------------------------------------------- the Layer 4 texts, parsed
def l4():
    V = {}
    # L4-E11 17a: the hard short (case 2) and the pins
    V["toff"], = one("l4e11out", r"turn-off (\d+\.\d+ to \d+\.\d+ us) under I\(SCP\)")
    V["x_a"], = one("l4e11out", r"A resistive EXTRAPOLATION, not a bound \(I\): (\d+ A) would flow")
    V["ron"], = one("l4e11out", r"TI prints RON at (\d+\.\d+ to \d+ A) only")
    V["x_peak"], V["x_t"], V["x_i2t"] = one("l4e11out", r"(\d+ A) for (\d+\.\d+ us) \((\d+\.\d+ A2s)\) is E11-38's TEST TARGET for the recorded peak")
    if V["x_a"] != V["x_peak"]:
        refuse("L4-E11 17a's extrapolation (%s) and its test target (%s) differ" % (V["x_a"], V["x_peak"]))
    V["in_v"], V["in_l"] = one("l4e11out", r"IN at most (\d+\.\d+ V) by TI's Equation 14 at that extrapolation with U42 within (\d+ nH) of C236")
    # L4-E11 E11-39 (18c): the stagger
    V["stagger"], = one("l4e11out", r"(each by a PWM-duty ramp into the fan's PWM input, never both within \d+ s and never while U12 or U22 starts)",
                        within="E11-39 | FIRMWARE |")
    # L4-E9 4e, the guard-on row (L4-E7's round 5)
    row = "with the guard already on (B6; D-10)"
    V["loop"], V["rnd"] = one("l4e9md", r"at round 2's (\d+\.\d+ uH) reference loop, no loop claimed to pass \(L4-E7's round (\d+)\)", within=row)
    V["conn"], V["absmax"], V["far"], V["target"] = one(
        "l4e9md", r"U5's pins, the complete budget, (-\d+\.\d+ to \+\d+\.\d+ V) at a fault at the connector \(past the (-\d+\.\d+ V) "
                  r"ABSOLUTE MAXIMUM\) and (-\d+\.\d+ to \+\d+\.\d+ V) at the lead's far end, against the (\+-\d+\.\d+ V) design target", within=row)
    V["lowl"], V["lowu5"] = one("l4e9md", r"inside \d+ V; at (\d+\.\d+ uH) U5 (\d+\.\d+ V)", within=row)
    V["q12a"], V["q12t"] = one("l4e9md", r"turns Q12 off: at most (\d+\.\d+ A) within (\d+\.\d+ us)", within=row)
    one("l4e9md", r"OPEN for the guard-on case: an absolute-rating violation at a connector fault \(round 2's \d+\.\d+ uH WITHDRAWN as a passing floor")
    # DOWNSTREAM-REGISTER.md R-176 (rows 2 and 3 as round 5 has them)
    r176 = "| R-176 | TEST |"
    V["r2"], V["r3"] = one("reg", r"\(2\) (a \d+ V supply connected cold: .+?); \(3\) (at layer \d+, the waveforms at the IC pins: .+?); \(4\) a reversed bench panel",
                           within=r176)
    V["pvf"], = one("reg", r"(PV_F at most \d+ V), its slew and INP inside their absolute ratings", within=r176)
    V["q12"], = one("reg", r"U21 turning Q12 off \((at most \d+ A, within \d+ us)\)", within=r176)
    V["nopass"], = one("reg", r"(no loop is claimed to pass \(round \d+\))", within=r176)
    V["a_conn"], V["a_abs"] = one("reg", r"at that reference loop the pins' complete budget reads (-\d+\.\d+ to \+\d+\.\d+ V) at a connector fault, "
                                         r"past the (-\d+\.\d+ V) absolute maximum", within=r176)
    if V["a_conn"] != V["conn"] or V["a_abs"] != V["absmax"]:
        refuse("R-176's connector-fault reading (%s, %s) is not L4-E9 4e's (%s, %s)" % (V["a_conn"], V["a_abs"], V["conn"], V["absmax"]))
    return V


def edits(V):
    """(id, target, field path for the yaml or the table row's first cell for the markdown, old pattern, new text)."""
    open_b6 = "PROVISIONAL, OPEN (B6-ENG-1, the engineer's stage question: R-180 an input only, R-186 Analog Devices' answer, R-187 does " \
              "not hold; its wider form B6-ENG-2, R-189, D-16)"
    return [
        ("L5-F10 a", "yaml", ("IF-AE-DOCK", "pin1_vsys_dock"),
         r"a short applied while on at most \d+ A for at most \d+\.\d+ us \(a ceiling, no inductance credited; INFERRED\), IN at most "
         r"\d+\.\d+ V with U42 within \d+ nH of C236 \(a layout requirement\)",
         "a short applied while on: U42 off within %s under I(SCP) (MAKER rows, from a threshold printed typical only); its peak is NOT "
         "BOUNDED by printed data: %s for %s (%s) is a resistive extrapolation, not a bound (TI prints RON at %s only), and E11-38's "
         "test target for the recorded peak, a reading over it revising L4-E11 17a (PROVISIONAL: E11-38, R-184); IN at most %s by TI's "
         "Equation 14 at that extrapolation with U42 within %s of C236 (a layout requirement)"
         % (V["toff"], V["x_peak"], V["x_t"], V["x_i2t"], V["ron"], V["in_v"], V["in_l"])),
        ("L5-F10 b", "yaml", ("IF-AE-DOCK", "pin1_vsys_dock"),
         r"firmware starts them one at a time with a PWM ramp, never both within \d+ s and never while U12 starts \(R-188\)",
         "firmware starts them one at a time, %s (E11-39, R-188; L4-E11 18c; PROVISIONAL: the start current NOT READ, E11-35, R-179; "
         "U42's limit, E11-38)" % V["stagger"]),
        ("L5-F09 a", "yaml", ("IF-EXT-DC", "protection"),
         r"every rating with its margin only from a source loop of at least \d+\.\d+ uH \(U5 \d+\.\d+ V of \+-\d+\.\d+ V, a DESIGN "
         r"TARGET\), NOT under it \(at \d+\.\d+ uH U5 \d+\.\d+ V\): PROVISIONAL, NOT CLOSED \(B6-ENG-1: R-180, R-186 or R-187; L4-E7's "
         r"round \d+ on B6 is running, and its result re-reads this sentence\)",
         "D-10's guard-on case is OPEN since L4-E7's round %s, an absolute-rating violation at a connector fault, not a missed "
         "target: round 2's %s reference loop is withdrawn as a passing floor and no loop is claimed to pass; at that loop U5's pins, "
         "the complete budget, read %s at a fault at the connector, past the %s absolute maximum, and %s at the lead's far end, "
         "against the %s design target; at %s U5 %s; the short-circuit trip or the OV path turns Q12 off at most %s within %s "
         "(MODELED, L4-E7 round %s; L4-E9 4e and 8a D-10; DRAFTED R-173): %s"
         % (V["rnd"], V["loop"], V["conn"], V["absmax"], V["far"], V["target"], V["lowl"], V["lowu5"], V["q12a"], V["q12t"], V["rnd"],
            open_b6)),
        ("L5-F09 b", "yaml", ("IF-EXT-DC", "bench"),
         r"V-E16 \(the solar guard's six rows, R-176; row 3 a pass only for a source loop at or over \d+\.\d+ uH until B6-ENG-1 is "
         r"decided: PROVISIONAL\)",
         "V-E16 (the solar guard's six rows, R-176 as L4-E7's round %s restated them: row 2 %s; row 3 Q12 off %s, and %s, B6-ENG-1 "
         "decides: PROVISIONAL, OPEN, B6-ENG-1 and B6-ENG-2)" % (V["rnd"], V["pvf"], V["q12"], V["nopass"])),
        ("L5-F09 c", "hwfw", "| R-173 the solar guard",
         r"the backstop's trip and the guard's six bench rows; row 3 a pass only from a \d+\.\d+ uH loop until B6-ENG-1",
         "the backstop's trip and the guard's six bench rows (R-176 as L4-E7's round %s restated them); at row 3 %s, B6-ENG-1 decides "
         "(PROVISIONAL, OPEN: B6-ENG-1, B6-ENG-2)" % (V["rnd"], V["nopass"])),
        ("L5-F09 d", "hwfw", "| V-E16 |",
         r"\(2\) a \d+ V supply connected cold: Q12 never conducts, D4 carries nothing, PV_F at most \d+ V; \(3\) at layer \d+, the "
         r"waveforms at the IC pins: a \d+ V supply stepped onto the port with the guard on, from about \d+\.\d+ V and from \d+ V, "
         r"through a loop measured first: U5's CSPIN to CSNIN within \+-\d+\.\d+ V, U21 turning Q12 off \(at most \d+ A, within \d+ "
         r"us\), D4 carrying nothing, PV_P under \d+\.\d+ V, a pass only for a loop at or over \d+\.\d+ uH until B6-ENG-1 is decided "
         r"\(PROVISIONAL: L4-E7's round \d+ on B6 is running; R-180, R-186 or R-187\);",
         "(2) %s; (3) %s (PROVISIONAL, OPEN: D-10's guard-on case; at round 2's reference loop the pins' complete budget reads %s at a "
         "connector fault, past the %s absolute maximum; B6-ENG-1 and B6-ENG-2: R-180, R-186, R-187, R-189);"
         % (V["r2"], V["r3"], V["a_conn"], V["a_abs"])),
    ]


def wrap_into(text, start, end, new):
    """Replace text[start:end] by `new`, and re-wrap it with the rest of the line the old text ended on, to WIDTH at the
    indentation of the line it starts on (a YAML double-quoted scalar folds a line break and its indentation into one space)."""
    ls = text.rfind("\n", 0, start) + 1
    indent = len(text[ls:]) - len(text[ls:].lstrip(" "))
    col = start - ls
    le = text.find("\n", end)
    le = len(text) if le < 0 else le
    new = new + text[end:le]
    end = le
    out, line = [], ""
    room = WIDTH - col
    for w in new.split(" "):
        cand = w if not line else line + " " + w
        if len(cand) > room and line:
            out.append(line)
            line, room = w, WIDTH - indent
        else:
            line = cand
    out.append(line)
    return text[:start] + ("\n" + " " * indent).join(out) + text[end:]


def table_cells(line):
    s = line.strip()
    return len(s[1:-1].split("|")) if s.startswith("|") and s.endswith("|") else -1


def field_text(doc, path):
    c = doc["board_to_board"]["contracts"][path[0]][path[1]]
    return flat(c if isinstance(c, str) else str(c))


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
    V = l4()
    E = edits(V)
    texts = {k: open(p, encoding="utf-8").read() for k, p in paths.items()}
    for _i, _t, _w, _o, new in E:
        if '"' in new or "\\" in new or "|" in new or chr(0x2014) in new or chr(0x2013) in new:
            refuse("%s: the new text carries a quote, a backslash, a pipe or a dash" % _i)
    state = []
    for i, tg, where, old, new in E:
        n_old = len(list(rx(old).finditer(texts[tg])))
        has_new = flat(new) in flat(texts[tg])
        state.append((i, n_old, has_new))
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
            new_texts[tg] = wrap_into(new_texts[tg], m.start(), m.end(), new)
        else:
            ln_start = new_texts[tg].rfind("\n", 0, m.start()) + 1
            ln_end = new_texts[tg].find("\n", m.end())
            before = table_cells(new_texts[tg][ln_start:ln_end])
            if not new_texts[tg][ln_start:].startswith(where):
                refuse("%s: the old text is not in the row %r" % (i, where))
            new_texts[tg] = new_texts[tg][:m.start()] + new + new_texts[tg][m.end():]
            ln_end2 = new_texts[tg].find("\n", ln_start)
            if table_cells(new_texts[tg][ln_start:ln_end2]) != before or before < 0:
                refuse("%s: the row's cell count changed" % i)
    # re-parse and re-read
    import yaml
    try:
        doc = yaml.safe_load(new_texts["yaml"])
    except Exception as e:  # noqa: BLE001
        refuse("the patched YAML does not parse: %s" % e)
    for i, tg, where, old, new in E:
        if tg == "yaml":
            ft = field_text(doc, where)
            if flat(new) not in ft or rx(old).search(ft):
                refuse("%s: %s.%s does not carry the new text alone after patching" % (i, where[0], where[1]))
        else:
            if flat(new) not in flat(new_texts[tg]) or rx(old).search(new_texts[tg]):
                refuse("%s: %s does not carry the new text alone after patching" % (i, HWFW))
    for k in new_texts:
        if new_texts[k] == texts[k]:
            refuse("%s is unchanged" % k)
        if chr(0x2014) in new_texts[k] or chr(0x2013) in new_texts[k]:
            refuse("%s carries an em or en dash" % k)
    # L4-E11's dock draft keeps every anchor in the patched yaml
    d = tempfile.mkdtemp(prefix="l5pwr2-")
    try:
        y = os.path.join(d, "pcb_interfaces.yaml")
        open(y, "w", encoding="utf-8").write(new_texts["yaml"])
        r = subprocess.run([sys.executable, "-B", os.path.join(REPO, DOCK_DRAFT), y, "--check"], capture_output=True, text=True)
        if r.returncode != 0 or "CHECK OK" not in r.stdout:
            refuse("L4-E11's dock draft no longer applies to the patched yaml: %s" % (r.stderr.strip().splitlines() or [""])[-1][:200])
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
