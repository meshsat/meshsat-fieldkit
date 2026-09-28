#!/usr/bin/env python3
"""What every draft of this stream does BEFORE it touches a file, and how it refuses (stream w5si2, 28 September 2026,
MESHSAT-1357; the drafts check's M4: "no draft asserts that the stream is merged ... three stop on AttributeError or
FileNotFoundError").

A draft states its preconditions as sentences (`need`), checks them first, builds every new text in memory, and writes
last. Whatever stops it, it ends with ONE sentence that says what did not hold and whether anything was written, and
exit code 2; never a traceback. `run(main)` is that ending. A failure nobody foresaw is still said in a sentence, with
the exception's name and the line of the draft it came from, because a draft that dies silently is read as applied.
"""
import os, sys, ast, traceback

WROTE = []          # every file a draft has written, so a refusal can say so


class Refused(Exception):
    """A precondition that does not hold: the sentence is the message."""


def need(cond, sentence):
    if not cond: raise Refused(sentence)


def root_of(here, argv=None):
    """The tree a draft runs on: --root <tree>, else the tree the draft lies in."""
    argv = sys.argv if argv is None else argv
    if "--root" in argv:
        need(argv.index("--root") + 1 < len(argv), "--root names no tree")
        return os.path.abspath(argv[argv.index("--root") + 1])
    return os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))


def need_files(root, rels, why):
    for r in rels:
        need(os.path.exists(os.path.join(root, r)), "%s is not in the tree %s: %s" % (r, root, why))


STREAM_FILES = ("v2/ecad/tools/edge_length.py", "v2/ecad/tools/ibis_read.py", "v2/ecad/tools/ibis_manifest.py",
                "v2/ecad/tools/pcb_edge_rates.yaml", "v2/vendor/ibis-manifest.yaml", ".gitignore")
STREAM_NAMES = {"v2/ecad/tools/edge_length.py": ("load_rates", "citations", "model_record", "Reason", "schematic_table"),
                "v2/ecad/tools/ibis_read.py": ("cell_check", "flagged_pins"),
                "v2/ecad/tools/ibis_manifest.py": ("load", "pin", "state_of")}


def need_stream(root):
    """The stream is MERGED into the tree the draft runs on: its files are there, its tools define what the drafts
    call (read from the parsed source, never searched for as text), and the ignore rule that keeps the makers' models
    out of the repository is in .gitignore."""
    why = "stream w5si2 (fnd/w5si2) is not merged into this tree, and this draft changes a file for what that stream brings"
    need_files(root, STREAM_FILES, why)
    for rel, names in STREAM_NAMES.items():
        try: tree = ast.parse(open(os.path.join(root, rel), encoding="utf-8").read())
        except SyntaxError as e: raise Refused("%s does not parse (%s): %s" % (rel, e, why))
        have = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))}
        lost = [n for n in names if n not in have]
        need(not lost, "%s does not define %s: %s" % (rel, ", ".join(lost), why))
    rules = [l.strip() for l in open(os.path.join(root, ".gitignore"), encoding="utf-8").read().splitlines()]
    need("v2/vendor/*/ibis/*.ibs" in rules, ".gitignore does not ignore v2/vendor/*/ibis/*.ibs, so a maker's model could be "
                                          "committed and published: " + why)


def tools_on_path(root):
    t = os.path.join(root, "v2", "ecad", "tools")
    if t not in sys.path: sys.path.insert(0, t)
    return t


def write(path, text):
    """Write one file whole, through a temporary name, and note it."""
    with open(path + ".part", "w", encoding="utf-8") as f: f.write(text)
    os.replace(path + ".part", path)
    WROTE.append(path)


def run(main):
    """Run a draft's main(); end in one sentence and exit code 2 if it cannot go on."""
    def said():
        return ("nothing was written" if not WROTE else
                "WRITTEN BEFORE IT STOPPED: %s (put them back with `git checkout -- <file>` and read why)" % ", ".join(WROTE))
    try:
        rc = main()
    except Refused as e:
        print("REFUSED: %s; %s" % (e, said())); sys.exit(2)
    except AssertionError as e:
        tb = traceback.extract_tb(sys.exc_info()[2])[-1]
        print("REFUSED: %s (%s line %d); %s" % (str(e) or "a check of the draft did not hold", os.path.basename(tb.filename), tb.lineno, said()))
        sys.exit(2)
    except Exception as e:
        tb = traceback.extract_tb(sys.exc_info()[2])[-1]
        print("REFUSED: the draft met %s: %s (%s line %d), which it did not foresee; %s" % (
            type(e).__name__, str(e)[:200], os.path.basename(tb.filename), tb.lineno, said()))
        sys.exit(2)
    sys.exit(rc or 0)
