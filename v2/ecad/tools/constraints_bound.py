#!/usr/bin/env python3
"""A layout constraint sheet is bound to the inputs it was computed from, and says so where it is used
(MESHSAT-1357, 27 September 2026; the independent review of handover H2, finding 3 A).

WHY IT EXISTS. At H2 board A's sheet (`v2/docs/layout-constraints/A.md`) gave VIN_RAW as 12.31 A and 11.92 mm on one
outer face while the committed intent file declared 14.10 A. The sheet had gone stale in silence: it was written
against one candidate, the boards moved, and nothing compared the page with its inputs. The review's words: "The
supplied old widths must not become current layout requirements." Commit ecfe5414 re-bound the seven sheets by hand,
and set 6 then moved every board's netlist again with nobody re-running the calculation. A re-binding by hand is a
repair; this is the check that makes the next one necessary to notice.

WHAT IT READS, per board, and none of it is prose:
  * the sheet's `bound` block, the fenced block that closes its opening paragraph (the form is stated in
    v2/docs/layout-constraints/README.md, "The bound block"): one line per input with its path, its sha256/16 and the
    commit it last changed in, the model, and the stack with its copper;
  * the board's section of `calc/rail_widths.out`, which opens with the same block as the tool printed it;
  * the committed files themselves, hashed;
  * `calc/rail_widths.py`, RUN in memory on those files (its `rows`, `markdown` and `render`), and
    `stackup_write.STACKS`, the table the copper thicknesses come from;
  * the sheet's power tables in its section 2, split on the pipe character with an escaped pipe kept as text.
JSON is read with json, YAML with PyYAML, a board file's nets with a small S-expression reader; a netlist is only
hashed. No regular expression is used anywhere in this file, and no sentence decides anything.

WHAT FAILS, each naming the sheet, the input and both values:
  1. a sheet that declares no input (no `bound` block, or a block with no input line);
  2. a declared input whose sha256/16 is not the committed file's, or whose path is not the file the calculation
     reads, or that is not the declared phase's artefact; an input the calculation reads that the sheet does not
     declare; a declared commit that is not the one git names for the file (asked only where git can answer);
  3. a model or a stack that is not the calculation's: the function, decision 35, the rise, the hole plating, the
     stack's name and its outer and inner copper; and a copper thickness of the calculation's own table that is not
     `stackup_write.STACKS`'s for that stack;
  4. a power table that is not what rail_widths.py prints for the board NOW, cell by cell: the rail, the voltage,
     the currents, the governing current, the three widths and the barrel counts; a row missing, a row added, a row
     out of order; a power table in section 2 that the tool does not print;
  5. the board's section of rail_widths.out differing from a fresh run, and (the set) the file differing byte for
     byte;
  6. a typed list that has outlived its subject: a pack-path root the intent file no longer declares, a maker's
     figure for a rail the intent file no longer declares or has caught up with, a net of board E5's table that its
     board file does not carry;
  7. a row whose note still opens with the mark --emit leaves on a row that moved or is new: the numbers are the
     tool's and nobody has yet said, from the intent file's own text, what moved them.

THE ONE COLUMN IT DOES NOT COMPARE is a sheet table's last column when it is headed `note`: that column is the
sheet's own words about a row (what moved, and why, from the intent file's text). A number in a note is a quotation
with its source named beside it, and this check cannot vouch for it; README.md says so at the point of use.

WHERE IT WRITES. Nowhere, by default: it prints. Given `--out-dir DIR`, or run by the pipeline (VERDICT_DIR in the
environment, which is how retake_schematic_phase.py and gate_sweep.sh run every writer), it writes one verdict per
board, `constraints_bound_<letter>`, and with no `--board` the set's `constraints_bound` beside them.

Usage: constraints_bound.py [--board <letter>] [--root <repository>] [--out-dir <dir>] [--no-git] [--json]
       constraints_bound.py --emit <letter> [--sheet] [--root <repository>]
  --emit prints the `bound` block and the section 2 tables as the sheet should carry them now, with the notes the
  sheet already holds kept by rail and every row that moved or is new marked for its explanation. With --sheet it
  prints the WHOLE sheet so re-bound (its block's hashes, commits and `read` line, its model and stack, its tables;
  every other line as it stands), for whoever re-binds to put in the sheet's place. It writes nothing, and the sheet
  it prints fails the check until each marked row is explained.
Exit: 0 PASS, 1 FAIL, 3 INCONCLUSIVE (the calculation could not be run here), 2 usage.
"""
import os, sys, json, hashlib, datetime, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v
import phase_artefacts as _pa
import stackup_write as _sw
import track_current as _tc
import via_current as _vc

ECAD = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(ECAD))          # the repository: v2/ecad/tools -> the root
TOOL = "constraints_bound"
SHEET_DIR = ("v2", "docs", "layout-constraints")
SHEETS = {"a": "A.md", "b": "B.md", "c": "C.md", "d": "D.md", "e": "E.md", "e5": "E5.md", "p": "P.md"}
INPUT_ROLES = ("netlist", "intent", "board_file", "chain")
OTHER_KEYS = ("sheet", "board", "read", "current", "older", "model", "stack")
FENCE = "```"
OPEN = FENCE + "bound"
NOTE = "note"
POWER_SECTION = "2."
# What --emit writes in the note of a row that moved or is new. A note that still opens with one of them is a row
# nobody has explained, and the check fails on it: a re-binding by machine cannot pass for a re-reading.
MARK_MOVED = "**MOVED, explain it**"
MARK_NEW = "**NEW ROW, explain it**"


# ------------------------------------------------------------------------------------------------------------------
# Reading: a Markdown table, a `bound` block, a sheet's sections, the output file's sections, a board file's nets
# ------------------------------------------------------------------------------------------------------------------
def norm(cell):
    """A cell as compared: its words, single-spaced."""
    return " ".join(str(cell).split())


def split_row(line):
    """The cells of one Markdown table row, or None when the line is not one. Split on the pipe character; a pipe
    written `\\|` is part of its cell."""
    s = line.strip()
    if not s.startswith("|"): return None
    cells, cur, i = [], [], 1
    while i < len(s):
        ch = s[i]
        if ch == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|"); i += 2; continue
        if ch == "|":
            cells.append(norm("".join(cur))); cur = []; i += 1; continue
        cur.append(ch); i += 1
    if norm("".join(cur)): cells.append(norm("".join(cur)))          # a row that does not close with a pipe
    return cells


def is_rule(cells):
    """The row under a table's header: every cell made of hyphens and colons alone."""
    return bool(cells) and all(c and all(ch in "-:" for ch in c) and "-" in c for c in cells)


def tables(lines, first=0):
    """[{head, rows, line}] of the Markdown tables in `lines` (a header, its rule and the rows under it)."""
    out, i = [], 0
    while i < len(lines):
        head = split_row(lines[i])
        rule = split_row(lines[i + 1]) if i + 1 < len(lines) else None
        if head is None or rule is None or not is_rule(rule):
            i += 1; continue
        t = {"head": head, "rows": [], "line": first + i + 1}
        i += 2
        while i < len(lines):
            r = split_row(lines[i])
            if r is None: break
            t["rows"].append(r); i += 1
        out.append(t)
    return out


def bound_blocks(lines):
    """[{line, body: [(n, text)]}] of the fenced `bound` blocks in `lines`."""
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip() != OPEN:
            i += 1; continue
        b = {"line": i + 1, "body": [], "closed": False}
        i += 1
        while i < len(lines):
            if lines[i].strip() == FENCE:
                b["closed"] = True; i += 1; break
            if lines[i].strip(): b["body"].append((i + 1, lines[i]))
            i += 1
        out.append(b)
    return out


def _pairs(tokens, keys):
    """{key: [values]} from a run of tokens in which each known key is followed by its values."""
    out, cur = {}, None
    for t in tokens:
        if t in keys and t not in out:
            cur = t; out[cur] = []
        elif cur is not None:
            out[cur].append(t)
        else:
            out.setdefault("", []).append(t)
    return out


def _number(text):
    try: return float(text)
    except (TypeError, ValueError): return None


def read_bound(block):
    """A `bound` block as data: {board, sheet, read, inputs: {role: {path, sha16, changed, line}}, model, stack,
    errors}. A line that does not read in the fixed form is an error, never skipped."""
    d = {"board": None, "sheet": None, "read": None, "inputs": {}, "model": None, "stack": None, "errors": []}
    if not block.get("closed"):
        d["errors"].append("the block opened at line %d is never closed" % block["line"])
    for n, raw in block["body"]:
        tok = raw.split()
        key, rest = tok[0], tok[1:]
        if key in INPUT_ROLES:
            p = _pairs(rest[1:], ("sha256/16", "changed"))
            sha = (p.get("sha256/16") or [None])[0]
            if not rest or sha is None or p.get(""):
                d["errors"].append("line %d: an input reads `%s <path> sha256/16 <16 hex> [changed <commit>]`, and "
                                   "this one is %r" % (n, key, norm(raw)))
                continue
            if key in d["inputs"]:
                d["errors"].append("line %d: %s is declared twice" % (n, key)); continue
            d["inputs"][key] = {"path": rest[0], "sha16": sha, "changed": (p.get("changed") or [None])[0], "line": n}
        elif key == "model":
            p = _pairs(rest[1:], ("decision", "rise", "plating"))
            m = {"function": rest[0] if rest else None,
                 "decision": _number((p.get("decision") or [None])[0]),
                 "rise_k": _number((p.get("rise") or [None])[0]),
                 "plating_um": _number((p.get("plating") or [None])[0])}
            if None in m.values():
                d["errors"].append("line %d: the model reads `model <function> decision <n> rise <K> K plating <um> "
                                   "um`, and this one is %r" % (n, norm(raw)))
            d["model"] = m
        elif key == "stack":
            p = _pairs(rest[1:], ("outer", "inner"))
            inner = (p.get("inner") or [None])[0]
            s = {"name": rest[0] if rest else None, "outer": _number((p.get("outer") or [None])[0]),
                 "inner": None if inner == "none" else _number(inner)}
            if s["name"] is None or s["outer"] is None or inner is None or (inner != "none" and s["inner"] is None):
                d["errors"].append("line %d: the stack reads `stack <name> outer <mm> mm inner <mm> mm` (or `inner "
                                   "none`), and this one is %r" % (n, norm(raw)))
            d["stack"] = s
        elif key == "board":
            d["board"] = rest[0].lower() if rest else None
        elif key == "sheet":
            d["sheet"] = rest[0] if rest else None
        elif key == "read":
            p = _pairs(rest, ("at",))
            d["read"] = {"date": (p.get("") or [None])[0], "commit": (p.get("at") or [None])[0]}
        elif key in OTHER_KEYS:
            pass                                          # `current` and `older`: the sheet's own words, for a reader
        else:
            d["errors"].append("line %d: %r is no key of a bound block (%s)" % (n, key, ", ".join(OTHER_KEYS + INPUT_ROLES)))
    return d


def sections(lines):
    """[(heading words, first line number, body lines)] of a sheet's level-two sections; the opening, everything
    above the first of them, is the entry whose heading is ()."""
    out, cur, start, body = [], (), 1, []
    for n, l in enumerate(lines, 1):
        w = l.split()
        if w and w[0] == "##":
            out.append((cur, start, body)); cur, start, body = tuple(w[1:]), n, []
        else:
            body.append(l)
    out.append((cur, start, body))
    return out


def out_sections(text):
    """{letter: the text of that board's section} of rail_widths.out, and the letters in the file's order."""
    secs, order, cur = {}, [], None
    for l in text.splitlines(True):
        w = l.split()
        if len(w) == 3 and w[0] == "###" and w[1] == "Board":
            cur = w[2].lower(); order.append(cur); secs[cur] = ""
        if cur is not None: secs[cur] += l
    return secs, order


def sexp_nets(text):
    """The net names a KiCad board file declares, from its `(net <number> "<name>")` forms, read as S-expressions:
    parentheses, quoted strings with their escapes, and atoms."""
    names, stack, i, n = set(), [], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            stack.append([]); i += 1
        elif ch == ")":
            done = stack.pop() if stack else []
            if len(done) == 3 and done[0] == ("atom", "net") and done[2][0] == "string": names.add(done[2][1])
            i += 1
        elif ch == '"':
            j, buf = i + 1, []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1]); j += 2
                else:
                    buf.append(text[j]); j += 1
            if stack and len(stack[-1]) < 3: stack[-1].append(("string", "".join(buf)))
            i = j + 1
        elif ch.isspace():
            i += 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in '()"': j += 1
            if stack and len(stack[-1]) < 3: stack[-1].append(("atom", text[i:j]))
            i = j
    return names


# ------------------------------------------------------------------------------------------------------------------
# The calculation, the files, git
# ------------------------------------------------------------------------------------------------------------------
def calc_path(root=None):
    return os.path.join(root or ROOT, *(SHEET_DIR + ("calc", "rail_widths.py")))


def load_calc(path=None):
    """rail_widths.py as a module. It is the CODE of the tree this tool sits in; the files it reads are `root`'s."""
    p = path or calc_path()
    sp = importlib.util.spec_from_file_location("meshsat_rail_widths", p)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


def sha16(path):
    try:
        with open(path, "rb") as f: return hashlib.sha256(f.read()).hexdigest()[:16]
    except OSError:
        return None


def _git(root, *args):
    try:
        r = subprocess.run(["git", "-C", root] + list(args), capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def git_state(root):
    """None where git cannot answer for `root` (no git, an extraction with no history, a directory that is not a
    checkout's own root), else {shallow}."""
    rc, top = _git(root, "rev-parse", "--show-toplevel")
    if rc != 0 or not top or os.path.realpath(top) != os.path.realpath(root): return None
    rc, sh = _git(root, "rev-parse", "--is-shallow-repository")
    return {"shallow": sh == "true"}


def stack_copper(name):
    """(outer, inner) copper thickness of a named stack of stackup_write.STACKS, inner None on a two-layer stack;
    None when the table has no such stack."""
    st = _sw.STACKS.get(name)
    if not st: return None
    cu = {it[0]: it[1] for it in st if len(it) == 2}
    return cu.get("F.Cu"), cu.get("In1.Cu")


def _same(a, b, tol=5e-7):
    if a is None or b is None: return a is None and b is None
    return abs(float(a) - float(b)) <= tol


# ------------------------------------------------------------------------------------------------------------------
# The judgement
# ------------------------------------------------------------------------------------------------------------------
class Checks:
    def __init__(self, sheet):
        self.sheet, self.n, self.fails, self.notes = sheet, 0, [], []

    def ok(self, good, fail):
        """One check: counted, and its sentence kept when it did not hold."""
        self.n += 1
        if not good: self.fails.append("%s: %s" % (self.sheet, fail))
        return bool(good)

    def note(self, text):
        self.notes.append("%s: %s" % (self.sheet, text))


def compare_table(c, want, got, what):
    """One of the tool's tables against the sheet's (or the output file's): header, order and every cell."""
    head = list(got["head"])
    if head and head[-1] == NOTE and len(head) == len(want["head"]) + 1: head = head[:-1]
    if not c.ok(head == want["head"],
                "%s, line %d: the header is not the tool's. It reads %r and rail_widths.py prints %r"
                % (what, got["line"], got["head"], want["head"])):
        return
    rails_want = [r[0] for r in want["rows"]]
    rails_got = [r[0] if r else "" for r in got["rows"]]
    missing = [r for r in rails_want if r not in rails_got]
    extra = [r for r in rails_got if r not in rails_want]
    c.ok(not missing, "%s: the tool prints %d row(s) the sheet does not carry: %s"
         % (what, len(missing), ", ".join(missing)))
    c.ok(not extra, "%s: the sheet carries %d row(s) the tool does not print: %s" % (what, len(extra), ", ".join(extra)))
    c.ok(len(set(rails_got)) == len(rails_got), "%s: a rail stands in two rows: %s"
         % (what, ", ".join(sorted({r for r in rails_got if rails_got.count(r) > 1}))))
    if not missing and not extra:
        c.ok(rails_got == rails_want, "%s: the rows are not in the tool's order (the intent file's own)" % what)
    by = {r[0]: r for r in got["rows"] if r}
    noted = len(got["head"]) == len(want["head"]) + 1
    for w in want["rows"]:
        g = by.get(w[0])
        if g is None: continue
        if noted and len(g) > len(want["head"]):
            c.ok(not g[len(want["head"])].startswith((MARK_MOVED, MARK_NEW)),
                 "%s, rail %s: its note still opens with the re-binding's mark, so the row moved or is new and nobody "
                 "has explained it from the intent file's own text" % (what, w[0]))
        for k, col in enumerate(want["head"]):
            if k == 0: continue
            have = g[k] if k < len(g) else ""
            c.ok(have == w[k], "%s, rail %s, column `%s`: the sheet says %r and rail_widths.py prints %r on the "
                 "committed input" % (what, w[0], col, have, w[k]))


def judge(letter, root=None, calc=None, git=None):
    """One board's sheet against its inputs. Returns {letter, sheet, checked, fails, notes, inputs, missing_input}."""
    root = os.path.abspath(root or ROOT)
    RW = calc or load_calc()
    name = SHEETS.get(letter) or (letter.upper() + ".md")
    rel_sheet = "/".join(SHEET_DIR + (name,))
    c = Checks(rel_sheet)
    res = {"letter": letter, "sheet": rel_sheet, "inputs": {"board": letter}, "missing_input": None}

    def done():
        res.update(checked=c.n, fails=c.fails, notes=c.notes)
        return res

    def record(key, rel, content=None):
        r = _pa.record(os.path.join(root, rel), content=content)
        if r: res["inputs"][key] = r

    # ---- the calculation, run now on the committed files
    fresh, why = None, None
    try:
        fresh = RW.rows(letter, root)
        fresh_md = RW.markdown(fresh)
    except SystemExit as e:
        why = "rail_widths.py refused: %s" % e
    except (OSError, ValueError, KeyError) as e:
        why = "rail_widths.py could not read its input: %s: %s" % (type(e).__name__, e)
    ran = _pa.record(getattr(RW, "__file__", None) or calc_path(), content=False)      # the calculation that was RUN
    if ran: res["inputs"]["rail_widths"] = ran
    record("rail_widths_out", "/".join(SHEET_DIR + ("calc", "rail_widths.out")), content=False)
    record("sheet", rel_sheet, content=False)
    if fresh:
        for role, rel, _sha in fresh["inputs"]: record(role, rel)

    # ---- 1. the sheet and its declaration
    try:
        with open(os.path.join(root, rel_sheet), encoding="utf-8") as f: lines = f.read().splitlines()
    except OSError:
        c.ok(False, "there is no such sheet in this tree")
        res["missing_input"] = "the sheet %s" % rel_sheet
        return done()
    secs = sections(lines)
    opening = secs[0][2]
    blocks = bound_blocks(opening)
    anywhere = bound_blocks(lines)
    if not c.ok(blocks, "the sheet declares no input: its opening paragraph carries no `bound` block%s, so nothing "
                        "says which netlist and intent file its numbers were computed from"
                        % (" (one stands below the first section, at line %d, where it binds nothing)" % anywhere[0]["line"]
                           if anywhere else "")):
        return done()
    c.ok(len(anywhere) == 1, "the sheet carries %d `bound` blocks (lines %s); a sheet is bound once"
         % (len(anywhere), ", ".join(str(b["line"]) for b in anywhere)))
    said = read_bound(blocks[0])
    for e in said["errors"]: c.ok(False, "the bound block, %s" % e)
    if not c.ok(said["inputs"], "the sheet declares no input: its `bound` block names no netlist, intent file, board "
                                "file or chain"):
        return done()
    c.ok(said["board"] == letter, "the bound block says board %r and this is board %s's sheet" % (said["board"], letter))
    c.ok(said["sheet"] in (None, name[:-3]), "the bound block says sheet %r and the file is %s" % (said["sheet"], name))

    # ---- 2. every declared input against the committed file, and against what the calculation reads
    gs = git_state(root) if git is None else (git_state(root) if git else None)
    if gs is None: c.note("git does not answer for this tree, so no declared commit was compared with its history")
    elif gs["shallow"]: c.note("this clone is shallow, so no declared commit was compared with its history")
    reads = {role: (rel, sha) for role, rel, sha in (fresh["inputs"] if fresh else [])}
    for role, d in sorted(said["inputs"].items()):
        now = sha16(os.path.join(root, d["path"]))
        c.ok(now is not None, "the %s it declares, %s, is not in this tree" % (role, d["path"]))
        # every input the sheet declares is recorded, read by the calculation or not (board A's sheet declares the
        # committed layout its older sections were read on): a reading is then stale when that file moves too
        if role not in res["inputs"]: record(role, d["path"])
        if now is not None:
            c.ok(now == d["sha16"], "the %s %s: the sheet was computed on sha256/16 %s and the committed file is %s"
                 % (role, d["path"], d["sha16"], now))
        if role in reads:
            c.ok(d["path"] == reads[role][0], "the %s: the sheet declares %s and rail_widths.py reads %s"
                 % (role, d["path"], reads[role][0]))
        if not c.ok(d["changed"], "the %s %s names no commit it last changed in" % (role, d["path"])): continue
        if gs is None or gs["shallow"]: continue
        rc, full = _git(root, "rev-parse", "--verify", "--quiet", d["changed"] + "^{commit}")
        if not c.ok(rc == 0 and full, "the %s: the sheet names commit %s, which this repository does not hold"
                    % (role, d["changed"])):
            continue
        rc, last = _git(root, "log", "-1", "--format=%H", "--", d["path"])
        if rc == 0 and last:
            c.ok(last == full, "the %s %s: the sheet says it last changed in %s and git names %s"
                 % (role, d["path"], d["changed"], last[:8]))
        rc, dirty = _git(root, "status", "--porcelain", "--", d["path"])
        c.ok(rc == 0 and not dirty, "the %s %s is not its commit's in this checkout (%s): a sheet is bound to a "
             "committed input" % (role, d["path"], (dirty or "git did not answer")[:2].strip()))
    for role, (rel, sha) in sorted(reads.items()):
        c.ok(role in said["inputs"], "rail_widths.py reads the %s %s (sha256/16 %s) and the sheet does not declare it"
             % (role, rel, sha))
    ecad = os.path.join(root, "v2", "ecad")
    declared = {"netlist": _pa.netlist(letter, ecad), "intent": _pa.intent(letter, ecad),
                "board_file": _pa.board_file(letter, ecad)}
    for role, (rel, _sha) in sorted(reads.items()):
        p = declared.get(role)
        if p is None: continue
        c.ok(os.path.relpath(p, root) == os.path.normpath(rel), "the %s rail_widths.py reads, %s, is not the declared "
             "phase's (%s)" % (role, rel, os.path.relpath(p, root)))
    if said["read"] is not None:
        try: datetime.date.fromisoformat(str(said["read"]["date"])); good = True
        except ValueError: good = False
        c.ok(good and said["read"]["commit"], "the bound block's `read` line reads `read <yyyy-mm-dd> at <commit>`")
        if good and said["read"]["commit"] and gs is not None and not gs["shallow"]:
            rc, full = _git(root, "rev-parse", "--verify", "--quiet", said["read"]["commit"] + "^{commit}")
            c.ok(rc == 0 and full, "the sheet says it was read at commit %s, which this repository does not hold"
                 % said["read"]["commit"])
    else:
        c.ok(False, "the bound block carries no `read <yyyy-mm-dd> at <commit>` line, so it does not say when and "
                    "on which candidate the sheet was bound")

    if fresh is None:
        # A sheet that has already failed on what COULD be compared has been judged, and reads FAIL (its declared
        # intent file is gone: the hash check above said so). Only where nothing failed is this the whole answer, and
        # then the tool has not judged: INCONCLUSIVE, with the reason as the input that was absent.
        decided = bool(c.fails)
        c.ok(False, "the calculation could not be run on this tree, so no table was compared (%s)" % why)
        res["missing_input"] = None if decided else why
        return done()

    # ---- 3. the model and the stack
    m, s = said["model"], said["stack"]
    if c.ok(m is not None, "the bound block states no model"):
        for k, label in (("function", "function"), ("decision", "decision"), ("rise_k", "temperature rise, K"),
                         ("plating_um", "hole plating, um")):
            same = (m[k] == RW.MODEL[k]) if k == "function" else _same(m[k], RW.MODEL[k])
            c.ok(same, "the model's %s: the sheet says %s and rail_widths.py computes with %s" % (label, m[k], RW.MODEL[k]))
    c.ok(_same(RW.MODEL["plating_um"], _vc.PLATING_UM), "rail_widths.py states %s um of hole plating and "
         "via_current.py rates a barrel at %s" % (RW.MODEL["plating_um"], _vc.PLATING_UM))
    c.ok(callable(getattr(_tc, RW.MODEL["function"].split(".")[-1], None)),
         "rail_widths.py names %s, which track_current.py does not define" % RW.MODEL["function"])
    if c.ok(s is not None, "the bound block states no stack"):
        c.ok(s["name"] == fresh["stack"], "the stack: the sheet says %s and rail_widths.py's table for board %s says %s"
             % (s["name"], letter.upper(), fresh["stack"]))
        c.ok(_same(s["outer"], fresh["cu_out"]), "the outer copper: the sheet says %s mm and rail_widths.py's table "
             "for board %s says %s mm" % (s["outer"], letter.upper(), fresh["cu_out"]))
        c.ok(_same(s["inner"], fresh["cu_in"]), "the inner copper: the sheet says %s and rail_widths.py's table for "
             "board %s says %s" % (s["inner"], letter.upper(), fresh["cu_in"]))
    cu = stack_copper(fresh["stack"])
    if c.ok(cu is not None, "rail_widths.py builds board %s on %s, which stackup_write.STACKS does not record"
            % (letter.upper(), fresh["stack"])):
        c.ok(_same(cu[0], fresh["cu_out"]) and _same(cu[1], fresh["cu_in"]),
             "rail_widths.py computes board %s at %s mm outer and %s inner, and stackup_write.STACKS records %s at %s "
             "and %s" % (letter.upper(), fresh["cu_out"], fresh["cu_in"], fresh["stack"], cu[0], cu[1]))

    # ---- 6. the typed lists against their subjects (before the tables, which they decide)
    if fresh["kind"] == "intent":
        try:
            with open(os.path.join(root, reads["intent"][0]), encoding="utf-8") as f:
                rails = (json.load(f) or {}).get("rails") or {}
        except (OSError, ValueError):
            rails = {}
        gone = [r for r in fresh["pack_roots"] if r not in rails]
        c.ok(not gone, "rail_widths.py names %s as pack path and the intent file declares no such rail, so nothing "
             "is judged at the pack's service current in its place" % ", ".join(gone))
        for r in fresh["sized"]:
            if not c.ok(r["declared"], "rail_widths.py sizes %s at a maker's figure and the intent file declares no "
                        "such rail" % r["net"]):
                continue
            c.ok(r["amps"] > r["typ"], "rail_widths.py sizes %s at the maker's %.3f A and the intent file now "
                 "declares %.2f A typical: the entry has outlived its finding" % (r["net"], r["amps"], r["typ"]))
    else:
        try:
            with open(os.path.join(root, reads["board_file"][0]), encoding="utf-8", errors="replace") as f:
                nets = sexp_nets(f.read())
        except OSError:
            nets = set()
        gone = [r["net"] for r in fresh["rows"] if r["net"] not in nets]
        c.ok(not gone, "rail_widths.py's table for board %s names %s, which its board file does not carry"
             % (letter.upper(), ", ".join(gone)))

    # ---- 5. the board's section of the output file
    want_tabs = tables(fresh_md.splitlines())
    want_sec = "### Board %s\n\n%s\n\n" % (letter.upper(), fresh_md)
    try:
        with open(os.path.join(root, *(SHEET_DIR + ("calc", "rail_widths.out"))), encoding="utf-8") as f:
            out_text = f.read()
    except OSError:
        out_text = None
    if c.ok(out_text is not None, "calc/rail_widths.out is not in this tree"):
        have, _order = out_sections(out_text)
        if c.ok(letter in have, "calc/rail_widths.out has no section for board %s" % letter.upper()):
            hb = bound_blocks(have[letter].splitlines())
            head = read_bound(hb[0]) if hb else {"inputs": {}}
            for role, (rel, sha) in sorted(reads.items()):
                h = head["inputs"].get(role)
                c.ok(h is not None and h["path"] == rel and h["sha16"] == sha,
                     "calc/rail_widths.out, board %s: its table was computed on the %s %s and the committed file is %s "
                     "sha256/16 %s" % (letter.upper(), role, ("%s sha256/16 %s" % (h["path"], h["sha16"])) if h else
                                       "(none named)", rel, sha))
            if have[letter] != want_sec:
                a, b = have[letter].splitlines(), want_sec.splitlines()
                k = next((i for i in range(max(len(a), len(b))) if i >= len(a) or i >= len(b) or a[i] != b[i]), 0)
                c.ok(False, "calc/rail_widths.out, board %s, is not what rail_widths.py prints now; the first line that "
                     "differs is line %d of the section: the file has %r and a fresh run %r"
                     % (letter.upper(), k + 1, (a[k] if k < len(a) else "(nothing)")[:150],
                        (b[k] if k < len(b) else "(nothing)")[:150]))
            else:
                c.ok(True, "")

    # ---- 4. the sheet's power tables
    power = [x for x in secs if x[0] and x[0][0] == POWER_SECTION]
    if not c.ok(len(power) == 1, "the sheet has %d sections numbered 2, and the power table stands in one" % len(power)):
        return done()
    got_tabs = [t for t in tables(power[0][2], power[0][1]) if t["head"] and t["head"][0] == want_tabs[0]["head"][0]]
    kinds = {tuple(t["head"]): t for t in want_tabs}
    used = set()
    for t in got_tabs:
        head = tuple(t["head"][:-1]) if t["head"][-1] == NOTE else tuple(t["head"])
        if not c.ok(head in kinds and head not in used,
                    "section 2, line %d: a power table that rail_widths.py does not print for this board (its header "
                    "is %r); a table of widths in a sheet is the tool's or it is not there" % (t["line"], t["head"])):
            continue
        used.add(head)
        compare_table(c, kinds[head], t, "section 2's table `%s`" % head[1])
    for head, t in kinds.items():
        c.ok(head in used, "section 2 does not carry the table rail_widths.py prints for this board (%d row(s), "
             "columns %s)" % (len(t["rows"]), ", ".join(head)))
    return done()


def judge_set(root=None, letters=None, calc=None):
    """The output file as a whole against a fresh run, byte for byte."""
    root = os.path.abspath(root or ROOT)
    RW = calc or load_calc()
    rel = "/".join(SHEET_DIR + ("calc", "rail_widths.out"))
    c = Checks(rel)
    try:
        want = RW.render(letters, root)
    except SystemExit as e:
        c.ok(False, "rail_widths.py refused: %s" % e); want = None
    except (OSError, ValueError, KeyError) as e:
        c.ok(False, "rail_widths.py could not read its input: %s: %s" % (type(e).__name__, e)); want = None
    try:
        with open(os.path.join(root, rel), "rb") as f: have = f.read()
    except OSError:
        have = None
    c.ok(have is not None, "the file is not in this tree")
    if want is not None and have is not None:
        c.ok(have == want.encode("utf-8"), "the file (%d bytes, sha256/16 %s) is not what rail_widths.py prints now "
             "(%d bytes, sha256/16 %s): re-run `rail_widths.py --markdown` and commit its output"
             % (len(have), hashlib.sha256(have).hexdigest()[:16], len(want.encode("utf-8")),
                hashlib.sha256(want.encode("utf-8")).hexdigest()[:16]))
    return {"checked": c.n, "fails": c.fails, "notes": c.notes}


# ------------------------------------------------------------------------------------------------------------------
# --emit: what a sheet should carry now. It prints; the sheet is edited by whoever explains the rows that moved.
# ------------------------------------------------------------------------------------------------------------------
def emit_block(letter, root=None, calc=None, today=None):
    """The `bound` block a sheet should carry now, as lines. A commit git cannot name is written UNKNOWN, which the
    check refuses wherever git answers: it is a blank to fill, never a value."""
    root = os.path.abspath(root or ROOT)
    RW = calc or load_calc()
    t = RW.rows(letter, root)
    name = SHEETS.get(letter) or (letter.upper() + ".md")
    gs = git_state(root)
    L = [OPEN, "sheet      %s" % name[:-3]]
    for l in RW.bound_lines(t):
        w = l.split()
        if w[0] in INPUT_ROLES:
            # the full hash cut to 8: git's %h grows with the repository's size (a clone with more objects printed 9
            # characters on 29 September 2026 and every sheet read as changed), so the length is fixed here
            rc, last = _git(root, "log", "-1", "--format=%H", "--", w[1]) if gs is not None else (1, "")
            l += " changed %s" % (last[:8] if rc == 0 and last else "UNKNOWN")
        L.append(l)
    rc, head = _git(root, "rev-parse", "--short=8", "HEAD") if gs is not None else (1, "")
    L.append("read       %s at %s" % (today or datetime.date.today().isoformat(), head if rc == 0 and head else "UNKNOWN"))
    L.append(FENCE)
    return L


def emit_tables(letter, root=None, calc=None):
    """The section 2 tables a sheet should carry now, as lines: the tool's cells, and in the note column the note
    the sheet already holds for that rail, with every row that moved or is new marked for its explanation."""
    root = os.path.abspath(root or ROOT)
    RW = calc or load_calc()
    t = RW.rows(letter, root)
    name = SHEETS.get(letter) or (letter.upper() + ".md")
    old = {}
    try:
        with open(os.path.join(root, *(SHEET_DIR + (name,))), encoding="utf-8") as f: lines = f.read().splitlines()
    except OSError:
        lines = []
    for sec in sections(lines):
        if not (sec[0] and sec[0][0] == POWER_SECTION): continue
        for tab in tables(sec[2], sec[1]):
            noted = bool(tab["head"]) and tab["head"][-1] == NOTE
            head = tuple(tab["head"][:-1]) if noted else tuple(tab["head"])
            for r in tab["rows"]:
                if r: old[(head, r[0])] = (r[:len(head)], r[len(head)] if noted and len(r) > len(head) else "")
    L = []
    for tab in tables(RW.markdown(t).splitlines()):
        head = tuple(tab["head"])
        L.append("| " + " | ".join(list(head) + [NOTE]) + " |")
        L.append("|" + "|".join(RW.ALIGN.get(h, "---") for h in head) + "|---|")
        for r in tab["rows"]:
            was = old.get((head, r[0]))
            if was is None:
                note = MARK_NEW + " from the intent file's own text"
            else:
                cells, note = was
                moved = ["`%s` was %s" % (h, cells[k] if k < len(cells) else "absent")
                         for k, h in enumerate(head) if k and (cells[k] if k < len(cells) else "") != r[k]]
                if moved: note = ("%s (%s) %s" % (MARK_MOVED, "; ".join(moved), note)).strip()
            L.append("| " + " | ".join(x.replace("|", "\\|") for x in list(r) + [note]) + " |")
        L.append("")
    return L


def emit(letter, root=None, calc=None):
    return "\n".join(emit_block(letter, root, calc) + [""] + emit_tables(letter, root, calc))


def emit_sheet(letter, root=None, calc=None, today=None):
    """The whole sheet re-bound, as text: its block's inputs at the committed files' hashes and commits, its `read`
    line, its model and stack, and section 2's tables as the tool prints them now with the sheet's notes kept and
    every row that moved or is new marked. Every other line is the sheet's own. Raises ValueError for a sheet with no
    bound block in its opening: a first binding is written by whoever reads the sheet, never emitted."""
    root = os.path.abspath(root or ROOT)
    RW = calc or load_calc()
    name = SHEETS.get(letter) or (letter.upper() + ".md")
    with open(os.path.join(root, *(SHEET_DIR + (name,))), encoding="utf-8") as f: text = f.read()
    lines = text.split("\n")
    secs = sections(lines)
    blocks = bound_blocks(secs[0][2])
    if not blocks: raise ValueError("%s carries no bound block in its opening; there is nothing to re-bind" % name)
    said = read_bound(blocks[0])
    t = RW.rows(letter, root)
    gs = git_state(root)
    fresh = {}
    for l in RW.bound_lines(t):
        w = l.split()
        fresh[w[0]] = l

    def input_line(role, path):
        now = sha16(os.path.join(root, path))
        rc, last = _git(root, "log", "-1", "--format=%H", "--", path) if gs is not None else (1, "")
        last = last[:8] if rc == 0 and last else last   # a fixed length, as in emit above
        was = said["inputs"].get(role) or {}
        if not (rc == 0 and last):
            last = was.get("changed") if was.get("sha16") == now and was.get("path") == path and was.get("changed") else "UNKNOWN"
        return "%-10s %s sha256/16 %s changed %s" % (role, path, now or "absent", last)
    rc, head = _git(root, "rev-parse", "--short=8", "HEAD") if gs is not None else (1, "")
    reads = {role: rel for role, rel, _sha in t["inputs"]}
    out_block, seen, last_input = [], set(), None
    for n, raw in blocks[0]["body"]:
        key = raw.split()[0]
        if key in INPUT_ROLES:
            out_block.append(input_line(key, reads.get(key) or said["inputs"].get(key, {}).get("path") or raw.split()[1]))
            seen.add(key); last_input = len(out_block)
        elif key in ("model", "stack"): out_block.append(fresh[key])
        elif key == "read":
            out_block.append("read       %s at %s" % (today or datetime.date.today().isoformat(),
                                                      head if rc == 0 and head else "UNKNOWN"))
        else: out_block.append(raw)
        seen.add(key)
    missing = [input_line(role, rel) for role, rel in reads.items() if role not in seen]
    at = last_input if last_input is not None else len(out_block)
    out_block[at:at] = missing
    for key in ("model", "stack"):
        if key not in seen: out_block.append(fresh[key])
    if "read" not in seen:
        out_block.append("read       %s at %s" % (today or datetime.date.today().isoformat(), head if rc == 0 and head else "UNKNOWN"))
    a = blocks[0]["line"]                                     # the fence's line, 1-based; the opening starts at line 1
    b = next(i for i in range(a, len(lines)) if lines[i].strip() == FENCE)
    edits = [(a, b, out_block)]                                # replace lines[a:b], the block's body
    # section 2's tables
    new_tabs, cur = {}, None
    for l in emit_tables(letter, root, RW):
        c = split_row(l)
        if c is None: continue
        if c[0] == "rail" and not is_rule(c):
            cur = tuple(c[:-1]); new_tabs[cur] = []
        new_tabs[cur].append((c, l))
    power = [x for x in secs if x[0] and x[0][0] == POWER_SECTION]
    if len(power) != 1: raise ValueError("%s has %d sections numbered 2" % (name, len(power)))
    placed, end = set(), None
    for tab in tables(power[0][2], power[0][1]):
        noted = bool(tab["head"]) and tab["head"][-1] == NOTE
        head = tuple(tab["head"][:-1]) if noted else tuple(tab["head"])
        if head not in new_tabs: continue
        rows = new_tabs[head]
        keep_note = noted or any(c[-1] for c, _l in rows[2:])
        body = [l if keep_note else "| " + " | ".join(x.replace("|", "\\|") for x in c[:-1]) + " |"
                for c, l in rows]
        if not keep_note: body[1] = "|" + "|".join(RW.ALIGN.get(h, "---") for h in head) + "|"
        first = tab["line"] - 1                               # 0-based index of the table's header line
        edits.append((first, first + 2 + len(tab["rows"]), body))
        placed.add(head); end = first + 2 + len(tab["rows"])
    sec_end = power[0][1] + len(power[0][2])                  # 0-based index just past section 2's last line
    for head, rows in new_tabs.items():
        if head in placed: continue
        where = end if end is not None else sec_end
        edits.append((where, where, [""] + [l for _c, l in rows] + ([""] if end is None else [])))
    for x, y, new in sorted(edits, key=lambda e: e[0], reverse=True):
        lines[x:y] = new
    return "\n".join(lines)


# ------------------------------------------------------------------------------------------------------------------
def main(argv):
    known = {"--board": 1, "--root": 1, "--out-dir": 1, "--emit": 1, "--sheet": 0, "--no-git": 0, "--json": 0}
    i, bad = 0, []
    while i < len(argv):                      # an unknown or incomplete option is refused, never ignored
        k = argv[i]
        if k not in known: bad.append(k); i += 1; continue
        if known[k] and (i + 1 >= len(argv) or argv[i + 1].startswith("--")): bad.append(k + " (needs a value)")
        i += 1 + known[k]
    if bad:
        print("constraints_bound: REFUSED, unknown or incomplete argument(s): %s" % ", ".join(bad))
        print(__doc__.split("Usage:")[1].split("Exit:")[0].rstrip())
        return _v.USAGE
    root = os.path.abspath(_v.opt(argv, "--root", None) or ROOT)
    RW = load_calc()
    one = _v.opt(argv, "--emit", None)
    if one:
        if one.lower() not in RW.ORDER:
            print("constraints_bound: no board %r; the boards are %s" % (one, ", ".join(RW.ORDER))); return _v.USAGE
        if "--sheet" in argv:
            try: sys.stdout.write(emit_sheet(one.lower(), root, RW))
            except (ValueError, OSError) as e:
                print("constraints_bound: %s" % e); return _v.USAGE
            return 0
        print(emit(one.lower(), root, RW))
        return 0
    only = _v.opt(argv, "--board", None)
    if only and only.lower() not in RW.ORDER:
        print("constraints_bound: no board %r; the boards are %s" % (only, ", ".join(RW.ORDER))); return _v.USAGE
    letters = [only.lower()] if only else list(RW.ORDER)
    out_dir = _v.opt(argv, "--out-dir", None) or os.environ.get("VERDICT_DIR") or None
    git = False if "--no-git" in argv else None
    ran = calc_path()
    theirs = sha16(calc_path(root))
    results, worst = [], 0
    for letter in letters:
        r = judge(letter, root, RW, git)
        if theirs and theirs != sha16(ran):
            r["notes"].append("%s: the tree judged carries its own calc/rail_widths.py (sha256/16 %s); the one run is "
                              "this tool's tree's (%s)" % (r["sheet"], theirs, sha16(ran)))
        results.append(r)
        if r["missing_input"]: result = _v.INCONCLUSIVE
        else: result = _v.FAIL if r["fails"] else _v.PASS
        r["result"] = result
        worst = max(worst, _v.CODE[result])
        print("constraints_bound: %-3s %-13s %3d check(s), %d failed   %s"
              % (letter.upper(), result, r["checked"], len(r["fails"]), r["sheet"]))
        for f in r["fails"]: print("  FAIL %s" % f)
        for n in r["notes"]: print("  note %s" % n)
        if out_dir:
            _v.write("%s_%s" % (TOOL, letter), result, out_dir=out_dir, quiet=True,
                     counts={"checked": r["checked"], "fail": len(r["fails"])}, denominator=r["checked"],
                     evidence=r["fails"][:50], inputs=r["inputs"], missing_input=r["missing_input"],
                     note="the sheet's declared inputs against the committed files, its model and stack against the "
                          "calculation's, and its power tables cell by cell against rail_widths.py run now; a "
                          "table's note column is the sheet's own words and is not compared")
    st = None
    if not only:
        st = judge_set(root, letters, RW)
        st["result"] = _v.FAIL if st["fails"] else _v.PASS
        print("constraints_bound: set %-13s %3d check(s), %d failed   calc/rail_widths.out against a fresh run, byte "
              "for byte" % (st["result"], st["checked"], len(st["fails"])))
        for f in st["fails"]: print("  FAIL %s" % f)
        worst_boards = worst
        worst = max(worst, _v.CODE[st["result"]])
        if out_dir:
            n = sum(r["checked"] for r in results) + st["checked"]
            fails = [f for r in results for f in r["fails"]] + st["fails"]
            whole = _v.FAIL if fails else (_v.INCONCLUSIVE if worst_boards == _v.CODE[_v.INCONCLUSIVE] else _v.PASS)
            _v.write(TOOL, whole, out_dir=out_dir, quiet=True, counts={"checked": n, "fail": len(fails),
                                                                       "boards": len(results)},
                     denominator=n, evidence=fails[:50],
                     inputs={"board": None, "rail_widths_out": _pa.record(os.path.join(
                         root, *(SHEET_DIR + ("calc", "rail_widths.out"))), content=False) or "absent"},
                     note="the set's reading: every board's sheet, and calc/rail_widths.out byte for byte against a "
                          "fresh run. A board is decided by its own constraints_bound_<letter>")
    if "--json" in argv:
        print(json.dumps({"boards": results, "set": st}, indent=1, default=str))
    word = {v: k for k, v in _v.CODE.items()}[worst]
    print("constraints_bound: %s%s" % (word, "" if out_dir else "; nothing written (no --out-dir and no VERDICT_DIR), "
                                                                 "the exit code is the verdict"))
    return worst


def _printing(fn, argv):
    """The guard of a run that was told to write nowhere: a crash is printed and answered INCONCLUSIVE, and no
    verdict is left anywhere (verdict.guard would write one under the working directory)."""
    try:
        return fn(argv)
    except SystemExit:
        raise
    except BaseException as e:
        import traceback
        print("constraints_bound: CRASHED before deciding: %s"
              % traceback.format_exc().strip().split("\n")[-1][:200])
        return _v.CODE[_v.INCONCLUSIVE]


if __name__ == "__main__":
    _a = sys.argv[1:]
    if _v.opt(_a, "--out-dir", None) or os.environ.get("VERDICT_DIR"):
        _b = _v.opt(_a, "--board", None)
        sys.exit(_v.guard(TOOL + ("_" + _b.lower() if _b else ""), main, _a))
    sys.exit(_printing(main, _a))
