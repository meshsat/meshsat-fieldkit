#!/usr/bin/env python3
"""l6r2_passives.py: Layer 6 criterion 6.1 for the GENERIC parts of the six boards (MESHSAT-1357, record l6r2, 3 October 2026).

PROTOTYPE DESIGN: nothing is bought, built, powered or measured. The rows are the COMMITTED netlists' fitted parts (the
identity tool's reader, part_identities.rows: every part the schematic does not mark exclude_from_bom), and the parts here are
those WITHOUT an LCSC field: per board, in the order A, E, P, D, C, B, each distinct selection (part_identities' key: value,
land and every deciding requirement) is classified, and the GENERIC ones (multilayer ceramic capacitors, resistors, ferrite
beads, small diodes of a generic type, 0603 indicator LEDs) are given an exact part: maker, MPN, LCSC code, from a dated
public reading of JLCPCB's parts library (inputs/), checked property by property against the requirement the identity tool
derives from the netlist and the board's intent:
  a ceramic's rated voltage against rule V-1 (the voltage across it from the intent, or the BOUND of its nets, at derate.py's
    20 percent margin, rounded up to a standard rating); its dielectric against rules C-D1 to C-D3 (DIELECTRIC_ACCEPTS); its
    tolerance against the stated one or rule C-T;
  a resistor's power against rule R-P (a shunt twice its I^2 R at the declared peak, any other its package's standard rating),
    its tolerance against the stated one or rule R-T1, a shunt's temperature coefficient against rule R-S1;
  the temperature grade against the envelope's board air, -20 to +62.1 C (pcb_envelope.yaml): a resistor's or diode's operating
    range as the catalogue line prints it, a ceramic's by its dielectric class code (X7R and C0G -55 to +125 C, X5R -55 to +85 C);
  the stock against the five-kit need (rows on the board x 5): a part under it is a FINDING with an alternative.
The order of preference is rule I-1 (pcb_part_identities.yaml): the code the design already carries (lcsc_fill.py's MAP, else
the certified table, else the identity table's RESOLVED order code), then JLCPCB's basic library, then a preferred part, then a
maker whose own sheet is public (MAKER_TIER below), then the highest stock. Where the chosen part is a YAGEO CC X7R capacitor or
a UNI-ROYAL thick-film resistor, its identity is bound DECODED on the maker's ordering table by the identity tool's own rule D-2
reader (part_identities.read_binding); otherwise the identity is the catalogue line's, recorded DOCUMENT_OWED.

Nothing is reselected: ICs, modules, transistors, named inductors, connectors and mechanical parts are Layer 4's and earlier
selections; any of them without an LCSC field is listed as a FINDING (what its value names, if anything). A requirement the
generator and the intent leave open (a net with no bound, an RF inductor's unstated properties, a lamp's intensity) is a FINDING
with its line, never a guess.

Run from the repository root:  python3 v2/docs/records/l6r2/l6r2_passives.py > v2/docs/records/l6r2/l6r2_passives.out
  --identities         the block drafted_identities_l6r2_passives for pcb_part_identities.yaml
  --draft X            the text of the board-X apply draft (apply_gen_sch_X_lcsc.py)
  --write-drafts       write the six drafts beside this file (only this record's own files)
  --plan               the catalogue queries (codes and keywords) read_catalogue.py asks
Needs PyYAML and pdftotext (the identity tool's reader). Exit 2: a pinned input moved; 3: an input cannot be parsed; 4: a draft
does not compose."""
import ast
import collections
import difflib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tokenize
import csv
import importlib.util

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
TOOLS = os.path.join(TOP, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
import part_identities as PI  # noqa: E402

REC = "v2/docs/records/l6r2"
BOM_TOOL = REC + "/inputs/bom_from_netlist.py"
BOM_TOOL_FROM = dict(branch="fnd/int27", commit="e2a8df59801f6d41fe534209fd4e9cf5898635da",
                     path="v2/docs/handover/supplier/bom_from_netlist.py",
                     sha256="687c4acafacd96d22fa89dd6cd4786280f7aeb3548c3537ece3d5389ab906cc1")
CATALOGUE = REC + "/inputs/jlc-parts-2026-10-03.json"
LCSC_FILL = "v2/ecad/tools/lcsc_fill.py"
CERT = "v2/release/revA/order/JLC-CERTIFIED.tsv"
TABLE = "v2/ecad/tools/pcb_part_identities.yaml"
BLOCKED = "v2/ecad/tools/lcsc-blocked.txt"
MISMATCH = "v2/ecad/tools/jlc-mismatch.yaml"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
L4E9 = "v2/docs/records/l4e9/l4e9_power_path.py"
REGISTER = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
ORDER = ["a", "e", "p", "d", "c", "b"]
NAME = {"a": "A", "b": "B", "c": "C", "d": "D", "e": "E", "p": "P"}
GEN = {x: "v2/ecad/tools/gen_sch_%s.py" % x for x in ORDER}
NET = {b[0]: "v2/ecad/%s/out/%s.net" % (b[1], b[2]) for b in PI.BOARDS}
INTENT = {b[0]: "v2/ecad/%s/out/%s-intent.json" % (b[1], b[2]) for b in PI.BOARDS}
KITS = 5
AIR = (-20.0, 62.1)
# makers whose own datasheets are public on their own sites (rule I-1's MAKER_TIER), matched on the catalogue's brand text
MAKER_TIER = ("YAGEO", "SAMSUNG", "MURATA", "TDK", "UNI-ROYAL", "VISHAY", "PANASONIC", "KEMET", "WALSIN", "ROHM", "KOA", "BOURNS",
              "LITTELFUSE", "DIODES", "NEXPERIA", "ONSEMI", "SUNLORD", "WURTH", "TAIYO", "KYOCERA", "AVX")
# the dielectric class code's temperature range (the code is the range: first letter the cold end, the digit the hot end)
CLASS_RANGE = {"X7R": (-55, 125), "X7S": (-55, 125), "X8R": (-55, 150), "X5R": (-55, 85), "X6S": (-55, 105), "C0G": (-55, 125)}
# the pending drafts of each generator, in the order they apply: Layer 4's change list (L4-E9's cons_changes), then the drafts
# of the review of decision 31 (d8dec31) that the change list does not name; s117's two are already applied (both refuse)
D8 = "v2/docs/records/d8dec31"
STANDALONE = {"a": [D8 + "/apply_gen_sch_a_mainpb.py"], "e": [D8 + "/apply_gen_sch_e_pod.py"], "d": [D8 + "/apply_gen_sch_d_ptt.py"]}
D8_STYLE = (D8 + "/",)    # these take <generator> <netlist> and write unless --check

GENERIC_SEMI = re.compile(r"^(BAT54[A-Z]*|1N4148W?|SMBJ\d+(?:\.\d+)?C?A|SMAJ\d+(?:\.\d+)?C?A|BZT52C\d+(?:V\d)?)\b")
NOT_A_PART_LAND = re.compile(r"^(SolderJumper|SolderPad|LeadLands|PogoTargets)")


def sha256(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def die(code, msg):
    sys.stderr.write("l6r2_passives: %s\n" % msg); sys.exit(code)


def clean(s):
    t = {0x2013: "-", 0x2014: "-", 0x2212: "-", 0xB0: " ", 0x2103: "C", 0x3A9: "Ohm", 0xB5: "u", 0x3BC: "u", 0xB1: "+-", 0x2264: "<=",
         0x2265: ">=", 0x2019: "'", 0x2018: "'", 0x201C: '"', 0x201D: '"', 0x3001: "/", 0xA0: " ", 0xFF5E: "~"}
    return "".join(t.get(ord(ch), ch) if ord(ch) > 127 else ch for ch in str(s)).encode("ascii", "replace").decode("ascii")


# ------------------------------------------------------------------------------------------------ the design's own codes
def lcsc_fill_map():
    """lcsc_fill.py's MAP, read by parsing the file (it runs on import, so it is never imported)."""
    tree = ast.parse(open(os.path.join(TOP, LCSC_FILL), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "MAP" for t in n.targets):
            return ast.literal_eval(n.value)
    die(3, "lcsc_fill.py has no MAP")


def certified():
    out = {}
    for row in csv.DictReader(open(os.path.join(TOP, CERT), errors="replace"), delimiter="\t"):
        if (row.get("verdict") or "").strip() == "CERTIFIED" and (row.get("code") or "").strip():
            out.setdefault(((row.get("comment") or "").strip(), (row.get("fp") or "").strip()), row["code"].strip())
    return out


def refusals():
    """The codes this project has refused: lcsc-blocked.txt (a code, its replacement, an optional fp= land qualifier, the reason)
    and jlc-mismatch.yaml's declared mismatches (owner condition 1; a code, an optional comment_re and fp_contains). Read as
    lcsc_fill.py reads them; a refused code is never selected on a row it is refused for."""
    import yaml
    blocked = {}
    for line in open(os.path.join(TOP, BLOCKED), encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#"): continue
        f = line.split()
        if len(f) >= 2:
            fp = f[2][3:] if len(f) > 2 and f[2].startswith("fp=") else ""
            blocked[f[0]] = (fp, " ".join(f[3:] if fp else f[2:]))
    mm = (yaml.safe_load(open(os.path.join(TOP, MISMATCH), encoding="utf-8")) or {}).get("mismatches") or []
    return blocked, mm


def refused(code, value, land, REF):
    blocked, mm = REF
    if code in blocked and (not blocked[code][0] or blocked[code][0] in land):
        return "lcsc-blocked.txt: %s" % blocked[code][1]
    for e in mm:
        if e.get("code") != code: continue
        if e.get("comment_re") and not re.search(e["comment_re"], value): continue
        if e.get("fp_contains") and e["fp_contains"] not in land: continue
        return "jlc-mismatch.yaml %s: %s" % (e.get("id"), e.get("reason"))
    return None


def table():
    import yaml
    return yaml.safe_load(open(os.path.join(TOP, TABLE), encoding="utf-8"))


def design_code(value, land, MAP, CRT, tab_codes, key):
    """The code the design already carries for a row with no LCSC field, as the finish would fill it (lcsc_fill.py: MAP first,
    then the certified table), else the identity table's RESOLVED order code for the same selection key (board C, w5identc)."""
    for (vre, fsub), code in MAP.items():
        if re.match(vre, value) and fsub in land:
            return code, "lcsc_fill.py MAP (%s on %s)" % (vre, fsub)
    c = CRT.get((value.strip(), land.strip()))
    if c: return c, "the certified table JLC-CERTIFIED.tsv"
    if key in tab_codes: return tab_codes[key], "the identity table (w5identc), a RESOLVED selection"
    return None, None


# ------------------------------------------------------------------------------------------------ the selections
def classify(s):
    """The class of a selection: CAP, RES, FERRITE, LED, SEMI (a small diode of a generic type), or a finding class: OPEN (a
    generic part whose requirement is open), SPECIAL (not re-selected here), NOT_A_PART (copper: rule N-1)."""
    k, pre, req = s["kind"], s["prefix"], s["requirements"]
    land = (s["lands"] or [""])[0]
    val = (s["values"] or [""])[0]
    if NOT_A_PART_LAND.match(land):
        return "NOT_A_PART", "a land on the board itself (rule N-1): %s" % land
    if k == "capacitor":
        if req.get("construction") != "MLCC":
            return "SPECIAL", "a %s capacitor (not a generic part)" % req.get("construction")
        if req.get("v_open_on"):
            return "OPEN", "the rated voltage is open: no declared or bounded voltage on %s (rule V-1; never a guess)" % req.get("v_open_on")
        return "CAP", ""
    if k == "resistor":
        if req.get("link_current_min_a"):
            return "OPEN", "a link whose current rating (%s A) no catalogue line read states" % req.get("link_current_min_a")
        return "RES", ""
    if k == "inductor":
        ik = req.get("ind_kind")
        if ik == "ferrite bead": return "FERRITE", ""
        if req.get("named_part"):
            why = "names %s (a Layer 4 or earlier selection; Coilcraft parts are hand-fit, not in JLCPCB's catalogue)" % req.get("named_part")
            pm = re.search(r"XAL(\d{4})", str(req.get("named_part"))); lm = re.search(r"XAL(\d{4})", land)
            if pm and lm and pm.group(1) != lm.group(1):
                why += "; LAND: the part is an XAL%s and its land is drawn for the XAL%s (the two makers' land patterns are to be compared before layout)" % (pm.group(1), lm.group(1))
            return "SPECIAL", why
        return "OPEN", "a %s whose deciding properties beyond the inductance (tolerance, Q, self-resonance, current) the value does not state: %r" % (ik, val)
    if pre in ("D", "LED") and land.startswith("LED_0603"):
        return "LED", ""
    if pre in ("D", "LED") and land.startswith("LED_"):
        return "OPEN", "a panel lamp whose intensity and viewing angle through its light guide are not stated (w5identc: CHOICE_OWED)"
    if pre == "D" and GENERIC_SEMI.match(val):
        return "SEMI", ""
    return "SPECIAL", special_why(val, land)


MAKER_WORDS = ("TI", "Texas", "Omron", "NiceRF", "Hirose", "C&K", "APEM", "Ebyte", "Amphenol", "Preci-Dip", "Mill-Max", "Radiall", "Keystone",
               "Coilcraft", "Bourns", "NKK", "Floyd", "Quectel", "Arlitech", "JST", "Wurth", "Nexperia", "Diodes", "Littelfuse")
I3 = (("IDC-Header_2x13_P2.54mm_Vertical_SMD", "PROCUREMENT.md HC6-SC-7: XFCN BH254VS-26P (C48687640), rule I-3"),
      ("IDC-Header_2x13", "PROCUREMENT.md HC6-SC-7: Wurth WR-BHD 61202621621 (C17586777), rule I-3"),
      ("IDC-Header_2x08", "PROCUREMENT.md HC6-SC-7: Wurth WR-BHD 61201621621 (C5364137), rule I-3"),
      ("IDC-Header_2x05", "PROCUREMENT.md HC6-SC-7: Wurth WR-BHD 61201021621 (C4355000), rule I-3"),
      ("Mill-Max_0858", "PROCUREMENT.md HC6-SC-8: Mill-Max 0858-0-15-20-82-14-11-0 (hand-fit, no LCSC code; J_PRE1's longer pin NOT_PINNED), rule I-3"))


def _quantity(t):
    """A token that is a quantity (0.5A, 24MHz, 12AWG), not a part number: digits, an optional decimal part, then letters only."""
    m = re.match(r"\d+(\.\d+)?", t)
    return bool(m) and t[m.end():].isalpha()


def special_why(val, land):
    """What a special part's value or land names (never a selection): a part chosen on a page of record (rule I-3), a maker's
    part number in the value (with the maker word before it when there is one), a class, or nothing a part can be bought by."""
    for lp, why in I3:
        if land.startswith(lp):
            return "an identity chosen on a page of record: %s; the netlist carries no code (the generator owner writes it)" % why
    for rx, maker in PI.NAMED:
        m = rx.search(val)
        if m: return "names %s %s" % (maker, m.group(1))
    toks = [t.rstrip(".,;:") for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9.\-/#&]*", val)]
    for i, t in enumerate(toks[:-1]):
        # a maker's word followed by its part number (Keystone 3034, NiceRF SA868, Amphenol RJHSE5380)
        if t in MAKER_WORDS and re.search(r"\d{3}", toks[i + 1]) and not _quantity(toks[i + 1]):
            return "names %s %s; no LCSC code in the netlist" % (t, toks[i + 1])
    lm = re.search(r"JST_XH_(B\d+B-XH-A)", land)
    if lm:
        return "its land names JST %s; no LCSC code in the netlist" % lm.group(1)
    for i, t2 in enumerate(toks):
        designator = re.fullmatch(r"[A-Z]{1,2}_?\d{1,2}", t2)          # a pin, a net or a designator the value names (IO23, S1)
        if len(t2) >= 5 and len(re.findall(r"\d", t2)) >= 2 and re.search(r"[A-Za-z]", t2) and not _quantity(t2) and not designator:
            mk = next((w for w in toks[max(0, i - 2):i] if w in MAKER_WORDS), None)
            cls_ = " (a CLASS: the value says so)" if re.search(r"\bclass\b", val) else ""
            return "names %s%s%s; no LCSC code in the netlist" % (("%s " % mk) if mk else "the part number ", t2, cls_)
    return "names no part by number (what it connects to, a class or a function); no identity"


def plan_board(letter, MAP=None, CRT=None, TAB=None):
    """The selections of one board's uncoded fitted rows, classified, with the design's code and the catalogue keywords."""
    MAP = MAP if MAP is not None else lcsc_fill_map()
    CRT = CRT if CRT is not None else certified()
    TAB = TAB if TAB is not None else table()
    tab_codes = {}
    for s in TAB.get("selections") or []:
        oc = s.get("order_code") or {}
        if s["identity"].get("status") == "RESOLVED" and oc.get("code"):
            tab_codes[s["key"]] = oc["code"]
    rs, meta = PI.rows(boards=[letter])
    unc = [p for p in rs if not p["generator_lcsc"]]
    sels = PI.selections(unc)
    out = []
    for key, s in sels.items():
        d = dict(sid=PI.selection_id(key), board=letter, key=key, kind=s["kind"], prefix=s["prefix"],
                 refs=sorted(s["rows"], key=_nat), values=sorted(s["values"]), lands=sorted(s["lands"]),
                 requirements=dict(s["requirements"]), basis={k: sorted(v) for k, v in s["basis"].items()})
        d["refs"] = [r.split(":", 1)[1] for r in d["refs"]]
        d["cls"], d["why"] = classify(d)
        codes = set()
        for v in d["values"]:
            for l in d["lands"]:
                c, how = design_code(v, l, MAP, CRT, tab_codes, key)
                if c: codes.add((c, how))
        d["design"] = sorted(codes)[0] if codes else None
        d["design_codes"] = sorted(codes)
        d["keywords"] = keywords(d)
        out.append(d)
    out.sort(key=lambda d: (["CAP", "RES", "FERRITE", "LED", "SEMI", "OPEN", "SPECIAL", "NOT_A_PART"].index(d["cls"]), _nat(d["refs"][0])))
    return out, rs, meta


def _nat(ref):
    m = re.match(r"([A-Za-z_]+)(\d+)(.*)", ref)
    return (m.group(1), int(m.group(2)), m.group(3)) if m else (ref, 0, "")


# ------------------------------------------------------------------------------------------------ values and keywords
def farads(s):
    m = re.search(r"([\d.]+)\s*([pnuµm]?)F", str(s))
    if not m: return None
    return float(m.group(1)) * {"p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3, "": 1.0}[m.group(2)]


def ohms(s):
    s = str(s)
    m = re.search(r"([\d.]+)\s*([mkMG]?)(?:Ohm|Ω)", s)
    if not m: return None
    return float(m.group(1)) * {"m": 1e-3, "k": 1e3, "M": 1e6, "G": 1e9, "": 1.0}[m.group(2)]


def fmt_cap(f):
    for u, k in (("pF", 1e-12), ("nF", 1e-9), ("uF", 1e-6)):
        if f < k * 1000 - 1e-18: return "%g%s" % (round(f / k, 4), u)
    return "%guF" % (f / 1e-6)


def fmt_res(r):
    if r == 0: return "0Ω"
    for u, k in (("m", 1e-3), ("", 1.0), ("k", 1e3), ("M", 1e6)):
        if r < k * 1000 - 1e-12: return "%g%sΩ" % (round(r / k, 4), u)
    return "%gMΩ" % (r / 1e6)


def keywords(d):
    req, cls = d["requirements"], d["cls"]
    pkg = req.get("package") or ""
    if cls == "CAP":
        f = farads(req.get("value"))
        diel = req.get("dielectric")
        out = ["%s %s %s" % (pkg, fmt_cap(f), diel)]
        if (req.get("v_rating_min") or 0) >= 25:
            out.append("%s %s %gV %s" % (pkg, fmt_cap(f), req["v_rating_min"], diel))
        if diel == "X7R" and f >= 1e-6 - 1e-12:
            out.append("%s %s X5R" % (pkg, fmt_cap(f)))     # rule C-D3b's fallback, read only where it is used
        return out
    if cls == "RES":
        r = ohms(req.get("value"))
        return ["%s %s" % (fmt_res(r), pkg)] if r is not None else []
    if cls == "FERRITE":
        m = re.search(r"(\d+)\s*R", str(req.get("value") or d["values"][0]))
        land = (d["lands"] or [""])[0]
        p = re.search(r"_(\d{4})_", land)
        return ["%s %sΩ@100MHz" % (p.group(1) if p else "", m.group(1))] if m else []
    if cls == "SEMI":
        return [GENERIC_SEMI.match(d["values"][0]).group(1)]
    return []


# ------------------------------------------------------------------------------------------------ the catalogue and the checks
def attrs(row):
    return {a: v for a, v in (row.get("attributes") or {}).items()}


def _num(rx, s, scale=None):
    m = re.search(rx, str(s or ""))
    if not m: return None
    v = float(m.group(1))
    return v * scale[m.group(2)] if scale else v


def parse_tol(s): return _num(r"±\s*([\d.]+)\s*%", s)
def parse_volt(s): return _num(r"([\d.]+)\s*(kV|V)\b", s, {"kV": 1000.0, "V": 1.0})
def parse_ppm(s): return _num(r"±?\s*([\d.]+)\s*ppm", s)


def parse_power(s):
    s = str(s or "")
    m = re.search(r"(\d+)\s*/\s*(\d+)\s*W", s)
    if m: return float(m.group(1)) / float(m.group(2))
    return _num(r"([\d.]+)\s*(mW|W)\b", s, {"mW": 1e-3, "W": 1.0})


def parse_temp(s):
    m = re.search(r"(-?\d+)\s*℃?\s*~\s*\+?(-?\d+)\s*℃", str(s or ""))
    return (float(m.group(1)), float(m.group(2))) if m else None


def diel_of(s):
    s = str(s or "").upper()
    for d in ("C0G", "NP0", "X7R", "X7S", "X8R", "X5R", "X6S", "Y5V", "X7T"):
        if d in s: return "C0G" if d == "NP0" else d
    return None


# A maker's series sheet held in the tree supplies a property the catalogue line does not print (MAKER basis, the page read here):
# (brand, model prefix, document, page, the phrases the page must print, the facts, the value range in ohms they hold for)
SERIES_FACTS = [
    ("MILLIOHM", "HoJLR2512", "v2/vendor/passives/milliohm-hojlr2512-series.pdf", 2,
     ("\u00b150 (2mR~500mR)", "Operating Temperature Range -50\u2103~+170\u2103"),
     {"Temperature Coefficient": "\u00b150ppm/\u2103", "Operating Temperature": "-50\u2103~+170\u2103"}, (0.002, 0.5)),
]


def with_series_facts(row):
    """The catalogue line with the properties a held maker's series sheet prints where the line prints none; each supplied
    property named in row['maker_facts'] with its page. Refuses (exit 4) when the page does not print the phrase."""
    a = dict(row.get("attributes") or {})
    used = []
    for brand, prefix, doc, page, phrases, facts, rng in SERIES_FACTS:
        if brand not in (row.get("brand") or "").upper() or not (row.get("model") or "").startswith(prefix): continue
        r = ohms(a.get("Resistance"))
        if r is None or not (rng[0] - 1e-12 <= r <= rng[1] + 1e-12): continue
        text = " ".join(PI.page_text(os.path.join(TOP, doc), page).split())
        for ph in phrases:
            if " ".join(ph.split()) not in text: die(4, "%s p.%d does not print %r" % (doc, page, ph))
        for k, v in facts.items():
            if not a.get(k) or a.get(k) == "-":
                a[k] = v; used.append("%s from %s p.%d" % (k, doc, page))
    if not used: return row
    out = dict(row); out["attributes"] = a; out["maker_facts"] = used
    return out


def check(d, row):
    """Every deciding property of the selection against the catalogue line. Returns (ok, lines, grade) where each line is
    (property, required, read, verdict) and grade is (lo, hi, basis) or None."""
    req, cls = d["requirements"], d["cls"]
    row = with_series_facts(row)
    a = attrs(row)
    L, grade = [], None
    pkg = row.get("package") or ""

    def need(prop, required, read, ok):
        L.append((prop, required, read, "MEETS" if ok else ("NOT READ" if read in (None, "") else "FAILS")))

    if cls in ("CAP", "RES", "FERRITE"):
        need("package", req.get("package") or (d["lands"][0]), pkg, bool(req.get("package")) and pkg == req.get("package")
             or (cls == "FERRITE" and pkg and pkg in (d["lands"][0])))
    if cls == "CAP":
        f, fr = farads(req.get("value")), farads(a.get("Capacitance"))
        need("capacitance", req.get("value"), a.get("Capacitance"), f is not None and fr is not None and abs(fr - f) <= 1e-6 * f)
        v = parse_volt(a.get("Voltage Rating"))
        need("rated voltage", "%g V or more" % req["v_rating_min"], a.get("Voltage Rating"), v is not None and v + 1e-9 >= float(req["v_rating_min"]))
        dl = diel_of(a.get("Temperature Coefficient"))
        acc = PI.DIELECTRIC_ACCEPTS.get(req.get("dielectric"), (req.get("dielectric"),))
        need("dielectric", "%s (accepts %s)" % (req.get("dielectric"), "/".join(acc)), a.get("Temperature Coefficient"), dl in acc)
        t = parse_tol(a.get("Tolerance"))
        need("tolerance", "%g %% or tighter" % req["tolerance_max_pct"], a.get("Tolerance"), t is not None and t <= float(req["tolerance_max_pct"]) + 1e-9)
        mlcc = "Multilayer Ceramic" in (row.get("describe") or "") + (row.get("sort") or "")
        need("construction", "MLCC", "multilayer ceramic" if mlcc else (row.get("sort") or ""), mlcc)
        if dl in CLASS_RANGE:
            lo, hi = CLASS_RANGE[dl]; grade = (lo, hi, "the dielectric class code %s (its range is the code)" % dl)
    elif cls == "RES":
        r, rr = ohms(req.get("value")), ohms(a.get("Resistance"))
        need("resistance", req.get("value"), a.get("Resistance"), r is not None and rr is not None and (abs(rr - r) <= 1e-6 * max(r, 1e-9) or (r == 0 and rr == 0)))
        if req.get("resistor_kind") != "zero-ohm link":
            t = parse_tol(a.get("Tolerance"))
            need("tolerance", "%g %% or tighter" % req["tolerance_max_pct"], a.get("Tolerance"), t is not None and t <= float(req["tolerance_max_pct"]) + 1e-9)
        p = parse_power(a.get("Power(Watts)"))
        need("power", "%g W or more" % req["power_min_w"], a.get("Power(Watts)"), p is not None and p + 1e-12 >= float(req["power_min_w"]))
        if req.get("tcr_max_ppm"):
            c = parse_ppm(a.get("Temperature Coefficient"))
            need("temperature coefficient", "%d ppm/K or less" % req["tcr_max_ppm"], a.get("Temperature Coefficient"), c is not None and c <= req["tcr_max_ppm"] + 1e-9)
        tr = parse_temp(a.get("Operating Temperature"))
        if tr: grade = (tr[0], tr[1], "the catalogue line's operating temperature")
    elif cls == "FERRITE":
        m = re.search(r"(\d+)\s*R", d["values"][0]); want = float(m.group(1)) if m else None
        imp = _num(r"([\d.]+)\s*Ω\s*@\s*100\s*MHz", a.get("Impedance @ Frequency"))
        need("impedance at 100 MHz", "%g Ohm" % want if want else None, a.get("Impedance @ Frequency"), want is not None and imp is not None and abs(imp - want) < 1e-6)
        if req.get("current_min_a"):
            ca = _num(r"([\d.]+)\s*(mA|A)\b", a.get("Current Rating"), {"mA": 1e-3, "A": 1.0})
            need("current rating", "%g A or more" % req["current_min_a"], a.get("Current Rating"), ca is not None and ca + 1e-9 >= req["current_min_a"])
        tr = parse_temp(a.get("Operating Temperature"))
        if tr: grade = (tr[0], tr[1], "the catalogue line's operating temperature")
    elif cls == "SEMI":
        tok = GENERIC_SEMI.match(d["values"][0]).group(1)
        model = row.get("model") or ""
        need("type", tok, model, model.upper().startswith(tok.upper()))
        land = d["lands"][0]
        want = {"D_SOD-123": ("SOD-123",), "D_SMB": ("SMB", "DO-214AA"), "D_SMC": ("SMC", "DO-214AB"), "D_SOD-323": ("SOD-323",),
                "D_SMA": ("SMA", "DO-214AC")}.get(land.split("_P")[0], ())
        need("package (the land %s)" % land, "/".join(want), pkg, any(w in pkg for w in want) and not any(x in pkg for x in ("SOD-123F", "SOD-123FL")) if want else False)
        tr = parse_temp(a.get("Operating Temperature") or row.get("describe"))
        if tr: grade = (tr[0], tr[1], "the catalogue line's operating temperature")
    elif cls == "LED":
        need("package", "0603", pkg, "0603" in pkg)
        txt = (row.get("describe") or "") + " " + (row.get("sort") or "")
        need("kind", "an LED", clean(txt)[:60], "LED" in txt or "Light Emitting" in txt)
        col = re.match(r"^(green|red|blue|amber|yellow|white)\b", d["values"][0], re.I)
        rc = " ".join(str(v) for k, v in a.items() if "olor" in k)
        if col:
            need("colour", col.group(1).lower(), rc, col.group(1).lower() in rc.lower() or (col.group(1).lower() == "amber" and ("yellow" in rc.lower() or "orange" in rc.lower() or "amber" in rc.lower())))
        else:
            L.append(("colour", "not stated by the value (lcsc_fill.py's MAP takes green)", rc, "MEETS" if "green" in rc.lower() else "NOT READ"))
        tr = parse_temp(a.get("Operating Temperature") or row.get("describe"))
        if tr: grade = (tr[0], tr[1], "the catalogue line's operating temperature")
    ok = all(x[3] == "MEETS" for x in L) and bool(L)
    return ok, L, grade


def grade_verdict(g):
    if not g: return "NOT READ"
    lo, hi = g[0], g[1]
    if lo < AIR[0] and hi > AIR[1]: return "INSIDE"
    if lo <= AIR[0] and hi >= AIR[1]: return "AT_LIMIT"
    return "OUTSIDE"


def maker_tier(brand):
    b = (brand or "").upper()
    return any(m in b for m in MAKER_TIER)


def choose(d, cat):
    """Rule I-1 over the catalogue lines read for this selection: the eligible ones (every requirement met, stock for five kits)
    ranked by the design's own code, the basic library, a preferred part, MAKER_TIER, then stock. Returns a dict."""
    need = len(d["refs"]) * KITS
    cands = {}
    for c, _how in d["design_codes"]:
        if c in cat["codes"]: cands[c] = cat["codes"][c]
    for kw in d["keywords"]:
        for r in cat["searches"].get(kw, {}).get("rows", []):
            cands.setdefault(r["code"], r)
    design = {c for c, _ in d["design_codes"]}
    judged = []
    REF = cat.get("_refusals")
    for c, r in cands.items():
        ok, lines, grade = check(d, r)
        why = refused(c, d["values"][0], d["lands"][0], REF) if REF else None
        if why:
            lines = lines + [("the project's refusals", "not refused", why, "FAILS")]; ok = False
        judged.append(dict(code=c, row=r, ok=ok, lines=lines, grade=grade, stock=r.get("stock") or 0, design=c in design))
    def rank(j):
        r = j["row"]
        return (not j["design"], r.get("lib") != "base", not r.get("preferred"), not maker_tier(r.get("brand")), -(j["stock"]), j["code"])
    elig = sorted([j for j in judged if j["ok"] and j["stock"] >= need], key=rank)
    okl = sorted([j for j in judged if j["ok"]], key=rank)
    res = dict(need=need, judged=len(judged), design_judged=[j for j in judged if j["design"]])
    if elig:
        res["pick"] = elig[0]
        alt = [j for j in elig[1:] if (j["row"].get("brand") or "") != (elig[0]["row"].get("brand") or "")] or elig[1:]
        res["alt"] = alt[0] if alt else None
        res["state"] = "SELECTED"
    elif okl:
        res["pick"] = okl[0]; res["alt"] = None; res["state"] = "LOW_STOCK"
    elif d["cls"] == "CAP" and d["requirements"].get("dielectric") == "X7R" and not d.get("c_d3b"):
        # rule C-D3b: where no X7R part is made or stocked at the value, land and rating, X5R is taken and the hot-spot question
        # is recorded OPEN on the selection
        d2 = dict(d); d2["requirements"] = dict(d["requirements"], dielectric="X5R"); d2["c_d3b"] = True
        res2 = choose(d2, cat)
        if res2.get("pick") and res2["state"] in ("SELECTED", "LOW_STOCK"):
            res2["c_d3b"] = "rule C-D3b: no X7R line read meets the value, land and rating with stock; an X5R part is taken and the hot-spot question is OPEN"
            res2["design_judged"] = res["design_judged"]
            return res2
        res["pick"] = None; res["alt"] = None; res["state"] = "NO_MATCH"
        near = sorted(judged, key=lambda j: (sum(1 for x in j["lines"] if x[3] != "MEETS"), -(j["stock"])))
        res["near"] = near[0] if near else None
    else:
        res["pick"] = None; res["alt"] = None; res["state"] = "NO_MATCH"
        near = sorted(judged, key=lambda j: (sum(1 for x in j["lines"] if x[3] != "MEETS"), -(j["stock"])))
        res["near"] = near[0] if near else None
    return res


def price_at(row, qty):
    pr = row.get("prices") or []
    if not pr: return None, None
    first = pr[0]["price"]
    at = next((p["price"] for p in pr if p["from"] <= qty <= (p["to"] if (p["to"] or 0) > 0 else 10 ** 9)), pr[-1]["price"])
    return first, at


# ------------------------------------------------------------------------------------------------ DECODED bindings
YAGEO_DOC = "v2/vendor/passives/yageo-cc-series.pdf"
UNIROYAL_DOC = "v2/vendor/passives/held/uniroyal-series-11cd644d.pdf"
_UNI_TEMPLATE = None


def _uniroyal_template(TAB):
    for s in TAB.get("selections") or []:
        ds = s["identity"].get("datasheet") or {}
        if ds.get("scheme") == "uniroyal-thick-film-p2":
            return {k: v for k, v in ds.items() if k not in ("established", "not_established")}
    return None


YAGEO_ROWS = {"size": {"0201": "0201 (0603)", "0402": "0402 (1005)", "0603": "0603 (1608)", "0805": "0805 (2012)", "1206": "1206 (3216)",
                       "1210": "1210 (3225)", "1812": "1812 (4532)", "2220": "2220 (5750)"},
              "tolerance": {"J": ("J = ± 5% (1)", "± 5%"), "K": ("K = ± 10%", "± 10%"), "M": ("M = ± 20%", "± 20%")},
              "packaging": {"R": ("R = Paper/PE taping reel; Reel 7 inch", "Paper/PE taping reel"), "K": ("K = Blister taping reel; Reel 7 inch", "Blister taping reel"),
                            "P": ("P = Paper/PE taping reel; Reel 13 inch", "Paper/PE taping reel"), "F": ("F = Blister taping reel; Reel 13 inch", "Blister taping reel")},
              "voltage": {"5": ("5 = 6.3 V", "6.3 V"), "6": ("6 = 10 V", "10 V"), "7": ("7 = 16 V", "16 V"), "8": ("8 = 25 V", "25 V"),
                          "9": ("9 = 50 V", "50 V"), "0": ("0 = 100 V", "100 V"), "A": ("A = 200 V", "200 V"), "Y": ("Y = 250 V", "250 V")}}


def decoded_binding(model, brand, kind, TAB):
    """A DECODED binding for a YAGEO CC ... X7R ... BB ... capacitor or a UNI-ROYAL thick-film resistor, built from the maker's
    ordering table's own rows (the page the identity tool's SCHEMES pin); read_binding then judges it. None when the part is
    neither family or a position's code has no row."""
    b = (brand or "").upper()
    if kind == "capacitor" and "YAGEO" in b:
        m = re.fullmatch(r"CC(\d{4})([JKM])([RKPF])X7R([0-9AY])BB(\d{2}[0-9R])", model or "")
        if not m: return None
        size, tol, pk, vc, val = m.groups()
        if size not in YAGEO_ROWS["size"] or vc not in YAGEO_ROWS["voltage"]: return None
        f = [dict(field="series", code="CC"), dict(field="size", code=size, row=YAGEO_ROWS["size"][size]),
             dict(field="tolerance", code=tol, row=YAGEO_ROWS["tolerance"][tol][0], means=YAGEO_ROWS["tolerance"][tol][1]),
             dict(field="packaging", code=pk, row=YAGEO_ROWS["packaging"][pk][0], means=YAGEO_ROWS["packaging"][pk][1]),
             dict(field="dielectric", code="X7R"),
             dict(field="voltage", code=vc, row=YAGEO_ROWS["voltage"][vc][0], means=YAGEO_ROWS["voltage"][vc][1]),
             dict(field="process", code="BB"),
             dict(field="value", code=val, rule="pf_2sig", row="2 significant digits+number of zeros")]
        return dict(binding="DECODED", scheme="yageo-cc-x7r-v26-p2", path=YAGEO_DOC, page=2, publisher="YAGEO",
                    table="YAGEO product specification, Surface-Mount Ceramic Multilayer Capacitors, General Purpose & High Cap., X7R 6.3 V to 250 V, V.26 of 19 November 2024: ORDERING INFORMATION, GLOBAL PART NUMBER",
                    sha256=PI.SCHEMES["yageo-cc-x7r-v26-p2"]["sha256"], fields=f)
    if kind == "resistor" and "UNI-ROYAL" in b:
        tpl = _uniroyal_template(TAB)
        m = re.fullmatch(r"(0603)(WA)([FJ])(\d{3}[0-9JKL])(T)(5)(E)", model or "") or re.fullmatch(r"(1206)(W4)([FJ])(\d{3}[0-9JKL])(T)(5)(E)", model or "")
        if not (tpl and m): return None
        size, pw, tol, val, pk, q, sp = m.groups()
        f = []
        for fld in tpl["fields"]:
            g = dict(fld)
            if g["field"] == "size": g["code"] = size
            elif g["field"] == "power": g["code"] = pw; g["means"] = {"WA": "1/10W", "W4": "1/4W"}[pw]
            elif g["field"] == "tolerance": g["code"] = tol; g["means"] = {"F": "±1%", "J": "±5%"}[tol]
            elif g["field"] == "value": g["code"] = val
            f.append(g)
        out = dict(tpl); out["fields"] = f
        return out
    return None


def bind(model, brand, d, TAB):
    """(binding, state, why): the DECODED binding judged by part_identities.read_binding on the requirement the identity tool
    derives (its _judged form), or (None, 'NONE', why)."""
    ds = decoded_binding(model, brand, d["kind"], TAB)
    if not ds: return None, "NONE", "no maker's ordering table in the tree decodes %s (%s)" % (model, brand)
    r = PI.read_binding(ds, model, root=TOP, maker=brand, req=PI._judged(d["requirements"]), kind=d["kind"])
    return ds, r["state"], r.get("why")


# ------------------------------------------------------------------------------------------------ the drafts and their composition
ANCHOR = "import schlayout, time as _time\n"
MARK = "# LAYER 6 RECORD l6r2 (MESHSAT-1357"


def change_chain(board):
    """The pending Layer 4 drafts of this board's generator in their application order (L4-E9's change list)."""
    sp = importlib.util.spec_from_file_location("l6r2_l4e9pp", os.path.join(TOP, L4E9))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    reg = m.md_table(open(os.path.join(TOP, REGISTER), encoding="utf-8").read(), "| ID | Kind |")
    out = []
    for c in m.cons_changes(reg):
        if c[1] == "ALT": continue
        for s in [x.strip() for x in c[4].split(",")]:
            if not s.startswith("apply_gen_sch_%s_" % board): continue
            hits = [p for p in m.CHANGE_SCRIPTS if p.endswith("/" + s)]
            for h in hits:
                rel = "v2/docs/records/" + h
                if rel not in out: out.append(rel)
    return out


def run_draft(rel, target, net):
    if rel.startswith(D8_STYLE):
        args = [sys.executable, "-B", os.path.join(TOP, rel), target, net]
    else:
        args = [sys.executable, "-B", os.path.join(TOP, rel), target, "--write"]
    r = subprocess.run(args, cwd=os.path.dirname(target), capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]


def compose(board, entries):
    """Commutation: the chain (and each standalone draft) then this draft gives the same text as this draft then the chain."""
    import l6r2_apply
    gen0 = open(os.path.join(TOP, GEN[board]), encoding="utf-8").read()
    chain = change_chain(board)
    res = dict(chain=chain, standalone=STANDALONE.get(board, []), ok=True, notes=[])
    with tempfile.TemporaryDirectory(prefix="l6r2-") as td:
        net = os.path.join(td, "board.net"); shutil.copyfile(os.path.join(TOP, NET[board]), net)

        def apply_list(text, drafts):
            p = os.path.join(td, "gen_sch_%s.py" % board)
            open(p, "w", encoding="utf-8").write(text)
            for rel in drafts:
                rc, last = run_draft(rel, p, net)
                if rc != 0: return None, "%s refused: %s" % (rel, last[0][:160])
            return open(p, encoding="utf-8").read(), None

        def mine(text):
            st, new, why = l6r2_apply.apply_text(text, board, entries)
            return new if st == "OK" else None

        for drafts in ([chain] if chain else []) + [[s] for s in res["standalone"]]:
            a, err = apply_list(gen0, drafts)
            if a is None: res["ok"] = False; res["notes"].append("the other drafts alone: %s" % err); continue
            am = mine(a)
            b0 = mine(gen0)
            b, err2 = apply_list(b0, drafts) if b0 is not None else (None, "this draft refused the bare generator")
            same = am is not None and b is not None and am == b
            if am is not None: ast.parse(am)
            res["notes"].append("%s: %s" % (" then ".join(os.path.basename(x) for x in drafts),
                                              "commutes with this draft (identical text either order, sha256 %s)" % hashlib.sha256(am.encode()).hexdigest()[:16]
                                              if same else "DOES NOT COMMUTE (%s)" % (err2 or "the texts differ")))
            res["ok"] = res["ok"] and same
            if drafts is chain:
                res["touched"] = touched_refs(gen0, a)
        if not chain and not res["standalone"]:
            b0 = mine(gen0); res["ok"] = b0 is not None
            if b0 is not None: ast.parse(b0)
            res["notes"].append("no other pending draft names this generator: this draft applies to the bare generator (ast parses)" if b0 else "REFUSED on the bare generator")
            res["touched"] = set()
    return res


PART_CALLS = ("r", "c", "ic", "part", "nfet", "pfet", "tvs", "esd", "l", "fb", "led", "d", "q")


def touched_refs(old, new):
    """The designators whose part call a draft chain changes: on each changed line (a unified diff), the string literal that is the
    FIRST argument of a part call (r(, c(, ic(, part(, nfet(, ...), read by tokenize and never by a grep of prose; an LCSC code or a
    designator in a comment is never taken."""
    refs = set()
    rx = re.compile(r"^[A-Z][A-Z_]*\d+[A-Z]?$")
    for line in difflib.unified_diff(old.splitlines(), new.splitlines(), lineterm="", n=0):
        if not line or line[0] not in "+-" or line.startswith(("+++", "---")): continue
        try:
            toks = [t for t in tokenize.generate_tokens(io.StringIO(line[1:].strip() + "\n").readline)
                    if t.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT, tokenize.INDENT, tokenize.DEDENT)]
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue
        for i in range(len(toks) - 2):
            if toks[i].type == tokenize.NAME and toks[i].string in PART_CALLS and toks[i + 1].string == "(" and toks[i + 2].type == tokenize.STRING:
                try:
                    v = ast.literal_eval(toks[i + 2].string)
                except Exception:
                    continue
                if isinstance(v, str) and rx.match(v): refs.add(v)
    return refs


# ------------------------------------------------------------------------------------------------ the whole computation
def load_catalogue():
    p = os.path.join(TOP, CATALOGUE)
    if not os.path.exists(p): die(3, "the catalogue reading %s is not in the tree: run read_catalogue.py" % CATALOGUE)
    return json.load(open(p, encoding="utf-8"))


def compute():
    MAP, CRT, TAB = lcsc_fill_map(), certified(), table()
    cat = load_catalogue()
    cat["_refusals"] = refusals()
    boards = collections.OrderedDict()
    for b in ORDER:
        sels, rs, meta = plan_board(b, MAP, CRT, TAB)
        for d in sels:
            if d["cls"] in ("CAP", "RES", "FERRITE", "SEMI", "LED"):
                if d["cls"] == "LED" and not d["design"]:
                    d["choice"] = dict(state="NO_MATCH", pick=None, alt=None, need=len(d["refs"]) * KITS, judged=0, design_judged=[])
                    continue
                d["choice"] = choose(d, cat)
                pk = d["choice"].get("pick")
                if pk and d["choice"]["state"] != "NO_MATCH":
                    ds, st, why = bind(pk["row"].get("model"), pk["row"].get("brand"), d, TAB) if d["cls"] in ("CAP", "RES") else (None, "NONE", "not a capacitor or resistor family")
                    d["binding"] = (ds, st, why)
        boards[b] = dict(sels=sels, rows=rs, meta=meta)
    return boards, cat, TAB


def entries_for(board, B):
    """The draft's table: designator -> (the committed value, the selected code), for every SELECTED or LOW_STOCK pick."""
    out = {}
    rows = {p["ref"]: p for p in B[board]["rows"]}
    for d in B[board]["sels"]:
        ch = d.get("choice") or {}
        if ch.get("pick") and ch.get("state") in ("SELECTED", "LOW_STOCK"):
            for r in d["refs"]:
                out[r] = (rows[r]["value"], ch["pick"]["code"])
    return dict(sorted(out.items(), key=lambda kv: _nat(kv[0])))


def bom_tool_counts():
    out = {}
    with tempfile.TemporaryDirectory(prefix="l6r2-bom-") as td:
        for b in ORDER:
            o = os.path.join(td, "%s.csv" % b)
            r = subprocess.run([sys.executable, "-B", os.path.join(TOP, BOM_TOOL), os.path.join(TOP, NET[b]), "HEAD", o], capture_output=True, text=True)
            if r.returncode != 0: die(3, "bom_from_netlist.py refused %s: %s" % (NET[b], r.stderr[-200:]))
            m = re.search(r"(\d+) references in (\d+) lines, (\d+) without an LCSC field", r.stdout)
            out[b] = tuple(int(x) for x in m.groups())
    return out


def findings(B, comp):
    F = []
    for b in ORDER:
        for d in B[b]["sels"]:
            ch = d.get("choice")
            refs = ", ".join(d["refs"][:8]) + (" (+%d)" % (len(d["refs"]) - 8) if len(d["refs"]) > 8 else "")
            if d["cls"] in ("OPEN", "SPECIAL"):
                F.append((b, "OPEN REQUIREMENT" if d["cls"] == "OPEN" else "SPECIAL PART WITHOUT A CODE", refs, d["values"][0], d["why"]))
            if ch:
                if ch.get("c_d3b"):
                    F.append((b, "RULE C-D3b: X5R TAKEN, THE HOT-SPOT QUESTION OPEN", refs, d["values"][0], "%s %s; %s" % (ch["pick"]["code"], ch["pick"]["row"].get("model"), ch["c_d3b"])))
                if ch["state"] == "LOW_STOCK":
                    F.append((b, "STOCK UNDER THE FIVE-KIT NEED", refs, d["values"][0], "%s %s reads %s against a need of %d; no line read meets every requirement with that stock" % (
                        ch["pick"]["code"], ch["pick"]["row"].get("model"), ch["pick"]["stock"], ch["need"])))
                if ch["state"] == "NO_MATCH":
                    nr = ch.get("near")
                    F.append((b, "NO CATALOGUE LINE READ MEETS THE REQUIREMENT", refs, d["values"][0], ("nearest %s %s: %s" % (
                        nr["code"], nr["row"].get("model"), "; ".join("%s %s (read %s)" % (x[0], x[3], x[2]) for x in nr["lines"] if x[3] != "MEETS"))) if nr else "nothing read (no keyword)"))
                for j in ch.get("design_judged", []):
                    if not j["ok"]:
                        F.append((b, "THE DESIGN'S OWN CODE FAILS A REQUIREMENT", refs, d["values"][0], "%s %s (%s): %s" % (
                            j["code"], j["row"].get("model"), d["design"][1] if d["design"] else "", "; ".join("%s %s, read %s" % (x[0], x[3], x[2]) for x in j["lines"] if x[3] != "MEETS"))))
                if ch.get("pick") and ch["state"] != "NO_MATCH":
                    gv = grade_verdict(ch["pick"]["grade"])
                    if gv != "INSIDE":
                        F.append((b, "GRADE %s" % gv, refs, d["values"][0], "%s %s: %s" % (ch["pick"]["code"], ch["pick"]["row"].get("model"), ch["pick"]["grade"])))
    for b in ORDER:
        tol = [d for d in B[b]["sels"] if (d.get("choice") or {}).get("state") in ("SELECTED", "LOW_STOCK")
               and any("unstated" in x for x in d["basis"].get("tolerance_max_pct", []))]
        if tol:
            F.append((b, "TOLERANCE NOT STATED BY THE GENERATOR", "%d selections, %d rows" % (len(tol), sum(len(d["refs"]) for d in tol)), "",
                      "each takes rule C-T's or R-T1's default (C0G 5 %%, class 2 10 %% or 20 %%, a resistor 5 %%), which the selected part meets; the "
                      "generator owner states the tolerance where the circuit needs another: %s" % ", ".join("%s (%s)" % (d["sid"], ",".join(d["refs"][:3]) + ("+" if len(d["refs"]) > 3 else "")) for d in tol)))
        der = [d for d in B[b]["sels"] if (d.get("choice") or {}).get("state") in ("SELECTED", "LOW_STOCK") and d["cls"] == "CAP"
               and any(x.startswith("derived") for x in d["basis"].get("v_rating_min", []))]
        if der:
            F.append((b, "VOLTAGE NOT STATED BY THE GENERATOR, DERIVED FROM THE INTENT", "%d selections, %d rows" % (len(der), sum(len(d["refs"]) for d in der)), "",
                      "rule V-1: the voltage across each from the board's intent (DECLARED) or its nets' bound (BOUND) at the 20 percent margin; the "
                      "derivation is the requirement, not a guess (each selection's basis line in section 2)"))
    for b in ORDER:
        if not comp[b]["ok"]:
            F.append((b, "COMPOSITION", "", "", "; ".join(comp[b]["notes"])))
    return F


def report(B, cat, TAB, comp, bomc):
    P = print
    P("L6R2: THE GENERIC PARTS OF THE SIX BOARDS, LAYER 6 CRITERION 6.1 (l6r2_passives.py, MESHSAT-1357, 3 October 2026).")
    P("PROTOTYPE DESIGN: nothing bought, built, powered or measured. Rows: the committed netlists' fitted parts without an LCSC field.")
    P("Selections: part_identities' keys and requirements (rules V-1, C-D1 to C-D3, C-T, R-T1, R-S1, R-P, I-1). Parts: JLCPCB's public")
    P("parts library, read %s (inputs/). A stock figure or a price is true at its time only. Nothing reselected: specials are findings." % cat.get("read_utc"))
    P()
    P("0. THE PINS (sha256 of every input)")
    pins = [ENVELOPE, LCSC_FILL, CERT, TABLE, BLOCKED, MISMATCH, CATALOGUE, BOM_TOOL, L4E9, REGISTER, YAGEO_DOC] + [GEN[b] for b in ORDER] + [NET[b] for b in ORDER] + [INTENT[b] for b in ORDER]
    for rel in pins:
        P("   %s %s" % (sha256(rel), rel))
    if sha256(BOM_TOOL) != BOM_TOOL_FROM["sha256"]: die(2, "inputs/bom_from_netlist.py is not the file copied from %s" % BOM_TOOL_FROM["commit"])
    P("   %s %s (held back; w5identc's fetch_held_back.py; %s here)" % (PI.SCHEMES["uniroyal-thick-film-p2"]["sha256"], UNIROYAL_DOC,
                                                                     "fetched and matching" if os.path.exists(os.path.join(TOP, UNIROYAL_DOC)) and sha256(UNIROYAL_DOC) == PI.SCHEMES["uniroyal-thick-film-p2"]["sha256"] else "NOT fetched: its bindings read UNREAD"))
    P("   inputs/bom_from_netlist.py is a copy of %s at %s (%s), the supplier package's reader" % (BOM_TOOL_FROM["path"], BOM_TOOL_FROM["commit"][:8], BOM_TOOL_FROM["branch"]))
    P()
    P("1. THE ROWS: the supplier BOM reader (every (comp) block, exclude_from_bom included) against the identity tool's fitted rows")
    tot = [0, 0, 0, 0, 0]
    for b in ORDER:
        refs, lines, nolcsc = bomc[b]
        fitted = len(B[b]["rows"]); unc = sum(1 for p in B[b]["rows"] if not p["generator_lcsc"])
        P("   board %s: bom_from_netlist.py %4d references in %3d lines, %4d without an LCSC field; fitted (BOM) rows %4d, %4d of them without" % (NAME[b], refs, lines, nolcsc, fitted, unc))
        for i, v in enumerate((refs, lines, nolcsc, fitted, unc)): tot[i] += v
    P("   all six: %d references, %d without an LCSC field (the reader); %d fitted rows, %d without (this record's denominator)" % (tot[0], tot[2], tot[3], tot[4]))
    P()
    P("2. PER BOARD, THE SELECTIONS OF THE UNCODED FITTED ROWS (order A, E, P, D, C, B)")
    cov = {}
    for b in ORDER:
        sels = B[b]["sels"]
        c = collections.Counter(); rc = collections.Counter()
        for d in sels:
            st = (d.get("choice") or {}).get("state") or d["cls"]
            c[st] += 1; rc[st] += len(d["refs"])
        cov[b] = (c, rc)
        P("   BOARD %s: %d selections over %d rows; %s" % (NAME[b], len(sels), sum(len(d["refs"]) for d in sels),
                                                      "; ".join("%s %d (%d rows)" % (k, c[k], rc[k]) for k in sorted(c))))
        for d in sels:
            ch = d.get("choice")
            req = d["requirements"]
            head = "     %s %-10s %s rows %d [%s]: %s" % (d["sid"], d["cls"], ",".join(d["refs"][:6]) + ("+%d" % (len(d["refs"]) - 6) if len(d["refs"]) > 6 else ""),
                                                       len(d["refs"]), clean(d["values"][0])[:60], clean(d["lands"][0])[:34])
            P(head)
            if d["cls"] in ("CAP", "RES", "FERRITE", "SEMI", "LED"):
                rq = "; ".join("%s %s" % (k, req[k]) for k in ("value", "package", "dielectric", "v_rating_min", "tolerance_max_pct", "power_min_w", "tcr_max_ppm", "resistor_kind", "current_min_a") if req.get(k) is not None)
                P("        requirement: %s" % clean(rq))
                bs = "; ".join("%s: %s" % (k, " | ".join(v)) for k, v in d["basis"].items() if k in ("v_rating_min", "tolerance_max_pct", "power_min_w", "dielectric"))
                if bs: P("        basis: %s" % clean(bs)[:400])
                if d["design"]: P("        the design's code: %s from %s" % d["design"])
                if ch and ch.get("pick"):
                    pk = ch["pick"]; r = pk["row"]
                    p1, pn = price_at(r, ch["need"])
                    P("        %s: %s %s %s %s (%s%s), stock %s against a need of %d; USD %s at 1, %s at %d; grade %s (%s %s to %s C)" % (
                        ch["state"], pk["code"], clean(r.get("brand")), clean(r.get("model")), clean(r.get("package")), r.get("lib"), ", preferred" if r.get("preferred") else "",
                        pk["stock"], ch["need"], p1, pn, ch["need"], grade_verdict(pk["grade"]), clean(pk["grade"][2]) if pk["grade"] else "no range read", pk["grade"][0] if pk["grade"] else "", pk["grade"][1] if pk["grade"] else ""))
                    P("        checks: %s" % clean("; ".join("%s %s (%s)" % (x[0], x[3], x[2]) for x in pk["lines"])))
                    mf = with_series_facts(r).get("maker_facts")
                    if mf: P("        from the maker's series sheet (the catalogue line prints none): %s" % clean("; ".join(mf)))
                    if ch.get("c_d3b"): P("        %s" % ch["c_d3b"])
                    if d.get("binding"):
                        ds, st, why = d["binding"]
                        P("        identity: %s%s" % ("DECODED on %s p.%s (%s)" % (ds["path"], ds["page"], clean(why)) if st == "DECODED" else ("UNREAD (%s)" % clean(why)) if st == "UNREAD" else "DOCUMENT_OWED: %s" % clean(why if st == "NONE" else "rule D-2 refuses the decode: " + str(why)), ""))
                    if ch.get("alt"):
                        a = ch["alt"]; P("        alternative: %s %s %s, stock %s, %s" % (a["code"], clean(a["row"].get("brand")), clean(a["row"].get("model")), a["stock"], a["row"].get("lib")))
                    if b in comp and d["refs"] and any(r in comp[b].get("touched", set()) for r in d["refs"]):
                        P("        a pending draft names %s: the draft's value key decides at the regeneration" % ", ".join(r for r in d["refs"] if r in comp[b].get("touched", set())))
                elif ch:
                    P("        %s (%d catalogue lines judged)" % (ch["state"], ch["judged"]))
            else:
                P("        %s" % clean(d["why"]))
        P()
    return cov


def page_table(B):
    """The page's per-board table (L6R2-PASSIVES.md carries it verbatim; test_l6r2 holds the two equal)."""
    L = ["| Board | Uncoded fitted rows | SELECTED rows (selections) | Open: OPEN requirement | Open: SPECIAL (not re-selected) | NOT_A_PART | NO_MATCH | Designators in the draft |",
         "|---|---|---|---|---|---|---|---|"]
    for b in ORDER:
        rc, c = collections.Counter(), collections.Counter()
        for d in B[b]["sels"]:
            st = (d.get("choice") or {}).get("state") or d["cls"]
            rc[st] += len(d["refs"]); c[st] += 1
        L.append("| %s | %d | %d (%d) | %d | %d | %d | %d | %d |" % (NAME[b], sum(rc.values()), rc["SELECTED"] + rc["LOW_STOCK"], c["SELECTED"] + c["LOW_STOCK"],
                                                           rc["OPEN"], rc["SPECIAL"], rc["NOT_A_PART"], rc["NO_MATCH"], len(entries_for(b, B))))
    return "\n".join(L) + "\n"


def main(argv):
    if "--page-table" in argv:
        sys.stdout.write(page_table(compute()[0])); return 0
    if "--plan" in argv:
        MAP, CRT, TAB = lcsc_fill_map(), certified(), table()
        codes, kws = set(), set()
        for b in ORDER:
            sels, _, _ = plan_board(b, MAP, CRT, TAB)
            for d in sels:
                if d["cls"] in ("CAP", "RES", "FERRITE", "SEMI", "LED"):
                    codes.update(c for c, _ in d["design_codes"]); kws.update(d["keywords"])
        print(json.dumps(dict(codes=sorted(codes), keywords=sorted(kws)), ensure_ascii=False, indent=1))
        return 0
    B, cat, TAB = compute()
    if "--draft" in argv:
        import l6r2_apply
        b = argv[argv.index("--draft") + 1]
        sys.stdout.write(l6r2_apply.render_draft(b, entries_for(b, B))); return 0
    if "--write-drafts" in argv:
        import l6r2_apply
        for b in ORDER:
            p = os.path.join(HERE, "apply_gen_sch_%s_lcsc.py" % b)
            open(p, "w", encoding="utf-8").write(l6r2_apply.render_draft(b, entries_for(b, B)))
            print("written", os.path.relpath(p, TOP))
        return 0
    if "--identities" in argv:
        import yaml
        sys.stdout.write("# ADDED 3 October 2026 (MESHSAT-1357, Layer 6 record l6r2). Outside `selections:` on purpose (see `what`). Rendered by l6r2_passives.py --identities;\n"
                         "# build_table.py does not carry this block: re-apply it with v2/docs/records/l6r2/apply_part_identities_block.py after a regeneration.\n")
        sys.stdout.write(yaml.safe_dump(json.loads(json.dumps(identity_block(B))), sort_keys=False, allow_unicode=False, width=140))
        return 0
    comp = {b: compose(b, entries_for(b, B)) for b in ORDER}
    bomc = bom_tool_counts()
    cov = report(B, cat, TAB, comp, bomc)
    print("3. FINDINGS (per board; each with its line)")
    F = findings(B, comp)
    for b in ORDER:
        fb = [f for f in F if f[0] == b]
        kinds = collections.Counter(f[1] for f in fb)
        print("   BOARD %s: %d findings (%s)" % (NAME[b], len(fb), "; ".join("%s %d" % kv for kv in sorted(kinds.items()))))
        for f in fb:
            if f[1].startswith("TOLERANCE"):
                import textwrap
                print("     %s: %s:" % (f[1], f[2]))
                for ln in textwrap.wrap(clean(f[4]), 180): print("       " + ln)
            else:
                print("     %s: %s [%s]: %s" % (f[1], f[2], clean(f[3])[:70], clean(f[4])[:300]))
    print()
    print("4. THE DRAFTS: apply_gen_sch_X_lcsc.py per board, composition against every other pending draft of that generator")
    for b in ORDER:
        e = entries_for(b, B)
        print("   board %s: %d designators keyed by (designator, committed value); chain %s; standalone %s" % (
            NAME[b], len(e), ", ".join(os.path.basename(x) for x in comp[b]["chain"]) or "none", ", ".join(os.path.basename(x) for x in comp[b]["standalone"]) or "none"))
        for n in comp[b]["notes"]: print("     %s" % n)
        t = sorted(r for r in e if r in comp[b].get("touched", set()))
        if t: print("     designators the pending drafts' changed lines name (their value key decides at the regeneration): %s" % ", ".join(t))
    print()
    print("5. COVERAGE AND THE LAYER 6 CRITERION 6.1 FOR THESE ROWS")
    for b in ORDER:
        c, rc = cov[b]
        done = rc["SELECTED"]; low = rc["LOW_STOCK"]; tot = sum(rc.values())
        print("   board %s: %d of %d uncoded fitted rows SELECTED (every requirement met, stock for five kits), %d LOW_STOCK (selected, the stock a finding), %d still open (%s)" % (
            NAME[b], done, tot, low, tot - done - low, "; ".join("%s %d" % (k, rc[k]) for k in sorted(rc) if k not in ("SELECTED", "LOW_STOCK"))))
    ids = identity_block(B)["drafted_identities_l6r2_passives"]["rows"]
    st = collections.Counter(r["identity"]["status"] + ("/" + r["identity"].get("datasheet", {}).get("binding", "") if r["identity"].get("datasheet") else "/" + (r["identity"].get("reason_class") or "")) for r in ids)
    print("   identity block drafted_identities_l6r2_passives: %d rows; %s" % (len(ids), "; ".join("%s %d" % kv for kv in sorted(st.items()))))
    print("   6.1 moves for the generic rows of the six boards from OPEN to PARTLY: each selected row carries a maker, an MPN, a package, a code and a")
    print("   grade; the identity is DECODED on the maker's own ordering table where it is a YAGEO CC X7R or UNI-ROYAL part, else the catalogue's")
    print("   line (DOCUMENT_OWED). The specials and the open requirements stay findings. Nothing is applied: the drafts are release-guarded.")
    return 0


def identity_block(B):
    rows = []
    for b in ORDER:
        for d in B[b]["sels"]:
            ch = d.get("choice") or {}
            pk = ch.get("pick")
            if not pk or ch.get("state") not in ("SELECTED", "LOW_STOCK"): continue
            r = pk["row"]
            ident = dict(maker=r.get("brand"), mpn=r.get("model"))
            ds, st, why = d.get("binding") or (None, "NONE", "")
            if st == "DECODED" or st == "UNREAD":
                ident["status"] = "RESOLVED"
                dd = dict(ds); dd.pop("fields", None)
                ident["datasheet"] = dict(path=ds["path"], sha256=ds["sha256"], page=ds["page"], binding="DECODED", scheme=ds["scheme"], publisher=ds["publisher"],
                                          **({"held_back": True, "fetch": ds.get("fetch")} if ds.get("held_back") else {}))
                ident["fields"] = ds["fields"]
            else:
                ident["status"] = "UNRESOLVED"
                ident["reason_class"] = "DOCUMENT_OWED"
                ident["reason"] = "the identity is JLCPCB's catalogue line (maker, MPN, package and the attributes checked in l6r2_passives.out); no maker's document in the tree binds it: %s" % clean(why)
                ident["next_action"] = "file the maker's sheet that prints %s (or its ordering table, with a DECODED scheme in part_identities.SCHEMES)" % clean(r.get("model"))
            rows.append(dict(id="L6R2-" + d["sid"], board=NAME[b], refs=d["refs"], kind=d["kind"], key=d["key"], requirements=PI._judged(d["requirements"]),
                             state=ch["state"], identity=ident, rule_c_d3b=ch.get("c_d3b"),
                             order_code=dict(code=pk["code"], read="JLCPCB parts library: %s, %s, %s, stock %s, %s library" % (clean(r.get("model")), clean(r.get("brand")), clean(r.get("package")), pk["stock"], r.get("lib"))),
                             grade=dict(range_c=list(pk["grade"][:2]) if pk["grade"] else None, basis=clean(pk["grade"][2]) if pk["grade"] else None, verdict=grade_verdict(pk["grade"])),
                             alternative=(dict(code=ch["alt"]["code"], mpn=ch["alt"]["row"].get("model"), maker=ch["alt"]["row"].get("brand")) if ch.get("alt") else None)))
    return dict(drafted_identities_l6r2_passives=dict(
        what="The exact parts selected for the GENERIC rows (capacitors, resistors, ferrites, small diodes, indicator LEDs) of the six boards' committed netlists "
             "that carry no LCSC field, per v2/docs/records/l6r2/L6R2-PASSIVES.md. These rows are not selections of the table (its scope is board C's slice), "
             "so part_identities.py check does not read this block; test_l6r2.py reads it (rule D-2 on every DECODED binding).",
        taken_by="MESHSAT-1357 Layer 6 record l6r2, 3 October 2026, on fnd/int28 at a1f696de",
        authority="SESSION, under the owner's standing rule of 26 September 2026 (rule I-1's order applied, nothing reselected); reverse by removing the block (apply_part_identities_block.py --remove)",
        rendered_by="v2/docs/records/l6r2/l6r2_passives.py --identities",
        rows=rows))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
