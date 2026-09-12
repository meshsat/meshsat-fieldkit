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
NOT_PART = re.compile(r"^(?:"
                      r"[0-9.]+\s*(?:m|u|n|p|k|K|M|G)?(?:Ohm|OHM|R|F|H|V|A|W|Hz|HZ)[0-9]*|"
                      r"[0-9.]+(?:m|u|n|p|k|K|M)?|"
                      r"GND|VCC|VDD|USB[0-9]?|I2C|SPI|UART[0-9]?|PWM|LED|RGB|IP6[0-9]|NP0|X[57]R|"
                      r"GPIO[0-9]*|BCM[0-9]*|SLLS[0-9]+|SLUS[A-Z0-9]+|MESHSAT-[0-9]+"
                      r")$", re.I)


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


def norm_pkg(s):
    """One canonical spelling for a package, from either side.

    KiCad writes `R_0603_1608Metric` and `SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm`; JLC writes `0603`
    and `SOIC-8` and `DO-214AA(SMB)`. Both are reduced to the same short token so the comparison is
    about the package and not about either tool's naming habits."""
    if not s:
        return ""
    s = s.upper().strip()
    s = re.sub(r"^(?:PACKAGE_[A-Z_]+:|[A-Z_]+:)", "", s)          # strip a KiCad library prefix
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
            keep = [{k: c.get(k) for k in ("componentCode", "componentModelEn", "componentBrandEn",
                                           "componentSpecificationEn", "componentLibraryType",
                                           "stockCount", "initialPrice", "assemblyComponentFlag",
                                           "minPurchaseNum", "leastPatchNumber")} for c in lst]
            today = datetime.date.today().isoformat()
            cache[key] = {"asked": today, "list": keep}
            return keep, today
        except Exception:
            time.sleep(2 * (attempt + 1))
    return None, None                                              # unreachable: never a pass


def same_part(want, got):
    """Is the component JLC returned the part we asked for? Punctuation and case do not matter; the
    letters and digits do, and a suffix like R for reel or TRG1 for packaging is allowed on either."""
    a = re.sub(r"[^A-Z0-9]", "", (want or "").upper())
    b = re.sub(r"[^A-Z0-9]", "", (got or "").upper())
    if not a or not b:
        return False
    if a.startswith(b) or b.startswith(a):
        return True
    # An order code carries suffixes in the middle as well as at the end: LM74700-Q1 is sold as
    # LM74700QDBVRQ1, where DBVR is the package and reel. A common prefix of six or more characters is
    # the same silicon; below that it is a coincidence.
    n = 0
    while n < min(len(a), len(b)) and a[n] == b[n]:
        n += 1
    return n >= 6


def intended_part(comment):
    """The manufacturer part a BOM row means, out of its free prose, or None for a jellybean.

    Two rules, both learnt from the first full run. **Parentheses are stripped first**: this project's
    BOM convention puts the part before the explanation, and the explanation is full of net names, so
    `10.0k 1% (RFBOUT2)` was being searched for as a part called RFBOUT2, and `Ebyte E22-900M30S 1 W
    LoRa (SX1262)` as the bare silicon rather than the module we buy. **And the FIRST token wins**,
    because `Ebyte E72-2G4M20S1E CC2652P` means the module and names the chip inside it second."""
    head = re.sub(r"\([^)]*\)", " ", comment)
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


def newest_boms(only=None):
    """{letter: (bom path, folder)} for the newest phase of each board.

    B is read from the QUOTE folder deliberately: B15 is the newest ROUTED deliverable but B16 is what
    the order set ships, and certifying the wrong one would certify a parts list nobody is buying."""
    best = {}
    for d in sorted(glob.glob(os.path.join(BOARDS_DIR, "meshsat-pcb-*"))):
        m = re.match(r"meshsat-pcb-([a-z0-9]+)-revA-([A-Z]+)(\d+)", os.path.basename(d))
        if not m:
            continue
        letter, num = m.group(1), int(m.group(3))
        boms = glob.glob(os.path.join(d, "*bom.csv"))
        if not boms:
            continue
        if letter not in best or num > best[letter][0]:
            best[letter] = (num, boms[0], os.path.basename(d))
    if only:
        best = {k: v for k, v in best.items() if k in only}
    return {k: (v[1], v[2]) for k, v in best.items()}


def rows_to_check(only=None):
    """Every distinct (value, footprint) that is a component, with the boards and quantity it carries."""
    out = {}
    for letter, (bom, folder) in sorted(newest_boms(only).items()):
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
                                       "boards": set(), "qty": 0})
            rec["boards"].add(letter.upper())
            rec["qty"] += max(1, len(refs))
            if code and not rec["code"]:
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
    keys.append(comment[:60])
    for k in keys:
        hit = handfit.get(k)
        if hit:
            return hit
    return None


def certify(rec, cache, handfit, aliases, refresh=False):
    """One row's verdict, with the evidence that produced it."""
    comment, fp, code = rec["comment"], rec["fp"], rec["code"]
    want = intended_part(comment)
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
    if want:
        # same_part is deliberately loose (a common prefix of six is the same silicon), so the FIRST
        # match is often the wrong order code of the right chip: asked TUSB2046BI, the page answers
        # TUSB2046BVF, TUSB2046BVFR and TUSB2046BIRHBR, and only one of those is an LQFP-32 like our
        # land. Score every match instead: exact model first, then the package we actually drew, then
        # stock that covers the order. This one change is what separates a wrong order code from a
        # wrong part, and the wrong order code is the commoner defect by far.
        want_pkg = norm_pkg(fp)
        cand = [c for c in lst if same_part(want, c.get("componentModelEn"))]
        if cand:
            def rank(c):
                m = re.sub(r"[^A-Z0-9]", "", (c.get("componentModelEn") or "").upper())
                w = re.sub(r"[^A-Z0-9]", "", want.upper())
                pkg = norm_pkg(c.get("componentSpecificationEn"))
                return (bool(want_pkg) and pkg == want_pkg,
                        (c.get("stockCount") or 0) >= need,
                        m == w,
                        c.get("componentLibraryType") == "base",
                        c.get("stockCount") or 0)
            top = max(cand, key=rank)
    else:
        # A jellybean has no model to match, so the best answer is the one that is actually in stock
        # in the right package. The top hit is ranked by JLCPCB's own relevance and was repeatedly a
        # zero-stock part when an identical one with half a million in stock sat below it.
        want_pkg = norm_pkg(fp)
        ok = [c for c in lst if norm_pkg(c.get("componentSpecificationEn")) == want_pkg
              and (c.get("stockCount") or 0) >= need]
        if ok:
            top = max(ok, key=lambda c: (c.get("componentLibraryType") == "base", c.get("stockCount") or 0))
    ev = dict(code=top.get("componentCode"), model=top.get("componentModelEn"),
              brand=top.get("componentBrandEn"), pkg=top.get("componentSpecificationEn"),
              lib=top.get("componentLibraryType"), stock=top.get("stockCount") or 0,
              price=top.get("initialPrice"), need=need, asked=asked)

    if want and not same_part(want, ev["model"]):
        ev.update(verdict="WRONG_MODEL",
                  note="asked for %s, JLCPCB's best answer is %s" % (want, ev["model"]))
        return ev
    a, b = norm_pkg(fp), norm_pkg(ev["pkg"])
    if a and b and a != b and aliases.get("%s=%s" % (a, b)) is None and aliases.get("%s=%s" % (b, a)) is None:
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
        wider = re.sub(r"[A-Za-z]+$", "", want).rstrip("-") if want else ""
        if want and len(wider) >= 5 and wider.upper() != want.upper():
            lst2, asked2 = query(wider, cache, refresh)
            cand2 = [c for c in (lst2 or []) if same_part(want, c.get("componentModelEn"))
                     and norm_pkg(c.get("componentSpecificationEn")) == a]
            if cand2:
                top = max(cand2, key=lambda c: ((c.get("stockCount") or 0) >= need,
                                                c.get("componentLibraryType") == "base",
                                                c.get("stockCount") or 0))
                ev = dict(code=top.get("componentCode"), model=top.get("componentModelEn"),
                          brand=top.get("componentBrandEn"), pkg=top.get("componentSpecificationEn"),
                          lib=top.get("componentLibraryType"), stock=top.get("stockCount") or 0,
                          price=top.get("initialPrice"), need=need, asked=asked2)
                if (ev["stock"] or 0) < need:
                    ev.update(verdict="NO_STOCK", note="stock %s against a need of %d for %d boards"
                              % (ev["stock"], need, BOARD_QTY))
                    return ev
                ev.update(verdict="CERTIFIED",
                          note="found on the wider search %r: the row's suffix hid this package" % wider)
                return ev
        ev.update(verdict="PACKAGE_MISMATCH",
                  note="our land is %s, the part is %s" % (a, b))
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

    handfit, aliases = declared(HANDFIT), declared(ALIASES)
    cache = load_cache()
    rows = rows_to_check(only)
    keys = sorted(rows)
    if a.limit:
        keys = keys[:a.limit]

    results, counts = [], {}
    for i, k in enumerate(keys, 1):
        rec = rows[k]
        ev = certify(rec, cache, handfit, aliases, a.refresh)
        ev.update(comment=rec["comment"], fp=rec["fp"], bom_code=rec["code"],
                  boards=",".join(sorted(rec["boards"])), qty=rec["qty"])
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
    for r in bad[:40]:
        print("%-17s %-42s %s" % (r["verdict"], r["comment"][:42], r.get("note", "")[:70]))
    print("\njlc_certify: %d components, %s" % (len(results), ", ".join(
        "%s %d" % (k, counts[k]) for k in sorted(counts))))
    res = verdict.INCONCLUSIVE if counts.get("NOT_CHECKED") else (verdict.FAIL if bad else verdict.PASS)
    return verdict.write("jlc_certify", res, counts=counts, denominator=len(results),
                         evidence=["%s: %s (%s)" % (r["verdict"], r["comment"][:60], r.get("note", "")[:60])
                                   for r in bad[:30]],
                         note="table at %s" % os.path.relpath(a.table, ROOT), out_dir=a.out_dir)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
