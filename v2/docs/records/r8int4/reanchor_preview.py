"""Preview the re-anchoring of pcb_requirements.yaml citations (hc3 apply script's reanchor) without writing:
prints a unified diff of the registry text. Usage: reanchor_preview.py SCRIPT (run from the repository root)."""
import importlib.util, os, sys, difflib
spec = importlib.util.spec_from_file_location("apply_registry_hc3", sys.argv[1]); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
root = m.repo_root(os.getcwd()); reg = os.path.join(root, "v2/ecad/tools/pcb_requirements.yaml")
orig = open(reg, encoding="utf-8").read()
doc = m.Doc(orig); log = []
m.ROOT_FOR_OPS[0] = root; m.WRITE_FILES[0] = False; m.DRY_RUN[0] = True
m.reanchor(doc, root, log, True)
for r in log: print("%-8s %-22s %-14s %s" % r)
new = doc.text()
for l in difflib.unified_diff(orig.split("\n"), new.split("\n"), lineterm="", n=0):
    print(l)
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf-8").write(new)
