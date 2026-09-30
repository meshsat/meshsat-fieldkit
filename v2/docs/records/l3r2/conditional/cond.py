#!/usr/bin/env python3
"""Shared machinery of the conditional restatements of layer 3's second issue (L3-R2, MESHSAT-1357, 30 September 2026).

PREPARED, NOT APPLIED. Each script beside this module (od_l3_1.py to od_l3_6.py) is the exact registry change one answer
of the owner to one row of v2/docs/handover/layer3/OWNER-DECISIONS-L3.md makes. It is run only once the owner has
answered that row, with his own words:

  python3 od_l3_N.py --option <option> --words "<the owner's words>" --date YYYY-MM-DD [--check] [--registry PATH]

What every script does, in this order, refusing on the first thing that does not hold:
  1. the row's prerequisites (another row decided, and how) are read from the registry, where an earlier script recorded
     them as an owner ruling carrying `decides: <row>:<option>`;
  2. an owner ruling with the next free D number is added after the last one: `decides`, the owner's `words` exactly as
     given (a dash character, which the tree does not carry, is written as a comma and the ruling says so) and the
     `ruling` text of the option chosen;
  3. the option's edits, each located by record id and by the text it replaces, which is asserted first; every figure
     the new text quotes from a record is asserted in that record's file;
  4. once rows L3-OD1 to L3-OD4 are all decided with L3-OD1 approved, M-02 is closed by the last ruling and REQ-072 stops
     waiting on it;
  5. the result is re-parsed, every changed entry is compared with the list the script declares, and the registry must
     validate (rules_lib.validate_requirements, 0 errors). Nothing is written with --check.

After a script: rules_lib.py requirements, rules_render.py --requirements, and
v2/docs/handover/layer3/render_l3r2.py, which reads the decision from the ruling.
"""
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import l3edit as E  # noqa: E402

DECISIONS_PAGE = "v2/docs/handover/layer3/OWNER-DECISIONS-L3.md"
L3DATA = os.path.join(E.TOP, "v2/docs/handover/layer3/l3r2.yaml")
ROWS = ("L3-OD1", "L3-OD2", "L3-OD3", "L3-OD4", "L3-OD5", "L3-OD6")   # M-02 closes on the first four
# The head of the sentence row L3-OD6 `coverage` appends to REQ-072's statement and acceptance; od_l3_1.py carries it
# over when it restates REQ-072 after that answer (od6_tail).
OD6_MARK = "M1's weather share (row L3-OD6"
DRY_WORDS = "(dry run: the owner's words go here)"


def args(argv, options):
    a = {"check": "--check" in argv, "registry": E.REGISTRY, "option": None, "words": None, "date": None, "extra": {}}
    it = iter(range(len(argv)))
    for i in it:
        k = argv[i]
        if k in ("--option", "--words", "--date", "--registry") and i + 1 < len(argv):
            a[k[2:]] = argv[i + 1]; next(it, None)
        elif k.startswith("--") and k not in ("--check",) and i + 1 < len(argv):
            a["extra"][k[2:]] = argv[i + 1]; next(it, None)
    if a["option"] not in options: E.refuse("--option must be one of %s" % ", ".join(options))
    if not a["words"]:
        if not a["check"]: E.refuse("--words (the owner's own words) is required to apply an answer")
        a["words"] = DRY_WORDS
    if not a["date"]:
        if not a["check"]: E.refuse("--date YYYY-MM-DD (the day the owner answered) is required")
        a["date"] = "2026-10-01"
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", a["date"]): E.refuse("--date is not YYYY-MM-DD")
    return a


def decided(d):
    out = {}
    for r in d.get("owner_rulings") or []:
        s = str(r.get("decides") or "")
        if ":" in s:
            row, opt = s.split(":", 1)
            out[row] = (opt, r["id"])
    return out


def require(d, row, reqs):
    """Refuse unless `row` is undecided and every prerequisite holds: 'L3-ODn:option', 'L3-ODn:opt1|opt2' or 'L3-ODn:*'."""
    dec = decided(d)
    if row in dec: E.refuse("%s is already decided (%s, %s)" % (row, dec[row][0], dec[row][1]))
    for q in reqs:
        r, o = q.split(":")
        if r not in dec: E.refuse("%s needs %s decided first" % (row, r))
        if o != "*" and dec[r][0] not in o.split("|"):
            E.refuse("%s needs %s answered %s; it was answered %s" % (row, r, " or ".join(o.split("|")), dec[r][0]))
    return dec


def l3data():
    import yaml
    return yaml.safe_load(open(L3DATA, encoding="utf-8"))


CHECKED = ("energy_basis", "power_path_check")   # files that count only with an accepted independent check


def basis_state(data, root=None, key="energy_basis"):
    """(True, '') when l3r2.yaml's `key` (energy_basis, or power_path_check of D-24) names its record and its check (and,
    for the energy basis, its outputs), each held in this tree at its sha256/16, and the check's first line reads
    'accepted: yes' (CHECK-2 of L3-R2, B3); else (False, why)."""
    root = root or E.TOP
    v = data.get(key)
    if not v: return False, "l3r2.yaml's %s is not filed yet" % key
    files = [(v.get("record"), v.get("sha16")), (v.get("check"), v.get("check_sha16"))]
    files += [(o.get("path"), o.get("sha16")) for o in (v.get("outputs") or [])]
    if not v.get("check") or (key == "energy_basis" and not v.get("outputs")):
        return False, "l3r2.yaml's %s names no check%s" % (key, " or no outputs" if key == "energy_basis" else "")
    for path, sha in files:
        p = os.path.join(root, str(path))
        if not os.path.isfile(p) or E.sha16(p) != str(sha):
            return False, "l3r2.yaml's %s names %s at %s, which this tree does not hold" % (key, path, sha)
    first = open(os.path.join(root, str(v["check"])), encoding="utf-8").readline().strip()
    if first != "accepted: yes": return False, "%s's check %s reads %r, not 'accepted: yes'" % (key, v["check"], first)
    return True, ""


def held_by(row, data=None):
    d = next((x for x in (data or l3data())["decisions"] if x["id"] == row), {})
    return d.get("held_by", "D-22")


def row_holds(row, data=None):
    return list(next((x for x in (data or l3data())["decisions"] if x["id"] == row), {}).get("held_until") or [])


def hold(a, row, needs=None):
    """The owner's review of 30 September 2026 (D-22) holds rows L3-OD1, L3-OD2 and L3-OD4, and his instruction on the
    six-row table (D-23) row L3-OD6, until the corrected, independently checked energy comparison arrives; an option
    that moves an item out of the lid also waits on the relocation facts. A held answer is never written into the tree's
    own registry while l3r2.yaml names no basis with an accepted check (basis_state); a copy (--registry, the tests and
    dryrun.py) is not held, so the prepared change is exercised before it is needed."""
    if a["check"] or os.path.abspath(a["registry"]) != os.path.abspath(E.REGISTRY): return
    data = l3data()
    for k in (row_holds(row, data) if needs is None else needs):
        if k in CHECKED:
            ok, why = basis_state(data, key=k)
            if not ok: E.refuse("%s is held (%s): %s" % (row, held_by(row, data), why))
            continue
        v = data.get(k)
        if not v: E.refuse("%s is held (%s): l3r2.yaml's %s is not filed yet" % (row, held_by(row, data), k))
        rp = os.path.join(E.TOP, str(v.get("record")))
        if not os.path.isfile(rp) or E.sha16(rp) != str(v.get("sha16")):
            E.refuse("%s is held: l3r2.yaml's %s names %s at %s, which this tree does not hold" % (row, k, v.get("record"), v.get("sha16")))


# Row L3-OD6's weather basis against row L3-OD2's lid (CHECK-2 of L3-R2, B2). The table's rows are l3r2.yaml's
# (quantified.rows, filled by fill_l3r2_from_basis.py), or a fixture given with --table on a copy of the registry.
LID = {"qmx-out": "qmx-out", "qmx-outside": "qmx-out", "tablet-out": "tablet-out", "both-kept": "both-kept"}
FIGS = ("usable_wh", "lid_block", "cells", "nominal_wh", "mass_kg", "volume_cyl_l", "volume_box_l", "x_wh", "x_cells", "fits",
        "evidence")


def od6_rows(a):
    import yaml
    tp = a["extra"].get("table")
    if tp:
        if os.path.abspath(a["registry"]) == os.path.abspath(E.REGISTRY):
            E.refuse("--table is a fixture for a copy of the registry; the tree's registry reads l3r2.yaml")
        data = yaml.safe_load(open(tp, encoding="utf-8"))
        return (data["rows"] if "rows" in data else
                next(x for x in data["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]), True
    return next(x for x in l3data()["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"], False


def od6_row(rows, option, share, build):
    """The filled table row for an answer; refused when the table has no such row or its figures are HELD."""
    want = "mean-day" if option == "mean-day" else str(share)
    t = next((r for r in rows if (r.get("option") == option) and str(r.get("build")) == build and
              ("mean-day" if r.get("option") == "mean-day" else str(r.get("share"))) == want), None)
    if t is None: E.refuse("row L3-OD6's table has no %s %s row in the %s build" % (option, share or "", build))
    miss = [k for k in FIGS if t.get(k) is None]
    if miss: E.refuse("the target %s is HELD: its %s are not filled from the checked energy basis" % (t.get("id"), ", ".join(miss)))
    if not isinstance(t["fits"], list) or any(x not in ("tablet-out", "qmx-out", "both-kept") for x in t["fits"]):
        E.refuse("the target %s: fits %r is not a list of lids" % (t["id"], t["fits"]))
    return t


def od6_verify(t):
    """The row's figures against the filed basis's output, read again by exact keys (basis_reader.py); refused on any
    difference. Only for l3r2.yaml's own table (a fixture is not a basis)."""
    sys.path.insert(0, os.path.dirname(HERE))
    import basis_reader as BR
    data = l3data()
    ok, why = basis_state(data)
    if not ok: E.refuse("row L3-OD6's figures cannot be verified: %s" % why)
    out = next((o for o in data["energy_basis"]["outputs"] if str(o["path"]).endswith("weather_basis.out")), None)
    if out is None: E.refuse("l3r2.yaml's energy_basis names no weather_basis.out")
    try:
        got = BR.sizing(open(os.path.join(E.TOP, out["path"]), encoding="utf-8").read())
    except BR.BasisError as e:
        E.refuse("the filed weather_basis.out does not read: %s" % e)
    key = ("mean-day" if t["option"] == "mean-day" else str(t["share"]), t["build"])
    for k, v in got[key].items():
        if t.get(k) != v: E.refuse("row L3-OD6's %s %s reads %r; the filed basis prints %r" % (t["id"], k, t.get(k), v))


def evidence_path(a, path):
    """On the tree's registry an evidence file must be one the filed, accepted basis names (its record or an output);
    a copy of the registry (the tests and dryrun.py) may name a fixture. Returns the file's text."""
    evp = path if os.path.isabs(path) else os.path.join(E.TOP, path)
    if os.path.abspath(a["registry"]) == os.path.abspath(E.REGISTRY) and not a["check"]:
        data = l3data()
        ok, why = basis_state(data)
        if not ok: E.refuse("the evidence cannot be the filed basis: %s" % why)
        v = data["energy_basis"]
        named = {str(v["record"])} | {str(o["path"]) for o in v["outputs"]}
        if os.path.relpath(os.path.abspath(evp), E.TOP) not in named:
            E.refuse("%s is not the filed energy basis or one of its outputs (%s)" % (path, ", ".join(sorted(named))))
    if not os.path.isfile(evp): E.refuse("the evidence %s is not in this tree" % path)
    return open(evp, encoding="utf-8").read()


def exact_phrase(text, phrase):
    """True when `phrase` is a whole line, a whole table cell or a whole double-quoted phrase of `text` (whitespace
    folded): a figure or a band binds exactly, never as a substring of a longer one (CHECK-2 of L3-R2, minor 6)."""
    want = " ".join(phrase.split())
    for line in text.split("\n"):
        s = " ".join(line.split())
        if s == want or s.strip("-* ") == want: return True
        if "|" in s and want in [" ".join(c.split()) for c in s.split("|")]: return True
    return want in [" ".join(q.split()) for q in re.findall(r'"([^"]+)"', " ".join(text.split()))]


def exact_token(text, value, unit):
    """True when '<value> <unit>' stands in `text` with no digit or point before it and a word end after it."""
    return re.search(r"(?<![\d.])%s %s\b" % (re.escape(str(value)), re.escape(unit)), " ".join(text.split())) is not None


def od6_answer(d):
    """(option, share, build, ruling id) of row L3-OD6's answer in the registry, or None."""
    for r in d.get("owner_rulings") or []:
        if str(r.get("decides") or "").startswith("L3-OD6:"):
            return str(r["decides"]).split(":", 1)[1], r.get("weather_share"), r.get("weather_build"), r["id"]
    return None


def weather_conflict(raw, rid_basis, lid, t, n_text, extra_rulings=()):
    """An open conflict: REQ-072's weather basis (its answer's store) is not carried by the lid, or by any lid."""
    cid = E.next_id(E.parse(raw), "CFL", ("records",))
    carriers = ", ".join(t["fits"]) or "no lid of the table"
    st = ("REQ-072's weather basis (%s: %s in the %s build) is not carried by %s: on the checked energy basis it asks "
          "%s Wh usable, a lid block of %s, %s cells, %s Wh nominal, %s kg and %s / %s litres of cells (%s), which %s "
          "carries." % (rid_basis, n_text, t["build"], ("the lid of row L3-OD2 (%s)" % lid) if lid else "any lid of the case",
                        t["usable_wh"], t["lid_block"], t["cells"], t["nominal_wh"], t["mass_kg"], t["volume_cyl_l"],
                        t["volume_box_l"], t["evidence"], carriers))
    acc = ("One of: an owner ruling that changes the weather basis, the lid's items, the store, or M1's duration or "
           "operating state, after which REQ-072 is judged again; until then REQ-072 reads FAIL and layer 3 is not complete.")
    for x in (st, acc): E.screen(x, cid)
    ev = str(t["evidence"]).split(" ")[0]
    src = ['"owner ruling %s"' % rid_basis] + list('"owner ruling %s"' % x for x in extra_rulings) + \
          (['"%s"' % ev] if not os.path.isabs(ev) and os.path.isfile(os.path.join(E.TOP, ev)) else [])   # a fixture is named in the text only
    entry = ("  - id: %s\n    kind: conflict\n    parent: NEED-05\n    statement: >-\n%s    acceptance: >-\n%s"
             "    allocated_to: [kit, procedure]\n    verification_method: [MANUAL_REVIEW]\n    verification_phase: SCHEMATIC\n"
             "    prototype_1: core\n    prototype_1_basis: NEED_DEFAULT\n    satisfied_by:\n      rules: []\n      decisions: []\n"
             "    rule_coverage: NONE\n    rulings: [%s]\n    status: CONFLICT_OPEN\n    evidence_result: FAIL\n"
             "    evidence_phase: SCHEMATIC\n    release_effect: BLOCKER\n    source: [%s]\n    source_check: VERIFIED\n"
             % (cid, E.fold(st, 6), E.fold(acc, 6), ", ".join([rid_basis] + list(extra_rulings) + ["D-20", "D-21", "D-22", "D-23"]),
                ", ".join(src)))
    return E.insert_after_entry(raw, "REQ-072", entry, "records"), cid


def words_clean(w):
    out = w
    for dch in E.DASHES: out = out.replace(dch, ",")
    return " ".join(out.split()), out != w


RULING = """  - id: {rid}
    authority: OWNER
    ruled_on: "{date}"
    title: "{title}"
    decides: "{row}:{option}"
{extra}    words: >-
{words}    ruling: >-
{ruling}    source: ["owner ruling {rid}", "{page}"]
"""


def add_ruling(raw, d, row, option, title, ruling, words, date, extra=None):
    rid = E.next_id(d, "D", ("owner_rulings",))
    if any(r["id"] == rid for r in d["owner_rulings"]): E.refuse("%s is already an owner ruling" % rid)
    w, changed = words_clean(words)
    text = ruling + (" (The owner's words are recorded with each dash character written as a comma.)" if changed else "")
    for t in (title, text): E.screen(t, "the ruling of %s" % row)
    last = d["owner_rulings"][-1]["id"]
    ext = "".join("    %s: %s\n" % (k, "null" if v is None else v) for k, v in (extra or {}).items())
    entry = RULING.format(rid=rid, date=date, title=title, row=row, option=option, extra=ext, words=E.fold(w, 6),
                          ruling=E.fold(text, 6), page=DECISIONS_PAGE)
    return E.insert_after_entry(raw, last, entry, "owner_rulings"), rid


def swap_ruling(raw, d, old, new):
    """Every record citing `old` in `rulings` cites `new` in its place (a reversed ruling may not be cited)."""
    touched = []
    for r in d["records"]:
        if old in (r.get("rulings") or []):
            def f(b, old=old, new=new):
                items = E.flow_items(b, "rulings")
                return E.set_flow(b, "rulings", [new if x == old else x for x in items])
            raw = E.replace_entry(raw, r["id"], f)
            touched.append(r["id"])
    return raw, touched


def add_ruling_ref(block, rid):
    items = E.flow_items(block, "rulings")
    if items is None: return set_line(block, "rulings", "[%s]" % rid, after="rule_coverage")
    if rid in items: return block
    return E.set_flow(block, "rulings", items + [rid])


def add_choice_ref(block, cid):
    items = E.flow_items(block, "choices") or []
    if cid in items: return block
    return E.set_flow(block, "choices", items + [cid])


def replace_in_field(block, field, old, new):
    t = E.field_text(block, field)
    if t is None or t.count(old) != 1: E.refuse("field %s does not carry %r once" % (field, old[:70]))
    return E.set_folded(block, field, t.replace(old, new))


def restate(raw, rid, stamp, statement=None, acceptance=None):
    """New statement and/or acceptance, the old text kept in `history` with the ruling that changed it."""
    def f(b):
        old = []
        if statement is not None:
            old.append("statement '%s'" % E.field_text(b, "statement"))
            E.screen(statement, "%s's statement" % rid)
            b = E.set_folded(b, "statement", statement)
        if acceptance is not None:
            old.append("acceptance '%s'" % E.field_text(b, "acceptance"))
            E.screen(acceptance, "%s's acceptance" % rid)
            b = E.set_folded(b, "acceptance", acceptance)
        return E.append_folded(b, "history", "Restated by %s: it read %s." % (stamp, "; ".join(old)), after="source_check")
    return E.replace_entry(raw, rid, f)


def ordinal(n):
    return "%d%s" % (n, "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def od6_tail(text):
    """The sentence row L3-OD6 `coverage` appended (from OD6_MARK to the end), with a leading space; '' if none."""
    t = " ".join(str(text or "").split())
    i = t.find(OD6_MARK)
    return "" if i < 0 else " " + t[i:]


def drop_field(block, field):
    lines, a, b = E._field_lines(block, field)
    if a is None: return block
    return "\n".join(lines[:a] + lines[b:])


def set_line(block, field, value, after):
    lines, a, b = E._field_lines(block, field)
    if a is not None: return "\n".join(lines[:a] + ["    %s: %s" % (field, value)] + lines[b:])
    _, a2, b2 = E._field_lines(block, after)
    if a2 is None: E.refuse("anchor %s absent" % after)
    return "\n".join(lines[:b2] + ["    %s: %s" % (field, value)] + lines[b2:])


def superseded_entry(sid, rec, by, ruling):
    return ("  - id: %s\n    kind: superseded\n    parent: %s\n    statement: >-\n%s    acceptance: \"n/a\"\n"
            "    allocated_to: [%s]\n    verification_method: [MANUAL_REVIEW]\n    verification_phase: SCHEMATIC\n"
            "    satisfied_by:\n      rules: []\n      decisions: []\n    rule_coverage: NONE\n    status: SUPERSEDED\n"
            "    superseded_by: >-\n%s    evidence_result: NOT_APPLICABLE\n    release_effect: NONE\n"
            "    source: [\"owner ruling %s\"]\n    source_check: VERIFIED\n"
            % (sid, rec["parent"], E.fold(rec["statement"], 6), ", ".join(rec["allocated_to"]), E.fold(by, 6), ruling))


def close_m02_if_done(raw, rid_last):
    d = E.parse(raw)
    dec = decided(d)
    if not all(r in dec for r in ROWS[:4]) or dec["L3-OD1"][0] != "approve": return raw, False
    if not any(x["id"] == "M-02" for x in d["open_items"]): return raw, False
    it = next(x for x in d["open_items"] if x["id"] == "M-02")
    raw, _ = E.remove_entry(raw, "M-02")
    closed = ("  - id: M-02\n    closed_by: %s\n    closing_evidence: >-\n%s    title: >-\n%s"
              % (rid_last, E.fold("Rows L3-OD1 to L3-OD4 of " + DECISIONS_PAGE + " are decided by the owner (" +
                                  ", ".join("%s %s by %s" % (r, dec[r][0], dec[r][1]) for r in ROWS[:4]) +
                                  "); REQ-072 keeps reading FAIL until the design is drawn, reviewed and tested.", 6),
                 E.fold(it["title"], 6)))
    raw = E.insert_at_section_end(raw, "closed_items", closed)
    def f(b):
        w = E.flow_items(b, "waits_on")
        return E.set_flow(b, "waits_on", [x for x in w if x != "M-02"])
    raw = E.replace_entry(raw, "REQ-072", f)
    return raw, True


def finish(name, a, old, new, expected):
    """Compare, validate, print, write. `expected` is a set of (section, id, kind); a changed M-02 closure is added."""
    before, after = E.parse(old), E.parse(new)
    got = set(E.diff_entries(before, after))
    m02 = {("open_items", "M-02", "removed"), ("closed_items", "M-02", "added")}
    if m02 <= got: expected = set(expected) | m02 | {("records", "REQ-072", "changed")}
    if got != set(expected):
        E.refuse("the entries changed are not the declared list: extra %s, missing %s"
                 % (sorted(got - set(expected)), sorted(set(expected) - got)))
    errs, warns = E.validate(new)
    if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    for sec, eid, kind in sorted(got):
        print("%-14s %-8s %s %s" % (sec, eid, kind, ",".join(E.changed_fields(before, after, sec, eid)) if kind == "changed" else ""))
    print("%s: option %s, %d entries, validator 0 errors, %d warnings%s" % (name, a["option"], len(got), len(warns),
                                                                          " (check only, nothing written)" if a["check"] else ""))
    if not a["check"]:
        E.commit_text(a["registry"], old, new)
        print("%s: written %s" % (name, os.path.relpath(a["registry"], E.TOP)))


def run(name, fn, options, argv):
    try:
        a = args(argv, options)
        old = open(a["registry"], encoding="utf-8").read()
        new, expected = fn(a, old, E.parse(old))
        finish(name, a, old, new, expected)
    except E.Refused as e:
        print("%s: REFUSED: %s" % (name, e))
        return 2
    return 0
