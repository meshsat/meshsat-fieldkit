#!/usr/bin/env python3
"""Regeneration parity: is a committed artefact exactly what its generator produces? (MESHSAT-1357, 26 September 2026.)

The owner's condition 5 of 25 September 2026 says "generator is current" needs parity, not a claim. This is the
instrument the regeneration parity run used (W7, box 52646493, commit 82dd1e4d, KiCad 9.0.9, 25 September): it read
PARITY or PARITY_AFTER_NOISE for the schematic, netlist, intent, provenance, BOM and ERC of boards A, B, C, D, E and P,
and it is committed here with fixtures (tests/test_regen_compare.py) so the next run is the same instrument.

For each artefact kind it removes ONLY the fields on a closed noise list, counts every removal, then compares what is
left. Anything not on the list is a difference, reported with a bucket that says what kind.

  schematic (.kicad_sch)
    N1  title_block (date "YYYY-MM-DD"), one per file: every gen_sch_<x>.py writes today's date into its title_block.
    N2  the page-frame date, one per page: schlayout.py's frame writes
        "page k of n   MeshSat field kit V2, CERN-OHL-S-2.0   PROTOTYPE, nothing built   <date>" (schlayout.Engine.frame).
        The first version of this comparator left it out and a date-only change read DIFFERENT; the fixture
        `t_every_date_the_generator_writes_is_noise_and_nothing_else_is` holds it. A YYYY-MM-DD string always has
        the same width, so the text's position does not move with it.
    L1  comment 1 "Phase <label>" and L2 the page-frame heading "<board title>   <label>" (the same frame): both
        come from the PHASE environment. They are REPORTED (phase_labels, labels_differ) and normalised, so a label
        difference is visible without hiding a design difference.
  netlist (.net)
    N3  (design (source ...) (date ...) (tool ...)): the export's own path, time and KiCad build.
    N4  the sheet title_block (date "YYYY-MM-DD"), the schematic's N1 as the export copies it.
    L1  comment 1 "Phase <label>" in the sheet title_block (reported, as above).
    If the text still differs, a semantic comparison (components: value, footprint, fields, libsource, properties;
    nets: name to sorted (ref, pin, pinfunction, pintype)) classifies it, and a component's tstamps (its uuid5 place
    in the generator's sequence, kisch.py) is counted apart, because inserting one part shifts every later one.
  intent (-intent.json)       N5 "written" (intent.py, the time it was written).
  provenance (.net.prov.json) N6 "taken" (sch_prov.py). schematic_sha256 is NOT noise: it must equal the first 32
                              hex of sha256(the schematic beside it) on BOTH sides, and the two schematics must read
                              PARITY or PARITY_AFTER_NOISE; only then is its difference explained by N1 and N2.
  bom (-bom.csv)              no noise: a sorted row set (same rows in another order is PARITY_AFTER_NOISE).
  erc (-erc.json)             a multiset of (severity, type, description, sorted item descriptions); N7 coordinates
                              and uuids are dropped, because they are positions, not findings.
  board_vs_net                the committed board against its committed netlist, per reference as netlist_parts.py
                              reads it (rule SCH-002's companion): a value, a land, an order code or a reference on
                              one side only is a difference (`board_vs_net` says why this is stricter than the gate).
  sch002_v-*                  a netlist_board verdict found in the run's v-committed/ or v-regen/, reported beside the
                              rows and never counted in the exit code: it is a gate's reading, not a comparison.

Usage:
  regen_compare.py pair <kind> <committed file> <other file>   one comparison, JSON on stdout
  regen_compare.py box  <repo clone> <box out dir>              every board whose routeflow profile names it
exit 0 when every comparison is PARITY or PARITY_AFTER_NOISE, 1 otherwise.

THE BOX LAYOUT `box` READS. The driver that produces it is the regeneration run on a KiCad box (W7's
w7_regen_box.sh, not in this tree yet): for each letter <L>, `<out>/<L>/ref/` holds kicad-cli's exports of the
COMMITTED schematic (netlist, BOM, ERC JSON), `<out>/<L>/regen/` the regenerated schematic, netlist, intent,
provenance, BOM and ERC, and `<out>/<L>/v-committed/` and `v-regen/` any netlist_board verdicts. The committed files
are read from the clone's HEAD with `git show`, whatever its working tree holds. Which directory is a board's is read
from the clone's own routeflow profile (`project`) and board table, never guessed from a directory listing.
"""
import csv, glob, hashlib, io, json, os, re, subprocess, sys, difflib
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist_parts  # noqa: E402


def _read(p):
    return open(p, encoding="utf-8", errors="replace").read()


def blocks(t, head):
    """Every balanced S-expression block in `t` that starts with the literal `head`, quoted strings respected."""
    out, i = [], 0
    while True:
        i = t.find(head, i)
        if i < 0: return out
        d, j = 0, i
        while j < len(t):
            ch = t[j]
            if ch == '"':
                j += 1
                while j < len(t) and t[j] != '"':
                    if t[j] == "\\": j += 1
                    j += 1
            elif ch == "(": d += 1
            elif ch == ")":
                d -= 1
                if d == 0: break
            j += 1
        out.append(t[i:j + 1]); i = j + 1


def _prop(b, name):
    m = re.search(r'\(property "%s" "((?:[^"\\]|\\.)*)"' % re.escape(name), b)
    return m.group(1) if m else None


def sch_parts(p):
    """{ref: (value, footprint name, LCSC, in_bom)} of the placed symbols of a schematic (lib_symbols skipped)."""
    t = _read(p)
    ls = t.find("(lib_symbols")
    body = t
    if ls >= 0:
        lb = blocks(t[ls:], "(lib_symbols")
        if lb: body = t[:ls] + t[ls + len(lb[0]):]
    parts = {}
    for b in blocks(body, "(symbol (lib_id") + blocks(body, "(symbol\n\t\t(lib_id"):
        ref = _prop(b, "Reference")
        if not ref or ref.startswith("#"): continue
        parts[ref] = (_prop(b, "Value"), (_prop(b, "Footprint") or "").split(":")[-1], _prop(b, "LCSC") or "",
                      not re.search(r"\(in_bom no\)", b))
    return parts


# ---------------------------------------------------------------- schematic
_N1 = re.compile(r'(\(title_block \(title "[^"]*"\) \(date ")(\d{4}-\d{2}-\d{2})("\))')
_N2 = re.compile(r'(\(text "page \d+ of \d+   MeshSat field kit V2, CERN-OHL-S-2\.0   PROTOTYPE, nothing built   )(\d{4}-\d{2}-\d{2})(")')
_L1 = re.compile(r'(\(comment 1 "Phase )([A-Za-z0-9]+)')
_L2 = re.compile(r'(\(text "PCB-[A-Z0-9]+ [^"]*?   )([A-Za-z0-9]+)(")')


def norm_sch(t):
    """(normalised text, {noise id: count}, phase labels found)"""
    counts = {}
    t, counts["N1_title_date"] = _N1.subn(r"\1NOISE\3", t)
    t, counts["N2_page_frame_date"] = _N2.subn(r"\1NOISE\3", t)
    labels = _L1.findall(t) + _L2.findall(t)
    t, counts["L1_comment1_phase"] = _L1.subn(r"\1NOISE", t)
    t, counts["L2_frame_phase"] = _L2.subn(r"\1NOISE\3", t)
    return t, counts, sorted(set(x[1] for x in labels))


def _libsyms(t):
    i = t.find("(lib_symbols")
    if i < 0: return {}
    lb = blocks(t[i:], "(lib_symbols")
    if not lb: return {}
    out = {}
    for b in blocks(lb[0][len("(lib_symbols"):], '(symbol "'):
        name = re.match(r'\(symbol "([^"]+)"', b).group(1)
        if ":" in name: out[name] = hashlib.sha256(b.encode()).hexdigest()[:16]
    return out


def _changed_lines(a, b):
    d = [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0)
         if l[:1] in "+-" and l[:3] not in ("+++", "---")]
    return len(d), [l[:240] for l in d[:60]]


def cmp_sch(a_path, b_path):
    ta, tb = _read(a_path), _read(b_path)
    na, ca, la = norm_sch(ta); nb, cb, lb = norm_sch(tb)
    r = {"kind": "schematic", "phase_labels": [la, lb], "noise_removed": [ca, cb]}
    if ta == tb: r["result"] = "PARITY"; return r
    if na == nb:
        r["result"] = "PARITY_AFTER_NOISE"
        if la != lb: r["labels_differ"] = True
        return r
    r["result"] = "DIFFERENT"
    pa, pb = sch_parts(a_path), sch_parts(b_path)
    r["parts_only_committed"] = sorted(set(pa) - set(pb)); r["parts_only_other"] = sorted(set(pb) - set(pa))
    r["parts_changed"] = [[k, pa[k][:3], pb[k][:3]] for k in sorted(set(pa) & set(pb)) if pa[k] != pb[k]][:200]
    sa, sb = _libsyms(na), _libsyms(nb)
    r["lib_symbols_only_committed"] = sorted(set(sa) - set(sb)); r["lib_symbols_only_other"] = sorted(set(sb) - set(sa))
    r["lib_symbols_changed"] = sorted(k for k in set(sa) & set(sb) if sa[k] != sb[k])
    r["line_counts"] = [na.count("\n"), nb.count("\n")]
    r["changed_lines"], r["changed_lines_sample"] = _changed_lines(na, nb)
    parts = r["parts_only_committed"] or r["parts_only_other"] or r["parts_changed"]
    libs = r["lib_symbols_changed"] or r["lib_symbols_only_committed"] or r["lib_symbols_only_other"]
    r["bucket_hint"] = "PARTS" if parts else ("LIBRARY" if libs else "DRAWING_ONLY")
    return r


# ---------------------------------------------------------------- netlist
_N3 = re.compile(r'(\(design\s*\n\s*)\(source "[^"]*"\)\s*\n\s*\(date "[^"]*"\)\s*\n\s*\(tool "[^"]*"\)')
_HDR = re.compile(r'\(design\s*\n\s*\(source "([^"]*)"\)\s*\n\s*\(date "([^"]*)"\)\s*\n\s*\(tool "([^"]*)"\)')
_N4 = re.compile(r'(\(title_block\s*\n(?:\s*\((?:title|company|rev) "[^"]*"\)\s*\n)*\s*\(date ")(\d{4}-\d{2}-\d{2})("\))')
_NL1 = re.compile(r'(\(comment \(number "1"\) \(value "Phase )([A-Za-z0-9]+)')


def norm_net(t):
    counts = {}
    hdr = _HDR.search(t)
    t, counts["N3_design_source_date_tool"] = _N3.subn(r"\1(source NOISE) (date NOISE) (tool NOISE)", t, count=1)
    t, counts["N4_title_date"] = _N4.subn(r"\1NOISE\3", t)
    lab = sorted(set(x[1] for x in _NL1.findall(t)))
    t, counts["L1_comment1_phase"] = _NL1.subn(r"\1NOISE", t)
    return t, counts, lab, (list(hdr.groups()) if hdr else None)


def parse_net(t):
    comps, nets = {}, {}
    for b in blocks(t, "(comp (ref"):
        ref = re.search(r'\(ref "([^"]+)"\)', b).group(1)
        v = re.search(r'\(value "((?:[^"\\]|\\.)*)"\)', b); f = re.search(r'\(footprint "([^"]*)"\)', b)
        fields = dict(re.findall(r'\(field \(name "([^"]+)"\) "((?:[^"\\]|\\.)*)"\)', b))
        props = dict(re.findall(r'\(property \(name "([^"]+)"\) \(value "((?:[^"\\]|\\.)*)"\)\)', b))
        lib = re.search(r'\(libsource \(lib "([^"]*)"\) \(part "([^"]*)"\)', b)
        ts = re.search(r'\(tstamps "([^"]*)"\)\)\s*$', b)
        comps[ref] = {"value": v.group(1) if v else None, "footprint": f.group(1) if f else None,
                      "fields": fields, "properties": props, "libsource": list(lib.groups()) if lib else None,
                      "tstamps": ts.group(1) if ts else None}
    i = t.find("(nets")
    if i >= 0:
        for b in blocks(t[i + 5:], "(net (code"):
            name = re.search(r'\(name "((?:[^"\\]|\\.)*)"\)', b).group(1)
            nodes = []
            for nb_ in blocks(b, "(node (ref"):
                ref = re.search(r'\(ref "([^"]+)"\)', nb_).group(1); pin = re.search(r'\(pin "([^"]+)"\)', nb_).group(1)
                pf = re.search(r'\(pinfunction "([^"]*)"\)', nb_); pt = re.search(r'\(pintype "([^"]*)"\)', nb_)
                nodes.append((ref, pin, pf.group(1) if pf else "", pt.group(1) if pt else ""))
            nets[name] = sorted(nodes)
    return comps, nets


def content_hash(t):
    """A content identity of a netlist: its components and nets, with no export path, date or tool in it. Two
    exports of the same design give the same hash; the file's sha does not."""
    c, n = parse_net(t)
    return hashlib.sha256(json.dumps([c, n], sort_keys=True).encode()).hexdigest()[:16]


def cmp_net(a_path, b_path):
    ta, tb = _read(a_path), _read(b_path)
    na, ca, la, ha = norm_net(ta); nb, cb, lb, hb = norm_net(tb)
    r = {"kind": "netlist", "phase_labels": [la, lb], "noise_removed": [ca, cb], "design_header": [ha, hb],
         "content_hash": [content_hash(ta), content_hash(tb)]}
    if ta == tb: r["result"] = "PARITY"; return r
    if na == nb:
        r["result"] = "PARITY_AFTER_NOISE"
        if la != lb: r["labels_differ"] = True
        return r
    ca_, na_ = parse_net(ta); cb_, nb_ = parse_net(tb)
    r["counts"] = {"comps": [len(ca_), len(cb_)], "nets": [len(na_), len(nb_)]}
    r["comps_only_committed"] = sorted(set(ca_) - set(cb_)); r["comps_only_other"] = sorted(set(cb_) - set(ca_))
    both = sorted(set(ca_) & set(cb_))
    r["comps_changed"] = [[k, {f: [ca_[k][f], cb_[k][f]] for f in ca_[k] if f != "tstamps" and ca_[k][f] != cb_[k][f]}]
                          for k in both if any(ca_[k][f] != cb_[k][f] for f in ca_[k] if f != "tstamps")][:200]
    r["comps_uuid_shifted"] = sum(1 for k in both if ca_[k]["tstamps"] != cb_[k]["tstamps"])
    r["nets_only_committed"] = sorted(set(na_) - set(nb_))[:200]; r["nets_only_other"] = sorted(set(nb_) - set(na_))[:200]
    r["nets_changed"] = []
    for k in sorted(set(na_) & set(nb_)):
        if na_[k] != nb_[k]:
            sa, sb = set(map(tuple, na_[k])), set(map(tuple, nb_[k]))
            r["nets_changed"].append([k, sorted(sa - sb)[:20], sorted(sb - sa)[:20]])
    r["nets_changed"] = r["nets_changed"][:200]
    semantic_same = not (r["comps_only_committed"] or r["comps_only_other"] or r["comps_changed"] or r["comps_uuid_shifted"]
                         or r["nets_only_committed"] or r["nets_only_other"] or r["nets_changed"])
    r["changed_lines"], r["changed_lines_sample"] = _changed_lines(na, nb)
    # The text differs and the components and nets do not: an ordering or formatting difference in the export,
    # which is the export's (ENVIRONMENT) and not the design's.
    r["result"] = "DIFFERENT_TEXT_SAME_CONTENT" if semantic_same else "DIFFERENT"
    return r


# ---------------------------------------------------------------- json sidecars
def cmp_json(a_path, b_path, kind, noise):
    a, b = json.load(open(a_path)), json.load(open(b_path))
    r = {"kind": kind}
    if a == b: r["result"] = "PARITY"; return r
    a2 = {k: v for k, v in a.items() if k not in noise}; b2 = {k: v for k, v in b.items() if k not in noise}
    r["keys_changed"] = sorted(k for k in set(a2) | set(b2) if a2.get(k) != b2.get(k))
    r["result"] = "PARITY_AFTER_NOISE" if not r["keys_changed"] else "DIFFERENT"
    return r


def cmp_prov(a_path, b_path, sch_a, sch_b, sch_result):
    """Provenance sidecars, judged with the schematics they name."""
    r = cmp_json(a_path, b_path, "provenance", ("taken",))
    if r["result"] != "DIFFERENT": return r
    a, b = json.load(open(a_path)), json.load(open(b_path))

    def self_ok(rec, sch):
        want = rec.get("schematic_sha256") or ""
        return bool(want) and hashlib.sha256(open(sch, "rb").read()).hexdigest()[:len(want)] == want
    selfa, selfb = self_ok(a, sch_a), self_ok(b, sch_b)
    r["sidecar_self_consistent"] = [selfa, selfb]
    if r["keys_changed"] == ["schematic_sha256"] and selfa and selfb and sch_result in ("PARITY", "PARITY_AFTER_NOISE"):
        r["result"] = "PARITY_AFTER_NOISE"
        r["note"] = ("only schematic_sha256 moved; each sidecar matches its own schematic, and the two schematics are "
                     "equal after N1 and N2, so the dates are the whole difference")
    return r


# ---------------------------------------------------------------- bom and erc
def cmp_bom(a_path, b_path):
    ra = sorted(tuple(x) for x in csv.reader(io.StringIO(_read(a_path))))
    rb = sorted(tuple(x) for x in csv.reader(io.StringIO(_read(b_path))))
    r = {"kind": "bom", "rows": [len(ra), len(rb)]}
    if _read(a_path) == _read(b_path): r["result"] = "PARITY"; return r
    if ra == rb: r["result"] = "PARITY_AFTER_NOISE"; r["note"] = "same rows, different order"; return r
    r["rows_only_committed"] = [list(x) for x in sorted(set(ra) - set(rb))][:100]
    r["rows_only_other"] = [list(x) for x in sorted(set(rb) - set(ra))][:100]
    r["result"] = "DIFFERENT"
    return r


def _erc_items(p):
    d = json.load(open(p)); out = []
    for sh in d.get("sheets", []):
        for v in sh.get("violations", []):
            items = sorted(i.get("description", "") for i in v.get("items", []))
            out.append((v.get("severity"), v.get("type"), v.get("description"), tuple(items)))
    return sorted(out)


def cmp_erc(a_path, b_path):
    a, b = _erc_items(a_path), _erc_items(b_path)
    r = {"kind": "erc", "violations": [len(a), len(b)],
         "by_type": [dict(Counter("%s:%s" % (x[0], x[1]) for x in a)), dict(Counter("%s:%s" % (x[0], x[1]) for x in b))]}
    if a == b: r["result"] = "PARITY_AFTER_NOISE"; return r
    ca, cb = Counter(a), Counter(b)
    r["only_committed"] = [list(x[:3]) + [list(x[3])[:4]] for x in (ca - cb).elements()][:50]
    r["only_other"] = [list(x[:3]) + [list(x[3])[:4]] for x in (cb - ca).elements()][:50]
    r["result"] = "DIFFERENT"
    return r


# ---------------------------------------------------------------- board against netlist
def board_vs_net(pcb_path, net_path):
    """The committed board against the committed netlist, as a PARITY reading: every difference counts.

    The per-reference reading is netlist_parts' (rule SCH-002's companion), so the parity run and the gate read the
    same values and lands. The RESULT is stricter than that gate's, on purpose, and it is the draft's of 25
    September (W7's, sha16 8099a3df2ba7b5c2): a reference on one side only (netlist_board's question) and an order
    code that differs (CMP-002's) also make the row DIFFERENT, because a parity reading says whether two artefacts
    are the same, not which rule a difference breaks. The committed copy of 26 September first counted values and
    lands alone, and board E's D9 and D10, in the netlist and not on the E17 board (decision 31's resolution,
    present in the generator and absent from the board), read PARITY; the draft had read DIFFERENT. A board-only
    reference with a bench, mounting, test-point or jumper prefix is not a difference, by netlist_board's own
    declared list (netlist_board.BENCH), which is the one exception list both read."""
    import netlist_board
    r = netlist_parts.compare(netlist_parts.read_components(net_path), netlist_parts.read_footprints(pcb_path))
    only_board = [x for x in r["only_board"] if not x.startswith(netlist_board.BENCH)]
    out = {"kind": "board_vs_netlist_values", "shared_refs": r["shared_refs"], "value": r["value"],
           "footprint": r["footprint"], "lcsc_on_board_differs": r["lcsc"],
           "only_netlist": r["only_netlist"], "only_board": only_board,
           "only_board_declared_bench": [x for x in r["only_board"] if x.startswith(netlist_board.BENCH)]}
    bad = r["value"] or r["footprint"] or r["lcsc"] or r["only_netlist"] or only_board
    out["result"] = "DIFFERENT" if bad else "PARITY"
    return out


KINDS = {"schematic": cmp_sch, "netlist": cmp_net, "bom": cmp_bom, "erc": cmp_erc,
         "intent": lambda a, b: cmp_json(a, b, "intent", ("written",)),
         "provenance": lambda a, b: cmp_json(a, b, "provenance", ("taken",)),
         "board_vs_net": board_vs_net}


def boards_of(repo):
    """{letter: (project directory name, stem)} from the clone's own routeflow profiles."""
    out = {}
    for pf in sorted(glob.glob(os.path.join(repo, "v2", "ecad", "tools", "routeflow", "*.json"))):
        try: p = json.load(open(pf, encoding="utf-8"))
        except ValueError: continue
        letter, stem = os.path.basename(pf)[:-5], p.get("board")
        proj = os.path.basename(str(p.get("project") or "").rstrip("/"))
        if stem and proj and os.path.exists(os.path.join(repo, "v2", "ecad", "tools", "gen_sch_%s.py" % letter)):
            out[letter] = (proj, stem)
    return out


def _committed(repo, rel, dest):
    """The committed bytes of a tracked file, from the clone's HEAD, whatever its working tree now holds."""
    p = subprocess.run(["git", "-C", repo, "show", "HEAD:" + rel], capture_output=True)
    with open(dest, "wb") as fh: fh.write(p.stdout)
    return dest


def _ok(p):
    return os.path.exists(p) and os.path.getsize(p) > 0


def box(repo, out):
    res = {}
    for L, (d, n) in sorted(boards_of(repo).items()):
        o = os.path.join(out, L); os.makedirs(os.path.join(o, "committed"), exist_ok=True)
        base = "v2/ecad/%s" % d
        c = {"schematic": _committed(repo, base + "/%s.kicad_sch" % n, os.path.join(o, "committed", n + ".kicad_sch")),
             "netlist": _committed(repo, base + "/out/%s.net" % n, os.path.join(o, "committed", n + ".net")),
             "intent": _committed(repo, base + "/out/%s-intent.json" % n, os.path.join(o, "committed", n + "-intent.json")),
             "provenance": _committed(repo, base + "/out/%s.net.prov.json" % n, os.path.join(o, "committed", n + ".net.prov.json")),
             "board": _committed(repo, base + "/%s.kicad_pcb" % n, os.path.join(o, "committed", n + ".kicad_pcb"))}
        g = lambda sub, f: os.path.join(o, sub, f)
        rows = {
            # 1. the committed netlist against what KiCad exports from the committed schematic today
            "net_committed_vs_export_of_committed_sch": ("netlist", c["netlist"], g("ref", n + ".net")),
            # 2. the generator's output against the committed artefacts
            "sch_committed_vs_regen": ("schematic", c["schematic"], g("regen", n + ".kicad_sch")),
            "net_committed_vs_regen": ("netlist", c["netlist"], g("regen", n + ".net")),
            "intent_committed_vs_regen": ("intent", c["intent"], g("regen", n + "-intent.json")),
            "prov_committed_vs_regen": ("provenance", c["provenance"], g("regen", n + ".net.prov.json")),
            # 3. exports of the committed schematic against exports of the regenerated one
            "bom_export_committed_vs_regen": ("bom", g("ref", n + "-bom.csv"), g("regen", n + "-bom.csv")),
            "erc_export_committed_vs_regen": ("erc", g("ref", n + "-erc.json"), g("regen", n + "-erc.json")),
            # 4. the committed board against the committed netlist: values and footprints (SCH-002's companion)
            "board_vs_committed_net_values": ("board_vs_net", c["board"], c["netlist"]),
        }
        res[L] = {}
        for key, (kind, a, b) in rows.items():
            if not (_ok(a) and _ok(b)):
                res[L][key] = {"kind": kind, "result": "MISSING_INPUT", "missing": [p for p in (a, b) if not _ok(p)]}
                continue
            try: res[L][key] = KINDS[kind](a, b)
            except Exception as e: res[L][key] = {"kind": kind, "result": "COMPARATOR_ERROR", "error": repr(e)[:300]}
        pa, pb = c["provenance"], g("regen", n + ".net.prov.json")
        if _ok(pa) and _ok(pb) and _ok(g("regen", n + ".kicad_sch")):
            res[L]["prov_committed_vs_regen"] = cmp_prov(pa, pb, c["schematic"], g("regen", n + ".kicad_sch"),
                                                         res[L]["sch_committed_vs_regen"].get("result"))
        for tag in ("v-committed", "v-regen"):
            vp = g(tag, "netlist_board.verdict.json")
            if _ok(vp):
                v = json.load(open(vp))
                res[L]["sch002_" + tag] = {"kind": "verdict", "result": v.get("verdict"), "counts": v.get("counts"),
                                           "inputs": v.get("inputs")}
    return res


def main(argv):
    if len(argv) == 4 and argv[0] == "pair" and argv[1] in KINDS:
        r = KINDS[argv[1]](argv[2], argv[3]); print(json.dumps(r, indent=1))
        return 0 if r["result"].startswith("PARITY") else 1
    if len(argv) == 3 and argv[0] == "box":
        res = box(argv[1], argv[2])
        with open(os.path.join(argv[2], "parity.json"), "w") as fh: json.dump(res, fh, indent=1)
        bad = 0
        for L, rows in sorted(res.items()):
            for key, r in rows.items():
                print("%-2s %-44s %s" % (L, key, r["result"]))
                # A netlist_board verdict found beside the run (the sch002_* rows) is REPORTED, not compared: it is
                # a gate's reading, PASS or FAIL, and never PARITY, so counting it made every clean run exit 1.
                if r.get("kind") == "verdict": continue
                bad += not str(r["result"]).startswith("PARITY")
        return 1 if bad or not res else 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
