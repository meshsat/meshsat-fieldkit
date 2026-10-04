#!/usr/bin/env python3
"""apply_set29_readers.py: three readers brought to set 29's merged tree (MESHSAT-1357, integration set 29, 4 October 2026; the
coordinator's integration corrections, each a reader that pinned another record's STRUCTURE and failed its test after the merges).

  1. test_l8p.py: the test read the first "with scratch stand-ins for" line of record l8p's output. L4-E11's round 9 corrected
     L8P-F02 and L8P-F03, so boards A and E now compose to the generator's end with NO stand-in and the output prints no such line
     (IndexError). The property kept: no stand-in for the closed L8P-F01 is used, now read on every such line, none being a pass.
  2. l6r2_passives.py, change_chain(): it built a board's pending chain from L4-E9's CHANGE_SCRIPTS only. L4-E9 now lists drafts it
     reads from copied inputs (record l8p's three, record l8r2's pack return), which CHANGE_SCRIPTS does not carry, so the chain
     skipped record l8p's PTC draft and L4-E11's DD-7 draft, which the change list orders after it, refused. A draft the change
     list names and CHANGE_SCRIPTS lacks is now found in the tree by its file name under v2/docs/records (exactly one).
  3. l8r2_drafts.py: the change list's board E round now carries record l8p's enable draft and this record's own pack return. E_ROUND
     gains ("l8p", "enable") before cin, and e_round_page() leaves out this record's own drafts (MINE_E), which it composes against
     the round at every prefix.
Nothing of any record's figures or prose changes. Run from the repository root: apply_set29_readers.py [--check | --write]; each old
text must occur exactly once; a second run exits 3 ("already applied"). Then regenerate the two outputs through _bin/regen_out.py."""
import ast
import sys

EDITS = [
    ("v2/ecad/tools/tests/test_l8p.py",
     '    assert "L8P-F01" not in t.split("with scratch stand-ins for ")[1].split("\\n")[0], "a stand-in for the closed L8P-F01 is still used"\n',
     '    for seg in t.split("with scratch stand-ins for ")[1:]:      # none at all since L4-E11\'s round 9 corrected L8P-F02 and L8P-F03\n'
     '        assert "L8P-F01" not in seg.split("\\n")[0], "a stand-in for the closed L8P-F01 is still used"\n'),
    ("v2/docs/records/l6r2/l6r2_passives.py",
     '            hits = [p for p in m.CHANGE_SCRIPTS if p.endswith("/" + s)]\n',
     '            hits = [p for p in m.CHANGE_SCRIPTS if p.endswith("/" + s)]\n'
     '            if not hits:      # a draft L4-E9 reads from a copied input (records l8p, l8r2): found in the tree by its name, exactly one\n'
     '                import glob\n'
     '                found = sorted(glob.glob(os.path.join(TOP, "v2", "docs", "records", "*", s)))\n'
     '                if len(found) == 1:\n'
     '                    hits = [os.path.relpath(found[0], os.path.join(TOP, "v2", "docs", "records")).replace(os.sep, "/")]\n'),
    ("v2/docs/records/l8r2/l8r2_drafts.py",
     '           ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("d8dec31", "cin")]\n',
     '           ("l4e9", "hotswap"), ("l4e11", "entry"), ("l4e7", "solar_guard"), ("l4e11", "aux"), ("l8p", "enable"), ("d8dec31", "cin")]\n'),
    ("v2/docs/records/l8r2/l8r2_drafts.py",
     '    """board E\'s scripts in the change list\'s order, as L4-POWER-ARCHITECTURE.md\'s change table gives them (the ALT rows left out)."""\n',
     '    """board E\'s scripts in the change list\'s order, as L4-POWER-ARCHITECTURE.md\'s change table gives them (the ALT rows left out,\n'
     '    and this record\'s own drafts, MINE_E, which the table lists since set 29 and which are composed against the round)."""\n'
     '    own = {"apply_gen_sch_e_%s.py" % n for _r, n in MINE_E}\n'),
    ("v2/docs/records/l8r2/l8r2_drafts.py",
     '            if s not in seq:\n                seq.append(s)\n    return seq\n',
     '            if s not in seq and s not in own:\n                seq.append(s)\n    return seq\n'),
]


def main(argv):
    write = "--write" in argv
    texts = {}
    done = 0
    for path, old, new in EDITS:
        t = texts.get(path) or open(path, encoding="utf-8").read()
        if new in t and old not in t:
            done += 1
            continue
        if t.count(old) != 1:
            sys.stderr.write("apply_set29_readers: REFUSED: %s: %d occurrence(s) of %r\n" % (path, t.count(old), old[:70]))
            return 1
        assert new != old
        texts[path] = t.replace(old, new)
    if done == len(EDITS):
        sys.stderr.write("apply_set29_readers: already applied\n")
        return 3
    for path, t in texts.items():
        ast.parse(t)
        if write:
            open(path, "w", encoding="utf-8").write(t)
    print("apply_set29_readers: %s, %d edit(s) in %d file(s)" % ("WRITTEN" if write else "CHECK OK", len(EDITS) - done, len(texts)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
