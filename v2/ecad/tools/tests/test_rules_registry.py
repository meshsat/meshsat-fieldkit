

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


# ---------------------------------------------------------------------------------------------------------
# THE BOARD THAT DECLARES A CONDUCTOR LEAVING THE CASE IS IN SCOPE FOR THE RULE ABOUT IT (17 September 2026).
#
# TRN-001's applicability was a list of interfaces and board properties and it missed board D, which carries
# two headset jacks on the face, a VHF antenna SMA and a 30 W power amplifier output. Its own gate had been
# measuring them all along and REFUSED board D's deliverable this morning for seven conductors reaching a
# semiconductor with nothing between, while the readiness carried no TRN-001 row for board D at all: the gate
# and the registry disagreed about whether the rule applies, and a board was blocked by a rule the status page
# said was not about it.

def t_every_board_s_external_port_fact_is_its_own_declaration():
    """The fact is not typed: it says what `boards/<letter>.json` declares, so the scope of the rule and the
    thing the gate reads cannot drift apart again."""
    import os, json, sys
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLS)
    import rules_lib as R
    f = R.facts()
    for letter, fact in sorted(f.items()):
        if not isinstance(fact, dict) or str(letter).startswith("_"): continue
        p = os.path.join(TOOLS, "boards", "%s.json" % letter)
        declared = bool((json.load(open(p, encoding="utf-8")) or {}).get("external_ports")) if os.path.exists(p) else False
        assert bool(fact.get("external_ports")) == declared, \
            ("board %s declares external_ports=%s and pcb_board_facts.yaml says %s"
             % (letter, declared, fact.get("external_ports")))


def t_a_board_with_a_declared_external_port_is_in_scope_for_the_port_rule():
    import os, sys
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLS)
    import rules_lib as R
    reg, f = R.load(), R.facts()
    for letter, fact in sorted(f.items()):
        if not isinstance(fact, dict) or str(letter).startswith("_"): continue
        if not fact.get("external_ports"): continue
        ids = {r["id"] for r, _why in R.rules_for(letter, reg, f)}
        assert "TRN-001" in ids, ("board %s declares a conductor that leaves the case and TRN-001 does not "
                                 "apply to it" % letter)


def t_the_declared_phase_is_one_fact_and_it_names_the_board_this_tree_holds():
    """THE PHASE IS A FACT ABOUT THE BOARD, WRITTEN TWICE, AND THE TWO COPIES DRIFTED (17 September 2026).

    `boards/<letter>.json` carries `"phase"` and `pcb_board_facts.yaml` carries `phase_declared`; the chain and
    the sweep read the first, the registry reads the second, and on 17 September board C said C24 in one and
    C18 in the other while board B said B21 and B19. Worse than the drift is what the field was pointed at: it
    had been set to the route IN FLIGHT, and every reader that gates on it asks "is this folder the board", so
    a declaration naming a route that has not landed makes those gates answer about a board that does not
    exist. Board P's P4 folder holds the board this tree holds byte for byte and was read as stale against a
    declared P5 that had been measured, refused and abandoned.

    Two properties, both checked on the committed tree: the two copies agree, and the declared phase is a
    phase the board in the tree actually carries on its silk.
    """
    import os, sys, json
    TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, TOOLS)
    import rules_lib as R
    import rules_status as S
    facts, m = R.facts(), S.manifest()
    for letter in sorted(m["boards"]):
        table = os.path.join(TOOLS, "boards", "%s.json" % letter)
        fact = (facts.get(letter) or {}).get("phase_declared")
        if os.path.exists(table):
            decl = (json.load(open(table, encoding="utf-8")) or {}).get("phase")
            assert decl and fact and decl == fact, \
                ("board %s declares %r in boards/%s.json and %r in pcb_board_facts.yaml: one fact, one value"
                 % (letter, decl, letter, fact))
        else:
            decl = fact
            assert decl, "board %s has no board table and no phase_declared, so nothing declares its phase" % letter
        su = S.subject(letter, m)
        if not su.get("board"): continue                 # no board file in the tree: a different failure, reported there
        assert su.get("agrees") is not False, \
            ("board %s declares %s and the board in %s carries %s: the declaration names a board this tree does "
             "not hold, and every gate that reads it (the folder rule, the sweep's order-code lookup) is then "
             "answering about a board that does not exist. The phase of a route in flight belongs to the run, "
             "not to this field." % (letter, decl, su["dir"], su.get("legend_phase")))
