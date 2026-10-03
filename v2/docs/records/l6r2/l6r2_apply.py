#!/usr/bin/env python3
"""l6r2_apply.py: the shared logic of the six DRAFT apply scripts of record l6r2 (MESHSAT-1357, 3 October 2026).

Each board's draft (apply_gen_sch_X_lcsc.py) carries its own table, designator -> (the committed value, the selected LCSC code)
or, since round 4, (the committed value, the selected code, the code it replaces), rendered by l6r2_passives.py, and inserts it
into gen_sch_X.py once, before the line `import schlayout, time as _time` (every generator places its parts there, so the table
is read after every part call and before any symbol is written). The inserted block sets a part's LCSC field only when its value
is the value the code was selected for AND the part carries no code, or carries exactly the code the entry replaces (round 4: a
code the generator's call writes that fails a requirement, finding F7); a part whose value or code another draft has changed keeps
what it has, and the generator prints those designators. Designators are never changed. Why a table and not a keyword on each call (SESSION): many calls are made in loops and in helper functions
whose values are parameters (the converter blocks), and a keyword on each call would need those calls restructured; the
value-keyed table is order-independent against the other drafts. Reverse: remove the block.

RELEASE GUARD: a draft refuses the repository's own generator until v2/docs/records/l6r2/RELEASE.md reads `released: yes` and
names an accepted check; it writes scratch copies freely. A second application is refused. The new text must differ and must
parse (ast)."""
import ast
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHOR = "import schlayout, time as _time\n"
MARK = "# LAYER 6 RECORD l6r2 (MESHSAT-1357"
NAMES = ("_L6R2_LCSC", "_p6", "_e6", "_s6")


def _top():
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()


def released():
    p = os.path.join(HERE, "RELEASE.md")
    if not os.path.exists(p): return False
    t = open(p, encoding="utf-8").read()
    return bool(re.search(r"^released:\s*yes\s*$", t, re.M)) and bool(re.search(r"^accepted check:\s*\S+", t, re.M))


def block(board, entries):
    lines = [MARK + ", 3 October 2026): the LCSC order codes of board %s's generic parts (resistors, capacitors," % board.upper(),
             "# ferrites, small diodes, indicator LEDs) selected in v2/docs/records/l6r2/L6R2-PASSIVES.md (rule I-1; every requirement checked",
             "# against JLCPCB's parts library there). Keyed by designator AND the value each code was selected for: a part whose value another",
             "# draft has changed keeps no code from this table and is printed below; a part that already carries a code keeps its own,",
             "# unless the entry names that very code as the one it replaces (a third field: a code written in a call that fails a requirement).",
             "_L6R2_LCSC = {"]
    for ref, e in entries.items():
        lines.append("    %r: %r," % (ref, tuple(e)))
    lines += ["}",
              "for _p6 in P:",
              "    _e6 = _L6R2_LCSC.get(_p6[\"ref\"])",
              "    if _e6 and _p6.get(\"value\") == _e6[0] and (_p6.get(\"lcsc\") or \"\") in (\"\",) + tuple(_e6[2:]):",
              "        _p6[\"lcsc\"] = _e6[1]",
              "_s6 = sorted(_k for _k, _e in _L6R2_LCSC.items() if not any(_q[\"ref\"] == _k and _q.get(\"value\") == _e[0] and _q.get(\"lcsc\") == _e[1] for _q in P))",
              "if _s6:",
              "    print(\"l6r2: %d LCSC entries not applied (the part's value or code moved, or the part is gone): %s\" % (len(_s6), \", \".join(_s6)))",
              ""]
    return "\n".join(lines)


def apply_text(text, board, entries):
    """(state, new text, why). OK, or REFUSED with the reason; pure: nothing written."""
    if text.count(ANCHOR) != 1:
        return "REFUSED", None, "the anchor line %r is not in the generator exactly once" % ANCHOR.strip()
    if MARK in text:
        return "REFUSED", None, "the block is already in the generator: a second application is refused"
    for n in NAMES:
        if re.search(r"\b%s\b" % re.escape(n), text):
            return "REFUSED", None, "the generator already uses the name %s" % n
    new = text.replace(ANCHOR, block(board, entries) + ANCHOR, 1)
    if new == text:
        return "REFUSED", None, "the new text does not differ"
    try:
        ast.parse(new)
    except SyntaxError as e:
        return "REFUSED", None, "the result does not parse: %s" % e
    return "OK", new, "%d entries inserted before the layout" % len(entries)


def render_draft(board, entries):
    body = ["#!/usr/bin/env python3",
            '"""apply_gen_sch_%s_lcsc.py: DRAFT for board %s\'s generator owner (Layer 6 record l6r2, MESHSAT-1357, 3 October 2026). NOT APPLIED.' % (board, board.upper()),
            "",
            "It writes the LCSC field of board %s's generic parts into v2/ecad/tools/gen_sch_%s.py: %d designators, each keyed by the value" % (board.upper(), board, len(entries)),
            "the code was selected for (v2/docs/records/l6r2/L6R2-PASSIVES.md and l6r2_passives.out; the logic in l6r2_apply.py). Rendered by"]
    n3 = sum(1 for e in entries.values() if len(e) > 2)
    if n3:
        body[-1] = "the code was selected for; %d of them correct a code the generator's call writes (the entry's third field is the code" % n3
        body.append("replaced, finding F7) (v2/docs/records/l6r2/L6R2-PASSIVES.md and l6r2_passives.out; the logic in l6r2_apply.py). Rendered by")
    body += [
            "`l6r2_passives.py --write-drafts`; test_l6r2.py holds this file equal to the render and proves its composition with every other",
            "pending draft of the generator.",
            "Usage:  apply_gen_sch_%s_lcsc.py TARGET [--check | --write]     (default --check: nothing is written)" % board,
            "Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse).\"\"\"",
            "import os",
            "import sys",
            "",
            "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
            "import l6r2_apply  # noqa: E402",
            "",
            "BOARD = %r" % board,
            "ENTRIES = {"]
    for ref, e in entries.items():
        body.append("    %r: %r," % (ref, tuple(e)))
    body += ["}", "", "", "if __name__ == \"__main__\":", "    sys.exit(l6r2_apply.main(BOARD, ENTRIES, sys.argv[1:]))", ""]
    return "\n".join(body)


def main(board, entries, argv):
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__); return 3
    target = os.path.realpath(args[0])
    write = "--write" in argv
    own = os.path.realpath(os.path.join(_top(), "v2", "ecad", "tools", "gen_sch_%s.py" % board))
    if target == own and not released():
        print("apply_gen_sch_%s_lcsc: REFUSED: the repository's own generator, and v2/docs/records/l6r2/RELEASE.md does not read "
              "'released: yes' with an accepted check" % board)
        return 3
    st, new, why = apply_text(open(target, encoding="utf-8").read(), board, entries)
    if st != "OK":
        print("apply_gen_sch_%s_lcsc: REFUSED: %s" % (board, why)); return 3
    if write:
        open(target, "w", encoding="utf-8").write(new)
        print("apply_gen_sch_%s_lcsc: WRITTEN, %s" % (board, why))
    else:
        print("apply_gen_sch_%s_lcsc: checked, not written: %s" % (board, why))
    return 0
