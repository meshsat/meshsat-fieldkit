#!/usr/bin/env python3
"""jlc_certify.py, every part on the shipped BOMs certified buyable, with a date (MESHSAT-862, 11 September 2026).

WHY. Nothing in this pipeline has ever checked that an LCSC code is the right part. `lcsc_fill.py`
fills BLANKS only and never looks at a code that is already there, which is how all twenty three of
the codes on `lcsc-blocked.txt` got into shipped BOMs: they were typed into an `ic()` call and found
later by a person reading a cart. Two of them were 0402 parts on 0603 lands. One resolved to an LED
where a BAT54 was meant. One to a lever switch where a CSD17570Q5B was meant.

Appendix 32.54 named the instrument that answers this and promised `tools/jlc_stock.py` as Stage 2.
That file was never written. This is it, under a name that says what it does.

WHAT CERTIFIED MEANS. All of it true, and dated:

  the row names a part, not a class;
  JLCPCB returns a component whose model IS that part;
  its package matches the footprint we drew, or the pair is declared equivalent with a reason;
  stock covers the order, five of each board by the owner's ruling, times the quantity per board;
  and the date of the check is written beside it.

Anything else is WRONG_MODEL, PACKAGE_MISMATCH, NO_STOCK, NOT_AT_JLC, NO_PART_CHOSEN or NOT_CHECKED,
and each of those is fixed or declared with a reason, in this repository's erc-allow.txt idiom.

WHAT "IS THAT PART" AND "MATCHES THE FOOTPRINT" MEAN SINCE 26 SEPTEMBER 2026 (MESHSAT-1357; finding W6-F3 of the
known design findings in v2/docs/ARCHITECTURE.md). Before that day neither was true of the label. Two parts were
"the same" when they shared six leading characters or one number sat inside the other, a package was compared by
its family name alone, and a row carrying a code was taken to be identified by it. So this table certified
BQ4050RSMR (a 4 x 4 mm package) on a 5 x 5 mm land, TUSB2046BVFR (the commercial grade) as TUSB2046BI,
STM32H743VIT6 as STM32H753VITx, a 5 mOhm shunt as a 3 mOhm one, a key M socket on a key B land, XSD's C4661
("23.5*16*25", no package) on the Keystone 3568 fuse-holder land, and C2089 ("8550SS-TA", TO-92-3, not an LED
package) as sixteen 3 mm panel LEDs. Now, code or no code:

  the answer carries every character of the part the row names (`same_part`);
  a land drawn from one maker's drawing names its part (`land_part`: Keystone 3568, Hirose U.FL-R-SMT-1, JST
    B2P-VH), and the answer is that part;
  a body size and a pitch that both sides state agree (`pkg_geometry`);
  an M.2 land's key is the key the maker's drawing gives the part (`part_key`);
  and a row that names no part, on a land that names no part, answered on a package only one side names, is
    NOT_IDENTIFIED.

WHAT THAT STILL DOES NOT CATCH. A code-carrying row that names no part, on a class land whose package the answer
shares (an 0603 resistor's code on `LED_0603_1608Metric`), is identified by its code: the package agrees and the
class is not compared, because no catalogue line this tool reads states one. A value is compared only where it is
a frequency (`frequency_conflict`). A land from a maker not in LAND_MAKERS is read as naming no part, and its row
is judged as a class land's row is.

A table written before that day is not evidence of identity or land; its re-take belongs to the order-set rebuild
the owner ruled on 25 September 2026 (decision 41, appendix 32.365: the order set is rebuilt and quarantined).

WHAT IT DOES NOT CLAIM. That a stock figure or a price is still true tomorrow: it is a dated reading,
like the datasheet currency check. And that the part is the RIGHT part for the circuit, which is what
the datasheet in the store and the gates on the board are for. This says only that it can be bought.

Usage: jlc_certify.py [--boards a,b,c] [--refresh] [--out-dir out] [--table PATH]
       --refresh re-queries everything; without it a cached answer younger than the cache age is used.
"""
import sys, os, re, csv, json, time, glob, argparse, datetime, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # v2/
BOARDS_DIR = os.path.join(ROOT, "release", "revA", "boards")
TABLE = os.path.join(ROOT, "release", "revA", "order", "JLC-CERTIFIED.tsv")
HANDFIT = os.path.join(HERE, "jlc-handfit.txt")
ALIASES = os.path.join(HERE, "package-aliases.txt")
MISMATCH = os.path.join(HERE, "jlc-mismatch.yaml")     # declared condition 1 mismatches (round 8, 26 September 2026)
REPO = os.path.dirname(ROOT)                            # the repository root, above v2/
CACHE = os.path.join(HERE, "out", "jlc-cache.json")
API = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
BOARD_QTY = 5          # the owner's ruling: minimum five of each board
CACHE_DAYS = 7

sys.path.insert(0, HERE)
import verdict                                          # noqa: E402

# A row that is a wire, a solder land or a header is not a component and is never certified. It is
# copper and wire on our own board, and JLC places none of it.
LEAD = re.compile(r"JST|IDC|solder land|solder pad|\blead\b|wire|electrode|pigtail|jumper|header|"
                  r"strap|breakout|harness|ribbon|block B|pack lead|tap sense|target|land\b", re.I)
# A footprint that is a header, a test point or a solder land: whatever the comment says, the row is
# the land, not the silicon it breaks out to.
BENCH_FP = re.compile(r"^(?:PinHeader|PinSocket|TestPoint|SolderWire|Conn_01x|Conn_02x|"
                      r"SolderJumper|Jumper|NetTie|Mounting|Fiducial)", re.I)
# A part number inside the BOM's free prose: the Comment column is not an MPN field.
# A part number: five or more characters of alphanumerics and the separators makers actually use,
# carrying at least one letter and one digit. It MUST be allowed to start with a digit: 74LVC1G04,
# 1N4148W, 2N7002 and Amphenol's 10164227-1004A1RLF all do, and the first version of this pattern
# required a leading letter, so every one of them fell through to whatever net name came later in the
# prose. That single character was most of the first run's wrong answers.
PART_TOKEN = re.compile(r"\b[A-Za-z0-9][A-Za-z0-9./+-]{4,}\b")
# ...and the price of allowing that is that component VALUES now look like part numbers, so they are
# excluded by shape: 10mOhm, 4.7uH, 100nF, 22u, 13V8, 145MHz.
# 26 SEPTEMBER 2026, ROUND 8 (MESHSAT-1357; the parts stream's draft 01): four more shapes that are not a part and
# that the re-take over the 45bde541 netlists took for one, each refusing a row whose ordered part is the part it
# describes. A temperature coefficient ("10.7k 0.1% 25ppm": the tool asked JLCPCB for a part called 25ppm); a PACKAGE
# name ("6 MHz HC-49S-SMD passive", "SOT-23-5", "DO-214AB", "QFN-32"); this project's own finding ids ("W3-F01",
# "R4A-N15", "F-IN-02"); and TI's literature numbers by their family prefixes (SLUS, SLLS, SCPS, SLVS and the rest,
# of which the first two were already here by name). Each is anchored on the whole token, and the collisions were
# read against the parts this project names: SMAJ15A, SMBJ18A and SMCJ40A keep their letter after SM[ABC], so the
# package shape (which needs a digit there) leaves them alone; a Coilcraft DO1608C or DO3316P carries no hyphen after
# DO, so only the hyphenated JEDEC shape (DO-214AB, TO-92-3) is excluded; SN74LVC86APWR is not a TI literature
# family; and a Maxim part in the DS range (DS3231MZ) is not touched, because document numbers such as DS40068 are
# not excluded by shape at all: the one place they were read as a part was a parenthetical, and that is corrected
# in `intended_part` instead.
NOT_PART = re.compile(r"^(?:"
                      r"[0-9.]+\s*(?:m|u|n|p|k|K|M|G)?(?:Ohm|OHM|R|F|H|V|A|W|Hz|HZ)[0-9]*|"
                      r"[0-9.]+(?:m|u|n|p|k|K|M)?|"
                      r"[0-9.]+\s*ppm(?:/K|/C)?|"
                      r"HC-?49[A-Z0-9-]*|(?:SOT|SOD|SOIC|S?SOP|TSSOP|MSOP|[VWU]?QFN|[VWU]?DFN|[LT]?QFP|BGA|LGA)-?\d+[A-Z0-9-]*|"
                      r"(?:DO|TO)-\d+[A-Z0-9-]*|"
                      r"[A-Z]\d{1,2}[A-Z]?-[A-Z]{1,3}\d+|F-[A-Z]+-\d+|"
                      r"S(?:BA|BO|BV|CA|CB|CE|CH|CL|CP|CZ|DA|DL|GL|LA|LD|LE|LL|LO|LU|LV|NA|NL|NO|NV|PR|WR)S[A-Z0-9]{3,5}|"
                      r"GND|VCC|VDD|USB[0-9]?|I2C|SPI|UART[0-9]?|PWM|LED|RGB|IP6[0-9]|NP0|X[57]R|"
                      r"GPIO[0-9]*|BCM[0-9]*|SLLS[0-9]+|SLUS[A-Z0-9]+|MESHSAT-[0-9]+"
                      r")$", re.I)


PIN_COUNT = re.compile(r"^\d+-?(?:pin|pins|way|pole|pos)$", re.I)     # "22-pin", "16-pin": see `intended_part`


VALUE = re.compile(r"^([0-9]+(?:\.[0-9]+)?)\s*(m|u|n|p|k|K|M|R)?\s*(Ohm|OHM|F|H|R)?\b")


def jlc_keyword(comment, fp):
    """The search string for a jellybean: its value with real units, its voltage, and its package.

    JLCPCB's search wants `100nF 1206`, not `100n 1206`, which returns nothing at all. The unit comes
    from the footprint prefix, because the BOM value does not carry one: C_ is farads, L_ is henries,
    R_ is ohms and needs no suffix. The voltage rating is kept when the row states one, since a 50 V
    1206 and a 16 V 1206 are different parts and the cheaper one is not always the right one."""
    val = comment.split("(")[0].strip()
    # The value does not always lead: board C writes "ferrite 600R" where the map writes
    # "600R@100MHz", and VALUE is anchored, so four ferrites parsed as nothing at all.
    kindword = ""
    if re.search(r"(?i)\bferrite\b|\bbead\b", val):
        kindword = "ferrite"                  # wherever the word sits: "ferrite 600R" and "600R 2A ferrite"
        val = re.sub(r"(?i)\b(?:ferrite\s+bead|ferrite|bead)\b", " ", val).strip()
    m = VALUE.match(val)
    if not m:
        return None
    num, mult, unit = m.groups()
    mult = mult or ""
    unit = unit or ""          # the group is optional, and the guards below may now leave it unset
    kind = fp.split("_", 1)[0].upper()
    if unit and unit.upper() == "OHM":
        unit = ""
    if kind == "R" and not unit and not mult:
        # Measured against the endpoint: "180 0603" answers CL10C180JB8NNNC, a 180 pF CAPACITOR, and
        # "27 2010" answers a 1N5339B zener. "27R 2010" answers the resistor with 4.1k in stock.
        # Only a BARE number needs it: this project writes "43R" and "0.255R" with R as the decimal
        # marker, which the value parser returns as the multiplier, and appending another R asked for
        # "43RR" and "0.255RR" and got a Murata capacitor. A k or m multiplier is already unambiguous
        # ("698k 0603" answers the resistor), and a milliohm value searches worst of all with a suffix.
        unit = "R"
    if not unit and not kindword and mult != "R":
        # A ferrite is specified in ohms at 100 MHz, not in henries, and this project writes that as
        # "600R" on an L_ land. Defaulting the L_ prefix to H asked JLCPCB for "600RH".
        unit = {"C": "F", "L": "H"}.get(kind, "")
    volts = re.search(r"\b(\d+(?:\.\d+)?)\s*V\b", val)
    pkg = norm_pkg(fp)
    parts = [num + mult + unit]
    if volts:
        parts.append(volts.group(1) + "V")
    if pkg:
        parts.append(pkg)
    if kindword:
        parts.append(kindword)
    return " ".join(parts)


def declared(path):
    """`key   # reason` lines. A line without a reason declares nothing."""
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, errors="replace"):
        line = line.strip()
        if not line or line.startswith("#") or "#" not in line:
            continue
        k, r = line.split("#", 1)
        if k.strip() and r.strip():
            out[k.strip()] = r.strip()
    return out


# ------------------------------------------------------------------------------------------------------------------
# DECLARED CONDITION 1 MISMATCHES (26 September 2026, round 8, MESHSAT-1357; review of the 22:35 progress report,
# finding D1). The owner's condition 1 of 25 September: a part substitution is a component mismatch until compatibility
# is proven. Fourteen rows of JLC-CERTIFIED.tsv (2aaa7b7f) record one: a gold-plated JST variant the held catalogue
# does not list, an order suffix the held sheet does not list, a KENTO yellow LED on rows whose value says amber, TI's
# SN74LVC86APWR where the value names Nexperia's 74LVC86APW. This tool reads every one of them CERTIFIED, because each
# model carries every character of the part the row names, and a full run writes the whole table: the marks were made
# by hand in the output, so the next run would have certified all fourteen again and lcsc_fill would have filled and
# accepted their codes from the table. A mismatch written down only where the tool does not read it is not a refusal.
#
# So the mismatches are an INPUT, `tools/jlc-mismatch.yaml`, read here on every run. A row whose code (the BOM's, or the
# answer a search picked) is declared there, and whose comment the entry's `comment_re` matches when it has one, reads
# WRONG_MODEL with the declared reason, whatever the catalogue said; a row the tool already refuses for another reason
# keeps its verdict and gains the reason. The declaration is lifted only by a compatibility decision in the same file
# that names it and cites its evidence: a file in this repository, its sha256 as it sits here, and the words in it that
# establish compatibility. A decision without that is REFUSED, printed and recorded, and the mismatch stands; a
# mismatch entry that cannot be read (no id, code, reason or record) stops the run before the table is written, because
# dropping it silently is the one failure this input exists to prevent.
CONDITION_1 = "MISMATCH under owner condition 1, not a pass"


class MismatchInputError(ValueError):
    """The declared mismatch input cannot be read as declarations: the run must not write a table without it."""


def _compat_problem(c, by_id, root):
    """The reason a compatibility decision cannot lift its mismatch, or None when it can."""
    if not isinstance(c, dict):
        return "the entry is not a mapping"
    mid = str(c.get("clears") or "").strip()
    if not mid:
        return "it names no mismatch to clear (clears:)"
    if mid not in by_id:
        return "it clears %s, which no mismatch entry declares" % mid
    for k in ("ruled_by", "ruled_on", "why"):
        if not str(c.get(k) or "").strip():
            return "it has no %s" % k
    ev = c.get("evidence")
    if not isinstance(ev, list) or not ev:
        return "it cites no evidence"
    import hashlib
    for i, item in enumerate(ev, 1):
        if not isinstance(item, dict):
            return "evidence %d is not a mapping of path, sha256 and finding" % i
        p, sha, finding = (str(item.get(k) or "").strip() for k in ("path", "sha256", "finding"))
        if not p or not sha or not finding:
            return "evidence %d lacks %s" % (i, ", ".join(k for k, v in (("path", p), ("sha256", sha), ("finding", finding)) if not v))
        full = os.path.normpath(os.path.join(root, p))
        if os.path.isabs(p) or not full.startswith(os.path.normpath(root) + os.sep):
            return "evidence %d (%s) is not a path inside this repository" % (i, p)
        if not os.path.isfile(full):
            return "evidence %d (%s) is not a file in this tree" % (i, p)
        h = hashlib.sha256(open(full, "rb").read()).hexdigest()
        if h != sha.lower():
            return "evidence %d (%s) has sha256 %s, not the %s the decision cites" % (i, p, h[:12], sha[:12])
    return None


def mismatch_declarations(path=None, root=None):
    """{"entries": [...], "cleared": {id: decision}, "refused": [(id, why)], "path": path} from the declared input.

    Raises MismatchInputError when the file is missing or a mismatch entry cannot be read; a compatibility decision
    that cannot be accepted is returned in `refused` and lifts nothing."""
    path = path or MISMATCH
    root = root or REPO
    if not os.path.exists(path):
        raise MismatchInputError("the declared mismatch input %s is missing" % os.path.basename(path))
    try:
        import yaml
        d = yaml.safe_load(open(path, encoding="utf-8")) or {}
    except Exception as e:
        raise MismatchInputError("the declared mismatch input %s cannot be parsed: %s" % (os.path.basename(path), e))
    if not isinstance(d, dict) or d.get("schema_version") != 1:
        raise MismatchInputError("the declared mismatch input %s is not schema_version 1" % os.path.basename(path))
    entries, ids = [], set()
    for i, e in enumerate(d.get("mismatches") or [], 1):
        if not isinstance(e, dict):
            raise MismatchInputError("mismatch entry %d is not a mapping" % i)
        lack = [k for k in ("id", "code", "reason", "record") if not str(e.get(k) or "").strip()]
        if lack:
            raise MismatchInputError("mismatch entry %d (%s) has no %s" % (i, e.get("id") or e.get("code") or "?", ", ".join(lack)))
        code = str(e["code"]).strip()
        if not re.fullmatch(r"C\d+", code):
            raise MismatchInputError("mismatch entry %s: %r is not an LCSC code" % (e["id"], code))
        if e["id"] in ids:
            raise MismatchInputError("mismatch entry id %s is declared twice" % e["id"])
        ids.add(e["id"])
        rx = None
        if e.get("comment_re"):
            try:
                rx = re.compile(str(e["comment_re"]))
            except re.error as x:
                raise MismatchInputError("mismatch entry %s: comment_re does not compile (%s)" % (e["id"], x))
        entries.append(dict(e, id=str(e["id"]), code=code, _rx=rx, fp_contains=str(e.get("fp_contains") or "")))
    by_id = {e["id"]: e for e in entries}
    cleared, refused = {}, []
    for c in d.get("compatibility") or []:
        why = _compat_problem(c, by_id, root)
        if why:
            refused.append((str((c or {}).get("clears") or "?") if isinstance(c, dict) else "?", why))
        else:
            cleared[str(c["clears"]).strip()] = c
    return {"entries": entries, "cleared": cleared, "refused": refused, "path": path}


def declared_hits(rec, ev, decl):
    """The mismatch entries that apply to this row: its code (the answer's, else the BOM's), its comment, its land."""
    if not decl:
        return []
    codes = {c for c in ((ev or {}).get("code"), rec.get("code")) if c}
    comment, fp = rec.get("comment") or "", rec.get("fp") or ""
    return [e for e in decl["entries"] if e["code"] in codes
            and (e["_rx"] is None or e["_rx"].search(comment))
            and (not e["fp_contains"] or e["fp_contains"] in fp)]


def apply_declared(rec, ev, decl):
    """The row's verdict with every declared, uncleared mismatch applied to it (see the block above)."""
    hits = declared_hits(rec, ev, decl)
    if not hits:
        return ev
    ev = dict(ev)
    rel = os.path.relpath(decl.get("path") or MISMATCH, os.path.dirname(HERE))
    held = [e for e in hits if e["id"] not in decl["cleared"]]
    if not held:
        for e in hits:
            c = decl["cleared"][e["id"]]
            ev["note"] = ((ev.get("note") or "") + ("; " if ev.get("note") else "") +
                          "declared mismatch %s (%s) cleared by a compatibility decision ruled by %s on %s, evidence %s"
                          % (e["id"], rel, c["ruled_by"], c["ruled_on"],
                             ", ".join("%s sha256 %s" % (x["path"], str(x["sha256"])[:12]) for x in c["evidence"])))
        return ev
    e = held[0]
    refused = [w for i, w in decl["refused"] if i == e["id"]]
    reason = "%s: ordered %s, schematic names %s; %s%s (declared %s in %s; record %s)%s" % (
        CONDITION_1, e.get("ordered") or ev.get("model") or "?", e.get("named") or "?", e["reason"],
        ("; recommended %s" % e["recommended"]) if e.get("recommended") else "", e["id"], rel, e["record"],
        ("; a compatibility decision naming it was refused: %s" % refused[0]) if refused else "")
    if ev.get("verdict") in ("WRONG_MODEL", "PACKAGE_MISMATCH"):
        ev["note"] = (ev.get("note") or "") + "; also a " + reason
    else:
        ev["note"] = reason + "; the tool read %s%s" % (ev.get("verdict"), (" (%s)" % ev["note"]) if ev.get("note") else "")
        ev["verdict"] = "WRONG_MODEL"
    ev["declared_mismatch"] = e["id"]
    return ev


_DECLARED = None


def _declared_mismatches():
    global _DECLARED
    if _DECLARED is None:
        _DECLARED = mismatch_declarations()
    return _DECLARED


def norm_pkg(s):
    """One canonical spelling for a package, from either side.

    KiCad writes `R_0603_1608Metric` and `SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm`; JLC writes `0603`
    and `SOIC-8` and `DO-214AA(SMB)`. Both are reduced to the same short token so the comparison is
    about the package and not about either tool's naming habits."""
    if not s:
        return ""
    s = s.upper().strip()
    s = re.sub(r"^(?:PACKAGE_[A-Z_]+:|[A-Z_]+:)", "", s)          # strip a KiCad library prefix
    # HC-49 CRYSTALS (26 September 2026, round 8). KiCad draws the surface-mount can as `Crystal_SMD_HC49-SD` and
    # JLCPCB writes `HC-49S-SMD`; neither reduced to anything, so board D's two 6 MHz crystals read NOT_IDENTIFIED once
    # the parser stopped taking "HC-49S-SMD" for their part. The family alone would join an SMD land to a through-hole
    # HC-49/U or HC-49/S can, so the mounting stays in the name: HC-49-SMD for a surface-mount body on either side,
    # and the through-hole spellings keep their own suffix and are compared as they are.
    if re.search(r"HC-?49", s):
        if re.search(r"SMD|HC-?49-?SD\b", s):
            return "HC-49-SMD"
        m = re.search(r"HC-?49[-/]?([A-Z0-9]*)", s)
        return "HC-49" + (("-" + m.group(1)) if m and m.group(1) else "")
    m = re.match(r"^(?:R|C|L|LED|D|F|FB)_(\d{4})[_ ]", s)           # passive: R_0603_1608Metric
    if m:
        return m.group(1)
    m = re.match(r"^(?:D|F|FB|L)_(SM[ABC])\b", s)                   # diode body: D_SMB -> SMB
    if m:
        return m.group(1)
    # The general KiCad shape is <kind>_<package>_<metric or dimensions>: D_SOD-123, Fuse_1812_4532Metric,
    # Crystal_SMD_3225_2Pin. Taking the first token alone turned all of those into D, FUSE and CRYSTAL,
    # which then "mismatched" every real answer. Take the package field instead.
    m = re.match(r"^(?:D|F|FB|L|R|C|LED|FUSE|CRYSTAL|DIODE)_([A-Z0-9-]+)(?:_|$)", s)
    if m and m.group(1) not in ("SMD",) and any(c.isdigit() for c in m.group(1)):
        return m.group(1)        # a package carries digits; `L_COILCRAFT_...` is a maker, not a package
    m = re.match(r"^(?:CRYSTAL|FUSE|L|C)_SMD_(\d{4})", s)           # Crystal_SMD_3225_2Pin -> 3225
    if m:
        return m.group(1)
    m = re.match(r"^(\d{4})\b", s)                                 # JLC: "0603"
    if m:
        return m.group(1)
    for code, short in (("DO-214AC", "SMA"), ("DO-214AA", "SMB"), ("DO-214AB", "SMC")):
        if code in s:
            return short
    s = re.sub(r"\(.*?\)", "", s)                                  # VSON-8(5x6) -> VSON-8
    s = s.split(",")[0]                                            # SMD,10x6.5mm -> SMD
    m = re.match(r"^([A-Z]+(?:-[A-Z]+)?-?\d+)", s)                 # SOIC-8, TSSOP-24, SOT-583, QFN-64
    if m:
        return m.group(1).rstrip("-")
    # A standard package name anywhere in the string. `Winbond_USON-8-1EP_3x2mm` is a USON-8 whatever
    # the maker prefix says, and so is `WSON-6-1EP_2x2mm`.
    m = re.search(r"\b((?:[WVUTLHX]?[SQ]?(?:SOIC|SOP|SON|QFN|QFP|TSSOP|SSOP|MSOP|DFN|BGA|LGA|LQFP)"
                  r"|SOT|SOD|TO|DO|DIP|SC|SMA|SMB|SMC)-?\d+)\b", s)
    if m:
        return m.group(1)
    # Nothing standard in it. This is a land drawn from one maker's own drawing (Ebyte_E22-900M30S,
    # L_Coilcraft_XAL4020-XXX, CM5_Conn_A_10164227, Radiall_SMPMAX_R222M00720). It has no package name
    # to compare, and taking its first token returned the MAKER (COILCRAFT, BOSCH, QUECTEL), which then
    # "mismatched" every real answer and would have been silenced by an alias line that waved through
    # every part that maker sells. Say nothing instead: an empty string skips the comparison, and the
    # mechanical check for a custom land is the custom-footprint audit, not this string.
    m = re.search(r"(POWERPAK|D2PAK|DPAK|SOT-?223|TO-?\d+)", s)
    if m:
        return m.group(1)
    if re.fullmatch(r"SM[ABC]", s):      # JLCPCB writes the diode body bare as well as as DO-214xx
        return s
    return ""


_KI_BODY = re.compile(r"(?:^|_)(\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)(?:x\d+(?:\.\d+)?)?mm(?=_|$)", re.I)
_KI_PITCH = re.compile(r"(?:^|_)P(\d+(?:\.\d+)?)mm(?=_|$)", re.I)
_JLC_BODY = re.compile(r"(?:\(|^|[,_])\s*(\d+(?:\.\d+)?)\s*[xX*]\s*(\d+(?:\.\d+)?)\s*(?:mm)?\s*(?:\)|,|$)")
_JLC_PITCH = re.compile(r"\bP\s*=\s*(\d+(?:\.\d+)?)\s*mm", re.I)
BODY_TOL_MM = 0.15      # a nominal 4.9 against 5.0 is the same body; 4 against 5 is not
PITCH_TOL_MM = 0.01


def pkg_geometry(s):
    """{"body": (w, h) or None, "pitch": mm or None} as a package string STATES them, from either side.

    26 September 2026 (W6-F3): `norm_pkg` reduces both sides to a family name, which is right for the naming habits
    of the two tools and blind to size: KiCad's `QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm` and JLCPCB's `VQFN-32-EP(4x4)`
    are both QFN-32 and the alias QFN-32=VQFN-32 joined them, which is how board P's BQ4050RSMR (RSM, 4 x 4 mm,
    0.4 mm pitch) was certified on a 5 x 5 mm land. KiCad writes the body as `_WxHmm` and the pitch as `_Pxmm` (an
    exposed pad is `_EPaxbmm` and is not the body); JLCPCB writes the body in parentheses or after a comma and the
    pitch as `P=x mm`. A dimension a side does not state is None, and nothing is compared against a None."""
    s = (s or "").strip()
    body = pitch = None
    base = s.split(":")[-1]
    m = _KI_BODY.search(base)
    if m: body = (float(m.group(1)), float(m.group(2)))
    else:
        m = _JLC_BODY.search(s)
        if m: body = (float(m.group(1)), float(m.group(2)))
    m = _KI_PITCH.search(base) or _JLC_PITCH.search(s)
    if m: pitch = float(m.group(1))
    return {"body": body, "pitch": pitch}


def geometry_conflict(fp, spec):
    """The sentence for a body or pitch both sides state and that differs, or None. Only a land with a standard
    package name is measured this way: a maker's own land (`Ebyte_E22-900M30S`, `BatteryHolder_Keystone_3034_1x20mm`)
    carries numbers that are not a package body, and it has its own audit."""
    if not norm_pkg(fp): return None
    a, b = pkg_geometry(fp), pkg_geometry(spec)
    if a["body"] and b["body"]:
        sa, sb = sorted(a["body"]), sorted(b["body"])
        if any(abs(x - y) > BODY_TOL_MM for x, y in zip(sa, sb)):
            return "our land's body is %g x %g mm and the part's is %g x %g mm" % (a["body"] + b["body"])
    if a["pitch"] and b["pitch"] and abs(a["pitch"] - b["pitch"]) > PITCH_TOL_MM:
        return "our land's pitch is %g mm and the part's is %g mm" % (a["pitch"], b["pitch"])
    return None


# THE M.2 KEY IS PART OF THE LAND AND NO CATALOGUE LINE STATES IT (26 September 2026). Board B's J_M2C2 is drawn as a
# key B socket and carried TE 1-2199119-5, which TE's own drawing gives as KEY M, and the RM520N-GL is "a standard
# M.2 Key-B WWAN module" (Quectel RM520N-GL Hardware Design V1.0, 2022-07-15, section 2.1, held as
# v2/vendor/quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf), so it cannot be inserted. JLCPCB's line for C574849 reads `SMD,P=0.5mm` and names
# no key, so the key is read from the maker's drawing, declared here per part number with the drawing it came from.
M2_KEYS = {
    # TE customer drawing C-2199119 rev F, ECR-19-011878, 19 March 2020, sheet 2 part-number table
    # (v2/vendor/m2/te-2199119-customer-drawing-revF.pdf, sha256 ef35dbf8332b951c64be9662678bc2820f6091e1f2bb07777d0b4bf4f97b9bff)
    **{pn: "M" for pn in ("1-2199119-3", "1-2199119-4", "1-2199119-5", "1-2199119-6")},
    **{pn: "A" for pn in ("1-2199119-2", "2199119-7", "2199119-8", "2199119-9")},
    **{pn: "E" for pn in ("1-2199119-1", "2199119-2", "2199119-4", "2199119-6")},
    **{pn: "B" for pn in ("1-2199119-0", "2199119-1", "3-2199119-1", "2199119-3", "2199119-5")},
    # TE customer drawing C-2199230 rev B3, sheet 2 part-number table
    # (v2/vendor/m2/te-2199230-m2-e-key.pdf, sha256 3e2f380fe945f5246122692dd3ab7dc4926c343c7155346eac803b4b251ac7e2)
    **{pn: "M" for pn in ("1-2199230-3", "1-2199230-4", "1-2199230-5", "1-2199230-6", "1-2199230-7")},
    **{pn: "A" for pn in ("1-2199230-2", "2199230-7", "2199230-8", "2199230-9")},
    **{pn: "E" for pn in ("1-2199230-1", "2199230-2", "2199230-4", "2199230-6")},
    **{pn: "B" for pn in ("1-2199230-0", "2199230-1", "2199230-3", "2199230-5")},
}
# Amphenol customer drawing C MDT-XXX-X-XX-001 rev 4 (30 April 2014), ORDER P/N SYSTEM: MDT, the connector height
# (three digits), the CONNECTOR KEY ID letter (A, B, E, M), the plating (01, 02, 03), 001
# (v2/vendor/m2/amphenol-mdt420m02001-m2-m-key.pdf, sha256 1246e4aa4fdfc05efbd20b5b30a7f1bc1942f0813c567f0a9f9c1d92b5345113)
_AMPHENOL_MDT = re.compile(r"^MDT\d{3}([ABEM])0[123]001$")
_LAND_KEY = re.compile(r"(?:^|[_:\s])([ABEM])[-_ ]?KEY(?:[-_ ]|$)", re.I)
_TEXT_KEY = re.compile(r"\bKEY[\s:=-]*([ABEM])\b|\b([ABEM])[\s-]KEY\b", re.I)


def land_key(fp):
    """The M.2 key our land is drawn for (`M2_B-Key_Socket_3052` is B), or None for a land that is not keyed."""
    m = _LAND_KEY.search((fp or "").split(":")[-1])
    return m.group(1).upper() if m else None


def part_key(model, text=""):
    """(key, source) of the part the catalogue answered, or (None, None) when nothing states it."""
    mm = re.sub(r"\s", "", (model or "").upper())
    for pn, k in M2_KEYS.items():
        if mm == pn: return k, "TE's drawing for %s" % pn[pn.index("2199"):pn.index("2199") + 7]
    m = _AMPHENOL_MDT.match(re.sub(r"[^A-Z0-9]", "", mm))
    if m: return m.group(1), "Amphenol's order code system (C MDT-XXX-X-XX-001 rev 4)"
    m = _TEXT_KEY.search(" ".join(str(x or "") for x in (model, text)))
    if m: return (m.group(1) or m.group(2)).upper(), "the catalogue's own line"
    return None, None


def load_cache():
    try:
        return json.load(open(CACHE))
    except Exception:
        return {}


def save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = CACHE + ".part"
    json.dump(c, open(tmp, "w"), indent=0, sort_keys=True)
    os.replace(tmp, CACHE)


def query(keyword, cache, refresh=False):
    """Ask JLCPCB. Cached by keyword with its date, so a rerun is free and the table reproducible."""
    key = keyword.strip()
    hit = cache.get(key)
    if hit and not refresh:
        age = (datetime.date.today() - datetime.date.fromisoformat(hit["asked"])).days
        if age <= CACHE_DAYS:
            return hit["list"], hit["asked"]
    body = json.dumps({"keyword": key, "currentPage": 1, "pageSize": 12, "searchSource": "search"})
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "-X", "POST", API, "-H", "Content-Type: application/json",
                            "-H", "User-Agent: " + UA, "-d", body, "--max-time", "45"],
                           capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
            lst = (d.get("data") or {}).get("componentPageInfo", {}).get("list") or []
            # "describe" and "erpComponentName" joined the kept fields on 26 September 2026 (round 8). `_certify` builds
            # the answer's description from exactly these two (ev["desc"]) and `frequency_conflict` reads it, but they
            # were never kept, so the frequency guard saw only the model and the package: it caught NX3225SA-25MHz
            # because the model spells its frequency, and it could not have caught a crystal whose model does not
            # (SJK's 6CS06000F20UCG, whose catalogue line reads "6MHz ±20ppm 20pF"). A cached answer written before
            # that day carries neither field, and the guard stays silent on it as before; --refresh re-asks.
            keep = [{k: c.get(k) for k in ("componentCode", "componentModelEn", "componentBrandEn",
                                           "componentSpecificationEn", "componentLibraryType",
                                           "stockCount", "initialPrice", "assemblyComponentFlag",
                                           "minPurchaseNum", "leastPatchNumber",
                                           "describe", "erpComponentName")} for c in lst]
            today = datetime.date.today().isoformat()
            cache[key] = {"asked": today, "list": keep}
            return keep, today
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None, None                                              # unreachable: never a pass


_ORDER_TAIL = re.compile(r"^[A-Z][A-Z0-9]{0,2}$")


def _alnum(x):
    return re.sub(r"[^A-Z0-9]", "", (x or "").upper())


def _model_core(got):
    """A catalogue model without the packing and finish codes JLCPCB appends in trailing parentheses."""
    return re.sub(r"(?:\s*\([^()]*\))+\s*$", "", got or "")


# THE PART A LAND NAMES (26 September 2026). KiCad names a land drawn from one maker's drawing
# <class>_<Maker>_<part>_<pins, pitch, orientation> (Fuseholder_Blade_Mini_Keystone_3568, U.FL_Hirose_U.FL-R-SMT-1_Vertical,
# SMA_Amphenol_132134_Vertical, USB3_A_Receptacle_Wuerth_692122030100) and a JST land JST_<series>_<part>_...
# (JST_VH_B2P-VH_1x02_P3.96mm_Vertical). The makers listed are the ones whose lands in this set name a part; a maker
# whose land names only a PACKAGE (Texas_DSG0008A, Winbond_USON-8, Bosch_LGA-14), a land that names a family by a
# placeholder (TRACO's TEN40-110xxWIRH) and a class land (LED_D3.0mm, IDC-Header_2x10_P2.54mm) name no part.
LAND_MAKERS = ("AMASS", "Amphenol", "Ebyte", "GCT", "Hirose", "HRO", "JST", "Keystone", "Molex", "NiceRF", "Omron",
               "Pulse", "Quectel", "Radiall", "Seeed", "Skyworks", "Stewart", "Vishay", "Wuerth")
_LAND_MAKER = {m.upper() for m in LAND_MAKERS}
# The fields after the part: pins (1x04, 1x04-1MP, 2Pin), pitch (P1.00mm), a size (1x20mm, D3.0mm), a metric code,
# an orientation or a mounting word. The part is the first field after the maker that carries a digit, before these.
_LAND_TAIL = re.compile(r"^(?:\d+x\d+.*|P\d.*|.*mm|.*Metric|\d+(?:-\d+)?MP|.*\d+Pin|Vertical|Horizontal|"
                        r"SMD|THT|Pin\d.*|NarrowPad.*|ClockwisePinNumbering)$", re.I)


def land_part(fp):
    """The maker's part number a land is drawn for, or None when the land names a class, a package or a family."""
    toks = (fp or "").split(":")[-1].split("_")
    for i, t in enumerate(toks):
        if t.upper() not in _LAND_MAKER:
            continue
        for u in toks[i + 1:]:
            if _LAND_TAIL.match(u):
                return None
            if any(c.isdigit() for c in u):
                return u
        return None
    return None


def same_part(want, got):
    """Is the component JLC returned the part we asked for? Punctuation and case do not matter; EVERY letter and
    digit of the part the row names does (26 September 2026, finding W6-F3).

    Until that day two parts were the same when they shared six leading characters, or when one number sat inside
    the other. That made TPS2065C the same as TPS2061C (an active-low enable) and TPS2069C (1.5 A), E22-900M30S
    the same as E22-900M33S, ATECC608B as ATECC608A, BQ25731 as BQ25730, STM32H753 as STM32H743, TUSB2046BI (the
    industrial grade) as TUSB2046BVFR (the commercial one), a 3 mOhm LR2512 shunt as the 5 mOhm one, and TE's key
    B 2199119-5 as its key M 1-2199119-5. The rule now, which is what a maker's order code actually adds to a
    part number, in three shapes and no others:

      1. the answer begins with the whole part we named and adds ordering after it (TPS2065CDBV, TPS2065CDBVR);
      2. a maker's letter prefix in front of a part we named from a DIGIT (74LVC08APW, TI's SN74LVC08APWR);
      3. an ordering code inserted before a qualifier we named after the last hyphen, when that qualifier starts
         with a letter (LM74700-Q1, LM74700QDBVRQ1; BQ34Z100-G1, BQ34Z100PWR-G1).

    An answer that names LESS than the row (132134 for 132134-11) is not the part the row names: a row that means
    the base part says so. A maker's placeholder is a character like any other: ST's `x` in STM32H753VITx stands for
    a grade the row did not choose, so no orderable part carries it and the orderable code belongs in the generator.
    A part number under five characters is compared exactly.

    THE CATALOGUE'S TRAILING PARENTHESES ARE NOT PART OF THE PART (26 September 2026). JLCPCB appends packing and
    finish codes to a model in parentheses: Hirose's reel code in `U.FL-R-SMT-1(10)`, JST's `(LF)(SN)`, a gain bin
    in `8550SS-TA(RANGE:160-300)`. Read as characters, `U.FL-R-SMT(10)` begins with `UFLRSMT1` and passed for
    U.FL-R-SMT-1, a different Hirose part number, by the reel code's first digit. They are dropped from the answer before
    it is compared; the row's own part never carries parentheses (PART_TOKEN does not read them)."""
    a, b = _alnum(want), _alnum(_model_core(got))
    if not a or not b:
        return False
    if len(a) < 5:
        return a == b
    if b.startswith(a):
        return True
    if a[0].isdigit():
        m = re.match(r"^([A-Z]{1,3})(\d.*)$", b)
        if m and m.group(2).startswith(a):
            return True
    w = (want or "").upper().strip()
    if "-" in w:
        base, tail = w.rsplit("-", 1)
        base, tail = _alnum(base), _alnum(tail)
        if len(base) >= 5 and _ORDER_TAIL.match(tail) and len(b) > len(base) + len(tail) \
                and b.startswith(base) and b.endswith(tail):
            return True
    return False


def intended_part(comment):
    """The manufacturer part a BOM row means, out of its free prose, or None for a jellybean.

    Two rules, both learnt from the first full run. **Parentheses are stripped first**: this project's
    BOM convention puts the part before the explanation, and the explanation is full of net names, so
    `10.0k 1% (RFBOUT2)` was being searched for as a part called RFBOUT2, and `Ebyte E22-900M30S 1 W
    LoRa (SX1262)` as the bare silicon rather than the module we buy. **And the FIRST token wins**,
    because `Ebyte E72-2G4M20S1E CC2652P` means the module and names the chip inside it second."""
    # Parentheses are blanked rather than removed, so every position below is a position in the comment as
    # written and "the FIRST token wins" can be applied to the whole row instead of to the prose alone.
    masked = re.sub(r"\(([^)]*)\)", lambda m: " " * (len(m.group(0))), comment)
    cands = []
    got = _first_token(masked)
    if got: cands.append((masked.index(got), got))
    # 14 September 2026: A PARENTHETICAL OF THE FORM "(Maker PartNumber)" NAMES THE PART. Blanking every
    # parenthesis is right when the parenthesis is an explanation, which is what it usually is here, and it was
    # written for `10.0k 1% (RFBOUT2)` being searched for as a part called RFBOUT2. But board B's HDMI
    # receptacle reads "HDMI type A receptacle (Molex 208658-1001): cable to the Xenarc 709GNK pass-through on
    # the face plate": the only part number in the row is inside the parentheses, so the tool reached past them,
    # found 709GNK, the MONITOR the cable goes to, and called a correct order code WRONG_MODEL. The refinement
    # is narrow on purpose: it offers a candidate only for a parenthetical that opens with a capitalised maker
    # word followed by something part-shaped, so a bare `(RFBOUT2)` and a bare `(SX1262)` stay explanations and
    # the two rules those were written for still hold. Position decides between the candidates, as before.
    # 26 SEPTEMBER 2026, ROUND 8 (MESHSAT-1357, the parts stream's draft 01): "FOLLOWED BY SOMETHING PART-SHAPED" MEANS
    # THE NEXT WORD, NOT THE FIRST PART-SHAPED TOKEN ANYWHERE AFTER IT. The pattern took any capitalised word as the
    # maker and then searched the rest of the parenthesis, so "100n 16V (REFCLK AC coupling, DS40068 3.1, W3-F03)"
    # read REFCLK as a maker and DS40068, a Microchip document number, as the row's part; "(HCSL series Rs, DS40068
    # Table 8-1, W3-F03)" and "(PCIe AC coupling at the switch transmitter, W3-F01)" did the same, and four board B
    # passives whose ordered parts are exactly the values they name were refused WRONG_MODEL. A maker (one or two
    # capitalised words: "Molex", "Texas Instruments") is followed by its part number, so the candidate is the word
    # right after it, or nothing.
    for m in re.finditer(r"\(([^)]*)\)", comment):
        mm = re.match(r"\s*[A-Z][A-Za-z&.\-]{2,}(?:\s+[A-Z][A-Za-z&.\-]{2,})?[\s,]+([^\s,;:()]+)", m.group(1))
        if not mm: continue
        t = _first_token(mm.group(1))
        if t: cands.append((m.start(), t))
    # A PIN COUNT GIVES WAY TO A PART (27 September 2026, round 8, second pass). "Touch Display 2 FPC 22-pin 0.5 mm
    # (Hirose FH12-22S-0.5SH), Standard-Mini 22-to-15 cable" read "22-pin", which comes first, as its part, ahead of the
    # Hirose part in the parenthesis that its land is drawn for; the first pass then needed the land rule of `row_part`
    # to read the row, and that rule no longer reads a row whose words give no reason. A pin count is not a part, so it
    # never wins over a candidate that is one. Where it is the ONLY candidate ("RockBLOCK 9704 16-pin (IDC 2x8)", board
    # B's bracket header) it is still returned, as before: `rows_to_check` keeps a row whose words say IDC, lead or
    # header only when it names something, so returning None there would take a declared bench header out of the table
    # altogether. That header's reading is a limit of LEAD, recorded, not changed in this pass.
    real = [c for c in cands if not PIN_COUNT.match(c[1])]
    cands = real or cands
    return min(cands)[1] if cands else None


def row_part(comment, fp):
    """(the part a row is identified by, or None; the OTHER part its words name, or None).

    26 SEPTEMBER 2026, ROUND 8 (MESHSAT-1357, the parts stream's draft 01): A CONNECTOR ROW NAMES WHAT IT PLUGS INTO
    AS OFTEN AS WHAT IT IS. Board P's "JST-PH 1x5 socket for the four cell thermistors (Semitec 103AT-2, ...)" sits on
    JST's B5B-PH-K land and orders JST's B5B-PH-K-S; board E's "JST-XH 1x2 (B2B-XH-A): lid and tamper reed sensor
    lead, Littelfuse 59140-1-S-05-A ..." sits on the B2B-XH-A land and orders B2B-XH-A. The tool read the thermistor
    and the reed switch as the rows' parts and refused both. A land drawn from one maker's drawing (`land_part`) is
    strong evidence of what the row IS: the copper is that part's.

    27 SEPTEMBER 2026, ROUND 8, SECOND PASS (the independent check of the first): THE LAND IDENTIFIES THE ROW ONLY WHEN
    THE WORDS SAY THE OTHER PART IS NOT THE ROW'S OWN. The first pass let the land's part win whenever the words named a
    part unrelated to it, without asking whether that part was really at the far end of a lead. So a genuine conflict
    between the value and the land read CERTIFIED with a note where fc144600 refused it; reproduced offline, all three
    WRONG_MODEL at fc144600 and CERTIFIED after the first pass:
      "Ebyte E22-900M30S 1 W LoRa (SX1262)" on the Ebyte_E22-900M33S land with an E22-900M33S code (the sibling class
        of finding W6-F3: the schematic names one module and the copper and the order are another);
      "JST B4B-XH-A socket" on JST's B4B-PH-K land with the PH code;
      "Molex 502382-1270 12-pin panel lead" on a JST PH 12-pin land with the JST code.
    Each is a substitution under the owner's condition 1: the schematic names X and the order is Y. Now the land's part
    identifies the row only when `far_end_reason` finds BOTH halves of the evidence in the words: they name the land's
    own part or its JST series (the row says what it IS), AND they mark the other part as a thing away from the land (a
    maker other than the land's right before it, or wording such as "lead to", "from the", "on the", "holder" or
    "thermistor" beside it, in its own clause). Otherwise the row is read by the part its words name, as at fc144600,
    so the answer is compared with that part and with the land's (`_certify`), and `certify` writes both parts into the
    note and never lets a catalogue pass stand over the conflict. A part the words name that IS the land's with more
    ordering (132134-11 on the 132134 land) is no conflict and decides, which keeps board A's SMA jacks refused for
    the base part JLCPCB answers."""
    want = intended_part(comment)
    lp = land_part(fp)
    if want and lp and not (same_part(want, lp) or same_part(lp, want)) and far_end_reason(comment, fp, want, lp):
        return lp, want
    return want, None


def value_land_conflict(comment, fp):
    """(the part the words name, the land's part, the reason the words give for reading the named part as away from
    the land, or None) when the two are unrelated parts; None when there is no such pair."""
    want = intended_part(comment)
    lp = land_part(fp)
    if not (want and lp) or same_part(want, lp) or same_part(lp, want):
        return None
    return want, lp, far_end_reason(comment, fp, want, lp)


def _land_maker_series(fp):
    """(the maker a land that names a part is drawn from, as the land spells it; its JST series, PH or XH or VH, or
    None), or (None, None) for a land that names no maker."""
    toks = (fp or "").split(":")[-1].split("_")
    for i, t in enumerate(toks):
        if t.upper() in _LAND_MAKER:
            ser = toks[i + 1] if (t.upper() == "JST" and i + 1 < len(toks) and re.fullmatch(r"[A-Z][A-Z][A-Z]?", toks[i + 1])) else None
            return t, ser
    return None, None


_WORD = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9./+-]*[A-Za-z0-9])?")


def _names_land(comment, fp, lp):
    """The words of the row that name the land's own part (or its base part: 132134 for the 132134-11 land, Keystone's
    3034) or, on a JST land, its series ("JST-PH", "JST XH", "XH2.5", "PH 2.0"); None when they name neither."""
    for t in _WORD.findall(comment or ""):
        if len(_alnum(t)) >= 4 and (same_part(t, lp) or same_part(lp, t)):
            return t
    _maker, ser = _land_maker_series(fp)
    if ser:
        m = (re.search(r"\bJST[- ]?%s\b" % ser, comment or "", re.I) or
             re.search(r"\b%s ?\d+(?:\.\d+)?\b" % ser, comment or ""))
        if m:
            return m.group(0)
    return None


# The two marks of a part AWAY FROM the land, each read inside the named part's own clause (the text between the
# nearest , ; : ( or ) on either side of it). BEFORE it: a lead, cable or pigtail running to or from it, "from the",
# "to the" or "for the" right in front of it, or the kind of thing it is (a thermistor, a reed switch, a magnet).
# AFTER it: "on the", "in the", "under the", "to the" (it sits somewhere else), or a word saying what it is that a
# board connector is not (a holder it goes in, a cable, a remote unit, a thermistor, a wall receptacle).
_FAR_BEFORE = re.compile(r"(?:\b(?:lead|leads|cable|pigtail|wire|harness)\s+(?:to|from)(?:\s+the)?|\b(?:from|to|for)\s+the|"
                         r"\b(?:thermistor|NTC|reed\s+(?:switch|sensor)|magnet))\s+$", re.I)
_FAR_AFTER = re.compile(r"^\s*(?:(?:on|in|under|inside|over|at|to)\s+the\b|(?:holder|cable|harness|remote|receiver|"
                        r"magnet|thermistor|NTC|reed|sensor|wall\s+receptacle)\b)", re.I)
# A PLACEMENT WHOSE OBJECT IS THE LAND ITSELF PLACES NOTHING AWAY FROM IT (27 September 2026, round 8, the integration
# of the cert stream after its second independent check). "Ebyte E22-900M30S on the E22-900M33S land" and "Ebyte
# E22-900M30S in the E22-900M33S footprint" put the M30S ON the copper drawn for the M33S: the W6-F3 sibling
# substitution, which fc144600 refused and the second pass certified because "on the" and "in the" were counted
# without reading what follows them. A preposition of place ("on/in/under/inside/over/at/to the") marks the named
# part as away from the land only when its object is something else: an object that names the land's own part or
# JST series, or the words land, footprint, pad or pads, is the land, and the words then say the part sits on it.
# The noun marks (holder, cable, remote and the rest of _FAR_AFTER's second group) are unchanged.
_FAR_PLACE = re.compile(r"^\s*(?:on|in|under|inside|over|at|to)\s+the\b", re.I)
_LAND_WORD = re.compile(r"\b(?:lands?|footprints?|pads?)\b", re.I)
# A maker's name, as this project writes one in front of a part ("Semitec 103AT-2", "Littelfuse 59140-1-S-05-A"): one
# capitalised word. The words a clause may open with that are not makers are listed, so they never count as one.
_MAKER_WORD = re.compile(r"^[A-Z][a-z][A-Za-z]+$")
_NOT_MAKER = {"the", "for", "from", "lead", "leads", "cable", "socket", "header", "plug", "jack", "touch", "display",
              "standard", "mini", "remote", "vehicle", "shore", "panel", "module", "cell", "pack", "pigtail", "second",
              "bare", "lid", "one", "each", "both", "and", "with", "via", "mated", "mating", "housing", "receptacle"}


def far_end_reason(comment, fp, want, lp):
    """Why the row's words read `want` as a part away from the land drawn for `lp` (the far end of a lead, or the part
    inside a holder), or None when they do not say so. Both halves are required (see `row_part`)."""
    named = _names_land(comment, fp, lp)
    if not named:
        return None
    c = comment or ""
    # The named part as a whole token, not inside a longer one ("103AT" is not the head of "103AT-2").
    m = re.search(r"(?<![A-Za-z0-9./+-])%s(?![A-Za-z0-9/+]|[-.][A-Za-z0-9])" % re.escape(want), c)
    if not m:
        return None
    pos = m.start()
    cs = max(c.rfind(ch, 0, pos) for ch in ",;:()") + 1
    ends = [i for i in (c.find(ch, pos + len(want)) for ch in ",;:()") if i >= 0]
    before, after = c[cs:pos], c[pos + len(want):min(ends) if ends else len(c)]
    maker, _ser = _land_maker_series(fp)
    words = before.split()
    mk = words[-1] if words else ""
    if _MAKER_WORD.match(mk) and mk.lower() not in _NOT_MAKER and mk.upper() != (maker or "").upper():
        return "the words name the land's %s and put %s after another maker's name (%s)" % (named, want, mk)
    m = _FAR_BEFORE.search(before)
    if not m:
        m = _FAR_AFTER.match(after)
        if m and _FAR_PLACE.match(after):
            obj = after[m.end():]
            if _LAND_WORD.search(obj) or _names_land(obj, fp, lp):
                m = None          # the object of the placement is the land: the part is ON it, not away from it
    if m:
        return "the words name the land's %s and place %s away from it ('%s')" % (named, want, " ".join(m.group(0).split()))
    return None


def _first_token(head):
    for t in PART_TOKEN.findall(head):
        t = t.strip(".,;:-/")
        if len(t) < 5:
            continue
        has_d = any(c.isdigit() for c in t)
        has_a = any(c.isalpha() for c in t)
        # A digit is always required: without it the pattern happily returned "green", "Amphenol",
        # "ferrite" and "sunlight" as part numbers, each searched for and answered with something real,
        # which is the worst failure shape there is. A LETTER is not required, because TE and Amphenol
        # number their connectors in digits and hyphens alone: 1-2199119-5 and 2199230-4 are the M.2
        # sockets, and demanding a letter sent all three of them to the module name later in the prose.
        if not has_d:
            continue
        if not has_a and not (re.fullmatch(r"\d+-\d+(?:-\d+)?", t) and len(t) >= 9):
            continue
        if re.fullmatch(r"20\d\d-\d\d-\d\d", t):          # a date, not a part
            continue
        if NOT_PART.match(t):
            continue
        return t
    return None


def declared_phase(letter, tools=HERE):
    """The phase the board itself declares, read the way the sweep reads it: the board table first, the
    registry's facts for a board that has no table (board E5 has no schematic chain and therefore no
    boards/e5.json)."""
    p = os.path.join(tools, "boards", "%s.json" % letter.lower())
    if os.path.exists(p):
        try: return str((json.load(open(p, encoding="utf-8")) or {}).get("phase") or "").upper()
        except ValueError: return ""
    try:
        sys.path.insert(0, tools)
        import rules_lib
        return str(((rules_lib.board_facts().get(letter.lower()) or {}).get("phase_declared")) or "").upper()
    except BaseException:
        return ""


def folders_by_letter(boards_dir=None):
    """{letter: {PHASE: (bom path, folder name)}} over every deliverable folder that carries a BOM."""
    out = {}
    for d in sorted(glob.glob(os.path.join(boards_dir or BOARDS_DIR, "meshsat-pcb-*"))):
        m = re.match(r"meshsat-pcb-([a-z0-9]+)-revA-([A-Z]+\d+)", os.path.basename(d))
        if not m: continue
        boms = glob.glob(os.path.join(d, "*bom.csv"))
        if not boms: continue
        out.setdefault(m.group(1), {})[m.group(2).upper()] = (boms[0], os.path.basename(d))
    return out


def newest_boms(only=None, boards_dir=None, tools=HERE):
    """{letter: (bom path, folder)} for the folder each board DECLARES, and `newest_boms.missing` names the
    boards that have no folder at their declared phase.

    THE NEWEST FOLDER IS NOT THE BOARD (17 September 2026). This took the highest phase number per letter, so
    board A was certified from the A24 folder while the board this tree holds is A32 and board D from D11
    against a tree holding D12: rules CMP-002 and SUP-001 are per board and were being answered about boards
    this project is not building. `gate_sweep.sh` already refuses that case and says so; the set gate supplied
    it, and the two disagreed about the same boards. A board with no folder at its declared phase has nothing
    to certify, which is INCONCLUSIVE with the reason recorded, never a pass and never a failure.

    B is read from the QUOTE folder deliberately and still is: `meshsat-pcb-b-revA-B19-quote` carries the
    phase B19 that board B declares, and certifying a parts list nobody is buying would be the same error in
    the other direction."""
    have = folders_by_letter(boards_dir)
    best, missing = {}, {}
    for letter, phases in sorted(have.items()):
        if only and letter not in only: continue
        want = declared_phase(letter, tools)
        if want and want in phases:
            best[letter] = phases[want]
        else:
            missing[letter] = (want or "nothing", sorted(phases))
    newest_boms.missing = missing
    return best


newest_boms.missing = {}


def all_boms(only=None, boards_dir=None):
    """{letter: [(bom path, folder)]} for EVERY folder of every board that carries a bill of materials.

    THE TABLE IS KNOWLEDGE AND THE VERDICT IS JUDGEMENT, and they need different inputs (17 September 2026).
    Narrowing the certification to the folder each board declares fixed the verdicts and immediately broke
    something else: `JLC-CERTIFIED.tsv` is where this project looks up whether a value can be bought at all,
    and with four boards' folders dropped, seven passive values on boards D and E had no certified row to draw
    on and the rule that every value a generator writes can be given a code failed. So the table is built from
    every folder, as it always was, and only the per-board and set VERDICTS are restricted to the folder the
    board declares."""
    out = {}
    for letter, phases in sorted(folders_by_letter(boards_dir).items()):
        if only and letter not in only: continue
        out[letter] = [phases[p] for p in sorted(phases)]
    return out


def rows_to_check(only=None, declared_only=False, boards_dir=None, tools=HERE):
    """Every distinct (value, footprint) that is a component, with the boards and quantity it carries.

    `declared_only` restricts the scan to the folder each board DECLARES, which is what the verdicts are taken
    over; the table itself is built over every folder."""
    out = {}
    # THE DECLARED FOLDER GOES FIRST, and that ordering is load-bearing: a key is (value, footprint) and the
    # first non-empty LCSC code on it wins, so scanning an older folder first attributes ITS code to the row.
    # Measured on board P, 17 September 2026: with the folders in alphabetical order the pack's two charge and
    # discharge FETs lost the code its own P4 folder carries and came back WRONG_MODEL against a search by
    # model name. The table may be built over every folder; what a row IS comes from the board's own.
    _decl_first = newest_boms(only, boards_dir=boards_dir, tools=tools)
    _src = (sorted(_decl_first.items()) if declared_only else
            ([(l, _decl_first[l]) for l in sorted(_decl_first)]
             + [(l, bf) for l, lst in sorted(all_boms(only, boards_dir=boards_dir).items()) for bf in lst
                if bf != _decl_first.get(l)]))
    _decl_pairs = set(_decl_first.items())
    for letter, (bom, folder) in _src:
        # A DECLARED FOLDER'S BLANK IS AN ANSWER TOO (26 September 2026, the decision 41 re-take). Going first was
        # not enough: the first non-empty code won, so a row the declared folder carries WITHOUT a code took the
        # code of an older folder of the same board. Board C's sixteen 3 mm panel lamps carry no code in C24, where
        # they are bench-fitted and allow-listed, and C2089 (an 8550SS in TO-92-3) in C17, where lcsc_fill had put
        # it from the certified table; the per-board verdict then failed C24 NOT_IDENTIFIED sixteen times for a code
        # C24 does not order. A key a declared folder carries takes its code from declared folders only.
        _is_decl = (letter, (bom, folder)) in _decl_pairs
        for r in csv.DictReader(open(bom, newline="", encoding="utf-8", errors="replace")):
            comment = " ".join((r.get("Comment") or "").split())
            fp = (r.get("Footprint") or "").strip()
            code = (r.get("LCSC Part #") or "").strip()
            refs = [x for x in (r.get("Designator") or "").split(",") if x.strip()]
            # LEAD names the words that make a row a wire, a land or a header. It reads the whole
            # comment, and this project's comments describe FUNCTION as well as nature: R57's
            # "1k (strap [LED4_1, LED3_1] = 01: I2C management)" is a 1k resistor whose job is to
            # strap two pins, and it was being dropped as though it were a wire strap. A row that
            # parses as a value on its own land, or that names a manufacturer part, is a component
            # whatever else the prose says.
            if not comment:
                continue
            # A row that carries a CODE is a component by definition: the code is the part's identity,
            # and dropping it here is how a wrong or unstocked code reaches an order without ever being
            # asked about. Before 12 September the drop was silent, and rewording a connector's prose so
            # that it named the socket rather than the wall receptacle at the other end of its lead would
            # have removed the row from the table instead of certifying it.
            if code:
                pass
            elif LEAD.search(comment) and not (jlc_keyword(comment, fp) or intended_part(comment)):
                continue
            key = (comment, fp)
            rec = out.setdefault(key, {"comment": comment, "fp": fp, "code": code,
                                       "boards": set(), "qty": 0, "declared": _is_decl})
            rec["boards"].add(letter.upper())
            rec["qty"] += max(1, len(refs))
            if code and not rec["code"] and (_is_decl or not rec["declared"]):
                rec["code"] = code
    return out


CLASS_ROW = re.compile(r"\bclass\b|\bowed\b", re.I)   # prose that names a category where a part belongs


def hand_fit_route(comment, want, handfit):
    """The declared purchase route for a row, or None.

    `intended_part` strips parentheses before it reads a part number, because this project's BOM
    convention puts the explanation there and the explanation is full of net names. That is right for
    identifying a row and WRONG for matching a declaration: C's three APEM toggles read
    `SOS locking toggle, maintained (APEM 5636ADKB-2V, both positions latched)`, so the only part
    number in the row sat inside the parentheses, `want` was None, and the declaration in
    jlc-handfit.txt never matched anything. Three panel parts that are declared, bought and excluded
    from the CPL were reported NOT_CHECKED for a month.

    So the declaration is matched against every part-shaped token in the WHOLE comment. This widening
    is bounded to rows that carry no code (see certify), because a row's prose often mentions a
    hand-fit part it merely connects to: D's `PA drive (coax to the RA30H1317M1 input on the plate)` is
    a U.FL socket JLC places, and the RA30H1317M1 is the module at the other end of the coax.
    """
    keys = [want] if want else []
    for t in PART_TOKEN.findall(comment):
        t = t.strip(".,;:-/")
        if len(t) >= 5 and any(c.isdigit() for c in t) and not NOT_PART.match(t):
            keys.append(t)
    for k in keys:
        hit = handfit.get(k)
        if hit:
            return hit
    # A row with no part number at all is declared by its own words, and counting characters to hit
    # `comment[:60]` exactly is a trap: "9 A spring pin, pack return (Mill-Max 0858 class, dock block)"
    # is 61 and its twin on the CELL+ side is 55, so one matched and the other did not. A declaration
    # that is a PREFIX of the row's comment matches it. Twenty characters is the floor, because a short
    # prefix would quietly cover rows nobody meant to declare.
    for k, hit in handfit.items():
        if len(k) >= 20 and comment.startswith(k):
            return hit
    return None


def project_allow():
    """Every `<project>/lcsc-allow.txt` line: the comment substring a board declares may carry no LCSC code,
    with the reason it gives.

    14 September 2026 (MESHSAT-862). A blank row is judged by TWO declarations and this tool could see only
    one of them: `tools/jlc-handfit.txt`, which is for parts bought elsewhere, and not the board's own allow
    list, which is for copper and leads JLCPCB never places (a ribbon header, a wire land, a solder jumper).
    `verify_deliverable` was corrected for exactly this on 11 September, when board E read 34 of 35 with its
    allow list right; the same sentence belongs here. The lists are merged across boards because every line
    in them declares what a row IS rather than what one board does with it, and the file it came from travels
    in the note."""
    out = {}
    for f in sorted(glob.glob(os.path.join(os.path.dirname(BOARDS_DIR), "..", "ecad", "pcb-*", "lcsc-allow.txt"))
                    + glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pcb-*", "lcsc-allow.txt"))):
        for ln in open(f, errors="replace"):
            ln = ln.strip()
            if not ln or ln.startswith("#") or "#" not in ln: continue
            k, why = ln.split("#", 1)
            if k.strip() and why.strip(): out.setdefault(k.strip(), (why.strip(), os.path.basename(os.path.dirname(f))))
    return out


PROJECT_ALLOW = None


# A VALUE THAT NAMES A FREQUENCY IS PART OF THE PART (16 September 2026). Board D's two crystals read
# "6 MHz 3225" and carried C448646, which JLCPCB's own catalogue calls NX3225SA-25MHz: a 25 MHz part certified
# against a 6 MHz line, on both crystals of a board that is otherwise finished. Nothing was wrong with the
# check that let it through, except its question: `same_part` compares the manufacturer PART NUMBER, and a
# jellybean row names no part number, so the row was decided on package and stock alone. A hub fed 25 MHz
# where its PLL wants 6 does not enumerate, and a codec clocked at 25 MHz where the USB audio frame is derived
# from 6 does not play. The frequency is checked here because it is the one quantity in these rows that both
# sides state and neither side infers.
FREQ_IN = __import__("re").compile(r"(\d+(?:\.\d+)?)\s*(k|M|G)?\s?Hz", __import__("re").I)
_MULT = {None: 1.0, "": 1.0, "K": 1e3, "M": 1e6, "G": 1e9}


def frequencies(text):
    """Every frequency a string names, in hertz. An empty set when it names none, which is most rows."""
    out = set()
    for m in FREQ_IN.finditer(text or ""):
        try: out.add(round(float(m.group(1)) * _MULT[(m.group(2) or "").upper()]))
        except Exception: pass
    return out


# WHICH ROWS THIS APPLIES TO, and it is deliberately narrow. A ferrite reads "600R@100MHz" and an inductor
# "68nH 0805 (LPF, 145 MHz 5th order)": both name a frequency that is a CONDITION, not the part, and the
# catalogue's own line for them may name a different one (a self-resonance) with neither being wrong. A part
# whose VALUE BEGINS with a frequency is a different thing: for a crystal, a resonator or an oscillator the
# frequency IS the part, and that is the only case checked here.
FREQ_IS_THE_PART = __import__("re").compile(r"^\s*\d+(?:\.\d+)?\s*(?:k|M|G)?\s?Hz\b", __import__("re").I)


def frequency_conflict(comment, ev):
    """The message for a row whose value names a frequency the catalogue entry does not, or None."""
    if not FREQ_IS_THE_PART.match(comment or ""): return None
    want = frequencies(comment)
    if not want: return None
    got = frequencies(" ".join(str(ev.get(k) or "") for k in ("desc", "model", "pkg")))
    if not got:
        return None    # the catalogue says nothing about frequency: this check has no evidence and says so by staying silent
    if want & got: return None
    fmt = lambda s: ", ".join("%g MHz" % (v / 1e6) if v >= 1e6 else "%g kHz" % (v / 1e3) for v in sorted(s))
    return "the row asks for %s and the catalogue part is %s (%s %s)" % (
        fmt(want), fmt(got), ev.get("code") or "?", (ev.get("model") or "")[:40])


def certify(rec, cache, handfit, aliases, refresh=False, mismatches=None):
    """One row's verdict, with the evidence that produced it. The frequency guard is applied HERE, to the
    result, rather than beside each of the four places a CERTIFIED verdict is written: a guard that has to be
    remembered at every return is a guard that a fifth return will miss. The declared condition 1 mismatches are
    applied here for the same reason, last, so that no return path can write a pass over one (`mismatches` is the
    loaded input; None reads tools/jlc-mismatch.yaml)."""
    ev = _certify(rec, cache, handfit, aliases, refresh)
    if isinstance(ev, dict) and ev.get("verdict") in ("CERTIFIED", "HAND_FIT"):
        bad = frequency_conflict(rec.get("comment"), ev)
        if bad:
            ev = dict(ev); ev.update(verdict="WRONG_MODEL", note=bad)
    if isinstance(ev, dict):
        # THE VALUE AGAINST THE LAND (round 8; narrowed in its second pass, 27 September 2026, see `row_part`). A row
        # whose words name a part unrelated to the part its land is drawn for is one of two things, and the note says
        # which. With the words' own evidence that the named part is away from the land, the land's part identified the
        # row and the named part is written here, never dropped. Without it, the value and the land disagree: both parts
        # are written here, and a verdict reached through the catalogue (it carries a model) that would pass is
        # WRONG_MODEL, so no answer can certify one side of the conflict. `_certify` refuses every such row already,
        # since the answer cannot be both parts; this is the guard for the path a later change adds, as the frequency
        # guard above is. A declared verdict (a hand-fit route or an allow line on a row with no code) keeps its verdict
        # and gains the sentence: it declares a purchase, not an identity, as it did at fc144600.
        vl = value_land_conflict(rec.get("comment") or "", rec.get("fp") or "")
        if vl:
            named, lp, why = vl
            ev = dict(ev)
            if why:
                s = ("the row's words also name %s, which is not the part its land is drawn for (%s): %s, so %s is read as "
                     "the part at the far end of its lead or inside the land's part, and the land's part identifies the row"
                     % (named, lp, why, named))
            else:
                s = ("the row's words name %s and its land is drawn for %s, and nothing in them marks %s as a part away "
                     "from the land (they would name the land's part or JST series, and put %s after another maker's name "
                     "or after wording such as 'lead to', 'on the' or 'thermistor'): the value and the land disagree, a "
                     "substitution under owner condition 1 until the generator's row names one part" % (named, lp, named, named))
                if ev.get("model") and ev.get("verdict") in ("CERTIFIED", "HAND_FIT"):
                    s += "; the tool read %s on %s" % (ev["verdict"], ev["model"])
                    ev["verdict"] = "WRONG_MODEL"
            ev["note"] = (ev.get("note") or "") + ("; " if ev.get("note") else "") + s
        ev = apply_declared(rec, ev, _declared_mismatches() if mismatches is None else mismatches)
    return ev


def package_problem(fp, spec, aliases):
    """The sentence for a package that is not our land, or None: the family first (with the declared aliases),
    then the body and pitch both sides state (26 September 2026)."""
    a, b = norm_pkg(fp), norm_pkg(spec)
    if a and b and a != b and aliases.get("%s=%s" % (a, b)) is None and aliases.get("%s=%s" % (b, a)) is None:
        return "our land is %s, the part is %s" % (a, b)
    return geometry_conflict(fp, spec)


def _pkg_agrees(fp, spec, aliases):
    """Both sides name a package and nothing about it differs."""
    return bool(norm_pkg(fp) and norm_pkg(spec)) and package_problem(fp, spec, aliases) is None


def key_problem(fp, ev):
    """(verdict, note) for an M.2 land whose part is keyed differently or whose key nothing states, or None."""
    lk = land_key(fp)
    if not lk: return None
    pk, src = part_key(ev.get("model"), " ".join(str(ev.get(k) or "") for k in ("pkg", "desc")))
    if pk is None:
        return ("NOT_CHECKED", "our land is M.2 key %s and neither the catalogue line for %s nor a declared maker's "
                               "drawing states that part's key: read the drawing and declare it in M2_KEYS"
                               % (lk, ev.get("model")))
    if pk != lk:
        return ("PACKAGE_MISMATCH", "our land is M.2 key %s and %s is key %s (%s)" % (lk, ev.get("model"), pk, src))
    return None


def _certify(rec, cache, handfit, aliases, refresh=False):
    """One row's verdict, with the evidence that produced it."""
    comment, fp, code = rec["comment"], rec["fp"], rec["code"]
    want, _other = row_part(comment, fp)
    need = rec["qty"] * BOARD_QTY

    # A bench header's comment names the chip it breaks out ("CC2652P cJTAG ZBA (bench): 3V3 ...") and
    # the extractor dutifully reads CC2652P out of it, then certifies a 5-pin 2.54 mm header against a
    # VQFN-48. The footprint is the honest evidence of what the row IS: when it is a plain header or a
    # test land, the row is that header, whatever silicon the prose mentions.
    if BENCH_FP.match(fp):
        # Bench headers, test points and solder jumpers are fitted by hand at bring-up and JLC places
        # none of them (make_handoff.py already strips them from the CPL). They are a declared class,
        # not an open question, and saying NOT_CHECKED about them buried the rows that ARE unanswered.
        note = "a header, test point or solder jumper: fitted by hand, not placed by JLC"
        if CLASS_ROW.search(comment):
            # The header is the board part and it is answered; the MODULE its prose names as a class is
            # a separate, owner-side purchase. Say both, or the buyer reads a settled row and never
            # learns that something still has to be chosen.
            note += "; the module its comment names as a class is an owner-side purchase, not a JLC line"
        return dict(verdict="BENCH_FITTED", need=need, note=note)

    hf = hand_fit_route(comment, want, handfit)
    if hf and not code:
        # A row with no code and a declared purchase route is answered. A row WITH a code is not: its
        # code is checked first, because a hand-fit declaration that runs before the code check hides a
        # package mismatch behind a purchase route, and the package is the defect that builds a board
        # wrong. The declaration is applied at the stock check instead, which is the one verdict a
        # purchase route legitimately answers.
        return dict(verdict="HAND_FIT", note=hf, need=need)


    # The class test runs LAST of the three declarations and only on a row that carries no code, because
    # a code IS an answer: E's J_SOLAR reads "bare 12 V class panel in ... (JST-VH, 10 A)" and the land is
    # a JST B2P-VH with a part number. Reading "class" out of the prose of a row whose part is chosen
    # reported five answered connectors as unchosen and hid the two that really were wrong.
    if not code and CLASS_ROW.search(comment):
        return dict(verdict="NO_PART_CHOSEN", note="the row names a class, not a part", need=need)


    # THE BOARD'S OWN DECLARATION, and it runs after BOTH the purchase route and the class test. A part
    # bought from Digi-Key is HAND_FIT, which says where it comes from; a row that names a CLASS rather
    # than a part is still unanswered, whatever any allow list says, because an allow line declares what a
    # row IS and not that somebody has chosen it. Putting this first cost both distinctions: 35 rows with
    # real purchase routes read as bench parts, and "12 V class mixer fan" read as answered.
    global PROJECT_ALLOW
    if PROJECT_ALLOW is None: PROJECT_ALLOW = project_allow()
    if not code:
        for k, (why, proj) in PROJECT_ALLOW.items():
            if k in comment:
                return dict(verdict="BENCH_FITTED", need=need,
                            note="declared in %s/lcsc-allow.txt: %s" % (proj, why))

    # A code that is already there is validated by the code itself; a blank row is searched by the
    # part it means, or by its value and package when it is a jellybean.
    kw = code or want or jlc_keyword(comment, fp)
    if not kw:
        return dict(verdict="NOT_CHECKED", need=need,
                    note="no part number and no value this search understands: %r" % comment[:50])
    lst, asked = query(kw, cache, refresh)
    if lst is None:
        return dict(verdict="NOT_CHECKED", note="JLCPCB did not answer", need=need)
    if not lst:
        return dict(verdict="NOT_AT_JLC", note="no component for %r" % kw, need=need, asked=asked)

    # Prefer an exact model match anywhere in the page over whatever ranked first.
    top = lst[0]
    want_pkg = norm_pkg(fp)
    lp = land_part(fp)
    if want:
        # Every candidate here carries the whole part the row names (same_part, 26 September 2026), so what
        # still separates them is the order code, and the order code is mostly the PACKAGE: asked TUSB2046BI, the
        # page answers the QFN industrial part and two LQFP commercial ones. Score every match: the part our land
        # names, when it names one (land_part), then the package we actually drew (family, and body and pitch
        # where both sides state them), then stock that covers the order, then the exact model. This one change is what separates a wrong order code from a wrong part,
        # and the wrong order code is the commoner defect by far.
        cand = [c for c in lst if same_part(want, c.get("componentModelEn"))]
        if cand:
            def rank(c):
                m = re.sub(r"[^A-Z0-9]", "", (c.get("componentModelEn") or "").upper())
                w = re.sub(r"[^A-Z0-9]", "", want.upper())
                return (not lp or same_part(lp, c.get("componentModelEn")),
                        _pkg_agrees(fp, c.get("componentSpecificationEn"), aliases),
                        (c.get("stockCount") or 0) >= need,
                        m == w,
                        c.get("componentLibraryType") == "base",
                        c.get("stockCount") or 0)
            top = max(cand, key=rank)
    else:
        # A jellybean has no model to match, so the best answer is the one that is actually in stock
        # in the right package. The top hit is ranked by JLCPCB's own relevance and was repeatedly a
        # zero-stock part when an identical one with half a million in stock sat below it.
        # A PACKAGE NEITHER SIDE NAMES PICKS NOTHING (26 September 2026). Two empty package names compared
        # equal, so a fuse-holder row searched as "25" took the first answer in stock, C4661 (XSD's "23.5*16*25"; its maker's
        # sibling C4650 is "15*10*20 UType heat sink White").
        ok = [c for c in lst if want_pkg and _pkg_agrees(fp, c.get("componentSpecificationEn"), aliases)
              and (c.get("stockCount") or 0) >= need]
        if ok:
            top = max(ok, key=lambda c: (c.get("componentLibraryType") == "base", c.get("stockCount") or 0))
    ev = dict(desc=" ".join(str(top.get(_k) or "") for _k in ("erpComponentName", "describe")),
              code=top.get("componentCode"), model=top.get("componentModelEn"),
              brand=top.get("componentBrandEn"), pkg=top.get("componentSpecificationEn"),
              lib=top.get("componentLibraryType"), stock=top.get("stockCount") or 0,
              price=top.get("initialPrice"), need=need, asked=asked)

    if want and not same_part(want, ev["model"]):
        ev.update(verdict="WRONG_MODEL",
                  note="asked for %s, JLCPCB's best answer is %s" % (want, ev["model"]))
        return ev
    a, b = norm_pkg(fp), norm_pkg(ev["pkg"])
    prob = package_problem(fp, ev["pkg"], aliases)
    if lp and not same_part(lp, ev["model"]):
        # A LAND THAT NAMES ITS PART IS ANSWERED BY THAT PART (26 September 2026), whether the answer came from the
        # row's code or from a search, and whether or not the row names a part as well. The copper is drawn from
        # that maker's drawing; another maker's part on it is a substitution until a drawing proves the land is
        # shared (the owner's condition 1 of 25 September 2026), and the proof then goes into the generator's row.
        # The code used to be taken as the identity, and a code-carrying row that named no part was certified on it
        # when a package was named on one side only, because the package comparison below needs both. JLC-CERTIFIED.tsv
        # at 82dd1e4d, lines 194 to 196: C4661, XSD's "23.5*16*25" with no package (its maker's sibling C4650 reads
        # "15*10*20 UType heat sink White"), on the Keystone 3568 land of the 25 A fuse on boards A, E and P; lines
        # 79 and 80: C10081, "GL5528(10-20)", on board E's two 10 A ones. C4661 entered as a SEARCH answer with no
        # code (the table at e0f3ef4f), lcsc_fill filled it into the BOMs from this table's CERTIFIED rows by comment
        # and land, and from 07c57b30 on it was certified on that code. A code can be this table's own mistake.
        # A row that names a part is held to its land too: "CR2032 holder Keystone 3034" reads CR2032, the CELL,
        # as its part, and Q&J's CR2032-BS-6-1 matched it on the Keystone 3034 land (line 380).
        ev.update(verdict="WRONG_MODEL",
                  note="%sits land is drawn for %s; the %s answer is %s (%s)"
                       % ("the row names no part number and " if not want else "the row names %s, but " % want,
                          lp, "code's" if code else "search's", ev["model"], ev["pkg"] or "no package"))
        return ev
    if not want and not lp and not prob and not (a and b):
        # A ROW THAT NAMES NO PART, ON A LAND THAT NAMES NO PART, ANSWERED ON A PACKAGE ONE SIDE DOES NOT NAME
        # (26 September 2026), code or no code. Nothing then identifies the answer: C165546 ("NXA50V22M5*11 LO",
        # "Plugin,D5xL11mm") for "22u 50V X7R 1210", and C2089 ("8550SS-TA", TO-92-3) as sixteen of board C's 3 mm
        # panel LEDs on the class land LED_D3.0mm (JLC-CERTIFIED.tsv at 82dd1e4d, lines 228 to 243).
        ev.update(verdict="NOT_IDENTIFIED",
                  note="the row names no part number, its land names none, and %s, so the %s answer (%s, %s) is "
                       "identified by nothing: name the part in the generator's row%s"
                       % ("the land names no package" if not a else "the catalogue line names no package this comparison reads",
                          "code's" if code else "search's", ev["model"], ev["pkg"] or "no package",
                          "" if code else " or declare it hand-fit"))
        return ev
    if prob:
        if not want and not code:
            # No part number in the row, no code either, and the package does not match: the search
            # answered with something unrelated because there was nothing to search for.
            # PACKAGE_MISMATCH would blame the package; the real fault is that the BOM row never names
            # its part, and that is what has to be fixed, in the generator.
            #
            # A row that DOES carry a code is a different thing entirely: the code IS the part's
            # identity, the answer is authoritative, and a package that does not match our land is a
            # hard defect, not a failure to identify. Reading it as NOT_IDENTIFIED hid an 0805 180 ohm
            # resistor on eleven 0603 lands and an 0805 ferrite on four more, on board C.
            ev.update(verdict="NOT_IDENTIFIED",
                      note="the row names no part number, so nothing can be certified: give it one in "
                           "the generator or declare it hand-fit (search answered %s, %s)"
                           % (ev["model"], b))
            return ev
        # A row certified by its code alone has no part number to broaden, and since a code-carrying
        # row now reaches this branch, `want` can be None here.
        # THE WIDER SEARCH IS A WIDER QUESTION, NOT A LOOSER ANSWER (26 September 2026). It drops the row's
        # trailing letters to ask JLCPCB for more candidates; each candidate must still carry every letter the
        # row named (same_part against `want`, never against `wider`) and the land we drew. Before, the looser
        # same_part let the query's missing letters decide: TUSB2046BI came back as TUSB2046BVFR, "found on the
        # wider search", which is the commercial grade (07c57b30).
        wider = re.sub(r"[A-Za-z]+$", "", want).rstrip("-") if want else ""
        if want and len(wider) >= 5 and wider.upper() != want.upper():
            lst2, asked2 = query(wider, cache, refresh)
            cand2 = [c for c in (lst2 or []) if same_part(want, c.get("componentModelEn"))
                     and (not lp or same_part(lp, c.get("componentModelEn")))
                     and _pkg_agrees(fp, c.get("componentSpecificationEn"), aliases)]
            if cand2:
                top = max(cand2, key=lambda c: ((c.get("stockCount") or 0) >= need,
                                                c.get("componentLibraryType") == "base",
                                                c.get("stockCount") or 0))
                ev = dict(desc=" ".join(str(top.get(_k) or "") for _k in ("erpComponentName", "describe")),
                          code=top.get("componentCode"), model=top.get("componentModelEn"),
                          brand=top.get("componentBrandEn"), pkg=top.get("componentSpecificationEn"),
                          lib=top.get("componentLibraryType"), stock=top.get("stockCount") or 0,
                          price=top.get("initialPrice"), need=need, asked=asked2)
                kp = key_problem(fp, ev)
                if kp:
                    ev.update(verdict=kp[0], note=kp[1])
                    return ev
                if (ev["stock"] or 0) < need:
                    ev.update(verdict="NO_STOCK", note="stock %s against a need of %d for %d boards"
                              % (ev["stock"], need, BOARD_QTY))
                    return ev
                ev.update(verdict="CERTIFIED",
                          note="found on the wider search %r: the row's suffix hid this package" % wider)
                return ev
        ev.update(verdict="PACKAGE_MISMATCH", note=prob)
        return ev
    kp = key_problem(fp, ev)
    if kp:
        ev.update(verdict=kp[0], note=kp[1])
        return ev
    if (ev["stock"] or 0) < need:
        if hf:
            # The part is right, the package is right and JLCPCB cannot supply the order: that is
            # exactly what a declared purchase route answers, and it is the only verdict it answers.
            ev.update(verdict="HAND_FIT",
                      note="%s (JLCPCB stock %s against a need of %d)" % (hf, ev["stock"], need))
            return ev
        ev.update(verdict="NO_STOCK", note="stock %s against a need of %d for %d boards"
                  % (ev["stock"], need, BOARD_QTY))
        return ev
    ev.update(verdict="CERTIFIED", note="")
    return ev


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--boards")
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out-dir", default="out")
    ap.add_argument("--table", default=TABLE)
    ap.add_argument("--limit", type=int)
    a = ap.parse_args(argv)
    only = set(a.boards.split(",")) if a.boards else None

    # A RUN ABOUT ONE BOARD MUST NOT REWRITE THE SET'S TABLE (17 September 2026). `JLC-CERTIFIED.tsv` is the
    # order set's own record of what can be bought, 720 rows over every folder, and `--boards c` wrote 88 of
    # them over it: every other board's parts vanished from the file a person reads while ordering, and
    # nothing said so. It is the same shape as the scoped readiness run of this morning, and the same answer:
    # a narrowed run writes its own table beside its own verdicts and leaves the set's alone.
    if only and os.path.abspath(a.table) == os.path.abspath(TABLE):
        a.table = os.path.join(a.out_dir, "jlc-certified-%s.tsv" % "-".join(sorted(only)))
        print("scoped run (--boards %s): the set's table %s is left as it stands; this run writes %s"
              % (",".join(sorted(only)), os.path.relpath(TABLE, ROOT), a.table))

    handfit, aliases = declared(HANDFIT), declared(ALIASES)
    # THE DECLARED MISMATCHES ARE READ BEFORE ANYTHING IS ASKED (26 September 2026, round 8). A run that cannot read
    # them must not write the table: it would write CERTIFIED over every row they hold, which is the defect they fix.
    try:
        decl = mismatch_declarations()
    except MismatchInputError as e:
        print("jlc_certify: %s; the table %s is left as it stands" % (e, os.path.relpath(a.table, ROOT)))
        return verdict.write("jlc_certify", verdict.INCONCLUSIVE, counts={}, denominator=0, out_dir=a.out_dir,
                             missing_input="%s, so no row can be judged against the declared condition 1 mismatches" % e,
                             note="the table was not written")
    for mid, why in decl["refused"]:
        print("jlc_certify: a compatibility decision for %s is REFUSED and lifts nothing: %s" % (mid, why))
    cache = load_cache()
    rows = rows_to_check(only)
    keys = sorted(rows)
    if a.limit:
        keys = keys[:a.limit]

    results, counts = [], {}
    for i, k in enumerate(keys, 1):
        rec = rows[k]
        ev = certify(rec, cache, handfit, aliases, a.refresh, mismatches=decl)
        ev.update(comment=rec["comment"], fp=rec["fp"], bom_code=rec["code"],
                  boards=",".join(sorted(rec["boards"])), qty=rec["qty"], _key=k)
        results.append(ev)
        counts[ev["verdict"]] = counts.get(ev["verdict"], 0) + 1
        if i % 25 == 0:
            save_cache(cache)
            print("  %d/%d" % (i, len(keys)), flush=True)
    save_cache(cache)

    os.makedirs(os.path.dirname(a.table), exist_ok=True)
    cols = ["verdict", "comment", "fp", "boards", "qty", "need", "bom_code", "code", "model",
            "brand", "pkg", "lib", "stock", "price", "asked", "note"]
    with open(a.table, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for r in sorted(results, key=lambda r: (r["verdict"], r["comment"])):
            w.writerow(r)

    # BENCH_FITTED joins CERTIFIED and HAND_FIT as an acceptable, declared outcome: the row is real,
    # its disposition is known, and no purchase at JLCPCB is owed for it.
    bad = [r for r in results if r["verdict"] not in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED")]
    # THE SET'S OWN NUMBERS ARE THE DECLARED FOLDERS' ROWS. The table may be wider; the judgement is not.
    _decl_keys = set(rows_to_check(only, declared_only=True))
    _decl = [r for r in results if r.get("_key") in _decl_keys]
    _decl_counts = {}
    for r in _decl: _decl_counts[r["verdict"]] = _decl_counts.get(r["verdict"], 0) + 1
    _decl_bad = [r for r in _decl if r["verdict"] not in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED")]
    for r in bad[:40]:
        print("%-17s %-42s %s" % (r["verdict"], r["comment"][:42], r.get("note", "")[:70]))
    # What the declared input did on this run, and which declarations matched nothing (a stale declaration reads as
    # cover it is not giving, as a stale allow line does; named, not blocking, since a scoped run sees fewer rows).
    _held = {}
    for r in results:
        if r.get("declared_mismatch"): _held.setdefault(r["declared_mismatch"], []).append(r["comment"][:50])
    _stale = [e["id"] for e in decl["entries"] if e["id"] not in _held and e["id"] not in decl["cleared"]]
    print("jlc_certify: declared mismatches (%s): %d entries, %d row(s) held WRONG_MODEL by them, %d cleared by a "
          "decision, %d decision(s) refused%s" % (os.path.relpath(decl["path"], ROOT), len(decl["entries"]),
                                                  sum(len(v) for v in _held.values()), len(decl["cleared"]),
                                                  len(decl["refused"]),
                                                  ("; matching no row of this run: %s" % ", ".join(_stale)) if _stale else ""))
    # AND WHICH BOARDS THIS LINE IS NOT ABOUT (17 September 2026). The set's summary is read by the final gate
    # and printed where a person decides whether to order, so a count taken over three boards' folders must
    # not read like a count over seven. A board whose declared phase has no folder is named here every time.
    _miss = dict(getattr(newest_boms, "missing", {}) or {})
    print("\njlc_certify: %d components, %s%s" % (len(_decl), ", ".join(
        "%s %d" % (k, _decl_counts[k]) for k in sorted(_decl_counts)),
        ("; NOT CERTIFIED: %s (no deliverable folder at the declared phase %s)"
         % (", ".join(sorted(x.upper() for x in _miss)),
            ", ".join(sorted(set(v[0] for v in _miss.values()))))) if _miss else ""))
    # A PER-BOARD VERDICT BESIDE THE SET ONE (17 September 2026), the pattern check_contracts and final_gate
    # already use. Rules CMP-002 (the package on the land is the package ordered) and SUP-001 (every placed
    # part is buyable) are PER BOARD, and they were reading the SET's verdict: board D asks for two 6 MHz
    # crystals that do not exist and was certified against a 25 MHz part (owner decision 37), and that one
    # defect failed both rules on all seven boards, including four that carry no crystal at all. A row names
    # the boards it sits on, so each board can be asked about its own rows and nobody else's.
    # WHICH BOARD A ROW BELONGS TO IS THE BOARD'S DECLARED FOLDER (17 September 2026). The table above is
    # built over every folder, because it is this project's knowledge of what can be bought; the ATTRIBUTION
    # is built again over the folder each board declares, because a row that exists only in a folder cut three
    # phases ago is not a part of the board this tree holds. Before this, board A was certified from A24 while
    # its tree carries A32 and board D from D11 against D12, and the two rules these verdicts decide (CMP-002
    # and SUP-001) are per board.
    _declared = rows_to_check(only, declared_only=True)
    _ev_by_key = {r.get("_key"): r for r in results}
    _by_board = {}
    for _k, _rec in sorted(_declared.items()):
        _r = _ev_by_key.get(_k)
        if _r is None: continue
        for _l in sorted(_rec["boards"]):
            _l = _l.strip().lower()
            if _l: _by_board.setdefault(_l, []).append(_r)
    for _l, _rows in sorted(_by_board.items()):
        _bad = [r for r in _rows if r["verdict"] not in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED")]
        _nc = [r for r in _rows if r["verdict"] == "NOT_CHECKED"]
        verdict.write("jlc_certify_%s" % _l,
                      verdict.INCONCLUSIVE if _nc else (verdict.FAIL if _bad else verdict.PASS),
                      counts={k: sum(1 for r in _rows if r["verdict"] == k) for k in sorted({r["verdict"] for r in _rows})},
                      denominator=len(_rows), quiet=True,
                      evidence=["%s: %s (%s)" % (r["verdict"], r["comment"][:60], r.get("note", "")[:60]) for r in _bad[:20]],
                      note="the rows this board carries; the set's own verdict is jlc_certify", out_dir=a.out_dir)
    # A DECLARED ZERO IS AN ANSWER AND AN UNDECLARED ZERO IS NOT. Board E5 is the dock block: copper, holes
    # and plated targets, with no BOM and no part to buy, so it produces no row here. Left silent it would read
    # as "no verdict for this board" and both rules would go INCONCLUSIVE on a board that cannot fail them.
    try:
        import rules_status as _rs
        _set = [x.lower() for x in (_rs.manifest().get("boards") or {})]
    except BaseException:
        _set = [x.lower() for x in newest_boms(only)]
    _missing = dict(getattr(newest_boms, "missing", {}) or {})
    for _l in sorted(_set):
        if only and _l not in {x.lower() for x in only}: continue
        if _l in _by_board: continue
        # A BOARD WITH NO FOLDER AT ITS DECLARED PHASE IS NOT A BARE BOARD (17 September 2026). Both states
        # produce no row here and they are opposite answers: board E5 declares that it has no component to
        # buy, and board A has plenty and no folder cut at the phase its tree holds. Written as the same PASS,
        # the second read as "certified" about a board nobody had certified.
        if _l in _missing:
            _want, _have = _missing[_l]
            verdict.write("jlc_certify_%s" % _l, verdict.INCONCLUSIVE, counts={"folders": len(_have)},
                          denominator=0, quiet=True, out_dir=a.out_dir,
                          inputs={"board": _l, "declared_phase": _want},
                          evidence=["folders that exist: %s" % ", ".join(_have)],
                          missing_input=("no deliverable folder at the declared phase %s, so this board's parts "
                                         "were not certified against the board this tree holds (the folders "
                                         "that exist are %s)" % (_want, ", ".join(_have))))
            continue
        verdict.write("jlc_certify_%s" % _l.lower(), verdict.PASS, counts={}, denominator=0, quiet=True,
                      note="this board's deliverable carries no component row to certify (a bare board: copper, "
                           "holes and targets); a declared zero, not an absence", out_dir=a.out_dir)
    res = (verdict.INCONCLUSIVE if _decl_counts.get("NOT_CHECKED")
           else (verdict.FAIL if _decl_bad else verdict.PASS))
    # A SET VERDICT TAKEN OVER THREE BOARDS IS NOT A VERDICT ABOUT SEVEN (17 September 2026). With the folder
    # selection corrected, the boards whose declared phase has no folder produce no row at all, and a PASS
    # over what remains would say the set's parts are certified while four boards' parts were never read.
    # That is the project's own rule about a reading taken with less input, at set level: it goes out as
    # INCONCLUSIVE with the boards named, and `rules_status` will not let it stand in front of a reading that
    # had every board.
    _miss = dict(getattr(newest_boms, "missing", {}) or {})
    return verdict.write("jlc_certify", res, counts=_decl_counts, denominator=len(_decl),
                         evidence=["%s: %s (%s)" % (r["verdict"], r["comment"][:60], r.get("note", "")[:60])
                                   for r in _decl_bad[:30]]
                                  + (["not certified: %s (declared %s, folders %s)"
                                      % (l.upper(), v[0], ", ".join(v[1])) for l, v in sorted(_miss.items())]),
                         missing_input=(("%d board(s) have no deliverable folder at their declared phase (%s), "
                                         "so the set's parts were judged over the rest"
                                         % (len(_miss), ", ".join(sorted(x.upper() for x in _miss))))
                                        if _miss else None),
                         inputs={"declared_mismatches": os.path.abspath(decl["path"]),     # recorded by its sha256 (verdict.write)
                                 "held": {k: len(v) for k, v in sorted(_held.items())},
                                 "cleared": sorted(decl["cleared"]),
                                 "refused": ["%s: %s" % (i, w) for i, w in decl["refused"]],
                                 "matching_no_row": _stale},
                         note="table at %s" % os.path.relpath(a.table, ROOT), out_dir=a.out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
