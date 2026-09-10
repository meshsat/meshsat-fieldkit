#!/usr/bin/env python3
"""kb_parts.py, the parts this design builds with against the documents we hold (MESHSAT-862, 10 September 2026).

The store's most useful output is not a passage, it is the list of parts it CANNOT answer about. Every
`ic()` call in a schematic generator names its part in the first token of its value string, so the list
of parts this design actually instantiates is mechanical rather than remembered, and each one is looked
up in the store: does any page of any indexed document mention it.

A part with no document is not a small thing here. `TPS2065CDBV` sat on a SOT-23-6 land for four board
phases because a footprint key is a claim about a package and nobody checked it; the sheet that would
have settled it in one line is not in this tree. The rule of section 8 of the handover, confirm the
package from the same datasheet page, cannot be followed for a part whose datasheet we do not have.

Usage: kb_parts.py [--missing] [--json] [--board b]      (--missing lists only what has no document)
"""
import sys, os, ast, glob, json, argparse, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kbdb, kbenv                      # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
# A part number: letters and digits, at least five characters, carrying both. Passives (10k, 100n) and
# the generic footprint keys never match, which is the point: this list is ICs, modules and connectors.
# A part-number shape: starts with a letter, carries a digit, at least six characters. Package names,
# net names and pin labels have the same shape, so they are excluded by pattern rather than guessed at,
# and anything that slips through simply shows up in the report as a part with no document, where it is
# obvious. Over-listing is cheap; missing a part we cannot check is the expensive direction.
PART = re.compile(r"\b(?=[A-Za-z0-9-]*[0-9])[A-Z][A-Za-z0-9]{2,}[0-9][A-Za-z0-9]*(?:[-/][A-Za-z0-9.]+)*\b")
NOT_A_PART = re.compile(
    r"^(?:GPIO\d+|BCM\d+|VBUS\d+|POGO\d+|"
    r"SOD\d+\w*|SOT\d+\w*|SOIC\d+|SO\d+EP|SSOP\d+|TSSOP\d+|HTSSOP\d+|VSSOP\d+|MSOP\d+|"
    r"QFN\d+|WQFN\d+|VQFN\d+|UQFN\d+|DFN\d+|TDSON\d+|USON\d+|MLPD\d+|LQFP\d+|TQFP\d+|QFP\d+|"
    r"BGA\d+|DDA\d+|TSOT\d+|PH\d+x\d+|RS\d{4}|R\d{4}|C\d{4}|L\d{4}|LED\d{4}|"
    r"USB\d|PCIE\d?|HDMI\d?|DSI\d|CSI\d|UART\d|SPI\d|I2C\d|CAN\d|ETH\d|"
    r"X7R|X5R|NP0|C0G|CR\d{4}|M2\.5|M\d|"
    # LCSC order codes: the generators carry them beside the part, and they are not documents
    r"C\d{3,9}|"
    # net and pin labels that happen to have the shape of a part number
    r"SPARE\d+|HUBRST\d+|PRSNT\d+|OUTPUT\d+|INPUT\d+|WIFI\d+|PICO\d+|SLOT\d+|BANK\d+|CH\d+|"
    # more package spellings, including the ones drawn as library footprint names
    r"LQFP\d+EP|TQFP\d+EP|LGA\d+\w?|CPOL\d+|C\d+u\d+|R[A-Z]{2}\d{4}[A-Z]?-\d+|DBV\d?|DRV\d?)$", re.I)
SKIP = {"SWD", "NOTE", "PADS", "TEST"}


def _first_token(node):
    """The part number of an ic() value: the first word of its string, through a % format if there is one."""
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        node = node.left
    if isinstance(node, ast.JoinedStr):
        node = node.values[0] if node.values else None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        head = node.value.strip().split()
        return head[0] if head else None
    return None


def parts_from_generators():
    """{part: {"boards": set, "lcsc": set, "note": str}} over every string a gen_sch_*.py holds.

    Not only `ic()` calls: most boards wrap `ic()` in helpers (`nfet`, `ina219`, an eFuse builder) and
    the part number then lives in the helper's own format string. Scanning every string literal finds
    those, at the price of some package names, which the pattern above excludes."""
    out = {}
    for path in sorted(glob.glob(os.path.join(TOOLS, "gen_sch_*.py"))):
        board = os.path.basename(path)[len("gen_sch_"):-3]
        try:
            tree = ast.parse(open(path, errors="replace").read())
        except SyntaxError as e:
            print("kb_parts: %s does not parse (%s)" % (os.path.basename(path), e), file=sys.stderr)
            continue
        lcsc_here = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                if re.fullmatch(r"C\d{3,9}", node.value.strip()):
                    lcsc_here.add(node.value.strip())
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Constant) and isinstance(node.value, str)):
                continue
            text = node.value
            for tok in PART.findall(text):
                if len(tok) < 6 or tok.upper() in SKIP or NOT_A_PART.match(tok):
                    continue
                rec = out.setdefault(tok, {"boards": set(), "lcsc": set(), "note": ""})
                rec["boards"].add(board)
                if not rec["note"]:
                    rec["note"] = " ".join(text.split())[:110]
    return out


def variants(part):
    """A datasheet names the family, an order code names the reel. TPS259631DDAR is documented as
    TPS25963x; AP2112K-3.3 as AP2112. So a part is looked up by its number and by shorter stems of it,
    longest first, and the stem that hit is reported so a thin match is visible as a thin match."""
    p = part.upper()
    out = [p]
    base = re.split(r"[-/]", p)[0]
    if base != p:
        out.append(base)
    # The family stem: the LONGEST prefix that ends in a digit and is followed by a letter, which is
    # where a manufacturer's order code starts. TPS2065CDBV -> TPS2065, TMP117AIDRVR -> TMP117,
    # M2044SD3A01 -> M2044 (the NKK sheet spells only the family), STM32H753VITx -> STM32H753.
    # Longest, not shortest: shortest would turn TPS2065CDBV into TPS20 and match half of TI.
    stem = None
    for i in range(len(base) - 1, 3, -1):
        if base[i - 1].isdigit() and base[i].isalpha():
            stem = base[:i]
            break
    if stem and len(stem) >= 5 and stem not in out:
        out.append(stem)
    return out


def lookup(db, part):
    """(matched_variant, relpath, page, how) for the first variant the tree carries, else None.

    Two places are searched, and the filename is not an afterthought: `rf/radiall-R222M00720-tds.pdf`
    is that part's datasheet and its pages never spell the order code, so a text-only search called a
    present document missing. A missing-datasheet report that invents missing datasheets is worse than
    none, because it sends someone to fetch what is already here."""
    for v in variants(part):
        with db.cursor() as c:
            c.execute("SELECT d.relpath, MIN(c.page) FROM chunks c JOIN documents d ON d.id=c.document_id "
                      "WHERE d.present=1 AND c.page>0 AND c.text LIKE %s GROUP BY d.relpath "
                      "ORDER BY (d.status='current') DESC, COUNT(*) DESC LIMIT 1", ("%" + v + "%",))
            row = c.fetchone()
        if row:
            return v, row[0], row[1], "text"
        with db.cursor() as c:
            # LOWER() on both sides: relpath is utf8mb4_bin (a case sensitive tree, see schema.sql)
            # and a file is named in lower case while a part number is written in upper case, so a
            # plain LIKE reported connectors/amphenol-rjhse5380-rj45-jack.pdf as a missing document
            # minutes after it was added.
            c.execute("SELECT relpath FROM documents WHERE present=1 AND LOWER(relpath) LIKE %s "
                      "ORDER BY (status='current') DESC LIMIT 1", ("%" + v.lower() + "%",))
            row = c.fetchone()
        if row:
            return v, row[0], 0, "filename"
    return None


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--missing", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--board")
    a = ap.parse_args(argv)
    parts = parts_from_generators()
    if a.board:
        parts = {k: v for k, v in parts.items() if a.board in v["boards"]}
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return 3
    rows, missing = [], []
    for part in sorted(parts):
        hit = lookup(db, part)
        rec = {"part": part, "boards": sorted(parts[part]["boards"]), "lcsc": sorted(parts[part]["lcsc"]),
               "note": parts[part]["note"]}
        if hit:
            rec.update({"matched": hit[0], "relpath": hit[1], "page": hit[2], "how": hit[3],
                        "exact": hit[0] == part.upper()})
        else:
            missing.append(rec)
        rows.append(rec)
    if a.json:
        print(json.dumps({"parts": len(rows), "missing": len(missing), "rows": rows}, indent=1))
        return 0
    for r in rows:
        if a.missing and "relpath" in r:
            continue
        if "relpath" in r:
            mark = "  " if r["exact"] else "~ "     # ~ = matched a shorter family stem, not the exact number
            where = ("p.%s" % r["page"]) if r["how"] == "text" else "(filename only, its pages do not spell it)"
            print("%s%-26s %-10s %s %s" % (mark, r["part"], ",".join(r["boards"]), r["relpath"], where))
        else:
            print("MISSING %-26s %-10s %-10s %s" % (r["part"], ",".join(r["boards"]),
                                                    ",".join(r["lcsc"]) or "-", r["note"]))
    print("\nkb_parts: %d parts named by the schematic generators, %d with no document in this tree"
          % (len(rows), len(missing)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
