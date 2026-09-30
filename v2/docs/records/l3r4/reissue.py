#!/usr/bin/env python3
"""The re-issue of the definition documents on the owner's layer 3 answers (L3-C26; MESHSAT-1357, layer 3 round 4,
30 September 2026). PREPARED: it writes nothing until the owner has decided every row of
v2/docs/handover/layer3/OWNER-DECISIONS-L3.md and the prepared scripts have recorded his answers in the registry.

`v2/docs/CONOPS.md` and `v2/docs/PRODUCT-BRIEF.md` are baselined (v2/docs/handover/DEFINITION-STATUS.md): a baseline is
reopened only when a requirement, the scope, the operating concept or another relevant decision changes, and the
affected document is then issued again with the change stated in it. The rows L3-OD1 to L3-OD7 restate requirements
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
  - on a set of answers whose requirements cannot both hold (render_l3r2.coherent, l3r2.yaml's `contradictions`, D-26:
    a target the studied candidate does not meet is valid and is not refused), or while an open conflict other than
    CFL-017 cites one of the answers' rulings;
  - when a baselined file is not the text l3r2.yaml's `baseline_definition` names (sha256/16), or a passage's text is
    not found exactly once where the map says;
  - when an output path resolves (os.path.realpath) to a baselined file, is the same file as one (os.path.samefile, a
    hard link), is a link or has more than one link, checked before anything is written, or a written text carries a
    dash character;
  - to write again once the re-issue is approved (l3r2.yaml's `definition_reissue` filed): an approved record is only
    compared (--check), and then against the sha256/16 `definition_reissue` files and the draft's sha the record names,
    never against a digest recomputed from a registry that goes on changing.
Every proposed text is built from the registry: the rulings' own text, the statements of the records they restated,
and the option each row was answered with. Nothing else is stated. The draft and the change record are bound to the
answers digest, the sha256/16 of the rulings of the answered rows and of every record citing them as the registry holds them, not to
the whole registry, so the ruling that approves the re-issue leaves them current (CHECK-1 of round 4, minor 1).

Passages of two kinds: DEFINITION passages are restated; CURRENT passages state the design as generated (the QMX's
rail, enable, bank and lid tray; the one pack's charge, measurement and protection chain, by designator or in words;
board A's front end at its generated 100 W; the held cell and its limits) and stay, read through DEFINITION-STATUS.md,
whose current values gain the rows the draft proposes (its rule: a circuit correction updates that page, not the
baseline). The PACK and CELL lists are held complete by the vocabulary their own passages carry (VOCAB_RX, EXEMPT).

Usage:
  python3 reissue.py [--registry PATH] [--data PATH] [--docs-root DIR] [--out-dir DIR] [--check]
                                              the draft and the change record (--check: compare); --data is a copy of
                                              l3r2.yaml and --docs-root a directory holding copies of v2/docs/CONOPS.md
                                              and v2/docs/PRODUCT-BRIEF.md at their sha (the tests)
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
ROWS = ("L3-OD7", "L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6")   # row L3-OD7 first (D-27)
# D-27: the passages row L3-OD7 changes are mapped for 72-required (the figure becomes the owner's); its other two answers
# change M1's runtime or its store, whose passages are mapped with the runtime comparison's figures (closure item L3-C56).
RUNTIME_MAPPED = ("72-required",)
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

    def O(self, row): return self.dec[row][0] if row in self.dec else None   # None: not applicable (row L3-OD2 after a reject)
    def R(self, row): return self.dec[row][1]
    def date(self, row): return long_date(self.dec[row][2])
    def cite(self, row): return "owner ruling %s on row %s" % (self.R(row), row)

    def text(self, row):
        """The ruling's decided text, as the registry holds it, without its 'Row ... decided:' head."""
        t = " ".join(str(self.rul[self.R(row)]["ruling"]).split())
        m = re.match(r"^Row %s of \S+ (decided|approved|not approved)[:,] " % re.escape(row), t)
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

    def od1_store(self):
        """(cell, base block) as row L3-OD1's ruling states them, with the ruling's own words on the lid pack's board
        and each pack's charger path and gauge asserted in its text (CHECK-2 of round 4, minor 5)."""
        t = self.text("L3-OD1")
        m = re.findall(r"two separately protected packs of the (.+?), a base pack of (4S\d+P) across the two base pockets", t)
        if len(m) != 1: E.refuse("ruling %s does not name its cell and base block once" % self.R("L3-OD1"))
        for w in ("a lid pack under its own protection board", "each with its own charger path and gauge"):
            if w not in t: E.refuse("ruling %s does not read %r" % (self.R("L3-OD1"), w))
        return m[0]

    def cell_name(self):
        """The held cell's name: row L3-OD1's ruling's where it is approved, else the one REQ-074 names."""
        if self.O("L3-OD1") == "approve": return self.od1_store()[0]
        m = re.findall(r"(Samsung INR18650-35E)", self.stmt("REQ-074"))
        if not m: E.refuse("REQ-074 names no held cell")
        return m[0]

    def cell(self):
        """The cell as the registry holds it: row L3-OD1's ruling's, and under row L3-OD5 `cells` the held cell that row's
        ruling reopens."""
        cell = self.od1_store()[0]
        if self.O("L3-OD5") == "cells":
            return ("the %s as held, the cell of D-06 that %s reopens (CFL-017 %s)"
                    % (cell, self.cite("L3-OD5"), cfl017_state(self)))
        return "the " + cell

    def store(self):
        return ("two separately protected packs of %s, a base %s across the two base pockets and a %s lid pack under its "
                "own protection board, each with its own charger path and gauge" % (self.cell(), self.od1_store()[1], self.lid()))

    def array_phrase(self):
        """The solar array as row L3-OD3's answer states it: its option label in l3r2.yaml ('A 200 W stage and 400 Wp in
        2S2P'), asserted against the ruling's text; for `keep`, the array and window the ruling names."""
        op, t = self.O("L3-OD3"), self.text("L3-OD3")
        if op == "keep":
            wp = re.findall(r"the kit's array is (\d+ Wp)", t)
            win = re.findall(r"REQ-016's (\d+ W) window", t)
            if len(wp) != 1 or len(win) != 1: E.refuse("ruling %s names no single array and window" % self.R("L3-OD3"))
            return "the kit's solar array of %s inside REQ-016's %s window" % (wp[0], win[0])
        row = next(x for x in self.data["decisions"] if x["id"] == "L3-OD3")
        lab = next(o["label"] for o in row["options"] if o["id"] == op)
        m = re.match(r"^A (\d+ W) stage and (\d+ Wp) in (\w+);", lab)
        if not m: E.refuse("row L3-OD3's option %s states no stage, array and arrangement" % op)
        w, wp, arr = m.groups()
        if arr not in t or w not in t: E.refuse("ruling %s does not name %s at %s" % (self.R("L3-OD3"), arr, w))
        return "the kit's solar array, %s in %s into %s %s stage" % (
            wp, arr, "board E's" if "board E's stage" in self.stmt("REQ-016") else "the", w)

    def tablet_size(self):
        """The lid tablet's size as REQ-011 states it after row L3-OD2's answer ('holds an 8 inch rugged tablet')."""
        m = re.findall(r"holds an? (\d+ inch) rugged tablet", self.stmt("REQ-011"))
        if len(m) != 1: E.refuse("REQ-011 names no single tablet size")
        return m[0]

    def stage_w(self):
        m = re.findall(r"at most (\d+ W) into the stage", self.stmt("REQ-016"))
        if len(m) != 1: E.refuse("REQ-016 names no single stage rating")
        return m[0]

    def m1(self):
        """REQ-072's reading as the registry holds it when the re-issue is written."""
        r = self.rec["REQ-072"]
        return {k: str(r.get(k)) for k in ("evidence_result", "evidence_class", "evidence_phase", "release_effect",
                                           "prototype_1")}

    def m1_reads(self):
        m = self.m1()
        return "REQ-072 reads %s (%s, %s phase) when this re-issue is written" % (
            m["evidence_result"], m["evidence_class"], m["evidence_phase"])

    def m1_plain(self, flag=True):
        """The plain sentence D-24 asks for: an option that cannot meet the mission is flagged plainly."""
        m = self.m1()
        s = "Requirement REQ-072%s %s" % (", part of prototype 1's core," if m["prototype_1"] == "core" else "",
                                         self.m1_reads()[len("REQ-072 "):])
        if flag and m["evidence_result"] == "FAIL":
            s += ": the design as it stands does not meet mission M1"
        return s + "; its current reading is kept in the requirements registry and `handover/DEFINITION-STATUS.md`."

    def digest(self):
        """The answers digest: the answered rows' rulings and every record citing them, as the registry holds them."""
        import hashlib
        import json
        rids = [self.R(r) for r in ROWS if r in self.dec]
        body = {"rulings": [self.rul[x] for x in rids],
                "records": [r for r in self.req["records"] if set(rids) & set(r.get("rulings") or [])]}
        return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode("utf-8")).hexdigest()[:16]

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


def answered(c):
    return [r for r in ROWS if r in c.dec]


def rulings_list(c):
    return and_list(sorted({c.R(r) for r in answered(c)}, key=lambda x: int(x.split("-")[1])))


def dates(c):
    ds = sorted({c.dec[r][2] for r in answered(c)})
    return and_list([long_date(d) for d in ds])


# ------------------------------------------------------------------------------------------------ the passages
class P:
    """A passage of a baselined document: from `start` on line `a` to the end of `end` on line `b` (line numbers of
    the baselined text), changed when any row of `when` is answered with one of its options (`when` = ALL: always).
    `new(ctx, old)` gives the proposed text. kind DEFINITION: restated in the re-issue; CURRENT: a statement of the
    design as generated, lines a to b whole, with `start` a text they must carry; it stays and is read through
    DEFINITION-STATUS.md's current values (its rule: a circuit correction updates that page, not the baseline), in the
    row of its `group`."""

    def __init__(self, pid, doc, a, start, b, end, when, new, what, kind="DEFINITION", group=None):
        self.pid, self.doc, self.a, self.start, self.b, self.end = pid, doc, a, start, b, end
        self.when, self.new, self.what, self.kind, self.group = when, new, what, kind, group

    def rows(self):
        return list(ROWS) if self.when == ALL else [r for r in ROWS if r in self.when]

    def fires(self, c):
        if self.pid in APPROVE_ONLY and c.O("L3-OD1") != "approve": return False
        return self.when == ALL or any(c.O(r) in opts for r, opts in self.when.items())


def status_line(layer):
    old = "**Status: layer %d of the foundation baseline (MESHSAT-1357), BASELINED at `a9f212c7`,**" % layer
    return old, (lambda c, o: "**Status: layer %d of the foundation baseline (MESHSAT-1357), RE-ISSUED on the owner's "
                 "rulings on layer 3 (the re-issue note below), pending its layer's review; BASELINED at `a9f212c7`,**" % layer)


def head_note(doc):
    def f(c, old):
        base = "handover/layer3/"
        s = ("**Re-issue on the owner's rulings on layer 3 (%s).** The owner decided rows L3-OD1 to L3-OD7 of `%s"
             "OWNER-DECISIONS-L3.md` (owner rulings %s). They restate requirements this %s traces to, which reopens it "
             "by the rule above: each passage they change is restated in place and names its row and ruling, the "
             "change record `%s%s` lists every passage, and its draft `%s%s` keeps each one's baselined text. The "
             "owner's approval of that record is named in `%sl3r2.yaml` (`definition_reissue`)." % (
                 dates(c), base, rulings_list(c), "document" if doc == "CONOPS" else "brief", base, RECORD, base, DRAFT,
                 base))
        if c.O("L3-OD1") == "approve": s += (" Where a passage this re-issue does not restate states a requirement, an intention or a condition about "
              "\"the pack\", it reads as each of the two packs of %s, as that ruling reads the requirements. Where it "
              "states the circuit as generated for one pack (one charger, one gauge, one pack node, one protection "
              "chain), it states the design before that ruling, whose packs each have their own charger path and gauge; "
              "the current values are kept in `handover/DEFINITION-STATUS.md`." % c.cite("L3-OD1"))
        if doc == "CONOPS" and c.O("L3-OD2") == "qmx-out":
            s += (" Where a passage this re-issue does not restate names the QMX, its HF rail or its bank port, it states "
                  "the design as generated before %s took HF out of the kit; the current values are kept in "
                  "`handover/DEFINITION-STATUS.md`." % c.cite("L3-OD2"))
        if doc == "CONOPS" and c.O("L3-OD2") == "qmx-outside":
            s += (" Where a passage names the QMX's lid tray, it states the design before %s carried the QMX outside the "
                  "case; the current values are kept in `handover/DEFINITION-STATUS.md`." % c.cite("L3-OD2"))
        if doc == "CONOPS" and c.O("L3-OD3") in ("2s2p", "1s4p"):
            s += (" Where a passage names board A's front end at its generated 100 W, it states the design before %s "
                  "restated REQ-016 for a %s stage; the current values are kept in `handover/DEFINITION-STATUS.md`."
                  % (c.cite("L3-OD3"), c.stage_w()))
        if c.O("L3-OD5") == "cells":
            s += (" Where a passage names the held cell, the %s, or its limits, it states the cell of D-06, which %s "
                  "reopens; CFL-017 is %s in the requirements registry." % (c.cell_name(), c.cite("L3-OD5"), cfl017_state(c)))
        return old + "\n\n" + wrap(s)
    return f


def solar_setting(c):
    if c.O("L3-OD3") == "keep":
        return "the kit's solar array on the solar input, inside REQ-016's window (%s)" % c.cite("L3-OD3")
    return ("the kit's solar array on the solar input, its panels and folding stand set out beside the case (%s)"
            % c.cite("L3-OD3"))


def solar_source(c):
    return "%s, its panels and folding stand carried outside the case (%s; REQ-016)" % (c.array_phrase(), c.cite("L3-OD3"))


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
         "pack, whose text the re-issue's draft `handover/layer3/%s` keeps). %s The solar input is REQ-016 as "
         "owner ruling %s %s it: \"%s\" The weather M1 is judged on is the owner's (%s): \"%s\" M1's balance is "
         "requirement REQ-072: \"%s\" %s No figure of it is demonstrated capability, and nothing has been built."
         % (DRAFT, store_sentence(c), c.R("L3-OD3"), op, c.stmt("REQ-016"), c.cite("L3-OD6"),
                          c.text("L3-OD6"), c.stmt("REQ-072"), c.m1_plain()))
    return wrap(s)


def store_sentence(c):
    """The store as row L3-OD1's answer sets it: Option A(i)'s two packs, or D-06's one pack kept with the open store
    problem its feasibility item records (D-26)."""
    if c.O("L3-OD1") == "approve":
        return "The store is %s (%s)." % (c.store(), c.cite("L3-OD1"))
    fea = [r["id"] for r in c.req["records"] if r.get("kind") == "feasibility" and "FI-01" in (r.get("blocker_ids") or [])]
    return ("The store is D-06's one 4S3P pack, which %s keeps; battery and solar stay mandatory, and the store that meets "
            "M1 is an open engineering problem, feasibility item FI-01%s (D-26)." % (
                c.cite("L3-OD1"), (" (%s)" % ", ".join(fea)) if fea else ""))


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


def cells_note(c):
    return (" Row L3-OD5's answer reopens that cell (%s)." % od5_quote(c)) if c.O("L3-OD5") == "cells" else ""


def cfl017_state(c):
    """CFL-017 as the registry holds it after row L3-OD5's answer: resolved, or kept open."""
    st = str((c.rec.get("CFL-017") or {}).get("status"))
    return "resolved" if st == "CONFLICT_RESOLVED" else "kept open" if st == "CONFLICT_OPEN" else "reading %s" % st


def od5_quote(c):
    return "%s, CFL-017 %s: \"%s\"" % (c.cite("L3-OD5"), cfl017_state(c), c.text("L3-OD5"))


def new_rows(c, old):
    rows = []
    for row in answered(c):
        r = c.rul[c.R(row)]
        rows.append("| %s | %s | RULED %s | %s |" % (r["id"], " ".join(str(r["title"]).split()), short_date(c.dec[row][2]),
                                                     c.text(row)))
    words = {6: "six", 7: "seven"}
    return (old[:-2] + "; the owner decided those changes on layer 3, in the %s rulings that follow%s |\n" % (
        words.get(len(rows), str(len(rows))), "" if len(rows) == len(ROWS) else " (row L3-OD2 does not apply after row "
        "L3-OD1's reject)") + "\n".join(rows))


def brief_night(c, old):
    head = ("- Does not meet mission M1 as the design stands." if c.m1()["evidence_result"] == "FAIL" else
            "- Not shown to hold mission M1.")
    s = ("%s %s %s Its solar input is REQ-016 (%s) and the weather it is judged on is "
         "the owner's (%s: \"%s\") (`CONOPS.md` M1); no figure of it is demonstrated capability."
         % (head, c.m1_plain(flag=False), store_sentence(c), c.cite("L3-OD3"), c.cite("L3-OD6"), c.text("L3-OD6")))
    return wrap(s, "", "  ")


def brief_power(c, old):
    if c.O("L3-OD1") != "approve":                   # D-06's one pack kept: only the solar input and the reading move
        new = sub(old, "a solar input; missions", "a solar input from %s; missions" % solar_source(c))
        return sub(new, "(D-06), and on the pack and solar input alone the kit does not run through a night (REQ-072, "
                        "\"What it is not, today\").",
                   "(D-06, kept by %s; the store that meets mission M1 an open problem, feasibility item FI-01), and "
                   "whether the pack and the solar input carry M1 is requirement REQ-072's reading (%s; \"What it is not, "
                   "today\")." % (c.cite("L3-OD1"), c.m1_reads()))
    new = sub(old, "- **Power:** its own pack;", "- **Power:** its own two packs (%s);" % c.cite("L3-OD1"))
    new = sub(new, "a solar input; missions longer than\n  the pack rely",
              "a solar input from %s; missions longer than\n  the packs rely" % solar_source(c))
    new = sub(new, "(D-06), and on the pack and solar input alone the kit does not run through a night (REQ-072, \"What "
                   "it is not, today\").",
              "(D-06, kept by %s), and whether the packs and the solar input carry mission M1 is requirement REQ-072's "
              "reading (%s; \"What it is not, today\")." % (c.cite("L3-OD1"), c.m1_reads()))
    return new


def brief_bearers(c, old):
    if c.O("L3-OD2") == "qmx-out": return "no HF since %s, " % c.cite("L3-OD2")
    return ("HF (an assembled QRP Labs QMX, carried outside the case on a sealed lead across the case wall, %s), "
            % c.cite("L3-OD2"))


QMX_OUT, QMX_ANY, LID_ITEM = ("qmx-out",), ("qmx-out", "qmx-outside"), ("qmx-out", "qmx-outside", "tablet-out")
OD3_ANY, OD5_ANY = ("2s2p", "1s4p", "keep"), ("reading-c", "measure", "cells")
APPROVE = {"L3-OD1": ("approve",)}
LID_ANY = ("qmx-out", "qmx-outside", "tablet-out", "both-kept")
# A passage naming the store names the lid block row L3-OD2 sets and the cell row L3-OD5 `cells` reopens.
STORE = {"L3-OD1": ("approve",), "L3-OD2": LID_ANY, "L3-OD5": ("cells",)}

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
      ("the lid tablet (ATAK class, an %s tablet in the lid bracket beside the lid pack since %s, fed by the USB-C "
       "outlet and the kit's WiFi, 32.50 item 16d; REQ-011)" % (c.tablet_size(), c.cite("L3-OD2"))),
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
      dict(STORE, **{"L3-OD3": OD3_ANY}),
      lambda c, o: sub(sub(o, "the kit's own pack (one 4S3P block, owner ruling D-06),",
                           "the kit's own store, %s (%s, superseding D-06's one 4S3P block)," % (c.store(), c.cite("L3-OD1")))
                       if c.O("L3-OD1") == "approve" else sub(o, "(one 4S3P block, owner ruling D-06),",
                                                              "(one 4S3P block, owner ruling D-06, kept by %s),"
                                                              % c.cite("L3-OD1")),
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
                        "pack at %s (%s).%s" % (c.cite("L3-OD1"), c.date("L3-OD1"), c.text("L3-OD1"), c.lid(),
                                                c.cite("L3-OD2"), cells_note(c))),
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
      dict(STORE, **{"L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")}), energy,
      "section 3, M1's energy: the night, the day's energy, the solar window, the design month and the routes"),
    P("C18", "CONOPS", 215, "Until then REQ-072 reads FAIL and this section is not", 216, "restated.",
      {"L3-OD1": ("approve", "reject")},
      lambda c, o: ("The owner answered it on layer 3 with the rulings of section 7 (rows L3-OD1 to L3-OD7), and this "
                    "section is restated on them. %s" % c.m1_plain()),
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
    P("C27", "CONOPS", 1012, "(3.35 Ah per cell, so 8.04 Ah for the 3P block)", 1012, "for the 3P block)",
      {"L3-OD1": ("approve",), "L3-OD5": ("cells",)},
      lambda c, o: ("(3.35 Ah per cell, so 8.04 Ah for D-06's 3P block, and the same share of each pack of %s%s)"
                    % (c.cite("L3-OD1"), "; the held cell's figure, which %s reopens" % c.cite("L3-OD5")
                       if c.O("L3-OD5") == "cells" else "")),
      "section 6, what aged means in ampere-hours"),
    P("C28", "CONOPS", 1019, "Missions longer than the pack rely on vehicle or solar input: M1 is set at 72 hours (section 3,",
      1024, "session's 72 hours, not asked.", {"L3-OD1": ("approve", "reject"), "L3-OD7": RUNTIME_MAPPED},
      lambda c, o: wrap("Missions longer than the packs rely on vehicle or solar input: M1 is set at 72 hours (section 3, "
                        "required by %s in place of the session's SC-21), and whether the two packs of %s carry it with "
                        "the solar input of %s on the weather basis of %s is REQ-072's reading (section 3): %s."
                        % (c.cite("L3-OD7"), c.cite("L3-OD1"), c.cite("L3-OD3"), c.cite("L3-OD6"), c.m1_reads()))
      if c.O("L3-OD1") == "approve" else
      sub(sub(o, "(section 3,\ntaken by the session under the owner's standing rule in place of the later setting D-06 "
                 "reserved for the owner, whose\nown setting replaces it)",
              "(section 3, required by %s in place of the session's SC-21)" % c.cite("L3-OD7")),
          "with the\nsession's 72 hours, not asked.",
          "with the 72 hours the owner set (%s); %s keeps that pack, and the store that meets M1 is an open engineering "
          "problem, feasibility item FI-01." % (c.cite("L3-OD7"), c.cite("L3-OD1"))),
      "section 6, missions longer than the pack and M1's night"),
    P("C29", "CONOPS", 1040, "operate to specification inside the envelope; survive and recover at the margin |", 1040,
      "survive and recover at the margin |", {"L3-OD5": OD5_ANY},
      lambda c, o: o[:-2] + ". **Decided on %s by %s (CFL-017 %s):** %s |" % (
          c.date("L3-OD5"), c.cite("L3-OD5"), cfl017_state(c), c.text("L3-OD5")),
      "section 7, the D-02a row"),
    P("C30", "CONOPS", 1048, "| D-06 | Pack size and runtime target | RULED 26 Sep |", 1048, "RULED 26 Sep |", APPROVE,
      lambda c, o: ("| D-06 | Pack size and runtime target | RULED 26 Sep, SUPERSEDED %s by %s |"
                    % (short_date(c.dec["L3-OD1"][2]), c.cite("L3-OD1"))),
      "section 7, the D-06 row's status"),
    P("C31", "CONOPS", 1062, "and the smallest justified changes presented for the owner's decision; unmet criteria stay "
      "visible |", 1062, "unmet criteria stay visible |", ALL, new_rows,
      "section 7, the D-20 row and the owner's rulings on layer 3"),
    P("C32", "CONOPS", 1101, "On pack and solar alone the kit does not carry it through a single night on D-06's one pack",
      1101, "not a shorter mission.", APPROVE,
      lambda c, o: ("The store, the solar input and the weather it is judged on are the owner's rulings on layer 3 (%s, "
                    "%s and %s, section 7), which replace the finding this row recorded on D-06's one pack; whether the "
                    "design carries M1 is REQ-072's reading: %s." % (c.R("L3-OD1"), c.R("L3-OD3"), c.R("L3-OD6"),
                                                                   c.m1_reads())),
      "section 7a, M1's mission duration row"),
    P("C33", "CONOPS", 1117, "| M1's solar window and design month (REQ-016 and REQ-072 of the requirements registry; Review "
      "B of layer 3, B4 and B5); **pass 3** | ", 1117, "**pass 3** | ", {"L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")},
      lambda c, o: o + ("**Superseded on %s by owner rulings %s and %s (rows L3-OD3 and L3-OD6, section 7), which now set "
                        "REQ-016 and M1's weather basis; the choice as taken:** " % (
                            long_date(max(c.dec["L3-OD3"][2], c.dec["L3-OD6"][2])), c.R("L3-OD3"), c.R("L3-OD6"))),
      "section 7a, M1's solar window and design month row"),
    # Row L3-OD7 (D-27): the 72 hours become the owner's, in place of the session's SC-21.
    P("C34", "CONOPS", 163, "**The", 165, "whenever he gives one.**", {"L3-OD7": RUNTIME_MAPPED},
      lambda c, o: wrap("**The duration is 72 hours, required by %s in place of the session's SC-21 (section 7a), which "
                        "D-20 had preserved with M1's specified duration.**" % c.cite("L3-OD7")),
      "section 3, M1's duration and who set it"),
    P("C35", "CONOPS", 1101, "Reversed by the owner's own setting |", 1101, "Reversed by the owner's own setting |",
      {"L3-OD7": RUNTIME_MAPPED},
      lambda c, o: "Replaced by the owner's own setting, %s: 72 hours required |" % c.cite("L3-OD7"),
      "section 7a, M1's mission duration row: its reversal"),
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
      ("and an %s rugged tablet (ATAK class) in the lid bracket beside the lid pack (%s) |"
       % (c.tablet_size(), c.cite("L3-OD2"))),
      "who it is for, the local end users: the tablet in the lid"),
    P("B05", "BRIEF", 61, "| Remote correspondents | reached over Iridium, cellular, HF (Winlink and Reticulum over the Mercury "
      "modem), VHF APRS, or a second kit over a kit-to-kit WiFi link;", 61, "over a kit-to-kit WiFi link;",
      {"L3-OD2": QMX_OUT},
      lambda c, o: ("| Remote correspondents | reached over Iridium, cellular, VHF APRS, or a second kit over a "
                    "kit-to-kit WiFi link (HF left the kit by %s);" % c.cite("L3-OD2")),
      "who it is for, the remote correspondents: HF"),
    P("B06", "BRIEF", 66, "P pack protection) and a", 69, "since the owner reversed D-08).", STORE,
      lambda c, o: ("P pack protection) and two separately protected 4S lithium-ion packs to be built for the kit rather "
                    "than bought, of %s: a base %s across the two base pockets and a %s lid pack under its own protection "
                    "board, each with its own charger path and gauge (%s, which supersedes D-06's one 4S3P block of about "
                    "145 Wh in the east pocket; the lid pack's count by %s)."
                    % ("cells of " + c.cell() if c.O("L3-OD5") == "cells" else c.cell() + " cells", c.od1_store()[1], c.lid(),
                       c.cite("L3-OD1"), c.cite("L3-OD2"))),
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
      dict(STORE, **{"L3-OD3": OD3_ANY, "L3-OD6": ("mean-day", "coverage")}),
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
      {"L3-OD5": OD5_ANY},
      lambda c, o: o + " The owner decided row L3-OD5 on them (%s)." % od5_quote(c),
      "what the first prototype has to show: the qualification margins"),
    P("B19", "BRIEF", 309, "for which the session took 72 hours as a planning value", 309,
      "`handover/ENGINEERING-QUESTIONS.md` EQ-13)", {"L3-OD7": RUNTIME_MAPPED},
      lambda c, o: ("for which the owner set 72 hours required (%s), replacing the session's planning value SC-21 "
                    "(`handover/ENGINEERING-QUESTIONS.md` EQ-13)" % c.cite("L3-OD7")),
      "the open items table: L-02, M1's duration"),
]

# Passages that restate the two-pack store: they apply only where row L3-OD1 is approved. Six carry a variant for a
# reject (D-06's one pack kept, FI-01), so a reject restates them too (D-26: a reject leaves an open engineering problem,
# it does not block the other rows).
REJECT_OK = {"C07", "C17", "C18", "C28", "B08", "B15"}
APPROVE_ONLY = {p.pid for p in PASSAGES if p.when != ALL and "L3-OD1" in p.when and p.pid not in REJECT_OK}

# Statements of the design as generated (CURRENT), by group: (first line, last line, a text those lines carry). Each
# stays in the baseline, read through DEFINITION-STATUS.md's current values, and the board, case or cell change that
# follows is engineering work downstream (CHECK-1 of round 4, B1: every statement of the generated circuit an answer
# would change, treated the same way).
#   HF     the QMX, its rail, its EMCON enable, its bank and port, its load row and its lid tray (row L3-OD2 qmx-out;
#          qmx-outside: the lid tray only)
#   PACK   the one pack's charge, measurement and protection chain as generated (row L3-OD1 approve): lines naming the
#          BQ25731 and its shunt R17, its ADCs and bus address, its CHRG_INHIBIT and CHG_INHIBIT, the gauge's host J_SMB
#          and the pack node CELL_F, the gauge's datasheet commands, board P's BQ7720700, JP1 and F2, the pack
#          protection table and K3's pack current
#   SOLAR  board A's front end at its generated 100 W (row L3-OD3 2s2p or 1s4p, a 200 W stage)
#   CELL   the held cell, the Samsung INR18650-35E, and its limits (row L3-OD5 cells, which reopens the cell)
CURRENT = {
    "HF": ([(310, 310, "both E72, the QMX receiving"), (311, 311, "bank 1 (the SDR, the camera, the QMX, the wall port), the 5G module"),
            (312, 312, "the PA and HF rails"), (315, 315, "the HF unit and the two WiFi link cards"), (352, 352, "SDR on, HF receiving"),
            (417, 417, "| QMX HF | the enable of the converter that feeds its DC input"),
            (441, 441, "the 30 W PA, the QMX, the RockBLOCK 9704"), (467, 467, "Bank 2 (the GNSS, both E72, the QMX)"),
            (497, 497, "bank 1 (the SDR, the camera, the QMX, the wall port) with no host"),
            (522, 522, "bank 1 (the SDR, the camera, the QMX, the wall port) and the monitor"),
            (568, 568, "the PA and HF software holds"), (669, 669, "**the RockBLOCK (bank 1, port 4) with the QMX (bank 2, port 4)**"),
            (671, 671, "the SDR, the wall port, the camera and the QMX; bank 2"), (673, 673, "bank 1 HF, bank 2 Iridium, bank 3 APRS"),
            (953, 953, "| QMX HF | 1 / 12 |"), (977, 977, "| HF (deferred by D-01) |"), (989, 989, "the PA at key-down and HF transmitting"),
            (1095, 1095, "the QMX tray 1.5 mm west"), (1098, 1098, "the RockBLOCK with the QMX (port 4 of banks 1 and 2)")],
           "CQ", "a statement of the design as generated that names the QMX or HF"),
    "PACK": ([(306, 306, "BQ7720700"), (311, 311, "BQ25731"), (312, 312, "CHRG_INHIBIT"),
              (313, 313, "regulates the charge into the 4S pack beyond its sense resistor `R17`"), (320, 320, "gen_sch_p.py"),
              (310, 310, "any cell +55 C on the gauge's thermistors"), (322, 322, "the pack's XT60 unplugged"),
              (323, 323, "the pack's arming jumper open"), (335, 337, "the chemical fuse F2"),
              (349, 349, "the gauge's 336 uA"), (379, 379, "the gauge's 20 A for 2 s limit and the 25 A blade bound"),
              (468, 468, "the sensor controller and with it the pack gauge's readings"),
              (529, 529, "the sensor controller's link (the gauge's readings"), (536, 541, "ADCVBAT"),
              (547, 550, "pcb_pack_protection.yaml"), (566, 569, "as the pack gauge reads them"),
              (571, 582, "reads the same four thermistors through the same gauge"), (583, 588, "CHRG_INHIBIT"),
              (590, 594, "the pack gauge's only SMBus host"), (598, 600, "the charger at 0x6B"), (634, 640, "BQ7720700"),
              (646, 648, "the pack's FETs off"), (727, 732, "(OTD, SC-12)"),
              (695, 695, "the gauge's charge window"), (697, 698, "the 10 s average pack current above 9.0 A"),
              (822, 827, "the pack voltage the charger reads"), (830, 837, "SLUUAQ3A 5.4.2 and 13.1.8"),
              (854, 860, "golden image"), (881, 881, "the charger loses its host"), (882, 882, "the charger has no host"),
              (885, 885, "the secure element, the charger, the supervisors' status"),
              (887, 887, "the gauge's SMBus shutdown the sensor controller already sends"),
              (889, 889, "the loads sit on the charger's system node"), (890, 890, "the hottest cell as the gauge reads it"),
              (893, 893, "a permanent pack protection"), (911, 911, "the charger falls to its host-free 256 mA"),
              (914, 914, "the gauge and board P's second level"), (928, 934, "(K3)"),
              (990, 990, "the pack chain's 10 A continuous rating"), (991, 991, "the loads sit on the charger's system node"),
              (1097, 1097, "the pack's voltage and current read from the charger in place of the gauge's readings"),
              (1106, 1106, "the pack voltage the charger reads at 12.8 V"), (1112, 1112, "under the gauge's OTD")],
             "CP", "a statement of the one pack's circuit as generated"),
    "SOLAR": ([(991, 991, "the front end regulates 20 V at up to 5 A (100 W")], "CS",
              "a statement of board A's front end as generated"),
    "CELL": ([(236, 236, "+60 C"), (306, 306, "INR18650-35E"), (321, 321, "Samsung INR18650-35E Ver. 1.1"),
              (338, 339, "the Samsung INR18650-35E at its"), (341, 342, "minimum after 500 cycles (7.9)"),
              (363, 364, "the Samsung INR18650-35E, of"),
              (391, 391, "the Samsung INR18650-35E specification"), (394, 394, "section 3.15: discharge -10 to 60 C"),
              (548, 548, "-10 to 60 C at the cell surface"), (559, 560, "+60 C"), (576, 576, "the cells' +60 C"),
              (662, 662, "+60 C"), (727, 730, "the cells' 60 C"), (739, 739, "+60 C"), (821, 821, "Ver. 1.1 3.9"),
              (1012, 1012, "3.35 Ah per cell"), (1015, 1015, "60 % after 500 cycles (7.9)"),
              (1103, 1103, "80 % of the cell's specification minimum capacity"), (1106, 1106, "the cell's 2.65 V cut-off"),
              (1112, 1112, "+60 C"),
              (158, 158, "their 60 C discharge limit", "BRIEF")],
             "CC", "a statement of the held cell or its limits"),
}
# The vocabulary each group's completeness is held to: VOCAB_RX itself, searched in every line of both documents before
# their appendices (CHECK-3 of round 4, minor 1: the pattern, not only the phrases the group's passages already carry).
# A line it matches is in a passage of the group, in section 7's rulings table (history), or in EXEMPT with its reason
# (CHECK-2 of round 4, minors 1 and 4). The CELL pattern carries the cell sheet's ageing figures (CHECK-3, minor 2).
VOCAB_RX = {"PACK": r"\bthe\s+(?:pack\s+)?(?:charger|gauge)(?:'s)?(?:\s+[a-z0-9]+|[,;.:)])|"
                    r"\bthe\s+pack\s+chain(?:'s)?(?:\s+[a-z0-9]+|[,;.:)])|\bOTD\b|\bXT60\b|\bthe\s+pack's\s+(?:arming\s+jumper|FETs)\b",
            "CELL": r"INR18650-35E|Ver\. 1\.1|Version 1\.0|\bsection 3\.15\b|\b60 C\b|\b3\.35 Ah\b|\b2\.65 V\b|"
                    r"\b(?:\d+ %|minimum)\s+after\s+\d+\s+cycles\b|\bthe cell's specification minimum\b"}
EXEMPT = {
    "PACK": {("CONOPS", 233): "the Transport procedure of mission M2: a pack carried as cargo in its gauge's shutdown, read per "
                              "pack (the phrase runs on to line 234)",
             ("CONOPS", 205): "the gauge holding the charge on its cells' measured temperature, a behaviour each pack's "
                              "gauge has",
             ("CONOPS", 289): "the pack gauge holding charging off in the cold, a condition read per pack",
             ("CONOPS", 307): "the Deploy procedure: a pack in its gauge's shutdown is woken by an input, a condition "
                              "the head note reads per pack",
             ("CONOPS", 308): "the Startup row: a pack in its gauge's shutdown starts only on an input, a condition read "
                              "per pack",
             ("CONOPS", 321): "the Storage procedure, which puts the pack in its gauge's shutdown, read per pack",
             ("CONOPS", 348): "the power state PS-SHUT, the pack in its gauge's shutdown, read per pack",
             ("CONOPS", 561): "the pack's own protection opening its FETs, a behaviour each pack's gauge has",
             ("CONOPS", 817): "graceful shutdown on the gauge's state of charge, an intention the head note reads per "
                              "pack; its fallback through the charger (822 to 827) is PACK",
             ("CONOPS", 819): "the voltage line standing in for the gauge's state of charge until the pack's learning "
                              "cycle, a condition of graceful shutdown read per pack (817)",
             ("CONOPS", 1014): "the pack replaced when its gauge's learned capacity falls below the aged line, a "
                               "condition read per pack",
             ("CONOPS", 1100): "section 7a's storage and transport choice, a procedure read per pack",
             ("CONOPS", 1111): "section 7a's water and gas choice, which puts the pack in its gauge's shutdown, read per "
                               "pack"},
    "CELL": {("BRIEF", 67): "restated by B06, whose store names the cell as the registry holds it (reopened under "
                            "row L3-OD5 `cells`)"},
}
GROUP_WHEN = {"HF": {"L3-OD2": QMX_OUT}, "PACK": {"L3-OD1": ("approve",)}, "SOLAR": {"L3-OD3": ("2s2p", "1s4p")},
              "CELL": {"L3-OD5": ("cells",)}}
for _g, (_items, _pfx, _what) in CURRENT.items():
    for _i, _it in enumerate(_items):
        _a, _b, _t = _it[:3]
        _when = {"L3-OD2": QMX_ANY} if (_g == "HF" and _a == 1095) else GROUP_WHEN[_g]
        PASSAGES.append(P("%s%02d" % (_pfx, _i + 1), _it[3] if len(_it) > 3 else "CONOPS", _a, _t, _b, None, _when, None,
                          _what, kind="CURRENT", group=_g))


def vocabulary(group, docs):
    """The phrases VOCAB_RX[group] finds in the group's own passages (their whole lines, joined, so a phrase broken over
    a line is found), line breaks read as spaces."""
    rx = re.compile(VOCAB_RX[group])
    out = set()
    for p in PASSAGES:
        if p.group == group:
            out |= {" ".join(m.group(0).split()) for m in rx.finditer("\n".join(docs[p.doc].split("\n")[p.a - 1:p.b]))}
    return sorted(out)


def uncovered(group, docs):
    """(doc, line, matches) of every match of VOCAB_RX[group] before the appendices, searched across line breaks
    (CHECK-4 of round 4), none of whose lines is in the group's passages, section 7's rulings table or EXEMPT."""
    import bisect
    rx = re.compile(VOCAB_RX[group])
    out = {}
    for k, text in docs.items():
        body = text[:text.index("\n## Appendix")]
        lines = body.split("\n")
        starts = [0]
        for l in lines: starts.append(starts[-1] + len(l) + 1)
        cov = {n for p in PASSAGES if p.group == group and p.doc == k for n in range(p.a, p.b + 1)}
        for m in rx.finditer(body):
            a = bisect.bisect_right(starts, m.start())
            b = bisect.bisect_right(starts, m.end() - 1)
            ls = range(a, b + 1)
            if any(n in cov or lines[n - 1].startswith("| D-") or (k, n) in EXEMPT[group] for n in ls): continue
            out.setdefault((k, a), []).append(" ".join(m.group(0).split()))
    return [(k, n, sorted(set(v))) for (k, n), v in sorted(out.items())]


def lines_of(ps):
    """'line 991' or 'lines 306, 335 to 337, ...'."""
    one = len(ps) == 1 and ps[0].a == ps[0].b
    return ("line " if one else "lines ") + ", ".join(str(p.a) if p.a == p.b else "%d to %d" % (p.a, p.b) for p in ps)


def current_rows(c, cur):
    """The rows proposed for DEFINITION-STATUS.md's current values: one per group of CURRENT passages the answers
    touch, and M1's reading (REQ-072) in every case."""
    rows = []
    for g in ("HF", "PACK", "SOLAR", "CELL"):
        ps = [p for p in cur if p.group == g]
        if not ps: continue
        if g == "HF" and c.O("L3-OD2") == "qmx-out":
            what = ("the QMX HF set and its HF function left the kit by %s; these passages state the design as generated "
                    "before it (its rail, its EMCON enable, its bank and port, its load row and its lid tray)" % c.cite("L3-OD2"))
        elif g == "HF":
            what = ("the QMX HF set left the lid for a place outside the case by %s; the lid tray this passage names is "
                    "the design before it" % c.cite("L3-OD2"))
        elif g == "PACK":
            what = ("these passages state the circuit as generated for one pack, by designator or in words (the BQ25731 "
                    "charging it through `R17` and reading its voltage and current, the charger's host and its host-free "
                    "fallback, the gauge on `J_SMB` with board E's `U10` its only SMBus host and the pack node `CELL_F`, "
                    "the gauge's four thermistors the hot stop reads, board P's second level, JP1 and F2, and the pack "
                    "chain's ratings); %s makes the store two separately protected packs, each with its own charger path "
                    "and gauge, and whether the pack-current limits of K3, C2 and C3 (9.0 A) apply per pack or in total is "
                    "set downstream" % c.cite("L3-OD1"))
        elif g == "SOLAR":
            what = ("this passage states board A's front end as generated, regulating 20 V at up to 5 A (100 W); %s "
                    "restates REQ-016 for a %s stage" % (c.cite("L3-OD3"), c.stage_w()))
        else:
            what = ("these passages name the held cell of D-06, the %s, and its limits; %s reads \"%s\", and CFL-017 is "
                    "%s in the requirements registry" % (c.cell_name(), c.cite("L3-OD5"), c.text("L3-OD5"), cfl017_state(c)))
        docs_ = [k for k in DOCS if k in {p.doc for p in ps}]
        where = "; ".join("`%s` %s" % (os.path.basename(DOCS[k]), lines_of([p for p in ps if p.doc == k])) for k in docs_)
        rows.append("| DC-L3-%s | %s | %s; the board, case or cell change that follows is engineering "
                    "work downstream, not re-issued text |" % (g, where, what))
    m = c.m1()
    ev = " ".join(str((c.rec["REQ-072"].get("evidence") or [""])[-1]).split()).replace("|", "/")
    rows.append("| DC-L3-M1 | `CONOPS.md` section 3 (M1) and sections 6 and 7a; `PRODUCT-BRIEF.md`, the power bullet and "
                "the M1 bullet | REQ-072 reads %s (%s, %s phase, release effect %s) when the re-issue is written; its "
                "latest evidence entry in the requirements registry: \"%s\" |" % (
                    m["evidence_result"], m["evidence_class"], m["evidence_phase"], m["release_effect"], ev))
    return rows


# ------------------------------------------------------------------------------------------------ locating and applying
def baselined(root=E.TOP, data=None):
    """{doc: text} of the two baselined files, each held at the sha256/16 l3r2.yaml's baseline_definition names."""
    data = data or RL.load_data()
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
    if p.kind == "CURRENT":
        off = sum(len(x) + 1 for x in lines[:p.a - 1])
        old = "\n".join(lines[p.a - 1:p.b])
        if p.start not in old or text.count(old) != 1:
            E.refuse("%s: lines %d to %d do not carry %r, or not once" % (p.pid, p.a, p.b, p.start[:60]))
        return off, off + len(old), old
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
    ln = " ".join(text.split("\n")[p.a - 1:p.b])
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
    """The Ctx of a decided set whose requirements do not contradict, or a refusal naming why not. A target the studied
    candidate does not meet is valid (D-26): it carries its feasibility item and is re-issued as recorded."""
    try:
        c = Ctx(req, data)
    except RL.RenderError as e:
        E.refuse("the registry's rulings do not read: %s" % e)
    missing = [r for r in ROWS if not RL.settled(r, c.dec)]
    if missing:
        E.refuse("rows %s are undecided: the re-issue follows the owner's answers to every row" % and_list(missing))
    why, ok = RL.coherent(c.dec, data)
    if not ok: E.refuse("the answers set requirements that cannot both hold (contradictory): %s" % "; ".join(why))
    if c.O("L3-OD7") not in RUNTIME_MAPPED:
        E.refuse("row L3-OD7 is answered %s (%s): the passages its runtime or its store changes are mapped with the runtime "
                 "comparison's figures (l3r2.yaml runtime_comparison, closure item L3-C56), and the re-issue is written "
                 "after that (D-27)" % (c.O("L3-OD7"), c.R("L3-OD7")))
    rids = {c.R(r) for r in answered(c)}
    bad = [r["id"] for r in req["records"] if r.get("status") == "CONFLICT_OPEN" and r["id"] != "CFL-017"
           and rids & set(r.get("rulings") or [])]
    if bad: E.refuse("open conflicts cite the answers' rulings: %s" % and_list(bad))
    return c


def quote(text):
    return "\n".join("> " + l if l else ">" for l in text.split("\n"))


def render(c, docs, applied, cur, base):
    dg = c.digest()
    d = ["# The definition re-issue on the owner's layer 3 answers: DRAFT", "",
         "**Status: PROPOSED, not approved.** Written by `v2/docs/records/l3r4/reissue.py` from the owner's rulings on "
         "rows L3-OD1 to L3-OD7 of `OWNER-DECISIONS-L3.md` as the requirements registry records them (answers digest "
         "`%s`: the sha256/16 of the answered rows' rulings and of every record citing them). `CONOPS.md` and `PRODUCT-BRIEF.md` "
         "are unchanged and stay BASELINED (`%s` and `%s`) until the owner approves the change record `%s` by a ruling "
         "that decides the re-issue; the documents are then issued again through their layers' review "
         "(`handover/DEFINITION-STATUS.md`, the rule). Prototype design: no V2 board has been fabricated, ordered or "
         "powered, and no kit has been field deployed." % (dg, base[DOCS["CONOPS"]], base[DOCS["BRIEF"]], RECORD), "",
         "## The answers", "", "| Row | Option | Owner ruling | Ruled on | Title |", "|---|---|---|---|---|"]
    for row in ROWS:
        if row not in c.dec:
            d.append("| %s | not applicable | none | none | row L3-OD1 rejected: every option of this row sets a lid pack |" % row)
            continue
        r = c.rul[c.R(row)]
        d.append("| %s | `%s` | %s | %s | %s |" % (row, c.O(row), r["id"], c.date(row), " ".join(str(r["title"]).split())))
    d += ["", "## M1 as the registry reads it", "", c.m1_plain()]
    for k in ("CONOPS", "BRIEF"):
        d += ["", "## `%s`" % os.path.basename(DOCS[k]), ""]
        for p, old, new in applied[k][1]:
            rows = [r for r in p.rows() if r in c.dec and (p.when == ALL or c.O(r) in p.when[r])]
            d += ["### %s. %s (line %s)" % (p.pid, p.what, p.a if p.a == p.b else "%d to %d" % (p.a, p.b)), "",
                  "Rows and rulings: %s." % "; ".join("%s `%s`, %s" % (r, c.O(r), c.R(r)) for r in rows), "",
                  "**Baselined text:**", "", quote(old), "", "**Proposed text:**", "", quote(new), ""]
    d += ["## Rows proposed for `handover/DEFINITION-STATUS.md`'s current values", "",
          "The statements below name the design as generated before the answers; `handover/DEFINITION-STATUS.md`'s rule "
          "keeps them in the baseline and carries their current value on that page, as it carries M1's reading. The "
          "rows proposed for it:", "", "| Row | Where | Current value |", "|---|---|---|"] + current_rows(c, cur) + [""]
    for p in cur:
        d.append("- `%s` %s (%s, %s): \"%s\"" % (os.path.basename(DOCS[p.doc]),
                                                 "line %d" % p.a if p.a == p.b else "lines %d to %d" % (p.a, p.b),
                                                 p.pid, p.group, excerpt(docs[p.doc], p)))
    d += ["", "## The proposed documents", "",
          "The re-issue applied in memory to the baselined files; nothing is written into them.", "",
          "| Document | Baselined sha256/16 | Proposed sha256/16 | Passages restated |", "|---|---|---|---|"]
    for k in ("CONOPS", "BRIEF"):
        d.append("| `%s` | `%s` | `%s` | %d |" % (DOCS[k], base[DOCS[k]], RL.sha16_bytes(applied[k][0].encode("utf-8")),
                                                 len(applied[k][1])))
    draft = "\n".join(d).rstrip("\n") + "\n"
    rec = change_record(c, applied, cur, RL.sha16_bytes(draft.encode("utf-8")), dg, base)
    return draft, rec


def change_record(c, applied, cur, draft_sha, dg, base):
    latest = max(c.dec[r][2] for r in answered(c))
    d = ["# Change record: the definition re-issue on the owner's layer 3 answers", "",
         "**Status: PROPOSED for the owner's approval** (closure item L3-C26 of `L3-RECONCILIATION.md`). Written by "
         "`v2/docs/records/l3r4/reissue.py` from the owner's rulings on the rows and the records citing them (answers digest "
         "`%s`); the passages, with their baselined and proposed texts, are `%s` (sha256/16 `%s`)." % (dg, DRAFT, draft_sha),
         "", "## Why the definition reopens", "",
         "`handover/DEFINITION-STATUS.md`, the rule: a definition baseline is reopened only when a requirement, the "
         "scope, the operating concept or another relevant decision changes, and the affected document is issued again "
         "with the change stated in it. The owner's rulings below restate requirements `CONOPS.md` and "
         "`PRODUCT-BRIEF.md` trace to.", "", "## M1 as the registry reads it", "", c.m1_plain(), "",
         "## The answers and the records each ruling is cited by", "",
         "| Row | Option | Owner ruling | Ruled on | Records citing the ruling (the registry) | Passages it changes |",
         "|---|---|---|---|---|---|"]
    for row in answered(c):
        ps = [p.pid for k in ("CONOPS", "BRIEF") for p, o, n in applied[k][1]
              if p.when != ALL and c.O(row) in p.when.get(row, ())]
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
    names = {"HF": "the QMX or HF", "PACK": "the one pack's charge, measurement and protection chain",
             "SOLAR": "board A's front end at its generated 100 W", "CELL": "the held cell and its limits"}
    for g in ("HF", "PACK", "SOLAR", "CELL"):
        ps = [p for p in cur if p.group == g]
        if ps:
            where = "; ".join("`%s` %s" % (os.path.basename(DOCS[k]), lines_of([p for p in ps if p.doc == k]))
                              for k in DOCS if k in {p.doc for p in ps})
            d += ["Statements of the design as generated that name %s (%s): they stay, read through "
                  "`handover/DEFINITION-STATUS.md`, whose current values gain the row DC-L3-%s the draft proposes."
                  % (names[g], where, g), ""]
    d += ["M1's reading: `handover/DEFINITION-STATUS.md`'s current values gain the row DC-L3-M1, carrying REQ-072's "
          "reading as the draft proposes it.", "",
          "Where a passage the re-issue does not restate states a requirement, an intention or a condition about \"the "
          "pack\", it reads as each of the two packs of %s; where it states the circuit as generated for one pack, it "
          "states the design before that ruling (the head note of both documents)." % c.cite("L3-OD1"),
          "", "## The documents", "", "| Document | Baselined sha256/16 | Proposed sha256/16 |", "|---|---|---|"]
    for k in ("CONOPS", "BRIEF"):
        d.append("| `%s` | `%s` | `%s` |" % (DOCS[k], base[DOCS[k]], RL.sha16_bytes(applied[k][0].encode("utf-8"))))
    d += ["", "## Approval", "",
          "The re-issue takes effect when an owner ruling that carries `decides: definition_reissue`, dated %s or later "
          "(on or after every row's ruling), approves this record, and `handover/layer3/l3r2.yaml`'s "
          "`definition_reissue` names it with its sha256/16 and that ruling (`{record, sha16, approved_by}`). The approving "
          "ruling does not change the answers digest, so this record and its draft stay current; `reissue.py` never "
          "rewrites them once `definition_reissue` is filed. Only then are the proposed texts written into `CONOPS.md` "
          "and `PRODUCT-BRIEF.md`, through their layers' review." % long_date(latest)]
    return "\n".join(d).rstrip("\n") + "\n"


# ------------------------------------------------------------------------------------------------ the map
def passage_map(docs):
    data = RL.load_data()
    opts = {d["id"]: [o["id"] for o in d["options"]] for d in data["decisions"]}
    m = ["# The passages each owner answer changes (layer 3, rows L3-OD1 to L3-OD7)", "",
         "Generated by `reissue.py --map` from the baselined `CONOPS.md` (`%s`) and `PRODUCT-BRIEF.md` (`%s`) and the "
         "passage list in `reissue.py`; every line and text below is read from those files, each passage quoted whole. "
         "DEFINITION passages are restated by the re-issue; CURRENT passages state the design as generated (groups HF, "
         "PACK, SOLAR and CELL) and stay, read through `handover/DEFINITION-STATUS.md` (its rule: a circuit correction "
         "updates that page, not the baseline), which gains one row per group."
         % (data["baseline_definition"][DOCS["CONOPS"]], data["baseline_definition"][DOCS["BRIEF"]]), "",
         "## By row and option", "", "| Row | Option | Passages it changes (document line) |", "|---|---|---|",
         "| every row | %s | %s |" % (ALL, ", ".join("%s (%s %d)" % (p.pid, p.doc, p.a) for p in PASSAGES if p.when == ALL))]
    for row in ROWS:
        for o in opts[row]:
            ps = [p for p in PASSAGES if p.when != ALL and o in p.when.get(row, ())]
            if row == "L3-OD7" and o not in RUNTIME_MAPPED:
                m.append("| %s | `%s` | not mapped yet: its passages are mapped with the runtime comparison's figures "
                         "(closure item L3-C56), and the generator refuses the answer until then (D-27) |" % (row, o))
                continue
            m.append("| %s | `%s` | %s |" % (row, o, ", ".join("%s (%s %d)" % (p.pid, p.doc, p.a) for p in ps) or
                                              "none beyond every answer's"))
    m += ["", "## The passages", ""]
    for p in PASSAGES:
        off, end, old = locate(docs[p.doc], p)
        trig = ALL if p.when == ALL else "; ".join("%s: %s" % (r, ", ".join("`%s`" % x for x in p.when[r])) for r in p.rows())
        m += ["### %s. %s, %s (%s%s)" % (p.pid, os.path.basename(DOCS[p.doc]),
                                         "line %d" % p.a if p.a == p.b else "lines %d to %d" % (p.a, p.b), p.kind,
                                         ", " + p.group if p.group else ""),
              "", "%s. Changed by: %s." % (p.what[0].upper() + p.what[1:], trig), "", quote(old), ""]
    return "\n".join(m).rstrip("\n") + "\n"


# ------------------------------------------------------------------------------------------------ main
def guard_out(paths, root=E.TOP):
    """Refuse, before anything is written, an output that resolves to a baselined file, is the same file as one (a
    hard link), is a link, or is a file with more than one link (CHECK-1 of round 4, minor 3; CHECK-2, minor 3)."""
    base = [os.path.join(root, x) for x in DOCS.values()]
    real = {os.path.realpath(x) for x in base}
    for q in paths:
        if os.path.islink(q): E.refuse("%s is a link: the re-issue writes only plain files" % q)
        if os.path.realpath(q) in real: E.refuse("%s is a baselined file: the re-issue never writes into it" % q)
        if os.path.exists(q):
            if any(os.path.samefile(q, x) for x in base):
                E.refuse("%s is the same file as a baselined file (a hard link): the re-issue never writes into it" % q)
            if os.stat(q).st_nlink > 1: E.refuse("%s has more than one link: the re-issue writes only plain files" % q)


def approved_check(dr, out):
    """After the approval (CHECK-2 of round 4, minor 2): the approved record is the file `definition_reissue` names, at
    the sha256/16 it files, and the draft is at the sha256/16 the record names. Nothing is recomputed from the registry,
    whose records (REQ-072 among them) go on changing after the approval."""
    rec, draft = os.path.join(out, RECORD), os.path.join(out, DRAFT)
    named = dr.get("record") if os.path.isabs(str(dr.get("record"))) else os.path.join(E.TOP, str(dr.get("record")))
    why = []
    if not (os.path.exists(rec) and os.path.exists(named) and os.path.samefile(rec, named)):
        why.append("definition_reissue names %s, not %s" % (dr.get("record"), rec))
    elif RL.sha16_bytes(open(rec, "rb").read()) != str(dr.get("sha16")):
        why.append("%s is not at the sha256/16 definition_reissue files (%s)" % (RECORD, dr.get("sha16")))
    else:
        m = re.findall(r"`%s` \(sha256/16 `([0-9a-f]{16})`\)" % re.escape(DRAFT), open(rec, encoding="utf-8").read())
        if len(m) != 1: why.append("the record names no single draft sha")
        elif not os.path.exists(draft) or RL.sha16_bytes(open(draft, "rb").read()) != m[0]:
            why.append("%s is not at the sha256/16 the record names (%s)" % (DRAFT, m[0]))
    print("reissue: the approved draft and change record %s" % ("are the files definition_reissue names" if not why
                                                               else "DIFFER: " + "; ".join(why)))
    return 0 if not why else 1


def main(argv):
    check = "--check" in argv
    opt = lambda k, dflt: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else dflt
    try:
        data = yaml.safe_load(open(opt("--data", RL.DATA), encoding="utf-8"))
        if check and "--map" not in argv and data.get("definition_reissue"):
            return approved_check(data["definition_reissue"], opt("--out-dir", L3))
        root = opt("--docs-root", E.TOP)
        docs = baselined(root=root, data=data)
        before = {k: RL.sha16_bytes(open(os.path.join(root, v), "rb").read()) for k, v in DOCS.items()}
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
        c = answers(req, data)
        applied, cur = apply_all(docs, c)
        draft, rec = render(c, docs, applied, cur, data["baseline_definition"])
        for t in (draft, rec):
            for d in E.DASHES:
                if d in t: E.refuse("a written text carries a dash character")
        out = opt("--out-dir", L3)
        targets = [os.path.join(out, DRAFT), os.path.join(out, RECORD)]
        guard_out(targets, root)
        if check:
            same = all(os.path.exists(q) and open(q, encoding="utf-8").read() == t for q, t in zip(targets, (draft, rec)))
            print("reissue: the draft and the change record %s" % ("are current" if same else "are OUT OF DATE"))
            return 0 if same else 1
        if data.get("definition_reissue"):
            E.refuse("the re-issue is approved (l3r2.yaml's definition_reissue names %s): an approved record is only "
                     "compared (--check), never rewritten" % data["definition_reissue"].get("record"))
        os.makedirs(out, exist_ok=True)
        for q, t in zip(targets, (draft, rec)):
            open(q, "w", encoding="utf-8").write(t)
        after = {k: RL.sha16_bytes(open(os.path.join(root, v), "rb").read()) for k, v in DOCS.items()}
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
