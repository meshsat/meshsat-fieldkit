#!/usr/bin/env python3
"""What the repaired reliability.py reads, declared in rules_status.py's CONFIG_INPUTS (stream d6rel, MESHSAT-1357,
28 September 2026; the fresh check's m8). For the INTEGRATOR to run: rules_status.py is his file.

WHY. `rules_status.CONFIG_INPUTS["reliability.py"]` still describes the tool as it was before this stream: it names
tools/pcb_board_facts.yaml, which the repaired tool no longer reads, and its comment says the tool takes the newest
netlist by mtime and records none, "so its readings do not bind anyway". A reading counts as current only while every
declared input is unchanged, so a wrong declaration either stales REL-001 for a file the tool never opens or misses a
file it does open.

WHAT THE REPAIRED TOOL READS (read in reliability.py and wear_inventory.py of this stream):
  * the declared list, tools/pcb_reliability.yaml (`judge`: the inventory's rules, the open items, every board's
    classes, exclusions and `written_against` pin), recorded by sha256 in the reading's inputs.list;
  * every document the list cites under v2/vendor/ (`_cited`: the bytes are compared with the sha256 the list
    carries, for a class's `source` and for a `looked_in`), which this script lists FROM THE LIST of the tree it runs
    in, so the declaration and the list cannot disagree on the day it is applied;
  * the artefact of the board's declared phase (its netlist, or board E5's board file), which is the thing judged and
    is recorded by sha256 and content, not a configuration input;
  * the manifest's stem and the routeflow profile's project directory, to FIND the artefact, which CONFIG_INPUTS does
    not declare for any tool (its own header says so).

It asserts the old entry is present as read on fnd/int7 at 1c4235ec, that the new text differs, re-parses the file
with `ast` and reads the entry back (and that no other entry changed), and refuses a second run. A citation added to
the list later is added to the entry by hand or by a successor of this script: the instrument sees what is declared.

Usage: apply_config_inputs_reliability.py [--root <tree>]
Prototype work: nothing here has been built or measured. An AI review, never a qualified review.
"""
import os, sys, ast

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))

OLD = ('    # reliability.py:31 and :53 the declared list; :55 rules_lib.board_facts for the project names. (It also reads\n'
       '    # the newest `<stem>*/out/<stem>.net` by mtime, :47, and records no netlist, so its readings do not bind anyway.)\n'
       '    "reliability.py": ("tools/pcb_reliability.yaml", "tools/pcb_board_facts.yaml"),\n')
MARK = "reliability.py, the repaired tool of stream d6rel"


def fail(msg):
    print("apply_config_inputs_reliability: REFUSED: %s" % msg); sys.exit(2)


def config_inputs(text, path):
    """CONFIG_INPUTS of a rules_status.py source, by parsing it: never by running it."""
    tree = ast.parse(text, filename=path)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CONFIG_INPUTS" for t in node.targets):
            return ast.literal_eval(node.value)
    fail("%s assigns no CONFIG_INPUTS at module level" % path)


def cited_documents(root):
    import yaml
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_reliability.yaml")
    d = yaml.safe_load(open(p, encoding="utf-8"))
    if not isinstance(d, dict) or "inventory" not in d:
        fail("%s is not the list of the repaired tool (no `inventory` section): merge stream d6rel first" % p)
    docs = set()
    for b in (d.get("boards") or {}).values():
        for c in (b or {}).get("classes") or []:
            s = c.get("source")
            for x in (s if isinstance(s, list) else ([s] if s else [])) + ((c.get("no_figure") or {}).get("looked_in") or []):
                name = str(x.get("document") or "")
                if not name.startswith("v2/vendor/"): fail("the list cites %r, which is not under v2/vendor/" % name)
                if not os.path.isfile(os.path.join(root, name)): fail("the list cites %s, which is not in this tree" % name)
                docs.add("../vendor/" + name[len("v2/vendor/"):])          # CONFIG_INPUTS paths are relative to v2/ecad
    if not docs: fail("the list cites no document")
    return sorted(docs)


def main(argv):
    root = os.path.abspath(argv[argv.index("--root") + 1] if "--root" in argv else DEFAULT_ROOT)
    p = os.path.join(root, "v2", "ecad", "tools", "rules_status.py")
    if not os.path.isfile(p): fail("%s is not the repository root" % root)
    old = open(p, encoding="utf-8").read()
    if MARK in old: fail("the entry already describes the repaired tool: this script has run")
    if old.count(OLD) != 1: fail("the entry of the unrepaired tool is not in %s as read at 1c4235ec" % p)
    src = open(os.path.join(root, "v2", "ecad", "tools", "reliability.py"), encoding="utf-8").read()
    if "written_against" not in src or "board_facts" in src:
        fail("v2/ecad/tools/reliability.py in this tree is not the repaired tool: merge stream d6rel first")
    before = config_inputs(old, p)
    if before.get("reliability.py") != ("tools/pcb_reliability.yaml", "tools/pcb_board_facts.yaml"):
        fail("CONFIG_INPUTS['reliability.py'] does not parse to the old entry")
    docs = cited_documents(root)
    want = tuple(["tools/pcb_reliability.yaml"] + docs)
    lines = ['    # %s (28 September 2026, S-89; declared by\n' % MARK,
             '    # v2/docs/records/d6rel/apply_config_inputs_reliability.py): judge() reads the declared list (the inventory\'s\n',
             '    # rules, the open items, every board\'s classes, exclusions and `written_against` pin) and records it by sha256\n',
             '    # in inputs.list; _cited() reads every document the list cites under v2/vendor/ and compares its bytes with the\n',
             '    # sha256 the list carries, so each is an input too (%d documents, listed from the list on the day this entry\n' % len(docs),
             '    # was written; a citation added to the list later is added here). It no longer reads pcb_board_facts.yaml\n',
             '    # and no longer takes the newest netlist by mtime: the artefact is the declared phase\'s (wear_inventory.artefact\n',
             '    # through phase_artefacts), recorded by sha256 and by content, so its readings bind.\n',
             '    "reliability.py": ("tools/pcb_reliability.yaml",\n']
    for i, d in enumerate(docs):
        lines.append('                       "%s"%s\n' % (d, ")," if i == len(docs) - 1 else ","))
    new = old.replace(OLD, "".join(lines), 1)
    if new == old: fail("the new text equals the old")
    after = config_inputs(new, p)                                       # RE-PARSED with ast
    if after.get("reliability.py") != want: fail("the entry does not read back as written: %r" % (after.get("reliability.py"),))
    changed = sorted(k for k in set(before) | set(after) if k != "reliability.py" and before.get(k) != after.get(k))
    if changed: fail("another entry changed: %s" % ", ".join(changed))
    for d in want:
        if not os.path.isfile(os.path.normpath(os.path.join(root, "v2", "ecad", d))): fail("declared input %s is not in this tree" % d)
    open(p, "w", encoding="utf-8").write(new)
    print("apply_config_inputs_reliability: CONFIG_INPUTS['reliability.py'] declares the list and %d cited document(s); "
          "pcb_board_facts.yaml is gone from it; re-parsed with ast, %d other entries unchanged"
          % (len(docs), len(after) - 1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
