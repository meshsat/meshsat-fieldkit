#!/usr/bin/env python3
"""l5r3_panel.py: Layer 5's third round on the panel's contract, read back (MESHSAT-1357, 3 October 2026).

Reads PANEL.md, HW-FW-CONTRACT.md and ASSEMBLY.md as the tree holds them, the two copied inputs (the panel firmware's findings and
session choices at fnd/fw-panel 42c27369, record l8r2's section 3d at 29ffb518), and the sources the decisions rest on (board B's
and board D's generators, CONOPS.md), and prints: every file read with its sha256; the resolution of each finding F-04 to F-13 and
each PI text, as an excerpt verbatim in its target with the source that decides it, its mark, its invalidation trigger and the
Layer 5 criterion it moves; and the coverage of the firmware's session choices (every S-nn named in the copied section 6 is either
adopted in PANEL.md section 9a or HW-FW-CONTRACT.md section 3.8, or named there as not adopted with its reason). It REFUSES (exit 3)
when an excerpt is not in its target, a figure is not in a cited source, a copied input's body does not hash to its declared sha,
a finding F-04 to F-13 has no resolution, or a session choice is unaccounted for. Stdlib only; under a second. Run from anywhere:
`python3 v2/docs/records/l5r2/l5r3_panel.py`. Nothing here is measured: it is a check of text against text."""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TARGETS = {"panel": "v2/docs/PANEL.md", "hwfw": "v2/docs/HW-FW-CONTRACT.md", "assembly": "v2/docs/ASSEMBLY.md"}
SOURCES = {
    "fw": "v2/docs/records/l5r2/inputs/fw-panel-sections-5-6-42c27369.md",
    "l8r2": "v2/docs/records/l5r2/inputs/l8r2-section-3d-29ffb518.md",
    "genb": "v2/ecad/tools/gen_sch_b.py",
    "gend": "v2/ecad/tools/gen_sch_d.py",
    "conops": "v2/docs/CONOPS.md",
}
CRITERIA = {"5.6": "sequencing across interfaces", "5.7": "reset, default and cable-out states for every control line",
            "5.8": "communications and addressing consistent", "5.11": "firmware obligations affecting hardware explicit",
            "5.13": "interface contracts consistent with the tree"}
PI = "l8r2's apply_gen_sch_c_pibtn.py released and board C regenerated"
T = []


def row(i, finding, tg, tx, src, where, figs, mark, trig, crit):
    T.append(dict(id=i, finding=finding, target=tg, text=tx, sources=src, where=where, figures=figs, mark=mark, trigger=trig,
                  criteria=crit))


row("R3-F04", "F-04 the expander order", "panel",
    "On boot the firmware writes the output registers to 0 first (every LED bit is still an input at power-up, so nothing lights)",
    ["fw"], "the firmware's F-04 and S-10; PANEL.md section 5 and FW-A08 (the one rule)", ["F-04", "S-10"],
    "RULE (SESSION, decided on the contract's own rows)", "none", ["5.7", "5.13"])
row("R3-F05", "F-05 NVG against the TX lamp's floor", "panel",
    "The TX lamp follows the panel's duty in every position (DAY 100 %, NIGHT 15 %, NVG 2 %)", ["fw", "conops"],
    "CONOPS section 4's NVG row (behaviour) and section 7a's NVIS target; the shared LED_RAIL (PANEL.md section 1)",
    ["panel at 2 % duty, backlight 5 %, red and amber indicators only", "MIL-STD-3009, Type I, Class B NVIS", "F-05"],
    "RULE (SESSION; CONOPS decides the behaviour)", "an owner ruling that the TX lamp outranks the NVG target (a CONOPS change)", ["5.11", "5.13"])
row("R3-F06", "F-06 the lamp test's chirp", "panel", "a double chirp (F-06: this sentence said a chirp", ["fw"],
    "PANEL.md's sounder patterns (the specific statement); the firmware's F-06 and S-15", ["double chirp", "F-06"],
    "RULE (SESSION)", "none", ["5.13"])
row("R3-F07", "F-07 the slot fault's indicator", "panel",
    "two compute modules lost; decided 3 October 2026, F-07", ["conops", "fw"], "CONOPS section 4e's fault table",
    ["| a compute module lost |", "MASTER CAUT; the e-paper names the slot", "| two modules lost |", "MASTER WARN; SOS set in that state"],
    "RULE (SESSION; CONOPS decides the behaviour)", "none", ["5.13"])
row("R3-F08", "F-08 the e-paper's pacing", "panel",
    "a change of page refreshes at once and the idle page's content at most once a minute", ["fw"], "the firmware's F-08 and S-16",
    ["F-08", "a change of page refreshes at once"], "RULE (SESSION); the panel's least interval TBD (Layer 6)",
    "PDi's statement of a least refresh interval (Layer 6)", ["5.11"])
row("R3-F09", "F-09 the operator's retry", "panel",
    "then leaves it off until the operator acts: from the touch UI, by a retry command over the bridge protocol", ["fw"],
    "the firmware's F-09 and S-04", ["F-09", "panel_slot_operator_retry"], "RULE (SESSION); the protocol owed (MESHSAT-837)",
    "the bridge protocol's definition (MESHSAT-837, the firmware's F-02)", ["5.8", "5.11"])
row("R3-F10", "F-10 the boot-time 5 Hz rule", "hwfw",
    "at 5 Hz, enter H1 with the stop dated at the start-up and raise no slot until the line is back at 1 Hz and 30 minutes have passed",
    ["fw"], "FW-C13's exit (H1 left only at 1 Hz and after 30 minutes); the firmware's F-10 and S-18", ["F-10", "S-18"],
    "RULE (SESSION, the stricter of the two rows)", "none", ["5.6", "5.11"])
row("R3-F11", "F-11 board D's boot levels", "hwfw",
    "X_SA_PD 1 (the exciter on and receiving, `gen_sch_d.py`: 'PD from the expander (default on)'), X_AMP_EN 1", ["gend", "conops", "fw"],
    "gen_sch_d.py's SA868 and codec-mute notes and its level stages; CONOPS's EMCON row",
    ["PD from the expander (default on)", "So the default is a defined \"mute off\"", "the VHF path keeps listening", "F-11"],
    "NETLIST (the generator's designed power-up levels); RULE (SESSION)", "a change of board D's level stages or the SA868's PD polarity", ["5.7", "5.11"])
row("R3-F12", "F-12 the margin hold's SOS text", "panel", '"SOS QUEUED: MARGIN HOLD, COOLING"', ["fw"], "the firmware's F-12 and S-12",
    ["SOS QUEUED: MARGIN HOLD, COOLING"], "RULE (SESSION; the firmware's text adopted)", "none", ["5.11"])
row("R3-F12h", "F-12 in FW-C15", "hwfw", "the e-paper showing \"SOS QUEUED: MARGIN HOLD, COOLING\" (F-12", ["fw"], "the firmware's F-12",
    ["SOS QUEUED: MARGIN HOLD, COOLING"], "RULE (SESSION)", "none", ["5.11"])
row("R3-F13", "F-13 the HDMI select encoding", "panel",
    "slot 1 = both selects low; slot 2 = `HDMI_SEL1` high, `HDMI_SEL2` low; slot 3 = `HDMI_SEL2` high", ["genb", "fw"],
    "gen_sch_b.py lines 1336 to 1348 (U3, U4, U519, U520) with TI SCDS343F Table 1",
    ['ts3("U3", "HDMI1", "HDMI2", "HDMIM", "HDMI_SEL1", "HDMI_EN1")', 'ts3("U4", "HDMIM", "HDMI3", "HDMIO", "HDMI_SEL2", "HDMI_EN2")',
     "H H L: All A channels are enabled", "H H H: All B channels are enabled"], "NETLIST (the generator)", "a change of board B's display switches", ["5.8", "5.13"])
row("R3-PI1", "PI: PANEL.md section 1", "panel", "DRAFTED by record l8r2 at `29ffb518`", ["l8r2"], "l8r2 3d's text for section 1",
    ["read by U1 P1.3"], "DRAFTED; PROVISIONAL", PI, ["5.7", "5.13"])
row("R3-PI4", "PI: PANEL.md section 4", "panel",
    "PI_BTN_n, the PI button, low = pressed (PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND, tau 1.0 ms); raises EXP_INT on a change",
    ["l8r2"], "l8r2 3d's text for section 4", ["PI_BTN_n: the PI button, low = pressed (PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND,", "tau 1.0 ms"],
    "DRAFTED; PROVISIONAL", PI, ["5.7"])
row("R3-PI5", "PI: PANEL.md section 5", "panel", "(read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second poll", ["l8r2"],
    "l8r2 3d's text for section 5", ["(read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second poll)"], "DRAFTED; PROVISIONAL", PI, ["5.11"])
row("R3-PIA", "PI: ASSEMBLY.md line 127", "assembly", "(the panel controller reads it on U1 P1.3; nothing leaves the backer", ["l8r2"],
    "l8r2 3d's text for ASSEMBLY.md", ["(the panel controller reads it on U1 P1.3; nothing leaves the backer)"], "DRAFTED; PROVISIONAL", PI, ["5.13"])
row("R3-PIC", "PI: FW-C03", "hwfw", "DRAFTED: `C:U1` P1.3 (PI_BTN_n)", ["l8r2"], "l8r2 3d's text for FW-C03",
    ["\"`C:U1` P1.3 (PI_BTN_n)\""], "DRAFTED; PROVISIONAL", PI, ["5.11"])
FINDINGS = ["F-04", "F-05", "F-06", "F-07", "F-08", "F-09", "F-10", "F-11", "F-12", "F-13"]


def flat(s):
    return " ".join(str(s).split())


def refuse(msg):
    sys.stderr.write("l5r3_panel: %s\n" % msg)
    sys.exit(3)


def copied_body(text, rel):
    m = re.search(r"the body's own sha256 is ([0-9a-f]{64})", text)
    i, j = text.find("<!-- BODY BEGIN -->\n"), text.find("<!-- BODY END -->")
    if not m or i < 0 or j < i:
        refuse("%s does not carry its declared body" % rel)
    body = text[i + len("<!-- BODY BEGIN -->\n"):j]
    if hashlib.sha256(body.encode("utf-8")).hexdigest() != m.group(1):
        refuse("%s's body does not hash to the sha its header declares" % rel)
    return body


def section(text, start, stop):
    i = text.find(start)
    j = text.find(stop, i + 1) if i >= 0 else -1
    if i < 0 or j < 0:
        refuse("a section is not where it was: %r" % start[:50])
    return text[i:j]


def compute():
    raw, texts, pins = {}, {}, {}
    for k, rel in list(TARGETS.items()) + list(SOURCES.items()):
        p = os.path.join(ROOT, rel)
        if not os.path.isfile(p):
            refuse("missing %s" % rel)
        b = open(p, "rb").read()
        pins[k] = (rel, hashlib.sha256(b).hexdigest())
        t = b.decode("utf-8")
        if "/inputs/" in rel:
            t = copied_body(t, rel)
        raw[k] = t
        texts[k] = flat(t)
    errs = []
    for e in T:
        if flat(e["text"]) not in texts[e["target"]]:
            errs.append("%s: the excerpt is not in %s: %r" % (e["id"], TARGETS[e["target"]], e["text"][:70]))
        src = " ".join(texts[s] for s in e["sources"])
        lost = [f for f in e["figures"] if flat(f) not in src]
        if lost:
            errs.append("%s: figures not in %s: %s" % (e["id"], ", ".join(e["sources"]), lost))
        if "PROVISIONAL" in e["mark"] and not e["trigger"]:
            errs.append("%s: PROVISIONAL with no trigger" % e["id"])
    done = {f for e in T for f in FINDINGS if e["finding"].startswith(f + " ")}
    if set(FINDINGS) - done:
        errs.append("findings without a resolution: %s" % sorted(set(FINDINGS) - done))
    # coverage of the firmware's session choices: every S-nn of the copied section 6 is accounted for in 9a or 3.8
    fw6 = raw["fw"][raw["fw"].find("## 6. Session choices"):]
    sids = sorted(set(re.findall(r"^\| (S-\d\d) \|", fw6, re.M)))
    s9a = flat(section(raw["panel"], "## 9a. Values the contract takes from the panel firmware", "## 10. Shore charge inhibit"))
    s38 = flat(section(raw["hwfw"], "### 3.8 Values adopted from the panel firmware", "## 4. What round 8 changes"))
    cover = {}
    for s in sids:
        where = [n for n, body in (("PANEL.md 9a", s9a), ("HW-FW-CONTRACT.md 3.8", s38)) if re.search(r"\b%s\b" % s, body)]
        notad = re.search(r"Not adopted, with the reason:\*\*(.*)$", s9a)
        if notad and re.search(r"\b%s\b" % s, notad.group(1)):
            where.append("not adopted (PANEL.md 9a)")
        if not where:
            errs.append("%s is not accounted for" % s)
        cover[s] = where
    if len(sids) != 36:
        errs.append("the copied section 6 names %d session choices, not 36" % len(sids))
    if errs:
        for x in errs:
            sys.stderr.write("l5r3_panel: %s\n" % x)
        sys.exit(3)
    return dict(pins=pins, cover=cover, rows=T, prov=[(e["id"], e["trigger"]) for e in T if "PROVISIONAL" in e["mark"]])


def md_rows(R):
    keys = dict(TARGETS, **SOURCES)
    out = ["| id | finding or text | target | text written (excerpt, verbatim) | decided by (file; where) | mark | invalidation trigger | criterion (5.x) |",
           "|---|---|---|---|---|---|---|---|"]
    for e in R["rows"]:
        src = "; ".join(os.path.basename(keys[s]) for s in e["sources"]) + "; " + e["where"]
        out.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (e["id"], e["finding"], os.path.basename(TARGETS[e["target"]]),
                                                                e["text"].replace("|", "/"), src, e["mark"], e["trigger"], ", ".join(e["criteria"])))
    return out


def render(R):
    L = []
    p = L.append
    p("L5-R3: THE PANEL'S CONTRACT AGAINST ITS FIRMWARE, READ BACK (MESHSAT-1357, 3 October 2026). Prototype design: nothing built,")
    p("powered or measured; a check of text against text.")
    p("")
    p("0. INPUTS (sha256)")
    for k in list(TARGETS) + list(SOURCES):
        rel, h = R["pins"][k]
        p("   %-9s %s  %s" % (k, h, rel))
    p("")
    p("1. THE RESOLUTIONS AND THE PI TEXTS (%d; every excerpt in its target, every figure in a cited source)" % len(R["rows"]))
    for e in R["rows"]:
        p("   %s | %s | target %s" % (e["id"], e["finding"], TARGETS[e["target"]]))
        p("      text: %s" % e["text"])
        p("      decided by: %s; %s" % (", ".join(SOURCES[s] for s in e["sources"]), e["where"]))
        p("      figures: %s" % ", ".join(e["figures"]))
        p("      mark: %s; trigger: %s; criteria: %s" % (e["mark"], e["trigger"], ", ".join(e["criteria"])))
    p("")
    p("2. THE FIRMWARE'S SESSION CHOICES, ACCOUNTED FOR (%d)" % len(R["cover"]))
    for s in sorted(R["cover"]):
        p("   %s: %s" % (s, "; ".join(R["cover"][s])))
    p("")
    p("3. THE PROVISIONAL ENTRIES (%d)" % len(R["prov"]))
    for i, t in R["prov"]:
        p("   %s: %s" % (i, t))
    p("")
    p("4. THE TABLE AS MARKDOWN (L5-PANEL-R3.md carries these lines)")
    for ln in md_rows(R):
        p("   " + ln)
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.stdout.write(render(compute()))
