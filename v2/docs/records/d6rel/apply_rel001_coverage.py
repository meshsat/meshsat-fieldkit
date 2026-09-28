#!/usr/bin/env python3
"""The two shared-file changes of stream d6rel (MESHSAT-1357, finding H3-01 of the independent review of handover H3,
registry item S-89, erratum h of RELEASE-H3.md), for the INTEGRATOR to run; the stream does not edit these files.

  stage coverage    v2/ecad/tools/pcb_rules_coverage.yaml, the REL-001 entry: the fixtures name both test files, the
                    note says what the checker reads now and what the set 6 artefacts read under it, the remediation
                    names what is still owed, and `evidence_not_before` puts a FLOOR under REL-001's evidence at the
                    instant the tool changed what its PASS means. The floor is what makes an old word-list PASS stop
                    counting: rules_status keeps an older reading that had its input in front of a newer one that
                    declares its input absent (v2/docs/records/d6rel/consumers-probe.txt, items 2 and 3), so without
                    the floor a PASS of the unrepaired tool would stand in front of the repaired tool's INCONCLUSIVE.
                    Run it BEFORE the re-take, or after: it changes no reading, it says which readings count.

  stage close-s89   v2/ecad/tools/pcb_requirements.yaml: item S-89 leaves open_items for closed_items with the commit
                    that closed it and the evidence, READ from this tree: it REFUSES to run until REL-001 has been
                    re-taken on every board of the manifest with the list this tree holds, after the floor, bound to
                    the declared phase's artefact and with no refusal and no missing input. The re-take is the box's
                    (gate_sweep.sh or retake_gate.sh); this script never runs a gate. The records that WAIT on S-89
                    (on the integration tip REQ-022, REQ-024, REQ-026, REQ-028 and REQ-064) lose that wait and cite
                    the closing in their history, which is the registry's rule for a closed item and what its
                    validator asks ("cite that instead"). The item's `limits_reading` is not carried into the closed
                    entry (no closed item carries one); the closing evidence says what becomes of the limit.

Every stage asserts the old text is present, asserts the new text differs, re-parses the file (YAML; for the registry
also `python3 rules_lib.py requirements`, the tree's own validator, read only) and refuses a second run. It writes
nothing when an assertion fails.

Usage: apply_rel001_coverage.py --stage coverage  (--commit <merge> | --floor <ISO instant>) [--root <tree>]
       apply_rel001_coverage.py --stage close-s89 --commit <hash of the merged d6rel work> [--root <tree>] [--no-validate]
  --root    the repository root (default: the root this script sits in, v2/docs/records/d6rel/../../../..)
  --commit  the merge that brings this stream's reliability.py into the tree: closed_by names it, and its committer
            instant (read with git in the checkout) is the floor when --floor is not given; it must be a commit the
            tree holds
  --floor   the instant before which no reliability reading counts. NEVER A CONSTANT: the floor is the instant the
            repaired tool ENTERS THE TREE THE READINGS LIVE IN. A first draft carried the instant of the worker's
            last tool commit (16:46:27 CEST); the integration line then re-took reliability with the UNREPAIRED tool
            at 16:54 CEST (1c4235ec), and that fixed instant would have let seven word-list PASS readings stand.
            Either stage refuses a floor that is not after every reading of the unrepaired tool the tree holds
            (a reading with no `candidates` count); the close-s89 stage reads the floor the coverage entry carries.
Prototype work: nothing here has been built or measured. An AI review, never a qualified review.
"""
import os, re, sys, json, glob, hashlib, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))

OLD_NOTE_MARK = "declares 25 classes over the seven boards covering all 111 parts whose value names a connector"
NEW_NOTE_MARK = "the population is an INVENTORY (wear_inventory.py)"

NEW_REL001 = """ REL-001: {implementation: NONE_YET, verification: {tool: reliability.py, verdict: reliability, fixtures: "tests/test_reliability.py, tests/test_reliability_inventory.py"}, maturity: ENFORCED, gap_category: ABSENT,
   evidence_not_before: {"reliability": "%(floor)s"},
   _evidence_not_before_why: "28 September 2026, stream d6rel (finding H3-01 of the independent review of handover H3, registry item S-89, erratum h of RELEASE-H3.md): reliability.py changed what its PASS means. Until then its population was the parts whose value text matched twelve words, so an RJ45 jack, the SIM sockets and the dock's spring pins (61 parts of the set 6 netlists) were in no denominator, and a board with no netlist read PASS of zero. A reading taken before this instant is a reading of the word list and is not current evidence for REL-001 whatever it says. rules_status keeps an older reading that had its input in front of a newer one that declares its input absent, so without this floor a word-list PASS would stand in front of the repaired tool's INCONCLUSIVE (v2/docs/records/d6rel/consumers-probe.txt, items 2 and 3). The instant is the one the repaired tool entered this tree (the merge's committer instant), checked by the apply script to be after every reading of the unrepaired tool the tree held; a fixed instant would not have been (the integration line re-took reliability with the unrepaired tool at 16:54 CEST on 28 September 2026, after the worker's last tool commit of 16:46).",
   note: "nothing considers vibration, mating cycles or moisture for any interface 16 September 2026: THE LIST EXISTS AND IS CHECKED AGAINST THE BOARDS. 28 September 2026 (stream d6rel, S-89): the population is an INVENTORY (wear_inventory.py): every component of the declared phase's netlist (board E5: its board file) is read and asked for by its reference class and its land, never by the words of its value, and every candidate is in exactly one declared class or under one declared exclusion with a visible reason and the land it speaks of, or the gate refuses. On the set 6 artefacts (73ae2f21): 427 candidates (A 82, B 153, C 74, D 40, E 35, E5 17, P 26), 185 classed in 57 classes, 242 excluded under 14 exclusions (test points, solder jumpers, fuses soldered without a holder, the I/O controllers' programming pads, bench and commissioning headers), 0 refused; the list of 16 September covered 111 parts and would have left 316 of these candidates unread. Of the 57 classes, 24 cite the maker's cycle figure to a document held under v2/vendor/ by sha256, page and words (30 documents in all), 16 state that the maker's documents read give none (the JST catalogues and handling precautions, Keystone's holder pages), 8 mate nothing (solder lands, screw joints) and 9 OWE their figure under an open item of the list (REL-O-01 to REL-O-06: the pre-charge pin, the 2.54 mm lead headers with no named part, the Amphenol NVMe sockets, the panel ribbon header, the headset jacks, board E5's plated targets), with 3 measures owed (REL-O-09 to REL-O-11), so every board reads INCONCLUSIVE on its owed items and none reads PASS. A missing, unreadable or empty netlist reads INCONCLUSIVE with the reason, never PASS; the netlist is the declared phase's and is recorded by sha256 and by content; each board's declaration is bound to the artefact it was written against (written_against) and another sha reads INCONCLUSIVE, because the gate cannot read a part off the value text and a substitution is a mismatch until proven. The lowest figure cited in the kit is the e-paper flex connector at 20 mating cycles (Hirose FH34, board C); the pack's XT60 (1000) is unplugged before every lift of the stack, and the headset jacks, mated at every use, owe their figure. What it does NOT do is test anything: this rule is verified at the PROTOTYPE, no board has been built, and the dock block's contact targets carry the open item the mate-cycle test exists for.",
   remediation: {action: "28 September 2026: the checker and the list are repaired (stream d6rel, S-89). What remains of the SHEET is the nine owed figures and three owed measures of pcb_reliability.yaml's open_items, each with its next action (a part pick, a maker's sheet, a build choice between a header and a soldered lead, a hold-down design), and the expected mates per connector once a service life is ruled (REL-O-07, REQ-028). The TEST PLAN for the prototype is the laboratory stage and belongs with it", owner: SESSION, execution: SEQUENTIAL, depends_on: [ENV-001], p50_h: 4, p80_h: 10}}
"""


def fail(msg):
    print("apply_rel001_coverage: REFUSED: %s" % msg); sys.exit(2)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def reparse_yaml(path):
    import yaml
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    if not isinstance(d, dict): fail("%s does not parse as a mapping after the change" % path)
    return d


def old_tool_readings_after(root, floor):
    """Every reliability reading in this tree's evidence folders that the UNREPAIRED tool wrote (no inventory count) and
    that is not before `floor`, as sentences; [] when the floor is after all of them. Every file is read, not only the
    winner rules_status would pick, because the floor is what decides which readings count."""
    tools = os.path.join(root, "v2", "ecad", "tools")
    if tools not in sys.path: sys.path.insert(0, tools)
    import rules_status as S, phase_artefacts as PA
    m = S.manifest(); out = []
    for letter in PA.letters():
        for d in S._project_dirs(letter, m):
            for f in sorted(glob.glob(os.path.join(d, "reliability*.verdict.json"))):
                try: rec = json.load(open(f, encoding="utf-8"))
                except (OSError, ValueError): continue
                if "candidates" in (rec.get("counts") or {}): continue          # the repaired tool's reading
                try:
                    late = _instant(rec.get("ts")) >= _instant(floor)
                except (ValueError, TypeError):
                    late = True
                if late:
                    out.append("board %s: the unrepaired tool's %s at %s (%s)"
                               % (letter.upper(), rec.get("verdict"), rec.get("ts"), os.path.relpath(f, root)))
    return out


def floor_for(root, floor, commit):
    """The floor: --floor as given, else the committer instant of --commit read with git in this checkout; refused unless
    it is after every reading of the unrepaired tool this tree holds (see the module docstring on why it is never a
    constant)."""
    if not floor:
        if not commit:
            fail("--floor <instant> or --commit <the merge that brings reliability.py in> is required: the floor is never a constant")
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%cI", commit], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            fail("git in %s cannot give the instant of commit %s; pass --floor" % (root, commit))
        floor = r.stdout.strip()
        print("apply_rel001_coverage: the floor is the committer instant of %s: %s" % (commit, floor))
    _instant(floor)
    late = old_tool_readings_after(root, floor)
    if late:
        fail("the floor %s is not after every reading of the unrepaired tool this tree holds:\n  %s\n  pass a later --floor "
             "(the instant the repaired tool entered this tree)" % (floor, "\n  ".join(late)))
    return floor


def stage_coverage(root, floor):
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")
    old = open(p, encoding="utf-8").read()
    if NEW_NOTE_MARK in old: fail("the REL-001 entry already carries the inventory note: this stage has run")
    if OLD_NOTE_MARK not in old: fail("the REL-001 note of 16 September is not in %s: the file is not the one this script was written for" % p)
    # the entry: from its key line to the blank line that ends it
    m = re.search(r"(?ms)^ REL-001: \{.*?\n(?=\n)", old)
    if not m: fail("the REL-001 entry could not be delimited")
    block = m.group(0)
    for must in ("tool: reliability.py", "verdict: reliability", "fixtures: tests/test_reliability.py", OLD_NOTE_MARK,
                 "The SHEET is DONE (17 September 2026)"):
        if must not in block: fail("the REL-001 entry does not carry %r" % must)
    if "evidence_not_before" in block: fail("the REL-001 entry already carries an evidence floor")
    new_block = NEW_REL001 % {"floor": floor}
    new = old.replace(block, new_block, 1)
    if new == old: fail("the new text equals the old")
    if new.count(new_block) != 1 or NEW_NOTE_MARK not in new: fail("the replacement did not land once")
    tmp = p + ".d6rel.tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    d = reparse_yaml(tmp)
    e = (d.get("coverage") or {}).get("REL-001") or {}          # the rule entries sit under the file's `coverage` key
    ok = (e.get("evidence_not_before") == {"reliability": floor}
          and e.get("verification", {}).get("fixtures") == "tests/test_reliability.py, tests/test_reliability_inventory.py"
          and e.get("maturity") == "ENFORCED" and NEW_NOTE_MARK in (e.get("note") or ""))
    if not ok:
        os.remove(tmp); fail("the patched REL-001 entry does not read back as written: %r" % {k: e.get(k) for k in ("evidence_not_before", "verification", "maturity")})
    os.replace(tmp, p)
    print("apply_rel001_coverage: coverage: REL-001 entry replaced in %s (sha256/16 %s -> %s); floor %s; re-parsed"
          % (os.path.relpath(p, root), hashlib.sha256(old.encode("utf-8")).hexdigest()[:16], sha16(p), floor))
    return 0


def _instant(s):
    import datetime as _dt
    t = (s or "").strip().replace("Z", "+00:00")
    d = _dt.datetime.fromisoformat(t)
    if d.tzinfo is None: d = d.replace(tzinfo=_dt.timezone.utc)      # a verdict writes UTC with no offset
    return d


def retake_evidence(root, floor):
    """[(letter, verdict record, path)] of the current REL-001 reading of every board, found the way rules_status finds
    them (read only), each checked: after the floor, the list this tree holds, bound to the declared phase's artefact,
    no refusal, no missing input. The reasons it is not there yet are returned as the second value."""
    tools = os.path.join(root, "v2", "ecad", "tools")
    sys.path.insert(0, tools)
    import rules_status as S, phase_artefacts as PA
    lst = sha16(os.path.join(tools, "pcb_reliability.yaml"))
    m = S.manifest()
    found, why = [], []
    for letter in PA.letters():
        rec = S._verdicts(letter, m).get("reliability")
        if rec is None:
            why.append("board %s: no reliability verdict in this tree" % letter.upper()); continue
        inp = rec.get("inputs") or {}
        li = inp.get("list") if isinstance(inp.get("list"), dict) else {}
        kind, design = PA.design_of(letter)
        key = "netlist" if kind == "netlist" else "board_file"
        art = inp.get(key) or inp.get("%s_%s" % (key, letter))          # a per-board run, or the set-level run's key
        art = art if isinstance(art, dict) else {}
        problems = []
        try:
            if _instant(rec.get("ts")) < _instant(floor): problems.append("taken %s, before the floor %s" % (rec.get("ts"), floor))
        except (ValueError, TypeError):
            problems.append("its timestamp %r cannot be read" % rec.get("ts"))
        if li.get("sha256_16") != lst: problems.append("read list %s, this tree holds %s" % (li.get("sha256_16"), lst))
        if not design: problems.append("this tree holds no %s for the board" % (kind or "artefact"))
        elif art.get("sha256_16") != design.get("sha256_16"):
            problems.append("read %s %s, the declared phase's is %s" % (kind, art.get("sha256_16"), design.get("sha256_16")))
        if rec.get("verdict") not in ("PASS", "INCONCLUSIVE"): problems.append("reads %s" % rec.get("verdict"))
        if rec.get("missing_input"): problems.append("declares its input missing: %s" % str(rec.get("missing_input"))[:120])
        c = rec.get("counts") or {}
        pb = (c.get("per_board") or {}).get(letter) or {}
        refused = pb.get("refused") if pb else c.get("refused")
        if refused is None: problems.append("carries no counts of the inventory (a reading of the word-list tool?)")
        elif refused != 0: problems.append("refused %s part(s)" % refused)
        if problems: why.append("board %s: %s (%s)" % (letter.upper(), "; ".join(problems), os.path.relpath(rec["_path"], root)))
        else: found.append((letter, rec, os.path.relpath(rec["_path"], root)))
    return found, why


def stage_close_s89(root, commit, validate=True):
    p = os.path.join(root, "v2", "ecad", "tools", "pcb_requirements.yaml")
    old = open(p, encoding="utf-8").read()
    # THE FLOOR IS THE COVERAGE ENTRY'S, so the two stages cannot disagree; and it is checked again against the tree.
    cov = reparse_yaml(os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml"))
    floor = (((cov.get("coverage") or {}).get("REL-001") or {}).get("evidence_not_before") or {}).get("reliability")
    if not floor: fail("pcb_rules_coverage.yaml's REL-001 entry carries no evidence floor for reliability: run --stage coverage first")
    late = old_tool_readings_after(root, floor)
    if late: fail("the coverage entry's floor %s is not after every reading of the unrepaired tool this tree holds:\n  %s"
                  % (floor, "\n  ".join(late)))
    if not commit or not re.fullmatch(r"[0-9a-f]{7,40}", commit): fail("--commit <hash> is required: the commit closed_by names")
    if os.path.isdir(os.path.join(root, ".git")) or os.path.isfile(os.path.join(root, ".git")):
        r = subprocess.run(["git", "-C", root, "cat-file", "-e", commit + "^{commit}"], capture_output=True)
        if r.returncode != 0: fail("this tree does not hold commit %s" % commit)
    else:
        print("apply_rel001_coverage: note: %s is not a git checkout, so the commit is not checked here" % root)
    if re.search(r"(?m)^  - id: S-89\n    closed_by:", old): fail("S-89 is already in closed_items: this stage has run")
    m = re.search(r"(?ms)^  - id: S-89\n    class: SESSION\n    status: OPEN\n(.*?)(?=^  - id: |^closed_items:)", old)
    if not m: fail("open item S-89 is not in %s as this script expects it" % p)
    block, body = m.group(0), m.group(1)
    t = body.find("    title: >-\n")
    if t < 0: fail("the S-89 block carries no folded title")
    title_body = body[t + len("    title: >-\n"):]
    # Whatever stands before the title (on the integration tip: `limits_reading: [{rule: REL-001, boards: all}]`) is an
    # OPEN item's field; no closed item of the registry carries one, and the closing evidence says what becomes of it.
    limits = body[:t].strip()
    if "REL-001's completeness can be false" not in title_body: fail("the S-89 block does not carry its title")
    if old.count("\nclosed_items:\n") != 1: fail("closed_items: is not exactly once in the registry")
    found, why = retake_evidence(root, floor)
    if why: fail("REL-001 has not been re-taken as this closure needs:\n  " + "\n  ".join(why)
                 + "\n  Re-take reliability on every board (the box: gate_sweep.sh, or retake_gate.sh), then run this stage again.")
    # THE VALIDATOR IS READ BEFORE THE CHANGE AND AFTER IT: a tree may carry errors of its own (a copy without every
    # page a record names), so the bar is that this change adds none, and that none of the errors names S-89.
    tools = os.path.join(root, "v2", "ecad", "tools")
    before_errs = _validator(tools) if validate else None
    ev_rows = []
    for letter, rec, path in found:
        c = rec.get("counts") or {}; pb = (c.get("per_board") or {}).get(letter) or {}
        inp = rec.get("inputs") or {}; art = inp.get("netlist") or inp.get("board_file") or {}
        ev_rows.append("%s %s (%s candidates, %s classed, %s excluded, 0 refused; %s %s; %s)"
                       % (letter.upper(), rec.get("verdict"), pb.get("candidates"), pb.get("classed"), pb.get("excluded"),
                          "netlist" if "netlist" in inp else "board file", art.get("sha256_16"), path))
    lst = sha16(os.path.join(root, "v2", "ecad", "tools", "pcb_reliability.yaml"))
    closing = (
        "Stream d6rel, merged as commit %s (v2/docs/records/d6rel/README.md). reliability.py reads an inventory by reference class "
        "and land (wear_inventory.py; pcb_reliability.yaml section inventory), every candidate classed or excluded with a visible "
        "reason and the land it speaks of; a missing, unreadable or empty netlist reads INCONCLUSIVE with the reason (verdict.write's "
        "missing_input, which rules_status reads as INCONCLUSIVE: v2/docs/records/d6rel/consumers-probe.txt); the netlist is the "
        "declared phase's (phase_artefacts) and the reading records it by sha256 and by content; each board's declaration is bound "
        "to the artefact it was written against (written_against) and another sha reads INCONCLUSIVE; the reviewer's four cases read "
        "PASS, FAIL, FAIL, INCONCLUSIVE on the repaired tool (v2/docs/records/d6rel/matrix-on-repaired-tool.txt; 2 of 4 on the "
        "unrepaired tool, matrix-on-unrepaired-tool.txt) and are tests/test_reliability.py t_matrix_1 to t_matrix_4, with fixtures "
        "for a connector whose value carries no wear word, the empty netlist, a class with no cycle figure and the sha mismatch; the "
        "inventory of the set 6 artefacts reads 427 candidates, 185 classed, 242 excluded, 0 refused where the word list had covered "
        "111 (inventory-before-after.txt). REL-001 re-taken on every board of the manifest with list sha256/16 %s after the evidence "
        "floor %s of pcb_rules_coverage.yaml: %s. Every board reads INCONCLUSIVE on the figures and measures the list still owes "
        "(open items REL-O-01 to REL-O-11 of pcb_reliability.yaml, each with its next action), never PASS; REL-001 stays a desk "
        "reading that tests nothing and replaces no physical verification. The item's limit on the readings (%s) ends with it: a "
        "reading taken after the floor is the repaired tool's and is not LIMITED; one taken before it is, and the floor makes it "
        "not current." % (commit, lst, floor, "; ".join(ev_rows), " ".join(limits.split()) or "none declared"))
    entry = ("  - id: S-89\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s"
             % (commit, _fold(closing), title_body))
    new = old.replace(block, "", 1).replace("\nclosed_items:\n", "\nclosed_items:\n" + entry, 1)
    if new == old: fail("the new text equals the old")
    if new.count("  - id: S-89\n") != 1: fail("S-89 is not exactly once after the change")
    # A RECORD NEVER WAITS ON A CLOSED ITEM; IT CITES WHAT CLOSED IT (the registry's own rule, and the validator's:
    # "waits on S-89, which commit X closed; cite that instead"). Every record whose waits_on names S-89 loses that wait
    # and gains the citation in its history, the field the registry uses for what an earlier reading said and what
    # changed it. The record's result fields are not touched: what REL-001 reads is the re-take's to say.
    new, cited = _cite_instead_of_wait(new, commit, floor)
    if not cited: fail("no record waits on S-89, which the registry of fnd/int7 does not match (five records did)")
    tmp = p + ".d6rel.tmp"
    open(tmp, "w", encoding="utf-8").write(new)
    d = reparse_yaml(tmp)
    open_ids = [x.get("id") for x in d.get("open_items") or []]
    closed = {x.get("id"): x for x in d.get("closed_items") or []}
    if "S-89" in open_ids or "S-89" not in closed or closed["S-89"].get("closed_by") != "commit %s" % commit:
        os.remove(tmp); fail("the registry does not read back with S-89 closed by commit %s" % commit)
    for rid in cited:
        rec = next((x for x in d.get("records") or [] if x.get("id") == rid), None)
        if rec is None or "S-89" in (rec.get("waits_on") or []) or ("S-89" not in (rec.get("history") or "")):
            os.remove(tmp); fail("record %s does not read back with its wait on S-89 cited instead" % rid)
    os.replace(tmp, p)
    print("apply_rel001_coverage: close-s89: S-89 moved to closed_items in %s (closed_by commit %s); the wait on it cited "
          "instead in %s; re-parsed" % (os.path.relpath(p, root), commit, ", ".join(cited)))
    if validate:
        after_errs = _validator(tools)
        new_errs = [e for e in after_errs if e not in before_errs]
        print("apply_rel001_coverage: rules_lib.py requirements: %d error(s) before this change, %d after, %d new"
              % (len(before_errs), len(after_errs), len(new_errs)))
        if new_errs or any("S-89" in e for e in after_errs):
            open(p, "w", encoding="utf-8").write(old)
            fail("the registry validator reads new errors after the change; the file is restored to the text before this stage:\n  "
                 + "\n  ".join((new_errs or [e for e in after_errs if "S-89" in e])[:10]))
    return 0


def _validator(tools):
    """The ERROR lines of `python3 rules_lib.py requirements` in this tree's tools directory (read only)."""
    r = subprocess.run([sys.executable, "rules_lib.py", "requirements"], cwd=tools, capture_output=True, text=True)
    return sorted(l for l in (r.stdout + r.stderr).split("\n") if l.startswith("ERROR"))


def _cite_instead_of_wait(text, commit, floor):
    """(text, [record ids]) with S-89 removed from every record's `waits_on` and the closing cited in its `history`."""
    sentence = ("28 September 2026: S-89 (REL-001's population, inputs and binding: the independent review of handover H3, "
                "finding H3-01) closed by commit %s, stream d6rel, v2/docs/records/d6rel/README.md; this record cited the wait "
                "on it and cites the closing instead. REL-001's readings taken after the evidence floor %s are the repaired "
                "tool's (an inventory by reference class and land, the netlist bound by sha) and are not LIMITED; each board "
                "reads INCONCLUSIVE on the figures and measures pcb_reliability.yaml still owes (REL-O-01 to REL-O-11)."
                % (commit, floor))
    i = text.find("\nrecords:\n")
    if i < 0: fail("the registry carries no records: section")
    head, body = text[:i + len("\nrecords:\n")], text[i + len("\nrecords:\n"):]
    parts = re.split(r"(?m)(?=^  - id: )", body)
    cited = []
    for k, blk in enumerate(parts):
        m = re.search(r"(?m)^    waits_on: \[(.*)\]\n", blk)
        if not m: continue
        waits = [w.strip() for w in m.group(1).split(",") if w.strip()]
        if "S-89" not in waits: continue
        rid = re.match(r"  - id: (\S+)", blk).group(1)
        rest = [w for w in waits if w != "S-89"]
        line = ("    waits_on: [%s]\n" % ", ".join(rest)) if rest else ""
        blk = blk.replace(m.group(0), line, 1)
        h = re.search(r"(?ms)^    history: >-\n((?:      .*\n)+)", blk)
        if h:
            blk = blk.replace(h.group(0), h.group(0) + _fold(sentence), 1)
        else:
            sc = re.search(r"(?m)^    source_check: \S+\n", blk)
            if not sc: fail("record %s carries no source_check line to anchor its history to" % rid)
            blk = blk.replace(sc.group(0), sc.group(0) + "    history: >-\n" + _fold(sentence), 1)
        parts[k] = blk
        cited.append(rid)
    return head + "".join(parts), cited


def _fold(text, width=118, indent="      "):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: lines.append(cur)
    return "".join(indent + l + "\n" for l in lines)


def main(argv):
    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    stage = opt("--stage")
    root = os.path.abspath(opt("--root", DEFAULT_ROOT))
    if not os.path.isfile(os.path.join(root, "v2", "ecad", "tools", "pcb_rules_coverage.yaml")): fail("%s is not the repository root" % root)
    if stage == "coverage": return stage_coverage(root, floor_for(root, opt("--floor"), opt("--commit")))
    if stage == "close-s89": return stage_close_s89(root, opt("--commit"), validate="--no-validate" not in argv)
    fail("--stage coverage or --stage close-s89")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
