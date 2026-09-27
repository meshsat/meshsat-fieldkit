#!/usr/bin/env python3
"""The population rule REL-001 is asked about, as an explicit inventory (MESHSAT-1357, 28 September 2026).

WHY IT EXISTS. `reliability.py` took the parts to inspect from a regular expression over each component's VALUE
PROSE (twelve words), so a connector whose value carried none of the words left the completeness denominator in
silence: an "RJ45 MagJack" beside one declared connector read PASS of one covered part (the independent review of
handover H3, finding H3-01). On the six netlists of the set 6 candidate 61 parts with a connector, holder, switch
or wire reference were in neither the word set nor any class. The population is now an INVENTORY: every
component of the artefact is read, and whether it is a candidate is decided from what it IS DRAWN AS, its
reference class and its land, never from what its description says.

WHAT IS A CANDIDATE. The rules are data (`pcb_reliability.yaml`, section `inventory`), so they are in one place,
are bound to every reading by the file's sha, and are changed by changing the file:

  1. THE REFERENCE CLASS, the letters a reference begins with (`J_RF1` is J, `SW_SOS` is SW, `U30A` is U). Every
     class these artefacts use is declared `mechanical` (a part of it is always a candidate) or `electrical` (its
     land decides). A class nobody declared is REFUSED and its parts are candidates: a new prefix is classed
     deliberately or it stops the reading.
  2. THE LAND, for a part of an electrical class. A land declared mechanical (a connector library, a header, a
     holder, a socket) makes the part a candidate whatever its reference: a module receptacle drawn as U, programming
     pads drawn as U. A land declared soldered (a package library, a named module land) does not. A land that is
     declared NEITHER, and a part with no land at all, is a candidate: where the form cannot be read the part is
     asked for, because a completeness gate must fail in that direction.
  3. THE WORDS, as a second net only. A part that rules 1 and 2 leave out and whose IDENTITY (the value before the
     description, `reliability.identity`) names a socket, a holder or a jack is a candidate too. The words never
     remove a part and are never the denominator.

WHAT IT READS. A KiCad netlist (`read_netlist`) or, for a board with no schematic (E5), its board file
(`read_board`), both as S-expressions with the project's own reader (`netlist_parts.top_level`); no KiCad and no
pcbnew. Each part is its reference, value, land and the number of its pins on nets (pads, for a board file).

WHAT IT DOES NOT DO. It decides nothing about a class's figure, load or measure: that is `reliability.py`. It sees
no mass: a heavy SOLDERED part (a module, a large inductor) is not a candidate here, and the joints under such
parts are outside what this inventory can find from a netlist. Nothing is tested; no board has been built.
"""
import os, re, fnmatch, contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, HERE)
import netlist_parts as _np

KINDS = ("mechanical", "electrical")
_LETTERS = re.compile(r"[A-Za-z]+")


class Unreadable(Exception):
    """The artefact could not be read as what it has to be. The message is the reason a reading gives."""


def ref_class(ref):
    """The letters a reference begins with, up to the first character that is not a letter: `J_RF1` is J,
    `SW_SOS` is SW, `CAM_H1` is CAM, `U30A` is U, `TP6` is TP. Compared EXACTLY with the declared classes.

    (`rules_lib.ref_prefix` answers another question: it keeps the underscore and the letters after it, so
    `J_RF1` is `J_RF` there, which names a signal and not a class of part.)"""
    m = _LETTERS.match(ref or "")
    return m.group(0) if m else ""


def _balanced(text, want_root):
    """Refuse a file that is not one S-expression whose head is `want_root`."""
    depth, head, first, closed = 0, None, True, False
    for m in _np._TOK.finditer(text):
        t = m.group(0)
        if closed: raise Unreadable("text follows the end of the (%s ...) expression" % want_root)
        if t == "(":
            depth += 1
        elif t == ")":
            depth -= 1
            if depth < 0: raise Unreadable("a bracket closes that was never opened")
            if depth == 0: closed = True
        elif first:
            raise Unreadable("the file does not begin with an expression")
        elif head is None:
            head = t
        first = False
    if head != want_root: raise Unreadable("the file is not a (%s ...) expression (it begins %r)" % (want_root, head))
    if depth != 0: raise Unreadable("%d bracket(s) never close: the file is cut short" % depth)


def _text(path):
    try:
        with open(path, "rb") as f: raw = f.read()
    except OSError as e:
        raise Unreadable("it cannot be opened (%s)" % type(e).__name__)
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Unreadable("it is not UTF-8 text")


def read_netlist(path):
    """({ref: {"value", "footprint", "pins"}}, raw bytes) of a KiCad netlist. Raises `Unreadable`.

    A netlist with a well-formed and EMPTY components section returns {}: the caller decides what an empty
    board means (for REL-001 it is a missing input, never a pass of nothing)."""
    raw, txt = _text(path)
    _balanced(txt, "export")
    sections = _np.top_level(txt, {"components"})
    if not sections: raise Unreadable("it has no (components ...) section")
    parts = {}
    for comps in sections:
        for c in comps[1:]:
            if not (isinstance(c, list) and c and c[0] == "comp"): continue
            ref = _np._child(c, "ref")
            if not ref or len(ref) < 2: raise Unreadable("a component carries no reference")
            r = _np._str(ref[1])
            if r in parts: raise Unreadable("reference %s is there twice" % r)
            val, fp = _np._child(c, "value"), _np._child(c, "footprint")
            parts[r] = {"value": _np._str(val[1]) if val and len(val) > 1 else "",
                        "footprint": _np._str(fp[1]) if fp and len(fp) > 1 else "", "pins": 0}
    for nets in _np.top_level(txt, {"nets"}):
        for n in nets[1:]:
            if not (isinstance(n, list) and n and n[0] == "net"): continue
            for node in n[1:]:
                if not (isinstance(node, list) and node and node[0] == "node"): continue
                ref = _np._child(node, "ref")
                r = _np._str(ref[1]) if ref and len(ref) > 1 else None
                if r in parts: parts[r]["pins"] += 1
    return parts, raw


def read_board(path):
    """The same record from a board file's top-level footprints, for a board whose board file is its design.
    `pins` is the number of pads the footprint draws. The land is the bare name a board file carries."""
    raw, txt = _text(path)
    _balanced(txt, "kicad_pcb")
    parts = {}
    for fp in _np.top_level(txt, {"footprint", "module"}):
        props, pads = {}, 0
        for c in fp[1:]:
            if not (isinstance(c, list) and c): continue
            if c[0] == "property" and len(c) >= 3:
                props[_np._str(c[1])] = _np._str(c[2]) if not isinstance(c[2], list) else ""
            elif c[0] == "fp_text" and len(c) >= 3 and c[1] in ("reference", "value"):
                props.setdefault(c[1].capitalize(), _np._str(c[2]))
            elif c[0] == "pad":
                pads += 1
        r = props.get("Reference")
        if not r: raise Unreadable("a footprint carries no reference")
        if r in parts: raise Unreadable("reference %s is there twice" % r)
        parts[r] = {"value": props.get("Value") or "",
                    "footprint": _np._str(fp[1]) if len(fp) > 1 and not isinstance(fp[1], list) else "", "pins": pads}
    return parts, raw


def split_land(fp):
    """(library, name) of a land: `Connector_JST:JST_VH_B2P` is (Connector_JST, JST_VH_B2P); a bare name has no library."""
    fp = fp or ""
    return tuple(fp.split(":", 1)) if ":" in fp else ("", fp)


def land_matches(fp, patterns):
    """Does a land match one of the patterns? A pattern is compared with the whole land and with its bare name, so
    `Connector_JST:JST_VH_*` and `JST_VH_*` both name the same lands and a board file's bare name is matched too."""
    _lib, name = split_land(fp)
    return any(fnmatch.fnmatchcase(fp or "", p) or fnmatch.fnmatchcase(name, p) for p in (patterns or []))


def check_rules(inv):
    """The reasons the inventory rules of a list cannot be used, as sentences; [] when they can."""
    bad = []
    if not isinstance(inv, dict): return ["the list carries no `inventory` section, so no part can be asked for"]
    rc = inv.get("reference_classes")
    if not isinstance(rc, dict) or not rc:
        bad.append("`inventory.reference_classes` declares no reference class")
    else:
        for k, v in sorted(rc.items()):
            if not isinstance(v, dict) or v.get("kind") not in KINDS:
                bad.append("reference class %s is declared with no kind (%s)" % (k, " or ".join(KINDS)))
            elif not str(v.get("what") or "").strip():
                bad.append("reference class %s does not say what it is" % k)
    fp = inv.get("footprint")
    if not isinstance(fp, dict):
        bad.append("`inventory.footprint` is missing")
    else:
        for k in ("mechanical_libraries", "mechanical_names", "soldered_libraries", "soldered_names"):
            if not isinstance(fp.get(k), list): bad.append("`inventory.footprint.%s` is not a list" % k)
    return bad


def land_kind(fp, inv):
    """(kind, by): `mechanical`, `soldered`, `undeclared` or `absent`, and the pattern that decided.
    Mechanical is asked FIRST, so a land both lists could match is a candidate."""
    if not (fp or "").strip(): return "absent", ""
    lib, name = split_land(fp)
    r = inv["footprint"]
    for p in r["mechanical_libraries"]:
        if lib and fnmatch.fnmatchcase(lib, p): return "mechanical", "library %s" % p
    for p in r["mechanical_names"]:
        if fnmatch.fnmatchcase(name, p): return "mechanical", "name %s" % p
    for p in r["soldered_libraries"]:
        if lib and fnmatch.fnmatchcase(lib, p): return "soldered", "library %s" % p
    for p in r["soldered_names"]:
        if fnmatch.fnmatchcase(name, p): return "soldered", "name %s" % p
    return "undeclared", ""


def candidates(parts, inv, words=None):
    """{"candidates": {ref: why}, "undeclared_class": [ref], "by_words": [ref], "prose_only": [ref],
        "how": {reference_class|land|land_undeclared|no_land|undeclared_class|words: count}}.

    `words` is the second net: (pattern, prefixes never asked by words, identity function), or None."""
    rc = inv["reference_classes"]
    out, undeclared, by_words, prose = {}, [], [], []
    how = dict.fromkeys(("reference_class", "land", "land_undeclared", "no_land", "undeclared_class", "words"), 0)
    for ref in sorted(parts):
        p = parts[ref]
        k = ref_class(ref)
        decl = rc.get(k)
        if decl is None:
            undeclared.append(ref); how["undeclared_class"] += 1
            out[ref] = "its reference class %s is not declared in the inventory" % (k or "(none)")
            continue
        if decl["kind"] == "mechanical":
            out[ref] = "reference class %s (%s)" % (k, decl["what"]); how["reference_class"] += 1
            continue
        kind, by = land_kind(p["footprint"], inv)
        if kind == "mechanical":
            out[ref] = "its land %s is a mechanical or mating land (%s)" % (p["footprint"], by); how["land"] += 1
        elif kind == "undeclared":
            out[ref] = ("its land %s is declared neither mechanical nor soldered, so it is asked for"
                        % p["footprint"]); how["land_undeclared"] += 1
        elif kind == "absent":
            out[ref] = "it carries no land, so nothing shows it is a soldered package"; how["no_land"] += 1
        elif words:
            pat, never, identity = words
            v = p["value"] or ""
            if not pat.search(v): continue
            m = pat.search(identity(v))
            if k in never:
                continue                                  # a diode's value says what it stands off: never a wear word
            if m:
                out[ref] = "its value names a %s (the word net)" % m.group(0); how["words"] += 1
                by_words.append(ref)
            else:
                prose.append(ref)
    return {"candidates": out, "undeclared_class": undeclared, "by_words": by_words, "prose_only": prose, "how": how}


@contextlib.contextmanager
def declared(manifest=None, profiles=None):
    """Resolve declared phases through `phase_artefacts` with ANOTHER manifest or another routeflow profile
    directory, for the time of the block: an isolated fixture's. With neither, the tree's own are used and
    nothing is touched. `profiles` is a directory holding `routeflow/*.json`."""
    import phase_artefacts as _pa
    keep = (_pa.MANIFEST, _pa.HERE)
    try:
        if manifest: _pa.MANIFEST = os.path.abspath(manifest)
        if profiles: _pa.HERE = os.path.abspath(profiles)
        yield _pa
    finally:
        _pa.MANIFEST, _pa.HERE = keep


def artefact(letter, ecad=None):
    """(kind, path) of the artefact REL-001 reads for a board of the manifest: ("netlist", the declared phase's
    netlist) or, where the manifest says the board has no schematic, ("board_file", the declared phase's board
    file). (None, None) for a letter the manifest does not know. The path may not exist.

    THE DECLARED PHASE, never the newest file: `phase_artefacts.phase_dir` reads the manifest's stem and the
    routeflow profile's project directory, which is how `rules_status.candidate` finds the design it judges."""
    import phase_artefacts as _pa
    if not _pa.stem(letter): return None, None
    if _pa.no_schematic(letter): return "board_file", _pa.board_file(letter, ecad)
    return "netlist", _pa.netlist(letter, ecad)


def read(kind, path):
    return read_board(path) if kind == "board_file" else read_netlist(path)
