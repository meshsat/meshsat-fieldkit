#!/usr/bin/env python3
"""Stream s122 (S-122, MESHSAT-1357): the parser and the name finder shared by `inventory.py`, `verdicts.py`, the
document corrections and the closure script.

It reads, and writes nothing:
  * the committed netlists of the six netlisted boards at the commit it runs in (`tx_inhibit.parse_netlist`), each by
    its sha256/16;
  * the documents CFL-016 names, parsed by headings into sections, then into table rows and cells, list items,
    quotes and paragraphs, then into sentences;
  * the scope: which sections of each document are CFL-016's (its statement, its notes and the brief of stream s122).

A sentence is inventoried when it names a part reference, a net, a board, a rail, a gate function, a generator line
or (round 4, set 14's check-int15-1 B1) a maker's part number (`names()`, key `parts`, found by `partnos()`); the
finder is a parser of tokens, never a judge of the sentence."""
import hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
import tx_inhibit as TX  # noqa: E402

NETLISTS = {"A": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net",
            "B": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net",
            "C": "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net",
            "D": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net",
            "E": "v2/ecad/pcb-e1-dock-e7/out/pcb-e1-dock.net",
            "P": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net"}
GENERATORS = {"A": "v2/ecad/tools/gen_sch_a.py", "B": "v2/ecad/tools/gen_sch_b.py", "C": "v2/ecad/tools/gen_sch_c.py",
              "D": "v2/ecad/tools/gen_sch_d.py", "E": "v2/ecad/tools/gen_sch_e.py", "P": "v2/ecad/tools/gen_sch_p.py"}

STATUS_KEY = "Current values of CONOPS's circuit passages (stream s122, 29 September 2026)"
# The scope: (document, the sections read). A section is named by the leading number or identifier of its heading
# ("1", "4b", "M4"); ALL means every section. `rows` narrows a section to the table rows whose first cell starts with
# one of the given words. Sources: CFL-016's statement and notes (pcb_requirements.yaml) and the brief of stream s122.
SCOPE = [
    ("v2/docs/PANEL.md", {"1": None, "2": None, "3": None, "5": None, "6": None, "7": None, "9": None, "10": None}),
    ("v2/docs/CONOPS.md", {"2a": None, "M2": None, "M4": None, "4": None, "4a": None, "4b": None, "4b.1": None, "4c": None,
                           "4d": None, "4e": None, "4f": None, "5": None}),
    ("v2/docs/V2-SPEC.md", "ALL"),
    ("v2/docs/OPERATING-ENVELOPE.md", {"2": None, "3": None, "4": None}),
    ("v2/docs/TEST-PLAN.md", "ALL"),
    ("v2/docs/ASSEMBLY.md", {"2": None, "4": None, "8": None, "9": None}),
    ("v2/ecad/tools/pcb_decisions.yaml", {"28": None, "40": None}),
    # round 2 (the baseline rule): where CONOPS's current circuit values are kept, judged directly
    ("v2/docs/feasibility/EMCON.md", {"0a.1": None}),
    ("v2/docs/handover/DEFINITION-STATUS.md", {STATUS_KEY: None}),
]
# CONOPS.md is a baselined definition (its head; handover/DEFINITION-STATUS.md): its circuit statements are read through
# the status page, so a CONOPS sentence whose value differs from the netlists is BASELINE when the status page keeps its
# current value (a row of STATUS_KEY's table), and STALE when it does not.
BASELINED = ("v2/docs/CONOPS.md",)
DASHES = ("\u2014", "\u2013")


AT = os.environ.get("S122_AT") or None   # read the documents at this commit (the netlists are always this tree's)


def read_bytes(rel):
    if AT and not rel.endswith(".net"):
        r = subprocess.run(["git", "-C", TOP, "show", "%s:%s" % (AT, rel)], capture_output=True, check=True)
        return r.stdout
    return open(os.path.join(TOP, rel), "rb").read()


def read(rel):
    return read_bytes(rel).decode("utf-8")


def sha16(rel):
    return hashlib.sha256(read_bytes(rel)).hexdigest()[:16]


def netlists():
    out = {}
    for k, rel in NETLISTS.items():
        nl = TX.parse_netlist(os.path.join(TOP, rel))
        if nl is None: raise SystemExit("s122lib: no netlist %s" % rel)
        nl["sha16"] = sha16(rel)
        nl["path"] = rel
        out[k] = nl
    return out


# ------------------------------------------------------------------ parsing
HEAD = re.compile(r"^(#{1,4})\s+(.*)$")


def sec_key(title):
    t = title.strip()
    m = re.match(r"^(\d+[a-z]?(?:\.\d+)?)[.\s]", t + " ")
    if m: return m.group(1)
    m = re.match(r"^(M\d|A\d+)[.\s]", t + " ")
    if m: return m.group(1)
    return t


def md_blocks(rel):
    """[(section key, section title, block kind, first line number, text, row key)] for a Markdown file. Table rows
    are one block per cell (kind 'cell:<n>'), list items and paragraphs one block each."""
    lines = read(rel).split("\n")
    out, key, title, para, pstart = [], "head", "head", [], 0
    stack = []
    item = []          # [key, title, first line, [texts], number] of the list item being read (round 3, check m7)

    def flush():
        nonlocal para, item
        if item:
            out.append((item[0], item[1], "item", item[2], " ".join(x.strip() for x in item[3]), item[4]))
        item = []
        if para:
            out.append((key, title, "para", pstart, " ".join(x.strip() for x in para), None))
        para = []
    for n, l in enumerate(lines, 1):
        m = HEAD.match(l)
        if m:
            flush()
            lvl, t = len(m.group(1)), m.group(2)
            k = sec_key(t)
            stack = [s for s in stack if s[0] < lvl] + [(lvl, k)]
            key, title = k, t
            out.append((key, title, "heading", n, t, None))
            continue
        s = l.strip()
        if not s:
            flush(); continue
        if s.startswith("|"):
            flush()
            if re.match(r"^\|[\s:|-]+\|$", s): continue
            cells = [c.strip() for c in s.strip("|").split(" | ")]
            rk = re.sub(r"[`*]", "", cells[0])[:40]
            for i, c in enumerate(cells):
                out.append((key, title, "cell:%d" % i, n, c, rk))
            continue
        m2 = re.match(r"^([-*]|(\d+)\.)\s+", s)
        if m2:
            flush()
            item = [key, title, n, [s[m2.end():]], m2.group(2)]
            continue
        if item and l[:1] in (" ", "\t"):
            item[3].append(s)          # a wrapped item's continuation line
            continue
        if item:
            flush()
        if s.startswith(">"):
            s = s.lstrip("> ").strip()
            if not para: pstart = n
            para.append(s); continue
        if not para: pstart = n
        para.append(s)
    flush()
    return out


def yaml_blocks(rel, numbers):
    import yaml
    d = yaml.safe_load(read(rel))
    raw = read(rel).split("\n")
    out = []
    for x in d["decisions"]:
        if str(x["n"]) not in numbers: continue
        ln = next(i for i, l in enumerate(raw, 1) if l.strip() == "- n: %d" % x["n"])
        for f in ("outcome", "reversed_by"):
            out.append((str(x["n"]), x.get("title", ""), "field:" + f, ln, str(x.get(f, "")), f))
    return out


ABBR = r"(?<!\be\.g)(?<!\bi\.e)(?<!\bvs)(?<!\bno)(?<!\bNo)(?<!\bFig)(?<!\bpp)(?<!\bapprox)(?<!\bSt)(?<!\bet al)"
SPLIT = re.compile(ABBR + r"(?<=[.!?:;])\s+(?=(?:\*\*)?[A-Z`\"(\[])")


def sentences(text):
    """Split a block into sentences on '.', '!', '?' and on ';' or ':' before a capital (the documents run clauses
    together with semicolons); never inside a backtick span."""
    spans = [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", text)]
    out, last = [], 0
    for m in SPLIT.finditer(text):
        if any(a < m.start() < b for a, b in spans): continue
        if text[m.start() - 1] in ";:" : continue           # keep a clause with its sentence
        if re.search(r"\b\d+\.$", text[last:m.start()]) and re.match(r"\d", text[m.end():m.end() + 1] or ""): continue
        s = text[last:m.start()].strip()
        if s: out.append(s)
        last = m.end()
    s = text[last:].strip()
    if s: out.append(s)
    return out


def in_scope(rel, spec, key, kind, rowkey):
    if spec == "ALL": return True
    if key not in spec: return False
    rows = spec[key]
    if rows is None: return True
    if kind.startswith("cell:") and rowkey is not None:
        return any(rowkey.startswith(r) for r in rows)
    if kind == "item" and rowkey is not None:
        return rowkey in rows
    return False


# ------------------------------------------------------------------ names
REF = re.compile(r"(?<![\w{/.-])((?:U|R|C|D|Q|J|L|F|FB|TP|SW|BZ|Y|JP|K|X|LED)\d{1,3}[A-Z]?|J_[A-Z0-9_]+|SW_[A-Z]+|U_LIGHT"
                 r"|(?:U|Q|R|C)\{s\}\d\d|PIJ2_[AB])(?![\w-])")
GEN = re.compile(r"(gen_sch_[a-z]\d*\.py|gen_pcb_[a-z]\d*\.py|stackup_write\.py|panel1450\.py)`?(?::(\d+(?:-\d+)?(?:(?:,|,? and) `?:\d+(?:-\d+)?`?)*))?")
BOARD = re.compile(r"\b(?:board [ABCDEP]\b|boards? [A-E](?: and [A-E])+|A2[0-9]\b|B1[0-9]\b|C[5-8]\b|D[6-9]\b|E[4-7]\b|P[2-9]\b|"
                   r"PCB-[A-E]\b|[ABCDEP]'s\b|the dock strip|the pack board|the backer|the generated boards?|(?i:as generated))")
RAIL = re.compile(r"(?<![\w])(\+\d+V\d*(?:_[A-Z0-9]+)*|\+\d+V\d+|VBAT|VSYS|VBUS\d*|SHORE_12V|VIN_RAW|rails?)(?![\w])")
GATE = re.compile(r"\b(AND|NOR|NAND|OR gate|inverter|inverts?|buffer|Schmitt|open[- ]drains?|load switch|eFuse|supervisor|"
                  r"gate[sd]?|pull[- ]?(?:up|down)s?|pulled (?:low|high|up|down)|interlock|comparator|enable[sd]?|load switch(?:es)?|back-feed)\b")


TOPIC = re.compile(r"\bEMCON\b")
NUMW = "two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty"
COUNT = re.compile(r"\b(%s)\s+(?:\w[\w&/.-]*\s+){0,4}?(LEDs?|pins?|sockets?|cards?|receptacles?|holders?|fuses?|"
                   r"resistors?|switch(?:es)?|toggles?|jacks?|headers?|connectors?|contacts?|gates?|supervisors?|monitors?|"
                   r"expanders?|drives?|coolers?|fans?|lands?|arrestors?|buffers?|converters?|slots?)\b" % NUMW, re.I)


def expand(tok):
    if "{s}" in tok: return [tok.replace("{s}", str(s)) for s in (1, 2, 3)]
    return [tok]


def all_nets(nls):
    s = set()
    for nl in nls.values(): s |= set(nl["nets"])
    return s


NETLIKE = re.compile(r"(?<![\w+/.-])(\+?[A-Z][A-Z0-9]*(?:_[A-Za-z0-9#]+)+|[A-Z][A-Z0-9]{1,}_?[nN]|\+\d+V\d*(?:_[A-Z0-9]+)*)(?![\w])")


def names(s, nets):
    """What a sentence names: refs, nets, boards, rails, gate words and generator citations."""
    body = s
    refs = sorted({r for m in REF.finditer(body) for r in expand(m.group(1))})
    nn = set()
    for m in re.finditer(r"`([^`]+)`", body):
        t = m.group(1)
        for tok in re.split(r"[\s/,()]+", t):
            tok = tok.strip(".;:")
            if tok in nets: nn.add(tok)
            mm = re.match(r"^(.*?)(\d)\.\.(\d)$", tok)
            if mm:
                for i in range(int(mm.group(2)), int(mm.group(3)) + 1):
                    if mm.group(1) + str(i) in nets: nn.add(mm.group(1) + str(i))
    for m in NETLIKE.finditer(body):
        if m.group(1) in nets: nn.add(m.group(1))
    gens = [(m.group(1), m.group(2)) for m in GEN.finditer(body)]
    boards = sorted({m.group(0) for m in BOARD.finditer(body)})
    rails = sorted({m.group(1) for m in RAIL.finditer(body)})
    gates = sorted({m.group(1).lower() for m in GATE.finditer(body)})
    topic = ["EMCON"] if TOPIC.search(body) else []
    counts = sorted({m.group(0) for m in COUNT.finditer(body)})
    return {"refs": refs, "nets": sorted(nn), "boards": boards, "rails": rails, "gates": gates, "gens": gens,
            "topic": topic, "counts": counts, "parts": partnos(body)}


# round 3 read four words; round 4 (check-s122-3 m2: other wordings of the same class) reads the wordings the check swept
ABSENT = re.compile(r"\b(absent|owed|not drawn|not connected|not gated|has no|have no|does not have|do not have|nothing does|"
                    r"lacks?|no path|no hardware|only through|driven only|in the schematic|until [^.;]{0,80}generators?)\b", re.I)

# ------------------------------------------------------------------ makers' part numbers (round 4)
# A maker's part number is read by its shape, never from a list of known parts:
#   * a letter-led token of upper-case letters and digits (with - or / inside) of five characters or more that holds a
#     run of three digits or more (TMDS341A, LM5069, RA30H1317M1, E22-900M30S, D38999/26FC4SN);
#   * a digit-led token that holds a capital letter and four digits or more (74LVC1G157GW, 2N7002, 5636ADKB-2V);
#   * a digit-only token with a dash or slash that holds a run of six digits (2199119-3, 1-2199119-5, 132134-11);
#   * a series word of two to four capitals, a space, and a digit-led token with a dash and three digits or more
#     (TEN 40-2412WIN, APEM 5636ADKB-2V; not "FOR 1-CELL");
#   * the same shapes in the file name of a maker's sheet the sentence cites (`m2/amphenol-mdt420b01001-m2-b-key.pdf`
#     gives MDT420B01001): a row's source names the part the row relies on.
# Not part numbers: a token with a lower-case letter (a commit, a unit), a registry or standard identifier (letters,
# dashes, then one number: CFL-016, MIL-STD-810, AEC-Q100), a token led by a standard body (IEC, EN, ISO, UN, ...), a
# pure range of two numbers of up to four digits (144-146), a file path, a URL, a commit and a generator citation
# (removed before the scan).
STDBODY = {"IEC", "EN", "ISO", "UN", "MIL", "IPC", "ECSS", "ETSI", "SAE", "NATO", "ANSI", "IEEE", "JEDEC", "RTCA", "EIA",
           "UL", "CISPR", "ITU", "IP", "DO"}
PN_STRIP = re.compile(r"https?://\S+|[\w./-]+\.(?:py|md|yaml|json|out|net|pdf|kicad_\w+|csv|txt|sh|step|stp)(?::\d+(?:-\d+)?)?"
                      r"|\b(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")   # a commit holds a letter a to f; 2199119 is a part
PN_TOK = re.compile(r"(?<![\w/.+-])([A-Za-z0-9][A-Za-z0-9/-]*[A-Za-z0-9])(?![\w/+-]|\.\w)")
PN_ID = re.compile(r"^[A-Z]+(?:-[A-Z]+)*-[A-Z]?\d+[a-z]?$")
PN_SERIES = re.compile(r"\b([A-Z]{2,4}) (\d[0-9A-Z]*-[0-9A-Z-]*[0-9A-Z])\b")


def is_partno(t):
    """True when the token has a maker's part number's shape (the rules above)."""
    if re.search(r"[a-z]", t) or not re.search(r"\d", t): return False
    if t[0].isalpha():
        return (len(t) >= 5 and bool(re.search(r"\d{3}", t)) and not PN_ID.match(t)
                and re.split(r"[-/]", t)[0] not in STDBODY)
    if re.search(r"[A-Z]", t):
        return len(t) >= 5 and len(re.findall(r"\d", t)) >= 4
    return bool(re.search(r"\d{6}", t)) and bool(re.search(r"[-/]", t))


PN_SHEET = re.compile(r"[\w./-]*?([\w-]+)\.(?:pdf|html?)\b")


def partnos(s):
    """The makers' part numbers a sentence names, by shape (`is_partno`), a series word kept with its number, and those
    in the file names of the sheets it cites."""
    out = set()
    for m in PN_SHEET.finditer(s):
        for seg in re.split(r"[-_]", m.group(1)):
            if is_partno(seg.upper()) and not re.fullmatch(r"\d+", seg): out.add(seg.upper())
    body = PN_STRIP.sub(" ", s)
    for m in PN_SERIES.finditer(body):
        if m.group(1) not in STDBODY and len(re.findall(r"\d", m.group(2))) >= 3: out.add(m.group(1) + " " + m.group(2))
    for m in PN_TOK.finditer(body):
        tok = m.group(1)
        if is_partno(tok) and not any(tok != x and tok in x.split(" ") for x in out): out.add(tok)
    return sorted(out)


def inventory(nls=None):
    """[(id, doc, section, kind, line, sentence, names)] for every in-scope sentence that names something, and every
    sentence of a baselined document that states something absent, owed, not drawn or not connected (the wordings of
    ABSENT)."""
    nls = nls or netlists()
    nets = all_nets(nls)
    inv = []
    for rel, spec in SCOPE:
        if rel.endswith(".yaml"):
            blocks = yaml_blocks(rel, spec)
            spec2 = "ALL"
        else:
            blocks, spec2 = md_blocks(rel), spec
        cnt = {}
        for key, title, kind, line, text, rowkey in blocks:
            if kind == "heading": continue
            scoped = in_scope(rel, spec2, key, kind, rowkey)
            if not scoped and rel not in BASELINED: continue
            for s in sentences(text):
                # round 3 (check-s122-2, B1): every sentence of a baselined document that states something is absent,
                # owed, not drawn or not connected is inventoried, in any section, named or not
                absent = rel in BASELINED and bool(ABSENT.search(s))
                if not scoped and not absent: continue
                nm = names(s, nets)
                if not any(nm.values()) and not absent: continue
                if kind.startswith("cell:") and rowkey:
                    nm["row"] = [rowkey]      # round 4: a cell's row label, which names the board of a boards table row
                base = "%s#%s:L%d:%s" % (os.path.basename(rel), key, line, kind)
                cnt[base] = cnt.get(base, 0) + 1
                inv.append(("%s:s%d" % (base, cnt[base]), rel, key, kind, line, s, nm))
    return inv


def sid_digest(s):
    return hashlib.sha256(" ".join(s.split()).encode()).hexdigest()[:10]
