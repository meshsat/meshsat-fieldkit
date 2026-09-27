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

WHAT IT CHECKS:
  * completeness: every candidate is disposed, exactly once, and a class or an exclusion speaks of the land the
    board really carries (`footprints`), so a class written for one connector family cannot cover another;
  * a class names its load and its measure;
  * a class's cycle figure cites the maker's document held in this tree, by its sha, with the page and the words;
    a class with no figure says which of three things is true: the maker's document states none
    (`none_published`, with the documents that were read), nothing is mated (`not_mated`: a solder land, a screw
    joint), or the figure is OWED because the part or its document is not identified, which carries an open
    item and keeps the board's reading INCONCLUSIVE until it is closed;
  * a declared count matches the board.

WHAT IT CANNOT DO is test anything: REL-001 is verified at the PROTOTYPE and no board has been built. This is the
desk half: a reading of a netlist and a list. It replaces no physical verification, the figures are the makers'
ratings of the parts and not a claim about the kit, and it sees no mass, so the joints under heavy soldered
parts are outside it.

Usage: reliability.py [--rel pcb_reliability.yaml] [--ecad <dir>] [--board <letter>] [--vendor <dir>]
                      [--manifest <readiness_manifest.json>] [--profiles <dir holding routeflow/>]
                      [--out-dir <dir>] [--json]
       exit 0 PASS, 1 FAIL, 3 INCONCLUSIVE
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
WEAR = re.compile(r"socket|receptacle|holder|SMA|XT60|JST|IDC|header|standoff|U\.FL|M\.2|blade", re.I)
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
        if not isinstance(src, dict):
            fails.append("%s gives %d cycles and cites no document for them" % (who, cyc)); return None
        n = len(fails)
        for k in ("page", "words"):
            if not str(src.get(k) or "").strip():
                fails.append("%s cites its figure without the %s" % (who, k))
        _cited(src, vdir, have_vendor, who, fails, unjudged)
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
    elif kind == "owed":
        it = (open_items or {}).get(nof.get("open_item"))
        if not isinstance(it, dict):
            fails.append("%s owes its figure and names no open item of this list (%r)" % (who, nof.get("open_item")))
        elif not (str(it.get("what") or "").strip() and str(it.get("next_action") or "").strip()):
            fails.append("%s owes its figure under open item %s, which does not say what is owed and the next action"
                         % (who, nof.get("open_item")))
    return kind if len(fails) == n else None


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
               prose_only=[], by_words=[], inventory=[], excluded_by=[], figures={}, owed=[], how={})
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
            out["owed"].append("%s: class %s owes its cycle figure (open item %s: %s)"
                               % (L, c.get("name"), c["no_figure"].get("open_item"),
                                  " ".join(str(open_items[c["no_figure"]["open_item"]].get("what")).split())))
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
    if unjudged:
        why_not.append("%s: the vendor library is not in this tree (%s), so %d cited document(s) could not be "
                       "checked: %s" % (L, vdir, len(unjudged), _short(sorted(set(unjudged)), 4)))
    why_not.extend(out["owed"])
    out["missing_input"] = missing
    out["result"] = _v.FAIL if fails else (_v.INCONCLUSIVE if why_not else _v.PASS)
    return out


def judge(rel=None, ecad=None, only=None, vendor=None, manifest=None, profiles=None):
    """{letter: reading} for every board of the manifest and every board the list declares (or `only`)."""
    import yaml
    d = yaml.safe_load(open(rel or REL, encoding="utf-8"))
    if not isinstance(d, dict): raise ValueError("the list is not a mapping")
    inv = d.get("inventory")
    bad = _wi.check_rules(inv)
    if bad: raise ValueError("; ".join(bad))
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
    try:
        r = judge(rel, ecad, only, vendor, _v.opt(argv, "--manifest", None), _v.opt(argv, "--profiles", None))
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
                  "figures: %d cited, %d none published, %d not mated, %d owed"
                  % (v["candidates"], v["covered"], v["classes"], v["excluded"], v["exclusions"], v["refused"],
                     f.get("cited", 0), f.get("none_published", 0), f.get("not_mated", 0), f.get("owed", 0)))
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
                            "fail": len(fails), "inconclusive": len(open_),
                            "per_board": {k: {"result": v["result"], "candidates": v["candidates"],
                                              "classed": v["covered"], "excluded": v["excluded"],
                                              "refused": v["refused"]} for k, v in sorted(r.items())}},
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
