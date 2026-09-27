"""Run ONLY the re-anchoring step of fnd/hc3's apply script (records/hc3/apply_registry.py), after its registry change
was committed with --no-reanchor. A second full run is not idempotent on this tree (REQ-050's evidence_result moved to
PASS by a later op of the same run, which the first op's old-or-new guard then refuses), so this driver imports the
script and calls reanchor() with --accept-rewritten semantics on the committed tree. Usage: reanchor_only.py SCRIPT
[--write]  (run from the repository root)."""
import importlib.util, os, sys
spec = importlib.util.spec_from_file_location("apply_registry_hc3", sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
write = "--write" in sys.argv
root = m.repo_root(os.getcwd()); reg = os.path.join(root, "v2/ecad/tools/pcb_requirements.yaml")
doc = m.Doc(open(reg, encoding="utf-8").read()); log = []
m.ROOT_FOR_OPS[0] = root; m.WRITE_FILES[0] = write; m.DRY_RUN[0] = not write
try:
    m.reanchor(doc, root, log, True)
except m.Refused as e:
    for r in log: print("%-8s %-22s %-14s %s" % r)
    print("REFUSED: %s" % e); sys.exit(1)
for r in log: print("%-8s %-22s %-14s %s" % r)
if write:
    open(reg, "w", encoding="utf-8").write(doc.text()); print("reanchor_only: written")
else:
    print("reanchor_only: dry run")
