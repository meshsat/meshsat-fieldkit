#!/usr/bin/env python3
"""CONOPS.md's EMCON statements rewritten whole from the committed netlists of integration set 12 (MESHSAT-1357, 29 September
2026). The answer to the focused re-check of set 12 (`checks/check-int13-2.md`), blocking B1 carried: the first answer
(`apply_check13_fixes.py`) corrected the two rows the first check named and claimed the rest of the section had been read,
which it had not; three more rows were stale on main since stream w4b, and the board A rows named parts board A no longer
carries. A second failure on the same document, so the method changes: instead of patching named rows, this script
  1. parses the committed netlists of boards A, B, C and D and ASSERTS every gate, supply and net that the new text names
     (`GATES` below), refusing before anything is written if one does not hold;
  2. replaces section 4b's preamble and table as ONE text, and the Off-or-held, Guarantee, Source and Open cells of section
     4's EMCON row, leaving the rest of the file byte for byte (the diff is asserted to touch only those lines, all after the
     needs table of section 2);
  3. appends to CFL-016 an entry that withdraws the two false sentences of the first answer and states what was read, and
     rebinds CFL-016, REQ-005 and CFL-014 and the registry's needs pin to the new file;
  4. files the substance check's two re-checks and the focused re-check under `checks/`, and corrects the README's checks
     table and its line-shift note (minors 4 and 5).
Refuses a second run. Run: python3 <this file>."""
import hashlib, os, re, shutil, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import apply_check1_answers as A
import tx_inhibit as TX

TAG = "apply_conops_4b_set12"
REF = "v2/docs/records/int13/apply_conops_4b_set12.py"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
CON = "v2/docs/CONOPS.md"
DASHES = ("—", "–")
NETS = {"A": ("v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "6c40250c47195ebb"),
        "B": ("v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net", "3ef9b8c49a01b728"),
        "C": ("v2/ecad/pcb-c-display-c8/out/pcb-c-display.net", "87b69472ac83ca5a"),
        "D": ("v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net", "a2d48972d171aad1")}
# (board, ref, value substring or None, {pin: net}) for every gate the new text names
GATES = [
    ("C", "U9", None, {}), ("C", "R52", "330R", {}), ("C", "D23", None, {}),
    ("B", "U112", "SN74LVC1G04", {"2": "EMCON_HW", "4": "EMCON_ON1", "5": "+3V3_CM1"}),
    ("B", "U212", "SN74LVC1G04", {"2": "EMCON_HW", "4": "EMCON_ON2", "5": "+3V3_CM2"}),
    ("B", "U312", "SN74LVC1G04", {"2": "EMCON_HW", "4": "EMCON_ON3", "5": "+3V3_CM3"}),
    ("B", "U501", "SN74LVC1G08", {"1": "EMCON_HW", "2": "LIME_HW_EN", "4": "LIME_EN_A"}),
    ("B", "U502", "SN74LVC1G08", {"1": "LIME_EN_A", "2": "LIME_SW_EN", "4": "LIME_EN"}),
    ("B", "U503", "SN74LVC1G08", {"1": "EMCON_HW", "2": "RB_SW_EN", "4": "RB_EN"}),
    ("B", "U536", "SN74LVC1G08", {"1": "EMCON_HW", "2": "RB_SW_IEN", "4": "RB_IEN_DRV"}),
    ("B", "R532", "2.7k", {"1": "RB_IEN_DRV", "2": "RB_IEN"}),
    ("B", "U543", "TPS3808G30", {"1": "RB_IEN", "5": "+3V3_DEV", "6": "+5V_DEV"}),
    ("B", "U537", "SN74LVC1G08", {"1": "RB_IEN", "2": "RB_STATUS", "4": "RB_GO"}),
    ("B", "U538", "SN74LVC1G08", {"1": "RB_RXD_H", "2": "RB_GO", "4": "RB_RXD"}),
    ("B", "U539", "SN74LVC1G08", {"1": "RB_CTRL_H", "2": "RB_GO", "4": "RB_CTRL"}),
    ("B", "J_RB9704", None, {"3": "RB_IEN", "7": "RB_STATUS"}),
    ("B", "U504", "SN74LVC1G08", {"1": "EMCON_HW", "2": "LORA_ON", "4": "E22_EN"}),
    ("B", "U544", None, {"2": "E22_EN", "4": "LORA_GO", "5": "+3V3_CM3"}),
    ("B", "U545", "SN74LVC1G08", {"1": "LORA_RXEN", "2": "LORA_GO", "4": "LORA_RXEN_G"}),
    ("B", "U546", "SN74LVC1G08", {"1": "LORA_TXEN", "2": "LORA_GO", "4": "LORA_TXEN_G"}),
    ("B", "U547", "SN74LVC1G08", {"2": "LORA_GO", "4": "LORA_NRST"}), ("B", "U548", "SN74LVC1G08", {"2": "LORA_GO", "4": "LORA_MOSI"}),
    ("B", "U549", "SN74LVC1G08", {"2": "LORA_GO", "4": "LORA_SCLK"}), ("B", "U550", "SN74LVC1G08", {"2": "LORA_GO", "4": "LORA_NSS"}),
    ("B", "U12", None, {"6": "LORA_RXEN_G", "7": "LORA_TXEN_G"}),
    ("B", "R542", "100k", {"1": "LORA_TXEN_G", "2": "GND"}), ("B", "R543", "100k", {"1": "LORA_RXEN_G", "2": "GND"}),
    ("B", "U505", "SN74LVC1G08", {"1": "EMCON_HW", "2": "ZB_ON", "4": "E72_EN"}),
    ("B", "U540", "SN74LVC2G07", {"6": "ZBA_RXD", "4": "ZBA_RST_n"}), ("B", "U542", "SN74LVC2G07", {"6": "ZBB_RXD", "4": "ZBB_RST_n"}),
    ("B", "U541", "SN74LVC2G07", {"6": "ZBA_BSL", "4": "ZBB_BSL"}),
    ("B", "R536", None, {}), ("B", "R537", None, {}),
    ("B", "U216", "SN74LV1T08", {"1": "EMCON_HW", "2": "PCIE_PWR_EN2", "4": "S2A_EN", "5": "+5V_S2"}),
    ("B", "U203", "AP64500", {"3": "S2A_EN"}),
    ("B", "U215", "SN74LVC2G06", {"1": "EMCON_ON2", "6": "5G_W_DIS_n", "3": "GND"}),
    ("B", "U220", "SN74LVC2G06", {"1": "EMCON_ON2", "6": "5G_PWROFF_n"}),
    ("B", "U221", "TPS3808G30", {"1": "5G_TPR_n", "5": "+3V3_S2A", "6": "+3V3_S2A"}),
    ("B", "U554", "SN74LVC2G07", {"1": "5G_TPR_n", "6": "5G_PWROFF_n"}),
    ("B", "Q212", None, {"1": "EMCON_ON2", "3": "5G_DCHG"}), ("B", "R295", "15R", {"1": "+3V3_M2C2", "2": "5G_DCHG"}),
    ("B", "U116", "SN74LV1T08", {"1": "EMCON_HW", "2": "PCIE_PWR_EN1", "4": "S1A_EN", "5": "+5V_S1"}),
    ("B", "U316", "SN74LV1T08", {"1": "EMCON_HW", "2": "PCIE_PWR_EN3", "4": "S3A_EN", "5": "+5V_S3"}),
    ("B", "U115", "SN74LVC2G06", {"1": "EMCON_ON1", "6": "WIFI_W_DIS_n", "3": "GND"}),
    ("B", "U315", "SN74LVC2G06", {"1": "EMCON_ON3", "6": "WIFI2_W_DIS_n", "3": "GND"}),
    ("B", "U113", "SN74LVC2G06", {"1": "EMCON_ON1", "3": "EMCON_ON1", "6": "WL_nDIS1", "4": "BT_nDIS1", "5": "+3V3_CM1"}),
    ("B", "U213", "SN74LVC2G06", {"1": "EMCON_ON2", "3": "EMCON_ON2", "6": "WL_nDIS2", "4": "BT_nDIS2", "5": "+3V3_CM2"}),
    ("B", "U313", "SN74LVC2G06", {"1": "EMCON_ON3", "3": "EMCON_ON3", "6": "WL_nDIS3", "4": "BT_nDIS3", "5": "+3V3_CM3"}),
    ("B", "U114", "SN74LVC2G06", {"1": "WL_nDIS1_OFF", "3": "BT_nDIS1_OFF", "6": "WL_nDIS1", "4": "BT_nDIS1"}),
    ("A", "U35", "SN74AUP1G08", {"1": "TX_INHIBIT_n", "2": "EMCON_HW", "4": "PA_TXOK", "5": "+3V3_EMCON"}),
    ("A", "U36", "SN74AUP1G08", {"1": "PA_TXOK", "2": "PA_HOLD", "4": "PA_EN", "5": "+3V3_EMCON"}),
    ("A", "U37", "SN74AUP1G08", {"1": "TX_INHIBIT_n", "2": "EMCON_HW", "4": "HF_TXOK", "5": "+3V3_EMCON"}),
    ("A", "U38", "SN74AUP1G08", {"1": "HF_TXOK", "2": "HF_HOLD", "4": "HF_EN", "5": "+3V3_EMCON"}),
    ("D", "U12", "74LVC1G08", {"1": "PTT_ANY", "2": "TX_INHIBIT_n", "4": "KEY"}),
    ("D", "U14", "74LVC1G08", {"1": "KEY", "2": "PA_EN", "4": "PA_KEY"}),
]
NETS_PRESENT = [("B", "+3V3_ZB", ["R536", "R537"]), ("B", "E72_EN", ["U505", "U22"]), ("C", "EMCON_HW", ["R52", "D23"]),
                ("C", "TX_INHIBIT_n", ["D23"])]

SEC4B = """### 4b. What EMCON does to each radio, as generated

Read from the committed netlists of integration set 12 (29 September 2026, MESHSAT-1357): board A `6c40250c47195ebb`,
board B `3ef9b8c49a01b728`, board C `87b69472ac83ca5a`, board D `a2d48972d171aad1`. Every gate, supply and net the rows
below name was asserted on those netlists by `v2/docs/records/int13/apply_conops_4b_set12.py` before this text was
written. The transmitter-by-transmitter record, with each state, fault and proof owed, is `feasibility/EMCON.md` section 4
(board B's round 8 in its section 4b, stream w4b in 4c, stream d4emcon's remedies of set 12 in 4d). "Asserted" means
`SW_EMCON` closed: `TX_INHIBIT_n` goes low; on board C `U9` buffers it onto `EMCON_HW` through `R52` (330 Ohm) and `D23`
clamps `EMCON_HW` to `TX_INHIBIT_n` (finding D4E-F1); board B inverts `EMCON_HW` once per slot into `EMCON_ON1..3` (high =
asserted), each from that module's own 3.3 V (`U112`, `U212`, `U312`); board A gates its PA and HF rails on both lines.

| Radio | What the line drives | What EMCON removes | Receive under EMCON |
|---|---|---|---|
| LimeSDR Mini 2.4 | the enable of the eFuse that feeds its USB VBUS, its only supply: `EMCON_HW` AND the hub's port power AND the software enable (`U501`, `U502`) | power | lost |
| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired (`RB_EN` = `EMCON_HW` AND `RB_SW_EN`, `U503`); its ENABLE, forced low in hardware since stream w4b: `U536` drives it as `EMCON_HW` AND the firmware's request `RB_SW_IEN`, through `R532` since set 12, and `U543`, a TPS3808G30 supervisor powered from `+5V_DEV` that watches `+3V3_DEV`, holds it low below 2.79 V; since set 12 the module's RXD and P_EN inputs pass only while `RB_GO` = `RB_IEN` AND its `I_BTD` status (`U537`, `U538`, `U539`; `feasibility/EMCON.md` sections 4c and 4d) | power at that pin, and the ENABLE; the module's own two 10 F supercapacitors (about 16 J) keep it powered after the supply gate opens, and what it does when ENABLE falls is in no held document, so its local chain stays OPEN (`feasibility/EMCON.md` sections 4.4 and 4c) | lost, at the latest once its own stored energy is spent (about 4.5 minutes idle, INFERRED, EMCON.md section 4.4) |
| E22-900M30S LoRa | the enable of the load switch that feeds its VCC pins (`E22_EN` = `EMCON_HW` AND `LORA_ON`, `U504`); since set 12 its TXEN, RXEN, NRST and SPI inputs pass slot 3's lines only while that enable is high: `LORA_GO`, a copy of `E22_EN` on slot 3's own 3.3 V (`U544`), gates `LORA_TXEN` into TXEN (`U546`), `LORA_RXEN` into RXEN (`U545`) and NRST, MOSI, SCK and NSS (`U547` to `U550`), TXEN and RXEN held low by 100 k (`R542`, `R543`; `feasibility/EMCON.md` section 4d) | power; TXEN held low | lost |
| Two E72 CC2652P (Zigbee, Thread) | the enable of the load switch that feeds both (`E72_EN` = `EMCON_HW` AND `ZB_ON`, `U505`, into `U22`); since set 12 the host's receive, reset and boot-select lines reach them only through open-drain buffers (`U540` to `U542`), the receive lines pulled up to the modules' own switched rail `+3V3_ZB` (`R536`, `R537`; `feasibility/EMCON.md` section 4d) | power | lost |
| RM520N-GL 5G | the enable of its 3.3 V buck (`U203`): `S2A_EN` = `EMCON_HW` AND `PCIE_PWR_EN2`, driven by `U216` from slot 2's own 5 V since stream w4b; its FULL_CARD_POWER_OFF# pulled low by `U220` from `EMCON_ON2`, and held low by `U221`, a TPS3808G30 on the buck's output, through `U554` while that rail comes up (finding D4E-F2, set 12); its W_DISABLE1# pulled low by `U215` from `EMCON_ON2`; its socket rail discharged through 15 Ohm (`Q212`, `R295`) | power, with no firmware in the path: RF off within about 1.2 ms plus 1.8 ms per mF of the module's own input capacitance, which no held document states (`feasibility/EMCON.md` section 4b, SD-EMC-1r8); Quectel warns that cutting the supply of a working module can corrupt its flash, a residual accepted | lost |
| Two AW7915-AED WiFi link cards | the enable of each card's 3.3 V buck: `S1A_EN` and `S3A_EN` = `EMCON_HW` AND the slot's `PCIE_PWR_EN`, driven by `U116` and `U316` from the slot's own 5 V since stream w4b; each card's W_DISABLE1#, pulled low by `U115` and `U315` from `EMCON_ON1` and `EMCON_ON3` | power (the disable pin is not counted: the maker's datasheet does not mention it and the mainline Linux driver has no code for it) | lost |
| SA868 VHF with the 30 W PA | the KEY gate on board D (`KEY` = `PTT_ANY` AND `TX_INHIBIT_n`, `U12`) and, through it, the PA's keying (`PA_KEY` = `KEY` AND `PA_EN`, `U14`); the PA rail on board A (`PA_EN` = `TX_INHIBIT_n` AND `EMCON_HW` AND the software hold `PA_HOLD`, `U35` and `U36` on their own supply `+3V3_EMCON`; `feasibility/EMCON.md` section 4a); the exciter's supply is not gated and the resting relay joins antenna to exciter | transmit only | continues |
| QMX HF | the enable of the converter that feeds its DC input (`HF_EN` = `TX_INHIBIT_n` AND `EMCON_HW` AND the software hold `HF_HOLD`, `U37` and `U38` on `+3V3_EMCON`); its USB supply is not gated | power (its receiver runs from the DC input per its manual) | lost |
| The three compute modules' own WiFi and Bluetooth | each module's WL_nDisable and BT_nDisable, only ever pulled low, by open-drain outputs run from the module's own 3.3 V: `U{s}13` from `EMCON_ON{s}` and `U{s}14` from the software request | RF (the module's radio disabled in hardware, Compute Module 5 datasheet sections 2.1.1 and 2.1.2) | lost |
| LG290P GNSS, DCF77, lightning sensor | nothing | receive-only; nothing to remove | continues |

"""

CELL4 = ("radios dark (owner ruling D-05), as section 4b: power removed from the SDR, the RockBLOCK (its ENABLE forced low as "
         "well), the LoRa module, both E72, the HF unit and the two WiFi link cards; the compute modules' own WiFi and "
         "Bluetooth disabled through open drains; the 5G module's supply removed by hardware with its disable pins pulled low "
         "at the same moment (since board B's round 8, section 4b); the PA rail and keying off; software holds every send, an "
         "SOS included")
CELL5 = ("HW for the gated rails, the module radio disables, the RockBLOCK's ENABLE and the VHF keying; the RockBLOCK stays "
         "powered on its own stored energy after its supply gate opens, and what it does when its ENABLE falls is in no held "
         "document (`feasibility/EMCON.md` sections 4.4 and 4c); SW hold on top")
CELL7 = ("`PANEL.md` sections 6 and 9; `feasibility/EMCON.md` sections 4 and 4a to 4d; section 4b (the committed netlists of "
         "integration set 12)")
CELL8 = ("session work owed under D-05 (S-01), each with its dependency in `feasibility/EMCON.md` section 4d.5: the Iridium "
         "9704's response to its ENABLE (a maker's document, or bench E-04); `U536`'s residual race and the band of `U{s}12` to "
         "`U{s}15` (E-11); the SA868's PTT threshold (bench E-01, S-92); row 3's ground on board A in the LM5176's shutdown "
         "(S-93); RF-002's walk classes for set 12's new parts (a tools item); the hardware EMCON lamp's plate light guide "
         "(S-44; the lamp is drawn on board C since its round 8); every row's radio-side latency (E-01 to E-10, E-12); twelve "
         "bench tests, none of them with the kit's own SDR (EMCON.md section 6). Drawn and closed at desk: the 5G module's "
         "staged supply removal since board B's round 8 (SD-EMC-1r8), the RockBLOCK's ENABLE in hardware and the enable "
         "dividers of `U501` to `U504` since stream w4b, and the back-feed paths into the RockBLOCK, the E22 and the E72 "
         "since set 12 (EMCON.md sections 4c and 4d).")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def sha16(p): return hashlib.sha256(open(os.path.join(TOP, p), "rb").read()).hexdigest()[:16]


def gates_hold():
    nl = {}
    for k, (p, s) in NETS.items():
        if sha16(p) != s: refuse("board %s's netlist is not set 12's %s" % (k, s))
        nl[k] = TX.parse_netlist(os.path.join(TOP, p))
    n = 0
    for k, ref, val, pins in GATES:
        if ref not in nl[k]["comps"]: refuse("board %s has no %s" % (k, ref))
        if val and val not in TX.value(nl[k], ref): refuse("board %s %s is %r, not %s" % (k, ref, TX.value(nl[k], ref)[:50], val))
        for p, net in pins.items():
            got = nl[k]["pin"].get((ref, p))
            if got != net: refuse("board %s %s pin %s is %r, not %s" % (k, ref, p, got, net))
            n += 1
    for k, net, refs in NETS_PRESENT:
        on = {r for r, _p, *_ in nl[k]["nets"].get(net, [])}
        if not set(refs) <= on: refuse("board %s net %s lacks %s" % (k, net, sorted(set(refs) - on)))
    return n


def rewrite():
    p = os.path.join(TOP, CON)
    t = open(p, encoding="utf-8").read()
    i = t.index("### 4b. What EMCON does to each radio, as generated\n")
    j = t.index("**Owner ruling D-05 (26 September 2026): EMCON means radios dark, as generated and completed.**")
    if t.count("### 4b. What EMCON does to each radio") != 1 or not i < j: refuse("section 4b's bounds")
    t = t[:i] + SEC4B + t[j:]
    lines = t.split("\n")
    rows = [k for k, l in enumerate(lines) if l.startswith("| EMCON | `SW_EMCON` closed")]
    if len(rows) != 1: refuse("section 4's EMCON row")
    cells = [c.strip() for c in lines[rows[0]].strip().strip("|").split(" | ")]
    if len(cells) != 9: refuse("the EMCON row has %d cells" % len(cells))
    for k, want in ((4, "radios dark (owner ruling D-05)"), (5, "HW for the gated rails"), (7, "`PANEL.md` sections 6 and 9"),
                    (8, "session work owed under D-05 (S-01)")):
        if not cells[k].startswith(want): refuse("EMCON row cell %d" % k)
    cells[4], cells[5], cells[7], cells[8] = CELL4, CELL5, CELL7, CELL8
    lines[rows[0]] = "| " + " | ".join(cells) + " |"
    t = "\n".join(lines)
    if any(d in SEC4B + CELL4 + CELL5 + CELL7 + CELL8 for d in DASHES): refuse("a dash in the new text")
    open(p, "w", encoding="utf-8").write(t)


def append(out, rid, entry, rebind=None):
    A.screen(entry, rid)
    if not re.search(r"v2/[^\s,;()]*\.(?:py|md)", entry): refuse("%s: the entry names no file" % rid)
    i, j = A.span(out, rid)
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
    if rebind:
        if t.count(rebind[0]) != 1: refuse("%s: the binding %s found %d times" % (rid, rebind[0], t.count(rebind[0])))
        t = t.replace(rebind[0], rebind[1])
    return out[:i] + t + out[j:]


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    npins = gates_hold()
    con_old = sha16(CON)
    rewrite()
    con_new = sha16(CON)
    d = subprocess.run(["git", "-C", TOP, "diff", "-U0", "--", CON], capture_output=True, text=True, check=True).stdout
    hunks = [(int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)) for m in re.finditer(r"(?m)^@@ -(\d+)(?:,(\d+))? ", d)]
    if not hunks or min(a for a, _n in hunks) <= 146: refuse("the diff reaches the needs table: %s" % hunks)
    touched = "; ".join("%d to %d" % (a, a + max(n, 1) - 1) for a, n in hunks)
    before = yaml.safe_load(reg)
    old_b, new_b = "%s@%s" % (CON, con_old), "%s@%s" % (CON, con_new)
    bound = sorted(r["id"] for r in before["records"] if old_b in (r.get("evidence_bound_to") or []))
    if bound != ["CFL-014", "CFL-016", "REQ-005"]: refuse("records bound to CONOPS.md: %s" % bound)
    out = reg
    op = "needs_document_sha256: %s" % before["needs_document_sha256"]
    if out.count(op) != 1 or not before["needs_document_sha256"].startswith(con_old): refuse("the needs pin")
    out = out.replace(op + "\n", "needs_document_sha256: %s\n" % hashlib.sha256(open(os.path.join(TOP, CON), "rb").read()).hexdigest(), 1)
    head = ("%s re-read at integration set 12, second pass (%s, %s to %s): section 4b's preamble and table and section 4's "
            "EMCON row were rewritten whole from the committed netlists of set 12 (A 6c40250c47195ebb, B 3ef9b8c49a01b728, C "
            "87b69472ac83ca5a, D a2d48972d171aad1), %d pin assignments of the gates they name asserted on those netlists before "
            "the text was written; the diff touches only old lines %s, all after the needs table" % (CON, REF, con_old, con_new, npins, touched))
    out = append(out, "CFL-016", head + ". Correction (the focused re-check of set 12, v2/docs/records/int13/checks/check-int13-2.md, "
                 "blocking B1 carried): the entry of apply_check13_fixes said that the section's other rows were read against the "
                 "same netlist by the check, and that every named document describes the circuit as generated; both sentences are "
                 "withdrawn. The first check had read only the two rows it named, and more were stale on main since stream w4b: "
                 "section 4's EMCON row (the RockBLOCK's ENABLE held by firmware, the back-feed paths owed), section 4b's 5G row "
                 "(its buck's enable named U215; it is U216, EMCON_HW AND PCIE_PWR_EN2 on +5V_S2), its WiFi row (U115 and U315 "
                 "named for the buck enables; they are U116 and U316, and U115 and U315 pull W_DISABLE1# only), and its board A "
                 "rows, which named U26 and a round 8 candidate where U35 to U38 are generated. The other documents this record "
                 "names were read by that re-check, which found no stale statement outside CONOPS.md; rebound to %s. The "
                 "result stands on the rewritten text." % con_new, (old_b, new_b))
    out = append(out, "REQ-005", head + ". This record reads section 2a's list of critical peripherals, which the diff does "
                 "not touch; rebound to %s. No result changes." % con_new, (old_b, new_b))
    out = append(out, "CFL-014", head + ". This record reads section 4's Charging row, which the diff does not touch; "
                 "rebound to %s. No result changes." % con_new, (old_b, new_b))
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        if (rid in bound and not dd <= {"evidence", "evidence_bound_to"}) or (rid not in bound and dd): refuse("%s: %s" % (rid, dd))
    top = {k for k in set(before) | set(after) if k != "records" and before.get(k) != after.get(k)}
    if top != {"needs_document_sha256"}: refuse("top-level fields moved: %s" % top)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    # the checks, filed; the README's checks table and line-shift note
    scr = os.path.join(os.path.expanduser("~"), "worktrees", "meshsat-fieldkit", "_scratch") + os.sep   # where the checkers wrote
    for src, dst in (("chk-set12/CHECK-2.md", "check-set12-2.md"), ("chk-set12/CHECK-3.md", "check-set12-3.md"),
                     ("chk-int13b/CHECK.md", "check-int13-2.md")):
        t = open(scr + src, encoding="utf-8").read()
        t = re.sub(r"`?_scratch/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*`?", "a scratch clone", t)
        t = re.sub(r"/home/[^\s`)]*|/tmp/[^\s`)]*|/root/[^\s`)]*", "a local path", t)
        open(os.path.join(HERE, "checks", dst), "w", encoding="utf-8").write(t)
    rp = os.path.join(HERE, "README.md")
    t = open(rp, encoding="utf-8").read()
    for o, n in (("| `checks/check-set12-1.md` (the substance check, and its re-checks on rf2walk2 and rf2walk3) |",
                  "| `checks/check-set12-1.md` (the substance check), `checks/check-set12-2.md` and `-3.md` (its re-checks on rf2walk2 and rf2walk3) |"),
                 ("| `checks/check-int13-1.md` (the integration check at `005e5f5e`) | not mergeable: B1, and minors m1 to m9 | `apply_check13_fixes.py` (B1, m1, m2, m3, m6, m8, m9), this README (m4, m5, m7), the re-take at the corrected commit (m5) |",
                  "| `checks/check-int13-1.md` (the integration check at `005e5f5e`) | not mergeable: B1, and minors m1 to m9 | `apply_check13_fixes.py` (B1, m1, m2, m3, m6, m8, m9), this README (m4, m5, m7), the re-take at the corrected commit (m5) |\n"
                  "| `checks/check-int13-2.md` (the focused re-check at `69156cad`) | not mergeable: B1 carried (the first answer claimed rows it had not read), and five minors | `apply_conops_4b_set12.py` (section 4b and the EMCON row rewritten whole from the netlists, B1 and minors 1 to 3), this README (minors 4 and 5) |"),
                 ("  - `gen_sch_a.py` moved by +35 lines after line 857 and by +55 after line 907, as the check measured.",
                  "  - `gen_sch_a.py` moved by +35 lines from main's line 860 and by +55 from main's line 910 (the focused re-check's measure; the first note said after 857 and 907).")):
        if t.count(o) != 1: refuse("README: %r" % o[:60])
        t = t.replace(o, n)
    open(rp, "w", encoding="utf-8").write(t)
    print("%s: %d pin assignments asserted on set 12's netlists; CONOPS %s to %s (old lines %s); CFL-016, REQ-005, CFL-014 "
          "rebound and the needs pin moved; three checks filed; README corrected" % (TAG, npins, con_old, con_new, touched))
    return 0


if __name__ == "__main__":
    sys.exit(main())
