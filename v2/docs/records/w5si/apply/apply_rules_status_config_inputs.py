#!/usr/bin/env python3
"""DRAFT for the integrator (stream w5si, second pass, 27 September 2026, RE-ISSUED 28 September 2026 by stream w5si2,
MESHSAT-1357, layer 9): declare what edge_length.py now reads. rules_status.py's CONFIG_INPUTS is the integrator's;
this script makes the change and the integrator runs it. It replaces the draft of 27 September, which declared the
makers' thirteen IBIS models as ordinary inputs (the drafts check's B1), and the first pass's draft, filed as
recovered under ../recovery/pass1-drafts/.

RE-ISSUED BECAUSE THE MODELS ARE NOT IN THE REPOSITORY. A declared input no commit holds "cannot be dated by a
commit" and reads CONFIG_CHANGED, so with the models declared the only state that read current was the one that
publishes them. This issue declares NO model. It declares the tracked manifest that pins them,
../vendor/ibis-manifest.yaml, which is dated like any input, and the models are held to it by
apply_rules_status_pinned_models.py, run AFTER this one. It works in both states of the tree: it reads the data file
and the manifest, never a model.

WHY. rules_status.CONFIG_INPUTS["edge_length.py"] lists the configuration a SI-001 reading depends on, and rules_status
examines only DECLARED paths. Since this stream the reading also reads:
  * tools/pcb_edge_rates.yaml, the edge rates as data (recorded by the reading as inputs.edge_rates);
  * the manifest that pins the makers' models (inputs.ibis_manifest); the models themselves are recorded under
    inputs.model_N and are NOT declared here;
  * every held document a record of that file cites (inputs.document_N);
  * the search listing the data file names (inputs.search_listing);
  * for a net that continues onto another board of the set, that board's declared netlist (inputs.far_netlist_<x>).
Without the entry a changed data file, a changed manifest or a regenerated neighbour netlist would leave a SI-001
reading reading current. AND THE OTHER WAY ROUND: once the entry is applied, the data file, the manifest and the
listing must be COMMITTED before rules_status or rules_render run, or every SI-001 reading reads CONFIG_CHANGED (an
uncommitted configuration input cannot be dated). The models need not be and must not be committed.

WHAT IS RE-DERIVED AT APPLY TIME, on the tree it runs in, never typed here: the list of cited documents (from the data
file, through edge_length.citations) and the six netlist paths (from phase_artefacts, the declared phase of each
board). A LIMIT, stated here and in what the script prints (the drafts check's M9): the netlists are named by their
phase directory (pcb-a-power-a23 and so on), because the templates of CONFIG_INPUTS know only the judged board's own
phase, and a glob over the phase directories would hold a reading to an older phase's netlist of the same name. When
a board's declared phase moves, or the data file cites a new document, run this again with --refresh: it re-derives
the entry and replaces it. Until then a reading of a board whose NEIGHBOUR moved phase is held to the neighbour's old
netlist: it reads current against a file the design has left, which --refresh ends.

HOW: on the parsed structure (see _pyedit.py). The ONE module-level assignment to CONFIG_INPUTS is located with ast,
the value of its key "edge_length.py" is replaced at the position the parser gives, and a comment goes on lines of its
own above the key. The file is parsed again and the evaluated dictionary must be the old one with exactly that one
value changed: every other key there with the same value, none added, none lost; the new value holds every entry the
old one had, in the same order, plus the derived ones; and no other statement of the module changed.

Applied by the integrator on the integrated tree (after set 6), from anywhere:
    python3 v2/docs/records/w5si/apply/apply_rules_status_config_inputs.py [--root <tree>] [--dry-run] [--refresh]
A second run without --refresh is refused ("already applied"); with --refresh it is refused when nothing moved.
"""
import os, sys, ast, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _pyedit as PE
import _apply as AP

ROOT = AP.root_of(HERE) if "--root" not in sys.argv or sys.argv.index("--root") + 1 < len(sys.argv) else os.path.abspath(".")
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
ECAD = os.path.join(ROOT, "v2", "ecad")
TARGET = os.path.join(TOOLS, "rules_status.py")
sys.path.insert(0, TOOLS)

KEY = "edge_length.py"
BEFORE = ("tools/boards/{letter}.json", "{phase}/out/{stem}-intent.json", "{phase}/{stem}.kicad_pro",
          "tools/pcb_board_facts.yaml", "tools/stackup_write.py",
          "../vendor/standards/usb-2-0-specification-2024-09-27.md")
DATA = "tools/pcb_edge_rates.yaml"
MANIFEST = "../vendor/ibis-manifest.yaml"
MARK = "stream w5si"
COMMENT = (
    "    # SINCE 27 SEPTEMBER 2026 (stream w5si, MESHSAT-1357) EDGE_SOURCES is the STANDARD records of tools/pcb_edge_rates.yaml,\n"
    "    # the data file every edge is read from (edge_length.load_rates). The reading records it by sha (inputs.edge_rates),\n"
    "    # with every document a record it used cites (inputs.document_N), the search listing the data file names\n"
    "    # (inputs.search_listing), every other board's netlist a continued net was answered from (inputs.far_netlist_<letter>)\n"
    "    # and the manifest that pins the makers' IBIS models (inputs.ibis_manifest). All of them are declared below. THE MODELS\n"
    "    # ARE NOT: they are not in the repository, and PINNED_INPUTS holds them to the manifest. The documents and the netlist paths were DERIVED\n"
    "    # from the data file and from phase_artefacts when the entry was written, by\n"
    "    # v2/docs/records/w5si/apply/apply_rules_status_config_inputs.py: the netlists are named by phase directory, so\n"
    "    # when a board's declared phase moves or the data file cites a new document, that script is run again with --refresh.\n")


def derived():
    """(documents, listing, netlists), each a list of paths relative to v2/ecad, from the tree this runs in."""
    import edge_length as E, phase_artefacts as pa
    import ibis_manifest as IM
    rates, refusals = E.load_rates(os.path.join(TOOLS, "pcb_edge_rates.yaml"))
    assert not refusals, "the data file refuses records, so its citations are not all read: %s" % refusals[:3]
    man = IM.load(ROOT)
    assert not man["why"] and not man["refusals"], "the manifest does not stand: %s %s" % (man["why"], man["refusals"][:2])
    docs, models = set(), set()
    for sect in E.SECTIONS:
        for r in rates[sect]:
            for c in E.citations(r): docs.add(c["document"])
            if (r.get("ibis") or {}).get("file"): models.add(r["ibis"]["file"])
    # a model is never declared: what the manifest pins, and any .ibs, is held by PINNED_INPUTS
    models |= {d for d in docs if IM.pin(man, d) is not None or d.lower().endswith(".ibs")}
    docs -= models
    lost = sorted(m for m in models if IM.pin(man, m) is None)
    assert not lost, "the data file reads a model the manifest does not pin: %s" % ", ".join(lost)
    rel = lambda p: os.path.relpath(os.path.join(ROOT, p), ECAD)
    sl = (rates.get("search_listing") or {}).get("path")
    nls = []
    for L in "abcdep":
        p = pa.netlist(L, ECAD)
        if p: nls.append(os.path.relpath(p, ECAD))
    return sorted(rel(d) for d in docs), ([rel(sl)] if sl else []), nls


def tuple_text(entries, indent):
    """The tuple as this file writes its entries: one string per line after the first, at the key's column."""
    pad = " " * indent
    lines, cur = [], "("
    for i, e in enumerate(entries):
        piece = json.dumps(e) + ("," if i < len(entries) - 1 or len(entries) == 1 else "")
        if cur not in ("(",) and len(pad) + len(cur) + 1 + len(piece) > 118:
            lines.append(cur); cur = " " + piece
        else:
            cur = cur + ("" if cur == "(" else " ") + piece
    lines.append(cur + ")")
    return ("\n" + pad).join(lines)


def main():
    AP.need_stream(ROOT)
    AP.need(os.path.exists(TARGET), "v2/ecad/tools/rules_status.py is not in the tree %s" % ROOT)
    src = open(TARGET, encoding="utf-8").read()
    tree = PE.parse(src)
    stmt = PE.assignment(tree, "CONFIG_INPUTS")
    assert isinstance(stmt.value, ast.Dict), "CONFIG_INPUTS is not a dictionary literal"
    pairs = [(k, v) for k, v in zip(stmt.value.keys, stmt.value.values) if isinstance(k, ast.Constant) and k.value == KEY]
    assert len(pairs) == 1, "%d entries for %s in CONFIG_INPUTS, expected one" % (len(pairs), KEY)
    knode, vnode = pairs[0]
    old_dict = ast.literal_eval(stmt.value)
    old = tuple(old_dict[KEY])
    refresh = "--refresh" in sys.argv
    docs, listing, nls = derived()
    assert docs and len(nls) == 6, "the data file cites %d documents and %d of the six boards have a netlist of their declared phase: %s" % (len(docs), len(nls), nls)
    for p in [MANIFEST] + docs + listing + nls:
        assert os.path.exists(os.path.join(ECAD, p)), "declared input %s is not in this tree" % p
        assert not p.lower().endswith(".ibs"), "a maker's model would be declared as an ordinary input: %s" % p
    new = list(BEFORE) + [DATA, MANIFEST]
    for p in docs + listing + nls:
        if p not in new: new.append(p)
    new = tuple(new)
    if DATA in old:
        assert refresh, "already applied"
        assert old[:len(BEFORE)] == BEFORE, "the entry's first %d inputs are not the ones this draft knows: re-read it" % len(BEFORE)
        assert new != old, "already applied: nothing moved since the entry was derived"
    else:
        assert not refresh, "--refresh asks for an entry this draft wrote, and the entry does not name %s" % DATA
        assert old == BEFORE, "the entry of %s is not as this draft read it: re-read it\n%r" % (KEY, old)
    a, b = PE.span(src, vnode)
    edits = [(a, b, tuple_text(new, vnode.col_offset))]
    if MARK not in src[PE.line_start(src, knode) - 1200:PE.line_start(src, knode)] or DATA not in old:
        edits.append((PE.line_start(src, knode), PE.line_start(src, knode), COMMENT))
    out = PE.apply(src, edits)
    assert out != src
    tree2 = PE.parse(out)
    new_dict = ast.literal_eval(PE.assignment(tree2, "CONFIG_INPUTS").value)
    why = PE.same_except(old_dict, new_dict, changed={KEY: new})
    assert why is None, why
    assert list(new_dict) == list(old_dict), "the order of the keys moved"
    assert [e for e in new_dict[KEY] if e in old] == [e for e in old if e in new_dict[KEY]] and \
        (DATA in old or all(e in new_dict[KEY] for e in old)), "an input the entry declared before is lost or out of order"
    rest = lambda t: [ast.dump(n) for n in t.body if n is not PE.assignment(t, "CONFIG_INPUTS")]
    assert rest(tree) == rest(tree2), "a statement other than CONFIG_INPUTS changed"
    msg = ("rules_status.CONFIG_INPUTS[%r]: %d inputs (%d before): the data file, the manifest that pins the makers' models, %d "
           "document(s), %d listing, %d netlists; no model is declared\n"
           "  THE NETLISTS ARE NAMED BY PHASE DIRECTORY (%s): when a board's declared phase moves, or the data file cites a new "
           "document, run this draft again with --refresh, or a reading is held to a netlist the design has left\n"
           "  OWED after this draft: apply_rules_status_pinned_models.py, and the data file, the manifest and the search listing "
           "committed before rules_status or rules_render run" % (
               KEY, len(new), len(old), len(docs), len(listing), len(nls), ", ".join(os.path.dirname(os.path.dirname(n)) for n in nls)))
    if "--dry-run" in sys.argv:
        print("dry run, nothing written: " + msg); return 0
    AP.write(TARGET, out)
    back = ast.literal_eval(PE.assignment(PE.parse(open(TARGET, encoding="utf-8").read()), "CONFIG_INPUTS").value)
    assert back == new_dict, "the file read back is not the entry that was written"
    print(msg)
    return 0


if __name__ == "__main__":
    AP.run(main)
