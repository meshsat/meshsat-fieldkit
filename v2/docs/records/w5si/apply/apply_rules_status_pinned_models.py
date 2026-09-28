#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si2, 28 September 2026, MESHSAT-1357, layer 9): let rules_status date a reading
against files that a TRACKED MANIFEST PINS and the repository does not hold. rules_status.py is the integrator's; this
script makes the change and the integrator runs it.

WHY. The makers' IBIS models SI-001 reads are withheld from the repository (v2/vendor/ibis-manifest.yaml, its header).
rules_status binds a reading to its configuration by the sha the reading recorded or by the instant the file was
committed, and a declared input no commit holds "cannot be dated by a commit": CONFIG_CHANGED. The drafts check of
28 September 2026 (AI review) showed what follows from declaring the models as ordinary inputs:
    models committed          BOUND            (the one state that publishes them)
    present, never committed  CONFIG_CHANGED   "cannot be dated by a commit"
    absent                    CONFIG_CHANGED   "the reading recorded sha ... and the file is absent"
so the only state that read current was the one that publishes.

WHAT THIS ADDS. The manifest is declared as an ordinary configuration input of edge_length.py (that is
apply_rules_status_config_inputs.py, run BEFORE this one) and is dated like any other: by the sha the reading recorded
(inputs.ibis_manifest) or by its commit. The models are NOT declared there. They are held to the manifest by a second
table, PINNED_INPUTS, and a function, _pinned_state, which _config_state asks last:

    the reading        this checkout now         it reads
    read the model,    the file pinned           BOUND
      at the sha       the model is absent       BOUND: the pin dates it. A clean clone, the public repository and a
      pinned                                     handover ZIP read a reading taken with the models as current
    read the model at  any                       CONFIG_CHANGED, naming both
      another sha
    any                present, and NOT the      CONFIG_CHANGED for every reading that asked for that model
                       file pinned
    recorded the       absent                    BOUND: the reading is INCONCLUSIVE by the tool and says which state it
      model absent                               was taken in; nothing changed since
    recorded the       present, the file pinned  CONFIG_CHANGED, on purpose and saying so: the reading was taken without
      model absent                               a model that is here now, so a re-take reads more
    did not ask for    any                       not asked: the reading does not depend on it
      the model
    (the manifest cannot be read, or refuses a row)  CONFIG_CHANGED: nothing pins what the reading read
A model that is ABSENT never makes a reading read as changed by accident.

HOW: on the parsed structure (_pyedit.py). The block is inserted on lines of its own above `def _config_state`, and the
ONE final `return True, "BOUND", "", used` of that function becomes the three statements that ask _pinned_state first.
The file is parsed again and compared: every other module-level statement is the same, _config_state's body is the old
one up to its last statement, and the last statement is the old return.

Its test is v2/ecad/tools/tests/test_pinned_models.py, on an isolated git repository of its own; it is skipped, saying
so, until this draft is applied.

    python3 v2/docs/records/w5si/apply/apply_rules_status_pinned_models.py [--root <tree>] [--dry-run]
A second run is refused ("already applied").
"""
import os, sys, ast

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _pyedit as PE
import _apply as AP

MANIFEST = "../vendor/ibis-manifest.yaml"
BLOCK = '''# ------------------------------------------------------------------------------------------------------------------
# INPUTS A TRACKED MANIFEST PINS (28 September 2026, MESHSAT-1357, stream w5si2). The makers' IBIS models rule SI-001
# reads are NOT in the repository: several forbid distribution in their own header and publication is the owner's
# decision. What is tracked is v2/vendor/ibis-manifest.yaml, which pins each model by the sha256 of the extracted
# file; it is declared in CONFIG_INPUTS and dated like any input. The models are held to it HERE and never asked of
# git: a file no commit holds "cannot be dated by a commit", which would make the only current state the one that
# publishes. Per model the manifest pins and the reading asked for (inputs.model_N, or a document of the same path in
# a reading older than the manifest):
#   the reading read it at the sha pinned           BOUND, whether the model is in this checkout or not
#   the reading read it at another sha              CONFIG_CHANGED
#   the file in this checkout is not the one pinned CONFIG_CHANGED
#   the reading recorded it absent, and it is absent now    BOUND (the reading is INCONCLUSIVE by the tool)
#   the reading recorded it absent, and it is here now      CONFIG_CHANGED: a re-take reads more, and says so
# A manifest lies at <repository>/v2/vendor/ and names its files relative to the repository. Paths are relative to
# v2/ecad, as in CONFIG_INPUTS; a fixture hands an absolute path.
PINNED_INPUTS = {"edge_length.py": ("%s",)}


def _recorded_model(rec, file):
    """("READ", sha256/16) or ("ABSENT", None) as the reading recorded a pinned file, by its path; None when the reading
    did not ask for it."""
    want = os.path.normpath(str(file))
    for v in (rec.get("inputs") or {}).values():
        if not isinstance(v, dict) or os.path.normpath(str(v.get("path") or "")) != want: continue
        if v.get("absent"): return "ABSENT", None
        if v.get("sha256_16"): return "READ", str(v["sha256_16"])
    return None


def _pinned_state(rec, wf, pinned=None):
    """None, or why a reading is not current against the files a tracked manifest pins. See the block comment above."""
    table = PINNED_INPUTS if pinned is None else pinned
    for tmpl in table.get(wf, ()):
        mp = os.path.normpath(os.path.join(ECAD, tmpl))
        root = os.path.dirname(os.path.dirname(os.path.dirname(mp)))
        rel = os.path.relpath(mp, root)
        try:
            import ibis_manifest as _im
            man = _im.load(root, rel)
        except Exception as e:
            return "the manifest %%s could not be read (%%s), so nothing pins the models a reading read" %% (rel, type(e).__name__)
        if man.get("why"): return "%%s, so nothing pins the models a reading read" %% man["why"]
        if man.get("refusals"): return "the manifest refuses a row, so not every model is pinned: %%s" %% "; ".join(man["refusals"])[:200]
        for file, row in sorted(man["models"].items()):
            got = _recorded_model(rec, file)
            if got is None: continue
            pin16 = row["sha256"][:16]
            state, held = _im.state_of(root, row)
            if state == _im.DIFFERS:
                return ("the model %%s in this checkout is not the file %%s pins (sha256/16 %%s held, %%s pinned)"
                        %% (file, rel, held[:16], pin16))
            if got[0] == "READ" and got[1] != pin16:
                return "the reading read %%s at sha256/16 %%s and %%s pins it at %%s" %% (file, got[1], rel, pin16)
            if got[0] == "ABSENT" and state == _im.PRESENT:
                return ("the reading was taken without the model %%s, which is in this checkout now and is the file %%s pins: "
                        "a re-take reads more than this reading did" %% (file, rel))
    return None


''' % MANIFEST
TAIL = ('why = _pinned_state(rec, wf)\n'
        '    if why: return False, "CONFIG_CHANGED", "a file the manifest pins changed since the reading: %s" % why, []\n'
        '    return True, "BOUND", "", used')


def func(tree, name):
    hits = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(hits) == 1, "%d module-level functions named %s, expected one" % (len(hits), name)
    return hits[0]


def main():
    root = AP.root_of(HERE)
    AP.need_stream(root)
    target = os.path.join(root, "v2", "ecad", "tools", "rules_status.py")
    AP.need(os.path.exists(target), "v2/ecad/tools/rules_status.py is not in the tree %s" % root)
    src = open(target, encoding="utf-8").read()
    tree = PE.parse(src)
    names = {t.id for n in tree.body if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    funcs = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)}
    AP.need("PINNED_INPUTS" not in names and "_pinned_state" not in funcs, "already applied")
    AP.need("_recorded_model" not in funcs, "rules_status.py already defines _recorded_model, which this draft would define: re-read it")
    AP.need("ECAD" in names, "rules_status.py assigns no module-level ECAD, which the block resolves its paths against: re-read it")
    cfg = ast.literal_eval(PE.assignment(tree, "CONFIG_INPUTS").value)
    AP.need(MANIFEST in cfg.get("edge_length.py", ()),
            "CONFIG_INPUTS['edge_length.py'] does not declare %s: run apply_rules_status_config_inputs.py first, so that the manifest "
            "itself is dated like any input" % MANIFEST)
    AP.need(not any(str(p).endswith(".ibs") for p in cfg.get("edge_length.py", ())),
            "CONFIG_INPUTS['edge_length.py'] declares a maker's model (.ibs) as an ordinary input: it would read CONFIG_CHANGED "
            "wherever the models are not committed; re-issue the entry with apply_rules_status_config_inputs.py --refresh")
    f = func(tree, "_config_state")
    last = f.body[-1]
    AP.need(isinstance(last, ast.Return) and isinstance(last.value, ast.Tuple) and len(last.value.elts) == 4
            and isinstance(last.value.elts[0], ast.Constant) and last.value.elts[0].value is True
            and isinstance(last.value.elts[1], ast.Constant) and last.value.elts[1].value == "BOUND"
            and isinstance(last.value.elts[3], ast.Name) and last.value.elts[3].id == "used",
            "_config_state does not end in `return True, \"BOUND\", \"\", used` as this draft read it: re-read the function")
    args = [a.arg for a in f.args.args]
    AP.need(args[:1] == ["rec"], "_config_state's first argument is not `rec`: re-read the function")
    assigned = {t.id for n in ast.walk(f) if isinstance(n, ast.Assign) for t in n.targets if isinstance(t, ast.Name)}
    AP.need("wf" in assigned and "why" not in assigned and "why" not in args,
            "_config_state does not assign `wf` (the writer's file), or already uses the name `why`: re-read the function")
    a, b = PE.span(src, last)
    at = PE.line_start(src, f)
    out = PE.apply(src, [(a, b, TAIL), (at, at, BLOCK)])
    assert out != src, "the new text does not differ from the old"
    tree2 = PE.parse(out)
    f2 = func(tree2, "_config_state")
    # every other module-level statement is the same, in the same order; two functions and one assignment are new
    new_names = ("PINNED_INPUTS", "_recorded_model", "_pinned_state")
    def is_new(n):
        return (isinstance(n, ast.FunctionDef) and n.name in new_names) or (
            isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in new_names for t in n.targets))
    rest = lambda t, skip: [ast.dump(n) for n in t.body if n is not skip and not is_new(n)]
    assert rest(tree, f) == rest(tree2, f2), "a module-level statement other than _config_state changed"
    assert sum(1 for n in tree2.body if is_new(n)) == 3, "the block did not add exactly one table and two functions"
    assert [ast.dump(n) for n in f.body[:-1]] == [ast.dump(n) for n in f2.body[:len(f.body) - 1]], "_config_state's body changed before its end"
    assert len(f2.body) == len(f.body) + 2 and ast.dump(f2.body[-1]) == ast.dump(last), "_config_state does not end in the old return"
    assert ast.dump(f.args) == ast.dump(f2.args)
    pinned = ast.literal_eval(PE.assignment(tree2, "PINNED_INPUTS").value)
    assert pinned == {"edge_length.py": (MANIFEST,)}, pinned
    AP.need(os.path.exists(os.path.normpath(os.path.join(root, "v2", "ecad", MANIFEST))), "the manifest %s is not in this tree" % MANIFEST)
    msg = ("rules_status.py: PINNED_INPUTS, _recorded_model and _pinned_state added above _config_state, which asks _pinned_state "
           "before it answers BOUND (%d lines added)\n  OWED after this draft: `python3 tests/run.py pinned_models` and `python3 tests/run.py "
           "rules_status` from v2/ecad/tools/tests; the code bundle of every reading rules_status.py writes changes with this edit"
           % (out.count("\n") - src.count("\n")))
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: " + msg); return 0
    AP.write(target, out)
    back = PE.parse(open(target, encoding="utf-8").read())
    assert ast.dump(back) == ast.dump(tree2), "the file read back is not the text that was written"
    print(msg)
    return 0


if __name__ == "__main__":
    AP.run(main)
