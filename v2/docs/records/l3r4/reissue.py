#!/usr/bin/env python3
"""The re-issue of the definition documents on the owner's layer 3 answers (L3-C26; MESHSAT-1357, layer 3 round 4,
30 September 2026). PREPARED: it writes nothing until the owner has decided every row of
v2/docs/handover/layer3/OWNER-DECISIONS-L3.md and the prepared scripts have recorded his answers in the registry.

`v2/docs/CONOPS.md` and `v2/docs/PRODUCT-BRIEF.md` are baselined (v2/docs/handover/DEFINITION-STATUS.md): a baseline is
reopened only when a requirement, the scope, the operating concept or another relevant decision changes, and the
affected document is then issued again with the change stated in it. The rows L3-OD1 to L3-OD6 restate requirements
those documents trace to, so their answers reopen both. This script maps every passage an answer makes inconsistent
with the requirements (PASSAGES below, each located by its line in the baselined file and by its own text) and, once
the answers are recorded, writes the proposed re-issue:

  v2/docs/handover/layer3/DEFINITION-REISSUE-DRAFT.md   every passage the answers change: its baselined text and its
                                                          proposed text, each naming its row and the owner's ruling
  v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md  the change record the owner approves (l3r2.yaml's
                                                          `definition_reissue`: {record, sha16, approved_by})

It never writes into the baselined files: they change only after the owner approves the change record by a ruling
whose `decides` is `definition_reissue`, and then through their layers' review. It refuses, writing nothing:
  - while any row is undecided in the registry (a ruling carrying `decides: <row>:<option>`);
  - on a set of answers that is not coherent (render_l3r2.coherent, the combinations l3r2.yaml states), or while an
    open conflict other than CFL-017 cites one of the answers' rulings;
  - when a baselined file is not the text l3r2.yaml's `baseline_definition` names (sha256/16), or a passage's text is
    not found exactly once where the map says;
  - when an output path is a baselined file, or a written text carries a dash character.
Every proposed text is built from the registry: the rulings' own text, the statements of the records they restated,
and the option each row was answered with. Nothing else is stated.

Usage:
  python3 reissue.py [--registry PATH] [--out-dir DIR] [--check]   the draft and the change record (--check: compare)
  python3 reissue.py --map [--check]                                v2/docs/records/l3r4/PASSAGE-MAP.md, the passages
                                                                    each row and option changes (no answer needed)
"""
import os
import re
import sys
import textwrap

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402

L3 = os.path.join(E.TOP, "v2", "docs", "handover", "layer3")
sys.path.insert(0, L3)
import render_l3r2 as RL  # noqa: E402
import yaml  # noqa: E402

DOCS = {"CONOPS": "v2/docs/CONOPS.md", "BRIEF": "v2/docs/PRODUCT-BRIEF.md"}
ROWS = ("L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6")
DRAFT = "DEFINITION-REISSUE-DRAFT.md"
RECORD = "DEFINITION-CHANGE-RECORD-L3.md"
MAP = os.path.join(HERE, "PASSAGE-MAP.md")
WIDTH = 120
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
ALL = "every answer"


# ------------------------------------------------------------------------------------------------ the answers
class Ctx:
    """The recorded answers, read from the registry: option, ruling and date per row, and the records they restated."""

    def __init__(self, req, data):
        self.req, self.data = req, data
        self.dec = RL.decided(req, data)
        self.rul = {r["id"]: r for r in req["owner_rulings"]}
        self.rec = {r["id"]: r for r in req["records"]}

    def O(self, row): return self.dec[row][0]
    def R(self, row): return self.dec[row][1]
    def date(self, row): return long_date(self.dec[row][2])
    def cite(self, row): return "owner ruling %s on row %s" % (self.R(row), row)

    def text(self, row):
        """The ruling's decided text, as the registry holds it, without its 'Row ... decided:' head."""
        t = " ".join(str(self.rul[self.R(row)]["ruling"]).split())
        m = re.match(r"^Row %s of \S+ (decided|approved)[:,] " % re.escape(row), t)
        if not m: E.refuse("ruling %s does not open with 'Row %s of ... decided:'" % (self.R(row), row))
        t = t[m.end():]
        return t[0].upper() + t[1:]

    def stmt(self, rid):
        r = self.rec.get(rid)
        if r is None: E.refuse("the registry holds no record %s" % rid)
        return " ".join(str(r["statement"]).split())

    def lid(self):
        """The lid pack's block, from row L3-OD2's option label in l3r2.yaml ('the lid pack is 4SnP')."""
        row = next(x for x in self.data["decisions"] if x["id"] == "L3-OD2")
        lab = next(o["label"] for o in row["options"] if o["id"] == self.O("L3-OD2"))
        m = re.findall(r"the lid pack is (4S\d+P)", lab)
        if len(m) != 1: E.refuse("row L3-OD2's option %s names no single lid block" % self.O("L3-OD2"))
        return m[0]

    def store(self):
        return ("two separately protected packs of the Samsung INR18650-35E, a base 4S6P across the two base pockets "
                "and a %s lid pack under its own protection board, each with its own charger path and gauge" % self.lid())

    def deploy_req(self):
        """The requirement row L3-OD4 `adopt` added: the one record citing only that ruling, under NEED-06."""
        rid = self.R("L3-OD4")
        hits = [r["id"] for r in self.req["records"] if r.get("rulings") == [rid] and r.get("parent") == "NEED-06"]
        if len(hits) != 1: E.refuse("row L3-OD4's ruling %s is cited alone by %d NEED-06 records, not one" % (rid, len(hits)))
        return hits[0]

    def citing(self, rid):
        return [r["id"] for r in self.req["records"] if rid in (r.get("rulings") or [])]


def long_date(s):
    y, m, d = str(s).split("-")
    return "%d %s %s" % (int(d), MONTHS[int(m) - 1], y)


def short_date(s):
    y, m, d = str(s).split("-")
    return "%d %s" % (int(d), MONTHS[int(m) - 1][:3])


def wrap(text, first="", rest=""):
    return "\n".join(textwrap.wrap(" ".join(text.split()), WIDTH, initial_indent=first, subsequent_indent=rest,
                                   break_on_hyphens=False, break_long_words=False))


def sub(old, a, b):
    if old.count(a) != 1: E.refuse("the passage does not carry %r once" % a[:60])
    return old.replace(a, b)


def and_list(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def rulings_list(c):
    return and_list(sorted({c.R(r) for r in ROWS}, key=lambda x: int(x.split("-")[1])))


def dates(c):
    ds = sorted({c.dec[r][2] for r in ROWS})
    return and_list([long_date(d) for d in ds])


# ------------------------------------------------------------------------------------------------ the passages
class P:
    """A passage of a baselined document: from `start` on line `a` to the end of `end` on line `b` (line numbers of
    the baselined text), changed when any row of `when` is answered with one of its options (`when` = ALL: always).
    `new(ctx, old)` gives the proposed text. kind DEFINITION: restated in the re-issue; CURRENT: a statement of the
    design as generated, which stays and is read through DEFINITION-STATUS.md's current values (its rule: a circuit
    correction updates that page, not the baseline)."""

    def __init__(self, pid, doc, a, start, b, end, when, new, what, kind="DEFINITION"):
        self.pid, self.doc, self.a, self.start, self.b, self.end = pid, doc, a, start, b, end
        self.when, self.new, self.what, self.kind = when, new, what, kind

    def rows(self):
        return list(ROWS) if self.when == ALL else [r for r in ROWS if r in self.when]

    def fires(self, c):
        return self.when == ALL or any(c.O(r) in opts for r, opts in self.when.items())


def status_line(layer):
    old = "**Status: layer %d of the foundation baseline (MESHSAT-1357), BASELINED at `a9f212c7`,**" % layer
    return old, (lambda c, o: "**Status: layer %d of the foundation baseline (MESHSAT-1357), RE-ISSUED on the owner's "
                 "rulings on layer 3 (the re-issue note below), pending its layer's review; BASELINED at `a9f212c7`,**" % layer)


def head_note(doc):
    def f(c, old):
        base = "handover/layer3/"
        s = ("**Re-issue on the owner's rulings on layer 3 (%s).** The owner decided rows L3-OD1 to L3-OD6 of `%s"
             "OWNER-DECISIONS-L3.md` (owner rulings %s). They restate requirements this %s traces to, which reopens it "
             "by the rule above: each passage they change is restated in place and names its row and ruling, the "
             "change record `%s%s` lists every passage, and its draft `%s%s` keeps each one's baselined text. The "
             "owner's approval of that record is named in `%sl3r2.yaml` (`definition_reissue`)." % (
                 dates(c), base, rulings_list(c), "document" if doc == "CONOPS" else "brief", base, RECORD, base, DRAFT,
                 base))
        s += (" Where a passage this re-issue does not restate says \"the pack\", it reads as each of the two packs of "
              "%s, as that ruling reads the requirements." % c.cite("L3-OD1"))
        if doc == "CONOPS" and c.O("L3-OD2") == "qmx-out":
            s += (" Where a passage this re-issue does not restate names the QMX, its HF rail or its bank port, it states "
                  "the design as generated before %s took HF out of the kit; the current values are kept in "
                  "`handover/DEFINITION-STATUS.md`." % c.cite("L3-OD2"))
        return old + "\n\n" + wrap(s)
    return f


def solar_setting(c):
    if c.O("L3-OD3") == "keep":
        return "the kit's solar array on the solar input, inside REQ-016's window (%s)" % c.cite("L3-OD3")
    return ("the kit's solar array on the solar input, its panels and folding stand set out beside the case (%s)"
            % c.cite("L3-OD3"))


def solar_source(c):
    arr = {"2s2p": "four 100 W panels in two series pairs (2S2P, 400 Wp) into board E's 200 W stage",
           "1s4p": "four 100 W panels in parallel (1S4P, 400 Wp) into board E's 200 W stage"}
    if c.O("L3-OD3") == "keep":
        return ("the kit's solar array inside REQ-016's 100 W window, its panels and folding stand carried outside the "
                "case (%s)" % c.cite("L3-OD3"))
    return ("the kit's solar array, %s, its panels and folding stand carried outside the case (%s; REQ-016)"
            % (arr[c.O("L3-OD3")], c.cite("L3-OD3")))


def since_list(c):
    parts = ["the second pack has left the deferred list and joined the core (%s)" % c.cite("L3-OD1")]
    if c.O("L3-OD2") == "qmx-out": parts.append("HF has left the kit (%s)" % c.cite("L3-OD2"))
    if c.O("L3-OD2") == "tablet-out":
        parts.append("the tablet bracket has left the kit, the tablet's use kept outside the case (%s)" % c.cite("L3-OD2"))
    return and_list(parts)


def energy(c, old):
    op = "keeps" if c.O("L3-OD3") == "keep" else "restates"
    s = ("**What M1 asks of the kit's energy, as the owner ruled it on layer 3** (rows L3-OD1, L3-OD3 and L3-OD6 of "
         "`handover/layer3/OWNER-DECISIONS-L3.md`; this replaces the layer-4 finding of 27 September 2026 on D-06's one "
         "pack, whose text the re-issue's draft `handover/layer3/%s` keeps). The store is %s (%s). The solar input is REQ-016 as "
         "owner ruling %s %s it: \"%s\" The weather M1 is judged on is the owner's (%s): \"%s\" M1's balance is "
         "requirement REQ-072: \"%s\" Whether the design meets it is REQ-072's reading in the requirements registry, "
         "with the energy basis and the cases it names; no figure of it is demonstrated capability, and nothing has "
         "been built." % (DRAFT, c.store(), c.cite("L3-OD1"), c.R("L3-OD3"), op, c.stmt("REQ-016"), c.cite("L3-OD6"),
                          c.text("L3-OD6"), c.stmt("REQ-072")))
    return wrap(s)


def m1_setting(c, old):
    new = sub(old, "a solar panel on the solar input.", solar_setting(c) + ".")
    if c.O("L3-OD4") == "adopt":
        rq = c.deploy_req()
        new += " **The open kit's deployment condition (%s; requirement %s):** \"%s\"" % (c.cite("L3-OD4"), rq, c.stmt(rq))
    return new


def deploy_row(c, old):
    add = ", sets out the solar array's panels and folding stand beside the case (%s)" % c.cite("L3-OD3")
    if c.O("L3-OD4") == "adopt":
        add += ", and stands the open kit as requirement %s sets it (%s)" % (c.deploy_req(), c.cite("L3-OD4"))
    return sub(old, "(D-02e);", "(D-02e)" + add + ";")


def od5_quote(c):
    return "%s: \"%s\"" % (c.cite("L3-OD5"), c.text("L3-OD5"))


def new_rows(c, old):
    rows = []
    for row in ROWS:
        r = c.rul[c.R(row)]
        rows.append("| %s | %s | RULED %s | %s |" % (r["id"], " ".join(str(r["title"]).split()), short_date(c.dec[row][2]),
                                                     c.text(row)))
    return (old[:-2] + "; the owner decided those changes on layer 3, in the six rulings that follow |\n" + "\n".join(rows))


def brief_night(c, old):
    core = (c.rec.get("REQ-072") or {}).get("prototype_1") == "core"
    s = ("- Not shown to hold mission M1. The owner's rulings on layer 3 set M1's store, %s (%s), its solar input (%s; "
         "REQ-016) and the weather it is judged on (%s: \"%s\"); whether the design meets M1 is requirement REQ-072's "
         "reading%s (`CONOPS.md` M1; the requirements registry), and no figure of it is demonstrated capability."
         % (c.store(), c.cite("L3-OD1"), c.cite("L3-OD3"), c.cite("L3-OD6"), c.text("L3-OD6"),
            ", part of prototype 1's core" if core else ""))
    return wrap(s, "", "  ")


def brief_power(c, old):
    new = sub(old, "- **Power:** its own pack;", "- **Power:** its own two packs (%s);" % c.cite("L3-OD1"))
    new = sub(new, "a solar input; missions longer than\n  the pack rely",
              "a solar input from %s; missions longer than\n  the packs rely" % solar_source(c))
    new = sub(new, "(D-06), and on the pack and solar input alone the kit does not run through a night (REQ-072, \"What "
                   "it is not, today\").",
              "(D-06, kept by %s), and whether the packs and the solar input carry mission M1 is requirement REQ-072's "
              "reading (\"What it is not, today\")." % c.cite("L3-OD1"))
    return new


def brief_bearers(c, old):
    if c.O("L3-OD2") == "qmx-out": return "no HF since %s, " % c.cite("L3-OD2")
    return ("HF (an assembled QRP Labs QMX, carried outside the case on a sealed lead across the case wall, %s), "
            % c.cite("L3-OD2"))


QMX_OUT, QMX_ANY, LID_ITEM = ("qmx-out",), ("qmx-out", "qmx-outside"), ("qmx-out", "qmx-outside", "tablet-out")
OD3_ANY, OD5_ANY = ("2s2p", "1s4p", "keep"), ("reading-c", "measure", "cells")
APPROVE = {"L3-OD1": ("approve",)}
LID_ANY = ("qmx-out", "qmx-outside", "tablet-out", "both-kept")
STORE = {"L3-OD1": ("approve",), "L3-OD2": LID_ANY}   # a passage naming the store names the lid block row L3-OD2 sets

PASSAGES = [
    # ---------------------------------------------------------------------------------------------- CONOPS.md
    P("C01", "CONOPS", 3, status_line(2)[0], 3, status_line(2)[0], ALL, status_line(2)[1],
      "the status line of the head"),
    P("C02", "CONOPS", 15, "a change to it alone does not reopen this", 16, "document.", ALL, head_note("CONOPS"),
      "the head, after the rule of reopening: the re-issue note"),
    P("C03", "CONOPS", 65, "The HF transmitter is to operate on the amateur bands under the owner's licence (appendix 32.50 "
      "item 16a)", 65, "item 16a)", {"L3-OD2": QMX_ANY},
      lambda c, o: ("The kit carries no HF transmitter: the QMX HF set and its HF function left the kit by %s "
                    "(REQ-067)" % c.cite("L3-OD2")) if c.O("L3-OD2") == "qmx-out" else
      ("The HF transmitter, the QMX HF set carried outside the case on a sealed lead across the case wall (%s), is to "
       "operate on the amateur bands under the owner's licence (appendix 32.50 item 16a)" % c.cite("L3-OD2")),
      "section 1, the kit operator: the HF transmitter"),
    P("C04", "CONOPS", 67, "the lid tablet (ATAK class, fed by the USB-C outlet and the kit's WiFi, 32.50 item 16d)", 67,
      "32.50 item 16d)", {"L3-OD2": LID_ITEM},
      lambda c, o: ("a tablet (ATAK class) carried outside the case and served by the kit's WiFi and the USB-C outlet, "
                    "the lid bracket having left the kit by %s (32.50 item 16d)" % c.cite("L3-OD2"))
      if c.O("L3-OD2") == "tablet-out" else
      ("the lid tablet (ATAK class, an 8 inch tablet in the lid bracket beside the lid pack since %s, fed by the USB-C "
       "outlet and the kit's WiFi, 32.50 item 16d; REQ-011)" % c.cite("L3-OD2")),
      "section 1, the local end users: the lid tablet"),
    P("C05", "CONOPS", 68, "| Remote correspondents | reached over Iridium Messaging Transport, 5G cellular, HF (Winlink, "
      "Reticulum over the Mercury modem), VHF APRS, or a second kit;", 68, "or a second kit;", {"L3-OD2": QMX_OUT},
      lambda c, o: ("| Remote correspondents | reached over Iridium Messaging Transport, 5G cellular, VHF APRS, or a "
                    "second kit (HF left the kit by %s);" % c.cite("L3-OD2")),
      "section 1, the remote correspondents: HF"),
    P("C06", "CONOPS", 69, "| Second kit | kit-to-kit WiFi link without an access point, LoRa mesh, HF |", 69, "HF |",
      {"L3-OD2": QMX_OUT},
      lambda c, o: ("| Second kit | kit-to-kit WiFi link without an access point, LoRa mesh (HF left the kit by %s) |"
                    % c.cite("L3-OD2")),
      "section 1, the second kit: HF"),
    P("C07", "CONOPS", 70, "| Power sources | the kit's own pack (one 4S3P block, owner ruling D-06),", 70, "a solar panel |",
      {"L3-OD1": ("approve",), "L3-OD2": LID_ANY, "L3-OD3": OD3_ANY},
      lambda c, o: sub(sub(o, "the kit's own pack (one 4S3P block, owner ruling D-06),",
                           "the kit's own store, %s (%s, superseding D-06's one 4S3P block)," % (c.store(), c.cite("L3-OD1"))),
                       "a solar panel |", solar_source(c) + " |"),
      "section 1, the power sources: the pack and the solar panel"),
    P("C08", "CONOPS", 105, "HF and a second pack. Deferral removes nothing from the design.", 105,
      "Deferral removes nothing from the design.",
      {"L3-OD1": ("approve",), "L3-OD2": ("qmx-out", "tablet-out")},
      lambda c, o: o + " Since the owner's rulings on layer 3, %s." % since_list(c),
      "section 2a, the functions D-01 names outside the core"),
    P("C09", "CONOPS", 107, "The second pack has no location found yet:", 111, "deferred function of D-01; it is not withdrawn.",
      STORE,
      lambda c, o: wrap("**The two packs (%s, %s; D-06 superseded).** The ruling reads: \"%s\" Row L3-OD2 set the lid "
                        "pack at %s (%s)." % (c.cite("L3-OD1"), c.date("L3-OD1"), c.text("L3-OD1"), c.lid(),
                                              c.cite("L3-OD2"))),
      "section 2a, the second pack"),
    P("C10", "CONOPS", 115, "HF is deferred, VHF voice is not named", 115, "HF is deferred, VHF voice is not named",
      {"L3-OD2": QMX_OUT},
      lambda c, o: "HF has left the kit (%s), VHF voice is not named" % c.cite("L3-OD2"),
      "section 2a, the core's messaging row: HF"),
    P("C11", "CONOPS", 117, "| Pack, vehicle and solar charging | NEED-05 | the three inputs (", 117, "the three inputs (",
      APPROVE,
      lambda c, o: ("| Pack, vehicle and solar charging | NEED-05 | the three inputs into both packs of %s, each on its "
                    "own charger path (" % c.cite("L3-OD1")),
      "section 2a, the core's charging row"),
    P("C12", "CONOPS", 120, "| Pack safety | NEED-13 | the pack's protection, including the floor of D-15 |", 120,
      "the floor of D-15 |", APPROVE,
      lambda c, o: ("| Pack safety | NEED-13 | each pack's protection, including the floor of D-15, for both packs of %s |"
                    % c.cite("L3-OD1")),
      "section 2a, the core's pack safety row"),
    P("C13", "CONOPS", 128, "such as the accessory", 129, "outlets under NEED-05 or the HF rail.", {"L3-OD2": QMX_OUT},
      lambda c, o: ("such as the accessory\noutlets under NEED-05; HF, which the ruling also left out, has since left the "
                    "kit (%s)." % c.cite("L3-OD2")),
      "section 2a, the deferred example of the HF rail"),
    P("C14", "CONOPS", 154, "The kit sits on a table or a vehicle tailgate, lid open,", 155, "a solar panel on the solar input.",
      {"L3-OD3": OD3_ANY, "L3-OD4": ("adopt",)}, m1_setting,
      "section 3, M1's setting: the solar panel and the deployment condition"),
    P("C15", "CONOPS", 161, "by day the pack charges from solar while the kit runs", 161, "while the kit runs", APPROVE,
      lambda c, o: "by day the packs of %s charge from solar while the kit runs" % c.cite("L3-OD1"),
      "section 3, M1's sequence: the pack charging by day"),
    P("C16", "CONOPS", 163, "the kit keeps running on its pack plus solar for the mission's duration (NEED-05)", 163,
      "duration (NEED-05)", APPROVE,
      lambda c, o: ("the kit keeps running on its packs plus solar for the mission's duration (NEED-05; %s)"
                    % c.cite("L3-OD1")),
      "section 3, M1's must-hold: the pack plus solar"),
    P("C17", "CONOPS", 167, "**What that asks of the kit's energy, and what the", 198, "whatever the solar rating.",
      {"L3-OD1": ("approve",), "L3-OD2": LID_ANY, "L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")}, energy,
      "section 3, M1's energy: the night, the day's energy, the solar window, the design month and the routes"),
    P("C18", "CONOPS", 215, "Until then REQ-072 reads FAIL and this section is not", 216, "restated.", APPROVE,
      lambda c, o: ("The owner answered it on layer 3 with the rulings of section 7 (rows L3-OD1 to L3-OD6), and this "
                    "section is restated on them; REQ-072's reading is kept in the requirements registry."),
      "section 3, M1: the owner's instruction D-20"),
    P("C19", "CONOPS", 307, "| Deploy | operator opens the lid, fits antennas, connects cables, shades the plate (D-02e);", 307,
      "shades the plate (D-02e);", {"L3-OD3": OD3_ANY, "L3-OD4": ("adopt",)}, deploy_row,
      "section 4, the Deploy row"),
    P("C20", "CONOPS", 313, "the 4 A charge setting is to be lowered for cell life on the ruled 4S3P pack (a session item "
      "under D-06)", 313, "(a session item under D-06)", APPROVE,
      lambda c, o: ("each pack's charge setting is to stay within REQ-075's limit for cell life, on the two packs of %s "
                    "(a session item carried from D-06)" % c.cite("L3-OD1")),
      "section 4, the Charging row: the charge setting"),
    P("C21", "CONOPS", 321, "D-02a's storage margins (+71 C, -33 C) are beyond the cells' ratings, so they run on the kit less "
      "its pack and on the pack at its cells' own limits", 321, "at its cells' own limits", {"L3-OD5": OD5_ANY},
      lambda c, o: o + " (%s)" % od5_quote(c),
      "section 4, the Storage row: D-02a's storage margins"),
    P("C22", "CONOPS", 346, "| 4S3P, the ruled pack, +20 C: new / aged 80 % / aged 60 %, h |", 346, "aged 60 %, h |", APPROVE,
      lambda c, o: "| 4S3P, D-06's pack (superseded by %s), +20 C: new / aged 80 %% / aged 60 %%, h |" % c.cite("L3-OD1"),
      "section 4a, the power-state table's runtime column"),
    P("C23", "CONOPS", 363, "**The pack (owner ruling D-06, 26 September 2026).**", 363,
      "**The pack (owner ruling D-06, 26 September 2026).**", STORE,
      lambda c, o: ("**The pack of owner ruling D-06 (26 September 2026), superseded by %s: the kit now carries %s; the "
                    "paragraph below and the runtime columns above are D-06's pack's, kept as its record until they are "
                    "restated for the two packs (REQ-014 and REQ-075).**" % (c.cite("L3-OD1"), c.store())),
      "section 4a, the pack paragraph"),
    P("C24", "CONOPS", 369, "table's runtime columns describe the ruled pack.", 369, "describe the ruled pack.", APPROVE,
      lambda c, o: "table's runtime columns describe D-06's pack.",
      "section 4a, what the runtime columns describe"),
    P("C25", "CONOPS", 999, "(D-06: one 4S3P 18650 block of about 145 Wh, its fit designed against Peli's figures since D-08 "
      "was reversed)", 999, "since D-08 was reversed)", APPROVE,
      lambda c, o: o[:-1] + ("; superseded by %s, whose runtime REQ-014 states for both packs together and for each pack "
                             "alone)" % c.cite("L3-OD1")),
      "section 6, the pack the figures are for"),
    P("C26", "CONOPS", 1009, "**The runtime requirement (owner ruling D-06, 26 September 2026)**", 1010,
      "a typical mode at +20 C for an aged pack.", APPROVE,
      lambda c, o: sub(sub(o, "(owner ruling D-06, 26 September 2026)**",
                           "(owner ruling D-06, 26 September 2026, kept by %s for both packs together and for each pack "
                           "alone)**" % c.cite("L3-OD1")), "for an aged pack.", "for aged packs."),
      "section 6, the runtime requirement"),
    P("C27", "CONOPS", 1012, "(3.35 Ah per cell, so 8.04 Ah for the 3P block)", 1012, "for the 3P block)", APPROVE,
      lambda c, o: ("(3.35 Ah per cell, so 8.04 Ah for D-06's 3P block, and the same share of each pack of %s)"
                    % c.cite("L3-OD1")),
      "section 6, what aged means in ampere-hours"),
    P("C28", "CONOPS", 1019, "Missions longer than the pack rely on vehicle or solar input: M1 is set at 72 hours (section 3,",
      1024, "session's 72 hours, not asked.", APPROVE,
      lambda c, o: wrap("Missions longer than the packs rely on vehicle or solar input: M1 is set at 72 hours (section 3, "
                        "taken by the session under the owner's standing rule in place of the later setting D-06 reserved "
                        "for the owner, whose own setting replaces it), and whether the two packs of %s carry it with the "
                        "solar input of %s on the weather basis of %s is REQ-072's reading in the requirements registry "
                        "(section 3)." % (c.cite("L3-OD1"), c.cite("L3-OD3"), c.cite("L3-OD6"))),
      "section 6, missions longer than the pack and M1's night"),
    P("C29", "CONOPS", 1040, "operate to specification inside the envelope; survive and recover at the margin |", 1040,
      "survive and recover at the margin |", {"L3-OD5": OD5_ANY},
      lambda c, o: o[:-2] + ". **Answered on %s by %s (CFL-017):** %s |" % (c.date("L3-OD5"), c.cite("L3-OD5"),
                                                                             c.text("L3-OD5")),
      "section 7, the D-02a row"),
    P("C30", "CONOPS", 1048, "| D-06 | Pack size and runtime target | RULED 26 Sep |", 1048, "RULED 26 Sep |", APPROVE,
      lambda c, o: ("| D-06 | Pack size and runtime target | RULED 26 Sep, SUPERSEDED %s by %s |"
                    % (short_date(c.dec["L3-OD1"][2]), c.cite("L3-OD1"))),
      "section 7, the D-06 row's status"),
    P("C31", "CONOPS", 1062, "and the smallest justified changes presented for the owner's decision; unmet criteria stay "
      "visible |", 1062, "unmet criteria stay visible |", ALL, new_rows,
      "section 7, the D-20 row and the owner's six rulings on layer 3"),
    P("C32", "CONOPS", 1101, "On pack and solar alone the kit does not carry it through a single night on D-06's one pack",
      1101, "not a shorter mission.", APPROVE,
      lambda c, o: ("The store, the solar input and the weather it is judged on are the owner's rulings on layer 3 (%s, "
                    "%s and %s, section 7), which replace the finding this row recorded on D-06's one pack; whether the "
                    "design carries M1 is REQ-072's reading." % (c.R("L3-OD1"), c.R("L3-OD3"), c.R("L3-OD6"))),
      "section 7a, M1's mission duration row"),
    P("C33", "CONOPS", 1117, "| M1's solar window and design month (REQ-016 and REQ-072 of the requirements registry; Review "
      "B of layer 3, B4 and B5); **pass 3** | ", 1117, "**pass 3** | ", {"L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")},
      lambda c, o: o + ("**Superseded on %s by owner rulings %s and %s (rows L3-OD3 and L3-OD6, section 7), which now set "
                        "REQ-016 and M1's weather basis; the choice as taken:** " % (
                            long_date(max(c.dec["L3-OD3"][2], c.dec["L3-OD6"][2])), c.R("L3-OD3"), c.R("L3-OD6"))),
      "section 7a, M1's solar window and design month row"),
    # ---------------------------------------------------------------------------------------------- PRODUCT-BRIEF.md
    P("B01", "BRIEF", 3, status_line(1)[0], 3, status_line(1)[0], ALL, status_line(1)[1], "the status line of the head"),
    P("B02", "BRIEF", 15, "a change to it alone does not reopen this brief.", 15, "does not reopen this brief.", ALL,
      head_note("BRIEF"), "the head, after the rule of reopening: the re-issue note"),
    P("B03", "BRIEF", 58, "the HF transmitter is to operate on the amateur bands under the owner's licence |", 58,
      "under the owner's licence |", {"L3-OD2": QMX_ANY},
      lambda c, o: ("the kit carries no HF transmitter, the QMX HF set having left the kit by %s |" % c.cite("L3-OD2"))
      if c.O("L3-OD2") == "qmx-out" else
      ("the HF transmitter, the QMX carried outside the case on a sealed lead across the case wall (%s), is to operate "
       "on the amateur bands under the owner's licence |" % c.cite("L3-OD2")),
      "who it is for, the kit operator: the HF transmitter"),
    P("B04", "BRIEF", 60, "and a rugged tablet (ATAK class) in the lid |", 60, "in the lid |", {"L3-OD2": LID_ITEM},
      lambda c, o: ("and a rugged tablet (ATAK class) carried outside the case, served by the kit's WiFi and the USB-C "
                    "outlet (the lid bracket left the kit by %s) |" % c.cite("L3-OD2"))
      if c.O("L3-OD2") == "tablet-out" else
      ("and an 8 inch rugged tablet (ATAK class) in the lid bracket beside the lid pack (%s) |" % c.cite("L3-OD2")),
      "who it is for, the local end users: the tablet in the lid"),
    P("B05", "BRIEF", 61, "| Remote correspondents | reached over Iridium, cellular, HF (Winlink and Reticulum over the Mercury "
      "modem), VHF APRS, or a second kit over a kit-to-kit WiFi link;", 61, "over a kit-to-kit WiFi link;",
      {"L3-OD2": QMX_OUT},
      lambda c, o: ("| Remote correspondents | reached over Iridium, cellular, VHF APRS, or a second kit over a "
                    "kit-to-kit WiFi link (HF left the kit by %s);" % c.cite("L3-OD2")),
      "who it is for, the remote correspondents: HF"),
    P("B06", "BRIEF", 66, "P pack protection) and a", 69, "since the owner reversed D-08).", STORE,
      lambda c, o: ("P pack protection) and two separately protected 4S lithium-ion packs to be built for the kit rather "
                    "than bought, of Samsung INR18650-35E cells: a base 4S6P across the two base pockets and a %s lid pack "
                    "under its own protection board, each with its own charger path and gauge (%s, which supersedes "
                    "D-06's one 4S3P block of about 145 Wh in the east pocket; the lid pack's count by %s)."
                    % (c.lid(), c.cite("L3-OD1"), c.cite("L3-OD2"))),
      "what the V2 kit is: the pack"),
    P("B07", "BRIEF", 78, "HF (an assembled QRP Labs QMX), ", 78, "HF (an assembled QRP Labs QMX), ", {"L3-OD2": QMX_ANY},
      brief_bearers, "what the V2 kit is, the long-range bearers: HF"),
    P("B08", "BRIEF", 93, "- **Power:** its own pack;", 95, "(REQ-072, \"What it is not, today\").",
      {"L3-OD1": ("approve",), "L3-OD3": OD3_ANY}, brief_power, "what the V2 kit is: power"),
    P("B09", "BRIEF", 125, "the sensor pod and the ground stud (`CASE-MARGINS.md` C2 to C4", 125,
      "(`CASE-MARGINS.md` C2 to C4", {"L3-OD2": ("qmx-outside",)},
      lambda c, o: ("the sensor pod, the ground stud and the sealed lead to the QMX carried outside the case, which "
                    "changes the ruled connector plate (%s) (`CASE-MARGINS.md` C2 to C4" % c.cite("L3-OD2")),
      "what the V2 kit is, the antenna entries: the connector plate"),
    P("B10", "BRIEF", 128, "with the pack and the lid's carried items fitted", 128, "carried items fitted", APPROVE,
      lambda c, o: "with the packs of %s and the lid's carried items fitted" % c.cite("L3-OD1"),
      "what the V2 kit is, carried as one closed case: the pack"),
    P("B11", "BRIEF", 133, "The kit is to be weighed", 134, "and measured at assembly.", {"L3-OD3": OD3_ANY},
      lambda c, o: o + (" The solar array's panels and their folding stand travel outside the case, beside it, and are "
                        "part of the kit's claimed form (%s)." % c.cite("L3-OD3")),
      "what the V2 kit is, carried as one closed case: the solar array"),
    P("B12", "BRIEF", 145, "The second pack has no location found; it is deferred, not withdrawn.", 145,
      "it is deferred, not withdrawn.", {"L3-OD1": ("approve",), "L3-OD2": ("qmx-out", "tablet-out")},
      lambda c, o: "Since the owner's rulings on layer 3, %s." % since_list(c),
      "what it is not today, the deferred functions: the second pack"),
    P("B13", "BRIEF", 152, "full sun: the kit is to be operated shaded, with a lid sun shield or a tarp (D-02e).", 152,
      "a tarp (D-02e).", {"L3-OD4": ("adopt",)},
      lambda c, o: o + (" Not meant to stand open on ground steeper, or under a push greater, than requirement %s states "
                        "(%s)." % (c.deploy_req(), c.cite("L3-OD4"))),
      "what it is not today: the deployment condition"),
    P("B14", "BRIEF", 170, "at +20 C for an aged pack (D-06)", 170, "for an aged pack (D-06)", APPROVE,
      lambda c, o: "at +20 C for aged packs, for both packs together and each pack alone (D-06, kept by %s)" % c.cite("L3-OD1"),
      "what it is not today: the runtime requirement"),
    P("B15", "BRIEF", 171, "- Not able to run through a night on its own pack and solar input.", 179,
      "a night needs that overnight input.",
      {"L3-OD1": ("approve",), "L3-OD2": LID_ANY, "L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")},
      brief_night, "what it is not today: the night on the pack and solar input"),
    P("B16", "BRIEF", 180, "- No transport route is claimed for the pack: its classification, the conditions that apply to it "
      "or an applicable", 181, "requirement REQ-069).", APPROVE,
      lambda c, o: ("- No transport route is claimed for either pack of %s: each pack's classification, the conditions "
                    "that apply to it or an applicable\n  exception are to be established first (`CONOPS.md` section 7a, "
                    "requirement REQ-069)." % c.cite("L3-OD1")),
      "what it is not today: the pack's transport route"),
    P("B17", "BRIEF", 206, "NOT_YET_TESTED, never as a pass (`CONOPS.md` section 2a).", 206, "(`CONOPS.md` section 2a).",
      APPROVE,
      lambda c, o: o + (" Since %s the second pack is in that core, and pack charging and pack safety cover both packs."
                        % c.cite("L3-OD1")),
      "what the first prototype has to show: the core"),
    P("B18", "BRIEF", 207, "The test plan's hot and cold levels beyond the envelope are", 209, "the margin.",
      {"L3-OD5": OD5_ANY}, lambda c, o: o + " The owner answered CFL-017 on them (%s)." % od5_quote(c),
      "what the first prototype has to show: the qualification margins"),
]

# Statements of the design as generated that name the QMX, its rail or its bank port: under qmx-out they state the
# design before the ruling; they stay, read through DEFINITION-STATUS.md's current values (its rule), and the board
# and case changes that follow are engineering work downstream. (line, the text on that line)
QMX_CURRENT = [
    (310, "both E72, the QMX receiving"), (311, "bank 1 (the SDR, the camera, the QMX, the wall port), the 5G module"),
    (312, "the PA and HF rails"), (315, "the HF unit and the two WiFi link cards"), (352, "SDR on, HF receiving"),
    (417, "| QMX HF | the enable of the converter that feeds its DC input"), (441, "the 30 W PA, the QMX, the RockBLOCK 9704"),
    (467, "Bank 2 (the GNSS, both E72, the QMX)"), (497, "bank 1 (the SDR, the camera, the QMX, the wall port) with no host"),
    (522, "bank 1 (the SDR, the camera, the QMX, the wall port) and the monitor"), (568, "the PA and HF software holds"),
    (669, "**the RockBLOCK (bank 1, port 4) with the QMX (bank 2, port 4)**"),
    (671, "the SDR, the wall port, the camera and the QMX; bank 2"), (673, "bank 1 HF, bank 2 Iridium, bank 3 APRS"),
    (953, "| QMX HF | 1 / 12 |"), (977, "| HF (deferred by D-01) |"), (989, "the PA at key-down and HF transmitting"),
    (1095, "the QMX tray 1.5 mm west"), (1098, "the RockBLOCK with the QMX (port 4 of banks 1 and 2)"),
]
for _i, (_ln, _t) in enumerate(QMX_CURRENT):
    PASSAGES.append(P("CQ%02d" % (_i + 1), "CONOPS", _ln, _t, _ln, _t,
                      {"L3-OD2": ("qmx-out", "qmx-outside") if _ln == 1095 else QMX_OUT}, None,
                      "a statement of the design as generated that names the QMX or HF", kind="CURRENT"))


def current_row(c, cur):
    """The row proposed for DEFINITION-STATUS.md's current values, for the CURRENT passages the answers touch."""
    lines = ", ".join(str(p.a) for p in cur)
    if c.O("L3-OD2") == "qmx-out":
        what = ("the QMX HF set and its HF function left the kit by %s; these passages state the design as generated "
                "before it (its rail, its EMCON enable, its bank and port, its load row and its lid tray)" % c.cite("L3-OD2"))
    else:
        what = ("the QMX HF set left the lid for a place outside the case by %s; the lid tray this passage names is the "
                "design before it" % c.cite("L3-OD2"))
    return ("| DC-L3 | `CONOPS.md` lines %s | %s; the board and case changes that follow are engineering work downstream, "
            "not re-issued text |" % (lines, what))


# ------------------------------------------------------------------------------------------------ locating and applying
def baselined(root=E.TOP):
    """{doc: text} of the two baselined files, each held at the sha256/16 l3r2.yaml's baseline_definition names."""
    data = RL.load_data()
    base = data.get("baseline_definition") or {}
    out = {}
    for k, path in DOCS.items():
        fp = os.path.join(root, path)
        b = open(fp, "rb").read()
        if RL.sha16_bytes(b) != str(base.get(path)):
            E.refuse("%s is not the baselined text l3r2.yaml names (%s); the passage map is for that text" % (path, base.get(path)))
        out[k] = b.decode("utf-8")
    return out


def locate(text, p):
    """(offset, end, old): the passage's text, from `start` on line a to the end of `end` on line b, found once."""
    lines = text.split("\n")
    if p.b < p.a or p.b > len(lines): E.refuse("%s: lines %d to %d are outside the file" % (p.pid, p.a, p.b))
    la, lb = lines[p.a - 1], lines[p.b - 1]
    if la.count(p.start) != 1: E.refuse("%s: line %d does not carry %r once" % (p.pid, p.a, p.start[:60]))
    off = sum(len(x) + 1 for x in lines[:p.a - 1]) + la.index(p.start)
    if p.a == p.b and p.start.endswith(p.end):
        end = off + len(p.start)
    else:
        if lb.count(p.end) != 1: E.refuse("%s: line %d does not carry %r once" % (p.pid, p.b, p.end[:60]))
        end = sum(len(x) + 1 for x in lines[:p.b - 1]) + lb.index(p.end) + len(p.end)
    old = text[off:end]
    if end <= off or not old.startswith(p.start) or text.count(old) != 1:
        E.refuse("%s: its text is not found once from line %d to line %d" % (p.pid, p.a, p.b))
    return off, end, old


def excerpt(text, p):
    """The clause of line a that carries the passage's text: from the table cell or clause boundary ('| ' or '; ')
    before it to the one after it."""
    ln = text.split("\n")[p.a - 1]
    i = ln.index(p.start)
    j = i + len(p.start)
    a = max([ln.rfind(sep, 0, i) + len(sep) for sep in ("| ", "; ") if ln.rfind(sep, 0, i) >= 0] or [0])
    ends = [ln.find(sep, j) for sep in (" |", "; ") if ln.find(sep, j) >= 0]
    b = min(ends) if ends else len(ln)
    return ("..." if a else "") + ln[a:b] + ("..." if b < len(ln) else "")


def apply_all(docs, c):
    """{doc: (new_text, [(p, old, new)])} and the CURRENT passages the answers touch; refuses overlaps."""
    out, cur = {}, []
    for k, text in docs.items():
        edits = []
        for p in PASSAGES:
            if p.doc != k or not p.fires(c): continue
            off, end, old = locate(text, p)
            if p.kind == "CURRENT":
                cur.append(p)
                continue
            new = p.new(c, old)
            if new == old: E.refuse("%s: the proposed text equals the baselined text" % p.pid)
            for d in E.DASHES:
                if d in new: E.refuse("%s: the proposed text carries a dash character" % p.pid)
            edits.append((off, end, p, old, new))
        edits.sort(key=lambda e: e[0])
        for x, y in zip(edits, edits[1:]):
            if y[0] < x[1]: E.refuse("%s and %s overlap" % (x[2].pid, y[2].pid))
        t = text
        for off, end, p, old, new in reversed(edits):
            t = t[:off] + new + t[end:]
        out[k] = (t, [(p, old, new) for off, end, p, old, new in edits])
    return out, cur


# ------------------------------------------------------------------------------------------------ the answers' state
def answers(req, data):
    """The Ctx of a decided, coherent set, or a refusal naming why not."""
    try:
        c = Ctx(req, data)
    except RL.RenderError as e:
        E.refuse("the registry's rulings do not read: %s" % e)
    missing = [r for r in ROWS if r not in c.dec]
    if missing:
        E.refuse("rows %s are undecided: the re-issue follows the owner's answers to every row" % and_list(missing))
    why, ok = RL.coherent(c.dec, data)
    if not ok: E.refuse("the answers are not coherent: %s" % "; ".join(why))
    rids = {c.R(r) for r in ROWS}
    bad = [r["id"] for r in req["records"] if r.get("status") == "CONFLICT_OPEN" and r["id"] != "CFL-017"
           and rids & set(r.get("rulings") or [])]
    if bad: E.refuse("open conflicts cite the answers' rulings: %s" % and_list(bad))
    return c


def quote(text):
    return "\n".join("> " + l if l else ">" for l in text.split("\n"))


def render(req_path, c, docs, applied, cur):
    reg_sha = E.sha16(req_path)
    base = RL.load_data()["baseline_definition"]
    d = ["# The definition re-issue on the owner's layer 3 answers: DRAFT", "",
         "**Status: PROPOSED, not approved.** Written by `v2/docs/records/l3r4/reissue.py` from the owner's rulings on "
         "rows L3-OD1 to L3-OD6 of `OWNER-DECISIONS-L3.md` as the requirements registry records them (registry "
         "sha256/16 `%s`). `CONOPS.md` and `PRODUCT-BRIEF.md` are unchanged and stay BASELINED (`%s` and `%s`) until "
         "the owner approves the change record `%s` by a ruling that decides the re-issue; the documents are then "
         "issued again through their layers' review (`handover/DEFINITION-STATUS.md`, the rule). Prototype design: "
         "no V2 board has been fabricated, ordered or powered, and no kit has been field deployed." % (
             reg_sha, base[DOCS["CONOPS"]], base[DOCS["BRIEF"]], RECORD), "",
         "## The answers", "", "| Row | Option | Owner ruling | Ruled on | Title |", "|---|---|---|---|---|"]
    for row in ROWS:
        r = c.rul[c.R(row)]
        d.append("| %s | `%s` | %s | %s | %s |" % (row, c.O(row), r["id"], c.date(row), " ".join(str(r["title"]).split())))
    for k in ("CONOPS", "BRIEF"):
        d += ["", "## `%s`" % os.path.basename(DOCS[k]), ""]
        for p, old, new in applied[k][1]:
            rows = [r for r in p.rows() if p.when == ALL or c.O(r) in p.when[r]]
            d += ["### %s. %s (line %s)" % (p.pid, p.what, p.a if p.a == p.b else "%d to %d" % (p.a, p.b)), "",
                  "Rows and rulings: %s." % "; ".join("%s `%s`, %s" % (r, c.O(r), c.R(r)) for r in rows), "",
                  "**Baselined text:**", "", quote(old), "", "**Proposed text:**", "", quote(new), ""]
    d += ["## Statements of the design as generated (read through `handover/DEFINITION-STATUS.md`)", ""]
    if cur:
        d += ["These passages name the design as generated before the answers; `handover/DEFINITION-STATUS.md`'s rule "
              "keeps them in the baseline and carries their current value on that page. The row proposed for its "
              "current values:", "", "| Row | Where | Current value |", "|---|---|---|", current_row(c, cur), ""]
        for p in cur:
            d.append("- `CONOPS.md` line %d (%s): \"%s\"" % (p.a, p.pid, excerpt(docs["CONOPS"], p)))
        d.append("")
    else:
        d += ["None: the answers change no statement of the design as generated.", ""]
    d += ["## The proposed documents", "",
          "The re-issue applied in memory to the baselined files; nothing is written into them.", "",
          "| Document | Baselined sha256/16 | Proposed sha256/16 | Passages restated |", "|---|---|---|---|"]
    for k in ("CONOPS", "BRIEF"):
        d.append("| `%s` | `%s` | `%s` | %d |" % (DOCS[k], base[DOCS[k]], RL.sha16_bytes(applied[k][0].encode("utf-8")),
                                                 len(applied[k][1])))
    draft = "\n".join(d).rstrip("\n") + "\n"
    rec = change_record(c, applied, cur, RL.sha16_bytes(draft.encode("utf-8")), reg_sha)
    return draft, rec


def change_record(c, applied, cur, draft_sha, reg_sha):
    base = RL.load_data()["baseline_definition"]
    latest = max(c.dec[r][2] for r in ROWS)
    d = ["# Change record: the definition re-issue on the owner's layer 3 answers", "",
         "**Status: PROPOSED for the owner's approval** (closure item L3-C26 of `L3-RECONCILIATION.md`). Written by "
         "`v2/docs/records/l3r4/reissue.py` from the requirements registry (sha256/16 `%s`); the passages, with their "
         "baselined and proposed texts, are `%s` (sha256/16 `%s`)." % (reg_sha, DRAFT, draft_sha), "",
         "## Why the definition reopens", "",
         "`handover/DEFINITION-STATUS.md`, the rule: a definition baseline is reopened only when a requirement, the "
         "scope, the operating concept or another relevant decision changes, and the affected document is issued again "
         "with the change stated in it. The owner's rulings below restate requirements `CONOPS.md` and "
         "`PRODUCT-BRIEF.md` trace to.", "",
         "## The answers and the records each ruling is cited by", "",
         "| Row | Option | Owner ruling | Ruled on | Records citing the ruling (the registry) | Passages it changes |",
         "|---|---|---|---|---|---|"]
    for row in ROWS:
        ps = [p.pid for k in ("CONOPS", "BRIEF") for p, o, n in applied[k][1]
              if p.when == ALL or c.O(row) in p.when.get(row, ())]
        ps = [x for x in ps if not any(q.pid == x and q.when == ALL for q in PASSAGES)]
        d.append("| %s | `%s` | %s | %s | %s | %s |" % (row, c.O(row), c.R(row), c.date(row),
                                                       ", ".join(c.citing(c.R(row))) or "none", ", ".join(ps) or "none"))
    d += ["", "Every answer also changes the head of both documents (C01, C02, B01, B02) and section 7's table of rulings "
          "(C31).", "", "## The passages restated", "",
          "| Passage | Document | Lines | What | Baselined sha256/16 | Proposed sha256/16 |", "|---|---|---|---|---|---|"]
    for k in ("CONOPS", "BRIEF"):
        for p, old, new in applied[k][1]:
            d.append("| %s | `%s` | %s | %s | `%s` | `%s` |" % (
                p.pid, DOCS[k], p.a if p.a == p.b else "%d to %d" % (p.a, p.b), p.what,
                RL.sha16_bytes(old.encode("utf-8")), RL.sha16_bytes(new.encode("utf-8"))))
    d += ["", "## What the re-issue does not restate", ""]
    if cur:
        d.append("Statements of the design as generated that name the QMX or HF (`CONOPS.md` lines %s): they stay, read "
                 "through `handover/DEFINITION-STATUS.md`, whose current values gain the row the draft proposes."
                 % ", ".join(str(p.a) for p in cur))
    d.append("Every other mention of \"the pack\" reads as each of the two packs of %s (the head note of both "
             "documents)." % c.cite("L3-OD1"))
    d += ["", "## The documents", "", "| Document | Baselined sha256/16 | Proposed sha256/16 |", "|---|---|---|"]
    for k in ("CONOPS", "BRIEF"):
        d.append("| `%s` | `%s` | `%s` |" % (DOCS[k], base[DOCS[k]], RL.sha16_bytes(applied[k][0].encode("utf-8"))))
    d += ["", "## Approval", "",
          "The re-issue takes effect when an owner ruling that carries `decides: definition_reissue`, dated %s or later "
          "(on or after every row's ruling), approves this record, and `handover/layer3/l3r2.yaml`'s "
          "`definition_reissue` names it with its sha256/16 and that ruling (`{record, sha16, approved_by}`). Only then "
          "are the proposed texts written into `CONOPS.md` and `PRODUCT-BRIEF.md`, through their layers' review." %
          long_date(latest)]
    return "\n".join(d).rstrip("\n") + "\n"


# ------------------------------------------------------------------------------------------------ the map
def passage_map(docs):
    data = RL.load_data()
    opts = {d["id"]: [o["id"] for o in d["options"]] for d in data["decisions"]}
    m = ["# The passages each owner answer changes (layer 3, rows L3-OD1 to L3-OD6)", "",
         "Generated by `reissue.py --map` from the baselined `CONOPS.md` (`%s`) and `PRODUCT-BRIEF.md` (`%s`) and the "
         "passage list in `reissue.py`; every line and text below is read from those files. DEFINITION passages are "
         "restated by the re-issue; CURRENT passages state the design as generated and stay, read through "
         "`handover/DEFINITION-STATUS.md` (its rule: a circuit correction updates that page, not the baseline)."
         % (data["baseline_definition"][DOCS["CONOPS"]], data["baseline_definition"][DOCS["BRIEF"]]), "",
         "## By row and option", "", "| Row | Option | Passages it changes (document line) |", "|---|---|---|",
         "| every row | %s | %s |" % (ALL, ", ".join("%s (%s %d)" % (p.pid, p.doc, p.a) for p in PASSAGES if p.when == ALL))]
    for row in ROWS:
        for o in opts[row]:
            ps = [p for p in PASSAGES if p.when != ALL and o in p.when.get(row, ())]
            m.append("| %s | `%s` | %s |" % (row, o, ", ".join("%s (%s %d)" % (p.pid, p.doc, p.a) for p in ps) or
                                              "none beyond every answer's"))
    m += ["", "## The passages", ""]
    for p in PASSAGES:
        off, end, old = locate(docs[p.doc], p)
        trig = ALL if p.when == ALL else "; ".join("%s: %s" % (r, ", ".join("`%s`" % x for x in p.when[r])) for r in p.rows())
        m += ["### %s. %s, %s (%s)" % (p.pid, os.path.basename(DOCS[p.doc]),
                                       "line %d" % p.a if p.a == p.b else "lines %d to %d" % (p.a, p.b), p.kind),
              "", "%s. Changed by: %s." % (p.what[0].upper() + p.what[1:], trig), "",
              quote(old if p.kind == "DEFINITION" else excerpt(docs[p.doc], p)), ""]
    return "\n".join(m).rstrip("\n") + "\n"


# ------------------------------------------------------------------------------------------------ main
def guard_out(paths):
    for q in paths:
        if os.path.abspath(q) in {os.path.abspath(os.path.join(E.TOP, x)) for x in DOCS.values()}:
            E.refuse("%s is a baselined file: the re-issue never writes into it" % q)


def main(argv):
    check = "--check" in argv
    opt = lambda k, dflt: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else dflt
    try:
        docs = baselined()
        before = {k: RL.sha16_bytes(open(os.path.join(E.TOP, v), "rb").read()) for k, v in DOCS.items()}
        if "--map" in argv:
            body = passage_map(docs)
            guard_out([MAP])
            if check:
                same = os.path.exists(MAP) and open(MAP, encoding="utf-8").read() == body
                print("reissue: PASSAGE-MAP.md %s" % ("is current" if same else "is OUT OF DATE: run reissue.py --map"))
                return 0 if same else 1
            open(MAP, "w", encoding="utf-8").write(body)
            print("reissue: wrote %s (%d passages)" % (os.path.relpath(MAP, E.TOP), len(PASSAGES)))
            return 0
        reg = opt("--registry", E.REGISTRY)
        req = yaml.safe_load(open(reg, encoding="utf-8"))
        c = answers(req, RL.load_data())
        applied, cur = apply_all(docs, c)
        draft, rec = render(reg, c, docs, applied, cur)
        for t in (draft, rec):
            for d in E.DASHES:
                if d in t: E.refuse("a written text carries a dash character")
        out = opt("--out-dir", L3)
        targets = [os.path.join(out, DRAFT), os.path.join(out, RECORD)]
        guard_out(targets)
        if check:
            same = all(os.path.exists(q) and open(q, encoding="utf-8").read() == t for q, t in zip(targets, (draft, rec)))
            print("reissue: the draft and the change record %s" % ("are current" if same else "are OUT OF DATE"))
            return 0 if same else 1
        os.makedirs(out, exist_ok=True)
        for q, t in zip(targets, (draft, rec)):
            open(q, "w", encoding="utf-8").write(t)
        after = {k: RL.sha16_bytes(open(os.path.join(E.TOP, v), "rb").read()) for k, v in DOCS.items()}
        if after != before: E.refuse("a baselined file changed while the re-issue ran")
        print("reissue: %d passages restated (%d in CONOPS.md, %d in PRODUCT-BRIEF.md), %d statement(s) of the design "
              "as generated read through DEFINITION-STATUS.md; wrote %s and %s" % (
                  len(applied["CONOPS"][1]) + len(applied["BRIEF"][1]), len(applied["CONOPS"][1]),
                  len(applied["BRIEF"][1]), len(cur), DRAFT, RECORD))
        return 0
    except E.Refused as e:
        print("reissue: REFUSED: %s" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
