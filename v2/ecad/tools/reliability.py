#!/usr/bin/env python3
"""What carries load and what sees cycling (rule REL-001, MESHSAT-862, 16 September 2026; the inventory and the
input rules of MESHSAT-1357, 28 September 2026).

The rule asks for a per-board list of the parts and joints that carry mechanical load or see cycling, the
expected cycles or level, and the measure taken. This kit is CARRIED, so the question is not academic: every
connector mated in the field is a wear item and every board-mounted jack is a lever with the case as its
fulcrum. `pcb_reliability.yaml` declares the classes per board and this gate checks them against the board.

WHAT CHANGED ON 28 SEPTEMBER 2026, AND WHY. The independent review of handover H3 (finding H3-01) showed this
gate reading PASS with an unclassified RJ45 jack on the board, and PASS with the board's netlist absent. Three
causes, each repaired here:

  1. THE POPULATION WAS WORDS IN PROSE. The parts to inspect were the ones whose value text matched twelve words,
     so a connector described with none of them left the denominator in silence; 61 parts of the set 6 netlists
     did. The population is now an INVENTORY (`wear_inventory.py`): every component is read, and its reference
     class and its land decide whether it is a candidate. Every candidate must be DISPOSED: it falls in exactly
     one declared class, or under one declared exclusion that gives its reason and names the land it speaks of.
     A candidate that is neither is a refusal. The twelve words remain as a second net below the inventory.
  2. A MISSING INPUT READ AS A PASS. A board with no netlist read PASS of zero parts. A required input that is
     not there, cannot be read or is empty is INCONCLUSIVE with its reason (exit 3), never PASS.
  3. THE NETLIST WAS THE NEWEST FILE BY MTIME, and the reading named none. It is the netlist of the board's
     DECLARED phase (`phase_artefacts`, the resolution `rules_status` uses), or for a board with no schematic
     (E5) its declared phase's board file, and the reading records it by path and sha256 with the list's own sha.
  4. THE LIST WAS BOUND TO NOTHING. A class names a PART and cites that part's figure, and this gate cannot read
     the part off the value text (reading the value text is the defect above), so nothing showed which netlist a
     board's classes had been written against. Each board's declaration now carries `written_against`, the
     sha256 of the artefact its author read (printed by `--pins`); an artefact of another sha is not the one the
     list speaks of, and the reading is INCONCLUSIVE with the reason, whether the components and nets are the
     same (a re-export: read the values against the list and re-pin) or differ (the design changed: re-declare).

WHAT IT CHECKS:
  * completeness: every candidate is disposed, exactly once, and a class or an exclusion speaks of the land the
    board really carries (`footprints`), so a class written for one connector family cannot cover another;
  * the artefact read is the one the board's declaration was written against (`written_against.sha256_16`);
  * a class names its load and its measure;
  * a class's cycle figure cites the maker's document held in this tree, by its sha, with the page and the words;
    a class with no figure says which of three things is true: the maker's document states none
    (`none_published`, with the documents that were read), nothing is mated (`not_mated`: a solder land, a screw
    joint), or the figure is OWED because the part or its document is not identified, which carries an open
    item and keeps the board's reading INCONCLUSIVE until it is closed; a measure that is not designed yet is
    owed the same way (`measure_owed`);
  * a declared count matches the board.

WHAT IT CANNOT DO is test anything: REL-001 is verified at the PROTOTYPE and no board has been built. This is the
desk half: a reading of a netlist and a list. It replaces no physical verification, the figures are the makers'
ratings of the parts and not a claim about the kit, and it sees no mass, so the joints under heavy soldered
parts are outside it.

Usage: reliability.py [--rel pcb_reliability.yaml] [--ecad <dir>] [--board <letter>] [--vendor <dir>]
                      [--manifest <readiness_manifest.json>] [--profiles <dir holding routeflow/>]
                      [--out-dir <dir>] [--json]
       exit 0 PASS, 1 FAIL, 3 INCONCLUSIVE
       reliability.py --pins [--ecad <dir>] [--manifest ...] [--profiles ...]
       prints the `written_against` line of every board of the manifest from the declared phase's artefact in
       this tree, for a person to read against the list and paste; it edits nothing (a sha says nothing about
       the values, and a substitution is a mismatch until proven)
"""
import os, re, sys, json, fnmatch, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import wear_inventory as _wi

ECAD = os.path.dirname(HERE)
VENDOR = os.path.normpath(os.path.join(ECAD, "..", "vendor"))
REL = os.path.join(HERE, "pcb_reliability.yaml")
# THE SECOND NET, below the inventory (`wear_inventory.candidates`, rule 3): the words a part's IDENTITY carries
# (`identity`, below). Until 28 September 2026 this expression WAS the population, which is the defect of finding
# H3-01; it now only ADDS a part the reference class and the land leave out, and never removes one.
WEAR_TWELVE = re.compile(r"socket|receptacle|holder|SMA|XT60|JST|IDC|header|standoff|U\.FL|M\.2|blade", re.I)
# THE TWELVE WORDS above are the list as it stood when it was the population, kept under their own name for the record
# and for the tests that show the defect. `jack`, `RJ45` and `plug` joined the net on 28 September 2026 (the fresh
# check of stream d6rel, m5): an "RJ45 MagJack" drawn as `U99` on a soldered package land passed both the reference
# class and the land, and the net that is there for exactly that case did not know the word. A soldered part whose
# identity names the jack it feeds (board B's magnetics and PoE controller) becomes a candidate by it and is
# excluded by name with its reason, which is the direction a completeness gate errs in.
WEAR = re.compile(WEAR_TWELVE.pattern + r"|jack|RJ45|plug", re.I)
# ...AND THE WORD HAS TO BE ABOUT A MECHANICAL PART (16 September 2026). A transient suppressor's value says
# what it STANDS OFF, which is a voltage: "SMCJ40A (40 V standoff on a line specified to 36 V)" matched
# `standoff` and six correct diodes on three boards were reported as load-bearing parts in no declared class.
# A capacitor, a resistor, an inductor, a diode, a transistor or a ferrite is never a socket, a holder or a
# standoff whatever its prose says, and the prefix is the letters matched exactly, never the first of them,
# which is the lesson derate.py learnt twice. A connector (J), a module receptacle (U), a fuse holder (F) and
# a battery holder (BT) stay in, because those are the parts this rule exists for.
NOT_WEAR_PREFIX = ("C", "R", "L", "D", "Q", "FB", "TP", "FID", "LOGO")
NO_FIGURE = ("none_published", "not_mated", "owed")
NOTE = ("every candidate part of the inventory falls in one declared class, with its cycle figure from the maker's "
        "document or the reason it has none, its load and the measure taken, or under one declared exclusion with "
        "its reason. A desk reading of a netlist and a list: it tests nothing and replaces no physical "
        "verification; REL-001 is verified at the prototype and no board has been built")


def _sha(path):
    try:
        with open(path, "rb") as f: return hashlib.sha256(f.read()).hexdigest()
    except OSError:
        return None


def _cited(doc, vdir, have_vendor, who, fails, unjudged):
    """Check one cited document {document, sha256_16}: in the tree, and the bytes that were read."""
    if not isinstance(doc, dict) or not str(doc.get("document") or "").strip():
        fails.append("%s cites no document" % who); return
    name = str(doc["document"]).strip()
    if not name.startswith("v2/vendor/"):
        fails.append("%s cites %s, which is not a document under v2/vendor/" % (who, name)); return
    said = str(doc.get("sha256_16") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{16}", said):
        fails.append("%s cites %s without the sha256 of the bytes that were read" % (who, name)); return
    if not have_vendor:
        unjudged.append(name); return
    now = _sha(os.path.join(vdir, name[len("v2/vendor/"):]))
    if now is None:
        fails.append("%s cites %s, which is not in this tree" % (who, name))
    elif now[:16] != said:
        fails.append("%s cites %s at sha256 %s and the tree holds %s: the document is not the one that was read"
                     % (who, name, said, now[:16]))


def _figure(L, c, open_items, vdir, have_vendor, fails, unjudged):
    """What a class says about its cycle figure: `cited`, one of NO_FIGURE, or None when it is refused."""
    who = "%s: class %s" % (L, c.get("name"))
    cyc, src, nof = c.get("cycles"), c.get("source"), c.get("no_figure")
    if cyc is not None:
        if isinstance(cyc, bool) or not isinstance(cyc, int) or cyc <= 0:
            fails.append("%s gives a cycle figure that is not a positive whole number (%r)" % (who, cyc)); return None
        if nof is not None:
            fails.append("%s gives a cycle figure and a reason it has none" % who); return None
        # One document, or one per part number where a class holds several parts of one rating.
        srcs = src if isinstance(src, list) else [src]
        if not srcs or not all(isinstance(x, dict) for x in srcs):
            fails.append("%s gives %d cycles and cites no document for them" % (who, cyc)); return None
        n = len(fails)
        for x in srcs:
            for k in ("page", "words"):
                if not str(x.get(k) or "").strip():
                    fails.append("%s cites its figure without the %s" % (who, k))
            _cited(x, vdir, have_vendor, who, fails, unjudged)
        return "cited" if len(fails) == n else None
    if not isinstance(nof, dict) or nof.get("kind") not in NO_FIGURE:
        fails.append("%s gives no cycle figure and does not say why it has none (%s)" % (who, ", ".join(NO_FIGURE)))
        return None
    kind, n = nof["kind"], len(fails)
    if not str(nof.get("statement") or "").strip():
        fails.append("%s gives no cycle figure and does not say why it has none: its reason is empty" % who)
    if kind == "none_published":
        looked = nof.get("looked_in")
        if not isinstance(looked, list) or not looked:
            fails.append("%s says no figure is published and does not say where it looked" % who)
        else:
            for d in looked: _cited(d, vdir, have_vendor, who, fails, unjudged)
        # It may name the open item that says what is done about a figure no maker publishes; if it names one, it is there.
        if nof.get("open_item") is not None:
            _open_item(who, "a figure its maker does not publish", nof.get("open_item"), open_items, fails)
    elif kind == "owed":
        _open_item(who, "its figure", nof.get("open_item"), open_items, fails)
    return kind if len(fails) == n else None


def _open_item(who, what, key, open_items, fails):
    """An owed thing names an open item of the list, which says what is owed and the next action."""
    it = (open_items or {}).get(key)
    if not isinstance(it, dict):
        fails.append("%s owes %s and names no open item of this list (%r)" % (who, what, key)); return False
    if not (str(it.get("what") or "").strip() and str(it.get("next_action") or "").strip()):
        fails.append("%s owes %s under open item %s, which does not say what is owed and the next action"
                     % (who, what, key)); return False
    return True


class Refused(ValueError):
    """The list is refused by the tool's own check of it. The message is the reasons."""


def _holds(item, letter):
    """Does an open item hold this board by naming it (`holds: all`, or a list of board letters)?"""
    h = item.get("holds") if isinstance(item, dict) else None
    return h == "all" or (isinstance(h, list) and str(letter).lower() in [str(x).lower() for x in h])


def check_open_items(d):
    """The reasons the open items of a list are refused, as sentences; [] when there is none.

    An open item says what is owed and the next action, and it HOLDS something: a class names it (its figure or its
    measure is owed under it, or its maker publishes no figure), or the item names the boards it holds (`holds: all`,
    or `holds: [a, b]`). An item that names no board and that no class names holds no reading, and a list that carries
    one reads as if the item were being accounted for: a list with such an item and one cited class read PASS (the
    fresh check of stream d6rel, 28 September 2026, its P15). It is refused here, before any board is judged."""
    items = d.get("open_items")
    if items is None: return []
    if not isinstance(items, dict): return ["`open_items` is not a mapping"]
    boards = d.get("boards") if isinstance(d.get("boards"), dict) else {}
    named = set()
    for b in boards.values():
        for c in ((b or {}).get("classes") or []):
            if not isinstance(c, dict): continue
            nf = c.get("no_figure") if isinstance(c.get("no_figure"), dict) else {}
            if nf.get("open_item") is not None: named.add(str(nf["open_item"]))
            if c.get("measure_owed") is not None: named.add(str(c["measure_owed"]))
    bad = []
    for key, it in sorted(items.items(), key=lambda kv: str(kv[0])):
        if not isinstance(it, dict) or not (str(it.get("what") or "").strip() and str(it.get("next_action") or "").strip()):
            bad.append("open item %s does not say what is owed and the next action" % key); continue
        h = it.get("holds")
        if h is None:
            if str(key) not in named:
                bad.append("open item %s names no board (`holds`) and no class names it, so it holds no reading" % key)
        elif h == "all":
            pass
        elif isinstance(h, list) and h:
            unknown = [str(x) for x in h if str(x).lower() not in boards]
            if unknown: bad.append("open item %s holds board(s) %s, which the list does not declare" % (key, ", ".join(unknown)))
        else:
            bad.append("open item %s carries a `holds` that is neither `all` nor a list of boards" % key)
    return bad


def _refs(decl):
    r = decl.get("refs")
    return [str(x) for x in r] if isinstance(r, list) else []


def _hits(ref, decls):
    return [d for d in decls if any(fnmatch.fnmatchcase(ref, p) for p in _refs(d))]


def _short(refs, n=12):
    refs = list(refs)
    return ", ".join(refs) if len(refs) <= n else "%s and %d more" % (", ".join(refs[:n]), len(refs) - n)


def judge_board(letter, b, inv, open_items, ecad=None, vendor=None, rel_dir=None):
    """One board's reading. `b` is the board's declaration in the list, or None when the list declares none."""
    import phase_artefacts as _pa
    L = letter.upper()
    vdir = vendor or VENDOR
    have_vendor = os.path.isdir(vdir)
    fails, notes, why_not, unjudged = [], [], [], []
    missing = None
    classes = [c for c in ((b or {}).get("classes") or []) if isinstance(c, dict)]
    excl = [x for x in ((b or {}).get("exclusions") or []) if isinstance(x, dict)]
    out = dict(classes=len(classes), exclusions=len(excl), candidates=0, covered=0, excluded=0, refused=0,
               fails=fails, notes=notes, inconclusive=why_not, netlist=False, artefact=None, artefact_kind=None,
               prose_only=[], by_words=[], inventory=[], excluded_by=[], figures={}, owed=[], how={},
               measures_owed=0, undecided=[], held_by=[], unjudged=0)
    # ---- the declarations themselves, judged whether or not the board can be read
    fig = {}
    for c in classes:
        for k in ("name", "load", "measure"):
            if not str(c.get(k, "") or "").strip():
                fails.append("%s: a class carries no %s" % (L, k))
        if not _refs(c): fails.append("%s: class %s names no reference" % (L, c.get("name")))
        fig[id(c)] = _figure(L, c, open_items, vdir, have_vendor, fails, unjudged)
        if fig[id(c)]:
            out["figures"][fig[id(c)]] = out["figures"].get(fig[id(c)], 0) + 1
        if fig[id(c)] == "owed":
            out["held_by"].append(str(c["no_figure"].get("open_item")))
            out["owed"].append("%s: class %s owes its cycle figure (open item %s: %s)"
                               % (L, c.get("name"), c["no_figure"].get("open_item"),
                                  " ".join(str(open_items[c["no_figure"]["open_item"]].get("what")).split())))
        # A CLASS WHOSE MAKER PUBLISHES NO FIGURE NEVER LETS ITS BOARD READ PASS (28 September 2026; the integrator's
        # decision after the fresh check of stream d6rel, m1, on the H3 review's condition). Until then the class
        # was accepted once it said where it had looked, and a board whose only class was one JST header read PASS
        # with no figure cited at all (the check's P1); board P would have read PASS with none of its four classes
        # cited the day its one owed measure closed. "The maker states none" is a finding about a document, not a
        # figure: the class is UNDECIDED and holds its board INCONCLUSIVE, named, as an owed figure does. `not_mated`
        # is another thing (a solder land, a screw joint: no figure applies) and holds nothing.
        if fig[id(c)] == "none_published":
            nf = c["no_figure"]
            item = nf.get("open_item")
            if item is not None: out["held_by"].append(str(item))
            out["undecided"].append(
                "%s: class %s has no cycle figure: the maker's documents that were read state none (%s), so the class "
                "is undecided and the board is not passed on it%s"
                % (L, c.get("name"), ", ".join(str(x.get("document")) for x in nf.get("looked_in") or [] if isinstance(x, dict)),
                   (" (open item %s: %s)" % (item, " ".join(str(open_items[item].get("next_action")).split()))) if item is not None else ""))
        # A MEASURE THAT IS NOT TAKEN YET IS OWED LIKE A FIGURE: the class says what is there today and names
        # the open item, and the board does not read PASS on a measure nobody has designed.
        if c.get("measure_owed") is not None:
            if _open_item("%s: class %s" % (L, c.get("name")), "its measure", c.get("measure_owed"), open_items, fails):
                out["measures_owed"] += 1
                out["held_by"].append(str(c["measure_owed"]))
                out["owed"].append("%s: class %s owes its measure (open item %s: %s)"
                                   % (L, c.get("name"), c["measure_owed"],
                                      " ".join(str(open_items[c["measure_owed"]].get("what")).split())))
    # AN OPEN ITEM THAT NAMES THE BOARD HOLDS IT (`holds`), whatever its classes say: what the list cannot see on this
    # board (the joints under heavy soldered parts, the footprints only its board file carries) or cannot compare
    # (no expected number of mates is stated) keeps the reading from PASS, named with its next action.
    for key in sorted(open_items or {}, key=str):
        it = open_items[key]
        if _holds(it, letter):
            out["held_by"].append(str(key))
            out["owed"].append("%s: open item %s holds the board: %s (next action: %s)"
                               % (L, key, " ".join(str(it.get("what")).split()), " ".join(str(it.get("next_action")).split())))
    for x in excl:
        who = "%s: the exclusion of %s" % (L, _short(_refs(x)) or "no reference")
        if not _refs(x): fails.append("%s: an exclusion names no reference" % L)
        if not str(x.get("reason") or "").strip(): fails.append("%s gives no reason" % who)
        if not (isinstance(x.get("footprints"), list) and x["footprints"]):
            fails.append("%s does not name the land it speaks of (footprints)" % who)
    # ---- the board
    if b is None:
        why_not.append("board %s is a board of the manifest and the list declares nothing for it" % L)
    kind, path = _wi.artefact(letter, ecad)
    what = {"netlist": "netlist", "board_file": "board file (this board has no schematic: its board file is its design)"}
    parts = None
    if kind is None:
        missing = ("board %s is not a board of the manifest (readiness_manifest.json), so the phase it declares and "
                   "the netlist of that phase cannot be resolved" % L)
    elif not os.path.isfile(path):
        missing = "board %s has no %s of its declared phase in this tree (%s)" % (L, kind.replace("_", " "), _pa.rel(path))
    else:
        try:
            parts, raw = _wi.read(kind, path)
        except _wi.Unreadable as e:
            missing = "board %s's %s %s cannot be read: %s" % (L, kind.replace("_", " "), _pa.rel(path), e)
        else:
            out["artefact"] = _pa.record(path, raw, sha256=hashlib.sha256(raw).hexdigest(), parts=len(parts))
            out["artefact_kind"] = kind
            if not parts:
                missing = ("board %s's %s %s holds no component, so there is nothing to compare the list with"
                           % (L, kind.replace("_", " "), _pa.rel(path)))
                parts = None
    if missing:
        why_not.append(missing)
        notes.append("%s, so the list could not be compared with the board" % missing)
    # ---- THE DECLARATION IS BOUND TO THE ARTEFACT IT WAS WRITTEN AGAINST (28 September 2026). A class names a
    # PART and cites that part's figure, and this gate cannot read the part off the value text (that reading is the
    # defect of H3-01), so the list says which artefact its author read: `written_against.sha256_16`, the sha256 of
    # the declared phase's netlist or board file. An artefact of another sha is not the one the list speaks of. The
    # reading is INCONCLUSIVE and declares it as a missing input (the artefact the list was written against is not
    # here), and says whether the components and nets are the same (a re-export: read the values against the list
    # and re-pin with --pins) or not (the design changed: re-declare the list against it). The comparison below
    # still runs, because a refusal on the artefact that IS here is real and FAIL wins; a PASS cannot come of it.
    out["pin"] = None
    if parts is not None and b is not None:
        pin = b.get("written_against") if isinstance(b.get("written_against"), dict) else {}
        said = str(pin.get("sha256_16") or "").strip().lower()
        c_said = str(pin.get("content16") or "").strip().lower()
        have, c_have = out["artefact"]["sha256_16"], out["artefact"].get("content16")
        same = (c_said == c_have) if (c_said and c_have) else None      # None: nothing to compare the design by
        out["pin"] = {"declared": said or None, "read": have, "bound": bool(said) and said == have, "same_design": same}
        shown = kind.replace("_", " ")
        if not re.fullmatch(r"[0-9a-f]{16}", said):
            missing = ("board %s's declaration does not say which %s it was written against (written_against: "
                       "{sha256_16: ...}, printed by reliability.py --pins), so the list cannot be bound to the %s "
                       "that was read (%s, sha256 %s)" % (L, shown, shown, _pa.rel(path), have))
        elif said != have:
            if same is True:
                tail = ("its components and nets are the same (a re-export of the same design): read the values "
                        "against the list and re-pin it (reliability.py --pins)")
            elif same is False:
                tail = "its components or nets differ, so the design changed: re-declare the list against it and re-pin"
            elif c_have:
                tail = ("the pin carries no content identity, so whether the design is the same cannot be told: read "
                        "the netlist against the list and re-pin (reliability.py --pins)")
            else:
                tail = ("whether the design is the same cannot be told from a board file: read it against the list "
                        "and re-pin (reliability.py --pins)")
            missing = ("board %s's declaration was written against the %s of sha256 %s and the declared phase's %s "
                       "%s reads %s: %s" % (L, shown, said, shown, _pa.rel(path), have, tail))
        if missing:
            why_not.append(missing)
            notes.append("%s; the comparison below is of the artefact that is here" % missing)
    if parts is not None and b is not None:
        out["netlist"] = True
        found = _wi.candidates(parts, inv, (WEAR, NOT_WEAR_PREFIX, identity))
        cand = found["candidates"]
        out["candidates"], out["how"] = len(cand), found["how"]
        out["prose_only"], out["by_words"] = found["prose_only"], found["by_words"]
        if found["prose_only"]:
            notes.append("%s: %d part(s) carry a wear word only in the description of what they do and are "
                         "not asked for: %s" % (L, len(found["prose_only"]), ", ".join(found["prose_only"])))
        seen = {}
        for r in found["undeclared_class"]:
            seen.setdefault(_wi.ref_class(r), []).append(r)
        for k, rs in sorted(seen.items()):
            fails.append("%s: reference class %s (%s) is not declared in the inventory: class it mechanical or "
                         "electrical" % (L, k or "(none)", _short(rs)))
        took = {id(d): [] for d in classes + excl}
        for r in sorted(cand):
            p = parts[r]
            hc, hx = _hits(r, classes), _hits(r, excl)
            row = dict(ref=r, value=p["value"], footprint=p["footprint"], pins=p["pins"], why=cand[r])
            if len(hc) + len(hx) > 1:
                names = [str(c.get("name", "?")) for c in hc] + ["the exclusion of %s" % _short(_refs(x)) for x in hx]
                if len(hc) > 1 and not hx:
                    fails.append("%s: %s falls in %d classes (%s)" % (L, r, len(hc), ", ".join(names)))
                else:
                    fails.append("%s: %s is disposed %d times (%s): a part is in one class or under one exclusion"
                                 % (L, r, len(names), "; ".join(names)))
                row.update(disposition="refused", by="disposed %d times" % len(names))
            elif not hc and not hx:
                fails.append("%s: %s (%s) carries load or sees cycling and is in no declared class and under no "
                             "declared exclusion: %s" % (L, r, (p["value"] or "")[:45], cand[r]))
                row.update(disposition="refused", by="no class and no exclusion")
            else:
                d = (hc or hx)[0]
                lands = d.get("footprints")
                label = ("class %s" % d.get("name")) if hc else ("the exclusion of %s" % _short(_refs(d)))
                if isinstance(lands, list) and lands and not _wi.land_matches(p["footprint"], lands):
                    fails.append("%s: %s is put under %s, which speaks of the lands %s, and the board gives it %s"
                                 % (L, r, label, ", ".join(str(x) for x in lands), p["footprint"] or "no land"))
                    row.update(disposition="refused", by="%s speaks of another land" % label)
                else:
                    took[id(d)].append(r)
                    row.update(disposition="class" if hc else "exclusion",
                               by=d.get("name") if hc else " ".join(str(d.get("reason") or "").split()))
            out["inventory"].append(row)
        for d in classes + excl:
            is_c = d in classes
            label = ("class %s" % d.get("name")) if is_c else ("the exclusion of %s" % _short(_refs(d)))
            got, want = len(took[id(d)]), d.get("count_expected")
            if want is not None and int(want) != got:
                fails.append("%s: %s expects %s part(s) and the netlist has %d" % (L, label, want, got))
            elif got == 0 and not [r for r in cand if _hits(r, [d])]:
                fails.append("%s: %s covers no candidate part of the board: a declaration about nothing" % (L, label))
            if not is_c and got:
                out["excluded_by"].append(dict(refs=_refs(d), parts=took[id(d)],
                                               reason=" ".join(str(d.get("reason") or "").split())))
        out["covered"] = sum(len(took[id(c)]) for c in classes)
        out["excluded"] = sum(len(took[id(x)]) for x in excl)
        out["refused"] = len([r for r in out["inventory"] if r["disposition"] == "refused"])
    no_vendor = None
    if unjudged:
        # THE VENDOR LIBRARY IS A REQUIRED INPUT, AND ITS ABSENCE IS DECLARED AS ONE (28 September 2026, the fresh
        # check's m9e): the reading was INCONCLUSIVE with `missing_input` empty, so a consumer could not tell a
        # reading whose citations nobody checked from one that only owes a figure.
        out["unjudged"] = len(set(unjudged))
        no_vendor = ("%s: the vendor library is not in this tree (%s), so %d cited document(s) could not be "
                     "checked: %s" % (L, vdir, len(set(unjudged)), _short(sorted(set(unjudged)), 4)))
        why_not.append(no_vendor)
    why_not.extend(out["owed"])
    why_not.extend(out["undecided"])
    out["held_by"] = sorted(set(out["held_by"]))
    out["missing_input"] = "; ".join(x for x in (missing, no_vendor) if x) or None
    out["result"] = _v.FAIL if fails else (_v.INCONCLUSIVE if why_not else _v.PASS)
    return out


def judge(rel=None, ecad=None, only=None, vendor=None, manifest=None, profiles=None):
    """{letter: reading} for every board of the manifest and every board the list declares (or `only`)."""
    import yaml
    d = yaml.safe_load(open(rel or REL, encoding="utf-8"))
    if not isinstance(d, dict): raise ValueError("the list is not a mapping")
    inv = d.get("inventory")
    bad = _wi.check_rules(inv) + check_open_items(d)
    if bad: raise Refused("; ".join(bad))
    open_items = d.get("open_items") or {}
    decl = d.get("boards") or {}
    out = {}
    with _wi.declared(manifest, profiles) as _pa:
        for letter in sorted(set(decl) | set(_pa.letters())):
            if only and letter != only: continue
            out[letter] = judge_board(letter, decl.get(letter), inv, open_items, ecad, vendor)
    return out


def identity(value):
    """What the part IS, without the description of what it does in this circuit (27 September 2026).

    A value in these netlists is written `<the part and its properties>: <what it does here>`, and `WEAR` was
    searched in all of it. Board B's `U116`, `U216` and `U316` are SN74LV1T08 AND gates in SOT-23-5 whose
    description reads "slot 1's card-socket supply enable = EMCON AND PCIE_PWR_EN1": the word `socket` says what
    the gate SWITCHES, and three logic gates were refused as load-bearing parts in no declared class. The
    same reading had already put three soldered LQFP-128 PCIe switches (`U101`, `U201`, `U301`, "port 2 card
    socket") in the list, where a class was declared for them that says they are not connectors. A prefix cannot
    decide this one, because a module receptacle is a `U` too.

    THE SEPARATOR is the first colon followed by white space that stands OUTSIDE every bracket. 89 of the 2630
    values of the six netlists carry their first colon inside a bracket ("SMCJ40A (bus clamp: 40 V standoff"),
    which is a remark on the part and not the end of its identity, so a plain split would cut an identity
    short and could drop a connector named in the remark. A value with no such colon, or with a bracket that
    never closes, is ALL identity: when the form cannot be read the part is asked for rather than dropped.

    Since 28 September 2026 it serves the second net only (`wear_inventory.candidates`, rule 3): the inventory
    decides by the reference class and the land, and the words add what those leave out.
    """
    v = value or ""
    depth = 0
    for i, ch in enumerate(v):
        if ch in "([{": depth += 1
        elif ch in ")]}": depth = max(0, depth - 1)
        elif ch == ":" and depth == 0 and v[i + 1:i + 2].isspace(): return v[:i]
    return v


def pins(ecad=None, manifest=None, profiles=None):
    """The `written_against` record of every board of the manifest, read from the declared phase's artefact in this
    tree: [(letter, kind, record or None, path)], the record as `phase_artefacts.record` gives it with `parts`, or
    {"unreadable": why} when the artefact cannot be read. Printed by --pins and never written into the list by this
    tool: a sha says nothing about the VALUES, and re-pinning is a person reading the parts against the list."""
    out = []
    with _wi.declared(manifest, profiles) as _pa:
        for letter in _pa.letters():
            kind, path = _wi.artefact(letter, ecad)
            rec = None
            if path and os.path.isfile(path):
                try:
                    parts, raw = _wi.read(kind, path)
                    rec = _pa.record(path, raw, parts=len(parts))
                except _wi.Unreadable as e:
                    rec = {"unreadable": str(e)}
            out.append((letter, kind, rec, _pa.rel(path) if path else None))
    return out


def _print_pins(ecad, manifest, profiles):
    for letter, kind, rec, path in pins(ecad, manifest, profiles):
        shown = (kind or "artefact").replace("_", " ")
        if rec is None:
            print(" %s:   # no %s of the declared phase in this tree (%s)" % (letter, shown, path)); continue
        if "unreadable" in rec:
            print(" %s:   # the %s %s cannot be read: %s" % (letter, shown, path, rec["unreadable"])); continue
        extra = (', content16: "%s"' % rec["content16"]) if rec.get("content16") else ""
        print(' %s:\n   written_against: {artefact: %s, path: "%s", sha256_16: "%s"%s}   # %d part(s); read the '
              'values against the list before pasting' % (letter, kind, rec["path"], rec["sha256_16"], extra, rec["parts"]))
    return 0


def _inputs(r, rel, only):
    """What the reading judged, by content: the list, and per board the artefact of its declared phase."""
    import phase_artefacts as _pa
    inp = {"list": _pa.record(rel or REL, content=False, sha256=_sha(rel or REL)) or os.path.basename(rel or REL)}
    if only: inp["board"] = only
    for letter, v in sorted(r.items()):
        if not v.get("artefact"): continue
        key = "netlist" if v["artefact_kind"] == "netlist" else "board_file"
        inp[key if only else "%s_%s" % (key, letter)] = v["artefact"]
    return inp


def main(argv):
    rel = _v.opt(argv, "--rel", None)
    ecad = _v.opt(argv, "--ecad", None)
    vendor = _v.opt(argv, "--vendor", None)
    out_dir = _v.opt(argv, "--out-dir", None)
    kw = {"out_dir": out_dir} if out_dir else {}
    only = (_v.opt(argv, "--board", None) or "").lower() or None
    if "--pins" in argv:
        return _print_pins(ecad, _v.opt(argv, "--manifest", None), _v.opt(argv, "--profiles", None))
    try:
        r = judge(rel, ecad, only, vendor, _v.opt(argv, "--manifest", None), _v.opt(argv, "--profiles", None))
    except Refused as e:
        print("reliability: the list is refused by its own check (%s)" % e)
        return _v.write("reliability", _v.INCONCLUSIVE, denominator=0, rules=["REL-001"],
                        inputs={"board": only} if only else {},
                        note="the reliability list is refused by its own check: %s" % " ".join(str(e).split())[:400],
                        missing_input="a reliability list that passes its own check: %s" % " ".join(str(e).split())[:300], **kw)
    except Exception as e:
        print("reliability: the list could not be read (%s: %s)" % (type(e).__name__, e))
        return _v.write("reliability", _v.INCONCLUSIVE, denominator=0, rules=["REL-001"],
                        inputs={"board": only} if only else {},
                        note="the reliability list could not be read: %s" % " ".join(str(e).split())[:200],
                        missing_input="the reliability list: it could not be read (%s)" % type(e).__name__, **kw)
    if only and not r:
        print("reliability: board %s is not a board of the manifest and the list declares nothing for it" % only.upper())
        return _v.write("reliability", _v.INCONCLUSIVE, denominator=0, rules=["REL-001"], inputs={"board": only},
                        note="this board is not a board of the manifest and carries no declared list of "
                             "load-bearing or cycling parts",
                        missing_input="a board of the manifest: %s is not one" % only.upper(), **kw)
    fails = [f for v in r.values() for f in v["fails"]]
    open_ = [w for v in r.values() for w in v["inconclusive"]]
    inp = _inputs(r, rel, only)
    print("reliability: the list %s sha256 %s" % (inp["list"]["path"] if isinstance(inp["list"], dict) else inp["list"],
                                                   _sha(rel or REL)))
    for letter, v in sorted(r.items()):
        a = v.get("artefact")
        print("reliability: %-3s %-12s %s" % (letter.upper(), v["result"],
              ("%s %s sha256 %s, %d part(s)" % (v["artefact_kind"].replace("_", " "), a["path"], a["sha256"], a["parts"]))
              if a else "no artefact read"))
        if v["netlist"]:
            f = v["figures"]
            print("             %d candidate(s): %d classed in %d class(es), %d excluded by %d exclusion(s), %d refused; "
                  "figures: %d cited, %d none published, %d not mated, %d owed; measures owed: %d"
                  % (v["candidates"], v["covered"], v["classes"], v["excluded"], v["exclusions"], v["refused"],
                     f.get("cited", 0), f.get("none_published", 0), f.get("not_mated", 0), f.get("owed", 0),
                     v["measures_owed"]))
        for x in v["excluded_by"]:
            print("  excluded %s: %d part(s), %s: %s" % (letter.upper(), len(x["parts"]), _short(x["parts"], 8), x["reason"]))
    for n in [n for v in r.values() for n in v["notes"]][:12]: print("  note %s" % n)
    for w in open_: print("  INCONCLUSIVE %s" % w)
    for f in fails: print("  FAIL %s" % f)
    if "--json" in argv: print(json.dumps(r, indent=1))
    res = _v.FAIL if fails else (_v.INCONCLUSIVE if open_ else _v.PASS)
    absent = [v["missing_input"] for v in r.values() if v.get("missing_input")]
    tot = lambda k: sum(v[k] for v in r.values())
    figs = lambda k: sum(v["figures"].get(k, 0) for v in r.values())
    return _v.write("reliability", res, rules=["REL-001"],
                    counts={"boards": len(r), "candidates": tot("candidates"), "classed": tot("covered"),
                            "covered": tot("covered"), "excluded": tot("excluded"), "refused": tot("refused"),
                            "classes": tot("classes"), "exclusions": tot("exclusions"),
                            "figures_cited": figs("cited"), "figures_none_published": figs("none_published"),
                            "figures_not_mated": figs("not_mated"), "figures_owed": figs("owed"),
                            "measures_owed": tot("measures_owed"),
                            "classes_undecided": sum(len(v["undecided"]) for v in r.values()),
                            "citations_unjudged": tot("unjudged"),
                            "fail": len(fails), "inconclusive": len(open_),
                            "per_board": {k: {"result": v["result"], "candidates": v["candidates"],
                                              "classed": v["covered"], "excluded": v["excluded"],
                                              "refused": v["refused"], "held_by": v["held_by"],
                                              "classes_undecided": len(v["undecided"]),
                                              "citations_unjudged": v["unjudged"],
                                              "bound": bool((v.get("pin") or {}).get("bound")),
                                              "artefact": ({"kind": v["artefact_kind"], "sha256_16": v["artefact"]["sha256_16"]}
                                                           if v.get("artefact") else None)}
                                          for k, v in sorted(r.items())}},
                    denominator=tot("candidates"),
                    evidence=(fails + open_ + ["%s: %d part(s) excluded (%s): %s" % (k.upper(), len(x["parts"]),
                                                                                    _short(x["parts"], 6), x["reason"])
                                               for k, v in sorted(r.items()) for x in v["excluded_by"]])[:50],
                    inputs=inp, note=NOTE,
                    missing_input=("; ".join(absent) if (absent and res == _v.INCONCLUSIVE) else None), **kw)


if __name__ == "__main__":
    # EVERY GATE LEAVES A READING WHEN IT RAISES (18 September 2026). The thirteen one-line entries of this
    # morning were the gates a crash had already cost a verdict; these are the rest of the deciding gates in
    # the coverage map, guarded the same way, so a rule whose tool raised reads INCONCLUSIVE naming the
    # exception rather than 'no verdict', which the registry reads as nobody having looked.
    sys.exit(_v.guard("reliability", main, sys.argv[1:]))
