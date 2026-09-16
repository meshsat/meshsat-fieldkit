

def t_a_coverage_map_that_will_not_parse_is_an_error_and_not_an_empty_map():
    """16 September 2026. `validate` read the coverage map inside `except BaseException: {}`, so a file that
    would not PARSE became an empty map, every rule's live maturity read None, and the policy that an ENFORCED
    blocker must carry a false-positive analysis stopped being checked while validate printed 0 errors. It
    happened on a missing comma in a flow mapping: the validator said the registry was fine and `rules_status`
    could not read the file at all. Absent is a tree being set up; unreadable is a tree lying to itself."""
    import os, shutil, sys, tempfile, subprocess
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = tempfile.mkdtemp(prefix="cov-parse-")
    for f in ("rules_lib.py", "pcb_rules.yaml", "pcb_rules_coverage.yaml", "pcb_board_facts.yaml",
              "pcb_board_holds.yaml"):
        src = os.path.join(here, f)
        if os.path.exists(src): shutil.copy(src, d)
    # the acceptable fixture: the tree as it is
    r = subprocess.run([sys.executable, os.path.join(d, "rules_lib.py"), "validate"],
                       capture_output=True, text=True)
    assert "does not parse" not in r.stdout, "the tree's own coverage map does not parse"
    # the defective fixture: a coverage map that exists and is broken
    p = os.path.join(d, "pcb_rules_coverage.yaml")
    # Read THEN write. `open(p, "w").write(open(p).read())` truncates the file before the inner read runs, so
    # the "broken" fixture was an EMPTY file, which parses to None and is treated as absent: the test passed
    # the defect through and then failed for the right reason. Python evaluates the arguments in order.
    _body = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(_body.replace("coverage:", "coverage: {broken", 1))
    r2 = subprocess.run([sys.executable, os.path.join(d, "rules_lib.py"), "validate"],
                        capture_output=True, text=True)
    assert r2.returncode != 0 and "does not parse" in r2.stdout, \
        "a broken coverage map still validates clean:\n%s" % (r2.stdout[-400:])
    # ...and an ABSENT one is still tolerated, which is what the tolerance was written for
    os.remove(p)
    r3 = subprocess.run([sys.executable, os.path.join(d, "rules_lib.py"), "validate"],
                        capture_output=True, text=True)
    assert "does not parse" not in r3.stdout, "an absent coverage map is now refused, which breaks a new tree"
