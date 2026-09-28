#!/usr/bin/env python3
"""Declare the reviewed sets' file as a configuration input of port_protect.py (MESHSAT-1357, worker d8dec31, 28
September 2026; the fresh check's item B1, open item S-88). The integrator runs it on v2/ecad/tools/rules_status.py,
its file.

port_protect.py reads v2/ecad/tools/pcb_port_reviews.json (the external pins a review enumerated for each board, held
against the declaration pin by pin) and records it in every reading's `inputs` as `port_reviews`, by sha. rules_status
binds a reading to the configuration its writer is declared to read in CONFIG_INPUTS; a file read but not declared is
a change the readings would not see. This adds "tools/pcb_port_reviews.json" to port_protect.py's tuple and the line
references of the comment above it, asserts the old text once, asserts the new text differs, imports the patched module
from a copy to check it still loads and carries the entry, and refuses a second run.

Usage: apply_config_inputs_port_reviews.py <tree root> [--check]
"""
import importlib.util, os, shutil, sys, tempfile

OLD = '''    # port_protect.py:112, :463-472, :523-524 and :538-539 the board table's external_ports and _external_ports_why;
    # :482-485 boardtable.letter_for (every table's `name`; the reading records the letter it resolved); :101-106 and
    # :285-288 the intent file beside the netlist, whose rails stop the search, which the reading records by sha
    # (phase_artefacts.reading_inputs, :436).
    "port_protect.py": ("tools/boards/{letter}.json", "{phase}/out/{stem}-intent.json"),
'''
NEW = '''    # port_protect.py:112, :463-472, :523-524 and :538-539 the board table's external_ports and _external_ports_why;
    # :482-485 boardtable.letter_for (every table's `name`; the reading records the letter it resolved); :101-106 and
    # :285-288 the intent file beside the netlist, whose rails stop the search, which the reading records by sha
    # (phase_artefacts.reading_inputs, :436). Since 28 September 2026 (S-88, the review of decision 31, item B1):
    # port_protect.reviews() reads tools/pcb_port_reviews.json, the external pins a review enumerated for each board,
    # which reconcile() holds the declaration against pin by pin; the reading records it as inputs.port_reviews by sha.
    "port_protect.py": ("tools/boards/{letter}.json", "{phase}/out/{stem}-intent.json", "tools/pcb_port_reviews.json"),
'''


def main(argv):
    if not argv: print(__doc__); return 2
    root, dry = os.path.abspath(argv[0]), "--check" in argv
    p = os.path.join(root, "v2", "ecad", "tools", "rules_status.py")
    old = open(p, encoding="utf-8").read()
    if '"tools/pcb_port_reviews.json"' in old:
        raise SystemExit("apply_config_inputs_port_reviews: already applied (the entry is in the file)")
    assert old.count(OLD) == 1, "the port_protect.py entry of CONFIG_INPUTS is not the text this script expects"
    if not os.path.exists(os.path.join(root, "v2", "ecad", "tools", "pcb_port_reviews.json")):
        raise SystemExit("apply_config_inputs_port_reviews: v2/ecad/tools/pcb_port_reviews.json is not in the tree; merge the branch first")
    new = old.replace(OLD, NEW)
    assert new != old
    # the patched module still loads, from a copy beside the tools it imports, and carries the entry
    tools = os.path.dirname(p)
    tmp = tempfile.mkdtemp(prefix="cfg-inputs-")
    try:
        for f in os.listdir(tools):
            if f.endswith(".py"): shutil.copy(os.path.join(tools, f), tmp)
        open(os.path.join(tmp, "rules_status.py"), "w", encoding="utf-8").write(new)
        sys.path.insert(0, tmp)
        spec = importlib.util.spec_from_file_location("rs_patched", os.path.join(tmp, "rules_status.py"))
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        assert m.CONFIG_INPUTS["port_protect.py"] == ("tools/boards/{letter}.json", "{phase}/out/{stem}-intent.json",
                                                      "tools/pcb_port_reviews.json"), m.CONFIG_INPUTS["port_protect.py"]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if not dry:
        with open(p, "w", encoding="utf-8") as f: f.write(new)
    print("apply_config_inputs_port_reviews: port_protect.py declares 3 configuration inputs%s" % (" (checked, not written)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
